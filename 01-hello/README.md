---
learn: "1"
title: Hello, Una
editions: ["0.2"]
codes: [U0001, U0003, U0101, U1001, U1008, U2001, U2004, U3004, U7001, U7002]
time: 55
builds: A packing slip that a store prints for the box of one order, with examples that test each line
prerequisites: []
template: 2
nav: ["A first program", "Reading a diagnostic", "Printing and the console", "Values, types and names", "Functions and comments", "Examples and una test", "Day-to-day: a packing slip", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 1 Hello, Una

A program is a set of instructions that a computer follows, written in a language that both you and the computer can read. This chapter is where you write your first one. It assumes no experience: every word it uses is explained the first time it appears. You start from an empty directory, write a program that prints a line, read what Una says when the program is wrong, and end with a small program a store would really use, checked, run and tested. On the way you meet the ideas every later chapter builds on: packages, modules, functions, values, types and diagnostics.

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

In many languages the first program is one line, and so is the first surprise. A program that only meant to write a line on the screen can also read your files or send data over the network, and nothing in its text says whether it does. A mistake, such as a number where a word should be, often shows up only when that line runs: in front of a customer, or months later.

Una moves these questions to the time before the program runs. Every word in this part is taught in this chapter, in the section named after it; read it now for the idea, and come back to it later:

:::steps
1. **One command checks everything.** Before you run a program, `una check` reads all of it and lists each mistake it finds, with the place and the reason. `una run` refuses to start a program that still has a mistake in it ([section 1.2](#s1-2)).
2. **The first lines of a function say what it may do.** A function is a named piece of a program. Its first lines say whether it may print on the screen, and Una holds the rest of the function to them ([section 1.3](#s1-3)).
3. **Whoever runs the program decides what it gets.** A small file of settings next to the code says that the program may print. The code asks, the settings allow, and a reader can see both ([section 1.3](#s1-3)).
4. **Tests live next to the code.** An example runs a function and says what it must give back, and `una test` checks every example ([section 1.6](#s1-6)).
:::

> [!KEY]
> In Una, the first lines of a function say what it may do outside the program. If they do not say it, Una does not let the function do it.

## 1.1 A first program

### What a program is

A **program** is a list of instructions for a computer, such as "write this line on the screen" or "add these two prices". Think of a recipe: it names what it needs, then gives the steps in order, and anyone who follows it gets the same dish. A computer follows a program the same way, one step after another, exactly as written.

You write a program as text, in a file, in a **programming language**: a small language with strict rules, so that each line has one meaning. That text is the **source code**, or just the code. This book teaches the language Una.

A few more words come up on every page:

- **Running** a program means having the computer follow its instructions.
- A **value** is one piece of data the program works with: the number `18`, the text `"The store is open"`. [Section 1.4](#s1-4) covers values.
- The **console** is the window of text where you type commands and where a program writes its lines. [Section 1.3](#s1-3) covers it.
- `una` is the tool that reads Una code. It **checks** the code, which means it looks for mistakes without running it, and it **runs** the code when the check passes.

### Why Una checks before it runs

A mistake in a program is normal: everyone makes them while writing code. What matters is when you find out. If a mistake surfaces only when its line runs, it may surface in front of a customer, months after the code was written. Una finds as many mistakes as it can before the program starts. `una check` reads the whole program and reports each mistake with the place it is at and what is wrong, and `una run` will not start a program with a mistake it can see. [Section 1.2](#s1-2) shows what such a report looks like.

### What you need: a terminal, `una` and Z3

Una runs on macOS, on Macs with Apple silicon, and on Linux, on x86-64 and ARM computers: those are the systems each release of `una` is built for.

You work with `una` in a **terminal**: the program that shows the console on your screen. To open one:

- on macOS, open the Terminal app, in Applications > Utilities, or find it by typing "Terminal" in Spotlight, which [[Cmd]]+[[Space]] opens;
- on Linux, open the Terminal app from your applications menu; on many systems [[Ctrl]]+[[Alt]]+[[T]] opens one.

In the terminal you type a **command**, a line that names a program and what it should do, and press [[Enter]]; the program runs and prints its answer under the command.

Next, install `una` and the solver it uses, Z3: a program that `una check` asks to prove facts about your code, from [chapter 2](/learn/values/) on. The [install page](/docs/install/) installs both, at the versions that go together, and sets up your terminal so that typing `una` runs it from any directory.

To see that it worked, type `una --version` and press [[Enter]]. It prints the version of `una`, the editions it supports and the version of Z3 it expects. Then run `z3 --version`, which must report that same version. The programs of this chapter need no proof, so they run without Z3, but from [chapter 2](/learn/values/) on, `una check` cannot prove anything without it.

### The package and its manifest

Una keeps a program's files together in a **package**: a **directory** (a folder) with a manifest, `una.toml`, a lock file, `verification.lock`, and the code under a directory named `src/`. Every program in this book is a package, so it is worth making the first one by hand.

A new terminal starts in your **home directory**: the directory that holds your own files and directories, such as `Documents`. The terminal is always "in" one directory, and commands work there. Two commands move you around:

- `mkdir store` makes a directory named `store` in the directory you are in;
- `cd store` moves the terminal into `store`, so that the next commands work there.

Make the directory `store` in your home directory, move into it, and make `src` inside it:

```sh
mkdir store
cd store
mkdir src
```

A **path** names a file or a directory by the directories that lead to it, separated by `/`: `store/src` is the directory `src` inside `store`, and `src/hello.una` is the file `hello.una` inside `src`. A path without a leading `/` starts from the directory you are in.

The **manifest** is a short file of settings that `una` reads before it reads any code. You write it with a **text editor**: a program that saves exactly the characters you type, with no fonts or formatting. Any code editor works. On macOS, TextEdit works too, once you choose Format > Make Plain Text before you type; on Linux, the text editor that comes with your system works. Create a new file, write these lines, and save it in the `store` directory with the name `una.toml` exactly. If the editor offers to add `.txt` to the name, refuse it: `una.toml.txt` is a different file, and `una` does not read it.

```toml include="steps/01-hello/una.toml" title="una.toml"
[package]
name = "hello"
version = "0.1.0"
edition = "0.2"

[run]
entry = "hello"
grants = ["console"]
```

It has two tables, each a heading in brackets followed by `key = value` lines:

- `[package]` names the package, gives its version, and names its **edition**: the version of the Una language its code is written in. This book uses edition `0.2`. A package keeps the rules of its edition even when `una` gets newer.
- `[run]` says how `una run` starts the program. `entry` names the module, the file of code, that holds `main`, the function the program starts with; [The first module](#the-first-module-hello) explains both. `grants` lists what the program may use outside itself when it runs: here, the console. [Section 1.3](#s1-3) explains grants.

The package's name, `hello`, need not match its directory's name, `store`.

### The lock file: `verification.lock`

`verification.lock` tells `una` which solver to use, at which exact version, and how much work it may spend, so that a check that passes on your machine passes on every other one. You do not need to understand its lines yet: copy them as they are. The file is the same in every package of this book. Create it with your editor, as you did `una.toml`, and save it in `store` with the name `verification.lock`:

```text include="steps/01-hello/expected/commands/explain-u7004.txt#L32-L37"
encoding_version = "una-smt-1"
solver           = "z3"
solver_version   = "5.1.0"
logic            = "QF_UFLIA"
step_budget      = 5000000
random_seed      = 0
```

`una explain U7004` prints these lines too, under "Fixed example", so you can copy the lock from your terminal at any time. Take that one: the lock it shows first, under "Failing example", is the broken one. For each later package, make the file again the same way, or copy it from `store` with your file manager (Finder on macOS).

### The first module: `hello`

Now the code. A source file is a file of Una code, and it holds one **module**: a named unit of code. Its name is the name of the file: `src/hello.una` holds the module `hello`. A module holds **declarations**, each of which gives a name to something, such as a function.

A **function** is a named list of steps. Every program has one function where it starts, `main`, as a recipe has a first step. Write `src/hello.una`:

:::steps
```una include="steps/01-hello/src/hello.una" title="src/hello.una" verified="check, run"
module hello

--- Says that the store is open.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("The store is open")
```

1. **`module hello`.** The first line names the module. It must match the file name.
2. **`--- Says that the store is open.`** A **doc comment**: a note for people, which the computer does not run. It belongs to the declaration under it. [Section 1.5](#s1-5) covers comments.
3. **`pub main() -> Unit`.** The function's **header**, its first line. `pub` makes it **public**, so that `una run` can reach it. `main` is its name, and `()` says it takes no inputs. `-> Unit` says what it gives back when it ends: `Unit` means nothing useful, since `main` is run for what it does, not for a value.
4. **`uses @console: Console[print]`.** What the function may do outside the program: call the operation `print` of `Console`, the console, through the name `@console`. [Section 1.3](#s1-3) explains this line.
5. **`=`, then the body.** The **body** is the list of steps, indented by two spaces under `=`. Its one step prints a line of text: the text between the double quotes.
:::

### Checking and running it

In the `store` directory, check the package, then run it:

```sh
una check .
una run .
```

The `.` names the current directory, the package's. `una check .` prints nothing when the package is right. `una run .` checks again, then runs `main`, and the console shows what it prints:

```text include="steps/01-hello/expected/output.txt"
The store is open
```

That is your first program. Every program in this book is made the same way: a directory with `una.toml`, `verification.lock` and a module under `src/`, then `una check .` and `una run .` in that directory.

### How a package is laid out

The pieces fit together by name, and `una` checks each link:

- The directory holds `una.toml`, `verification.lock` and `src/`.
- Each file `src/<name>.una` holds the module `<name>`, and its first line says `module <name>`.
- `entry` in `una.toml` names one of those modules, and that module has `pub main() -> Unit`.
- Each step of `main` runs in order, top to bottom, and the program ends when the last step ends.

When one of these links breaks, `una check` says which. [A module named unlike its file](#a-module-named-unlike-its-file-u1008), in Common mistakes, shows a broken one.

### Check yourself: a first program

This module is in `src/greeting.una`, in a package whose manifest has `entry = "greeting"`:

```una include="steps/02-greeting/src/greeting.una" title="steps/02-greeting/src/greeting.una"
module greeting

--- Greets the first customers of the day.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("Good morning")
  @console.print("The store is open")
  @console.print("Today's special: desk lamps")
```

What does `una run .` print?

:::answer Show the answer
```text include="steps/02-greeting/expected/output.txt"
Good morning
The store is open
Today's special: desk lamps
```

Three lines, in the order of the three steps. The doc comment prints nothing: it is a note for people. The apostrophe in `Today's` is an ordinary character inside the text.
:::

## 1.2 Reading a diagnostic

### What a diagnostic is

A **diagnostic** is a report that `una check` writes about one problem in your code. It is like the note a proofreader leaves in the margin: it points at the exact word, says what is wrong, and often suggests a correction. Each diagnostic has a **code**, such as `U1001`, that names the kind of problem.

### Why a checker reports mistakes

A computer does exactly what the code says, even when the code says something you did not mean. A misspelt name, a number where a text should be, a step that asks for something the program may not do: without a checker, each of these is found only when its line runs. `una check` finds them while you write, and says where they are.

### A typo the checker catches

Change `print` to `write`, which `Console` does not have. The block that shows the change is a **diff**: a listing of the lines that differ between two versions of a file, with `-` before each line taken out and `+` before each line put in, and a few unmarked lines around them so you can find the place:

```diff include="steps/01-hello..steps/03-typo:src/hello.una" title="src/hello.una"
--- a/src/hello.una
+++ b/src/hello.una
@@ -4,4 +4,4 @@
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print("The store is open")
+  @console.write("The store is open")
```

`una check .` now reports:

```text include="steps/03-typo/expected/rendered.txt"
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

### The parts of a diagnostic

Each diagnostic has the same parts, in the same order:

:::steps
1. **`[U1001] Error:`** The code, which names the kind of problem. Every code has a page on this site, such as [U1001](/docs/errors/U1001/), and `una explain U1001` prints the same text in your terminal.
2. **The message.** One sentence that says what is wrong: here, that `Console` has no operation `write`.
3. **`src/hello.una:7:12`.** The file, the line and the column: line 7, character 12. Lines and columns count from 1.
4. **The excerpt.** Line 7 of the file, with its number on the left. The marks under it, `──┬──`, underline the exact span, here `write`, and the line from `╰──` repeats the message next to it.
5. **`Help` and `Note` lines.** A `Help` line proposes a repair when there is one. Some repairs are exact edits, which `una fix .` applies for you. A `Note` adds what you need to understand the problem; the last one names `una explain`.
:::

Read a diagnostic in that order: the message first, then the place, then the help. The message says what, the place says where, and the help says what to do.

### Several problems in one check

`una check .` reports every problem it finds in one pass, not only the first. With two misspelt operations, it reports two diagnostics:

```diff include="steps/01-hello..steps/04-two-typos:src/hello.una" title="src/hello.una"
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

```text include="steps/04-two-typos/expected/diagnostics.txt"
error U1001 at src/hello.una:7:12: capability `Console` has no operation `write`
error U1001 at src/hello.una:8:12: capability `Console` has no operation `show`
```

This book lists them here in a short form, one line each: the code, the place and the message. In your terminal, `una check .` prints each one in full, as for `write`. Fix them in any order, and run `una check .` again until it prints nothing.

### Exit codes, and a run that refuses to start

Every command ends with an **exit code**, a number the terminal receives when the command ends. `una check .` exits with 0 when the package checks, and with 1 when it reports a problem, so another program that runs `una check` for you, such as a code editor, can tell success from failure without reading the text.

`una run .` never runs a package that does not check. It prints the same diagnostics and stops, so a program that runs is always a program that checked.

### Asking `una explain`

Each code has a longer explanation, with a failing example and a fixed one. `una explain` prints it:

```sh
una explain U1001
```

```text include="steps/03-typo/expected/commands/explain-u1001.txt#L2-L4"
# U1001: Unresolved name

Every name must refer to something visible where it is used: a local binding (a parameter, a `let`, a pattern binding or a lambda parameter), a declaration of the module, a name the module imports, or the prelude (ADR 0023). U1001 reports a name that none of these holds, whether it names a value, a type, a capability, a handler, a module or an imported declaration. An import names a module of the package or one of the two standard modules that can be imported: `std.host`, with the host capabilities and their failure kinds, and `std.testing`, with the helpers for examples. The prelude is always in scope and is not imported. A variant in a `when` pattern, an `is` test or after `fail` takes its kind from the context, and is checked against that kind instead. An operation that a capability does not declare is unresolved too, after `@x.` in a call and after `expect performed` or `expect not performed` in an example: the diagnostic offers the closest operation as an edit (ADR 0082).
```

The first line names the code and its meaning: U1001 is an unresolved name, a name that refers to nothing. The paragraph after it is the full rule, which names terms of later chapters and the numbered decision records behind it; a failing example and a fixed one follow it. You do not need all of it now. The site has the same text, on the page of each code, such as [U1001](/docs/errors/U1001/).

### Canonical form

**Canonical form** is the one layout Una accepts for any code: indentation, spaces, line breaks and the order of a few parts. `una check .` reports code that differs from it, as here, with spaces inside the parentheses:

```diff include="steps/01-hello..steps/05-layout:src/hello.una" title="src/hello.una"
--- a/src/hello.una
+++ b/src/hello.una
@@ -4,4 +4,4 @@
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print("The store is open")
+  @console.print( "The store is open" )
```

```text include="steps/05-layout/expected/rendered.txt#L1,L8"
[U7001] Error: line 7 is not in canonical form
   │ Help: repair 1: rewrite in canonical form, as `una fmt` does; edit src/hello.una:7:1..8:1 to "  @console.print(\"The store is open\")\n"
```

The `Help` line holds the line as canonical form writes it. You rarely fix layout by hand: `una fmt .` rewrites every file of the package in canonical form. Since all Una code has one layout, no review ever argues about it.

### The commands so far

You have met four commands. The others come when a section needs them: `una test` in [section 1.6](#s1-6), and the rest in [chapter 13, Tools](/learn/tools/).

| Command | What it does | Prints when all is well |
| --- | --- | --- |
| `una check .` | Looks for mistakes, without running anything | nothing |
| `una run .` | Checks, then runs `main` | what the program prints |
| `una explain U1001` | Explains a code | the explanation |
| `una fmt .` | Rewrites the code in canonical form | nothing |

### Check yourself: diagnostics

This version of `hello` has one wrong letter order:

```diff include="steps/01-hello..steps/06-misspelt:src/hello.una" title="src/hello.una"
--- a/src/hello.una
+++ b/src/hello.una
@@ -4,4 +4,4 @@
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print("The store is open")
+  @console.pirnt("The store is open")
```

Which code does `una check .` report, at which line and column? Then compare its `Help` line with the diagnostic for `write`, which had none.

:::answer Show the answer
```text include="steps/06-misspelt/expected/rendered.txt"
[U1001] Error: capability `Console` has no operation `pirnt`
   ╭─[ src/hello.una:7:12 ]
   │
 7 │   @console.pirnt("The store is open")
   │            ──┬──
   │              ╰──── capability `Console` has no operation `pirnt`
   │
   │ Help: repair 1: write `print`; edit src/hello.una:7:12..7:17 to "print"
   │
   │ Note: run `una explain U1001` for an explanation
───╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

The code is U1001, at line 7, column 12, where `pirnt` starts: the same kind of problem as `write`. This time there is a `Help` line: `pirnt` is close to `print`, so the checker names the operation you most likely meant, as an exact edit that `una fix .` can apply. `write` is close to no operation of `Console`, so it got none.
:::

## 1.3 Printing and the console

### What the console is

The **console** is the channel of text between a program and the person who runs it. In a terminal, it is the window itself: what the program prints appears there, line after line, under the command that started it. Printing is the simplest way a program shows its results.

In Una the console is a **capability**: a named set of **operations**, actions on the world outside the program. `Console` has one operation, `print`, which writes one line of text and ends it with a new line. Other capabilities reach a clock, files or the network. Think of a badge that a store gives each employee: it names the doors the employee may open. A capability is such a badge, and a function shows its badges in its header.

### Why a function must ask for the console

Remove the `uses` line from `main`, and keep its body:

```diff include="steps/01-hello..steps/07-no-uses:src/hello.una" title="src/hello.una"
--- a/src/hello.una
+++ b/src/hello.una
@@ -1,7 +1,4 @@
 module hello
 
 --- Says that the store is open.
-pub main() -> Unit
-  uses @console: Console[print]
-=
-  @console.print("The store is open")
+pub main() -> Unit = @console.print("The store is open")
```

Canonical form writes a body of one line on the header line, after `=`. `una check .` reports:

```text include="steps/07-no-uses/expected/rendered.txt#L1-L5"
[U3004] Error: `@console` is used here, but this code declares no `uses`, so it is pure
   ╭─[ src/hello.una:4:22 ]
   │
 4 │ pub main() -> Unit = @console.print("The store is open")
   │                      ────┬───
```

The message says that `main` uses `@console`, but its header declares no `uses`, so the function is **pure**: it computes values and touches nothing outside the program. The `Help` line offers the repair, with a warning: it widens what the function may do, so make sure that printing is part of its job.

The rule protects whoever reads or runs the code. In many languages any line may print, write a file or send data over the network, and only reading every line tells you which do. In Una the header says it, and the checker holds the body to the header.

### How to write `uses`

A `uses` line goes under the header, indented two spaces, before `=`. Its parts:

:::steps
1. **`uses`.** The keyword that starts the line. A **keyword** is a word with a fixed meaning in the language.
2. **`@console`.** The name the body uses for the capability. A capability name always starts with `@`. You choose the rest of it.
3. **`: Console`.** The capability.
4. **`[print]`.** The operations the function may call, in brackets, separated by commas. Leave the brackets out, `Console`, and the function may call every operation of the capability.
:::

In the body, a call of an operation is the name, a dot, the operation and its **argument**, the value it works on, in parentheses: `@console.print("The store is open")`.

#### Another name, and every operation

This program names the console `@screen`, asks for `Console` with all its operations, and prints four lines, one of them empty:

```una include="steps/08-notices/src/notices.una" title="steps/08-notices/src/notices.una" verified="check, run"
module notices

--- Prints the notices of the morning, with an empty line after the greeting.
pub main() -> Unit
  uses @screen: Console
=
  @screen.print("Good morning")
  @screen.print("")
  @screen.print("Fresh stock: desk lamps and wool rugs")
  @screen.print("The café opens at 10:00")
```

`una run .` prints:

```text include="steps/08-notices/expected/output.txt"
Good morning

Fresh stock: desk lamps and wool rugs
The café opens at 10:00
```

The name is a choice, but most code uses `@console`, so that every reader recognizes it. `Console[print]` and `Console` grant the same thing today, since `print` is the console's only operation. Listing the operations is the habit to keep: for a capability with many operations, a header that lists the few it needs says more.

### Granting the console: `[run] grants`

A `uses` line asks for the console. The program gets it only when the run grants it. The `grants` line of `una.toml` is that grant:

```toml include="steps/01-hello/una.toml" title="una.toml"
[package]
name = "hello"
version = "0.1.0"
edition = "0.2"

[run]
entry = "hello"
grants = ["console"]
```

The two halves work together. The `uses` line of `main` is a promise to callers and reviewers: this function prints, and does nothing else outside the program. The `grants` line is the decision of whoever runs the program, and so is a `--grant` flag of `una run`, which adds to it for one run. If you remove `console` from the grants, `una check .` still passes, since the code is right, but `una run .` refuses to start: it reports U3012, which says that `main` uses `print` of `Console` and that nothing grants it.

### How printing behaves

- Each `print` writes one line, and the lines appear in the order the steps run.
- `print` adds the end of the line itself. `print("")` writes an empty line.
- A text may hold any printable character, `é` included, in any language.
- `print` takes one value, and it must be a text. [Section 1.4](#s1-4) shows how to print a number.
- A step that prints stands on its own line. Una does not let a call that prints hide inside another computation, so a reader who scans the left edge of a body sees every effect it has, in the order it has them.

### When a function should print

Most functions should not print: they take values and return a value, and a pure function is easy to test, as [section 1.6](#s1-6) shows. Print in `main`, or in a few functions whose job is to print, and give each of them a `uses` line. The packing slip of [section 1.7](#s1-7) has that shape: seven pure functions build the lines, and `main` prints them.

### Check yourself: printing

Two questions, without code.

1. A package's `una.toml` has `grants = []`, and its `main` has `uses @console: Console[print]`. Does `una check .` pass? Does `una run .` start?
2. A module has a public function `slip_title` with no `uses` line. Can its body call `@console.print`?

:::answer Show the answer
1. `una check .` passes: the code asks for the console in its header, and that is all a check needs. `una run .` refuses to start, with U3012, since the run grants nothing that `main` uses.
2. No. A public function without `uses` is pure, and `@console` in its body is U3004, as in [Why a function must ask for the console](#why-a-function-must-ask-for-the-console).
:::

## 1.4 Values, types and names

### What a value is

A **value** is one piece of data: the number `18`, the text `"LAMP-01"`, the answer `true`. A program computes new values from old ones, as `18 - 9` gives `9`, and prints some of them.

Every value has a **type**, which says what kind of value it is, and so what you can do with it. You can multiply two numbers, but not two product names. Think of the fields of a paper form: one box takes a date, another a phone number, and a clerk refuses a form with a name in the date box. Types are those boxes, and `una check` is the clerk. The types of this chapter:

| Type | Its values | Written as |
| --- | --- | --- |
| `Int` | whole numbers, positive, zero or negative | `18`, `1_990`, `-500` |
| `Text` | a sequence of characters | `"Desk lamp, brass"` |
| `Bool` | the answer to a yes-or-no question | `true`, `false` |
| `Unit` | one value only, which carries no information | `unit` |

A value written out in the code, such as `18` or `"LAMP-01"`, is a **literal**. [Chapter 2](/learn/values/) covers each type in full.

### Why every value has a type

`print` takes a text. Give it a number:

```diff include="steps/01-hello..steps/09-print-number:src/hello.una" title="src/hello.una"
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

```text include="steps/09-print-number/expected/rendered.txt#L1"
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

`+`, `-` and `*` add, subtract and multiply. `/` divides and drops the remainder, and `mod` gives the remainder (for numbers that are not negative; [chapter 2](/learn/values/#euclidean-division) shows the rest): `3980 / 100` is 39, and `3980 mod 100` is 80. `*`, `/` and `mod` come before `+` and `-`, as in school arithmetic, and parentheses change the order.

#### Putting values into a text

A name or a computation in braces, inside a text, puts its value into the text: `"{lamps} x {sku}"`. This is an **interpolation**. Numbers, texts and `true` and `false` can all go in braces, and so can a computation, such as `{lamps * lamp_cents}`. An `Int` goes in as plain decimal digits, with no leading zero and no `_`.

### Values in a store

This program names four values, one of each kind it prints, and computes with them:

:::steps
```una include="steps/10-values/src/values.una" title="steps/10-values/src/values.una" verified="check, run"
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

```text include="steps/10-values/expected/output.txt#L1-L5"
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

Then write `una.toml` and `src/opening.una` with your editor, and make `verification.lock` as in [the first package](#the-lock-file-verificationlock). This program prints the store's opening hours:

:::steps
```una include="steps/11-printing/src/opening.una" title="src/opening.una" verified="check, run"
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

```toml include="steps/11-printing/una.toml" title="una.toml"
[package]
name = "opening"
version = "0.1.0"
edition = "0.2"

[run]
entry = "opening"
grants = ["console"]
```

`una run .` prints:

```text include="steps/11-printing/expected/output.txt"
Open today from 9:00 to 18:00
That is 9 hours of trading
Orders placed before 18:00 ship today
```

### How values and names behave

- **No conversions behind your back.** A value keeps its type. An `Int` becomes a text only where the code puts it in braces.
- **One name, one value.** A name made with `let` cannot be given another value, and the same name cannot be made twice in one body. [Chapter 2](/learn/values/#s2-4) shows `let edit`, for a value that must change, such as a running total.
- **A name exists from its line on.** A step can use a name only after the `let` that makes it.
- **Whole numbers have no size limit.** An `Int` never overflows, however large a total grows ([chapter 2](/learn/values/#s2-1)).
- **A text literal cannot go inside braces.** Write `let wood = "oak"`, then `"{wood}"`. [Chapter 2](/learn/values/#a-text-inside-an-interpolation-u0006) shows the diagnostic.
- **Few characters are special.** Besides the quote, the backslash and the braces, every character in a text, `:`, `<`, `x` or a space, prints as it is.

### Check yourself: values

The last four lines of `values` name two hours, then compute with the names and with parentheses:

```una include="steps/10-values/src/values.una#L16-L19" title="steps/10-values/src/values.una"
  let opens = 9
  let closes = 18
  @console.print("{closes - opens - 1} hours of trading, without the lunch hour")
  @console.print("{2 + 3 * 4} and {(2 + 3) * 4}")
```

What do the last two lines print?

:::answer Show the answer
```text include="steps/10-values/expected/output.txt#L6-L7"
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

## 1.5 Functions and comments

### What a function is

A program of one `main` grows long quickly. A **function** gives a piece of the work a name, so that you write it once and use it wherever it is needed. Think of a price lookup at a till: you give it a SKU, and it gives back the price. You do not need to know how it finds the price; you only need its name, what to give it, and what it gives back.

A function's inputs are its **parameters**, and what it gives back is its **result**. Using a function is a **call**: you write its name and the values it should work with, the **arguments**, in parentheses. The code that makes the call is the **caller**, and the call stands for the result.

### Why programs use functions

Here is a program that prints when orders ship at three stores, each line written out in full:

```una include="steps/12-repeated/src/cutoffs.una" title="steps/12-repeated/src/cutoffs.una" verified="check, run"
module cutoffs

--- Prints when orders ship the same day, at each of the three stores.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("Downtown: orders placed before 18:00 ship today")
  @console.print("Harbor: orders placed before 17:00 ship today")
  @console.print("Airport: orders placed before 20:00 ship today")
```

It works, but the sentence "orders placed before … ship today" is written three times. To change it, say to "ship the same day", you change three lines, and missing one prints two wordings. Nothing can test the sentence on its own either, since it exists only inside `print` calls. A function that builds the line from the store and the hour fixes both: the sentence is written once, and a test can call the function and check its result.

### How to write a function

A function is a header and a body:

:::steps
```una include="steps/13-functions/src/notice.una#cutoff_line" title="src/notice.una"
--- The line that tells customers until when an order ships the same day.
pub cutoff_line(hour: Int) -> Text = "Orders placed before {hour}:00 ship today"
```

1. **`pub`.** Public: code in other modules may call it. Leave it out for a function only its own module uses.
2. **`cutoff_line`.** The name, in small letters, digits and `_`, as for values.
3. **`(hour: Int)`.** The parameters, in parentheses: each a name, `:` and a type, separated by commas. `()` means none.
4. **`-> Text`.** The type of the result.
5. **`= "Orders placed before {hour}:00 ship today"`.** The body: the computation whose value is the result. Inside it, `hour` holds the argument of the call.
:::

A call writes the name and the arguments: `cutoff_line(18)` is the text `"Orders placed before 18:00 ship today"`.

### A module of small functions: `notice`

The module `notice` declares two small functions and a `main` that calls them:

:::steps
```una include="steps/13-functions/src/notice.una" title="src/notice.una" verified="check, run"
module notice

-- The notice the store's console shows when the store opens.

--- The hour the store closes, on the 24-hour clock.
pub closing_hour() -> Int = 18

--- The line that tells customers until when an order ships the same day.
pub cutoff_line(hour: Int) -> Text = "Orders placed before {hour}:00 ship today"

--- Prints the notice.
pub main() -> Unit
  uses @console: Console[print]
=
  -- Ask for the hour, then build the line from it.
  let hour = closing_hour()
  @console.print(cutoff_line(hour))
```

1. **`pub closing_hour() -> Int = 18`.** A function of no parameters that returns an `Int`. A function with no `uses` line whose body is one line is written on one line, after `=`. This is its **short form**.
2. **`pub cutoff_line(hour: Int) -> Text`.** One parameter, `hour`, of type `Int`, and a `Text` result. The body is a text that puts `hour` in its place.
3. **`let hour = closing_hour()`.** A call. The parentheses are needed even when there are no arguments.
4. **`cutoff_line(hour)`.** A call with one argument. The value of `hour` becomes the parameter `hour` inside the function.
5. **`-- Ask for the hour, then build the line from it.`** A plain comment, inside a body.
:::

Its package is a directory `notice/`, made as in [Opening hours](#opening-hours), and its manifest names the module `notice`:

```toml include="steps/13-functions/una.toml" title="una.toml"
[package]
name = "notice"
version = "0.1.0"
edition = "0.2"

[run]
entry = "notice"
grants = ["console"]
```

`una run .` prints:

```text include="steps/13-functions/expected/output.txt"
Orders placed before 18:00 ship today
```

### The forms of a function

The module `shipping` has one function of each form. `main` calls each one:

```una include="steps/14-function-forms/src/shipping.una" title="steps/14-function-forms/src/shipping.una" verified="check, run"
module shipping

--- The hour the store closes, on the 24-hour clock: a function with no parameters.
pub closing_hour() -> Int = 18

--- The cutoff line of one store: a function with two parameters.
pub cutoff(store: Text, hour: Int) -> Text = "{store}: orders placed before {hour}:00 ship today"

--- What a line of an order costs, in cents.
pub line_cents(quantity: Int, cents: Int) -> Int = quantity * cents

--- What a line costs when each unit is `off` cents cheaper: the long form, with a body of
--- several lines.
pub discounted(quantity: Int, cents: Int, off: Int) -> Int
=
  let each = cents - off
  quantity * each

-- A private function: no `pub`, so only this module can call it.
welcome(store: Text) -> Text = "Welcome to the {store} store"

--- Prints the cutoff line of one store: a function that prints, so its header says so.
pub announce(store: Text, hour: Int) -> Unit
  uses @console: Console[print]
=
  @console.print(cutoff(store, hour: hour))

--- Calls each function once.
pub main() -> Unit
  uses @console: Console[print]
=
  let hour = closing_hour()
  @console.print(cutoff("Downtown", hour: hour))
  @console.print("{line_cents(2, cents: 1990)} cents")
  @console.print("{discounted(2, cents: 1990, off: 200)} cents")
  @console.print(welcome("Harbor"))
  announce("Airport", hour: 20)
  @console.print("{discounted(3, cents: 500, off: 50)} cents")
  @console.print(cutoff("Harbor", hour: hour - 1))
```

#### No parameters

`closing_hour()` takes nothing and always returns 18. A call still needs its parentheses: `closing_hour()`.

#### Several parameters, and labels at the call

`cutoff(store: Text, hour: Int)` takes two parameters, separated by a comma. A call with more than one argument names every argument after the first, with the name of its parameter and `:`: `cutoff("Downtown", hour: hour)`, `line_cents(2, cents: 1990)`. The first argument may go without its name. Every other one carries it, or is a name equal to the parameter's, as `hour` could be here ([chapter 3](/learn/functions/) shows that short form), so a call reads the same a year from now, without a look at the header.

#### The long form: a body of several lines

`discounted` has a body of two lines, so it is written in the **long form**: the header, `=` alone on its line, then the body, indented two spaces. A body's lines run in order, and the value of its last line is the result: here `quantity * each`. Una has no `return`; the last line is the result.

#### Public and private

`welcome` has no `pub`, so it is **private**: only the module `shipping` can call it. Keep a function private until another module needs it. Here a plain `--` comment says what it is; a doc comment would do too, but it matters most on a public function, whose readers see its header and not its body.

#### A function that prints

`announce` prints, so its header says so, with a `uses` line, as `main`'s does. It returns `Unit`, since it is called for what it does, and `main` calls it as a step of its own: `announce("Airport", hour: 20)`. A function can call a function that uses the console only when it holds the console too, as `main` does.

`una run .` prints:

```text include="steps/14-function-forms/expected/output.txt#L1-L5"
Downtown: orders placed before 18:00 ship today
3980 cents
3580 cents
Welcome to the Harbor store
Airport: orders placed before 20:00 ship today
```

### Two kinds of comment

A **comment** is a note for people, which the program ignores. Una has two kinds:

- `--` starts a **comment**, which runs to the end of its line. It is for the reader of the code.
- `---` starts a **doc comment**, which belongs to the declaration under it. It is part of that declaration's documentation, and tools print it with the declaration's header. Every public function should have one.

Una has no block comments: a comment of several lines repeats `--` or `---` on each, as the doc comment of `discounted` does.

### Doc comments in `una contract`

Tools read doc comments too. `una contract` prints the full header of a function, with its doc comment, named by module and function:

```sh
una contract notice.cutoff_line
```

```text include="steps/13-functions/expected/commands/contract.txt#L2-L3"
--- The line that tells customers until when an order ships the same day.
pub cutoff_line(hour: Int) -> Text
```

This is what a reviewer, an editor or an agent sees of the function without reading its body.

### How a call behaves

#### What happens at a call

1. The arguments are computed, from left to right.
2. Each parameter holds the value of its argument.
3. The body runs, and its value is the result.
4. The call stands for that result in the caller.

`cutoff("Harbor", hour: hour - 1)` computes `hour - 1`, 17, runs the body with `store` holding `"Harbor"` and `hour` holding 17, and gives back the line.

#### Functions that cannot print

`closing_hour` and `cutoff_line` are public and have no `uses` line, so neither can print, read a file or ask the clock. They take values and return a value, and that is all they can do. This is why `main` builds the line with `cutoff_line` and prints it itself: the one function that prints is the one that says so.

#### Calls must match the header

The checker holds every call to its function's header: the number of arguments, their types and their labels. Leave out the label of `cents`:

```diff include="steps/14-function-forms..steps/15-missing-label:src/shipping.una" title="src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -33,3 +33,3 @@
   @console.print(cutoff("Downtown", hour: hour))
-  @console.print("{line_cents(2, cents: 1990)} cents")
+  @console.print("{line_cents(2, 1990)} cents")
   @console.print("{discounted(2, cents: 1990, off: 200)} cents")
```

```text include="steps/15-missing-label/expected/rendered.txt#L1,L8"
[U2004] Error: argument 2 of `line_cents` needs a label; only the first argument may go without one
    │ Help: repair 1: label it `cents`; edit src/shipping.una:34:34..34:38 to "cents: 1990"
```

The message says that argument 2 of `line_cents` needs a label, and the `Help` line gives the exact edit, `cents: 1990`, which `una fix .` applies. An argument of the wrong type is U2001, as `print(18)` was.

#### The order of declarations

The order of declarations in a module is free: `main` may call a function declared after it. Canonical form does not reorder declarations, so keep them in the order a reader needs: the parts first, and `main`, which puts them together, after them.

### When to write a function

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Name a value that one body computes once | `let` |
| Use the same computation in several places | a function |
| Test a computation on its own | a function without `uses`, and an example ([section 1.6](#s1-6)) |
| Print, or reach anything else outside the program | a function with a `uses` line, usually `main` |
| Keep a helper to one module | a function without `pub` |
:::

### Check yourself: functions

`main` of `shipping` ends with two more calls:

```una include="steps/14-function-forms/src/shipping.una#discounted" title="steps/14-function-forms/src/shipping.una"
--- What a line costs when each unit is `off` cents cheaper: the long form, with a body of
--- several lines.
pub discounted(quantity: Int, cents: Int, off: Int) -> Int
=
  let each = cents - off
  quantity * each
```

What do `discounted(3, cents: 500, off: 50)` and `cutoff("Harbor", hour: hour - 1)`, with `hour` holding 18, give? The last two lines of `main` print them.

:::answer Show the answer
```text include="steps/14-function-forms/expected/output.txt#L6-L7"
1350 cents
Harbor: orders placed before 17:00 ship today
```

In `discounted`, `each` is 500 − 50, 450, and the result is 3 × 450, 1350. In `cutoff`, the argument `hour - 1` is computed first, 17, and the body puts it in the line.
:::

## 1.6 Examples and `una test`

### What an example is

An **example** is a small test, written in the module next to the code it tests: it calls a function with chosen arguments and states what the result must be. It is like checking a new calculator with 2 + 2 before you trust it with a bill. `una test` runs every example and reports which hold.

### Why programs need tests

`una check` proves many things, but not what you meant. If `cutoff_line` says "ship tomorrow" when the store means "ship today", the code checks: the checker cannot know which sentence is right. An example states the sentence you meant, and fails the moment the code says something else.

### Writing an example

A function that returns a value is easy to test: call it, and compare what it returns with what you expect. The module `notice` ends with two examples:

:::steps
```una include="steps/16-examples/src/notice.una#L19-L25" title="src/notice.una" caption="two examples at the end of the module"
example "the store closes at six in the evening"
  do closing_hour()
  expect result == 18

example "the cutoff line names the hour"
  do cutoff_line(18)
  expect result == "Orders placed before 18:00 ship today"
```

1. **`example "the store closes at six in the evening"`.** An example has a name in quotes. Write it as the fact the example checks, since that is what `una test` reports.
2. **`do closing_hour()`.** The call under test, on its own line.
3. **`expect result == 18`.** A fact that must hold. `result` is the value the `do` call returned, and `==` compares two values: it is `true` when they are equal. An example may have several `expect` lines, and each must hold.
:::

### Running the examples

Run every example of the package:

```sh
una test .
```

```text include="steps/16-examples/expected/commands/test.txt#L2-L5"
example notice "the store closes at six in the evening" ... ok
example notice "the cutoff line names the hour" ... ok

2 examples: 2 passed, 0 failed
```

Each example gets a line, with the module, the name, and `ok` when every `expect` holds. The last line counts them.

### A failing example

When an `expect` does not hold, the example fails, and the report says which line and what the value was. Here the second example expects a different wording than the function gives:

```diff include="steps/16-examples..steps/17-failing:src/notice.una" title="src/notice.una" context="1"
--- a/src/notice.una
+++ b/src/notice.una
@@ -24,2 +24,2 @@
   do cutoff_line(18)
-  expect result == "Orders placed before 18:00 ship today"
+  expect result == "Orders placed before 18:00 ship the same day"
```

```text include="steps/17-failing/expected/commands/test.txt#L2-L7"
example notice "the store closes at six in the evening" ... ok
example notice "the cutoff line names the hour" ... FAILED
  src/notice.una:25: expect result == "Orders placed before 18:00 ship the same day"
  it is false, with `result` = `"Orders placed before 18:00 ship today"`

2 examples: 1 passed, 1 failed
```

Read the report from the top. `FAILED` names the example. The next line gives the place of the `expect` that did not hold, `src/notice.una:25`, and repeats it. The last line gives the value of `result`, so you can compare it with what the example expects. `una test .` exits with code 1, so a script can stop on a failed test. Whether the function or the example is wrong is your call: here the function says what the store means, so the fix is to the example.

### How examples behave

#### Examples are checked code

Examples are code, and `una check .` checks them as it checks the rest of the module. An `expect` that compares an `Int` result with a text is a type error at check time, not a failed test at run time:

```diff include="steps/13-functions..steps/18-example-type:src/notice.una" title="src/notice.una" context="1"
--- a/src/notice.una
+++ b/src/notice.una
@@ -17 +17,9 @@
   @console.print(cutoff_line(hour))
+
+example "the store closes at six in the evening"
+  do closing_hour()
+  expect result == "18"
+
+example "the cutoff line names the hour"
+  do cutoff_line(18)
+  expect result == "Orders placed before 18:00 ship today"
```

```text include="steps/18-example-type/expected/rendered.txt#L1"
[U2001] Error: `==` needs operands of one type, and these are `Int` and `Text`
```

`==` compares values of one type, and `closing_hour()` returns an `Int`.

#### What an example may do

An example may call any function of its module, public or private, and it never prints: `una run .` ignores the examples, and `una test .` runs nothing but them. `una test .` checks the package first, as `una run .` does, so an example runs only in a package that checks clean.

#### One fact per example

A good example states one fact, in its name and in its `expect` lines. When it fails, its name tells you what broke before you read any code. Prefer exact values over loose ones: `expect result == "Orders placed before 18:00 ship today"` catches a change of one word, which a test of the length alone would miss.

### What to test, and what not

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Pin what a pure function returns for one input | an example with `expect result == …` |
| Cover an input the program does not reach today, such as zero units | one more example |
| Know that the code has the right types and authority | `una check .`, which needs no example |
| Test a function that prints | [chapter 10](/learn/testing/), with a fake console: a stand-in that records what would be printed |
:::

### Check yourself: examples

This example is added at the end of `notice`:

```una include="steps/19-early-cutoff/src/notice.una#L27-L29" title="steps/19-early-cutoff/src/notice.una"
example "the cutoff line for nine in the morning"
  do cutoff_line(9)
  expect result == "Orders placed before 09:00 ship today"
```

Does it pass?

:::answer Show the answer
It fails:

```text include="steps/19-early-cutoff/expected/commands/test.txt#L4-L6"
example notice "the cutoff line for nine in the morning" ... FAILED
  src/notice.una:29: expect result == "Orders placed before 09:00 ship today"
  it is false, with `result` = `"Orders placed before 9:00 ship today"`
```

An interpolation writes an `Int` in its plain decimal form, with no leading zero: `9`, not `09`. The function is right for the store's notice, so the fix is to the example.
:::

## 1.7 Day-to-day: a packing slip

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

- `title`, `count_line` and `total_line` put `Int` parameters into a text with interpolation, as in [section 1.4](#s1-4).
- `ship_to` and `item` take two and three parameters, separated by commas. The angle brackets in `ship_to` and the `x` in `item` are plain characters of the text: only braces are special.
- `item` starts with two spaces, inside the text, so that the item lines stand out on paper.
- `line_cents` returns an `Int`, not a text: it multiplies two `Int` values with `*`.
- `closing` takes no parameters and always returns the same text.

Money is in **cents**, as an `Int`: 1990 is 19 units and 90 cents. Whole cents never round, so the total is exact. [Chapter 2](/learn/values/) shows how to print them as an amount with two decimals.

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

The calls with more than one argument name every argument after the first: `line_cents(lamps, cents: 1990)`, `item(lamps, sku: "LAMP-01", name: "Desk lamp, brass")`, as [section 1.5](#s1-5) explains. [Chapter 3](/learn/functions/) gives the full rule.

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

## 1.8 Testing it

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

## 1.9 Common mistakes

Each mistake below is a small change to `day-to-day/src/slip.una`, followed by what `una check .` reports. Read each diagnostic as [section 1.2](#s1-2) shows: the message, then the place, then the help.

### Single quotes (U0001)

:::mistake
Write a text between single quotes, as many languages allow:

```diff include="day-to-day..mistakes/1:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -36,3 +36,3 @@
   @console.print(ship_to(318, email: "customer318@example.invalid"))
-  @console.print(item(lamps, sku: "LAMP-01", name: "Desk lamp, brass"))
+  @console.print(item(lamps, sku: "LAMP-01", name: 'Desk lamp, brass'))
   @console.print(item(rugs, sku: "RUG-07", name: "Wool rug, 120 by 180 cm"))
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U0001] Error: invalid character `'`; text literals use double quotes
```

*Why:* a text in Una is written between double quotes only. A single quote is not a character Una code may contain outside a text or a comment, so each of the two is reported. The message names the character and the rule, and the marks point at each quote.

*Fix:* `"Desk lamp, brass"`. See [U0001](/docs/errors/U0001/).
:::

### A comment with `//` (U0101)

:::mistake
Start the comment at the top of the module the way C, Java or TypeScript do:

```diff include="day-to-day..mistakes/2:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -2,4 +2,4 @@
 
--- A packing slip: the sheet that goes into the box with an order, so that the customer
--- can check what arrived. This version prints the slip of one sample order.
+// A packing slip: the sheet that goes into the box with an order, so that the customer
+// can check what arrived. This version prints the slip of one sample order.
 
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U0101] Error: unexpected `/`, expected a declaration
```

*Why:* a comment in Una starts with `--`, and a doc comment with `---`. `/` is division, and a module cannot start a declaration with it. The message says what the checker found, `/`, and what it expected in that place, a declaration: a mistake of **syntax**, the rules of how code is written.

*Fix:* `-- A packing slip: …`. See [U0101](/docs/errors/U0101/).
:::

### Printing without `uses` (U3004)

:::mistake
Remove the `uses` line from `main`:

```diff include="day-to-day..mistakes/3:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -28,3 +28,2 @@
 pub main() -> Unit
-  uses @console: Console[print]
 =
```

```text include="mistakes/3/expected/rendered.txt#L1,L8"
[U3004] Error: `@console` is used here, but this code declares no `uses`, so it is pure
    │ Help: repair 1 (widens authority: the function then holds this authority, and every caller must hold it too: check that the operation belongs to this function's job): declare `uses @console: ...` in the header, with the capability and the operations used
```

*Why:* a public function without `uses` is pure: it cannot use any capability. una reports U3004 once for each of the seven `@console` lines, since each is a separate use. The words in parentheses in the `Help` line are a warning: this repair gives the function more authority, so check that printing is its job.

*Fix:* put the line back: `uses @console: Console[print]`. See [U3004](/docs/errors/U3004/).
:::

### A module named unlike its file (U1008)

:::mistake
Rename the module in its first line, but not the file:

```diff include="day-to-day..mistakes/4:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -1,2 +1,2 @@
-module slip
+module packing
 
```

```text include="mistakes/4/expected/rendered.txt#L1,L8,L12"
[U1008] Error: module `packing` is in `src/slip.una`, which must hold module `slip`
   │ Help: repair 1: declare `module slip`, or move the file to match `packing`; edit src/slip.una:1:8..1:15 to "slip"
[U7002] Error: [run] entry `slip` is not a module of this package
```

*Why:* `src/slip.una` must hold the module `slip`. One change breaks two links, so una reports two diagnostics: U1008 for the file and its `module` line, and U7002, since the manifest's `entry = "slip"` now names a module that does not exist. Fix the first, and the second goes with it.

*Fix:* keep the names in step: the file, the `module` line and the `entry` of `una.toml`. `una fix .` applies the edit of the `Help` line. See [U1008](/docs/errors/U1008/).
:::

### Printing a number (U2001)

:::mistake
Print the total itself, instead of the line that holds it:

```diff include="day-to-day..mistakes/5:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -39,3 +39,3 @@
   @console.print(count_line(lamps + rugs, lines: 2))
-  @console.print(total_line(lamp_cents + rug_cents))
+  @console.print(lamp_cents + rug_cents)
   @console.print(closing())
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U2001] Error: argument `line` of operation `Console.print` must be `Text`, found `Int`
```

*Why:* `print` takes a `Text`, and `lamp_cents + rug_cents` is an `Int`. Una converts no value to another type unless the code says so. The message names the parameter, `line`, the type it must have and the type it got.

*Fix:* put the number in a text, `"{lamp_cents + rug_cents}"`, or call `total_line`, which does. See [U2001](/docs/errors/U2001/).
:::

### Indenting by four spaces (U0003)

:::mistake
Indent the first line of the body of `main` by four spaces, a habit from other languages:

```diff include="day-to-day..mistakes/6:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -30,3 +30,3 @@
 =
-  let lamps = 2
+    let lamps = 2
   let rugs = 1
```

```text include="mistakes/6/expected/rendered.txt#L1,L8,L10"
[U0003] Error: inconsistent indentation of 4 spaces; expected 0 or 2
    │ Help 1: repair 1: indent with 2 spaces; edit src/slip.una:31:1..31:5 to "  "
    │ Help 2: repair 2: remove the indentation; edit src/slip.una:31:1..31:5 to ""
```

*Why:* in Una, indentation is part of the syntax: it says which lines belong to which body. Each level is exactly two spaces deeper than the one around it. The body of `main` is one level deep, so its lines start with two spaces. The message gives the two depths that would be valid, 0 and 2, and each `Help` line offers one.

*Fix:* two spaces. The first repair is an exact edit, and `una fix .` applies it. Indent with spaces only: a tab in the indentation is an error too. See [U0003](/docs/errors/U0003/).
:::

## 1.10 Exercises

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
*Hint:* a kilogram is 1000 grams. `/` divides two `Int` values and drops the remainder, and `mod` gives the remainder: `2350 / 1000` is 2, and `2350 mod 1000` is 350. Both can go inside the braces of a text, as in [section 1.4](#s1-4).
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

`cents mod 100 / 10` is the tens of cents, and `cents mod 10` the cents left over, so each digit is printed on its own and a zero is never lost. This works for an amount that is not negative; [chapter 3](/learn/functions/) shows `if`, for the cases that need a choice.
:::
::::

## 1.11 Recap and reference

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
