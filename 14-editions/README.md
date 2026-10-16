---
learn: "14"
title: Editions
editions: ["0.1", "0.2", "0.3"]
codes: [U0101, U0103, U2001, U3023, U3025, U3026, U5001, U7002]
time: 30
builds: A shelf-label printer on the edition 0.3 preview, with a dry run the checker enforces
prerequisites: ["6", "8", "11", "12", "13"]
template: 2
---

# 14 Editions

A language that grows has to add keywords and tighten rules, and a program written last year must still mean what it meant. Una does this with editions: each package names the edition of the language it is written in, and every release of `una` keeps each stable edition it serves as it was. This chapter shows what an edition is, what editions `0.2` and `0.3` add, and how to move a package from one edition to the next, letting the checker and `una fix` find what has to change.

## What you'll build

:::build
A shelf-label printer for a store, on edition `0.3`. It reads a stock export, prints a label for every line with stock, and has a dry run that counts the labels without printing any. The dry run is not a convention: the checker proves that no label is printed when `dry_run` is true. `main` makes a dry run, then a real one:

```text include="day-to-day/expected/output.txt"
dry run: 2 labels
[LAMP-01 | 4 on hand]
[SHELF-03 | 12 on hand]
printed 2 labels
```

You will learn to:

- name a package's edition in `una.toml`, and know what stays fixed for that edition;
- recognize what edition `0.2` adds, and the diagnostics a construct of a later edition gives;
- use edition `0.3`, a preview, and its stricter rules;
- move a package to a later edition with `una check` and `una fix`;
- lock a function's authority in `una.toml`, so that a change to it shows up in review.
:::

## Why it works this way

Languages that grow without editions face a choice. Either a new keyword breaks every program that used the word as a name, or the language never adds one. A rule that becomes stricter, such as one that rejects code that can never run, breaks programs that passed yesterday, and the team that maintains them finds out on the day a compiler is upgraded.

Una separates the two things a release changes:

:::steps
1. **The compiler improves for every edition.** A new release fixes bugs, adds explanations and makes the tools better, for every package.
2. **The language changes only in a new edition.** New keywords, new constructs and stricter rules come with an edition, and a package gets them only when its `una.toml` names that edition.
3. **Editions are cumulative.** Edition `0.3` has every construct and rule of `0.2`, and `0.2` has every construct of `0.1`. Moving a package forward never removes a construct; it can only reject code that a stricter rule no longer allows.
:::

So upgrading `una` never changes what a stable edition accepts or rejects, except to fix a soundness or security error. Moving a package to a new edition is a separate step, a change to one line of `una.toml`, which you make when you are ready and review like any other change.

> [!KEY]
> A package's edition is a line of `una.toml`. Upgrading `una` keeps the meaning of every stable edition, and a later edition only adds constructs and tightens rules.

## 14.1 An edition is part of the package

### The edition line of `una.toml`

`[package] edition` names the edition. It is a required key of `una.toml`, with `name` and `version`, and leaving it out is U7002. A single `.una` file checked on its own, outside a package, has edition `0.1`.

### A stock list in edition `0.1`

This step is a stock list in edition `0.1`, the first edition. It has kinds, functions and lists, and its loops are written with `fold`:

```toml include="steps/01-edition-0-1/una.toml" title="steps/01-edition-0-1/una.toml"
[package]
name = "shelf"
version = "0.1.0"
edition = "0.1"

[run]
entry = "shelf"
grants = ["console"]
```

```una include="steps/01-edition-0-1/src/shelf.una" title="steps/01-edition-0-1/src/shelf.una" verified="check, run"
module shelf

--- A line of a stock list: a SKU and the units on hand.
kind Line
  sku: Text
  units: Int

--- The units of every line, added up.
total(lines: List[Line]) -> Int = lines.fold(initial: 0, step: fn(sum, line) -> sum + line.units)

pub main() -> Unit
  uses @console: Console[print]
=
  let lines = [Line(sku: "LAMP-01", units: 4), Line(sku: "DESK-02", units: 1)]
  @console.print("{lines.len} lines, {total(lines)} units")
```

