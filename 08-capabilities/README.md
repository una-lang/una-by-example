---
learn: "8"
title: Capabilities
editions: ["0.2"]
codes: [U1001, U3001, U3002, U3004, U3010, U3012, U3014, U5001]
time: 40
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

### Printing is an effect

Start with the smallest effect: printing. A packing slip has a title and one line per item. Building a line is pure computation. Printing it is an effect, and the header says so.

### Each step is a package

The step is a package, as in [chapter 1](/learn/hello/#s1-1): `una.toml`, `verification.lock` (copy it from chapter 1, or take the step, whole, from the chapter's download, `08-capabilities.tar.gz`) and the module under `src/`. The manifest grants the console, which is what lets `main` print:

```toml include="steps/01-uses/una.toml" title="steps/01-uses/una.toml"
[package]
name = "slips"
version = "0.1.0"
edition = "0.2"

[run]
entry = "slips"
grants = ["console"]
```

### A packing slip

The module builds the lines of a packing slip and prints them:

:::steps
```una include="steps/01-uses/src/slips.una" title="steps/01-uses/src/slips.una" verified="check, run"
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

Walkthrough:

1. **`slip_line(sku: Text, quantity: Int) -> Text`.** No `uses`, so the body may not perform any operation. It builds a text and returns it.
2. **`uses @console: Console[print]`.** This line gives `print_line` a binding named `@console`, of the host capability `Console`, with the one operation `print`. The brackets list the operations the function may perform. Without brackets, every operation of the capability is allowed.
3. **`@console.print(slip_line(sku, quantity: quantity))`.** An operation is written on the binding: `@console.print(...)`. A call to a pure function, such as `slip_line`, may stand inside its arguments.
4. **`print_line("LAMP-01", quantity: 2)` in `main`.** `main` holds `@console`, and `print_line` needs `@console`, so the call passes it on by name. Nothing else is written at the call.
:::

`una run .` prints:

```text include="steps/01-uses/expected/output.txt"
Packing slip for order A-1001
2 x LAMP-01
1 x DESK-02
```

### Bindings are found by name

A binding is found by its name, never by its type. If `print_line` asked for `@out: Console[print]`, the call in `main` would not check: `main` holds a `@console`, not an `@out`. [Section 8.4](#s8-4) shows how to hand one over under another name.

### Private functions infer their `uses`

`print_line` is private, so its `uses` line can be left out: the checker infers the least set of capabilities that covers its body and its callees. Remove the line, and `una contract` prints the inferred header:

```diff include="steps/01-uses..steps/02-inferred:src/slips.una" context="1" title="src/slips.una"
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

```text include="steps/02-inferred/expected/commands/contract.txt"
$ una contract slips.print_line
--- Prints one line of a packing slip. It may print, and nothing else.
print_line(sku: Text, quantity: Int) -> Unit
  uses @console: Console[print] -- inferred
```

A `pub` function is the module's reviewed boundary, so it must declare every `uses` itself. A `pub` function with no `uses` is pure, and an operation in its body is U3004 ([an effect in a pure `pub` function](#an-effect-in-a-pure-pub-function-u3004) shows it). Write `uses` on a private function too whenever its effects are part of what a reader should know.

### How many operations to allow

:::decide
**Which to use:**

| You want… | Write |
| --- | --- |
| A function that only computes | No `uses` |
| One operation of a capability | `uses @x: C[op]` |
| Several operations | `uses @x: C[op1, op2]` |
| Every operation, now and when the capability gains more | `uses @x: C`, without brackets |
:::

List the operations you need. A header with brackets also tells the reader what the function does not do.

## 8.2 The host's capabilities and grants

### The host capabilities

The runtime provides the host capabilities: `Console` to print, `Clock` to read the time, `Env` to read environment variables, `Files` to read and write files, and `Keys` for keyed hashes. Edition `0.2` adds `Http`. They are in scope in every module, and they enter a program only one way: through the `uses` of `main`, from `una run`.

### Grants in `una.toml`

`una run` gives `main` only what the package grants. The grants are listed in `[run] grants` of `una.toml`, or passed as `--grant` flags. This step writes an end-of-day stock export, stamped with the time, so it needs three grants:

```toml include="steps/03-host/una.toml" title="steps/03-host/una.toml"
[package]
name = "export"
version = "0.1.0"
edition = "0.2"

[run]
entry = "export"
grants = ["console", "clock", "files:src:write"]
```

### An end-of-day stock export

The module reads the clock, writes the export, and reports the outcome:

:::steps
```una include="steps/03-host/src/export.una" title="steps/03-host/src/export.una" verified="check, run"
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

Walkthrough:

1. **Three `uses` lines on `main`.** Each names one host capability and the operations it needs. `main` may write files, but not read them.
2. **`@clock.now()`.** `Clock.now` gives the milliseconds since the Unix epoch, as an `Int`. Each call is an effect, so it goes on its own line.
3. **`attempt @files.write("stock-export.csv", content: content)`.** `Files.write` can fail with `FileError` (`NotFound`, `Denied` or `Io`). `attempt` keeps the outcome, as in [chapter 6](/learn/failure/), and the `when` reports either case.
4. **`"files:src:write"`.** A `Files` grant carries a directory and a mode. The path `stock-export.csv` resolves inside `src/`. A path outside the grant, an absolute one or one that climbs out with `..`, fails with `Denied` instead of reaching the file.
:::

`una run .` prints:

```text include="steps/03-host/expected/output.txt"
export written: 3 lines
```

and leaves the export in `src/stock-export.csv`. The time in it changes on every run, so the program does not print it.

### What `una check` and `una run` compare

When `una.toml` lists `[run] grants`, `una check` compares them with the `uses` of `main`. Remove `"clock"` from the list, and the check fails with U3012. A grant in the manifest is a line that shows in review.

`una run` takes `--grant` flags as a second source, such as `una run . --grant clock`. It grants the union of `[run] grants` and its flags, for that run only, and it checks the `uses` of `main` against that union before anything runs: a host operation that neither grants is U3012 there too. `una check` takes no `--grant` flag, so it reads only the manifest. A package whose manifest lacks `"clock"` therefore fails `una check`, yet `una run . --grant clock` runs it. What a run may do is the manifest plus the command line, so read both.

### Labels on what a program reads

> [!NOTE] What a program reads from files and the environment is labeled.
> `Files.read` returns `internal Text`, and `Env.get` returns `internal` values too. `Clock.now` returns a public `Int`. A label says how sensitive data is, and the console accepts only `public` data. So the program can write what it read to a file, but cannot print it without a declared policy. [Chapter 9, Information flow](/learn/information-flow/), explains labels and how to release data legitimately.

## 8.3 Your own capabilities and handlers

### Capabilities you declare

The host capabilities cover the machine. A program's own services, such as a mail service, a payment provider or a customer directory, are capabilities you declare. A `capability` lists operations, each with `op`, and no code. A `handler` gives the operations their code. Several handlers can implement one capability, and the caller picks one with `with`.

### Receipts by email

This step sends receipts by email. On a developer's machine the mail service prints each message instead of sending it, and a second handler stands for a service that refuses every address:

:::steps
```una include="steps/04-handlers/src/receipts.una" title="steps/04-handlers/src/receipts.una" verified="check, run"
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

Walkthrough:

1. **`capability Mailer` and `op send(...) -> Unit`.** An operation has a name, typed parameters and a result type, like a function header with no body. `fails MailError` says how it can fail, exactly as on a function.
2. **`send_receipt`.** It uses `@mailer: Mailer[send]` and fails with `MailError`. It does not know which mail service it talks to.
3. **`handler printed(prefix: Text) for Mailer`.** A handler implements every operation of its capability. Its operations take the parameter names only: the types come from the capability. `prefix` is a parameter of the handler, given when it is installed and seen by every operation.
4. **`uses @console: Console[print]` inside the handler.** A handler can use capabilities of its own. They come from the code that installs it: here `main`, which holds `@console`.
5. **`fail Bounced(address: to)`.** An operation body is ordinary Una code. `bouncing` fails with a variant of the operation's error kind.
6. **`with @mailer = printed("[mail]")`.** This installs the handler for the one statement it ends. Inside that call, `@mailer` is the `printed` handler.
:::

`una run .` prints:

```text include="steps/04-handlers/expected/output.txt"
[mail] to rosa@example.invalid: Receipt for order A-1001
second receipt: Err(Bounced("tomas@example.invalid"))
```

The second line comes from `attempt` with the `bouncing` handler: the receipt was not sent, and the outcome says why.

### More clauses on an operation

An operation can carry more clauses than `fails`. `requires` states what callers must establish, `ensures` what callers may rely on, and `accepts` the most sensitive data the operation may receive ([chapter 9](/learn/information-flow/)). An `ensures` on an operation is an assumption about the outside service: callers may rely on it, the verifier checks every handler written in Una against it, and the service itself is trusted to keep it. `una report .` lists every capability declaration as an assumption.

### A handler is not a value

> [!TIP]
> A handler is not a value. It cannot be stored in a variable or returned. It exists only where `with` or an example's `given` line installs it, and its parameters are fixed there.

## 8.4 Passing authority: `with`, rebinding and narrowing

### What a callee receives

A call passes a binding when the callee's name for it matches the caller's. `with` changes what a callee receives, for one statement:

| Write | The callee's `@x` is |
| --- | --- |
| nothing | the caller's `@x`, if it has one |
| `with @x = @y` | the caller's `@y`, which has the same capability |
| `with @x = handler(args)` | a new instance of that handler |

Several bindings go in one `with`, separated by commas. The binding lasts only for the statement it ends.

### Narrowing: a greeting that may only look up

A callee may also receive a binding with more operations than it needs. It then holds only the operations its own header lists. This is how authority narrows on its way down. In this step, the customer directory has two operations, looking a customer up and erasing one. The page greeting may look up, and only the erase request may erase:

:::steps
```una include="steps/05-with/src/accounts.una" title="steps/05-with/src/accounts.una" verified="check, run"
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

Walkthrough:

1. **`capability Customers` with `find` and `forget`.** Two operations with different risks. A capability can also declare operations without `fails`: these two cannot fail.
2. **`uses @customers: Customers[find]` on `greeting`.** The `directory` handler implements both operations, but `greeting` holds only `find`. An `@customers.forget(id)` in its body would not check.
3. **`if none use Customer(id: id, name: "guest")`.** `find` returns an `Option`, so the handling clauses of [chapter 6](/learn/failure/) apply to an operation as to any call.
4. **`uses @audit: Console[print]` on `erase`.** The audit trail is a console here, under the name `@audit`, so the header says what the console is for.
5. **`with @customers = directory(customers), @audit = @console`.** The first binding installs a handler. The second is a rebinding: the callee's `@audit` is the caller's `@console`. `main` holds no `@audit` of its own, so without the rebinding the call would not check.
:::

`una run .` prints:

```text include="steps/05-with/expected/output.txt"
Welcome back, Rosa
Welcome back, guest
audit: erased customer C-20
```

### Each installation is a new instance

Each `with @customers = directory(customers)` installs a new instance. A handler holds no state between calls, and `directory` takes its map as a parameter, so `forget` has nothing to change here. A handler for a real directory would call the service.

### Checking that authority narrows

> [!IMPORTANT]
> Narrowing is a promise you can check. Because `greeting` holds `Customers[find]`, no change to its body can make it erase a customer without a change to its header, which a reviewer sees.

## 8.5 Edition 0.3 preview: conditions and boundaries

Edition `0.3` is a preview: a package opts in with `edition = "0.3"` in `una.toml`, and [chapter 14, Editions](/learn/editions/), explains what that means. It adds two ways to say more about authority.

### Conditions on operations

An operation in `uses` may carry a condition over the function's parameters, written after `where`. The header then says not only what a function may do, but when. A dry run is the common case: the function may place orders only when `dry_run` is false. The verifier proves, at every place where the operation can run, that the condition holds. A call of a function that performs the operation counts as such a place too, so the condition holds through every layer of calls.

A condition is never inferred: a private function without `uses` has no condition on any operation. A function with a condition cannot be passed as a value, since the function that receives it could not prove the condition.

### A restock with a dry run

The step's `reorder` may place an order only when `dry_run` is false:

```una include="steps/06-conditions/src/restock.una" title="steps/06-conditions/src/restock.una" verified="check, run"
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

```text include="steps/06-conditions/expected/output.txt"
would order 20 x LAMP-01
ordered 20 x LAMP-01
```

The first call is a dry run, so it only prints. The third finds enough stock and does nothing. If `reorder` placed the order without the `dry_run` branch, `una check` would report U5001, with a counterexample in which `dry_run` is true ([running an operation where its condition may not hold](#running-an-operation-where-its-condition-may-not-hold-edition-03-u5001) shows it).

### Boundaries

A package often holds code it did not write, such as a vendored library that prints barcodes. `una.toml` can mark such a module as a boundary, with a ceiling: the most the rest of the package may grant it, as a list of capabilities and operations. A call into a boundary takes nothing by name. The caller grants each capability with `with`, so every call shows what the boundary receives, and the checker holds every grant under the ceiling. Here the vendored module is `barcode`, and its ceiling allows `Console[print]`:

```toml include="steps/07-boundaries/una.toml" title="steps/07-boundaries/una.toml"
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

```una include="steps/07-boundaries/src/barcode.una" title="steps/07-boundaries/src/barcode.una" verified="check, run"
module barcode

--- Prints a shelf label with the SKU spelled out for a barcode font. This module is code from
--- outside the store, so `una.toml` lists it as a boundary.
pub print_label(sku: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("*{sku.to_upper}*")
```

The store's own module calls it:

```una include="steps/07-boundaries/src/shelf.una" title="steps/07-boundaries/src/shelf.una" verified="check, run"
module shelf

import barcode (print_label)

pub main() -> Unit
  uses @console: Console[print]
=
  print_label("lamp-01") with @console = @console
  print_label("desk-02") with @console = @console
```

`una run .` prints:

```text include="steps/07-boundaries/expected/output.txt"
*LAMP-01*
*DESK-02*
```

A call to `print_label` without `with @console = @console` is U3020. If `print_label` also needed a `Clock`, granting it would be U3021, since the ceiling allows only `Console[print]`. A binding that the callee does not need is not counted against the ceiling. A boundary module can never be trusted, so it can never release labeled data ([chapter 9](/learn/information-flow/)).

## 8.6 Day-to-day: shipping notices

### What the dispatch step must do

Now the program from the start of the chapter. When orders leave the warehouse, the store emails each customer a notice. The customer directory and the mail service are services on the network, which can time out. The operator reads a log with one line per order.

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

Most of the mistakes below are a small change to `day-to-day/src/notices.una`. The others change a step of this chapter, as each one says.

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

*Why:* `dispatch` needs `@log`, and `main` holds only `@console`. Bindings are found by name, never by type.

*Fix:* add `@log = @console` to the `with`. The repair una offers, a `uses @log` line on `main`, would widen `main`'s header instead, so `una fix` skips it, and `una fix --dry-run .` says so ([For agents](#for-agents)).
:::

### Using an operation the header does not list (U3002)

:::mistake
In [step 05](#narrowing-a-greeting-that-may-only-look-up), give `erase` the header of `greeting`, `uses @customers: Customers[find]`:

```diff include="steps/05-with..mistakes/2:src/accounts.una" context="1" title="src/accounts.una"
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

*Why:* the brackets list every operation the function may perform.

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

*Why:* a `pub` function declares every `uses`, so one without `uses` is pure.

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

*Why:* `directory_down` implements `Customers`, and `@mailer` is a `Mailer`.

*Fix:* install `mail_down()`, the handler of `Mailer` that never answers.
:::

### Using a host capability that is not granted (U3012)

:::mistake
In [step 03](#grants-in-unatoml), remove `"clock"` from `[run] grants`:

```diff include="steps/03-host..mistakes/5:una.toml" context="1" title="una.toml"
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

*Why:* `main` uses `Clock[now]`, and the package does not grant it.

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

*Why:* examples are deterministic, so they never reach the host. una also reports U3001 at `expect performed @log.print`, since no `given` line binds `@log`.

*Fix:* install a handler for every binding the `do` line needs, such as `quiet()` for a console.
:::

### Running an operation where its condition may not hold, edition 0.3 (U5001)

:::mistake
In [step 06](#a-restock-with-a-dry-run), place the order without the dry-run branch:

```diff include="steps/06-conditions..mistakes/7:src/restock.una" context="1" title="src/restock.una"
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

*Why:* the header allows `order` only where `not dry_run` holds, and the verifier finds a run where it does not.

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
*Hint:* a handler's operation takes the parameter names only, and its body can use the handler's parameters. An `if … then … else …` fits on one line.
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
*Hint:* branch on `dry_run`. In the dry run, log one line per shipment, such as `would notify A-1001`, and call nothing that uses `@mailer`.
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
- Declare each outside service as a `capability`, and give it one handler for production and fakes for tests.
- Every example installs its fakes with `given`, and checks effects with `expect performed` and `expect not performed`.
- In edition `0.3`, `where` puts a condition on an operation, and `[boundaries]` limits what outside code receives.
:::

### Reference

:::reference
- Construct pages: [`capability` and `op`](/docs/language/capabilities/capability/), [`uses`](/docs/language/capabilities/uses/), [`with`](/docs/language/capabilities/with/), [`handler`](/docs/language/capabilities/handler/), [host capabilities and grants](/docs/language/capabilities/host/), [`example`](/docs/language/examples/example/)
- Configuration: [`[run] grants`](/docs/configure/run/grants/), [`[boundaries]`](/docs/configure/boundaries/)
- Standard library: [the prelude and the host capabilities](/docs/std/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U3001](/docs/errors/U3001/), [U3002](/docs/errors/U3002/), [U3004](/docs/errors/U3004/), [U3010](/docs/errors/U3010/), [U3012](/docs/errors/U3012/), [U3014](/docs/errors/U3014/), [U3020](/docs/errors/U3020/), [U3021](/docs/errors/U3021/), [U5001](/docs/errors/U5001/)
- Specification: [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [requirements and examples](/docs/spec/08-requirements-and-examples/), [standard library](/docs/spec/14-standard-library/), [diagnostics and ABI](/docs/spec/13-diagnostics-and-abi/)
- Editions: [editions](/docs/editions/)
:::
