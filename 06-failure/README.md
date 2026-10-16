---
learn: "6"
title: Failure
editions: ["0.2"]
codes: [U0101, U0102, U1001, U2001, U2007, U3007, U3008, U3009, U3013]
time: 40
builds: An order-intake step that accepts or rejects each line of an order batch
prerequisites: ["3", "4", "5"]
template: 2
---

# 6 Failure

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
> Apart from running out of resources (U6003), host text that is not valid UTF-8 (U6005) and faults that a checked program cannot reach (U8001), nothing in Una fails at run time without the code saying so: division by zero and fixed-width overflow are ruled out by proof ([chapter 7](/learn/contracts/)), and there are no exceptions to catch.

## 6.1 Declaring a failure: `fails` and `fail`

Start with the smallest real case: the quantity a customer types into an order form. It must be a whole number from 1 to 99. Three things can be wrong with it, so the error kind has three variants, and each carries what a message will need.

Each step of this chapter is a package, as in [chapter 1](/learn/hello/package/): a directory with `una.toml`, `verification.lock` and the module under `src/`. The manifest names the package and the module that `una run` starts:

```toml include="steps/01-quantity/una.toml" title="steps/01-quantity/una.toml"
[package]
name = "quantity"
version = "0.1.0"
edition = "0.2"

[run]
entry = "quantity"
grants = ["console"]
```

`verification.lock` pins the solver and is the same in every example: copy it from chapter 1, or download the step's package from this page. Then, in the package's directory:

```sh
una check .
una run .
```

:::steps
```una include="steps/01-quantity/src/quantity.una" title="steps/01-quantity/src/quantity.una" verified="check, run"
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

Walkthrough:

1. **`kind QuantityError = …`.** An error kind is a sum kind like any other ([chapter 4](/learn/kinds/)). Name the variants after what went wrong, not after where: `NotANumber`, not `ReaderFailed`.
2. **`fails QuantityError`.** This header line says that `parse_quantity` can fail, and with which kind. A function declares at most one error kind.
3. **`raw.trim.to_int()` then `if none fail NotANumber(raw)`.** `to_int` returns an `Option[Int]` ([chapter 5](/learn/collections/)): `None` when the text is not a number. The clause on the next line turns `None` into a failure of this function. After it, `n` is a plain `Int`.
4. **`fail TooSmall(value: n)`.** This ends the function with that variant. `fail` can stand in any branch, and the other branches give the value.
5. **`if error use 0`.** In `main`, each call is followed by a handling clause. Here it recovers with `0`. Section 6.2 shows the others.
:::

`una run .` prints:

```text include="steps/01-quantity/expected/output.txt"
3 and 0
```

> [!NOTE] Private functions infer their error kind.
> `parse_quantity` is private, so its `fails` line could be left out: the checker infers it, and `una contract` prints the inferred header with the comment `-- inferred`. A `pub` function is a module's reviewed boundary, so it must declare `fails`. Write the line anyway whenever the failure is part of what a caller should know.

Remove the line to see it. The program checks and prints the same thing, and `una contract` shows the header the checker inferred:

```diff include="steps/01-quantity..steps/02-inferred:src/quantity.una" context="1" title="src/quantity.una"
--- a/src/quantity.una
+++ b/src/quantity.una
@@ -7,3 +7,2 @@
 parse_quantity(raw: Text) -> Int
-  fails QuantityError
 =
```

```text include="steps/02-inferred/expected/commands/contract.txt"
$ una contract quantity.parse_quantity
--- The quantity typed into an order form: a whole number from 1 to 99.
parse_quantity(raw: Text) -> Int
  fails QuantityError -- inferred
