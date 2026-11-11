---
learn: "6"
title: Functions and their results
editions: ["0.2"]
codes: [U0101, U0103, U2001, U2004, U2005, U2006, U2011, U3001, U3004, U3013, U5001, U7001]
time: 50
builds: A shipping report that quotes each order of the day by weight and zone, with a weekend offer
prerequisites: ["1", "2", "3", "4", "5"]
template: 2
nav: ["Calls in depth", "The result of a function", "What a header says", "Day-to-day: shipping quotes", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 6 Functions and their results

You have written functions since [chapter 1](/learn/hello/#s1-4): a name, parameters, a result type and a body. This chapter looks at them closely, from the two sides of every function. From the caller's side: how a call matches its arguments to parameters, in what order it works them out, and how a dot turns a call into a method call on your own kinds. From the function's side: how its body gives back its result, what the checker does with that result, and what its header tells the rest of the program. You end with a shipping report that quotes each order of the day.

## What you'll build

:::build
A shipping report. For each order of the day, the program works out the charge from the parcel's weight and the zone it ships to, ships large orders within the country for free, and gives a weekend offer to one order:

```text include="day-to-day/expected/output.txt"
order 1042: 7.90
order 1043: ships free
order 1044: 30.90
order 1045: 15.45
order 1046: 13.90
```

You will learn to:

- call a function with labels, in any order, with punning, and as a method on a value of your own kind;
- know the order in which a call works out its arguments, and why a call that prints stands on a line of its own;
- give back a result from a body of one line or of several, and read what the checker says when the result is wrong;
- rely on a function's header, and nothing else, when you use its result;
- choose between a public and a private function, and read the header the checker infers for a private one.
:::

## Why it works this way

In a program of any size, most code is calls of functions that someone else wrote, or that you wrote months ago. A caller then has the function's header in front of it, and not its body. In many languages that header tells only part of the story. Arguments are matched by their place, so a call that swaps two numbers is accepted, and the bug shows up later in a wrong total. Whether a function prints or writes a file shows only in its body. What it promises about its result, such as "never negative", lives in a comment that nothing checks.

Una puts the whole story in the header, and checks it from both sides. A call names every argument after the first, so a swap is visible where it happens. The checker holds the body to the result type that the header states. A caller may rely on the header's promises, and only on those: the verifier never reads the body of a function to prove something about its caller. A public header also says what the function may do outside the program, and the checker refuses a body that does more.

> [!KEY]
> A caller of a Una function needs only its header. The names, the types, the effects and the promises are all there, and the checker makes sure the body keeps them.

## 6.1 Calls in depth: labels, the order of evaluation, method calls on your own kinds

### What a call is, part by part

A **call** asks a function to do its work. You have written many since [chapter 1](/learn/hello/#s1-4): `opening_hours()`, `section("Hours", notice: opening_hours())`. Here are the words for each part of one, all in one place:

- The **function** is the named piece of work, written once, with its header and body.
- A **parameter** is a name in the header for a value the function needs, with its type: `cents: Int`.
- An **argument** is the value a call passes for a parameter: in `half(1_990)`, the argument is `1990`.
- A **label** is a parameter's name written before an argument, with a colon: `off_cents: 200`.
- The **caller** is the code that writes the call. The call stands for the function's result in the caller's code.

Think of an order form at a supplier: every box on the form has a printed name, "quantity", "unit price", "deliver by", and you write a value in each. Nobody reads the form by the order of the boxes. They read the names. A label is that printed name, carried into the call.

Each example of this chapter is a package, made as [chapter 2](/learn/numbers/#each-step-is-a-package) explains, and the chapter's download, `06-functions.tar.gz`, holds them all.

### Why Una labels arguments

The module `lines` has a function `reduced(cents: Int, off_cents: Int)`, which takes `off_cents` off a price. Both parameters are whole numbers. Called by place alone, as many languages allow, `reduced(1_990, 200)` and `reduced(200, 1_990)` look equally right, and the second one gives a negative price. Una does not accept the first form:

```diff include="steps/01-labels..steps/02-positional:src/lines.una" context="1"
--- a/src/lines.una
+++ b/src/lines.una
@@ -16,3 +16,3 @@
   @console.print("one argument: {half(1_990)} and {half(cents: 1_990)}")
-  @console.print("two arguments: {reduced(1_990, off_cents: 200)}")
+  @console.print("two arguments: {reduced(1_990, 200)}")
   @console.print("every argument labeled: {reduced(cents: 1_990, off_cents: 200)}")
```

```text include="steps/02-positional/expected/rendered.txt"
[U2004] Error: argument 2 of `reduced` needs a label; only the first argument may go without one
    ╭─[ src/lines.una:17:50 ]
    │
 17 │   @console.print("two arguments: {reduced(1_990, 200)}")
    │                                                  ─┬─
    │                                                   ╰─── argument 2 of `reduced` needs a label; only the first argument may go without one
    │
    │ Help: repair 1: label it `off_cents`; edit src/lines.una:17:50..17:53 to "off_cents: 200"
    │
    │ Note: run `una explain U2004` for an explanation
────╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

The first line says which argument needs a label: argument 2 of `reduced`. The marks point at `200`, and the `Help` line gives the exact repair, `off_cents: 200`, which `una fix .` can make for you. With the label, the call reads `reduced(1_990, off_cents: 200)`: the price, then what comes off it. A swap would read `reduced(200, off_cents: 1_990)`, which looks wrong at a glance, to you and to anyone who reviews the code.

### How to write a call

The module `lines` has three functions, and its `main` calls them in every form a call can take:

```una include="steps/01-labels/src/lines.una" title="src/lines.una" verified="check, run"
module lines

--- What `units` units cost at `unit_cents` cents each.
pub line_total(unit_cents: Int, units: Int) -> Int = unit_cents * units

--- A price with `off_cents` taken off.
pub reduced(cents: Int, off_cents: Int) -> Int = cents - off_cents

--- Half of an amount, rounded down.
pub half(cents: Int) -> Int = cents / 2

--- Prints one line for each form of a call.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("one argument: {half(1_990)} and {half(cents: 1_990)}")
  @console.print("two arguments: {reduced(1_990, off_cents: 200)}")
  @console.print("every argument labeled: {reduced(cents: 1_990, off_cents: 200)}")
  @console.print("labels in any order: {reduced(off_cents: 200, cents: 1_990)}")
  let units = 3
  @console.print("punning: {line_total(4_500, units)}")
  @console.print("a call inside a call: {half(line_total(1_990, units: 2))}")
```

`una run .` prints:

```text include="steps/01-labels/expected/output.txt"
one argument: 995 and 995
two arguments: 1790
every argument labeled: 1790
labels in any order: 1790
punning: 13500
a call inside a call: 1990
```

Each line of `main` shows one form. The sections below name them.

#### One argument

A call with one argument may leave the label out, since there is nothing to confuse the argument with: `half(1_990)`. Writing it is allowed too: `half(cents: 1_990)` is the same call.

#### The first argument, then labels

With two or more arguments, the first may go without a label, and every other argument carries one: `reduced(1_990, off_cents: 200)`. An unlabeled first argument always fills the first parameter, here `cents`, whatever the value is.

#### Every argument labeled

The first argument may carry its label too: `reduced(cents: 1_990, off_cents: 200)`. Write it when the first value alone does not say what it is.

#### Labels in any order

Labeled arguments may come in any order, since each one says which parameter it fills: `reduced(off_cents: 200, cents: 1_990)` is the same call as the one before it. Write them in the order that reads best.

#### Punning: a name that matches

When an argument is a name equal to its parameter's name, the name is its own label. `main` binds `units` with `let`, then calls `line_total(4_500, units)`, which means `line_total(4_500, units: units)`. This shorthand is called **punning**. It works from the second argument on: a first argument always fills the first parameter, whatever its name.

#### A call inside a call

An argument can be any expression, such as a sum or another call. An **expression** is a piece of code that gives a value: `2`, `cents / 2` and `half(1_990)` are expressions. In `half(line_total(1_990, units: 2))`, the inner call gives 3980, and `half` receives 3980.

### Method calls on your own kinds

A call can also be written with its first argument in front, followed by a dot. [Section 3.2](/learn/text-and-conditions/#s3-2) showed this **method syntax** on texts, as in `raw.trim`. It works the same way on the kinds you declare yourself ([chapter 4](/learn/kinds/#s4-1)): `lamp.rate()` is `rate(lamp)`. The module `parcels` declares the record kind `Parcel`, and four functions that take a parcel as their first parameter:

```una include="steps/06-methods/src/parcels.una" title="src/parcels.una" verified="check, run"
module parcels

--- A parcel ready to ship.
kind Parcel
  sku: Text
  grams: Int

--- The rate of a parcel, in cents: 790 up to 2 kg, and 1290 above.
pub rate(parcel: Parcel) -> Int = if parcel.grams <= 2_000 then 790 else 1_290

--- The rate of a parcel with a handling fee added.
pub with_fee(parcel: Parcel, fee: Int) -> Int = parcel.rate + fee

--- The line printed on a parcel's label.
pub label(parcel: Parcel) -> Text = "{parcel.sku}, {parcel.grams} g"

--- The SKU as the warehouse writes it. Its name is also the name of a field of `Parcel`.
pub sku(parcel: Parcel) -> Text = "SKU {parcel.sku}"

--- Prints one line for each form of a method call.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Parcel(sku: "LAMP-01", grams: 1_200)
  @console.print("a call: {rate(lamp)}, the same as a method: {lamp.rate()}")
  @console.print("without parentheses: {lamp.rate}")
  @console.print("more arguments: {lamp.with_fee(fee: 50)}")
  @console.print("a chain: {lamp.label.to_upper}")
  @console.print("a field: {lamp.sku}, the function: {lamp.sku()}")
```

`una run .` prints:

```text include="steps/06-methods/expected/output.txt"
a call: 790, the same as a method: 790
without parentheses: 790
more arguments: 840
a chain: LAMP-01, 1200 G
a field: LAMP-01, the function: SKU LAMP-01
```

:::steps
```una include="steps/06-methods/src/parcels.una#main" title="src/parcels.una"
--- Prints one line for each form of a method call.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Parcel(sku: "LAMP-01", grams: 1_200)
  @console.print("a call: {rate(lamp)}, the same as a method: {lamp.rate()}")
  @console.print("without parentheses: {lamp.rate}")
  @console.print("more arguments: {lamp.with_fee(fee: 50)}")
  @console.print("a chain: {lamp.label.to_upper}")
  @console.print("a field: {lamp.sku}, the function: {lamp.sku()}")
```

1. **`lamp.rate()`.** The value before the dot becomes the first argument, without a label: `rate(lamp)`. The checker finds `rate` among the functions the module can call, as for any call.
2. **`lamp.rate`.** A call of one argument may also drop its empty parentheses.
3. **`lamp.with_fee(fee: 50)`.** The other arguments go in the parentheses, with their labels, as in a plain call: `with_fee(lamp, fee: 50)`. The body of `with_fee` uses method syntax too: `parcel.rate + fee`.
4. **`lamp.label.to_upper`.** Calls chain from left to right: `label(lamp)` gives a text, and `to_upper`, the prelude's function from [section 3.2](/learn/text-and-conditions/#s3-2) that writes a text in capital letters, works on that text.
5. **`lamp.sku` and `lamp.sku()`.** `Parcel` has a field `sku`, and the module also has a function `sku`. Without parentheses, the dot reads the field. With parentheses, it calls the function.
:::

Method syntax changes how a call is written, not what it does: the checker treats `lamp.rate` and `rate(lamp)` as the same call, with the same labels and the same types. It reads well where a value goes through steps, `order.parcel.rate`, and where a function answers a question about one value, `parcel.rate`.

### The order of evaluation

To **evaluate** an expression is to work out its value. A call evaluates its arguments first, then runs the function's body. Una evaluates them in a fixed order, so that the same program always does the same thing:

- **Left to right.** The arguments are evaluated in the order you wrote them.
- **Inner calls first.** An argument that is a call is evaluated before the call that receives it: in `half(line_total(1_990, units: 2))`, `line_total` runs before `half`.
- **A record's fields in their declared order.** `Parcel(sku: "LAMP-01", grams: 1_200)` evaluates `sku`, then `grams`, the order the kind declares. Canonical form writes the fields in that order, so the order you read is the order that runs. Write them in another order, and `una check .` reports the line as U7001, with the canonical line in its `Help`:

```text include="steps/07-field-order/expected/rendered.txt#L1-L8"
[U7001] Error: line 24 is not in canonical form
    ╭─[ src/parcels.una:24:1 ]
    │
 24 │   let lamp = Parcel(grams: 1_200, sku: "LAMP-01")
    │ ────────────────────────┬────────────────────────
    │                         ╰────────────────────────── line 24 is not in canonical form
    │
    │ Help: repair 1: rewrite in canonical form, as `una fmt` does; edit src/parcels.una:24:1..25:1 to "  let lamp = Parcel(sku: \"LAMP-01\", grams: 1_200)\n"
```

#### A call that prints stands on its own line

A call of a function that prints may not be an argument. It must be a line of its own, or the value after `let`. Here `pack` prints a line and gives back the SKU it packed:

```una include="steps/08-one-effect/src/packing.una" title="src/packing.una" verified="check, run"
module packing

--- Prints that a parcel is being packed, and gives back its SKU.
pack(sku: Text) -> Text
  uses @console: Console[print]
=
  @console.print("packing {sku}")
  sku

--- Packs two parcels, then says which went first.
pub main() -> Unit
  uses @console: Console[print]
=
  let first = pack("LAMP-01")
  let second = pack("RUG-07")
  @console.print("{first}, then {second}")
```

```text include="steps/08-one-effect/expected/output.txt"
packing LAMP-01
packing RUG-07
LAMP-01, then RUG-07
```

Each call of `pack` stands after a `let`, so the lines it prints come in the order of the lines of `main`. Put a call of `pack` inside `print`, and `una check .` refuses it:

```text include="steps/09-nested-effect/expected/rendered.txt#L1-L6"
[U3013] Error: `pack` has effects or can fail, so it must be the whole expression of a statement or `let`; bind its result with `let` first
    ╭─[ src/packing.una:15:18 ]
    │
 15 │   @console.print(pack("LAMP-01"))
    │                  ───────┬───────
    │                         ╰───────── `pack` has effects or can fail, so it must be the whole expression of a statement or `let`; bind its result with `let` first
```

The message says what to do: bind the result with `let` first, then print it. With this rule, every line that does something outside the program is a line of its own, in the order it runs, and a reader never has to work out which of two effects inside one expression comes first. The same rule holds for a call that can fail, which [chapter 7](/learn/failure/#s7-3) covers.

### How a call behaves

#### The checker matches every argument

Before a program runs, `una check .` matches each argument of each call with one parameter. It reports four kinds of mismatch, each with its own code:

- **A second argument without a label**, U2004, as [Why Una labels arguments](#why-una-labels-arguments) showed.
- **A label that names no parameter**, U2005. The `Help` line lists the parameters still without an argument, which is usually the label you meant:

```text include="steps/03-unknown-label/expected/rendered.txt#L1-L8"
[U2005] Error: `reduced` has no parameter `discount`
    ╭─[ src/lines.una:17:50 ]
    │
 17 │   @console.print("two arguments: {reduced(1_990, discount: 200)}")
    │                                                  ────┬───
    │                                                      ╰───── `reduced` has no parameter `discount`
    │
    │ Help: repair 1: the parameters that no other argument gives are `off_cents`
```

- **A parameter given twice**, U2006. Here the first argument fills `cents` without a label, and the second says `cents:` again:

```text include="steps/04-label-twice/expected/rendered.txt#L1"
[U2006] Error: parameter `cents` of `reduced` is given twice
```

- **Too many or too few arguments**, U2001. A call must give every parameter exactly one argument:

```text include="steps/05-extra-argument/expected/rendered.txt#L1"
[U2001] Error: `half` takes 1 argument, but 2 are given
```

#### A parameter holds the argument's value

Inside the body, a parameter is a plain name, like one bound with `let` ([section 2.1](/learn/numbers/#s2-1)): it holds the argument's value for the whole call. A call gives back its result, and that is all it gives back: the caller's own names keep their values. ([Section 16.2](/learn/memory/#s16-2) shows the one kind of parameter, declared `edit`, that hands a value back to the caller. Every parameter in this chapter is a plain one.)

#### A function may call itself

A body may call the function it belongs to. This is **recursion**: the function does one small part of the work, and calls itself for the rest. `marked_down` takes 10 percent off a price once a week, with the one-line `if` of [section 3.4](/learn/text-and-conditions/#s3-4):

```una include="steps/10-markdowns/src/markdowns.una#marked_down" title="src/markdowns.una"
--- The price after `weeks` weekly markdowns of 10 percent, each rounded down. The function
--- calls itself, with one week fewer, until no week is left.
pub marked_down(cents: Int, weeks: Int) -> Int = if weeks <= 0 then cents else marked_down(cents * 90 / 100, weeks: weeks - 1)
```

```text include="steps/10-markdowns/expected/output.txt"
after 3 weeks: 7290
```

Follow the calls. `marked_down(10_000, weeks: 3)` has weeks left, so it calls `marked_down(9_000, weeks: 2)`, which calls `marked_down(8_100, weeks: 1)`, which calls `marked_down(7_290, weeks: 0)`. That call has no week left, so it gives back 7290, and each call before it gives back that value. Every call has one week fewer, so the calls end. A function that never reaches its stopping case calls itself until the run reaches its limit on the depth of calls, and stops with U6003 ([section 16.4](/learn/memory/#s16-4)).

### When to label, pun or use a method call

:::decide
**Which to use:**

| You want to… | Write |
| --- | --- |
| Call a function of one argument | `half(1_990)`: the label is optional |
| Pass several values | the first without a label, the others labeled: `reduced(1_990, off_cents: 200)` |
| Make the first value clear too | a label on it as well: `reduced(cents: 1_990, off_cents: 200)` |
| Pass a name that matches the parameter | the name alone, from the second argument on: `line_total(4_500, units)` |
| Ask a question about one value, or chain steps on it | method syntax: `lamp.rate`, `lamp.label.to_upper` |
| Use the result of a call that prints | `let` it first, then use the name |
:::

Name parameters for what they mean to a caller: `off_cents` reads well at the call, where `amount2` would not. A good name and a label together make a call explain itself.

### Check yourself: calls

The module `shelves` asks what to order for one shelf:

```una include="steps/11-shelves/src/shelves.una" title="src/shelves.una"
module shelves

--- A shelf of the store: the SKU it holds, and how many units are on it.
kind Shelf
  sku: Text
  on_hand: Int

--- How many units to order so that the shelf holds `target` units again.
pub to_order(shelf: Shelf, target: Int) -> Int = if shelf.on_hand >= target then 0 else target - shelf.on_hand

--- Prints what to order for one shelf, for three targets.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = Shelf(sku: "LAMP-01", on_hand: 6)
  let target = 10
  @console.print("{lamps.to_order(target: 4)}")
  @console.print("{to_order(lamps, target)}")
  @console.print("{lamps.to_order(target: target + 5)}")
```

What does `una run .` print?

:::answer Show the answer
```text include="steps/11-shelves/expected/output.txt"
0
4
9
```

The shelf holds 6 units. `lamps.to_order(target: 4)` is `to_order(lamps, target: 4)`: the shelf already holds 4 or more, so 0. `to_order(lamps, target)` puns `target`, which holds 10: 10 - 6 is 4. `lamps.to_order(target: target + 5)` evaluates its argument first, 15, and 15 - 6 is 9.
:::

`reduced` is declared `reduced(cents: Int, off_cents: Int)`. Which of these calls check: `reduced(off_cents: 5, cents: 300)`, `reduced(300, 5)`, `reduced(300, off: 5)`?

:::answer Show the answer
Only the first. Its arguments are both labeled, so their order does not matter. `reduced(300, 5)` has a second argument without a label, U2004. `reduced(300, off: 5)` names a parameter `reduced` does not have, U2005.
:::

## 6.2 The result of a function: return types, the last line, unused values

### What a result is

A function's **result** is the one value it gives back to its caller. Its type, the **result type** or **return type**, is written in the header after `->`: `half(cents: Int) -> Int` gives back an `Int`. Think of a quote from a mover: you send the rooms and the distance, and you get back one number, the price. The quote form says in advance that you will get a price, not a list of boxes.

In Una, the result is the value of the body. A body of one line gives its value; a body of several lines gives the value of its last line. There is no separate step that says "give this back".

### Why the header states the result type

Every caller depends on the result type. `@console.print(...)` needs a `Text`, `half(...)` needs an `Int`, and `if ships_free(...)` needs a `Bool`. If the type of the result could change with the body, a small change inside one function would break callers in places you never looked. So Una holds every body to its header: the body must give a value of the result type, and the checker says so at the line where it does not. Here `ships_free` is meant to give back a `Bool`, and its body gives back texts:

```text include="steps/13-wrong-type/expected/rendered.txt#L1-L6"
[U2001] Error: `ships_free` returns `Bool`, found `Text`
    ╭─[ src/fees.una:12:62 ]
    │
 12 │ pub ships_free(goods: Int) -> Bool = if goods >= 10_000 then "yes" else "no"
    │                                                              ──┬──
    │                                                                ╰──── `ships_free` returns `Bool`, found `Text`
```

The message names the function and both types: it returns `Bool`, and the checker found `Text`. The marks point at `"yes"`, the value of the wrong type. The same diagnostic follows for `"no"`, the other branch. The callers of `ships_free` are not reported: they rely on the header, which still says `Bool`.

### How to write a body

The module `fees` has a function of each shape a result takes:

```una include="steps/12-results/src/fees.una" title="src/fees.una" verified="check, run"
module fees

--- What a quote says: the charge in cents, and whether the order ships free.
kind Quote
  cents: Int
  free: Bool

--- Half of an amount, rounded down. A body of one line, in the short form.
pub half(cents: Int) -> Int = cents / 2

--- Whether an order of `goods` cents ships free. The result is a `Bool`.
pub ships_free(goods: Int) -> Bool = goods >= 10_000

--- The rate of a parcel of `grams` grams: 450 cents for the first kilogram, and 250 more for
--- each kilogram or part of one after it. A body of several lines, in the long form.
pub parcel_rate(grams: Int) -> Int
=
  let kilos = (grams + 999) / 1_000
  let extra = kilos - 1
  450 + extra * 250

--- The quote for an order. The result is a value of a kind of this module.
pub quote(goods: Int, grams: Int) -> Quote
=
  let free = ships_free(goods)
  let cents = if free then 0 else parcel_rate(grams)
  Quote(cents, free)

--- Prints a quote. It is called for what it prints, so its result is `Unit`.
pub print_quote(quote: Quote) -> Unit
  uses @console: Console[print]
=
  @console.print("charge: {quote.cents} cents")
  @console.print("ships free: {quote.free}")

--- Prints a few results.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("half of 1990: {half(1_990)}")
  @console.print("500 g: {parcel_rate(500)}, 2300 g: {parcel_rate(2_300)}")
  print_quote(quote(4_500, grams: 2_300))
  print_quote(quote(12_000, grams: 2_300))
```

`una run .` prints:

```text include="steps/12-results/expected/output.txt"
half of 1990: 995
500 g: 450, 2300 g: 950
charge: 950 cents
ships free: false
charge: 0 cents
ships free: true
```

#### The short form: one line

`half` and `ships_free` have a body of one line, written after `=` on the header's line. This is the **short form**, as in [section 1.4](/learn/hello/#s1-4). The expression after `=` is the result: `cents / 2` is an `Int`, and `goods >= 10_000` is a `Bool`. A long expression stays on one line: canonical form has no limit on the width of a line.

#### The long form: a block, whose last line is the result

`parcel_rate` needs two names on the way to its result, so it is written in the **long form**: the header, `=` alone on its line, then the body, indented two spaces. A body of several lines is a **block**. Its lines run in order, from the top, and the value of its last line is the value of the block, and so the function's result:

```una include="steps/12-results/src/fees.una#parcel_rate" title="src/fees.una"
--- The rate of a parcel of `grams` grams: 450 cents for the first kilogram, and 250 more for
--- each kilogram or part of one after it. A body of several lines, in the long form.
pub parcel_rate(grams: Int) -> Int
=
  let kilos = (grams + 999) / 1_000
  let extra = kilos - 1
  450 + extra * 250
```

The first two lines are **statements**: lines that do something, here naming a value with `let`, rather than giving the block's value. `kilos` is the number of started kilograms: adding 999 grams before dividing by 1000 turns 1 to 1000 grams into one kilogram, and 1001 to 2000 into two. The last line, `450 + extra * 250`, is the rate.

#### Clauses between the header and `=`

A header may have **clauses**: lines under its first line that say more about the function, such as `requires` and `ensures` from [chapter 5](/learn/contracts/#s5-1), and `uses` from [chapter 1](/learn/hello/#s1-5). They come in a fixed order, `requires`, then `ensures`, then `uses`, then the clauses of later chapters, each indented two spaces, before `=`. A function with any clause takes the long form, even when its body is one line. A header with its clauses in another order does not check (U0102).

#### A result of a kind of your own

`quote` gives back a `Quote`, a record kind of the module. Its last line builds the record, `Quote(cents, free)`, with both fields punned: the names `cents` and `free` match the fields. Punning works on a record's first field too, unlike on a function's first parameter: in a record, every field is matched by its name, and a name equal to a field fills that field. Any type can be a result, a kind of yours included, and a caller reads its fields: `quote.cents`.

#### A result of `Unit`

`print_quote` is called for what it prints, not for a value, so its result type is `Unit`, as `main`'s is. `Unit` has one value, which carries no information. A block of type `Unit` may end with a call of type `Unit`, such as a `print`.

### How the checker treats a result

#### The last line must be a value

A block's value is its last line, so the last line cannot be a `let`: a `let` names a value, and gives none. Bind the rate to a name on the last line of `parcel_rate`, and `una check .` reports:

```text include="steps/14-let-last/expected/rendered.txt#L1-L6"
[U0101] Error: a block cannot end with `let`; its last line is its value
    ╭─[ src/fees.una:20:3 ]
    │
 20 │   let rate = 450 + extra * 250
    │   ─┬─
    │    ╰─── a block cannot end with `let`; its last line is its value
```

The repair is to write the value itself, `450 + extra * 250`, on the last line.

#### Una has no `return`

Many languages end a function with `return` and a value. Una has no `return`: the last line is always the result, so a function has one place where its result is made. Write `return` out of habit, and the message says so:

```text include="steps/15-return/expected/rendered.txt#L1-L6"
[U0103] Error: `return` is not a keyword in Una; the last expression is the result
    ╭─[ src/fees.una:20:3 ]
    │
 20 │   return 450 + extra * 250
    │   ───┬──
    │      ╰──── `return` is not a keyword in Una; the last expression is the result
```

#### A value nobody uses

A statement must not give a value that is then thrown away. A call of `half` on a line of its own, whose result nobody names, is a mistake the checker catches:

```diff include="steps/12-results..steps/16-unused:src/fees.una" context="1"
--- a/src/fees.una
+++ b/src/fees.una
@@ -39,2 +39,3 @@
 =
+  half(1_990)
   @console.print("half of 1990: {half(1_990)}")
```

```text include="steps/16-unused/expected/rendered.txt#L1-L6"
[U2011] Error: this statement has type `Int`, and only `Unit` values can be discarded; bind the value with `let`
    ╭─[ src/fees.una:40:3 ]
    │
 40 │   half(1_990)
    │   ─────┬─────
    │        ╰─────── this statement has type `Int`, and only `Unit` values can be discarded; bind the value with `let`
```

The message says what to do: bind the value with `let`, or remove the line. Only a statement of type `Unit`, such as a `print` or a call of `print_quote`, may stand alone, since it has no value to lose. A call whose result is dropped is almost always a slip: the work was done, and its answer went nowhere.

#### A caller knows the result only from the header

When the verifier ([chapter 5](/learn/contracts/#s5-4)) proves something about a caller, it knows a call's result only from the callee's header: its type, and what its `ensures` clauses promise. It never reads the body. In the module `rates`, `half` requires an amount that is not negative, and `main` passes it the result of `base_rate`:

```una include="steps/18-promise/src/rates.una" title="src/rates.una" verified="check, run"
module rates

--- The rate of a parcel of `grams` grams, in cents: 790 up to 2 kg, and 1290 above.
pub base_rate(grams: Int) -> Int
  ensures result >= 790
=
  if grams <= 2_000 then 790 else 1_290

--- Half of an amount, rounded down. The amount must not be negative.
pub half(cents: Int) -> Int
  requires cents >= 0
=
  cents / 2

--- Prints the weekend rate of a light parcel: half the rate.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("weekend rate: {half(base_rate(300))}")
```

```text include="steps/18-promise/expected/output.txt"
weekend rate: 395
```

`base_rate` promises `result >= 790`, so the verifier proves that its result is not negative, and the call of `half` checks. Now take the promise away, and keep the same body, on one line, since the function now has no clause:

```diff include="steps/18-promise..steps/19-no-promise:src/rates.una" context="1"
--- a/src/rates.una
+++ b/src/rates.una
@@ -3,6 +3,3 @@
 --- The rate of a parcel of `grams` grams, in cents: 790 up to 2 kg, and 1290 above.
-pub base_rate(grams: Int) -> Int
-  ensures result >= 790
-=
-  if grams <= 2_000 then 790 else 1_290
+pub base_rate(grams: Int) -> Int = if grams <= 2_000 then 790 else 1_290
 
```

```text include="steps/19-no-promise/expected/rendered.txt#L1-L10"
[U5001] Error: precondition `base_rate(300) >= 0` of this call is refuted
    ╭─[ src/rates.una:16:34 ]
    │
  8 │   requires cents >= 0
    │            ─────┬────
    │                 ╰────── requires clause
    │
 16 │   @console.print("weekend rate: {half(base_rate(300))}")
    │                                  ──────────┬─────────
    │                                            ╰─────────── precondition `base_rate(300) >= 0` of this call is refuted
```

The body still gives back 790 for 300 grams, and still never gives back a negative number. But the header now says only `-> Int`, and an `Int` may be negative, so the verifier cannot prove `base_rate(300) >= 0`, the precondition of `half` with the call in place. This is the rule that keeps a large program checkable: each function is proved once, against its own header, and its callers rely on that header alone. A change inside a body cannot break a proof elsewhere, as long as the header holds. When callers need a fact about a result, the function's header promises it with `ensures`.

### Short or long, and when to promise more

:::decide
**Which to use:**

| The function… | Write |
| --- | --- |
| Has no clauses, and its result is one expression | the short form: `half(cents: Int) -> Int = cents / 2` |
| Needs a few named steps to reach its result | the long form, with a block whose last line is the result |
| Gives back several values that belong together | a record kind as its result, such as `Quote` |
| Is called for what it does, not for a value | the result type `Unit` |
| Gives a result its callers need a fact about, such as "never negative" | an `ensures` clause that promises it |
:::

`una fmt .` writes the short or the long form for you: it follows from the clauses and the body, not from taste ([section 18.1](/learn/tools/#s18-1)).

### Check yourself: results

You add one line at the end of `print_quote`, so that it reads:

```una include="steps/17-unit-last/src/fees.una#print_quote" title="src/fees.una"
--- Prints a quote. It is called for what it prints, so its result is `Unit`.
pub print_quote(quote: Quote) -> Unit
  uses @console: Console[print]
=
  @console.print("charge: {quote.cents} cents")
  @console.print("ships free: {quote.free}")
  quote.cents
```

Does `una check .` pass?

:::answer Show the answer
No:

```text include="steps/17-unit-last/expected/rendered.txt#L1-L6"
[U2001] Error: `print_quote` returns `Unit`, found `Int`
    ╭─[ src/fees.una:35:3 ]
    │
 35 │   quote.cents
    │   ─────┬─────
    │        ╰─────── `print_quote` returns `Unit`, found `Int`
```

The last line of a block is its value, and so the function's result. `print_quote` promises `Unit`, and its last line is now `quote.cents`, an `Int`. Remove the line, and the block ends with a `print` again, whose type is `Unit`.
:::

## 6.3 What a header says: `pub`, private functions and inferred headers

### What `pub` means

A program can have many modules, and one module can call the functions of another, as [chapter 11](/learn/packages/#s11-2) shows. `pub`, short for public, decides which functions it may call:

- A function that starts with `pub` is **public**: any module may call it.
- A function without `pub` is **private**: only the functions of its own module may call it.

Think of a shop. The counter is public: customers walk up and ask for what is on the menu. The back room is private: the staff use it to get the work done, and no customer goes in. A module's public functions are its counter, and its private functions are its back room.

### Why a public header must say everything

The caller of a public function may live in another module, written by someone else, years later. That caller sees the header, not the body. So the header of a `pub` function states everything a caller relies on:

- the type of every parameter and of the result, as every header does;
- what the function may do outside the program, with `uses`, such as print;
- the ways it can fail, with `fails`, which [chapter 7](/learn/failure/#s7-2) covers.

If a public header could leave out its `uses`, a function that looks like a pure computation could print, write files or send data, and nothing at the call would show it. So a `pub` function that prints without a `uses` line does not check. A private function is different: every one of its callers is in the same file, in view of whoever changes it. So Una lets a private function leave out its `uses` line, and works it out from the body.

### How to write a public and a private function

`pub` goes first, before the function's name: `pub to_order(on_hand: Int, target: Int) -> Int`. A private function leaves it out: `show(sku: Text, units: Int) -> Unit`. Everything else in the header is written as for any function. `pub` goes on kinds too, with the same meaning: a public kind may be used by other modules.

`main` must be public: `una run .` starts it from outside its module, and refuses a module without `pub main() -> Unit` ([section 1.3](/learn/hello/#s1-3)).

### A private function's inferred `uses`

The module `restock` prints a restock list. It has a public function that computes, and a private function that prints, without a `uses` line:

:::steps
```una include="steps/20-inferred/src/restock.una" title="src/restock.una" verified="check, run"
module restock

--- How many units to order so that the shelf holds `target` again, and none when it already
--- does.
pub to_order(on_hand: Int, target: Int) -> Int = if on_hand >= target then 0 else target - on_hand

-- Prints one line of the restock list. It is private and has no `uses` line: the checker
-- infers it from the body.
show(sku: Text, units: Int) -> Unit = @console.print("{sku}: order {units}")

--- Prints the restock list of two SKUs.
pub main() -> Unit
  uses @console: Console[print]
=
  show("LAMP-01", units: to_order(3, target: 10))
  show("RUG-07", units: to_order(12, target: 10))
```

1. **`to_order`.** A public function with no `uses` line: it is **pure**, as [section 1.5](/learn/hello/#s1-5) says, so it may only compute. It never orders fewer than none.
2. **`show(sku: Text, units: Int) -> Unit = @console.print(…)`.** A private function that prints, with no `uses` line in its header, written in the short form.
3. **`main` calls `show`.** `main` declares the console, so `show`, called from it, can be given the console too.
:::

`una run .` prints:

```text include="steps/20-inferred/expected/output.txt"
LAMP-01: order 7
RUG-07: order 0
```

The checker has filled in what `show` left out. It sees that the body uses `@console.print`, and that every caller of `show` holds the console. Working out a missing part from the code around it is called **inference**, and the header it gives is the **inferred** header. The same holds for `fails`: a private function may leave it out, and the checker infers it, as [chapter 7](/learn/failure/#s7-2) shows.

### Reading a whole header: `una contract`

`una contract` prints a function's whole header, as a caller may rely on it. You name the function by its module and its name, joined by a dot:

```sh
una contract restock.show
```

```text include="steps/20-inferred/expected/commands/contract-show.txt#L2-L3"
show(sku: Text, units: Int) -> Unit
  uses @console: Console[print] -- inferred
```

The part the checker inferred is marked `-- inferred`, so a reviewer sees that `show` prints, even though its source does not say so. `una contract` also prints a function's doc comment, the `---` lines above it:

```sh
una contract restock.to_order
```

```text include="steps/20-inferred/expected/commands/contract-to-order.txt#L2-L4"
--- How many units to order so that the shelf holds `target` again, and none when it already
--- does.
pub to_order(on_hand: Int, target: Int) -> Int
```

This is what an editor, a reviewer or an agent sees of the function without reading its body: what it is for, what it takes and what it gives back. That is why every public function in this book has a doc comment.

### Authority in the build report

What a function may do outside the program is its **authority**. The build report, `una report .`, lists the authority of every function of the package, declared or inferred, in its `authority:` part:

```text include="steps/20-inferred/expected/commands/report.txt#L8-L10"
authority:
  restock.main (pub): @console: Console[print]
  restock.show (private, inferred): @console: Console[print]
```

`restock.main` is public and declares the console. `restock.show` is private, and its console is inferred. `to_order` is not listed: it has no authority, and can only compute. A reviewer reads the effects of a whole package in one place, without opening a body.

### How inference behaves

#### Inference follows the callers

A private function's `uses` come from its body, and its callers must have them to give. Here a public function, `print_list`, calls `show` but declares no `uses`:

```diff include="steps/20-inferred..steps/21-public-caller:src/restock.una" context="1"
--- a/src/restock.una
+++ b/src/restock.una
@@ -11,2 +11,8 @@
 --- Prints the restock list of two SKUs.
+pub print_list() -> Unit
+=
+  show("LAMP-01", units: to_order(3, target: 10))
+  show("RUG-07", units: to_order(12, target: 10))
+
+--- Prints the restock list.
 pub main() -> Unit
@@ -14,3 +20,2 @@
 =
-  show("LAMP-01", units: to_order(3, target: 10))
-  show("RUG-07", units: to_order(12, target: 10))
+  print_list()
```

```text include="steps/21-public-caller/expected/rendered.txt#L1-L8"
[U3001] Error: no caller of `show` binds `@console`, so its capability cannot be inferred
   ╭─[ src/restock.una:9:39 ]
   │
 9 │ show(sku: Text, units: Int) -> Unit = @console.print("{sku}: order {units}")
   │                                       ────┬───
   │                                           ╰───── no caller of `show` binds `@console`, so its capability cannot be inferred
   │
   │ Help: repair 1: declare `uses @console: <capability>[print]` in the header; this states authority its callers are already charged for
```

The error is at the use of `@console` in `show`: no caller of `show` holds the console, so the checker has none to give it. The repair that fits is to give `print_list`, the public function that prints through `show`, the line `uses @console: Console[print]`.

#### Nothing is inferred for a public function

A `pub` function writes its `uses` itself. Make `show` public, and it no longer checks:

```text include="steps/22-public-show/expected/rendered.txt#L1-L6"
[U3004] Error: `@console` is used here, but this code declares no `uses`, so it is pure
   ╭─[ src/restock.una:8:43 ]
   │
 8 │ pub show(sku: Text, units: Int) -> Unit = @console.print("{sku}: order {units}")
   │                                           ────┬───
   │                                               ╰───── `@console` is used here, but this code declares no `uses`, so it is pure
```

"This code declares no `uses`, so it is pure": a public header without `uses` promises a pure function, and the body breaks the promise. So inference saves lines inside a module, where every caller is in view, and never hides an effect from another module.

#### Types are never inferred

Inference covers `uses` and `fails`, and never a type. Every parameter and every result of every function, public or private, has its type written. Leave out the result type, and the header does not parse:

```text include="steps/23-no-result-type/expected/rendered.txt#L1"
[U0101] Error: unexpected `=`, expected `->` and the result type
```

### When a function should print

Most functions should not print: they take values and give back a value. Such a pure function does the same thing every time you call it with the same arguments, so an example can test it ([section 14.1](/learn/testing/#s14-1)). Print in `main`, or in a few small functions whose only job is to print, and give each of them its `uses` line. The packing slip of [chapter 2](/learn/numbers/#s2-4) has that shape: pure functions build the lines, and `main` prints them.

### Public or private

:::decide
**Which to use:**

| The function… | Make it |
| --- | --- |
| Is part of what the module offers other modules | `pub`, with a doc comment and its whole header |
| Is called by `una run` | `pub`: `main` must be public |
| Is a helper used only inside its module | private |
| Is private and prints | private, with its `uses` written, as this book does, or left to inference |
:::

Start private, and make a function `pub` when another module needs it. A private function can change freely, since all its callers are in view. A public one is a promise: a change to its header can break callers you cannot see. This book writes the `uses` line on every function that prints, private ones included, so that every header says what its function does; the inferred header is there for the helpers where you choose to leave it out.

### Check yourself: authority

You make `to_order` private, and add a private function that prints a heading, with no `uses` line, which `main` calls first:

```una include="steps/24-heading/src/restock.una" title="src/restock.una"
module restock

-- How many units to order so that the shelf holds `target` again, and none when it already
-- does.
to_order(on_hand: Int, target: Int) -> Int = if on_hand >= target then 0 else target - on_hand

-- Prints the heading of the list.
heading() -> Unit = @console.print("Restock list")

-- Prints one line of the restock list. It is private and has no `uses` line: the checker
-- infers it from the body.
show(sku: Text, units: Int) -> Unit = @console.print("{sku}: order {units}")

--- Prints the restock list of two SKUs.
pub main() -> Unit
  uses @console: Console[print]
=
  heading()
  show("LAMP-01", units: to_order(3, target: 10))
  show("RUG-07", units: to_order(12, target: 10))
```

Which functions does the `authority:` part of `una report .` list now, and how is each marked?

:::answer Show the answer
```text include="steps/24-heading/expected/commands/report.txt#L8-L11"
authority:
  restock.heading (private, inferred): @console: Console[print]
  restock.main (pub): @console: Console[print]
  restock.show (private, inferred): @console: Console[print]
```

Three functions print: `heading`, `main` and `show`. `main` is public and declares its console. `heading` and `show` are private and leave their `uses` out, so theirs are inferred from `main`, which calls both. `to_order` is private now, but it still only computes, so it has no authority and is not listed.
:::

## 6.4 Day-to-day: shipping quotes

### What the program must do

Every order needs a shipping charge before it can be paid. The charge depends on the parcel's weight and on how far it travels, large orders within the country ship for free, and this weekend one order gets half off its shipping. The report at the end of the day lists the charge of each order.

Each rule is a function, and each function's header states what its callers may rely on. The program is one module, `shipping`, and each part uses one idea of this chapter:

- **The kinds** give an order and its parcel names, so that the functions take one value each, and method calls read well ([section 6.1](#s6-1)).
- **The rates** promise facts about their results, which their callers need ([section 6.2](#s6-2)).
- **The quote** puts the rates together, with method calls and one `if`.
- **The report** keeps the printing in two functions, and everything else pure ([section 6.3](#s6-3)).

### The kinds: zones, parcels and orders

```una include="day-to-day/src/shipping.una#Zone..Order" title="day-to-day/src/shipping.una" caption="the kinds"
--- How far a parcel travels: within the country, to a neighboring country, or farther.
kind Zone = Home | Neighbor | World

--- A parcel: its weight in grams and the zone it ships to.
kind Parcel
  grams: Int
  zone: Zone

--- An order of the day: its number, the price of its goods in cents, and its parcel.
kind Order
  number: Int
  goods: Int
  parcel: Parcel
```

`Zone` is a sum kind ([section 4.2](/learn/kinds/#s4-2)): a parcel ships within the country, to a neighboring country, or farther. A `Parcel` is a record of its weight and its zone, and an `Order` holds its number, the price of its goods in cents, and its parcel. With these kinds, a function about an order takes one argument, the order, and reads what it needs from it.

### The rates

```una include="day-to-day/src/shipping.una#base_rate..rate" title="day-to-day/src/shipping.una" caption="the rates"
--- The rate for `grams` grams within the country, in cents: 790 up to 2 kg, and 250 more
--- for each kilogram or part of one above 2 kg.
pub base_rate(grams: Int) -> Int
  requires grams > 0
  ensures result >= 790
=
  let extra_kilos = (grams - 2_000 + 999) / 1_000
  if grams <= 2_000 then 790 else 790 + extra_kilos * 250

--- What a zone adds to the rate, in cents.
pub surcharge(zone: Zone) -> Int
  ensures result >= 0
=
  when zone
    is Home -> 0
    is Neighbor -> 600
    is World -> 1_800

--- The rate of a parcel: the rate for its weight, and the surcharge of its zone.
pub rate(parcel: Parcel) -> Int
  requires parcel.grams > 0
  ensures result >= 790
=
  base_rate(parcel.grams) + parcel.zone.surcharge
```

`base_rate` gives the rate for a weight: 790 cents up to 2 kg, and 250 more for each kilogram or part of one above that. Its first line names `extra_kilos`, the started kilograms above 2 kg, and its last line, a one-line `if`, is the result. `requires grams > 0` rules out an empty parcel, and `ensures result >= 790` promises the lowest rate to every caller.

`surcharge` takes a zone apart with `when` ([section 4.3](/learn/kinds/#s4-3)), one arm per zone. Its `ensures result >= 0` looks obvious from the body, and it matters all the same: the callers of `surcharge` see its header, not its body.

`rate` puts the two together for a parcel. Its last line calls `base_rate` with a plain call, and `surcharge` with method syntax: `parcel.zone.surcharge` reads the zone of the parcel, then its surcharge. The verifier proves `rate`'s promise from the headers alone: at least 790 from `base_rate`, and at least 0 from `surcharge`. It also proves the precondition of `base_rate` at the call, from `rate`'s own `requires parcel.grams > 0`.

### The quote

```una include="day-to-day/src/shipping.una#ships_free..quote" title="day-to-day/src/shipping.una" caption="the quote"
--- Whether an order ships free: 10000 cents of goods or more, within the country.
pub ships_free(order: Order) -> Bool = order.goods >= 10_000 and order.parcel.zone is Home

--- What shipping costs for an order, in cents.
pub quote(order: Order) -> Int
  requires order.parcel.grams > 0
  ensures result >= 0
=
  if order.ships_free then 0 else order.parcel.rate
```

`ships_free` answers a question about an order with a `Bool`: 10000 cents of goods or more, and a parcel that stays in the country. The `is` test of [section 4.2](/learn/kinds/#s4-2) checks the zone.

`quote` reads as the rule itself: if the order ships free, nothing, else the rate of its parcel. Both calls are method calls, `order.ships_free` and `order.parcel.rate`. Its `requires` passes the weight rule on to its own callers, and its `ensures result >= 0` follows from `rate`'s promise: 0 when the order ships free, at least 790 otherwise.

### The weekend offer

```una include="day-to-day/src/shipping.una#weekend_price" title="day-to-day/src/shipping.una" caption="the offer"
--- The weekend offer: half the charge, rounded up to a whole cent. It never raises the charge.
pub weekend_price(charge: Int) -> Int
  requires charge >= 0
  ensures result >= 0 and result <= charge
=
  (charge + 1) / 2
```

`weekend_price` halves a charge, rounding up to a whole cent: adding 1 before dividing by 2 rounds a half cent up. Its header promises two facts: the price is never negative, and never more than the charge. The verifier proves both for every charge that is not negative, the only charges a quote gives.

### The report

```una include="day-to-day/src/shipping.una#money..main" title="day-to-day/src/shipping.una" caption="the report" verified="check, run"
--- Cents as an amount with two decimals, for an amount that is not negative.
pub money(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"

--- The line of the report for one order.
pub report_line(order: Order, charge: Int) -> Text = if charge == 0 then "order {order.number}: ships free" else "order {order.number}: {money(charge)}"

--- Prints one line of the report.
show(order: Order, charge: Int) -> Unit
  uses @console: Console[print]
=
  @console.print(report_line(order, charge))

--- Prints the shipping report of the orders of the day.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Order(number: 1042, goods: 3_980, parcel: Parcel(grams: 1_200, zone: Home))
  show(lamp, charge: lamp.quote)
  let desk = Order(number: 1043, goods: 15_900, parcel: Parcel(grams: 24_000, zone: Home))
  show(desk, charge: desk.quote)
  let rug = Order(number: 1044, goods: 4_500, parcel: Parcel(grams: 3_200, zone: World))
  show(rug, charge: rug.quote)
  let chair = Order(number: 1045, goods: 4_500, parcel: Parcel(grams: 3_200, zone: World))
  show(chair, charge: weekend_price(chair.quote))
  let mugs = Order(number: 1046, goods: 2_500, parcel: Parcel(grams: 800, zone: Neighbor))
  show(mugs, charge: mugs.quote)
```

`money` writes cents as an amount with two decimals, and `report_line` chooses the text of one line with a one-line `if`. Both are pure, so examples can check them. `show` prints one line, and is private. `main` builds five orders and prints a line for each.

Every call in `main` that prints stands on a line of its own, and every argument only computes: `lamp.quote` and `weekend_price(chair.quote)` are evaluated before `show` runs. `weekend_price(chair.quote)` checks because of a header: `weekend_price` requires a charge that is not negative, and the verifier knows that `chair.quote` is not negative from `quote`'s `ensures`. The promise of one function is what makes the call of the next one safe.

### Running it

In the `day-to-day` directory:

```sh
una check .
una run .
```

`una check .` prints nothing, and `una run .` prints the report shown in [What you'll build](#what-youll-build). Order 1044 ships 3200 g abroad: 790 for the first 2 kg, 500 for two started kilograms above them, and 1800 for the zone, 30.90 in all. Order 1045 is the same parcel on the weekend: half of 3090, 15.45.

`una contract shipping.quote` prints the header that every caller of `quote` relies on, with its doc comment:

```text include="day-to-day/expected/commands/contract-quote.txt#L2-L5"
--- What shipping costs for an order, in cents.
pub quote(order: Order) -> Int
  requires order.parcel.grams > 0
  ensures result >= 0
```

> [!SECURITY]
> Of the ten functions in the file, only `show` and `main` touch the console, and both say so in their headers. Every other function has no `uses` line, so it cannot have an effect of any kind: a change to a rate cannot start printing, writing files or sending data without a change to its header that a reviewer sees.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/shipping.una" title="day-to-day/src/shipping.una" caption="the whole program" verified="check, run, test"
module shipping

-- Shipping quotes: what each order of the day costs to ship, by weight and zone.

--- How far a parcel travels: within the country, to a neighboring country, or farther.
kind Zone = Home | Neighbor | World

--- A parcel: its weight in grams and the zone it ships to.
kind Parcel
  grams: Int
  zone: Zone

--- An order of the day: its number, the price of its goods in cents, and its parcel.
kind Order
  number: Int
  goods: Int
  parcel: Parcel

--- The rate for `grams` grams within the country, in cents: 790 up to 2 kg, and 250 more
--- for each kilogram or part of one above 2 kg.
pub base_rate(grams: Int) -> Int
  requires grams > 0
  ensures result >= 790
=
  let extra_kilos = (grams - 2_000 + 999) / 1_000
  if grams <= 2_000 then 790 else 790 + extra_kilos * 250

--- What a zone adds to the rate, in cents.
pub surcharge(zone: Zone) -> Int
  ensures result >= 0
=
  when zone
    is Home -> 0
    is Neighbor -> 600
    is World -> 1_800

--- The rate of a parcel: the rate for its weight, and the surcharge of its zone.
pub rate(parcel: Parcel) -> Int
  requires parcel.grams > 0
  ensures result >= 790
=
  base_rate(parcel.grams) + parcel.zone.surcharge

--- Whether an order ships free: 10000 cents of goods or more, within the country.
pub ships_free(order: Order) -> Bool = order.goods >= 10_000 and order.parcel.zone is Home

--- What shipping costs for an order, in cents.
pub quote(order: Order) -> Int
  requires order.parcel.grams > 0
  ensures result >= 0
=
  if order.ships_free then 0 else order.parcel.rate

--- The weekend offer: half the charge, rounded up to a whole cent. It never raises the charge.
pub weekend_price(charge: Int) -> Int
  requires charge >= 0
  ensures result >= 0 and result <= charge
=
  (charge + 1) / 2

--- Cents as an amount with two decimals, for an amount that is not negative.
pub money(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"

--- The line of the report for one order.
pub report_line(order: Order, charge: Int) -> Text = if charge == 0 then "order {order.number}: ships free" else "order {order.number}: {money(charge)}"

--- Prints one line of the report.
show(order: Order, charge: Int) -> Unit
  uses @console: Console[print]
=
  @console.print(report_line(order, charge))

--- Prints the shipping report of the orders of the day.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Order(number: 1042, goods: 3_980, parcel: Parcel(grams: 1_200, zone: Home))
  show(lamp, charge: lamp.quote)
  let desk = Order(number: 1043, goods: 15_900, parcel: Parcel(grams: 24_000, zone: Home))
  show(desk, charge: desk.quote)
  let rug = Order(number: 1044, goods: 4_500, parcel: Parcel(grams: 3_200, zone: World))
  show(rug, charge: rug.quote)
  let chair = Order(number: 1045, goods: 4_500, parcel: Parcel(grams: 3_200, zone: World))
  show(chair, charge: weekend_price(chair.quote))
  let mugs = Order(number: 1046, goods: 2_500, parcel: Parcel(grams: 800, zone: Neighbor))
  show(mugs, charge: mugs.quote)

example "a parcel up to 2 kg ships at the lowest rate"
  do base_rate(2_000)
  expect result == 790

example "each started kilogram above 2 kg adds 250 cents"
  do base_rate(3_200)
  expect result == 1_290

example "the rest of the world adds 1800 cents"
  do surcharge(World)
  expect result == 1_800

example "a large order within the country ships free"
  do quote(Order(number: 1, goods: 15_900, parcel: Parcel(grams: 24_000, zone: Home)))
  expect result == 0

example "a large order abroad pays shipping"
  do quote(Order(number: 2, goods: 15_900, parcel: Parcel(grams: 24_000, zone: Neighbor)))
  expect result == 6_890

example "the weekend offer rounds up to a whole cent"
  do weekend_price(3_091)
  expect result == 1_546

example "the weekend offer of nothing is nothing"
  do weekend_price(0)
  expect result == 0

example "an amount keeps its zero cents"
  do money(705)
  expect result == "7.05"

example "a free order says so"
  do report_line(Order(number: 1043, goods: 15_900, parcel: Parcel(grams: 24_000, zone: Home)), charge: 0)
  expect result == "order 1043: ships free"
```

## 6.5 Testing it

### Each rule at its edges

Each example calls one pure function and states its result, in the form of [section 1.7](/learn/hello/#s1-7). The first ones test the rates at their edges: the last weight at the lowest rate, the first weights of a started kilogram above it, and the far zone:

```una include="day-to-day/src/shipping.una#L88-L98" title="day-to-day/src/shipping.una" caption="the rates"
example "a parcel up to 2 kg ships at the lowest rate"
  do base_rate(2_000)
  expect result == 790

example "each started kilogram above 2 kg adds 250 cents"
  do base_rate(3_200)
  expect result == 1_290

example "the rest of the world adds 1800 cents"
  do surcharge(World)
  expect result == 1_800
```

### Results built from other results

The quotes are the results the report depends on. One example ships a large order free within the country; the next sends the same order to a neighboring country, where it pays 6890 cents: 6290 for 24 kg and 600 for the zone. Each example builds its order in place, as the argument of `quote`:

```una include="day-to-day/src/shipping.una#L100-L106" title="day-to-day/src/shipping.una" caption="the quotes"
example "a large order within the country ships free"
  do quote(Order(number: 1, goods: 15_900, parcel: Parcel(grams: 24_000, zone: Home)))
  expect result == 0

example "a large order abroad pays shipping"
  do quote(Order(number: 2, goods: 15_900, parcel: Parcel(grams: 24_000, zone: Neighbor)))
  expect result == 6_890
```

### The offer and the report

The weekend offer has an example for its rounding, and one for a charge of nothing. `money` and `report_line` each have one for the case that is easiest to get wrong, an amount with a zero in its cents and an order that ships free:

```una include="day-to-day/src/shipping.una#L108-L122" title="day-to-day/src/shipping.una" caption="the offer and the report"
example "the weekend offer rounds up to a whole cent"
  do weekend_price(3_091)
  expect result == 1_546

example "the weekend offer of nothing is nothing"
  do weekend_price(0)
  expect result == 0

example "an amount keeps its zero cents"
  do money(705)
  expect result == "7.05"

example "a free order says so"
  do report_line(Order(number: 1043, goods: 15_900, parcel: Parcel(grams: 24_000, zone: Home)), charge: 0)
  expect result == "order 1043: ships free"
```

The examples and the `ensures` clauses do different jobs. `ensures result >= 0 and result <= charge` is proved for every charge, but it does not say which value `weekend_price` gives back. The examples fix exact values, 1546 and 0, for two cases. The examples leave out `show` and `main`, the two functions that print: they only print what the tested functions give back.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L12"
example shipping "a parcel up to 2 kg ships at the lowest rate" ... ok
example shipping "each started kilogram above 2 kg adds 250 cents" ... ok
example shipping "the rest of the world adds 1800 cents" ... ok
example shipping "a large order within the country ships free" ... ok
example shipping "a large order abroad pays shipping" ... ok
example shipping "the weekend offer rounds up to a whole cent" ... ok
example shipping "the weekend offer of nothing is nothing" ... ok
example shipping "an amount keeps its zero cents" ... ok
example shipping "a free order says so" ... ok

9 examples: 9 passed, 0 failed
```

## 6.6 Common mistakes

Each mistake is a small change to `day-to-day/src/shipping.una`, followed by what `una check .` reports.

### A second argument without its label (U2004)

:::mistake
Pass the charge without its label:

```diff include="day-to-day..mistakes/1:src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -77,3 +77,3 @@
   let lamp = Order(number: 1042, goods: 3_980, parcel: Parcel(grams: 1_200, zone: Home))
-  show(lamp, charge: lamp.quote)
+  show(lamp, lamp.quote)
   let desk = Order(number: 1043, goods: 15_900, parcel: Parcel(grams: 24_000, zone: Home))
```

```text include="mistakes/1/expected/rendered.txt#L1,L8"
[U2004] Error: argument 2 of `show` needs a label; only the first argument may go without one
    │ Help: repair 1: label it `charge`; edit src/shipping.una:78:14..78:24 to "charge: lamp.quote"
```

*Why:* in many languages arguments are matched by their place, so this habit comes first. In Una only the first argument may go without a label. The message names the argument by its place, 2, and the marks point at it, `lamp.quote`: a call, not the name `charge`, so punning does not apply.

*Fix:* write `charge: lamp.quote`, the label the `Help` line names. The repair is an exact edit, which `una fix .` applies. See [U2004](/docs/errors/U2004/).
:::

### Branches of two types (U2001)

:::mistake
Give back the number itself when the order does not ship free:

```diff include="day-to-day..mistakes/2:src/shipping.una" context="0"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -65 +65 @@
-pub report_line(order: Order, charge: Int) -> Text = if charge == 0 then "order {order.number}: ships free" else "order {order.number}: {money(charge)}"
+pub report_line(order: Order, charge: Int) -> Text = if charge == 0 then "order {order.number}: ships free" else charge
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U2001] Error: `report_line` returns `Text`, found `Int`
```

*Why:* both branches of the `if` give the function's result, which is a `Text`, and `charge` is an `Int`. The mistake comes from thinking of the `else` as a fallback that may be anything; it is the other half of one value. The marks point at the branch with the wrong type, not at the callers of `report_line`, which still rely on its header.

*Fix:* a text in both branches, such as `"order {order.number}: {money(charge)}"`. See [U2001](/docs/errors/U2001/).
:::

### A result nobody uses (U2011)

:::mistake
Work out a quote on a line of its own, before printing it:

```diff include="day-to-day..mistakes/3:src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -77,2 +77,3 @@
   let lamp = Order(number: 1042, goods: 3_980, parcel: Parcel(grams: 1_200, zone: Home))
+  lamp.quote
   show(lamp, charge: lamp.quote)
```

```text include="mistakes/3/expected/rendered.txt#L1-L6"
[U2011] Error: this statement has type `Int`, and only `Unit` values can be discarded; bind the value with `let`
    ╭─[ src/shipping.una:78:3 ]
    │
 78 │   lamp.quote
    │   ─────┬────
    │        ╰────── this statement has type `Int`, and only `Unit` values can be discarded; bind the value with `let`
```

*Why:* `lamp.quote` gives an `Int`, and a statement may only throw away a value of type `Unit`. The quote is worked out, then lost: nothing names it, and the next line works it out again. The message says what to do.

*Fix:* remove the line, or bind the quote, `let charge = lamp.quote`, and pass `charge` on. See [U2011](/docs/errors/U2011/).
:::

### A promise the caller needs, left out (U5001)

:::mistake
Remove the postcondition of `quote`:

```diff include="day-to-day..mistakes/4:src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -49,3 +49,2 @@
   requires order.parcel.grams > 0
-  ensures result >= 0
 =
```

```text include="mistakes/4/expected/rendered.txt#L1-L10"
[U5001] Error: precondition `chair.quote >= 0` of this call is refuted
    ╭─[ src/shipping.una:83:23 ]
    │
 55 │   requires charge >= 0
    │            ─────┬─────
    │                 ╰─────── requires clause
    │
 83 │   show(chair, charge: weekend_price(chair.quote))
    │                       ─────────────┬────────────
    │                                    ╰────────────── precondition `chair.quote >= 0` of this call is refuted
```

*Why:* the verifier proves the call of `weekend_price` with the header of `quote`, not its body. Without its `ensures`, a quote could be any `Int`, a negative one too, so the precondition of `weekend_price`, `chair.quote >= 0`, cannot be proved. The body never gives back a negative number, which is why the clause looked unneeded. The first mark shows the clause that asks, and the second the call that cannot give it.

*Fix:* put the clause back. A caller can rely only on what a header promises. See [U5001](/docs/errors/U5001/).
:::

### A public function that prints without `uses` (U3004)

:::mistake
Make `show` public, in the short form, without its `uses` line:

```diff include="day-to-day..mistakes/5:src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -67,6 +67,3 @@
 --- Prints one line of the report.
-show(order: Order, charge: Int) -> Unit
-  uses @console: Console[print]
-=
-  @console.print(report_line(order, charge))
+pub show(order: Order, charge: Int) -> Unit = @console.print(report_line(order, charge))
 
```

```text include="mistakes/5/expected/rendered.txt#L1-L6"
[U3004] Error: `@console` is used here, but this code declares no `uses`, so it is pure
    ╭─[ src/shipping.una:68:47 ]
    │
 68 │ pub show(order: Order, charge: Int) -> Unit = @console.print(report_line(order, charge))
    │                                               ────┬───
    │                                                   ╰───── `@console` is used here, but this code declares no `uses`, so it is pure
```

*Why:* nothing is inferred for a `pub` function. A public header without `uses` promises a pure function, since its callers may be in other modules, and this body prints. The mistake often comes from making a working private function public: it checked before, because its `uses` was inferred, or written.

*Fix:* keep the `uses @console: Console[print]` line in its header, or keep `show` private. See [U3004](/docs/errors/U3004/).
:::

### The long form for a one-line function (U7001)

:::mistake
Write `ships_free` with `=` on its own line:

```diff include="day-to-day..mistakes/6:src/shipping.una" context="0"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -45 +45,3 @@
-pub ships_free(order: Order) -> Bool = order.goods >= 10_000 and order.parcel.zone is Home
+pub ships_free(order: Order) -> Bool
+=
+  order.goods >= 10_000 and order.parcel.zone is Home
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U7001] Error: lines 45 to 47 are not in canonical form
```

*Why:* a function without clauses whose body is one line has one canonical form, the short one. The long form looks tidier to many readers, but Una keeps one layout per function, so that every program reads the same way. The message names the lines, and the `Help` line holds the canonical text.

*Fix:* run `una fmt .`, which rewrites it, or `una fix .`, which applies the `Help` line's edit. See [U7001](/docs/errors/U7001/).
:::

## 6.7 Exercises

The exercises come with the chapter's download, `06-functions.tar.gz`. Each one starts from `exercises/N/start`: the day-to-day program with the exercise's example added at the end, and a **stub** of the function to write: its header, with a body that gives back a placeholder, `0`. `una test .` fails there until the exercise is done. Work in this order:

1. Read the example: it says what the function must give back.
2. Write the function, in whatever layout comes to you.
3. Run `una fmt .`, which puts it in canonical form, then `una check .` until it is clean.
4. Run `una test .` until every example passes.

### Exercise 1: delivery days

::::exercise
Write `delivery_days(zone)`: 2 days within the country, 4 to a neighboring country, and 9 to the rest of the world. The start package ends with:

```una include="exercises/1/start/src/shipping.una#L124-L134" title="exercises/1/start/src/shipping.una"
--- The days an order takes to arrive: 2 within the country, 4 to a neighboring country, and 9
--- to the rest of the world.
pub delivery_days(zone: Zone) -> Int = 0

example "an order within the country arrives in two days"
  do delivery_days(Home)
  expect result == 2

example "an order to the rest of the world takes nine days"
  do delivery_days(World)
  expect result == 9
```

:::hint
*Hint:* `surcharge` has the same shape: one value per zone. Its body is a `when` with one arm per zone, and a `when` of several lines takes the long form.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L11-L18"
example shipping "an order within the country arrives in two days" ... FAILED
  src/shipping.una:130: expect result == 2
  it is false, with `result` = `0`
example shipping "an order to the rest of the world takes nine days" ... FAILED
  src/shipping.una:134: expect result == 9
  it is false, with `result` = `0`

11 examples: 9 passed, 2 failed
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Give `delivery_days` a `when` with one arm per zone:

```diff include="exercises/1/start..exercises/1/answer:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -125,3 +125,8 @@
 --- to the rest of the world.
-pub delivery_days(zone: Zone) -> Int = 0
+pub delivery_days(zone: Zone) -> Int
+=
+  when zone
+    is Home -> 2
+    is Neighbor -> 4
+    is World -> 9
 
```

The result type is `Int`, so each arm gives an `Int`, and the `when`, the function's last line, is its result.
:::
::::

### Exercise 2: a members' price

::::exercise
Members pay 20 percent less for shipping, rounded down to a whole cent. Write `members_price(charge)`, with a header that promises, like `weekend_price`, that the price is never negative and never more than the charge. Then print order 1047 in `main`: 2500 cents of goods, 800 g, to a neighboring country, at the members' price. The start package ends with:

```una include="exercises/2/start/src/shipping.una#L124-L129" title="exercises/2/start/src/shipping.una"
--- The members' price: 20 percent off the charge, rounded down. It never raises the charge.
pub members_price(charge: Int) -> Int = 0

example "members pay 20 percent less"
  do members_price(1_390)
  expect result == 1_112
```

:::hint
*Hint:* 20 percent off is 80 percent of the charge: `charge * 80 / 100`. Copy the clauses of `weekend_price`. In `main`, build the order with `let`, as for `mugs`, and pass `members_price(member.quote)` as the charge.
:::

Check your answer with `una test .`, then `una run .` for the new line.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Give `members_price` its clauses and its body, and print the new order:

```diff include="exercises/2/start..exercises/2/answer:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -86,2 +86,4 @@
   show(mugs, charge: mugs.quote)
+  let member = Order(number: 1047, goods: 2_500, parcel: Parcel(grams: 800, zone: Neighbor))
+  show(member, charge: members_price(member.quote))
 
@@ -124,3 +126,7 @@
 --- The members' price: 20 percent off the charge, rounded down. It never raises the charge.
-pub members_price(charge: Int) -> Int = 0
+pub members_price(charge: Int) -> Int
+  requires charge >= 0
+  ensures result >= 0 and result <= charge
+=
+  charge * 80 / 100
 
```

The clauses take the long form. The verifier proves both promises for every charge that is not negative, and the call in `main` checks because `quote` promises a charge that is not negative.
:::
::::

### Exercise 3: two orders packed together

::::exercise
Two orders to the same customer are packed together, and pay the charge of each. Write `pair_quote(first, second)`, which gives back the sum of the two quotes, with a header that promises a result that is not negative. The start package ends with:

```una include="exercises/3/start/src/shipping.una#L124-L129" title="exercises/3/start/src/shipping.una"
--- What shipping costs for two orders packed together, in cents: the charge of each.
pub pair_quote(first: Order, second: Order) -> Int = 0

example "two orders pay the charge of each"
  do pair_quote(Order(number: 1, goods: 3_980, parcel: Parcel(grams: 1_200, zone: Home)), second: Order(number: 2, goods: 2_500, parcel: Parcel(grams: 800, zone: Neighbor)))
  expect result == 2_180
```

:::hint
*Hint:* the body is one line, with two method calls: `first.quote + second.quote`. Each call of `quote` has a precondition, so `pair_quote` must require it for both orders. The verifier then proves your `ensures` from `quote`'s own.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Require a weight for each parcel, and promise a sum that is not negative:

```diff include="exercises/3/start..exercises/3/answer:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -124,3 +124,8 @@
 --- What shipping costs for two orders packed together, in cents: the charge of each.
-pub pair_quote(first: Order, second: Order) -> Int = 0
+pub pair_quote(first: Order, second: Order) -> Int
+  requires first.parcel.grams > 0
+  requires second.parcel.grams > 0
+  ensures result >= 0
+=
+  first.quote + second.quote
 
```

Without the two `requires` lines, the calls of `quote` do not check: nothing tells the verifier that each parcel weighs something. Without the `ensures`, the function checks, but a caller of `pair_quote` would know nothing about its result.
:::
::::

## 6.8 Recap and reference

### For agents

:::agents
`una --json check .` gives every diagnostic with its `code`, `message`, `primary` span and `repairs`. U2004 and U7001 carry exact edits, which `una fix .` applies. U3004's repair, a `uses` line, widens authority and is a description with no edit: add it by hand. U5001 carries ranked repairs that need a decision. `una contract module.name` prints a function's whole header, declared or inferred. The compact rule: *label every argument after the first; `x.f(args)` is `f(x, args)`; a call that prints is a line or a `let` of its own; a block's last line is the result; a `pub` header declares its `uses`; callers rely only on the header.*
:::

### Recap

:::recap
- Label every argument after the first; a name equal to its parameter's name counts as its label, and labeled arguments may come in any order.
- `lamp.rate()` is `rate(lamp)`: the value before the dot is the first argument. Without parentheses, a field of that name comes first.
- Arguments are evaluated left to right, inner calls first; a call that prints is a line or a `let` of its own.
- A function's result is its body's value: the one line of the short form, or the last line of a block. Una has no `return`.
- A statement may throw away only a `Unit` value; bind any other with `let`.
- A caller knows a result only from the header: its type and its `ensures`.
- A `pub` function writes its `uses`; a private one may leave them out, and `una contract` shows what the checker inferred.
:::

### Reference

:::reference
- Construct pages: [functions: forms, clauses, labels, method calls](/docs/language/functions/), [`ensures` and `result`](/docs/language/functions/ensures/), [`uses`](/docs/language/capabilities/uses/), [canonical form](/docs/language/canonical-form/)
- Commands: [`una contract`](/docs/cli/contract/), [`una report`](/docs/cli/report/), [`una fmt`](/docs/cli/fmt/), [`una fix`](/docs/cli/fix/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U0102](/docs/errors/U0102/), [U0103](/docs/errors/U0103/), [U2001](/docs/errors/U2001/), [U2004](/docs/errors/U2004/), [U2005](/docs/errors/U2005/), [U2006](/docs/errors/U2006/), [U2011](/docs/errors/U2011/), [U3001](/docs/errors/U3001/), [U3004](/docs/errors/U3004/), [U3013](/docs/errors/U3013/), [U5001](/docs/errors/U5001/), [U6003](/docs/errors/U6003/), [U7001](/docs/errors/U7001/)
- Specification: [functions and contracts](/docs/spec/04-functions-and-contracts/), [grammar](/docs/spec/02-grammar/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [verification](/docs/spec/12-verification/), [canonical form](/docs/spec/15-canonical-form/)
:::
