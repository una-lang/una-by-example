---
learn: "7"
title: Contracts and the verifier
editions: ["0.2"]
codes: [U1001, U2014, U2016, U5001, U5002]
time: 60
builds: The billing step of a store, which prices an invoice, applies a coupon, splits the payment and refunds
prerequisites: ["3", "4", "5", "6"]
template: 2
nav: ["requires", "ensures and counterexamples", "Refined kinds and predicates", "What the verifier proves", "Contracts at the boundary", "Day-to-day: billing", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 7 Contracts and the verifier

Billing code is where a small slip costs real money: a coupon that is worth more than the order, a refund that pays back more than was paid, a rate typed as 110 percent. Tests catch the cases someone thought of. In Una you write the rule itself into the function's header, as a contract, and the verifier proves before the program runs that the rule holds for every input. When it does not, the verifier shows you the input that breaks it. This chapter writes contracts for the billing step of a store, and shows how to read what the verifier says.

## What you'll build

:::build
The billing step of a small store. It prices the lines of an invoice, applies a coupon, pays from store credit first and the rest by card, and refunds part of the invoice later, refusing a refund of more than was paid:

```text include="day-to-day/expected/output.txt"
2 x LAMP-01 at 19.90: 39.80
1 x DESK-02 at 149.00: 149.00
subtotal 188.80, coupon -18.88, total 169.92
store credit 50.00, card 119.92
refund 39.80: paid back
refund 200.00: refused, only 169.92 was paid
```

You will learn to:

- state what a function needs with `requires`, and what it promises with `ensures`;
- read a counterexample, and turn it into a fix and an example;
- make the rules of your data part of its type, with refined kinds and predicates;
- list what the verifier proved with `una obligations`, and tell a refuted proof (U5001) from one the solver could not decide (U5002);
- check data from outside once, at the boundary, and trace contracts back to the business rules they come from.
:::

## Why it works this way

In most languages, the rules of a function live in comments, in assertions that run with the code, and in tests. A comment can be wrong. An assertion fires in production, on the input nobody tried. A test covers the inputs someone wrote down; the bug is in another: a coupon worth more than a cheap order, a refund on an order paid with store credit.

Una moves the rules into the header and proves them:

:::steps
1. **A contract is part of the header.** `requires` states what must hold of the arguments, and `ensures` what holds of the result. A reader learns what a function does from its header alone.
2. **The verifier proves every contract, for every input.** `una check` turns each rule into a question for an SMT solver, Z3, at the version `verification.lock` pins. A rule that fails for some input is refuted, and the diagnostic shows that input: a counterexample.
3. **Nothing unproven passes.** When the solver cannot decide a question, the result is an error too, never a silent pass. A program that checks holds no value that breaks its contracts, and its contracts cost nothing when it runs. The exceptions are visible: `checked`, which tests at run time, and the standard library and capability operations, whose contracts are trusted, not proven.
:::

The price: you state your rules in a small language the solver understands, and sometimes write a guard to give it a fact it cannot see. In return, the checker finds the input that breaks a rule before a customer does.

> [!KEY]
> A contract is a rule the verifier proves for every input before the program runs. When it cannot prove the rule, it does not pass the program: it shows the input that breaks the rule, or says that it cannot decide.

## 7.1 Preconditions: `requires`

### What a contract is

When a store hires a courier, the two sign an agreement. The store promises to hand over parcels that are packed, labeled and under 30 kilograms. The courier promises to deliver each one within two days. Each side knows what it must do and what it may count on, and neither has to watch how the other works.

A function and the code that uses it have the same kind of agreement. A **function** ([chapter 3](/learn/functions/)) is a named piece of code that takes values, its **parameters**, and gives back one value, its **result**. The code that uses a function is its **caller**, and the values the caller passes are the **arguments**. A **contract** is the agreement between the two, written into the function's **header**: the line with its name, parameters and result type, and the clause lines under it, up to `=`. The **body**, after `=`, is how the function keeps its side.

A contract has two halves:

- A **precondition**, written `requires`, is what the caller promises about the arguments. It is this section's subject.
- A **postcondition**, written `ensures`, is what the function promises about its result. [Section 7.2](#s7-2) covers it.

What makes a contract in Una more than a comment is that una checks both halves, for every caller and every input, before the program runs.

### Each step is a package

Each step of this chapter is a package, as in [chapter 1, Hello, Una](/learn/hello/#s1-1): a directory with `una.toml`, `verification.lock` and the module under `src/`. The manifest names the package and the module that `una run` starts:

```toml include="steps/02-requires/una.toml" title="steps/02-requires/una.toml"
[package]
name = "installments"
version = "0.1.0"
edition = "0.2"

[run]
entry = "installments"
grants = ["console"]
```

`verification.lock` pins the solver and is the same in every example: copy it from chapter 1, or take the step's package, whole, from the chapter's download, `07-contracts.tar.gz`. Then, in the package's directory:

```sh
una check .
una run .
```

### What a precondition states

A precondition states what must hold of the arguments for a call to make sense. `requires count >= 1` on a function that divides by `count` says that a call with 0 is a mistake of the caller, not a case the function handles.

A precondition is a condition: an expression that is `true` or `false`, such as `count >= 1`, `price >= 0` or `skus.len > 0`. It may read every parameter of the function. It is checked at both ends:

- **At every call,** the verifier proves the precondition for the arguments given. A call it cannot prove does not check.
- **In the body,** the precondition is a fact the verifier assumes. Here it proves that the division never divides by zero.

### Why a function needs a precondition

Some functions only make sense for some arguments. Splitting a total into monthly installments divides it by the number of months, and a division by zero has no answer. Here is that function with nothing to say so:

```una include="steps/01-no-requires/src/installments.una" title="steps/01-no-requires/src/installments.una"
module installments

--- One of `count` equal monthly installments of `total` cents, rounded down.
installment(total: Int, count: Int) -> Int = total / count

--- What the customer pays each month. The checkout form allows 0 months, which means
--- paying everything now.
monthly(total: Int, months: Int) -> Int = if months < 1 then total else installment(total, count: months)

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{installment(12000, count: 3)} a month for 3 months")
  @console.print("{monthly(12000, months: 0)} now, or {monthly(12000, months: 4)} a month for 4 months")
```

In many languages this code runs, and works, until some call passes 0 months. Then the division fails while the program runs: the checkout stops in front of a customer, or a later line works with a value that means nothing. A test finds the problem only if someone thought to try 0.

Una does not run it. `una check .` reports:

```text include="steps/01-no-requires/expected/rendered.txt"
[U5001] Error: division obligation `count != 0` is refuted
   ╭─[ src/installments.una:4:46 ]
   │
 4 │ installment(total: Int, count: Int) -> Int = total / count
   │                                              ──────┬──────
   │                                                    ╰──────── division obligation `count != 0` is refuted
   │
   │ Help: repair 1: guard the division with `if count != 0`
   │
   │ Note 1: obligation ob-69e79e4e9a3b (division) is refuted: count != 0
   │
   │ Note 2: counterexample: count = 0
   │
   │ Note 3: run `una explain U5001` for an explanation
───╯
```

Every division by a value that is not a literal must be proven safe: its divisor must not be 0. Here nothing tells una that `count` is never 0, and the line `Note 2` gives the case that breaks: `count = 0`. The function has no way to say "never call me with 0". A precondition is that way.

### What the verifier is

The **verifier** is the part of una that proves things about your program without running it. `una check .` runs it after the other checks pass. It works in three steps:

1. **It lists what must be true.** Every place where the program relies on a fact becomes a question: "is `count != 0` here, whatever the inputs?" Such a question is a **proof obligation**. A division gives one, each `requires` gives one at every call, and each `ensures` gives one for the body.
2. **It asks a solver.** A **solver** is a program that answers such questions by reasoning about every possible value at once, not by trying values one after another. Una uses the solver Z3, at the exact version that `verification.lock` names, so every machine gets the same answers.
3. **It reports the answer.** An obligation is **proven** when it holds for every input, which needs no message. It is **refuted** when some input breaks it: that is U5001, and the input is the **counterexample**, shown on the line `Note 2: counterexample: …`. When the solver cannot decide, the obligation is **unknown**: that is U5002, an error too ([section 7.4](#s7-4)).

A test runs the code on the inputs someone wrote down. A check that runs with the program, an assertion in other languages, stops the program on the input that breaks it, after the fact. The verifier covers every input, before the program runs, and its proofs cost nothing when the program runs. In exchange, you write your conditions in a small language the solver can decide ([the refinement language](#the-refinement-language), in section 7.3).

### How to write `requires`

A `requires` clause is the word `requires` and a condition, on a line of its own under the header, indented two spaces, before `=`. A function with a clause is written in the long form ([chapter 3](/learn/functions/#s3-2)): the header, the clauses, `=` alone on its line, then the body. A function may have any number of clauses, and every one must hold.

The step of this part shows every form a precondition takes. Each function is small, and `main` calls each one with arguments that meet its precondition:

#### One condition

The simplest precondition names one parameter:

```una include="steps/04-clauses/src/checkout.una#unit_price" title="steps/04-clauses/src/checkout.una"
--- The price of one unit when a pack of `units` costs `pack_cents`, rounded down.
unit_price(pack_cents: Int, units: Int) -> Int
  requires units >= 1
=
  pack_cents / units
```

The body divides by `units`. The clause makes that safe, and every caller must show that its `units` is at least 1.

#### Several conditions, several clauses

A precondition may relate parameters to each other. Write each condition as a clause of its own:

```una include="steps/04-clauses/src/checkout.una#after_coupon" title="steps/04-clauses/src/checkout.una"
--- The price after a coupon worth `off` cents. Three clauses, and all of them must hold.
after_coupon(price: Int, off: Int) -> Int
  requires price >= 0
  requires off >= 0
  requires off <= price
=
  price - off
```

The three clauses hold together, as if joined by `and`. Separate lines read better, and when a call breaks one, the message names that one. `requires off <= price` is a condition on two parameters: a coupon may not take off more than the price.

#### Fields and lengths

A condition may read the fields of a record parameter and the length of a list or of a text. It may join conditions with `and`, and `or` and `not` work the same way:

```una include="steps/04-clauses/src/checkout.una#line_cents..family" title="steps/04-clauses/src/checkout.una"
--- What one line costs. The clause reads two fields of the line.
line_cents(line: CartLine) -> Int
  requires line.quantity >= 1 and line.unit_cents >= 0
=
  line.quantity * line.unit_cents

--- The average units of the lines of a delivery, rounded down.
average_units(quantities: List[Int]) -> Int
  requires quantities.len > 0
=
  quantities.sum() / quantities.len

--- The product family of a SKU: its first four characters, as `LAMP` in `LAMP-01`.
family(sku: Text) -> Text
  requires sku.len >= 4
=
  sku.slice(start: 0, end: 4)
```

`average_units` divides by `quantities.len`, so it needs a list that is not empty. `family` cuts the first four characters with `slice`, which has a precondition of its own in the prelude: the cut must lie inside the text. `requires sku.len >= 4` is what lets `family` meet it.

#### A condition for one case: `implies` and `is`

`a implies b` reads "if `a`, then `b`". It holds whenever `a` is false, so it states a rule for one case only. `zone is Abroad` tests the variant of a sum kind ([chapter 4](/learn/kinds/)):

```una include="steps/04-clauses/src/checkout.una#shipping_cents" title="steps/04-clauses/src/checkout.una"
--- What shipping costs, in cents, for a parcel of `grams` grams. Abroad, a parcel weighs at
--- most 20 kilograms.
shipping_cents(zone: Zone, grams: Int) -> Int
  requires grams >= 1
  requires zone is Abroad implies grams <= 20000
=
  when zone
    is Local -> 495
    is National -> 795 + grams / 1000 * 100
    is Abroad -> 2500 + grams / 1000 * 300
```

A local or national parcel may weigh anything from 1 gram up. Only a parcel abroad must weigh at most 20,000 grams.

#### A named condition

When the same condition appears in many clauses, give it a name with a `predicate`, and write `requires fits(off, price)`. [Predicates](#predicates-named-conditions), in section 7.3, show how.

#### Running the precondition forms

`main` calls each function once:

```una include="steps/04-clauses/src/checkout.una#main" title="steps/04-clauses/src/checkout.una"
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("one unit of a pack of 4: {unit_price(1990, units: 4)}")
  @console.print("after a coupon: {after_coupon(1990, off: 500)}")
  let one_line = line_cents(CartLine(sku: "LAMP-01", quantity: 2, unit_cents: 1990))
  @console.print("one line: {one_line}")
  @console.print("average units: {average_units([2, 1, 3])}")
  let sku = "LAMP-01"
  @console.print("family of {sku}: {family(sku)}")
  @console.print("shipping: {shipping_cents(National, grams: 2300)} and {shipping_cents(Abroad, grams: 1500)}")
  @console.print("weekly price: {weekly_price(1990)} and {weekly_price(300)}")
```

`una run .` prints:

```text include="steps/04-clauses/expected/output.txt"
one unit of a pack of 4: 497
after a coupon: 1490
one line: 3980
average units: 2
family of LAMP-01: LAMP
shipping: 995 and 2800
weekly price: 1490 and 0
```

Each call is proven before it runs. `unit_price(1990, units: 4)` gives the verifier the literal 4, and `4 >= 1` holds. `family(sku)` passes a text whose value the verifier knows, `"LAMP-01"`, of length 7.

### Installments that never divide by zero

Back to installments, now with the precondition. The step splits a total into monthly installments:

:::steps
```una include="steps/02-requires/src/installments.una" title="steps/02-requires/src/installments.una" verified="check, run"
module installments

--- One of `count` equal monthly installments of `total` cents, rounded down.
installment(total: Int, count: Int) -> Int
  requires count >= 1
=
  total / count

--- What the customer pays each month. The checkout form allows 0 months, which means
--- paying everything now.
monthly(total: Int, months: Int) -> Int = if months < 1 then total else installment(total, count: months)

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{installment(12000, count: 3)} a month for 3 months")
  @console.print("{monthly(12000, months: 0)} now, or {monthly(12000, months: 4)} a month for 4 months")
```

1. **`requires count >= 1`.** A clause of the long form, under the header and before `=`. A function can have several `requires` clauses, and they all hold together.
2. **`total / count`.** Every division by a value that is not a literal is a proof obligation: the divisor is not zero. The precondition proves it.
3. **`installment(12000, count: 3)`.** The verifier proves `3 >= 1` at the call. With a literal, the proof is immediate.
4. **`if months < 1 then total else installment(total, count: months)`.** `months` comes from a checkout form and can be 0. In the `else` branch, the verifier knows that `months < 1` is false, so it proves `months >= 1` for the call.
:::

`una run .` prints:

```text include="steps/02-requires/expected/output.txt"
4000 a month for 3 months
12000 now, or 3000 a month for 4 months
```

### How a precondition is checked

#### What the verifier knows at a call

At each call, the verifier proves the callee's precondition with the arguments in place of the parameters. It can use every fact it has at that line:

- **Literals:** `installment(12000, count: 3)` gives `3 >= 1`.
- **The branch the call is in:** inside `else` of `if months < 1`, it knows `months >= 1`.
- **The caller's own `requires`:** a function that requires `n >= 2` may call `installment` with `n`.
- **What other calls promise:** the `ensures` of a function called earlier on the path ([section 7.2](#s7-2)).
- **Kinds:** a value of a refined kind carries its condition ([section 7.3](#s7-3)).

It never uses what a function's body does, only what its header says. So a precondition is part of the function's public face: change it, and every call is checked again.

#### Inside the body

Inside the function, each `requires` is a fact. The verifier assumes it and uses it to prove the obligations of the body: the division in `installment`, the `slice` in `family`. The body never checks the condition itself, and it costs nothing when the program runs.

#### A call that does not meet the precondition

Remove the guard from `monthly` and call `installment` directly. `una check .` now refutes the call, and says why:

```diff include="steps/02-requires..steps/03-unguarded:src/installments.una" context="1" title="src/installments.una"
--- a/src/installments.una
+++ b/src/installments.una
@@ -10,3 +10,3 @@
 --- paying everything now.
-monthly(total: Int, months: Int) -> Int = if months < 1 then total else installment(total, count: months)
+monthly(total: Int, months: Int) -> Int = installment(total, count: months)
 
```

```text include="steps/03-unguarded/expected/rendered.txt"
[U5001] Error: precondition `months >= 1` of this call is refuted
    ╭─[ src/installments.una:11:43 ]
    │
  5 │   requires count >= 1
    │            ─────┬────
    │                 ╰────── requires clause
    │
 11 │ monthly(total: Int, months: Int) -> Int = installment(total, count: months)
    │                                           ────────────────┬────────────────
    │                                                           ╰────────────────── precondition `months >= 1` of this call is refuted
    │
    │ Help 1: repair 1: strengthen the type of the parameter `months` to a refined kind that implies `months >= 1`
    │
    │ Help 2: repair 2: add `requires months >= 1` to the enclosing function; its callers then prove it
    │
    │ Help 3: repair 3: add a guard (`if` or a `when` arm) that handles the values where `months >= 1` does not hold
    │
    │ Help 4: repair 4 (escape: checked; a runtime test replaces the static proof: the program fails at run time where the proof would have rejected it; it counts against [escape_budget] and is listed in the build report): check the value with `checked(value, months >= 1) else fail <Variant>`
    │
    │ Note 1: obligation ob-b0ef023087ff (precondition) is refuted: months >= 1
    │
    │ Note 2: counterexample: months = 0
    │
    │ Note 3: run `una explain U5001` for an explanation
────╯
```

Read the diagnostic from the top. The first line names the obligation, a precondition, and its goal, `months >= 1`, written with the caller's argument in place of `count`. The two marks show the clause that asked for it and the call that does not meet it. `Note 2` is the counterexample: with `months = 0`, the goal is false. The help lines are the ranked repairs: a stronger type for `months`, a `requires` on `monthly` that moves the obligation to its callers, a guard, and last `checked`, a test at run time that counts against a budget ([chapter 6, Failure](/learn/failure/#s6-4)).

#### What a `requires` clause may say

- A `requires` clause reads the parameters as the caller passes them. It cannot name the result: `result` belongs to `ensures`, and elsewhere it is U2012.
- It is written in the refinement language: no calls of ordinary functions, and products and divisions only by a literal. Anything else is U2014 ([a contract outside the refinement language](#a-contract-outside-the-refinement-language-u2014)).

### A precondition, a guard or a kind

:::decide
**Which to use:**

| The bad value… | Use |
| --- | --- |
| Is a mistake of the caller, which can always avoid it | `requires`: every caller proves it |
| Can come from a person or another system | A guard or a failure in the function that receives it ([section 7.5](#s7-5)) |
| Is impossible by the type already | Nothing: a refined kind ([section 7.3](#s7-3)) carries the fact |
| Holds of every value of a kind, everywhere | A refined kind, instead of the same `requires` on many functions |
| Can only be decided by running code, such as the format of a text | `checked` with an opaque predicate ([section 7.3](#s7-3)) |
:::

A precondition moves work to the callers: each one must show the condition. That is right when the condition is the caller's to keep, as "never 0 months" is. When the value comes from outside the program, no caller can promise anything about it, and the function that receives it must check it.

### Check yourself: preconditions

`weekly_price` takes the weekly coupon of 5.00 off a price, and turns a price below 5.00 into 0:

```una include="steps/04-clauses/src/checkout.una#weekly_price" title="steps/04-clauses/src/checkout.una"
--- The price on a product page after the weekly coupon of 5.00. A price below 5.00 becomes 0.
weekly_price(price: Int) -> Int
  requires price >= 0
=
  if price < 500 then 0 else after_coupon(price, off: 500)
```

It calls `after_coupon` from [Several conditions, several clauses](#several-conditions-several-clauses), with its three clauses. Now drop the `if`, and write the body as `after_coupon(price, off: 500)`. Does it still check? If not, which clause fails, and for which price?

:::answer Show the answer
It does not check. `price >= 0` holds by `weekly_price`'s own precondition, and `500 >= 0` holds for the literal. `500 <= price` is the clause no fact supports:

```text include="steps/05-weekly/expected/rendered.txt#L1,L22"
[U5001] Error: precondition `500 <= price` of this call is refuted
    │ Note 2: counterexample: price = 0
```

Any price below 500 breaks it, and the counterexample shows one. The `if` was what proved the clause: in the `else` branch, `price < 500` is false.
:::

One more, without code. `unit_price` requires `units >= 1`. Which of these calls check?

1. `unit_price(1990, units: 4)`.
2. `unit_price(1990, units: 0)`.
3. `unit_price(cents, units: packs)`, inside a function that has `requires packs >= 2`.
4. `unit_price(cents, units: packs)`, inside a function that says nothing about `packs`.

:::answer Show the answer
Calls 1 and 3 check. In call 1 the literal 4 is at least 1. In call 3 the caller's own precondition, `packs >= 2`, implies `packs >= 1`. Call 2 is refuted: 0 is not at least 1, and the literal itself is the case. Call 4 is refuted too, with a value of `packs` below 1 as the counterexample: nothing tells the verifier what `packs` holds. A guard, a `requires` on the caller, or a refined kind must supply the fact.
:::

## 7.2 Postconditions: `ensures` and counterexamples

### What a postcondition promises

A postcondition is the function's half of the contract: what holds of the result when the function returns. Inside the clause, `result` names the value returned. The verifier proves the clause on every path that returns, and every caller may then assume it without reading the body.

Think of a shop's guarantee printed on a receipt: "this price never goes up after you pay". You do not need to know how the shop computes its prices to rely on it. A postcondition is that kind of promise, made by a function to every caller, and una holds the function to it.

### Why callers need a promise

A caller knows a function only by its header. Here `after_coupon` has preconditions but promises nothing, and `left_on_card`, which calls it, promises that a gift card never ends below 0:

```una include="steps/06-no-promise/src/coupons.una#after_coupon..left_on_card" title="steps/06-no-promise/src/coupons.una"
--- The price after a coupon worth `off` cents.
after_coupon(price: Int, off: Int) -> Int
  requires price >= 0
  requires off >= 0
=
  if off > price then 0 else price - off

--- What is left of a gift card after it pays for an order.
left_on_card(card: Int, price: Int) -> Int
  requires card >= 0
  requires price >= 0
  ensures result >= 0
=
  let due = after_coupon(price, off: card)
  card - (price - due)
```

Read the body of `after_coupon`, and the promise of `left_on_card` holds: the coupon never takes off more than the price. But `una check .` refutes it:

```text include="steps/06-no-promise/expected/rendered.txt"
[U5001] Error: postcondition of `left_on_card` is refuted
    ╭─[ src/coupons.una:17:3 ]
    │
 14 │   ensures result >= 0
    │           ─────┬─────
    │                ╰─────── ensures clause
    │
 17 │   card - (price - due)
    │   ──────────┬─────────
    │             ╰─────────── postcondition of `left_on_card` is refuted
    │
    │ Help 1: repair 1: add a guard or an arm so that the failing path returns a value for which `result >= 0` holds
    │
    │ Help 2: repair 2: adjust the `ensures` clause
    │
    │ Note 1: obligation ob-3376a2cf2fdd (postcondition) is refuted: result >= 0
    │
    │ Note 2: counterexample: card = 0, price = 0, result = -1
    │
    │ Note 3: run `una explain U5001` for an explanation
────╯
```

The verifier does not read the body of `after_coupon` when it checks `left_on_card`. It reads only its header, and the header says nothing about the result, so `due` could be any integer. `Note 2` shows a card of 0 and a price of 0 for which the result is −1. For that, `due` must be −1, which the counterexample leaves out. It is not a run: the real `after_coupon` never returns a negative `due`. It is what the header allows.

There is a reason the verifier works this way. If it read every body, a change to `after_coupon`'s body could silently break a proof in `left_on_card`, or in any of a hundred callers. By reading headers only, each function is checked once, against its own contract, and a caller depends on the promise, not on the code behind it. So a function promises in its header exactly what its callers need.

### How to write `ensures`

An `ensures` clause is the word `ensures` and a condition, on its own line under the header, before `=`. It sits with the `requires` clauses, and a function may have any number of each. The condition may read the parameters, as the caller passed them, and `result`, the value the function returns. Like `requires`, it is written in the refinement language.

The step of this part shows each form. `main` prints what each function returns:

```una include="steps/07-promises/src/stockroom.una#Shelf..Packing" title="steps/07-promises/src/stockroom.una" caption="the kinds"
--- How full a shelf is.
kind Shelf = Empty | Low | Stocked

--- How `units` units pack in boxes of 6, and how many stay loose.
kind Packing
  boxes: Int
  loose: Int
```

#### A promise for some cases: `implies`

A promise may cover only the cases a caller needs. `status` promises what an empty shelf and a full one give, and says nothing about the shelves in between:

```una include="steps/07-promises/src/stockroom.una#status" title="steps/07-promises/src/stockroom.una"
--- How full a shelf of `units` units is. The clauses state the two cases a caller relies on,
--- and leave the case between them to the body.
status(units: Int) -> Shelf
  requires units >= 0
  ensures units == 0 implies result is Empty
  ensures units >= 10 implies result is Stocked
=
  if units == 0 then Empty else if units < 10 then Low else Stocked
```

`result is Empty` tests the variant of the result. `units == 0 implies result is Empty` holds for every input: when `units` is not 0, it says nothing.

#### The whole answer

A clause can state the result exactly. Then a caller knows everything the function does, from its header alone:

```una include="steps/07-promises/src/stockroom.una#free_shipping" title="steps/07-promises/src/stockroom.una"
--- Whether an order ships free. The clause gives the whole answer.
free_shipping(total: Int) -> Bool
  ensures result == (total >= 5000)
=
  total >= 5000
```

`result == (total >= 5000)` compares two `Bool` values: the result is `true` exactly when the total is at least 5000.

#### Lengths and fields of the result

A promise may speak of the length of a list result, or of the fields of a record result:

```una include="steps/07-promises/src/stockroom.una#add_sku..pack" title="steps/07-promises/src/stockroom.una"
--- The SKUs of a cart, with one more at the end.
add_sku(skus: List[Text], sku: Text) -> List[Text]
  ensures result.len == skus.len + 1
=
  skus.append(item: sku)

--- How `units` units pack in boxes of 6. The clauses speak of the fields of the result.
pack(units: Int) -> Packing
  requires units >= 0
  ensures result.boxes * 6 + result.loose == units
  ensures result.loose >= 0 and result.loose < 6
=
  Packing(boxes: units / 6, loose: units mod 6)
```

`add_sku` passes on the promise of `append` from the prelude: one more element. `pack` has two clauses, which hold together. The first relates the two fields: boxes of 6 and the loose units add up to `units`. The second bounds one field. `result.boxes * 6` is allowed in a clause, since one side of the product is a literal.

#### The value of an `edit` parameter: `old`

A parameter declared `edit` is passed in and out: the function may change the caller's binding ([chapter 12](/learn/memory-and-concurrency/#s12-2) covers it). In `ensures`, the parameter's name means its value at the end, and `old(name)` its value when the call began:

```una include="steps/07-promises/src/stockroom.una#restock" title="steps/07-promises/src/stockroom.una"
--- Adds `units` to the count of a shelf. `old(shelf)` is the count before the call.
restock(edit shelf: Int, units: Int) -> Unit
  requires units >= 0
  ensures shelf == old(shelf) + units
=
  shelf = shelf + units
```

`old` is allowed only in `ensures`, and only on an `edit` parameter.

#### Running the promise forms

```text include="steps/07-promises/expected/output.txt#L1-L5"
Empty Low Stocked
free shipping at 4999: false, at 5000: true
["LAMP-01", "RUG-07"]
20 units: 3 boxes and 2 loose
lamps on the shelf: 10
```

### A coupon that never goes negative

A coupon is a good first case of a real rule. It takes some cents off a price, and two rules hold whatever the coupon: the price never becomes negative, and it never goes up.

:::steps
```una include="steps/08-ensures/src/coupons.una" title="steps/08-ensures/src/coupons.una" verified="check, run, test"
module coupons

--- The price after a coupon worth `off` cents. A coupon never makes a price negative, and
--- never raises it.
after_coupon(price: Int, off: Int) -> Int
  requires price >= 0
  requires off >= 0
  ensures result >= 0
  ensures result <= price
  ensures off <= price implies result == price - off
=
  if off > price then 0 else price - off

--- What is left of a gift card after it pays for an order.
left_on_card(card: Int, price: Int) -> Int
  requires card >= 0
  requires price >= 0
  ensures result >= 0
=
  let due = after_coupon(price, off: card)
  card - (price - due)

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{after_coupon(1990, off: 500)} {after_coupon(300, off: 500)}")
  @console.print("{left_on_card(5000, price: 1990)} {left_on_card(1000, price: 1990)}")

example "a coupon worth more than the price gives 0"
  do after_coupon(0, off: 1)
  expect result == 0
```

1. **`ensures result >= 0` and `ensures result <= price`.** The two rules. They hold on both branches of the `if`, and the verifier proves each one.
2. **`ensures off <= price implies result == price - off`.** A third clause says what the result is when the coupon fits. `implies` reads "if… then…": the clause says nothing when `off > price`.
3. **`left_on_card`.** A caller. It knows `after_coupon` only by its header, never by its body. With the first two clauses alone, it knows only that `due` is between 0 and `price`, which is not enough to prove `result >= 0`. The third clause gives it what it needs.
4. **The example.** It pins down the case where the coupon is worth more than the price. [From a counterexample to an example](#from-a-counterexample-to-an-example) shows where it comes from.
:::

`una run .` prints:

```text include="steps/08-ensures/expected/output.txt"
1490 0
3010 0
```

### Reading a counterexample

Now write the body most people write first, `price - off`, and check:

```diff include="steps/08-ensures..steps/09-counterexample:src/coupons.una" context="1" title="src/coupons.una"
--- a/src/coupons.una
+++ b/src/coupons.una
@@ -11,3 +11,3 @@
 =
-  if off > price then 0 else price - off
+  price - off
 
```

```text include="steps/09-counterexample/expected/rendered.txt"
[U5001] Error: postcondition of `after_coupon` is refuted
    ╭─[ src/coupons.una:12:3 ]
    │
  8 │   ensures result >= 0
    │           ─────┬─────
    │                ╰─────── ensures clause
    │
 12 │   price - off
    │   ─────┬─────
    │        ╰─────── postcondition of `after_coupon` is refuted
    │
    │ Help 1: repair 1: add a guard or an arm so that the failing path returns a value for which `result >= 0` holds
    │
    │ Help 2: repair 2: adjust the `ensures` clause
    │
    │ Note 1: obligation ob-3bf1d4af758b (postcondition) is refuted: result >= 0
    │
    │ Note 2: counterexample: off = 1, price = 0, result = -1
    │
    │ Note 3: run `una explain U5001` for an explanation
────╯
```

The diagnostic points at the returned expression, `price - off`, and at the clause it breaks, `ensures result >= 0`. The counterexample is `off = 1, price = 0, result = -1`: a coupon of 1 cent on a free item. Run the body by hand on those values and the result is −1, so the rule is broken.

The solver often picks the smallest numbers that break the rule, such as 0 and 1, so a case that looks artificial usually stands for a real one: here, any coupon worth more than its order.

### When the body calls other functions

A counterexample gives values of the parameters, and of `result`, for which the contract breaks. When the body has no calls, as here, it is a case you can run by hand. When the body calls other functions, the verifier knows each call only by the callee's header, so a call's result in the counterexample can be any value that header allows, even one the callee never returns. Then the values are not a run, but they still point at the problem: the body relies on something the callee does not promise ([a caller that needs a promise the callee does not make](#a-caller-that-needs-a-promise-the-callee-does-not-make-u5001)), or it does not handle an input it should ([exercise 3](#exercise-3-a-second-refund)).

### From a counterexample to an example

Two things to do with a counterexample:

1. **Fix the code or the contract.** Here the code is wrong: a coupon larger than the price gives 0. Sometimes the contract promises more than you meant.
2. **Keep the case as an example,** when it is a run, as this one is. The example in `coupons.una` is this counterexample, written as a test. The proof already covers it, but the example documents the case for a reader and shows it in `una test .`:

```text include="steps/08-ensures/expected/commands/test.txt#L2-L4"
example coupons "a coupon worth more than the price gives 0" ... ok

1 example: 1 passed, 0 failed
```

### How a postcondition is checked

#### Every path that returns

A body can return in several places: each branch of an `if`, each arm of a `when`. The verifier proves each `ensures` clause on every one of them, with the facts of that path: the function's `requires`, the condition of the branch, and the promises of the calls made on the way. One path that breaks the clause is enough for U5001, and the diagnostic points at that path's returned expression.

#### What a caller gets

After a call, the caller may assume every `ensures` clause of the callee, with its own arguments in place of the parameters. After `let due = after_coupon(price, off: card)`, `left_on_card` knows `due >= 0`, `due <= price`, and `card <= price implies due == price - card`. Promises add up: each function's `ensures` is a fact for the next one, and in [the day-to-day program](#s7-6) a chain of them proves that no invoice is negative.

The standard library has contracts too, and the verifier trusts them without reading their bodies. `min` promises a result no larger than either of its two arguments, and equal to one of them.

#### What `ensures` does not cover

> [!NOTE]
> `ensures` describes normal returns only. A function that fails, with `fail`, returns no value, and its postcondition says nothing about that path. Contracts also do not prove that a function ends: they hold *if* it returns.

#### What an `ensures` clause may say

`result` is allowed only in `ensures` and in the `expect` lines of examples (U2012 elsewhere). The rest of the rules of a `requires` clause apply: the parameters, the refinement language, no calls but predicates.

### A contract or an example

A postcondition and an example both say something about the result, but not the same thing:

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| State a rule that holds for every input, such as "never negative" | `ensures` |
| Give callers a fact they need to prove their own contracts | `ensures` |
| Pin down one exact answer, such as "10% of 188.85 is 18.88" | an `example` ([chapter 10](/learn/testing/)) |
| Keep a counterexample as a case a reader can see | an `example` |
| Describe what the function is for, in words | a doc comment (`---`) |
:::

How much to promise is a choice. Promise what the callers need and what will stay true. A promise that states the exact result, as `free_shipping`'s does, gives callers the most, and ties the function's body to it for good. A bound, such as `result <= amount`, leaves the body free to change, for example to round differently.

### Check yourself: postconditions

`points` gives a customer one loyalty point for each whole 1.00, and at most 100 points for one order:

```una include="steps/07-promises/src/stockroom.una#points" title="steps/07-promises/src/stockroom.una"
--- The loyalty points of an order: one for each whole 1.00, and at most 100.
points(total: Int) -> Int
  requires total >= 0
  ensures result >= 0
  ensures result <= 100
=
  min(total / 100, b: 100)
```

Does it check? And what does `points(25000)` return?

:::answer Show the answer
It checks. The body is a call of `min`, whose contract promises a result no larger than `b`, which is 100, and equal to one of its two arguments. `total / 100` is at least 0, since `total` is, and 100 is too, so the result is at least 0. Both clauses follow from `min`'s promise, without a branch in the body.

```text include="steps/07-promises/expected/output.txt#L6"
points for 250.00: 100
```

25000 cents is 250 whole units of 1.00, and `min` keeps it at 100.
:::

A second one: what may a caller assume about `status(5)`?

:::answer Show the answer
Nothing but its type: the result is a `Shelf`. Both clauses of `status` speak of other inputs, 0 and from 10 up, so for 5 they say nothing. The body returns `Low`, but a caller cannot rely on that, since the header does not promise it. To let callers rely on it, add `ensures units >= 1 and units < 10 implies result is Low`.
:::

## 7.3 Refined kinds and predicates

### A rule on the kind

A **type** says what kind of value a name holds: `Int` holds whole numbers, `Text` holds texts. A `kind` declares a type of your own ([chapter 4](/learn/kinds/)). A **refined kind** is a type with a condition attached: a base type, and a rule that every value of the kind obeys. `kind Cents = Int where it >= 0` is the integers that are not negative. In the condition, `it` stands for the value.

Think of a parcel locker that only opens for parcels below a size. You do not check each parcel's size again when you take it out: it got in, so it fits. A refined kind is that locker. A value is checked once, when it enters the kind, and from then on everyone who receives a `Cents` knows it is not negative.

A rule that holds of every value of a kind belongs on the kind. `Int in 1..99` is short for `Int where 1 <= it and it <= 99`, and `in 0..<100` would leave out 100.

### Why put a rule on a kind

A price in cents is never negative. With preconditions alone, every function that takes a price must say so, and every function that returns one must promise it:

```una include="steps/10-repeated/src/prices.una" title="steps/10-repeated/src/prices.una" verified="check, run"
module prices

--- The price after a coupon worth `off` cents. A price is never negative, so the clauses say
--- so.
after_coupon(price: Int, off: Int) -> Int
  requires price >= 0
  requires off >= 0
  ensures result >= 0
=
  if off > price then 0 else price - off

--- The price with a shipping fee added. The same rule, written again.
with_fee(price: Int, fee: Int) -> Int
  requires price >= 0
  requires fee >= 0
  ensures result >= 0
=
  price + fee

--- The price after a markdown of `cut` cents. This function forgot the rule.
marked_down(price: Int, cut: Int) -> Int = price - cut

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("after a coupon: {after_coupon(1990, off: 500)}")
  @console.print("with a fee: {with_fee(1990, fee: 495)}")
  @console.print("on the shelf label: {marked_down(1990, cut: 2500)} cents")
```

`una run .` prints:

```text include="steps/10-repeated/expected/output.txt"
after a coupon: 1490
with a fee: 2485
on the shelf label: -510 cents
```

The program checks, and the last line prints a negative price on a shelf label. The rule "a price is never negative" lives in the clauses of each function, written again each time, and `marked_down` forgot it. Nothing connects the three functions: they all take an `Int`, and an `Int` may be anything.

Put the rule on a kind, `Cents`, and make it the type of every price. Then the rule is written once, a function that returns `Cents` must prove it on every path, and a function that receives `Cents` gets it for free. `marked_down` with a result of type `Cents` would not check: `price - cut` is negative whenever the cut is larger than the price, and the verifier would refute it with such a case.

### How to write a refined kind

A refined kind is a `kind` declaration with three parts: its name, `=` and the base type, then the condition after `where`. The condition reads the value as `it`, and is written in the refinement language, like `requires` and `ensures`. The step of this part shows every form:

```una include="steps/11-refined-forms/src/catalog.una#Cents..BulkLine" title="steps/11-refined-forms/src/catalog.una" caption="the kinds"
--- An amount of money in cents. It is never negative.
kind Cents = Int where it >= 0

--- A discount in whole percent, from 0 to 100: `..` keeps both ends.
kind Percent = Int in 0..100

--- A slot on a shelf of 12 slots, numbered from 0: `..<` leaves 12 out.
kind Slot = Int in 0..<12

--- A staff discount: a `Percent` of at most 50. It holds both conditions.
kind StaffDiscount = Percent where it <= 50

--- A SKU, such as `LAMP-01`: at least four characters.
kind Sku = Text where it.len >= 4

--- A list that holds at least one element, of any type.
kind NonEmpty[T] = List[T] where it.len > 0

--- One line of a delivery. The quantity is refined in place, with `in`.
kind Line
  sku: Text
  quantity: Int in 1..99

--- A line of at least 10 units, which earns free units.
kind BulkLine = Line where it.quantity >= 10
```

#### A condition with `where`

`kind Cents = Int where it >= 0` is the general form. Any condition of the refinement language works: comparisons, `and`, `or`, `not`, `implies`, and calls of predicates ([Predicates](#predicates-named-conditions) show them).

#### A range with `in`

`Int in 0..100` is short for a `where` with two comparisons, both ends included. `Int in 0..<12` leaves the end out, which fits a count of positions: 12 slots numbered 0 to 11. `next_slot` moves to the next slot and wraps around:

```una include="steps/11-refined-forms/src/catalog.una#next_slot" title="steps/11-refined-forms/src/catalog.una"
--- The next slot of the shelf, back to 0 after the last one.
next_slot(slot: Slot) -> Slot = if slot < 11 then slot + 1 else 0
```

The result is a `Slot`, so the verifier proves both branches: `slot + 1` is below 12 when `slot < 11`, and 0 is in range.

#### Refinements of refinements, and type arguments

A refinement of a refined kind adds its condition to the first: `kind Small = Cents where it < 100` is both `>= 0` and `< 100`. The prelude already has one: `Nat`, the integers that are not negative. In the step, a staff discount is a `Percent` of at most 50, so a value of it holds both conditions:

```una include="steps/11-refined-forms/src/catalog.una#staff_pays" title="steps/11-refined-forms/src/catalog.una"
--- What a staff member pays, in percent of the price: always at least half.
staff_pays(rate: StaffDiscount) -> Percent
  ensures result >= 50
=
  100 - rate
```

`100 - rate` is a `Percent`, and at least 50, because `rate` is between 0 and 50.

> [!IMPORTANT]
> A refined kind cannot be a type argument: `List[Cents]` and `Option[Quantity]` are ill-formed (U2002). Put the refinement on a field of a record, as `Line` does with `quantity`, and use a list of the records.

#### Texts, lists and records

The base can be any type. A condition on a text or a list usually reads its length, and a condition on a record reads its fields:

```una include="steps/11-refined-forms/src/catalog.una#family..free_units" title="steps/11-refined-forms/src/catalog.una"
--- The product family of a SKU: its first four characters.
family(sku: Sku) -> Text = sku.slice(start: 0, end: 4)

--- The average units of the lines of a delivery, rounded down.
average_units(quantities: NonEmpty[Int]) -> Int = quantities.sum() / quantities.len

--- The free units of a bulk line: one for every 10 units.
free_units(line: BulkLine) -> Int
  ensures result >= 1
=
  line.quantity / 10
```

- `Sku` is a text of at least four characters, so `family` can cut four characters with `slice` with no clause of its own: the kind carries the fact.
- `NonEmpty[T]` takes a type parameter, so it works for a list of any type. `average_units` divides by the length, and the kind proves it is not 0. The argument of `NonEmpty` is a plain type here, `Int`; only a refined kind cannot be a type argument.
- `BulkLine` is a `Line` whose quantity is at least 10, so `free_units` can promise at least one free unit.

#### A range in place

A range can also be written right where a type goes, without a `kind`: on a field, as `quantity: Int in 1..99` in `Line`, or on a parameter:

```una include="steps/11-refined-forms/src/catalog.una#place" title="steps/11-refined-forms/src/catalog.una"
--- Where to put a box: a row from 1 to 5, refined in place, and a slot.
place(row: Int in 1..5, slot: Slot) -> Text = "row {row}, slot {slot}"
```

A `where` cannot be written in place: a condition other than a range needs a named kind.

#### Running the kind forms

`main` calls each function:

```text include="steps/11-refined-forms/expected/output.txt#L2-L4,L6"
after slot 4: 5, after slot 11: 0
family of LAMP-01: LAMP
average units: 2
row 2, slot 7
```

### Cents, quantities and free shipping

Now the kinds at work in a cart, with a predicate, a named condition that [Predicates](#predicates-named-conditions) explains in full:

:::steps
```una include="steps/12-refined/src/cart.una" title="steps/12-refined/src/cart.una" verified="check, run"
module cart

--- An amount of money in cents. It is never negative.
kind Cents = Int where it >= 0

--- How many units of one SKU a line may order.
kind Quantity = Int in 1..99

--- One line of a cart.
kind Line
  sku: Text
  unit_cents: Cents
  quantity: Quantity

--- An order ships free from 50.00.
predicate reflect ships_free(total: Cents) -> Bool = total >= 5000

--- What shipping costs for an order of `total` cents.
shipping(total: Cents) -> Cents
  ensures ships_free(total) implies result == 0
=
  if ships_free(total) then 0 else 495

--- The line with one more unit, up to the limit of a line.
one_more(line: Line) -> Line
=
  if line.quantity < 99
    Line(sku: line.sku, unit_cents: line.unit_cents, quantity: line.quantity + 1)
  else
    line

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Line(sku: "LAMP-01", unit_cents: 1990, quantity: 2)
  let more = one_more(lamp)
  @console.print("{more.quantity} x {more.sku}")
  @console.print("shipping {shipping(3980)}, then {shipping(5970)}")
```

1. **`kind Cents = Int where it >= 0`.** A function that takes `Cents` may assume it; one that returns `Cents` must prove it.
2. **`quantity: Quantity`.** A field of a refined kind. Building a `Line` proves the field's condition, and reading `line.quantity` gives the fact back.
3. **`predicate reflect ships_free(total: Cents) -> Bool = total >= 5000`.** A named condition. `reflect` means the verifier sees its body. Code may call a `reflect` predicate like any function, as `shipping` does.
4. **`ensures ships_free(total) implies result == 0`.** A contract that names a business rule reads as the rule.
5. **`if line.quantity < 99`.** `line.quantity + 1` enters `Quantity` again. Without the guard, the verifier refutes it with a line of 99 units, as [A value that does not fit](#a-value-that-does-not-fit) shows.
:::

`una run .` prints:

```text include="steps/12-refined/expected/output.txt"
3 x LAMP-01
shipping 495, then 0
```

### How a refined kind is checked

#### Where a value enters the kind

The verifier proves the condition at every place a value enters the kind: an argument, a returned value, a field of a record, and a `let` with the kind written. The other way needs no proof: a `Cents` goes wherever an `Int` goes.

So the work happens at the edges. `shipping` returns 0 or 495, and the verifier proves each is a `Cents`. `Line(sku: "LAMP-01", unit_cents: 1990, quantity: 2)` proves `1990 >= 0` and `2 in 1..99`. A function that only passes a `Cents` along proves nothing at all.

#### What a value of the kind gives back

Wherever a value of a refined kind is read, its condition is a fact: a parameter of the kind, a field, the result of a call that returns the kind. `family` cuts a `Sku` without a clause, and `average_units` divides by the length of a `NonEmpty` without a guard, because the condition comes with the value.

#### A value that does not fit

Take the guard out of `one_more`, and add a unit whatever the quantity:

```diff include="steps/12-refined..steps/13-one-more:src/cart.una" context="1" title="src/cart.una"
--- a/src/cart.una
+++ b/src/cart.una
@@ -23,9 +23,4 @@
 
---- The line with one more unit, up to the limit of a line.
-one_more(line: Line) -> Line
-=
-  if line.quantity < 99
-    Line(sku: line.sku, unit_cents: line.unit_cents, quantity: line.quantity + 1)
-  else
-    line
+--- The line with one more unit.
+one_more(line: Line) -> Line = Line(sku: line.sku, unit_cents: line.unit_cents, quantity: line.quantity + 1)
 
```

```text include="steps/13-one-more/expected/rendered.txt"
[U5001] Error: refinement `(line.quantity + 1) in 1..99` is refuted
    ╭─[ src/cart.una:25:91 ]
    │
  7 │ kind Quantity = Int in 1..99
    │                        ──┬──
    │                          ╰──── range
    │
 25 │ one_more(line: Line) -> Line = Line(sku: line.sku, unit_cents: line.unit_cents, quantity: line.quantity + 1)
    │                                                                                           ────────┬────────
    │                                                                                                   ╰────────── refinement `(line.quantity + 1) in 1..99` is refuted
    │
    │ Help 1: repair 1: add `requires (line.quantity + 1) in 1..99` to the enclosing function; its callers then prove it
    │
    │ Help 2: repair 2: add a guard (`if` or a `when` arm) that handles the values where `(line.quantity + 1) in 1..99` does not hold
    │
    │ Help 3: repair 3 (escape: checked; a runtime test replaces the static proof: the program fails at run time where the proof would have rejected it; it counts against [escape_budget] and is listed in the build report): check the value with `checked(value, (line.quantity + 1) in 1..99) else fail <Variant>`
    │
    │ Note 1: obligation ob-2a5905c8f53d (refinement) is refuted: (line.quantity + 1) in 1..99
    │
    │ Note 2: counterexample: line = Line#0, line.quantity = 99, line.sku = Text#0, line.unit_cents = 0
    │
    │ Note 3: run `una explain U5001` for an explanation
────╯
```

The goal is the condition of `Quantity` with the new value in place of `it`: `(line.quantity + 1) in 1..99`. The mark on `1..99` is labeled `range`, the declaration it comes from. The counterexample is a line of 99 units, the most a line may hold: one more would be 100. `Line#0` and `Text#0` stand for a line and a text the solver chose, and `line.unit_cents = 0` is one value it picked; only `line.quantity` matters here.

### Predicates: named conditions

A **predicate** is a named condition: a function that returns a `Bool`, which contracts and kinds may call. It turns a rule of the business into a word, so `requires fits(off, price)` reads as the rule it states.

#### Why name a condition

The same condition tends to appear in many places: "an order ships free from 50.00" in a precondition, a postcondition, a kind and a branch of code. Written out each time, the places can drift apart, and a change of the threshold must find them all. A predicate states the rule once, under a name, and every clause that uses it changes with it.

#### How to write a predicate

`predicate reflect name(parameters) -> Bool = condition`: the word `predicate`, the word `reflect`, a name, typed parameters, the result type `Bool`, and a body of one condition after `=`. `reflect` means the verifier sees the body: when a clause calls the predicate, the verifier reads it as its body with the arguments in place.

A `reflect` predicate is pure, uses no capabilities, cannot fail, and returns a value for every input. Its body is written in the refinement language. It may call other predicates, but never itself, directly or through another predicate (U2015).

#### Where a predicate is used

The step declares three predicates and uses them in every place a condition goes:

```una include="steps/14-predicates/src/shipping.una#Cents..thank_you" title="steps/14-predicates/src/shipping.una"
--- An amount of money in cents. It is never negative.
kind Cents = Int where it >= 0

--- An order ships free from 50.00.
predicate reflect ships_free(total: Cents) -> Bool = total >= 5000

--- A coupon fits a price when it takes off no more than the price.
predicate reflect fits(off: Cents, price: Cents) -> Bool = off <= price

--- An order ready to ship as a gift: it ships free, and no coupon was used. One predicate
--- may call another.
predicate reflect gift_ready(total: Cents, off: Cents) -> Bool = ships_free(total) and off == 0

--- An order total that ships free: a predicate in a `where` clause.
kind FreeTotal = Cents where ships_free(it)

--- The price after a coupon: a predicate in `requires`.
after_coupon(price: Cents, off: Cents) -> Cents
  requires fits(off, price)
=
  price - off

--- What shipping costs: a predicate in `ensures`, and in code.
shipping(total: Cents) -> Cents
  ensures ships_free(total) implies result == 0
=
  if ships_free(total) then 0 else 495

--- The note on a packing slip: a predicate of two arguments, called in code.
slip_note(total: Cents, off: Cents) -> Text = if gift_ready(total, off) then "gift wrap" else "standard"

--- The thank-you line of an order that ships free. It takes a `FreeTotal`, so it needs no
--- check of its own.
thank_you(total: FreeTotal) -> Text = "{total} cents, shipped free"
```

- **In `requires`:** `after_coupon` requires `fits(off, price)`, so its body may compute `price - off` and return a `Cents`. The verifier reads `fits` as `off <= price`.
- **In `ensures`:** `shipping` promises `ships_free(total) implies result == 0`.
- **In a `where` clause:** `FreeTotal` is the `Cents` that ship free. `thank_you` takes one, so it is never called for an order that pays for shipping.
- **In code:** `shipping` and `slip_note` call predicates in an `if`, like ordinary functions.
- **In another predicate:** `gift_ready` calls `ships_free`.

`una run .` prints:

```text include="steps/14-predicates/expected/output.txt"
after a coupon: 1490
shipping 495, then 0
gift wrap, standard
6200 cents, shipped free
```

`thank_you(6200)` proves that 6200 is a `Cents` and that `ships_free(6200)` holds, which the verifier computes from the body of `ships_free`.

### Opaque predicates

#### Rules the solver cannot read

Some rules cannot be written in the refinement language: "13 digits" needs a test on each character of a text, which the solver does not decide. A predicate can also be `opaque`: the verifier sees only its name. Its body may be any pure expression that cannot fail, such as a call of `is_digits`, and it runs when the program runs.

#### How a value gets an opaque fact

Since the verifier cannot read the body, it can never prove an opaque predicate. In code, a value gets its fact from `checked` at run time, or from the `ensures` of a capability operation ([chapter 8, Capabilities](/learn/capabilities/)). [Chapter 6](/learn/failure/#s6-4) uses one for the format of a SKU. Here, a barcode scanned at the till:

```una include="steps/15-opaque/src/barcodes.una" title="steps/15-opaque/src/barcodes.una" verified="check, run"
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

```toml include="steps/15-opaque/una.toml" title="steps/15-opaque/una.toml"
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

```text include="steps/15-opaque/expected/output.txt"
4006381333931: 1990 cents
not a barcode: 12-34
```

`checked(raw.trim, is_barcode(it)) else fail NotABarcode` runs the predicate's body on the trimmed text. When it holds, the value becomes a `Barcode`; when it does not, the function fails with `NotABarcode`. Every `checked` counts against the module's escape budget in `una.toml`, here 1, and appears in the build report: a reviewer sees each place where a run, not a proof, decides.

#### Calling an opaque predicate elsewhere

An opaque predicate may be called only inside `checked`, in the body of another opaque predicate, and named in a `where` clause or a capability operation's clause. Call it in an `if`, and una refuses:

```diff include="steps/15-opaque..steps/16-opaque-call:src/barcodes.una" context="1" title="src/barcodes.una"
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

```text include="steps/16-opaque-call/expected/rendered.txt"
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

### The refinement language

The condition of a refinement, and every `requires` and `ensures` clause, is written in the **refinement language**, the part of Una the solver decides: integer, boolean and text literals, parameters, `result`, `it`, fields, `.len`, `+`, `-` and unary `-`, `*` when one side is a literal, `/` and `mod` by a literal that is not zero, comparisons, `in`, `is`, `and`, `or`, `not`, `implies`, and calls of predicates. Anything else in a clause, such as the product of two parameters, is U2014 ([a contract outside the refinement language](#a-contract-outside-the-refinement-language-u2014)).

Some things look allowed and are not: ordering two texts with `<`, comparing with a variant by `==` (write `is`), and calls of ordinary functions. A clause that needs one of these needs a different statement of the rule, or an opaque predicate.

### A precondition, a refined kind or a runtime check

Three tools state a rule about a value. Choose by where the rule belongs and who can decide it:

:::decide
**Which to use:**

| The rule… | Use |
| --- | --- |
| Holds of every value of a type, wherever it goes, such as "a price is never negative" | a refined kind |
| Is about one function's arguments together, such as "the coupon is no larger than the price" | `requires` |
| Relates the result to the arguments | `ensures` |
| Has a name in the business, and appears in several clauses | a `reflect` predicate, used in them |
| Can only be decided by running code, such as the format of a barcode | an `opaque` predicate and `checked`, once, where the value enters |
| Concerns data from outside the program | a check where it enters, which gives it a refined kind ([section 7.5](#s7-5)) |
:::

A refined kind is usually the strongest choice: one declaration, checked at every way in, and a fact at every use. A precondition fits rules that tie several parameters together, which no single type can carry.

### Check yourself: refined kinds and predicates

`staff_pays` takes a `StaffDiscount`, a `Percent` of at most 50, and promises a result of at least 50:

```una include="steps/11-refined-forms/src/catalog.una#StaffDiscount" title="steps/11-refined-forms/src/catalog.una"
--- A staff discount: a `Percent` of at most 50. It holds both conditions.
kind StaffDiscount = Percent where it <= 50
```

What does `staff_pays(30)` return? Which of these calls check: `staff_pays(0)`, `staff_pays(50)`, `staff_pays(60)`?

:::answer Show the answer
```text include="steps/11-refined-forms/expected/output.txt#L1"
staff pay 70% and 50%
```

`staff_pays(30)` is 70. `staff_pays(0)` and `staff_pays(50)` check: both values are in `0..100` and at most 50. `staff_pays(60)` does not: 60 is a `Percent`, but not a `StaffDiscount`, and the refinement is refuted at the call.
:::

A bulk line is a `Line` of at least 10 units. What does `free_units(Line(sku: "RUG-07", quantity: 24))` return, and what would happen with a quantity of 9?

:::answer Show the answer
```text include="steps/11-refined-forms/expected/output.txt#L5"
free units: 2
```

24 units give two free units: 24 / 10 rounds down to 2. With 9 units the call does not check: `free_units` takes a `BulkLine`, and the verifier refutes the condition of `BulkLine` where the line enters the kind. The program never runs with a bulk line of 9 units.
:::

## 7.4 What the verifier proves

### Obligations and `una obligations`

Every contract, refinement and division becomes one or more **obligations**: a question for the solver, with an answer. `una obligations .` lists them all, each with its status, its identity, its kind, where it is, and its goal. For the cart of [section 7.3](#s7-3), where the first line is `shipping`'s result entering `Cents`, its declared type:

```text include="steps/12-refined/expected/commands/obligations.txt"
$ una obligations .
proven   ob-91854e18e0ff refinement    src/cart.una:19:1 result >= 0
proven   ob-993bde8df1da postcondition src/cart.una:20:11 ships_free(total) implies result == 0
proven   ob-7cd127341d91 refinement    src/cart.una:22:17 total >= 0
proven   ob-4fcc7418858d refinement    src/cart.una:28:37 line.unit_cents >= 0
proven   ob-2a5905c8f53d refinement    src/cart.una:28:64 (line.quantity + 1) in 1..99
proven   ob-7397ad5ab9ad refinement    src/cart.una:35:47 1990 >= 0
proven   ob-827f34a7ed20 refinement    src/cart.una:35:63 2 in 1..99
proven   ob-0ebf927b2507 refinement    src/cart.una:38:38 3980 >= 0
proven   ob-cb89b59f2358 refinement    src/cart.una:38:61 5970 >= 0
```

### The kinds of obligations

The kinds you meet most:

| Kind | Where | The goal |
| --- | --- | --- |
| `precondition` | Every call of a function with `requires` | The callee's `requires`, for the arguments given |
| `postcondition` | Every path that returns | The function's `ensures` |
| `refinement` | Every place a value enters a refined kind | The kind's condition, for that value |
| `division` | Every `/` and `mod` by a value that is not a literal | The divisor is not zero |
| `exhaustive` | A `when` with literal or range arms and no `else` | Some arm matches |
| `overflow` | Arithmetic on a fixed-width integer, such as `U8` | The exact result fits the type |

### Statuses and identities

Each obligation has one of three statuses:

- **proven:** the goal holds for every input.
- **refuted:** U5001, with a counterexample.
- **unknown:** U5002, with the reason. This is an error too.

The identity, such as `ob-2a5905c8f53d`, comes from the module, the function, the kind and the goal, so a reviewer can follow an obligation across commits. The same goal twice in one function shares one identity.

### When the solver cannot decide: U5002

The solver decides linear arithmetic: sums, differences, products where one side is a literal, and quotients and remainders by a literal that is not zero. A product of two values that are not literals, such as a unit price times a quantity, is beyond it: the solver treats it as an unknown number. When the solver then finds values that break a rule, una checks them with real multiplication. If they agree, the rule really breaks, and you get U5001 with those values as a counterexample. If every case the solver found needs a product that real arithmetic does not give, you get U5002. Here the solver cannot prove that the price of a line is not negative, even though it obviously is:

```diff include="steps/17-products..steps/18-unknown:src/invoice.una" context="1" title="src/invoice.una"
--- a/src/invoice.una
+++ b/src/invoice.una
@@ -18,8 +18,4 @@
 
---- What one line costs. The guard handles a case that cannot happen, since both factors
---- are at least 0; the solver cannot see that for itself.
-line_total(line: Line) -> Cents
-=
-  let total = line.unit_cents * line.quantity
-  if total < 0 then 0 else total
+--- What one line costs.
+line_total(line: Line) -> Cents = line.unit_cents * line.quantity
 
```

```text include="steps/18-unknown/expected/rendered.txt#L1"
[U5002] Error: refinement `result >= 0` could not be proven (the refutation depends on a product, quotient or remainder of two values, which the encoding of `spec/12 §2` leaves uninterpreted)
```

The message names the section of the specification that defines what the solver decides (see [Reference](#reference)).

### Proving a product with a guard

U5002 is not a claim that the code is wrong: it says that the proof is missing, and una does not pass a program with a missing proof. The first help line proposes a guard:

:::steps
```una include="steps/17-products/src/invoice.una" title="steps/17-products/src/invoice.una" verified="check, run"
module invoice

--- An amount of money in cents. It is never negative.
kind Cents = Int where it >= 0

--- One line of an invoice.
kind Line
  sku: Text
  unit_cents: Cents
  quantity: Int in 1..99

--- Loyalty points: one for each whole 1.00 spent.
points(total: Cents) -> Int
  ensures result >= 0
  ensures result * 100 <= total
=
  total / 100

--- What one line costs. The guard handles a case that cannot happen, since both factors
--- are at least 0; the solver cannot see that for itself.
line_total(line: Line) -> Cents
=
  let total = line.unit_cents * line.quantity
  if total < 0 then 0 else total

pub main() -> Unit
  uses @console: Console[print]
=
  let desk = Line(sku: "DESK-02", unit_cents: 14900, quantity: 2)
  let total = line_total(desk)
  @console.print("{total} cents, {points(total)} points")
```

1. **`points`.** Division by the literal 100 is linear, so the verifier proves both clauses with no help. `result * 100` is allowed in a clause: one side is a literal.
2. **`let total = line.unit_cents * line.quantity`, then `if total < 0 then 0 else total`.** In the `else` branch, the verifier knows `total >= 0`, so the result is a `Cents`. The `then` branch never runs, since both factors are at least 0. The verifier does not check that claim: it accepts the guard whatever the branch returns. You check it, from the kinds of the factors, and if a kind changes, you read the guard again. The guard costs one comparison at run time.
:::

`una run .` prints:

```text include="steps/17-products/expected/output.txt"
29800 cents, 298 points
```

### Other sources of U5002

U5002 also comes from a proof that runs out of the step budget in `verification.lock`; the reason says which. A loop gives U5002 too: it keeps, from one turn to the next, only the refinements of the bindings it updates. `let edit total: Cents = 0` keeps `total >= 0`, which is all the day-to-day program needs. For any other fact the reason says what to do: state what one iteration does as the `ensures` of a helper with an `edit` parameter ([chapter 12, Memory and concurrency](/learn/memory-and-concurrency/)).

> [!TIP]
> Prefer a guard to `checked` when you can show from the kinds that the guard never fires. A guard needs no error variant and no budget, and the verifier proves the code around it. Use `checked` when you cannot show it, or for a rule that only a test at run time can decide: it fails at run time instead of answering quietly.

## 7.5 Contracts at the boundary

### Where code meets code

Contracts are checked where code meets code. At each call, the caller proves the callee's `requires` and gets its `ensures` in return. A refined kind is a boundary too: the value is checked once, where it enters the kind, and every function after that may rely on it.

### Checking outside data once

That leaves data from outside the program: text typed by a person, a line of a file, a field of a request. No proof can say what a person will type. Check it once, where it enters, and give it a refined kind there:

:::steps
```una include="steps/19-boundary/src/rates.una" title="steps/19-boundary/src/rates.una" verified="check, run"
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
2. **`if n < 0 or n > 100` then `fail`, `else n`.** In the `else` branch, the verifier knows `0 <= n <= 100`, so it proves the result a `Percent`.
3. **`rest_of(rate: Percent) -> Percent = 100 - rate`.** Inside the program, nothing checks again: `100 - rate` is in range because `rate` is.
4. **`attempt parse_rate(raw)`.** In the `Ok(rate)` arm, `rate` is a `Percent`, with its fact, as after a direct call. `attempt` keeps what a callee promises ([chapter 6](/learn/failure/#s6-3)).
:::

`una run .` prints:

```text include="steps/19-boundary/expected/output.txt"
15% off: the customer pays 85%
150 is not between 0 and 100
'ten' is not a number
```

> [!SECURITY]
> A refined kind turns "every function must remember to check the rate" into "one function checks it, and the checker refuses every other way in". A new function that takes a `Percent` cannot receive 150, whoever calls it.

### Rules from outside the code: `requirement`

Some rules come from outside the code too: a billing policy, a regulation, a promise to customers. A `requirement` records such a rule with its source and owner, and `derived from` ties a function's contract to it. `una trace` lists the functions derived from a requirement, with their proofs, and `una report .` lists a package's requirements.

## 7.6 Day-to-day: billing

### What the billing step must do

Now the program from the start of the chapter. The store's billing step receives the lines of an invoice and a coupon. It must never charge a negative amount, never take off more than the invoice is worth, pay from store credit first, and never refund more than the customer paid. Each of these rules becomes a contract or a kind, and the verifier proves them all.

### The rules and the kinds

Two requirements name the store's rules. The kinds carry the facts that hold of every value: money is never negative, a rate is between 0 and 100, a line orders 1 to 99 units.

```una include="day-to-day/src/billing.una#BILLING_1..RefundError" title="day-to-day/src/billing.una" caption="the rules and the kinds"
requirement BILLING_1
  text "A coupon or store credit never makes a customer pay less than 0 or more than the subtotal"
  source policy "Store billing rules"
  owner billing
  status active

requirement BILLING_2
  text "A refund never pays back more than the customer paid"
  source policy "Store billing rules"
  owner billing
  status active

--- An amount of money in cents. It is never negative.
pub kind Cents = Int where it >= 0

--- A share in whole percent.
pub kind Percent = Int in 0..100

--- One line of an invoice.
pub kind Line
  sku: Text
  unit_cents: Cents
  quantity: Int in 1..99

--- A coupon on the whole invoice.
pub kind Coupon = NoCoupon | PercentOff(rate: Percent) | CentsOff(amount: Cents)

--- How an invoice is paid: from store credit first, and the rest by card.
pub kind Payment
  credit: Cents
  card: Cents

--- Why a refund was refused.
pub kind RefundError = | MoreThanPaid(paid: Cents)
```

A `requirement` holds the text of a rule as its source wrote it, the source, the team that owns it, and whether it is `active` or only `proposed`. `Coupon` is a sum kind whose variants carry refined fields, so a `PercentOff(rate: 110)` does not check.

### Pricing the lines

`line_total` multiplies, with the guard from [section 7.4](#s7-4). `subtotal` sums with a loop. `total` is declared `Cents`, so every assignment to it proves the sum not negative, which holds since both sides are `Cents`.

```una include="day-to-day/src/billing.una#line_total..subtotal" title="day-to-day/src/billing.una"
--- What one line costs. The guard handles a case that cannot happen, since both factors
--- are at least 0; the solver cannot see that for itself.
pub line_total(line: Line) -> Cents
=
  let total = line.unit_cents * line.quantity
  if total < 0 then 0 else total

--- The sum of every line.
pub subtotal(lines: List[Line]) -> Cents
=
  let edit total: Cents = 0
  for line in lines
    total = total + line_total(line)
  total
```

### The coupon

`discount` promises that it never takes off more than the amount. Each arm keeps the promise: no coupon takes 0, a percentage takes part of the amount, and a coupon worth more than the amount takes all of it and no more. `percent_of` multiplies two values, so it has the guard too, and its own `ensures` gives `discount` the fact it needs about that arm.

```una include="day-to-day/src/billing.una#percent_of..discount" title="day-to-day/src/billing.una"
--- `rate` percent of `amount`, rounded down. The guard cannot fire: both factors are at least 0, and `rate` is at most 100.
percent_of(amount: Cents, rate: Percent) -> Cents
  ensures result <= amount
=
  let part = amount * rate / 100
  if part < 0 or part > amount then 0 else part

--- What a coupon takes off `amount`: never more than `amount`.
pub discount(amount: Cents, coupon: Coupon) -> Cents
  ensures result <= amount
  derived from BILLING_1
=
  when coupon
    is NoCoupon -> 0
    is PercentOff(rate) -> percent_of(amount, rate)
    is CentsOff(off) -> if off > amount then amount else off
```

### Paying

`pay` splits a total between store credit and card. Its two clauses are the whole rule: the two parts add up to the total, and the credit used is never more than the customer has. The verifier proves both on both branches, and also that `total - credit` is a `Cents` where `credit < total`.

```una include="day-to-day/src/billing.una#pay" title="day-to-day/src/billing.una"
--- Splits `total` between store credit and card, credit first.
pub pay(total: Cents, credit: Cents) -> Payment
  ensures result.credit + result.card == total
  ensures result.credit <= credit
  derived from BILLING_1
=
  if credit >= total then Payment(credit: total, card: 0) else Payment(credit: credit, card: total - credit)
```

### Refunding

`refund` fails rather than break its promise. Its `ensures` covers the path that returns, and the path that fails returns nothing. The failure carries what was paid, so a message can say how much a refund may be.

The contracts leave some things open on purpose. `refund` does not say that it pays back exactly what was asked, and `discount` does not say how a percentage is rounded. Those are choices of the business, not rules of safety, and the examples in [section 7.7](#s7-7) pin them down. A contract states what must never break; an example states what the answer is for one case.

```una include="day-to-day/src/billing.una#refund" title="day-to-day/src/billing.una"
--- What a refund pays back: what was asked, if the customer paid at least that much.
pub refund(paid: Cents, asked: Cents) -> Cents
  ensures result <= paid
  fails RefundError
  derived from BILLING_2
=
  if asked > paid then fail MoreThanPaid(paid) else asked
```

### Running it

`main` prices two lines, applies a 10% coupon, and pays with 50.00 of store credit. Look at `let total: Cents = gross - off`. Subtracting two `Cents` can give a negative number, so the verifier must prove `gross - off >= 0`. It can, but only because `discount` promises `off <= gross`. Remove that `ensures` and this line no longer checks ([a caller that needs a promise the callee does not make](#a-caller-that-needs-a-promise-the-callee-does-not-make-u5001) shows it). Contracts compose this way: each function's promise is the next function's fact.

```una include="day-to-day/src/billing.una#money..main" title="day-to-day/src/billing.una"
--- An amount for a person to read, such as 19.90.
pub money(cents: Cents) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"

--- One line of the refund report.
pub refund_line(paid: Cents, asked: Cents) -> Text
=
  let outcome = attempt refund(paid, asked: asked)
  when outcome
    is Ok(back) -> "refund {money(back)}: paid back"
    is Err(failure) -> "refund {money(asked)}: refused, {why(failure)}"

why(failure: RefundError) -> Text
=
  when failure
    is MoreThanPaid(paid) -> "only {money(paid)} was paid"

pub main() -> Unit
  uses @console: Console[print]
=
  let lines = [Line(sku: "LAMP-01", unit_cents: 1990, quantity: 2), Line(sku: "DESK-02", unit_cents: 14900, quantity: 1)]
  for line in lines
    @console.print("{line.quantity} x {line.sku} at {money(line.unit_cents)}: {money(line_total(line))}")
  let gross = subtotal(lines)
  let off = discount(gross, coupon: PercentOff(rate: 10))
  let total: Cents = gross - off
  let payment = pay(total, credit: 5000)
  @console.print("subtotal {money(gross)}, coupon -{money(off)}, total {money(total)}")
  @console.print("store credit {money(payment.credit)}, card {money(payment.card)}")
  @console.print(refund_line(total, asked: 3980))
  @console.print(refund_line(total, asked: 20000))
```

`una run .` prints the invoice shown in [What you'll build](#what-youll-build). The second refund asks for 200.00 of an invoice of 169.92, so `refund` fails. `refund_line` keeps the outcome with `attempt`, and `why` turns the failure into words, so the report shows every refund, paid or refused. `money` divides and takes the remainder by the literal 100, so it has no division obligation at all.

### Tracing a rule to its proof

`una trace BILLING_2` lists the function derived from the refund rule, its contract, and the proof of each obligation:

```text include="day-to-day/expected/commands/trace.txt"
$ una trace BILLING_2
requirement BILLING_2 (active)
  text "A refund never pays back more than the customer paid"
  source policy "Store billing rules"
  owner billing
billing.refund
  ensures result <= paid
  proven   ob-204eda00affc refinement    result >= 0
  proven   ob-ef9bbe64fc88 postcondition result <= paid
  proven   ob-258d17d765c8 refinement    paid >= 0
```

A reviewer who owns the refund policy can read this instead of the code: the rule, the function that implements it, the promise in its header, and the proof.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/billing.una" title="day-to-day/src/billing.una" caption="the whole program" verified="check, run, test"
module billing

requirement BILLING_1
  text "A coupon or store credit never makes a customer pay less than 0 or more than the subtotal"
  source policy "Store billing rules"
  owner billing
  status active

requirement BILLING_2
  text "A refund never pays back more than the customer paid"
  source policy "Store billing rules"
  owner billing
  status active

--- An amount of money in cents. It is never negative.
pub kind Cents = Int where it >= 0

--- A share in whole percent.
pub kind Percent = Int in 0..100

--- One line of an invoice.
pub kind Line
  sku: Text
  unit_cents: Cents
  quantity: Int in 1..99

--- A coupon on the whole invoice.
pub kind Coupon = NoCoupon | PercentOff(rate: Percent) | CentsOff(amount: Cents)

--- How an invoice is paid: from store credit first, and the rest by card.
pub kind Payment
  credit: Cents
  card: Cents

--- Why a refund was refused.
pub kind RefundError = | MoreThanPaid(paid: Cents)

--- What one line costs. The guard handles a case that cannot happen, since both factors
--- are at least 0; the solver cannot see that for itself.
pub line_total(line: Line) -> Cents
=
  let total = line.unit_cents * line.quantity
  if total < 0 then 0 else total

--- The sum of every line.
pub subtotal(lines: List[Line]) -> Cents
=
  let edit total: Cents = 0
  for line in lines
    total = total + line_total(line)
  total

--- `rate` percent of `amount`, rounded down. The guard cannot fire: both factors are at least 0, and `rate` is at most 100.
percent_of(amount: Cents, rate: Percent) -> Cents
  ensures result <= amount
=
  let part = amount * rate / 100
  if part < 0 or part > amount then 0 else part

--- What a coupon takes off `amount`: never more than `amount`.
pub discount(amount: Cents, coupon: Coupon) -> Cents
  ensures result <= amount
  derived from BILLING_1
=
  when coupon
    is NoCoupon -> 0
    is PercentOff(rate) -> percent_of(amount, rate)
    is CentsOff(off) -> if off > amount then amount else off

--- Splits `total` between store credit and card, credit first.
pub pay(total: Cents, credit: Cents) -> Payment
  ensures result.credit + result.card == total
  ensures result.credit <= credit
  derived from BILLING_1
=
  if credit >= total then Payment(credit: total, card: 0) else Payment(credit: credit, card: total - credit)

--- What a refund pays back: what was asked, if the customer paid at least that much.
pub refund(paid: Cents, asked: Cents) -> Cents
  ensures result <= paid
  fails RefundError
  derived from BILLING_2
=
  if asked > paid then fail MoreThanPaid(paid) else asked

--- An amount for a person to read, such as 19.90.
pub money(cents: Cents) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"

--- One line of the refund report.
pub refund_line(paid: Cents, asked: Cents) -> Text
=
  let outcome = attempt refund(paid, asked: asked)
  when outcome
    is Ok(back) -> "refund {money(back)}: paid back"
    is Err(failure) -> "refund {money(asked)}: refused, {why(failure)}"

why(failure: RefundError) -> Text
=
  when failure
    is MoreThanPaid(paid) -> "only {money(paid)} was paid"

pub main() -> Unit
  uses @console: Console[print]
=
  let lines = [Line(sku: "LAMP-01", unit_cents: 1990, quantity: 2), Line(sku: "DESK-02", unit_cents: 14900, quantity: 1)]
  for line in lines
    @console.print("{line.quantity} x {line.sku} at {money(line.unit_cents)}: {money(line_total(line))}")
  let gross = subtotal(lines)
  let off = discount(gross, coupon: PercentOff(rate: 10))
  let total: Cents = gross - off
  let payment = pay(total, credit: 5000)
  @console.print("subtotal {money(gross)}, coupon -{money(off)}, total {money(total)}")
  @console.print("store credit {money(payment.credit)}, card {money(payment.card)}")
  @console.print(refund_line(total, asked: 3980))
  @console.print(refund_line(total, asked: 20000))

example "a coupon worth more than the invoice takes the whole invoice"
  do discount(1000, coupon: CentsOff(amount: 1500))
  expect result == 1000

example "ten percent is rounded down"
  do discount(18885, coupon: PercentOff(rate: 10))
  expect result == 1888

example "store credit pays first"
  do pay(16992, credit: 5000)
  expect result.credit == 5000
  expect result.card == 11992

example "credit larger than the total leaves nothing for the card"
  do pay(1990, credit: 5000)
  expect result.card == 0

example "a refund of more than was paid is refused"
  do refund(16992, asked: 20000)
  expect fails MoreThanPaid

example "an empty invoice costs nothing"
  do subtotal([])
  expect result == 0
```

## 7.7 Testing it

### What the examples pin down

A proof covers every input, so why write examples? Because a contract states only what you wrote in it. `discount` promises `result <= amount`, and a body that always returns 0 keeps that promise too. The examples pin down the values the business expects: 10% of 188.85 is 18.88, rounded down; credit pays before the card; a refund of more than was paid is refused.

```una include="day-to-day/src/billing.una#L120-L143" title="day-to-day/src/billing.una" caption="the examples"
example "a coupon worth more than the invoice takes the whole invoice"
  do discount(1000, coupon: CentsOff(amount: 1500))
  expect result == 1000

example "ten percent is rounded down"
  do discount(18885, coupon: PercentOff(rate: 10))
  expect result == 1888

example "store credit pays first"
  do pay(16992, credit: 5000)
  expect result.credit == 5000
  expect result.card == 11992

example "credit larger than the total leaves nothing for the card"
  do pay(1990, credit: 5000)
  expect result.card == 0

example "a refund of more than was paid is refused"
  do refund(16992, asked: 20000)
  expect fails MoreThanPaid

example "an empty invoice costs nothing"
  do subtotal([])
  expect result == 0
```

### Examples are checked like code

Each example calls one function with `do` and checks the result with `expect`, or the failure with `expect fails` ([chapter 6](/learn/failure/#s6-6) explains each line). The examples are verified like the rest of the code: a `do` line that calls `pay` with `credit: -5`, or `discount` with a rate of 110, does not check, since the argument does not fit its kind.

### Examples and proofs together

Two habits make examples and proofs work together:

- **Turn each counterexample into an example**, as in [section 7.2](#s7-2). The case that broke the code once is the case a later change is most likely to break again.
- **Test the exact values; prove the bounds.** A contract states a range or a relation that holds for every input. An example states one exact answer that a person can check by hand.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L9"
example billing "a coupon worth more than the invoice takes the whole invoice" ... ok
example billing "ten percent is rounded down" ... ok
example billing "store credit pays first" ... ok
example billing "credit larger than the total leaves nothing for the card" ... ok
example billing "a refund of more than was paid is refused" ... ok
example billing "an empty invoice costs nothing" ... ok

6 examples: 6 passed, 0 failed
```

## 7.8 Common mistakes

Each mistake below is a small change to `day-to-day/src/billing.una`, followed by what `una check .` reports.

### A coupon that can be worth more than the order (U5001)

:::mistake
In `discount`, return the coupon's value without the cap:

```diff include="day-to-day..mistakes/1:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -67,3 +67,3 @@
     is PercentOff(rate) -> percent_of(amount, rate)
-    is CentsOff(off) -> if off > amount then amount else off
+    is CentsOff(off) -> off
 
```

```text include="mistakes/1/expected/rendered.txt"
[U5001] Error: postcondition of `discount` is refuted
    ╭─[ src/billing.una:68:25 ]
    │
 62 │   ensures result <= amount
    │           ────────┬───────
    │                   ╰───────── ensures clause
    │
 68 │     is CentsOff(off) -> off
    │                         ─┬─
    │                          ╰─── postcondition of `discount` is refuted
    │
    │ Help 1: repair 1: add a guard or an arm so that the failing path returns a value for which `result <= amount` holds
    │
    │ Help 2: repair 2: adjust the `ensures` clause
    │
    │ Note 1: obligation ob-e0a2abc0bb6a (postcondition) is refuted: result <= amount
    │
    │ Note 2: counterexample: amount = 0, coupon = CentsOff, coupon.amount = 1, coupon.rate = 101, result = 1
    │
    │ Note 3: run `una explain U5001` for an explanation
────╯
```

*Why:* with `amount = 0` and a `CentsOff` coupon of 1 cent, the result is 1, which breaks `result <= amount`. In a counterexample for a sum kind, `coupon = CentsOff` names the variant, and only that variant's fields mean anything: `coupon.rate` belongs to `PercentOff`, and its value here is noise.

*Fix:* cap the coupon at the amount, as the day-to-day program does.
:::

### A caller that needs a promise the callee does not make (U5001)

:::mistake
Remove `ensures result <= amount` from `discount`:

```diff include="day-to-day..mistakes/2:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -61,3 +61,2 @@
 pub discount(amount: Cents, coupon: Coupon) -> Cents
-  ensures result <= amount
   derived from BILLING_1
```

```text include="mistakes/2/expected/rendered.txt#L1,L18"
[U5001] Error: refinement `(gross - off) >= 0` is refuted
     │ Note 2: counterexample: gross = 0, lines = List#0, lines.len = 2, off = 1, total = -1
```

*Why:* the error is in `main`, not in `discount`. A caller knows a function only by its header, so without the clause `main` cannot prove that `gross - off` is not negative. The counterexample is not a run: `discount(0, …)` never returns 1, but its header now allows it. `List#0` names some list the solver chose, and `total = -1` is the value that breaks the rule; only `gross` and `off` matter.

*Fix:* put the clause back. When a caller needs a fact about a result, the callee's `ensures` is where it goes.
:::

### A comparison the wrong way round (U5001)

:::mistake
In `refund`, swap `asked` and `paid` in the test:

```diff include="day-to-day..mistakes/3:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -83,3 +83,3 @@
 =
-  if asked > paid then fail MoreThanPaid(paid) else asked
+  if paid > asked then fail MoreThanPaid(paid) else asked
 
```

```text include="mistakes/3/expected/rendered.txt#L1,L18"
[U5001] Error: postcondition of `refund` is refuted
    │ Note 2: counterexample: asked = 1, paid = 0, result = 1
```

*Why:* with `paid = 0` and `asked = 1`, the refund pays 1 cent of an invoice that cost nothing. The `ensures` catches a swap a quick review misses.

*Fix:* `if asked > paid then fail MoreThanPaid(paid) else asked`.
:::

### A product without a guard (U5002)

:::mistake
Write `line_total` as one expression:

```diff include="day-to-day..mistakes/4:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -39,6 +39,3 @@
 --- are at least 0; the solver cannot see that for itself.
-pub line_total(line: Line) -> Cents
-=
-  let total = line.unit_cents * line.quantity
-  if total < 0 then 0 else total
+pub line_total(line: Line) -> Cents = line.unit_cents * line.quantity
 
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U5002] Error: refinement `result >= 0` could not be proven (the refutation depends on a product, quotient or remainder of two values, which the encoding of `spec/12 §2` leaves uninterpreted)
```

*Why:* the solver treats the product of two values as an unknown number, so it cannot prove the result is not negative. The values it found do not agree with real multiplication, so there is no counterexample, and the message gives that reason.

*Fix:* bind the product, then guard it, as in [section 7.4](#s7-4).
:::

### A contract outside the refinement language (U2014)

:::mistake
Promise the exact product in `line_total`:

```diff include="day-to-day..mistakes/5:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -40,2 +40,3 @@
 pub line_total(line: Line) -> Cents
+  ensures result == line.unit_cents * line.quantity
 =
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U2014] Error: `*` of two operands that are not literals is outside the refinement language
```

*Why:* a clause is a question for the solver, written in the language it decides, which multiplies only by a literal.

*Fix:* state what the solver can decide, such as `result >= line.unit_cents`, or leave the exact value to an example.
:::

### A rate above 100 percent (U5001)

:::mistake
Give the coupon a rate of 110:

```diff include="day-to-day..mistakes/6:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -111,3 +111,3 @@
   let gross = subtotal(lines)
-  let off = discount(gross, coupon: PercentOff(rate: 10))
+  let off = discount(gross, coupon: PercentOff(rate: 110))
   let total: Cents = gross - off
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U5001] Error: refinement `110 in 0..100` is refuted
```

*Why:* `rate` is a `Percent`, and 110 is not in `0..100`. The goal names no variable, so there is no counterexample: the literal itself is the case.

*Fix:* a rate from 0 to 100. A rate typed by a person goes through a function such as `parse_rate` ([section 7.5](#s7-5)).
:::

## 7.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples, and a stub when there is one. `una check .` or `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

### Exercise 1: free shipping

::::exercise
Shipping costs 4.95, and nothing from 50.00. The start package has `shipping` with its contract and a body that always charges 4.95. `una check .` refutes it:

```una include="exercises/1/start/src/billing.una#shipping" title="exercises/1/start/src/billing.una"
--- What shipping costs for an invoice of `total` cents: 4.95, and nothing from 50.00.
--- Exercise 1: make the body keep the contract.
pub shipping(total: Cents) -> Cents
  ensures result <= 495
  ensures total >= 5000 implies result == 0
=
  495
```

```text include="exercises/1/start/expected/rendered.txt#L1,L18"
[U5001] Error: postcondition of `shipping` is refuted
    │ Note 2: counterexample: result = 495, total = 5000
```

:::hint
*Hint:* read the counterexample as a test case: here the body has no calls, so it is one. For an invoice of exactly 50.00, the body charges 4.95. The body needs a branch for that case, and a branch on `total > 5000` is refuted with the same counterexample.
:::

Check your answer with `una check .`, then `una test .`, which runs these examples:

```una include="exercises/1/start/src/billing.una#L153-L159" title="exercises/1/start/src/billing.una"
example "an invoice from 50.00 ships free"
  do shipping(5000)
  expect result == 0

example "a smaller invoice pays 4.95"
  do shipping(4999)
  expect result == 495
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Give the body a branch:

```diff include="exercises/1/start..exercises/1/answer:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -86,3 +86,2 @@
 --- What shipping costs for an invoice of `total` cents: 4.95, and nothing from 50.00.
---- Exercise 1: make the body keep the contract.
 pub shipping(total: Cents) -> Cents
@@ -91,3 +90,3 @@
 =
-  495
+  if total >= 5000 then 0 else 495
 
```
:::
::::

### Exercise 2: a fixed price

::::exercise
A coupon can set the price of a whole invoice, such as "everything for 150.00". Add a variant `FixedPrice(cents: Cents)` to `Coupon`, and an arm for it in `discount`: it takes off the difference when the invoice costs more than the fixed price, and nothing otherwise. The start package ends with these examples, and `una check .` reports U1001 until the variant exists:

```una include="exercises/2/start/src/billing.una#L145-L151" title="exercises/2/start/src/billing.una"
example "a fixed price below the subtotal takes off the difference"
  do discount(18880, coupon: FixedPrice(cents: 15000))
  expect result == 3880

example "a fixed price above the subtotal takes off nothing"
  do discount(1000, coupon: FixedPrice(cents: 1500))
  expect result == 0
```

:::hint
*Hint:* add the variant, then the arm. The verifier checks the arm against the header of `discount`.
:::

The first arm most people write is `amount - cents`. `una check .` refutes it:

```text include="exercises/2/unguarded/expected/rendered.txt#L1,L8,L18"
[U5001] Error: refinement `result >= 0` is refuted
 69 │     is FixedPrice(cents) -> amount - cents
    │ Note 2: counterexample: amount = 0, coupon = FixedPrice, coupon.amount = -1, coupon.cents = 3, coupon.rate = 101, result = -3
```

The counterexample is a fixed price of 0.03 on an invoice of 0: the discount would be −3 cents. Only `coupon.cents` matters here, as in [a coupon that can be worth more than the order](#a-coupon-that-can-be-worth-more-than-the-order-u5001): `coupon.amount = -1` is outside `Cents` because that field belongs to no value here.

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Add the variant, and an arm with a guard:

```diff include="exercises/2/start..exercises/2/answer:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -27,3 +27,3 @@
 --- A coupon on the whole invoice.
-pub kind Coupon = NoCoupon | PercentOff(rate: Percent) | CentsOff(amount: Cents)
+pub kind Coupon = NoCoupon | PercentOff(rate: Percent) | CentsOff(amount: Cents) | FixedPrice(cents: Cents)
 
@@ -68,2 +68,3 @@
     is CentsOff(off) -> if off > amount then amount else off
+    is FixedPrice(cents) -> if cents < amount then amount - cents else 0
 
```
:::
::::

### Exercise 3: a second refund

::::exercise
A customer can ask for a refund in parts. Write `refund_again(paid, already, asked)`, which refunds `asked` when the refunds together stay within what was paid, and fails with `MoreThanPaid` otherwise. The start package has the header, with its contract, and a body that forgets the refunds already made. `una check .` refutes it:

```una include="exercises/3/start/src/billing.una#refund_again" title="exercises/3/start/src/billing.una"
--- A further refund, after `already` was paid back: the refunds together never pay back more
--- than the customer paid. Exercise 3: refuse what would go above `paid`.
pub refund_again(paid: Cents, already: Cents, asked: Cents) -> Cents
  requires already <= paid
  ensures already + result <= paid
  fails RefundError
  derived from BILLING_2
=
  refund(paid, asked: asked)
    if error pass
```

```text include="exercises/3/start/expected/rendered.txt#L1,L18"
[U5001] Error: postcondition of `refund_again` is refuted
    │ Note 2: counterexample: already = 1, asked = 0, paid = 1, result = 1
```

`result = 1` with `asked = 0` is not what `refund` returns. It is what `refund`'s header allows: any amount up to `paid`. The body never limits the refund to what is left, so the verifier cannot prove the refunds together stay within `paid`.

:::hint
*Hint:* compare `already + asked` with `paid`, and fail with `MoreThanPaid(paid)` when it is more, so the message still names what the customer paid.
:::

Check your answer with `una test .`, which runs these examples:

```una include="exercises/3/start/src/billing.una#L156-L162" title="exercises/3/start/src/billing.una"
example "a second refund cannot pass what is left"
  do refund_again(16992, already: 10000, asked: 8000)
  expect fails MoreThanPaid

example "a second refund within what is left is paid back"
  do refund_again(16992, already: 10000, asked: 6992)
  expect result == 6992
```

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Refuse what would take the refunds above `paid`:

```diff include="exercises/3/start..exercises/3/answer:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -86,3 +86,3 @@
 --- A further refund, after `already` was paid back: the refunds together never pay back more
---- than the customer paid. Exercise 3: refuse what would go above `paid`.
+--- than the customer paid.
 pub refund_again(paid: Cents, already: Cents, asked: Cents) -> Cents
@@ -93,4 +93,3 @@
 =
-  refund(paid, asked: asked)
-    if error pass
+  if already + asked > paid then fail MoreThanPaid(paid) else asked
 
```

The function is `derived from BILLING_2`, so `una trace BILLING_2` now lists it next to `refund`, with its proofs:

```text include="exercises/3/answer/expected/commands/trace.txt#L11-L16"
billing.refund_again
  requires already <= paid
  ensures already + result <= paid
  proven   ob-f4387ed6cf13 refinement    result >= 0
  proven   ob-0b04b97219e5 postcondition already + result <= paid
  proven   ob-c249bb5b8dee refinement    paid >= 0
```
:::
::::

## 7.10 Recap and reference

### For agents

:::agents
`una --json check .` gives each obligation that is not proven as a diagnostic with its `obligation` (id, kind, goal, status) and its `counterexample` as name and value pairs. For [a coupon that can be worth more than the order](#a-coupon-that-can-be-worth-more-than-the-order-u5001):

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U5001","severity":"error","domain":"verification","message":"postcondition of `discount` is refuted","primary":{"file":"src/billing.una","start":{"line":68,"col":25},"end":{"line":68,"col":28}},"related":[{"file":"src/billing.una","start":{"line":62,"col":11},"end":{"line":62,"col":27},"message":"ensures clause"}],"obligation":{"id":"ob-e0a2abc0bb6a","kind":"postcondition","goal":"result <= amount","status":"refuted"},"counterexample":{"bindings":[{"name":"amount","value":0},{"name":"coupon","value":"CentsOff"},{"name":"coupon.amount","value":1},{"name":"coupon.rate","value":101},{"name":"result","value":1}]},"repairs":[{"rank":1,"escape_cost":0,"description":"add a guard or an arm so that the failing path returns a value for which `result <= amount` holds","edit":null},{"rank":2,"escape_cost":0,"description":"adjust the `ensures` clause","edit":null}],"explain":"una explain U5001"}],"fixable":0}
```

The repairs of U5001 and U5002 carry no `edit`, since only the author knows whether the code or the contract is wrong, so `una fix` leaves them. `una --json obligations .` and `una --json trace <ID>` list every obligation, proven or not. The compact rule: *every call proves the callee's `requires`, every return proves the `ensures`, every value that enters a refined kind proves its condition, and unknown is an error; clauses multiply and divide only by literals.*
:::

### Recap

:::recap
- `requires` states what a caller must prove; the body may assume it.
- `ensures` states what every return promises; callers know a function by its header alone.
- A counterexample shows where a contract breaks; calls in it follow their headers, not their bodies. Fix the code or the contract, and keep a real case as an example.
- Put a rule that holds of every value on its kind, `Int where it >= 0`, never on a type argument. Name a rule that several clauses share with a `reflect` predicate; a rule only a run can decide is an `opaque` predicate, established with `checked`.
- Clauses multiply and divide only by literals. A guard for a case the solver cannot rule out is yours to confirm from the kinds.
- U5001: refuted, with a counterexample; U5002: no proof and no real counterexample. Both are errors.
- Check data from outside once, where it enters, and give it a refined kind there.
- Record business rules as requirements, and read their proofs with `una trace`.
:::

### Reference

:::reference
- Construct pages: [`requires`](/docs/language/functions/requires/), [`ensures`](/docs/language/functions/ensures/), [`where` and refinements](/docs/language/types/where/), [`predicate`](/docs/language/types/predicate/), [`kind`](/docs/language/types/kind/), [`checked` and the escape budget](/docs/language/errors/checked/), [`requirement`](/docs/language/requirements/requirement/), [`example`](/docs/language/examples/example/), [verification](/docs/language/verification/)
- Prelude: [`Nat`, `Option`, `Result`, `to_int`](/docs/std/)
- Commands: [`una check`](/docs/cli/check/), [`una obligations`](/docs/cli/obligations/), [`una trace`](/docs/cli/trace/), [`una report`](/docs/cli/report/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U2002](/docs/errors/U2002/), [U2012](/docs/errors/U2012/) (`result` or `old` outside `ensures`), [U2014](/docs/errors/U2014/), [U2015](/docs/errors/U2015/) (a predicate body that is not allowed), [U2016](/docs/errors/U2016/), [U5001](/docs/errors/U5001/), [U5002](/docs/errors/U5002/), [U5003](/docs/errors/U5003/) (the solver is missing or not the pinned version)
- Specification: [functions and contracts](/docs/spec/04-functions-and-contracts/), [types](/docs/spec/03-types/), [verification](/docs/spec/12-verification/), [requirements and examples](/docs/spec/08-requirements-and-examples/), [errors](/docs/spec/06-errors/)
:::
