---
learn: "7"
title: Contracts and the verifier
editions: ["0.2"]
codes: [U1001, U2014, U5001, U5002]
time: 40
builds: The billing step of a store, which prices an invoice, applies a coupon, splits the payment and refunds
prerequisites: ["3", "4", "5", "6"]
template: 2
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

A precondition states what must hold of the arguments for a call to make sense. `requires count >= 1` on a function that divides by `count` says that a call with 0 is a mistake of the caller.

A precondition is checked at both ends:

- **At every call,** the verifier proves the precondition for the arguments given. A call it cannot prove does not check.
- **In the body,** the precondition is a fact the verifier assumes. Here it proves that the division never divides by zero.

Each step of this chapter is a package, as in [chapter 1, Hello, Una](/learn/hello/package/): a directory with `una.toml`, `verification.lock` and the module under `src/`. The manifest names the package and the module that `una run` starts:

```toml include="steps/01-requires/una.toml" title="steps/01-requires/una.toml"
[package]
name = "installments"
version = "0.1.0"
edition = "0.2"

[run]
entry = "installments"
grants = ["console"]
```

`verification.lock` pins the solver and is the same in every example: copy it from chapter 1, or download the step's package from this page. Then, in the package's directory:

```sh
una check .
una run .
```

:::steps
```una include="steps/01-requires/src/installments.una" title="steps/01-requires/src/installments.una" verified="check, run"
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

```text include="steps/01-requires/expected/output.txt"
4000 a month for 3 months
12000 now, or 3000 a month for 4 months
```

Remove the guard from `monthly` and call `installment` directly. `una check .` now refutes the call, and says why:

```diff include="steps/01-requires..steps/02-unguarded:src/installments.una" context="1" title="src/installments.una"
--- a/src/installments.una
+++ b/src/installments.una
@@ -10,3 +10,3 @@
 --- paying everything now.
-monthly(total: Int, months: Int) -> Int = if months < 1 then total else installment(total, count: months)
+monthly(total: Int, months: Int) -> Int = installment(total, count: months)
 
```

```text include="steps/02-unguarded/expected/rendered.txt"
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

:::decide
**Which to use:**

