---
learn: "6"
title: Failure
editions: ["0.2"]
codes: [U0101, U0102, U2001, U2007, U3007, U3008, U3009, U3013]
time: 35
builds: An order-intake step that accepts or rejects each line of an order batch
prerequisites: ["3", "4", "5"]
template: 2
---

# 6 Failure

Real programs spend much of their code on what goes wrong: input that does not parse, a product that does not exist, a service that does not answer. In Una a failure is an ordinary value of a kind you declare, a function's header says which kind it can fail with, and every call that can fail is followed by a line that says what to do about it. This chapter shows how to design those kinds, how to handle and translate failures between layers, and how to process a batch in which some items fail and others succeed.

## What you'll build

:::build
An order-intake step for a small store. It reads order lines such as `LAMP-01, 2`, checks each one against an inventory service, and reports every line, accepted or rejected, with a reason a person can act on:

```text include=day-to-day/expected/output.txt
ok      2 x LAMP-01
reject  3 of DESK-02 wanted, 1 left
reject  no product has the SKU CHAIR-09
reject  the quantity in 'LAMP-01, two' is not a whole number above 0
reject  cannot read the line 'LAMP-01'
```

You will learn to:

- declare an error kind whose variants carry what someone needs to fix the problem;
- choose among the five handling clauses, and translate a failure from one layer to the next;
- handle failures that come from a capability, such as a service that times out;
- turn a failure into a value with `attempt`, so one bad line does not stop a batch;
- test every failure path with examples and fake services.
:::

## Why it works this way

In many languages a function can fail in ways its signature does not show: an exception thrown three calls deep, a null returned on a path nobody tested, a panic on an index out of range. A reader has to read the bodies to find out what can go wrong, and a reviewer cannot tell from a diff whether a new failure was introduced.

Una moves all of that into view. Three rules do it:

:::steps
1. **A failure is a value of a sum kind.** You declare it like any other kind, and its variants can carry data.
2. **A header says what a function can fail with.** `fails OrderError` is part of the contract, next to `requires` and `uses`. A public function that does not say `fails` cannot fail, and the checker holds it to that.
3. **Every call that can fail is handled where it is made.** The next line, indented, says what happens: recover with a value, pass the failure on, or turn it into a failure of your own kind. Nothing propagates unless that line says so.
:::

The price is a few extra lines at each call. In return, the failure behavior of any function can be read from its header and its call sites, and the checker proves that no failure goes unhandled.

> [!KEY]
> Apart from running out of resources, nothing in Una fails at run time without the code saying so: division by zero and overflow are ruled out by proof (chapter 7), and there are no exceptions or panics to catch.

## 6.1 Declaring a failure: `fails` and `fail`

Start with the smallest real case: the quantity a customer types into an order form. It must be a whole number from 1 to 99. Three things can be wrong with it, so the error kind has three variants, and each carries what a message will need.

:::steps
```una include=steps/01-quantity/src/quantity.una title="steps/01-quantity/src/quantity.una" verified="check, run"
module quantity

--- Why a quantity was rejected. Each variant carries what the user needs to fix it.
kind QuantityError = NotANumber(raw: Text) | TooSmall(value: Int) | TooLarge(value: Int)

--- The quantity typed into an order form: a whole number from 1 to 99.
parse_quantity(raw: Text) -> Int
  fails QuantityError
=
  let n = raw.trim.to_int()
    if none fail NotANumber(raw)
  if n < 1
    fail TooSmall(value: n)
  else if n > 99
    fail TooLarge(value: n)
  else
    n

pub main() -> Unit
  uses @console: Console[print]
=
  let a = parse_quantity(" 3 ")
    if error use 0
  let b = parse_quantity("three")
    if error use 0
  @console.print("{a} and {b}")
```

Walkthrough:

1. **`kind QuantityError = …`.** An error kind is a sum kind like any other (chapter 4). Name the variants after what went wrong, not after where: `NotANumber`, not `ParseStep2Failed`.
2. **`fails QuantityError`.** This header line says that `parse_quantity` can fail, and with which kind. A function declares at most one error kind.
3. **`raw.trim.to_int()` then `if none fail NotANumber(raw)`.** `to_int` returns an `Option[Int]` (chapter 5): `None` when the text is not a number. The clause on the next line turns `None` into a failure of this function. After it, `n` is a plain `Int`.
4. **`fail TooSmall(value: n)`.** This ends the function with that variant. `fail` can stand in any branch, and the other branches give the value.
5. **`if error use 0`.** In `main`, each call is followed by a handling clause. Here it recovers with `0`. Section 6.2 shows the others.
:::

