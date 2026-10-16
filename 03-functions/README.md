---
learn: "3"
title: Functions
editions: ["0.2"]
codes: [U2001, U2004, U2010, U3004, U5001, U7001]
time: 35
builds: A shipping quote for each order of the day, by weight and zone, with promotions passed in as functions
prerequisites: ["1", "2"]
template: 2
---

# 3 Functions

A function is where most of a program's decisions live: what a parcel costs to ship, when an order ships for free, what a promotion takes off. When a function is called from many places, its header is all most callers read, so it must say everything they need: the values it takes, the value it returns, what it may do outside the program, and what it promises. This chapter writes functions in Una, calls them with named arguments, chooses with `if`, and passes functions as values, through a shipping quote that a store computes for every order.

## What you'll build

:::build
A shipping report. For each order of the day, the program computes the charge from the parcel's weight and the zone it ships to, ships large domestic orders for free, and applies the store's promotions, each one a function passed in:

```text include="day-to-day/expected/output.txt"
order 1042: 7.90
order 1043: ships free
order 1044: 30.90
order 1045: 15.45
order 1046: 6.32
```

You will learn to:

- declare parameters and results, and call with named arguments;
- choose between the short and the long form, and add `requires` and `ensures` clauses;
- choose a value with `if`, on one line or over several;
- tell what a public header must declare from what the checker infers for a private one;
- pass a function, or a lambda written in place, as a value.
:::

## Why it works this way

In many languages a function's signature tells only part of the story. Arguments are matched by position, so `quote(3980, 1200, 1)` compiles whatever order the parameters have, and a swap of two numbers is a bug no tool sees. Whether the function writes to a log or a database is visible only in its body. Its promises, such as "never negative", live in a comment that no tool checks.

Una puts the whole story in the header, and checks it:

:::steps
1. **Arguments carry their parameters' names.** Every argument after the first is written `name: value`, so a call says what each value means.
2. **A public header declares its effects.** A `pub` function that prints says `uses @console: …`. A private function may leave it out, and the checker infers it and shows it to you.
3. **Promises are clauses.** `requires` states what a caller must provide, and `ensures` what the function guarantees. The verifier proves both, and a caller relies on the header alone.
4. **A function is a value.** It can be passed to another function, so a rule that varies, such as a promotion, is a parameter with a type of its own.
:::

> [!KEY]
> A caller of a Una function needs only its header. The names, the types, the effects and the promises are all there, and the checker makes sure the body keeps them.

## 3.1 Parameters, labels and results

A function's header lists its parameters in parentheses, each with its type, then `->` and the type of its result. The types are never inferred in a header: you write them, and every call is checked against them.

A call passes the first argument as it is, and every other one with its parameter's name, a **label**: `line_total(1_990, units: 2)`. The rule makes a call readable on its own, without a look at the header, and it makes a swap of two values visible where it happens: `units: 1_990` reads as wrong at a glance.

:::steps
```una include="steps/01-parameters/src/lines.una" title="src/lines.una" verified="check, run"
module lines

--- What `units` units cost at `unit_cents` cents each.
pub line_total(unit_cents: Int, units: Int) -> Int = unit_cents * units

--- What a line costs with `percent` off its total, rounded down to a whole cent.
pub discounted(unit_cents: Int, units: Int, percent: Int) -> Int = line_total(unit_cents, units: units) * (100 - percent) / 100

--- Prints what three lines of an order cost.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = line_total(1_990, units: 2)
  let units = 3
  let rugs = line_total(4_500, units)
  let mugs = discounted(1_250, percent: 10, units: 4)
  @console.print("lamps {lamps}, rugs {rugs}, mugs {mugs}")
```

1. **`line_total(unit_cents: Int, units: Int) -> Int`.** Two parameters, both `Int`, and an `Int` result.
2. **`line_total(1_990, units: 2)`.** The first argument goes without a label; the second carries `units:`.
3. **`line_total(4_500, units)`.** A name equal to the parameter's name counts as labeled. `units` here means `units: units`.
4. **`discounted(1_250, percent: 10, units: 4)`.** Labeled arguments may come in any order, since each says which parameter it is for.
5. **`line_total(unit_cents, units: units)` inside `discounted`.** A function may call another, with the same rules.
:::

`una run .` prints:

```text include="steps/01-parameters/expected/output.txt"
lamps 3980, rugs 13500, mugs 4500
```

