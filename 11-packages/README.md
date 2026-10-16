---
learn: "11"
title: Packages and modules
editions: ["0.2", "0.3"]
codes: [U1001, U1002, U1003, U1004, U1008, U3023, U5001, U7001, U7002]
time: 40
builds: A store's invoice, split into modules for money, the catalog, prices and the invoice itself
prerequisites: ["6", "7", "8", "10"]
template: 2
---

# 11 Packages and modules

A program of one file is easy to read until it grows. Then the price rules, the catalog and the invoice text sit side by side, any function can call any other, and a reviewer cannot tell which functions other parts of the program are meant to use. In Una a package is split into modules, one file each. A module shares only what it marks `pub`, and every other module names what it takes with `import`. This chapter splits a store's invoice into modules, walks through `una.toml`, and locks the contracts of public functions in edition `0.3`.

## What you'll build

:::build
An invoice for a small store, split into five modules: one for money, one for the catalog service, one for prices, one for the invoice lines, and one that runs it all. Each module has its own examples, and `una test` runs them together. The invoice reads:

```text include="day-to-day/expected/output.txt"
2 x Desk lamp at 19.90 (members 17.91): 39.80
1 x Oak desk at 249.00 (members 224.10): 249.00
CHAIR-09: not in the catalog
```

You will learn to:

- lay out a package: one module per file, named after its path under `src/`;
- decide what a module shares with `pub`, and take it elsewhere with `import`;
- read and write `una.toml`, and know what `verification.lock` pins;
- lock the `uses` of a public function in `una.toml`, and give a vendored module a ceiling, in edition `0.3`;
- test a package of several modules with one command.
:::

## Why it works this way

In many languages, a file can see a great deal it never asked for: every public name of every file in the project, globals, and whatever an import brings in with it. Splitting a program into files does not, by itself, say which parts are the interface of a file and which are its details. A dependency added by one line in a manifest can bring in code that reads files or opens connections, and nothing in the caller's code shows it. In una 0.3.14 a package has no dependencies on other packages ([section 11.3](#s11-3)).

Una keeps the structure small and visible:

:::steps
1. **One file is one module, and its path is its name.** `src/store/money.una` holds the module `store.money`, and nothing else.
2. **Private by default.** A declaration is visible outside its module only when it says `pub`. A `pub` function's header is its contract with the rest of the package, so it declares its `uses` and `fails`, as [chapter 6, Failure](/learn/failure/), and [chapter 8, Capabilities](/learn/capabilities/), showed.
3. **Every import is named.** `import store.money (format)` takes one declaration, by name. There is no import of everything.
4. **The manifest is checked.** `una.toml` holds a fixed set of tables, and a table or key that una does not know is an error, not a setting that is silently ignored.
:::

> [!KEY]
> A module's `pub` declarations are its interface, and its imports say exactly what it uses of other modules. Both are in the source, where a reviewer reads them.

## 11.1 Modules: one file each