`una run .` prints:

```text include=steps/01-quantity/expected/output.txt
3 and 0
```

> [!NOTE] Private functions infer their error kind.
> `parse_quantity` is private, so its `fails` line could be left out: the checker infers it, and `una contract` prints the inferred header with the comment `-- inferred`. A `pub` function is a module's reviewed boundary, so it must declare `fails`. Write the line anyway whenever the failure is part of what a caller should know.

Remove the line to see it. The program checks and prints the same thing, and `una contract` shows the header the checker inferred:

```diff include=steps/01-quantity..steps/02-inferred:src/quantity.una context=1
--- a/src/quantity.una
+++ b/src/quantity.una
@@ -7,3 +7,2 @@
 parse_quantity(raw: Text) -> Int
-  fails QuantityError
 =
```

```text include=steps/02-inferred/expected/commands/contract.txt
$ una contract quantity.parse_quantity
--- The quantity typed into an order form: a whole number from 1 to 99.
parse_quantity(raw: Text) -> Int
  fails QuantityError -- inferred
```

So a private function without `fails` can still fail. Its contract is the inferred header, which `una contract` prints.

## 6.2 Handling a failure: the five clauses

A statement that can fail is followed by one or two clauses, each on its own line, indented one level below it:

| Clause | Use it when | After it |
| --- | --- | --- |
| `if error use v` | You can carry on with a sensible value | The statement's value is `v` on failure |
| `if error pass` | Your function fails with the *same* kind, and the caller should decide | The failure goes to your caller unchanged |
| `if error fail V(...)` | Your function fails with a *different* kind: translate it | Your function fails with `V`; inside `V(...)`, `error` is the original failure |
| `if none use v` | The statement gives an `Option`, and `None` has a sensible default | The value is unwrapped, or `v` |
| `if none fail V(...)` | `None` means the input is wrong | The value is unwrapped, or your function fails with `V` |

> [!IMPORTANT]
> When a statement can both fail and give an `Option`, `if error` comes first and `if none` second.

### Translating between layers with `error`

Most programs have layers: a low-level parser, a line reader above it, a batch report above that. Each layer has its own error kind, because each layer knows different things. The quantity parser knows the text was not a number, and the line reader also knows the line number. `if error fail` translates, and `error` keeps the original failure as a payload, so nothing is lost:

:::steps
```una include=steps/03-translate/src/upload.una title="steps/03-translate/src/upload.una" verified="check, run"
module upload

kind QuantityError = NotANumber(raw: Text) | OutOfRange(value: Int)

--- Why a line of an uploaded file was rejected, with its line number.
kind LineError = MissingQuantity(line: Int) | BadQuantity(line: Int, cause: QuantityError)

parse_quantity(raw: Text) -> Int
  fails QuantityError
=
  let n = raw.trim.to_int()
    if none fail NotANumber(raw)
  if n < 1 or n > 99
    fail OutOfRange(value: n)
  else
    n

--- The quantity on line `number` of an upload, `"SKU, quantity"`.
quantity_on_line(number: Int, text: Text) -> Int
  fails LineError
=
  let raw = text.split(on: ",").at(index: 1)
    if none fail MissingQuantity(line: number)
  parse_quantity(raw)
    if error fail BadQuantity(line: number, cause: error)

explain(e: LineError) -> Text
=
  when e
    is MissingQuantity(line) -> "line {line}: no quantity"
    is BadQuantity(line, cause) -> "line {line}: {cause_text(cause)}"

cause_text(c: QuantityError) -> Text
=
  when c
    is NotANumber(raw) -> "'{raw.trim}' is not a number"
    is OutOfRange(value) -> "{value} is not between 1 and 99"

show(number: Int, text: Text) -> Text
=
  let outcome = attempt quantity_on_line(number, text: text)
  when outcome
    is Ok(value) -> "line {number}: {value} units"
    is Err(failure) -> explain(failure)

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(show(1, text: "LAMP-01, 2"))
  @console.print(show(2, text: "LAMP-01"))
  @console.print(show(3, text: "LAMP-01, lots"))
  @console.print(show(4, text: "LAMP-01, 500"))
```

`una run .` prints:

```text include=steps/03-translate/expected/output.txt
line 1: 2 units
line 2: no quantity
line 3: 'lots' is not a number
line 4: 500 is not between 1 and 99
```

Walkthrough:

