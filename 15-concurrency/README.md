---
learn: "15"
title: Concurrency and parallelism
editions: ["0.2"]
codes: [U2023, U2024]
time: 5
builds: A stock query that asks every warehouse at once
prerequisites: ["7", "10", "12", "14"]
template: 2
nav: ["together", "together for", "Common mistakes"]
---

# 15 Concurrency and parallelism

## 15.1 Running work at the same time: `together`


### What concurrent work is

Two clerks can count two aisles at once, and the count of the store is done in the time of the longer aisle, not of both. Work that runs this way is **concurrent**: several pieces of it are in progress at the same time.

In Una, each piece is a **task**: an expression that runs on its own, alongside others, and ends with a result. A `together` block starts its tasks, waits until every one has ended, and then gives their results. No task outlives the block that started it. Running tasks this way, always inside a block that waits for them, is called **structured concurrency**.

### Why Una has `together`

Asking two warehouses how many units they hold takes two round trips over the network, and each one waits for its answer. They do not depend on each other, so they can wait at the same time. Without concurrency, the program waits for each in turn.

In many languages, concurrent work brings two problems. Two threads that write the same counter can lose an update, depending on which one runs first: a **race**. And the result can depend on timing, so a test that passes today fails tomorrow. Una avoids both by its rules: a task cannot assign anything outside itself ([What the result can depend on](#what-the-result-can-depend-on)), and the result of a block is always the result of running its tasks one after another.

### How to write `together`

This step asks three warehouses about a SKU, builds a list of labels, and counts days:

```una include="steps/01-together-forms/src/counts.una" title="steps/01-together-forms/src/counts.una" verified="check, run"
module counts

--- A warehouse's stock service: the units of a SKU on hand.
capability Inventory
  op on_hand(sku: Text) -> Int

--- A warehouse held in memory: 0 for a SKU it does not hold.
handler shelves(stock: Map[Text, Int]) for Inventory
  op on_hand(sku) = stock.get(key: sku).or_else(default: 0)

--- The units of a SKU in one warehouse.
units_of(sku: Text) -> Int
  uses @inventory: Inventory[on_hand]
=
  @inventory.on_hand(sku)

--- The days in each of the first `weeks` weeks of a sale, counted from day 1.
last_days(weeks: Int) -> List[Int]
=
  let days = together for week in 1..weeks
    week * 7
  days

pub main() -> Unit
  uses @console: Console[print]
=
  let north = empty_map().with(key: "LAMP-01", value: 4)
  let south = empty_map().with(key: "LAMP-01", value: 2)
  let east = empty_map().with(key: "DESK-02", value: 3)
  together
    let north_units = units_of("LAMP-01") with @inventory = shelves(north)
    let south_units = units_of("LAMP-01") with @inventory = shelves(south)
    let east_units = units_of("LAMP-01") with @inventory = shelves(east)
  @console.print("LAMP-01: {north_units} + {south_units} + {east_units} = {north_units + south_units + east_units}")
  let edit labels: List[Text] = []
  labels = together for sku in ["LAMP-01", "DESK-02"]
    let size = sku.len
    "[{sku}] ({size} characters)"
  @console.print("{labels}")
  @console.print("last days: {last_days(3)}")
  @console.print("no weeks: {last_days(0)}")
```

```text include="steps/01-together-forms/expected/output.txt"
LAMP-01: 4 + 2 + 0 = 6
["[LAMP-01] (7 characters)", "[DESK-02] (7 characters)"]
last days: [7, 14, 21]
no weeks: []
```

#### Branches: `together` with `let` lines

`together` on a line of its own, then two or more indented `let` lines. Each `let` is a **branch**, and its expression is a task. After the block, the branches' bindings are in scope in order, as plain `let` lines would be: here `north_units`, `south_units` and `east_units`. A branch may install a handler with `with`, as each one here installs its own warehouse.

#### One task per element: `together for`

`together for sku in [...]`, then an indented body, as for a `for` loop ([chapter 9](/learn/loops/#s9-1)). It runs one task per element, and gives the list of what each task's body ends with, in the order of the list. It stands where a value goes: after `let`, as in `last_days`, or after `=` in an assignment, as `labels = together for …` in `main`.

#### Over a range

`together for week in 1..weeks` runs one task per whole number of the range. `last_days(0)` walks the empty range `1..0`, starts no task, and gives an empty list.

### Asking two warehouses at once

This step uses a capability that can fail. `Inventory` is a warehouse's stock service, and each warehouse is a binding of it, `@north` and `@south`. The handler `shelves` answers from a map, and `offline` always fails.

:::steps
```una include="steps/02-together/src/stock.una" title="steps/02-together/src/stock.una" verified="check, run, test"
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

1. **`together` with two `let` branches.** Each `let` is a task. A branch sees the bindings in scope before the block, and none of its siblings: the second branch cannot read `up`. After the block, `up` and `down` are bound, in branch order, as two `let` statements would bind them.
2. **`if error pass` under each branch.** A branch handles its failures as its `let` would outside the block. Here a failure of either warehouse makes the block fail, and `total_on_hand` fails with it.
3. **`together for sku in skus`.** One task per SKU. The body is a block whose last line is the element's value, so the result is a `List[Text]`, in the order of `skus`, whatever order the tasks finish in.
4. **Capabilities in tasks.** Each task uses the bindings of the enclosing function's `uses`. `main` installs both handlers for one call with `with`, and every task of that call sees them.
5. **The example.** `given @south = offline()` makes one warehouse fail, and the example expects the whole count to fail with `Timeout` ([chapter 10, Testing](/learn/testing/#s14-3), covers `given`).
:::

`una run .` prints:

```text include="steps/02-together/expected/output.txt"
LAMP-01: 6 units
DESK-02: 3 units
CHAIR-09: 0 units
```

`una test .` prints:

```text include="steps/02-together/expected/commands/test.txt#L2-L4"
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

#### A task cannot change what is outside it

Count the SKUs asked in an outer `let edit`:

```diff include="steps/02-together..steps/03-shared-counter:src/stock.una" context="1" title="src/stock.una"
--- a/src/stock.una
+++ b/src/stock.una
@@ -36,3 +36,5 @@
 =
-  together for sku in skus
+  let edit asked = 0
+  let lines = together for sku in skus
+    asked = asked + 1
     let units = total_on_hand(sku)
@@ -40,2 +42,3 @@
     "{sku}: {units} units"
+  lines.append(item: "{asked} SKUs asked")
 
```

```text include="steps/03-shared-counter/expected/rendered.txt"
[U2023] Error: `asked` is declared outside this `together` task, which captures its value and cannot change it, so it cannot be assigned here; return the new value from the task instead
    ╭─[ src/stock.una:39:5 ]
    │
 39 │     asked = asked + 1
    │     ──┬──
    │       ╰──── `asked` is declared outside this `together` task, which captures its value and cannot change it, so it cannot be assigned here; return the new value from the task instead
    │
    │ Note: run `una explain U2023` for an explanation
────╯
```

Each task captured `asked` as it was when the block started, so an assignment could only change a task's copy, and two tasks adding 1 at once would be a race. The message gives the fix: return the value from the task. Here the count is `lines.len`.

#### Two branches or more

```diff include="steps/01-together-forms..steps/04-one-branch:src/counts.una" context="0" title="src/counts.una"
--- a/src/counts.una
+++ b/src/counts.una
@@ -32,3 +32 @@
-    let south_units = units_of("LAMP-01") with @inventory = shelves(south)
-    let east_units = units_of("LAMP-01") with @inventory = shelves(east)
-  @console.print("LAMP-01: {north_units} + {south_units} + {east_units} = {north_units + south_units + east_units}")
+  @console.print("LAMP-01: {north_units}")
```

```text include="steps/04-one-branch/expected/rendered.txt#L1"
[U2024] Error: `together` needs at least two `let` branches; with one, write a plain `let`
```

A `together` block has at least two branches, and only `let` branches (U2024). With one task, write a plain `let`. Written after `let`, as `let x = together` with branches, it is U0101: only `together for` gives a value.

#### The interpreter and the executable

`una run` runs the tasks one after another, in index order: the interpreter is the reference, and it stays deterministic. An executable built by `una build` runs each task on its own operating-system **thread**, a line of work the machine runs at the same time as others, with its own memory, and copies the values a task reads when it starts and its result when it ends ([chapter 13, Tools](/learn/tools/#s18-5), shows `una build`). Both give the same result.

#### What `together` leaves out

> [!NOTE]
> There are no task values, no detached tasks, no timeouts and no channels: `async` and `await` are not part of Una.

### A loop or `together for`

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| One result per element, each computed on its own | `together for` |
| A running total, or a step that reads what the previous turn left | A `for` loop with `let edit` |
| A few different pieces of work at once, each bound to a name | `together` with `let` branches |
| To stop at the first failure, in list order | Either: both stop as a sequential run would |
:::

### Check yourself: the first failure

`close_sites` closes each site at once, and a site with no count fails:

```una include="steps/05-first-failure/src/closing.una" title="steps/05-first-failure/src/closing.una"
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
```text include="steps/05-first-failure/expected/output.txt"
Err(NotCounted("south"))
```

The block fails with the failure of the lowest-indexed task that failed, `south`, as a run of the tasks one after another would. In an executable the `east` task may fail first, and the answer is the same.
:::

## 15.2 Building a list at the same time: `together for`

### Building a list at the same time: `together for`

`together for` runs one **task** per element: a piece of work the program may run alongside the others, at the same time, instead of one after another. It gives the list of what each task's body ends with. It stands where a value goes, after `let` or in an assignment:

```una include="steps/06-loop-forms/src/shelves.una#labels" title="steps/06-loop-forms/src/shelves.una"
--- A shelf label for each SKU, made at the same time: `together for` builds a list.
labels(skus: List[Text]) -> List[Text]
=
  let made = together for sku in skus
    "label {sku}"
  made
```

```text include="steps/06-loop-forms/expected/output.txt#L10"
["label DESK-02", "label LAMP-01"]
```

The results come in the order of the list, whatever order the tasks finish in. A task cannot assign a binding declared outside it, so `together for` cannot keep a running total: it only builds a list. [Chapter 15](#s15-1) covers tasks in full.

## 15.3 Common mistakes

### Counting in a shared binding inside `together` (U2023)

:::mistake
Count the closed days in an outer `let edit`:

```diff include="steps/07-end-of-day-stock-count..mistakes/1:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -70,3 +70,5 @@
 =
+  let edit closed = 0
   together for day in days
+    closed = closed + 1
     close_day(day)
```

```text include="mistakes/1/expected/rendered.txt"
[U2023] Error: `closed` is declared outside this `together` task, which captures its value and cannot change it, so it cannot be assigned here; return the new value from the task instead
    ╭─[ src/stockcount.una:73:5 ]
    │
 73 │     closed = closed + 1
    │     ───┬──
    │        ╰──── `closed` is declared outside this `together` task, which captures its value and cannot change it, so it cannot be assigned here; return the new value from the task instead
    │
    │ Note: run `una explain U2023` for an explanation
────╯
```

*Why:* each task captures the values around it and runs on its own, so an assignment to an outer binding would be a race between tasks ([What the result can depend on](#what-the-result-can-depend-on)). The mark points at the binding being assigned.

*Fix:* return what each task computes, and combine the results after the block. Here the count is `reports.len`.

See [U2023](/docs/errors/U2023/).
:::
