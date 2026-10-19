---
learn: "7"
title: Results and failures
editions: ["0.2"]
codes: [U0101, U0102, U1001, U2001, U2007, U2016, U3007, U3008, U3009, U3013, U5001, U7003]
time: 60
builds: An order intake that accepts or rejects each order line, with a reason for every rejection
prerequisites: ["3", "4", "5", "6"]
template: 2
nav: ["Option", "fails and fail", "The handling clauses", "attempt and Result", "checked and opaque predicates", "Data from outside", "Day-to-day: order intake", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 7 Results and failures

Real programs spend much of their code on what goes wrong: a text that is not a number, a product the store does not sell, more units wanted than are on the shelf. This chapter shows how Una says so. A value that may be missing has a type of its own, `Option`. A function that can fail says so in its header, with a kind you declare for its failures, and every call of it is followed by a line that says what to do when it fails. You learn to write those lines, to keep a failure as a value, and to check data from outside the program once, where it enters.

## What you'll build

:::build
An order intake for a small store. It reads order lines such as `LAMP-01, 2`, checks each one against the store's stock list, and reports every line, accepted or rejected, with a reason a person can act on:

```text include="day-to-day/expected/output.txt"
ok      2 x LAMP-01
reject  3 of DESK-02 wanted, 1 left
reject  no product has the SKU CHAIR-09
reject  the shelf of RUG-07 is being counted; retry later
reject  the quantity in 'LAMP-01, two' is not a whole number above 0
reject  cannot read the line 'LAMP-01'
```

You will learn to:

- use an `Option` for a value that may be missing, and take it apart;
- declare a kind of failures whose variants carry what someone needs to fix the problem;
- choose among the five handling clauses, and translate a failure from one layer to the next;
- keep a failure as a value with `attempt`, so that one bad line still gets its own report;
- test data from outside the program once, with a guard or with `checked`.
:::

## Why it works this way

In many languages a function can fail in ways its header does not show: an exception thrown three calls deep, or a special "no value" returned on a path nobody tested. A reader has to read the bodies to find out what can go wrong, and a reviewer cannot tell from a change whether it added a new way to fail.

Una puts all of that in view. Four rules do it:

:::steps
1. **A missing value has its own type.** A search that may find nothing gives an `Option`, and the checker refuses to use it as if the value were there.
2. **A failure is a value of a sum kind.** You declare it like any other kind, and its variants can carry data.
3. **A header says what a function can fail with.** `fails OrderError` is part of the header, next to `requires` and `uses`. A public function that does not say `fails` cannot fail, and the checker holds it to that.
4. **Every call that can fail is handled where it is made.** The next line, indented, says what happens: carry on with a value, pass the failure on, or turn it into a failure of your own kind. Nothing passes a failure on unless that line says so.
:::

The price is a few extra lines at each call. In return, a function's failures can be read from its header, and none goes unhandled.

> [!KEY]
> Nothing in Una fails at run time without the code saying so, apart from a few stops outside the program's logic, such as running out of call depth or memory (U6003); [Reference](#reference) lists them all. Division by zero and a broken precondition are ruled out by proof ([chapter 5](/learn/contracts/)), and there are no exceptions to catch.

## 7.1 A value that may be missing: `Option`

### What an `Option` is

Some questions have no answer. Ask a store for the price of a product it does not sell, ask the text `"seven"` for the number it holds, or ask a SKU for the position of a `/` it does not have: there is nothing to give back. An **`Option`** is the type of an answer that may be missing. Think of a parcel locker at a pickup point: you open it, and either a parcel is inside or the locker is empty. Before you carry anything away, you look.

`Option[T]` is a generic sum kind of the prelude ([section 4.4](/learn/kinds/#s4-4)) with two variants:

- `Some(value)` holds one value of the type `T`. A price lookup that finds the price gives `Some(1990)`, an `Option[Int]`.
- `None` holds nothing. It means "there is no value here".

`T` is the **type parameter**: it stands for whatever type the option may hold. `Option[Int]` may hold an `Int`, and `Option[Product]` a `Product`. An `Option[Int]` is not an `Int`: you cannot add it to a number, compare it with `<`, or use it where an `Int` is expected, until you have said what happens when it is `None`.

### Why absence needs its own type

In many languages a search that finds nothing returns a special value, often called null, of the same type as a real answer. The type then says that a product is always there, and the first line that uses a missing product fails while the program runs, often far from the search.

In Una the type says it. Each example of this chapter is a package, made as [chapter 2](/learn/numbers/#each-step-is-a-package) explains, and the chapter's download, `07-failure.tar.gz`, holds them all. Here, `find_product` gives back an `Option[Product]`, and `price_of` reads the price from it as if the product were always found:

```diff include="steps/01-option..steps/02-missing-price:src/lookup.una" context="1" title="src/lookup.una"
--- a/src/lookup.una
+++ b/src/lookup.una
@@ -21,5 +21,3 @@
   let found = find_product(sku)
-  when found
-    is Some(product) -> Some(product.cents)
-    is None -> None
+  Some(found.cents)
 
```

`una check .` reports:

```text include="steps/02-missing-price/expected/rendered.txt"
[U1001] Error: `Option[Product]` has no field `cents`, and no function `cents` in scope applies
    ╭─[ src/lookup.una:22:14 ]
    │
 22 │   Some(found.cents)
    │              ──┬──
    │                ╰──── `Option[Product]` has no field `cents`, and no function `cents` in scope applies
    │
    │ Note: run `una explain U1001` for an explanation
────╯
```

Read it from the top. `found` is an `Option[Product]`, and the message says that this type has no field `cents`: the field belongs to `Product`, which the option may or may not hold. The mark points at `.cents`. The checker does not guess what a missing product should mean. You decide, with one of the forms of the next part, and the decision is written where the value is used.

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

`Some(14)` wraps a value. `None` holds nothing, so it says nothing about the type: write the type on the name, `let missing: Option[Int] = None`, as [section 2.1](/learn/numbers/#s2-1) shows for any `let`. More often an `Option` comes from a function. Two functions of the prelude on a text return one: `to_int`, which reads a whole number, and `find`, which gives the position of the first place a smaller text appears:

```una include="steps/03-option-forms/src/counts.una#L44-L48" title="steps/03-option-forms/src/counts.una"
  let sku = "LAMP-01"
  let dash = sku.find(text: "-")
  let number = sku.slice(start: 5, end: 7).to_int()
  let slash = sku.find(text: "/")
  @console.print("{dash} {number} {slash}")
```

```text include="steps/03-option-forms/expected/output.txt#L8"
Some(4) Some(1) None
```

`find` gives the position of the first `-` in `LAMP-01`, counted from 0. `to_int` reads the digits `01` as 1. `LAMP-01` has no `/`, so the last search gives `None`.

#### Both cases: `when`

A `when` ([section 4.3](/learn/kinds/#s4-3)) takes an `Option` apart, as it takes apart any sum kind. `shown` has one arm per variant: `is Some(units)` binds the value inside to the name `units`, and `is None` says what to do without one. Each arm gives a `Text`, so the `when` gives one too.

```una include="steps/03-option-forms/src/counts.una#L36" title="steps/03-option-forms/src/counts.una"
  @console.print("{shown(counted)} / {shown(missing)}")
```

```text include="steps/03-option-forms/expected/output.txt#L2"
14 on the shelf / not counted yet
```

#### One case and the rest: `else`

When only the `Some` case needs work, an `else` arm covers the other. `well_stocked` answers `false` for a missing count:

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

`count is None` is a condition, `true` or `false`, that tests the variant with `is` ([section 4.2](/learn/kinds/#s4-2)) without taking the value out. `is_some()` asks the same question the other way round:

```una include="steps/03-option-forms/src/counts.una#L39" title="steps/03-option-forms/src/counts.una"
  @console.print("{needs_count(missing)} {missing.is_some()}")
```

```text include="steps/03-option-forms/expected/output.txt#L5"
true false
```

#### A default under the line: `if none use`

`typed_units` writes the default on its own line under the call: `if none use 0`. After that line, `units` is a plain `Int`. This line is a **handling clause**. It and `if none fail`, which turns a missing value into a failure, are taught with the other clauses in [section 7.3](#s7-3).

```una include="steps/03-option-forms/src/counts.una#L40-L42" title="steps/03-option-forms/src/counts.una"
  let typed = typed_units(" 7 ")
  let spelled = typed_units("seven")
  @console.print("{typed} {spelled}")
```

```text include="steps/03-option-forms/expected/output.txt#L6"
7 0
```

### Looking up a price

The forms together, in a price lookup. `find_product` makes the option, `price_of` passes the absence on to its caller, and `label` decides what it means:

:::steps
```una include="steps/01-option/src/lookup.una" title="steps/01-option/src/lookup.una" verified="check, run"
module lookup

--- A product the store sells, with the price of one unit in cents.
kind Product
  sku: Text
  cents: Int

--- The product with the SKU `sku`, or `None` when the store does not sell it.
find_product(sku: Text) -> Option[Product]
=
  if sku == "LAMP-01"
    Some(Product(sku: "LAMP-01", cents: 1990))
  else if sku == "DESK-02"
    Some(Product(sku: "DESK-02", cents: 15900))
  else
    None

--- The price of `sku`, or `None` when the store does not sell it.
price_of(sku: Text) -> Option[Int]
=
  let found = find_product(sku)
  when found
    is Some(product) -> Some(product.cents)
    is None -> None

--- What a product page shows for `sku`.
label(sku: Text) -> Text
=
  let price = price_of(sku)
  when price
    is Some(cents) -> "{sku}: {cents} cents"
    is None -> "{sku}: not sold here"

--- Prints two product pages, and three values that may be missing.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(label("DESK-02"))
  @console.print(label("CHAIR-09"))
  let missing = price_of("CHAIR-09")
  @console.print("{missing} or {missing.or_else(default: 0)}")
  let typed = "3".to_int()
  let dash = "LAMP-01".find(text: "-")
  @console.print("{typed} and {dash}")
```

1. **`find_product(sku: Text) -> Option[Product]`.** A function of your own that returns an `Option`: `Some` with the product for the two SKUs the store sells, and `None` for any other. Each branch of the `if` ([section 3.4](/learn/text-and-conditions/#s3-4)) gives an `Option[Product]`.
2. **`when found`.** One arm per case, `is Some(product)` and `is None`. The name in `Some(product)` binds the value inside.
3. **`Some(product.cents)`.** `price_of` itself returns an `Option`, so its caller decides what a missing price means. `label` decides: it prints "not sold here".
4. **`missing.or_else(default: 0)`.** The short form when a default is right: the value inside `Some`, or the default for `None`.
5. **`"3".to_int()` and `"LAMP-01".find(text: "-")`.** Two functions of the prelude that return an `Option`.
:::

`una run .` prints:

```text include="steps/01-option/expected/output.txt"
DESK-02: 15900 cents
CHAIR-09: not sold here
None or 0
Some(3) and Some(4)
```

An `Option` is printed as `Some(3)` or `None`, which helps while you look for a mistake, but a report should say what the absence means, as `label` does.

### How an `Option` behaves

#### A `when` covers both cases

A `when` over an `Option` must have an arm for `Some` and one for `None`, or an `else`. Leave the `None` arm out of `shown`, and `una check .` reports:

```text include="steps/04-no-none-arm/expected/rendered.txt"
[U2007] Error: `when` does not match variant `None` of `Option`
   ╭─[ src/counts.una:6:3 ]
   │
 6 │   when count
   │   ──┬─
   │     ╰─── `when` does not match variant `None` of `Option`
   │
   │ Help: repair 1: add an arm for each missing variant, such as `is None`, or an `else` arm
   │
   │ Note: run `una explain U2007` for an explanation
───╯
```

The message names the variant that has no arm, `None`, and the mark points at the `when`. The `Help` line gives both repairs: an arm `is None`, or an `else` arm. So when the day comes that a value is missing, the program already says what to do.

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
> The default of `or_else` is an argument like any other, so it is computed before the call, whether it is used or not. Keep it a plain value, such as `0` or `"other"`. A call that prints or can fail cannot be the default: give its result a name with `let` first.

### Choosing how to use an `Option`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Do different things when the value is there and when it is not | `when` with `is Some(v)` and `is None` |
| Work only on the value, with one answer for the rest | `when` with `is Some(v)` and `else` |
| Carry on with a default | `or_else(default: v)`, or `if none use v` on the line under the call ([section 7.3](#s7-3)) |
| Know only whether there is a value | `is_some()`, or `o is None` in a condition |
| Make a missing value a failure of your function | `if none fail V` ([section 7.3](#s7-3)) |
:::

Prefer a `when` when the absence needs its own words, as on a product page. Prefer `or_else` when the default is the honest answer, as 0 units on a shelf nobody stocked.

### Check yourself: `Option`

The three functions of [How to write and use an `Option`](#how-to-write-and-use-an-option) get one more set of counts:

```una include="steps/03-option-forms/src/counts.una#L49" title="steps/03-option-forms/src/counts.una"
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

A **failure** is a function's way of saying "I could not do this, and here is why", instead of giving back a value. Think of a card terminal at a till. Most of the time it says "approved". Sometimes it prints a slip that says "declined", or "card expired in March". The slip is not a price, and nobody mistakes it for one; it says what went wrong, with what the cashier needs to act on it.

In Una a failure is a value too, of a kind you declare. A few words name the parts, and the rest of this chapter uses them:

- An **error kind** is a sum kind ([section 4.2](/learn/kinds/#s4-2)) whose variants are the ways a function can fail: `NotANumber`, `TooSmall`, `TooLarge`. A variant may carry data, such as the text that was not a number.
- `fails QuantityError`, a line of a function's header, says that the function can fail, and with which kind. The **header** is the line with the function's name, parameters and result type, and the lines under it up to `=` ([section 6.2](/learn/functions/#s6-2)).
- `fail TooSmall(value: n)` ends the function with that variant, instead of a value.
- The function's **caller**, the code that called it, must then say what to do with a failure: carry on, pass it on, or turn it into its own. [Section 7.3](#s7-3) shows how.

### Why a function declares its failures

Take the quantity a customer types into an order form. It must be a whole number from 1 to 99. Without a way to fail, a function that reads it must still give back a number, so it gives 0 for anything it cannot use:

```una include="steps/05-sentinel/src/quantity.una" title="steps/05-sentinel/src/quantity.una" verified="check, run"
module quantity

--- The quantity typed into an order form: a whole number from 1 to 99. Any other text gives
--- 0, so the caller cannot tell a bad quantity from what went wrong with it.
quantity_or_zero(raw: Text) -> Int
=
  let n = raw.trim.to_int().or_else(default: 0)
  if n < 1 or n > 99 then 0 else n

--- One line of an order form: the typed text, the units, and the price of that many lamps.
priced(raw: Text) -> Text
=
  let units = quantity_or_zero(raw)
  "'{raw}': {units} units, {units * 1990} cents"

--- Prints four typed quantities, priced.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(priced("3"))
  @console.print(priced("three"))
  @console.print(priced("0"))
  @console.print(priced("500"))
```

`una run .` prints:

```text include="steps/05-sentinel/expected/output.txt"
'3': 3 units, 5970 cents
'three': 0 units, 0 cents
'0': 0 units, 0 cents
'500': 0 units, 0 cents
```

The program runs, and three different problems come out the same way: a word, a zero, and a number too large all become "0 units, 0 cents". The caller cannot tell them apart, so it cannot tell the customer what to fix. Worse, 0 looks like a quantity, so code that forgets to check for it prices an empty order and carries on. A value used to mean "no value", such as this 0, is called a **sentinel**, and nothing in the type tells a caller to check for it.

A declared failure fixes both problems. The header says that the function can fail and with which kind, so a reader sees it without reading the body. Each way to fail is a variant of its own, with the data a message needs. And the checker refuses a call that does not say what to do when the function fails.

### A function that fails: `parse_quantity`

Here is the quantity again, with a failure. The module declares the error kind, a function that fails with it, and a `main` that calls the function twice, once with good input and once with bad:

:::steps
```una include="steps/06-quantity/src/quantity.una" title="steps/06-quantity/src/quantity.una" verified="check, run"
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

--- Reads two typed quantities, one good and one bad.
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
3. **`raw.trim.to_int()` then `if none fail NotANumber(raw)`.** `to_int` returns an `Option[Int]` ([section 7.1](#s7-1)): `None` when the text is not a number. The clause on the next line turns `None` into a failure of this function. After it, `n` is a plain `Int`.
4. **`fail TooSmall(value: n)`.** This ends the function with that variant. `fail` can stand in any branch of an `if`, and the other branches give the value.
5. **`if error use 0`.** In `main`, each call is followed by a handling clause, on its own line, indented under the call. Here it carries on with `0`. [Section 7.3](#s7-3) shows the others.
:::

`una run .` prints:

```text include="steps/06-quantity/expected/output.txt"
3 and 0
```

The first call returns `3`. The second fails with `NotANumber`, and its clause carries on with `0`. Here `main` chose 0 on purpose, at the call, where a reader sees it: the function itself no longer hides the failure.

### How to write an error kind and `fail`

The step of this part is a card payment, with each form of an error kind and of `fail`:

```una include="steps/07-fail-forms/src/payment.una#ServiceError..refuse" title="steps/07-fail-forms/src/payment.una"
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
- A variant may carry fields, as `Expired(month: Int)` and `OverLimit(limit: Int, asked: Int)`, when a message or a second try needs them.
- A kind with one variant starts with `|`, as `kind ServiceError = | Timeout` does, as for any sum of one variant ([section 4.2](/learn/kinds/#s4-2)).

#### `fails` in the header

`fails PaymentError` goes on its own line under the header line, indented two spaces, before `=`, next to any `requires` or `uses` line, in the order [section 6.2](/learn/functions/#s6-2) gives. A function names one error kind at most: every way it can fail is a variant of that kind.

#### `fail` in a branch

`charge` fails in the `if` branch and gives a value in the `else` branch:

```una include="steps/07-fail-forms/src/payment.una#charge" title="steps/07-fail-forms/src/payment.una"
--- The amount charged: `fail` in one branch of an `if`, the value in the other.
charge(cents: Int, limit: Int) -> Int
  fails PaymentError
=
  if cents > limit
    fail OverLimit(limit: limit, asked: cents)
  else
    cents
```

`fail OverLimit(limit: limit, asked: cents)` names the variant and gives each field by its label. When a variant has one field, its value may be given without the label, as `fail Expired(month)` in `valid_until` does. And a bare name that equals a field's name counts as that field's label, so `BadShelf(shelf, cause: error)` in [section 7.3](#s7-3) is `BadShelf(shelf: shelf, cause: error)`.

#### `fail` as the whole body

A function that always fails, such as a stand-in for a card terminal that is offline, has `fail` as its whole body, on its own line after `=`:

```una include="steps/07-fail-forms/src/payment.una#always_down" title="steps/07-fail-forms/src/payment.una"
--- A payment service that is always down: `fail` as the whole body.
always_down(cents: Int) -> Int
  fails ServiceError
=
  fail Timeout
```

#### Failing on a missing value: `if none fail`

`if none fail NotANumber(raw)`, in `parse_quantity`, is the short way to fail when a value is missing: it stands on the line under an expression that gives an `Option`. [Section 7.3](#s7-3) covers it with the other clauses.

#### The forms, run

`main` calls each function once with a value that works and once with one that fails, and carries on with `0` after every failure:

```una include="steps/07-fail-forms/src/payment.una#L40-L55" title="steps/07-fail-forms/src/payment.una"
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

```text include="steps/07-fail-forms/expected/output.txt#L1"
4500 0 11 0 0 0
```

`charge` gives 4500 under the limit and fails over it; `valid_until` gives 11 for a card that expires next month and fails for one that expired in March; the last two always fail.

### How a failure behaves

#### `fail` ends the function

`fail` ends the function at once, as giving back a value does: no line after it runs, and the function gives no value. The caller's clause decides what happens next.

#### A function has one error kind

A function declares at most one kind in `fails`, and every `fail` in it must name a variant of that kind. To fail with a variant of another kind is U3009 ([failing with a variant of another kind](#failing-with-a-variant-of-another-kind-u3009)). When a function calls another that fails with a different kind, it translates the failure into its own, with `if error fail` ([section 7.3](#s7-3)).

#### Every call that can fail is handled

A call of a function that can fail must be followed by a clause that handles the failure, or be wrapped in `attempt` ([section 7.4](#s7-4)). Without one, the checker reports U3007 ([forgetting the clause](#forgetting-the-clause-u3007)). Nothing passes a failure on unless a line says so.

#### Public functions declare; private ones may infer

A `pub` function must declare `fails` when it can fail: its header is what other modules rely on ([section 6.3](/learn/functions/#s6-3)), and a `fail` in a `pub` function without `fails` is U3009 ([a public function that fails without saying so](#a-public-function-that-fails-without-saying-so-u3009)). A private function may leave the line out, and the checker infers it, as it infers `uses`.

`parse_quantity` is private. Remove its `fails` line:

```diff include="steps/06-quantity..steps/08-inferred:src/quantity.una" context="1" title="src/quantity.una"
--- a/src/quantity.una
+++ b/src/quantity.una
@@ -7,3 +7,2 @@
 parse_quantity(raw: Text) -> Int
-  fails QuantityError
 =
```

The program checks and prints the same thing, and `una contract` prints the header the checker inferred, marked with the comment `-- inferred`:

```text include="steps/08-inferred/expected/commands/contract.txt"
$ una contract quantity.parse_quantity
--- The quantity typed into an order form: a whole number from 1 to 99.
parse_quantity(raw: Text) -> Int
  fails QuantityError -- inferred
```

So a private function without `fails` can still fail. Its header is the inferred one. Write the line anyway whenever the failure is part of what a caller should know: this book always does.

#### What is not a failure

Some problems never reach the program as failures, because they are ruled out before it runs. A division by zero, or a call that breaks a function's `requires`, is a proof obligation that the verifier must prove ([section 5.4](/learn/contracts/#s5-4)): a program with one it cannot prove does not run. A few problems outside the program's logic, such as running out of memory, stop the run instead; [Reference](#reference) lists them.

### Failing as the function you are given: `fails of`

#### What `fails of` is

A parameter can hold a function, which the body then calls: its type, such as `fn(Text) -> Int`, says what the function takes and gives back, and a call passes a function by its name ([section 10.2](/learn/collections/#s10-2) teaches functions as values). Whether such a function can fail then depends on what it is given. Think of a cashier who rings up a cart with whatever price list the manager hands over: with the regular list, a SKU missing from it stops the sale; with a sale sign that prices everything at 5.00, nothing can go wrong. `fails of price`, a line of the header, says exactly that: this function fails when, and only when, its parameter `price` fails, and with the same kind.

#### Why a parameter's failures need a clause

The step of this part prices a cart of two SKUs with one of two price functions. `listed` knows two SKUs and fails with `NoPrice` for any other; `flat` prices everything at 500 and never fails:

```una include="steps/09-fails-of/src/pricing.una#PriceError" title="steps/09-fails-of/src/pricing.una"
--- Why a price list has no price for a SKU.
kind PriceError = | NoPrice(sku: Text)
```

```una include="steps/09-fails-of/src/pricing.una#listed..flat" title="steps/09-fails-of/src/pricing.una"
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

A parameter of the type `fn(Text) -> Int` holds a function that gives an `Int` and cannot fail. Here is a `pub` function that totals a cart with a price function, without `fails of`, called with the price list, which can fail:

```diff include="steps/09-fails-of..steps/10-no-fails-of:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -8,3 +8,2 @@
 pub total_of_two(first: Text, second: Text, price: fn(Text) -> Int) -> Int
-  fails of price
 =
```

`una check .` reports, once for each call that passes `listed`:

```text include="steps/10-no-fails-of/expected/rendered.txt#L1-L8"
[U3009] Error: this function can fail with `PriceError`, which the expected function type does not allow
    ╭─[ src/pricing.una:34:65 ]
    │
 34 │   let known = total_of_two("LAMP-01", second: "DESK-02", price: listed)
    │                                                                 ───┬──
    │                                                                    ╰──── this function can fail with `PriceError`, which the expected function type does not allow
    │
    │ Note: run `una explain U3009` for an explanation
```

The mark points at the argument, `listed`. The message says that `listed` can fail with `PriceError`, and that the type of the parameter, `fn(Text) -> Int`, allows no failure. Writing `fails PriceError` on `total_of_two` would not help: the parameter's type would still allow no failure, and every call would need a clause, even with a price function that never fails.

#### How to write `fails of`

`fails of p` goes under the header, as `fails` does, and names a parameter `p` whose type is a function type written without `fails`. In the body, a call of `p` takes a clause, and `if error pass` hands its failure on:

```una include="steps/09-fails-of/src/pricing.una#total_of_two" title="steps/09-fails-of/src/pricing.una"
--- The total of a cart of two SKUs, each priced by `price`. It fails when, and only when,
--- `price` fails, and with the same error kind.
pub total_of_two(first: Text, second: Text, price: fn(Text) -> Int) -> Int
  fails of price
=
  let first_cents = price(first)
    if error pass
  let second_cents = price(second)
    if error pass
  first_cents + second_cents
```

At each call of `total_of_two`, the failure is that of the argument. `listed` fails with `PriceError`, so a call with `listed` needs a clause; `flat` cannot fail, so a call with it needs none:

```una include="steps/09-fails-of/src/pricing.una#L35-L38" title="steps/09-fails-of/src/pricing.una"
  let known = total_of_two("LAMP-01", second: "DESK-02", price: listed)
    if error use -1
  let flat_total = total_of_two("LAMP-01", second: "VASE-03", price: flat)
  @console.print("{known} {flat_total}")
```

```text include="steps/09-fails-of/expected/output.txt#L1"
17890 1000
```

#### How `fails of` behaves

- `fails of p` exists from edition `0.2` on. Its twin for capabilities, `uses of p`, is taught in [section 12.4](/learn/capabilities/#s12-4).
- `fails E` and `fails of p` can both appear in one header. When both are there, the argument for `p` must fail with `E` (U3009 at the argument), so that the function keeps one error kind.
- A private function may leave `fails of p` out, and the checker infers it when the body only passes on the failures of `p`, as it infers `fails` ([Public functions declare; private ones may infer](#public-functions-declare-private-ones-may-infer)). That is why `total_of_two` is `pub` here: the line is what its callers rely on.
- In edition `0.2`, the prelude's functions that take a function and apply it to each element of a list declare `fails of` it ([section 10.3](/learn/collections/#s10-3)).

### A sentinel, an `Option` or a failure

:::decide
**Which to use:**

| When the function cannot give a normal answer… | Use |
| --- | --- |
| Never | a sentinel value such as 0 or -1, which a caller can mistake for an answer |
| And "no answer" is a normal outcome, with nothing more to say | an `Option` ([section 7.1](#s7-1)) |
| And the caller needs to know why, to act on it | `fails` with an error kind |
:::

A price lookup for a SKU the store does not sell gives `None`: that is a normal answer. A quantity typed as `"three"` is a failure with a reason, `NotANumber`, which a form shows to the customer.

### Check yourself: failures

Both calls fail. Predict the line:

```una include="steps/07-fail-forms/src/payment.una#L56-L60" title="steps/07-fail-forms/src/payment.una"
  let over = charge(30000, limit: 10000)
    if error use -1
  let lapsed = valid_until(3, today: 10)
    if error use 99
  @console.print("{over} {lapsed}")
```

:::answer Show the answer
```text include="steps/07-fail-forms/expected/output.txt#L2"
-1 99
```

30000 is over the limit, so `charge` runs `fail OverLimit(…)`: the function ends there and gives no value, and the clause under the call gives `-1` instead. The card expired in month 3, before month 10, so `valid_until` fails with `Expired`, and its own clause gives `99`. Each call's clause decides what a failure becomes at that call.
:::

And one about `fails of`. `VASE-03` is not in the price list:

```una include="steps/09-fails-of/src/pricing.una#L39-L41" title="steps/09-fails-of/src/pricing.una"
  let unknown = total_of_two("LAMP-01", second: "VASE-03", price: listed)
    if error use -1
  @console.print("{unknown}")
```

What does it print?

:::answer Show the answer
```text include="steps/09-fails-of/expected/output.txt#L2"
-1
```

`total_of_two` declares `fails of price`, so with `listed` it fails as `listed` does: `listed` fails with `NoPrice` for `VASE-03`, and `if error pass` hands that failure on. So the call fails, and the clause under it gives `-1`. The price of `LAMP-01` alone is never returned.
:::

## 7.3 Handling a failure: the clauses

### What a handling clause is

A **handling clause** is a line under a call that says what to do if the call fails, or if its value is missing. Think of the instructions a store leaves for a clerk: "if the lamp is out of stock, offer the next model", "if the card is declined, ask for another". The instruction sits next to the task it belongs to, and nobody has to guess.

A clause stands on its own line, indented one level under the statement it handles. Una has five, in two families:

- `if error …` handles an expression that **fails**: `if error use`, `if error pass` and `if error fail`.
- `if none …` handles a value that is **missing**, an `Option` that is `None` ([section 7.1](#s7-1)): `if none use` and `if none fail`.

The word after `if error` or `if none` is the decision: **use** a value and carry on, **pass** the failure on to your own caller, or **fail** with a variant of your own.

### Why every call needs one

Una passes no failure on by itself. A call that can fail with no clause under it does not check. Leave out the clause under `read_count`:

```diff include="steps/11-clauses..steps/12-no-clause:src/shelves.una" context="1" title="src/shelves.una"
--- a/src/shelves.una
+++ b/src/shelves.una
@@ -20,3 +20,2 @@
   let units = read_count(raw)
-    if error use 0
   units
```

`una check .` reports:

```text include="steps/12-no-clause/expected/rendered.txt"
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

"Unwrapped" means taken out of its `Some`: after the clause, the name holds a plain `Int`, not an `Option[Int]`. The step of this part has one function per clause, around a shelf count that a clerk types:

```una include="steps/11-clauses/src/shelves.una#CountError..read_count" title="steps/11-clauses/src/shelves.una"
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

```una include="steps/11-clauses/src/shelves.una#count_or_zero" title="steps/11-clauses/src/shelves.una"
--- `if error use`: carry on with 0 when the count cannot be read.
count_or_zero(raw: Text) -> Int
=
  let units = read_count(raw)
    if error use 0
  units
```

When `read_count` fails, `units` is 0, and the function goes on. `count_or_zero` cannot fail itself: the clause has handled every failure.

#### Pass it on: `if error pass`

```una include="steps/11-clauses/src/shelves.una#count_label" title="steps/11-clauses/src/shelves.una"
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

```una include="steps/11-clauses/src/shelves.una#shown" title="steps/11-clauses/src/shelves.una"
--- `if error use`, with `error` in the value: a failure becomes a sentence.
shown(raw: Text) -> Text
=
  let text = count_label(raw)
    if error use explain(error)
  text
```

Inside a clause, the name `error` holds the failure that happened, here a `CountError`. `if error use explain(error)` turns it into a sentence. `explain` is an ordinary function with a `when` over the variants, declared in the same module:

```una include="steps/11-clauses/src/shelves.una#explain" title="steps/11-clauses/src/shelves.una"
--- What a person reads about a count that could not be used.
explain(failure: CountError) -> Text
=
  when failure
    is NotCounted(shelf) -> "shelf {shelf} was not counted"
    is Unreadable(raw) -> "'{raw}' is not a count"
```

#### Translate it: `if error fail`

```una include="steps/11-clauses/src/shelves.una#audit" title="steps/11-clauses/src/shelves.una"
--- `if error fail`: a `CountError` becomes an `AuditError` that names the shelf.
audit(shelf: Text, raw: Text) -> Int
  fails AuditError
=
  read_count(raw)
    if error fail BadShelf(shelf, cause: error)
```

`audit` fails with `AuditError`, another kind, so it cannot pass a `CountError` on. `if error fail BadShelf(shelf, cause: error)` fails with its own variant instead, and keeps the original failure in the field `cause`, so nothing is lost. The clause here stands under the function's last line, the call whose value the function gives back: a clause may follow any statement that can fail, not only a `let`.

#### Carry on when a value is missing: `if none use`

```una include="steps/11-clauses/src/shelves.una#counted..required" title="steps/11-clauses/src/shelves.una"
--- `if none use`: a shelf with no count entered counts as 0.
counted(shelf: Text, entered: Option[Int]) -> Int
=
  let units = entered
    if none use 0
  units

--- `if none fail`: a shelf with no count entered is a failure.
required(shelf: Text, entered: Option[Int]) -> Int
  fails CountError
=
  let units = entered
    if none fail NotCounted(shelf)
  units
```

A clerk may not have entered a count yet, so `entered` is an `Option[Int]`. An `if none` clause may follow any expression of an `Option` type, here the parameter itself. `counted` treats a missing count as 0 units with `if none use 0`, and `required` treats it as a failure with `if none fail NotCounted(shelf)`.

#### The clauses, run

`main` calls each function. To print what `audit` failed with, it uses `attempt`, which keeps a failure as a value that can be printed, `Err(…)`; [section 7.4](#s7-4) explains it.

```una include="steps/11-clauses/src/shelves.una#L72-L83" title="steps/11-clauses/src/shelves.una"
  let typed = count_or_zero(" 7 ")
  let spelled = count_or_zero("seven")
  let three = shown("3")
  let cross = shown("x")
  @console.print("{typed} {spelled} / {three} / {cross}")
  let audited = attempt audit("A-12", raw: "seven")
  @console.print("{audited}")
  let missing = required("B-03", entered: None)
    if error use -1
  let found = counted("A-12", entered: Some(7))
  let absent = counted("B-03", entered: None)
  @console.print("{found} {absent} {missing}")
```

```text include="steps/11-clauses/expected/output.txt#L1-L3"
7 0 / 3 units / 'x' is not a count
Err(BadShelf(shelf: "A-12", cause: Unreadable("seven")))
7 0 -1
```

The second line shows translation at work: the `AuditError` names the shelf, and its `cause` keeps the `CountError` that started it.

### Translating between layers with `error`

Most programs have layers: a low-level reader, a line reader above it, a report above that. Each layer has its own error kind, because each layer knows different things. The quantity reader knows the text was not a number, and the line reader also knows the line number. `if error fail` translates, and `error` keeps the original failure as a field, so nothing is lost. This step uses a smaller `QuantityError` than [section 7.2](#s7-2), with one variant for both bounds, which is enough here:

:::steps
```una include="steps/13-translate/src/upload.una" title="steps/13-translate/src/upload.una" verified="check, run"
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
  let comma = text.find(text: ",")
    if none fail MissingQuantity(line: number)
  let raw = text.slice(start: comma + 1, end: text.len)
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

--- Shows four lines of an upload.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(show(1, text: "LAMP-01, 2"))
  @console.print(show(2, text: "LAMP-01"))
  @console.print(show(3, text: "LAMP-01, lots"))
  @console.print(show(4, text: "LAMP-01, 500"))
```

1. **`text.find(text: ",")` and `if none fail MissingQuantity(line: number)`.** `find` gives `None` when the line has no comma. That is the input's fault, so it becomes a failure. After the clause, `comma` is the comma's position.
2. **`text.slice(start: comma + 1, end: text.len)`.** The text after the comma. `slice` requires its positions to lie inside the text ([section 3.2](/learn/text-and-conditions/#s3-2)), and the verifier proves it: when `find` gives a position, it also knows that the comma ends inside the text.
3. **`if error fail BadQuantity(line: number, cause: error)`.** This is translation. `quantity_on_line` fails with `LineError`, and `parse_quantity` fails with `QuantityError`, so `if error pass` would not be allowed ([Passing a failure of another kind](#passing-a-failure-of-another-kind-u3008) shows the diagnostic). `error` is the `QuantityError` that happened, and it is kept as the `cause`.
4. **`explain` and `cause_text`.** Turning a failure into a message is an ordinary `when`. Because `when` must cover every variant, adding a variant to `LineError` later makes the checker point at every message function that needs a new arm.
5. **`attempt quantity_on_line(number, text: text)` in `show`.** `attempt` keeps the outcome as a value, `Ok(value)` or `Err(failure)`, so `show` can print a message for either. [Section 7.4](#s7-4) explains it.
:::

`una run .` prints:

```text include="steps/13-translate/expected/output.txt"
line 1: 2 units
line 2: no quantity
line 3: 'lots' is not a number
line 4: 500 is not between 1 and 99
```

### How the clauses behave

#### Each clause on its own line, in order

A clause goes on its own line, indented one level under the statement. Written on the same line, it is U0101 ([the clause on the same line](#the-clause-on-the-same-line-u0101)). A statement takes each clause at most once, and when it has both families, `if error` comes first and `if none` second: the call's failure is decided before the value it gave. The other order is U0102 ([`if none` before `if error`](#if-none-before-if-error-u0102)).

#### One call that can fail per statement

A call that can fail must be the whole expression of its statement or `let`, so that its clause handles exactly one call. Nesting it inside another call, as `check_stock(parse_order(line))`, is U3013 ([nesting a call that can fail](#nesting-a-call-that-can-fail-u3013)): give the inner call's result a name with `let` first, with its own clause.

#### What each clause requires

- `use v`: `v` has the type of the statement's value, since it takes the value's place. A value of another type, such as a text where an `Int` goes, is U2001: the message names the type expected and the type found.
- `pass`: the call fails with the same kind as your function. Another kind is U3008 ([passing a failure of another kind](#passing-a-failure-of-another-kind-u3008)).
- `fail V(...)`: `V` is a variant of your function's kind, as for any `fail`.
- `error` is a name only inside an `if error` clause, where it holds the failure.

#### A clause on a call that cannot fail

In editions `0.1` and `0.2`, which this book uses, an `if error` clause under a call that cannot fail is accepted, and never runs. In edition `0.3`, it is U3025, and `una fix` deletes it ([chapter 19](/learn/editions/)).

### Choosing a clause

:::decide
**Which to use:**

| The failure, or the missing value… | Use |
| --- | --- |
| Has a sensible value to carry on with | `if error use v` / `if none use v` |
| Is for your caller to decide, and your function fails with the same kind | `if error pass` |
| Needs your own terms, or your layer adds what it knows | `if error fail V(cause: error)` |
| Means the input is wrong | `if none fail V` |
| Must be kept to decide later, or counted | `attempt` ([section 7.4](#s7-4)) |
:::

Prefer `fail` with your own variant over `use` with a value that only looks like an answer: a sentinel such as 0 is what [section 7.2](#s7-2) set out to avoid. Use `use` when the value is honest, such as 0 units on a shelf nobody counted, or a price page that says "ask for a price".

### Check yourself: handling clauses

`shown` passes through `count_label`, and `count_or_zero` carries on with 0. Predict the line:

```una include="steps/11-clauses/src/shelves.una#L84-L86" title="steps/11-clauses/src/shelves.una"
  let padded = shown(" 12 ")
  let blank = count_or_zero("")
  @console.print("{padded} / {blank}")
```

:::answer Show the answer
```text include="steps/11-clauses/expected/output.txt#L4"
12 units / 0
```

`read_count` trims the text, so `" 12 "` reads as 12, `count_label` gives `"12 units"`, and `shown` never needs its clause. The empty text is not a number, so `read_count` fails with `Unreadable`, and the clause in `count_or_zero` gives 0.
:::

## 7.4 Failures as values: `attempt` and `Result`

### What `attempt` and `Result` are

The handling clauses of [section 7.3](#s7-3) decide on the spot, at the call. Sometimes you want to *keep* the outcome and decide later. Think of the card slips at a till at the end of the day: each slip says "approved", or "declined, and why". The clerk files every slip and counts them later; one declined card does not stop the pile.

`attempt` turns one call into such a slip. `attempt raw.parse_int()` runs the call and gives a value of the type `Result[T, E]`, a generic sum kind of the prelude with two variants:

- `Ok(value)` when the call returned, with the value, of the type `T`;
- `Err(failure)` when the call failed, with the failure, of the error kind `E`.

`attempt` itself never fails: a failure becomes an `Err`, which a `when` takes apart like any sum kind.

### Why a form needs failures as values

The examples of this section read quantities with the prelude's own failing function, `parse_int`, which turns a text into an `Int` and fails with `ParseError`, a sum kind of the prelude: `Empty` for an empty text, `NoDigits` for a sign alone, `NotADigit(at)` with the position of the first wrong character, counted from 0, and `TooLong` for more than 4300 digits. Unlike `to_int`, it says why a text is not a number. Both exist from edition `0.2` on.

An order form has three boxes for quantities. With `if error pass`, the first box that fails ends the whole function, and the boxes after it are never read:

```una include="steps/14-batch-stops/src/batch.una" title="steps/14-batch-stops/src/batch.una" verified="check, run"
module batch

--- The units of the three quantities typed into an order form, added up. One quantity that
--- is not a number fails the whole form.
total_units(first: Text, second: Text, third: Text) -> Int
  fails ParseError
=
  let first_units = first.parse_int()
    if error pass
  let second_units = second.parse_int()
    if error pass
  let third_units = third.parse_int()
    if error pass
  first_units + second_units + third_units

--- Adds up two order forms: one with three numbers, one with two that are not.
pub main() -> Unit
  uses @console: Console[print]
=
  let good = total_units("12", second: "3", third: "5")
    if error use -1
  let mixed = total_units("12", second: "", third: "3x")
    if error use -1
  @console.print("{good} and {mixed}")
```

`una run .` prints:

```text include="steps/14-batch-stops/expected/output.txt"
20 and -1
```

The first form adds up to 20. The second holds one good quantity and two bad ones, and the whole form comes out as -1: the function stopped at the empty text, the second box, and the caller cannot tell which box failed, or why, or how many were good. `if error use 0` on each box would hide the failures instead. To report every box, the program must keep each outcome, good or bad, and carry on.

### How to write `attempt`

#### `attempt` and a `let`

The usual form gives the outcome a name: `let outcome = attempt raw.parse_int()`. `attempt` is followed by exactly one call, and no clause goes under it: `attempt` is the handling.

#### `attempt` as the whole body

A function whose body is only `attempt` returns the outcome, and cannot fail itself:

```una include="steps/15-attempt/src/batch.una#parse_typed" title="steps/15-attempt/src/batch.una"
--- A typed quantity as a number, or the reason it is not one. The whole body is `attempt`.
parse_typed(raw: Text) -> Result[Int, ParseError] = attempt raw.parse_int()
```

Its result type is written out: `Result[Int, ParseError]`, the type of `parse_int`'s value and the kind it fails with.

#### Taking a `Result` apart: `when`

```una include="steps/15-attempt/src/batch.una#describe" title="steps/15-attempt/src/batch.una"
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

This step reports each of four typed quantities with the reason `ParseError` gives, and counts the good ones:

:::steps
```una include="steps/15-attempt/src/batch.una#L1-L40" title="steps/15-attempt/src/batch.una"
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
    is TooLong -> "more than 4300 digits"

--- One line of the report for a typed quantity.
describe(raw: Text, outcome: Result[Int, ParseError]) -> Text
=
  when outcome
    is Ok(value) -> "'{raw}': {value} units"
    is Err(failure) -> "'{raw}': {explain(failure)}"

--- The report line of a typed quantity: `attempt` keeps the outcome, and `describe` reads it.
report(raw: Text) -> Text
=
  let outcome = attempt raw.parse_int()
  describe(raw, outcome: outcome)

--- 1 for a typed quantity that is a number, 0 for one that is not: `is_ok` in a condition.
accepted(raw: Text) -> Int = if parse_typed(raw).is_ok() then 1 else 0

--- Reports four typed quantities, and counts the good ones.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(report("12"))
  @console.print(report(""))
  @console.print(report("-"))
  @console.print(report("3x"))
  let count = accepted("12") + accepted("") + accepted("-") + accepted("3x")
  let last = parse_typed("7")
```

1. **`parse_typed(raw: Text) -> Result[Int, ParseError] = attempt raw.parse_int()`.** The whole body is `attempt`, so the function returns the outcome and cannot fail itself.
2. **`explain`.** A `when` turns each variant of `ParseError` into words.
3. **`let outcome = attempt raw.parse_int()`, in `report`.** The usual form. Nothing fails, even for a bad quantity: the failure is a value in `outcome`, which `describe` reads.
4. **`parse_typed(raw).is_ok()`, in `accepted`.** `is_ok` says whether a `Result` is `Ok`, and the `if` turns the answer into 1 or 0, so `main` can add them up.
:::

`una run .` prints:

```text include="steps/15-attempt/expected/output.txt#L1-L5"
'12': 12 units
'': nothing was typed
'-': a sign with no digits
'3x': not a digit at position 1
1 of 4 accepted, then Ok(7)
```

Every quantity gets its line, with its own reason. The last value is printed as `Ok(7)`: a `Result` is printed like any other value of a sum kind.

### How `attempt` behaves

#### One call, the whole expression

`attempt` applies to the whole expression after it, and that expression must be one call. It is tempting to write `attempt` and a question about the outcome on one line:

```diff include="steps/15-attempt..steps/16-attempt-expression:src/batch.una" context="1" title="src/batch.una"
--- a/src/batch.una
+++ b/src/batch.una
@@ -24,3 +24,3 @@
 =
-  let outcome = attempt raw.parse_int()
+  let outcome = attempt raw.parse_int().is_ok()
   describe(raw, outcome: outcome)
```

`una check .` reports three errors. The first is the one to read:

```text include="steps/16-attempt-expression/expected/rendered.txt#L1-L8"
[U2001] Error: argument `r` of `is_ok` must be `Result[_, _]`, found `Int`
    ╭─[ src/batch.una:25:25 ]
    │
 25 │   let outcome = attempt raw.parse_int().is_ok()
    │                         ───────┬───────
    │                                ╰───────── argument `r` of `is_ok` must be `Result[_, _]`, found `Int`
    │
    │ Note: run `una explain U2001` for an explanation
```

`attempt` took the whole of `raw.parse_int().is_ok()`, which is the call `is_ok(raw.parse_int())`. Its argument `r` is the `Int` that `parse_int` gives, not a `Result`, so the types do not match. The other two errors follow from the same line: `parse_int` is now nested inside another call (U3013), and `outcome` has become a `Result` of a `Bool`. The fix is two lines: `let outcome = attempt raw.parse_int()`, then `outcome.is_ok()` where the question is asked.

#### What an `Ok` value keeps

When the outcome is `Ok`, everything the called function promises about its result in its header holds for the value, as after a direct call: its `ensures` ([section 5.2](/learn/contracts/#s5-2)), and its result type, refined kinds included. [Section 7.6](#s7-6) relies on this.

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
| Keep the outcome, to report or count it | `attempt`, then `when` or `is_ok` |
| Accept outside input that no proof can establish | `checked` ([section 7.5](#s7-5)) |
:::

### Check yourself: `attempt`

`parse_int` does not trim spaces. Predict what this prints:

```una include="steps/15-attempt/src/batch.una#L41-L42" title="steps/15-attempt/src/batch.una"
  @console.print("{count} of 4 accepted, then {last}")
  let padded = parse_typed(" 5")
```

:::answer Show the answer
```text include="steps/15-attempt/expected/output.txt#L6"
Err(NotADigit(0))
```

The space at position 0 is not a digit, so `parse_int` fails with `NotADigit(at: 0)`. `parse_typed` is an `attempt`, so the failure comes back as a value, `Err(…)`, and nothing fails: the program prints it and goes on.
:::

## 7.5 When no proof can decide: `checked` and opaque predicates

### What `checked` is

Before a program runs, Una's verifier proves facts about it, such as the condition of a refined kind wherever a value enters the kind ([section 5.3](/learn/contracts/#s5-3)). Some facts depend on data that arrives only while the program runs, such as the text a person types, and on rules the verifier cannot read. For those, `checked` tests the fact when the program runs, once, and from then on the value carries the fact in its type.

Think of a ticket check at the door of a hall. Inside, nobody asks again: being inside means the ticket was checked. A value that has passed `checked` is like a guest inside. Its type says that the test passed, and every function that takes that type can rely on it.

### Opaque predicates

#### Rules the verifier cannot read

A `reflect` predicate ([section 5.3](/learn/contracts/#s5-3)) has a body in the refinement language, which the verifier reads. Some rules cannot be written in it: "seven characters, a dash, then two digits" needs a test of each character of a text, which the solver does not decide. Such a rule goes in an **opaque predicate**, written `predicate opaque` in place of `predicate reflect`. The verifier sees only its name. Its body may be any pure expression that cannot fail, such as a call of `is_digits`, the prelude's test that every character of a text is a digit, and it runs when the program runs.

#### Where an opaque predicate may stand

An opaque predicate may be named in a kind's `where` clause, as `kind Sku = Text where well_formed(it)`, which states the fact without proving it. It is called in only two places: as the condition of `checked`, and in the body of another opaque predicate. A call anywhere else, in an `if` or in a `requires`, is U2016, as [How `checked` behaves](#how-checked-behaves) shows.

### Why a run-time test is needed

`shelf_label` takes a `Sku`, so it never prints a label for a malformed code. Pass it the text a person typed, and the verifier refuses:

```diff include="steps/17-checked..steps/18-unchecked:src/sku.una" context="1" title="src/sku.una"
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

```text include="steps/18-unchecked/expected/rendered.txt"
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

Read it from the top. The first line says that the refinement `well_formed(raw)` is refuted: the verifier cannot show the condition for this argument. The two marks show the `where` clause that asks for it and the argument that must meet it. `Note 2` is the counterexample, `Text#0`, the verifier's name for some text it knows nothing about: `raw` could be any text. The help lines are the repairs, ranked. The first three need a proof, which no one can give for text typed by a person: the verifier cannot even read the rule. The fourth is `checked`.

### How to write `checked`

`checked(value, condition) else fail V` has four parts:

1. **`value`**, the value to test, here `raw.trim`.
2. **`condition`**, written with `it` standing for the value. It is a condition of the refinement language of [section 5.3](/learn/contracts/#s5-3), or a call of an opaque predicate, so that it can run.
3. **`else fail V`**, the variant your function fails with when the test does not hold. It is a `fail` like any other, so `V` belongs to the function's error kind.
4. **The result**, when the test holds: the value, with a type refined by the condition. Given back where a `Sku` is expected, it is a `Sku`.

### A checked SKU parser

The step's module turns outside text into a `Sku` with `checked`, then prints a shelf label for a well-formed SKU and `not a sku: lamp 1` for the bad input:

```una include="steps/17-checked/src/sku.una" title="steps/17-checked/src/sku.una" verified="check, run"
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

--- Shows four typed SKUs.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(show("LAMP-01"))
  @console.print(show("lamp 1"))
  @console.print(show(" LAMP-02 "))
  @console.print(show("RUG-07"))
```

`una run .` prints:

```text include="steps/17-checked/expected/output.txt#L1-L2"
sku LAMP-01
not a sku: lamp 1
```

`parse_sku` trims the text, then `checked` tests `well_formed(it)` on it, with `it` standing for the trimmed text. When the test holds, the result has the kind `Sku`; when it does not, `parse_sku` fails with `NotASku`, like any `fail`. `show` keeps the outcome with `attempt` ([section 7.4](#s7-4)), and its `is Err` arm needs no name for the failure, since `SkuError` has one variant.

### How a value gets an opaque fact

The verifier can never prove an opaque predicate, since it cannot read the body. So in code, a value gets its fact from `checked`, at run time. Here is a second rule of this kind, a barcode scanned at the till:

```una include="steps/20-opaque/src/barcodes.una" title="steps/20-opaque/src/barcodes.una" verified="check, run"
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

--- Shows two scans.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(describe("4006381333931"))
  @console.print(describe("12-34"))
```

```text include="steps/20-opaque/expected/output.txt"
4006381333931: 1990 cents
not a barcode: 12-34
```

`read_barcode` is the only way to make a `Barcode` from a text, and `price_tag` takes a `Barcode`, so a price tag is never printed for a scan that failed the test. The predicate runs once, inside `checked`, and the type carries its answer from there.

### The escape budget

> [!WARNING]
> `checked` replaces a proof with a test, so `una.toml` limits how many uses each module may have, and `una report .` counts them under `escapes`.

```toml include="steps/17-checked/una.toml" title="steps/17-checked/una.toml"
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

The table `[escape_budget]` is the **escape budget**: `checked_per_module = 1` allows one use in each module. It is a line of the manifest, so raising it is a change a reviewer sees. `una report .` lists the use, next to the budget:

```text include="steps/17-checked/expected/commands/report.txt#L2,L10-L11"
package sku 0.1.0
escapes:
  sku: 1 checked, budget 1
```

Without an `[escape_budget]` table the budget is 0. Remove the table, and the first `checked` in a module does not check:

```text include="steps/19-no-budget/expected/rendered.txt#L1,L8-L12"
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

#### A failed test is an ordinary failure

When the condition does not hold, the function fails with the variant after `else fail`, and its callers handle that failure with the clauses of [section 7.3](#s7-3), or with `attempt`.

#### Calling an opaque predicate elsewhere

Call `is_barcode` in an `if`, and `una check .` refuses:

```diff include="steps/20-opaque..steps/21-opaque-call:src/barcodes.una" context="1" title="src/barcodes.una"
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

```text include="steps/21-opaque-call/expected/rendered.txt"
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
| How a value gets the fact | proven, where it enters the kind | `checked` at run time |
| Called in code | anywhere | only inside `checked` and other opaque bodies |

### A proof, a guard or `checked`

:::decide
**Which to use:**

| The fact… | Use |
| --- | --- |
| Follows from what the code already knows | nothing: the verifier proves it |
| Is the caller's to keep, such as "never 0 months" | `requires` ([section 5.1](/learn/contracts/#s5-1)) |
| Holds of every value of a type, wherever it goes | a refined kind for the parameter or the result ([section 5.3](/learn/contracts/#s5-3)) |
| Can be tested with a condition of the refinement language | a guard: an `if` that handles the other values, as [section 7.6](#s7-6) shows |
| Depends on outside data and a rule the verifier cannot read | `checked` with an opaque predicate, within the budget |
:::

Prefer a guard to `checked` whenever the condition is in the refinement language: a guard needs no budget, and the verifier proves the code around it. Use `checked` when it is not: the test then runs, fails with a reason, and is listed for review.

### Check yourself: `checked`

`well_formed` wants seven characters, a dash at position 4, and two digits. What do these two lines print?

```una include="steps/17-checked/src/sku.una#L33-L34" title="steps/17-checked/src/sku.una"
  @console.print(show(" LAMP-02 "))
  @console.print(show("RUG-07"))
```

:::answer Show the answer
```text include="steps/17-checked/expected/output.txt#L3-L4"
sku LAMP-02
not a sku: RUG-07
```

`parse_sku` tests the trimmed text, so the spaces around `LAMP-02` do not matter, and the label shows the trimmed SKU, the value `checked` gave back. `RUG-07` has six characters, so the test fails, `parse_sku` fails with `NotASku`, and `show` prints its `Err` arm.
:::

## 7.6 Data from outside: checking it once

### Where the program meets the world

Inside a program, contracts are checked where code meets code. At each call, the caller proves the callee's `requires` and gets its `ensures` in return. A refined kind is a meeting point too: a value is checked once, where it enters the kind, and every function after that may rely on it.

A **boundary** is where the program meets something it does not control: text typed by a person, a line of a file, a field sent by another system. No proof can say what a person will type. So at the boundary, the program tests the data once, and gives it a refined kind if it passes. (The rules a contract comes from, such as a billing policy, cross a boundary too; [section 5.5](/learn/contracts/#s5-5) records them.)

Think of the receiving dock of a warehouse. Goods arrive from many suppliers, and each delivery is checked once, at the dock, against the order. Inside the warehouse, nobody checks the boxes again: a box on a shelf has passed the dock.

### Why outside data needs a check

A discount rate is typed into the back office as text. Here is a function that turns the text into a `Percent`, and checks only that it is a number:

```una include="steps/22-unchecked-rate/src/rates.una#Percent..parse_rate" title="steps/22-unchecked-rate/src/rates.una"
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

```text include="steps/22-unchecked-rate/expected/rendered.txt"
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

The goal is the condition of `Percent` for the returned value: `result in 0..100`. The counterexample says what the solver tried: `raw = Text#1`, some text, and `result = 101`. The solver does not know what `to_int` gives for that text, beyond an `Int`, so 101 is possible. That is the honest answer: a person can type `101`, or `-5`, or `150`.

Without the check, the program has two bad choices. It can trust the text, and carry a "percent" of 150 into every function that computes a price. Or every function that receives a rate can test it again, and one of them will forget. Una takes a third way: one function checks, and gives the value its kind.

### How to check data once

A function at the boundary takes the raw value, tests it, and either gives it back with its refined kind or fails. The step of this part shows the two ways to test:

```una include="steps/23-check-forms/src/rates.una#Percent..by_check" title="steps/23-check-forms/src/rates.una"
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

```toml include="steps/23-check-forms/una.toml" title="steps/23-check-forms/una.toml"
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

`by_check` writes the test as `checked(n, it in 0..100) else fail OutOfRange(value: n)`: the value, the condition with `it` for the value, and the failure ([section 7.5](#s7-5)). It counts against the module's escape budget, so its `una.toml` allows one.

#### Running the forms

```text include="steps/23-check-forms/expected/output.txt"
guard: Ok(15) Err(OutOfRange(150))
checked: Ok(15) Err(OutOfRange(-5))
```

Both forms give the same results here. The guard is the better choice when, as here, the test is in the refinement language: it needs no budget. `checked` is for a test the solver cannot follow, such as the format of a SKU.

### A discount rate typed in the back office

Now a whole boundary: the back office types a rate, and the program tells a number from text that is not one, and a rate in range from one out of it:

:::steps
```una include="steps/24-boundary/src/rates.una" title="steps/24-boundary/src/rates.una" verified="check, run"
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

--- Shows three typed rates.
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
5. **`attempt parse_rate(raw)`.** In the `Ok(rate)` arm, `rate` is a `Percent`, with its fact, as after a direct call ([What an `Ok` value keeps](#what-an-ok-value-keeps)).
:::

`una run .` prints:

```text include="steps/24-boundary/expected/output.txt"
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

A boundary function fails with a reason, rather than giving back `None`. The reason tells a person what to fix. And in edition `0.2` an `Option[Percent]` is not even allowed: a refined kind cannot be a type argument, as [Refinements of refinements, and type arguments](/learn/contracts/#refinements-of-refinements-and-type-arguments) says.

### Check yourself: boundaries

Someone adds a function to the back-office module of [A discount rate typed in the back office](#a-discount-rate-typed-in-the-back-office). It reads a rate from text and passes it straight on, without `parse_rate`:

```una include="steps/25-quick-rest/src/rates.una#quick_rest" title="steps/25-quick-rest/src/rates.una"
--- A rest computed from typed text, without `parse_rate`.
quick_rest(raw: Text) -> Percent
=
  let n = raw.trim.to_int()
    if none use 0
  rest_of(n)
```

Does it check? If not, what is the obligation, and what is the fix?

:::answer Show the answer
It does not check:

```text include="steps/25-quick-rest/expected/rendered.txt#L1,L18"
[U5001] Error: refinement `n in 0..100` is refuted
    │ Note 2: counterexample: n = 101, raw = Text#1, raw.len = 0
```

`rest_of` takes a `Percent`, so the call raises a refinement obligation: `n in 0..100`. Nothing tells the verifier what `to_int` gave back, so it refutes the goal with a value out of range, 101, as in [Why outside data needs a check](#why-outside-data-needs-a-check). The fix is the boundary itself: get the rate from `parse_rate`, with `attempt` or a handling clause, and pass on the `Percent` it gives back. The checker leaves no other way in.
:::

## 7.7 Day-to-day: order intake

### What the program must do

Now the program from [What you'll build](#what-youll-build). Orders arrive as lines of text, such as `LAMP-01, 2`. Each line must have a comma, a whole number of at least 1 after it, and a SKU the store's stock list knows, and it must ask for no more units than are on hand. A shelf that is being counted has no count for now. Every line gets its own report line, and a rejected line says why, in words an operator can act on.

The design follows from that, and each part uses one section of this chapter: one error kind for the order layer, `OrderError`, whose variants carry what an operator needs ([section 7.2](#s7-2)); one for the stock list, `StockError`, which the order layer translates with a clause ([section 7.3](#s7-3)); an `Option` for a SKU the stock list does not know ([section 7.1](#s7-1)); and `attempt` around each line, so that every line gets its report ([section 7.4](#s7-4)). Every function except `main` is pure: it only computes, so each one can be tested with a plain example.

### The kinds and the stock list

```una include="day-to-day/src/orders.una#Order..on_hand" title="day-to-day/src/orders.una" caption="the kinds and the stock list"
--- One line of an order: a stock-keeping unit (SKU) and how many of it.
pub kind Order
  sku: Text
  quantity: Int

--- Why an order line was rejected. Each variant carries what a person needs to act on it.
pub kind OrderError = Malformed(line: Text) | BadQuantity(line: Text) | UnknownSku(sku: Text) | OutOfStock(sku: Text, wanted: Int, left: Int) | Unavailable(sku: Text)

--- Why the stock list cannot give a count.
pub kind StockError = | BeingCounted(sku: Text)

--- The units on hand of a SKU, `None` for a SKU the store does not sell. It fails while the
--- SKU's shelf is being counted.
pub on_hand(sku: Text) -> Option[Int]
  fails StockError
=
  if sku == "LAMP-01"
    Some(4)
  else if sku == "DESK-02"
    Some(1)
  else if sku == "RUG-07"
    fail BeingCounted(sku)
  else
    None
```

`OutOfStock` carries the SKU, the units wanted and the units left, which is everything the report line needs. `Unavailable` carries the SKU whose shelf is being counted, since the operator's action is to retry that line later.

`on_hand` is the store's stock list, written as a function. Its result says two things at once. `Some(4)` is a count, and `None` means that the store does not sell the SKU: a normal answer. A failure, `BeingCounted`, means that the stock list cannot answer for now: the shelf of `RUG-07` is being counted. In a larger program the counts would come from a file or a service, [chapter 12](/learn/capabilities/) shows how; the rest of the program would not change.

### Parsing, a step on the text alone

`parse_order` only looks at the text. Each problem with the text becomes its own variant: `if none fail` for a part that is missing, and `fail` in a branch for a quantity below 1.

```una include="day-to-day/src/orders.una#parse_order" title="day-to-day/src/orders.una"
--- Reads `"SKU, quantity"`. It only looks at the text.
pub parse_order(line: Text) -> Order
  fails OrderError
=
  let comma = line.find(text: ",")
    if none fail Malformed(line)
  let sku = line.slice(start: 0, end: comma).trim
  let quantity = line.slice(start: comma + 1, end: line.len).trim.to_int()
    if none fail BadQuantity(line)
  if quantity < 1
    fail BadQuantity(line)
  else
    Order(sku: sku, quantity: quantity)
```

`find` gives the position of the comma, or `None` when the line has none. The SKU is the text before the comma, and the quantity the text after it, each trimmed. The verifier proves both `slice` calls, since `find` tells it that the comma lies inside the line.

### Checking stock, a step with two clauses

Two clauses handle the one call: the stock list's failure becomes `Unavailable`, and an unknown SKU becomes `UnknownSku`. After them, `left` is a plain `Int`, and the comparison with the quantity wanted is ordinary code. `check_stock` gives back the order unchanged when there is enough stock, so the next step can use it.

```una include="day-to-day/src/orders.una#check_stock" title="day-to-day/src/orders.una"
--- Confirms that the stock list holds enough units of the order's SKU.
pub check_stock(order: Order) -> Order
  fails OrderError
=
  let left = on_hand(order.sku)
    if error fail Unavailable(sku: order.sku)
    if none fail UnknownSku(sku: order.sku)
  if order.quantity > left
    fail OutOfStock(sku: order.sku, wanted: order.quantity, left: left)
  else
    order
```

The two clauses are in the fixed order: `if error` first, for the call's failure, then `if none`, for the value it gave.

### Composing the steps

Both steps fail with `OrderError`, the same kind as `accept`, so `if error pass` hands their failures on unchanged. The order of the two statements is the order of the work: a line that does not parse never reaches the stock list.

```una include="day-to-day/src/orders.una#accept" title="day-to-day/src/orders.una"
--- One line, from text to an order that can be shipped.
pub accept(line: Text) -> Order
  fails OrderError
=
  let order = parse_order(line)
    if error pass
  check_stock(order)
    if error pass
```

### The report

`reason` has one arm per variant. If `OrderError` gains a variant, the checker reports this `when` until it has an arm for it ([exercise 1](#exercise-1-a-per-line-limit) shows this). `reason` writes the fields of each variant into its sentence, which is why each variant carries what it does: an operator who reads `3 of DESK-02 wanted, 1 left` knows what to change.

```una include="day-to-day/src/orders.una#reason..report" title="day-to-day/src/orders.una"
--- What a person reads in the report.
pub reason(failure: OrderError) -> Text
=
  when failure
    is Malformed(line) -> "cannot read the line '{line}'"
    is BadQuantity(line) -> "the quantity in '{line}' is not a whole number above 0"
    is UnknownSku(sku) -> "no product has the SKU {sku}"
    is OutOfStock(sku, wanted, left) -> "{wanted} of {sku} wanted, {left} left"
    is Unavailable(sku) -> "the shelf of {sku} is being counted; retry later"

--- One line of the report: the order line accepted, or the reason it was not.
pub report(line: Text) -> Text
=
  let outcome = attempt accept(line)
  when outcome
    is Ok(order) -> "ok      {order.quantity} x {order.sku}"
    is Err(failure) -> "reject  {reason(failure)}"
```

`report` is where [section 7.4](#s7-4) pays off. `attempt` keeps the outcome of `accept`, so `report` itself never fails: its header has no `fails`, and that is a promise to its callers. Every line gets a report line, accepted or rejected, with the reason.

### Running it

`main` reports one line of each kind:

```una include="day-to-day/src/orders.una#main" title="day-to-day/src/orders.una"
--- Prints the report of the day's order lines.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(report("LAMP-01, 2"))
  @console.print(report("DESK-02, 3"))
  @console.print(report("CHAIR-09, 1"))
  @console.print(report("RUG-07, 1"))
  @console.print(report("LAMP-01, two"))
  @console.print(report("LAMP-01"))
```

In the `day-to-day` directory:

```sh
una check .
una run .
```

`una run .` prints the report shown in [What you'll build](#what-youll-build). The order lines here are literals, one for each outcome: a line in stock, too many units, an unknown SKU, a shelf being counted, a quantity in words and a line with no comma. `report` pads `ok` and `reject` to the same width, so the reasons line up.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/orders.una" title="day-to-day/src/orders.una" caption="the whole program" verified="check, run, test"
module orders

--- One line of an order: a stock-keeping unit (SKU) and how many of it.
pub kind Order
  sku: Text
  quantity: Int

--- Why an order line was rejected. Each variant carries what a person needs to act on it.
pub kind OrderError = Malformed(line: Text) | BadQuantity(line: Text) | UnknownSku(sku: Text) | OutOfStock(sku: Text, wanted: Int, left: Int) | Unavailable(sku: Text)

--- Why the stock list cannot give a count.
pub kind StockError = | BeingCounted(sku: Text)

--- The units on hand of a SKU, `None` for a SKU the store does not sell. It fails while the
--- SKU's shelf is being counted.
pub on_hand(sku: Text) -> Option[Int]
  fails StockError
=
  if sku == "LAMP-01"
    Some(4)
  else if sku == "DESK-02"
    Some(1)
  else if sku == "RUG-07"
    fail BeingCounted(sku)
  else
    None

--- Reads `"SKU, quantity"`. It only looks at the text.
pub parse_order(line: Text) -> Order
  fails OrderError
=
  let comma = line.find(text: ",")
    if none fail Malformed(line)
  let sku = line.slice(start: 0, end: comma).trim
  let quantity = line.slice(start: comma + 1, end: line.len).trim.to_int()
    if none fail BadQuantity(line)
  if quantity < 1
    fail BadQuantity(line)
  else
    Order(sku: sku, quantity: quantity)

--- Confirms that the stock list holds enough units of the order's SKU.
pub check_stock(order: Order) -> Order
  fails OrderError
=
  let left = on_hand(order.sku)
    if error fail Unavailable(sku: order.sku)
    if none fail UnknownSku(sku: order.sku)
  if order.quantity > left
    fail OutOfStock(sku: order.sku, wanted: order.quantity, left: left)
  else
    order

--- One line, from text to an order that can be shipped.
pub accept(line: Text) -> Order
  fails OrderError
=
  let order = parse_order(line)
    if error pass
  check_stock(order)
    if error pass

--- What a person reads in the report.
pub reason(failure: OrderError) -> Text
=
  when failure
    is Malformed(line) -> "cannot read the line '{line}'"
    is BadQuantity(line) -> "the quantity in '{line}' is not a whole number above 0"
    is UnknownSku(sku) -> "no product has the SKU {sku}"
    is OutOfStock(sku, wanted, left) -> "{wanted} of {sku} wanted, {left} left"
    is Unavailable(sku) -> "the shelf of {sku} is being counted; retry later"

--- One line of the report: the order line accepted, or the reason it was not.
pub report(line: Text) -> Text
=
  let outcome = attempt accept(line)
  when outcome
    is Ok(order) -> "ok      {order.quantity} x {order.sku}"
    is Err(failure) -> "reject  {reason(failure)}"

--- Prints the report of the day's order lines.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(report("LAMP-01, 2"))
  @console.print(report("DESK-02, 3"))
  @console.print(report("CHAIR-09, 1"))
  @console.print(report("RUG-07, 1"))
  @console.print(report("LAMP-01, two"))
  @console.print(report("LAMP-01"))

example "a line in stock is accepted"
  do accept("LAMP-01, 2")
  expect result == Order(sku: "LAMP-01", quantity: 2)

example "the spaces around the SKU and the quantity do not matter"
  do parse_order(" DESK-02 , 1 ")
  expect result == Order(sku: "DESK-02", quantity: 1)

example "a line without a comma is Malformed"
  do accept("LAMP-01")
  expect fails Malformed

example "a quantity that is not a number is BadQuantity"
  do accept("LAMP-01, two")
  expect fails BadQuantity

example "a quantity of 0 is BadQuantity"
  do accept("LAMP-01, 0")
  expect fails BadQuantity

example "a SKU the stock list does not know is UnknownSku"
  do accept("CHAIR-09, 1")
  expect fails UnknownSku

example "a shelf being counted is Unavailable"
  do accept("RUG-07, 1")
  expect fails Unavailable

example "too many units are out of stock"
  do accept("LAMP-01, 9")
  expect fails OutOfStock

example "the report says how many units are left"
  do report("DESK-02, 3")
  expect result == "reject  3 of DESK-02 wanted, 1 left"
```

## 7.8 Testing it

### One example per path

Each way `accept` can end is a **path**: it gives back an order, or it fails with one of the variants of `OrderError`. Every path gets an example, and since every function here is pure, each example is one call and one `expect` line, with nothing to set up. Each example states one fact, so when one fails, `una test .` names it and says which `expect` line did not hold, as [the exercises](#s7-10) show.

### The accepted line: `expect result`

```una include="day-to-day/src/orders.una#L92-L98" title="day-to-day/src/orders.una" caption="the accepted lines"
example "a line in stock is accepted"
  do accept("LAMP-01, 2")
  expect result == Order(sku: "LAMP-01", quantity: 2)

example "the spaces around the SKU and the quantity do not matter"
  do parse_order(" DESK-02 , 1 ")
  expect result == Order(sku: "DESK-02", quantity: 1)
```

`expect result == Order(…)` compares the whole order that the call gave back with the one it should be: two records are equal when every field is ([section 4.1](/learn/kinds/#s4-1)). The second example calls `parse_order` alone, to show that the spaces around both parts are trimmed.

### The failure paths: `expect fails`

```una include="day-to-day/src/orders.una#L100-L122" title="day-to-day/src/orders.una" caption="the failure paths"
example "a line without a comma is Malformed"
  do accept("LAMP-01")
  expect fails Malformed

example "a quantity that is not a number is BadQuantity"
  do accept("LAMP-01, two")
  expect fails BadQuantity

example "a quantity of 0 is BadQuantity"
  do accept("LAMP-01, 0")
  expect fails BadQuantity

example "a SKU the stock list does not know is UnknownSku"
  do accept("CHAIR-09, 1")
  expect fails UnknownSku

example "a shelf being counted is Unavailable"
  do accept("RUG-07, 1")
  expect fails Unavailable

example "too many units are out of stock"
  do accept("LAMP-01, 9")
  expect fails OutOfStock
```

`expect fails OutOfStock` holds when the `do` call failed with that variant, and the example fails when the call returned instead. [Section 14.2](/learn/testing/#s14-2) covers `expect fails` in full. There is one example for each variant of `OrderError`, and two for `BadQuantity`, since a quantity can be wrong in two ways: not a number, or below 1. A `do` line needs no handling clause: the example itself catches the failure.

### The report line

```una include="day-to-day/src/orders.una#L124-L126" title="day-to-day/src/orders.una" caption="the report"
example "the report says how many units are left"
  do report("DESK-02, 3")
  expect result == "reject  3 of DESK-02 wanted, 1 left"
```

One example checks the whole text of a report line, so that a change to a message, or to the fields it uses, shows up.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L12"
example orders "a line in stock is accepted" ... ok
example orders "the spaces around the SKU and the quantity do not matter" ... ok
example orders "a line without a comma is Malformed" ... ok
example orders "a quantity that is not a number is BadQuantity" ... ok
example orders "a quantity of 0 is BadQuantity" ... ok
example orders "a SKU the stock list does not know is UnknownSku" ... ok
example orders "a shelf being counted is Unavailable" ... ok
example orders "too many units are out of stock" ... ok
example orders "the report says how many units are left" ... ok

9 examples: 9 passed, 0 failed
```

## 7.9 Common mistakes

Each mistake is a small change to `day-to-day/src/orders.una`, followed by what `una check .` reports.

### Forgetting the clause (U3007)

:::mistake
Remove `if error pass` under `let order = parse_order(line)`:

```diff include="day-to-day..mistakes/1:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -58,3 +58,2 @@
   let order = parse_order(line)
-    if error pass
   check_stock(order)
```

```text include="mistakes/1/expected/rendered.txt"
[U3007] Error: `parse_order` can fail with `OrderError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
    ╭─[ src/orders.una:58:15 ]
    │
 58 │   let order = parse_order(line)
    │               ────────┬────────
    │                       ╰────────── `parse_order` can fail with `OrderError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
    │
    │ Note: run `una explain U3007` for an explanation
────╯
```

*Why:* in languages with exceptions, a failure travels up by itself, so leaving the call bare feels natural. In Una nothing passes a failure on by itself. The message names the call, `parse_order`, and the kind it fails with, `OrderError`, and the mark covers the call. Its last part lists the two ways to handle it.

*Fix:* add the clause that matches your intent, as [How to write the clauses](#how-to-write-the-clauses) lists them; here `if error pass`. See [U3007](/docs/errors/U3007/).
:::

### Passing a failure of another kind (U3008)

:::mistake
In `check_stock`, write `if error pass` instead of `if error fail Unavailable(sku: order.sku)`:

```diff include="day-to-day..mistakes/2:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -46,3 +46,3 @@
   let left = on_hand(order.sku)
-    if error fail Unavailable(sku: order.sku)
+    if error pass
     if none fail UnknownSku(sku: order.sku)
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U3008] Error: `if error pass` passes a `StockError` failure, and this code fails with `OrderError`; use `if error fail` with a variant of `OrderError`
```

*Why:* `pass` looks like the simplest clause, but it hands the failure on unchanged, and a function has one error kind: `StockError` is not `OrderError`. The message names both kinds, the one the call fails with and the one this code fails with, and says what to write instead.

*Fix:* translate with `if error fail Unavailable(sku: order.sku)`. To keep the original, add a variant with a field of type `StockError`, such as `StockFailed(cause: StockError)`, and write `if error fail StockFailed(cause: error)`. See [U3008](/docs/errors/U3008/).
:::

### Failing with a variant of another kind (U3009)

:::mistake
Write `if error fail BeingCounted(sku: order.sku)` in `check_stock`:

```diff include="day-to-day..mistakes/3:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -46,3 +46,3 @@
   let left = on_hand(order.sku)
-    if error fail Unavailable(sku: order.sku)
+    if error fail BeingCounted(sku: order.sku)
     if none fail UnknownSku(sku: order.sku)
```

```text include="mistakes/3/expected/rendered.txt#L1"
[U3009] Error: `BeingCounted` is a variant of `StockError`, and this code fails with `OrderError`
```

*Why:* `BeingCounted` is the name of what went wrong, so it is tempting to reuse it. But `fail` names a variant of the function's own error kind, and `BeingCounted` belongs to `StockError`. The message names the variant, its kind, and the kind this code fails with.

*Fix:* name a variant of your own kind, `Unavailable`. See [U3009](/docs/errors/U3009/).
:::

### A public function that fails without saying so (U3009)

:::mistake
Remove `fails OrderError` from `parse_order`:

```diff include="day-to-day..mistakes/4:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -29,3 +29,2 @@
 pub parse_order(line: Text) -> Order
-  fails OrderError
 =
```

```text include="mistakes/4/expected/rendered.txt#L1,L8"
[U3009] Error: this code declares no error kind, so it cannot fail with `Malformed`; declare `fails` in its header
    │ Help: repair 1: declare `fails OrderError` in the header; edit src/orders.una:29:37..29:37 to "\n  fails OrderError"
```

`una check` reports this once for every way the body fails, three times here.

*Why:* a private function may leave out `fails`, so it is easy to forget that a `pub` one may not: a `pub` header is what other modules rely on. The message is reported at each place the body fails, and the help line gives the exact edit, the line to add and where.

*Fix:* `una fix .` applies the repair shown. See [U3009](/docs/errors/U3009/).
:::

### Nesting a call that can fail (U3013)

:::mistake
Write `check_stock(parse_order(line))`:

```diff include="day-to-day..mistakes/5:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -57,5 +57,3 @@
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

*Why:* nesting calls is how many languages chain steps. In Una a call that can fail is the whole expression of its statement, so that each failure has its own handling line and the order of the work stays visible. The message names the inner call, `parse_order`, and says what to do: give its result a name with `let` first.

*Fix:* `let order = parse_order(line)` with its clause, then `check_stock(order)` with its own. A `do` line of an example is the one place where calls that can fail may nest. See [U3013](/docs/errors/U3013/).
:::

### The clause on the same line (U0101)

:::mistake
Write `let order = parse_order(line) if error pass`:

```diff include="day-to-day..mistakes/6:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -57,4 +57,3 @@
 =
-  let order = parse_order(line)
-    if error pass
+  let order = parse_order(line) if error pass
   check_stock(order)
```

```text include="mistakes/6/expected/rendered.txt#L1,L8"
[U0101] Error: a handling clause goes on its own line, indented under the expression it handles
    │ Help: repair 1: move the clause to its own line; edit src/orders.una:58:32..58:46 to "\n    if error pass"
```

*Why:* the clause reads like part of the sentence, so it is natural to write it on the same line. But a clause is a line of its own, so that every handling decision starts a line a reviewer can scan. The help line gives the exact edit: the clause moves to the next line, indented.

*Fix:* `una fix .` moves it. See [U0101](/docs/errors/U0101/).
:::

### `if none` before `if error` (U0102)

:::mistake
Swap the two clauses under `on_hand(order.sku)` in `check_stock`:

```diff include="day-to-day..mistakes/7:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -46,4 +46,4 @@
   let left = on_hand(order.sku)
+    if none fail UnknownSku(sku: order.sku)
     if error fail Unavailable(sku: order.sku)
-    if none fail UnknownSku(sku: order.sku)
   if order.quantity > left
```

```text include="mistakes/7/expected/rendered.txt#L1"
[U0102] Error: `if error` clause after `if none`; handling clauses go in the order if error, if none
```

*Why:* both clauses handle one call, so their order can look free. It is fixed: the `if error` clause handles the call, and `if none` handles the value it gave, so the call's failure comes first. The message names the clause out of place and the order to use.

*Fix:* put `if error` first. See [U0102](/docs/errors/U0102/).
:::

### Re-raising a stored failure (U0101)

:::mistake
In `report`, after `attempt`, write `is Err(failure) -> fail failure`:

```diff include="day-to-day..mistakes/8:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -78,3 +78,3 @@
     is Ok(order) -> "ok      {order.quantity} x {order.sku}"
-    is Err(failure) -> "reject  {reason(failure)}"
+    is Err(failure) -> fail failure
 
```

```text include="mistakes/8/expected/rendered.txt#L1,L8"
[U0101] Error: unexpected `failure`, expected a variant
    │ Help: repair 1: `fail` takes a variant of the error kind, as in `fail Broke`, not a stored value; fail where the error is found, or pass a call's failure on with `if error pass`
```

*Why:* after `attempt`, the failure is in a name, and handing it on with `fail` looks natural. But `fail` takes a variant of the error kind, at the place the failure is decided, not a stored value: the parser expected a variant name where `failure` stands. The help line explains both ways out.

*Fix:* if you only want to pass the failure on, do not `attempt`; use `if error pass`. Here `report` must not fail at all, so its `Err` arm gives back the reason, as before. See [U0101](/docs/errors/U0101/).
:::

## 7.10 Exercises

The exercises come with the chapter's download, `07-failure.tar.gz`. Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's example added, and a **stub** of what to write when there is one, a header with a body that gives back a placeholder. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: it writes the code in the canonical form that `una check` expects.

### Exercise 1: a per-line limit

::::exercise
The store ships at most 10 units of a SKU per line. Add a variant `TooMany(sku: Text, limit: Int)` and reject larger quantities in `parse_order`, before the stock list is asked. The start package ends with this example, and `una check .` reports U1001 until the variant exists:

```una include="exercises/1/start/src/orders.una#L128-L130" title="exercises/1/start/src/orders.una"
example "more than ten units on one line is TooMany"
  do parse_order("LAMP-01, 11")
  expect fails TooMany
```

:::hint
*Hint:* work in three small steps, and run `una check .` after each. First add the variant `TooMany(sku: Text, limit: Int)` to `OrderError`: the checker then shows the one `when` that needs a new arm, in `reason`. Second, give `reason` that arm, with a sentence that uses both fields. Third, in `parse_order`, add one more `else if` branch after the test for a quantity below 1, which fails with `TooMany` when the quantity is above 10 ([`fail` in a branch](#fail-in-a-branch)).
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
-pub kind OrderError = Malformed(line: Text) | BadQuantity(line: Text) | UnknownSku(sku: Text) | OutOfStock(sku: Text, wanted: Int, left: Int) | Unavailable(sku: Text)
+pub kind OrderError = Malformed(line: Text) | BadQuantity(line: Text) | UnknownSku(sku: Text) | OutOfStock(sku: Text, wanted: Int, left: Int) | Unavailable(sku: Text) | TooMany(sku: Text, limit: Int)
 
@@ -38,2 +38,4 @@
     fail BadQuantity(line)
+  else if quantity > 10
+    fail TooMany(sku: sku, limit: 10)
   else
@@ -71,2 +73,3 @@
     is Unavailable(sku) -> "the shelf of {sku} is being counted; retry later"
+    is TooMany(sku, limit) -> "at most {limit} of {sku} per line"
 
```

`una test .` reports every example passing.
:::
::::

### Exercise 2: a line with no SKU

::::exercise
The line ` , 2` has a comma and a quantity, but nothing before the comma. Today `parse_order` accepts it with an empty SKU, and the stock list then rejects it as an unknown SKU, with an empty name in the report. Make `parse_order` fail with `Malformed` when the SKU is empty. The start package ends with this example:

```una include="exercises/2/start/src/orders.una#L128-L130" title="exercises/2/start/src/orders.una"
example "a line with no SKU before the comma is Malformed"
  do parse_order(" , 2")
  expect fails Malformed
```

:::hint
*Hint:* after the line that makes `sku`, test its length, `sku.len == 0`, with an `if` that has no `else` ([section 3.4](/learn/text-and-conditions/#s3-4)), and `fail Malformed(line)` in it.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/2/start/expected/commands/test.txt#L11-L15"
example orders "a line with no SKU before the comma is Malformed" ... FAILED
  src/orders.una:130: expect fails Malformed
  the `do` line completed with `Order(sku: "", quantity: 2)`

10 examples: 9 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Test the SKU right after it is made:

```diff include="exercises/2/start..exercises/2/answer:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -34,2 +34,4 @@
   let sku = line.slice(start: 0, end: comma).trim
+  if sku.len == 0
+    fail Malformed(line)
   let quantity = line.slice(start: comma + 1, end: line.len).trim.to_int()
```

The test runs before the quantity is read, so a line with no SKU is `Malformed`, whatever follows the comma.
:::
::::

### Exercise 3: the units a line ships

::::exercise
Write `units_of(line)`: the quantity of an order line when `accept` accepts it, and 0 when it rejects it. The start package has it with a body of `0`, and these examples:

```una include="exercises/3/start/src/orders.una#L128-L138" title="exercises/3/start/src/orders.una"
--- The units an order line ships: its quantity when it is accepted, 0 when it is rejected.
--- Exercise 3: replace the 0.
pub units_of(line: Text) -> Int = 0

example "an accepted line ships its quantity"
  do units_of("LAMP-01, 2")
  expect result == 2

example "a rejected line ships nothing"
  do units_of("DESK-02, 3")
  expect result == 0
```

:::hint
*Hint:* `units_of` must not fail, so keep the outcome of `accept` with `attempt` ([section 7.4](#s7-4)), then take it apart with a `when` whose `Ok` arm gives the order's quantity and whose `Err` arm gives 0. The header changes to the long form, since the body has two steps.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/3/start/expected/commands/test.txt#L11-L16"
example orders "an accepted line ships its quantity" ... FAILED
  src/orders.una:134: expect result == 2
  it is false, with `result` = `0`
example orders "a rejected line ships nothing" ... ok

11 examples: 10 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Keep the outcome, and give 0 for a rejected line:

```diff include="exercises/3/start..exercises/3/answer:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -128,4 +128,8 @@
 --- The units an order line ships: its quantity when it is accepted, 0 when it is rejected.
---- Exercise 3: replace the 0.
-pub units_of(line: Text) -> Int = 0
+pub units_of(line: Text) -> Int
+=
+  let outcome = attempt accept(line)
+  when outcome
+    is Ok(order) -> order.quantity
+    is Err -> 0
 
```

`if error use` would not do here: it needs a value of the type `Order` to carry on with, and no order stands for a rejected line. `attempt` keeps the outcome as a value, and the `when` decides what each case ships.
:::
::::

## 7.11 Recap and reference

### For agents

:::agents
Every diagnostic of [Common mistakes](#s7-9) is available as JSON with `una --json check .`. For [Forgetting the clause](#forgetting-the-clause-u3007):

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U3007","severity":"error","domain":"authority","message":"`parse_order` can fail with `OrderError`; handle the failure with an `if error` clause, or wrap the call in `attempt`","primary":{"file":"src/orders.una","start":{"line":58,"col":15},"end":{"line":58,"col":32}},"related":[],"repairs":[],"explain":"una explain U3007"}],"fixable":0}
```

`repairs` is empty because the right clause depends on intent, which only the author knows. U0101 for a clause on the same line ([the clause on the same line](#the-clause-on-the-same-line-u0101)) and U3009 for a missing `fails` ([a public function that fails without saying so](#a-public-function-that-fails-without-saying-so-u3009)) carry exact edits, which `una fix .` applies. The compact rule: *a call that can fail is the whole expression of its statement, followed by `if error …` and then `if none …` on their own lines, or is wrapped in `attempt`, which gives a `Result`.*
:::

### Recap

:::recap
- A value that may be missing is an `Option[T]`, `Some(value)` or `None`: take it apart with `when`, or use `or_else`.
- A failure is a value of a sum kind you declare, whose variants carry what a person needs.
- A header declares at most one error kind with `fails`, or `fails of p`. A `pub` function must declare it; a private one may leave it to inference.
- A call that can fail is the whole expression of its statement, and its handling clauses follow on their own lines: `if error` first, then `if none`.
- `use` carries on, `pass` hands on the same kind, `fail V(cause: error)` translates.
- `attempt` keeps the outcome of one call as a `Result`, `Ok` or `Err`.
- `checked` is a budgeted run-time test for facts no proof can establish. Use it once, where data enters; prefer a guard when you can.
- Give every failure path an example.
:::

### Reference

:::reference
- Construct pages: [`fails`](/docs/language/errors/fails/), [`fail`](/docs/language/errors/fail/), [`if error` and `if none`](/docs/language/errors/if-error/), [`attempt`](/docs/language/errors/attempt/), [`checked` and the escape budget](/docs/language/errors/checked/), [`predicate`](/docs/language/types/predicate/), [`example`](/docs/language/examples/example/)
- Prelude: [`Option`, `Result`, `or_else`, `is_some`, `is_ok`, `to_int`, `find`, `parse_int`, `ParseError`](/docs/std/)
- Configuration: [`[escape_budget] checked_per_module`](/docs/configure/escape-budget/checked-per-module/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U0102](/docs/errors/U0102/), [U1001](/docs/errors/U1001/), [U2001](/docs/errors/U2001/), [U2007](/docs/errors/U2007/), [U2016](/docs/errors/U2016/) (an opaque predicate called outside `checked`), [U3007](/docs/errors/U3007/), [U3008](/docs/errors/U3008/), [U3009](/docs/errors/U3009/), [U3013](/docs/errors/U3013/), [U5001](/docs/errors/U5001/) (a refinement the verifier refutes), [U7003](/docs/errors/U7003/) (`checked` beyond the escape budget), [U3025](/docs/errors/U3025/) and [U3026](/docs/errors/U3026/) (edition `0.3`: a clause or `attempt` on a call that cannot fail), and the stops at run time: [U6001](/docs/errors/U6001/) (`main` failed with its declared kind), [U6003](/docs/errors/U6003/) (call depth or memory), [U6004](/docs/errors/U6004/) (an HTTP header value with a control character), [U6005](/docs/errors/U6005/) (host text that is not valid UTF-8) and [U8001](/docs/errors/U8001/) (an internal error of una)
- Specification: [errors](/docs/spec/06-errors/), [types](/docs/spec/03-types/), [the standard library](/docs/spec/14-standard-library/), [text](/docs/spec/22-text/)
:::