```

So a private function without `fails` can still fail. Its contract is the inferred header, which `una contract` prints.

## 6.2 Handling a failure: the five clauses

A statement that can fail is followed by one or two clauses, each on its own line, indented one level below it:

| Clause | Use it when | After it |
| --- | --- | --- |
| `if error use v` | You can carry on with a sensible value | The statement's value is `v` on failure; `error` can be used in `v` |
| `if error pass` | Your function fails with the *same* kind, and the caller should decide | The failure goes to your caller unchanged |
| `if error fail V(...)` | Your function fails with a *different* kind: translate it | Your function fails with `V`; inside `V(...)`, `error` is the original failure |
| `if none use v` | The statement gives an `Option`, and `None` has a sensible default | The value is unwrapped, or `v` |
| `if none fail V(...)` | `None` means the input is wrong | The value is unwrapped, or your function fails with `V` |

> [!IMPORTANT]
> When a statement can both fail and give an `Option`, `if error` comes first and `if none` second.

### Translating between layers with `error`

Most programs have layers: a low-level parser, a line reader above it, a batch report above that. Each layer has its own error kind, because each layer knows different things. The quantity parser knows the text was not a number, and the line reader also knows the line number. `if error fail` translates, and `error` keeps the original failure as a payload, so nothing is lost. This step uses a smaller `QuantityError` than 6.1, with one variant for both bounds, which is enough here:

:::steps
```una include="steps/03-translate/src/upload.una" title="steps/03-translate/src/upload.una" verified="check, run"
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

```text include="steps/03-translate/expected/output.txt"
line 1: 2 units
line 2: no quantity
line 3: 'lots' is not a number
line 4: 500 is not between 1 and 99
```

Walkthrough:

1. **`if none fail MissingQuantity(line: number)`.** `at(index: 1)` gives `None` when the line has no comma. That is the input's fault, so it becomes a failure.
2. **`if error fail BadQuantity(line: number, cause: error)`.** This is translation. `quantity_on_line` fails with `LineError`, and `parse_quantity` fails with `QuantityError`, so `if error pass` would not be allowed (see Common mistakes). `error` is the `QuantityError` that occurred, and it is kept as the `cause`.
3. **`explain` and `cause_text`.** Turning a failure into a message is an ordinary `when`. Because `when` must cover every variant, adding a variant to `LineError` later makes the checker point at every message function that needs a new arm.
4. **`attempt quantity_on_line(number, text: text)` in `show`.** `attempt` keeps the outcome as a value, `Ok(value)` or `Err(failure)`, so `show` can print a message for either. Section 6.3 explains it.
:::

### Recovering with a default from a service

`if error use` and `if none use` are for places where carrying on is the right behavior. A product page should still render when the price service is down. The failure here comes from a capability operation: `Catalog.cents` declares `fails StoreError`, exactly as a function would.

This step uses four constructs that [chapter 8, Capabilities](/learn/capabilities/), covers in full. A `capability` names a set of operations, each declared with `op`, as the host's `Console` names `print`. A function that performs them says so with `uses`. A `handler … for Catalog` gives the operations their code: `fixed` answers with one price, and `down` always fails. `with @catalog = fixed(…)` runs one call with that handler, and `given @catalog = …` does the same for an example. The kind `StoreError = | Timeout` has one variant, and a sum kind with one variant starts with `|`.

```una include="steps/04-defaults/src/prices.una" title="steps/04-defaults/src/prices.una" verified="check, run, test"
module prices

kind StoreError = | Timeout

--- The catalog service: a price in cents, or `None` for a SKU it does not sell.
capability Catalog
  op cents(sku: Text) -> Option[Int]
    fails StoreError

--- The price a product page shows. A page must render even when the catalog is down,
--- so every failure becomes 0, which the page shows as "ask for a price".
shown_price(sku: Text) -> Int
  uses @catalog: Catalog[cents]
=
  let found = @catalog.cents(sku)
    if error use None
    if none use 0
  found

handler fixed(sku: Text, price: Int) for Catalog
  op cents(asked) = if asked == sku then Some(price) else None

handler down() for Catalog
  op cents(asked) = fail Timeout

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = shown_price("LAMP-01") with @catalog = fixed("LAMP-01", price: 1990)
  let desk = shown_price("DESK-02") with @catalog = fixed("LAMP-01", price: 1990)
  let later = shown_price("LAMP-01") with @catalog = down()
  @console.print("{lamp} {desk} {later}")

example "an unknown SKU shows 0"
  given @catalog = fixed("LAMP-01", price: 1990)
  do shown_price("DESK-02")
  expect result == 0

example "a catalog that is down shows 0, and does not fail"
  given @catalog = down()
  do shown_price("LAMP-01")
  expect result == 0
```