1. **`if none fail MissingQuantity(line: number)`.** `at(index: 1)` gives `None` when the line has no comma. That is the input's fault, so it becomes a failure.
2. **`if error fail BadQuantity(line: number, cause: error)`.** This is translation. `quantity_on_line` fails with `LineError`, and `parse_quantity` fails with `QuantityError`, so `if error pass` would not be allowed (see Common mistakes). `error` is the `QuantityError` that occurred, and it is kept as the `cause`.
3. **`explain` and `cause_text`.** Turning a failure into a message is an ordinary `when`. Because `when` must cover every variant, adding a variant to `LineError` later makes the checker point at every message function that needs a new arm.
:::

### Recovering with a default from a service

`if error use` and `if none use` are for places where carrying on is the right behavior. A product page should still render when the price service is down. The failure here comes from a capability operation (chapter 8): `Catalog.cents` declares `fails StoreError`, exactly as a function would.

```una include=steps/04-defaults/src/prices.una title="steps/04-defaults/src/prices.una" verified="check, run, test"
module prices

kind StoreError = | Timeout

--- The catalog service: a price in cents, or `None` for a SKU it does not sell.
capability Catalog
  op cents(sku: Text) -> Option[Int]
    fails StoreError

--- The price a product page shows. A page must render even when the catalog is down,
--- so every failure becomes 0, which the page shows as "ask for a price".
shown_price(sku: Text) -> Int
  uses @catalog: Catalog[cents]
=
  let found = @catalog.cents(sku)
    if error use None
    if none use 0
  found

handler fixed(sku: Text, price: Int) for Catalog
  op cents(s) = if s == sku then Some(price) else None

handler down() for Catalog
  op cents(s) = fail Timeout

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = shown_price("LAMP-01") with @catalog = fixed("LAMP-01", price: 1990)
  let desk = shown_price("DESK-02") with @catalog = fixed("LAMP-01", price: 1990)
  let later = shown_price("LAMP-01") with @catalog = down()
  @console.print("{lamp} {desk} {later}")

example "an unknown SKU shows 0"
  given @catalog = fixed("LAMP-01", price: 1990)
  do shown_price("DESK-02")
  expect result == 0

example "a catalog that is down shows 0, and does not fail"
  given @catalog = down()
  do shown_price("LAMP-01")
  expect result == 0
```

`una run .` prints `1990 0 0`, and `una test .` reports both examples passing.

The two clauses read top to bottom. First, a failure of the call becomes the value `None`. Then `None`, from either source, becomes `0`. `shown_price` has no `fails` line, and it needs none: no failure leaves it. Its header promises callers a price, always.

> [!TIP]
> The handlers `fixed` and `down` are fake catalogs. `with @catalog = …` installs one for a single call, and `given` installs one for an example. This is how every failure path in this chapter gets tested without a real service.

## 6.3 Failures as values: `attempt` and `Result`

The handling clauses decide on the spot. Sometimes you want to *keep* the outcome and decide later, for example to report every line of a batch rather than stop at the first bad one. `attempt` turns one call into a `Result[T, E]`: `Ok(value)` if it returned, `Err(failure)` if it failed. `Result` is a sum kind of the prelude, so `when` takes it apart.

You have already seen `attempt` in `show` above. Its form is always `let name = attempt call(...)`: one call, bound with `let`. When the outcome is `Ok`, the callee's `ensures` hold for the value, exactly as after a direct call.

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Carry on with a default | `if error use` / `if none use` |
| Let the caller decide, same error kind | `if error pass` |
| Report the failure in your own terms | `if error fail V(cause: error)` |
| Keep going and collect outcomes, retry, or count failures | `attempt`, then `when` |
| Accept outside input that no proof can establish | `checked` (section 6.4) |
:::

## 6.4 When no proof can decide: `checked`

Some facts depend on rules the verifier cannot see inside, such as whether a text is a well-formed SKU. `checked(value, condition) else fail V` tests the condition when the program runs, and gives a value of the refined kind when it holds.

> [!WARNING]
> It replaces a proof with a test, so `una.toml` budgets it per module, and every use stays visible in review.

```toml include=steps/05-checked/una.toml title="steps/05-checked/una.toml"
[package]
name = "sku"
version = "0.1.0"
edition = "0.2"

[run]
entry = "sku"
grants = ["console"]

[escape_budget]
checked_per_module = 1
```