| The bad value… | Use |
| --- | --- |
| Is a mistake of the caller, which can always avoid it | `requires`: every caller proves it |
| Can come from a person or another system | A guard or a failure in the function that receives it ([section 7.5](#s7-5)) |
| Is impossible by the type already | Nothing: a refined kind ([section 7.3](#s7-3)) carries the fact |
:::

## 7.2 Postconditions: `ensures` and counterexamples

A postcondition states what holds of the result when the function returns. Inside the clause, `result` names the value returned. The verifier proves the clause on every path that returns, and every caller may then assume it without reading the body.

A coupon is a good first case. It takes some cents off a price, and two rules hold whatever the coupon: the price never becomes negative, and it never goes up.

:::steps
```una include="steps/03-ensures/src/coupons.una" title="steps/03-ensures/src/coupons.una" verified="check, run, test"
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
4. **The example.** It pins down the case where the coupon is worth more than the price. The next paragraphs show where it comes from.
:::

`una run .` prints:

```text include="steps/03-ensures/expected/output.txt"
1490 0
3010 0
```

### Reading a counterexample

Now write the body most people write first, `price - off`, and check:

```diff include="steps/03-ensures..steps/04-counterexample:src/coupons.una" context="1" title="src/coupons.una"
--- a/src/coupons.una
+++ b/src/coupons.una
@@ -11,3 +11,3 @@
 =
-  if off > price then 0 else price - off
+  price - off
 
```

```text include="steps/04-counterexample/expected/rendered.txt"
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

A counterexample gives values of the parameters, and of `result`, for which the contract breaks. When the body has no calls, as here, it is a case you can run by hand. When the body calls other functions, the verifier knows each call only by the callee's header, so a call's result in the counterexample can be any value that header allows, even one the callee never returns. Then the values are not a run, but they still point at the problem: the body relies on something the callee does not promise ([section 7.8](#s7-8), mistake 2), or it does not handle an input it should ([section 7.10](#s7-10), exercise 3).

The solver often picks the smallest numbers that break the rule, such as 0 and 1, so a case that looks artificial usually stands for a real one: here, any coupon worth more than its order.

Two things to do with a counterexample:

1. **Fix the code or the contract.** Here the code is wrong: a coupon larger than the price gives 0. Sometimes the contract promises more than you meant.
2. **Keep the case as an example,** when it is a run, as this one is. The example in `coupons.una` is this counterexample, written as a test. The proof already covers it, but the example documents the case for a reader and shows it in `una test .`:

```text include="steps/03-ensures/expected/commands/test.txt#L2-L4"
example coupons "a coupon worth more than the price gives 0" ... ok

1 example: 1 passed, 0 failed
```

> [!NOTE]
> `ensures` describes normal returns only. A function that fails, with `fail`, returns no value, and its postcondition says nothing about that path. Contracts also do not prove that a function ends: they hold *if* it returns.

## 7.3 Refined kinds and predicates

A rule that holds of every value of a kind belongs on the kind. A refined kind is a base type with a condition: `kind Cents = Int where it >= 0` is the integers that are not negative, and `it` stands for the value. `Int in 1..99` is short for `Int where 1 <= it and it <= 99`, and `in 0..<100` would leave out 100.

The verifier proves the condition at every place a value enters the kind: an argument, a returned value, a field of a record, and a `let` with the kind written. The other way needs no proof: a `Cents` goes wherever an `Int` goes.

:::steps
```una include="steps/05-refined/src/cart.una" title="steps/05-refined/src/cart.una" verified="check, run"
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
5. **`if line.quantity < 99`.** `line.quantity + 1` enters `Quantity` again. Without the guard, the verifier refutes it with a line of 99 units.
:::

`una run .` prints:

```text include="steps/05-refined/expected/output.txt"
3 x LAMP-01
shipping 495, then 0
```

A refinement of a refined kind adds its condition to the first: `kind Small = Cents where it < 100` is both `>= 0` and `< 100`. The prelude already has one: `Nat`, the integers that are not negative.

> [!IMPORTANT]
> A refined kind cannot be a type argument: `List[Cents]` and `Option[Quantity]` are ill-formed (U2002). Put the refinement on a field of a record, as `Line` does with `quantity`, and use a list of the records.

The condition of a refinement, and every `requires` and `ensures` clause, is written in the **refinement language**, the part of Una the solver decides: integer, boolean and text literals, parameters, `result`, `it`, fields, `.len`, `+`, `-` and unary `-`, `*` when one side is a literal, `/` and `mod` by a literal that is not zero, comparisons, `in`, `is`, `and`, `or`, `not`, `implies`, and calls of predicates. Anything else in a clause, such as the product of two parameters, is U2014 ([section 7.8](#s7-8), mistake 5).

A predicate can also be `opaque`: the verifier sees only its name. In code, a value gets its fact from `checked` at run time, or from the `ensures` of a capability operation ([chapter 8, Capabilities](/learn/capabilities/)). [Chapter 6](/learn/failure/#s6-4) uses one for the format of a SKU.

## 7.4 What the verifier proves

Every contract, refinement and division becomes one or more **obligations**: a question for the solver, with an answer. `una obligations .` lists them all, each with its status, its identity, its kind, where it is, and its goal. For the cart of [section 7.3](#s7-3), where the first line is `shipping`'s result entering `Cents`, its declared type:

```text include="steps/05-refined/expected/commands/obligations.txt"
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

The kinds you meet most:

| Kind | Where | The goal |
| --- | --- | --- |
| `precondition` | Every call of a function with `requires` | The callee's `requires`, for the arguments given |
| `postcondition` | Every path that returns | The function's `ensures` |
| `refinement` | Every place a value enters a refined kind | The kind's condition, for that value |
| `division` | Every `/` and `mod` by a value that is not a literal | The divisor is not zero |
| `exhaustive` | A `when` with literal or range arms and no `else` | Some arm matches |
| `overflow` | Arithmetic on a fixed-width integer, such as `U8` | The exact result fits the type |

Each obligation has one of three statuses:

- **proven:** the goal holds for every input.
- **refuted:** U5001, with a counterexample.
- **unknown:** U5002, with the reason. This is an error too.

The identity, such as `ob-2a5905c8f53d`, comes from the module, the function, the kind and the goal, so a reviewer can follow an obligation across commits. The same goal twice in one function shares one identity.

### When the solver cannot decide: U5002

The solver decides linear arithmetic: sums, differences, products where one side is a literal, and quotients and remainders by a literal that is not zero. A product of two values that are not literals, such as a unit price times a quantity, is beyond it: the solver treats it as an unknown number. When the solver then finds values that break a rule, una checks them with real multiplication. If they agree, the rule really breaks, and you get U5001 with those values as a counterexample. If every case the solver found needs a product that real arithmetic does not give, you get U5002. Here the solver cannot prove that the price of a line is not negative, even though it obviously is:

```diff include="steps/06-products..steps/07-unknown:src/invoice.una" context="1" title="src/invoice.una"
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

```text include="steps/07-unknown/expected/rendered.txt#L1"
[U5002] Error: refinement `result >= 0` could not be proven (the refutation depends on a product, quotient or remainder of two values, which the encoding of `spec/12 §2` leaves uninterpreted)
```

The message names the section of the specification that defines what the solver decides (see Reference).

U5002 is not a claim that the code is wrong: it says that the proof is missing, and una does not pass a program with a missing proof. The first help line proposes a guard:

:::steps
```una include="steps/06-products/src/invoice.una" title="steps/06-products/src/invoice.una" verified="check, run"
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

```text include="steps/06-products/expected/output.txt"
29800 cents, 298 points
```

U5002 also comes from a proof that runs out of the step budget in `verification.lock`; the reason says which. A loop gives U5002 too: it keeps, from one turn to the next, only the refinements of the bindings it updates. `let edit total: Cents = 0` keeps `total >= 0`, which is all the day-to-day program needs. For any other fact the reason says what to do: state what one iteration does as the `ensures` of a helper with an `edit` parameter ([chapter 12, Memory and concurrency](/learn/memory-and-concurrency/)).

> [!TIP]
> Prefer a guard to `checked` when you can show from the kinds that the guard never fires. A guard needs no error variant and no budget, and the verifier proves the code around it. Use `checked` when you cannot show it, or for a rule that only a test at run time can decide: it fails at run time instead of answering quietly.

## 7.5 Contracts at the boundary

Contracts are checked where code meets code. At each call, the caller proves the callee's `requires` and gets its `ensures` in return. A refined kind is a boundary too: the value is checked once, where it enters the kind, and every function after that may rely on it.

That leaves data from outside the program: text typed by a person, a line of a file, a field of a request. No proof can say what a person will type. Check it once, where it enters, and give it a refined kind there:

:::steps
```una include="steps/08-boundary/src/rates.una" title="steps/08-boundary/src/rates.una" verified="check, run"
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

```text include="steps/08-boundary/expected/output.txt"
15% off: the customer pays 85%
150 is not between 0 and 100
'ten' is not a number
```

> [!SECURITY]
> A refined kind turns "every function must remember to check the rate" into "one function checks it, and the checker refuses every other way in". A new function that takes a `Percent` cannot receive 150, whoever calls it.

Some rules come from outside the code too: a billing policy, a regulation, a promise to customers. A `requirement` records such a rule with its source and owner, and `derived from` ties a function's contract to it. `una trace` lists the functions derived from a requirement, with their proofs, and `una report .` lists a package's requirements.

## 7.6 Day-to-day: billing

Now the program from the start of the chapter. The store's billing step receives the lines of an invoice and a coupon. It must never charge a negative amount, never take off more than the invoice is worth, pay from store credit first, and never refund more than the customer paid. Each of these rules becomes a contract or a kind, and the verifier proves them all.

**The rules and the kinds.** Two requirements name the store's rules. The kinds carry the facts that hold of every value: money is never negative, a rate is between 0 and 100, a line orders 1 to 99 units.

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

**Pricing the lines.** `line_total` multiplies, with the guard from [section 7.4](#s7-4). `subtotal` sums with a loop. `total` is declared `Cents`, so every assignment to it proves the sum not negative, which holds since both sides are `Cents`.

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

**The coupon.** `discount` promises that it never takes off more than the amount. Each arm keeps the promise: no coupon takes 0, a percentage takes part of the amount, and a coupon worth more than the amount takes all of it and no more. `percent_of` multiplies two values, so it has the guard too, and its own `ensures` gives `discount` the fact it needs about that arm.

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

**Paying.** `pay` splits a total between store credit and card. Its two clauses are the whole rule: the two parts add up to the total, and the credit used is never more than the customer has. The verifier proves both on both branches, and also that `total - credit` is a `Cents` where `credit < total`.

```una include="day-to-day/src/billing.una#pay" title="day-to-day/src/billing.una"
--- Splits `total` between store credit and card, credit first.
pub pay(total: Cents, credit: Cents) -> Payment
  ensures result.credit + result.card == total
  ensures result.credit <= credit
  derived from BILLING_1
=
  if credit >= total then Payment(credit: total, card: 0) else Payment(credit: credit, card: total - credit)
```

**Refunding.** `refund` fails rather than break its promise. Its `ensures` covers the path that returns, and the path that fails returns nothing. The failure carries what was paid, so a message can say how much a refund may be.

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

**Running it.** `main` prices two lines, applies a 10% coupon, and pays with 50.00 of store credit. Look at `let total: Cents = gross - off`. Subtracting two `Cents` can give a negative number, so the verifier must prove `gross - off >= 0`. It can, but only because `discount` promises `off <= gross`. Remove that `ensures` and this line no longer checks (mistake 2 shows it). Contracts compose this way: each function's promise is the next function's fact.

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

`una run .` prints the invoice shown under "What you'll build". The second refund asks for 200.00 of an invoice of 169.92, so `refund` fails. `refund_line` keeps the outcome with `attempt`, and `why` turns the failure into words, so the report shows every refund, paid or refused. `money` divides and takes the remainder by the literal 100, so it has no division obligation at all.

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

Each example calls one function with `do` and checks the result with `expect`, or the failure with `expect fails` ([chapter 6](/learn/failure/#s6-6) explains each line). The examples are verified like the rest of the code: a `do` line that calls `pay` with `credit: -5`, or `discount` with a rate of 110, does not check, since the argument does not fit its kind.

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

Two habits make examples and proofs work together:

- **Turn each counterexample into an example**, as in [section 7.2](#s7-2). The case that broke the code once is the case a later change is most likely to break again.
- **Test the exact values; prove the bounds.** A contract states a range or a relation that holds for every input. An example states one exact answer that a person can check by hand.

## 7.8 Common mistakes

Each mistake below is a small change to `day-to-day/src/billing.una`, followed by what `una check .` reports.

:::mistake
**1. A coupon that can be worth more than the order (U5001).** In `discount`, return the coupon's value without the cap:

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

:::mistake
**2. A caller that needs a promise the callee does not make (U5001).** Remove `ensures result <= amount` from `discount`:

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

:::mistake
**3. A comparison the wrong way round (U5001).** In `refund`, swap `asked` and `paid` in the test:

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

:::mistake
**4. A product without a guard (U5002).** Write `line_total` as one expression:

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

:::mistake
**5. A contract outside the refinement language (U2014).** Promise the exact product in `line_total`:

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

:::mistake
**6. A rate above 100 percent (U5001).** Give the coupon a rate of 110:

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

## 7.9 For agents

:::agents
`una --json check .` gives each obligation that is not proven as a diagnostic with its `obligation` (id, kind, goal, status) and its `counterexample` as name and value pairs. For mistake 1:

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U5001","severity":"error","domain":"verification","message":"postcondition of `discount` is refuted","primary":{"file":"src/billing.una","start":{"line":68,"col":25},"end":{"line":68,"col":28}},"related":[{"file":"src/billing.una","start":{"line":62,"col":11},"end":{"line":62,"col":27},"message":"ensures clause"}],"obligation":{"id":"ob-e0a2abc0bb6a","kind":"postcondition","goal":"result <= amount","status":"refuted"},"counterexample":{"bindings":[{"name":"amount","value":0},{"name":"coupon","value":"CentsOff"},{"name":"coupon.amount","value":1},{"name":"coupon.rate","value":101},{"name":"result","value":1}]},"repairs":[{"rank":1,"escape_cost":0,"description":"add a guard or an arm so that the failing path returns a value for which `result <= amount` holds","edit":null},{"rank":2,"escape_cost":0,"description":"adjust the `ensures` clause","edit":null}],"explain":"una explain U5001"}],"fixable":0}
```

The repairs of U5001 and U5002 carry no `edit`, since only the author knows whether the code or the contract is wrong, so `una fix` leaves them. `una --json obligations .` and `una --json trace <ID>` list every obligation, proven or not. The compact rule: *every call proves the callee's `requires`, every return proves the `ensures`, every value that enters a refined kind proves its condition, and unknown is an error; clauses multiply and divide only by literals.*
:::

## 7.10 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples, and a stub when there is one. `una check .` or `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

::::exercise
**Exercise 1: free shipping.** Shipping costs 4.95, and nothing from 50.00. The start package has `shipping` with its contract and a body that always charges 4.95. `una check .` refutes it:

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

::::exercise
**Exercise 2: a fixed price.** A coupon can set the price of a whole invoice, such as "everything for 150.00". Add a variant `FixedPrice(cents: Cents)` to `Coupon`, and an arm for it in `discount`: it takes off the difference when the invoice costs more than the fixed price, and nothing otherwise. The start package ends with these examples, and `una check .` reports U1001 until the variant exists:

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

The counterexample is a fixed price of 0.03 on an invoice of 0: the discount would be −3 cents. Only `coupon.cents` matters here, as in mistake 1: `coupon.amount = -1` is outside `Cents` because that field belongs to no value here.

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

::::exercise
**Exercise 3: a second refund.** A customer can ask for a refund in parts. Write `refund_again(paid, already, asked)`, which refunds `asked` when the refunds together stay within what was paid, and fails with `MoreThanPaid` otherwise. The start package has the header, with its contract, and a body that forgets the refunds already made. `una check .` refutes it:

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

## 7.11 Recap

:::recap
- `requires` states what a caller must prove; the body may assume it.
- `ensures` states what every return promises; callers know a function by its header alone.
- A counterexample shows where a contract breaks; calls in it follow their headers, not their bodies. Fix the code or the contract, and keep a real case as an example.
- Put a rule that holds of every value on its kind, `Int where it >= 0`; never on a type argument.
- Clauses multiply and divide only by literals. A guard for a case the solver cannot rule out is yours to confirm from the kinds.
- U5001: refuted, with a counterexample; U5002: no proof and no real counterexample. Both are errors.
- Check data from outside once, where it enters, and give it a refined kind there.
- Record business rules as requirements, and read their proofs with `una trace`.
:::

## 7.12 Reference

:::reference
- Construct pages: [`requires`](/docs/language/functions/requires/), [`ensures`](/docs/language/functions/ensures/), [`where` and refinements](/docs/language/types/where/), [`predicate`](/docs/language/types/predicate/), [`kind`](/docs/language/types/kind/), [`checked` and the escape budget](/docs/language/errors/checked/), [`requirement`](/docs/language/requirements/requirement/), [`example`](/docs/language/examples/example/), [verification](/docs/language/verification/)
- Prelude: [`Nat`, `Option`, `Result`, `to_int`](/docs/std/)
- Commands: [`una check`](/docs/cli/check/), [`una obligations`](/docs/cli/obligations/), [`una trace`](/docs/cli/trace/), [`una report`](/docs/cli/report/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U2002](/docs/errors/U2002/), [U2014](/docs/errors/U2014/), [U5001](/docs/errors/U5001/), [U5002](/docs/errors/U5002/), [U5003](/docs/errors/U5003/) (the solver is missing or not the pinned version)
- Specification: [functions and contracts](/docs/spec/04-functions-and-contracts/), [types](/docs/spec/03-types/), [verification](/docs/spec/12-verification/), [requirements and examples](/docs/spec/08-requirements-and-examples/), [errors](/docs/spec/06-errors/)
:::
