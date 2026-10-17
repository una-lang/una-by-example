---
learn: "2"
title: Values
editions: ["0.2"]
codes: [U0006, U0101, U1002, U2001, U2019, U2022, U5001]
time: 55
builds: The shelf labels of a store, with prices, sale prices, prices per kilogram and the number of copies to print
prerequisites: ["1"]
template: 2
nav: ["Numbers: Int", "Conditions: Bool", "Text", "let and let edit", "Fixed-width integers", "Day-to-day: shelf labels", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 2 Values

A store's software is mostly small computations on plain values: a price in cents, a discount, a SKU typed with a stray space, a product name too long for its label, a count that a printer reads as one byte. Each of these goes wrong in familiar ways: an integer that silently overflows, a rounding nobody chose, a number used as a yes or no, a cut that runs past the end of a text. This chapter shows the values Una has, `Int`, `Bool`, `Text` and the fixed-width integers, how names hold them, and how the checker catches each of these mistakes before the program runs.

## What you'll build

:::build
The shelf labels of a store. The program cleans each SKU, cuts each name to the width of a label, prints the price, the sale price or the price per kilogram, and counts how many copies the label printer must print:

```text include="day-to-day/expected/output.txt"
LAMP-01 | Desk lamp, brass | 19.90
RUG-07 | Wool rug, 120 by 180 cm, | 45.00, now 38.25 (15% off)
COFFEE-05 | Coffee beans, dark roast | 12.50 (25.00 per kg)
DESK-02 | Oak writing desk | 159.00
23 labels to print
```

You will learn to:

- compute with `Int`, which never overflows, and keep money in whole cents;
- combine conditions with `Bool`, `and`, `or` and `not`;
- clean, search, cut and build `Text`, and let the verifier prove a cut is in range;
- name values with `let`, and change them with `let edit`;
- use a fixed-width integer where a protocol needs one, with its range proved.
:::

## Why it works this way

In many languages the basic values are where the quiet bugs live. A 32-bit or 64-bit integer wraps around when a total gets large, and the result is wrong without an error. Integer division rounds toward zero, so the remainder of a negative amount is negative. A number, an empty text or a null passes for `false` in a condition. A substring call with an index past the end throws at run time, or returns less than the code expected.

Una makes each of these a rule that the checker enforces:

:::steps
1. **`Int` has no bound.** It is a whole number of any size, so a sum or a product is always exact. Where a width matters, you choose a fixed-width type, and the verifier, the part of `una check` that proves facts about the code ([section 2.1](#division-by-zero-a-proof-obligation)), proves that every operation stays in its range.
2. **Division is defined everywhere it can run.** The remainder of a division is never negative, and a division by a value that may be zero does not check.
3. **`Bool` is its own type.** A condition must be a `Bool`. An `Int` or a `Text` is never read as true or false.
4. **Operations state what they need.** Cutting a text requires positions inside it, and the verifier proves it at each call, from the code around the call.
:::

> [!KEY]
> A value in Una means exactly what its type says. No value turns into another type unless the code says so, and no operation can leave the range of its type at run time.

## 2.1 Numbers: `Int`

### What an integer is

An **integer** is a whole number: positive, zero or negative, with no fraction. `7`, `0` and `-1205` are integers; `19.90` is not. Una's integer type is `Int`, and it has no limit on its size: an `Int` can be as large as the computer's memory allows.

Most numbers in a store are counts of whole things: units on a shelf, lines of an order, labels to print. Money is one too, once you count it in its smallest unit. A price of 19.90 is 1990 **cents**, and an `Int` holds 1990 exactly.

### Why money is whole cents

A price written with a decimal point looks natural, so try it:

```una include="steps/01-fraction/src/shelf.una" title="steps/01-fraction/src/shelf.una"
module shelf

--- Prints the price of a desk lamp, written with a decimal point.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = 19.90
  @console.print("{lamp}")
```

```text include="steps/01-fraction/expected/rendered.txt"
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
- Write a negative number with `-` in front: `-1205`.
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

```una include="steps/02-operators/src/arithmetic.una#L7-L13" title="steps/02-operators/src/arithmetic.una"
  let units = 7
  let per_box = 2
  @console.print("{units + per_box}, {units - per_box} and {units * per_box}")
  @console.print("{units / per_box} full boxes, {units mod per_box} unit left over")
  @console.print("{-units} and {per_box - units}")
  @console.print("{2 + 3 * 4} and {(2 + 3) * 4}")
  @console.print("{1_000_000 * 1_000_000}")
```

```text include="steps/02-operators/expected/output.txt#L1-L5"
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
```una include="steps/03-prices/src/prices.una" title="src/prices.una" verified="check, run"
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

```text include="steps/03-prices/expected/output.txt"
order: 8480 cents, or 84 units and 80 cents
15% off: 1272 cents off, 7208 to pay
refund: -13 and 95
no overflow: 9223372036854775808
```

The discount is 15 percent of 8480 cents, 1272: the exact value is 1272.0, so nothing is dropped here. Where a percentage does not come out whole, `/` rounds down, and [the sale prices of section 2.6](#sale-prices-and-prices-per-kilogram) show the store choosing that on purpose.

### How `Int` behaves

#### No 64-bit limit

The last line shows that `Int` has no 64-bit limit: the sum is exact. Many languages store integers in 64 **bits**, binary digits, and a sum past the largest 64-bit value wraps around to a large negative number, or stops the program. In Una it is just a larger number.

#### Euclidean division

The refund line shows how Una divides a negative number. Division and `mod` are **Euclidean**: the remainder is never negative, and the quotient is chosen to make that true. So `-1205 / 100` is `-13` and `-1205 mod 100` is `95`, since `-13 * 100 + 95` is `-1205`. Languages that round toward zero give `-12` and `-5` instead. For amounts that are not negative, both rules agree, and that is why the money functions of this chapter state that they take an amount that is not negative.

#### Division by zero, a proof obligation

Dividing by zero has no answer, so Una does not let a program reach such a division. Here is a function whose divisor comes from a **parameter**, an input of the function ([chapter 1](/learn/hello/#s1-5)):

```una include="steps/04-division/src/split.una" title="steps/04-division/src/split.una"
module split

--- What each of `people` pays when they share a bill of `total` cents, rounded down.
pub share(total: Int, people: Int) -> Int = total / people

--- Prints one share of a bill.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{share(9000, people: 4)} cents each")
```

```text include="steps/04-division/expected/rendered.txt"
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

Read it as [chapter 1](/learn/hello/#s1-2) shows: the message, the place, then the notes. The checker turned the division into a **proof obligation**, a fact that must be proved before the program may run: here, `people != 0`, "people is not zero". The part of `una check` that proves such facts is the **verifier**. It asks the solver Z3, which `verification.lock` pins, whether the fact holds for every value the parameters can take. It does not: the line `Note 2: counterexample: people = 0` gives the value that breaks it. A **counterexample** is that value. The obligation is **refuted**, and the code is U5001.

A literal divisor, such as `100`, proves itself. For a divisor that comes from a parameter, the function must say why it cannot be zero: the `Help` line proposes a guard with `if`, and [section 2.6](#s2-6) shows the other way, a precondition that every caller must meet.

> [!NOTE]
> `Int` arithmetic costs a little more than a machine's own, since a value may outgrow a machine word. Where a protocol, a file format or a hash needs a fixed width, use the fixed-width types of [section 2.5](#s2-5).

### `Int` or something else

:::decide
**Which to use:**

| The number is… | Use |
| --- | --- |
| A count, a quantity or an amount of money | `Int`, with money in cents |
| A field that a protocol, a file or a device reads with a fixed width | a fixed-width type ([section 2.5](#s2-5)) |
| A code made of digits, such as a postal code with a leading zero | `Text`: you never compute with it, and `01310` is not an integer literal |
| A price with a fraction | `Int` cents, and a function that writes them with two decimals, as `money` does in [section 2.6](#s2-6) |
:::

### Check yourself: integers

The step `arithmetic` ends with two more lines:

```una include="steps/02-operators/src/arithmetic.una#L14-L15" title="steps/02-operators/src/arithmetic.una"
  @console.print("{1990 * 3 / 100}")
  @console.print("{-7 / 2} and {-7 mod 2}")
```

What do they print? The first is three units at 19.90, in whole units of money.

:::answer Show the answer
```text include="steps/02-operators/expected/output.txt#L6-L7"
59
-4 and 1
```

`1990 * 3` is 5970, and `/ 100` drops the remainder: 59. For `-7 / 2`, Euclidean division keeps the remainder at 0 or above: −4 × 2 is −8, and −7 − (−8) is 1. So the quotient is −4 and the remainder 1.
:::

## 2.2 Conditions: `Bool`

### What a condition is

A **condition** is a question whose answer is yes or no: is the order over 100.00? Is the address in the country? Una's type for such answers is `Bool`, and it has exactly two values, `true` and `false`. A comparison, such as `cents >= 10_000`, gives a `Bool`.

Conditions are how a program decides. A `Bool` says whether an order ships for free, and an `if` ([chapter 3](/learn/functions/#s3-3)) picks one of two values depending on it: `if free then 0 else 495` is 0 when `free` is `true`, and 495 otherwise.

### Why `Bool` is its own type

In some languages a number can stand for a yes or no: 0 means no, and anything else means yes. So a slip, such as writing the amount where the rule belongs, still runs, and quietly answers the wrong question. In Una a condition must be a `Bool`. Join an amount to a condition by mistake:

```diff include="steps/07-rules..steps/05-not-a-condition:src/rules.una" title="src/rules.una" context="0"
--- a/src/rules.una
+++ b/src/rules.una
@@ -4 +4 @@
-pub ships_free(cents: Int, domestic: Bool) -> Bool = cents >= 10_000 and domestic
+pub ships_free(cents: Int, domestic: Bool) -> Bool = cents and domestic
```

```text include="steps/05-not-a-condition/expected/rendered.txt#L1"
[U2001] Error: an operand of `and` must be `Bool`, found `Int`
```

`and` joins two conditions, and `cents` is an `Int`. The rule meant `cents >= 10_000`, and the checker says so before the program runs.

### How to write conditions

#### Comparisons

| Operator | True when |
| --- | --- |
| `==` | the two values are equal |
| `!=` | they differ |
| `<`, `<=` | the left is smaller, or smaller or equal |
| `>`, `>=` | the left is larger, or larger or equal |

`==` and `!=` work on two values of any one type. `<` and the other orderings work on `Int`, on the fixed-width types of [section 2.5](#s2-5), and on `Text`, which is ordered character by character.

#### `and`, `or` and `not`

- `a and b` is `true` when both are.
- `a or b` is `true` when at least one is.
- `not a` turns `true` into `false` and back.

#### The order of operations

Arithmetic comes first, then comparisons, then `not`, then `and`, then `or`. So `not units > 5` means `not (units > 5)`, and `a or b and c` means `a or (b and c)`. Parentheses make any order explicit, and a reader thanks you for them in a mixed rule.

The step tries each form:

```una include="steps/06-conditions/src/stock.una#L1-L16" title="steps/06-conditions/src/stock.una"
module stock

--- Whether a shelf holds any units.
pub in_stock(units: Int) -> Bool = units > 0

--- Prints what comparisons and the operators on `Bool` give.
pub main() -> Unit
  uses @console: Console[print]
=
  let units = 3
  @console.print("{units == 3} {units != 3} {units < 3} {units <= 3} {units > 3} {units >= 3}")
  @console.print("{in_stock(units)} {in_stock(0)} {not in_stock(0)}")
  @console.print("{true and false} {true or false} {not true}")
  let lamp = "LAMP-01"
  let rug = "RUG-07"
  @console.print("{lamp == rug} {lamp != rug} {lamp < rug}")
```

```text include="steps/06-conditions/expected/output.txt#L1-L4"
true false false true false true
true false true
false true false
false true true
```

`in_stock` is a function that returns a `Bool`: `in_stock(0)` is `false`, and `not in_stock(0)` is `true`. `"LAMP-01" < "RUG-07"` is `true`, since `L` comes before `R`.

### Store rules that return a `Bool`

Store rules are full of conditions like these, so they make good functions:

:::steps
```una include="steps/07-rules/src/rules.una" title="src/rules.una" verified="check, run"
module rules

--- Whether an order ships for free: 10000 cents of goods or more, to a domestic address.
pub ships_free(cents: Int, domestic: Bool) -> Bool = cents >= 10_000 and domestic

--- Whether the carrier must get a signature: an order over 50000 cents, or a gift over 20000.
pub needs_signature(cents: Int, gift: Bool) -> Bool = cents > 50_000 or (gift and cents > 20_000)

--- Prints the shipping rules for three orders.
pub main() -> Unit
  uses @console: Console[print]
=
  let domestic = ships_free(12_000, domestic: true)
  let abroad = ships_free(12_000, domestic: false)
  @console.print("12000 cents: free at home {domestic}, free abroad {abroad}")
  let gift = needs_signature(30_000, gift: true)
  let plain = needs_signature(30_000, gift: false)
  @console.print("30000 cents: signature as a gift {gift}, otherwise {plain}")
  @console.print("a small order pays shipping: {not ships_free(2_500, domestic: true)}")
  let lamp = "LAMP-01"
  let rug = "RUG-07"
  @console.print("same SKU: {lamp == lamp}, different SKUs: {lamp != rug}")
```

1. **`cents >= 10_000 and domestic`.** Both parts must be `true`. `domestic` is already a `Bool`, so it needs no comparison: write `domestic`, not `domestic == true`.
2. **`cents > 50_000 or (gift and cents > 20_000)`.** `and` binds tighter than `or`, but the parentheses make the rule readable at a glance.
3. **`ships_free(12_000, domestic: false)`.** A call with two arguments names the second one, as in [chapter 1](/learn/hello/#several-parameters-and-labels-at-the-call).
4. **`not ships_free(2_500, domestic: true)`.** `not` turns `true` into `false` and back.
5. **`lamp == lamp` and `lamp != rug`.** Equality compares values, here two texts, character by character.
:::

`una run .` prints:

```text include="steps/07-rules/expected/output.txt"
12000 cents: free at home true, free abroad false
30000 cents: signature as a gift true, otherwise false
a small order pays shipping: true
same SKU: true, different SKUs: true
```

### The checker's rules for conditions

A `Bool` prints as `true` or `false`. Everything else about `Bool` is a rule of the checker:

- A condition must be a `Bool`. An `if` over an `Int`, such as `if percent then …`, does not check, and neither does `quantity and true`. A number is not true or false in Una, and neither is a text.
- `==` compares two values of the same type. Comparing an `Int` with a `Text` is a type error, never a quiet `false`.
- Comparisons do not chain, as the next example shows.

A range test written as a chain, as in school, does not check:

```diff include="steps/07-rules..steps/08-chained:src/rules.una" title="src/rules.una" context="0"
--- a/src/rules.una
+++ b/src/rules.una
@@ -7,0 +8,3 @@
+
+--- Whether a discount is one the store runs: from 1 to 90 percent off.
+pub fair_discount(percent: Int) -> Bool = 1 <= percent <= 90
```

```text include="steps/08-chained/expected/rendered.txt#L1"
[U0101] Error: comparisons cannot be chained; join them with `and`, as in `a < b and b < c`
```

The message gives the repair: `percent >= 1 and percent <= 90`, which says the same thing in a way no reader can misread.

### One function per rule

A rule that the store applies in more than one place deserves a function that returns a `Bool`, named after the question it answers: `ships_free`, `needs_signature`, `on_sale`. The call then reads as the rule, `if ships_free(cents, domestic: domestic)`, and the rule lives in one place, with its own examples. When the free-shipping threshold changes, one line changes, and one example tells you whether the new rule is the one you meant.

### Check yourself: conditions

The step `stock` ends with two conditions, where `units` is 3 and `gift` is `true`:

```una include="steps/06-conditions/src/stock.una#L17-L19" title="steps/06-conditions/src/stock.una"
  let gift = true
  @console.print("{not units > 5}")
  @console.print("{not gift or units > 5}")
```

What do they print?

:::answer Show the answer
```text include="steps/06-conditions/expected/output.txt#L5-L6"
true
false
```

`not` comes after comparisons, so `not units > 5` is `not (units > 5)`: 3 > 5 is `false`, and `not false` is `true`. In the second line, `not` applies to `gift` alone, before `or`: `not gift` is `false`, `units > 5` is `false`, and `false or false` is `false`.
:::

## 2.3 Text

### What a text is

A **text** is a sequence of characters: letters, digits, spaces, punctuation. A SKU, a product name and a line of a label are texts. Una's type is `Text`, and you write a text between double quotes on one line, as in [chapter 1](/learn/hello/#s1-4).

A text may hold the characters of any language, `é` and `ü` included, since it is **Unicode**: the standard that numbers every character of every writing system. Una stores a text in **UTF-8**, the usual encoding of Unicode, which uses one byte for an English letter and two to four for others. Positions and lengths count characters, never bytes.

### Why text needs care

Texts come from people and from other systems, and they are messy. A SKU typed at the till arrives as `"lamp-01 "`, with small letters and a stray space, and compares unequal to the `"LAMP-01"` of the catalog:

```text include="steps/09-text-forms/expected/output.txt#L1"
[lamp-01 ] and [LAMP-01] are equal: false
```

A product name may be longer than its label. A program must clean, compare and cut text, and a cut at a position past the end of a text has no answer. Una gives you the functions to clean and search, and the verifier proves that every cut lies inside its text.

### How to write a text

#### Quotes and escapes

A few characters need an **escape**, a backslash and a letter, inside the quotes:

| Write | For |
| --- | --- |
| `\"` | a double quote |
| `\\` | a backslash |
| `\{` and `\}` | a brace, since a brace starts an interpolation |
| `\n` | a new line |
| `\t` | a tab |
| `\u{e9}` | the character with that Unicode number in hexadecimal: `é` |

#### Joining texts: interpolation

Una joins texts with an **interpolation**, as in [chapter 1](/learn/hello/#putting-values-into-a-text): `"{sku}-{size}"` is the SKU, a dash and the size. Una has no `+` for text: `+` adds numbers, and [Common mistakes](#s2-8) shows what the checker says to it. A text literal cannot go inside the braces of another text, so name it with `let` first, as `size` is named here.

The step writes each form:

```una include="steps/09-text-forms/src/texts.una#L1-L16" title="steps/09-text-forms/src/texts.una"
module texts

--- Prints texts written with escapes and joined with interpolation.
pub main() -> Unit
  uses @console: Console[print]
=
  let raw = "lamp-01 "
  let sku = "LAMP-01"
  @console.print("[{raw}] and [{sku}] are equal: {raw == sku}")
  @console.print("a quote \", a backslash \\ and braces \{ \}")
  @console.print("before a tab:\tafter it")
  @console.print("Caf\u{e9} table")
  let size = "XL"
  @console.print("{sku}-{size}")
  let empty = ""
  @console.print("[{empty}] has {empty.len} characters, [{sku}] has {sku.len}")
```

```text include="steps/09-text-forms/expected/output.txt#L2-L6"
a quote ", a backslash \ and braces { }
before a tab:	after it
Café table
LAMP-01-XL
[] has 0 characters, [LAMP-01] has 7
```

`.len` gives the length of a text, its number of characters: `""`, the **empty text**, has 0.

### The prelude's text functions

The **prelude** is the set of types and functions every module has without an import. It gives text most of what a program needs. You call its functions with **method syntax**: `raw.trim` is the call `trim(raw)`, and `sku.starts_with(prefix: prefix)` is `starts_with(sku, prefix: prefix)`. The value before the dot becomes the first argument. A call that takes nothing but that value may leave out the parentheses, as `raw.trim` and `sku.len` do.

:::steps
```una include="steps/10-catalog/src/catalog.una" title="src/catalog.una" verified="check, run"
module catalog

--- The SKU as labels print it: without the white space around it, in capital letters.
pub clean_sku(raw: Text) -> Text = raw.trim.to_upper

--- Prints what the prelude's text functions do to a SKU and a product name.
pub main() -> Unit
  uses @console: Console[print]
=
  let raw = "  lamp-01 "
  let sku = clean_sku(raw)
  @console.print("[{raw}] becomes [{sku}], {sku.len} characters")
  let prefix = "LAMP-"
  @console.print("a lamp: {sku.starts_with(prefix: prefix)}")
  let name = "Café table, oak"
  let wood = "oak"
  let walnut = "walnut"
  @console.print("{name.len} characters, oak: {name.contains_text(part: wood)}")
  @console.print(name.replace(pattern: wood, by: walnut))
  @console.print("a quote \" and a brace \{ in a text")
```

1. **`raw.trim.to_upper`.** Two calls in a row: `trim` removes the white space at both ends, and `to_upper` writes the letters in capitals. Each returns a new text; `raw` itself does not change.
2. **`sku.len`.** The number of characters, counted as Unicode scalar values. `"Café table, oak"` has 15: the `é` here is one, not the two bytes UTF-8 needs for it.
3. **`let prefix = "LAMP-"`, then `starts_with(prefix: prefix)`.** A text literal cannot appear inside the braces of another text, so the prefix gets a name first.
4. **`contains_text(part: wood)` and `replace(pattern: wood, by: walnut)`.** A search, and a replacement of every occurrence.
5. **`"a quote \" and a brace \{ in a text"`.** Two escapes.
:::

`una run .` prints:

```text include="steps/10-catalog/expected/output.txt"
[  lamp-01 ] becomes [LAMP-01], 7 characters
a lamp: true
15 characters, oak: true
Café table, walnut
a quote " and a brace { in a text
```

### The text functions at a glance

The table lists the prelude's main functions on a text `t`:

| Function | Gives | Notes |
| --- | --- | --- |
| `t.len` | `Int` | the number of characters, as Unicode scalar values |
| `t.trim`, `t.trim_start`, `t.trim_end` | `Text` | without the white space (spaces, tabs, new lines) at both ends, or one end |
| `t.to_upper`, `t.to_lower` | `Text` | changes the letters `a` to `z` and `A` to `Z` only |
| `t.starts_with(prefix: p)`, `t.ends_with(suffix: s)` | `Bool` | |
| `t.contains_text(part: p)` | `Bool` | |
| `t.replace(pattern: p, by: r)` | `Text` | every occurrence; `p` must not be empty |
| `t.slice(start: a, end: b)` | `Text` | the characters from position `a` up to, not including, `b` |
| `t.split(on: s)` | a list of `Text` | `s` must not be empty; a **list** is a sequence of values, the subject of [chapter 5](/learn/collections/) |

`to_upper` changes only the 26 letters of the English alphabet, so `é` stays `é`: the result is the same on every machine, whatever its language settings.

> [!NOTE]
> `len`, `trim`, `starts_with` and `==` work in every edition. `trim_start`, `trim_end`, `to_upper`, `to_lower`, `ends_with`, `contains_text`, `replace`, `slice` and `split` are the text functions of edition `0.2` and later; in a package of edition `0.1` their names are ordinary names.

### Cutting a text, and the proof it takes

A label has room for 24 characters, so a longer name must be cut. Positions in a text count characters from 0, so the first 24 characters are those at positions 0 to 23. `slice` cuts, and it **requires** its positions to lie inside the text: `0 <= start`, `start <= end` and `end <= t.len`. A requirement of this kind is a **precondition**, and the verifier proves it at every call, before the program runs.

:::steps
```una include="steps/11-names/src/names.una" title="src/names.una" verified="check, run"
module names

--- A product name cut to the 24 characters a label has room for.
pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name

--- Prints two names as a label shows them.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = "Desk lamp, brass"
  let rug = "Wool rug, 120 by 180 cm, natural undyed"
  @console.print("[{fit_name(lamp)}]")
  @console.print("[{fit_name(rug)}]")
```

1. **`if name.len > 24 then … else name`.** An `if` chooses between two values: the value after `then` when the condition holds, and the value after `else` when it does not. Here, the cut name when it is too long, and the name itself when it fits. [Chapter 3](/learn/functions/#s3-3) covers `if`.
2. **`name.slice(start: 0, end: 24)`.** The first 24 characters. It needs `24 <= name.len`. In the `then` branch, the verifier knows that `name.len > 24`, so it proves it.
:::

```text include="steps/11-names/expected/output.txt"
[Desk lamp, brass]
[Wool rug, 120 by 180 cm,]
```

### When the proof fails: a counterexample

Without the `if`, nothing says the name is long enough:

```diff include="steps/11-names..steps/12-unguarded:src/names.una" title="src/names.una" context="0"
--- a/src/names.una
+++ b/src/names.una
@@ -4 +4 @@
-pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name
+pub fit_name(name: Text) -> Text = name.slice(start: 0, end: 24)
```

```text include="steps/12-unguarded/expected/rendered.txt#L1,L10,L16"
[U5001] Error: precondition `0 <= 0 and 0 <= 24 and 24 <= name.len` of this call is refuted
   │ Help 2: repair 2: add a guard (`if` or a `when` arm) that handles the values where `0 <= 0 and 0 <= 24 and 24 <= name.len` does not hold
   │ Note 2: counterexample: name = Text#0, name.len = 0
```

Read it in order. The first line names the obligation: the precondition of `slice`, with the call's arguments in place of `start` and `end`. The `Help` line proposes a guard, which is what the `if` was. The **counterexample** is the case that breaks the requirement: an empty name, whose length is 0. A text in a counterexample is shown by a placeholder, `Text#0`, followed by the facts about it that matter. Where another language would fail at run time on a short name, or cut it silently, Una refuses the program and names the input that would break it.

### How text behaves

- **A text never changes.** `trim`, `to_upper` and `replace` return a new text; the one you passed stays as it was.
- **Lengths and positions count characters.** `"Café"` has 4, whatever bytes UTF-8 uses. Positions run from 0 to `len - 1`.
- **Equality is exact.** `==` compares character by character: `"lamp-01 "` and `"LAMP-01"` differ in case and in the space.
- **Case changes are ASCII only.** `to_upper` and `to_lower` change `a` to `z` and `A` to `Z`, nothing else, so a text keeps its length.
- **The empty text is a text.** `""` has length 0, and `trim` of a text of spaces gives it.
- **Cuts are proved.** `slice` and `replace` state what they need, and a call the verifier cannot prove does not check.

### Check yourself: text

The step `texts` ends with two more lines:

```una include="steps/09-text-forms/src/texts.una#L17-L20" title="steps/09-text-forms/src/texts.una"
  let padded = "  oak desk "
  @console.print("{padded.trim.len}")
  let cafe = "Café"
  @console.print(cafe.to_upper)
```

What do they print?

:::answer Show the answer
```text include="steps/09-text-forms/expected/output.txt#L7-L8"
8
CAFé
```

`trim` removes the two spaces at the front and the one at the end, leaving `oak desk`, 8 characters. `to_upper` changes only the letters `a` to `z`, so `é` stays as it is.
:::

## 2.4 Names: `let` and `let edit`

### What a name is

A **name**, or **binding**, ties a word to a value, so that later lines can use the value by its word. Think of a sticky label on a box: the label says `total`, and the box holds 8480. You met `let` in [chapter 1](/learn/hello/#naming-a-value-let). This section shows the two kinds of name and the rules they follow.

### Why names do not change by default

Most values in a function are computed once: a price, a SKU, the result of a call. If any line could give such a name a new value, a reader would have to read every line to know what the name holds at a given point. So a plain `let` name never changes. Try to assign one:

```diff include="steps/14-till..steps/13-assign-let:src/till.una" title="src/till.una" context="1"
--- a/src/till.una
+++ b/src/till.una
@@ -7,3 +7,3 @@
   let lamp = 1_990
-  let edit total = 0
+  let total = 0
   let edit items = 0
```

```text include="steps/13-assign-let/expected/rendered.txt#L1"
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

### A running total at the till

A till adds up the items a cashier scans, so its total is an editable name:

:::steps
```una include="steps/14-till/src/till.una" title="src/till.una" verified="check, run"
module till

--- Prints the running total of a till as three items are scanned.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = 1_990
  let edit total = 0
  let edit items = 0
  total = total + lamp
  items = items + 1
  total = total + lamp
  items = items + 1
  @console.print("{items} items, {total} cents")
  total = total + 4_500
  items = items + 1
  @console.print("{items} items, {total} cents")
  let edit receipt: Text = "LAMP-01"
  receipt = "{receipt}, LAMP-01, RUG-07"
  @console.print(receipt)
```

1. **`let lamp = 1_990`.** A plain name. Its type, `Int`, comes from its value.
2. **`let edit total = 0`.** An editable name, which later lines may assign. Its type is fixed by its first value: every later value must be an `Int`.
3. **`total = total + lamp`.** An assignment. It is a statement on its own line, and it gives `total` a new value.
4. **`let edit receipt: Text = "LAMP-01"`.** A type written after the name, with `:`. It is optional here, but it tells a reader what the name will hold.
5. **`receipt = "{receipt}, LAMP-01, RUG-07"`.** A text that starts with the old value: the way to add to a text.
:::

`una run .` prints:

```text include="steps/14-till/expected/output.txt"
2 items, 3980 cents
3 items, 8480 cents
LAMP-01, LAMP-01, RUG-07
```

> [!NOTE]
> `let edit` belongs to edition `0.2` and later. In a package of edition `0.1`, `edit` is a reserved word, and every name is a plain `let`.

### How names behave

#### A name lives to the end of its block

A **block** is a run of lines at the same indentation, such as the body of a function. A name exists from its `let` line to the end of its block. A line before the `let` cannot use it.

#### One name, one meaning: no shadowing

Making the same name a second time is an error, even with `let` both times:

```diff include="steps/14-till..steps/15-rebind:src/till.una" title="src/till.una" context="1"
--- a/src/till.una
+++ b/src/till.una
@@ -7,2 +7,3 @@
   let lamp = 1_990
+  let lamp = 2_490
   let edit total = 0
```

```text include="steps/15-rebind/expected/rendered.txt"
[U1002] Error: `lamp` is already bound in this scope; a local cannot rebind another
   ╭─[ src/till.una:8:7 ]
   │
 7 │   let lamp = 1_990
   │       ──┬─
   │         ╰─── first defined here
 8 │   let lamp = 2_490
   │       ──┬─
   │         ╰─── `lamp` is already bound in this scope; a local cannot rebind another
   │
   │ Note: run `una explain U1002` for an explanation
───╯
```

The diagnostic marks both lines: where the name was first defined, and where it was made again. Some languages allow the second `let`, which **shadows** the first: the old value is still there, hidden behind the new one. Una does not, inside a block or in a block nested in it, so a name means one thing from its line to the end of its block. To change a value, use `let edit` and an assignment; for a different value, choose a different name.

#### An editable name keeps its type

`let edit items = 0` makes `items` an `Int` for good. Assign it a text:

```diff include="steps/14-till..steps/16-edit-type:src/till.una" title="src/till.una" context="1"
--- a/src/till.una
+++ b/src/till.una
@@ -10,3 +10,3 @@
   total = total + lamp
-  items = items + 1
+  items = "one"
   total = total + lamp
```

```text include="steps/16-edit-type/expected/rendered.txt#L1"
[U2001] Error: expected `Int`, found `Text`
```

The checker expected an `Int`, the type of `items`, and found a `Text`.

#### Adding to a text in place

`receipt = "{receipt}, …"` does not copy the whole text each time. When an assignment adds to the end of a text that nothing else holds, the text grows in place, so building a long text this way takes time in proportion to its length.

### Choosing between `let` and `let edit`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Name a value you compute once | `let` |
| Keep a total, a count or a text that grows | `let edit`, and assignments |
| Say what type a name holds | `let name: Type = …`, with either form |
| A value that differs by case | `let` with an `if … then … else`, not a `let edit` assigned in two places |
:::

Prefer `let`. A name that cannot change is one less thing a reader must track, and in most functions every name can be a `let`. Use `let edit` when a value really accumulates, as `total` does here, and as loops do in [chapter 5](/learn/collections/).

### Check yourself: names

A shelf holds 10 units. Three are sold, then a delivery brings five:

```una include="steps/17-restock/src/restock.una" title="steps/17-restock/src/restock.una"
module restock

--- Prints the stock of a shelf after a sale and a delivery.
pub main() -> Unit
  uses @console: Console[print]
=
  let edit stock = 10
  stock = stock - 3
  let sold = 10 - stock
  stock = stock + 5
  @console.print("{stock} in stock, {sold} sold")
```

What does it print?

:::answer Show the answer
```text include="steps/17-restock/expected/output.txt"
12 in stock, 3 sold
```

`stock` goes 10, 7, 12. `sold` is computed once, when `stock` is 7, so it is 3, and it stays 3 when `stock` changes later: a plain `let` holds the value it was given, not a formula.
:::

## 2.5 Fixed-width integers

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

```una include="steps/18-overflow/src/printer.una#copies" title="steps/18-overflow/src/printer.una"
--- How many copies of a label to print: one per facing on the shelf, and one spare.
--- The label printer reads the count as one byte, so it is a `U8`.
pub copies(facings: U8) -> U8 = facings + 1
```

```text include="steps/18-overflow/expected/rendered.txt#L1,L8,L10,L12,L16"
[U5001] Error: overflow obligation `facings + 1 in 0..255` is refuted
   │ Help 1: repair 1: guard the operation with `if facings.to_int() + 1 in 0..255`
   │ Help 2: repair 2: give the values a wider type, converting them explicitly
   │ Help 3: repair 3: if wrapping or saturating is meant, use `wrapping_add`, `saturating_add` or their siblings
   │ Note 2: counterexample: facings = 255
```

The obligation `facings + 1 in 0..255` says that the sum must lie between 0 and 255, and the counterexample is the one value that breaks it, 255. The repairs list the three honest choices: check the range first, use a wider type, or say that wrapping or saturating is what you mean. Each makes the behavior at the edge of the range visible in the code.

### How to write fixed-width values

#### A literal takes the type its place expects

`let copies: U8 = 200` makes 200 a `U8`, since the name says so. A literal also takes the type of the parameter it is passed to, or of the other side of an operator. A literal that does not fit its type is U2022, and [A literal out of range](#a-literal-out-of-range-u2022), in Common mistakes, shows it.

#### Converting between integer types

- `x.to_int()` turns any fixed-width value into an `Int`. Every value fits, so it never fails.
- `x.to_u8()`, `x.to_u16()`, `x.to_i32()` and the others turn a value into a narrower type. Each is a proof obligation that the value fits.
- A `U8` and an `Int`, or a `U8` and a `U16`, do not mix in one operation: convert one of them first.

#### Wrapping and saturating, by name

- `a.wrapping_add(by: b)`, `wrapping_sub` and `wrapping_mul` wrap around, as other languages do silently.
- `a.saturating_add(by: b)`, `saturating_sub` and `saturating_mul` stop at the end of the range: at 0 or at the largest value.

These never leave the range, so they need no proof.

The step writes each form:

```una include="steps/19-fixed-forms/src/widths.una#L1-L14" title="steps/19-fixed-forms/src/widths.una"
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

```text include="steps/19-fixed-forms/expected/output.txt#L1-L4"
200, -128 and 18446744073709551615
300 as an Int
44 wrapped, 255 saturated
42 as a U8
```

`copies.to_int() + 100` is an `Int`, so 300 is fine. In a `U8`, 200 + 100 wraps to 44 or saturates at 255. `count.to_u8()` narrows the `Int` 42: the verifier knows `count` is 42, so it proves that it fits.

### Label copies as one byte: `U8`

The module `printer` counts the copies of a shelf label in a `U8`, and a roll of labels in a `U16`:

:::steps
```una include="steps/20-printer/src/printer.una" title="src/printer.una" verified="check, run"
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
2. **`requires facings < 255`.** A **precondition**: a fact every caller must make true, written on its own line under the header, before `=`. It makes `facings + 1` fit in a `U8`, so the verifier proves the addition, and it proves the precondition at each call. [Chapter 7](/learn/contracts/#s7-1) covers preconditions in full.
3. **`let lamps: U8 = 4`.** A literal takes the type its context expects, here `U8`. A literal that does not fit, such as `300`, does not check.
4. **`lamp_labels.to_int() + mug_labels.to_int()`.** Two `U8` values turned into `Int` before they are added. Every `U8` fits in an `Int`, so `to_int()` always succeeds; the sum is an `Int` and cannot overflow.
5. **`roll.saturating_sub(by: 1_200)`.** Subtraction that stops at the bottom of the range, 0, instead of going below it. Methods such as this one say in their names what happens at the ends of the range.
:::

`una run .` prints:

```text include="steps/20-printer/expected/output.txt"
5 and 13 labels
18 labels in all
0 left on a roll of 1000 after 1200
```

### How fixed-width integers behave

- **No silent wrap.** Every operation that could leave the range is an obligation, and a refuted one does not check.
- **Literals are checked at once.** A literal that does not fit its type is U2022, before any proof.
- **A constant computation is proved, not folded.** `200 + 100` where a `U8` is expected is not one literal: it gets an overflow obligation, which is refuted.
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

```diff include="steps/19-fixed-forms..steps/21-constant-overflow:src/widths.una" title="src/widths.una" context="0"
--- a/src/widths.una
+++ b/src/widths.una
@@ -7 +7 @@
-  let copies: U8 = 200
+  let copies: U8 = 200 + 100
```

Does it still check? And in the original step, what does the last line print, with `roll` holding 500?

```una include="steps/19-fixed-forms/src/widths.una#L15-L16" title="steps/19-fixed-forms/src/widths.una"
  let roll: U16 = 500
  @console.print("{roll.saturating_sub(by: 600)} and {roll.wrapping_sub(by: 600)}")
```

:::answer Show the answer
It does not check:

```text include="steps/21-constant-overflow/expected/rendered.txt#L1"
[U5001] Error: overflow obligation `200 + 100 in 0..255` is refuted
```

`200 + 100` is 300, which a `U8` cannot hold, and the verifier proves that the sum leaves the range. The last line of the original prints:

```text include="steps/19-fixed-forms/expected/output.txt#L5"
0 and 65436
```

500 − 600 is −100. `saturating_sub` stops at 0. `wrapping_sub` wraps around the 65536 values of a `U16`: −100 + 65536 is 65436.
:::

## 2.6 Day-to-day: shelf labels

### What the program must do

Every product on a shelf has a label: its SKU, its name, and its price. The labels change every week, as prices change and sales start and end, so the store prints them from its catalog. The data is messy in the usual ways. SKUs arrive with stray spaces and in small letters, some names are longer than the label, and a product sold by weight must show its price per kilogram as well.

The program follows the data. Each fix to a value is a small function with a doc comment and an example: clean the SKU, fit the name, write the price. Each kind of label is a function built from those. `main` prints the labels of four products and counts the copies to print. Every section of this chapter has its part:

- `Int` cents and Euclidean division ([section 2.1](#s2-1)) write the prices, and a precondition makes a division by a parameter safe.
- `Bool` ([section 2.2](#s2-2)) states the store's rule for a sale.
- The prelude's text functions and a proved `slice` ([section 2.3](#s2-3)) clean SKUs and fit names.
- A `let edit` total ([section 2.4](#s2-4)) counts the copies.
- A `U8` ([section 2.5](#s2-5)) is the count the label printer reads.

### Cleaning the values

Three functions turn raw values into what a label prints:

```una include="day-to-day/src/labels.una#clean_sku..money" title="day-to-day/src/labels.una" caption="clean, fit, format"
--- The SKU as labels print it: without the white space around it, in capital letters.
pub clean_sku(raw: Text) -> Text = raw.trim.to_upper

--- A product name cut to the 24 characters a label has room for.
pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name

--- Cents as an amount with two decimals, for an amount that is not negative: 1990 is "19.90".
pub money(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"
```

`money` writes the two digits of the cents one by one, as in the last exercise of [chapter 1](/learn/hello/#exercise-3-amounts-with-two-decimals), so 1205 is `12.05` and never `12.5`. Its doc comment states that it is for amounts that are not negative, since a refund would need the rule of [Euclidean division](#euclidean-division), in section 2.1.

### Sale prices and prices per kilogram

A sale price and a price per kilogram, each rounded down to a whole cent:

```una include="day-to-day/src/labels.una#on_sale..per_kilo" title="day-to-day/src/labels.una" caption="the prices"
--- Whether a discount is one the store runs: from 1 to 90 percent off.
pub on_sale(percent: Int) -> Bool = percent >= 1 and percent <= 90

--- The price after `percent` off, rounded down to a whole cent.
pub sale_cents(cents: Int, percent: Int) -> Int = cents * (100 - percent) / 100

--- The price of one kilogram, in cents, for a pack of `grams` grams, rounded down.
pub per_kilo(cents: Int, grams: Int) -> Int
  requires grams > 0
=
  cents * 1000 / grams
```

`on_sale` turns a store rule into a `Bool`: a discount from 1 to 90 percent is one the store runs. `sale_cents` multiplies before it divides, so a 15 percent discount on 1999 cents gives 1699, the price rounded down. `per_kilo` divides by `grams`, a parameter, so it needs a reason why `grams` is not zero. Its precondition, `requires grams > 0`, is that reason. The verifier then proves the division, and every caller must prove `grams > 0` in turn.

### Three kinds of label

Three kinds of label, each a line of text:

```una include="day-to-day/src/labels.una#regular_label..weight_label" title="day-to-day/src/labels.una" caption="three kinds of label"
--- The label of a product at its regular price.
pub regular_label(sku: Text, name: Text, cents: Int) -> Text = "{clean_sku(sku)} | {fit_name(name)} | {money(cents)}"

--- The label of a product on sale, with the old price and the new one. A discount the
--- store does not run gives the regular label.
pub sale_label(sku: Text, name: Text, cents: Int, percent: Int) -> Text
=
  let now = sale_cents(cents, percent: percent)
  let regular = regular_label(sku, name: name, cents: cents)
  if on_sale(percent) then "{regular}, now {money(now)} ({percent}% off)" else regular

--- The label of a product sold by weight, with the price of one kilogram.
pub weight_label(sku: Text, name: Text, cents: Int, grams: Int) -> Text
  requires grams > 0
=
  let kilo = per_kilo(cents, grams: grams)
  "{regular_label(sku, name: name, cents: cents)} ({money(kilo)} per kg)"
```

`sale_label` names two values with `let`, then chooses between two texts with `if`: the sale label when `on_sale(percent)` holds, and the regular label otherwise. A discount of 95 percent is more likely a typing mistake than a sale, so the label then shows the regular price. `weight_label` repeats its callee's precondition, `requires grams > 0`, since it passes `grams` on to `per_kilo`, and a precondition must be proved at every call.

### Copies, and `main`

`copies` gives the count the printer reads, as in [section 2.5](#s2-5). `main` prints each label and adds its copies to a running total, which is a `let edit` name:

```una include="day-to-day/src/labels.una#copies..main" title="day-to-day/src/labels.una"
--- How many copies of a label to print: one for each facing on the shelf, and one spare.
--- The label printer reads the count as one byte, so it is a `U8`.
pub copies(facings: U8) -> U8
  requires facings < 255
=
  facings + 1

--- Prints the labels of four products, and how many copies to print in all.
pub main() -> Unit
  uses @console: Console[print]
=
  let edit printed = 0
  @console.print(regular_label(" lamp-01", name: "Desk lamp, brass", cents: 1990))
  printed = printed + copies(4).to_int()
  @console.print(sale_label("rug-07 ", name: "Wool rug, 120 by 180 cm, natural", cents: 4500, percent: 15))
  printed = printed + copies(2).to_int()
  @console.print(weight_label("coffee-05", name: "Coffee beans, dark roast", cents: 1250, grams: 500))
  printed = printed + copies(12).to_int()
  @console.print(regular_label("DESK-02", name: "Oak writing desk", cents: 15900))
  printed = printed + copies(1).to_int()
  @console.print("{printed} labels to print")
```

`copies(4)` passes a literal, which takes the type `U8` from the parameter. `copies(4).to_int()` converts the result before it is added to `printed`, an `Int`, since the two types do not mix. The verifier proves the precondition of each call, `4 < 255` and the others, from the literals. It also proves `500 > 0` for the call of `weight_label`.

The two kinds of integer meet only at that one conversion. `copies` speaks the printer's language, a byte, because that is what the printer reads; `printed` is an `Int`, because a total has no reason to stop at 255. Converting at the boundary keeps each type where it belongs.

### Running it

`una run .` prints the labels shown in [What you'll build](#what-youll-build). The rug's name is cut to 24 characters, which ends it on a comma: the rule is simple, and the label shows it. The SKUs come out clean, the coffee shows 25.00 per kilogram for a 500 g pack at 12.50, and the copies add up to 23: 5, 3, 13 and 2.

> [!TIP]
> When a function divides by a parameter or cuts a text at a computed position, write the precondition first, then the body. The verifier tells you at once whether the precondition is enough, and each caller learns what it must provide.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/labels.una" title="day-to-day/src/labels.una" caption="the whole program" verified="check, run, test"
module labels

-- Shelf labels: one line for each product, as the label printer prints it, and how many
-- copies of the labels to print.

--- The SKU as labels print it: without the white space around it, in capital letters.
pub clean_sku(raw: Text) -> Text = raw.trim.to_upper

--- A product name cut to the 24 characters a label has room for.
pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name

--- Cents as an amount with two decimals, for an amount that is not negative: 1990 is "19.90".
pub money(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"

--- Whether a discount is one the store runs: from 1 to 90 percent off.
pub on_sale(percent: Int) -> Bool = percent >= 1 and percent <= 90

--- The price after `percent` off, rounded down to a whole cent.
pub sale_cents(cents: Int, percent: Int) -> Int = cents * (100 - percent) / 100

--- The price of one kilogram, in cents, for a pack of `grams` grams, rounded down.
pub per_kilo(cents: Int, grams: Int) -> Int
  requires grams > 0
=
  cents * 1000 / grams

--- The label of a product at its regular price.
pub regular_label(sku: Text, name: Text, cents: Int) -> Text = "{clean_sku(sku)} | {fit_name(name)} | {money(cents)}"

--- The label of a product on sale, with the old price and the new one. A discount the
--- store does not run gives the regular label.
pub sale_label(sku: Text, name: Text, cents: Int, percent: Int) -> Text
=
  let now = sale_cents(cents, percent: percent)
  let regular = regular_label(sku, name: name, cents: cents)
  if on_sale(percent) then "{regular}, now {money(now)} ({percent}% off)" else regular

--- The label of a product sold by weight, with the price of one kilogram.
pub weight_label(sku: Text, name: Text, cents: Int, grams: Int) -> Text
  requires grams > 0
=
  let kilo = per_kilo(cents, grams: grams)
  "{regular_label(sku, name: name, cents: cents)} ({money(kilo)} per kg)"

--- How many copies of a label to print: one for each facing on the shelf, and one spare.
--- The label printer reads the count as one byte, so it is a `U8`.
pub copies(facings: U8) -> U8
  requires facings < 255
=
  facings + 1

--- Prints the labels of four products, and how many copies to print in all.
pub main() -> Unit
  uses @console: Console[print]
=
  let edit printed = 0
  @console.print(regular_label(" lamp-01", name: "Desk lamp, brass", cents: 1990))
  printed = printed + copies(4).to_int()
  @console.print(sale_label("rug-07 ", name: "Wool rug, 120 by 180 cm, natural", cents: 4500, percent: 15))
  printed = printed + copies(2).to_int()
  @console.print(weight_label("coffee-05", name: "Coffee beans, dark roast", cents: 1250, grams: 500))
  printed = printed + copies(12).to_int()
  @console.print(regular_label("DESK-02", name: "Oak writing desk", cents: 15900))
  printed = printed + copies(1).to_int()
  @console.print("{printed} labels to print")

example "a SKU loses its spaces and is written in capitals"
  do clean_sku("  lamp-01 ")
  expect result == "LAMP-01"

example "a long name is cut to 24 characters"
  do fit_name("Wool rug, 120 by 180 cm, natural")
  expect result.len == 24

example "a short name is kept as it is"
  do fit_name("Desk lamp, brass")
  expect result == "Desk lamp, brass"

example "an amount keeps the zero of its cents"
  do money(1205)
  expect result == "12.05"

example "a discount rounds down to a whole cent"
  do sale_cents(1999, percent: 15)
  expect result == 1699

example "a discount over 90 percent is not a sale"
  do on_sale(95)
  expect result == false

example "the price of a kilogram of a 500 g pack is twice the price"
  do per_kilo(1250, grams: 500)
  expect result == 2500

example "a sale label shows the old and the new price"
  do sale_label("rug-07", name: "Wool rug", cents: 4500, percent: 15)
  expect result == "RUG-07 | Wool rug | 45.00, now 38.25 (15% off)"

example "a shelf with four facings gets five labels"
  do copies(4)
  expect result == 5
```

## 2.7 Testing it

### Examples at the edges

Every function of the program but `main` is pure, with no `uses` line, so each one gets examples that give it values and check what it returns. The examples aim at the edges, where values go wrong:

```una include="day-to-day/src/labels.una#L67-L101" title="day-to-day/src/labels.una" caption="the examples"
example "a SKU loses its spaces and is written in capitals"
  do clean_sku("  lamp-01 ")
  expect result == "LAMP-01"

example "a long name is cut to 24 characters"
  do fit_name("Wool rug, 120 by 180 cm, natural")
  expect result.len == 24

example "a short name is kept as it is"
  do fit_name("Desk lamp, brass")
  expect result == "Desk lamp, brass"

example "an amount keeps the zero of its cents"
  do money(1205)
  expect result == "12.05"

example "a discount rounds down to a whole cent"
  do sale_cents(1999, percent: 15)
  expect result == 1699

example "a discount over 90 percent is not a sale"
  do on_sale(95)
  expect result == false

example "the price of a kilogram of a 500 g pack is twice the price"
  do per_kilo(1250, grams: 500)
  expect result == 2500

example "a sale label shows the old and the new price"
  do sale_label("rug-07", name: "Wool rug", cents: 4500, percent: 15)
  expect result == "RUG-07 | Wool rug | 45.00, now 38.25 (15% off)"

example "a shelf with four facings gets five labels"
  do copies(4)
  expect result == 5
```

### What each example covers

Each one covers a rule that the sample run alone would hide:

- "a long name is cut to 24 characters" checks the length of the result, `result.len`, not its text: the fact that matters is the width.
- "an amount keeps the zero of its cents" covers 1205, whose cents are under ten, a case none of the four products reaches.
- "a discount rounds down to a whole cent" fixes the rounding: 1999 cents at 15 percent off is 1699.15, and the store charges 1699.
- "a discount over 90 percent is not a sale" checks the store rule at a value outside it.
- "a shelf with four facings gets five labels" checks a `U8` result against a literal, which takes the type `U8` from the other side of `==`.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L12"
example labels "a SKU loses its spaces and is written in capitals" ... ok
example labels "a long name is cut to 24 characters" ... ok
example labels "a short name is kept as it is" ... ok
example labels "an amount keeps the zero of its cents" ... ok
example labels "a discount rounds down to a whole cent" ... ok
example labels "a discount over 90 percent is not a sale" ... ok
example labels "the price of a kilogram of a 500 g pack is twice the price" ... ok
example labels "a sale label shows the old and the new price" ... ok
example labels "a shelf with four facings gets five labels" ... ok

9 examples: 9 passed, 0 failed
```

### The case no example needs: zero grams

No example tests what happens when `grams` is 0, and none can: an example is code, and `una check .` proves the precondition of every call in it as in any other code. A call `per_kilo(1250, grams: 0)` in an example is refuted before the example runs, which is the strongest test of that case there is.

## 2.8 Common mistakes

Each mistake below is a small change to `day-to-day/src/labels.una`, followed by what `una check .` reports.

### Joining texts with `+` (U2001)

:::mistake
Build the weight label with `+`, as many languages allow:

```diff include="day-to-day..mistakes/1:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -42,3 +42,3 @@
   let kilo = per_kilo(cents, grams: grams)
-  "{regular_label(sku, name: name, cents: cents)} ({money(kilo)} per kg)"
+  regular_label(sku, name: name, cents: cents) + " ({money(kilo)} per kg)"
 
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U2001] Error: an operand of `+` must be `Int`, found `Text`
```

*Why:* `+` adds numbers. A text is not a number, and Una converts neither side. The message names the operator and the type it found, and the marks point at the operand that is a text. una also reports that the function no longer returns a `Text`, since `+` gives an `Int`: one mistake, two consequences, and fixing the first removes both.

*Fix:* join texts with an interpolation, `"{regular_label(sku, name: name, cents: cents)} ({money(kilo)} per kg)"`. See [U2001](/docs/errors/U2001/).
:::

### Assigning a plain `let` (U2019)

:::mistake
Declare the running total with `let`:

```diff include="day-to-day..mistakes/2:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -55,3 +55,3 @@
 =
-  let edit printed = 0
+  let printed = 0
   @console.print(regular_label(" lamp-01", name: "Desk lamp, brass", cents: 1990))
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U2019] Error: `printed` is not editable; declare it `let edit printed`, or the parameter `edit printed`
```

*Why:* a name declared with `let` holds one value. una reports each of the four assignments, one diagnostic each, and the message gives the exact declaration to write.

*Fix:* `let edit printed = 0`, as the message says. See [U2019](/docs/errors/U2019/).
:::

### Dividing by a parameter (U5001)

:::mistake
Remove the precondition of `per_kilo`, which canonical form then writes on one line:

```diff include="day-to-day..mistakes/3:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -21,6 +21,3 @@
 --- The price of one kilogram, in cents, for a pack of `grams` grams, rounded down.
-pub per_kilo(cents: Int, grams: Int) -> Int
-  requires grams > 0
-=
-  cents * 1000 / grams
+pub per_kilo(cents: Int, grams: Int) -> Int = cents * 1000 / grams
 
```

```text include="mistakes/3/expected/rendered.txt#L1,L8,L12"
[U5001] Error: division obligation `grams != 0` is refuted
    │ Help: repair 1: guard the division with `if grams != 0`
    │ Note 2: counterexample: cents = 0, grams = 0
```

*Why:* `grams` may be 0, and a division by zero is never allowed to run. The first line names the obligation, `grams != 0`; the `Note 2` line is the counterexample, the case that breaks it, with every parameter's value. `cents = 0` is there only because the solver had to pick some value; `grams = 0` is what matters.

*Fix:* put back `requires grams > 0`, so that each caller proves it, or guard the division as the `Help` line says. See [U5001](/docs/errors/U5001/).
:::

### A text inside an interpolation (U0006)

:::mistake
Print a label through an interpolation, with its arguments written in place:

```diff include="day-to-day..mistakes/4:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -62,3 +62,3 @@
   printed = printed + copies(12).to_int()
-  @console.print(regular_label("DESK-02", name: "Oak writing desk", cents: 15900))
+  @console.print("{regular_label("DESK-02", name: "Oak writing desk", cents: 15900)}")
   printed = printed + copies(1).to_int()
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U0006] Error: text literal inside interpolation; bind it with `let` and interpolate the name
```

*Why:* the braces of an interpolation cannot hold a text literal, since its quotes would end the outer text. una reports each of the two, and the message gives the repair.

*Fix:* print the label itself, `@console.print(regular_label(…))`, or name the texts with `let` first, as the message says. See [U0006](/docs/errors/U0006/).
:::

### A literal out of range (U2022)

:::mistake
Give a shelf 300 facings:

```diff include="day-to-day..mistakes/5:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -61,3 +61,3 @@
   @console.print(weight_label("coffee-05", name: "Coffee beans, dark roast", cents: 1250, grams: 500))
-  printed = printed + copies(12).to_int()
+  printed = printed + copies(300).to_int()
   @console.print(regular_label("DESK-02", name: "Oak writing desk", cents: 15900))
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U2022] Error: the literal `300` does not fit `U8`, which holds `0` to `255`
```

*Why:* the parameter of `copies` is a `U8`, so the literal is a `U8`, and 300 does not fit. The message gives the type and its range, `0` to `255`. This check needs no proof: the checker sees the literal and the type.

*Fix:* a value that fits, or a wider type for the parameter if the printer accepts one. See [U2022](/docs/errors/U2022/).
:::

### A number as a condition (U2001)

:::mistake
Test the discount itself, as if a number could be true:

```diff include="day-to-day..mistakes/6:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -35,3 +35,3 @@
   let regular = regular_label(sku, name: name, cents: cents)
-  if on_sale(percent) then "{regular}, now {money(now)} ({percent}% off)" else regular
+  if percent then "{regular}, now {money(now)} ({percent}% off)" else regular
 
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U2001] Error: the condition of `if` must be `Bool`, found `Int`
```

*Why:* a condition must be a `Bool`. An `Int` is never true or false. The message names the place, the condition of `if`, the type it needs and the type it found.

*Fix:* say the rule: `if on_sale(percent)`, or `if percent > 0`. See [U2001](/docs/errors/U2001/).
:::

## 2.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added at the end, and a stub of the function to write, whose body is a placeholder value. `una test .` fails there until the exercise is done. Work as in [chapter 1](/learn/hello/#s1-10):

1. Read the examples: they say what the function must return.
2. Write the body, in place of the placeholder.
3. Run `una fmt .`, then `una check .`. When the verifier refutes something, read the counterexample: it is the input your code does not handle yet.
4. Run `una test .` until every example passes.

### Exercise 1: sales tax

::::exercise
Write `with_tax(cents, percent)`, the price with a sales tax of `percent` added, rounded to the nearest cent, with half a cent rounding up. The start package ends with:

```una include="exercises/1/start/src/labels.una#L103-L113" title="exercises/1/start/src/labels.una"
--- The price with `percent` of sales tax added, rounded to the nearest cent; half a cent
--- rounds up.
pub with_tax(cents: Int, percent: Int) -> Int = cents

example "tax is added and rounded down below half a cent"
  do with_tax(1990, percent: 8)
  expect result == 2149

example "half a cent rounds up"
  do with_tax(1990, percent: 5)
  expect result == 2090
```

:::hint
*Hint:* `cents * (100 + percent)` is the price in hundredths of a cent: for 1990 cents and 8 percent, 214920. `/ 100` alone would round down. Adding half of 100, 50, before dividing by 100 makes every value from half a cent up reach the next cent.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L11-L18"
example labels "tax is added and rounded down below half a cent" ... FAILED
  src/labels.una:109: expect result == 2149
  it is false, with `result` = `1990`
example labels "half a cent rounds up" ... FAILED
  src/labels.una:113: expect result == 2090
  it is false, with `result` = `1990`

11 examples: 9 passed, 2 failed
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Give `with_tax` its body:

```diff include="exercises/1/start..exercises/1/answer:src/labels.una" context="1" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -104,3 +104,3 @@
 --- rounds up.
-pub with_tax(cents: Int, percent: Int) -> Int = cents
+pub with_tax(cents: Int, percent: Int) -> Int = (cents * (100 + percent) + 50) / 100
 
```

1990 cents with 8 percent is 214920 hundredths of a cent; adding 50 and dividing by 100 gives 2149. With 5 percent it is 208950, which rounds up to 2090.
:::
::::

### Exercise 2: the price of one unit in a pack

::::exercise
A pack of olive soap holds six bars. Write `pack_label(sku, name, cents, units)`, the regular label followed by the price of one unit, and print the label of the soap in `main`, with three copies. The start package ends with:

```una include="exercises/2/start/src/labels.una#L103-L108" title="exercises/2/start/src/labels.una"
--- The label of a pack of several units, with the price of one unit.
pub pack_label(sku: Text, name: Text, cents: Int, units: Int) -> Text = ""

example "a pack label shows the price of one unit"
  do pack_label("soap-12", name: "Olive soap, 6 bars", cents: 900, units: 6)
  expect result == "SOAP-12 | Olive soap, 6 bars | 9.00 (1.50 each)"
```

:::hint
*Hint:* the price of one unit is a division by `units`, a parameter. Write it as `per_kilo` is written, and let `una check .` tell you what is missing.
:::

Check your answer with `una test .`, then `una run .` for the new label.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Give `pack_label` a precondition and its body, and print the soap's label in `main`:

```diff include="exercises/2/start..exercises/2/answer:src/labels.una" context="1" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -64,2 +64,4 @@
   printed = printed + copies(1).to_int()
+  @console.print(pack_label("soap-12", name: "Olive soap, 6 bars", cents: 900, units: 6))
+  printed = printed + copies(3).to_int()
   @console.print("{printed} labels to print")
@@ -103,3 +105,7 @@
 --- The label of a pack of several units, with the price of one unit.
-pub pack_label(sku: Text, name: Text, cents: Int, units: Int) -> Text = ""
+pub pack_label(sku: Text, name: Text, cents: Int, units: Int) -> Text
+  requires units > 0
+=
+  let each = cents / units
+  "{regular_label(sku, name: name, cents: cents)} ({money(each)} each)"
 
```

Without `requires units > 0`, `una check .` reports U5001 for the division, with `units = 0` in the counterexample. With it, the verifier proves the division, and proves `6 > 0` at the call in `main`. The copies now add up to 27.
:::
::::

### Exercise 3: labels left on the roll

::::exercise
The label printer counts the labels left on its roll as a `U16`. Write `labels_left(roll, printed)`, which subtracts what was printed, and gives 0 when more was printed than the roll held. The start package ends with:

```una include="exercises/3/start/src/labels.una#L103-L113" title="exercises/3/start/src/labels.una"
--- How many labels are left on a roll after `printed` of them. A roll holds at most a few
--- thousand labels, so the count is a `U16`. Printing more than the roll holds leaves none.
pub labels_left(roll: U16, printed: U16) -> U16 = roll

example "printing takes labels off the roll"
  do labels_left(1_000, printed: 23)
  expect result == 977

example "printing more than the roll holds leaves no labels"
  do labels_left(10, printed: 23)
  expect result == 0
```

:::hint
*Hint:* try `roll - printed` first, and read what `una check .` reports. One of its repairs names the kind of method you need.
:::

Check your answer with `una test .`. A `U16` holds 0 to 65535, as the table of [section 2.5](#s2-5) shows.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Give `labels_left` its body:

```diff include="exercises/3/start..exercises/3/answer:src/labels.una" context="1" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -104,3 +104,3 @@
 --- thousand labels, so the count is a `U16`. Printing more than the roll holds leaves none.
-pub labels_left(roll: U16, printed: U16) -> U16 = roll
+pub labels_left(roll: U16, printed: U16) -> U16 = roll.saturating_sub(by: printed)
 
```

`roll - printed` is refuted, with a counterexample where `printed` is larger than `roll`. `saturating_sub` stops at 0, which is exactly the rule of the exercise, and needs no proof, since it never leaves the range.
:::
::::

## 2.10 Recap and reference

### For agents

:::agents
`una --json check .` reports each diagnostic with its `code`, `message` and `primary` span. A refuted obligation, U5001, also carries a `counterexample` with one binding for each value, and repairs ranked from the guard to the escape. U2001, U2019 and U2022 carry no repair, since the right type or value is the author's choice. The compact rule: *money is `Int` cents; join text with interpolation, never `+`; a name that changes is `let edit`; a division by a parameter or a `slice` at computed positions needs a `requires` or a guard; fixed-width arithmetic needs a proof that it fits.*
:::

### Recap

:::recap
- `Int` has no bound, so its arithmetic is exact. Keep money in whole cents.
- `/` and `mod` are Euclidean: the remainder is never negative. A division by a value that may be zero does not check.
- A condition is a `Bool`: compare, then combine with `and`, `or` and `not`. Comparisons do not chain.
- Join texts with interpolation, never `+`, and name a text literal before you use it in braces.
- `slice` states what it requires, and the verifier proves it at each call: guard the call with an `if`, or pass it on with `requires`.
- Prefer `let`. Use `let edit` for a value that accumulates; a name is bound once per block.
- Use a fixed-width type only where a width is required: its arithmetic is proved to fit, and conversions are explicit. Both it and `let edit` need edition `0.2`.
:::

### Reference

:::reference
- Construct pages: [literals and operators](/docs/language/lexical-structure/), [built-in types](/docs/language/types/), [`let` and `if`](/docs/language/control-flow/), [`let edit`](/docs/language/control-flow/let-edit/), [`requires`](/docs/language/functions/requires/)
- Guides: [fixed-width integers](/docs/guides/fixed-width-integers/), [work with text](/docs/guides/text/)
- Standard library: [the prelude](/docs/std/) (`Int`, `Bool`, `Text`, `trim`, `starts_with`), [text](/docs/std/text/) (`slice`, `replace`, `contains_text`, `to_upper`, `split`), [the built-in methods](/docs/std/builtin/) (`.len`, `to_int`, `to_u8`, `saturating_sub`)
- Diagnostics: [U0006](/docs/errors/U0006/), [U0101](/docs/errors/U0101/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2019](/docs/errors/U2019/), [U2022](/docs/errors/U2022/), [U5001](/docs/errors/U5001/)
- Specification: [lexical structure](/docs/spec/01-lexical-structure/), [types](/docs/spec/03-types/), [the standard library](/docs/spec/14-standard-library/), [the memory model](/docs/spec/17-memory-model/), [fixed-width integers](/docs/spec/18-fixed-width-integers/), [text](/docs/spec/22-text/)
:::
