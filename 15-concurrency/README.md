---
learn: "15"
title: Concurrency and parallelism
editions: ["0.2"]
codes: [U0101, U0103, U1001, U2023, U2024, U3007]
time: 50
builds: A stock check that asks three warehouses at once about every line of an order
prerequisites: ["7", "10", "12", "14"]
template: 2
nav: ["together", "together for", "Failures and order", "Day-to-day: every warehouse", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 15 Concurrency and parallelism

A program that asks a service a question waits for the answer. When it asks three warehouses how many lamps they hold, one after another, it waits three times, although none of the questions needs the answer of another. This chapter shows how to ask them all at once. You learn what it means for work to run at the same time, how to write it with `together` and `together for`, and exactly what Una promises about the result: what it can depend on, what happens when a warehouse does not answer, and in what order the effects are recorded. You end with a stock check that asks every warehouse about every line of an order at once.

## What you'll build

:::build
A stock check for a store with three warehouses, north, south and east. For every line of an order, it asks all three warehouses at the same time how many units they hold, and it checks all the lines at once too. It prints what each warehouse holds, whether the order ships, and which warehouse did not answer when one is offline:

```text include="day-to-day/expected/output.txt"
Order 1042
  LAMP-01: 5 wanted, 4 + 2 + 0 = 6 on hand, ships
  DESK-02: 2 wanted, 1 + 0 + 1 = 2 on hand, ships
  the whole order ships
Order 1043
  RUG-07: 6 wanted, 0 + 3 + 5 = 8 on hand, ships
  LAMP-01: 9 wanted, 4 + 2 + 0 = 6 on hand, short by 3
  the order waits for stock
Order 1042, again
  the east warehouse did not answer; check again later
```

You will learn to:

- run a few pieces of work at the same time, each bound to a name, with `together`;
- build a list with one piece of work per element, all at the same time, with `together for`;
- predict the result of concurrent work: the result of running it one piece after another;
- know which failure wins when several pieces fail, and in what order effects are recorded;
- test concurrent code with fakes, and read U2023 and the other diagnostics of this chapter.
:::

## Why it works this way

Running work at the same time is one of the hardest parts of programming in most languages. The trouble comes from two places. When two pieces of work change the same value, such as a counter, the result depends on which one gets there first: one update can be lost, and only on some runs. And when the result depends on timing, a test can pass a hundred times and fail on the next run, on another computer, or under load. Such bugs are hard to reproduce, and so hard to fix.

Una allows concurrency in one shape only, and that shape removes both sources. A piece of work that runs alongside others can read the values around it but cannot change them, so no two pieces ever change the same value. Every piece ends before the block that started it ends, so nothing keeps running in the background. And the result of the block is fixed: it is the result of running the pieces one after another, in the order they are written, stopping at the first failure. Running them at the same time can change how long the program waits, and the order in which the outside world sees their effects, but never what the program computes.

> [!KEY]
> In Una, work that runs at the same time gives the result of running it one piece after another, in the order written: concurrency changes when things happen, not what the program computes.

## 15.1 Running work at the same time: `together`

### What concurrent work is

Think of finding out how many lamps three warehouses hold, by phone. You can call the north warehouse, wait for the answer, then call the south one, then the east one. Or three clerks can each call one warehouse, at the same moment, while you wait until all three come back. The second way can take as long as the slowest call, not as long as all three together.

Work that runs this way is **concurrent**: several pieces of it are in progress at the same time, instead of one after another. Each piece is a **task**: a part of the program that runs on its own and ends with a result. In Una, a `together` block starts its tasks, waits until every one of them has ended, and then gives their results to the code that comes after it. No task outlives the block that started it. Running tasks this way, always inside a block that waits for them all, is called **structured concurrency**.

A word you will meet next to this one is **parallel**: two tasks run in parallel when the computer really runs them at the same instant, on two of its processor cores. Concurrency is the broader idea: the tasks are in progress at the same time, whether the computer runs them at the same instant or switches between them. Una lets you say that work may run concurrently; how much of it runs in parallel is the computer's business ([The interpreter and an executable](#the-interpreter-and-an-executable)).

### Why a program waits on several services at once

Most of the time a program spends waiting is not spent computing. It is spent waiting for answers: from a warehouse's stock service, a payment service, a database. In [chapter 12](/learn/capabilities/#s12-3) such a service is a capability, and each call of one of its operations waits until the service answers. Over a network, an answer can take a tenth of a second or more.

A program that asks two warehouses, one after the other, waits twice. Each step of a body runs to its end before the next one starts, as [chapter 1](/learn/hello/#s1-3) says, so the second question is not even sent until the first answer has come back. The two questions do not depend on each other, so nothing is gained by that order. With `together`, the program can send both and wait once, for the slower of the two.

Only the waiting can change. The result stays what it was, and this chapter shows that the result cannot change: the program computes the same totals, the same failures and the same report, whether the questions are asked one after another or at the same time.

### How to write `together`

Each example of this chapter is a package of its own, a step, as [chapter 2](/learn/numbers/#each-step-is-a-package) explains. The first step asks two warehouses for the units of one SKU, one after the other. `Warehouse` is a capability with one operation, `on_hand`, which can fail with `StockError` when a warehouse does not answer, and `shelves` is a handler that answers from a map, as the handler `warehouse` of [chapter 12](/learn/capabilities/#s12-3) does; here `Warehouse` names the capability, and the handler is `shelves`:

```una include="steps/01-one-after-another/src/stock.una" title="steps/01-one-after-another/src/stock.una" verified="check, run"
module stock

--- Why a warehouse gave no count.
kind StockError = | Offline(site: Text)

--- A warehouse's stock service: the units of a SKU on its shelves.
capability Warehouse
  op on_hand(sku: Text) -> Int
    fails StockError

--- A warehouse whose stock is held in a map: none of a SKU it does not stock.
handler shelves(stock: Map[Text, Int]) for Warehouse
  op on_hand(sku) = stock.get(key: sku).or_else(default: 0)

--- The units of `sku` in both warehouses, asked one after the other.
total(sku: Text) -> Int
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  fails StockError
=
  let in_north = @north.on_hand(sku)
    if error pass
  let in_south = @south.on_hand(sku)
    if error pass
  in_north + in_south

pub main() -> Unit
  uses @console: Console[print]
=
  let north = empty_map().with(key: "LAMP-01", value: 4)
  let south = empty_map().with(key: "LAMP-01", value: 2)
  let units = total("LAMP-01") with @north = shelves(north), @south = shelves(south)
    if error use 0
  @console.print("LAMP-01: {units} units")
```

`una run .` prints:

```text include="steps/01-one-after-another/expected/output.txt"
LAMP-01: 6 units
```

The two `let` lines of `total` run in order: first the north warehouse is asked, and only when it has answered, the south one. To ask both at the same time, put the two `let` lines under `together`:

:::steps
```diff include="steps/01-one-after-another..steps/02-together:src/stock.una" title="src/stock.una"
--- a/src/stock.una
+++ b/src/stock.una
@@ -12,16 +12,17 @@
 handler shelves(stock: Map[Text, Int]) for Warehouse
   op on_hand(sku) = stock.get(key: sku).or_else(default: 0)
 
---- The units of `sku` in both warehouses, asked one after the other.
+--- The units of `sku` in both warehouses, both asked at the same time.
 total(sku: Text) -> Int
   uses @north: Warehouse[on_hand]
   uses @south: Warehouse[on_hand]
   fails StockError
 =
-  let in_north = @north.on_hand(sku)
-    if error pass
-  let in_south = @south.on_hand(sku)
-    if error pass
+  together
+    let in_north = @north.on_hand(sku)
+      if error pass
+    let in_south = @south.on_hand(sku)
+      if error pass
   in_north + in_south
 
 pub main() -> Unit
```

1. **`together`.** The keyword, alone on its line, opens the block. The block is a statement: a step of the body, like a `let` line.
2. **`let in_north = @north.on_hand(sku)`.** Each `let` line indented under `together` is a **branch**, and its expression is a task. This task asks the north warehouse.
3. **`if error pass`.** A branch keeps its handling clause, under it, as the same `let` would outside the block ([chapter 7](/learn/failure/#s7-3)).
4. **`let in_south = @south.on_hand(sku)`.** The second branch, a second task. The two tasks start together.
5. **`in_north + in_south`.** The first line after the block. It runs only when both tasks have ended, and both names are bound by then.
:::

`una run .` prints the same line as before:

```text include="steps/02-together/expected/output.txt"
LAMP-01: 6 units
```

That is the point of the change: the result is the same, and only the waiting can differ. Under `una run`, the tasks still run one after another, so this step takes no less time; the waiting shrinks in an executable that asks real services ([The interpreter and an executable](#the-interpreter-and-an-executable)).

### The forms of `together`

The module `forms` has one function for each way of writing a branch, and a `main` that calls them:

```una include="steps/03-together-forms/src/forms.una" title="steps/03-together-forms/src/forms.una" verified="check, run"
module forms

--- Why a warehouse gave no count.
kind StockError = | Offline(site: Text)

--- A warehouse's stock service: the units of a SKU on its shelves.
capability Warehouse
  op on_hand(sku: Text) -> Int
    fails StockError

--- A warehouse whose stock is held in a map: none of a SKU it does not stock.
handler shelves(stock: Map[Text, Int]) for Warehouse
  op on_hand(sku) = stock.get(key: sku).or_else(default: 0)

--- A warehouse that does not answer.
handler offline(site: Text) for Warehouse
  op on_hand(sku) = fail Offline(site)

--- Two branches: the units of `sku` in two warehouses.
total(sku: Text) -> Int
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  fails StockError
=
  together
    let in_north = @north.on_hand(sku)
      if error pass
    let in_south = @south.on_hand(sku)
      if error pass
  in_north + in_south

--- Three branches: the units of `sku` in three warehouses, as a text.
three_sites(sku: Text) -> Text
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  uses @east: Warehouse[on_hand]
  fails StockError
=
  together
    let in_north = @north.on_hand(sku)
      if error pass
    let in_south = @south.on_hand(sku)
      if error pass
    let in_east = @east.on_hand(sku)
      if error pass
  "{in_north} + {in_south} + {in_east} = {in_north + in_south + in_east}"

--- The units of `sku` in the one warehouse a caller hands over.
units_of(sku: Text) -> Int
  uses @warehouse: Warehouse[on_hand]
  fails StockError
=
  @warehouse.on_hand(sku)
    if error pass

--- A branch that installs its own handler: each store's stock comes from its own map.
two_stores(sku: Text, harbor: Map[Text, Int], market: Map[Text, Int]) -> Int
  fails StockError
=
  together
    let at_harbor = units_of(sku) with @warehouse = shelves(harbor)
      if error pass
    let at_market = units_of(sku) with @warehouse = shelves(market)
      if error pass
  at_harbor + at_market

--- Branches that handle their own failure: a warehouse that does not answer counts as none.
estimate(sku: Text) -> Int
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
=
  together
    let in_north = @north.on_hand(sku)
      if error use 0
    let in_south = @south.on_hand(sku)
      if error use 0
  in_north + in_south

pub main() -> Unit
  uses @console: Console[print]
=
  let north = empty_map().with(key: "LAMP-01", value: 4)
  let south = empty_map().with(key: "LAMP-01", value: 2)
  let east = empty_map().with(key: "DESK-02", value: 3)
  let units = total("LAMP-01") with @north = shelves(north), @south = shelves(south)
    if error use 0
  @console.print("two branches: {units}")
  let line = three_sites("LAMP-01") with @north = shelves(north), @south = shelves(south), @east = shelves(east)
    if error use "no count"
  @console.print("three branches: {line}")
  let stores = two_stores("LAMP-01", harbor: north, market: south)
    if error use 0
  @console.print("a handler per branch: {stores}")
  let rough = estimate("LAMP-01") with @north = shelves(north), @south = shelves(south)
  @console.print("a clause per branch: {rough}")
```

`una run .` prints:

```text include="steps/03-together-forms/expected/output.txt"
two branches: 6
three branches: 4 + 2 + 0 = 6
a handler per branch: 6
a clause per branch: 6
```

#### Two branches

`total` is the smallest `together`: two branches, each one call of an operation. A `together` block always has at least two branches.

#### Three branches or more

`three_sites` asks three warehouses, `@north`, `@south` and `@east`, at once. A block may have as many branches as you need, each on its own `let` line, and they all may run at the same time. After the block, the three names are bound, and the last line puts them in a text.

#### A branch that installs a handler: `with`

`two_stores` has no warehouse bindings of its own. Each branch calls `units_of` with a handler installed for that one call, `with @warehouse = shelves(harbor)` and `with @warehouse = shelves(market)`, as [chapter 12](/learn/capabilities/#s12-4) shows. Each task gets its own installation, so the two tasks ask two different warehouses through the same function.

#### A branch that handles its own failure

`estimate` handles each failure in its branch, with `if error use 0`: a warehouse that does not answer counts as none. A branch takes any clause of [chapter 7](/learn/failure/#s7-3), and the clause applies to that branch alone. Since every failure is handled, `estimate` itself cannot fail, and its header has no `fails`.

#### What a branch may hold

The expression of a branch is any expression a `let` takes: a call of an operation, a call of your own function, an arithmetic expression, a text. Usually it is a call that waits for something, since that is what is worth running at the same time. A branch may also call a function that has its own `together` inside: tasks may hold tasks.

### How `together` behaves

#### A branch sees what came before the block, not its siblings

The expression of a branch sees every name bound before the block: the parameters, and the `let` lines above `together`. It does not see the names of the other branches, its **siblings**, since they are computed at the same time and do not exist yet. Here a third branch tries to add the other two:

```diff include="steps/03-together-forms..steps/04-sibling:src/forms.una" title="src/forms.una"
--- a/src/forms.una
+++ b/src/forms.una
@@ -27,7 +27,8 @@
       if error pass
     let in_south = @south.on_hand(sku)
       if error pass
-  in_north + in_south
+    let both = in_north + in_south
+  both
 
 --- Three branches: the units of `sku` in three warehouses, as a text.
 three_sites(sku: Text) -> Text
```

```text include="steps/04-sibling/expected/rendered.txt"
[U1001] Error: cannot find name `in_north` in this module, its imports or the prelude
    ╭─[ src/forms.una:30:16 ]
    │
 30 │     let both = in_north + in_south
    │                ────┬───
    │                    ╰───── cannot find name `in_north` in this module, its imports or the prelude
    │
    │ Note: run `una explain U1001` for an explanation
────╯
[U1001] Error: cannot find name `in_south` in this module, its imports or the prelude
    ╭─[ src/forms.una:30:27 ]
    │
 30 │     let both = in_north + in_south
    │                           ────┬───
    │                               ╰───── cannot find name `in_south` in this module, its imports or the prelude
    │
    │ Note: run `una explain U1001` for an explanation
────╯
```

The message is the one for a name that does not exist at all, U1001, once for each sibling the branch reads. The marks point at the two names. Inside the block, `in_north` and `in_south` do not exist yet; after the block, they do. The repair is the one `total` already uses: compute the sum on the first line after the block.

#### At least two branches, and only `let` lines

A block of one branch would run one task while the function waits for it, which is what a plain `let` already does. So Una refuses it:

```diff include="steps/03-together-forms..steps/05-one-branch:src/forms.una" title="src/forms.una"
--- a/src/forms.una
+++ b/src/forms.una
@@ -25,9 +25,7 @@
   together
     let in_north = @north.on_hand(sku)
       if error pass
-    let in_south = @south.on_hand(sku)
-      if error pass
-  in_north + in_south
+  in_north
 
 --- Three branches: the units of `sku` in three warehouses, as a text.
 three_sites(sku: Text) -> Text
```

```text include="steps/05-one-branch/expected/rendered.txt"
[U2024] Error: `together` needs at least two `let` branches; with one, write a plain `let`
    ╭─[ src/forms.una:25:3 ]
    │
 25 │   together
    │   ────┬───
    │       ╰───── `together` needs at least two `let` branches; with one, write a plain `let`
    │
    │ Note: run `una explain U2024` for an explanation
────╯
```

The message gives the repair: with one task, write a plain `let`. The same code, U2024, reports a block that holds a line other than a `let`, such as a call standing on its own: every line under `together` is a branch, and a branch is a `let` line. A step that needs several lines goes into a function, and the branch calls it.

#### After the block, the names come in order

When every task has ended, the names of the branches are bound in the order of the branches, as consecutive `let` lines would bind them. Each name has the type its `let` would give it outside the block, and the verifier knows about it what it would know after that `let`.

#### The block ends when every task has ended

The line after the block runs only when all its tasks have ended. A task cannot keep running after its block, and it cannot be handed to other code to finish later: a branch gives a value, not a task.

#### `together` is a step, not a value

`together` with branches is a statement: it binds names and gives no value of its own. So it cannot stand after `let`, and it cannot be the last line of a body, the line that gives the function's result. Both are U0101, and [Common mistakes](#s15-6) shows each one. To build a list of results, use `together for` ([section 15.2](#s15-2)).

#### Edition `0.2` and later

`together` is a keyword from edition `0.2` on, the edition of every package in this book. In a package of edition `0.1`, it is a reserved word ([chapter 19](/learn/editions/)).

### `together` or plain `let` lines

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| Two or more calls that wait on services and do not need each other's answers | `together`, one branch per call |
| A call that needs the result of an earlier one | plain `let` lines, in order |
| One call | a plain `let` |
| A failure of one service to fail the whole step | `if error pass` on that branch |
| A failure of one service to count as a default | `if error use` on that branch |
| One result for each element of a list | `together for` ([section 15.2](#s15-2)) |
:::

### Check yourself: a warehouse that does not answer

This step asks two warehouses twice, once with `estimate` and once with `total`. The north warehouse holds 4 lamps, and the south one does not answer: `offline` is a handler whose operation always fails with `Offline`.

```una include="steps/06-estimate/src/estimate.una" title="steps/06-estimate/src/estimate.una"
module estimate

--- Why a warehouse gave no count.
kind StockError = | Offline(site: Text)

--- A warehouse's stock service: the units of a SKU on its shelves.
capability Warehouse
  op on_hand(sku: Text) -> Int
    fails StockError

--- A warehouse whose stock is held in a map: none of a SKU it does not stock.
handler shelves(stock: Map[Text, Int]) for Warehouse
  op on_hand(sku) = stock.get(key: sku).or_else(default: 0)

--- A warehouse that does not answer.
handler offline(site: Text) for Warehouse
  op on_hand(sku) = fail Offline(site)

--- The units of `sku` in two warehouses: a warehouse that does not answer counts as none.
estimate(sku: Text) -> Int
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
=
  together
    let in_north = @north.on_hand(sku)
      if error use 0
    let in_south = @south.on_hand(sku)
      if error use 0
  in_north + in_south

--- The units of `sku` in two warehouses: a warehouse that does not answer fails the count.
total(sku: Text) -> Int
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  fails StockError
=
  together
    let in_north = @north.on_hand(sku)
      if error pass
    let in_south = @south.on_hand(sku)
      if error pass
  in_north + in_south

pub main() -> Unit
  uses @console: Console[print]
=
  let north = empty_map().with(key: "LAMP-01", value: 4)
  let rough = estimate("LAMP-01") with @north = shelves(north), @south = offline("south")
  @console.print("estimate: {rough}")
  let exact = total("LAMP-01") with @north = shelves(north), @south = offline("south")
    if error use -1
  @console.print("total: {exact}")
```

What does `una run .` print?

:::answer Show the answer
```text include="steps/06-estimate/expected/output.txt"
estimate: 4
total: -1
```

In `estimate`, each branch handles its own failure, so the south branch gives 0 and the block ends normally: 4 + 0. In `total`, the south branch passes its failure on, so the block fails, `total` fails with it, and the clause of `main`, `if error use -1`, gives -1. Running the branches at the same time changes neither answer.
:::

## 15.2 Building a list at the same time: `together for`

### What `together for` is

`together` suits a few pieces of work you can name one by one. Often the pieces come from a list: one question per line of an order, one label per SKU. `together for` runs one task for each element of a list, or for each number of a range, all of them concurrent, and gives the list of their results.

It reads like the `for` loop of [chapter 9](/learn/loops/#s9-1), with one difference that matters. A `for` loop takes its turns one after another, and a turn may change a name declared before the loop with `let edit`. The tasks of `together for` run concurrently, and each one gives back a value. `together for` builds a list: one element per task, in the order of the list it walks.

### Why one task per element

A store checks an order of ten lines against its warehouses. Asked one line after another, the check takes ten times as long as one line. The lines do not depend on each other, so they can all be checked at once, and in an executable the check can take about as long as the slowest line. The number of lines is known only when the program runs, so a `together` block, whose branches are written one by one, cannot do it. `together for` makes as many tasks as the list has elements.

### How to write `together for`

The module `labels` has one function for each form:

```una include="steps/07-together-for-forms/src/labels.una" title="steps/07-together-for-forms/src/labels.una" verified="check, run"
module labels

--- A shelf label for each SKU: a `together for` over a list, as the value of a `let`.
labels(skus: List[Text]) -> List[Text]
  ensures result.len == skus.len
=
  let made = together for sku in skus
    "label {sku}"
  made

--- The last day of each of the first `weeks` weeks of a sale: a `together for` over a range.
last_days(weeks: Int) -> List[Int]
  requires weeks >= 0
  ensures result.len == weeks
=
  together for week in 1..weeks
    week * 7

--- A body of several lines: its last line is the task's value.
sizes(skus: List[Text]) -> List[Text]
=
  together for sku in skus
    let size = sku.len
    let word = if size == 1 then "character" else "characters"
    "{sku}: {size} {word}"

--- A `together for` inside a `together for`: the label of each SKU of each order.
order_labels(orders: List[List[Text]]) -> List[List[Text]]
=
  together for order in orders
    labels(order)

pub main() -> Unit
  uses @console: Console[print]
=
  let skus = ["LAMP-01", "DESK-02", "RUG-07"]
  @console.print("{labels(skus)}")
  @console.print("{labels([])}")
  @console.print("{last_days(3)}")
  @console.print("{last_days(0)}")
  @console.print("{sizes(skus)}")
  let lamps = ["LAMP-01"]
  let desks = ["DESK-02", "DESK-05"]
  @console.print("{order_labels([lamps, desks])}")
  let edit shelf: List[Text] = []
  shelf = together for sku in desks
    "shelf {sku}"
  @console.print("{shelf}")
```

`una run .` prints:

```text include="steps/07-together-for-forms/expected/output.txt"
["label LAMP-01", "label DESK-02", "label RUG-07"]
[]
[7, 14, 21]
[]
["LAMP-01: 7 characters", "DESK-02: 7 characters", "RUG-07: 6 characters"]
[["label LAMP-01"], ["label DESK-02", "label DESK-05"]]
["shelf DESK-02", "shelf DESK-05"]
```

#### Over a list

`together for sku in skus`, then an indented body. `sku` is the **element name**, as the loop variable of a `for` loop: in each task, it stands for one element of `skus`. The body is the work of one task, and its last line is the task's value: here the text `"label {sku}"`. The result is a `List[Text]`, one label per SKU. `labels([])` walks an empty list, starts no task, and gives an empty list.

#### Over a range

`together for week in 1..weeks` runs one task per whole number of the range, as a `for` loop over a range takes one turn per number ([chapter 9](/learn/loops/#s9-1)). Both kinds of range work, `..` with its end and `..<` without. `last_days(0)` walks the empty range `1..0`, starts no task, and gives an empty list.

#### A body of several lines

The body of `sizes` has three lines. The first two are `let` lines of the task's own, and the last line is the task's value. A name made in the body is the task's own: each task has its own `size` and its own `word`.

#### Where it stands: after `let`, as the last line, or in an assignment

`together for` gives a value, so it stands where a value goes:

- after `let`, as in `labels`: `let made = together for sku in skus`;
- as the last line of a body, as in `last_days` and `sizes`, where it is the function's result;
- after `=` in an assignment to a `let edit` name ([chapter 9](/learn/loops/#s9-2)), as `shelf = together for sku in desks` in `main`.

#### One inside another

`order_labels` walks a list of orders, each a list of SKUs, and its body calls `labels`, which has a `together for` of its own. The result is a list of lists, one per order, each in the order of its SKUs. A `together for` may also stand directly in the body of another.

### Counting the stock of every SKU

The forms together, with warehouses. `stock_lines` counts several SKUs at once, and each of its tasks calls `total`, which asks two warehouses at once:

:::steps
```una include="steps/08-stock-of-each/src/stock.una" title="steps/08-stock-of-each/src/stock.una" verified="check, run"
module stock

--- Why a warehouse gave no count.
kind StockError = | Offline(site: Text)

--- A warehouse's stock service: the units of a SKU on its shelves.
capability Warehouse
  op on_hand(sku: Text) -> Int
    fails StockError

--- A warehouse whose stock is held in a map: none of a SKU it does not stock.
handler shelves(stock: Map[Text, Int]) for Warehouse
  op on_hand(sku) = stock.get(key: sku).or_else(default: 0)

--- The units of `sku` in both warehouses, both asked at the same time.
total(sku: Text) -> Int
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  fails StockError
=
  together
    let in_north = @north.on_hand(sku)
      if error pass
    let in_south = @south.on_hand(sku)
      if error pass
  in_north + in_south

--- One line per SKU, every SKU counted at the same time.
stock_lines(skus: List[Text]) -> List[Text]
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  fails StockError
=
  together for sku in skus
    let units = total(sku)
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
```

1. **`together for sku in skus`.** One task per SKU, as the last line of the body, so the list it builds is the function's result.
2. **`let units = total(sku)`, then `if error pass`.** A line of the body that can fail takes a clause, as in any block. A failure of `total` makes its task fail, and the task's failure makes `stock_lines` fail.
3. **`"{sku}: {units} units"`.** The last line, the task's value.
4. **Tasks inside tasks.** Each task calls `total`, whose `together` starts two tasks of its own. Three SKUs, two warehouses each: six questions, which may all be in progress at once.
5. **The bindings in tasks.** Each task uses `@north` and `@south`, the bindings of the `uses` lines of `stock_lines`. `main` installs both handlers for the one call, with `with`, and every task of that call sees them.
:::

`una run .` prints:

```text include="steps/08-stock-of-each/expected/output.txt"
LAMP-01: 6 units
DESK-02: 3 units
CHAIR-09: 0 units
```

`CHAIR-09` is in neither map, so both warehouses answer 0.

### How `together for` behaves

#### The results come in the order of the list

The list `together for` gives has its results in the order of the elements, whatever order the tasks finish in. If the task for `CHAIR-09` finishes first, its line is still the third. You never sort the results back into place.

#### One element, one task

The result has exactly as many elements as the list it walks, or as the range has numbers: one per task. An empty list or an empty range starts no task, and gives an empty list.

#### What the verifier knows: the length

The verifier knows that length too. `labels` promises `ensures result.len == skus.len`, and `last_days` promises `ensures result.len == weeks`, from `requires weeks >= 0`. `una check .` proves both from the `together for` alone ([chapter 5](/learn/contracts/#s5-2)). Each element has the type of the body's last line, with whatever that type promises.

#### It gives a value, so it ends a block or names one

A `together for` that is neither named by a `let`, nor assigned, nor the last line of its block would build a list and lose it. Here `stock_lines` gets a line after it:

```diff include="steps/08-stock-of-each..steps/09-for-statement:src/stock.una" title="src/stock.una"
--- a/src/stock.una
+++ b/src/stock.una
@@ -35,6 +35,7 @@
     let units = total(sku)
       if error pass
     "{sku}: {units} units"
+  ["no SKUs asked"]
 
 pub main() -> Unit
   uses @console: Console[print]
```

```text include="steps/09-for-statement/expected/rendered.txt"
[U0101] Error: a `together for` must be the last line of its block or the value of a `let` or of an assignment
    ╭─[ src/stock.una:34:3 ]
    │
 34 │   together for sku in skus
    │   ────┬───
    │       ╰───── a `together for` must be the last line of its block or the value of a `let` or of an assignment
    │
    │ Note: run `una explain U0101` for an explanation
────╯
```

The message says where a `together for` may stand: as the last line of its block, as the value of a `let`, or as the value of an assignment to a `let edit` name, as in `main` above. Name the list, or make it the last line.

#### It builds a list, not a total

A task cannot change a name declared outside it, so a `together for` cannot add up a running total as a `for` loop does. Build the list, then add it up after the block, with `sum` or `fold` ([chapter 10](/learn/collections/#s10-3)). [Section 15.3](#s15-3) says why.

### A loop, `map` or `together for`

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| One result per element, each from a call that waits on a service | `together for` |
| One result per element, from a short pure computation | `map` ([chapter 10](/learn/collections/#s10-3)), or `together for` |
| A running total, or a turn that reads what the turn before it left | a `for` loop with `let edit` ([chapter 9](/learn/loops/#s9-2)) |
| A few different pieces of work, each with its own name | `together` with branches ([section 15.1](#s15-1)) |
| A step for each element that only prints | a `for` loop: printing in order is what you want |
:::

In an executable, each task runs on a thread of its own ([The interpreter and an executable](#the-interpreter-and-an-executable)), and starting a thread, and copying in what the task reads, is work too. So `together for` pays off when each task waits for something, such as a service. For a short computation that waits for nothing, such as building a label, `map` reads more simply.

### Check yourself: the order of the results

`plan` decides, for each SKU, whether to order more of it:

```una include="steps/10-restock/src/restock.una" title="steps/10-restock/src/restock.una"
module restock

--- What to do about each SKU: order more when fewer than 3 units are left.
plan(skus: List[Text], stock: Map[Text, Int]) -> List[Text]
=
  together for sku in skus
    let units = stock.get(key: sku).or_else(default: 0)
    if units < 3 then "order {sku}" else "{sku} ok"

pub main() -> Unit
  uses @console: Console[print]
=
  let stock = empty_map().with(key: "DESK-02", value: 1).with(key: "LAMP-01", value: 8)
  let skus = ["RUG-07", "LAMP-01", "DESK-02"]
  @console.print("{plan(skus, stock: stock)}")
```

Suppose the task for `LAMP-01` finishes first. What does `una run .` print?

:::answer Show the answer
```text include="steps/10-restock/expected/output.txt"
["order RUG-07", "LAMP-01 ok", "order DESK-02"]
```

The results come in the order of `skus`, `RUG-07`, `LAMP-01`, `DESK-02`, whatever order the tasks finish in. `RUG-07` is not in the map, so `or_else` gives 0, which is fewer than 3. `DESK-02` has 1 unit left, and `LAMP-01` has 8.
:::

## 15.3 What the result can depend on: failures and order

### What it means for a result to depend on something

A result **depends** on something when changing that thing can change the result. The total of an order depends on its lines: change a quantity, and the total changes. A well-made program's result depends on its inputs, and on the answers its services give, and on nothing else.

With concurrent tasks, there is one more candidate: timing. Which task finishes first can change from run to run, with the load of the computer or the speed of the network. In Una, the result of a block never depends on it. This section states the guarantee, the three rules that give it, and what timing can still change.

### Why shared changes go wrong: races

Picture two clerks who keep one tally on a whiteboard. Each reads the number, adds the boxes they counted, and writes the new number. If both read 10 at the same moment, one adds 3 and writes 13, the other adds 5 and writes 15, and the 3 boxes are lost. Had one clerk waited for the other, the board would read 18. This is a **race**: two tasks change the same value, and the result depends on which one gets there first. It happens only on some runs, which is what makes a race so hard to find.

In many languages, tasks share values that both may change, and a programmer must add locks or other care to keep them from racing. In Una, tasks never share a value that changes, so a race cannot be written.

### The guarantee: the result of a run one after another

The result of a `together` block, and of a `together for`, is the result of running its tasks one after another, in the order they are written, and stopping at the first one that fails. You can always predict the result by reading the tasks in order, as if `together` were not there. Three rules give that guarantee.

### Rule 1: tasks share nothing that changes

A task **captures** the values of the names around it that it reads: it gets their values as they are when the block starts, as a lambda does ([chapter 10](/learn/collections/#s10-2)). It cannot change a name declared outside it. Here `stock_lines` counts the SKUs it was asked about in an outer `let edit` name:

```diff include="steps/08-stock-of-each..steps/11-shared-counter:src/stock.una" title="src/stock.una"
--- a/src/stock.una
+++ b/src/stock.una
@@ -31,10 +31,13 @@
   uses @south: Warehouse[on_hand]
   fails StockError
 =
-  together for sku in skus
+  let edit asked = 0
+  let lines = together for sku in skus
+    asked = asked + 1
     let units = total(sku)
       if error pass
     "{sku}: {units} units"
+  lines.append(item: "{asked} SKUs asked")
 
 pub main() -> Unit
   uses @console: Console[print]
```

```text include="steps/11-shared-counter/expected/rendered.txt"
[U2023] Error: `asked` is declared outside this `together` task, which captures its value and cannot change it, so it cannot be assigned here; return the new value from the task instead
    ╭─[ src/stock.una:36:5 ]
    │
 36 │     asked = asked + 1
    │     ──┬──
    │       ╰──── `asked` is declared outside this `together` task, which captures its value and cannot change it, so it cannot be assigned here; return the new value from the task instead
    │
    │ Note: run `una explain U2023` for an explanation
────╯
```

The marks point at `asked`, the name being assigned. The three tasks run at the same time, so `asked = asked + 1` would be the whiteboard of the two clerks, and the count could come out 1, 2 or 3. The message gives the repair: return the new value from the task. Here, each task already returns its line, and the number of SKUs asked is the length of the list:

```diff include="steps/08-stock-of-each..steps/12-count-returned:src/stock.una" title="src/stock.una"
--- a/src/stock.una
+++ b/src/stock.una
@@ -31,10 +31,11 @@
   uses @south: Warehouse[on_hand]
   fails StockError
 =
-  together for sku in skus
+  let lines = together for sku in skus
     let units = total(sku)
       if error pass
     "{sku}: {units} units"
+  lines.append(item: "{lines.len} SKUs asked")
 
 pub main() -> Unit
   uses @console: Console[print]
```

```text include="steps/12-count-returned/expected/output.txt"
LAMP-01: 6 units
DESK-02: 3 units
CHAIR-09: 0 units
3 SKUs asked
```

Passing an outer name to a function that changes it for its caller (`edit`, [section 16.2](/learn/memory/#s16-2)) or takes it over (`take`, [section 16.3](/learn/memory/#s16-3)) is U2023 too. A task's own names, made in its body, are its own: it may declare them `let edit` and change them, as any block may.

### Rule 2: the first failure in order wins

When one task fails, the block fails too, and the failure it gives is the failure that a run one after another would give: the failure of the first task, in the order written, that fails.

- **The tasks after it are canceled.** A task written after a failing one is **canceled** if it is still running: it is stopped, and its result is dropped, since the block will fail anyway. One that has already ended keeps what it did, and its result is dropped too. A task that has not started yet never starts.
- **The tasks before it run on.** A task written before the failing one keeps running to its end, since a run one after another would have run it first. It may fail in turn, and then its failure is the one that wins.
- **Canceling waits for a safe point.** A canceled task stops at its next call, operation or loop turn. An operation already in progress, such as a question a warehouse is answering, completes, and what it already did stays done.
- **The block still waits.** It fails only after every task has ended, failed or stopped.

This step asks two warehouses with `total`, first with the south one offline, then with both offline:

```una include="steps/13-failures/src/failures.una" title="steps/13-failures/src/failures.una" verified="check, run, test"
module failures

--- Why a warehouse gave no count.
kind StockError = | Offline(site: Text)

--- A warehouse's stock service: the units of a SKU on its shelves.
capability Warehouse
  op on_hand(sku: Text) -> Int
    fails StockError

--- A warehouse whose stock is held in a map: none of a SKU it does not stock.
handler shelves(stock: Map[Text, Int]) for Warehouse
  op on_hand(sku) = stock.get(key: sku).or_else(default: 0)

--- A warehouse that does not answer.
handler offline(site: Text) for Warehouse
  op on_hand(sku) = fail Offline(site)

--- The units of `sku` in both warehouses, both asked at the same time.
total(sku: Text) -> Int
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  fails StockError
=
  together
    let in_north = @north.on_hand(sku)
      if error pass
    let in_south = @south.on_hand(sku)
      if error pass
  in_north + in_south

pub main() -> Unit
  uses @console: Console[print]
=
  let north = empty_map().with(key: "LAMP-01", value: 4)
  let south_down = attempt total("LAMP-01") with @north = shelves(north), @south = offline("south")
  @console.print("south offline: {south_down}")
  let both_down = attempt total("LAMP-01") with @north = offline("north"), @south = offline("south")
  @console.print("both offline: {both_down}")

example "the north warehouse is asked even though the south one fails"
  given @north = shelves(empty_map().with(key: "LAMP-01", value: 4))
  given @south = offline("south")
  do total("LAMP-01")
  expect fails Offline
  expect performed @north.on_hand
```

`una run .` prints:

```text include="steps/13-failures/expected/output.txt"
south offline: Err(Offline("south"))
both offline: Err(Offline("north"))
```

With both warehouses offline, both tasks fail, perhaps the south one first. The block still fails with `Offline("north")`, the failure of the first branch, as a run one after another would. The example checks the second point of the list: when the south warehouse fails, the north one, the branch before it, was still asked. `una test .` prints:

```text include="steps/13-failures/expected/commands/test.txt#L2-L4"
example failures "the north warehouse is asked even though the south one fails" ... ok

1 example: 1 passed, 0 failed
```

Under `una test`, which runs the tasks one after another, a task after a failing one never starts, so an example could state that its warehouse was not asked, and pass every time. But that is the interpreter's schedule, not a promise of the language: in an executable, that task may have asked its warehouse before it was canceled. So `expect performed` and `expect not performed` belong on the tasks before a failing one, and on blocks that do not fail ([chapter 14](/learn/testing/#s14-3)).

### Rule 3: effects are recorded in task order

What a program does to the world outside it, such as asking a service or printing a line, is an effect ([chapter 12](/learn/capabilities/#s12-1)). Una keeps a record of the operations a run performs, the trace that `expect performed` reads ([section 14.3](/learn/testing/#s14-3)). In the trace, the operations of a block's tasks are listed task by task, in the order of the tasks, each task's operations in its own order, whatever order they really happened in. The trace of a canceled task ends where it stopped, with a mark that it was canceled.

What the record cannot fix is the moment each effect reaches the outside world. Here each task prints a line:

```una include="steps/14-printing-tasks/src/announce.una" title="steps/14-printing-tasks/src/announce.una" verified="check, run"
module announce

--- Prints a line for each SKU from its own task, and gives back the length of each SKU.
announce(skus: List[Text]) -> List[Int]
  uses @console: Console[print]
=
  together for sku in skus
    @console.print("checking {sku}")
    sku.len

pub main() -> Unit
  uses @console: Console[print]
=
  let lengths = announce(["LAMP-01", "RUG-07", "DESK-02"])
  @console.print("lengths: {lengths}")
```

`una run .` prints:

```text include="steps/14-printing-tasks/expected/output.txt"
checking LAMP-01
checking RUG-07
checking DESK-02
lengths: [7, 6, 7]
```

`una run` gives the lines in task order every time, for the reason of [The interpreter and an executable](#the-interpreter-and-an-executable). But tasks that run at the same time may print in any order: a program built into an executable may print `checking RUG-07` first. Each task's own lines keep their order, and the result, `lengths: [7, 6, 7]`, is always the same. When the order of the lines matters, print after the block, from the results, as every other program of this chapter does.

### The interpreter and an executable

`una run` and `una test` run your program in Una's **interpreter**, which follows the program step by step. It runs the tasks of a block one after another, in their order: that is one of the ways the tasks may run, and it is the one the guarantee describes, so the interpreter is the reference. Its runs are the same every time.

`una build` turns a program into an **executable**, a file the computer runs directly ([section 18.5](/learn/tools/#s18-5)). There, each task runs on its own **thread**, a line of work that the computer runs at the same time as others, on another core when it has one. Each task gets its own copy of the values it reads when it starts, and its result is copied back when it ends. The tasks may really run at the same time, but nothing promises it: an executable starts a block's tasks a group at a time, so a very long list does not run all at once, and how many run together is the implementation's choice. The executable gives the same result, the same failure and the same exit status as the interpreter, as long as the run stays within its limits. Each task's copies count toward the run's memory limit, so an executable can stop with U6003 where `una run` does not ([section 16.4](/learn/memory/#s16-4)). Within the limits, what may differ is only what timing decides: the order in which the lines of different tasks appear, and how far a canceled task got.

### What Una leaves out

`together` and `together for` are the whole of concurrency in Una. There are no task values to keep and wait for later, no tasks that run on after their block, no race between tasks to take the first answer, no timeouts, and no channels for tasks to send each other messages. `async` and `await`, which some languages use for waiting on a service, are not part of Una: `una check` answers U0103, "not supported; use `together`" ([Writing `await` (U0103)](#writing-await-u0103)). A task that never ends keeps its block from ending: Una does not check that a task ends.

### Code whose result does not depend on timing

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A count or a total over the tasks | return a value from each task, then combine the list after the block |
| One service failure to fail everything | `if error pass` in the task: the first failure in order wins |
| To go on without a service that fails | `if error use` in the task, or `attempt` ([chapter 7](/learn/failure/#s7-4)) |
| Lines printed in a fixed order | print after the block, from its results |
| An example about the services a block asked | `expect performed` on tasks before the failing one, or on a block that does not fail |
:::

### Check yourself: the first failure

`close_sites` closes each site at once, and a site with no count fails:

```una include="steps/15-first-failure/src/closing.una" title="steps/15-first-failure/src/closing.una"
module closing

kind CloseError = | NotCounted(site: Text)

--- The closing count of a site, from the counts that came in. A site with no count fails.
closing_count(site: Text, counted: Map[Text, Int]) -> Int
  fails CloseError
=
  counted.get(key: site)
    if none fail NotCounted(site: site)

--- The closing count of every site, one task per site.
close_sites(sites: List[Text], counted: Map[Text, Int]) -> List[Int]
  fails CloseError
=
  together for site in sites
    closing_count(site, counted: counted)
      if error pass

pub main() -> Unit
  uses @console: Console[print]
=
  let counted = empty_map().with(key: "north", value: 12)
  let outcome = attempt close_sites(["north", "south", "east"], counted: counted)
  @console.print("{outcome}")
```

Only `north` has a count, so the tasks for `south` and `east` both fail. What does `una run .` print, every time?

:::answer Show the answer
```text include="steps/15-first-failure/expected/output.txt"
Err(NotCounted("south"))
```

The block fails with the failure of the first task, in list order, that fails: `south`, as a run one after another would. In an executable the `east` task may fail first, and the answer is the same.
:::

## 15.4 Day-to-day: asking every warehouse at once

### What the program must do

A store keeps its stock in three warehouses, north, south and east. When an order comes in, the store needs to know, for each line, how many units of the SKU each warehouse holds, whether the three together hold enough, and whether the whole order can ship. The warehouses are services, and asking each one takes time, so the check should ask all three at once, and check all the lines of the order at once. When a warehouse does not answer, the check stops, and says which warehouse to try again.

The program is one module, `availability`. Its warehouses are handlers inside the program, so the whole check runs with no network, and its examples replace each warehouse with a fake.

### The kinds and the warehouses

```una include="day-to-day/src/availability.una#StockError..offline" title="day-to-day/src/availability.una" caption="the kinds, the capability and the handlers" verified="check"
--- Why a warehouse gave no count.
pub kind StockError = | Offline(site: Text)

--- One line of an order: a SKU and how many units the customer wants.
pub kind OrderLine
  sku: Text
  quantity: Int

--- What each warehouse holds of one line's SKU.
pub kind Availability
  sku: Text
  wanted: Int
  north: Int
  south: Int
  east: Int

--- A warehouse's stock service: the units of a SKU on its shelves.
pub capability Warehouse
  op on_hand(sku: Text) -> Int
    fails StockError

--- A warehouse whose stock is held in a map: none of a SKU it does not stock.
pub handler shelves(stock: Map[Text, Int]) for Warehouse
  op on_hand(sku) = stock.get(key: sku).or_else(default: 0)

--- A warehouse that does not answer.
pub handler offline(site: Text) for Warehouse
  op on_hand(sku) = fail Offline(site)
```

`OrderLine` is what the customer asks for. `Availability` is what the warehouses answer about one line: the SKU, the units wanted, and one field per warehouse. `Warehouse` is the stock service, with one operation that can fail with `StockError`. `shelves` answers from a map, as a real warehouse would answer from its stock list, and `offline` stands for a warehouse that does not answer, with the name of its site in the failure.

### One line: three warehouses at once

```una include="day-to-day/src/availability.una#availability" title="day-to-day/src/availability.una" caption="one line" verified="check"
--- What the three warehouses hold of a line's SKU, all three asked at the same time.
pub availability(line: OrderLine) -> Availability
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  uses @east: Warehouse[on_hand]
  fails StockError
=
  together
    let north = @north.on_hand(line.sku)
      if error pass
    let south = @south.on_hand(line.sku)
      if error pass
    let east = @east.on_hand(line.sku)
      if error pass
  Availability(sku: line.sku, wanted: line.quantity, north: north, south: south, east: east)
```

`availability` holds three warehouse bindings, `@north`, `@south` and `@east`, and asks all three in one `together` block, a branch each. Each branch passes its failure on: a count that misses a warehouse would be wrong, so any warehouse that does not answer fails the line. The record is built on the first line after the block, when the three counts are in.

### An order: every line at once

```una include="day-to-day/src/availability.una#check_order" title="day-to-day/src/availability.una" caption="the order" verified="check"
--- Every line of an order, all the lines checked at the same time.
pub check_order(lines: List[OrderLine]) -> List[Availability]
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  uses @east: Warehouse[on_hand]
  fails StockError
=
  together for line in lines
    availability(line)
      if error pass
```

`check_order` runs one task per line of the order, and each task runs `availability`, which starts three tasks of its own. An order of two lines makes six questions, which may all be in progress at once. The list comes back in the order of the lines, and if any line fails, the whole order fails with the failure of the first line, in order, that fails.

### The pure parts: what is held, and the report

```una include="day-to-day/src/availability.una#held..reason" title="day-to-day/src/availability.una" caption="the pure functions" verified="check"
--- The units of the line's SKU in the three warehouses together.
pub held(found: Availability) -> Int = found.north + found.south + found.east

--- Whether the three warehouses together hold enough units for the line.
pub can_ship(found: Availability) -> Bool = held(found) >= found.wanted

--- Whether every line of the order can ship.
pub ships_whole(found: List[Availability]) -> Bool = found.filter(keep: fn(line) -> not can_ship(line)).is_empty

--- One line of the report: the SKU, what each warehouse holds, and whether it ships.
pub report_line(found: Availability) -> Text
=
  let counts = "{found.north} + {found.south} + {found.east} = {held(found)}"
  let verdict = if can_ship(found) then "ships" else "short by {found.wanted - held(found)}"
  "{found.sku}: {found.wanted} wanted, {counts} on hand, {verdict}"

--- What a person reads when a warehouse did not answer.
pub reason(failure: StockError) -> Text
=
  when failure
    is Offline(site) -> "the {site} warehouse did not answer; check again later"
```

Everything else is pure: it uses no service and runs no task. `held` adds the three counts, `can_ship` compares them with what is wanted, and `ships_whole` keeps the lines that cannot ship and checks that there are none. `report_line` builds one line of the report, and `reason` turns a failure into a sentence. The concurrent part of the program stays small, in two functions, and everything it gives back is an ordinary value.

### Printing the report

```una include="day-to-day/src/availability.una#north_stock..main" title="day-to-day/src/availability.una" caption="the stock and the report" verified="check, run"
--- The stock of the north warehouse.
pub north_stock() -> Map[Text, Int] = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)

--- The stock of the south warehouse.
pub south_stock() -> Map[Text, Int] = empty_map().with(key: "LAMP-01", value: 2).with(key: "RUG-07", value: 3)

--- The stock of the east warehouse.
pub east_stock() -> Map[Text, Int] = empty_map().with(key: "DESK-02", value: 1).with(key: "RUG-07", value: 5)

--- Prints the report of one order, or why it could not be checked.
pub print_report(order: Text, outcome: Result[List[Availability], StockError]) -> Unit
  uses @console: Console[print]
=
  @console.print("Order {order}")
  when outcome
    is Ok(found) ->
      for line in found
        @console.print("  {report_line(line)}")
      let whole = if ships_whole(found) then "the whole order ships" else "the order waits for stock"
      @console.print("  {whole}")
    is Err(failure) -> @console.print("  {reason(failure)}")

--- Checks two orders against the three warehouses, then the first again while one is offline.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = [OrderLine(sku: "LAMP-01", quantity: 5), OrderLine(sku: "DESK-02", quantity: 2)]
  let rugs = [OrderLine(sku: "RUG-07", quantity: 6), OrderLine(sku: "LAMP-01", quantity: 9)]
  let first = attempt check_order(lamps) with @north = shelves(north_stock()), @south = shelves(south_stock()), @east = shelves(east_stock())
  print_report("1042", outcome: first)
  let second = attempt check_order(rugs) with @north = shelves(north_stock()), @south = shelves(south_stock()), @east = shelves(east_stock())
  print_report("1043", outcome: second)
  let retry = attempt check_order(lamps) with @north = shelves(north_stock()), @south = shelves(south_stock()), @east = offline("east")
  print_report("1042, again", outcome: retry)
```

The three `*_stock` functions give each warehouse's stock list. `print_report` takes the outcome of a check, a `Result` from `attempt` ([chapter 7](/learn/failure/#s7-4)), and prints either the lines or the reason. It prints after the check has ended, with a plain `for` loop, so the lines are always in order. `main` checks two orders with all three warehouses, then the first order again with the east warehouse offline. Each check installs the three handlers for its one call, with `with`.

### Running it

In the `day-to-day` directory:

```sh
una check .
una run .
```

`una run .` prints:

```text include="day-to-day/expected/output.txt"
Order 1042
  LAMP-01: 5 wanted, 4 + 2 + 0 = 6 on hand, ships
  DESK-02: 2 wanted, 1 + 0 + 1 = 2 on hand, ships
  the whole order ships
Order 1043
  RUG-07: 6 wanted, 0 + 3 + 5 = 8 on hand, ships
  LAMP-01: 9 wanted, 4 + 2 + 0 = 6 on hand, short by 3
  the order waits for stock
Order 1042, again
  the east warehouse did not answer; check again later
```

Order 1042 ships whole. Order 1043 holds a line that is short: 9 lamps wanted, 6 on hand. The third check fails at the east warehouse, so it prints the reason and no lines.

### The whole program

```una include="day-to-day/src/availability.una" title="day-to-day/src/availability.una" caption="the whole program" verified="check, run, test"
module availability

-- Checks an order against the stock of three warehouses, asking all of them at once.

--- Why a warehouse gave no count.
pub kind StockError = | Offline(site: Text)

--- One line of an order: a SKU and how many units the customer wants.
pub kind OrderLine
  sku: Text
  quantity: Int

--- What each warehouse holds of one line's SKU.
pub kind Availability
  sku: Text
  wanted: Int
  north: Int
  south: Int
  east: Int

--- A warehouse's stock service: the units of a SKU on its shelves.
pub capability Warehouse
  op on_hand(sku: Text) -> Int
    fails StockError

--- A warehouse whose stock is held in a map: none of a SKU it does not stock.
pub handler shelves(stock: Map[Text, Int]) for Warehouse
  op on_hand(sku) = stock.get(key: sku).or_else(default: 0)

--- A warehouse that does not answer.
pub handler offline(site: Text) for Warehouse
  op on_hand(sku) = fail Offline(site)

--- What the three warehouses hold of a line's SKU, all three asked at the same time.
pub availability(line: OrderLine) -> Availability
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  uses @east: Warehouse[on_hand]
  fails StockError
=
  together
    let north = @north.on_hand(line.sku)
      if error pass
    let south = @south.on_hand(line.sku)
      if error pass
    let east = @east.on_hand(line.sku)
      if error pass
  Availability(sku: line.sku, wanted: line.quantity, north: north, south: south, east: east)

--- Every line of an order, all the lines checked at the same time.
pub check_order(lines: List[OrderLine]) -> List[Availability]
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  uses @east: Warehouse[on_hand]
  fails StockError
=
  together for line in lines
    availability(line)
      if error pass

--- The units of the line's SKU in the three warehouses together.
pub held(found: Availability) -> Int = found.north + found.south + found.east

--- Whether the three warehouses together hold enough units for the line.
pub can_ship(found: Availability) -> Bool = held(found) >= found.wanted

--- Whether every line of the order can ship.
pub ships_whole(found: List[Availability]) -> Bool = found.filter(keep: fn(line) -> not can_ship(line)).is_empty

--- One line of the report: the SKU, what each warehouse holds, and whether it ships.
pub report_line(found: Availability) -> Text
=
  let counts = "{found.north} + {found.south} + {found.east} = {held(found)}"
  let verdict = if can_ship(found) then "ships" else "short by {found.wanted - held(found)}"
  "{found.sku}: {found.wanted} wanted, {counts} on hand, {verdict}"

--- What a person reads when a warehouse did not answer.
pub reason(failure: StockError) -> Text
=
  when failure
    is Offline(site) -> "the {site} warehouse did not answer; check again later"

--- The stock of the north warehouse.
pub north_stock() -> Map[Text, Int] = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)

--- The stock of the south warehouse.
pub south_stock() -> Map[Text, Int] = empty_map().with(key: "LAMP-01", value: 2).with(key: "RUG-07", value: 3)

--- The stock of the east warehouse.
pub east_stock() -> Map[Text, Int] = empty_map().with(key: "DESK-02", value: 1).with(key: "RUG-07", value: 5)

--- Prints the report of one order, or why it could not be checked.
pub print_report(order: Text, outcome: Result[List[Availability], StockError]) -> Unit
  uses @console: Console[print]
=
  @console.print("Order {order}")
  when outcome
    is Ok(found) ->
      for line in found
        @console.print("  {report_line(line)}")
      let whole = if ships_whole(found) then "the whole order ships" else "the order waits for stock"
      @console.print("  {whole}")
    is Err(failure) -> @console.print("  {reason(failure)}")

--- Checks two orders against the three warehouses, then the first again while one is offline.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = [OrderLine(sku: "LAMP-01", quantity: 5), OrderLine(sku: "DESK-02", quantity: 2)]
  let rugs = [OrderLine(sku: "RUG-07", quantity: 6), OrderLine(sku: "LAMP-01", quantity: 9)]
  let first = attempt check_order(lamps) with @north = shelves(north_stock()), @south = shelves(south_stock()), @east = shelves(east_stock())
  print_report("1042", outcome: first)
  let second = attempt check_order(rugs) with @north = shelves(north_stock()), @south = shelves(south_stock()), @east = shelves(east_stock())
  print_report("1043", outcome: second)
  let retry = attempt check_order(lamps) with @north = shelves(north_stock()), @south = shelves(south_stock()), @east = offline("east")
  print_report("1042, again", outcome: retry)

example "each warehouse's count goes into its own field"
  given @north = shelves(north_stock())
  given @south = shelves(south_stock())
  given @east = shelves(east_stock())
  do availability(OrderLine(sku: "LAMP-01", quantity: 5))
  expect result == Availability(sku: "LAMP-01", wanted: 5, north: 4, south: 2, east: 0)

example "the lines come back in the order of the order"
  given @north = shelves(north_stock())
  given @south = shelves(south_stock())
  given @east = shelves(east_stock())
  do check_order([OrderLine(sku: "RUG-07", quantity: 1), OrderLine(sku: "DESK-02", quantity: 1)])
  expect result.len == 2
  expect result.first() == Some(Availability(sku: "RUG-07", wanted: 1, north: 0, south: 3, east: 5))

example "an empty order asks no warehouse"
  given @north = shelves(north_stock())
  given @south = shelves(south_stock())
  given @east = shelves(east_stock())
  do check_order([])
  expect result == []
  expect not performed @north.on_hand

example "a warehouse that does not answer fails the line"
  given @north = shelves(north_stock())
  given @south = shelves(south_stock())
  given @east = offline("east")
  do availability(OrderLine(sku: "LAMP-01", quantity: 5))
  expect fails Offline

example "the warehouses before the one that fails are still asked"
  given @north = shelves(north_stock())
  given @south = offline("south")
  given @east = shelves(east_stock())
  do availability(OrderLine(sku: "LAMP-01", quantity: 5))
  expect fails Offline
  expect performed @north.on_hand

example "one line that cannot be checked fails the whole order"
  given @north = shelves(north_stock())
  given @south = offline("south")
  given @east = shelves(east_stock())
  do check_order([OrderLine(sku: "LAMP-01", quantity: 5), OrderLine(sku: "DESK-02", quantity: 2)])
  expect fails Offline

example "a line short of stock says by how much"
  do report_line(Availability(sku: "LAMP-01", wanted: 9, north: 4, south: 2, east: 0))
  expect result == "LAMP-01: 9 wanted, 4 + 2 + 0 = 6 on hand, short by 3"

example "an order ships whole only when every line can ship"
  do ships_whole([Availability(sku: "LAMP-01", wanted: 5, north: 4, south: 2, east: 0), Availability(sku: "RUG-07", wanted: 9, north: 0, south: 3, east: 5)])
  expect not result

example "an empty order ships whole"
  do ships_whole([])
  expect result

example "the reason names the warehouse"
  do reason(Offline("east"))
  expect result == "the east warehouse did not answer; check again later"
```

## 15.5 Testing it

### Fakes for each warehouse

The examples install each warehouse with a `given` line, as [chapter 14](/learn/testing/#s14-3) shows: `shelves` with a stock list for a warehouse that answers, and `offline` for one that does not. The handlers are part of the program, so the examples need no network and give the same answer on every run. Every example of a function that asks the warehouses gives all three bindings a `given` line.

### The counts, and the order of the results

```una include="day-to-day/src/availability.una#L118-L139" title="day-to-day/src/availability.una" caption="the happy paths"
example "each warehouse's count goes into its own field"
  given @north = shelves(north_stock())
  given @south = shelves(south_stock())
  given @east = shelves(east_stock())
  do availability(OrderLine(sku: "LAMP-01", quantity: 5))
  expect result == Availability(sku: "LAMP-01", wanted: 5, north: 4, south: 2, east: 0)

example "the lines come back in the order of the order"
  given @north = shelves(north_stock())
  given @south = shelves(south_stock())
  given @east = shelves(east_stock())
  do check_order([OrderLine(sku: "RUG-07", quantity: 1), OrderLine(sku: "DESK-02", quantity: 1)])
  expect result.len == 2
  expect result.first() == Some(Availability(sku: "RUG-07", wanted: 1, north: 0, south: 3, east: 5))

example "an empty order asks no warehouse"
  given @north = shelves(north_stock())
  given @south = shelves(south_stock())
  given @east = shelves(east_stock())
  do check_order([])
  expect result == []
  expect not performed @north.on_hand
```

The first example checks that each warehouse's count lands in its own field. The second checks the guarantee of `together for`: the lines come back in the order of the order, whatever order their tasks finish in. The third checks the edge: an empty order starts no task, so no warehouse is asked, which `expect not performed` states.

### The failure paths

```una include="day-to-day/src/availability.una#L141-L161" title="day-to-day/src/availability.una" caption="the failure paths"
example "a warehouse that does not answer fails the line"
  given @north = shelves(north_stock())
  given @south = shelves(south_stock())
  given @east = offline("east")
  do availability(OrderLine(sku: "LAMP-01", quantity: 5))
  expect fails Offline

example "the warehouses before the one that fails are still asked"
  given @north = shelves(north_stock())
  given @south = offline("south")
  given @east = shelves(east_stock())
  do availability(OrderLine(sku: "LAMP-01", quantity: 5))
  expect fails Offline
  expect performed @north.on_hand

example "one line that cannot be checked fails the whole order"
  given @north = shelves(north_stock())
  given @south = offline("south")
  given @east = shelves(east_stock())
  do check_order([OrderLine(sku: "LAMP-01", quantity: 5), OrderLine(sku: "DESK-02", quantity: 2)])
  expect fails Offline
```

One warehouse offline fails the line, and one line that fails fails the whole order. The second example states the rule of the first failure from the other side: the south warehouse fails, and the north one, the branch before it, was still asked.

### What not to test: what timing decides

No example states whether the east warehouse was asked when the south one failed. Under `una test`, the east branch never starts, since the tasks run one after another. But the language does not promise that: in an executable, the east branch, which comes after the failing one, may have asked its warehouse before it was canceled. An example that states it would test the interpreter's schedule, not the guarantee. Test what the guarantee fixes: the result, the failure, and the effects of the tasks before a failing one.

### The pure functions

The last four examples test `report_line`, `ships_whole` and `reason` with plain values, without fakes. An empty order ships whole, since none of its lines is short.

### Running the examples

```text include="day-to-day/expected/commands/test.txt#L2-L13"
example availability "each warehouse's count goes into its own field" ... ok
example availability "the lines come back in the order of the order" ... ok
example availability "an empty order asks no warehouse" ... ok
example availability "a warehouse that does not answer fails the line" ... ok
example availability "the warehouses before the one that fails are still asked" ... ok
example availability "one line that cannot be checked fails the whole order" ... ok
example availability "a line short of stock says by how much" ... ok
example availability "an order ships whole only when every line can ship" ... ok
example availability "an empty order ships whole" ... ok
example availability "the reason names the warehouse" ... ok

10 examples: 10 passed, 0 failed
```

## 15.6 Common mistakes

Each mistake is a small change to `day-to-day/src/availability.una`, followed by what `una check .` reports. None of these diagnostics carries an edit that `una fix` can apply: each repair depends on what you meant.

### Counting in a shared name inside `together for` (U2023)

:::mistake
Count the lines checked in an outer `let edit` name:

```diff include="day-to-day..mistakes/1:src/availability.una" context="1"
--- a/src/availability.una
+++ b/src/availability.una
@@ -56,5 +56,8 @@
 =
-  together for line in lines
+  let edit asked = 0
+  let found = together for line in lines
+    asked = asked + 1
     availability(line)
       if error pass
+  found
 
```

```text include="mistakes/1/expected/rendered.txt"
[U2023] Error: `asked` is declared outside this `together` task, which captures its value and cannot change it, so it cannot be assigned here; return the new value from the task instead
    ╭─[ src/availability.una:59:5 ]
    │
 59 │     asked = asked + 1
    │     ──┬──
    │       ╰──── `asked` is declared outside this `together` task, which captures its value and cannot change it, so it cannot be assigned here; return the new value from the task instead
    │
    │ Note: run `una explain U2023` for an explanation
────╯
```

*Why:* each task captures the names around it as they were when the block started, and runs at the same time as the others. An assignment to an outer name would be two clerks writing on one whiteboard: a race, which Una refuses. The marks point at the name being assigned.

*Fix:* return what each task computes, and combine the results after the block. Here the count is `found.len`. See [U2023](/docs/errors/U2023/).
:::

### Building the result inside the block (U2024, U1001)

:::mistake
Indent the line that builds the record, so that it stands under `together`:

```diff include="day-to-day..mistakes/2:src/availability.una" context="1"
--- a/src/availability.una
+++ b/src/availability.una
@@ -47,3 +47,3 @@
       if error pass
-  Availability(sku: line.sku, wanted: line.quantity, north: north, south: south, east: east)
+    Availability(sku: line.sku, wanted: line.quantity, north: north, south: south, east: east)
 
```

```text include="mistakes/2/expected/rendered.txt#L1-L13"
[U2024] Error: the body of `together` holds only `let` statements, one per branch; call a function from a branch's `let` for more steps
    ╭─[ src/availability.una:41:3 ]
    │
 41 │   together
    │   ────┬───
    │       ╰───── the body of `together` holds only `let` statements, one per branch; call a function from a branch's `let` for more steps
    │
 48 │     Availability(sku: line.sku, wanted: line.quantity, north: north, south: south, east: east)
    │     ─────────────────────────────────────────────┬────────────────────────────────────────────
    │                                                  ╰────────────────────────────────────────────── not a `let`
    │
    │ Note: run `una explain U2024` for an explanation
────╯
```

*Why:* every line under `together` belongs to the block, and the block holds only `let` lines, one per task. The marks point at `together` and at the line that is not a `let`. Three more diagnostics follow, U1001 at `north`, `south` and `east`: the names that the block's tasks bind exist only after the block, so a line inside it cannot read them.

*Fix:* write the line that uses the branches' names after the block, at the indentation of `together`. See [U2024](/docs/errors/U2024/).
:::

### Naming a `together` block with `let` (U0101)

:::mistake
Give the block a name, as if it were a value:

```diff include="day-to-day..mistakes/3:src/availability.una" context="1"
--- a/src/availability.una
+++ b/src/availability.una
@@ -40,3 +40,3 @@
 =
-  together
+  let counts = together
     let north = @north.on_hand(line.sku)
```

```text include="mistakes/3/expected/rendered.txt"
[U0101] Error: `together` with branches is a statement; write `together for` to build a list
    ╭─[ src/availability.una:41:16 ]
    │
 41 │   let counts = together
    │                ────┬───
    │                    ╰───── `together` with branches is a statement; write `together for` to build a list
    │
    │ Note: run `una explain U0101` for an explanation
────╯
```

*Why:* `together` with branches is a statement. Its results are the names of its branches, `north`, `south` and `east`, so there is no single value for `counts` to hold. The message also names the form that does give a value, `together for`, for a list of results.

*Fix:* remove `let counts =`, and use the names of the branches after the block. See [U0101](/docs/errors/U0101/).
:::

### A branch without its clause (U3007)

:::mistake
Leave out the clause of the east branch:

```diff include="day-to-day..mistakes/4:src/availability.una" context="1"
--- a/src/availability.una
+++ b/src/availability.una
@@ -46,3 +46,2 @@
     let east = @east.on_hand(line.sku)
-      if error pass
   Availability(sku: line.sku, wanted: line.quantity, north: north, south: south, east: east)
```

```text include="mistakes/4/expected/rendered.txt"
[U3007] Error: `@east.on_hand` can fail with `StockError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
    ╭─[ src/availability.una:46:16 ]
    │
 46 │     let east = @east.on_hand(line.sku)
    │                ───────────┬───────────
    │                           ╰───────────── `@east.on_hand` can fail with `StockError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
    │
    │ Note: run `una explain U3007` for an explanation
────╯
```

*Why:* a branch is a `let` line, and handles its failures as that `let` would outside the block. `@east.on_hand` can fail, so its line needs a clause, as every call that can fail does ([chapter 7](/learn/failure/#s7-3)). The other two branches still have theirs; each branch is checked on its own.

*Fix:* put the clause back under the branch, `if error pass`, or choose another, such as `if error use 0` for a count that may miss a warehouse. See [U3007](/docs/errors/U3007/).
:::

### Printing with `together for` (U0101)

:::mistake
Print the lines of the report with `together for`, to print them all at once:

```diff include="day-to-day..mistakes/5:src/availability.una" context="1"
--- a/src/availability.una
+++ b/src/availability.una
@@ -98,3 +98,3 @@
     is Ok(found) ->
-      for line in found
+      together for line in found
         @console.print("  {report_line(line)}")
```

```text include="mistakes/5/expected/rendered.txt"
[U0101] Error: a `together for` must be the last line of its block or the value of a `let` or of an assignment
    ╭─[ src/availability.una:99:7 ]
    │
 99 │       together for line in found
    │       ────┬───
    │           ╰───── a `together for` must be the last line of its block or the value of a `let` or of an assignment
    │
    │ Note: run `una explain U0101` for an explanation
────╯
```

*Why:* `together for` builds a list, so it must stand where its value is used: named by a `let`, assigned to a `let edit` name, or as the last line of its block. Here it is neither, since the summary line follows it. Even where it is allowed, printing from tasks would print the lines in an order that timing decides.

*Fix:* keep the plain `for` loop. Printing after the check, in order, is what a report wants. See [U0101](/docs/errors/U0101/).
:::

### Writing `await` (U0103)

:::mistake
Wait for the warehouse with `await`, as some other languages do:

```diff include="day-to-day..mistakes/6:src/availability.una" context="1"
--- a/src/availability.una
+++ b/src/availability.una
@@ -41,3 +41,3 @@
   together
-    let north = @north.on_hand(line.sku)
+    let north = await @north.on_hand(line.sku)
       if error pass
```

```text include="mistakes/6/expected/rendered.txt"
[U0103] Error: `await` is not supported; use `together`
    ╭─[ src/availability.una:42:17 ]
    │
 42 │     let north = await @north.on_hand(line.sku)
    │                 ──┬──
    │                   ╰──── `await` is not supported; use `together`
    │
    │ Note: run `una explain U0103` for an explanation
────╯
```

*Why:* in Una, every call already waits for its answer, and work that should wait at the same time goes in a `together` block. `await` and `async` are reserved words that Una does not use, so the check reports them and names the construct to use.

*Fix:* remove `await`. The branch already runs at the same time as its siblings. See [U0103](/docs/errors/U0103/).
:::

## 15.7 Exercises

The exercises come with the chapter's download, `15-concurrency.tar.gz`. Each one starts from `exercises/N/start`: the day-to-day program with the exercise's example added, and a stub of the function to write, a header with a placeholder body. `una test .` fails there until the exercise is done. Check your work with `una check .` and `una test .`.

### Exercise 1: the SKUs of an order

::::exercise
Write `skus_of(lines)`, which gives back the SKU of each line of an order, in the order of the lines, with `together for`. The start package has the stub and its example:

```una include="exercises/1/start/src/availability.una#skus_of" title="exercises/1/start/src/availability.una"
--- The SKU of each line of an order, in the order of the lines.
pub skus_of(lines: List[OrderLine]) -> List[Text] = []
```

```una include="exercises/1/start/src/availability.una#L182-L184" title="exercises/1/start/src/availability.una"
example "the SKUs come in the order of the lines"
  do skus_of([OrderLine(sku: "LAMP-01", quantity: 5), OrderLine(sku: "DESK-02", quantity: 2)])
  expect result == ["LAMP-01", "DESK-02"]
```

:::hint
*Hint:* the body is a `together for` over `lines`, and the last line of its body is the SKU of the line.
:::

On the start package, `una test .` reports:

```text include="exercises/1/start/expected/commands/test.txt#L12-L16"
example availability "the SKUs come in the order of the lines" ... FAILED
  src/availability.una:184: expect result == ["LAMP-01", "DESK-02"]
  it is false, with `result` = `[]`

11 examples: 10 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Walk the lines, and give back each one's SKU:

```diff include="exercises/1/start..exercises/1/answer:src/availability.una" context="1" title="src/availability.una"
--- a/src/availability.una
+++ b/src/availability.una
@@ -61,3 +61,6 @@
 --- The SKU of each line of an order, in the order of the lines.
-pub skus_of(lines: List[OrderLine]) -> List[Text] = []
+pub skus_of(lines: List[OrderLine]) -> List[Text]
+=
+  together for line in lines
+    line.sku
 
```

The function is pure, and asks no warehouse. For a short computation like this one, `lines.map(each: fn(line) -> line.sku)` would do the same, as [Building a list at the same time](#s15-2) says.
:::
::::

### Exercise 2: counts that record a silent warehouse as none

::::exercise
A clerk wants to see what each warehouse holds of a line's SKU, even when one of them does not answer. Write `partial(line)`, which asks the three warehouses at the same time and gives back an `Availability`, as `availability` does, but records 0 in the field of a warehouse that does not answer instead of failing. The start package has the stub, and an example in which the south warehouse is offline:

```una include="exercises/2/start/src/availability.una#partial" title="exercises/2/start/src/availability.una"
--- What each warehouse holds of a line's SKU, all three asked at the same time. A warehouse
--- that does not answer is recorded as holding none.
pub partial(line: OrderLine) -> Availability
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  uses @east: Warehouse[on_hand]
=
  Availability(sku: line.sku, wanted: line.quantity, north: 0, south: 0, east: 0)
```

```una include="exercises/2/start/src/availability.una#L188-L193" title="exercises/2/start/src/availability.una"
example "a warehouse that does not answer is recorded as holding none"
  given @north = shelves(north_stock())
  given @south = offline("south")
  given @east = shelves(east_stock())
  do partial(OrderLine(sku: "DESK-02", quantity: 2))
  expect result == Availability(sku: "DESK-02", wanted: 2, north: 1, south: 0, east: 1)
```

:::hint
*Hint:* start from the `together` block of `availability`. Change each branch's clause so that a warehouse that does not answer gives 0, and build the record on the line after the block.
:::

On the start package, `una test .` reports:

```text include="exercises/2/start/expected/commands/test.txt#L12-L16"
example availability "a warehouse that does not answer is recorded as holding none" ... FAILED
  src/availability.una:193: expect result == Availability(sku: "DESK-02", wanted: 2, north: 1, south: 0, east: 1)
  it is false, with `result` = `Availability(sku: "DESK-02", wanted: 2, north: 0, south: 0, east: 0)`

11 examples: 10 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/2/answer`).
A `together` block with a clause per branch that gives a default, then the record:

```diff include="exercises/2/start..exercises/2/answer:src/availability.una" context="1" title="src/availability.una"
--- a/src/availability.una
+++ b/src/availability.una
@@ -67,3 +67,10 @@
 =
-  Availability(sku: line.sku, wanted: line.quantity, north: 0, south: 0, east: 0)
+  together
+    let north = @north.on_hand(line.sku)
+      if error use 0
+    let south = @south.on_hand(line.sku)
+      if error use 0
+    let east = @east.on_hand(line.sku)
+      if error use 0
+  Availability(sku: line.sku, wanted: line.quantity, north: north, south: south, east: east)
 
```

`DESK-02` has 1 unit in the north warehouse and 1 in the east one. The south one does not answer, so its branch gives 0, and its field says 0. Every failure is handled in its branch, so the block never fails, and `partial` needs no `fails` in its header. Unlike `estimate` of [section 15.1](#s15-1), which adds the counts, `partial` keeps each warehouse's count in its own field.
:::
::::

### Exercise 3: every order of the day at once

::::exercise
At the end of the day, the store checks every open order at once. Write `check_day(orders)`, which gives back, for each order, whether it ships whole, in the order of the orders. Every order is checked at the same time, and a warehouse that does not answer fails the whole day. The start package has the stub and its example:

```una include="exercises/3/start/src/availability.una#check_day" title="exercises/3/start/src/availability.una"
--- For each order of the day, whether it ships whole: every order checked at the same time.
pub check_day(orders: List[List[OrderLine]]) -> List[Bool]
  uses @north: Warehouse[on_hand]
  uses @south: Warehouse[on_hand]
  uses @east: Warehouse[on_hand]
  fails StockError
=
  []
```

```una include="exercises/3/start/src/availability.una#L188-L193" title="exercises/3/start/src/availability.una"
example "each order of the day gets its own answer, in order"
  given @north = shelves(north_stock())
  given @south = shelves(south_stock())
  given @east = shelves(east_stock())
  do check_day([[OrderLine(sku: "LAMP-01", quantity: 5)], [OrderLine(sku: "LAMP-01", quantity: 9)]])
  expect result == [true, false]
```

:::hint
*Hint:* a `together for` over the orders, whose body checks one order with `check_order` and then calls `ships_whole`. `check_order` can fail, so its line needs a `let` and a clause.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
One task per order, and inside it, `check_order`'s own tasks:

```diff include="exercises/3/start..exercises/3/answer:src/availability.una" context="1" title="src/availability.una"
--- a/src/availability.una
+++ b/src/availability.una
@@ -67,3 +67,6 @@
 =
-  []
+  together for order in orders
+    let found = check_order(order)
+      if error pass
+    ships_whole(found)
 
```

The first order wants 5 lamps, and the warehouses hold 6: it ships. The second wants 9: it waits. Each task runs `check_order`, which runs a task per line, and each line asks three warehouses: tasks three levels deep, and the result is still the list a run one after another would give.
:::
::::

## 15.8 Recap and reference

### For agents

:::agents
`una --json check .` prints each diagnostic of this chapter with its `code`, `message` and `primary` span; none carries a repair edit, so the document reports `"fixable":0`, and `una fix` changes nothing. U2023 marks the outer name a task assigns; U2024 marks `together`, with each line of the block that is not a `let`; U0101 marks `together` or `together for` where it stands; U0103 marks `async` or `await`. In `una --json test .`, an example's `trace` lists the events of a block's tasks in task order, each event with its task's path in `task`. The compact rule: *a `together` block or a `together for` gives the result of running its tasks one after another, in order, stopping at the first failure; a task reads outer names and never assigns them.*
:::

### Recap

:::recap
- `together` with two or more `let` branches runs them as tasks, and binds their names after the block, in order.
- A branch sees the names bound before the block, never its siblings, and keeps its own clause.
- `together for x in xs` runs one task per element and gives their values in list order.
- `together` is a statement; `together for` is a value: after `let`, in an assignment, or last in a block.
- A task never assigns an outer name (U2023): return a value, and combine the list after the block.
- The first failure in order wins; later tasks are canceled, earlier ones run on.
- Effects are recorded in task order, but printed lines may appear in any order: print after the block.
:::

### Reference

:::reference
- Construct pages: [`together`](/docs/language/control-flow/together/), [`for`](/docs/language/control-flow/for/), [`let edit`](/docs/language/control-flow/let-edit/), [`if error`](/docs/language/errors/if-error/), [`uses`](/docs/language/capabilities/uses/), [`example`](/docs/language/examples/example/)
- Commands: [`una run`](/docs/cli/run/), [`una test`](/docs/cli/test/), [`una build`](/docs/cli/build/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U0103](/docs/errors/U0103/), [U1001](/docs/errors/U1001/), [U2023](/docs/errors/U2023/), [U2024](/docs/errors/U2024/), [U3007](/docs/errors/U3007/)
- Specification: [structured concurrency](/docs/spec/19-structured-concurrency/), [dynamic semantics](/docs/spec/11-dynamic-semantics/), [the native backend](/docs/spec/16-native-backend/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [errors](/docs/spec/06-errors/)
:::
