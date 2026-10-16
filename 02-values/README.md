---
learn: "2"
title: Values
editions: ["0.2"]
codes: [U0006, U2001, U2019, U2022, U5001]
time: 35
builds: The shelf labels of a store, with prices, sale prices, prices per kilogram and the number of copies to print
prerequisites: ["1"]
template: 2
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
1. **`Int` has no bound.** It is a whole number of any size, so a sum or a product is always exact. Where a width matters, you choose a fixed-width type, and the verifier proves that every operation stays in its range.
2. **Division is defined everywhere it can run.** The remainder of a division is never negative, and a division by a value that may be zero does not check.
3. **`Bool` is its own type.** A condition must be a `Bool`. An `Int` or a `Text` is never read as true or false.
4. **Operations state what they need.** Cutting a text requires positions inside it, and the verifier proves it at each call, from the code around the call.
:::

> [!KEY]
> A value in Una means exactly what its type says. No value turns into another type unless the code says so, and no operation can leave the range of its type at run time.

## 2.1 Numbers: `Int`

An `Int` is a whole number, positive, zero or negative, with no limit on its size. You write it in decimal, and you may group the digits with `_`, as `1_990` or `10_000`. The usual operators work on it: `+`, `-`, `*`, `/` for division and `mod` for the remainder, with the usual precedence, and parentheses to group.

Money is an `Int` of cents, in this chapter and in every chapter of this tutorial. A price never needs a fraction, so it never needs rounding until the code chooses one:

:::steps
```una include="steps/01-int/src/prices.una" title="src/prices.una" verified="check, run"
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

```text include="steps/01-int/expected/output.txt"
order: 8480 cents, or 84 units and 80 cents
15% off: 1272 cents off, 7208 to pay
refund: -13 and 95
no overflow: 9223372036854775808
```

Two lines need a closer look. The last one shows that `Int` has no 64-bit limit: the sum is exact. Many languages would print a large negative number there, or stop with an error.

The refund line shows how Una divides. Division and `mod` are **Euclidean**: the remainder is never negative, and the quotient is chosen to make that true. So `-1205 / 100` is `-13` and `-1205 mod 100` is `95`, since `-13 * 100 + 95` is `-1205`. Languages that round toward zero give `-12` and `-5` instead. For amounts that are not negative, both rules agree, and that is why the money functions of this chapter state that they take an amount that is not negative.

A division by a value that may be zero does not check. `una check` turns each division into a **proof obligation**, a fact the verifier must prove before the program may run: here, that the divisor is not zero. A literal such as `100` proves itself. For a divisor that comes from a parameter, the function must say why it cannot be zero, and [section 2.6](#s2-6) shows how.

> [!NOTE]
> `Int` arithmetic costs a little more than a machine's own, since a value may outgrow a machine word. Where a protocol, a file format or a hash needs a fixed width, use the fixed-width types of [section 2.5](#s2-5).

## 2.2 Conditions: `Bool`

A `Bool` is `true` or `false`. Comparisons give one: `==` and `!=` for equal and not equal, and `<`, `<=`, `>` and `>=` for order. `and`, `or` and `not` combine them. Store rules are full of conditions like these, so they make good functions:

:::steps
```una include="steps/02-bool/src/rules.una" title="src/rules.una" verified="check, run"
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
3. **`ships_free(12_000, domestic: false)`.** A call with two arguments names the second one, as in [chapter 1](/learn/hello/#s1-6).
4. **`not ships_free(2_500, domestic: true)`.** `not` turns `true` into `false` and back.
5. **`lamp == lamp` and `lamp != rug`.** Equality compares values, here two texts, character by character.
:::

`una run .` prints:

```text include="steps/02-bool/expected/output.txt"
12000 cents: free at home true, free abroad false
30000 cents: signature as a gift true, otherwise false
a small order pays shipping: true
same SKU: true, different SKUs: true
```

A `Bool` prints as `true` or `false`. Everything else about `Bool` is a rule of the checker:

- A condition must be a `Bool`. An `if` over an `Int`, such as `if percent then …`, does not check, and neither does `quantity and true`. A number is not true or false in Una, and neither is a text.
- `==` compares two values of the same type. Comparing an `Int` with a `Text` is a type error, never a quiet `false`.
- Comparisons do not chain. `1 <= percent <= 90` does not check: write `percent >= 1 and percent <= 90`, which says the same thing in a way no reader can misread.

A rule that the store applies in more than one place deserves a function that returns a `Bool`, named after the question it answers: `ships_free`, `needs_signature`, `on_sale`. The call then reads as the rule, `if ships_free(cents, domestic: domestic)`, and the rule lives in one place, with its own examples. When the free-shipping threshold changes, one line changes, and one example tells you whether the new rule is the one you meant.

## 2.3 Text

A `Text` is a sequence of characters, written between double quotes on one line. It may hold the characters of any language, since its encoding is UTF-8. A few characters need an escape inside the quotes: `\"` for a quote, `\\` for a backslash, `\n` for a new line, `\t` for a tab, and `\{` and `\}` for braces, since a brace starts an interpolation.

The prelude, the set of functions every module has without an import, gives text most of what a program needs. You call them with **method syntax**: `raw.trim` is the call `trim(raw)`, and `sku.starts_with(prefix: prefix)` is `starts_with(sku, prefix: prefix)`. A call that takes nothing but its receiver may leave out the parentheses, as `raw.trim` and `sku.len` do.

:::steps
```una include="steps/03-text/src/catalog.una" title="src/catalog.una" verified="check, run"
module catalog

--- The SKU as labels print it: without the spaces around it, in capital letters.
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

1. **`raw.trim.to_upper`.** Two calls in a row: `trim` removes the spaces at both ends, and `to_upper` writes the letters in capitals. Each returns a new text; `raw` itself does not change.
2. **`sku.len`.** The number of characters. `"Café table, oak"` has 15, since `é` counts as one character, not as the two bytes UTF-8 needs for it.
3. **`let prefix = "LAMP-"`, then `starts_with(prefix: prefix)`.** A text literal cannot appear inside the braces of another text, so the prefix gets a name first.
4. **`contains_text(part: wood)` and `replace(pattern: wood, by: walnut)`.** A search, and a replacement of every occurrence.
5. **`"a quote \" and a brace \{ in a text"`.** Two escapes.
:::

`una run .` prints:

```text include="steps/03-text/expected/output.txt"
[  lamp-01 ] becomes [LAMP-01], 7 characters
a lamp: true
15 characters, oak: true
Café table, walnut
a quote " and a brace { in a text
```

| Function | Gives | Notes |
| --- | --- | --- |
| `t.len` | `Int` | the number of characters |
| `t.trim`, `t.trim_start`, `t.trim_end` | `Text` | without the spaces at both ends, or one end |
| `t.to_upper`, `t.to_lower` | `Text` | changes the letters `a` to `z` and `A` to `Z` only |
| `t.starts_with(prefix: p)`, `t.ends_with(suffix: s)` | `Bool` | |
| `t.contains_text(part: p)` | `Bool` | |
| `t.replace(pattern: p, by: r)` | `Text` | every occurrence; `p` must not be empty |
| `t.slice(start: a, end: b)` | `Text` | the characters from position `a` up to, not including, `b` |
| `t.split(on: s)` | a list of `Text` | `s` must not be empty; lists are the subject of [chapter 5](/learn/collections/) |

`to_upper` changes only the 26 letters of the English alphabet, so `é` stays `é`: the result is the same on every machine, whatever its language settings. Two texts are joined with an interpolation, `"{first}{second}"`. Una has no `+` for text, and [Common mistakes](#s2-8) shows what the checker says to it.

**Cutting a text, and the proof it takes.** A label has room for 24 characters, so a longer name must be cut. `slice` cuts, and it **requires** its positions to lie inside the text: a requirement that the verifier proves at every call, before the program runs.

:::steps
```una include="steps/04-slice/src/names.una" title="src/names.una" verified="check, run"
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

1. **`if name.len > 24 then … else name`.** A choice between two values: the cut name when it is too long, the name itself when it fits. [Chapter 3](/learn/functions/#s3-3) covers `if`.
2. **`name.slice(start: 0, end: 24)`.** The first 24 characters. It needs `24 <= name.len`, and the `if` above it says that `name.len > 24`, so the verifier proves it.
:::

```text include="steps/04-slice/expected/output.txt"
[Desk lamp, brass]
[Wool rug, 120 by 180 cm,]
```

Without the `if`, nothing says the name is long enough:

```diff include="steps/04-slice..steps/05-unguarded:src/names.una" title="src/names.una" context="0"
--- a/src/names.una
+++ b/src/names.una
@@ -4 +4 @@
-pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name
+pub fit_name(name: Text) -> Text = name.slice(start: 0, end: 24)
```

```text include="steps/05-unguarded/expected/rendered.txt#L1,L10,L16"
[U5001] Error: precondition `0 <= 0 and 0 <= 24 and 24 <= name.len` of this call is refuted
   │ Help 2: repair 2: add a guard (`if` or a `when` arm) that handles the values where `0 <= 0 and 0 <= 24 and 24 <= name.len` does not hold
   │ Note 2: counterexample: name = Text#0, name.len = 0
```

The **counterexample** is the case that breaks the requirement: an empty name, whose length is 0. A text in a counterexample is shown by a placeholder, `Text#0`, followed by the facts about it that matter. Where another language would fail at run time on a short name, or cut it silently, Una refuses the program and names the input that would break it.

## 2.4 Names: `let` and `let edit`

`let` gives a name to a value, and the name holds that value until the end of its block. A name cannot be bound twice in one block, and it cannot be assigned. When a value must change, as a running total does, you declare the name with `let edit`, and assign it new values with `=`:

:::steps
```una include="steps/06-let/src/till.una" title="src/till.una" verified="check, run"
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

```text include="steps/06-let/expected/output.txt"
2 items, 3980 cents
3 items, 8480 cents
LAMP-01, LAMP-01, RUG-07
```

A name declared with `let` cannot change, and the checker holds you to it. An assignment to it is a type error, U2019, whose message tells you to declare it `let edit`. Binding the same name a second time in one block, `let total = 3` and then `let total = 4`, is a different error: Una has no shadowing within a block, so a name means one thing from its line to the end of its block.

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

> [!NOTE]
> `receipt = "{receipt}, …"` does not copy the whole text each time. When an assignment adds to the end of a text that nothing else holds, the text grows in place, so building a long text this way takes time in proportion to its length.

## 2.5 Fixed-width integers

`Int` fits nearly every number in a store's code. Some places need an exact width instead: a byte in a protocol, a field of a file format, a count that a device reads as one byte. For these, Una has the unsigned types `U8`, `U16`, `U32` and `U64`, from 0 up to 255, 65535 and so on, and the signed types `I8`, `I16`, `I32` and `I64`, which also hold negative values. Each is its own type, distinct from `Int` and from the others.

A fixed-width value never wraps around. Every `+`, `-`, `*`, `/` and `mod` on one is a proof obligation: the verifier must prove that the exact result fits the type.

:::steps
```una include="steps/07-fixed-width/src/printer.una" title="src/printer.una" verified="check, run"
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

1. **`pub copies(facings: U8) -> U8`.** The label printer reads the number of copies as one byte, so the result is a `U8`.
2. **`requires facings < 255`.** A **precondition**: a fact every caller must make true. It makes `facings + 1` fit in a `U8`, so the verifier proves the addition, and it proves the precondition at each call. [Chapter 7](/learn/contracts/) covers contracts in full.
3. **`let lamps: U8 = 4`.** A literal takes the type its context expects, here `U8`. A literal that does not fit, such as `300`, does not check.
4. **`lamp_labels.to_int() + mug_labels.to_int()`.** Two `U8` values turned into `Int` before they are added. Every `U8` fits in an `Int`, so `to_int()` always succeeds; the sum is an `Int` and cannot overflow.
5. **`roll.saturating_sub(by: 1_200)`.** Subtraction that stops at the bottom of the range, 0, instead of going below it. Methods such as this one say in their names what happens at the ends of the range.
:::

`una run .` prints:

```text include="steps/07-fixed-width/expected/output.txt"
5 and 13 labels
18 labels in all
0 left on a roll of 1000 after 1200
```

Remove the precondition, and the verifier finds the one value that breaks the addition:

```diff include="steps/07-fixed-width..steps/08-overflow:src/printer.una" title="src/printer.una" context="0"
--- a/src/printer.una
+++ b/src/printer.una
@@ -5,4 +5 @@
-pub copies(facings: U8) -> U8
-  requires facings < 255
-=
-  facings + 1
+pub copies(facings: U8) -> U8 = facings + 1
```

```text include="steps/08-overflow/expected/rendered.txt#L1,L8,L10,L12,L16"
[U5001] Error: overflow obligation `facings + 1 in 0..255` is refuted
   │ Help 1: repair 1: guard the operation with `if facings.to_int() + 1 in 0..255`
   │ Help 2: repair 2: give the values a wider type, converting them explicitly
   │ Help 3: repair 3: if wrapping or saturating is meant, use `wrapping_add`, `saturating_add` or their siblings
   │ Note 2: counterexample: facings = 255
```

The repairs list the three honest choices: check the range first, use a wider type, or say that wrapping or saturating is what you mean. Each makes the behavior at the edge of the range visible in the code.

Conversions are explicit in both directions. `to_int()` widens and never fails. `to_u8()`, `to_u16()` and the others narrow, and each narrowing is a proof obligation that the value fits. Operands of two different integer types, such as a `U8` and an `Int`, do not mix: convert one of them first.

## 2.6 Day-to-day: shelf labels

Every product on a shelf has a label: its SKU, its name, and its price. The labels change every week, as prices change and sales start and end, so the store prints them from its catalog. The data is messy in the usual ways. SKUs arrive with stray spaces and in small letters, some names are longer than the label, and a product sold by weight must show its price per kilogram as well.

The program follows the data. Each fix to a value is a small function with a doc comment and an example: clean the SKU, fit the name, write the price. Each kind of label is a function built from those. `main` prints the labels of four products and counts the copies to print.

**Cleaning the values.** Three functions turn raw values into what a label prints:

```una include="day-to-day/src/labels.una#clean_sku..money" title="day-to-day/src/labels.una" caption="clean, fit, format"
--- The SKU as labels print it: without the spaces around it, in capital letters.
pub clean_sku(raw: Text) -> Text = raw.trim.to_upper

--- A product name cut to the 24 characters a label has room for.
pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name

--- Cents as an amount with two decimals, for an amount that is not negative: 1990 is "19.90".
pub money(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"
```

`money` writes the two digits of the cents one by one, as in the last exercise of [chapter 1](/learn/hello/#s1-10), so 1205 is `12.05` and never `12.5`. Its doc comment states that it is for amounts that are not negative, since a refund would need the Euclidean rule of [section 2.1](#s2-1) in mind.

**Prices.** A sale price and a price per kilogram, each rounded down to a whole cent:

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

**The labels.** Three kinds of label, each a line of text:

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

**Copies, and the run.** `copies` gives the count the printer reads, as in [section 2.5](#s2-5). `main` prints each label and adds its copies to a running total, which is a `let edit` name:

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

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/labels.una" title="day-to-day/src/labels.una" caption="the whole program" verified="check, run, test"
module labels

-- Shelf labels: one line for each product, as the label printer prints it, and how many
-- copies of the labels to print.

--- The SKU as labels print it: without the spaces around it, in capital letters.
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

`una run .` prints the labels shown under "What you'll build". The rug's name is cut to 24 characters, which ends it on a comma: the rule is simple, and the label shows it. The SKUs come out clean, the coffee shows 25.00 per kilogram for a 500 g pack at 12.50, and the copies add up to 23: 5, 3, 13 and 2.

> [!TIP]
> When a function divides by a parameter or cuts a text at a computed position, write the precondition first, then the body. The verifier tells you at once whether the precondition is enough, and each caller learns what it must provide.

## 2.7 Testing it

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

Each one covers a rule that the sample run alone would hide:

- "a long name is cut to 24 characters" checks the length of the result, `result.len`, not its text: the fact that matters is the width.
- "an amount keeps the zero of its cents" covers 1205, whose cents are under ten, a case none of the four products reaches.
- "a discount rounds down to a whole cent" fixes the rounding: 1999 cents at 15 percent off is 1699.15, and the store charges 1699.
- "a discount over 90 percent is not a sale" checks the store rule at a value outside it.
- "a shelf with four facings gets five labels" checks a `U8` result against a literal, which takes the type `U8` from the other side of `==`.

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

No example tests what happens when `grams` is 0, and none can: an example is code, and `una check .` proves the precondition of every call in it as in any other code. A call `per_kilo(1250, grams: 0)` in an example is refuted before the example runs, which is the strongest test of that case there is.

## 2.8 Common mistakes

Each mistake below is a small change to `day-to-day/src/labels.una`, followed by what `una check .` reports.

:::mistake
**1. Joining texts with `+` (U2001).** Building the weight label with `+`, as many languages allow:

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

*Why:* `+` adds numbers. A text is not a number, and Una converts neither side. una also reports that the function no longer returns a `Text`, since `+` gives an `Int`.

*Fix:* join texts with an interpolation, `"{regular_label(sku, name: name, cents: cents)} ({money(kilo)} per kg)"`. See [U2001](/docs/errors/U2001/).
:::

:::mistake
**2. Assigning a plain `let` (U2019).** Declaring the running total with `let`:

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

*Why:* a name declared with `let` holds one value. una reports each of the four assignments.

*Fix:* `let edit printed = 0`, as the message says. See [U2019](/docs/errors/U2019/).
:::

:::mistake
**3. Dividing by a parameter (U5001).** Removing the precondition of `per_kilo`, which canonical form then writes on one line:

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

*Why:* `grams` may be 0, and a division by zero is never allowed to run. The counterexample is that case.

*Fix:* put back `requires grams > 0`, so that each caller proves it, or guard the division as the `Help` line says. See [U5001](/docs/errors/U5001/).
:::

:::mistake
**4. A text inside an interpolation (U0006).** Printing a label through an interpolation, with its arguments written in place:

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

*Why:* the braces of an interpolation cannot hold a text literal. una reports each of the two.

*Fix:* print the label itself, `@console.print(label(…))`, or name the texts with `let` first, as the message says. See [U0006](/docs/errors/U0006/).
:::

:::mistake
**5. A literal out of range (U2022).** Giving a shelf 300 facings:

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

*Why:* the parameter of `copies` is a `U8`, so the literal is a `U8`, and 300 does not fit.

*Fix:* a value that fits, or a wider type for the parameter if the printer accepts one. See [U2022](/docs/errors/U2022/).
:::

:::mistake
**6. A number as a condition (U2001).** Testing the discount itself, as if a number could be true:

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

*Why:* a condition must be a `Bool`. An `Int` is never true or false.

*Fix:* say the rule: `if on_sale(percent)`, or `if percent > 0`. See [U2001](/docs/errors/U2001/).
:::

## 2.9 For agents

:::agents
`una --json check .` reports each diagnostic with its `code`, `message` and `primary` span. A refuted obligation, U5001, also carries a `counterexample` with one binding for each value, and repairs ranked from the guard to the escape. The repairs of U2001, U2019 and U2022 are descriptions, since the right type or value is the author's choice. The compact rule: *money is `Int` cents; join text with interpolation, never `+`; a name that changes is `let edit`; a division by a parameter or a `slice` at computed positions needs a `requires` or a guard; fixed-width arithmetic needs a proof that it fits.*
:::

## 2.10 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added at the end, and a stub of the function to write, whose body is a placeholder value. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

::::exercise
**Exercise 1: sales tax.** Write `with_tax(cents, percent)`, the price with a sales tax of `percent` added, rounded to the nearest cent, with half a cent rounding up. The start package ends with:

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
*Hint:* `cents * (100 + percent)` is the price in hundredths of a cent. Adding half of 100 before dividing by 100 rounds to the nearest cent.
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

::::exercise
**Exercise 2: the price of one unit in a pack.** A pack of olive soap holds six bars. Write `pack_label(sku, name, cents, units)`, the regular label followed by the price of one unit, and print the label of the soap in `main`, with three copies. The start package ends with:

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

::::exercise
**Exercise 3: labels left on the roll.** The label printer counts the labels left on its roll as a `U16`. Write `labels_left(roll, printed)`, which subtracts what was printed, and gives 0 when more was printed than the roll held. The start package ends with:

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

Check your answer with `una test .`.

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

## 2.11 Recap

:::recap
- `Int` has no bound, so its arithmetic is exact. Keep money in whole cents.
- `/` and `mod` are Euclidean: the remainder is never negative. A division by a value that may be zero does not check.
- A condition is a `Bool`. Compare with `==`, `!=`, `<` and the others, and combine with `and`, `or` and `not`; comparisons do not chain.
- Join texts with interpolation, never `+`. Bind a text literal with `let` before you use it inside braces.
- `slice` and other functions state what they require, and the verifier proves it at each call: guard the call with an `if`, or pass the requirement on with `requires`.
- Prefer `let`. Use `let edit` for a value that accumulates; a name is bound once per block.
- Use a fixed-width type only where a width is required. Its arithmetic is proved to fit, and conversions are explicit.
:::

## 2.12 Reference

:::reference
- Construct pages: [literals and operators](/docs/language/lexical-structure/), [built-in types](/docs/language/types/), [`let` and `if`](/docs/language/control-flow/), [`let edit`](/docs/language/control-flow/let-edit/), [`requires`](/docs/language/functions/requires/)
- Guides: [fixed-width integers](/docs/guides/fixed-width-integers/), [work with text](/docs/guides/text/)
- Standard library: [the prelude](/docs/std/) (`Int`, `Bool`, `Text`, `trim`, `starts_with`), [text](/docs/std/text/) (`slice`, `replace`, `contains_text`, `to_upper`, `split`), [the built-in methods](/docs/std/builtin/) (`.len`, `to_int`, `to_u8`, `saturating_sub`)
- Diagnostics: [U0006](/docs/errors/U0006/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2019](/docs/errors/U2019/), [U2022](/docs/errors/U2022/), [U5001](/docs/errors/U5001/)
- Specification: [lexical structure](/docs/spec/01-lexical-structure/), [types](/docs/spec/03-types/), [the standard library](/docs/spec/14-standard-library/), [the memory model](/docs/spec/17-memory-model/), [fixed-width integers](/docs/spec/18-fixed-width-integers/), [text](/docs/spec/22-text/)
:::