```una include=steps/05-checked/src/sku.una title="steps/05-checked/src/sku.una" verified="check, run"
module sku

--- A SKU as the warehouse prints it: seven characters, ending in a dash and two digits, as in `LAMP-01`.
--- The rule is checked when the program runs, so the predicate is opaque to proofs.
predicate opaque well_formed(t: Text) -> Bool = t.len == 7 and t.slice(start: 4, end: 5) == "-" and is_digits(t.slice(start: 5, end: 7))

kind Sku = Text where well_formed(it)

kind SkuError = | NotASku

--- Turns text from the outside into a `Sku`, or fails.
parse_sku(raw: Text) -> Sku
  fails SkuError
=
  checked(raw.trim, well_formed(it)) else fail NotASku

show(raw: Text) -> Text
=
  let outcome = attempt parse_sku(raw)
  when outcome
    is Ok(value) -> "sku {value}"
    is Err -> "not a sku: {raw}"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(show("LAMP-01"))
  @console.print(show("lamp 1"))
```

`una run .` prints `sku LAMP-01` and `not a sku: lamp 1`. From then on, a `Sku` can be passed anywhere one is required, with no second check.

> [!TIP]
> Use `checked` at the edge of the program, once per fact, and prefer a proof (chapter 7) wherever the verifier can see the rule.

## 6.5 Day-to-day: order intake

Now the program from the start of the chapter. Orders arrive as lines of text. Each line must parse, name a product the inventory knows, and ask for no more units than are on hand. The inventory is a service that can time out. A bad line must not stop the batch, and the report must say why each rejected line was rejected.

The design follows from that: one error kind for the order layer, `OrderError`, whose variants carry what an operator needs, and one for the inventory service, `StoreError`, which the order layer translates.

```una include=day-to-day/src/orders.una#L1-L17 title="day-to-day/src/orders.una" caption="the kinds and the service"
module orders

--- One line of an order: a stock-keeping unit (SKU) and how many of it.
pub kind Order
  sku: Text
  quantity: Int

--- Why an order line was rejected. Each variant carries what a person needs to act on it.
pub kind OrderError = Malformed(line: Text) | BadQuantity(line: Text) | UnknownSku(sku: Text) | OutOfStock(sku: Text, wanted: Int, left: Int) | Unavailable

--- How the inventory service can fail.
pub kind StoreError = | Timeout

--- The inventory service: how many units of a SKU are on hand, or `None` for an unknown SKU.
pub capability Inventory
  op on_hand(sku: Text) -> Option[Int]
    fails StoreError
```

`OutOfStock` carries the SKU, the units wanted and the units left, which is everything the report line needs. `Unavailable` carries nothing, because the operator's action is the same whatever the cause: retry later.

**Parsing, a pure step.** `parse_order` only looks at the text. It has no `uses`, so it cannot touch the inventory, and its tests need no fakes.

```una include=day-to-day/src/orders.una#parse_order title="day-to-day/src/orders.una"
--- Reads `"SKU, quantity"`. Pure: it only looks at the text.
pub parse_order(line: Text) -> Order
  fails OrderError
=
  let parts = line.split(on: ",")
  if parts.len != 2
    fail Malformed(line)
  else
    let sku = parts.at(index: 0)
      if none fail Malformed(line)
    let raw = parts.at(index: 1)
      if none fail Malformed(line)
    let quantity = raw.trim.to_int()
      if none fail BadQuantity(line)
    if quantity < 1
      fail BadQuantity(line)
    else
      Order(sku: sku.trim, quantity: quantity)
```

> [!NOTE]
> `at` returns an `Option` even after the length check, because its type does not depend on the check. The `if none fail Malformed(line)` clauses state what the code would do anyway.

**Checking stock, a step with a service.** Two clauses handle the one call: the service's failure becomes `Unavailable`, and an unknown SKU becomes `UnknownSku`.

```una include=day-to-day/src/orders.una#check_stock title="day-to-day/src/orders.una"
--- Confirms that the inventory holds enough units of the order's SKU.
pub check_stock(order: Order) -> Order
  uses @inventory: Inventory[on_hand]
  fails OrderError
=
  let left = @inventory.on_hand(order.sku)
    if error fail Unavailable
    if none fail UnknownSku(sku: order.sku)
  if order.quantity > left
    fail OutOfStock(sku: order.sku, wanted: order.quantity, left: left)
  else
    order
```

**Composing the steps.** Both steps fail with `OrderError`, the same kind as `accept`, so `if error pass` hands their failures on unchanged.

```una include=day-to-day/src/orders.una#accept title="day-to-day/src/orders.una"
--- One line, from text to an order that can be shipped.
pub accept(line: Text) -> Order
  uses @inventory: Inventory[on_hand]
  fails OrderError
=
  let order = parse_order(line)
    if error pass
  check_stock(order)
    if error pass
```

