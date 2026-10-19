---
learn: "17"
title: Information flow
editions: ["0.2"]
codes: [U1001, U2001, U3015, U4001, U4002, U4003, U4004, U4005, U4007, U7005]
time: 58
builds: The shipping-notice service with customer data labeled, and a policy that releases a masked address to the log
prerequisites: ["7", "10", "12", "14"]
template: 2
nav: ["Labels and how they follow data", "Sinks", "Implicit flows", "Categories", "Policies and trusted modules", "Day-to-day: labeled notices", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 17 Information flow


The shipping-notice service of [chapter 12](/learn/capabilities/) prints customers' email addresses in its log. Nothing stopped it: the address is a `Text` like any other. In Una you can say how sensitive a value is with a label, such as `secret[PII]`, and the checker follows that label through every computation, every branch and every call. Labeled data reaches a log, a file or a service only if that place accepts its label. This chapter labels data, shows where the checker stops it, and releases what may legitimately go out through a declared policy.

## What you'll build

:::build
The dispatch step of [chapter 12](/learn/capabilities/#s12-5), with the customers' names and addresses labeled as personal data. The mail service may receive them. The log may not, so it shows each address masked, through a policy that a reviewer can find in one place:

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
- recognize data without keeping it, with a keyed hash, a `Hashed`;
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

What the checker guarantees is called **noninterference**, and it has a precise scope. An observer who sees only what reaches `public` places, such as the console, sees the same output from two runs whose labeled inputs differ, unless a policy released something. Timing, termination and resource use, among others, are outside that model ([What the checker promises](#what-the-checker-promises)).

> [!KEY]
> Labeled data leaves a program only through a place that accepts its label, or through a policy that a reviewer can read. The checker does not trust names, comments or intentions: it follows the data.

## 17.1 Labels and how they follow data


### What a label is

An office stamps some folders "confidential" and some "for internal use only". The stamp travels with the folder, and anyone who copies a page from it copies the stamp too. A clerk at the front desk sees the stamp and knows that the folder stays behind the counter.

A **label** is that stamp, on a value. It says how sensitive the value is, and who may see it. In Una a label is part of a value's **type**, the description of what the value is ([chapter 2](/learn/numbers/#s2-1)): `Int` is a whole number, and `confidential Int` is a whole number that is confidential. The checker reads the label wherever the value goes.

A label has a **level**. Una has five, from least to most sensitive:

| Level | Meant for |
| --- | --- |
| `public` | anyone, such as a price on the shelf |
| `internal` | the store's own systems, such as a file the program read |
| `confidential` | business data, such as what the store pays its supplier |
| `secret` | data about people, such as a phone number |
| `restricted` | the most sensitive data, such as credentials |

A type with no label is `public`. A label may also name **categories**, which say what kind of data a value is, such as `secret[PII] Text` for personal data. [Section 17.4](#s17-4) covers categories; until then, a label is just a level.

The checker knows only the order of the levels: `public` is below `internal`, which is below `confidential`, and so on up to `restricted`. What each level is meant for, in the right-hand column, is a convention you choose for your store, not a rule of the language.

### Why a program needs labels

Each example of this chapter is a package, made as [chapter 2](/learn/numbers/#each-step-is-a-package) explains, and the chapter's download, `17-information-flow.tar.gz`, holds them all.

Here is a catalog with no labels. The store sells each product at its `price`, and pays its supplier its `cost`. The difference, the margin, is business data the store would rather not show to customers:

```una include="steps/01-no-labels/src/pricing.una" title="steps/01-no-labels/src/pricing.una" verified="check, run"
module pricing

--- A product of the catalog: its SKU, the price customers pay, and what the store pays its supplier.
kind Product
  sku: Text
  price: Int
  cost: Int

--- The margin of a product, in cents.
margin(product: Product) -> Int = product.price - product.cost

pub main() -> Unit
  uses @console: Console[print]
=
  let catalog = [Product(sku: "LAMP-01", price: 4990, cost: 2100), Product(sku: "DESK-02", price: 18900, cost: 12600)]
  let margins = catalog.map(each: margin)
  @console.print("margins: {margins}")
```

`una run .` prints:

```text include="steps/01-no-labels/expected/output.txt"
margins: [2890, 6300]
```

The program checks, runs, and prints every margin to the console. Nothing in it says that `cost` is sensitive, so nothing can stop the margins from going out. In a real store this line could be a debug print, a line in a log that a support team reads, or a field in a web page. A comment on `cost` would not help: the checker does not read comments, and the person who adds the print may never see it.

A label makes the rule part of the program. Once `cost` is `confidential Int`, every value computed from it is confidential too, and the console refuses it. You will see that refusal in [Printing a confidential value](#printing-a-confidential-value).

### How to write a label

You write a label in front of the type it applies to: `confidential Int`, `secret Text`. A label goes anywhere a type goes. The next step shows each place, one function per form, and checks every one with an example.

#### On a field

A field of a kind ([chapter 4](/learn/kinds/#s4-1)) can carry a label. Every value of the kind then holds a labeled value in that field, next to its unlabeled ones:

```una include="steps/02-label-forms/src/pricing.una#UnitCost" title="steps/02-label-forms/src/pricing.una"
--- What the store pays its supplier for one unit of a SKU. A label on a field: the amount is
--- confidential.
kind UnitCost
  sku: Text
  cents: confidential Int
```

`sku` is public and `cents` is confidential, in the same record.

#### On a parameter and on the result

A parameter's label says what the function receives; the result's label says what the caller gets back:

```una include="steps/02-label-forms/src/pricing.una#landed" title="steps/02-label-forms/src/pricing.una"
--- A label on a parameter and on the result: the cost of a unit once freight is paid.
landed(cost: confidential Int, freight: Int) -> confidential Int = cost + freight
```

`freight` has no label, so it is public. The header says the result is `confidential Int`, which is what `cost + freight` is.

#### On an annotated `let`

A `let` may state the type of the value it names, after a colon. That type can carry a label:

```una include="steps/02-label-forms/src/pricing.una#batch" title="steps/02-label-forms/src/pricing.una"
--- A label on an annotated `let`: what a batch of units costs the store.
batch(item: UnitCost, quantity: Int) -> confidential Int
=
  let total: confidential Int = item.cents * quantity
  total
```

`let total: confidential Int` says, at that line, that `total` is confidential. Without the annotation, `total` would take the type of its value, `confidential Int`, anyway.

#### Inside another type

A label may stand inside a type that holds other types, such as a list. `List[confidential Int]` is a list whose elements are confidential:

```una include="steps/02-label-forms/src/pricing.una#cost_list" title="steps/02-label-forms/src/pricing.una"
--- A label inside a type: the list is public, and each element is confidential.
cost_list(items: List[UnitCost]) -> List[confidential Int] = items.map(each: fn(item) -> item.cents)
```

The elements are confidential, and the list itself is not: how many costs there are is public.

#### On a whole list

A label in front of `List` labels the list as a whole, its length included:

```una include="steps/02-label-forms/src/pricing.una#renegotiating" title="steps/02-label-forms/src/pricing.una"
--- A label on the whole list: which SKUs the store is renegotiating with its supplier.
renegotiating() -> confidential List[Text] = ["DESK-02"]
```

Which SKUs the store is renegotiating is confidential, and so is how many there are.

#### `public`, written out

`public` is a level like the others, and you may write it. It means the same as no label:

```una include="steps/02-label-forms/src/pricing.una#shelf_name" title="steps/02-label-forms/src/pricing.una"
--- `public` written out, which means the same as no label.
shelf_name(item: UnitCost) -> public Text = item.sku
```

Write it where a reader might wonder, such as on the result of a function that takes labeled data and gives a public answer. [Section 17.5](#s17-5) does that.

#### Running the label forms

`main` prints only public facts: the SKUs, and how many costs are on file. The examples look at the labeled values themselves. An `expect` line of an example may compare a labeled value, since a test is the author looking at their own data ([Examples are not sinks](#examples-are-not-sinks) says more):

```una include="steps/02-label-forms/src/pricing.una#L34-L48" title="steps/02-label-forms/src/pricing.una" caption="the examples"
example "a lamp that costs 21.00, with 3.50 of freight"
  do landed(2100, freight: 350)
  expect result == 2450

example "three desks"
  do batch(UnitCost(sku: "DESK-02", cents: 12600), quantity: 3)
  expect result == 37800

example "the costs of two SKUs, in order"
  do cost_list([UnitCost(sku: "LAMP-01", cents: 2100), UnitCost(sku: "DESK-02", cents: 12600)])
  expect result == [2100, 12600]

example "one SKU is being renegotiated"
  do renegotiating()
  expect result.len == 1
```

`una run .` prints:

```text include="steps/02-label-forms/expected/output.txt"
LAMP-01 and DESK-02: 2 costs on file
```

and `una test .` prints:

```text include="steps/02-label-forms/expected/commands/test.txt#L2-L7"
example pricing "a lamp that costs 21.00, with 3.50 of freight" ... ok
example pricing "three desks" ... ok
example pricing "the costs of two SKUs, in order" ... ok
example pricing "one SKU is being renegotiated" ... ok

4 examples: 4 passed, 0 failed
```

### A catalog with a confidential cost

Now the catalog of [Why a program needs labels](#why-a-program-needs-labels), with its cost labeled. The price of a product is public. What the store pays its supplier is confidential, and so is anything computed from it:

:::steps
```una include="steps/03-labels/src/pricing.una" title="steps/03-labels/src/pricing.una" verified="check, run"
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

```text include="steps/03-labels/expected/output.txt"
LAMP-01: 4990 cents
DESK-02: 18900 cents
2 margins computed
```

### What the checker promises

`main` reads both costs to compute the margins. Would its output change if the costs did? Change them, and run it again. Here the lamp costs the store 40.00 instead of 21.00, and the desk 0.01 instead of 126.00:

```diff include="steps/03-labels..steps/37-other-costs:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -17,3 +17,3 @@
 =
-  let catalog = [Product(sku: "LAMP-01", price: 4990, cost: 2100), Product(sku: "DESK-02", price: 18900, cost: 12600)]
+  let catalog = [Product(sku: "LAMP-01", price: 4990, cost: 4000), Product(sku: "DESK-02", price: 18900, cost: 1)]
   for product in catalog
```

`una run .` prints:

```text include="steps/37-other-costs/expected/output.txt"
LAMP-01: 4990 cents
DESK-02: 18900 cents
2 margins computed
```

These are the three lines that the catalog of [A catalog with a confidential cost](#a-catalog-with-a-confidential-cost) printed, character for character. The margins are very different, and nothing on the console shows it. That is not luck with these numbers. The checker accepts this program, and the program releases nothing, so no other costs could change what it prints, as long as the run finishes.

This promise is called **noninterference**: values with a high label do not *interfere* with what can be seen at a lower one. An **observer** is whoever reads one place where data leaves the program: the person who reads the console sees `public` data, and a service that accepts `internal` data sees data up to `internal`. The promise holds for every observer. Take two runs whose data is the same at the observer's label and below, and differs only above it: the observer sees the same thing in both. What an observer can see is what the program returns, the failures it reports, the arguments it passes to operations, and whether an operation runs at all.

The promise has three limits:

- **What a policy releases.** A policy lowers a label on purpose ([section 17.5](#s17-5)), so what it releases may differ between two runs. The build report lists every release, so you can see each one.
- **Runs that finish.** The promise compares runs that end. A run that stops early, for instance because it runs out of memory, may stop at a point that depends on a labeled value.
- **What the model covers.** Some ways of learning about data are outside it, such as how long a run takes and how much memory it uses: a run that is slower for some costs shows that to anyone who times it. The build report lists them under `out of model` ([What the build report shows](#what-the-build-report-shows)), and [the security model](/docs/security/) describes each one.

### How labels follow data

The checker gives every value a label, and follows it through each step of the program. These are the rules, each with the example that shows it.

#### A literal is public

A value written in the program, such as `4990`, `"LAMP-01"` or `true`, is `public`. Anyone who reads the program can see it, so it reveals nothing.

#### Combining values joins their labels

When a computation uses several values, its result takes the highest of their levels. This is called the **join** of the labels. `product.price - product.cost` joins `public` and `confidential`, so the margin is `confidential`. `cost + freight` in `landed` is `confidential` for the same reason. The rule holds for arithmetic (`+`, `-`, `*`, `/`), comparisons (`==`, `<`, `>=`), the logical operators (`and`, `or`, `not`), and interpolation: `"margin {margin(product)}"` is a confidential text.

#### A field keeps its own label

Reading a field gives the field's label, raised by the label of the record it comes from. `product.sku` is public and `product.cost` is confidential, from the same `product`. That is why `price_tag` is public: it reads only public fields.

#### Length, and the label of a whole

`.len` has the label of the whole it measures, not of its elements. `cost_list(...).len` is public, since the list of costs is public and only its elements are labeled. `renegotiating().len` is confidential, since the whole list is labeled.

Whole values work the same way. Comparing two products with `==`, or interpolating a whole product with `"{product}"`, reads every field, `cost` included. So both results carry the label of the most sensitive field of the kind. (Interpolating a whole record needs edition `0.2`, [chapter 19](/learn/editions/).)

#### A declared type is a checkpoint

A value may flow into a place with a declared type only if its label is at or below the declared one. Every declared type is such a place: a parameter, a result, a field, and an annotated `let`. Here the annotated `let` of `batch` says `Int`, and the value is confidential:

```diff include="steps/02-label-forms..steps/04-let-flow:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -14,3 +14,3 @@
 =
-  let total: confidential Int = item.cents * quantity
+  let total: Int = item.cents * quantity
   total
```

`una check .` reports:

```text include="steps/04-let-flow/expected/rendered.txt"
[U4001] Error: `total` is `Int`, and this value is `confidential Int`: a flow from `confidential` to `public`
    ╭─[ src/pricing.una:15:20 ]
    │
 15 │   let total: Int = item.cents * quantity
    │                    ──────────┬──────────
    │                              ╰──────────── `total` is `Int`, and this value is `confidential Int`: a flow from `confidential` to `public`
    │
    │ Note: run `una explain U4001` for an explanation
────╯
```

Read it from the top. `[U4001]` is the code of a flow into a declared type with a lower label. The message names the place, `` `total` is `Int` ``, and the value, `` `confidential Int` ``. The mark under line 15 points at the value, not at the name. The last clause, *a flow from `confidential` to `public`*, says which way the information would move. The repair is one of two: raise the declared label to `confidential Int`, or lower the value on purpose through a policy, a declared release ([section 17.5](#s17-5)).

### Printing a confidential value

Now print the margins themselves, as [Why a program needs labels](#why-a-program-needs-labels) did:

```diff include="steps/03-labels..steps/05-leak:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -21,2 +21,2 @@
   let margins = catalog.map(each: margin)
-  @console.print("{margins.len} margins computed")
+  @console.print("margins: {margins}")
```

```text include="steps/05-leak/expected/rendered.txt#L1-L10"
[U4003] Error: `@console.print` accepts `public` data, and this argument is `confidential`
    ╭─[ src/pricing.una:22:18 ]
    │
 22 │   @console.print("margins: {margins}")
    │                  ──────────┬─────────
    │                            ╰─────────── `@console.print` accepts `public` data, and this argument is `confidential`
    │
    │ Help 1: repair 1: send `@console.print` only data labeled `public` or lower, or send this value to an operation that accepts `confidential`
    │
    │ Help 2: repair 2 (escape: trusted; the guarantee then rests on trusted code, whose labels are not checked: a policy releases the data, or a module joins the trusted base; it is listed in the build report and needs review): declassify the value through a policy of a trusted module
```

The interpolation `"margins: {margins}"` carries the labels of what it interpolates, so the text is `confidential`, and `Console.print` accepts `public`. The place where data leaves the program, the **sink**, is the subject of [section 17.2](#s17-2). The repairs una lists, in the Help lines, come in order: first send only public data, or send the value to a place that accepts its label; last, release it through a policy, which it marks as an escape. [Section 17.5](#s17-5) shows when that is right.

### Choosing a level

:::decide
**Which to use:**

| The value is… | Label it |
| --- | --- |
| Shown to anyone, such as a price | nothing (`public`) |
| For the store's own systems, such as data read from a file | `internal` |
| Business data, such as costs and margins | `confidential` |
| About a person, such as a name or an address | `secret[PII]`, with a category ([section 17.4](#s17-4)) |
| The most sensitive, such as credentials | `restricted` |
:::

These are conventions, not rules of the language. The checker knows only the order of the levels. Pick the level that matches who may see the data, and keep it the same across a package. When in doubt between two levels, pick the higher one: a label that is too high costs you a policy later, and a label that is too low lets data out.

### Check yourself: labels

Each question changes the catalog of [A catalog with a confidential cost](#a-catalog-with-a-confidential-cost). Decide whether `una check .` passes, and if not, which code it reports and where.

First, a line for the buyer's sheet, printed for each product:

```diff include="steps/03-labels..steps/06-sheet-line:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -14,2 +14,5 @@
 
+--- A line of the buyer's sheet: what a product costs the store, and what it sells for.
+sheet_line(product: Product) -> Text = "{product.sku}: costs {product.cost}, sells for {product.price}"
+
 pub main() -> Unit
@@ -19,3 +22,3 @@
   for product in catalog
-    @console.print(price_tag(product))
+    @console.print(sheet_line(product))
   let margins = catalog.map(each: margin)
```

:::answer Show the answer
It does not check:

```text include="steps/06-sheet-line/expected/rendered.txt#L1"
[U4001] Error: the result of `sheet_line` is `Text`, and this value is `confidential Text`: a flow from `confidential` to `public`
```

The interpolation reads `product.cost`, so the text is `confidential`, and the header of `sheet_line` declares a plain `Text`. The checker stops at the first checkpoint the value meets, the declared result, before it reaches the console.
:::

Second, print each product whole:

```diff include="steps/03-labels..steps/07-whole-record:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -19,3 +19,3 @@
   for product in catalog
-    @console.print(price_tag(product))
+    @console.print("on the shelf: {product}")
   let margins = catalog.map(each: margin)
```

:::answer Show the answer
It does not check:

```text include="steps/07-whole-record/expected/rendered.txt#L1-L8"
[U4003] Error: `@console.print` accepts `public` data, and this argument is `confidential`
    ╭─[ src/pricing.una:20:20 ]
    │
 20 │     @console.print("on the shelf: {product}")
    │                    ────────────┬────────────
    │                                ╰────────────── `@console.print` accepts `public` data, and this argument is `confidential`
    │
    │ Help 1: repair 1: field `cost` of `Product` is `confidential`: interpolate only the fields that `@console.print` accepts
```

Interpolating the whole product writes every field, `cost` included, so the text is `confidential`. The first repair names the field that makes it so: interpolate only the fields the console accepts, as `price_tag` does.
:::

## 17.2 Sinks: where labeled data may go


### What a sink is

A **sink** is a place where data leaves the program: printed to the console, written to a file, sent to a service. In Una every such exit is an argument of a capability operation ([chapter 12](/learn/capabilities/)), so every argument of an operation is a sink.

Each sink has a **ceiling**: the highest label it accepts. Think of a mail slot marked "internal mail only": anything at or below that label may go through, and anything above it is turned away at the slot. The checker proves, at every call of an operation, that every argument is at or below the operation's ceiling.

### Why a sink needs a ceiling

The store's supplier needs the reorder list, which the program reads from a file. Here is a program that sends it. The supplier's service is a capability declared as in [chapter 12](/learn/capabilities/#s12-3), with nothing about labels:

```una include="steps/09-no-accepts/src/reorder.una" title="steps/09-no-accepts/src/reorder.una"
module reorder

--- The supplier's ordering service, declared as in chapter 12.
capability Supplier
  op submit(order: Text) -> Unit

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

`main` writes the list to a file, reads it back into `list`, and hands it to `send_list`, which submits it to the supplier. The parameter of `send_list` says `internal Text`: data read from a file is `internal`, as the next subsections explain. `una check .` refuses the call in `send_list`:

```text include="steps/09-no-accepts/expected/rendered.txt#L1-L8"
[U4003] Error: `@supplier.submit` accepts `public` data, and this argument is `internal`
    ╭─[ src/reorder.una:11:20 ]
    │
 11 │   @supplier.submit(list)
    │                    ──┬─
    │                      ╰─── `@supplier.submit` accepts `public` data, and this argument is `internal`
    │
    │ Help 1: repair 1: send `@supplier.submit` only data labeled `public` or lower, or send this value to an operation that accepts `internal`
```

The list is `internal`, since it came from a file ([Data from outside is `internal`](#data-from-outside-is-internal)). An operation with no ceiling of its own accepts only `public` data. So the checker refuses to send the list, even though the supplier is exactly where it should go. What is missing is a way to say that this service may receive the store's internal data. That is the `accepts` clause. The first repair una lists says the same: send this value to an operation that accepts `internal`.

### The ceilings of the host's operations

The operations the host provides ([chapter 12](/learn/capabilities/#s12-2)) have fixed ceilings:

| Operation | Accepts | Gives back |
| --- | --- | --- |
| `Console.print(line)` | `public` | nothing |
| `Clock.now()` | `public` | a public `Int` |
| `Env.get(name)` | `public` | an `Option[internal Text]` |
| `Files.read(path)` | `public` | an `internal Text` |
| `Files.write(path, content)` | `internal` | nothing |
| `Http.get`, `post`, `put` and `delete` ([chapter 12](/learn/capabilities/#s12-2)) | `internal`, for every argument | a `Response`, the web service's answer, labeled `internal` |
| `Keys.hmac(key_name, data)` | `public` for the key name, any label for the data | a `Hashed`, labeled `internal` and the label of the data ([A keyed hash](#a-keyed-hash-keyshmac-and-hashed)) |

So a program may print only public data, and may write to a file, or send to a web service, what it read from one, but no more than `internal`.

### Data from outside is `internal`

Data read from files, the environment or the network is labeled `internal`. `Files.read` returns `internal Text`, `Env.get` returns `internal` values, and an `Http` request, a message to a web service, returns a `Response`, the web service's answer, labeled `internal`: a file, an environment variable or a web service may hold anything, so the program may pass what it read to the store's own systems, but may not print it. A count of what was read, such as its length, carries the same label, as [Check yourself: sinks and keyed hashes](#check-yourself-sinks-and-keyed-hashes) shows.

### How to write `accepts`

An operation of your own states its ceiling with an `accepts` clause, the word `accepts` and a label, on its own line under the operation. The clause belongs only to an `op` of a `capability`: a function has no ceiling of its own, since what it may send is bounded by the operations it calls.

```una include="steps/08-sinks/src/reorder.una#Supplier" title="steps/08-sinks/src/reorder.una"
--- The supplier's ordering service. It may receive the store's internal data, and no more.
capability Supplier
  op submit(order: Text) -> Unit
    accepts internal
```

- **The label** is any label: a level, such as `accepts internal`, or a level with categories, such as `accepts secret[PII]` ([section 17.4](#s17-4)).
- **Without the clause,** the operation accepts `public`.
- **One clause per operation.** An operation has at most one `accepts` clause, and it applies to every argument of the operation.
- **Its place.** The clauses of an operation come in a fixed order: every `requires`, then every `ensures`, then `fails`, then `accepts`. The `Mailer` of [section 17.6](#s17-6) has a `fails` clause and then its `accepts`.

### Sending a reorder list to the supplier

This step passes a reorder list from a file to the supplier, whose service accepts `internal` data:

:::steps
```una include="steps/08-sinks/src/reorder.una" title="steps/08-sinks/src/reorder.una" verified="check, run"
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

```text include="steps/08-sinks/expected/output.txt"
reorder list sent to the supplier
```

### How a sink is checked

#### Every argument, on its own

The checker compares each argument with the ceiling, one at a time. A call with two arguments above the ceiling gets two diagnostics, one for each. An argument at or below the ceiling checks: `public` data may go anywhere.

#### Every label inside an argument

An argument's label includes the labels inside it. A `List[confidential Int]` sent to the console is refused, although the list itself is public, since printing it would print its elements. That is the leak of [Printing a confidential value](#printing-a-confidential-value).

#### A handler is checked for its most sensitive caller

A handler of an operation ([chapter 12](/learn/capabilities/#s12-3)) receives what callers send. The checker does not know which caller will run it, so it checks the handler for the most sensitive caller the `accepts` clause allows. Here the fake supplier prints a fixed line each time it is called:

```diff include="steps/08-sinks..steps/10-printing-handler:src/reorder.una" context="1" title="src/reorder.una"
--- a/src/reorder.una
+++ b/src/reorder.una
@@ -13,5 +13,6 @@
 
---- A supplier that accepts every order, for this run.
+--- A supplier that accepts every order, and says so on the console.
 handler accepting() for Supplier
-  op submit(order) = unit
+  uses @console: Console[print]
+  op submit(order) = @console.print("order received")
 
```

```text include="steps/10-printing-handler/expected/rendered.txt#L1-L6"
[U4003] Error: `@console.print` accepts `public` data, and it runs in an operation body whose callers may pass `internal` data, which it would reveal
    ╭─[ src/reorder.una:17:22 ]
    │
 17 │   op submit(order) = @console.print("order received")
    │                      ────────────────┬───────────────
    │                                      ╰───────────────── `@console.print` accepts `public` data, and it runs in an operation body whose callers may pass `internal` data, which it would reveal
```

The printed line is a literal, and it is still refused. The message gives the reason: the operation body may receive `internal` data, which the print *would reveal*. Whether the line appears is itself a signal, and a handler could print it only for some orders. So a handler of an operation that accepts `internal` data may not print at all. A fake that does nothing, fails, or returns fixed values stays valid.

#### Examples are not sinks

> [!NOTE]
> `expect` lines of examples are not sinks. An example may compare a `secret` result with a value, and in a package of edition `0.2`, `una test .` prints it in full when the example fails, since a test is the author looking at their own data. (Edition `0.1` hides the labeled fields of a result as `<redacted:level>`, [chapter 19](/learn/editions/).) The `do` line is checked like any other code: an example can observe a secret, but cannot send it anywhere the program itself could not.

### Raising a ceiling, or sending less

:::decide
**Which to use:**

| The data… | Do this |
| --- | --- |
| Must reach the service as it is, such as an address for the mail service | give the operation an `accepts` clause with the data's label |
| Is more than the service needs, such as a whole record when it needs an id | send only the fields it needs, which may be public |
| Must reach a public place in part, such as a masked address in a log | release that part through a policy ([section 17.5](#s17-5)) |
:::

Raise a ceiling only to the label the real service may receive. An `accepts` clause is a statement about the service, which a reviewer reads, not a way to make a diagnostic go away.

### A keyed hash: `Keys.hmac` and `Hashed`

#### What a keyed hash is

A fingerprint card tells you whether two cards come from the same person, and it does not tell you the person's name or address. A **hash** is that card for a piece of data: a short value computed from a text, such that the same text always gives the same hash, and the hash does not give the text back. A **keyed hash** also mixes in a secret key that the host keeps outside the program, so that someone who has a copy of the hashes, and no key, cannot hash a guess and compare. The standard way to compute one is called HMAC, short for *hash-based message authentication code*.

In Una the host's `Keys` capability computes keyed hashes, with its operation `hmac`, and the result has the built-in type `Hashed`. A `Hashed` is opaque: the program can compare two of them, and can do nothing else with them.

#### Why a program hashes data

The store keeps a do-not-mail list: the customers who asked for no marketing. A list of their addresses would itself be personal data, and anyone who saw a copy would learn who is on it. A list of keyed hashes holds no address. To check a customer, the program hashes the customer's address with the same key and looks for that hash in the list. A match says the address is on the list, and the list never says whose addresses it holds.

#### How to write a keyed hash

A function that hashes declares the capability, as any function that uses the host does ([chapter 12](/learn/capabilities/#s12-2)): `uses @keys: Keys[hmac]`. Then:

- **The call** is `@keys.hmac(key_name: "optout", data: address)`. `key_name` names a key the host holds, and `data` is the text to hash.
- **The failure.** `hmac` fails with `KeyError`, whose one variant, `UnknownKey`, means the host has no key of that name. The call needs a handling clause, as every call that may fail does ([chapter 7](/learn/failure/#s7-3)).
- **The type** of the result is `Hashed`, with a label: `internal`, joined with the label of `data`.

Here is the check of the do-not-mail list:

```una include="steps/11-hashed/src/optout.una#opted_out" title="steps/11-hashed/src/optout.una"
--- Whether an address is on the do-not-mail list. The list keeps no addresses, only their
--- keyed hashes, made with the key `optout`, so a copy of the list reveals no one.
opted_out(address: secret Text, list: List[internal Hashed]) -> secret Bool
  uses @keys: Keys[hmac]
  fails KeyError
=
  let hashed = @keys.hmac(key_name: "optout", data: address)
    if error pass
  list.filter(keep: fn(entry) -> entry == hashed).len > 0
```

1. **`address: secret Text`.** An address is about a person, so it is `secret`.
2. **`if error pass`.** If the host has no key named `optout`, the check fails with `KeyError`, and the caller decides what to do.
3. **`hashed`** is a `secret Hashed`: `internal`, joined with the label of the address.
4. **`entry == hashed`** compares two hashes. It reads `hashed`, so it is a `secret Bool`, and so is the answer: whether a customer is on the list is something about the customer.

#### How a hash behaves

**It keeps the label of what it hashed.** Hashing does not lower a label. The hash of a `secret` address is `secret`, and a public answer computed from it is U4001, as [Check yourself: sinks and keyed hashes](#check-yourself-sinks-and-keyed-hashes) shows. To send a hash where its label may not go, release it through a policy ([section 17.5](#s17-5)).

**Only `==` and `!=`.** A `Hashed` cannot be interpolated, so its bytes never reach a text. Add `let shown: secret Text = "hash {hashed}"` to `opted_out`:

```text include="steps/12-hash-text/expected/rendered.txt#L1"
[U2001] Error: interpolation writes values that hold no function and no `Hashed`, and this value is a `Hashed`
```

**The key name is public.** `hmac` accepts `public` data for `key_name` and any label for `data`, since whether the call fails with `UnknownKey` depends on the key name alone. Hash with `key_name: address`:

```text include="steps/13-hash-key-name/expected/rendered.txt#L1"
[U4003] Error: `@keys.hmac` accepts `public` data, and this argument is `secret`
```

#### Testing it with a stand-in

To run `hmac`, `una run` needs the grant `keys:<file>`, which names the file of keys the host reads. The steps of this book run with no keys, so `main` here prints only a line, and examples check `opted_out` with a stand-in for the host:

```una include="steps/11-hashed/src/optout.una#L15-L28" title="steps/11-hashed/src/optout.una" caption="the stand-in and the examples"
--- A stand-in for the key service, for the examples: one address hashes to the seed 1, and
--- every other address to the seed 2.
handler fake_keys() for Keys
  op hmac(key_name, data) = if data == "rita@example.invalid" then fake_hash(1) else fake_hash(2)

example "an address on the list is found"
  given @keys = fake_keys()
  do opted_out("rita@example.invalid", list: [fake_hash(1)])
  expect result == true

example "an address that is not on the list is not found"
  given @keys = fake_keys()
  do opted_out("tom@example.invalid", list: [fake_hash(1)])
  expect result == false
```

- **`fake_keys`** is a handler of `Keys`, a host capability, written as a fake of a host capability is in [chapter 14](/learn/testing/#a-fake-of-a-host-capability). It makes hashes with `fake_hash(seed)`, from the standard module `std.testing`, which the file imports with `import std.testing (fake_hash)`. The **seed** is a number that picks which fake hash you get: the same seed always gives the same hash, so `fake_hash(1)` stands for the hash of the listed address.
- **`given @keys = fake_keys()`** installs the handler for one example only. [Section 14.3](/learn/testing/#s14-3) teaches `given` and fakes in full.

**Only in examples.** A function of `std.testing` may be called only in example lines and in handlers that only `given` installs, so fake hashes never reach a real run. Install `fake_keys` in `main`, with `with` and the clause that handles a `KeyError`:

```una include="steps/14-hash-fake-in-main/src/optout.una#main" title="steps/14-hash-fake-in-main/src/optout.una"
pub main() -> Unit
  uses @console: Console[print]
=
  let found = opted_out("rita@example.invalid", list: []) with @keys = fake_keys()
    if error use false
  @console.print("checked")
```

`una check .` refuses the binding:

```text include="steps/14-hash-fake-in-main/expected/rendered.txt#L1"
[U3015] Error: this `with` binding installs a handler that uses `std.testing`, which only `given` lines of examples may install
```

`una test .` prints:

```text include="steps/11-hashed/expected/commands/test.txt#L2-L5"
example optout "an address on the list is found" ... ok
example optout "an address that is not on the list is not found" ... ok

2 examples: 2 passed, 0 failed
```

Use a keyed hash to recognize or match a value without keeping it, such as a do-not-mail list or a list of addresses already seen. Do not hash a value you need back: nothing turns a `Hashed` into the text it came from.

### Check yourself: sinks and keyed hashes

The reorder program prints how many characters it sent, instead of a fixed message:

```diff include="steps/08-sinks..steps/15-length:src/reorder.una" context="1" title="src/reorder.una"
--- a/src/reorder.una
+++ b/src/reorder.una
@@ -26,2 +26,2 @@
   send_list(list) with @supplier = accepting()
-  @console.print("reorder list sent to the supplier")
+  @console.print("{list.len} characters sent to the supplier")
```

Does `una check .` pass?

:::answer Show the answer
No:

```text include="steps/15-length/expected/rendered.txt#L1"
[U4003] Error: `@console.print` accepts `public` data, and this argument is `internal`
```

`list` is `internal Text`, a whole that is labeled. `.len` has the label of the whole it measures, so the length is `internal` too, and the console accepts only `public`. Compare `margins.len` in [A catalog with a confidential cost](#a-catalog-with-a-confidential-cost): there the list was public and only its elements were labeled.
:::

Second, someone declares the answer of `opted_out` public, reasoning that a hash reveals nothing:

```diff include="steps/11-hashed..steps/16-hashed-public:src/optout.una" context="1" title="src/optout.una"
--- a/src/optout.una
+++ b/src/optout.una
@@ -6,3 +6,3 @@
 --- keyed hashes, made with the key `optout`, so a copy of the list reveals no one.
-opted_out(address: secret Text, list: List[internal Hashed]) -> secret Bool
+opted_out(address: secret Text, list: List[internal Hashed]) -> Bool
   uses @keys: Keys[hmac]
```

Does `una check .` pass?

:::answer Show the answer
No:

```text include="steps/16-hashed-public/expected/rendered.txt#L1"
[U4001] Error: the result of `opted_out` is `Bool`, and this value is `secret Bool`: a flow from `secret` to `public`
```

The hash carries the label of the address it was made from, so `entry == hashed` is a `secret Bool`, and the declared result is a public `Bool`. A hash hides the text, but whether a customer is on the list is still a fact about that customer. Keep the answer `secret`, or release it through a policy if a public place must have it.
:::

## 17.3 Branches and failures: implicit flows


### What an implicit flow is

Ask a colleague whether a customer spent more than 500.00 this year, and agree that they will answer by raising a hand for yes. They never say the amount, yet you learn something about it. The answer is in which way they acted.

A program can leak the same way. A value **flows explicitly** when it is copied or computed into another, as the cost flows into the margin. It **flows implicitly** when it decides which way the program goes: a branch on the cost that returns `0` or `790` reveals something about the cost, although `0` and `790` are constants.

The checker tracks implicit flows with the label of the **program counter**: the label of what decided that the program is where it is now. (The name comes from the processor, whose program counter holds the place in the program that runs next. Here it names the label of that place.) At the start of a function it is `public`. Inside a branch on labeled data, it rises to the condition's label, and everything the branch decides carries that label. After the branch, it is back to what it was.

### Why constants can leak

Give a loyalty card a badge, decided by what the customer spent, and declare the badge public:

```una include="steps/18-badge/src/loyalty.una#badge" title="steps/18-badge/src/loyalty.una"
--- `if … then … else` on a labeled condition: the badge printed on a loyalty card.
badge(spent: confidential Int) -> Text = if spent >= 50000 then "gold" else "standard"
```

`una check .` reports:

```text include="steps/18-badge/expected/rendered.txt#L1-L6"
[U4001] Error: the result of `badge` is `public`, and which value it returns depends on this `confidential` condition: a flow from `confidential` to `public`
   ╭─[ src/loyalty.una:7:45 ]
   │
 7 │ badge(spent: confidential Int) -> Text = if spent >= 50000 then "gold" else "standard"
   │                                             ───────┬──────
   │                                                    ╰──────── the result of `badge` is `public`, and which value it returns depends on this `confidential` condition: a flow from `confidential` to `public`
```

`"gold"` and `"standard"` are literals, so each is public. But a reader who sees the badge learns whether `spent` is at least 50000. The diagnostic says so, and points at the condition, `spent >= 50000`, since that is where the information enters. Without this rule, a program could copy a secret one bit at a time through branches, and no single value in it would carry a label.

### How the program counter rises

Every construct that chooses a way by a value raises the program counter by that value's label: the branches, and loops, which choose how many times their body runs. The next step shows each one, with a confidential amount, and declares each result `confidential`:

#### `if … then … else`

```una include="steps/17-pc-forms/src/loyalty.una#badge" title="steps/17-pc-forms/src/loyalty.una"
--- `if … then … else` on a labeled condition: the badge printed on a loyalty card.
badge(spent: confidential Int) -> confidential Text = if spent >= 50000 then "gold" else "standard"
```

#### An `if` block

```una include="steps/17-pc-forms/src/loyalty.una#points" title="steps/17-pc-forms/src/loyalty.una"
--- An `if` block on a labeled condition: the points a purchase of `cents` earns.
points(spent: confidential Int, cents: Int) -> confidential Int
=
  if spent >= 50000
    let doubled = cents / 50
    doubled
  else
    cents / 100
```

Both branches of the block run under the condition's label: `doubled`, computed from the public `cents`, is confidential inside the branch, and so is `cents / 100`.

#### `when` on a labeled value

A `when` ([chapter 8](/learn/choices/#s8-2)) chooses an arm by the variant of a value. On a labeled value, which arm runs reveals the variant:

```una include="steps/17-pc-forms/src/loyalty.una#discount" title="steps/17-pc-forms/src/loyalty.una"
--- A `when` on a labeled value: the discount of a tier, in percent.
discount(tier: confidential Tier) -> confidential Int
=
  when tier
    is Gold -> 10
    is Silver -> 5
    is Standard -> 0
```

#### `if none use` on a labeled `Option`

Whether an `Option` ([chapter 7](/learn/failure/#s7-1)) is `None` is information too, so the value chosen by `if none use` carries the option's label:

```una include="steps/17-pc-forms/src/loyalty.una#spending" title="steps/17-pc-forms/src/loyalty.una"
--- `if none use` on a labeled `Option`: what a customer spent, or 0 for a new customer.
spending(found: confidential Option[Int]) -> confidential Int
=
  let spent = found
    if none use 0
  spent
```

#### A `for` loop over a labeled list or range

A `for` loop ([chapter 9](/learn/loops/#s9-1)) decides something too: how many times its body runs. A loop over a list runs once per element, so the number of turns reveals the list's length, which has the label of the whole list ([Length, and the label of a whole](#length-and-the-label-of-a-whole)). A loop over a range reveals its bounds. So the body runs under the label of the whole list, or of the bounds:

```una include="steps/17-pc-forms/src/loyalty.una#total_spent..stamps" title="steps/17-pc-forms/src/loyalty.una"
--- A `for` loop over a labeled list: what a customer spent over several purchases.
total_spent(purchases: confidential List[Int]) -> confidential Int
=
  let edit total: confidential Int = 0
  for cents in purchases
    total = total + cents
  total

--- A `for` loop over a labeled range: the stamps on a card, 10 for each visit.
stamps(visits: confidential Int) -> confidential Int
=
  let edit earned: confidential Int = 0
  for visit in 1..visits
    earned = earned + 10
  earned
```

`total` and `earned` are editable names, accumulators that each turn updates ([chapter 9](/learn/loops/#s9-2)). An editable name keeps the label it was declared with, so each one is declared with the label the loop gives it: `let edit total: confidential Int = 0`. Without that label, `total` would be a public `Int`, and the update inside the loop would be U4001.

A loop over a list whose elements alone are labeled, such as the catalog of [step 03](#a-catalog-with-a-confidential-cost), a `List[Product]` with a confidential field, runs at the program counter it had: how many products there are is public. Each element still carries its own labels. The prelude's `map`, `filter` and `fold` follow the same rule as a loop: the function they call once per element runs under the label of the whole list.

An operation in the body is under the loop's label too. Print a line for each purchase:

```diff include="steps/17-pc-forms..steps/38-loop-print:src/loyalty.una" context="1" title="src/loyalty.una"
--- a/src/loyalty.una
+++ b/src/loyalty.una
@@ -48,2 +48,9 @@
 
+--- Prints a line for each purchase on the receipt.
+print_purchases(purchases: confidential List[Int]) -> Unit
+  uses @console: Console[print]
+=
+  for cents in purchases
+    @console.print("one more purchase")
+
 pub main() -> Unit
```

```text include="steps/38-loop-print/expected/rendered.txt#L1-L9"
[U4003] Error: `@console.print` accepts `public` data, and it runs under a `confidential` condition, which it would reveal
    ╭─[ src/loyalty.una:54:5 ]
    │
 53 │   for cents in purchases
    │                ────┬────
    │                    ╰────── the labeled condition
 54 │     @console.print("one more purchase")
    │     ─────────────────┬─────────────────
    │                      ╰─────────────────── `@console.print` accepts `public` data, and it runs under a `confidential` condition, which it would reveal
```

The mark "the labeled condition" points at `purchases`, after `in`: the list decides how many times the body runs, so it plays the part of an `if`'s condition. The printed text is a literal, and the number of lines printed would still reveal how many purchases there are. To show the count, release it through a policy ([section 17.5](#s17-5)) and print it after the loop, or send each line to a place that accepts `confidential` data.

#### Running the branch forms

The examples look at each labeled result:

```una include="steps/17-pc-forms/src/loyalty.una#L54-L76" title="steps/17-pc-forms/src/loyalty.una" caption="the examples"
example "a customer who spent 720.00 gets the gold badge"
  do badge(72000)
  expect result == "gold"

example "a gold customer earns double points"
  do points(72000, cents: 5000)
  expect result == 100

example "a silver customer gets 5 percent off"
  do discount(Silver)
  expect result == 5

example "a new customer has spent nothing"
  do spending(None)
  expect result == 0

example "three purchases add up"
  do total_spent([2100, 4990, 12600])
  expect result == 19690

example "a customer with 3 visits has 30 stamps"
  do stamps(3)
  expect result == 30
```

```text include="steps/17-pc-forms/expected/commands/test.txt#L2-L9"
example loyalty "a customer who spent 720.00 gets the gold badge" ... ok
example loyalty "a gold customer earns double points" ... ok
example loyalty "a silver customer gets 5 percent off" ... ok
example loyalty "a new customer has spent nothing" ... ok
example loyalty "three purchases add up" ... ok
example loyalty "a customer with 3 visits has 30 stamps" ... ok

6 examples: 6 passed, 0 failed
```

### A fee decided by a branch

This step charges a shipping fee. Loyal customers, those who spent at least 50000 cents, ship for free, and what a customer spent is confidential:

:::steps
```una include="steps/19-branches/src/shipping.una" title="steps/19-branches/src/shipping.una" verified="check, run"
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

```text include="steps/19-branches/expected/output.txt"
shipping charged for 2 orders
```

### What may happen under a labeled branch

A branch on labeled data may compute values, and those values carry the label. It may not do anything a public observer would notice: fail, or act on the world below the label.

#### A failure is a flow too

Whether a function fails is something its caller observes ([chapter 7](/learn/failure/)). A `fail` inside a branch on labeled data would reveal the condition to every caller, through the failure. So `fail`, and handling clauses that fail or pass a failure on, are allowed only where the program counter is `public`. Add a free-shipping code that fails for customers who did not spend enough:

```diff include="steps/19-branches..steps/20-fail:src/shipping.una" context="1" title="src/shipping.una"
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

```text include="steps/20-fail/expected/rendered.txt#L1-L10"
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

The diagnostic has two marks. The first, "the labeled condition", is the branch that raised the program counter. The second is the `fail` it decides. The repair is in the message: return a labeled value instead of failing.

#### Return a labeled answer instead

Here is the repair. The code is an `Option`: `Some` with the code for a loyal customer, `None` for anyone else, and the whole answer is confidential:

```una include="steps/21-labeled-answer/src/shipping.una#free_shipping_code" title="steps/21-labeled-answer/src/shipping.una" verified="check, run, test"
--- The free-shipping code of a loyal customer, or `None`. The answer carries the label of
--- what decided it, so the caller learns it only where `confidential` data may go.
free_shipping_code(spent: confidential Int) -> confidential Option[Text] = if spent < 50000 then None else Some("FREESHIP")
```

```text include="steps/21-labeled-answer/expected/commands/test.txt#L2-L5"
example shipping "a loyal customer has a code" ... ok
example shipping "another customer has none" ... ok

2 examples: 2 passed, 0 failed
```

The caller receives the answer with its label, and decides what to do with it under the same rules. It may send it to a place that accepts `confidential` data, such as the payment provider, and may not branch on it to fail.

#### An effect under a labeled branch

An operation performed inside the branch is seen by its sink, so the sink must accept the condition's label. Thank loyal customers on the console:

```diff include="steps/19-branches..steps/22-effect-under-branch:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -17,2 +17,9 @@
 
+--- Greets a loyal customer at the checkout.
+greet(spent: confidential Int) -> Unit
+  uses @console: Console[print]
+=
+  if spent >= 50000
+    @console.print("thank you for shopping with us again")
+
 --- A payment provider that accepts every charge, for this run.
```

```text include="steps/22-effect-under-branch/expected/rendered.txt#L1-L9"
[U4003] Error: `@console.print` accepts `public` data, and it runs under a `confidential` condition, which it would reveal
    ╭─[ src/shipping.una:23:5 ]
    │
 22 │   if spent >= 50000
    │      ───────┬──────
    │             ╰──────── the labeled condition
 23 │     @console.print("thank you for shopping with us again")
    │     ───────────────────────────┬──────────────────────────
    │                                ╰──────────────────────────── `@console.print` accepts `public` data, and it runs under a `confidential` condition, which it would reveal
```

The printed text is a literal, but whether it is printed reveals the branch. The message names both: the console accepts `public`, *and it runs under a `confidential` condition*. The payment provider of this step accepts `confidential`, so `@payments.charge` would be allowed in the same branch.

#### A call under a labeled branch

The same rule covers calls of your own functions. Under a labeled program counter, a function may call another only if the callee cannot fail, and every operation it may perform accepts that label. A pure function, one with no `uses` that does nothing but compute its result, such as `shipping_fee`, may be called anywhere if it cannot fail. Move the print of the last step into a function of its own, `thank`, and call it from the branch:

```diff include="steps/19-branches..steps/23-call-under-branch:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -21,2 +21,15 @@
 
+--- Thanks a customer on the console.
+thank() -> Unit
+  uses @console: Console[print]
+=
+  @console.print("thank you for shopping with us again")
+
+--- Greets a loyal customer at the checkout, through `thank`.
+greet(spent: confidential Int) -> Unit
+  uses @console: Console[print]
+=
+  if spent >= 50000
+    thank()
+
 pub main() -> Unit
```

```text include="steps/23-call-under-branch/expected/rendered.txt#L1-L9"
[U4002] Error: `thank` has effects that accept at most `public` data, and it is called under a `confidential` condition, which would be revealed
    ╭─[ src/shipping.una:33:5 ]
    │
 32 │   if spent >= 50000
    │      ───────┬──────
    │             ╰──────── the labeled condition
 33 │     thank()
    │     ───┬───
    │        ╰───── `thank` has effects that accept at most `public` data, and it is called under a `confidential` condition, which would be revealed
```

The print is now one call away, and the checker still finds it: `thank` holds the console, which accepts only `public` data, so calling it under a `confidential` condition is U4002. The code is U4002 rather than U4003 because the diagnostic is about the call of your function, not about an operation in this branch. A function with a `fails` clause is refused in the same place, for the reason of [A failure is a flow too](#a-failure-is-a-flow-too).

#### After the branch

The program counter rises only inside the branch. The lines after the `if`, the `when` or the `for` run at the label they had before it, so a function may branch on a secret, produce a labeled value, and then fail or print on public data in its next lines.

### Where to put a decision

:::decide
**Which to use:**

| You need to… | Do this |
| --- | --- |
| Compute a value that depends on labeled data | branch, and label the result |
| Repeat work over a labeled list or up to a labeled bound | loop, label the accumulators, and act only on services that accept the label |
| Report "no answer" for some labeled inputs | return a labeled `Option` or a labeled variant, not a failure |
| Fail, or print, or call a service, depending on labeled data | release the one fact the decision needs through a policy ([section 17.5](#s17-5)), then branch on the public result |
| Act on a service that accepts the label | do it in the branch: its `accepts` covers the condition |
:::

### Check yourself: branches

A bulky item costs 15.00 to ship for every customer. Someone writes it with the same shape as `shipping_fee`, and declares it public:

```diff include="steps/19-branches..steps/24-flat-fee:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -10,2 +10,5 @@
 shipping_fee(spent: confidential Int) -> confidential Int = if spent >= 50000 then 0 else 790
+
+--- The fee for a bulky item, which every customer pays.
+bulky_fee(spent: confidential Int) -> Int = if spent >= 50000 then 1500 else 1500
 
```

Both branches give 1500. Does `una check .` pass?

:::answer Show the answer
No:

```text include="steps/24-flat-fee/expected/rendered.txt#L1"
[U4001] Error: the result of `bulky_fee` is `public`, and which value it returns depends on this `confidential` condition: a flow from `confidential` to `public`
```

The checker does not compare the branches' values: it sees a result chosen by a confidential condition, and labels it so. Here the branch is useless, and the repair is to remove it: `bulky_fee() -> Int = 1500`. A rule that never looks at the values is one you can predict from the code's shape alone.
:::

## 17.4 Categories


### What a category is

A level says how sensitive data is. A **category** says what kind of data it is: personal data, a location, a payment card number. Think of a colored sticker next to the "confidential" stamp: two folders can be equally sensitive and still belong in different cabinets.

You write categories in square brackets after the level: `secret[PII] Text` is secret, and it is personal data (PII stands for *personally identifiable information*). Each package declares its own categories by name.

### Why a level is not enough

A courier needs a customer's phone number, so that the driver can call at the door. The analytics service records bookings, and it may receive secret data, such as the store's sales figures. Here is a route booking with a level and no category:

```una include="steps/25-no-category/src/courier.una" title="steps/25-no-category/src/courier.una" verified="check, run"
module courier

--- A stop on a delivery route. The phone number is secret, and nothing says it is personal.
kind Stop
  order: Text
  city: Text
  phone: secret Text

--- The courier's booking service. It may receive secret data.
capability Courier
  op book(order: Text, phone: Text) -> Unit
    accepts secret

--- The store's analytics service. It may receive secret data too: sales figures, for one.
capability Analytics
  op record(event: Text) -> Unit
    accepts secret

--- Books every stop of a route, and records each booking for the analysts.
book_route(stops: List[Stop]) -> Unit
  uses @courier: Courier[book]
  uses @analytics: Analytics[record]
=
  for stop in stops
    @courier.book(stop.order, phone: stop.phone)
    @analytics.record("booked {stop.order} in {stop.city} for {stop.phone}")

--- A courier that accepts every booking, for this run.
handler accepting() for Courier
  op book(order, phone) = unit

--- An analytics service that stores nothing, for this run.
handler discarding() for Analytics
  op record(event) = unit

pub main() -> Unit
  uses @console: Console[print]
=
  let route = [Stop(order: "A-1001", city: "Recife", phone: "+55 81 5550 0101"), Stop(order: "A-1002", city: "Olinda", phone: "+55 81 5550 0102")]
  book_route(route) with @courier = accepting(), @analytics = discarding()
  @console.print("route booked and recorded")
```

`una run .` prints:

```text include="steps/25-no-category/expected/output.txt"
route booked and recorded
```

It checks, and every customer's phone number now sits in the analytics records. Both services accept `secret`, and the phone is `secret`, so nothing tells them apart. A higher level for the phone would not help either: the courier must still receive it. What the program needs to say is that the courier may receive *personal* data and the analytics service may not.

### How to write categories

#### Declaring them in `una.toml`

A package declares its categories in `una.toml`, under the table `[labels]`, as a list of names:

```toml include="steps/26-categories/una.toml" title="steps/26-categories/una.toml"
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

A category's name is written in UpperCamelCase: it starts with a capital letter, and each word in it does too, such as `PII` or `Location`. Any other name, such as `pii`, is U1005.

#### On a type

The categories go in square brackets right after the level, before the type: `secret[PII] Text`. Several categories are separated by commas: `confidential[Location, PII] Text`.

#### In an `accepts` clause

A ceiling can name categories too: `accepts secret[PII]` accepts secret data that is personal, and anything below it.

### A courier that may receive a phone number

The step books a courier, whose service may receive personal data:

:::steps
```una include="steps/26-categories/src/courier.una" title="steps/26-categories/src/courier.una" verified="check, run"
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

```text include="steps/26-categories/expected/output.txt"
route booked: Recife, Olinda
```

The analytics service of [Why a level is not enough](#why-a-level-is-not-enough), with `accepts secret`, would now refuse the phone. Personal data reaches only the places that say they may receive it.

### How categories flow and combine

#### A label flows only into one with the same categories, or more

A label flows into another only if its level is at or below the other's, *and* its categories are among the other's. So `secret[PII]` flows into `secret[PII]` and `restricted[PII]`, but not into `secret`. Give the courier `accepts secret`:

```diff include="steps/26-categories..steps/27-no-category-ceiling:src/courier.una" context="1" title="src/courier.una"
--- a/src/courier.una
+++ b/src/courier.una
@@ -12,3 +12,3 @@
   op book(order: Text, phone: Text) -> Unit
-    accepts secret[PII]
+    accepts secret
 
```

```text include="steps/27-no-category-ceiling/expected/rendered.txt#L1"
[U4003] Error: `@courier.book` accepts `secret` data, and this argument is `secret[PII]`
```

The levels match, and the category does not. Personal data never loses its category by accident.

#### Combining values joins categories

When values combine, the result takes the higher level and every category of either. Declare a second category, `Location`, for the door of each stop, and send the courier the phone and the door in one text:

```diff include="steps/26-categories..steps/28-two-categories:src/courier.una" context="1" title="src/courier.una"
--- a/src/courier.una
+++ b/src/courier.una
@@ -2,3 +2,3 @@
 
---- A stop on a delivery route. The phone number is personal data.
+--- A stop on a delivery route. The phone number is personal data, and the door is a location.
 kind Stop
@@ -7,2 +7,3 @@
   phone: secret[PII] Text
+  door: confidential[Location] Text
 
@@ -19,3 +20,3 @@
   for stop in stops
-    @courier.book(stop.order, phone: stop.phone)
+    @courier.book(stop.order, phone: "{stop.phone}, {stop.door}")
 
@@ -31,3 +32,3 @@
 =
-  let route = [Stop(order: "A-1001", city: "Recife", phone: "+55 81 5550 0101"), Stop(order: "A-1002", city: "Olinda", phone: "+55 81 5550 0102")]
+  let route = [Stop(order: "A-1001", city: "Recife", phone: "+55 81 5550 0101", door: "Rua do Sol 10"), Stop(order: "A-1002", city: "Olinda", phone: "+55 81 5550 0102", door: "Rua da Aurora 5")]
   book_route(route) with @courier = accepting()
```

```text include="steps/28-two-categories/expected/rendered.txt#L1-L6"
[U4003] Error: `@courier.book` accepts `secret[PII]` data, and this argument is `secret[Location, PII]`
    ╭─[ src/courier.una:21:38 ]
    │
 21 │     @courier.book(stop.order, phone: "{stop.phone}, {stop.door}")
    │                                      ─────────────┬─────────────
    │                                                   ╰─────────────── `@courier.book` accepts `secret[PII]` data, and this argument is `secret[Location, PII]`
```

The text joins `secret[PII]` and `confidential[Location]` into `secret[Location, PII]`: the higher level, and both categories. The courier accepts personal data, not locations, so the combined text is refused. To send both, the courier's ceiling would name both: `accepts secret[Location, PII]`.

#### A category must be declared

A category that `[labels] categories` does not declare is U4007. A misspelled category cannot create a new, unchecked kind of data:

```diff include="steps/26-categories..steps/29-misspelled:src/courier.una" context="1" title="src/courier.una"
--- a/src/courier.una
+++ b/src/courier.una
@@ -6,3 +6,3 @@
   city: Text
-  phone: secret[PII] Text
+  phone: secret[PIl] Text
 
```

```text include="steps/29-misspelled/expected/rendered.txt#L1-L6"
[U4007] Error: label category `PIl` is not declared in `[labels] categories` of `una.toml`
   ╭─[ src/courier.una:7:17 ]
   │
 7 │   phone: secret[PIl] Text
   │                 ─┬─
   │                  ╰─── label category `PIl` is not declared in `[labels] categories` of `una.toml`
```

The help line offers the declared name that is closest, and `una fix .` applies it.

#### Dropping a category takes a policy

Dropping a category is a release, like lowering a level: only a policy can do it ([section 17.5](#s17-5)), and its `to` type shows the label it gives.

### Choosing categories

:::decide
**Which to use:**

| You want to… | Do this |
| --- | --- |
| Keep one kind of data, such as personal data, away from services that may receive other secrets | declare a category, such as `PII`, and put it on the data and on the ceilings that may receive it |
| Tell apart two kinds of data that some services receive separately | one category for each, such as `Location` and `PII` |
| Mark data that only differs in how sensitive it is | a level, with no new category |
:::

Declare few categories, each for a kind of data that a law, a contract or a promise to customers treats apart.

### Check yourself: categories

A fraud-screening service accepts the highest level, `restricted`, and no category. Give it the courier's booking:

```diff include="steps/26-categories..steps/30-restricted:src/courier.una" context="1" title="src/courier.una"
--- a/src/courier.una
+++ b/src/courier.una
@@ -12,3 +12,3 @@
   op book(order: Text, phone: Text) -> Unit
-    accepts secret[PII]
+    accepts restricted
 
```

Does the phone, `secret[PII]`, reach it?

:::answer Show the answer
No:

```text include="steps/30-restricted/expected/rendered.txt#L1"
[U4003] Error: `@courier.book` accepts `restricted` data, and this argument is `secret[PII]`
```

`secret` is below `restricted`, so the level fits. But `PII` is not among the ceiling's categories, which are none. A label flows only when both its level and its categories fit.
:::

## 17.5 Releasing data: policies and trusted modules


### What a policy is

Some flows to a lower label are the point of the program. A report must say how many lines a file has. A log should say which customer a notice went to, without the address. Lowering a label on purpose is called **declassifying**, or **releasing**, the data.

In a well-run office, a confidential document leaves the building only through one desk, which redacts it, signs a form that says why, and files a copy. A **policy** is that desk. It is a declaration that names what it accepts, what it gives, the function that computes the released value, why the release is needed and who answers for it. Calling the policy is the only way to lower a label.

### Why a release needs a declared place

The reorder list of [section 17.2](#s17-2) is `internal`. The report wants only how many SKUs it holds. Try to count them into a public `Int`:

```diff include="steps/31-policy..steps/32-unreleased-count:src/reorder.una" context="1" title="src/reorder.una"
--- a/src/reorder.una
+++ b/src/reorder.una
@@ -1,4 +1,2 @@
 module reorder
-
-import release (line_count)
 
@@ -12,2 +10,3 @@
     if error use ""
-  @console.print("{line_count(list)} SKUs to reorder")
+  let count: Int = list.split(on: "\n").filter(keep: fn(line) -> line.len > 0).len
+  @console.print("{count} SKUs to reorder")
```

```text include="steps/32-unreleased-count/expected/rendered.txt#L1-L6"
[U4001] Error: `count` is `Int`, and this value is `internal Int`: a flow from `internal` to `public`
    ╭─[ src/reorder.una:11:20 ]
    │
 11 │   let count: Int = list.split(on: "\n").filter(keep: fn(line) -> line.len > 0).len
    │                    ───────────────────────────────┬───────────────────────────────
    │                                                   ╰───────────────────────────────── `count` is `Int`, and this value is `internal Int`: a flow from `internal` to `public`
```

The count is computed from the list, so it is `internal`, and the annotation says `Int`, which is `public`. The checker is right: a count is something about the list. Here it is also a harmless thing to show, and the program has no way to say so. If any line could lower a label, every label would be only as strong as the least careful line of the program. A policy puts each release in one place, with a reason, where a reviewer can find it.

### How to write a policy

A policy has five lines, all required, and a function that it names:

```una include="steps/31-policy/src/release.una#line_count..count_lines" title="steps/31-policy/src/release.una"
--- Releases how many lines a list has, and nothing of what they say.
pub policy line_count
  from internal Text
  to Int
  via count_lines
  purpose "report the size of the reorder list"
  owner purchasing

count_lines(list: internal Text) -> Int = list.split(on: "\n").filter(keep: fn(line) -> line.len > 0).len
```

| Line | Says |
| --- | --- |
| `pub policy line_count` | The name callers use, like a function's |
| `from internal Text` | What it accepts, with its label |
| `to Int` | What it gives, with the lower label: here `public`, since there is none |
| `via count_lines` | The function that computes the released value |
| `purpose "…"` | Why the release is needed, in words a reviewer reads |
| `owner purchasing` | Who answers for it, such as a team: a name that starts with a small letter and holds only small letters, digits and `_`, as a function's name does |

#### `from` and `to`

`from` and `to` are types with their labels. Apart from the labels, they must match the `via` function's parameter and result exactly. `to` may keep some label, such as `internal`, and may drop categories: a policy from `secret[PII] Text` to `secret Text` drops only the category.

#### `via`

The `via` function takes one parameter, of the type of `from`, and returns the type of `to`. It is a private function of the same module, with no `pub`, so the policy is the only way to call it.

#### `purpose` and `owner`

They are not checked against the code: they are for people. The build report prints them next to every call, so a reviewer reads, in one list, every release the program makes and why.

### Trusted modules

A policy may live only in a **trusted module**: a module whose code the guarantee relies on, and which a reviewer reads with care. A module is trusted only when it says so twice: `trusted module` in its header, and its name under `[trusted] modules` in `una.toml`:

```toml include="steps/31-policy/una.toml" title="steps/31-policy/una.toml"
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

The rest of a trusted module's code is checked as usual. Only the bodies of its `via` functions are not checked for labels ([Inside `via`, labels are not checked](#inside-via-labels-are-not-checked)).

### Releasing a count

The program reads the list, which is `internal`, and prints only what the policy releases:

```una include="steps/31-policy/src/reorder.una" title="steps/31-policy/src/reorder.una" verified="check, run"
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

`import release (line_count)` brings the policy from the module `release` into this one. An import names the module and, in parentheses, the names it uses from it; [chapter 11](/learn/packages/#s11-2) covers imports. The call `line_count(list)` looks like a function call, and it is one: `list` flows into `from internal Text`, and the result is a public `Int`.

`una run .` prints:

```text include="steps/31-policy/expected/output.txt"
2 SKUs to reorder
```

### What the build report shows

`una report .` prints the build report ([chapter 18](/learn/tools/#s18-4)): what the package was proven to do, and what it trusts. Two of its sections are about releases:

```text include="steps/31-policy/expected/commands/report.txt#L2,L9-L12,L15-L16,L25"
package reorder 0.1.0
information:
  release.line_count at src/release.una:14:6, purpose "report the size of the reorder list", owner purchasing
  release.line_count at src/release.una:18:6, purpose "report the size of the reorder list", owner purchasing
  release.line_count at src/reorder.una:13:20, purpose "report the size of the reorder list", owner purchasing
tcb:
  trusted modules: release (19 lines)
out of model: timing, termination and divergence, resource consumption and allocation, stack exhaustion, external systems beyond declared signatures, races between the check and the use of a file path, hard links, order of effects across concurrent tasks
```

- **`information:`** lists every call of a policy, with its place, its purpose and its owner. Two calls are in the policy's examples, in `release.una`, and one in `main`.
- **`tcb:`**, the *trusted computing base*, lists the code the guarantee trusts. `trusted modules: release (19 lines)` is the code a reviewer must read line by line.
- **`out of model:`** lists what the guarantee does not cover, such as timing and termination ([What the checker promises](#what-the-checker-promises)).

Adding a trusted module is a change to the manifest, and each new release adds a line to `information:`, so both show in review.

### How a policy behaves

#### A policy call obeys the program counter

A policy call is allowed only where the program counter is at or below the policy's `to` label. A policy's result may be lower than what it read, so a call under a branch on data above `to` would reveal the condition through that result. For a policy to `public`, such as `line_count`, that means a path that public data alone decides. Call the policy only when the list is not empty:

```diff include="steps/31-policy..steps/33-release-under-branch:src/reorder.una" context="1" title="src/reorder.una"
--- a/src/reorder.una
+++ b/src/reorder.una
@@ -12,2 +12,3 @@
     if error use ""
-  @console.print("{line_count(list)} SKUs to reorder")
+  let shown = if list.len > 0 then line_count(list) else 0
+  @console.print("{shown} SKUs to reorder")
```

```text include="steps/33-release-under-branch/expected/rendered.txt#L1-L8"
[U4002] Error: policy `line_count` lowers data to `public`, and it is called under an `internal` condition, which its result would reveal
    ╭─[ src/reorder.una:13:36 ]
    │
 13 │   let shown = if list.len > 0 then line_count(list) else 0
    │                  ──────┬─────      ────────┬───────
    │                        ╰───────────────────────────── the labeled condition
    │                                            │
    │                                            ╰───────── policy `line_count` lowers data to `public`, and it is called under an `internal` condition, which its result would reveal
```

`list.len > 0` is `internal`, so the call runs under an `internal` condition, and U4002 points at both. The second diagnostic of the same run, U4003 at the print, follows from the first: `shown` was chosen by the condition. Call each release to `public` on a path that public data alone decides. A policy whose `to` keeps a label, such as `internal Int`, may be called under a branch on data up to that label.

#### A policy needs a trusted module

Remove `trusted` from the header of `release`:

```diff include="steps/31-policy..steps/34-untrusted-header:src/release.una" context="1" title="src/release.una"
--- a/src/release.una
+++ b/src/release.una
@@ -1,2 +1,2 @@
-trusted module release
+module release
 
@@ -11,9 +11 @@
 count_lines(list: internal Text) -> Int = list.split(on: "\n").filter(keep: fn(line) -> line.len > 0).len
-
-example "a list of two SKUs has two lines"
-  do line_count("LAMP-01,20\nDESK-02,5\n")
-  expect result == 2
-
-example "a list of three SKUs, with a blank line between two of them"
-  do line_count("LAMP-01,20\n\nMUG-03,40\nDESK-02,5")
-  expect result == 3
```

```text include="steps/34-untrusted-header/expected/diagnostics.txt"
error U4004 at src/release.una:4:12: policy `line_count` is declared in module `release`, which is not trusted
error U7005 at una.toml:7:12: [trusted] modules lists `release`, whose header does not say `trusted module`
```

Two diagnostics, one for each half of the double declaration. U4004 says the policy is in a module that is not trusted. U7005 says the manifest lists a module whose header does not agree. Both halves must say `trusted`.

#### Inside `via`, labels are not checked

Inside a `via` function the checker does not check labels, since lowering one is its job. Types, refinements and proofs are still checked.

That makes a `via` function trusted code, and it covers what the function does and how it fails, as well as what it returns. A `via` function may declare `uses`, and the policy then has the same `uses`. Its operations stay within those `uses`, but nothing checks the labels of what it sends through them: a `via` function that holds a console could print the raw value it receives, and `una check` would pass. So keep every function of a trusted module small, keep each `via` function pure, with no `uses`, unless the release needs one, such as a keyed hash, and review it line by line. [Reference](#reference) links the rules of the specification that say so.

#### The `via` function's own rules

The `via` function must be private, used only through its policy, of the same types as `from` and `to` apart from labels, and without a `requires` clause, since a policy call checks its argument against `from` only. Each is U4005 otherwise; [a public `via` function](#a-public-via-function-u4005) shows one.

> [!WARNING]
> A policy is trusted code: the guarantee holds only if the `via` function releases what its purpose says and nothing more, through its result, its failures or its effects. Release the least you can, such as a count, a first letter or one yes-or-no answer, and keep `via` functions short enough to review line by line.

### What to release

:::decide
**Which to use:**

| The program needs… | Release |
| --- | --- |
| How much data there is | a count, as `line_count` does |
| To tell values apart in a log, without showing them | a masked form, such as a first letter and a domain ([section 17.6](#s17-6)) |
| One decision, such as whether to fail | one `Bool` ([exercise 3](#exercise-3-a-blocked-domain)) |
| The data itself, to a service | no policy: an `accepts` clause on that service ([section 17.2](#s17-2)) |
:::

### What the U4 codes mean

| Code | Typical cause | Usual repair |
| --- | --- | --- |
| U4001 | A value flowing into a declared type with a lower label: a return, a parameter, a field, an annotated `let` | Raise the declared label, or lower the value through a policy |
| U4002 | A failure, or a call that may fail or act, under a branch on labeled data; a policy call under a branch on data above its `to` label | Return a labeled value instead of failing, or release before the branch |
| U4003 | An argument of an operation above the operation's `accepts`, or an operation under a branch on data above it | Send less, or send it to a place that accepts it, or act outside the branch |
| U4004 | A policy in a module that is not trusted | Move it into a trusted module |
| U4005 | A policy whose `via` function is public, used directly, of the wrong types, or has a `requires` clause | Make `via` private, match the types, drop `requires`, and call the policy |
| U4007 | A category that `una.toml` does not declare | Declare it, or correct its name |

### Check yourself: policies

First, the main idea. Someone thinks the policy is too much ceremony, drops the import, and writes the counting function in `reorder` itself:

```diff include="steps/31-policy..steps/35-plain-function:src/reorder.una" context="1" title="src/reorder.una"
--- a/src/reorder.una
+++ b/src/reorder.una
@@ -2,3 +2,4 @@
 
-import release (line_count)
+--- How many lines a list has.
+count_lines(list: internal Text) -> Int = list.split(on: "\n").filter(keep: fn(line) -> line.len > 0).len
 
@@ -12,2 +13,2 @@
     if error use ""
-  @console.print("{line_count(list)} SKUs to reorder")
+  @console.print("{count_lines(list)} SKUs to reorder")
```

Does `una check .` pass?

:::answer Show the answer
No:

```text include="steps/35-plain-function/expected/rendered.txt#L1"
[U4001] Error: the result of `count_lines` is `Int`, and this value is `internal Int`: a flow from `internal` to `public`
```

The body is the same as `count_lines` in `release.una`, but here it is an ordinary function, so its labels are checked: a count of an `internal` list is `internal`, and the header says `Int`. Only a `via` function, reached through a policy of a trusted module, may lower a label.
:::

Second, a detail of this policy. `release.una` ends with two examples of the policy. The second gives it a list with a blank line between two SKUs:

```una include="steps/31-policy/src/release.una#L17-L19" title="steps/31-policy/src/release.una"
example "a list of three SKUs, with a blank line between two of them"
  do line_count("LAMP-01,20\n\nMUG-03,40\nDESK-02,5")
  expect result == 3
```

What does `line_count` return for that text, and does the example pass?

:::answer Show the answer
It returns 3, and the example passes:

```text include="steps/31-policy/expected/commands/test.txt#L2-L5"
example release "a list of two SKUs has two lines" ... ok
example release "a list of three SKUs, with a blank line between two of them" ... ok

2 examples: 2 passed, 0 failed
```

`count_lines` splits the text at each line break, which gives four pieces, one of them empty, then keeps only the pieces that are not empty. A blank line is not a SKU, so it is not counted. That is a choice of the `via` function, and an example is how you pin it down: the checker does not look inside `via`.
:::

## 17.6 Day-to-day: shipping notices with labels

### What changes from chapter 12

Now the service from [chapter 12](/learn/capabilities/#s12-5), with the customers' data labeled. Four changes make it safe: labels on the fields of `Customer`, an `accepts` clause on `Mailer`, a label on the result of `notice`, and a policy in a new trusted module, `privacy`, which `notices.una` imports and `notify` calls. The doc comments of `Customer`, `Mailer`, `notice` and `notify` change to say so. The rest of the code is chapter 12's, and so are its examples, with one expected value changed and two examples added for the policy ([section 17.7](#s17-7)). Each part below says what it is for, and which idea of this chapter it uses.

### Labels on the data

A customer's name and address are personal data, so both fields are `secret[PII]` ([section 17.4](#s17-4)). The id and the notice preference stay public: the log needs the id, and the program branches on the preference.

```una include="day-to-day/src/notices.una#Customer" title="day-to-day/src/notices.una"
--- A customer, as the customer directory knows them. Name and address are personal data.
pub kind Customer
  id: Text
  name: secret[PII] Text
  email: secret[PII] Text
  wants_notices: Bool
```

### A mail service that may receive them

The mail service must receive the real address and a notice that names the customer. So its operation is a sink whose ceiling is personal data ([section 17.2](#s17-2)). Without `accepts secret[PII]`, the call that sends the notice would be U4003 twice, once for the address and once for the body ([a sink without `accepts`](#a-sink-without-accepts-u4003) shows it).

```una include="day-to-day/src/notices.una#Mailer" title="day-to-day/src/notices.una"
--- The mail service, a service on the network. It may receive personal data.
pub capability Mailer
  op send(to: Text, subject: Text, body: Text) -> Unit
    fails ServiceError
    accepts secret[PII]
```

### A notice that carries the label

The text of the notice interpolates the customer's name, so it joins the name's label: its result is `secret[PII] Text` ([How labels follow data](#how-labels-follow-data)). Only the mail service, which accepts that label, receives it.

```una include="day-to-day/src/notices.una#notice" title="day-to-day/src/notices.una"
--- The text of a shipping notice. It holds the customer's name, so it carries the name's label.
pub notice(customer: Customer, shipment: Shipment) -> secret[PII] Text = "Hello {customer.name}, your order {shipment.order} is on its way with {shipment.carrier}."
```

### The leak the checker stops

In chapter 12, `notify` returned the address it wrote to, and the log printed it. Keep that design, with the label it now needs, and the checker finds the log line:

```diff include="day-to-day..steps/36-leak-2:src/notices.una" context="1" title="src/notices.una"
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

```text include="steps/36-leak-2/expected/rendered.txt#L1-L6"
[U4003] Error: `@log.print` accepts `public` data, and this argument is `secret[PII]`
    ╭─[ src/notices.una:78:16 ]
    │
 78 │     @log.print(log_line(shipment, outcome: outcome))
    │                ──────────────────┬─────────────────
    │                                  ╰─────────────────── `@log.print` accepts `public` data, and this argument is `secret[PII]`
```

The message points at `@log.print`, in `dispatch`, although the address came from `notify`, two functions away. The label followed the address through `notify`'s result, the `Result` of `attempt`, and the text `log_line` built from it.

### The release that is allowed

The operator needs to see which customer each notice went to, not the address itself. A policy in a trusted module, `privacy`, releases a masked form: the first letter of the mailbox and the domain ([section 17.5](#s17-5)).

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

`mask_email` never returns more than one character of the mailbox. An address it cannot read is hidden whole, rather than shown in part. Its result is written `public Text`, so a reader sees at once that it lowers the label. `notify` is the only function that needs the raw address, so it is where the release happens: it sends the real address to the mail service, then returns the masked form, which is public. The rest of the program never holds the address, so the log line is public too:

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

The call of the policy obeys the program counter too. `masked_email` releases to `public`, so it may be called only where the program counter is `public`: here, after the checks of the directory and of `wants_notices`, which are public. A call of `masked_email` inside a branch on labeled data would be U4002, since its public result would reveal the condition. Put each release to `public` on a path that public data alone decides.

### The manifest

The manifest declares the category, so that `secret[PII]` is allowed ([section 17.4](#s17-4)), and the trusted module, so that `privacy` may hold a policy ([section 17.5](#s17-5)):

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

`una run .` prints the log shown in [What you'll build](#what-youll-build). `una report .` lists every call of `privacy.masked_email` under `information`, with its place, purpose and owner: the one in `notify`, and the two in the policy's examples ([section 17.7](#s17-7)). It lists `privacy` under `tcb`, with its line count, as the code the guarantee trusts. `dispatch`, `log_line`, `reason`, `main`, the kinds `Shipment`, `ServiceError` and `NoticeError`, and the handlers `directory`, `outbox`, `mail_down` and `directory_down` are those of chapter 12, unchanged.

So the whole change to chapter 12's program is: one `import` line, three labels (on `name`, on `email` and on the result of `notice`), one `accepts` clause, one call of a policy in `notify`, the doc comments of `Customer`, `Mailer`, `notice` and `notify`, a module of 19 lines, and in the examples, the address the first one expects and two examples of the policy. In exchange, a later change outside the trusted module that prints a name or an address fails `una check` instead of reaching the log. The `via` functions are the exception: their labels are not checked ([section 17.5](#s17-5)). A reviewer who wants to know what personal data leaves the program reads the `accepts` clauses and the trusted module, line by line, and not every other line.

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

example "the log shows the first letter and the domain of an address"
  do masked_email("tomas@example.invalid")
  expect result == "t***@example.invalid"

example "an address the mask cannot read is hidden"
  do masked_email("no address")
  expect result == "(hidden)"
```

## 17.7 Testing it

### Examples of the policy

The examples are those of [section 12.6](/learn/capabilities/#s12-6), with one change: the first one expects the masked address, `r***@example.invalid`, which is what `notify` now returns. Two more examples, at the end of the file, test the policy itself:

```una include="day-to-day/src/notices.una#L152-L158" title="day-to-day/src/notices.una" caption="the policy's examples"
example "the log shows the first letter and the domain of an address"
  do masked_email("tomas@example.invalid")
  expect result == "t***@example.invalid"

example "an address the mask cannot read is hidden"
  do masked_email("no address")
  expect result == "(hidden)"
```

A policy can be called like a function, so its examples need no fakes. Test the release the way a reviewer would read it: what an ordinary value becomes, and what an unexpected one becomes. A mask that showed a whole malformed address would pass the type checker, since labels are not checked inside `via`, so this example is the check that it does not.

### Examples can observe a secret

An `expect` line compares a value whatever its label, and a `do` line is checked like ordinary code: an example can observe a secret, but cannot send it anywhere the program itself could not ([Examples are not sinks](#examples-are-not-sinks)). So chapter 12's example of `notice` still passes: its result is now a `secret[PII] Text`, and its `expect` line compares it with the text of the notice.

### The failure paths and their fakes

The examples of the failure paths are chapter 12's, with its fakes: `directory_down` for the directory that does not answer, and `mail_down`. The examples of `UnknownCustomer`, `OptedOut` and `DirectoryDown` install `mail_down` on purpose, as [A failure that comes first](/learn/capabilities/#a-failure-that-comes-first) explains: had `notify` sent any mail before it failed, the example would see `MailDown`. Labels do not alter which paths exist or how a fake reaches them. ([Chapter 14](/learn/testing/#s14-3) gives a more direct way to say that no mail went out, `expect not performed`; this chapter keeps chapter 12's examples, so that only the labels change.) The fakes `outbox` and `mail_down` are handlers of `Mailer`, which now accepts `secret[PII]`. They pass the check because they do nothing with what they receive. A fake mail service that printed each message, as `printed` in [chapter 12](/learn/capabilities/#s12-3) did, would be U4003: what it prints could reveal the notice ([A handler is checked for its most sensitive caller](#a-handler-is-checked-for-its-most-sensitive-caller)).

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L12"
example notices "a customer who wants notices gets one" ... ok
example notices "an unknown customer is rejected before any mail is sent" ... ok
example notices "a customer who asked for no notices is rejected before any mail is sent" ... ok
example notices "a directory that does not answer is DirectoryDown, before any mail is sent" ... ok
example notices "a mail service that does not answer is MailDown" ... ok
example notices "the notice names the customer, the order and the carrier" ... ok
example notices "a skipped shipment says why in the log" ... ok
example notices "the log shows the first letter and the domain of an address" ... ok
example notices "an address the mask cannot read is hidden" ... ok

9 examples: 9 passed, 0 failed
```

## 17.8 Common mistakes

Each mistake below is a small change to the day-to-day program or to a step of this chapter, as it says. Each diagnostic names the place a value would flow into, the label it has, and the label that place allows; read those three, and the repair follows.

### Dropping a label in a return type (U4001)

:::mistake
In [step 03](#a-catalog-with-a-confidential-cost), declare the margin as a plain `Int`:

```diff include="steps/03-labels..mistakes/1:src/pricing.una" context="1" title="src/pricing.una"
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

*Why:* `product.cost` is `confidential`, so the difference is too, and a result is checked against the declared label. It happens when a function is first written with plain types, and a field it reads gains a label later. The message gives the declared type, `Int`, then the value's, `confidential Int`, then the direction of the flow.

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

*Why:* an operation accepts `public` data unless it says more. It happens when a capability is declared before its data is labeled, as in chapter 12. una reports the address and the body, one diagnostic each, since each argument is its own sink; the mark points at the argument.

*Fix:* give the operation the ceiling of the service it stands for. Do not lower the data to fit: the mail service needs the real address.
:::

### A branch that decides a public result (U4001)

:::mistake
In [step 19](#a-fee-decided-by-a-branch), declare the fee as a plain `Int`:

```diff include="steps/19-branches..mistakes/3:src/shipping.una" context="1" title="src/shipping.una"
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

*Why:* the fee is a constant in each branch, but which branch runs depends on `spent`. It is easy to miss, since no labeled value appears in the result. The message says *which value it returns depends on this `confidential` condition*, and the mark points at the condition, since that is where the information enters.

*Fix:* declare `confidential Int`.
:::

### A category that is not declared (U4007)

:::mistake
In [step 26](#a-courier-that-may-receive-a-phone-number), remove the `[labels]` table from `una.toml`:

```diff include="steps/26-categories..mistakes/4:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -5,5 +5,2 @@
 
-[labels]
-categories = ["PII"]
-
 [run]
```

```text include="mistakes/4/expected/rendered.txt#L1-L2,L10-L11"
[U4007] Error: label category `PII` is not declared in `[labels] categories` of `una.toml`
   ╭─[ src/courier.una:7:17 ]
[U4007] Error: label category `PII` is not declared in `[labels] categories` of `una.toml`
    ╭─[ src/courier.una:13:20 ]
```

*Why:* each package declares its categories, so a typo cannot create one. It happens when code is copied from another package, whose manifest declared the category. una reports each use of the category, one diagnostic each: in the field `phone`, and in the `accepts` clause of `book`. The marks point at the uses, not at the manifest, since that is where the unknown name is used.

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

*Why:* trust is declared twice, in the module and in the manifest, so that adding it shows in review. It happens when a trusted module is copied into a package without its manifest line. The message names the module and the half of the declaration that is missing.

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

*Why:* a public `via` function would release data without the policy, so its calls would be missing from the report. It happens when a helper is made public to reuse it elsewhere, or to test it. The message names the function and gives both repairs.

*Fix:* keep `via` private, and call the policy, `masked_email`. An example can call the policy directly, as [section 17.7](#s17-7) does.
:::

## 17.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added, and a stub when there is one. `una test .` fails there until the exercise is done. Work in the start package: edit the files it names, run `una fmt .` to put the code in canonical form, then `una check .` until it passes, then `una test .`.

### Exercise 1: release the domain

::::exercise
The operations team counts notices by mail provider, so it needs the domain of each address, and nothing else. Add a policy `email_domain` to `privacy.una`, from `secret[PII] Text` to `public Text`, that gives the part after the `@`, or `(none)` when there is no single `@`. The start package already imports it, so `una check .` reports U1001 until it exists, and it ends with:

```una include="exercises/1/start/src/notices.una#L160-L166" title="exercises/1/start/src/notices.una"
example "the domain of an address"
  do email_domain("rosa@example.invalid")
  expect result == "example.invalid"

example "an address with no domain has none"
  do email_domain("no address")
  expect result == "(none)"
```

:::hint
*Hint:* write it in two parts, as `masked_email` is. First the policy, with its five lines: `from`, `to`, `via`, a `purpose` and an `owner`. Then a private `via` function with the same types apart from labels, which splits the address on `@`, as `mask_email` does, and gives the second part when there are exactly two.
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

`una test .` reports 11 examples passing. `una report .` now lists the calls of `email_domain` under `information`, with their purpose.
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

```una include="exercises/2/start/src/notices.una#L164-L170" title="exercises/2/start/src/notices.una"
example "a priority customer's subject says so"
  do subject(Customer(id: "C-17", name: "Rosa", email: "rosa@example.invalid", wants_notices: true, vip: true), shipment: Shipment(order: "A-1001", customer: "C-17", carrier: "Parcelo"))
  expect result == "Priority: order A-1001 has shipped"

example "another customer's subject is plain"
  do subject(Customer(id: "C-20", name: "Tomas", email: "tomas@example.invalid", wants_notices: true, vip: false), shipment: Shipment(order: "A-1002", customer: "C-20", carrier: "Parcelo"))
  expect result == "Order A-1002 has shipped"
```

:::hint
*Hint:* an `if … then … else …` on `customer.vip`, with an interpolated subject in each branch ([How the program counter rises](#how-the-program-counter-rises)). Keep the result type: try `-> Text` once, and read what the checker says.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/2/start/expected/commands/test.txt#L11-L13,L16"
example notices "a priority customer's subject says so" ... FAILED
  src/notices.una:166: expect result == "Priority: order A-1001 has shipped"
  it is false, with `result` = `"Order A-1001 has shipped"`
11 examples: 10 passed, 1 failed
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

```una include="exercises/3/start/src/notices.una#L162-L166" title="exercises/3/start/src/notices.una"
example "an address at a blocked domain is rejected before any mail is sent"
  given @customers = directory(sample_customers())
  given @mailer = mail_down()
  do notify(Shipment(order: "A-1006", customer: "C-30", carrier: "Parcelo"))
  expect fails Blocked
```

Like the failure paths of the program, it installs `mail_down`, so it passes only if `notify` fails with `Blocked` before any mail goes out.

The direct way, a branch on `customer.email.ends_with(suffix: "@blocked.example.invalid")` in `notify`, does not check. Among the diagnostics una reports:

```text include="exercises/3/direct/expected/rendered.txt#L10"
[U4002] Error: this `fail` depends on `secret[PII]` data, so its failure would reveal it; return a labeled value instead of failing
```

:::hint
*Hint:* `notify` needs one public fact about the address: is it at the blocked domain? A policy can release exactly that bit ([What to release](#what-to-release)), and `notify` can branch on a public `Bool` and fail. Add the policy to `privacy.una`, import it in `notices.una` next to `masked_email`, and add an `else if` branch to `notify`.
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

## 17.10 Recap and reference

### For agents

:::agents
`una --json check .` reports the U4xxx codes in the domain `security`. For [the leak the checker stops](#the-leak-the-checker-stops):

```json include="steps/36-leak-2/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U4003","severity":"error","domain":"security","message":"`@log.print` accepts `public` data, and this argument is `secret[PII]`","primary":{"file":"src/notices.una","start":{"line":78,"col":16},"end":{"line":78,"col":52}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"send `@log.print` only data labeled `public` or lower, or send this value to an operation that accepts `secret[PII]`","edit":null},{"rank":2,"escape_cost":1,"escape":{"kind":"trusted","cost":"the guarantee then rests on trusted code, whose labels are not checked: a policy releases the data, or a module joins the trusted base; it is listed in the build report and needs review"},"description":"declassify the value through a policy of a trusted module","edit":null}],"explain":"una explain U4003"}],"fixable":0}
```

Neither repair has an `edit`, so `una fix` changes nothing: each needs a decision about the data. The first keeps the label. The second, a policy, has `escape_cost` 1 and an `escape` of kind `trusted`: it moves the guarantee onto trusted code. Prefer the repairs with `escape_cost` 0. The compact rule: *a value flows only to a place labeled at or above it, branches label what they decide, `fail` needs a `public` program counter, and only a `policy` of a module trusted in its header and in `una.toml` lowers a label.*
:::

### Recap

:::recap
- A label is a level and categories: `public`, `internal`, `confidential`, `secret`, `restricted`, and categories such as `[PII]` that `una.toml` declares.
- A result carries the labels of what it was computed from, and of every condition or loop that chose it.
- Every operation argument is a sink. `Console.print` accepts `public`, and your own operations accept what `accepts` says.
- Data read from files or the environment is `internal`. A keyed hash from `Keys.hmac`, a `Hashed`, keeps the label of what it hashed, and only `==` and `!=` read it.
- Under a branch on labeled data, return a labeled value instead of failing or acting.
- Lower a label only through a `policy` with a private `via` function, in a module trusted in its header and in `una.toml`.
- Release the least you can, test each policy with examples, and read the release list in `una report .`.
:::

### Reference

:::reference
- Construct pages: [labels](/docs/language/information-flow/labels/), [`policy`](/docs/language/information-flow/policy/), [trusted modules](/docs/language/information-flow/trusted/), [host capabilities](/docs/language/capabilities/host/), [`example`](/docs/language/examples/example/)
- Configuration: [`[labels] categories`](/docs/configure/labels/categories/), [`[trusted] modules`](/docs/configure/trusted/modules/)
- Standard library: [the prelude and the host capabilities](/docs/std/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U2001](/docs/errors/U2001/), [U3015](/docs/errors/U3015/), [U4001](/docs/errors/U4001/), [U4002](/docs/errors/U4002/), [U4003](/docs/errors/U4003/), [U4004](/docs/errors/U4004/), [U4005](/docs/errors/U4005/), [U4007](/docs/errors/U4007/), [U7005](/docs/errors/U7005/)
- Specification: [information flow](/docs/spec/07-information-flow/), including [the guarantee and its scope](/docs/spec/07-information-flow/#s1) (noninterference), [labels](/docs/spec/07-information-flow/#s2), [declassification policies](/docs/spec/07-information-flow/#s5) (rule 3: inside `via` functions labels are not checked, and they are part of the trusted computing base) and [checking](/docs/spec/07-information-flow/#s7) (rules 3 to 6), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [memory model](/docs/spec/17-memory-model/#s6) (labels in loops and on editable names), [standard library](/docs/spec/14-standard-library/) (the host capabilities and their labels), [diagnostics and ABI](/docs/spec/13-diagnostics-and-abi/)
- Security model: [what is proven, trusted and outside the model](/docs/security/)
:::