`una run .` prints:

```text include="steps/04-defaults/expected/output.txt"
1990 0 0
```

The two clauses read top to bottom. First, a failure of the call becomes the value `None`. Then `None`, from either source, becomes `0`. `shown_price` has no `fails` line, and it needs none: no failure leaves it. Its header promises callers a price, always.

> [!TIP]
> An `example` is a test that lives next to the code. Its `given` lines install fakes, `do` calls the code under test, `result` is what that call returned, and each `expect` line states something that must hold. `una test .` runs every example and reports each one. [Chapter 10, Testing](/learn/testing/), covers examples in full.

`una test .` prints:

```text include="steps/04-defaults/expected/commands/test.txt#L2-L5"
example prices "an unknown SKU shows 0" ... ok
example prices "a catalog that is down shows 0, and does not fail" ... ok

2 examples: 2 passed, 0 failed
```

The handlers `fixed` and `down` are fake catalogs. This is how every failure path in this chapter gets tested without a real service.

## 6.3 Failures as values: `attempt` and `Result`

The handling clauses decide on the spot. Sometimes you want to *keep* the outcome and decide later, for example to report every line of a batch rather than stop at the first bad one. `attempt` turns one call into a `Result[T, E]`: `Ok(value)` if it returned, `Err(failure)` if it failed. `Result` is a sum kind of the prelude, so `when` takes it apart.

`attempt` takes exactly one call, never a larger expression. You usually bind its result with `let`, as `show` does in 6.2. It can also be the whole body of a function that returns the `Result`. When the outcome is `Ok`, everything the callee promises about its result in its header holds for the value, exactly as after a direct call ([chapter 7](/learn/contracts/) shows those promises, `ensures`).

This step checks quantities typed by a person with the prelude's own failing function, `parse_int`, which fails with `ParseError`. It reports every quantity and counts the good ones, instead of stopping at the first bad one:

:::steps
```una include="steps/05-attempt/src/batch.una" title="steps/05-attempt/src/batch.una" verified="check, run"
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
2. **`explain`.** `ParseError` is a sum kind of the prelude: `Empty`, `NoDigits` for a sign alone, and `NotADigit(at)` with the position of the first wrong character, counted from 0. A `when` turns each into words.
3. **`let outcome = attempt raw.parse_int()`.** The usual form. The loop goes on after a bad quantity, since nothing failed: the failure is a value in `outcome`.
4. **`outcome.is_ok()`.** `is_ok` says whether a `Result` is `Ok`, without taking it apart.
:::

`una run .` prints:

```text include="steps/05-attempt/expected/output.txt"
'12': 12 units
'': nothing was typed
'-': a sign with no digits
'3x': not a digit at position 1
1 of 4 accepted, then Ok(7)
```

The last value interpolates as `Ok(7)`: a `Result` is printed like any other value of a sum kind.

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Carry on with a default | `if error use` / `if none use` |
| Let the caller decide, same error kind | `if error pass` |
| Report the failure in your own terms | `if error fail V(cause: error)` |
| Keep going and collect outcomes, retry, or count failures | `attempt`, then `when` |
| Accept outside input that no proof can establish | `checked` (section 6.4) |
:::

## 6.4 When no proof can decide: `checked`

Some facts depend on rules the verifier cannot see inside, such as whether a text is a well-formed SKU. `checked(value, condition) else fail V` tests the condition when the program runs, and gives a value of the refined kind when it holds.

Three constructs of [chapter 7](/learn/contracts/) appear here, briefly:

- `kind Sku = Text where well_formed(it)` is a refined kind: a `Text` for which the condition holds, where `it` stands for the value.
- A `predicate` is a named condition. It is `reflect`, and the verifier sees its body, or `opaque`, and the verifier does not. `checked` is the only way to establish an opaque one.
- `t.slice(start: 4, end: 5)` is the text from position 4 up to, not including, position 5.

> [!WARNING]
> `checked` replaces a proof with a test, so `una.toml` budgets it per module, and `una report .` counts the uses of each module under `escapes`.

```toml include="steps/06-checked/una.toml" title="steps/06-checked/una.toml"
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

