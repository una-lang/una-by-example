---
learn: "1"
title: Hello, Una
editions: ["0.2"]
codes: [U0001, U0003, U0101, U1001, U1008, U3004, U7002]
time: 20
builds: The store's morning notices, printed on the console
prerequisites: []
template: 2
nav: ["Your first program", "Modules", "Writing a function", "Printing and uses", "Common mistakes"]
---

# 1 Hello, Una


A program is a set of instructions that a computer follows, written in a language that both you and the computer can read. This chapter is where you write your first one. It assumes no experience: every word it uses is explained the first time it appears. You start from an empty directory, write a program that prints a line, read what Una says when the program is wrong, and end with a small program a store would really use, checked, run and tested. On the way you meet the ideas every later chapter builds on: packages, modules, functions, values, types and diagnostics.

## Why it works this way

In many languages the first program is one line, and so is the first surprise. A program that only meant to write a line on the screen can also read your files or send data over the network, and nothing in its text says whether it does. A mistake, such as a number where a word should be, often shows up only when that line runs: in front of a customer, or months later.

Una moves these questions to the time before the program runs. Every word in this part is taught in this chapter, in the section named after it; read it now for the idea, and come back to it later:

:::steps
1. **One command checks everything.** Before you run a program, `una check` reads all of it and lists each mistake it finds, with the place and the reason. `una run` refuses to start a program that still has a mistake in it ([section 18.2](/learn/tools/#s18-2)).
2. **The first lines of a function say what it may do.** A function is a named piece of a program. Its first lines say whether it may print on the screen, and Una holds the rest of the function to them ([section 1.4](#s1-4)).
3. **Whoever runs the program decides what it gets.** A small file of settings next to the code says that the program may print. The code asks, the settings allow, and a reader can see both ([section 1.4](#s1-4)).
4. **Tests live next to the code.** An example runs a function and says what it must give back, and `una test` checks every example ([section 14.1](/learn/testing/#s14-1)).
:::

> [!KEY]
> In Una, the first lines of a function say what it may do outside the program. If they do not say it, Una does not let the function do it.

## 1.1 Your first program: hello world


### What a program is

A **program** is a list of instructions for a computer, such as "write this line on the screen" or "add these two prices". Think of a recipe: it names what it needs, then gives the steps in order, and anyone who follows it gets the same dish. A computer follows a program the same way, one step after another, exactly as written.

You write a program as text, in a file, in a **programming language**: a small language with strict rules, so that each line has one meaning. That text is the **source code**, or just the code. This book teaches the language Una.

A few more words come up on every page:

- **Running** a program means having the computer follow its instructions.
- A **value** is one piece of data the program works with: the number `18`, the text `"The store is open"`. [Section 2.1](/learn/numbers/#s2-1) covers values.
- The **console** is the window of text where you type commands and where a program writes its lines. [Section 1.4](#s1-4) covers it.
- `una` is the tool that reads Una code. It **checks** the code, which means it looks for mistakes without running it, and it **runs** the code when the check passes.

### What you need: a terminal, `una` and Z3

Una runs on macOS, on Macs with Apple silicon, and on Linux, on x86-64 and ARM computers: those are the systems each release of `una` is built for.

You work with `una` in a **terminal**: the program that shows the console on your screen. To open one:

- on macOS, open the Terminal app, in Applications > Utilities, or find it by typing "Terminal" in Spotlight, which [[Cmd]]+[[Space]] opens;
- on Linux, open the Terminal app from your applications menu; on many systems [[Ctrl]]+[[Alt]]+[[T]] opens one.

In the terminal you type a **command**, a line that names a program and what it should do, and press [[Enter]]; the program runs and prints its answer under the command.

Next, install `una` and the solver it uses, Z3: a program that `una check` asks to prove facts about your code, from [chapter 2](/learn/numbers/) on. The [install page](/docs/install/) installs both, at the versions that go together, and sets up your terminal so that typing `una` runs it from any directory.

To see that it worked, type `una --version` and press [[Enter]]. It prints the version of `una`, the editions it supports and the version of Z3 it expects. Then run `z3 --version`, which must report that same version. The programs of this chapter need no proof, so they run without Z3, but from [chapter 2](/learn/numbers/) on, `una check` cannot prove anything without it.

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
- `[run]` says how `una run` starts the program. `entry` names the module, the file of code, that holds `main`, the function the program starts with; [The first module](#the-first-module-hello) explains both. `grants` lists what the program may use outside itself when it runs: here, the console. [Section 1.4](#s1-4) explains grants.

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
2. **`--- Says that the store is open.`** A **doc comment**: a note for people, which the computer does not run. It belongs to the declaration under it. [Section 1.3](#s1-3) covers comments.
3. **`pub main() -> Unit`.** The function's **header**, its first line. `pub` makes it **public**, so that `una run` can reach it. `main` is its name, and `()` says it takes no inputs. `-> Unit` says what it gives back when it ends: `Unit` means nothing useful, since `main` is run for what it does, not for a value.
4. **`uses @console: Console[print]`.** What the function may do outside the program: call the operation `print` of `Console`, the console, through the name `@console`. [Section 1.4](#s1-4) explains this line.
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

## 1.2 Modules

### Two kinds of comment

A **comment** is a note for people, which the program ignores. Una has two kinds:

- `--` starts a **comment**, which runs to the end of its line. It is for the reader of the code.
- `---` starts a **doc comment**, which belongs to the declaration under it. It is part of that declaration's documentation, and tools print it with the declaration's header. Every public function should have one.

Una has no block comments: a comment of several lines repeats `--` or `---` on each, as the doc comment of `discounted` does.

## 1.3 Writing a function


### What a function is

A program of one `main` grows long quickly. A **function** gives a piece of the work a name, so that you write it once and use it wherever it is needed. Think of a price lookup at a till: you give it a SKU, and it gives back the price. You do not need to know how it finds the price; you only need its name, what to give it, and what it gives back.

A function's inputs are its **parameters**, and what it gives back is its **result**. Using a function is a **call**: you write its name and the values it should work with, the **arguments**, in parentheses. The code that makes the call is the **caller**, and the call stands for the result.

### Why programs use functions

Here is a program that prints when orders ship at three stores, each line written out in full:

```una include="steps/04-repeated/src/cutoffs.una" title="steps/04-repeated/src/cutoffs.una" verified="check, run"
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
```una include="steps/05-functions/src/notice.una#cutoff_line" title="src/notice.una"
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
```una include="steps/05-functions/src/notice.una" title="src/notice.una" verified="check, run"
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

Its package is a directory `notice/`, made as in [Opening hours](/learn/numbers/#opening-hours), and its manifest names the module `notice`:

```toml include="steps/05-functions/una.toml" title="una.toml"
[package]
name = "notice"
version = "0.1.0"
edition = "0.2"

[run]
entry = "notice"
grants = ["console"]
```

`una run .` prints:

```text include="steps/05-functions/expected/output.txt"
Orders placed before 18:00 ship today
```

### The forms of a function

The module `shipping` has one function of each form. `main` calls each one:

```una include="steps/06-function-forms/src/shipping.una" title="steps/06-function-forms/src/shipping.una" verified="check, run"
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

`cutoff(store: Text, hour: Int)` takes two parameters, separated by a comma. A call with more than one argument names every argument after the first, with the name of its parameter and `:`: `cutoff("Downtown", hour: hour)`, `line_cents(2, cents: 1990)`. The first argument may go without its name. Every other one carries it, or is a name equal to the parameter's, as `hour` could be here ([chapter 6](/learn/functions/) shows that short form), so a call reads the same a year from now, without a look at the header.

#### The long form: a body of several lines

`discounted` has a body of two lines, so it is written in the **long form**: the header, `=` alone on its line, then the body, indented two spaces. A body's lines run in order, and the value of its last line is the result: here `quantity * each`. Una has no `return`; the last line is the result.

#### Public and private

`welcome` has no `pub`, so it is **private**: only the module `shipping` can call it. Keep a function private until another module needs it. Here a plain `--` comment says what it is; a doc comment would do too, but it matters most on a public function, whose readers see its header and not its body.

#### A function that prints

`announce` prints, so its header says so, with a `uses` line, as `main`'s does. It returns `Unit`, since it is called for what it does, and `main` calls it as a step of its own: `announce("Airport", hour: 20)`. A function can call a function that uses the console only when it holds the console too, as `main` does.

`una run .` prints:

```text include="steps/06-function-forms/expected/output.txt#L1-L5"
Downtown: orders placed before 18:00 ship today
3980 cents
3580 cents
Welcome to the Harbor store
Airport: orders placed before 20:00 ship today
```

### When to write a function

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Name a value that one body computes once | `let` |
| Use the same computation in several places | a function |
| Test a computation on its own | a function without `uses`, and an example ([section 14.1](/learn/testing/#s14-1)) |
| Print, or reach anything else outside the program | a function with a `uses` line, usually `main` |
| Keep a helper to one module | a function without `pub` |
:::

### Check yourself: functions

`main` of `shipping` ends with two more calls:

```una include="steps/06-function-forms/src/shipping.una#discounted" title="steps/06-function-forms/src/shipping.una"
--- What a line costs when each unit is `off` cents cheaper: the long form, with a body of
--- several lines.
pub discounted(quantity: Int, cents: Int, off: Int) -> Int
=
  let each = cents - off
  quantity * each
```

What do `discounted(3, cents: 500, off: 50)` and `cutoff("Harbor", hour: hour - 1)`, with `hour` holding 18, give? The last two lines of `main` print them.

:::answer Show the answer
```text include="steps/06-function-forms/expected/output.txt#L6-L7"
1350 cents
Harbor: orders placed before 17:00 ship today
```

In `discounted`, `each` is 500 − 50, 450, and the result is 3 × 450, 1350. In `cutoff`, the argument `hour - 1` is computed first, 17, and the body puts it in the line.
:::

## 1.4 Printing: the console, `print` and `uses`


### What the console is

The **console** is the channel of text between a program and the person who runs it. In a terminal, it is the window itself: what the program prints appears there, line after line, under the command that started it. Printing is the simplest way a program shows its results.

In Una the console is a **capability**: a named set of **operations**, actions on the world outside the program. `Console` has one operation, `print`, which writes one line of text and ends it with a new line. Other capabilities reach a clock, files or the network. Think of a badge that a store gives each employee: it names the doors the employee may open. A capability is such a badge, and a function shows its badges in its header.

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

```una include="steps/07-notices/src/notices.una" title="steps/07-notices/src/notices.una" verified="check, run"
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

```text include="steps/07-notices/expected/output.txt"
Good morning

Fresh stock: desk lamps and wool rugs
The café opens at 10:00
```

The name is a choice, but most code uses `@console`, so that every reader recognizes it. `Console[print]` and `Console` grant the same thing today, since `print` is the console's only operation. Listing the operations is the habit to keep: for a capability with many operations, a header that lists the few it needs says more.

### How printing behaves

- Each `print` writes one line, and the lines appear in the order the steps run.
- `print` adds the end of the line itself. `print("")` writes an empty line.
- A text may hold any printable character, `é` included, in any language.
- `print` takes one value, and it must be a text. [Section 2.1](/learn/numbers/#s2-1) shows how to print a number.
- A step that prints stands on its own line. Una does not let a call that prints hide inside another computation, so a reader who scans the left edge of a body sees every effect it has, in the order it has them.

### Check yourself: printing

Two questions, without code.

1. A package's `una.toml` has `grants = []`, and its `main` has `uses @console: Console[print]`. Does `una check .` pass? Does `una run .` start?
2. A module has a public function `slip_title` with no `uses` line. Can its body call `@console.print`?

:::answer Show the answer
1. `una check .` passes: the code asks for the console in its header, and that is all a check needs. `una run .` refuses to start, with U3012, since the run grants nothing that `main` uses.
2. No. A public function without `uses` is pure, and `@console` in its body is U3004, as in [Why a function must ask for the console](/learn/capabilities/#why-a-function-must-ask-for-the-console).
:::

## 1.5 Common mistakes

### Single quotes (U0001)

:::mistake
Write a text between single quotes, as many languages allow:

```diff include="steps/08-packing-slip..mistakes/1:src/slip.una" context="1"
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

```diff include="steps/08-packing-slip..mistakes/2:src/slip.una" context="1"
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

```diff include="steps/08-packing-slip..mistakes/3:src/slip.una" context="1"
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

```diff include="steps/08-packing-slip..mistakes/4:src/slip.una" context="1"
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

### Indenting by four spaces (U0003)

:::mistake
Indent the first line of the body of `main` by four spaces, a habit from other languages:

```diff include="steps/08-packing-slip..mistakes/5:src/slip.una" context="1"
--- a/src/slip.una
+++ b/src/slip.una
@@ -30,3 +30,3 @@
 =
-  let lamps = 2
+    let lamps = 2
   let rugs = 1
```

```text include="mistakes/5/expected/rendered.txt#L1,L8,L10"
[U0003] Error: inconsistent indentation of 4 spaces; expected 0 or 2
    │ Help 1: repair 1: indent with 2 spaces; edit src/slip.una:31:1..31:5 to "  "
    │ Help 2: repair 2: remove the indentation; edit src/slip.una:31:1..31:5 to ""
```

*Why:* in Una, indentation is part of the syntax: it says which lines belong to which body. Each level is exactly two spaces deeper than the one around it. The body of `main` is one level deep, so its lines start with two spaces. The message gives the two depths that would be valid, 0 and 2, and each `Help` line offers one.

*Fix:* two spaces. The first repair is an exact edit, and `una fix .` applies it. Indent with spaces only: a tab in the indentation is an error too. See [U0003](/docs/errors/U0003/).
:::
