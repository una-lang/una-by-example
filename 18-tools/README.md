---
learn: "18"
title: Tools
editions: ["0.2"]
codes: [U0001, U0101, U1001, U1006, U2004, U3001, U5001, U7001]
time: 55
builds: Sale price tags for a store, taken through every check before a release
prerequisites: ["5", "12", "14"]
template: 2
nav: ["Check, format and fix", "Reading a diagnostic", "Obligations, contracts, traces", "The build report", "Running, testing and building", "Day-to-day: sale price tags", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 18 Tools


Writing a program is half of the work. The other half is finding out whether it is right: reading what the checker reports, letting it repair what it can, seeing what it proved and what the program may do, and finally running, testing and shipping it. In Una all of that is one command, `una`, and each of its subcommands prints a text for people, or with `--json` a document for programs. This chapter takes a small pricing package through the commands you use every day, in the order you use them, and explains what each one tells you and why it is built that way.

## What you'll build

:::build
Price tags for a sale at a store. Each tag shows a product's price and its sale price, which must never fall below what the store paid for the product, and a SKU the catalog does not list gets a tag that says so:

```text include="day-to-day/expected/output.txt"
LAMP-01  19.90 now 13.93
DESK-02  129.00 now 110.00
CHAIR-09  not in the catalog
```

You will learn to:

- run the loop of `una check`, `una fmt` and `una fix`, and know what `una fix` will and will not change;
- read a diagnostic: its code, its places, its repairs and its counterexample, as text and as JSON;
- list what the verifier proved with `una obligations`, `una contract` and `una trace`;
- read the build report, which says what the package may do and what it trusts;
- run, test and build a native executable, and connect an editor with `una lsp`.
:::

## Why it works this way

A **compiler**, the program that checks code and turns it into something a machine runs, often prints only a wall of text for a person. A **script**, a file of commands run one after another, an editor or an **agent**, a program built on an AI model that writes code, then parses messages never meant to be parsed, and breaks when one changes. And a compiler that only says "error" leaves the reader to work out the repair, even when the compiler knew exactly what it was.

Una's tools are built around three rules:

:::steps
1. **Every problem is a diagnostic with a code.** The code has a page and an explanation in the binary, `una explain U2004`. The text of a message may improve from release to release, and the code stays.
2. **Every command has two renderings of one result.** By default a command prints for people. With `--json` it prints the same content as one JSON document, data for programs ([section 18.1](#s18-1) shows one), named by its **schema**, the name of its shape, such as `una.diagnostics/1`. A schema keeps its version when keys are added, and changes it when a key is removed or changes meaning.
3. **A repair is data.** A diagnostic lists its repairs, ranked. A repair whose change is exact carries the edit itself, and `una fix` applies those edits, and only those that keep what the program is allowed to do.
:::

The checks also give more than a yes or a no: the obligations, a function's full contract and the build report show a reviewer what was proven, not only that the check passed.

> [!KEY]
> Whatever `una check` reports, `una explain` explains, `--json` gives as data, and `una fix` repairs when the edit is exact and widens nothing.

## 18.1 Check, format and fix


### What a tool is

Every chapter so far has used `una` the same way: you type a line such as `una check .` in a terminal, and una answers. A **command** is one such line, as [chapter 1](/learn/hello/#s1-1) showed: the name of a program, `una`, then words that tell it what to do. Those words are the command's **arguments**:

- The first word after `una`, such as `check`, `run` or `test`, picks one of una's jobs. Each job is a **subcommand**; this chapter calls them commands too, as in "the command `una check`".
- A word that starts with `--`, such as `--json` or `--dry-run`, is a **flag**: a switch that changes how the command works. Some flags take a value, as `--tier 0` does.
- The last word, `.`, is the path of the package to work on. `.` means "the directory I am in". A few commands take a name instead of a path, such as `una explain U2004`, which takes a diagnostic's code.

Together, the commands of `una` are its **tools**. Like the saw, the plane and the square on a carpenter's bench, each does one job around your code.

When a command finishes, it leaves two things besides the text you read:

- **Two output streams.** A program prints to two places that the terminal shows together. **stdout**, the standard output, carries the result you asked for: what the program prints, a report, a listing. **stderr**, the standard error, carries messages about problems, such as diagnostics. A script can keep the two apart, and save the result to a file while the problems show on the screen.
- **An exit code.** A number that the terminal does not print and that says how the command went: 0 when it succeeded, another number when it did not ([section 18.5](#s18-5) lists them).

### The commands of `una`

This chapter covers every command this book uses, in the order you use them:

| Command | What it does | Section |
| --- | --- | --- |
| `una --version` | Prints the version, the editions and the Z3 version | [chapter 1](/learn/hello/#s1-1) |
| `una check .` | Looks for mistakes, without running anything | [18.1](#s18-1) |
| `una fmt .` | Rewrites the code in canonical form | [18.1](#s18-1) |
| `una fix .` | Applies the exact repairs, then formats | [18.1](#s18-1) |
| `una explain U1001` | Explains a diagnostic's code | [18.2](#s18-2) |
| `una obligations .` | Lists every fact the verifier had to prove | [18.3](#s18-3) |
| `una contract NAME` | Prints a function's full header | [18.3](#s18-3) |
| `una trace NAME` | Follows a requirement to the code | [18.3](#s18-3) |
| `una report .` | Prints the build report | [18.4](#s18-4) |
| `una run .` | Checks, then runs `main` | [18.5](#s18-5) |
| `una test .` | Checks, then runs every example | [18.5](#s18-5) |
| `una build .` | Checks, then builds an executable | [18.5](#s18-5) |
| `una lsp` | Serves an editor | [18.1](#s18-1) |

Each example of this chapter is a package, made as [chapter 2](/learn/numbers/#each-step-is-a-package) explains, and the chapter's download, `18-tools.tar.gz`, holds them all. Run every command in the package's directory.

### Why you check before you run

A mistake in a program is normal: everyone makes them while writing code. What matters is when you find out.


Here is a receipt line written by someone used to another language. It has two habits from there: an `=` at the end of the header, which is how some languages open a body, and a second argument without its label. An argument's label is the `name:` before it in a call ([chapter 6](/learn/functions/#s6-1)), not the security label of [chapter 17](/learn/information-flow/).

```una include="steps/01-fix/src/receipt.una" title="steps/01-fix/src/receipt.una"
module receipt

--- One line of a receipt: the units, the SKU and the line's total in cents.
line_text(units: Int, sku: Text, cents: Int) -> Text =
  "{units} x {sku}  {cents}"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(line_text(2, "LAMP-01", cents: 3980))
```

In many languages you would learn about such mistakes only when the program runs, or never, if no test reaches the line. una reads the whole package without running anything, and reports what is wrong first:

```sh
una check .
```

```text include="steps/01-fix/expected/rendered.txt"
[U0101] Error: unexpected end of line, expected an expression
   ╭─[ src/receipt.una:4:55 ]
   │
 4 │ line_text(units: Int, sku: Text, cents: Int) -> Text =
   │                                                       ┬
   │                                                       ╰── unexpected end of line, expected an expression
   │
   │ Help: repair 1: put `=` on a line of its own: a function whose body is a block has the long form, the header, `=`, then the indented body; edit src/receipt.una:4:1..5:1 to "line_text(units: Int, sku: Text, cents: Int) -> Text\n=\n"
   │
   │ Note: run `una explain U0101` for an explanation
───╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

The checker reports one problem, a **syntax error**: text that breaks the grammar of the language, the rules for how words and symbols may follow each other. Here it is U0101, a line that ends where an expression was expected. Before anything else, una **parses** each file: it works out which part of the text is a header, a body or a call. A file that does not parse cannot be checked further, so the missing label is not reported yet. The `Help` line holds a repair with an exact edit, and the last line counts the diagnostics that `una fix` can repair for you. The rest of this section shows the three commands of this loop: `una check` finds the problems, `una fmt` lays the code out, and `una fix` applies the exact repairs.

### How to write the check loop

Commands that work on a package take its path, `.`, last; `una trace`, `una contract` and `una explain` take a name instead. Flags go between the command's name and the path. Two flags, `--json` and `--color`, are global: they work with every command and may go anywhere on the line, and this book writes them right after `una`.

#### `una check .`

`una check .` checks the package and changes nothing. It checks in **tiers**, two passes of increasing cost:

- **Tier 0** checks the syntax, the names, the types, the capabilities and the information-flow labels ([chapter 17](/learn/information-flow/)), and that every file is in canonical form. It needs no solver and answers quickly.
- **Tier 1** adds the verifier ([chapter 5](/learn/contracts/#what-the-verifier-is)), which proves the contracts, refinements and divisions with Z3, a **solver**: a program that searches for values that break a fact, and proves the fact when there are none. It runs only when tier 0 reports nothing.

When the package is right, `una check .` prints nothing and exits with code 0. Fix the label by hand, put the body on the header's line, and that is what happens: the package of the next step checks clean. The same answer for a program is one JSON document with an empty list:

```sh
una --json check .
```

```text include="steps/02-fixed/expected/commands/json.txt"
$ una --json check .
{"schema":"una.diagnostics/1","diagnostics":[],"fixable":0}
```

**JSON** is a plain text format for data that programs exchange: `{` and `}` hold named values, each a key in quotes, a `:` and its value, and `[` and `]` hold a list. `schema` names the shape of the document, `diagnostics` is the list of problems, empty here, and `fixable` counts the problems `una fix` could repair. [Section 18.2](#s18-2) reads a full diagnostic.

#### `una check --tier 0 .`

`--tier 0` stops after tier 0 and skips the solver, so it answers in a moment, as you want while you type. It does not prove anything: a promise the code breaks, such as the one of [section 18.2](#s18-2), passes `una check --tier 0 .` and fails `una check .`. Run the full check before you consider a change done.

#### `una fmt .` and `una fmt --check .`

**Canonical form** is the one layout Una accepts for any code: indentation, spaces, line breaks and the order of a few parts. Since all Una code has one layout, no review ever argues about it. `una fmt .` rewrites every file of the package into it. `una fmt --check .` writes nothing and reports each place that differs, as the diagnostic U7001. `una check .` reports U7001 too, so a file out of canonical form never passes the check.

This step has the right label, but the body of a one-line function sits on its own line. The change from the previous step is shown as a **diff**: a line that starts with `-` was removed, a line with `+` was added, and the rest is unchanged context:

```diff include="steps/02-fixed..steps/03-layout:src/receipt.una" title="src/receipt.una"
--- a/src/receipt.una
+++ b/src/receipt.una
@@ -1,7 +1,9 @@
 module receipt
 
 --- One line of a receipt: the units, the SKU and the line's total in cents.
-line_text(units: Int, sku: Text, cents: Int) -> Text = "{units} x {sku}  {cents}"
+line_text(units: Int, sku: Text, cents: Int) -> Text
+=
+  "{units} x {sku}  {cents}"
 
 pub main() -> Unit
   uses @console: Console[print]
```

```text include="steps/03-layout/expected/rendered.txt"
[U7001] Error: lines 4 to 6 are not in canonical form
   ╭─[ src/receipt.una:4:1 ]
   │
 4 │ ╭─▶ line_text(units: Int, sku: Text, cents: Int) -> Text
   ┆ ┆
 6 │ ├─▶   "{units} x {sku}  {cents}"
   │ │
   │ ╰────────────────────────────────── lines 4 to 6 are not in canonical form
   │
   │     Help: repair 1: rewrite in canonical form, as `una fmt` does; edit src/receipt.una:4:1..7:1 to "line_text(units: Int, sku: Text, cents: Int) -> Text = \"{units} x {sku}  {cents}\"\n"
   │
   │     Note: run `una explain U7001` for an explanation
───╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

The arrows on the left mark lines 4 to 6, out of form. The `Help` line is the edit `una fmt .` makes: a function with no clauses (no `uses`, `requires`, `ensures` or `fails`) whose body is one plain line (no `when`, no `if` with blocks, no `with` or handling clause) ends on the header line, after `=`. `main`, which has a `uses` clause, keeps the long form. The `┆` in the margin stands for a line the excerpt leaves out.

Spaces matter too: spaces inside the parentheses of a call are out of canonical form:

```diff include="steps/06-hello..steps/07-layout-2:src/hello.una" title="src/hello.una"
--- a/src/hello.una
+++ b/src/hello.una
@@ -4,4 +4,4 @@
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print("The store is open")
+  @console.print( "The store is open" )
```

```text include="steps/07-layout-2/expected/rendered.txt#L1,L8"
[U7001] Error: line 7 is not in canonical form
   │ Help: repair 1: rewrite in canonical form, as `una fmt` does; edit src/hello.una:7:1..8:1 to "  @console.print(\"The store is open\")\n"
```

The `Help` line holds the line as canonical form writes it, and `una fmt .` makes that edit.

#### `una fix --dry-run .` and `una fix .`

`una fix .` applies the exact repairs that the diagnostics carry, then formats every file, then checks the package once more. `una fix --dry-run .` shows what `una fix .` would change, and writes nothing. On the receipt line of the first step:

```sh
una fix --dry-run .
```

```text include="steps/01-fix/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/receipt.una:4:1 U0101 put `=` on a line of its own: a function whose body is a block has the long form, the header, `=`, then the indented body
fixed src/receipt.una:11:31 U2004 label it `sku`
```

Each line is one repair: the word `fixed`, the place, the code and what the repair does. The second repair is the missing label, which `una check .` had not reported yet: after the first repair, the file parses, and the next round finds it. Running `una fix .` gives the package that the next step holds:

```diff include="steps/01-fix..steps/02-fixed:src/receipt.una" title="src/receipt.una"
--- a/src/receipt.una
+++ b/src/receipt.una
@@ -1,10 +1,9 @@
 module receipt
 
 --- One line of a receipt: the units, the SKU and the line's total in cents.
-line_text(units: Int, sku: Text, cents: Int) -> Text =
-  "{units} x {sku}  {cents}"
+line_text(units: Int, sku: Text, cents: Int) -> Text = "{units} x {sku}  {cents}"
 
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print(line_text(2, "LAMP-01", cents: 3980))
+  @console.print(line_text(2, sku: "LAMP-01", cents: 3980))
```

```text include="steps/02-fixed/expected/output.txt"
2 x LAMP-01  3980
```

#### `--json` and `--color`

The two global flags of [How to write the check loop](#how-to-write-the-check-loop):

- `una --json check .` prints one JSON document on stdout instead of the text for people, and nothing on stderr, except a usage error (exit code 2) or an internal error (exit code 3).
- `una --color never check .` prints without colors, as the outputs of this book are. `auto`, the default, uses colors when the output goes to a terminal, and `always` uses them everywhere.

### Habits from other languages

People who come to Una from other languages bring their habits, and the checker knows the common ones. When a syntax error has the shape of another language's form, the first repair names Una's form, and carries an exact edit when the rewrite is certain. Two more habits, in one function each: an `if` with `then` whose `else` is on the next line, and a name that starts with `_`, which some languages use for "unused":

```una include="steps/04-habits/src/receipt.una" title="steps/04-habits/src/receipt.una"
module receipt

--- The total of a line in cents.
line_cents(units: Int, unit_cents: Int) -> Int = units * unit_cents

--- A label for a line: "bulk" from 10 units on.
size_label(units: Int) -> Text
=
  if units >= 10 then "bulk"
  else "single"

pub main() -> Unit
  uses @console: Console[print]
=
  let _total = line_cents(2, unit_cents: 1990)
  @console.print("{size_label(2)} {_total}")
```

```text include="steps/04-habits/expected/rendered.txt"
[U0101] Error: unexpected end of line, expected `else`
   ╭─[ src/receipt.una:9:29 ]
   │
 9 │   if units >= 10 then "bulk"
   │                             ┬
   │                             ╰── unexpected end of line, expected `else`
   │
   │ Help 1: repair 1: write the `if` with blocks: `if` and its condition, the indented branch, `else`, then the indented branch; edit src/receipt.una:9:1..11:1 to "  if units >= 10\n    \"bulk\"\n  else\n    \"single\"\n"
   │
   │ Help 2: repair 2: an `if` with `then` needs `else`; to fail early, make the rest of the body its `else` branch, as in `if x < 0 then fail Broke else x`, or use the block form, whose `else` block holds the rest
   │
   │ Note: run `una explain U0101` for an explanation
───╯
[U0001] Error: invalid character `_`; names start with a letter
    ╭─[ src/receipt.una:15:7 ]
    │
 15 │   let _total = line_cents(2, unit_cents: 1990)
    │       ┬
    │       ╰── invalid character `_`; names start with a letter
    │
    │ Help: repair 1: rename `_total` to `total2` in its declaration: a name starts with a letter; edit src/receipt.una:15:7..16:42 to "total2 = line_cents(2, unit_cents: 1990)\n  @console.print(\"{size_label(2)} {total2"
    │
    │ Note: run `una explain U0001` for an explanation
────╯
[U0001] Error: invalid character `_`; names start with a letter
    ╭─[ src/receipt.una:16:36 ]
    │
 16 │   @console.print("{size_label(2)} {_total}")
    │                                    ┬
    │                                    ╰── invalid character `_`; names start with a letter
    │
    │ Help: repair 1: rename `_total` to `total2` in its declaration: a name starts with a letter; edit src/receipt.una:15:7..16:42 to "total2 = line_cents(2, unit_cents: 1990)\n  @console.print(\"{size_label(2)} {total2"
    │
    │ Note: run `una explain U0001` for an explanation
────╯
3 of 3 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

Read each one by its first line:

:::steps
1. **U0101 at 9:29.** An `if` with `then` on one line must end with its `else` on that line. The repair rewrites the `if` in the block form: the condition, the indented branch, `else`, the indented branch.
2. **U0001 at 15:7 and 16:36.** A name starts with a letter. Both diagnostics carry the same repair, which renames the binding and every use of it to `total2`, a name used nowhere else in the function.
:::

Neither is reported as a warning to ignore: Una has one syntax, and the other form is an error. `una fix --dry-run .` lists the two repairs it would apply, one per edit; the rename counts once, since both diagnostics carry the same edit:

```text include="steps/04-habits/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/receipt.una:9:1 U0101 write the `if` with blocks: `if` and its condition, the indented branch, `else`, then the indented branch
fixed src/receipt.una:15:7 U0001 rename `_total` to `total2` in its declaration: a name starts with a letter
```

`total2` is correct, but not the name you would choose. `una fix` cannot know the meaning of a name, so read the result, and rename by hand when a better name exists.

### How the check loop behaves

#### What one check reports

- **Every problem in one pass.** `una check .` reports all the problems it finds, not only the first: the receipt of [Habits from other languages](#habits-from-other-languages) gave three at once ([section 18.2](#s18-2) shows more).
- **Except after a syntax error.** A file that does not parse is not checked for names, types or proofs, so its other problems appear once it parses, as the missing label of the first step did.
- **In a fixed order.** Diagnostics are sorted by file, then position, then code. The same package gives the same output on every run and every machine.

#### How `una fix` works

`una fix .` works in **rounds**. Each round checks the package, takes the first repair of each diagnostic when that repair has an exact edit, and applies the edits that do not overlap. The next round checks again, which is how the first step's label was found after the syntax repair. Each `fixed` line gives its place in the file as that round left it, so the label's line moved from 10 to 11. The rounds stop when one finds nothing more to apply, when the text comes back to an earlier state, or after 16 rounds. Then `una fix .` formats every file that parses, writes each changed file once, and checks the package a last time. The format step prints no `fixed` line: only the repairs of the rounds get one. What it could not repair stays, and it reports those diagnostics on stderr, as `una check .` would.

### What `una fix` applies, and what it leaves to you

What `una fix` applies is narrow on purpose:

| `una fix` applies | `una fix` leaves to you |
| --- | --- |
| The first repair of a diagnostic, when it carries an exact edit | A repair without an edit, such as a guard for a refuted proof |
| Edits to the package's modules | Any change to `una.toml` or `verification.lock` |
| Edits that keep what the code may do | An edit that adds a `uses`, makes a declaration `pub` or adds a grant |
| Formatting of every file that parses | A repair marked as an escape, such as `checked`, which gives up a proof ([Repairs that cost a guarantee](#repairs-that-cost-a-guarantee)) |

The right column holds every change that needs a decision: what a function is meant to compute, what the program may do, what it trusts. `una fix --dry-run .` names each repair with an edit that it skips, and why: [A capability that is not there](#a-capability-that-is-not-there-u3001), in Common mistakes, shows it for a repair that would widen what a function may do.

### In an editor: `una lsp`

An **editor** is the program where you write code. Many editors can show the problems of a file as you type, through a **language server**: a program that runs beside the editor and answers its questions about the code, in a standard form called the Language Server Protocol.

`una lsp` is Una's language server. You do not run it yourself: you set your editor to start it, and the editor talks to it over stdout and **stdin**, the standard input, the stream a program reads from. As you type, it shows the tier 0 diagnostics of `una check`; when you open or save a file, it also runs the proofs. Above each function it shows how many of its obligations are proven (a **code lens**). It offers the repairs with exact edits as quick fixes, one click each, and formats a file. It also shows what a name is when you hold the pointer over it, and where it is declared. It checks and proves, and it never runs a program.

### Check, format or fix

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| A quick answer while you type, without proofs | `una check --tier 0 .`, or an editor with `una lsp` |
| The full answer, proofs included, before you call a change done | `una check .` |
| The layout fixed, and nothing else | `una fmt .` |
| To know whether the layout is right, without changing files | `una fmt --check .` |
| To see the exact repairs before anything changes | `una fix --dry-run .` |
| To apply them, then format | `una fix .` |
:::

### Check yourself: the check loop

Start from the clean receipt of the second step, and make two changes at once: the body of `line_text` goes back on its own line, and the call loses its label again.

```diff include="steps/02-fixed..steps/05-label-and-layout:src/receipt.una" title="src/receipt.una"
--- a/src/receipt.una
+++ b/src/receipt.una
@@ -1,9 +1,11 @@
 module receipt
 
 --- One line of a receipt: the units, the SKU and the line's total in cents.
-line_text(units: Int, sku: Text, cents: Int) -> Text = "{units} x {sku}  {cents}"
+line_text(units: Int, sku: Text, cents: Int) -> Text
+=
+  "{units} x {sku}  {cents}"
 
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print(line_text(2, sku: "LAMP-01", cents: 3980))
+  @console.print(line_text(2, "LAMP-01", cents: 3980))
```

How many diagnostics does `una check .` report? And what does `una fix --dry-run .` print?

:::answer Show the answer
`una check .` reports two: U7001 for the layout and U2004 for the label. Both carry an exact edit, so the JSON document counts both as fixable:

```text include="steps/05-label-and-layout/expected/commands/json.txt"
$ una --json check .
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U7001","severity":"error","domain":"project","message":"lines 4 to 6 are not in canonical form","primary":{"file":"src/receipt.una","start":{"line":4,"col":1},"end":{"line":6,"col":29}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"rewrite in canonical form, as `una fmt` does","edit":{"file":"src/receipt.una","start":{"line":4,"col":1},"end":{"line":7,"col":1},"replacement":"line_text(units: Int, sku: Text, cents: Int) -> Text = \"{units} x {sku}  {cents}\"\n"}}],"explain":"una explain U7001"},{"schema":"una.diagnostic/1","code":"U2004","severity":"error","domain":"types","message":"argument 2 of `line_text` needs a label; only the first argument may go without one","primary":{"file":"src/receipt.una","start":{"line":11,"col":31},"end":{"line":11,"col":40}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"label it `sku`","edit":{"file":"src/receipt.una","start":{"line":11,"col":31},"end":{"line":11,"col":40},"replacement":"sku: \"LAMP-01\""}}],"explain":"una explain U2004"}],"fixable":2}
```

But `una fix --dry-run .` prints one line:

```text include="steps/05-label-and-layout/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/receipt.una:11:31 U2004 label it `sku`
```

The label is a repair, so it gets a `fixed` line. The layout is not a repair round's edit: `una fix` formats every file after its rounds, as `una fmt .` does, and that step has no line of its own. `una fix .` would still fix both.
:::

## 18.2 Reading a diagnostic


### What a diagnostic is

A **diagnostic** is una's report of one problem in your code. Think of a note from a building inspector: it names the rule that is broken by its number, says where, says what is wrong, and suggests how to fix it. A diagnostic has the same parts:

- a **code**, such as U5001, which names the kind of problem and never changes;
- a **severity**, which is always `error` in this release: una has no warnings to ignore;
- a **domain**, the part of the language the problem belongs to: `syntax`, `names`, `types`, `authority`, `security`, `verification`, `runtime`, `project` or `internal`;
- a **message**, one sentence for a person;
- a **primary place**, the exact span of code the problem is about, and sometimes **related places**, other spans that explain it;
- **repairs**, ranked from best to worst, each with an exact edit or only a description;
- for a proof, the **obligation** that failed and a **counterexample**.

### Why diagnostics have codes and parts

Suppose a checker printed only `error: sale_price may return a value below cost`. A person can read it. A script that wants to know whether the problem is a proof or a typo has to guess from the words, and the guess breaks the day the words improve. An editor that wants to underline the right characters has to find them in the sentence. A person who wants to know how to fix it has to work it out alone.

So every part of a Una diagnostic is a separate field. The code tells a program what happened, and stays the same when the message improves. The places are numbers, not prose. The repairs are a list, and the exact ones carry their edit. The text for people and the JSON for programs are two renderings of one value, so both always say the same thing.

### A typo the checker catches

The simplest diagnostics come from a typo. [Chapter 1](/learn/hello/#if-una-check-finds-a-mistake) read one in three steps: what is wrong, where, and the repair. Here is another, in a program that prints one line, with `print` changed to `write`, which `Console` does not have:

```diff include="steps/06-hello..steps/13-typo:src/hello.una" title="src/hello.una"
--- a/src/hello.una
+++ b/src/hello.una
@@ -4,4 +4,4 @@
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print("The store is open")
+  @console.write("The store is open")
```

`una check .` reports:

```text include="steps/13-typo/expected/rendered.txt"
[U1001] Error: capability `Console` has no operation `write`
   ╭─[ src/hello.una:7:12 ]
   │
 7 │   @console.write("The store is open")
   │            ──┬──
   │              ╰──── capability `Console` has no operation `write`
   │
   │ Note: run `una explain U1001` for an explanation
───╯
```

The first line gives the code, U1001, and the message: `Console` has no operation `write`. Under it, `src/hello.una:7:12` is the file, the line and the column, the 12th character of line 7; lines and columns count from 1. The excerpt shows line 7 with its number on the left. The marks under it, `──┬──`, underline the exact span, `write`, and the line from `╰──` repeats the message next to it. This time there is no `Help` line: `write` is close to no operation of `Console`, so the checker has no repair to offer. The `Note` names the command that explains the code, and with no exact edit, there is no last line about `una fix`.

Read every diagnostic in that order: the message says what, the place says where, and the help, when there is one, says what to do. A diagnostic of the verifier has more parts, in the same order.

### A sale price with one wrong word


A diagnostic that the verifier reports has the most parts. This step computes a sale price that must never fall below cost, from a price, a cost and a percent off. It has a requirement it is derived from ([chapter 5](/learn/contracts/#s5-5)), and a private function that reads a typed percent. The body has one wrong word: on line 24, on the path where the discount goes below cost, it returns `price` instead of `cost`.

```una include="steps/09-refuted/src/discount.una" title="steps/09-refuted/src/discount.una" caption="with one wrong word, on line 24"
module discount

requirement PRICING_1
  text "A sale price is never below what the store paid for the product"
  source human
  owner pricing
  status active

--- An amount of money in cents, never negative.
pub kind Cents = Int where it >= 0

--- A discount in percent, from 0 to 90.
pub kind Percent = Int in 0..90

--- Why a typed percent was rejected.
kind PercentError = NotANumber(raw: Text) | OutOfRange(value: Int)

--- The price after `off` percent, never below `cost`.
pub sale_price(price: Cents, cost: Cents, off: Percent) -> Cents
  ensures result >= cost
  derived from PRICING_1
=
  let discounted = price - price * off / 100
  if discounted < cost then price else discounted

--- A percent typed by a person, such as "30".
parse_percent(raw: Text) -> Percent
=
  let n = raw.trim.to_int()
    if none fail NotANumber(raw)
  if n < 0 or n > 90
    fail OutOfRange(value: n)
  else
    n

pub main() -> Unit
  uses @console: Console[print]
=
  let off = parse_percent(" 30")
    if error use 0
  let lamp = sale_price(1990, cost: 1200, off: off)
  let desk = sale_price(12900, cost: 11000, off: off)
  @console.print("LAMP-01 {lamp}, DESK-02 {desk}")

example "30 percent off a lamp"
  do sale_price(1990, cost: 1200, off: 30)
  expect result == 1393

example "a typed percent above 90 is OutOfRange"
  do parse_percent("95")
  expect fails OutOfRange
```

`una check .` reports:

```text include="steps/09-refuted/expected/rendered.txt"
[U5001] Error: postcondition of `sale_price` is refuted
    ╭─[ src/discount.una:24:29 ]
    │
 20 │   ensures result >= cost
    │           ───────┬──────
    │                  ╰──────── ensures clause
    │
 24 │   if discounted < cost then price else discounted
    │                             ──┬──
    │                               ╰──── postcondition of `sale_price` is refuted
    │
    │ Help 1: repair 1: add a guard or an arm so that the failing path returns a value for which `result >= cost` holds
    │
    │ Help 2: repair 2: adjust the `ensures` clause
    │
    │ Note 1: obligation ob-8a05af02a5f7 (postcondition) is refuted: result >= cost
    │
    │ Note 2: counterexample: cost = 1, off = 0, price = 0, result = 0
    │
    │ Note 3: run `una explain U5001` for an explanation
────╯
```

### The parts of a diagnostic

#### The first line: code and message

`[U5001] Error:` is the code and the severity. U5001 means that the verifier found values for which a promise fails: the promise is **refuted**. The message names which promise: the postcondition, the `ensures` clause, of `sale_price`.

#### The places

The box under the first line shows the code around each place, with the file, line and column of the primary place at its top: `src/discount.una:24:29`. Each place has a mark, a line under the span, and a label at its end:

- the **related place**, `ensures clause`, on line 20, is the promise;
- the **primary place**, on line 24, is the value that breaks it: `price`.

#### Help lines: the repairs

`Help 1` and `Help 2` are the repairs, best first, each numbered `repair N`. A repair with an exact edit ends with `edit <place> to "<text>"`, as the receipt's did. These two have no edit: the right change depends on what the function is meant to do, which una cannot know.

#### Note lines: the obligation, the counterexample, the explanation

- `Note 1` is the **obligation**: its identifier, `ob-8a05af02a5f7`, its kind, `postcondition`, and its goal, `result >= cost`. [Section 18.3](#s18-3) lists every obligation by that identifier.
- `Note 2` is the **counterexample**: one choice of values for which the goal is false.
- The last `Note` says where to read more: `una explain U5001`.

#### The last line: what `una fix` can apply

A diagnostic with an exact edit ends the output with a count, ``1 of 1 diagnostics have an edit that `una fix` applies``, as the receipt's did. The refuted proof has none, so there is no such line.

#### Reading it from the top

:::steps
1. **The first line.** U5001: the postcondition of `sale_price` is refuted.
2. **The two places.** The promise, line 20, and the value that breaks it, `price` on line 24.
3. **The repairs.** A guard or an arm that returns a value that keeps the promise, or a changed promise. Neither is mechanical.
4. **The obligation.** Its goal, `result >= cost`, is the promise with the returned value as `result`.
5. **The counterexample.** With `price = 0` and `cost = 1`, the discounted price 0 is below cost, so the function returns `price`, 0, and 0 is not at least 1. Plug the values into the code and the bug is in plain sight.
6. **The note.** Where to read more.
:::

### Several problems in one check

`una check .` reports every problem it finds in one pass, not only the first, as the receipt of [Habits from other languages](#habits-from-other-languages) showed. With two misspelt operations in the program of [A typo the checker catches](#a-typo-the-checker-catches), it reports two diagnostics:

```diff include="steps/06-hello..steps/12-two-typos:src/hello.una" title="src/hello.una"
--- a/src/hello.una
+++ b/src/hello.una
@@ -4,4 +4,5 @@
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print("The store is open")
+  @console.write("The store is open")
+  @console.show("Orders placed before 18:00 ship today")
```

```text include="steps/12-two-typos/expected/diagnostics.txt"
error U1001 at src/hello.una:7:12: capability `Console` has no operation `write`
error U1001 at src/hello.una:8:12: capability `Console` has no operation `show`
```

This book lists them here in a short form, one line each: the code, the place and the message. In your terminal, `una check .` prints each one in full, as for `write`. Fix them in any order, and run `una check .` again until it prints nothing.

### Repairs that cost a guarantee

Not every repair is equal. This step halves a price typed at the till, for a two-for-one offer, and promises a `Cents`, which is never negative:

```una include="steps/10-half-price/src/discount.una" title="steps/10-half-price/src/discount.una"
module discount

--- An amount of money in cents, never negative.
pub kind Cents = Int where it >= 0

--- Half of a price typed at the till, for a two-for-one offer.
half_price(typed: Int) -> Cents = typed / 2

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{half_price(1990)}")
```

```text include="steps/10-half-price/expected/rendered.txt"
[U5001] Error: refinement `result >= 0` is refuted
   ╭─[ src/discount.una:7:35 ]
   │
 4 │ pub kind Cents = Int where it >= 0
   │                            ───┬───
   │                               ╰───── where clause
   │
 7 │ half_price(typed: Int) -> Cents = typed / 2
   │                                   ────┬────
   │                                       ╰────── refinement `result >= 0` is refuted
   │
   │ Help 1: repair 1: add a guard (`if` or a `when` arm) that handles the values where `result >= 0` does not hold
   │
   │ Help 2: repair 2 (escape: checked; a runtime test replaces the static proof: the program fails at run time where the proof would have rejected it; it counts against [escape_budget] and is listed in the build report): check the value with `checked(value, result >= 0) else fail <Variant>`
   │
   │ Note 1: obligation ob-5d6aa711c19b (refinement) is refuted: result >= 0
   │
   │ Note 2: counterexample: result = -1, typed = -2
   │
   │ Note 3: run `una explain U5001` for an explanation
───╯
```

The counterexample is a typed amount of -2, which halves to -1. The two repairs differ in what they cost:

- **Repair 1 keeps every guarantee.** A guard that handles a negative amount, and the verifier proves the result again.
- **Repair 2 is an escape.** `checked` tests the condition while the program runs instead of proving it ([chapter 7](/learn/failure/#s7-5)). The program then fails at run time where the proof would have rejected it, it counts against the package's `[escape_budget]`, and the build report lists it. The label `(escape: checked; …)` says so, before the description.

Escapes always come after the repairs that keep the guarantee. A third kind of mark, `(widens authority: …)`, says that a repair gives a function more power than it had: [A capability that is not there](#a-capability-that-is-not-there-u3001) shows one. Widenings come after the repairs that keep authority, and `una fix` applies neither an escape nor a widening.

### An explanation for every code: `una explain`

Every code has an explanation in the binary: a paragraph, and for almost every code a failing example and a fixed one. You need no network and no browser. The first lines of the one for the missing label of [section 18.1](#s18-1):

```text include="steps/01-fix/expected/commands/explain.txt#L1-L4"
$ una explain U2004
# U2004: Missing argument label

A call with two or more arguments may omit the label of its first argument only; every other argument names its parameter, as in `max(x, b: 10)`, or is a bare name equal to the parameter's name, which counts as labeled (`spec/04 §3`). A constructor with two or more fields labels every argument, the first included. The diagnostic carries an edit that labels the argument with the parameter at its position.
```

The paragraph is the full rule, and it may name terms and rules that this book does not cover; you do not need all of it to fix the problem. The failing example and the fixed one follow it. The site has the same text on each code's page, such as [U2004](/docs/errors/U2004/).

### The same diagnostic as JSON

The refuted sale price, for a program, is one line of JSON:

```sh
una --json check .
```

```json include="steps/09-refuted/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U5001","severity":"error","domain":"verification","message":"postcondition of `sale_price` is refuted","primary":{"file":"src/discount.una","start":{"line":24,"col":29},"end":{"line":24,"col":34}},"related":[{"file":"src/discount.una","start":{"line":20,"col":11},"end":{"line":20,"col":25},"message":"ensures clause"}],"obligation":{"id":"ob-8a05af02a5f7","kind":"postcondition","goal":"result >= cost","status":"refuted"},"counterexample":{"bindings":[{"name":"cost","value":1},{"name":"off","value":0},{"name":"price","value":0},{"name":"result","value":0}]},"repairs":[{"rank":1,"escape_cost":0,"description":"add a guard or an arm so that the failing path returns a value for which `result >= cost` holds","edit":null},{"rank":2,"escape_cost":0,"description":"adjust the `ensures` clause","edit":null}],"explain":"una explain U5001"}],"fixable":0}
```

Every part of the text is a key:

| Key | What it holds |
| --- | --- |
| `code`, `severity`, `domain`, `message` | The first line, split into its parts |
| `primary`, `related` | The places, each a file, a `start` and an `end`, with a `message` for a related place |
| `obligation` | The identifier, kind, goal and status of the obligation, for a proof only |
| `counterexample` | The values, as a list of `bindings`, each a `name` and a `value`, for a proof only |
| `repairs` | Each repair's `rank`, its `escape_cost`, its `description` and its `edit`, or `null` when it has none |
| `explain` | The command that explains the code |
| `fixable` | At the end of the document: how many diagnostics `una fix` would repair |

The escape of the half price, in JSON, is a repair with `escape_cost` 1 and an `escape` key that says what the guarantee loses:

```json include="steps/10-half-price/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U5001","severity":"error","domain":"verification","message":"refinement `result >= 0` is refuted","primary":{"file":"src/discount.una","start":{"line":7,"col":35},"end":{"line":7,"col":44}},"related":[{"file":"src/discount.una","start":{"line":4,"col":28},"end":{"line":4,"col":35},"message":"where clause"}],"obligation":{"id":"ob-5d6aa711c19b","kind":"refinement","goal":"result >= 0","status":"refuted"},"counterexample":{"bindings":[{"name":"result","value":-1},{"name":"typed","value":-2}]},"repairs":[{"rank":1,"escape_cost":0,"description":"add a guard (`if` or a `when` arm) that handles the values where `result >= 0` does not hold","edit":null},{"rank":2,"escape_cost":1,"escape":{"kind":"checked","cost":"a runtime test replaces the static proof: the program fails at run time where the proof would have rejected it; it counts against [escape_budget] and is listed in the build report"},"description":"check the value with `checked(value, result >= 0) else fail <Variant>`","edit":null}],"explain":"una explain U5001"}],"fixable":0}
```

### How diagnostics behave

- **Places count from 1.** Lines and columns start at 1, and a column counts characters: a character such as `é` counts as one column, even though a file stores it in more than one byte, a unit of storage. `end` is the first position after the span: the mark under `price` starts at column 29 and ends before column 34, five characters.
- **Proof parts only for proofs.** `obligation` and `counterexample` appear only for the verifier's codes, U5001 and U5002, the second for a goal the solver could not decide.
- **A counterexample is one case, not a run.** The solver picks values that break the goal, often the smallest ones. A record or a list it does not need in detail gets a placeholder name such as `Product#0` or `List#0`, and its fields that matter get their own lines, such as `product.cost = 1`.
- **Repairs are ordered.** By escape cost first, then by rank: the repairs that keep every guarantee come first, then those that widen, then the escapes.

### Text or JSON

:::decide
**Which to use:**

| You are… | Read |
| --- | --- |
| A person at a terminal | The text: `una check .` |
| A script or a release check | The JSON, `una --json check .`, and the exit code |
| An editor | Neither: `una lsp`, tier 0 as you type, proofs on save |
| Unsure what a code means | `una explain <code>`, or its page on the site |
:::

### Check yourself: reading a diagnostic

This step takes a coupon off a price, and promises a `Cents`:

```una include="steps/11-coupon/src/discount.una#after_coupon" title="steps/11-coupon/src/discount.una"
--- The price after a coupon worth `off` cents.
pub after_coupon(price: Cents, off: Cents) -> Cents = price - off
```

`una check .` rejects it with U5001. Before you look: which value of `off` breaks the promise when `price` is 0? And will `una fix .` change the code?

:::answer Show the answer
Any coupon worth more than the price, such as `off = 1` with `price = 0`:

```text include="steps/11-coupon/expected/rendered.txt"
[U5001] Error: refinement `result >= 0` is refuted
   ╭─[ src/discount.una:7:55 ]
   │
 4 │ pub kind Cents = Int where it >= 0
   │                            ───┬───
   │                               ╰───── where clause
   │
 7 │ pub after_coupon(price: Cents, off: Cents) -> Cents = price - off
   │                                                       ─────┬─────
   │                                                            ╰─────── refinement `result >= 0` is refuted
   │
   │ Help 1: repair 1: add a guard (`if` or a `when` arm) that handles the values where `result >= 0` does not hold
   │
   │ Help 2: repair 2 (escape: checked; a runtime test replaces the static proof: the program fails at run time where the proof would have rejected it; it counts against [escape_budget] and is listed in the build report): check the value with `checked(value, result >= 0) else fail <Variant>`
   │
   │ Note 1: obligation ob-5649fc082080 (refinement) is refuted: result >= 0
   │
   │ Note 2: counterexample: off = 1, price = 0, result = -1
   │
   │ Note 3: run `una explain U5001` for an explanation
───╯
```

`result = -1` breaks `result >= 0`, the rule of `Cents`. `una fix .` changes nothing: neither repair has an edit, and the second is an escape. The fix is a decision, such as returning 0 when the coupon is worth more than the price, or a `requires off <= price` that every caller proves.
:::

Second, the program of [A typo the checker catches](#a-typo-the-checker-catches), with one wrong letter order this time:

```diff include="steps/06-hello..steps/14-misspelt:src/hello.una" title="src/hello.una"
--- a/src/hello.una
+++ b/src/hello.una
@@ -4,4 +4,4 @@
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print("The store is open")
+  @console.pirnt("The store is open")
```

The checker reports U1001 at line 7, column 12, where `pirnt` starts, and suggests `print` as an exact edit. Before you look: in `una --json check .`, what is `fixable`, and what are the `start` and `end` of the repair's `edit`?

:::answer Show the answer
```json include="steps/14-misspelt/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U1001","severity":"error","domain":"names","message":"capability `Console` has no operation `pirnt`","primary":{"file":"src/hello.una","start":{"line":7,"col":12},"end":{"line":7,"col":17}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"write `print`","edit":{"file":"src/hello.una","start":{"line":7,"col":12},"end":{"line":7,"col":17},"replacement":"print"}}],"explain":"una explain U1001"}],"fixable":1}
```

`fixable` is 1: the one diagnostic has a repair with an edit. The edit starts at line 7, column 12, and ends at column 17, the first position after `pirnt`, so it covers the five characters of the word and replaces them with `"print"`. The `edit` has the same span as `primary`, since the repair rewrites exactly the marked word.
:::

## 18.3 What was proven: obligations, contracts and traces


[Section 5.4](/learn/contracts/#s5-4) listed the obligations of a package with `una obligations`, [section 5.5](/learn/contracts/#s5-5) followed a requirement to its proof with `una trace`, and [section 6.3](/learn/functions/#s6-3) read a whole header with `una contract`. This section uses the three together on one package, as a reviewer does, and adds what those sections left out: their JSON forms, what they print for a package that does not check, and how they behave in a script.

### What a proof obligation is

A **proof obligation** is one fact that the verifier must prove before the package checks, and its status is proven, refuted or unknown, as [section 5.4](/learn/contracts/#s5-4) explains with its kinds. [Section 8.2](/learn/choices/#s8-2) adds `exhaustive`, for a `when` over numbers without `else`. Two more kinds, `effect_condition` and `contract_lock`, exist only in edition `0.3`. The **edition** is the version of the Una language that a package's `una.toml` names ([chapter 19](/learn/editions/)), and this chapter's packages are on edition `0.2`.

### Why you list what was proven

A package that checks clean prints nothing, so a reviewer needs the list itself, as [section 5.4](/learn/contracts/#s5-4) showed. A review asks three questions of a package at once: which facts did the verifier prove, and where? What does each function promise, including what nobody wrote down? Which code carries the rule "a sale price is never below cost"? The three commands answer them, from the same proofs.

### From promises to obligations

This step is the fixed sale price. The fix is the one word that [section 18.2](#s18-2) found:

```diff include="steps/09-refuted..steps/08-proven:src/discount.una" context="1" title="src/discount.una"
--- a/src/discount.una
+++ b/src/discount.una
@@ -23,3 +23,3 @@
   let discounted = price - price * off / 100
-  if discounted < cost then price else discounted
+  if discounted < cost then cost else discounted
 
```

The whole package, which checks clean:

```una include="steps/08-proven/src/discount.una" title="steps/08-proven/src/discount.una" verified="check, run, test"
module discount

requirement PRICING_1
  text "A sale price is never below what the store paid for the product"
  source human
  owner pricing
  status active

--- An amount of money in cents, never negative.
pub kind Cents = Int where it >= 0

--- A discount in percent, from 0 to 90.
pub kind Percent = Int in 0..90

--- Why a typed percent was rejected.
kind PercentError = NotANumber(raw: Text) | OutOfRange(value: Int)

--- The price after `off` percent, never below `cost`.
pub sale_price(price: Cents, cost: Cents, off: Percent) -> Cents
  ensures result >= cost
  derived from PRICING_1
=
  let discounted = price - price * off / 100
  if discounted < cost then cost else discounted

--- A percent typed by a person, such as "30".
parse_percent(raw: Text) -> Percent
=
  let n = raw.trim.to_int()
    if none fail NotANumber(raw)
  if n < 0 or n > 90
    fail OutOfRange(value: n)
  else
    n

pub main() -> Unit
  uses @console: Console[print]
=
  let off = parse_percent(" 30")
    if error use 0
  let lamp = sale_price(1990, cost: 1200, off: off)
  let desk = sale_price(12900, cost: 11000, off: off)
  @console.print("LAMP-01 {lamp}, DESK-02 {desk}")

example "30 percent off a lamp"
  do sale_price(1990, cost: 1200, off: 30)
  expect result == 1393

example "a typed percent above 90 is OutOfRange"
  do parse_percent("95")
  expect fails OutOfRange
```

### How to write the three commands

#### Every obligation and its status: `una obligations .`

`una obligations .` checks the package and lists every obligation with its status, proven or not:

```text include="steps/08-proven/expected/commands/obligations.txt"
$ una obligations .
proven   ob-a1f2aa4dc27a refinement    src/discount.una:19:5 result >= 0
proven   ob-8a05af02a5f7 postcondition src/discount.una:20:11 result >= cost
proven   ob-ab12d15138b8 refinement    src/discount.una:27:1 result in 0..90
proven   ob-973036ad50b4 refinement    src/discount.una:41:25 1990 >= 0
proven   ob-d4bc9c2cf5f2 refinement    src/discount.una:41:37 1200 >= 0
proven   ob-a1fc2815567e refinement    src/discount.una:41:48 off in 0..90
proven   ob-f4b448300879 refinement    src/discount.una:42:25 12900 >= 0
proven   ob-118790a80d6d refinement    src/discount.una:42:38 11000 >= 0
proven   ob-a1fc2815567e refinement    src/discount.una:42:50 off in 0..90
proven   ob-5b991b13fcbf refinement    src/discount.una:46:17 1990 >= 0
proven   ob-44bcd7b237f7 refinement    src/discount.una:46:29 1200 >= 0
proven   ob-effe966d12dd refinement    src/discount.una:46:40 30 in 0..90
```

Each line has five columns: the status, the identifier, the kind, the place and the goal. Most lines are `refinement`: each literal passed as `Cents` must be at least 0, and each `off` passed as `Percent` must be in `0..90`. The line at `19:5` is the result of `sale_price`, which must be a `Cents`, and the line at `27:1` is the result of `parse_percent`, which must be a `Percent`. One `ensures` gives one `postcondition` line.

This listing is a first run. Run it again, or after `una check .`, and each line ends with `(cached)`, and the report counts them under `cached`.

#### A function's full header: `una contract <module.function>`

`una contract` prints a function's full header, as a caller relies on it, with its doc comments. The function is named by its module and its name. For a private function it shows what the checker inferred:

```text include="steps/08-proven/expected/commands/contract.txt"
$ una contract discount.parse_percent
--- A percent typed by a person, such as "30".
parse_percent(raw: Text) -> Percent
  fails PercentError -- inferred
```

`parse_percent` declares no `fails` clause, and the contract shows the one the checker inferred, marked `-- inferred`, as [section 6.3](/learn/functions/#s6-3) showed for `uses` and [section 7.2](/learn/failure/#s7-2) for `fails`. For `sale_price`, the contract ends with the requirement it is derived from:

```text include="steps/08-proven/expected/commands/contract-sale.txt"
$ una contract discount.sale_price
--- The price after `off` percent, never below `cost`.
pub sale_price(price: Cents, cost: Cents, off: Percent) -> Cents
  ensures result >= cost
  derived from PRICING_1
-- requirement PRICING_1 (active): "A sale price is never below what the store paid for the product"
```

#### From a requirement to the code: `una trace <REQUIREMENT>`

`una trace` goes the other way, from a requirement to the code. It prints the requirement, every function derived from it with the clauses that carry it, and the obligations that prove them:

```text include="steps/08-proven/expected/commands/trace.txt"
$ una trace PRICING_1
requirement PRICING_1 (active)
  text "A sale price is never below what the store paid for the product"
  source human
  owner pricing
discount.sale_price
  ensures result >= cost
  proven   ob-a1f2aa4dc27a refinement    result >= 0
  proven   ob-8a05af02a5f7 postcondition result >= cost
```

A reviewer who asks "where is this rule enforced, and is it proven?" gets the answer from one command.

#### The same, as JSON

Each of the three takes `--json`. The contract of `parse_percent`, as data:

```text include="steps/08-proven/expected/commands/contract-json.txt"
$ una --json contract discount.parse_percent
{"schema":"una.contract/1","function":"discount.parse_percent","public":false,"docs":["A percent typed by a person, such as \"30\"."],"header":"parse_percent(raw: Text) -> Percent","constraints":[],"result_labels":[],"of_raises":[],"requires":[],"ensures":[],"uses":[],"fails":{"kind":"PercentError","inferred":true},"derived_from":[]}
```

Each clause is a key, and each inferred part says so: `"inferred":true` on `fails`. `una --json obligations .` gives each obligation its `hypotheses` too, the facts the solver could assume at that place, such as `price >= 0` from the type of `price`. When a goal cannot be proven, the hypotheses show what the verifier knew, and so what is missing.

```sh
una --json obligations .
```

```json include="steps/08-proven/expected/commands/obligations-json.txt#L2"
{"schema":"una.obligations/1","obligations":[{"id":"ob-a1f2aa4dc27a","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":19,"col":5},"end":{"line":19,"col":15}},"declaration":"discount.sale_price","goal":"result >= 0","hypotheses":["price >= 0","cost >= 0","0 <= off","off <= 90"],"cached":false},{"id":"ob-8a05af02a5f7","kind":"postcondition","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":20,"col":11},"end":{"line":20,"col":25}},"declaration":"discount.sale_price","goal":"result >= cost","hypotheses":["price >= 0","cost >= 0","0 <= off","off <= 90"],"cached":false},{"id":"ob-ab12d15138b8","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":27,"col":1},"end":{"line":27,"col":14}},"declaration":"discount.parse_percent","goal":"result in 0..90","hypotheses":[],"cached":false},{"id":"ob-973036ad50b4","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":41,"col":25},"end":{"line":41,"col":29}},"declaration":"discount.main","goal":"1990 >= 0","hypotheses":[],"cached":false},{"id":"ob-d4bc9c2cf5f2","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":41,"col":37},"end":{"line":41,"col":41}},"declaration":"discount.main","goal":"1200 >= 0","hypotheses":[],"cached":false},{"id":"ob-a1fc2815567e","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":41,"col":48},"end":{"line":41,"col":51}},"declaration":"discount.main","goal":"off in 0..90","hypotheses":[],"cached":false},{"id":"ob-f4b448300879","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":42,"col":25},"end":{"line":42,"col":30}},"declaration":"discount.main","goal":"12900 >= 0","hypotheses":["lamp >= 0","lamp >= 1200"],"cached":false},{"id":"ob-118790a80d6d","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":42,"col":38},"end":{"line":42,"col":43}},"declaration":"discount.main","goal":"11000 >= 0","hypotheses":["lamp >= 0","lamp >= 1200"],"cached":false},{"id":"ob-a1fc2815567e","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":42,"col":50},"end":{"line":42,"col":53}},"declaration":"discount.main","goal":"off in 0..90","hypotheses":["lamp >= 0","lamp >= 1200"],"cached":false},{"id":"ob-5b991b13fcbf","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":46,"col":17},"end":{"line":46,"col":21}},"declaration":"discount.example \"30 percent off a lamp\"","goal":"1990 >= 0","hypotheses":[],"cached":false},{"id":"ob-44bcd7b237f7","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":46,"col":29},"end":{"line":46,"col":33}},"declaration":"discount.example \"30 percent off a lamp\"","goal":"1200 >= 0","hypotheses":[],"cached":false},{"id":"ob-effe966d12dd","kind":"refinement","domain":"semantic","status":"proven","source":{"file":"src/discount.una","start":{"line":46,"col":40},"end":{"line":46,"col":42}},"declaration":"discount.example \"30 percent off a lamp\"","goal":"30 in 0..90","hypotheses":[],"cached":false}]}
```

### A refuted proof in the listings

On the package of [section 18.2](#s18-2), with the wrong word, the same commands still answer. `una obligations .` lists the refuted obligation among the proven ones, by the identifier the diagnostic printed in its `Note 1`, and exits with code 1:

```text include="steps/09-refuted/expected/commands/obligations.txt#L1-L4"
$ una obligations .
proven   ob-a1f2aa4dc27a refinement    src/discount.una:19:5 result >= 0
refuted  ob-8a05af02a5f7 postcondition src/discount.una:20:11 result >= cost
proven   ob-ab12d15138b8 refinement    src/discount.una:27:1 result in 0..90
```

`una contract` prints the header as before, since a header does not depend on the proofs:

```text include="steps/09-refuted/expected/commands/contract.txt"
$ una contract discount.sale_price
--- The price after `off` percent, never below `cost`.
pub sale_price(price: Cents, cost: Cents, off: Percent) -> Cents
  ensures result >= cost
  derived from PRICING_1
-- requirement PRICING_1 (active): "A sale price is never below what the store paid for the product"
```

### How the three commands behave

- **Names.** A function is named by its module and its name, `discount.sale_price`. A requirement is named by its identifier, `PRICING_1`.
- **Identifiers.** An obligation's identifier is computed from its declaration, its kind and its goal. It survives edits elsewhere in the file, and two identical obligations in one function share one, as the two `off in 0..90` lines do.
- **The proof cache.** una keeps proven results in the package's proof cache, `.una/cache/`. After a first check, a result that came from the cache is marked `(cached)`.
- **Exit codes.** `una obligations .` and `una trace` exit with code 1 when an obligation is not proven, so a script can rely on them.
- **What `una contract` checks.** Only tier 0. When the package has a tier 0 error, such as a type error, it prints the diagnostics instead of the header and exits with code 1. An unknown name is a usage error, code 2.

### Obligations, contract or trace

:::decide
**Which to use:**

| You want to know… | Use |
| --- | --- |
| Everything the verifier proved, and what it did not | `una obligations .` |
| What a function promises and may do, written or inferred | `una contract <module.function>` |
| Where a requirement is enforced, and whether it is proven | `una trace <REQUIREMENT>` |
| Why a goal failed | The diagnostic, then `una --json obligations .` for its hypotheses |
:::

### Check yourself: a requirement with nothing derived from it

Remove the `derived from` line from `sale_price`, and keep the requirement:

```diff include="steps/08-proven..steps/15-no-derived:src/discount.una" context="1" title="src/discount.una"
--- a/src/discount.una
+++ b/src/discount.una
@@ -20,3 +20,2 @@
   ensures result >= cost
-  derived from PRICING_1
 =
```

Does the package still check? What does `una trace PRICING_1` print?

:::answer Show the answer
It checks and runs as before: `derived from` is a link for the reader and the tools, and the proof of `ensures` does not need it. But the trace has nothing to follow:

```text include="steps/15-no-derived/expected/commands/trace.txt"
$ una trace PRICING_1
requirement PRICING_1 (active)
  text "A sale price is never below what the store paid for the product"
  source human
  owner pricing
```

The requirement is printed, and no function under it. A requirement that no function is derived from is a rule nobody has shown to be enforced: a reviewer reads the empty trace as a gap.
:::

## 18.4 The build report


### What a build report is

Chapters 5, 6 and 17 each showed one part of the build report: its `requirements` ([section 5.5](/learn/contracts/#s5-5)), its `authority` ([section 6.3](/learn/functions/#s6-3)) and its `information` ([section 17.5](/learn/information-flow/#s17-5)). This section reads the whole report.

A packaged food carries a label: what is inside, what was added, what it may contain. You read it without tasting the food. The **build report** is that label for a package. `una report .` checks the package and prints, on one page, what a reviewer needs to know about it: what was proven, what each function may do, what the proofs rely on, and what the guarantees do not cover.

### Why a report

A change to a package can look small in its diff of the code and still change a lot: one new `uses` line gives a function the power to write files, and one `checked` replaces a proof with a test at run time. A **reviewer** is the person who reads a proposed change before it is accepted, and one who reads only the changed lines can miss what they mean for the whole package. The report states those facts in fixed sections, so that comparing the report before and after a change shows every new power and every new trust, however small the code change was.

### How to produce it

```sh
una report .
```

`una report .` prints the report for people, on stdout. `una --json report .` prints the same report as the document `una.report/2`, which a release script can store and compare between two versions of a package. Both check the package first, at tier 1, and exit with code 1 when an obligation is not proven.

### The report of the sale price

The report of the fixed sale price:

```text include="steps/08-proven/expected/commands/report.txt"
$ una report .
package discount 0.1.0
lock: z3 5.1.0, sha256 3ae01f54b3b40760c00b7537ac3ba510a2288a5a4dd42a583dab76ea66719c3c
proven: 12 semantic obligations; security and authority by typing
obligations: 12 proven, 0 refuted, 0 unknown; 0 cached
authority:
  discount.main (pub): @console: Console[print]
handler authority:
information:
escapes:
assumptions:
tcb:
  trusted modules: 
  host capabilities: Console
  solver: z3 5.1.0
  proof cache: .una/cache/
  proof cache key: ~/.una/proof-cache.key
requirements:
  PRICING_1 (active): discount.sale_price
coverage: 2 pub functions, 1 with ensures, 1 with derived from, 0 trivial ensures
native: aarch64-apple-darwin
  arbitrary precision: discount.sale_price.price, discount.sale_price.cost, discount.sale_price.result
out of model: timing, termination and divergence, resource consumption and allocation, stack exhaustion, external systems beyond declared signatures, races between the check and the use of a file path, hard links, order of effects across concurrent tasks
```

### The sections of the report

#### What was proven: `lock`, `proven`, `obligations`

`lock` names the solver and a **digest** of `verification.lock`: a long number computed from the file's bytes, here with SHA-256, which changes if a single byte of the file changes. Two reports with the same digest were proven under the same lock. `proven` counts the proven obligations, and adds `security and authority by typing`: information flow and capabilities need no solver, since the checker proves them by their types. `obligations` counts them by status, and how many came from the proof cache.

#### What the code may do: `authority` and `handler authority`

Every function and handler with a `uses` clause, and what it may do. Here only `main` may print. A new line in this section, in a diff of the report, is a new power in the code.

#### What the code relies on: `information`, `escapes`, `assumptions`

`information` lists the calls of **policies**, the declarations that may lower the label on data, so that data labeled secret can reach a place that shows it; every such release goes through a policy ([chapter 17](/learn/information-flow/#s17-5)). `escapes` lists the uses of `checked`, by module, against the budget of `una.toml`. `assumptions` lists the operations of the package's own capabilities whose behavior the verifier assumes from their declarations: what an operation's header promises is all a proof knows of it.

#### What the proofs trust: `tcb`

The **trusted computing base** is everything the guarantees rest on without being proven by una: the trusted modules, which `una.toml` lists as the only modules allowed to hold policies ([chapter 17](/learn/information-flow/#s17-5)), the host capabilities, the solver, and the proof cache with the key that authenticates its entries. The smaller it is, the less there is to trust.

#### Requirements and coverage

`requirements` lists, for each requirement, the functions derived from it. `coverage` counts the public functions, how many have an `ensures` and how many a `derived from`, and the `trivial ensures`: a promise the solver proves with no hypothesis at all, such as `ensures true`, which promises nothing and is counted as missing.

#### The executable: `native`

`native` names the machine that `una build` builds for, the one una runs on, such as `aarch64-apple-darwin`. Under it, `arbitrary precision` lists the values the executable keeps as numbers of any size, because no refinement bounds them to a **machine word**, the fixed-size number a processor works with fastest. `Percent` is bounded by `0..90`, so `off` is not listed; `Cents` has no upper bound, so `price`, `cost` and the result are.

#### What the guarantees do not cover: `out of model`

The proofs say nothing about these: how long a run takes, whether it ends, how much memory it uses, what systems outside the declared capabilities do, and the other entries of the line, such as the order in which **concurrent tasks**, parts of a program that run at the same time ([chapter 15](/learn/concurrency/)), perform their operations. They are listed so that nobody reads more into "proven" than it means.

### A report of a package that does not check

On the package with the wrong word, `una report .` prints the diagnostic on stderr, and the report on stdout, whose counts show the refuted obligation:

```text include="steps/09-refuted/expected/commands/report.txt#L1-L5"
$ una report .
package discount 0.1.0
lock: z3 5.1.0, sha256 3ae01f54b3b40760c00b7537ac3ba510a2288a5a4dd42a583dab76ea66719c3c
proven: 11 semantic obligations; security and authority by typing
obligations: 11 proven, 1 refuted, 0 unknown; 0 cached
```

It exits with code 1, so a release script that runs it stops there.

### Reading the report as a review checklist

Read the report as a checklist for a change. A pull request, a proposed change that others review before it is merged (added to the main code), that adds a line under `authority`, a module under `trusted modules`, or a count under `escapes` changes what the package may do or what its proofs rest on, even when its diff of the code looks small. A drop in `coverage`, or a requirement that loses its functions, is a promise that went away.

> [!NOTE]
> The `native` line names the machine `una` runs on, so the report of the same package differs between a Mac and a Linux machine in that line only.

### A report, a contract or a trace

:::decide
**Which to use:**

| You review… | Read |
| --- | --- |
| A whole package, or a release | `una report .`, compared with the report of the last release |
| One function | `una contract <module.function>` |
| One rule of the business | `una trace <REQUIREMENT>` |
:::

### Check yourself: what a change shows in the report

This change replaces the range test of `parse_percent` with `checked`, a test at run time, and gives the module a budget of one `checked` in `una.toml`:

```diff include="steps/08-proven..steps/16-checked:src/discount.una" context="1" title="src/discount.una"
--- a/src/discount.una
+++ b/src/discount.una
@@ -30,6 +30,3 @@
     if none fail NotANumber(raw)
-  if n < 0 or n > 90
-    fail OutOfRange(value: n)
-  else
-    n
+  checked(n, it in 0..90) else fail OutOfRange(value: n)
 
```

```diff include="steps/08-proven..steps/16-checked:una.toml" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -6,3 +6,6 @@
 [run]
 entry = "discount"
 grants = ["console"]
+
+[escape_budget]
+checked_per_module = 1
```

The package still checks and prints the same output. Which section of the report changes?

:::answer Show the answer
`escapes`, which had no line:

```text include="steps/16-checked/expected/commands/report.txt#L10-L11"
escapes:
  discount: 1 checked, budget 1
```

The module `discount` uses one `checked`, the whole of its budget. Nothing else changes: the obligations still count 12, since the result of `parse_percent` is now proven from the `checked` value. The report shows a reviewer that one fact is now tested at run time instead of proven, which the diff of the code alone did not say.
:::

## 18.5 Running, testing and building


### What running, testing and building are

una can execute a package in three ways:

- **Running** executes `main`. `una run .` does it inside una itself, which reads the checked program and carries it out step by step. A program that executes another program this way is an **interpreter**.
- **Testing** executes every `example` of the package ([chapter 14](/learn/testing/)), each on its own, and compares the results with what the examples expect.
- **Building** turns the package into a **native executable**: a file of instructions for the machine's processor, which runs on its own, without una. Turning code into such a file is **compiling**, and a program that does it is a compiler.

### Why three commands

Each answers its own need. While you write, `una run .` shows what the program does right away. Before a change is done, `una test .` checks the numbers against values a person worked out. To ship, `una build .` gives an executable that the store's machines run without una installed.

### How to write them

#### `una run .` and `--grant`

`una run .` runs `main` of the module that `[run] entry` names, with the grants of `[run] grants` ([chapter 12](/learn/capabilities/#s12-2)). `una run --grant <spec> .` adds a grant for one run, such as `--grant clock`, on top of those of `una.toml`.

#### `una test .`

`una test .` runs every example and prints one line for each, then a count:

```text include="steps/08-proven/expected/commands/test.txt"
$ una test .
example discount "30 percent off a lamp" ... ok
example discount "a typed percent above 90 is OutOfRange" ... ok

2 examples: 2 passed, 0 failed
```

#### `una build .`

`una build .` compiles the package into a native executable, after the same checks:

```sh
una build .
```

```text include="steps/08-proven/expected/commands/build.txt"
$ una build .
built target/una/discount
```

#### With `--json`

With `--json`, `una run .` prints the run as one document: the status, the lines printed, the failure if any, and the **trace** of the run, the list of every operation it performed. This is a different thing from `una trace`, which follows a requirement to the code:

```text include="steps/08-proven/expected/commands/run.txt"
$ una --json run .
{"schema":"una.run/1","tier":1,"status":"ok","output":["LAMP-01 1393, DESK-02 11000"],"failure":null,"diagnostics":[],"trace":[{"seq":1,"instance":"host:Console","capability":"Console","op":"print","args":{"line":"\"LAMP-01 1393, DESK-02 11000\""},"outcome":{"kind":"ok","value":"unit"}}]}
```

The trace is what the program asked of the outside world, in order, with the arguments and the outcome of each operation. `una --json test .` gives each example its outcome, its result and its own trace:

```text include="steps/08-proven/expected/commands/test-json.txt"
$ una --json test .
{"schema":"una.test/1","tier":1,"redacted":false,"diagnostics":[],"examples":[{"module":"discount","name":"30 percent off a lamp","outcome":"pass","reason":null,"expectation":null,"result":{"kind":"ok","value":"1393"},"trace":[]},{"module":"discount","name":"a typed percent above 90 is OutOfRange","outcome":"pass","reason":null,"expectation":null,"result":{"kind":"fail","variant":"OutOfRange","value":"OutOfRange(95)"},"trace":[]}],"passed":2,"failed":0}
```

### Every command checks first

`una run`, `una test` and `una build` check the package first, at tier 1, and run nothing when the check reports an error. On the package with the wrong word, the run is `rejected`: nothing ran, `output` and `trace` are empty, and `diagnostics` holds the reason:

```text include="steps/09-refuted/expected/commands/run.txt"
$ una --json run .
{"schema":"una.run/1","tier":1,"status":"rejected","output":[],"failure":null,"diagnostics":[{"schema":"una.diagnostic/1","code":"U5001","severity":"error","domain":"verification","message":"postcondition of `sale_price` is refuted","primary":{"file":"src/discount.una","start":{"line":24,"col":29},"end":{"line":24,"col":34}},"related":[{"file":"src/discount.una","start":{"line":20,"col":11},"end":{"line":20,"col":25},"message":"ensures clause"}],"obligation":{"id":"ob-8a05af02a5f7","kind":"postcondition","goal":"result >= cost","status":"refuted"},"counterexample":{"bindings":[{"name":"cost","value":1},{"name":"off","value":0},{"name":"price","value":0},{"name":"result","value":0}]},"repairs":[{"rank":1,"escape_cost":0,"description":"add a guard or an arm so that the failing path returns a value for which `result >= cost` holds","edit":null},{"rank":2,"escape_cost":0,"description":"adjust the `ensures` clause","edit":null}],"explain":"una explain U5001"}],"trace":[]}
```

So a program that runs, or an executable that exists, is always one that checked.

### How running, testing and building behave

- **The status of a run.** `ok` for a run that returned, `failed` when `main` failed with its error kind, `aborted` when the run was stopped, by a limit ([chapter 16](/learn/memory/#s16-4) shows one) or another runtime error, and `rejected` when the checks failed and nothing ran.
- **The examples run alone.** Each example gets only the handlers its `given` lines install, so an example never reaches the console or a real service by accident.
- **The executable.** `una build .` writes it under the package, at `target/una/<name>`, with `<name>` from `[package] name`. It runs `main` with the grants of `una.toml` built in, takes further `--grant` flags, and prints what `una run .` prints. Building needs the system's **linker**, `cc`, on the path, the list of directories where the terminal looks for programs. **Linking** is the last step of a build: it joins the compiled code with the **runtime library**, the code that every Una executable shares. It builds for the machine it runs on.

### Exit codes

Every command of `una` ends with an **exit code**, the number the terminal receives when the command ends ([What a tool is](#what-a-tool-is)), and one of four:

| Code | Meaning |
| --- | --- |
| 0 | Success: no error, every obligation proven, every example passed |
| 1 | The output holds at least one error with a code, an obligation that is not proven, or a failed example |
| 2 | A usage error: the command line itself is wrong, such as an unknown flag or a path with no package; it is printed on stderr, without a code |
| 3 | An internal error of una itself, U8001 |

So `una check .` exits with 0 when the package checks, and with 1 when it reports a problem. `una run .` exits with 1 when the run is not `ok`, and `una test .` with 1 when an example fails. Another program that runs una for you, such as a release script or a code editor, tells success from failure by this number, without reading the text. The exit code does not depend on `--json`: the document and the text say the same thing.

### Choosing a command

The table matches each question of this chapter to the command that answers it:

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Know whether the package is right, fast, while you type | `una check --tier 0 .`, or an editor with `una lsp` |
| Know whether it is right, proofs included | `una check .` |
| Apply the repairs that are exact | `una fix --dry-run .`, then `una fix .` |
| See what was proven, and for which requirement | `una obligations .`, `una trace <requirement>` |
| See what a function promises, inferred clauses included | `una contract <module.function>` |
| Review what a package may do and trusts | `una report .` |
| Run it, test it, ship it | `una run .`, `una test .`, `una build .` |
:::

### Check yourself: an example with the wrong number

Someone worked out 30 percent off 19.90 by hand and wrote 13.90:

```diff include="steps/08-proven..steps/17-failing-example:src/discount.una" context="1" title="src/discount.una"
--- a/src/discount.una
+++ b/src/discount.una
@@ -46,3 +46,3 @@
   do sale_price(1990, cost: 1200, off: 30)
-  expect result == 1393
+  expect result == 1390
 
```

Does `una check .` accept the package? What does `una test .` print?

:::answer Show the answer
`una check .` accepts it: an example's `do` line must check, but whether its expectation holds is decided by running it. `una test .` runs it and reports the failure, with the line, the expectation and the value the code gave:

```text include="steps/17-failing-example/expected/commands/test.txt"
$ una test .
example discount "30 percent off a lamp" ... FAILED
  src/discount.una:47: expect result == 1390
  it is false, with `result` = `1393`
example discount "a typed percent above 90 is OutOfRange" ... ok

2 examples: 1 passed, 1 failed
```

The code computes 1393, which is right: 1990 - 1990 * 30 / 100 is 1990 - 597. The example was wrong, so the fix is in the example. A failed example says that the code and the person disagree; reading the value tells you which one is wrong.
:::

## 18.6 Day-to-day: price tags for a sale

### What the program must do

Now the program from the start of the chapter, and the checks it goes through before a release. The store runs a sale of 30 percent. Each shelf gets a tag with the price and the sale price, which a requirement says must never be below what the store paid. The prices come from the store's catalog, a capability, so the tags can be tested with a catalog held in memory. The program uses what earlier chapters taught; this chapter's part is what comes after the code is written: the commands that show it is right, what it may do, and what it promises.

### The requirement and the kinds

The requirement records the rule in words, so that `una trace` can follow it to the code. `Cents` and `Percent` are refined kinds ([chapter 5](/learn/contracts/#s5-3)), so a negative price or a discount of 95 percent cannot reach the functions of [The price](#the-price) and [The tag](#the-tag). `Product` is a record, and `Catalog` is the store's own capability with one operation, which `una report .` lists under `assumptions`.

```una include="day-to-day/src/pricetags.una#L1-L24" title="day-to-day/src/pricetags.una" caption="the requirement, the kinds and the catalog"
module pricetags

requirement PRICING_1
  text "A sale price is never below what the store paid for the product"
  source human
  owner pricing
  status active

--- An amount of money in cents, never negative.
pub kind Cents = Int where it >= 0

--- A discount in percent, from 0 to 90.
pub kind Percent = Int in 0..90

--- A product on the shelf: its SKU, its price and what the store paid for it.
pub kind Product
  sku: Text
  price: Cents
  cost: Cents

--- The store's catalog: the product with a SKU, or `None` for a SKU it does not list.
pub capability Catalog
  op product(sku: Text) -> Option[Product]

```

### The price

`sale_price` promises `result >= product.cost` and names the requirement it is derived from. The verifier proves the promise on both paths of the `if`, which gives the `postcondition` obligation that `una trace PRICING_1` shows at the end of this section.

```una include="day-to-day/src/pricetags.una#sale_price" title="day-to-day/src/pricetags.una"
--- The price after `off` percent, never below cost.
pub sale_price(product: Product, off: Percent) -> Cents
  ensures result >= product.cost
  derived from PRICING_1
=
  let discounted = product.price - product.price * off / 100
  if discounted < product.cost then product.cost else discounted
```

### The tag

`shown` writes cents as a person reads them, with `mod` for the remainder. `tag` asks the catalog, the only thing it may do, as its `uses` clause says, and handles a SKU the catalog does not list.

```una include="day-to-day/src/pricetags.una#shown..tag" title="day-to-day/src/pricetags.una"
--- Cents as a person reads them, such as 19.90.
pub shown(amount: Cents) -> Text
=
  let cents = amount mod 100
  let pad = if cents < 10 then "0" else ""
  "{amount / 100}.{pad}{cents}"

--- The tag printed on the shelf for `sku` during a sale of `off` percent.
pub tag(sku: Text, off: Percent) -> Text
  uses @catalog: Catalog[product]
=
  let found = @catalog.product(sku)
  when found
    is Some(product) -> "{sku}  {shown(product.price)} now {shown(sale_price(product, off: off))}"
    is None -> "{sku}  not in the catalog"
```

`when found` takes the catalog's answer apart. With `Some(product)`, the tag shows the price and the sale price, each through `shown`. With `None`, it says that the catalog does not list the SKU. Both arms give a `Text`, and `tag` cannot fail: a missing product is an ordinary answer of the catalog, not a failure.

### Running it

`listed` is a catalog held in a map, and `main` installs it for each tag with `with`:

```una include="day-to-day/src/pricetags.una#listed..main" title="day-to-day/src/pricetags.una"
--- A catalog held in memory, for this run and for tests.
handler listed(products: Map[Text, Product]) for Catalog
  op product(sku) = products.get(key: sku)

--- The products of this example run.
sample() -> Map[Text, Product]
=
  let lamp = Product(sku: "LAMP-01", price: 1990, cost: 1200)
  let desk = Product(sku: "DESK-02", price: 12900, cost: 11000)
  empty_map().with(key: lamp.sku, value: lamp).with(key: desk.sku, value: desk)

pub main() -> Unit
  uses @console: Console[print]
=
  for sku in ["LAMP-01", "DESK-02", "CHAIR-09"]
    let line = tag(sku, off: 30) with @catalog = listed(sample())
    @console.print(line)
```

`sample` holds the two products of this run. In production, the handler would read the store's database, and nothing else of the program would change: `tag` knows only the capability.

`una run .` prints the tags shown in [What you'll build](#what-youll-build). The lamp loses 30 percent, from 19.90 to 13.93. The desk would fall to 90.30, below its cost of 110.00, so its sale price stops at cost. The chair is not in the catalog.

### The whole program

The whole file:

```una include="day-to-day/src/pricetags.una" title="day-to-day/src/pricetags.una" caption="the whole program" verified="check, run, test"
module pricetags

requirement PRICING_1
  text "A sale price is never below what the store paid for the product"
  source human
  owner pricing
  status active

--- An amount of money in cents, never negative.
pub kind Cents = Int where it >= 0

--- A discount in percent, from 0 to 90.
pub kind Percent = Int in 0..90

--- A product on the shelf: its SKU, its price and what the store paid for it.
pub kind Product
  sku: Text
  price: Cents
  cost: Cents

--- The store's catalog: the product with a SKU, or `None` for a SKU it does not list.
pub capability Catalog
  op product(sku: Text) -> Option[Product]

--- The price after `off` percent, never below cost.
pub sale_price(product: Product, off: Percent) -> Cents
  ensures result >= product.cost
  derived from PRICING_1
=
  let discounted = product.price - product.price * off / 100
  if discounted < product.cost then product.cost else discounted

--- Cents as a person reads them, such as 19.90.
pub shown(amount: Cents) -> Text
=
  let cents = amount mod 100
  let pad = if cents < 10 then "0" else ""
  "{amount / 100}.{pad}{cents}"

--- The tag printed on the shelf for `sku` during a sale of `off` percent.
pub tag(sku: Text, off: Percent) -> Text
  uses @catalog: Catalog[product]
=
  let found = @catalog.product(sku)
  when found
    is Some(product) -> "{sku}  {shown(product.price)} now {shown(sale_price(product, off: off))}"
    is None -> "{sku}  not in the catalog"

--- A catalog held in memory, for this run and for tests.
handler listed(products: Map[Text, Product]) for Catalog
  op product(sku) = products.get(key: sku)

--- The products of this example run.
sample() -> Map[Text, Product]
=
  let lamp = Product(sku: "LAMP-01", price: 1990, cost: 1200)
  let desk = Product(sku: "DESK-02", price: 12900, cost: 11000)
  empty_map().with(key: lamp.sku, value: lamp).with(key: desk.sku, value: desk)

pub main() -> Unit
  uses @console: Console[print]
=
  for sku in ["LAMP-01", "DESK-02", "CHAIR-09"]
    let line = tag(sku, off: 30) with @catalog = listed(sample())
    @console.print(line)

example "a sale takes the percent off the price"
  do sale_price(Product(sku: "LAMP-01", price: 1990, cost: 1200), off: 30)
  expect result == 1393

example "a sale price stops at cost"
  do sale_price(Product(sku: "DESK-02", price: 12900, cost: 11000), off: 30)
  expect result == 11000

example "cents are shown with two digits"
  do shown(1905)
  expect result == "19.05"

example "a SKU the catalog does not list gets no price"
  given @catalog = listed(sample())
  do tag("CHAIR-09", off: 30)
  expect result == "CHAIR-09  not in the catalog"
```

### The checks before a release

Before the tags go to the printer, run the commands of this chapter, in this order:

```sh
una fmt --check .
una check .
una test .
una trace PRICING_1
una report .
una build .
```

Each command answers one question, and each would stop the release for its own reason:

| Command | Section | It stops the release when… |
| --- | --- | --- |
| `una fmt --check .` | [18.1](#s18-1) | A file is not in canonical form (U7001) |
| `una check .` | [18.1](#s18-1) | A name, a type, a capability, a security label or a proof is wrong |
| `una test .` | [18.5](#s18-5) | An example fails: a number is not the one a person expects |
| `una trace PRICING_1` | [18.3](#s18-3) | An obligation derived from the requirement is not proven |
| `una report .` | [18.4](#s18-4) | An obligation is not proven; and a reviewer reads what changed |
| `una build .` | [18.5](#s18-5) | The executable cannot be built, for example without `cc` |

`una fmt --check .` and `una check .` print nothing: the package is canonical and proven. `una trace PRICING_1` shows that the requirement reaches `sale_price` and that both of its obligations are proven:

```text include="day-to-day/expected/commands/trace.txt"
$ una trace PRICING_1
requirement PRICING_1 (active)
  text "A sale price is never below what the store paid for the product"
  source human
  owner pricing
pricetags.sale_price
  ensures result >= product.cost
  proven   ob-7c59f0c13fa3 refinement    result >= 0
  proven   ob-a498f6efa270 postcondition result >= product.cost
```

The first obligation is the result of `sale_price`, a `Cents`; the second is the promise. `una report .` shows what the package may do. Its `authority` section has two lines, `main` may print and `tag` may ask the catalog, and `assumptions` lists the operation of `Catalog` that the proofs take on trust:

```text include="day-to-day/expected/commands/report.txt#L6-L8,L12-L13"
authority:
  pricetags.main (pub): @console: Console[print]
  pricetags.tag (pub): @catalog: Catalog[product]
assumptions:
  pricetags.Catalog: product
```

`una contract` shows the same for one function, which is what a reviewer of `tag` checks:

```text include="day-to-day/expected/commands/contract.txt"
$ una contract pricetags.tag
--- The tag printed on the shelf for `sku` during a sale of `off` percent.
pub tag(sku: Text, off: Percent) -> Text
  uses @catalog: Catalog[product]
```

Finally, `una build .` writes the executable that the store runs:

```text include="day-to-day/expected/commands/build.txt"
$ una build .
built target/una/pricetags
```

Every one of these commands exits with code 0 on this package, so a release script can run them in turn and stop at the first that does not. The order goes from the cheapest question to the most expensive one: formatting needs no types, the checks need no run, and the examples need a package that checks. A **continuous integration** service, which runs such a script on every proposed change, can add `--json` to each command and keep the documents, so that the report of every release can be compared with the one before it.

## 18.7 Testing it

### Values worked out by hand

The examples cover the price and the tag: a normal discount, the stop at cost, the formatting of cents, and a SKU the catalog does not list, each with a value worked out by hand. The last one installs the catalog with `given`, as `main` does with `with`.

```una include="day-to-day/src/pricetags.una#L67-L82" title="day-to-day/src/pricetags.una" caption="the examples"
example "a sale takes the percent off the price"
  do sale_price(Product(sku: "LAMP-01", price: 1990, cost: 1200), off: 30)
  expect result == 1393

example "a sale price stops at cost"
  do sale_price(Product(sku: "DESK-02", price: 12900, cost: 11000), off: 30)
  expect result == 11000

example "cents are shown with two digits"
  do shown(1905)
  expect result == "19.05"

example "a SKU the catalog does not list gets no price"
  given @catalog = listed(sample())
  do tag("CHAIR-09", off: 30)
  expect result == "CHAIR-09  not in the catalog"
```

### Only the handlers an example installs

`una test .` runs each example in turn, with only the handlers its `given` lines install: an example can never reach the real catalog, or the console, by accident. With `--json`, each example in the document also carries its trace, the operations its `do` line performed; each `expect performed` line checks that one operation is in it.

### What an example checks that a proof does not

An example and a proof check different things. The verifier proves that `sale_price` is never below cost, for every product and every percent. The examples check that the numbers are the ones a person expects: that 30 percent off 19.90 is 13.93, which no `ensures` clause states. A proof says "never below cost"; an example says "13.93". A function with a contract still needs an example of its ordinary case, and a function whose result has no rule to prove, such as `shown`, needs examples for its edge cases, such as a price with fewer than 10 cents.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L7"
example pricetags "a sale takes the percent off the price" ... ok
example pricetags "a sale price stops at cost" ... ok
example pricetags "cents are shown with two digits" ... ok
example pricetags "a SKU the catalog does not list gets no price" ... ok

4 examples: 4 passed, 0 failed
```

## 18.8 Common mistakes

Each mistake below is a small change to `day-to-day/src/pricetags.una`, followed by what `una check .` reports, how to read it, and which tool repairs it.

### A layout of your own (U7001)

:::mistake
Put the body of the handler's operation on its own line:

```diff include="day-to-day..mistakes/1:src/pricetags.una" context="1" title="src/pricetags.una"
--- a/src/pricetags.una
+++ b/src/pricetags.una
@@ -50,3 +50,4 @@
 handler listed(products: Map[Text, Product]) for Catalog
-  op product(sku) = products.get(key: sku)
+  op product(sku) =
+    products.get(key: sku)
 
```

```text include="mistakes/1/expected/rendered.txt"
[U7001] Error: lines 51 to 52 are not in canonical form
    ╭─[ src/pricetags.una:51:1 ]
    │
 51 │ ╭─▶   op product(sku) =
 52 │ ├─▶     products.get(key: sku)
    │ │
    │ ╰──────────────────────────────── lines 51 to 52 are not in canonical form
    │
    │     Help: repair 1: rewrite in canonical form, as `una fmt` does; edit src/pricetags.una:51:1..53:1 to "  op product(sku) = products.get(key: sku)\n"
    │
    │     Note: run `una explain U7001` for an explanation
────╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

*Why:* canonical form is part of the language, so every package reads the same way, and a diff shows only real changes. The arrows mark lines 51 to 52 as one span out of form, and the `Help` line gives the exact text `una fmt .` puts there: the operation on one line. The last line says `una fix` can apply it.

*Fix:* `una fmt .`, or `una fix .`, which formats too. See [U7001](/docs/errors/U7001/).
:::

### A missing label (U2004)

:::mistake
Leave out `off:` in the first example:

```diff include="day-to-day..mistakes/2:src/pricetags.una" context="1" title="src/pricetags.una"
--- a/src/pricetags.una
+++ b/src/pricetags.una
@@ -67,3 +67,3 @@
 example "a sale takes the percent off the price"
-  do sale_price(Product(sku: "LAMP-01", price: 1990, cost: 1200), off: 30)
+  do sale_price(Product(sku: "LAMP-01", price: 1990, cost: 1200), 30)
   expect result == 1393
```

```text include="mistakes/2/expected/rendered.txt#L1,L8"
[U2004] Error: argument 2 of `sale_price` needs a label; only the first argument may go without one
    │ Help: repair 1: label it `off`; edit src/pricetags.una:68:67..68:69 to "off: 30"
```

*Why:* every argument after the first names its parameter, so a call reads the same without the header at hand. The message names the argument by its position, 2, and the repair names the label it needs, `off`, with the exact edit: from column 67 to 69 of line 68, the text `30` becomes `off: 30`.

*Fix:* `una fix .` applies the edit. `una fix --dry-run .` shows it first:

```text include="mistakes/2/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/pricetags.una:68:67 U2004 label it `off`
```

See [U2004](/docs/errors/U2004/).
:::

### A promise the code breaks (U5001)

:::mistake
Return `product.price` where the price falls below cost:

```diff include="day-to-day..mistakes/3:src/pricetags.una" context="1" title="src/pricetags.una"
--- a/src/pricetags.una
+++ b/src/pricetags.una
@@ -30,3 +30,3 @@
   let discounted = product.price - product.price * off / 100
-  if discounted < product.cost then product.cost else discounted
+  if discounted < product.cost then product.price else discounted
 
```

```text include="mistakes/3/expected/rendered.txt#L1,L18"
[U5001] Error: postcondition of `sale_price` is refuted
    │ Note 2: counterexample: off = 0, product = Product#0, product.cost = 1, product.price = 0, result = 0
```

*Why:* a product can cost more than its price, as in the counterexample, and then the function returns a value below cost. Read the counterexample field by field: `product = Product#0` is a placeholder for the record, and its fields that matter follow, a cost of 1 and a price of 0. With those values the discounted price, 0, is below cost, so the changed line returns `product.price`, 0, and `result = 0` is not at least the cost of 1.

*Fix:* return `product.cost` on that path. `una fix` has nothing to apply: the repairs have no edit. See [U5001](/docs/errors/U5001/).
:::

### A requirement that does not exist (U1006)

:::mistake
Mistype the requirement's name:

```diff include="day-to-day..mistakes/4:src/pricetags.una" context="1" title="src/pricetags.una"
--- a/src/pricetags.una
+++ b/src/pricetags.una
@@ -27,3 +27,3 @@
   ensures result >= product.cost
-  derived from PRICING_1
+  derived from PRICING_2
 =
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U1006] Error: requirement `PRICING_2` is not declared in this package
```

*Why:* a `derived from` must name a requirement of the package, or `una trace` would follow a link to nothing. U1006 is in the `names` domain: a name that resolves to nothing, found at tier 0, before any proof.

*Fix:* correct the name, or declare the requirement. See [U1006](/docs/errors/U1006/).
:::

### A capability that is not there (U3001)

:::mistake
Call `tag` in `main` without installing a catalog:

```diff include="day-to-day..mistakes/5:src/pricetags.una" context="1" title="src/pricetags.una"
--- a/src/pricetags.una
+++ b/src/pricetags.una
@@ -63,3 +63,3 @@
   for sku in ["LAMP-01", "DESK-02", "CHAIR-09"]
-    let line = tag(sku, off: 30) with @catalog = listed(sample())
+    let line = tag(sku, off: 30)
     @console.print(line)
```

```text include="mistakes/5/expected/rendered.txt#L1,L8"
[U3001] Error: `tag` needs `@catalog: Catalog[product]`, which is not in scope here
    │ Help: repair 1 (widens authority: the function then holds this authority, and every caller must hold it too: check that the operation belongs to this function's job): declare `uses @catalog: Catalog[product]` in the header; edit src/pricetags.una:61:32..61:32 to "\n  uses @catalog: Catalog[product]"
```

The repair is marked `(widens authority: …)`: it would declare the capability in `main`'s header, which gives `main` a power it does not have, so `una fix` does not apply it:

```text include="mistakes/5/expected/commands/fix.txt"
$ una fix --dry-run .
skipped src/pricetags.una:61:32 U3001 declare `uses @catalog: Catalog[product]` in the header: widens authority
```

*Why:* `tag` needs a catalog, and `main` has none in scope. Even with the widening, `main` could not run: `main` may only do what the host grants it, and the catalog is the package's own capability, which no grant provides.

*Fix:* install a handler for the call with `with @catalog = listed(sample())`, as the program does. See [U3001](/docs/errors/U3001/).
:::

## 18.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's function and example added. `una test .` fails there until the exercise is done. Work in the start package's directory, and use the loop of this chapter: `una fmt .`, `una check .`, read each diagnostic from its first line, then `una test .`.

### Exercise 1: a clearance price

::::exercise
A clearance takes 5.00 off, never below cost. The start package has a first attempt, which `una check .` rejects, and an example:

```una include="exercises/1/start/src/pricetags.una#clearance_price" title="exercises/1/start/src/pricetags.una"
--- The price of a product on clearance: 5.00 off, never below cost. Exercise 1: make the
--- verifier accept it.
pub clearance_price(product: Product) -> Cents
  ensures result >= product.cost
  derived from PRICING_1
=
  if product.price > product.cost then product.price - 500 else product.cost
```

```una include="exercises/1/start/src/pricetags.una#L92-L94" title="exercises/1/start/src/pricetags.una"
example "a clearance takes 5.00 off, but stops at cost"
  do clearance_price(Product(sku: "LAMP-01", price: 1500, cost: 1200))
  expect result == 1200
```

`una check .` reports two refuted obligations with the same counterexample:

```text include="exercises/1/start/expected/diagnostics.txt"
error U5001 at src/pricetags.una:90:40: refinement `result >= 0` is refuted
  counterexample: product = "Product#0", product.cost = 0, product.price = 1, result = -499
error U5001 at src/pricetags.una:90:40: postcondition of `clearance_price` is refuted
  counterexample: product = "Product#0", product.cost = 0, product.price = 1, result = -499
```

The first is the refinement of the result, a `Cents`; the second is the `ensures` clause. Both fail on the same path.

:::hint
*Hint:* compute the result for the counterexample by hand: a price of 1 and a cost of 0. The `if` takes its first branch, since 1 is above 0, and returns 1 - 500. The test in the `if` compares the wrong value: it should ask whether the price after the 5.00 is still above cost.
:::

Check your answer with `una check .`, then `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Compare the discounted price with the cost, not the price:

```diff include="exercises/1/start..exercises/1/answer:src/pricetags.una" context="1" title="src/pricetags.una"
--- a/src/pricetags.una
+++ b/src/pricetags.una
@@ -83,4 +83,3 @@
 
---- The price of a product on clearance: 5.00 off, never below cost. Exercise 1: make the
---- verifier accept it.
+--- The price of a product on clearance: 5.00 off, never below cost.
 pub clearance_price(product: Product) -> Cents
@@ -89,3 +88,3 @@
 =
-  if product.price > product.cost then product.price - 500 else product.cost
+  if product.price - 500 > product.cost then product.price - 500 else product.cost
 
```
:::
::::

### Exercise 2: a basket

::::exercise
The till needs the total of a basket during the sale. Write the body of `basket_total`, which asks the catalog for each SKU and adds up the sale prices; a SKU the catalog does not list adds nothing. The start package has the stub and an example:

```una include="exercises/2/start/src/pricetags.una#basket_total" title="exercises/2/start/src/pricetags.una"
--- The total of a basket during a sale of `off` percent. A SKU the catalog does not list
--- adds nothing. Exercise 2: write the body.
pub basket_total(skus: List[Text], off: Percent) -> Cents
  uses @catalog: Catalog[product]
=
  0
```

```una include="exercises/2/start/src/pricetags.una#L91-L94" title="exercises/2/start/src/pricetags.una"
example "a basket adds the sale prices of the products it lists"
  given @catalog = listed(sample())
  do basket_total(["LAMP-01", "DESK-02", "CHAIR-09"], off: 30)
  expect result == 12393
```

:::hint
*Hint:* a `for` loop over the SKUs ([section 10.1](/learn/collections/#s10-1)), a `let edit total: Cents = 0` ([section 9.2](/learn/loops/#s9-2)), and a `when` on what the catalog gives, with one arm for `Some(product)` and one for `None`. The verifier proves that the total stays a `Cents`, since each sale price is one. When you are done, `una contract pricetags.basket_total` should show the same `uses` as the stub: the loop adds no power.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/2/start/expected/commands/test.txt#L6-L10"
example pricetags "a basket adds the sale prices of the products it lists" ... FAILED
  src/pricetags.una:94: expect result == 12393
  it is false, with `result` = `0`

5 examples: 4 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Replace the body:

```diff include="exercises/2/start..exercises/2/answer:src/pricetags.una" context="1" title="src/pricetags.una"
--- a/src/pricetags.una
+++ b/src/pricetags.una
@@ -84,3 +84,3 @@
 --- The total of a basket during a sale of `off` percent. A SKU the catalog does not list
---- adds nothing. Exercise 2: write the body.
+--- adds nothing.
 pub basket_total(skus: List[Text], off: Percent) -> Cents
@@ -88,3 +88,9 @@
 =
-  0
+  let edit total: Cents = 0
+  for sku in skus
+    let found = @catalog.product(sku)
+    total = when found
+      is Some(product) -> total + sale_price(product, off: off)
+      is None -> total
+  total
 
```

`una contract pricetags.basket_total` shows that the basket may ask the catalog and nothing else:

```text include="exercises/2/answer/expected/commands/contract.txt"
$ una contract pricetags.basket_total
--- The total of a basket during a sale of `off` percent. A SKU the catalog does not list
--- adds nothing.
pub basket_total(skus: List[Text], off: Percent) -> Cents
  uses @catalog: Catalog[product]
```
:::
::::

### Exercise 3: two requirements

::::exercise
The store adds a second rule: a member never pays more than the shelf price. `member_price` takes 1.00 off and is derived from both requirements. The start package adds the requirement, the function and two examples:

```una include="exercises/3/start/src/pricetags.una#L84-L105" title="exercises/3/start/src/pricetags.una"
requirement PRICING_2
  text "A member never pays more than the price on the shelf"
  source human
  owner pricing
  status active

--- The price a member pays: 1.00 off, never below cost and never above the shelf price.
--- Exercise 3: make the verifier accept it, without dropping either requirement.
pub member_price(product: Product) -> Cents
  ensures result >= product.cost
  ensures result <= product.price
  derived from PRICING_1, PRICING_2
=
  if product.price - 100 < product.cost then product.cost else product.price - 100

example "a member pays 1.00 less"
  do member_price(Product(sku: "LAMP-01", price: 1990, cost: 1200))
  expect result == 1890

example "a member price stops at cost"
  do member_price(Product(sku: "DESK-02", price: 11050, cost: 11000))
  expect result == 11000
```

`una check .` reports:

```text include="exercises/3/start/expected/diagnostics.txt"
error U5001 at src/pricetags.una:97:46: postcondition of `member_price` is refuted
  counterexample: product = "Product#0", product.cost = 1, product.price = 0, result = 1
```

Make the package check without dropping either `ensures` clause, and keep both examples passing.

:::hint
*Hint:* look at the counterexample: a cost of 1 and a price of 0. No result can be at least the cost and at most the price for that product. The function cannot fix that; its callers can promise never to ask. Which clause states what a caller promises ([chapter 5](/learn/contracts/#s5-1))?
:::

Check your answer with `una check .`, then `una test .` and `una trace PRICING_2`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Add a `requires` clause, which every caller then proves:

```diff include="exercises/3/start..exercises/3/answer:src/pricetags.una" context="1" title="src/pricetags.una"
--- a/src/pricetags.una
+++ b/src/pricetags.una
@@ -90,4 +90,6 @@
 --- The price a member pays: 1.00 off, never below cost and never above the shelf price.
---- Exercise 3: make the verifier accept it, without dropping either requirement.
+--- A product whose cost is above its price cannot meet both requirements, so callers prove
+--- that it is not one.
 pub member_price(product: Product) -> Cents
+  requires product.cost <= product.price
   ensures result >= product.cost
```

`una trace PRICING_2` shows the second requirement reaching `member_price`, with every obligation proven:

```text include="exercises/3/answer/expected/commands/trace.txt"
$ una trace PRICING_2
requirement PRICING_2 (active)
  text "A member never pays more than the price on the shelf"
  source human
  owner pricing
pricetags.member_price
  requires product.cost <= product.price
  ensures result >= product.cost
  ensures result <= product.price
  proven   ob-f6655d5a7e9c refinement    result >= 0
  proven   ob-077e1c646169 postcondition result >= product.cost
  proven   ob-592d56ba992b postcondition result <= product.price
```
:::
::::

## 18.10 Recap and reference

### For agents

:::agents
Every command prints one JSON document with `--json`, its `schema` key first. The run of the day-to-day program, with its trace:

```json include="day-to-day/expected/commands/run.txt#L2"
{"schema":"una.run/1","tier":1,"status":"ok","output":["LAMP-01  19.90 now 13.93","DESK-02  129.00 now 110.00","CHAIR-09  not in the catalog"],"failure":null,"diagnostics":[],"trace":[{"seq":1,"instance":"with:listed#1","capability":"Catalog","op":"product","args":{"sku":"\"LAMP-01\""},"outcome":{"kind":"ok","value":"Some(Product(sku: \"LAMP-01\", price: 1990, cost: 1200))"}},{"seq":2,"instance":"host:Console","capability":"Console","op":"print","args":{"line":"\"LAMP-01  19.90 now 13.93\""},"outcome":{"kind":"ok","value":"unit"}},{"seq":3,"instance":"with:listed#2","capability":"Catalog","op":"product","args":{"sku":"\"DESK-02\""},"outcome":{"kind":"ok","value":"Some(Product(sku: \"DESK-02\", price: 12900, cost: 11000))"}},{"seq":4,"instance":"host:Console","capability":"Console","op":"print","args":{"line":"\"DESK-02  129.00 now 110.00\""},"outcome":{"kind":"ok","value":"unit"}},{"seq":5,"instance":"with:listed#3","capability":"Catalog","op":"product","args":{"sku":"\"CHAIR-09\""},"outcome":{"kind":"ok","value":"None"}},{"seq":6,"instance":"host:Console","capability":"Console","op":"print","args":{"line":"\"CHAIR-09  not in the catalog\""},"outcome":{"kind":"ok","value":"unit"}}]}
```

Each event names the handler instance that answered, such as `with:listed#1`, so an agent can check what a run asked of each service. The loop for an agent: `una --json check .`, apply what `una fix .` applies, read the remaining repairs by `rank` and `escape_cost`, then `una --json test .`. `una fix` never widens authority, never edits `una.toml`, and never applies an escape. Exit codes: 0 success, 1 an error, an unproven obligation or a failed example, 2 a usage error, 3 an internal error.
:::

### Recap

:::recap
- `una check .` is the loop. `--tier 0` skips the proofs for a quick answer; run the full check before a change is done.
- `una fix --dry-run .` shows the exact repairs, and `una fix .` applies them and formats. It never widens authority, applies an escape, or edits `una.toml`.
- A diagnostic has a code, places, ranked repairs, and for a proof, an obligation and a counterexample. `una explain` explains any code.
- `--json` turns every command's output into one document with a `schema` key, and exit codes say the same as the text.
- `una obligations`, `una contract` and `una trace` show what was proven, what a function promises, and which code carries a rule.
- `una report` shows what the package may do and trusts; compare it between releases.
- `una run`, `una test` and `una build` check first, and run nothing that does not check.
:::

### Reference

:::reference
- Command line: [all commands](/docs/cli/), [`una check`](/docs/cli/check/), [`una fmt`](/docs/cli/fmt/), [`una fix`](/docs/cli/fix/), [`una explain`](/docs/cli/explain/), [`una obligations`](/docs/cli/obligations/), [`una contract`](/docs/cli/contract/), [`una trace`](/docs/cli/trace/), [`una report`](/docs/cli/report/), [`una run`](/docs/cli/run/), [`una test`](/docs/cli/test/), [`una build`](/docs/cli/build/), [`una lsp`](/docs/cli/lsp/)
- For agents: [Una for agents](/docs/agents/), [JSON output and diagnostics](/docs/agents/json/), [repairs](/docs/agents/repairs/), [the build report](/docs/agents/build-report/)
- Construct pages: [`ensures`](/docs/language/functions/ensures/), [`requires`](/docs/language/functions/requires/), [`requirement` and `derived from`](/docs/language/requirements/requirement/), [`where` and refinements](/docs/language/types/where/), [`example`](/docs/language/examples/example/)
- Diagnostics: [U0001](/docs/errors/U0001/), [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1006](/docs/errors/U1006/), [U2004](/docs/errors/U2004/), [U3001](/docs/errors/U3001/), [U5001](/docs/errors/U5001/), [U7001](/docs/errors/U7001/), and [all codes](/docs/errors/)
- Specification: [diagnostics, agent ABI and project files](/docs/spec/13-diagnostics-and-abi/), [verification](/docs/spec/12-verification/), [canonical form](/docs/spec/15-canonical-form/), [native backend](/docs/spec/16-native-backend/)
:::