```una include="steps/06-checked/src/sku.una" title="steps/06-checked/src/sku.una" verified="check, run"
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
```

`una run .` prints:

```text include="steps/06-checked/expected/output.txt"
sku LAMP-01
not a sku: lamp 1
```

`parse_sku` trims the text, then `checked` tests `well_formed(it)` on it, with `it` standing for the trimmed text. When the test holds, the result has the kind `Sku`; when it does not, `parse_sku` fails with `NotASku`, like any `fail`.

The budget is a line of the manifest, so raising it is a change a reviewer sees. Without an `[escape_budget]` table the budget is 0, and the first `checked` in a module is U7003. `checked_per_module = 1` allows one use in each module.

From then on, a `Sku` can be passed anywhere one is required, with no second check. `shelf_label` takes a `Sku`, so the only way to call it with outside text is through `parse_sku`. A call with a plain `Text` does not check: the verifier cannot prove that the text is well formed.

> [!TIP]
> Use `checked` at the edge of the program, once per fact, and prefer a proof ([chapter 7](/learn/contracts/)) wherever the verifier can see the rule.

## 6.5 Day-to-day: order intake

Now the program from the start of the chapter. Orders arrive as lines of text. Each line must parse, name a product the inventory knows, and ask for no more units than are on hand. The inventory is a service that can time out. A bad line must not stop the batch, and the report must say why each rejected line was rejected.

The design follows from that: one error kind for the order layer, `OrderError`, whose variants carry what an operator needs, and one for the inventory service, `StoreError`, which the order layer translates.

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

**Parsing, a pure step.** `parse_order` only looks at the text. It has no `uses`, so it cannot touch the inventory, and its tests need no fakes.

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

**Checking stock, a step with a service.** Two clauses handle the one call: the service's failure becomes `Unavailable`, and an unknown SKU becomes `UnknownSku`. After them, `left` is a plain `Int`, and the comparison with the quantity wanted is ordinary code. `check_stock` returns the order unchanged when there is enough stock, so the next step can use it.

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

**Composing the steps.** Both steps fail with `OrderError`, the same kind as `accept`, so `if error pass` hands their failures on unchanged. The order of the two statements is the order of the work: a line that does not parse never reaches the inventory, which section 6.6 proves with an example.

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

**The batch.** `attempt` keeps each outcome, so `process` itself never fails. Its header has no `fails`, and that is a promise to its callers.

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

**The report.** One `when` per kind. If `OrderError` gains a variant, the checker reports this `when` until it has an arm for it (exercise 1 shows this). `reason` writes the fields of each variant into its sentence, which is why each variant carries what it does: an operator who reads `3 of DESK-02 wanted, 1 left` knows what to change.

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

**Running it.** In production, the `Inventory` handler would call the warehouse over the network. Here, a handler holds the stock in a map, and `main` installs it with `with`. `warehouse` takes the map as a parameter when it is installed, so each run and each example can start from the stock it needs. `offline` always fails, which is the only way to test `Unavailable` on demand.

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

