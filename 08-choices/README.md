---
learn: "8"
title: Choosing
editions: ["0.2"]
codes: [U0101, U1001, U2001, U2002, U2004, U2007, U2008, U2009, U2026, U5001]
time: 30
builds: A shipment tracker that prices parcels and follows each one from packing to delivery or return
prerequisites: ["3", "4", "5", "6", "7"]
template: 2
nav: ["Every form of if", "when in full", "Guards", "Kinds that contain themselves", "Day-to-day: shipment tracking", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 8 Choosing

## What you'll build

:::build
A shipment tracker for a small store. It prices each parcel by zone and weight, follows a shipment through the events a carrier reports, ignores a scan that arrives twice, and says whether a returned parcel is owed a refund:

```text include="day-to-day/expected/output.txt"
A-1001: postage 600
A-1001: with the courier, tracking CX-4471
A-1001: no change, still with the courier, tracking CX-4471
A-1001: delivered on day 3
A-1002: postage 1200
A-1002: returned on day 12, damaged; refund due: true
```

You will learn to:

- declare a record kind, build its values with labeled fields, and read them with a dot;
- declare a sum kind whose variants carry only the data that is true in that state;
- take a value apart with `when`, and let the checker find the arm you forgot;
- write a generic kind, and constrain a generic function with `Eq` or `Ord`;
- declare a kind that contains itself, and test a program built from kinds with examples.
:::

## 8.1 Every form of `if`

### One line, several lines, or `when`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Choose between two short values | `if c then a else b`, on one line |
| Choose among several cases, by conditions tried in order | `else if`, on one line or over several |
| Name values on the way to a branch's answer | `if` over several lines, with a block in each branch |
| Use a choice as one part of a larger expression | `(if c then a else b)`, in parentheses |
| Change an editable binding only when a condition holds | `if` without `else`, as a statement |
| Choose by the kind of value you hold, such as the zone a parcel ships to | `when`, in [chapter 4](/learn/kinds/#s4-3) |
:::

Choose the one-line form while both branches are short, and switch to several lines when a branch needs a name or the line stops reading at a glance. `una fmt .` keeps whichever form you wrote: both are canonical.

## 8.2 `when` in full

### How `when` behaves

#### The arms are tried in order

When the program runs, the arms are tried from the first to the last, and the first that matches gives the value. Over variants, at most one arm can match each value. Over literals, the same: a literal repeated in a later arm is U2008, "this literal is already matched by an earlier arm". Ranges may overlap, and then the first arm that matches wins: with `in 1..5` and then `in 3..8`, the value 4 takes the first arm. Write ranges that do not overlap, so that their order does not change the answer.

#### Every variant has an arm

The checker makes sure that every variant of the subject's kind has an arm, or that an `else` covers the ones left out. A `when` over a `Zone` with arms for `Local` and `National` only is U2007, "`when` does not match variant `Abroad` of `Zone`", and its help offers the repair: an arm for each missing variant, or an `else`. [A `when` that misses a variant](#a-when-that-misses-a-variant-u2007) shows the whole diagnostic.

This rule is what makes a sum safe to grow. Add a variant to a kind, and every `when` over it without an `else` stops checking, each one at its `when` line, until it says what the new variant means.

> [!TIP]
> Prefer an arm per variant to `else` on a sum that will grow. Keep `else` for "every other case is the same", as `refund_due` does in the day-to-day program, and for literals and ranges.

#### `else` comes last, and every arm can be reached

An arm that no value can reach is an error, U2008. Move the `else` of `aisle_name` to the top:

```diff include="steps/01-when-forms..steps/02-when-rules:src/desk.una" title="src/desk.una" context="1"
--- a/src/desk.una
+++ b/src/desk.una
@@ -31,5 +31,5 @@
   when aisle
+    else -> "aisle {aisle}"
     is 1 -> "lighting"
     is 2 -> "rugs"
-    else -> "aisle {aisle}"
 
```

```text include="steps/02-when-rules/expected/rendered.txt#L1-L12"
[U2008] Error: this arm follows the `else` arm, so no value reaches it; `else` must be the last arm
    ╭─[ src/desk.una:33:5 ]
    │
 32 │     else -> "aisle {aisle}"
    │     ──┬─
    │       ╰─── the `else` arm
 33 │     is 1 -> "lighting"
    │     ──┬─
    │       ╰─── this arm follows the `else` arm, so no value reaches it; `else` must be the last arm
    │
    │ Note: run `una explain U2008` for an explanation
────╯
```

The first mark shows the `else`, and the second an arm after it: `else` already matched every value, so `is 1` can never run. The checker reports each arm after the `else`, here two. The same code reports an arm for a variant that an earlier arm already matched, "variant `Local` is already matched by an earlier arm", an `else` after arms for every variant, "no value reaches this `else`", and a literal that an earlier arm already matched, "this literal is already matched by an earlier arm".

#### Ranges must cover every value

Over variants, the checker counts the arms. Over ranges with no `else`, it cannot: an `Int` has no end. So whether the ranges cover every value the subject can take is a **proof obligation**, a question that the verifier must answer for every possible input ([chapter 2](/learn/numbers/#s2-2) met the first ones). When some value falls between the ranges, the verifier reports U5001 with a **counterexample**: a value that no arm matches. [Ranges that leave a gap](#ranges-that-leave-a-gap-u5001) shows one, with `grams = -1`. An `else` ends the question.

#### The arms give one type

Every arm of a `when` gives a value of the same type, as both branches of an `if` do. An arm that gives a number where the others give a text is reported where it is written: in a function that returns `Text`, U2001, "`note` returns `Text`, found `Int`".

#### A bound name is new

The names an arm binds exist only in that arm. They are new names, so one cannot repeat a name already bound around the `when`, such as a parameter: binding `locker` in a function that has a parameter `locker` is U1002, "`locker` is already bound in this scope". Bind the field under another name, as `is AtLocker(locker: spot)`.

### `when`, `if` or `is`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| A different value for each variant of a sum | `when`, one arm per variant |
| The fields of a variant | `when`, with an arm that binds them |
| One question about the variant, as a `Bool` | `is`: `delivery is AtLocker` |
| A different value for some numbers or texts | `when` with literal or range arms, and `else` |
| A choice on a condition, such as `grams > 2000` | `if` ([chapter 3](/learn/text-and-conditions/#s3-4)) |
| The same answer for every other variant | `when` with `else` last, knowing that a new variant gets it too |
:::

## 8.3 What a branch proves: guards

### How `if` behaves

#### The condition is a `Bool`

The condition must be `true` or `false`. A number or a text is not a condition: `if on_hand then …` does not check, since 0 is not `false` in Una. Write the comparison you mean, `if on_hand > 0`.

#### Both branches give one type

The checker holds both branches of an `if` that gives a value to one type, the type the place of the `if` expects. A branch that returns a number where the function returns a text is reported at that branch, where the mistake is, not later where the value is used. [Branches of two types](/learn/functions/#branches-of-two-types-u2001), in Common mistakes, shows the diagnostic.

#### An `if` that gives a value has an `else`

Whichever way the condition goes, a value is needed, so an `if` that gives one always has an `else`. Leave it out of the one-line form, and the line does not parse:

```diff include="steps/03-if-forms..steps/04-no-else:src/choices.una" title="src/choices.una" context="0"
--- a/src/choices.una
+++ b/src/choices.una
@@ -4 +4 @@
-weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy" else "light"
+weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy"
```

```text include="steps/04-no-else/expected/rendered.txt#L1-L6,L8"
[U0101] Error: unexpected end of line, expected `else`
   ╭─[ src/choices.una:4:65 ]
   │
 4 │ weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy"
   │                                                                 ┬
   │                                                                 ╰── unexpected end of line, expected `else`
   │ Help: repair 1: an `if` with `then` needs `else`; to fail early, make the rest of the body its `else` branch, as in `if x < 0 then fail Broke else x`, or use the block form, whose `else` block holds the rest
```

The mark points at the end of the line, where `else` was expected. Add the `else` and its value.

#### Only the chosen branch runs

Una evaluates the condition, then only the branch it picks. The other branch is never evaluated, so it cannot divide by zero or call a function for nothing. This is what makes recursion stop: in `marked_down` ([section 6.1](/learn/functions/#s6-1)), the branch that calls the function again is not evaluated once no week is left.

#### What a branch knows from its condition

Inside a branch, the verifier knows that the condition held, or, in the `else` branch, that it did not. That knowledge can prove what would otherwise fail. `per_unit` divides by `units`, and a division by a value that is not a literal must be proven safe ([chapter 2](/learn/numbers/#s2-2)):

```una include="steps/03-if-forms/src/choices.una#per_unit" title="steps/03-if-forms/src/choices.una"
--- The price of one unit of a pack. The division is in the branch where `units > 0` holds.
per_unit(pack_cents: Int, units: Int) -> Int = if units > 0 then pack_cents / units else 0
```

```text include="steps/03-if-forms/expected/output.txt#L6"
250, 0
```

The division sits in the branch where `units > 0` holds, so `units` is never 0 there. Weaken the condition to `units >= 0`, and the proof fails:

```diff include="steps/03-if-forms..steps/05-branch-facts:src/choices.una" title="src/choices.una" context="0"
--- a/src/choices.una
+++ b/src/choices.una
@@ -33 +33 @@
-per_unit(pack_cents: Int, units: Int) -> Int = if units > 0 then pack_cents / units else 0
+per_unit(pack_cents: Int, units: Int) -> Int = if units >= 0 then pack_cents / units else 0
```

```text include="steps/05-branch-facts/expected/rendered.txt#L1-L6,L8,L12"
[U5001] Error: division obligation `units != 0` is refuted
    ╭─[ src/choices.una:33:67 ]
    │
 33 │ per_unit(pack_cents: Int, units: Int) -> Int = if units >= 0 then pack_cents / units else 0
    │                                                                   ─────────┬────────
    │                                                                            ╰────────── division obligation `units != 0` is refuted
    │ Help: repair 1: guard the division with `if units != 0`
    │ Note 2: counterexample: units = 0
```

The counterexample, `units = 0`, is a value that passes the new condition and still divides by zero. The help line proposes a guard, which is exactly what the original condition was.

### A precondition, a guard or a kind

:::decide
**Which to use:**

| The bad value… | Use |
| --- | --- |
| Is a mistake of the caller, which can always avoid it | `requires`: every caller proves it |
| Can come from a person or another system | A guard or a failure in the function that receives it ([section 7.6](/learn/failure/#s7-6)) |
| Is impossible by the type already | Nothing: a refined kind ([section 5.3](/learn/contracts/#s5-3)) carries the fact |
| Holds of every value of a kind, everywhere | A refined kind, instead of the same `requires` on many functions |
| Can only be decided by running code, such as the format of a text | `checked` with an opaque predicate ([section 5.3](/learn/contracts/#s5-3)) |
:::

A precondition moves work to the callers: each one must show the condition. That is right when the condition is the caller's to keep, as "never 0 months" is. When the value comes from outside the program, no caller can promise anything about it, and the function that receives it must check it.

### Proving a product with a guard

U5002 is not a claim that the code is wrong: it says that the proof is missing. The first repair is a guard, which gives the solver the fact it cannot derive:

:::steps
```una include="steps/06-products/src/invoice.una" title="steps/06-products/src/invoice.una" verified="check, run"
module invoice

--- An amount of money in cents. It is never negative.
kind Cents = Int where it >= 0

--- One line of an invoice.
kind Line
  sku: Text
  unit_cents: Cents
  quantity: Int in 1..99

--- Loyalty points: one for each whole 1.00 spent.
points(total: Cents) -> Int
  ensures result >= 0
  ensures result * 100 <= total
=
  total / 100

--- What one line costs. The guard handles a case that cannot happen, since both factors
--- are at least 0; the solver cannot see that for itself.
line_total(line: Line) -> Cents
=
  let total = line.unit_cents * line.quantity
  if total < 0 then 0 else total

pub main() -> Unit
  uses @console: Console[print]
=
  let desk = Line(sku: "DESK-02", unit_cents: 14900, quantity: 2)
  let total = line_total(desk)
  @console.print("{total} cents, {points(total)} points")
```

1. **`points`.** Division by the literal 100 is linear, so the verifier proves both clauses with no help. `result * 100` is allowed in a clause: one side is a literal.
2. **`let total = line.unit_cents * line.quantity`, then `if total < 0 then 0 else total`.** In the `else` branch, the verifier knows `total >= 0`, so the result is a `Cents`. The `then` branch never runs, since both factors are at least 0. The verifier does not check that claim: it accepts the guard whatever the branch returns. You check it, from the kinds of the factors, and if a kind changes, you read the guard again. The guard costs one comparison at run time.
:::

`una run .` prints:

```text include="steps/06-products/expected/output.txt"
29800 cents, 298 points
```

## 8.4 Kinds that contain themselves


### What a recursive kind is

Some data holds smaller data of the same shape. A store sells gift kits: a kit holds two products, and each of them may be a single item or another kit. A box of boxes, like a set of nesting dolls. A **recursive kind** is a kind that contains itself in one of its fields, so a value can hold another value of its own kind, which can hold another, as deep as the data goes.

### Why a kind contains itself

With records of fixed fields, every level of nesting needs a kind of its own: a kit of items, a kit of kits of items, and so on, with a limit you choose in advance. A real catalog does not stop at the depth you planned. A recursive kind describes every depth with one declaration.

### How to write a recursive kind

```una include="steps/07-bundles/src/bundles.una#Bundle" title="steps/07-bundles/src/bundles.una"
--- A product the store sells: one item, or a kit of two products, each of which may be a kit.
kind Bundle = Item(sku: Text, cents: Int) | Kit(first: Bundle, second: Bundle)
```

A kind can contain itself in two ways.

#### A variant that holds its own kind

`Bundle` is a sum whose variant `Kit` has two fields of kind `Bundle`, the kind being declared. The variant `Item` has none, and that matters: it is where a bundle stops. Every value of `Bundle` is built from items at the bottom, with kits above them.

> [!NOTE]
> A kind that holds itself directly in a field, as `Kit` does, needs edition 0.2 or later, the edition of every package in this book. In edition 0.1, a kind may contain itself only through a `List` or an `Option` field, the form that follows; `Bundle` there is U2002, "kind `Bundle` contains itself through field `first`; a kind may contain itself only through `List` or `Option`".

#### Through a list or an option

A field may hold a list of values of the kind being declared, `List[GiftSet]`, or a value that may be missing, `Option[Category]`. A **list** is a sequence of values of one type, written in brackets, such as `[bulb, bulb]` ([chapter 10](/learn/collections/#s10-1) teaches lists). An **`Option`** holds either `Some(value)` or `None`, nothing ([section 4.4](/learn/kinds/#generic-sums) introduces it). This form works in every edition, and it needs no variant that ends: the empty list `[]` and `None` are where the value stops.

```una include="steps/08-gift-sets/src/kits.una" title="steps/08-gift-sets/src/kits.una" verified="check, run"
module kits

--- A gift set of any number of products, each of which may be a set. The kind contains itself
--- through a list, and the empty list is where a set stops.
kind GiftSet
  sku: Text
  parts: List[GiftSet]

--- A product category, inside a larger one or at the top. The kind contains itself through
--- an `Option`, and `None` is where the chain stops.
kind Category
  name: Text
  parent: Option[Category]

pub main() -> Unit
  uses @console: Console[print]
=
  let bulb = GiftSet(sku: "BULB-02", parts: [])
  let lamp = GiftSet(sku: "LAMP-01", parts: [bulb, bulb])
  @console.print("{lamp.sku} holds {lamp.parts.len} parts")
  let lighting = Category(name: "Lighting", parent: None)
  let lamps = Category(name: "Lamps", parent: Some(lighting))
  @console.print("{lamps}")
```

```text include="steps/08-gift-sets/expected/output.txt"
LAMP-01 holds 2 parts
Category(name: "Lamps", parent: Some(Category(name: "Lighting", parent: None)))
```

A gift set holds any number of parts, each a gift set, and a set with no parts, `parts: []`, is a single product. A category may sit inside a larger one, and `parent: None` marks the top. `lamp.parts.len` is the number of elements of the list: 2. Use a list when a value holds any number of parts, and an `Option` when it holds at most one, as a category has at most one parent.

### A reading kit, priced

A function over a recursive kind usually calls itself: for a kit, it computes the answer for each part and combines them. A function that calls itself is **recursive**, as [chapter 6](/learn/functions/#s6-1) showed with `marked_down`.

:::steps
```una include="steps/07-bundles/src/bundles.una" title="steps/07-bundles/src/bundles.una" verified="check, run"
module bundles

--- A product the store sells: one item, or a kit of two products, each of which may be a kit.
kind Bundle = Item(sku: Text, cents: Int) | Kit(first: Bundle, second: Bundle)

--- The price of a bundle: an item's price, or the prices of a kit's two parts added up.
price(bundle: Bundle) -> Int
=
  when bundle
    is Item(cents) -> cents
    is Kit(first, second) -> price(first) + price(second)

--- How many items a bundle holds. Check yourself: what does `main` print for `office`?
items(bundle: Bundle) -> Int
=
  when bundle
    is Item -> 1
    is Kit(first, second) -> items(first) + items(second)

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Item(sku: "LAMP-01", cents: 1990)
  let bulb = Item(sku: "BULB-02", cents: 350)
  let reading = Kit(first: lamp, second: Kit(first: bulb, second: bulb))
  @console.print("reading kit: {price(reading)} cents")
  @console.print("{reading}")
  let desk = Item(sku: "DESK-02", cents: 15900)
  let office = Kit(first: desk, second: reading)
  @console.print("office kit: {items(office)} items")
```

1. **`is Item(cents) -> cents`.** The bottom: an item's price is its own.
2. **`is Kit(first, second) -> price(first) + price(second)`.** A kit's price is the price of each part, added. Each call works on a smaller bundle, so the calls end at the items.
3. **`Kit(first: lamp, second: Kit(first: bulb, second: bulb))`.** A kit of a lamp and a kit of two bulbs: two levels.
:::

`una run .` prints, among other lines:

```text include="steps/07-bundles/expected/output.txt#L1-L2"
reading kit: 2690 cents
Kit(first: Item(sku: "LAMP-01", cents: 1990), second: Kit(first: Item(sku: "BULB-02", cents: 350), second: Item(sku: "BULB-02", cents: 350)))
```

The lamp costs 1990 and each bulb 350: 1990 + 350 + 350 = 2690. The second line prints the kit as you would build it, every level inside the one above.

### How a recursive kind behaves

#### Every kind needs a value that ends

Every value of a kind is finite: it must be possible to build one without going on forever. A kind whose every variant needs another value of the same kind has no such value. Declare one:

```diff include="steps/07-bundles..steps/09-endless:src/bundles.una" title="src/bundles.una" context="0"
--- a/src/bundles.una
+++ b/src/bundles.una
@@ -4,0 +5,3 @@
+
+--- A crate that always holds another crate: no value of it can ever be built.
+kind Crate = | Holds(inner: Crate)
```

```text include="steps/09-endless/expected/rendered.txt"
[U2002] Error: kind `Crate` has no finite value: every variant contains a kind without one; add a variant without it, as `End`
   ╭─[ src/bundles.una:7:6 ]
   │
 7 │ kind Crate = | Holds(inner: Crate)
   │      ──┬──
   │        ╰──── kind `Crate` has no finite value: every variant contains a kind without one; add a variant without it, as `End`
   │
   │ Note: run `una explain U2002` for an explanation
───╯
```

A `Crate` would hold a crate, which would hold a crate, without end, so no `Crate` can ever be built. U2002 says so, and its message gives the repair: a variant that does not contain the kind, such as `End`. In `Bundle`, `Item` is that variant. In edition 0.1, the same declaration is U2002 for another reason: `Crate` contains itself directly, which that edition allows only through a `List` or an `Option`.

#### A recursive call has a limit

Each level of a bundle is one more call of `price` waiting for its parts. A run has a limit on how many calls may wait at once, and a value deep enough to exceed it stops the run with U6003. Store data such as kits nests a few levels, far below the limit. For a long sequence of the same thing, use a list ([chapter 10](/learn/collections/#s10-1)) and a loop, which do not count calls.

### A recursive kind or a list

:::decide
**Which to use:**

| Your data… | Use |
| --- | --- |
| Is many values of one kind, in order | A list: `List[Item]` |
| Holds parts that are each a whole of the same kind | A recursive kind, with a variant that ends |
| Has a fixed depth, such as an order and its lines | Records, one per level |
:::

### Check yourself: recursive kinds

`items` counts the items of a bundle:

```una include="steps/07-bundles/src/bundles.una#items" title="steps/07-bundles/src/bundles.una"
--- How many items a bundle holds. Check yourself: what does `main` print for `office`?
items(bundle: Bundle) -> Int
=
  when bundle
    is Item -> 1
    is Kit(first, second) -> items(first) + items(second)
```

`office` is `Kit(first: desk, second: reading)`, where `desk` is an item and `reading` is the reading kit of this section. What does `items(office)` give?

:::answer Show the answer
```text include="steps/07-bundles/expected/output.txt#L3"
office kit: 4 items
```

`items(office)` is `items(desk) + items(reading)`. The desk is an item, 1. The reading kit is `items(lamp)` plus the items of its inner kit of two bulbs, 1 + 2 = 3. In all, 1 + 3 = 4. The bulb is counted twice, since the kit holds two of it.
:::

## 8.5 Day-to-day: shipment tracking

### What the program must do

Now the program from the start of the chapter. The store ships parcels by post or by courier. Each parcel has a price for its zone and its weight. Carriers report events: a pickup, a delivery, a parcel that came back. The tracker must keep each shipment's status, ignore an event that does not fit, such as a pickup scan sent twice, and say whether a returned parcel is owed a refund.

The program uses every part of the chapter: records for parcels, sums for zones, carriers, reasons, statuses and events, `when` to take each one apart, and a generic `Change[T]` to compare a status before and after an event.

### The kinds

The design starts from the kinds. Everything a function does follows from them.

```una include="day-to-day/src/tracking.una#Zone..Change" title="day-to-day/src/tracking.una" caption="the kinds"
--- How far a parcel travels.
pub kind Zone = Local | National | Abroad

--- A parcel ready to ship. `order` is the number on the customer's receipt.
pub kind Parcel
  order: Text
  grams: Int
  zone: Zone

--- Who carries a parcel.
pub kind Carrier = Post | Courier

--- Why a parcel came back.
pub kind ReturnReason = Damaged | WrongItem | Refused

--- Where a shipment is. Each state carries what is known in that state, and nothing else.
pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int)

--- What a carrier or the warehouse reports about a shipment.
pub kind Event = PickedUp(carrier: Carrier, tracking: Text) | DeliveredOn(day: Int) | CameBack(reason: ReturnReason, day: Int)

--- A value before and after something happened.
pub kind Change[T]
  before: T
  after: T
```

Read them in order:

- **`Zone`, `Carrier` and `ReturnReason`** are sums without fields: fixed lists of names. `Zone` is ordered nearest first.
- **`Parcel`** is a record of three fields, one of which is a `Zone`.
- **`Status`** is the heart of the program. Each variant carries what is known in that state: nothing while packed, a carrier and a tracking number while in transit, a day once delivered, a reason and a day once returned. A delivered status without a day cannot be written.
- **`Event`** is a second sum, for what the outside world reports, and its variants mirror the transitions.
- **`Change[T]`** records a value before and after an event. `Change[Status]` lets the report tell an event that changed something from one that did not.

Every kind is `pub`, so other modules can use it ([chapter 6](/learn/functions/#s6-3) explains `pub`).

### Pricing a parcel

`postage` adds the price of the zone to the supplement for the weight. Each part is a `when`: one arm per zone, and weight bands with an `else`, as in [section 4.3](/learn/kinds/#s4-3). `postage` is public and has a doc comment; its two helpers are private.

```una include="day-to-day/src/tracking.una#postage..weight_cents" title="day-to-day/src/tracking.una"
--- Postage in cents: a price for the zone, and a supplement for the weight.
pub postage(parcel: Parcel) -> Int = zone_cents(parcel.zone) + weight_cents(parcel.grams)

zone_cents(zone: Zone) -> Int
=
  when zone
    is Local -> 300
    is National -> 450
    is Abroad -> 1200

weight_cents(grams: Int) -> Int
=
  when grams
    in 0..500 -> 0
    in 501..2000 -> 150
    else -> 400
```

`zone_cents` has no `else`, so a new zone stops the program from checking until it has a price. `weight_cents` has an `else`, since weights never run out: it is what makes the bands cover every `Int`.

### Following events

`apply` takes the status and an event, and gives the next status. One `when` over the event, and in each arm a test of the status with `is`. An event that does not fit the current status leaves it as it is, so a second pickup scan, or a return before any delivery, changes nothing. `track` wraps the two statuses in a `Change`, and `changed` compares them with the `Eq` constraint of [section 4.4](/learn/kinds/#s4-4).

```una include="day-to-day/src/tracking.una#apply..changed" title="day-to-day/src/tracking.una"
--- The status after an event. An event that does not fit the status changes nothing, such
--- as a pickup scan that a carrier sends twice.
pub apply(status: Status, event: Event) -> Status
=
  when event
    is PickedUp(carrier, tracking) -> if status is Packed then InTransit(carrier, tracking) else status
    is DeliveredOn(day) -> if status is InTransit then Delivered(day) else status
    is CameBack(reason, day) -> if status is Delivered then Returned(reason, day) else status

--- What an event does to a status: the status before it, and after it.
pub track(status: Status, event: Event) -> Change[Status] = Change(before: status, after: apply(status, event))

--- Whether something changed. Any type whose values can be compared will do.
pub changed[T: Eq](change: Change[T]) -> Bool = change.before != change.after
```

Follow one event through it. `apply(Packed, event: PickedUp(carrier: Courier, tracking: "CX-4471"))` matches the first arm, which binds `carrier` and `tracking`. The status is `Packed`, so the arm builds `InTransit(carrier, tracking)` from the two fields it bound. The same event again, on that `InTransit` status, matches the same arm, but `status is Packed` is now `false`, and the arm gives `status` back unchanged.

Why ignore an event that does not fit, rather than fail? Carriers resend scans, and a report that arrives late is still a report. The tracker keeps the status it trusts, and the `Change` shows that nothing happened. [Chapter 6, Failure](/learn/failure/), shows how a function declares that it can fail, for the cases where an event that does not fit must stop the work. `Event` and `Status` are two kinds, not one, because what a carrier reports and what the store knows are different things: a `PickedUp` event carries what the status after it will hold, and nothing about the status before it.

`InTransit(carrier, tracking)` in the first arm builds a variant from two bindings of the same names as its fields. A name equal to the field's name counts as its label, so this is `InTransit(carrier: carrier, tracking: tracking)`.

### Words for people

`describe` has one arm per status and binds the fields it prints. `carrier_name` and `reason_text` turn variants without fields into words. None of them has an `else`, so a new carrier, reason or status is reported at the `when` that must say something about it. `refund_due` is the other kind of function: one case matters, and `else` covers the rest. A parcel refused at the door is not owed a refund, since the store sent it correctly.

```una include="day-to-day/src/tracking.una#describe..refund_due" title="day-to-day/src/tracking.una"
--- A status, for a person to read.
pub describe(status: Status) -> Text
=
  when status
    is Packed -> "packed, waiting for a carrier"
    is InTransit(carrier, tracking) -> "with {carrier_name(carrier)}, tracking {tracking}"
    is Delivered(day) -> "delivered on day {day}"
    is Returned(reason, day) -> "returned on day {day}, {reason_text(reason)}"

carrier_name(carrier: Carrier) -> Text
=
  when carrier
    is Post -> "the post"
    is Courier -> "the courier"

reason_text(reason: ReturnReason) -> Text
=
  when reason
    is Damaged -> "damaged"
    is WrongItem -> "the wrong item"
    is Refused -> "refused at the door"

--- Whether the store owes the customer a refund: only for a parcel that came back by the
--- store's fault.
pub refund_due(status: Status) -> Bool
=
  when status
    is Returned(reason) -> reason != Refused
    else -> false
```

`is Returned(reason) -> reason != Refused` binds one of the two fields of `Returned` and leaves `day` out. `reason != Refused` compares two values of `ReturnReason` with `!=`, which works on any kind without functions.

### Running it

`main` prices a lamp, then sends it through a pickup, the same pickup again, and a delivery. Then it prices a vase sent abroad and reports its return. Each line comes from `report`, which says "no change" when the event did not change the status.

```una include="day-to-day/src/tracking.una#report..main" title="day-to-day/src/tracking.una"
--- One line of the tracking report.
pub report(order: Text, change: Change[Status]) -> Text = if changed(change) then "{order}: {describe(change.after)}" else "{order}: no change, still {describe(change.after)}"

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
  @console.print("{lamp.order}: postage {postage(lamp)}")
  let picked = track(Packed, event: PickedUp(carrier: Courier, tracking: "CX-4471"))
  @console.print(report(lamp.order, change: picked))
  let again = track(picked.after, event: PickedUp(carrier: Courier, tracking: "CX-4471"))
  @console.print(report(lamp.order, change: again))
  let arrived = track(again.after, event: DeliveredOn(day: 3))
  @console.print(report(lamp.order, change: arrived))
  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad)
  @console.print("{vase.order}: postage {postage(vase)}")
  let back = track(Delivered(day: 8), event: CameBack(reason: Damaged, day: 12))
  @console.print("{report(vase.order, change: back)}; refund due: {refund_due(back.after)}")
```

Each event starts from the status the event before it left: `picked.after`, then `again.after`. `una run .` prints the report shown in [What you'll build](#what-youll-build). The third line is the duplicate scan: the status stayed `InTransit`, and the report says so instead of pretending something happened. Nothing in `main` can build a delivered shipment without a day, or a shipment in transit without a tracking number, because `Status` has no such variant.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/tracking.una" title="day-to-day/src/tracking.una" caption="the whole program" verified="check, run, test"
module tracking

--- How far a parcel travels.
pub kind Zone = Local | National | Abroad

--- A parcel ready to ship. `order` is the number on the customer's receipt.
pub kind Parcel
  order: Text
  grams: Int
  zone: Zone

--- Who carries a parcel.
pub kind Carrier = Post | Courier

--- Why a parcel came back.
pub kind ReturnReason = Damaged | WrongItem | Refused

--- Where a shipment is. Each state carries what is known in that state, and nothing else.
pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int)

--- What a carrier or the warehouse reports about a shipment.
pub kind Event = PickedUp(carrier: Carrier, tracking: Text) | DeliveredOn(day: Int) | CameBack(reason: ReturnReason, day: Int)

--- A value before and after something happened.
pub kind Change[T]
  before: T
  after: T

--- Postage in cents: a price for the zone, and a supplement for the weight.
pub postage(parcel: Parcel) -> Int = zone_cents(parcel.zone) + weight_cents(parcel.grams)

zone_cents(zone: Zone) -> Int
=
  when zone
    is Local -> 300
    is National -> 450
    is Abroad -> 1200

weight_cents(grams: Int) -> Int
=
  when grams
    in 0..500 -> 0
    in 501..2000 -> 150
    else -> 400

--- The status after an event. An event that does not fit the status changes nothing, such
--- as a pickup scan that a carrier sends twice.
pub apply(status: Status, event: Event) -> Status
=
  when event
    is PickedUp(carrier, tracking) -> if status is Packed then InTransit(carrier, tracking) else status
    is DeliveredOn(day) -> if status is InTransit then Delivered(day) else status
    is CameBack(reason, day) -> if status is Delivered then Returned(reason, day) else status

--- What an event does to a status: the status before it, and after it.
pub track(status: Status, event: Event) -> Change[Status] = Change(before: status, after: apply(status, event))

--- Whether something changed. Any type whose values can be compared will do.
pub changed[T: Eq](change: Change[T]) -> Bool = change.before != change.after

--- A status, for a person to read.
pub describe(status: Status) -> Text
=
  when status
    is Packed -> "packed, waiting for a carrier"
    is InTransit(carrier, tracking) -> "with {carrier_name(carrier)}, tracking {tracking}"
    is Delivered(day) -> "delivered on day {day}"
    is Returned(reason, day) -> "returned on day {day}, {reason_text(reason)}"

carrier_name(carrier: Carrier) -> Text
=
  when carrier
    is Post -> "the post"
    is Courier -> "the courier"

reason_text(reason: ReturnReason) -> Text
=
  when reason
    is Damaged -> "damaged"
    is WrongItem -> "the wrong item"
    is Refused -> "refused at the door"

--- Whether the store owes the customer a refund: only for a parcel that came back by the
--- store's fault.
pub refund_due(status: Status) -> Bool
=
  when status
    is Returned(reason) -> reason != Refused
    else -> false

--- One line of the tracking report.
pub report(order: Text, change: Change[Status]) -> Text = if changed(change) then "{order}: {describe(change.after)}" else "{order}: no change, still {describe(change.after)}"

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
  @console.print("{lamp.order}: postage {postage(lamp)}")
  let picked = track(Packed, event: PickedUp(carrier: Courier, tracking: "CX-4471"))
  @console.print(report(lamp.order, change: picked))
  let again = track(picked.after, event: PickedUp(carrier: Courier, tracking: "CX-4471"))
  @console.print(report(lamp.order, change: again))
  let arrived = track(again.after, event: DeliveredOn(day: 3))
  @console.print(report(lamp.order, change: arrived))
  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad)
  @console.print("{vase.order}: postage {postage(vase)}")
  let back = track(Delivered(day: 8), event: CameBack(reason: Damaged, day: 12))
  @console.print("{report(vase.order, change: back)}; refund due: {refund_due(back.after)}")

example "a heavy parcel abroad pays the zone and the weight"
  do postage(Parcel(order: "A-1003", grams: 2500, zone: Abroad))
  expect result == 1600

example "a pickup moves a packed parcel into transit"
  do apply(Packed, event: PickedUp(carrier: Post, tracking: "PO-1"))
  expect result is InTransit

example "a second pickup scan changes nothing"
  do track(InTransit(carrier: Post, tracking: "PO-1"), event: PickedUp(carrier: Post, tracking: "PO-1"))
  expect not changed(result)

example "a parcel cannot come back before it was delivered"
  do apply(Packed, event: CameBack(reason: Damaged, day: 2))
  expect result is Packed

example "a refused parcel is not refunded"
  do refund_due(Returned(reason: Refused, day: 5))
  expect result == false
```

## 8.6 Testing it

### Values typed in place

Kinds make tests short. Each example builds the values it needs, in one line, and checks one fact. There is no setup and no fake object: `Packed` and `Returned(reason: Refused, day: 5)` are values you type.

```una include="day-to-day/src/tracking.una#L110-L128" title="day-to-day/src/tracking.una" caption="the examples"
example "a heavy parcel abroad pays the zone and the weight"
  do postage(Parcel(order: "A-1003", grams: 2500, zone: Abroad))
  expect result == 1600

example "a pickup moves a packed parcel into transit"
  do apply(Packed, event: PickedUp(carrier: Post, tracking: "PO-1"))
  expect result is InTransit

example "a second pickup scan changes nothing"
  do track(InTransit(carrier: Post, tracking: "PO-1"), event: PickedUp(carrier: Post, tracking: "PO-1"))
  expect not changed(result)

example "a parcel cannot come back before it was delivered"
  do apply(Packed, event: CameBack(reason: Damaged, day: 2))
  expect result is Packed

example "a refused parcel is not refunded"
  do refund_due(Returned(reason: Refused, day: 5))
  expect result == false
```

> [!TIP]
> An `example` is a test that lives next to the code ([chapter 14](/learn/testing/#s14-1)). `do` calls the code under test, `result` is what that call returned, and each `expect` line states something that must hold. `una test .` runs every example and reports each one. [Chapter 10, Testing](/learn/testing/), covers examples in full.

### Variants, and the edges the run does not reach

`expect result is InTransit` checks the variant without its fields, which is all that example is about. `expect not changed(result)` calls a function of the program on the result: any `Bool` expression works. The examples cover the edges that the run in `main` does not reach: a heavy parcel abroad, a return before a delivery, and a refused parcel. Each one names its case in plain words, so the list of examples reads as the rules of the tracker.

### One example per rule that an `else` decides

An arm per variant is checked by the checker: forget one, and the program does not check. An `else` is not: whatever it answers, it checks. So the rules that an `else` decides deserve examples of their own. "a refused parcel is not refunded" tests the one arm of `refund_due`, and "a parcel cannot come back before it was delivered" tests the `else status` of `apply`.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L8"
example tracking "a heavy parcel abroad pays the zone and the weight" ... ok
example tracking "a pickup moves a packed parcel into transit" ... ok
example tracking "a second pickup scan changes nothing" ... ok
example tracking "a parcel cannot come back before it was delivered" ... ok
example tracking "a refused parcel is not refunded" ... ok

5 examples: 5 passed, 0 failed
```

### When an example fails

When an example fails, `una test .` names it and shows the value `result` had, as [Exercise 1](#exercise-1-a-lost-parcel) shows. Because every value prints as you would build it, the failure message is a value you can paste into a new example.

## 8.7 Common mistakes

Each mistake below is a small change to `day-to-day/src/tracking.una`, followed by what `una check .` reports.

### Leaving out a field (U2009)

:::mistake
Build the lamp's `Parcel` without its zone:

```diff include="day-to-day..mistakes/1:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -96,3 +96,3 @@
 =
-  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
+  let lamp = Parcel(order: "A-1001", grams: 1200)
   @console.print("{lamp.order}: postage {postage(lamp)}")
```

```text include="mistakes/1/expected/rendered.txt#L1-L6"
[U2009] Error: `Parcel` is missing field `zone`
    ╭─[ src/tracking.una:97:14 ]
    │
 97 │   let lamp = Parcel(order: "A-1001", grams: 1200)
    │              ───┬──
    │                 ╰──── `Parcel` is missing field `zone`
```

*Why:* every field gets a value when a record is built. There are no defaults, so a parcel without a zone cannot exist. The mark points at the kind's name, `Parcel`, the constructor that lacks a field, and the message names the field.

*Fix:* give the field, `zone: National`. When you add a field to a kind, this error appears at every place that builds it, which is the list of places to update. See [U2009](/docs/errors/U2009/).
:::

### A `when` that misses a variant (U2007)

:::mistake
Remove the `Returned` arm from `describe`:

```diff include="day-to-day..mistakes/2:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -67,3 +67,2 @@
     is Delivered(day) -> "delivered on day {day}"
-    is Returned(reason, day) -> "returned on day {day}, {reason_text(reason)}"
 
```

```text include="mistakes/2/expected/rendered.txt#L1-L8"
[U2007] Error: `when` does not match variant `Returned` of `Status`
    ╭─[ src/tracking.una:64:3 ]
    │
 64 │   when status
    │   ──┬─
    │     ╰─── `when` does not match variant `Returned` of `Status`
    │
    │ Help: repair 1: add an arm for each missing variant, such as `is Returned`, or an `else` arm
```

*Why:* a `when` over a sum covers every variant. The mark is on the `when` itself, since the problem is an arm that is not there, and the message names the missing variant and its kind. This is the same error you get after adding a variant to `Status`, at every `when` that needs an arm for it.

*Fix:* add the arm. Add `else` only when every remaining variant really gets the same answer. See [U2007](/docs/errors/U2007/).
:::

### A text where a variant goes (U2001)

:::mistake
Give the zone as a text:

```diff include="day-to-day..mistakes/3:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -104,3 +104,3 @@
   @console.print(report(lamp.order, change: arrived))
-  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad)
+  let vase = Parcel(order: "A-1002", grams: 300, zone: "Abroad")
   @console.print("{vase.order}: postage {postage(vase)}")
```

```text include="mistakes/3/expected/rendered.txt#L1-L6"
[U2001] Error: field `zone` of `Parcel` must be `Zone`, found `Text`
     ╭─[ src/tracking.una:105:56 ]
     │
 105 │   let vase = Parcel(order: "A-1002", grams: 300, zone: "Abroad")
     │                                                        ────┬───
     │                                                            ╰───── field `zone` of `Parcel` must be `Zone`, found `Text`
```

*Why:* `Zone` is a kind of its own, and `"Abroad"` is a `Text`. The message names the field, the type it needs and the type it found. The checker never turns one into the other, so a typo such as `"Abraod"` cannot become a new zone.

*Fix:* the variant, `zone: Abroad`, without quotes. See [U2001](/docs/errors/U2001/).
:::

### Ranges that leave a gap (U5001)

:::mistake
Replace the `else` of `weight_cents` with a last band:

```diff include="day-to-day..mistakes/4:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -43,3 +43,3 @@
     in 501..2000 -> 150
-    else -> 400
+    in 2001..30000 -> 400
 
```

```text include="mistakes/4/expected/rendered.txt#L1,L8,L12"
[U5001] Error: exhaustiveness of this `when`, `grams in 0..500 or grams in 501..2000 or grams in 2001..30000`, is refuted
    │ Help: repair 1: add an `else` arm, or arms for the values the others miss
    │ Note 2: counterexample: grams = -1
```

*Why:* without an `else`, the verifier must prove that the ranges cover every `Int`, and the first line quotes what it tried to prove. `Note 2` is the counterexample: no arm matches `grams = -1`, nor anything above 30,000. An `Int` can be any whole number, negative ones included.

*Fix:* end with an `else` arm, as the help says. To rule out negative weights for good, give the field a refined kind, as [chapter 5](/learn/contracts/#s5-3) shows. See [U5001](/docs/errors/U5001/).
:::

### Comparing with a variant that has fields (U2009)

:::mistake
Test the status with `==` in `apply`:

```diff include="day-to-day..mistakes/5:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -51,3 +51,3 @@
     is PickedUp(carrier, tracking) -> if status is Packed then InTransit(carrier, tracking) else status
-    is DeliveredOn(day) -> if status is InTransit then Delivered(day) else status
+    is DeliveredOn(day) -> if status == InTransit then Delivered(day) else status
     is CameBack(reason, day) -> if status is Delivered then Returned(reason, day) else status
```

```text include="mistakes/5/expected/rendered.txt#L1,L8"
[U2009] Error: variant `InTransit` needs its fields: `carrier`, `tracking`
    │ Help: repair 1: write `status is InTransit`; edit src/tracking.una:52:31..52:50 to "status is InTransit"
```

*Why:* `InTransit` on its own is not a value: it needs a carrier and a tracking number. `==` compares two whole values, so it has nothing to compare `status` with. This one comes from other languages, where comparing a status with a name is the usual test.

*Fix:* `status is InTransit`, which tests the variant only. The help line holds the exact edit, and `una fix .` applies it. See [U2009](/docs/errors/U2009/).
:::

### Comparing values of a type parameter without `Eq` (U2026)

:::mistake
Leave the constraint out of `changed`:

```diff include="day-to-day..mistakes/6:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -58,3 +58,3 @@
 --- Whether something changed. Any type whose values can be compared will do.
-pub changed[T: Eq](change: Change[T]) -> Bool = change.before != change.after
+pub changed[T](change: Change[T]) -> Bool = change.before != change.after
 
```

```text include="mistakes/6/expected/rendered.txt#L1,L8"
[U2026] Error: equality on values of the type parameter `T` needs the constraint `Eq`; write `[T: Eq]`
    │ Help: repair 1: constrain `T` by `Eq`; edit src/tracking.una:59:13..59:14 to "T: Eq"
```

*Why:* a generic function knows only what its constraints say about `T`, and `!=` needs `Eq`. `changed` is `pub`, so nothing is inferred for it: its header must say what it needs.

*Fix:* `[T: Eq]`, which the help's edit writes and `una fix .` applies. See [U2026](/docs/errors/U2026/).
:::

### A field without its label (U2004)

:::mistake
Build the lamp's parcel with its order number first and unlabeled, as a function call allows:

```diff include="day-to-day..mistakes/7:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -96,3 +96,3 @@
 =
-  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
+  let lamp = Parcel("A-1001", grams: 1200, zone: National)
   @console.print("{lamp.order}: postage {postage(lamp)}")
```

```text include="mistakes/7/expected/rendered.txt#L1,L8"
[U2004] Error: `Parcel` has 3 fields, so every argument needs its field's label
    │ Help: repair 1: label it `order`; edit src/tracking.una:97:21..97:29 to "order: \"A-1001\""
```

*Why:* a call may leave the label of its first argument out, so the habit carries over. A record or variant with two or more fields labels every one, the first too, so a value reads the same wherever it is built.

*Fix:* `order: "A-1001"`, which the help's edit writes and `una fix .` applies. See [U2004](/docs/errors/U2004/).
:::

## 8.8 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added, and a stub of what to write when there is one. `una check .` or `una test .` fails there until the exercise is done. Work in small steps: make one change, run `una check .`, and read what it reports before the next change. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

### Exercise 1: a lost parcel

::::exercise
Sometimes a carrier loses a parcel. Add a variant `Lost(day: Int)` to `Status`, describe it as "lost since day N", and make it owed a refund. The start package ends with these examples, and `una check .` reports U1001 until the variant exists:

```una include="exercises/1/start/src/tracking.una#L130-L136" title="exercises/1/start/src/tracking.una"
example "a lost parcel says since when"
  do describe(Lost(day: 20))
  expect result == "lost since day 20"

example "a lost parcel is refunded"
  do refund_due(Lost(day: 20))
  expect result == true
```

:::hint
*Hint:* work in three steps. First add the variant at the end of `Status`, after a `|`, and run `una check .`: the checker shows the one `when` that needs a new arm. Then add that arm to `describe`, binding `day`. Last, run `una test .`: the other `when` over `Status` has an `else`, so it checks, and only the second example tells you that it answers wrongly.
:::

What `una check .` reports after adding only the variant:

```text include="exercises/1/variant/expected/rendered.txt#L1,L8"
[U2007] Error: `when` does not match variant `Lost` of `Status`
    │ Help: repair 1: add an arm for each missing variant, such as `is Lost`, or an `else` arm
```

With the variant and an arm in `describe`, `una check .` is clean, and `una test .` shows what the `else` of `refund_due` answers:

```text include="exercises/1/described/expected/commands/test.txt#L8-L12"
example tracking "a lost parcel is refunded" ... FAILED
  src/tracking.una:137: expect result == true
  it is false, with `result` = `false`

7 examples: 6 passed, 1 failed
```

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Add the variant, and an arm in each `when` over `Status`:

```diff include="exercises/1/start..exercises/1/answer:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -18,3 +18,3 @@
 --- Where a shipment is. Each state carries what is known in that state, and nothing else.
-pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int)
+pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int) | Lost(day: Int)
 
@@ -68,2 +68,3 @@
     is Returned(reason, day) -> "returned on day {day}, {reason_text(reason)}"
+    is Lost(day) -> "lost since day {day}"
 
@@ -88,2 +89,3 @@
     is Returned(reason) -> reason != Refused
+    is Lost -> true
     else -> false
```

The `else` of `refund_due` would have answered `false` for a lost parcel. This is the cost of an `else` on a sum that grows: the checker cannot tell you that a new variant needs a different answer.
:::
::::

### Exercise 2: express shipping

::::exercise
The store offers express shipping for 5.00 more. Add a field `express: Bool` to `Parcel`, and add 500 cents to the postage of an express parcel. The start package ends with this example, and `una check .` reports U2009 until the field exists:

```una include="exercises/2/start/src/tracking.una#L130-L132" title="exercises/2/start/src/tracking.una"
example "express adds 5.00 to the postage"
  do postage(Parcel(order: "A-1004", grams: 300, zone: Local, express: true))
  expect result == 800
```

:::hint
*Hint:* add the field as a fourth line under `kind Parcel`, then run `una check .`: every place that builds a `Parcel` is reported, since each must now say whether it is express. Give each one `express: false` or `express: true`. Then change `postage`: an `if … then … else` in parentheses can be one term of an addition; without the parentheses it is U0101.
:::

Check your answer with `una test .`, and `una run .` to see the new postage of the vase, if you send it express.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Add the field, use it in `postage`, and give it in every `Parcel`:

```diff include="exercises/2/start..exercises/2/answer:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -10,2 +10,3 @@
   zone: Zone
+  express: Bool
 
@@ -29,3 +30,3 @@
 --- Postage in cents: a price for the zone, and a supplement for the weight.
-pub postage(parcel: Parcel) -> Int = zone_cents(parcel.zone) + weight_cents(parcel.grams)
+pub postage(parcel: Parcel) -> Int = zone_cents(parcel.zone) + weight_cents(parcel.grams) + (if parcel.express then 500 else 0)
 
@@ -96,3 +97,3 @@
 =
-  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
+  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National, express: false)
   @console.print("{lamp.order}: postage {postage(lamp)}")
@@ -104,3 +105,3 @@
   @console.print(report(lamp.order, change: arrived))
-  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad)
+  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad, express: true)
   @console.print("{vase.order}: postage {postage(vase)}")
@@ -110,3 +111,3 @@
 example "a heavy parcel abroad pays the zone and the weight"
-  do postage(Parcel(order: "A-1003", grams: 2500, zone: Abroad))
+  do postage(Parcel(order: "A-1003", grams: 2500, zone: Abroad, express: false))
   expect result == 1600
```

The answer sends the vase express, so `una run .` prints `A-1002: postage 1700`.
:::
::::

### Exercise 3: the next action

::::exercise
Design a kind. For each status, the store does one thing next: wait while a parcel is packed, send the tracking number to the customer while it is in transit, ask for a review once it is delivered, refund a parcel returned damaged or wrong, and put a refused parcel back on the shelf. The start package has a placeholder kind, `Action`, a stub for `next_action`, and these examples, which report U1001 until the kind has the variants they name:

```una include="exercises/3/start/src/tracking.una#L136-L150" title="exercises/3/start/src/tracking.una"
example "a parcel in transit sends its tracking number"
  do next_action(InTransit(carrier: Post, tracking: "PO-7"))
  expect result == SendTracking(tracking: "PO-7")

example "a damaged parcel is refunded"
  do next_action(Returned(reason: Damaged, day: 4))
  expect result == Refund

example "a refused parcel goes back on the shelf"
  do next_action(Returned(reason: Refused, day: 4))
  expect result == Restock

example "a delivered parcel asks for a review"
  do next_action(Delivered(day: 3))
  expect result == AskForReview
```

:::hint
*Hint:* read the examples first: they name the variants, `SendTracking`, `Refund`, `Restock` and `AskForReview`, and the placeholder has `Wait`. Only one action carries data, so only one variant has a field. In `next_action`, write one arm per status; the `Returned` arm binds `reason` and compares it with `==`, which works on a variant without fields. A `when` inside an arm starts on its own line, below the `->`.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Declare the actions, and choose one for each status:

```diff include="exercises/3/start..exercises/3/answer:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -93,7 +93,13 @@
 
---- What the store does next about a shipment. Exercise 3: declare it as a sum kind.
-pub kind Action = | Wait
+--- What the store does next about a shipment.
+pub kind Action = Wait | SendTracking(tracking: Text) | AskForReview | Refund | Restock
 
---- The next action for a status. Exercise 3: one action for each case.
-pub next_action(status: Status) -> Action = Wait
+--- The next action for a status.
+pub next_action(status: Status) -> Action
+=
+  when status
+    is Packed -> Wait
+    is InTransit(tracking) -> SendTracking(tracking)
+    is Delivered -> AskForReview
+    is Returned(reason) -> if reason == Refused then Restock else Refund
 
```

`is InTransit(tracking)` binds one of the two fields of `InTransit` by its name, and `SendTracking(tracking)` passes it on, unlabeled since that variant has one field. The `Returned` arm chooses with an `if`, since only one reason differs.
:::
::::

## 8.9 Recap and reference

### For agents

:::agents
`una --json check .` gives every diagnostic as JSON. For [A `when` that misses a variant](#a-when-that-misses-a-variant-u2007):

```json include="mistakes/2/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U2007","severity":"error","domain":"types","message":"`when` does not match variant `Returned` of `Status`","primary":{"file":"src/tracking.una","start":{"line":64,"col":3},"end":{"line":64,"col":7}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"add an arm for each missing variant, such as `is Returned`, or an `else` arm","edit":null}],"explain":"una explain U2007"}],"fixable":0}
```

U2007 carries no `edit`, since only the author knows what a new arm should do. U2004, U2026 and the `==` form of U2009 carry exact edits, which `una fix .` applies. The compact rule: *records label every field and are nominal; a sum of one variant starts with `|`; `when` covers every variant or ends with `else`, which comes last; test a variant with `is`, not `==`; a generic function writes `[T: Eq]`, `[T: Ord]` or `[T: Integer]` for what it does with `T`; a recursive kind has a variant that ends.*
:::

### Recap

:::recap
- Declare a record for parts that are all there at once; build it with every field labeled, and read it with a dot.
- Records are nominal: the same fields do not make the same kind. An alias is only another name.
- Declare a sum for a value of several cases, each variant with only its own fields. A sum of one variant starts with `|`.
- Test a variant with `is`; `==` compares whole values, and only sums without fields have an order.
- `when` covers every variant; prefer an arm per variant to `else` on a sum that will grow, and put `else` last.
- Range and literal arms end with `else`, unless they cover every value.
- A generic function writes the weakest constraint its body needs: `Eq`, `Ord` or `Integer`.
- A recursive kind needs a variant that does not contain it.
:::

### Reference

:::reference
- Construct pages: [`kind`](/docs/language/types/kind/), [`when`](/docs/language/control-flow/when/), [constraints on generics](/docs/language/types/constraints/), [`example`](/docs/language/examples/example/)
- Prelude: [`Option`](/docs/std/)
- Commands: [`una contract`](/docs/cli/contract/), [`una fix`](/docs/cli/fix/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2002](/docs/errors/U2002/), [U2004](/docs/errors/U2004/), [U2007](/docs/errors/U2007/), [U2008](/docs/errors/U2008/), [U2009](/docs/errors/U2009/), [U2019](/docs/errors/U2019/), [U2025](/docs/errors/U2025/), [U2026](/docs/errors/U2026/), [U2027](/docs/errors/U2027/), [U5001](/docs/errors/U5001/), [U6003](/docs/errors/U6003/), [U7001](/docs/errors/U7001/)
- Specification: [types](/docs/spec/03-types/), [grammar](/docs/spec/02-grammar/), [functions and contracts](/docs/spec/04-functions-and-contracts/), [static semantics](/docs/spec/10-static-semantics/), [constraints on generics](/docs/spec/20-constraints-on-generics/), [canonical form](/docs/spec/15-canonical-form/), [verification](/docs/spec/12-verification/)
:::
