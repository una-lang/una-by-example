---
learn: "2"
title: Numbers
editions: ["0.2"]
codes: [U0007, U0101, U1001, U1002, U2001, U2022, U5001]
time: 50
builds: A packing slip that a store prints for the box of one order, with examples that test each line
prerequisites: ["1"]
template: 2
nav: ["Values, types and let", "Whole numbers: Int", "Fixed-width integers", "Day-to-day: a packing slip", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 2 Numbers

A store counts all day: units on a shelf, lines of an order, boxes for a parcel, prices in cents. In chapter 1 every value your programs used was a text. This chapter adds numbers. You learn what a value and its type are, how to give a value a name with `let`, and how to print a number. Then you meet Una's whole numbers, `Int`, which never overflow, and the fixed-width integers, such as `U8`, for the places where a number must fit a set size. You end with the packing slip that goes into the box of an order, checked, run and tested.

## What you'll build

:::build
A packing slip: the sheet that goes into the box with an order, so that the customer can check what arrived. The program prints the slip of one sample order:

```text include="day-to-day/expected/output.txt"
Packing slip for order 1042
Ship to customer 318 <customer318@example.invalid>
  2 x LAMP-01  Desk lamp, brass
  1 x RUG-07  Wool rug, 120 by 180 cm
3 units in 2 lines
Boxes in this shipment: 2
Total paid: 8480 cents
Questions? Write to orders@example.invalid and quote the order number.
```

You will learn to:

- give values names with `let`, and say what type a name holds;
- put numbers into a text, so that `print` can show them;
- compute with whole numbers: `+`, `-`, `*`, `/` and `mod`, in the right order;
- keep money exact, as whole cents;
- choose a fixed-width type, such as `U32`, when a number must fit a set size.
:::

## Why it works this way

In many languages the plain numbers are where quiet mistakes live. A whole number has a largest value, and a total that grows past it jumps to a wrong number, often a negative one, with no error. A price such as 0.10 is stored as an approximation, so that adding prices can give 0.30000000000000004. A division by zero stops the program while it runs, in front of a customer. A number can be turned into a text, or a text into a number, without a word in the code, and the result is not what anyone meant.

Una makes each of these a rule that `una check` enforces before the program runs:

:::steps
1. **`Int` has no largest value.** A sum or a product of whole numbers is always exact, however large it grows.
2. **There are no inexact numbers.** Una has no type for fractions yet, so an amount such as 19.90 is counted in whole cents, the `Int` 1990, and nothing rounds unless the code says how.
3. **A division must be safe.** A division by a value that may be zero does not pass the check, and the check says which value breaks it.
4. **A fixed size is proved.** Where you choose a type with a set size, every operation on it must be proved to stay inside that size.
5. **No value changes its type on its own.** A number becomes a text only where the code puts it into one.
:::

> [!KEY]
> A number in Una means exactly what its type says: an `Int` is exact at any size, and a fixed-width value never leaves its range while the program runs.

## 2.1 Values, types and names: `let`

### What a value is

A **value** is one piece of data that a program works with: the number `18`, the text `"LAMP-01"`. A program computes new values from old ones, as `18 - 9` gives `9`, and prints some of them.

Every value has a **type**, which says what kind of value it is, and so what you can do with it. You can multiply two numbers, but not two product names. Think of the boxes of a paper form: one box takes a date, another a phone number, and a clerk refuses a form with a name in the date box. Types are those boxes, and `una check` is the clerk.

The types of this chapter:

| Type | Its values | Written as |
| --- | --- | --- |
| `Int` | whole numbers: positive, zero or negative | `18`, `1_990`, `-500` |
| `Text` | a sequence of characters, as in chapter 1 | `"Desk lamp, brass"` |
| `Unit` | one value only, which carries no information; `main` gives it back | `unit` |

A value written out in the code, such as `18` or `"LAMP-01"`, is a **literal**. [Section 2.3](#s2-3) adds the fixed-width integers, and [chapter 3](/learn/text-and-conditions/#s3-3) adds `Bool`, the type of yes-or-no answers.

### Why every value has a type

`print` takes a text. Here is a program that prints when the store closes, and a version that gives `print` the number `18` instead:

```diff include="steps/01-closing..steps/02-print-number:src/closing.una" title="src/closing.una"
--- a/src/closing.una
+++ b/src/closing.una
@@ -4,4 +4,4 @@
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print("The store closes at 18:00")
+  @console.print(18)
```

```text include="steps/02-print-number/expected/rendered.txt"
[U2001] Error: argument `line` of operation `Console.print` must be `Text`, found `Int`
   ╭─[ src/closing.una:7:18 ]
   │
 7 │   @console.print(18)
   │                  ─┬
   │                   ╰── argument `line` of operation `Console.print` must be `Text`, found `Int`
   │
   │ Note: run `una explain U2001` for an explanation
───╯
```

The message says that the argument of `print`, which is called `line`, must be a `Text`, and that the value given is an `Int`. Some languages would turn the number into a text without a word, and some would fail only when the line runs. Una refuses before the program runs, and it never turns a value of one type into another unless the code says so. Saying so takes two braces, as [Putting values into a text](#putting-values-into-a-text) shows.

### How to write values and names

#### Literals

- An `Int` literal is written in decimal digits: `18`, `1990`. An `_` may group the digits, so `1_990` is 1990, easier to read. For a negative number, write a minus sign in front: `-500`. [Section 2.2](#s2-2) gives every rule.
- A `Text` literal is written between double quotes, on one line, as in chapter 1: `"Desk lamp, brass"`. [Chapter 3](/learn/text-and-conditions/#s3-1) covers texts in full.
- The one `Unit` value is written `unit`. You rarely write it: a function whose result type is `Unit`, such as `main`, gives it back on its own.

#### Naming a value: `let`

`let` gives a name to a value, so that the steps after it can use the value by its name:

- `let lamps = 2` names the value `2` as `lamps`. The type, `Int`, comes from the value.
- `let lamp_cents: Int = 1_990` writes the type too, after `:`. It is optional, and it tells a reader what the name holds. When it is written, `una check` holds the value to it.

A `let` is a step of a body, on a line of its own, like a call of `print`. Such a name is also called a **binding**: it binds a word to a value. A name of a value follows the rules of a function's name: small letters, digits and `_`, starting with a letter, with no `__` and no `_` at the end: `lamps`, `lamp_cents`, `sku2`.

#### Putting values into a text

A name or a computation in braces, inside a text, puts its value into the text: `"{lamps} x {sku}"` is the value of `lamps`, then ` x `, then the value of `sku`. This is an **interpolation**. An `Int` goes in as plain decimal digits, with a minus sign when it is negative, and with no `_`. A computation may stand in the braces too: `"{lamps * lamp_cents} cents"`.

That is how a program prints a number: it puts the number into a text, and prints the text. [Chapter 3](/learn/text-and-conditions/#s3-1) shows the rest of what braces can hold.

### Each step is a package

Each example of this chapter, and of every chapter after it, is a package of its own, made as in [chapter 1, Making the package](/learn/hello/#making-the-package): a directory with `una.toml`, `verification.lock` and the module under `src/`. The book calls these packages the chapter's **steps**. Each one has a name such as `steps/03-values`: the number orders the steps in the download.

You can type each step, or take it whole from the chapter's download, `02-numbers.tar.gz`, which holds every package of this chapter. To make a step by hand next to the package of chapter 1, start in your home directory. A new terminal starts there already; if your terminal is still in `hello`, go up to your home directory with `cd ..` (`..` is the path of the directory above). Then make the new directory as before:

```sh
cd ..
mkdir values
cd values
mkdir src
```

Then write `una.toml`, `src/values.una` and `verification.lock` with your editor. `verification.lock` is the same in every package of this book. The manifest names the package and the module that `una run .` starts, here `values`, and grants the console, as in chapter 1.

### Values in a store

This program names four values, two texts and two numbers, and prints them and what it computes from them:

:::steps
```una include="steps/03-values/src/values.una" title="steps/03-values/src/values.una" verified="check, run"
module values

--- Prints a few values of two types, named with `let`, and what is computed from them.
pub main() -> Unit
  uses @console: Console[print]
=
  let sku = "LAMP-01"
  let name: Text = "Desk lamp, brass"
  let lamps = 2
  let lamp_cents: Int = 1_990
  @console.print(sku)
  @console.print(name)
  @console.print("{lamps}")
  @console.print("{lamps} x {sku}")
  @console.print("{lamps * lamp_cents} cents for {lamps} lamps")
  let total = lamps * lamp_cents
  @console.print("Total: {total} cents")
```

1. **`let sku = "LAMP-01"`.** A name for a `Text`. A **SKU**, a stock keeping unit, is the code a store gives each product.
2. **`let name: Text = "Desk lamp, brass"`.** A `Text` with its type written out.
3. **`let lamps = 2`.** A name for an `Int`.
4. **`let lamp_cents: Int = 1_990`.** An `Int` with its type written out. Money is kept in **cents**, whole numbers, so that nothing ever rounds by accident; [section 2.2](#s2-2) says why.
5. **`@console.print(sku)`.** A name of a `Text` can go to `print` as it is.
6. **`@console.print("{lamps}")`.** A number goes into a text first: the text holds only the number.
7. **`"{lamps * lamp_cents} cents for {lamps} lamps"`.** A computation and a name inside one text.
8. **`let total = lamps * lamp_cents`.** A name for a computed value. The computation runs once, at this line, and `total` holds its result.
:::

`una run .` prints:

```text include="steps/03-values/expected/output.txt"
LAMP-01
Desk lamp, brass
2
2 x LAMP-01
3980 cents for 2 lamps
Total: 3980 cents
```

### Opening hours

Names make a computation read like the sentence it stands for. This program prints the store's hours from two numbers:

:::steps
```una include="steps/04-opening/src/opening.una" title="steps/04-opening/src/opening.una" verified="check, run"
module opening

--- Prints today's opening hours, and what follows from them.
pub main() -> Unit
  uses @console: Console[print]
=
  let opens = 9
  let closes = 18
  @console.print("Open today from {opens}:00 to {closes}:00")
  let hours = closes - opens
  @console.print("That is {hours} hours of trading")
  let cutoff = closes - 1
  @console.print("Orders placed before {cutoff}:00 ship today")
```

1. **`let opens = 9` and `let closes = 18`.** The two hours that everything else comes from.
2. **`"Open today from {opens}:00 to {closes}:00"`.** A text with two interpolations. The `:00` after each brace is plain text.
3. **`let hours = closes - opens`.** A computed value, 9, named for what it means.
4. **`let cutoff = closes - 1`.** The last hour at which an order ships the same day.
:::

Its manifest names the package and its module `opening`:

```toml include="steps/04-opening/una.toml" title="steps/04-opening/una.toml"
[package]
name = "opening"
version = "0.1.0"
edition = "0.2"

[run]
entry = "opening"
grants = ["console"]
```

`una run .` prints:

```text include="steps/04-opening/expected/output.txt"
Open today from 9:00 to 18:00
That is 9 hours of trading
Orders placed before 17:00 ship today
```

When the store changes its closing time, one line changes, `let closes = 18`, and the three printed lines follow it.

### How values and names behave

#### A value keeps its type

No value turns into another type on its own. An `Int` becomes part of a text only where the code puts it in braces, and a text never turns into a number on its own. A name with a written type holds the value to that type. Write the price as a text, `let lamp_cents: Int = "1990"`, and `una check .` reports:

```text include="steps/07-declared/expected/rendered.txt#L1-L6"
[U2001] Error: `lamp_cents` is declared as `Int`, found `Text`
    ╭─[ src/values.una:10:25 ]
    │
 10 │   let lamp_cents: Int = "1990"
    │                         ───┬──
    │                            ╰──── `lamp_cents` is declared as `Int`, found `Text`
```

The quotes make `"1990"` a `Text`, four characters, not the number. The message names the binding, the type it was given, and the type it got.

#### A name exists from its line on

The steps of a body run in order, from the top, and a name exists only from the `let` that makes it. Move `let hours` of `opening` one line down, under the line that prints it:

```text include="steps/06-before/expected/rendered.txt#L1-L6"
[U1001] Error: cannot find name `hours` in this module, its imports or the prelude
    ╭─[ src/opening.una:10:28 ]
    │
 10 │   @console.print("That is {hours} hours of trading")
    │                            ──┬──
    │                              ╰──── cannot find name `hours` in this module, its imports or the prelude
```

At line 10 the name `hours` does not exist yet, so `una check .` cannot find it. The repair is to make the name before the step that uses it.

#### A name is made once

A body makes each name once. Reuse a name for a new value, as `let lamps = lamps * lamp_cents` would in `values`, and `una check .` points at both lines:

```text include="steps/05-twice/expected/rendered.txt"
[U1002] Error: `lamps` is already bound in this scope; a local cannot rebind another
    ╭─[ src/values.una:16:7 ]
    │
  9 │   let lamps = 2
    │       ──┬──
    │         ╰──── first defined here
    │
 16 │   let lamps = lamps * lamp_cents
    │       ──┬──
    │         ╰──── `lamps` is already bound in this scope; a local cannot rebind another
    │
    │ Note: run `una explain U1002` for an explanation
────╯
```

In the message, a **scope** is the part of the code where a name exists, here the body of the function, and a **local** is a name made inside it with `let`. If one name could hold two values, a reader would have to know which line they stand on to know what it means. Give the new value a name of its own, such as `total`.

#### A name keeps its value

A name made with `let` holds its value to the end of the body: no later step can give it another. A count that changes as a program works, such as a running total, uses `let edit` and an assignment, which [chapter 9](/learn/loops/#s9-2) teaches with loops. Every name in this chapter keeps its value.

### When to name a value

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Use a value in several steps of one body | `let`, once, then its name |
| Give a computation a name that says what it means | `let hours = closes - opens` |
| State what type a name holds, for the reader and the check | `let lamp_cents: Int = 1_990` |
| Use the same value in several functions | a function that gives it back, as in [chapter 1](/learn/hello/#s1-4) |
| Print a number | an interpolation: `"{lamps}"` |
:::

### Check yourself: values and names

A program counts the places in the boxes of an order of mugs:

```una include="steps/08-names/src/names.una#main" title="steps/08-names/src/names.una"
--- Prints the labels of a box of mugs.
pub main() -> Unit
  uses @console: Console[print]
=
  let mugs = 6
  let per_box = 4
  let boxes = 2
  let places = boxes * per_box
  let spare = places - mugs
  @console.print("{mugs} mugs in {boxes} boxes")
  @console.print("{spare} empty places")
  @console.print("{places - spare} of {places} places taken")
```

What does `una run .` print?

:::answer Show the answer
```text include="steps/08-names/expected/output.txt"
6 mugs in 2 boxes
2 empty places
6 of 8 places taken
```

`places` is 2 × 4, 8, and `spare` is 8 − 6, 2. The last line computes `places - spare` inside the braces: 8 − 2 is 6.
:::

One more, without code. With `lamps` an `Int` and `sku` a `Text`, which of these steps check?

1. `@console.print(lamps)`
2. `@console.print("{lamps}")`
3. `let both = lamps * sku`
4. `@console.print("{lamps} x {sku}")`

:::answer Show the answer
Steps 2 and 4 check. Step 1 gives `print` an `Int` where it takes a `Text`: U2001, as in [Why every value has a type](#why-every-value-has-a-type). Step 3 multiplies a number by a text, which has no meaning, and the check reports U2001 for it too. In steps 2 and 4 the braces put the values into a text, so `print` gets the `Text` it takes.
:::

## 2.2 Whole numbers: `Int`

### What an integer is

An **integer** is a whole number: positive, zero or negative, with no fraction. `7`, `0` and `-1205` are integers; `19.90` is not. Una's integer type is `Int`, and it has no largest value: an `Int` can be as large as the computer's memory allows.

Most numbers in a store are counts of whole things: units on a shelf, lines of an order, labels to print. Money is one too, once you count it in its smallest unit. A price of 19.90 is 1990 **cents**, and an `Int` holds 1990 exactly.

### Why money is whole cents

A price written with a decimal point looks natural, so try it:

```una include="steps/09-fraction/src/shelf.una" title="steps/09-fraction/src/shelf.una"
module shelf

--- Prints the price of a desk lamp, written with a decimal point.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = 19.90
  @console.print("{lamp}")
```

```text include="steps/09-fraction/expected/rendered.txt"
[U0101] Error: `19.90` is a fractional literal; Una's integer literals are decimal
   ╭─[ src/shelf.una:7:17 ]
   │
 7 │   let lamp = 19.90
   │                 ─┬
   │                  ╰── `19.90` is a fractional literal; Una's integer literals are decimal
   │
   │ Note: run `una explain U0101` for an explanation
───╯
```

The message says that `19.90` is a **fractional literal**, a number with a fraction, and that Una's integer literals are written in decimal digits only. Una has no type for numbers with a fraction today.

For money, whole cents work well. Many languages store a fraction such as 0.10 as a binary approximation, so that adding prices gives totals such as 0.30000000000000004, and every program rounds them in its own way, often without saying so. With whole cents, every sum and product is exact, and the one place a fraction appears, a division, says how it rounds. Money is an `Int` of cents in this chapter and in every chapter of this book.

### Numbers with a fraction: still to come

Two kinds of number with a fraction are planned for Una. A **decimal** type will hold amounts such as 19.90 exactly, in base ten, as people write them. **Floating-point** types will hold approximate values over a very wide range, for measurements and science, where a tiny rounding error does not matter. When they arrive, this chapter gains a section for each. Until then, keep money in cents and measures in whole small units, such as grams or millimeters, all as `Int`.

### How to write integers and arithmetic

#### Integer literals

- Write an integer in decimal digits: `7`, `1990`.
- Group the digits with `_` to make large numbers readable: `1_990`, `10_000`, `1_000_000`. An `_` goes only between two digits: never two in a row, never at the start or the end.
- For a negative number, write a minus sign in front: `-1205`.
- A literal has no leading zero, except `0` itself: `007` is not a literal. [A number with a leading zero](#a-number-with-a-leading-zero-u0007) shows what `una check` says.

#### The operators

An **operator** is a sign that computes a value from the values next to it, its **operands**, as `+` does in `7 + 2`.

| Operator | Meaning | `7` and `2` give |
| --- | --- | --- |
| `+` | addition | `7 + 2` is 9 |
| `-` | subtraction, or a minus sign in front of one value | `7 - 2` is 5, `-7` is minus seven |
| `*` | multiplication | `7 * 2` is 14 |
| `/` | division, dropping the remainder | `7 / 2` is 3 |
| `mod` | the remainder of the division | `7 mod 2` is 1 |

#### The order of operations

- `*`, `/` and `mod` come before `+` and `-`, as in school arithmetic: `2 + 3 * 4` is 14.
- Operators of the same level go from left to right: `20 - 6 - 4` is 10.
- A minus sign in front of one value comes first of all: `-7 / 2` divides minus seven by 2.
- Parentheses change the order: `(2 + 3) * 4` is 20.

### The operators at work

The step tries each operator on 7 units packed 2 to a box:

```una include="steps/10-operators/src/arithmetic.una#L7-L14" title="steps/10-operators/src/arithmetic.una"
  let units = 7
  let per_box = 2
  @console.print("{units + per_box}, {units - per_box} and {units * per_box}")
  @console.print("{units / per_box} full boxes, {units mod per_box} unit left over")
  @console.print("{-units} and {per_box - units}")
  @console.print("{2 + 3 * 4} and {(2 + 3) * 4}")
  @console.print("{20 - 6 - 4} and {20 - (6 - 4)}")
  @console.print("{1_000_000 * 1_000_000}")
```

```text include="steps/10-operators/expected/output.txt#L1-L6"
9, 5 and 14
3 full boxes, 1 unit left over
-7 and -5
14 and 20
10 and 18
1000000000000
```

`7 / 2` gives 3 full boxes and drops the half, and `7 mod 2` gives the 1 unit left over. `20 - (6 - 4)` computes the parentheses first: 20 − 2 is 18. `1_000_000 * 1_000_000` is exact, with all its zeros.

### Money as `Int` cents

A price never needs a fraction, so it never needs rounding until the code chooses one:

:::steps
```una include="steps/11-prices/src/prices.una" title="steps/11-prices/src/prices.una" verified="check, run"
module prices

--- Prints a few computations on prices in cents.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = 1_990
  let rug = 4_500
  let order = 2 * lamp + rug
  @console.print("order: {order} cents, or {order / 100} units and {order mod 100} cents")
  let discount = order * 15 / 100
  @console.print("15% off: {discount} cents off, {order - discount} to pay")
  let refund = -1_205
  @console.print("refund: {refund / 100} and {refund mod 100}")
  let past_64_bits = 9_223_372_036_854_775_807 + 1
  @console.print("no overflow: {past_64_bits}")
```

1. **`let order = 2 * lamp + rug`.** Multiplication first, then addition: 2 lamps at 1990 cents and a rug at 4500.
2. **`order / 100` and `order mod 100`.** Division of two `Int` values gives a whole number and drops the remainder; `mod` gives the remainder. Together they split cents into whole units of money and cents.
3. **`order * 15 / 100`.** A percentage. Multiply first, then divide, so that nothing is dropped before the division.
4. **`refund / 100` and `refund mod 100`.** Division of a negative amount.
5. **`9_223_372_036_854_775_807 + 1`.** The largest value that many languages can hold in a whole number, plus one.
:::

`una run .` prints:

```text include="steps/11-prices/expected/output.txt"
order: 8480 cents, or 84 units and 80 cents
15% off: 1272 cents off, 7208 to pay
refund: -13 and 95
no overflow: 9223372036854775808
```

The discount is 15 percent of 8480 cents, 1272: the exact value is 1272.0, so nothing is dropped. Where a percentage does not come out whole, `/` drops the fraction, and so rounds down. The refund line is the subject of [Euclidean division](#euclidean-division).

### Functions on whole numbers: `abs`, `min` and `max`

Una gives every module a few functions on `Int`, ready to call, without writing them. They belong to the **prelude**, the set of functions every module has, which [section 3.2](/learn/text-and-conditions/#s3-2) presents:

- `abs(x)` is the distance of `x` from zero: `abs(-3)` is 3, and `abs(3)` is 3.
- `min(a, b: c)` is the smaller of two values, and `max(a, b: c)` the larger. The second argument carries its label, `b`, as every argument after the first does.

The step computes three facts about the stock of one SKU:

:::steps
```una include="steps/12-int-functions/src/stock.una" title="steps/12-int-functions/src/stock.una" verified="check, run"
module stock

--- Prints what `abs`, `min` and `max` give for the stock of one SKU.
pub main() -> Unit
  uses @console: Console[print]
=
  let on_shelf = 14
  let reserved = 17
  let counted = 11
  @console.print("free to sell: {max(on_shelf - reserved, b: 0)}")
  @console.print("one customer may buy: {min(on_shelf, b: 10)}")
  @console.print("the count is off by {abs(counted - on_shelf)}")
```

1. **`max(on_shelf - reserved, b: 0)`.** 14 − 17 is −3: more units are promised to orders than the shelf holds. `max` with 0 makes the answer 0, never below.
2. **`min(on_shelf, b: 10)`.** A limit of 10 units per customer, or fewer when the shelf holds fewer.
3. **`abs(counted - on_shelf)`.** How far a count is off, whichever way: 11 − 14 is −3, and its distance from zero is 3.
:::

```text include="steps/12-int-functions/expected/output.txt"
free to sell: 0
one customer may buy: 10
the count is off by 3
```

### How `Int` behaves

#### No 64-bit limit

The last line of `prices` shows that `Int` has no 64-bit limit: the sum is exact. Many languages store whole numbers in 64 **bits**, binary digits, and a sum past the largest 64-bit value wraps around to a large negative number, or stops the program. In Una it is just a larger number.

#### Euclidean division

The refund line of `prices` shows how Una divides a negative number. Division and `mod` are **Euclidean**: the remainder is never negative, and the quotient is chosen to make that true. So `-1205 / 100` is `-13` and `-1205 mod 100` is `95`, since −13 × 100 + 95 is −1205. Many languages round toward zero instead, and give −12 and −5. For amounts that are not negative, both rules agree, so a function that splits cents into units and cents is right for every amount that is not negative.

#### Division by zero, a proof obligation

Dividing by zero has no answer, so Una does not let a program reach such a division. Here is a function whose divisor comes from a parameter:

```una include="steps/13-division/src/split.una" title="steps/13-division/src/split.una"
module split

--- What each of `people` pays when they share a bill of `total` cents, rounded down.
pub share(total: Int, people: Int) -> Int = total / people

--- Prints one share of a bill.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{share(9000, people: 4)} cents each")
```

```text include="steps/13-division/expected/rendered.txt"
[U5001] Error: division obligation `people != 0` is refuted
   ╭─[ src/split.una:4:45 ]
   │
 4 │ pub share(total: Int, people: Int) -> Int = total / people
   │                                             ───────┬──────
   │                                                    ╰──────── division obligation `people != 0` is refuted
   │
   │ Help: repair 1: guard the division with `if people != 0`
   │
   │ Note 1: obligation ob-7797c5169054 (division) is refuted: people != 0
   │
   │ Note 2: counterexample: people = 0
   │
   │ Note 3: run `una explain U5001` for an explanation
───╯
```

Read it in three steps, as in [chapter 1](/learn/hello/#if-una-check-finds-a-mistake):

1. **The message.** `una check` turned the division into a **proof obligation**: a fact that must be proved before the program may run. Here it is `people != 0`, "people is not zero". The part of `una check` that proves such facts is the **verifier**. It asks Z3, the solver you installed in chapter 1, whether the fact holds for every value the parameters can take. It does not, so the obligation is **refuted**, and the code is U5001.
2. **The place.** The marks point at the whole division, `total / people`.
3. **The notes.** `Note 2: counterexample: people = 0` gives a value that breaks the obligation, a **counterexample**: a call such as `share(9000, people: 0)` would divide by zero. `Note 1` repeats the obligation with its identifier, `ob-…`, which tools use to name it.

A divisor written as a literal other than zero, such as `100`, needs no proof. For a divisor that comes from a parameter, the function must say why it cannot be zero. The `Help` line proposes a **guard**: an `if` that runs the division only when `people != 0`, "people is not equal to 0", holds ([section 3.4](/learn/text-and-conditions/#s3-4) teaches `if`). The other way is a **precondition**, a rule every caller must meet, such as "people is greater than 0" ([section 5.1](/learn/contracts/#s5-1)).

#### Dividing by the literal 0

A division by the literal `0` can never be safe. Change one line of `arithmetic`, so that it divides by `0`:

```diff include="steps/10-operators..steps/14-zero:src/arithmetic.una" title="src/arithmetic.una" context="0"
--- a/src/arithmetic.una
+++ b/src/arithmetic.una
@@ -15 +15 @@
-  @console.print("{1990 * 3 / 100}")
+  @console.print("{units / 0}")
```

```text include="steps/14-zero/expected/rendered.txt#L1-L6"
[U5001] Error: division obligation `0 != 0` is refuted
    ╭─[ src/arithmetic.una:15:20 ]
    │
 15 │   @console.print("{units / 0}")
    │                    ────┬────
    │                        ╰────── division obligation `0 != 0` is refuted
```

The obligation is `0 != 0`, false whatever the values are, so it needs no counterexample.

> [!NOTE]
> An `Int` that may grow past the computer's own number size costs a little more to compute with than a number of a fixed size. Where a number must have a fixed size, such as a number another program reads as one byte, use the fixed-width types of [section 2.3](#s2-3).

### `Int` or something else

:::decide
**Which to use:**

| The number is… | Use |
| --- | --- |
| A count, a quantity or an amount of money | `Int`, with money in cents |
| A field that another program, a file or a device reads with a fixed size | a fixed-width type ([section 2.3](#s2-3)) |
| A code made of digits, such as a postal code with a leading zero | `Text`: you never compute with it, and `01310` is not an integer literal |
| A price with a fraction | `Int` cents, written with two decimals where the program prints it, as [exercise 3](#exercise-3-amounts-with-two-decimals) does |
| A measure with a fraction | `Int` in a smaller unit, such as grams or millimeters |
:::

### Check yourself: integers

The step `arithmetic` ends with two more lines:

```una include="steps/10-operators/src/arithmetic.una#L15-L16" title="steps/10-operators/src/arithmetic.una"
  @console.print("{1990 * 3 / 100}")
  @console.print("{-7 / 2} and {-7 mod 2}")
```

What do they print? The first is three units at 19.90, in whole units of money.

:::answer Show the answer
```text include="steps/10-operators/expected/output.txt#L7-L8"
59
-4 and 1
```

`1990 * 3` is 5970, and `/ 100` drops the remainder: 59. In `-7 / 2`, the minus sign comes first, and Euclidean division keeps the remainder at 0 or above: −4 × 2 is −8, and −7 − (−8) is 1. So the quotient is −4 and the remainder 1.
:::

## 2.3 Fixed-width integers

### What a fixed-width integer is

An `Int` grows as large as it needs. A **fixed-width integer** has a set number of bits, and so a smallest and a largest value. Think of the counter on a parking ticket machine with three digits: it shows 0 to 999, and nothing past that. A computer stores such a number in 8, 16, 32 or 64 bits, and other programs, file formats and devices often expect exactly that: a **byte**, 8 bits, holds 0 to 255.

Una has the **unsigned** types `U8`, `U16`, `U32` and `U64`, which hold 0 and up, and the **signed** types `I8`, `I16`, `I32` and `I64`, which hold negative values too. The number is the width in bits:

| Type | Smallest | Largest |
| --- | --- | --- |
| `U8` | 0 | 255 |
| `U16` | 0 | 65535 |
| `U32` | 0 | 4294967295 |
| `U64` | 0 | 18446744073709551615 |
| `I8` | -128 | 127 |
| `I16` | -32768 | 32767 |
| `I32` | -2147483648 | 2147483647 |
| `I64` | -9223372036854775808 | 9223372036854775807 |

Each is its own type, distinct from `Int` and from the others.

> [!NOTE]
> The fixed-width types belong to edition `0.2` and later, the edition of every package in this book. In a package of edition `0.1`, `U8` and the others are ordinary names.

### Why every operation is proved

In many languages a fixed-width number that passes its largest value **wraps around**: 255 + 1 in a byte gives 0, with no error. A count of 256 labels kept in a byte becomes 0, the label printer prints nothing, and nobody knows why. In Una a fixed-width value never wraps around unless the code asks for it by name. Every `+`, `-`, `*`, `/`, `mod` and minus sign on one is a proof obligation: the verifier must prove that the exact result fits the type.

A function that adds 1 to a byte, with nothing to say the byte is below 255, does not check:

```una include="steps/16-overflow/src/printer.una#copies" title="steps/16-overflow/src/printer.una"
--- How many copies of a label to print: one per facing on the shelf, and one spare.
--- The label printer reads the count as one byte, so it is a `U8`.
pub copies(facings: U8) -> U8 = facings + 1
```

```text include="steps/16-overflow/expected/rendered.txt#L1,L8,L10,L12,L16"
[U5001] Error: overflow obligation `facings + 1 in 0..255` is refuted
   │ Help 1: repair 1: guard the operation with `if facings.to_int() + 1 in 0..255`
   │ Help 2: repair 2: give the values a wider type, converting them explicitly
   │ Help 3: repair 3: if wrapping or saturating is meant, use `wrapping_add`, `saturating_add` or their siblings
   │ Note 2: counterexample: facings = 255
```

The obligation `facings + 1 in 0..255` says that the sum must lie between 0 and 255, and the counterexample is the one value that breaks it, 255. The three repairs are the three honest choices: test the range first, with an `if` ([section 3.4](/learn/text-and-conditions/#s3-4)), use a wider type, or say that wrapping or stopping at the end of the range is what you mean. Each makes the behavior at the edge of the range visible in the code.

### How to write fixed-width values

#### A literal takes the type its place expects

`let copies: U8 = 200` makes 200 a `U8`, since the name's type says so. A literal also takes the type of the parameter it is passed to, or of the other operand of an operator. A literal that does not fit its type does not check, as [How fixed-width integers behave](#how-fixed-width-integers-behave) shows.

#### Method calls

The operations of this section are **methods**: functions written after a value, with a dot. `copies.to_int()` calls `to_int` on `copies`, as `@console.print(…)` calls `print` on the console. A method call always takes its parentheses here, and a second value goes in them with its label, as in `copies.wrapping_add(by: 100)`. [Section 3.2](/learn/text-and-conditions/#s3-2) covers method calls in full.

#### Converting between integer types

- `x.to_int()` turns any fixed-width value into an `Int`. Every value fits, so it never fails.
- `x.to_u8()`, `x.to_u16()`, `x.to_i32()` and the others turn a value into another integer type. Where every value fits, such as from `U8` to `U16`, the conversion is called **widening**, and it needs no proof. Every other conversion, to a type that cannot hold every value of the source, such as from `Int`, or from `I8` to `U16`, is **narrowing**, and the verifier must prove that the value fits.
- A `U8` and an `Int`, or a `U8` and a `U16`, do not mix in one operation: convert one of them first.

#### Wrapping and saturating, by name

- `a.wrapping_add(by: b)`, `wrapping_sub` and `wrapping_mul` wrap around, as other languages do silently.
- `a.saturating_add(by: b)`, `saturating_sub` and `saturating_mul` stop at the end of the range: at the smallest or at the largest value.

These never leave the range, so they need no proof.

### Each form at work

The step writes each form:

```una include="steps/17-widths/src/widths.una#L1-L14" title="steps/17-widths/src/widths.una"
module widths

--- Prints values of fixed-width types, and what their methods give.
pub main() -> Unit
  uses @console: Console[print]
=
  let copies: U8 = 200
  let offset: I8 = -128
  let largest: U64 = 18_446_744_073_709_551_615
  @console.print("{copies}, {offset} and {largest}")
  @console.print("{copies.to_int() + 100} as an Int")
  @console.print("{copies.wrapping_add(by: 100)} wrapped, {copies.saturating_add(by: 100)} saturated")
  let count = 42
  @console.print("{count.to_u8()} as a U8")
```

```text include="steps/17-widths/expected/output.txt#L1-L4"
200, -128 and 18446744073709551615
300 as an Int
44 wrapped, 255 saturated
42 as a U8
```

`copies.to_int() + 100` is an `Int`, so 300 is fine. In a `U8`, 200 + 100 wraps around to 44, since 300 − 256 is 44, or saturates at 255. `count.to_u8()` narrows the `Int` 42: the verifier knows that `count` is 42, so it proves that it fits.

### Label copies as one byte: `U8`

The module `printer` counts the copies of a shelf label in a `U8`, and a roll of labels in a `U16`:

:::steps
```una include="steps/15-printer/src/printer.una" title="steps/15-printer/src/printer.una" verified="check, run"
module printer

--- How many copies of a label to print: one per facing on the shelf, and one spare.
--- The label printer reads the count as one byte, so it is a `U8`.
pub copies(facings: U8) -> U8
  requires facings < 255
=
  facings + 1

--- Prints how many labels two shelves need.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps: U8 = 4
  let mugs: U8 = 12
  let lamp_labels = copies(lamps)
  let mug_labels = copies(mugs)
  @console.print("{lamp_labels} and {mug_labels} labels")
  let labels = lamp_labels.to_int() + mug_labels.to_int()
  @console.print("{labels} labels in all")
  let roll: U16 = 1_000
  @console.print("{roll.saturating_sub(by: 1_200)} left on a roll of {roll} after 1200")
```

1. **`pub copies(facings: U8) -> U8`.** The label printer reads the number of copies as one byte, so the result is a `U8`. A **facing** is one row of a product on the front of a shelf.
2. **`requires facings < 255`.** A **precondition**: a rule every caller must meet, written on its own line under the header, before `=`. Here it says that `facings` is less than 255, so that `facings + 1` fits in a `U8`. The verifier proves the addition from it, and checks the rule at each call. [Chapter 5](/learn/contracts/#s5-1) covers preconditions in full.
3. **`let lamps: U8 = 4`.** A literal takes the type its place expects, here `U8`.
4. **`lamp_labels.to_int() + mug_labels.to_int()`.** Two `U8` values turned into `Int` before they are added. The sum is an `Int`, and cannot overflow.
5. **`roll.saturating_sub(by: 1_200)`.** Subtraction that stops at the bottom of the range, 0, instead of going below it.
:::

`una run .` prints:

```text include="steps/15-printer/expected/output.txt"
5 and 13 labels
18 labels in all
0 left on a roll of 1000 after 1200
```

### How fixed-width integers behave

#### A literal must fit at once

A literal that does not fit its type is refused before any proof. Write `300` for the `U8` of `widths`:

```text include="steps/18-literal-range/expected/rendered.txt#L1-L6"
[U2022] Error: the literal `300` does not fit `U8`, which holds `0` to `255`
   ╭─[ src/widths.una:7:20 ]
   │
 7 │   let copies: U8 = 300
   │                    ─┬─
   │                     ╰─── the literal `300` does not fit `U8`, which holds `0` to `255`
```

The message gives the range of the type, so you can see why: a `U8` holds 0 to 255. A minus sign with its literal counts as one literal, so `-128` fits an `I8`.

#### Types do not mix

An operation takes two values of one type. Add the `Int` `count` to the `U8` `copies`:

```text include="steps/19-mixed/expected/rendered.txt#L1-L6"
[U2001] Error: an operand of `+` must be `U8`, found `Int`
    ╭─[ src/widths.una:14:29 ]
    │
 14 │   @console.print("{copies + count} in all")
    │                             ──┬──
    │                               ╰──── an operand of `+` must be `U8`, found `Int`
```

The `U8` came first, so the message asks the other operand to be a `U8` too. Convert one of them: `copies.to_int() + count` is an `Int` sum.

#### A narrowing must be proved

A conversion that may not fit is proved like an operation. A function that narrows any `Int` to a `U8` does not check:

```una include="steps/20-narrowing/src/tags.una#copies_byte" title="steps/20-narrowing/src/tags.una"
--- The number of copies, as the label printer reads it: one byte.
pub copies_byte(copies: Int) -> U8 = copies.to_u8()
```

```text include="steps/20-narrowing/expected/rendered.txt#L1,L8,L16"
[U5001] Error: overflow obligation `copies.to_u8() in 0..255` is refuted
   │ Help 1: repair 1: guard the operation with `if copies in 0..255`
   │ Note 2: counterexample: copies = -1
```

The counterexample, `copies = -1`, is an `Int` that no `U8` can hold. A precondition that `copies` lies between 0 and 255 ([chapter 5](/learn/contracts/#s5-1)), or a value the verifier knows, as `count` in `widths`, makes the conversion safe.

#### More rules

- **Every operation, even with literals.** `250 + 6` where a `U8` is expected is not one literal: it gets an overflow obligation, which is refuted.
- **Division too.** `/` and `mod` on fixed-width values are Euclidean, as on `Int`, and a divisor that may be zero is a division obligation, as in [section 2.2](#division-by-zero-a-proof-obligation).
- **Interpolation shows the number.** A fixed-width value in braces goes into the text as its decimal digits, as an `Int` does.
- **Lengths stay `Int`.** The length of a text, which [chapter 3](/learn/text-and-conditions/#s3-2) shows, is always an `Int`.

### When to use a fixed width

:::decide
**Which to use:**

| The number… | Use |
| --- | --- |
| Is a count, a total or money in your own code | `Int` |
| Is read or written by a device, a protocol or a file format with a set width | the fixed-width type it names |
| Must wrap around on purpose, as in a checksum | a fixed-width type and `wrapping_add` |
| Must stop at the end of the range, as a counter of labels left | `saturating_sub` and its siblings |
| Crosses between the two | `to_int()` one way, and a narrowing method, with its proof, the other |
:::

### Check yourself: fixed-width integers

Change the first `let` of `widths` so that the `U8` is computed:

```diff include="steps/17-widths..steps/21-constant-overflow:src/widths.una" title="src/widths.una" context="0"
--- a/src/widths.una
+++ b/src/widths.una
@@ -7 +7 @@
-  let copies: U8 = 200
+  let copies: U8 = 200 + 100
```

Does it still check? And in the original step, what does the last line print, with `roll` holding 500?

```una include="steps/17-widths/src/widths.una#L15-L16" title="steps/17-widths/src/widths.una"
  let roll: U16 = 500
  @console.print("{roll.saturating_sub(by: 600)} and {roll.wrapping_sub(by: 600)}")
```

:::answer Show the answer
It does not check:

```text include="steps/21-constant-overflow/expected/rendered.txt#L1"
[U5001] Error: overflow obligation `200 + 100 in 0..255` is refuted
```

`200 + 100` is 300, which a `U8` cannot hold, and the verifier proves that the sum leaves the range. The last line of the original prints:

```text include="steps/17-widths/expected/output.txt#L5"
0 and 65436
```

500 − 600 is −100. `saturating_sub` stops at 0. `wrapping_sub` wraps around the 65536 values of a `U16`: −100 + 65536 is 65436.
:::

## 2.4 Day-to-day: a packing slip

### What the program must do

A packing slip goes into every box the store ships. It names the order and the customer, lists each line of the order with its quantity, counts the units and the boxes, and gives the total paid. The warehouse prints it as the box is packed.

The design follows from the job and from what you have learned. Each line of the slip comes from its own function, which takes the values the line shows and gives back its text. Those functions have no `uses` line, so they print nothing, and an example can test each one by its result. `main` names the sample order's values with `let`, calls the functions, and prints what they give back, line by line.

### The slip's package and manifest

The program is one module, `slip`, in a package of its own, made as in [Each step is a package](#each-step-is-a-package), with this manifest:

```toml include="day-to-day/una.toml" title="day-to-day/una.toml"
[package]
name = "slip"
version = "0.1.0"
edition = "0.2"

[run]
entry = "slip"
grants = ["console"]
```

### The lines of the slip

Nine functions, each with a doc comment, each written in the short form, on one line:

```una include="day-to-day/src/slip.una#title..closing" title="day-to-day/src/slip.una" caption="one function per line of the slip"
--- The first line of a slip: the order the box holds. The warehouse keeps an order's
--- number as an unsigned 32-bit number, so it is a `U32`.
pub title(order: U32) -> Text = "Packing slip for order {order}"

--- Where the box goes: the customer's number, a `U32` as well, and email address.
pub ship_to(customer: U32, email: Text) -> Text = "Ship to customer {customer} <{email}>"

--- One line of the order: how many units of a SKU, and what the SKU is.
pub item(quantity: Int, sku: Text, name: Text) -> Text = "  {quantity} x {sku}  {name}"

--- What one line of the order costs, in cents.
pub line_cents(quantity: Int, cents: Int) -> Int = quantity * cents

--- How many boxes the units need, at most two units to a box: half the units, rounded up.
pub boxes(units: Int) -> Int = (units + 1) / 2

--- How much the order holds.
pub count_line(units: Int, lines: Int) -> Text = "{units} units in {lines} lines"

--- How many boxes the order ships in.
pub box_line(count: Int) -> Text = "Boxes in this shipment: {count}"

--- What the customer paid for the goods, in cents.
pub total_line(cents: Int) -> Text = "Total paid: {cents} cents"

--- The last line, the same on every slip.
pub closing() -> Text = "Questions? Write to orders@example.invalid and quote the order number."
```

Each function uses an idea of this chapter:

- `title` and `ship_to` take a `U32`. The warehouse keeps the numbers of orders and customers in 32 bits, so their type says so, and a number that does not fit is refused at the call.
- `item`, `count_line`, `box_line` and `total_line` put their parameters into a text with interpolation. `item` starts with two spaces, inside the text, so that the item lines stand out on paper.
- `line_cents` gives back an `Int`, not a text: it multiplies two `Int` values with `*`.
- `boxes` divides with `/`, which drops the remainder. Adding 1 before dividing by 2 turns "half, rounded down" into "half, rounded up": 3 units need 2 boxes, and 4 units need 2 as well.
- `closing` takes no parameters and always gives back the same text.

Money is in cents, as an `Int`: 1990 is 19 units of money and 90 cents. Whole cents never round, so the total is exact. [Exercise 3](#exercise-3-amounts-with-two-decimals) prints them with two decimals.

### Printing the slip

`main` names the order's values, computes what follows from them, then prints the slip one line at a time:

```una include="day-to-day/src/slip.una#main" title="day-to-day/src/slip.una" verified="check, run"
--- Prints the slip of order 1042: two desk lamps and one rug.
pub main() -> Unit
  uses @console: Console[print]
=
  let order: U32 = 1042
  let lamps = 2
  let rugs = 1
  let units = lamps + rugs
  let lamp_cents = line_cents(lamps, cents: 1990)
  let rug_cents = line_cents(rugs, cents: 4500)
  @console.print(title(order))
  @console.print(ship_to(318, email: "customer318@example.invalid"))
  @console.print(item(lamps, sku: "LAMP-01", name: "Desk lamp, brass"))
  @console.print(item(rugs, sku: "RUG-07", name: "Wool rug, 120 by 180 cm"))
  @console.print(count_line(units, lines: 2))
  @console.print(box_line(boxes(units)))
  @console.print(total_line(lamp_cents + rug_cents))
  @console.print(closing())
```

Read it in two parts:

1. **The six `let` lines** name the order's values. `order` is a `U32`, as `title` takes. `units` is the sum of the two quantities, and `lamp_cents` and `rug_cents` are what `line_cents` gives back for each line.
2. **The eight `print` lines** print the slip, each one calling the function of its line. `box_line(boxes(units))` calls `boxes` first, and passes its result to `box_line`.

`ship_to(318, …)` passes a literal where a `U32` is expected, so 318 is a `U32`. The calls with more than one argument label every argument after the first, as in chapter 1: `line_cents(lamps, cents: 1990)`.

### Why one function per line of the slip

Why so many small functions for a program this size? Each one is a line of the slip that someone may want to change: the wording of the closing line, the layout of an item, the size of a box. A change to one of them touches one line of code and its examples, and the header of each says, without a look at its body, that it only computes a text or a number. The same program written as one `main` with every text in place would be shorter, and nothing in it could be tested except by reading what it prints.

### Running it

In the `day-to-day` directory, `una run .` prints the slip shown in [What you'll build](#what-youll-build): the order and the customer, two item lines, three units in two lines, two boxes, and a total of 8480 cents, which is 2 × 1990 + 4500.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/slip.una" title="day-to-day/src/slip.una" caption="the whole program" verified="check, run, test"
module slip

-- A packing slip: the sheet that goes into the box with an order, so that the customer
-- can check what arrived. This version prints the slip of one sample order.

--- The first line of a slip: the order the box holds. The warehouse keeps an order's
--- number as an unsigned 32-bit number, so it is a `U32`.
pub title(order: U32) -> Text = "Packing slip for order {order}"

--- Where the box goes: the customer's number, a `U32` as well, and email address.
pub ship_to(customer: U32, email: Text) -> Text = "Ship to customer {customer} <{email}>"

--- One line of the order: how many units of a SKU, and what the SKU is.
pub item(quantity: Int, sku: Text, name: Text) -> Text = "  {quantity} x {sku}  {name}"

--- What one line of the order costs, in cents.
pub line_cents(quantity: Int, cents: Int) -> Int = quantity * cents

--- How many boxes the units need, at most two units to a box: half the units, rounded up.
pub boxes(units: Int) -> Int = (units + 1) / 2

--- How much the order holds.
pub count_line(units: Int, lines: Int) -> Text = "{units} units in {lines} lines"

--- How many boxes the order ships in.
pub box_line(count: Int) -> Text = "Boxes in this shipment: {count}"

--- What the customer paid for the goods, in cents.
pub total_line(cents: Int) -> Text = "Total paid: {cents} cents"

--- The last line, the same on every slip.
pub closing() -> Text = "Questions? Write to orders@example.invalid and quote the order number."

--- Prints the slip of order 1042: two desk lamps and one rug.
pub main() -> Unit
  uses @console: Console[print]
=
  let order: U32 = 1042
  let lamps = 2
  let rugs = 1
  let units = lamps + rugs
  let lamp_cents = line_cents(lamps, cents: 1990)
  let rug_cents = line_cents(rugs, cents: 4500)
  @console.print(title(order))
  @console.print(ship_to(318, email: "customer318@example.invalid"))
  @console.print(item(lamps, sku: "LAMP-01", name: "Desk lamp, brass"))
  @console.print(item(rugs, sku: "RUG-07", name: "Wool rug, 120 by 180 cm"))
  @console.print(count_line(units, lines: 2))
  @console.print(box_line(boxes(units)))
  @console.print(total_line(lamp_cents + rug_cents))
  @console.print(closing())

example "the title names the order"
  do title(1042)
  expect result == "Packing slip for order 1042"

example "the address line holds the customer number and the email"
  do ship_to(318, email: "customer318@example.invalid")
  expect result == "Ship to customer 318 <customer318@example.invalid>"

example "an item line is indented and starts with the quantity"
  do item(2, sku: "LAMP-01", name: "Desk lamp, brass")
  expect result == "  2 x LAMP-01  Desk lamp, brass"

example "a line costs its quantity times the unit price"
  do line_cents(2, cents: 1990)
  expect result == 3980

example "a line of zero units costs nothing"
  do line_cents(0, cents: 1990)
  expect result == 0

example "an odd number of units needs one box more than half of them"
  do boxes(3)
  expect result == 2

example "an even number of units fills every box"
  do boxes(4)
  expect result == 2

example "no units need no box"
  do boxes(0)
  expect result == 0

example "the count line gives units and lines"
  do count_line(3, lines: 2)
  expect result == "3 units in 2 lines"

example "the box line gives the number of boxes"
  do box_line(2)
  expect result == "Boxes in this shipment: 2"

example "the total is in cents"
  do total_line(8480)
  expect result == "Total paid: 8480 cents"
```

## 2.5 Testing it

### One example per function

Every function of the slip gives back a value, so each can have an example. Eight of the nine have one, in the form chapter 1 showed; `closing` always gives back the same text, which the run shows. The form is `do` a call, then `expect result ==` the exact value. An example may expect a number as well as a text:

```una include="day-to-day/src/slip.una#L65-L71" title="day-to-day/src/slip.una" caption="two examples of line_cents"
example "a line costs its quantity times the unit price"
  do line_cents(2, cents: 1990)
  expect result == 3980

example "a line of zero units costs nothing"
  do line_cents(0, cents: 1990)
  expect result == 0
```

[Chapter 14](/learn/testing/#s14-1) covers examples in full.

### The edges of a computation

A computation can be right for the sample order and wrong elsewhere, so its examples try the edges too:

- `boxes` has three: an odd number of units, 3, which needs the rounding up; an even number, 4, which must not get a box too many; and 0, no units and no box.
- "a line of zero units costs nothing" covers a case the sample order never reaches.
- "an item line is indented and starts with the quantity" pins the two leading spaces, which are easy to lose in an edit and hard to see in the output.

An example that states the whole expected text catches a change of one character.

### Running the slip's examples

In the `day-to-day` directory, `una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L14"
example slip "the title names the order" ... ok
example slip "the address line holds the customer number and the email" ... ok
example slip "an item line is indented and starts with the quantity" ... ok
example slip "a line costs its quantity times the unit price" ... ok
example slip "a line of zero units costs nothing" ... ok
example slip "an odd number of units needs one box more than half of them" ... ok
example slip "an even number of units fills every box" ... ok
example slip "no units need no box" ... ok
example slip "the count line gives units and lines" ... ok
example slip "the box line gives the number of boxes" ... ok
example slip "the total is in cents" ... ok

11 examples: 11 passed, 0 failed
```

Each example takes one line of the report, so when one fails, the report names the line of the slip that changed.

### What the examples leave out: `main`

The examples do not call `main`. It only names values and prints what the functions give back, and the functions are what the examples cover. Most Una programs take this shape: a short `main` that prints, and functions with no `uses` line that hold the computations and their examples.

## 2.6 Common mistakes

Each mistake is a small change to `day-to-day/src/slip.una`, followed by what `una check .` reports. Read each diagnostic as [chapter 1](/learn/hello/#if-una-check-finds-a-mistake) shows: the message, then the place, then the help.

### Printing a number (U2001)

:::mistake
Print the total itself, instead of the line that holds it:

```diff include="day-to-day..mistakes/1:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -49,3 +49,3 @@
   @console.print(box_line(boxes(units)))
-  @console.print(total_line(lamp_cents + rug_cents))
+  @console.print(lamp_cents + rug_cents)
   @console.print(closing())
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U2001] Error: argument `line` of operation `Console.print` must be `Text`, found `Int`
```

*Why:* `print` takes a `Text`, and `lamp_cents + rug_cents` is an `Int`. Una turns no value into another type unless the code says so. The message names the parameter, `line`, the type it must have and the type it got.

*Fix:* put the number in a text, `"{lamp_cents + rug_cents}"`, or call `total_line`, which does. See [U2001](/docs/errors/U2001/).
:::

### A price with a decimal point (U0101)

:::mistake
Write the price of a lamp as it appears on a shelf tag:

```diff include="day-to-day..mistakes/2:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -41,3 +41,3 @@
   let units = lamps + rugs
-  let lamp_cents = line_cents(lamps, cents: 1990)
+  let lamp_cents = line_cents(lamps, cents: 19.90)
   let rug_cents = line_cents(rugs, cents: 4500)
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U0101] Error: `19.90` is a fractional literal; Una's integer literals are decimal
```

*Why:* Una has no type for numbers with a fraction, so `19.90` is not a literal it reads. The marks point at `90`, the digits after the point, which no integer literal can have.

*Fix:* write the price in cents, `1990`, as every amount of the slip is. See [U0101](/docs/errors/U0101/).
:::

### A number with a leading zero (U0007)

:::mistake
Write the order number as a form would, with a leading zero:

```diff include="day-to-day..mistakes/3:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -37,3 +37,3 @@
 =
-  let order: U32 = 1042
+  let order: U32 = 01042
   let lamps = 2
```

```text include="mistakes/3/expected/rendered.txt#L1-L12"
[U0007] Error: malformed integer literal `01042`
    ╭─[ src/slip.una:38:20 ]
    │
 38 │   let order: U32 = 01042
    │                    ──┬──
    │                      ╰──── malformed integer literal `01042`
    │
    │ Help: repair 1: write `1042`; edit src/slip.una:38:20..38:25 to "1042"
    │
    │ Note: run `una explain U0007` for an explanation
────╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

*Why:* an integer literal has no leading zero, except `0` itself, so `01042` is a **malformed** literal: it breaks the rules of how a literal is written. The `Help` line gives the literal it means, and the last line of the output says that `una fix .` can make that edit.

*Fix:* write `1042`. A number whose zeros matter, such as a postal code, is a `Text`. See [U0007](/docs/errors/U0007/).
:::

### An `Int` where a `U32` is expected (U2001)

:::mistake
Leave out the type of `order`:

```diff include="day-to-day..mistakes/4:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -37,3 +37,3 @@
 =
-  let order: U32 = 1042
+  let order = 1042
   let lamps = 2
```

```text include="mistakes/4/expected/rendered.txt#L1-L6"
[U2001] Error: argument `order` of `title` must be `U32`, found `Int`
    ╭─[ src/slip.una:44:24 ]
    │
 44 │   @console.print(title(order))
    │                        ──┬──
    │                          ╰──── argument `order` of `title` must be `U32`, found `Int`
```

*Why:* without a type, `let order = 1042` makes `order` an `Int`, and `title` takes a `U32`. The two are different types, and Una converts neither into the other on its own. The marks point at the argument, not at the `let`: the name is fine until it reaches a place that wants a `U32`.

*Fix:* write the type, `let order: U32 = 1042`, so that the literal is a `U32`. See [U2001](/docs/errors/U2001/).
:::

### A number too large for its type (U2022)

:::mistake
Give the order a number past the range of a `U32`:

```diff include="day-to-day..mistakes/5:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -37,3 +37,3 @@
 =
-  let order: U32 = 1042
+  let order: U32 = 5_000_000_000
   let lamps = 2
```

```text include="mistakes/5/expected/rendered.txt#L1-L6"
[U2022] Error: the literal `5000000000` does not fit `U32`, which holds `0` to `4294967295`
    ╭─[ src/slip.una:38:20 ]
    │
 38 │   let order: U32 = 5_000_000_000
    │                    ──────┬──────
    │                          ╰──────── the literal `5000000000` does not fit `U32`, which holds `0` to `4294967295`
```

*Why:* a `U32` holds 0 to 4294967295, and 5000000000 is larger. The check refuses the literal at once, before any proof. The message writes the literal without its `_` and gives the range of the type.

*Fix:* use a number inside the range, or, when order numbers really grow past it, a wider type, `U64`, in `title` and in `main`. See [U2022](/docs/errors/U2022/).
:::

### One name made twice (U1002)

:::mistake
Copy the line of `lamps` for the rugs, and forget to change the name:

```diff include="day-to-day..mistakes/6:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -39,3 +39,3 @@
   let lamps = 2
-  let rugs = 1
+  let lamps = 1
   let units = lamps + rugs
```

```text include="mistakes/6/expected/rendered.txt#L1-L13"
[U1002] Error: `lamps` is already bound in this scope; a local cannot rebind another
    ╭─[ src/slip.una:40:7 ]
    │
 39 │   let lamps = 2
    │       ──┬──
    │         ╰──── first defined here
 40 │   let lamps = 1
    │       ──┬──
    │         ╰──── `lamps` is already bound in this scope; a local cannot rebind another
    │
    │ Note: run `una explain U1002` for an explanation
────╯
[U1001] Error: cannot find name `rugs` in this module, its imports or the prelude
```

*Why:* a body makes each name once, so the second `let lamps` is refused, with marks on both lines. Three more diagnostics follow, each U1001: the lines that use `rugs` cannot find it, since no `let` makes it now. One slip, four reports: fix the first, and the others go with it.

*Fix:* write `let rugs = 1`. See [U1002](/docs/errors/U1002/).
:::

## 2.7 Exercises

The exercises come with the chapter's download, `02-numbers.tar.gz`. Each starts from `exercises/N/start`: the day-to-day program with the exercise's examples added at the end, and a **stub** of each function to write: its header, with a body that gives back a **placeholder**, a value of the right type that is not the answer, such as the empty text `""` or `0`. `una test .` fails there until the exercise is done. Work in this order:

1. Read the examples: they say what each function must give back.
2. Write the function's body, in place of the placeholder.
3. Run `una check .`, and fix what it reports.
4. Run `una test .` until every example passes, then `una run .` to see the slip.

### Exercise 1: the weight of the parcel

::::exercise
The warehouse wants the weight on the slip, in kilograms and grams. Write `weight_line(grams)`, which turns 2350 into `Parcel weight: 2 kg 350 g`. The start package ends with:

```una include="exercises/1/start/src/slip.una#L97-L106" title="exercises/1/start/src/slip.una"
--- The weight of a parcel, in kilograms and grams: 2350 is "Parcel weight: 2 kg 350 g".
pub weight_line(grams: Int) -> Text = ""

example "a weight shows whole kilograms and the grams left over"
  do weight_line(2350)
  expect result == "Parcel weight: 2 kg 350 g"

example "a parcel under one kilogram shows 0 kg"
  do weight_line(800)
  expect result == "Parcel weight: 0 kg 800 g"
```

:::hint
*Hint:* a kilogram is 1000 grams. `/` divides two `Int` values and drops the remainder, and `mod` gives the remainder: `2350 / 1000` is 2, and `2350 mod 1000` is 350. Both can go inside the braces of a text, as in [Putting values into a text](#putting-values-into-a-text).
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L13-L20"
example slip "a weight shows whole kilograms and the grams left over" ... FAILED
  src/slip.una:102: expect result == "Parcel weight: 2 kg 350 g"
  it is false, with `result` = `""`
example slip "a parcel under one kilogram shows 0 kg" ... FAILED
  src/slip.una:106: expect result == "Parcel weight: 0 kg 800 g"
  it is false, with `result` = `""`

13 examples: 11 passed, 2 failed
```

The placeholder gives back the empty text, `""`, which is what each report shows as `result`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Give `weight_line` its body:

```diff include="exercises/1/start..exercises/1/answer:src/slip.una" context="1" title="src/slip.una"
--- a/src/slip.una
+++ b/src/slip.una
@@ -97,3 +97,3 @@
 --- The weight of a parcel, in kilograms and grams: 2350 is "Parcel weight: 2 kg 350 g".
-pub weight_line(grams: Int) -> Text = ""
+pub weight_line(grams: Int) -> Text = "Parcel weight: {grams / 1000} kg {grams mod 1000} g"
 
```

Each brace holds one computation, and the text puts the results in their places.
:::
::::

### Exercise 2: shipping and the amount to pay

::::exercise
The slip should also show the shipping charge, 450 cents for this order, and what the customer pays in all. Write `to_pay(goods, shipping)` and `pay_line(cents)`, and print two new lines after the total: `Shipping: 450 cents` and `To pay: 8930 cents`. The start package ends with:

```una include="exercises/2/start/src/slip.una#L97-L109" title="exercises/2/start/src/slip.una"
--- What the customer pays: the goods and the shipping, in cents.
pub to_pay(goods: Int, shipping: Int) -> Int = 0

--- The line with the amount to pay.
pub pay_line(cents: Int) -> Text = ""

example "shipping is added to the goods"
  do to_pay(8480, shipping: 450)
  expect result == 8930

example "the pay line is in cents"
  do pay_line(8930)
  expect result == "To pay: 8930 cents"
```

:::hint
*Hint:* `to_pay` adds its two parameters, and `pay_line` is written as `total_line` is. In `main`, give the sum of the two lines a name with `let`, so that both `total_line` and `to_pay` can use it, and print the new lines after the total.
:::

Check your answer with `una test .`, then `una run .` for the two new lines.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Give both functions their bodies, and print the new lines in `main`:

```diff include="exercises/2/start..exercises/2/answer:src/slip.una" context="1" title="src/slip.una"
--- a/src/slip.una
+++ b/src/slip.una
@@ -49,3 +49,6 @@
   @console.print(box_line(boxes(units)))
-  @console.print(total_line(lamp_cents + rug_cents))
+  let goods = lamp_cents + rug_cents
+  @console.print(total_line(goods))
+  @console.print("Shipping: 450 cents")
+  @console.print(pay_line(to_pay(goods, shipping: 450)))
   @console.print(closing())
@@ -97,6 +100,6 @@
 --- What the customer pays: the goods and the shipping, in cents.
-pub to_pay(goods: Int, shipping: Int) -> Int = 0
+pub to_pay(goods: Int, shipping: Int) -> Int = goods + shipping
 
 --- The line with the amount to pay.
-pub pay_line(cents: Int) -> Text = ""
+pub pay_line(cents: Int) -> Text = "To pay: {cents} cents"
 
```

`goods` names the sum once, and two lines use it. `to_pay(goods, shipping: 450)` labels its second argument, as every argument after the first is labeled.
:::
::::

### Exercise 3: amounts with two decimals

::::exercise
Customers read `84.80` more easily than `8480 cents`. Write `amount(cents)`, which writes an amount of cents with two decimals, and use it in `total_line`, so that the slip says `Total paid: 84.80`. Watch the cents under ten: 1205 is `12.05`, not `12.5`. The start package ends with:

```una include="exercises/3/start/src/slip.una#L97-L110" title="exercises/3/start/src/slip.una"
--- An amount of cents with two decimals: 8480 is "84.80", and 1205 is "12.05".
pub amount(cents: Int) -> Text = ""

example "an amount has two decimals"
  do amount(8480)
  expect result == "84.80"

example "cents under ten keep their zero"
  do amount(1205)
  expect result == "12.05"

example "less than one unit starts with 0"
  do amount(7)
  expect result == "0.07"
```

:::hint
*Hint:* write the whole units, a point, and then the two digits of the cents one by one: the tens of cents and the cents left over. Each is a `/` or a `mod` of `cents`, or both. For 1205: the units are `1205 / 100`, 12; the cents are `1205 mod 100`, 5; the tens of cents are `5 / 10`, 0; and the last digit is `5 mod 10`, 5.
:::

Check your answer with `una test .`, then `una run .` for the new total. The example of `total_line` must change too, since the line it tests changes.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Give `amount` its body, and use it in `total_line` and its example:

```diff include="exercises/3/start..exercises/3/answer:src/slip.una" context="1" title="src/slip.una"
--- a/src/slip.una
+++ b/src/slip.una
@@ -28,3 +28,3 @@
 --- What the customer paid for the goods, in cents.
-pub total_line(cents: Int) -> Text = "Total paid: {cents} cents"
+pub total_line(cents: Int) -> Text = "Total paid: {amount(cents)}"
 
@@ -92,8 +92,8 @@
 
-example "the total is in cents"
+example "the total is an amount"
   do total_line(8480)
-  expect result == "Total paid: 8480 cents"
+  expect result == "Total paid: 84.80"
 
 --- An amount of cents with two decimals: 8480 is "84.80", and 1205 is "12.05".
-pub amount(cents: Int) -> Text = ""
+pub amount(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"
 
```

`cents mod 100 / 10` is the tens of cents, and `cents mod 10` the cents left over, so each digit is printed on its own and a zero is never lost. This works for an amount that is not negative; a refund would need the rule of [Euclidean division](#euclidean-division), and a choice that [section 3.4](/learn/text-and-conditions/#s3-4) teaches.
:::
::::

## 2.8 Recap and reference

### For agents

:::agents
`una --json check .` prints each diagnostic with its `code`, `message`, `primary` span and `repairs`; `una --json test .` prints each example's outcome. U0007 carries an exact edit, the literal rewritten, which `una fix .` applies. U5001 gives a counterexample and repairs that are descriptions only (a guard, a wider type, a wrapping or saturating method). U0101, U1001, U1002, U2001 and U2022 depend on intent, so they carry no repair. The compact rule: *`Int` is unbounded and exact, with Euclidean `/` and `mod`; money is `Int` cents; every division by a value that is not a nonzero literal, and every operation or narrowing on `U8`…`U64`, `I8`…`I64`, is a proof obligation; types never convert implicitly.*
:::

### Recap

:::recap
- Every value has a type. `print` takes a `Text`; put a number into one with braces: `"{units} units"`.
- `let name = value` names a value; `let name: Type = value` also states its type. A body makes each name once.
- `Int` is a whole number of any size, so a sum or a product is exact.
- Keep money in `Int` cents, and divide last: `order * 15 / 100`.
- `*`, `/` and `mod` come before `+` and `-`, left to right; parentheses change the order.
- `/` and `mod` are Euclidean. A divisor that may be zero is refuted with a counterexample.
- A fixed-width type, such as `U8`, is for a number of a set size. Every operation on it is proved to fit; wrapping and saturating are methods.
- Integer types never mix: convert with `to_int()`, or narrow with `to_u8()` and its proof.
:::

### Reference

:::reference
- Construct pages: [source files, comments and literals](/docs/language/lexical-structure/), [functions](/docs/language/functions/), [`example`](/docs/language/examples/example/)
- Commands: [`una check`](/docs/cli/check/), [`una run`](/docs/cli/run/), [`una test`](/docs/cli/test/), [`una fix`](/docs/cli/fix/), [`una explain`](/docs/cli/explain/)
- Standard library: [the prelude](/docs/std/) (`abs`, `min`, `max`)
- Diagnostics: [U0007](/docs/errors/U0007/), [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2022](/docs/errors/U2022/), [U5001](/docs/errors/U5001/)
- Specification: [lexical structure](/docs/spec/01-lexical-structure/), [grammar](/docs/spec/02-grammar/), [types](/docs/spec/03-types/), [dynamic semantics](/docs/spec/11-dynamic-semantics/), [verification](/docs/spec/12-verification/), [the standard library](/docs/spec/14-standard-library/), [fixed-width integers](/docs/spec/18-fixed-width-integers/)
:::
