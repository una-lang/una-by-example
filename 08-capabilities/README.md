---
learn: "8"
title: Capabilities
editions: ["0.2"]
codes: [U1001, U3001, U3002, U3004, U3005, U3010, U3011, U3012, U3014, U3020, U5001]
time: 55
builds: A shipping-notice service that looks customers up and emails them, tested with fake services
prerequisites: ["3", "4", "6"]
template: 2
nav: ["uses", "Host capabilities and grants", "Your capabilities and handlers", "with, rebinding and narrowing", "Conditions and boundaries (0.3)", "Day-to-day: shipping notices", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 8 Capabilities

A service that sends shipping notices talks to a customer directory, a mail server and a log. In most languages any function can open a connection, read a file or print, so you learn what a function touches only by reading its body and every body it calls. In Una a function can only compute unless its `uses`, written or inferred, say otherwise. Every effect outside the program goes through a capability that the header names and that the caller hands over. This chapter shows how to use the host's capabilities, how to declare your own with handlers, how to pass and narrow authority, and how to test the whole service with fake handlers.

## What you'll build

:::build
A dispatch step for a small store. For each order that has left the warehouse, it looks the customer up in a directory service, emails them a shipping notice through a mail service, and writes one line to a log. A customer who is unknown, who asked for no notices, or whose mail cannot be sent is skipped with a reason:

```text include="day-to-day/expected/output.txt"
sent     A-1001 to rosa@example.invalid
sent     A-1002 to tomas@example.invalid
skipped  A-1003: no customer has the id C-99
skipped  A-1004: customer C-21 asked for no notices
skipped  A-1005: the mail service did not answer; retry later
```

You will learn to:

- read a header's `uses` clauses as the complete list of what a function may do;
- grant the host's capabilities to a program in `una.toml`, and nothing more;
- declare a capability with `capability` and `op`, and give it code with `handler`;
- pass, rebind and narrow authority with `with`;
- test every path of a service with fake handlers installed by `given`.
:::

## Why it works this way

In a language with ambient authority, any line of any library can reach the network, the file system or the clock. That is convenient until you review a change: a new dependency, or a helper three calls deep, can start sending data somewhere, and nothing in the signatures shows it. Tests have the same problem. A function that reaches for a global client is hard to run against a fake.

Una has no ambient authority. Three rules replace it:

:::steps
1. **A capability is the only way out of the program.** Printing, reading a file, asking the time or calling a service are operations on a capability, written `@name.operation(...)`.
2. **A header lists the capabilities a function uses.** `uses @mailer: Mailer[send]` names a binding, `@mailer`, its capability, `Mailer`, and the operations allowed, `send`. A function's effects, including those of every function it calls, stay within its `uses`.
3. **Authority moves only downward, by name.** A caller hands its bindings to a callee, under the callee's names, with `with`. A capability reference is not a value: it cannot be stored, returned or passed as an ordinary argument.
:::

The cost is a line in the header for each capability. In return, a reviewer reads what a function may do from its header, the checker holds every body to it, and a test replaces any service by installing another handler.

> [!KEY]
> A function's `uses`, written or inferred, are the complete list of what it may do outside the program. A `pub` function writes them all, and one with no `uses` is pure: it can only compute its result. The host's capabilities reach `main` only as `una run` grants them: in `[run] grants` of `una.toml`, or with a `--grant` flag.

## 8.1 Declaring what a function may do: `uses`

### What an effect is

Most of what a program does happens inside it: adding prices, building a line of text, choosing a branch. Some of what it does reaches outside: it prints a line on the screen, writes a file, asks the clock for the time, or sends a message to another computer. Each of these is an **effect**: something the program does to, or learns from, the world outside it. A function with no effects can only compute its result. Call it twice with the same arguments and it gives the same answer, and nothing else in the world changes.

Una treats effects as authority that must be handed out, the way a store hands out keys. A cashier's keycard opens the till and the front door, and not the stockroom or the office safe. Anyone can read on the card what it opens, and nobody gets in anywhere without one. A few words name the parts, and this chapter uses them throughout:

- A **capability** is the authority to do one kind of thing outside the program, such as printing to the console or reading the clock. `Console` and `Clock` are capabilities.
- An **operation** is one thing a capability can do: `print` is an operation of `Console`, and `now` is an operation of `Clock`.
- A **binding** is the name a function uses for a capability it holds. It always starts with `@`, as in `@console`. You perform an operation on a binding: `@console.print("…")`.
- A **`uses` clause** is a line of a function's header that names a binding, its capability, and the operations the function may perform with it: `uses @console: Console[print]`.

The `uses` clauses of a header are the function's keycard: the complete list of what it may do outside the program.

### Each step is a package

Each step of this chapter is a package, as in [chapter 1](/learn/hello/#s1-1): `una.toml`, `verification.lock` (copy it from chapter 1, or take the step, whole, from the chapter's download, `08-capabilities.tar.gz`) and the module under `src/`. The manifest of a step that prints grants the console, which is what lets `main` print; [section 8.2](#s8-2) explains grants:

```toml include="steps/01-hidden-effect/una.toml" title="steps/01-hidden-effect/una.toml"
[package]
name = "slips"
version = "0.1.0"
edition = "0.2"

[run]
entry = "slips"
grants = ["console"]
```

In the package's directory, `una check .` checks the step and `una run .` runs it:

```sh
una check .
una run .
```

### Why a header lists effects

In most languages any function may print, write a file or open a network connection, and nothing in its header says so. To learn what a function does outside the program, you read its body, and the body of every function it calls, and theirs. A helper that only formats a line today can start sending data somewhere tomorrow, and the change shows nowhere but in that one body.

Here is that change in Una. `slip_line` builds one line of a packing slip, and its header promises a text and nothing else. Someone adds a line that prints, to see what the function is doing:

```una include="steps/01-hidden-effect/src/slips.una" title="steps/01-hidden-effect/src/slips.una"
module slips

--- One line of a packing slip. Its header promises a text, and nothing else.
pub slip_line(sku: Text, quantity: Int) -> Text
=
  @console.print("building the line for {sku}")
  "{quantity} x {sku}"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(slip_line("LAMP-01", quantity: 2))
```

`una check .` refuses it:

```text include="steps/01-hidden-effect/expected/rendered.txt"
[U3004] Error: `@console` is used here, but this code declares no `uses`, so it is pure
   ╭─[ src/slips.una:6:3 ]
   │
 6 │   @console.print("building the line for {sku}")
   │   ────┬───
   │       ╰───── `@console` is used here, but this code declares no `uses`, so it is pure
   │
   │ Help: repair 1 (widens authority: the function then holds this authority, and every caller must hold it too: check that the operation belongs to this function's job): declare `uses @console: ...` in the header, with the capability and the operations used
   │
   │ Note: run `una explain U3004` for an explanation
───╯
```

Read the diagnostic from the top. The code is U3004, and the message names the binding, `@console`, and the reason: the function "declares no `uses`, so it is pure". The mark points at `@console` in the body. The help line is the repair: declare a `uses` line in the header. It is marked "widens authority", because the repair gives the function more power, and every caller must then hold that power too. Whether the function should print is a decision for its author, so the checker does not make it.

So a header that says nothing about effects is a promise: the function has none. A header that lists `uses @console: Console[print]` is a promise too: the function may print, and do nothing else outside the program. The checker holds every body to its header, so a reviewer learns what a function may do from the header alone.

### How to write `uses`

#### The parts of a `uses` line

A `uses` clause sits under the header, with the other clauses, before `=`. Take `uses @files: Files[read, write]`:

1. **`uses`** starts the clause.
2. **`@files`** is the binding: the name the body uses for the capability. You choose it. `@files` is the usual name for `Files`, and a name such as `@audit` can say what a capability is for.
3. **`: Files`** is the capability.
4. **`[read, write]`** lists the operations the function may perform, separated by commas.

A function written in the long form ([chapter 3](/learn/functions/#s3-2)) has its clauses on their own lines, each indented two spaces. When a function has several kinds of clause, they go in this order: `requires`, `ensures`, `uses`, `fails`, then `derived from`.

The step of this part shows every form. It is a small back room of a store: it announces restocked items, and it saves a count to a file:

```toml include="steps/02-uses-forms/una.toml" title="steps/02-uses-forms/una.toml"
[package]
name = "backroom"
version = "0.1.0"
edition = "0.2"

[run]
entry = "backroom"
grants = ["console", "files:src:read,write"]
```

#### No `uses`: a pure function

A function without `uses` is **pure**: it can only compute its result.

```una include="steps/02-uses-forms/src/backroom.una#shelf_tag" title="steps/02-uses-forms/src/backroom.una"
--- No `uses`: a pure function. It can only compute its result.
shelf_tag(sku: Text) -> Text = "[{sku}]"
```

#### One operation

The brackets hold one operation. `announce` may print, and nothing else:

```una include="steps/02-uses-forms/src/backroom.una#announce" title="steps/02-uses-forms/src/backroom.una"
--- One operation of one capability: it may print, and nothing else.
announce(sku: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("restocked {shelf_tag(sku)}")
```

`@console.print(…)` performs the operation on the binding. A call of a pure function, `shelf_tag(sku)`, may stand inside its arguments.

#### Several operations of one capability

List them in one pair of brackets. `copy_count` reads a file and writes another, so it needs both operations of `Files`:

```una include="steps/02-uses-forms/src/backroom.una#copy_count" title="steps/02-uses-forms/src/backroom.una"
--- Two operations of one capability, in one pair of brackets.
copy_count(source: Text, to: Text) -> Unit
  uses @files: Files[read, write]
  fails FileError
=
  let count = @files.read(source)
    if error pass
  @files.write(to, content: count)
    if error pass
```

Both operations of `Files` can fail, with `FileError`, so `copy_count` declares `fails FileError` and passes each failure on with `if error pass`, as [chapter 6](/learn/failure/) shows.

#### Every operation: no brackets

Without brackets, the function may perform every operation of the capability, including any the capability gains later:

```una include="steps/02-uses-forms/src/backroom.una#announce_all" title="steps/02-uses-forms/src/backroom.una"
--- No brackets: every operation of the capability, now and later.
announce_all(skus: List[Text]) -> Unit
  uses @console: Console
=
  for sku in skus
    @console.print("restocked {shelf_tag(sku)}")
```

`Console` has one operation today, `print`, so `Console` and `Console[print]` allow the same thing now. They differ when the capability grows: the first header would allow the new operation at once, and the second would not.

#### Several capabilities

Write one `uses` line per binding. `save_and_say` writes a file and prints:

```una include="steps/02-uses-forms/src/backroom.una#save_and_say" title="steps/02-uses-forms/src/backroom.una"
--- Two capabilities, one `uses` line each.
save_and_say(sku: Text, units: Int) -> Unit
  uses @files: Files[write]
  uses @console: Console[print]
  fails FileError
=
  @files.write("count.txt", content: "{sku},{units}")
    if error pass
  @console.print("saved the count of {sku}")
```

#### No `uses` on a private function: inferred

A function without `pub` is **private**: only its own module can call it. A private function may leave its `uses` out, and una infers them: the fewest that cover its body and the functions it calls. [How `uses` behaves](#how-uses-behaves) shows it on a packing slip.

#### Running the forms

`main` holds `@console` and `@files`, and calls each function:

```una include="steps/02-uses-forms/src/backroom.una#main" title="steps/02-uses-forms/src/backroom.una"
pub main() -> Unit
  uses @console: Console[print]
  uses @files: Files[read, write]
=
  announce("LAMP-01")
  announce_all(["DESK-02", "RUG-07"])
  save_and_say("LAMP-01", units: 4)
    if error use unit
  copy_count("count.txt", to: "count-copy.txt")
    if error use unit
  @console.print("copied the count")
  close_shelf("RUG-07", units: 9)
    if error use unit
```

`una run .` prints:

```text include="steps/02-uses-forms/expected/output.txt"
restocked [LAMP-01]
restocked [DESK-02]
restocked [RUG-07]
saved the count of LAMP-01
copied the count
restocked [RUG-07]
saved the count of RUG-07
```

The count and its copy land in `src/count.txt` and `src/count-copy.txt`. `main` passes each failure of a file to `if error use unit`, which goes on as if the line had done nothing: a back room that cannot save a count still announces its stock.

### A packing slip

Now the clauses at work on a packing slip. A packing slip has a title and one line per item. Building a line is pure computation. Printing it is an effect, and the header says so:

:::steps
```una include="steps/03-uses/src/slips.una" title="steps/03-uses/src/slips.una" verified="check, run"
module slips

--- One line of a packing slip. Pure: it has no `uses`, so all it can do is compute a value.
slip_line(sku: Text, quantity: Int) -> Text = "{quantity} x {sku}"

--- Prints one line of a packing slip. It may print, and nothing else.
print_line(sku: Text, quantity: Int) -> Unit
  uses @console: Console[print]
=
  @console.print(slip_line(sku, quantity: quantity))

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("Packing slip for order A-1001")
  print_line("LAMP-01", quantity: 2)
  print_line("DESK-02", quantity: 1)
```

1. **`slip_line(sku: Text, quantity: Int) -> Text`.** No `uses`, so the body may not perform any operation. It builds a text and returns it.
2. **`uses @console: Console[print]`.** This line gives `print_line` a binding named `@console`, of the host capability `Console`, with the one operation `print`.
3. **`@console.print(slip_line(sku, quantity: quantity))`.** The operation, with the pure function's result as its argument.
4. **`print_line("LAMP-01", quantity: 2)` in `main`.** `main` holds `@console`, and `print_line` needs `@console`, so the call passes it on by name. Nothing else is written at the call.
:::

`una run .` prints:

```text include="steps/03-uses/expected/output.txt"
Packing slip for order A-1001
2 x LAMP-01
1 x DESK-02
```

### How `uses` behaves

#### Bindings are found by name

A call hands the callee the bindings its header asks for, by name, never by type. If `print_line` asked for `@out: Console[print]`, the call in `main` would not check: `main` holds a `@console`, not an `@out`. [Section 8.4](#s8-4) shows how to hand a binding over under another name, and [forgetting to hand over a binding](#forgetting-to-hand-over-a-binding-u3001) shows the diagnostic, U3001.

#### A caller holds at least what its callees use

A caller must hold every binding its callees need, with at least the operations they list. `main` may call `print_line` because it holds `@console` with `print`. A function that holds `Customers[find]` cannot call one that needs `Customers[forget]`: that is U3002, which [using an operation the header does not list](#using-an-operation-the-header-does-not-list-u3002) shows. So the effects of a function include the effects of every function it calls, and its header covers them all.

#### Private functions infer their `uses`

`print_line` is private, so its `uses` line can be left out. Remove it, and `una contract` prints the header una infers:

```diff include="steps/03-uses..steps/04-inferred:src/slips.una" context="1" title="src/slips.una"
--- a/src/slips.una
+++ b/src/slips.una
@@ -6,6 +6,3 @@
 --- Prints one line of a packing slip. It may print, and nothing else.
-print_line(sku: Text, quantity: Int) -> Unit
-  uses @console: Console[print]
-=
-  @console.print(slip_line(sku, quantity: quantity))
+print_line(sku: Text, quantity: Int) -> Unit = @console.print(slip_line(sku, quantity: quantity))
 
```

```text include="steps/04-inferred/expected/commands/contract.txt"
$ una contract slips.print_line
--- Prints one line of a packing slip. It may print, and nothing else.
print_line(sku: Text, quantity: Int) -> Unit
  uses @console: Console[print] -- inferred
```

The `-- inferred` comment marks what una added. Inference finds the fewest `uses` that cover the body and its callees, and an inferred function may do exactly that much. A private function that writes at least one `uses` line has exactly the ones it writes.

#### A `pub` function declares every `uses`

A `pub` function is the module's reviewed boundary: other modules call it, and its header is what they read. It must declare every `uses` itself, and one with no `uses` is pure, as [Why a header lists effects](#why-a-header-lists-effects) showed. Write `uses` on a private function too whenever its effects are part of what a reader should know.

### How many operations to allow

:::decide
**Which to use:**

| You want… | Write |
| --- | --- |
| A function that only computes | No `uses` |
| One operation of a capability | `uses @x: C[op]` |
| Several operations | `uses @x: C[op1, op2]` |
| Every operation, now and when the capability gains more | `uses @x: C`, without brackets |
| A private helper whose effects are obvious from its callers | No `uses` line; let una infer it |
:::

List the operations you need. A header with brackets also tells the reader what the function does not do, and it keeps saying so when the capability gains an operation.

### Check yourself: `uses`

`close_shelf`, in the back room's step, writes no `uses` and is private. It calls `announce`, then `save_and_say`:

```una include="steps/02-uses-forms/src/backroom.una#close_shelf" title="steps/02-uses-forms/src/backroom.una"
--- Closes a shelf for the night. It writes no `uses`, so una infers them.
close_shelf(sku: Text, units: Int) -> Unit
=
  announce(sku)
  save_and_say(sku, units: units)
    if error pass
```

Which `uses` and which `fails` does una infer for it?

:::answer Show the answer
The union of what its callees need: `@console` with `print`, which both callees use, and `@files` with `write`, from `save_and_say`. `save_and_say` can fail with `FileError`, and `if error pass` passes that failure on, so `fails FileError` is inferred too:

```text include="steps/02-uses-forms/expected/commands/contract.txt"
$ una contract backroom.close_shelf
--- Closes a shelf for the night. It writes no `uses`, so una infers them.
close_shelf(sku: Text, units: Int) -> Unit
  uses @console: Console[print] -- inferred
  uses @files: Files[write] -- inferred
  fails FileError -- inferred
```

`read` is not in the list: no callee of `close_shelf` reads a file.
:::

A second one: which functions of the back room could a test call with no fake at all?

:::answer Show the answer
Only `shelf_tag`. It has no `uses`, so it touches nothing outside the program, and a test can call it and compare the text it returns. Every other function performs an operation, and an example must give each binding it needs a stand-in, as [section 8.7](#s8-7) shows.
:::

## 8.2 The host's capabilities and grants

### What the host is

The **host** is what runs your program: the una runtime on your computer or a server. It is the only part of the system that can really print, read a file or ask the time, so the capabilities for these things come from it. They are the **host capabilities**:

| Capability | Operations | What it does |
| --- | --- | --- |
| `Console` | `print(line: Text) -> Unit` | writes a line to the screen |
| `Clock` | `now() -> Int` | gives the milliseconds since the Unix epoch, 1 January 1970 |
| `Env` | `get(name: Text)` | reads an environment variable of the process |
| `Files` | `read(path: Text)`, `write(path: Text, content: Text)` | reads and writes files, and can fail with `FileError` |
| `Keys` | `hmac(key_name: Text, data: Text)` | computes a keyed hash with a secret key that never enters the program |
| `Http` | requests over the network (edition `0.2`) | talks to web services |

They are in scope in every module, with no `import`. But a function can hold one only if its caller hands it over, and the first caller of all is `main`. `main` gets its host capabilities from `una run`, and only those that the package **grants**: a grant is the permission, written down, for the program to use a host capability when it runs.

### Why a program needs grants

You run programs you did not write: a tool from a colleague, a package from the internet, an example from a book. Its header says what it may do, but the header is part of the program, written by its author. A grant is written by the person who runs it.

Here is a stock export whose `main` writes a file. Its manifest grants only the console:

```toml include="steps/05-ungranted/una.toml" title="steps/05-ungranted/una.toml"
[package]
name = "export"
version = "0.1.0"
edition = "0.2"

[run]
entry = "export"
grants = ["console"]
```

```una include="steps/05-ungranted/src/export.una" title="steps/05-ungranted/src/export.una"
module export

--- Writes the end-of-day stock export. The manifest grants only the console.
pub main() -> Unit
  uses @console: Console[print]
  uses @files: Files[write]
=
  let outcome = attempt @files.write("stock-export.csv", content: "LAMP-01,4\n")
  @console.print("export: {outcome}")
```

`una check .` refuses it before anything runs:

```text include="steps/05-ungranted/expected/rendered.txt"
[U3012] Error: `main` uses `write` of `Files`, which `[run] grants` does not grant
   ╭─[ src/export.una:6:3 ]
   │
 6 │   uses @files: Files[write]
   │   ────────────┬────────────
   │               ╰────────────── `main` uses `write` of `Files`, which `[run] grants` does not grant
   │
   │ Help: repair 1 (widens grant: the program then gets this host authority when it runs): grant `write` of `Files` in `[run] grants` of `una.toml`, or with `--grant`
   │
   │ Note: run `una explain U3012` for an explanation
───╯
```

The message is U3012: `main` uses `write` of `Files`, "which `[run] grants` does not grant". The mark points at the `uses` line of `main`. The help line offers a repair that "widens grant": add the grant to `una.toml`. The person who owns the package decides whether to, and the decision shows in review, as a changed line of the manifest.

### How to write grants

#### `[run] grants` in `una.toml`

The grants are a list of texts under `[run]`, next to `entry`, which names the module whose `main` runs:

```toml include="steps/06-host/una.toml" title="steps/06-host/una.toml"
[package]
name = "export"
version = "0.1.0"
edition = "0.2"

[run]
entry = "export"
grants = ["console", "clock", "files:src:write"]
```

Each text grants one host capability:

| Grant | What `main` may use |
| --- | --- |
| `"console"` | `Console` |
| `"clock"` | `Clock` |
| `"files:src:read"` | `Files[read]`, inside the directory `src` |
| `"files:src:write"` | `Files[write]`, inside `src` |
| `"files:src:read,write"` | both operations, inside `src` |
| `"files:src/exports:write"` | `Files[write]`, inside `src/exports` only |

A `Files` grant always carries a directory and a mode, so it says where the program may read or write, and which of the two.

#### `--grant` on the command line

`una run` also takes grants as flags, one per capability, such as `--grant clock`. They count for that run only, and nothing records them. Prefer the manifest: it is reviewed with the code.

#### The host capabilities in `main`

`main` declares what it uses, as any function does, and the grants must cover it. The step of this section writes an end-of-day stock export, stamped with the time, so it needs three grants, as its manifest shows.

### An end-of-day stock export

The module reads the clock, writes the export, and reports the outcome:

:::steps
```una include="steps/06-host/src/export.una" title="steps/06-host/src/export.una" verified="check, run"
module export

--- The stock to export, one `SKU,units` line each.
stock_lines() -> List[Text] = ["LAMP-01,4", "DESK-02,1", "CHAIR-09,0"]

--- Writes the end-of-day stock export, stamped with the time it was taken.
pub main() -> Unit
  uses @console: Console[print]
  uses @clock: Clock[now]
  uses @files: Files[write]
=
  let taken = @clock.now()
  let body = stock_lines().join(separator: "\n")
  let content = "taken at {taken}\n{body}\n"
  let outcome = attempt @files.write("stock-export.csv", content: content)
  when outcome
    is Ok -> @console.print("export written: {stock_lines().len} lines")
    is Err(failure) -> @console.print("export failed: {failure}")
```

1. **Three `uses` lines on `main`.** Each names one host capability and the operations it needs. `main` may write files, but not read them.
2. **`@clock.now()`.** `Clock.now` gives the milliseconds since the Unix epoch, as an `Int`. Each call is an effect, so it goes on its own line.
3. **`attempt @files.write("stock-export.csv", content: content)`.** `Files.write` can fail with `FileError` (`NotFound`, `Denied` or `Io`). `attempt` keeps the outcome, as in [chapter 6](/learn/failure/), and the `when` reports either case.
4. **`"files:src:write"`.** The path `stock-export.csv` resolves inside `src/`, the directory of the grant.
:::

`una run .` prints:

```text include="steps/06-host/expected/output.txt"
export written: 3 lines
```

and leaves the export in `src/stock-export.csv`. The time in it changes on every run, so the program does not print it.

### How grants behave

#### What `una check` and `una run` compare

When `una.toml` lists `[run] grants`, `una check` compares them with the `uses` of `main`: a host operation that the grants do not cover is U3012, as [Why a program needs grants](#why-a-program-needs-grants) showed.

`una run` grants the union of `[run] grants` and its `--grant` flags, for that run only, and it checks the `uses` of `main` against that union before anything runs: a host operation that neither grants is U3012 there too. `una check` takes no `--grant` flag, so it reads only the manifest. A package whose manifest lacks `"clock"` therefore fails `una check`, yet `una run . --grant clock` runs it. What a run may do is the manifest plus the command line, so read both.

#### Paths stay inside the grant

A `Files` grant fixes a directory when the program starts, and every path the program passes is read from that directory. A path that tries to leave it does not reach the file: the operation fails with `Denied`. The step tries four paths against a grant of `src/`:

```una include="steps/07-outside-grant/src/export.una#try_write" title="steps/07-outside-grant/src/export.una"
--- Writes one line to `path`, and says what happened.
try_write(path: Text) -> Text
  uses @files: Files[write]
=
  let outcome = attempt @files.write(path, content: "LAMP-01,4\n")
  when outcome
    is Ok -> "{path}: written"
    is Err(failure) -> "{path}: {failure}"
```

```text include="steps/07-outside-grant/expected/output.txt#L1-L3"
stock-export.csv: written
../stock-export.csv: Denied
/tmp/stock-export.csv: Denied
```

- **`stock-export.csv`** is inside `src/`, and is written.
- **`../stock-export.csv`** climbs out with `..`, so it is `Denied`.
- **`/tmp/stock-export.csv`** is an absolute path, a path from the root of the disk, so it is `Denied` too.

`Denied` is a failure like any other, so the program handles it and goes on. The grant, not the program, decides where its files may be.

#### Labels on what a program reads

> [!NOTE] What a program reads from files and the environment is labeled.
> `Files.read` returns `internal Text`, and `Env.get` returns `internal` values too. `Clock.now` returns a public `Int`. A label says how sensitive data is, and the console accepts only `public` data. So the program can write what it read to a file, as the back room of [section 8.1](#s8-1) does, but cannot print it without a declared policy. [Chapter 9, Information flow](/learn/information-flow/), explains labels and how to release data legitimately.

### Which grant to give

:::decide
**Which to use:**

| The program… | Grant |
| --- | --- |
| Prints | `"console"` |
| Reads the time | `"clock"` |
| Reads its input files | `"files:<dir>:read"`, on the directory that holds them |
| Writes its output | `"files:<dir>:write"`, on a directory of its own |
| Needs a capability for one run only, such as a test of a new feature | `--grant` on that run |
:::

Grant the least that works: the narrowest directory, and only the modes the program uses. A grant that is not there cannot be misused.

### Check yourself: grants

The step of [Paths stay inside the grant](#paths-stay-inside-the-grant) tries a fourth path, `reports/../stock-export.csv`. It contains `..`. What does it print for it?

:::answer Show the answer
```text include="steps/07-outside-grant/expected/output.txt#L4"
reports/../stock-export.csv: written
```

The path goes into `reports` and back out, so it ends inside `src/`: it names the same file as `stock-export.csv`, and the write is allowed. Only a `..` that leaves the granted directory is `Denied`.
:::

A package grants `["console", "files:src:read"]`. Its `main` declares `uses @console: Console[print]` and `uses @files: Files[write]`. Does `una check .` pass?

:::answer Show the answer
No. The grant covers reading files, not writing them, so `una check .` reports U3012 at the `uses @files` line of `main`, as in [Why a program needs grants](#why-a-program-needs-grants). Either grant `"files:src:write"` or `"files:src:read,write"`, or remove the write from `main`.
:::

## 8.3 Your own capabilities and handlers

### What a capability you declare is

The host capabilities cover the machine: the screen, the clock, the files. A store's program also talks to services of its own: a mail service, a payment provider, a customer directory, a scale at the packing desk. In Una each of these is a capability that you declare, and it comes in two parts:

- A **`capability` declaration** lists what the service can do: its operations, each with the types it takes and gives back, and how it can fail. It holds no code.
- A **`handler`** gives those operations their code: one way to provide the service. A capability can have many handlers, such as one that talks to the real service, one that prints what it would send, and one that always fails, for tests.

Think of a job description and the people who fill it. The description of a cashier lists the duties: take payment, give change, print a receipt. Any trained person can do the job, and the store can put a trainee on the till for practice without changing the description. The `capability` is the description; each `handler` is a person who can do the job. The code that needs the service names the description in its `uses`, and its caller chooses who does the work, with `with`.

### Why declare a capability

Here is a receipt sender written before the store had a mail service. It prints each message on the console:

```una include="steps/08-mail-by-console/src/receipts.una" title="steps/08-mail-by-console/src/receipts.una" verified="check, run"
module receipts

--- Emails the receipt of an order. For now it prints the message, since the store has no mail
--- service yet.
send_receipt(to: Text, order: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("to {to}: Receipt for order {order}")

pub main() -> Unit
  uses @console: Console[print]
=
  send_receipt("rosa@example.invalid", order: "A-1001")
```

```text include="steps/08-mail-by-console/expected/output.txt"
to rosa@example.invalid: Receipt for order A-1001
```

It runs, but it is fragile in three ways:

1. **The header says the wrong thing.** `uses @console: Console[print]` tells a reviewer that `send_receipt` prints. It does not say that it sends mail, which is its job.
2. **Changing the service means changing the code.** When the store gets a real mail service, the body of `send_receipt` changes, and so does the header of every function that calls it, since they must now hold whatever the new service needs.
3. **The failures have nowhere to go.** A mail service can refuse an address or not answer. Printing never fails, so the header has no `fails` clause, and no caller is ready for a failure.

A capability fixes all three. `uses @mailer: Mailer[send]` says what the function does. The handler can change without touching `send_receipt` or its callers. And the operation's `fails` clause tells every caller how mail can fail.

### How to write a capability

#### The capability and its operations

A capability is the word `capability`, a name, and one operation per line under it, indented two spaces. An operation is `op`, a name, typed parameters and a result type, like a function header with no body:

```una include="steps/10-handlers/src/receipts.una#MailError..Mailer" title="steps/10-handlers/src/receipts.una"
--- How the mail service can fail.
kind MailError = Bounced(address: Text) | Timeout

--- The mail service: what it can do, with no code.
capability Mailer
  op send(to: Text, subject: Text) -> Unit
    fails MailError
```

#### An operation that can fail: `fails`

A clause under an operation, indented two spaces more, says how it can fail. `fails MailError` works exactly as on a function ([chapter 6](/learn/failure/)): a caller handles the failure or passes it on.

#### An operation with a contract: `requires` and `ensures`

An operation can carry the contracts of [chapter 7](/learn/contracts/). The scale at the packing desk takes a SKU of at least four characters, and promises a weight of at least 1 gram:

```una include="steps/09-scale/src/scales.una#ScaleError..Scale" title="steps/09-scale/src/scales.una"
--- How the scale can fail.
kind ScaleError = | NotOnScale

--- The scale at the packing desk. The clauses of `weigh` are its contract: a caller passes a
--- SKU of at least four characters, and gets a weight of at least 1 gram back.
capability Scale
  op weigh(sku: Text) -> Int
    requires sku.len >= 4
    ensures result >= 1
    fails ScaleError
```

`requires` is what every caller must prove at the call. `ensures` is what every caller may rely on. For a service outside the program, an `ensures` is an assumption: una checks every handler written in Una against it, and trusts the real service to keep it.

#### What an operation accepts: `accepts`

A fourth clause, `accepts`, states the most sensitive data the operation may receive. [Chapter 9](/learn/information-flow/) explains it.

#### A capability for other modules: `pub capability`

Like a function or a kind, a capability can be used outside its module only when it is declared `pub`: `pub capability Mailer`. The day-to-day program of [section 8.6](#s8-6) declares its services `pub`.

### How to write a handler

#### The handler and its operations

A handler is the word `handler`, a name, parameters in parentheses, `for` and the capability it implements. Under it, one `op` line per operation of the capability, each with the operation's name, its parameter names, `=` and the body:

```una include="steps/09-scale/src/scales.una#fixed" title="steps/09-scale/src/scales.una"
--- A scale on a developer's machine: it weighs every item at the same weight.
handler fixed(grams: Int) for Scale
  op weigh(sku) = if grams < 1 then fail NotOnScale else grams
```

The operation's parameters take their names only: their types and the result type come from the capability. The body is ordinary Una code. Here it fails with a variant of the operation's error kind when the fixed weight makes no sense, and returns the weight otherwise.

#### Handler parameters

`fixed(grams: Int)` has a parameter, as a function does. Its value is given when the handler is installed, and every operation of the handler can read it: `weigh` returns `grams`. A handler with no parameters is written with empty parentheses, as `bouncing()`.

#### A handler with capabilities of its own

A handler may declare `uses` lines, under its first line. A mail service for a developer's machine prints each message, so it holds the console:

```una include="steps/10-handlers/src/receipts.una#printed" title="steps/10-handlers/src/receipts.una"
--- A mail service for a developer's machine: it prints each message instead of sending it.
handler printed(prefix: Text) for Mailer
  uses @console: Console[print]
  op send(to, subject) = @console.print("{prefix} to {to}: {subject}")
```

The code that installs the handler must hold those capabilities.

#### Installing a handler: `with`

A handler runs only where it is installed. `with @scale = fixed(850)`, at the end of a statement, installs the handler for the call in that statement:

```una include="steps/09-scale/src/scales.una#parcel_grams..main" title="steps/09-scale/src/scales.una"
--- A parcel's weight in grams: the item, and a box of 150 grams.
parcel_grams(sku: Text) -> Int
  requires sku.len >= 4
  ensures result >= 151
  uses @scale: Scale[weigh]
  fails ScaleError
=
  let grams = @scale.weigh(sku)
    if error pass
  grams + 150

--- A scale on a developer's machine: it weighs every item at the same weight.
handler fixed(grams: Int) for Scale
  op weigh(sku) = if grams < 1 then fail NotOnScale else grams

pub main() -> Unit
  uses @console: Console[print]
=
  let weighed = attempt parcel_grams("LAMP-01") with @scale = fixed(850)
  @console.print("{weighed}")
  let empty = attempt parcel_grams("LAMP-01") with @scale = fixed(0)
  @console.print("{empty}")
```

`parcel_grams` holds `@scale: Scale[weigh]`. It never learns which handler answers; `main` chooses. An example installs a handler with a `given` line instead, as [section 8.7](#s8-7) shows. The step prints:

```text include="steps/09-scale/expected/output.txt#L1"
Ok(1000)
```

The weight is the item's 850 grams and the box's 150. `parcel_grams` promises at least 151 grams, and the verifier proves it from the operation's `ensures result >= 1`, without knowing any handler.

### Receipts by email

Now the mail service, with two handlers. On a developer's machine the mail service prints each message instead of sending it, and a second handler stands for a service that refuses every address:

:::steps
```una include="steps/10-handlers/src/receipts.una" title="steps/10-handlers/src/receipts.una" verified="check, run"
module receipts

--- How the mail service can fail.
kind MailError = Bounced(address: Text) | Timeout

--- The mail service: what it can do, with no code.
capability Mailer
  op send(to: Text, subject: Text) -> Unit
    fails MailError

--- Emails the receipt of an order. It may send mail, and nothing else.
send_receipt(to: Text, order: Text) -> Unit
  uses @mailer: Mailer[send]
  fails MailError
=
  @mailer.send(to, subject: "Receipt for order {order}")
    if error pass

--- A mail service for a developer's machine: it prints each message instead of sending it.
handler printed(prefix: Text) for Mailer
  uses @console: Console[print]
  op send(to, subject) = @console.print("{prefix} to {to}: {subject}")

--- A mail service that refuses every address.
handler bouncing() for Mailer
  op send(to, subject) = fail Bounced(address: to)

pub main() -> Unit
  uses @console: Console[print]
=
  send_receipt("rosa@example.invalid", order: "A-1001") with @mailer = printed("[mail]")
    if error use unit
  let outcome = attempt send_receipt("tomas@example.invalid", order: "A-1002") with @mailer = bouncing()
  @console.print("second receipt: {outcome}")
```

1. **`capability Mailer` and `op send(...) -> Unit`.** One operation, which can fail with `MailError`.
2. **`send_receipt`.** It uses `@mailer: Mailer[send]` and fails with `MailError`. It does not know which mail service it talks to.
3. **`handler printed(prefix: Text) for Mailer`.** `prefix` is a parameter of the handler, given when it is installed and seen by `send`.
4. **`uses @console: Console[print]` inside the handler.** The console comes from the code that installs it: here `main`, which holds `@console`.
5. **`fail Bounced(address: to)`.** `bouncing` fails every time, with a variant of the operation's error kind.
6. **`with @mailer = printed("[mail]")`.** Inside that call, `@mailer` is the `printed` handler. `if error use unit` handles a failure, which `printed` never has.
7. **`attempt … with @mailer = bouncing()`.** The same function with the other handler. `attempt` keeps the failure as a value.
:::

`una run .` prints:

```text include="steps/10-handlers/expected/output.txt"
[mail] to rosa@example.invalid: Receipt for order A-1001
second receipt: Err(Bounced("tomas@example.invalid"))
```

The second line comes from `attempt` with the `bouncing` handler: the receipt was not sent, and the outcome says why.

### How handlers behave

#### A handler implements every operation

A handler must implement every operation of its capability, with the same names and the same number of parameters. Give the scale a second operation, `tare`, which sets it to zero, and leave the handler as it was:

```una include="steps/11-missing-op/src/scales.una#Scale..fixed" title="steps/11-missing-op/src/scales.una"
--- The scale at the packing desk: it weighs, and it can be set to zero.
capability Scale
  op weigh(sku: Text) -> Int
  op tare() -> Unit

--- A scale that only weighs.
handler fixed(grams: Int) for Scale
  op weigh(sku) = grams
```

```text include="steps/11-missing-op/expected/rendered.txt"
[U3011] Error: handler `fixed` does not implement the operation `tare` of `Scale`
   ╭─[ src/scales.una:9:9 ]
   │
 9 │ handler fixed(grams: Int) for Scale
   │         ──┬──
   │           ╰──── handler `fixed` does not implement the operation `tare` of `Scale`
   │
   │ Note: run `una explain U3011` for an explanation
───╯
```

U3011 names the handler, `fixed`, and the operation it lacks, `tare`. The mark is on the handler's name. Add `op tare() = unit` to the handler, or remove the operation if no handler should have it.

#### A handler is held to the operation's contract

The verifier checks each operation of a handler against the operation's `ensures`, as it checks a function. Return `grams` without the test:

```diff include="steps/09-scale..steps/12-broken-promise:src/scales.una" context="1" title="src/scales.una"
--- a/src/scales.una
+++ b/src/scales.una
@@ -26,3 +26,3 @@
 handler fixed(grams: Int) for Scale
-  op weigh(sku) = if grams < 1 then fail NotOnScale else grams
+  op weigh(sku) = grams
 
```

```text include="steps/12-broken-promise/expected/rendered.txt"
[U5001] Error: postcondition of `weigh` is refuted
    ╭─[ src/scales.una:27:19 ]
    │
 11 │     ensures result >= 1
    │             ─────┬─────
    │                  ╰─────── ensures clause
    │
 27 │   op weigh(sku) = grams
    │                   ──┬──
    │                     ╰──── postcondition of `weigh` is refuted
    │
    │ Help 1: repair 1: add a guard or an arm so that the failing path returns a value for which `result >= 1` holds
    │
    │ Help 2: repair 2: adjust the `ensures` clause
    │
    │ Note 1: obligation ob-8bdfbdc534e5 (postcondition) is refuted: result >= 1
    │
    │ Note 2: counterexample: grams = 0, result = 0, sku = Text#0, sku.len = 4
    │
    │ Note 3: run `una explain U5001` for an explanation
────╯
```

The diagnostic is U5001, the refuted postcondition of [chapter 7](/learn/contracts/#s7-2). The marks show the promise, `ensures result >= 1` on the operation, and the body that breaks it, `grams`. The counterexample, `grams = 0`, is a scale installed with a weight of 0. Callers rely on the promise, so a handler that breaks it does not check.

#### A handler is not a value

> [!TIP]
> A handler is not a value. It cannot be stored in a variable, passed as an ordinary argument or returned. It exists only where `with` or an example's `given` line installs it, and its parameters are fixed there.

#### Every capability is in the report

`una report .` lists each capability the package declares under `assumptions`, with its operations, since the program assumes that each service does what its declaration says. Under `authority` and `handler authority` it lists what each function and each handler may use:

```text include="steps/10-handlers/expected/commands/report.txt#L5-L9,L12-L13"
obligations: 0 proven, 0 refuted, 0 unknown; 0 cached
authority:
  receipts.main (pub): @console: Console[print]
  receipts.send_receipt (private): @mailer: Mailer[send]
handler authority:
escapes:
assumptions:
```

### A capability, a host capability or a pure function

:::decide
**Which to use:**

| The code needs… | Use |
| --- | --- |
| Only to compute a value from its arguments | A pure function, with no `uses` |
| The screen, the clock, the files or the network of the machine | A host capability, granted to `main` |
| A service of the business, such as mail, payments or a directory | A `capability` of your own, with a handler for each way to provide it |
| A stand-in for a service in a test | Another handler of the same capability |
:::

A capability of your own costs a declaration and a handler. It pays back as soon as the service has two providers, which it does the day you write a test.

### Check yourself: handlers

`main` in the scale's step makes a second call, with a scale installed at a weight of 0:

```una include="steps/09-scale/src/scales.una#main" title="steps/09-scale/src/scales.una"
pub main() -> Unit
  uses @console: Console[print]
=
  let weighed = attempt parcel_grams("LAMP-01") with @scale = fixed(850)
  @console.print("{weighed}")
  let empty = attempt parcel_grams("LAMP-01") with @scale = fixed(0)
  @console.print("{empty}")
```

What does the second line print?

:::answer Show the answer
```text include="steps/09-scale/expected/output.txt#L2"
Err(NotOnScale)
```

`fixed(0)` takes the `then` branch of its test, `grams < 1`, and fails with `NotOnScale`. `parcel_grams` passes the failure on with `if error pass`, and `attempt` in `main` keeps it as `Err(NotOnScale)`.
:::

A second one, without code: a handler `free()` for `Scale` has `op weigh(sku) = 0`. Does it check?

:::answer Show the answer
No. `weigh` promises `result >= 1`, and 0 breaks it, so the verifier refutes the operation with U5001, as in [A handler is held to the operation's contract](#a-handler-is-held-to-the-operations-contract).
:::

## 8.4 Passing authority: `with`, rebinding and narrowing

### What passing authority means

A capability moves from a caller to a callee, and only that way. A store manager lends a colleague a key for one errand: the colleague uses it for that errand and hands it back. They cannot copy it, keep it in a drawer, or give it to a stranger. In Una, the caller is the manager, the callee is the colleague, and the errand is one call.

Three things can happen at a call:

- **By name.** The callee's header asks for `@customers`, and the caller holds a `@customers`. It is handed over with nothing written at the call.
- **Rebinding.** The callee asks for `@audit`, and the caller holds the same capability under another name, `@console`. `with @audit = @console` hands it over under the callee's name.
- **Installing.** The caller holds no such capability, or wants another provider. `with @customers = directory(customers)` installs a handler.

And whatever the callee receives, it may use only the operations its own header lists: authority narrows on its way down.

### Why authority moves only downward

If a capability were a value, a function could keep it: store it in a record, return it, or pass it to code that its header never mentions. A reviewer would then have to follow every value to know who can print or send mail. Una forbids it. Try to keep the console in a variable:

```una include="steps/13-stored-capability/src/slips.una" title="steps/13-stored-capability/src/slips.una"
module slips

pub main() -> Unit
  uses @console: Console[print]
=
  let saved = @console
  saved.print("Packing slip for order A-1001")
```

```text include="steps/13-stored-capability/expected/rendered.txt"
[U3005] Error: capability `@console` is used as a value; capabilities pass by name, through `uses` and `with`
   ╭─[ src/slips.una:6:15 ]
   │
 6 │   let saved = @console
   │               ────┬───
   │                   ╰───── capability `@console` is used as a value; capabilities pass by name, through `uses` and `with`
   │
   │ Note: run `una explain U3005` for an explanation
───╯
```

U3005 says that the capability is "used as a value", and how capabilities move instead: "by name, through `uses` and `with`". Because a capability never travels any other way, every function's reach is in its header, and in the headers of the functions that call it.

### How to write `with`

#### Passing by name: nothing to write

When the names match, write nothing. `main` holds `@console`, and `print_line` in [section 8.1](#s8-1) asks for `@console`, so `print_line("LAMP-01", quantity: 2)` passes it.

#### Rebinding: `with @x = @y`

`with`, at the end of a statement, then the callee's name, `=` and the caller's binding. Both must be the same capability, and the caller's binding must permit at least the operations the callee lists.

#### Installing a handler: `with @x = handler(args)`

The callee's name, `=` and a call of a handler for the capability the callee needs at that name. The handler's own `uses` must be held by the caller.

#### Several bindings

One `with` takes several bindings, separated by commas: `with @customers = directory(customers), @audit = @console`.

#### How far `with` reaches

A `with` belongs to the statement it ends, or to the `let` it ends, and to nothing after it. The next statement gets its bindings by name again, or from its own `with`.

| Write | The callee's `@x` is |
| --- | --- |
| nothing | the caller's `@x`, if it has one |
| `with @x = @y` | the caller's `@y`, which has the same capability |
| `with @x = handler(args)` | a new instance of that handler |

### Narrowing: a greeting that may only look up

In this step, the customer directory has two operations, looking a customer up and erasing one. The page greeting may look up, and only the erase request may erase:

:::steps
```una include="steps/14-with/src/accounts.una" title="steps/14-with/src/accounts.una" verified="check, run"
module accounts

kind Customer
  id: Text
  name: Text

--- The customer directory. Looking a customer up and erasing one are separate operations.
capability Customers
  op find(id: Text) -> Option[Customer]
  op forget(id: Text) -> Unit

--- The greeting on an order page. It may look customers up, and never erase one.
greeting(id: Text) -> Text
  uses @customers: Customers[find]
=
  let customer = @customers.find(id)
    if none use Customer(id: id, name: "guest")
  "Welcome back, {customer.name}"

--- Erases a customer at their request, and writes the request to the audit trail.
erase(id: Text) -> Unit
  uses @customers: Customers[forget]
  uses @audit: Console[print]
=
  @customers.forget(id)
  @audit.print("audit: erased customer {id}")

--- A directory held in memory. It is a fixed value, so `forget` changes nothing here.
handler directory(customers: Map[Text, Customer]) for Customers
  op find(id) = customers.get(key: id)
  op forget(id) = unit

pub main() -> Unit
  uses @console: Console[print]
=
  let customers = empty_map().with(key: "C-17", value: Customer(id: "C-17", name: "Rosa"))
  let page = greeting("C-17") with @customers = directory(customers)
  @console.print(page)
  let unknown = greeting("C-99") with @customers = directory(customers)
  @console.print(unknown)
  erase("C-20") with @customers = directory(customers), @audit = @console
```

1. **`capability Customers` with `find` and `forget`.** Two operations with different risks. Neither has a `fails` clause: these two cannot fail.
2. **`uses @customers: Customers[find]` on `greeting`.** The `directory` handler implements both operations, but `greeting` holds only `find`. An `@customers.forget(id)` in its body would not check.
3. **`if none use Customer(id: id, name: "guest")`.** `find` returns an `Option`, so the handling clauses of [chapter 6](/learn/failure/) apply to an operation as to any call.
4. **`uses @audit: Console[print]` on `erase`.** The audit trail is a console here, under the name `@audit`, so the header says what the console is for.
5. **`let page = greeting("C-17") with @customers = directory(customers)`.** A `with` at the end of a `let`: it installs the handler for that call.
6. **`with @customers = directory(customers), @audit = @console`.** Two bindings. The first installs a handler. The second is a rebinding: the callee's `@audit` is the caller's `@console`. `main` holds no `@audit` of its own, so without the rebinding the call would not check.
:::

`una run .` prints:

```text include="steps/14-with/expected/output.txt"
Welcome back, Rosa
Welcome back, guest
audit: erased customer C-20
```

### How `with` behaves

#### A callee holds only what its header lists

A callee may receive a binding with more operations than it needs. It then holds only the operations its own header lists. `directory` can forget customers, but inside `greeting` the binding permits `find` and nothing else.

#### Each installation is a new instance

Each `with @customers = directory(customers)` installs a new instance. A handler holds no state between calls, and `directory` takes its map as a parameter, so `forget` has nothing to change here. A handler for a real directory would call the service.

#### Where a handler's own capabilities come from

A handler installed with `with` takes its own `uses` from the code around the statement, by name. `printed`, in [section 8.3](#s8-3), holds `@console` because `main`, which installs it, holds `@console`.

#### A binding of the wrong capability

A rebinding needs the same capability on both sides, and a handler must implement the capability the callee needs at that name. Installing a `Customers` handler as `@mailer` is U3010, as [installing a handler of another capability](#installing-a-handler-of-another-capability-u3010) shows.

#### Checking that authority narrows

> [!IMPORTANT]
> Narrowing is a promise you can check. Because `greeting` holds `Customers[find]`, no change to its body can make it erase a customer without a change to its header, which a reviewer sees.

### Pass, rebind or install

:::decide
**Which to use:**

| At the call… | Write |
| --- | --- |
| The caller holds the capability under the callee's name | Nothing |
| The caller holds it under another name | `with @callee_name = @caller_name` |
| The caller must choose a provider, or holds none | `with @x = handler(args)` |
| The caller wants the callee to use fewer operations | Nothing: the callee's header already limits it |
:::

Name bindings after what they are for, as `@audit` and `@log` are. A rebinding at the call then reads as a decision: "the audit trail is the console, here".

### Check yourself: `with`

In the step, remove `@audit = @console` from the last line of `main`, so that it reads `erase("C-20") with @customers = directory(customers)`. Does it check?

:::answer Show the answer
No. `erase` needs `@audit: Console[print]`, and `main` holds no binding named `@audit`: bindings are found by name, never by type, so `@console` does not count. `una check .` reports U3001 at the call, as [forgetting to hand over a binding](#forgetting-to-hand-over-a-binding-u3001) shows for the day-to-day program.
:::

A second one: `main` holds `@console: Console[print]`. It calls `greeting("C-17")` with no `with` at all. What does `una check .` say?

:::answer Show the answer
U3001 again. `greeting` needs `@customers`, and `main` holds none. A handler exists only where `with` installs it, so the call must install one, as the step does.
:::

## 8.5 Edition 0.3 preview: conditions and boundaries

### What edition 0.3 adds

An **edition** is a version of the language that a package chooses. Edition `0.3` is a preview: a package opts in with `edition = "0.3"` in `una.toml`, and [chapter 14, Editions](/learn/editions/), explains what that means. It adds two ways to say more about authority:

- A **condition on an operation**: the header says not only what a function may do, but when.
- A **boundary**: a module from outside the store's own code, such as a vendored library, receives only what each call grants it, up to a ceiling written in `una.toml`.

### Why an operation needs a condition

A function often has a mode in which it must not act: a dry run, a preview, a rehearsal. The rule "never place an order in a dry run" usually lives in an `if` somewhere in the body, or in a callee, and nothing makes sure every path respects it. One forgotten branch, and the rehearsal places real orders. A condition puts the rule in the header, where the verifier proves it on every path.

### How to write a condition

After the operation's name in the brackets of `uses`, write `where` and a condition over the function's parameters: `uses @supplier: Supplier[order where not dry_run]` lets the function place an order only where `dry_run` is false. The condition is written in the refinement language of [chapter 7](/learn/contracts/#s7-3), like a `requires` clause, and must be a `Bool`. It reads the parameters only: they never change during a call, so the condition's value is fixed for the whole call. Operations without `where` in the same brackets are unconditioned.

### A restock with a dry run

The step's `reorder` may place an order only when `dry_run` is false:

```toml include="steps/15-conditions/una.toml" title="steps/15-conditions/una.toml"
[package]
name = "restock"
version = "0.1.0"
edition = "0.3"

[run]
entry = "restock"
grants = ["console"]
```

```una include="steps/15-conditions/src/restock.una" title="steps/15-conditions/src/restock.una" verified="check, run"
module restock

--- The supplier's ordering service.
capability Supplier
  op order(sku: Text, units: Int) -> Unit

--- Reorders a SKU that runs low. A dry run only says what it would order.
reorder(sku: Text, left: Int, dry_run: Bool) -> Unit
  uses @supplier: Supplier[order where not dry_run]
  uses @console: Console[print]
=
  if left >= 5
    unit
  else if dry_run
    @console.print("would order 20 x {sku}")
  else
    @supplier.order(sku, units: 20)

--- A supplier on a developer's machine: it prints each order instead of placing it.
handler printed() for Supplier
  uses @console: Console[print]
  op order(sku, units) = @console.print("ordered {units} x {sku}")

pub main() -> Unit
  uses @console: Console[print]
=
  reorder("LAMP-01", left: 2, dry_run: true) with @supplier = printed()
  reorder("LAMP-01", left: 2, dry_run: false) with @supplier = printed()
  reorder("DESK-02", left: 9, dry_run: false) with @supplier = printed()
```

`una run .` prints:

```text include="steps/15-conditions/expected/output.txt"
would order 20 x LAMP-01
ordered 20 x LAMP-01
```

The first call is a dry run, so it only prints. The third finds enough stock and does nothing. In the `else` branch that places the order, the verifier knows that `dry_run` is false, which is the condition.

### How a condition is checked

The verifier proves, at every place where the operation can run, that the condition holds. A call of a function that performs the operation counts as such a place too, so the condition holds through every layer of calls. If `reorder` placed the order without the `dry_run` branch, `una check` would report U5001, with a counterexample in which `dry_run` is true ([running an operation where its condition may not hold](#running-an-operation-where-its-condition-may-not-hold-edition-03-u5001) shows it).

Two rules keep the proof sound:

- **A condition is never inferred.** A private function without `uses` has no condition on any operation.
- **A function with a condition is not a value.** A function can usually be passed to another function as an argument ([chapter 3](/learn/functions/#s3-5)). One whose `uses` carry a condition cannot, since the function that receives it could not prove the condition.

### What a boundary is

A package often holds code it did not write, such as a vendored library that prints barcodes. Its functions declare their own `uses`, but a reviewer of the store's code would like a limit that the library's author cannot change: whatever its headers say, it never gets more than this. `una.toml` can mark such a module as a **boundary**, with a **ceiling**: the most the rest of the package may grant it, as a list of capabilities and operations.

### How to write a boundary

Under `[boundaries]` in `una.toml`, one line per module: its name in quotes, `=`, and the list of what it may receive. Here the vendored module is `barcode`, and its ceiling allows `Console[print]`:

```toml include="steps/16-boundaries/una.toml" title="steps/16-boundaries/una.toml"
[package]
name = "shelf"
version = "0.1.0"
edition = "0.3"

[run]
entry = "shelf"
grants = ["console"]

[boundaries]
"barcode" = ["Console[print]"]
```

### Calling into a boundary

This is the vendored module. Its function needs `@console`, which the store's code must grant it:

```una include="steps/16-boundaries/src/barcode.una" title="steps/16-boundaries/src/barcode.una" verified="check, run"
module barcode

--- Prints a shelf label with the SKU spelled out for a barcode font. This module is code from
--- outside the store, so `una.toml` lists it as a boundary.
pub print_label(sku: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("*{sku.to_upper}*")
```

The store's own module calls it, and grants the console at each call with `with`:

```una include="steps/16-boundaries/src/shelf.una" title="steps/16-boundaries/src/shelf.una" verified="check, run"
module shelf

import barcode (print_label)

pub main() -> Unit
  uses @console: Console[print]
=
  print_label("lamp-01") with @console = @console
  print_label("desk-02") with @console = @console
```

`una run .` prints:

```text include="steps/16-boundaries/expected/output.txt"
*LAMP-01*
*DESK-02*
```

### How a boundary is checked

#### Nothing passes by name

A call into a boundary takes nothing by name. The caller grants each capability with `with`, so every call shows what the boundary receives. Leave out the `with` on the second call:

```diff include="steps/16-boundaries..steps/17-boundary-call:src/shelf.una" context="1" title="src/shelf.una"
--- a/src/shelf.una
+++ b/src/shelf.una
@@ -8,2 +8,2 @@
   print_label("lamp-01") with @console = @console
-  print_label("desk-02") with @console = @console
+  print_label("desk-02")
```

```text include="steps/17-boundary-call/expected/rendered.txt"
[U3020] Error: `print_label` is in the boundary `barcode` and needs `@console: Console[print]`, which a call into it grants only with `with`
   ╭─[ src/barcode.una:6:3 ]
   │
 6 │   uses @console: Console[print]
   │   ──────────────┬──────────────
   │                 ╰──────────────── the boundary's requirement
   │
   ├─[ src/shelf.una:9:3 ]
   │
 9 │   print_label("desk-02")
   │   ───────────┬──────────
   │              ╰──────────── `print_label` is in the boundary `barcode` and needs `@console: Console[print]`, which a call into it grants only with `with`
   │
   │ Note: run `una explain U3020` for an explanation
───╯
```

U3020 points at two places: the boundary's requirement, the `uses` line of `print_label`, and the call that does not grant it. `with @console = @console` reads as redundant elsewhere; at a boundary it is the grant.

#### The ceiling holds every grant

The checker holds every grant under the ceiling. If `print_label` also needed a `Clock`, granting it would be U3021, since the ceiling allows only `Console[print]`. A binding that the callee does not need is not counted against the ceiling. A boundary module can never be trusted, so it can never release labeled data ([chapter 9](/learn/information-flow/)).

### A condition, a narrower header or a boundary

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A function that may perform an operation only in some calls, such as never in a dry run | A condition: `op where …` in its `uses` |
| A function that never performs an operation | Leave the operation out of its `uses` |
| Code you did not write to receive at most some authority, whatever its headers say | A boundary with a ceiling, in `una.toml` |
:::

Conditions and boundaries are edition `0.3`. In edition `0.2`, the closest you can come is a narrow header and a review of every call.

### Check yourself: conditions and boundaries

`rehearse` holds `uses @mailer: Mailer[send where not dry_run]` and calls `dispatch(shipments)`, whose header holds `uses @mailer: Mailer[send]` with no condition. Does the call check, with no `if` around it?

:::answer Show the answer
No. `dispatch` may send mail on every call, so the call is a place where `send` can run, and there the verifier must prove `not dry_run`. Nothing tells it what `dry_run` is, so it refutes the condition with `dry_run = true`. [Exercise 3](#exercise-3-a-dry-run-edition-03) starts from exactly this function, and its answer puts the call in the `else` branch of `if dry_run`.
:::

## 8.6 Day-to-day: shipping notices

### What the dispatch step must do

Now the program from the start of the chapter. When orders leave the warehouse, the store emails each customer a notice. The customer directory and the mail service are services on the network, which can time out. The operator reads a log with one line per order. Each part of the job uses one idea of this chapter:

| Part of the job | How the program does it |
| --- | --- |
| Talk to the directory and the mail service | two capabilities of its own, `Customers` and `Mailer` ([section 8.3](#s8-3)) |
| Write the notice's text | a pure function, with no `uses` ([section 8.1](#s8-1)) |
| Send one notice, and nothing else | a header with exactly two operations |
| Run a batch and log each outcome | a header with a third binding, `@log`, which `main` rebinds to the console ([section 8.4](#s8-4)) |
| Run with fake services, here and in tests | handlers, installed with `with` and, in tests, `given` |
| Print at all | the one grant of `una.toml`, `"console"` ([section 8.2](#s8-2)) |

### The kinds and the services

`Customer` and `Shipment` are records. `NoticeError` has one variant for each reason a notice is not sent. `Customers` and `Mailer` are capabilities: what the services can do, with no code.

```una include="day-to-day/src/notices.una#L1-L30" title="day-to-day/src/notices.una" caption="the kinds and the services"
module notices

--- A customer, as the customer directory knows them.
pub kind Customer
  id: Text
  name: Text
  email: Text
  wants_notices: Bool

--- An order that has left the warehouse and waits for its shipping notice.
pub kind Shipment
  order: Text
  customer: Text
  carrier: Text

--- How a remote service can fail.
pub kind ServiceError = | Timeout

--- Why a shipment got no notice. Each variant carries what an operator needs to act on it.
pub kind NoticeError = UnknownCustomer(id: Text) | OptedOut(id: Text) | DirectoryDown | MailDown

--- The customer directory, a service on the network.
pub capability Customers
  op find(id: Text) -> Option[Customer]
    fails ServiceError

--- The mail service, a service on the network.
pub capability Mailer
  op send(to: Text, subject: Text, body: Text) -> Unit
    fails ServiceError
```

### The notice text, pure

`notice` has no `uses`, and it is `pub`, so it cannot reach any service. Its tests need no fakes.

```una include="day-to-day/src/notices.una#notice" title="day-to-day/src/notices.una"
--- The text of a shipping notice. Pure: it has no `uses`, so it cannot reach any service.
pub notice(customer: Customer, shipment: Shipment) -> Text = "Hello {customer.name}, your order {shipment.order} is on its way with {shipment.carrier}."
```

### One notice

`notify` holds two bindings, with one operation each. Its header says, completely, that it may look customers up and send mail. It cannot print, read files or erase anyone.

```una include="day-to-day/src/notices.una#notify" title="day-to-day/src/notices.una"
--- Finds the customer of a shipment and emails them the notice. Returns the address it wrote to.
pub notify(shipment: Shipment) -> Text
  uses @customers: Customers[find]
  uses @mailer: Mailer[send]
  fails NoticeError
=
  let customer = @customers.find(shipment.customer)
    if error fail DirectoryDown
    if none fail UnknownCustomer(id: shipment.customer)
  if not customer.wants_notices
    fail OptedOut(id: customer.id)
  else
    @mailer.send(customer.email, subject: "Order {shipment.order} has shipped", body: notice(customer, shipment: shipment))
      if error fail MailDown
    customer.email
```

`notify` returns the address rather than printing it, because printing is not its job: it has no binding for a log, and the header shows that. The order of the statements is the order of the work. The directory is asked first. A failure of the directory becomes `DirectoryDown`, and an unknown customer becomes `UnknownCustomer`. A customer who asked for no notices fails with `OptedOut` before any mail is sent, and a failure of the mail service becomes `MailDown`. When everything works, `notify` returns the address it wrote to.

### The log

`reason` and `log_line` turn an outcome into the text an operator reads. Both are pure.

```una include="day-to-day/src/notices.una#reason..log_line" title="day-to-day/src/notices.una"
--- What an operator reads in the dispatch log.
pub reason(failure: NoticeError) -> Text
=
  when failure
    is UnknownCustomer(id) -> "no customer has the id {id}"
    is OptedOut(id) -> "customer {id} asked for no notices"
    is DirectoryDown -> "the customer directory did not answer; retry later"
    is MailDown -> "the mail service did not answer; retry later"

--- One line of the dispatch log.
pub log_line(shipment: Shipment, outcome: Result[Text, NoticeError]) -> Text
=
  when outcome
    is Ok(address) -> "sent     {shipment.order} to {address}"
    is Err(failure) -> "skipped  {shipment.order}: {reason(failure)}"
```

### The batch

`dispatch` holds the two services and a log. `attempt` keeps each outcome, so one failure does not stop the batch, and each outcome becomes one line on `@log`.

```una include="day-to-day/src/notices.una#dispatch" title="day-to-day/src/notices.una"
--- Sends a notice for every shipment and logs each outcome. One failure does not stop the batch.
pub dispatch(shipments: List[Shipment]) -> Unit
  uses @customers: Customers[find]
  uses @mailer: Mailer[send]
  uses @log: Console[print]
=
  for shipment in shipments
    let outcome = attempt notify(shipment)
    @log.print(log_line(shipment, outcome: outcome))
```

`dispatch` calls the log `@log`, not `@console`. The name says what the binding is for, and the caller decides what it is: the console in `main`, a fake in a test, or one day a log service with a handler of its own. `dispatch` holds the union of what it does itself and what `notify` needs, and nothing more. `una report .` lists, under `authority`, the bindings of every public function, so a reviewer can read the service's whole reach in one place.

### The handlers

In production, `Customers` and `Mailer` would have handlers that call the real services over the network. Such a handler declares its own `uses`, such as the host's `Http`, and the code that installs it must hold them. The network would then appear in the header of `main` and in the grants of `una.toml`, and nowhere in `notify` or `dispatch`, which do not change. Here, `directory` holds the customers in a map, `outbox` accepts every message and delivers none, and `mail_down` and `directory_down` never answer. `quiet` is a fake console for the tests.

```una include="day-to-day/src/notices.una#directory..quiet" title="day-to-day/src/notices.una"
--- A directory held in memory, for this run and for tests.
handler directory(customers: Map[Text, Customer]) for Customers
  op find(id) = customers.get(key: id)

--- A mail service that accepts every message and delivers none: a fake for this run and for tests.
handler outbox() for Mailer
  op send(to, subject, body) = unit

--- A mail service that never answers.
handler mail_down() for Mailer
  op send(to, subject, body) = fail Timeout

--- A directory that never answers.
handler directory_down() for Customers
  op find(id) = fail Timeout

--- A console that prints nothing, for tests.
handler quiet() for Console
  op print(line) = unit
```

### Running it

`main` holds only `@console`, which `una.toml` grants. It installs the handlers with `with`, and hands its console to `dispatch` as `@log`. The second batch runs with `mail_down`, to show the last line of the log.

```una include="day-to-day/src/notices.una#sample_customers..main" title="day-to-day/src/notices.una"
--- The customers of this run and of the examples. Every address is fictional.
pub sample_customers() -> Map[Text, Customer]
=
  let rosa = Customer(id: "C-17", name: "Rosa", email: "rosa@example.invalid", wants_notices: true)
  let tomas = Customer(id: "C-20", name: "Tomas", email: "tomas@example.invalid", wants_notices: true)
  let ines = Customer(id: "C-21", name: "Ines", email: "ines@example.invalid", wants_notices: false)
  empty_map().with(key: rosa.id, value: rosa).with(key: tomas.id, value: tomas).with(key: ines.id, value: ines)

pub main() -> Unit
  uses @console: Console[print]
=
  let customers = sample_customers()
  let morning = [Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"), Shipment(order: "A-1002", customer: "C-20", carrier: "Parcelo"), Shipment(order: "A-1003", customer: "C-99", carrier: "Parcelo"), Shipment(order: "A-1004", customer: "C-21", carrier: "Parcelo")]
  dispatch(morning) with @customers = directory(customers), @mailer = outbox(), @log = @console
  let late = [Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida")]
  dispatch(late) with @customers = directory(customers), @mailer = mail_down(), @log = @console
```

`una run .` prints the log shown in [What you'll build](#what-youll-build). The addresses use the reserved domain `example.invalid`, so no real mailbox could receive them.

Compare the two calls of `dispatch` in `main`: they differ in one handler, `outbox()` or `mail_down()`. Running the same code against another service, in a program or in a test, costs exactly that change, and `dispatch` and `notify` never learn which service they talk to.

> [!SECURITY]
> The log prints customers' email addresses. In a real store that is personal data, and a log is a place it should not go. [Chapter 9](/learn/information-flow/) labels the addresses `secret[PII]`, lets the checker find this line, and releases a masked form through a policy.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/notices.una" title="day-to-day/src/notices.una" caption="the whole program" verified="check, run, test"
module notices

--- A customer, as the customer directory knows them.
pub kind Customer
  id: Text
  name: Text
  email: Text
  wants_notices: Bool

--- An order that has left the warehouse and waits for its shipping notice.
pub kind Shipment
  order: Text
  customer: Text
  carrier: Text

--- How a remote service can fail.
pub kind ServiceError = | Timeout

--- Why a shipment got no notice. Each variant carries what an operator needs to act on it.
pub kind NoticeError = UnknownCustomer(id: Text) | OptedOut(id: Text) | DirectoryDown | MailDown

--- The customer directory, a service on the network.
pub capability Customers
  op find(id: Text) -> Option[Customer]
    fails ServiceError

--- The mail service, a service on the network.
pub capability Mailer
  op send(to: Text, subject: Text, body: Text) -> Unit
    fails ServiceError

--- The text of a shipping notice. Pure: it has no `uses`, so it cannot reach any service.
pub notice(customer: Customer, shipment: Shipment) -> Text = "Hello {customer.name}, your order {shipment.order} is on its way with {shipment.carrier}."

--- Finds the customer of a shipment and emails them the notice. Returns the address it wrote to.
pub notify(shipment: Shipment) -> Text
  uses @customers: Customers[find]
  uses @mailer: Mailer[send]
  fails NoticeError
=
  let customer = @customers.find(shipment.customer)
    if error fail DirectoryDown
    if none fail UnknownCustomer(id: shipment.customer)
  if not customer.wants_notices
    fail OptedOut(id: customer.id)
  else
    @mailer.send(customer.email, subject: "Order {shipment.order} has shipped", body: notice(customer, shipment: shipment))
      if error fail MailDown
    customer.email

--- What an operator reads in the dispatch log.
pub reason(failure: NoticeError) -> Text
=
  when failure
    is UnknownCustomer(id) -> "no customer has the id {id}"
    is OptedOut(id) -> "customer {id} asked for no notices"
    is DirectoryDown -> "the customer directory did not answer; retry later"
    is MailDown -> "the mail service did not answer; retry later"

--- One line of the dispatch log.
pub log_line(shipment: Shipment, outcome: Result[Text, NoticeError]) -> Text
=
  when outcome
    is Ok(address) -> "sent     {shipment.order} to {address}"
    is Err(failure) -> "skipped  {shipment.order}: {reason(failure)}"

--- Sends a notice for every shipment and logs each outcome. One failure does not stop the batch.
pub dispatch(shipments: List[Shipment]) -> Unit
  uses @customers: Customers[find]
  uses @mailer: Mailer[send]
  uses @log: Console[print]
=
  for shipment in shipments
    let outcome = attempt notify(shipment)
    @log.print(log_line(shipment, outcome: outcome))

--- A directory held in memory, for this run and for tests.
handler directory(customers: Map[Text, Customer]) for Customers
  op find(id) = customers.get(key: id)

--- A mail service that accepts every message and delivers none: a fake for this run and for tests.
handler outbox() for Mailer
  op send(to, subject, body) = unit

--- A mail service that never answers.
handler mail_down() for Mailer
  op send(to, subject, body) = fail Timeout

--- A directory that never answers.
handler directory_down() for Customers
  op find(id) = fail Timeout

--- A console that prints nothing, for tests.
handler quiet() for Console
  op print(line) = unit

--- The customers of this run and of the examples. Every address is fictional.
pub sample_customers() -> Map[Text, Customer]
=
  let rosa = Customer(id: "C-17", name: "Rosa", email: "rosa@example.invalid", wants_notices: true)
  let tomas = Customer(id: "C-20", name: "Tomas", email: "tomas@example.invalid", wants_notices: true)
  let ines = Customer(id: "C-21", name: "Ines", email: "ines@example.invalid", wants_notices: false)
  empty_map().with(key: rosa.id, value: rosa).with(key: tomas.id, value: tomas).with(key: ines.id, value: ines)

pub main() -> Unit
  uses @console: Console[print]
=
  let customers = sample_customers()
  let morning = [Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"), Shipment(order: "A-1002", customer: "C-20", carrier: "Parcelo"), Shipment(order: "A-1003", customer: "C-99", carrier: "Parcelo"), Shipment(order: "A-1004", customer: "C-21", carrier: "Parcelo")]
  dispatch(morning) with @customers = directory(customers), @mailer = outbox(), @log = @console
  let late = [Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida")]
  dispatch(late) with @customers = directory(customers), @mailer = mail_down(), @log = @console

example "a customer who wants notices gets one"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect result == "rosa@example.invalid"
  expect performed @mailer.send

example "an unknown customer gets no mail"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  do notify(Shipment(order: "A-1003", customer: "C-99", carrier: "Parcelo"))
  expect fails UnknownCustomer
  expect not performed @mailer.send

example "a customer who asked for no notices gets no mail"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  do notify(Shipment(order: "A-1004", customer: "C-21", carrier: "Parcelo"))
  expect fails OptedOut
  expect not performed @mailer.send

example "a directory that does not answer is DirectoryDown, and no mail is sent"
  given @customers = directory_down()
  given @mailer = outbox()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect fails DirectoryDown
  expect not performed @mailer.send

example "a mail service that does not answer is MailDown"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect fails MailDown

example "the batch logs every shipment, even when the mail service is down"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  given @log = quiet()
  do dispatch([Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida")])
  expect performed @log.print
```

## 8.7 Testing it

### Fakes for every path

Examples never reach the host or a real service. Each one installs fakes with `given`, one line per binding the `do` line needs, so every path of the service can be tested on demand: a directory that does not answer, a mail service that does not answer, a customer who opted out.

```una include="day-to-day/src/notices.una#L114-L153" title="day-to-day/src/notices.una" caption="the examples"
example "a customer who wants notices gets one"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect result == "rosa@example.invalid"
  expect performed @mailer.send

example "an unknown customer gets no mail"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  do notify(Shipment(order: "A-1003", customer: "C-99", carrier: "Parcelo"))
  expect fails UnknownCustomer
  expect not performed @mailer.send

example "a customer who asked for no notices gets no mail"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  do notify(Shipment(order: "A-1004", customer: "C-21", carrier: "Parcelo"))
  expect fails OptedOut
  expect not performed @mailer.send

example "a directory that does not answer is DirectoryDown, and no mail is sent"
  given @customers = directory_down()
  given @mailer = outbox()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect fails DirectoryDown
  expect not performed @mailer.send

example "a mail service that does not answer is MailDown"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect fails MailDown

example "the batch logs every shipment, even when the mail service is down"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  given @log = quiet()
  do dispatch([Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida")])
  expect performed @log.print
```

### Checking effects: `expect performed`

Two kinds of `expect` line check effects:

- `expect performed @mailer.send` holds when the `do` call performed that operation at least once.
- `expect not performed @mailer.send` holds when it never did. Here it proves that an unknown customer, an opted-out customer and a directory that does not answer never cause a mail to be sent.

### A fake console

The last example needs a `given` line for `@log` too, because `dispatch` uses it. An example cannot use the real console: every capability comes from a `given` line, so a test run is deterministic. `quiet` is a handler for the host capability `Console`, which user code may write like any other.

### What an example cannot check

A handler holds no state, so an example cannot count how many mails were sent, or read their text back. It checks what a `do` call returns, how it fails, and which operations it performed. To check the text of a notice, test the pure function that builds it, `notice`, with no fakes at all.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L9"
example notices "a customer who wants notices gets one" ... ok
example notices "an unknown customer gets no mail" ... ok
example notices "a customer who asked for no notices gets no mail" ... ok
example notices "a directory that does not answer is DirectoryDown, and no mail is sent" ... ok
example notices "a mail service that does not answer is MailDown" ... ok
example notices "the batch logs every shipment, even when the mail service is down" ... ok

6 examples: 6 passed, 0 failed
```

## 8.8 Common mistakes

Most of the mistakes below are a small change to `day-to-day/src/notices.una`. The others change a step of this chapter, as each one says. The capability diagnostics are U3 codes, reported before any proof is tried. Each names the binding and what is missing, and marks the place in the code where it is needed.

### Forgetting to hand over a binding (U3001)

:::mistake
Leave `@log = @console` out of the first `with` in `main`:

```diff include="day-to-day..mistakes/1:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -109,3 +109,3 @@
   let morning = [Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"), Shipment(order: "A-1002", customer: "C-20", carrier: "Parcelo"), Shipment(order: "A-1003", customer: "C-99", carrier: "Parcelo"), Shipment(order: "A-1004", customer: "C-21", carrier: "Parcelo")]
-  dispatch(morning) with @customers = directory(customers), @mailer = outbox(), @log = @console
+  dispatch(morning) with @customers = directory(customers), @mailer = outbox()
   let late = [Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida")]
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U3001] Error: `dispatch` needs `@log: Console[print]`, which is not in scope here
```

*Why:* the console is right there in `main`, so it seems `dispatch` should find it. But `dispatch` needs `@log`, and `main` holds only `@console`. Bindings are found by name, never by type. The message names the callee, the binding with its capability, and "not in scope here"; the mark is on the call.

*Fix:* add `@log = @console` to the `with`. The repair una offers, a `uses @log` line on `main`, would widen `main`'s header instead, so `una fix` skips it, and `una fix --dry-run .` says so ([For agents](#for-agents)).
:::

### Using an operation the header does not list (U3002)

:::mistake
In the step of [Narrowing: a greeting that may only look up](#narrowing-a-greeting-that-may-only-look-up), give `erase` the header of `greeting`, `uses @customers: Customers[find]`:

```diff include="steps/14-with..mistakes/2:src/accounts.una" context="1" title="src/accounts.una"
--- a/src/accounts.una
+++ b/src/accounts.una
@@ -21,3 +21,3 @@
 erase(id: Text) -> Unit
-  uses @customers: Customers[forget]
+  uses @customers: Customers[find]
   uses @audit: Console[print]
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U3002] Error: `@customers` permits `find`, not `forget`
```

*Why:* the header was copied from a similar function. The brackets list every operation the function may perform, and the mark is on the operation the header does not list, `forget`. The repair una offers widens the header, so it is yours to judge.

*Fix:* write `Customers[forget]`. Add an operation to a header only when it belongs to the function's job: every caller must then hold it too.
:::

### An effect in a pure `pub` function (U3004)

:::mistake
Add a log line to `notice`:

```diff include="day-to-day..mistakes/3:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -32,3 +32,6 @@
 --- The text of a shipping notice. Pure: it has no `uses`, so it cannot reach any service.
-pub notice(customer: Customer, shipment: Shipment) -> Text = "Hello {customer.name}, your order {shipment.order} is on its way with {shipment.carrier}."
+pub notice(customer: Customer, shipment: Shipment) -> Text
+=
+  @log.print("writing the notice for {shipment.order}")
+  "Hello {customer.name}, your order {shipment.order} is on its way with {shipment.carrier}."
 
```

```text include="mistakes/3/expected/rendered.txt#L1"
[U3004] Error: `@log` is used here, but this code declares no `uses`, so it is pure
```

*Why:* a log line is a habit when something needs watching. But a `pub` function declares every `uses`, so one without `uses` is pure, and the mark is on the binding it tries to use, `@log`.

*Fix:* log in the caller, which already holds `@log`. A message text should stay a pure function, which tests can call without fakes.
:::

### Installing a handler of another capability (U3010)

:::mistake
Write `@mailer = directory_down()`:

```diff include="day-to-day..mistakes/4:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -111,3 +111,3 @@
   let late = [Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida")]
-  dispatch(late) with @customers = directory(customers), @mailer = mail_down(), @log = @console
+  dispatch(late) with @customers = directory(customers), @mailer = directory_down(), @log = @console
 
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U3010] Error: this handler implements `Customers`, and `dispatch` needs `@mailer` to be `Mailer`
```

*Why:* both handlers stand for a service that never answers, and their names are close. The message says which capability the handler implements, `Customers`, and which one the callee needs at that name, `Mailer`; the mark is on the handler's call.

*Fix:* install `mail_down()`, the handler of `Mailer` that never answers.
:::

### Using a host capability that is not granted (U3012)

:::mistake
In the step of [An end-of-day stock export](#an-end-of-day-stock-export), remove `"clock"` from `[run] grants`:

```diff include="steps/06-host..mistakes/5:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -7,2 +7,2 @@
 entry = "export"
-grants = ["console", "clock", "files:src:write"]
+grants = ["console", "files:src:write"]
```

```text include="mistakes/5/expected/rendered.txt#L1,L8"
[U3012] Error: `main` uses `now` of `Clock`, which `[run] grants` does not grant
   │ Help: repair 1 (widens grant: the program then gets this host authority when it runs): grant `now` of `Clock` in `[run] grants` of `una.toml`, or with `--grant`
```

*Why:* grants are easy to forget when a `uses` line is added to `main`. The mark is on the `uses` line that is not granted, and the help line widens the grant, which is for the package's owner to decide.

*Fix:* grant `"clock"` if the program needs the time. Otherwise remove the `uses` line and the call.
:::

### An example without a fake (U3014)

:::mistake
Remove `given @log = quiet()` from the last example:

```diff include="day-to-day..mistakes/6:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -150,3 +150,2 @@
   given @mailer = mail_down()
-  given @log = quiet()
   do dispatch([Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida")])
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U3014] Error: `dispatch` needs `@log: Console[print]`, a host capability, and examples cannot use host capabilities; give it a handler with `given`
```

*Why:* in `main` the log is the console, so it seems a test could use it too. But examples are deterministic, so they never reach the host. The first diagnostic marks the `do` line and names the binding it needs. una also reports U3001 at `expect performed @log.print`, since no `given` line binds `@log`.

*Fix:* install a handler for every binding the `do` line needs, such as `quiet()` for a console.
:::

### Running an operation where its condition may not hold, edition 0.3 (U5001)

:::mistake
In the step of [A restock with a dry run](#a-restock-with-a-dry-run), place the order without the dry-run branch:

```diff include="steps/15-conditions..mistakes/7:src/restock.una" context="1" title="src/restock.una"
--- a/src/restock.una
+++ b/src/restock.una
@@ -13,4 +13,2 @@
     unit
-  else if dry_run
-    @console.print("would order 20 x {sku}")
   else
```

```text include="mistakes/7/expected/rendered.txt#L1,L12,L18"
[U5001] Error: `@supplier.order` may run where `not dry_run` is not proven
    │ Help 1: repair 1: guard the operation with `if not dry_run`
    │ Note 2: counterexample: dry_run = true, left = 4
```

*Why:* the dry-run branch looks like a nicety and is easy to drop. The header allows `order` only where `not dry_run` holds, and the verifier finds a run where it does not: the counterexample has `dry_run = true` with `left = 4`, few enough units to order. The marks show the condition in the header and the operation that may break it.

*Fix:* the repair una lists first, a guard, which the step has as its `else if dry_run` branch.
:::

## 8.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added, and a stub of what to write when there is one. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`, since canonical form decides, for example, where a short body goes.

### Exercise 1: a directory of one customer

::::exercise
Small tests often need a directory with exactly one customer. Write a handler `only(customer: Customer)` for `Customers` whose `find` gives that customer for their id and `None` for any other. The start package ends with these examples, and `una check .` reports U1001 until the handler exists:

```una include="exercises/1/start/src/notices.una#L155-L165" title="exercises/1/start/src/notices.una"
example "a directory of one customer finds that customer"
  given @customers = only(Customer(id: "C-17", name: "Rosa", email: "rosa@example.invalid", wants_notices: true))
  given @mailer = outbox()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect result == "rosa@example.invalid"

example "a directory of one customer knows no one else"
  given @customers = only(Customer(id: "C-17", name: "Rosa", email: "rosa@example.invalid", wants_notices: true))
  given @mailer = outbox()
  do notify(Shipment(order: "A-1002", customer: "C-20", carrier: "Parcelo"))
  expect fails UnknownCustomer
```

:::hint
*Hint:* start from `directory`, which has the same shape. Write `handler only(customer: Customer) for Customers`, then one line `op find(id) = …`: the operation takes the parameter names only, and its body can read the handler's parameter `customer`. `find` returns an `Option[Customer]`, so the body gives `Some(customer)` when `id == customer.id` and `None` otherwise, with an `if … then … else …` on one line.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Add the handler next to the others:

```diff include="exercises/1/start..exercises/1/answer:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -88,2 +88,6 @@
 
+--- A directory that holds one customer, for small tests.
+handler only(customer: Customer) for Customers
+  op find(id) = if id == customer.id then Some(customer) else None
+
 --- A directory that never answers.
```

`una test .` reports 8 examples passing.
:::
::::

### Exercise 2: archive every notice

::::exercise
The store keeps a copy of every notice it sends in an archive mailbox, `archive@example.invalid`, through a second mail service. The start package has `notify_and_archive`, which holds a second binding of `Mailer`, `@archive`, and does not use it yet:

```una include="exercises/2/start/src/notices.una#notify_and_archive" title="exercises/2/start/src/notices.una"
--- Sends the notice, then a copy of it to the store's archive mailbox. Exercise 2: send the copy.
pub notify_and_archive(shipment: Shipment) -> Text
  uses @customers: Customers[find]
  uses @mailer: Mailer[send]
  uses @archive: Mailer[send]
  fails NoticeError
=
  notify(shipment)
    if error pass
```

and two examples: a notice that was sent is archived, and one that was not sent is not.

```una include="exercises/2/start/src/notices.una#L165-L179" title="exercises/2/start/src/notices.una"
example "every notice sent is archived"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  given @archive = outbox()
  do notify_and_archive(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect result == "rosa@example.invalid"
  expect performed @archive.send

example "a notice that was not sent is not archived"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  given @archive = outbox()
  do notify_and_archive(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect fails MailDown
  expect not performed @archive.send
```

:::hint
*Hint:* keep the address that `notify` returns with `let`, then send the copy on `@archive`. A failure of the archive should not undo a notice that was already sent, so handle it with `if error use unit`.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/2/start/expected/commands/test.txt#L8-L10,L13"
example notices "every notice sent is archived" ... FAILED
  src/notices.una:171: expect performed @archive.send
  the trace has no `@archive.send`
8 examples: 7 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Replace the body:

```diff include="exercises/2/start..exercises/2/answer:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -50,3 +50,3 @@
 
---- Sends the notice, then a copy of it to the store's archive mailbox. Exercise 2: send the copy.
+--- Sends the notice, then a copy of it to the store's archive mailbox.
 pub notify_and_archive(shipment: Shipment) -> Text
@@ -57,4 +57,7 @@
 =
-  notify(shipment)
+  let address = notify(shipment)
     if error pass
+  @archive.send("archive@example.invalid", subject: "Notice for order {shipment.order}", body: "sent to {address}")
+    if error use unit
+  address
 
```

The two bindings have the same capability and different names, so an example installs a different fake for each, and `expect performed @archive.send` tells them apart.
:::
::::

### Exercise 3: a dry run (edition 0.3)

::::exercise
Before a big batch, the operator wants a rehearsal that sends nothing. The start package switches to edition `0.3` and adds `rehearse`, whose header allows `send` only where `not dry_run` holds:

```una include="exercises/3/start/src/notices.una#rehearse" title="exercises/3/start/src/notices.una"
--- Like `dispatch`, but a dry run only logs what it would send. Exercise 3: make the dry run
--- send nothing.
pub rehearse(shipments: List[Shipment], dry_run: Bool) -> Unit
  uses @customers: Customers[find]
  uses @mailer: Mailer[send where not dry_run]
  uses @log: Console[print]
=
  dispatch(shipments)
```

Its body calls `dispatch` in every case, so `una check .` reports:

```text include="exercises/3/start/expected/rendered.txt#L1"
[U5001] Error: `@mailer.send` may run where `not dry_run` is not proven
```

The start package also has two examples: a dry run performs `@log.print` and not `@mailer.send`, and a real run performs `@mailer.send`.

:::hint
*Hint:* replace the body with an `if dry_run` that has two branches. In the dry-run branch, loop over the shipments with `for` and log one line per shipment on `@log`, such as `would notify A-1001`, and call nothing that uses `@mailer`. In the `else` branch, call `dispatch(shipments)` as before: there the verifier knows `dry_run` is false, which proves the condition.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Branch on `dry_run`:

```diff include="exercises/3/start..exercises/3/answer:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -76,4 +76,3 @@
 
---- Like `dispatch`, but a dry run only logs what it would send. Exercise 3: make the dry run
---- send nothing.
+--- Like `dispatch`, but a dry run only logs what it would send.
 pub rehearse(shipments: List[Shipment], dry_run: Bool) -> Unit
@@ -83,3 +82,7 @@
 =
-  dispatch(shipments)
+  if dry_run
+    for shipment in shipments
+      @log.print("would notify {shipment.order}")
+  else
+    dispatch(shipments)
 
```

In the `else` branch, `dry_run` is false, so the verifier proves the condition at the call of `dispatch`.
:::
::::

## 8.10 Recap and reference

### For agents

:::agents
`una --json check .` reports the capability diagnostics of this chapter, the U3xxx codes, in the domain `authority`. For [forgetting to hand over a binding](#forgetting-to-hand-over-a-binding-u3001):

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U3001","severity":"error","domain":"authority","message":"`dispatch` needs `@log: Console[print]`, which is not in scope here","primary":{"file":"src/notices.una","start":{"line":110,"col":3},"end":{"line":110,"col":20}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"widens":{"kind":"authority","cost":"the function then holds this authority, and every caller must hold it too: check that the operation belongs to this function's job"},"description":"declare `uses @log: Console[print]` in the header","edit":{"file":"src/notices.una","start":{"line":106,"col":32},"end":{"line":106,"col":32},"replacement":"\n  uses @log: Console[print]"}}],"explain":"una explain U3001"}],"fixable":0}
```

A repair that gives a function more authority carries `widens`, with its kind (`authority`, or `grant` for U3012) and its cost, and ranks after the repairs that keep authority. `una fix` skips the repairs that widen:

```text include="mistakes/1/expected/commands/fix.txt"
$ una fix --dry-run .
skipped src/notices.una:106:32 U3001 declare `uses @log: Console[print]` in the header: widens authority
```

The compact rule: *every effect is `@binding.op(...)` on a binding of the header's `uses`; bindings pass by name or through `with`; `main` gets only the granted host capabilities; examples install every binding with `given`.*
:::

### Recap

:::recap
- A function's `uses` list everything it may do outside the program. A `pub` function without `uses` is pure.
- List the operations a function needs in brackets. A callee holds only the operations its own header lists.
- Bindings pass by name. `with @x = @y` rebinds, and `with @x = handler(args)` installs a handler, for one statement.
- The host's capabilities reach `main` only as `una run` grants them: `[run] grants` in `una.toml`, plus any `--grant` flags of that run.
- Declare each outside service as a `capability`, and give it one handler for production and fakes for tests. A handler implements every operation, and is held to each operation's `ensures`.
- A capability is never a value: it moves only downward, by name or through `with`, for one statement.
- Every example installs its fakes with `given`, and checks effects with `expect performed` and `expect not performed`.
- In edition `0.3`, `where` puts a condition on an operation, and `[boundaries]` limits what outside code receives.
:::

### Reference

:::reference
- Construct pages: [`capability` and `op`](/docs/language/capabilities/capability/), [`uses`](/docs/language/capabilities/uses/), [`with`](/docs/language/capabilities/with/), [`handler`](/docs/language/capabilities/handler/), [host capabilities and grants](/docs/language/capabilities/host/), [`example`](/docs/language/examples/example/)
- Configuration: [`[run] grants`](/docs/configure/run/grants/), [`[boundaries]`](/docs/configure/boundaries/)
- Standard library: [the prelude and the host capabilities](/docs/std/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U3001](/docs/errors/U3001/), [U3002](/docs/errors/U3002/), [U3004](/docs/errors/U3004/), [U3005](/docs/errors/U3005/), [U3010](/docs/errors/U3010/), [U3011](/docs/errors/U3011/), [U3012](/docs/errors/U3012/), [U3014](/docs/errors/U3014/), [U3020](/docs/errors/U3020/), [U3021](/docs/errors/U3021/), [U5001](/docs/errors/U5001/)
- Specification: [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [requirements and examples](/docs/spec/08-requirements-and-examples/), [standard library](/docs/spec/14-standard-library/), [diagnostics and ABI](/docs/spec/13-diagnostics-and-abi/)
- Editions: [editions](/docs/editions/)
:::