**The batch.** `attempt` keeps each outcome, so `process` itself never fails. Its header has no `fails`, and that is a promise to its callers.

```una include=day-to-day/src/orders.una#process title="day-to-day/src/orders.una"
--- Every line, accepted or rejected: one bad line does not stop the batch.
pub process(lines: List[Text]) -> List[Result[Order, OrderError]]
  uses @inventory: Inventory[on_hand]
=
  let edit results: List[Result[Order, OrderError]] = []
  for line in lines
    let outcome = attempt accept(line)
    results = results.append(item: outcome)
  results
```

**The report.** One `when` per kind. If `OrderError` gains a variant, the checker reports this `when` until it has an arm for it (exercise 1 shows this).

```una include=day-to-day/src/orders.una#reason..describe title="day-to-day/src/orders.una"
--- What a person reads in the batch report.
pub reason(e: OrderError) -> Text
=
  when e
    is Malformed(line) -> "cannot read the line '{line}'"
    is BadQuantity(line) -> "the quantity in '{line}' is not a whole number above 0"
    is UnknownSku(sku) -> "no product has the SKU {sku}"
    is OutOfStock(sku, wanted, left) -> "{wanted} of {sku} wanted, {left} left"
    is Unavailable -> "the inventory did not answer; retry later"

pub describe(outcome: Result[Order, OrderError]) -> Text
=
  when outcome
    is Ok(value) -> "ok      {value.quantity} x {value.sku}"
    is Err(failure) -> "reject  {reason(failure)}"
```

**Running it.** In production, the `Inventory` handler would call the warehouse over HTTP (chapter 9). Here, a handler holds the stock in a map, and `main` installs it with `with`.

```una include=day-to-day/src/orders.una#warehouse..main title="day-to-day/src/orders.una"
--- An inventory held in memory, for the demo and for tests.
handler warehouse(stock: Map[Text, Int]) for Inventory
  op on_hand(sku) = stock.get(key: sku)

--- An inventory that never answers.
handler offline() for Inventory
  op on_hand(sku) = fail Timeout

pub main() -> Unit
  uses @console: Console[print]
=
  let stock = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)
  let lines = ["LAMP-01, 2", "DESK-02, 3", "CHAIR-09, 1", "LAMP-01, two", "LAMP-01"]
  let results = process(lines) with @inventory = warehouse(stock)
  for outcome in results
    @console.print(describe(outcome))
```

`una run .` prints the report shown under "What you'll build". The order lines here are literals.

> [!SECURITY]
> Lines read from a file are labeled `internal`, and printing a report built from them is a question of information flow, which chapter 10 answers with a policy.

The whole file, to read in one piece or to copy:

