---
learn: "13"
title: Limits on authority
editions: ["0.2", "0.3"]
codes: [U0101, U3002, U3020, U3021, U3023, U5001, U7002]
time: 50
builds: A price sale with a dry run, whose authority is locked in una.toml and whose tag printer has a ceiling
prerequisites: ["11", "12"]
template: 2
nav: ["Conditions on operations", "Boundaries", "Locking a contract", "Day-to-day: a price sale", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 13 Limits on authority

[Chapter 12](/learn/capabilities/) showed how a header says what a function may do: print, look a customer up, send a mail. Three questions remain open in a working program. May the function do it on every call, or only in some, such as never in a dry run? Who notices when an edit widens a header? And how much may code that the store did not write, copied into `src/`, ever receive? This chapter answers each one with a rule that `una check` enforces: a condition on an operation, a lock on a header in `una.toml`, and a ceiling for a module. You end with a price sale that rehearses before it changes any price.

## What you'll build

:::build
A price sale for a store. It first runs as a dry run, which prints what it would change and changes nothing, then runs for real: it sets each new price and prints a shelf tag through a tag printer's module that the store copied in. The program prints:

```text include="day-to-day/expected/output.txt"
Dry run: 20 percent off
  LAMP-01 would go from 1990 to 1592
  DESK-02 would go from 24900 to 19920
  RUG-07 would go from 4500 to 3600
The dry run plans 6278 cents off
Sale: 20 percent off
  set LAMP-01 to 1592
  tag: [Desk lamp | 1592 cents]
  set DESK-02 to 19920
  tag: [Oak desk | 19920 cents]
  set RUG-07 to 3600
  tag: [Wool rug | 3600 cents]
The sale took 6278 cents off
```

You will learn to:

- write a condition on an operation, `set_price where not dry_run`, and read the proof the verifier makes of it;
- choose edition `0.3`, the preview of the next version of Una, in `una.toml`;
- give a module from outside the store a ceiling, so that every call into it shows what it receives, and grant it less than you hold, `with @x = @y[ops]`;
- lock the `uses` of a public function in `una.toml`, so that an edit of the code alone cannot widen it;
- test a dry run's price with a stand-in price list.
:::

## Why it works this way

A header that lists `PriceList[set_price]` says that the function may set prices. It does not say when. In most programs, a rule such as "a dry run changes nothing" lives in an `if` somewhere in the body, or in a function three calls away. Nothing checks that every path respects it, and a rehearsal that forgets one branch changes real prices.

A second risk is the edit itself. The verifier proves that a body keeps its header, but an edit can change both together: the header loses a line, the body loses its guard, and the package still checks. In a change that touches many files, the missing line is easy to overlook.

A third risk is code the store did not write. A label printer's module, copied into the package, declares its own `uses`. A new version of it can ask for more, the clock today and the files tomorrow, and the store's code passes it what it asks for by name.

Una gives each risk a rule that the checker enforces. A condition puts "never in a dry run" into the header, where the verifier proves it on every path. A lock in `una.toml` keeps a copy of a header, so that widening it needs a change to the manifest, which a reviewer sees. A boundary gives a module a ceiling, and every call into it must grant each capability by hand, within that ceiling.

> [!KEY]
> In edition `0.3`, a header can say when a function may act, `una.toml` can lock what a header allows, and a module from outside can receive no more than its ceiling.

## 13.1 Conditions on operations (edition 0.3)

### What a condition on an operation is

A store gives a new employee a key to the stockroom, with one rule: during a fire drill, nobody takes stock out. The key says what the employee may open; the rule says when. A **condition on an operation** is such a rule, written in the header. `uses @supplier: Supplier[order where not dry_run]` says that the function may place an order, and only on a call where `dry_run` is false.

The verifier, the part of `una` that proves facts about your code before it runs ([chapter 5](/learn/contracts/#s5-1)), then proves the rule: at every place where the order can be placed, it shows that `dry_run` is false there. A function that could place an order during a dry run does not check.

### Edition 0.3: a preview, chosen in `una.toml`

An **edition** is the version of the Una language that a package is written in, named by the line `edition` in the `[package]` table of `una.toml` ([chapter 1](/learn/hello/#making-the-package)). Every chapter before this one uses edition `0.2`. Conditions on operations, boundaries and locks exist only in edition `0.3`. Every package of this chapter opts in with one line, `edition = "0.3"`:

```toml include="steps/01-conditions/una.toml" title="steps/01-conditions/una.toml"
[package]
name = "restock"
version = "0.1.0"
edition = "0.3"

[run]
entry = "restock"
grants = ["console"]
```

Edition `0.3` is a **preview** until every rule planned for it has landed. Until then, a later release of `una` may add obligations or errors to a package of edition `0.3`, so a package that checks today may need a change after an update. The edition only gets stricter, and stricter concerns the programs that edition `0.2` can express: such a program keeps its result, or gains an obligation or an error. A later release may also accept a new construct that earlier releases reject as a syntax error, such as the condition on an operation of this section, but only a construct that narrows what a program may do: without it, the program is one that edition `0.2` accepts, with no fewer allowed behaviors. It may also accept refined type arguments, a refined kind inside the brackets of another type such as `List[Percent]`, which edition `0.2` rejects. Editions `0.1` and `0.2` are stable: a later release does not change what they accept, except to fix a security or soundness error. Edition `0.3` has every rule of edition `0.2`, so all you learned so far still holds. Besides this chapter, only some packages of [chapter 19, Editions](/learn/editions/), use edition `0.3`; every other chapter of this book stays on `0.2`.

Edition `0.3` adds three things to authority, one per section of this chapter: conditions on operations, here; boundaries, with a narrower kind of rebinding, `with @x = @y[ops]` ([section 13.2](#s13-2)); and locked contracts ([section 13.3](#s13-3)).

### Why an operation needs a condition

A function often has a mode in which it must not act: a dry run, a preview, a rehearsal. Without a condition, the header of a restock function says only `Supplier[order]`, and the rule "never order in a dry run" lives in the body. A reader must read every branch to know that the rule holds, and so must every reader after the next edit. A condition moves the rule to the header, and the verifier checks the body against it.

Each example of this chapter is a package of its own, as [chapter 2](/learn/numbers/#each-step-is-a-package) explains.

### How to write a condition

After an operation's name, in the brackets of `uses`, write `where` and a condition. The restock step lets `reorder` place an order only when `dry_run` is false:

:::steps
```una include="steps/01-conditions/src/restock.una" title="steps/01-conditions/src/restock.una" verified="check, run"
module restock

--- The supplier's ordering service.
capability Supplier
  op order(sku: Text, units: Int) -> Unit

--- Reorders a SKU that runs low. A dry run only says what it would order.
reorder(sku: Text, left: Int, dry_run: Bool) -> Unit
  uses @supplier: Supplier[order where not dry_run]
  uses @console: Console[print]
=
  if left >= 5
    unit
  else if dry_run
    @console.print("would order 20 x {sku}")
  else
    @supplier.order(sku, units: 20)

--- A supplier on a developer's machine: it prints each order instead of placing it.
handler printed() for Supplier
  uses @console: Console[print]
  op order(sku, units) = @console.print("ordered {units} x {sku}")

pub main() -> Unit
  uses @console: Console[print]
=
  reorder("LAMP-01", left: 2, dry_run: true) with @supplier = printed()
  reorder("LAMP-01", left: 2, dry_run: false) with @supplier = printed()
  reorder("DESK-02", left: 9, dry_run: false) with @supplier = printed()
```

1. **`capability Supplier`.** A capability of the package, with one operation, `order` ([chapter 12](/learn/capabilities/#s12-3)).
2. **`uses @supplier: Supplier[order where not dry_run]`.** The operation `order`, then `where`, then the condition `not dry_run`. The condition is a `Bool` over the function's parameters, written in the refinement language of [chapter 5](/learn/contracts/#the-refinement-language), like a `requires` clause.
3. **`if left >= 5` … `else if dry_run` … `else`.** The body. In the `else` branch, which places the order, the verifier knows that `dry_run` is false, which is the condition.
4. **`handler printed()`.** A supplier for a developer's machine: it prints each order instead of placing it.
:::

`una run .` prints:

```text include="steps/01-conditions/expected/output.txt"
would order 20 x LAMP-01
ordered 20 x LAMP-01
```

The first call is a dry run, so it only prints what it would order. The second places the order. The third finds enough stock and does nothing.

### Every form of a condition

The step `02-condition-forms` has one function for each form, and a `main` that calls them:

```una include="steps/02-condition-forms/src/supply.una" title="steps/02-condition-forms/src/supply.una" verified="check, run"
module supply

--- The supplier's service. A quote costs nothing; an order buys the units.
capability Supplier
  op quote(sku: Text, units: Int) -> Int
  op order(sku: Text, units: Int) -> Unit

--- One operation with a condition: an order only where `dry_run` is false.
reorder(sku: Text, units: Int, dry_run: Bool) -> Unit
  uses @supplier: Supplier[order where not dry_run]
=
  if not dry_run
    @supplier.order(sku, units)

--- Two operations: `quote` has no condition, and the condition on `order` has two parts.
restock(sku: Text, units: Int, dry_run: Bool) -> Int
  uses @supplier: Supplier[quote, order where not dry_run and units <= 50]
=
  let cost = @supplier.quote(sku, units)
  if not dry_run and units <= 50
    @supplier.order(sku, units)
  cost

--- A call is checked too: `reorder` may order only where `not dry_run` holds, and so may this
--- function.
reorder_pair(first: Text, second: Text, dry_run: Bool) -> Unit
  uses @supplier: Supplier[order where not dry_run]
=
  reorder(first, units: 10, dry_run)
  reorder(second, units: 10, dry_run)

--- A supplier on a developer's machine: it quotes 250 cents a unit, and prints each order
--- unless it is `quiet`. A handler's `uses` may carry a condition too.
handler printed(quiet: Bool) for Supplier
  uses @console: Console[print where not quiet]
  op quote(sku, units) = units * 250
  op order(sku, units) =
    if not quiet
      @console.print("ordered {units} x {sku}")

pub main() -> Unit
  uses @console: Console[print]
=
  reorder("LAMP-01", units: 20, dry_run: true) with @supplier = printed(quiet: false)
  reorder("LAMP-01", units: 20, dry_run: false) with @supplier = printed(quiet: false)
  let small = restock("DESK-02", units: 5, dry_run: false) with @supplier = printed(quiet: false)
  @console.print("5 desks cost {small}")
  let large = restock("RUG-07", units: 80, dry_run: false) with @supplier = printed(quiet: false)
  @console.print("80 rugs would cost {large}, too many to order at once")
  reorder_pair("CHAIR-09", second: "SHELF-04", dry_run: false) with @supplier = printed(quiet: false)
  reorder("CHAIR-09", units: 10, dry_run: false) with @supplier = printed(quiet: true)
```

```text include="steps/02-condition-forms/expected/output.txt"
ordered 20 x LAMP-01
ordered 5 x DESK-02
5 desks cost 1250
80 rugs would cost 20000, too many to order at once
ordered 10 x CHAIR-09
ordered 10 x SHELF-04
```

#### One operation with a condition

`reorder` lists one operation, `order`, with the condition `not dry_run`, and guards the order with `if not dry_run`. Its first call, a dry run, prints nothing.

#### Operations with and without a condition

`restock` lists two operations in one pair of brackets, separated by a comma: `quote`, with no condition, and `order`, with one. An operation without `where` may run on every call, so `restock` asks for a quote even in a dry run.

#### A condition of several parts

A condition is any `Bool` of the refinement language over the parameters: `not dry_run and units <= 50` lets `restock` order only outside a dry run, and at most 50 units at once. The rugs ask for 80, so `restock` gives back the quote and orders nothing.

#### A call of a function with a condition

`reorder_pair` calls `reorder` twice, and holds the same condition. A call is checked as an operation is: `reorder` may order where `not dry_run` holds of the arguments it receives, and `reorder_pair` passes its own `dry_run`, so the condition of `reorder_pair` covers each call.

#### A condition in a handler's `uses`

A handler's `uses` may carry a condition too, over the handler's own parameters. `printed(quiet: Bool)` may print only where `quiet` is false, and its `order` guards the print. The last call of `main` installs a quiet supplier, so its order prints nothing.

### How a condition is checked

#### At every operation

The verifier proves the condition at every place where the operation can run. Take the dry-run branch out of the restock of [How to write a condition](#how-to-write-a-condition):

```diff include="steps/01-conditions..steps/03-unguarded:src/restock.una" context="1" title="src/restock.una"
--- a/src/restock.una
+++ b/src/restock.una
@@ -13,4 +13,2 @@
     unit
-  else if dry_run
-    @console.print("would order 20 x {sku}")
   else
```

```text include="steps/03-unguarded/expected/rendered.txt"
[U5001] Error: `@supplier.order` may run where `not dry_run` is not proven
    ╭─[ src/restock.una:15:5 ]
    │
  9 │   uses @supplier: Supplier[order where not dry_run]
    │                                        ─────┬─────
    │                                             ╰─────── condition
    │
 15 │     @supplier.order(sku, units: 20)
    │     ───────────────┬───────────────
    │                    ╰───────────────── `@supplier.order` may run where `not dry_run` is not proven
    │
    │ Help 1: repair 1: guard the operation with `if not dry_run`
    │
    │ Help 2: repair 2: add `requires not dry_run` to the enclosing function; its callers then prove it
    │
    │ Note 1: obligation ob-c36fd10895b1 (effect_condition) is refuted: not dry_run
    │
    │ Note 2: counterexample: dry_run = true, left = 4
    │
    │ Note 3: run `una explain U5001` for an explanation
────╯
```

Read it as any diagnostic of the verifier:

- The first line names the operation and the condition: `@supplier.order` may run where `not dry_run` is not proven.
- The marks point at two places: the condition in the header, labeled `condition`, and the operation that may break it.
- The counterexample, `dry_run = true, left = 4`, is a call where it goes wrong: a dry run with 4 units left, few enough to order.
- The first repair guards the operation with `if not dry_run`. The second adds `requires not dry_run`, which would forbid dry runs altogether: callers would then have to prove that `dry_run` is false.

#### At every call

A call of a function that may perform the operation is such a place too. The verifier reads the callee's header there: the callee's condition, at the call's arguments, must imply the caller's. A callee without a condition on the operation may perform it on every call, so its call needs a guard. [Check yourself: conditions](#check-yourself-conditions) shows what happens when a callee's header drops its condition.

#### At every handler you install

A handler installed inside the function, as `with @restock = via_supplier()`, counts as a call too. When the handler's own `uses` list the operation, the handler's condition must imply the function's, and the check is charged at the `with`. A handler whose `uses` list `Supplier[order]` with no condition may order on every call, so a function that holds `Supplier[order where not dry_run]` and installs it gets U5001 at the `with`. The diagnostic's first repair writes the condition in the `uses` of the handler; the second guards the `with` with `if not dry_run`.

#### For the whole call

A condition reads the arguments the caller passed, so its value is fixed for the whole call.

#### Never inferred

A private function without `uses` gets its `uses` inferred from its body ([chapter 6](/learn/functions/#s6-3)), and an inferred `uses` has no condition on any operation. A condition exists only where a header writes it.

#### Not a function value

A function can usually be passed to another function as an argument ([chapter 10](/learn/collections/#s10-2)). A function whose `uses` carry a condition cannot: the function that receives it could not prove the condition, so using its name as a value is U3006. A lambda that calls it can be passed, as any lambda can.

#### Only in edition 0.3

In editions `0.1` and `0.2`, `where` inside the brackets of `uses` is a syntax error, U0101, as [A condition in an edition 0.2 package](#a-condition-in-an-edition-02-package-u0101) shows.

### A condition, a guard or a narrower header

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A function that may perform an operation only on some calls, such as never in a dry run | A condition: `op where …` in its `uses` |
| A function that never performs an operation | Leave the operation out of its `uses` |
| To skip an operation on some calls, with no promise to callers | A guard, `if …`, in the body |
| A function that must never be called in some case at all | `requires`, as in [chapter 5](/learn/contracts/#s5-1) |
:::

A guard alone keeps the body right today; a condition makes the rule part of the header, so the next edit of the body is checked against it too.

### Check yourself: conditions

In the step of [Every form of a condition](#every-form-of-a-condition), `reorder` keeps its guard, `if not dry_run`, but its header loses the condition:

```diff include="steps/02-condition-forms..steps/04-header-not-body:src/supply.una" context="1" title="src/supply.una"
--- a/src/supply.una
+++ b/src/supply.una
@@ -7,5 +7,5 @@
 
---- One operation with a condition: an order only where `dry_run` is false.
+--- Orders only where `dry_run` is false, but its header no longer says so.
 reorder(sku: Text, units: Int, dry_run: Bool) -> Unit
-  uses @supplier: Supplier[order where not dry_run]
+  uses @supplier: Supplier[order]
 =
```

`reorder_pair` is unchanged. Does the package check?

:::answer Show the answer
No. `una check .` reports one diagnostic for each call in `reorder_pair`:

```text include="steps/04-header-not-body/expected/diagnostics.txt"
error U5001 at src/supply.una:29:3: `@supplier.order` may run where `not dry_run` is not proven
  counterexample: dry_run = true
error U5001 at src/supply.una:30:3: `@supplier.order` may run where `not dry_run` is not proven
  counterexample: dry_run = true
```

The verifier checks a call against the callee's header, not its body. The header of `reorder` now lets it order on every call, so at each call in `reorder_pair` the condition `not dry_run` is not proven, and `dry_run = true` refutes it. The first repair writes the condition back into the `uses` of `reorder`, and since `reorder` is private and in the same module, `una fix .` can make that edit:

```text include="steps/04-header-not-body/expected/rendered.txt#L12"
    │ Help 1: repair 1: write the condition in the `uses` of `reorder`, as `order where ...`: `not dry_run` with each parameter of this function replaced by the parameter of `reorder` it is passed as; `reorder` then proves it where it runs `order`; edit src/supply.una:10:33..10:33 to " where not dry_run"
```
:::

## 13.2 A ceiling for a module: boundaries

### What a boundary is

When a store lets a contractor in to service the label printer, it gives them a badge that opens the stockroom and nothing else. Whatever the contractor brings, the badge decides which doors open.

A **boundary** is such a badge for a module, written in `una.toml`. It marks a module, usually **vendored** code, a supplier's code copied into the package's `src/` ([chapter 11](/learn/packages/#s11-3)), and gives it a **ceiling**: the most the rest of the package may ever grant it, as a list of capabilities and operations. A call into the module that would grant more fails the check, and every call into it must grant each capability by hand, with `with`.

### Why give a module a ceiling

The store copied a label printer's module into `src/vendor/labels.una`. A new version of it arrives, and besides printing, it now reads the clock. Its header says so, but the output does not change:

```diff include="steps/05-boundary..steps/06-unbounded:src/vendor/labels.una" context="0" title="src/vendor/labels.una"
--- a/src/vendor/labels.una
+++ b/src/vendor/labels.una
@@ -3 +3 @@
---- Prints a shelf label for a product.
+--- Prints a shelf label for a product. This version also reads the clock.
@@ -5,0 +6 @@
+  uses @clock: Clock[now]
@@ -6,0 +8 @@
+  let printed_at = @clock.now()
```

This package has no boundary yet. The store accepts the new version with two small edits of its own: `main` declares that it holds the clock, and `una.toml` grants it. Without the first, `una check` reports U3001 at the call; without the second, `una check` and `una run` report U3012 ([chapter 12](/learn/capabilities/#s12-2)).

```diff include="steps/05-boundary..steps/06-unbounded:una.toml" context="0" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -8,5 +8 @@
-grants = ["console"]
-
-# Code from the label printer's supplier: the most the store may ever grant it.
-[boundaries]
-"vendor.labels" = ["Console[print]"]
+grants = ["console", "clock"]
```

```una include="steps/06-unbounded/src/store/app.una" title="steps/06-unbounded/src/store/app.una" verified="check, run"
module store.app

import vendor.labels (print_label)

pub main() -> Unit
  uses @console: Console[print]
  uses @clock: Clock[now]
=
  print_label("LAMP-01", price: "19.90")
```

```text include="steps/06-unbounded/expected/output.txt"
[LAMP-01 | 19.90]
```

The package checks and runs, and the label looks as before. The call itself did not change: `print_label` takes the clock by name, as any call passes the capabilities its callee needs ([chapter 12](/learn/capabilities/#s12-4)). Nothing at the call says where the clock goes, and once the store's code holds a capability for a job of its own, a later version of the supplier's module can start using it with no change at all in the store's code. With access to files, the same change could read data it was never meant to see. A boundary makes every such grant visible at the call, and turns one beyond the ceiling into an error.

### How to write `[boundaries]`

:::steps
```toml include="steps/05-boundary/una.toml" title="steps/05-boundary/una.toml"
[package]
name = "store"
version = "0.1.0"
edition = "0.3"

[run]
entry = "store.app"
grants = ["console"]

# Code from the label printer's supplier: the most the store may ever grant it.
[boundaries]
"vendor.labels" = ["Console[print]"]
```

1. **`edition = "0.3"`.** `[boundaries]` exists only in edition `0.3`.
2. **`[boundaries]`.** The table of boundaries.
3. **`"vendor.labels"`.** The key: the module path of a module of the package, in quotes, since it holds a dot. It also covers every module below it, by whole parts of the path: `vendor.labels` covers `vendor.labels.fonts`, but not `vendor.labelsmith`.
4. **`["Console[print]"]`.** The ceiling: an array of texts, each a capability with the operations it may receive, `Capability[operation, …]`, with at least one operation. It names no binding and no condition: a ceiling names capabilities and operations only.
:::

### Printing labels through a boundary

The module itself is ordinary Una. It declares what it uses, as any public function does:

```una include="steps/05-boundary/src/vendor/labels.una" title="steps/05-boundary/src/vendor/labels.una" verified="check"
module vendor.labels

--- Prints a shelf label for a product.
pub print_label(sku: Text, price: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("[{sku} | {price}]")
```

The store's code calls it:

```una include="steps/05-boundary/src/store/app.una" title="steps/05-boundary/src/store/app.una" verified="check, run"
module store.app

import vendor.labels (print_label)

pub main() -> Unit
  uses @console: Console[print]
=
  print_label("LAMP-01", price: "19.90") with @console = @console
```

```text include="steps/05-boundary/expected/output.txt"
[LAMP-01 | 19.90]
```

A call into the boundary takes nothing by name. The caller grants each capability with `with`, here `with @console = @console`: the label module's `@console` is the app's own `@console`. Elsewhere, this rebinding would be redundant; at a boundary it is the grant, so every call into the module shows exactly what it receives.

### How calls into a boundary are checked

A **call into a boundary** is a call from code outside the boundary to a function or a handler inside it. Code inside the boundary calls its own functions as usual.

#### Everything is granted with `with` (U3020)

Call the label module the usual way, without `with`:

```diff include="steps/05-boundary..steps/07-by-name:src/store/app.una" context="0" title="src/store/app.una"
--- a/src/store/app.una
+++ b/src/store/app.una
@@ -8 +8 @@
-  print_label("LAMP-01", price: "19.90") with @console = @console
+  print_label("LAMP-01", price: "19.90")
```

```text include="steps/07-by-name/expected/rendered.txt"
[U3020] Error: `print_label` is in the boundary `vendor.labels` and needs `@console: Console[print]`, which a call into it grants only with `with`
   ╭─[ src/store/app.una:8:3 ]
   │
 8 │   print_label("LAMP-01", price: "19.90")
   │   ───────────────────┬──────────────────
   │                      ╰──────────────────── `print_label` is in the boundary `vendor.labels` and needs `@console: Console[print]`, which a call into it grants only with `with`
   │
   ├─[ src/vendor/labels.una:5:3 ]
   │
 5 │   uses @console: Console[print]
   │   ──────────────┬──────────────
   │                 ╰──────────────── the boundary's requirement
   │
   │ Note: run `una explain U3020` for an explanation
───╯
```

The first mark is the call, and the second is the requirement inside the boundary that the call left to be met by name. The fix is the `with` of [Printing labels through a boundary](#printing-labels-through-a-boundary).

#### What a call grants stays within the ceiling (U3021)

Now add the boundary to the package of [Why give a module a ceiling](#why-give-a-module-a-ceiling), with the new version of the module, and grant it the clock with `with`:

```una include="steps/08-over-ceiling/src/store/app.una" title="steps/08-over-ceiling/src/store/app.una"
module store.app

import vendor.labels (print_label)

pub main() -> Unit
  uses @console: Console[print]
  uses @clock: Clock[now]
=
  print_label("LAMP-01", price: "19.90") with @console = @console, @clock = @clock
```

```text include="steps/08-over-ceiling/expected/rendered.txt"
[U3021] Error: the call of `print_label` grants `Clock[now]` to `vendor.labels`, whose ceiling in `una.toml` allows no operation of `Clock`
   ╭─[ src/store/app.una:9:3 ]
   │
 9 │   print_label("LAMP-01", price: "19.90") with @console = @console, @clock = @clock
   │   ───────────────────┬──────────────────
   │                      ╰──────────────────── the call of `print_label` grants `Clock[now]` to `vendor.labels`, whose ceiling in `una.toml` allows no operation of `Clock`
   │
   │ Note: run `una explain U3021` for an explanation
───╯
```

The call grants `Clock[now]`, and the ceiling allows no operation of `Clock`. To accept the new version, someone must widen the ceiling in `una.toml`, which a reviewer sees, or the store keeps the old version.

#### What counts against the ceiling

Each binding that the callee's `uses` name counts, with every operation it permits. A handler installed for the call counts with its own `uses` too. A binding of the `with` that the callee does not ask for counts for nothing, since the callee can never use it. A boundary module can never be one of the package's trusted modules, so it can never release labeled data ([chapter 17](/learn/information-flow/)).

#### What a boundary key may say (U7002)

Each of these is U7002, at the key in `una.toml`: a key that is not a module of the package, a key inside another key's modules, a malformed ceiling, a capability named twice in one ceiling, an unknown capability or operation, a module that `[trusted]` lists ([chapter 17](/learn/information-flow/)) inside a boundary, and the `[run] entry` inside a boundary.

### Granting less at the call: `with @x = @y[ops]`

[Chapter 12](/learn/capabilities/#narrowing-a-greeting-that-may-only-look-up) showed one way authority narrows: a callee's header limits what it may use, whatever binding it receives. A ceiling does not stop at the callee's header, though. It counts every operation that the granted binding permits. So at a boundary, the caller must hand over less, and edition `0.3` lets it say so at the call.

#### What a narrowed rebinding is

When you lend a colleague your key ring for one errand, you can take off every key but the one they need. A **narrowed rebinding** does that with a binding: it hands the callee the caller's binding with only some of its operations. You write `with @x = @y[ops]`: the callee's name `@x`, `=`, the caller's binding `@y`, and in brackets the names of the operations the callee may receive, separated by commas. It is the rebinding `with @x = @y` of chapter 12, with brackets added.

#### Why a boundary needs it

In this step, the price list has two operations, and the label module reads prices to print them:

```una include="steps/09-narrow-wide/src/store/prices.una" title="steps/09-narrow-wide/src/store/prices.una"
module store.prices

--- The store's price list: reading a price, and setting one.
pub capability PriceList
  op price(sku: Text) -> Int
  op set_price(sku: Text, cents: Int) -> Unit
```

```una include="steps/09-narrow-wide/src/vendor/labels.una" title="steps/09-narrow-wide/src/vendor/labels.una"
module vendor.labels

import store.prices (PriceList)

--- Prints a shelf label with the current price of a product, read from the price list.
pub print_price_tag(sku: Text) -> Unit
  uses @prices: PriceList[price]
  uses @console: Console[print]
=
  let cents = @prices.price(sku)
  @console.print("[{sku} | {cents} cents]")
```

```toml include="steps/09-narrow-wide/una.toml" title="steps/09-narrow-wide/una.toml"
[package]
name = "store"
version = "0.1.0"
edition = "0.3"

[run]
entry = "store.app"
grants = ["console"]

# Code from the label printer's supplier: the most the store may ever grant it.
[boundaries]
"vendor.labels" = ["Console[print]", "PriceList[price]"]
```

The ceiling allows `PriceList[price]`. `reprice` holds `PriceList[price, set_price]`, since it sets a price, and grants its whole binding to the label module:

```una include="steps/09-narrow-wide/src/store/app.una#reprice" title="steps/09-narrow-wide/src/store/app.una"
--- Sets a new price, then prints the shelf label with it.
reprice(sku: Text, cents: Int) -> Unit
  uses @prices: PriceList[price, set_price]
  uses @console: Console[print]
=
  @prices.set_price(sku, cents)
  print_price_tag(sku) with @console = @console, @prices = @prices
```

```text include="steps/09-narrow-wide/expected/rendered.txt#L1"
[U3021] Error: the call of `print_price_tag` grants `PriceList[price, set_price]` to `vendor.labels`, whose ceiling in `una.toml` allows `PriceList[price]`
```

The label module asks only for `price`, but the binding it receives permits `set_price` too, so the call would grant more than the ceiling.

#### One operation: `@prices[price]`

Narrow the binding at the call, `with @prices = @prices[price]`: the label module's `@prices` is the caller's `@prices`, restricted to `price`.

```diff include="steps/09-narrow-wide..steps/10-narrowed:src/store/app.una" context="0" title="src/store/app.una"
--- a/src/store/app.una
+++ b/src/store/app.una
@@ -18 +18 @@
-  print_price_tag(sku) with @console = @console, @prices = @prices
+  print_price_tag(sku) with @console = @console, @prices = @prices[price]
```

```text include="steps/10-narrowed/expected/output.txt"
set LAMP-01 to 1592
[LAMP-01 | 1592 cents]
```

The call now grants `PriceList[price]`, which is within the ceiling, so the package checks and runs. `reprice` itself still holds both operations: only what it hands over is narrower.

#### Several operations, and calls outside a boundary

This step has no boundary. The price list has three operations, and `review` holds all of them. It hands each helper only the operations named at the call:

:::steps
```una include="steps/18-narrow-forms/src/pricing.una" title="steps/18-narrow-forms/src/pricing.una" verified="check, run"
module pricing

--- The store's price list: reading a price, setting one, and taking a product off the list.
capability PriceList
  op price(sku: Text) -> Int
  op set_price(sku: Text, cents: Int) -> Unit
  op remove(sku: Text) -> Unit

--- Prints the price of a SKU. It only reads.
show_price(sku: Text) -> Unit
  uses @prices: PriceList[price]
  uses @console: Console[print]
=
  let cents = @prices.price(sku)
  @console.print("{sku} costs {cents}")

--- Raises the price of a SKU by `cents`.
raise_price(sku: Text, cents: Int) -> Unit
  uses @prices: PriceList[price, set_price]
=
  let current = @prices.price(sku)
  @prices.set_price(sku, cents: current + cents)

--- Takes 10 percent off a SKU, and gives back the new price. A dry run sets no price.
mark_down(sku: Text, dry_run: Bool) -> Int
  uses @prices: PriceList[price, set_price where not dry_run]
=
  let cents = @prices.price(sku)
  let sale = cents - cents / 10
  if not dry_run
    @prices.set_price(sku, cents: sale)
  sale

--- Reviews the price list. It holds every operation, and hands each helper only the ones named
--- at the call. A dry run changes nothing.
review(dry_run: Bool) -> Unit
  uses @prices: PriceList[price, set_price where not dry_run, remove where not dry_run]
  uses @console: Console[print]
=
  show_price("LAMP-01") with @prices = @prices[price]
  if not dry_run
    raise_price("LAMP-01", cents: 100) with @prices = @prices[price, set_price]
  let sale = mark_down("DESK-02", dry_run) with @prices = @prices[price, set_price]
  @console.print("DESK-02 goes to {sale}")
  if not dry_run
    @prices.remove("RUG-07")

--- A price list where every product costs `each` cents, and that prints each change.
handler flat(each: Int) for PriceList
  uses @console: Console[print]
  op price(sku) = each
  op set_price(sku, cents) = @console.print("set {sku} to {cents}")
  op remove(sku) = @console.print("removed {sku}")

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("Dry run:")
  review(dry_run: true) with @prices = flat(1990)
  @console.print("Review:")
  review(dry_run: false) with @prices = flat(1990)
```

1. **`show_price("LAMP-01") with @prices = @prices[price]`.** One operation in the brackets: `show_price` receives a binding that may only read.
2. **`raise_price(…) with @prices = @prices[price, set_price]`.** Several operations, separated by commas, as in the brackets of `uses`. `raise_price` never receives `remove`.
3. **`if not dry_run`.** `review` may set a price only where `not dry_run` holds, and the narrowed binding keeps that condition. `raise_price` has no condition, so its call needs the guard.
4. **`mark_down(…) with @prices = @prices[price, set_price]`.** No guard here: the condition of `mark_down`, `not dry_run`, implies the one the binding carries.
:::

`una run .` prints:

```text include="steps/18-narrow-forms/expected/output.txt"
Dry run:
LAMP-01 costs 1990
DESK-02 goes to 1791
Review:
LAMP-01 costs 1990
set LAMP-01 to 2090
set DESK-02 to 1791
DESK-02 goes to 1791
removed RUG-07
```

The dry run reads two prices and sets none. The review sets two prices and removes a product.

#### How a narrowed rebinding behaves

- **The caller must hold each operation.** The brackets may name only operations that `@y` permits. If `review` held only `PriceList[price]`, `@prices[set_price]` would be U3002: "`@prices` permits `price`, not `set_price`, so a narrowed rebinding of it cannot grant `set_price`".
- **The capability must declare it.** An operation that the capability does not declare, such as `@prices[refund]`, is U1001: "capability `PriceList` has no operation `refund`".
- **The callee gets only the bracketed operations.** A callee that needs another operation of the binding gets U3002 at the call, as for any binding with too few operations, as [Check yourself: narrowing](#check-yourself-narrowing) shows.
- **Names only.** The brackets hold names of operations and nothing else: no `where` and no condition, as [A condition inside the narrowing brackets](#a-condition-inside-the-narrowing-brackets-u0101) shows.
- **Conditions stay.** The narrowed binding runs as the caller's binding, and every condition that binding carries still applies, as the guard around `raise_price` shows.
- **Any call, in edition 0.3.** A narrowed rebinding is allowed at any call, not only at a boundary. In editions `0.1` and `0.2` the brackets are a syntax error, U0101.

#### When to narrow outside a boundary

Outside a boundary, the callee's header already limits what it may use, so narrowing proves nothing more about the callee. It pins, at the call, what the callee receives. If a later edit widens the header of `show_price` to `PriceList[price, set_price]`, the call `with @prices = @prices[price]` fails with U3002, instead of quietly handing over the right to set prices. Narrow where a reader of the caller should see at a glance what each helper gets; pass the binding whole where the callee's header is enough.

### A boundary, a lock or neither

:::decide
**Which to use:**

| The code… | Use |
| --- | --- |
| Is yours, and its header is reviewed with it | Nothing more: the header and the verifier suffice |
| Is yours, and a header must not widen without a review of `una.toml` | A lock in `[contracts]` ([section 13.3](#s13-3)) |
| Comes from a supplier, copied into `src/` | `[boundaries]`, with the least ceiling it needs |
| Comes from a supplier, and you also want its public functions' headers fixed | Both: a boundary for the module, and locks for its functions |
| Receives a binding that permits more than it should get, at a boundary or where you want the call to show it | A narrowed rebinding at the call, `with @x = @y[ops]` |
:::

### Check yourself: a module below the boundary

The supplier adds a second module, `src/vendor/labels/fonts.una`, and the app calls it as it would call any module, by name:

```una include="steps/11-fonts/src/vendor/labels/fonts.una" title="steps/11-fonts/src/vendor/labels/fonts.una"
module vendor.labels.fonts

--- Prints a shelf label in large letters.
pub print_large(sku: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("** {sku} **")
```

```una include="steps/11-fonts/src/store/app.una" title="steps/11-fonts/src/store/app.una"
module store.app

import vendor.labels (print_label)
import vendor.labels.fonts (print_large)

pub main() -> Unit
  uses @console: Console[print]
=
  print_label("LAMP-01", price: "19.90") with @console = @console
  print_large("LAMP-01")
```

`una.toml` is the one of [How to write `[boundaries]`](#how-to-write-boundaries), with the key `vendor.labels` only. Does the package check?

:::answer Show the answer
It does not:

```text include="steps/11-fonts/expected/rendered.txt#L1"
[U3020] Error: `print_large` is in the boundary `vendor.labels` and needs `@console: Console[print]`, which a call into it grants only with `with`
```

The key `vendor.labels` covers every module below it, so `vendor.labels.fonts` is in the boundary too, and a call into it grants its capabilities only with `with`. Write `print_large("LAMP-01") with @console = @console`.
:::

### Check yourself: narrowing

In the step of [Several operations, and calls outside a boundary](#several-operations-and-calls-outside-a-boundary), `review` narrows the binding it gives `show_price` to the other operation:

```diff include="steps/18-narrow-forms..steps/19-narrow-too-few:src/pricing.una" context="0" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -40 +40 @@
-  show_price("LAMP-01") with @prices = @prices[price]
+  show_price("LAMP-01") with @prices = @prices[set_price]
```

`review` holds `set_price`, so the brackets are allowed. Does the package check?

:::answer Show the answer
No:

```text include="steps/19-narrow-too-few/expected/diagnostics.txt"
error U3002 at src/pricing.una:40:3: `show_price` needs `@prices` to permit `price`, which it does not here
```

`show_price` reads a price, so its header needs `@prices` to permit `price`. The narrowed binding permits only `set_price`, so the call gives `show_price` too few operations, which is U3002 at the call. Narrow to what the callee's header lists: `@prices[price]`.
:::

## 13.3 Locking a contract: `[contracts]`

### What a locked contract is

When a store signs an agreement with a courier, each side keeps a copy. If someone later edits the agreement on one side, the copies disagree, and the change is noticed. A **locked contract** is such a copy for one function. The function's header says what it may do; `una.toml` keeps a copy of that, under `[contracts]`; and the checker fails when the header allows more than the copy.

### Why lock a header

A header is code, and an edit to the code can change it. Here is a sale function whose header and body both lost their condition in the same edit: the header no longer says "never on a dry run", and the body no longer checks `dry_run`.

```diff include="steps/12-locked..steps/13-unlocked:src/store/sale.una" context="1" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -8,7 +8,6 @@
 pub apply_sale(sku: Text, cents: Int, percent: Int, dry_run: Bool) -> Int
-  uses @prices: PriceList[set_price where not dry_run]
+  uses @prices: PriceList[set_price]
 =
   let sale = cents - cents * percent / 100
-  if not dry_run
-    @prices.set_price(sku, cents: sale)
+  @prices.set_price(sku, cents: sale)
   sale
```

This package has no `[contracts]` table yet: it is the situation a lock prevents. The body keeps its header, so the package checks clean. `una run .` prints:

```text include="steps/13-unlocked/expected/output.txt"
set DESK-02 to 19920
a dry run plans 19920
set LAMP-01 to 1791
the sale applied 1791
```

The first line is a price change during a dry run, which the doc comment still says cannot happen. The verifier proved that the body keeps its header, but the header itself changed, and no rule said it should not. A reviewer must notice that a line of the header disappeared, in a change that may touch many files.

Locking moves the decision out of the code. With the condition copied into `una.toml`, the header can lose it only if the manifest changes too, and a change to `una.toml` is easy to see, and easy to require a review for.

### How to write `[contracts]`

A lock is one line under `[contracts]`:

:::steps
```toml include="steps/12-locked/una.toml" title="steps/12-locked/una.toml"
[package]
name = "store"
version = "0.1.0"
edition = "0.3"

[run]
entry = "store.app"
grants = ["console"]

# What `store.sale.apply_sale` may do with the price list, and when.
[contracts]
"store.sale.apply_sale" = ["@prices: PriceList[set_price where not dry_run]"]
```

1. **`[contracts]`.** The table of locks. Like `[boundaries]`, it exists only in edition `0.3`.
2. **`"store.sale.apply_sale"`.** The key: the **qualified name** of a public function of the package, its module path, a dot, and its name. It is in quotes, since it holds dots.
3. **`["…"]`.** The value: an array of `uses` clauses, each a text written as the header writes it, without the word `uses`.
4. **`@prices: PriceList[set_price where not dry_run]`.** One clause: the binding, its capability, and in brackets the operations the function may perform, each with its condition when it has one.
:::

#### Several bindings, and operations without a condition

A lock lists every binding the header has, and an operation may be listed with or without a condition. This step locks two functions:

```toml include="steps/14-lock-forms/una.toml" title="steps/14-lock-forms/una.toml"
[package]
name = "store"
version = "0.1.0"
edition = "0.3"

[run]
entry = "store.app"
grants = ["console"]

# Reading a price may only read the price list.
# A sale may read prices, set them only outside a dry run, and record to the audit log.
[contracts]
"store.sale.apply_sale" = ["@prices: PriceList[price, set_price where not dry_run]", "@audit: Audit[record]"]
"store.sale.show_price" = ["@prices: PriceList[price]"]
```

- `show_price` may only read prices: its lock lists `price` with no condition.
- `apply_sale` has two bindings, so its lock has two texts. `price` has no condition, and `set_price` has one.

The module writes the same clauses in the headers:

```una include="steps/14-lock-forms/src/store/sale.una" title="steps/14-lock-forms/src/store/sale.una" verified="check"
module store.sale

--- The price list of the shop.
pub capability PriceList
  op price(sku: Text) -> Int
  op set_price(sku: Text, cents: Int) -> Unit

--- The log where every price change is recorded.
pub capability Audit
  op record(line: Text) -> Unit

--- The price of a SKU, in cents.
pub show_price(sku: Text) -> Int
  uses @prices: PriceList[price]
=
  @prices.price(sku)

--- Takes `percent` off the price of a SKU, and records it. A dry run changes no price.
pub apply_sale(sku: Text, percent: Int, dry_run: Bool) -> Int
  uses @prices: PriceList[price, set_price where not dry_run]
  uses @audit: Audit[record]
=
  let cents = @prices.price(sku)
  let sale = cents - cents * percent / 100
  if not dry_run
    @prices.set_price(sku, cents: sale)
  @audit.record("{sku}: {cents} to {sale}")
  sale
```

```una include="steps/14-lock-forms/src/store/app.una" title="steps/14-lock-forms/src/store/app.una" verified="check, run"
module store.app

import store.sale (Audit, PriceList, apply_sale, show_price)

--- A price list where every SKU costs `each` cents, and that prints each change instead of storing it.
handler flat(each: Int) for PriceList
  uses @console: Console[print]
  op price(sku) = each
  op set_price(sku, cents) = @console.print("set {sku} to {cents}")

--- An audit log that prints each line.
handler printed() for Audit
  uses @console: Console[print]
  op record(line) = @console.print("audit: {line}")

pub main() -> Unit
  uses @console: Console[print]
=
  let shown = show_price("LAMP-01") with @prices = flat(1990)
  @console.print("LAMP-01 costs {shown}")
  let planned = apply_sale("LAMP-01", percent: 10, dry_run: true) with @prices = flat(1990), @audit = printed()
  @console.print("a dry run plans {planned}")
```

```text include="steps/14-lock-forms/expected/output.txt"
LAMP-01 costs 1990
audit: LAMP-01: 1990 to 1791
a dry run plans 1791
```

The dry run reads the price and writes the audit line, and sets no price.

### A sale that cannot lose its dry run

Back to the sale of [Why lock a header](#why-lock-a-header), with its condition, its guard, and the lock of [How to write `[contracts]`](#how-to-write-contracts):

```una include="steps/12-locked/src/store/sale.una" title="steps/12-locked/src/store/sale.una" verified="check"
module store.sale

--- The price list of the shop.
pub capability PriceList
  op set_price(sku: Text, cents: Int) -> Unit

--- Takes `percent` off the price of a product. A dry run changes nothing, and says what it would do.
pub apply_sale(sku: Text, cents: Int, percent: Int, dry_run: Bool) -> Int
  uses @prices: PriceList[set_price where not dry_run]
=
  let sale = cents - cents * percent / 100
  if not dry_run
    @prices.set_price(sku, cents: sale)
  sale
```

```una include="steps/12-locked/src/store/app.una" title="steps/12-locked/src/store/app.una" verified="check, run"
module store.app

import store.sale (PriceList, apply_sale)

--- A price list that prints each change instead of storing it.
handler printed() for PriceList
  uses @console: Console[print]
  op set_price(sku, cents) = @console.print("set {sku} to {cents}")

pub main() -> Unit
  uses @console: Console[print]
=
  let planned = apply_sale("DESK-02", cents: 24900, percent: 20, dry_run: true) with @prices = printed()
  @console.print("a dry run plans {planned}")
  let applied = apply_sale("LAMP-01", cents: 1990, percent: 10, dry_run: false) with @prices = printed()
  @console.print("the sale applied {applied}")
```

```text include="steps/12-locked/expected/output.txt"
a dry run plans 19920
set LAMP-01 to 1791
the sale applied 1791
```

The dry run of the desk plans its sale price and sets nothing. The real sale of the lamp sets its price. The handler `printed` prints each change instead of storing it, so you see when `set_price` runs.

### How a lock is checked

The body and the lock are checked separately. The verifier proves that the body keeps its header, as [section 13.1](#s13-1) showed. The lock adds one more check: that the header keeps the lock. The header must grant no more than its lock.

#### A header may grant less

A header may grant less than its lock, since that only narrows what the function may do: fewer operations, a stronger condition, or no binding of a capability that the lock names. A binding that the lock does not name at all, or an operation that it does not list, is U3023.

#### An operation the lock does not list (U3023)

Give `show_price` the right to set prices too:

```diff include="steps/14-lock-forms..steps/15-extra-op:src/store/sale.una" context="0" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -14 +14 @@
-  uses @prices: PriceList[price]
+  uses @prices: PriceList[price, set_price]
```

```text include="steps/15-extra-op/expected/rendered.txt"
[U3023] Error: the header of `show_price` lets `@prices.set_price` run, which its lock in `una.toml` does not list
    ╭─[ src/store/sale.una:14:34 ]
    │
 14 │   uses @prices: PriceList[price, set_price]
    │                                  ────┬────
    │                                      ╰────── the header of `show_price` lets `@prices.set_price` run, which its lock in `una.toml` does not list
    │
    ├─[ una.toml:14:28 ]
    │
 14 │ "store.sale.show_price" = ["@prices: PriceList[price]"]
    │                            ─────────────┬─────────────
    │                                         ╰─────────────── the lock
    │
    │ Help: repair 1: list only the operations of the lock in the header's `@prices`
    │
    │ Note: run `una explain U3023` for an explanation
────╯
```

The first mark points at the operation in the header, and the second at the lock it breaks. The repair lists only the operations of the lock.

#### Weakening a locked header (U3023)

Now delete the condition from the header of `apply_sale`, and keep the guard:

```diff include="steps/12-locked..steps/16-weakened:src/store/sale.una" context="0" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -9 +9 @@
-  uses @prices: PriceList[set_price where not dry_run]
+  uses @prices: PriceList[set_price]
```

```text include="steps/16-weakened/expected/rendered.txt#L1-L14,L18"
[U3023] Error: the header of `apply_sale` lets `@prices.set_price` run where `not dry_run` does not hold, which `una.toml` locks
    ╭─[ src/store/sale.una:9:27 ]
    │
  9 │   uses @prices: PriceList[set_price]
    │                           ────┬────
    │                               ╰────── the header of `apply_sale` lets `@prices.set_price` run where `not dry_run` does not hold, which `una.toml` locks
    │
    ├─[ una.toml:12:28 ]
    │
 12 │ "store.sale.apply_sale" = ["@prices: PriceList[set_price where not dry_run]"]
    │                            ────────────────────────┬────────────────────────
    │                                                    ╰────────────────────────── lock
    │
    │ Help: repair 1: restore the locked condition: write `set_price where not dry_run` in the header of `apply_sale`, or a condition that implies it; edit src/store/sale.una:9:36..9:36 to " where not dry_run"
    │ Note 2: counterexample: dry_run = true
```

The header now allows what the lock forbids, and the counterexample says when: `dry_run = true`. The body would still behave, since its guard is still there, but the promise the header makes is weaker than the lock, and that is what U3023 reports. The repair writes the condition back, and `una fix .` applies it:

```text include="steps/16-weakened/expected/commands/fix.txt"
$ una fix --dry-run .
fixed src/store/sale.una:9:36 U3023 restore the locked condition: write `set_price where not dry_run` in the header of `apply_sale`, or a condition that implies it
```

The repair changes the module, never `una.toml`. To weaken the contract, someone must change `una.toml`, and that change is what a reviewer sees.

#### What a lock may say (U7002)

Each of these is U7002, at the lock's line: a key that names no public function of the package; a text that does not parse, or lists no operation; one binding locked twice; a capability that the function's module does not see; an operation that the capability does not declare; and a condition that is not a `Bool` over the function's parameters. A handler is never locked: its operations are checked against its own header.

### When to lock a contract

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A function to keep what its body does, as its header says | Nothing more: the verifier already proves it |
| A header that cannot widen in a code change alone | A lock in `[contracts]` |
| To keep a supplier's module within what you grant it | A ceiling in `[boundaries]` ([section 13.2](#s13-2)) |
| The same rule on every call of a function | Its header; a lock only guards the header |
:::

Lock the functions whose authority matters to the business: the ones that change prices, send money or delete records.

### Check yourself: a narrower header

The header of `apply_sale` now asks for a stronger condition than its lock, and the guard matches it. The app adds a sale of 0 percent:

```diff include="steps/12-locked..steps/17-narrower:src/store/sale.una" context="0" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -9 +9 @@
-  uses @prices: PriceList[set_price where not dry_run]
+  uses @prices: PriceList[set_price where not dry_run and percent > 0]
@@ -12 +12 @@
-  if not dry_run
+  if not dry_run and percent > 0
```

```una include="steps/17-narrower/src/store/app.una#main" title="steps/17-narrower/src/store/app.una"
pub main() -> Unit
  uses @console: Console[print]
=
  let planned = apply_sale("DESK-02", cents: 24900, percent: 20, dry_run: true) with @prices = printed()
  @console.print("a dry run plans {planned}")
  let applied = apply_sale("LAMP-01", cents: 1990, percent: 10, dry_run: false) with @prices = printed()
  @console.print("the sale applied {applied}")
  let kept = apply_sale("RUG-07", cents: 4500, percent: 0, dry_run: false) with @prices = printed()
  @console.print("a sale of 0 percent keeps {kept}")
```

Does the package check against the same lock? If it does, what does `una run .` print?

:::answer Show the answer
It checks: the header's condition, `not dry_run and percent > 0`, implies the lock's, `not dry_run`, so the header grants less than the lock allows. `una run .` prints:

```text include="steps/17-narrower/expected/output.txt"
a dry run plans 19920
set LAMP-01 to 1791
the sale applied 1791
a sale of 0 percent keeps 4500
```

A sale of 0 percent changes nothing, so the guard skips `set_price`, and no `set` line is printed for the rug.
:::

## 13.4 Day-to-day: a price sale

### What the sale must do

Twice a year the store runs a sale: a percentage off every product on a list. Before the prices change, the staff want a rehearsal: a **dry run** that prints each old and new price, and the total taken off, and changes nothing. Then the sale runs for real: it sets each new price in the price list, and prints a shelf tag for each product.

Three rules must hold, and each one gets a rule of this chapter:

- A dry run never sets a price: a condition on `set_price`.
- No edit of the code alone can drop that rule: a lock in `una.toml`.
- The tag printer's module, which the store copied from the printer's maker, receives nothing but the console: a boundary.

The package has three modules: `vendor.tags`, the tag printer's code; `store.sale`, the sale itself; and `store.app`, which runs it.

### The manifest: a lock and a boundary

```toml include="day-to-day/una.toml" title="day-to-day/una.toml"
[package]
name = "store"
version = "0.1.0"
edition = "0.3"

[run]
entry = "store.app"
grants = ["console"]

# What the sale may do with the price list, and when.
[contracts]
"store.sale.apply_sale" = ["@prices: PriceList[set_price where not dry_run]"]
"store.sale.run_sale" = ["@prices: PriceList[set_price where not dry_run]", "@console: Console[print]"]

# Code from the maker of the tag printer: the most the store may ever grant it.
[boundaries]
"vendor.tags" = ["Console[print]"]
```

- `edition = "0.3"` turns on the tables below it.
- `[contracts]` locks the two functions that may set prices, `apply_sale` and `run_sale`, with the condition `not dry_run`. `run_sale` also prints, so its lock lists `@console` too: every binding of a locked header must be in its lock.
- `[boundaries]` gives `vendor.tags` the ceiling `Console[print]`.

### The tag printer, a vendored module

```una include="day-to-day/src/vendor/tags.una" title="day-to-day/src/vendor/tags.una" verified="check"
module vendor.tags

--- Prints a price tag for a shelf. This module comes from the maker of the tag printer, and
--- `una.toml` lists it as a boundary.
pub print_tag(name: Text, cents: Int) -> Unit
  uses @console: Console[print]
=
  @console.print("  tag: [{name} | {cents} cents]")
```

The module is ordinary Una, and knows nothing of the boundary: its header asks for the console, as any public function that prints does. The boundary is the store's decision, in the store's `una.toml`.

### The price of one item

`store.sale` starts with its kinds and its capability:

```una include="day-to-day/src/store/sale.una#Percent..sale_price" title="day-to-day/src/store/sale.una" caption="the kinds, the capability and the price rule"
--- A discount in whole percent, from 0 to 100.
pub kind Percent = Int in 0..100

--- A product in the sale: its SKU, its name, and its price before the sale, in cents.
pub kind Item
  sku: Text
  name: Text
  cents: Int

--- The store's price list, where the tills read each price.
pub capability PriceList
  op set_price(sku: Text, cents: Int) -> Unit

--- The price `cents` with `percent` taken off. The discount is rounded down to whole cents.
pub sale_price(cents: Int, percent: Percent) -> Int = cents - cents * percent / 100
```

- `Percent` is a refined kind ([chapter 5](/learn/contracts/#s5-3)): a sale takes 0 to 100 percent off, never more, so no price can go below zero.
- `Item` is a record of a product in the sale.
- `PriceList` is the store's price list, with one operation, `set_price`.
- `sale_price` is pure: it takes the discount off with whole numbers. `cents * percent / 100` divides by 100 and drops the remainder, so a discount that is not a whole number of cents is rounded down.

`apply_sale` prices one item:

```una include="day-to-day/src/store/sale.una#apply_sale" title="day-to-day/src/store/sale.una" verified="check"
--- Takes `percent` off the price of one item, and gives back its sale price. A dry run changes
--- no price.
pub apply_sale(item: Item, percent: Percent, dry_run: Bool) -> Int
  uses @prices: PriceList[set_price where not dry_run]
=
  let sale = sale_price(item.cents, percent)
  if not dry_run
    @prices.set_price(item.sku, cents: sale)
  sale
```

Its header allows `set_price` only where `not dry_run` holds, and its body guards the operation with the same test. It gives back the sale price in both cases, so a dry run can report what it would set.

### Running the sale over every item

```una include="day-to-day/src/store/sale.una#planned_line..run_sale" title="day-to-day/src/store/sale.una" caption="the line of a dry run, and the whole sale"
--- The line a dry run prints for one item.
pub planned_line(item: Item, sale: Int) -> Text = "  {item.sku} would go from {item.cents} to {sale}"

--- Runs the sale over every item, and gives back the cents taken off in all. A dry run prints
--- what it would do, and changes no price; a real run sets each price and prints its tag.
pub run_sale(items: List[Item], percent: Percent, dry_run: Bool) -> Int
  uses @prices: PriceList[set_price where not dry_run]
  uses @console: Console[print]
=
  let edit saved = 0
  for item in items
    let sale = apply_sale(item, percent, dry_run)
    saved = saved + item.cents - sale
    if dry_run
      @console.print(planned_line(item, sale))
    else
      print_tag(item.name, cents: sale) with @console = @console
  saved
```

`run_sale` walks the list with `for`, and keeps the total taken off in `saved`, a name that changes with `let edit` ([chapter 9](/learn/loops/#s9-2)). Two calls in its loop are checked by this chapter's rules:

- **`apply_sale(item, percent, dry_run)`.** A call of a function with a condition. `apply_sale` may set a price where `not dry_run` holds of the `dry_run` it receives, which is `run_sale`'s own, so the condition of `run_sale` covers the call.
- **`print_tag(item.name, cents: sale) with @console = @console`.** A call into the boundary: it grants the console by hand, and the console is within the ceiling. It sits in the `else` branch, so a dry run prints a planned line instead of a tag.

### The app: a dry run, then the sale

```una include="day-to-day/src/store/app.una" title="day-to-day/src/store/app.una" verified="check, run"
module store.app

import store.sale (Item, PriceList, run_sale)

--- A price list that prints each change instead of storing it.
handler printed() for PriceList
  uses @console: Console[print]
  op set_price(sku, cents) = @console.print("  set {sku} to {cents}")

--- The products of the spring sale.
spring_items() -> List[Item]
=
  let lamp = Item(sku: "LAMP-01", name: "Desk lamp", cents: 1990)
  let desk = Item(sku: "DESK-02", name: "Oak desk", cents: 24900)
  let rug = Item(sku: "RUG-07", name: "Wool rug", cents: 4500)
  [lamp, desk, rug]

--- Rehearses the spring sale, then runs it.
pub main() -> Unit
  uses @console: Console[print]
=
  let items = spring_items()
  @console.print("Dry run: 20 percent off")
  let planned = run_sale(items, percent: 20, dry_run: true) with @prices = printed()
  @console.print("The dry run plans {planned} cents off")
  @console.print("Sale: 20 percent off")
  let saved = run_sale(items, percent: 20, dry_run: false) with @prices = printed()
  @console.print("The sale took {saved} cents off")
```

The handler `printed` stands in for the price list: it prints each change instead of storing it, so the output shows exactly when `set_price` runs. `main` calls `run_sale` twice on the same items: first with `dry_run: true`, then with `dry_run: false`.

### Running it

In the `day-to-day` directory:

```sh
una check .
una run .
```

```text include="day-to-day/expected/output.txt"
Dry run: 20 percent off
  LAMP-01 would go from 1990 to 1592
  DESK-02 would go from 24900 to 19920
  RUG-07 would go from 4500 to 3600
The dry run plans 6278 cents off
Sale: 20 percent off
  set LAMP-01 to 1592
  tag: [Desk lamp | 1592 cents]
  set DESK-02 to 19920
  tag: [Oak desk | 19920 cents]
  set RUG-07 to 3600
  tag: [Wool rug | 3600 cents]
The sale took 6278 cents off
```

The dry run prints three planned lines and no `set` line: `set_price` never ran. The sale prints a `set` line from the price list and a tag from the vendored module for each item. Both runs take off the same total, 6278 cents.

### The whole program

The sale module, with its examples, in one piece:

```una include="day-to-day/src/store/sale.una" title="day-to-day/src/store/sale.una" caption="the whole sale module" verified="check, test"
module store.sale

import vendor.tags (print_tag)

--- A discount in whole percent, from 0 to 100.
pub kind Percent = Int in 0..100

--- A product in the sale: its SKU, its name, and its price before the sale, in cents.
pub kind Item
  sku: Text
  name: Text
  cents: Int

--- The store's price list, where the tills read each price.
pub capability PriceList
  op set_price(sku: Text, cents: Int) -> Unit

--- The price `cents` with `percent` taken off. The discount is rounded down to whole cents.
pub sale_price(cents: Int, percent: Percent) -> Int = cents - cents * percent / 100

--- Takes `percent` off the price of one item, and gives back its sale price. A dry run changes
--- no price.
pub apply_sale(item: Item, percent: Percent, dry_run: Bool) -> Int
  uses @prices: PriceList[set_price where not dry_run]
=
  let sale = sale_price(item.cents, percent)
  if not dry_run
    @prices.set_price(item.sku, cents: sale)
  sale

--- The line a dry run prints for one item.
pub planned_line(item: Item, sale: Int) -> Text = "  {item.sku} would go from {item.cents} to {sale}"

--- Runs the sale over every item, and gives back the cents taken off in all. A dry run prints
--- what it would do, and changes no price; a real run sets each price and prints its tag.
pub run_sale(items: List[Item], percent: Percent, dry_run: Bool) -> Int
  uses @prices: PriceList[set_price where not dry_run]
  uses @console: Console[print]
=
  let edit saved = 0
  for item in items
    let sale = apply_sale(item, percent, dry_run)
    saved = saved + item.cents - sale
    if dry_run
      @console.print(planned_line(item, sale))
    else
      print_tag(item.name, cents: sale) with @console = @console
  saved

--- A price list that keeps nothing, for the examples.
handler ignored() for PriceList
  op set_price(sku, cents) = unit

example "20 percent off a desk lamp"
  do sale_price(1990, percent: 20)
  expect result == 1592

example "0 percent off keeps the price"
  do sale_price(4500, percent: 0)
  expect result == 4500

example "100 percent off gives the item away"
  do sale_price(4500, percent: 100)
  expect result == 0

example "a discount that is not whole cents is rounded down"
  do sale_price(999, percent: 15)
  expect result == 850

example "a dry run gives the sale price"
  given @prices = ignored()
  do apply_sale(Item(sku: "LAMP-01", name: "Desk lamp", cents: 1990), percent: 20, dry_run: true)
  expect result == 1592

example "a real run gives the same sale price"
  given @prices = ignored()
  do apply_sale(Item(sku: "LAMP-01", name: "Desk lamp", cents: 1990), percent: 20, dry_run: false)
  expect result == 1592

example "the line of a dry run names the old and the new price"
  do planned_line(Item(sku: "RUG-07", name: "Wool rug", cents: 4500), sale: 3600)
  expect result == "  RUG-07 would go from 4500 to 3600"
```

## 13.5 Testing it

### The price rule, at its edges

`sale_price` is pure, so its examples are the simple ones of [chapter 1](/learn/hello/#s1-7): a call and its result. They cover an ordinary discount, the two ends of `Percent`, and a discount that is not a whole number of cents:

```una include="day-to-day/src/store/sale.una#L54-L68" title="day-to-day/src/store/sale.una" caption="the price rule"
example "20 percent off a desk lamp"
  do sale_price(1990, percent: 20)
  expect result == 1592

example "0 percent off keeps the price"
  do sale_price(4500, percent: 0)
  expect result == 4500

example "100 percent off gives the item away"
  do sale_price(4500, percent: 100)
  expect result == 0

example "a discount that is not whole cents is rounded down"
  do sale_price(999, percent: 15)
  expect result == 850
```

### The dry run, with a stand-in price list

`apply_sale` uses the price list, so an example of it needs a price list to call. `given @prices = ignored()` installs the handler `ignored`, which keeps nothing, for one example, as in [chapter 12](/learn/capabilities/#s12-6). Both examples check the price that comes back, in a dry run and in a real one:

```una include="day-to-day/src/store/sale.una#L70-L78" title="day-to-day/src/store/sale.una" caption="a dry run and a real run"
example "a dry run gives the sale price"
  given @prices = ignored()
  do apply_sale(Item(sku: "LAMP-01", name: "Desk lamp", cents: 1990), percent: 20, dry_run: true)
  expect result == 1592

example "a real run gives the same sale price"
  given @prices = ignored()
  do apply_sale(Item(sku: "LAMP-01", name: "Desk lamp", cents: 1990), percent: 20, dry_run: false)
  expect result == 1592
```

The examples pin down the price itself, which no condition states: a dry run must report the same price that the real run sets.

### What must not happen: proved, not tested

That a dry run sets no price is not an example's job here. The condition on `set_price` puts the rule in the header, and the verifier proves it on every path, for every item and every percent, before any example runs. If the guard goes, `una check .` reports U5001, as [Setting a price without the guard](#setting-a-price-without-the-guard-u5001) shows, and `una test .` fails with it. A test can also check which operations a call performed, a tool of [section 14.3](/learn/testing/#s14-3).

### What the examples leave out: `run_sale` and the tags

`run_sale` prints, and its examples would need a stand-in for the console too ([chapter 14](/learn/testing/#s14-3)). An example outside the boundary also cannot call `print_tag`: an example's `do` line takes no `with`, so it can call into a boundary only a function with no `uses`. The text that a dry run prints for each item is the pure `planned_line`, which has its own example:

```una include="day-to-day/src/store/sale.una#L80-L82" title="day-to-day/src/store/sale.una" caption="the line of a dry run"
example "the line of a dry run names the old and the new price"
  do planned_line(Item(sku: "RUG-07", name: "Wool rug", cents: 4500), sale: 3600)
  expect result == "  RUG-07 would go from 4500 to 3600"
```

### Running the examples

```text include="day-to-day/expected/commands/test.txt#L2-L10"
example store.sale "20 percent off a desk lamp" ... ok
example store.sale "0 percent off keeps the price" ... ok
example store.sale "100 percent off gives the item away" ... ok
example store.sale "a discount that is not whole cents is rounded down" ... ok
example store.sale "a dry run gives the sale price" ... ok
example store.sale "a real run gives the same sale price" ... ok
example store.sale "the line of a dry run names the old and the new price" ... ok

7 examples: 7 passed, 0 failed
```

## 13.6 Common mistakes

Each mistake is a small change to a package of this chapter, followed by what `una check .` reports.

### Setting a price without the guard (U5001)

:::mistake
Drop the guard of `apply_sale` in the day-to-day program, and set the price on every call:

```diff include="day-to-day..mistakes/1:src/store/sale.una" context="1" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -26,4 +26,3 @@
   let sale = sale_price(item.cents, percent)
-  if not dry_run
-    @prices.set_price(item.sku, cents: sale)
+  @prices.set_price(item.sku, cents: sale)
   sale
```

```text include="mistakes/1/expected/rendered.txt#L1-L12,L18"
[U5001] Error: `@prices.set_price` may run where `not dry_run` is not proven
    ╭─[ src/store/sale.una:27:3 ]
    │
 24 │   uses @prices: PriceList[set_price where not dry_run]
    │                                           ─────┬─────
    │                                                ╰─────── condition
    │
 27 │   @prices.set_price(item.sku, cents: sale)
    │   ────────────────────┬───────────────────
    │                       ╰───────────────────── `@prices.set_price` may run where `not dry_run` is not proven
    │
    │ Help 1: repair 1: guard the operation with `if not dry_run`
    │ Note 2: counterexample: dry_run = true, item = Item#0, item.cents = 0, item.sku = Text#0, percent = 0
```

*Why:* the header allows `set_price` only where `not dry_run` holds, and nothing in the body makes it hold before the operation. The counterexample has `dry_run = true`; the other values it lists, such as `Item#0`, are placeholders that any item fills. The marks show the condition in the header and the operation that may break it.

*Fix:* the first repair, a guard: `if not dry_run` around the operation, as the program has it. See [U5001](/docs/errors/U5001/).
:::

### A condition in an edition 0.2 package (U0101)

:::mistake
Leave the restock step of [section 13.1](#s13-1) on edition `0.2`:

```diff include="steps/01-conditions..mistakes/2:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -3,3 +3,3 @@
 version = "0.1.0"
-edition = "0.3"
+edition = "0.2"
 
```

```text include="mistakes/2/expected/rendered.txt"
[U0101] Error: unexpected keyword `where`, expected `,` or `]`
   ╭─[ src/restock.una:9:34 ]
   │
 9 │   uses @supplier: Supplier[order where not dry_run]
   │                                  ──┬──
   │                                    ╰──── unexpected keyword `where`, expected `,` or `]`
   │
   │ Note: run `una explain U0101` for an explanation
───╯
```

*Why:* edition `0.2` has no conditions on operations, so in its grammar the brackets of `uses` hold only names of operations, separated by commas. The word `where` there is a syntax error, and the marks point at it. Nothing in the code is wrong; the edition is.

*Fix:* write `edition = "0.3"` in `una.toml`, if the package may follow a preview edition, or remove the condition and keep the rule in a guard. See [U0101](/docs/errors/U0101/).
:::

### Calling into a boundary by name (U3020)

:::mistake
Call the tag printer as you would call any function, without `with`:

```diff include="day-to-day..mistakes/3:src/store/sale.una" context="1" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -46,3 +46,3 @@
     else
-      print_tag(item.name, cents: sale) with @console = @console
+      print_tag(item.name, cents: sale)
   saved
```

```text include="mistakes/3/expected/rendered.txt"
[U3020] Error: `print_tag` is in the boundary `vendor.tags` and needs `@console: Console[print]`, which a call into it grants only with `with`
    ╭─[ src/store/sale.una:47:7 ]
    │
 47 │       print_tag(item.name, cents: sale)
    │       ────────────────┬────────────────
    │                       ╰────────────────── `print_tag` is in the boundary `vendor.tags` and needs `@console: Console[print]`, which a call into it grants only with `with`
    │
    ├─[ src/vendor/tags.una:6:3 ]
    │
  6 │   uses @console: Console[print]
    │   ──────────────┬──────────────
    │                 ╰──────────────── the boundary's requirement
    │
    │ Note: run `una explain U3020` for an explanation
────╯
```

*Why:* `run_sale` holds `@console`, and outside a boundary the call would take it by name. A call into a boundary takes nothing by name, so that every grant to the module is written at the call. The first mark is the call, and the second the requirement inside the boundary that it leaves unmet.

*Fix:* grant it by hand, `with @console = @console`. See [U3020](/docs/errors/U3020/).
:::

### Dropping the condition from a locked header (U3023, U5001)

:::mistake
Delete the condition from the header of `apply_sale`, and keep its guard:

```diff include="day-to-day..mistakes/4:src/store/sale.una" context="1" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -23,3 +23,3 @@
 pub apply_sale(item: Item, percent: Percent, dry_run: Bool) -> Int
-  uses @prices: PriceList[set_price where not dry_run]
+  uses @prices: PriceList[set_price]
 =
```

```text include="mistakes/4/expected/rendered.txt#L1,L14,L18,L22,L29,L33,L39"
[U3023] Error: the header of `apply_sale` lets `@prices.set_price` run where `not dry_run` does not hold, which `una.toml` locks
    │ Help: repair 1: restore the locked condition: write `set_price where not dry_run` in the header of `apply_sale`, or a condition that implies it; edit src/store/sale.una:24:36..24:36 to " where not dry_run"
    │ Note 2: counterexample: dry_run = true, percent = 4
[U5001] Error: `@prices.set_price` may run where `not dry_run` is not proven
 42 │     let sale = apply_sale(item, percent, dry_run)
    │ Help 1: repair 1: write the condition in the `uses` of `apply_sale`, as `set_price where ...`: `not dry_run` with each parameter of this function replaced by the parameter of `apply_sale` it is passed as; `apply_sale` then proves it where it runs `set_price`
    │ Note 2: counterexample: dry_run = true, items = List#0, items.len = 1, percent = 0, saved = 0
```

*Why:* two rules see the change. The header no longer keeps its lock in `una.toml`, which is U3023 at the header. And `run_sale`, whose condition still says `not dry_run`, calls a function whose header may now set a price on every call, which is U5001 at the call: the verifier reads the callee's header, not its guard.

*Fix:* write the condition back, as the U3023 repair says; `una fix .` makes that edit, and both diagnostics go away. See [U3023](/docs/errors/U3023/).
:::

### A lock key without its module (U7002)

:::mistake
Name the locked function by its short name:

```diff include="day-to-day..mistakes/5:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -11,3 +11,3 @@
 [contracts]
-"store.sale.apply_sale" = ["@prices: PriceList[set_price where not dry_run]"]
+"apply_sale" = ["@prices: PriceList[set_price where not dry_run]"]
 "store.sale.run_sale" = ["@prices: PriceList[set_price where not dry_run]", "@console: Console[print]"]
```

```text include="mistakes/5/expected/rendered.txt"
[U7002] Error: [contracts] locks `apply_sale`, which is not a public function of this package
    ╭─[ una.toml:12:1 ]
    │
 12 │ "apply_sale" = ["@prices: PriceList[set_price where not dry_run]"]
    │ ──────┬─────
    │       ╰─────── [contracts] locks `apply_sale`, which is not a public function of this package
    │
    │ Note: run `una explain U7002` for an explanation
────╯
```

*Why:* a key of `[contracts]` is the qualified name of a public function: its module path, a dot, and its name. `apply_sale` alone names no function that una can find, so the lock guards nothing, and una refuses it rather than ignore it.

*Fix:* write `"store.sale.apply_sale"`. See [U7002](/docs/errors/U7002/).
:::

### A 0.3 table in an edition 0.2 package (U7002)

:::mistake
Leave the boundary step of [section 13.2](#s13-2) on edition `0.2`:

```diff include="steps/05-boundary..mistakes/6:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -3,3 +3,3 @@
 version = "0.1.0"
-edition = "0.3"
+edition = "0.2"
 
```

```text include="mistakes/6/expected/rendered.txt"
[U7002] Error: unknown table [boundaries] in una.toml
    ╭─[ una.toml:11:2 ]
    │
 11 │ [boundaries]
    │  ─────┬────
    │       ╰────── unknown table [boundaries] in una.toml
    │
    │ Note: run `una explain U7002` for an explanation
────╯
```

*Why:* `[boundaries]` and `[contracts]` exist only in edition `0.3`. In edition `0.2`, each is a table una does not know, and an unknown table is an error, not a setting that is silently ignored: a ceiling that una skipped would give no protection. The mark points at the table's name.

*Fix:* set `edition = "0.3"` if you want the preview's rules, or remove the table. See [U7002](/docs/errors/U7002/).
:::

### A condition inside the narrowing brackets (U0101)

:::mistake
In the step of [Several operations, and calls outside a boundary](#several-operations-and-calls-outside-a-boundary), restate the caller's condition when you narrow the binding for `mark_down`:

```diff include="steps/18-narrow-forms..mistakes/7:src/pricing.una" context="0" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -43 +43 @@
-  let sale = mark_down("DESK-02", dry_run) with @prices = @prices[price, set_price]
+  let sale = mark_down("DESK-02", dry_run) with @prices = @prices[price, set_price where not dry_run]
```

```text include="mistakes/7/expected/rendered.txt"
[U0101] Error: unexpected keyword `where`, expected `,` or `]`
    ╭─[ src/pricing.una:43:84 ]
    │
 43 │   let sale = mark_down("DESK-02", dry_run) with @prices = @prices[price, set_price where not dry_run]
    │                                                                                    ──┬──
    │                                                                                      ╰──── unexpected keyword `where`, expected `,` or `]`
    │
    │ Note: run `una explain U0101` for an explanation
────╯
```

*Why:* the brackets of a narrowed rebinding take names of operations only. `where` belongs in the brackets of `uses`, in a header, so here it is a syntax error, and the mark points at it. There is nothing to restate: the narrowed binding runs as the caller's, and keeps every condition that the caller's binding carries.

*Fix:* write the names alone, `@prices[price, set_price]`. See [U0101](/docs/errors/U0101/).
:::

## 13.7 Exercises

The exercises come with the chapter's download, `13-authority.tar.gz`. Each starts from `exercises/N/start`: the day-to-day program with a new function and its examples added. `una check .` reports a problem there, so `una test .` fails until the exercise is done.

### Exercise 1: a clearance that keeps its dry run

::::exercise
At the end of a season, the store halves the price of some products. A product of 1000 cents or less is cheap already, and keeps its price. The start package adds `clearance`, whose header allows `set_price` only where `not dry_run and item.cents > 1000` holds, and three examples:

```una include="exercises/1/start/src/store/sale.una#L84-L107" title="exercises/1/start/src/store/sale.una"
--- Halves the price of an item at the end of a season, and gives back its new price. An item of
--- 1000 cents or less is cheap already, and keeps its price. A dry run changes no price. Exercise 1:
--- make the body keep its header.
pub clearance(item: Item, dry_run: Bool) -> Int
  uses @prices: PriceList[set_price where not dry_run and item.cents > 1000]
=
  let half = item.cents / 2
  @prices.set_price(item.sku, cents: half)
  half

example "a dry run of a clearance gives the new price"
  given @prices = ignored()
  do clearance(Item(sku: "RUG-07", name: "Wool rug", cents: 4500), dry_run: true)
  expect result == 2250

example "a clearance halves the price"
  given @prices = ignored()
  do clearance(Item(sku: "RUG-07", name: "Wool rug", cents: 4500), dry_run: false)
  expect result == 2250

example "a cheap item keeps its price"
  given @prices = ignored()
  do clearance(Item(sku: "SOAP-03", name: "Hand soap", cents: 800), dry_run: false)
  expect result == 800
```

`una check .` reports:

```text include="exercises/1/start/expected/diagnostics.txt"
error U5001 at src/store/sale.una:91:3: `@prices.set_price` may run where `not dry_run and item.cents > 1000` is not proven
  counterexample: dry_run = true, half = 500, item = "Item#0", item.cents = 1001, item.sku = "Text#0"
```

Change the body of `clearance` so that it keeps its header, and the three examples pass.

:::hint
*Hint:* the diagnostic's first repair guards the operation, but the result must change too: a cheap item gives back its own price. Let one `if` choose the price, and a second guard the operation inside the branch that halves it. The verifier proves the condition from both.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Keep a cheap item's price, and guard the operation in the branch that halves it:

```diff include="exercises/1/start..exercises/1/answer:src/store/sale.una" context="1" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -84,4 +84,3 @@
 --- Halves the price of an item at the end of a season, and gives back its new price. An item of
---- 1000 cents or less is cheap already, and keeps its price. A dry run changes no price. Exercise 1:
---- make the body keep its header.
+--- 1000 cents or less is cheap already, and keeps its price. A dry run changes no price.
 pub clearance(item: Item, dry_run: Bool) -> Int
@@ -89,5 +88,9 @@
 =
-  let half = item.cents / 2
-  @prices.set_price(item.sku, cents: half)
-  half
+  if item.cents <= 1000
+    item.cents
+  else
+    let half = item.cents / 2
+    if not dry_run
+      @prices.set_price(item.sku, cents: half)
+    half
 
```

Inside the `else`, `item.cents > 1000` holds, and inside the guard `not dry_run` holds, so both parts of the condition are proven where `set_price` runs.
:::
::::

### Exercise 2: honor a lock

::::exercise
The start package adds `end_sale`, which puts an item's old price back and gives back that price, and a lock for it in `una.toml`:

```toml include="exercises/2/start/una.toml" title="exercises/2/start/una.toml"
[package]
name = "store"
version = "0.1.0"
edition = "0.3"

[run]
entry = "store.app"
grants = ["console"]

# What the sale may do with the price list, and when.
[contracts]
"store.sale.apply_sale" = ["@prices: PriceList[set_price where not dry_run]"]
"store.sale.end_sale" = ["@prices: PriceList[set_price where not dry_run]"]
"store.sale.run_sale" = ["@prices: PriceList[set_price where not dry_run]", "@console: Console[print]"]

# Code from the maker of the tag printer: the most the store may ever grant it.
[boundaries]
"vendor.tags" = ["Console[print]"]
```

```una include="exercises/2/start/src/store/sale.una#L84-L100" title="exercises/2/start/src/store/sale.una"
--- Puts back the price an item had before the sale, and gives back that price. A dry run changes
--- no price. Exercise 2: honor the lock in `una.toml`.
pub end_sale(item: Item, dry_run: Bool) -> Int
  uses @prices: PriceList[set_price]
=
  @prices.set_price(item.sku, cents: item.cents)
  item.cents

example "a dry run of the end of a sale gives the old price"
  given @prices = ignored()
  do end_sale(Item(sku: "RUG-07", name: "Wool rug", cents: 4500), dry_run: true)
  expect result == 4500

example "the end of a sale gives the old price back"
  given @prices = ignored()
  do end_sale(Item(sku: "RUG-07", name: "Wool rug", cents: 4500), dry_run: false)
  expect result == 4500
```

`una check .` reports that the header lets `set_price` run when `dry_run` is true:

```text include="exercises/2/start/expected/diagnostics.txt"
error U3023 at src/store/sale.una:87:27: the header of `end_sale` lets `@prices.set_price` run where `not dry_run` does not hold, which `una.toml` locks
  counterexample: dry_run = true
```

Change `end_sale` so that a dry run sets no price, and its header keeps the lock. Do not change `una.toml`.

:::hint
*Hint:* copy the condition from the lock into the header. The verifier then asks for the guard that makes the header true:

```text include="exercises/2/header-only/expected/rendered.txt#L1,L12"
[U5001] Error: `@prices.set_price` may run where `not dry_run` is not proven
    │ Help 1: repair 1: guard the operation with `if not dry_run`
```
:::

Check your answer with `una test .`. Both examples must pass, which needs `una check .` to report nothing: the verifier then proves that a dry run sets no price.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Write the locked condition in the header, and guard the operation to match it:

```diff include="exercises/2/start..exercises/2/answer:src/store/sale.una" context="1" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -84,7 +84,8 @@
 --- Puts back the price an item had before the sale, and gives back that price. A dry run changes
---- no price. Exercise 2: honor the lock in `una.toml`.
+--- no price.
 pub end_sale(item: Item, dry_run: Bool) -> Int
-  uses @prices: PriceList[set_price]
+  uses @prices: PriceList[set_price where not dry_run]
 =
-  @prices.set_price(item.sku, cents: item.cents)
+  if not dry_run
+    @prices.set_price(item.sku, cents: item.cents)
   item.cents
```

The header now keeps the lock, and the body keeps the header: two separate proofs, as in [How a lock is checked](#how-a-lock-is-checked).
:::
::::

### Exercise 3: end the sale for every item

::::exercise
The start package adds `put_back`, which sets one item back to its old price, and `end_all`, which calls it for every item and counts them. `end_all` promises that a dry run sets no price, but its loop calls `put_back` on every turn:

```una include="exercises/3/start/src/store/sale.una#L84-L109" title="exercises/3/start/src/store/sale.una"
--- Sets one item back to its price before the sale.
pub put_back(item: Item) -> Unit
  uses @prices: PriceList[set_price]
=
  @prices.set_price(item.sku, cents: item.cents)

--- Ends the sale for every item, and gives back how many prices it puts back. A dry run only
--- counts them. Exercise 3: make the dry run set no price.
pub end_all(items: List[Item], dry_run: Bool) -> Int
  uses @prices: PriceList[set_price where not dry_run]
=
  let edit count = 0
  for item in items
    put_back(item)
    count = count + 1
  count

example "a dry run counts the prices"
  given @prices = ignored()
  do end_all([Item(sku: "RUG-07", name: "Wool rug", cents: 4500), Item(sku: "LAMP-01", name: "Desk lamp", cents: 1990)], dry_run: true)
  expect result == 2

example "the end of the sale counts every price it puts back"
  given @prices = ignored()
  do end_all([Item(sku: "RUG-07", name: "Wool rug", cents: 4500), Item(sku: "LAMP-01", name: "Desk lamp", cents: 1990)], dry_run: false)
  expect result == 2
```

`una check .` reports:

```text include="exercises/3/start/expected/diagnostics.txt"
error U5001 at src/store/sale.una:97:5: `@prices.set_price` may run where `not dry_run` is not proven
  counterexample: count = 0, dry_run = true, items = "List#0", items.len = 1
```

Change `end_all` so that a dry run still counts every item, sets no price, and both examples pass. Do not change `put_back`.

:::hint
*Hint:* the diagnostic is at the call of `put_back`, not at an operation: its header has no condition, so it may set a price on every call. `put_back` has no `dry_run` parameter, so a condition in its header could not name one. Guard the call instead, and keep the count outside the guard.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Guard the call, and count on every turn:

```diff include="exercises/3/start..exercises/3/answer:src/store/sale.una" context="1" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -90,3 +90,3 @@
 --- Ends the sale for every item, and gives back how many prices it puts back. A dry run only
---- counts them. Exercise 3: make the dry run set no price.
+--- counts them.
 pub end_all(items: List[Item], dry_run: Bool) -> Int
@@ -96,3 +96,4 @@
   for item in items
-    put_back(item)
+    if not dry_run
+      put_back(item)
     count = count + 1
```

A call of a function that may perform the operation is checked as the operation is. Inside the guard, `dry_run` is false, so the condition of `end_all` holds at the call.
:::
::::

## 13.8 Recap and reference

### For agents

:::agents
`una --json check .` reports a broken condition as U5001, an `effect_condition` obligation with a counterexample and the condition as a related span. A weakened locked condition is U3023, a `contract_lock` obligation with a counterexample; an operation or binding the lock omits is U3023 with no obligation. `una fix .` restores a locked condition (U3023) and writes a caller's condition into a private callee of the same module (U5001 at a call); it never edits `una.toml`. U3020, U3021 and U7002 carry no edit. The compact rule: *in edition `0.3`, an operation with `where` runs only where its condition holds; a header never grants more than its lock; a call into a boundary grants everything with `with`, within the ceiling.*
:::

### Recap

:::recap
- Conditions, boundaries and locks need `edition = "0.3"`, a preview; in edition `0.2` they are U0101 or U7002.
- `PriceList[set_price where not dry_run]` allows `set_price` only where `dry_run` is false; guard it with `if not dry_run` (U5001).
- A call is checked as an operation is: the callee's header condition must imply the caller's.
- `[boundaries]` gives a module and those below it a ceiling; calls into it grant with `with` (U3020), within it (U3021).
- `with @x = @y[ops]` grants only the named operations, which the caller must hold (U3002); names only, and the caller's conditions still apply.
- `[contracts]` locks a public function's `uses`; its header may grant less, never more (U3023).
- `una fix .` restores a locked condition, and never edits `una.toml`.
- Test a dry run's result with a stand-in handler; the condition, which the verifier proves, keeps it from setting a price.
:::

### Reference

:::reference
- Construct pages: [`uses`](/docs/language/capabilities/uses/), [`capability` and `op`](/docs/language/capabilities/capability/), [`handler`](/docs/language/capabilities/handler/), [`with`](/docs/language/capabilities/with/), [`where`](/docs/language/types/where/), [`example`](/docs/language/examples/example/)
- Configuration: [`[package] edition`](/docs/configure/package/edition/), [`[boundaries]`](/docs/configure/boundaries/), [`una.toml`](/docs/configure/)
- Commands: [`una check`](/docs/cli/check/), [`una fix`](/docs/cli/fix/), [`una test`](/docs/cli/test/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U3002](/docs/errors/U3002/), [U3006](/docs/errors/U3006/), [U3020](/docs/errors/U3020/), [U3021](/docs/errors/U3021/), [U3023](/docs/errors/U3023/), [U5001](/docs/errors/U5001/), [U7002](/docs/errors/U7002/)
- Specification: [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [verification](/docs/spec/12-verification/), [diagnostics, the command line and project files](/docs/spec/13-diagnostics-and-abi/), [grammar](/docs/spec/02-grammar/)
:::
