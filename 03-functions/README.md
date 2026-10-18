---
learn: "3"
title: Functions
editions: ["0.2"]
codes: [U0101, U2001, U2004, U2005, U2010, U2011, U3001, U3003, U3004, U5001, U7001]
time: 50
builds: A shipping quote for each order of the day, by weight and zone, with promotions passed in as functions
prerequisites: ["1", "2"]
template: 2
nav: ["Parameters, labels and results", "Two forms and clauses", "if", "pub and inferred headers", "Functions as values and lambdas", "Day-to-day: shipping quotes", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
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

- declare parameters and results, call with labeled arguments, and let a function call itself;
- choose between the short and the long form, and add `requires` and `ensures` clauses;
- choose a value with `if`, on one line or over several, and see what each branch knows;
- tell what a public header must declare from what the checker infers for a private one;
- pass a function, or a lambda written in place, as a value.
:::

## Why it works this way

In many languages a function's signature tells only part of the story. Arguments are matched by position, so `quote(3980, 1200, 1)` is accepted by the tool that turns the program into one the computer runs, whatever order the parameters have, and a swap of two numbers is a bug no tool sees. Whether the function writes to a log or a database is visible only in its body. Its promises, such as "never negative", live in a comment that no tool checks.

Una puts the whole story in the header, and checks it:

:::steps
1. **Arguments carry their parameters' names.** Every argument after the first is written `name: value`, so a call says what each value means.
2. **A public header declares its effects.** A `pub` function that prints says `uses @console: …`. A private function may leave it out, and the checker infers it and shows it to you.
3. **Promises are clauses.** `requires` states what a caller must provide, and `ensures` what the function guarantees. The verifier, the part of `una check` that proves facts about a program before it runs, proves both, and a caller relies on the header alone.
4. **A function is a value.** It can be passed to another function, so a rule that varies, such as a promotion, is a parameter with a type of its own.
:::

> [!KEY]
> A caller of a Una function needs only its header. The names, the types, the effects and the promises are all there, and the checker makes sure the body keeps them.

## 3.1 Parameters, labels and results

### What a function is

A **function** is a named piece of work that you can ask for again and again. Think of the price list behind a shop counter: "a line costs the unit price times the number of units". The clerk does not need a new rule for every customer. The rule takes the numbers of this sale, and gives back the total. A function is a rule like that, written down once, with a name.

A few words name its parts, and the rest of this chapter uses them:

- A **parameter** is a name for a value the function needs, such as `unit_cents` or `units`. Each parameter has a **type**: the set of values it may hold, such as `Int` for whole numbers or `Text` for texts ([chapter 2](/learn/values/)).
- The **result** is the one value the function gives back. It has a type too.
- The **header** is the first line: the function's name, its parameters with their types, and the type of its result. Later sections add more lines to it, before `=`.
- The **body** comes after `=`: how the function computes its result from its parameters.
- A **call** asks for the function's work: `line_total(1_990, units: 2)`. The code that writes the call is the **caller**, and the values it passes are the **arguments**. Inside the body, each parameter holds the argument the caller passed for it.

[Section 1.5](/learn/hello/#s1-5) wrote your first functions with these words. This section goes further: each part of a header, every form of a call, and the rules that every call follows.

### Why programs are split into functions

Here is a program that prices three lines of an order, with 10 percent off each line, all in `main`:

```una include="steps/01-no-function/src/receipt.una" title="steps/01-no-function/src/receipt.una" verified="check, run"
module receipt

--- Prints what three lines of an order cost, with 10 percent off each line.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamps = 1_990 * 2 * 90 / 100
  let rugs = 4_500 * 3 * 90 / 100
  let mugs = 1_250 * 4 * 90 / 100
  @console.print("lamps {lamps}, rugs {rugs}, mugs {mugs}")
```

`una run .` prints:

```text include="steps/01-no-function/expected/output.txt"
lamps 3582, rugs 12150, mugs 4500
```

The numbers are right, but the program has three problems:

1. **The rule is written three times.** "Price times units, less 10 percent" appears on three lines. To change the discount to 15 percent, you must change three places, and missing one gives a receipt that is wrong on one line only.
2. **The rule has no name.** A reader sees `1_990 * 2 * 90 / 100` and must work out what it means. Nothing in the code says "this is the price of a discounted line".
3. **The rule cannot be tested alone.** An example ([chapter 1](/learn/hello/#s1-6)) calls a function and checks what it returns. A computation buried in `main` has nothing to call.

A function solves all three. You write the rule once, give it a name, and call it wherever it applies.

### How to write a function

Each step of this chapter is a package, as in [chapter 1, Hello, Una](/learn/hello/#s1-1): a directory with `una.toml`, `verification.lock` and the module under `src/`. Copy `verification.lock` from chapter 1, or take each step's package, whole, from the chapter's download, `03-functions.tar.gz`. Then run `una check .` and `una run .` in the package's directory.

Here is the rule of the receipt as a function, with its parts named:

:::steps
```una include="steps/02-parameters/src/lines.una#line_total" title="steps/02-parameters/src/lines.una"
--- What `units` units cost at `unit_cents` cents each.
pub line_total(unit_cents: Int, units: Int) -> Int = unit_cents * units
```

1. **`--- What …`.** A doc comment, which [chapter 1](/learn/hello/#s1-5) introduced: what the function does, for a reader and for the tools.
2. **`pub`.** The function can be called from other modules too. [Section 3.4](#s3-4) explains it; without `pub`, only its own module may call it.
3. **`line_total`.** The function's name, in lowercase words joined by `_`. Name a function for what it gives back or does.
4. **`(unit_cents: Int, units: Int)`.** The parameters, in parentheses and separated by commas. Each one is a name, a colon, and its type.
5. **`-> Int`.** The arrow, then the type of the result.
6. **`= unit_cents * units`.** The body. Its value is the result: here, the product of the two parameters.
:::

Every type in a header is written by you. Una never guesses the type of a parameter or of a result, so the header alone tells a caller what to pass and what comes back, and the checker holds every call to it.

#### A function with no parameters

A function may take no values at all. Its parentheses stay, empty, in the header and at every call:

```una include="steps/03-calls/src/calls.una#opening_hour" title="steps/03-calls/src/calls.una"
--- The hour the store opens, on the 24-hour clock. A function with no parameters.
opening_hour() -> Int = 9
```

```una include="steps/03-calls/src/calls.una#L20" title="steps/03-calls/src/calls.una"
  @console.print("opens at {opening_hour()}:00")
```

```text include="steps/03-calls/expected/output.txt#L1"
opens at 9:00
```

A call is `opening_hour()`. Without the parentheses, `opening_hour` names the function without calling it, which [section 3.5](#s3-5) puts to use.

#### A function that gives back nothing useful: `Unit`

Some functions are called for what they do, not for a value. `main` prints, and has nothing to give back, so its result type is `Unit`. `Unit` has one value, `unit`, which carries no information. Every `main` in this book is `pub main() -> Unit`.

### How to call a function: labels

A call is the function's name and its arguments in parentheses. In Una, an argument usually carries its parameter's name, followed by a colon. That name is the argument's **label**. The rule is short:

- the first argument may go without a label;
- every other argument carries one.

The module `lines` shows each form of a call:

:::steps
```una include="steps/02-parameters/src/lines.una" title="steps/02-parameters/src/lines.una" verified="check, run"
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

1. **`line_total(1_990, units: 2)`.** The first argument goes without a label and fills the first parameter, `unit_cents`. The second carries `units:`.
2. **`line_total(4_500, units)`.** A name equal to the parameter's name counts as its label. `units` here means `units: units`. This is called **punning**.
3. **`discounted(1_250, percent: 10, units: 4)`.** Labeled arguments may come in any order, since each says which parameter it is for.
4. **`line_total(unit_cents, units: units)` inside `discounted`.** A function may call another, with the same rules. Here the body of `discounted` passes its own parameters on.
:::

`una run .` prints:

```text include="steps/02-parameters/expected/output.txt"
lamps 3980, rugs 13500, mugs 4500
```

#### One argument

A call with one argument may leave out the label, as `half(1_990)` does: there is nothing to confuse the argument with. Writing it, `half(cents: 1_990)`, is allowed too.

#### Two or more arguments

The first argument fills the first parameter, with or without a label. Every other argument must say which parameter it fills. The rule makes a call readable on its own, without a look at the header, and it makes a swap of two values visible where it happens: `line_total(2, units: 1_990)` reads as wrong at a glance.

#### Labels in any order

After the first argument, the labeled ones may come in any order: `discounted(1_250, percent: 10, units: 4)` and `discounted(1_250, units: 4, percent: 10)` are the same call. Write them in the order that reads best at the call.

#### Punning: a name that matches

When the value you pass is a name equal to the parameter's name, the name is its own label. `line_total(4_500, units)` is `line_total(4_500, units: units)`. Punning works from the second argument on. A first argument always fills the first parameter, whatever its name.

#### A call inside a call

An argument can be any expression that only computes, including another call. The inner call runs first, and its result becomes the argument. A call that prints or can fail is not an argument: it goes on a line of its own, or after `let`, and the checker reports U3013 otherwise ([chapter 6](/learn/failure/) shows it):

```una include="steps/03-calls/src/calls.una#half" title="steps/03-calls/src/calls.una"
--- Half of an amount, rounded down. A function with one parameter.
half(cents: Int) -> Int = cents / 2
```

```una include="steps/03-calls/src/calls.una#L21-L22" title="steps/03-calls/src/calls.una"
  @console.print("half of 1990: {half(1_990)}")
  @console.print("half of two lamps: {half(line_total(1_990, units: 2))}")
```

```text include="steps/03-calls/expected/output.txt#L2-L3"
half of 1990: 995
half of two lamps: 1990
```

In `half(line_total(1_990, units: 2))`, `line_total` gives 3980, and `half` receives 3980. Una evaluates arguments from left to right, in the order you wrote them.

### Method syntax

A call can also be written with its first argument in front, followed by a dot: `1_990.half` is `half(1_990)`, and `1_990.line_total(units: 3)` is `line_total(1_990, units: 3)`. This is **method syntax**, and [chapter 2](/learn/values/#s2-3) used it for the text functions of the **prelude**, the functions every module has without asking, as in `raw.trim`. A call of one argument may also drop its empty parentheses: `1_990.half`.

```una include="steps/03-calls/src/calls.una#L23" title="steps/03-calls/src/calls.una"
  @console.print("method syntax: {1_990.half}, {1_990.line_total(units: 3)}")
```

```text include="steps/03-calls/expected/output.txt#L4"
method syntax: 995, 5970
```

Both forms are the same call, and the checker treats them alike. Use method syntax where it reads as a chain of steps on one value, as `raw.trim.to_upper` does, and the plain form elsewhere. A value can also have **fields**, named parts of a record, such as the city of an address ([chapter 4](/learn/kinds/#s4-1)); when the value has a field of the same name, the dot reads the field instead.

### Lines of an order

Back to the receipt. With `line_total` and `discounted`, each line of the order is one call, and the rules are written once:

```una include="steps/02-parameters/src/lines.una#discounted" title="steps/02-parameters/src/lines.una"
--- What a line costs with `percent` off its total, rounded down to a whole cent.
pub discounted(unit_cents: Int, units: Int, percent: Int) -> Int = line_total(unit_cents, units: units) * (100 - percent) / 100
```

`discounted` builds on `line_total`: it asks for the line's total, then takes `percent` off. To change how a line is totaled, you change `line_total`, and `discounted` follows. To test the discount, an example calls `discounted(1_250, percent: 10, units: 4)` and expects 4500. Each function is small, named for what it gives back, and usable on its own.

### How a call behaves

#### The checker matches every argument

Before a program runs, `una check .` matches each argument with a parameter. It reports a label that names no parameter, a second argument without a label, a parameter that gets no argument, and an argument too many. Here the second argument says `count:`, a label `line_total` does not have:

```diff include="steps/02-parameters..steps/04-unknown-label:src/lines.una" context="1" title="src/lines.una"
--- a/src/lines.una
+++ b/src/lines.una
@@ -12,3 +12,3 @@
 =
-  let lamps = line_total(1_990, units: 2)
+  let lamps = line_total(1_990, count: 2)
   let units = 3
```

```text include="steps/04-unknown-label/expected/rendered.txt"
[U2005] Error: `line_total` has no parameter `count`
    ╭─[ src/lines.una:13:33 ]
    │
 13 │   let lamps = line_total(1_990, count: 2)
    │                                 ──┬──
    │                                   ╰──── `line_total` has no parameter `count`
    │
    │ Help: repair 1: the parameters that no other argument gives are `units`
    │
    │ Note: run `una explain U2005` for an explanation
────╯
```

Read the diagnostic from the top. The first line gives the code, U2005, and names the problem. The marks under line 13 point at the label the checker could not match. The help line lists the parameters that no argument fills yet, here `units`: the label the call meant. [A second argument without its label](#a-second-argument-without-its-label-u2004), in Common mistakes, shows the error for a missing label, and its repair, which `una fix .` applies for you.

#### A parameter is a name for a value

Inside the body, a parameter is a plain name, like one bound with `let` ([chapter 2](/learn/values/#s2-4)): it holds the argument for the whole call, and the body cannot assign it a new value. The caller's value is not changed by the call. A function gives back what it computes as its result, and that is all a plain call can change. From edition 0.2, a parameter may also be declared `edit`, as in `bump(edit cents: Int)`: such a parameter is passed in and out, and the caller's binding receives the value the body leaves in it. [Section 12.2](/learn/memory-and-concurrency/#s12-2) teaches it; every parameter in this chapter is a plain one.

#### A function may call itself

A body may call the function it belongs to. This is **recursion**: the function solves a small part of the problem, and calls itself for the rest. `marked_down` takes 10 percent off a price once a week. Its body uses `if`, which [section 3.3](#s3-3) covers: `if weeks <= 0 then cents else …` gives `cents` when no week is left, and the expression after `else` otherwise.

```una include="steps/03-calls/src/calls.una#marked_down" title="steps/03-calls/src/calls.una"
--- The price after `weeks` weekly markdowns of 10 percent, each one rounded down. The function
--- calls itself, with one week fewer, until no week is left.
marked_down(cents: Int, weeks: Int) -> Int = if weeks <= 0 then cents else marked_down(cents * 90 / 100, weeks: weeks - 1)
```

```una include="steps/03-calls/src/calls.una#L24" title="steps/03-calls/src/calls.una"
  @console.print("after 3 weeks of markdowns: {marked_down(10_000, weeks: 3)}")
```

```text include="steps/03-calls/expected/output.txt#L5"
after 3 weeks of markdowns: 7290
```

Follow the calls. `marked_down(10_000, weeks: 3)` is not the end, so it calls `marked_down(9_000, weeks: 2)`, which calls `marked_down(8_100, weeks: 1)`, which calls `marked_down(7_290, weeks: 0)`. That call has no week left, so it answers `7290`, and each call before it gives that answer back. Every call has one week fewer, so the calls end. A recursion that never reaches its stopping case would call itself until the run runs out of room, which Una reports as U6003 when the program runs. For most work over a list, a loop ([chapter 5](/learn/collections/#s5-2)) is the clearer choice.

### When to write a function

:::decide
**Which to use:**

| You have… | Write |
| --- | --- |
| A rule used in more than one place | A function, called wherever the rule applies |
| A rule with a name in the business, such as "line total" or "free shipping" | A function with that name, even if it is called once |
| A computation you want to test on its own | A function, and an example that calls it |
| A value computed once, used a few lines later | A `let` inside the body, not a function |
| A step that repeats over a list | A loop, or a function over the list ([chapter 5](/learn/collections/)) |
:::

Name parameters for what they mean to a caller: `unit_cents` and `units` read well at the call, where `a` and `b` would not. A good name and a label together make a call explain itself: `discounted(1_250, percent: 10, units: 4)`.

### Check yourself: calls

`lines` declares `line_total(unit_cents: Int, units: Int)` and `discounted(unit_cents: Int, units: Int, percent: Int)`. Which of these calls check, and what does each one that checks give?

1. `line_total(300, units: 5)`
2. `line_total(units: 5, unit_cents: 300)`
3. `discounted(1_000, percent: 50, units: 2)`
4. `line_total(300, 5)`

:::answer Show the answer
Calls 1, 2 and 3 check. Call 1 gives 1500. Call 2 labels both arguments, so their order does not matter, and it gives 1500 too. Call 3 gives 1000: the line costs 2000, less 50 percent. Call 4 does not check: its second argument has no label, which is U2004.
:::

`main` in `calls` ends with one more line:

```una include="steps/03-calls/src/calls.una#L25" title="steps/03-calls/src/calls.una"
  @console.print("two weeks from 1000: {marked_down(1_000, weeks: 2)}")
```

Predict what it prints.

:::answer Show the answer
```text include="steps/03-calls/expected/output.txt#L6"
two weeks from 1000: 810
```

810: the first call takes 10 percent off 1000, which gives 900, and calls itself with one week left. The second takes 10 percent off 900, which gives 810, and calls itself with no week left, which answers 810.
:::

## 3.2 Two forms, and clauses

### What the two forms are

A function's body can be a single expression, such as `cents / 2`, or several lines that name values on the way to the result. An **expression** is a piece of code that gives a value: `2`, `cents / 2` and `line_total(1_990, units: 2)` are expressions. Una writes each function in one of two layouts, its **forms**:

- The **short form** puts the whole function on one line: the header, `=`, and an expression. `half(cents: Int) -> Int = cents / 2`.
- The **long form** puts the header on its first line, then any **clauses**, one per line and indented, then `=` alone on its line, then the body, indented by two spaces.

A **clause** is a line of the header that says more about the function than its parameters and result: `uses`, from [chapter 1](/learn/hello/#s1-3), says what the function may do outside the program, and this section adds `requires` and `ensures`, which state its promises.

### Why one canonical form

In many languages the same function can be laid out in a dozen ways, and a team spends review time on line breaks. Una has one layout for each function, its **canonical form**: the short form when the function has no clauses and its body is one line, and the long form for every other function. `una fmt .` writes it, and `una check .` reports any other layout as U7001 ([chapter 1](/learn/hello/#s1-2)).

So you never decide the form by taste. A function's form follows from what it holds, and every function in every Una program reads the same way.

> [!TIP]
> Canonical form is not a style to learn by heart: it is what `una fmt` writes. Write a function in the layout that comes to you, run `una fmt .`, and read the form it chose.

### How to write the short form

`name(parameters) -> Type = expression`, on one line, with nothing after it:

```una include="steps/05-forms/src/fees.una#half" title="steps/05-forms/src/fees.una"
--- Half of an amount, rounded down. No clauses and a body of one line: the short form.
pub half(cents: Int) -> Int = cents / 2
```

The expression after `=` is the result. It may be as long as it needs, on one line: canonical form has no line width, so a long expression stays on one line rather than wrapping. When it no longer reads well on one line, name its parts in a block, in the long form.

### How to write the long form

The long form has three parts, in this order, each on its own lines:

1. The header line: `name(parameters) -> Type`, with nothing after the type.
2. The clauses, if any, each indented by two spaces.
3. `=` alone at the start of a line, then the body, indented by two spaces.

#### A body of several lines: a block

A body over several lines is a **block**: some lines that name values with `let` ([chapter 2](/learn/values/#s2-4)), and a last line that gives the block's value. The value of the last line is the result of the function. Una has no `return`: the last line is always the answer.

```una include="steps/05-forms/src/fees.una#parcel_rate" title="steps/05-forms/src/fees.una"
--- The rate of a parcel of `grams` grams: 450 cents for the first kilogram, and 250 more
--- for each kilogram or part of one after it. A body of several lines needs the long form.
pub parcel_rate(grams: Int) -> Int
  requires grams > 0
  ensures result >= 450
=
  let kilos = (grams + 999) / 1_000
  450 + (kilos - 1) * 250
```

The body first names `kilos`, the number of started kilograms: adding 999 grams before dividing by 1000 turns 1 to 1000 grams into one kilogram, and 1001 to 2000 into two. Its last line, `450 + (kilos - 1) * 250`, is the rate. A long form without clauses is also allowed, when the body is a block: the header, `=`, and the block.

#### Clauses between the header and `=`

Clauses sit between the header line and `=`, in a fixed order: every `requires`, then every `ensures`, then every `uses`, then `fails`, the clause of [chapter 6](/learn/failure/) that names how a function can fail, then `derived from`, the clause of [section 7.5](/learn/contracts/#s7-5) that names the rule a function implements. A header with its clauses in another order does not check (U0102). A function with any clause takes the long form, even when its body is one line, as `with_card_fee` does in the next example.

### Clauses: `requires` and `ensures`

Two clauses state a function's promises, the two halves of an agreement between the function and its callers:

- `requires p` is a **precondition**: a condition on the parameters that every caller must make true. A **condition** is an expression that is `true` or `false` ([chapter 2](/learn/values/#s2-2)). The body may rely on it.
- `ensures q` is a **postcondition**: a condition on the result, named `result` inside the clause, that the function guarantees whenever it returns. Every caller may rely on it.

The **verifier**, the part of `una check` that proves facts about the program without running it, checks both before the program runs: each `ensures` against the body, for every input that meets the `requires`, and each `requires` at every call. When it finds an input that breaks one, it reports U5001 with that input, a **counterexample**, as [chapter 2](/learn/values/#s2-3) showed for a cut text.

#### Why a rate needs a precondition

Take `parcel_rate` without its `requires` line. Its promise, `ensures result >= 450`, says that no parcel ships for less than the lowest rate:

```diff include="steps/05-forms..steps/06-no-requires:src/fees.una" title="src/fees.una" context="1"
--- a/src/fees.una
+++ b/src/fees.una
@@ -14,3 +14,2 @@
 pub parcel_rate(grams: Int) -> Int
-  requires grams > 0
   ensures result >= 450
```

```text include="steps/06-no-requires/expected/rendered.txt#L1-L10,L18"
[U5001] Error: postcondition of `parcel_rate` is refuted
    ╭─[ src/fees.una:18:3 ]
    │
 15 │   ensures result >= 450
    │           ──────┬──────
    │                 ╰──────── ensures clause
    │
 18 │   450 + (kilos - 1) * 250
    │   ───────────┬───────────
    │              ╰───────────── postcondition of `parcel_rate` is refuted
    │ Note 2: counterexample: grams = -999, result = 200
```

The verifier found a weight that breaks the promise: `grams = -999`. A parcel of minus 999 grams makes `kilos` 0, and the rate 200. No parcel weighs less than nothing, but nothing in the function said so, and a caller could pass such a value. `requires grams > 0` says so: it rules out every weight of zero or below, and with it the promise holds.

### Fees in both forms

The module `fees` shows both forms, and both clauses:

:::steps
```una include="steps/05-forms/src/fees.una" title="steps/05-forms/src/fees.una" verified="check, run"
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
  @console.print("1001 g: {parcel_rate(1_001)}, 2000 g: {parcel_rate(2_000)}")
```

1. **`half`.** No clauses and a body of one line: the short form.
2. **`with_card_fee`.** One `ensures` clause, so the long form, even though its body is one line. `result == cents + 50` promises the exact answer.
3. **`parcel_rate`.** A precondition, a postcondition, and a body of two lines.
4. **`requires grams > 0` and `ensures result >= 450`.** From the precondition, the verifier proves that `kilos` is at least 1, so the rate is at least 450.
:::

`una run .` prints:

```text include="steps/05-forms/expected/output.txt#L1-L3"
half of 1990: 995
with the card fee: 2040
500 g: 450, 2300 g: 950
```

Each call in `main` passes a weight above zero, so the verifier proves `requires grams > 0` at each one.

### A promise the body does not keep

A promise the body does not keep does not check. Raise the promised minimum to 500:

```diff include="steps/05-forms..steps/07-promise:src/fees.una" title="src/fees.una" context="0"
--- a/src/fees.una
+++ b/src/fees.una
@@ -16 +16 @@
-  ensures result >= 450
+  ensures result >= 500
```

```text include="steps/07-promise/expected/rendered.txt#L1-L10,L18"
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

Read the diagnostic from the top. The first line says which promise failed: the postcondition of `parcel_rate`. The first mark points at the clause, line 16, and the second at the line of the body that computes the result, line 19. The last line is the counterexample: a parcel of 1000 g, for which the body returns 450, which breaks the promise of 500. Either the body or the clause is wrong, and the verifier cannot tell which: that is your decision. [Chapter 7, Contracts and the verifier](/learn/contracts/), covers clauses in depth.

### How a body behaves

#### The value of a block is its last line

A block runs its lines in order, from the top, and its value is the value of its last line. Every line before the last is a **statement**: a line that does something, such as naming a value with `let` or printing, rather than giving the block's value.

#### A value nobody uses

A statement must not give a value that is then thrown away. A call of `with_card_fee` on a line of its own, whose result nobody names, is a mistake the checker catches:

```diff include="steps/05-forms..steps/08-unused-value:src/fees.una" title="src/fees.una" context="1"
--- a/src/fees.una
+++ b/src/fees.una
@@ -24,2 +24,3 @@
 =
+  with_card_fee(1_990)
   @console.print("half of 1990: {half(1_990)}")
```

```text include="steps/08-unused-value/expected/rendered.txt#L1-L6"
[U2011] Error: this statement has type `Int`, and only `Unit` values can be discarded; bind the value with `let`
    ╭─[ src/fees.una:25:3 ]
    │
 25 │   with_card_fee(1_990)
    │   ──────────┬─────────
    │             ╰─────────── this statement has type `Int`, and only `Unit` values can be discarded; bind the value with `let`
```

The message says what to do: bind the value with `let`, or remove the line. Only a statement of type `Unit`, such as a `print`, may stand alone, since it has no value to lose. A call whose result is dropped is almost always a slip: the work was done, and its answer went nowhere.

#### Names inside a body belong to it

A name bound with `let` in a body exists from its line to the end of the body, and only there. `kilos` in `parcel_rate` means nothing in `half` or in `main`. Two functions may each have a `let kilos` without any conflict, and a parameter's name is local to its function in the same way.

#### Clauses are checked, not run

A `requires` or `ensures` clause costs nothing when the program runs. The verifier proves it once, during `una check`, and the program runs without testing it again. A clause that cannot be proven stops the check, so a program that runs has every one of its clauses proven.

### Short or long, and when to add a clause

:::decide
**Which to use:**

| The function… | Write |
| --- | --- |
| Has no clauses, and its body is one expression | The short form |
| Needs a few named steps to reach its result | The long form, with a block |
| Is only correct for some arguments, such as a weight above zero | The long form, with `requires` |
| Gives a result its callers need to rely on, such as "never negative" | The long form, with `ensures` |
| Has no condition worth stating | No clause: the short form, if its body fits on a line |
:::

A clause belongs where a caller would otherwise have to read the body to use the function safely. `requires grams > 0` tells every caller what to pass. `ensures result >= 450` tells every caller what comes back, so a caller that sums rates knows the sum is at least 450 per parcel, without reading a line of `parcel_rate`.

### Check yourself: forms

Which form does each function take? Write the canonical layout of each, then compare with the answer.

1. A function `double(cents: Int) -> Int` whose body is `cents * 2`.
2. The same function, with `requires cents >= 0`.
3. A function `boxes(units: Int) -> Int` that names `full = units / 6`, then gives `full + 1`.

:::answer Show the answer
1. The short form, `double(cents: Int) -> Int = cents * 2`: no clauses, one line.
2. The long form, since it has a clause: the header, then `  requires cents >= 0` on its own line, then `=` alone, then `  cents * 2`.
3. The long form with a block: the header, `=`, then `  let full = units / 6` and `  full + 1`, each indented by two spaces.
:::

`main` in `fees` prints one more line, for two parcels close to a kilogram boundary:

```una include="steps/05-forms/src/fees.una#L28" title="steps/05-forms/src/fees.una"
  @console.print("1001 g: {parcel_rate(1_001)}, 2000 g: {parcel_rate(2_000)}")
```

Predict both rates before you open the answer.

:::answer Show the answer
```text include="steps/05-forms/expected/output.txt#L4"
1001 g: 700, 2000 g: 700
```

Both cost 700. A parcel of 1001 g has started its second kilogram, so `kilos` is 2: (1001 + 999) / 1000 is 2. A parcel of 2000 g fills two kilograms exactly: (2000 + 999) / 1000 is 2 too, rounded down. The first kilogram costs 450, and the second 250 more.
:::

## 3.3 Choosing a value: `if`

### What `if` is

`if` chooses between two values by a condition. Think of a sign at the till: "orders of 100.00 or more ship free; otherwise shipping is 4.90". The clerk checks one fact, and the answer is one of two prices. `if` writes that rule: `if goods >= 10_000 then 0 else 490`.

Three words name its parts:

- The **condition** is the expression after `if`: a `Bool`, `true` or `false` ([chapter 2](/learn/values/#s2-2)).
- A **branch** is one of the possible answers: the one after `then` when the condition is `true`, and the one after `else` when it is `false`.
- Only the branch the condition picks runs. The other is skipped.

In Una, `if` is an expression: like `2 + 3` or a call, it gives a value. You can put it wherever a value goes: as a function's body, after `let`, as an argument, or inside interpolation braces.

### Why a program chooses

A function without a choice answers every input the same way. Here is a product page that says how many units are left, with one sentence for every case:

```una include="steps/09-no-if/src/shelf.una" title="steps/09-no-if/src/shelf.una" verified="check, run"
module shelf

--- What a product page says about the stock of a product. One sentence for every case.
availability(on_hand: Int) -> Text = "only {on_hand} units left"

--- Prints what the product page says for four stock levels.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(availability(0))
  @console.print(availability(1))
  @console.print(availability(3))
  @console.print(availability(40))
```

`una run .` prints:

```text include="steps/09-no-if/expected/output.txt"
only 0 units left
only 1 units left
only 3 units left
only 40 units left
```

Only one line in four is right. "Only 0 units left" should say the product is out of stock, "only 1 units left" is bad English, and "only 40 units left" makes a full shelf sound scarce. The sentence depends on the number, and a single expression cannot say so. `if` can.

### How to write `if`

`if` has three forms: on one line, over several lines, and without `else`. The step for this part has a small function for each, and `main` prints one line for each function.

#### On one line: `if … then … else …`

`if condition then value else value`, all on one line. Both values are expressions:

```una include="steps/11-if-forms/src/choices.una#weight_class" title="steps/11-if-forms/src/choices.una"
--- Whether a parcel counts as heavy: an `if` on one line.
weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy" else "light"
```

```text include="steps/11-if-forms/expected/output.txt#L1"
heavy, light
```

2300 g is above 2000, so the condition is `true` and the result is `"heavy"`. 800 g is not, and the result is `"light"`.

#### More than two cases: `else if`

An `else` may hold another `if`. The conditions are tried in order, and the first one that holds gives the value. The last `else` catches every case no condition took:

```una include="steps/11-if-forms/src/choices.una#zone_name" title="steps/11-if-forms/src/choices.una"
--- The name of a shipping zone: an `else if` chain, still on one line.
zone_name(zone: Int) -> Text = if zone == 1 then "home" else if zone == 2 then "neighbors" else "world"
```

```text include="steps/11-if-forms/expected/output.txt#L2"
home, neighbors, world
```

#### Over several lines: a block in each branch

When a branch needs a few lines, write the `if` over several lines. The condition goes on the `if` line, with no `then`. Each branch is a block, indented by two spaces under its `if`, `else if` or `else`, and its value is its last line, as in a function's body ([section 3.2](#s3-2)):

```una include="steps/11-if-forms/src/choices.una#box" title="steps/11-if-forms/src/choices.una"
--- The box a parcel needs: an `if` over several lines, with a block in each branch.
box(grams: Int) -> Text
=
  if grams <= 500
    "envelope"
  else if grams <= 5_000
    let liters = grams / 250
    "box of {liters} liters"
  else
    "crate"
```

```text include="steps/11-if-forms/expected/output.txt#L3"
envelope, box of 8 liters, crate
```

The second branch names `liters` before its last line. A name bound inside a branch exists only in that branch.

#### Inside a larger expression

An `if` can be one part of a larger expression. It then goes in parentheses, which are required: without them the line does not parse (U0101), since the parser must see where the `if` ends:

```una include="steps/11-if-forms/src/choices.una#handling" title="steps/11-if-forms/src/choices.una"
--- The handling fee of an order: an `if` in parentheses, as one part of a sum.
handling(goods: Int) -> Int = 190 + (if goods >= 10_000 then 0 else 300)
```

```text include="steps/11-if-forms/expected/output.txt#L4"
490, 190
```

An order of 4500 cents pays 190 plus 300. An order of 12000 cents pays 190 plus 0.

#### Without `else`: a statement

In edition 0.2 and later, the edition of every package in this book, an `if` over several lines may leave out `else`. (In edition 0.1 every `if` has an `else`.) It then gives no value: it is a statement, whose lines run only when the condition holds. It is useful with a binding declared `let edit` ([chapter 2](/learn/values/#s2-4)), which its lines may assign:

```una include="steps/11-if-forms/src/choices.una#packing_note" title="steps/11-if-forms/src/choices.una"
--- A note for the packing slip: an `if` without `else`, which only runs its lines when the
--- condition holds.
packing_note(units: Int) -> Text
=
  let edit note = "standard"
  if units > 10
    note = "bulk, use a pallet"
  note
```

```text include="steps/11-if-forms/expected/output.txt#L5"
standard, bulk, use a pallet
```

For 4 units the condition is `false`, nothing happens, and `note` keeps `"standard"`. For 24 units the assignment runs. Loops in [chapter 5](/learn/collections/#s5-2) use this form at each turn. When you only need a value, prefer the forms with `else`: `let note = if units > 10 then "bulk, use a pallet" else "standard"` says the same in one line, with no binding to edit.

### Stock messages with `if`

Back to the product page. The module `stock` gives each stock level its own sentence:

:::steps
```una include="steps/10-if/src/stock.una" title="steps/10-if/src/stock.una" verified="check, run"
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

```text include="steps/10-if/expected/output.txt"
out of stock
only 1 unit left
only 3 units left
in stock
```

Compare with the page without `if`. Each stock level now gets the sentence that fits it, and the rule for each case is written once, where a reader looks for it.

### How `if` behaves

#### The condition is a `Bool`

The condition must be `true` or `false`. A number or a text is not a condition: `if on_hand then …` does not check, since 0 is not `false` in Una. Write the comparison you mean, `if on_hand > 0`.

#### Both branches give one type

The checker holds both branches of an `if` that gives a value to one type, the type the place of the `if` expects. A branch that returns a number where the function returns a text is reported at that branch, where the mistake is, not later where the value is used. [Branches of two types](#branches-of-two-types-u2001), in Common mistakes, shows the diagnostic.

#### An `if` that gives a value has an `else`

Whichever way the condition goes, a value is needed, so an `if` that gives one always has an `else`. Leave it out of the one-line form, and the line does not parse:

```diff include="steps/11-if-forms..steps/12-no-else:src/choices.una" title="src/choices.una" context="0"
--- a/src/choices.una
+++ b/src/choices.una
@@ -4 +4 @@
-weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy" else "light"
+weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy"
```

```text include="steps/12-no-else/expected/rendered.txt#L1-L6,L8"
[U0101] Error: unexpected end of line, expected `else`
   ╭─[ src/choices.una:4:65 ]
   │
 4 │ weight_class(grams: Int) -> Text = if grams > 2_000 then "heavy"
   │                                                                 ┬
   │                                                                 ╰── unexpected end of line, expected `else`
   │ Help: repair 1: an `if` with `then` needs `else`; to fail early, make the rest of the body its `else` branch, as in `if x < 0 then fail Broke else x`, or use the block form, whose `else` block holds the rest
```

The mark points at the end of the line, where `else` was expected. Add the `else` and its value.

#### Only the chosen branch runs

Una evaluates the condition, then only the branch it picks. The other branch is never evaluated, so it cannot divide by zero or call a function for nothing. This is what makes recursion stop: in `marked_down` ([section 3.1](#s3-1)), the branch that calls the function again is not evaluated once no week is left.

#### What a branch knows from its condition

Inside a branch, the verifier knows that the condition held, or, in the `else` branch, that it did not. That knowledge can prove what would otherwise fail. `per_unit` divides by `units`, and a division by a value that is not a literal must be proven safe ([chapter 2](/learn/values/#s2-1)):

```una include="steps/11-if-forms/src/choices.una#per_unit" title="steps/11-if-forms/src/choices.una"
--- The price of one unit of a pack. The division is in the branch where `units > 0` holds.
per_unit(pack_cents: Int, units: Int) -> Int = if units > 0 then pack_cents / units else 0
```

```text include="steps/11-if-forms/expected/output.txt#L6"
250, 0
```

The division sits in the branch where `units > 0` holds, so `units` is never 0 there. Weaken the condition to `units >= 0`, and the proof fails:

```diff include="steps/11-if-forms..steps/13-branch-facts:src/choices.una" title="src/choices.una" context="0"
--- a/src/choices.una
+++ b/src/choices.una
@@ -33 +33 @@
-per_unit(pack_cents: Int, units: Int) -> Int = if units > 0 then pack_cents / units else 0
+per_unit(pack_cents: Int, units: Int) -> Int = if units >= 0 then pack_cents / units else 0
```

```text include="steps/13-branch-facts/expected/rendered.txt#L1-L6,L8,L12"
[U5001] Error: division obligation `units != 0` is refuted
    ╭─[ src/choices.una:33:67 ]
    │
 33 │ per_unit(pack_cents: Int, units: Int) -> Int = if units >= 0 then pack_cents / units else 0
    │                                                                   ─────────┬────────
    │                                                                            ╰────────── division obligation `units != 0` is refuted
    │ Help: repair 1: guard the division with `if units != 0`
    │ Note 2: counterexample: units = 0
```

The counterexample, `units = 0`, is a value that passes the new condition and still divides by zero. The help line proposes a guard, which is exactly what the original condition was.

### One line, several lines, or `when`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Choose between two short values | `if c then a else b`, on one line |
| Choose among several cases, by conditions tried in order | `else if`, on one line or over several |
| Name values on the way to a branch's answer | `if` over several lines, with a block in each branch |
| Use a choice as one part of a larger expression | `(if c then a else b)`, in parentheses |
| Change an editable binding only when a condition holds | `if` without `else`, as a statement |
| Choose by the kind of value you hold, such as the zone a parcel ships to | `when`, in [chapter 4](/learn/kinds/#s4-3) |
:::

Choose the one-line form while both branches are short, and switch to several lines when a branch needs a name or the line stops reading at a glance. `una fmt .` keeps whichever form you wrote: both are canonical.

### Check yourself: `if`

`wrap_fee` prices gift wrapping:

```una include="steps/11-if-forms/src/choices.una#wrap_fee" title="steps/11-if-forms/src/choices.una"
--- The gift-wrapping fee of an order: nothing without a gift, 150 cents a unit, and 500 at most.
wrap_fee(units: Int, gift: Bool) -> Int = if not gift then 0 else if units > 3 then 500 else 150 * units
```

`main` prints `wrap_fee(2, gift: true)`, `wrap_fee(5, gift: true)` and `wrap_fee(5, gift: false)`. Predict the three values.

:::answer Show the answer
```text include="steps/11-if-forms/expected/output.txt#L7"
300, 500, 0
```

2 units as a gift take the last branch, 150 × 2 = 300. 5 units as a gift pass the second condition, `units > 3`, and pay the cap of 500. Without a gift, the first condition holds, and the other branches never run.
:::

## 3.4 `pub`, and the headers the checker infers

### What `pub` means

A **module** is one file of code, named by its `module` line ([chapter 1](/learn/hello/#s1-1)). A program can have many modules, and one module can use the functions of another. `pub`, short for public, decides which functions it may use:

- A function that starts with `pub` is **public**: any module may call it.
- A function without `pub` is **private**: only the functions of its own module may call it.

Think of a shop. The counter is public: customers walk up and ask for what is on the menu. The back room is private: the staff use it to get the work done, and no customer goes in. A module's public functions are its counter, and its private functions are its back room.

### Why a public header must say everything

The caller of a public function may live in another module, written by someone else, years later. That caller sees the header, not the body. So the header of a `pub` function must state everything a caller relies on:

- the type of every parameter and of the result, as every header does;
- every `uses`: what the function may do outside the program, such as print;
- the ways it can fail, with `fails`: a function that can fail, such as a lookup that may find nothing, names its possible failures in its header. [Chapter 6](/learn/failure/) covers them.

If a public header could leave out its `uses`, a function that looks like a pure computation could print, write files or send data, and nothing at the call would show it. Una does not allow that: a `pub` function that prints without `uses` does not check ([A public function that prints without `uses`](#a-public-function-that-prints-without-uses-u3004), in Common mistakes, shows the diagnostic).

A private function is different. Every one of its callers is in the same file, in view of whoever changes it. So Una lets a private function leave out its `uses`, and works them out for you.

### How to write `pub`

`pub` goes first, before the function's name: `pub to_order(on_hand: Int, target: Int) -> Int`. Everything else in the header is written as for any function. A private function simply leaves `pub` out: `show(sku: Text, units: Int) -> Unit`.

`pub` applies to other declarations too, with the same meaning, such as the **kinds** of [chapter 4](/learn/kinds/), the data types you declare yourself. `main` must be public: `una run` calls it from outside the module, and refuses a module without `pub main() -> Unit`.

### A private function's inferred `uses`

The module `restock` prints a restock list. It has a public function that computes, and a private function that prints. The computing one uses `max`, a function of the prelude: `max(a, b)` gives the larger of its two arguments.

:::steps
```una include="steps/14-inferred/src/restock.una" title="steps/14-inferred/src/restock.una" verified="check, run"
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

1. **`to_order`.** A public function with no `uses`: it cannot print, and it only computes. `max(target - on_hand, b: 0)` never orders fewer than none. Its second parameter is named `b`, hence the label.
2. **`show(sku: Text, units: Int) -> Unit = @console.print(…)`.** A private function that prints, with no `uses` in its header.
3. **`main` calls `show`.** `main` declares the console, so `show`, called from it, gets the console too.
:::

`una run .` prints:

```text include="steps/14-inferred/expected/output.txt"
LAMP-01: order 7
RUG-07: order 0
```

The checker has filled in what `show` left out. It sees that the body uses `@console.print`, and that every caller of `show` has the console to give. Working out such a missing part from the code around it is called **inference**, and the result is the **inferred** header.

### Reading the inferred header: `una contract`

`una contract` prints a function's full header, as a caller may rely on it. For `show`, the part the checker inferred is marked as such:

```sh
una contract restock.show
```

```text include="steps/14-inferred/expected/commands/contract.txt#L2-L3"
show(sku: Text, units: Int) -> Unit
  uses @console: Console[print] -- inferred
```

The `-- inferred` mark keeps the inference visible: a reviewer sees that `show` prints, even though its source does not say so.

### Authority in the build report

The build report, `una report .`, lists the **authority** of every function: what each one may do outside the program, declared or inferred. For this package, its authority part lists `restock.main` as public and `restock.show` as private and inferred, each with `@console: Console[print]`. A function with no authority, such as `to_order`, is not listed: it can only compute. A reviewer reads the effects of a whole package in one place, without opening a body.

### How inference behaves

#### Inference follows the calls

A private function's `uses` come from its body and from its callers: the checker gives it what its body needs, provided its callers have it to give. When no caller has it, there is nothing to infer. Here a public function, `print_list`, calls `show` but declares no `uses`:

```diff include="steps/14-inferred..steps/15-public-calls-private:src/restock.una" title="src/restock.una" context="1"
--- a/src/restock.una
+++ b/src/restock.una
@@ -10,2 +10,8 @@
 --- Prints the restock list of two SKUs.
+pub print_list() -> Unit
+=
+  show("LAMP-01", units: to_order(3, target: 10))
+  show("RUG-07", units: to_order(12, target: 10))
+
+--- Prints the restock list.
 pub main() -> Unit
@@ -13,3 +19,2 @@
 =
-  show("LAMP-01", units: to_order(3, target: 10))
-  show("RUG-07", units: to_order(12, target: 10))
+  print_list()
```

```text include="steps/15-public-calls-private/expected/rendered.txt#L1-L6,L8"
[U3001] Error: no caller of `show` binds `@console`, so its capability cannot be inferred
   ╭─[ src/restock.una:8:39 ]
   │
 8 │ show(sku: Text, units: Int) -> Unit = @console.print("{sku}: order {units}")
   │                                       ────┬───
   │                                           ╰───── no caller of `show` binds `@console`, so its capability cannot be inferred
   │ Help: repair 1: declare `uses @console: <capability>[print]` in the header; this states authority its callers are already charged for
```

The error is reported at the use of `@console` in `show`: no caller of `show` binds the console, so the checker cannot give it one. The help line proposes to declare it in `show`'s header; the fix that fits here is to add `uses @console: Console[print]` to `print_list`, the public function that prints through `show`.

#### Nothing is inferred at the module's boundary

A `pub` function writes its `uses` itself, always. A `pub` function that prints without `uses` is U3004: "this code declares no `uses`, so it is pure". So the inference saves lines inside a module, where every caller is in view, and never hides an effect from another module.

#### Types are never inferred in a header

The inference covers `uses`, and the `fails` of a private function ([chapter 6](/learn/failure/)). It never covers types. Every parameter and every result of every function, public or private, has its type written. A header that leaves out `-> Int` does not parse.

### Public or private

:::decide
**Which to use:**

| The function… | Make it |
| --- | --- |
| Is part of what the module offers other modules | `pub`, with a doc comment and its full header |
| Is called from `una run` | `pub`: `main` must be public |
| Is a helper used only inside its module | Private, and let its `uses` be inferred |
| Is private, but its effects deserve to be read in the source | Private, with its `uses` written: writing them is always allowed |
:::

Start private, and make a function `pub` when another module needs it. A private function can change freely, since all its callers are in view. A public one is a promise: changing its header can break callers you cannot see.

> [!NOTE]
> The rule is the same as in [chapter 1](/learn/hello/#s1-3): what a public function may do is in its header. Private functions are the module's own business, and the checker still knows exactly what each one does.

### Check yourself: `pub`

`restock` has three functions: `to_order` (public, no `uses`), `show` (private, prints) and `main` (public, `uses @console: Console[print]`). For each, answer two questions: may another module call it, and may it print?

:::answer Show the answer
- `to_order`: another module may call it; it may not print, since a public function without `uses` is pure.
- `show`: no other module may call it; it prints, with the console inferred from its caller, `main`.
- `main`: public, and it prints, as its `uses` says. `una run` calls it.

The authority part of `una report .` lists exactly the two that may print:

```text include="steps/14-inferred/expected/commands/report.txt#L6-L8"
authority:
  restock.main (pub): @console: Console[print]
  restock.show (private, inferred): @console: Console[print]
```
:::

## 3.5 Functions as values, and lambdas

### What a function value is

So far, a function was something you call. In Una, a function is also a **value**, like a number or a text: you can pass it to another function as an argument, name it with `let`, and get it back as a result. Think of a recipe card. You can follow it, but you can also hand the card to someone else and let them follow it when the time comes. Passing a function is handing over the card.

Two new terms name the parts:

- A **function type** is the type of a function value. `fn(Int) -> Int` is the type of every function that takes one `Int` and returns an `Int`, whatever its name.
- A **lambda** is a function written in place, without a name, where a value goes: `fn(cents) -> cents - 500`. (The name comes from mathematics; other books call it an anonymous function.)

### Why pass a function

A store keeps changing its promotions. Here are three, each written as its own function:

```una include="steps/16-no-lambdas/src/rules.una" title="steps/16-no-lambdas/src/rules.una" verified="check, run"
module rules

--- The price after the clearance rule, 500 cents off, kept between 0 and the price.
clearance_price(cents: Int) -> Int = max(0, b: min(cents - 500, b: cents))

--- The price after the rule "ends in 99", kept between 0 and the price.
ends_in_99_price(cents: Int) -> Int = max(0, b: min((cents + 1) / 100 * 100 - 1, b: cents))

--- The price after the members' rule, 20 percent off, kept between 0 and the price.
members_price(cents: Int) -> Int = max(0, b: min(cents * 80 / 100, b: cents))

--- Prints a price under three rules.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{clearance_price(2_050)} {ends_in_99_price(2_050)} {members_price(2_050)}")
  @console.print("{clearance_price(300)} {ends_in_99_price(300)} {members_price(300)}")
```

`una run .` prints:

```text include="steps/16-no-lambdas/expected/output.txt"
1550 1999 1640
0 299 240
```

Each function does two things: it applies its rule, and it keeps the result between 0 and the price, with `min` and `max` from the prelude ([section 3.4](#s3-4) introduced `max`; `min` gives the smaller of its arguments). The second part is the same in all three, copied. A fourth promotion means a fourth copy, and a fix to the clamping, such as a minimum price, must be made in every copy.

What differs between the three is only the rule. If the rule could be a parameter, the clamping would be written once, and each promotion would be just its rule. A function type makes that possible.

### How to write function values

#### A function type: `fn(Int) -> Int`

Write `fn`, the parameter types in parentheses, `->`, and the result type. A parameter of function type is declared like any other parameter, and called like any function:

```una include="steps/17-lambdas/src/pricing.una#priced" title="steps/17-lambdas/src/pricing.una"
--- A price after a pricing rule: a function from a price in cents to a price in cents.
pub priced(cents: Int, rule: fn(Int) -> Int) -> Int = rule(cents)
```

`rule` is a parameter whose value is a function. `rule(cents)` calls whatever function the caller passed.

#### Passing a named function

Pass a declared function by its name, without parentheses: `priced(2_050, rule: ends_in_99)`. With parentheses, `ends_in_99(2_050)` would call it, and pass its result, a number. Without them, the function itself is passed, to be called later by `priced`. The function's type must match the parameter's: `ends_in_99` takes an `Int` and returns an `Int`, so it fits `fn(Int) -> Int`.

#### A lambda

`fn(parameters) -> expression` writes a function in place:

```una include="steps/17-lambdas/src/pricing.una#L14" title="steps/17-lambdas/src/pricing.una"
  @console.print("{priced(2_050, rule: fn(cents) -> cents - 500)}")
```

`fn(cents) -> cents - 500` takes `cents` and gives `cents - 500`. Its parameter's type, `Int`, comes from the type of `rule`, so you need not write it. Its body is one expression, after `->`.

#### A lambda with its types written

Where nothing says what a lambda's parameters are, write their types, as in a header. A lambda named with `let` needs them:

```una include="steps/18-function-forms/src/promotions.una#L17-L18" title="steps/18-function-forms/src/promotions.una"
  let clearance = fn(cents: Int) -> cents - 500
  @console.print("clearance: {clearance(2_000)}")
```

```text include="steps/18-function-forms/expected/output.txt#L3"
clearance: 1500
```

`clearance` is now a name for a function, called like one: `clearance(2_000)`.

#### Several parameters

A function type may take several parameters, `fn(Int, Int) -> Int`, and a lambda then names each one. A function value is called with its arguments in order, with no labels, since its type gives its parameters no names:

```una include="steps/18-function-forms/src/promotions.una#line_price" title="steps/18-function-forms/src/promotions.una"
--- The price of a line under a rule for whole lines: a function of two parameters.
line_price(unit_cents: Int, units: Int, rule: fn(Int, Int) -> Int) -> Int = rule(unit_cents, units)
```

```una include="steps/18-function-forms/src/promotions.una#L13" title="steps/18-function-forms/src/promotions.una"
  @console.print("3 for 2: {line_price(1_990, units: 3, rule: fn(cents, units) -> cents * (units - units / 3))}")
```

```text include="steps/18-function-forms/expected/output.txt#L1"
3 for 2: 3980
```

The lambda prices "3 for 2": of 3 units, one is free, so the line pays 1990 × 2 = 3980.

#### A function that returns a function

The result type can be a function type too. Such a function builds functions:

```una include="steps/18-function-forms/src/promotions.una#percent_off" title="steps/18-function-forms/src/promotions.una"
--- A promotion that takes `percent` percent off: a function that returns a function.
percent_off(percent: Int) -> fn(Int) -> Int = fn(cents) -> cents * (100 - percent) / 100
```

```una include="steps/18-function-forms/src/promotions.una#L14-L16" title="steps/18-function-forms/src/promotions.una"
  let ten_off = percent_off(10)
  let quarter_off = percent_off(25)
  @console.print("10 off: {ten_off(2_000)}, 25 off: {quarter_off(2_000)}")
```

```text include="steps/18-function-forms/expected/output.txt#L2"
10 off: 1800, 25 off: 1500
```

`percent_off(10)` returns a lambda that takes 10 percent off, and `percent_off(25)` one that takes 25. The lambda uses `percent`, a parameter of the function that made it, and keeps its value after `percent_off` has returned.

### Pricing rules passed as values

The module `pricing` passes a named function and two lambdas to the same parameter:

:::steps
```una include="steps/17-lambdas/src/pricing.una" title="steps/17-lambdas/src/pricing.una" verified="check, run"
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
3. **`fn(cents) -> cents - 500`.** A lambda. Its parameter's type comes from the type of `rule`.
4. **`fn(cents) -> cents * markup / 100`.** A lambda that uses `markup`, a name from around it.
:::

`una run .` prints:

```text include="steps/17-lambdas/expected/output.txt"
1999
1550
2460
```

`priced` knows nothing about promotions: it applies whatever rule it is given. A new rule is a new function or a new lambda, and `priced` never changes. The day-to-day program of this chapter uses the same design to clamp every promotion in one place.

### How function values behave

#### Where a lambda gets its types

A lambda gets its parameter types from where it is used: the parameter it is passed to says `fn(Int) -> Int`, so `cents` is an `Int`. Bound with `let` on its own line, a lambda has no such place, and the checker asks for the type, with U2010 ([A lambda bound with `let`](#a-lambda-bound-with-let-u2010), in Common mistakes). Write `fn(cents: Int) -> …`, or pass the lambda straight to the function that uses it.

#### A lambda captures values

A lambda may use names from around it, such as `markup` or `percent`. It **captures** them: it keeps a copy of the value each one has when the lambda is made. A later assignment to a `let edit` binding does not reach a lambda made before it, and the lambda cannot assign the binding itself.

#### A function type without `uses` is pure

`fn(Int) -> Int` has no `uses`, so a function of that type cannot print, read the clock or touch anything outside the program. Pass a function that prints where such a type is expected, and the call does not check:

```diff include="steps/17-lambdas..steps/19-lambda-prints:src/pricing.una" title="src/pricing.una" context="1"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -8,2 +8,8 @@
 
+-- A rule that prints the price it is given. It is private, so its `uses` is inferred.
+logged(cents: Int) -> Int
+=
+  @console.print("pricing {cents}")
+  cents
+
 --- Prints a price under three rules.
@@ -12,3 +18,3 @@
 =
-  @console.print("{priced(2_050, rule: ends_in_99)}")
+  @console.print("{priced(2_050, rule: logged)}")
   @console.print("{priced(2_050, rule: fn(cents) -> cents - 500)}")
```

```text include="steps/19-lambda-prints/expected/rendered.txt#L12-L17"
[U3003] Error: this function uses `@console: ?[print]`, which the expected function type does not allow
    ╭─[ src/pricing.una:19:40 ]
    │
 19 │   @console.print("{priced(2_050, rule: logged)}")
    │                                        ───┬──
    │                                           ╰──── this function uses `@console: ?[print]`, which the expected function type does not allow
```

The mark points at `logged`, where it is passed: it uses `@console`, which `fn(Int) -> Int` does not allow. In `@console: ?[print]`, the `?` stands for the capability's type, `Console`, which the checker does not name in this message. (The checker also reports, at `logged`'s body, that no caller gives it the console, since it is only passed, never called from `main`.) So a promotion passed to `priced` is a pure function, whoever wrote it: its type guarantees it. When a function should accept a parameter that may print or fail, its header says so with `uses of` or `fails of` and the parameter's name: [section 6.1](/learn/failure/#s6-1) teaches `fails of`, and [section 8.4](/learn/capabilities/#s8-4) teaches `uses of`.

#### A lambda's body is one expression

A lambda holds one expression, on one line. A rule that needs several lines, a `let` or a clause is a named function, passed by its name. A named function can also have its own examples, which a lambda cannot.

#### Functions cannot be compared

`==` compares two values of the same type, but not two functions: whether two functions always give the same answer is not something a program can decide. Comparing two functions with `==` is U2001, whose message says that the values hold functions. Compare what the functions return instead.

### A named function or a lambda

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A rule used in several places, or one worth an example | A named function, passed by its name |
| A one-line rule used once, at the call | A lambda, `fn(x) -> …` |
| A rule that reads a value from around the call | A lambda, which captures it |
| A rule that needs several lines | A named function |
| A family of rules that differ by a number, such as a percentage | A function that returns a lambda, such as `percent_off` |
:::

Lists use function values everywhere: `map`, `filter` and `fold` in [chapter 5](/learn/collections/#s5-4) take a lambda that says what to do with each element.

### Check yourself: function values

`main` in `promotions` builds one more rule out of `ten_off`:

```una include="steps/18-function-forms/src/promotions.una#L19-L20" title="steps/18-function-forms/src/promotions.una"
  let twice = fn(cents: Int) -> ten_off(ten_off(cents))
  @console.print("10 off twice: {twice(1_000)}")
```

Predict what it prints.

:::answer Show the answer
```text include="steps/18-function-forms/expected/output.txt#L4"
10 off twice: 810
```

`twice` calls `ten_off` on the result of `ten_off`. 1000 less 10 percent is 900, and 900 less 10 percent is 810.
:::

Then `main` makes a lambda that reads an editable binding, and changes the binding:

```una include="steps/18-function-forms/src/promotions.una#L21-L24" title="steps/18-function-forms/src/promotions.una"
  let edit markup = 120
  let raised = fn(cents: Int) -> cents * markup / 100
  markup = 200
  @console.print("markup: {raised(1_000)}, markup now {markup}")
```

Predict the line it prints.

:::answer Show the answer
```text include="steps/18-function-forms/expected/output.txt#L5"
markup: 1200, markup now 200
```

`raised` captured `markup` when it was made, with the value 120, so it gives 1000 × 120 / 100 = 1200. The assignment of 200 changes the binding, which the last part of the line shows, but not the value the lambda keeps.
:::

## 3.6 Day-to-day: shipping quotes

### What the program must do

Every order needs a shipping charge before it can be paid. The rate depends on the parcel's weight, the zone adds a surcharge, large orders within the country ship for free, and marketing runs promotions that change from week to week. The report at the end of the day lists the charge of each order.

Each rule is a function, and each function's header states what a caller may rely on. The promotions are the part that changes most, so they are parameters: the code that applies a promotion does not know which one it is, and a new promotion is a new function, not a change to the quote.

The program is one module, `shipping`, and each part of it uses one idea of this chapter:

- **The rate and the zone** are functions with `if` chains ([section 3.3](#s3-3)), each with a precondition that rules out input the store never sees, and a postcondition its callers rely on ([section 3.2](#s3-2)).
- **The quote** calls them with labeled arguments ([section 3.1](#s3-1)), and its own clauses follow from theirs.
- **The promotions** are function values, passed to one function that keeps every promotion within bounds ([section 3.5](#s3-5)).
- **The report** prints through a private function whose `uses` the checker infers ([section 3.4](#s3-4)).

### The rate and the zone

Two functions with `if` chains, each with a precondition and a postcondition:

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

The store's price list has steps, not a formula: one price up to 500 g, another up to 2 kg, then a price per kilogram. An `if` chain writes those steps in the order a clerk reads them, and the first condition that holds gives the rate.

`base_rate` requires a weight above zero, which rules out an empty parcel. Its third branch rounds up to a started kilogram: adding 999 grams before dividing by 1000 turns 1 to 1000 extra grams into one kilogram, 1001 to 2000 into two. Its `ensures result >= 450` says that no parcel ships for less than the lowest rate, and the verifier proves it for each branch.

`zone_surcharge` requires a zone from 1 to 3, the zones the store ships to. Its `ensures result >= 0` looks obvious from the body, and it matters all the same: callers of `zone_surcharge` see its header, not its body. [A promise the caller needs, left out](#a-promise-the-caller-needs-left-out-u5001), in Common mistakes, shows what happens to `quote` without that line.

### The quote

One function puts the rules together:

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

`ships_free(goods, zone)` passes `goods` first, and `zone` punned, since the name matches the parameter. `quote` repeats the preconditions of the functions it calls, since its callers must provide the weight and the zone. Its `ensures result >= 0` follows from the postconditions of `base_rate` and `zone_surcharge`: 0 when the order ships free, at least 450 plus at least 0 otherwise.

### Promotions as values

A promotion is any function from a charge to a charge. `promoted` applies one, and its header guarantees that the customer never pays more than the charge, and never less than nothing, whatever the promotion computes:

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

This is the design that [Why pass a function](#why-pass-a-function) asked for: the clamping is written once, and each promotion is only its rule. The body clamps the promotion's result between 0 and the charge, with `min` and `max` from the prelude. Their own postconditions let the verifier prove `promoted`'s promise for every promotion, the ones that exist today and the ones marketing has not invented yet.

### The report

`money` writes cents as an amount, as in [chapter 2](/learn/values/#s2-6). `report_line` chooses the text with a one-line `if`. `show` prints one line, and is private, so its `uses` is inferred. `main` quotes five orders:

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

`report_line` is public and pure: it builds the text, and an example can check it. `show` only prints what `report_line` builds. Keeping the printing in one small function keeps every other function free of effects, and testable.

The first three orders show the rules: a light parcel within the country, a heavy desk that ships free, and a parcel abroad. The last two apply promotions: `half_off` by its name, and a members' rule of 20 percent off as a lambda. `show(1044, charge)` uses punning again: the value named `charge` goes to the parameter `charge`.

Every call of `quote` is checked against its preconditions, so the verifier proves that `24_000 > 0` and that zone 3 is between 1 and 3. Every call of `promoted` must provide `charge >= 0`, and the verifier proves it from `quote`'s postcondition: the promise of one function is what makes the call of the next one safe.

### Running it

`una run .` prints the report shown in [What you'll build](#what-youll-build). Order 1044 ships 3200 g abroad: 790 for the first 2 kg, 500 for two started kilograms above them, and 1800 for the zone, 30.90 in all. Its weekend promotion halves that to 15.45.

> [!SECURITY]
> Of the ten functions in the file, only `show` and `main` touch the console. `main` says so in its header, `una contract shipping.show` shows the inferred `uses` of `show`, and every other function has no `uses`, so it cannot have an effect of any kind. A promotion passed to `promoted` is a pure function too: the type `fn(Int) -> Int` has no `uses`, so a promotion that tried to print would not check.

### The whole program

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

## 3.7 Testing it

### Each rule at its edges

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

### Misbehaving promotions, passed as lambdas

Two of them pass lambdas in their `do` lines. "a promotion never raises the charge" passes a promotion that adds 100 cents, and "a promotion never makes the charge negative" one that takes off 1000. Neither is a real promotion. They are the misbehaving promotions that `promoted` exists to contain, so they test the reason for its body, not only the happy path.

### Postconditions and examples together

The postconditions and the examples do different jobs. `ensures result >= 0 and result <= charge` is proved for every promotion and every charge, but it does not say which value `promoted` returns. The examples fix exact values, 790 and 0, for two cases. Together they say both what is always true and what happens in the cases a reader cares about.

### What the examples leave out

The examples leave out `show` and `main`, the two functions that print. Everything they do is call a function the examples already cover and print the result, so a test of them would test the console. Zone 2 has no example of its own either; "a large order abroad pays shipping" passes through it, with 6890 cents: 6290 for 24 kg and 600 for the zone.

### Running the examples

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

### A second argument without its label (U2004)

:::mistake
Pass the weight by position:

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

*Why:* in many languages, arguments are matched by position, so this habit comes first. In Una only the first argument may go without a label; every other one says which parameter it fills. Read the message: "argument 2 of `quote` needs a label", and the mark points at that argument, `1_200`.

*Fix:* `grams: 1_200`, the label the help line names. The repair is an exact edit, which `una fix .` applies. See [U2004](/docs/errors/U2004/).
:::

### Branches of two types (U2001)

:::mistake
Return the number itself when the order does not ship free:

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

*Why:* both branches of an `if` give the function's result, which is a `Text`, and `charge` is an `Int`. The mistake comes from thinking of the `else` as a fallback that may be anything; in Una it is the other half of one value. The mark points at the branch with the wrong type, not at the callers of `report_line`.

*Fix:* a text in both branches, such as `"order {order}: {money(charge)}"`. See [U2001](/docs/errors/U2001/).
:::

### A promise the caller needs, left out (U5001)

:::mistake
Remove the postcondition of `zone_surcharge`:

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

*Why:* the verifier checks `quote` with the header of `zone_surcharge`, not its body. Without its `ensures`, the surcharge could be any `Int`, so `quote` could be negative. The body of `zone_surcharge` never returns a negative number, which is why the clause looked unnecessary. Read the counterexample, `grams = 1, result = -1, zone = 1`: for a 1 g parcel in zone 1, the verifier assumed the worst surcharge the header allows, and found a negative quote.

*Fix:* put the clause back. A caller can rely only on what a header promises. See [U5001](/docs/errors/U5001/).
:::

### A call that breaks a precondition (U5001)

:::mistake
Quote a zone the store does not ship to:

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

*Why:* `quote` requires a zone from 1 to 3, and the verifier proves that at every call. The first line of the diagnostic shows the precondition with the call's arguments in place: `4 >= 1 and 4 <= 3`. With a literal, the obligation is simply false, and the first mark shows the clause that asked for it.

*Fix:* a zone from 1 to 3. When the zone comes from data, check it with an `if` before the call, so that the verifier sees the check. See [U5001](/docs/errors/U5001/).
:::

### A public function that prints without `uses` (U3004)

:::mistake
Make `show` public:

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

*Why:* nothing is inferred for a `pub` function. A public header declares its effects, since its callers may be in other modules. The mistake usually comes from making a working private function public: it checked before, because its `uses` was inferred. The message says that the code "declares no `uses`, so it is pure", and the mark points at the use of `@console`.

*Fix:* add `uses @console: Console[print]` to its header, or keep it private. See [U3004](/docs/errors/U3004/).
:::

### A lambda bound with `let` (U2010)

:::mistake
Name the members' rule before passing it:

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

*Why:* a lambda's parameter types come from the place it is passed to. A `let` gives it none, so the checker cannot know that `cents` is an `Int`. The message names the parameter and the annotation to add.

*Fix:* `fn(cents: Int) -> cents * 80 / 100`, or pass the lambda straight to `promoted`. See [U2010](/docs/errors/U2010/).
:::

### The long form for a one-line function (U7001)

:::mistake
Write `ships_free` with `=` on its own line:

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

*Why:* a function without clauses whose body is one line has one canonical form, the short one. The long form looks tidier to many readers, but Una keeps one layout per function. The message names the lines, and the help line holds the exact canonical text.

*Fix:* `una fmt .` rewrites it. See [U7001](/docs/errors/U7001/).
:::

## 3.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added at the end, and a stub of the function to write, whose body is a placeholder value. `una test .` fails there until the exercise is done.

Work the same way in each one:

1. Read the examples at the end of the file: they say what the function must return.
2. Write the function, in whatever layout comes to you.
3. Run `una fmt .`, which puts it in canonical form, then `una check .` until it is clean.
4. Run `una test .` until every example passes.

### Exercise 1: delivery days

::::exercise
Write `delivery_days(zone)`: 2 days within the home country, 4 in the neighboring countries, and 9 in the rest of the world. The start package ends with:

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
*Hint:* `zone_surcharge` has the same shape: one value per zone. Copy its header and clauses, rename it, and change the three values. A function with a `requires` clause and a body of several lines takes the long form.
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

### Exercise 2: a promotion for members

::::exercise
Members pay 300 cents less for shipping. Write `member_discount(charge)`, and print a sixth line of the report, for order 1047, with the charge of order 1044 at the members' price. The start package ends with:

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
*Hint:* a promotion is a function from a charge to a charge, like `half_off`, so its body is one line. It only subtracts: `promoted` already keeps the result between 0 and the charge, so the second example passes once the first does. For the report line, copy the two lines of order 1045 in `main` and change what they pass.
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

### Exercise 3: two promotions in a row

::::exercise
Write `both(first, second)`, which returns a new promotion: `first`, then `second` on what `first` gives. The start package ends with:

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
*Hint:* the result type is `fn(Int) -> Int`, so the body is a lambda, as in `percent_off` of [section 3.5](#s3-5). The lambda takes a charge, gives it to `first`, and gives what `first` returns to `second`. It may call `first` and `second`, which it captures.
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

## 3.10 Recap and reference

### For agents

:::agents
`una --json check .` gives every diagnostic with its repairs. U2004 and U7001 carry exact edits, which `una fix .` applies; U5001 carries a counterexample and ranked repairs that need a decision. `una --json contract shipping.quote` gives a function's full header, declared or inferred. The compact rule: *label every argument after the first; use the long form for clauses or a block; a block's value is its last line; an `if` that gives a value has an `else`; a `pub` header declares its `uses`; callers rely only on `requires` and `ensures`; a lambda takes its types from where it is passed.*
:::

### Recap

:::recap
- A header lists each parameter with its type, and the result type. Types in a header are never inferred.
- Label every argument after the first. A name equal to the parameter's name counts as its label.
- Use the short form for a function with no clauses and a one-line body, and the long form for the rest. `una fmt .` writes the right one.
- `requires` is what callers must provide, and `ensures` what the function guarantees. Callers rely on the header alone.
- `if` gives a value; both branches have one type, and an `if` that gives a value has an `else`.
- A `pub` function declares its `uses`. A private one may leave them out, and `una contract` shows what the checker inferred.
- Pass a named function for a rule worth naming and testing, and a lambda for a one-line rule at the call.
:::

### Reference

:::reference
- Construct pages: [functions: forms, clauses, labels, method calls, lambdas](/docs/language/functions/), [`requires`](/docs/language/functions/requires/), [`ensures` and `result`](/docs/language/functions/ensures/), [`if` and blocks](/docs/language/control-flow/), [`uses`](/docs/language/capabilities/uses/), [canonical form](/docs/language/canonical-form/)
- Guides: [write a contract and read a counterexample](/docs/guides/contracts-and-proofs/)
- Commands: [`una contract`](/docs/cli/contract/), [`una report`](/docs/cli/report/), [`una fmt`](/docs/cli/fmt/), [`una fix`](/docs/cli/fix/)
- Standard library: [the prelude](/docs/std/) (`min`, `max`)
- Diagnostics: [U0101](/docs/errors/U0101/), [U0102](/docs/errors/U0102/), [U2001](/docs/errors/U2001/), [U2004](/docs/errors/U2004/), [U2005](/docs/errors/U2005/), [U2010](/docs/errors/U2010/), [U2011](/docs/errors/U2011/), [U3001](/docs/errors/U3001/), [U3003](/docs/errors/U3003/), [U3004](/docs/errors/U3004/), [U3013](/docs/errors/U3013/), [U5001](/docs/errors/U5001/), [U6003](/docs/errors/U6003/), [U7001](/docs/errors/U7001/)
- Specification: [functions and contracts](/docs/spec/04-functions-and-contracts/), [grammar](/docs/spec/02-grammar/), [types](/docs/spec/03-types/), [verification](/docs/spec/12-verification/), [canonical form](/docs/spec/15-canonical-form/), [the standard library](/docs/spec/14-standard-library/)
:::
