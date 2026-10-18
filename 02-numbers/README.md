---
learn: "2"
title: Numbers
editions: ["0.2"]
codes: [U0101, U2001, U2019, U5001]
time: 35
builds: A packing slip that a store prints for the box of one order, with examples that test each line
prerequisites: ["1"]
template: 2
nav: ["Values, types and let", "Whole numbers: Int", "Fixed-width integers", "Day-to-day: a packing slip", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 2 Numbers


A store's software is mostly small computations on plain values: a price in cents, a discount, a SKU typed with a stray space, a product name too long for its label, a count that a printer reads as one byte. Each of these goes wrong in familiar ways: an integer that silently overflows, a rounding nobody chose, a number used as a yes or no, a cut that runs past the end of a text. This chapter shows the values Una has, `Int`, `Bool`, `Text` and the fixed-width integers, how names hold them, and how the checker catches each of these mistakes before the program runs.

## What you'll build

:::build
A packing slip: the sheet that goes into the box with an order, so that the customer can check what arrived. The program prints the slip of one sample order:

```text include="day-to-day/expected/output.txt"
Packing slip for order 1042
Ship to customer 318 <customer318@example.invalid>
  2 x LAMP-01  Desk lamp, brass
  1 x RUG-07  Wool rug, 120 by 180 cm
3 units in 2 lines
Total paid: 8480 cents
Questions? Write to orders@example.invalid and quote the order number.
```

You will learn to:

- set up a package from an empty directory: `una.toml`, `verification.lock` and a module;
- run `una check`, `una run` and `una test`, and read what they report;
- print on the console, and say in a function's header that it prints;
- name values, compute with them, and put them into text;
- write functions with doc comments, and test them with examples.
:::

## Why it works this way

In many languages the basic values are where the quiet mistakes live. A whole number has a largest value, and a total that grows past it jumps to a wrong number, often a negative one, with no error. A division of a negative amount can leave a negative remainder. A number, or an empty text, can stand for "no" in a condition. Cutting a piece out of a text at a position past its end stops the program while it runs, or gives back less than the code expected. Each section of this chapter shows one of these in Una.

Una makes each of these a rule that the checker enforces:

:::steps
1. **`Int` has no bound.** It is a whole number of any size, so a sum or a product is always exact. Where a width matters, you choose a fixed-width type, and the verifier, the part of `una check` that proves facts about the code ([section 2.1](#division-by-zero-a-proof-obligation)), proves that every operation stays in its range.
2. **Division is defined everywhere it can run.** The remainder of a division is never negative, and a division by a value that may be zero does not check.
3. **`Bool` is its own type.** A condition must be a `Bool`. An `Int` or a `Text` is never read as true or false.
4. **Operations state what they need.** Cutting a text requires positions inside it, and the verifier proves it at each call, from the code around the call.
:::

> [!KEY]
> A value in Una means exactly what its type says. No value turns into another type unless the code says so, and no operation can leave the range of its type at run time.

## 2.1 Values, types and names: `let`


### What a value is

A **value** is one piece of data: the number `18`, the text `"LAMP-01"`, the answer `true`. A program computes new values from old ones, as `18 - 9` gives `9`, and prints some of them.

Every value has a **type**, which says what kind of value it is, and so what you can do with it. You can multiply two numbers, but not two product names. Think of the fields of a paper form: one box takes a date, another a phone number, and a clerk refuses a form with a name in the date box. Types are those boxes, and `una check` is the clerk. The types of this chapter:

| Type | Its values | Written as |
| --- | --- | --- |
| `Int` | whole numbers, positive, zero or negative | `18`, `1_990`, `-500` |
| `Text` | a sequence of characters | `"Desk lamp, brass"` |
| `Bool` | the answer to a yes-or-no question | `true`, `false` |
| `Unit` | one value only, which carries no information | `unit` |

A value written out in the code, such as `18` or `"LAMP-01"`, is a **literal**. [Chapter 2](/learn/numbers/) covers each type in full.

### Why every value has a type

`print` takes a text. Give it a number:

```diff include="steps/01-hello..steps/02-print-number:src/hello.una" title="src/hello.una"
--- a/src/hello.una
+++ b/src/hello.una
@@ -1,7 +1,7 @@
 module hello
 
---- Says that the store is open.
+--- Says until when the store is open.
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print("The store is open")
+  @console.print(18)
```

```text include="steps/02-print-number/expected/rendered.txt#L1"
[U2001] Error: argument `line` of operation `Console.print` must be `Text`, found `Int`
```

`print`'s argument is called `line`, and its type is `Text`; the value given is an `Int`. Some languages would turn the number into a text without a word, and some would refuse only when the line runs. Una refuses before the program runs, and it never turns a value of one type into another unless the code says so. Saying so is easy, as [Putting values into a text](#putting-values-into-a-text) shows.

### How to write values and names

#### Literals

- An `Int` literal is written in decimal digits. An `_` may group them, so `1_990` is 1990 and easier to read. For a negative number, write a minus sign in front: `-500`.
- A `Text` literal is written between double quotes, on one line: `"Desk lamp, brass"`. A few characters need a backslash before them: `\"` for a quote, `\\` for a backslash, and `\{` and `\}` for braces, since a brace starts an interpolation, as [Putting values into a text](#putting-values-into-a-text) shows.
- A `Bool` literal is `true` or `false`.

#### Naming a value: `let`

`let` gives a name to a value, so that later steps can use it:

- `let lamps = 2` names the value `2` as `lamps`. The type, `Int`, comes from the value.
- `let lamp_cents: Int = 1_990` writes the type too, after `:`. It is optional, and it tells a reader what the name holds.

The name holds that one value from its line to the end of the body. A name of a value starts with a small letter and holds small letters, digits and `_`: `lamps`, `lamp_cents`, `sku2`.

#### Computing with `Int`

`+`, `-` and `*` add, subtract and multiply. `/` divides and drops the remainder, and `mod` gives the remainder (for numbers that are not negative; [chapter 2](#euclidean-division) shows the rest): `3980 / 100` is 39, and `3980 mod 100` is 80. `*`, `/` and `mod` come before `+` and `-`, as in school arithmetic, and parentheses change the order.

#### Putting values into a text

A name or a computation in braces, inside a text, puts its value into the text: `"{lamps} x {sku}"`. This is an **interpolation**. Numbers, texts and `true` and `false` can all go in braces, and so can a computation, such as `{lamps * lamp_cents}`. An `Int` goes in as plain decimal digits, with no leading zero and no `_`.

### Values in a store

This program names four values, one of each kind it prints, and computes with them:

:::steps
```una include="steps/03-values/src/values.una" title="steps/03-values/src/values.una" verified="check, run"
module values

--- Prints values of three types, and a few computations on them.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = 2
  let lamp_cents: Int = 1_990
  let sku = "LAMP-01"
  let in_stock = true
  @console.print("{lamps} x {sku}")
  @console.print("in stock: {in_stock}")
  @console.print("{lamps * lamp_cents} cents")
  @console.print("{lamps * lamp_cents / 100} units and {lamps * lamp_cents mod 100} cents")
  @console.print("a brace \{ and a quote \" in a text")
  let opens = 9
  let closes = 18
  @console.print("{closes - opens - 1} hours of trading, without the lunch hour")
  @console.print("{2 + 3 * 4} and {(2 + 3) * 4}")
```

1. **`let lamps = 2`.** A name for an `Int`.
2. **`let lamp_cents: Int = 1_990`.** A name with its type written out. Money is kept in **cents**, whole numbers, so that nothing ever rounds by accident.
3. **`let sku = "LAMP-01"`.** A `Text`. A **SKU**, a stock keeping unit, is the code a store gives each product.
4. **`let in_stock = true`.** A `Bool`.
5. **`"{lamps * lamp_cents / 100} units and {lamps * lamp_cents mod 100} cents"`.** Two computations inside one text.
6. **`"a brace \{ and a quote \" in a text"`.** Two escapes.
:::

`una run .` prints, among other lines:

```text include="steps/03-values/expected/output.txt#L1-L5"
2 x LAMP-01
in stock: true
3980 cents
39 units and 80 cents
a brace { and a quote " in a text
```

### Opening hours

Each program from here on is a package of its own, in a directory next to `store`. To make one, go up from `store` to your home directory with `cd ..` (`..` is the path of the directory above), then make the new directory as before:

```sh
cd ..
mkdir opening
cd opening
mkdir src
```

Then write `una.toml` and `src/opening.una` with your editor, and make `verification.lock` as in [the first package](/learn/hello/#making-the-package). This program prints the store's opening hours:

:::steps
```una include="steps/04-printing/src/opening.una" title="src/opening.una" verified="check, run"
module opening

--- Prints today's opening hours.
pub main() -> Unit
  uses @console: Console[print]
=
  let opens = 9
  let closes = 18
  let hours = closes - opens
  @console.print("Open today from {opens}:00 to {closes}:00")
  @console.print("That is {hours} hours of trading")
  @console.print("Orders placed before {closes}:00 ship today")
```

1. **`let hours = closes - opens`.** A name for a computed value: 9.
2. **`"Open today from {opens}:00 to {closes}:00"`.** A text with interpolations. The `:00` after each brace is plain text.
3. **Three `print` calls.** Each prints one line, in order.
:::

Its manifest names the package and its module `opening`, and grants the console, as the first package's did:

```toml include="steps/04-printing/una.toml" title="una.toml"
[package]
name = "opening"
version = "0.1.0"
edition = "0.2"

[run]
entry = "opening"
grants = ["console"]
```

`una run .` prints:

```text include="steps/04-printing/expected/output.txt"
Open today from 9:00 to 18:00
That is 9 hours of trading
Orders placed before 18:00 ship today
```

### How values and names behave

- **No conversions behind your back.** A value keeps its type. An `Int` becomes a text only where the code puts it in braces.
- **One name, one value.** A name made with `let` cannot be given another value, and the same name cannot be made twice in one body. [Chapter 2](#s2-1) shows `let edit`, for a value that must change, such as a running total.
- **A name exists from its line on.** A step can use a name only after the `let` that makes it.
- **Whole numbers have no size limit.** An `Int` never overflows, however large a total grows ([chapter 2](#s2-2)).
- **A text literal cannot go inside braces.** Write `let wood = "oak"`, then `"{wood}"`. [Chapter 3](/learn/text-and-conditions/#a-text-inside-an-interpolation-u0006) shows the diagnostic.
- **Few characters are special.** Besides the quote, the backslash and the braces, every character in a text, `:`, `<`, `x` or a space, prints as it is.

### Check yourself: values

The last four lines of `values` name two hours, then compute with the names and with parentheses:

```una include="steps/03-values/src/values.una#L16-L19" title="steps/03-values/src/values.una"
  let opens = 9
  let closes = 18
  @console.print("{closes - opens - 1} hours of trading, without the lunch hour")
  @console.print("{2 + 3 * 4} and {(2 + 3) * 4}")
```

What do the last two lines print?

:::answer Show the answer
```text include="steps/03-values/expected/output.txt#L6-L7"
8 hours of trading, without the lunch hour
14 and 20
```

`closes - opens - 1` is computed from the left: 18 − 9 is 9, and 9 − 1 is 8. In `2 + 3 * 4` the multiplication comes first, 12, then 2 + 12 is 14. The parentheses of `(2 + 3) * 4` make the addition come first: 5 × 4 is 20.
:::

One more, without code. With `lamps` an `Int` and `sku` a `Text`, which of these steps check?

1. `@console.print(lamps)`
2. `@console.print("{lamps}")`
3. `let both = lamps * sku`
4. `@console.print("{lamps} x {sku}")`

:::answer Show the answer
Steps 2 and 4 check. Step 1 gives `print` an `Int` where it takes a `Text`: U2001, as in [Why every value has a type](#why-every-value-has-a-type). Step 3 multiplies a number by a text, which has no meaning, and the checker reports U2001 for it too. In steps 2 and 4 the braces put the values into a text, so `print` gets the `Text` it takes.
:::


### What a name is

A **name**, or **binding**, ties a word to a value, so that later lines can use the value by its word. Think of a sticky label on a box: the label says `total`, and the box holds 8480. You met `let` in [chapter 2](#naming-a-value-let). This section shows the two kinds of name and the rules they follow.

### Why names do not change by default

Most values in a function are computed once: a price, a SKU, the result of a call. If any line could give such a name a new value, a reader would have to read every line to know what the name holds at a given point. So a plain `let` name never changes. Try to assign one:

```diff include="steps/05-till..steps/06-assign-let:src/till.una" title="src/till.una" context="1"
--- a/src/till.una
+++ b/src/till.una
@@ -7,3 +7,3 @@
   let lamp = 1_990
-  let edit total = 0
+  let total = 0
   let edit items = 0
```

```text include="steps/06-assign-let/expected/rendered.txt#L1"
[U2019] Error: `total` is not editable; declare it `let edit total`, or the parameter `edit total`
```

The message names the problem and both repairs. When a value really must change, as a running total does, you say so where the name is made.

### How to write names

| Write | Meaning |
| --- | --- |
| `let lamp = 1_990` | a plain name; its type comes from its value |
| `let lamp: Int = 1_990` | the same, with its type written after `:` |
| `let edit total = 0` | an **editable** name, which later lines may give new values |
| `let edit receipt: Text = "LAMP-01"` | the same, with its type |
| `total = total + lamp` | an **assignment**: the editable name `total` gets the value on the right |

An assignment is a **statement**: a line that does something instead of giving a value. It stands on its own line, and the right side is computed first, from the name's old value.

## 2.2 Whole numbers: `Int`


### What an integer is

An **integer** is a whole number: positive, zero or negative, with no fraction. `7`, `0` and `-1205` are integers; `19.90` is not. Una's integer type is `Int`, and it has no limit on its size: an `Int` can be as large as the computer's memory allows.

Most numbers in a store are counts of whole things: units on a shelf, lines of an order, labels to print. Money is one too, once you count it in its smallest unit. A price of 19.90 is 1990 **cents**, and an `Int` holds 1990 exactly.

### Why money is whole cents

A price written with a decimal point looks natural, so try it:

```una include="steps/07-fraction/src/shelf.una" title="steps/07-fraction/src/shelf.una"
module shelf

--- Prints the price of a desk lamp, written with a decimal point.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = 19.90
  @console.print("{lamp}")
```

```text include="steps/07-fraction/expected/rendered.txt"
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

The message says that `19.90` is a **fractional literal**, a number with a fraction, and that Una's integer literals are written in decimal digits only. Una has no number type for fractions.

That is a choice, not a gap. Many languages store a fraction such as 0.1 as a binary approximation, so adding prices gives totals such as 0.30000000000000004, and rounding them is a decision the code makes in a hundred places without saying so. With whole cents, every sum and product is exact, and the one place a fraction appears, a division, says how it rounds. Money is an `Int` of cents in this chapter and in every chapter of this book.

### How to write integers and arithmetic

#### Integer literals

- Write an integer in decimal digits: `7`, `1990`.
- Group the digits with `_` to make large numbers readable: `1_990`, `10_000`, `1_000_000`. The `_` goes only between digits.
- For a negative number, write a minus sign in front of the literal: `-1205`.
- A literal has no leading zero, except `0` itself: `007` is a mistake.

#### The operators

| Operator | Meaning | `7` and `2` give |
| --- | --- | --- |
| `+` | addition | `7 + 2` is 9 |
| `-` | subtraction, or a minus sign in front of one value | `7 - 2` is 5, `-7` is minus seven |
| `*` | multiplication | `7 * 2` is 14 |
| `/` | division, dropping the remainder | `7 / 2` is 3 |
| `mod` | the remainder of the division | `7 mod 2` is 1 |

`*`, `/` and `mod` come before `+` and `-`, and operators of the same level go from left to right. Parentheses change the order. The step tries each operator on 7 units packed 2 to a box:

```una include="steps/08-operators/src/arithmetic.una#L7-L13" title="steps/08-operators/src/arithmetic.una"
  let units = 7
  let per_box = 2
  @console.print("{units + per_box}, {units - per_box} and {units * per_box}")
  @console.print("{units / per_box} full boxes, {units mod per_box} unit left over")
  @console.print("{-units} and {per_box - units}")
  @console.print("{2 + 3 * 4} and {(2 + 3) * 4}")
  @console.print("{1_000_000 * 1_000_000}")
```

```text include="steps/08-operators/expected/output.txt#L1-L5"
9, 5 and 14
3 full boxes, 1 unit left over
-7 and -5
14 and 20
1000000000000
```

`7 / 2` gives 3 full boxes and drops the half, and `7 mod 2` gives the 1 unit left over. `1_000_000 * 1_000_000` is exact, with all its zeros.

### Money as `Int` cents

A price never needs a fraction, so it never needs rounding until the code chooses one:

:::steps
```una include="steps/09-prices/src/prices.una" title="src/prices.una" verified="check, run"
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
2. **`order / 100` and `order mod 100`.** Division of two `Int` values gives a whole number and drops the remainder; `mod` gives the remainder. Together they split cents into units and cents.
3. **`order * 15 / 100`.** A percentage. Multiply first, then divide, so that nothing is lost before the division.
4. **`refund / 100` and `refund mod 100`.** Division of a negative amount.
5. **`9_223_372_036_854_775_807 + 1`.** The largest value of a 64-bit integer, plus one.
:::

`una run .` prints:

```text include="steps/09-prices/expected/output.txt"
order: 8480 cents, or 84 units and 80 cents
15% off: 1272 cents off, 7208 to pay
refund: -13 and 95
no overflow: 9223372036854775808
```

The discount is 15 percent of 8480 cents, 1272: the exact value is 1272.0, so nothing is dropped here. Where a percentage does not come out whole, `/` rounds down, and [the sale prices of section 2.6](/learn/text-and-conditions/#sale-prices-and-prices-per-kilogram) show the store choosing that on purpose.

### How `Int` behaves

#### No 64-bit limit

The last line shows that `Int` has no 64-bit limit: the sum is exact. Many languages store integers in 64 **bits**, binary digits, and a sum past the largest 64-bit value wraps around to a large negative number, or stops the program. In Una it is just a larger number.

#### Euclidean division

The refund line shows how Una divides a negative number. Division and `mod` are **Euclidean**: the remainder is never negative, and the quotient is chosen to make that true. So `-1205 / 100` is `-13` and `-1205 mod 100` is `95`, since `-13 * 100 + 95` is `-1205`. Languages that round toward zero give `-12` and `-5` instead. For amounts that are not negative, both rules agree, and that is why the money functions of this chapter state that they take an amount that is not negative.

#### Division by zero, a proof obligation

Dividing by zero has no answer, so Una does not let a program reach such a division. Here is a function whose divisor comes from a **parameter**, an input of the function ([chapter 1](/learn/hello/#s1-3)):

```una include="steps/10-division/src/split.una" title="steps/10-division/src/split.una"
module split

--- What each of `people` pays when they share a bill of `total` cents, rounded down.
pub share(total: Int, people: Int) -> Int = total / people

--- Prints one share of a bill.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{share(9000, people: 4)} cents each")
```

```text include="steps/10-division/expected/rendered.txt"
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

Read it as [chapter 18](/learn/tools/#s18-2) shows: the message, the place, then the notes. The checker turned the division into a **proof obligation**, a fact that must be proved before the program may run: here, `people != 0`, "people is not zero". The part of `una check` that proves such facts is the **verifier**. It asks the solver Z3, which `verification.lock` pins, whether the fact holds for every value the parameters can take. It does not: the line `Note 2: counterexample: people = 0` gives the value that breaks it. (`Note 1` repeats the obligation with its identifier, `ob-…`, which tools use to name it.) A **counterexample** is that value. The obligation is **refuted**, and the code is U5001.

A literal divisor, such as `100`, proves itself. For a divisor that comes from a parameter, the function must say why it cannot be zero: the `Help` line proposes a **guard**, an `if` that tests the divisor before the division runs, and [section 3.5](/learn/text-and-conditions/#s3-5) shows the other way, a precondition that every caller must meet.

> [!NOTE]
> `Int` arithmetic costs a little more than the computer's own arithmetic on numbers of a fixed size, since an `Int` may grow past that size. Where a number must have a fixed size, such as a number another program reads as one byte, use the fixed-width types of [section 2.3](#s2-3).

### `Int` or something else

:::decide
**Which to use:**

| The number is… | Use |
| --- | --- |
| A count, a quantity or an amount of money | `Int`, with money in cents |
| A field that a protocol, a file or a device reads with a fixed width | a fixed-width type ([section 2.3](#s2-3)) |
| A code made of digits, such as a postal code with a leading zero | `Text`: you never compute with it, and `01310` is not an integer literal |
| A price with a fraction | `Int` cents, and a function that writes them with two decimals, as `money` does in [section 3.5](/learn/text-and-conditions/#s3-5) |
:::

### Check yourself: integers

The step `arithmetic` ends with two more lines:

```una include="steps/08-operators/src/arithmetic.una#L14-L15" title="steps/08-operators/src/arithmetic.una"
  @console.print("{1990 * 3 / 100}")
  @console.print("{-7 / 2} and {-7 mod 2}")
```

What do they print? The first is three units at 19.90, in whole units of money.

:::answer Show the answer
```text include="steps/08-operators/expected/output.txt#L6-L7"
59
-4 and 1
```

`1990 * 3` is 5970, and `/ 100` drops the remainder: 59. For `-7 / 2`, Euclidean division keeps the remainder at 0 or above: −4 × 2 is −8, and −7 − (−8) is 1. So the quotient is −4 and the remainder 1.
:::

## 2.3 Fixed-width integers


### What a fixed-width integer is

An `Int` grows as large as it needs. A **fixed-width integer** has a set number of bits, and so a smallest and a largest value. Think of the counter on a parking ticket machine with three digits: it shows 0 to 999, and nothing past that. A computer stores such a number in 8, 16, 32 or 64 bits, and other programs, file formats and devices often expect exactly that: a byte, 8 bits, holds 0 to 255.

Una has the **unsigned** types `U8`, `U16`, `U32` and `U64`, which hold 0 and up, and the **signed** types `I8`, `I16`, `I32` and `I64`, which hold negative values too:

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
> The fixed-width types belong to edition `0.2` and later. In a package of edition `0.1`, `U8` and the others are ordinary names.

### Why every operation is proved

In many languages a fixed-width number that passes its largest value **wraps around**: 255 + 1 in a byte gives 0, without an error. A count of 256 labels kept in a byte becomes 0, the label printer prints nothing, and nobody knows why. In Una a fixed-width value never wraps around unless the code asks for it by name. Every `+`, `-`, `*`, `/` and `mod` on one is a proof obligation: the verifier must prove that the exact result fits the type.

A function that adds 1 to a byte, with nothing to say the byte is below 255, does not check:

```una include="steps/12-overflow/src/printer.una#copies" title="steps/12-overflow/src/printer.una"
--- How many copies of a label to print: one per facing on the shelf, and one spare.
--- The label printer reads the count as one byte, so it is a `U8`.
pub copies(facings: U8) -> U8 = facings + 1
```

```text include="steps/12-overflow/expected/rendered.txt#L1,L8,L10,L12,L16"
[U5001] Error: overflow obligation `facings + 1 in 0..255` is refuted
   │ Help 1: repair 1: guard the operation with `if facings.to_int() + 1 in 0..255`
   │ Help 2: repair 2: give the values a wider type, converting them explicitly
   │ Help 3: repair 3: if wrapping or saturating is meant, use `wrapping_add`, `saturating_add` or their siblings
   │ Note 2: counterexample: facings = 255
```

The obligation `facings + 1 in 0..255` says that the sum must lie between 0 and 255, and the counterexample is the one value that breaks it, 255. The repairs list the three honest choices: check the range first, use a wider type, or say that wrapping or saturating is what you mean. Each makes the behavior at the edge of the range visible in the code.

### How to write fixed-width values

#### A literal takes the type its place expects

`let copies: U8 = 200` makes 200 a `U8`, since the name says so. A literal also takes the type of the parameter it is passed to, or of the other side of an operator. A literal that does not fit its type is U2022, and [A literal out of range](/learn/text-and-conditions/#a-literal-out-of-range-u2022), in Common mistakes, shows it.

#### Converting between integer types

- `x.to_int()` turns any fixed-width value into an `Int`. Every value fits, so it never fails.
- `x.to_u8()`, `x.to_u16()`, `x.to_i32()` and the others turn a value into another integer type. A conversion that can lose a value, from `Int` or to a smaller range, is a proof obligation that the value fits; one where every value fits, such as `U8` to `U16`, is not.
- These methods always take their parentheses: `x.to_int` without them names the prelude's `to_int` of a text, and the checker then reports that its argument must be a `Text`.
- A `U8` and an `Int`, or a `U8` and a `U16`, do not mix in one operation: convert one of them first.

#### Wrapping and saturating, by name

- `a.wrapping_add(by: b)`, `wrapping_sub` and `wrapping_mul` wrap around, as other languages do silently.
- `a.saturating_add(by: b)`, `saturating_sub` and `saturating_mul` stop at the end of the range: at 0 or at the largest value.

These never leave the range, so they need no proof.

The step writes each form:

```una include="steps/13-fixed-forms/src/widths.una#L1-L14" title="steps/13-fixed-forms/src/widths.una"
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

```text include="steps/13-fixed-forms/expected/output.txt#L1-L4"
200, -128 and 18446744073709551615
300 as an Int
44 wrapped, 255 saturated
42 as a U8
```

`copies.to_int() + 100` is an `Int`, so 300 is fine. In a `U8`, 200 + 100 wraps to 44 or saturates at 255. `count.to_u8()` narrows the `Int` 42: the verifier knows `count` is 42, so it proves that it fits.

### Label copies as one byte: `U8`

The module `printer` counts the copies of a shelf label in a `U8`, and a roll of labels in a `U16`:

:::steps
```una include="steps/11-printer/src/printer.una" title="src/printer.una" verified="check, run"
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
2. **`requires facings < 255`.** A **precondition**: a fact every caller must make true, written on its own line under the header, before `=`. It makes `facings + 1` fit in a `U8`, so the verifier proves the addition, and it proves the precondition at each call. [Chapter 5](/learn/contracts/#s5-1) covers preconditions in full.
3. **`let lamps: U8 = 4`.** A literal takes the type its context expects, here `U8`. A literal that does not fit, such as `300`, does not check.
4. **`lamp_labels.to_int() + mug_labels.to_int()`.** Two `U8` values turned into `Int` before they are added. Every `U8` fits in an `Int`, so `to_int()` always succeeds; the sum is an `Int` and cannot overflow.
5. **`roll.saturating_sub(by: 1_200)`.** Subtraction that stops at the bottom of the range, 0, instead of going below it. Methods such as this one say in their names what happens at the ends of the range.
:::

`una run .` prints:

```text include="steps/11-printer/expected/output.txt"
5 and 13 labels
18 labels in all
0 left on a roll of 1000 after 1200
```

### How fixed-width integers behave

- **No silent wrap.** Every operation that could leave the range is an obligation, and a refuted one does not check.
- **Literals are checked at once.** A literal that does not fit its type is U2022, before any proof.
- **A constant computation is proved, not folded.** `250 + 10` where a `U8` is expected is not one literal: it gets an overflow obligation, which is refuted.
- **Types do not mix.** Operands of two integer types are U2001; convert one with `to_int()` or a narrowing method.
- **Contracts read the exact value.** In a `requires` clause, a `U8` reads as its mathematical value, so `facings < 255` compares integers and never overflows.
- **Lengths stay `Int`.** `t.len` and the length of a list are always `Int`.

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

Change the first line of `widths` so that the `U8` is computed:

```diff include="steps/13-fixed-forms..steps/14-constant-overflow:src/widths.una" title="src/widths.una" context="0"
--- a/src/widths.una
+++ b/src/widths.una
@@ -7 +7 @@
-  let copies: U8 = 200
+  let copies: U8 = 200 + 100
```

Does it still check? And in the original step, what does the last line print, with `roll` holding 500?

```una include="steps/13-fixed-forms/src/widths.una#L15-L16" title="steps/13-fixed-forms/src/widths.una"
  let roll: U16 = 500
  @console.print("{roll.saturating_sub(by: 600)} and {roll.wrapping_sub(by: 600)}")
```

:::answer Show the answer
It does not check:

```text include="steps/14-constant-overflow/expected/rendered.txt#L1"
[U5001] Error: overflow obligation `200 + 100 in 0..255` is refuted
```

`200 + 100` is 300, which a `U8` cannot hold, and the verifier proves that the sum leaves the range. The last line of the original prints:

```text include="steps/13-fixed-forms/expected/output.txt#L5"
0 and 65436
```

500 − 600 is −100. `saturating_sub` stops at 0. `wrapping_sub` wraps around the 65536 values of a `U16`: −100 + 65536 is 65436.
:::

## 2.4 Day-to-day: a packing slip

### What the program must do

A packing slip goes into every box the store ships. It names the order and the customer, lists each line of the order with its quantity, counts the units, and gives the total paid. The warehouse prints it as the box is packed.

The design follows from the job and from this chapter's ideas. Each line of the slip comes from its own function, which takes the values the line shows and returns its text. Those functions have no `uses` line, so they cannot print, and an example can test each one by its result. `main` holds the sample order's values, calls the functions, and prints what they return, line by line.

### The slip's package and manifest

The program is one module, `slip`, in a package of its own: make a directory `day-to-day` with its `src`, as in [Opening hours](#opening-hours), add `verification.lock`, and write this manifest, which grants the console:

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

Seven functions, each with a doc comment, each written in the short form, on one line:

```una include="day-to-day/src/slip.una#title..closing" title="day-to-day/src/slip.una" caption="one function per line of the slip"
--- The first line of a slip: the order the box holds.
pub title(order: Int) -> Text = "Packing slip for order {order}"

--- Where the box goes: the customer's number and email address.
pub ship_to(customer: Int, email: Text) -> Text = "Ship to customer {customer} <{email}>"

--- One line of the order: how many units of a SKU, and what the SKU is.
pub item(quantity: Int, sku: Text, name: Text) -> Text = "  {quantity} x {sku}  {name}"

--- What one line of the order costs, in cents.
pub line_cents(quantity: Int, cents: Int) -> Int = quantity * cents

--- How much the box holds.
pub count_line(units: Int, lines: Int) -> Text = "{units} units in {lines} lines"

--- What the customer paid for the goods, in cents.
pub total_line(cents: Int) -> Text = "Total paid: {cents} cents"

--- The last line, the same on every slip.
pub closing() -> Text = "Questions? Write to orders@example.invalid and quote the order number."
```

Each function uses one idea of this chapter:

- `title`, `count_line` and `total_line` put `Int` parameters into a text with interpolation, as in [section 2.1](#s2-1).
- `ship_to` and `item` take two and three parameters, separated by commas. The angle brackets in `ship_to` and the `x` in `item` are plain characters of the text: only braces are special.
- `item` starts with two spaces, inside the text, so that the item lines stand out on paper.
- `line_cents` returns an `Int`, not a text: it multiplies two `Int` values with `*`.
- `closing` takes no parameters and always returns the same text.

Money is in **cents**, as an `Int`: 1990 is 19 units and 90 cents. Whole cents never round, so the total is exact. [Chapter 2](/learn/numbers/) shows how to print them as an amount with two decimals.

### Printing the slip

`main` names the quantities and computes the cost of each line, then prints the slip one line at a time:

```una include="day-to-day/src/slip.una#main" title="day-to-day/src/slip.una"
--- Prints the slip of order 1042: two desk lamps and one rug.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = 2
  let rugs = 1
  let lamp_cents = line_cents(lamps, cents: 1990)
  let rug_cents = line_cents(rugs, cents: 4500)
  @console.print(title(1042))
  @console.print(ship_to(318, email: "customer318@example.invalid"))
  @console.print(item(lamps, sku: "LAMP-01", name: "Desk lamp, brass"))
  @console.print(item(rugs, sku: "RUG-07", name: "Wool rug, 120 by 180 cm"))
  @console.print(count_line(lamps + rugs, lines: 2))
  @console.print(total_line(lamp_cents + rug_cents))
  @console.print(closing())
```

Read it in two parts. The four `let` lines name the order's values: how many lamps and rugs, and what each line costs, from `line_cents`. The seven `print` lines then print the slip, each one calling the function of its line. `count_line(lamps + rugs, lines: 2)` computes its first argument, 3, before the call.

The calls with more than one argument name every argument after the first: `line_cents(lamps, cents: 1990)`, `item(lamps, sku: "LAMP-01", name: "Desk lamp, brass")`, as [section 1.3](/learn/hello/#s1-3) explains. [Chapter 6](/learn/functions/) gives the full rule.

Each `@console.print` call is a line of its own. In Una, a call that prints, or does anything else outside the program, always stands on a line of its own: as a step, as the whole value of a `let`, or as the last line of a body, never hidden inside another computation. A reader who scans the left edge of `main` sees every effect it has, in the order it has them.

### Why one function per line of the slip

Why so many small functions for a program this size? Each one is a line of the slip that someone may want to change: the wording of the closing line, the layout of an item, the email address. A change to one of them touches one line of code and one example, and the header of each tells you, without a look at its body, that it only computes a text or a number. The same program written as one `main` of seven prints, with every text in place, would be shorter, and nothing in it could be tested without reading what it prints.

### Running it

In the package's directory, `una run .` prints the slip shown in [What you'll build](#what-youll-build): the order and the customer, two item lines, three units in two lines, and a total of 8480 cents, which is 2 times 1990 plus 4500.

> [!SECURITY]
> The slip's functions have no `uses` line, so the checker proves they cannot print, read files or reach the network. Only `main` touches the console, and only because its header says so and the run grants it, here through `una.toml`. When this program grows, anything new a function does outside the program shows up in that function's header, where a reviewer sees it.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/slip.una" title="day-to-day/src/slip.una" caption="the whole program" verified="check, run, test"
module slip

-- A packing slip: the sheet that goes into the box with an order, so that the customer
-- can check what arrived. This version prints the slip of one sample order.

--- The first line of a slip: the order the box holds.
pub title(order: Int) -> Text = "Packing slip for order {order}"

--- Where the box goes: the customer's number and email address.
pub ship_to(customer: Int, email: Text) -> Text = "Ship to customer {customer} <{email}>"

--- One line of the order: how many units of a SKU, and what the SKU is.
pub item(quantity: Int, sku: Text, name: Text) -> Text = "  {quantity} x {sku}  {name}"

--- What one line of the order costs, in cents.
pub line_cents(quantity: Int, cents: Int) -> Int = quantity * cents

--- How much the box holds.
pub count_line(units: Int, lines: Int) -> Text = "{units} units in {lines} lines"

--- What the customer paid for the goods, in cents.
pub total_line(cents: Int) -> Text = "Total paid: {cents} cents"

--- The last line, the same on every slip.
pub closing() -> Text = "Questions? Write to orders@example.invalid and quote the order number."

--- Prints the slip of order 1042: two desk lamps and one rug.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = 2
  let rugs = 1
  let lamp_cents = line_cents(lamps, cents: 1990)
  let rug_cents = line_cents(rugs, cents: 4500)
  @console.print(title(1042))
  @console.print(ship_to(318, email: "customer318@example.invalid"))
  @console.print(item(lamps, sku: "LAMP-01", name: "Desk lamp, brass"))
  @console.print(item(rugs, sku: "RUG-07", name: "Wool rug, 120 by 180 cm"))
  @console.print(count_line(lamps + rugs, lines: 2))
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

example "the count line gives units and lines"
  do count_line(3, lines: 2)
  expect result == "3 units in 2 lines"

example "the total is in cents"
  do total_line(8480)
  expect result == "Total paid: 8480 cents"
```

## 2.5 Testing it

### One example per function

Every function of the slip returns a value, so every one gets an example. The examples call each function with the sample order's values and state the exact text or number it must return:

```una include="day-to-day/src/slip.una#L43-L69" title="day-to-day/src/slip.una" caption="the examples"
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

example "the count line gives units and lines"
  do count_line(3, lines: 2)
  expect result == "3 units in 2 lines"

example "the total is in cents"
  do total_line(8480)
  expect result == "Total paid: 8480 cents"
```

### Cases the sample order does not reach

Two of them check more than the sample shows. "a line of zero units costs nothing" covers a case the sample order never reaches. "an item line is indented and starts with the quantity" pins the two leading spaces, which are easy to lose in an edit and hard to see in the output. An example that states the whole expected text catches a change of one character.

### Running the slip's examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L10"
example slip "the title names the order" ... ok
example slip "the address line holds the customer number and the email" ... ok
example slip "an item line is indented and starts with the quantity" ... ok
example slip "a line costs its quantity times the unit price" ... ok
example slip "a line of zero units costs nothing" ... ok
example slip "the count line gives units and lines" ... ok
example slip "the total is in cents" ... ok

7 examples: 7 passed, 0 failed
```

Each example takes one line of the report, so when one fails, the report names the line of the slip that changed. Tools read the same results as JSON, a text format that programs read, with `una --json test .`, one entry for each example with its outcome.

### What the examples leave out: `main`

The examples do not test `main`, and they do not need to. `main` only names values and prints what the functions return, and the functions are what the examples cover. This is the shape most Una programs take: a thin `main` with the effects, and pure functions, with no `uses` line, that hold the logic and the tests. [Chapter 10, Testing](/learn/testing/), shows how to test functions that do have effects, with fakes that stand in for the console and other capabilities.

## 2.6 Common mistakes

Each mistake below is a small change to `day-to-day/src/slip.una`, followed by what `una check .` reports. Read each diagnostic as [section 18.2](/learn/tools/#s18-2) shows: the message, then the place, then the help.

### Printing a number (U2001)

:::mistake
Print the total itself, instead of the line that holds it:

```diff include="day-to-day..mistakes/1:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -39,3 +39,3 @@
   @console.print(count_line(lamps + rugs, lines: 2))
-  @console.print(total_line(lamp_cents + rug_cents))
+  @console.print(lamp_cents + rug_cents)
   @console.print(closing())
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U2001] Error: argument `line` of operation `Console.print` must be `Text`, found `Int`
```

*Why:* `print` takes a `Text`, and `lamp_cents + rug_cents` is an `Int`. Una converts no value to another type unless the code says so. The message names the parameter, `line`, the type it must have and the type it got.

*Fix:* put the number in a text, `"{lamp_cents + rug_cents}"`, or call `total_line`, which does. See [U2001](/docs/errors/U2001/).
:::

## 2.7 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added at the end, and a **stub** of each function to write: the function's header with a body that only returns a **placeholder**, a value of the right type that is not the answer, such as the empty text `""` or `0`. `una test .` fails there until the exercise is done. Work in this order:

1. Read the examples: they say what the function must return.
2. Write the function's body, in place of the placeholder.
3. Run `una fmt .`, then `una check .`, and fix what it reports. Canonical form, for example, puts a body of one line on the header line.
4. Run `una test .` until every example passes.

### Exercise 1: the weight of the parcel

::::exercise
The warehouse wants the weight on the slip, in kilograms and grams. Write `weight_line(grams)`, which turns 2350 into `Parcel weight: 2 kg 350 g`. The start package ends with:

```una include="exercises/1/start/src/slip.una#L71-L80" title="exercises/1/start/src/slip.una"
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
*Hint:* a kilogram is 1000 grams. `/` divides two `Int` values and drops the remainder, and `mod` gives the remainder: `2350 / 1000` is 2, and `2350 mod 1000` is 350. Both can go inside the braces of a text, as in [section 2.1](#s2-1).
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L9-L16"
example slip "a weight shows whole kilograms and the grams left over" ... FAILED
  src/slip.una:76: expect result == "Parcel weight: 2 kg 350 g"
  it is false, with `result` = `""`
example slip "a parcel under one kilogram shows 0 kg" ... FAILED
  src/slip.una:80: expect result == "Parcel weight: 0 kg 800 g"
  it is false, with `result` = `""`

9 examples: 7 passed, 2 failed
```

The placeholder returns the empty text, `""`, which is what each report shows as `result`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Give `weight_line` its body:

```diff include="exercises/1/start..exercises/1/answer:src/slip.una" context="1" title="src/slip.una"
--- a/src/slip.una
+++ b/src/slip.una
@@ -71,3 +71,3 @@
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

```una include="exercises/2/start/src/slip.una#L71-L83" title="exercises/2/start/src/slip.una"
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
@@ -39,3 +39,6 @@
   @console.print(count_line(lamps + rugs, lines: 2))
-  @console.print(total_line(lamp_cents + rug_cents))
+  let goods = lamp_cents + rug_cents
+  @console.print(total_line(goods))
+  @console.print("Shipping: 450 cents")
+  @console.print(pay_line(to_pay(goods, shipping: 450)))
   @console.print(closing())
@@ -71,6 +74,6 @@
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

```una include="exercises/3/start/src/slip.una#L71-L84" title="exercises/3/start/src/slip.una"
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
@@ -21,3 +21,3 @@
 --- What the customer paid for the goods, in cents.
-pub total_line(cents: Int) -> Text = "Total paid: {cents} cents"
+pub total_line(cents: Int) -> Text = "Total paid: {amount(cents)}"
 
@@ -66,8 +66,8 @@
 
-example "the total is in cents"
+example "the total is an amount"
   do total_line(8480)
-  expect result == "Total paid: 8480 cents"
+  expect result == "Total paid: 84.80"
 
 --- An amount of cents with two decimals: 8480 is "84.80", and 1205 is "12.05".
-pub amount(cents: Int) -> Text = ""
+pub amount(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"
 
```

`cents mod 100 / 10` is the tens of cents, and `cents mod 10` the cents left over, so each digit is printed on its own and a zero is never lost. This works for an amount that is not negative; [chapter 6](/learn/functions/) shows `if`, for the cases that need a choice.
:::
::::

## 2.8 Recap and reference

### For agents

:::agents
Every command takes `--json` before its name and then prints one JSON document on stdout. `una --json check .` gives each diagnostic with its `code`, `message`, `primary` span and `repairs`, and `una --json test .` gives each example with its outcome. U0003, U1008, U2004 and U7001 carry exact edits, which `una fix .` applies, as U1001 does when it can name the operation meant. U0001, U0101, U2001 and U3004 depend on intent, so their repairs, when they have one, are descriptions only. The compact rule: *a package is `una.toml`, `verification.lock` and `src/<module>.una` with a matching `module` line; a function that prints declares `uses @console: Console[print]`, and the run grants `console`, in `una.toml` or with `--grant`.*
:::

### Recap

:::recap
- A package is `una.toml`, `verification.lock` and modules under `src/`: `src/slip.una` holds the module `slip`.
- `una check .` reports each problem with a code, a place and a message; `una run .` and `una test .` check first. Read the message, then the place, then the help.
- A function that prints says so in its header, `uses @console: Console[print]`, and the run grants `console`. A public function without `uses` cannot print.
- Every value has a type. `let` names a value, and braces put values into a text: `"{units} units"`.
- Label every argument after the first: `line_cents(2, cents: 1990)`.
- Comments start with `--`, and doc comments with `---`, which `una contract` prints.
- Keep the logic in functions without `uses`, and test each one with an `example`: `do` a call, `expect` a fact about `result`.
:::

### Reference

:::reference
- Start: [install](/docs/install/), [getting started](/docs/getting-started/), [canonical form and `una fmt`](/docs/language/canonical-form/)
- Construct pages: [source files, comments and literals](/docs/language/lexical-structure/), [functions](/docs/language/functions/), [`uses`](/docs/language/capabilities/uses/), [host capabilities and grants](/docs/language/capabilities/host/), [`example`](/docs/language/examples/example/)
- Configuration: [`[package] edition`](/docs/configure/package/edition/), [`[run] entry`](/docs/configure/run/entry/), [`[run] grants`](/docs/configure/run/grants/), [`verification.lock`](/docs/configure/verification-lock/)
- Commands: [`una check`](/docs/cli/check/), [`una run`](/docs/cli/run/), [`una test`](/docs/cli/test/), [`una fmt`](/docs/cli/fmt/), [`una fix`](/docs/cli/fix/), [`una explain`](/docs/cli/explain/), [`una contract`](/docs/cli/contract/)
- Standard library: [the host capabilities](/docs/std/) (`Console`, `print`)
- Diagnostics: [U0001](/docs/errors/U0001/), [U0003](/docs/errors/U0003/), [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1008](/docs/errors/U1008/), [U2001](/docs/errors/U2001/), [U2004](/docs/errors/U2004/), [U3004](/docs/errors/U3004/), [U3012](/docs/errors/U3012/), [U7001](/docs/errors/U7001/), [U7002](/docs/errors/U7002/), [U7004](/docs/errors/U7004/)
- Specification: [lexical structure](/docs/spec/01-lexical-structure/), [types](/docs/spec/03-types/), [functions and contracts](/docs/spec/04-functions-and-contracts/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [requirements and examples](/docs/spec/08-requirements-and-examples/), [diagnostics and the command line](/docs/spec/13-diagnostics-and-abi/), [the standard library](/docs/spec/14-standard-library/), [canonical form](/docs/spec/15-canonical-form/)
:::
