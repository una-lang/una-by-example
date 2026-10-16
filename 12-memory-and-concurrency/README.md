---
learn: "12"
title: Memory and concurrency
editions: ["0.2"]
codes: [U2012, U2017, U2019, U2020, U2023, U3013]
time: 40
builds: An end-of-day stock count that replays each site's movements and closes every site at once
prerequisites: ["4", "5", "6", "7", "8", "10"]
template: 2
---

# 12 Memory and concurrency

A store's day ends with a count. Every site replays the sales and deliveries its tills recorded, rejects the movements that do not add up, and reports what is left on the shelves. That work changes values step by step, and the sites are independent of each other, so they can be counted at the same time. This chapter shows how Una lets a function change a value without sharing it, how a value is given up for good, how independent work runs concurrently with a result that never depends on timing, and what stops a run that grows too deep or too large.

## What you'll build

:::build
An end-of-day stock count for a store with two sites. Each site's ledger takes its movements one by one, a movement that does not add up leaves the ledger as it was, and both sites are closed at the same time:

```text include="day-to-day/expected/output.txt"
north: 2 applied, 1 rejected
  LAMP-01 4 -> 3
  rejected: 2 of DESK-02 sold, 1 counted
  LAMP-01 3 -> 9
  closing {"DESK-02": 1, "LAMP-01": 9}
south: 1 applied, 1 rejected
  rejected: no product has the SKU CHAIR-09
  LAMP-01 2 -> 0
  closing {"LAMP-01": 0}
```

You will learn to:

- update a value in place with `let edit`, and know that no other binding sees the change;
- pass a value in and out of a function with an `edit` parameter, and rely on it being left unchanged when the call fails;
- give a value up with `take`, so that no code can use it afterwards;
- run independent work concurrently with `together` and `together for`, with the result of a sequential run;
- recognize U6003, the stop at the call depth or memory limit, and avoid it with loops.
:::

## Why it works this way

Most languages let two parts of a program hold the same object. A function that receives a list can change it under its caller, a cache can change a record that a report is still reading, and two threads can write the same counter at once. Reading a function then means asking who else holds what it holds, and concurrent code needs locks, or a type system of lifetimes and borrows, to stay correct.

Una takes another route. Three rules do it:

:::steps
1. **Values are values.** There are no references and no lifetimes. A `let` binding is a value, and copying it into another binding gives that binding its own value.
2. **Change is local and visible.** A binding declared `let edit` can be rebound, and a parameter declared `edit` passes a value in and out. The call says `edit` too, so a reader sees at the call which bindings it may change.
3. **Concurrent tasks share nothing.** A `together` task reads the values of the bindings around it, and cannot assign them. Each task returns its result, and the block's result is the result of running the tasks one after another.
:::

The price is that two parts of a program never share a changing value: one of them returns a new value, or takes it with `edit`. In return, a value cannot change behind your back, and concurrency changes when the work happens, not what it computes. The backend may still update a value in place when nothing else holds it, without anything the program can observe.

> [!KEY]
> In Una, the only bindings a call can change are the ones it names with `edit`, and only if the call returns. A failed call leaves them as they were.

## 12.1 Values, not references

Start with one shelf of the store. Its record holds a SKU and the units on it. The program takes a copy at the start of the day, changes the shelf twice, and keeps a snapshot between the changes.

