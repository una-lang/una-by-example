---
learn: "7"
title: Results and failures
editions: ["0.2"]
codes: [U0101, U0102, U1001, U2001, U2007, U2016, U3007, U3008, U3009, U3013, U5001, U7003]
time: 60
builds: An order-intake step that accepts or rejects each line of an order batch
prerequisites: ["3", "4", "5", "6"]
template: 2
nav: ["Option", "fails and fail", "The handling clauses", "attempt and Result", "checked and opaque predicates", "Data from outside", "Day-to-day: order intake", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 7 Results and failures


Real programs spend much of their code on what goes wrong: input that does not parse, a product that does not exist, a service that does not answer. In Una a failure is an ordinary value of a kind you declare, a function's header says which kind it can fail with, and every call that can fail is followed by a line that says what to do about it. This chapter shows how to design those kinds, how to handle and translate failures between layers, and how to process a batch in which some items fail and others succeed.

## What you'll build

:::build
An order-intake step for a small store. It reads order lines such as `LAMP-01, 2`, checks each one against an inventory service, and reports every line, accepted or rejected, with a reason a person can act on:

```text include="day-to-day/expected/output.txt"
ok      2 x LAMP-01
reject  3 of DESK-02 wanted, 1 left
reject  no product has the SKU CHAIR-09
reject  the quantity in 'LAMP-01, two' is not a whole number above 0
reject  cannot read the line 'LAMP-01'
```

You will learn to:

- declare an error kind whose variants carry what someone needs to fix the problem;
- choose among the five handling clauses, and translate a failure from one layer to the next;
- handle failures that come from a capability, such as a service that times out;
- turn a failure into a value with `attempt`, so one bad line does not stop a batch;
- test every failure path with examples and fake services.
:::

## Why it works this way

In many languages a function can fail in ways its signature does not show: an exception thrown three calls deep, a null returned on a path nobody tested, a panic on an index out of range. A reader has to read the bodies to find out what can go wrong, and a reviewer cannot tell from a diff whether a new failure was introduced.

Una moves all of that into view. Three rules do it:

:::steps
1. **A failure is a value of a sum kind.** You declare it like any other kind, and its variants can carry data.
2. **A header says what a function can fail with.** `fails OrderError` is part of the contract, next to `requires` and `uses`. A public function that does not say `fails` cannot fail, and the checker holds it to that.
3. **Every call that can fail is handled where it is made.** The next line, indented, says what happens: recover with a value, pass the failure on, or turn it into a failure of your own kind. Nothing propagates unless that line says so.
:::

The price is a few extra lines at each call. In return, the failure behavior of any function can be read from its header and its call sites, and the checker proves that no failure goes unhandled.

> [!KEY]
> Nothing in Una fails at run time without the code saying so, apart from a few aborts outside the program's logic, such as running out of call depth or memory (U6003) or host text that is not valid UTF-8 (U6005); [Reference](#reference) lists them all. Division by zero and fixed-width overflow are ruled out by proof ([chapter 5](/learn/contracts/)), and there are no exceptions to catch.

## 7.1 A value that may be missing: `Option`


### What an `Option` is

Some questions have no answer. Ask a catalog for the price of a SKU it does not sell, ask an empty list for its first element, or ask the text `"seven"` for the number it holds: there is nothing to give back. An **`Option`** is the type of an answer that may be missing. Think of a parcel locker at a pickup point: you open it, and either a parcel is inside or the locker is empty. Before you carry anything away, you look.

`Option[T]` is a sum kind of the prelude ([chapter 4](/learn/kinds/#s4-2)) with two variants:

- `Some(value)` holds one value of the type `T`. A price lookup that finds the price gives `Some(1990)`, an `Option[Int]`.
- `None` holds nothing. It means "there is no value here".

`T` is a **type parameter**: it stands for whatever type the option may hold. `Option[Int]` may hold an `Int`, and `Option[Product]` a `Product`. An `Option[Int]` is not an `Int`: you cannot add it to a number, compare it with `<`, or use it where an `Int` is expected until you have said what happens when it is `None`.

### Why absence needs its own type

In many languages a search that finds nothing returns a special value, often called null, of the same type as a real answer. The type then says that a price is always there, and the first line that uses a missing price fails while the program runs, often far from the search.

In Una the type says it. Here is a price lookup that uses the search result as if the product were always found:

```diff include="steps/01-option..steps/02-missing-price:src/lookup.una" context="1" title="src/lookup.una"
--- a/src/lookup.una
+++ b/src/lookup.una
@@ -11,5 +11,3 @@
   let found = catalog.first_where(keep: fn(product) -> product.sku == sku)
-  when found
-    is Some(product) -> Some(product.cents)
-    is None -> None
+  Some(found.cents)
 
```

`una check .` reports:

```text include="steps/02-missing-price/expected/rendered.txt"
[U1001] Error: `Option[Product]` has no field `cents`, and no function `cents` in scope applies
    ╭─[ src/lookup.una:12:14 ]
    │
 12 │   Some(found.cents)
    │              ──┬──
    │                ╰──── `Option[Product]` has no field `cents`, and no function `cents` in scope applies
    │
    │ Note: run `una explain U1001` for an explanation
────╯
```

Read it from the top. `first_where` returned an `Option[Product]`, and the message says that this type has no field `cents`: the field belongs to `Product`, which the option may or may not hold. The mark points at `.cents`. The checker does not guess what a missing product should mean. You decide, with one of the forms of the next part, and the decision is written where the value is used.

### How to write and use an `Option`

The step of this part shows each form on a shelf count, which a clerk may not have taken yet:

```una include="steps/03-option-forms/src/counts.una#shown..typed_units" title="steps/03-option-forms/src/counts.una"
--- What a shelf label shows for a count that may be missing: `when` with both arms.
shown(count: Option[Int]) -> Text
=
  when count
    is Some(units) -> "{units} on the shelf"
    is None -> "not counted yet"

--- Whether a shelf holds more than 10 units: `when` with an `else` arm.
well_stocked(count: Option[Int]) -> Bool
=
  when count
    is Some(units) -> units > 10
    else -> false

--- The units to order for a shelf: a missing count orders a full shelf of 12.
to_order(count: Option[Int]) -> Int = 12 - count.or_else(default: 0)

--- Whether a shelf still needs counting: a test of the variant, in a condition.
needs_count(count: Option[Int]) -> Bool = count is None

--- The units typed by a clerk, or 0 when the text is not a number: `if none use`.
typed_units(raw: Text) -> Int
=
  let units = raw.trim.to_int()
    if none use 0
  units
```

#### Making one: `Some`, `None`, and the functions that return one

```una include="steps/03-option-forms/src/counts.una#L33-L35" title="steps/03-option-forms/src/counts.una"
  let counted = Some(14)
  let missing: Option[Int] = None
  @console.print("{counted} {missing}")
```

```text include="steps/03-option-forms/expected/output.txt#L1"
Some(14) None
```

`Some(14)` wraps a value. `None` holds nothing, so it says nothing about the type: write the type on the binding, `Option[Int]`, as for an empty list. More often an `Option` comes from a function. In the prelude, these return one: `first`, `at` and `first_where` on a list, `get` on a map ([section 10.4](/learn/collections/#s10-4)), and `to_int` and `find` on a text:

```una include="steps/03-option-forms/src/counts.una#L44-L47" title="steps/03-option-forms/src/counts.una"
  let sku = "LAMP-01"
  let dash = sku.find(text: "-")
  let number = sku.slice(start: 5, end: 7).to_int()
  @console.print("{dash} {number} {sku.chars().first()}")
```

```text include="steps/03-option-forms/expected/output.txt#L8"
Some(4) Some(1) Some("L")
```

`find` gives the position of the first `-` in `LAMP-01`, `to_int` reads the digits `01` as 1, and `chars().first()` is the first character.

#### Both cases: `when`

A `when` ([chapter 4](/learn/kinds/#s4-3)) takes an `Option` apart. `shown` has one arm per variant: `is Some(units)` binds the value inside to the name `units`, and `is None` says what to do without one. Each arm gives a `Text`, so the `when` gives one too.

```una include="steps/03-option-forms/src/counts.una#L36" title="steps/03-option-forms/src/counts.una"
  @console.print("{shown(counted)} / {shown(missing)}")
```

```text include="steps/03-option-forms/expected/output.txt#L2"
14 on the shelf / not counted yet
```

#### One case and the rest: `else`

When only the `Some` case needs work, an `else` arm covers every variant without an arm of its own. `well_stocked` answers `false` for a missing count:

```una include="steps/03-option-forms/src/counts.una#L37" title="steps/03-option-forms/src/counts.una"
  @console.print("{well_stocked(counted)} {well_stocked(missing)}")
```

```text include="steps/03-option-forms/expected/output.txt#L3"
true false
```

#### A default: `or_else`

`count.or_else(default: 0)` is the value inside `Some`, or the default for `None`. It is the short form of a `when` whose `None` arm is a plain value. `to_order` orders a full shelf of 12 units when no count is known:

```una include="steps/03-option-forms/src/counts.una#L38" title="steps/03-option-forms/src/counts.una"
  @console.print("{to_order(Some(5))} {to_order(missing)}")
```

```text include="steps/03-option-forms/expected/output.txt#L4"
7 12
```

#### A question about the case: `is None` and `is_some`

`count is None` is a condition, `true` or `false`, that tests the variant without taking the value out. `is_some()` is the same question the other way round:

```una include="steps/03-option-forms/src/counts.una#L39" title="steps/03-option-forms/src/counts.una"
  @console.print("{needs_count(missing)} {missing.is_some()}")
```

```text include="steps/03-option-forms/expected/output.txt#L5"
true false
```

#### A default under the line: `if none use`

`typed_units` writes the default on its own line under the call: `if none use 0`. After that line, `units` is a plain `Int`. This clause, and `if none fail`, which turns a missing value into a failure, belong to [chapter 6, Failure](#s7-3).

```una include="steps/03-option-forms/src/counts.una#L40-L42" title="steps/03-option-forms/src/counts.una"
  let typed = typed_units(" 7 ")
  let spelled = typed_units("seven")
  @console.print("{typed} {spelled}")
```

```text include="steps/03-option-forms/expected/output.txt#L6"
7 0
```

### Looking up a price

The forms together, in a catalog lookup. `price_of` passes the absence on to its caller, and `label` decides what it means:

:::steps
```una include="steps/01-option/src/lookup.una" title="steps/01-option/src/lookup.una" verified="check, run"
module lookup

--- A product the store sells, with the price of one unit in cents.
kind Product
  sku: Text
  cents: Int

--- The price of `sku`, or `None` when the catalog does not list it.
price_of(catalog: List[Product], sku: Text) -> Option[Int]
=
  let found = catalog.first_where(keep: fn(product) -> product.sku == sku)
  when found
    is Some(product) -> Some(product.cents)
    is None -> None

--- What a product page shows for `sku`.
label(catalog: List[Product], sku: Text) -> Text
=
  let price = price_of(catalog, sku: sku)
  when price
    is Some(cents) -> "{sku}: {cents} cents"
    is None -> "{sku}: not sold here"

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Product(sku: "LAMP-01", cents: 1990)
  let desk = Product(sku: "DESK-02", cents: 15900)
  let catalog = [lamp, desk]
  @console.print(label(catalog, sku: "DESK-02"))
  @console.print(label(catalog, sku: "CHAIR-09"))
  let missing = price_of(catalog, sku: "CHAIR-09")
  @console.print("{missing} or {missing.or_else(default: 0)}")
  let typed = "3".to_int()
  @console.print("{typed} and {catalog.at(index: 5)}")
```

1. **`catalog.first_where(keep: fn(product) -> product.sku == sku)`.** The first element for which the test holds, as an `Option[Product]`. The test is a lambda, a function written in place ([chapter 10](/learn/collections/#s10-2); [section 10.3](/learn/collections/#s10-3) uses more of them).
2. **`when found`.** One arm per case, `is Some(product)` and `is None`. The name in `Some(product)` binds the value inside.
3. **`Some(product.cents)`.** `price_of` itself returns an `Option`, so its caller decides what a missing price means. `label` decides: it prints "not sold here".
4. **`missing.or_else(default: 0)`.** The short form when a default is right: the value inside `Some`, or the default for `None`.
5. **`"3".to_int()` and `catalog.at(index: 5)`.** Two more functions that return an `Option`: a text that may not be a number, and a position that may be past the end.
:::

`una run .` prints:

```text include="steps/01-option/expected/output.txt"
DESK-02: 15900 cents
CHAIR-09: not sold here
None or 0
Some(3) and None
```

An `Option` interpolates as `Some(3)` or `None`, which helps when you debug, but a report should say what the absence means, as `label` does.

### How an `Option` behaves

#### A `when` covers both cases

A `when` over an `Option` must have an arm for `Some` and one for `None`, or an `else`. Leave one out, and the checker names the variant that has no arm: [a `when` that forgets `None`](/learn/collections/#a-when-that-forgets-none-u2007) shows the message. When the day comes that a value is missing, the program already says what to do.

#### Options compare by what they hold

```una include="steps/03-option-forms/src/counts.una#L43" title="steps/03-option-forms/src/counts.una"
  @console.print("{counted == Some(14)} {missing == None}")
```

```text include="steps/03-option-forms/expected/output.txt#L7"
true true
```

`Some(14) == Some(14)` holds, and `None == None` holds. `Some(0)` and `None` differ: a count of zero is a count, and a missing count is not.

#### The default of `or_else` is computed first

> [!NOTE]
> The default of `or_else` is an argument like any other, so it is computed before the call, whether it is used or not. Keep it a plain value, such as `0` or `"other"`. A call that has effects, such as one that asks a service, cannot be the default: bind its result with `let` first.

### Choosing how to use an `Option`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Do different things when the value is there and when it is not | `when` with `is Some(v)` and `is None` |
| Work only on the value, with one answer for the rest | `when` with `is Some(v)` and `else` |
| Carry on with a default | `or_else(default: v)`, or `if none use v` on the line under the call ([chapter 7](/learn/failure/)) |
| Know only whether there is a value | `is_some()`, or `o is None` in a condition |
| Make a missing value a failure of your function | `if none fail V`, in [chapter 7](/learn/failure/) |
:::

Prefer a `when` when the absence needs its own words, as on a product page. Prefer `or_else` when the default is the honest answer, as 0 units for a category with no sales.

### Check yourself: `Option`

The three functions of [How to write and use an `Option`](#how-to-write-and-use-an-option) get one more set of counts:

```una include="steps/03-option-forms/src/counts.una#L48" title="steps/03-option-forms/src/counts.una"
  @console.print("{shown(Some(0))} / {to_order(Some(12))} / {well_stocked(Some(10))}")
```

What does the line print?

:::answer Show the answer
```text include="steps/03-option-forms/expected/output.txt#L9"
0 on the shelf / 0 / false
```

`Some(0)` is a count of zero, not a missing count, so `shown` takes the `Some` arm. `to_order(Some(12))` is 12 − 12 = 0. `well_stocked(Some(10))` takes the `Some` arm, and 10 > 10 is `false`.
:::

## 7.2 Declaring a failure: `fails` and `fail`


### What a failure is

A **failure** is a function's way of saying "I could not do this, and here is why", instead of giving a value. Think of a card terminal at a till. Most of the time it says "approved". Sometimes it prints a slip that says "declined", or "card expired in March". The slip is not a price, and nobody mistakes it for one; it says what went wrong, with what the cashier needs to act on it.

In Una a failure is a value too, of a kind you declare. A few words name the parts, and the rest of this chapter uses them:

- An **error kind** is a sum kind ([chapter 4](/learn/kinds/#s4-2)) whose variants are the ways a function can fail: `NotANumber`, `TooSmall`, `TooLarge`. A variant may carry data, such as the text that was not a number.
- `fails QuantityError`, a line of a function's header, says that the function can fail, and with which kind. A **header** is the line with the function's name, parameters and result type, and the lines under it up to `=` ([chapter 6](/learn/functions/#s6-2)).
- `fail TooSmall(value: n)` ends the function with that variant, instead of a value.
- The function's **caller**, the code that called it, must then say what to do with a failure: carry on, pass it on, or turn it into its own. [Section 7.3](#s7-3) shows how.

### Why a function declares its failures

Take the quantity a customer types into an order form. It must be a whole number from 1 to 99. Without a way to fail, a function that reads it must still give back a number, so it gives 0 for anything it cannot use:

```una include="steps/04-sentinel/src/quantity.una" title="steps/04-sentinel/src/quantity.una" verified="check, run"
module quantity

--- The quantity typed into an order form: a whole number from 1 to 99. Any other text gives
--- 0, so the caller cannot tell a bad quantity from what went wrong with it.
quantity_or_zero(raw: Text) -> Int
=
  let n = raw.trim.to_int().or_else(default: 0)
  if n < 1 or n > 99 then 0 else n

pub main() -> Unit
  uses @console: Console[print]
=
  for raw in ["3", "three", "0", "500"]
    let units = quantity_or_zero(raw)
    @console.print("'{raw}': {units} units, {units * 1990} cents")
```

`una run .` prints:

```text include="steps/04-sentinel/expected/output.txt"
'3': 3 units, 5970 cents
'three': 0 units, 0 cents
'0': 0 units, 0 cents
'500': 0 units, 0 cents
```

The program runs, and three different problems come out the same way: a word, a zero, and a number too large all become "0 units, 0 cents". The caller cannot tell them apart, so it cannot tell the customer what to fix. Worse, 0 looks like a quantity, so code that forgets to check for it prices an empty order and carries on. A value used to mean "no value", such as this 0, is called a **sentinel**, and nothing in the type tells a caller to check for it.

A declared failure fixes both problems. The header says that the function can fail and with which kind, so a reader sees it without reading the body. Each way to fail is a variant of its own, with the data a message needs. And the checker refuses a call that does not say what to do when the function fails.

### Each step is a package

Each step of this chapter is a package, as in [chapter 1](/learn/hello/#s1-1): a directory with `una.toml`, `verification.lock` and the module under `src/`. The manifest names the package and the module that `una run` starts:

```toml include="steps/05-quantity/una.toml" title="steps/05-quantity/una.toml"
[package]
name = "quantity"
version = "0.1.0"
edition = "0.2"

[run]
entry = "quantity"
grants = ["console"]
```

`verification.lock` pins the solver and is the same in every example: copy it from chapter 1, or take the step's package, whole, from the chapter's download, `06-failure.tar.gz`. Then, in the package's directory:

```sh
una check .
una run .
```

### A function that fails: `parse_quantity`

Here is the quantity again, with a failure. The module declares the error kind, a function that fails with it, and a `main` that calls the function twice, once with good input and once with bad:

:::steps
```una include="steps/05-quantity/src/quantity.una" title="steps/05-quantity/src/quantity.una" verified="check, run"
module quantity

--- Why a quantity was rejected. Each variant carries what the user needs to fix it.
kind QuantityError = NotANumber(raw: Text) | TooSmall(value: Int) | TooLarge(value: Int)

--- The quantity typed into an order form: a whole number from 1 to 99.
parse_quantity(raw: Text) -> Int
  fails QuantityError
=
  let n = raw.trim.to_int()
    if none fail NotANumber(raw)
  if n < 1
    fail TooSmall(value: n)
  else if n > 99
    fail TooLarge(value: n)
  else
    n

pub main() -> Unit
  uses @console: Console[print]
=
  let typed = parse_quantity(" 3 ")
    if error use 0
  let spelled = parse_quantity("three")
    if error use 0
  @console.print("{typed} and {spelled}")
```

1. **`kind QuantityError = …`.** An error kind is a sum kind like any other. Name the variants after what went wrong, not after where: `NotANumber`, not `ReaderFailed`.
2. **`fails QuantityError`.** This header line says that `parse_quantity` can fail, and with which kind. A function declares at most one error kind.
3. **`raw.trim.to_int()` then `if none fail NotANumber(raw)`.** `to_int` returns an `Option[Int]` ([chapter 7](#s7-1)): `None` when the text is not a number. The clause on the next line turns `None` into a failure of this function. After it, `n` is a plain `Int`.
4. **`fail TooSmall(value: n)`.** This ends the function with that variant. `fail` can stand in any branch, and the other branches give the value.
5. **`if error use 0`.** In `main`, each call is followed by a handling clause, on its own line, indented under the call. Here it recovers with `0`. [Section 7.3](#s7-3) shows the others.
:::

`una run .` prints:

```text include="steps/05-quantity/expected/output.txt"
3 and 0
```

The first call returns `3`. The second fails with `NotANumber`, and its clause recovers with `0`. Here `main` chose 0 on purpose, at the call, where a reader sees it: the function itself no longer hides the failure.

### How to write an error kind and `fail`

The step of this part is a card payment, with each form of an error kind and of `fail`:

```una include="steps/06-fail-forms/src/payment.una#ServiceError..refuse" title="steps/06-fail-forms/src/payment.una"
--- How the payment service can fail. A kind with one variant starts with `|`.
kind ServiceError = | Timeout

--- Why a card payment was refused. Variants with data and without data can mix.
kind PaymentError = Declined | Expired(month: Int) | OverLimit(limit: Int, asked: Int)

--- The amount charged: `fail` in one branch of an `if`, the value in the other.
charge(cents: Int, limit: Int) -> Int
  fails PaymentError
=
  if cents > limit
    fail OverLimit(limit: limit, asked: cents)
  else
    cents

--- The month a card expires, if it is not before `today`: a variant with one field.
valid_until(month: Int, today: Int) -> Int
  fails PaymentError
=
  if month < today
    fail Expired(month)
  else
    month

--- A payment service that is always down: `fail` as the whole body.
always_down(cents: Int) -> Int
  fails ServiceError
=
  fail Timeout

--- A refusal with no detail: a variant without data.
refuse(cents: Int) -> Int
  fails PaymentError
=
  fail Declined
```

#### An error kind

An error kind is declared like any sum kind, with `kind`, a name, `=` and its variants separated by `|`:

- A variant may carry no data, as `Declined`, when the name says everything.
- A variant may carry fields, as `Expired(month: Int)` and `OverLimit(limit: Int, asked: Int)`, when a message or a retry needs them.
- A kind with one variant starts with `|`: `kind ServiceError = | Timeout`. The grammar requires it, so that the line reads as a sum kind with one variant.

#### `fails` in the header

`fails PaymentError` goes on its own line under the header line, indented two spaces, before `=`, next to any `requires` or `uses` line. A function names one error kind at most: every way it can fail is a variant of that kind.

#### `fail` in a branch

`charge` fails in the `if` branch and gives a value in the `else` branch:

```una include="steps/06-fail-forms/src/payment.una#charge" title="steps/06-fail-forms/src/payment.una"
--- The amount charged: `fail` in one branch of an `if`, the value in the other.
charge(cents: Int, limit: Int) -> Int
  fails PaymentError
=
  if cents > limit
    fail OverLimit(limit: limit, asked: cents)
  else
    cents
```

`fail OverLimit(limit: limit, asked: cents)` names the variant and gives each field by its label. When a variant has one field, its value may be given without the label, as `fail Expired(month)` in `valid_until` does. And a bare name that equals a field's name counts as that field's label, so [section 7.3](#s7-3)'s `BadShelf(shelf, cause: error)` is `BadShelf(shelf: shelf, cause: error)`.

#### `fail` as the whole body

A function that always fails, such as a stand-in for a service that is down, has `fail` as its whole body, on its own line after `=`:

```una include="steps/06-fail-forms/src/payment.una#always_down" title="steps/06-fail-forms/src/payment.una"
--- A payment service that is always down: `fail` as the whole body.
always_down(cents: Int) -> Int
  fails ServiceError
=
  fail Timeout
```

#### Failing on a missing value: `if none fail`

`if none fail NotANumber(raw)`, in `parse_quantity`, is the short way to fail when a value is missing: it stands on the line under a call that gives an `Option`. [Section 7.3](#s7-3) covers it with the other clauses.

#### The forms, run

`main` calls each function once with a value that works and once with one that fails, and recovers from every failure with `0`:

```una include="steps/06-fail-forms/src/payment.una#L39-L54" title="steps/06-fail-forms/src/payment.una"
pub main() -> Unit
  uses @console: Console[print]
=
  let paid = charge(4500, limit: 10000)
    if error use 0
  let refused = charge(24000, limit: 10000)
    if error use 0
  let until = valid_until(11, today: 10)
    if error use 0
  let expired = valid_until(3, today: 10)
    if error use 0
  let offline = always_down(4500)
    if error use 0
  let declined = refuse(4500)
    if error use 0
  @console.print("{paid} {refused} {until} {expired} {offline} {declined}")
```

```text include="steps/06-fail-forms/expected/output.txt#L1"
4500 0 11 0 0 0
```

`charge` gives 4500 under the limit and fails over it; `valid_until` gives 11 for a card that expires next month and fails for one that expired in March; the last two always fail.

### How a failure behaves

#### `fail` ends the function

`fail` ends the function at once, as giving a value does: no line after it runs, and the function gives no value. The caller's clause decides what happens next.

#### A function has one error kind

A function declares at most one kind in `fails`, and every `fail` in it must name a variant of that kind. To fail with a variant of another kind is U3009 ([failing with a variant of another kind](#failing-with-a-variant-of-another-kind-u3009)). When a function calls another that fails with a different kind, it translates the failure into its own, with `if error fail` ([section 7.3](#s7-3)).

#### Every call that can fail is handled

A call of a function that can fail must be followed by a clause that handles the failure, or be wrapped in `attempt` ([section 7.4](#s7-4)). Without one, the checker reports U3007 ([forgetting the clause](#forgetting-the-clause-u3007)). Nothing passes a failure on unless a line says so.

#### Public functions declare; private ones may infer

A `pub` function, one that other modules can call ([chapter 6](/learn/functions/#s6-3)), must declare `fails` when it can fail: its header is the module's reviewed promise, and a `fail` in a `pub` function without `fails` is U3009 ([a public function that fails without saying so](#a-public-function-that-fails-without-saying-so-u3009)). A private function may leave the line out, and the checker infers it.

`parse_quantity` is private. Remove its `fails` line:

```diff include="steps/05-quantity..steps/07-inferred:src/quantity.una" context="1" title="src/quantity.una"
--- a/src/quantity.una
+++ b/src/quantity.una
@@ -7,3 +7,2 @@
 parse_quantity(raw: Text) -> Int
-  fails QuantityError
 =
```

The program checks and prints the same thing, and `una contract` prints the header the checker inferred, marked with the comment `-- inferred`:

```text include="steps/07-inferred/expected/commands/contract.txt"
$ una contract quantity.parse_quantity
--- The quantity typed into an order form: a whole number from 1 to 99.
parse_quantity(raw: Text) -> Int
  fails QuantityError -- inferred
```

So a private function without `fails` can still fail. Its contract is the inferred header. Write the line anyway whenever the failure is part of what a caller should know.

#### What is not a failure

Some problems never reach the program as failures, because they are ruled out before it runs. A division by zero, or a call that breaks a function's `requires`, is a proof obligation that the verifier must prove ([chapter 5](/learn/contracts/)): a program with one it cannot prove does not run. A few problems outside the program's logic, such as running out of memory, stop the run instead; [Reference](#reference) lists them.

### Failing as the function you are given: `fails of`

#### What `fails of` is

A function may take another function as a parameter, as `map` takes the function it applies ([chapter 10](/learn/collections/#s10-2), [chapter 10](/learn/collections/#s10-3)). Then whether it can fail depends on what it is given. Think of a cashier who rings up a cart with whatever price list the manager hands over: with the regular list, a SKU missing from it stops the sale; with a sale sign that prices everything at 5.00, nothing can go wrong. `fails of price`, a line of the header, says exactly that: this function fails when, and only when, its parameter `price` fails, and with the same kind.

#### Why a parameter's failures need a clause

The step of this part prices a cart with one of two price functions. `listed` knows two SKUs and fails with `NoPrice` for any other; `flat` prices everything at 500 and never fails:

```una include="steps/08-fails-of/src/pricing.una#PriceError" title="steps/08-fails-of/src/pricing.una"
--- Why a price list has no price for a SKU.
kind PriceError = | NoPrice(sku: Text)
```

```una include="steps/08-fails-of/src/pricing.una#listed..flat" title="steps/08-fails-of/src/pricing.una"
--- The store's price list. It knows two SKUs, and fails for any other.
listed(sku: Text) -> Int
  fails PriceError
=
  if sku == "LAMP-01"
    1990
  else if sku == "DESK-02"
    15900
  else
    fail NoPrice(sku)

--- A flat price for every SKU, during a sale. It never fails.
flat(sku: Text) -> Int = 500
```

A parameter of a function type such as `fn(Text) -> Int` is a function that gives an `Int` and cannot fail. Here is a `pub` function that totals a cart with a price function, without `fails of`, called with a price list that fails for an unknown SKU:

```diff include="steps/08-fails-of..steps/09-no-fails-of:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -8,3 +8,2 @@
 pub total_with(skus: List[Text], price: fn(Text) -> Int) -> Int
-  fails of price
 =
```

`una check .` reports, once for each call that passes `listed`:

```text include="steps/09-no-fails-of/expected/rendered.txt#L1-L8"
[U3009] Error: this function can fail with `PriceError`, which the expected function type does not allow
    ╭─[ src/pricing.una:34:57 ]
    │
 34 │   let known = total_with(["LAMP-01", "DESK-02"], price: listed)
    │                                                         ───┬──
    │                                                            ╰──── this function can fail with `PriceError`, which the expected function type does not allow
    │
    │ Note: run `una explain U3009` for an explanation
```

The mark points at the argument, `listed`. The message says that `listed` can fail with `PriceError`, and that the type of the parameter, `fn(Text) -> Int`, allows no failure. Writing `fails PriceError` on `total_with` would not help: the parameter's type would still allow no failure, and every call would need a clause, even with a price function that never fails.

#### How to write `fails of`

`fails of p` goes under the header, as `fails` does, and names a parameter `p` whose type is a function type written without `fails`. In the body, a call of `p` that can fail takes a clause, and `if error pass` hands its failure on:

```una include="steps/08-fails-of/src/pricing.una#total_with" title="steps/08-fails-of/src/pricing.una"
--- The total of a cart, with each SKU priced by `price`. It fails when, and only when,
--- `price` fails, and with the same error kind.
pub total_with(skus: List[Text], price: fn(Text) -> Int) -> Int
  fails of price
=
  let edit total = 0
  for sku in skus
    let cents = price(sku)
      if error pass
    total = total + cents
  total
```

At each call of `total_with`, the failure is that of the argument. `listed` fails with `PriceError`, so a call with `listed` needs a clause; `flat` and the lambda cannot fail, so a call with them needs none:

```una include="steps/08-fails-of/src/pricing.una#L35-L39" title="steps/08-fails-of/src/pricing.una"
  let known = total_with(["LAMP-01", "DESK-02"], price: listed)
    if error use -1
  let flat_total = total_with(["LAMP-01", "VASE-03"], price: flat)
  let lambda_total = total_with(["LAMP-01"], price: fn(sku) -> sku.len * 100)
  @console.print("{known} {flat_total} {lambda_total}")
```

```text include="steps/08-fails-of/expected/output.txt#L1"
17890 1000 700
```

The lambda prices each SKU at 100 cents per character of its code, so `LAMP-01` costs 700.

#### How `fails of` behaves

- `fails of p` exists from edition `0.2` on. Its twin for capabilities, `uses of p`, is taught in [section 12.4](/learn/capabilities/#s12-4), with what else a parameter named by these clauses may and may not do.
- `fails E` and `fails of p` can both appear in one header. When both are there, the argument for `p` must fail with `E` (U3009 at the argument), so that the function keeps one error kind.
- A private function may leave `fails of p` out, and the checker infers it when the body only passes on the failures of `p`, as it infers `fails` ([Public functions declare; private ones may infer](#public-functions-declare-private-ones-may-infer)). That is why `total_with` is `pub` here: the line is what its callers rely on.
- In edition `0.2`, `map`, `filter`, `fold` and `first_where` declare `fails of` their function parameter, so they accept a function that fails, and stop at its first failure.

### A sentinel, an `Option` or a failure

:::decide
**Which to use:**

| When the function cannot give a normal answer… | Use |
| --- | --- |
| Never | a sentinel value such as 0 or -1, which a caller can mistake for an answer |
| And "no answer" is a normal outcome, with nothing more to say | an `Option` ([chapter 7](#s7-1)) |
| And the caller needs to know why, to act on it | `fails` with an error kind |
:::

A price lookup for a SKU the catalog does not sell gives `None`: that is a normal answer. A quantity typed as `"three"` is a failure with a reason, `NotANumber`, which a form shows to the customer.

### Check yourself: failures

Both calls fail. Predict the line:

```una include="steps/06-fail-forms/src/payment.una#L55-L59" title="steps/06-fail-forms/src/payment.una"
  let over = charge(30000, limit: 10000)
    if error use -1
  let lapsed = valid_until(3, today: 10)
    if error use 99
  @console.print("{over} {lapsed}")
```

:::answer Show the answer
```text include="steps/06-fail-forms/expected/output.txt#L2"
-1 99
```

30000 is over the limit, so `charge` runs `fail OverLimit(…)`: the function ends there and gives no value, and the clause under the call gives `-1` instead. The card expired in month 3, before month 10, so `valid_until` fails with `Expired`, and its own clause gives `99`. Each call's clause decides what a failure becomes at that call.
:::

And one about `fails of`. `VASE-03` is not in the price list:

```una include="steps/08-fails-of/src/pricing.una#L40-L42" title="steps/08-fails-of/src/pricing.una"
  let unknown = total_with(["LAMP-01", "VASE-03"], price: listed)
    if error use -1
  @console.print("{unknown}")
```

What does it print?

:::answer Show the answer
```text include="steps/08-fails-of/expected/output.txt#L2"
-1
```

`total_with` declares `fails of price`, so with `listed` it fails as `listed` does: the loop reaches `VASE-03`, `listed` fails with `NoPrice`, and `if error pass` hands that failure on. So the call fails, and the clause under it gives `-1`. The total of `LAMP-01` alone is never returned.
:::

## 7.3 Handling a failure: the clauses


### What a handling clause is

A **handling clause** is a line under a call that says what to do if the call fails. Think of the instructions a store leaves for a clerk: "if the lamp is out of stock, offer the next model", "if the card is declined, call the manager". The instruction sits next to the task it belongs to, and nobody has to guess.

A clause stands on its own line, indented one level under the statement it handles. Una has five, in two families:

- `if error …` handles a call that **fails**: `if error use`, `if error pass` and `if error fail`.
- `if none …` handles a value that is **missing**, an `Option` that is `None` ([chapter 7](#s7-1)): `if none use` and `if none fail`.

The word after `if error` or `if none` is the decision: **use** a value and carry on, **pass** the failure on to your own caller, or **fail** with a variant of your own.

### Why every call needs one

Una passes no failure on by itself. A call that can fail with no clause under it does not check. Leave out the clause under `read_count`:

```diff include="steps/10-clauses..steps/11-no-clause:src/shelves.una" context="1" title="src/shelves.una"
--- a/src/shelves.una
+++ b/src/shelves.una
@@ -20,3 +20,2 @@
   let units = read_count(raw)
-    if error use 0
   units
```

`una check .` reports:

```text include="steps/11-no-clause/expected/rendered.txt"
[U3007] Error: `read_count` can fail with `CountError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
    ╭─[ src/shelves.una:20:15 ]
    │
 20 │   let units = read_count(raw)
    │               ───────┬───────
    │                      ╰───────── `read_count` can fail with `CountError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
    │
    │ Note: run `una explain U3007` for an explanation
────╯
```

The message names the call, `read_count`, and the kind it can fail with, `CountError`. The mark covers the call. The end of the message gives the two ways out: an `if error` clause under the call, or `attempt`, which keeps the outcome as a value ([section 7.4](#s7-4)). Una does not choose for you, because only you know whether a count that cannot be read should be 0, a failure of your own, or something to report.

### How to write the clauses

| Clause | Use it when | After it |
| --- | --- | --- |
| `if error use v` | You can carry on with a sensible value | The statement's value is `v` on failure; `error` can be used in `v` |
| `if error pass` | Your function fails with the *same* kind, and the caller should decide | The failure goes to your caller unchanged |
| `if error fail V(...)` | Your function fails with a *different* kind: translate it | Your function fails with `V`; inside `V(...)`, `error` is the original failure |
| `if none use v` | The statement gives an `Option`, and `None` has a sensible default | The value is unwrapped, or `v` |
| `if none fail V(...)` | `None` means the input is wrong | The value is unwrapped, or your function fails with `V` |

The step of this part has one function per clause, around a shelf count that a clerk types:

```una include="steps/10-clauses/src/shelves.una#CountError..read_count" title="steps/10-clauses/src/shelves.una"
--- Why a shelf count could not be used.
kind CountError = NotCounted(shelf: Text) | Unreadable(raw: Text)

--- Why a shelf audit failed: the shelf, and the count's own failure as its cause.
kind AuditError = | BadShelf(shelf: Text, cause: CountError)

--- The units a clerk typed for a shelf. `if none fail`: a text that is not a number fails.
read_count(raw: Text) -> Int
  fails CountError
=
  let units = raw.trim.to_int()
    if none fail Unreadable(raw)
  units
```

#### Fail on a missing value: `if none fail`

`read_count` turns a text into a count. `to_int` gives `None` for a text that is not a number, and `if none fail Unreadable(raw)` turns that `None` into a failure of `read_count`. After the clause, `units` is a plain `Int`: the clause has dealt with the other case.

#### Carry on with a value: `if error use`

```una include="steps/10-clauses/src/shelves.una#count_or_zero" title="steps/10-clauses/src/shelves.una"
--- `if error use`: carry on with 0 when the count cannot be read.
count_or_zero(raw: Text) -> Int
=
  let units = read_count(raw)
    if error use 0
  units
```

When `read_count` fails, `units` is 0, and the function goes on. `count_or_zero` cannot fail itself: the clause has handled every failure.

#### Pass it on: `if error pass`

```una include="steps/10-clauses/src/shelves.una#count_label" title="steps/10-clauses/src/shelves.una"
--- `if error pass`: the same kind, `CountError`, so the failure goes to the caller as it is.
count_label(raw: Text) -> Text
  fails CountError
=
  let units = read_count(raw)
    if error pass
  "{units} units"
```

`count_label` fails with `CountError`, the same kind as `read_count`, so `if error pass` hands the failure to `count_label`'s caller as it is. Use it when the caller knows better what a failure means.

#### Use the failure in the value: `error`

```una include="steps/10-clauses/src/shelves.una#shown" title="steps/10-clauses/src/shelves.una"
--- `if error use`, with `error` in the value: a failure becomes a sentence.
shown(raw: Text) -> Text
=
  let text = count_label(raw)
    if error use explain(error)
  text
```

Inside a clause, the name `error` holds the failure that happened, here a `CountError`. `if error use explain(error)` turns it into a sentence. `explain` is an ordinary function with a `when` over the variants, declared in the same module:

```una include="steps/10-clauses/src/shelves.una#explain" title="steps/10-clauses/src/shelves.una"
--- What a person reads about a count that could not be used.
explain(failure: CountError) -> Text
=
  when failure
    is NotCounted(shelf) -> "shelf {shelf} was not counted"
    is Unreadable(raw) -> "'{raw}' is not a count"
```

#### Translate it: `if error fail`

```una include="steps/10-clauses/src/shelves.una#audit" title="steps/10-clauses/src/shelves.una"
--- `if error fail`: a `CountError` becomes an `AuditError` that names the shelf.
audit(shelf: Text, raw: Text) -> Int
  fails AuditError
=
  read_count(raw)
    if error fail BadShelf(shelf, cause: error)
```

`audit` fails with `AuditError`, another kind, so it cannot pass a `CountError` on. `if error fail BadShelf(shelf, cause: error)` fails with its own variant instead, and keeps the original failure in the field `cause`, so nothing is lost. The clause here stands under the function's last line, the call whose value the function gives: a clause may follow any statement that can fail, not only a `let`.

#### Carry on when a value is missing: `if none use`

```una include="steps/10-clauses/src/shelves.una#counted..required" title="steps/10-clauses/src/shelves.una"
--- `if none use`: a shelf missing from the counts counts as 0.
counted(counts: Map[Text, Int], shelf: Text) -> Int
=
  let units = counts.get(key: shelf)
    if none use 0
  units

--- `if none fail`: a shelf missing from the counts is a failure.
required(counts: Map[Text, Int], shelf: Text) -> Int
  fails CountError
=
  let units = counts.get(key: shelf)
    if none fail NotCounted(shelf)
  units
```

A map's `get` gives an `Option`. `counted` treats a missing shelf as 0 units with `if none use 0`, and `required` treats it as a failure with `if none fail NotCounted(shelf)`.

#### The clauses, run

`main` calls each function. To print what `audit` failed with, it uses `attempt`, which keeps a failure as a value that can be printed, `Err(…)`; [section 7.4](#s7-4) explains it.

```una include="steps/10-clauses/src/shelves.una#L71-L83" title="steps/10-clauses/src/shelves.una"
  let typed = count_or_zero(" 7 ")
  let spelled = count_or_zero("seven")
  let three = shown("3")
  let cross = shown("x")
  @console.print("{typed} {spelled} / {three} / {cross}")
  let audited = attempt audit("A-12", raw: "seven")
  @console.print("{audited}")
  let counts = empty_map().with(key: "A-12", value: 7)
  let missing = required(counts, shelf: "B-03")
    if error use -1
  let found = counted(counts, shelf: "A-12")
  let absent = counted(counts, shelf: "B-03")
  @console.print("{found} {absent} {missing}")
```

```text include="steps/10-clauses/expected/output.txt#L1-L3"
7 0 / 3 units / 'x' is not a count
Err(BadShelf(shelf: "A-12", cause: Unreadable("seven")))
7 0 -1
```

The second line shows translation at work: the `AuditError` names the shelf, and its `cause` keeps the `CountError` that started it.

### Translating between layers with `error`

Most programs have layers: a low-level parser, a line reader above it, a batch report above that. Each layer has its own error kind, because each layer knows different things. The quantity parser knows the text was not a number, and the line reader also knows the line number. `if error fail` translates, and `error` keeps the original failure as a payload, so nothing is lost. This step uses a smaller `QuantityError` than [section 7.2](#s7-2), with one variant for both bounds, which is enough here:

:::steps
```una include="steps/12-translate/src/upload.una" title="steps/12-translate/src/upload.una" verified="check, run"
module upload

kind QuantityError = NotANumber(raw: Text) | OutOfRange(value: Int)

--- Why a line of an uploaded file was rejected, with its line number.
kind LineError = MissingQuantity(line: Int) | BadQuantity(line: Int, cause: QuantityError)

parse_quantity(raw: Text) -> Int
  fails QuantityError
=
  let n = raw.trim.to_int()
    if none fail NotANumber(raw)
  if n < 1 or n > 99
    fail OutOfRange(value: n)
  else
    n

--- The quantity on line `number` of an upload, `"SKU, quantity"`.
quantity_on_line(number: Int, text: Text) -> Int
  fails LineError
=
  let raw = text.split(on: ",").at(index: 1)
    if none fail MissingQuantity(line: number)
  parse_quantity(raw)
    if error fail BadQuantity(line: number, cause: error)

explain(failure: LineError) -> Text
=
  when failure
    is MissingQuantity(line) -> "line {line}: no quantity"
    is BadQuantity(line, cause) -> "line {line}: {cause_text(cause)}"

cause_text(cause: QuantityError) -> Text
=
  when cause
    is NotANumber(raw) -> "'{raw.trim}' is not a number"
    is OutOfRange(value) -> "{value} is not between 1 and 99"

show(number: Int, text: Text) -> Text
=
  let outcome = attempt quantity_on_line(number, text: text)
  when outcome
    is Ok(value) -> "line {number}: {value} units"
    is Err(failure) -> explain(failure)

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(show(1, text: "LAMP-01, 2"))
  @console.print(show(2, text: "LAMP-01"))
  @console.print(show(3, text: "LAMP-01, lots"))
  @console.print(show(4, text: "LAMP-01, 500"))
```

`una run .` prints:

```text include="steps/12-translate/expected/output.txt"
line 1: 2 units
line 2: no quantity
line 3: 'lots' is not a number
line 4: 500 is not between 1 and 99
```

Walkthrough:

1. **`if none fail MissingQuantity(line: number)`.** `at(index: 1)` gives `None` when the line has no comma. That is the input's fault, so it becomes a failure.
2. **`if error fail BadQuantity(line: number, cause: error)`.** This is translation. `quantity_on_line` fails with `LineError`, and `parse_quantity` fails with `QuantityError`, so `if error pass` would not be allowed ([Passing a failure of another kind](#passing-a-failure-of-another-kind-u3008) shows the diagnostic). `error` is the `QuantityError` that occurred, and it is kept as the `cause`.
3. **`explain` and `cause_text`.** Turning a failure into a message is an ordinary `when`. Because `when` must cover every variant, adding a variant to `LineError` later makes the checker point at every message function that needs a new arm.
4. **`attempt quantity_on_line(number, text: text)` in `show`.** `attempt` keeps the outcome as a value, `Ok(value)` or `Err(failure)`, so `show` can print a message for either. [Section 7.4](#s7-4) explains it.
:::

### How the clauses behave

#### Each clause on its own line, in order

A clause goes on its own line, indented one level under the statement. Written on the same line, it is U0101 ([the clause on the same line](#the-clause-on-the-same-line-u0101)). A statement takes each clause at most once, and when it has both families, `if error` comes first and `if none` second: the call's failure is decided before the value it gave. The other order is U0102 ([`if none` before `if error`](#if-none-before-if-error-u0102)).

#### One call that can fail per statement

A call that can fail must be the whole expression of its statement or `let`, so that its clause handles exactly one call. Nesting it inside another call, as `check_stock(parse_order(line))`, is U3013 ([nesting a call that can fail](#nesting-a-call-that-can-fail-u3013)): bind the inner call with `let` first, with its own clause.

#### What each clause requires

- `use v`: `v` has the type of the statement's value, since it takes the value's place. A value of another type, such as a text where an `Order` goes, is U2001: the message names the type expected and the type found.
- `pass`: the call fails with the same kind as your function. Another kind is U3008 ([passing a failure of another kind](#passing-a-failure-of-another-kind-u3008)).
- `fail V(...)`: `V` is a variant of your function's kind, as for any `fail`.
- `error` is a name only inside an `if error` clause, where it holds the failure.

#### A clause on a call that cannot fail

In editions `0.1` and `0.2`, an `if error` clause under a call that cannot fail is accepted, and never runs. In edition `0.3`, it is U3025, and `una fix` deletes it.

### Choosing a clause

:::decide
**Which to use:**

| The failure, or the missing value… | Use |
| --- | --- |
| Has a sensible value to carry on with | `if error use v` / `if none use v` |
| Is for your caller to decide, and your function fails with the same kind | `if error pass` |
| Needs your own terms, or your layer adds what it knows | `if error fail V(cause: error)` |
| Means the input is wrong | `if none fail V` |
| Must be kept to decide later, counted or retried | `attempt` ([section 7.4](#s7-4)) |
:::

Prefer `fail` with your own variant over `use` with a value that only looks like an answer: a sentinel such as 0 is what [section 7.2](#s7-2) set out to avoid. Use `use` when the value is honest, such as 0 units on a shelf nobody counted, or a price page that says "ask for a price".

### Check yourself: handling clauses

`shown` passes through `count_label`, and `count_or_zero` recovers with 0. Predict the line:

```una include="steps/10-clauses/src/shelves.una#L84-L86" title="steps/10-clauses/src/shelves.una"
  let padded = shown(" 12 ")
  let blank = count_or_zero("")
  @console.print("{padded} / {blank}")
```

:::answer Show the answer
```text include="steps/10-clauses/expected/output.txt#L4"
12 units / 0
```

`read_count` trims the text, so `" 12 "` reads as 12, `count_label` gives `"12 units"`, and `shown` never needs its clause. The empty text is not a number, so `read_count` fails with `Unreadable`, and the clause in `count_or_zero` gives 0.
:::

## 7.4 Failures as values: `attempt` and `Result`


### What `attempt` and `Result` are

The handling clauses of [section 7.3](#s7-3) decide on the spot, at the call. Sometimes you want to *keep* the outcome and decide later. Think of a stack of card payments at the end of the day: each slip says "approved" or "declined, and why". The clerk files every slip and counts them later; one declined card does not stop the pile.

`attempt` turns one call into such a slip. `attempt raw.parse_int()` runs the call and gives a value of the type `Result[T, E]`, a sum kind of the prelude with two variants:

- `Ok(value)` when the call returned, with the value, of the type `T`;
- `Err(failure)` when the call failed, with the failure, of the error kind `E`.

`attempt` itself never fails: a failure becomes an `Err`, which a `when` ([chapter 4](/learn/kinds/#s4-3)) takes apart like any sum kind.

### Why a batch needs failures as values

The examples of this section read quantities with the prelude's own failing function, `parse_int`, which turns a text into an `Int` and fails with `ParseError`, a sum kind of the prelude: `Empty` for an empty text, `NoDigits` for a sign alone, and `NotADigit(at)` with the position of the first wrong character, counted from 0. Unlike `to_int`, it says why a text is not a number. Both exist from edition `0.2` on.

A batch is a list of items processed one after another, such as the quantities typed into an order form. With `if error pass`, the first item that fails ends the whole function, and every later item is lost:

```una include="steps/13-batch-stops/src/batch.una" title="steps/13-batch-stops/src/batch.una" verified="check, run"
module batch

--- The units of every typed quantity, added up. One quantity that is not a number fails the
--- whole batch.
total_units(typed: List[Text]) -> Int
  fails ParseError
=
  let edit total = 0
  for raw in typed
    let units = raw.parse_int()
      if error pass
    total = total + units
  total

pub main() -> Unit
  uses @console: Console[print]
=
  let good = total_units(["12", "3"])
    if error use -1
  let mixed = total_units(["12", "", "3", "3x"])
    if error use -1
  @console.print("{good} and {mixed}")
```

`una run .` prints:

```text include="steps/13-batch-stops/expected/output.txt"
15 and -1
```

The first batch adds up to 15. The second holds two good quantities, 12 and 3, and two bad ones, and the whole batch comes out as -1: the loop stopped at the empty text, the second item, and the caller cannot tell which item failed, or why, or how many were good. `if error use 0` on each item would hide the failures instead. To report every item, the loop must keep each outcome, good or bad, and carry on.

### How to write `attempt`

#### `attempt` and a `let`

The usual form binds the outcome: `let outcome = attempt raw.parse_int()`. `attempt` is followed by exactly one call, of a function or of a capability operation, and no clause goes under it: `attempt` is the handling.

#### `attempt` as the whole body

A function whose body is only `attempt` returns the outcome, and cannot fail itself:

```una include="steps/14-attempt/src/batch.una#parse_typed" title="steps/14-attempt/src/batch.una"
--- A typed quantity as a number, or the reason it is not one. The whole body is `attempt`.
parse_typed(raw: Text) -> Result[Int, ParseError] = attempt raw.parse_int()
```

Its result type is written out: `Result[Int, ParseError]`, the type of `parse_int`'s value and the kind it fails with.

#### Taking a `Result` apart: `when`

```una include="steps/14-attempt/src/batch.una#describe" title="steps/14-attempt/src/batch.una"
--- One line of the report for a typed quantity.
describe(raw: Text, outcome: Result[Int, ParseError]) -> Text
=
  when outcome
    is Ok(value) -> "'{raw}': {value} units"
    is Err(failure) -> "'{raw}': {explain(failure)}"
```

`is Ok(value)` binds the value, and `is Err(failure)` binds the failure. When the arm does not need the failure, write `is Err` alone, as `show` does in [section 7.5](#s7-5).

#### A question about the outcome: `is_ok`

`outcome.is_ok()` is `true` for `Ok` and `false` for `Err`, without taking the outcome apart. It suits a count.

### Reporting every typed quantity

This step checks quantities typed by a person with `parse_int`. It reports every quantity, with the reason `ParseError` gives, and counts the good ones:

:::steps
```una include="steps/14-attempt/src/batch.una#L1-L32" title="steps/14-attempt/src/batch.una"
module batch

--- A typed quantity as a number, or the reason it is not one. The whole body is `attempt`.
parse_typed(raw: Text) -> Result[Int, ParseError] = attempt raw.parse_int()

--- Why a typed quantity is not a whole number, for a person to read.
explain(failure: ParseError) -> Text
=
  when failure
    is Empty -> "nothing was typed"
    is NoDigits -> "a sign with no digits"
    is NotADigit(at) -> "not a digit at position {at}"

--- One line of the report for a typed quantity.
describe(raw: Text, outcome: Result[Int, ParseError]) -> Text
=
  when outcome
    is Ok(value) -> "'{raw}': {value} units"
    is Err(failure) -> "'{raw}': {explain(failure)}"

pub main() -> Unit
  uses @console: Console[print]
=
  let typed = ["12", "", "-", "3x"]
  let edit accepted = 0
  for raw in typed
    let outcome = attempt raw.parse_int()
    @console.print(describe(raw, outcome: outcome))
    if outcome.is_ok()
      accepted = accepted + 1
  let last = parse_typed("7")
  @console.print("{accepted} of {typed.len} accepted, then {last}")
```

1. **`parse_typed(raw: Text) -> Result[Int, ParseError] = attempt raw.parse_int()`.** The whole body is `attempt`, so the function returns the outcome and cannot fail itself.
2. **`explain`.** A `when` turns each variant of `ParseError` into words.
3. **`let outcome = attempt raw.parse_int()`.** The usual form. The loop goes on after a bad quantity, since nothing failed: the failure is a value in `outcome`.
4. **`outcome.is_ok()`.** `is_ok` says whether a `Result` is `Ok`, without taking it apart.
:::

`una run .` prints:

```text include="steps/14-attempt/expected/output.txt#L1-L5"
'12': 12 units
'': nothing was typed
'-': a sign with no digits
'3x': not a digit at position 1
1 of 4 accepted, then Ok(7)
```

Every item gets its line, with its own reason. The last value interpolates as `Ok(7)`: a `Result` is printed like any other value of a sum kind.

### How `attempt` behaves

#### One call, the whole expression

`attempt` applies to the whole expression after it, and that expression must be one call. It is tempting to write `attempt` and a question about the outcome on one line:

```diff include="steps/14-attempt..steps/15-attempt-expression:src/batch.una" context="1" title="src/batch.una"
--- a/src/batch.una
+++ b/src/batch.una
@@ -26,3 +26,3 @@
   for raw in typed
-    let outcome = attempt raw.parse_int()
+    let outcome = attempt raw.parse_int().is_ok()
     @console.print(describe(raw, outcome: outcome))
```

`una check .` reports three errors. The first is the one to read:

```text include="steps/15-attempt-expression/expected/rendered.txt#L1-L8"
[U2001] Error: argument `r` of `is_ok` must be `Result[_, _]`, found `Int`
    ╭─[ src/batch.una:27:27 ]
    │
 27 │     let outcome = attempt raw.parse_int().is_ok()
    │                           ───────┬───────
    │                                  ╰───────── argument `r` of `is_ok` must be `Result[_, _]`, found `Int`
    │
    │ Note: run `una explain U2001` for an explanation
```

`attempt` took the whole of `raw.parse_int().is_ok()`, which is the call `is_ok(raw.parse_int())`. Its argument `r` is the `Int` that `parse_int` gives, not a `Result`, so the types do not match. The other two errors follow from the same line: `parse_int` is now nested inside another call (U3013), and `outcome` has become a `Result` of a `Bool`. The fix is two lines: `let outcome = attempt raw.parse_int()`, then `outcome.is_ok()` where the question is asked.

#### What an `Ok` value keeps

When the outcome is `Ok`, everything the called function promises about its result in its header holds for the value, as after a direct call ([chapter 5](/learn/contracts/#s5-2) shows those promises, `ensures`).

#### A stored failure is not raised again

An `Err(failure)` is a value. `fail` names a variant where a failure is decided, so `fail failure` with a stored failure does not check ([re-raising a stored failure](#re-raising-a-stored-failure-u0101)). To pass a failure on, handle the call with `if error pass` and do not `attempt` it.

#### `attempt` of a call that cannot fail

In editions `0.1` and `0.2`, `attempt` of a call that cannot fail is accepted. In edition `0.3`, it is U3026: remove the `attempt` and use the value directly.

### Choosing how to handle a failure

The table compares the handling clauses, `attempt`, and `checked`, which [section 7.5](#s7-5) introduces:

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Carry on with a default | `if error use` / `if none use` |
| Let the caller decide, same error kind | `if error pass` |
| Report the failure in your own terms | `if error fail V(cause: error)` |
| Keep going and collect outcomes, retry, or count failures | `attempt`, then `when` |
| Accept outside input that no proof can establish | `checked` ([section 7.5](#s7-5)) |
:::

### Check yourself: `attempt`

`parse_int` does not trim spaces. Predict what this prints:

```una include="steps/14-attempt/src/batch.una#L33-L34" title="steps/14-attempt/src/batch.una"
  let padded = parse_typed(" 5")
  @console.print("{padded}")
```

:::answer Show the answer
```text include="steps/14-attempt/expected/output.txt#L6"
Err(NotADigit(0))
```

The space at position 0 is not a digit, so `parse_int` fails with `NotADigit(at: 0)`. `parse_typed` is an `attempt`, so the failure comes back as a value, `Err(…)`, and nothing fails: the program prints it and goes on.
:::

## 7.5 When no proof can decide: `checked` and opaque predicates


### What `checked` is

Before a program runs, Una's **verifier** proves facts about it: that a division never divides by zero, that a call meets the conditions its function states ([chapter 5](/learn/contracts/) covers it). Some facts depend on data that arrives only while the program runs, such as the text a person types, and on rules the verifier does not see inside. For those, `checked` tests the fact when the program runs, once, and from then on the value carries the fact in its type.

Think of a ticket check at the door of a hall. Inside, nobody asks again: being inside means the ticket was checked. A value that has passed `checked` is like a guest inside. Its type says that the test passed, and every function that takes that type can rely on it.

### Facts the verifier cannot see

Three constructs of [chapter 5](/learn/contracts/) appear here, briefly:

- `kind Sku = Text where well_formed(it)` is a **refined kind**: a `Text` for which the condition after `where` holds, where `it` stands for the value. A `Text` becomes a `Sku` only where the condition is proven.
- A `predicate` is a named condition. It is either `reflect`, when the verifier may see its body, or `opaque`, when it may not. An opaque predicate may be named in a kind's `where` clause and in the `requires` and `ensures` clauses of a capability operation ([chapter 12](/learn/capabilities/)), which state the fact without testing it. It runs only as the condition of `checked` and in the bodies of other opaque predicates; a call anywhere else is U2016.
- `t.slice(start: 4, end: 5)` is the text from position 4 up to, not including, position 5.

### Why a run-time test is needed

`shelf_label` takes a `Sku`, so it never prints a label for a malformed code. Pass it the text a person typed, and the verifier refuses:

```diff include="steps/16-checked..steps/17-unchecked:src/sku.una" context="1" title="src/sku.una"
--- a/src/sku.una
+++ b/src/sku.una
@@ -19,8 +19,3 @@
 
-show(raw: Text) -> Text
-=
-  let outcome = attempt parse_sku(raw)
-  when outcome
-    is Ok(value) -> shelf_label(value)
-    is Err -> "not a sku: {raw}"
+show(raw: Text) -> Text = shelf_label(raw)
 
```

`una check .` reports:

```text include="steps/17-unchecked/expected/rendered.txt"
[U5001] Error: refinement `well_formed(raw)` is refuted
    ╭─[ src/sku.una:20:39 ]
    │
  7 │ kind Sku = Text where well_formed(it)
    │                       ───────┬───────
    │                              ╰───────── where clause
    │
 20 │ show(raw: Text) -> Text = shelf_label(raw)
    │                                       ─┬─
    │                                        ╰─── refinement `well_formed(raw)` is refuted
    │
    │ Help 1: repair 1: strengthen the type of the parameter `raw` to a refined kind that implies `well_formed(raw)`
    │
    │ Help 2: repair 2: add `requires well_formed(raw)` to the enclosing function; its callers then prove it
    │
    │ Help 3: repair 3: add a guard (`if` or a `when` arm) that handles the values where `well_formed(raw)` does not hold
    │
    │ Help 4: repair 4 (escape: checked; a runtime test replaces the static proof: the program fails at run time where the proof would have rejected it; it counts against [escape_budget] and is listed in the build report): check the value with `checked(value, well_formed(raw)) else fail <Variant>`
    │
    │ Note 1: obligation ob-63f8dbd41c36 (refinement) is refuted: well_formed(raw)
    │
    │ Note 2: counterexample: raw = Text#0
    │
    │ Note 3: run `una explain U5001` for an explanation
────╯
```

Read it from the top. The first line says that the refinement `well_formed(raw)` is refuted: the verifier found a text for which it cannot show the condition. The two marks show the `where` clause that asks for it and the argument that must meet it. `Note 2` is the counterexample, `Text#0`, the verifier's name for some text it knows nothing about: `raw` could be any text. The help lines are the repairs, ranked. The first three need a proof, which no one can give for text typed by a person. The fourth is `checked`.

### How to write `checked`

`checked(value, condition) else fail V` has four parts:

1. **`value`**, the value to test, here `raw.trim`.
2. **`condition`**, written with `it` standing for the value. It is a condition of the refinement language of [chapter 5](/learn/contracts/#s5-3), or a call of an opaque predicate, so that it can run.
3. **`else fail V`**, the variant your function fails with when the test does not hold. It is a `fail` like any other, so `V` belongs to the function's error kind.
4. **The result**, when the test holds: the value, with a type refined by the condition. Returned where a `Sku` is expected, it is a `Sku`.

### A checked SKU parser

The step's module turns outside text into a `Sku` with `checked`, then prints a shelf label for a well-formed SKU and `not a sku: lamp 1` for the bad input:

```una include="steps/16-checked/src/sku.una" title="steps/16-checked/src/sku.una" verified="check, run"
module sku

--- A SKU as the warehouse prints it: seven characters, ending in a dash and two digits, as in `LAMP-01`.
--- The rule is checked when the program runs, so the predicate is opaque to proofs.
predicate opaque well_formed(t: Text) -> Bool = t.len == 7 and t.slice(start: 4, end: 5) == "-" and is_digits(t.slice(start: 5, end: 7))

kind Sku = Text where well_formed(it)

kind SkuError = | NotASku

--- Turns text from the outside into a `Sku`, or fails.
parse_sku(raw: Text) -> Sku
  fails SkuError
=
  checked(raw.trim, well_formed(it)) else fail NotASku

--- The label printed on a shelf. It takes a `Sku`, so it never sees unchecked text.
shelf_label(sku: Sku) -> Text = "sku {sku}"

show(raw: Text) -> Text
=
  let outcome = attempt parse_sku(raw)
  when outcome
    is Ok(value) -> shelf_label(value)
    is Err -> "not a sku: {raw}"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(show("LAMP-01"))
  @console.print(show("lamp 1"))
  @console.print(show(" LAMP-02 "))
  @console.print(show("RUG-07"))
```

`una run .` prints:

```text include="steps/16-checked/expected/output.txt#L1-L2"
sku LAMP-01
not a sku: lamp 1
```

`parse_sku` trims the text, then `checked` tests `well_formed(it)` on it, with `it` standing for the trimmed text. When the test holds, the result has the kind `Sku`; when it does not, `parse_sku` fails with `NotASku`, like any `fail`. `show` keeps the outcome with `attempt` ([section 7.4](#s7-4)), and its `is Err` arm needs no name for the failure, since `SkuError` has one variant.

### The escape budget

> [!WARNING]
> `checked` replaces a proof with a test, so `una.toml` budgets it per module, and `una report .` counts the uses of each module under `escapes`.

```toml include="steps/16-checked/una.toml" title="steps/16-checked/una.toml"
[package]
name = "sku"
version = "0.1.0"
edition = "0.2"

[run]
entry = "sku"
grants = ["console"]

[escape_budget]
checked_per_module = 1
```

The budget is a line of the manifest, so raising it is a change a reviewer sees. `checked_per_module = 1` allows one use in each module. `una report .` lists the use, next to the budget:

```text include="steps/16-checked/expected/commands/report.txt#L2,L10-L11"
package sku 0.1.0
escapes:
  sku: 1 checked, budget 1
```

Without an `[escape_budget]` table the budget is 0. Remove the table, and the first `checked` in a module does not check:

```text include="steps/18-no-budget/expected/rendered.txt#L1,L8-L12"
[U7003] Error: module `sku` uses `checked` 1 time, and `[escape_budget] checked_per_module` allows 0
    │ Help 1: repair 1: state the fact in a refined type or a `requires` clause, so that the solver proves it, and remove the `checked`
    │
    │ Help 2: repair 2: handle the values where the fact does not hold with a guard (`if` or a `when` arm), and remove the `checked`
    │
    │ Help 3: repair 3 (escape: escape_budget; the module may use more runtime tests in place of proofs; each one is listed in the build report and needs review): raise `checked_per_module` in `[escape_budget]` of `una.toml`
```

The message counts the uses and the budget. The first two repairs remove the `checked` in favor of a proof or a guard; only the third raises the budget, and it says what that costs: each use is listed in the report and needs review.

### How `checked` behaves

#### The test runs once

`checked` runs its condition once, when the program reaches it. A value that passed it carries its refined kind, so every function that takes a `Sku` relies on the fact with no second test.

#### Using a checked value

Once `parse_sku` has returned it, a `Sku` can be passed anywhere one is required. `shelf_label` takes a `Sku`, so the only way to call it with outside text is through `parse_sku`. A call with a plain `Text` does not check, as [Why a run-time test is needed](#why-a-run-time-test-is-needed) showed.

#### A failed test is an ordinary failure

When the condition does not hold, the function fails with the variant after `else fail`, and its callers handle that failure with the clauses of [section 7.3](#s7-3), or with `attempt`.

> [!TIP]
> Use `checked` at the edge of the program, once per fact, and prefer a proof ([chapter 5](/learn/contracts/)) wherever the verifier can see the rule.

### A proof, a guard or `checked`

:::decide
**Which to use:**

| The fact… | Use |
| --- | --- |
| Follows from what the code already knows | nothing: the verifier proves it |
| Is the caller's to keep, such as "never 0 months" | `requires` ([chapter 5](/learn/contracts/#s5-1)) |
| Can be tested with a plain condition, and the code can carry on either way | an `if` guard |
| Depends on outside data and a rule the verifier cannot see | `checked` with an opaque predicate, within the budget |
:::

### Check yourself: `checked`

`well_formed` wants seven characters, a dash at position 4, and two digits. What do these two lines print?

```una include="steps/16-checked/src/sku.una#L32-L33" title="steps/16-checked/src/sku.una"
  @console.print(show(" LAMP-02 "))
  @console.print(show("RUG-07"))
```

:::answer Show the answer
```text include="steps/16-checked/expected/output.txt#L3-L4"
sku LAMP-02
not a sku: RUG-07
```

`parse_sku` tests the trimmed text, so the spaces around `LAMP-02` do not matter, and the label shows the trimmed SKU, the value `checked` gave back. `RUG-07` has six characters, so the test fails, `parse_sku` fails with `NotASku`, and `show` prints its `Err` arm.
:::

### Opaque predicates

#### Rules the solver cannot read

Some rules cannot be written in the refinement language: "13 digits" needs a test on each character of a text, which the solver does not decide. A predicate can also be `opaque`: the verifier sees only its name. Its body may be any pure expression that cannot fail, such as a call of `is_digits`, and it runs when the program runs.

#### How a value gets an opaque fact

Since the verifier cannot read the body, it can never prove an opaque predicate. In code, a value gets its fact from `checked` at run time, or from the `ensures` of a capability operation ([chapter 8, Capabilities](/learn/capabilities/)). [Chapter 7](#s7-5) uses one for the format of a SKU. Here, a barcode scanned at the till:

```una include="steps/19-opaque/src/barcodes.una" title="steps/19-opaque/src/barcodes.una" verified="check, run"
module barcodes

--- A barcode as the store prints it: 13 digits. Only a run can tell, so the verifier sees only
--- the predicate's name.
predicate opaque is_barcode(t: Text) -> Bool = t.len == 13 and is_digits(t)

--- A text that passed the barcode check.
kind Barcode = Text where is_barcode(it)

--- Why a scan was refused.
kind ScanError = | NotABarcode

--- Text from the scanner becomes a `Barcode` here, or the call fails.
read_barcode(raw: Text) -> Barcode
  fails ScanError
=
  checked(raw.trim, is_barcode(it)) else fail NotABarcode

--- A price tag. It takes a `Barcode`, so it never sees unchecked text.
price_tag(code: Barcode, cents: Int) -> Text = "{code}: {cents} cents"

--- What the till shows for a scan.
describe(raw: Text) -> Text
=
  let outcome = attempt read_barcode(raw)
  when outcome
    is Ok(code) -> price_tag(code, cents: 1990)
    is Err -> "not a barcode: {raw}"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(describe("4006381333931"))
  @console.print(describe("12-34"))
```

```toml include="steps/19-opaque/una.toml" title="steps/19-opaque/una.toml"
[package]
name = "barcodes"
version = "0.1.0"
edition = "0.2"

[run]
entry = "barcodes"
grants = ["console"]

[escape_budget]
checked_per_module = 1
```

```text include="steps/19-opaque/expected/output.txt"
4006381333931: 1990 cents
not a barcode: 12-34
```

The example uses the tools of failure from [chapter 6, Failure](/learn/failure/). In brief:

- **`kind ScanError = | NotABarcode`** is a sum kind with one variant, the one reason a scan is refused. The leading `|` lets a sum have a single variant.
- **`fails ScanError`** in the header says the function may fail, with a variant of `ScanError`, instead of returning a value; **`fail NotABarcode`** is where it does ([section 7.2](#s7-2)).
- **`checked(raw.trim, is_barcode(it)) else fail NotABarcode`** runs the predicate's body on the trimmed text when the program runs. When it holds, the value becomes a `Barcode`; when it does not, the function fails with `NotABarcode` ([section 7.5](#s7-5)).
- **`attempt read_barcode(raw)`** keeps the outcome of a call that can fail as a value: `Ok(code)` when it returned `code`, `Err` when it failed. The `when` then handles both ([section 7.4](#s7-4)).
- **The escape budget.** Every `checked` counts against the module's budget in `una.toml`, here `checked_per_module = 1`, and appears in the build report: a reviewer sees each place where a run, not a proof, decides ([section 7.5](#s7-5)).

#### Calling an opaque predicate elsewhere

An opaque predicate may be called only inside `checked`, in the body of another opaque predicate, and named in a `where` clause or a capability operation's clause. Call it in an `if`, and `una` refuses:

```diff include="steps/19-opaque..steps/20-opaque-call:src/barcodes.una" context="1" title="src/barcodes.una"
--- a/src/barcodes.una
+++ b/src/barcodes.una
@@ -22,8 +22,3 @@
 --- What the till shows for a scan.
-describe(raw: Text) -> Text
-=
-  let outcome = attempt read_barcode(raw)
-  when outcome
-    is Ok(code) -> price_tag(code, cents: 1990)
-    is Err -> "not a barcode: {raw}"
+describe(raw: Text) -> Text = if is_barcode(raw) then "a barcode: {raw}" else "not a barcode: {raw}"
 
```

```text include="steps/20-opaque-call/expected/rendered.txt"
[U2016] Error: opaque predicate `is_barcode` is called outside `checked`, so its fact would bypass the escape budget
    ╭─[ src/barcodes.una:23:34 ]
    │
 23 │ describe(raw: Text) -> Text = if is_barcode(raw) then "a barcode: {raw}" else "not a barcode: {raw}"
    │                                  ───────┬───────
    │                                         ╰───────── opaque predicate `is_barcode` is called outside `checked`, so its fact would bypass the escape budget
    │
    │ Help 1: repair 1: if the code needs only the test and not the fact, test with a function, not a predicate, with the body of `is_barcode`
    │
    │ Help 2: repair 2 (escape: checked; a runtime test replaces the static proof: the program fails at run time where the proof would have rejected it; it counts against [escape_budget] and is listed in the build report): check the value with `checked(value, is_barcode(it)) else fail <Variant>`
    │
    │ Note: run `una explain U2016` for an explanation
────╯
```

The test itself is harmless, but a value that passed it would carry a fact the escape budget never counted. The first repair keeps the budget: when the code needs only a yes or no, write a plain function with the same body. The second makes the call a `checked`, which the budget counts.

#### `reflect` or `opaque`

| | `predicate reflect` | `predicate opaque` |
| --- | --- | --- |
| Body | in the refinement language, not recursive | any pure expression that cannot fail |
| What the verifier sees | the body | only the name |
| How a value gets the fact | proven, where it enters | `checked` at run time, or a capability operation's `ensures` |
| Called in code | anywhere | only inside `checked` and other opaque bodies |

### A guard, a stronger type or `checked`

:::decide
**Which to use:**

| The solver lacks a fact… | Use |
| --- | --- |
| That you can show from the kinds, such as "a product of two `Cents` is not negative" | A guard: bind the value, then `if … then … else` |
| That holds of a binding a loop updates | A refined type for the binding, such as `Nat` or `Cents` |
| About what one turn of a loop does, beyond its type | A helper with an `edit` parameter, whose `ensures` states it |
| That only a test at run time can decide, such as the format of a text | `checked`, which fails at run time and counts against the escape budget |
:::

Prefer a guard to `checked` when you can show from the kinds that the guard never fires. A guard needs no error variant and no budget, and the verifier proves the code around it. Use `checked` when you cannot show it: it fails at run time instead of answering quietly.

## 7.6 Data from outside: checking it once


### Where the program meets the world

Inside a program, contracts are checked where code meets code. At each call, the caller proves the callee's `requires` and gets its `ensures` in return. A refined kind is a meeting point too: a value is checked once, where it enters the kind, and every function after that may rely on it.

A **boundary** is where the program meets something it does not control. Two things cross it:

- **Data from outside**: text typed by a person, a line of a file, a field of a request from another system. No proof can say what a person will type.
- **Rules from outside**: a billing policy, a regulation, a promise made to customers. They are written by people, in documents, and the code must follow them.

Think of the receiving dock of a warehouse. Goods arrive from many suppliers, and each delivery is checked once, at the dock, against the order. Inside the warehouse, nobody checks the boxes again: a box on a shelf has passed the dock. And the rules of the dock, what is accepted and what is sent back, come from the store's purchasing policy, which says who wrote them. This section shows both halves: checking data once, where it enters, and recording the rules a contract comes from, with `requirement`.

### Why outside data needs a check

A discount rate is typed into the back office as text. Here is a function that turns the text into a `Percent`, and checks only that it is a number:

```una include="steps/21-unchecked-rate/src/rates.una#Percent..parse_rate" title="steps/21-unchecked-rate/src/rates.una"
--- A share in whole percent.
kind Percent = Int in 0..100

--- Why a typed rate was refused.
kind RateError = | NotANumber(raw: Text)

--- A discount rate typed into the back office. It checks that the text is a number, and
--- nothing more.
parse_rate(raw: Text) -> Percent
  fails RateError
=
  let n = raw.trim.to_int()
    if none fail NotANumber(raw)
  n
```

`una check .` refuses it:

```text include="steps/21-unchecked-rate/expected/rendered.txt"
[U5001] Error: refinement `result in 0..100` is refuted
    ╭─[ src/rates.una:16:3 ]
    │
  4 │ kind Percent = Int in 0..100
    │                       ───┬──
    │                          ╰──── range
    │
 16 │   n
    │   ┬
    │   ╰── refinement `result in 0..100` is refuted
    │
    │ Help 1: repair 1: add a guard (`if` or a `when` arm) that handles the values where `result in 0..100` does not hold
    │
    │ Help 2: repair 2 (escape: checked; a runtime test replaces the static proof: the program fails at run time where the proof would have rejected it; it counts against [escape_budget] and is listed in the build report): check the value with `checked(value, result in 0..100) else fail <Variant>`
    │
    │ Note 1: obligation ob-2b8bb19e1487 (refinement) is refuted: result in 0..100
    │
    │ Note 2: counterexample: raw = Text#1, raw.len = 0, result = 101
    │
    │ Note 3: run `una explain U5001` for an explanation
────╯
```

The goal is the condition of `Percent` for the returned value: `result in 0..100`. The counterexample says what the solver tried: `raw = Text#1`, some text, and `result = 101`. `Text#1` stands for a text the solver chose; it does not know what `to_int` returns for it, beyond an `Int`, so 101 is possible. That is the honest answer: a person can type `101`, or `-5`, or `150`.

Without the check, the program has two bad choices. It can trust the text, and carry a "percent" of 150 into every function that computes a price. Or every function that receives a rate can test it again, and one of them will forget. Una takes a third way: one function checks, and gives the value its kind.

### How to check data once

A function at the boundary takes the raw value, tests it, and either returns it with its refined kind or fails. The step of this part shows the two ways to test:

```una include="steps/22-check-forms/src/rates.una#Percent..by_check" title="steps/22-check-forms/src/rates.una"
--- A share in whole percent.
kind Percent = Int in 0..100

--- Why a rate was refused.
kind RateError = | OutOfRange(value: Int)

--- A guard: the code tests the value, and fails when it does not fit.
by_guard(n: Int) -> Percent
  fails RateError
=
  if n < 0 or n > 100 then fail OutOfRange(value: n) else n

--- `checked`: a test at run time that gives the value its kind, or fails.
by_check(n: Int) -> Percent
  fails RateError
=
  checked(n, it in 0..100) else fail OutOfRange(value: n)
```

```toml include="steps/22-check-forms/una.toml" title="steps/22-check-forms/una.toml"
[package]
name = "rates"
version = "0.1.0"
edition = "0.2"

[run]
entry = "rates"
grants = ["console"]

[escape_budget]
checked_per_module = 1
```

#### A guard that fails

`by_guard` tests the value with an `if`, and fails with a variant of its error kind when the value does not fit. In the `else` branch, the verifier knows `0 <= n` and `n <= 100`, so it proves that `n` is a `Percent`. Nothing runs that the proof did not cover.

#### `checked`

`by_check` writes the test as `checked(n, it in 0..100) else fail OutOfRange(value: n)`: the value, the condition with `it` for the value, and the failure. At run time it tests the condition. When the condition holds, the value comes back with its kind; when it does not, the function fails. [Chapter 7](#s7-5) introduced `checked`. Each one counts against the module's **escape budget**, a limit set in `una.toml` under `[escape_budget]`, and appears in the build report, so a reviewer sees every place where a run, not a proof, decides.

#### An opaque predicate

A rule that only running code can decide, such as "13 digits", goes in an opaque predicate, established with `checked`, as [Opaque predicates](#opaque-predicates), in section 7.3, shows.

#### Running the forms

```text include="steps/22-check-forms/expected/output.txt"
guard: Ok(15) Err(OutOfRange(150))
checked: Ok(15) Err(OutOfRange(-5))
```

Both forms give the same results here. The guard is the better choice when, as here, the test is in the refinement language: it needs no budget. `checked` is for a test the solver cannot follow, and for the cases where you want the build report to list the check.

### A discount rate typed in the back office

Now a whole boundary: the back office types a rate, and the program tells a number from text that is not one, and a rate in range from one out of it:

:::steps
```una include="steps/23-boundary/src/rates.una" title="steps/23-boundary/src/rates.una" verified="check, run"
module rates

--- A share in whole percent.
kind Percent = Int in 0..100

--- Why a typed rate was refused.
kind RateError = NotANumber(raw: Text) | OutOfRange(value: Int)

--- A discount rate typed into the back office. This is where text from a person becomes a
--- `Percent`, so this is where it is checked.
parse_rate(raw: Text) -> Percent
  fails RateError
=
  let n = raw.trim.to_int()
    if none fail NotANumber(raw)
  if n < 0 or n > 100
    fail OutOfRange(value: n)
  else
    n

--- What is left of 100 percent after the rate. A `Percent` needs no second check.
rest_of(rate: Percent) -> Percent = 100 - rate

--- Why a rate was refused, for a person to read.
explain(failure: RateError) -> Text
=
  when failure
    is NotANumber(raw) -> "'{raw}' is not a number"
    is OutOfRange(value) -> "{value} is not between 0 and 100"

describe(raw: Text) -> Text
=
  let outcome = attempt parse_rate(raw)
  when outcome
    is Ok(rate) -> "{rate}% off: the customer pays {rest_of(rate)}%"
    is Err(failure) -> explain(failure)

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(describe("15"))
  @console.print(describe("150"))
  @console.print(describe("ten"))
```

1. **`parse_rate(raw: Text) -> Percent`.** The only place where text becomes a `Percent`. It fails, with `RateError`, when the text is not a number or not between 0 and 100.
2. **`raw.trim.to_int()` and `if none fail NotANumber(raw)`.** `trim` removes the spaces at both ends, and `to_int` gives `None` for text that is not a number.
3. **`if n < 0 or n > 100` then `fail`, `else n`.** In the `else` branch, the verifier knows `0 <= n <= 100`, so it proves the result a `Percent`.
4. **`rest_of(rate: Percent) -> Percent = 100 - rate`.** Inside the program, nothing checks again: `100 - rate` is in range because `rate` is.
5. **`attempt parse_rate(raw)`.** In the `Ok(rate)` arm, `rate` is a `Percent`, with its fact, as after a direct call. `attempt` keeps what a callee promises ([chapter 7](#s7-4)).
:::

`una run .` prints:

```text include="steps/23-boundary/expected/output.txt"
15% off: the customer pays 85%
150 is not between 0 and 100
'ten' is not a number
```

### How a check at the boundary behaves

#### One way in

Once `parse_rate` exists, a `Percent` can come from nowhere but a proof: a literal the verifier checks, a computation it proves, or this function, whose `else` branch is itself a proof.

> [!SECURITY]
> A refined kind turns "every function must remember to check the rate" into "one function checks it, and the checker refuses every unproven way in". A new function that takes a `Percent` cannot receive 150, whoever calls it.

#### The fact survives `attempt` and `when`

`attempt` keeps the callee's promise on the `Ok` path, and the arm `is Ok(rate)` gives `rate` its kind. So the caller of a boundary function handles the failure once, and from then on works with a value that needs no check.

#### Fail, do not return an `Option`

A boundary function fails with a reason, rather than returning `None`. The reason tells a person what to fix. And in edition `0.2` an `Option[Percent]` is not even allowed: a refined kind cannot be a type argument, as the note in [Refinements of refinements, and type arguments](/learn/contracts/#refinements-of-refinements-and-type-arguments) says.

#### A refined field in a variant

A refined kind can be the field of a variant, as `PercentOff(rate: Percent)` in [the day-to-day program](/learn/contracts/#the-rules-and-the-kinds). Then building the variant proves the field: `PercentOff(rate: 110)` does not check ([a rate above 100 percent](/learn/contracts/#a-rate-above-100-percent-u5001)).

### Check yourself: boundaries

A colleague adds a function to the back-office module of [A discount rate typed in the back office](#a-discount-rate-typed-in-the-back-office). It reads a rate from text and passes it straight on, without `parse_rate`:

`quick_rest(raw: Text) -> Percent`, whose body reads the number with `let n = raw.trim.to_int()` and `if none use 0`, then calls `rest_of(n)`.

Does it check? If not, what is the obligation, and what is the fix?

:::answer Show the answer
It does not check. `rest_of` takes a `Percent`, so the call raises a refinement obligation: `n in 0..100`. Nothing tells the verifier what `to_int` returned, so it refutes the goal with a value out of range, as in [Why outside data needs a check](#why-outside-data-needs-a-check). The fix is the boundary itself: get the rate from `parse_rate`, with `attempt` or a handling clause, and pass on the `Percent` it returns. The checker leaves no other way in.
:::

A second one: which functions does `una trace TAX_1` list for the refund step of [How to write a requirement](/learn/contracts/#how-to-write-a-requirement)?

:::answer Show the answer
None. No function names `TAX_1` in a `derived from` clause, and the report shows it with nothing after the colon:

```text include="steps/24-requirements/expected/commands/report.txt#L22"
  TAX_1 (active): 
```

A requirement with no function is a rule the code does not implement yet, or implements without saying so. The report makes the gap visible.
:::

## 7.7 Day-to-day: order intake

### What the program must do

Now the program from [What you'll build](#what-youll-build). Orders arrive as lines of text. Each line must parse, name a product the inventory knows, and ask for no more units than are on hand. The inventory is a service that can time out. A bad line must not stop the batch, and the report must say why each rejected line was rejected.

The design follows from that, and each part uses one section of this chapter: one error kind for the order layer, `OrderError`, whose variants carry what an operator needs ([section 7.2](#s7-2)); one for the inventory service, `StoreError`, which the order layer translates with a clause ([section 7.3](#s7-3)); and `attempt` around each line, so that the batch goes on ([section 7.4](#s7-4)). The inventory is a capability, a service the program asks through operations; [Recovering with a default from a service](/learn/capabilities/#recovering-with-a-default-from-a-service) introduced capabilities and handlers, and [chapter 12](/learn/capabilities/) covers them.

### The kinds and the service

```una include="day-to-day/src/orders.una#L1-L17" title="day-to-day/src/orders.una" caption="the kinds and the service"
module orders

--- One line of an order: a stock-keeping unit (SKU) and how many of it.
pub kind Order
  sku: Text
  quantity: Int

--- Why an order line was rejected. Each variant carries what a person needs to act on it.
pub kind OrderError = Malformed(line: Text) | BadQuantity(line: Text) | UnknownSku(sku: Text) | OutOfStock(sku: Text, wanted: Int, left: Int) | Unavailable

--- How the inventory service can fail.
pub kind StoreError = | Timeout

--- The inventory service: how many units of a SKU are on hand, or `None` for an unknown SKU.
pub capability Inventory
  op on_hand(sku: Text) -> Option[Int]
    fails StoreError
```

`OutOfStock` carries the SKU, the units wanted and the units left, which is everything the report line needs. `Unavailable` carries nothing, because the operator's action is the same whatever the cause: retry later.

### Parsing, a pure step

`parse_order` only looks at the text. It has no `uses`, so it cannot touch the inventory, and its tests need no fakes. Each problem with the text becomes its own variant: `if none fail` for a part that is missing, and `fail` in a branch for a quantity below 1.

```una include="day-to-day/src/orders.una#parse_order" title="day-to-day/src/orders.una"
--- Reads `"SKU, quantity"`. Pure: it only looks at the text.
pub parse_order(line: Text) -> Order
  fails OrderError
=
  let parts = line.split(on: ",")
  if parts.len != 2
    fail Malformed(line)
  else
    let sku = parts.at(index: 0)
      if none fail Malformed(line)
    let raw = parts.at(index: 1)
      if none fail Malformed(line)
    let quantity = raw.trim.to_int()
      if none fail BadQuantity(line)
    if quantity < 1
      fail BadQuantity(line)
    else
      Order(sku: sku.trim, quantity: quantity)
```

> [!NOTE]
> `at` returns an `Option` even after the length check, because its type does not depend on the check. The `if none fail Malformed(line)` clauses state what the code would do anyway.

### Checking stock, a step with a service

Two clauses handle the one call: the service's failure becomes `Unavailable`, and an unknown SKU becomes `UnknownSku`. After them, `left` is a plain `Int`, and the comparison with the quantity wanted is ordinary code. `check_stock` returns the order unchanged when there is enough stock, so the next step can use it.

```una include="day-to-day/src/orders.una#check_stock" title="day-to-day/src/orders.una"
--- Confirms that the inventory holds enough units of the order's SKU.
pub check_stock(order: Order) -> Order
  uses @inventory: Inventory[on_hand]
  fails OrderError
=
  let left = @inventory.on_hand(order.sku)
    if error fail Unavailable
    if none fail UnknownSku(sku: order.sku)
  if order.quantity > left
    fail OutOfStock(sku: order.sku, wanted: order.quantity, left: left)
  else
    order
```

### Composing the steps

Both steps fail with `OrderError`, the same kind as `accept`, so `if error pass` hands their failures on unchanged. The order of the two statements is the order of the work: a line that does not parse never reaches the inventory, which [section 6.6](#the-order-of-the-steps-expect-not-performed) proves with an example.

```una include="day-to-day/src/orders.una#accept" title="day-to-day/src/orders.una"
--- One line, from text to an order that can be shipped.
pub accept(line: Text) -> Order
  uses @inventory: Inventory[on_hand]
  fails OrderError
=
  let order = parse_order(line)
    if error pass
  check_stock(order)
    if error pass
```

### The batch

This is where [section 7.4](#s7-4) pays off. `attempt` keeps each outcome, and a `for` loop appends it to a list declared with `let edit` ([chapter 9](/learn/loops/#s9-1)), so `process` itself never fails. Its header has no `fails`, and that is a promise to its callers.

```una include="day-to-day/src/orders.una#process" title="day-to-day/src/orders.una"
--- Every line, accepted or rejected: one bad line does not stop the batch.
pub process(lines: List[Text]) -> List[Result[Order, OrderError]]
  uses @inventory: Inventory[on_hand]
=
  let edit results: List[Result[Order, OrderError]] = []
  for line in lines
    let outcome = attempt accept(line)
    results = results.append(item: outcome)
  results
```

`process` returns `List[Result[Order, OrderError]]`, not the accepted orders alone. The caller keeps every outcome in the order of the batch, so it can print a report, count the rejected lines, retry the `Unavailable` ones later, or ship the rest. A list of orders alone would lose the reasons.

### The report

One `when` per kind. If `OrderError` gains a variant, the checker reports this `when` until it has an arm for it ([exercise 1](#exercise-1-a-per-line-limit) shows this). `reason` writes the fields of each variant into its sentence, which is why each variant carries what it does: an operator who reads `3 of DESK-02 wanted, 1 left` knows what to change.

```una include="day-to-day/src/orders.una#reason..describe" title="day-to-day/src/orders.una"
--- What a person reads in the batch report.
pub reason(failure: OrderError) -> Text
=
  when failure
    is Malformed(line) -> "cannot read the line '{line}'"
    is BadQuantity(line) -> "the quantity in '{line}' is not a whole number above 0"
    is UnknownSku(sku) -> "no product has the SKU {sku}"
    is OutOfStock(sku, wanted, left) -> "{wanted} of {sku} wanted, {left} left"
    is Unavailable -> "the inventory did not answer; retry later"

--- One line of the batch report.
pub describe(outcome: Result[Order, OrderError]) -> Text
=
  when outcome
    is Ok(value) -> "ok      {value.quantity} x {value.sku}"
    is Err(failure) -> "reject  {reason(failure)}"
```

### Running it

In production, the `Inventory` handler would call the warehouse over the network. Here, a handler holds the stock in a map, and `main` installs it with `with`. `warehouse` takes the map as a parameter when it is installed, so each run and each example can start from the stock it needs. `offline` always fails, so an example can reach `Unavailable` whenever it needs to.

```una include="day-to-day/src/orders.una#warehouse..main" title="day-to-day/src/orders.una"
--- An inventory held in memory, for this example run and for tests.
handler warehouse(stock: Map[Text, Int]) for Inventory
  op on_hand(sku) = stock.get(key: sku)

--- An inventory that never answers.
handler offline() for Inventory
  op on_hand(sku) = fail Timeout

pub main() -> Unit
  uses @console: Console[print]
=
  let stock = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)
  let lines = ["LAMP-01, 2", "DESK-02, 3", "CHAIR-09, 1", "LAMP-01, two", "LAMP-01"]
  let results = process(lines) with @inventory = warehouse(stock)
  for outcome in results
    @console.print(describe(outcome))
```

`una run .` prints the report shown in [What you'll build](#what-youll-build). The order lines here are literals, one for each outcome: a line in stock, too many units, an unknown SKU, a quantity in words and a line with no comma. `describe` pads `ok` and `reject` to the same width, so the reasons line up.

> [!SECURITY]
> Lines read from a file are labeled `internal`, a label that may not reach the console without a declared policy. Printing a report built from them is a question of information flow, which [chapter 9, Information flow](/learn/information-flow/), answers with a policy.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/orders.una" title="day-to-day/src/orders.una" caption="the whole program" verified="check, run, test"
module orders

--- One line of an order: a stock-keeping unit (SKU) and how many of it.
pub kind Order
  sku: Text
  quantity: Int

--- Why an order line was rejected. Each variant carries what a person needs to act on it.
pub kind OrderError = Malformed(line: Text) | BadQuantity(line: Text) | UnknownSku(sku: Text) | OutOfStock(sku: Text, wanted: Int, left: Int) | Unavailable

--- How the inventory service can fail.
pub kind StoreError = | Timeout

--- The inventory service: how many units of a SKU are on hand, or `None` for an unknown SKU.
pub capability Inventory
  op on_hand(sku: Text) -> Option[Int]
    fails StoreError

--- Reads `"SKU, quantity"`. Pure: it only looks at the text.
pub parse_order(line: Text) -> Order
  fails OrderError
=
  let parts = line.split(on: ",")
  if parts.len != 2
    fail Malformed(line)
  else
    let sku = parts.at(index: 0)
      if none fail Malformed(line)
    let raw = parts.at(index: 1)
      if none fail Malformed(line)
    let quantity = raw.trim.to_int()
      if none fail BadQuantity(line)
    if quantity < 1
      fail BadQuantity(line)
    else
      Order(sku: sku.trim, quantity: quantity)

--- Confirms that the inventory holds enough units of the order's SKU.
pub check_stock(order: Order) -> Order
  uses @inventory: Inventory[on_hand]
  fails OrderError
=
  let left = @inventory.on_hand(order.sku)
    if error fail Unavailable
    if none fail UnknownSku(sku: order.sku)
  if order.quantity > left
    fail OutOfStock(sku: order.sku, wanted: order.quantity, left: left)
  else
    order

--- One line, from text to an order that can be shipped.
pub accept(line: Text) -> Order
  uses @inventory: Inventory[on_hand]
  fails OrderError
=
  let order = parse_order(line)
    if error pass
  check_stock(order)
    if error pass

--- Every line, accepted or rejected: one bad line does not stop the batch.
pub process(lines: List[Text]) -> List[Result[Order, OrderError]]
  uses @inventory: Inventory[on_hand]
=
  let edit results: List[Result[Order, OrderError]] = []
  for line in lines
    let outcome = attempt accept(line)
    results = results.append(item: outcome)
  results

--- What a person reads in the batch report.
pub reason(failure: OrderError) -> Text
=
  when failure
    is Malformed(line) -> "cannot read the line '{line}'"
    is BadQuantity(line) -> "the quantity in '{line}' is not a whole number above 0"
    is UnknownSku(sku) -> "no product has the SKU {sku}"
    is OutOfStock(sku, wanted, left) -> "{wanted} of {sku} wanted, {left} left"
    is Unavailable -> "the inventory did not answer; retry later"

--- One line of the batch report.
pub describe(outcome: Result[Order, OrderError]) -> Text
=
  when outcome
    is Ok(value) -> "ok      {value.quantity} x {value.sku}"
    is Err(failure) -> "reject  {reason(failure)}"

--- An inventory held in memory, for this example run and for tests.
handler warehouse(stock: Map[Text, Int]) for Inventory
  op on_hand(sku) = stock.get(key: sku)

--- An inventory that never answers.
handler offline() for Inventory
  op on_hand(sku) = fail Timeout

pub main() -> Unit
  uses @console: Console[print]
=
  let stock = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)
  let lines = ["LAMP-01, 2", "DESK-02, 3", "CHAIR-09, 1", "LAMP-01, two", "LAMP-01"]
  let results = process(lines) with @inventory = warehouse(stock)
  for outcome in results
    @console.print(describe(outcome))

example "a line in stock is accepted"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do accept("LAMP-01, 2")
  expect result.quantity == 2

example "too many units are out of stock"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do accept("LAMP-01, 9")
  expect fails OutOfStock

example "a malformed line never reaches the inventory"
  given @inventory = offline()
  do accept("LAMP-01")
  expect fails Malformed
  expect not performed @inventory.on_hand

example "an inventory that does not answer is Unavailable"
  given @inventory = offline()
  do accept("LAMP-01, 1")
  expect fails Unavailable

example "a SKU the inventory does not know is UnknownSku"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do accept("CHAIR-09, 1")
  expect fails UnknownSku

example "a quantity that is not a number is BadQuantity, before the inventory is asked"
  given @inventory = offline()
  do accept("LAMP-01, two")
  expect fails BadQuantity
  expect not performed @inventory.on_hand
```

## 7.8 Testing it

### One example per path

Every failure path gets an example: a line in stock, too many units, a malformed line, an inventory that does not answer, an unknown SKU, and a quantity that is not a number. The fakes make each one deterministic. Each example states one fact, so when one fails, `una test .` names it and says which `expect` line did not hold, as [the exercises](#s7-10) show.

```una include="day-to-day/src/orders.una#L105-L135" title="day-to-day/src/orders.una" caption="the examples"
example "a line in stock is accepted"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do accept("LAMP-01, 2")
  expect result.quantity == 2

example "too many units are out of stock"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do accept("LAMP-01, 9")
  expect fails OutOfStock

example "a malformed line never reaches the inventory"
  given @inventory = offline()
  do accept("LAMP-01")
  expect fails Malformed
  expect not performed @inventory.on_hand

example "an inventory that does not answer is Unavailable"
  given @inventory = offline()
  do accept("LAMP-01, 1")
  expect fails Unavailable

example "a SKU the inventory does not know is UnknownSku"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do accept("CHAIR-09, 1")
  expect fails UnknownSku

example "a quantity that is not a number is BadQuantity, before the inventory is asked"
  given @inventory = offline()
  do accept("LAMP-01, two")
  expect fails BadQuantity
  expect not performed @inventory.on_hand
```

Each line of an example has one job. The first two install the fakes and make the call:

- `given @inventory = warehouse(…)` installs a fake inventory for this example only, as `with` does for one call.
- `do accept("LAMP-01, 9")` calls the code under test. A `do` line may nest calls that can fail, which a statement in a body may not.

The `expect` lines that follow depend on what the example tests.

### The accepted line: `expect result`

The first example tests the path on which nothing fails. `expect result.quantity == 2` states a fact about `result`, the value the `do` call returned.

### The failure paths: `expect fails`

The other five examples each test a failure, one for each variant of `OrderError`. `expect fails OutOfStock` holds when the `do` call failed with that variant. A `do` call that fails with no `expect fails` line fails the example.

### The order of the steps: `expect not performed`

`expect not performed @inventory.on_hand` holds when the call never performed that operation. Here it proves the order of the steps: a malformed line or a quantity that is not a number never reaches the inventory, because parsing comes first.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L9"
example orders "a line in stock is accepted" ... ok
example orders "too many units are out of stock" ... ok
example orders "a malformed line never reaches the inventory" ... ok
example orders "an inventory that does not answer is Unavailable" ... ok
example orders "a SKU the inventory does not know is UnknownSku" ... ok
example orders "a quantity that is not a number is BadQuantity, before the inventory is asked" ... ok

6 examples: 6 passed, 0 failed
```

## 7.9 Common mistakes

Each mistake below is a small change to `day-to-day/src/orders.una`, followed by what `una check .` reports.

### Forgetting the clause (U3007)

:::mistake
Remove `if error pass` under `let order = parse_order(line)`:

```diff include="day-to-day..mistakes/1:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -56,3 +56,2 @@
   let order = parse_order(line)
-    if error pass
   check_stock(order)
```

```text include="mistakes/1/expected/rendered.txt"
[U3007] Error: `parse_order` can fail with `OrderError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
    ╭─[ src/orders.una:56:15 ]
    │
 56 │   let order = parse_order(line)
    │               ────────┬────────
    │                       ╰────────── `parse_order` can fail with `OrderError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
    │
    │ Note: run `una explain U3007` for an explanation
────╯
```

*Why:* in languages with exceptions, a failure travels up by itself, so leaving the call bare feels natural. In Una nothing propagates implicitly. The message names the call, `parse_order`, and the kind it fails with, `OrderError`, and the mark covers the call. Its last part lists the two ways to handle it.

*Fix:* add the clause that matches your intent (table in [section 7.3](#s7-3)).
:::

### Passing a failure of another kind (U3008)

:::mistake
In `check_stock`, write `if error pass` instead of `if error fail Unavailable`:

```diff include="day-to-day..mistakes/2:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -43,3 +43,3 @@
   let left = @inventory.on_hand(order.sku)
-    if error fail Unavailable
+    if error pass
     if none fail UnknownSku(sku: order.sku)
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U3008] Error: `if error pass` passes a `StoreError` failure, and this code fails with `OrderError`; use `if error fail` with a variant of `OrderError`
```

*Why:* `pass` looks like the simplest clause, but it hands the failure on unchanged, and a function has one error kind: `StoreError` is not `OrderError`. The message names both kinds, the one the call fails with and the one this code fails with, and says what to write instead.

*Fix:* translate with `if error fail Unavailable`. To keep the original, add a variant with a field of type `StoreError`, such as `| StoreFailed(cause: StoreError)`, and write `if error fail StoreFailed(cause: error)`.
:::

### Failing with a variant of another kind (U3009)

:::mistake
Write `if error fail Timeout` in `check_stock`:

```diff include="day-to-day..mistakes/3:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -43,3 +43,3 @@
   let left = @inventory.on_hand(order.sku)
-    if error fail Unavailable
+    if error fail Timeout
     if none fail UnknownSku(sku: order.sku)
```

```text include="mistakes/3/expected/rendered.txt#L1"
[U3009] Error: `Timeout` is a variant of `StoreError`, and this code fails with `OrderError`
```

*Why:* `Timeout` is the name of what went wrong, so it is tempting to reuse it. But `fail` names a variant of the function's own error kind, and `Timeout` belongs to `StoreError`. The message names the variant, its kind, and the kind this code fails with.

*Fix:* name a variant of your own kind.
:::

### A public function that fails without saying so (U3009)

:::mistake
Remove `fails OrderError` from `parse_order`:

```diff include="day-to-day..mistakes/4:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -20,3 +20,2 @@
 pub parse_order(line: Text) -> Order
-  fails OrderError
 =
```

```text include="mistakes/4/expected/rendered.txt#L1,L8"
[U3009] Error: this code declares no error kind, so it cannot fail with `Malformed`; declare `fails` in its header
    │ Help: repair 1: declare `fails OrderError` in the header; edit src/orders.una:20:37..20:37 to "\n  fails OrderError"
```

`una check` reports this once for every `fail` in the body, five times here.

*Why:* a private function may leave out `fails`, so it is easy to forget that a `pub` one may not: a `pub` header is a reviewed contract. The message is reported at each `fail` of the body, and the help line gives the exact edit, the line to add and where.

*Fix:* `una fix .` applies the repair shown.
:::

### Nesting a call that can fail (U3013)

:::mistake
Write `check_stock(parse_order(line))`:

```diff include="day-to-day..mistakes/5:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -55,5 +55,3 @@
 =
-  let order = parse_order(line)
-    if error pass
-  check_stock(order)
+  check_stock(parse_order(line))
     if error pass
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U3013] Error: `parse_order` has effects or can fail, so it must be the whole expression of a statement or `let`; bind its result with `let` first
```

*Why:* nesting calls is how many languages chain steps. In Una a call that can fail is the whole expression of its statement, so that each failure has its own handling line and the order of the work stays visible. The message names the inner call, `parse_order`, and says what to do: bind its result with `let` first.

*Fix:* `let order = parse_order(line)` with its clause, then `check_stock(order)` with its own. (`do` lines of examples are exempt.)
:::

### The clause on the same line (U0101)

:::mistake
Write `let order = parse_order(line) if error pass`:

```diff include="day-to-day..mistakes/6:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -55,4 +55,3 @@
 =
-  let order = parse_order(line)
-    if error pass
+  let order = parse_order(line) if error pass
   check_stock(order)
```

```text include="mistakes/6/expected/rendered.txt#L1,L8"
[U0101] Error: a handling clause goes on its own line, indented under the expression it handles
    │ Help: repair 1: move the clause to its own line; edit src/orders.una:56:32..56:46 to "\n    if error pass"
```

*Why:* the clause reads like part of the sentence, so it is natural to write it on the same line. But a clause is a line of its own, so that every handling decision starts a line a reviewer can scan. The help line gives the exact edit: the clause moves to the next line, indented.

*Fix:* `una fix .` moves it.
:::

### `if none` before `if error` (U0102)

:::mistake
Swap the two clauses under `@inventory.on_hand` in `check_stock`:

```diff include="day-to-day..mistakes/7:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -43,4 +43,4 @@
   let left = @inventory.on_hand(order.sku)
+    if none fail UnknownSku(sku: order.sku)
     if error fail Unavailable
-    if none fail UnknownSku(sku: order.sku)
   if order.quantity > left
```

```text include="mistakes/7/expected/rendered.txt#L1"
[U0102] Error: `if error` clause after `if none`; handling clauses go in the order if error, if none
```

*Why:* both clauses handle one call, so their order can look free. It is fixed: the `if error` clause handles the call, and `if none` handles the value it gave, so the call's failure comes first. The message names the clause out of place and the order to use.

*Fix:* put `if error` first.
:::

### Re-raising a stored failure (U0101)

:::mistake
After `attempt`, write `is Err(failure) -> fail failure`:

```diff include="day-to-day..mistakes/8:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -85,3 +85,3 @@
     is Ok(value) -> "ok      {value.quantity} x {value.sku}"
-    is Err(failure) -> "reject  {reason(failure)}"
+    is Err(failure) -> fail failure
 
```

```text include="mistakes/8/expected/rendered.txt#L1,L8"
[U0101] Error: unexpected `failure`, expected a variant
    │ Help: repair 1: `fail` takes a variant of the error kind, as in `fail Broke`, not a stored value; fail where the error is found, or pass a call's failure on with `if error pass`
```

*Why:* after `attempt`, the failure is in a binding, and handing it on with `fail` looks natural. But `fail` takes a variant of the error kind, at the place the failure is decided, not a stored value: the parser expected a variant name where `failure` stands. The help line explains both ways out.

*Fix:* if you only want to pass the failure on, do not `attempt`; use `if error pass`. [Exercise 3](/learn/testing/#exercise-4-fall-back-to-the-backup) shows a fallback that needs no re-raise.
:::

## 7.10 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's example added, and a stub of what to write when there is one. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

### Exercise 1: a per-line limit

::::exercise
The store ships at most 10 units of a SKU per line. Add a variant `TooMany(sku: Text, limit: Int)` and reject larger quantities in `parse_order`, before the inventory is asked. The start package ends with this example, and `una check .` reports U1001 until the variant exists:

```una include="exercises/1/start/src/orders.una#L137-L141" title="exercises/1/start/src/orders.una"
example "more than ten units on one line is TooMany"
  given @inventory = offline()
  do accept("LAMP-01, 11")
  expect fails TooMany
  expect not performed @inventory.on_hand
```

:::hint
*Hint:* work in three small steps, and run `una check .` after each. First add the variant `TooMany(sku: Text, limit: Int)` to `OrderError`: the checker then shows the one `when` that needs a new arm, in `reason`. Second, give `reason` that arm, with a sentence that uses both fields. Third, in `parse_order`, add one more `else if` branch after the check for a quantity below 1, which fails with `TooMany` when the quantity is above 10 ([`fail` in a branch](#fail-in-a-branch)).
:::

What `una check .` reports after adding only the variant:

```text include="exercises/1/variant/expected/rendered.txt#L1,L8"
[U2007] Error: `when` does not match variant `TooMany` of `OrderError`
    │ Help: repair 1: add an arm for each missing variant, such as `is TooMany`, or an `else` arm
```

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Add the variant to `OrderError`, the limit to `parse_order`, and the arm to `reason`:

```diff include="exercises/1/start..exercises/1/answer:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -8,3 +8,3 @@
 --- Why an order line was rejected. Each variant carries what a person needs to act on it.
-pub kind OrderError = Malformed(line: Text) | BadQuantity(line: Text) | UnknownSku(sku: Text) | OutOfStock(sku: Text, wanted: Int, left: Int) | Unavailable
+pub kind OrderError = Malformed(line: Text) | BadQuantity(line: Text) | UnknownSku(sku: Text) | OutOfStock(sku: Text, wanted: Int, left: Int) | Unavailable | TooMany(sku: Text, limit: Int)
 
@@ -34,2 +34,4 @@
       fail BadQuantity(line)
+    else if quantity > 10
+      fail TooMany(sku: sku.trim, limit: 10)
     else
@@ -79,2 +81,3 @@
     is Unavailable -> "the inventory did not answer; retry later"
+    is TooMany(sku, limit) -> "at most {limit} of {sku} per line"
 
```

`una test .` reports every example passing.
:::
::::

### Exercise 2: units shipped

::::exercise
Write `shipped(results)`, the total of the units of the accepted lines. The start package has it with a body of `0`, and this example:

```una include="exercises/2/start/src/orders.una#L137-L143" title="exercises/2/start/src/orders.una"
--- How many units a batch ships in all. Exercise 2: replace the 0.
pub shipped(results: List[Result[Order, OrderError]]) -> Int = 0

example "a batch ships only its accepted units"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do shipped(process(["LAMP-01, 2", "LAMP-01, 9", "LAMP-01, 1"]))
  expect result == 3
```

:::hint
*Hint:* first write a private function from one outcome to its units: a `when` over the `Result` ([section 7.4](#s7-4)) whose `Ok` arm gives the order's quantity and whose `Err` arm gives 0. Then `shipped` is one line: `map` that function over the results, and `sum` the list ([chapter 10](/learn/collections/#s10-3)).
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/2/start/expected/commands/test.txt#L8-L12"
example orders "a batch ships only its accepted units" ... FAILED
  src/orders.una:143: expect result == 3
  it is false, with `result` = `0`

7 examples: 6 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Add `units`, and give `shipped` its body:

```diff include="exercises/2/start..exercises/2/answer:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -136,4 +136,11 @@
 
---- How many units a batch ships in all. Exercise 2: replace the 0.
-pub shipped(results: List[Result[Order, OrderError]]) -> Int = 0
+--- The units an outcome ships: its quantity when accepted, 0 when rejected.
+units(outcome: Result[Order, OrderError]) -> Int
+=
+  when outcome
+    is Ok(value) -> value.quantity
+    is Err -> 0
+
+--- How many units a batch ships in all.
+pub shipped(results: List[Result[Order, OrderError]]) -> Int = results.map(each: units).sum()
 
```
:::
::::

## 7.11 Recap and reference

### For agents

:::agents
Every diagnostic of [Common mistakes](#s7-9) is available as JSON with `una --json check .`. For [Forgetting the clause](#forgetting-the-clause-u3007):

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U3007","severity":"error","domain":"authority","message":"`parse_order` can fail with `OrderError`; handle the failure with an `if error` clause, or wrap the call in `attempt`","primary":{"file":"src/orders.una","start":{"line":56,"col":15},"end":{"line":56,"col":32}},"related":[],"repairs":[],"explain":"una explain U3007"}],"fixable":0}
```

`repairs` is empty because the right clause depends on intent, which only the author knows. U0101 ([the clause on the same line](#the-clause-on-the-same-line-u0101)) and U3009 ([a public function that fails without saying so](#a-public-function-that-fails-without-saying-so-u3009)) carry exact edits, which `una fix .` applies. The compact rule: *a call that can fail is the whole expression of its statement, followed by `if error …` and then `if none …` on their own lines, or is wrapped in `attempt`, which gives a `Result`.*
:::

### Recap

:::recap
- A failure is a value of a sum kind you declare. Its variants carry what someone needs to act on it.
- A header declares at most one error kind with `fails`, and may add `fails of p` to fail as the parameter `p` does. A `pub` function must declare it, and a private one may let the checker infer it.
- A call that can fail is the whole expression of its statement, and its handling clauses follow on their own lines: `if error` first, then `if none`.
- `use` recovers, `pass` hands on the same kind, `fail V(cause: error)` translates between layers.
- `attempt` keeps the outcome of one call as a `Result`, for batches, counts and fallbacks.
- `checked` is a budgeted run-time test for facts no proof can establish. Use it at the edge.
- Fake the services with handlers, and give every failure path an example.
:::

### Reference

:::reference
- Construct pages: [`fails`](/docs/language/errors/fails/), [`fail`](/docs/language/errors/fail/), [`if error` and `if none`](/docs/language/errors/if-error/), [`attempt`](/docs/language/errors/attempt/), [`checked` and the escape budget](/docs/language/errors/checked/), [`capability` and `op`](/docs/language/capabilities/capability/), [`handler`](/docs/language/capabilities/handler/), [`with`](/docs/language/capabilities/with/), [`example`](/docs/language/examples/example/), [`predicate`](/docs/language/types/predicate/)
- Prelude: [`Option`, `Result`, `to_int`, `parse_int`, `ParseError`, `is_ok`](/docs/std/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U0102](/docs/errors/U0102/), [U1001](/docs/errors/U1001/), [U2001](/docs/errors/U2001/), [U2007](/docs/errors/U2007/), [U3007](/docs/errors/U3007/), [U3008](/docs/errors/U3008/), [U3009](/docs/errors/U3009/), [U3013](/docs/errors/U3013/), [U5001](/docs/errors/U5001/) (a refinement the verifier refutes), [U7003](/docs/errors/U7003/) (`checked` beyond the escape budget), [U3025](/docs/errors/U3025/) and [U3026](/docs/errors/U3026/) (edition `0.3`: a clause or `attempt` on a call that cannot fail), and the stops at run time: [U6001](/docs/errors/U6001/) (`main` failed with its declared kind), [U6003](/docs/errors/U6003/) (call depth or memory), [U6004](/docs/errors/U6004/) (an HTTP header value with a control character), [U6005](/docs/errors/U6005/) (host text that is not valid UTF-8) and [U8001](/docs/errors/U8001/) (an internal error of una)
- Specification: [errors](/docs/spec/06-errors/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [requirements and examples](/docs/spec/08-requirements-and-examples/), [types](/docs/spec/03-types/), [text](/docs/spec/22-text/)
:::
