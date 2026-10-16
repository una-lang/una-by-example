---
learn: "9"
title: Information flow
editions: ["0.2"]
codes: [U1001, U4001, U4002, U4003, U4005, U4007, U7005]
time: 40
builds: The shipping-notice service with customer data labeled, and a policy that releases a masked address to the log
prerequisites: ["4", "6", "8"]
template: 2
---

# 9 Information flow

The shipping-notice service of [chapter 8](/learn/capabilities/) prints customers' email addresses in its log. Nothing stopped it: the address is a `Text` like any other. In Una you can say how sensitive a value is with a label, such as `secret[PII]`, and the checker follows that label through every computation, every branch and every call. Labeled data reaches a log, a file or a service only if that place accepts its label. This chapter labels data, shows where the checker stops it, and releases what may legitimately go out through a declared policy.

## What you'll build

:::build
The dispatch step of chapter 8, with the customers' names and addresses labeled as personal data. The mail service may receive them. The log may not, so it shows each address masked, through a policy that a reviewer can find in one place:

```text include="day-to-day/expected/output.txt"
sent     A-1001 to r***@example.invalid
sent     A-1002 to t***@example.invalid
skipped  A-1003: no customer has the id C-99
skipped  A-1004: customer C-21 asked for no notices
skipped  A-1005: the mail service did not answer; retry later
```

You will learn to:

- label data with a level, such as `confidential` or `secret`, and a category, such as `PII`;
- predict the label of a result, including one decided by a branch;
- see which places accept which labels, and why data from outside is labeled;
- release data on purpose with a `policy` in a trusted module;
- read the U4xxx diagnostics and repair them without weakening the guarantee.
:::

## Why it works this way

Many leaks of personal data are not attacks. A developer adds a debug line, an error message includes the request, a log line prints a whole record. Each change is small, and nothing in the language says that the value it prints came from a customer's record three calls away.

Una checks the flow of data as part of the type system:

:::steps
1. **A label says how sensitive a value is.** It is part of the type: `secret[PII] Text` is a text that is secret and personal. A type without a label is `public`.
2. **A result carries the labels of what it was computed from.** That includes values chosen by a branch on labeled data, since the choice reveals the condition.
3. **Every place data leaves is a sink with a ceiling.** The console accepts `public` data. An operation of your own accepts what its `accepts` clause says. The checker proves, at every call, that the data is at or below the ceiling.
4. **Lowering a label takes a policy.** A policy names what it releases, to what label, through which function, for what purpose and with which owner. It lives in a trusted module, which `una.toml` lists, and the build report lists every call.
:::

What the checker guarantees has a precise scope. An observer who sees only what reaches `public` places, such as the console, sees the same output from two runs whose labeled inputs differ, unless a policy released something. Timing, termination and resource use, among others, are outside that model, and the build report lists them under `out of model`.

> [!KEY]
> Labeled data leaves a program only through a place that accepts its label, or through a policy that a reviewer can read. The checker does not trust names, comments or intentions: it follows the data.

## 9.1 Labels and how they follow data

### Levels of sensitivity

A label is a level, optionally with categories. The levels, from least to most sensitive, are `public`, `internal`, `confidential`, `secret` and `restricted`. You write a label in front of a type: `confidential Int`, `secret Text`. A type with no label is `public`.

### Each step is a package

