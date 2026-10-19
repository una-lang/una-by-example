---
learn: "12"
title: Capabilities
editions: ["0.2"]
codes: [U1001, U3001, U3002, U3004, U3005, U3010, U3011, U3012, U5001]
time: 50
builds: A shipping-notice service that looks customers up and emails them, through services it declares
prerequisites: ["4", "6", "7", "11"]
template: 2
nav: ["uses", "Host capabilities and grants", "Your capabilities and handlers", "with, rebinding and narrowing", "Day-to-day: shipping notices", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 12 Capabilities

A service that sends shipping notices talks to a customer directory, a mail server and a log. In most languages any function can open a connection, read a file or print, so you learn what a function touches only by reading its body and every body it calls. In Una a function can only compute unless its `uses`, written or inferred, say otherwise. Every effect outside the program goes through a capability that the header names and that the caller hands over. This chapter shows how to read and write `uses`, how a run grants the host's capabilities, how to declare services of your own with handlers, and how to pass and narrow authority from one function to the next.

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
- run the same code against another service by installing another handler.
:::

## Why it works this way

In a language with **ambient authority**, where code may act outside the program without being handed the right, any line of any library can reach the network, the file system or the clock. That is convenient until you review a change. A new dependency, or a helper three calls deep, can start sending data somewhere, and nothing in the signatures shows it. Tests have the same problem. A function that reaches for a global client is hard to run against a stand-in.

Una has no ambient authority. Three rules replace it:

:::steps
1. **A capability is the only way out of the program.** Printing, reading a file, asking the time or calling a service are operations on a capability, written `@name.operation(...)`.
2. **A header lists the capabilities a function uses.** `uses @mailer: Mailer[send]` names a binding, `@mailer`, its capability, `Mailer`, and the operations allowed, `send`. A function's effects, including those of every function it calls, stay within its `uses`.
3. **Authority moves only downward, by name.** A caller hands its bindings to a callee, under the callee's names, with `with`. A capability reference is not a value: it cannot be stored, returned or passed as an ordinary argument.
:::

The cost is a line in the header for each capability. In return, a reviewer reads what a function may do from its header, the checker holds every body to it, and the same code runs against another service by installing another handler.

> [!KEY]
> A function's `uses`, written or inferred, are the complete list of what it may do outside the program. A `pub` function writes them all, and one with no `uses` is pure: it can only compute its result. The host's capabilities reach `main` only as `una run` grants them: in `[run] grants` of `una.toml`, or with a `--grant` flag.

## 12.1 Declaring what a function may do: `uses` in full

### What an effect is

Most of what a program does happens inside it: adding prices, building a line of text, choosing a branch. Some of what it does reaches outside: it prints a line on the screen, writes a file, asks the clock for the time, or sends a message to another computer. Each of these is an **effect**: something the program does to, or learns from, the world outside it. A function with no effects can only compute its result. Call it twice with the same arguments and it gives the same answer, and nothing else in the world changes.

Una treats effects as authority that must be handed out, the way a store hands out keys. A cashier's keycard opens the till and the front door, and not the stockroom or the office safe. Anyone can read on the card what it opens, and nobody gets in anywhere without one. [Chapter 1](/learn/hello/#s1-5) used one such card, the console. This chapter names every part, and uses these words throughout:

- A **capability** is the authority to do one kind of thing outside the program, such as printing to the console or reading the clock. `Console` and `Clock` are capabilities.
- An **operation** is one thing a capability can do: `print` is an operation of `Console`, and `now` is an operation of `Clock`.
- A **binding** is the name a function uses for a capability it holds. It always starts with `@`, as in `@console`. You perform an operation on a binding: `@console.print("…")`.
- A **`uses` clause** is a line of a function's header that names a binding, its capability, and the operations the function may perform with it: `uses @console: Console[print]`.

The `uses` clauses of a header are the function's keycard: the complete list of what it may do outside the program. Each step of this chapter is a package, made as [chapter 2](/learn/numbers/#each-step-is-a-package) explains, and the manifest of a step that prints grants the console, as [section 12.2](#s12-2) explains.

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

You met U3004 in [section 1.5](/learn/hello/#s1-5) and [section 6.3](/learn/functions/#s6-3). Read it now as a reviewer would. The message names the binding, `@console`, and the reason: the function "declares no `uses`, so it is pure". The mark points at `@console` in the body. The help line is the repair: declare a `uses` line in the header. It is marked "widens authority", because the repair gives the function more power, and every caller must then hold that power too. Whether the function should print is a decision for its author, so the checker does not make it.

So a header that says nothing about effects is a promise: the function has none. A header that lists `uses @console: Console[print]` is a promise too: the function may print, and do nothing else outside the program. The checker holds every body to its header, so a reviewer learns what a function may do from the header alone.

### How to write `uses`

#### The parts of a `uses` line

A `uses` clause sits under the header, with the other clauses, before `=`. Take `uses @files: Files[read, write]`:

1. **`uses`** starts the clause.
2. **`@files`** is the binding: the name the body uses for the capability. You choose it. `@files` is the usual name for `Files`, and a name such as `@audit` can say what a capability is for.
3. **`: Files`** is the capability.
4. **`[read, write]`** lists the operations the function may perform, separated by commas.

A function written in the long form ([section 6.2](/learn/functions/#s6-2)) has its clauses on their own lines, each indented two spaces. When a function has several kinds of clause, they go in this order: `requires`, `ensures`, `uses`, `fails`, then `derived from`.

The step of this part shows every form. It is a small back room of a store: it announces restocked items, and it saves a count to a file. Its manifest grants the console and the files of `src/`, which [section 12.2](#s12-2) explains:

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

Both operations of `Files` can fail, with `FileError`, so `copy_count` declares `fails FileError` and passes each failure on with `if error pass`, as [section 7.3](/learn/failure/#s7-3) shows.

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

#### No `uses` line on a private function

A private function may leave its `uses` out, and the checker infers them, as [section 6.3](/learn/functions/#s6-3) shows: the fewest that cover its body and the functions it calls. The back room has one such function, `close_shelf`, which the check-yourself question of this section asks about.

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

A call hands the callee the bindings its header asks for, by name, never by type. If `print_line` asked for `@out: Console[print]`, the call in `main` would not check: `main` holds a `@console`, not an `@out`. [Section 12.4](#s12-4) shows how to hand a binding over under another name, and [forgetting to hand over a binding](#forgetting-to-hand-over-a-binding-u3001) shows the diagnostic, U3001.

#### A caller holds at least what its callees use

A caller must hold every binding its callees need, with at least the operations they list. `main` may call `print_line` because it holds `@console` with `print`. A function that holds `Customers[find]` cannot call one that needs `Customers[forget]`: that is U3002, which [using an operation the header does not list](#using-an-operation-the-header-does-not-list-u3002) shows. So the effects of a function include the effects of every function it calls, and its header covers them all.

#### Written or inferred, the header is exact

A `pub` function writes every `uses` itself, and one with no `uses` is pure. A private function with no `uses` line gets the inferred ones, and may do exactly that much. A private function that writes at least one `uses` line has exactly the ones it writes: nothing more is inferred for it. This book writes `uses` on private functions too whenever their effects are part of what a reader should know.

### How many operations to allow

:::decide
**Which to use:**

| You want… | Write |
| --- | --- |
| A function that only computes | No `uses` |
| One operation of a capability | `uses @x: C[op]` |
| Several operations | `uses @x: C[op1, op2]` |
| Every operation, now and when the capability gains more | `uses @x: C`, without brackets |
| A private helper whose effects are obvious from its body | No `uses` line; let the checker infer it |
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

Which `uses` and which `fails` does the checker infer for it?

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

A second one: may `announce_all` call `copy_count`, without changing its header?

:::answer Show the answer
No. `copy_count` needs `@files` with `read` and `write`, and `announce_all` holds only `@console`. A caller must hold every binding its callees use, so `una check .` reports U3001 at the call: `copy_count` needs `@files`, "which is not in scope here". To make the call, `announce_all` would have to declare `uses @files: Files[read, write]` too, and handle or declare the `FileError` of the call, and every caller of `announce_all` would then need them as well.
:::

## 12.2 The host's capabilities and grants

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

They are in scope in every module, with no `import`. But a function can hold one only if its caller hands it over, and the first caller of all is `main`. `main` gets its host capabilities from `una run`, and only those that the run **grants**.

### What a grant is

A grant is the permission, written down, for the program to use a host capability when it runs. You have written one since chapter 1. The program that says the store is open has this manifest:

```toml include="steps/04-hello/una.toml" title="steps/04-hello/una.toml"
[package]
name = "hello"
version = "0.1.0"
edition = "0.2"

[run]
entry = "hello"
grants = ["console"]
```

`una run .` prints:

```text include="steps/04-hello/expected/output.txt"
The store is open
```

The two halves work together. The `uses @console: Console[print]` line of `main` is a promise to callers and reviewers: this function prints, and does nothing else outside the program. The line `grants = ["console"]` is the package's decision, in its manifest, about what a run may do: this run may print. A store's keycard works the same way: the card lists the doors, and the building still decides which doors are open tonight.

### Why a program needs grants

You run programs you did not write: a tool from a colleague, a package from the internet, an example from a book. Its header says what it may do, but the header is part of the program, written by its author. The grants are what the package's manifest, or the person at the command line, allows the run to do.

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

The message is U3012: `main` uses `write` of `Files`, "which `[run] grants` does not grant". The mark points at the `uses` line of `main`. The help line offers a repair that "widens grant": add the grant to `una.toml`. The people who maintain the package decide whether to, and the decision shows in review, as a changed line of the manifest.

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
| `"env"` | `Env` |
| `"keys:<keyfile>"` | `Keys`, with the secret keys read from that file |
| `"http:<origin>"` or `"http:<origin>:<methods>"` | `Http`, toward that origin only, such as `https://api.example.invalid`, and only those methods when they are listed (edition `0.2`) |

A `Files` grant always carries a directory and a mode, so it says where the program may read or write, and which of the two.

#### `--grant` on the command line

`una run` also takes grants as flags, one per capability, such as `--grant clock` after `una run .`. They count for that run only, and nothing records them. Prefer the manifest: it is reviewed with the code.

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
3. **`attempt @files.write("stock-export.csv", content: content)`.** `Files.write` can fail with `FileError` (`NotFound`, `Denied` or `Io`). `attempt` keeps the outcome, as in [section 7.4](/learn/failure/#s7-4), and the `when` reports either case.
4. **`"files:src:write"`.** The path `stock-export.csv` resolves inside `src/`, the directory of the grant.
:::

`una run .` prints:

```text include="steps/06-host/expected/output.txt"
export written: 3 lines
```

and leaves the export in `src/stock-export.csv`. The time in it changes on every run, so the program does not print it.

### How grants behave

#### What `una check` and `una run` compare

When `una.toml` lists grants under `[run]`, `una check` compares them with the `uses` of `main`: a host operation that the grants do not cover is U3012, as [Why a program needs grants](#why-a-program-needs-grants) showed.

`una run` grants the union of `[run] grants` and its `--grant` flags, for that run only, and it checks the `uses` of `main` against that union before anything runs: a host operation that neither grants is U3012 there too, and the program does not start. `una check` takes no `--grant` flag, so it reads only the manifest. A package whose manifest has no `grants` line gives `una check` no list to compare with, so its check passes. Whatever the manifest says, `una run .` stops with U3012 before anything runs when a host operation of `main` is not granted, until a grant is added in `una.toml` or with `--grant`. A package whose `grants` list lacks `"clock"`, as in [Using a host capability that is not granted](#using-a-host-capability-that-is-not-granted-u3012), fails `una check`, yet `una run . --grant clock` runs it. What a run may do is the manifest plus the command line, so read both.

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
> `Files.read` returns `internal Text`, and `Env.get` returns `internal` values too. `Clock.now` returns a public `Int`. A label says how sensitive data is, and the console accepts only `public` data. So the program can write what it read to a file, as the back room of [section 12.1](#s12-1) does, but cannot print it without a declared policy. [Chapter 17](/learn/information-flow/) explains labels and how to release data legitimately.

### Which grant to give

:::decide
**Which to use:**

| The program… | Grant |
| --- | --- |
| Prints | `"console"` |
| Reads the time | `"clock"` |
| Reads its input files | `"files:<dir>:read"`, on the directory that holds them |
| Writes its output | `"files:<dir>:write"`, on a directory of its own |
| Needs a capability for one run only, such as a trial of a new feature | `--grant` on that run |
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

## 12.3 Your own capabilities and handlers

### What a capability you declare is

The host capabilities cover the machine: the screen, the clock, the files. A store's program also talks to services of its own: a mail service, a payment provider, a customer directory, an inventory, a scale at the packing desk. In Una each of these is a capability that you declare, and it comes in two parts:

- A **`capability` declaration** lists what the service can do: its operations, each with the types it takes and gives back, and how it can fail. It holds no code.
- A **`handler`** gives those operations their code: one way to provide the service. A capability can have many handlers, such as one that talks to the real service, one that prints what it would send, and one that always fails.

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

```una include="steps/09-handlers/src/receipts.una#MailError..Mailer" title="steps/09-handlers/src/receipts.una"
--- How the mail service can fail.
kind MailError = Bounced(address: Text) | Timeout

--- The mail service: what it can do, with no code.
capability Mailer
  op send(to: Text, subject: Text) -> Unit
    fails MailError
```

#### An operation that can fail: `fails`

A clause under an operation, indented two spaces more, says how it can fail. `fails MailError` works exactly as on a function ([section 7.2](/learn/failure/#s7-2)): a caller handles the failure with a clause or passes it on.

#### An operation with a contract: `requires` and `ensures`

An operation can carry the contracts of [chapter 5](/learn/contracts/). The scale at the packing desk takes a SKU of at least four characters, and promises a weight of at least 1 gram:

```una include="steps/10-scale/src/scales.una#ScaleError..Scale" title="steps/10-scale/src/scales.una"
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

`requires` is what every caller must prove at the call. `ensures` is what every caller may rely on. For a service outside the program, an `ensures` is an assumption: the verifier checks every handler written in Una against it, and trusts the real service to keep it.

#### What an operation accepts: `accepts`

A fourth clause, `accepts`, states the most sensitive data the operation may receive. [Chapter 17](/learn/information-flow/) explains it.

#### A capability for other modules: `pub capability`

Like a function or a kind, a capability can be used outside its module only when it is declared `pub` ([section 11.2](/learn/packages/#s11-2)): `pub capability Mailer`. The day-to-day program of [section 12.5](#s12-5) declares its services `pub`.

### How to write a handler

#### The handler and its operations

A handler is the word `handler`, a name, parameters in parentheses, `for` and the capability it implements. Under it, one `op` line per operation of the capability, each with the operation's name, its parameter names, `=` and the body:

```una include="steps/10-scale/src/scales.una#fixed" title="steps/10-scale/src/scales.una"
--- A scale on a developer's machine: it weighs every item at the same weight.
handler fixed(grams: Int) for Scale
  op weigh(sku) = if grams < 1 then fail NotOnScale else grams
```

The operation's parameters take their names only: their types and the result type come from the capability. The body is ordinary Una code. Here it fails with a variant of the operation's error kind when the fixed weight makes no sense, and returns the weight otherwise.

#### Handler parameters

`fixed(grams: Int)` has a parameter, as a function does. Its value is given when the handler is installed, and every operation of the handler can read it: `weigh` returns `grams`. A handler with no parameters is written with empty parentheses, as `bouncing()`.

#### A handler with capabilities of its own

A handler may declare `uses` lines, under its first line. A mail service for a developer's machine prints each message, so it holds the console:

```una include="steps/09-handlers/src/receipts.una#printed" title="steps/09-handlers/src/receipts.una"
--- A mail service for a developer's machine: it prints each message instead of sending it.
handler printed(prefix: Text) for Mailer
  uses @console: Console[print]
  op send(to, subject) = @console.print("{prefix} to {to}: {subject}")
```

The code that installs the handler must hold those capabilities.

#### Installing a handler: `with`

A handler runs only where it is installed. `with @scale = fixed(850)`, at the end of a statement, installs the handler for the call in that statement:

```una include="steps/10-scale/src/scales.una#parcel_grams..main" title="steps/10-scale/src/scales.una"
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

`parcel_grams` holds `@scale: Scale[weigh]`. It never learns which handler answers; `main` chooses. The step prints:

```text include="steps/10-scale/expected/output.txt#L1"
Ok(1000)
```

The weight is the item's 850 grams and the box's 150. `parcel_grams` promises at least 151 grams, and the verifier proves it from the operation's `ensures result >= 1`, without knowing any handler. [Section 12.4](#s12-4) covers every form of `with`.

### Receipts by email

Now the mail service, with two handlers. On a developer's machine the mail service prints each message instead of sending it, and a second handler stands for a service that refuses every address:

:::steps
```una include="steps/09-handlers/src/receipts.una" title="steps/09-handlers/src/receipts.una" verified="check, run"
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

```text include="steps/09-handlers/expected/output.txt"
[mail] to rosa@example.invalid: Receipt for order A-1001
second receipt: Err(Bounced("tomas@example.invalid"))
```

The second line comes from `attempt` with the `bouncing` handler: the receipt was not sent, and the outcome says why.

### Recovering with a default from a service

A service can fail, and the clauses of [section 7.3](/learn/failure/#s7-3) handle the failure of an operation as they handle any call's. Most code passes the failure on, but sometimes carrying on is the right behavior. A product page must show how many units a customer may order, even when the inventory service does not answer, and it must never promise stock it cannot confirm:

:::steps
```una include="steps/11-orderable/src/orderable.una" title="steps/11-orderable/src/orderable.una" verified="check, run"
module orderable

--- How the inventory service can fail.
kind StoreError = | Timeout

--- The inventory service: how many units of a SKU are on hand, or `None` for a SKU it does not
--- stock.
capability Inventory
  op on_hand(sku: Text) -> Option[Int]
    fails StoreError

--- How many units of a SKU a customer may order on the product page. The page must show a
--- number even when the inventory does not answer, and must never promise stock it cannot
--- confirm, so a failure and an unknown SKU both give 0.
orderable(sku: Text) -> Int
  uses @inventory: Inventory[on_hand]
=
  let units = @inventory.on_hand(sku)
    if error use None
    if none use 0
  units

--- An inventory held in memory: the units on hand of each SKU.
handler warehouse(stock: Map[Text, Int]) for Inventory
  op on_hand(sku) = stock.get(key: sku)

--- An inventory that never answers.
handler offline() for Inventory
  op on_hand(sku) = fail Timeout

--- Prints what the product page offers for three SKUs, then for one while the inventory is
--- offline.
pub main() -> Unit
  uses @console: Console[print]
=
  let stock = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)
  for sku in ["LAMP-01", "DESK-02", "CHAIR-09"]
    let units = orderable(sku) with @inventory = warehouse(stock)
    @console.print("{sku}: up to {units}")
  let later = orderable("LAMP-01") with @inventory = offline()
  @console.print("LAMP-01, inventory offline: up to {later}")
```

1. **`kind StoreError = | Timeout`.** How the inventory can fail. A sum kind with one variant starts with `|`.
2. **`op on_hand(sku: Text) -> Option[Int]` with `fails StoreError`.** The operation gives two kinds of answer and one failure: `Some(units)` for a SKU it stocks, `None` for a SKU it does not, and `Timeout` when it does not answer.
3. **`if error use None`, then `if none use 0`.** Two clauses on one call, read top to bottom. First, a failure of the call becomes the value `None`. Then `None`, from either source, becomes `0`.
4. **`handler warehouse(stock: Map[Text, Int]) for Inventory`.** An inventory held in a map ([section 10.4](/learn/collections/#s10-4)), passed when the handler is installed. `stock.get(key: sku)` already gives an `Option[Int]`.
5. **`handler offline() for Inventory`.** An inventory that never answers.
6. **`with @inventory = warehouse(stock)` inside a `for`.** Each turn of the loop installs the handler for its own call of `orderable`.
:::

`una run .` prints:

```text include="steps/11-orderable/expected/output.txt"
LAMP-01: up to 4
DESK-02: up to 1
CHAIR-09: up to 0
LAMP-01, inventory offline: up to 0
```

`orderable` has no `fails` line, and it needs none: no failure leaves it. Its header promises callers a number, always. `CHAIR-09` is not in the map, so the warehouse gives `None`, and the page offers 0; with `offline()`, the failure becomes 0 too.

### How handlers behave

#### A handler implements every operation

A handler must implement every operation of its capability, with the same names and the same number of parameters. Give the scale a second operation, `tare`, which sets it to zero, and leave the handler as it was:

```una include="steps/12-missing-op/src/scales.una#Scale..fixed" title="steps/12-missing-op/src/scales.una"
--- The scale at the packing desk: it weighs, and it can be set to zero.
capability Scale
  op weigh(sku: Text) -> Int
  op tare() -> Unit

--- A scale that only weighs.
handler fixed(grams: Int) for Scale
  op weigh(sku) = grams
```

```text include="steps/12-missing-op/expected/rendered.txt"
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

```diff include="steps/10-scale..steps/13-broken-promise:src/scales.una" context="1" title="src/scales.una"
--- a/src/scales.una
+++ b/src/scales.una
@@ -26,3 +26,3 @@
 handler fixed(grams: Int) for Scale
-  op weigh(sku) = if grams < 1 then fail NotOnScale else grams
+  op weigh(sku) = grams
 
```

```text include="steps/13-broken-promise/expected/rendered.txt"
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

The diagnostic is U5001, the refuted postcondition of [section 5.2](/learn/contracts/#s5-2). The marks show the promise, `ensures result >= 1` on the operation, and the body that breaks it, `grams`. The counterexample, `grams = 0`, is a scale installed with a weight of 0. Callers rely on the promise, so a handler that breaks it does not check.

#### A handler is not a value

> [!TIP]
> A handler is not a value. It cannot be stored in a variable, passed as an ordinary argument or returned. It exists only where `with` installs it, and its parameters are fixed there.

An example installs one too, with a `given` line, as [section 12.6](#s12-6) shows.

#### Every capability is in the report

The `authority:` part of `una report .` ([section 6.3](/learn/functions/#s6-3)) lists your own capabilities as it lists the host's. Two more parts are for capabilities you declare. Under `handler authority`, the report lists what each handler may use. Under `assumptions`, it lists each capability the package declares, with its operations, since the program assumes that each service does what its declaration says:

```text include="steps/09-handlers/expected/commands/report.txt#L6-L10,L13-L14"
authority:
  receipts.main (pub): @console: Console[print]
  receipts.send_receipt (private): @mailer: Mailer[send]
handler authority:
  receipts.printed for receipts.Mailer (private): @console: Console[print]
assumptions:
  receipts.Mailer: send
```

### A capability, a host capability or a pure function

:::decide
**Which to use:**

| The code needs… | Use |
| --- | --- |
| Only to compute a value from its arguments | A pure function, with no `uses` |
| The screen, the clock, the files or the network of the machine | A host capability, granted to `main` |
| A service of the business, such as mail, payments or a directory | A `capability` of your own, with a handler for each way to provide it |
| To keep working when a service fails | A clause on the operation's call, such as `if error use` |
| Another provider of the same service, for a trial run or a developer's machine | Another handler of the same capability |
:::

A capability of your own costs a declaration and a handler. It pays back as soon as the service has two providers, which it does the day you run it on a developer's machine or write a test.

### Check yourself: handlers

`main` in the scale's step makes a second call, with a scale installed at a weight of 0:

```una include="steps/10-scale/src/scales.una#main" title="steps/10-scale/src/scales.una"
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
```text include="steps/10-scale/expected/output.txt#L2"
Err(NotOnScale)
```

`fixed(0)` takes the `then` branch of its test, `grams < 1`, and fails with `NotOnScale`. `parcel_grams` passes the failure on with `if error pass`, and `attempt` in `main` keeps it as `Err(NotOnScale)`.
:::

A second one, without code: a handler `free()` for `Scale` has `op weigh(sku) = 0`. Does it check?

:::answer Show the answer
No. `weigh` promises `result >= 1`, and 0 breaks it, so the verifier refutes the operation with U5001, as in [A handler is held to the operation's contract](#a-handler-is-held-to-the-operations-contract).
:::

## 12.4 Passing authority: `with`, rebinding and narrowing

### What passing authority means

A capability moves from a caller to a callee, and only that way. A store manager lends a colleague a key for one errand: the colleague uses it for that errand and hands it back. They cannot copy it, keep it in a drawer, or give it to a stranger. In Una, the caller is the manager, the callee is the colleague, and the errand is one call.

Three things can happen at a call:

- **By name.** The callee's header asks for `@customers`, and the caller holds a `@customers`. It is handed over with nothing written at the call.
- **Rebinding.** The callee asks for `@audit`, and the caller holds the same capability under another name, `@console`. `with @audit = @console` hands it over under the callee's name.
- **Installing.** The caller holds no such capability, or wants another provider. `with @customers = directory(customers)` installs a handler.

And whatever the callee receives, it may use only the operations its own header lists: authority narrows on its way down.

A capability can also travel inside a function that is passed as an argument, such as a lambda that prints. Edition `0.2` lets a header say so, with `uses of`, as [Authority inside a function argument](#authority-inside-a-function-argument-uses-of) shows.

### Why authority moves only downward

If a capability were a value, a function could keep it: store it in a record, return it, or pass it to code that its header never mentions. A reviewer would then have to follow every value to know who can print or send mail. Una forbids it. Try to keep the console in a variable:

```una include="steps/14-stored-capability/src/slips.una" title="steps/14-stored-capability/src/slips.una"
module slips

pub main() -> Unit
  uses @console: Console[print]
=
  let saved = @console
  saved.print("Packing slip for order A-1001")
```

```text include="steps/14-stored-capability/expected/rendered.txt"
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

When the names match, write nothing. `main` holds `@console`, and `print_line` in [section 12.1](#s12-1) asks for `@console`, so `print_line("LAMP-01", quantity: 2)` passes it.

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
```una include="steps/15-with/src/accounts.una" title="steps/15-with/src/accounts.una" verified="check, run"
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
3. **`if none use Customer(id: id, name: "guest")`.** `find` returns an `Option`, so the handling clauses of [section 7.3](/learn/failure/#s7-3) apply to an operation as to any call.
4. **`uses @audit: Console[print]` on `erase`.** The audit trail is a console here, under the name `@audit`, so the header says what the console is for.
5. **`let page = greeting("C-17") with @customers = directory(customers)`.** A `with` at the end of a `let`: it installs the handler for that call. The line above it, `empty_map().with(key: …, value: …)`, is something else: the map method of [section 10.4](/learn/collections/#s10-4) that adds an entry, not the `with` clause.
6. **`with @customers = directory(customers), @audit = @console`.** Two bindings. The first installs a handler. The second is a rebinding: the callee's `@audit` is the caller's `@console`. `main` holds no `@audit` of its own, so without the rebinding the call would not check.
:::

`una run .` prints:

```text include="steps/15-with/expected/output.txt"
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

A handler installed with `with` takes its own `uses` from the code around the statement, by name. `printed`, in [section 12.3](#s12-3), holds `@console` because `main`, which installs it, holds `@console`.

#### A binding of the wrong capability

A rebinding needs the same capability on both sides, and a handler must implement the capability the callee needs at that name. Installing a `Customers` handler as `@mailer` is U3010, as [installing a handler of another capability](#installing-a-handler-of-another-capability-u3010) shows.

#### Checking that authority narrows

> [!IMPORTANT]
> Narrowing is a promise you can check. Because `greeting` holds `Customers[find]`, no change to its body can make it erase a customer without a change to its header, which a reviewer sees.

### Authority inside a function argument: `uses of`

#### What a function argument may carry

A function can take another function as an argument ([section 10.2](/learn/collections/#s10-2)): `each_sku` below runs an `action` once for each SKU of a shelf. The function it receives, often a lambda, may do something outside the program, such as print a label. Then the effect happens inside `each_sku`, so its header must say so.

#### Why the parameter's type is not enough

The type `fn(Text) -> Unit` says nothing about effects, and a function type with no `uses` is pure. Pass a lambda that prints:

```una include="steps/16-pure-parameter/src/shelf.una" title="steps/16-pure-parameter/src/shelf.una"
module shelf

--- Runs `action` once for each SKU of a shelf. Its parameter's type says nothing about
--- effects, so `action` must be pure.
pub each_sku(skus: List[Text], action: fn(Text) -> Unit) -> Unit
=
  for sku in skus
    action(sku)

pub main() -> Unit
  uses @console: Console[print]
=
  each_sku(["LAMP-01", "DESK-02"], action: fn(sku) -> @console.print("label {sku}"))
```

```text include="steps/16-pure-parameter/expected/rendered.txt"
[U3004] Error: `@console` is used in a lambda whose type declares no `uses`, so the lambda is pure; pass it directly as an argument for a parameter whose type or `uses of` clause allows the effect
    ╭─[ src/shelf.una:13:55 ]
    │
 13 │   each_sku(["LAMP-01", "DESK-02"], action: fn(sku) -> @console.print("label {sku}"))
    │                                                       ────┬───
    │                                                           ╰───── `@console` is used in a lambda whose type declares no `uses`, so the lambda is pure; pass it directly as an argument for a parameter whose type or `uses of` clause allows the effect
    │
    │ Note: run `una explain U3004` for an explanation
────╯
```

U3004 marks `@console` inside the lambda: the lambda's type comes from the parameter, `fn(Text) -> Unit`, which declares no `uses`, so the lambda is pure. The message also names the way out: a parameter "whose type or `uses of` clause allows the effect". Writing `uses @console: Console[print]` on `each_sku` would be wrong too: `each_sku` does not print, its argument does, and another caller may pass an action that writes a file instead.

#### How to write `uses of`

`uses of action` means "this function may do whatever `action` does". It is the twin of `fails of action`, which [section 7.2](/learn/failure/#s7-2) taught: "this function fails as `action` fails". `uses of` goes among the `uses` lines, and `fails of` goes where `fails` goes. Both exist from edition `0.2` on. The parameter's type is written without `uses` or `fails` of its own:

```una include="steps/17-uses-of/src/shelf.una" title="steps/17-uses-of/src/shelf.una" verified="check, run"
module shelf

--- Runs `action` once for each SKU of a shelf. It may do what `action` does, and fails as
--- `action` fails.
pub each_sku(skus: List[Text], action: fn(Text) -> Unit) -> Unit
  uses of action
  fails of action
=
  for sku in skus
    action(sku)
      if error pass

--- Saves a shelf label to a file of its own.
save_label(sku: Text) -> Unit
  uses @files: Files[write]
  fails FileError
=
  @files.write("{sku}.txt", content: "label {sku}")
    if error pass

pub main() -> Unit
  uses @console: Console[print]
  uses @files: Files[write]
=
  each_sku(["LAMP-01", "DESK-02"], action: fn(sku) -> @console.print("label {sku}"))
  let saved = attempt each_sku(["LAMP-01", "DESK-02"], action: save_label)
  @console.print("saved: {saved}")
```

`una run .` prints:

```text include="steps/17-uses-of/expected/output.txt"
label LAMP-01
label DESK-02
saved: Ok(unit)
```

#### How it behaves

- **The caller pays.** At each call, the effects of `each_sku` are its own `uses` plus those of the argument given for `action`. The first call in `main` prints, so `main` must hold `@console`; the second saves files, so `main` must hold `@files`. Each lambda runs on the bindings of the code where it is written.
- **A named function works too.** The second call passes `save_label` by its name. It writes a file and can fail with `FileError`, and `main` holds `@files`, so the call checks.
- **One error kind.** `fails of action` lets `each_sku` fail with whatever the argument fails with: nothing for the printing lambda, `FileError` for `save_label`, which `attempt` keeps as a value.
- **Nothing escapes.** Inside `each_sku`, `action` may only be called, or passed on to a parameter that is itself named by an `of` clause. It cannot be stored or returned, so the authority it carries never outlives the call.
- **Private functions infer it.** A private function without `uses` gets `uses of p` inferred for a function parameter `p` that its body only calls.

### Pass, rebind or install

:::decide
**Which to use:**

| At the call… | Write |
| --- | --- |
| The caller holds the capability under the callee's name | Nothing |
| The caller holds it under another name | `with @callee_name = @caller_name` |
| The caller must choose a provider, or holds none | `with @x = handler(args)` |
| The caller wants the callee to use fewer operations | Nothing: the callee's header already limits it |
| The callee runs a function it is given, which may have effects | `uses of p` and `fails of p` on the callee (edition `0.2`) |
:::

Name bindings after what they are for, as `@audit` and `@log` are. A rebinding at the call then reads as a decision: "the audit trail is the console, here".

Edition `0.3` adds limits on top of these rules: a condition on an operation, such as "never in a dry run", a narrower rebinding at the call, and a ceiling on what a module may receive. [Chapter 13](/learn/authority/) teaches them.

### Check yourself: `with`

In the step, remove `@audit = @console` from the last line of `main`, so that it reads `erase("C-20") with @customers = directory(customers)`. Does it check?

:::answer Show the answer
No. `erase` needs `@audit: Console[print]`, and `main` holds no binding named `@audit`: bindings are found by name, never by type, so `@console` does not count. `una check .` reports U3001 at the call, as [forgetting to hand over a binding](#forgetting-to-hand-over-a-binding-u3001) shows for the day-to-day program.
:::

A second one: `main` in [Authority inside a function argument](#authority-inside-a-function-argument-uses-of) gives `each_sku` the function `save_label`, which writes files. Remove `uses @files: Files[write]` from the header of `main`. Does it check?

:::answer Show the answer
No. With `uses of action`, a call of `each_sku` performs the effects of its argument, so the second call writes files on behalf of `main`, through `save_label`, which needs `@files`, and `main` no longer holds it. `una check .` reports U3001, as for any binding that is not in scope: authority still comes only from the caller's header.
:::

## 12.5 Day-to-day: shipping notices

### What the dispatch step must do

Now the program from the start of the chapter. When orders leave the warehouse, the store emails each customer a notice. The customer directory and the mail service are services on the network, which can time out. The operator reads a log with one line per order. Each part of the job uses one idea of this chapter:

| Part of the job | How the program does it |
| --- | --- |
| Talk to the directory and the mail service | two capabilities of its own, `Customers` and `Mailer` ([section 12.3](#s12-3)) |
| Write the notice's text | a pure function, with no `uses` ([section 12.1](#s12-1)) |
| Send one notice, and nothing else | a header with exactly two operations |
| Run a batch and log each outcome | a header with a third binding, `@log`, which `main` rebinds to the console ([section 12.4](#s12-4)) |
| Run with stand-in services | handlers, installed with `with` |
| Print at all | the one grant of `una.toml`, `"console"` ([section 12.2](#s12-2)) |

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

`notice` has no `uses`, and it is `pub`, so it cannot reach any service. An example can test it with values alone.

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

`dispatch` calls the log `@log`, not `@console`. The name says what the binding is for, and the caller decides what it is: the console in `main`, or one day a log service with a handler of its own. `dispatch` holds the union of what it does itself and what `notify` needs, and nothing more. `una report .` lists, under `authority`, the bindings of every function, public or private, so a reviewer can read the service's whole reach in one place.

### The handlers

In production, `Customers` and `Mailer` would have handlers that call the real services over the network. Such a handler declares its own `uses`, such as the host's `Http`, and the code that installs it must hold them. The network would then appear in the header of `main` and in the grants of `una.toml`, and nowhere in `notify` or `dispatch`, which do not change. Here, `directory` holds the customers in a map, `outbox` accepts every message and delivers none, and `mail_down` and `directory_down` never answer.

```una include="day-to-day/src/notices.una#directory..directory_down" title="day-to-day/src/notices.una"
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

Compare the two calls of `dispatch` in `main`: they differ in one handler, `outbox()` or `mail_down()`. Running the same code against another service costs exactly that change, and `dispatch` and `notify` never learn which service they talk to.

> [!SECURITY]
> The log prints customers' email addresses. In a real store that is personal data, and a log is a place it should not go. [Chapter 17](/learn/information-flow/) labels the addresses `secret[PII]`, lets the checker find this line, and releases a masked form through a policy.

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

example "an unknown customer is rejected before any mail is sent"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1003", customer: "C-99", carrier: "Parcelo"))
  expect fails UnknownCustomer

example "a customer who asked for no notices is rejected before any mail is sent"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1004", customer: "C-21", carrier: "Parcelo"))
  expect fails OptedOut

example "a directory that does not answer is DirectoryDown, before any mail is sent"
  given @customers = directory_down()
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect fails DirectoryDown

example "a mail service that does not answer is MailDown"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect fails MailDown

example "the notice names the customer, the order and the carrier"
  do notice(Customer(id: "C-17", name: "Rosa", email: "rosa@example.invalid", wants_notices: true), shipment: Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect result == "Hello Rosa, your order A-1001 is on its way with Parcelo."

example "a skipped shipment says why in the log"
  do log_line(Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida"), outcome: Err(MailDown))
  expect result == "skipped  A-1005: the mail service did not answer; retry later"
```

## 12.6 Testing it

### Stand-in services for every path

An example cannot write `with`, since its `do` line is a single call. The direct way for it to install each handler its `do` line needs is a `given` line, such as `given @mailer = outbox()`, which [section 14.3](/learn/testing/#s14-3) covers in full. With the handlers of this chapter, every path of `notify` can be tested on demand: a customer who wants notices, an unknown customer, a customer who opted out, a directory that does not answer, and a mail service that does not answer.

```una include="day-to-day/src/notices.una#L110-L138" title="day-to-day/src/notices.una" caption="the examples of notify"
example "a customer who wants notices gets one"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect result == "rosa@example.invalid"

example "an unknown customer is rejected before any mail is sent"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1003", customer: "C-99", carrier: "Parcelo"))
  expect fails UnknownCustomer

example "a customer who asked for no notices is rejected before any mail is sent"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1004", customer: "C-21", carrier: "Parcelo"))
  expect fails OptedOut

example "a directory that does not answer is DirectoryDown, before any mail is sent"
  given @customers = directory_down()
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect fails DirectoryDown

example "a mail service that does not answer is MailDown"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect fails MailDown
```

The happy path expects the address with `expect result`, and each failure path names its variant with `expect fails`, as in [section 7.8](/learn/failure/#the-failure-paths-expect-fails).

### A failure that comes first

Three examples install `mail_down()` on purpose. Had `notify` sent any mail before it failed, the mail service would have failed first, and the example would see `MailDown` instead of the variant it expects. So each of them also shows that the directory's answer is checked before any mail goes out.

### The pure parts, with values alone

`notice` and `log_line` hold no binding, so their examples need no handler at all: values in, a text out.

```una include="day-to-day/src/notices.una#L140-L146" title="day-to-day/src/notices.una" caption="the examples of the pure functions"
example "the notice names the customer, the order and the carrier"
  do notice(Customer(id: "C-17", name: "Rosa", email: "rosa@example.invalid", wants_notices: true), shipment: Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect result == "Hello Rosa, your order A-1001 is on its way with Parcelo."

example "a skipped shipment says why in the log"
  do log_line(Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida"), outcome: Err(MailDown))
  expect result == "skipped  A-1005: the mail service did not answer; retry later"
```

`dispatch` prints through `@log`, and it is not tested here: an example cannot use the host's console, and checking which operations a call performed is a tool of [chapter 14](/learn/testing/).

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L10"
example notices "a customer who wants notices gets one" ... ok
example notices "an unknown customer is rejected before any mail is sent" ... ok
example notices "a customer who asked for no notices is rejected before any mail is sent" ... ok
example notices "a directory that does not answer is DirectoryDown, before any mail is sent" ... ok
example notices "a mail service that does not answer is MailDown" ... ok
example notices "the notice names the customer, the order and the carrier" ... ok
example notices "a skipped shipment says why in the log" ... ok

7 examples: 7 passed, 0 failed
```

## 12.7 Common mistakes

Most of the mistakes below are a small change to `day-to-day/src/notices.una`. The others change a step of this chapter, as each one says. The capability diagnostics are U3 codes, reported before any proof is tried. Each names the binding or the handler and what is missing, and marks the place in the code where it is needed.

### Forgetting to hand over a binding (U3001)

:::mistake
Leave `@log = @console` out of the first `with` in `main`:

```diff include="day-to-day..mistakes/1:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -105,3 +105,3 @@
   let morning = [Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"), Shipment(order: "A-1002", customer: "C-20", carrier: "Parcelo"), Shipment(order: "A-1003", customer: "C-99", carrier: "Parcelo"), Shipment(order: "A-1004", customer: "C-21", carrier: "Parcelo")]
-  dispatch(morning) with @customers = directory(customers), @mailer = outbox(), @log = @console
+  dispatch(morning) with @customers = directory(customers), @mailer = outbox()
   let late = [Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida")]
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U3001] Error: `dispatch` needs `@log: Console[print]`, which is not in scope here
```

*Why:* the console is right there in `main`, so it seems `dispatch` should find it. But `dispatch` needs `@log`, and `main` holds only `@console`. Bindings are found by name, never by type. The message names the callee, the binding with its capability, and "not in scope here"; the mark is on the call.

*Fix:* add `@log = @console` to the `with`. The repair una offers, a `uses @log` line on `main`, would widen `main`'s header instead, so `una fix` skips it, and `una fix --dry-run .` says so ([For agents](#for-agents)). See [U3001](/docs/errors/U3001/).
:::

### Using an operation the header does not list (U3002)

:::mistake
In the step of [Narrowing: a greeting that may only look up](#narrowing-a-greeting-that-may-only-look-up), give `erase` the header of `greeting`, `uses @customers: Customers[find]`:

```diff include="steps/15-with..mistakes/2:src/accounts.una" context="1" title="src/accounts.una"
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

*Fix:* write `Customers[forget]`. Add an operation to a header only when it belongs to the function's job: every caller must then hold it too. See [U3002](/docs/errors/U3002/).
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

*Fix:* log in the caller, which already holds `@log`. A message text should stay a pure function, which an example can call with values alone. See [U3004](/docs/errors/U3004/).
:::

### Installing a handler of another capability (U3010)

:::mistake
Write `@mailer = directory_down()`:

```diff include="day-to-day..mistakes/4:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -107,3 +107,3 @@
   let late = [Shipment(order: "A-1005", customer: "C-17", carrier: "Rapida")]
-  dispatch(late) with @customers = directory(customers), @mailer = mail_down(), @log = @console
+  dispatch(late) with @customers = directory(customers), @mailer = directory_down(), @log = @console
 
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U3010] Error: this handler implements `Customers`, and `dispatch` needs `@mailer` to be `Mailer`
```

*Why:* both handlers stand for a service that never answers, and their names are close. The message says which capability the handler implements, `Customers`, and which one the callee needs at that name, `Mailer`; the mark is on the handler's call.

*Fix:* install `mail_down()`, the handler of `Mailer` that never answers. See [U3010](/docs/errors/U3010/).
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

*Why:* grants are easy to forget when a `uses` line is added to `main`. The mark is on the `uses` line that is not granted, and the help line widens the grant, which is for the people who maintain the package to decide.

*Fix:* grant `"clock"` if the program needs the time. Otherwise remove the `uses` line and the call. See [U3012](/docs/errors/U3012/).
:::

### Adding an operation that the handlers lack (U3011)

:::mistake
Give `Mailer` a second operation, `delivered`, which asks whether a message arrived, and leave the handlers as they are:

```diff include="day-to-day..mistakes/6:src/notices.una" context="2" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -28,4 +28,6 @@
 pub capability Mailer
   op send(to: Text, subject: Text, body: Text) -> Unit
+    fails ServiceError
+  op delivered(to: Text) -> Bool
     fails ServiceError
 
```

```text include="mistakes/6/expected/rendered.txt#L1,L10"
[U3011] Error: handler `outbox` does not implement the operation `delivered` of `Mailer`
[U3011] Error: handler `mail_down` does not implement the operation `delivered` of `Mailer`
```

*Why:* the capability is the description of the service, and every handler must do the whole job. A new operation therefore breaks every handler of the capability at once: here `outbox` and `mail_down`, one diagnostic each, with the mark on the handler's name.

*Fix:* give each handler an `op delivered(to) = …` line, such as `true` for `outbox` and `fail Timeout` for `mail_down`. Or leave the operation out until the service has it. See [U3011](/docs/errors/U3011/).
:::

## 12.8 Exercises

The exercises come with the chapter's download, `12-capabilities.tar.gz`. Each one starts from `exercises/N/start`: the day-to-day package with the exercise's examples added, and a stub of what to write when there is one. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`, so the layout is canonical.

### Exercise 1: a directory of one customer

::::exercise
Small examples often need a directory with exactly one customer. Write a handler `only(customer: Customer)` for `Customers` whose `find` gives that customer for their id and `None` for any other. The start package ends with these examples, and `una check .` reports U1001 until the handler exists:

```una include="exercises/1/start/src/notices.una#L148-L158" title="exercises/1/start/src/notices.una"
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

`una test .` reports 9 examples passing.
:::
::::

### Exercise 2: archive every notice

::::exercise
The store keeps a copy of every notice it sends in an archive mailbox, `archive@example.invalid`, through a second mail service. A notice counts as sent only once its copy is archived. The start package has `notify_and_archive`, which holds a second binding of `Mailer`, `@archive`, and does not use it yet:

```una include="exercises/2/start/src/notices.una#notify_and_archive" title="exercises/2/start/src/notices.una"
--- Sends the notice, then a copy of it to the store's archive mailbox. A notice counts as sent
--- only once its copy is archived. Exercise 2: send the copy.
pub notify_and_archive(shipment: Shipment) -> Text
  uses @customers: Customers[find]
  uses @mailer: Mailer[send]
  uses @archive: Mailer[send]
  fails NoticeError
=
  notify(shipment)
    if error pass
```

and two examples: a notice that is sent and archived gives the address, and one whose copy cannot be archived fails with `MailDown`.

```una include="exercises/2/start/src/notices.una#L159-L171" title="exercises/2/start/src/notices.una"
example "a notice that is sent and archived gives the address"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  given @archive = outbox()
  do notify_and_archive(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect result == "rosa@example.invalid"

example "a notice whose copy cannot be archived is MailDown"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  given @archive = mail_down()
  do notify_and_archive(Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect fails MailDown
```

:::hint
*Hint:* keep the address that `notify` returns with `let`, then send the copy on `@archive`, and give the address back on the last line. A failure of the archive means the notice does not count as sent, so turn it into the variant the example expects, with `if error fail MailDown`.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/2/start/expected/commands/test.txt#L10-L12,L14"
example notices "a notice whose copy cannot be archived is MailDown" ... FAILED
  src/notices.una:171: expect fails MailDown
  the `do` line completed with `"rosa@example.invalid"`
9 examples: 8 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Replace the body:

```diff include="exercises/2/start..exercises/2/answer:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -51,3 +51,3 @@
 --- Sends the notice, then a copy of it to the store's archive mailbox. A notice counts as sent
---- only once its copy is archived. Exercise 2: send the copy.
+--- only once its copy is archived.
 pub notify_and_archive(shipment: Shipment) -> Text
@@ -58,4 +58,7 @@
 =
-  notify(shipment)
+  let address = notify(shipment)
     if error pass
+  @archive.send("archive@example.invalid", subject: "Notice for order {shipment.order}", body: "sent to {address}")
+    if error fail MailDown
+  address
 
```

The two bindings have the same capability and different names, so an example installs a different handler for each: the second example sends the notice through `outbox()` and fails the copy through `mail_down()`.
:::
::::

### Exercise 3: a contact line that never fails

::::exercise
A packer writes the customer's name and address on each parcel. Write `contact(id: Text) -> Text`, which gives `"Rosa <rosa@example.invalid>"` for a known customer, and `"<id>: no address on file"` for an unknown one or when the directory does not answer. Its header has no `fails`, so no failure may leave it. The start package has the header with a stub body, and three examples:

```una include="exercises/3/start/src/notices.una#contact" title="exercises/3/start/src/notices.una"
--- The line a packer writes on a parcel: the customer's name and address, or a note when the
--- directory does not know the customer or does not answer. It never fails. Exercise 3.
pub contact(id: Text) -> Text
  uses @customers: Customers[find]
=
  ""
```

```una include="exercises/3/start/src/notices.una#L155-L168" title="exercises/3/start/src/notices.una"
example "a known customer gives a name and an address"
  given @customers = directory(sample_customers())
  do contact("C-17")
  expect result == "Rosa <rosa@example.invalid>"

example "an unknown customer gives a note"
  given @customers = directory(sample_customers())
  do contact("C-99")
  expect result == "C-99: no address on file"

example "a directory that does not answer gives a note, and no failure"
  given @customers = directory_down()
  do contact("C-17")
  expect result == "C-17: no address on file"
```

:::hint
*Hint:* do as `orderable` does in [Recovering with a default from a service](#recovering-with-a-default-from-a-service). Call `@customers.find(id)` and turn its failure into `None` with `if error use None`. Then take the `Option` apart with `when`: `is Some(customer)` builds the line from `customer.name` and `customer.email`, and `is None` gives the note.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/3/start/expected/commands/test.txt#L9-L11,L19"
example notices "a known customer gives a name and an address" ... FAILED
  src/notices.una:158: expect result == "Rosa <rosa@example.invalid>"
  it is false, with `result` = `""`
10 examples: 7 passed, 3 failed
```

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Replace the body:

```diff include="exercises/3/start..exercises/3/answer:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -67,3 +67,3 @@
 --- The line a packer writes on a parcel: the customer's name and address, or a note when the
---- directory does not know the customer or does not answer. It never fails. Exercise 3.
+--- directory does not know the customer or does not answer. It never fails.
 pub contact(id: Text) -> Text
@@ -71,3 +71,7 @@
 =
-  ""
+  let found = @customers.find(id)
+    if error use None
+  when found
+    is Some(customer) -> "{customer.name} <{customer.email}>"
+    is None -> "{id}: no address on file"
 
```

The directory's failure becomes `None`, so the third example falls into the same arm as an unknown customer, and `contact` keeps the promise of its header: a text, always.
:::
::::

## 12.9 Recap and reference

### For agents

:::agents
`una --json check .` reports the capability diagnostics of this chapter, the U3xxx codes, in the domain `authority`. For [forgetting to hand over a binding](#forgetting-to-hand-over-a-binding-u3001):

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U3001","severity":"error","domain":"authority","message":"`dispatch` needs `@log: Console[print]`, which is not in scope here","primary":{"file":"src/notices.una","start":{"line":106,"col":3},"end":{"line":106,"col":20}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"widens":{"kind":"authority","cost":"the function then holds this authority, and every caller must hold it too: check that the operation belongs to this function's job"},"description":"declare `uses @log: Console[print]` in the header","edit":{"file":"src/notices.una","start":{"line":102,"col":32},"end":{"line":102,"col":32},"replacement":"\n  uses @log: Console[print]"}}],"explain":"una explain U3001"}],"fixable":0}
```

A repair that gives a function more authority carries `widens`, with its kind (`authority`, or `grant` for U3012) and its cost, and ranks after the repairs that keep authority. `una fix` skips the repairs that widen:

```text include="mistakes/1/expected/commands/fix.txt"
$ una fix --dry-run .
skipped src/notices.una:102:32 U3001 declare `uses @log: Console[print]` in the header: widens authority
```

The compact rule: *every effect is `@binding.op(...)` on a binding of the header's `uses`; bindings pass by name or through `with`; a handler implements every operation of its capability and keeps its contract; `main` gets only the granted host capabilities.*
:::

### Recap

:::recap
- A function's `uses` list everything it may do outside the program; a `pub` function without `uses` is pure.
- List the operations a function needs; a callee holds only those its header lists.
- Bindings pass by name, or through `with` for one statement; a capability is never a value.
- Host capabilities reach `main` only as `[run] grants` and `--grant` allow; grant the least that works.
- Declare each outside service as a `capability`, with a handler for each way to provide it; every handler implements every operation.
- A clause such as `if error use` on an operation's call keeps a function working when a service fails.
- A function argument with effects needs `uses of` and `fails of` (edition `0.2`).
- Edition `0.3` adds conditions on operations and ceilings for modules ([chapter 13](/learn/authority/)).
:::

### Reference

:::reference
- Construct pages: [`capability` and `op`](/docs/language/capabilities/capability/), [`uses`](/docs/language/capabilities/uses/), [`with`](/docs/language/capabilities/with/), [`handler`](/docs/language/capabilities/handler/), [host capabilities and grants](/docs/language/capabilities/host/)
- Configuration: [`[run] grants`](/docs/configure/run/grants/)
- Standard library: [the prelude and the host capabilities](/docs/std/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U3001](/docs/errors/U3001/), [U3002](/docs/errors/U3002/), [U3004](/docs/errors/U3004/), [U3005](/docs/errors/U3005/), [U3010](/docs/errors/U3010/), [U3011](/docs/errors/U3011/), [U3012](/docs/errors/U3012/), [U5001](/docs/errors/U5001/)
- Specification: [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [standard library](/docs/spec/14-standard-library/), [diagnostics and ABI](/docs/spec/13-diagnostics-and-abi/)
- Editions: [editions](/docs/editions/)
:::