`una run .` prints the report shown under "What you'll build". The order lines here are literals, one for each outcome: a line in stock, too many units, an unknown SKU, a quantity in words and a line with no comma. `describe` pads `ok` and `reject` to the same width, so the reasons line up.

> [!SECURITY]
> Lines read from a file are labeled `internal`, a label that may not reach the console without a declared policy. Printing a report built from them is a question of information flow, which [chapter 9, Information flow](/learn/information-flow/), answers with a policy.

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

## 6.6 Testing it

Every failure path gets an example: a line in stock, too many units, a malformed line, an inventory that does not answer, an unknown SKU, and a quantity that is not a number. The fakes make each one deterministic. Each example states one fact, so when one fails, `una test .` names it and says which `expect` line did not hold, as the exercises below show.

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

Each line of an example has one job:

- `given @inventory = warehouse(…)` installs a fake inventory for this example only, as `with` does for one call.
- `do accept("LAMP-01, 9")` calls the code under test. A `do` line may nest calls that can fail, which a statement in a body may not.
- `expect result.quantity == 2` states a fact about `result`, the value the `do` call returned.
- `expect fails OutOfStock` holds when the `do` call failed with that variant. A `do` call that fails with no `expect fails` line fails the example.
- `expect not performed @inventory.on_hand` holds when the call never performed that operation. Here it proves the order of the steps: a malformed line or a quantity that is not a number never reaches the inventory, because parsing comes first.

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

## 6.7 Common mistakes

Each mistake below is a small change to `day-to-day/src/orders.una`, followed by what `una check .` reports.

:::mistake
**1. Forgetting the clause (U3007).** Remove `if error pass` under `let order = parse_order(line)`:

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

*Why:* nothing propagates implicitly.

*Fix:* add the clause that matches your intent (table in 6.2).
:::

:::mistake
**2. Passing a failure of another kind (U3008).** In `check_stock`, write `if error pass` instead of `if error fail Unavailable`:

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

*Why:* a function has one error kind, and `StoreError` is not `OrderError`.

*Fix:* translate with `if error fail Unavailable`. To keep the original, add a variant with a field of type `StoreError`, such as `| StoreFailed(cause: StoreError)`, and write `if error fail StoreFailed(cause: error)`.
:::

:::mistake
**3. Failing with a variant of another kind (U3009).** Write `if error fail Timeout` in `check_stock`:

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

*Why:* `fail` names a variant of the function's own error kind, and `Timeout` belongs to `StoreError`.

*Fix:* name a variant of your own kind.
:::

:::mistake
**4. A public function that fails without saying so (U3009).** Remove `fails OrderError` from `parse_order`:

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

una reports this once for every `fail` in the body, five times here.

*Why:* a `pub` header is a reviewed contract.

*Fix:* `una fix .` applies the repair shown.
:::

:::mistake
**5. Nesting a call that can fail (U3013).** Write `check_stock(parse_order(line))`:

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

*Why:* "one effect per line". Each failure needs its own handling line, and evaluation order stays visible.

*Fix:* `let order = parse_order(line)` with its clause, then `check_stock(order)` with its own. (`do` lines of examples are exempt.)
:::

:::mistake
**6. The clause on the same line (U0101).** Write `let order = parse_order(line) if error pass`:

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

*Why:* a clause is a line of its own, so that every handling decision starts a line a reviewer can scan.

*Fix:* `una fix .` moves it.
:::

:::mistake
**7. `if none` before `if error` (U0102).** Swap the two clauses under `@inventory.on_hand` in `check_stock`:

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

*Why:* the `if error` clause handles the call, and `if none` handles the value it gave, so the call's failure comes first.

*Fix:* put `if error` first.
:::

:::mistake
**8. Re-raising a stored failure (U0101).** After `attempt`, writing `is Err(failure) -> fail failure`:

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

*Why:* `fail` names a variant at the place the failure is decided.

*Fix:* if you only want to pass the failure on, do not `attempt`; use `if error pass`. Exercise 3 shows a fallback that needs no re-raise.
:::

