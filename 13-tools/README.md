---
learn: "13"
title: Tools
editions: ["0.2"]
codes: [U0101, U1006, U2004, U3001, U5001, U7001]
time: 40
builds: Sale price tags for a store, taken through every check before a release
prerequisites: ["6", "7", "8", "10"]
template: 2
nav: ["Check, format and fix", "Reading a diagnostic", "Obligations, contracts, traces", "The build report", "Running, testing and building", "Day-to-day: sale price tags", "Testing it", "Common mistakes", "For agents", "Exercises", "Recap", "Reference"]
---

# 13 Tools

Writing a program is half of the work. The other half is finding out whether it is right: reading what the checker reports, letting it repair what it can, seeing what it proved and what the program may do, and finally running, testing and shipping it. In Una all of that is one command, `una`, and each of its subcommands prints a text for people, or with `--json` a JSON document for programs. This chapter takes a small pricing package through the commands you use every day, in the order you use them.

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
- read a diagnostic: its code, its place, its repairs and its counterexample, as text and as JSON;
- list what the verifier proved with `una obligations`, `una contract` and `una trace`;
- read the build report, which says what the package may do and what it trusts;
- run, test and build a native executable, and connect an editor with `una lsp`.
:::

## Why it works this way

A compiler that prints a wall of text for a person is hard to use well from a script, an editor or an agent. Each of them ends up parsing messages that were never meant to be parsed, and breaks when a message changes. And a compiler that only says "error" leaves the reader to work out the repair, even when the compiler knew exactly what it was.

Una's tools are built around three rules:

:::steps
1. **Every problem is a diagnostic with a code.** The code has a page and an explanation in the binary, `una explain U2004`. The text of a message may improve from release to release, and the code stays.
2. **Every command has two renderings of one result.** By default a command prints for people. With `--json` it prints one JSON document named by its schema, such as `una.diagnostics/1`, with the same content. A schema keeps its version when keys are added, and changes it when a key is removed or changes meaning.
3. **A repair is data.** A diagnostic lists its repairs, ranked. A repair whose change is exact carries the edit itself, and `una fix` applies those edits, and only those that keep what the program is allowed to do.
:::

The checks also give more than a yes or a no. The verifier's obligations, a function's full contract and the build report are all printed on request, so a reviewer can see what was proven, not only that the check passed.

> [!KEY]
> Whatever `una check` reports, `una explain` explains, `--json` gives as data, and `una fix` repairs when the edit is exact and widens nothing.

## 13.1 Check, format and fix

### The check loop and its tiers

The loop you run most is `una check .`. It checks the package in tiers: tier 0 is the syntax, the names, the types, the capabilities and the labels, and tier 1 adds the verifier, which proves the contracts with Z3. `una check --tier 0 .` stops after tier 0, for a quick answer while you type. Diagnostics go to stderr, and the exit code is 1 when there is at least one error.

### A receipt line with two problems

Start with a receipt line written by someone used to another language: an `=` at the end of the header, as some languages open a body, and a second argument without its label.

