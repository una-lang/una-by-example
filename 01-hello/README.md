---
learn: "1"
title: Hello, Una
editions: ["0.2"]
codes: [U0001, U0003, U0101, U1001, U1002, U1008, U2001, U2004, U3003, U3004, U7002]
time: 50
builds: The store's morning notices, printed on the console, with an example for each notice
prerequisites: []
template: 2
nav: ["Your first program", "Modules", "The main function", "Writing a function", "Printing and uses", "Day-to-day: morning notices", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 1 Hello, Una

A program is a set of instructions that a computer follows, written in a language that both you and the computer can read. This chapter is where you write your first one. It assumes no experience: every word it uses is explained the first time it appears. You start from an empty directory and write a program that prints "Hello, world". Then you learn the parts every Una program is made of: modules, the `main` function, functions of your own, and printing. You end with a small program that a store prints every morning, checked, run and tested.

## What you'll build

:::build
The morning notices of a store: the lines its console prints when the store opens, with the hours, the shipping cutoff, the offer of the day and the café. The program prints:

```text include="day-to-day/expected/output.txt"
Harbor Street store
Good morning
------------------------------
Hours
Open today from 9:00 to 18:00
------------------------------
Shipping
Orders placed before 17:00 ship today
------------------------------
Offer
Today's special: desk lamps
------------------------------
Café
The café opens at 10:00
------------------------------
Questions? Ask at the help desk by the main door
```

You will learn to:

- set up a package from an empty directory, and run `una check` and `una run` in it;
- read what a module is, and what its first line says;
- write the `main` function, where a program starts;
- write functions of your own, with parameters and a result, and call them;
- print on the console, and say in a function's header that it prints.
:::

## Why it works this way

A program grows. The first version prints one line; a year later it has hundreds of lines, written by several people. Two things make such a program hard to change. The first is not knowing where anything is: the same sentence typed in five places, so that a change misses one. The second is not knowing what a piece of code does to the world outside the program: whether it only computes, or also prints, writes files or sends messages.

Una answers both from the first program on. Code lives in modules, files with a name, and the work is split into functions, each with a name, its inputs and its result, so that each thing is written once. The first lines of a function, its header, also say what it may do outside the program. A function that prints says so, and Una refuses one that prints without saying it. You can read a function's header and know what the function may do, without reading its body.

> [!KEY]
> In Una, a function's first lines say what it takes, what it gives back, and what it may do outside the program, such as printing.

## 1.1 Your first program: hello world

### What a program is

A **program** is a list of instructions for a computer, such as "write this line on the screen". Think of a recipe: it names what it needs, then gives the steps in order, and anyone who follows it gets the same dish. A computer follows a program the same way, one step after another, exactly as written.

You write a program as text, in a file, in a **programming language**: a small language with strict rules, so that each line has one meaning. That text is the **source code**, or just the code. This book teaches the language Una.

A few more words come up on every page:

- **Running** a program means having the computer follow its instructions.
- The **console** is the window of text where you type commands and where a program writes its lines. [Section 1.5](#s1-5) covers it.
- `una` is the tool that reads Una code. It **checks** the code, which means it looks for mistakes without running it, and it **runs** the code when the check passes.

### What you need: a terminal, `una` and Z3

Una runs on macOS, on Macs with Apple silicon, and on Linux, on x86-64 and ARM computers: those are the systems each release of `una` is built for.

You work with `una` in a **terminal**: the program that shows the console on your screen. To open one:

- on macOS, open the Terminal app, in Applications > Utilities, or find it by typing "Terminal" in Spotlight, which [[Cmd]]+[[Space]] opens;
- on Linux, open the Terminal app from your applications menu; on many systems [[Ctrl]]+[[Alt]]+[[T]] opens one.

In the terminal you type a **command**, a line that names a program and what it should do, and press [[Enter]]; the program runs and prints its answer under the command.

Next, install `una` and Z3, a program that `una` asks to prove facts about your code. The programs of this chapter need no proof, but from [chapter 2](/learn/numbers/) on, `una check` cannot prove anything without Z3. The [install page](/docs/install/) installs both, at the versions that go together, and sets up your terminal so that typing `una` runs it from any directory.

### Checking the install: `una --version`

To see that the install worked, type `una --version` and press [[Enter]]. It prints the version of `una`, the editions of the language it supports, and the version of Z3 it expects. Then type `z3 --version`, which must report that same version of Z3.

If `una --version` answers `unexpected argument '--version'` instead, the `una` that ran is a release older than 0.3, which did not know `--version` yet. Run the installer again, as the [install page](/docs/install/) says, to get the current release.

If `una --version` still gives the same answer, an old copy of `una` is in the way. When you type `una`, the terminal looks for a program of that name in a list of directories, in order, and runs the first one it finds. That list is your **PATH**. The installer puts the new `una` at `~/.una/bin/una`, where `~` stands for your home directory. Type `which -a una`: it prints the path of every copy of `una` the terminal can find, the one it runs first at the top. Delete every copy that is not the one in `~/.una/bin`, or move it out of the directories the list names. Then open a new terminal, so that it starts with the updated PATH, and type `una --version` again.

### Hello, world: the whole program

This is a whole Una program. It prints one line, `Hello, world`, the line that first programs have printed in many languages for decades:

```una include="steps/01-hello/src/hello.una" title="src/hello.una" verified="check, run"
module hello

--- Greets the world.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("Hello, world")
```

Each line is explained in this chapter, and you can read most of it already:

- `module hello` names this file of code. [Section 1.2](#s1-2) covers modules.
- `--- Greets the world.` is a note for people, which the computer does not run.
- `pub main() -> Unit` and the lines under it are the function `main`, where the program starts. [Section 1.3](#s1-3) covers `main`.
- `uses @console: Console[print]` says that this function may print on the console. [Section 1.5](#s1-5) covers printing.
- `@console.print("Hello, world")` prints the text between the double quotes.

To run it, you put it in a package, then ask `una` to check and run it.

### Making the package

Una keeps a program's files together in a **package**: a **directory** (a folder) with a manifest, `una.toml`, a lock file, `verification.lock`, and the code under a directory named `src/`. Every program in this book is a package, so it is worth making the first one by hand.

A new terminal starts in your **home directory**: the directory that holds your own files and directories, such as `Documents`. The terminal is always "in" one directory, and commands work there. Two commands move you around:

- `mkdir hello` makes a directory named `hello` in the directory you are in;
- `cd hello` moves the terminal into `hello`, so that the next commands work there.

Make the directory `hello` in your home directory, move into it, and make `src` inside it:

```sh
mkdir hello
cd hello
mkdir src
```

A **path** names a file or a directory by the directories that lead to it, separated by `/`: `hello/src` is the directory `src` inside `hello`, and `src/hello.una` is the file `hello.una` inside `src`. A path without a leading `/` starts from the directory you are in.

The **manifest** is a short file of settings that `una` reads before it reads any code. You write it with a **text editor**: a program that saves exactly the characters you type, with no fonts or formatting. Any code editor works. On macOS, TextEdit works too, once you choose Format > Make Plain Text before you type; on Linux, the text editor that comes with your system works. Create a new file, write these lines, and save it in the `hello` directory with the name `una.toml` exactly. If the editor offers to add `.txt` to the name, refuse it: `una.toml.txt` is a different file, and `una` does not read it.

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
- `[run]` says how `una run` starts the program. `entry` names the module that holds `main`, and `grants` lists what the program may use outside itself when it runs: here, the console. [Section 1.5](#s1-5) explains grants.

The second file, `verification.lock`, tells `una` which version of Z3 to use and how much work a proof may take, so that a check that passes on your computer passes on every other one. You do not need to understand its lines yet: copy them as they are. The file is the same in every package of this book. Create it with your editor, and save it in `hello` with the name `verification.lock`:

```text include="steps/01-hello/expected/commands/explain-u7004.txt#L32-L37"
encoding_version = "una-smt-1"
solver           = "z3"
solver_version   = "5.1.0"
logic            = "QF_UFLIA"
step_budget      = 5000000
random_seed      = 0
```

`una explain U7004` prints these lines too, under "Fixed example", so you can copy the lock from your terminal at any time. Take that one: the lock it shows first, under "Failing example", is the broken one. [Chapter 11](/learn/packages/#s11-3) explains both files in full.

Last, save the program itself as `src/hello.una`: the file `hello.una` in the directory `src`.

### Checking and running it

In the `hello` directory, check the package, then run it:

```sh
una check .
una run .
```

The `.` names the current directory, the package's. `una check .` prints nothing when the package is right. `una run .` checks again, then runs `main`, and the console shows what it prints:

```text include="steps/01-hello/expected/output.txt"
Hello, world
```

That is your first program. Every program in this book is made the same way: a directory with `una.toml`, `verification.lock` and a module under `src/`, then `una check .` and `una run .` in that directory.

### If `una check` finds a mistake

A mistake in a program is normal: everyone makes them while writing code. Una finds as many as it can before the program runs. Here is the program with one letter left out of `print`:

```diff include="steps/01-hello..steps/02-typo:src/hello.una"
--- a/src/hello.una
+++ b/src/hello.una
@@ -4,4 +4,4 @@
 pub main() -> Unit
   uses @console: Console[print]
 =
-  @console.print("Hello, world")
+  @console.prnt("Hello, world")
```

`una check .` reports a **diagnostic**, a report of one problem:

```text include="steps/02-typo/expected/rendered.txt"
[U1001] Error: capability `Console` has no operation `prnt`
   ╭─[ src/hello.una:7:12 ]
   │
 7 │   @console.prnt("Hello, world")
   │            ──┬─
   │              ╰─── capability `Console` has no operation `prnt`
   │
   │ Help: repair 1: write `print`; edit src/hello.una:7:12..7:16 to "print"
   │
   │ Note: run `una explain U1001` for an explanation
───╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

Read it in three steps:

1. **The first line says what is wrong.** `U1001` is the diagnostic's **code**, the name of this kind of problem, and the message says that the console has no operation named `prnt`.
2. **The box shows where.** `src/hello.una:7:12` is the file, the line 7 and the column 12, the 12th character of the line. The line is shown under it, and the marks point at the word.
3. **`Help` suggests a repair.** Here: write `print`.

`una run .` checks first, so it refuses to run a program with a mistake like this one, and prints the same diagnostic. Fix the word, and `una check .` prints nothing again. [Section 18.2](/learn/tools/#s18-2) reads diagnostics in depth.

### How a package is laid out

The pieces fit together by name, and `una` checks each link:

- The directory holds `una.toml`, `verification.lock` and `src/`.
- Each file `src/<name>.una` holds the module `<name>`, and its first line says `module <name>`.
- `entry` in `una.toml` names one of those modules, and that module has `pub main() -> Unit`.
- `una check .` reads every file of the package; `una run .` checks, then runs `main`.

The package's name in `una.toml`, `hello`, need not match its directory's name, though here it does.

### Check yourself: a first program

You change the program's last two lines to these, and save the file:

```una include="steps/03-hello-una/src/hello.una#main" title="src/hello.una"
--- Greets the language you are learning.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("Hello, Una")
```

What does `una run .` print now? And what does `una check .` print?

:::answer Show the answer
```text include="steps/03-hello-una/expected/output.txt"
Hello, Una
```

`una run .` prints the new text, exactly as it stands between the double quotes. `una check .` prints nothing, since the package is still right. The doc comment changed too, but it is a note for people: it prints nothing.
:::

## 1.2 Modules

### What a module is

A **module** is one file of Una code, with a name. Think of the chapters of a binder of store procedures: each chapter has a title on its first page, and holds the procedures on one subject. A module's first line is its title, and what follows are its **declarations**: each one gives a name to something, such as a function, a named list of steps. In this chapter, every declaration is a function.

A small program is one module. A larger one is several, each on one subject, such as prices or shipping; [chapter 11](/learn/packages/) shows how modules use each other.

### Why code lives in named modules

A program of one file without names would work, for a while. But a reader looking for the opening hours of the store would have to read all of it, and two people changing it at once would change the same file. Modules give each subject its own file, and their names let `una` find a module from its file, and a file from its module. That is why the name of the file and the first line of the module must agree: `una` checks that they do.

### How to write a module

A module is a file `src/<name>.una` in the package. Here is the module `opening`, in the file `src/opening.una`:

:::steps
```una include="steps/04-opening/src/opening.una" title="src/opening.una" verified="check, run"
module opening

-- The notices of the store's front door.

--- Prints when the store opens.
pub main() -> Unit
  uses @console: Console[print]
=
  -- One line, for the sign on the door.
  @console.print("The store opens at 9:00")

--- Prints when the store closes.
pub closing() -> Unit
  uses @console: Console[print]
=
  @console.print("The store closes at 18:00")
```

1. **`module opening`.** The module line: the keyword `module` and the module's name. A **keyword** is a word with a fixed meaning in the language. The name must be the file's name without `.una`, written in small letters, digits and `_`.
2. **`-- The notices of the store's front door.`** A **comment**: a note for people, which `una` skips. It starts with `--` and runs to the end of its line.
3. **`--- Prints when the store opens.`** A **doc comment**: three dashes, right above a declaration. It belongs to that declaration and documents it; tools print it with the declaration's header. Every public declaration should have one.
4. **`pub main() -> Unit` …** The first declaration, the function `main`.
5. **`-- One line, for the sign on the door.`** A comment may also stand inside a function, on a line of its own.
6. **`pub closing() -> Unit` …** A second declaration, the function `closing`, after a blank line.
:::

Its package is made as in [Making the package](#making-the-package), with `entry = "opening"` in `una.toml`. `una run .` prints:

```text include="steps/04-opening/expected/output.txt"
The store opens at 9:00
```

Only one line: `una run .` runs `main`, and `main` does not call `closing`. A declaration is not a step of the program; it only gives a name to something that a step can use. [Section 1.4](#s1-4) shows how one function calls another.

### Comments, line by line

Una has two kinds of comment, and no other:

- `--` starts a comment for the reader of the code. It may stand on a line of its own, at the top of the module or inside a body.
- `---` starts a doc comment, which documents the declaration right under it.

Una has no comment that spans several lines on its own: a note of several lines repeats `--` or `---` on each. A comment written another way is not a comment, and `una check` reports the line, as [A comment with `//`](#a-comment-with-u0101) shows.

### How a module behaves

`una check .` holds every module to three rules.

#### The module line matches the file

Change the first line of `src/opening.una` to `module door`, and `una check .` reports:

```text include="steps/05-module-name/expected/rendered.txt#L1-L11"
[U1008] Error: module `door` is in `src/opening.una`, which must hold module `opening`
   ╭─[ src/opening.una:1:8 ]
   │
 1 │ module door
   │        ──┬─
   │          ╰─── module `door` is in `src/opening.una`, which must hold module `opening`
   │
   │ Help: repair 1: declare `module opening`, or move the file to match `door`; edit src/opening.una:1:8..1:12 to "opening"
   │
   │ Note: run `una explain U1008` for an explanation
───╯
```

The message says both names: the module's, `door`, and the one its file asks for, `opening`. The `Help` line offers both repairs: change the name, or move the file. A second diagnostic, `U7002`, follows: `entry` in `una.toml` names the module `opening`, which the package no longer has. Fix the first line, and both go away.

#### Each name is declared once

Rename `closing` to `main`, so that the module declares `main` twice:

```text include="steps/06-twice/expected/rendered.txt"
[U1002] Error: `main` is defined twice in this module, both times as a function
    ╭─[ src/opening.una:13:5 ]
    │
  6 │ pub main() -> Unit
    │     ──┬─
    │       ╰─── first defined here
    │
 13 │ pub main() -> Unit
    │     ──┬─
    │       ╰─── `main` is defined twice in this module, both times as a function
    │
    │ Note: run `una explain U1002` for an explanation
────╯
```

Two declarations with one name would leave `una run .` unable to tell which `main` to start, so a module gives each name once. The diagnostic points at both: where the name was first given, and where it is given again.

#### The order of declarations does not matter

The declarations of a module may come in any order. `closing` could come before `main`, and the program would print the same line. Most modules put the small pieces first and `main` last, so that a reader meets each piece before the code that uses it.

### When to start a new module

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Write a small program, as in this chapter | one module, named after what it does |
| Keep code on another subject apart, such as prices | a module of its own ([chapter 11](/learn/packages/)) |
| Leave a note for the reader of the code | a comment, `--` |
| Document what a declaration is for | a doc comment, `---`, right above it |
:::

### Check yourself: modules

The file `src/opening.una` starts with this line instead:

```una include="steps/07-capital/src/opening.una#L1"
module Opening
```

Does `una check .` pass?

:::answer Show the answer
No:

```text include="steps/07-capital/expected/rendered.txt#L1"
[U0101] Error: unexpected `Opening`, expected a module path
```

A module's name is written in small letters, so `Opening`, with a capital letter, is not a name a module line accepts: `una` expected "a module path", a module's name. Write `module opening`, the file's name.
:::

## 1.3 The `main` function

### What `main` is

A program has many functions, and one of them is where a run starts: `main`. Think of the first step of a recipe: you may read the recipe in any order, but you cook it from step one. When you type `una run .`, `una` finds the module that `entry` names in `una.toml`, finds its function `main`, and follows the steps of `main` from the first to the last. When the last step ends, the program ends.

### Why a program has one starting point

A module may declare many functions, in any order, as [section 1.2](#s1-2) shows. Without a fixed starting point, nobody could tell which of them runs first. With `main`, the answer is always the same: `una run .` starts at `main` of the entry module, and everything else runs because `main`, or a function it calls, asks for it.

### How to write `main`

Here is a `main` with three steps:

:::steps
```una include="steps/08-greeting/src/greeting.una" title="src/greeting.una" verified="check, run"
module greeting

--- Greets the first customers of the day.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("Good morning")
  @console.print("The store is open")
  @console.print("Today's special: desk lamps")
```

1. **`pub`.** Makes `main` **public**: reachable from outside its module, which is how `una run .` reaches it. [Chapter 6](/learn/functions/#s6-3) covers `pub` in full.
2. **`main`.** The name, exactly `main`.
3. **`()`.** The parameters, the inputs of the function. `main` takes none, so the parentheses are empty.
4. **`-> Unit`.** What the function gives back when it ends. `Unit` means nothing useful: `main` runs for what it does, not for a value.
5. **`uses @console: Console[print]`.** What the function may do outside the program: print. [Section 1.5](#s1-5) explains the line.
6. **`=`, then the body.** The **body** is the list of steps, each on its own line and indented by two spaces under `=`. The first lines, from `pub` to the `uses` line, are the function's **header**.
:::

The package's `una.toml` names the module `greeting` as its entry:

```toml include="steps/08-greeting/una.toml" title="una.toml"
[package]
name = "greeting"
version = "0.1.0"
edition = "0.2"

[run]
entry = "greeting"
grants = ["console"]
```

`una run .` prints:

```text include="steps/08-greeting/expected/output.txt"
Good morning
The store is open
Today's special: desk lamps
```

### How `main` behaves

- **The steps run in order.** Each step runs to its end before the next one starts, from the top of the body to the bottom.
- **The program ends with `main`.** When the last step of `main` ends, the program ends.
- **`main` is found by its header.** `una run .` looks in the entry module for exactly `pub main() -> Unit`. A module without one may still check clean, since it may be meant for other modules to use, but `una run .` refuses to start it, and says that the module has no `pub main() -> Unit` to run. The same happens when `main` lacks `pub`.
- **The entry names the module.** `entry = "greeting"` names the module `greeting`, the file `src/greeting.una`. A package has one entry, and so one `main` that `una run .` starts.

### When the program grows

`main` is where a run starts, not where all the work must be. As a program grows, its steps move into functions of their own, and `main` calls them in order, so that it reads like a table of contents: first the greeting, then the hours, then the offers. [Section 1.4](#s1-4) shows how to write such functions.

### Check yourself: `main`

The sign on a store's front door is printed by this program:

```una include="steps/09-door-sign/src/sign.una#main" title="src/sign.una"
--- Prints the sign for the front door, with an empty line between its two parts.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("Welcome")
  @console.print("")
  @console.print("Open from 9:00 to 18:00")
  @console.print("Closed on public holidays")
```

What does `una run .` print?

:::answer Show the answer
```text include="steps/09-door-sign/expected/output.txt"
Welcome

Open from 9:00 to 18:00
Closed on public holidays
```

Four lines, in the order of the four steps. The second step prints an empty text, `""`, which is a line with nothing on it.
:::

## 1.4 Writing a function

### What a function is

A **function** is a named piece of a program. It may take inputs, it does its work, and it may give back a value when it is done. Think of a price lookup at a till: you give it a SKU, the code of a product, and it gives back the price. You need only its name, what to give it, and what it gives back; you do not need to know how it finds the price.

A function's inputs are its **parameters**, and what it gives back is its **result**. Using a function is a **call**: you write its name and, in parentheses, the values it should work with, its **arguments**. The code that makes the call is the **caller**, and the call stands for the result.

A **value** is one piece of data a program works with, such as the text `"Good morning"`. Every value has a **type**, the kind of value it is: a text in double quotes has the type `Text`. [Chapter 2](/learn/numbers/#s2-1) covers values and types in full, and [chapter 3](/learn/text-and-conditions/#s3-1) covers text.

### Why programs use functions

Here is a board by the entrance of a store, with the hours at the top and again at the bottom:

```una include="steps/10-repeated/src/board.una#main" title="src/board.una" verified="check, run"
--- Prints the board by the entrance: the hours at the top and again at the bottom.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("Open today from 9:00 to 18:00")
  @console.print("Fresh stock: desk lamps and wool rugs")
  @console.print("The café opens at 10:00")
  @console.print("Open today from 9:00 to 18:00")
```

It works, but the hours are written twice. When the store changes its hours, you must change two lines, and a missed one prints two different hours on the same board. A function that gives back the hours writes them once:

```una include="steps/11-function/src/board.una" title="src/board.una" verified="check, run"
module board

--- When the store is open today.
pub opening_hours() -> Text = "Open today from 9:00 to 18:00"

--- Prints the board by the entrance: the hours at the top and again at the bottom.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(opening_hours())
  @console.print("Fresh stock: desk lamps and wool rugs")
  @console.print("The café opens at 10:00")
  @console.print(opening_hours())
```

Both versions print the same board:

```text include="steps/11-function/expected/output.txt"
Open today from 9:00 to 18:00
Fresh stock: desk lamps and wool rugs
The café opens at 10:00
Open today from 9:00 to 18:00
```

Now the hours live in one place, under one name, `opening_hours`. A change there changes every line that uses it, and the name tells the reader what the text is.

### How to write a function

A function is a header and a body. The function `opening_hours` takes no parameters and gives back a text:

:::steps
```una include="steps/11-function/src/board.una#opening_hours" title="src/board.una"
--- When the store is open today.
pub opening_hours() -> Text = "Open today from 9:00 to 18:00"
```

1. **`pub`.** Public, as for `main`: other modules may call it. Leave it out, and only its own module can.
2. **`opening_hours`.** The name: small letters, digits and `_`, starting with a letter. A good name says what the result is.
3. **`()`.** The parameters, in parentheses. `()` means none.
4. **`-> Text`.** The type of the result: this function gives back a text.
5. **`= "Open today from 9:00 to 18:00"`.** The body: the value the function gives back.
:::

A call writes the name and the parentheses: `opening_hours()` stands for the text `"Open today from 9:00 to 18:00"`. The parentheses are needed even when there are no arguments. In `main`, `@console.print(opening_hours())` first calls `opening_hours`, then prints the text the call gives back.

### The forms of a function

The module `notices` has one function of each form, and a `main` that calls them:

```una include="steps/12-function-forms/src/notices.una" title="src/notices.una" verified="check, run"
module notices

--- When the store is open today: a function with no parameters, in the short form.
pub opening_hours() -> Text = "Open today from 9:00 to 18:00"

--- When the store is open on Sundays: the same as every other day, so it calls
--- `opening_hours` instead of repeating its text.
pub sunday_hours() -> Text = opening_hours()

-- A private function: no `pub`, so only this module can call it.
cafe_hours() -> Text = "The café opens at 10:00"

--- Prints a heading and the notice under it: a function with two parameters, in the long
--- form, since its body has two steps.
pub section(heading: Text, notice: Text) -> Unit
  uses @console: Console[print]
=
  @console.print(heading)
  @console.print(notice)

--- Calls each function.
pub main() -> Unit
  uses @console: Console[print]
=
  section("Hours", notice: opening_hours())
  section("Sundays", notice: sunday_hours())
  section("Café", notice: cafe_hours())
```

`una run .` prints:

```text include="steps/12-function-forms/expected/output.txt"
Hours
Open today from 9:00 to 18:00
Sundays
Open today from 9:00 to 18:00
Café
The café opens at 10:00
```

#### The short form: a body of one line

`opening_hours` has a body of one line, written on the header's line after `=`. This is the **short form**. Una asks for it whenever a function has no `uses` line and its body is one line: `una fmt .`, which lays code out the way Una expects, writes such a function this way.

#### A body that calls another function

`sunday_hours` gives back what `opening_hours` gives back: its body is a call. On Sundays the store keeps the hours of every other day, so `sunday_hours` names that rule, and the text of the hours stays in one place.

#### Parameters, and labels at the call

`section(heading: Text, notice: Text)` takes two parameters, separated by a comma. Each is a name, `:` and a type. Inside the body, `heading` and `notice` stand for the arguments of the call.

A call with more than one argument names every argument after the first, with its parameter's name and `:`. The call `section("Hours", notice: opening_hours())` passes `"Hours"` as `heading`, since the first argument goes without its name, and the result of `opening_hours()` as `notice`. The name, the **label**, makes the call read the same a year from now, without a look at the header.

#### The long form: a body of several steps

`section` has a body of two steps, so it is written in the **long form**: the header, `=` alone on its line, then the body, indented two spaces. The steps run in order, as in `main`. A function with a `uses` line is always written in the long form.

#### A function that gives back nothing: `Unit`

`section` is called for what it does, printing two lines, not for a value, so its result type is `Unit`, as `main`'s is. A call of it stands on its own line in a body, as a step: `section("Café", notice: cafe_hours())`.

#### Public and private

`cafe_hours` has no `pub`, so it is **private**: only the module `notices` can call it. Keep a function private until another module needs it. Here a plain `--` comment says what it is; a doc comment would do too, but it matters most on a public function, whose readers see its header and not its body.

### How a call behaves

- **The arguments are worked out first.** In `section("Hours", notice: opening_hours())`, the call `opening_hours()` runs first, and its text becomes `notice`. Then the body of `section` runs.
- **The caller waits.** While `section` runs, `main` waits. When the body of `section` ends, `main` goes on with its next step.
- **A call gives back the type its header says.** `opening_hours()` is always a `Text`. Una checks the body against the header: change the body of `cafe_hours` to the number `10`, and `una check .` reports:

```text include="steps/15-wrong-result/expected/rendered.txt#L1"
[U2001] Error: `cafe_hours` returns `Text`, found `Int`
```

- **Every parameter gets an argument.** Leave out the notice, `section(opening_hours())`, and the call is short of an argument:

```text include="steps/14-missing-argument/expected/rendered.txt#L1"
[U2001] Error: `section` is missing argument `notice`
```

- **The second argument carries its label.** Leave out `notice:`, as in `section("Hours", opening_hours())`, and `una check .` reports:

```text include="steps/13-missing-label/expected/rendered.txt"
[U2004] Error: argument 2 of `section` needs a label; only the first argument may go without one
    ╭─[ src/notices.una:25:20 ]
    │
 25 │   section("Hours", opening_hours())
    │                    ───────┬───────
    │                           ╰───────── argument 2 of `section` needs a label; only the first argument may go without one
    │
    │ Help: repair 1: label it `notice`; edit src/notices.una:25:20..25:35 to "notice: opening_hours()"
    │
    │ Note: run `una explain U2004` for an explanation
────╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

The message says which argument needs a label, the second, and the `Help` line gives the exact repair: label it `notice`.

### When to write a function

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Use the same text in several places | a function that gives it back, such as `opening_hours()` |
| Give a few steps a name, and run them from several places | a function with a body of several steps, such as `section` |
| Say that one rule follows another | a function whose body calls the other, such as `sunday_hours` |
| Keep a helper to its own module | a function without `pub` |
| Start the program | `pub main() -> Unit` in the entry module |
:::

### Check yourself: functions

The help desk of a store prints this:

```una include="steps/16-order-of-calls/src/desk.una" title="src/desk.una"
module desk

--- Where customers can ask a question.
pub help_desk() -> Text = "Ask at the help desk by the main door"

--- Prints a heading and the notice under it.
pub section(heading: Text, notice: Text) -> Unit
  uses @console: Console[print]
=
  @console.print(heading)
  @console.print(notice)

--- Prints two sections, with a line of its own between them.
pub main() -> Unit
  uses @console: Console[print]
=
  section("Questions", notice: help_desk())
  @console.print("Thank you for shopping with us")
  section("Lost something?", notice: help_desk())
```

What does `una run .` print?

:::answer Show the answer
```text include="steps/16-order-of-calls/expected/output.txt"
Questions
Ask at the help desk by the main door
Thank you for shopping with us
Lost something?
Ask at the help desk by the main door
```

`main` has three steps, run in order. The first and the last call `section`, which prints its heading and then its notice, the text `help_desk()` gives back. The step between them prints its own line. The same text appears twice, written once.
:::

## 1.5 Printing: the console, `print` and `uses`

### What the console is

The **console** is the channel of text between a program and the person who runs it. In a terminal, it is the window itself: what the program prints appears there, line after line, under the command that started it. Printing is the simplest way a program shows its results.

In Una the console is a **capability**: something outside the program that a function may use, with a set of **operations**, the actions it offers. The console's capability is `Console`, and its operation `print` writes one line of text. Think of a badge that a store gives each employee, naming the doors the employee may open. A function's header shows such a badge: the `uses` line. [Chapter 12](/learn/capabilities/#s12-1) covers capabilities in full; this section covers the console.

### Why a function says that it prints

Printing changes the world outside the program: a line appears on someone's screen. A function that only gives back a text changes nothing; you may call it as often as you like. Una keeps the two apart, in the header, where a reader looks first. A function that prints says so with a `uses` line, and Una refuses a function that prints without one. So a header without `uses` promises that the function does nothing outside the program.

### How to write `uses`

A `uses` line goes under the header, indented two spaces, before `=`. Here it is on two functions:

:::steps
```una include="steps/17-printing/src/signs.una" title="src/signs.una" verified="check, run"
module signs

--- Prints a line of dashes, to separate the parts of a sign.
pub rule() -> Unit
  uses @console: Console[print]
=
  @console.print("--------------------")

--- Prints the sign of the café, between two rules.
pub main() -> Unit
  uses @console: Console[print]
=
  rule()
  @console.print("The café opens at 10:00")
  rule()
```

1. **`uses`.** The keyword that starts the line.
2. **`@console`.** The name the body uses for the console. A name that starts with `@` always stands for a capability.
3. **`: Console`.** The capability: the console.
4. **`[print]`.** The operations the function may use, in brackets: here only `print`.
5. **`@console.print("The café opens at 10:00")`.** A call of the operation: the capability's name, a dot, the operation, and its argument in parentheses. The argument is the text to print.
6. **`rule()`.** `main` calls `rule`, which prints. A function that calls a function that prints also prints, so `main` has its own `uses` line too.
:::

`una run .` prints:

```text include="steps/17-printing/expected/output.txt"
--------------------
The café opens at 10:00
--------------------
```

### Granting the console: `grants`

A `uses` line is the code asking for the console. The person who runs the program decides whether it gets it, in `una.toml`:

```toml include="steps/17-printing/una.toml" title="una.toml"
[package]
name = "signs"
version = "0.1.0"
edition = "0.2"

[run]
entry = "signs"
grants = ["console"]
```

`grants = ["console"]` lets the run use the console. So two things must agree before a line is printed: the code asks, in its headers, and the manifest allows, in `grants`. Every package in this chapter grants the console. [Chapter 12](/learn/capabilities/#s12-2) shows grants in full, and what happens when a program asks for more than its manifest grants.

### How printing behaves

- **One line per call.** Each call of `print` writes one line, and ends it, so the next call starts a new line.
- **In the order the steps run.** The lines appear in the order of the calls, as `main` and the functions it calls run them.
- **Exactly the text.** `print` writes the text as it is, spaces and every character included, such as `é`. `print("")` writes an empty line.
- **Only text.** `print` takes one value, a text. [Chapter 2](/learn/numbers/#s2-1) shows how to print a number.
- **No `uses`, no printing.** A public function that prints must have a `uses` line. Take it away from `rule`, and `una check .` reports:

```text include="steps/18-no-uses/expected/rendered.txt#L1-L6"
[U3004] Error: `@console` is used here, but this code declares no `uses`, so it is pure
   ╭─[ src/signs.una:4:22 ]
   │
 4 │ pub rule() -> Unit = @console.print("--------------------")
   │                      ────┬───
   │                          ╰───── `@console` is used here, but this code declares no `uses`, so it is pure
```

The function is **pure**: without `uses`, it may do nothing outside the program. The marks point at `@console`, the use that the header does not allow.

### When to print, and when to give back a text

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Make a text the program shows | a function without `uses` that gives back a `Text` |
| Show a line to the person running the program | `@console.print(...)` in a function with `uses @console: Console[print]` |
| Print the same few lines from several places | a function with `uses` and a `Unit` result, such as `rule` |
| Let the run print | `grants = ["console"]` in `una.toml` |
:::

A function that gives back a text can be tested on its own, as [Testing it](#s1-7) shows, so the work of a program goes into such functions, and a few functions with `uses`, `main` first, print what they give back.

### Check yourself: printing

In this version, `frame` calls `rule` twice. Does `una check .` pass?

```una include="steps/19-caller-no-uses/src/signs.una#frame" title="src/signs.una"
--- Prints a rule, twice.
pub frame() -> Unit
=
  rule()
  rule()
```

:::answer Show the answer
No:

```text include="steps/19-caller-no-uses/expected/rendered.txt#L1-L6"
[U3003] Error: `rule` uses `@console: Console[print]`, but this code declares no `uses`, so its effects would exceed its header
    ╭─[ src/signs.una:12:3 ]
    │
 12 │   rule()
    │   ───┬──
    │      ╰──── `rule` uses `@console: Console[print]`, but this code declares no `uses`, so its effects would exceed its header
```

`rule` prints, so a call of it prints too. `frame` has no `uses` line, so it may not print, and each call of `rule` in its body is a diagnostic, `U3003`. The repair is the line the `Help` gives: `uses @console: Console[print]` in the header of `frame`.
:::

## 1.6 Day-to-day: morning notices

### What the program must do

Every morning, when a store opens, a screen by the entrance shows the notices of the day, and the staff read them before the doors open. The notices are:

- the store's name and a greeting;
- one part for each subject: the hours, the shipping cutoff, the offer of the day and the café, each a heading with its notice under it;
- where customers can ask a question, at the end.

A line of dashes separates the parts, so that a reader finds each one at a glance. The texts change often: the offer every day, the hours with the seasons. So each text should be written once, in a place with a name, and the code that prints should not need to change when a text does.

The program is one module, `morning`, in a package whose `una.toml` names it as the entry and grants the console:

```toml include="day-to-day/una.toml" title="day-to-day/una.toml"
[package]
name = "morning"
version = "0.1.0"
edition = "0.2"

[run]
entry = "morning"
grants = ["console"]
```

### The notices, one function each

Each notice is a function that gives back its text:

```una include="day-to-day/src/morning.una#store_name..help_desk" title="day-to-day/src/morning.una" caption="the notices" verified="check"
--- The name of the store, the first line of the notices.
pub store_name() -> Text = "Harbor Street store"

--- The greeting under the name.
pub greeting() -> Text = "Good morning"

--- When the store is open today.
pub opening_hours() -> Text = "Open today from 9:00 to 18:00"

--- Until when an order placed today ships today.
pub shipping_cutoff() -> Text = "Orders placed before 17:00 ship today"

--- Today's offer.
pub special() -> Text = "Today's special: desk lamps"

--- When the café inside the store opens.
pub cafe_hours() -> Text = "The café opens at 10:00"

--- Where customers can ask a question.
pub help_desk() -> Text = "Questions? Ask at the help desk by the main door"
```

Each has a doc comment that says what the text is for, a name that says what it holds, and the result type `Text`. None of them has a `uses` line: each only gives back a text, and prints nothing, so each is written in the short form, on one line.

This is the part of the program that changes from day to day. When the café changes its hours, one line changes, the body of `cafe_hours`, and every place that prints the café's hours prints the new ones. Since these functions print nothing, each one can also be tested on its own, as [Testing it](#s1-7) shows.

### Printing a part: `rule` and `section`

Two private functions print. `rule` prints the line of dashes, and `section` prints a heading, its notice and a rule:

```una include="day-to-day/src/morning.una#rule..section" title="day-to-day/src/morning.una" caption="the functions that print"
--- Prints a line of dashes, which separates the parts of the notices.
rule() -> Unit
  uses @console: Console[print]
=
  @console.print("------------------------------")

--- Prints a heading and the notice under it, then a rule.
section(heading: Text, notice: Text) -> Unit
  uses @console: Console[print]
=
  @console.print(heading)
  @console.print(notice)
  rule()
```

Both have a `uses` line, since both print: `section` prints two lines itself, and a third through `rule`. A function that calls `rule` prints, so it holds the console too. Both are written in the long form, as every function with a `uses` line is, and both give back `Unit`, since they are called for the lines they print.

Both are private, with no `pub`: only this module uses them. `section` takes two parameters, the heading and the notice, so every part of the notices is printed the same way. To change the look of every part, such as a rule of stars in place of dashes, you change one function.

### `main`

`main` prints the name and the greeting, a rule, then one `section` for each subject, and the help desk last:

```una include="day-to-day/src/morning.una#main" title="day-to-day/src/morning.una" verified="check, run"
--- Prints the morning notices.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(store_name())
  @console.print(greeting())
  rule()
  section("Hours", notice: opening_hours())
  section("Shipping", notice: shipping_cutoff())
  section("Offer", notice: special())
  section("Café", notice: cafe_hours())
  @console.print(help_desk())
```

Its steps run in order, from the top. The first two print texts that functions give back; `rule()` prints the first line of dashes; each `section` prints one part. Each call of `section` labels its second argument, `notice:`, and the argument is a call: `opening_hours()` runs first, and its text becomes the notice.

`main` reads like the notices themselves: a reader sees the order of the parts without reading how a part is printed, and adds a part with one line. The texts live in the notice functions, the layout in `rule` and `section`, and the order in `main`: each kind of change has one place.

### Running it

In the `day-to-day` directory:

```sh
una check .
una run .
```

`una check .` prints nothing, and `una run .` prints the notices:

```text include="day-to-day/expected/output.txt"
Harbor Street store
Good morning
------------------------------
Hours
Open today from 9:00 to 18:00
------------------------------
Shipping
Orders placed before 17:00 ship today
------------------------------
Offer
Today's special: desk lamps
------------------------------
Café
The café opens at 10:00
------------------------------
Questions? Ask at the help desk by the main door
```

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/morning.una" title="day-to-day/src/morning.una" caption="the whole program" verified="check, run, test"
module morning

-- The notices that the console of the store prints each morning, when the store opens.

--- The name of the store, the first line of the notices.
pub store_name() -> Text = "Harbor Street store"

--- The greeting under the name.
pub greeting() -> Text = "Good morning"

--- When the store is open today.
pub opening_hours() -> Text = "Open today from 9:00 to 18:00"

--- Until when an order placed today ships today.
pub shipping_cutoff() -> Text = "Orders placed before 17:00 ship today"

--- Today's offer.
pub special() -> Text = "Today's special: desk lamps"

--- When the café inside the store opens.
pub cafe_hours() -> Text = "The café opens at 10:00"

--- Where customers can ask a question.
pub help_desk() -> Text = "Questions? Ask at the help desk by the main door"

--- Prints a line of dashes, which separates the parts of the notices.
rule() -> Unit
  uses @console: Console[print]
=
  @console.print("------------------------------")

--- Prints a heading and the notice under it, then a rule.
section(heading: Text, notice: Text) -> Unit
  uses @console: Console[print]
=
  @console.print(heading)
  @console.print(notice)
  rule()

--- Prints the morning notices.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(store_name())
  @console.print(greeting())
  rule()
  section("Hours", notice: opening_hours())
  section("Shipping", notice: shipping_cutoff())
  section("Offer", notice: special())
  section("Café", notice: cafe_hours())
  @console.print(help_desk())

example "the notices start with the store's name"
  do store_name()
  expect result == "Harbor Street store"

example "the greeting is for the morning"
  do greeting()
  expect result == "Good morning"

example "the hours give the opening and the closing time"
  do opening_hours()
  expect result == "Open today from 9:00 to 18:00"

example "the cutoff names the hour"
  do shipping_cutoff()
  expect result == "Orders placed before 17:00 ship today"

example "the offer names what is on sale"
  do special()
  expect result == "Today's special: desk lamps"

example "the café keeps its own hours"
  do cafe_hours()
  expect result == "The café opens at 10:00"

example "the help desk says where to go"
  do help_desk()
  expect result == "Questions? Ask at the help desk by the main door"
```

## 1.7 Testing it

### What an example is

An **example** is a check that lives next to the code: it calls a function and says what the call must give back. `una test .` runs every example of the package and reports each one. The morning notices have one example per notice:

```una include="day-to-day/src/morning.una#L53-L59" title="day-to-day/src/morning.una" caption="the first two examples"
example "the notices start with the store's name"
  do store_name()
  expect result == "Harbor Street store"

example "the greeting is for the morning"
  do greeting()
  expect result == "Good morning"
```

Each example has three lines:

1. **`example "…"`.** The keyword `example` and a sentence that says what the example shows. It names the example in the report.
2. **`do greeting()`.** The call to make, indented two spaces.
3. **`expect result == "Good morning"`.** What must hold afterwards: `result` stands for what the call gave back, and `==` means "is equal to".

This is the simplest form of an example. [Chapter 14](/learn/testing/#s14-1) covers examples in full.

### One example per notice

Every function that gives back a text has an example that states the exact text. An example of the whole text catches a change of one character, such as a missing space, which is easy to miss when you read the output.

### Running the examples

In the `day-to-day` directory, `una test .` checks the package first, then runs the examples:

```text include="day-to-day/expected/commands/test.txt#L2-L10"
example morning "the notices start with the store's name" ... ok
example morning "the greeting is for the morning" ... ok
example morning "the hours give the opening and the closing time" ... ok
example morning "the cutoff names the hour" ... ok
example morning "the offer names what is on sale" ... ok
example morning "the café keeps its own hours" ... ok
example morning "the help desk says where to go" ... ok

7 examples: 7 passed, 0 failed
```

Each example takes one line of the report. When an example fails, its line says `FAILED`, with the line of the `expect` and the value `result` had; the exercises of [Exercises](#s1-9) start from such a report.

### What the examples leave out: the printing functions

The examples do not call `main`, `section` or `rule`. These functions print, and an example of a function that prints needs a stand-in for the console, which [chapter 14](/learn/testing/#s14-3) shows. The printing functions here only print what the tested functions give back, so the examples cover what can go wrong: the text of each notice.

## 1.8 Common mistakes

Each mistake is a small change to `day-to-day/src/morning.una`, followed by what `una check .` reports. Read each diagnostic as [If `una check` finds a mistake](#if-una-check-finds-a-mistake) shows: the message, then the place, then the help.

### Single quotes (U0001)

:::mistake
Write a text between single quotes:

```diff include="day-to-day..mistakes/1:src/morning.una" context="1"
--- a/src/morning.una
+++ b/src/morning.una
@@ -46,3 +46,3 @@
   rule()
-  section("Hours", notice: opening_hours())
+  section('Hours', notice: opening_hours())
   section("Shipping", notice: shipping_cutoff())
```

```text include="mistakes/1/expected/rendered.txt#L1-L9"
[U0001] Error: invalid character `'`; text literals use double quotes
    ╭─[ src/morning.una:47:11 ]
    │
 47 │   section('Hours', notice: opening_hours())
    │           ┬
    │           ╰── invalid character `'`; text literals use double quotes
    │
    │ Note: run `una explain U0001` for an explanation
────╯
```

*Why:* a text in Una is written between double quotes, `"`. A single quote, `'`, is not a character the language uses outside a text, so the check stops at it, once for each quote.

*Fix:* write `"Hours"`. See [U0001](/docs/errors/U0001/).
:::

### A comment with `//` (U0101)

:::mistake
Start a comment with `//`, as some other languages do:

```diff include="day-to-day..mistakes/2:src/morning.una" context="1"
--- a/src/morning.una
+++ b/src/morning.una
@@ -2,3 +2,3 @@
 
--- The notices that the console of the store prints each morning, when the store opens.
+// The notices that the console of the store prints each morning, when the store opens.
 
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U0101] Error: unexpected `/`, expected a declaration
```

*Why:* in Una a comment starts with `--`. `//` is not a comment, so the check reads the line as code, and a module holds only declarations at that place.

*Fix:* write `--`. See [U0101](/docs/errors/U0101/).
:::

### A public function that prints without `uses` (U3004)

:::mistake
Make `rule` public and write it on one line, without its `uses` line:

```diff include="day-to-day..mistakes/3:src/morning.una" context="1"
--- a/src/morning.una
+++ b/src/morning.una
@@ -26,6 +26,3 @@
 --- Prints a line of dashes, which separates the parts of the notices.
-rule() -> Unit
-  uses @console: Console[print]
-=
-  @console.print("------------------------------")
+pub rule() -> Unit = @console.print("------------------------------")
 
```

```text include="mistakes/3/expected/rendered.txt#L1-L6"
[U3004] Error: `@console` is used here, but this code declares no `uses`, so it is pure
    ╭─[ src/morning.una:27:22 ]
    │
 27 │ pub rule() -> Unit = @console.print("------------------------------")
    │                      ────┬───
    │                          ╰───── `@console` is used here, but this code declares no `uses`, so it is pure
```

*Why:* a public function without a `uses` line is pure: it may do nothing outside the program. Printing is something outside the program.

*Fix:* give the header its `uses` line back, `uses @console: Console[print]`, with `=` and the body on lines of their own. See [U3004](/docs/errors/U3004/).
:::

### A module named unlike its file (U1008)

:::mistake
Rename the module, but not its file:

```diff include="day-to-day..mistakes/4:src/morning.una" context="1"
--- a/src/morning.una
+++ b/src/morning.una
@@ -1,2 +1,2 @@
-module morning
+module notices
 
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U1008] Error: module `notices` is in `src/morning.una`, which must hold module `morning`
```

*Why:* the file `src/morning.una` must hold the module `morning`. A second diagnostic, `U7002`, follows: `entry` in `una.toml` names a module the package no longer has.

*Fix:* write `module morning`, or rename the file and the entry with the module. See [U1008](/docs/errors/U1008/).
:::

### Indenting by four spaces (U0003)

:::mistake
Indent a step of a body by four spaces:

```diff include="day-to-day..mistakes/5:src/morning.una" context="1"
--- a/src/morning.una
+++ b/src/morning.una
@@ -35,3 +35,3 @@
 =
-  @console.print(heading)
+    @console.print(heading)
   @console.print(notice)
```

```text include="mistakes/5/expected/rendered.txt#L1-L10"
[U0003] Error: inconsistent indentation of 4 spaces; expected 0 or 2
    ╭─[ src/morning.una:36:1 ]
    │
 36 │     @console.print(heading)
    │ ──┬─
    │   ╰─── inconsistent indentation of 4 spaces; expected 0 or 2
    │
    │ Help 1: repair 1: indent with 2 spaces; edit src/morning.una:36:1..36:5 to "  "
    │
    │ Help 2: repair 2: remove the indentation; edit src/morning.una:36:1..36:5 to ""
```

*Why:* Una indents by two spaces, always. A line indented by four belongs to no level the check knows.

*Fix:* indent by two spaces, as the first repair says. See [U0003](/docs/errors/U0003/).
:::

### A second argument without its label (U2004)

:::mistake
Leave out the label of `section`'s second argument:

```diff include="day-to-day..mistakes/6:src/morning.una" context="1"
--- a/src/morning.una
+++ b/src/morning.una
@@ -46,3 +46,3 @@
   rule()
-  section("Hours", notice: opening_hours())
+  section("Hours", opening_hours())
   section("Shipping", notice: shipping_cutoff())
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U2004] Error: argument 2 of `section` needs a label; only the first argument may go without one
```

*Why:* every argument after the first carries its parameter's name, so that a call says what each value is.

*Fix:* write `notice: opening_hours()`, as the `Help` line of the diagnostic says. See [U2004](/docs/errors/U2004/).
:::

## 1.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's example added, and, when the exercise asks for a new function, a **stub** of it: its header with a body that gives back a **placeholder**, the empty text `""`. `una test .` fails there until the exercise is done. Work in this order:

1. Read the example: it says what the function must give back.
2. Change the code.
3. Run `una check .`, and fix what it reports.
4. Run `una test .` until every example passes, then `una run .` to see the notices.

### Exercise 1: the help desk moves

::::exercise
The help desk moves next to the café. The example of `help_desk` has already been changed to the new text:

```una include="exercises/1/start/src/morning.una#L77-L79" title="exercises/1/start/src/morning.una"
example "the help desk says where to go"
  do help_desk()
  expect result == "Questions? Ask at the help desk by the café"
```

Change `help_desk` so that the example passes.

:::hint
*Hint:* only the text in the body of `help_desk` changes. Copy the new text from the example, so that not one character differs.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L8-L12"
example morning "the help desk says where to go" ... FAILED
  src/morning.una:79: expect result == "Questions? Ask at the help desk by the café"
  it is false, with `result` = `"Questions? Ask at the help desk by the main door"`

7 examples: 6 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Give `help_desk` the new text:

```diff include="exercises/1/start..exercises/1/answer:src/morning.una" context="1" title="src/morning.una"
--- a/src/morning.una
+++ b/src/morning.una
@@ -23,3 +23,3 @@
 --- Where customers can ask a question.
-pub help_desk() -> Text = "Questions? Ask at the help desk by the main door"
+pub help_desk() -> Text = "Questions? Ask at the help desk by the café"
 
```

The example states the new text, the function gives it back, and `main` prints it without a change of its own.
:::
::::

### Exercise 2: a notice for returns

::::exercise
Add a part for returns. Write `returns_policy()`, which gives back `Returns are free within 30 days`, and print it in `main` under the heading `Returns`, after the café. The start package ends with:

```una include="exercises/2/start/src/morning.una#L81-L86" title="exercises/2/start/src/morning.una"
--- How long customers have to bring an item back.
pub returns_policy() -> Text = ""

example "returns are free for 30 days"
  do returns_policy()
  expect result == "Returns are free within 30 days"
```

:::hint
*Hint:* the body of `returns_policy` is its text, as for the other notices. In `main`, add one call of `section`, written as the one for the café is.
:::

Check your answer with `una test .`, then `una run .` for the new part.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Give `returns_policy` its text, and print it in `main`:

```diff include="exercises/2/start..exercises/2/answer:src/morning.una" context="1" title="src/morning.una"
--- a/src/morning.una
+++ b/src/morning.una
@@ -50,2 +50,3 @@
   section("Café", notice: cafe_hours())
+  section("Returns", notice: returns_policy())
   @console.print(help_desk())
@@ -81,3 +82,3 @@
 --- How long customers have to bring an item back.
-pub returns_policy() -> Text = ""
+pub returns_policy() -> Text = "Returns are free within 30 days"
 
```

The new part prints its heading, its notice and a rule, like every other part, since `section` does the printing.
:::
::::

### Exercise 3: Sunday hours that follow the week

::::exercise
On Sundays the store keeps the hours of every other day. Write `sunday_hours()` so that it always gives back what `opening_hours()` gives back, even after the hours change, and print it in `main` under the heading `Sundays`, after the hours. The start package ends with:

```una include="exercises/3/start/src/morning.una#L81-L86" title="exercises/3/start/src/morning.una"
--- When the store is open on Sundays: the same hours as every other day.
pub sunday_hours() -> Text = ""

example "Sundays keep the hours of every other day"
  do sunday_hours()
  expect result == opening_hours()
```

:::hint
*Hint:* the example compares with `opening_hours()`, not with a text. Copying the text into `sunday_hours` passes it today, but not after the hours change. A body may be a call of another function.
:::

Check your answer with `una test .`, then `una run .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Make the body of `sunday_hours` a call of `opening_hours`, and print it in `main`:

```diff include="exercises/3/start..exercises/3/answer:src/morning.una" context="1" title="src/morning.una"
--- a/src/morning.una
+++ b/src/morning.una
@@ -47,2 +47,3 @@
   section("Hours", notice: opening_hours())
+  section("Sundays", notice: sunday_hours())
   section("Shipping", notice: shipping_cutoff())
@@ -81,3 +82,3 @@
 --- When the store is open on Sundays: the same hours as every other day.
-pub sunday_hours() -> Text = ""
+pub sunday_hours() -> Text = opening_hours()
 
```

The hours are still written once, in `opening_hours`. When they change, the Sunday line changes with them.
:::
::::

## 1.10 Recap and reference

### For agents

:::agents
Every command takes `--json` before its name and then prints one JSON document on stdout. `una --json check .` gives each diagnostic with its `code`, `message`, `primary` span and `repairs`, and `una --json test .` gives each example with its outcome. U0003, U1001 (when it can name the operation meant), U1008, U2004 and U3003 carry exact edits, which `una fix .` applies. U0001, U0101, U2001 and U3004 depend on intent, so their repairs, when they have one, are descriptions only. The compact rule: *a package is `una.toml`, `verification.lock` and `src/<module>.una` with a matching `module` line; the entry module has `pub main() -> Unit`; a function that prints declares `uses @console: Console[print]`, and the run grants `console`.*
:::

### Recap

:::recap
- A package is `una.toml`, `verification.lock` and modules under `src/`; `una check .` checks it, and `una run .` checks it and runs it.
- The file `src/morning.una` holds the module `morning`, and its first line says `module morning`.
- A run starts at `pub main() -> Unit` of the module that `entry` names, and runs its steps in order.
- A function is a header, `=`, and a body: one line in the short form, several steps in the long form.
- Every argument after the first carries its label: `section("Hours", notice: opening_hours())`.
- A function that prints says so, `uses @console: Console[print]`, and so does every function that calls it; the run grants `console` in `una.toml`.
- Comments start with `--`; doc comments start with `---` and document the declaration under them.
- An example calls a function and states its result: `do greeting()`, then `expect result == "Good morning"`.
:::

### Reference

:::reference
- Start: [install](/docs/install/), [getting started](/docs/getting-started/)
- Construct pages: [source files, comments and literals](/docs/language/lexical-structure/), [functions](/docs/language/functions/), [`uses`](/docs/language/capabilities/uses/), [host capabilities and grants](/docs/language/capabilities/host/), [`example`](/docs/language/examples/example/)
- Configuration: [`[package] edition`](/docs/configure/package/edition/), [`[run] entry`](/docs/configure/run/entry/), [`[run] grants`](/docs/configure/run/grants/), [`verification.lock`](/docs/configure/verification-lock/)
- Commands: [`una check`](/docs/cli/check/), [`una run`](/docs/cli/run/), [`una test`](/docs/cli/test/), [`una fmt`](/docs/cli/fmt/), [`una fix`](/docs/cli/fix/), [`una explain`](/docs/cli/explain/)
- Standard library: [the host capabilities](/docs/std/) (`Console`, `print`)
- Diagnostics: [U0001](/docs/errors/U0001/), [U0003](/docs/errors/U0003/), [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/), [U1008](/docs/errors/U1008/), [U2001](/docs/errors/U2001/), [U2004](/docs/errors/U2004/), [U3003](/docs/errors/U3003/), [U3004](/docs/errors/U3004/), [U7002](/docs/errors/U7002/), [U7004](/docs/errors/U7004/)
- Specification: [lexical structure](/docs/spec/01-lexical-structure/), [functions and contracts](/docs/spec/04-functions-and-contracts/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [requirements and examples](/docs/spec/08-requirements-and-examples/), [diagnostics and the command line](/docs/spec/13-diagnostics-and-abi/)
:::