:::mistake
**9. A default of the wrong type (U2001).** `if error use "none"` where the call gives an `Order`:

```diff include="day-to-day..mistakes/9:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -56,3 +56,3 @@
   let order = parse_order(line)
-    if error pass
+    if error use "none"
   check_stock(order)
```

```text include="mistakes/9/expected/rendered.txt#L1"
[U2001] Error: expected `Order`, found `Text`
```

*Why:* `use` gives the statement's value on failure, so it must have the statement's type.

*Fix:* use an `Order`, or handle the failure with `fail` or `pass`.
:::

## 6.8 For agents

:::agents
Every diagnostic above is available as JSON with `una --json check .`. For mistake 1:

```json include="mistakes/1/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U3007","severity":"error","domain":"authority","message":"`parse_order` can fail with `OrderError`; handle the failure with an `if error` clause, or wrap the call in `attempt`","primary":{"file":"src/orders.una","start":{"line":56,"col":15},"end":{"line":56,"col":32}},"related":[],"repairs":[],"explain":"una explain U3007"}],"fixable":0}
```

`repairs` is empty because the right clause depends on intent, which only the author knows. U0101 (mistake 6) and U3009 (mistake 4) carry exact edits, which `una fix .` applies. The compact rule: *a call that can fail is the whole expression of its statement, followed by `if error …` and then `if none …` on their own lines, or is wrapped in `attempt`, which gives a `Result`.*
:::

## 6.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's example added. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

::::exercise
**Exercise 1: a per-line limit.** The store ships at most 10 units of a SKU per line. Add a variant `TooMany(sku: Text, limit: Int)` and reject larger quantities in `parse_order`, before the inventory is asked. The start package ends with this example, and `una check .` reports U1001 until the variant exists:

```una include="exercises/1/start/src/orders.una#L137-L141" title="exercises/1/start/src/orders.una"
example "more than ten units on one line is TooMany"
  given @inventory = offline()
  do accept("LAMP-01, 11")
  expect fails TooMany
  expect not performed @inventory.on_hand
```

:::hint
*Hint:* add the variant first and run `una check .`: the checker shows the one `when` that needs a new arm.
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
+    is TooMany(sku, limit) -> "at most {limit} of {sku} per order"
 
```

`una test .` reports every example passing.
:::
::::

::::exercise
**Exercise 2: units shipped.** Write `shipped(results)`, the total of the units of the accepted lines. The start package has it with a body of `0`, and this example:

```una include="exercises/2/start/src/orders.una#L137-L143" title="exercises/2/start/src/orders.una"
--- How many units a batch ships in all. Exercise 2: replace the 0.
pub shipped(results: List[Result[Order, OrderError]]) -> Int = 0

example "a batch ships only its accepted units"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do shipped(process(["LAMP-01, 2", "LAMP-01, 9", "LAMP-01, 1"]))
  expect result == 3
```

:::hint
*Hint:* a private function from one `Result` to an `Int`, then `map` and `sum`.
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

::::exercise
**Exercise 3: fall back to the backup.** The store keeps a backup copy of its inventory. When the inventory does not answer, ask the backup once before giving up. The start package has `on_hand_or_backup`, which asks only the inventory, and three examples:

```una include="exercises/3/start/src/orders.una#on_hand_or_backup" title="exercises/3/start/src/orders.una"
--- The units of `sku` on hand: asks the inventory, and asks the backup copy once when the
--- inventory does not answer.
pub on_hand_or_backup(sku: Text) -> Option[Int]
  uses @inventory: Inventory[on_hand]
  uses @backup: Inventory[on_hand]
  fails StoreError
=
  -- Exercise 3: ask @backup when this call fails.
  @inventory.on_hand(sku)
    if error pass
