---
learn: "1"
title: Hello, Una
editions: ["0.2"]
codes: [U0001, U0003, U0101, U1001, U1008, U2001, U3004, U7002]
time: 30
builds: A packing slip that a store prints for the box of one order, with examples that test each line
prerequisites: []
template: 2
---

# 1 Hello, Una

Every program starts the same way: a directory, a manifest, a first module, and a command that tells you whether the code is right before it runs. In Una that command is `una check`, and it does more than in most languages. It checks types, proves the program's contracts with a solver, and reads each function's header to see what the function may do outside the program, such as printing. This chapter starts from an empty directory and ends with a small program a store would really use, checked, run and tested.

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
- say in a function's header that it prints, and grant that to the program;
- write functions with doc comments, and test them with examples.
:::

## Why it works this way

In many languages the first program is one line, and so is the first surprise. A script that only meant to print can also read files, open network connections or change environment variables, and nothing in its text says whether it does. Mistakes in types often show up only when the line runs, in front of a customer, or not at all until a rare input reaches them.

Una moves these questions to the moment you check the code:

:::steps
1. **One command checks everything.** `una check` reads the whole package and reports the problems it finds, each with a code, a place and a message, before anything runs. `una run` refuses to start a package that does not check.
2. **A header says what a function may do.** `uses @console: Console[print]` in the header of `main` says that `main` may print on the console, and nothing else. A public function whose header has no `uses` cannot print at all. A private one may leave the line out, and the checker works it out and shows it, as [chapter 3](/learn/functions/) explains.
3. **The run says what the program gets.** `una.toml` grants the console to the program, and `una run` can grant more with a `--grant` flag. The code asks for an authority, and the run gives it: both are written down, and a reviewer can read both.
4. **Tests live next to the code.** An `example` calls a function and states what it returns, and `una test` runs every example.
:::

> [!KEY]
> In Una, what a public function may do is part of its header. If the header does not say it, the checker does not let the body do it.

## 1.1 A first package

To follow this chapter you need `una` and the solver it uses, Z3. The [install page](/docs/install/) installs both, at the versions that go together, and says how to put `una` on your path. Run `una --version` to see that it works: it prints the version of `una`, the editions it supports and the version of Z3 it expects. Then run `z3 --version`, which must report that same version. The programs of this chapter need no proof, so they run without Z3, but from [chapter 2](/learn/values/) on, `una check` cannot prove anything without it.

A Una program is a **package**: a directory with a manifest, `una.toml`, a lock file, `verification.lock`, and the code under `src/`. Make the directory and its `src/` from an empty directory:

```sh
mkdir store
cd store
mkdir src
```

The manifest names the package and its **edition**, the version of the language its code is written in. This tutorial uses edition `0.2`. The `[run]` table says which module `una run` starts, and what the program may do when it runs:

```toml include="steps/01-hello/una.toml" title="una.toml"
[package]
name = "hello"
version = "0.1.0"
edition = "0.2"

[run]
entry = "hello"
grants = ["console"]
```

`verification.lock` pins the solver that proves the package's contracts: which solver, its exact version, the logic it works in, and how much work it may spend on each proof. With the lock, a proof that passes on your machine passes on every other one. The file is the same in every package of this tutorial. Write it with these six lines, which are the "fixed example" of the code U7004, the diagnostic for a missing or broken lock:

```text include="steps/01-hello/expected/commands/explain-u7004.txt#L32-L37"
encoding_version = "una-smt-1"
solver           = "z3"
solver_version   = "5.1.0"
logic            = "QF_UFLIA"
step_budget      = 5000000
random_seed      = 0
```

`una explain U7004` prints these lines too, under "Fixed example", so you can copy the lock from your terminal at any time. Take that one: the lock it shows first, under "Failing example", is the broken one.

