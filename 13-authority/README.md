---
learn: "13"
title: Limits on authority
editions: ["0.2", "0.3"]
codes: [U3020, U3021, U3023, U5001, U7002]
time: 20
builds: A price sale with a dry run
prerequisites: ["11", "12"]
template: 2
nav: ["Conditions on operations", "Boundaries", "Locking a contract", "Common mistakes", "Exercises"]
---

# 13 Limits on authority

## 13.1 Conditions on operations


### What edition 0.3 adds

An **edition** is a version of the language that a package chooses. Edition `0.3` is a preview: a package opts in with `edition = "0.3"` in `una.toml`, and [chapter 14, Editions](/learn/editions/), explains what that means. It adds three ways to say more about authority:

- A **condition on an operation**: the header says not only what a function may do, but when.
- A **boundary**: a module from outside the store's own code, such as a vendored library, receives only what each call grants it, up to a ceiling written in `una.toml`.
- A **narrowed rebinding**: `with @x = @y[ops]` hands a callee the caller's `@y` restricted to the operations in brackets, at any call. A caller that holds `@directory: Customers` can write `greeting("C-17") with @customers = @directory[find]`, and `greeting` receives only `find`. In editions `0.1` and `0.2` the brackets are a syntax error, U0101. At a boundary it matters most: the ceiling counts every operation a binding permits after narrowing.

### Why an operation needs a condition

A function often has a mode in which it must not act: a dry run, a preview, a rehearsal. The rule "never place an order in a dry run" usually lives in an `if` somewhere in the body, or in a callee, and nothing makes sure every path respects it. One forgotten branch, and the rehearsal places real orders. A condition puts the rule in the header, where the verifier proves it on every path.

### How to write a condition