Each step of this chapter is a package, as in [chapter 1](/learn/hello/#s1-1): `una.toml`, `verification.lock` (copy it from chapter 1, or take the step, whole, from the chapter's download, `13-tools.tar.gz`) and the module under `src/`:

```toml include="steps/01-fix/una.toml" title="steps/01-fix/una.toml"
[package]
name = "receipt"
version = "0.1.0"
edition = "0.2"

[run]
entry = "receipt"
grants = ["console"]
```

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

The checker reports one problem, the syntax error. A file that does not parse cannot be checked further, so the missing label is not reported yet. The diagnostic's `Help` line holds a repair with an exact edit, and the last line counts the diagnostics that `una fix` can repair.

### Previewing and applying the repairs

`una fix --dry-run .` shows what `una fix .` would change, without writing anything:

```sh
una fix --dry-run .
```

```text include="steps/01-fix/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/receipt.una:4:1 U0101 put `=` on a line of its own: a function whose body is a block has the long form, the header, `=`, then the indented body
fixed src/receipt.una:11:31 U2004 label it `sku`
```

It works in rounds. Round one applies the syntax repair, the file then parses, and round two finds and repairs the missing label. Each line's position is in the file as the earlier rounds left it, so the label's line moved from 10 to 11. After the last round it formats every file, as `una fmt .` does, and checks the package once more. Running `una fix .` gives the package that the next step holds:

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

The function whose body is one line ends on the header line: that is canonical form, which `una fmt .` writes and `una fmt --check .` checks. A file that is not in canonical form is U7001, an error like any other, so every Una file in a package reads the same way.

### What `una fix` applies, and what it leaves to you

What `una fix` applies is narrow on purpose:

| `una fix` applies | `una fix` leaves to you |
| --- | --- |
| The first repair of a diagnostic, when it carries an exact edit | A repair without an edit, such as a guard for a refuted proof |
| Edits to the package's modules | Any change to `una.toml` or `verification.lock` |
| Edits that keep what the code may do | An edit that adds a `uses`, makes a declaration `pub` or adds a grant |
| Formatting of every file that parses | A repair marked as an escape, such as `checked` |

`una fix --dry-run .` names each repair it skips and why: [A capability that is not there](#a-capability-that-is-not-there-u3001), in Common mistakes, shows it for a repair that would widen what a function may do.

### In an editor: `una lsp`

> [!TIP] In an editor.
> `una lsp` is a language server: it speaks the Language Server Protocol over stdin and stdout, so any editor with a client for it shows the diagnostics of `una check` as you type. It also offers the repairs with edits as quick fixes, formats a file, and answers hover, go to definition and the outline of a file. It checks and proves, and it never runs a program.

## 13.2 Reading a diagnostic

### A sale price with one wrong word

A diagnostic that the verifier reports has the most parts. This step computes a sale price that must never fall below cost, from a price, a cost and a percent off. It has a requirement it is derived from, and a private function that reads a typed percent. The body has one wrong word: on line 24, on the path where the discount goes below cost, it returns `price` instead of `cost`.

```una include="steps/03-refuted/src/discount.una" title="steps/03-refuted/src/discount.una" caption="with one wrong word, on line 24"
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

### The parts of a refuted proof

`una check .` reports:

```text include="steps/03-refuted/expected/rendered.txt"
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

Read it from the top:

:::steps
1. **The first line.** The code, U5001, and the message: the postcondition of `sale_price` is refuted. U5001 means that the verifier found values for which a promise fails.
2. **The two places.** `ensures clause` marks the promise, line 20. The main mark is the value that breaks it: `price`, on line 24.
3. **`Help 1` and `Help 2`.** The repairs, best first. Neither has an edit here: the right change depends on what the function is meant to do, so `una fix` leaves it to you.
4. **`Note 1`.** The obligation: its identifier, its kind and its goal, `result >= cost`. `una obligations .` lists the same identifier.
5. **`Note 2`.** The counterexample: with `price = 0` and `cost = 1`, the discounted price 0 is below cost, the function returns `price`, 0, and 0 is not at least 1. Plug the values into the code and the bug is in plain sight.
6. **`Note 3`.** Where to read more.
:::

### An explanation for every code: `una explain`

Every code has an explanation in the binary, which prints a paragraph, then a failing example and a fixed one. The first lines of the one for the missing label of [section 13.1](#s13-1):

```text include="steps/01-fix/expected/commands/explain.txt#L1-L4"
$ una explain U2004
# U2004: Missing argument label

A call with two or more arguments may omit the label of its first argument only; every other argument names its parameter, as in `max(x, b: 10)`, or is a bare name equal to the parameter's name, which counts as labeled (`spec/04 §3`). A constructor with two or more fields labels every argument, the first included. The diagnostic carries an edit that labels the argument with the parameter at its position.
```

### The same diagnostic as JSON

The same diagnostic, for a program, is one line of JSON:

```sh
una --json check .
```

```json include="steps/03-refuted/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U5001","severity":"error","domain":"verification","message":"postcondition of `sale_price` is refuted","primary":{"file":"src/discount.una","start":{"line":24,"col":29},"end":{"line":24,"col":34}},"related":[{"file":"src/discount.una","start":{"line":20,"col":11},"end":{"line":20,"col":25},"message":"ensures clause"}],"obligation":{"id":"ob-8a05af02a5f7","kind":"postcondition","goal":"result >= cost","status":"refuted"},"counterexample":{"bindings":[{"name":"cost","value":1},{"name":"off","value":0},{"name":"price","value":0},{"name":"result","value":0}]},"repairs":[{"rank":1,"escape_cost":0,"description":"add a guard or an arm so that the failing path returns a value for which `result >= cost` holds","edit":null},{"rank":2,"escape_cost":0,"description":"adjust the `ensures` clause","edit":null}],"explain":"una explain U5001"}],"fixable":0}
```

Every field of the text is a key. `primary` and `related` hold the exact places, with lines and columns counted from 1 and an `end` that is exclusive. `obligation` and `counterexample` appear only for the verifier's codes, U5001 and U5002. Each repair has its `rank`, its `escape_cost`, which is 0 for a repair that keeps every guarantee, and its `edit`, which is `null` when the repair is not mechanical. `fixable` counts the diagnostics that `una fix` would repair.

## 13.3 What was proven: obligations, contracts and traces

### From promises to obligations

A package that checks clean is proven, but "proven" covers many small facts. The verifier turns every promise into **obligations**: each `ensures`, each `requires` at each call, each refined value, each division. This step is the fixed price. The fix is the one word that [section 13.2](#s13-2) found:

```diff include="steps/03-refuted..steps/04-proven:src/discount.una" context="1" title="src/discount.una"
--- a/src/discount.una
+++ b/src/discount.una
@@ -23,3 +23,3 @@
   let discounted = price - price * off / 100
-  if discounted < cost then price else discounted
+  if discounted < cost then cost else discounted
 
```

The whole package, which checks clean:

```una include="steps/04-proven/src/discount.una" title="steps/04-proven/src/discount.una" verified="check, run, test"
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

### Every obligation and its status: `una obligations`

`una obligations .` lists every obligation with its status:

```text include="steps/04-proven/expected/commands/obligations.txt"
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

Each line is a status, an identifier, a kind, a place and a goal. Most are `refinement`: each literal passed as `Cents` must be at least 0, and each `off` passed as `Percent` must be in `0..90`. The line at `27:1` is the result of `parse_percent`, which must be a `Percent`. After a first check, a result the proof cache already holds is marked `(cached)`. The command exits with code 1 when any obligation is not proven, so a script can rely on it.

### A function's full header: `una contract`

`una contract` prints a function's full header, as a caller relies on it, with its doc comments. For a private function it shows what the checker inferred:

```text include="steps/04-proven/expected/commands/contract.txt"
$ una contract discount.parse_percent
--- A percent typed by a person, such as "30".
parse_percent(raw: Text) -> Percent
  fails PercentError -- inferred
```

`parse_percent` declares no `fails` clause, and the contract shows the one the checker inferred, marked `-- inferred` ([chapter 6, Failure](/learn/failure/), explains inference). For `sale_price`, the contract ends with the requirement it is derived from:

```text include="steps/04-proven/expected/commands/contract-sale.txt"
$ una contract discount.sale_price
--- The price after `off` percent, never below `cost`.
pub sale_price(price: Cents, cost: Cents, off: Percent) -> Cents
  ensures result >= cost
  derived from PRICING_1
-- requirement PRICING_1 (active): "A sale price is never below what the store paid for the product"
```

### From a requirement to the code: `una trace`

`una trace` goes the other way, from a requirement to the code. It prints the requirement, every function derived from it with the clauses that carry it, and the obligations that prove them:

```text include="steps/04-proven/expected/commands/trace.txt"
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

A reviewer who asks "where is this rule enforced, and is it proven?" gets the answer from one command ([chapter 10, Testing](/learn/testing/), introduced requirements).

### How the three commands name things

The three commands name things the same way. An obligation's identifier, such as `ob-8a05af02a5f7`, is the one a U5001 diagnostic prints in its `Note 1`, so a refuted proof can be found in the listing. An id is computed from the declaration, the kind and the goal, so it survives edits elsewhere, and two identical obligations in one function share one, as the two `off in 0..90` lines do. A function is named by its module and its name, `discount.sale_price`. `una contract` checks the package without the solver, since a header does not depend on the proofs, and reports the package's diagnostics instead when there are any. With `--json`, `una obligations .` also lists, for each obligation, the hypotheses the solver could assume, which helps to see why a goal could not be proven.

## 13.4 The build report

### One page for a reviewer: `una report`

`una report .` checks the package and prints what a reviewer needs to know about it, on one page:

```text include="steps/04-proven/expected/commands/report.txt"
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

The sections, in order:

- **`lock`, `proven`, `obligations`.** The solver and a digest of `verification.lock`, then the counts of obligations by status. `security and authority by typing` means that information flow and capabilities need no solver: the checker proves them by their types.
- **`authority` and `handler authority`.** Every function and handler with a `uses` clause, and what it may do. Here only `main` may print. A new line in this section, in a diff of the report, is a new power in the code.
- **`information`, `escapes`, `assumptions`.** The policies called, the uses of `checked` against the budget of `una.toml`, and the operations of the package's own capabilities, whose behavior the verifier assumes.
- **`tcb`.** What the proofs trust: trusted modules, the host capabilities, the solver, and the proof cache with its key.
- **`requirements` and `coverage`.** Which functions each requirement reaches, and how many public functions have an `ensures` or a `derived from`.
- **`native`.** The host target of `una build`, and the values the executable keeps at arbitrary precision because no refinement bounds them to a machine word.
- **`out of model`.** What the guarantees do not cover, such as timing and resource use.

The report exits with code 1 when an obligation is not proven. With `--json` it is the document `una.report/2`, which a release script can compare between two versions of a package.

### Reading the report as a review checklist

Read the report as a review checklist. A pull request that adds a line under `authority`, a module under `trusted modules`, or a count under `escapes` changes what the package may do or what its proofs rest on, even when its diff of the code looks small. `coverage` also counts `trivial ensures`, a promise the solver proves with no hypothesis at all, such as `ensures true`: it is reported as missing, since it promises nothing.

> [!NOTE]
> The `native` line names the machine `una` runs on, such as `aarch64-apple-darwin`, so the report of the same package differs between a Mac and a Linux machine in that line only.

## 13.5 Running, testing and building

### Running and testing: `una run` and `una test`

Three commands run the code. `una run .` runs `main` of the module that `[run] entry` names, with the grants of `[run] grants`. `una test .` runs every example and prints one line for each:

```text include="steps/04-proven/expected/commands/test.txt"
$ una test .
example discount "30 percent off a lamp" ... ok
example discount "a typed percent above 90 is OutOfRange" ... ok

2 examples: 2 passed, 0 failed
```

It exits with code 1 when an example fails. Both commands check the package first, and run nothing when the check reports an error.

### A run as data: `--json` and the trace

With `--json`, `una run .` prints the run as one document: the status, the lines printed, the failure if any, and the trace, every operation the run performed:

```text include="steps/04-proven/expected/commands/run.txt"
$ una --json run .
{"schema":"una.run/1","tier":1,"status":"ok","output":["LAMP-01 1393, DESK-02 11000"],"failure":null,"diagnostics":[],"trace":[{"seq":1,"instance":"host:Console","capability":"Console","op":"print","args":{"line":"\"LAMP-01 1393, DESK-02 11000\""},"outcome":{"kind":"ok","value":"unit"}}]}
```

The trace is what the program asked of the outside world, in order, with the arguments and the outcome of each operation. `una run --grant <spec> .` adds a grant for one run, such as `--grant clock`, on top of the grants of `una.toml`.

`status` is `ok` for a run that returned, `failed` when `main` failed with its error kind, `aborted` when a limit stopped it ([chapter 12, Memory and concurrency](/learn/memory-and-concurrency/), shows one), and `rejected` when the checks failed and nothing ran.

### A native executable: `una build`

`una build .` compiles the package into a native executable, after the same checks:

```sh
una build .
```

```text include="steps/04-proven/expected/commands/build.txt"
$ una build .
built target/una/discount
```

The executable is written under the package, at `target/una/<name>`, with `<name>` from `[package] name`. It runs `main` with the grants of `una.toml` built in, takes further `--grant` flags, and prints what `una run .` prints (for concurrent tasks, see [chapter 12](/learn/memory-and-concurrency/#s12-4)). Building needs a C compiler on the path, `cc`, to link, and builds for the machine it runs on.

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

## 13.6 Day-to-day: price tags for a sale

### What the program must do

Now the program from the start of the chapter, and the checks it goes through before a release. The store runs a sale of 30 percent. Each shelf gets a tag with the price and the sale price, which a requirement says must never be below what the store paid. The prices come from the store's catalog, a capability, so the tags can be tested with a catalog held in memory.

### The requirement and the kinds

The requirement records the rule in words. `Cents` and `Percent` are refined kinds ([chapter 7, Contracts and the verifier](/learn/contracts/)), so a negative price or a discount of 95 percent cannot reach the functions of [The price](#the-price) and [The tag](#the-tag).

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

`sale_price` promises `result >= product.cost` and names the requirement it is derived from. The verifier proves the promise on both paths of the `if`.

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

| Command | It stops the release when… |
| --- | --- |
| `una fmt --check .` | A file is not in canonical form (U7001) |
| `una check .` | A name, a type, a capability, a label or a proof is wrong |
| `una test .` | An example fails: a number is not the one a person expects |
| `una trace PRICING_1` | An obligation derived from the requirement is not proven |
| `una report .` | An obligation is not proven; and a reviewer reads what changed |
| `una build .` | The executable cannot be built, for example without `cc` |

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

The report's `authority` section has two lines: `main` may print, and `tag` may ask the catalog. `una contract` shows the same for one function, which is what a reviewer of `tag` checks:

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

Every one of these commands exits with code 0 on this package, so a release script can run them in turn and stop at the first that does not. The order goes from the cheapest question to the most expensive one: formatting needs no types, the checks need no run, and the examples need a package that checks. A script for a continuous integration service can add `--json` to each command and keep the documents, so that the report of every release can be compared with the one before it.

## 13.7 Testing it

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

`una test .` runs each example in turn, with only the handlers its `given` lines install: an example can never reach the real catalog, or the console, by accident. With `--json`, each example in the document also carries its trace, the operations its `do` line performed, which `expect performed` checks one at a time.

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

## 13.8 Common mistakes

Each mistake below is a small change to `day-to-day/src/pricetags.una`, followed by what `una check .` reports, and which tool repairs it.

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

*Why:* canonical form is part of the language, so every package reads the same way, and a diff shows only real changes.

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

*Why:* every argument after the first names its parameter, so a call reads the same without the header at hand.

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

*Why:* a product can cost more than its price, as in the counterexample, and then the function returns a value below cost.

*Fix:* read the counterexample into the code, and return `product.cost` on that path. `una fix` has nothing to apply: the repairs have no edit. See [U5001](/docs/errors/U5001/).
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

*Why:* a `derived from` must name a requirement of the package, or `una trace` would follow a link to nothing.

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

The repair would declare the capability in `main`'s header, which widens what `main` may do, so `una fix` does not apply it:

```text include="mistakes/5/expected/commands/fix.txt"
$ una fix --dry-run .
skipped src/pricetags.una:61:32 U3001 declare `uses @catalog: Catalog[product]` in the header: widens authority
```

*Why:* `main` may only do what the host grants it, and the catalog is the package's own capability, which no grant provides.

*Fix:* install a handler for the call with `with @catalog = listed(sample())`, as the program does. See [U3001](/docs/errors/U3001/).
:::

## 13.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's function and example added. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one line on the header line.

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

:::hint
*Hint:* compute the result for the counterexample by hand: a price of 1 and a cost of 0. The test in the `if` compares the wrong value.
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
*Hint:* a `for` loop over the SKUs, a `let edit total: Cents = 0`, and a `when` on what the catalog gives. The verifier proves that the total stays a `Cents`, since each sale price is one.
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
*Hint:* look at the counterexample: a cost of 1 and a price of 0. No result can be at least the cost and at most the price for that product. The function cannot fix that; its callers can promise never to ask.
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

## 13.10 Recap and reference

### For agents

:::agents
Every command prints one JSON document with `--json`, its `schema` key first. The run of the day-to-day program, with its trace:

```json include="day-to-day/expected/commands/run.txt#L2"
{"schema":"una.run/1","tier":1,"status":"ok","output":["LAMP-01  19.90 now 13.93","DESK-02  129.00 now 110.00","CHAIR-09  not in the catalog"],"failure":null,"diagnostics":[],"trace":[{"seq":1,"instance":"with:listed#1","capability":"Catalog","op":"product","args":{"sku":"\"LAMP-01\""},"outcome":{"kind":"ok","value":"Some(Product(sku: \"LAMP-01\", price: 1990, cost: 1200))"}},{"seq":2,"instance":"host:Console","capability":"Console","op":"print","args":{"line":"\"LAMP-01  19.90 now 13.93\""},"outcome":{"kind":"ok","value":"unit"}},{"seq":3,"instance":"with:listed#2","capability":"Catalog","op":"product","args":{"sku":"\"DESK-02\""},"outcome":{"kind":"ok","value":"Some(Product(sku: \"DESK-02\", price: 12900, cost: 11000))"}},{"seq":4,"instance":"host:Console","capability":"Console","op":"print","args":{"line":"\"DESK-02  129.00 now 110.00\""},"outcome":{"kind":"ok","value":"unit"}},{"seq":5,"instance":"with:listed#3","capability":"Catalog","op":"product","args":{"sku":"\"CHAIR-09\""},"outcome":{"kind":"ok","value":"None"}},{"seq":6,"instance":"host:Console","capability":"Console","op":"print","args":{"line":"\"CHAIR-09  not in the catalog\""},"outcome":{"kind":"ok","value":"unit"}}]}
```

Each event names the handler instance that answered, such as `with:listed#1`, so an agent can check what a run asked of each service. The loop for an agent: `una --json check .`, apply what `una fix .` applies, read the remaining repairs by `rank` and `escape_cost`, then `una --json test .`. `una fix` never widens authority, never edits `una.toml`, and never applies an escape.
:::

### Recap

:::recap
- `una check .` is the loop. `--tier 0` skips the proofs for a quick answer.
- `una fix --dry-run .` shows the exact repairs, and `una fix .` applies them and formats. It never widens authority or edits `una.toml`.
- A diagnostic has a code, places, ranked repairs, and for a proof, an obligation and a counterexample. `una explain` explains any code.
- `--json` turns every command's output into one document with a `schema` key.
- `una obligations`, `una contract` and `una trace` show what was proven and for which rule.
- `una report` shows what the package may do and trusts.
- `una run`, `una test` and `una build` check first, and run nothing that does not check.
:::

### Reference

:::reference
- Command line: [all commands](/docs/cli/), [`una check`](/docs/cli/check/), [`una fmt`](/docs/cli/fmt/), [`una fix`](/docs/cli/fix/), [`una explain`](/docs/cli/explain/), [`una obligations`](/docs/cli/obligations/), [`una contract`](/docs/cli/contract/), [`una trace`](/docs/cli/trace/), [`una report`](/docs/cli/report/), [`una run`](/docs/cli/run/), [`una test`](/docs/cli/test/), [`una build`](/docs/cli/build/), [`una lsp`](/docs/cli/lsp/)
- For agents: [Una for agents](/docs/agents/), [JSON output and diagnostics](/docs/agents/json/), [repairs](/docs/agents/repairs/), [the build report](/docs/agents/build-report/)
- Construct pages: [`ensures`](/docs/language/functions/ensures/), [`requires`](/docs/language/functions/requires/), [`requirement` and `derived from`](/docs/language/requirements/requirement/), [`where` and refinements](/docs/language/types/where/), [`example`](/docs/language/examples/example/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U1006](/docs/errors/U1006/), [U2004](/docs/errors/U2004/), [U3001](/docs/errors/U3001/), [U5001](/docs/errors/U5001/), [U7001](/docs/errors/U7001/), and [all codes](/docs/errors/)
- Specification: [diagnostics, agent ABI and project files](/docs/spec/13-diagnostics-and-abi/), [verification](/docs/spec/12-verification/), [canonical form](/docs/spec/15-canonical-form/), [native backend](/docs/spec/16-native-backend/)
:::
