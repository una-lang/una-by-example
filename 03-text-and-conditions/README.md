---
learn: "3"
title: Text and conditions
editions: ["0.2"]
codes: [U0006, U0101, U2001, U2022, U5001]
time: 30
builds: The shelf labels of a store, with prices, sale prices, prices per kilogram and the number of copies to print
prerequisites: ["1", "2"]
template: 2
nav: ["Text", "Working with text", "Conditions: Bool", "Choosing a value: if", "Day-to-day: shelf labels", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 3 Text and conditions

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

## 3.1 Text


### What a text is

A **text** is a sequence of characters: letters, digits, spaces, punctuation. A SKU, a product name and a line of a label are texts. Una's type is `Text`, and you write a text between double quotes on one line, as in [chapter 2](/learn/numbers/#s2-1).

A text may hold the characters of any language, `é` and `ü` included, since it is **Unicode**: the standard that numbers every character of every writing system. Una stores a text in **UTF-8**, the usual encoding of Unicode, which uses one **byte**, a unit of storage of 8 bits, for an English letter and two to four for others. Positions and lengths count characters, never bytes.

### Why text needs care

Texts come from people and from other systems, and they are messy. A SKU typed at the till arrives as `"lamp-01 "`, with small letters and a stray space, and compares unequal to the `"LAMP-01"` of the catalog:

```text include="steps/01-text-forms/expected/output.txt#L1"
[lamp-01 ] and [LAMP-01] are equal: false
```

A product name may be longer than its label. A program must clean, compare and cut text, and a cut at a position past the end of a text has no answer. Una gives you the functions to clean and search, and the verifier proves that every cut lies inside its text.

### How to write a text

#### Quotes and escapes

A few characters need an **escape**, a backslash and one more character, inside the quotes:

| Write | For |
| --- | --- |
| `\"` | a double quote |
| `\\` | a backslash |
| `\{` and `\}` | a brace, since a brace starts an interpolation |
| `\n` | a new line |
| `\t` | a tab |
| `\u{e9}` | the character with that Unicode number in hexadecimal: `é` |

#### Joining texts: interpolation

Una joins texts with an **interpolation**, as in [chapter 2](/learn/numbers/#putting-values-into-a-text): `"{sku}-{size}"` is the SKU, a dash and the size. Una has no `+` for text: `+` adds numbers, and [Common mistakes](#s3-7) shows what the checker says to it. A text literal cannot go inside the braces of another text, so name it with `let` first, as `size` is named here.

The step writes each form:

```una include="steps/01-text-forms/src/texts.una#L1-L16" title="steps/01-text-forms/src/texts.una"
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

```text include="steps/01-text-forms/expected/output.txt#L2-L6"
a quote ", a backslash \ and braces { }
before a tab:	after it
Café table
LAMP-01-XL
[] has 0 characters, [LAMP-01] has 7
```

`.len` gives the length of a text, its number of characters: `""`, the **empty text**, has 0.

### How text behaves

- **A text never changes.** `trim`, `to_upper` and `replace` return a new text; the one you passed stays as it was.
- **Lengths and positions count characters.** `"Café"` has 4, whatever bytes UTF-8 uses. Positions run from 0 to `len - 1`.
- **Equality is exact.** `==` compares character by character: `"lamp-01 "` and `"LAMP-01"` differ in case and in the space.
- **Case changes are ASCII only.** `to_upper` and `to_lower` change `a` to `z` and `A` to `Z`, nothing else, so a text keeps its length.
- **The empty text is a text.** `""` has length 0, and `trim` of a text of spaces gives it.
- **Cuts are proved.** `slice` and `replace` state what they need, and a call the verifier cannot prove does not check.

### Check yourself: text

The step `texts` ends with two more lines:

```una include="steps/01-text-forms/src/texts.una#L17-L20" title="steps/01-text-forms/src/texts.una"
  let padded = "  oak desk "
  @console.print("{padded.trim.len}")
  let cafe = "Café"
  @console.print(cafe.to_upper)
```

What do they print?

:::answer Show the answer
```text include="steps/01-text-forms/expected/output.txt#L7-L8"
8
CAFé
```

`trim` removes the two spaces at the front and the one at the end, leaving `oak desk`, 8 characters. `to_upper` changes only the letters `a` to `z`, so `é` stays as it is.
:::

## 3.2 Working with text: the prelude's functions and method calls

### The prelude's text functions

The **prelude** is the set of types and functions every module has without an import. It gives text most of what a program needs. You call its functions with **method syntax**: `raw.trim` is the call `trim(raw)`, and `sku.starts_with(prefix: prefix)` is `starts_with(sku, prefix: prefix)`. The value before the dot becomes the first argument. `.len` and the prelude's functions that take nothing but that value may leave out the parentheses, as `raw.trim` and `sku.len` do. The methods of the fixed-width integers in [section 2.3](/learn/numbers/#s2-3) always keep theirs.

:::steps
```una include="steps/02-catalog/src/catalog.una" title="src/catalog.una" verified="check, run"
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
2. **`sku.len`.** The number of characters, as Unicode counts them (it calls them scalar values). `"Café table, oak"` has 15: the `é` here is one, not the two bytes UTF-8 needs for it.
3. **`let prefix = "LAMP-"`, then `starts_with(prefix: prefix)`.** A text literal cannot appear inside the braces of another text, so the prefix gets a name first.
4. **`contains_text(part: wood)` and `replace(pattern: wood, by: walnut)`.** A search, and a replacement of every occurrence.
5. **`"a quote \" and a brace \{ in a text"`.** Two escapes.
:::

`una run .` prints:

```text include="steps/02-catalog/expected/output.txt"
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
| `t.split(on: s)` | a list of `Text` | `s` must not be empty; a **list** is a sequence of values, the subject of [chapter 10](/learn/collections/) |

`to_upper` changes only the 26 letters of the English alphabet, so `é` stays `é`: the result is the same on every machine, whatever its language settings.

> [!NOTE]
> `len`, `trim`, `starts_with` and `==` work in every edition. `trim_start`, `trim_end`, `to_upper`, `to_lower`, `ends_with`, `contains_text`, `replace`, `slice` and `split` are the text functions of edition `0.2` and later; in a package of edition `0.1` their names are ordinary names.

### Cutting a text, and the proof it takes

A label has room for 24 characters, so a longer name must be cut. Positions in a text count characters from 0, so the first 24 characters are those at positions 0 to 23. `slice` cuts, and it **requires** its positions to lie inside the text: `0 <= start`, `start <= end` and `end <= t.len`. A requirement of this kind is a **precondition**, and the verifier proves it at every call, before the program runs.

:::steps
```una include="steps/03-names/src/names.una" title="src/names.una" verified="check, run"
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

1. **`if name.len > 24 then … else name`.** An `if` chooses between two values: the value after `then` when the condition holds, and the value after `else` when it does not. Here, the cut name when it is too long, and the name itself when it fits. [Chapter 3](#s3-4) covers `if`.
2. **`name.slice(start: 0, end: 24)`.** The first 24 characters. It needs `24 <= name.len`. In the `then` branch, the verifier knows that `name.len > 24`, so it proves it.
:::

```text include="steps/03-names/expected/output.txt"
[Desk lamp, brass]
[Wool rug, 120 by 180 cm,]
```

### When the proof fails: a counterexample

Without the `if`, nothing says the name is long enough:

```diff include="steps/03-names..steps/04-unguarded:src/names.una" title="src/names.una" context="0"
--- a/src/names.una
+++ b/src/names.una
@@ -4 +4 @@
-pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name
+pub fit_name(name: Text) -> Text = name.slice(start: 0, end: 24)
```

```text include="steps/04-unguarded/expected/rendered.txt#L1,L10,L16"
[U5001] Error: precondition `0 <= 0 and 0 <= 24 and 24 <= name.len` of this call is refuted
   │ Help 2: repair 2: add a guard (`if` or a `when` arm) that handles the values where `0 <= 0 and 0 <= 24 and 24 <= name.len` does not hold
   │ Note 2: counterexample: name = Text#0, name.len = 0
```

Read it in order. The first line names the obligation: the precondition of `slice`, with the call's arguments in place of `start` and `end`. The `Help` line proposes a guard, which is what the `if` was. The **counterexample** is the case that breaks the requirement: an empty name, whose length is 0. A text in a counterexample is shown by a placeholder, `Text#0`, followed by the facts about it that matter. Where another language would fail at run time on a short name, or cut it silently, Una refuses the program and names the input that would break it.

### Method syntax

A call can also be written with its first argument in front, followed by a dot: `1_990.half` is `half(1_990)`, and `1_990.line_total(units: 3)` is `line_total(1_990, units: 3)`. This is **method syntax**, and [chapter 3](#s3-1) used it for the text functions of the **prelude**, the functions every module has without asking, as in `raw.trim`. A call of one argument may also drop its empty parentheses: `1_990.half`.

```una include="steps/05-calls/src/calls.una#L23" title="steps/05-calls/src/calls.una"
  @console.print("method syntax: {1_990.half}, {1_990.line_total(units: 3)}")
```

```text include="steps/05-calls/expected/output.txt#L4"
method syntax: 995, 5970
```

Both forms are the same call, and the checker treats them alike. Use method syntax where it reads as a chain of steps on one value, as `raw.trim.to_upper` does, and the plain form elsewhere. A value can also have **fields**, named parts of a record, such as the city of an address ([chapter 4](/learn/kinds/#s4-1)); when the value has a field of the same name, the dot reads the field instead.

## 3.3 Conditions: `Bool`


### What a condition is

A **condition** is a question whose answer is yes or no: is the order over 100.00? Is the address in the country? Una's type for such answers is `Bool`, and it has exactly two values, `true` and `false`. A comparison, such as `cents >= 10_000`, gives a `Bool`.

Conditions are how a program decides. A `Bool` says whether an order ships for free, and an `if` ([chapter 3](#s3-4)) picks one of two values depending on it: `if free then 0 else 495` is 0 when `free` is `true`, and 495 otherwise.

### Why `Bool` is its own type

In some languages a number can stand for a yes or no: 0 means no, and anything else means yes. So a slip, such as writing the amount where the rule belongs, still runs, and quietly answers the wrong question. In Una a condition must be a `Bool`. Join an amount to a condition by mistake (`>=` means "at least", and `and` joins two conditions, as the next subsection shows):

```diff include="steps/06-rules..steps/07-not-a-condition:src/rules.una" title="src/rules.una" context="0"
--- a/src/rules.una
+++ b/src/rules.una
@@ -4 +4 @@
-pub ships_free(cents: Int, domestic: Bool) -> Bool = cents >= 10_000 and domestic
+pub ships_free(cents: Int, domestic: Bool) -> Bool = cents and domestic
```

```text include="steps/07-not-a-condition/expected/rendered.txt#L1"
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

`==` and `!=` work on two values of any one type. `<` and the other orderings work on `Int`, on the fixed-width types of [section 2.3](/learn/numbers/#s2-3), and on `Text`, which is ordered character by character.

#### `and`, `or` and `not`

- `a and b` is `true` when both are.
- `a or b` is `true` when at least one is.
- `not a` turns `true` into `false` and back.

#### The order of operations

Arithmetic comes first, then comparisons, then `not`, then `and`, then `or`. So `not units > 5` means `not (units > 5)`, and `a or b and c` means `a or (b and c)`. Parentheses make any order explicit, and a reader thanks you for them in a mixed rule.

The step tries each form:

```una include="steps/08-conditions/src/stock.una#L1-L16" title="steps/08-conditions/src/stock.una"
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

```text include="steps/08-conditions/expected/output.txt#L1-L4"
true false false true false true
true false true
false true false
false true true
```

`in_stock` is a function that returns a `Bool`: `in_stock(0)` is `false`, and `not in_stock(0)` is `true`. `"LAMP-01" < "RUG-07"` is `true`, since `L` comes before `R`.

### Store rules that return a `Bool`

Store rules are full of conditions like these, so they make good functions:

:::steps
```una include="steps/06-rules/src/rules.una" title="src/rules.una" verified="check, run"
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
3. **`ships_free(12_000, domestic: false)`.** A call with two arguments names the second one, as in [chapter 1](/learn/hello/#parameters-and-labels-at-the-call).
4. **`not ships_free(2_500, domestic: true)`.** `not` turns `true` into `false` and back.
5. **`lamp == lamp` and `lamp != rug`.** Equality compares values, here two texts, character by character.
:::

`una run .` prints:

```text include="steps/06-rules/expected/output.txt"
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

```diff include="steps/06-rules..steps/09-chained:src/rules.una" title="src/rules.una" context="0"
--- a/src/rules.una
+++ b/src/rules.una
@@ -7,0 +8,3 @@
+
+--- Whether a discount is one the store runs: from 1 to 90 percent off.
+pub fair_discount(percent: Int) -> Bool = 1 <= percent <= 90
```

```text include="steps/09-chained/expected/rendered.txt#L1"
[U0101] Error: comparisons cannot be chained; join them with `and`, as in `a < b and b < c`
```

The message gives the repair: `percent >= 1 and percent <= 90`, which says the same thing in a way no reader can misread.

### One function per rule

A rule that the store applies in more than one place deserves a function that returns a `Bool`, named after the question it answers: `ships_free`, `needs_signature`, `on_sale`. The call then reads as the rule, `if ships_free(cents, domestic: domestic)`, and the rule lives in one place, with its own examples. When the free-shipping threshold changes, one line changes, and one example tells you whether the new rule is the one you meant.

### Check yourself: conditions

The step `stock` ends with two conditions, where `units` is 3 and `gift` is `true`:

```una include="steps/08-conditions/src/stock.una#L17-L19" title="steps/08-conditions/src/stock.una"
  let gift = true
  @console.print("{not units > 5}")
  @console.print("{not gift or units > 5}")
```

What do they print?

:::answer Show the answer
```text include="steps/08-conditions/expected/output.txt#L5-L6"
true
false
```

`not` comes after comparisons, so `not units > 5` is `not (units > 5)`: 3 > 5 is `false`, and `not false` is `true`. In the second line, `not` applies to `gift` alone, before `or`: `not gift` is `false`, `units > 5` is `false`, and `false or false` is `false`.
:::

## 3.4 Choosing between two values: `if`


### What `if` is

`if` chooses between two values by a condition. Think of a sign at the till: "orders of 100.00 or more ship free; otherwise shipping is 4.90". The clerk checks one fact, and the answer is one of two prices. `if` writes that rule: `if goods >= 10_000 then 0 else 490`.

Three words name its parts:

- The **condition** is the expression after `if`: a `Bool`, `true` or `false` ([chapter 3](#s3-3)).
- A **branch** is one of the possible answers: the one after `then` when the condition is `true`, and the one after `else` when it is `false`.
- Only the branch the condition picks runs. The other is skipped.

In Una, `if` is an expression: like `2 + 3` or a call, it gives a value. You can put it wherever a value goes: as a function's body, after `let`, as an argument, or inside interpolation braces.

### Why a program chooses

A function without a choice answers every input the same way. Here is a product page that says how many units are left, with one sentence for every case:

```una include="steps/10-no-if/src/shelf.una" title="steps/10-no-if/src/shelf.una" verified="check, run"
module shelf

--- What a product page says about the stock of a product. One sentence for every case.
availability(on_hand: Int) -> Text = "only {on_hand} units left"

--- Prints what the product page says for four stock levels.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(availability(0))
  @console.print(availability(1))
  @console.print(availability(3))
  @console.print(availability(40))
```

`una run .` prints:

```text include="steps/10-no-if/expected/output.txt"
only 0 units left
only 1 units left
only 3 units left
only 40 units left
```

Only one line in four is right. "Only 0 units left" should say the product is out of stock, "only 1 units left" is bad English, and "only 40 units left" makes a full shelf sound scarce. The sentence depends on the number, and a single expression cannot say so. `if` can.

### How to write `if`

`if` has three forms: on one line, over several lines, and without `else`. The step for this part has a small function for each, and `main` prints one line for each function.

#### On one line: `if … then … else …`

`if condition then value else value`, all on one line. Both values are expressions:

```una include="steps/11-if-forms/src/choices.una#weight_class" title="steps/11-if-forms/src/choices.una"
--- Whether a parcel counts as heavy: an `if` on one line.
weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy" else "light"
```

```text include="steps/11-if-forms/expected/output.txt#L1"
heavy, light
```

2300 g is above 2000, so the condition is `true` and the result is `"heavy"`. 800 g is not, and the result is `"light"`.

#### More than two cases: `else if`

An `else` may hold another `if`. The conditions are tried in order, and the first one that holds gives the value. The last `else` catches every case no condition took:

```una include="steps/11-if-forms/src/choices.una#zone_name" title="steps/11-if-forms/src/choices.una"
--- The name of a shipping zone: an `else if` chain, still on one line.
zone_name(zone: Int) -> Text = if zone == 1 then "home" else if zone == 2 then "neighbors" else "world"
```

```text include="steps/11-if-forms/expected/output.txt#L2"
home, neighbors, world
```

#### Over several lines: a block in each branch

When a branch needs a few lines, write the `if` over several lines. The condition goes on the `if` line, with no `then`. Each branch is a block, indented by two spaces under its `if`, `else if` or `else`, and its value is its last line, as in a function's body ([section 6.2](/learn/functions/#s6-2)):

```una include="steps/11-if-forms/src/choices.una#box" title="steps/11-if-forms/src/choices.una"
--- The box a parcel needs: an `if` over several lines, with a block in each branch.
box(grams: Int) -> Text
=
  if grams <= 500
    "envelope"
  else if grams <= 5_000
    let liters = grams / 250
    "box of {liters} liters"
  else
    "crate"
```

```text include="steps/11-if-forms/expected/output.txt#L3"
envelope, box of 8 liters, crate
```

The second branch names `liters` before its last line. A name bound inside a branch exists only in that branch.

#### Inside a larger expression

An `if` can be one part of a larger expression. It then goes in parentheses, which are required: without them the line does not parse (U0101), since the parser must see where the `if` ends:

```una include="steps/11-if-forms/src/choices.una#handling" title="steps/11-if-forms/src/choices.una"
--- The handling fee of an order: an `if` in parentheses, as one part of a sum.
handling(goods: Int) -> Int = 190 + (if goods >= 10_000 then 0 else 300)
```

```text include="steps/11-if-forms/expected/output.txt#L4"
490, 190
```

An order of 4500 cents pays 190 plus 300. An order of 12000 cents pays 190 plus 0.

#### Without `else`: a statement

In edition 0.2 and later, the edition of every package in this book, an `if` over several lines may leave out `else`. (In edition 0.1 every `if` has an `else`.) It then gives no value: it is a statement, whose lines run only when the condition holds. It is useful with a binding declared `let edit` ([chapter 2](/learn/numbers/#s2-1)), which its lines may assign:

```una include="steps/11-if-forms/src/choices.una#packing_note" title="steps/11-if-forms/src/choices.una"
--- A note for the packing slip: an `if` without `else`, which only runs its lines when the
--- condition holds.
packing_note(units: Int) -> Text
=
  let edit note = "standard"
  if units > 10
    note = "bulk, use a pallet"
  note
```

```text include="steps/11-if-forms/expected/output.txt#L5"
standard, bulk, use a pallet
```

For 4 units the condition is `false`, nothing happens, and `note` keeps `"standard"`. For 24 units the assignment runs. Loops in [chapter 9](/learn/loops/#s9-1) use this form at each turn. When you only need a value, prefer the forms with `else`: `let note = if units > 10 then "bulk, use a pallet" else "standard"` says the same in one line, with no binding to edit.

### Stock messages with `if`

Back to the product page. The module `stock` gives each stock level its own sentence:

:::steps
```una include="steps/12-if/src/stock.una" title="steps/12-if/src/stock.una" verified="check, run"
module stock

--- "unit" or "units", whichever goes with `count`.
pub units_word(count: Int) -> Text = if count == 1 then "unit" else "units"

--- What a product page says about the stock of a product.
pub availability(on_hand: Int) -> Text
=
  if on_hand <= 0
    "out of stock"
  else if on_hand < 5
    let word = units_word(on_hand)
    "only {on_hand} {word} left"
  else
    "in stock"

--- Prints what the product page says for four stock levels.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(availability(0))
  @console.print(availability(1))
  @console.print(availability(3))
  @console.print(availability(40))
```

1. **`if count == 1 then "unit" else "units"`.** The one-line form, as a whole function body. Both branches are `Text`.
2. **`if on_hand <= 0`, `else if on_hand < 5`, `else`.** The form over several lines. The conditions are tried in order, and the first that holds gives the value.
3. **`let word = units_word(on_hand)` inside a branch.** A branch is a block, so it may name values before its last line. `word` exists only inside that branch.
4. **`"only {on_hand} {word} left"`.** The branch's last line, and so its value.
:::

`una run .` prints:

```text include="steps/12-if/expected/output.txt"
out of stock
only 1 unit left
only 3 units left
in stock
```

Compare with the page without `if`. Each stock level now gets the sentence that fits it, and the rule for each case is written once, where a reader looks for it.

### Check yourself: `if`

`wrap_fee` prices gift wrapping:

```una include="steps/11-if-forms/src/choices.una#wrap_fee" title="steps/11-if-forms/src/choices.una"
--- The gift-wrapping fee of an order: nothing without a gift, 150 cents a unit, and 500 at most.
wrap_fee(units: Int, gift: Bool) -> Int = if not gift then 0 else if units > 3 then 500 else 150 * units
```

`main` prints `wrap_fee(2, gift: true)`, `wrap_fee(5, gift: true)` and `wrap_fee(5, gift: false)`. Predict the three values.

:::answer Show the answer
```text include="steps/11-if-forms/expected/output.txt#L7"
300, 500, 0
```

2 units as a gift take the last branch, 150 × 2 = 300. 5 units as a gift pass the second condition, `units > 3`, and pay the cap of 500. Without a gift, the first condition holds, and the other branches never run.
:::

## 3.5 Day-to-day: shelf labels

### What the program must do

Every product on a shelf has a label: its SKU, its name, and its price. The labels change every week, as prices change and sales start and end, so the store prints them from its catalog. The data is messy in the usual ways. SKUs arrive with stray spaces and in small letters, some names are longer than the label, and a product sold by weight must show its price per kilogram as well.

The program follows the data. Each fix to a value is a small function with a doc comment and an example: clean the SKU, fit the name, write the price. Each kind of label is a function built from those. `main` prints the labels of four products and counts the copies to print. Every section of this chapter has its part:

- `Int` cents and Euclidean division ([section 2.2](/learn/numbers/#s2-2)) write the prices, and a precondition makes a division by a parameter safe.
- `Bool` ([section 3.3](#s3-3)) states the store's rule for a sale.
- The prelude's text functions and a proved `slice` ([section 3.1](#s3-1)) clean SKUs and fit names.
- A `let edit` total ([section 2.1](/learn/numbers/#s2-1)) counts the copies.
- A `U8` ([section 2.3](/learn/numbers/#s2-3)) is the count the label printer reads.

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

`money` writes the two digits of the cents one by one, as in the last exercise of [chapter 2](/learn/numbers/#exercise-3-amounts-with-two-decimals), so 1205 is `12.05` and never `12.5`. Its doc comment states that it is for amounts that are not negative, since a refund would need the rule of [Euclidean division](/learn/numbers/#euclidean-division), in section 2.1.

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

`copies` gives the count the printer reads, as in [section 2.3](/learn/numbers/#s2-3). `main` prints each label and adds its copies to a running total, which is a `let edit` name:

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

## 3.6 Testing it

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

## 3.7 Common mistakes

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

*Why:* `+` adds numbers. A text is not a number, and Una converts neither side. The message names the operator and the type it found. una reports each operand that is a text, here both, and also that the function no longer returns a `Text`, since `+` gives an `Int`: one mistake, three diagnostics, and the one fix removes them all.

*Fix:* join texts with an interpolation, `"{regular_label(sku, name: name, cents: cents)} ({money(kilo)} per kg)"`. See [U2001](/docs/errors/U2001/).
:::

### Dividing by a parameter (U5001)

:::mistake
Remove the precondition of `per_kilo`, which canonical form then writes on one line:

```diff include="day-to-day..mistakes/2:src/labels.una" context="1"
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

```text include="mistakes/2/expected/rendered.txt#L1,L8,L12"
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

```diff include="day-to-day..mistakes/3:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -62,3 +62,3 @@
   printed = printed + copies(12).to_int()
-  @console.print(regular_label("DESK-02", name: "Oak writing desk", cents: 15900))
+  @console.print("{regular_label("DESK-02", name: "Oak writing desk", cents: 15900)}")
   printed = printed + copies(1).to_int()
```

```text include="mistakes/3/expected/rendered.txt#L1"
[U0006] Error: text literal inside interpolation; bind it with `let` and interpolate the name
```

*Why:* the braces of an interpolation cannot hold a text literal, since its quotes would end the outer text. una reports each of the two, and the message gives the repair.

*Fix:* print the label itself, `@console.print(regular_label(…))`, or name the texts with `let` first, as the message says. See [U0006](/docs/errors/U0006/).
:::

### A literal out of range (U2022)

:::mistake
Give a shelf 300 facings:

```diff include="day-to-day..mistakes/4:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -61,3 +61,3 @@
   @console.print(weight_label("coffee-05", name: "Coffee beans, dark roast", cents: 1250, grams: 500))
-  printed = printed + copies(12).to_int()
+  printed = printed + copies(300).to_int()
   @console.print(regular_label("DESK-02", name: "Oak writing desk", cents: 15900))
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U2022] Error: the literal `300` does not fit `U8`, which holds `0` to `255`
```

*Why:* the parameter of `copies` is a `U8`, so the literal is a `U8`, and 300 does not fit. The message gives the type and its range, `0` to `255`. This check needs no proof: the checker sees the literal and the type.

*Fix:* a value that fits, or a wider type for the parameter if the printer accepts one. See [U2022](/docs/errors/U2022/).
:::

### A number as a condition (U2001)

:::mistake
Test the discount itself, as if a number could be true:

```diff include="day-to-day..mistakes/5:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -35,3 +35,3 @@
   let regular = regular_label(sku, name: name, cents: cents)
-  if on_sale(percent) then "{regular}, now {money(now)} ({percent}% off)" else regular
+  if percent then "{regular}, now {money(now)} ({percent}% off)" else regular
 
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U2001] Error: the condition of `if` must be `Bool`, found `Int`
```

*Why:* a condition must be a `Bool`. An `Int` is never true or false. The message names the place, the condition of `if`, the type it needs and the type it found.

*Fix:* say the rule: `if on_sale(percent)`, or `if percent > 0`. See [U2001](/docs/errors/U2001/).
:::

## 3.8 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added at the end, and a stub of the function to write, whose body is a placeholder value. `una test .` fails there until the exercise is done. Work as in [chapter 2](/learn/numbers/#s2-7):

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

Check your answer with `una test .`. A `U16` holds 0 to 65535, as the table of [section 2.3](/learn/numbers/#s2-3) shows.

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

## 3.9 Recap and reference

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
- Use a fixed-width type only where a width is required. Its arithmetic is proved to fit, and conversions are explicit. It and `let edit` need edition `0.2` or later.
:::

### Reference

:::reference
- Construct pages: [literals and operators](/docs/language/lexical-structure/), [built-in types](/docs/language/types/), [`let` and `if`](/docs/language/control-flow/), [`let edit`](/docs/language/control-flow/let-edit/), [`requires`](/docs/language/functions/requires/)
- Guides: [fixed-width integers](/docs/guides/fixed-width-integers/), [work with text](/docs/guides/text/)
- Standard library: [the prelude](/docs/std/) (`Int`, `Bool`, `Text`, `trim`, `starts_with`), [text](/docs/std/text/) (`slice`, `replace`, `contains_text`, `to_upper`, `split`), [the built-in methods](/docs/std/builtin/) (`.len`, `to_int`, `to_u8`, `saturating_sub`)
- Diagnostics: [U0006](/docs/errors/U0006/), [U0101](/docs/errors/U0101/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2019](/docs/errors/U2019/), [U2022](/docs/errors/U2022/), [U5001](/docs/errors/U5001/)
- Specification: [lexical structure](/docs/spec/01-lexical-structure/), [types](/docs/spec/03-types/), [the standard library](/docs/spec/14-standard-library/), [the memory model](/docs/spec/17-memory-model/), [fixed-width integers](/docs/spec/18-fixed-width-integers/), [text](/docs/spec/22-text/)
:::