After the operation's name in the brackets of `uses`, write `where` and a condition over the function's parameters: `uses @supplier: Supplier[order where not dry_run]` lets the function place an order only where `dry_run` is false. The condition is written in the refinement language of [chapter 5](/learn/contracts/#s5-3), like a `requires` clause, and must be a `Bool`. It reads the arguments the caller passed, so its value is fixed for the whole call, even if the body changes an `edit` parameter: a parameter the function may change for its caller ([chapter 16](/learn/memory/#s16-2)). A handler's `uses` may carry conditions too. Operations without `where` in the same brackets are unconditioned.

### A restock with a dry run

The step's `reorder` may place an order only when `dry_run` is false:

```toml include="steps/01-conditions/una.toml" title="steps/01-conditions/una.toml"
[package]
name = "restock"
version = "0.1.0"
edition = "0.3"

[run]
entry = "restock"
grants = ["console"]
```

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

`una run .` prints:

```text include="steps/01-conditions/expected/output.txt"
would order 20 x LAMP-01
ordered 20 x LAMP-01
```

The first call is a dry run, so it only prints. The third finds enough stock and does nothing. In the `else` branch that places the order, the verifier knows that `dry_run` is false, which is the condition.

### How a condition is checked

The verifier proves, at every place where the operation can run, that the condition holds. A call of a function that performs the operation counts as such a place too, so the condition holds through every layer of calls. If `reorder` placed the order without the `dry_run` branch, `una check` would report U5001, with a counterexample in which `dry_run` is true ([running an operation where its condition may not hold](#running-an-operation-where-its-condition-may-not-hold-edition-03-u5001) shows it).

Two rules keep the proof sound:

- **A condition is never inferred.** A private function without `uses` has no condition on any operation.
- **A function with a condition is not a value.** A function can usually be passed to another function as an argument ([chapter 10](/learn/collections/#s10-2)). One whose `uses` carry a condition cannot, since the function that receives it could not prove the condition.

## 13.2 A ceiling for a module: boundaries

### What a boundary is

A package often holds code it did not write, such as a vendored library that prints barcodes. Its functions declare their own `uses`, but a reviewer of the store's code would like a limit that the library's author cannot change: whatever its headers say, it never gets more than this. `una.toml` can mark such a module as a **boundary**, with a **ceiling**: the most the rest of the package may grant it, as a list of capabilities and operations.

### How to write a boundary

Under `[boundaries]` in `una.toml`, one line per module: its name in quotes, `=`, and the list of what it may receive. Here the vendored module is `barcode`, and its ceiling allows `Console[print]`:

```toml include="steps/02-boundaries/una.toml" title="steps/02-boundaries/una.toml"
[package]
name = "shelf"
version = "0.1.0"
edition = "0.3"

[run]
entry = "shelf"
grants = ["console"]

[boundaries]
"barcode" = ["Console[print]"]
```

### Calling into a boundary

This is the vendored module. Its function needs `@console`, which the store's code must grant it:

```una include="steps/02-boundaries/src/barcode.una" title="steps/02-boundaries/src/barcode.una" verified="check, run"
module barcode

--- Prints a shelf label with the SKU spelled out for a barcode font. This module is code from
--- outside the store, so `una.toml` lists it as a boundary.
pub print_label(sku: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("*{sku.to_upper}*")
```

The store's own module calls it, and grants the console at each call with `with`:

```una include="steps/02-boundaries/src/shelf.una" title="steps/02-boundaries/src/shelf.una" verified="check, run"
module shelf

import barcode (print_label)

pub main() -> Unit
  uses @console: Console[print]
=
  print_label("lamp-01") with @console = @console
  print_label("desk-02") with @console = @console
```

`una run .` prints:

```text include="steps/02-boundaries/expected/output.txt"
*LAMP-01*
*DESK-02*
```

### How a boundary is checked

#### Nothing passes by name

A call into a boundary takes nothing by name. The caller grants each capability with `with`, so every call shows what the boundary receives. Leave out the `with` on the second call:

```diff include="steps/02-boundaries..steps/03-boundary-call:src/shelf.una" context="1" title="src/shelf.una"
--- a/src/shelf.una
+++ b/src/shelf.una
@@ -8,2 +8,2 @@
   print_label("lamp-01") with @console = @console
-  print_label("desk-02") with @console = @console
+  print_label("desk-02")
```

```text include="steps/03-boundary-call/expected/rendered.txt"
[U3020] Error: `print_label` is in the boundary `barcode` and needs `@console: Console[print]`, which a call into it grants only with `with`
   ╭─[ src/barcode.una:6:3 ]
   │
 6 │   uses @console: Console[print]
   │   ──────────────┬──────────────
   │                 ╰──────────────── the boundary's requirement
   │
   ├─[ src/shelf.una:9:3 ]
   │
 9 │   print_label("desk-02")
   │   ───────────┬──────────
   │              ╰──────────── `print_label` is in the boundary `barcode` and needs `@console: Console[print]`, which a call into it grants only with `with`
   │
   │ Note: run `una explain U3020` for an explanation
───╯
```

U3020 points at two places: the boundary's requirement, the `uses` line of `print_label`, and the call that does not grant it. `with @console = @console` reads as redundant elsewhere; at a boundary it is the grant.

#### The ceiling holds every grant

The checker holds every grant under the ceiling. If `print_label` also needed a `Clock`, granting it would be U3021, since the ceiling allows only `Console[print]`. A binding that the callee does not need is not counted against the ceiling. A boundary module can never be trusted, so it can never release labeled data ([chapter 17](/learn/information-flow/)).

### A condition, a narrower header or a boundary

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A function that may perform an operation only in some calls, such as never in a dry run | A condition: `op where …` in its `uses` |
| A function that never performs an operation | Leave the operation out of its `uses` |
| Code you did not write to receive at most some authority, whatever its headers say | A boundary with a ceiling, in `una.toml` |
:::

Conditions and boundaries are edition `0.3`. In edition `0.2`, the closest you can come is a narrow header and a review of every call.

### Check yourself: conditions and boundaries

`rehearse` holds `uses @mailer: Mailer[send where not dry_run]` and calls `dispatch(shipments)`, whose header holds `uses @mailer: Mailer[send]` with no condition. Does the call check, with no `if` around it?

:::answer Show the answer
No. `dispatch` may send mail on every call, so the call is a place where `send` can run, and there the verifier must prove `not dry_run`. Nothing tells it what `dry_run` is, so it refutes the condition with `dry_run = true`. [Exercise 3](#exercise-1-a-dry-run-edition-03) starts from exactly this function, and its answer puts the call in the `else` branch of `if dry_run`.
:::


### What a boundary is

When a store lets a contractor in to service the label printer, it gives them a badge that opens the stockroom and nothing else. Whatever the contractor brings, the badge decides which doors open.

A **boundary** is such a badge for a module, written in `una.toml`. It marks a module, usually vendored code from a supplier, and gives it a **ceiling**: the most the rest of the package may ever grant it. A call into the module that would grant more fails the check.

### Why give a module a ceiling

The store copied a label printer's module into `src/vendor/labels.una`. A new version of it arrives, and besides printing, it now reads the clock. Its header says so, but the output does not change:

```diff include="steps/04-boundary..steps/05-unbounded:src/vendor/labels.una" context="0" title="src/vendor/labels.una"
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

This package has no boundary yet. The store accepts the new version with two small edits of its own: `main` declares that it holds the clock, and `una.toml` grants it. Without the first, `una check` reports U3001 at the call; without the second, `una run` stops with U3012 ([chapter 12](/learn/capabilities/#s12-2)).

```diff include="steps/04-boundary..steps/05-unbounded:una.toml" context="0" title="una.toml"
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

```una include="steps/05-unbounded/src/store/app.una" title="steps/05-unbounded/src/store/app.una" verified="check, run"
module store.app

import vendor.labels (print_label)

pub main() -> Unit
  uses @console: Console[print]
  uses @clock: Clock[now]
=
  print_label("LAMP-01", price: "19.90")
```

```text include="steps/05-unbounded/expected/output.txt"
[LAMP-01 | 19.90]
```

The package checks and runs, and the label looks as before. The call itself did not change: `print_label` takes the clock by name, as any call passes the capabilities its callee needs ([chapter 12](/learn/capabilities/#s12-1)). Nothing at the call says where the clock goes, and once the store's code holds a capability for a job of its own, a later version of the supplier's module can start using it with no change at all in the store's code. With network or file access, the same change could send data away. A boundary makes every such grant visible at the call, and turns one beyond the ceiling into an error.

### How to write `[boundaries]`

:::steps
```toml include="steps/04-boundary/una.toml" title="steps/04-boundary/una.toml"
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

1. **`[boundaries]`.** The table of boundaries, in edition `0.3`.
2. **`"vendor.labels"`.** The key: the module path of a module of the package. It also covers every module below it, by whole segments: `vendor.labels` covers `vendor.labels.fonts`, but not `vendor.labelsmith`.
3. **`["Console[print]"]`.** The ceiling: an array of texts, each a capability with the operations it may receive, `Capability[operation, …]`. No binding name and no condition: a ceiling names capabilities and operations only.
:::

### Printing labels through a boundary

The module itself is ordinary Una. It declares what it uses, as any public function does:

```una include="steps/04-boundary/src/vendor/labels.una" title="steps/04-boundary/src/vendor/labels.una" verified="check"
module vendor.labels

--- Prints a shelf label for a product.
pub print_label(sku: Text, price: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("[{sku} | {price}]")
```

The store's code calls it:

```una include="steps/04-boundary/src/store/app.una" title="steps/04-boundary/src/store/app.una" verified="check, run"
module store.app

import vendor.labels (print_label)

pub main() -> Unit
  uses @console: Console[print]
=
  print_label("LAMP-01", price: "19.90") with @console = @console
```

```text include="steps/04-boundary/expected/output.txt"
[LAMP-01 | 19.90]
```

A call into the boundary takes nothing by name. The caller grants each capability with `with`, here `with @console = @console`: the label module's `@console` is the app's own `@console`. So every call into the module shows exactly what it receives.

### How calls into a boundary are checked

A **call into a boundary** is a call from code outside the boundary to a function, handler or policy inside it. Two rules apply to it here ([chapter 13](#s13-1) shows the others), and code inside the boundary calls itself as usual.

#### Everything is granted with `with` (U3020)

Call the label module the usual way, without `with`:

```diff include="steps/04-boundary..steps/06-by-name:src/store/app.una" context="0" title="src/store/app.una"
--- a/src/store/app.una
+++ b/src/store/app.una
@@ -8 +8 @@
-  print_label("LAMP-01", price: "19.90") with @console = @console
+  print_label("LAMP-01", price: "19.90")
```

```text include="steps/06-by-name/expected/rendered.txt"
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

```una include="steps/07-over-ceiling/src/store/app.una" title="steps/07-over-ceiling/src/store/app.una"
module store.app

import vendor.labels (print_label)

pub main() -> Unit
  uses @console: Console[print]
  uses @clock: Clock[now]
=
  print_label("LAMP-01", price: "19.90") with @console = @console, @clock = @clock
```

```text include="steps/07-over-ceiling/expected/rendered.txt"
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

The call grants `Clock[now]`, and the ceiling allows no operation of `Clock`. To accept the new version, someone must widen the ceiling in `una.toml`, which a reviewer sees, or keep the old version.

#### What a boundary key may say

Each of these is U7002: a key that is not a module of the package, a key inside another key's extent, a malformed ceiling, a capability named twice in one ceiling, an unknown capability or operation, a trusted module inside a boundary, and the `[run] entry` inside a boundary. [Chapter 13](#s13-1) shows more of the rules on calls into a boundary.

### A boundary, a lock or neither

:::decide
**Which to use:**

| The code… | Use |
| --- | --- |
| Is yours, and its header is reviewed with it | Nothing: the header and the verifier suffice |
| Is yours, and a header must not widen without a review of `una.toml` | `[contracts]` |
| Comes from a supplier, copied into `src/` | `[boundaries]`, with the least ceiling it needs |
| Comes from a supplier, and you also want its public functions' headers fixed | Both: a boundary for the module, and locks for the functions |
:::

### Check yourself: a module below the boundary

The supplier adds a second module, `src/vendor/labels/fonts.una`, and the app calls it as it would call any module, by name:

```una include="steps/08-fonts/src/vendor/labels/fonts.una" title="steps/08-fonts/src/vendor/labels/fonts.una"
module vendor.labels.fonts

--- Prints a shelf label in large letters.
pub print_large(sku: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("** {sku} **")
```

```una include="steps/08-fonts/src/store/app.una" title="steps/08-fonts/src/store/app.una"
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

```text include="steps/08-fonts/expected/rendered.txt#L1"
[U3020] Error: `print_large` is in the boundary `vendor.labels` and needs `@console: Console[print]`, which a call into it grants only with `with`
```

The key `vendor.labels` covers every module below it, so `vendor.labels.fonts` is in the boundary too, and a call into it grants its capabilities only with `with`. Write `print_large("LAMP-01") with @console = @console`.
:::

## 13.3 Locking a contract: `[contracts]`


### What a locked contract is

When a store signs an agreement with a courier, each side keeps a copy. If someone later edits the agreement on one side, the copies disagree, and the change is noticed. A **locked contract** is such a copy for one function. The function's header says what it may do; `una.toml` keeps a copy of that, under `[contracts]`; and the checker fails when the header allows more than the copy.

> [!WARNING]
> `[contracts]` and `[boundaries]` ([section 13.2](#s13-2)) exist only in edition `0.3`, a preview ([chapter 14, Editions](/learn/editions/#s19-3)). In a package of edition `0.2`, each is an unknown table, U7002. Since `0.3` is a preview, a later release may add obligations or errors to an edition `0.3` package.

A function's header can say not only which operations it may perform, but when. `uses @prices: PriceList[set_price where not dry_run]` says that `set_price` runs only when `dry_run` is false ([chapter 8, Capabilities](#s13-1), shows these conditions). The verifier proves that the body keeps that promise.

### Why lock a header

A header is code, and an edit to the code can change it. Here is a sale function whose header and body both lost their condition in the same edit: the header no longer says "never on a dry run", and the body no longer checks `dry_run`.

```diff include="steps/09-locked..steps/10-unlocked:src/store/sale.una" context="1" title="src/store/sale.una"
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

```text include="steps/10-unlocked/expected/output.txt"
set DESK-02 to 19920
a dry run plans 19920
set LAMP-01 to 1791
the sale applied 1791
```

The first line is a price change during a dry run, which the doc comment still says cannot happen. The verifier proved that the body keeps its header, but the header itself changed, and no rule said it should not. A reviewer must notice that a line of the header disappeared, in a change that may touch many files.

Locking moves the decision out of the code. With the condition copied into `una.toml`, the header can lose it only if the manifest changes too, and a change to `una.toml` is easy to see and to require a review for.

### How to write `[contracts]`

A lock is one line under `[contracts]`:

:::steps
```toml include="steps/09-locked/una.toml" title="steps/09-locked/una.toml"
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

1. **`[contracts]`.** The table of locks. A package of edition `0.3` may have one.
2. **`"store.sale.apply_sale"`.** The key: the **qualified name** of a public function of the package, its module path, a dot, and its name. It is in quotes, since it holds dots.
3. **`["…"]`.** The value: an array of `uses` clauses, each a text written as the header writes it, without the word `uses`.
4. **`@prices: PriceList[set_price where not dry_run]`.** One clause: the binding, its capability, and in brackets the operations the function may perform, each with its condition when it has one.
:::

#### Several bindings, and operations without a condition

A lock lists every binding the header has, and an operation may be listed with or without a condition. This step locks two functions:

```toml include="steps/11-lock-forms/una.toml" title="steps/11-lock-forms/una.toml"
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

```una include="steps/11-lock-forms/src/store/sale.una" title="steps/11-lock-forms/src/store/sale.una" verified="check"
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

```una include="steps/11-lock-forms/src/store/app.una" title="steps/11-lock-forms/src/store/app.una" verified="check, run"
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

```text include="steps/11-lock-forms/expected/output.txt"
LAMP-01 costs 1990
audit: LAMP-01: 1990 to 1791
a dry run plans 1791
```

The dry run reads the price and writes the audit line, and sets no price.

### A sale that cannot lose its dry run

Back to the sale of [Why lock a header](#why-lock-a-header), with its condition, its guard, and the lock of [How to write `[contracts]`](#how-to-write-contracts):

```una include="steps/09-locked/src/store/sale.una" title="steps/09-locked/src/store/sale.una" verified="check"
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

```una include="steps/09-locked/src/store/app.una" title="steps/09-locked/src/store/app.una" verified="check, run"
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

```text include="steps/09-locked/expected/output.txt"
a dry run plans 19920
set LAMP-01 to 1791
the sale applied 1791
```

The dry run of the desk plans its sale price and sets nothing. The real sale of the lamp sets its price. The handler `printed` prints each change instead of storing it, so you see when `set_price` runs.

### How a lock is checked

The body and the lock are checked separately. The verifier proves that the body keeps its header, as [chapter 13](#s13-1) showed. The lock adds one more check: that the header keeps the lock. The header must grant no more than its lock.

#### A header may grant less

A header may grant less than its lock, since that only narrows what the function may do: fewer operations, a stronger condition, or no binding of a capability that the lock names. A binding that the lock does not name at all, or an operation that it does not list, is U3023.

#### An operation the lock does not list

Give `show_price` the right to set prices too:

```diff include="steps/11-lock-forms..steps/12-extra-op:src/store/sale.una" context="0" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -14 +14 @@
-  uses @prices: PriceList[price]
+  uses @prices: PriceList[price, set_price]
```

```text include="steps/12-extra-op/expected/rendered.txt"
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

```diff include="steps/09-locked..steps/13-weakened:src/store/sale.una" context="0" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -9 +9 @@
-  uses @prices: PriceList[set_price where not dry_run]
+  uses @prices: PriceList[set_price]
```

```text include="steps/13-weakened/expected/rendered.txt#L1-L12,L14,L18"
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
    │ Help: repair 1: restore the locked condition: write `set_price where not dry_run` in the header of `apply_sale`, or a condition that implies it; edit src/store/sale.una:9:36..9:36 to " where not dry_run"
    │ Note 2: counterexample: dry_run = true
```

The header now allows what the lock forbids, and the counterexample says when: `dry_run = true`. The body would still behave, since its guard is still there, but the promise the header makes is weaker than the lock, and that is what U3023 reports. The repair writes the condition back, and `una fix .` applies it: it changes the module, never `una.toml`. To weaken the contract, someone must change `una.toml`, and that change is what a reviewer sees.

#### What a lock may say

Each of these is U7002, at the lock's line: a key that names no public function of the package; a text that does not parse, or lists no operation; one binding locked twice; a capability that the function's module does not see; an operation that the capability does not declare; and a condition that is not a `Bool` over the function's parameters.

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

```diff include="steps/09-locked..steps/14-narrower:src/store/sale.una" context="0" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -9 +9 @@
-  uses @prices: PriceList[set_price where not dry_run]
+  uses @prices: PriceList[set_price where not dry_run and percent > 0]
@@ -12 +12 @@
-  if not dry_run
+  if not dry_run and percent > 0
```

```una include="steps/14-narrower/src/store/app.una#main" title="steps/14-narrower/src/store/app.una"
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

```text include="steps/14-narrower/expected/output.txt"
a dry run plans 19920
set LAMP-01 to 1791
the sale applied 1791
a sale of 0 percent keeps 4500
```

A sale of 0 percent changes nothing, so the guard skips `set_price`, and no `set` line is printed for the rug.
:::

## 13.4 Common mistakes

### Running an operation where its condition may not hold, edition 0.3 (U5001)

:::mistake
In the step of [A restock with a dry run](#a-restock-with-a-dry-run), place the order without the dry-run branch:

```diff include="steps/01-conditions..mistakes/1:src/restock.una" context="1" title="src/restock.una"
--- a/src/restock.una
+++ b/src/restock.una
@@ -13,4 +13,2 @@
     unit
-  else if dry_run
-    @console.print("would order 20 x {sku}")
   else
```

```text include="mistakes/1/expected/rendered.txt#L1,L12,L18"
[U5001] Error: `@supplier.order` may run where `not dry_run` is not proven
    │ Help 1: repair 1: guard the operation with `if not dry_run`
    │ Note 2: counterexample: dry_run = true, left = 4
```

*Why:* the dry-run branch looks like a nicety and is easy to drop. The header allows `order` only where `not dry_run` holds, and the verifier finds a run where it does not: the counterexample has `dry_run = true` with `left = 4`, few enough units to order. The marks show the condition in the header and the operation that may break it.

*Fix:* the repair una lists first, a guard, which the step has as its `else if dry_run` branch.
:::

### A `0.3` table in an edition `0.2` package (U7002)

:::mistake
Lock the catalog lookup in the day-to-day manifest:

```diff include="steps/15-stores-invoice..mistakes/2:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -8 +8,4 @@
 grants = ["console"]
+
+[contracts]
+"store.invoice.product_of" = ["@catalog: Catalog[find]"]
```

```text include="mistakes/2/expected/rendered.txt"
[U7002] Error: unknown table [contracts] in una.toml
    ╭─[ una.toml:10:2 ]
    │
 10 │ [contracts]
    │  ────┬────
    │      ╰────── unknown table [contracts] in una.toml
    │
    │ Note: run `una explain U7002` for an explanation
────╯
```

*Why:* `[contracts]` exists only in edition `0.3`. In edition `0.2`, it is a table una does not know, and the mark points at its line in `una.toml`.

*Fix:* set `edition = "0.3"` if you want the preview's rules, or remove the table. See [U7002](/docs/errors/U7002/).
:::

## 13.5 Exercises

### Exercise 1: a dry run (edition 0.3)

::::exercise
Before a big batch, the operator wants a rehearsal that sends nothing. The start package switches to edition `0.3` and adds `rehearse`, whose header allows `send` only where `not dry_run` holds:

```una include="exercises/1/start/src/notices.una#rehearse" title="exercises/1/start/src/notices.una"
--- Like `dispatch`, but a dry run only logs what it would send. Exercise 3: make the dry run
--- send nothing.
pub rehearse(shipments: List[Shipment], dry_run: Bool) -> Unit
  uses @customers: Customers[find]
  uses @mailer: Mailer[send where not dry_run]
  uses @log: Console[print]
=
  dispatch(shipments)
```

Its body calls `dispatch` in every case, so `una check .` reports:

```text include="exercises/1/start/expected/rendered.txt#L1"
[U5001] Error: `@mailer.send` may run where `not dry_run` is not proven
```

The start package also has two examples: a dry run performs `@log.print` and not `@mailer.send`, and a real run performs `@mailer.send`.

:::hint
*Hint:* replace the body with an `if dry_run` that has two branches. In the dry-run branch, loop over the shipments with `for` and log one line per shipment on `@log`, such as `would notify A-1001`, and call nothing that uses `@mailer`. In the `else` branch, call `dispatch(shipments)` as before: there the verifier knows `dry_run` is false, which proves the condition.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Branch on `dry_run`:

```diff include="exercises/1/start..exercises/1/answer:src/notices.una" context="1" title="src/notices.una"
--- a/src/notices.una
+++ b/src/notices.una
@@ -76,4 +76,3 @@
 
---- Like `dispatch`, but a dry run only logs what it would send. Exercise 3: make the dry run
---- send nothing.
+--- Like `dispatch`, but a dry run only logs what it would send.
 pub rehearse(shipments: List[Shipment], dry_run: Bool) -> Unit
@@ -83,3 +82,7 @@
 =
-  dispatch(shipments)
+  if dry_run
+    for shipment in shipments
+      @log.print("would notify {shipment.order}")
+  else
+    dispatch(shipments)
 
```

In the `else` branch, `dry_run` is false, so the verifier proves the condition at the call of `dispatch`.
:::
::::

### Exercise 2: honor a lock

::::exercise
This exercise starts from the sale package of [section 13.3](#s13-3), in edition `0.3`. It adds `end_sale`, which puts a product's old price back, and a lock for it in `una.toml`:

```toml include="exercises/2/start/una.toml" title="exercises/2/start/una.toml"
[package]
name = "store"
version = "0.1.0"
edition = "0.3"

[run]
entry = "store.app"
grants = ["console"]

# What the sale functions may do with the price list, and when.
[contracts]
"store.sale.apply_sale" = ["@prices: PriceList[set_price where not dry_run]"]
"store.sale.end_sale" = ["@prices: PriceList[set_price where not dry_run]"]
```

```una include="exercises/2/start/src/store/sale.una#L16-L34" title="exercises/2/start/src/store/sale.una"
--- Puts back the price a product had before its sale. Exercise 3: honor the lock in `una.toml`.
pub end_sale(sku: Text, cents: Int, dry_run: Bool) -> Unit
  uses @prices: PriceList[set_price]
=
  @prices.set_price(sku, cents: cents)

--- A price list that keeps nothing, for examples.
handler ignored() for PriceList
  op set_price(sku, cents) = unit

example "a dry run of the end of a sale changes no price"
  given @prices = ignored()
  do end_sale("DESK-02", cents: 24900, dry_run: true)
  expect not performed @prices.set_price

example "the end of a sale sets the old price back"
  given @prices = ignored()
  do end_sale("DESK-02", cents: 24900, dry_run: false)
  expect performed @prices.set_price
```

`una check .` reports that the header lets `set_price` run when `dry_run` is true:

```text include="exercises/2/start/expected/diagnostics.txt"
error U3023 at src/store/sale.una:18:27: the header of `end_sale` lets `@prices.set_price` run where `not dry_run` does not hold, which `una.toml` locks
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

Check your answer with `una test .`. Both examples must pass: a dry run sets no price, and a real one does.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Write the locked condition in the header, and guard the operation to match it:

```diff include="exercises/2/start..exercises/2/answer:src/store/sale.una" context="1" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -15,7 +15,8 @@
 
---- Puts back the price a product had before its sale. Exercise 3: honor the lock in `una.toml`.
+--- Puts back the price a product had before its sale. A dry run changes nothing.
 pub end_sale(sku: Text, cents: Int, dry_run: Bool) -> Unit
-  uses @prices: PriceList[set_price]
+  uses @prices: PriceList[set_price where not dry_run]
 =
-  @prices.set_price(sku, cents: cents)
+  if not dry_run
+    @prices.set_price(sku, cents: cents)
 
```

The header now keeps the lock, and the body keeps the header: two separate proofs, as in [How a lock is checked](#how-a-lock-is-checked).
:::
::::