Each step is a package, as in [chapter 1](/learn/hello/#s1-1), with the `verification.lock` of chapter 1, or whole from the chapter's download, `14-editions.tar.gz`. In the package's directory:

```sh
una check .
una run .
```

`una run .` prints:

```text include="steps/01-edition-0-1/expected/output.txt"
2 lines, 5 units
```

### One binary serves every edition

`una --version` prints the version of `una` and the editions it serves, one line each: at this release, `editions: 0.1, 0.2, 0.3`. Every one of them is checked by the same binary, so one machine can build packages of different editions side by side.

### Stable editions and previews

An edition is either **stable** or a **preview**:

| Edition | Status | What it promises |
| --- | --- | --- |
| `0.1` | Stable | A later release does not change what it accepts or rejects, except to fix a soundness or security error |
| `0.2` | Stable | The same promise |
| `0.3` | Preview | It may still get stricter in a later `0.3.x` release, never looser |

A package on a stable edition can stay there for as long as it likes. In edition `0.1`, the words that later editions use, such as `edit`, `take` and `together`, are reserved: using one gives a diagnostic that names the edition that has it.

### What an edition fixes, and what improves with every release

What an edition fixes is the language a package is written in: its keywords, its constructs, its rules and the signatures of the prelude. For example, `min`, `max` and `sum` work on `Int` in edition `0.1`, and a later release keeps those signatures for it, while edition `0.2` makes them generic over constrained types. What improves with every release, for every edition, is everything around the language: the wording of messages, the explanations of `una explain`, the repairs, the speed of the checks and the tools of [chapter 13](/learn/tools/).

## 14.2 What edition `0.2` adds

### Moving the stock list to `0.2`

Edition `0.2` is the edition of most of this tutorial. Move the stock list to it, and two things that `0.1` rejects become possible: a `for` loop with a `let edit` binding, and the interpolation of a whole list.

```diff include="steps/01-edition-0-1..steps/02-edition-0-2:una.toml" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -1,7 +1,7 @@
 [package]
 name = "shelf"
 version = "0.1.0"
-edition = "0.1"
+edition = "0.2"
 
 [run]
 entry = "shelf"
```

```diff include="steps/01-edition-0-1..steps/02-edition-0-2:src/shelf.una" title="src/shelf.una"
--- a/src/shelf.una
+++ b/src/shelf.una
@@ -5,11 +5,17 @@
   sku: Text
   units: Int
 
---- The units of every line, added up.
-total(lines: List[Line]) -> Int = lines.fold(initial: 0, step: fn(sum, line) -> sum + line.units)
+--- The units of every line, added up by a loop.
+total(lines: List[Line]) -> Int
+=
+  let edit sum = 0
+  for line in lines
+    sum = sum + line.units
+  sum
 
 pub main() -> Unit
   uses @console: Console[print]
 =
   let lines = [Line(sku: "LAMP-01", units: 4), Line(sku: "DESK-02", units: 1)]
   @console.print("{lines.len} lines, {total(lines)} units")
+  @console.print("{lines}")
```

`una run .` prints:

```text include="steps/02-edition-0-2/expected/output.txt"
2 lines, 5 units
[Line(sku: "LAMP-01", units: 4), Line(sku: "DESK-02", units: 1)]
```

The code of [section 14.1](#s14-1) also checks, unchanged, with only the edition line moved to `0.2`: moving forward did not require touching it. The changes to the code above are ones the new edition allows. `fold` is still there, and still right; the loop is simply easier to read for some code.

### The constructs `0.2` adds

Edition `0.2` adds, among others:

| Construct | Where to read about it |
| --- | --- |
| `for` loops, `let edit`, `edit` and `take` parameters | [Memory and concurrency](/learn/memory-and-concurrency/), [Collections](/learn/collections/) |
| `together` and `together for` | [Memory and concurrency](/learn/memory-and-concurrency/) |
| `Map`, the text functions and `ParseError`, `Json` | [Collections](/learn/collections/), [Failure](/learn/failure/) |
| Fixed-width integers such as `U8` and `I64`, with proven overflow | [Values](/learn/values/#s2-5) |
| Constraints on generics such as `T: Ord`, and `sort` | [Kinds](/learn/kinds/#s4-4) |
| `uses of` and `fails of` for function parameters | [`uses`](/docs/language/capabilities/uses/) |
| The interpolation of any value that `==` compares, except a `Hashed` | [Values](/learn/values/) |
| The `Http` capability | [HTTP in the standard library](/docs/std/http/) |

### The rules that changed

Some rules changed with it too. In edition `0.2`, a kind cannot take the name of a built-in type such as `Text` or `List`, and `una test` shows labeled values in full in a failed example's report.

### What a move from `0.1` can need

So moving a `0.1` package to `0.2` can still need changes, in three places: a name that became a keyword, such as a binding called `edit`, `take`, `old` or `together`; a kind named like a built-in type, which is U1002 in `0.2`; and a call that relied on a prelude signature of `0.1`, since `min`, `max`, `sum` and `contains` became generic over constrained types. The checker reports each one at its place, with the code and a repair, so the move is a list of small, local changes rather than a search through the package.

## 14.3 Edition `0.3`, a preview

### What edition `0.3` adds

Edition `0.3` adds constructs that narrow what a program may do, and rules that reject code that can never run:

- **Conditions on operations.** `uses @printer: Printer[print_label where not dry_run]` lets the function print a label only where the condition holds, and the verifier proves it at every call of the operation ([chapter 8, Capabilities](/learn/capabilities/#s8-5)).
- **Locked contracts.** `[contracts]` in `una.toml` locks the `uses` of a public function: its header may grant less, never more ([chapter 11, Packages and modules](/learn/packages/)).
- **Boundaries.** `[boundaries]` in `una.toml` gives a module a ceiling of operations that the code calling into it may grant ([chapter 8, Capabilities](/learn/capabilities/#s8-5)).
- **No dead failure handling.** An `if error` clause under a call that cannot fail is U3025, and `attempt` of a call that cannot fail is U3026.

The day-to-day program of this chapter uses the first two. This section shows the last one, since it is the rule a package meets when it moves to `0.3`.

### Failure handling that no longer runs

A restock list in edition `0.2` computes how many units to order for each line. `order_quantity` once parsed a typed number and could fail, so its callers handled a failure. It has since become a plain calculation, which cannot fail, and the handling stayed:

```una include="steps/03-restock/src/restock.una" title="steps/03-restock/src/restock.una" verified="check, run"
module restock

--- A line of a stock list: a SKU and the units on hand.
kind Line
  sku: Text
  units: Int

--- How many units to order so that the shelf holds 10.
order_quantity(line: Line) -> Int = if line.units >= 10 then 0 else 10 - line.units

--- The order line for `line`, or a note when nothing is needed.
order_text(line: Line) -> Text
=
  let wanted = order_quantity(line)
    if error use 0
  if wanted == 0 then "{line.sku}: enough" else "{line.sku}: order {wanted}"

--- The total of every order quantity.
total(lines: List[Line]) -> Int
=
  let edit sum = 0
  for line in lines
    let outcome = attempt order_quantity(line)
    sum = when outcome
      is Ok(wanted) -> sum + wanted
      is Err -> sum
  sum

pub main() -> Unit
  uses @console: Console[print]
=
  let lines = [Line(sku: "LAMP-01", units: 4), Line(sku: "SHELF-03", units: 12), Line(sku: "DESK-02", units: 9)]
  for line in lines
    @console.print(order_text(line))
  @console.print("{total(lines)} units to order")
```

In edition `0.2` this is accepted, and `una run .` prints:

```text include="steps/03-restock/expected/output.txt"
LAMP-01: order 6
SHELF-03: enough
DESK-02: order 1
7 units to order
```

### What `0.3` reports: U3025 and U3026

The `if error use 0` clause never runs, and the `Err` arm of `total` is never taken. They are harmless, but they mislead a reader into thinking `order_quantity` can fail. Edition `0.3` rejects both:

```diff include="steps/03-restock..steps/04-restock-0-3:una.toml" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -1,7 +1,7 @@
 [package]
 name = "restock"
 version = "0.1.0"
-edition = "0.2"
+edition = "0.3"
 
 [run]
 entry = "restock"
```

```text include="steps/04-restock-0-3/expected/rendered.txt"
[U3025] Error: this `if error` clause never runs, since the call of `order_quantity` cannot fail; remove the clause
    ╭─[ src/restock.una:15:5 ]
    │
 15 │     if error use 0
    │     ─┬
    │      ╰── this `if error` clause never runs, since the call of `order_quantity` cannot fail; remove the clause
    │
    │ Help: repair 1: remove the clause; edit src/restock.una:14:36..15:19 to ""
    │
    │ Note: run `una explain U3025` for an explanation
────╯
[U3026] Error: the call of `order_quantity` cannot fail, so `attempt` gives a `Result` whose `Err` is never taken; use the value of the call directly
    ╭─[ src/restock.una:23:19 ]
    │
 23 │     let outcome = attempt order_quantity(line)
    │                   ──────────────┬─────────────
    │                                 ╰─────────────── the call of `order_quantity` cannot fail, so `attempt` gives a `Result` whose `Err` is never taken; use the value of the call directly
    │
    │ Help: repair 1: remove `attempt` and use the value of the call directly, then unwrap each use of the `Result`: a `when ... is Ok(v)` becomes the value `v`, its `is Err` arm goes, and a declared `Result[T, E]` becomes `T`
    │
    │ Note: run `una explain U3026` for an explanation
────╯
1 of 2 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

Each diagnostic names its repair. U3025's repair deletes the clause, an exact edit. U3026's repair is a description, because the uses of the `Result` have to be unwrapped by hand.

### A preview may get stricter

> [!IMPORTANT]
> A preview may get stricter in a later `0.3.x` release: a package that checks today on `0.3` may get a new obligation or a new error after an upgrade. Use `0.3` where its rules help, and expect to rerun `una check` after each upgrade.

## 14.4 Moving a package forward

### The steps of a move

Moving a package to a later edition is a short loop. In the package's directory:

:::steps
1. **Change the edition** in `una.toml`, and only that line.
2. **Run `una check .`** and read every diagnostic. Each one is a place the new edition reads differently.
3. **Run `una fix --dry-run .`**, then `una fix .`, to apply the repairs that are exact.
4. **Repair the rest by hand**, guided by each diagnostic's repairs.
5. **Run `una test .`**, and compare the output of `una run .` with the output before the move.
:::

### Moving the restock list

For the restock list, the check of step 2 is the output of [section 14.3](#what-03-reports-u3025-and-u3026), and step 3 shows one exact repair:

```sh
una fix --dry-run .
```

```text include="steps/04-restock-0-3/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/restock.una:14:36 U3025 remove the clause
```

`una fix .` removes the clause. The `attempt` is left to you: remove it, and replace the `when` with the value it unwrapped. The package after both repairs:

```diff include="steps/03-restock..steps/05-restock-moved:src/restock.una" title="src/restock.una"
--- a/src/restock.una
+++ b/src/restock.una
@@ -12,7 +12,6 @@
 order_text(line: Line) -> Text
 =
   let wanted = order_quantity(line)
-    if error use 0
   if wanted == 0 then "{line.sku}: enough" else "{line.sku}: order {wanted}"
 
 --- The total of every order quantity.
@@ -20,10 +19,7 @@
 =
   let edit sum = 0
   for line in lines
-    let outcome = attempt order_quantity(line)
-    sum = when outcome
-      is Ok(wanted) -> sum + wanted
-      is Err -> sum
+    sum = sum + order_quantity(line)
   sum
 
 pub main() -> Unit
```

`una run .` prints the same as before the move:

```text include="steps/05-restock-moved/expected/output.txt"
LAMP-01: order 6
SHELF-03: enough
DESK-02: order 1
7 units to order
```

The move changed no output, removed a clause and an arm that never ran, and left a `total` that reads as what it is: a sum.

### A move is a change of its own

Make the move a change of its own, with the edition line and the repairs it needed and nothing else, so that a reviewer reads it as a move and not as new behavior. The edition belongs to the package, not to a module: every module of a package moves together, and a store whose code is split into several packages can move them one at a time, each on the day its own tests are ready.

### Which edition to name

The table sums up which edition a package's `una.toml` should name:

:::decide
**Which to use:**

| Your package… | Edition |
| --- | --- |
| Is stable code that you do not want to touch | Keep its edition: every release that lists it in `una --version` serves it |
| Uses loops, maps, `together` or any construct of this tutorial's later chapters | `0.2` |
| Needs a condition on an operation, a locked contract or a boundary | `0.3`, the preview |
| Is new, and should follow the stable rules | `0.2` |
:::

## 14.5 Day-to-day: a shelf-label printer

### What the program must do

Now the program from the start of the chapter. The store prints shelf labels from a stock export. A line that does not parse is left out, a line with no stock gets no label, and a dry run must count the labels without printing any, so that the night shift can check a run before it uses up the label stock. The package is on edition `0.3`, because the dry run's rule is one the checker can then enforce.

### The manifest: the edition and the lock

The manifest names the edition and locks one function's authority:

```toml include="day-to-day/una.toml" title="day-to-day/una.toml"
[package]
name = "labels"
version = "0.1.0"
edition = "0.3"

[run]
entry = "labels"
grants = ["console"]

[contracts]
"labels.print_labels" = ["@printer: Printer[print_label where not dry_run]"]
```

`edition = "0.3"` opts into the preview. `[contracts]` locks the authority of `print_labels`: whatever its header says, it may never print a label where `dry_run` is true. Each key is the qualified name of a public function, and each value lists `uses` clauses as a header writes them. The header may grant less than its lock, never more. A change to that line is a change to `una.toml`, which a reviewer sees in the diff, even when nobody touches the code.

Why both a condition and a lock? The condition makes the verifier check the body against the header. The lock makes the checker hold the header to `una.toml`. Without the lock, a later change could drop `where not dry_run` from the header and add a print without a guard, and the package would still check. With it, that change is U3023 until `una.toml` changes too.

### The kinds, the printer and the parser

These use edition `0.1` and `0.2` constructs only: a record, a sum kind for the failures, a capability, and a parser that fails with `LineError`.

```una include="day-to-day/src/labels.una#L1-L27" title="day-to-day/src/labels.una"
module labels

--- A line of a stock list: a SKU and the units on hand.
pub kind Line
  sku: Text
  units: Int

--- Why a line of a stock export was rejected.
pub kind LineError = Malformed(text: Text) | BadUnits(text: Text)

--- The shelf-label printer.
pub capability Printer
  op print_label(sku: Text, units: Int) -> Unit

--- Reads `"SKU, units"`.
pub parse_line(text: Text) -> Line
  fails LineError
=
  let parts = text.split(on: ",")
  let sku = parts.at(index: 0)
    if none fail Malformed(text)
  let raw = parts.at(index: 1)
    if none fail Malformed(text)
  let units = raw.trim.to_int()
    if none fail BadUnits(text)
  Line(sku: sku.trim, units: units)

```

### Reading an export

`read_lines` keeps the lines that parse. `attempt` keeps each outcome as a `Result`, and a `when` on it decides whether the line is added. On `0.3`, `attempt` must wrap a call that can fail, and `parse_line` can.

```una include="day-to-day/src/labels.una#read_lines" title="day-to-day/src/labels.una"
--- Reads every line of an export; a line that does not parse is left out.
pub read_lines(export: List[Text]) -> List[Line]
=
  let edit lines: List[Line] = []
  for text in export
    let outcome = attempt parse_line(text)
    lines = when outcome
      is Ok(line) -> lines.append(item: line)
      is Err -> lines
  lines
```

### Printing, with a dry run

The header gives `print_label` a condition: `where not dry_run`. Inside the body, the operation is called only under `if not dry_run`, and the verifier proves that the condition holds there. Remove the guard, and the check fails with a counterexample where `dry_run` is true ([An operation outside its condition](#an-operation-outside-its-condition-u5001) shows it).

```una include="day-to-day/src/labels.una#print_labels" title="day-to-day/src/labels.una"
--- Prints a label for every line with stock, and gives how many. A dry run prints nothing.
pub print_labels(lines: List[Line], dry_run: Bool) -> Int
  uses @printer: Printer[print_label where not dry_run]
=
  let edit printed = 0
  for line in lines
    if line.units > 0
      if not dry_run
        @printer.print_label(line.sku, units: line.units)
      printed = printed + 1
  printed
```

The function counts a label whether or not it prints it, so a dry run gives the number of labels a real run would print. The two nested `if` statements have no `else`: an `if` without `else` is a statement that does nothing when its condition is false, which edition `0.2` added along with the loop. The count is a `let edit` binding that the loop updates, as in [chapter 12](/learn/memory-and-concurrency/). The condition is part of the header, so `una contract labels.print_labels` shows it, and every caller sees that a dry run prints nothing without reading the body.

### Running it

`on_console` prints a label as a line of text, which stands in for the label printer here. It is a handler with a `uses` clause of its own, so it may print to the console and nothing else, and `una report .` lists it under `handler authority`. `silent` prints nothing, for the examples. `main` makes a dry run, then a real one, each installing `on_console` for one call with `with`:

```una include="day-to-day/src/labels.una#on_console..main" title="day-to-day/src/labels.una"
--- A printer that writes each label to the console.
handler on_console() for Printer
  uses @console: Console[print]
  op print_label(sku, units) = @console.print("[{sku} | {units} on hand]")

--- A printer that prints nothing, for the examples.
handler silent() for Printer
  op print_label(sku, units) = unit

--- The stock export of this run: one line has no stock, and one does not parse.
export() -> List[Text] = ["LAMP-01, 4", "DESK-02, 0", "CHAIR-09, two", "SHELF-03, 12"]

pub main() -> Unit
  uses @console: Console[print]
=
  let lines = read_lines(export())
  let planned = print_labels(lines, dry_run: true) with @printer = on_console()
  @console.print("dry run: {planned} labels")
  let printed = print_labels(lines, dry_run: false) with @printer = on_console()
  @console.print("printed {printed} labels")
```

`una run .` prints the output shown in [What you'll build](#what-youll-build). The run uses all three editions at once: the kinds and the `when` of `0.1`, the loops, `let edit` and the text functions of `0.2`, and the condition and the lock of `0.3`. The dry run counts two labels and prints none. The real run prints the lamp and the shelf. The desk has no stock, and the chair's line, `CHAIR-09, two`, does not parse, so neither gets a label.

### The whole program

The whole file:

```una include="day-to-day/src/labels.una" title="day-to-day/src/labels.una" caption="the whole program" verified="check, run, test"
module labels

--- A line of a stock list: a SKU and the units on hand.
pub kind Line
  sku: Text
  units: Int

--- Why a line of a stock export was rejected.
pub kind LineError = Malformed(text: Text) | BadUnits(text: Text)

--- The shelf-label printer.
pub capability Printer
  op print_label(sku: Text, units: Int) -> Unit

--- Reads `"SKU, units"`.
pub parse_line(text: Text) -> Line
  fails LineError
=
  let parts = text.split(on: ",")
  let sku = parts.at(index: 0)
    if none fail Malformed(text)
  let raw = parts.at(index: 1)
    if none fail Malformed(text)
  let units = raw.trim.to_int()
    if none fail BadUnits(text)
  Line(sku: sku.trim, units: units)

--- Reads every line of an export; a line that does not parse is left out.
pub read_lines(export: List[Text]) -> List[Line]
=
  let edit lines: List[Line] = []
  for text in export
    let outcome = attempt parse_line(text)
    lines = when outcome
      is Ok(line) -> lines.append(item: line)
      is Err -> lines
  lines

--- Prints a label for every line with stock, and gives how many. A dry run prints nothing.
pub print_labels(lines: List[Line], dry_run: Bool) -> Int
  uses @printer: Printer[print_label where not dry_run]
=
  let edit printed = 0
  for line in lines
    if line.units > 0
      if not dry_run
        @printer.print_label(line.sku, units: line.units)
      printed = printed + 1
  printed

--- A printer that writes each label to the console.
handler on_console() for Printer
  uses @console: Console[print]
  op print_label(sku, units) = @console.print("[{sku} | {units} on hand]")

--- A printer that prints nothing, for the examples.
handler silent() for Printer
  op print_label(sku, units) = unit

--- The stock export of this run: one line has no stock, and one does not parse.
export() -> List[Text] = ["LAMP-01, 4", "DESK-02, 0", "CHAIR-09, two", "SHELF-03, 12"]

pub main() -> Unit
  uses @console: Console[print]
=
  let lines = read_lines(export())
  let planned = print_labels(lines, dry_run: true) with @printer = on_console()
  @console.print("dry run: {planned} labels")
  let printed = print_labels(lines, dry_run: false) with @printer = on_console()
  @console.print("printed {printed} labels")

example "a line that does not parse is left out"
  do read_lines(export()).len
  expect result == 3

example "a dry run counts the labels and prints none"
  given @printer = silent()
  do print_labels(read_lines(export()), dry_run: true)
  expect result == 2
  expect not performed @printer.print_label

example "a run prints a label for each line with stock"
  given @printer = silent()
  do print_labels(read_lines(export()), dry_run: false)
  expect result == 2
  expect performed @printer.print_label
```

## 14.6 Testing it

### Three examples on the export of `main`

The examples check the parser and both kinds of run, on the same export that `main` uses, so a reader can compare their numbers with the program's output. The two runs use `silent`, so they print nothing, and they check what was performed:

```una include="day-to-day/src/labels.una#L72-L86" title="day-to-day/src/labels.una" caption="the examples"
example "a line that does not parse is left out"
  do read_lines(export()).len
  expect result == 3

example "a dry run counts the labels and prints none"
  given @printer = silent()
  do print_labels(read_lines(export()), dry_run: true)
  expect result == 2
  expect not performed @printer.print_label

example "a run prints a label for each line with stock"
  given @printer = silent()
  do print_labels(read_lines(export()), dry_run: false)
  expect result == 2
  expect performed @printer.print_label
```

### A plain `dry_run` and the calls `silent` records

The examples pass `dry_run` as a plain `true` or `false`. A caller has nothing to prove about it: the condition is proven once, inside `print_labels`, for every value of `dry_run`, so the examples only check behavior. `silent` answers every `print_label` with `unit`, and the trace of each example records the calls, which `expect performed` and `expect not performed` read.

### The proof and the examples

The proof and the examples cover different ground. The verifier proves, for every list and every call, that a label is printed only when `dry_run` is false, and the lock in `una.toml` keeps that rule from being dropped. The example "a dry run counts the labels and prints none" checks the same rule on one list, with `expect not performed`, and also checks the count, which no condition states. After an upgrade of `una` to a later `0.3.x` release, rerun both: a stricter rule can only add obligations or errors, and the examples catch a change in behavior.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L6"
example labels "a line that does not parse is left out" ... ok
example labels "a dry run counts the labels and prints none" ... ok
example labels "a run prints a label for each line with stock" ... ok

3 examples: 3 passed, 0 failed
```

## 14.7 Common mistakes

The first two mistakes are changes to the edition `0.1` stock list of [section 14.1](#s14-1). The others are changes to the day-to-day program.

### Interpolating a list in edition `0.1` (U2001)

:::mistake
Print the list as it is:

```diff include="steps/01-edition-0-1..mistakes/1:src/shelf.una" context="1" title="src/shelf.una"
--- a/src/shelf.una
+++ b/src/shelf.una
@@ -15 +15,2 @@
   @console.print("{lines.len} lines, {total(lines)} units")
+  @console.print("{lines}")
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U2001] Error: interpolation converts `Int`, `Bool` and `Text` to text, and this value is `List[Line]`
```

*Why:* edition `0.1` interpolates only `Int`, `Bool` and `Text`.

*Fix:* interpolate the fields you want, or move the package to `0.2`, which interpolates any value that `==` compares, except a `Hashed`. See [U2001](/docs/errors/U2001/).
:::

### Letting `una fix` rename a keyword (U0103)

:::mistake
Write the total with `let edit` and `for` in edition `0.1`:

```diff include="steps/01-edition-0-1..mistakes/2:src/shelf.una" context="1" title="src/shelf.una"
--- a/src/shelf.una
+++ b/src/shelf.una
@@ -8,3 +8,8 @@
 --- The units of every line, added up.
-total(lines: List[Line]) -> Int = lines.fold(initial: 0, step: fn(sum, line) -> sum + line.units)
+total(lines: List[Line]) -> Int
+=
+  let edit sum = 0
+  for line in lines
+    sum = sum + line.units
+  sum
 
```

```text include="mistakes/2/expected/rendered.txt"
[U0103] Error: `edit` is reserved for v0.2 (memory model)
    ╭─[ src/shelf.una:11:7 ]
    │
 11 │   let edit sum = 0
    │       ──┬─
    │         ╰─── `edit` is reserved for v0.2 (memory model)
    │
    │ Help: repair 1: rename it to `the_edit`; edit src/shelf.una:11:7..11:11 to "the_edit"
    │
    │ Note: run `una explain U0103` for an explanation
────╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

The repair is meant for a program that uses `edit` as a name, and `una fix --dry-run .` lists it:

```text include="mistakes/2/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/shelf.una:11:7 U0103 rename it to `the_edit`
```

*Why:* in edition `0.1`, `edit` is a reserved word, not a keyword, so the checker reads it as a name that must change. Applied here, the rename gives `let the_edit sum = 0`, which does not parse.

*Fix:* change `edition` in `una.toml` to `"0.2"`. Do not apply the rename: offering it here is a known issue of una 0.3.15. See [U0103](/docs/errors/U0103/).
:::

### Moving a package back (U0101, U7002)

:::mistake
Set the day-to-day program's edition to `0.2`:

```diff include="day-to-day..mistakes/3:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -3,3 +3,3 @@
 version = "0.1.0"
-edition = "0.3"
+edition = "0.2"
 
```

```text include="mistakes/3/expected/rendered.txt"
[U0101] Error: unexpected keyword `where`, expected `,` or `]`
    ╭─[ src/labels.una:41:38 ]
    │
 41 │   uses @printer: Printer[print_label where not dry_run]
    │                                      ──┬──
    │                                        ╰──── unexpected keyword `where`, expected `,` or `]`
    │
    │ Note: run `una explain U0101` for an explanation
────╯
[U7002] Error: unknown table [contracts] in una.toml
    ╭─[ una.toml:10:2 ]
    │
 10 │ [contracts]
    │  ────┬────
    │      ╰────── unknown table [contracts] in una.toml
    │
    │ Note: run `una explain U7002` for an explanation
────╯
```

*Why:* both constructs exist only in edition `0.3`. In `0.2`, the condition is a syntax error and `[contracts]` is an unknown table.

*Fix:* keep the edition the package's constructs need. See [U0101](/docs/errors/U0101/) and [U7002](/docs/errors/U7002/).
:::

### An operation outside its condition (U5001)

:::mistake
Remove the guard in `print_labels`:

```diff include="day-to-day..mistakes/4:src/labels.una" context="1" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -45,4 +45,3 @@
     if line.units > 0
-      if not dry_run
-        @printer.print_label(line.sku, units: line.units)
+      @printer.print_label(line.sku, units: line.units)
       printed = printed + 1
```

```text include="mistakes/4/expected/rendered.txt#L1,L12-L18"
[U5001] Error: `@printer.print_label` may run where `not dry_run` is not proven
    │ Help 1: repair 1: guard the operation with `if not dry_run`
    │
    │ Help 2: repair 2: add `requires not dry_run` to the enclosing function; its callers then prove it
    │
    │ Note 1: obligation ob-e03b3850e838 (effect_condition) is refuted: not dry_run
    │
    │ Note 2: counterexample: dry_run = true, line = Line#0, line.sku = Text#0, line.units = 1, lines = List#0, lines.len = 1, printed = 0
```

*Why:* the header lets `print_label` run only where `not dry_run` holds, and the verifier found a run where it does not: `dry_run = true` with one line in stock.

*Fix:* the first repair, `if not dry_run`. The second repair, `requires not dry_run`, would forbid every dry run. See [U5001](/docs/errors/U5001/).
:::

### Dropping a locked condition (U3023)

:::mistake
Remove the condition from the header:

```diff include="day-to-day..mistakes/5:src/labels.una" context="1" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -40,3 +40,3 @@
 pub print_labels(lines: List[Line], dry_run: Bool) -> Int
-  uses @printer: Printer[print_label where not dry_run]
+  uses @printer: Printer[print_label]
 =
```

```text include="mistakes/5/expected/rendered.txt#L1-L12,L16-L18"
[U3023] Error: the header of `print_labels` lets `@printer.print_label` run where `not dry_run` does not hold, which `una.toml` locks
    ╭─[ src/labels.una:41:26 ]
    │
 41 │   uses @printer: Printer[print_label]
    │                          ─────┬─────
    │                               ╰─────── the header of `print_labels` lets `@printer.print_label` run where `not dry_run` does not hold, which `una.toml` locks
    │
    ├─[ una.toml:11:26 ]
    │
 11 │ "labels.print_labels" = ["@printer: Printer[print_label where not dry_run]"]
    │                          ─────────────────────────┬────────────────────────
    │                                                   ╰────────────────────────── lock
    │ Note 1: obligation ob-35b380cf8520 (contract_lock) is refuted: not dry_run
    │
    │ Note 2: counterexample: dry_run = true
```

*Why:* the lock in `una.toml` says how much `print_labels` may ever do, and the header now grants more: printing in a dry run, as the counterexample `dry_run = true` shows.

*Fix:* restore the condition. To really change the rule, change the lock in `una.toml` too, where a reviewer sees it. See [U3023](/docs/errors/U3023/).
:::

## 14.8 Exercises

Each exercise starts from `exercises/N/start` and has an example that fails there until the exercise is done. Run `una fmt .` before `una check .`.

### Exercise 1: move a package to `0.2`

::::exercise
Someone added `low_stock` to the edition `0.1` stock list, with a loop, and an example for it. The package no longer checks. Make it check, and keep the code as it is. The start package's new function and example:

```una include="exercises/1/start/src/shelf.una#low_stock" title="exercises/1/start/src/shelf.una"
--- The SKUs of the lines with fewer than `limit` units, in the order of the list.
low_stock(lines: List[Line], limit: Int) -> List[Text]
=
  let edit found: List[Text] = []
  for line in lines
    if line.units < limit
      found = found.append(item: line.sku)
  found
```

```una include="exercises/1/start/src/shelf.una#L26-L28" title="exercises/1/start/src/shelf.una"
example "the lines below the limit are low on stock"
  do low_stock([Line(sku: "LAMP-01", units: 4), Line(sku: "DESK-02", units: 1)], limit: 2)
  expect result == ["DESK-02"]
```

```text include="exercises/1/start/expected/diagnostics.txt"
error U0103 at src/shelf.una:14:7: `edit` is reserved for v0.2 (memory model)
```

:::hint
*Hint:* the code is right. Read [Letting `una fix` rename a keyword](#letting-una-fix-rename-a-keyword-u0103) before you run `una fix`.
:::

Check your answer with `una check .`, then `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Change the edition, and nothing else:

```diff include="exercises/1/start..exercises/1/answer:una.toml" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -1,7 +1,7 @@
 [package]
 name = "shelf"
 version = "0.1.0"
-edition = "0.1"
+edition = "0.2"
 
 [run]
 entry = "shelf"
```
:::
::::

### Exercise 2: a restock run

::::exercise
The night shift wants labels for the lines that are low on stock, so they can restock them first. Write the body of `print_low`: like `print_labels`, but for the lines with fewer than `limit` units, with the same dry run. The start package has the header with its condition, a stub body, and two examples:

```una include="exercises/2/start/src/labels.una#print_low" title="exercises/2/start/src/labels.una"
--- Prints a label for every line with fewer than `limit` units, and gives how many, for a
--- restock run. A dry run prints nothing. Exercise 2: write the body.
pub print_low(lines: List[Line], limit: Int, dry_run: Bool) -> Int
  uses @printer: Printer[print_label where not dry_run]
=
  0
```

```una include="exercises/2/start/src/labels.una#L95-L105" title="exercises/2/start/src/labels.una"
example "a restock run prints the lines below the limit"
  given @printer = silent()
  do print_low(read_lines(export()), limit: 5, dry_run: false)
  expect result == 2
  expect performed @printer.print_label

example "a restock dry run prints nothing"
  given @printer = silent()
  do print_low(read_lines(export()), limit: 5, dry_run: true)
  expect result == 2
  expect not performed @printer.print_label
```

:::hint
*Hint:* start from the body of `print_labels`. If you leave out the guard, `una check .` reports where.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Replace the body:

```diff include="exercises/2/start..exercises/2/answer:src/labels.una" context="1" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -88,3 +88,3 @@
 --- Prints a label for every line with fewer than `limit` units, and gives how many, for a
---- restock run. A dry run prints nothing. Exercise 2: write the body.
+--- restock run. A dry run prints nothing.
 pub print_low(lines: List[Line], limit: Int, dry_run: Bool) -> Int
@@ -92,3 +92,9 @@
 =
-  0
+  let edit printed = 0
+  for line in lines
+    if line.units < limit
+      if not dry_run
+        @printer.print_label(line.sku, units: line.units)
+      printed = printed + 1
+  printed
 
```
:::
::::

### Exercise 3: a summary on every run

::::exercise
The printer gains a second operation, `print_summary`, which prints one line at the end of a run. The summary must be printed on every run, a dry run included, while labels stay forbidden in a dry run. The start package adds the operation to `Printer`:

```una include="exercises/3/start/src/labels.una#Printer" title="exercises/3/start/src/labels.una"
--- The shelf-label printer. `print_summary` prints a line at the end of a run, on paper.
pub capability Printer
  op print_label(sku: Text, units: Int) -> Unit
  op print_summary(labels: Int) -> Unit
```

It adds it to both handlers:

```una include="exercises/3/start/src/labels.una#on_console..silent" title="exercises/3/start/src/labels.una"
--- A printer that writes each label to the console.
handler on_console() for Printer
  uses @console: Console[print]
  op print_label(sku, units) = @console.print("[{sku} | {units} on hand]")
  op print_summary(labels) = @console.print("{labels} labels")

--- A printer that prints nothing, for the examples.
handler silent() for Printer
  op print_label(sku, units) = unit
  op print_summary(labels) = unit
```

And it adds this example:

```una include="exercises/3/start/src/labels.una#L92-L96" title="exercises/3/start/src/labels.una"
example "a dry run prints the summary, and no label"
  given @printer = silent()
  do print_labels(read_lines(export()), dry_run: true)
  expect performed @printer.print_summary
  expect not performed @printer.print_label
```

:::hint
*Hint:* the header decides which operations may run, and under which condition. Once the code checks on its own, read what `una check .` says about `una.toml`.
:::

After the change to the code alone, `una check .` reports:

```text include="exercises/3/unlocked/expected/rendered.txt#L1"
[U3023] Error: the header of `print_labels` lets `@printer.print_summary` run, which its lock in `una.toml` does not list
```

Check your answer with `una check .`, then `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Change the header and the body:

```diff include="exercises/3/start..exercises/3/answer:src/labels.una" context="1" title="src/labels.una"
--- a/src/labels.una
+++ b/src/labels.una
@@ -39,6 +39,6 @@
 
---- Prints a label for every line with stock, and gives how many. A dry run prints nothing.
---- Exercise 3: print the summary at the end of every run, a dry run included.
+--- Prints a label for every line with stock, and gives how many. A dry run prints no label,
+--- and every run prints the summary.
 pub print_labels(lines: List[Line], dry_run: Bool) -> Int
-  uses @printer: Printer[print_label where not dry_run]
+  uses @printer: Printer[print_label where not dry_run, print_summary]
 =
@@ -50,2 +50,3 @@
       printed = printed + 1
+  @printer.print_summary(printed)
   printed
```

and the lock, which a reviewer sees:

```diff include="exercises/3/start..exercises/3/answer:una.toml" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -8,4 +8,4 @@
 grants = ["console"]
 
 [contracts]
-"labels.print_labels" = ["@printer: Printer[print_label where not dry_run]"]
+"labels.print_labels" = ["@printer: Printer[print_label where not dry_run, print_summary]"]
```
:::
::::

## 14.9 Recap and reference

### For agents

:::agents
An edition shows up in two places of `una --json` output: a construct of a later edition gives U0103 (a reserved word) or U0101 (a syntax error) at the construct, and a table of a later edition gives U7002 at `una.toml`. To move a package, change only `edition` in `una.toml`, run `una --json check .`, apply what `una fix .` applies, and repair the rest from each diagnostic's repairs. Never apply a U0103 rename to `edit`, `take` or `together` used as a keyword: change the edition instead. The compact rule: *an edition is a line of `una.toml`; a later edition adds constructs and only tightens rules.*
:::

### Recap

:::recap
- `[package] edition` names a package's edition. A single file has edition `0.1`.
- Upgrading `una` keeps what each stable edition accepts and rejects, except to fix a soundness or security error.
- Editions are cumulative: a later edition adds constructs and tightens rules, and never removes a construct.
- `0.2` adds loops, `let edit`, `edit` and `take`, `together`, maps, JSON and more.
- `0.3` is a preview: conditions on operations, locked contracts, boundaries, and no dead failure handling. It may get stricter in a later `0.3.x`.
- To move a package: change the edition, `una check .`, `una fix .`, repair the rest, `una test .`.
- Never let `una fix` rename a keyword of a later edition; change the edition instead.
:::

### Reference

:::reference
- Editions: [editions](/docs/editions/), [moving from 0.1 to 0.2](/docs/editions/migrate-0.1-to-0.2/), [`[package] edition`](/docs/configure/package/edition/), [`[boundaries]`](/docs/configure/boundaries/)
- Construct pages: [`let edit`](/docs/language/control-flow/let-edit/), [`for`](/docs/language/control-flow/for/), [`together`](/docs/language/control-flow/together/), [`uses`](/docs/language/capabilities/uses/), [`if error`](/docs/language/errors/if-error/), [`attempt`](/docs/language/errors/attempt/), [constraints on generics](/docs/language/types/constraints/)
- Command line: [`una check`](/docs/cli/check/), [`una fix`](/docs/cli/fix/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U0103](/docs/errors/U0103/), [U2001](/docs/errors/U2001/), [U3023](/docs/errors/U3023/), [U3025](/docs/errors/U3025/), [U3026](/docs/errors/U3026/), [U5001](/docs/errors/U5001/), [U7002](/docs/errors/U7002/)
- Specification: [project files and editions](/docs/spec/13-diagnostics-and-abi/), [lexical structure, reserved words](/docs/spec/01-lexical-structure/), [memory model](/docs/spec/17-memory-model/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [errors](/docs/spec/06-errors/)
:::