Each step is a package, set up as in [chapter 8](/learn/capabilities/#s8-1): `una.toml`, `verification.lock` and the module under `src/`. Then, in the package's directory:

```sh
una check .
una run .
```

### A catalog with a confidential cost

Start with a catalog. The price of a product is public. What the store pays its supplier is confidential, and so is anything computed from it:

:::steps
```una include="steps/01-labels/src/pricing.una" title="steps/01-labels/src/pricing.una" verified="check, run"
module pricing

--- A product of the catalog. What the store pays its supplier is confidential.
kind Product
  sku: Text
  price: Int
  cost: confidential Int

--- The margin of a product, in cents. It is computed from the cost, so it is confidential too.
margin(product: Product) -> confidential Int = product.price - product.cost

--- The tag on the shelf. It reads only public fields, so it is public.
price_tag(product: Product) -> Text = "{product.sku}: {product.price} cents"

pub main() -> Unit
  uses @console: Console[print]
=
  let catalog = [Product(sku: "LAMP-01", price: 4990, cost: 2100), Product(sku: "DESK-02", price: 18900, cost: 12600)]
  for product in catalog
    @console.print(price_tag(product))
  let margins = catalog.map(each: margin)
  @console.print("{margins.len} margins computed")
```

Walkthrough:

1. **`cost: confidential Int`.** A field can carry a label. Every `Product` holds a confidential cost next to a public price.
2. **`margin(product: Product) -> confidential Int`.** The result of `price - cost` joins the labels of its operands, so it is `confidential`. The header must say so: declaring `-> Int` would claim the margin is public, and the checker reports U4001.
3. **`price_tag`.** It reads only `sku` and `price`, which are public, so its result is public. The checker does not label a whole record by its most sensitive field when you read a public field of it.
4. **`margins.len`.** `margins` is a `List[confidential Int]`: the elements are confidential, the list itself is not. How many margins there are is public, so `main` may print it.
:::

`una run .` prints:

```text include="steps/01-labels/expected/output.txt"
LAMP-01: 4990 cents
DESK-02: 18900 cents
2 margins computed
```

### Printing a confidential value

Now print the margins themselves:

```diff include="steps/01-labels..steps/02-leak:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -21,2 +21,2 @@
   let margins = catalog.map(each: margin)
-  @console.print("{margins.len} margins computed")
+  @console.print("margins: {margins}")
```

```text include="steps/02-leak/expected/rendered.txt#L1-L6"
[U4003] Error: `@console.print` accepts `public` data, and this argument is `confidential`
    ╭─[ src/pricing.una:22:18 ]
    │
 22 │   @console.print("margins: {margins}")
    │                  ──────────┬─────────
    │                            ╰─────────── `@console.print` accepts `public` data, and this argument is `confidential`
```

The interpolation `"margins: {margins}"` carries the labels of what it interpolates, so the text is `confidential`, and `Console.print` accepts `public`. The repairs una lists come in order: first send only public data, or send the value to a place that accepts its label; last, release it through a policy, which it marks as an escape. [Section 9.5](#s9-5) shows when that is right.

### Choosing a level

:::decide
**Which to use:**

| The value is… | Label it |
| --- | --- |
| Shown to anyone, such as a price | nothing (`public`) |
| For the store's own systems, such as data read from a file | `internal` |
| Business data, such as costs and margins | `confidential` |
| About a person, such as a name or an address | `secret[PII]`, with a category ([section 9.4](#s9-4)) |
| The most sensitive, such as credentials | `restricted` |
:::

These are conventions, not rules of the language. The checker knows only the order of the levels. Pick the level that matches who may see the data, and keep it the same across a package.

## 9.2 Sinks: where labeled data may go

### Sinks and their ceilings

A sink is a place where data leaves the program: an argument of a capability operation. Each sink has a ceiling, its `accepts` label, and every argument must be at or below it. The ceilings of the host's operations are fixed: `Console.print` accepts `public`, `Files.write` accepts `internal`. An operation you declare accepts `public`, unless its `accepts` clause says more.

### Data from outside is `internal`

Data read from files, the environment or the network is labeled `internal`. `Files.read` returns `internal Text`, and `Env.get` returns `internal` values: a file or an environment variable may hold anything, so the program may pass what it read to the store's own systems, but may not print it.

### Sending a reorder list to the supplier

This step passes a reorder list from a file to the supplier, whose service accepts `internal` data:

:::steps
```una include="steps/03-sinks/src/reorder.una" title="steps/03-sinks/src/reorder.una" verified="check, run"
module reorder

--- The supplier's ordering service. It may receive the store's internal data, and no more.
capability Supplier
  op submit(order: Text) -> Unit
    accepts internal

--- Sends the reorder list to the supplier.
send_list(list: internal Text) -> Unit
  uses @supplier: Supplier[submit]
=
  @supplier.submit(list)

--- A supplier that accepts every order, for this run.
handler accepting() for Supplier
  op submit(order) = unit

pub main() -> Unit
  uses @console: Console[print]
  uses @files: Files[read, write]
=
  @files.write("reorder.csv", content: "LAMP-01,20\nDESK-02,5\n")
    if error use unit
  let list = @files.read("reorder.csv")
    if error use ""
  send_list(list) with @supplier = accepting()
  @console.print("reorder list sent to the supplier")
```

Walkthrough:

1. **`accepts internal`.** The supplier's service is one of the store's own systems, so its operation may receive `internal` data. Without the clause it would accept only `public` data, and the call in `send_list` would be U4003.
2. **`@files.write(…)` then `@files.read(…)`.** A nightly job would write the list and a morning job read it. Here one program does both, with the grant `files:src:read,write`.
3. **`let list = @files.read("reorder.csv")`.** `list` is `internal Text`, whatever the file holds.
4. **`send_list(list: internal Text)`.** The parameter declares the label it receives. `@supplier.submit(list)` checks, because `internal` is at or below `internal`.
5. **`@console.print("reorder list sent to the supplier")`.** The message is a literal, so it is public. Printing `list` here would be U4003.
:::

`una run .` prints:

```text include="steps/03-sinks/expected/output.txt"
reorder list sent to the supplier
```

### How a handler is checked

A handler of an operation is checked for the most sensitive caller its `accepts` allows. So `accepting` may not print what it receives, or print anything at all: a handler of an operation that accepts `internal` data cannot signal that data to a `public` place, even by whether it prints. A fake that does nothing, fails, or returns fixed values stays valid.

### Examples are not sinks

> [!NOTE]
> `expect` lines of examples are not sinks. An example may compare a `secret` result with a value, and `una test .` may print it when the example fails, since a test is the author looking at their own data.

## 9.3 Branches and failures: implicit flows

### Leaking without copying

A value can leak without being copied. If a function returns `0` when a secret is above a threshold and `790` otherwise, the result reveals something about the secret, although `0` and `790` are constants. The checker tracks this with the label of the program counter: inside a branch on labeled data, everything the branch decides carries the condition's label.

### A fee decided by a branch

This step charges a shipping fee. Loyal customers, those who spent at least 50000 cents, ship for free, and what a customer spent is confidential:

:::steps
```una include="steps/04-branches/src/shipping.una" title="steps/04-branches/src/shipping.una" verified="check, run"
module shipping

--- The payment provider. It may receive confidential amounts.
capability Payments
  op charge(order: Text, cents: Int) -> Unit
    accepts confidential

--- The shipping fee, in cents. Loyal customers ship for free. Which branch runs depends on
--- what the customer spent, so the fee is confidential, even though 0 and 790 are not.
shipping_fee(spent: confidential Int) -> confidential Int = if spent >= 50000 then 0 else 790

--- Charges an order's shipping fee.
charge_shipping(order: Text, spent: confidential Int) -> Unit
  uses @payments: Payments[charge]
=
  @payments.charge(order, cents: shipping_fee(spent))

--- A payment provider that accepts every charge, for this run.
handler accepting() for Payments
  op charge(order, cents) = unit

pub main() -> Unit
  uses @console: Console[print]
=
  charge_shipping("A-1001", spent: 72000) with @payments = accepting()
  charge_shipping("A-1002", spent: 1500) with @payments = accepting()
  @console.print("shipping charged for 2 orders")
```

Walkthrough:

1. **`shipping_fee(spent: confidential Int) -> confidential Int`.** The branch is on `spent`, so the fee is `confidential`. Declaring `-> Int` is U4001, at the condition ([a branch that decides a public result](#a-branch-that-decides-a-public-result-u4001) shows it).
2. **`accepts confidential` on `charge`.** The payment provider must receive the fee, so its operation accepts `confidential` data.
3. **`@console.print("shipping charged for 2 orders")`.** `main` prints a constant. It knows how many orders it charged, which depends on nothing confidential.
:::

`una run .` prints:

```text include="steps/04-branches/expected/output.txt"
shipping charged for 2 orders
```

### A failure is a flow too

Whether a function fails is something its caller observes. A `fail` inside a branch on labeled data would reveal the condition to every caller, through the failure. So `fail`, and handling clauses that fail or pass a failure on, are allowed only where the program counter is `public`. Add a free-shipping code that fails for customers who did not spend enough:

```diff include="steps/04-branches..steps/05-fail:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -10,2 +10,13 @@
 shipping_fee(spent: confidential Int) -> confidential Int = if spent >= 50000 then 0 else 790
+
+kind FeeError = | NotEligible
+
+--- The free-shipping code of a loyal customer.
+free_shipping_code(spent: confidential Int) -> confidential Text
+  fails FeeError
+=
+  if spent < 50000
+    fail NotEligible
+  else
+    "FREESHIP"
 
```

```text include="steps/05-fail/expected/rendered.txt#L1-L10"
[U4002] Error: this `fail` depends on `confidential` data, so its failure would reveal it; return a labeled value instead of failing
    ╭─[ src/shipping.una:19:5 ]
    │
 18 │   if spent < 50000
    │      ──────┬──────
    │            ╰──────── the labeled condition
 19 │     fail NotEligible
    │     ────────┬───────
    │             ╰───────── this `fail` depends on `confidential` data, so its failure would reveal it; return a labeled value instead of failing
    │
```

The related location, "the labeled condition", is the branch that raised the program counter. The repair is in the message: return a labeled value instead of failing, such as a `confidential Option[Text]` that is `None` for a customer without the code. The caller then receives the answer with its label, and decides what to do under the same rules.

### Calls under a labeled branch

The same rule covers calls. Under a labeled program counter, a function may call another only if the callee cannot fail and every effect it performs accepts that label. A call to `@console.print` inside `if spent >= 50000` is U4003, since printing at all would reveal the branch.

## 9.4 Categories

### Declaring categories

A level says how sensitive data is. A category says what kind of data it is: `secret[PII] Text` is secret, and it is personal data. A package declares its categories in `una.toml`, under `[labels]`:

```toml include="steps/06-categories/una.toml" title="steps/06-categories/una.toml"
[package]
name = "courier"
version = "0.1.0"
edition = "0.2"

[labels]
categories = ["PII"]

[run]
entry = "courier"
grants = ["console"]
```

### How categories flow and combine

A label flows into another only if its level is at or below the other's, and its categories are among the other's. So `secret[PII]` flows into `secret[PII]` and `restricted[PII]`, but not into `secret`: personal data never loses its category by accident.

When values combine, their labels combine too: the result takes the higher level and every category of either. A text built from a `secret[PII]` phone and a `confidential` total is `secret[PII]`. A label may name several categories, such as `confidential[Location, PII]`, and each must be declared. Categories let a package say which places may receive which kinds of data. A courier may receive personal data and an analytics service may not, even when both accept `secret` data.

### A courier that may receive a phone number

The step books a courier, whose service may receive personal data:

:::steps
```una include="steps/06-categories/src/courier.una" title="steps/06-categories/src/courier.una" verified="check, run"
module courier

--- A stop on a delivery route. The phone number is personal data.
kind Stop
  order: Text
  city: Text
  phone: secret[PII] Text

--- The courier's booking service. It may receive personal data, so that a driver can call
--- the customer at the door.
capability Courier
  op book(order: Text, phone: Text) -> Unit
    accepts secret[PII]

--- Books every stop of a route with the courier.
book_route(stops: List[Stop]) -> Unit
  uses @courier: Courier[book]
=
  for stop in stops
    @courier.book(stop.order, phone: stop.phone)

--- The cities of a route, for the dispatch board. They are public.
cities(stops: List[Stop]) -> List[Text] = stops.map(each: fn(stop) -> stop.city)

--- A courier that accepts every booking, for this run.
handler accepting() for Courier
  op book(order, phone) = unit

pub main() -> Unit
  uses @console: Console[print]
=
  let route = [Stop(order: "A-1001", city: "Recife", phone: "+55 81 5550 0101"), Stop(order: "A-1002", city: "Olinda", phone: "+55 81 5550 0102")]
  book_route(route) with @courier = accepting()
  let board = cities(route).join(separator: ", ")
  @console.print("route booked: {board}")
```

Walkthrough:

1. **`phone: secret[PII] Text`.** A phone number is personal data. The level `secret` and the category `PII` travel with it.
2. **`accepts secret[PII]`.** The courier's booking service needs the phone, so a driver can call at the door. Its ceiling names the category. An operation that `accepts secret` without `PII` would reject the phone with U4003: the category is part of the ceiling.
3. **`@courier.book(stop.order, phone: stop.phone)`.** The order id is public and the phone is `secret[PII]`. Each argument is checked against the ceiling.
4. **`cities`.** It reads only the public `city` field, so the dispatch board, printed by `main`, shows no personal data.
:::

`una run .` prints:

```text include="steps/06-categories/expected/output.txt"
route booked: Recife, Olinda
```

### Undeclared and dropped categories

A category that `[labels] categories` does not declare is U4007, so a misspelt category, such as `PIl`, cannot create a new, unchecked kind of data. Dropping a category is a release like lowering a level: only a policy can do it, and its `to` type shows the label it gives.

## 9.5 Releasing data: policies and trusted modules

### Lowering a label on purpose

Some flows to a lower label are the point of the program. A report must say how many lines a file has. A log should say which customer a notice went to, without the address. A label is lowered only through a `policy`:

```una include="steps/07-policy/src/release.una" title="steps/07-policy/src/release.una" verified="check, run"
trusted module release

--- Releases how many lines a list has, and nothing of what they say.
pub policy line_count
  from internal Text
  to Int
  via count_lines
  purpose "report the size of the reorder list"
  owner purchasing

count_lines(list: internal Text) -> Int = list.split(on: "\n").filter(keep: fn(line) -> line.len > 0).len
```

### The five lines of a policy

A policy has five lines, all required:

| Line | Says |
| --- | --- |
| `from internal Text` | What it accepts, with its label |
| `to Int` | What it gives, with the lower label: here `public`, since there is none |
| `via count_lines` | The function that computes the released value |
| `purpose "…"` | Why the release is needed, in words a reviewer reads |
| `owner purchasing` | Who answers for it |

### `via` functions are trusted code

The `via` function is private to the module, so the policy is the only way to call it. Inside a `via` function the checker does not check labels, since lowering one is its job. Types, refinements and proofs are still checked.

That makes a `via` function trusted code, and it covers what the function does and how it fails, as well as what it returns. A `via` function may declare `uses`, and the policy then has the same `uses`. Its operations stay within those `uses`, but nothing checks the labels of what it sends through them: a `via` function that holds a console could print the raw value it receives, and `una check` would pass. So keep every function of a trusted module small, keep each `via` function pure, with no `uses`, unless the release needs one, such as a keyed hash, and review it line by line. [Reference](#reference) links the rules of the specification that say so.

### Trusted modules

A policy may live only in a trusted module, and a module is trusted only when it says so twice: `trusted module` in its header, and its name under `[trusted] modules` in `una.toml`:

```toml include="steps/07-policy/una.toml" title="steps/07-policy/una.toml"
[package]
name = "reorder"
version = "0.1.0"
edition = "0.2"

[trusted]
modules = ["release"]

[run]
entry = "reorder"
grants = ["console", "files:src:read,write"]
```

Adding a trusted module is a change to the manifest, which a reviewer sees. `una report .` lists every trusted module with its line count, and every call of a policy, with its place, purpose and owner.

### Releasing a count

The program reads the list, which is `internal`, and prints only what the policy releases:

```una include="steps/07-policy/src/reorder.una" title="steps/07-policy/src/reorder.una" verified="check, run"
module reorder

import release (line_count)

pub main() -> Unit
  uses @console: Console[print]
  uses @files: Files[read, write]
=
  @files.write("reorder.csv", content: "LAMP-01,20\nDESK-02,5\n")
    if error use unit
  let list = @files.read("reorder.csv")
    if error use ""
  @console.print("{line_count(list)} SKUs to reorder")
```

`una run .` prints:

```text include="steps/07-policy/expected/output.txt"
2 SKUs to reorder
```

> [!WARNING]
> A policy is trusted code: the guarantee holds only if the `via` function releases what its purpose says and nothing more, through its result, its failures or its effects. Release the least you can, such as a count, a first letter or one yes-or-no answer, and keep `via` functions short enough to review line by line.

### What the U4 codes mean

| Code | Typical cause | Usual repair |
| --- | --- | --- |
| U4001 | A value flowing into a declared type with a lower label: a return, a parameter, a field, an annotated `let` | Raise the declared label, or lower the value through a policy |
| U4002 | A failure, a call that may fail or act, or a policy call, under a branch on labeled data | Return a labeled value instead of failing, or release before the branch |
| U4003 | An argument of an operation above the operation's `accepts`, or an operation under a branch on data above it | Send less, or send it to a place that accepts it, or act outside the branch |
| U4004 | A policy in a module that is not trusted | Move it into a trusted module |
| U4005 | A policy whose `via` function is public, used directly, of the wrong types, or has a `requires` clause | Make `via` private, match the types, drop `requires`, and call the policy |
| U4007 | A category that `una.toml` does not declare | Declare it, or correct its name |

## 9.6 Day-to-day: shipping notices with labels

### What changes from chapter 8

Now the service from chapter 8, with the customers' data labeled. Four changes make it safe: labels on the fields of `Customer`, an `accepts` clause on `Mailer`, a label on the result of `notice`, and a policy in a new trusted module, `privacy`, which `notify` calls. The rest of the program stays as it was.

### Labels on the data

A customer's name and address are personal data:

```una include="day-to-day/src/notices.una#Customer" title="day-to-day/src/notices.una"
--- A customer, as the customer directory knows them. Name and address are personal data.
pub kind Customer
  id: Text
  name: secret[PII] Text
  email: secret[PII] Text
  wants_notices: Bool
```

### A mail service that may receive them

Without `accepts secret[PII]`, the call that sends the notice would be U4003 twice, once for the address and once for the body ([a sink without `accepts`](#a-sink-without-accepts-u4003) shows it).

```una include="day-to-day/src/notices.una#Mailer" title="day-to-day/src/notices.una"
--- The mail service, a service on the network. It may receive personal data.
pub capability Mailer
  op send(to: Text, subject: Text, body: Text) -> Unit
    fails ServiceError
    accepts secret[PII]
```

### A notice that carries the label

The text of the notice holds the customer's name, so its result is `secret[PII] Text`. Only the mail service, which accepts that label, receives it.

```una include="day-to-day/src/notices.una#notice" title="day-to-day/src/notices.una"
--- The text of a shipping notice. It holds the customer's name, so it carries the name's label.
pub notice(customer: Customer, shipment: Shipment) -> secret[PII] Text = "Hello {customer.name}, your order {shipment.order} is on its way with {shipment.carrier}."
```

### The leak the checker stops

In chapter 8, `notify` returned the address it wrote to, and the log printed it. Keep that design, with the label it now needs, and the checker finds the log line:

```diff include="day-to-day..steps/08-leak:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -37,5 +37,4 @@
 
---- Finds the customer of a shipment and emails them the notice. Returns the masked address,
---- which the log may show.
-pub notify(shipment: Shipment) -> Text
+--- Finds the customer of a shipment and emails them the notice. Returns the address.
+pub notify(shipment: Shipment) -> secret[PII] Text
   uses @customers: Customers[find]
@@ -52,3 +51,3 @@
       if error fail MailDown
-    masked_email(customer.email)
+    customer.email
 
@@ -64,3 +63,3 @@
 --- One line of the dispatch log.
-pub log_line(shipment: Shipment, outcome: Result[Text, NoticeError]) -> Text
+pub log_line(shipment: Shipment, outcome: Result[secret[PII] Text, NoticeError]) -> secret[PII] Text
 =
```

```text include="steps/08-leak/expected/rendered.txt#L1-L6"
[U4003] Error: `@log.print` accepts `public` data, and this argument is `secret[PII]`
    ╭─[ src/notices.una:78:16 ]
    │
 78 │     @log.print(log_line(shipment, outcome: outcome))
    │                ──────────────────┬─────────────────
    │                                  ╰─────────────────── `@log.print` accepts `public` data, and this argument is `secret[PII]`
```

The message points at `@log.print`, in `dispatch`, although the address came from `notify`, two functions away. The label followed the address through `notify`'s result, the `Result` of `attempt`, and the text `log_line` built from it.

### The release that is allowed

The operator needs to see which customer each notice went to, not the address itself. A policy in a trusted module, `privacy`, releases a masked form: the first letter of the mailbox and the domain.

```una include="day-to-day/src/privacy.una" title="day-to-day/src/privacy.una" verified="check, run, test"
trusted module privacy

--- Releases what a log may show of an email address: its first letter and its domain.
pub policy masked_email
  from secret[PII] Text
  to public Text
  via mask_email
  purpose "show in the dispatch log which address a notice went to"
  owner support

mask_email(address: secret[PII] Text) -> public Text
=
  let parts = address.split(on: "@")
  if parts.len != 2 or address.len < 3
    "(hidden)"
  else
    let domain = parts.at(index: 1)
      if none use ""
    "{address.slice(start: 0, end: 1)}***@{domain}"
```

`mask_email` never returns more than one character of the mailbox. An address it cannot read is hidden whole, rather than shown in part. `notify` is the only function that needs the raw address, so it is where the release happens: it sends the real address to the mail service, then returns the masked form, which is public. The rest of the program never holds the address, so the log line is public too:

```una include="day-to-day/src/notices.una#notify" title="day-to-day/src/notices.una"
--- Finds the customer of a shipment and emails them the notice. Returns the masked address,
--- which the log may show.
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
    masked_email(customer.email)
```

Look at what did not change in `notify`. It still fails with `OptedOut` and `UnknownCustomer`, because the conditions it branches on, the `Option` from the directory and the field `wants_notices`, are public. Reading `customer.email` gives a `secret[PII] Text`, while `customer.wants_notices` stays a public `Bool`: a field keeps its own label. A branch on the address itself, followed by a `fail`, would be U4002, as [exercise 3](#exercise-3-a-blocked-domain) shows.

The call of the policy obeys the same rule as a `fail`. It runs where the program counter is `public`: after the checks of the directory and of `wants_notices`, which are public. A call of `masked_email` inside a branch on labeled data would be U4002 too, since its public result would reveal the condition. Put each release on a path that public data alone decides.

### The manifest

The manifest declares the category and the trusted module:

```toml include="day-to-day/una.toml" title="day-to-day/una.toml"
[package]
name = "notices"
version = "0.1.0"
edition = "0.2"

[labels]
categories = ["PII"]

[trusted]
modules = ["privacy"]

[run]
entry = "notices"
grants = ["console"]
```

### Running it

`una run .` prints the log shown in [What you'll build](#what-youll-build). `una report .` lists every call of `privacy.masked_email` under `information`, with its place, purpose and owner: the one in `notify`, and the two in the policy's examples ([section 9.7](#s9-7)). It lists `privacy` under `tcb`, with its line count, as the code the guarantee trusts. The handlers, `dispatch`, `log_line` and `main` are those of chapter 8, unchanged.

So the whole change from chapter 8 is three labels, one `accepts` clause, one call of a policy and a module of 19 lines. In exchange, a later change outside the trusted module that prints a name or an address fails `una check` instead of reaching the log. The `via` functions are the exception: their labels are not checked ([section 9.5](#s9-5)). A reviewer who wants to know what personal data leaves the program reads the `accepts` clauses and the trusted module, line by line, and not every other line.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/notices.una" title="day-to-day/src/notices.una" caption="the whole program" verified="check, run, test"
module notices

import privacy (masked_email)

--- A customer, as the customer directory knows them. Name and address are personal data.
pub kind Customer
  id: Text
  name: secret[PII] Text
  email: secret[PII] Text
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

--- The mail service, a service on the network. It may receive personal data.
pub capability Mailer
  op send(to: Text, subject: Text, body: Text) -> Unit
    fails ServiceError
    accepts secret[PII]

--- The text of a shipping notice. It holds the customer's name, so it carries the name's label.
pub notice(customer: Customer, shipment: Shipment) -> secret[PII] Text = "Hello {customer.name}, your order {shipment.order} is on its way with {shipment.carrier}."

--- Finds the customer of a shipment and emails them the notice. Returns the masked address,
--- which the log may show.
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
    masked_email(customer.email)

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
  expect result == "r***@example.invalid"
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

example "the log shows the first letter and the domain of an address"
  do masked_email("tomas@example.invalid")
  expect result == "t***@example.invalid"

example "an address the mask cannot read is hidden"
  do masked_email("no address")
  expect result == "(hidden)"
```

## 9.7 Testing it

### Examples of the policy

The examples of chapter 8 still pass, with one change: the first one now expects the masked address, `r***@example.invalid`, which is what `notify` returns. Two new examples test the policy itself:

```una include="day-to-day/src/notices.una#L159-L165" title="day-to-day/src/notices.una" caption="the policy's examples"
example "the log shows the first letter and the domain of an address"
  do masked_email("tomas@example.invalid")
  expect result == "t***@example.invalid"

example "an address the mask cannot read is hidden"
  do masked_email("no address")
  expect result == "(hidden)"
```

A policy can be called like a function, so its examples need no fakes. Test the release the way a reviewer would read it: what an ordinary value becomes, and what an unexpected one becomes. A mask that showed a whole malformed address would pass the type checker, since labels are not checked inside `via`, so this example is the check that it does not.

### Examples can observe a secret

An `expect` line compares a value whatever its label, and a `do` line is checked like ordinary code: an example can observe a secret, but cannot send it anywhere the program itself could not.

### The failure paths and their fakes

The examples of the failure paths are those of chapter 8, unchanged: labels do not alter which paths exist or how a fake reaches them. The fakes `outbox` and `mail_down` are handlers of `Mailer`, which now accepts `secret[PII]`. They pass the check because they do nothing with what they receive. A fake mail service that printed each message, as `printed` in chapter 8 did, would be U4003: what it prints could reveal the notice.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L11"
example notices "a customer who wants notices gets one" ... ok
example notices "an unknown customer gets no mail" ... ok
example notices "a customer who asked for no notices gets no mail" ... ok
example notices "a directory that does not answer is DirectoryDown, and no mail is sent" ... ok
example notices "a mail service that does not answer is MailDown" ... ok
example notices "the batch logs every shipment, even when the mail service is down" ... ok
example notices "the log shows the first letter and the domain of an address" ... ok
example notices "an address the mask cannot read is hidden" ... ok

8 examples: 8 passed, 0 failed
```

## 9.8 Common mistakes

Each mistake below is a small change to the day-to-day program or to a step of this chapter, as it says.

### Dropping a label in a return type (U4001)

:::mistake
In [step 01](#a-catalog-with-a-confidential-cost), declare the margin as a plain `Int`:

```diff include="steps/01-labels..mistakes/1:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -9,3 +9,3 @@
 --- The margin of a product, in cents. It is computed from the cost, so it is confidential too.
-margin(product: Product) -> confidential Int = product.price - product.cost
+margin(product: Product) -> Int = product.price - product.cost
 
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U4001] Error: the result of `margin` is `Int`, and this value is `confidential Int`: a flow from `confidential` to `public`
```

*Why:* `product.cost` is `confidential`, so the difference is too, and a result is checked against the declared label.

*Fix:* declare `confidential Int`. A header is where callers learn what they receive.
:::

### A sink without `accepts` (U4003)

:::mistake
Remove `accepts secret[PII]` from `Mailer`:

```diff include="day-to-day..mistakes/2:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -32,3 +32,2 @@
     fails ServiceError
-    accepts secret[PII]
 
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U4003] Error: `@mailer.send` accepts `public` data, and this argument is `secret[PII]`
```

*Why:* an operation accepts `public` data unless it says more. una reports the address and the body, one diagnostic each.

*Fix:* give the operation the ceiling of the service it stands for. Do not lower the data to fit: the mail service needs the real address.
:::

### A branch that decides a public result (U4001)

:::mistake
In [step 04](#a-fee-decided-by-a-branch), declare the fee as a plain `Int`:

```diff include="steps/04-branches..mistakes/3:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -9,3 +9,3 @@
 --- what the customer spent, so the fee is confidential, even though 0 and 790 are not.
-shipping_fee(spent: confidential Int) -> confidential Int = if spent >= 50000 then 0 else 790
+shipping_fee(spent: confidential Int) -> Int = if spent >= 50000 then 0 else 790
 
```

```text include="mistakes/3/expected/rendered.txt#L1"
[U4001] Error: the result of `shipping_fee` is `public`, and which value it returns depends on this `confidential` condition: a flow from `confidential` to `public`
```

*Why:* the fee is a constant in each branch, but which branch runs depends on `spent`.

*Fix:* declare `confidential Int`. The diagnostic points at the condition, since that is where the information enters.
:::

### A category that is not declared (U4007)

:::mistake
In [step 06](#declaring-categories), remove the `[labels]` table from `una.toml`:

```diff include="steps/06-categories..mistakes/4:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -5,5 +5,2 @@
 
-[labels]
-categories = ["PII"]
-
 [run]
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U4007] Error: label category `PII` is not declared in `[labels] categories` of `una.toml`
```

*Why:* each package declares its categories, so a typo cannot create one.

*Fix:* declare `categories = ["PII"]` under `[labels]`.
:::

### A trusted module that `una.toml` does not list (U7005)

:::mistake
Remove the `[trusted]` table of the day-to-day program:

```diff include="day-to-day..mistakes/5:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -8,5 +8,2 @@
 
-[trusted]
-modules = ["privacy"]
-
 [run]
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U7005] Error: module `privacy` is `trusted` in its header but not listed in una.toml [trusted] modules
```

*Why:* trust is declared twice, in the module and in the manifest, so that adding it shows in review.

*Fix:* list the module under `[trusted] modules`, after a review of what it releases.
:::

### A public `via` function (U4005)

:::mistake
Make `mask_email` public:

```diff include="day-to-day..mistakes/6:src/privacy.una" context="1" title="src/privacy.una"
--- a/src/privacy.una
+++ b/src/privacy.una
@@ -10,3 +10,3 @@
 
-mask_email(address: secret[PII] Text) -> public Text
+pub mask_email(address: secret[PII] Text) -> public Text
 =
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U4005] Error: the `via` function of a policy is private to its trusted module, and `mask_email` is not; remove its `pub`, or declare it in this module
```

*Why:* a public `via` function would release data without the policy, so its calls would be missing from the report.

*Fix:* keep `via` private, and call the policy, `masked_email`.
:::

## 9.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added, and a stub when there is one. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`.

### Exercise 1: release the domain

::::exercise
The operations team counts notices by mail provider, so it needs the domain of each address, and nothing else. Add a policy `email_domain` to `privacy.una`, from `secret[PII] Text` to `public Text`, that gives the part after the `@`, or `(none)` when there is no single `@`. The start package already imports it, so `una check .` reports U1001 until it exists, and it ends with:

```una include="exercises/1/start/src/notices.una#L167-L173" title="exercises/1/start/src/notices.una"
example "the domain of an address"
  do email_domain("rosa@example.invalid")
  expect result == "example.invalid"

example "an address with no domain has none"
  do email_domain("no address")
  expect result == "(none)"
```

:::hint
*Hint:* `masked_email` already splits an address on `@`. A policy needs a purpose and an owner too.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Add the policy and its `via` function to `privacy.una`:

```diff include="exercises/1/start..exercises/1/answer:src/privacy.una" context="1" title="src/privacy.una"
--- a/src/privacy.una
+++ b/src/privacy.una
@@ -19 +19,18 @@
     "{address.slice(start: 0, end: 1)}***@{domain}"
+
+--- Releases the domain of an email address, and nothing of the mailbox.
+pub policy email_domain
+  from secret[PII] Text
+  to public Text
+  via domain_of
+  purpose "count notices by mail provider"
+  owner support
+
+domain_of(address: secret[PII] Text) -> public Text
+=
+  let parts = address.split(on: "@")
+  if parts.len != 2
+    "(none)"
+  else
+    parts.at(index: 1)
+      if none use "(none)"
```

`una test .` reports 10 examples passing.
:::
::::

### Exercise 2: priority notices

::::exercise
Some customers have a priority flag, which the store keeps `confidential`. Their notice's subject is `Priority: order A-1001 has shipped` instead of `Order A-1001 has shipped`. The start package adds the field `vip: confidential Bool` to `Customer`, uses `subject` in `notify`, and has a stub of it that ignores the flag:

```una include="exercises/2/start/src/notices.una#subject" title="exercises/2/start/src/notices.una"
--- The subject of a notice. Exercise 2: mark it `Priority:` for a priority customer.
pub subject(customer: Customer, shipment: Shipment) -> confidential Text = "Order {shipment.order} has shipped"
```

and these examples:

```una include="exercises/2/start/src/notices.una#L171-L177" title="exercises/2/start/src/notices.una"
example "a priority customer's subject says so"
  do subject(Customer(id: "C-17", name: "Rosa", email: "rosa@example.invalid", wants_notices: true, vip: true), shipment: Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect result == "Priority: order A-1001 has shipped"

example "another customer's subject is plain"
  do subject(Customer(id: "C-20", name: "Tomas", email: "tomas@example.invalid", wants_notices: true, vip: false), shipment: Shipment(order: "A-1002", customer: "C-20", carrier: "Parcelo"))
  expect result == "Order A-1002 has shipped"
```

:::hint
*Hint:* an `if … then … else …` on `customer.vip`. Keep the result type: try `-> Text` once, and read what the checker says.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/2/start/expected/commands/test.txt#L10-L12,L15"
example notices "a priority customer's subject says so" ... FAILED
  src/notices.una:173: expect result == "Priority: order A-1001 has shipped"
  it is false, with `result` = `"Order A-1001 has shipped"`
10 examples: 9 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Branch on the flag:

```diff include="exercises/2/start..exercises/2/answer:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -38,4 +38,4 @@
 
---- The subject of a notice. Exercise 2: mark it `Priority:` for a priority customer.
-pub subject(customer: Customer, shipment: Shipment) -> confidential Text = "Order {shipment.order} has shipped"
+--- The subject of a notice. It is decided by the confidential `vip` flag, so it is confidential.
+pub subject(customer: Customer, shipment: Shipment) -> confidential Text = if customer.vip then "Priority: order {shipment.order} has shipped" else "Order {shipment.order} has shipped"
 
```

The subject is `confidential` because a confidential flag chose it. The mail service accepts `secret[PII]`, which is above `confidential`, so the subject may go there, and nowhere public.
:::
::::

### Exercise 3: a blocked domain

::::exercise
A partner sends its own notices to the addresses at `blocked.example.invalid`, so the store must not mail them. The start package adds the variant `Blocked(id: Text)`, a customer at that domain, and this example:

```una include="exercises/3/start/src/notices.una#L169-L174" title="exercises/3/start/src/notices.una"
example "an address at a blocked domain gets no mail"
  given @customers = directory(sample_customers())
  given @mailer = outbox()
  do notify(Shipment(order: "A-1006", customer: "C-30", carrier: "Parcelo"))
  expect fails Blocked
  expect not performed @mailer.send
```

The direct way, a branch on `customer.email.ends_with(suffix: "@blocked.example.invalid")` in `notify`, does not check. Among the diagnostics una reports:

```text include="exercises/3/direct/expected/rendered.txt#L10"
[U4002] Error: this `fail` depends on `secret[PII]` data, so its failure would reveal it; return a labeled value instead of failing
```

:::hint
*Hint:* `notify` needs one public fact about the address: is it at the blocked domain? A policy can release exactly that bit, and `notify` can branch on a public `Bool` and fail.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Add a policy to `privacy.una` that releases one `Bool`:

```diff include="exercises/3/start..exercises/3/answer:src/privacy.una" context="1" title="src/privacy.una"
--- a/src/privacy.una
+++ b/src/privacy.una
@@ -19 +19,11 @@
     "{address.slice(start: 0, end: 1)}***@{domain}"
+
+--- Releases one fact about an address: whether it is at the blocked domain.
+pub policy blocked_domain
+  from secret[PII] Text
+  to public Bool
+  via is_blocked
+  purpose "skip the domain whose notices a partner sends"
+  owner support
+
+is_blocked(address: secret[PII] Text) -> public Bool = address.ends_with(suffix: "@blocked.example.invalid")
```

Import it in `notices.una`, and branch on it in `notify`:

```diff include="exercises/3/start..exercises/3/answer:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -2,3 +2,3 @@
 
-import privacy (masked_email)
+import privacy (blocked_domain, masked_email)
 
@@ -49,2 +49,4 @@
     fail OptedOut(id: customer.id)
+  else if blocked_domain(customer.email)
+    fail Blocked(id: customer.id)
   else
```

The policy releases one bit of personal data, on purpose, and the report lists the call. Without it, the `fail` would reveal that same bit to every caller with nothing to show for it in review.
:::
::::

## 9.10 Recap and reference

### For agents

:::agents
`una --json check .` reports the U4xxx codes in the domain `security`. For [the leak the checker stops](#the-leak-the-checker-stops):

```json include="steps/08-leak/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U4003","severity":"error","domain":"security","message":"`@log.print` accepts `public` data, and this argument is `secret[PII]`","primary":{"file":"src/notices.una","start":{"line":78,"col":16},"end":{"line":78,"col":52}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"send `@log.print` only data labeled `public` or lower, or send this value to an operation that accepts `secret[PII]`","edit":null},{"rank":2,"escape_cost":1,"escape":{"kind":"trusted","cost":"the guarantee then rests on trusted code, whose labels are not checked: a policy releases the data, or a module joins the trusted base; it is listed in the build report and needs review"},"description":"declassify the value through a policy of a trusted module","edit":null}],"explain":"una explain U4003"}],"fixable":0}
```

Neither repair has an `edit`, so `una fix` changes nothing: each needs a decision about the data. The first keeps the label. The second, a policy, has `escape_cost` 1 and an `escape` of kind `trusted`: it moves the guarantee onto trusted code. Prefer the repairs with `escape_cost` 0. The compact rule: *a value flows only to a place labeled at or above it, branches label what they decide, `fail` needs a `public` program counter, and only a `policy` of a module trusted in its header and in `una.toml` lowers a label.*
:::

### Recap

:::recap
- A label is a level and categories: `public`, `internal`, `confidential`, `secret`, `restricted`, and categories such as `[PII]` that `una.toml` declares.
- A result carries the labels of what it was computed from, and of every condition that chose it.
- Every operation argument is a sink. `Console.print` accepts `public`, and your own operations accept what `accepts` says.
- Data read from files or the environment is `internal`.
- Under a branch on labeled data, return a labeled value instead of failing.
- Lower a label only through a `policy` with a private `via` function, in a module trusted in its header and in `una.toml`.
- Release the least you can, test each policy with examples, and read the release list in `una report .`.
:::

### Reference

:::reference
- Construct pages: [labels](/docs/language/information-flow/labels/), [`policy`](/docs/language/information-flow/policy/), [trusted modules](/docs/language/information-flow/trusted/), [host capabilities](/docs/language/capabilities/host/), [`example`](/docs/language/examples/example/)
- Configuration: [`[labels] categories`](/docs/configure/labels/categories/), [`[trusted] modules`](/docs/configure/trusted/modules/)
- Standard library: [the prelude and the host capabilities](/docs/std/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U4001](/docs/errors/U4001/), [U4002](/docs/errors/U4002/), [U4003](/docs/errors/U4003/), [U4004](/docs/errors/U4004/), [U4005](/docs/errors/U4005/), [U4007](/docs/errors/U4007/), [U7005](/docs/errors/U7005/)
- Specification: [information flow](/docs/spec/07-information-flow/), including [declassification policies](/docs/spec/07-information-flow/#s5) (rule 3: inside `via` functions labels are not checked, and they are part of the trusted computing base) and [checking](/docs/spec/07-information-flow/#s7) (rules 5 and 6), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [standard library](/docs/spec/14-standard-library/), [diagnostics and ABI](/docs/spec/13-diagnostics-and-abi/)
- Security model: [what is proven, trusted and outside the model](/docs/security/)
:::
