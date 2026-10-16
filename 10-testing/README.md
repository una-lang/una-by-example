---
learn: "10"
title: Testing
editions: ["0.2"]
codes: [U0101, U1001, U1002, U3001, U3014, U5001]
time: 40
builds: A checkout that reserves stock, charges a card and mails a receipt, tested with fake services
prerequisites: ["6", "7", "8"]
template: 2
---

# 10 Testing

The verifier proves what a contract states, for every input. It cannot tell you whether a cart of two lamps costs 44.70, whether a declined card puts the stock back, or whether a receipt goes out only after the payment. You check those with examples: tests that live next to the code, run against fake services you write in Una, and see every operation the code performs. This chapter writes examples for values, for failures and for effects, and shows where an example ends and a contract begins.

## What you'll build

:::build
A checkout for a small store. It reserves the units of a cart in the warehouse, charges the customer's card, and mails a receipt. When a step fails, it says why, and puts back what it took. Run against fake services, its log reads:

```text include="day-to-day/expected/output.txt"
paid, reference PAY-4470
not enough DESK-02 in stock
the card was declined for 24900 cents
the cart is empty
```

You will learn to:

- write an `example` with `do` and `expect`, and read what `una test` reports when one fails;
- test every failure path with `expect fails`;
- replace a service with a fake handler, and check what a call did with `expect performed`;
- decide what belongs in a contract and what belongs in an example;
- link a contract to the requirement it implements, and trace it with `una trace`.
:::

## Why it works this way

In many languages, tests live in other files, in another framework, with rules of their own. A test can reach the real network or the real clock by accident, so it passes on one machine and fails on the next. Fakes are often made by replacing functions while the program runs, and nothing checks that a fake behaves like the service it replaces. A reader who wants to know what a function is for has to find its tests first.

Una takes a different route:

:::steps
1. **An example sits next to the code it tests.** It is a declaration of the module, checked by `una check` like any other code, and run by `una test`.
2. **An example cannot touch the world.** It has no host capabilities: every service it needs comes from a handler written in Una, so it gives the same result on every machine.
3. **A fake is an ordinary handler.** The checker holds it to the capability's declaration, including the promises of its operations.
4. **Each run records its effects.** An example can state which operations the code performed, and which it did not.
:::

> [!KEY]
> A contract is proven for every input, before the program runs. An example is checked for one input, when you run `una test`. State in a contract what must always hold, and write an example for the cases a reader should see and for what the code does to the world.

## 10.1 Examples: `do` and `expect`

### A first example: adding up a cart