A call with one argument may leave out its label, as `availability(3)` does in [section 3.3](#s3-3), since there is nothing to confuse it with. Name parameters for what they mean to a caller: `unit_cents` and `units` read well at the call, where `a` and `b` would not. A label that names no parameter does not check, and neither does a second argument without a label. [Common mistakes](#s3-8) shows the diagnostic, and its repair, which `una fix .` applies for you.

**Method syntax.** A call can also be written with its first argument in front, as the prelude's functions are in [chapter 2](/learn/values/#s2-3): `raw.trim` is `trim(raw)`, and `cents.line_total(units: 2)` would be `line_total(cents, units: 2)`. Use it where it reads as a pipeline of steps on one value, as `raw.trim.to_upper` does, and the plain form elsewhere.

## 3.2 Two forms, and clauses

Every function has exactly one canonical form, and `una fmt` writes it:

- The **short form**, `name(params) -> Type = expression`, on one line. It is the form of a function with no clauses whose body is one line.
- The **long form**: the header, then its clauses, one per line, then `=` alone on its line, then the body, indented by two spaces. Every other function takes it.

**Clauses** are lines of the header after the result type. `uses` is one, from [chapter 1](/learn/hello/#s1-3). Two more state a function's promises:

- `requires p` is a **precondition**: a fact about the parameters that every caller must make true. The body may rely on it.
- `ensures q` is a **postcondition**: a fact about the result, named `result`, that the function guarantees whenever it returns. Every caller may rely on it.

The verifier proves both before the program runs: each `ensures` against the body, and each `requires` at every call.

:::steps
```una include="steps/02-forms/src/fees.una" title="src/fees.una" verified="check, run"
module fees

--- Half of an amount, rounded down. No clauses and a body of one line: the short form.
pub half(cents: Int) -> Int = cents / 2

--- The amount with the card fee of 50 cents added. A clause needs the long form.
pub with_card_fee(cents: Int) -> Int
  ensures result == cents + 50
=
  cents + 50

--- The rate of a parcel of `grams` grams: 450 cents for the first kilogram, and 250 more
--- for each kilogram or part of one after it. A body of several lines needs the long form.
pub parcel_rate(grams: Int) -> Int
  requires grams > 0
  ensures result >= 450
=
  let kilos = (grams + 999) / 1_000
  450 + (kilos - 1) * 250

--- Prints a few fees and rates.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("half of 1990: {half(1_990)}")
  @console.print("with the card fee: {with_card_fee(1_990)}")
  @console.print("500 g: {parcel_rate(500)}, 2300 g: {parcel_rate(2_300)}")
```

1. **`half`.** No clauses and a body of one line: the short form.
2. **`with_card_fee`.** One `ensures` clause, so the long form, even though its body is one line.
3. **`parcel_rate`.** A precondition, a postcondition, and a body of two lines. The body is a block: `let` lines first, and its value is its last line.
4. **`requires grams > 0` and `ensures result >= 450`.** From the precondition, the verifier proves that `kilos` is at least 1, so the rate is at least 450.
:::

`una run .` prints:

```text include="steps/02-forms/expected/output.txt"
half of 1990: 995
with the card fee: 2040
500 g: 450, 2300 g: 950
```

A promise the body does not keep does not check. Raise the promised minimum to 500:

```diff include="steps/02-forms..steps/03-promise:src/fees.una" title="src/fees.una" context="0"
--- a/src/fees.una
+++ b/src/fees.una
@@ -16 +16 @@
-  ensures result >= 450
+  ensures result >= 500
```

```text include="steps/03-promise/expected/rendered.txt#L1-L10,L18"
[U5001] Error: postcondition of `parcel_rate` is refuted
    ╭─[ src/fees.una:19:3 ]
    │
 16 │   ensures result >= 500
    │           ──────┬──────
    │                 ╰──────── ensures clause
    │
 19 │   450 + (kilos - 1) * 250
    │   ───────────┬───────────
    │              ╰───────────── postcondition of `parcel_rate` is refuted
    │ Note 2: counterexample: grams = 1000, result = 450
```

The counterexample names an input, a parcel of 1000 g, for which the body returns 450, which breaks the promise. Either the body or the clause is wrong, and the verifier cannot tell which: that is your decision. [Chapter 7, Contracts and the verifier](/learn/contracts/), covers clauses in depth.

> [!TIP]
> Canonical form is not a style to learn: it is what `una fmt` writes. Write a function in the layout that comes to you, run `una fmt .`, and read the form it chose.

## 3.3 Choosing a value: `if`

`if` in Una is an expression: it gives a value, and both branches give one of the same type. On one line it reads `if condition then value else value`. Over several lines, each branch is an indented block, and its value is its last line. `else if` chains further conditions.

:::steps
```una include="steps/04-if/src/stock.una" title="src/stock.una" verified="check, run"
module stock

--- "unit" or "units", whichever goes with `count`.
pub units_word(count: Int) -> Text = if count == 1 then "unit" else "units"

--- What a product page says about the stock of a product.
pub availability(on_hand: Int) -> Text
=
  if on_hand <= 0
    "out of stock"
  else if on_hand < 5
    let word = units_word(on_hand)
    "only {on_hand} {word} left"
  else
    "in stock"

--- Prints what the product page says for four stock levels.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(availability(0))
  @console.print(availability(1))
  @console.print(availability(3))
  @console.print(availability(40))
```

1. **`if count == 1 then "unit" else "units"`.** The one-line form, as a whole function body. Both branches are `Text`.
2. **`if on_hand <= 0`, `else if on_hand < 5`, `else`.** The form over several lines. The conditions are tried in order, and the first that holds gives the value.
3. **`let word = units_word(on_hand)` inside a branch.** A branch is a block, so it may name values before its last line. `word` exists only inside that branch.
4. **`"only {on_hand} {word} left"`.** The branch's last line, and so its value.
:::

`una run .` prints:

```text include="steps/04-if/expected/output.txt"
out of stock
only 1 unit left
only 3 units left
in stock
```

An `if` that gives a value always has an `else`, since a value is needed whichever way the condition goes. The one-line form without `else` does not parse. An `if` over several lines without `else` is a statement, not a value: its body runs only when the condition holds, and a loop in [chapter 5](/learn/collections/) uses it so. The checker also holds the branches to one type, so an `if` whose branches return a text and a number is reported where it is written, not where its value is used.

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Choose between two short values | `if c then a else b`, on one line |
| Choose among several cases, or name values in a branch | `if` and `else if` over several lines |
| Choose by the variant of a value, such as `Some` or `None` | `when`, in [chapter 4](/learn/kinds/) |
| Do something only when a condition holds | `if` without `else`, as a statement, in a loop or a body |
:::

The branches of an `if` are checked with what the condition says. In [chapter 2](/learn/values/#s2-3), `fit_name` cuts a name only in the branch where `name.len > 24`, and the verifier uses that fact to prove the cut is in range.

## 3.4 `pub`, and the headers the checker infers

A declaration is private to its module unless it starts with `pub`. A private function can be called only from its own module. A `pub` function can be called from other modules, so its header is a promise to code you do not see, and it must declare everything: the `uses` of every capability it touches, and the failures it may return, which [chapter 6](/learn/failure/) covers.

A private function may leave out its `uses`. The checker works it out from the body and from the calls, and `una contract` prints the result:

:::steps
```una include="steps/05-inferred/src/restock.una" title="src/restock.una" verified="check, run"
module restock

--- How many units to order so that the shelf holds `target` again.
pub to_order(on_hand: Int, target: Int) -> Int = max(target - on_hand, b: 0)

-- Prints one line of the restock list. It is private, so it may leave out `uses`: the
-- checker infers it from the body.
show(sku: Text, units: Int) -> Unit = @console.print("{sku}: order {units}")

--- Prints the restock list of two SKUs.
pub main() -> Unit
  uses @console: Console[print]
=
  show("LAMP-01", units: to_order(3, target: 10))
  show("RUG-07", units: to_order(12, target: 10))
```

1. **`to_order`.** A public function with no `uses`: it cannot print, and it only computes. `max(target - on_hand, b: 0)` never orders fewer than none.
2. **`show(sku: Text, units: Int) -> Unit = @console.print(…)`.** A private function that prints, with no `uses` in its header.
3. **`main` calls `show`.** `main` declares the console, so `show`, called from it, gets the console too.
:::

`una run .` prints:

```text include="steps/05-inferred/expected/output.txt"
LAMP-01: order 7
RUG-07: order 0
```

`una contract` shows the header the checker inferred for `show`, marked as such:

```sh
una contract restock.show
```

```text include="steps/05-inferred/expected/commands/contract.txt#L2-L3"
show(sku: Text, units: Int) -> Unit
  uses @console: Console[print] -- inferred
```

The inference saves lines inside a module, where every caller is in view, and the `-- inferred` mark keeps it visible to a reviewer and to the build report. At the boundary of a module, nothing is inferred: a `pub` function that prints without `uses` does not check, as [Common mistakes](#s3-8) shows. Types are never inferred, for any function: every parameter and every result is written.

The build report lists the authority of every function, declared or inferred, so a reviewer can read the effects of a whole package in one place. For this package, the authority part of `una report .` lists `restock.main` as public and `restock.show` as private and inferred, each with `@console: Console[print]`.

> [!NOTE]
> The rule is the same as in [chapter 1](/learn/hello/#s1-3): what a public function may do is in its header. Private functions are the module's own business, and the checker still knows exactly what each one does.

## 3.5 Functions as values, and lambdas

A function is a value, and a parameter can take one. Its type is written `fn(Int) -> Int`: a function that takes an `Int` and returns an `Int`. You pass a function declared with a name by that name, or write one in place as a **lambda**, `fn(params) -> expression`.

:::steps
```una include="steps/06-lambdas/src/pricing.una" title="src/pricing.una" verified="check, run"
module pricing

--- A price after a pricing rule: a function from a price in cents to a price in cents.
pub priced(cents: Int, rule: fn(Int) -> Int) -> Int = rule(cents)

--- A rule: the price rounded down to the next price that ends in 99 cents.
pub ends_in_99(cents: Int) -> Int = (cents + 1) / 100 * 100 - 1

--- Prints a price under three rules.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{priced(2_050, rule: ends_in_99)}")
  @console.print("{priced(2_050, rule: fn(cents) -> cents - 500)}")
  let markup = 120
  @console.print("{priced(2_050, rule: fn(cents) -> cents * markup / 100)}")
```

1. **`priced(cents: Int, rule: fn(Int) -> Int) -> Int = rule(cents)`.** A parameter of function type, called like any function.
2. **`priced(2_050, rule: ends_in_99)`.** A named function passed as a value: no parentheses after its name, since it is not called here.
3. **`fn(cents) -> cents - 500`.** A lambda. Its parameter's type, `Int`, comes from the type of `rule`, so you need not write it. Its body is one expression.
4. **`fn(cents) -> cents * markup / 100`.** A lambda that uses `markup`, a name from around it. It captures the value `markup` has when the lambda is made.
:::

`una run .` prints:

```text include="steps/06-lambdas/expected/output.txt"
1999
1550
2460
```

A lambda gets its parameter types from where it is used. Bound with `let` on its own line, it has no such place, and the checker asks for the type: write `fn(cents: Int) -> …`, or pass it straight to the function that uses it. A lambda's body is one expression, so a rule that needs several lines is a named function, passed by its name.

Functions can also return functions, since a function is a value like any other. The last exercise of this chapter builds one promotion out of two that way.

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| A rule used in several places, or one worth an example | a named function, passed by its name |
| A one-line rule used once, at the call | a lambda, `fn(x) -> …` |
| A rule that reads a value from around the call | a lambda, which captures it |
| A rule that needs several lines | a named function |
:::

> [!NOTE]
> A function may call itself, and two functions may call each other. Loops over lists, in [chapter 5](/learn/collections/), cover most of what recursion does in other languages, with an end a reader can see.

## 3.6 Day-to-day: shipping quotes

Every order needs a shipping charge before it can be paid. The rate depends on the parcel's weight, the zone adds a surcharge, large orders within the country ship for free, and marketing runs promotions that change from week to week. The report at the end of the day lists the charge of each order.

Each rule is a function, and each function's header states what a caller may rely on. The promotions are the part that changes most, so they are parameters: the code that applies a promotion does not know which one it is, and a new promotion is a new function, not a change to the quote.

**The rate and the zone.** Two functions with `if` chains, each with a precondition and a postcondition:

```una include="day-to-day/src/shipping.una#base_rate..zone_surcharge" title="day-to-day/src/shipping.una" caption="rate and surcharge"
--- The rate of a parcel of `grams` grams within the home country, in cents: 450 up to
--- 500 g, 790 up to 2 kg, and 250 more for each kilogram or part of one above 2 kg.
pub base_rate(grams: Int) -> Int
  requires grams > 0
  ensures result >= 450
=
  if grams <= 500
    450
  else if grams <= 2_000
    790
  else
    790 + (grams - 2_000 + 999) / 1_000 * 250

--- What a zone adds to the rate, in cents. Zone 1 is the home country, zone 2 its
--- neighbors, and zone 3 the rest of the world.
pub zone_surcharge(zone: Int) -> Int
  requires zone >= 1 and zone <= 3
  ensures result >= 0
=
  if zone == 1
    0
  else if zone == 2
    600
  else
    1_800
```

`base_rate` requires a weight above zero, which rules out an empty parcel. Its third branch rounds up to a started kilogram: adding 999 grams before dividing by 1000 turns 1 to 1000 extra grams into one kilogram, 1001 to 2000 into two. Its `ensures result >= 450` says that no parcel ships for less than the lowest rate, and the verifier proves it for each branch.

`zone_surcharge` requires a zone from 1 to 3, the zones the store ships to. Its `ensures result >= 0` looks obvious from the body, and it matters all the same: callers of `zone_surcharge` see its header, not its body. [Common mistakes](#s3-8) shows what happens to `quote` without that line.

**The quote.** One function puts the rules together:

```una include="day-to-day/src/shipping.una#ships_free..quote" title="day-to-day/src/shipping.una" caption="the quote"
--- Whether an order ships for free: 10000 cents of goods or more, within the home country.
pub ships_free(goods: Int, zone: Int) -> Bool = zone == 1 and goods >= 10_000

--- What shipping costs for an order, before any promotion.
pub quote(goods: Int, grams: Int, zone: Int) -> Int
  requires grams > 0
  requires zone >= 1 and zone <= 3
  ensures result >= 0
=
  if ships_free(goods, zone) then 0 else base_rate(grams) + zone_surcharge(zone)
```

`ships_free(goods, zone)` uses two punned arguments, since the names match the parameters. `quote` repeats the preconditions of the functions it calls, since its callers must provide the weight and the zone. Its `ensures result >= 0` follows from the two postconditions above it: 0 when the order ships free, at least 450 plus at least 0 otherwise.

**Promotions as values.** A promotion is any function from a charge to a charge. `promoted` applies one, and its header guarantees that the customer never pays more than the charge, and never less than nothing, whatever the promotion computes:

```una include="day-to-day/src/shipping.una#half_off..promoted" title="day-to-day/src/shipping.una" caption="promotions"
--- A promotion: half the charge, rounded up to a whole cent.
pub half_off(charge: Int) -> Int = (charge + 1) / 2

--- The charge after a promotion. Whatever the promotion computes, the customer never pays
--- more than the charge, and never less than nothing.
pub promoted(charge: Int, promotion: fn(Int) -> Int) -> Int
  requires charge >= 0
  ensures result >= 0 and result <= charge
=
  max(0, b: min(promotion(charge), b: charge))
```

The body clamps the promotion's result between 0 and the charge, with `min` and `max` from the prelude. Their own postconditions let the verifier prove `promoted`'s promise for every promotion, the ones that exist today and the ones marketing has not invented yet.

**The report.** `money` writes cents as an amount, as in [chapter 2](/learn/values/#s2-6). `report_line` chooses the text with a one-line `if`. `show` prints one line, and is private, so its `uses` is inferred. `main` quotes five orders:

```una include="day-to-day/src/shipping.una#money..main" title="day-to-day/src/shipping.una" caption="the report"
--- Cents as an amount with two decimals, for an amount that is not negative.
pub money(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"

--- The line of the shipping report for one order.
pub report_line(order: Int, charge: Int) -> Text = if charge == 0 then "order {order}: ships free" else "order {order}: {money(charge)}"

-- Prints one line of the report. It is private, so its `uses` is inferred from its body.
show(order: Int, charge: Int) -> Unit = @console.print(report_line(order, charge))

--- Prints the shipping report of five orders of the day.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = quote(3_980, grams: 1_200, zone: 1)
  show(1042, charge: lamps)
  let desk = quote(15_900, grams: 24_000, zone: 1)
  show(1043, charge: desk)
  let charge = quote(4_500, grams: 3_200, zone: 3)
  show(1044, charge)
  let weekend = promoted(charge, promotion: half_off)
  show(1045, charge: weekend)
  let members = promoted(lamps, promotion: fn(cents) -> cents * 80 / 100)
  show(1046, charge: members)
```

The first three orders show the rules: a light parcel within the country, a heavy desk that ships free, and a parcel abroad. The last two apply promotions: `half_off` by its name, and a members' rule of 20 percent off as a lambda. `show(1044, charge)` uses punning again: the value named `charge` goes to the parameter `charge`.

Every call of `quote` is checked against its preconditions, so the verifier proves that `24_000 > 0` and that zone 3 is between 1 and 3. Every call of `promoted` must provide `charge >= 0`, and the verifier proves it from `quote`'s postcondition: the promise of one function is what makes the call of the next one safe.

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/shipping.una" title="day-to-day/src/shipping.una" caption="the whole program" verified="check, run, test"
module shipping

-- Shipping quotes: what each order of the day costs to ship, by weight and zone, and what
-- the store's promotions take off.

--- The rate of a parcel of `grams` grams within the home country, in cents: 450 up to
--- 500 g, 790 up to 2 kg, and 250 more for each kilogram or part of one above 2 kg.
pub base_rate(grams: Int) -> Int
  requires grams > 0
  ensures result >= 450
=
  if grams <= 500
    450
  else if grams <= 2_000
    790
  else
    790 + (grams - 2_000 + 999) / 1_000 * 250

--- What a zone adds to the rate, in cents. Zone 1 is the home country, zone 2 its
--- neighbors, and zone 3 the rest of the world.
pub zone_surcharge(zone: Int) -> Int
  requires zone >= 1 and zone <= 3
  ensures result >= 0
=
  if zone == 1
    0
  else if zone == 2
    600
  else
    1_800

--- Whether an order ships for free: 10000 cents of goods or more, within the home country.
pub ships_free(goods: Int, zone: Int) -> Bool = zone == 1 and goods >= 10_000

--- What shipping costs for an order, before any promotion.
pub quote(goods: Int, grams: Int, zone: Int) -> Int
  requires grams > 0
  requires zone >= 1 and zone <= 3
  ensures result >= 0
=
  if ships_free(goods, zone) then 0 else base_rate(grams) + zone_surcharge(zone)

--- A promotion: half the charge, rounded up to a whole cent.
pub half_off(charge: Int) -> Int = (charge + 1) / 2

--- The charge after a promotion. Whatever the promotion computes, the customer never pays
--- more than the charge, and never less than nothing.
pub promoted(charge: Int, promotion: fn(Int) -> Int) -> Int
  requires charge >= 0
  ensures result >= 0 and result <= charge
=
  max(0, b: min(promotion(charge), b: charge))

--- Cents as an amount with two decimals, for an amount that is not negative.
pub money(cents: Int) -> Text = "{cents / 100}.{cents mod 100 / 10}{cents mod 10}"

--- The line of the shipping report for one order.
pub report_line(order: Int, charge: Int) -> Text = if charge == 0 then "order {order}: ships free" else "order {order}: {money(charge)}"

-- Prints one line of the report. It is private, so its `uses` is inferred from its body.
show(order: Int, charge: Int) -> Unit = @console.print(report_line(order, charge))

--- Prints the shipping report of five orders of the day.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = quote(3_980, grams: 1_200, zone: 1)
  show(1042, charge: lamps)
  let desk = quote(15_900, grams: 24_000, zone: 1)
  show(1043, charge: desk)
  let charge = quote(4_500, grams: 3_200, zone: 3)
  show(1044, charge)
  let weekend = promoted(charge, promotion: half_off)
  show(1045, charge: weekend)
  let members = promoted(lamps, promotion: fn(cents) -> cents * 80 / 100)
  show(1046, charge: members)

example "a parcel up to 500 g ships at the lowest rate"
  do base_rate(500)
  expect result == 450

example "each started kilogram above 2 kg adds 250 cents"
  do base_rate(3_200)
  expect result == 1_290

example "the rest of the world adds 1800 cents"
  do zone_surcharge(3)
  expect result == 1_800

example "a large order within the country ships free"
  do quote(15_900, grams: 24_000, zone: 1)
  expect result == 0

example "a large order abroad pays shipping"
  do quote(15_900, grams: 24_000, zone: 2)
  expect result == 6_890

example "half off rounds up to a whole cent"
  do half_off(3_091)
  expect result == 1_546

example "a promotion never raises the charge"
  do promoted(790, promotion: fn(cents) -> cents + 100)
  expect result == 790

example "a promotion never makes the charge negative"
  do promoted(790, promotion: fn(cents) -> cents - 1_000)
  expect result == 0

example "a free order says so"
  do report_line(1043, charge: 0)
  expect result == "order 1043: ships free"
```

`una run .` prints the report shown under "What you'll build". Order 1044 ships 3200 g abroad: 790 for the first 2 kg, 500 for two started kilograms above them, and 1800 for the zone, 30.90 in all. Its weekend promotion halves that to 15.45.

> [!SECURITY]
> Of the ten functions in the file, only `show` and `main` touch the console. `main` says so in its header, `una contract shipping.show` shows the inferred `uses` of `show`, and every other function has no `uses`, so it cannot have an effect of any kind. A promotion passed to `promoted` is a pure function too: the type `fn(Int) -> Int` has no `uses`, so a promotion that tried to print would not check.

## 3.7 Testing it

The examples cover each rule at its edges: the lowest rate, a started kilogram, the far zone, free shipping within the country and not abroad, the rounding of `half_off`, and the two guarantees of `promoted`:

```una include="day-to-day/src/shipping.una#L78-L112" title="day-to-day/src/shipping.una" caption="the examples"
example "a parcel up to 500 g ships at the lowest rate"
  do base_rate(500)
  expect result == 450

example "each started kilogram above 2 kg adds 250 cents"
  do base_rate(3_200)
  expect result == 1_290

example "the rest of the world adds 1800 cents"
  do zone_surcharge(3)
  expect result == 1_800

example "a large order within the country ships free"
  do quote(15_900, grams: 24_000, zone: 1)
  expect result == 0

example "a large order abroad pays shipping"
  do quote(15_900, grams: 24_000, zone: 2)
  expect result == 6_890

example "half off rounds up to a whole cent"
  do half_off(3_091)
  expect result == 1_546

example "a promotion never raises the charge"
  do promoted(790, promotion: fn(cents) -> cents + 100)
  expect result == 790

example "a promotion never makes the charge negative"
  do promoted(790, promotion: fn(cents) -> cents - 1_000)
  expect result == 0

example "a free order says so"
  do report_line(1043, charge: 0)
  expect result == "order 1043: ships free"
```

Two of them pass lambdas in their `do` lines. "a promotion never raises the charge" passes a promotion that adds 100 cents, and "a promotion never makes the charge negative" one that takes off 1000. Neither is a real promotion. They are the misbehaving promotions that `promoted` exists to contain, so they test the reason for its body, not only the happy path.

The postconditions and the examples do different jobs. `ensures result >= 0 and result <= charge` is proved for every promotion and every charge, but it does not say which value `promoted` returns. The examples fix exact values, 790 and 0, for two cases. Together they say both what is always true and what happens in the cases a reader cares about.

The examples leave out `show` and `main`, the two functions that print. Everything they do is call a function the examples already cover and print the result, so a test of them would test the console. Zone 2 has no example of its own either; "a large order abroad pays shipping" passes through it, with 6890 cents: 6290 for 24 kg and 600 for the zone.

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L12"
example shipping "a parcel up to 500 g ships at the lowest rate" ... ok
example shipping "each started kilogram above 2 kg adds 250 cents" ... ok
example shipping "the rest of the world adds 1800 cents" ... ok
example shipping "a large order within the country ships free" ... ok
example shipping "a large order abroad pays shipping" ... ok
example shipping "half off rounds up to a whole cent" ... ok
example shipping "a promotion never raises the charge" ... ok
example shipping "a promotion never makes the charge negative" ... ok
example shipping "a free order says so" ... ok

9 examples: 9 passed, 0 failed
```

## 3.8 Common mistakes

Each mistake below is a small change to `day-to-day/src/shipping.una`, followed by what `una check .` reports.

:::mistake
**1. A second argument without its label (U2004).** Passing the weight by position:

```diff include="day-to-day..mistakes/1:src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -66,3 +66,3 @@
 =
-  let lamps = quote(3_980, grams: 1_200, zone: 1)
+  let lamps = quote(3_980, 1_200, zone: 1)
   show(1042, charge: lamps)
```

```text include="mistakes/1/expected/rendered.txt#L1,L8"
[U2004] Error: argument 2 of `quote` needs a label; only the first argument may go without one
    │ Help: repair 1: label it `grams`; edit src/shipping.una:67:28..67:33 to "grams: 1_200"
```

*Why:* only the first argument may go without a label.

*Fix:* `grams: 1_200`. The repair is an exact edit, which `una fix .` applies. See [U2004](/docs/errors/U2004/).
:::

:::mistake
**2. Branches of two types (U2001).** Returning the number itself when the order does not ship free:

```diff include="day-to-day..mistakes/2:src/shipping.una" context="0"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -58 +58 @@
-pub report_line(order: Int, charge: Int) -> Text = if charge == 0 then "order {order}: ships free" else "order {order}: {money(charge)}"
+pub report_line(order: Int, charge: Int) -> Text = if charge == 0 then "order {order}: ships free" else charge
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U2001] Error: `report_line` returns `Text`, found `Int`
```

*Why:* both branches of an `if` give the function's result, which is a `Text`, and `charge` is an `Int`.

*Fix:* a text in both branches, such as `"order {order}: {money(charge)}"`. See [U2001](/docs/errors/U2001/).
:::

:::mistake
**3. A promise the caller needs, left out (U5001).** Removing the postcondition of `zone_surcharge`:

```diff include="day-to-day..mistakes/3:src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -22,3 +22,2 @@
   requires zone >= 1 and zone <= 3
-  ensures result >= 0
 =
```

```text include="mistakes/3/expected/rendered.txt#L1-L10,L18"
[U5001] Error: postcondition of `quote` is refuted
    ╭─[ src/shipping.una:40:42 ]
    │
 38 │   ensures result >= 0
    │           ─────┬─────
    │                ╰─────── ensures clause
    │
 40 │   if ships_free(goods, zone) then 0 else base_rate(grams) + zone_surcharge(zone)
    │                                          ───────────────────┬───────────────────
    │                                                             ╰───────────────────── postcondition of `quote` is refuted
    │ Note 2: counterexample: grams = 1, result = -1, zone = 1
```

*Why:* the verifier checks `quote` with the header of `zone_surcharge`, not its body. Without its `ensures`, the surcharge could be any `Int`, so `quote` could be negative, and the counterexample shows one such case.

*Fix:* put the clause back. A caller can rely only on what a header promises. See [U5001](/docs/errors/U5001/).
:::

:::mistake
**4. A call that breaks a precondition (U5001).** Quoting a zone the store does not ship to:

```diff include="day-to-day..mistakes/4:src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -70,3 +70,3 @@
   show(1043, charge: desk)
-  let charge = quote(4_500, grams: 3_200, zone: 3)
+  let charge = quote(4_500, grams: 3_200, zone: 4)
   show(1044, charge)
```

```text include="mistakes/4/expected/rendered.txt#L1-L10"
[U5001] Error: precondition `4 >= 1 and 4 <= 3` of this call is refuted
    ╭─[ src/shipping.una:71:16 ]
    │
 38 │   requires zone >= 1 and zone <= 3
    │            ───────────┬───────────
    │                       ╰───────────── requires clause
    │
 71 │   let charge = quote(4_500, grams: 3_200, zone: 4)
    │                ─────────────────┬─────────────────
    │                                 ╰─────────────────── precondition `4 >= 1 and 4 <= 3` of this call is refuted
```

*Why:* `quote` requires a zone from 1 to 3, and the verifier proves that at every call. With a literal, the obligation is simply false.

*Fix:* a zone from 1 to 3. When the zone comes from data, check it with an `if` before the call, so that the verifier sees the check. See [U5001](/docs/errors/U5001/).
:::

:::mistake
**5. A public function that prints without `uses` (U3004).** Making `show` public:

```diff include="day-to-day..mistakes/5:src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -59,4 +59,4 @@
 
--- Prints one line of the report. It is private, so its `uses` is inferred from its body.
-show(order: Int, charge: Int) -> Unit = @console.print(report_line(order, charge))
+--- Prints one line of the report.
+pub show(order: Int, charge: Int) -> Unit = @console.print(report_line(order, charge))
 
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U3004] Error: `@console` is used here, but this code declares no `uses`, so it is pure
```

*Why:* nothing is inferred for a `pub` function. A public header declares its effects.

*Fix:* add `uses @console: Console[print]` to its header, or keep it private. See [U3004](/docs/errors/U3004/).
:::

:::mistake
**6. A lambda bound with `let` (U2010).** Naming the members' rule before passing it:

```diff include="day-to-day..mistakes/6:src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -74,3 +74,4 @@
   show(1045, charge: weekend)
-  let members = promoted(lamps, promotion: fn(cents) -> cents * 80 / 100)
+  let members_rule = fn(cents) -> cents * 80 / 100
+  let members = promoted(lamps, promotion: members_rule)
   show(1046, charge: members)
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U2010] Error: cannot infer the type of lambda parameter `cents`; annotate it, as in `cents: Int`
```

*Why:* a lambda's parameter types come from the place it is passed to. A `let` gives it none.

*Fix:* `fn(cents: Int) -> cents * 80 / 100`, or pass the lambda straight to `promoted`. See [U2010](/docs/errors/U2010/).
:::

:::mistake
**7. The long form for a one-line function (U7001).** Writing `ships_free` with `=` on its own line:

```diff include="day-to-day..mistakes/7:src/shipping.una" context="0"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -33 +33,3 @@
-pub ships_free(goods: Int, zone: Int) -> Bool = zone == 1 and goods >= 10_000
+pub ships_free(goods: Int, zone: Int) -> Bool
+=
+  zone == 1 and goods >= 10_000
```

```text include="mistakes/7/expected/rendered.txt#L1"
[U7001] Error: lines 33 to 35 are not in canonical form
```

*Why:* a function without clauses whose body is one line has one canonical form, the short one.

*Fix:* `una fmt .` rewrites it. See [U7001](/docs/errors/U7001/).
:::

## 3.9 For agents

:::agents
`una --json check .` gives every diagnostic with its repairs. U2004 and U7001 carry exact edits, which `una fix .` applies; U5001 carries a counterexample and ranked repairs that need a decision. `una --json contract shipping.quote` gives a function's full header, declared or inferred, which is what a caller may rely on. The compact rule: *label every argument after the first; write the long form when a function has clauses or a body of several lines; a `pub` header declares its `uses`; a caller relies only on `requires` and `ensures`; a lambda gets its parameter types from where it is passed.*
:::

## 3.10 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added at the end, and a stub of the function to write, whose body is a placeholder value. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

::::exercise
**Exercise 1: delivery days.** Write `delivery_days(zone)`: 2 days within the home country, 4 in the neighboring countries, and 9 in the rest of the world. The start package ends with:

```una include="exercises/1/start/src/shipping.una#L114-L124" title="exercises/1/start/src/shipping.una"
--- The days an order takes to arrive: 2 within the home country, 4 in the neighboring
--- countries, and 9 in the rest of the world.
pub delivery_days(zone: Int) -> Int = 0

example "an order within the country arrives in two days"
  do delivery_days(1)
  expect result == 2

example "an order to the rest of the world takes nine days"
  do delivery_days(3)
  expect result == 9
```

:::hint
*Hint:* `zone_surcharge` has the same shape. A function with a `requires` clause and a body of several lines takes the long form.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L11-L18"
example shipping "an order within the country arrives in two days" ... FAILED
  src/shipping.una:120: expect result == 2
  it is false, with `result` = `0`
example shipping "an order to the rest of the world takes nine days" ... FAILED
  src/shipping.una:124: expect result == 9
  it is false, with `result` = `0`

11 examples: 9 passed, 2 failed
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Give `delivery_days` a precondition and an `if` chain:

```diff include="exercises/1/start..exercises/1/answer:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -115,3 +115,11 @@
 --- countries, and 9 in the rest of the world.
-pub delivery_days(zone: Int) -> Int = 0
+pub delivery_days(zone: Int) -> Int
+  requires zone >= 1 and zone <= 3
+=
+  if zone == 1
+    2
+  else if zone == 2
+    4
+  else
+    9
 
```

The precondition is optional for the examples to pass, but it states the rule: a zone the store does not ship to has no delivery time, and a call with one does not check.
:::
::::

::::exercise
**Exercise 2: a promotion for members.** Members pay 300 cents less for shipping. Write `member_discount(charge)`, and print a sixth line of the report, for order 1047, with the charge of order 1044 at the members' price. The start package ends with:

```una include="exercises/2/start/src/shipping.una#L114-L123" title="exercises/2/start/src/shipping.una"
--- A promotion for members: 300 cents off the charge.
pub member_discount(charge: Int) -> Int = charge

example "members pay 300 cents less"
  do promoted(3_090, promotion: member_discount)
  expect result == 2_790

example "a member never pays less than nothing"
  do promoted(200, promotion: member_discount)
  expect result == 0
```

:::hint
*Hint:* the promotion only subtracts. `promoted` already keeps the result between 0 and the charge, so the second example passes once the first does.
:::

Check your answer with `una test .`, then `una run .` for the new line, `order 1047: 27.90`.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Give `member_discount` its body, and print order 1047 in `main`:

```diff include="exercises/2/start..exercises/2/answer:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -76,2 +76,4 @@
   show(1046, charge: members)
+  let member = promoted(charge, promotion: member_discount)
+  show(1047, charge: member)
 
@@ -114,3 +116,3 @@
 --- A promotion for members: 300 cents off the charge.
-pub member_discount(charge: Int) -> Int = charge
+pub member_discount(charge: Int) -> Int = charge - 300
 
```

`member_discount` may return a negative number for a small charge, and that is fine: the promise not to charge less than nothing belongs to `promoted`, which every promotion goes through.
:::
::::

::::exercise
**Exercise 3: two promotions in a row.** Write `both(first, second)`, which returns a new promotion: `first`, then `second` on what `first` gives. The start package ends with:

```una include="exercises/3/start/src/shipping.una#L114-L123" title="exercises/3/start/src/shipping.una"
--- A promotion made of two: `first`, then `second` on what `first` gives.
pub both(first: fn(Int) -> Int, second: fn(Int) -> Int) -> fn(Int) -> Int = first

example "half off twice is a quarter, rounded up each time"
  do promoted(3_090, promotion: both(half_off, second: half_off))
  expect result == 773

example "the second promotion applies to what the first gives"
  do both(half_off, second: fn(cents) -> cents - 300)(3_090)
  expect result == 1_245
```

:::hint
*Hint:* the result is a function, so the body is a lambda. It may call `first` and `second`, which it captures.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Return a lambda that applies both:

```diff include="exercises/3/start..exercises/3/answer:src/shipping.una" context="1" title="src/shipping.una"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -114,3 +114,3 @@
 --- A promotion made of two: `first`, then `second` on what `first` gives.
-pub both(first: fn(Int) -> Int, second: fn(Int) -> Int) -> fn(Int) -> Int = first
+pub both(first: fn(Int) -> Int, second: fn(Int) -> Int) -> fn(Int) -> Int = fn(charge) -> second(first(charge))
 
```

`both(half_off, second: half_off)` is itself a promotion, so `promoted` accepts it like any other. The second example calls the returned function at once, `both(…)(3_090)`: 3090 halved is 1545, less 300 is 1245.
:::
::::

## 3.11 Recap

:::recap
- A header lists each parameter with its type, and the result type. Types in a header are never inferred.
- Label every argument after the first. A name equal to the parameter's name counts as its label.
- Use the short form for a function with no clauses and a one-line body, and the long form for the rest. `una fmt .` writes the right one.
- `requires` is what callers must provide, and `ensures` what the function guarantees. Callers rely on the header alone.
- `if` gives a value; both branches have one of the same type, and an `if` that gives a value has an `else`.
- A `pub` function declares its `uses`. A private one may leave them out, and `una contract` shows what the checker inferred.
- Pass a named function for a rule worth naming and testing, and a lambda for a one-line rule at the call.
:::

## 3.12 Reference

:::reference
- Construct pages: [functions: forms, clauses, labels, method calls, lambdas](/docs/language/functions/), [`requires`](/docs/language/functions/requires/), [`ensures` and `result`](/docs/language/functions/ensures/), [`if` and blocks](/docs/language/control-flow/), [`uses`](/docs/language/capabilities/uses/), [canonical form](/docs/language/canonical-form/)
- Guides: [write a contract and read a counterexample](/docs/guides/contracts-and-proofs/)
- Commands: [`una contract`](/docs/cli/contract/), [`una fmt`](/docs/cli/fmt/), [`una fix`](/docs/cli/fix/)
- Standard library: [the prelude](/docs/std/) (`min`, `max`)
- Diagnostics: [U2001](/docs/errors/U2001/), [U2004](/docs/errors/U2004/), [U2005](/docs/errors/U2005/), [U2010](/docs/errors/U2010/), [U3004](/docs/errors/U3004/), [U5001](/docs/errors/U5001/), [U7001](/docs/errors/U7001/)
- Specification: [functions and contracts](/docs/spec/04-functions-and-contracts/), [verification](/docs/spec/12-verification/), [canonical form](/docs/spec/15-canonical-form/), [the standard library](/docs/spec/14-standard-library/)
:::