Now the code. A source file holds one **module**, and its name is the name of the file: `src/hello.una` holds the module `hello`.

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
2. **`--- Says that the store is open.`** A doc comment, which belongs to the declaration below it. [Section 1.4](#s1-4) covers comments.
3. **`pub main() -> Unit`.** The function `una run` starts. `pub` makes it public, `()` says it takes no parameters, and `-> Unit` says that it returns no useful value: `Unit` has one value only, so a function that returns it is run for what it does.
4. **`uses @console: Console[print]`.** The function's one authority: it may call the operation `print` of the capability `Console`, through the name `@console`.
5. **`=`, then the body.** The body is indented by two spaces. Its one line prints a line of text.
:::

In the `store` directory, check the package, then run it:

```sh
una check .
una run .
```

`una check .` prints nothing when the package is right, and its exit code is 0. `una run .` checks again, then runs `main`:

```text include="steps/01-hello/expected/output.txt"
The store is open
```

> [!NOTE]
> The `.` in `una check .` is the package's directory. Every command of this tutorial runs in a package's directory and names it as `.`.

## 1.2 Reading a diagnostic

A mistake is the normal state of code being written, so what `una check` says about one matters as much as what it accepts. Change `print` to `write`, which `Console` does not have:

```diff include="steps/01-hello..steps/02-typo:src/hello.una" title="src/hello.una"
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

```text include="steps/02-typo/expected/rendered.txt"
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

Each diagnostic has the same parts, in the same order:

:::steps
1. **`[U1001] Error:`** The code, which names the kind of problem. Every code has a page on this site, such as [U1001](/docs/errors/U1001/), and `una explain U1001` prints the same text in your terminal.
2. **The message.** One sentence that says what is wrong: here, that `Console` has no operation `write`.
3. **`src/hello.una:7:12`.** The file, line and column. The excerpt below it marks the exact span.
4. **`Help` and `Note` lines.** A `Help` line proposes a repair when there is one. Some repairs are exact edits, which `una fix .` applies for you; a `Note` adds what you need to understand the problem.
:::

`una check .` exits with code 1 when it reports a problem, so a script or an editor can tell success from failure without reading the text. It reports all the problems it finds in one pass, not only the first, so one run often shows several of them.

`una run .` never runs a package that does not check. It prints the same diagnostics and stops, so a program that runs is always a program that checked.

| Command | What it does | Prints when all is well |
| --- | --- | --- |
| `una check .` | Checks types, authority and proofs, and that the code is in canonical form | nothing |
| `una run .` | Checks, then runs `main` of the `[run] entry` module | what the program prints |
| `una test .` | Checks, then runs every example | one line per example, then a count |
| `una fmt .` | Rewrites the code in canonical form | nothing |
| `una fix .` | Applies the exact repairs that diagnostics carry, then formats | what it fixed |
| `una explain U1001` | Explains a code, with a failing and a fixed example | the explanation |

**Canonical form** is the one layout Una accepts for any code: indentation, spaces, line breaks and the order of a few parts. `una check .` reports code that differs from it, and `una fmt .` rewrites the code into it, so no review ever argues about layout.

## 1.3 Printing and the console

A program talks to the world only through **capabilities**: named sets of operations, such as `Console` with its operation `print`, that a function must ask for in its header. The host, the program that runs yours, provides a few of them: the console, the clock, files and others. Every one must be asked for in the code, and granted when the program runs: in `[run] grants` of `una.toml`, or by a `--grant` flag of `una run`.

Each section from here on has a program of its own, and each program is a package of its own. Make a directory next to `store`, such as `opening/`, with its `src/`, copy `verification.lock` into it, and write the manifest and the module shown. This program prints the store's opening hours:

:::steps
```una include="steps/03-printing/src/opening.una" title="src/opening.una" verified="check, run"
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

1. **`let opens = 9`.** `let` gives a name to a value. The name holds that one value from then on. [Chapter 2, Values](/learn/values/), covers names and values in full.
2. **`let hours = closes - opens`.** A computed value. `Int`, the type of `9` and `18`, is a whole number.
3. **`"Open today from {opens}:00 to {closes}:00"`.** A text with **interpolations**: a name in braces puts its value into the text. Most values can go in braces: numbers, texts, `true` and `false`, and the lists of [chapter 5](/learn/collections/).
4. **Three `print` calls.** Each prints one line, in order.
:::

Its manifest names the package and its module `opening`, and grants the console, as the first package's did:

```toml include="steps/03-printing/una.toml" title="una.toml"
[package]
name = "opening"
version = "0.1.0"
edition = "0.2"

[run]
entry = "opening"
grants = ["console"]
```

`una run .` prints:

```text include="steps/03-printing/expected/output.txt"
Open today from 9:00 to 18:00
That is 9 hours of trading
Orders placed before 18:00 ship today
```

The two halves work together. The `uses` line of `main` is a promise to callers and reviewers: this function prints, and does nothing else outside the program. The `grants` line of `una.toml` is the decision of whoever runs the program, and so is a `--grant` flag of `una run`, which adds to it for one run. If you remove `console` from the grants, `una check .` still passes, since the code is right, but `una run .` refuses to start: it reports U3012, "`main` uses `print` of `Console`, which neither `[run] grants` nor a `--grant` flag grants".

`print` takes a `Text` and nothing else. To print a number, put it in a text with braces, as `"{hours} hours"` does. [Common mistakes](#s1-8) shows what the checker says when you pass the number itself.

> [!TIP]
> `{` in a text starts an interpolation, and a lone `}` is an error. To print a brace itself, write `\{` or `\}`.

## 1.4 Functions and comments

A program of one `main` grows long quickly. A **function** gives a piece of the work a name, takes values as **parameters**, and returns a **result**. Its header states all three, with their types, and `una check` holds every call to them. [Chapter 3, Functions](/learn/functions/), covers functions in depth; this section gives you enough to write and test small ones.

Comments explain what the code does not say. Una has two kinds:

- `--` starts a **comment**, which runs to the end of its line. It is for the reader of the code.
- `---` starts a **doc comment**, which belongs to the declaration below it. It is part of that declaration's documentation, and tools print it with the declaration's header. Every public function should have one.

:::steps
```una include="steps/04-functions/src/notice.una" title="src/notice.una" verified="check, run"
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

1. **`pub closing_hour() -> Int = 18`.** A function of no parameters that returns an `Int`. A function with no clauses whose body is one line is written on one line, after `=`. This is its **short form**.
2. **`pub cutoff_line(hour: Int) -> Text`.** One parameter, `hour`, of type `Int`, and a `Text` result. The body is a text that puts `hour` in its place.
3. **`let hour = closing_hour()`.** A call. The parentheses are needed even when there are no arguments.
4. **`cutoff_line(hour)`.** A call with one argument. The value of `hour` becomes the parameter `hour` inside the function.
5. **`-- Ask for the hour, then build the line from it.`** A plain comment, inside a body.
:::

Its package is a directory `notice/`, made as in [section 1.3](#s1-3), and its manifest names the module `notice`:

```toml include="steps/04-functions/una.toml" title="una.toml"
[package]
name = "notice"
version = "0.1.0"
edition = "0.2"

[run]
entry = "notice"
grants = ["console"]
```

`una run .` prints:

```text include="steps/04-functions/expected/output.txt"
Orders placed before 18:00 ship today
```

`closing_hour` and `cutoff_line` are public and have no `uses` line, so neither can print, read a file or ask the clock. They take values and return a value, and that is all they can do. This is why `main` builds the line with `cutoff_line` and prints it itself: the one function that prints is the one that says so.

Tools read doc comments too. `una contract` prints the full header of a function, with its doc comment, named by module and function:

```sh
una contract notice.cutoff_line
```

```text include="steps/04-functions/expected/commands/contract.txt#L2-L3"
--- The line that tells customers until when an order ships the same day.
pub cutoff_line(hour: Int) -> Text
```

This is what a reviewer, an editor or an agent sees of the function without reading its body. Una has no block comments: a comment of several lines repeats `--` or `---` on each.

## 1.5 Examples and `una test`

A function that returns a value is easy to test: call it, and compare what it returns with what you expect. In Una such a test is an **example**, written in the module, next to the code it tests:

:::steps
```una include="steps/05-examples/src/notice.una#L19-L25" title="src/notice.una" caption="two examples at the end of the module"
example "the store closes at six in the evening"
  do closing_hour()
  expect result == 18

example "the cutoff line names the hour"
  do cutoff_line(18)
  expect result == "Orders placed before 18:00 ship today"
```

1. **`example "the store closes at six in the evening"`.** An example has a name in quotes. Write it as the fact the example checks, since that is what `una test` reports.
2. **`do closing_hour()`.** The call under test, on its own line.
3. **`expect result == 18`.** A fact that must hold. `result` is the value the `do` call returned, and `==` compares two values.
:::

Run every example of the package:

```sh
una test .
```

```text include="steps/05-examples/expected/commands/test.txt#L2-L5"
example notice "the store closes at six in the evening" ... ok
example notice "the cutoff line names the hour" ... ok

2 examples: 2 passed, 0 failed
```

Each example gets a line, with `ok` when every `expect` holds. When one does not, the example fails, and the report says which line and what the value was. Here the second example expects a different wording than the function gives:

```diff include="steps/05-examples..steps/06-failing:src/notice.una" title="src/notice.una" context="1"
--- a/src/notice.una
+++ b/src/notice.una
@@ -24,2 +24,2 @@
   do cutoff_line(18)
-  expect result == "Orders placed before 18:00 ship today"
+  expect result == "Orders placed before 18:00 ship the same day"
```

```text include="steps/06-failing/expected/commands/test.txt#L2-L7"
example notice "the store closes at six in the evening" ... ok
example notice "the cutoff line names the hour" ... FAILED
  src/notice.una:25: expect result == "Orders placed before 18:00 ship the same day"
  it is false, with `result` = `"Orders placed before 18:00 ship today"`

2 examples: 1 passed, 1 failed
```

The report gives the line of the `expect` that did not hold, `src/notice.una:25`, and the value of `result`. `una test .` exits with code 1, so a script can stop on a failed test. Whether the function or the example is wrong is your call: here the function says what the store means, so the fix is to the example.

Examples are code, and `una check .` checks them as it checks the rest of the module. An `expect` that compares an `Int` result with a text, such as `expect result == "18"`, is a type error at check time, not a failed test at run time. An example may call any function of its module, public or private, and it never prints: `una run .` ignores the examples, and `una test .` runs nothing but them.

A good example states one fact, in its name and in its `expect` lines. When it fails, its name tells you what broke before you read any code. Prefer exact values over loose ones: `expect result == "Orders placed before 18:00 ship today"` catches a change of one word, which a test of the length alone would miss.

> [!NOTE]
> `una test .` checks the package first, as `una run .` does. An example runs only in a package that checks clean.

## 1.6 Day-to-day: a packing slip

A packing slip goes into every box the store ships. It names the order and the customer, lists each line of the order with its quantity, counts the units, and gives the total paid. The warehouse prints it as the box is packed.

The design follows from the job. Each line of the slip comes from its own function, which takes the values the line shows and returns its text. Those functions have no `uses` line, so they cannot print, and an example can test each one by its result. `main` holds the sample order's values, calls the functions, and prints what they return, line by line. The program is one module, `slip`, in a package of its own: make a directory `day-to-day/` with its `src/`, copy `verification.lock` into it, and write this manifest, which grants the console:

```toml include="day-to-day/una.toml" title="day-to-day/una.toml"
[package]
name = "slip"
version = "0.1.0"
edition = "0.2"

[run]
entry = "slip"
grants = ["console"]
```

**The lines of the slip.** Seven functions, each with a doc comment, each written in the short form, on one line:

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

A few things are new here. `ship_to` and `item` take two and three parameters, separated by commas. `line_cents` multiplies two `Int` values with `*`. `item` starts with two spaces, inside the text, so that the item lines stand out on paper. The angle brackets in `ship_to` and the `x` in `item` are plain characters of the text. Only braces are special.

Money is in **cents**, as an `Int`: 1990 is 19 units and 90 cents. Whole cents never round, so the total is exact. [Chapter 2](/learn/values/) shows how to print them as an amount with two decimals.

**Printing the slip.** `main` names the quantities and computes the cost of each line, then prints the slip one line at a time:

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

The order of declarations in a module is free: `main` calls functions declared above it here, but it could come first. Canonical form does not reorder declarations, so keep them in the order a reader needs: the parts first, and `main`, which puts them together, after them.

The calls with more than one argument name every argument after the first: `line_cents(lamps, cents: 1990)`, `item(lamps, sku: "LAMP-01", name: "Desk lamp, brass")`. The first argument may go without its name. Every other one carries the name of its parameter, so a call reads the same a year from now, without a look at the header. The checker holds you to it, and [chapter 3](/learn/functions/) explains the rule.

Each `@console.print` call is a line of its own. In Una, a call that prints, or does anything else outside the program, is always a statement of its own, or the whole value of a `let`, never hidden inside another expression. A reader who scans the left edge of `main` sees every effect it has, in the order it has them.

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

Why so many small functions for a program this size? Each one is a line of the slip that someone may want to change: the wording of the closing line, the layout of an item, the email address. A change to one of them touches one line of code and one example, and the header of each tells you, without a look at its body, that it only computes a text or a number. The same program written as one `main` of seven prints, with every text in place, would be shorter, and nothing in it could be tested without reading what it prints.

In the package's directory, `una run .` prints the slip shown under "What you'll build": the order and the customer, two item lines, three units in two lines, and a total of 8480 cents, which is 2 times 1990 plus 4500.

> [!SECURITY]
> The slip's functions have no `uses` line, so the checker proves they cannot print, read files or reach the network. Only `main` touches the console, and only because its header says so and the run grants it, here through `una.toml`. When this program grows, a new effect in any function shows up in that function's header, where a reviewer sees it.

## 1.7 Testing it

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

Two of them check more than the sample shows. "a line of zero units costs nothing" covers a case the sample order never reaches. "an item line is indented and starts with the quantity" pins the two leading spaces, which are easy to lose in an edit and hard to see in the output. An example that states the whole expected text catches a change of one character.

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

Each example takes one line of the report, so when one fails, the report names the line of the slip that changed. Tools read the same results as JSON with `una --json test .`, one entry for each example with its outcome.

The examples do not test `main`, and they do not need to. `main` only names values and prints what the functions return, and the functions are what the examples cover. This is the shape most Una programs take: a thin `main` with the effects, and pure functions, with no `uses` line, that hold the logic and the tests. [Chapter 10, Testing](/learn/testing/), shows how to test functions that do have effects, with fakes that stand in for the console and other capabilities.

## 1.8 Common mistakes

Each mistake below is a small change to `day-to-day/src/slip.una`, followed by what `una check .` reports.

:::mistake
**1. Single quotes (U0001).** Writing a text between single quotes, as many languages allow:

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

*Why:* a text in Una is written between double quotes only. A single quote is not a character Una code may contain outside a text or a comment, so each of the two is reported.

*Fix:* `"Desk lamp, brass"`. See [U0001](/docs/errors/U0001/).
:::

:::mistake
**2. A comment with `//` (U0101).** Starting the comment at the top of the module the way C, Java or TypeScript do:

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

*Why:* a comment in Una starts with `--`, and a doc comment with `---`. `/` is division, and a module cannot start a declaration with it.

*Fix:* `-- A packing slip: …`. See [U0101](/docs/errors/U0101/).
:::

:::mistake
**3. Printing without `uses` (U3004).** Removing the `uses` line from `main`:

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

*Why:* a public function without `uses` is pure: it cannot use any capability. una reports U3004 once for each of the seven `@console` lines, since each is a separate use.

*Fix:* put the line back: `uses @console: Console[print]`. The `Help` line of the diagnostic says the same, and warns that the repair widens what the function may do. See [U3004](/docs/errors/U3004/).
:::

:::mistake
**4. A module named unlike its file (U1008).** Renaming the module in its first line, but not the file:

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

*Why:* `src/slip.una` must hold the module `slip`. una also reports U7002, since the manifest's `entry = "slip"` now names a module that does not exist.

*Fix:* keep the names in step: the file, the `module` line and the `entry` of `una.toml`. `una fix .` applies the edit of the `Help` line. See [U1008](/docs/errors/U1008/).
:::

:::mistake
**5. Printing a number (U2001).** Printing the total itself, instead of the line that holds it:

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

*Why:* `print` takes a `Text`, and `lamp_cents + rug_cents` is an `Int`. Una converts no value to another type unless the code says so.

*Fix:* put the number in a text, `"{lamp_cents + rug_cents}"`, or call `total_line`, which does. See [U2001](/docs/errors/U2001/).
:::

:::mistake
**6. Indenting by four spaces (U0003).** Indenting the first line of the body of `main` by four spaces, a habit from other languages:

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

*Why:* each level of indentation is exactly two spaces deeper than the one around it. The body of `main` is one level deep, so its lines start with two spaces.

*Fix:* two spaces. The first repair is an exact edit, and `una fix .` applies it. Indent with spaces only: a tab in the indentation is an error too. See [U0003](/docs/errors/U0003/).
:::

## 1.9 For agents

:::agents
Every command takes `--json` before its name and then prints one JSON document on stdout. `una --json check .` gives each diagnostic with its `code`, `message`, `primary` span and `repairs`, and `una --json test .` gives each example with its outcome. The diagnostics of this chapter are of two kinds. U0003 and U1008 carry exact edits, which `una fix .` applies. U0001, U0101, U2001 and U3004 depend on intent, so their repairs, when they have one, are descriptions only. The compact rule: *a package is `una.toml`, `verification.lock` and `src/<module>.una` with a matching `module` line; a function that prints declares `uses @console: Console[print]`, and the run grants `console`, in `una.toml` or with `--grant`.*
:::

## 1.10 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added at the end, and a stub of each function to write, which returns a placeholder value. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one line on the header line.

::::exercise
**Exercise 1: the weight of the parcel.** The warehouse wants the weight on the slip, in kilograms and grams. Write `weight_line(grams)`, which turns 2350 into `Parcel weight: 2 kg 350 g`. The start package ends with:

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
*Hint:* `/` divides two `Int` values and drops the remainder, and `mod` gives the remainder: `2350 / 1000` is 2, and `2350 mod 1000` is 350. Both can go inside the braces of a text.
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

::::exercise
**Exercise 2: shipping and the amount to pay.** The slip should also show the shipping charge, 450 cents for this order, and what the customer pays in all. Write `to_pay(goods, shipping)` and `pay_line(cents)`, and print two new lines after the total: `Shipping: 450 cents` and `To pay: 8930 cents`. The start package ends with:

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
*Hint:* in `main`, give the sum of the two lines a name with `let`, so that both `total_line` and `to_pay` can use it.
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

::::exercise
**Exercise 3: amounts with two decimals.** Customers read `84.80` more easily than `8480 cents`. Write `amount(cents)`, which writes an amount of cents with two decimals, and use it in `total_line`, so that the slip says `Total paid: 84.80`. Watch the cents under ten: 1205 is `12.05`, not `12.5`. The start package ends with:

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
*Hint:* write the whole units, a point, and then the two digits of the cents one by one: the tens of cents and the cents left over. Each is a `/` or a `mod` of `cents`, or both.
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

## 1.11 Recap

:::recap
- A package is a directory with `una.toml`, `verification.lock` and its modules under `src/`. The file `src/slip.una` holds the module `slip`.
- `una check .` reports every problem with a code, a place and a message, and prints nothing when all is well. `una run .` and `una test .` check first.
- `una explain` prints what a code means; `una fmt .` writes canonical form.
- A function that prints says so in its header, `uses @console: Console[print]`, and the run grants `console`. A public function without `uses` cannot print.
- `print` takes a `Text`. Put any value into a text with braces, `"{units} units"`.
- Comments start with `--`, and doc comments with `---`. A doc comment belongs to the declaration below it, and `una contract` prints it.
- Keep the logic in functions without `uses`, and test each one with an `example`: `do` a call, `expect` a fact about `result`.
:::

## 1.12 Reference

:::reference
- Start: [install](/docs/install/), [getting started](/docs/getting-started/), [canonical form and `una fmt`](/docs/language/canonical-form/)
- Construct pages: [source files, comments and literals](/docs/language/lexical-structure/), [functions](/docs/language/functions/), [`uses`](/docs/language/capabilities/uses/), [host capabilities and grants](/docs/language/capabilities/host/), [`example`](/docs/language/examples/example/)
- Configuration: [`[package] edition`](/docs/configure/package/edition/), [`[run] entry`](/docs/configure/run/entry/), [`[run] grants`](/docs/configure/run/grants/), [`verification.lock`](/docs/configure/verification-lock/)
- Commands: [`una check`](/docs/cli/check/), [`una run`](/docs/cli/run/), [`una test`](/docs/cli/test/), [`una fmt`](/docs/cli/fmt/), [`una fix`](/docs/cli/fix/), [`una explain`](/docs/cli/explain/), [`una contract`](/docs/cli/contract/)
- Standard library: [the host capabilities](/docs/std/) (`Console`, `print`)
- Diagnostics: [U0001](/docs/errors/U0001/), [U0003](/docs/errors/U0003/), [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1008](/docs/errors/U1008/), [U2001](/docs/errors/U2001/), [U3004](/docs/errors/U3004/), [U3012](/docs/errors/U3012/), [U7002](/docs/errors/U7002/), [U7004](/docs/errors/U7004/)
- Specification: [lexical structure](/docs/spec/01-lexical-structure/), [functions and contracts](/docs/spec/04-functions-and-contracts/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [requirements and examples](/docs/spec/08-requirements-and-examples/), [diagnostics and the command line](/docs/spec/13-diagnostics-and-abi/), [the standard library](/docs/spec/14-standard-library/), [canonical form](/docs/spec/15-canonical-form/)
:::