Each step of this chapter is a package, as in [chapter 1](/learn/hello/#s1-1): `una.toml`, `verification.lock` and the module under `src/`. Every package of this chapter uses edition `0.2`, which the manifest names:

```toml include="steps/01-values/una.toml" title="steps/01-values/una.toml"
[package]
name = "shelf"
version = "0.1.0"
edition = "0.2"

[run]
entry = "shelf"
grants = ["console"]
```

`verification.lock` is the same in every example: copy it from chapter 1, or take the step's package, whole, from the chapter's download, `12-memory-and-concurrency.tar.gz`. Then, in the package's directory:

```sh
una check .
una run .
```

:::steps
```una include="steps/01-values/src/shelf.una" title="steps/01-values/src/shelf.una" verified="check, run"
module shelf

--- A shelf of the store: the SKU it holds and how many units are on it.
kind Shelf
  sku: Text
  units: Int

pub main() -> Unit
  uses @console: Console[print]
=
  let opening = Shelf(sku: "LAMP-01", units: 4)
  let edit current = opening
  current.units = current.units + 6
  let snapshot = current
  current.units = current.units - 3
  let edit counts = [4, 0, 7]
  edit counts.set(index: 1, item: 12)
  @console.print("opening {opening.units}, snapshot {snapshot.units}, now {current.units}")
  @console.print("counts {counts}")
  @console.print("{current}")
```

Walkthrough:

1. **`let opening = Shelf(…)`.** A plain `let` binds a value for good. Assigning `opening` later is U2019, the code of an assignment to a binding that is not editable.
2. **`let edit current = opening`.** An editable binding, as in [chapter 2, Values](/learn/values/#s2-4), starts as a copy of `opening`'s value. Its type is fixed by that first value: it stays a `Shelf`.
3. **`current.units = current.units + 6`.** Assigning a field of an editable record rebinds `current` to a record with that field changed. `opening` keeps its own value, since it is another binding.
4. **`let snapshot = current`.** The snapshot is the value `current` has on this line. The next assignment to `current` does not reach it.
5. **`edit counts.set(index: 1, item: 12)`.** A list element changes through `set`, never by assignment, and the call says `edit`. `set` requires an index inside the list, and the verifier proves it here from the list's length.
:::

`una run .` prints:

```text include="steps/01-values/expected/output.txt"
opening 4, snapshot 10, now 7
counts [4, 12, 7]
Shelf(sku: "LAMP-01", units: 7)
```

The three numbers on the first line are three values: the opening count, the snapshot and the shelf now. The last line interpolates the whole record. In edition `0.2`, any value that `==` compares can be interpolated, a record, a list or a map included, but not a `Hashed`. This chapter uses that to print what each binding holds.

> [!NOTE] Copies are cheap.
> A copy need not duplicate the shelf's memory when the program runs. The backends of una share a value until one binding changes it, and change it in place when nothing else holds it. None of this is observable: the output is the output of the copies.

There are no compound assignments such as `+=`, and no `while` loop: a `for` loop, or recursion, does the repeating ([chapter 5, Collections](/learn/collections/), shows `for`).

## 12.2 Passing a value in and out: `edit`

A function that changes a value it receives must say so. A parameter declared `edit` is passed in and out: the function receives the caller's value, works on it as on a `let edit` binding, and when it returns, the caller's binding receives the final value. The caller writes `edit` at the call too, so the change is visible where it happens.

This step sets units of a shelf aside for orders. A reservation that asks for more units than are free fails, and the shelf must then stay as it was:

:::steps
```una include="steps/02-edit/src/reserve.una" title="steps/02-edit/src/reserve.una" verified="check, run"
module reserve

--- A shelf of the store: its SKU, the units on it, and the units set aside for orders.
kind Shelf
  sku: Text
  units: Int
  reserved: Int

kind ReserveError = | NotEnough(sku: Text, wanted: Int, free: Int)

--- Sets `units` aside for an order. On failure the shelf is left as it was.
reserve(edit shelf: Shelf, units: Int) -> Unit
  requires units > 0
  ensures shelf.reserved == old(shelf).reserved + units
  fails ReserveError
=
  let free = shelf.units - shelf.reserved
  if units > free
    fail NotEnough(sku: shelf.sku, wanted: units, free: free)
  shelf.reserved = shelf.reserved + units

pub main() -> Unit
  uses @console: Console[print]
=
  let edit lamps = Shelf(sku: "LAMP-01", units: 5, reserved: 0)
  edit lamps.reserve(units: 2)
    if error use unit
  reserve(edit lamps, units: 9)
    if error use unit
  @console.print("{lamps.reserved} of {lamps.units} reserved")
```

Walkthrough:

1. **`reserve(edit shelf: Shelf, units: Int) -> Unit`.** The parameter `shelf` is passed in and out. The function returns `Unit`: what it gives back is the changed shelf.
2. **`ensures shelf.reserved == old(shelf).reserved + units`.** In an `ensures` clause, `shelf` is the final value and `old(shelf)` the value on entry. The verifier proves the promise on every path that returns ([chapter 7, Contracts and the verifier](/learn/contracts/), covers `ensures`).
3. **`fail NotEnough(…)`.** A `fail` inside an `if` without `else` ends the function there ([chapter 6, Failure](/learn/failure/), covers `fail`).
4. **`edit lamps.reserve(units: 2)`.** A call written as a method puts `edit` before the receiver. It is the same call as `reserve(edit lamps, units: 2)`.
5. **`reserve(edit lamps, units: 9)` with `if error use unit`.** Nine units are more than the three that are free, so the call fails, and the clause carries on with `unit`.
:::

`una run .` prints:

```text include="steps/02-edit/expected/output.txt"
2 of 5 reserved
```

Two units are reserved, not eleven. The failed call changed nothing: a call that fails leaves every `edit` argument with the value it had before the call. The function's own assignments are discarded with its failure, so a half-done update never reaches the caller.

> [!IMPORTANT]
> Effects are not rolled back. If a function prints, sends a message or writes a file and then fails, those operations stay performed. Only the `edit` arguments go back to their old values.

An `edit` argument has three rules, each with its own code:

| Rule | Code |
| --- | --- |
| The call writes `edit` exactly where the parameter is declared `edit`, and nowhere else | U2020 |
| The argument is a place: an editable binding or a field of one, such as `ledger` or `cart.skus` | U2019 when the binding is not editable |
| No other argument of the same call uses the same binding, even another field of it | U2018 |

A call with an `edit` or `take` argument is also the whole expression of its statement or `let`, as a call that can fail is ([chapter 6, Failure](/learn/failure/)). So it cannot be nested in another call, and it cannot be wrapped in `attempt`. Section [12.8](#s12-8) shows the diagnostic.

## 12.3 Giving a value up: `take`

Some values must not be used after a point. A cart that has been checked out should not take more items, or the order and the cart disagree. A parameter declared `take` consumes its argument: after the call, the caller cannot use the binding, and every use of it is U2017.

:::steps
```una include="steps/03-take/src/checkout.una" title="steps/03-take/src/checkout.una" verified="check, run"
module checkout

--- A customer's cart: the SKUs in it and their total in cents.
kind Cart
  customer: Text
  skus: List[Text]
  cents: Int

--- An order, made from a cart at checkout.
kind Order
  number: Int
  customer: Text
  lines: Int
  cents: Int

--- Puts one unit of `sku` in the cart.
add(edit cart: Cart, sku: Text, cents: Int) -> Unit
  ensures cart.skus.len == old(cart).skus.len + 1
=
  cart.skus = cart.skus.append(item: sku)
  cart.cents = cart.cents + cents

--- Turns the cart into an order. It takes the cart, so nothing can add to it afterwards.
checkout(take cart: Cart, number: Int) -> Order = Order(number: number, customer: cart.customer, lines: cart.skus.len, cents: cart.cents)

pub main() -> Unit
  uses @console: Console[print]
=
  let edit cart = Cart(customer: "C-1042", skus: [], cents: 0)
  edit cart.add(sku: "LAMP-01", cents: 1990)
  edit cart.add(sku: "DESK-02", cents: 12900)
  let order = checkout(take cart, number: 1001)
  cart = Cart(customer: "C-1042", skus: [], cents: 0)
  @console.print("order {order.number}: {order.lines} lines, {order.cents} cents")
  @console.print("the new cart has {cart.skus.len} lines")
```

Walkthrough:

1. **`add(edit cart: Cart, sku: Text, cents: Int)`.** Adding to the cart changes it, so the cart is an `edit` parameter. Its `ensures` promises one more SKU.
2. **`checkout(take cart: Cart, number: Int) -> Order`.** The cart goes in and an order comes out. `take` states that the cart is used up.
3. **`let order = checkout(take cart, number: 1001)`.** The call writes `take`, as `edit` is written for an `edit` parameter. From here on, `cart` is taken.
4. **`cart = Cart(…)`.** An assignment gives a taken `let edit` binding a new value, and it can be used again. A plain `let` binding stays taken.
:::

`una run .` prints:

```text include="steps/03-take/expected/output.txt"
order 1001: 2 lines, 14890 cents
the new cart has 0 lines
```

The checker follows a taken binding through the program. A binding taken in one branch of an `if` or a `when` counts as taken after it. A binding taken inside a loop body must get a new value before the body ends, or be declared inside it, since the next iteration would use it again.

`take` also tells the backend that the value is not needed after the call, so it can reuse the value's memory instead of keeping a copy. The program behaves the same either way.

Three ways compete for a function that turns one value into another:

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A new value, and the caller keeps the old one | A plain parameter, and return the new value |
| To change the caller's value, with the change visible at the call | An `edit` parameter |
| To use the value up, so that nothing can use it afterwards | A `take` parameter |
| To change a value only when the whole update succeeds | An `edit` parameter and `fails`: a failure leaves the argument as it was |
:::

A function with an `edit` or `take` parameter cannot be used as a value, for example as the function given to `map` (U2021). Wrap the call in a function with plain parameters, as `applied` does in [section 12.7](#s12-7), and pass that function instead. A lambda cannot do it: its body is not a statement, so a call with `edit` or `take` there is U3013.

## 12.4 Running work at the same time: `together`

Asking two warehouses how many units they hold takes two round trips. They do not depend on each other, so they can happen at the same time. A `together` block runs its branches as concurrent tasks, and `together for` runs one task per element of a list. Every task ends before the block does, so no task outlives the code that started it.

This step uses a capability, as in [chapter 8, Capabilities](/learn/capabilities/): `Inventory` is a warehouse's stock service, and each warehouse is a binding of it, `@north` and `@south`. The handler `shelves` answers from a map, and `offline` always fails.

:::steps
```una include="steps/04-together/src/stock.una" title="steps/04-together/src/stock.una" verified="check, run, test"
module stock

kind StoreError = | Timeout

--- A warehouse's stock service: the units of a SKU on hand.
capability Inventory
  op on_hand(sku: Text) -> Int
    fails StoreError

--- A warehouse held in memory: 0 for a SKU it does not hold.
handler shelves(stock: Map[Text, Int]) for Inventory
  op on_hand(sku) = stock.get(key: sku).or_else(default: 0)

--- A warehouse that never answers.
handler offline() for Inventory
  op on_hand(sku) = fail Timeout

--- The units of `sku` in both warehouses. The two are asked at the same time.
total_on_hand(sku: Text) -> Int
  uses @north: Inventory[on_hand]
  uses @south: Inventory[on_hand]
  fails StoreError
=
  together
    let up = @north.on_hand(sku)
      if error pass
    let down = @south.on_hand(sku)
      if error pass
  up + down

--- One line per SKU, one task per SKU.
stock_lines(skus: List[Text]) -> List[Text]
  uses @north: Inventory[on_hand]
  uses @south: Inventory[on_hand]
  fails StoreError
=
  together for sku in skus
    let units = total_on_hand(sku)
      if error pass
    "{sku}: {units} units"

pub main() -> Unit
  uses @console: Console[print]
=
  let north = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 3)
  let south = empty_map().with(key: "LAMP-01", value: 2)
  let lines = stock_lines(["LAMP-01", "DESK-02", "CHAIR-09"]) with @north = shelves(north), @south = shelves(south)
    if error use ["a warehouse did not answer"]
  for line in lines
    @console.print(line)

example "a warehouse that does not answer fails the whole count"
  given @north = shelves(empty_map().with(key: "LAMP-01", value: 4))
  given @south = offline()
  do total_on_hand("LAMP-01")
  expect fails Timeout
```

Walkthrough:

1. **`together` with two `let` branches.** Each `let` is a task. A branch sees the bindings in scope before the block, and none of its siblings: the second branch cannot read `up`. After the block, `up` and `down` are bound, in branch order, as two `let` statements would bind them.
2. **`if error pass` under each branch.** A branch handles its failures as its `let` would outside the block. Here a failure of either warehouse makes the block fail, and `total_on_hand` fails with it.
3. **`together for sku in skus`.** One task per SKU. The body is a block whose last line is the element's value, so the result is a `List[Text]`, in the order of `skus`, whatever order the tasks finish in.
4. **Capabilities in tasks.** Each task uses the bindings of the enclosing function's `uses`. `main` installs both handlers for one call with `with`, and every task of that call sees them.
5. **The example.** `given @south = offline()` makes one warehouse fail, and the example expects the whole count to fail with `Timeout`.
:::

`una run .` prints:

```text include="steps/04-together/expected/output.txt"
LAMP-01: 6 units
DESK-02: 3 units
CHAIR-09: 0 units
```

`una test .` prints:

```text include="steps/04-together/expected/commands/test.txt#L2-L4"
example stock "a warehouse that does not answer fails the whole count" ... ok

1 example: 1 passed, 0 failed
```

### What the result can depend on

The result of a `together` block is the result of evaluating its tasks one after another, in order, and stopping at the first failure. Three rules give that:

:::steps
1. **Tasks share nothing that changes.** A task reads the values of the outer bindings as they were when the block started. Assigning an outer binding inside a task, or passing it as `edit` or `take`, is U2023. A task's own `let edit` bindings are its own.
2. **The first failure wins.** When a task fails, the tasks after it are cancelled, and the tasks before it run on. The block then fails with the failure of the lowest-indexed task that failed, exactly as a sequential run would have.
3. **The trace is in task order.** The operations the tasks perform are recorded task by task, in index order, whatever the interleaving. Only the moment each effect reaches the outside world, such as the order of two printed lines, depends on timing.
:::

`una run` runs the tasks one after another, in index order: the interpreter is the reference, and it stays deterministic. An executable built by `una build` runs each task on its own operating-system thread, with its own memory, and copies the values a task reads when it starts and its result when it ends ([chapter 13, Tools](/learn/tools/), shows `una build`). Both give the same result.

> [!NOTE]
> A `together` block has at least two branches, and only `let` branches (U2024). There are no task values, no detached tasks, no timeouts and no channels: `async` and `await` are not part of Una.

## 12.5 Limits: call depth and memory

Every run has two limits, and crossing either stops the run with U6003. The call depth counts the calls in progress: functions, lambdas, predicates, policies and handler operations. It is 10,000 by default. The memory budget is the memory a run holds beyond what it held at the start, 4096 MiB by default. Both can be changed for one run, with `--max-depth <n>` and `--max-memory <MiB>` on `una run`, `una test` and a built executable.

A loop's iterations are not calls. This step builds 20,000 shelf labels with a `for` loop, and runs with the default depth:

```una include="steps/05-loop/src/labels.una" title="steps/05-loop/src/labels.una" verified="check, run"
module labels

--- The shelf labels SKU-1 to SKU-`count`. A loop builds them: its iterations are not calls,
--- so the call depth stays the same however many labels there are.
labels(count: Int) -> List[Text]
=
  let edit made: List[Text] = []
  for n in 1..count
    made = made.append(item: "SKU-{n}")
  made

pub main() -> Unit
  uses @console: Console[print]
=
  let printed = labels(20000)
  let last = printed.at(index: 19999)
    if none use "none"
  @console.print("{printed.len} labels, the last {last}")
```

`una run .` prints:

```text include="steps/05-loop/expected/output.txt"
20000 labels, the last SKU-20000
```

The same labels built by recursion need one call in progress per label. The program still checks, since the checker does not count calls, but the run stops:

```diff include="steps/05-loop..steps/06-recursion:src/labels.una" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -1,13 +1,7 @@
 module labels
 
---- The shelf labels SKU-1 to SKU-`count`. A loop builds them: its iterations are not calls,
---- so the call depth stays the same however many labels there are.
-labels(count: Int) -> List[Text]
-=
-  let edit made: List[Text] = []
-  for n in 1..count
-    made = made.append(item: "SKU-{n}")
-  made
+--- The shelf labels SKU-1 to SKU-`count`, built by recursion: one call in progress per label.
+labels(count: Int) -> List[Text] = if count == 0 then [] else labels(count - 1).append(item: "SKU-{count}")
 
 pub main() -> Unit
   uses @console: Console[print]
```

`una --json run .` prints the run as one JSON document, with the abort in it:

```text include="steps/06-recursion/expected/commands/run.txt"
$ una --json run .
{"schema":"una.run/1","tier":1,"status":"aborted","output":[],"failure":null,"diagnostics":[{"schema":"una.diagnostic/1","code":"U6003","severity":"error","domain":"runtime","message":"this call exceeds the maximum call depth of 10000","primary":{"file":"src/labels.una","start":{"line":4,"col":63},"end":{"line":4,"col":80}},"related":[],"repairs":[],"explain":"una explain U6003"}],"trace":[]}
```

`status` is `aborted`, `diagnostics` holds U6003 at the call that went one level too deep, and nothing was printed. In a terminal, `una run .` shows the same diagnostic on stderr and exits with code 1. For more, run:

```sh
una explain U6003
```

It explains both limits, and ends with a failing and a fixed example.

The memory budget is checked at each call and at each iteration of a loop. A run over it stops with U6003 too, and the message names the limit in MiB. Where exactly the memory runs out depends on the machine, so a test should not rely on it. The depth limit is exact.

The checker cannot see either limit: how deep a recursion goes, and how much a run holds, depend on the values the program meets when it runs. So U6003 is never a diagnostic of `una check`. Under `una test`, an example whose `do` line crosses a limit fails, and its report says that the `do` line aborted.

> [!TIP]
> Build long lists with a `for` loop, as `labels` does, and keep recursion for structures that are shallow, such as a tree of categories. A run that only needs more depth can raise `--max-depth`, up to what a stack of 1 GiB holds.

## 12.6 Day-to-day: an end-of-day stock count

Now the program from the start of the chapter. Two sites close their day. Each has the counts it opened with and the movements its tills recorded: sales, which lower a count, and deliveries, which raise it. A movement for a SKU the site does not stock, or a sale of more units than are counted, is rejected and reported, and must leave the count as it was. The sites are independent, so they are closed at the same time.

The design follows from that. One `Ledger` per site holds the running counts, and one function applies a movement to it through an `edit` parameter. When the day is done, the ledger is closed into a `Report` with `take`, and `together for` closes every site at once.

```una include="day-to-day/src/stockcount.una#L1-L27" title="day-to-day/src/stockcount.una" caption="the kinds"
module stockcount

--- One movement of stock at a site: a SKU and a change in units, negative for a sale.
pub kind Movement
  sku: Text
  change: Int

--- Why a movement could not be applied to a ledger.
pub kind CountError = UnknownSku(sku: Text) | Oversold(sku: Text, wanted: Int, left: Int)

--- The running count of one site: the units of each SKU, and how many movements it took.
pub kind Ledger
  site: Text
  counts: Map[Text, Int]
  applied: Int

--- One site's day: its opening counts and the movements its tills recorded.
pub kind Day
  site: Text
  opening: Map[Text, Int]
  movements: List[Movement]

--- What a closed day reports: a summary, one line per movement, and the closing counts.
pub kind Report
  summary: Text
  lines: List[Text]
  closing: Map[Text, Int]
```

A `Movement` holds a signed change, so a sale and a delivery are one kind. `CountError` carries what a person needs to correct the count: the SKU, and for an oversold item the units sold and counted. `Report` keeps the closing counts as a map, which [chapter 5, Collections](/learn/collections/), introduced.

**Applying one movement.** `apply` takes the ledger with `edit` and fails with `CountError`. Its `ensures` promises one more applied movement, which holds only when it returns: a rejected movement is a failure, and then the ledger is left as it was.

```una include="day-to-day/src/stockcount.una#apply" title="day-to-day/src/stockcount.una"
--- Applies one movement to the ledger. On failure the ledger is left as it was.
pub apply(edit ledger: Ledger, movement: Movement) -> Text
  ensures ledger.applied == old(ledger).applied + 1
  fails CountError
=
  let left = ledger.counts.get(key: movement.sku)
    if none fail UnknownSku(sku: movement.sku)
  let next = left + movement.change
  if next < 0
    fail Oversold(sku: movement.sku, wanted: -movement.change, left: left)
  ledger.counts = ledger.counts.with(key: movement.sku, value: next)
  ledger.applied = ledger.applied + 1
  "{movement.sku} {left} -> {next}"
```

The function changes two fields, `counts` and `applied`, and returns a line for the report, such as `LAMP-01 4 -> 3`. The checks come first, so a movement that fails changes nothing, but the guarantee does not depend on that order: a failure after the assignments would discard them too.

**Replaying a day.** `close_day` keeps the ledger and the report's lines in two `let edit` bindings, and replays the movements in order. A rejected movement becomes a line of its own: `if error use` gives the statement's value when the call fails, and `error` is the `CountError` that `reason` turns into words.

```una include="day-to-day/src/stockcount.una#reason..close_day" title="day-to-day/src/stockcount.una"
--- What a person reads for a movement that was not applied.
pub reason(failure: CountError) -> Text
=
  when failure
    is UnknownSku(sku) -> "no product has the SKU {sku}"
    is Oversold(sku, wanted, left) -> "{wanted} of {sku} sold, {left} counted"

--- Closes the ledger: the report keeps its counts, and nothing can update the ledger after.
pub close(take ledger: Ledger, lines: List[Text]) -> Report
=
  let rejected = lines.len - ledger.applied
  let summary = "{ledger.site}: {ledger.applied} applied, {rejected} rejected"
  Report(summary: summary, lines: lines, closing: ledger.counts)

--- Replays one site's day, movement by movement.
pub close_day(day: Day) -> Report
=
  let edit ledger = Ledger(site: day.site, counts: day.opening, applied: 0)
  let edit lines: List[Text] = []
  for movement in day.movements
    let line = apply(edit ledger, movement: movement)
      if error use "rejected: {reason(error)}"
    lines = lines.append(item: line)
  close(take ledger, lines: lines)
```

`close` takes the ledger. After `close(take ledger, lines: lines)`, no later line of `close_day` can apply another movement to a closed day: the checker would report U2017 (section [12.8](#s12-8) shows it). The number of rejected movements is the number of lines minus the applied ones, since every movement gives one line.

Why an `edit` parameter, and not a function that returns a new ledger? Both would work. A function `apply(ledger: Ledger, movement: Movement) -> Ledger` would need a second result for the report's line, and every call would have to rebind the ledger by hand: `ledger = apply(ledger, …)`. Forgetting the rebinding would silently drop the movement. With `edit`, the call cannot forget, the line is the result, and the `ensures` clause can compare the ledger before and after with `old`.

`close_day` itself takes a plain `Day`. It builds its own ledger from the day's opening counts, so a caller's `Day` is never changed, and two calls with the same day give the same report. That is what lets `close_all` run the days as separate tasks.

**Closing every site at once.** One task per day. Each task builds its own ledger inside `close_day`, so the tasks share nothing that changes, and the reports come back in the order of `days`.

```una include="day-to-day/src/stockcount.una#close_all" title="day-to-day/src/stockcount.una"
--- Closes every site's day at once, one task per site. The reports come back in site order.
pub close_all(days: List[Day]) -> List[Report]
=
  together for day in days
    close_day(day)
```

**The days, and running it.** `sale` and `delivery` make movements with readable names. `north_day` and `south_day` hold the sample data, and `main` prints each report.

```una include="day-to-day/src/stockcount.una#sale..main" title="day-to-day/src/stockcount.una"
--- A sale of `units` units: a negative movement.
pub sale(sku: Text, units: Int) -> Movement = Movement(sku: sku, change: -units)

--- A delivery of `units` units: a positive movement.
pub delivery(sku: Text, units: Int) -> Movement = Movement(sku: sku, change: units)

--- The north site's day, as its tills recorded it.
north_day() -> Day
=
  let opening = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)
  let movements = [sale("LAMP-01", units: 1), sale("DESK-02", units: 2), delivery("LAMP-01", units: 6)]
  Day(site: "north", opening: opening, movements: movements)

--- The south site's day.
south_day() -> Day
=
  let opening = empty_map().with(key: "LAMP-01", value: 2)
  let movements = [sale("CHAIR-09", units: 1), sale("LAMP-01", units: 2)]
  Day(site: "south", opening: opening, movements: movements)

pub main() -> Unit
  uses @console: Console[print]
=
  let reports = close_all([north_day(), south_day()])
  for report in reports
    @console.print(report.summary)
    for line in report.lines
      @console.print("  {line}")
    @console.print("  closing {report.closing}")
```

`una run .` prints the report shown under "What you'll build". The north site rejects a sale of two desks with one counted, and the south site rejects a SKU it does not stock. Each closing map is the count after the movements that were applied, in SKU order, since a map keeps its keys in order.

Built with `una build`, the same program closes the two sites on two threads. The report is the same, line for line, because `main` prints only after `close_all` has returned every report, in site order.

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/stockcount.una" title="day-to-day/src/stockcount.una" caption="the whole program" verified="check, run, test"
module stockcount

--- One movement of stock at a site: a SKU and a change in units, negative for a sale.
pub kind Movement
  sku: Text
  change: Int

--- Why a movement could not be applied to a ledger.
pub kind CountError = UnknownSku(sku: Text) | Oversold(sku: Text, wanted: Int, left: Int)

--- The running count of one site: the units of each SKU, and how many movements it took.
pub kind Ledger
  site: Text
  counts: Map[Text, Int]
  applied: Int

--- One site's day: its opening counts and the movements its tills recorded.
pub kind Day
  site: Text
  opening: Map[Text, Int]
  movements: List[Movement]

--- What a closed day reports: a summary, one line per movement, and the closing counts.
pub kind Report
  summary: Text
  lines: List[Text]
  closing: Map[Text, Int]

--- Applies one movement to the ledger. On failure the ledger is left as it was.
pub apply(edit ledger: Ledger, movement: Movement) -> Text
  ensures ledger.applied == old(ledger).applied + 1
  fails CountError
=
  let left = ledger.counts.get(key: movement.sku)
    if none fail UnknownSku(sku: movement.sku)
  let next = left + movement.change
  if next < 0
    fail Oversold(sku: movement.sku, wanted: -movement.change, left: left)
  ledger.counts = ledger.counts.with(key: movement.sku, value: next)
  ledger.applied = ledger.applied + 1
  "{movement.sku} {left} -> {next}"

--- What a person reads for a movement that was not applied.
pub reason(failure: CountError) -> Text
=
  when failure
    is UnknownSku(sku) -> "no product has the SKU {sku}"
    is Oversold(sku, wanted, left) -> "{wanted} of {sku} sold, {left} counted"

--- Closes the ledger: the report keeps its counts, and nothing can update the ledger after.
pub close(take ledger: Ledger, lines: List[Text]) -> Report
=
  let rejected = lines.len - ledger.applied
  let summary = "{ledger.site}: {ledger.applied} applied, {rejected} rejected"
  Report(summary: summary, lines: lines, closing: ledger.counts)

--- Replays one site's day, movement by movement.
pub close_day(day: Day) -> Report
=
  let edit ledger = Ledger(site: day.site, counts: day.opening, applied: 0)
  let edit lines: List[Text] = []
  for movement in day.movements
    let line = apply(edit ledger, movement: movement)
      if error use "rejected: {reason(error)}"
    lines = lines.append(item: line)
  close(take ledger, lines: lines)

--- Closes every site's day at once, one task per site. The reports come back in site order.
pub close_all(days: List[Day]) -> List[Report]
=
  together for day in days
    close_day(day)

--- A sale of `units` units: a negative movement.
pub sale(sku: Text, units: Int) -> Movement = Movement(sku: sku, change: -units)

--- A delivery of `units` units: a positive movement.
pub delivery(sku: Text, units: Int) -> Movement = Movement(sku: sku, change: units)

--- The north site's day, as its tills recorded it.
north_day() -> Day
=
  let opening = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)
  let movements = [sale("LAMP-01", units: 1), sale("DESK-02", units: 2), delivery("LAMP-01", units: 6)]
  Day(site: "north", opening: opening, movements: movements)

--- The south site's day.
south_day() -> Day
=
  let opening = empty_map().with(key: "LAMP-01", value: 2)
  let movements = [sale("CHAIR-09", units: 1), sale("LAMP-01", units: 2)]
  Day(site: "south", opening: opening, movements: movements)

pub main() -> Unit
  uses @console: Console[print]
=
  let reports = close_all([north_day(), south_day()])
  for report in reports
    @console.print(report.summary)
    for line in report.lines
      @console.print("  {line}")
    @console.print("  closing {report.closing}")

--- A north ledger that counts `units` of LAMP-01 and nothing else, for the examples.
lamps(units: Int) -> Ledger = Ledger(site: "north", counts: empty_map().with(key: "LAMP-01", value: units), applied: 0)

--- `apply` through a copy, since a `do` line cannot pass `edit`.
applied(ledger: Ledger, movement: Movement) -> Ledger
  fails CountError
=
  let edit copy = ledger
  let receipt = apply(edit copy, movement: movement)
    if error pass
  copy

example "a sale lowers the count of its SKU"
  do applied(lamps(4), movement: sale("LAMP-01", units: 1))
  expect result.counts.get(key: "LAMP-01") == Some(3)
  expect result.applied == 1

example "selling more than is counted is Oversold"
  do applied(lamps(4), movement: sale("LAMP-01", units: 9))
  expect fails Oversold

example "a rejected movement leaves the counts as they were"
  do close_day(Day(site: "south", opening: empty_map().with(key: "LAMP-01", value: 2), movements: [sale("LAMP-01", units: 5)]))
  expect result.closing == empty_map().with(key: "LAMP-01", value: 2)
  expect result.summary == "south: 0 applied, 1 rejected"

example "closing every day at once gives the reports in site order"
  do close_all([north_day(), south_day()])
  expect result == [close_day(north_day()), close_day(south_day())]
```

## 12.7 Testing it

An example's `do` line cannot pass `edit`: it is not a statement, and it has no editable binding of its own. So the examples reach `apply` through a small private function, `applied`, which copies the ledger into a `let edit` binding, applies the movement and returns the copy. `lamps` builds the ledger the examples start from.

```una include="day-to-day/src/stockcount.una#L104-L132" title="day-to-day/src/stockcount.una" caption="the examples"
--- A north ledger that counts `units` of LAMP-01 and nothing else, for the examples.
lamps(units: Int) -> Ledger = Ledger(site: "north", counts: empty_map().with(key: "LAMP-01", value: units), applied: 0)

--- `apply` through a copy, since a `do` line cannot pass `edit`.
applied(ledger: Ledger, movement: Movement) -> Ledger
  fails CountError
=
  let edit copy = ledger
  let receipt = apply(edit copy, movement: movement)
    if error pass
  copy

example "a sale lowers the count of its SKU"
  do applied(lamps(4), movement: sale("LAMP-01", units: 1))
  expect result.counts.get(key: "LAMP-01") == Some(3)
  expect result.applied == 1

example "selling more than is counted is Oversold"
  do applied(lamps(4), movement: sale("LAMP-01", units: 9))
  expect fails Oversold

example "a rejected movement leaves the counts as they were"
  do close_day(Day(site: "south", opening: empty_map().with(key: "LAMP-01", value: 2), movements: [sale("LAMP-01", units: 5)]))
  expect result.closing == empty_map().with(key: "LAMP-01", value: 2)
  expect result.summary == "south: 0 applied, 1 rejected"

example "closing every day at once gives the reports in site order"
  do close_all([north_day(), south_day()])
  expect result == [close_day(north_day()), close_day(south_day())]
```

Each example checks one fact of the chapter:

- **"a sale lowers the count of its SKU"** checks `apply` through `applied`: the count and the number of applied movements.
- **"selling more than is counted is Oversold"** expects the failure with `expect fails Oversold`. `applied` passes the failure on with `if error pass`, so the example sees it.
- **"a rejected movement leaves the counts as they were"** closes a day whose only movement fails, and checks that the closing counts are the opening counts.
- **"closing every day at once gives the reports in site order"** compares `close_all` with closing the days one after another. This is the guarantee of `together for`, stated as an example.

None of the examples needs a fake service: the program has no capability but the console, and the console is used only in `main`. Every function under test takes its input as values and returns its result, which is what makes each one easy to check on its own.

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L7"
example stockcount "a sale lowers the count of its SKU" ... ok
example stockcount "selling more than is counted is Oversold" ... ok
example stockcount "a rejected movement leaves the counts as they were" ... ok
example stockcount "closing every day at once gives the reports in site order" ... ok

4 examples: 4 passed, 0 failed
```

## 12.8 Common mistakes

Each mistake below is a small change to `day-to-day/src/stockcount.una`, followed by what `una check .` reports.

:::mistake
**1. Leaving out `edit` at the call (U2020).** Write `apply(ledger, …)` in `close_day`:

```diff include="day-to-day..mistakes/1:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -62,3 +62,3 @@
   for movement in day.movements
-    let line = apply(edit ledger, movement: movement)
+    let line = apply(ledger, movement: movement)
       if error use "rejected: {reason(error)}"
```

```text include="mistakes/1/expected/rendered.txt#L1,L8"
[U2020] Error: parameter `ledger` of `apply` is declared `edit`, so its argument is written `edit ledger`
    │ Help: repair 1: write `edit ledger`; edit src/stockcount.una:63:22..63:28 to "edit ledger"
```

*Why:* the call must show which bindings it may change, so a reader never has to open `apply` to find out.

*Fix:* write `edit ledger`. The repair carries the edit, and `una fix .` applies it.

See [U2020](/docs/errors/U2020/).
:::

:::mistake
**2. Passing a plain `let` as `edit` (U2019).** Declare the ledger with `let` instead of `let edit`:

```diff include="day-to-day..mistakes/2:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -59,3 +59,3 @@
 =
-  let edit ledger = Ledger(site: day.site, counts: day.opening, applied: 0)
+  let ledger = Ledger(site: day.site, counts: day.opening, applied: 0)
   let edit lines: List[Text] = []
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U2019] Error: `ledger` is not editable; declare it `let edit ledger`, or the parameter `edit ledger`
```

*Why:* an `edit` argument is assigned when the call returns, and a plain `let` binding is never assigned.

*Fix:* `let edit ledger = …`. The diagnostic points at the argument, and the fix is at the declaration.

See [U2019](/docs/errors/U2019/).
:::

:::mistake
**3. Using a value after `take` (U2017).** Read the ledger's counts after closing it:

```diff include="day-to-day..mistakes/3:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -65,3 +65,4 @@
     lines = lines.append(item: line)
-  close(take ledger, lines: lines)
+  let report = close(take ledger, lines: lines)
+  Report(summary: report.summary, lines: report.lines, closing: ledger.counts)
 
```

```text include="mistakes/3/expected/rendered.txt"
[U2017] Error: `ledger` was passed by `take`, so it cannot be used afterwards
    ╭─[ src/stockcount.una:67:65 ]
    │
 66 │   let report = close(take ledger, lines: lines)
    │                           ───┬──
    │                              ╰──── passed by `take` here
 67 │   Report(summary: report.summary, lines: report.lines, closing: ledger.counts)
    │                                                                 ───┬──
    │                                                                    ╰──── `ledger` was passed by `take`, so it cannot be used afterwards
    │
    │ Note: run `una explain U2017` for an explanation
────╯
```

*Why:* `take` gave the ledger to `close`, and the diagnostic shows both places: where it was taken and where it is used.

*Fix:* use what `close` returns. `report.closing` already holds the counts.

See [U2017](/docs/errors/U2017/).
:::

:::mistake
**4. Wrapping an `edit` call in `attempt` (U3013).** Keep the outcome of `apply` as a `Result`:

```diff include="day-to-day..mistakes/4:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -62,4 +62,4 @@
   for movement in day.movements
-    let line = apply(edit ledger, movement: movement)
-      if error use "rejected: {reason(error)}"
+    let outcome = attempt apply(edit ledger, movement: movement)
+    let line = if outcome.is_ok() then "applied" else "rejected"
     lines = lines.append(item: line)
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U3013] Error: `apply` is called with `edit` or `take`, so the call must be the whole expression of a statement or `let`; bind its result with `let` first
```

*Why:* a call with an `edit` or `take` argument is the whole expression of its statement, so that the binding it changes is updated on that line and nowhere else.

*Fix:* handle the failure with a clause under the call, as `close_day` does with `if error use`. To pass the failure on, use `if error pass`.

See [U3013](/docs/errors/U3013/).
:::

:::mistake
**5. Counting in a shared binding inside `together` (U2023).** Count the closed days in an outer `let edit`:

```diff include="day-to-day..mistakes/5:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -70,3 +70,5 @@
 =
+  let edit closed = 0
   together for day in days
+    closed = closed + 1
     close_day(day)
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U2023] Error: `closed` is declared outside this `together` task, which captures its value and cannot change it, so it cannot be assigned here; return the new value from the task instead
```

*Why:* each task captures the values around it and runs on its own, so an assignment to an outer binding would be a race between tasks.

*Fix:* return what each task computes, and combine the results after the block. Here the count is `reports.len`.

See [U2023](/docs/errors/U2023/).
:::

:::mistake
**6. `old` outside `ensures` (U2012).** Use `old(ledger)` in the body of `apply`:

```diff include="day-to-day..mistakes/6:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -39,3 +39,3 @@
   ledger.counts = ledger.counts.with(key: movement.sku, value: next)
-  ledger.applied = ledger.applied + 1
+  ledger.applied = old(ledger).applied + 1
   "{movement.sku} {left} -> {next}"
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U2012] Error: `old` is allowed only in `ensures` clauses
```

*Why:* `old` names the value on entry for the promise in the header. In the body, the parameter is simply its current value.

*Fix:* write `ledger.applied + 1`. To keep the entry value for later in the body, bind it first: `let before = ledger.applied`.

See [U2012](/docs/errors/U2012/).
:::

## 12.9 For agents

:::agents
`una --json check .` gives each diagnostic of this chapter with its code and exact place. For mistake 1:

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U2020","severity":"error","domain":"types","message":"parameter `ledger` of `apply` is declared `edit`, so its argument is written `edit ledger`","primary":{"file":"src/stockcount.una","start":{"line":63,"col":22},"end":{"line":63,"col":28}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"write `edit ledger`","edit":{"file":"src/stockcount.una","start":{"line":63,"col":22},"end":{"line":63,"col":28},"replacement":"edit ledger"}}],"explain":"una explain U2020"}],"fixable":1}
```

The repair carries an `edit` that `una fix .` applies, so the document reports `"fixable":1`. U2017, U2019 and U2023 carry no edit: the right change depends on intent. `una --json run .` reports U6003 with `"status":"aborted"`, as in [section 12.5](#s12-5). The compact rule: *a call that changes a binding names it with `edit`, on a line of its own; a binding given with `take` is not used again until it is assigned; a `together` task returns its result and never assigns what is outside it.*
:::

## 12.10 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's example added, and a stub of what to write. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one line on the header line.

::::exercise
**Exercise 1: a recount.** A stocktake finds 7 lamps on the shelf where the ledger says 4. Write the body of `recount`, which sets the count of a SKU to what was counted. A recount is not a movement, so `applied` does not change, and the header promises it. The start package has the stub, a function for the example, and the example:

```una include="exercises/1/start/src/stockcount.una#recount..recounted" title="exercises/1/start/src/stockcount.una"
--- A stocktake correction: sets the count of `sku` to the `units` counted on the shelf.
--- It is not a movement, so `applied` does not change. Exercise 1: write the body.
pub recount(edit ledger: Ledger, sku: Text, units: Int) -> Unit
  ensures ledger.applied == old(ledger).applied
=
  unit

--- `recount` through a copy, for the example.
recounted(ledger: Ledger, sku: Text, units: Int) -> Ledger
=
  let edit copy = ledger
  recount(edit copy, sku: sku, units: units)
  copy
```

```una include="exercises/1/start/src/stockcount.una#L148-L151" title="exercises/1/start/src/stockcount.una"
example "a recount sets the count and is not a movement"
  do recounted(Ledger(site: "north", counts: empty_map().with(key: "LAMP-01", value: 4), applied: 2), sku: "LAMP-01", units: 7)
  expect result.counts.get(key: "LAMP-01") == Some(7)
  expect result.applied == 2
```

:::hint
*Hint:* one assignment to `ledger.counts`, with the map's `with`. The verifier proves the `ensures` once the body leaves `applied` alone.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L6-L10"
example stockcount "a recount sets the count and is not a movement" ... FAILED
  src/stockcount.una:150: expect result.counts.get(key: "LAMP-01") == Some(7)
  it is false, with `result` = `Ledger(site: "north", counts: {"LAMP-01": 4}, applied: 2)`

5 examples: 4 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Replace the body:

```diff include="exercises/1/start..exercises/1/answer:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -134,3 +134,3 @@
 --- A stocktake correction: sets the count of `sku` to the `units` counted on the shelf.
---- It is not a movement, so `applied` does not change. Exercise 1: write the body.
+--- It is not a movement, so `applied` does not change.
 pub recount(edit ledger: Ledger, sku: Text, units: Int) -> Unit
@@ -138,3 +138,3 @@
 =
-  unit
+  ledger.counts = ledger.counts.with(key: sku, value: units)
 
```
:::
::::

::::exercise
**Exercise 2: a delivery note, all or nothing.** A delivery note lists several movements, and the warehouse accepts it whole or not at all. Write the body of `apply_note`, which applies every movement of a note to the ledger and gives one line per movement, and fails when any movement fails. The start package has the stub, a function for the examples, and two examples:

```una include="exercises/2/start/src/stockcount.una#apply_note..after_note" title="exercises/2/start/src/stockcount.una"
--- Applies a delivery note, every movement or none, and gives one line per movement.
--- Exercise 2: write the body.
pub apply_note(edit ledger: Ledger, movements: List[Movement]) -> List[Text]
  fails CountError
=
  []

--- `apply_note` through a copy, for the examples: the ledger after the note, or before it.
after_note(ledger: Ledger, movements: List[Movement]) -> Ledger
=
  let edit copy = ledger
  let lines = apply_note(edit copy, movements: movements)
    if error use []
  copy
```

```una include="exercises/2/start/src/stockcount.una#L149-L157" title="exercises/2/start/src/stockcount.una"
example "a note whose movements all apply applies all of them"
  do after_note(lamps(4), movements: [delivery("LAMP-01", units: 6), sale("LAMP-01", units: 2)])
  expect result.counts.get(key: "LAMP-01") == Some(8)
  expect result.applied == 2

example "a note with one bad movement applies none of them"
  do after_note(lamps(4), movements: [delivery("LAMP-01", units: 6), sale("DESK-02", units: 1)])
  expect result.counts.get(key: "LAMP-01") == Some(4)
  expect result.applied == 0
```

The second example passes on the stub, which applies nothing. Your answer must keep it passing.

:::hint
*Hint:* a `for` loop that calls `apply` with `if error pass`. You do not need to undo anything: when `apply_note` fails, the caller's ledger is left as it was before the call.
:::

Check your answer with `una test .`. An answer that skips the bad movement with `if error use` fails the second example.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Replace the body:

```diff include="exercises/2/start..exercises/2/answer:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -134,3 +134,2 @@
 --- Applies a delivery note, every movement or none, and gives one line per movement.
---- Exercise 2: write the body.
 pub apply_note(edit ledger: Ledger, movements: List[Movement]) -> List[Text]
@@ -138,3 +137,8 @@
 =
-  []
+  let edit lines: List[Text] = []
+  for movement in movements
+    let line = apply(edit ledger, movement: movement)
+      if error pass
+    lines = lines.append(item: line)
+  lines
 
```

A movement that fails ends the loop and the function. The ledger the loop changed is discarded with the failure, so the caller's ledger never holds half a note.
:::
::::

::::exercise
**Exercise 3: a strict close.** Head office wants a stricter close: every movement of every site must apply, or the close fails and names the first site, in list order, that did not add up. The start package has `strict_day`, which fails at a site's first bad movement, a kind for the failure, a stub of `close_strict`, and `blamed`, which runs `close_strict` and names the site it blames, or `none` when it does not fail:

```una include="exercises/3/start/src/stockcount.una#CloseError..site_of" title="exercises/3/start/src/stockcount.una"
--- Why a strict close failed: the first site, in list order, with a movement that did not apply.
pub kind CloseError = | Short(site: Text, cause: CountError)

--- Replays one site's day, and fails at the first movement that does not apply.
pub strict_day(day: Day) -> Report
  fails CountError
=
  let edit ledger = Ledger(site: day.site, counts: day.opening, applied: 0)
  let edit lines: List[Text] = []
  for movement in day.movements
    let line = apply(edit ledger, movement: movement)
      if error pass
    lines = lines.append(item: line)
  close(take ledger, lines: lines)

--- Closes every day at once, strictly. Exercise 3: use `strict_day`, one task per day.
pub close_strict(days: List[Day]) -> List[Report]
  fails CloseError
=
  close_all(days)

--- The site that `close_strict` blames, or "none".
blamed(days: List[Day]) -> Text
=
  let outcome = attempt close_strict(days)
  when outcome
    is Ok -> "none"
    is Err(failure) -> site_of(failure)

site_of(failure: CloseError) -> Text
=
  when failure
    is Short(site, cause) -> site
```

```una include="exercises/3/start/src/stockcount.una#L168-L174" title="exercises/3/start/src/stockcount.una"
example "a strict close blames the first short site in list order"
  do blamed([Day(site: "east", opening: empty_map(), movements: []), south_day(), north_day()])
  expect result == "south"

example "a strict close of days that all apply blames no site"
  do blamed([Day(site: "east", opening: empty_map().with(key: "LAMP-01", value: 1), movements: [sale("LAMP-01", units: 1)])])
  expect result == "none"
```

In the first example, both the south and the north days fail. The close must name `south`, the first of them in the list.

:::hint
*Hint:* one task per day, as in `close_all`, with `strict_day` in each, and a clause that translates its failure into `Short` with the day's site. You do not need to find the first failure yourself.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Replace the body:

```diff include="exercises/3/start..exercises/3/answer:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -148,3 +148,3 @@
 
---- Closes every day at once, strictly. Exercise 3: use `strict_day`, one task per day.
+--- Closes every day at once, strictly: one task per day.
 pub close_strict(days: List[Day]) -> List[Report]
@@ -152,3 +152,5 @@
 =
-  close_all(days)
+  together for day in days
+    strict_day(day)
+      if error fail Short(site: day.site, cause: error)
 
```

Two tasks fail, and the block fails with the failure of the lowest-indexed one, as a sequential run would. In an executable, the tasks may finish in any order, and the answer is the same.
:::
::::

## 12.11 Recap

:::recap
- A `let` binding is a value, and a copy is a value of its own.
- `let edit` makes a binding editable: assign it or its fields with `=`, and a list element with `edit xs.set(…)`.
- An `edit` parameter passes a value in and out. The call writes `edit`, and a failed call leaves the argument unchanged.
- `old(x)` is an `edit` parameter's value on entry, and only `ensures` may use it.
- After `take x`, `x` is not used again until it is assigned.
- `together` and `together for` give the result of a sequential run, and the first failure in order wins.
- A task returns its result and never assigns the bindings around it.
- U6003 stops a run at the call depth or the memory budget. Build long lists with loops.
:::

## 12.12 Reference

:::reference
- Construct pages: [`let edit` and `edit` parameters](/docs/language/control-flow/let-edit/), [`take`](/docs/language/control-flow/take/), [`together`](/docs/language/control-flow/together/), [`for`](/docs/language/control-flow/for/), [`ensures`](/docs/language/functions/ensures/), [`attempt`](/docs/language/errors/attempt/), [`capability` and `op`](/docs/language/capabilities/capability/), [`handler`](/docs/language/capabilities/handler/), [`with`](/docs/language/capabilities/with/), [`example`](/docs/language/examples/example/)
- Prelude: [`set`, `append`, `Map` and `with`](/docs/std/)
- Diagnostics: [U2012](/docs/errors/U2012/), [U2017](/docs/errors/U2017/), [U2018](/docs/errors/U2018/), [U2019](/docs/errors/U2019/), [U2020](/docs/errors/U2020/), [U2021](/docs/errors/U2021/), [U2023](/docs/errors/U2023/), [U2024](/docs/errors/U2024/), [U3013](/docs/errors/U3013/), and at run time [U6003](/docs/errors/U6003/) (call depth or memory)
- Command line: [`una run`](/docs/cli/run/), [`una test`](/docs/cli/test/), [`una build`](/docs/cli/build/)
- Specification: [memory model](/docs/spec/17-memory-model/), [structured concurrency](/docs/spec/19-structured-concurrency/), [dynamic semantics, limits](/docs/spec/11-dynamic-semantics/), [native backend](/docs/spec/16-native-backend/)
:::