```una include=day-to-day/src/orders.una title="day-to-day/src/orders.una" caption="the whole program" verified="check, run, test"
module orders

--- One line of an order: a stock-keeping unit (SKU) and how many of it.
pub kind Order
  sku: Text
  quantity: Int

--- Why an order line was rejected. Each variant carries what a person needs to act on it.
pub kind OrderError = Malformed(line: Text) | BadQuantity(line: Text) | UnknownSku(sku: Text) | OutOfStock(sku: Text, wanted: Int, left: Int) | Unavailable

--- How the inventory service can fail.
pub kind StoreError = | Timeout

--- The inventory service: how many units of a SKU are on hand, or `None` for an unknown SKU.
pub capability Inventory
  op on_hand(sku: Text) -> Option[Int]
    fails StoreError

--- Reads `"SKU, quantity"`. Pure: it only looks at the text.
pub parse_order(line: Text) -> Order
  fails OrderError
=
  let parts = line.split(on: ",")
  if parts.len != 2
    fail Malformed(line)
  else
    let sku = parts.at(index: 0)
      if none fail Malformed(line)
    let raw = parts.at(index: 1)
      if none fail Malformed(line)
    let quantity = raw.trim.to_int()
      if none fail BadQuantity(line)
    if quantity < 1
      fail BadQuantity(line)
    else
      Order(sku: sku.trim, quantity: quantity)

--- Confirms that the inventory holds enough units of the order's SKU.
pub check_stock(order: Order) -> Order
  uses @inventory: Inventory[on_hand]
  fails OrderError
=
  let left = @inventory.on_hand(order.sku)
    if error fail Unavailable
    if none fail UnknownSku(sku: order.sku)
  if order.quantity > left
    fail OutOfStock(sku: order.sku, wanted: order.quantity, left: left)
  else
    order

--- One line, from text to an order that can be shipped.
pub accept(line: Text) -> Order
  uses @inventory: Inventory[on_hand]
  fails OrderError
=
  let order = parse_order(line)
    if error pass
  check_stock(order)
    if error pass

--- Every line, accepted or rejected: one bad line does not stop the batch.
pub process(lines: List[Text]) -> List[Result[Order, OrderError]]
  uses @inventory: Inventory[on_hand]
=
  let edit results: List[Result[Order, OrderError]] = []
  for line in lines
    let outcome = attempt accept(line)
    results = results.append(item: outcome)
  results

--- What a person reads in the batch report.
pub reason(e: OrderError) -> Text
=
  when e
    is Malformed(line) -> "cannot read the line '{line}'"
    is BadQuantity(line) -> "the quantity in '{line}' is not a whole number above 0"
    is UnknownSku(sku) -> "no product has the SKU {sku}"
    is OutOfStock(sku, wanted, left) -> "{wanted} of {sku} wanted, {left} left"
    is Unavailable -> "the inventory did not answer; retry later"

pub describe(outcome: Result[Order, OrderError]) -> Text
=
  when outcome
    is Ok(value) -> "ok      {value.quantity} x {value.sku}"
    is Err(failure) -> "reject  {reason(failure)}"

--- An inventory held in memory, for the demo and for tests.
handler warehouse(stock: Map[Text, Int]) for Inventory
  op on_hand(sku) = stock.get(key: sku)

--- An inventory that never answers.
handler offline() for Inventory
  op on_hand(sku) = fail Timeout

pub main() -> Unit
  uses @console: Console[print]
=
  let stock = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)
  let lines = ["LAMP-01, 2", "DESK-02, 3", "CHAIR-09, 1", "LAMP-01, two", "LAMP-01"]
  let results = process(lines) with @inventory = warehouse(stock)
  for outcome in results
    @console.print(describe(outcome))

example "a line in stock is accepted"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do accept("LAMP-01, 2")
  expect result.quantity == 2

example "too many units are out of stock"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do accept("LAMP-01, 9")
  expect fails OutOfStock

example "a malformed line never reaches the inventory"
  given @inventory = offline()
  do accept("LAMP-01")
  expect fails Malformed
  expect not performed @inventory.on_hand

example "an inventory that does not answer is Unavailable"
  given @inventory = offline()
  do accept("LAMP-01, 1")
  expect fails Unavailable
```

## 6.6 Testing it

Every failure path gets an example. The fakes make each one deterministic, and `expect not performed` proves that a malformed line never reaches the inventory: parsing comes first.

```una include=day-to-day/src/orders.una#L104-L123 title="day-to-day/src/orders.una" caption="the examples" verified="test"
example "a line in stock is accepted"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do accept("LAMP-01, 2")
  expect result.quantity == 2

example "too many units are out of stock"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do accept("LAMP-01, 9")
  expect fails OutOfStock

example "a malformed line never reaches the inventory"
  given @inventory = offline()
  do accept("LAMP-01")
  expect fails Malformed
  expect not performed @inventory.on_hand

example "an inventory that does not answer is Unavailable"
  given @inventory = offline()
  do accept("LAMP-01, 1")
  expect fails Unavailable
```

`una test .` prints:

```text include=day-to-day/expected/commands/test.txt#L2-L7
example orders "a line in stock is accepted" ... ok
example orders "too many units are out of stock" ... ok
example orders "a malformed line never reaches the inventory" ... ok
example orders "an inventory that does not answer is Unavailable" ... ok

4 examples: 4 passed, 0 failed
```

## 6.7 Common mistakes

Each mistake below is a one-line change to `day-to-day/src/orders.una`, followed by what `una check .` reports.

:::mistake
**1. Forgetting the clause (U3007).** Remove `if error pass` under `let order = parse_order(line)`:

```text include=mistakes/1/expected/rendered.txt
[U3007] Error: `parse_order` can fail with `OrderError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
    ╭─[ src/orders.una:56:15 ]
    │
 56 │   let order = parse_order(line)
    │               ────────┬────────
    │                       ╰────────── `parse_order` can fail with `OrderError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
    │
    │ Note: run `una explain U3007` for an explanation
────╯
```

*Why:* nothing propagates implicitly.

*Fix:* add the clause that matches your intent (table in 6.2).
:::