```

```una include="exercises/3/start/src/orders.una#L148-L165" title="exercises/3/start/src/orders.una"
example "when the inventory does not answer, the backup does"
  given @inventory = offline()
  given @backup = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  do on_hand_or_backup("LAMP-01")
  expect result == Some(4)

example "the backup is not asked when the inventory answers"
  given @inventory = warehouse(empty_map().with(key: "LAMP-01", value: 4))
  given @backup = offline()
  do on_hand_or_backup("LAMP-01")
  expect result == Some(4)
  expect not performed @backup.on_hand

example "when neither answers, the failure is Timeout"
  given @inventory = offline()
  given @backup = offline()
  do on_hand_or_backup("LAMP-01")
  expect fails Timeout
```

A handler holds no state, so no example can make one inventory fail once and then answer. Two bindings of `Inventory`, `@inventory` and `@backup`, make each case one an example can see.

:::hint
*Hint:* `attempt` works on a capability operation too. Keep the first outcome, and ask `@backup` only in the `Err` arm. The backup fails with `Timeout` too, so a plain `if error pass` hands on its failure.
:::

Check your answer with `una test .`. The first example fails on the start package, and the second fails on an answer that always asks the backup.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Replace the body:

```diff include="exercises/3/start..exercises/3/answer:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -143,5 +143,8 @@
 =
-  -- Exercise 3: ask @backup when this call fails.
-  @inventory.on_hand(sku)
-    if error pass
+  let first = attempt @inventory.on_hand(sku)
+  when first
+    is Ok(value) -> value
+    is Err ->
+      @backup.on_hand(sku)
+        if error pass
 
```

To use it in the program, call it from `check_stock` in place of `@inventory.on_hand`. Then `check_stock`, `accept` and `process` also declare `uses @backup: Inventory[on_hand]`, `main` installs a handler for `@backup` in the same `with`, and every example that calls them gives `@backup` a `given` line.
:::
::::

## 6.10 Recap

:::recap
- A failure is a value of a sum kind you declare. Its variants carry what someone needs to act on it.
- A header declares at most one error kind with `fails`. A `pub` function must declare it, and a private one may let the checker infer it.
- A call that can fail is the whole expression of its statement, and its handling clauses follow on their own lines: `if error` first, then `if none`.
- `use` recovers, `pass` hands on the same kind, `fail V(cause: error)` translates between layers.
- `attempt` keeps the outcome of one call as a `Result`, for batches, counts and fallbacks.
- `checked` is a budgeted run-time test for facts no proof can establish. Use it at the edge.
- Fake the services with handlers, and give every failure path an example.
:::

## 6.11 Reference

:::reference
- Construct pages: [`fails`](/docs/language/errors/fails/), [`fail`](/docs/language/errors/fail/), [`if error` and `if none`](/docs/language/errors/if-error/), [`attempt`](/docs/language/errors/attempt/), [`checked` and the escape budget](/docs/language/errors/checked/), [`capability` and `op`](/docs/language/capabilities/capability/), [`handler`](/docs/language/capabilities/handler/), [`with`](/docs/language/capabilities/with/), [`example`](/docs/language/examples/example/), [`predicate`](/docs/language/types/predicate/)
- Prelude: [`Option`, `Result`, `to_int`, `parse_int`, `ParseError`, `is_ok`](/docs/std/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U0102](/docs/errors/U0102/), [U1001](/docs/errors/U1001/), [U2001](/docs/errors/U2001/), [U2007](/docs/errors/U2007/), [U3007](/docs/errors/U3007/), [U3008](/docs/errors/U3008/), [U3009](/docs/errors/U3009/), [U3013](/docs/errors/U3013/), and at run time [U6003](/docs/errors/U6003/), [U6005](/docs/errors/U6005/), [U8001](/docs/errors/U8001/)
- Specification: [errors](/docs/spec/06-errors/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [requirements and examples](/docs/spec/08-requirements-and-examples/), [types](/docs/spec/03-types/), [text](/docs/spec/22-text/)
:::