An example names a case in plain words, runs one expression, and states what must hold of its result. Start with a cart that adds up its lines. Each step of this chapter is a package, as in [chapter 1, Hello, Una](/learn/hello/#s1-1): `una.toml`, `verification.lock` (copy it from chapter 1), and the module under `src/`. The manifest of this step names the package `cart` and runs the module `cart`:

```toml include="steps/01-examples/una.toml" title="steps/01-examples/una.toml"
[package]
name = "cart"
version = "0.1.0"
edition = "0.2"

[run]
entry = "cart"
grants = ["console"]
```

:::steps
```una include="steps/01-examples/src/cart.una" title="steps/01-examples/src/cart.una" verified="check, run, test"
module cart

--- One line of a cart: a SKU, how many units, and the price of one unit in cents.
pub kind Line
  sku: Text
  quantity: Int
  unit_cents: Int

--- What a whole cart holds: its units, and their price in cents.
pub kind Summary
  units: Int
  cents: Int

--- Adds up the units and the price of every line.
pub summarize(lines: List[Line]) -> Summary
=
  let edit units = 0
  let edit cents = 0
  for line in lines
    units = units + line.quantity
    cents = cents + line.quantity * line.unit_cents
  Summary(units: units, cents: cents)

pub main() -> Unit
  uses @console: Console[print]
=
  let cart = [Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990), Line(sku: "MUG-03", quantity: 1, unit_cents: 890)]
  let summary = summarize(cart)
  @console.print("{summary.units} units, {summary.cents} cents")

example "two lamps and a mug"
  do summarize([Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990), Line(sku: "MUG-03", quantity: 1, unit_cents: 890)])
  expect result.units == 3
  expect result.cents == 4870

example "an empty cart holds nothing"
  do summarize([])
  expect result == Summary(units: 0, cents: 0)
```

1. **`example "two lamps and a mug"`.** The text names the case. It is what `una test` prints, so write it as a sentence a reviewer can read. Names are unique within a module.
2. **`do summarize([...])`.** The `do` line runs the expression under test, once. An example has exactly one `do` line.
3. **`expect result.units == 3`.** Each `expect` line is a `Bool` that must be true. `result` is the value the `do` line gave, so you can read its fields. An example has at least one `expect` line, and may have several: here, one for each field.
4. **`expect result == Summary(units: 0, cents: 0)`.** Records compare field by field, so one line can state a whole value.
:::

### Running the examples with `una test`

`una run .` runs `main` only, and ignores the examples:

```text include="steps/01-examples/expected/output.txt"
3 units, 4870 cents
```

`una test .` checks the package first, as `una check` does, then runs every example of every module, each in a fresh machine, and prints one line per example:

```sh
una test .
```

```text include="steps/01-examples/expected/commands/test.txt"
$ una test .
example cart "two lamps and a mug" ... ok
example cart "an empty cart holds nothing" ... ok

2 examples: 2 passed, 0 failed
```

### When an example fails

Now break the code. Count one unit per line, instead of the line's quantity:

```diff include="steps/01-examples..steps/02-a-bug:src/cart.una" context="1" title="src/cart.una"
--- a/src/cart.una
+++ b/src/cart.una
@@ -19,3 +19,3 @@
   for line in lines
-    units = units + line.quantity
+    units = units + 1
     cents = cents + line.quantity * line.unit_cents
```

The package still checks: nothing in `summarize`'s header says what it adds up. `una test .` finds the bug:

```text include="steps/02-a-bug/expected/commands/test.txt"
$ una test .
example cart "two lamps and a mug" ... FAILED
  src/cart.una:33: expect result.units == 3
  it is false, with `result` = `Summary(units: 2, cents: 4870)`
example cart "an empty cart holds nothing" ... ok

2 examples: 1 passed, 1 failed
```

The report names the example, the file and line of the `expect` that did not hold, and the value of `result`. `una test` exits with code 1 when any example fails, so a build script or a continuous-integration job stops there.

### Examples can reach private functions

> [!TIP]
> An example may call the module's private functions, such as a helper you want to pin down on its own. Examples are part of the module, not callers from outside it.

## 10.2 Testing failures: `expect fails`

### Every failure path needs an example

A function that can fail ([chapter 6, Failure](/learn/failure/)) needs an example for each way it can fail, as much as for its happy path. `expect fails V` holds when the `do` line failed with the variant `V`. The `do` line itself needs no handling clause: whatever it fails with, the example catches.

### The failure paths of a coupon

This step applies a coupon code to a cart. A code can be unknown, and a coupon needs a cart of at least 20.00:

:::steps
```una include="steps/03-failures/src/coupons.una" title="steps/03-failures/src/coupons.una" verified="check, run, test"
module coupons

--- Why a coupon was not accepted.
pub kind CouponError = Unknown(code: Text) | BelowMinimum(minimum: Int)

--- The percent that a coupon code takes off.
pub percent_off(code: Text) -> Int
  fails CouponError
=
  if code == "SPRING10" then 10 else if code == "VIP25" then 25 else fail Unknown(code)

--- The price of a cart after a coupon, in cents. A coupon needs a cart of at least 20.00.
pub apply_coupon(code: Text, cents: Int) -> Int
  fails CouponError
=
  let percent = percent_off(code)
    if error pass
  if cents < 2000
    fail BelowMinimum(minimum: 2000)
  else
    cents - cents * percent / 100

pub main() -> Unit
  uses @console: Console[print]
=
  let spring = attempt apply_coupon("SPRING10", cents: 5000)
  let winter = attempt apply_coupon("WINTER5", cents: 5000)
  @console.print("{spring} {winter}")

example "SPRING10 takes 10 percent off"
  do apply_coupon("SPRING10", cents: 5000)
  expect result == 4500

example "an unknown code is Unknown"
  do apply_coupon("WINTER5", cents: 5000)
  expect fails Unknown

example "a small cart is BelowMinimum, even with a good code"
  do apply_coupon("VIP25", cents: 1500)
  expect fails BelowMinimum

example "the code is checked before the amount"
  do apply_coupon("WINTER5", cents: 1500)
  expect fails Unknown
```

1. **`expect result == 4500`.** The happy path: 10 percent off 50.00.
2. **`expect fails Unknown`.** `apply_coupon` fails with `CouponError`, and `Unknown` is one of its variants. You name the variant only, without its fields.
3. **`"a small cart is BelowMinimum, even with a good code"`.** The second failure path gets its own example.
4. **`"the code is checked before the amount"`.** When both inputs are wrong, the order of the checks decides which failure the caller sees. An example pins that order down, so a later edit that swaps the checks fails a test.
:::

```text include="steps/03-failures/expected/commands/test.txt"
$ una test .
example coupons "SPRING10 takes 10 percent off" ... ok
example coupons "an unknown code is Unknown" ... ok
example coupons "a small cart is BelowMinimum, even with a good code" ... ok
example coupons "the code is checked before the amount" ... ok

4 examples: 4 passed, 0 failed
```

### What the report says when an expectation is wrong

The expectations of an example are checked in order, and the first that does not hold fails it. Two mistakes are common. Here are both, written on purpose:

```una include="steps/04-misread/src/coupons.una#L30-L36" title="steps/04-misread/src/coupons.una"
example "SPRING10 on 50.00 is refused"
  do apply_coupon("SPRING10", cents: 5000)
  expect fails BelowMinimum

example "WINTER5 takes 5 percent off"
  do apply_coupon("WINTER5", cents: 5000)
  expect result == 4750
```

```text include="steps/04-misread/expected/commands/test.txt"
$ una test .
example coupons "SPRING10 on 50.00 is refused" ... FAILED
  src/coupons.una:32: expect fails BelowMinimum
  the `do` line completed with `4500`
example coupons "WINTER5 takes 5 percent off" ... FAILED
  src/coupons.una:36: expect result == 4750
  the `do` line failed with `Unknown("WINTER5")`, so `result` has no value

2 examples: 0 passed, 2 failed
```

- **`expect fails`, and the call succeeded.** The report gives the value it returned instead: `4500`. A cart of 50.00 meets the minimum, so the example was wrong, not the code.
- **`expect result`, and the call failed.** There is no `result` to compare, and the report gives the failure: `Unknown("WINTER5")`.

### A failure no `expect fails` line expects

A third rule closes the gap between those two mistakes. When the `do` line fails and no `expect fails` line expects it, the example fails, even if every other line held. A failure is never silently accepted.

> [!NOTE]
> An `expect` line that does not mention `result`, such as `expect performed @mail.send` in [section 10.3](#s10-3), still runs after a failed `do` line. That is how an example checks what a failing call did before it failed.

## 10.3 Fakes: `given`, `expect performed` and `expect not performed`

### A service in an example is a fake

Most code worth testing talks to something: a warehouse, a card processor, a mail service. In Una that something is a capability ([chapter 8, Capabilities](/learn/capabilities/)), and an example gives it a handler with a `given` line. The handler is the fake. It is ordinary Una code, so you write the fake you need: one that answers, one that refuses, one that never answers.

### Faking the warehouse and the mail service

This step mails the buyer when a SKU runs low. The warehouse promises, in the `ensures` of its operation, that it never reports fewer than 0 units:

:::steps
```una include="steps/05-fakes/src/restock.una" title="steps/05-fakes/src/restock.una" verified="check, run, test"
module restock

--- A count of units, never below zero.
kind Units = Int where it >= 0

--- The warehouse's stock.
pub capability Inventory
  op left(sku: Text) -> Int
    ensures result >= 0

--- The store's mail service.
pub capability Mail
  op send(to: Text, body: Text) -> Unit

--- Mails the buyer when a SKU runs low, with fewer than 3 units left. Says whether it did.
pub warn_if_low(sku: Text) -> Bool
  uses @inventory: Inventory[left]
  uses @mail: Mail[send]
=
  let units = @inventory.left(sku)
  if units < 3
    @mail.send("buyer@example.invalid", body: "{sku}: {units} left")
    true
  else
    false

--- A fake warehouse that holds `units` of every SKU.
handler shelf(units: Units) for Inventory
  op left(sku) = units

--- A fake mail service: it accepts every message and delivers none.
handler outbox() for Mail
  op send(to, body) = unit

pub main() -> Unit
  uses @console: Console[print]
=
  let low = warn_if_low("LAMP-01") with @inventory = shelf(2), @mail = outbox()
  let plenty = warn_if_low("DESK-02") with @inventory = shelf(40), @mail = outbox()
  @console.print("LAMP-01 warned: {low}, DESK-02 warned: {plenty}")

example "two units left mails the buyer"
  given @inventory = shelf(2)
  given @mail = outbox()
  do warn_if_low("LAMP-01")
  expect result
  expect performed @mail.send

example "forty units left mails nobody"
  given @inventory = shelf(40)
  given @mail = outbox()
  do warn_if_low("LAMP-01")
  expect not result
  expect not performed @mail.send
```

1. **`handler shelf(units: Units) for Inventory`.** A fake warehouse that holds `units` of every SKU. `Units` is a refined kind ([chapter 7, Contracts and the verifier](/learn/contracts/)): an `Int` that is never below zero. Its parameter is given where it is installed, so each example sets the stock it needs: `shelf(2)`, `shelf(40)`.
2. **`handler outbox() for Mail`.** A fake mail service that accepts every message. It delivers nothing, and it does not need to: the example only needs to know that a message was sent.
3. **`given @inventory = shelf(2)`.** Installs the handler as `@inventory` for this example only, as `with` does for one call. Every capability the `do` line needs must have a `given` line.
4. **`expect result` and `expect not result`.** `warn_if_low` returns a `Bool`, so `result` is already the condition.
5. **`expect performed @mail.send`.** Each run keeps a trace, the list of operations the code performed, in order. This line holds when the trace has at least one `send` on `@mail`. `expect not performed @mail.send` holds when it has none.
:::

```text include="steps/05-fakes/expected/commands/test.txt"
$ una test .
example restock "two units left mails the buyer" ... ok
example restock "forty units left mails nobody" ... ok

2 examples: 2 passed, 0 failed
```

### What `expect performed` does not say

`expect performed` says that an operation ran, not how often or with which arguments. When those matter, return them: a value the example can compare is the clearest evidence. The JSON report shown in [For agents](#for-agents) also lists every operation with its arguments.

### Fakes are checked too

A fake is a handler, and the verifier checks every handler against the operations it implements. Give `shelf` a plain `Int` instead of `Units`, the count that is never below zero:

```diff include="steps/05-fakes..steps/06-dishonest-fake:src/restock.una" context="1" title="src/restock.una"
--- a/src/restock.una
+++ b/src/restock.una
@@ -27,3 +27,3 @@
 --- A fake warehouse that holds `units` of every SKU.
-handler shelf(units: Units) for Inventory
+handler shelf(units: Int) for Inventory
   op left(sku) = units
```

```text include="steps/06-dishonest-fake/expected/rendered.txt#L1,L18"
[U5001] Error: postcondition of `left` is refuted
    │ Note 2: counterexample: result = -1, units = -1
```

The counterexample, `units = -1`, is a warehouse no real store has. A test that passed against it would prove nothing about the real one. Una rejects the fake before any example runs, so every fake keeps the promises that the code under test relies on.

### A fake holds no state

> [!NOTE]
> A handler holds no state between operations: `outbox` cannot count the messages it was given, and a fake cannot fail once and then answer. Each example also runs in a fresh machine, so no example sees what another did.

## 10.4 What the verifier proves, and what examples show

### A rule with a contract and two examples

Contracts and examples answer different questions. Take the store's shipping fee: 4.90, and free from 50.00 on. The rule comes from the store's terms, so the code records it as a requirement, and the contract that implements it says where it came from:

:::steps
```una include="steps/07-contracts/src/shipping.una" title="steps/07-contracts/src/shipping.una" verified="check, run, test"
module shipping

requirement SHIPPING_1
  text "Orders of 50.00 or more ship for free"
  source policy "Store terms, section 4"
  owner checkout
  status active

--- The shipping fee of an order, in cents: 4.90, and nothing from 50.00 on.
pub shipping_fee(subtotal: Int) -> Int
  ensures result >= 0 and result <= 490
  ensures subtotal >= 5000 implies result == 0
  derived from SHIPPING_1
=
  if subtotal >= 5000 then 0 else 490

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("49.99 pays {shipping_fee(4999)}, 50.00 pays {shipping_fee(5000)}")

example "an order of 49.99 pays 4.90"
  do shipping_fee(4999)
  expect result == 490

example "an order of exactly 50.00 ships for free"
  do shipping_fee(5000)
  expect result == 0
```

1. **`requirement SHIPPING_1`.** It records the rule in words, its source, the team that owns it, and whether it is active. Its name is in upper snake case and ends with `_` and a number (U1005 otherwise).
2. **`ensures`.** Two promises, proven for every `subtotal`: the fee is between 0 and 4.90, and an order of 50.00 or more pays nothing.
3. **`derived from SHIPPING_1`.** Ties the contract to the requirement.
4. **The examples.** Two chosen cases, one on each side of the threshold.
:::

### Tracing a requirement with `una trace`

`una trace` follows the requirement to the contracts derived from it, and to the status of each proof:

```sh
una trace SHIPPING_1
```

```text include="steps/07-contracts/expected/commands/trace.txt"
$ una trace SHIPPING_1
requirement SHIPPING_1 (active)
  text "Orders of 50.00 or more ship for free"
  source policy "Store terms, section 4"
  owner checkout
shipping.shipping_fee
  ensures result >= 0 and result <= 490
  ensures subtotal >= 5000 implies result == 0
  proven   ob-0e65adfc62af postcondition result >= 0 and result <= 490
  proven   ob-93e87c6acd5e postcondition subtotal >= 5000 implies result == 0
```

### A bug the verifier catches: off by one

Now compare two bugs. In the first, the threshold is off by one, `>` instead of `>=`:

```diff include="steps/07-contracts..steps/08-off-by-one:src/shipping.una" context="0" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -15 +15 @@
-  if subtotal >= 5000 then 0 else 490
+  if subtotal > 5000 then 0 else 490
```

```text include="steps/08-off-by-one/expected/diagnostics.txt"
error U5001 at src/shipping.una:15:34: postcondition of `shipping_fee` is refuted
  counterexample: result = 490, subtotal = 5000
```

The verifier rejects it before anything runs, and its counterexample, `subtotal = 5000`, is exactly the order the bug charges.

### A bug only an example catches: a dropped zero

In the second bug, a zero is missing from the fee:

```diff include="steps/07-contracts..steps/09-dropped-zero:src/shipping.una" context="0" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -15 +15 @@
-  if subtotal >= 5000 then 0 else 490
+  if subtotal >= 5000 then 0 else 49
```

The package checks clean: 49 cents is between 0 and 490, so every promise still holds. Only the example sees it:

```text include="steps/09-dropped-zero/expected/commands/test.txt"
$ una test .
example shipping "an order of 49.99 pays 4.90" ... FAILED
  src/shipping.una:24: expect result == 490
  it is false, with `result` = `49`
example shipping "an order of exactly 50.00 ships for free" ... ok

2 examples: 1 passed, 1 failed
```

The contract states a range, and the example states one exact value. Neither replaces the other.

### Choosing a contract or an example

The table sums up which construct answers which question:

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| A rule that must hold for every input, such as a bound or a threshold | `ensures` in the header, proven by `una check` |
| A precondition that callers must meet | `requires` |
| An exact value for a case a reader should see | an `example` with `expect result == …` |
| A failure path | an `example` with `expect fails` |
| What a call did, or did not do, to a service | an `example` with fakes and `expect performed` |
| Where a rule came from | a `requirement`, `derived from`, and `una trace` |
:::

## 10.5 Day-to-day: checkout

### What the checkout must do

Now the program from the start of the chapter. A checkout takes a cart and an email address. It reserves the units of every line in the warehouse, charges the card for the total, and mails a receipt. Three services, each a capability, and each step can fail.

### The kinds and the services

```una include="day-to-day/src/checkout.una#L1-L27" title="day-to-day/src/checkout.una" caption="the kinds and the services"
module checkout

--- One line of a cart: a SKU, how many units, and the price of one unit in cents.
pub kind Line
  sku: Text
  quantity: Int
  unit_cents: Int

--- Why a checkout did not go through.
pub kind CheckoutError = EmptyCart | OutOfStock(sku: Text) | Declined(cents: Int) | PaymentDown

--- How the card processor can fail.
pub kind PaymentError = Refused | Unreachable

--- The warehouse. `reserve` holds units for an order and says whether it could.
pub capability Inventory
  op reserve(sku: Text, quantity: Int) -> Bool
  op release(sku: Text, quantity: Int) -> Unit

--- The card processor. A charge gives the processor's reference for the payment.
pub capability Payments
  op charge(cents: Int) -> Text
    fails PaymentError

--- The store's mail service.
pub capability Mail
  op send(to: Text, body: Text) -> Unit
```

`CheckoutError` is what the caller sees. `PaymentError` is what the card processor says, and the checkout translates it: a refused card becomes `Declined`, with the amount, and a processor that does not answer becomes `PaymentDown`.

`reserve` returns a `Bool` instead of failing. A warehouse that says "not enough units" has answered the question, and the checkout decides what that means for the order. A failure is kept for the case where a service cannot answer at all, as `Unreachable` is for the card processor. Each service is its own capability, so each example can fake one of them without touching the others, and a header shows which of them a function needs.

### The total, a pure step

`shipping_fee` is the function of [section 10.4](#a-rule-with-a-contract-and-two-examples), with its contract. `total` adds the lines and the fee. It performs no operation, so its examples need no fakes.

```una include="day-to-day/src/checkout.una#shipping_fee..total" title="day-to-day/src/checkout.una"
--- The shipping fee in cents: 4.90, and nothing from 50.00 on.
pub shipping_fee(subtotal: Int) -> Int
  ensures result >= 0 and result <= 490
  ensures subtotal >= 5000 implies result == 0
=
  if subtotal >= 5000 then 0 else 490

--- What the customer pays for a cart, shipping included.
pub total(lines: List[Line]) -> Int
=
  let edit subtotal = 0
  for line in lines
    subtotal = subtotal + line.quantity * line.unit_cents
  subtotal + shipping_fee(subtotal)
```

### Reserving and releasing

Two private helpers, one for each direction. `reserve_all` fails at the first line the warehouse cannot hold. Private functions may leave their `uses` and `fails` to inference, but these two declare them, so each helper's effects can be read where it is defined.

```una include="day-to-day/src/checkout.una#reserve_all..release_all" title="day-to-day/src/checkout.una"
--- Reserves the units of every line, and fails at the first line the warehouse cannot hold.
reserve_all(lines: List[Line]) -> Unit
  uses @inventory: Inventory[reserve]
  fails CheckoutError
=
  for line in lines
    let held = @inventory.reserve(line.sku, quantity: line.quantity)
    if not held
      fail OutOfStock(sku: line.sku)

--- Hands the units of every line back to the warehouse.
release_all(lines: List[Line]) -> Unit
  uses @inventory: Inventory[release]
=
  for line in lines
    @inventory.release(line.sku, quantity: line.quantity)
```

### The checkout

An empty cart fails before any service is asked. Then the stock is reserved, and `attempt` keeps the outcome of the charge as a value, so the checkout can clean up before it fails: when the card is refused or the processor does not answer, the units go back to the warehouse.

```una include="day-to-day/src/checkout.una#checkout" title="day-to-day/src/checkout.una"
--- Reserves the cart, charges the card, and mails a receipt. Gives the payment's reference.
pub checkout(lines: List[Line], email: Text) -> Text
  uses @inventory: Inventory[reserve, release]
  uses @payments: Payments[charge]
  uses @mail: Mail[send]
  fails CheckoutError
=
  if lines.len == 0
    fail EmptyCart
  else
    reserve_all(lines)
      if error pass
    let cents = total(lines)
    let charged = attempt @payments.charge(cents)
    when charged
      is Ok(reference) ->
        @mail.send(email, body: "Paid {cents} cents. Reference {reference}.")
        reference
      is Err(problem) ->
        release_all(lines)
        when problem
          is Refused -> fail Declined(cents)
          is Unreachable -> fail PaymentDown
```

Step by step:

- `reserve_all(lines)` fails with `CheckoutError`, the checkout's own kind, so `if error pass` hands an `OutOfStock` to the caller unchanged.
- A handling clause does not fit the charge: `if error fail Declined(cents)` would leave the function at once, with the units still reserved, and could not tell `Refused` from `Unreachable`. `attempt` keeps the outcome as a value instead, so the `Err` arm can call `release_all` first, then fail.
- In the `Err` arm, a `when` on the processor's failure picks the checkout's variant: `Refused` becomes `Declined(cents)`, and `Unreachable` becomes `PaymentDown`.
- In the `Ok` arm, the receipt is mailed, and the processor's reference is the checkout's result.

The order of the statements is the order of the effects: reserve, charge, then mail. The examples in [section 10.6](#s10-6) pin that order down.

### The log

`describe` turns an outcome into a line of the store's log, and `reason` gives each failure its words. Neither performs an operation.

```una include="day-to-day/src/checkout.una#describe..reason" title="day-to-day/src/checkout.una"
--- What the store's log says about a checkout.
pub describe(outcome: Result[Text, CheckoutError]) -> Text
=
  when outcome
    is Ok(reference) -> "paid, reference {reference}"
    is Err(problem) -> reason(problem)

reason(problem: CheckoutError) -> Text
=
  when problem
    is EmptyCart -> "the cart is empty"
    is OutOfStock(sku) -> "not enough {sku} in stock"
    is Declined(cents) -> "the card was declined for {cents} cents"
    is PaymentDown -> "the card processor did not answer"
```

### The fakes

One handler per behavior a test needs: a warehouse with a given stock, a card processor with a limit, one that never answers, and a mail service that accepts everything. Each fits on a line or two. The parameters choose the case: `card(limit: 10000)` approves a cart of 44.70 and refuses one of 249.00, so one handler covers both outcomes, and each example shows its limit next to its cart.

```una include="day-to-day/src/checkout.una#shelf..outbox" title="day-to-day/src/checkout.una"
--- A fake warehouse that holds the units in `stock`.
handler shelf(stock: Map[Text, Int]) for Inventory
  op reserve(sku, quantity) = stock.get(key: sku).or_else(default: 0) >= quantity
  op release(sku, quantity) = unit

--- A fake card processor that accepts every charge up to `limit` cents.
handler card(limit: Int) for Payments
  op charge(cents) = if cents <= limit then "PAY-{cents}" else fail Refused

--- A fake card processor that never answers.
handler offline() for Payments
  op charge(cents) = fail Unreachable

--- A fake mail service: it accepts every message and delivers none.
handler outbox() for Mail
  op send(to, body) = unit
```

### Running it

`main` installs the same fakes with `with`, and runs four carts: two lamps, two desks when one is in stock, one desk over the card's limit, and an empty cart. In a real store, the handlers would call the warehouse, the card processor and the mail server; the checkout itself would not change.

```una include="day-to-day/src/checkout.una#main" title="day-to-day/src/checkout.una"
pub main() -> Unit
  uses @console: Console[print]
=
  let stock = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)
  let lamps = [Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)]
  let two_desks = [Line(sku: "DESK-02", quantity: 2, unit_cents: 24900)]
  let one_desk = [Line(sku: "DESK-02", quantity: 1, unit_cents: 24900)]
  let empty: List[Line] = []
  for cart in [lamps, two_desks, one_desk, empty]
    let outcome = attempt checkout(cart, email: "ana@example.invalid") with @inventory = shelf(stock), @payments = card(limit: 10000), @mail = outbox()
    @console.print(describe(outcome))
```

One `with` clause binds the three services, separated by commas, for the call it ends. `main` itself holds only `@console`, so the checkout can reach no other service than the ones installed there.

`una run .` prints the log shown in [What you'll build](#what-youll-build).

> [!WARNING]
> One path is still wrong. When the first line of a cart is reserved and the second is out of stock, the checkout fails without releasing the first. No example covers that case yet, so `una test .` passes. [Exercise 3](#exercise-3-put-back-what-was-reserved) writes the example that exposes it, then fixes the code.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/checkout.una" title="day-to-day/src/checkout.una" caption="the whole program" verified="check, run, test"
module checkout

--- One line of a cart: a SKU, how many units, and the price of one unit in cents.
pub kind Line
  sku: Text
  quantity: Int
  unit_cents: Int

--- Why a checkout did not go through.
pub kind CheckoutError = EmptyCart | OutOfStock(sku: Text) | Declined(cents: Int) | PaymentDown

--- How the card processor can fail.
pub kind PaymentError = Refused | Unreachable

--- The warehouse. `reserve` holds units for an order and says whether it could.
pub capability Inventory
  op reserve(sku: Text, quantity: Int) -> Bool
  op release(sku: Text, quantity: Int) -> Unit

--- The card processor. A charge gives the processor's reference for the payment.
pub capability Payments
  op charge(cents: Int) -> Text
    fails PaymentError

--- The store's mail service.
pub capability Mail
  op send(to: Text, body: Text) -> Unit

--- The shipping fee in cents: 4.90, and nothing from 50.00 on.
pub shipping_fee(subtotal: Int) -> Int
  ensures result >= 0 and result <= 490
  ensures subtotal >= 5000 implies result == 0
=
  if subtotal >= 5000 then 0 else 490

--- What the customer pays for a cart, shipping included.
pub total(lines: List[Line]) -> Int
=
  let edit subtotal = 0
  for line in lines
    subtotal = subtotal + line.quantity * line.unit_cents
  subtotal + shipping_fee(subtotal)

--- Reserves the units of every line, and fails at the first line the warehouse cannot hold.
reserve_all(lines: List[Line]) -> Unit
  uses @inventory: Inventory[reserve]
  fails CheckoutError
=
  for line in lines
    let held = @inventory.reserve(line.sku, quantity: line.quantity)
    if not held
      fail OutOfStock(sku: line.sku)

--- Hands the units of every line back to the warehouse.
release_all(lines: List[Line]) -> Unit
  uses @inventory: Inventory[release]
=
  for line in lines
    @inventory.release(line.sku, quantity: line.quantity)

--- Reserves the cart, charges the card, and mails a receipt. Gives the payment's reference.
pub checkout(lines: List[Line], email: Text) -> Text
  uses @inventory: Inventory[reserve, release]
  uses @payments: Payments[charge]
  uses @mail: Mail[send]
  fails CheckoutError
=
  if lines.len == 0
    fail EmptyCart
  else
    reserve_all(lines)
      if error pass
    let cents = total(lines)
    let charged = attempt @payments.charge(cents)
    when charged
      is Ok(reference) ->
        @mail.send(email, body: "Paid {cents} cents. Reference {reference}.")
        reference
      is Err(problem) ->
        release_all(lines)
        when problem
          is Refused -> fail Declined(cents)
          is Unreachable -> fail PaymentDown

--- What the store's log says about a checkout.
pub describe(outcome: Result[Text, CheckoutError]) -> Text
=
  when outcome
    is Ok(reference) -> "paid, reference {reference}"
    is Err(problem) -> reason(problem)

reason(problem: CheckoutError) -> Text
=
  when problem
    is EmptyCart -> "the cart is empty"
    is OutOfStock(sku) -> "not enough {sku} in stock"
    is Declined(cents) -> "the card was declined for {cents} cents"
    is PaymentDown -> "the card processor did not answer"

--- A fake warehouse that holds the units in `stock`.
handler shelf(stock: Map[Text, Int]) for Inventory
  op reserve(sku, quantity) = stock.get(key: sku).or_else(default: 0) >= quantity
  op release(sku, quantity) = unit

--- A fake card processor that accepts every charge up to `limit` cents.
handler card(limit: Int) for Payments
  op charge(cents) = if cents <= limit then "PAY-{cents}" else fail Refused

--- A fake card processor that never answers.
handler offline() for Payments
  op charge(cents) = fail Unreachable

--- A fake mail service: it accepts every message and delivers none.
handler outbox() for Mail
  op send(to, body) = unit

pub main() -> Unit
  uses @console: Console[print]
=
  let stock = empty_map().with(key: "LAMP-01", value: 4).with(key: "DESK-02", value: 1)
  let lamps = [Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)]
  let two_desks = [Line(sku: "DESK-02", quantity: 2, unit_cents: 24900)]
  let one_desk = [Line(sku: "DESK-02", quantity: 1, unit_cents: 24900)]
  let empty: List[Line] = []
  for cart in [lamps, two_desks, one_desk, empty]
    let outcome = attempt checkout(cart, email: "ana@example.invalid") with @inventory = shelf(stock), @payments = card(limit: 10000), @mail = outbox()
    @console.print(describe(outcome))

example "a cart under 50.00 pays shipping"
  do total([Line(sku: "MUG-03", quantity: 1, unit_cents: 4999)])
  expect result == 5489

example "a cart of two lamps is charged and mailed"
  given @inventory = shelf(empty_map().with(key: "LAMP-01", value: 4))
  given @payments = card(limit: 10000)
  given @mail = outbox()
  do checkout([Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)], email: "ana@example.invalid")
  expect result == "PAY-4470"
  expect performed @mail.send

example "an empty cart asks nobody anything"
  given @inventory = shelf(empty_map())
  given @payments = offline()
  given @mail = outbox()
  do checkout([], email: "ana@example.invalid")
  expect fails EmptyCart
  expect not performed @inventory.reserve
  expect not performed @payments.charge
  expect not performed @mail.send

example "a cart the warehouse cannot hold is never charged"
  given @inventory = shelf(empty_map().with(key: "DESK-02", value: 1))
  given @payments = card(limit: 100000)
  given @mail = outbox()
  do checkout([Line(sku: "DESK-02", quantity: 2, unit_cents: 24900)], email: "ana@example.invalid")
  expect fails OutOfStock
  expect not performed @payments.charge

example "a declined card releases the stock and mails nothing"
  given @inventory = shelf(empty_map().with(key: "DESK-02", value: 1))
  given @payments = card(limit: 10000)
  given @mail = outbox()
  do checkout([Line(sku: "DESK-02", quantity: 1, unit_cents: 24900)], email: "ana@example.invalid")
  expect fails Declined
  expect performed @inventory.release
  expect not performed @mail.send

example "a card processor that does not answer is PaymentDown"
  given @inventory = shelf(empty_map().with(key: "LAMP-01", value: 4))
  given @payments = offline()
  given @mail = outbox()
  do checkout([Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)], email: "ana@example.invalid")
  expect fails PaymentDown
  expect performed @inventory.release
```

## 10.6 Testing it

### One example per path

Each example covers one path through `checkout`, and each states both the outcome and the effects that matter for that path:

```una include="day-to-day/src/checkout.una#L129-L174" title="day-to-day/src/checkout.una" caption="the examples"
example "a cart under 50.00 pays shipping"
  do total([Line(sku: "MUG-03", quantity: 1, unit_cents: 4999)])
  expect result == 5489

example "a cart of two lamps is charged and mailed"
  given @inventory = shelf(empty_map().with(key: "LAMP-01", value: 4))
  given @payments = card(limit: 10000)
  given @mail = outbox()
  do checkout([Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)], email: "ana@example.invalid")
  expect result == "PAY-4470"
  expect performed @mail.send

example "an empty cart asks nobody anything"
  given @inventory = shelf(empty_map())
  given @payments = offline()
  given @mail = outbox()
  do checkout([], email: "ana@example.invalid")
  expect fails EmptyCart
  expect not performed @inventory.reserve
  expect not performed @payments.charge
  expect not performed @mail.send

example "a cart the warehouse cannot hold is never charged"
  given @inventory = shelf(empty_map().with(key: "DESK-02", value: 1))
  given @payments = card(limit: 100000)
  given @mail = outbox()
  do checkout([Line(sku: "DESK-02", quantity: 2, unit_cents: 24900)], email: "ana@example.invalid")
  expect fails OutOfStock
  expect not performed @payments.charge

example "a declined card releases the stock and mails nothing"
  given @inventory = shelf(empty_map().with(key: "DESK-02", value: 1))
  given @payments = card(limit: 10000)
  given @mail = outbox()
  do checkout([Line(sku: "DESK-02", quantity: 1, unit_cents: 24900)], email: "ana@example.invalid")
  expect fails Declined
  expect performed @inventory.release
  expect not performed @mail.send

example "a card processor that does not answer is PaymentDown"
  given @inventory = shelf(empty_map().with(key: "LAMP-01", value: 4))
  given @payments = offline()
  given @mail = outbox()
  do checkout([Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)], email: "ana@example.invalid")
  expect fails PaymentDown
  expect performed @inventory.release
```

Read them as a specification of the checkout.

### The total and the happy path

Two examples test paths on which nothing fails:

- **The total.** A cart under 50.00 pays 4.90 of shipping: 49.99 plus 4.90 is 54.89.
- **The happy path.** Two lamps cost 44.70 with shipping, the processor's reference comes back, and a receipt is sent.

### The failure paths: `expect fails`

Four examples each test a failure, one for each variant of `CheckoutError`:

- **An empty cart** fails with `EmptyCart`, and none of the three services is asked anything.
- **A cart the warehouse cannot hold** fails with `OutOfStock`, and the card is never charged.
- **A declined card** fails with `Declined`, the stock is released, and no receipt goes out.
- **A processor that does not answer** fails with `PaymentDown`, and the stock is released too.

### What must not happen: `expect not performed`

The `expect not performed` lines carry as much weight as the `expect fails` lines. A checkout that charged the card before it reserved the stock would still fail with `OutOfStock` for the example of a cart the warehouse cannot hold, but `expect not performed @payments.charge` would catch the charge.

### Two habits that keep examples useful

Two habits keep a set of examples like this one useful. First, each example states the effects that matter for its path and no more: the happy path checks that a receipt was sent, and leaves the stock to the paths where it can go wrong. Second, when a bug turns up, the first change is an example that fails because of it. [Exercise 3](#exercise-3-put-back-what-was-reserved) does exactly that for the gap in the reservations, so the fix comes with the evidence that it works.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt"
$ una test .
example checkout "a cart under 50.00 pays shipping" ... ok
example checkout "a cart of two lamps is charged and mailed" ... ok
example checkout "an empty cart asks nobody anything" ... ok
example checkout "a cart the warehouse cannot hold is never charged" ... ok
example checkout "a declined card releases the stock and mails nothing" ... ok
example checkout "a card processor that does not answer is PaymentDown" ... ok

6 examples: 6 passed, 0 failed
```

## 10.7 Common mistakes

Each mistake below is a small change to `day-to-day/src/checkout.una`, followed by what `una check .` reports. `una test .` reports the same diagnostics and runs nothing, since a package that does not check has no examples to run.

### Testing `main` (U3014)

:::mistake
Add an example that runs the whole program:

```diff include="day-to-day..mistakes/1:src/checkout.una" context="1" title="src/checkout.una"
--- a/src/checkout.una
+++ b/src/checkout.una
@@ -174 +174,5 @@
   expect performed @inventory.release
+
+example "the log shows four checkouts"
+  do main()
+  expect result == unit
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U3014] Error: `main` needs `@console: Console[print]`, a host capability, and examples cannot use host capabilities; give it a handler with `given`
```

*Why:* `main` needs the console, a host capability, and an example never reaches the host. That is what keeps it deterministic.

*Fix:* give `@console` a handler of your own, as the help says: `handler quiet() for Console` with `op print(line) = unit`, then `given @console = quiet()` in the example. Better, test the functions `main` calls, `checkout` and `describe`, whose results an example can compare. A fake console holds no state, so it cannot show what was printed.
:::

### A service with no `given` (U3001)

:::mistake
Leave out the card processor in the happy-path example:

```diff include="day-to-day..mistakes/2:src/checkout.una" context="1" title="src/checkout.una"
--- a/src/checkout.una
+++ b/src/checkout.una
@@ -134,3 +134,2 @@
   given @inventory = shelf(empty_map().with(key: "LAMP-01", value: 4))
-  given @payments = card(limit: 10000)
   given @mail = outbox()
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U3001] Error: `checkout` needs `@payments: Payments[charge]`, which no `given` line binds
```

*Why:* every capability the `do` line needs must be bound by a `given` line. An example never falls back to a real service.

*Fix:* add `given @payments = card(limit: 10000)`.
:::

### A misspelt operation (U1001)

:::mistake
Write `@mail.sent` for `@mail.send`:

```diff include="day-to-day..mistakes/3:src/checkout.una" context="1" title="src/checkout.una"
--- a/src/checkout.una
+++ b/src/checkout.una
@@ -138,3 +138,3 @@
   expect result == "PAY-4470"
-  expect performed @mail.send
+  expect performed @mail.sent
 
```

```text include="mistakes/3/expected/rendered.txt#L1,L8"
[U1001] Error: capability `Mail` has no operation `sent`
     │ Help: repair 1: write `send`; edit src/checkout.una:139:26..139:30 to "send"
```

*Why:* `expect performed` names an operation of the capability, and the checker resolves it like a call.

*Fix:* `una fix .` applies the repair shown.
:::

### Expecting the service's failure (U1001)

:::mistake
Expect `Refused`, what the card processor says, instead of `Declined`, what the checkout says:

```diff include="day-to-day..mistakes/4:src/checkout.una" context="1" title="src/checkout.una"
--- a/src/checkout.una
+++ b/src/checkout.una
@@ -163,3 +163,3 @@
   do checkout([Line(sku: "DESK-02", quantity: 1, unit_cents: 24900)], email: "ana@example.invalid")
-  expect fails Declined
+  expect fails Refused
   expect performed @inventory.release
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U1001] Error: cannot find variant `Refused` in `CheckoutError`
```

*Why:* `expect fails` names a variant of the error kind of the `do` call, and `checkout` fails with `CheckoutError`. It translated `Refused` into `Declined`.

*Fix:* expect the caller's variant, `Declined`.
:::

### Copying an example and keeping its name (U1002)

:::mistake
Copy the first example and change only its body:

```diff include="day-to-day..mistakes/5:src/checkout.una" context="1" title="src/checkout.una"
--- a/src/checkout.una
+++ b/src/checkout.una
@@ -132,2 +132,6 @@
 
+example "a cart under 50.00 pays shipping"
+  do total([Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)])
+  expect result == 4470
+
 example "a cart of two lamps is charged and mailed"
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U1002] Error: example "a cart under 50.00 pays shipping" is defined twice in this module
```

*Why:* the name is how `una test` reports an example, so it is unique within its module.

*Fix:* name the case the new example covers, such as `"two lamps pay shipping"`.
:::

### Installing a fake with `with` on a `do` line (U0101)

:::mistake
Move the card processor from a `given` line to the `do` line:

```diff include="day-to-day..mistakes/6:src/checkout.una" context="1" title="src/checkout.una"
--- a/src/checkout.una
+++ b/src/checkout.una
@@ -169,5 +169,4 @@
   given @inventory = shelf(empty_map().with(key: "LAMP-01", value: 4))
-  given @payments = offline()
   given @mail = outbox()
-  do checkout([Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)], email: "ana@example.invalid")
+  do checkout([Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)], email: "ana@example.invalid") with @payments = offline()
   expect fails PaymentDown
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U0101] Error: unexpected keyword `with`, expected end of line
```

*Why:* a `do` line is one expression, and an example installs its handlers with `given` lines only.

*Fix:* write `given @payments = offline()` above the `do` line.
:::

## 10.8 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added at the end. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`, since the check also requires canonical form.

### Exercise 1: a card that refuses everything

::::exercise
The start package has an example that needs a fake card processor which refuses every charge, whatever the amount:

```una include="exercises/1/start/src/checkout.una#L176-L182" title="exercises/1/start/src/checkout.una"
example "a card that refuses every charge is Declined"
  given @inventory = shelf(empty_map().with(key: "LAMP-01", value: 4))
  given @payments = refusing()
  given @mail = outbox()
  do checkout([Line(sku: "LAMP-01", quantity: 1, unit_cents: 1990)], email: "ana@example.invalid")
  expect fails Declined
  expect performed @inventory.release
```

`una test .` stops at the check, since no handler is called `refusing`:

```text include="exercises/1/start/expected/diagnostics.txt"
error U1001 at src/checkout.una:178:21: cannot find handler `refusing` in this module, its imports or the prelude
```

:::hint
*Hint:* a handler implements every operation of its capability. `Payments` has one operation, `charge`, and it fails with `PaymentError`.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Add the handler next to the other fakes:

```diff include="exercises/1/start..exercises/1/answer:src/checkout.una" context="1" title="src/checkout.una"
--- a/src/checkout.una
+++ b/src/checkout.una
@@ -108,2 +108,6 @@
 
+--- A fake card processor that refuses every charge.
+handler refusing() for Payments
+  op charge(cents) = fail Refused
+
 --- A fake card processor that never answers.
```
:::
::::

### Exercise 2: tell the customer

::::exercise
When the card is declined, the store wants to mail the customer, so that they can try another card. The start package has this example:

```una include="exercises/2/start/src/checkout.una#L176-L182" title="exercises/2/start/src/checkout.una"
example "a declined card mails the customer"
  given @inventory = shelf(empty_map().with(key: "LAMP-01", value: 4))
  given @payments = card(limit: 1000)
  given @mail = outbox()
  do checkout([Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)], email: "ana@example.invalid")
  expect fails Declined
  expect performed @mail.send
```

:::hint
*Hint:* the `Refused` arm of `checkout` becomes a block: send the mail, then fail. Then run `una test .` again, and read which example fails now.
:::

If you change only the code, `una test .` reports another example:

```text include="exercises/2/code-only/expected/commands/test.txt#L6-L8"
example checkout "a declined card releases the stock and mails nothing" ... FAILED
  src/checkout.una:168: expect not performed @mail.send
  the trace has `@mail.send` at event 4
```

That example states the old behavior. A change of behavior changes the examples that describe it, in the same edit.

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Mail the customer in the `Refused` arm, and update the example that said no mail goes out:

```diff include="exercises/2/start..exercises/2/answer:src/checkout.una" context="1" title="src/checkout.una"
--- a/src/checkout.una
+++ b/src/checkout.una
@@ -81,3 +81,5 @@
         when problem
-          is Refused -> fail Declined(cents)
+          is Refused ->
+            @mail.send(email, body: "Your card was declined for {cents} cents. Nothing was charged.")
+            fail Declined(cents)
           is Unreachable -> fail PaymentDown
@@ -158,3 +160,3 @@
 
-example "a declined card releases the stock and mails nothing"
+example "a declined card releases the stock"
   given @inventory = shelf(empty_map().with(key: "DESK-02", value: 1))
@@ -165,3 +167,2 @@
   expect performed @inventory.release
-  expect not performed @mail.send
 
```
:::
::::

### Exercise 3: put back what was reserved

::::exercise
Fix the gap named in [section 10.5](#running-it). The start package has two examples. The first fails: a cart whose second line is out of stock must release the first. The second passes, and must keep passing: a cart whose first line is out of stock has nothing to release.

```una include="exercises/3/start/src/checkout.una#L176-L190" title="exercises/3/start/src/checkout.una"
example "a line out of stock releases the lines reserved before it"
  given @inventory = shelf(empty_map().with(key: "LAMP-01", value: 4))
  given @payments = card(limit: 100000)
  given @mail = outbox()
  do checkout([Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990), Line(sku: "DESK-02", quantity: 1, unit_cents: 24900)], email: "ana@example.invalid")
  expect fails OutOfStock
  expect performed @inventory.release

example "a first line out of stock releases nothing"
  given @inventory = shelf(empty_map().with(key: "LAMP-01", value: 4))
  given @payments = card(limit: 100000)
  given @mail = outbox()
  do checkout([Line(sku: "DESK-02", quantity: 1, unit_cents: 24900), Line(sku: "LAMP-01", quantity: 2, unit_cents: 1990)], email: "ana@example.invalid")
  expect fails OutOfStock
  expect not performed @inventory.release
```

```text include="exercises/3/start/expected/commands/test.txt#L8-L13"
example checkout "a line out of stock releases the lines reserved before it" ... FAILED
  src/checkout.una:182: expect performed @inventory.release
  the trace has no `@inventory.release`
example checkout "a first line out of stock releases nothing" ... ok

8 examples: 7 passed, 1 failed
```

:::hint
*Hint:* in `reserve_all`, keep a `let edit` list of the lines reserved so far, and hand them to `release_all` before you fail. `reserve_all` then needs `release` in its `uses` too. Releasing every line of the cart passes the first example, but not the second.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Track the reserved lines, and release them at the first line that cannot be held:

```diff include="exercises/3/start..exercises/3/answer:src/checkout.una" context="1" title="src/checkout.una"
--- a/src/checkout.una
+++ b/src/checkout.una
@@ -43,7 +43,9 @@
 
---- Reserves the units of every line, and fails at the first line the warehouse cannot hold.
+--- Reserves the units of every line. At the first line the warehouse cannot hold, it releases
+--- the lines it reserved before it, and fails.
 reserve_all(lines: List[Line]) -> Unit
-  uses @inventory: Inventory[reserve]
+  uses @inventory: Inventory[reserve, release]
   fails CheckoutError
 =
+  let edit reserved: List[Line] = []
   for line in lines
@@ -51,3 +53,5 @@
     if not held
+      release_all(reserved)
       fail OutOfStock(sku: line.sku)
+    reserved = reserved.append(item: line)
 
```
:::
::::

## 10.9 Recap and reference

### For agents

:::agents
`una --json check .` reports example mistakes in the same shape as any other. For [a misspelt operation](#a-misspelt-operation-u1001), with its exact edit:

```json include="mistakes/3/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U1001","severity":"error","domain":"names","message":"capability `Mail` has no operation `sent`","primary":{"file":"src/checkout.una","start":{"line":139,"col":26},"end":{"line":139,"col":30}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"write `send`","edit":{"file":"src/checkout.una","start":{"line":139,"col":26},"end":{"line":139,"col":30},"replacement":"send"}}],"explain":"una explain U1001"}],"fixable":1}
```

`una --json test .` prints `una.test/1`. Each example has `outcome`, `reason`, the `expectation` that failed with its file and line, the `result`, and the `trace`. Each event of a trace has `seq`, `instance`, `capability`, `op`, `args` and `outcome`, so an agent can check arguments that `expect performed` does not. For [the dropped zero](#a-bug-only-an-example-catches-a-dropped-zero) of section 10.4:

```json include="steps/09-dropped-zero/expected/commands/json-test.txt#L2"
{"schema":"una.test/1","tier":1,"redacted":false,"diagnostics":[],"examples":[{"module":"shipping","name":"an order of 49.99 pays 4.90","outcome":"fail","reason":"it is false, with `result` = `49`","expectation":{"file":"src/shipping.una","line":24,"text":"expect result == 490"},"result":{"kind":"ok","value":"49"},"trace":[]},{"module":"shipping","name":"an order of exactly 50.00 ships for free","outcome":"pass","reason":null,"expectation":null,"result":{"kind":"ok","value":"0"},"trace":[]}],"passed":1,"failed":1}
```

The compact rule: *an example has `given` lines for every capability its `do` line needs, one `do` line, and one or more `expect` lines; it never uses a host capability.*
:::

### Recap

:::recap
- Write an `example` next to the code: a name a reader understands, one `do` line, and `expect` lines that must hold.
- `una test .` checks the package, runs every example in a fresh machine, and exits with code 1 when one fails.
- Give every failure path its own example with `expect fails`, naming a variant of the `do` call's error kind.
- Replace each service with a fake handler installed by `given`. Examples never use host capabilities.
- Check effects with `expect performed` and `expect not performed`: what a call must do, and what it must not.
- A fake is checked against the operations it implements, so it keeps their promises.
- Prove in `ensures` what must hold for every input; pin exact values and effects with examples. Trace rules to contracts with `requirement`, `derived from` and `una trace`.
:::

### Reference

:::reference
- Construct pages: [`example`](/docs/language/examples/example/), [`requirement` and `derived from`](/docs/language/requirements/requirement/), [`handler`](/docs/language/capabilities/handler/), [`with`](/docs/language/capabilities/with/), [`capability` and `op`](/docs/language/capabilities/capability/), [`ensures`](/docs/language/functions/ensures/), [`attempt`](/docs/language/errors/attempt/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/), [U1005](/docs/errors/U1005/), [U3001](/docs/errors/U3001/), [U3014](/docs/errors/U3014/), [U5001](/docs/errors/U5001/)
- Specification: [requirements and examples](/docs/spec/08-requirements-and-examples/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [verification](/docs/spec/12-verification/), [dynamic semantics](/docs/spec/11-dynamic-semantics/), [diagnostics and the command line](/docs/spec/13-diagnostics-and-abi/)
:::