:::mistake
**2. Passing a failure of another kind (U3008).** In `check_stock`, write `if error pass` instead of `if error fail Unavailable`:

```text include=mistakes/2/expected/rendered.txt#L1
[U3008] Error: `if error pass` passes a `StoreError` failure, and this code fails with `OrderError`; use `if error fail` with a variant of `OrderError`
```

*Why:* a function has one error kind, and `StoreError` is not `OrderError`.

*Fix:* translate with `if error fail Unavailable`, or `if error fail V(cause: error)` to keep the original.
:::

:::mistake
**3. Failing with a variant of another kind (U3009).** Write `if error fail Timeout` in `check_stock`:

```text include=mistakes/3/expected/rendered.txt#L1
[U3009] Error: `Timeout` is a variant of `StoreError`, and this code fails with `OrderError`
```

*Fix:* name a variant of your own kind.
:::

:::mistake
**4. A public function that fails without saying so (U3009).** Remove `fails OrderError` from `parse_order`:

```text include=mistakes/4/expected/rendered.txt#L1,L8
[U3009] Error: this code declares no error kind, so it cannot fail with `Malformed`; declare `fails` in its header
    │ Help: repair 1: declare `fails OrderError` in the header; edit src/orders.una:20:37..20:37 to "\n  fails OrderError"
```

*Why:* a `pub` header is a reviewed contract.

*Fix:* `una fix .` applies the repair shown.
:::

:::mistake
**5. Nesting a call that can fail (U3013).** Write `check_stock(parse_order(line))`:

```text include=mistakes/5/expected/rendered.txt#L1
[U3013] Error: `parse_order` has effects or can fail, so it must be the whole expression of a statement or `let`; bind its result with `let` first
```

*Why:* "one effect per line". Each failure needs its own handling line, and evaluation order stays visible.

*Fix:* `let order = parse_order(line)` with its clause, then `check_stock(order)` with its own. (`do` lines of examples are exempt.)
:::

:::mistake
**6. The clause on the same line (U0101).** Write `let order = parse_order(line) if error pass`:

```text include=mistakes/6/expected/rendered.txt#L1,L8
[U0101] Error: a handling clause goes on its own line, indented under the expression it handles
    │ Help: repair 1: move the clause to its own line; edit src/orders.una:56:32..56:46 to "\n    if error pass"
```

*Fix:* `una fix .` moves it.
:::

:::mistake
**7. `if none` before `if error` (U0102).**

```text include=mistakes/7/expected/rendered.txt#L1
[U0102] Error: `if error` clause after `if none`; handling clauses go in the order if error, if none
```
:::

:::mistake
**8. Re-raising a stored failure (U0101).** After `attempt`, writing `is Err(failure) -> fail failure`:

```text include=mistakes/8/expected/rendered.txt#L1,L8
[U0101] Error: unexpected `failure`, expected a variant
    │ Help: repair 1: `fail` takes a variant of the error kind, as in `fail Broke`, not a stored value; fail where the error is found, or pass a call's failure on with `if error pass`
```

*Why:* `fail` names a variant at the place the failure is decided.

*Fix:* if you only want to pass the failure on, do not `attempt`; use `if error pass`. Exercise 3 shows a retry that needs no re-raise.
:::

:::mistake
**9. A default of the wrong type (U2001).** `if error use "none"` where the call gives an `Order`:

```text include=mistakes/9/expected/rendered.txt#L1
[U2001] Error: expected `Order`, found `Text`
```
:::

## 6.8 For agents

:::agents
Every diagnostic above is available as JSON with `una --json check .`. For mistake 1:

```json include=mistakes/1/expected/commands/json.txt#L2
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U3007","severity":"error","domain":"authority","message":"`parse_order` can fail with `OrderError`; handle the failure with an `if error` clause, or wrap the call in `attempt`","primary":{"file":"src/orders.una","start":{"line":56,"col":15},"end":{"line":56,"col":32}},"related":[],"repairs":[],"explain":"una explain U3007"}],"fixable":0}
```

`repairs` is empty because the right clause depends on intent, which only the author knows. U0101 (mistake 6) and U3009 (mistake 4) carry exact edits, which `una fix .` applies. The compact rule: *a call that can fail is the whole expression of its statement, followed by `if error …` and then `if none …` on their own lines, or is bound with `let x = attempt …`.*
:::

## 6.9 Exercises

::::exercise
**Exercise 1: a per-line limit.** The store ships at most 10 units of a SKU per line. Add a variant `TooMany(sku: Text, limit: Int)` and reject larger quantities in `parse_order`, before the inventory is asked.