A package is a directory with `una.toml`, `verification.lock` and `src/`, as in [chapter 1, Hello, Una](/learn/hello/#s1-1). Each file under `src/` is a module, and its name is its path: `src/store/money.una` is `store.money`, and its first line must say so. A directory under `src/` only groups modules. It is not a module itself.

There is no list of modules to keep up to date. `una check .` reads every `.una` file under `src/`, checks all of them together, and reports each diagnostic with its file, so a new file is part of the package as soon as it exists. `una run .` starts at one module, the entry, and `una test .` runs the examples of every module.

This first step has two modules. `store.money`, in `src/store/money.una`, formats an amount, and `store.app`, in `src/store/app.una`, prints with it:

```una include="steps/01-modules/src/store/money.una" title="steps/01-modules/src/store/money.una" verified="check"
module store.money

--- An amount in cents as a person reads it: 1990 is "19.90".
pub format(cents: Int) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"
```

```una include="steps/01-modules/src/store/app.una" title="steps/01-modules/src/store/app.una" verified="check, run"
module store.app

import store.money (format)

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("a lamp costs {format(1990)}, a desk {format(24905)}")
```

:::steps
1. **`module store.money`.** The header names the module. A file whose header does not match its path is U1008 (mistake 1 shows it).
2. **`pub format(...)`.** `pub` makes `format` part of the module's interface. Without it, no other module could import it.
3. **`import store.money (format)`.** An import names a module of the package, then, in parentheses, each declaration it takes. In the importing module, `format` is then a plain name.
4. **`cents mod 100`.** `mod` is the remainder of a division, as `/` is its quotient.
:::

`una.toml` says which module `una run` starts: `[run] entry` is a module path, here `store.app`, and that module has the `pub main`.

```toml include="steps/01-modules/una.toml" title="steps/01-modules/una.toml"
[package]
name = "store"
version = "0.1.0"
edition = "0.2"

[run]
entry = "store.app"
grants = ["console"]
```

`una run .` prints:

```text include="steps/01-modules/expected/output.txt"
a lamp costs 19.90, a desk 249.05
```

Group modules by what they are about, not by what kind of declaration they hold: `store.money` keeps the type of an amount, its formatting and its tests together. A reader who wants to know how amounts are printed then opens one file.

A module path follows the file system, so moving a file renames its module. The checker then reports the header that no longer matches, and every import of the old name, so nothing is left pointing at a module that is gone.

## 11.2 `pub` and `import`

`pub` goes on a function, a kind, a capability, a handler, a predicate or a policy. An `example` or a `requirement` is never `pub`. What an import brings in depends on what it names:

- **A function or a handler** is then used by its plain name.
- **A record kind** brings its type and its constructor: `Product(sku: …, name: …, cents: …)` works in the importing module, and so do its fields.
- **A sum kind** brings its variants with it: importing `InvoiceError` lets the module write `fail UnknownSku(…)`. A `when` needs no import to match a variant, since its arms take the variants of the value's type.
- **A capability** brings the name a `uses` clause needs. Its operations come with it.

This step adds a kind for amounts to `store.money`, and a catalog module with a record, a capability and a handler, all `pub`. The kind `Cents`, an `Int` that is never below zero, is a refined kind of [chapter 7, Contracts and the verifier](/learn/contracts/), and `store.catalog` imports it from `store.money` like any other declaration:

:::steps
```una include="steps/02-imports/src/store/catalog.una" title="steps/02-imports/src/store/catalog.una" verified="check"
module store.catalog

import store.money (Cents)

--- A product the store sells.
pub kind Product
  sku: Text
  name: Text
  cents: Cents

--- The catalog service: the product with a SKU, or `None` for a SKU it does not list.
pub capability Catalog
  op find(sku: Text) -> Option[Product]

--- A catalog held in memory, for runs and tests.
pub handler listed(products: List[Product]) for Catalog
  op find(sku) = products.first_where(keep: fn(product) -> product.sku == sku)
```

1. **`import store.money (Cents)`.** A module imports what it uses, even another module's kinds. `Product.cents` is a `Cents`, so a negative price cannot be built anywhere in the package.
2. **`pub kind Product`.** The record, its constructor and its fields are part of the interface.
3. **`pub capability Catalog`.** Code in other modules can now declare `uses @catalog: Catalog[find]`.
4. **`pub handler listed(...)`.** A handler is shared like a function, so every module and every example can run against the same in-memory catalog.
:::

The money module now keeps a private helper, `digits`, next to its public `format`:

```una include="steps/02-imports/src/store/money.una" title="steps/02-imports/src/store/money.una" verified="check"
module store.money

--- An amount of money in cents, never below zero.
pub kind Cents = Int where it >= 0

--- An amount in cents as a person reads it: 1990 is "19.90", and -150 is "-1.50".
pub format(cents: Int) -> Text = if cents < 0 then "-{digits(0 - cents)}" else digits(cents)

--- The digits of an amount of 0 or more, with two after the point.
digits(cents: Int) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"
```

And the app takes what it needs, one name at a time:

```una include="steps/02-imports/src/store/app.una" title="steps/02-imports/src/store/app.una" verified="check, run"
module store.app

import store.catalog (Catalog, Product, listed)
import store.money (format)

--- Why a price could not be shown.
kind PriceError = | NotListed(sku: Text)

--- The price of a SKU, as a person reads it.
price_tag(sku: Text) -> Text
  uses @catalog: Catalog[find]
  fails PriceError
=
  let product = @catalog.find(sku)
    if none fail NotListed(sku)
  "{product.name}: {format(product.cents)}"

pub main() -> Unit
  uses @console: Console[print]
=
  let products = [Product(sku: "LAMP-01", name: "Desk lamp", cents: 1990)]
  let lamp = attempt price_tag("LAMP-01") with @catalog = listed(products)
  let chair = attempt price_tag("CHAIR-09") with @catalog = listed(products)
  @console.print("{lamp}")
  @console.print("{chair}")
```

```text include="steps/02-imports/expected/output.txt"
Ok("Desk lamp: 19.90")
Err(NotListed("CHAIR-09"))
```

`PriceError` and `price_tag` have no `pub`, so they belong to `store.app` alone. A private function may leave its `uses` and `fails` to inference, but `price_tag` writes them, so its header can be read without its body.

### Private stays private

Try to import `digits`:

```diff include="steps/02-imports..steps/03-private:src/store/app.una" context="0" title="src/store/app.una"
--- a/src/store/app.una
+++ b/src/store/app.una
@@ -4 +4 @@
-import store.money (format)
+import store.money (digits, format)
```

```text include="steps/03-private/expected/rendered.txt#L1,L14"
[U1004] Error: function `digits` is private to module `store.money`
    │ Help: repair 1 (widens visibility: every module may then call it: check that it belongs to the module's interface): declare `digits` with `pub`; edit src/store/money.una:10:1..10:1 to "pub "
```

The checker offers the repair, adding `pub`, but it marks the repair as one that widens visibility. `una fix .` does not apply such a repair by itself: making a helper public is a decision about the module's interface, and you take it by editing the declaration, with a doc comment for its new callers.

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A function, kind or handler that other modules need | `pub`, with a doc comment, and every clause of its header written |
| A helper that only this module uses | no `pub`: it stays private, and may infer its `uses` and `fails` |
| A declaration of another module | `import module.path (name, …)`, one name per declaration |
| A host capability's name, written explicitly | `import std.host (Console)`, optional, since the prelude has it |
:::

## 11.3 The manifest and the lock

`una.toml` describes the package. In edition `0.2` it has five tables, and no others:

| Table | Keys | What it says |
| --- | --- | --- |
| `[package]` | `name`, `version`, `edition` | The package, and the edition of the language its modules are written in. Required. |
| `[run]` | `entry`, `grants` | The module that `una run` starts, and the host capabilities it is granted, besides those of a `--grant` flag. |
| `[labels]` | `categories` | The categories that labels may name ([chapter 9, Information flow](/learn/information-flow/)). |
| `[trusted]` | `modules` | The modules that may declare policies, each also marked `trusted module` in its header. |
| `[escape_budget]` | `checked_per_module` | How many uses of `checked` each module may have, 0 by default ([chapter 6, Failure](/learn/failure/)). |

Here is a manifest that uses four of them, with a comment on each. TOML comments start with `#`:

```toml include="steps/04-manifest/una.toml" title="steps/04-manifest/una.toml"
# The package: its name, its version, and the edition of the language it is written in.
[package]
name = "store"
version = "0.2.0"
edition = "0.2"

# What `una run` starts, and the host capabilities it grants, besides those of a `--grant` flag.
[run]
entry = "store.app"
grants = ["console"]

# The categories that labels may name.
[labels]
categories = ["PII"]

# How many uses of `checked` each module may have.
[escape_budget]
checked_per_module = 0
```

The package still runs as before. A table or key that is not in this list is U7002, with the line of the manifest: mistake 6 shows one.

### No dependencies on other packages yet

una 0.3.14 has no way to depend on another package: `una.toml` has no dependency table, and a package imports only its own modules and two standard modules, `std.host` and `std.testing`. Importing anything else says so:

```text include="steps/05-no-dependencies/expected/rendered.txt#L1"
[U1001] Error: module `vendor.tax` is not a module of this package; the standard modules that can be imported are `std.host` and `std.testing`
```

So everything a package runs is in its own `src/`, the prelude, or the host capabilities that `una run` grants, in `[run] grants` or by a `--grant` flag. Until a release adds dependencies, code from elsewhere, such as a supplier's library, is copied into `src/` as modules of the package, where the checker sees all of it. Edition `0.3` can then give such a module a ceiling, as [section 11.4](#s11-4) shows.

### `verification.lock`

`verification.lock` is the other file at the root of every package. It pins the verifier: the encoding of the queries, the solver and its version (`z3`, `5.1.0`), their logic, a step budget and a random seed. With the same sources, `una.toml` and lock, `una check` gives the same diagnostics and the same proofs on every machine. A missing or invalid lock is U7004, and a solver of another version is U5003. You rarely edit it: copy it from an existing package, and change it only to adopt a new solver, in a change of its own.

## 11.4 Locks in edition `0.3`: `[contracts]` and `[boundaries]`

Edition `0.3` is a preview ([chapter 14, Editions](/learn/editions/)), and it adds two tables to `una.toml`. Both move a decision out of the code and into the manifest, where it is reviewed apart.

### Locking a contract

A function's header can say not only what it may do, but when: `uses @prices: PriceList[set_price where not dry_run]` says that `set_price` runs only when `dry_run` is false ([section 8.5 of chapter 8, Capabilities](/learn/capabilities/#s8-5), shows these conditions). But a header is code, and an edit to the code can delete the condition. `[contracts]` locks it:

```toml include="steps/06-locked/una.toml" title="steps/06-locked/una.toml"
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

```una include="steps/06-locked/src/store/sale.una" title="steps/06-locked/src/store/sale.una" verified="check"
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

```una include="steps/06-locked/src/store/app.una" title="steps/06-locked/src/store/app.una" verified="check, run"
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

```text include="steps/06-locked/expected/output.txt"
a dry run plans 19920
set LAMP-01 to 1791
the sale applied 1791
```

Each key of `[contracts]` is the qualified name of a public function, its module path then its name. Each value lists `uses` clauses, written as a header writes them. The header must grant no more than its lock. It may grant less, with a stronger condition or fewer operations, since that only narrows what the function may do. A binding that the lock does not name, or an operation it does not list, is U3023 as well.

The lock and the body are checked separately. The verifier proves that the body keeps its header, as [chapter 8](/learn/capabilities/#s8-5) showed: without `if not dry_run`, `set_price` could run on a dry run, and the check fails. The lock adds one more proof, that the header keeps the lock. Now delete the condition from the header:

```diff include="steps/06-locked..steps/07-weakened:src/store/sale.una" context="0" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -9 +9 @@
-  uses @prices: PriceList[set_price where not dry_run]
+  uses @prices: PriceList[set_price]
```

```text include="steps/07-weakened/expected/rendered.txt#L1-L12,L14,L18"
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
    │ Help: repair 1: restore the locked condition: write `set_price where not dry_run` in the header of `apply_sale`, or a condition that implies it
    │ Note 2: counterexample: dry_run = true
```

The header now allows what the lock forbids, and the counterexample says when: `dry_run = true`. To weaken the contract, someone must change `una.toml`, and that change is what a reviewer sees.

### Giving a module a ceiling

`[boundaries]` marks a module, such as code from a supplier, as a boundary, with a ceiling: the most the rest of the package may ever grant it. The key is a module of the package, and it covers the modules below it too: `vendor.labels` also covers a module `vendor.labels.fonts`. A directory with no module of its own name cannot be a key. Here the label printer's module may receive the console, and nothing else:

```toml include="steps/08-boundary/una.toml" title="steps/08-boundary/una.toml"
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

The module itself is ordinary Una. It declares what it uses, as any public function does:

```una include="steps/08-boundary/src/vendor/labels.una" title="steps/08-boundary/src/vendor/labels.una" verified="check"
module vendor.labels

--- Prints a shelf label for a product.
pub print_label(sku: Text, price: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("[{sku} | {price}]")
```

The store's code calls it:

```una include="steps/08-boundary/src/store/app.una" title="steps/08-boundary/src/store/app.una" verified="check, run"
module store.app

import vendor.labels (print_label)

pub main() -> Unit
  uses @console: Console[print]
=
  print_label("LAMP-01", price: "19.90") with @console = @console
```

A call into the boundary takes nothing by name. The caller grants each capability with `with`, here `with @console = @console`, so every call shows exactly what the module receives. A call that leaves a capability to be taken by name is U3020, and one that grants beyond the ceiling is U3021. [Section 8.5 of chapter 8, Capabilities](/learn/capabilities/#s8-5), shows the rules and their diagnostics.

```text include="steps/08-boundary/expected/output.txt"
[LAMP-01 | 19.90]
```

> [!WARNING]
> `[contracts]` and `[boundaries]` exist only in edition `0.3`. In a package of edition `0.2`, each is an unknown table, U7002. Since `0.3` is a preview, a later release may add obligations or errors to an edition `0.3` package.

## 11.5 Day-to-day: the store's invoice

Now the program from the start of the chapter. An order is a list of SKUs with quantities. The invoice looks each SKU up in the catalog, prices the line, shows what a member would pay for one unit, and names the SKUs the catalog does not list. Five modules under `src/store/` share the work:

- `money.una`: `Cents`, and `format` for amounts as people read them;
- `catalog.una`: `Product`, the `Catalog` service, and an in-memory catalog;
- `pricing.una`: line prices and the members' price;
- `invoice.una`: order lines, lookups, and the text of each line;
- `app.una`: `main`, the entry of the package.

The imports form a graph with no cycle: `money` imports nothing, `catalog` and `pricing` import `money`, `invoice` imports the three, and `app` imports `catalog` and `invoice`. An import cycle is U1003 (mistake 4).

Each import goes from a module that knows more to one that knows less. `money` knows nothing of products, and `pricing` takes amounts, not products, so a price rule can be tested without a catalog. Only `invoice` puts a product, its price and its text together, and only `app` decides which catalog the program runs against.

The `pub` lines are the interface of each module. `money` shares `Cents` and `format`. `catalog` shares all it declares. `pricing` shares `line_cents` and `member_price`, and keeps `discount`. `invoice` shares its two kinds and its two functions. `app` shares only `main`, which `una run` needs, since the entry's `main` must be `pub`.

**Money.** The same module as in [section 11.2](#s11-2), with its examples. `format` handles a negative amount, for a refund, and its private helper handles the digits:

```una include="day-to-day/src/store/money.una" title="day-to-day/src/store/money.una" verified="check"
module store.money

--- An amount of money in cents, never below zero.
pub kind Cents = Int where it >= 0

--- An amount in cents as a person reads it: 1990 is "19.90", and -150 is "-1.50".
pub format(cents: Int) -> Text = if cents < 0 then "-{digits(0 - cents)}" else digits(cents)

--- The digits of an amount of 0 or more, with two after the point.
digits(cents: Int) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"

example "two digits after the point"
  do format(1990)
  expect result == "19.90"

example "a leading zero is kept"
  do format(24905)
  expect result == "249.05"

example "a refund keeps its sign"
  do format(-150)
  expect result == "-1.50"
```

**The catalog.** Unchanged from [section 11.2](#s11-2): the record, the service, and a handler that holds the products in a list. `listed` takes the products as a parameter where it is installed, so the app and each example choose the catalog they need, and the module keeps no product list of its own.

```una include="day-to-day/src/store/catalog.una" title="day-to-day/src/store/catalog.una" verified="check"
module store.catalog

import store.money (Cents)

--- A product the store sells.
pub kind Product
  sku: Text
  name: Text
  cents: Cents

--- The catalog service: the product with a SKU, or `None` for a SKU it does not list.
pub capability Catalog
  op find(sku: Text) -> Option[Product]

--- A catalog held in memory, for runs and tests.
pub handler listed(products: List[Product]) for Catalog
  op find(sku) = products.first_where(keep: fn(product) -> product.sku == sku)
```

**Pricing.** Two public functions and one private helper:

```una include="day-to-day/src/store/pricing.una" title="day-to-day/src/store/pricing.una" verified="check, test"
module store.pricing

import store.money (Cents)

--- The price of `quantity` units at `cents` each.
pub line_cents(cents: Cents, quantity: Int) -> Int = cents * quantity

--- What a member pays: 10 percent off, rounded in the store's favor.
pub member_price(cents: Cents) -> Int
  ensures result >= 0 and result <= cents
=
  cents - discount(cents)

--- The members' discount, rounded down to a whole cent.
discount(cents: Cents) -> Int
  ensures result >= 0 and result <= cents
=
  cents / 10

example "members pay 10 percent less"
  do member_price(24900)
  expect result == 22410

example "the discount rounds down"
  do discount(1999)
  expect result == 199
```

`line_cents` returns a plain `Int`, not a `Cents`. `quantity` is any `Int`, so a line of -1 units gives a negative total, and a `Cents` result is refuted (U5001, with `quantity = -1`). Even with a quantity of 0 or more, the verifier leaves the product of two values uninterpreted, so it could not prove the result is 0 or more (U5002). `format` takes any `Int` for that reason.

`member_price` promises that a member never pays more than the price, nor less than 0. The verifier proves that promise from `discount`'s header, not from its body, so `discount` states its own bounds in `ensures`. Both take a `Cents`, so neither can be called with a negative price. `discount` stays private: the invoice shows what a member pays, not how the discount is computed. Exercise 2 changes that decision on purpose.

**The invoice.** It imports from three modules, and is the only module that knows how an invoice line reads:

```una include="day-to-day/src/store/invoice.una#L1-L28" title="day-to-day/src/store/invoice.una"
module store.invoice

import store.catalog (Catalog, Product, listed)
import store.money (format)
import store.pricing (line_cents, member_price)

--- Why a line could not be invoiced.
pub kind InvoiceError = | UnknownSku(sku: Text)

--- One line of an order: a SKU and how many units of it.
pub kind OrderLine
  sku: Text
  quantity: Int

--- The product an order line names.
pub product_of(line: OrderLine) -> Product
  uses @catalog: Catalog[find]
  fails InvoiceError
=
  @catalog.find(line.sku)
    if none fail UnknownSku(sku: line.sku)

--- One line of the invoice, as text, with the members' price of one unit.
pub describe(line: OrderLine, product: Product) -> Text
=
  let total = line_cents(product.cents, quantity: line.quantity)
  let member = member_price(product.cents)
  "{line.quantity} x {product.name} at {format(product.cents)} (members {format(member)}): {format(total)}"
```

`product_of` turns a missing product into its own failure, `UnknownSku`, with the SKU. `describe` is pure, so a test can call it with any product, without a catalog. It uses three imported functions, `line_cents`, `member_price` and `format`, and the import lines at the top of the file name each of them, so a reader knows where to look for each one.

**The app.** It runs the order against an in-memory catalog. `attempt` keeps each lookup's outcome, so an unknown SKU becomes a line of the invoice instead of stopping it:

```una include="day-to-day/src/store/app.una" title="day-to-day/src/store/app.una" verified="check, run"
module store.app

import store.catalog (Product, listed)
import store.invoice (OrderLine, describe, product_of)

pub main() -> Unit
  uses @console: Console[print]
=
  let products = [Product(sku: "LAMP-01", name: "Desk lamp", cents: 1990), Product(sku: "DESK-02", name: "Oak desk", cents: 24900)]
  let order = [OrderLine(sku: "LAMP-01", quantity: 2), OrderLine(sku: "DESK-02", quantity: 1), OrderLine(sku: "CHAIR-09", quantity: 1)]
  for line in order
    let found = attempt product_of(line) with @catalog = listed(products)
    when found
      is Ok(product) -> @console.print(describe(line, product: product))
      is Err -> @console.print("{line.sku}: not in the catalog")
```

`store.app` imports `product_of` and `describe`, but not `InvoiceError`. It never writes that type's name, and `is Err` matches any failure. A module imports a kind when it writes the kind, in a parameter's type for example, or builds one of its variants.

`main` installs `listed(products)` for each lookup with `with`. In a real store, a handler that calls the catalog service would take its place, and no other module would change: `invoice` names the `Catalog` capability, never a handler.

The whole package checks, runs and passes its tests. `una run .` prints the invoice shown under "What you'll build".

## 11.6 Testing it

Each module carries the examples of its own functions, and `una test .` runs every example of every module, module by module. It checks the whole package first: when any module has a diagnostic, it reports them all and runs no example, since the package as a whole is what the examples test.

```text include="day-to-day/expected/commands/test.txt"
$ una test .
example store.invoice "a known SKU is found" ... ok
example store.invoice "a line shows the members' price of one unit" ... ok
example store.invoice "an unknown SKU is UnknownSku" ... ok
example store.money "two digits after the point" ... ok
example store.money "a leading zero is kept" ... ok
example store.money "a refund keeps its sign" ... ok
example store.pricing "members pay 10 percent less" ... ok
example store.pricing "the discount rounds down" ... ok

8 examples: 8 passed, 0 failed
```

An example sits in the module whose function it tests, so it can call the module's private functions too: `"the discount rounds down"` tests `discount`, which no other module can see.

```una include="day-to-day/src/store/invoice.una#L30-L42" title="day-to-day/src/store/invoice.una" caption="the invoice's examples"
example "a known SKU is found"
  given @catalog = listed([Product(sku: "LAMP-01", name: "Desk lamp", cents: 1990)])
  do product_of(OrderLine(sku: "LAMP-01", quantity: 2))
  expect result.name == "Desk lamp"

example "a line shows the members' price of one unit"
  do describe(OrderLine(sku: "LAMP-01", quantity: 2), product: Product(sku: "LAMP-01", name: "Desk lamp", cents: 1990))
  expect result == "2 x Desk lamp at 19.90 (members 17.91): 39.80"

example "an unknown SKU is UnknownSku"
  given @catalog = listed([])
  do product_of(OrderLine(sku: "CHAIR-09", quantity: 1))
  expect fails UnknownSku
```

The invoice's examples use the catalog's public handler, `listed`, imported like any other declaration. A fake shared this way stays the same for every module that tests against it. Each example names a case within its module, and two modules may use the same example name, since `una test` prints the module with each one.

`store.app` has no examples of its own. Everything it does is a call to a function that another module tests. An example could still run `main` with a fake console (`given @console = …`, [chapter 10, Testing](/learn/testing/#s10-7), mistake 1), but it would only show that something was printed. Keep an entry module this thin: wiring services to functions, and printing what they return. The less it decides, the less goes untested.

## 11.7 Common mistakes

Each mistake below is a small change to the day-to-day package, followed by what `una check .` reports.

:::mistake
**1. A module header that does not match its path (U1008).** Add `src/store/shipping.una`, and name the module after the file alone:

```una include="mistakes/1/src/store/shipping.una" title="mistakes/1/src/store/shipping.una"
module shipping

--- The shipping fee in cents: 4.90, and nothing from 50.00 on.
pub fee(subtotal: Int) -> Int = if subtotal >= 5000 then 0 else 490
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U1008] Error: module `shipping` is in `src/store/shipping.una`, which must hold module `store.shipping`
```

*Why:* a module's name is its path under `src/`, so that an import says where to find the file.

*Fix:* write `module store.shipping`.
:::

:::mistake
**2. Using a name you did not import (U1001).** Drop `member_price` from the invoice's import, and keep the call:

```diff include="day-to-day..mistakes/2:src/store/invoice.una" context="1" title="src/store/invoice.una"
--- a/src/store/invoice.una
+++ b/src/store/invoice.una
@@ -4,3 +4,3 @@
 import store.money (format)
-import store.pricing (line_cents, member_price)
+import store.pricing (line_cents)
 
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U1001] Error: cannot find name `member_price` in this module, its imports or the prelude
```

*Why:* a module sees its own declarations, its imports and the prelude. Being `pub` in another module is not enough.

*Fix:* add the name to the import of `store.pricing`.
:::

:::mistake
**3. An import that clashes with a declaration (U1002).** Declare a private `format` in the invoice, next to the imported one:

```diff include="day-to-day..mistakes/3:src/store/invoice.una" context="1" title="src/store/invoice.una"
--- a/src/store/invoice.una
+++ b/src/store/invoice.una
@@ -22,2 +22,5 @@
 
+--- A quantity as the invoice writes it.
+format(quantity: Int) -> Text = "{quantity} x"
+
 --- One line of the invoice, as text, with the members' price of one unit.
```

```text include="mistakes/3/expected/rendered.txt#L1"
[U1002] Error: `format` is already defined in this module
```

*Why:* an explicit import and a declaration of the module share one namespace, so one name cannot mean two things.

*Fix:* rename the new function, for example `quantity_text`.
:::

:::mistake
**4. An import cycle (U1003).** Add a helper for members' prices to `store.money`, which then imports `store.pricing`, which imports `store.money`:

```diff include="day-to-day..mistakes/4:src/store/money.una" context="1" title="src/store/money.una"
--- a/src/store/money.una
+++ b/src/store/money.una
@@ -1,2 +1,4 @@
 module store.money
+
+import store.pricing (member_price)
 
@@ -7,2 +9,5 @@
 pub format(cents: Int) -> Text = if cents < 0 then "-{digits(0 - cents)}" else digits(cents)
+
+--- What a member pays, as a person reads it.
+pub format_member(cents: Cents) -> Text = format(member_price(cents))
 
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U1003] Error: import cycle between modules `store.money` and `store.pricing`
```

*Why:* modules form a graph with no cycle, so each can be read, and checked, after the modules it uses.

*Fix:* put the helper where both of its parts are visible, such as `store.pricing` or `store.invoice`.
:::

:::mistake
**5. Imports out of order (U7001).** Put `store.money` before `store.catalog`:

```diff include="day-to-day..mistakes/5:src/store/invoice.una" context="1" title="src/store/invoice.una"
--- a/src/store/invoice.una
+++ b/src/store/invoice.una
@@ -2,4 +2,4 @@
 
+import store.money (format)
 import store.catalog (Catalog, Product, listed)
-import store.money (format)
 import store.pricing (line_cents, member_price)
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U7001] Error: line 3 is not in canonical form
```

*Why:* canonical form sorts imports by module path, and the names inside each import, so two people who add imports never produce two orders.

*Fix:* `una fmt .` sorts them.
:::

:::mistake
**6. A `0.3` table in an edition `0.2` package (U7002).** Lock the catalog lookup in the day-to-day manifest:

```diff include="day-to-day..mistakes/6:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -8 +8,4 @@
 grants = ["console"]
+
+[contracts]
+"store.invoice.product_of" = ["@catalog: Catalog[find]"]
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U7002] Error: unknown table [contracts] in una.toml
```

*Why:* `[contracts]` exists only in edition `0.3`. In edition `0.2`, it is a table una does not know.

*Fix:* set `edition = "0.3"` if you want the preview's rules, or remove the table.
:::

## 11.8 For agents

:::agents
A diagnostic about an import carries the place of the declaration as a related span, and its repair. For [section 11.2](#s11-2):

```json include="steps/03-private/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U1004","severity":"error","domain":"names","message":"function `digits` is private to module `store.money`","primary":{"file":"src/store/app.una","start":{"line":4,"col":21},"end":{"line":4,"col":27}},"related":[{"file":"src/store/money.una","start":{"line":10,"col":1},"end":{"line":10,"col":7},"message":"declared here without `pub`"}],"repairs":[{"rank":1,"escape_cost":0,"widens":{"kind":"visibility","cost":"every module may then call it: check that it belongs to the module's interface"},"description":"declare `digits` with `pub`","edit":{"file":"src/store/money.una","start":{"line":10,"col":1},"end":{"line":10,"col":1},"replacement":"pub "}}],"explain":"una explain U1004"}],"fixable":0}
```

The repair has `escape_cost` 0, but `widens` names the visibility it would open, so `una fix` skips it. It gives the reason `widens authority` for every repair that widens what code may reach, visibility included:

```text include="steps/03-private/expected/commands/fix.txt"
$ una fix --dry-run .
skipped src/store/money.una:10:1 U1004 declare `digits` with `pub`: widens authority
```

The compact rule: *one module per file, named by its path; take each declaration you use with a named import; make a declaration `pub` only on purpose, with its whole header written.*
:::

## 11.9 Exercises

Each exercise starts from `exercises/N/start`: a package of this chapter with the exercise's examples added, and a stub of what to write when there is one. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`.

::::exercise
**Exercise 1: a module for shipping.** The invoice gains a total with shipping, 4.90 below 50.00 and nothing from 50.00 on. It imports `shipping_fee` from `store.shipping`, a module that does not exist yet:

```una include="exercises/1/start/src/store/invoice.una#L31-L32" title="exercises/1/start/src/store/invoice.una"
--- What an order costs with shipping. Exercise 1: write `store.shipping`.
pub with_shipping(subtotal: Int) -> Int = subtotal + shipping_fee(subtotal)
```

```una include="exercises/1/start/src/store/invoice.una#L48-L54" title="exercises/1/start/src/store/invoice.una"
example "an order of 49.99 pays 4.90 of shipping"
  do with_shipping(4999)
  expect result == 5489

example "an order of 50.00 ships for free"
  do with_shipping(5000)
  expect result == 5000
```

:::hint
*Hint:* the module `store.shipping` lives in `src/store/shipping.una`, and its function must be `pub` for the invoice to import it.
:::

`una test .` stops at the check until the module exists:

```text include="exercises/1/start/expected/diagnostics.txt"
error U1001 at src/store/invoice.una:6:8: module `store.shipping` is not a module of this package; the standard modules that can be imported are `std.host` and `std.testing`
error U1001 at src/store/invoice.una:32:54: cannot find name `shipping_fee` in this module, its imports or the prelude
```

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Add the module:

```una include="exercises/1/answer/src/store/shipping.una" title="exercises/1/answer/src/store/shipping.una" verified="check, run, test"
module store.shipping

--- The shipping fee of an order, in cents: 4.90, and nothing from 50.00 on.
pub shipping_fee(subtotal: Int) -> Int = if subtotal >= 5000 then 0 else 490
```
:::
::::

::::exercise
**Exercise 2: show what a member saves.** The invoice wants a note with the discount on one unit, such as `members save 1.99`. The start package has `saving_note` with an empty text, and this example:

```una include="exercises/2/start/src/store/invoice.una#L47-L49" title="exercises/2/start/src/store/invoice.una"
example "a note says what a member saves on one unit"
  do saving_note(Product(sku: "LAMP-01", name: "Desk lamp", cents: 1990))
  expect result == "members save 1.99"
```

```text include="exercises/2/start/expected/commands/test.txt#L5-L7"
example store.invoice "a note says what a member saves on one unit" ... FAILED
  src/store/invoice.una:49: expect result == "members save 1.99"
  it is false, with `result` = `""`
```

:::hint
*Hint:* `store.pricing` already computes the discount, in a private function. Importing it gives the U1004 of [section 11.2](#s11-2). Decide that it belongs to the module's interface, and say so in the declaration.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Make `discount` public in `store.pricing`:

```diff include="day-to-day..exercises/2/answer:src/store/pricing.una" context="1" title="src/store/pricing.una"
--- a/src/store/pricing.una
+++ b/src/store/pricing.una
@@ -14,3 +14,3 @@
 --- The members' discount, rounded down to a whole cent.
-discount(cents: Cents) -> Int
+pub discount(cents: Cents) -> Int
   ensures result >= 0 and result <= cents
```

Then import it in the invoice, and use it:

```diff include="exercises/2/start..exercises/2/answer:src/store/invoice.una" context="1" title="src/store/invoice.una"
--- a/src/store/invoice.una
+++ b/src/store/invoice.una
@@ -4,3 +4,3 @@
 import store.money (format)
-import store.pricing (line_cents, member_price)
+import store.pricing (discount, line_cents, member_price)
 
@@ -29,4 +29,4 @@
 
---- What a member saves on one unit. Exercise 2: replace the empty text.
-pub saving_note(product: Product) -> Text = ""
+--- What a member saves on one unit.
+pub saving_note(product: Product) -> Text = "members save {format(discount(product.cents))}"
 
```
:::
::::

::::exercise
**Exercise 3: honor a lock.** This exercise starts from the sale package of [section 11.4](#s11-4), in edition `0.3`. It adds `end_sale`, which puts a product's old price back, and a lock for it in `una.toml`:

```toml include="exercises/3/start/una.toml" title="exercises/3/start/una.toml"
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

```una include="exercises/3/start/src/store/sale.una#L16-L34" title="exercises/3/start/src/store/sale.una"
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

```text include="exercises/3/start/expected/diagnostics.txt"
error U3023 at src/store/sale.una:18:27: the header of `end_sale` lets `@prices.set_price` run where `not dry_run` does not hold, which `una.toml` locks
  counterexample: dry_run = true
```

:::hint
*Hint:* copy the condition from the lock into the header. The verifier then asks for the guard that makes the header true:

```text include="exercises/3/header-only/expected/rendered.txt#L1,L12"
[U5001] Error: `@prices.set_price` may run where `not dry_run` is not proven
    │ Help 1: repair 1: guard the operation with `if not dry_run`
```
:::

Check your answer with `una test .`. Both examples must pass: a dry run sets no price, and a real one does.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Write the locked condition in the header, and guard the operation to match it:

```diff include="exercises/3/start..exercises/3/answer:src/store/sale.una" context="1" title="src/store/sale.una"
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
:::
::::

## 11.10 Recap

:::recap
- One file is one module, and its header names its path under `src/`: `src/store/money.una` is `module store.money`.
- Declarations are private by default. Mark `pub` only what other modules need, with a doc comment and its whole header written.
- Import each declaration you use by name. A sum kind brings its variants, and a record its constructor and fields.
- Keep the imports a graph with no cycle, and let `una fmt` keep them sorted.
- `una.toml` has a fixed set of tables, and an unknown one is U7002. In una 0.3.14, a package imports only its own modules, `std.host` and `std.testing`.
- `verification.lock` pins the solver, so a check gives the same result on every machine.
- In edition `0.3`, lock the `uses` of a public function in `[contracts]`, and give a supplier's module a ceiling in `[boundaries]`.
:::

## 11.11 Reference

:::reference
- Construct and configuration pages: [modules and imports](/docs/language/modules/), [`kind`](/docs/language/types/kind/), [`where`](/docs/language/types/where/), [`capability` and `op`](/docs/language/capabilities/capability/), [`handler`](/docs/language/capabilities/handler/), [`uses`](/docs/language/capabilities/uses/), [`example`](/docs/language/examples/example/), [canonical form](/docs/language/canonical-form/), [`una.toml`](/docs/configure/), [`[package] name`](/docs/configure/package/name/), [`[package] version`](/docs/configure/package/version/), [`[package] edition`](/docs/configure/package/edition/), [`[run] entry`](/docs/configure/run/entry/), [`[run] grants`](/docs/configure/run/grants/), [`[labels] categories`](/docs/configure/labels/categories/), [`[trusted] modules`](/docs/configure/trusted/modules/), [`[escape_budget] checked_per_module`](/docs/configure/escape-budget/checked-per-module/), [`[boundaries]`](/docs/configure/boundaries/), [`verification.lock`](/docs/configure/verification-lock/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/), [U1003](/docs/errors/U1003/), [U1004](/docs/errors/U1004/), [U1008](/docs/errors/U1008/), [U3020](/docs/errors/U3020/), [U3021](/docs/errors/U3021/), [U3023](/docs/errors/U3023/), [U5001](/docs/errors/U5001/), [U5003](/docs/errors/U5003/), [U7001](/docs/errors/U7001/), [U7002](/docs/errors/U7002/), [U7004](/docs/errors/U7004/)
- Specification: [diagnostics, the command line and project files](/docs/spec/13-diagnostics-and-abi/), [grammar](/docs/spec/02-grammar/), [static semantics](/docs/spec/10-static-semantics/), [canonical form](/docs/spec/15-canonical-form/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [verification](/docs/spec/12-verification/)
:::
