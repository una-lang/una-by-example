---
learn: "16"
title: Memory
editions: ["0.2"]
codes: [U2001, U2012, U2017, U2018, U2019, U2020, U3013]
time: 35
builds: An end-of-day stock count that replays each site's movements and closes every site at once
prerequisites: ["9", "10", "15"]
template: 2
nav: ["Values, not references", "edit", "take", "Call depth and memory limits", "Day-to-day: a stock count", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 16 Memory


A store's day ends with a count. Every site replays the sales and deliveries its tills recorded, rejects the movements that do not add up, and reports what is left on the shelves. That work changes a value step by step: the count of each SKU. This chapter shows what a value is in Una, and why two names never share one; how a function changes its caller's value, in plain sight at the call, and leaves it alone when it fails; how a value is given up for good; and what stops a run that grows too deep or too large.

## What you'll build

:::build
An end-of-day stock count for a store with two sites. Each site's ledger takes its movements one by one, a movement that does not add up leaves the ledger as it was, and both sites are closed at the same time, as in chapter 15:

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

- tell a copy from a shared reference, and know that no other binding sees a change you make;
- pass a value in and out of a function with an `edit` parameter, and rely on it being left unchanged when the call fails;
- state what such a function did, with `old(name)` in its `ensures` clause;
- give a value up with `take`, so that no code can use it afterwards;
- recognize U6003, the stop at the call depth or memory limit, and avoid it with loops.
:::

## Why it works this way

Most languages let two parts of a program hold the same object. A function that receives a list can change it under its caller, and a cache can change a record that a report is still reading. Reading a function then means asking who else holds what it holds, and a change made in one place can show up in another, far from the line that made it. Some languages add rules to keep this in check.

Una takes another route. Three rules do it:

:::steps
1. **Values are values.** There are no references. A `let` binding is a value, and copying it into another binding gives that binding its own value.
2. **Change is local and visible.** A binding declared `let edit` can be rebound, and a parameter declared `edit` passes a value in and out. The call says `edit` too, so a reader sees at the call which bindings it may change. A call that fails changes none of them.
3. **A value given up stays given up.** A parameter declared `take` uses its argument up, and the checker refuses every later use of the caller's binding.
:::

The price is that two parts of a program never share a changing value: one of them returns a new value, or takes it with `edit`. In return, a value cannot change behind your back, which is also why the tasks of [chapter 15](/learn/concurrency/) share nothing that changes. These rules fix what a program computes. How una lays out memory is its own choice and never changes the result; only how much memory a run may use is limited ([section 16.4](#s16-4)).

> [!KEY]
> In Una, the only bindings a call can change are the ones it names with `edit`, and only if the call returns. A failed call leaves them as they were.

## 16.1 Values, not references


### What a value is

A **value** is a piece of data: the number 4, the text `"LAMP-01"`, a list `[4, 0, 7]`, or a record such as a shelf with its SKU and its units. A **binding** is a name for a value, made with `let` ([section 2.1](/learn/numbers/#s2-1)) or `let edit` ([section 9.2](/learn/loops/#s9-2)), and a parameter is a binding too. You have used values and bindings since chapter 2. This section says what happens when one binding is made from another.

Think of a stock sheet on paper. When a clerk photocopies it and writes on the copy, the original does not change: the copy is a sheet of its own. Una's values work like the photocopy. Writing `let snapshot = current` gives `snapshot` its own copy of `current`'s value, and nothing that later happens to `current` reaches it.

Many languages work like a shared whiteboard instead. There, a name holds a **reference**, an address where the data lives, and two names can hold the same address. Two such names share the data: write through one, and the other sees the change. Una has no references, so two bindings never share a value that changes. To **mutate** a value, meaning to change it after it was made, you rebind a name that you declared editable, and only that name sees the change.

Each example of this chapter is a package, made as [chapter 2](/learn/numbers/#each-step-is-a-package) explains, and the chapter's download, `16-memory.tar.gz`, holds them all. Every package of this chapter uses edition `0.2`, the edition that brings `let edit`, loops and the parameter modes `edit` and `take`; a package of edition `0.1` has none of them ([chapter 19](/learn/editions/) covers editions).

### Why Una has no shared references

With aliases, a change in one place shows up somewhere else. A report reads a shelf's count, some other code changes the shelf, and the report now prints a number it never computed. Finding the cause means finding every name that could hold the same data. With values, the cause of every change is a line that names the binding it changes.

This module declares a shelf, takes a copy at the start of the day, changes the shelf twice, and keeps a snapshot between the changes:

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

1. **`let opening = Shelf(…)`.** A plain `let` binds a value for good. Assigning `opening` later is U2019, the code of an assignment to a binding that is not editable.
2. **`let edit current = opening`.** An editable binding, as in [section 9.2](/learn/loops/#s9-2), starts as a copy of `opening`'s value. Its type is fixed by that first value: it stays a `Shelf`.
3. **`current.units = current.units + 6`.** Assigning a field of an editable record rebinds `current` to a record with that field changed. `opening` keeps its own value, since it is another binding.
4. **`let snapshot = current`.** The snapshot is the value `current` has on this line. The next assignment to `current` does not reach it.
5. **`edit counts.set(index: 1, item: 12)`.** A list element changes through `set`, never by assignment, and the call says `edit`, as in [section 10.1](/learn/collections/#s10-1). `set` requires an index inside the list, and the verifier proves it here from the list's length.
:::

`una run .` prints:

```text include="steps/01-values/expected/output.txt"
opening 4, snapshot 10, now 7
counts [4, 12, 7]
Shelf(sku: "LAMP-01", units: 7)
```

Three numbers, three values: the opening count, 4; the snapshot, 10; and the shelf now, 7. In a language where `current`, `opening` and `snapshot` were references to one shelf, all three would print 7. The last line prints the whole record: in edition `0.2`, interpolation writes out a whole record, list or map, a record of several fields as its name and the names and values of its fields, as here.

### How to change a binding

[Section 9.2](/learn/loops/#s9-2) taught the **assignment**: the binding, then `=`, then the new value. Only an editable binding changes, and only by an assignment or by a call that says `edit`. The part on the left of `=` is a **place**: an editable binding, or a field of one, as deep as the record goes. The word matters in [section 16.2](#s16-2), where an `edit` argument must be a place too. This step shows each form:

```una include="steps/02-places/src/places.una#L1-L12" title="steps/02-places/src/places.una" caption="the kinds"
module places

--- Where a customer's orders are shipped.
kind Address
  street: Text
  city: Text

--- A customer of the store, with the loyalty points they hold.
kind Customer
  number: Text
  address: Address
  points: Int
```

```una include="steps/02-places/src/places.una#L23-L35" title="steps/02-places/src/places.una" caption="main"
pub main() -> Unit
  uses @console: Console[print]
=
  let edit points = 120
  points = points + 30
  @console.print("points: {points}")
  let edit customer = Customer(number: "C-1042", address: Address(street: "1 Elm Row", city: "Porto"), points: points)
  customer.points = customer.points + 10
  customer.address.city = "Braga"
  @console.print("customer: {customer.points} points, ships to {customer.address.city}")
  let edit shelves = [4, 0, 7]
  edit shelves.set(index: 1, item: 12)
  @console.print("shelves: {shelves}")
```

```text include="steps/02-places/expected/output.txt#L1-L3"
points: 150
customer: 160 points, ships to Braga
shelves: [4, 12, 7]
```

#### A whole binding

`points = points + 30` gives `points` a new value computed from its old one. The right side is read first, with the old value, and then the binding takes the result: 120 + 30 is 150.

#### A field of a record, at any depth

`customer.points = customer.points + 10` changes one field. `customer.address.city = "Braga"` changes a field of a field: the address inside the customer. In both, una builds a new record with that field changed and rebinds `customer` to it; every other field keeps its value. Each field in the path must be a field of a record kind, and the path must start at an editable binding.

#### An element of a list: `set`

A list has no assignable positions: `shelves[1] = 12` is not Una. The prelude function `set` of [section 10.1](/learn/collections/#s10-1) changes one element, and since it changes the list it is given, it takes the list as an `edit` parameter, which [section 16.2](#s16-2) explains. You write `edit` before the list: `edit shelves.set(index: 1, item: 12)`. Positions count from 0, so index 1 is the second element. A map changes the same way, with `edit stock.set(key: …, value: …)` or `edit stock.remove(key: …)` ([section 10.4](/learn/collections/#s10-4)), or by assigning the new map that `with` gives back.

### How values behave

#### A copy is its own value

`let snapshot = current` copies, and so does passing a value to a function, putting it in a list, or storing it in a record. After the copy, the two are separate: assigning one never changes the other, as the snapshot of [Why Una has no shared references](#why-una-has-no-shared-references) showed.

#### An editable binding keeps its type

A `let edit` binding takes its type from its first value, and every later value must have that type, as [section 9.2](/learn/loops/#an-editable-name-keeps-its-type) showed for a number. The rule holds for every place, a field included. Assign a text to `points`:

```diff include="steps/02-places..steps/03-fixed-type:src/places.una" context="0" title="src/places.una"
--- a/src/places.una
+++ b/src/places.una
@@ -27 +27 @@
-  points = points + 30
+  points = "150 points"
```

```text include="steps/03-fixed-type/expected/rendered.txt"
[U2001] Error: expected `Int`, found `Text`
    ╭─[ src/places.una:27:12 ]
    │
 27 │   points = "150 points"
    │            ──────┬─────
    │                  ╰─────── expected `Int`, found `Text`
    │
    │ Note: run `una explain U2001` for an explanation
────╯
```

The mark points at the new value: the binding is an `Int`, and the value is a `Text`. A binding that holds a refined kind, such as `Cents` of [chapter 5](/learn/contracts/#s5-3), keeps its condition only when you write the type: `let edit total: Cents = 0`, as [section 9.3](/learn/loops/#keeping-a-fact-through-the-loop-a-refined-type) did with `Units`. Without it, the binding is a plain `Int`.

#### Only an editable binding changes

Assigning a plain `let` binding, a parameter declared without `edit`, the variable of a `for` loop or, inside a lambda, a binding it captured is U2019 ([section 9.2](/learn/loops/#s9-2); [Assigning a plain `let`](/learn/loops/#assigning-a-plain-let-u2019) shows the message). A lambda keeps a copy of each value it captures when it is made ([section 10.2](/learn/collections/#s10-2)), so a later assignment outside it does not reach it either.

#### No `+=` and no `while`

There are no compound assignments such as `+=`: write `points = points + 30`. And there is no `while` loop: a `for` loop, or **recursion**, a function that calls itself, does the repeating ([section 9.1](/learn/loops/#s9-1) covers both).

#### What a copy means when the program runs

> [!NOTE] A copy is a rule about results.
> The rules of this section say what a program computes: each binding has its own value. They do not say how una lays out the memory. The specification lets una share a value's memory between bindings and update a value in place when nothing else holds it. None of this is observable: the output is always the output of the copies.

### `let` or `let edit`

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A name for a value that never changes | `let` |
| A running total, a list built step by step, or a record updated field by field | `let edit` |
| The value a binding had at some point, kept while it changes | A plain `let` copy, as `snapshot` |
| To change one element of a list | `let edit` for the list, then `edit list.set(index: …, item: …)` |
:::

Prefer `let`. A reader who sees `let` knows the value never changes; `let edit` asks them to follow every assignment.

### Check yourself: copies

`markdown` builds a price tag, keeps the original price, and then lowers the price:

```una include="steps/02-places/src/places.una#markdown" title="steps/02-places/src/places.una"
--- The price on a tag, before and after a markdown of 500 cents.
markdown() -> Text
=
  let edit price = 1990
  let tag = "LAMP-01 at {price}"
  let original = price
  price = price - 500
  "{tag}; was {original}; now {price}"
```

What does `markdown()` return? Decide what `tag` holds before you open the answer.

:::answer Show the answer
```text include="steps/02-places/expected/output.txt#L4"
LAMP-01 at 1990; was 1990; now 1490
```

`tag` was made from `price` when `price` was 1990, and a text holds its characters, not a link to `price`. `original` is a copy of 1990. Only `price` changes, to 1490.
:::

## 16.2 Passing a value in and out: `edit`


### What an `edit` parameter is

You hand a clerk your shopping list and ask them to add what is missing. They write on it and hand it back. If they cannot finish, they hand back your list exactly as you gave it. An `edit` parameter works the same way.

A **parameter** declared `edit` is passed in and out: the function receives the caller's value, works on it as on a `let edit` binding, and when it returns, the caller's binding receives the final value. The caller writes `edit` at the call too, so the change is visible where it happens. When the function fails ([chapter 7, Results and failures](/learn/failure/#s7-2)), the caller's binding keeps the value it had before the call.

### Why a function needs to change its caller's value

Without `edit`, a function that "changes" a shelf returns a new shelf, and the caller must remember to keep it. Here the caller keeps the result under a new name, and prints the old one:

```una include="steps/04-no-edit/src/reserve.una" title="steps/04-no-edit/src/reserve.una" verified="check, run"
module reserve

--- A shelf of the store: its SKU, the units on it, and the units set aside for orders.
kind Shelf
  sku: Text
  units: Int
  reserved: Int

--- The shelf with `units` more set aside for an order: a new value, which the caller must keep.
reserved(shelf: Shelf, units: Int) -> Shelf = Shelf(sku: shelf.sku, units: shelf.units, reserved: shelf.reserved + units)

pub main() -> Unit
  uses @console: Console[print]
=
  let edit lamps = Shelf(sku: "LAMP-01", units: 5, reserved: 0)
  let updated = reserved(lamps, units: 2)
  @console.print("{lamps.reserved} of {lamps.units} reserved")
```

`una run .` prints:

```text include="steps/04-no-edit/expected/output.txt"
0 of 5 reserved
```

Nothing was reserved. The reservation went into `updated`, which nothing reads, and the program printed `lamps`, which no line changed. The checker cannot know which binding the caller meant to update. And to give back a second result as well, such as a line for a report, the function would have to return a record of both, which every caller unpacks by hand.

An `edit` parameter removes both problems: the call names the binding it updates, and the function's result is free for something else.

### How to write an `edit` parameter

This step moves stock between the shelves of a SKU. Its kinds:

```una include="steps/05-edit-forms/src/transfer.una#Shelf..PickError" title="steps/05-edit-forms/src/transfer.una" caption="the kinds"
--- A shelf of the store: the SKU it holds and how many units are on it.
kind Shelf
  sku: Text
  units: Int

--- The two shelves of a SKU: the one customers see, and the one in the stockroom.
kind Spot
  front: Shelf
  back: Shelf

kind PickError = | Short(sku: Text, wanted: Int, left: Int)
```

#### The `edit` parameter and the call

:::steps
```una include="steps/05-edit-forms/src/transfer.una#receive" title="steps/05-edit-forms/src/transfer.una"
--- Adds a delivery to a shelf, and gives back how many units it held before.
receive(edit shelf: Shelf, units: Int) -> Int
  ensures shelf.units == old(shelf).units + units
=
  let before = shelf.units
  shelf.units = shelf.units + units
  before
```

1. **`edit shelf: Shelf`.** The word `edit` before the parameter's name. In the body, `shelf` is editable: `shelf.units = …` changes it.
2. **`-> Int`.** The function still has a result of its own: here, the units the shelf held before. A function that has nothing else to give back returns `Unit`.
3. **`ensures shelf.units == old(shelf).units + units`.** A promise about what the call did to `shelf`, which the next part explains.
:::

The call writes `edit` before the argument: `let before = receive(edit front, units: 4)`. The argument must be an editable binding, here a `let edit`. When the call returns, `front` holds the shelf with 4 more units, and `before` holds the result.

#### Naming the value on entry: `old`

An `ensures` clause ([section 5.2](/learn/contracts/#s5-2)) states what is true when the function returns. For a plain parameter that is simple, since the parameter never changes. An `edit` parameter has two values: the one the caller passed in, and the one the function hands back. So inside `ensures`, the parameter's name means its final value, and `old(name)` means its value on entry:

- `shelf.units` in the clause of `receive` is the units the caller gets back;
- `old(shelf).units` is the units the caller passed in;
- so `shelf.units == old(shelf).units + units` promises the caller exactly `units` more, and the verifier proves it from the body, as it proves every `ensures`.

`old` has three rules. It is allowed only in an `ensures` clause; in the body, the parameter is simply its current value, and a binding made at the start, such as `let before = shelf.units`, keeps the entry value. It applies only to an `edit` parameter, since a plain parameter has one value (on a plain parameter, U2012 says "`old` applies only to an `edit` parameter, as in `old(xs)`"). And a `requires` clause reads the values on entry already, so `old` is not allowed there. Anywhere else, `old(…)` is U2012, which [`old` outside `ensures`](#old-outside-ensures-u2012) shows.

#### The method form

A call can be written as a method on its first argument ([chapter 6](/learn/functions/#s6-1)). Then `edit` goes before the receiver: `edit front.receive(units: 1)` is the same call as `receive(edit front, units: 1)`. That is the form of `edit shelves.set(…)` in [section 16.1](#s16-1).

#### Several `edit` parameters

```una include="steps/05-edit-forms/src/transfer.una#move" title="steps/05-edit-forms/src/transfer.una"
--- Moves `units` from one shelf to another: two parameters passed in and out.
move(edit source: Shelf, edit target: Shelf, units: Int) -> Unit
  ensures source.units == old(source).units - units
  ensures target.units == old(target).units + units
=
  source.units = source.units - units
  target.units = target.units + units
```

A function may have several `edit` parameters, each passed in and out. The call writes `edit` at each: `move(edit back, target: edit front, units: 3)`. The two arguments must be different bindings.

#### A field as the argument

An `edit` argument may be a field of an editable binding: `receive(edit spot.back, units: 5)` changes the `back` field of `spot`, and leaves `front` as it was.

#### The whole run

`main` makes two shelves and calls each form in turn:

```una include="steps/05-edit-forms/src/transfer.una#L48-L61" title="steps/05-edit-forms/src/transfer.una" caption="main"
pub main() -> Unit
  uses @console: Console[print]
=
  let edit front = Shelf(sku: "LAMP-01", units: 2)
  let edit back = Shelf(sku: "LAMP-01", units: 10)
  let before = receive(edit front, units: 4)
  @console.print("front had {before}, now {front.units}")
  let earlier = edit front.receive(units: 1)
  @console.print("front had {earlier}, now {front.units}")
  move(edit back, target: edit front, units: 3)
  @console.print("front {front.units}, back {back.units}")
  let edit spot = Spot(front: front, back: back)
  let back_before = receive(edit spot.back, units: 5)
  @console.print("the stockroom had {back_before}, now {spot.back.units}")
```

```text include="steps/05-edit-forms/expected/output.txt#L1-L4"
front had 2, now 6
front had 6, now 7
front 10, back 7
the stockroom had 7, now 12
```

Follow the front shelf: it starts at 2, receives 4 (6), receives 1 (7), and gets 3 from the back (10). The back shelf starts at 10 and gives 3 (7). The `spot` record then copies both shelves, and its back receives 5 (12).

### Reserving units on a shelf

Back to the reservation of [Why a function needs to change its caller's value](#why-a-function-needs-to-change-its-callers-value), with `edit`. A reservation that asks for more units than are free fails, and the shelf must then stay as it was:

:::steps
```una include="steps/06-edit/src/reserve.una" title="steps/06-edit/src/reserve.una" verified="check, run"
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

1. **`reserve(edit shelf: Shelf, units: Int) -> Unit`.** The parameter `shelf` is passed in and out. The function returns `Unit`: what it gives back is the changed shelf.
2. **`ensures shelf.reserved == old(shelf).reserved + units`.** The verifier proves the promise on every path that returns.
3. **`fail NotEnough(…)`.** A `fail` inside an `if` without `else` ends the function there ([section 7.2](/learn/failure/#s7-2) covers `fail`).
4. **`edit lamps.reserve(units: 2)`.** The method form. Two units are free to reserve, and the call returns.
5. **`reserve(edit lamps, units: 9)` with `if error use unit`.** Nine units are more than the three that are free, so the call fails, and the clause carries on with `unit` ([chapter 7](/learn/failure/#s7-3) covers the clauses).
:::

`una run .` prints:

```text include="steps/06-edit/expected/output.txt"
2 of 5 reserved
```

### How an `edit` call behaves

#### A failed call changes nothing

Two units are reserved, not eleven. The failed call changed nothing: a call that fails leaves every `edit` argument with the value it had before the call. The function's own assignments are discarded with its failure, so a half-done update never reaches the caller. A loop whose body fails leaves the bindings it updates at their values from before the loop, for the same reason.

> [!IMPORTANT]
> Effects are not rolled back. If a function prints, sends a message or writes a file and then fails, those operations stay performed. Only the `edit` arguments go back to their old values.

#### The rules of an `edit` argument

An `edit` argument has three rules, each with its own code:

| Rule | Code |
| --- | --- |
| The call writes `edit` exactly where the parameter is declared `edit`, and nowhere else | U2020 |
| The argument is a place: an editable binding or a field of one, such as `ledger` or `spot.back` | U2020 when it is not a place; U2019 when its binding is not editable |
| No other argument of the same call uses the same binding, even another field of it | U2018 |

The third rule holds even for two different fields. Move stock between the two shelves of one `spot`:

```diff include="steps/05-edit-forms..steps/07-two-fields:src/transfer.una" context="0" title="src/transfer.una"
--- a/src/transfer.una
+++ b/src/transfer.una
@@ -59,0 +60 @@
+  move(edit spot.back, target: edit spot.front, units: 2)
```

```text include="steps/07-two-fields/expected/rendered.txt"
[U2018] Error: `spot` is passed as `edit` in this call, so the call cannot use it again
    ╭─[ src/transfer.una:60:37 ]
    │
 60 │   move(edit spot.back, target: edit spot.front, units: 2)
    │             ────┬────               ─────┬────
    │                 ╰─────────────────────────────── passed as `edit` here
    │                                          │
    │                                          ╰────── `spot` is passed as `edit` in this call, so the call cannot use it again
    │
    │ Note: run `una explain U2018` for an explanation
────╯
```

The first mark is the first `edit` argument, and the second is the other use of `spot` in the same call. Each `edit` argument is written back when the call returns, so two of them on one binding would both write it, and one change would be lost. Copy one shelf out first, or give `spot` a function of its own.

#### One call per line

A call with an `edit` argument, or a `take` argument ([section 16.3](#s16-3)), is the whole expression of its statement or `let`, as a call that can fail is ([section 7.3](/learn/failure/#s7-3)). So it cannot be nested in another call or in a text, and it cannot be wrapped in `attempt` (U3013, [Wrapping an `edit` call in `attempt`](#wrapping-an-edit-call-in-attempt-u3013)). A statement call whose result is not `Unit` binds its result with `let`, as `let before = receive(…)` does.

#### Where `edit` is allowed

- An operation of a capability and a handler ([chapter 12](/learn/capabilities/#s12-3)) cannot declare `edit` or `take` parameters (U2020).
- A function with an `edit` or `take` parameter cannot be used as a value ([section 10.2](/learn/collections/#s10-2)), for example as the function given to `map` (U2021). Wrap the call in a function with plain parameters, as `applied` does in [Reaching `apply` through a copy](#reaching-apply-through-a-copy), and pass that function instead. A lambda cannot do it: its body is not a statement, so a call with `edit` or `take` there is U3013.

### Return a new value, or `edit`

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A new value, and the caller keeps the old one | A plain parameter, and return the new value |
| To change the caller's value, with the change visible at the call | An `edit` parameter |
| To change a value and give back another result, such as a report line | An `edit` parameter, and the other result as the function's result |
| To change a value only when the whole update succeeds | An `edit` parameter and `fails`: a failure leaves the argument as it was |
:::

### Check yourself: a failed call

`pick` takes units off a shelf, and fails when the shelf holds fewer:

```una include="steps/05-edit-forms/src/transfer.una#pick..after_picks" title="steps/05-edit-forms/src/transfer.una"
--- Takes `units` off a shelf for an order. It fails when the shelf holds fewer.
pick(edit shelf: Shelf, units: Int) -> Unit
  fails PickError
=
  if units > shelf.units
    fail Short(sku: shelf.sku, wanted: units, left: shelf.units)
  shelf.units = shelf.units - units

--- What is left on a shelf of 5 rugs after the orders ask for each number of `wanted` in turn.
after_picks(wanted: List[Int]) -> Int
=
  let edit shelf = Shelf(sku: "RUG-07", units: 5)
  for units in wanted
    pick(edit shelf, units: units)
      if error use unit
  shelf.units
```

What does `after_picks([2, 4, 3])` return?

:::answer Show the answer
```text include="steps/05-edit-forms/expected/output.txt#L5"
rugs left: 0
```

The shelf starts with 5 rugs. Picking 2 leaves 3. Picking 4 fails, since 4 is more than 3, and the failed call leaves the shelf at 3: `if error use unit` carries on. Picking 3 leaves 0.
:::

## 16.3 Giving a value up: `take`


### What `take` is

At the till, a customer hands over a gift voucher. The clerk keeps it, and the customer no longer has it: they cannot hand the same voucher over again. A **`take`** parameter is that hand-over. The function receives the argument for good, and after the call the caller's binding is **taken**: no line may use it until it is given a new value.

### Why some values must not be used again

A cart that has been checked out should not take more items, or the order and the cart disagree. Here `checkout` takes a plain parameter, so the caller keeps the cart, and adds to it after the order was made:

```una include="steps/08-no-take/src/checkout.una#checkout..main" title="steps/08-no-take/src/checkout.una"
--- Turns the cart into an order. The caller keeps the cart, and can still add to it.
checkout(cart: Cart, number: Int) -> Order = Order(number: number, customer: cart.customer, lines: cart.skus.len, cents: cart.cents)

pub main() -> Unit
  uses @console: Console[print]
=
  let edit cart = Cart(customer: "C-1042", skus: [], cents: 0)
  edit cart.add(sku: "LAMP-01", cents: 1990)
  edit cart.add(sku: "DESK-02", cents: 12900)
  let order = checkout(cart, number: 1001)
  edit cart.add(sku: "RUG-07", cents: 4500)
  @console.print("order {order.number}: {order.lines} lines, {order.cents} cents")
  @console.print("the cart: {cart.skus.len} lines, {cart.cents} cents")
```

```text include="steps/08-no-take/expected/output.txt"
order 1001: 2 lines, 14890 cents
the cart: 3 lines, 19390 cents
```

The customer sees three items in the cart, and the order has two. The rug was never ordered, and nothing says so. A comment that says "do not use the cart after checkout" is easy to miss. `take` makes it a rule the checker enforces.

### How to write `take`

This step redeems gift vouchers, which can each be used once:

```una include="steps/09-take-forms/src/vouchers.una" title="steps/09-take-forms/src/vouchers.una" verified="check, run"
module vouchers

--- A gift voucher: a code and what it takes off an order, in cents.
kind Voucher
  code: Text
  cents: Int

--- Redeems a voucher. It takes the voucher, so the same voucher cannot be redeemed twice.
redeem(take voucher: Voucher) -> Int = voucher.cents

--- Redeems a voucher and says so. It takes its parameter, and passes it on with `take`.
redeem_text(take voucher: Voucher) -> Text
=
  let code = voucher.code
  let cents = redeem(take voucher)
  "{code}: {cents} off"

--- Redeems one voucher for each code: each turn makes its own voucher and takes it.
redeem_codes(codes: List[Text]) -> Int
=
  let edit total = 0
  for code in codes
    let voucher = Voucher(code: code, cents: 200)
    let cents = redeem(take voucher)
    total = total + cents
  total

pub main() -> Unit
  uses @console: Console[print]
=
  let gift = Voucher(code: "GIFT-10", cents: 1000)
  let first = redeem(take gift)
  @console.print("first: {first} off")
  let edit spare = Voucher(code: "SPRING-5", cents: 500)
  let second = redeem(take spare)
  spare = Voucher(code: "SUMMER-5", cents: 500)
  let third = redeem_text(take spare)
  @console.print("second: {second} off, then {third}")
  let codes = ["A-1", "A-2", "A-3"]
  @console.print("three codes: {redeem_codes(codes)} off")
```

```text include="steps/09-take-forms/expected/output.txt"
first: 1000 off
second: 500 off, then SUMMER-5: 500 off
three codes: 600 off
```

#### The `take` parameter and the call

`redeem(take voucher: Voucher)` declares the parameter with `take`, and the call writes `take` before the argument: `redeem(take gift)`. The argument is a binding, never a field: `redeem(take order.voucher)` is U2020.

#### Any local binding can be taken

A plain `let` (`gift`), a `let edit` (`spare`) and a parameter can each be taken. `redeem_text` takes its own parameter and passes it on to `redeem` with `take`, after reading the code it needs.

#### A new value revives a binding

`spare = Voucher(…)` gives a taken `let edit` binding a new value, and it can be used again: `redeem_text(take spare)` redeems the new voucher. A plain `let` binding cannot be assigned, so once taken, it stays taken.

#### A binding declared inside a loop

`redeem_codes` makes a new voucher at each turn of its loop, and takes it in the same turn. Each turn has its own `voucher`, so nothing is taken twice.

### Checking out a cart

Back to the cart, with `take`:

:::steps
```una include="steps/10-take/src/checkout.una" title="steps/10-take/src/checkout.una" verified="check, run"
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

1. **`add(edit cart: Cart, sku: Text, cents: Int)`.** Adding to the cart changes it, so the cart is an `edit` parameter. Its `ensures` promises one more SKU.
2. **`checkout(take cart: Cart, number: Int) -> Order`.** The cart goes in and an order comes out. `take` states that the cart is used up.
3. **`let order = checkout(take cart, number: 1001)`.** The call writes `take`, as `edit` is written for an `edit` parameter. From here on, `cart` is taken.
4. **`cart = Cart(…)`.** The customer starts a new cart: an assignment revives the binding.
:::

`una run .` prints:

```text include="steps/10-take/expected/output.txt"
order 1001: 2 lines, 14890 cents
the new cart has 0 lines
```

Adding the rug to the old cart after the checkout is now U2017, at the line that uses it. [Using a value after `take`](#using-a-value-after-take-u2017) shows the diagnostic.

### How the checker follows a taken binding

#### After an `if` or a `when`

A binding taken in one branch of an `if` or a `when` counts as taken after it, since the checker cannot know which branch ran. Redeem the gift voucher only on a large order, and print its code afterwards:

```diff include="steps/09-take-forms..steps/11-taken-branch:src/vouchers.una" context="0" title="src/vouchers.una"
--- a/src/vouchers.una
+++ b/src/vouchers.una
@@ -32,2 +32,5 @@
-  let first = redeem(take gift)
-  @console.print("first: {first} off")
+  let order_cents = 4500
+  let edit first = 0
+  if order_cents >= 3000
+    first = redeem(take gift)
+  @console.print("first: {first} off, with {gift.code}")
```

```text include="steps/11-taken-branch/expected/rendered.txt"
[U2017] Error: `gift` was passed by `take`, so it cannot be used afterwards
    ╭─[ src/vouchers.una:36:45 ]
    │
 35 │     first = redeem(take gift)
    │                         ──┬─
    │                           ╰─── passed by `take` here
 36 │   @console.print("first: {first} off, with {gift.code}")
    │                                             ──┬─
    │                                               ╰─── `gift` was passed by `take`, so it cannot be used afterwards
    │
    │ Note: run `una explain U2017` for an explanation
────╯
```

The first mark is where the binding was taken, and the second where it is used. Read `gift.code` into a binding of its own before the `if`, and print that.

#### In a loop

A binding taken in a loop body is taken in every turn after the first. So a binding taken in a loop body must get a new value before the body ends, or be declared inside it, as in `redeem_codes`.

#### What `take` means at run time

`take` also tells the backend, the part of una that runs the program, the interpreter or an executable ([section 15.3](/learn/concurrency/#s15-3)), that the value is not needed after the call, so it can reuse the value's memory. The program behaves the same either way: `take` is checked before the program runs, and leaves no trace in what it computes. A plain argument that nothing reads after the call can be given up the same way, so choose `take` for the rule it enforces, not for speed.

### Choosing between a plain parameter, `edit` and `take`

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

### Check yourself: taking in a loop

This version of `redeem_codes` makes one voucher before the loop:

```diff include="steps/09-take-forms..steps/12-taken-loop:src/vouchers.una" context="1" title="src/vouchers.una"
--- a/src/vouchers.una
+++ b/src/vouchers.una
@@ -17,8 +17,8 @@
 
---- Redeems one voucher for each code: each turn makes its own voucher and takes it.
+--- Redeems a voucher for each code.
 redeem_codes(codes: List[Text]) -> Int
 =
+  let voucher = Voucher(code: "A-1", cents: 200)
   let edit total = 0
   for code in codes
-    let voucher = Voucher(code: code, cents: 200)
     let cents = redeem(take voucher)
```

Does it check? If not, which line does `una check .` point at?

:::answer Show the answer
It does not:

```text include="steps/12-taken-loop/expected/rendered.txt"
[U2017] Error: `voucher` is taken in every iteration of this loop; give it a new value before the end of the body, or declare it inside the loop
    ╭─[ src/vouchers.una:24:29 ]
    │
 24 │     let cents = redeem(take voucher)
    │                             ───┬───
    │                                ╰───── `voucher` is taken in every iteration of this loop; give it a new value before the end of the body, or declare it inside the loop
    │
    │ Note: run `una explain U2017` for an explanation
────╯
```

The first turn takes `voucher`, and the second would use it again. The message gives both fixes: assign it a new value before the end of the body, or declare it inside the loop, as the original does.
:::

## 16.4 Limits: call depth and memory


### What the call depth and the memory budget are

When a function calls another, the first one waits until the second returns. A call that is running, or waiting for one it made, is **in progress**. Picture a stack of plates: each call puts a plate on top, and each return takes one off. The **call depth** is the height of the stack: the number of calls in progress at once. Calls of functions, lambdas, predicates and the operations of handlers all count.

**Memory** is where a running program keeps its values. A run's **memory budget** is how much memory it may hold beyond what it held when it started, measured in MiB, mebibytes, of 1,048,576 bytes each.

### Why a run has limits

A recursion that never reaches its **base case**, the case it answers without calling itself, never stops calling itself. This function counts the weeks a stock lasts, and stops only when the stock is exactly 0:

```una include="steps/13-runaway/src/restock.una" title="steps/13-runaway/src/restock.una"
module restock

--- How many weeks `stock` units last when `per_week` units sell each week. It stops only when
--- the stock is exactly 0.
weeks_left(stock: Int, per_week: Int) -> Int = if stock == 0 then 0 else 1 + weeks_left(stock - per_week, per_week)

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("12 units at 3 a week: {weeks_left(12, per_week: 3)} weeks")
  @console.print("10 units at 3 a week: {weeks_left(10, per_week: 3)} weeks")
```

With 12 units at 3 a week, the stock reaches 0. With 10 units, it goes 10, 7, 4, 1, −2, and never meets 0. `una --json run .` shows the run as one JSON document:

```text include="steps/13-runaway/expected/commands/run.txt"
$ una --json run .
{"schema":"una.run/1","tier":1,"status":"aborted","output":["12 units at 3 a week: 4 weeks"],"failure":null,"diagnostics":[{"schema":"una.diagnostic/1","code":"U6003","severity":"error","domain":"runtime","message":"this call exceeds the maximum call depth of 10000","primary":{"file":"src/restock.una","start":{"line":5,"col":78},"end":{"line":5,"col":116}},"related":[],"repairs":[],"explain":"una explain U6003"}],"trace":[{"seq":1,"instance":"host:Console","capability":"Console","op":"print","args":{"line":"\"12 units at 3 a week: 4 weeks\""},"outcome":{"kind":"ok","value":"unit"}}]}
```

The first line was printed, and then `status` is `aborted`, with U6003 at the call that went one level too deep. Without the limit, the program would use memory until the machine ran out. The limit turns that into a clear stop, at the line that caused it. The fix is the base case of [chapter 9](/learn/loops/#una-has-no-while): `if stock < per_week then 0`, with the `requires per_week >= 1` that keeps every call moving toward it.

### How the limits are set

Every run has both limits, and crossing either stops it with U6003:

| Limit | Default | Flag |
| --- | --- | --- |
| Call depth | 10,000 calls in progress | `--max-depth <n>` |
| Memory budget | 4096 MiB | `--max-memory <MiB>`, at least 1 |

The flags work on `una run`, `una test` and a built executable, for one run. `--max-depth` can go up to what a stack of 1 GiB (1,024 MiB) holds.

### A loop is not a call

A **call** is one function running another and waiting for its answer, and only calls in progress count toward the call depth. A loop's turns are not calls: the body runs again, in the same function, and nothing waits for it. So a loop does not use up the call depth, however many turns it takes, while a function that calls itself, as `weeks_of_stock` of [section 9.1](/learn/loops/#una-has-no-while) does, adds one call in progress per step. For the same reason, a value has no depth limit of its own: a loop can build a list, or a structure inside a structure, much deeper than the call depth.

This step builds 20,000 shelf labels with a `for` loop, and runs with the default depth:

```una include="steps/14-loop/src/labels.una" title="steps/14-loop/src/labels.una" verified="check, run"
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

```text include="steps/14-loop/expected/output.txt"
20000 labels, the last SKU-20000
```

### Recursion that goes too deep

The same labels built by recursion need one call in progress per label. The program still checks, since the checker does not count calls, but the run stops:

```diff include="steps/14-loop..steps/15-recursion:src/labels.una" title="src/labels.una"
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

```text include="steps/15-recursion/expected/commands/run.txt"
$ una --json run .
{"schema":"una.run/1","tier":1,"status":"aborted","output":[],"failure":null,"diagnostics":[{"schema":"una.diagnostic/1","code":"U6003","severity":"error","domain":"runtime","message":"this call exceeds the maximum call depth of 10000","primary":{"file":"src/labels.una","start":{"line":4,"col":63},"end":{"line":4,"col":80}},"related":[],"repairs":[],"explain":"una explain U6003"}],"trace":[]}
```

`status` is `aborted`, `diagnostics` holds U6003 at the call that went one level too deep, and nothing was printed. In a terminal, `una run .` shows the same diagnostic on the terminal's error output (stderr) and exits with code 1. For more, run:

```sh
una explain U6003
```

It explains both limits, and ends with a failing and a fixed example.

### How the limits behave

#### The memory budget

The memory budget is checked at each call and at each turn of a loop. A run over it stops with U6003 too, and the message names the limit in MiB: `this call exceeds the memory limit of N MiB`. Where exactly the memory runs out depends on the machine, so a test should not rely on it. The depth limit is exact.

#### Why the checker cannot see the limits

The checker cannot see either limit: how deep a recursion goes, and how much a run holds, depend on the values the program meets when it runs. So U6003 is never a diagnostic of `una check`. Under `una test`, an example whose `do` line crosses a limit fails, and its report says that the `do` line aborted.

#### In tasks

Each task of a `together` block ([chapter 15](/learn/concurrency/)) counts its call depth from the depth of the block that started it, and the memory of all tasks counts against one budget.

> [!TIP]
> Build long lists with a `for` loop, as `labels` does, and keep recursion for structures that are shallow, such as a tree of categories. A run that only needs more depth can raise `--max-depth`.

### A loop or recursion

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| One step per element of a list, or per number of a range | A `for` loop: no depth at all |
| A long list built step by step | A `for` loop with `let edit` |
| To walk a shallow structure, such as categories inside categories | Recursion |
| To repeat until something happens, with no limit known in advance | Recursion, with a base case every path reaches, and fewer steps than the call depth (10,000 by default) |
:::

### Check yourself: how deep

The recursive `labels` of [Recursion that goes too deep](#recursion-that-goes-too-deep) now builds 9,000 labels:

```una include="steps/16-depth-9000/src/labels.una#main" title="steps/16-depth-9000/src/labels.una"
pub main() -> Unit
  uses @console: Console[print]
=
  let printed = labels(9000)
  let last = printed.at(index: 8999)
    if none use "none"
  @console.print("{printed.len} labels, the last {last}")
```

With the default limit, does the run stop with U6003, or print? If it prints, what?

:::answer Show the answer
```text include="steps/16-depth-9000/expected/output.txt"
9000 labels, the last SKU-9000
```

9,000 labels need about 9,000 calls in progress, one per label, plus `main`: fewer than the 10,000 of the default limit. At 20,000, the same function stops. The limit counts calls in progress, not calls made, and a loop counts none.
:::

## 16.5 Day-to-day: an end-of-day stock count

### What the program must do

Now the program from the start of the chapter. Two sites close their day. Each has the counts it opened with and the movements its tills recorded: sales, which lower a count, and deliveries, which raise it. A movement for a SKU the site does not stock, or a sale of more units than are counted, is rejected and reported, and must leave the count as it was. The sites are independent, so they are closed at the same time.

The design follows from that. One `Ledger` per site holds the running counts, and one function applies a movement to it through an `edit` parameter. When the day is done, the ledger is closed into a `Report` with `take`, and `together for` of [section 15.2](/learn/concurrency/#s15-2) closes every site at once.

### The kinds

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

A `Movement` holds a signed change, so a sale and a delivery are one kind. `CountError` carries what a person needs to correct the count: the SKU, and for an oversold item the units sold and counted. `Report` keeps the closing counts as a map, which [section 10.4](/learn/collections/#s10-4) introduced.

### Applying one movement

`apply` takes the ledger with `edit` and fails with `CountError`. Its `ensures` promises one more applied movement, which holds only when it returns: a rejected movement is a failure, and then the ledger is left as it was.

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

### Replaying a day

`close_day` keeps the ledger and the report's lines in two `let edit` bindings, and replays the movements in order. A rejected movement becomes a line of its own: `if error use` gives the statement's value when the call fails, and `error` is the `CountError` that `reason` turns into words.

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

`close` takes the ledger. After `close(take ledger, lines: lines)`, no later line of `close_day` can apply another movement to a closed day: the checker would report U2017 ([Using a value after `take`](#using-a-value-after-take-u2017) shows it). The number of rejected movements is the number of lines minus the applied ones, since every movement gives one line.

### Why an `edit` parameter, not a new ledger

Why an `edit` parameter, and not a function that returns a new ledger? Both would work. A function `apply(ledger: Ledger, movement: Movement) -> Ledger` would need a second result for the report's line, and every call would have to rebind the ledger by hand: `ledger = apply(ledger, …)`. Forgetting the rebinding would silently drop the movement. With `edit`, the call cannot forget, the line is the result, and the `ensures` clause can compare the ledger before and after with `old`.

`close_day` itself takes a plain `Day`. It builds its own ledger from the day's opening counts, so a caller's `Day` is never changed, and two calls with the same day give the same report. That is what lets `close_all` run the days as separate tasks.

### Closing every site at once

One task per day, with `together for` as [section 15.2](/learn/concurrency/#s15-2) taught it. Each task builds its own ledger inside `close_day`, so the tasks share nothing that changes, and the reports come back in the order of `days`. This is where the rules of this chapter meet those of chapter 15: a task cannot assign a binding outside it, so a ledger that each task changes must be made inside the task.

```una include="day-to-day/src/stockcount.una#close_all" title="day-to-day/src/stockcount.una"
--- Closes every site's day at once, one task per site. The reports come back in site order.
pub close_all(days: List[Day]) -> List[Report]
=
  together for day in days
    close_day(day)
```

### The sample days

`sale` and `delivery` make movements with readable names. `north_day` and `south_day` hold the sample data, and `main` prints each report.

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

### Running it

`una run .` prints the report shown in [What you'll build](#what-youll-build). The north site rejects a sale of two desks with one counted, and the south site rejects a SKU it does not stock. Each closing map is the count after the movements that were applied, in SKU order, since a map keeps its keys in order.

Built with `una build`, the same program closes the two sites on two threads. The report is the same, line for line, because `main` prints only after `close_all` has returned every report, in site order.

### The whole program

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

## 16.6 Testing it

### Reaching `apply` through a copy

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

### What each example checks

Each example checks one fact of the chapter:

- **"a sale lowers the count of its SKU"** checks `apply` through `applied`: the count and the number of applied movements.
- **"selling more than is counted is Oversold"** expects the failure with `expect fails Oversold`. `applied` passes the failure on with `if error pass`, so the example sees it.
- **"a rejected movement leaves the counts as they were"** closes a day whose only movement fails, and checks that the closing counts are the opening counts.
- **"closing every day at once gives the reports in site order"** compares `close_all` with closing the days one after another. This is the guarantee of `together for` ([section 15.3](/learn/concurrency/#s15-3)), stated as an example.

### No fakes needed

None of the examples needs a fake service: the program has no capability but the console, and the console is used only in `main`. Every function under test takes its input as values and returns its result, which is what makes each one easy to check on its own.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L7"
example stockcount "a sale lowers the count of its SKU" ... ok
example stockcount "selling more than is counted is Oversold" ... ok
example stockcount "a rejected movement leaves the counts as they were" ... ok
example stockcount "closing every day at once gives the reports in site order" ... ok

4 examples: 4 passed, 0 failed
```

## 16.7 Common mistakes

Each mistake below is a small change to `day-to-day/src/stockcount.una`, followed by what `una check .` reports.

### Leaving out `edit` at the call (U2020)

:::mistake
Write `apply(ledger, …)` in `close_day`:

```diff include="day-to-day..mistakes/1:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -62,3 +62,3 @@
   for movement in day.movements
-    let line = apply(edit ledger, movement: movement)
+    let line = apply(ledger, movement: movement)
       if error use "rejected: {reason(error)}"
```

```text include="mistakes/1/expected/rendered.txt"
[U2020] Error: parameter `ledger` of `apply` is declared `edit`, so its argument is written `edit ledger`
    ╭─[ src/stockcount.una:63:22 ]
    │
 63 │     let line = apply(ledger, movement: movement)
    │                      ───┬──
    │                         ╰──── parameter `ledger` of `apply` is declared `edit`, so its argument is written `edit ledger`
    │
    │ Help: repair 1: write `edit ledger`; edit src/stockcount.una:63:22..63:28 to "edit ledger"
    │
    │ Note: run `una explain U2020` for an explanation
────╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

*Why:* the call must show which bindings it may change, so a reader never has to open `apply` to find out. The mark points at the argument that lacks the word.

*Fix:* write `edit ledger`. The repair carries the edit, and `una fix .` applies it.

See [U2020](/docs/errors/U2020/).
:::

### Passing a plain `let` as `edit` (U2019)

:::mistake
Declare the ledger with `let` instead of `let edit`:

```diff include="day-to-day..mistakes/2:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -59,3 +59,3 @@
 =
-  let edit ledger = Ledger(site: day.site, counts: day.opening, applied: 0)
+  let ledger = Ledger(site: day.site, counts: day.opening, applied: 0)
   let edit lines: List[Text] = []
```

```text include="mistakes/2/expected/rendered.txt"
[U2019] Error: `ledger` is not editable; declare it `let edit ledger`, or the parameter `edit ledger`
    ╭─[ src/stockcount.una:63:27 ]
    │
 63 │     let line = apply(edit ledger, movement: movement)
    │                           ───┬──
    │                              ╰──── `ledger` is not editable; declare it `let edit ledger`, or the parameter `edit ledger`
    │
    │ Note: run `una explain U2019` for an explanation
────╯
```

*Why:* an `edit` argument is assigned when the call returns, and a plain `let` binding is never assigned.

*Fix:* `let edit ledger = …`. The diagnostic points at the argument, and the fix is at the declaration.

See [U2019](/docs/errors/U2019/).
:::

### Using a value after `take` (U2017)

:::mistake
Read the ledger's counts after closing it:

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

*Why:* `take` gave the ledger to `close`, and the diagnostic shows both places: the first mark is where it was taken, and the second where it is used.

*Fix:* use what `close` returns. `report.closing` already holds the counts.

See [U2017](/docs/errors/U2017/).
:::

### Wrapping an `edit` call in `attempt` (U3013)

:::mistake
Keep the outcome of `apply` as a `Result`:

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

```text include="mistakes/4/expected/rendered.txt"
[U3013] Error: `apply` is called with `edit` or `take`, so the call must be the whole expression of a statement or `let`; `attempt` cannot wrap it, so make the call itself the whole expression of a statement or `let`, and handle a failure with `if error`
    ╭─[ src/stockcount.una:63:27 ]
    │
 63 │     let outcome = attempt apply(edit ledger, movement: movement)
    │                           ───────────────────┬──────────────────
    │                                              ╰──────────────────── `apply` is called with `edit` or `take`, so the call must be the whole expression of a statement or `let`; `attempt` cannot wrap it, so make the call itself the whole expression of a statement or `let`, and handle a failure with `if error`
    │
    │ Note: run `una explain U3013` for an explanation
────╯
```

*Why:* a call with an `edit` or `take` argument is the whole expression of its statement, so that the binding it changes is updated on that line and nowhere else. The mark covers the whole call, inside the `attempt`.

*Fix:* handle the failure with a clause under the call, as `close_day` does with `if error use`. To pass the failure on, use `if error pass`.

See [U3013](/docs/errors/U3013/).
:::

### `old` outside `ensures` (U2012)

:::mistake
Use `old(ledger)` in the body of `apply`:

```diff include="day-to-day..mistakes/5:src/stockcount.una" context="1" title="src/stockcount.una"
--- a/src/stockcount.una
+++ b/src/stockcount.una
@@ -39,3 +39,3 @@
   ledger.counts = ledger.counts.with(key: movement.sku, value: next)
-  ledger.applied = ledger.applied + 1
+  ledger.applied = old(ledger).applied + 1
   "{movement.sku} {left} -> {next}"
```

```text include="mistakes/5/expected/rendered.txt"
[U2012] Error: `old` is allowed only in `ensures` clauses
    ╭─[ src/stockcount.una:40:20 ]
    │
 40 │   ledger.applied = old(ledger).applied + 1
    │                    ─────┬─────
    │                         ╰─────── `old` is allowed only in `ensures` clauses
    │
    │ Note: run `una explain U2012` for an explanation
────╯
```

*Why:* `old` names the value on entry for the promise in the header. In the body, the parameter is simply its current value, so the mark points at `old(ledger)`.

*Fix:* write `ledger.applied + 1`. To keep the entry value for later in the body, bind it first: `let before = ledger.applied`.

See [U2012](/docs/errors/U2012/).
:::

## 16.8 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's example added, and a stub of what to write. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one line on the header line.

### Exercise 1: a recount

::::exercise
A stocktake finds 7 lamps on the shelf where the ledger says 4. Write the body of `recount`, which sets the count of a SKU to what was counted. A recount is not a movement, so `applied` does not change, and the header promises it. The start package has the stub, a function for the example, and the example:

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

### Exercise 2: a delivery note, all or nothing

::::exercise
A delivery note lists several movements, and the warehouse accepts it whole or not at all. Write the body of `apply_note`, which applies every movement of a note to the ledger and gives one line per movement, and fails when any movement fails. The start package has the stub, a function for the examples, and two examples:

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

### Exercise 3: a strict close

::::exercise
The store wants a stricter close: every movement of every site must apply, or the close fails and names the first site, in list order, that did not add up. The start package has `strict_day`, which fails at a site's first bad movement, a kind for the failure, a stub of `close_strict`, and `blamed`, which runs `close_strict` and names the site it blames, or `none` when it does not fail:

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

Two tasks fail, and the block fails with the failure of the lowest-indexed one, as a sequential run would ([section 15.3](/learn/concurrency/#s15-3)). In an executable, the tasks may finish in any order, and the answer is the same.
:::
::::

## 16.9 Recap and reference

### For agents

:::agents
`una --json check .` gives each diagnostic of this chapter with its code and exact place. For [Leaving out `edit` at the call](#leaving-out-edit-at-the-call-u2020):

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U2020","severity":"error","domain":"types","message":"parameter `ledger` of `apply` is declared `edit`, so its argument is written `edit ledger`","primary":{"file":"src/stockcount.una","start":{"line":63,"col":22},"end":{"line":63,"col":28}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"write `edit ledger`","edit":{"file":"src/stockcount.una","start":{"line":63,"col":22},"end":{"line":63,"col":28},"replacement":"edit ledger"}}],"explain":"una explain U2020"}],"fixable":1}
```

The repair carries an `edit` that `una fix .` applies, so the document reports `"fixable":1`. U2012, U2017, U2019 and U3013 carry no edit: the right change depends on intent. `una --json run .` reports U6003 with `"status":"aborted"`, as in [section 16.4](#s16-4). The compact rule: *a call that changes a binding names it with `edit`, on a line of its own; a binding given with `take` is not used again until it is assigned; `old(x)` appears only in `ensures`, on an `edit` parameter.*
:::

### Recap

:::recap
- A `let` binding is a value, and a copy is a value of its own.
- `let edit` makes a binding editable: assign it or its fields with `=`, and a list element with `edit xs.set(…)`.
- An `edit` parameter passes a value in and out. The call writes `edit`, and a failed call leaves the argument unchanged.
- `old(x)` is an `edit` parameter's value on entry, and only `ensures` may use it.
- After `take x`, `x` is not used again until it is assigned.
- A loop's turns are not calls: only calls in progress count toward the call depth.
- U6003 stops a run at the call depth or the memory budget. Build long lists with loops.
:::

### Reference

:::reference
- Construct pages: [`let edit` and `edit` parameters](/docs/language/control-flow/let-edit/), [`take`](/docs/language/control-flow/take/), [`for`](/docs/language/control-flow/for/), [`ensures`](/docs/language/functions/ensures/), [`attempt`](/docs/language/errors/attempt/), [`capability` and `op`](/docs/language/capabilities/capability/), [`handler`](/docs/language/capabilities/handler/), [`example`](/docs/language/examples/example/)
- Prelude: [`set`, `append`, `Map` and `with`](/docs/std/)
- Diagnostics: [U2012](/docs/errors/U2012/), [U2017](/docs/errors/U2017/), [U2018](/docs/errors/U2018/), [U2019](/docs/errors/U2019/), [U2020](/docs/errors/U2020/), [U2021](/docs/errors/U2021/), [U3013](/docs/errors/U3013/), and at run time [U6003](/docs/errors/U6003/) (call depth or memory)
- Command line: [`una run`](/docs/cli/run/), [`una test`](/docs/cli/test/), [`una build`](/docs/cli/build/)
- Specification: [memory model](/docs/spec/17-memory-model/), [dynamic semantics, limits](/docs/spec/11-dynamic-semantics/), [native backend](/docs/spec/16-native-backend/)
:::
