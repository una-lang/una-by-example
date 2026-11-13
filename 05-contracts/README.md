---
learn: "5"
title: Contracts and the verifier
editions: ["0.2"]
codes: [U1001, U1005, U1006, U1007, U2014, U5001, U5002]
time: 65
builds: The billing step of a store, which prices an invoice, applies a coupon, splits the payment and checks refunds
prerequisites: ["2", "3", "4"]
template: 2
nav: ["requires", "ensures and counterexamples", "Refined kinds and predicates", "What the verifier proves", "Requirements", "Day-to-day: billing", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 5 Contracts and the verifier

Billing code is where a small slip costs real money: a coupon that is worth more than the order, a refund that pays back more than was paid, a rate typed as 110 percent. Tests catch the cases someone thought of. In Una you write the rule itself into the function's header, as a contract, and the verifier proves before the program runs that the rule holds for every input. When it does not, the verifier shows you an input that breaks it. This chapter writes contracts for the billing step of a store, and shows how to read what the verifier says.

## What you'll build

:::build
The billing step of a small store. It prices the two lines of an invoice, applies a coupon, pays from store credit first and the rest by card, and checks two refunds against what was paid:

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
- trace a contract back to the business rule it comes from, with `requirement` and `una trace`.
:::

## Why it works this way

In most languages, the rules of a function live in comments, in checks that run with the code, and in tests. A comment can be wrong. A check that runs with the code stops the program in front of a customer. A test covers the inputs someone wrote down, and the bug is in another: a coupon worth more than a cheap order.

Una moves the rules into the header and proves them:

:::steps
1. **A contract is part of the header.** `requires` states what must hold of the arguments, and `ensures` what holds of the result. A reader learns what a function does from its header alone.
2. **The verifier proves every contract, for every input.** `una check` turns each rule into a question for the solver Z3, at the version `verification.lock` pins. A rule that fails for some input is refuted, and the diagnostic shows that input: a counterexample.
3. **Nothing unproven passes.** When the solver cannot decide a question, the result is an error too, never a silent pass. A program that checks holds no value that breaks its contracts, and its contracts cost nothing when it runs. The exceptions are visible in the code: a test that runs with the program, `checked` ([chapter 7](/learn/failure/#s7-5)), and the contracts of the standard library, which are trusted, not proven.
:::

The price: you state your rules in a small language the solver understands, and sometimes add a guard to give it a fact. In return, the checker finds the input that breaks a rule before a customer does.

> [!KEY]
> A contract is a rule the verifier proves for every input before the program runs. When it cannot prove the rule, it does not pass the program: it shows an input that breaks the rule, or says that it cannot decide.

## 5.1 Preconditions: `requires`

### What a contract is

When a store hires a courier, the two sign an agreement. The store promises to hand over parcels that are packed, labeled and under 30 kilograms. The courier promises to deliver each one within two days. Each side knows what it must do and what it may count on, and neither has to watch how the other works.

A function and the code that calls it have the same kind of agreement. As [chapter 1](/learn/hello/#s1-4) showed, a function takes values, its **parameters**, and gives back a value, its **result**; the code that calls it is its **caller**, and the values the caller passes are the **arguments**. A **contract** is the agreement between the two, written into the function's **header**, the lines from its name down to `=`. The **body**, after `=`, is how the function keeps its side.

A contract has two halves:

- A **precondition**, written `requires`, is what the caller promises about the arguments. It is this section's subject.
- A **postcondition**, written `ensures`, is what the function promises about its result. [Section 5.2](#s5-2) covers it.

A contract in Una is more than a comment: `una` checks both halves, for every caller and every input, before the program runs.

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

`monthly` uses `if` from [section 3.4](/learn/text-and-conditions/#s3-4): a checkout form allows 0 months, which means paying everything now. In many languages this code runs, and works, until some call passes 0 to `installment`. Then the division fails while the program runs, and the checkout stops in front of a customer. A test finds the problem only if someone thought to try 0.

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

You met this diagnostic in [section 2.2](/learn/numbers/#s2-2): every division by a value that is not a literal is a **proof obligation**, a fact that must be proven before the program may run, here `count != 0`. Nothing tells `una` that `count` is never 0, and the line `Note 2` gives the case that breaks it, `count = 0`: the **counterexample**. The `Help` line offers a guard, an `if` around the division, but a guard makes `installment` invent an answer for 0 installments, which has none. What `installment` needs is a way to say "never call me with 0", so that each caller, where the number comes from, makes sure of it. A precondition is that way.

Each example of this chapter is a package, made as [chapter 2](/learn/numbers/#each-step-is-a-package) explains, and the chapter's download, `05-contracts.tar.gz`, holds them all.

### What the verifier is

The **verifier** is the part of `una check` that proves facts about your program without running it. It runs after the other checks pass, in three steps:

1. **It lists what must be true.** Every place where the program relies on a fact becomes a question: "is `count != 0` here, whatever the inputs?" Such a question is a proof obligation. A division gives one, each `requires` gives one at every call, and each `ensures` gives one for the body.
2. **It asks a solver.** A **solver** is a program that answers such questions by reasoning about every possible value at once, not by trying values one after another. Una uses the solver Z3, at the exact version that `verification.lock` names, so every machine gets the same answers.
3. **It reports the answer.** An obligation is **proven** when it holds for every input, which needs no message. It is **refuted** when some input breaks it: that is U5001, and the input is the counterexample, on the line `Note 2: counterexample: …`. When the solver cannot decide, the obligation is **unknown**: that is U5002, an error too ([section 5.4](#s5-4)).

A test runs the code on the inputs someone wrote down. The verifier covers every input, before the program runs, and its proofs cost nothing when the program runs. In exchange, you write your conditions in a small language the solver can decide, [the refinement language](#the-refinement-language) of section 5.3.

### How to write `requires`

A `requires` clause is the word `requires` and a condition, on a line of its own under the header, indented two spaces, before `=`. A **condition** is an expression that is `true` or `false`, a `Bool` ([section 3.3](/learn/text-and-conditions/#s3-3)), such as `units >= 1`. A function with a clause is written in the long form of [chapter 1](/learn/hello/#s1-4): the header, the clauses, `=` alone on its line, then the body. A function may have any number of clauses, and every one must hold.

The step of this part shows every form a precondition takes. It works with two kinds of the store, a record and a sum ([chapter 4](/learn/kinds/)):

```una include="steps/02-clauses/src/checkout.una#CartLine..Zone" title="steps/02-clauses/src/checkout.una" caption="the kinds"
--- One line of a cart: a SKU, how many units, and the price of one unit in cents.
kind CartLine
  sku: Text
  quantity: Int
  unit_cents: Int

--- Where a parcel goes.
kind Zone = Local | National | Abroad
```

#### One condition

The simplest precondition names one parameter:

```una include="steps/02-clauses/src/checkout.una#unit_price" title="steps/02-clauses/src/checkout.una"
--- The price of one unit when a pack of `units` costs `pack_cents`, rounded down.
unit_price(pack_cents: Int, units: Int) -> Int
  requires units >= 1
=
  pack_cents / units
```

The body divides by `units`. The clause makes that safe, and every caller must show that its `units` is at least 1.

#### Several conditions, several clauses

A precondition may relate parameters to each other. Write each condition as a clause of its own:

```una include="steps/02-clauses/src/checkout.una#after_coupon" title="steps/02-clauses/src/checkout.una"
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

A condition may read the fields of a record parameter, and the length of a text with `.len`. It may join conditions with `and`; `or` and `not` work the same way:

```una include="steps/02-clauses/src/checkout.una#line_cents..family" title="steps/02-clauses/src/checkout.una"
--- What one line costs. The clause reads two fields of the line.
line_cents(line: CartLine) -> Int
  requires line.quantity >= 1 and line.unit_cents >= 0
=
  line.quantity * line.unit_cents

--- The product family of a SKU: its first four characters, as `LAMP` in `LAMP-01`.
family(sku: Text) -> Text
  requires sku.len >= 4
=
  sku.slice(start: 0, end: 4)
```

`family` cuts the first four characters with `slice`, whose own precondition ([section 3.2](/learn/text-and-conditions/#s3-2)) says that the cut must lie inside the text. `requires sku.len >= 4` is what lets `family` meet it.

#### A condition for one case: `implies` and `is`

`a implies b` reads "if `a`, then `b`". It holds whenever `a` is false, so it states a rule for one case only. `zone is Abroad` tests the variant of a sum, as in [section 4.2](/learn/kinds/#s4-2):

```una include="steps/02-clauses/src/checkout.una#shipping_cents" title="steps/02-clauses/src/checkout.una"
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

When the same condition appears in many clauses, give it a name with a `predicate`, and write `requires fits(off, price)`. [Predicates](#predicates-named-conditions), in section 5.3, show how.

#### Running the precondition forms

`main` calls each function once, with arguments that meet its precondition:

```una include="steps/02-clauses/src/checkout.una#main" title="steps/02-clauses/src/checkout.una"
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("one unit of a pack of 4: {unit_price(1990, units: 4)}")
  @console.print("after a coupon: {after_coupon(1990, off: 500)}")
  let one_line = line_cents(CartLine(sku: "LAMP-01", quantity: 2, unit_cents: 1990))
  @console.print("one line: {one_line}")
  let sku = "LAMP-01"
  @console.print("family of {sku}: {family(sku)}")
  @console.print("shipping: {shipping_cents(National, grams: 2300)} and {shipping_cents(Abroad, grams: 1500)}")
  @console.print("weekly price: {weekly_price(1990)} and {weekly_price(300)}")
```

`una run .` prints:

```text include="steps/02-clauses/expected/output.txt"
one unit of a pack of 4: 497
after a coupon: 1490
one line: 3980
family of LAMP-01: LAMP
shipping: 995 and 2800
weekly price: 1490 and 0
```

Each call is proven before it runs. `unit_price(1990, units: 4)` gives the verifier the literal 4, and `4 >= 1` holds. `family(sku)` passes a text whose value the verifier knows, `"LAMP-01"`, of length 7.

### Installments that never divide by zero

Back to installments, now with the precondition:

:::steps
```una include="steps/03-requires/src/installments.una" title="steps/03-requires/src/installments.una" verified="check, run"
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

1. **`requires count >= 1`.** The clause, under the header and before `=`.
2. **`total / count`.** The division's obligation, `count != 0`, now follows from the precondition.
3. **`if months < 1 then total else installment(total, count: months)`.** `months` comes from a checkout form and can be 0. In the `else` branch, the verifier knows that `months < 1` is false, so it proves `months >= 1` for the call.
4. **`installment(12000, count: 3)`.** The verifier proves `3 >= 1` at the call. With a literal, the proof is immediate.
:::

`una run .` prints:

```text include="steps/03-requires/expected/output.txt"
4000 a month for 3 months
12000 now, or 3000 a month for 4 months
```

### How a precondition is checked

#### What the verifier knows at a call

At each call, the verifier proves the callee's precondition with the arguments in place of the parameters. It can use every fact it has at that line:

- **Literals:** `installment(12000, count: 3)` gives `3 >= 1`.
- **The branch the call is in:** inside `else` of `if months < 1`, it knows `months >= 1`.
- **The caller's own `requires`:** a function that requires `n >= 2` may call `installment` with `n`.
- **What other calls promise:** the `ensures` of a function called earlier ([section 5.2](#s5-2)).
- **Kinds:** a value of a refined kind carries its condition ([section 5.3](#s5-3)).

It never uses what a function's body does, only what its header says. So a precondition is part of the function's public face: change it, and every call is checked again.

#### Inside the body

Inside the function, each `requires` is a fact. The verifier assumes it, and uses it to prove the obligations of the body: the division in `installment`, the `slice` in `family`. The body never tests the condition itself, and the condition costs nothing when the program runs.

#### A call that does not meet the precondition

Remove the guard from `monthly`, and call `installment` directly:

```diff include="steps/03-requires..steps/04-unguarded:src/installments.una" context="1" title="src/installments.una"
--- a/src/installments.una
+++ b/src/installments.una
@@ -10,3 +10,3 @@
 --- paying everything now.
-monthly(total: Int, months: Int) -> Int = if months < 1 then total else installment(total, count: months)
+monthly(total: Int, months: Int) -> Int = installment(total, count: months)
 
```

`una check .` now refutes the call, and says why:

```text include="steps/04-unguarded/expected/rendered.txt"
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

Read the diagnostic from the top. The first line names the obligation, a precondition, and its goal, `months >= 1`, written with the caller's argument in place of `count`. The two marks show the clause that asked for it, on line 5, and the call that does not meet it, on line 11. `Note 2` is the counterexample: with `months = 0`, the goal is false. The `Help` lines are the repairs, best first:

1. a stronger type for `months`, a refined kind ([section 5.3](#s5-3));
2. a `requires` on `monthly`, which moves the obligation to its callers;
3. a guard, as the `if` was;
4. last, `checked`, a test at run time, which [section 7.5](/learn/failure/#s7-5) covers.

#### What a `requires` clause may say

- It reads the parameters as the caller passes them. It cannot name the result: `result` belongs to `ensures`, and elsewhere it is U2012.
- It is written in the refinement language: no calls of ordinary functions, and products and divisions only by a literal. Anything else is U2014 ([a contract outside the refinement language](#a-contract-outside-the-refinement-language-u2014)).

### A precondition or a guard

A precondition and a guard both protect the same division. They differ in who handles the bad case:

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Make a bad argument the caller's mistake, checked at every call | `requires` |
| Handle every argument, with an answer for the bad case | a guard, `if` in the body ([section 3.4](/learn/text-and-conditions/#s3-4)) |
| State a rule that holds of every value of a type | a refined kind ([section 5.3](#s5-3)) |
| Pass an obligation on to your own callers | `requires`, with the same condition |
:::

`monthly` uses a guard because 0 months has a meaning: pay now. `installment` uses a precondition because 0 installments has none.

### Check yourself: preconditions

`weekly_price` takes the weekly coupon of 5.00 off a price, and turns a price below 5.00 into 0:

```una include="steps/02-clauses/src/checkout.una#weekly_price" title="steps/02-clauses/src/checkout.una"
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

## 5.2 Postconditions: `ensures` and counterexamples

### What a postcondition promises

A postcondition is the function's half of the contract: what holds of the result when the function returns. Inside the clause, `result` names the value returned. The verifier proves the clause on every path that returns, and every caller may then assume it without reading the body.

Think of a guarantee printed on a receipt: "this price never goes up after you pay". You do not need to know how the shop computes its prices to rely on it. A postcondition is that kind of promise, made by a function to every caller, and `una` holds the function to it.

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

The verifier does not read the body of `after_coupon` when it checks `left_on_card`. It reads only its header, and the header says nothing about the result, so `due` could be any whole number. `Note 2` shows a card of 0 and a price of 0 for which the result is −1. For that, `due` must be −1, which the counterexample leaves out. It is not a run: the real `after_coupon` never returns a negative `due`. It is what the header allows.

There is a reason the verifier works this way. If it read every body, a change to the body of `after_coupon` could silently break a proof in `left_on_card`, or in any of a hundred callers. By reading headers only, each function is checked once, against its own contract, and a caller depends on the promise, not on the code behind it. So a function promises in its header exactly what its callers need.

### How to write `ensures`

An `ensures` clause is the word `ensures` and a condition, on its own line under the header, before `=`. It sits with the `requires` clauses, after them, and a function may have any number of each. The condition may read the parameters, as the caller passed them, and `result`, the value the function returns. Like `requires`, it is written in the refinement language.

#### A bound on the result

The rate of a parcel is never below 4.50, whatever it weighs:

```una include="steps/07-forms/src/fees.una#parcel_rate" title="steps/07-forms/src/fees.una"
--- The rate of a parcel of `grams` grams: 450 cents for the first kilogram, and 250 more
--- for each kilogram or part of one after it. The clause states a lower bound.
pub parcel_rate(grams: Int) -> Int
  requires grams > 0
  ensures result >= 450
=
  let kilos = (grams + 999) / 1_000
  450 + (kilos - 1) * 250
```

`ensures result >= 450` is a **bound**: it does not say what the rate is, only how low it can go. It needs the precondition. Take `requires grams > 0` away:

```diff include="steps/07-forms..steps/08-no-requires-2:src/fees.una" title="src/fees.una" context="1"
--- a/src/fees.una
+++ b/src/fees.una
@@ -11,3 +11,2 @@
 pub parcel_rate(grams: Int) -> Int
-  requires grams > 0
   ensures result >= 450
```

```text include="steps/08-no-requires-2/expected/rendered.txt#L1-L10,L18"
[U5001] Error: postcondition of `parcel_rate` is refuted
    ╭─[ src/fees.una:15:3 ]
    │
 12 │   ensures result >= 450
    │           ──────┬──────
    │                 ╰──────── ensures clause
    │
 15 │   450 + (kilos - 1) * 250
    │   ───────────┬───────────
    │              ╰───────────── postcondition of `parcel_rate` is refuted
    │ Note 2: counterexample: grams = -999, result = 200
```

The verifier found a weight that breaks the promise: `grams = -999`. A parcel of minus 999 grams makes `kilos` 0, and the rate 200. No parcel weighs less than nothing, but nothing in the function said so, and a caller could pass such a value. `requires grams > 0` rules out every weight of zero or below, and with it the promise holds. This is how the two halves work together: the precondition limits the inputs, and the postcondition is proven for those inputs only.

#### The exact result

A clause can state the result exactly, with `==`:

```una include="steps/07-forms/src/fees.una#with_card_fee" title="steps/07-forms/src/fees.una"
--- The amount with the card fee of 50 cents added. The clause states the exact result.
pub with_card_fee(cents: Int) -> Int
  ensures result == cents + 50
=
  cents + 50
```

A caller then knows everything the function does from its header alone.

#### A promise for some cases: `implies`

A promise may cover only the cases a caller needs. `status` promises what an empty shelf and a full one give, and says nothing about the shelves in between. It returns a variant of a sum kind:

```una include="steps/09-promises/src/stockroom.una#Shelf" title="steps/09-promises/src/stockroom.una"
--- How full a shelf is.
kind Shelf = Empty | Low | Stocked
```

```una include="steps/09-promises/src/stockroom.una#status" title="steps/09-promises/src/stockroom.una"
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

#### A `Bool` result

A clause can give the whole answer of a function that returns a `Bool`:

```una include="steps/09-promises/src/stockroom.una#free_shipping" title="steps/09-promises/src/stockroom.una"
--- Whether an order ships free. The clause gives the whole answer.
free_shipping(total: Int) -> Bool
  ensures result == (total >= 5000)
=
  total >= 5000
```

`result == (total >= 5000)` compares two `Bool` values: the result is `true` exactly when the total is at least 5000.

#### Fields of the result

A promise may speak of the fields of a record result:

```una include="steps/09-promises/src/stockroom.una#Packing" title="steps/09-promises/src/stockroom.una"
--- How `units` units pack in boxes of 6, and how many stay loose.
kind Packing
  boxes: Int
  loose: Int
```

```una include="steps/09-promises/src/stockroom.una#pack" title="steps/09-promises/src/stockroom.una"
--- How `units` units pack in boxes of 6. The clauses speak of the fields of the result.
pack(units: Int) -> Packing
  requires units >= 0
  ensures result.boxes * 6 + result.loose == units
  ensures result.loose >= 0 and result.loose < 6
=
  Packing(boxes: units / 6, loose: units mod 6)
```

`pack` has two clauses, which hold together. The first relates the two fields: boxes of 6 and the loose units add up to `units`. The second bounds one field. `result.boxes * 6` is allowed in a clause, since one side of the product is a literal.

#### The value before the call: `old`

A function can also change a value its caller passes in, with an `edit` parameter, which [section 16.2](/learn/memory/#s16-2) teaches; its `ensures` then names the value from before the call as `old(name)`. Nothing in this chapter changes a parameter.

#### Running the promise forms

`una run .` in the two steps prints:

```text include="steps/07-forms/expected/output.txt"
with the card fee: 2040
500 g: 450, 2300 g: 950
1001 g: 700, 2000 g: 700
```

```text include="steps/09-promises/expected/output.txt#L1-L3"
Empty Low Stocked
free shipping at 4999: false, at 5000: true
20 units: 3 boxes and 2 loose
```

### A coupon that never goes negative

A coupon is a good first case of a real rule. It takes some cents off a price, and two rules hold whatever the coupon: the price never becomes negative, and it never goes up.

:::steps
```una include="steps/10-ensures/src/coupons.una" title="steps/10-ensures/src/coupons.una" verified="check, run, test"
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
2. **`ensures off <= price implies result == price - off`.** A third clause says what the result is when the coupon fits. It says nothing when `off > price`.
3. **`left_on_card`.** A caller. It knows `after_coupon` only by its header. With the first two clauses alone, it knows only that `due` is between 0 and `price`, which is not enough to prove `result >= 0`. The third clause gives it what it needs.
4. **`example "a coupon worth more than the price gives 0"`.** The example. It pins down the case where the coupon is worth more than the price. [From a counterexample to an example](#from-a-counterexample-to-an-example) shows where it comes from.
:::

`una run .` prints:

```text include="steps/10-ensures/expected/output.txt"
1490 0
3010 0
```

### Reading a counterexample

Now write the body most people write first, `price - off`, and check:

```diff include="steps/10-ensures..steps/11-counterexample:src/coupons.una" context="1" title="src/coupons.una"
--- a/src/coupons.una
+++ b/src/coupons.una
@@ -11,3 +11,3 @@
 =
-  if off > price then 0 else price - off
+  price - off
 
```

```text include="steps/11-counterexample/expected/rendered.txt"
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

Read it in four steps:

1. **The first line** names the promise that failed: the postcondition of `after_coupon`.
2. **The two marks** point at the clause it breaks, `ensures result >= 0` on line 8, and at the returned expression, `price - off` on line 12.
3. **`Help 1` and `Help 2`** are the two repairs: change the body, or change the clause. The verifier cannot tell which one is wrong. That is your decision.
4. **`Note 2`** is the counterexample, `off = 1, price = 0, result = -1`: a coupon of 1 cent on a free item. Run the body by hand on those values and the result is −1, so the rule is broken.

The solver often picks the smallest numbers that break the rule, such as 0 and 1, so a case that looks artificial usually stands for a real one: here, any coupon worth more than its order.

#### When the body calls other functions

When the body has no calls, as here, a counterexample is a case you can run by hand. When the body calls other functions, the verifier knows each call only by the callee's header, so a call's result in the counterexample can be any value that header allows, even one the callee never returns, as in [Why callers need a promise](#why-callers-need-a-promise). Then the values are not a run, but they still point at the problem: the body relies on something the callee does not promise.

### From a counterexample to an example

Two things to do with a counterexample:

1. **Fix the code or the contract.** Here the code is wrong: a coupon larger than the price must give 0. Sometimes the contract promises more than you meant.
2. **Keep the case as an example,** when it is a run, as this one is. The example in `coupons.una`, written as in [chapter 1](/learn/hello/#s1-7), is this counterexample. The proof already covers it, but the example documents the case for a reader and shows it in `una test .`:

```text include="steps/10-ensures/expected/commands/test.txt#L2-L4"
example coupons "a coupon worth more than the price gives 0" ... ok

1 example: 1 passed, 0 failed
```

### How a postcondition is checked

#### Every path that returns

A body can return in several places: each branch of an `if`, each arm of a `when`. The verifier proves each `ensures` clause on every one of them, with the facts of that path: the function's `requires`, the condition of the branch, and the promises of the calls made on the way. One path that breaks the clause is enough for U5001, and the diagnostic points at that path's returned expression.

#### What a caller gets

After a call, the caller may assume every `ensures` clause of the callee, with its own arguments in place of the parameters. After `let due = after_coupon(price, off: card)`, `left_on_card` knows `due >= 0`, `due <= price`, and `card <= price implies due == price - card`. Promises add up: each function's `ensures` is a fact for the next one, and in [the day-to-day program](#s5-6) a chain of them proves that no total is negative.

The standard library has contracts too, and the verifier trusts them without reading their bodies. `min`, the smaller of two whole numbers ([section 2.2](/learn/numbers/#s2-2)), as in `min(total / 100, b: 100)`, promises a result no larger than either argument, and equal to one of them.

#### A promise the body does not keep

Raise the promised minimum of `parcel_rate` to 500:

```diff include="steps/07-forms..steps/12-promise:src/fees.una" title="src/fees.una" context="0"
--- a/src/fees.una
+++ b/src/fees.una
@@ -13 +13 @@
-  ensures result >= 450
+  ensures result >= 500
```

```text include="steps/12-promise/expected/rendered.txt#L1-L10,L18"
[U5001] Error: postcondition of `parcel_rate` is refuted
    ╭─[ src/fees.una:16:3 ]
    │
 13 │   ensures result >= 500
    │           ──────┬──────
    │                 ╰──────── ensures clause
    │
 16 │   450 + (kilos - 1) * 250
    │   ───────────┬───────────
    │              ╰───────────── postcondition of `parcel_rate` is refuted
    │ Note 2: counterexample: grams = 1000, result = 450
```

The counterexample is a parcel of 1000 g, for which the body returns 450. Either the body or the clause is wrong, and here it is the clause: the rate of the first kilogram is 4.50.

#### What `ensures` does not cover

> [!NOTE]
> `ensures` describes normal returns only. A function that fails, which [section 7.2](/learn/failure/#s7-2) teaches, returns no value on that path, and its postcondition says nothing about it. Contracts also do not prove that a function ends: they hold *if* it returns.

#### What an `ensures` clause may say

`result` is allowed only in `ensures`, and in the `expect` lines of examples (U2012 elsewhere). The rest of the rules of a `requires` clause apply: the parameters, the refinement language, and no calls but of the predicates of [section 5.3](#predicates-named-conditions).

### A contract or an example

A postcondition and an example both say something about the result, but not the same thing:

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| State a rule that holds for every input, such as "never negative" | `ensures` |
| Give callers a fact they need to prove their own contracts | `ensures` |
| Pin down one exact answer, such as "10% of 188.85 is 18.88" | an `example` |
| Keep a counterexample as a case a reader can see | an `example` |
| Describe what the function is for, in words | a doc comment (`---`) |
:::

How much to promise is a choice. Promise what the callers need and what will stay true. A promise that states the exact result, as `free_shipping`'s does, gives callers the most, and ties the body to it for good. A bound, such as `result <= price`, leaves the body free to change, for example to round differently.

### Check yourself: postconditions

`points` gives a customer one loyalty point for each whole 1.00, and at most 100 points for one order:

```una include="steps/09-promises/src/stockroom.una#points" title="steps/09-promises/src/stockroom.una"
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
It checks. The body is a call of `min`, whose contract promises a result no larger than `b`, which is 100, and equal to one of its two arguments. `total / 100` is at least 0, since `total` is, and 100 is too, so the result is at least 0. Both clauses follow from the promise of `min`, without a branch in the body.

```text include="steps/09-promises/expected/output.txt#L4"
points for 250.00: 100
```

25000 cents is 250 whole units of 1.00, and `min` keeps it at 100.
:::

A second one: what may a caller assume about `status(5)`?

:::answer Show the answer
Nothing but its type: the result is a `Shelf`. Both clauses of `status` speak of other inputs, 0 and from 10 up, so for 5 they say nothing. The body returns `Low`, but a caller cannot rely on that, since the header does not promise it. To let callers rely on it, add `ensures units >= 1 and units < 10 implies result is Low`.
:::

## 5.3 Refined kinds and predicates

### A rule on the kind

A **type** says what sort of value a name holds: `Int` holds whole numbers, `Text` holds texts, and a `kind` declares a type of your own ([chapter 4](/learn/kinds/)). A **refined kind** is a type with a condition attached: a base type, and a rule that every value of the kind obeys. `kind Cents = Int where it >= 0` is the whole numbers that are not negative. In the condition, `it` stands for the value.

Think of a parcel locker that only takes parcels below a size. A parcel that got in fits, and nobody measures it again. A refined kind is that locker: a value is checked once, when it enters the kind, and everyone who receives a `Cents` knows it is not negative.

### Why put a rule on a kind

A price in cents is never negative. With preconditions alone, every function that takes a price must say so, and every function that returns one must promise it:

```una include="steps/13-repeated/src/prices.una" title="steps/13-repeated/src/prices.una" verified="check, run"
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

```text include="steps/13-repeated/expected/output.txt"
after a coupon: 1490
with a fee: 2485
on the shelf label: -510 cents
```

The program checks, and the last line prints a negative price on a shelf label. The rule "a price is never negative" lives in the clauses of each function, written again each time, and `marked_down` forgot it. Nothing connects the three functions: they all take an `Int`, and an `Int` may be anything.

Put the rule on a kind, `Cents`, and make it the type of every price. Then the rule is written once, a function that returns `Cents` must prove it on every path, and a function that receives `Cents` gets it for free. `marked_down` with a result of type `Cents` would not check: `price - cut` is negative whenever the cut is larger than the price, and the verifier would refute it with such a case.

### How to write a refined kind

A refined kind is a `kind` declaration with three parts: its name, `=` and the base type, then the condition after `where`. The condition reads the value as `it`, and is written in the refinement language, like `requires` and `ensures`. The step of this part shows every form:

```una include="steps/14-refined-forms/src/catalog.una#Cents..BulkLine" title="steps/14-refined-forms/src/catalog.una" caption="the kinds"
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

--- One line of a delivery. The quantity is refined in place, with `in`.
kind Line
  sku: Text
  quantity: Int in 1..99

--- A line of at least 10 units, which earns free units.
kind BulkLine = Line where it.quantity >= 10
```

#### A condition with `where`

`kind Cents = Int where it >= 0` is the general form. The prelude, the names every module can use without declaring them, already has a kind like `Cents`: `Nat`, which is `Int where it >= 0`. Any condition of the refinement language works: comparisons, `and`, `or`, `not`, `implies`, and calls of the [predicates](#predicates-named-conditions) of this section.

#### A range with `in`

`Int in 0..100` is short for `Int where 0 <= it and it <= 100`: `..` keeps both ends. `Int in 0..<12` leaves the end out, which fits a count of positions: 12 slots numbered 0 to 11. `next_slot` moves to the next slot and wraps around:

```una include="steps/14-refined-forms/src/catalog.una#next_slot" title="steps/14-refined-forms/src/catalog.una"
--- The next slot of the shelf, back to 0 after the last one.
next_slot(slot: Slot) -> Slot = if slot < 11 then slot + 1 else 0
```

The result is a `Slot`, so the verifier proves both branches: `slot + 1` is below 12 when `slot < 11`, and 0 is in range.

#### Refinements of refinements, and type arguments

A refinement of a refined kind adds its condition to the first: `kind Small = Cents where it < 100` is both `>= 0` and `< 100`. In the step, a staff discount is a `Percent` of at most 50, so a value of it holds both conditions:

```una include="steps/14-refined-forms/src/catalog.una#staff_pays" title="steps/14-refined-forms/src/catalog.una"
--- What a staff member pays, in percent of the price: always at least half.
staff_pays(rate: StaffDiscount) -> Percent
  ensures result >= 50
=
  100 - rate
```

`100 - rate` is a `Percent`, and at least 50, because `rate` is between 0 and 50.

> [!IMPORTANT]
> In editions 0.1 and 0.2, which this book uses, a refined kind cannot be the type argument of a generic kind ([section 4.4](/learn/kinds/#s4-4)): with `kind Change[T]`, the type `Change[Cents]` is ill-formed (U2002), and the diagnostic asks for the base type, `Change[Int]`. Put the refinement on a field of a record instead, as `Line` does with `quantity`. Edition 0.3 allows refined type arguments ([chapter 19](/learn/editions/)).

#### Texts and records

The base can be any type. A condition on a text usually reads its length, and a condition on a record reads its fields:

```una include="steps/14-refined-forms/src/catalog.una#family..free_units" title="steps/14-refined-forms/src/catalog.una"
--- The product family of a SKU: its first four characters.
family(sku: Sku) -> Text = sku.slice(start: 0, end: 4)

--- The free units of a bulk line: one for every 10 units.
free_units(line: BulkLine) -> Int
  ensures result >= 1
=
  line.quantity / 10
```

- `Sku` is a text of at least four characters, so `family` can cut four characters with `slice` with no clause of its own: the kind carries the fact.
- `BulkLine` is a `Line` whose quantity is at least 10, so `free_units` can promise at least one free unit.

#### A range in place

A range can also be written right where a type goes, without a `kind`: on a field, as `quantity: Int in 1..99` in `Line`, or on a parameter:

```una include="steps/14-refined-forms/src/catalog.una#place" title="steps/14-refined-forms/src/catalog.una"
--- Where to put a box: a row from 1 to 5, refined in place, and a slot.
place(row: Int in 1..5, slot: Slot) -> Text = "row {row}, slot {slot}"
```

A `where` cannot be written in place: a condition other than a range needs a named kind.

#### Running the kind forms

`main` calls each function. Among its lines:

```text include="steps/14-refined-forms/expected/output.txt#L2-L3,L5"
after slot 4: 5, after slot 11: 0
family of LAMP-01: LAMP
row 2, slot 7
```

### Cents, quantities and free shipping

Now the kinds at work in a cart, with a predicate, a named condition that [Predicates](#predicates-named-conditions) explains in full:

:::steps
```una include="steps/15-refined/src/cart.una" title="steps/15-refined/src/cart.una" verified="check, run"
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
3. **`predicate reflect ships_free(total: Cents) -> Bool = total >= 5000`.** A named condition. Code may call it like any function, as `shipping` does.
4. **`ensures ships_free(total) implies result == 0`.** A contract that names a business rule reads as the rule.
5. **`if line.quantity < 99`.** An `if` over several lines ([section 3.4](/learn/text-and-conditions/#s3-4)). `line.quantity + 1` enters `Quantity` again, and the guard proves that it fits. Without the guard, the verifier refutes it with a line of 99 units, as [A value that does not fit](#a-value-that-does-not-fit) shows.
:::

`una run .` prints:

```text include="steps/15-refined/expected/output.txt"
3 x LAMP-01
shipping 495, then 0
```

### How a refined kind is checked

#### Where a value enters the kind

The verifier proves the condition at every place a value enters the kind: an argument, a returned value, a field of a record, and a `let` with the kind written, such as `let total: Cents = gross - off`. The other way needs no proof: a `Cents` goes wherever an `Int` goes.

So the work happens at the edges. `shipping` returns 0 or 495, and the verifier proves each is a `Cents`. `Line(sku: "LAMP-01", unit_cents: 1990, quantity: 2)` proves `1990 >= 0` and `2 in 1..99`. A function that only passes a `Cents` along has nothing new to prove.

#### What a value of the kind gives back

Wherever a value of a refined kind is read, its condition is a fact: a parameter of the kind, a field, the result of a call that returns the kind. `family` cuts a `Sku` without a clause, because the condition comes with the value.

#### A value that does not fit

Take the guard out of `one_more`, and add a unit whatever the quantity:

```diff include="steps/15-refined..steps/16-one-more:src/cart.una" context="1" title="src/cart.una"
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

```text include="steps/16-one-more/expected/rendered.txt"
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

A `reflect` predicate uses no capabilities, cannot fail, and returns a value for every input. Its body is written in the refinement language. It may call other `reflect` predicates, but never itself, directly or through another predicate (U2015). The other kind, an `opaque` predicate, whose body the verifier does not see, comes with the run-time tests of [section 7.5](/learn/failure/#s7-5).

#### Where a predicate is used

The step declares three predicates and uses them in every place a condition goes:

```una include="steps/17-predicates/src/shipping.una#Cents..thank_you" title="steps/17-predicates/src/shipping.una"
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

```text include="steps/17-predicates/expected/output.txt"
after a coupon: 1490
shipping 495, then 0
gift wrap, standard
6200 cents, shipped free
```

`thank_you(6200)` proves that 6200 is a `Cents` and that `ships_free(6200)` holds, which the verifier computes from the body of `ships_free`.

### The refinement language

The condition of a refinement, and every `requires` and `ensures` clause, is written in the **refinement language**, the part of Una the solver decides:

- whole number, `Bool` and text literals, the parameters, `result`, `it`, fields, and `.len`;
- `+`, `-` and unary `-`; `*` when one side is a literal; `/` and `mod` by a literal that is not zero;
- the comparisons `==`, `!=`, `<`, `<=`, `>`, `>=`, and `in` a range, `is` a variant;
- `and`, `or`, `not`, `implies`;
- calls of `reflect` predicates.

Anything else in a clause, such as the product of two parameters, is U2014 ([a contract outside the refinement language](#a-contract-outside-the-refinement-language-u2014)). Some things look allowed and are not: ordering two texts with `<`, comparing with a variant by `==` (write `is`), and calls of ordinary functions. A clause that needs one of these needs a different statement of the rule.

### A precondition, a refined kind or a predicate

Several tools state a rule about a value. Choose by where the rule belongs:

:::decide
**Which to use:**

| The rule… | Use |
| --- | --- |
| Holds of every value of a type, wherever it goes, such as "a price is never negative" | a refined kind |
| Is about one function's arguments together, such as "the coupon is no larger than the price" | `requires` |
| Relates the result to the arguments | `ensures` |
| Has a name in the business, and appears in several clauses | a `reflect` predicate, used in them |
| Can only be decided by running code, such as the format of a barcode | a test at run time ([section 7.5](/learn/failure/#s7-5)) |
| Concerns data from outside the program | a check where it enters ([section 7.6](/learn/failure/#s7-6)) |
:::

A refined kind is usually the strongest choice: one declaration, checked at every way in, and a fact at every use. A precondition fits rules that tie several parameters together, which no single type can carry.

### Check yourself: refined kinds and predicates

`staff_pays` takes a `StaffDiscount`, a `Percent` of at most 50, and promises a result of at least 50:

```una include="steps/14-refined-forms/src/catalog.una#StaffDiscount" title="steps/14-refined-forms/src/catalog.una"
--- A staff discount: a `Percent` of at most 50. It holds both conditions.
kind StaffDiscount = Percent where it <= 50
```

What does `staff_pays(30)` return? Which of these calls check: `staff_pays(0)`, `staff_pays(50)`, `staff_pays(60)`?

:::answer Show the answer
```text include="steps/14-refined-forms/expected/output.txt#L1"
staff pay 70% and 50%
```

`staff_pays(30)` is 70. `staff_pays(0)` and `staff_pays(50)` check: both values are in `0..100` and at most 50. `staff_pays(60)` does not: 60 is a `Percent`, but not a `StaffDiscount`, and the refinement is refuted at the call.
:::

A bulk line is a `Line` of at least 10 units. What does `free_units(Line(sku: "RUG-07", quantity: 24))` return, and what would happen with a quantity of 9?

:::answer Show the answer
```text include="steps/14-refined-forms/expected/output.txt#L4"
free units: 2
```

24 units give two free units: 24 / 10 rounds down to 2. With 9 units the call does not check: `free_units` takes a `BulkLine`, and the verifier refutes the condition of `BulkLine` where the line enters the kind. The program never runs with a bulk line of 9 units.
:::

## 5.4 What the verifier proves

### What an obligation is

Before a new shop opens, an inspector walks through it with a checklist: the fire exits, the wiring, the ramp at the door. Each item gets one mark: passed, failed, or could not be inspected. The shop opens only when every item has passed.

The verifier works through your program the same way. Its checklist is the list of proof obligations, or **obligations** for short: one question for each place where the program relies on a fact, as [What the verifier is](#what-the-verifier-is) in section 5.1 says. "Is this divisor never 0?" "Does this call meet the callee's `requires`?" "Does this value fit the kind it enters?" Each question gets one mark, its **status**:

- **proven:** the fact holds for every input;
- **refuted:** some input breaks it, and the verifier shows that input;
- **unknown:** the solver could not decide.

A program checks only when every obligation is proven. You never write an obligation yourself: `una` derives them from what you wrote, the contracts, the refined kinds, the divisions and a few other constructs. This section shows how to see them, what each kind asks, and what to do when the solver cannot answer.

### Why list the obligations

When `una check .` passes, it prints nothing. Silence is the right answer for a program that is correct, but it does not tell you what was proven. Was the guard you just added the thing that proved the division safe? Did the rule you care about become a question at all? A function with no contract has nothing to prove, and it passes in the same silence as a function whose every promise was proven.

A reviewer needs to see the checklist, not only the result. `una obligations .` prints it: every obligation of the package, proven or not, with where it comes from and what it asks.

### How to list the obligations: `una obligations`

In the package's directory, run:

```sh
una obligations .
```

It checks the package first. When the package has an error that is not an obligation, such as a syntax error or a missing `uses`, it reports that error instead of a list. Otherwise it prints one line per obligation. The step of this part has one small function for each kind of obligation, and it prints:

:::steps
```text include="steps/18-obligation-kinds/expected/commands/obligations.txt"
$ una obligations .
proven   ob-b852e63daefa division      src/stockroom.una:11:3 units != 0
proven   ob-2a3920108dd8 postcondition src/stockroom.una:15:11 result <= 99
proven   ob-0d6cd810c278 refinement    src/stockroom.una:20:1 result >= 0
proven   ob-011bffbfed9b division      src/stockroom.una:23:72 people != 0
proven   ob-7ed451ea7768 overflow      src/stockroom.una:29:51 shelf + 1 in 0..255
proven   ob-20fdd4197f66 precondition  src/stockroom.una:34:31 4 >= 1
proven   ob-82707e2c71ad refinement    src/stockroom.una:34:101 1000 >= 0
proven   ob-8ef0d001a88c refinement    src/stockroom.una:35:61 12 in 0..999
```

1. **`proven`.** The status. A list with only `proven` lines is a package that checks.
2. **`ob-b852e63daefa`.** The obligation's identity: a short name that stays the same while the obligation does not change.
3. **`division`.** The kind of question, which the next part explains one by one.
4. **`src/stockroom.una:11:3`.** Where it is: the file, the line and the column of the code that raised it.
5. **`units != 0`.** The goal: the fact the solver must prove, written in Una with the names of your code.
:::

Each line is one question, answered on its own. `una --json obligations .` prints the same list as JSON, for tools and agents.

### The kinds of obligations

Edition `0.2` has six kinds, and each comes from one construct. This section shows five, with one function of the step for each. The sixth, `exhaustive`, comes from a `when` that chooses by a number, which [section 8.2](/learn/choices/#s8-2) teaches with its obligation.

#### `precondition`: at every call of a function with `requires`

```una include="steps/18-obligation-kinds/src/stockroom.una#unit_price" title="steps/18-obligation-kinds/src/stockroom.una"
--- The price of one unit of a pack. The clause gives each call a precondition obligation, and
--- the division gives the body a division obligation.
unit_price(pack_cents: Int, units: Int) -> Int
  requires units >= 1
=
  pack_cents / units
```

```text include="steps/18-obligation-kinds/expected/commands/obligations.txt#L7"
proven   ob-20fdd4197f66 precondition  src/stockroom.una:34:31 4 >= 1
```

The goal is the callee's clause, `units >= 1`, with the caller's argument in place of the parameter. `main` calls `unit_price(1990, units: 4)`, so the goal is `4 >= 1`. The line points at the call, in `main`, not at the clause.

#### `division`: at every `/` and `mod` by a value that is not a literal

The same function divides by `units`, which gives a second obligation, in the body:

```text include="steps/18-obligation-kinds/expected/commands/obligations.txt#L2"
proven   ob-b852e63daefa division      src/stockroom.una:11:3 units != 0
```

The precondition proves it: inside the body, `units >= 1` is a fact, so `units` is never 0. `share` proves its division with a guard instead:

```una include="steps/18-obligation-kinds/src/stockroom.una#share" title="steps/18-obligation-kinds/src/stockroom.una"
--- A share of a bill. The guard proves the division obligation.
share(total: Int, people: Int) -> Int = if people == 0 then total else total / people
```

```text include="steps/18-obligation-kinds/expected/commands/obligations.txt#L5"
proven   ob-011bffbfed9b division      src/stockroom.una:23:72 people != 0
```

In the `else` branch, `people == 0` is false. A division by a literal, such as `total / 100`, raises no obligation: the divisor is visibly not 0.

#### `postcondition`: at every return of a function with `ensures`

```una include="steps/18-obligation-kinds/src/stockroom.una#capped" title="steps/18-obligation-kinds/src/stockroom.una"
--- At most 99 units on one line. The clause gives the body a postcondition obligation.
capped(units: Int) -> Int
  ensures result <= 99
=
  if units > 99 then 99 else units
```

```text include="steps/18-obligation-kinds/expected/commands/obligations.txt#L3"
proven   ob-2a3920108dd8 postcondition src/stockroom.una:15:11 result <= 99
```

One obligation covers every path that returns: both branches of the `if`. The line points at the clause.

#### `refinement`: wherever a value enters a refined kind

```una include="steps/18-obligation-kinds/src/stockroom.una#with_fee" title="steps/18-obligation-kinds/src/stockroom.una"
--- A price with the shipping fee. The result enters `Cents`: a refinement obligation.
with_fee(price: Cents) -> Cents = price + 495
```

```text include="steps/18-obligation-kinds/expected/commands/obligations.txt#L4,L8-L9"
proven   ob-0d6cd810c278 refinement    src/stockroom.una:20:1 result >= 0
proven   ob-82707e2c71ad refinement    src/stockroom.una:34:101 1000 >= 0
proven   ob-8ef0d001a88c refinement    src/stockroom.una:35:61 12 in 0..999
```

The first line is the result entering `Cents`: `result >= 0`. The other two are arguments entering the refined parameters of their functions in `main`: 1000 entering `Cents`, and 12 entering `Int in 0..999`, the type of the parameter of `fill(units: Int in 0..999)`, the step's function that says how full a bin is. The goal is the kind's condition with the value in place of `it`.

#### `overflow`: at arithmetic on a fixed-width integer, and at a conversion to a narrower one

```una include="steps/18-obligation-kinds/src/stockroom.una#next_shelf" title="steps/18-obligation-kinds/src/stockroom.una"
--- The next shelf of a rack of 201 shelves. `U8` holds 0 to 255: an overflow obligation.
next_shelf(shelf: U8) -> U8 = if shelf < 200 then shelf + 1 else 0
```

```text include="steps/18-obligation-kinds/expected/commands/obligations.txt#L6"
proven   ob-7ed451ea7768 overflow      src/stockroom.una:29:51 shelf + 1 in 0..255
```

A `U8` holds the whole numbers 0 to 255 ([section 2.3](/learn/numbers/#s2-3)). `shelf + 1` must stay in that range, and the guard `shelf < 200` proves it does. A conversion of a value to a narrower fixed-width type raises the same kind of obligation: the value must fit.

#### Two more kinds in edition `0.3`

Edition `0.3`, a preview of the next version of the language, adds two kinds, which come from the limits on authority of [chapter 13](/learn/authority/): `effect_condition` and `contract_lock`. Packages on edition `0.2`, as every step of this chapter is, never see them.

#### Running the step

```text include="steps/18-obligation-kinds/expected/output.txt"
unit price 497, capped 99, with fee 1495
share 333, bin stocked, next shelf 8
```

### The obligations of a cart

Now the list for a real module: the cart of [Cents, quantities and free shipping](#cents-quantities-and-free-shipping), in section 5.3. It has no division and no `when` on numbers, so its obligations are refinements and one postcondition:

```text include="steps/15-refined/expected/commands/obligations.txt"
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

Read it against the code, line by line:

1. **`19:1 result >= 0`.** `shipping` returns `Cents`, so its result must not be negative, on both branches. The line points at the function.
2. **`20:11 ships_free(total) implies result == 0`.** The `ensures` of `shipping`.
3. **`22:17 total >= 0`.** `shipping` calls `ships_free(total)`, whose parameter is `Cents`.
4. **`28:37 line.unit_cents >= 0`** and **`28:64 (line.quantity + 1) in 1..99`.** `one_more` builds a `Line`, so each refined field proves its kind. The second is the one the guard `if line.quantity < 99` proves.
5. **`35:47` to `38:61`.** `main` builds a line and calls `shipping` with literals. Each literal entering a refined kind is a question, and an easy one.

Every rule of the cart that matters is on this list, and so is every place where a value could break one. When a line you expected is missing, the rule did not become a question: look for a contract or a kind that is not there.

### How an obligation is answered

#### With the facts of its path

The solver answers each obligation with the facts known at its place in the code, and only those: the function's `requires`, the conditions of the `if` branches and `when` arms on the way, the refined kinds of the values in scope, and the `ensures` of the functions called before it. It never uses what a callee's body does. So a guard proves an obligation only inside its branch, and a fact proven in one function reaches another only through a header.

#### Statuses

- **proven:** nothing to report. The obligation costs nothing when the program runs.
- **refuted:** U5001, with a counterexample, which [section 5.2](#s5-2) shows how to read.
- **unknown:** U5002, with the reason. This is an error too: `una` never passes a program with a missing proof.

#### Identities

The identity, such as `ob-2a5905c8f53d`, comes from the module, the function, the kind and the goal. An edit that does not change the obligation keeps its identity, so a reviewer can follow one obligation across versions of the code. The same goal of the same kind twice in one function shares one identity.

#### A pinned solver

The answers come from the solver Z3 at the version `verification.lock` names, with a fixed **step budget**, the most work it may do on one question. Within the step budget, the same program and the same lock give the same answers on every machine.

### When the solver cannot decide: U5002

#### What the solver decides

The solver decides **linear arithmetic**: sums and differences of values, products where one side is a literal, such as `price * 3`, and quotients and remainders by a literal that is not zero. A question in that language is one it can answer, given enough steps. A product of two values that are not literals, such as a unit price times a quantity, is beyond it: the solver treats the product as an unknown number.

When it then finds values that break a rule, `una` checks them with real multiplication. If they agree, the rule really breaks, and you get U5001 with those values as a counterexample. If every case the solver found needs a product that real arithmetic does not give, the values are no run of the program, and you get U5002.

#### A product the solver cannot read

An invoice line costs its unit price times its quantity, and both are at least 0. Written as one expression, the solver cannot prove that the cost is not negative:

```diff include="steps/19-products..steps/20-unknown:src/invoice.una" context="1" title="src/invoice.una"
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

```text include="steps/20-unknown/expected/rendered.txt#L1"
[U5002] Error: refinement `result >= 0` could not be proven (the refutation depends on a product, quotient or remainder of two values, which the encoding of `spec/12 §2` leaves uninterpreted)
```

Read the message in two parts. The first is the obligation: the refinement `result >= 0`, the result entering `Cents`, "could not be proven". The part in parentheses is the reason: the only refutation the solver found "depends on a product, quotient or remainder of two values". It names the section of the specification that defines what the solver decides ([Reference](#reference) links it). There is no counterexample, because the solver found no real one.

#### Giving the solver the fact: bind and guard

The version before the change, on the `-` side of the diff, is the repair. It names the product with `let`, then guards it with `if`: `if total < 0 then 0 else total`. The solver still cannot tell that `total` is not negative, but it does not need to: in the `else` branch, `total < 0` is false, so the value returned there is at least 0, and the other branch returns 0. The guard handles a case that cannot happen, and costs one comparison when the program runs. [Section 8.3](/learn/choices/#s8-3) shows more of what a branch proves.

### Check yourself: obligations

Here is the whole invoice step, with the guard:

```una include="steps/19-products/src/invoice.una" title="steps/19-products/src/invoice.una" verified="check, run"
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

How many obligations does `una obligations .` list for it, and of which kinds?

:::answer Show the answer
Six: two postconditions and four refinements.

```text include="steps/19-products/expected/commands/obligations.txt"
$ una obligations .
proven   ob-00d161d86eb3 postcondition src/invoice.una:14:11 result >= 0
proven   ob-a14e2a20a58d postcondition src/invoice.una:15:11 result * 100 <= total
proven   ob-d6433d56c573 refinement    src/invoice.una:21:1 result >= 0
proven   ob-200f35c3fccb refinement    src/invoice.una:29:47 14900 >= 0
proven   ob-b453dd62cb76 refinement    src/invoice.una:29:64 2 in 1..99
proven   ob-f82fc95c6633 refinement    src/invoice.una:31:42 total >= 0
```

The postconditions are the two `ensures` of `points`. The refinements are the result of `line_total` entering `Cents`, the two refined fields of the `Line` that `main` builds, and `total` entering `points`, whose parameter is `Cents`. The product in `line_total` raises none of its own: the guard is what lets the refinement be proven. `points` divides by the literal 100, so there is no division obligation.
:::

A second one. Is this function proven, refuted (U5001) or unknown (U5002)?

```una include="steps/21-shelf-area/src/shelves.una#area" title="steps/21-shelf-area/src/shelves.una"
--- The floor area of a shelf, in square centimeters.
area(width: Int in 1..100, depth: Int in 1..100) -> Int
  ensures result >= 1
=
  width * depth
```

:::answer Show the answer
Unknown:

```text include="steps/21-shelf-area/expected/rendered.txt#L1"
[U5002] Error: postcondition of `area` could not be proven (the refutation depends on a product, quotient or remainder of two values, which the encoding of `spec/12 §2` leaves uninterpreted)
```

`width * depth` is a product of two values, so the solver treats it as an unknown number, and every value that would break `result >= 1` needs a product that real arithmetic does not give. The rule holds, since both factors are at least 1, but the proof is missing. Bind the product and guard it, as `line_total` does.
:::

## 5.5 Requirements: rules from outside the code

### What a requirement is

A **requirement** records a rule that comes from outside the code, in the words of its source, with the team that answers for it. The store's billing policy says "a refund never pays back more than the customer paid". In Una that sentence becomes a `requirement` declaration, and a function whose contract implements it says so with a `derived from` clause.

Think of a store's procedures binder, where each rule has a number, so that a note on a till can say "see rule 4.2". A requirement gives a rule that number, and `derived from` is the note.

### Why tie a contract to its rule

A contract says what the code does: `ensures result <= paid`. It does not say why. When the billing policy changes, someone must find every function that implements the old rule, and when an auditor asks how the store follows a regulation, someone must show the code that does. Comments drift, and a search for words misses the function that phrases the rule differently. A requirement makes the link part of the program: `una` checks it, and `una trace` follows it from the rule to the proof.

### How to write a requirement

#### The declaration

A requirement is a top-level declaration, like a function or a kind: the word `requirement`, an identifier, and four lines, all required, each indented two spaces:

```una include="steps/22-requirements/src/refunds.una#L3-L7" title="steps/22-requirements/src/refunds.una"
requirement REFUND_1
  text "A refund never pays back more than the customer paid"
  source policy "Store billing rules"
  owner billing
  status active
```

| Line | Says |
| --- | --- |
| `requirement REFUND_1` | The identifier: capital letters, digits and `_`, ending with `_` and a number |
| `text "…"` | The rule, in the words of its source, in quotes |
| `source policy "Store billing rules"` | Where the rule comes from, in one of the four forms below |
| `owner billing` | The team that answers for it, in small letters joined by `_` |
| `status active` | `active` for a rule in force, `proposed` for one that waits for a person to accept it |

The number at the end of the identifier lets you add `REFUND_2` next to `REFUND_1` without renaming anything.

#### The sources

`source` takes one of four forms. The step declares one of each:

```una include="steps/22-requirements/src/refunds.una#L9-L25" title="steps/22-requirements/src/refunds.una"
requirement REFUND_2
  text "A refund above 500.00 needs a second look"
  source human
  owner support
  status active

requirement TAX_1
  text "A refund returns the tax that was charged with it"
  source regulation "Consumer tax code, part 4"
  owner finance
  status active

requirement REFUND_3
  text "A refund is never negative"
  source generated "billing review"
  owner billing
  status proposed
```

- **`policy "Store billing rules"`.** A document of the business, by name.
- **`human`.** A person stated the rule, with no document behind it.
- **`regulation "Consumer tax code, part 4"`.** A law or a regulation, by name.
- **`generated "billing review"`.** A tool or an agent proposed the rule, during the task named in quotes. Such a requirement must stay `proposed`: only a person can make it `active`, by changing its source to `human`, `policy` or `regulation`.

#### `derived from` on a function

A function that implements a rule names it in a `derived from` clause, the last of its clauses, after `requires` and `ensures`. It may name several requirements, separated by commas:

```una include="steps/22-requirements/src/refunds.una#refund..needs_review" title="steps/22-requirements/src/refunds.una"
--- What a refund pays back: what was asked, which is never more than what was paid.
refund(paid: Cents, asked: Cents) -> Cents
  requires asked <= paid
  ensures result <= paid
  derived from REFUND_1, REFUND_3
=
  asked

--- Whether a refund needs a second look by a person.
needs_review(asked: Cents) -> Bool
  ensures result == (asked > 50000)
  derived from REFUND_2
=
  asked > 50000
```

`una run .` prints:

```text include="steps/22-requirements/expected/output.txt"
refund 3980, needs review: true
```

### Following a rule to its proof

`una trace` takes a requirement's identifier and lists every function derived from it, with its contract and the status of each obligation:

```text include="steps/22-requirements/expected/commands/trace.txt"
$ una trace REFUND_1
requirement REFUND_1 (active)
  text "A refund never pays back more than the customer paid"
  source policy "Store billing rules"
  owner billing
refunds.refund
  requires asked <= paid
  ensures result <= paid
  proven   ob-0b48412701fd refinement    result >= 0
  proven   ob-0ac4aeb885fd postcondition result <= paid
```

Read it from the top: the requirement, its status, its text, source and owner; then `refunds.refund`, the function that implements it, by module and name; its `requires` and `ensures`; and the obligations of the function, both proven. A person who answers for the refund policy can read this instead of the code.

`una report .`, the build report of [section 18.4](/learn/tools/#s18-4), lists every requirement of the package with the functions derived from it, under `requirements`:

```text include="steps/22-requirements/expected/commands/report.txt#L29-L33"
requirements:
  REFUND_1 (active): refunds.refund
  REFUND_2 (active): refunds.needs_review
  REFUND_3 (proposed): refunds.refund
  TAX_1 (active): 
```

`REFUND_3` is marked `(proposed)`, so a reader sees that `refund` follows a rule nobody has accepted yet; a function derived from a proposed requirement still checks. `TAX_1` has nothing after its colon: no function implements it yet, which the report shows at once.

### How requirements are checked

#### A generated rule stays proposed

Make the generated requirement `active`:

```diff include="steps/22-requirements..steps/23-generated-active:src/refunds.una" context="1" title="src/refunds.una"
--- a/src/refunds.una
+++ b/src/refunds.una
@@ -24,3 +24,3 @@
   owner billing
-  status proposed
+  status active
 
```

```text include="steps/23-generated-active/expected/rendered.txt#L1"
[U1007] Error: requirement `REFUND_3` has source `generated`, so its status must be `proposed`
```

U1007 points at the status. A tool may propose a rule, but only a person may put it in force, and the change of source that does so shows when the code is reviewed.

#### Every name in `derived from` exists

A `derived from` that names a requirement the package does not declare, such as a typing slip, is U1006:

```diff include="steps/22-requirements..steps/24-unknown-requirement:src/refunds.una" context="1" title="src/refunds.una"
--- a/src/refunds.una
+++ b/src/refunds.una
@@ -40,3 +40,3 @@
   ensures result == (asked > 50000)
-  derived from REFUND_2
+  derived from REFUND_4
 =
```

```text include="steps/24-unknown-requirement/expected/rendered.txt#L1"
[U1006] Error: requirement `REFUND_4` is not declared in this package
```

#### One identifier, one requirement

Two requirements with the same identifier in one package are U1002, as two declarations with one name are anywhere ([section 1.2](/learn/hello/#s1-2)).

### Where each rule belongs

:::decide
**Which to use:**

| The rule… | Use |
| --- | --- |
| Holds of every value of a type | a refined kind ([section 5.3](#s5-3)) |
| Is the caller's to keep | `requires` |
| Is what a function promises about its result | `ensures` |
| Comes from a policy, a regulation or a person | a `requirement`, and `derived from` on the functions that implement it |
| Explains what a function is for | a doc comment (`---`) |
:::

A requirement does not replace a contract: it names the reason for one. The contract is what the verifier proves, and the requirement is what a person reads to know why.

### Check yourself: requirements

Which of these requirement identifiers check: `RETURNS_1`, `GIFT_CARD_12`, `RETURNS`, and `REFUND_REVIEW`?

:::answer Show the answer
`RETURNS_1` and `GIFT_CARD_12` check: capital letters joined by `_`, ending with `_` and a number. `RETURNS` and `REFUND_REVIEW` do not end with a number. For `REFUND_REVIEW`, `una check .` reports:

```text include="steps/25-requirement-name/expected/rendered.txt#L1"
[U1005] Error: requirement identifier `REFUND_REVIEW` must be upper snake case ending with `_` and a number, as in `REFUND_REVIEW_1`
```

The `Help` line of the full diagnostic renames it to `REFUND_REVIEW_1`, here and in every `derived from` that names it.
:::

A tool adds a requirement with `source generated "pricing review"` and `status proposed`. A person reads it, and the store adopts the rule in its pricing policy. What changes in the declaration?

:::answer Show the answer
Two lines. The source becomes `policy "…"`, with the name of the pricing policy, and then the status may become `active`. Changing only the status is U1007, since a generated requirement must stay proposed, as [A generated rule stays proposed](#a-generated-rule-stays-proposed) shows.
:::

## 5.6 Day-to-day: billing

### What the billing step must do

Now the program from the start of the chapter. The store's billing step receives the lines of an invoice and a coupon. It prices the lines, takes the coupon off, splits the total between the customer's store credit and a card, and checks each refund the customer asks for against what was paid. Each rule of the business becomes one of the tools of this chapter:

| Rule | How the program states it |
| --- | --- |
| Money is never negative | the refined kind `Cents` ([section 5.3](#s5-3)) |
| A rate is between 0 and 100, a line orders 1 to 99 units | the refined kind `Percent`, and a range on a field |
| A coupon never takes off more than the invoice is worth | `ensures result <= amount` on `discount` ([section 5.2](#s5-2)) |
| Store credit pays first, and the two parts add up to the total | two `ensures` on `pay` |
| A refund never pays back more than was paid | `requires asked <= paid` on `refund` ([section 5.1](#s5-1)), and a guard in its caller |
| Where the two money rules come from | two requirements ([section 5.5](#s5-5)) |

The verifier proves them all before the program runs. The invoice of this chapter has two lines; an invoice of any number of lines needs a list, which [section 10.1](/learn/collections/#s10-1) teaches. The parts below build the module in order, one declaration or a few at a time.

### The rules and the kinds

The module opens with two requirements, which name the store's rules in the words of its billing policy, and the kinds, which carry the facts that hold of every value:

```una include="day-to-day/src/billing.una#BILLING_1..Payment" title="day-to-day/src/billing.una" caption="the rules and the kinds"
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
```

- **`BILLING_1` and `BILLING_2`.** Two rules of a policy document, owned by the billing team, both in force. The functions that implement them say so with `derived from`.
- **`Cents` and `Percent`.** Every amount in the module is a `Cents`, so no amount is ever negative, and every rate is a `Percent`.
- **`Line`.** A record whose fields carry their rules: a price in `Cents`, and a quantity from 1 to 99, refined in place.
- **`Coupon`.** A sum kind with three variants. Its fields are refined, so a `PercentOff(rate: 110)` does not check.
- **`Payment`.** The result of paying, with both parts in `Cents`.

### Pricing the lines

`line_total` multiplies a price by a quantity: a product of two values, which the solver cannot read, so it binds the product and guards it, as [Giving the solver the fact](#giving-the-solver-the-fact-bind-and-guard) shows. `subtotal` adds the two lines. The sum of two `Cents` is never negative, a fact the solver reads at once, so `subtotal` needs no guard:

```una include="day-to-day/src/billing.una#line_total..subtotal" title="day-to-day/src/billing.una"
--- What one line costs. The guard handles a case that cannot happen, since both factors
--- are at least 0; the solver cannot see that for itself.
pub line_total(line: Line) -> Cents
=
  let total = line.unit_cents * line.quantity
  if total < 0 then 0 else total

--- The sum of an invoice of two lines.
pub subtotal(first: Line, second: Line) -> Cents = line_total(first) + line_total(second)
```

### The coupon

`discount` promises that it never takes off more than the amount. Each arm of its `when` ([section 4.3](/learn/kinds/#s4-3)) keeps the promise: no coupon takes 0, a percentage takes part of the amount, and a coupon worth more than the amount takes all of it and no more. `percent_of` multiplies two values, so it has the guard too, and its own `ensures` gives `discount` the fact it needs about that arm:

```una include="day-to-day/src/billing.una#percent_of..discount" title="day-to-day/src/billing.una"
--- `rate` percent of `amount`, rounded down. The guard cannot fire: both factors are at
--- least 0, and `rate` is at most 100.
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

`pay` splits a total between store credit and card. Its two clauses are the whole rule: the two parts add up to the total, and the credit used is never more than the customer has. The verifier proves both on both branches, and also that `total - credit` is a `Cents` where `credit < total`:

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

`refund` requires that the customer asks for no more than was paid. Its body only returns what was asked, and its `ensures` follows from its `requires`. The rule lives in the header, where every caller must meet it:

```una include="day-to-day/src/billing.una#refund" title="day-to-day/src/billing.una"
--- What a refund pays back: what was asked, which may not be more than what was paid.
pub refund(paid: Cents, asked: Cents) -> Cents
  requires asked <= paid
  ensures result <= paid
  derived from BILLING_2
=
  asked
```

`line_text` writes one line of the invoice. `refund_line` is a caller of `refund`. It writes one line of the refund report, and it guards the call: when the customer asks for more than was paid, it says so, and it calls `refund` only in the `else` branch, where `asked > paid` is false, so `asked <= paid` holds. `money` writes an amount for a person to read, and divides and takes the remainder by the literal 100 only, so it has no division obligation at all:

```una include="day-to-day/src/billing.una#money..refund_line" title="day-to-day/src/billing.una"
--- An amount for a person to read, such as 19.90.
pub money(cents: Cents) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"

--- One line of the invoice as it is printed.
pub line_text(line: Line) -> Text = "{line.quantity} x {line.sku} at {money(line.unit_cents)}: {money(line_total(line))}"

--- One line of the refund report: the refund, or why it is refused.
pub refund_line(paid: Cents, asked: Cents) -> Text
=
  if asked > paid
    "refund {money(asked)}: refused, only {money(paid)} was paid"
  else
    let back = refund(paid, asked: asked)
    "refund {money(back)}: paid back"
```

The contracts leave some things open on purpose. `discount` does not say how a percentage is rounded, and `refund_line` does not promise its exact words. Those are choices of the business, not rules of safety, and the examples in [section 5.7](#s5-7) pin them down. A contract states what must never break, and an example states what the answer is for one case.

### Running it

`main` prices two lines, applies a 10% coupon, pays with 50.00 of store credit, and checks two refunds:

```una include="day-to-day/src/billing.una#main" title="day-to-day/src/billing.una" verified="check, run"
--- Prices an invoice of two lines, pays it, and checks two refunds.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Line(sku: "LAMP-01", unit_cents: 1990, quantity: 2)
  let desk = Line(sku: "DESK-02", unit_cents: 14900, quantity: 1)
  @console.print(line_text(lamp))
  @console.print(line_text(desk))
  let gross = subtotal(lamp, second: desk)
  let off = discount(gross, coupon: PercentOff(rate: 10))
  let total: Cents = gross - off
  let payment = pay(total, credit: 5000)
  @console.print("subtotal {money(gross)}, coupon -{money(off)}, total {money(total)}")
  @console.print("store credit {money(payment.credit)}, card {money(payment.card)}")
  @console.print(refund_line(total, asked: 3980))
  @console.print(refund_line(total, asked: 20000))
```

Look at `let total: Cents = gross - off`. Subtracting two `Cents` can give a negative number, so the verifier must prove `gross - off >= 0`. It can, but only because `discount` promises `off <= gross`. Remove that `ensures`, and this line no longer checks, as [a caller that needs a promise the callee does not make](#a-caller-that-needs-a-promise-the-callee-does-not-make-u5001) shows. Contracts compose this way: each function's promise is the next function's fact.

In the `day-to-day` directory, `una run .` prints:

```text include="day-to-day/expected/output.txt"
2 x LAMP-01 at 19.90: 39.80
1 x DESK-02 at 149.00: 149.00
subtotal 188.80, coupon -18.88, total 169.92
store credit 50.00, card 119.92
refund 39.80: paid back
refund 200.00: refused, only 169.92 was paid
```

The second refund asks for 200.00 of an invoice of 169.92, so `refund_line` refuses it and never calls `refund`.

### Tracing a rule to its proof

As in [Following a rule to its proof](#following-a-rule-to-its-proof), `una trace BILLING_2` lists the function derived from the refund rule, its contract, and the proof of each obligation:

```text include="day-to-day/expected/commands/trace.txt"
$ una trace BILLING_2
requirement BILLING_2 (active)
  text "A refund never pays back more than the customer paid"
  source policy "Store billing rules"
  owner billing
billing.refund
  requires asked <= paid
  ensures result <= paid
  proven   ob-204eda00affc refinement    result >= 0
  proven   ob-ef9bbe64fc88 postcondition result <= paid
```

A person who answers for the refund policy can read this instead of the code: the rule, the function that implements it, the clauses of its header, and the proof. `una trace BILLING_1` lists `discount` and `pay` the same way.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/billing.una" title="day-to-day/src/billing.una" caption="the whole program" verified="check, run, test"
module billing

-- The billing step of a store: it prices an invoice, takes a coupon off, splits the payment
-- between store credit and card, and checks each refund against what was paid.

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

--- What one line costs. The guard handles a case that cannot happen, since both factors
--- are at least 0; the solver cannot see that for itself.
pub line_total(line: Line) -> Cents
=
  let total = line.unit_cents * line.quantity
  if total < 0 then 0 else total

--- The sum of an invoice of two lines.
pub subtotal(first: Line, second: Line) -> Cents = line_total(first) + line_total(second)

--- `rate` percent of `amount`, rounded down. The guard cannot fire: both factors are at
--- least 0, and `rate` is at most 100.
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

--- What a refund pays back: what was asked, which may not be more than what was paid.
pub refund(paid: Cents, asked: Cents) -> Cents
  requires asked <= paid
  ensures result <= paid
  derived from BILLING_2
=
  asked

--- An amount for a person to read, such as 19.90.
pub money(cents: Cents) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"

--- One line of the invoice as it is printed.
pub line_text(line: Line) -> Text = "{line.quantity} x {line.sku} at {money(line.unit_cents)}: {money(line_total(line))}"

--- One line of the refund report: the refund, or why it is refused.
pub refund_line(paid: Cents, asked: Cents) -> Text
=
  if asked > paid
    "refund {money(asked)}: refused, only {money(paid)} was paid"
  else
    let back = refund(paid, asked: asked)
    "refund {money(back)}: paid back"

--- Prices an invoice of two lines, pays it, and checks two refunds.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Line(sku: "LAMP-01", unit_cents: 1990, quantity: 2)
  let desk = Line(sku: "DESK-02", unit_cents: 14900, quantity: 1)
  @console.print(line_text(lamp))
  @console.print(line_text(desk))
  let gross = subtotal(lamp, second: desk)
  let off = discount(gross, coupon: PercentOff(rate: 10))
  let total: Cents = gross - off
  let payment = pay(total, credit: 5000)
  @console.print("subtotal {money(gross)}, coupon -{money(off)}, total {money(total)}")
  @console.print("store credit {money(payment.credit)}, card {money(payment.card)}")
  @console.print(refund_line(total, asked: 3980))
  @console.print(refund_line(total, asked: 20000))

example "two lines add up"
  do subtotal(Line(sku: "LAMP-01", unit_cents: 1990, quantity: 2), second: Line(sku: "DESK-02", unit_cents: 14900, quantity: 1))
  expect result == 18880

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

example "a refund within what was paid pays back what was asked"
  do refund(16992, asked: 3980)
  expect result == 3980

example "a refund of more than was paid is refused"
  do refund_line(16992, asked: 20000)
  expect result == "refund 200.00: refused, only 169.92 was paid"

example "an amount below 10 cents keeps its zero"
  do money(1905)
  expect result == "19.05"
```

## 5.7 Testing it

### What the examples pin down

A proof covers every input, so why write examples? Because a contract states only what you wrote in it. `discount` promises `result <= amount`, and a body that always returns 0 keeps that promise too. The examples pin down the values the business expects: 10% of 188.85 is 18.88, rounded down; credit pays before the card; a refund of more than was paid is refused, in these words.

```una include="day-to-day/src/billing.una#L117-L148" title="day-to-day/src/billing.una" caption="the examples"
example "two lines add up"
  do subtotal(Line(sku: "LAMP-01", unit_cents: 1990, quantity: 2), second: Line(sku: "DESK-02", unit_cents: 14900, quantity: 1))
  expect result == 18880

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

example "a refund within what was paid pays back what was asked"
  do refund(16992, asked: 3980)
  expect result == 3980

example "a refund of more than was paid is refused"
  do refund_line(16992, asked: 20000)
  expect result == "refund 200.00: refused, only 169.92 was paid"

example "an amount below 10 cents keeps its zero"
  do money(1905)
  expect result == "19.05"
```

Each example is written as in [chapter 1](/learn/hello/#s1-7): `do` makes one call, and `expect` states what must hold of `result`. An example may have several `expect` lines, as "store credit pays first" does, and every one must hold. [Chapter 14](/learn/testing/#s14-1) covers examples in full.

### Examples are checked like code

The examples are verified like the rest of the code: a `do` line that calls `pay` with `credit: -5`, or `discount` with a rate of 110, does not check, since the argument does not fit its kind. An example cannot test a case that the contracts rule out, and it needs no such test, since the verifier has proven that no code can make that call.

### Examples and proofs together

Two habits make examples and proofs work together:

- **Turn each counterexample into an example**, as in [section 5.2](#s5-2). The case that broke the code once is the case a later change is most likely to break again.
- **Test the exact values; prove the bounds.** A contract states a range or a relation that holds for every input. An example states one exact answer that a person can check by hand.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L11"
example billing "two lines add up" ... ok
example billing "a coupon worth more than the invoice takes the whole invoice" ... ok
example billing "ten percent is rounded down" ... ok
example billing "store credit pays first" ... ok
example billing "credit larger than the total leaves nothing for the card" ... ok
example billing "a refund within what was paid pays back what was asked" ... ok
example billing "a refund of more than was paid is refused" ... ok
example billing "an amount below 10 cents keeps its zero" ... ok

8 examples: 8 passed, 0 failed
```

## 5.8 Common mistakes

Each mistake is a small change to `day-to-day/src/billing.una`, followed by what `una check .` reports. Read each diagnostic the same way: the first line names the obligation and its goal, the marks show the clause that asks and the code that does not deliver, and `Note 2`, when there is one, is the counterexample.

### A coupon that can be worth more than the order (U5001)

:::mistake
In `discount`, return the coupon's value without the cap:

```diff include="day-to-day..mistakes/1:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -63,3 +63,3 @@
     is PercentOff(rate) -> percent_of(amount, rate)
-    is CentsOff(off) -> if off > amount then amount else off
+    is CentsOff(off) -> off
 
```

```text include="mistakes/1/expected/rendered.txt"
[U5001] Error: postcondition of `discount` is refuted
    ╭─[ src/billing.una:64:25 ]
    │
 58 │   ensures result <= amount
    │           ────────┬───────
    │                   ╰───────── ensures clause
    │
 64 │     is CentsOff(off) -> off
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

*Why:* the arm returns the coupon's value whatever the amount, and a coupon can be worth more than a cheap invoice. The marks point at the clause, `ensures result <= amount`, and at the arm's `off`. With `amount = 0` and a `CentsOff` coupon of 1 cent, the result is 1, which breaks `result <= amount`. In a counterexample for a sum kind, `coupon = CentsOff` names the variant, and only that variant's fields mean anything: `coupon.rate` belongs to `PercentOff`, and its value here means nothing.

*Fix:* cap the coupon at the amount, as the day-to-day program does. See [U5001](/docs/errors/U5001/).
:::

### A caller that needs a promise the callee does not make (U5001)

:::mistake
Remove `ensures result <= amount` from `discount`:

```diff include="day-to-day..mistakes/2:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -57,3 +57,2 @@
 pub discount(amount: Cents, coupon: Coupon) -> Cents
-  ensures result <= amount
   derived from BILLING_1
```

```text include="mistakes/2/expected/rendered.txt#L1-L10,L18"
[U5001] Error: refinement `(gross - off) >= 0` is refuted
     ╭─[ src/billing.una:109:22 ]
     │
  19 │ pub kind Cents = Int where it >= 0
     │                            ───┬───
     │                               ╰───── where clause
     │
 109 │   let total: Cents = gross - off
     │                      ─────┬─────
     │                           ╰─────── refinement `(gross - off) >= 0` is refuted
     │ Note 2: counterexample: desk = Line#0, desk.quantity = 1, desk.sku = "DESK-02", desk.unit_cents = 14900, gross = 0, lamp = Line#1, lamp.quantity = 2, lamp.sku = "LAMP-01", lamp.unit_cents = 1990, off = 1, total = -1
```

*Why:* the clause looked unneeded, since `discount` keeps it anyway, but the error is in `main`, not in `discount`. A caller knows a function only by its header, so without the clause `main` cannot prove that `gross - off` is not negative. The counterexample is not a run: `gross` is 0 and `off` is 1, values that the headers of `subtotal` and `discount` now allow. `Line#0` and `Line#1` name the two lines the solver chose; only `gross` and `off` matter.

*Fix:* put the clause back. When a caller needs a fact about a result, the callee's `ensures` is where it goes. See [U5001](/docs/errors/U5001/).
:::

### A comparison the wrong way round (U5001)

:::mistake
In `refund_line`, swap `asked` and `paid` in the guard:

```diff include="day-to-day..mistakes/3:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -93,3 +93,3 @@
 =
-  if asked > paid
+  if paid > asked
     "refund {money(asked)}: refused, only {money(paid)} was paid"
```

```text include="mistakes/3/expected/rendered.txt#L1-L10,L18"
[U5001] Error: precondition `asked <= paid` of this call is refuted
    ╭─[ src/billing.una:97:16 ]
    │
 76 │   requires asked <= paid
    │            ──────┬──────
    │                  ╰──────── requires clause
    │
 97 │     let back = refund(paid, asked: asked)
    │                ─────────────┬────────────
    │                             ╰────────────── precondition `asked <= paid` of this call is refuted
    │ Note 2: counterexample: asked = 1, paid = 0
```

*Why:* the two names read alike, and `paid > asked` looks as plausible as `asked > paid`. The marks point at the `requires` clause of `refund` and at the call in the `else` branch. In that branch `paid > asked` is false, which allows `paid = 0` and `asked = 1`: a refund of 1 cent on an invoice that cost nothing. The precondition catches a swap that a quick review misses.

*Fix:* `if asked > paid`. See [U5001](/docs/errors/U5001/).
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

*Why:* one expression looks simpler, and the rule obviously holds. But the solver treats the product of two values as an unknown number, so it cannot prove the result is not negative. The message ends with the reason, in parentheses. The values the solver found do not agree with real multiplication, so there is no counterexample, and the obligation is unknown, not refuted.

*Fix:* bind the product, then guard it, as in [Giving the solver the fact](#giving-the-solver-the-fact-bind-and-guard). See [U5002](/docs/errors/U5002/).
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

*Why:* the exact result seems the most useful promise to make. But a clause is a question for the solver, written in the language it decides, which multiplies only by a literal. U2014 is reported before any proof is tried, and the mark covers the whole product in the clause.

*Fix:* state what the solver can decide, such as `result >= line.unit_cents`, or leave the exact value to an example. See [U2014](/docs/errors/U2014/).
:::

### A rate above 100 percent (U5001)

:::mistake
Give the coupon a rate of 110:

```diff include="day-to-day..mistakes/6:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -108,3 +108,3 @@
   let gross = subtotal(lamp, second: desk)
-  let off = discount(gross, coupon: PercentOff(rate: 10))
+  let off = discount(gross, coupon: PercentOff(rate: 110))
   let total: Cents = gross - off
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U5001] Error: refinement `110 in 0..100` is refuted
```

*Why:* a rate of 110 is an easy slip of the keyboard. `rate` is a `Percent`, and the marks point at the range of `Percent` and at the literal 110. The goal names no variable, so there is no counterexample: the literal itself is the case.

*Fix:* a rate from 0 to 100. A rate that a person types while the program runs is checked once, where it enters the program, as [section 7.6](/learn/failure/#s7-6) shows. See [U5001](/docs/errors/U5001/).
:::

## 5.9 Exercises

The exercises come with the chapter's download, `05-contracts.tar.gz`. Each starts from `exercises/N/start`: the day-to-day program with the exercise's examples, and a stub, a function to finish, when there is one. `una check .` or `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: it lays the code out in canonical form, for example a body of one expression on the header's line.

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
*Hint:* read the counterexample as a test case: here the body has no calls, so it is one. For an invoice of exactly 50.00, the body charges 4.95, which breaks the second clause. The body needs two cases, so write it as `if <condition> then <one price> else <the other>`, with the condition the clause names. A branch on `total > 5000` is refuted with the same counterexample: 5000 itself must ship free.
:::

Check your answer with `una check .`, then `una test .`, which runs these examples:

```una include="exercises/1/start/src/billing.una#L158-L164" title="exercises/1/start/src/billing.una"
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
@@ -82,3 +82,2 @@
 --- What shipping costs for an invoice of `total` cents: 4.95, and nothing from 50.00.
---- Exercise 1: make the body keep the contract.
 pub shipping(total: Cents) -> Cents
@@ -87,3 +86,3 @@
 =
-  495
+  if total >= 5000 then 0 else 495
 
```
:::
::::

### Exercise 2: a fixed price

::::exercise
A coupon can set the price of a whole invoice, such as "everything for 150.00". Add a variant `FixedPrice(cents: Cents)` to `Coupon`, and an arm for it in `discount`: it takes off the difference when the invoice costs more than the fixed price, and nothing otherwise. The start package ends with these examples, and `una check .` reports U1001, "cannot find name `FixedPrice`", until the variant exists:

```una include="exercises/2/start/src/billing.una#L150-L156" title="exercises/2/start/src/billing.una"
example "a fixed price below the subtotal takes off the difference"
  do discount(18880, coupon: FixedPrice(cents: 15000))
  expect result == 3880

example "a fixed price above the subtotal takes off nothing"
  do discount(1000, coupon: FixedPrice(cents: 1500))
  expect result == 0
```

:::hint
*Hint:* work in three steps. First add `| FixedPrice(cents: Cents)` at the end of `Coupon`, and run `una check .`: it now reports that the `when` of `discount` has no arm for the new variant, as [section 4.3](/learn/kinds/#s4-3) says it must. Then add the arm `is FixedPrice(cents) -> …`. The verifier checks it against the header of `discount`: the result must be a `Cents`, so never negative, and at most `amount`.
:::

The first arm most people write is `amount - cents`. `una check .` refutes it:

```text include="exercises/2/unguarded/expected/rendered.txt#L1,L8,L18"
[U5001] Error: refinement `result >= 0` is refuted
 65 │     is FixedPrice(cents) -> amount - cents
    │ Note 2: counterexample: amount = 0, coupon = FixedPrice, coupon.amount = -1, coupon.cents = 3, coupon.rate = 101, result = -3
```

The counterexample is a fixed price of 0.03 on an invoice of 0: the discount would be −3 cents. Only `coupon.cents` matters here, as in [a coupon that can be worth more than the order](#a-coupon-that-can-be-worth-more-than-the-order-u5001): `coupon.amount = -1` is outside `Cents` because that field belongs to no value here.

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Add the variant, and an arm with a guard:

```diff include="exercises/2/start..exercises/2/answer:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -30,3 +30,3 @@
 --- A coupon on the whole invoice.
-pub kind Coupon = NoCoupon | PercentOff(rate: Percent) | CentsOff(amount: Cents)
+pub kind Coupon = NoCoupon | PercentOff(rate: Percent) | CentsOff(amount: Cents) | FixedPrice(cents: Cents)
 
@@ -64,2 +64,3 @@
     is CentsOff(off) -> if off > amount then amount else off
+    is FixedPrice(cents) -> if cents < amount then amount - cents else 0
 
```
:::
::::

### Exercise 3: a second refund

::::exercise
A customer can ask for a refund in parts. Write `refund_again(paid, already, asked)`, which pays back `asked` when the refunds together stay within what was paid, and pays back nothing, 0, otherwise. The start package has the header, with its contract, and a body that forgets the refunds already made. `una check .` refutes it:

```una include="exercises/3/start/src/billing.una#refund_again" title="exercises/3/start/src/billing.una"
--- A further refund, after `already` was paid back: the refunds together never pay back more
--- than the customer paid, and a refund that would go above `paid` pays back nothing.
--- Exercise 3: refuse what would go above `paid`.
pub refund_again(paid: Cents, already: Cents, asked: Cents) -> Cents
  requires already <= paid
  ensures already + result <= paid
  derived from BILLING_2
=
  if asked > paid then 0 else refund(paid, asked: asked)
```

```text include="exercises/3/start/expected/rendered.txt#L1,L18"
[U5001] Error: postcondition of `refund_again` is refuted
    │ Note 2: counterexample: already = 1, asked = 1, paid = 1, result = 1
```

The counterexample is a real run: a customer paid 0.01, already got 0.01 back, and asks for 0.01 again. `asked` is not more than `paid`, so the body pays it back, and the refunds together come to 0.02.

:::hint
*Hint:* the body may not rely on `refund` alone, since `refund` knows nothing of `already`. Write the test yourself: compare `already + asked` with `paid`, return 0 when it is more, and return `asked` otherwise. In the `else` branch, the verifier then knows `already + asked <= paid`, which is the promise.
:::

Check your answer with `una test .`, which runs these examples:

```una include="exercises/3/start/src/billing.una#L160-L166" title="exercises/3/start/src/billing.una"
example "a second refund cannot pass what is left"
  do refund_again(16992, already: 10000, asked: 8000)
  expect result == 0

example "a second refund within what is left is paid back"
  do refund_again(16992, already: 10000, asked: 6992)
  expect result == 6992
```

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Refuse what would take the refunds above `paid`:

```diff include="exercises/3/start..exercises/3/answer:src/billing.una" context="1" title="src/billing.una"
--- a/src/billing.una
+++ b/src/billing.una
@@ -83,3 +83,2 @@
 --- than the customer paid, and a refund that would go above `paid` pays back nothing.
---- Exercise 3: refuse what would go above `paid`.
 pub refund_again(paid: Cents, already: Cents, asked: Cents) -> Cents
@@ -89,3 +88,3 @@
 =
-  if asked > paid then 0 else refund(paid, asked: asked)
+  if already + asked > paid then 0 else asked
 
```

The function is `derived from BILLING_2`, so `una trace BILLING_2` now lists it next to `refund`, with its proofs:

```text include="exercises/3/answer/expected/commands/trace.txt#L11-L15"
billing.refund_again
  requires already <= paid
  ensures already + result <= paid
  proven   ob-f4387ed6cf13 refinement    result >= 0
  proven   ob-0b04b97219e5 postcondition already + result <= paid
```
:::
::::

## 5.10 Recap and reference

### For agents

:::agents
`una --json check .` gives each obligation that is not proven as a diagnostic with its `obligation` (id, kind, goal, status) and its `counterexample` as name and value pairs. For [a coupon that can be worth more than the order](#a-coupon-that-can-be-worth-more-than-the-order-u5001):

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U5001","severity":"error","domain":"verification","message":"postcondition of `discount` is refuted","primary":{"file":"src/billing.una","start":{"line":64,"col":25},"end":{"line":64,"col":28}},"related":[{"file":"src/billing.una","start":{"line":58,"col":11},"end":{"line":58,"col":27},"message":"ensures clause"}],"obligation":{"id":"ob-e0a2abc0bb6a","kind":"postcondition","goal":"result <= amount","status":"refuted"},"counterexample":{"bindings":[{"name":"amount","value":0},{"name":"coupon","value":"CentsOff"},{"name":"coupon.amount","value":1},{"name":"coupon.rate","value":101},{"name":"result","value":1}]},"repairs":[{"rank":1,"escape_cost":0,"description":"add a guard or an arm so that the failing path returns a value for which `result <= amount` holds","edit":null},{"rank":2,"escape_cost":0,"description":"adjust the `ensures` clause","edit":null}],"explain":"una explain U5001"}],"fixable":0}
```

The repairs of U5001 and U5002 carry no `edit`, since only the author knows whether the code or the contract is wrong, so `una fix` leaves them. `una --json obligations .` and `una --json trace <ID>` list every obligation, proven or not. The compact rule: *every call proves the callee's `requires`, every return proves the `ensures`, every value that enters a refined kind proves its condition, and unknown is an error; clauses multiply and divide only by literals.*
:::

### Recap

:::recap
- `requires` is what a caller must prove; `ensures` is what every return promises. Callers know a function by its header alone.
- A counterexample shows where a contract breaks. Fix the code or the contract, and keep a real case as an example.
- Put a rule that holds of every value on its kind, `Int where it >= 0`, and name a shared rule with a `reflect` predicate.
- Clauses multiply and divide only by literals. For a product of two values, bind it with `let` and guard it.
- `una obligations .` lists every question and its status. U5001 is refuted, U5002 unknown; both are errors.
- Record business rules as requirements, tie functions to them with `derived from`, and follow them with `una trace`.
:::

### Reference

:::reference
- Construct pages: [`requires`](/docs/language/functions/requires/), [`ensures`](/docs/language/functions/ensures/), [`where` and refinements](/docs/language/types/where/), [`predicate`](/docs/language/types/predicate/), [`kind`](/docs/language/types/kind/), [`requirement`](/docs/language/requirements/requirement/), [`example`](/docs/language/examples/example/), [verification](/docs/language/verification/)
- Prelude: [`Nat`, `min`](/docs/std/)
- Commands: [`una check`](/docs/cli/check/), [`una obligations`](/docs/cli/obligations/), [`una trace`](/docs/cli/trace/), [`una report`](/docs/cli/report/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/) (a name declared twice), [U1005](/docs/errors/U1005/) (a requirement identifier of the wrong form), [U1006](/docs/errors/U1006/), [U1007](/docs/errors/U1007/), [U2002](/docs/errors/U2002/), [U2012](/docs/errors/U2012/) (`result` outside `ensures`), [U2014](/docs/errors/U2014/), [U2015](/docs/errors/U2015/) (a predicate body that is not allowed), [U5001](/docs/errors/U5001/), [U5002](/docs/errors/U5002/), [U5003](/docs/errors/U5003/) (the solver is missing or not the pinned version)
- Specification: [functions and contracts](/docs/spec/04-functions-and-contracts/), [types](/docs/spec/03-types/), [verification](/docs/spec/12-verification/), [requirements and examples](/docs/spec/08-requirements-and-examples/)
:::
