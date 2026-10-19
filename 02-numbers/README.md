---
learn: "2"
title: Numbers
editions: ["0.2", "0.3"]
codes: [U0007, U0101, U1001, U1002, U2001, U2022, U2033, U5001]
time: 80
builds: A packing slip that a store prints for the box of one order, with examples that test each line
prerequisites: ["1"]
template: 2
nav: ["Values, types and let", "Whole numbers: Int", "Fixed-width integers", "Numbers with a fraction: F64", "Converting and rounding", "Special values of F64", "Day-to-day: a packing slip", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 2 Numbers

A store counts all day: units on a shelf, lines of an order, boxes for a parcel, prices in cents. In chapter 1 every value your programs used was a text. This chapter adds numbers. You learn what a value and its type are, how to give a value a name with `let`, and how to print a number. Then you meet Una's whole numbers, `Int`, which never overflow, the fixed-width integers, such as `U8`, for the places where a number must fit a set size, and `F64`, for measurements with a fraction, such as a weight in kilograms. You end with the packing slip that goes into the box of an order, checked, run and tested.

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
2. **Inexact numbers have a type of their own.** An amount such as 19.90 is counted in whole cents, the `Int` 1990. A measurement with a fraction is an `F64`, which never mixes with an integer, and nothing rounds unless the code says how.
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

The message says that `19.90` is a **fractional literal**, a number with a fraction, and that Una's integer literals are written in decimal digits only. In edition `0.2`, the edition of this package, Una has no type for numbers with a fraction.

For money, whole cents work well. Many languages store a fraction such as 0.10 as a binary approximation, so that adding prices gives totals such as 0.30000000000000004, and every program rounds them in its own way, often without saying so. With whole cents, every sum and product is exact, and the one place a fraction appears, a division, says how it rounds. Money is an `Int` of cents in this chapter and in every chapter of this book.

### Numbers with a fraction

Edition `0.3` adds a type for numbers with a fraction: `F64`, a **floating-point** number, which holds approximate values over a very wide range, for measurements, where a tiny rounding error does not matter. [Section 2.4](#s2-4) teaches it. It is not a type for money: an `F64` holds 19.90 only approximately. A **decimal** type, which will hold amounts such as 19.90 exactly, in base ten, as people write them, is planned for a later edition. Until then, keep money in cents, as `Int`.

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
| A measure with a fraction | `F64` in edition `0.3` ([section 2.4](#s2-4)), or `Int` in a smaller unit, such as grams or millimeters |
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
- **Lengths stay `Int`.** The length of a text, which [section 3.1](/learn/text-and-conditions/#s3-1) shows, is always an `Int`.

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

## 2.4 Numbers with a fraction: `F64`

### What a floating-point number is

Some numbers in a store are not counts. A desk lamp weighs 1.25 kilograms, a box is 30.5 centimeters long, and the reviews of a product give it 4.3 stars on average. Each of these is a **measurement**: a number with a fraction, read from a scale or a ruler, or computed from other measurements.

A **floating-point number** holds such a value as a row of digits and the place where the point goes, as scientific notation writes 1.25 × 10³ for 1250. The point "floats" to wherever the value needs it, so one type holds both the weight of a stamp and the distance to the moon. Una's floating-point type is `F64`: a number stored in 64 bits, with about 16 significant digits, from about 5 × 10⁻³²⁴ up to about 1.8 × 10³⁰⁸, positive or negative.

Those 64 bits hold a fixed number of binary digits, so most fractions are not stored exactly. Think of a ruler with very fine marks: a length that falls between two marks is read as the nearest one. `0.1` is stored as the nearest value the 64 bits can hold, which is a tiny bit more than one tenth. For a measurement that is fine, since the scale itself is less precise than that. For money it is not, which is why money stays in whole cents.

> [!NOTE]
> `F64` belongs to edition `0.3`, a preview ([section 19.3](/learn/editions/#s19-3)). Every step of sections 2.4 to 2.6 says `edition = "0.3"` in its `una.toml`. In editions `0.1` and `0.2`, `1.25` is an error, as [Why money is whole cents](#why-money-is-whole-cents) shows, and `F64` is an ordinary name.

### Why a store measures with `F64`

[Why money is whole cents](#why-money-is-whole-cents) wrote a price with a decimal point, and edition `0.2` refused it. Change only the edition of that package:

```diff include="steps/09-fraction..steps/22-fraction-0-3:una.toml" title="una.toml" context="0"
--- a/una.toml
+++ b/una.toml
@@ -4 +4 @@
-edition = "0.2"
+edition = "0.3"
```

Now the package checks, and `una run .` prints:

```text include="steps/22-fraction-0-3/expected/output.txt"
19.9
```

The line `let lamp = 19.90` is the same, and now it gives an `F64`. Look at what it prints: `19.9`, not `19.90`. An `F64` is a number, not the way it was written, and a number has no trailing zeros to keep. A price tag needs exactly two digits after the point, and a total of prices needs to be exact to the cent, so a price stays an `Int` of cents. `F64` is for the other numbers with a fraction: weights, lengths, volumes, ratings and averages, where the value is a measurement and the last digit does not matter.

### How to write an `F64`

#### The edition in `una.toml`

A package that uses `F64` names edition `0.3`:

```toml include="steps/23-floats/una.toml" title="steps/23-floats/una.toml"
[package]
name = "floats"
version = "0.1.0"
edition = "0.3"

[run]
entry = "floats"
grants = ["console"]
```

#### Float literals

A **float literal** is a number written with a point: `1.25`, `3.5`, `0.75`. It is always an `F64`.

- Write digits on both sides of the point: `0.5`, not `.5`, and `5.0`, not `5.`.
- Group the digits with `_`, between two digits only: `1_250.5`.
- Add a power of ten with `e`: `2.5e3` is 2.5 × 10³, so 2500.0, and `1.5e-3` is 1.5 × 10⁻³, so 0.0015. The `e` is lowercase, a negative exponent takes `-`, and there is no `+`.
- The whole part has no leading zero, except `0` itself: `0.5`, not `00.5`.

A number that breaks one of these rules, such as `.5`, `1.`, `1e5`, `1.0E5` or `1.0e+5`, does not check (U0007), and the message shows the form to write instead. An integer literal never becomes an `F64`: where an `F64` is expected, write `5000.0`, not `5000`. [Integers and `F64` do not mix](#integers-and-f64-do-not-mix) shows what `una check` says.

#### A negative value

Put a minus sign in front, as for an `Int`: `-1.25`, or `-lamp_kg` for a name. When a method is called on a negative literal, put the literal in parentheses: `(-7.5).abs()`. Without them, `-7.5.abs()` would call `abs` on `7.5` first, and then make the result negative.

#### Arithmetic on `F64`

`+`, `-`, `*` and `/` work on two `F64` values and give an `F64`, in the same order as on `Int` ([section 2.2](#the-order-of-operations)): `*` and `/` before `+` and `-`, left to right, and parentheses first. `/` keeps the fraction: `7.0 / 2.0` is 3.5. There is no `mod` on `F64`.

#### Methods

An `F64` has methods, called with a dot as `copies.to_int()` is in [section 2.3](#method-calls):

| Method | Gives | Example |
| --- | --- | --- |
| `x.abs()` | `x` without its minus sign | `(-7.5).abs()` is 7.5 |
| `x.sqrt()` | the square root of `x` | `2.0.sqrt()` is 1.4142135623730951 |
| `x.rem(by: y)` | the remainder of `x` divided by `y`, with the sign of `x` | `7.5.rem(by: 2.0)` is 1.5 |

[Section 2.5](#s2-5) adds the methods that convert and round, and [section 2.6](#s2-6) those that compare and test special values.

### Each float form at work

The step writes each form, with two weights in kilograms:

```una include="steps/23-floats/src/floats.una#L7-L14" title="steps/23-floats/src/floats.una"
  let lamp_kg = 1.25
  let rug_kg = 3.5
  @console.print("{lamp_kg} and {rug_kg}")
  @console.print("{lamp_kg + rug_kg}, {rug_kg - lamp_kg}, {lamp_kg * 4.0} and {rug_kg / 2.0}")
  @console.print("{-lamp_kg} and {(lamp_kg + rug_kg) * 2.0}")
  @console.print("{1_250.5}, {2.5e3}, {1.5e-3} and {6.0e-7}")
  @console.print("{1.0e20} and {1.0e21}")
  @console.print("{2.0.sqrt()}, {(-7.5).abs()} and {7.5.rem(by: 2.0)}")
```

```text include="steps/23-floats/expected/output.txt#L1-L6"
1.25 and 3.5
4.75, 2.25, 5.0 and 1.75
-1.25 and 9.5
1250.5, 2500.0, 0.0015 and 6.0e-7
100000000000000000000.0 and 1.0e21
1.4142135623730951, 7.5 and 1.5
```

- `lamp_kg * 4.0` is `5.0`. A whole `F64` is printed with `.0`, so it never looks like an `Int`.
- `1_250.5` prints as `1250.5`: the `_` is for the reader of the code only.
- `2.5e3` prints as `2500.0`, and `1.5e-3` as `0.0015`. A very small or very large value prints with `e`: `6.0e-7` and `1.0e21`.
- `2.0.sqrt()` calls `sqrt` on the literal `2.0`. The point that follows a digit starts the fraction; the point after the fraction calls the method.

### Weighing a parcel by its volume

A carrier bills a light but bulky parcel by the room it takes in the truck. Its **volumetric weight** is its length times its width times its height, in centimeters, divided by 5000, and the parcel is billed by its weight on the scale or its volumetric weight, whichever is greater:

:::steps
```una include="steps/24-parcel/src/parcel.una" title="steps/24-parcel/src/parcel.una" verified="check, run"
module parcel

--- The volumetric weight of a box in kilograms: its volume in cubic centimeters, divided by 5000.
pub volumetric_kg(length_cm: F64, width_cm: F64, height_cm: F64) -> F64 = length_cm * width_cm * height_cm / 5000.0

--- The weight a carrier bills a parcel by: its weight on the scale or its volumetric weight,
--- whichever is greater.
pub billed_kg(scale_kg: F64, length_cm: F64, width_cm: F64, height_cm: F64) -> F64
=
  let volume_kg = volumetric_kg(length_cm, width_cm: width_cm, height_cm: height_cm)
  max(scale_kg, b: volume_kg)

--- Prints the weights of two parcels: a desk lamp, and a rolled rug.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp_box = volumetric_kg(30.0, width_cm: 20.0, height_cm: 15.0)
  let rug_box = volumetric_kg(120.0, width_cm: 25.0, height_cm: 25.0)
  @console.print("Lamp box: {lamp_box} kg by volume")
  @console.print("Rug box: {rug_box} kg by volume")
  let lamp_billed = billed_kg(2.6, length_cm: 30.0, width_cm: 20.0, height_cm: 15.0)
  let rug_billed = billed_kg(4.2, length_cm: 120.0, width_cm: 25.0, height_cm: 25.0)
  @console.print("Lamp parcel billed at {lamp_billed} kg")
  @console.print("Rug parcel billed at {rug_billed} kg")
```

1. **`volumetric_kg(length_cm: F64, width_cm: F64, height_cm: F64) -> F64`.** Three measurements in, one out, all `F64`.
2. **`length_cm * width_cm * height_cm / 5000.0`.** The divisor is the float literal `5000.0`, since an `F64` divides only by an `F64`.
3. **`max(scale_kg, b: volume_kg)`.** The prelude's `max` of [section 2.2](#functions-on-whole-numbers-abs-min-and-max) takes two `F64` values too, and gives the greater.
4. **`volumetric_kg(30.0, width_cm: 20.0, height_cm: 15.0)`.** Each argument is a float literal. `30` would not check here.
:::

`una run .` prints:

```text include="steps/24-parcel/expected/output.txt"
Lamp box: 1.8 kg by volume
Rug box: 15.0 kg by volume
Lamp parcel billed at 2.6 kg
Rug parcel billed at 15.0 kg
```

The lamp's box takes little room, 1.8 kilograms by volume, so the scale's 2.6 kilograms is billed. The rolled rug weighs 4.2 kilograms, but its long box counts as 15 kilograms, and that is what the carrier bills.

### How `F64` behaves

#### Most fractions are approximate

An `F64` holds the binary value nearest to each literal, and each operation gives the value nearest to the exact result. Most of the time the printed result is the one you expect. Sometimes the tiny differences show:

```una include="steps/23-floats/src/floats.una#L15" title="steps/23-floats/src/floats.una"
  @console.print("{0.1 + 0.2} and {1.0 / 3.0}")
```

```text include="steps/23-floats/expected/output.txt#L7"
0.30000000000000004 and 0.3333333333333333
```

Neither `0.1` nor `0.2` is stored exactly, and their sum lands on a value just above the one nearest to `0.3`, so it prints with all its digits. `1.0 / 3.0` stops after about 16 digits. Una computes every operation by the same rule on every machine, in the interpreter and in a built program alike, so a program prints the same digits everywhere. The rule does not make the values exact. That is why a total of prices is an `Int` of cents.

#### Printing an `F64`

An `F64` in braces goes into the text as the shortest row of digits that reads back as the same value: `1.25`, `0.0015`, `0.30000000000000004`. There is always at least one digit after the point. A value from 0.000001 up to below 10²¹ is written with all its digits; a smaller or larger one with `e`:

```una include="steps/23-floats/src/floats.una#L12-L13" title="steps/23-floats/src/floats.una"
  @console.print("{1_250.5}, {2.5e3}, {1.5e-3} and {6.0e-7}")
  @console.print("{1.0e20} and {1.0e21}")
```

```text include="steps/23-floats/expected/output.txt#L4-L5"
1250.5, 2500.0, 0.0015 and 6.0e-7
100000000000000000000.0 and 1.0e21
```

Every printed `F64` is itself a float literal, after its sign, so you can paste it into a program and get the same value back.

#### Integers and `F64` do not mix

An operator takes two values of one type, as for the fixed-width integers. Write the divisor of `volumetric_kg` as the integer `5000`:

```diff include="steps/24-parcel..steps/25-float-integer:src/parcel.una" title="src/parcel.una" context="0"
--- a/src/parcel.una
+++ b/src/parcel.una
@@ -4 +4 @@
-pub volumetric_kg(length_cm: F64, width_cm: F64, height_cm: F64) -> F64 = length_cm * width_cm * height_cm / 5000.0
+pub volumetric_kg(length_cm: F64, width_cm: F64, height_cm: F64) -> F64 = length_cm * width_cm * height_cm / 5000
```

```text include="steps/25-float-integer/expected/rendered.txt#L1,L8"
[U2001] Error: the integer literal `5000` is not an `F64`; a float literal has a point
   │ Help: repair 1: write `5000.0`; edit src/parcel.una:4:110..4:114 to "5000.0"
```

The message says that `5000` is an integer literal, and that an `F64` needs a float literal, with a point. The help line is an exact edit, to `5000.0`, so `una fix .` can apply it. For a name that holds an integer, such as a count of boxes, you convert it instead, with `to_f64()`, which [section 2.5](#s2-5) teaches.

#### Division by zero gives a value, not an error

On `Int`, a division by a value that may be zero is refused before the program runs ([section 2.2](#division-by-zero-a-proof-obligation)). On `F64`, every operation has a result, and none stops the program: `1.0 / 0.0` is an infinity, and `0.0 / 0.0` is a value that is not a number. [Section 2.6](#s2-6) shows these values and how to test for them.

### `Int`, fixed width or `F64`

:::decide
**Which to use:**

| The number… | Use |
| --- | --- |
| Is a count of whole things | `Int` |
| Is money | `Int` cents, never `F64` |
| Is read or written in a set number of bits by a device or a format | a fixed-width integer |
| Is a measurement with a fraction: a weight, a length, a rating | `F64`, in edition `0.3` |
| Is an average or a ratio of two counts | `F64`, converting the counts with `to_f64()` |
:::

### Check yourself: `F64`

The last line of `floats` adds two pairs of literals:

```una include="steps/23-floats/src/floats.una#L16" title="steps/23-floats/src/floats.una"
  @console.print("{1.10 + 2.20} and {1.5 + 2.25}")
```

What does it print? One of the two sums prints exactly as a person would write it, and the other does not. Which, and why?

:::answer Show the answer
```text include="steps/23-floats/expected/output.txt#L8"
3.3000000000000003 and 3.75
```

`1.5` is 1 + 1/2, and `2.25` is 2 + 1/4. Halves and quarters are binary fractions, so both are stored exactly, and so is their sum, 3.75. `1.10` and `2.20` are tenths, which no binary digits hold exactly, so their sum lands one step away from the value nearest to 3.3, and prints with every digit.
:::

## 2.5 Converting and rounding

### What a conversion is

A **conversion** makes a value of one type from a value of another: an `F64` from an `Int`, or an `Int` from an `F64`. **Rounding** is part of the second: 2.7 kilograms becomes 2 or 3 whole kilograms only by a rule that says which. Think of a cashier who weighs loose coffee: the scale shows 0.347 kilograms, and the store's rule decides whether the receipt says 347 grams or 350.

### Why conversions are written

A program often mixes counts and measurements. The average rating of a product is the total of its stars, an `Int`, divided by its number of reviews, another `Int`, and the result is an `F64`. Divide an `F64` by the `Int` count of reviews, and `una check` stops:

```diff include="steps/27-label..steps/28-int-operand:src/label.una" title="src/label.una" context="0"
--- a/src/label.una
+++ b/src/label.una
@@ -10 +10 @@
-pub average_stars(total_stars: Int, reviews: Int) -> F64 = total_stars.to_f64() / reviews.to_f64()
+pub average_stars(total_stars: Int, reviews: Int) -> F64 = total_stars.to_f64() / reviews
```

```text include="steps/28-int-operand/expected/rendered.txt"
[U2001] Error: an operand of `/` must be `F64`, found `Int`
    ╭─[ src/label.una:10:83 ]
    │
 10 │ pub average_stars(total_stars: Int, reviews: Int) -> F64 = total_stars.to_f64() / reviews
    │                                                                                   ───┬───
    │                                                                                      ╰───── an operand of `/` must be `F64`, found `Int`
    │
    │ Help: repair 1: convert the integer with `to_f64()`; edit src/label.una:10:83..10:90 to "(reviews).to_f64()"
    │
    │ Note: run `una explain U2001` for an explanation
────╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

The message says that an operand of `/` must be an `F64` and is an `Int`. The help is an exact edit: convert the integer with `to_f64()`. Una never converts a number on its own, in either direction. A conversion from `F64` to an integer must round, and a program that rounds without saying how gives totals that differ from another program's by a cent here and a gram there. So each conversion is a method you write, and each rounding has a name that says its rule.

### How to convert and round

#### From an integer: `to_f64()`

`n.to_f64()` gives the `F64` of an `Int` or of a fixed-width integer: `3.to_f64()` is `3.0`. Every integer from −9,007,199,254,740,992 to 9,007,199,254,740,992 (2⁵³) converts exactly. A larger one becomes the nearest `F64`, as [Large integers are rounded](#large-integers-are-rounded) shows. It never fails.

#### Back to an integer: `to_int_exact()`

`x.to_int_exact()` gives the `Int` of an `F64` that is a whole number, and nothing for any other. Its result is an `Option[Int]`: either `Some(n)`, which holds the `Int` `n`, or `None`, which holds nothing. [Section 7.1](/learn/failure/#s7-1) teaches `Option` in full; here it is enough to print one. `2.0.to_int_exact()` is `Some(2)`, and `2.5.to_int_exact()` is `None`, since 2.5 has a fraction. To get an `Int` from 2.5, round it first, then convert: `2.5.floor().to_int_exact()` is `Some(2)`.

#### Rounding to a whole number

Each rounding method gives an `F64` with no fraction. They differ in which way they go:

| Method | Goes | `2.5` gives | `-2.5` gives |
| --- | --- | --- | --- |
| `x.floor()` | down, toward minus infinity | 2.0 | -3.0 |
| `x.ceil()` | up, toward plus infinity | 3.0 | -2.0 |
| `x.trunc()` | toward zero: drops the fraction | 2.0 | -2.0 |
| `x.round_half_even()` | to the nearest; a tie goes to the even neighbor | 2.0 | -2.0 |
| `x.round_half_away()` | to the nearest; a tie goes away from zero | 3.0 | -3.0 |

A **tie** is a value exactly halfway between two whole numbers, such as 2.5. Rounding a tie to the even neighbor, as many accounting and measurement standards do, sends half the ties up and half down, so a long column of rounded values does not drift upward. Rounding a tie away from zero is the rule most people learned at school.

#### Reading a number from a text: `parse_f64`

`parse_f64("2.75")` reads an `F64` from a text, as a program does with a weight typed by a person or sent by a scale. A text that is not a number makes it fail, so it is called with `attempt`, which keeps the outcome as a value: `Ok` with the number, or `Err` with the reason. [Section 7.4](/learn/failure/#s7-4) teaches `attempt`. The text is read as JSON writes numbers: `2.75`, `-0.5`, `1e3` and `1E+3` are read, and `2,75` and ` 2.75` (with a space) are not.

### Each conversion at work

```una include="steps/26-conversions/src/convert.una#L7-L15" title="steps/26-conversions/src/convert.una"
  let boxes = 3
  let tape_m: U8 = 12
  @console.print("{boxes.to_f64()} and {tape_m.to_f64()}")
  @console.print("{2.0.to_int_exact()}, {2.5.to_int_exact()} and {(-0.0).to_int_exact()}")
  @console.print("{2.5.floor()}, {2.5.ceil()} and {(-2.5).trunc()}")
  @console.print("{2.5.round_half_even()}, {3.5.round_half_even()} and {2.5.round_half_away()}")
  @console.print("{(-2.5).floor()}, {(-2.5).ceil()} and {(-2.5).round_half_away()}")
  @console.print("{2.7.floor().to_int_exact()} and {infinity().to_int_exact()}")
  @console.print("{9007199254740993.to_f64()}")
```

```text include="steps/26-conversions/expected/output.txt#L1-L7"
3.0 and 12.0
Some(2), None and Some(0)
2.0, 3.0 and -2.0
2.0, 4.0 and 3.0
-3.0, -2.0 and -3.0
Some(2) and None
9007199254740992.0
```

- `tape_m` is a `U8`, and `to_f64()` converts it as it converts the `Int` `boxes`.
- `(-0.0).to_int_exact()` is `Some(0)`: the integer zero has no sign. [Section 2.6](#s2-6) explains `-0.0`.
- On the line of ties, `round_half_even()` sends 2.5 down to 2.0 and 3.5 up to 4.0, the even neighbor each time. `round_half_away()` sends 2.5 up to 3.0.
- `infinity().to_int_exact()` is `None`: no integer is infinite.

The step then reads two texts:

```una include="steps/26-conversions/src/convert.una#L16-L18" title="steps/26-conversions/src/convert.una"
  let read = attempt parse_f64("2.75")
  let misread = attempt parse_f64("2,75")
  @console.print("{read} and {misread}")
```

```text include="steps/26-conversions/expected/output.txt#L8"
Ok(2.75) and Err(NotADigit(1))
```

`NotADigit(1)` says where the reading stopped: at position 1, the comma, counting from 0.

### A parcel label and a product rating

The step prints the weight of a parcel for a label printer that takes whole grams, the whole kilograms a carrier bills, and the rating of a product:

:::steps
```una include="steps/27-label/src/label.una" title="steps/27-label/src/label.una" verified="check, run"
module label

--- The weight of a parcel in whole grams, for the label printer: to the nearest gram, ties to even.
pub grams(weight_kg: F64) -> Option[Int] = (weight_kg * 1000.0).round_half_even().to_int_exact()

--- The whole kilograms a carrier bills: every kilogram started counts, so the weight is rounded up.
pub billed_kilograms(weight_kg: F64) -> Option[Int] = weight_kg.ceil().to_int_exact()

--- The average of the star ratings of a product, each rating from 1 to 5.
pub average_stars(total_stars: Int, reviews: Int) -> F64 = total_stars.to_f64() / reviews.to_f64()

--- A value shown with one digit after the point: 4.2857 is shown as 4.3.
pub one_decimal(x: F64) -> F64 = (x * 10.0).round_half_away() / 10.0

--- Prints the label of a parcel, and the rating of a product.
pub main() -> Unit
  uses @console: Console[print]
=
  let weight_kg = 2.3456
  @console.print("Weight in grams: {grams(weight_kg)}")
  @console.print("Billed kilograms: {billed_kilograms(weight_kg)}")
  let stars = average_stars(30, reviews: 7)
  @console.print("Rating: {stars}, shown as {one_decimal(stars)}")
  @console.print("No reviews: {average_stars(0, reviews: 0)}, and in grams {grams(nan())}")
```

1. **`(weight_kg * 1000.0).round_half_even().to_int_exact()`.** Kilograms to grams, rounded to the nearest gram, then converted. The result is an `Option[Int]`, since a weight that is not a number has no grams.
2. **`weight_kg.ceil().to_int_exact()`.** The carrier counts every kilogram started, so the weight is rounded up.
3. **`total_stars.to_f64() / reviews.to_f64()`.** Both counts converted, then divided, so the average keeps its fraction. An `Int` division would give 4, not 4.28.
4. **`(x * 10.0).round_half_away() / 10.0`.** One digit after the point: 42.857 is rounded to 43.0, and divided back to 4.3.
5. **`average_stars(0, reviews: 0)`.** A product with no reviews. The division is by `0.0`, an `F64`, so it is not refused; it gives a value that is not a number.
:::

`una run .` prints:

```text include="steps/27-label/expected/output.txt"
Weight in grams: Some(2346)
Billed kilograms: Some(3)
Rating: 4.285714285714286, shown as 4.3
No reviews: nan, and in grams None
```

The last line shows the two ends of an empty case: the average prints as `nan`, "not a number", and its grams are `None`. [Section 2.6](#s2-6) shows how to test for it before it reaches a label.

### How conversions behave

#### `to_int` is not a conversion of `F64`

The integer types convert with `to_int()` ([section 2.3](#converting-between-integer-types)). An `F64` does not:

```diff include="steps/27-label..steps/29-to-int:src/label.una" title="src/label.una" context="0"
--- a/src/label.una
+++ b/src/label.una
@@ -7 +7 @@
-pub billed_kilograms(weight_kg: F64) -> Option[Int] = weight_kg.ceil().to_int_exact()
+pub billed_kilograms(weight_kg: F64) -> Int = weight_kg.ceil().to_int()
```

```text include="steps/29-to-int/expected/rendered.txt#L1,L8"
[U2001] Error: `to_int` is not a conversion of `F64`; `to_int_exact()` gives `Some` of an integral value and `None` otherwise
   │ Help: repair 1: write `x.to_int_exact()`, after `floor()`, `ceil()`, `trunc()` or a rounding when the value may have a fraction
```

The message says that `to_int_exact()` is the conversion, and the help says to round first when the value may have a fraction. A conversion that rounds on its own would hide which way it rounds, and one that stops the program on 2.5 would fail in front of a customer. `to_int_exact()` does neither: it gives `None`, and the code says what happens then.

#### No `round()`

There is no method named `round`. Each rounding method's name says how it treats a tie, so a reader never has to guess.

#### Large integers are rounded

An `F64` holds about 16 significant digits, so a larger integer becomes the nearest `F64`:

```una include="steps/26-conversions/src/convert.una#L15" title="steps/26-conversions/src/convert.una"
  @console.print("{9007199254740993.to_f64()}")
```

```text include="steps/26-conversions/expected/output.txt#L7"
9007199254740992.0
```

9,007,199,254,740,993 is one more than 2⁵³, and the nearest `F64` is one less. Counts in a store are far below that, but an identifier or an amount in a smaller unit can reach it: keep those as `Int`.

#### Every rounding keeps special values

A rounding method keeps an infinity, a value that is not a number and the sign of a zero as they are: `infinity().floor()` is still an infinity. Only `to_int_exact()` turns them into `None`.

### Which rounding to use

:::decide
**Which to use:**

| You need… | Use |
| --- | --- |
| Whole units started, such as billed kilograms or boxes to order | `ceil()`, then `to_int_exact()` |
| Whole units completed, such as full boxes from a length of tape | `floor()`, then `to_int_exact()` |
| The nearest value, in a long column that must not drift | `round_half_even()` |
| The nearest value, as a person rounds by hand | `round_half_away()` |
| To drop the fraction, whatever the sign | `trunc()` |
| An `F64` from a count | `to_f64()` |
:::

### Check yourself: rounding

The last line of `convert` rounds a negative tie three ways:

```una include="steps/26-conversions/src/convert.una#L19" title="steps/26-conversions/src/convert.una"
  @console.print("{(-1.5).round_half_even()}, {(-1.5).round_half_away()} and {(-1.5).trunc()}")
```

What does it print?

:::answer Show the answer
```text include="steps/26-conversions/expected/output.txt#L9"
-2.0, -2.0 and -1.0
```

-1.5 lies halfway between -1 and -2. The even neighbor is -2, so `round_half_even()` gives -2.0. Away from zero is -2 too. `trunc()` drops the fraction and keeps -1.0.
:::

## 2.6 Special values and comparing `F64`

### What the special values are

Besides ordinary numbers, an `F64` has a few values that answer the questions an `Int` would refuse:

- **Infinity**, `inf`, and minus infinity, `-inf`: what a division by zero gives, or a result too large for 64 bits.
- **Not a number**, `nan`: what an operation without a meaningful result gives, such as `0.0 / 0.0` or the square root of `-1.0`.
- **Minus zero**, `-0.0`: a zero that remembers it came from the negative side, such as a negative weight too small to hold.

Think of the display of a scale: besides a weight, it can show "overload" or "error". The display has to show something, and a program has to test for those readings before it prints a label with them.

### Why Una gives them one meaning

Most languages compare `F64` values by the rules of the hardware, and those rules surprise. A `nan` is not equal to itself, so a list that holds one cannot find it, and a sort that meets one can put the other values in a wrong order. `-0.0` and `0.0` are equal, yet `1.0 / -0.0` and `1.0 / 0.0` differ.

Una makes `==` and `<` plain:

- **`==` is identity.** Two values are equal when they are the same value, bit for bit. So `nan() == nan()` is `true`, and `-0.0 == 0.0` is `false`.
- **`<` is one order of every value:** minus infinity, the negative numbers, `-0.0`, `0.0`, the positive numbers, infinity, and `nan` last. So `sort` always gives the same list.
- **The hardware's comparisons are methods**, named `ieee_eq`, `ieee_lt` and so on, for the code that means them.

Where the two meanings would differ, comparing with a literal zero, `una check` asks which one you mean.

### How to write and test special values

#### `nan()`, `infinity()` and `-infinity()`

There are no literals for the special values. The prelude gives `nan()` and `infinity()`, and `-infinity()` is the negative one. Printed, they are `nan`, `inf` and `-inf`.

#### Minus zero

`-0.0` is minus zero, and so is `-x` when `x` is `0.0`. It prints as `-0.0`.

#### `==` and `<`

`==`, `!=`, `<`, `<=`, `>` and `>=` compare two `F64` values by identity and by the one order. They are what `sort`, `min`, `max` and a map's keys use too.

#### The IEEE comparisons

| Method | Is `true` when |
| --- | --- |
| `x.ieee_eq(other: y)` | `x` equals `y`, with `-0.0` equal to `0.0`, and `nan` equal to nothing |
| `x.ieee_ne(other: y)` | `ieee_eq` is not true |
| `x.ieee_lt(other: y)`, `ieee_le`, `ieee_gt`, `ieee_ge` | `x` is less than (or equal, greater, greater or equal) `y`; always `false` when either is `nan` |

#### Testing a value

| Method | Is `true` when `x` is |
| --- | --- |
| `x.is_nan()` | `nan` |
| `x.is_finite()` | neither `nan` nor an infinity |
| `x.is_infinite()` | `inf` or `-inf` |
| `x.is_sign_negative()` | negative, `-0.0` included, `nan` excluded |
| `x.is_zero()` | `0.0` or `-0.0` |
| `x.is_positive_zero()`, `x.is_negative_zero()` | `0.0`; `-0.0` |

### Each special value at work

```una include="steps/30-specials/src/specials.una#L7-L17" title="steps/30-specials/src/specials.una"
  let empty_kg = 0.0
  let returned_kg = -empty_kg
  @console.print("{1.0 / empty_kg}, {-1.0 / empty_kg} and {empty_kg / empty_kg}")
  @console.print("{infinity()}, {-infinity()} and {nan()}")
  @console.print("{empty_kg} and {returned_kg}")
  @console.print("{nan() == nan()} and {empty_kg == returned_kg}")
  @console.print("{nan().ieee_eq(other: nan())} and {empty_kg.ieee_eq(other: returned_kg)}")
  @console.print("{returned_kg < empty_kg} and {returned_kg.ieee_lt(other: empty_kg)}")
  @console.print("{sort([2.5, nan(), -1.0, empty_kg, returned_kg, infinity()])}")
  @console.print("{max(nan(), b: 2.5)} and {min(nan(), b: 2.5)}")
  @console.print("{nan().is_nan()}, {infinity().is_finite()} and {returned_kg.is_zero()}")
```

```text include="steps/30-specials/expected/output.txt#L1-L9"
inf, -inf and nan
inf, -inf and nan
0.0 and -0.0
true and false
false and true
true and false
[-1.0, -0.0, 0.0, 2.5, inf, nan]
nan and 2.5
true, false and true
```

- The first line divides by zero three ways: a positive number gives `inf`, a negative one `-inf`, and zero `nan`. No line stops the program.
- `nan() == nan()` is `true`, and `empty_kg == returned_kg`, `0.0` against `-0.0`, is `false`: `==` is identity. The IEEE method says the opposite of each.
- `returned_kg < empty_kg` is `true`, since `-0.0` comes before `0.0` in the order. For `ieee_lt`, they are equal, so neither is less.
- `sort` puts `-0.0` before `0.0` and `nan` last.

### Checking a reading of the scale

A scale sends a reading for each parcel. The store uses a reading only when it is a finite weight above zero:

:::steps
```una include="steps/31-scale/src/scale.una" title="steps/31-scale/src/scale.una" verified="check, run"
module scale

--- Whether a reading of the parcel scale can be used: a finite weight above zero.
pub usable(reading_kg: F64) -> Bool = reading_kg.is_finite() and reading_kg.ieee_gt(other: 0.0)

--- Prints, for each reading of the scale, whether it can be used.
pub main() -> Unit
  uses @console: Console[print]
=
  let readings = [2.4, 0.0, -0.0, -1.5, nan(), infinity(), 0.75]
  for reading in readings
    @console.print("{reading} kg: {usable(reading)}")
```

1. **`reading_kg.is_finite()`.** Rules out `nan`, `inf` and `-inf`, the readings of a scale in error.
2. **`reading_kg.ieee_gt(other: 0.0)`.** Above zero in the IEEE sense: `0.0` and `-0.0` are both refused, and so is any negative reading.
3. **`for reading in readings`.** A `for` loop runs its indented line once for each value of the list `readings` ([chapter 9](/learn/loops/#s9-1) teaches loops, and [chapter 10](/learn/collections/#s10-1) lists).
:::

`una run .` prints:

```text include="steps/31-scale/expected/output.txt"
2.4 kg: true
0.0 kg: false
-0.0 kg: false
-1.5 kg: false
nan kg: false
inf kg: false
0.75 kg: true
```

Only 2.4 and 0.75 can go on a label.

### How special values behave

#### Comparing with a literal zero is refused (U2033)

Write the test of `usable` with `>`:

```diff include="steps/31-scale..steps/32-zero-compare:src/scale.una" title="src/scale.una" context="0"
--- a/src/scale.una
+++ b/src/scale.una
@@ -4 +4 @@
-pub usable(reading_kg: F64) -> Bool = reading_kg.is_finite() and reading_kg.ieee_gt(other: 0.0)
+pub usable(reading_kg: F64) -> Bool = reading_kg.is_finite() and reading_kg > 0.0
```

```text include="steps/32-zero-compare/expected/rendered.txt#L1,L8,L10"
[U2033] Error: `>` compares an `F64` with a literal zero, which tells `-0.0` from `0.0` by the order of `F64`
   │ Help 1: repair 1: compare as IEEE does, `-0.0` equal to `0.0`, with `reading_kg.ieee_gt(other: 0.0)`; edit src/scale.una:4:66..4:82 to "reading_kg.ieee_gt(other: 0.0)"
   │ Help 2: repair 2: test the sign bit with `reading_kg.is_sign_negative()` or `not reading_kg.is_sign_negative()`
```

The message says that `>` compares an `F64` with a literal zero, where the two meanings of a comparison part: with `>`, `nan` is above every number and `-0.0` is below `0.0`, and with the IEEE methods it is not. The checker refuses every comparison of an `F64` with `0.0` or `-0.0`, by `==`, `!=`, `<`, `<=`, `>` or `>=`, so that the code says which it means. The first help is an exact edit to `ieee_gt`, which is what `usable` means; the second tests the sign instead. For an equality, `x == 0.0`, the help is `x.is_zero()`.

#### `min` and `max` see `nan` as the greatest

`max` and `min` use the one order, where `nan` comes last:

```una include="steps/30-specials/src/specials.una#L16" title="steps/30-specials/src/specials.una"
  @console.print("{max(nan(), b: 2.5)} and {min(nan(), b: 2.5)}")
```

```text include="steps/30-specials/expected/output.txt#L8"
nan and 2.5
```

So `max(reading, b: 0.5)` gives `nan` for a `nan` reading. Test a reading with `is_finite()` before you take a maximum of it, as `usable` does.

#### Special values stay special

Every operation with a `nan` gives `nan`, and an infinity stays infinite except in operations such as `infinity() - infinity()`, which give `nan`. So one bad reading can turn a whole total into `nan`. Test the inputs, where you still know which one was wrong.

### `==`, an IEEE method or a test

:::decide
**Which to use:**

| You want to know… | Use |
| --- | --- |
| Whether two values are the same value, as a sort or a map key sees it | `==` |
| Whether two measurements are equal as numbers, `-0.0` equal to `0.0` | `x.ieee_eq(other: y)` |
| Whether a measurement is above, below or at zero | `ieee_gt`, `ieee_lt` and the others, `other: 0.0` |
| Whether a value is zero, of either sign | `x.is_zero()` |
| Whether a value can be used at all | `x.is_finite()` |
:::

### Check yourself: minus zero

The last lines of `specials` multiply a very small value by itself:

```una include="steps/30-specials/src/specials.una#L18-L19" title="steps/30-specials/src/specials.una"
  let tiny = 1.0e-300
  @console.print("{tiny * tiny}, {(tiny * tiny).is_zero()} and {-tiny * tiny}")
```

What does the line print?

:::answer Show the answer
```text include="steps/30-specials/expected/output.txt#L10"
0.0, true and -0.0
```

10⁻³⁰⁰ times 10⁻³⁰⁰ is 10⁻⁶⁰⁰, far below the smallest `F64`, so the product is a zero, and `is_zero()` says so. With a minus sign in front, the exact product is negative, so the zero is `-0.0`: minus zero comes from ordinary arithmetic, not only from a literal.
:::

## 2.7 Day-to-day: a packing slip

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

## 2.8 Testing it

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

## 2.9 Common mistakes

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

## 2.10 Exercises

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

## 2.11 Recap and reference

### For agents

:::agents
`una --json check .` prints each diagnostic with its `code`, `message`, `primary` span and `repairs`; `una --json test .` prints each example's outcome. U0007 carries an exact edit, the literal rewritten, which `una fix .` applies. U5001 gives a counterexample and repairs that are descriptions only (a guard, a wider type, a wrapping or saturating method). U0101, U1001, U1002, U2001 and U2022 depend on intent, so they carry no repair. In edition `0.3`, U2001 on an integer where an `F64` is expected, and U2033, carry exact edits. The compact rule: *`Int` is unbounded and exact, with Euclidean `/` and `mod`; money is `Int` cents; every division by a value that is not a nonzero literal, and every operation or narrowing on `U8`…`U64`, `I8`…`I64`, is a proof obligation; `F64` (edition `0.3`) is IEEE binary64, with `==` as identity; types never convert implicitly.*
:::

### Recap

:::recap
- Every value has a type. `print` takes a `Text`; put a number into one with braces: `"{units} units"`.
- `let name = value` names a value; `let name: Type = value` also states its type. A body makes each name once.
- `Int` is a whole number of any size, so a sum or a product is exact.
- Keep money in `Int` cents, and divide last: `order * 15 / 100`.
- `*`, `/` and `mod` come before `+` and `-`, left to right; parentheses change the order. `/` and `mod` are Euclidean, and a divisor that may be zero is refuted with a counterexample.
- A fixed-width type, such as `U8`, is for a number of a set size. Every operation on it is proved to fit, and it mixes with no other type: convert with `to_int()`, or narrow with `to_u8()` and its proof.
- `F64` (edition `0.3`) is for measurements, never money. Convert with `to_f64()`; back with a rounding, then `to_int_exact()`.
- Test an `F64` with `is_finite()`. `==` is identity; compare measurements with the IEEE methods.
:::

### Reference

:::reference
- Construct pages: [source files, comments and literals](/docs/language/lexical-structure/), [functions](/docs/language/functions/), [`example`](/docs/language/examples/example/)
- Commands: [`una check`](/docs/cli/check/), [`una run`](/docs/cli/run/), [`una test`](/docs/cli/test/), [`una fix`](/docs/cli/fix/), [`una explain`](/docs/cli/explain/)
- Standard library: [the prelude](/docs/std/) (`abs`, `min`, `max`, `nan`, `infinity`, `parse_f64`)
- Diagnostics: [U0007](/docs/errors/U0007/), [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2022](/docs/errors/U2022/), [U2033](/docs/errors/U2033/), [U5001](/docs/errors/U5001/)
- Specification: [lexical structure](/docs/spec/01-lexical-structure/), [grammar](/docs/spec/02-grammar/), [types](/docs/spec/03-types/), [dynamic semantics](/docs/spec/11-dynamic-semantics/), [verification](/docs/spec/12-verification/), [the standard library](/docs/spec/14-standard-library/), [fixed-width integers](/docs/spec/18-fixed-width-integers/), [numerics](/docs/spec/29-numerics/)
:::