:::hint
*Hint:* add the variant first and run `una check .`: the checker shows the one `when` that needs a new arm.
:::

What `una check .` reports after adding only the variant:

```text include=exercises/1/variant/expected/rendered.txt#L1,L8
[U2007] Error: `when` does not match variant `TooMany` of `OrderError`
    │ Help: repair 1: add an arm for each missing variant, such as `is TooMany`, or an `else` arm
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
In `OrderError`, add `| TooMany(sku: Text, limit: Int)`. In `parse_order`:

```una include=exercises/1/answer/src/orders.una#L33-L38
    if quantity < 1
      fail BadQuantity(line)
    else if quantity > 10
      fail TooMany(sku: sku.trim, limit: 10)
    else
      Order(sku: sku.trim, quantity: quantity)
```

In `reason`, add the arm:

```una include=exercises/1/answer/src/orders.una#L82
    is TooMany(sku, limit) -> "at most {limit} of {sku} per order"
```

The answer's example:

```una include=exercises/1/answer/src/orders.una#L128-L132
example "more than ten units on one line is TooMany"
  given @inventory = offline()
  do accept("LAMP-01, 11")
  expect fails TooMany
  expect not performed @inventory.on_hand
```

`una test .` reports 5 examples, 5 passed.
:::
::::

::::exercise
**Exercise 2: units shipped.** Write `shipped(results)`, the total of the units of the accepted lines.

:::hint
*Hint:* a private function from one `Result` to an `Int`, then `map` and `sum`.
:::

:::answer Answer (*check, run, test*; `exercises/2/answer`):

```una include=exercises/2/answer/src/orders.una#L125-L138
--- The units an outcome ships: its quantity when accepted, 0 when rejected.
units(outcome: Result[Order, OrderError]) -> Int
=
  when outcome
    is Ok(value) -> value.quantity
    is Err -> 0

--- How many units a batch ships in all.
pub shipped(results: List[Result[Order, OrderError]]) -> Int = results.map(each: units).sum()

example "a batch ships only its accepted units"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do shipped(process(["LAMP-01, 2", "LAMP-01, 9", "LAMP-01, 1"]))
  expect result == 3
```
:::
::::

::::exercise
**Exercise 3: retry once.** The inventory sometimes times out once and then answers. Ask it a second time before giving up.

:::hint
*Hint:* `attempt` works on a capability operation too. Retry at the level of the service, where the only failure is `Timeout`, so a plain `if error pass` hands on the second failure.
:::

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Add the function, and in `check_stock` call it instead of `@inventory.on_hand`, with the same two clauses:

```una include=exercises/3/answer/src/orders.una#L125-L140
--- Asks the inventory a second time when the first request fails.
on_hand_with_retry(sku: Text) -> Option[Int]
  uses @inventory: Inventory[on_hand]
  fails StoreError
=
  let first = attempt @inventory.on_hand(sku)
  when first
    is Ok(value) -> value
    is Err ->
      @inventory.on_hand(sku)
        if error pass

example "an inventory that stays down is still Unavailable"
  given @inventory = offline()
  do accept("LAMP-01, 1")
  expect fails Unavailable
```

```una include=exercises/3/answer/src/orders.una#L43-L45
  let left = on_hand_with_retry(order.sku)
    if error fail Unavailable
    if none fail UnknownSku(sku: order.sku)
```

The report from `una run .` does not change. `una test .` reports every example passing.
:::
::::

## 6.10 Recap

:::recap
- A failure is a value of a sum kind you declare. Its variants carry what someone needs to act on it.
- A header declares at most one error kind with `fails`. A `pub` function must declare it, and a private one may let the checker infer it.
- A call that can fail is the whole expression of its statement, and its handling clauses follow on their own lines: `if error` first, then `if none`.
- `use` recovers, `pass` hands on the same kind, `fail V(cause: error)` translates between layers.
- `attempt` keeps an outcome as a `Result`, for batches, counts and retries.
- `checked` is a budgeted run-time test for facts no proof can establish. Use it at the edge.
- Fake the services with handlers, and give every failure path an example.
:::

## 6.11 Reference

:::reference
- Construct pages: `fails`, `fail`, `if error` and `if none`, `attempt`, `checked`, under /docs/reference/language/errors/
- Prelude: `Option`, `Result`, `to_int`, `parse_int`, `ParseError`
- Diagnostics: U0101, U0102, U2001, U2007, U3007, U3008, U3009, U3013
- Specification: errors (spec chapter 6)
:::
