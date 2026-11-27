---
learn: "19"
title: Editions
editions: ["0.1", "0.2", "0.3", "0.4"]
codes: [U0101, U0103, U1002, U2001, U2002, U2028, U3023, U3025, U3026, U5001, U7002]
time: 35
builds: A shelf-label printer on the edition 0.3 preview, with a dry run the checker enforces
prerequisites: ["7", "12", "13", "16", "18"]
template: 2
nav: ["An edition per package", "What edition 0.2 adds", "Edition 0.3, a preview", "Moving a package forward", "Edition 0.4, a preview", "Day-to-day: shelf-label printer", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 19 Editions


A language that grows has to add keywords and tighten rules, and a program written last year must still mean what it meant. Una does this with editions: each package names the edition of the language it is written in, and every release of `una` keeps each stable edition, whose rules are final, exactly as it was. This chapter shows what an edition is, what editions `0.2` and `0.3` add, and how to move a package from one edition to the next, letting the checker and `una fix` find what has to change.

## What you'll build

:::build
A shelf-label printer for a store, on edition `0.3`. It reads a stock export, the list of stock lines that another system of the store writes out, prints a label for every line with stock, and has a dry run that counts the labels without printing any. The dry run is not a convention: the checker proves that no label is printed when `dry_run` is true. `main` makes a dry run, then a real one:

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
- move a package to edition `0.4`, a preview, whose manifest is `ita.una`, with `una migrate`;
- lock a function's authority in `una.toml`, so that a change to it shows up in review.
:::

## Why it works this way

Languages that grow without editions face a choice. Either a new keyword, a word the language keeps for itself, breaks every program that used the word as a name, or the language never adds one. A rule that becomes stricter, such as one that rejects code that can never run, breaks programs that passed yesterday, and the team that maintains them finds out on the day a compiler is upgraded.

Una separates the two things a release changes:

:::steps
1. **The compiler improves for every edition.** A new release fixes bugs, adds explanations and makes the tools better, for every package.
2. **The language changes only in a new edition.** New keywords, new constructs and stricter rules come with an edition, and a package gets them only when its manifest names that edition.
3. **Editions are cumulative.** Edition `0.3` has every construct and rule of `0.2`, and `0.2` has every construct of `0.1`. Moving a package forward never removes a construct. It can reject code that a stricter rule no longer allows or a name that became a keyword, and a few prelude functions and reports change too ([section 19.2](#s19-2)). Edition `0.3` also accepts some code that `0.2` rejects ([section 19.3](#s19-3)).
:::

So upgrading `una` never changes what a stable edition accepts or rejects, except to fix a soundness or security error: a bug that let the checker accept a program it should have rejected. Moving a package to a new edition is a separate step, a change to one line of `una.toml`, which you make when you are ready and review like any other change.

> [!KEY]
> A package's edition is a line of its manifest: `una.toml`, or `ita.una` from edition `0.4`. Upgrading `una` keeps the meaning of every stable edition, and a later edition adds constructs and, with few exceptions, tightens rules.

## 19.1 An edition is part of the package


### What an edition is

A board game sold for many years often comes in editions. The second edition adds new cards and fixes a rule that players found unfair, and the box says which edition it is. Friends who own the first edition still play by its rules, and their game still works; nobody comes to their house to change the cards.

Una works the same way, with two words that are easy to mix up:

- A **release** is a version of the `una` program itself, such as una 0.4.0. You install a release, and a newer one replaces it.
- An **edition** is a version of the Una language: its keywords, its constructs and its rules. Una 0.4.0 serves five, `0.1` to `0.5`, and this chapter uses the first four.

A **keyword** is a word the language keeps for itself, such as `if`, `for` or `uses`: it starts a piece of syntax, so it cannot name a value, a parameter or a field. A **construct** is one form of code with its own syntax and meaning, such as a `for` loop, a kind or a `uses` clause.

Each package names its edition in `una.toml`, and a release checks each package by the rules of the edition it names. One release serves several editions at once, so installing a newer release does not change the language your packages are written in. Only you change that, by editing one line.

Each example of this chapter is a package, made as [chapter 2](/learn/numbers/#each-step-is-a-package) explains, and the chapter's download, `19-editions.tar.gz`, holds them all.

### Why a language needs editions

Here is a small package in edition `0.1`. It counts how many units arrived on a shelf, and names its parameters `old` and `new`:

```toml include="steps/01-arrived/una.toml" title="steps/01-arrived/una.toml"
[package]
name = "restock"
version = "0.1.0"
edition = "0.1"

[run]
entry = "restock"
grants = ["console"]
```

```una include="steps/01-arrived/src/restock.una" title="steps/01-arrived/src/restock.una" verified="check, run"
module restock

--- How many units arrived: the count `new` on the shelf now, less the count `old` from before.
arrived(old: Int, new: Int) -> Int = new - old

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{arrived(4, new: 10)} units arrived")
```

```text include="steps/01-arrived/expected/output.txt"
6 units arrived
```

In edition `0.1`, `old` is an ordinary word. Edition `0.2` made it a keyword: inside an `ensures` clause, `old(x)` names the value an `edit` parameter had when the call began ([chapter 5](/learn/contracts/#s5-2)). Check the same code under edition `0.2`, with only the edition line changed:

```diff include="steps/01-arrived..steps/02-arrived-0-2:una.toml" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -1,7 +1,7 @@
 [package]
 name = "restock"
 version = "0.1.0"
-edition = "0.1"
+edition = "0.2"
 
 [run]
 entry = "restock"
```

```text include="steps/02-arrived-0-2/expected/rendered.txt"
[U0101] Error: `old` is a reserved keyword, so it cannot name a binding
   ╭─[ src/restock.una:4:9 ]
   │
 4 │ arrived(old: Int, new: Int) -> Int = new - old
   │         ─┬─
   │          ╰─── `old` is a reserved keyword, so it cannot name a binding
   │
   │ Help: repair 1: choose another name, such as `old_value`
   │
   │ Note: run `una explain U0101` for an explanation
───╯
```

U0101: a keyword cannot name a binding. The code did not change; the language did. In a language without editions, that would happen to this package on the day una was upgraded, whether or not anyone was ready.

With editions, nothing happens to it. The package says `edition = "0.1"`, and every release that serves edition `0.1` checks it by the rules of `0.1`, where `old` is a name. It moves to `0.2` only when someone changes that line, and [section 19.4](#s19-4) shows how.

### How to write the edition

`[package] edition` names the edition, as a text in quotes. It is a required key of `una.toml`, with `name` and `version`.

#### `edition = "0.1"`, `"0.2"` or `"0.3"`

Each of the three editions is written the same way:

- `edition = "0.1"` is the first edition. It has kinds, functions, lists, contracts, capabilities and labels.
- `edition = "0.2"` is the edition of most of this tutorial. It adds loops ([chapter 9](/learn/loops/)), the `edit` and `take` parameter modes ([chapter 16](/learn/memory/#s16-2) teaches `edit`, and [section 16.3](/learn/memory/#s16-3) `take`), `together` ([chapter 15](/learn/concurrency/#s15-1)), maps and more ([section 19.2](#s19-2)).
- `edition = "0.3"` is a preview, with stricter rules and a few constructs that narrow what a program may do ([section 19.3](#s19-3)).

Edition `0.4`, also a preview, is not written in `una.toml`: a package of edition `0.4` describes itself in a file of its own, `ita.una` ([section 19.5](#s19-5)), so `edition = "0.4"` in `una.toml` is U7002, whose message says to run `una migrate`. Edition `0.5`, a later preview, is described in `ita.una` too; this book does not use it yet.

#### An edition una does not know

An edition this release does not serve is U7002, the code for a problem in `una.toml`:

```diff include="steps/01-arrived..steps/03-edition-unknown:una.toml" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -1,7 +1,7 @@
 [package]
 name = "restock"
 version = "0.1.0"
-edition = "0.1"
+edition = "0.9"
 
 [run]
 entry = "restock"
```

```text include="steps/03-edition-unknown/expected/rendered.txt"
[U7002] Error: edition `0.9` is not supported; the editions are "0.1", "0.2", "0.3", "0.4" and "0.5"
   ╭─[ una.toml:4:11 ]
   │
 4 │ edition = "0.9"
   │           ──┬──
   │             ╰──── edition `0.9` is not supported; the editions are "0.1", "0.2", "0.3", "0.4" and "0.5"
   │
   │ Note: run `una explain U7002` for an explanation
───╯
```

The mark is on the value, and the message lists the editions this release serves, `0.4` and `0.5` included.

#### A manifest without an edition

Leaving the line out is U7002 too, at the `[package]` table that lacks it:

```text include="steps/04-no-edition/expected/rendered.txt"
[U7002] Error: [package] has no `edition`
   ╭─[ una.toml:1:2 ]
   │
 1 │ [package]
   │  ───┬───
   │     ╰───── [package] has no `edition`
   │
   │ Note: run `una explain U7002` for an explanation
───╯
```

A package has no default edition: its manifest must state one.

#### A single file

A single `.una` file checked on its own, outside a package, as in `una check shelf.una`, has no `una.toml`. It has edition `0.1`.

### A stock list in edition `0.1`

This step is a stock list in edition `0.1`. It has a record kind, a function and a list, and its total is computed with `fold` ([chapter 10](/learn/collections/#s10-3)), since edition `0.1` has no loops:

```toml include="steps/05-edition-0-1/una.toml" title="steps/05-edition-0-1/una.toml"
[package]
name = "shelf"
version = "0.1.0"
edition = "0.1"

[run]
entry = "shelf"
grants = ["console"]
```

```una include="steps/05-edition-0-1/src/shelf.una" title="steps/05-edition-0-1/src/shelf.una" verified="check, run"
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

`una run .` prints:

```text include="steps/05-edition-0-1/expected/output.txt"
2 lines, 5 units
```

### How editions behave

#### One binary serves every edition

`una --version` prints the version of `una`, the editions it serves, which of them are previews, and the version of Z3 built into it. At this release it lists the editions `0.1` to `0.5`, of which `0.3`, `0.4` and `0.5` are previews. Every one of them is checked by the same binary, so one machine can check, test and build packages of different editions side by side.

#### Stable editions and previews

An edition is either **stable** or a **preview**:

| Edition | Status | What it promises |
| --- | --- | --- |
| `0.1` | Stable | A later release does not change what it accepts or rejects, except to fix a soundness or security error |
| `0.2` | Stable | The same promise |
| `0.3` | Preview | It may still get stricter in a later release, never looser for the programs `0.2` can express |
| `0.4` | Preview | It may change in a later release, never in silence: a construct that changes or leaves gives a diagnostic; described in `ita.una` ([section 19.5](#s19-5)) |
| `0.5` | Preview | A later preview, also described in `ita.una`; this book does not use it yet |

A package on a stable edition can stay there for as long as it likes.

#### One number for a release and its edition

A version of `una` has three numbers, such as 0.5.1. The first two name the release it belongs to, written R0.5. A release is published in **increments**, and each increment is a version of `una` that you install: una 0.5.0 is increment R0.5.0, and una 0.5.1 is increment R0.5.1. An edition takes its number from its release, so edition `0.5` is the edition of release R0.5.

| Version of `una` | Its release | Edition of that release | Editions it serves |
| --- | --- | --- | --- |
| 0.4.0 | R0.4 | `0.4` | `0.1` and `0.2`, stable; `0.3`, `0.4` and `0.5`, previews |
| 0.5.0 | R0.5, increment R0.5.0 | `0.5` | The same |
| 0.5.1 | R0.5, increment R0.5.1 | `0.5` | The same |

The editions before `0.4` follow the same rule: each carries the number of the release that introduced it. A release that changes no syntax has no edition of its own.

The shared number says where an edition comes from, not whether it is stable. una 0.4.0 shipped edition `0.4` as a preview, and una 0.5.0 and 0.5.1 still serve it as one. All three also serve edition `0.5`, as an early preview whose rules are still landing. An edition stays a preview until a release declares it stable, so ask the `una` you have: `una --version` lists its editions and names the previews.

#### Words reserved for later editions

Some words were set aside before the editions that use them existed. In edition `0.1`, `edit`, `take` and `together` are **reserved**: not keywords yet, and not names either. Using one gives U0103, whose message names the edition that has it, written with a `v`, such as `` `edit` is reserved for v0.2 (memory model) ``, or says `a later edition` for a word that no edition has yet. Reserving a word early keeps it free: no `0.1` package can use `edit` as a name, so no `0.1` package breaks when `0.2` makes it a keyword. `old` was not reserved in `0.1`, which is why the package of [Why a language needs editions](#why-a-language-needs-editions) could use it. Nor was `weak`, a name in `0.1` that edition `0.2` reserves for a later edition ([The keywords `0.2` adds](#the-keywords-02-adds)).

#### What an edition fixes, and what improves with every release

What an edition fixes is the language a package is written in: its keywords, its constructs, its rules and the headers of the prelude, the functions every module has without an import ([chapter 3](/learn/text-and-conditions/#s3-2)). For example, `min`, `max` and `sum` work on `Int` in edition `0.1`, and a later release keeps those headers for it, while edition `0.2` makes them generic: they work on any type with the right constraint, such as `Ord` for `min` ([chapter 4](/learn/kinds/#s4-4)). What improves with every release, for every edition, is everything around the language: the wording of messages, the explanations of `una explain`, the repairs, the speed of the checks and the tools of [chapter 18](/learn/tools/).

### Check yourself: a word reserved for later

This package is in edition `0.1`, and names a parameter `take`:

```una include="steps/06-take/src/shelf.una" title="steps/06-take/src/shelf.una"
module shelf

--- The units left after a customer takes `take` of `units`.
left(units: Int, take: Int) -> Int = units - take

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{left(10, take: 3)} left")
```

Does it check? If not, what does `una fix --dry-run .` offer?

:::answer Show the answer
It does not check. `take` is reserved in edition `0.1`, so each of its three uses is U0103; the first:

```text include="steps/06-take/expected/rendered.txt#L1-L10"
[U0103] Error: `take` is reserved for v0.2 (memory model)
   ╭─[ src/shelf.una:4:18 ]
   │
 4 │ left(units: Int, take: Int) -> Int = units - take
   │                  ──┬─
   │                    ╰─── `take` is reserved for v0.2 (memory model)
   │
   │ Help: repair 1: rename it to `the_take`; edit src/shelf.una:4:18..4:22 to "the_take"
   │
   │ Note: run `una explain U0103` for an explanation
```

`una fix --dry-run .` would rename every use:

```text include="steps/06-take/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/shelf.una:4:18 U0103 rename it to `the_take`
fixed src/shelf.una:4:46 U0103 rename it to `the_take`
fixed src/shelf.una:9:29 U0103 rename it to `the_take`
```

Here the rename is right, since `take` is meant as a name: `the_take` works, and a better name, such as `taken`, works too. When a reserved word stands as the construct of a later edition, no rename is offered; [Using a construct of a later edition](#using-a-construct-of-a-later-edition-u0103) shows that case.
:::

## 19.2 What edition `0.2` adds


### What changes from `0.1` to `0.2`

Edition `0.2` changes four things, each of which this section shows. Every rule this section states for `0.2` holds in `0.3` too, since editions are cumulative:

- **Constructs.** New ways to write code, such as `for` loops and `let edit`.
- **Keywords.** Words that become part of the language, `edit`, `take`, `old` and `together`, and one word reserved for a later edition, `weak`.
- **Rules.** A few rules that are stricter or different, such as the names a kind may take.
- **The prelude.** The functions every module has without an import, some of which become generic.

### Moving the stock list to `0.2`

Move the stock list of [section 19.1](#s19-1) to `0.2`, and two things that `0.1` rejects become possible: a `for` loop with a `let edit` binding, and the interpolation of a whole list.

```diff include="steps/05-edition-0-1..steps/07-edition-0-2:una.toml" title="una.toml"
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

```diff include="steps/05-edition-0-1..steps/07-edition-0-2:src/shelf.una" title="src/shelf.una"
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

```text include="steps/07-edition-0-2/expected/output.txt"
2 lines, 5 units
[Line(sku: "LAMP-01", units: 4), Line(sku: "DESK-02", units: 1)]
```

The code of [section 19.1](#s19-1) also checks, unchanged, with only the edition line moved to `0.2`: moving forward did not require touching it. The changes to the code are ones the new edition allows. `fold` is still there, and still right; the loop is simply easier to read for some code.

### The constructs `0.2` adds

Edition `0.2` adds, among others:

| Construct | Where to read about it |
| --- | --- |
| `for` loops, `let edit`, `edit` and `take` parameters, and `if` without `else` as a statement | [Repeating: `for`](/learn/loops/), [`edit`](/learn/memory/#s16-2), [`take`](/learn/memory/#s16-3), [`if` without `else`](/learn/choices/#s8-1) |
| `together` and `together for` | [Concurrency and parallelism](/learn/concurrency/) |
| `Map`, the text functions and `ParseError`, `Json` | [Maps](/learn/collections/#s10-4), [the text functions](/learn/text-and-conditions/#s3-2), [`ParseError`](/learn/failure/#s7-4), [JSON](/learn/collections/#s10-5) |
| Fixed-width integers such as `U8` and `I64`, with proven overflow | [Numbers](/learn/numbers/#s2-3) |
| Constraints on generics such as `T: Ord`, and `sort` | [Constraints](/learn/kinds/#s4-4), [`sort`](/learn/collections/#sorting-sort) |
| `uses of p` and `fails of p`, header clauses for a function that takes another function as its parameter `p`: the function passed in may then use capabilities and fail, and the caller handles it | [`uses of`](/learn/capabilities/#authority-inside-a-function-argument-uses-of), [`fails of`](/learn/failure/#failing-as-the-function-you-are-given-fails-of), [`uses` in the docs](/docs/language/capabilities/uses/) |
| The interpolation of any value that `==` compares, except a `Hashed`, a fingerprint of secret data that only a host capability computes and that a program cannot read | [Text and conditions](/learn/text-and-conditions/#s3-1) |
| The `Http` capability | [HTTP in the standard library](/docs/std/http/) |

### The keywords `0.2` adds

Edition `0.2` makes four words keywords: `edit`, `take`, `old` and `together`. Each one starts a construct, so in `0.2` none of them can name a binding, a parameter or a field. `edit`, `take` and `together` were reserved in `0.1` already, so no `0.1` package uses them as names. `old` was not, so a `0.1` package may use it, and must rename it to move, as [Why a language needs editions](#why-a-language-needs-editions) showed.

Edition `0.2` also reserves a word for a later edition: `weak`. In `0.1` it is an ordinary name, so a `0.1` package may use it, and must rename it to move. This package names a parameter `weak`, for a week when sales are slow. It checks and runs in `0.1`; in `0.2`, each of its three uses is U0103, the first:

```text include="steps/20-weak-0-2/expected/rendered.txt#L1-L10"
[U0103] Error: `weak` is reserved for a later edition (aliasing)
   ╭─[ src/restock.una:4:26 ]
   │
 4 │ weekly_order(units: Int, weak: Bool) -> Int = if weak then units / 2 else units
   │                          ──┬─
   │                            ╰─── `weak` is reserved for a later edition (aliasing)
   │
   │ Help: repair 1: rename it to `the_weak`; edit src/restock.una:4:26..4:30 to "the_weak"
   │
   │ Note: run `una explain U0103` for an explanation
```

The message says that the word is kept for a later edition, and for what: aliasing. Here the word is meant as a name, so the rename is right, and `una fix --dry-run .` lists it at every use:

```text include="steps/20-weak-0-2/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/restock.una:4:26 U0103 rename it to `the_weak`
fixed src/restock.una:4:50 U0103 rename it to `the_weak`
fixed src/restock.una:9:43 U0103 rename it to `the_weak`
```

`una fix .` applies the three renames, and the package checks in `0.2`. A better name, such as `slow_week`, works too.

One word goes the other way. `with` is a keyword in every edition, for `with @catalog = …` ([chapter 12](/learn/capabilities/#s12-4)). From edition `0.2` on, `with` right after a `.` is a name, the method of a map that adds an entry: `prices.with(key: sku, value: 1990)`.

### The rules that changed

A few rules of `0.2` differ from `0.1`:

- **Built-in type names.** A kind, a variant or a capability cannot take the name of a built-in type such as `Text`, `List`, `Map` or `U8` (U1002). In `0.1`, a kind with a built-in type's name, even `Text`, shadows that type in its module. In `0.2` this is U1002.
- **Equality on type parameters.** A public generic function that compares two values of a type parameter `T` must write the constraint `[T: Eq]` (U2026, [chapter 4](/learn/kinds/#s4-4)); `0.1` inferred it.
- **The prelude.** `min`, `max`, `sum` and `contains` become generic over constrained types, and `sort`, `set` and `empty_map` are new.
- **Recursive kinds,** kinds with a field of their own kind ([chapter 8](/learn/choices/#s8-4)), no longer need that field inside a `List` or an `Option`, but must be able to end: some variant, such as a `Lit(value: Int)` in an expression kind, holds no value of the kind itself.
- **Test reports.** In `0.2`, a failed example's report shows labeled values, data marked secret or internal ([chapter 17](/learn/information-flow/)), in full. `0.1` hides only the labeled fields of a record, writing a level such as `<redacted:confidential>` in their place; a labeled value that is not a field, such as a `confidential Int` result, is shown in full there too.

### What a move from `0.1` can need

So moving a `0.1` package to `0.2` can still need changes, in five places: a name that became a keyword, such as a binding called `old`; a name that `0.2` reserves, such as `weak`, which is U0103; a kind named like a built-in type, which is U1002 in `0.2`; a public generic function that compares values of a type parameter without `[T: Eq]`, which is U2026; and a call that relied on a prelude header of `0.1`. The checker reports each one at its place, with the code and a repair, so the move is a list of small, local changes rather than a search through the package.

### Check yourself: a kind named `Map`

This package is in edition `0.1`. It declares a record named `Map`, for a floor map of the store, and it checks and runs:

```una include="steps/08-floor-map/src/shelf.una" title="steps/08-floor-map/src/shelf.una" verified="check, run"
module shelf

--- A floor map of the store: the aisle of a department.
kind Map
  department: Text
  aisle: Int

pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = Map(department: "lamps", aisle: 4)
  @console.print("{lamps.department} in aisle {lamps.aisle}")
```

```text include="steps/08-floor-map/expected/output.txt"
lamps in aisle 4
```

Change only its edition to `0.2`. Does it still check?

:::answer Show the answer
No. From edition `0.2` on, `Map` is the built-in type of maps, and a kind cannot take its name:

```text include="steps/09-floor-map-0-2/expected/rendered.txt"
[U1002] Error: `Map` is a built-in type of maps from edition 0.2, so a kind cannot take its name
   ╭─[ src/shelf.una:4:6 ]
   │
 4 │ kind Map
   │      ─┬─
   │       ╰─── `Map` is a built-in type of maps from edition 0.2, so a kind cannot take its name
   │
   │ Note: run `una explain U1002` for an explanation
───╯
```

The mark is on the name in the declaration. Rename the kind, such as to `FloorMap`, and every use of it, and the package checks in `0.2`. The diagnostic has no exact edit, since the new name is a choice.
:::

## 19.3 Edition `0.3`, a preview


### What a preview is

A **preview** is an edition that is still being completed. Its rules arrive one by one, release after release, until every rule planned for it has landed. You can use it today, and in exchange you accept that a later release may reject code it accepts now.

### Why a preview exists

Some rules are worth having before all of their companions are ready. A dry run that the checker proves, as the day-to-day program of this chapter has, is useful the day it lands. A preview lets a package opt into those rules early, and lets the rules be tried on real code before the edition becomes stable. A package that does not opt in sees none of it: edition `0.2` keeps its promise.

### What edition `0.3` adds

Edition `0.3` adds constructs that narrow what a program may do, rules that reject code that can never run, and one rule that accepts code that `0.2` rejects, refined type arguments:

- **Conditions on operations.** `uses @printer: Printer[print_label where not dry_run]` lets the function print a label only where the condition holds, and the verifier proves it at every call of the operation ([chapter 13](/learn/authority/#s13-1)).
- **Locked contracts.** `[contracts]` in `una.toml` locks the `uses` of a public function: its header may grant less, never more ([chapter 13](/learn/authority/#s13-3)).
- **Boundaries.** `[boundaries]` in `una.toml` lists the most a module may ever be given: a call into it may grant only the operations its ceiling names ([chapter 13](/learn/authority/#s13-2)). With it comes a narrowed rebinding: `with @x = @y[ops]` passes a binding narrowed to the operations in brackets ([chapter 13](/learn/authority/#granting-less-at-the-call-with-x-yops)).
- **No dead failure handling.** An `if error` clause under a call that cannot fail is U3025, and `attempt` of a call that cannot fail is U3026.
- **Units of measure.** `measure Gram` declares a unit, and `Int of Gram` is a number of grams, which cannot be mixed with a plain `Int` or with another unit except through an explicit conversion.
- **Refined type arguments.** A refined kind may be the type of a list's elements, as in `List[Units]` with `Units = Int in 0..100`.
- **`test`.** The declaration that runs under `una test`, written `example` in editions `0.1` and `0.2`, is written `test`, with the same `given`, `do` and `expect` lines. An `example` in an edition `0.3` package is U0103, and `una fix .` rewrites the word. `una test .` then prints `test` on each line and counts tests.

The day-to-day program uses the first two, and writes its tests with `test` ([section 19.7](#s19-7)). The rest of this section shows units, refined type arguments and the rules on failure handling.

### Units of measure

A number alone does not say what it counts. 1200 can be grams, cents or units on a shelf, and adding grams to cents is a mistake that no type of `0.2` catches. In `0.3`, a unit is part of the type.

#### A base unit: `measure Gram`

```una include="steps/10-parcel/src/parcel.una" title="steps/10-parcel/src/parcel.una" verified="check, run"
module parcel

--- A unit of weight.
measure Gram

--- What one lamp weighs.
lamp_weight() -> Int of Gram = 1200

--- The weight of a parcel of `units` lamps.
parcel_weight(units: Int) -> Int of Gram = units * lamp_weight()

pub main() -> Unit
  uses @console: Console[print]
=
  let weight = parcel_weight(3)
  let limit: Int of Gram = 5000
  @console.print("{weight} grams, within the limit: {weight <= limit}")
```

```text include="steps/10-parcel/expected/output.txt"
3600 grams, within the limit: true
```

:::steps
1. **`measure Gram`.** Declares a **base unit**, one that is not defined from another, at the top level of a module.
2. **`-> Int of Gram`.** `of` after an integer type gives it a unit. `Int of Gram` is a type of its own: neither `Int` nor any other unit.
3. **`= 1200`.** A literal number takes the unit its place expects, so `1200` here is 1200 grams.
4. **`units * lamp_weight()`.** `*` multiplies the units: a plain count times grams is grams. `+`, `-`, `mod` and the comparisons need the same unit on both sides.
:::

Units exist only while the package is checked: the program prints a plain number, and a unit costs nothing when the program runs.

#### A derived unit, and changing a unit: `convert`, `measured`, `magnitude`

A **derived unit** is defined from units already declared, with a whole-number factor: `measure Kilogram = 1000 * Gram` is a kilogram, a thousand grams, and `measure Milligram = Gram / 1000` would be a thousandth of a gram. A value never changes its unit by itself. Three methods change it, each where you write it, and they are the only ways:

```una include="steps/11-parcel-units/src/parcel.una" title="steps/11-parcel-units/src/parcel.una" verified="check, run"
module parcel

--- A unit of weight.
measure Gram

--- A thousand grams.
measure Kilogram = 1000 * Gram

--- The most a parcel may weigh, as the carrier states it.
parcel_limit() -> Int of Kilogram = 5

--- A scale's reading, a plain number of grams, as a weight.
from_scale(reading: Int) -> Int of Gram = reading.measured()

--- The postage in cents, from a price list of plain numbers: 1 cent for every 10 grams.
postage(grams: Int) -> Int = grams / 10

pub main() -> Unit
  uses @console: Console[print]
=
  let weight = from_scale(3650)
  let limit: Int of Gram = parcel_limit().convert()
  @console.print("{weight} grams, limit {limit} grams, within: {weight <= limit}")
  @console.print("postage: {postage(weight.magnitude())} cents")
```

```text include="steps/11-parcel-units/expected/output.txt"
3650 grams, limit 5000 grams, within: true
postage: 365 cents
```

:::steps
1. **`reading.measured()`.** Gives a plain number the unit that its place expects: here the result type, `Int of Gram`. Use it where a number enters the program without a unit, such as a scale's reading.
2. **`parcel_limit().convert()`.** Changes a value to the unit its place expects, of the same kind of quantity: from kilograms to grams, it multiplies by 1000, the exact ratio. The place must say which unit it expects, here the type of `limit`.
3. **`weight.magnitude()`.** Gives the plain number without its unit, for code that takes a plain `Int`, such as `postage`.
:::

`convert()` works only when the ratio from the value's unit to the expected one is a whole number, as kilograms to grams is. Grams to kilograms would divide, and lose the grams below a thousand, so una rejects it with U2030 rather than round. `measured()` with no expected unit, or `convert()` between units of different quantities, such as grams and meters, is U2030 too.

### Refined type arguments

The type in brackets after a generic type, such as `Int` in `List[Int]`, is a **type argument**: it fills the generic type's type parameter ([chapter 4](/learn/kinds/#s4-4)). In editions `0.1` and `0.2`, a type argument cannot be a refined kind, so a list cannot say that its elements keep a rule: the elements of a `List[Int]` carry no facts. In `0.3` it can:

```una include="steps/12-shelf-counts/src/shelves.una" title="steps/12-shelf-counts/src/shelves.una" verified="check, run"
module shelves

--- Units on a shelf, which holds at most 100.
kind Units = Int in 0..100

--- The counts of this morning's shelves, each a `Units`.
counts() -> List[Units] = [4, 12, 9]

--- The largest count, which is a `Units` too, or 0 for no shelf.
fullest(shelves: List[Units]) -> Units
=
  let edit top: Units = 0
  for units in shelves
    if units > top
      top = units
  top

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("fullest shelf: {fullest(counts())} units")
```

```text include="steps/12-shelf-counts/expected/output.txt"
fullest shelf: 12 units
```

The verifier proves that each element of the literal `[4, 12, 9]` is in `0..100`, and inside the loop it knows that each `units` is a `Units`, so it proves that `top` stays one. In edition `0.2`, the same code is rejected at each such type:

```text include="steps/13-shelf-counts-0-2/expected/rendered.txt#L1"
[U2002] Error: this type argument is the refined kind `Units`, and a refined type cannot instantiate a type parameter; write its base type `Int` and check the refinement where the value is used
```

### Failure handling that no longer runs

A restock list in edition `0.2` computes how many units to order for each line. `order_quantity` once parsed a typed number and could fail, so its callers handled a failure, with an `if error` clause and with `attempt` ([chapter 7](/learn/failure/#s7-3), [section 7.4](/learn/failure/#s7-4)): `if error use 0` gives a default when the call fails, and `attempt` keeps the outcome as a `Result`, `Ok` with the value or `Err` with the failure. It has since become a plain calculation, which cannot fail, and the handling stayed:

```una include="steps/14-restock/src/restock.una" title="steps/14-restock/src/restock.una" verified="check, run"
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

```text include="steps/14-restock/expected/output.txt"
LAMP-01: order 6
SHELF-03: enough
DESK-02: order 1
7 units to order
```

### What `0.3` reports: U3025 and U3026

The `if error use 0` clause never runs, and the `Err` arm of `total` is never taken. They are harmless, but they mislead a reader into thinking `order_quantity` can fail. Edition `0.3` rejects both:

```diff include="steps/14-restock..steps/15-restock-0-3:una.toml" title="una.toml"
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

```text include="steps/15-restock-0-3/expected/rendered.txt"
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

Each diagnostic names its repair. U3025's repair deletes the clause, an exact edit. U3026's repair is a description, because the uses of the `Result` have to be unwrapped by hand. The last line counts one of the two as fixable.

### How a preview behaves

- **It only gets stricter.** For every program that edition `0.2` can express, a later release keeps its result, or adds obligations or errors to it.
- **New constructs only narrow.** A later release may accept a construct that earlier releases reject as a syntax error, such as a condition on an operation. Each such construct only narrows what a program may do: erase it, and you get a program that edition `0.2` accepts.
- **Some code `0.2` rejects becomes accepted.** A later release may also accept code that `0.2` rejects, where a new proof shows it is safe: refined type arguments, which `0.2` rejects with U2002, are the first case.
- **The stable editions do not move.** Whatever happens to `0.3`, a release keeps what `0.1` and `0.2` accept and reject, except to fix a soundness or security error.

> [!IMPORTANT]
> A package that checks today on `0.3` may get a new obligation or a new error after an upgrade. Use `0.3` where its rules help, and rerun `una check .` and `una test .` after each upgrade.

### When to choose `0.3`

:::decide
**Which to use:**

| Your package… | Edition |
| --- | --- |
| Needs a condition on an operation, a locked contract, a boundary, a narrowed rebinding or units | `0.3` |
| Should stay exactly as it is across upgrades | `0.2` |
| Has failure handling you want the checker to keep honest | `0.3` |
| Is maintained by a team that cannot react to a new error after an upgrade | `0.2` |
:::

### Check yourself: grams and kilograms

Declare a second unit, a kilogram, and write the parcel's limit in kilograms:

```diff include="steps/10-parcel..steps/16-parcel-kilograms:src/parcel.una" context="1" title="src/parcel.una"
--- a/src/parcel.una
+++ b/src/parcel.una
@@ -4,2 +4,5 @@
 measure Gram
+
+--- A thousand grams.
+measure Kilogram = 1000 * Gram
 
@@ -15,3 +18,3 @@
   let weight = parcel_weight(3)
-  let limit: Int of Gram = 5000
+  let limit: Int of Kilogram = 5
   @console.print("{weight} grams, within the limit: {weight <= limit}")
```

A kilogram is 1,000 grams, and 3,600 grams is under 5 kilograms. Does the package check?

:::answer Show the answer
It does not. A unit is part of the type, and `<=` needs one type on both sides:

```text include="steps/16-parcel-kilograms/expected/rendered.txt"
[U2028] Error: `<=` needs operands of one type, and these are `Int of Gram` and `Int of 1000 * Gram`
    ╭─[ src/parcel.una:20:54 ]
    │
 20 │   @console.print("{weight} grams, within the limit: {weight <= limit}")
    │                                                      ───────┬───────
    │                                                             ╰───────── `<=` needs operands of one type, and these are `Int of Gram` and `Int of 1000 * Gram`
    │
    │ Note: run `una explain U2028` for an explanation
────╯
```

`Int of 1000 * Gram` is how the checker writes a kilogram: a scale of 1000 on the unit `Gram`. una never converts implicitly: two values of different units never meet in `+`, `-` or a comparison, and each such place is U2028. To compare them, convert one explicitly, where a gram is expected: `let limit_grams: Int of Gram = limit.convert()` multiplies by 1000, the exact ratio, and `weight <= limit_grams` checks, as in [the derived unit](#a-derived-unit-and-changing-a-unit-convert-measured-magnitude) above.
:::

One more, without code. Two packages check clean with una 0.4.0: the restock list after its move, on edition `0.3`, and the stock list of [section 19.2](#s19-2), on edition `0.2`. A later release comes out. Which of them can get a new error?

:::answer Show the answer
Only the package on edition `0.3`. It is on the preview, which a later release may make stricter: a new rule may add an obligation or an error to it. The package on edition `0.2`, a stable edition, keeps exactly what it accepts and rejects, except for a fix of a soundness or security error. That is why the preview's packages rerun `una check .` and `una test .` after each upgrade.
:::

## 19.4 Moving a package forward


### What a move is

**Moving** a package means changing the edition its `una.toml` names to a later one, and changing whatever code the new edition reads differently. The edition line is the whole decision; the rest is what the checker asks for.

### A move is a change of its own

Make the move a change of its own, with the edition line and the repairs it needed and nothing else, so that a reviewer reads it as a move and not as new behavior. The edition belongs to the package, not to a module: every module of a package moves together, and a store whose code is split into several packages can move them one at a time, each on the day its own tests are ready.

### The steps of a move

Moving a package to a later edition is a short loop. In the package's directory:

:::steps
1. **Change the edition** in `una.toml`, and only that line.
2. **Run `una check .`** and read every diagnostic. Each one is a place the new edition reads differently.
3. **Run `una fix --dry-run .`**, then `una fix .`, to apply the repairs that are exact.
4. **Repair the rest by hand**, guided by each diagnostic's repairs.
5. **Run `una test .`**, and compare the output of `una run .` with the output before the move.
:::

### Moving the restock list to `0.3`

For the restock list, the check of step 2 is the output of [What `0.3` reports](#what-03-reports-u3025-and-u3026), and step 3 shows one exact repair:

```sh
una fix --dry-run .
```

```text include="steps/15-restock-0-3/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/restock.una:14:36 U3025 remove the clause
```

`una fix .` removes the clause. The `attempt` is left to you: remove it, and replace the `when` with the value it unwrapped. The package after both repairs:

```diff include="steps/14-restock..steps/17-restock-moved:src/restock.una" title="src/restock.una"
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

```text include="steps/17-restock-moved/expected/output.txt"
LAMP-01: order 6
SHELF-03: enough
DESK-02: order 1
7 units to order
```

The move changed no output, removed a clause and an arm that never ran, and left a `total` that reads as what it is: a sum.

### Moving a name that became a keyword

The package of [Why a language needs editions](#why-a-language-needs-editions) moves to `0.2` the same way. Step 2 gives U0101 at `old`, with the repair "choose another name, such as `old_value`", which has no edit, since the right name is a choice. Step 3 shows that `una fix` has nothing to apply:

```text include="steps/02-arrived-0-2/expected/commands/fix.txt"
$ una fix --dry-run .
```

Step 4 is the rename by hand. `before` says what the count is:

```diff include="steps/01-arrived..steps/18-arrived-moved:src/restock.una" title="src/restock.una"
--- a/src/restock.una
+++ b/src/restock.una
@@ -1,7 +1,7 @@
 module restock
 
---- How many units arrived: the count `new` on the shelf now, less the count `old` from before.
-arrived(old: Int, new: Int) -> Int = new - old
+--- How many units arrived: the count `new` on the shelf now, less the count `before`.
+arrived(before: Int, new: Int) -> Int = new - before
 
 pub main() -> Unit
   uses @console: Console[print]
```

The package checks in `0.2`, and prints what it printed in `0.1`:

```text include="steps/18-arrived-moved/expected/output.txt"
6 units arrived
```

### How a move behaves

- **One edition per package.** Every module moves at once. A program is one package, so it has one edition: up to edition `0.3`, a package does not depend on other packages ([section 11.3](/learn/packages/#s11-3)).
- **Moving back fails where the code uses the later edition.** A construct of a later edition is usually a syntax error (U0101), a reserved word (U0103) or an unknown table (U7002) in an earlier one: [Moving a package back](#moving-a-package-back-u0101-u7002) shows it. A prelude function or a type rule of a later edition gives a type error, such as U1001, U2001 or U2002.
- **A rename is for a name.** In edition `0.1`, a reserved word used as a name gets a rename repair. A reserved word that stands as a construct of a later edition gets none, since the edition is what must change: [Using a construct of a later edition](#using-a-construct-of-a-later-edition-u0103) shows that case.
- **The output is the test of a move.** A move changes the language, not the program's behavior: the tests pass, and `una run .` prints what it printed before.

### Which edition to name

The table sums up which edition a package should name:

:::decide
**Which to use:**

| Your package… | Edition |
| --- | --- |
| Is stable code that you do not want to touch | Keep its edition: every release that lists it in `una --version` serves it |
| Uses loops, maps, `together` or any construct of this book outside chapter 13 and section 19.3 | `0.2` |
| Needs a condition on an operation, a locked contract, a boundary, a narrowed rebinding or units | `0.3`, the preview |
| Needs another package, or the constructs of long-running programs | `0.4`, the preview, with `ita.una` ([section 19.5](#s19-5)) |
| Is new, and should follow the stable rules | `0.2` |
:::

### Check yourself: a parameter named `take`, moved

Take the `0.1` package of [Check yourself: a word reserved for later](#check-yourself-a-word-reserved-for-later), and move it to `0.2` without renaming anything:

```diff include="steps/06-take..steps/19-take-0-2:una.toml" title="una.toml"
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

In `0.1`, each use of `take` was U0103, with a rename. What does `una check .` report in `0.2`, and what does `una fix --dry-run .` offer?

:::answer Show the answer
Two syntax errors, and no repair:

```text include="steps/19-take-0-2/expected/rendered.txt"
[U0101] Error: unexpected `:`, expected a parameter name
   ╭─[ src/shelf.una:4:22 ]
   │
 4 │ left(units: Int, take: Int) -> Int = units - take
   │                      ┬
   │                      ╰── unexpected `:`, expected a parameter name
   │
   │ Note: run `una explain U0101` for an explanation
───╯
[U0101] Error: unexpected `:`, expected an expression
   ╭─[ src/shelf.una:9:33 ]
   │
 9 │   @console.print("{left(10, take: 3)} left")
   │                                 ┬
   │                                 ╰── unexpected `:`, expected an expression
   │
   │ Note: run `una explain U0101` for an explanation
───╯
```

```text include="steps/19-take-0-2/expected/commands/fix.txt"
$ una fix --dry-run .
```

From edition `0.2` on, `take` is a keyword that starts a parameter's mode, as in `take items: List[Line]` ([chapter 16](/learn/memory/#s16-3)). So una reads `take` and expects the parameter's name after it, and finds `:`. The messages describe the syntax, not the word, which makes them harder to read: when a move gives a syntax error at a word that the new edition made a keyword, rename the word. Here, rename `take` to `taken`, by hand, before or after the move.
:::

## 19.5 Edition `0.4`, a preview

### What edition `0.4` is

Edition `0.4` is the edition of release 0.4.0, and a preview, as `0.3` is ([section 19.3](#s19-3)). It has every construct and rule of `0.3`, and it changes one thing that every earlier edition shares: where a package describes itself.

Up to edition `0.3`, a package's settings live in `una.toml` and its solver pin in `verification.lock`. From edition `0.4`, they live in two files written in Una's own syntax: `ita.una`, the **manifest**, the file that names the package and its settings, and `ita.lock`, the **lock**, the file that pins what the package was checked with. Think of a library card and the stamp on a returned book: the card says who you are and what you may borrow, and the stamp records exactly what you took, so that no one has to remember it.

Edition `0.4` also adds the constructs of long-running programs and of tasks and time, and lets a package use other packages, its **dependencies**: in this release, packages in directories of its own, since no public registry is served yet. This section shows the move itself; the new constructs have their own pages.

### Why the manifest moves to `ita.una`

A manifest decides what a program may do: which files it reads, which capabilities `main` is granted ([chapter 12](/learn/capabilities/)), and, from edition `0.4`, which other packages it runs. So the file must mean exactly what it says. `ita.una` is read by the same rules as a module: two-space indentation, `--` comments, and nothing that runs. It has no expressions, no conditions and no environment variables, and every line has one of a fixed set of forms, so a typo is an error, never a setting that is quietly ignored. `ita.lock` is written only by `una`, and is not edited by hand.

### The restock list in edition `0.4`

Here is the restock list of [section 19.4](#s19-4), moved to edition `0.4`. Its manifest names the package, its version and its edition in a head of three lines, then its run settings as a section:

```una include="steps/21-restock-0-4/ita.una" title="steps/21-restock-0-4/ita.una" verified="check, run"
ita restock
  version 0.1.0
  edition 0.4

run
  entry restock
  grants
    console
```

Each part has its place:

- **`ita restock`** heads the file with the package's name, where `una.toml` had `[package] name`.
- **`version`** and **`edition`** are the next lines, indented. A version is written as it is, `0.1.0`, with no quotes.
- **`run`** holds what `[run]` held: `entry`, the module whose `main` runs, and `grants`, one capability per line.

The lock holds the solver pin that `verification.lock` held, in the same syntax:

```una include="steps/21-restock-0-4/ita.lock" title="steps/21-restock-0-4/ita.lock"
-- Written by `una ita`; do not edit.
lock 1

solver
  encoding "una-smt-1"
  name "z3"
  version "5.1.0"
  logic "QF_UFLIA"
  steps 5000000
  seed 0
```

The modules do not change their language, and `una run .` prints what it printed in edition `0.3`:

```text include="steps/21-restock-0-4/expected/output.txt"
LAMP-01: order 6
SHELF-03: enough
DESK-02: order 1
7 units to order
```

### Moving with `una migrate`

You do not write these files by hand. `una migrate` reads `una.toml` and `verification.lock` and writes `ita.una` and `ita.lock` for you. Run it first with `--dry-run`, which prints what it would write and writes nothing. In the restock list of edition `0.2`, before its move to `0.3`:

```sh
una migrate --dry-run .
```

```text include="steps/14-restock/expected/commands/migrate.txt"
$ una migrate --dry-run .
-- ita.una
ita restock
  version 0.1.0
  edition 0.4

run
  entry restock
  grants
    console

-- ita.lock
-- Written by `una ita`; do not edit.
lock 1

solver
  encoding "una-smt-1"
  name "z3"
  version "5.1.0"
  logic "QF_UFLIA"
  steps 5000000
  seed 0

edition 0.2 -> 0.4: 2 diagnostics
```

The last line counts what the new edition reads differently. Edition `0.4` has every rule of `0.3`, so these are the two diagnostics of [What `0.3` reports](#what-03-reports-u3025-and-u3026): `una migrate` prints them in full, with their repairs, on the error stream. It applies none of them. The move to `0.4` is the loop of [The steps of a move](#the-steps-of-a-move), with `una migrate` in place of the edit of the edition line:

:::steps
1. **Run `una migrate .`** It writes `ita.una` and `ita.lock`, removes `una.toml` and `verification.lock`, and prints the diagnostics of the new edition.
2. **Run `una fix .`**, then repair the rest by hand, guided by each diagnostic.
3. **Run `una test .`**, and compare the output of `una run .` with the output before the move.
:::

`una migrate` exits with code 0 even when it prints diagnostics: they are the next steps of the move, not a failure of it.

### What `una migrate` changes in the code

`una migrate` also rewrites each module in the canonical form of edition `0.4`. That form wraps a line that is too long, which earlier editions never do, so the restock list's line of three stock lines is split:

```diff include="steps/17-restock-moved..steps/21-restock-0-4:src/restock.una" title="src/restock.una"
--- a/src/restock.una
+++ b/src/restock.una
@@ -25,7 +25,9 @@
 pub main() -> Unit
   uses @console: Console[print]
 =
-  let lines = [Line(sku: "LAMP-01", units: 4), Line(sku: "SHELF-03", units: 12), Line(sku: "DESK-02", units: 9)]
+  let lines = [Line(sku: "LAMP-01", units: 4), Line(sku: "SHELF-03", units: 12),
+    Line(sku: "DESK-02", units: 9)
+  ]
   for line in lines
     @console.print(order_text(line))
   @console.print("{total(lines)} units to order")
```

Only white space changes: the program is the same. A module that was in canonical form in its own edition changes in no other way.

### `edition = "0.4"` in `una.toml`

Edition `0.4` is never written in `una.toml`. Changing only the edition line, as for the earlier moves, is U7002 at the value, with `una migrate` as the way forward:

```text include="steps/22-restock-toml-0-4/expected/rendered.txt"
[U7002] Error: edition 0.4 is described by ita.una, not una.toml; run `una migrate`
   ╭─[ una.toml:4:11 ]
   │
 4 │ edition = "0.4"
   │           ──┬──
   │             ╰──── edition 0.4 is described by ita.una, not una.toml; run `una migrate`
   │
   │ Note: run `una explain U7002` for an explanation
───╯
```

The package is still checked in edition `0.4`, so the rest of its diagnostics show too, and `una migrate` keeps them for after the move.

### How edition `0.4` behaves

- **A preview.** A later release may add, change or remove a construct of edition `0.4`, but a program it accepted then gives the same result or a diagnostic, never a silent change. That is less than `0.3` promises, which only gets stricter.
- **One manifest.** A package has `ita.una` or `una.toml`, never both: a directory with both is an error, so the two can never disagree.
- **Only `una` writes the lock.** `una migrate` and the `una ita` commands write `ita.lock`; `una fix` and `una fmt` never edit `ita.lock`, and `una fmt ita.una` rewrites the manifest in its canonical form.
- **Words it reserves.** Edition `0.4` reserves words for its new constructs, such as `within`. A name that became one is U0103, with a rename that `una fix` applies.
- **Earlier editions stay.** A package of `una.toml` keeps its edition, and the same `una` checks both kinds of package side by side.

### Check yourself: a function named `within`

This package of edition `0.3` names a function `within`:

```una include="steps/23-fits-0-3/src/shelf.una" title="steps/23-fits-0-3/src/shelf.una" verified="check, run"
module shelf

--- Whether `units` more fit on a shelf that has `room` free.
within(units: Int, room: Int) -> Bool = units <= room

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("6 on a shelf with room for 10: {within(6, room: 10)}")
  @console.print("12 on a shelf with room for 10: {within(12, room: 10)}")
```

`una migrate --dry-run .` ends with this line:

```text include="steps/23-fits-0-3/expected/commands/migrate.txt#L24"
edition 0.3 -> 0.4: 3 diagnostics
```

Why three, for one function? And what does `una fix --dry-run .` offer once the package is moved?

:::answer Show the answer
`within` is a word edition `0.4` reserves, and it appears three times: the declaration and its two calls. Each is U0103:

```text include="steps/24-fits-0-4/expected/rendered.txt#L1-L10"
[U0103] Error: `within` is reserved for edition 0.4 (long-running programs)
   ╭─[ src/shelf.una:4:1 ]
   │
 4 │ within(units: Int, room: Int) -> Bool = units <= room
   │ ───┬──
   │    ╰──── `within` is reserved for edition 0.4 (long-running programs)
   │
   │ Help: repair 1: rename it to `the_within`; edit src/shelf.una:4:1..4:7 to "the_within"
   │
   │ Note: run `una explain U0103` for an explanation
```

`una fix` applies the three renames together, so the package checks again:

```text include="steps/24-fits-0-4/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/shelf.una:4:1 U0103 rename it to `the_within`
fixed src/shelf.una:9:51 U0103 rename it to `the_within`
fixed src/shelf.una:10:52 U0103 rename it to `the_within`
```

A name that says what the function answers, such as `fits`, reads better: rename it by hand instead, in all three places.
:::

## 19.6 Day-to-day: a shelf-label printer

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

`edition = "0.3"` opts into the preview. `[contracts]` locks the authority of `print_labels`: whatever its header says, it may never print a label where `dry_run` is true. Each key is the qualified name of a public function, its module's name, a dot and its own name, and each value lists `uses` clauses as a header writes them. The header may grant less than its lock, never more. A change to that line is a change to `una.toml`, which a reviewer sees in the diff, even when nobody touches the code.

Why both a condition and a lock? The condition makes the verifier check the body against the header. The lock makes the checker hold the header to `una.toml`. Without the lock, a later change could drop `where not dry_run` from the header and add a print without a guard, and the package would still check. With it, that change is U3023 until `una.toml` changes too.

### The kinds, the printer and the parser

These use edition `0.1` and `0.2` constructs only: a record, a sum kind for the failures, a capability, and a parser that fails with `LineError`. `text.split` is a text function of `0.2`; `to_int` and `trim` exist in `0.1` too.

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

`read_lines` keeps the lines that parse. `attempt` keeps each outcome as a `Result`, and a `when` on it decides whether the line is added. On `0.3`, `attempt` must wrap a call that can fail, and `parse_line` can, so U3026 does not apply.

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

The header gives `print_label` a condition: `where not dry_run`, a construct of `0.3`. Inside the body, the operation is called only under `if not dry_run`, and the verifier proves that the condition holds there. Remove the guard, and the check fails with a counterexample where `dry_run` is true ([An operation outside its condition](#an-operation-outside-its-condition-u5001) shows it).

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

The function counts a label whether or not it prints it, so a dry run gives the number of labels a real run would print. The two nested `if` statements have no `else`: an `if` without `else` is a statement that does nothing when its condition is false ([section 8.1](/learn/choices/#s8-1)), which edition `0.2` added along with the loop. The count is a `let edit` binding that the loop updates, as in [chapter 9](/learn/loops/#s9-2). The condition is part of the header, so `una contract labels.print_labels` shows it, and every caller sees that a dry run prints nothing without reading the body.

### Running it

`on_console` prints a label as a line of text, which stands in for the label printer here. It is a handler with a `uses` clause of its own, so it may print to the console and nothing else, and `una report .` lists it under `handler authority`. `silent` prints nothing, for the tests. `main` makes a dry run, then a real one, each installing `on_console` for one call with `with`:

```una include="day-to-day/src/labels.una#on_console..main" title="day-to-day/src/labels.una"
--- A printer that writes each label to the console.
handler on_console() for Printer
  uses @console: Console[print]
  op print_label(sku, units) = @console.print("[{sku} | {units} on hand]")

--- A printer that prints nothing, for the tests.
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

`una run .` prints the output shown in [What you'll build](#what-youll-build). It uses the kinds and the `when` of `0.1`, the loops, `let edit` and the text functions of `0.2`, and the condition and the lock of `0.3`. The dry run counts two labels and prints none. The real run prints the lamp and the shelf. The desk has no stock, and the chair's line, `CHAIR-09, two`, does not parse, so neither gets a label. `una report .` lists the printer handler under `handler authority`, with what it may do:

```text include="day-to-day/expected/commands/report.txt#L11-L12"
handler authority:
  labels.on_console for labels.Printer (private): @console: Console[print]
```

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

--- A printer that prints nothing, for the tests.
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

test "a line that does not parse is left out"
  do read_lines(export()).len
  expect result == 3

test "a dry run counts the labels and prints none"
  given @printer = silent()
  do print_labels(read_lines(export()), dry_run: true)
  expect result == 2
  expect not performed @printer.print_label

test "a run prints a label for each line with stock"
  given @printer = silent()
  do print_labels(read_lines(export()), dry_run: false)
  expect result == 2
  expect performed @printer.print_label
```

## 19.7 Testing it

### Three tests on the export of `main`

The package is of edition `0.3`, so each one is a `test`. The tests check the parser and both kinds of run, on the same export that `main` uses, so a reader can compare their numbers with the program's output. The two runs use `silent`, so they print nothing, and they check what was performed:

```una include="day-to-day/src/labels.una#L72-L86" title="day-to-day/src/labels.una" caption="the examples"
test "a line that does not parse is left out"
  do read_lines(export()).len
  expect result == 3

test "a dry run counts the labels and prints none"
  given @printer = silent()
  do print_labels(read_lines(export()), dry_run: true)
  expect result == 2
  expect not performed @printer.print_label

test "a run prints a label for each line with stock"
  given @printer = silent()
  do print_labels(read_lines(export()), dry_run: false)
  expect result == 2
  expect performed @printer.print_label
```

### A plain `dry_run` and the calls `silent` records

The tests pass `dry_run` as a plain `true` or `false`. Here the tests have nothing to prove about it: each installs its own printer with `given`, and the condition is proven once, inside `print_labels`, for every value of `dry_run`, so the tests only check behavior. `silent` answers every `print_label` with `unit`, and the trace of each test records the calls, which `expect performed` and `expect not performed` read.

### The proof and the tests

The proof and the tests cover different ground. The verifier proves, for every list and every call, that a label is printed only when `dry_run` is false, and the lock in `una.toml` keeps that rule from being dropped. The test "a dry run counts the labels and prints none" checks the same rule on one list, with `expect not performed`, and also checks the count, which no condition states. After an upgrade of `una` to a later release, rerun both: a stricter rule can only add obligations or errors, and the tests catch a change in behavior.

### Running the tests

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L6"
test labels "a line that does not parse is left out" ... ok
test labels "a dry run counts the labels and prints none" ... ok
test labels "a run prints a label for each line with stock" ... ok

3 tests: 3 passed, 0 failed
```

## 19.8 Common mistakes

The first two mistakes are changes to the edition `0.1` stock list of [section 19.1](#s19-1). The others are changes to the day-to-day program.

### Interpolating a list in edition `0.1` (U2001)

:::mistake
Print the list as it is:

```diff include="steps/05-edition-0-1..mistakes/1:src/shelf.una" context="1" title="src/shelf.una"
--- a/src/shelf.una
+++ b/src/shelf.una
@@ -15 +15,2 @@
   @console.print("{lines.len} lines, {total(lines)} units")
+  @console.print("{lines}")
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U2001] Error: interpolation converts `Int`, `Bool` and `Text` to text, and this value is `List[Line]`
```

*Why:* edition `0.1` interpolates only `Int`, `Bool` and `Text`. The message names both sides: what interpolation converts, and the type it was given, `List[Line]`.

*Fix:* interpolate the fields you want, or move the package to `0.2`, which interpolates any value that `==` compares, except a `Hashed`. See [U2001](/docs/errors/U2001/).
:::

### Using a construct of a later edition (U0103)

:::mistake
Write the total with `let edit` and `for` in edition `0.1`:

```diff include="steps/05-edition-0-1..mistakes/2:src/shelf.una" context="1" title="src/shelf.una"
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
    │ Note: run `una explain U0103` for an explanation
────╯
```

The diagnostic has no repair, and `una fix --dry-run .` has nothing to apply:

```text include="mistakes/2/expected/commands/fix.txt"
$ una fix --dry-run .
```

*Why:* in edition `0.1`, `edit` is a reserved word, not a keyword, so the checker refuses it. The message says the rest: `reserved for v0.2 (memory model)` names the edition where `let edit` exists. A rename is offered only where the renamed program parses, and `let the_edit sum = 0` does not, so no name would repair this line.

*Fix:* change `edition` in `una.toml` to `"0.2"`. See [U0103](/docs/errors/U0103/).
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
[U0101] Error: unexpected text literal, expected `(` and the parameters
    ╭─[ src/labels.una:72:6 ]
    │
 72 │ test "a line that does not parse is left out"
    │      ┬
    │      ╰── unexpected text literal, expected `(` and the parameters
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

*Why:* the condition, the `test` declarations and `[contracts]` exist only in edition `0.3`. In `0.2`, the condition is a syntax error, so the message speaks of `where` as an unexpected keyword. `test` is a name in `0.2`, so `test "a line that does not parse is left out"` reads as the start of a function named `test`, and the text where its parameters should be is a syntax error too; the parser reports the first such line only. `[contracts]` is an unknown table of `una.toml`. Three diagnostics in two files point at one cause: the edition line.

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

*Why:* the header lets `print_label` run only where `not dry_run` holds, and the verifier found a run where it does not. The obligation's kind, `effect_condition`, says that it is a condition on an operation. The counterexample is `dry_run = true` with one line in stock, `line.units = 1`: the placeholders `Line#0`, `Text#0` and `List#0` are values the solver needed but whose details do not matter.

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

*Why:* the lock in `una.toml` says how much `print_labels` may ever do, and the header now grants more: printing in a dry run, as the counterexample `dry_run = true` shows. The diagnostic has two places in two files: the header, the primary place, and the lock in `una.toml`, marked `lock`. The obligation's kind is `contract_lock`.

*Fix:* restore the condition. To really change the rule, change the lock in `una.toml` too, where a reviewer sees it. See [U3023](/docs/errors/U3023/).
:::

## 19.9 Exercises

Each exercise starts from `exercises/N/start` and has a test that fails there until the exercise is done: an `example` in the package of exercise 1, of edition `0.1`, and a `test` in the others, of edition `0.3`. Work in the start package's directory: check the edition in `una.toml` first, then run `una fmt .`, `una check .` and `una test .`.

### Exercise 1: move a package to `0.2`

::::exercise
The edition `0.1` stock list now also counts the units sold, with a function whose parameters are `old` and `new`:

```una include="exercises/1/start/src/shelf.una#sold" title="exercises/1/start/src/shelf.una"
--- The units sold since the last count: the count `old` from before, less the count `new` now.
sold(old: Int, new: Int) -> Int = old - new
```

Someone then added `low_stock`, with a loop, and an example for it. The package no longer checks. Move it to the edition that the loop needs, and change only what the move requires. The start package's new function and example:

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

```una include="exercises/1/start/src/shelf.una#L30-L32" title="exercises/1/start/src/shelf.una"
example "the lines below the limit are low on stock"
  do low_stock([Line(sku: "LAMP-01", units: 4), Line(sku: "DESK-02", units: 1)], limit: 2)
  expect result == ["DESK-02"]
```

```text include="exercises/1/start/expected/diagnostics.txt"
error U0103 at src/shelf.una:17:7: `edit` is reserved for v0.2 (memory model)
```

:::hint
*Hint:* the loop is right; the message says which edition has `edit`. Read [Using a construct of a later edition](#using-a-construct-of-a-later-edition-u0103), then follow [the steps of a move](#the-steps-of-a-move): after the edition line, run `una check .` again, since the new edition reads some names differently.
:::

Check your answer with `una check .`, then `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Change the edition:

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

With the edition line alone, `una check .` reports U0101 at `old`: "`old` is a reserved keyword, so it cannot name a binding". `una fix` has no edit for it, since the new name is a choice, so rename it by hand:

```diff include="exercises/1/start..exercises/1/answer:src/shelf.una" context="1" title="src/shelf.una"
--- a/src/shelf.una
+++ b/src/shelf.una
@@ -10,4 +10,4 @@
 
---- The units sold since the last count: the count `old` from before, less the count `new` now.
-sold(old: Int, new: Int) -> Int = old - new
+--- The units sold since the last count: the count `before`, less the count `new` now.
+sold(before: Int, new: Int) -> Int = before - new
 
```
:::
::::

### Exercise 2: a restock run

::::exercise
The night shift wants labels for the lines that are low on stock, so they can restock them first. Write the body of `print_low`: like `print_labels`, but for the lines with fewer than `limit` units, with the same dry run. The start package has the header with its condition, a stub body, and two tests:

```una include="exercises/2/start/src/labels.una#print_low" title="exercises/2/start/src/labels.una"
--- Prints a label for every line with fewer than `limit` units, and gives how many, for a
--- restock run. A dry run prints nothing. Exercise 2: write the body.
pub print_low(lines: List[Line], limit: Int, dry_run: Bool) -> Int
  uses @printer: Printer[print_label where not dry_run]
=
  0
```

```una include="exercises/2/start/src/labels.una#L95-L105" title="exercises/2/start/src/labels.una"
test "a restock run prints the lines below the limit"
  given @printer = silent()
  do print_low(read_lines(export()), limit: 5, dry_run: false)
  expect result == 2
  expect performed @printer.print_label

test "a restock dry run prints nothing"
  given @printer = silent()
  do print_low(read_lines(export()), limit: 5, dry_run: true)
  expect result == 2
  expect not performed @printer.print_label
```

:::hint
*Hint:* start from the body of `print_labels`, and change only the test on `line.units`. Keep the count outside the `if not dry_run`, so a dry run counts too. If you leave out the guard, `una check .` reports where, with a counterexample where `dry_run` is true.
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

--- A printer that prints nothing, for the tests.
handler silent() for Printer
  op print_label(sku, units) = unit
  op print_summary(labels) = unit
```

And it adds this test:

```una include="exercises/3/start/src/labels.una#L92-L96" title="exercises/3/start/src/labels.una"
test "a dry run prints the summary, and no label"
  given @printer = silent()
  do print_labels(read_lines(export()), dry_run: true)
  expect performed @printer.print_summary
  expect not performed @printer.print_label
```

:::hint
*Hint:* the header decides which operations may run, and under which condition: add `print_summary` to the `uses` clause of `print_labels`, with no condition, and call it after the loop. Once the code checks on its own, read what `una check .` says about `una.toml`: the lock must list what the header grants.
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

## 19.10 Recap and reference

### For agents

:::agents
A construct of a later edition usually gives U0101 or U0103 at the construct, a table of a later edition U7002 at `una.toml`, `edition = "0.4"` in `una.toml` U7002 with `una migrate` as its repair, and a later prelude function or type rule a type error, such as U1001, U2001 or U2002. To move a package, change only `edition`, run `una --json check .`, apply `una fix .`, and repair the rest by hand; to move it to `0.4`, run `una migrate .` instead of editing the line, then the same loop. Never edit `ita.lock` by hand. Never apply a U0103 rename to `edit`, `take` or `together` used as a keyword: change the edition instead. A U0101 at a word the new edition made a keyword needs a rename by hand. In edition `0.3`, the test declaration is `test`; an `example` there is U0103, which `una fix .` rewrites. The compact rule: *an edition is a line of the manifest, `una.toml` or, from `0.4`, `ita.una`; a later edition adds constructs and, with few exceptions, tightens rules.*
:::

### Recap

:::recap
- `[package] edition` names a package's edition, and is required. A single file has edition `0.1`.
- Upgrading `una` keeps what each stable edition accepts and rejects, except to fix a soundness or security error.
- Editions `0.1` to `0.4` are cumulative: each adds constructs, keywords and rules, and removes no construct of the one before.
- `0.2` adds loops, `let edit`, `edit` and `take`, `together`, maps, JSON and more, makes `old` a keyword, and reserves `weak`.
- `0.3` is a preview: conditions on operations, locked contracts, boundaries, narrowed rebindings, units, refined type arguments, no dead failure handling, and tests written `test`. It may get stricter in a later release.
- To move a package: change the edition, `una check .`, `una fix .`, repair the rest, `una test .`, and compare the output.
- `0.4` is a preview whose package is described by `ita.una` and pinned by `ita.lock`: `una migrate` writes both, rewrites the modules in its canonical form, and prints what the new edition reads differently. A later release may change it, never in silence.
- A word that stands as a construct of a later edition gets no rename; change the edition instead.
:::

### Reference

:::reference
- Editions: [editions](/docs/editions/), [moving from 0.1 to 0.2](/docs/editions/migrate-0.1-to-0.2/), [`[package] edition`](/docs/configure/package/edition/), [`[boundaries]`](/docs/configure/boundaries/)
- Construct pages: [`let edit`](/docs/language/control-flow/let-edit/), [`for`](/docs/language/control-flow/for/), [`together`](/docs/language/control-flow/together/), [`uses`](/docs/language/capabilities/uses/), [`if error`](/docs/language/errors/if-error/), [`attempt`](/docs/language/errors/attempt/), [constraints on generics](/docs/language/types/constraints/)
- Command line: [`una check`](/docs/cli/check/), [`una fix`](/docs/cli/fix/), `una migrate`
- Diagnostics: [U0101](/docs/errors/U0101/), [U0103](/docs/errors/U0103/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2002](/docs/errors/U2002/), [U2028](/docs/errors/U2028/), [U3023](/docs/errors/U3023/), [U3025](/docs/errors/U3025/), [U3026](/docs/errors/U3026/), [U5001](/docs/errors/U5001/), [U7002](/docs/errors/U7002/)
- Specification: [project files and editions](/docs/spec/13-diagnostics-and-abi/), [packages and `una migrate`](/docs/spec/30-packages/), [lexical structure, reserved words](/docs/spec/01-lexical-structure/), [types](/docs/spec/03-types/), [memory model](/docs/spec/17-memory-model/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [errors](/docs/spec/06-errors/)
:::
