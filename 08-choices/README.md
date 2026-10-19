---
learn: "8"
title: Choosing
editions: ["0.2"]
codes: [U0101, U1001, U1002, U2002, U2007, U2008, U2009, U5001]
time: 55
builds: A shipment tracker that prices parcels, follows each one through its history of events, and works out a refund
prerequisites: ["3", "4", "5", "6", "7"]
template: 2
nav: ["Every form of if", "when in full", "What a branch proves", "Kinds that contain themselves", "Day-to-day: shipment tracking", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 8 Choosing

Most of what a program decides is a choice: which price a parcel pays, what a status means, whether a refund is owed. You have already met the two tools Una has for it, `if` in chapter 3 and `when` in chapter 4. This chapter finishes them. You learn the forms of `if` that do something only when a condition holds, every kind of arm a `when` can have and the rules the checker holds it to, what the verifier knows inside each branch, and kinds whose values contain smaller values of the same kind. You end with a tracker that follows a parcel from packing to delivery or return.

## What you'll build

:::build
A shipment tracker for a small store. It prices each parcel by zone and weight, keeps each shipment's history of events, ignores a scan that arrives twice, and works out the refund for a parcel that came back:

```text include="day-to-day/expected/output.txt"
A-1001: postage 600
A-1001: with the courier, tracking CX-4471
A-1001: no change, still with the courier, tracking CX-4471
A-1001: delivered on day 3
A-1002: postage 1200
A-1002: returned on day 12, refused at the door; refund 3900
```

You will learn to:

- write an `if` without `else`, which runs its lines only when its condition holds, and choose the right form of `if`;
- write `when` with literal and range arms, and read every rule the checker holds a `when` to;
- use what the verifier knows inside a branch to prove a division, a refined result or a product;
- declare a kind that contains itself, and write the recursive functions that walk it.
:::

## Why it works this way

In many languages, a choice is easy to get almost right. A chain of conditions forgets a case, and that case quietly takes the last branch. A `switch` misses a value, and the program does nothing for it. A division sits a few lines after the test that made it safe, and an edit moves it out of the test's reach. Each of these runs without complaint until the day the forgotten case arrives.

Una checks choices before the program runs. A `when` must say what happens for every variant of a sum, and for every number or text its arms can receive: a variant without an arm is an error, a range that leaves a gap is a proof that fails, with the value that falls through it. An arm that no value can reach is an error too. Inside each branch, the verifier knows the condition that led there, so a division, a refined result or a product is proven where it is written, and moving it out of the branch makes the proof fail at once. And a kind may contain itself only when its values can end, so every value you build is finite.

> [!KEY]
> In Una, every choice covers every case, and each branch is proven with the facts of the path that leads to it.

## 8.1 Every form of `if`

### What an `if` without `else` is

[Section 3.4](/learn/text-and-conditions/#s3-4) taught `if` as an expression, a choice between two values: on one line as `if c then a else b`, with `else if` for more cases, in parentheses inside a larger expression, and over several lines with a block in each branch. Every one of those forms gives a value, so every one has an `else`.

One form is left: an `if` that gives no value, and only does something when its condition holds. Think of a note on a packing table: "if the order is fragile, wrap each unit". When the order is not fragile, there is nothing to do, and no "otherwise" to write. Such an `if` is a **statement**: a line of a block that does something, as a call to `@console.print` does, instead of giving a value. It is the last form of `if`, and this section teaches it, then how to choose between all the forms.

### Why a program needs an `if` that gives no value

The forms of section 3.4 always produce a value, and a value must exist for both answers of the condition. Some steps have no value at all: a line to print, a failure to raise. With only those forms, a function that prints an extra note for bulk orders would have to print something in the `else` branch too, or build a text that is sometimes empty. And a function that refuses a bad quantity would have to put the rest of its body inside an `else`, one level deeper for each check.

An `if` without `else` says exactly what the rule says: when the condition holds, run these lines; otherwise, go on.

### How to write an `if` without `else`

The step of this section has one function for each use of the form, and its `main` prints what each does:

```una include="steps/01-if-forms/src/choices.una#packing_notes" title="src/choices.una"
--- The packing notes for an order: each `if` without `else` prints its line only when its
--- condition holds.
packing_notes(units: Int, fragile: Bool) -> Unit
  uses @console: Console[print]
=
  @console.print("{units} units")
  if units > 10
    @console.print("  bulk: use a pallet")
  if fragile
    @console.print("  fragile: wrap each unit")
```

The form has three parts:

1. **`if units > 10`.** The keyword `if` and the condition, alone on the line, with no `then`, as in the block form of section 3.4.
2. **The lines under it, indented two spaces.** They run, in order, only when the condition is `true`. Here one line prints a note.
3. **No `else`.** When the condition is `false`, the lines are skipped, and the function goes on with the line after them.

`packing_notes` has two such `if`s, one after the other, and each one decides on its own. `main` calls it for 4 units that are not fragile, then for 24 that are:

```text include="steps/01-if-forms/expected/output.txt#L2-L5"
4 units
24 units
  bulk: use a pallet
  fragile: wrap each unit
```

For 4 units, both conditions are `false`, and only the first line prints. For 24 fragile units, both hold, and both notes print.

#### A branch of several lines

The lines under the `if` are a block, as a branch of section 3.4 is: they may name values with `let`, and hold another `if`:

```una include="steps/01-if-forms/src/choices.una#stock_note" title="src/choices.una"
--- A stock note: a branch of several lines, with a name of its own and an `if` inside it.
stock_note(sku: Text, on_hand: Int) -> Unit
  uses @console: Console[print]
=
  if on_hand < 5
    let missing = 5 - on_hand
    @console.print("{sku}: order {missing} more")
    if on_hand == 0
      @console.print("{sku}: hide it from the shop")
  @console.print("{sku}: counted")
```

```text include="steps/01-if-forms/expected/output.txt#L6-L9"
LAMP-01: counted
RUG-07: order 5 more
RUG-07: hide it from the shop
RUG-07: counted
```

The lamp has 12 units, so the whole branch is skipped, and only "counted" prints. The rug has none: the branch names `missing`, prints the order, then its inner `if` holds too, and prints the second note. `missing` exists only inside the branch.

#### Failing when a condition holds

A branch may also end the function with `fail`, as in [section 7.2](/learn/failure/#s7-2). Several such `if`s in a row check a value one rule at a time, and the last line gives the value once every rule has passed:

```una include="steps/01-if-forms/src/choices.una#quantity" title="src/choices.una"
--- A quantity from 1 to 99. Each `if` without `else` fails when its condition holds, and the
--- last line gives the value.
quantity(units: Int) -> Int
  fails QuantityError
=
  if units < 1
    fail TooFew(units)
  if units > 99
    fail TooMany(units)
  units
```

```text include="steps/01-if-forms/expected/output.txt#L10"
12, 0
```

12 passes both checks, so `quantity(12)` gives 12. 140 is above 99, so the second `if` fails with `TooMany`, and `main` recovers with 0. Written this way, each rule is one line, and the value stays at the left margin, not inside nested `else` blocks. [Section 8.3](#s8-3) shows what the verifier knows after such a check.

### How the form behaves

#### It gives no value

An `if` without `else` is a statement, so it can stand only where a statement can: on a line of a block, before other lines or as the last one. It cannot be the value of a `let`, the body of a one-line function or an argument, since there would be no value when the condition is `false`. When it is the last line of a block, as in `packing_notes`, the block gives `Unit`, nothing useful, which is what a function that only prints returns.

#### It has no `else if`

The form has no `else` of any kind, so it has no `else if` either. A chain of `else if` always ends with `else`, and is a choice of section 3.4 that gives a value. When several conditions should each decide on their own, write several `if`s, one after the other, as `packing_notes` does.

#### An `if` with `else` is the last line, or the value of a `let`

The forms with `else` give a value, so Una wants that value used. Over several lines, such an `if` stands only as the last line of its block, whose value it then gives, or after `let`. Add an `else` to the first `if` of `packing_notes`, which has a line after it:

```diff include="steps/01-if-forms..steps/03-else-mid-block:src/choices.una" title="src/choices.una"
--- a/src/choices.una
+++ b/src/choices.una
@@ -14,6 +14,8 @@
   @console.print("{units} units")
   if units > 10
     @console.print("  bulk: use a pallet")
+  else
+    @console.print("  standard: use a box")
   if fragile
     @console.print("  fragile: wrap each unit")
 
```

```text include="steps/03-else-mid-block/expected/rendered.txt#L1-L6"
[U0101] Error: an `if` with blocks must be the last line of its block or the value of a `let`
    ╭─[ src/choices.una:15:3 ]
    │
 15 │   if units > 10
    │   ─┬
    │    ╰── an `if` with blocks must be the last line of its block or the value of a `let`
```

The marks point at the `if`. Here both branches print, so the `if` gives no useful value, but its form is the one that does. To print one note or the other and then go on, write two `if`s without `else`, one with the condition and one with its opposite, `if units <= 10`.

#### `then` belongs to the one-line form

`then` comes only in the one-line form, where the value follows it on the same line. A block after `then`, as some other languages write it, does not parse:

```diff include="steps/01-if-forms..steps/02-then-at-end:src/choices.una" title="src/choices.una"
--- a/src/choices.una
+++ b/src/choices.una
@@ -4,7 +4,12 @@
 kind QuantityError = TooFew(units: Int) | TooMany(units: Int)
 
 --- Whether a parcel counts as heavy: an `if` on one line, as section 3.4 wrote it.
-weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy" else "light"
+weight_class(grams: Int) -> Text
+=
+  if grams > 2_000 then
+    "heavy"
+  else
+    "light"
 
 --- The packing notes for an order: each `if` without `else` prints its line only when its
 --- condition holds.
```

```text include="steps/02-then-at-end/expected/rendered.txt#L1-L8"
[U0101] Error: unexpected end of line, expected an expression
   ╭─[ src/choices.una:9:24 ]
   │
 9 │   if grams > 2_000 then
   │                        ┬
   │                        ╰── unexpected end of line, expected an expression
   │
   │ Help: repair 1: write the `if` with blocks: `if` and its condition, the indented branch, `else`, then the indented branch; edit src/choices.una:9:1..13:1 to "  if grams > 2_000\n    \"heavy\"\n  else\n    \"light\"\n"
```

The marks point at the end of the line, where a value was expected after `then`. The `Help` line gives the exact edit to the block form, without `then`, and the last line of the diagnostic, which this excerpt leaves out, says that `una fix .` can apply it.

### Choosing the form of `if`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Choose between two short values | `if c then a else b`, on one line |
| Choose among several cases, by conditions tried in order | `else if`, ending with `else` |
| Name values on the way to a branch's answer | `if` over several lines, with a block in each branch |
| Use a choice as one part of a larger expression | `(if c then a else b)`, in parentheses |
| Do something only when a condition holds, such as print a note | `if` without `else` |
| Refuse a value that breaks a rule, then carry on | `if` without `else`, whose branch is `fail` |
| Choose by the variant of a sum, or by many numbers or texts | `when` ([section 8.2](#s8-2)) |
:::

Choose the one-line form while both branches are short, and switch to several lines when a branch needs a name or the line stops reading at a glance. `una fmt .` keeps whichever form you wrote: both are canonical.

### Check yourself: an `if` without `else`

`carton_labels` prints the labels of a carton:

```una include="steps/01-if-forms/src/choices.una#carton_labels" title="src/choices.una"
--- The labels on a carton. Check yourself: what does `main` print for 3 units, and for 30?
carton_labels(units: Int) -> Unit
  uses @console: Console[print]
=
  if units > 20
    @console.print("  heavy: lift with two people")
  if units > 5
    @console.print("  stack at most three high")
  if units < 10
    @console.print("  fits on a shelf")
  @console.print("  this side up")
```

`main` prints a line `carton of 3`, calls `carton_labels(3)`, then does the same for 30. What does it print?

:::answer Show the answer
```text include="steps/01-if-forms/expected/output.txt#L11-L17"
carton of 3
  fits on a shelf
  this side up
carton of 30
  heavy: lift with two people
  stack at most three high
  this side up
```

Each `if` decides on its own. For 3 units only `units < 10` holds. For 30, both `units > 20` and `units > 5` hold, so two labels print; `units < 10` does not. The last line has no `if`, so it prints every time.
:::

## 8.2 `when` in full

### What `when` adds: arms by value

[Section 4.3](/learn/kinds/#s4-3) taught `when` over a sum kind: the subject after `when`, one arm per variant, the fields an arm binds, the `else` arm, arms of several lines, and the rule that every variant needs an arm. That is the core of `when`, and most `when`s in a program are of that kind.

A `when` can also choose by a plain value: an `Int`, a `Text` or a `Bool`. Think of the aisle signs in a store. Aisle 1 is lighting, aisle 2 is rugs, and every other aisle is shown by its number. Or of the shelf a delivery goes to: one to four units on the low shelf, five to ten on the middle one, more on the floor. Each sign matches either one exact value or a range of values. This section teaches those arms, then every rule the checker and the verifier hold a `when` to.

### Why `when` chooses by value

An `else if` chain can choose by a number, as `zone_name` of section 3.4 does: `if zone == 1 then "home" else if zone == 2 then "neighbors" else "world"`. Each condition repeats `zone ==`, and nothing stops a later condition from testing another value, or a value an earlier one already took. With ten values, the chain is hard to read and easy to get wrong.

A `when` names the subject once, and each arm says only the value it matches. The checker then sees the whole choice at once. It reports an arm that repeats a value. And when there is no `else`, the verifier proves that the arms cover every value the subject can have, or shows you one they miss.

### How to write literal and range arms

The step of this section has one function for each form, and its `main` prints one line for each:

```una include="steps/10-when-values/src/aisles.una#aisle_name" title="src/aisles.una"
--- Literal arms: whole numbers, then `else` for every other value.
aisle_name(aisle: Int) -> Text
=
  when aisle
    is 1 -> "lighting"
    is 2 -> "rugs"
    else -> "aisle {aisle}"
```

#### Literal arms

A **literal** is a value written out in the code, such as `2` or `"RUG-07"`. An arm `is 2` matches the value 2, and nothing else:

- **`is 1 -> "lighting"`.** The pattern is `is` and a literal, then `->` and the arm's value, as for a variant.
- **`else -> "aisle {aisle}"`.** Every other aisle. A whole number can be any of infinitely many values, so a `when` with literal arms over an `Int` ends with an `else`.

```text include="steps/10-when-values/expected/output.txt#L1"
rugs; aisle 7
```

A text works the same way:

```una include="steps/10-when-values/src/aisles.una#family" title="src/aisles.una"
--- Literal arms over a text.
family(sku: Text) -> Text
=
  when sku
    is "LAMP-01" -> "lamps"
    is "RUG-07" -> "rugs"
    else -> "other"
```

```text include="steps/10-when-values/expected/output.txt#L2"
rugs; other
```

The literal of an arm is a plain value: a text with interpolation braces, such as `"{sku}"`, cannot be a pattern.

#### Literal arms over a `Bool`

A `Bool` has exactly two values, so arms for `true` and `false` cover it, with no `else`:

```una include="steps/10-when-values/src/aisles.una#gift_note" title="src/aisles.una"
--- Literal arms over a `Bool`: `true` and `false` are all its values, so no `else` is needed.
gift_note(gift: Bool) -> Text
=
  when gift
    is true -> "wrap it"
    is false -> "no wrapping"
```

```text include="steps/10-when-values/expected/output.txt#L3"
wrap it; no wrapping
```

For a single condition, `if gift then "wrap it" else "no wrapping"` says the same in one line, and is the usual choice. The `when` form fits when each arm needs a block of its own.

#### Range arms

`in 1..<10` matches a whole number from 1 up to 10, with 10 left out, and `in 10..49` one from 10 to 49, with both ends included. A **range** has two forms: `a..b` includes its end `b`, and `a..<b` leaves it out.

```una include="steps/10-when-values/src/aisles.una#box_size" title="src/aisles.una"
--- Range arms: `..` includes its end, `..<` leaves it out.
box_size(units: Int) -> Text
=
  when units
    in 1..<10 -> "small box"
    in 10..49 -> "large box"
    else -> "pallet"
```

```text include="steps/10-when-values/expected/output.txt#L4"
small box; large box; pallet
```

9 units fit a small box, 10 need a large one, and 50 go on a pallet.

#### Arms that cover a refined range

When the subject's type is a range, such as `Int in 0..999` of [section 5.3](/learn/contracts/#s5-3), the arms can cover every value of it, and then the `when` needs no `else`. Literal and range arms may mix:

```una include="steps/10-when-values/src/aisles.una#fill" title="src/aisles.una"
--- How full a shelf of up to 999 units is. A literal arm and two range arms cover every value
--- of the parameter's range, with no `else`.
fill(units: Int in 0..999) -> Text
=
  when units
    is 0 -> "empty"
    in 1..9 -> "almost empty"
    in 10..999 -> "stocked"
```

```text include="steps/10-when-values/expected/output.txt#L5"
empty; almost empty; stocked
```

`is 0`, `in 1..9` and `in 10..999` together match every whole number from 0 to 999, all the values `units` can have. [How `when` behaves](#how-when-behaves) shows how una knows.

#### A choice inside an arm

An arm's value may itself be an `if`, or, in an arm of several lines, another `when`:

```una include="steps/10-when-values/src/aisles.una#postage" title="src/aisles.una"
--- A `when` inside an arm, and an `if` inside another.
postage(zone: Zone, grams: Int) -> Int
=
  when zone
    is Local -> if grams > 1_000 then 400 else 300
    is National ->
      when grams
        in 0..500 -> 450
        else -> 600
    is Abroad -> 1200
```

```text include="steps/10-when-values/expected/output.txt#L7"
400; 600
```

A local parcel of 1200 grams takes the first arm, whose `if` gives 400. A national one of 700 grams takes the second arm, whose inner `when` has no range for 700 and gives its `else`, 600. An inner `when` starts on its own line, under the `->`, as any arm of several lines does.

### Shelves, boxes and rates

Here is the whole step, with each form in a function, and a `main` that prints one line for each:

:::steps
```una include="steps/10-when-values/src/aisles.una" title="src/aisles.una" verified="check, run"
module aisles

--- How far a parcel travels.
kind Zone = Local | National | Abroad

--- Where a customer collects a parcel.
kind Delivery = AtDoor | AtStore(store: Text)

--- Literal arms: whole numbers, then `else` for every other value.
aisle_name(aisle: Int) -> Text
=
  when aisle
    is 1 -> "lighting"
    is 2 -> "rugs"
    else -> "aisle {aisle}"

--- Literal arms over a text.
family(sku: Text) -> Text
=
  when sku
    is "LAMP-01" -> "lamps"
    is "RUG-07" -> "rugs"
    else -> "other"

--- Literal arms over a `Bool`: `true` and `false` are all its values, so no `else` is needed.
gift_note(gift: Bool) -> Text
=
  when gift
    is true -> "wrap it"
    is false -> "no wrapping"

--- Range arms: `..` includes its end, `..<` leaves it out.
box_size(units: Int) -> Text
=
  when units
    in 1..<10 -> "small box"
    in 10..49 -> "large box"
    else -> "pallet"

--- How full a shelf of up to 999 units is. A literal arm and two range arms cover every value
--- of the parameter's range, with no `else`.
fill(units: Int in 0..999) -> Text
=
  when units
    is 0 -> "empty"
    in 1..9 -> "almost empty"
    in 10..999 -> "stocked"

--- The arms are tried in order: 150 units are in both ranges, and the first arm wins.
rate(units: Int) -> Text
=
  when units
    in 100..999 -> "pallet rate"
    in 10..999 -> "case rate"
    else -> "unit rate"

--- A `when` inside an arm, and an `if` inside another.
postage(zone: Zone, grams: Int) -> Int
=
  when zone
    is Local -> if grams > 1_000 then 400 else 300
    is National ->
      when grams
        in 0..500 -> 450
        else -> 600
    is Abroad -> 1200

--- Where to collect a parcel, seen from the store `store`. The arm binds the field `store`
--- under another name, `other`, since `store` is already the parameter's name.
pickup(delivery: Delivery, store: Text) -> Text
=
  when delivery
    is AtDoor -> "at the door"
    is AtStore(store: other) -> if other == store then "here" else "at {other}"

--- The shelf for a number of units. Check yourself: what does `main` print for 0, 5 and 12?
shelf(units: Int) -> Text
=
  when units
    in 1..4 -> "low shelf"
    in 5..10 -> "middle shelf"
    else -> "floor"

--- Prints one line for each function.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{aisle_name(2)}; {aisle_name(7)}")
  let rug = family("RUG-07")
  let mug = family("MUG-03")
  @console.print("{rug}; {mug}")
  @console.print("{gift_note(true)}; {gift_note(false)}")
  @console.print("{box_size(9)}; {box_size(10)}; {box_size(50)}")
  @console.print("{fill(0)}; {fill(7)}; {fill(450)}")
  @console.print("{rate(150)}; {rate(50)}; {rate(5)}")
  @console.print("{postage(Local, grams: 1_200)}; {postage(National, grams: 700)}")
  let home = "Harbour Road"
  let here = pickup(AtStore(store: home), store: home)
  let there = pickup(AtStore(store: "Mill Lane"), store: home)
  @console.print("{here}; {there}")
  @console.print("{shelf(0)}; {shelf(5)}; {shelf(12)}")
```

1. **`aisle_name` and `family`.** Literal arms over an `Int` and a `Text`, each ending with `else`.
2. **`gift_note`.** Literal arms over a `Bool`, with no `else`.
3. **`box_size`.** Range arms, then `else` for the values they leave out.
4. **`fill`.** A literal arm and two range arms that cover the parameter's whole range.
5. **`rate`.** Two ranges that overlap. [How `when` behaves](#how-when-behaves) explains which one wins.
6. **`postage`.** An `if` in one arm, and a `when` in another.
7. **`pickup`.** A field bound under another name, `store: other`, as in section 4.3, since the parameter is already called `store`.
8. **`let rug = family("RUG-07")`.** A text literal cannot stand inside the braces of an interpolation, so `main` names each result first, as [A text inside an interpolation](/learn/text-and-conditions/#a-text-inside-an-interpolation-u0006) showed.
:::

`una run .` prints:

```text include="steps/10-when-values/expected/output.txt#L1-L8"
rugs; aisle 7
rugs; other
wrap it; no wrapping
small box; large box; pallet
empty; almost empty; stocked
pallet rate; case rate; unit rate
400; 600
here; at Mill Lane
```

### How `when` behaves

#### The arms are tried in order

When the program runs, the arms are tried from the first to the last, and the first that matches gives the value. Over variants and literals, a value can match only one arm, since a repeated one is an error. Ranges may overlap, and then the order decides:

```una include="steps/10-when-values/src/aisles.una#rate" title="src/aisles.una"
--- The arms are tried in order: 150 units are in both ranges, and the first arm wins.
rate(units: Int) -> Text
=
  when units
    in 100..999 -> "pallet rate"
    in 10..999 -> "case rate"
    else -> "unit rate"
```

```text include="steps/10-when-values/expected/output.txt#L6"
pallet rate; case rate; unit rate
```

150 is in both `100..999` and `10..999`, and the first arm wins. Overlapping ranges are legal, but a reader must read them in order to know the answer. Prefer ranges that do not overlap, such as `in 10..99` for the second arm, so that each arm can be read alone.

#### Literals and ranges must cover every value

Over variants, the checker counts the arms, as section 4.3 showed. Over literals and ranges with no `else`, counting is not enough: an `Int` has no end. So whether the arms cover every value is a proof obligation, of a kind that [section 5.4](/learn/contracts/#s5-4) left for this section: `exhaustive`. Its goal is that the subject matches one of the arms, and the verifier proves it with the facts it has, among them the subject's type. `una obligations .` lists one for each `when` of the step that has literal or range arms and no `else`:

```text include="steps/10-when-values/expected/commands/obligations.txt#L1-L3"
$ una obligations .
proven   ob-31a6bafaaaa6 exhaustive    src/aisles.una:28:3 gift == true or gift == false
proven   ob-79340fc876dd exhaustive    src/aisles.una:44:3 units == 0 or units in 1..9 or units in 10..999
```

The goal of each is the arms joined by `or`. For `gift_note`, `gift == true or gift == false` holds for every `Bool`. For `fill`, `units == 0 or units in 1..9 or units in 10..999` holds because the type of `units` says that it is between 0 and 999. Both are `proven`, so they cost nothing at run time. The other lines of the listing are the refinements of the three calls of `fill` in `main`, one per argument.

When the arms leave a gap, the obligation is refuted. Replace the `else` of `box_size` with a last range:

```diff include="steps/10-when-values..steps/11-range-gap:src/aisles.una" title="src/aisles.una" context="1"
--- a/src/aisles.una
+++ b/src/aisles.una
@@ -37,3 +37,3 @@
     in 10..49 -> "large box"
-    else -> "pallet"
+    in 50..1000 -> "pallet"
 
```

```text include="steps/11-range-gap/expected/rendered.txt#L1-L6,L8,L12"
[U5001] Error: exhaustiveness of this `when`, `units in 1..<10 or units in 10..49 or units in 50..1000`, is refuted
    ╭─[ src/aisles.una:35:3 ]
    │
 35 │   when units
    │   ──┬─
    │     ╰─── exhaustiveness of this `when`, `units in 1..<10 or units in 10..49 or units in 50..1000`, is refuted
    │ Help: repair 1: add an `else` arm, or arms for the values the others miss
    │ Note 2: counterexample: units = 1001
```

The first line quotes what the verifier tried to prove: that `units` is in one of the three ranges. The marks point at the `when`. `Note 2` is the counterexample, a value that no arm matches: 1001, just past the last range. 0 and every negative number fall through too. The `Help` gives the two repairs: an `else`, or arms for the missing values. An `else` ends the question: a `when` with `else` has no `exhaustive` obligation at all.

#### `else` comes last

An `else` matches every value, so an arm after it can never run. Move the `else` of `aisle_name` to the top:

```diff include="steps/10-when-values..steps/12-else-first:src/aisles.una" title="src/aisles.una" context="1"
--- a/src/aisles.una
+++ b/src/aisles.una
@@ -12,5 +12,5 @@
   when aisle
+    else -> "aisle {aisle}"
     is 1 -> "lighting"
     is 2 -> "rugs"
-    else -> "aisle {aisle}"
 
```

```text include="steps/12-else-first/expected/rendered.txt#L1-L12"
[U2008] Error: this arm follows the `else` arm, so no value reaches it; `else` must be the last arm
    ╭─[ src/aisles.una:14:5 ]
    │
 13 │     else -> "aisle {aisle}"
    │     ──┬─
    │       ╰─── the `else` arm
 14 │     is 1 -> "lighting"
    │     ──┬─
    │       ╰─── this arm follows the `else` arm, so no value reaches it; `else` must be the last arm
    │
    │ Note: run `una explain U2008` for an explanation
────╯
```

The first mark shows the `else`, and the second an arm after it. The checker reports each arm that follows the `else`, here two, each as U2008.

#### Every arm can be reached

The same code, U2008, reports every other arm that no value can reach. This version of the step repeats a literal in `family`, repeats a variant in `postage`, and ends `postage` with an `else` after arms for every zone:

```text include="steps/13-repeated-arms/expected/diagnostics.txt"
error U2008 at src/aisles.una:23:5: this literal is already matched by an earlier arm
error U2008 at src/aisles.una:68:5: variant `Local` is already matched by an earlier arm
error U2008 at src/aisles.una:69:5: no value reaches this `else`: the arms above match every variant of `Zone`
```

Each message names the problem: "this literal is already matched by an earlier arm", "variant `Local` is already matched by an earlier arm", and "no value reaches this `else`: the arms above match every variant of `Zone`". Each one is a sign of a mistake in the choice, such as a copied arm whose value was never changed, so una refuses it instead of ignoring it.

#### Every arm gives the same type

All the arms of one `when` give values of one type, as both branches of an `if` do. An arm that gives a number where the others give a text is reported at that arm, U2001, as section 4.3 showed.

#### A pattern holds no condition

A pattern says which variant or which value an arm matches, and nothing more: an arm cannot add a condition of its own. Try to price heavy local parcels in an arm of their own:

```diff include="steps/10-when-values..steps/14-condition-in-pattern:src/aisles.una" title="src/aisles.una" context="1"
--- a/src/aisles.una
+++ b/src/aisles.una
@@ -60,3 +60,4 @@
   when zone
-    is Local -> if grams > 1_000 then 400 else 300
+    is Local if grams > 1_000 -> 400
+    is Local -> 300
     is National ->
```

```text include="steps/14-condition-in-pattern/expected/rendered.txt#L1-L6"
[U0101] Error: unexpected keyword `if`, expected `->`
    ╭─[ src/aisles.una:61:14 ]
    │
 61 │     is Local if grams > 1_000 -> 400
    │              ─┬
    │               ╰── unexpected keyword `if`, expected `->`
```

After the pattern `is Local`, the parser expected `->`. Put the condition inside the arm, as `postage` does: `is Local -> if grams > 1_000 then 400 else 300`. A pattern also matches one level only: `is AtStore(store: other)` binds a field, and cannot say what the field must hold. Test the field in the arm's value instead.

#### A bound name is new

The names an arm binds exist only in that arm, and they are new names: an arm cannot bind a name that is already bound around the `when`, such as a parameter. Bind the field of `pickup` under its own name, `store`, which the parameter already has:

```diff include="steps/10-when-values..steps/15-bound-name:src/aisles.una" title="src/aisles.una" context="0"
--- a/src/aisles.una
+++ b/src/aisles.una
@@ -74 +74 @@
-    is AtStore(store: other) -> if other == store then "here" else "at {other}"
+    is AtStore(store) -> if store == store then "here" else "at {store}"
```

```text include="steps/15-bound-name/expected/rendered.txt#L1-L9"
[U1002] Error: `store` is already bound in this scope; a local cannot rebind another
    ╭─[ src/aisles.una:74:16 ]
    │
 70 │ pickup(delivery: Delivery, store: Text) -> Text
    │                            ──┬──
    │                              ╰──── first defined here
    │
 74 │     is AtStore(store) -> if store == store then "here" else "at {store}"
    │                ──┬──
```

The first mark shows the parameter, "first defined here", and the second the field bound again. Una refuses it, since `store == store` would no longer say which store is which. Bind the field under another name, `is AtStore(store: other)`.

### `when`, `if` or `is`

Section 4.3 compared the three for sums. With values in the picture, the choice is:

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| A different value for each variant of a sum | `when`, one arm per variant, no `else` |
| One question about the variant, as a `Bool` | `is`: `delivery is AtStore` |
| A value for some exact numbers or texts | `when` with literal arms, and `else` |
| A value for bands of numbers | `when` with range arms that do not overlap, and `else` unless they cover the type |
| A choice by a condition that compares two values, such as `other == store` | `if` |
| A condition on top of a variant | `when`, with an `if` inside the arm |
:::

A `when` over a sum without `else` is the strongest of these: add a variant, and the checker points at every `when` that must say what it means. A `when` over numbers with ranges is the clearest way to write bands, since the verifier proves they leave no gap.

### Check yourself: `when` by value

The step ends with a function that chooses a shelf by how many units arrive:

```una include="steps/10-when-values/src/aisles.una#shelf" title="src/aisles.una"
--- The shelf for a number of units. Check yourself: what does `main` print for 0, 5 and 12?
shelf(units: Int) -> Text
=
  when units
    in 1..4 -> "low shelf"
    in 5..10 -> "middle shelf"
    else -> "floor"
```

`main` prints `shelf(0)`, `shelf(5)` and `shelf(12)` on one line. What does it print? And what would `una check .` report without the `else`?

:::answer Show the answer
```text include="steps/10-when-values/expected/output.txt#L9"
floor; middle shelf; floor
```

5 is not in `1..4`, since 4 is that range's end. It is in `5..10`, so it goes on the middle shelf. 12 is above 10, so it falls to `else`. 0 is in neither range either, so it falls to `else` too: an `else` catches the values below the ranges as well as above them. Without the `else`, the verifier would report U5001, since some values, such as 0 and 11, match no arm.
:::

## 8.3 What a branch proves: guards

### What a branch knows

Inside a branch, the verifier knows why the program is there. In the `then` branch of `if units > 0`, it knows that `units > 0` holds; in the `else` branch, that it does not. In an arm `in 1..12`, it knows that the subject is between 1 and 12, and in an arm `is Returned`, that the subject is that variant. These are the **facts of the path**: what is known at a point of the code because of the conditions that lead to it.

A **guard** is a condition you write so that a branch has the fact a step needs. Think of a cashier who checks that a customer is old enough before selling a bottle: the sale happens only after the check, and only there. [Section 3.4](/learn/text-and-conditions/#s3-4) used one to divide safely. This section shows every way a guard gives a fact, how far that fact reaches, and when a guard is the right tool, rather than a precondition or a refined kind.

### Why a guard is needed

[Section 2.2](/learn/numbers/#s2-2) showed that a division by a value that is not a literal is a proof obligation: the verifier must show the divisor is never 0. Here is a price per unit without any guard:

```diff include="steps/04-guard-forms..steps/05-no-guard:src/guards.una" title="src/guards.una" context="0"
--- a/src/guards.una
+++ b/src/guards.una
@@ -8 +8 @@
-per_unit(pack_cents: Int, units: Int) -> Int = if units > 0 then pack_cents / units else 0
+per_unit(pack_cents: Int, units: Int) -> Int = pack_cents / units
```

```text include="steps/05-no-guard/expected/rendered.txt#L1-L6,L8,L12"
[U5001] Error: division obligation `units != 0` is refuted
   ╭─[ src/guards.una:8:48 ]
   │
 8 │ per_unit(pack_cents: Int, units: Int) -> Int = pack_cents / units
   │                                                ─────────┬────────
   │                                                         ╰────────── division obligation `units != 0` is refuted
   │ Help: repair 1: guard the division with `if units != 0`
   │ Note 2: counterexample: units = 0
```

The verifier knows nothing about `units`, so it finds a value that breaks the division: `units = 0`, the counterexample. Nothing has gone wrong yet; the program has not run. But a pack recorded with 0 units would stop the run at that line, so una refuses the function until the code says what happens then. The `Help` line proposes the repair: a guard.

### How to write a guard

The step of this section prices one unit of a pack in four ways, each with its own guard, and its `main` prints each price for a pack of 4 units, then for an empty pack:

```una include="steps/04-guard-forms/src/guards.una" title="src/guards.una" verified="check, run"
module guards

--- Why a pack has no price per unit.
kind PackError = | NoUnits

--- The price of one unit of a pack, or 0 for an empty pack. The division is in the branch
--- where `units > 0` holds.
per_unit(pack_cents: Int, units: Int) -> Int = if units > 0 then pack_cents / units else 0

--- The same price, failing for an empty pack. The branch that fails never reaches the
--- division, so after the `if`, `units == 0` is false.
per_unit_or_fail(pack_cents: Int, units: Int) -> Int
  fails PackError
=
  if units == 0
    fail NoUnits
  pack_cents / units

--- The same price, dividing by a count that a guard keeps from being 0.
per_unit_counted(pack_cents: Int, units: Int) -> Int
=
  let count = if units > 0 then units else 1
  pack_cents / count

--- The same price for a pack of 1 to 12 units. Inside the range arm, `units` is never 0.
per_unit_boxed(pack_cents: Int, units: Int) -> Int
=
  when units
    in 1..12 -> pack_cents / units
    else -> 0

--- Prints each guarded price for a pack of 4 units, then for an empty pack.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{per_unit(1_000, units: 4)}, {per_unit(1_000, units: 0)}")
  let full = per_unit_or_fail(1_000, units: 4)
    if error use -1
  let empty = per_unit_or_fail(1_000, units: 0)
    if error use -1
  @console.print("{full}, {empty}")
  @console.print("{per_unit_counted(1_000, units: 4)}, {per_unit_counted(1_000, units: 0)}")
  @console.print("{per_unit_boxed(1_000, units: 4)}, {per_unit_boxed(1_000, units: 0)}")
```

```text include="steps/04-guard-forms/expected/output.txt"
250, 0
250, -1
250, 1000
250, 0
```

#### A guard with a fallback value

`per_unit` divides only in the `then` branch, where `units > 0` holds, and gives 0 in the `else` branch. This is the guard of section 3.4: the condition is the fact the division needs, or a stronger one.

#### A guard that fails

`per_unit_or_fail` has an `if` without `else` whose branch fails, as in [section 8.1](#s8-1). The branch that fails never reaches the lines after the `if`. So on the line after it, the verifier knows that `units == 0` was `false`, and the division is proven, outside any branch. The empty pack fails with `NoUnits`, and `main` recovers with -1.

#### A guard that picks a safe value

`per_unit_counted` uses the guard to choose the divisor: `let count = if units > 0 then units else 1`. The verifier knows the value of each branch under its condition, so it knows that `count` is `units` when `units > 0` and 1 otherwise, and never 0. The empty pack is priced as a pack of one, 1000.

#### A range arm

`per_unit_boxed` divides inside an arm `in 1..12`. The arm gives the fact `units` is between 1 and 12, which rules out 0 as well as any condition would.

### Proving a product with a guard

A guard can also give a fact that the verifier cannot work out for itself. [Section 5.4](/learn/contracts/#s5-4) showed that the solver cannot read a product of two values: for `unit_cents * quantity`, it cannot prove that the result is not negative, even when both factors are not, and it reports U5002. The first repair is a guard:

:::steps
```una include="steps/09-products/src/invoice.una" title="src/invoice.una" verified="check, run"
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

1. **`kind Cents = Int where it >= 0`.** A refined kind of [section 5.3](/learn/contracts/#s5-3): an amount that is never negative. `line_total` promises a `Cents`, so its result must be proven to be at least 0.
2. **`points`.** Division by the literal 100 is linear, so the verifier proves both clauses with no help. `result * 100` is allowed in a clause: one side is a literal.
3. **`let total = line.unit_cents * line.quantity`.** The product, named. The verifier knows nothing of its sign.
4. **`if total < 0 then 0 else total`.** In the `else` branch, the verifier knows `total >= 0`, so the result is a `Cents`. The `then` branch gives 0, which is a `Cents` too.
:::

`una run .` prints:

```text include="steps/09-products/expected/output.txt"
29800 cents, 298 points
```

The `then` branch never runs, since both factors are at least 0. The verifier does not check that claim: it proves the result whichever branch runs. You check it, from the kinds of the factors, and when one of those kinds changes, you read the guard again. The guard costs one comparison at run time.

### How a guard behaves

#### The fact holds only on its path

A fact holds inside its branch, and after an `if` only when the other branch can never get there, as with `fail`. Once both branches of an `if` have joined, the condition is no longer known. Keep the guarded `count` of `per_unit_counted`, but divide by `units`:

```diff include="steps/04-guard-forms..steps/07-fact-stays:src/guards.una" title="src/guards.una" context="1"
--- a/src/guards.una
+++ b/src/guards.una
@@ -22,3 +22,3 @@
   let count = if units > 0 then units else 1
-  pack_cents / count
+  pack_cents / units
 
```

```text include="steps/07-fact-stays/expected/rendered.txt#L1-L6,L8,L12"
[U5001] Error: division obligation `units != 0` is refuted
    ╭─[ src/guards.una:23:3 ]
    │
 23 │   pack_cents / units
    │   ─────────┬────────
    │            ╰────────── division obligation `units != 0` is refuted
    │ Help: repair 1: guard the division with `if units != 0`
    │ Note 2: counterexample: count = 1, units = 0
```

The counterexample, `count = 1, units = 0`, is a run that took the `else` branch: `count` is 1, and `units` is still 0. The guard protected `count`, not `units`. This is what makes guards safe to edit: a division moved out of the branch that guards it fails its proof at once.

#### A weak condition proves nothing

The condition must rule out every bad value. Weaken the guard of `per_unit` to `units >= 0`:

```diff include="steps/04-guard-forms..steps/06-weak-guard:src/guards.una" title="src/guards.una" context="0"
--- a/src/guards.una
+++ b/src/guards.una
@@ -8 +8 @@
-per_unit(pack_cents: Int, units: Int) -> Int = if units > 0 then pack_cents / units else 0
+per_unit(pack_cents: Int, units: Int) -> Int = if units >= 0 then pack_cents / units else 0
```

```text include="steps/06-weak-guard/expected/rendered.txt#L1-L6,L8,L12"
[U5001] Error: division obligation `units != 0` is refuted
   ╭─[ src/guards.una:8:67 ]
   │
 8 │ per_unit(pack_cents: Int, units: Int) -> Int = if units >= 0 then pack_cents / units else 0
   │                                                                   ─────────┬────────
   │                                                                            ╰────────── division obligation `units != 0` is refuted
   │ Help: repair 1: guard the division with `if units != 0`
   │ Note 2: counterexample: units = 0
```

The counterexample, `units = 0`, passes the new condition and still divides by zero. The `Help` line proposes a guard, `if units != 0`, which is exactly what a correct condition must imply.

#### Facts do not cross a call

The verifier proves each function on its own, with the facts of its own paths. A guard in a caller tells the callee nothing: a function that divides by its parameter needs its own guard, or a `requires` that every caller must prove ([section 5.1](/learn/contracts/#s5-1)). A fact reaches another function only through a header, as section 5.4 said.

#### `is` gives the variant, not its fields

The condition `status is Returned` gives the fact that `status` is that variant, but, as section 4.3 showed, the checker does not let you read its fields after it. To use the fields of a variant, bind them in a `when` arm.

### A precondition, a guard or a kind

All three state a rule about a value. Choose by who can keep the rule:

:::decide
**Which to use:**

| The bad value… | Use |
| --- | --- |
| Is a mistake of the caller, which can always avoid it, such as 0 months of installments | `requires`: every caller proves it ([section 5.1](/learn/contracts/#s5-1)) |
| Can come from a person or another system | A guard in the function that receives it, or a failure ([section 7.6](/learn/failure/#s7-6)) |
| Is a normal case with a sensible answer, such as an empty pack | A guard with a fallback value |
| Is impossible by the type already | Nothing: a refined kind ([section 5.3](/learn/contracts/#s5-3)) carries the fact |
| Holds of every value of a kind, everywhere | A refined kind, instead of the same guard in many functions |
| Is ruled out by the factors, but the solver cannot see it, as for a product | A guard that the program never takes, as in `line_total` |
| Can only be decided by running code, such as the format of a text | `checked` with an opaque predicate ([section 7.5](/learn/failure/#s7-5)) |
:::

A precondition moves the work to the callers: each one must show the condition. That is right when the condition is the caller's to keep. When the value comes from outside the program, no caller can promise anything about it, and the function that receives it must check it. And when the same rule holds everywhere, a refined kind says it once.

### Check yourself: guards

Here is `per_unit` with another guard:

```una include="steps/08-guard-below/src/guards.una#per_unit" title="src/guards.una"
--- The price of one unit of a pack, or 0 for an empty pack. The division is in the branch
--- where `units > 0` holds.
per_unit(pack_cents: Int, units: Int) -> Int = if units < 0 then 0 else pack_cents / units
```

Does it check? If not, what is the counterexample?

:::answer Show the answer
No:

```text include="steps/08-guard-below/expected/diagnostics.txt"
error U5001 at src/guards.una:8:73: division obligation `units != 0` is refuted
  counterexample: units = 0
```

The guard rules out negative units, which is not the fact the division needs. `units = 0` is not below 0, so it takes the `else` branch, which divides by it. The guard must rule out 0: `if units <= 0 then 0 else pack_cents / units` checks.
:::

## 8.4 Kinds that contain themselves

### What a recursive kind is

Some data holds smaller data of the same shape. A store sells gift kits: a kit holds two products, and each of them may be a single item or another kit. A box of boxes, like a set of nesting dolls. A **recursive kind** is a kind that contains itself in one of its fields, so a value can hold another value of its own kind, which can hold another, as deep as the data goes.

### Why a kind contains itself

With records of fixed fields, every level of nesting needs a kind of its own: a kit of items, a kit of kits of items, and so on, with a limit you choose in advance. A real catalog does not stop at the depth you planned. A recursive kind describes every depth with one declaration, and a recursive function, one that calls itself as in [section 6.1](/learn/functions/#s6-1), walks every depth with one body.

### How to write a recursive kind

```una include="steps/16-bundles/src/bundles.una#Bundle" title="src/bundles.una"
--- A product the store sells: one item, or a kit of two products, each of which may be a kit.
kind Bundle = Item(sku: Text, cents: Int) | Kit(first: Bundle, second: Bundle)
```

A kind can contain itself in two ways.

#### A variant that holds its own kind

`Bundle` is a sum whose variant `Kit` has two fields of kind `Bundle`, the kind being declared. The variant `Item` has none, and that matters: it is where a bundle stops. Every value of `Bundle` is built from items at the bottom, with kits above them.

#### Through an `Option`

A field may also hold an `Option` of the kind being declared ([section 7.1](/learn/failure/#s7-1)): `Some` of a value, or `None`. Then `None` is where the value stops, and the kind needs no variant of its own for it. A category of products may sit inside a larger one:

```una include="steps/17-categories/src/kits.una" title="src/kits.una" verified="check, run"
module kits

--- A product category, inside a larger one or at the top. The kind contains itself through
--- an `Option`, and `None` is where the chain stops.
kind Category
  name: Text
  parent: Option[Category]

--- The full name of a category: its parents' names first, then its own.
path(category: Category) -> Text
=
  when category.parent
    is Some(parent) -> "{path(parent)} > {category.name}"
    is None -> category.name

--- How many levels a category sits below the top.
depth(category: Category) -> Int
=
  when category.parent
    is Some(parent) -> 1 + depth(parent)
    is None -> 0

pub main() -> Unit
  uses @console: Console[print]
=
  let lighting = Category(name: "Lighting", parent: None)
  let lamps = Category(name: "Lamps", parent: Some(lighting))
  let desk_lamps = Category(name: "Desk lamps", parent: Some(lamps))
  @console.print("{lamps}")
  @console.print("{path(desk_lamps)}, {depth(desk_lamps)} levels down")
```

```text include="steps/17-categories/expected/output.txt"
Category(name: "Lamps", parent: Some(Category(name: "Lighting", parent: None)))
Lighting > Lamps > Desk lamps, 2 levels down
```

`lamps` sits inside `lighting`, and `parent: None` marks the top. The first line prints `lamps` as you would build it, with its parent inside it. `path` and `depth` each take the category's `parent` apart with a `when`: for `Some(parent)`, they call themselves on the parent; for `None`, they stop.

Use an `Option` when a value holds at most one more of its kind, as a category has at most one parent. A field may also hold a list of values of its kind, for any number of parts; [chapter 10](/learn/collections/#s10-1) teaches lists.

### A reading kit, priced

A function over a recursive kind usually has one arm for each variant: the variant that stops gives its answer at once, and the variant that contains the kind calls the function again on each part and combines the answers.

:::steps
```una include="steps/16-bundles/src/bundles.una" title="src/bundles.una" verified="check, run"
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

```text include="steps/16-bundles/expected/output.txt#L1-L2"
reading kit: 2690 cents
Kit(first: Item(sku: "LAMP-01", cents: 1990), second: Kit(first: Item(sku: "BULB-02", cents: 350), second: Item(sku: "BULB-02", cents: 350)))
```

The lamp costs 1990 and each bulb 350: 1990 + 350 + 350 = 2690. The second line prints the kit as you would build it, every level inside the one above.

### How a recursive kind behaves

#### Every kind needs a value that ends

Every value of a kind is finite: it must be possible to build one without going on forever. A kind whose every variant needs another value of the same kind has no such value. Declare one:

```diff include="steps/16-bundles..steps/18-endless:src/bundles.una" title="src/bundles.una" context="0"
--- a/src/bundles.una
+++ b/src/bundles.una
@@ -4,0 +5,3 @@
+
+--- A crate that always holds another crate: no value of it can ever be built.
+kind Crate = | Holds(inner: Crate)
```

```text include="steps/18-endless/expected/rendered.txt"
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

A `Crate` would hold a crate, which would hold a crate, without end, so no `Crate` can ever be built. U2002 says so, and its message gives the repair: a variant that does not contain the kind, such as `End`. In `Bundle`, `Item` is that variant, and in `Category`, `None` plays that part.

#### A `when` over it needs no special form

A recursive kind is a sum or a record like any other, so a `when` over it follows every rule of [section 8.2](#s8-2): an arm for each variant, or an `else`. The recursion is in the function, not in the `when`.

#### A recursive call has a limit

Each level of a bundle is one more call of `price` waiting for its parts. A run has a limit on how many calls may wait at once, and a value deep enough to exceed it stops the run with U6003, as [section 6.1](/learn/functions/#s6-1) said; [section 16.4](/learn/memory/#s16-4) covers the limits. Store data such as kits and categories nests a few levels, far below the limit.

### A recursive kind, records or a list

:::decide
**Which to use:**

| Your data… | Use |
| --- | --- |
| Has a fixed depth, such as a parcel and its address | Records, one per level |
| Holds parts that are each a whole of the same kind | A recursive kind, with a variant that ends |
| Holds at most one more of its kind, such as a parent | A field of `Option` of the kind |
| Is many values of one kind, in order | A list ([chapter 10](/learn/collections/#s10-1)) |
:::

### Check yourself: recursive kinds

`items` counts the items of a bundle:

```una include="steps/16-bundles/src/bundles.una#items" title="src/bundles.una"
--- How many items a bundle holds. Check yourself: what does `main` print for `office`?
items(bundle: Bundle) -> Int
=
  when bundle
    is Item -> 1
    is Kit(first, second) -> items(first) + items(second)
```

`office` is `Kit(first: desk, second: reading)`, where `desk` is an item and `reading` is the reading kit of this section. What does `items(office)` give?

:::answer Show the answer
```text include="steps/16-bundles/expected/output.txt#L3"
office kit: 4 items
```

`items(office)` is `items(desk) + items(reading)`. The desk is an item, 1. The reading kit is `items(lamp)` plus the items of its inner kit of two bulbs, 1 + 2 = 3. In all, 1 + 3 = 4. The bulb is counted twice, since the kit holds two of it.
:::

## 8.5 Day-to-day: shipment tracking

### What the program must do

The store ships parcels by post or by courier. Each parcel has a price for its zone and its weight. Carriers report events: a pickup, a delivery, a parcel that came back. The tracker keeps each shipment's history of events, works out its status from that history, ignores an event that does not fit, such as a pickup scan sent twice, and says how much of a returned parcel's price the store pays back.

The program uses every part of the chapter: `when` with one arm per variant and with range arms, `if` inside arms, a guard that keeps a refund from going below 0, and a recursive kind for the history. Its package is one module, `tracking`, the entry of its `una.toml`, which grants the console.

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

--- An amount of money in cents. It is never negative.
pub kind Cents = Int where it >= 0

--- Who carries a parcel.
pub kind Carrier = Post | Courier

--- Why a parcel came back.
pub kind ReturnReason = Damaged | WrongItem | Refused

--- Where a shipment is. Each state carries what is known in that state, and nothing else.
pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int)

--- What a carrier or the warehouse reports about a shipment.
pub kind Event = PickedUp(carrier: Carrier, tracking: Text) | DeliveredOn(day: Int) | CameBack(reason: ReturnReason, day: Int)

--- Every event of a shipment, the latest first. `Start` is the history before any event.
pub kind History = Start | After(event: Event, earlier: History)

--- A value before and after something happened.
pub kind Change[T]
  before: T
  after: T
```

Read them in order:

- **`Zone`, `Carrier` and `ReturnReason`** are sums without fields: fixed lists of names.
- **`Parcel`** is a record of three fields, one of which is a `Zone`. **`Cents`** is the refined kind of [section 5.3](/learn/contracts/#s5-3), for amounts that are never negative.
- **`Status`** is the heart of the program. Each variant carries what is known in that state: nothing while packed, a carrier and a tracking number while in transit, a day once delivered, a reason and a day once returned. A delivered status without a day cannot be written.
- **`Event`** is what the outside world reports, and its variants mirror the transitions.
- **`History`** is a recursive kind. `Start` is a history with no event yet. `After(event, earlier)` is the history `earlier` with one more event, the latest. So the latest event is on the outside, and `Start` is at the bottom, where every history ends.
- **`Change[T]`** is a generic record of [section 4.4](/learn/kinds/#s4-4): a value before and after something happened.

### Pricing a parcel

`postage` adds the price of the zone to the supplement for the weight. Each part is a `when`: one arm per zone, and weight bands with range arms and an `else`, as in [section 8.2](#s8-2).

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

`zone_cents` has no `else`, so a new zone stops the program from checking until it has a price. `weight_cents` has an `else`, since weights never run out: it is what makes the bands cover every `Int`, negative weights included.

### Following a history

`apply` takes a status and an event, and gives the next status: one `when` over the event, and in each arm an `if` that tests the status with `is`. An event that does not fit the current status leaves it as it is, so a second pickup scan, or a return before any delivery, changes nothing.

```una include="day-to-day/src/tracking.una#apply..changed" title="day-to-day/src/tracking.una"
--- The status after an event. An event that does not fit the status changes nothing, such
--- as a pickup scan that a carrier sends twice.
pub apply(status: Status, event: Event) -> Status
=
  when event
    is PickedUp(carrier, tracking) -> if status is Packed then InTransit(carrier, tracking) else status
    is DeliveredOn(day) -> if status is InTransit then Delivered(day) else status
    is CameBack(reason, day) -> if status is Delivered then Returned(reason, day) else status

--- The status a history leads to: every event applied, the oldest first.
pub status_of(history: History) -> Status
=
  when history
    is Start -> Packed
    is After(event, earlier) -> apply(status_of(earlier), event)

--- What the latest event of a history did: the status before it, and after it.
pub latest(history: History) -> Change[Status]
=
  when history
    is Start -> Change(before: Packed, after: Packed)
    is After(event, earlier) ->
      let before = status_of(earlier)
      Change(before, after: apply(before, event))

--- Whether something changed. Any type whose values can be compared will do.
pub changed[T: Eq](change: Change[T]) -> Bool = change.before != change.after
```

- **`status_of`** is recursive, as the functions of [section 8.4](#s8-4) are. A history with no event is `Packed`. A history with one more event is the status of the earlier history, with the event applied. So the oldest event is applied first.
- **`latest`** says what the latest event did. Its second arm has several lines: it names the status before the event, then builds the `Change`. `Change(before, after: …)` passes `before` without a label, since a name equal to the field's name counts as its label ([section 6.1](/learn/functions/#s6-1)).
- **`changed`** compares the two statuses with `!=`, which needs the `Eq` constraint of section 4.4.

Why ignore an event that does not fit, rather than fail? Carriers resend scans, and a report that arrives late is still a report. The tracker keeps the status it trusts, and the `Change` shows that nothing happened. A function that must stop the work instead would declare a failure, as [chapter 7](/learn/failure/#s7-2) shows.

### Words for people, and the refund

`describe` has one arm per status and binds the fields it prints. `carrier_name` and `reason_text` turn variants without fields into words. None of them has an `else`, so a new carrier, reason or status is reported at the `when` that must say something about it.

```una include="day-to-day/src/tracking.una#describe..refund" title="day-to-day/src/tracking.una"
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

--- What the store pays back for a shipment: all of `paid` for a parcel that came back by the
--- store's fault, `paid` less 600 cents of return postage for a refused one, and nothing
--- otherwise. The guard keeps the refund from going below 0.
pub refund(status: Status, paid: Cents) -> Cents
=
  when status
    is Returned(reason) ->
      if reason == Refused
        if paid > 600 then paid - 600 else 0
      else
        paid
    else -> 0
```

`refund` is the other kind of function: one case matters, and `else` covers the rest. Inside the `Returned` arm, an `if` asks about the reason. A parcel refused at the door is refunded less the 600 cents of return postage, and the inner `if paid > 600 then paid - 600 else 0` is a guard of [section 8.3](#s8-3): in its `then` branch, the verifier knows `paid > 600`, so `paid - 600` is at least 1, and the result is a `Cents`. Without the guard, a refused parcel of 400 cents would be owed -200.

### Running it

`report` turns the latest event of a history into a line of text. `main` prices a lamp, then builds its history one event at a time: a pickup, the same pickup again, and a delivery. Then it prices a vase sent abroad, which was delivered and then refused.

```una include="day-to-day/src/tracking.una#report..main" title="day-to-day/src/tracking.una"
--- One line of the tracking report.
pub report(order: Text, history: History) -> Text
=
  let change = latest(history)
  if changed(change)
    "{order}: {describe(change.after)}"
  else
    "{order}: no change, still {describe(change.after)}"

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
  @console.print("{lamp.order}: postage {postage(lamp)}")
  let picked = After(event: PickedUp(carrier: Courier, tracking: "CX-4471"), earlier: Start)
  @console.print(report(lamp.order, history: picked))
  let again = After(event: PickedUp(carrier: Courier, tracking: "CX-4471"), earlier: picked)
  @console.print(report(lamp.order, history: again))
  let arrived = After(event: DeliveredOn(day: 3), earlier: again)
  @console.print(report(lamp.order, history: arrived))
  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad)
  @console.print("{vase.order}: postage {postage(vase)}")
  let sent = After(event: DeliveredOn(day: 8), earlier: After(event: PickedUp(carrier: Post, tracking: "PO-2210"), earlier: Start))
  let back = After(event: CameBack(reason: Refused, day: 12), earlier: sent)
  @console.print("{report(vase.order, history: back)}; refund {refund(status_of(back), paid: 4500)}")
```

Each history is built on the one before it: `again` is `picked` with one more event, and `arrived` is `again` with one more. `una run .` prints the report shown in [What you'll build](#what-youll-build). The third line is the duplicate scan: the status stayed `InTransit`, and the report says so instead of pretending something happened. The vase paid 4500 cents and was refused, so the store pays back 4500 - 600 = 3900.

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

--- An amount of money in cents. It is never negative.
pub kind Cents = Int where it >= 0

--- Who carries a parcel.
pub kind Carrier = Post | Courier

--- Why a parcel came back.
pub kind ReturnReason = Damaged | WrongItem | Refused

--- Where a shipment is. Each state carries what is known in that state, and nothing else.
pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int)

--- What a carrier or the warehouse reports about a shipment.
pub kind Event = PickedUp(carrier: Carrier, tracking: Text) | DeliveredOn(day: Int) | CameBack(reason: ReturnReason, day: Int)

--- Every event of a shipment, the latest first. `Start` is the history before any event.
pub kind History = Start | After(event: Event, earlier: History)

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

--- The status a history leads to: every event applied, the oldest first.
pub status_of(history: History) -> Status
=
  when history
    is Start -> Packed
    is After(event, earlier) -> apply(status_of(earlier), event)

--- What the latest event of a history did: the status before it, and after it.
pub latest(history: History) -> Change[Status]
=
  when history
    is Start -> Change(before: Packed, after: Packed)
    is After(event, earlier) ->
      let before = status_of(earlier)
      Change(before, after: apply(before, event))

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

--- What the store pays back for a shipment: all of `paid` for a parcel that came back by the
--- store's fault, `paid` less 600 cents of return postage for a refused one, and nothing
--- otherwise. The guard keeps the refund from going below 0.
pub refund(status: Status, paid: Cents) -> Cents
=
  when status
    is Returned(reason) ->
      if reason == Refused
        if paid > 600 then paid - 600 else 0
      else
        paid
    else -> 0

--- One line of the tracking report.
pub report(order: Text, history: History) -> Text
=
  let change = latest(history)
  if changed(change)
    "{order}: {describe(change.after)}"
  else
    "{order}: no change, still {describe(change.after)}"

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
  @console.print("{lamp.order}: postage {postage(lamp)}")
  let picked = After(event: PickedUp(carrier: Courier, tracking: "CX-4471"), earlier: Start)
  @console.print(report(lamp.order, history: picked))
  let again = After(event: PickedUp(carrier: Courier, tracking: "CX-4471"), earlier: picked)
  @console.print(report(lamp.order, history: again))
  let arrived = After(event: DeliveredOn(day: 3), earlier: again)
  @console.print(report(lamp.order, history: arrived))
  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad)
  @console.print("{vase.order}: postage {postage(vase)}")
  let sent = After(event: DeliveredOn(day: 8), earlier: After(event: PickedUp(carrier: Post, tracking: "PO-2210"), earlier: Start))
  let back = After(event: CameBack(reason: Refused, day: 12), earlier: sent)
  @console.print("{report(vase.order, history: back)}; refund {refund(status_of(back), paid: 4500)}")

example "a heavy parcel abroad pays the zone and the weight"
  do postage(Parcel(order: "A-1003", grams: 2500, zone: Abroad))
  expect result == 1600

example "a second pickup scan changes nothing"
  do latest(After(event: PickedUp(carrier: Post, tracking: "PO-1"), earlier: After(event: PickedUp(carrier: Post, tracking: "PO-1"), earlier: Start)))
  expect not changed(result)

example "a parcel cannot come back before it was delivered"
  do status_of(After(event: CameBack(reason: Damaged, day: 2), earlier: Start))
  expect result is Packed

example "a damaged parcel is refunded in full"
  do refund(Returned(reason: Damaged, day: 5), paid: 4500)
  expect result == 4500

example "a refused parcel is refunded less the return postage"
  do refund(Returned(reason: Refused, day: 5), paid: 601)
  expect result == 1

example "a refund never goes below 0"
  do refund(Returned(reason: Refused, day: 5), paid: 400)
  expect result == 0

example "a delivered parcel is not refunded"
  do refund(Delivered(day: 3), paid: 4500)
  expect result == 0
```

## 8.6 Testing it

### The rules the run does not reach

Each example builds the values it needs and checks one rule. The run in `main` shows the common path; the examples cover the edges it does not reach: a heavy parcel abroad, a return before any delivery, and each case of `refund`.

```una include="day-to-day/src/tracking.una#L141-L167" title="day-to-day/src/tracking.una" caption="the examples"
example "a heavy parcel abroad pays the zone and the weight"
  do postage(Parcel(order: "A-1003", grams: 2500, zone: Abroad))
  expect result == 1600

example "a second pickup scan changes nothing"
  do latest(After(event: PickedUp(carrier: Post, tracking: "PO-1"), earlier: After(event: PickedUp(carrier: Post, tracking: "PO-1"), earlier: Start)))
  expect not changed(result)

example "a parcel cannot come back before it was delivered"
  do status_of(After(event: CameBack(reason: Damaged, day: 2), earlier: Start))
  expect result is Packed

example "a damaged parcel is refunded in full"
  do refund(Returned(reason: Damaged, day: 5), paid: 4500)
  expect result == 4500

example "a refused parcel is refunded less the return postage"
  do refund(Returned(reason: Refused, day: 5), paid: 601)
  expect result == 1

example "a refund never goes below 0"
  do refund(Returned(reason: Refused, day: 5), paid: 400)
  expect result == 0

example "a delivered parcel is not refunded"
  do refund(Delivered(day: 3), paid: 4500)
  expect result == 0
```

As in [section 1.7](/learn/hello/#s1-7), `do` calls the code under test, `result` is what it gave, and each `expect` line states something that must hold. `expect result is Packed` checks the variant without its fields, and `expect not changed(result)` calls a function of the program on the result: any `Bool` works. [Chapter 14](/learn/testing/#s14-1) covers examples in full.

### The edges of a guard

A guard has an edge, and each side of it deserves an example. "a refused parcel is refunded less the return postage" pays 601 cents, the smallest amount that takes the `then` branch, and gets 1 back. "a refund never goes below 0" pays 400, which takes the `else` branch. The verifier has already proven that the result is never negative; the examples show which number each side gives.

### One example per rule that an `else` decides

An arm per variant is checked by the checker: forget one, and the program does not check. An `else` is not: whatever it answers, it checks. So the rules that an `else` decides need examples of their own. "a delivered parcel is not refunded" tests the `else` of `refund`, and "a parcel cannot come back before it was delivered" tests the `else status` of `apply`.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L10"
example tracking "a heavy parcel abroad pays the zone and the weight" ... ok
example tracking "a second pickup scan changes nothing" ... ok
example tracking "a parcel cannot come back before it was delivered" ... ok
example tracking "a damaged parcel is refunded in full" ... ok
example tracking "a refused parcel is refunded less the return postage" ... ok
example tracking "a refund never goes below 0" ... ok
example tracking "a delivered parcel is not refunded" ... ok

7 examples: 7 passed, 0 failed
```

When an example fails, `una test .` names it and shows the value `result` had, as [Exercise 1](#exercise-1-a-lost-parcel) shows.

## 8.7 Common mistakes

Each mistake is a small change to `day-to-day/src/tracking.una`, followed by what `una check .` reports.

### A `when` that misses a variant (U2007)

:::mistake
Remove the `Returned` arm from `describe`:

```diff include="day-to-day..mistakes/1:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -86,3 +86,2 @@
     is Delivered(day) -> "delivered on day {day}"
-    is Returned(reason, day) -> "returned on day {day}, {reason_text(reason)}"
 
```

```text include="mistakes/1/expected/rendered.txt#L1-L8"
[U2007] Error: `when` does not match variant `Returned` of `Status`
    ╭─[ src/tracking.una:83:3 ]
    │
 83 │   when status
    │   ──┬─
    │     ╰─── `when` does not match variant `Returned` of `Status`
    │
    │ Help: repair 1: add an arm for each missing variant, such as `is Returned`, or an `else` arm
```

*Why:* a `when` over a sum covers every variant. The marks are on the `when` itself, since the problem is an arm that is not there, and the message names the missing variant and its kind. You get the same error after adding a variant to `Status`, at every `when` that needs an arm for it.

*Fix:* add the arm. Add `else` only when every remaining variant really gets the same answer. See [U2007](/docs/errors/U2007/).
:::

### Ranges that leave a gap (U5001)

:::mistake
Replace the `else` of `weight_cents` with a last band:

```diff include="day-to-day..mistakes/2:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -49,3 +49,3 @@
     in 501..2000 -> 150
-    else -> 400
+    in 2001..30000 -> 400
 
```

```text include="mistakes/2/expected/rendered.txt#L1,L8,L12"
[U5001] Error: exhaustiveness of this `when`, `grams in 0..500 or grams in 501..2000 or grams in 2001..30000`, is refuted
    │ Help: repair 1: add an `else` arm, or arms for the values the others miss
    │ Note 2: counterexample: grams = -1
```

*Why:* without an `else`, the verifier must prove that the ranges cover every `Int`, and the first line quotes what it tried to prove. `Note 2` is the counterexample: no arm matches `grams = -1`, nor anything above 30,000. An `Int` can be any whole number, negative ones included.

*Fix:* end with an `else` arm, as the help says. To rule out negative weights for good, give the field a refined kind, as [section 5.3](/learn/contracts/#s5-3) shows. See [U5001](/docs/errors/U5001/).
:::

### An `else` before the other arms (U2008)

:::mistake
Put the `else` of `refund` first:

```diff include="day-to-day..mistakes/3:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -107,2 +107,3 @@
   when status
+    else -> 0
     is Returned(reason) ->
@@ -112,3 +113,2 @@
         paid
-    else -> 0
 
```

```text include="mistakes/3/expected/rendered.txt#L1-L9"
[U2008] Error: this arm follows the `else` arm, so no value reaches it; `else` must be the last arm
     ╭─[ src/tracking.una:109:5 ]
     │
 108 │     else -> 0
     │     ──┬─
     │       ╰─── the `else` arm
 109 │     is Returned(reason) ->
     │     ─────────┬─────────
     │              ╰─────────── this arm follows the `else` arm, so no value reaches it; `else` must be the last arm
```

*Why:* the arms are tried in order, and `else` matches every value, so no status would ever reach the `Returned` arm, and every refund would be 0. The first mark shows the `else`, and the second the arm it hides. Una refuses the `when`, since an arm that can never run is always a mistake.

*Fix:* move `else` to the end, where it takes only the values the other arms leave. See [U2008](/docs/errors/U2008/).
:::

### A guard without its `else` (U0101)

:::mistake
Leave out the `else` of the guard in `refund`:

```diff include="day-to-day..mistakes/4:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -109,3 +109,3 @@
       if reason == Refused
-        if paid > 600 then paid - 600 else 0
+        if paid > 600 then paid - 600
       else
```

```text include="mistakes/4/expected/rendered.txt#L1-L8"
[U0101] Error: unexpected end of line, expected `else`
     ╭─[ src/tracking.una:110:38 ]
     │
 110 │         if paid > 600 then paid - 600
     │                                      ┬
     │                                      ╰── unexpected end of line, expected `else`
     │
     │ Help: repair 1: an `if` with `then` needs `else`; to fail early, make the rest of the body its `else` branch, as in `if x < 0 then fail Broke else x`, or use the block form, whose `else` block holds the rest
```

*Why:* the one-line `if` gives a value, the refund, so it needs one for both answers of its condition. Without `else`, a refused parcel of 600 cents or less would have no refund at all. The marks point at the end of the line, where `else` was expected.

*Fix:* add `else 0`, the value when the condition is `false`. The `if` without `else` of [section 8.1](#s8-1) is a statement, and never gives a value. See [U0101](/docs/errors/U0101/).
:::

### A guard that does not rule out the bad value (U5001)

:::mistake
Guard the refund with `paid > 0` instead of `paid > 600`:

```diff include="day-to-day..mistakes/5:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -109,3 +109,3 @@
       if reason == Refused
-        if paid > 600 then paid - 600 else 0
+        if paid > 0 then paid - 600 else 0
       else
```

```text include="mistakes/5/expected/rendered.txt#L1-L10,L18"
[U5001] Error: refinement `result >= 0` is refuted
     ╭─[ src/tracking.una:110:26 ]
     │
  13 │ pub kind Cents = Int where it >= 0
     │                            ───┬───
     │                               ╰───── where clause
     │
 110 │         if paid > 0 then paid - 600 else 0
     │                          ─────┬────
     │                               ╰────── refinement `result >= 0` is refuted
     │ Note 2: counterexample: paid = 1, result = -599, status = Returned, status.reason = Refused
```

*Why:* `refund` promises a `Cents`, a value of at least 0. In the `then` branch, the verifier knows only `paid > 0`, which allows `paid = 1`, and then the refund is -599. The marks point at `paid - 600`, the value that breaks the refinement, and at the `where` clause of `Cents` that it breaks. The counterexample names the whole path: the status, its reason, the amount and the result.

*Fix:* a condition that implies the result is at least 0: `paid > 600`, or `paid >= 600`. See [U5001](/docs/errors/U5001/).
:::

### Comparing with a variant that has fields (U2009)

:::mistake
Test the status with `==` in `apply`:

```diff include="day-to-day..mistakes/6:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -57,3 +57,3 @@
     is PickedUp(carrier, tracking) -> if status is Packed then InTransit(carrier, tracking) else status
-    is DeliveredOn(day) -> if status is InTransit then Delivered(day) else status
+    is DeliveredOn(day) -> if status == InTransit then Delivered(day) else status
     is CameBack(reason, day) -> if status is Delivered then Returned(reason, day) else status
```

```text include="mistakes/6/expected/rendered.txt#L1,L8"
[U2009] Error: variant `InTransit` needs its fields: `carrier`, `tracking`
    │ Help: repair 1: write `status is InTransit`; edit src/tracking.una:58:31..58:50 to "status is InTransit"
```

*Why:* `InTransit` on its own is not a value: it needs a carrier and a tracking number. `==` compares two whole values, so it has nothing to compare `status` with. This one comes from other languages, where comparing a status with a name is the usual test.

*Fix:* `status is InTransit`, which tests the variant only. The help line holds the exact edit, and `una fix .` applies it. See [U2009](/docs/errors/U2009/).
:::

### A recursive kind with no variant that ends (U2002)

:::mistake
Remove `Start` from `History`, so that every history is one event after another:

```diff include="day-to-day..mistakes/7:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -27,3 +27,3 @@
 --- Every event of a shipment, the latest first. `Start` is the history before any event.
-pub kind History = Start | After(event: Event, earlier: History)
+pub kind History = | After(event: Event, earlier: History)
 
```

```text include="mistakes/7/expected/rendered.txt#L1-L9"
[U2002] Error: kind `History` has no finite value: every variant contains a kind without one; add a variant without it, as `End`
    ╭─[ src/tracking.una:28:10 ]
    │
 28 │ pub kind History = | After(event: Event, earlier: History)
    │          ───┬───
    │             ╰───── kind `History` has no finite value: every variant contains a kind without one; add a variant without it, as `End`
    │
    │ Note: run `una explain U2002` for an explanation
────╯
```

*Why:* every `After` needs an earlier history, which would be another `After`, without end, so no `History` can be built. U2002 is reported at the kind. Each use of `Start` in the program is then reported too, as U1001, since the variant no longer exists.

*Fix:* keep a variant that does not contain the kind, here `Start`, as the bottom of every history. See [U2002](/docs/errors/U2002/).
:::

## 8.8 Exercises

Each exercise starts from `exercises/N/start` in this chapter's download: the day-to-day program with the exercise's examples added, and a stub of what to write when there is one. `una check .` or `una test .` fails there until the exercise is done. Work in small steps: make one change, run `una check .`, and read what it reports before the next change.

### Exercise 1: a lost parcel

::::exercise
Sometimes a carrier loses a parcel. Add a variant `Lost(day: Int)` to `Status`, describe it as "lost since day N", and refund it in full. The start package ends with these examples, and `una check .` reports U1001 until the variant exists:

```una include="exercises/1/start/src/tracking.una#L169-L175" title="exercises/1/start/src/tracking.una"
example "a lost parcel says since when"
  do describe(Lost(day: 20))
  expect result == "lost since day 20"

example "a lost parcel is refunded in full"
  do refund(Lost(day: 20), paid: 4500)
  expect result == 4500
```

:::hint
*Hint:* work in three steps. First add the variant at the end of `Status`, after a `|`, and run `una check .`: the checker shows the one `when` that needs a new arm. Then add that arm to `describe`, binding `day`. Last, run `una test .`: `refund` has an `else`, so it checks, and only the second example tells you what it answers.
:::

What `una check .` reports after adding only the variant:

```text include="exercises/1/variant/expected/rendered.txt#L1,L8"
[U2007] Error: `when` does not match variant `Lost` of `Status`
    │ Help: repair 1: add an arm for each missing variant, such as `is Lost`, or an `else` arm
```

With the variant and an arm in `describe`, `una check .` is clean, and `una test .` shows what the `else` of `refund` answers:

```text include="exercises/1/described/expected/commands/test.txt#L10-L14"
example tracking "a lost parcel is refunded in full" ... FAILED
  src/tracking.una:176: expect result == 4500
  it is false, with `result` = `0`

9 examples: 8 passed, 1 failed
```

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Add the variant, an arm in `describe`, and an arm in `refund`:

```diff include="exercises/1/start..exercises/1/answer:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -21,3 +21,3 @@
 --- Where a shipment is. Each state carries what is known in that state, and nothing else.
-pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int)
+pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int) | Lost(day: Int)
 
@@ -87,2 +87,3 @@
     is Returned(reason, day) -> "returned on day {day}, {reason_text(reason)}"
+    is Lost(day) -> "lost since day {day}"
 
@@ -112,2 +113,3 @@
         paid
+    is Lost -> paid
     else -> 0
```

The `else` of `refund` would have answered 0 for a lost parcel. This is the cost of an `else` on a sum that grows: the checker cannot tell you that a new variant needs a different answer, so an example has to.
:::
::::

### Exercise 2: counting the events

::::exercise
Write `scans`, which counts the events of a history. The start package has a stub that always gives 0, and these examples, the second of which fails until `scans` is written:

```una include="exercises/2/start/src/tracking.una#L172-L178" title="exercises/2/start/src/tracking.una"
example "a new shipment has no events"
  do scans(Start)
  expect result == 0

example "every event counts, a repeated scan too"
  do scans(After(event: DeliveredOn(day: 3), earlier: After(event: PickedUp(carrier: Post, tracking: "PO-1"), earlier: After(event: PickedUp(carrier: Post, tracking: "PO-1"), earlier: Start))))
  expect result == 3
```

:::hint
*Hint:* follow `status_of`. One arm per variant of `History`: `Start` has no event, and `After` has one event more than its `earlier` history. The `After` arm needs only the field `earlier`, so it can bind that one alone. A body that is a `when` goes on the lines under `=`.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
One arm for each variant, and a recursive call on the earlier history:

```diff include="exercises/2/start..exercises/2/answer:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -76,4 +76,8 @@
 
---- How many events a history holds. Exercise 2: count them.
-pub scans(history: History) -> Int = 0
+--- How many events a history holds.
+pub scans(history: History) -> Int
+=
+  when history
+    is Start -> 0
+    is After(earlier) -> 1 + scans(earlier)
 
```

Each call works on a smaller history, so the calls end at `Start`. The repeated pickup is counted, since `scans` counts events, not changes of status.
:::
::::

### Exercise 3: the next action

::::exercise
Design a kind. For each status, the store does one thing next: wait while a parcel is packed, send the tracking number to the customer while it is in transit, ask for a review once it is delivered, put a refused parcel back on the shelf, and refund one returned for any other reason. The start package has a placeholder kind, `Action`, a stub for `next_action`, and these examples, which report U1001 until the kind has the variants they name:

```una include="exercises/3/start/src/tracking.una#L175-L189" title="exercises/3/start/src/tracking.una"
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
*Hint:* read the examples first: they name the variants `SendTracking`, `Refund`, `Restock` and `AskForReview`, and the placeholder has `Wait`. Only one action carries data, so only one variant has a field. In `next_action`, write one arm per status; the `Returned` arm binds `reason` and chooses with an `if`, comparing the reason with `==`, which works on a variant without fields.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Declare the actions, and choose one for each status:

```diff include="exercises/3/start..exercises/3/answer:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -114,7 +114,13 @@
 
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

`is InTransit(tracking)` binds one of the two fields of `InTransit` by its name, and `SendTracking(tracking)` passes it on, unlabeled since that variant has one field. The `Returned` arm chooses with an `if`, since only one reason differs; a `when` over the reason, with an arm for `Refused` and an `else`, would say the same.
:::
::::

## 8.9 Recap and reference

### For agents

:::agents
`una --json check .` gives every diagnostic as JSON. For [A `when` that misses a variant](#a-when-that-misses-a-variant-u2007):

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U2007","severity":"error","domain":"types","message":"`when` does not match variant `Returned` of `Status`","primary":{"file":"src/tracking.una","start":{"line":83,"col":3},"end":{"line":83,"col":7}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"add an arm for each missing variant, such as `is Returned`, or an `else` arm","edit":null}],"explain":"una explain U2007"}],"fixable":0}
```

U2007, U2008 and U5001 carry no `edit`, since only the author knows what a missing or misplaced arm should do. The block form of an `if` written with `then` (U0101) and the `==` form of U2009 carry exact edits, which `una fix .` applies. The compact rule: *an `if` without `else` is a statement; an `if` with `else` gives a value and is the last line or a `let`; `when` covers every variant, literal and range, or ends with `else`, which comes last; a pattern holds no condition; a fact holds on its path only; a recursive kind has a variant that ends.*
:::

### Recap

:::recap
- An `if` without `else` runs its lines only when its condition holds; it gives no value.
- An `if` with `else`, over several lines, is the last line of its block or the value of a `let`.
- `when` takes literal arms (`is 2`, `is "RUG-07"`, `is true`) and range arms (`in 1..<10`, `in 10..49`); end them with `else` unless they cover every value.
- The arms are tried in order; prefer ranges that do not overlap, and put `else` last.
- A pattern holds no condition: put an `if` inside the arm.
- Inside a branch, the verifier knows its condition; after an `if` whose branch fails, it knows the opposite. Elsewhere, it knows neither.
- Guard values that can be bad; use `requires` for the caller's mistakes, a refined kind for rules that hold everywhere.
- A recursive kind needs a variant that does not contain it, or an `Option` field.
:::

### Reference

:::reference
- Construct pages: [`if`](/docs/language/control-flow/if/), [`when`](/docs/language/control-flow/when/), [`kind`](/docs/language/types/kind/), [`example`](/docs/language/examples/example/)
- Prelude: [`Option`](/docs/std/)
- Commands: [`una fix`](/docs/cli/fix/), [`una obligations`](/docs/cli/obligations/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2002](/docs/errors/U2002/), [U2007](/docs/errors/U2007/), [U2008](/docs/errors/U2008/), [U2009](/docs/errors/U2009/), [U5001](/docs/errors/U5001/), [U5002](/docs/errors/U5002/), [U6003](/docs/errors/U6003/)
- Specification: [grammar](/docs/spec/02-grammar/), [types](/docs/spec/03-types/), [static semantics](/docs/spec/10-static-semantics/), [verification](/docs/spec/12-verification/), [memory model](/docs/spec/17-memory-model/)
:::
