---
learn: "3"
title: Text and conditions
editions: ["0.2"]
codes: [U0006, U0007, U0101, U2001, U5001]
time: 55
builds: The shelf labels of a store, with cleaned SKUs, names cut to fit, sale prices, prices per kilogram and stock notes
prerequisites: ["1", "2"]
template: 2
nav: ["Text", "Working with text", "Conditions: Bool", "Choosing a value: if", "Day-to-day: shelf labels", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 3 Text and conditions

Most of what a store's program shows to people is text: a product name, a SKU, a line on a label, a note that says "sold out". And most of what it decides is a question with a yes or no answer: is this product on sale? Is the shelf empty? Does the name fit on the label? This chapter teaches both. You learn how Una writes and builds text, how to clean, search and cut it, how to ask yes-or-no questions with `Bool`, and how to choose between two values with `if`. You end with a program that prints the shelf labels of a store.

## What you'll build

:::build
The shelf labels of a store. The program cleans each SKU, cuts each name to the width of a label, writes the price, the sale price or the price per kilogram, adds a note when a shelf runs low, and asks for a check when a SKU does not look right:

```text include="day-to-day/expected/output.txt"
LAMP-01 | Desk lamp, brass | 19.90
RUG-07 | Wool rug, 120 by 180 cm, | 45.00, now 38.25 (15% off) | only 2 left
COFFEE-05 | Coffee beans, dark roast | 12.50 (25.00 per kg)
DESK-02 | Oak writing desk | 159.00 | sold out
Tea mug, blue: check the SKU "mug 4"
```

You will learn to:

- write texts, with escapes for the characters that need them, and build texts from values with interpolation;
- clean, search, replace and cut texts with the functions every module has, called with a dot;
- ask yes-or-no questions with comparisons and `Bool`, and join them with `and`, `or` and `not`;
- choose between two values with `if … then … else …`;
- read what the checker says when a cut or a division may go wrong, and guard it.
:::

## Why it works this way

Text and conditions are where many programs make quiet mistakes. In some languages, `+` joins a text and a number into a new text without a word, so that `"Total: " + 1 + 2` gives `Total: 12`, where the reader meant 3. A number or an empty text can stand for "no" in a condition, so a slip that tests the amount instead of the rule still runs, and answers the wrong question. A cut of a text at a position past its end stops the program while a customer waits, or quietly gives back less than the code expected.

Una makes each of these a rule that `una check` enforces before the program runs. A text and a number are different types, and nothing turns one into the other unless the code says so, with interpolation. A condition must be a `Bool`, `true` or `false`, and nothing else is read as one. A cut states what it needs, positions inside the text, and the checker proves that every cut in the program gets them, or points at the one that may not, with an example of the text that would break it. `if` is a choice between two values of one type, so every branch gives a value the rest of the code can use.

> [!KEY]
> In Una, a text is a text, a condition is a `Bool`, and a cut of a text is proved to stay inside it before the program runs.

## 3.1 Text

### What a text is

A **text** is a piece of writing that a program holds as a value: a product name, a SKU, a line of a label, a greeting. A text is a sequence of **characters**, in order: letters, digits, spaces, punctuation and symbols. You met texts in [chapter 1](/learn/hello/#s1-4), between double quotes, and the type of a text is `Text`.

Think of a text as the letters on a strip of paper. You can read them, count them, compare two strips, or write a new strip from parts of old ones. But a strip is not a number, even when it shows digits: "02134" on a parcel is a postal code, and nobody adds two postal codes.

A text can hold the characters of any language, `é`, `ü` and `×` included, since Una texts are **Unicode**: the standard that gives a number to every character of every writing system.

### Why a text is not a number

Some values look like numbers but are not amounts: a postal code, a phone number, a SKU's digits. You never add them or multiply them, and their exact characters matter, a leading zero included. Here is a program that keeps a postal code as an `Int`:

```una include="steps/01-postal-number/src/delivery.una" title="src/delivery.una"
module delivery

--- Prints where a parcel goes, with the postal code as a number.
pub main() -> Unit
  uses @console: Console[print]
=
  let postal_code = 02134
  @console.print("Deliver to {postal_code}")
```

`una check .` refuses it:

```text include="steps/01-postal-number/expected/rendered.txt#L1-L8"
[U0007] Error: malformed integer literal `02134`
   ╭─[ src/delivery.una:7:21 ]
   │
 7 │   let postal_code = 02134
   │                     ──┬──
   │                       ╰──── malformed integer literal `02134`
   │
   │ Help: repair 1: write `2134`; edit src/delivery.una:7:21..7:26 to "2134"
```

An `Int` literal never starts with a zero ([section 2.2](/learn/numbers/#s2-2)), so `02134` is not a number Una can write, and the `Help` line offers `2134`, which is a different postal code. The value is a text, and as a text it keeps every character:

```una include="steps/02-postal-text/src/delivery.una#main" title="src/delivery.una" verified="check, run"
--- Prints where a parcel goes, with the postal code as a text.
pub main() -> Unit
  uses @console: Console[print]
=
  let postal_code = "02134"
  @console.print("Deliver to {postal_code}")
```

```text include="steps/02-postal-text/expected/output.txt"
Deliver to 02134
```

The rule of thumb: if you compute with it, it is a number; if you only show it, compare it or take it apart, it is a text.

### How to write a text

#### A text literal

A **literal** is a value written out in the code ([section 2.1](/learn/numbers/#s2-1)). A text literal is the characters of the text between double quotes, `"Desk lamp, brass"`, on one line. The quotes are not part of the text: `"LAMP-01"` holds seven characters, from `L` to `1`. Two quotes with nothing between them, `""`, are the **empty text**: a text with no characters at all, as a strip of paper with nothing written on it.

#### Escapes

A few characters cannot be typed between the quotes as they are. A double quote would end the text, and a brace starts an interpolation, as the next part shows. For these, you write an **escape**: a backslash, `\`, followed by one more character, which together stand for one character of the text.

| Write | For |
| --- | --- |
| `\"` | a double quote |
| `\\` | a backslash |
| `\{` and `\}` | a brace |
| `\n` | a new line: what follows starts a new line when the text is printed |
| `\t` | a tab, a wide space that lines up columns |
| `\u{e9}` | the character whose Unicode number is written between the braces, in hexadecimal (base 16), here `é` |

This module prints one text of each form:

```una include="steps/03-literals/src/texts.una" title="src/texts.una" verified="check, run"
module texts

--- Prints one text of each form: plain, empty, and with each escape.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("Desk lamp, brass")
  @console.print("Café table, 2 × 1 m")
  @console.print("")
  @console.print("The sign says \"SALE\"")
  @console.print("A backslash: \\")
  @console.print("Braces: \{ and \}")
  @console.print("Aisle 4\nAisle 5")
  @console.print("LAMP-01\t19.90")
  @console.print("Caf\u{e9} table")
```

`una run .` prints:

```text include="steps/03-literals/expected/output.txt"
Desk lamp, brass
Café table, 2 × 1 m

The sign says "SALE"
A backslash: \
Braces: { and }
Aisle 4
Aisle 5
LAMP-01	19.90
Café table
```

Each `print` gives one line of output, except the seventh: `"Aisle 4\nAisle 5"` is one text with a new line inside it, so it prints as two lines. The empty text prints as an empty line. `\u{e9}` gives the same `é` as the one typed in the second line.

#### Putting values into a text: interpolation

A name or a computation between braces, inside a text literal, puts its value into the text. This is **interpolation**: `"{units} x {sku}"` is the value of `units`, the characters ` x `, and the value of `sku`. It is also how a program prints a number: `print` takes a text, and `"{units}"` is the text of the number.

```una include="steps/04-interpolation/src/receipt.una" title="src/receipt.una" verified="check, run"
module receipt

--- The SKU of the desk lamp.
lamp_sku() -> Text = "LAMP-01"

--- Prints the lines of a receipt, each built with interpolation.
pub main() -> Unit
  uses @console: Console[print]
=
  let units = 3
  let unit_cents = 1_990
  let sku = lamp_sku()
  let gift = true
  let copies: U8 = 2
  @console.print("{units} x {sku}")
  @console.print("{units} x {unit_cents} cents = {units * unit_cents} cents")
  @console.print("SKU: {lamp_sku()}")
  @console.print("Gift wrap: {gift}")
  @console.print("Receipts to print: {copies}")
  @console.print("{sku}{sku}")
```

```text include="steps/04-interpolation/expected/output.txt"
3 x LAMP-01
3 x 1990 cents = 5970 cents
SKU: LAMP-01
Gift wrap: true
Receipts to print: 2
LAMP-01LAMP-01
```

Between the braces you can write:

- a name, such as `{units}` or `{sku}`;
- a computation, such as `{units * unit_cents}`, which is worked out first;
- a call, such as `{lamp_sku()}`;
- a value of type `Int`, of a fixed-width type such as `U8` ([section 2.3](/learn/numbers/#s2-3)), `Bool` or `Text`. An `Int` goes in as its decimal digits, with no `_`; a `Bool` as `true` or `false`; a text as its characters.

The braces add nothing of their own: `"{sku}{sku}"` is the two texts side by side, with no space between them.

#### Joining texts

Interpolation is also how you join texts. To put a SKU, a bar and a name in one text, write `"{sku} | {name}"`. Una has no operator that joins texts: `+` adds numbers only, and `sku + " | "` does not check, as [Joining texts with `+`](#joining-texts-with-u2001) shows.

### The length of a text, and comparing texts

`.len`, written right after a text or a name that holds one, gives the text's **length**: how many characters it has. It is built into the language, and written without parentheses. `==` asks whether two values are equal, and gives `true` or `false`, which [section 3.3](#s3-3) covers.

```una include="steps/05-lengths/src/lengths.una#main" title="src/lengths.una" verified="check, run"
--- Prints the length of four texts, and compares texts.
pub main() -> Unit
  uses @console: Console[print]
=
  let sku = "LAMP-01"
  let cafe = "Café"
  let empty = ""
  let space = " "
  @console.print("{sku.len} {cafe.len} {empty.len} {space.len}")
  let typed = "lamp-01"
  let escaped = "Caf\u{e9}"
  @console.print("{sku == typed} {cafe == escaped}")
```

```text include="steps/05-lengths/expected/output.txt"
7 4 0 1
false true
```

`"LAMP-01"` has 7 characters, `"Café"` has 4, the empty text has 0, and a text of one space has 1: a space is a character like any other. `"LAMP-01" == "lamp-01"` is `false`, since a capital letter and a small letter are different characters. `"Café" == "Caf\u{e9}"` is `true`: the escape and the typed `é` are the same character, so the two texts are equal.

### How text behaves

- **A text never changes.** Once a text exists, its characters stay as they are. The functions of [section 3.2](#s3-2) that clean or change a text give back a new text, and leave the old one as it was.
- **Lengths count characters, not bytes.** Una stores `é` in two bytes, small units of storage, and `A` in one, but counts each as one character. A few symbols that look like one character on the screen, such as some emoji, are made of several Unicode characters, and count as that many.
- **Equality is exact.** Two texts are equal when they have the same characters in the same order: case, spaces and punctuation all count.
- **A text literal is one line.** A text that is not closed by `"` on its own line is U0004. For a text of several lines, write `\n` where each new line starts.
- **An unknown escape is refused.** `\q` is not an escape, and `una check` reports U0005; a backslash itself is written `\\`.
- **A brace in a text is an interpolation, or escaped.** A `{` that cannot start an interpolation, such as one followed by a quote, and a `}` outside an interpolation, are U0007, with a repair that writes `\{` or `\}`.
- **No text literal inside braces.** The quotes of a literal would end the outer text, so `una check` refuses a literal between the braces of an interpolation. Name the text with `let` first, then put the name in the braces, as [A text inside an interpolation](#a-text-inside-an-interpolation-u0006) shows.

### When to use a text

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Show words, codes or labels to people | a `Text` |
| Hold digits you never compute with, such as a postal code or a phone number | a `Text`, which keeps every character, leading zeros included |
| Count or compute, such as units or cents | an `Int` ([section 2.2](/learn/numbers/#s2-2)) |
| Build a text from values | interpolation, `"{units} x {sku}"` |
| Put a quote, a backslash, a brace, a new line or a tab in a text | an escape: `\"`, `\\`, `\{`, `\}`, `\n`, `\t` |
:::

### Check yourself: text

A gift receipt is printed by this `main`:

```una include="steps/06-text-check/src/receipt.una#main" title="src/receipt.una"
--- Prints a line of a gift receipt, and two more lines.
pub main() -> Unit
  uses @console: Console[print]
=
  let sku = "RUG-07"
  let units = 2
  let empty = ""
  @console.print("{units} x {sku} \{gift\}")
  @console.print("[{empty}] has {empty.len} characters, {sku} has {sku.len}")
  @console.print("Thank you\nCome again")
```

What does `una run .` print?

:::answer Show the answer
```text include="steps/06-text-check/expected/output.txt"
2 x RUG-07 {gift}
[] has 0 characters, RUG-07 has 6
Thank you
Come again
```

The first line puts `units` and `sku` into the text, and `\{gift\}` writes the braces themselves, so `gift` is printed as a word, not looked up as a name. The second line puts the empty text between the brackets, with nothing in it, and gives the lengths 0 and 6. The third `print` is one text with `\n` inside, so it prints as two lines.
:::

## 3.2 Working with text: the prelude's functions and method calls

### What the prelude's text functions are

Una comes with functions that every module can call without writing them: the **prelude**. Among them are the functions that work on text: remove the spaces around a text, change its letters to capitals, search it, replace a part of it, or cut a piece out of it. Think of the tools on a workbench that every workshop has: you do not make a ruler or scissors yourself, you pick them up.

You call most of them with a dot after the text, as `typed.trim`: that is the same call as `trim(typed)`, written so that it reads from left to right. This way of writing a call is **method syntax**.

### Why programs clean and search text

Texts come from people and from other systems, and they are messy. A SKU typed at the till arrives with a stray space and in small letters, and it does not equal the SKU of the catalog:

```una include="steps/07-messy-sku/src/till.una#main" title="src/till.una" verified="check, run"
--- Compares the SKU typed at the till with the SKU of the catalog.
pub main() -> Unit
  uses @console: Console[print]
=
  let typed = " lamp-01"
  let catalog = "LAMP-01"
  @console.print("[{typed}] and [{catalog}]")
  @console.print("the same SKU: {typed == catalog}")
```

```text include="steps/07-messy-sku/expected/output.txt"
[ lamp-01] and [LAMP-01]
the same SKU: false
```

The brackets show the space at the front of the typed SKU. To a reader both are the lamp; to `==` they are different texts. Before a program can compare such a value, it must clean it: remove the spaces around it and write it in one case. Before it can print a long name on a small label, it must cut it. The prelude's functions do this.

### How to call a function with a dot

Here the same functions are called in each form a call can take:

```una include="steps/08-method-syntax/src/till.una" title="src/till.una" verified="check, run"
module till

--- The SKU as labels print it: without the white space around it, in capital letters.
clean_sku(raw: Text) -> Text = raw.trim.to_upper

--- Calls the same functions in each form a call can take.
pub main() -> Unit
  uses @console: Console[print]
=
  let typed = " lamp-01"
  @console.print("[{trim(typed)}]")
  @console.print("[{typed.trim()}]")
  @console.print("[{typed.trim}]")
  @console.print("[{to_upper(trim(typed))}]")
  @console.print("[{typed.trim.to_upper}]")
  @console.print("[{clean_sku(typed)}] [{typed.clean_sku}]")
  let catalog = "LAMP-01"
  @console.print("the same SKU: {typed.clean_sku == catalog}")
```

```text include="steps/08-method-syntax/expected/output.txt"
[lamp-01]
[lamp-01]
[lamp-01]
[LAMP-01]
[LAMP-01]
[LAMP-01] [LAMP-01]
the same SKU: true
```

#### The plain form: `trim(typed)`

The function's name, then its arguments in parentheses, as in [chapter 1](/learn/hello/#s1-4). `trim` takes one text and gives back the text without the spaces around it.

#### Method syntax: `typed.trim()`

The first argument goes in front, followed by a dot and the function's name; the other arguments, if any, go in the parentheses. `typed.trim()` is exactly the call `trim(typed)`, and `una check` treats the two alike.

#### Without parentheses: `typed.trim`

When the value before the dot is the only argument, you may leave out the empty parentheses. `typed.trim` is the same call again, and this is how the book writes such calls. The methods of the fixed-width integers keep their parentheses, as `to_int()` does in [section 2.3](/learn/numbers/#s2-3).

#### A chain: `typed.trim.to_upper`

Calls written with a dot can follow each other. `typed.trim.to_upper` first trims `typed`, then writes the result in capital letters. A chain reads in the order the work is done; the plain form, `to_upper(trim(typed))`, gives the same text, but is read from the inside out.

#### Your own functions: `typed.clean_sku`

Method syntax works for every function, the ones you write included. `clean_sku` takes a text, so `typed.clean_sku` is the call `clean_sku(typed)`. [Section 6.1](/learn/functions/#s6-1) covers calls in depth.

A call with more arguments keeps their labels inside the parentheses: `sku.starts_with(prefix: "LAMP-")` is `starts_with(sku, prefix: "LAMP-")`, with the value before the dot as the first argument.

### Trimming: `trim`, `trim_start` and `trim_end`

`trim` removes the **white space**, the characters that print as blank space, such as spaces, tabs and new lines, at both ends of a text. `trim_start` removes it at the start only, and `trim_end` at the end only:

```una include="steps/09-trim/src/trimming.una#main" title="src/trimming.una" verified="check, run"
--- Prints what the three trimming functions leave of a few texts.
pub main() -> Unit
  uses @console: Console[print]
=
  let padded = "  oak desk  "
  @console.print("[{padded}]")
  @console.print("[{padded.trim}]")
  @console.print("[{padded.trim_start}]")
  @console.print("[{padded.trim_end}]")
  let typed = "\t RUG-07 \n"
  @console.print("[{typed.trim}]")
  let blank = "   "
  @console.print("[{blank.trim}] has {blank.trim.len} characters")
```

```text include="steps/09-trim/expected/output.txt"
[  oak desk  ]
[oak desk]
[oak desk  ]
[  oak desk]
[RUG-07]
[] has 0 characters
```

The space between `oak` and `desk` stays: trimming touches the ends only. The tab and the new line around `RUG-07` go, as spaces do. A text of spaces alone trims to the empty text, of length 0.

### Changing case: `to_upper` and `to_lower`

`to_upper` writes the letters `a` to `z` as `A` to `Z`, and `to_lower` does the reverse:

```una include="steps/10-case/src/case.una#main" title="src/case.una" verified="check, run"
--- Prints texts written in capital and in small letters.
pub main() -> Unit
  uses @console: Console[print]
=
  let typed = "lamp-01"
  @console.print(typed.to_upper)
  let shouted = "WOOL RUG, Natural"
  @console.print(shouted.to_lower)
  let cafe = "Café crème"
  @console.print("{cafe.to_upper}: {cafe.len} characters, then {cafe.to_upper.len}")
```

```text include="steps/10-case/expected/output.txt"
LAMP-01
wool rug, natural
CAFé CRèME: 10 characters, then 10
```

Only the 26 letters of the English alphabet change: `é` and `è` stay as they are. The rule is the same on every computer, whatever its language settings, and the length of the text never changes.

### Searching: `starts_with`, `ends_with`, `contains_text` and `is_digits`

These four answer a question about a text, with `true` or `false`:

- `t.starts_with(prefix: p)`: whether `t` begins with `p`;
- `t.ends_with(suffix: s)`: whether `t` ends with `s`;
- `t.contains_text(part: p)`: whether `p` appears anywhere in `t`;
- `t.is_digits`: whether every character of `t` is a digit from `0` to `9`.

```una include="steps/11-search/src/search.una#main" title="src/search.una" verified="check, run"
--- Prints what the search functions answer about a SKU and a few typed texts.
pub main() -> Unit
  uses @console: Console[print]
=
  let sku = "COFFEE-05"
  let food = sku.starts_with(prefix: "COFFEE-")
  let small = sku.ends_with(suffix: "-05")
  let dash = sku.contains_text(part: "-")
  @console.print("starts with COFFEE-: {food}, ends with -05: {small}, has a dash: {dash}")
  let lower = sku.starts_with(prefix: "coffee-")
  @console.print("starts with coffee-: {lower}")
  let count = "0042"
  let typed = "42 "
  let empty = ""
  @console.print("only digits: {count.is_digits}, {typed.is_digits}, {empty.is_digits}")
```

```text include="steps/11-search/expected/output.txt"
starts with COFFEE-: true, ends with -05: true, has a dash: true
starts with coffee-: false
only digits: true, false, true
```

The search is exact: `"coffee-"` is not found at the start of `"COFFEE-05"`, since the case differs. `"42 "` is not all digits, because of its space. `is_digits` of the empty text is `true`: it has no character that is not a digit.

Each answer is named with `let` before it is printed, such as `let food = sku.starts_with(prefix: "COFFEE-")`. The call holds a text literal, `"COFFEE-"`, and a text literal cannot stand inside the braces of an interpolation; the name can.

### Replacing: `replace`

`t.replace(pattern: p, by: r)` gives back `t` with every place where `p` appears replaced by `r`, from left to right:

```una include="steps/12-replace/src/names.una#main" title="src/names.una" verified="check, run"
--- Prints a product name and a SKU with parts replaced.
pub main() -> Unit
  uses @console: Console[print]
=
  let name = "Oak desk, oak legs"
  @console.print(name.replace(pattern: "oak", by: "walnut"))
  @console.print(name.replace(pattern: "Oak", by: "Walnut"))
  @console.print(name.replace(pattern: "pine", by: "walnut"))
  let typed = "lamp 01"
  @console.print(typed.replace(pattern: " ", by: "-"))
  let draft = "RUG-07 (draft)"
  @console.print(draft.replace(pattern: " (draft)", by: ""))
```

```text include="steps/12-replace/expected/output.txt"
Oak desk, walnut legs
Walnut desk, oak legs
Oak desk, oak legs
lamp-01
RUG-07
```

The search for the pattern is exact, as for `contains_text`: `"oak"` replaces the small `oak`, and `"Oak"` the capital one. A pattern that does not appear leaves the text as it was. Replacing with the empty text, `by: ""`, removes the pattern.

#### The pattern must not be empty

An empty pattern would appear between every two characters, so `replace` **requires** a pattern of at least one character. A literal pattern, as here, shows its length to the checker. A pattern that comes from a parameter does not, and `una check` refuses the call:

```una include="steps/13-empty-pattern/src/names.una#dashed" title="src/names.una"
--- A name with every `part` replaced by a dash.
dashed(name: Text, part: Text) -> Text = name.replace(pattern: part, by: "-")
```

```text include="steps/13-empty-pattern/expected/rendered.txt#L1-L6,L18"
[U5001] Error: precondition `part.len > 0` of this call is refuted
   ╭─[ src/names.una:4:42 ]
   │
 4 │ dashed(name: Text, part: Text) -> Text = name.replace(pattern: part, by: "-")
   │                                          ──────────────────┬─────────────────
   │                                                            ╰─────────────────── precondition `part.len > 0` of this call is refuted
   │ Note 2: counterexample: part = Text#0, part.len = 0
```

The message names what the call needs, `part.len > 0`, and says that the checker found a case where it does not hold: the call is **refuted**. The **counterexample** on the last line is that case: `part` is a text whose length is 0. `Text#0` stands for "some text"; the checker names it, and the facts after it, here its length, are the ones that matter. The repairs come in [section 3.4](#s3-4), which guards a call with `if`, and in [chapter 5](/learn/contracts/#s5-1), which passes the need on to the callers with `requires`.

### Cutting: `slice`

`t.slice(start: a, end: b)` gives back the characters of `t` from position `a` up to, but not including, position `b`. Positions count characters from 0: in `"COFFEE-05"`, `C` is at position 0, the dash at 6, and the last `5` at 8.

```una include="steps/14-slice/src/cuts.una#main" title="src/cuts.una" verified="check, run"
--- Prints the parts of a SKU, cut out with `slice`.
pub main() -> Unit
  uses @console: Console[print]
=
  let sku = "COFFEE-05"
  @console.print(sku.slice(start: 0, end: 6))
  @console.print(sku.slice(start: 7, end: 9))
  @console.print(sku.slice(start: 7, end: sku.len))
  @console.print("[{sku.slice(start: 3, end: 3)}]")
  @console.print(sku.slice(start: 0, end: sku.len))
```

```text include="steps/14-slice/expected/output.txt"
COFFEE
05
05
[]
COFFEE-05
```

Read the cuts as fences between characters: `start: 0, end: 6` takes the six characters before fence 6, `COFFEE`. `start: 7, end: sku.len` takes everything from position 7 to the end. Equal positions take nothing, the empty text. `start: 0, end: sku.len` takes the whole text. The length of a piece is always `end - start`.

#### A cut must stay inside the text

`slice` requires `0 <= start`, `start <= end` and `end <= t.len`: a cut cannot start before the text, end before it starts, or end past the last character. The checker proves this at every call, before the program runs. Here it can, since `sku` names a literal, whose length the checker knows. For a parameter it cannot, and a label that cuts every name to its first 24 characters does not check:

```una include="steps/15-cut-name/src/labels.una#fit_name" title="src/labels.una"
--- A product name cut to the 24 characters a label has room for.
pub fit_name(name: Text) -> Text = name.slice(start: 0, end: 24)
```

```text include="steps/15-cut-name/expected/rendered.txt#L1-L6,L16"
[U5001] Error: precondition `0 <= 0 and 0 <= 24 and 24 <= name.len` of this call is refuted
   ╭─[ src/labels.una:4:36 ]
   │
 4 │ pub fit_name(name: Text) -> Text = name.slice(start: 0, end: 24)
   │                                    ──────────────┬──────────────
   │                                                  ╰──────────────── precondition `0 <= 0 and 0 <= 24 and 24 <= name.len` of this call is refuted
   │ Note 2: counterexample: name = Text#0, name.len = 0
```

The message writes out what `slice` needs, with the call's own values in place of `start` and `end`: `0 <= 0 and 0 <= 24 and 24 <= name.len`. The counterexample is an empty name, whose length is 0: no 24 characters can be cut from it, and neither from any name shorter than 24. Another language might stop the program here while it runs, or cut less without a word; Una refuses the program and shows the input that would break it. [Section 3.4](#s3-4) fixes `fit_name` with an `if`.

### The text functions at a glance

| Function | Gives | What it needs |
| --- | --- | --- |
| `t.len` | `Int`, the number of characters | nothing |
| `t.trim`, `t.trim_start`, `t.trim_end` | `Text` without the white space at both ends, the start or the end | nothing |
| `t.to_upper`, `t.to_lower` | `Text` with the letters `a` to `z` changed | nothing |
| `t.starts_with(prefix: p)`, `t.ends_with(suffix: s)`, `t.contains_text(part: p)` | `Bool` | nothing |
| `t.is_digits` | `Bool`, whether every character is a digit | nothing |
| `t.replace(pattern: p, by: r)` | `Text` | `p` is not empty |
| `t.slice(start: a, end: b)` | `Text`, the characters from `a` up to `b` | `0 <= a`, `a <= b`, `b <= t.len` |

The prelude has a few more text functions, whose results are values of later chapters. `split`, `chars` and `bytes` give a **list**, a sequence of values ([chapter 10](/learn/collections/#s10-1)). `find` and `to_int` give an `Option`, a value that may be missing, as when a text holds no number ([chapter 7](/learn/failure/#s7-1)). Most of the text functions of this section came with edition `0.2`, the edition of every package in this book.

### A search box

The search box of a store's website matches what a customer types against product names. Customers type in any case, with stray spaces, so the search cleans what they typed and compares in small letters. The module also writes the last part of a product's web address from its name:

```una include="steps/16-search-box/src/search_box.una" title="src/search_box.una" verified="check, run"
module search_box

-- The search box of the store's website: what a customer types, and the product names.

--- What the customer typed, as the search compares it: trimmed, in small letters.
pub tidy(typed: Text) -> Text = typed.trim.to_lower

--- Whether a product name holds what the customer typed, whatever the case of its letters.
pub matches(name: Text, typed: Text) -> Bool = name.to_lower.contains_text(part: tidy(typed))

--- The last part of a product's web address: the name in small letters, with dashes for the
--- comma and the spaces.
pub web_name(name: Text) -> Text = name.trim.to_lower.replace(pattern: ",", by: "").replace(pattern: " ", by: "-")

--- The line the search shows for one product and one search.
pub search_line(name: Text, typed: Text) -> Text = "[{typed}] in {name}: {matches(name, typed: typed)}"

--- Prints four searches, and the web address of a product.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = "Desk lamp, Brass"
  let rug = "Wool rug, natural"
  @console.print(search_line(lamp, typed: "LAMP "))
  @console.print(search_line(rug, typed: "LAMP "))
  @console.print(search_line(rug, typed: " wool"))
  @console.print(search_line(lamp, typed: "brass"))
  @console.print("example.invalid/products/{web_name(lamp)}")
```

```text include="steps/16-search-box/expected/output.txt"
[LAMP ] in Desk lamp, Brass: true
[LAMP ] in Wool rug, natural: false
[ wool] in Wool rug, natural: true
[brass] in Desk lamp, Brass: true
example.invalid/products/desk-lamp-brass
```

- **`tidy`** trims what was typed and writes it in small letters, so that `"LAMP "` becomes `"lamp"`.
- **`matches`** writes the name in small letters too, then searches it for the tidied text. Both sides are in one case, so `"brass"` finds `"Brass"`.
- **`web_name`** is a chain of four calls: trim, small letters, remove the comma, then a dash for each space. `"Desk lamp, Brass"` becomes `desk-lamp-brass`.
- **`search_line`** puts the typed text, the name and the answer into one line. The brackets show the stray spaces of what was typed.

Each function does one step, and its name says which, so a reader can check each one alone.

### Which text function to use

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Remove the stray spaces around a typed value | `trim`, or `trim_start` or `trim_end` for one end |
| Compare texts whatever the case of their letters | `to_lower` (or `to_upper`) on both sides, then `==` |
| Ask whether a text begins, ends with or holds another | `starts_with`, `ends_with`, `contains_text` |
| Change every place where a part appears | `replace`, with a pattern that is not empty |
| Take a piece at known positions | `slice`, with positions the checker can prove |
| Do several of these in a row | a chain: `typed.trim.to_upper` |
:::

### Check yourself: text functions

A product name is typed with stray spaces:

```una include="steps/17-chain-check/src/chains.una#main" title="src/chains.una"
--- Prints a typed product name after a chain of text functions, and two facts about it.
pub main() -> Unit
  uses @console: Console[print]
=
  let typed = "  Wool Rug "
  @console.print(typed.trim.to_lower.replace(pattern: " ", by: "-"))
  let code = typed.trim.to_upper
  let wool = code.starts_with(prefix: "WOOL")
  @console.print("{code.len} {wool}")
```

What does `una run .` print?

:::answer Show the answer
```text include="steps/17-chain-check/expected/output.txt"
wool-rug
8 true
```

The chain runs left to right: `trim` gives `Wool Rug`, `to_lower` gives `wool rug`, and `replace` puts a dash in place of the space. In the second line, `code` is `WOOL RUG`, 8 characters with its inner space, and it starts with `WOOL`.
:::

## 3.3 Conditions: `Bool`

### What a condition is

A **condition** is a question whose answer is yes or no. Is the order over 100.00? Is the address in the country? Does the SKU start with `LAMP-`? Una's type for such answers is `Bool`, and it has exactly two values: `true` for yes, and `false` for no.

Think of a checklist at the packing station: each line is a question, and each gets a tick or a cross, nothing in between. A program asks such questions all the time, and decides what to do from the answers: which price to print, which note to add, whether a parcel ships for free.

You have seen `Bool` values already: `==` gave them in [section 3.1](#s3-1), and `starts_with` in [section 3.2](#s3-2). This section shows how to write conditions, how to join them, and the rules the checker holds them to.

### Why a condition has its own type

In some languages a number can stand for yes or no: 0 means no, and any other number means yes. Then a slip, such as writing the amount where the rule belongs, still runs, and quietly answers the wrong question. In Una a condition must be a `Bool`. Here the rule for free shipping forgets its comparison:

```una include="steps/18-amount-as-condition/src/shipping.una#ships_free" title="src/shipping.una"
--- Whether an order ships for free: 10000 cents of goods or more, to a domestic address.
pub ships_free(cents: Int, domestic: Bool) -> Bool = cents and domestic
```

```text include="steps/18-amount-as-condition/expected/rendered.txt#L1-L6"
[U2001] Error: an operand of `and` must be `Bool`, found `Int`
   ╭─[ src/shipping.una:4:54 ]
   │
 4 │ pub ships_free(cents: Int, domestic: Bool) -> Bool = cents and domestic
   │                                                      ──┬──
   │                                                        ╰──── an operand of `and` must be `Bool`, found `Int`
```

`and` joins two conditions, as this section shows, and `cents` is an `Int`, an amount. The rule meant `cents >= 10_000`, an amount of at least 10000 cents, and the checker says so before the program runs.

### How to write conditions

This module tries each form:

```una include="steps/19-comparisons/src/stock.una" title="src/stock.una" verified="check, run"
module stock

--- Whether a shelf holds any units.
pub in_stock(units: Int) -> Bool = units > 0

--- Prints what comparisons and the operators on `Bool` give.
pub main() -> Unit
  uses @console: Console[print]
=
  let units = 3
  @console.print("{units == 3} {units != 3} {units < 3} {units <= 3} {units > 3} {units >= 3}")
  @console.print("{true and true} {true and false} {false and false}")
  @console.print("{true or false} {false or false}")
  @console.print("{not true} {not false}")
  @console.print("{in_stock(units)} {in_stock(0)} {not in_stock(0)}")
  let few = units < 5
  @console.print("few left: {few}")
  @console.print("{units > 1 and units < 5} {units < 1 or units > 5}")
```

```text include="steps/19-comparisons/expected/output.txt"
true false false true false true
true false false
true false
false true
true false true
few left: true
true false
```

#### `true` and `false`

The two values of `Bool` are written `true` and `false`, in small letters. In an interpolation they print as those words.

#### Comparisons

A **comparison** compares two values and gives a `Bool`:

| Operator | True when |
| --- | --- |
| `==` | the two values are equal |
| `!=` | they are not equal |
| `<` | the left one is smaller |
| `<=` | the left one is smaller, or equal |
| `>` | the left one is larger |
| `>=` | the left one is larger, or equal |

With `units` equal to 3, the first line of output gives each comparison with 3 in turn: equal, not unequal, not smaller, smaller or equal, not larger, larger or equal.

#### `and`, `or` and `not`

Three operators join conditions into larger ones:

- `a and b` is `true` when both `a` and `b` are `true`;
- `a or b` is `true` when at least one of them is `true`;
- `not a` is `true` when `a` is `false`, and `false` when `a` is `true`.

`units > 1 and units < 5` asks whether `units` lies between the two: 3 does, so it is `true`. `units < 1 or units > 5` asks whether it lies outside them, and gives `false`. Una has one more such operator, `implies`, used mostly in the contracts of [chapter 5](/learn/contracts/).

#### A function that answers a question

`in_stock(units: Int) -> Bool = units > 0` is a function whose result is a `Bool`. A call of it, `in_stock(0)`, is a condition like any other, and `not in_stock(0)` asks the opposite question. Naming a condition this way, after the question it answers, is how a program keeps a rule in one place.

#### Naming a condition with `let`

`let few = units < 5` names a condition, as `let` names any value ([section 2.1](/learn/numbers/#s2-1)). `few` is a `Bool`, and you can use it wherever a condition goes.

#### The order of operations

When a condition mixes operators, Una works it out in this order: arithmetic first (`*`, `/`, `mod`, then `+` and `-`), then comparisons, then `not`, then `and`, then `or`. So `not units > 5` means `not (units > 5)`, and `a or b and c` means `a or (b and c)`. Parentheses make any order explicit, and a mixed rule is easier to read with them, even where the order would give the same answer.

### Comparing texts

`==` and `!=` work on two values of any one type, texts included. `<` and the other orderings work on `Int`, on the fixed-width types, and on `Text`. Texts are ordered character by character, by each character's Unicode number, which is not quite the order of a dictionary:

```una include="steps/20-text-order/src/order.una#main" title="src/order.una" verified="check, run"
--- Prints how texts compare and order.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = "LAMP-01"
  let rug = "RUG-07"
  @console.print("{lamp < rug} {rug < lamp}")
  let small = "lamp-01"
  @console.print("{lamp == small} {lamp < small}")
  let ten = "10"
  let nine = "9"
  @console.print("{ten < nine} {10 < 9}")
  let short = "LAMP"
  let empty = ""
  @console.print("{short < lamp} {empty < short}")
```

```text include="steps/20-text-order/expected/output.txt"
true false
false true
true false
true true
```

- `"LAMP-01" < "RUG-07"` is `true`: the first characters differ, and `L` comes before `R`.
- `"LAMP-01" < "lamp-01"` is `true`: the capital letters `A` to `Z` come before the small letters `a` to `z`.
- `"10" < "9"` is `true`, though 10 is larger than 9: as texts, `1` comes before `9`, and the rest does not matter. Compare amounts as `Int`, never as texts.
- A text that is the start of another comes first, so `"LAMP" < "LAMP-01"`, and the empty text comes before every other text.

### Store rules that give a `Bool`

The rules of a store are full of conditions, so they make good functions. The module `shipping` holds three:

```una include="steps/21-shipping-rules/src/shipping.una" title="src/shipping.una" verified="check, run"
module shipping

--- Whether an order ships for free: 10000 cents of goods or more, to a domestic address.
pub ships_free(cents: Int, domestic: Bool) -> Bool = cents >= 10_000 and domestic

--- Whether the carrier must get a signature: an order over 50000 cents, or a gift over 20000.
pub needs_signature(cents: Int, gift: Bool) -> Bool = cents > 50_000 or (gift and cents > 20_000)

--- Whether a typed SKU looks like one of the store's: a dash, and four characters at least.
pub looks_like_sku(typed: Text) -> Bool = typed.trim.len >= 4 and typed.contains_text(part: "-")

--- Prints the shipping rules for a few orders, and checks two typed SKUs.
pub main() -> Unit
  uses @console: Console[print]
=
  let home = ships_free(12_000, domestic: true)
  let abroad = ships_free(12_000, domestic: false)
  @console.print("12000 cents: free at home {home}, free abroad {abroad}")
  let gift = needs_signature(30_000, gift: true)
  let plain = needs_signature(30_000, gift: false)
  @console.print("30000 cents: a signature as a gift {gift}, otherwise {plain}")
  let pays = not ships_free(2_500, domestic: true)
  @console.print("2500 cents pays for shipping: {pays}")
  let typed = " lamp-01"
  let word = "lamp"
  @console.print("{looks_like_sku(typed)} {looks_like_sku(word)}")
```

```text include="steps/21-shipping-rules/expected/output.txt"
12000 cents: free at home true, free abroad false
30000 cents: a signature as a gift true, otherwise false
2500 cents pays for shipping: true
true false
```

1. **`cents >= 10_000 and domestic`.** Both parts must hold. `domestic` is already a `Bool`, so it needs no comparison: write `domestic`, not `domestic == true`.
2. **`cents > 50_000 or (gift and cents > 20_000)`.** `and` comes before `or` anyway, but the parentheses make the rule readable at a glance.
3. **`typed.trim.len >= 4 and typed.contains_text(part: "-")`.** A condition on a text, built from the functions of [section 3.2](#s3-2).
4. **`not ships_free(2_500, domestic: true)`.** `not` turns the answer of a call around: a small order pays for shipping.

Each rule lives in one function, with a name that says which question it answers. When the threshold for free shipping changes, one line changes.

### How conditions behave

#### Comparisons do not chain

In school, `1 <= percent <= 90` means that `percent` lies between 1 and 90. In Una it does not check:

```una include="steps/22-chained/src/shipping.una#fair_discount" title="src/shipping.una"
--- Whether a discount is one the store runs: from 1 to 90 percent off.
pub fair_discount(percent: Int) -> Bool = 1 <= percent <= 90
```

```text include="steps/22-chained/expected/rendered.txt#L1"
[U0101] Error: comparisons cannot be chained; join them with `and`, as in `a < b and b < c`
```

The message gives the repair: two comparisons joined with `and`, `percent >= 1 and percent <= 90`, which no reader can misread.

#### Only values of one type compare

`==` needs two values of the same type. Comparing an `Int` with a `Text`, such as `units == code`, is U2001, "`==` needs operands of one type", never a quiet `false`. The orderings work on numbers and texts only: `true < false` is U2001 too, since a `Bool` has no order.

#### The right side runs only when it is needed

`a and b` works out `a` first. When `a` is `false`, the answer is `false` whatever `b` is, so `b` is not worked out at all. In the same way, `a or b` skips `b` when `a` is `true`. Una relies on this: on the right side of `and`, the checker knows that the left side holds. Here a division by `units` is safe, because it only runs when `units > 0`:

```una include="steps/23-short-circuit/src/packs.una" title="src/packs.una" verified="check, run"
module packs

--- Whether each unit of a pack costs less than 500 cents. An empty pack has no unit, and is
--- not cheap.
pub cheap_each(cents: Int, units: Int) -> Bool = units > 0 and cents / units < 500

--- Prints the answer for three packs.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{cheap_each(900, units: 6)} {cheap_each(900, units: 1)} {cheap_each(900, units: 0)}")
```

```text include="steps/23-short-circuit/expected/output.txt"
true false false
```

For the empty pack, `units > 0` is `false`, so the division never runs, and the answer is `false`. Swap the two sides, and the division comes first, with nothing to say that `units` is not zero:

```text include="steps/24-division-first/expected/rendered.txt#L1-L6,L12"
[U5001] Error: division obligation `units != 0` is refuted
   ╭─[ src/packs.una:5:50 ]
   │
 5 │ pub cheap_each(cents: Int, units: Int) -> Bool = cents / units < 500 and units > 0
   │                                                  ──────┬──────
   │                                                        ╰──────── division obligation `units != 0` is refuted
   │ Note 2: counterexample: units = 0
```

This is the division obligation of [section 2.2](/learn/numbers/#s2-2): the checker must prove that the divisor is not zero, and the counterexample is `units = 0`. Order the parts of a condition so that each one is safe given the ones before it.

### When to use a `Bool`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Answer a yes-or-no question | a `Bool`, `true` or `false` |
| Name a rule of the store | a function that gives a `Bool`, named after the question: `ships_free` |
| Require two things at once | `and` |
| Accept either of two things | `or` |
| Ask the opposite question | `not` |
| Test a range | two comparisons joined with `and`, never a chain |
| Guard a step that needs the first part to hold | `and`, with the guarding part on the left |
:::

### Check yourself: conditions

`units` is 3 and `gift` is `true`:

```una include="steps/25-conditions-check/src/rules.una#main" title="src/rules.una"
--- Prints three conditions on the same two values.
pub main() -> Unit
  uses @console: Console[print]
=
  let units = 3
  let gift = true
  @console.print("{not units > 5}")
  @console.print("{not gift or units > 5}")
  @console.print("{units < 2 or units < 5 and gift}")
```

What do the three lines print?

:::answer Show the answer
```text include="steps/25-conditions-check/expected/output.txt"
true
false
true
```

`not` comes after comparisons, so `not units > 5` is `not (units > 5)`: 3 > 5 is `false`, and `not false` is `true`. In the second line `not` applies to `gift` alone: `not gift` is `false`, `units > 5` is `false`, and `false or false` is `false`. In the third, `and` comes before `or`: `units < 5 and gift` is `true`, so the whole is `true`, whatever `units < 2` gives.
:::

## 3.4 Choosing between two values: `if`

### What `if` is

`if` chooses between two values by a condition. Think of a sign at the till: "orders of 100.00 or more ship free; otherwise shipping is 4.90". The clerk checks one fact, and the answer is one of two prices. `if` writes that rule: `if goods >= 10_000 then 0 else 490`.

Three words name its parts:

- the **condition**, after `if`: a `Bool`;
- the **branches**: the value after `then`, which is the answer when the condition is `true`, and the value after `else`, which is the answer when it is `false`;
- only the branch the condition picks is worked out. The other is skipped.

An `if` is an **expression**: a piece of code that gives a value, as `2 + 3` or a call does. So an `if` can stand wherever a value goes: as the body of a function, after `let`, as an argument, or as part of a larger expression.

### Why a program chooses

A function without a choice answers every input the same way. Here is a product page that says how many units are left, with one sentence for every case:

```una include="steps/26-no-if/src/shelf.una" title="src/shelf.una" verified="check, run"
module shelf

--- What a product page says about the stock of a product: one sentence for every case.
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

```text include="steps/26-no-if/expected/output.txt"
only 0 units left
only 1 units left
only 3 units left
only 40 units left
```

Only one line in four reads well. "only 0 units left" should say that the product is out of stock, "only 1 units left" is bad English, and "only 40 units left" makes a full shelf sound scarce. The right sentence depends on the number, and a single text cannot say so. `if` can.

### How to write `if`

The module `choices` has an `if` in each place it can stand, and `main` prints one line for each:

```una include="steps/27-if-forms/src/choices.una" title="src/choices.una" verified="check, run"
module choices

--- Whether a parcel counts as heavy: an `if` as a function's whole body.
weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy" else "light"

--- The name of a shipping zone: an `else if` chain.
zone_name(zone: Int) -> Text = if zone == 1 then "home" else if zone == 2 then "neighbors" else "world"

--- The handling fee of an order: an `if` in parentheses, as one part of a sum.
handling(goods: Int) -> Int = 190 + (if goods >= 10_000 then 0 else 300)

--- Prints one line for each place an `if` can stand.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{weight_class(2_300)}, {weight_class(800)}")
  @console.print("{zone_name(1)}, {zone_name(2)}, {zone_name(7)}")
  @console.print("{handling(4_500)}, {handling(12_000)}")
  let units = 1
  let word = if units == 1 then "unit" else "units"
  @console.print("{units} {word}")
  @console.print(if units > 10 then "a bulk order" else "a regular order")
```

```text include="steps/27-if-forms/expected/output.txt"
heavy, light
home, neighbors, world
490, 190
1 unit
a regular order
```

#### `if … then … else …`

`if grams > 2_000 then "heavy" else "light"` is the whole form: the keyword `if`, the condition, `then` and the value for `true`, `else` and the value for `false`, all on one line. 2300 grams is above 2000, so `weight_class(2_300)` is `"heavy"`; 800 is not, so `weight_class(800)` is `"light"`.

#### More than two cases: `else if`

The value after `else` may be another `if`. `if zone == 1 then "home" else if zone == 2 then "neighbors" else "world"` tries the conditions in order, and the first that holds gives the value. The last `else` takes every case that no condition took, here every zone but 1 and 2.

#### As part of a larger expression: in parentheses

`190 + (if goods >= 10_000 then 0 else 300)` adds the result of the `if` to 190. The parentheses are required when an `if` is one part of a larger expression, so that the reader and the checker see where it ends. An order of 4500 cents pays 190 plus 300, and one of 12000 cents pays 190 plus 0.

#### After `let`, and as an argument

`let word = if units == 1 then "unit" else "units"` names the value an `if` gives. `@console.print(if units > 10 then "a bulk order" else "a regular order")` passes it to a call. In both places the `if` is the whole value, so it needs no parentheses.

Una has other forms of `if`, written over several lines with a block of steps in each branch, and `when`, which chooses by the shape of a value. [Chapter 8](/learn/choices/#s8-1) covers every form of `if`, and [section 4.3](/learn/kinds/#s4-3) introduces `when`.

### How `if` behaves

#### Every `if` on one line has its `else`

An `if` gives a value, so it needs one for each answer of its condition. Leave out the `else`:

```text include="steps/28-no-else/expected/rendered.txt#L1-L8"
[U0101] Error: unexpected end of line, expected `else`
   ╭─[ src/choices.una:4:65 ]
   │
 4 │ weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy"
   │                                                                 ┬
   │                                                                 ╰── unexpected end of line, expected `else`
   │
   │ Help: repair 1: an `if` with `then` needs `else`; to fail early, make the rest of the body its `else` branch, as in `if x < 0 then fail Broke else x`, or use the block form, whose `else` block holds the rest
```

The marks point at the end of the line, where `una check` expected `else`. Without it, `weight_class(800)` would have no text to give back. The `Help` line also mentions `fail` and a block form, which come in later chapters; for an `if` of this section, the repair is the missing `else` and its value.

#### Parentheses around an `if` inside a larger expression

Without its parentheses, the `if` in `handling` does not check:

```text include="steps/29-no-parentheses/expected/rendered.txt#L1-L6"
[U0101] Error: unexpected keyword `if`, expected an expression
    ╭─[ src/choices.una:10:37 ]
    │
 10 │ handling(goods: Int) -> Int = 190 + if goods >= 10_000 then 0 else 300
    │                                     ─┬
    │                                      ╰── unexpected keyword `if`, expected an expression
```

After `190 +`, the checker expected a value, and an `if` may only start one in parentheses.

#### Both branches give the same type

The two branches are two possible values of one expression, so they must have one type. A branch that gives a number where the other gives a text is refused:

```text include="steps/30-two-types/expected/rendered.txt#L1-L6"
[U2001] Error: expected `Text`, found `Int`
    ╭─[ src/choices.una:20:45 ]
    │
 20 │   let word = if units == 1 then "unit" else 2
    │                                             ┬
    │                                             ╰── expected `Text`, found `Int`
```

The `then` branch is a `Text`, so the checker expects a `Text` from the `else` branch too, and reports the `Int` it found there. A choice between `"unit"` and `"units"` is a choice between two texts.

#### The condition is a `Bool`

The condition of an `if` follows the rule of [section 3.3](#s3-3): an `Int` or a `Text` is not a condition. `if percent then …` is U2001, as [A number as a condition](#a-number-as-a-condition-u2001) shows.

#### Only the chosen branch runs, and it knows why

The branch that the condition does not pick is never worked out. And inside the branch it picks, the checker knows that the condition holds, as it knew the left side of `and` in [section 3.3](#s3-3). So an `if` can guard a step that would not be safe for every value:

```una include="steps/31-per-unit/src/packs.una#per_unit" title="src/packs.una" verified="check"
--- The price of one unit of a pack, in cents, rounded down. An empty pack gives 0.
per_unit(cents: Int, units: Int) -> Int = if units > 0 then cents / units else 0
```

```text include="steps/31-per-unit/expected/output.txt"
150, 333, 0
```

In the `then` branch, `units > 0` holds, so the division by `units` is proved safe. For an empty pack, the `else` branch gives 0, and the division never runs.

This repairs the cut of [section 3.2](#s3-2). `fit_name` cuts a name only when it is longer than 24 characters, and gives the name itself otherwise:

```diff include="steps/15-cut-name..steps/32-fit-name:src/labels.una" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -1,7 +1,7 @@
 module labels
 
 --- A product name cut to the 24 characters a label has room for.
-pub fit_name(name: Text) -> Text = name.slice(start: 0, end: 24)
+pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name
 
 --- Prints two names as a label shows them.
 pub main() -> Unit
```

```text include="steps/32-fit-name/expected/output.txt"
[Desk lamp, brass]
[Wool rug, 120 by 180 cm,]
```

In the `then` branch, `name.len > 24`, so `24 <= name.len` holds and the cut is proved. A short name never reaches the cut. [Section 8.3](/learn/choices/#s8-3) shows what else a branch proves.

### Stock messages with `if`

Back to the product page. The module `stock` gives each stock level its own sentence:

:::steps
```una include="steps/33-stock/src/stock.una" title="src/stock.una" verified="check, run"
module stock

--- "unit" or "units", whichever goes with `count`.
pub units_word(count: Int) -> Text = if count == 1 then "unit" else "units"

--- What a product page says about the stock of a product.
pub availability(on_hand: Int) -> Text
=
  let few = "only {on_hand} {units_word(on_hand)} left"
  if on_hand <= 0 then "out of stock" else if on_hand < 5 then few else "in stock"

--- Prints what the product page says for four stock levels.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(availability(0))
  @console.print(availability(1))
  @console.print(availability(3))
  @console.print(availability(40))
```

1. **`if count == 1 then "unit" else "units"`.** The one-line form as a function's whole body: the word that goes with a count.
2. **`let few = "only {on_hand} {units_word(on_hand)} left"`.** The long form of a function may name values with `let` before its last line, and the last line is the function's result ([section 6.2](/learn/functions/#s6-2)). Naming the sentence keeps the `if` short.
3. **`if on_hand <= 0 then "out of stock" else if on_hand < 5 then few else "in stock"`.** Three cases, tried in order: an empty shelf, then a shelf with a few units, then every other.
:::

`una run .` prints:

```text include="steps/33-stock/expected/output.txt"
out of stock
only 1 unit left
only 3 units left
in stock
```

Each stock level now gets the sentence that fits it, and the rule for each case is written once, where a reader looks for it.

### When to use `if`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Pick one of two values by a condition | `if … then … else …` |
| Pick one of several values, tried in order | `else if`, with a last `else` for the rest |
| Use the choice inside a sum or a comparison | the `if` in parentheses |
| Make a step safe that needs a condition, such as a cut or a division | an `if` whose `then` branch holds the step |
| Answer a yes-or-no question, not choose a value | a `Bool` expression, without `if`: write `units > 0`, not `if units > 0 then true else false` |
| Choose by the variant of a kind | `when` ([section 4.3](/learn/kinds/#s4-3)) |
:::

### Check yourself: `if`

`wrap_fee` prices gift wrapping:

```una include="steps/34-if-check/src/wrapping.una#wrap_fee" title="src/wrapping.una"
--- The gift-wrapping fee of an order: nothing without a gift, 150 cents a unit, 500 at most.
wrap_fee(units: Int, gift: Bool) -> Int = if not gift then 0 else if units > 3 then 500 else 150 * units
```

`main` prints `wrap_fee(2, gift: true)`, `wrap_fee(5, gift: true)` and `wrap_fee(5, gift: false)`, separated by commas. Predict the line.

:::answer Show the answer
```text include="steps/34-if-check/expected/output.txt"
300, 500, 0
```

2 units as a gift take the last branch, 150 × 2 = 300. 5 units as a gift pass the second condition, `units > 3`, and pay the most, 500. Without a gift, the first condition, `not gift`, holds, and the other branches are never worked out.
:::

## 3.5 Day-to-day: shelf labels

### What the program must do

Every product on a shelf has a label: its SKU, its name and its price. The labels change every week, as prices change and sales start and end, so the store prints them from its catalog. The data is messy in the usual ways. SKUs arrive with stray spaces and in small letters, some names are longer than the label, and some SKUs are typed wrong. A product sold by weight shows its price per kilogram too, and a shelf that runs low gets a note.

Every section of this chapter has its part:

- the text functions of [section 3.2](#s3-2) clean SKUs and cut names;
- interpolation, from [section 3.1](#s3-1), builds each line;
- `Bool` rules, from [section 3.3](#s3-3), say when a discount is a sale and when a SKU looks right;
- `if`, from [section 3.4](#s3-4), chooses the price, the note and the line, and guards the cut and the division.

The program is one module, `labels`, in a package whose `una.toml` names it as the entry, as in [chapter 1](/learn/hello/#making-the-package).

### Cleaning and checking the SKU

```una include="day-to-day/src/labels.una#clean_sku..valid_sku" title="day-to-day/src/labels.una" caption="the SKU"
--- The SKU as labels print it: without the white space around it, in capital letters.
pub clean_sku(raw: Text) -> Text = raw.trim.to_upper

--- Whether a cleaned SKU looks like one of the store's: at least four characters, with a dash
--- that is neither the first character nor the last, as in "LAMP-01".
pub valid_sku(sku: Text) -> Bool
=
  let dash = "-"
  let inside = not sku.starts_with(prefix: dash) and not sku.ends_with(suffix: dash)
  sku.len >= 4 and sku.contains_text(part: dash) and inside
```

`clean_sku` is a chain: trim, then capitals. `valid_sku` is the store's rule for a SKU, made of conditions: at least four characters, a dash, and the dash neither first nor last. It names the dash once, and names the condition on its place, `inside`, so that the last line reads as the rule.

### The name and the price

```una include="day-to-day/src/labels.una#fit_name..sale_cents" title="day-to-day/src/labels.una" caption="the name and the amounts"
--- A product name cut to the 24 characters a label has room for.
pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name

--- Cents as an amount with two decimals, for an amount that is not negative: 1990 is "19.90".
pub money(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"

--- Whether a discount is one the store runs: from 1 to 90 percent off.
pub on_sale(percent: Int) -> Bool = percent >= 1 and percent <= 90

--- The price after `percent` off, rounded down to a whole cent.
pub sale_cents(cents: Int, percent: Int) -> Int = cents * (100 - percent) / 100
```

`fit_name` is the guarded cut of [section 3.4](#s3-4). `money` writes cents with two decimals, using `/` and `mod` from [section 2.2](/learn/numbers/#s2-2): 1205 cents is 12, a point, then the two digits 0 and 5, so `12.05` and never `12.5`. Its doc comment says it is for amounts that are not negative. `on_sale` is the store's rule for a discount, and `sale_cents` takes the discount off, multiplying before it divides, so that 15 percent off 1999 cents gives 1699, rounded down.

### The price part of the label

```una include="day-to-day/src/labels.una#per_kilo..price_text" title="day-to-day/src/labels.una" caption="the price part"
--- The price of one kilogram, in cents, rounded down, for a pack of `grams` grams. A product
--- that is not sold by weight has 0 grams, and the result is then 0.
pub per_kilo(cents: Int, grams: Int) -> Int = if grams > 0 then cents * 1000 / grams else 0

--- The price part of a label: the old and the new price during a sale, the price and the price
--- of a kilogram for a product sold by weight, or else the price alone.
pub price_text(cents: Int, percent: Int, grams: Int) -> Text
=
  let regular = money(cents)
  let sale = "{regular}, now {money(sale_cents(cents, percent: percent))} ({percent}% off)"
  let weighed = "{regular} ({money(per_kilo(cents, grams: grams))} per kg)"
  if on_sale(percent) then sale else if grams > 0 then weighed else regular
```

`per_kilo` divides by `grams`, so its `if` guards the division, as `per_unit` does in [section 3.4](#s3-4). A product not sold by weight has 0 grams, and gets 0.

`price_text` names the three texts a price can take, then chooses one with an `else if` chain: the sale text when `on_sale(percent)` holds, the weighed text when the product has a weight, and the regular price otherwise. A discount of 95 percent is more likely a typing mistake than a sale, so `on_sale` is `false` for it, and the label shows the regular price.

### The stock note and the whole label

```una include="day-to-day/src/labels.una#stock_note..shelf_label" title="day-to-day/src/labels.una" caption="the label"
--- A note on the stock left, for a shelf with fewer than five units.
pub stock_note(units: Int) -> Text = if units <= 0 then "sold out" else "only {units} left"

--- The label of one product. A SKU that does not look right gives a line that asks for a check,
--- and a shelf with fewer than five units gets a note on its stock.
pub shelf_label(raw: Text, name: Text, cents: Int, percent: Int, grams: Int, units: Int) -> Text
=
  let sku = clean_sku(raw)
  let line = "{sku} | {fit_name(name)} | {price_text(cents, percent: percent, grams: grams)}"
  let noted = if units < 5 then "{line} | {stock_note(units)}" else line
  if valid_sku(sku) then noted else "{name}: check the SKU \"{raw}\""
```

`stock_note` gives one of two notes. `shelf_label` builds the line in three steps: the SKU, the name and the price joined with bars; then the line with its stock note, when fewer than five units are left; then a choice between that line and a line that asks for a check, when the SKU does not look right. That last line quotes the SKU as it was typed, with `\"` around it.

### `main`

```una include="day-to-day/src/labels.una#main" title="day-to-day/src/labels.una" verified="check, run"
--- Prints the labels of five products.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(shelf_label(" lamp-01", name: "Desk lamp, brass", cents: 1990, percent: 0, grams: 0, units: 12))
  @console.print(shelf_label("rug-07 ", name: "Wool rug, 120 by 180 cm, natural", cents: 4500, percent: 15, grams: 0, units: 2))
  @console.print(shelf_label("coffee-05", name: "Coffee beans, dark roast", cents: 1250, percent: 0, grams: 500, units: 30))
  @console.print(shelf_label("DESK-02", name: "Oak writing desk", cents: 15900, percent: 0, grams: 0, units: 0))
  @console.print(shelf_label("mug 4", name: "Tea mug, blue", cents: 650, percent: 0, grams: 0, units: 8))
```

Each step prints one label. Every value of a label is an argument of `shelf_label`, labeled after the first, as in [chapter 1](/learn/hello/#parameters-and-labels-at-the-call), so a reader sees which number is the price and which the discount.

### Running it

In the `day-to-day` directory:

```sh
una check .
una run .
```

`una check .` prints nothing: every cut and every division is proved. `una run .` prints the labels shown in [What you'll build](#what-youll-build). The SKUs come out clean, the rug's name is cut to 24 characters, which ends it on a comma, the coffee shows 25.00 per kilogram for a 500 g pack at 12.50, the rug and the desk get their stock notes, and the mug's SKU, `mug 4`, has no dash, so its line asks for a check.

> [!TIP]
> When a function cuts a text at a computed position, or divides by a parameter, write the guard first, then the step inside it. `una check .` tells you at once whether the guard is enough.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/labels.una" title="day-to-day/src/labels.una" caption="the whole program" verified="check, run, test"
module labels

-- Shelf labels: one line for each product, as the label printer prints it.

--- The SKU as labels print it: without the white space around it, in capital letters.
pub clean_sku(raw: Text) -> Text = raw.trim.to_upper

--- Whether a cleaned SKU looks like one of the store's: at least four characters, with a dash
--- that is neither the first character nor the last, as in "LAMP-01".
pub valid_sku(sku: Text) -> Bool
=
  let dash = "-"
  let inside = not sku.starts_with(prefix: dash) and not sku.ends_with(suffix: dash)
  sku.len >= 4 and sku.contains_text(part: dash) and inside

--- A product name cut to the 24 characters a label has room for.
pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name

--- Cents as an amount with two decimals, for an amount that is not negative: 1990 is "19.90".
pub money(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"

--- Whether a discount is one the store runs: from 1 to 90 percent off.
pub on_sale(percent: Int) -> Bool = percent >= 1 and percent <= 90

--- The price after `percent` off, rounded down to a whole cent.
pub sale_cents(cents: Int, percent: Int) -> Int = cents * (100 - percent) / 100

--- The price of one kilogram, in cents, rounded down, for a pack of `grams` grams. A product
--- that is not sold by weight has 0 grams, and the result is then 0.
pub per_kilo(cents: Int, grams: Int) -> Int = if grams > 0 then cents * 1000 / grams else 0

--- The price part of a label: the old and the new price during a sale, the price and the price
--- of a kilogram for a product sold by weight, or else the price alone.
pub price_text(cents: Int, percent: Int, grams: Int) -> Text
=
  let regular = money(cents)
  let sale = "{regular}, now {money(sale_cents(cents, percent: percent))} ({percent}% off)"
  let weighed = "{regular} ({money(per_kilo(cents, grams: grams))} per kg)"
  if on_sale(percent) then sale else if grams > 0 then weighed else regular

--- A note on the stock left, for a shelf with fewer than five units.
pub stock_note(units: Int) -> Text = if units <= 0 then "sold out" else "only {units} left"

--- The label of one product. A SKU that does not look right gives a line that asks for a check,
--- and a shelf with fewer than five units gets a note on its stock.
pub shelf_label(raw: Text, name: Text, cents: Int, percent: Int, grams: Int, units: Int) -> Text
=
  let sku = clean_sku(raw)
  let line = "{sku} | {fit_name(name)} | {price_text(cents, percent: percent, grams: grams)}"
  let noted = if units < 5 then "{line} | {stock_note(units)}" else line
  if valid_sku(sku) then noted else "{name}: check the SKU \"{raw}\""

--- Prints the labels of five products.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(shelf_label(" lamp-01", name: "Desk lamp, brass", cents: 1990, percent: 0, grams: 0, units: 12))
  @console.print(shelf_label("rug-07 ", name: "Wool rug, 120 by 180 cm, natural", cents: 4500, percent: 15, grams: 0, units: 2))
  @console.print(shelf_label("coffee-05", name: "Coffee beans, dark roast", cents: 1250, percent: 0, grams: 500, units: 30))
  @console.print(shelf_label("DESK-02", name: "Oak writing desk", cents: 15900, percent: 0, grams: 0, units: 0))
  @console.print(shelf_label("mug 4", name: "Tea mug, blue", cents: 650, percent: 0, grams: 0, units: 8))

example "a SKU loses its spaces and is written in capitals"
  do clean_sku("  lamp-01 ")
  expect result == "LAMP-01"

example "a SKU with a dash inside it looks right"
  do valid_sku("RUG-07")
  expect result

example "a SKU without a dash does not"
  do valid_sku("MUG 4")
  expect not result

example "a SKU that ends with its dash does not either"
  do valid_sku("LAMP-")
  expect not result

example "a long name is cut to 24 characters"
  do fit_name("Wool rug, 120 by 180 cm, natural")
  expect result.len == 24

example "a short name is kept as it is"
  do fit_name("Desk lamp, brass")
  expect result == "Desk lamp, brass"

example "an amount keeps the zero of its cents"
  do money(1205)
  expect result == "12.05"

example "a discount over 90 percent is not a sale"
  do on_sale(95)
  expect not result

example "a discount rounds down to a whole cent"
  do sale_cents(1999, percent: 15)
  expect result == 1699

example "a product not sold by weight has no price per kilogram"
  do per_kilo(1990, grams: 0)
  expect result == 0

example "a sale shows the old and the new price"
  do price_text(4500, percent: 15, grams: 0)
  expect result == "45.00, now 38.25 (15% off)"

example "an empty shelf is sold out"
  do stock_note(0)
  expect result == "sold out"

example "a SKU that does not look right asks for a check"
  do shelf_label("mug 4", name: "Tea mug", cents: 650, percent: 0, grams: 0, units: 8)
  expect result == "Tea mug: check the SKU \"mug 4\""
```

## 3.6 Testing it

### Examples for each rule

Every function of the program but `main` gives back a value and prints nothing, so each one can have examples, in the form of [section 1.7](/learn/hello/#s1-7): `do` a call, then `expect` what must hold. The examples aim at the edges, where values go wrong:

```una include="day-to-day/src/labels.una#L63-L81" title="day-to-day/src/labels.una" caption="the first five examples"
example "a SKU loses its spaces and is written in capitals"
  do clean_sku("  lamp-01 ")
  expect result == "LAMP-01"

example "a SKU with a dash inside it looks right"
  do valid_sku("RUG-07")
  expect result

example "a SKU without a dash does not"
  do valid_sku("MUG 4")
  expect not result

example "a SKU that ends with its dash does not either"
  do valid_sku("LAMP-")
  expect not result

example "a long name is cut to 24 characters"
  do fit_name("Wool rug, 120 by 180 cm, natural")
  expect result.len == 24
```

- "a SKU loses its spaces and is written in capitals" gives `clean_sku` a value with spaces at both ends.
- The three examples of `valid_sku` cover a right SKU and two wrong ones, one for each part of the rule.
- "a long name is cut to 24 characters" checks the length of the result, `result.len`, not its text: the width is what matters.

The other examples cover the rest: a price whose cents are under ten, a discount over 90 percent, the rounding of a sale, a product not sold by weight, a sale's price text, an empty shelf, and a label for a SKU that does not look right.

### `expect` takes a condition

The line after `expect` is a condition, a `Bool`, and the example passes when it is `true`. `expect result == "LAMP-01"` is a comparison, as in [chapter 1](/learn/hello/#s1-7). When the function itself gives a `Bool`, the result is already the condition: `expect result` says that `valid_sku("RUG-07")` must be `true`, and `expect not result` that `valid_sku("MUG 4")` must be `false`. Write them this way, not `expect result == true`, as you write `domestic` and not `domestic == true`.

### Running the examples

In the `day-to-day` directory, `una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L16"
example labels "a SKU loses its spaces and is written in capitals" ... ok
example labels "a SKU with a dash inside it looks right" ... ok
example labels "a SKU without a dash does not" ... ok
example labels "a SKU that ends with its dash does not either" ... ok
example labels "a long name is cut to 24 characters" ... ok
example labels "a short name is kept as it is" ... ok
example labels "an amount keeps the zero of its cents" ... ok
example labels "a discount over 90 percent is not a sale" ... ok
example labels "a discount rounds down to a whole cent" ... ok
example labels "a product not sold by weight has no price per kilogram" ... ok
example labels "a sale shows the old and the new price" ... ok
example labels "an empty shelf is sold out" ... ok
example labels "a SKU that does not look right asks for a check" ... ok

13 examples: 13 passed, 0 failed
```

## 3.7 Common mistakes

Each mistake is a small change to `day-to-day/src/labels.una`, followed by what `una check .` reports.

### Joining texts with `+` (U2001)

:::mistake
Build the start of the label with `+`, as some languages allow:

```diff include="day-to-day..mistakes/1:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -48,3 +48,3 @@
   let sku = clean_sku(raw)
-  let line = "{sku} | {fit_name(name)} | {price_text(cents, percent: percent, grams: grams)}"
+  let line = sku + " | " + fit_name(name)
   let noted = if units < 5 then "{line} | {stock_note(units)}" else line
```

```text include="mistakes/1/expected/rendered.txt#L1-L9"
[U2001] Error: an operand of `+` must be `Int`, found `Text`
    ╭─[ src/labels.una:49:14 ]
    │
 49 │   let line = sku + " | " + fit_name(name)
    │              ─┬─
    │               ╰─── an operand of `+` must be `Int`, found `Text`
    │
    │ Note: run `una explain U2001` for an explanation
────╯
```

*Why:* `+` adds numbers, and a text is not a number; Una turns neither into the other. The check reports each text that `+` is given, three times here, and a fourth diagnostic follows from them: `+` gives an `Int`, so `line` is an `Int`, and the `if` on the next line cannot choose between a text and it. One mistake, four diagnostics, and one fix removes them all.

*Fix:* join texts with interpolation, `"{sku} | {fit_name(name)} | …"`. See [U2001](/docs/errors/U2001/).
:::

### A text inside an interpolation (U0006)

:::mistake
Print a label through an interpolation, with its arguments written in place:

```diff include="day-to-day..mistakes/2:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -59,3 +59,3 @@
   @console.print(shelf_label("coffee-05", name: "Coffee beans, dark roast", cents: 1250, percent: 0, grams: 500, units: 30))
-  @console.print(shelf_label("DESK-02", name: "Oak writing desk", cents: 15900, percent: 0, grams: 0, units: 0))
+  @console.print("{shelf_label("DESK-02", name: "Oak writing desk", cents: 15900, percent: 0, grams: 0, units: 0)}")
   @console.print(shelf_label("mug 4", name: "Tea mug, blue", cents: 650, percent: 0, grams: 0, units: 8))
```

```text include="mistakes/2/expected/rendered.txt#L1-L9"
[U0006] Error: text literal inside interpolation; bind it with `let` and interpolate the name
    ╭─[ src/labels.una:60:32 ]
    │
 60 │   @console.print("{shelf_label("DESK-02", name: "Oak writing desk", cents: 15900, percent: 0, grams: 0, units: 0)}")
    │                                ────┬────
    │                                    ╰────── text literal inside interpolation; bind it with `let` and interpolate the name
    │
    │ Note: run `una explain U0006` for an explanation
────╯
```

*Why:* the braces of an interpolation cannot hold a text literal, since its quotes would end the outer text. The check reports each of the two literals, `"DESK-02"` and `"Oak writing desk"`, and the message says how to repair it.

*Fix:* the braces add nothing here, so print the label itself, `@console.print(shelf_label("DESK-02", …))`. Where a text must go into braces, name it with `let` first and put the name there. See [U0006](/docs/errors/U0006/).
:::

### A number as a condition (U2001)

:::mistake
Test the discount itself, as if a number could be true:

```diff include="day-to-day..mistakes/3:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -38,3 +38,3 @@
   let weighed = "{regular} ({money(per_kilo(cents, grams: grams))} per kg)"
-  if on_sale(percent) then sale else if grams > 0 then weighed else regular
+  if percent then sale else if grams > 0 then weighed else regular
 
```

```text include="mistakes/3/expected/rendered.txt#L1-L6"
[U2001] Error: the condition of `if` must be `Bool`, found `Int`
    ╭─[ src/labels.una:39:6 ]
    │
 39 │   if percent then sale else if grams > 0 then weighed else regular
    │      ───┬───
    │         ╰───── the condition of `if` must be `Bool`, found `Int`
```

*Why:* the condition of an `if` must be a `Bool`. An `Int` is never true or false in Una, not even 0. The message names the place, the condition of `if`, the type it needs, and the type it found.

*Fix:* say the rule: `if on_sale(percent)`, or `if percent > 0` for any discount at all. See [U2001](/docs/errors/U2001/).
:::

### A chained comparison (U0101)

:::mistake
Write the store's rule for a discount as a chain, as in school:

```diff include="day-to-day..mistakes/4:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -22,3 +22,3 @@
 --- Whether a discount is one the store runs: from 1 to 90 percent off.
-pub on_sale(percent: Int) -> Bool = percent >= 1 and percent <= 90
+pub on_sale(percent: Int) -> Bool = 1 <= percent <= 90
 
```

```text include="mistakes/4/expected/rendered.txt#L1-L6"
[U0101] Error: comparisons cannot be chained; join them with `and`, as in `a < b and b < c`
    ╭─[ src/labels.una:23:50 ]
    │
 23 │ pub on_sale(percent: Int) -> Bool = 1 <= percent <= 90
    │                                                  ─┬
    │                                                   ╰── comparisons cannot be chained; join them with `and`, as in `a < b and b < c`
```

*Why:* comparisons in Una do not chain. `1 <= percent` is a `Bool`, and comparing a `Bool` with 90 has no meaning, so the language refuses the form outright, and the message says what to write instead.

*Fix:* two comparisons joined with `and`: `percent >= 1 and percent <= 90`. See [U0101](/docs/errors/U0101/).
:::

### Cutting a text without a guard (U5001)

:::mistake
Cut every name to 24 characters, without the `if`:

```diff include="day-to-day..mistakes/5:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -16,3 +16,3 @@
 --- A product name cut to the 24 characters a label has room for.
-pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name
+pub fit_name(name: Text) -> Text = name.slice(start: 0, end: 24)
 
```

```text include="mistakes/5/expected/rendered.txt#L1-L6,L16"
[U5001] Error: precondition `0 <= 0 and 0 <= 24 and 24 <= name.len` of this call is refuted
    ╭─[ src/labels.una:17:36 ]
    │
 17 │ pub fit_name(name: Text) -> Text = name.slice(start: 0, end: 24)
    │                                    ──────────────┬──────────────
    │                                                  ╰──────────────── precondition `0 <= 0 and 0 <= 24 and 24 <= name.len` of this call is refuted
    │ Note 2: counterexample: name = Text#0, name.len = 0
```

*Why:* `slice` requires `24 <= name.len`, and nothing says that a name has 24 characters. The counterexample is an empty name, of length 0, from which no 24 characters can be cut. The checker refuses the program rather than let it stop on a short name.

*Fix:* put the `if` back, so that only a name longer than 24 characters is cut, as the second repair of the diagnostic suggests. See [U5001](/docs/errors/U5001/).
:::

### An `if` without `else` (U0101)

:::mistake
Leave out the `else` of the stock note, as if a shelf with units needed no note:

```diff include="day-to-day..mistakes/6:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -41,3 +41,3 @@
 --- A note on the stock left, for a shelf with fewer than five units.
-pub stock_note(units: Int) -> Text = if units <= 0 then "sold out" else "only {units} left"
+pub stock_note(units: Int) -> Text = if units <= 0 then "sold out"
 
```

```text include="mistakes/6/expected/rendered.txt#L1-L6"
[U0101] Error: unexpected end of line, expected `else`
    ╭─[ src/labels.una:42:67 ]
    │
 42 │ pub stock_note(units: Int) -> Text = if units <= 0 then "sold out"
    │                                                                   ┬
    │                                                                   ╰── unexpected end of line, expected `else`
```

*Why:* an `if` on one line gives a value, so it needs a value for each answer of its condition. Without `else`, `stock_note(2)` would have no text to give back. The marks point at the end of the line, where `else` was expected.

*Fix:* give the `if` its `else` and the value for `false`, here `else "only {units} left"`. See [U0101](/docs/errors/U0101/).
:::

## 3.8 Exercises

The exercises come with the chapter's download, `03-text-and-conditions.tar.gz`. Each starts from `exercises/N/start`: the day-to-day program with the exercise's examples added, and, when the exercise asks for a new function, a **stub** of it, whose body is a **placeholder** value. `una test .` fails there until the exercise is done. Work as in [chapter 1](/learn/hello/#s1-9):

1. Read the examples: they say what the function must give back.
2. Change the code.
3. Run `una check .`. When it refutes a cut or a division, read the counterexample: it is the input your code does not handle yet.
4. Run `una test .` until every example passes, then `una run .` to see the labels.

### Exercise 1: food or not

::::exercise
The store keeps food on its own shelves. Write `is_food(sku)`, which is `true` when the SKU starts with `COFFEE-` or with `TEA-`. The start package ends with:

```una include="exercises/1/start/src/labels.una#L115-L128" title="exercises/1/start/src/labels.una"
--- Whether a SKU is one of the store's foods: its SKU starts with "COFFEE-" or "TEA-".
pub is_food(sku: Text) -> Bool = false

example "coffee is a food"
  do is_food("COFFEE-05")
  expect result

example "tea is a food"
  do is_food("TEA-02")
  expect result

example "a lamp is not"
  do is_food("LAMP-01")
  expect not result
```

:::hint
*Hint:* the body is one condition: two calls of `starts_with`, joined by the operator that accepts either.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L15-L23"
example labels "coffee is a food" ... FAILED
  src/labels.una:120: expect result
  it is false, with `result` = `false`
example labels "tea is a food" ... FAILED
  src/labels.una:124: expect result
  it is false, with `result` = `false`
example labels "a lamp is not" ... ok

16 examples: 14 passed, 2 failed
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Give `is_food` its condition:

```diff include="exercises/1/start..exercises/1/answer:src/labels.una" context="1" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -115,3 +115,3 @@
 --- Whether a SKU is one of the store's foods: its SKU starts with "COFFEE-" or "TEA-".
-pub is_food(sku: Text) -> Bool = false
+pub is_food(sku: Text) -> Bool = sku.starts_with(prefix: "COFFEE-") or sku.starts_with(prefix: "TEA-")
 
```

The placeholder `false` passes the example for the lamp, but not the two for coffee and tea. With `or`, a SKU that starts with either prefix is a food.
:::
::::

### Exercise 2: the last unit

::::exercise
When one unit is left on a shelf, the label should say `last one`, not `only 1 left`. Change `stock_note`, then print the label of a brass bookend in `main`, after the mug: SKU `book-11`, 2400 cents, no discount, no weight, one unit. The start package has a new example after the one for an empty shelf:

```una include="exercises/2/start/src/labels.una#L111-L113" title="exercises/2/start/src/labels.una"
example "a shelf with one unit left says so"
  do stock_note(1)
  expect result == "last one"
```

:::hint
*Hint:* a third case goes between the two that `stock_note` has: an `else if` for `units == 1`.
:::

Check your answer with `una test .`, then `una run .` for the new label.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Add the case to `stock_note`, and the label to `main`:

```diff include="exercises/2/start..exercises/2/answer:src/labels.una" context="1" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -41,3 +41,3 @@
 --- A note on the stock left, for a shelf with fewer than five units.
-pub stock_note(units: Int) -> Text = if units <= 0 then "sold out" else "only {units} left"
+pub stock_note(units: Int) -> Text = if units <= 0 then "sold out" else if units == 1 then "last one" else "only {units} left"
 
@@ -61,2 +61,3 @@
   @console.print(shelf_label("mug 4", name: "Tea mug, blue", cents: 650, percent: 0, grams: 0, units: 8))
+  @console.print(shelf_label("book-11", name: "Brass bookend", cents: 2400, percent: 0, grams: 0, units: 1))
 
```

The new label ends with `last one`. The conditions are tried in order, so an empty shelf is still sold out, and two units or more still say how many are left.
:::
::::

### Exercise 3: three dots for a cut name

::::exercise
A cut name should show that it was cut. When a name is longer than 24 characters, keep its first 21 characters, remove the spaces at their end, and add `...`, so that the label never grows past 24. The start package has two new examples in place of the one for long names:

```una include="exercises/3/start/src/labels.una#L79-L85" title="exercises/3/start/src/labels.una"
example "a long name ends with three dots"
  do fit_name("Wool rug, 120 by 180 cm, natural")
  expect result == "Wool rug, 120 by 180..."

example "a cut name still fits the label"
  do fit_name("Coffee beans, dark roast, whole")
  expect result.len <= 24
```

:::hint
*Hint:* in the `then` branch, build a text with interpolation: the cut piece, trimmed at its end, then the three dots. A call that holds no text literal may stand inside the braces. Is a cut of 21 characters proved where the name has more than 24?
:::

Check your answer with `una test .`, then `una run .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Change the `then` branch of `fit_name`:

```diff include="exercises/3/start..exercises/3/answer:src/labels.una" context="1" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -16,3 +16,3 @@
 --- A product name cut to the 24 characters a label has room for.
-pub fit_name(name: Text) -> Text = if name.len > 24 then name.slice(start: 0, end: 24) else name
+pub fit_name(name: Text) -> Text = if name.len > 24 then "{name.slice(start: 0, end: 21).trim_end}..." else name
 
```

The first 21 characters of the rug's name end with a space, `Wool rug, 120 by 180 `, so `trim_end` removes it before the dots. The cut is proved, since a name longer than 24 characters is longer than 21 too. The rug's label now shows `Wool rug, 120 by 180...`.
:::
::::

## 3.9 Recap and reference

### For agents

:::agents
`una --json check .` prints each diagnostic with its `code`, `message`, `primary` span and `repairs`; a refuted obligation, U5001, also carries its `obligation` and a `counterexample`, and its repairs, from a guard to a `requires`, are descriptions only. U0007 carries an exact edit, which `una fix .` applies; U0101, U0006 and U2001 carry no edit, since the right form is the author's choice. The compact rule: *join texts with interpolation, never `+`; name a text literal before it goes in braces; a condition is a `Bool`, and comparisons do not chain; a one-line `if` has `else` and branches of one type; guard a `slice` or a division with `if` or `and`.*
:::

### Recap

:::recap
- A text is written between double quotes on one line; `\"`, `\\`, `\{`, `\}`, `\n`, `\t` and `\u{…}` are its escapes.
- Build a text from values with interpolation, `"{units} x {sku}"`; there is no `+` for texts, and no text literal inside the braces.
- `.len` counts characters, and `==` compares texts exactly, case and spaces included.
- `t.f(args)` is the call `f(t, args)`; chain such calls to clean a text: `typed.trim.to_upper`.
- `slice` needs positions inside the text, and `replace` a pattern that is not empty: the checker proves both at every call.
- A condition is a `Bool`: compare, then join with `and`, `or` and `not`; the right side of `and` runs, and is proved, only when the left side holds.
- `if c then a else b` chooses a value: both branches have one type, `else` is required, and the `then` branch knows that `c` holds.
:::

### Reference

:::reference
- Construct pages: [literals and operators](/docs/language/lexical-structure/), [built-in types](/docs/language/types/), [`let` and `if`](/docs/language/control-flow/), [`example`](/docs/language/examples/example/)
- Guides: [work with text](/docs/guides/text/)
- Standard library: [the prelude](/docs/std/) (`Text`, `Bool`, `trim`, `starts_with`, `is_digits`), [text](/docs/std/text/) (`slice`, `replace`, `contains_text`, `ends_with`, `to_upper`, `to_lower`, `trim_start`, `trim_end`), [the built-in methods](/docs/std/builtin/) (`.len`)
- Diagnostics: [U0004](/docs/errors/U0004/), [U0005](/docs/errors/U0005/), [U0006](/docs/errors/U0006/), [U0007](/docs/errors/U0007/), [U0101](/docs/errors/U0101/), [U2001](/docs/errors/U2001/), [U5001](/docs/errors/U5001/)
- Specification: [lexical structure](/docs/spec/01-lexical-structure/), [grammar](/docs/spec/02-grammar/), [types](/docs/spec/03-types/), [core IR](/docs/spec/09-core-ir/), [verification](/docs/spec/12-verification/), [the standard library](/docs/spec/14-standard-library/), [text](/docs/spec/22-text/)
:::
