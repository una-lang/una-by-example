---
learn: "11"
title: Packages and modules
editions: ["0.2", "0.3"]
codes: [U1001, U1002, U1003, U1004, U1008, U1009, U3020, U3021, U3023, U5001, U7001, U7002]
time: 55
builds: A store's invoice, split into modules for money, the catalog, prices and the invoice itself
prerequisites: ["6", "7", "8", "10"]
template: 2
nav: ["Packages and modules", "pub and import", "The manifest and the lock", "Locking a contract", "A ceiling for a module", "Day-to-day: the store's invoice", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 11 Packages and modules

A program of one file is easy to read until it grows. Then the price rules, the catalog and the invoice text sit side by side, any function can call any other, and a reviewer cannot tell which functions other parts of the program are meant to use. In Una a package is split into modules, one file each. A module shares only what it marks `pub`, and every other module names what it takes with `import`. This chapter splits a store's invoice into modules, walks through `una.toml`, and, in edition `0.3`, locks what public functions may do and limits what code from a supplier may receive.

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
- lock the `uses` of a public function in `una.toml`, and give a supplier's module a ceiling, in edition `0.3`;
- test a package of several modules with one command.
:::

## Why it works this way

In many languages, a file can see a great deal it never asked for: every public name of every file in the project, globals, and whatever an import brings in with it. Splitting a program into files does not, by itself, say which parts are the interface of a file and which are its details. A dependency added by one line in a manifest can bring in code that reads files or opens connections, and nothing in the caller's code shows it. In una 0.3.15 a package has no dependencies on other packages ([section 11.3](#s11-3)).

Una keeps the structure small and visible:

:::steps
1. **One file is one module, and its path is its name.** `src/store/money.una` holds the module `store.money`, and nothing else.
2. **Private by default.** A declaration is visible outside its module only when it says `pub`. A `pub` function's header is its contract with the rest of the package, so it declares its `uses` and `fails`, as [chapter 6, Failure](/learn/failure/), and [chapter 8, Capabilities](/learn/capabilities/), showed.
3. **Every import is named.** `import store.money (format)` takes one declaration, by name. There is no import of everything.
4. **The manifest is checked.** `una.toml` holds a fixed set of tables, and a table or key that una does not know is an error, not a setting that is silently ignored.
:::

> [!KEY]
> A module's `pub` declarations are its interface, and its imports say exactly what it uses of other modules. Both are in the source, where a reviewer reads them.

## 11.1 Packages and modules

### What a package and a module are

Think of a store's binder of procedures. The binder holds everything the staff need, and tabbed sections divide it: one for the till, one for deliveries, one for returns. A clerk looking for the refund rules opens one section, not the whole binder.

A **package** is the binder: one program, kept in one directory (a folder) with everything una needs to check and run it. A **module** is one section: a single file of Una code under the package's `src/` directory. A program grows by adding modules, and each module holds the code about one subject.

A few words name the parts, and the rest of the chapter uses them:

- A **path** is where a file sits, written as the directories that lead to it: `src/store/money.una` is the file `money.una` in the directory `store`, inside `src`.
- A **module path** is a module's name, built from its file's path: drop `src/` and `.una`, and write `.` for each `/`. So `src/store/money.una` holds the module `store.money`. Each part between dots is a **segment**.
- A **declaration** is a top-level item of a module: a function, a kind, a capability, a handler and the like, each starting at the left edge of the file.
- The **entry** is the module that `una run` starts, the one with `pub main`.

### Each step is a package

Each step of this chapter is a package, as in [chapter 1, Hello, Una](/learn/hello/#s1-1): a directory with `una.toml`, `verification.lock` and the modules under `src/`. `verification.lock` is the same in every example: copy it from chapter 1, or take the step's package, whole, from the chapter's download, `11-packages.tar.gz`. Then, in the package's directory:

```sh
una check .
una run .
```

### Why a program is split into modules

Every module has its own set of names, so one module cannot declare two things with the same name. Here is a store's program kept in one module. It formats an amount of money, and it also formats a tax rate, and both functions are called `format`:

```una include="steps/01-one-file/src/store.una" title="steps/01-one-file/src/store.una"
module store

--- An amount in cents as a person reads it: 1990 is "19.90".
format(cents: Int) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"

--- A tax rate as a person reads it: 8 is "8%".
format(percent: Int) -> Text = "{percent}%"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("a lamp costs {format(1990)}, with tax at {format(8)}")
```

`una check .` reports:

```text include="steps/01-one-file/expected/rendered.txt"
[U1002] Error: `format` is defined twice in this module, both times as a function
    ╭─[ src/store.una:10:1 ]
    │
  4 │ format(cents: Int) -> Text
    │ ───┬──
    │    ╰──── first defined here
    │
 10 │ format(percent: Int) -> Text = "{percent}%"
    │ ───┬──
    │    ╰──── `format` is defined twice in this module, both times as a function
    │
    │ Note: run `una explain U1002` for an explanation
────╯
```

The first line names the problem: `format` is defined twice. The two marks point at both declarations, so you see which one came first. Inside one module, a name means one thing, and the checker refuses to guess which `format` a call means.

In one file, every new function has to find a name that no other function of the whole program uses, and every function can call every other. As the file grows, so do both problems: names get longer to stay apart, and a change to any helper can affect any line of the program. Modules solve both. Each module has its own names, so the money module and the tax module can each have a `format` of their own. And each module decides which of its declarations other modules may use, which [section 11.2](#s11-2) covers.

### How to write a module

The next step splits a store's program into two modules. `store.money` formats an amount, and `store.app` prints with it:

```una include="steps/02-modules/src/store/money.una" title="steps/02-modules/src/store/money.una" verified="check"
module store.money

--- An amount in cents as a person reads it: 1990 is "19.90".
pub format(cents: Int) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"
```

```una include="steps/02-modules/src/store/app.una" title="steps/02-modules/src/store/app.una" verified="check, run"
module store.app

import store.money (format)

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("a lamp costs {format(1990)}, a desk {format(24905)}")
```

`una run .` prints:

```text include="steps/02-modules/expected/output.txt"
a lamp costs 19.90, a desk 249.05
```

A module file has three parts, always in this order:

:::steps
1. **The `module` line.** The first line of the file names the module: `module store.money`. It must be the module path of the file's own path.
2. **The imports.** Zero or more `import` lines, each naming a module of the package and the declarations it takes: `import store.money (format)`. [Section 11.2](#s11-2) covers imports.
3. **The declarations.** The functions, kinds and other declarations of the module, in any order, separated by blank lines. All of them see each other: a function can call one declared further down.
:::

Two smaller things in this step. `pub` before `format` makes it usable by other modules, and [section 11.2](#s11-2) explains it. `cents mod 100` is the remainder of dividing `cents` by 100, as `/` is the quotient: 1990 divided by 100 is 19, remainder 90 ([chapter 2, Values](/learn/values/#s2-1), covers both).

#### The entry module in `una.toml`

`una check .` checks every module, but `una run .` must know where to start. The manifest, `una.toml`, says so: `[run] entry` is a module path, here `store.app`, and that module has the `pub main`.

```toml include="steps/02-modules/una.toml" title="steps/02-modules/una.toml"
[package]
name = "store"
version = "0.1.0"
edition = "0.2"

[run]
entry = "store.app"
grants = ["console"]
```

[Section 11.3](#s11-3) explains every line of this file.

### Modules at every depth

A module path has as many segments as its file has directories under `src/`, plus one for the file. This step has three modules at three depths:

| File | Module |
| --- | --- |
| `src/app.una` | `app` |
| `src/store/money.una` | `store.money` |
| `src/store/tax/rates.una` | `store.tax.rates` |

The tax module knows the store's sales tax, and has a `format` of its own, for percentages:

```una include="steps/03-paths/src/store/tax/rates.una" title="steps/03-paths/src/store/tax/rates.una" verified="check"
module store.tax.rates

--- The store's sales tax, in percent.
pub rate() -> Int = 8

--- The tax on an amount, in cents, rounded down.
pub tax_cents(cents: Int) -> Int = cents * rate() / 100

--- The rate as a person reads it: 8 is "8%".
pub rate_text() -> Text = format(rate())

--- A percentage as a person reads it.
format(percent: Int) -> Text = "{percent}%"
```

The entry is `app`, a module of one segment, directly under `src/`:

```una include="steps/03-paths/src/app.una" title="steps/03-paths/src/app.una" verified="check, run"
module app

import store.money (format)
import store.tax.rates (rate_text, tax_cents)

pub main() -> Unit
  uses @console: Console[print]
=
  let cents = 1990
  @console.print("a lamp costs {format(cents)}, and tax at {rate_text()} adds {format(tax_cents(cents))}")
```

```toml include="steps/03-paths/una.toml" title="steps/03-paths/una.toml"
[package]
name = "store"
version = "0.1.0"
edition = "0.2"

[run]
entry = "app"
grants = ["console"]
```

`una run .` prints:

```text include="steps/03-paths/expected/output.txt"
a lamp costs 19.90, and tax at 8% adds 1.59
```

Two functions called `format` now live in one package without a clash: `store.money` has one, and `store.tax.rates` has another. `app` imports only the money one, and calls the tax module's `rate_text`, which uses its own `format` inside.

### How una finds and checks the modules

#### Every file under `src/` is a module

There is no list of modules to keep up to date. `una check .` reads every `.una` file under `src/`, checks all of them together, and reports each diagnostic with its file. A new file is part of the package as soon as it exists, and a deleted file is gone from it. Hidden entries, whose names start with a dot, are skipped.

A directory under `src/` only groups modules: it is not a module itself, and it needs no file of its own. `src/store/` holds `store.money`, but there is no module `store`.

#### The `module` line must match the path

A file whose `module` line does not match its path is U1008, at that line, with a repair that writes the right path. [A module header that does not match its path](#a-module-header-that-does-not-match-its-path-u1008) shows one.

#### The rules for a module path

Each segment is a lower-case name, as a function's name is: a lower-case letter, then lower-case letters, digits and underscores, such as `store`, `tax_rates` or `v2`. It may not contain `__` or end with `_` (U1005), and it may not be a keyword.

Paths that start with `std` or `prelude` belong to the standard library. Add a file `src/std/money.una` to the package of the last step, and `una check .` reports:

```text include="steps/04-reserved/expected/rendered.txt"
[U1009] Error: module `std.money` starts with `std`, a segment that only the standard library may use
   ╭─[ src/std/money.una:1:1 ]
   │
 1 │ module std.money
   │ ────────┬───────
   │         ╰───────── module `std.money` starts with `std`, a segment that only the standard library may use
   │
   │ Note: run `una explain U1009` for an explanation
───╯
```

The standard library has its own modules there, such as `std.host`, so a package may not add any. Choose another first segment, such as `store`.

#### Where checking and running start

`una check .` and `una test .` take every module. `una run .` starts at `main` in the entry module, and runs only what `main` calls. A module that nothing calls is still checked, and its examples still run under `una test .`.

### Grouping and moving modules

Group modules by what they are about, not by what kind of declaration they hold: `store.money` keeps the type of an amount, its formatting and its tests together. A reader who wants to know how amounts are printed then opens one file.

A module path follows the file system, so moving a file renames its module. The checker then reports the header that no longer matches, and every import of the old name, so nothing is left pointing at a module that is gone.

:::decide
**Which to use:**

| You have… | Use |
| --- | --- |
| A small program, a few functions about one subject | One module, such as `src/app.una` |
| Code about two subjects, such as money and the catalog | One module per subject |
| Several modules about one area | A directory for the area: `src/store/money.una`, `src/store/catalog.una` |
| A helper that two modules need | Its own module, or the module that owns its subject, imported by both |
:::

### Check yourself: module paths

The file `src/store/tax/rates.una` of [Modules at every depth](#modules-at-every-depth) now starts with a shorter line:

```diff include="steps/03-paths..steps/05-tax-header:src/store/tax/rates.una" context="0" title="src/store/tax/rates.una"
--- a/src/store/tax/rates.una
+++ b/src/store/tax/rates.una
@@ -1 +1 @@
-module store.tax.rates
+module tax.rates
```

The rest of the package is unchanged, and `app` still imports `store.tax.rates`. What does `una check .` report? Count the diagnostics before you open the answer.

:::answer Show the answer
Four diagnostics, three of them in `app`:

```text include="steps/05-tax-header/expected/diagnostics.txt"
error U1001 at src/app.una:4:8: module `store.tax.rates` is not a module of this package; the standard modules that can be imported are `std.host` and `std.testing`
error U1001 at src/app.una:10:61: cannot find name `rate_text` in this module, its imports or the prelude
error U1001 at src/app.una:10:87: cannot find name `tax_cents` in this module, its imports or the prelude
error U1008 at src/store/tax/rates.una:1:8: module `tax.rates` is in `src/store/tax/rates.una`, which must hold module `store.tax.rates`
```

The file still sits at `src/store/tax/rates.una`, so its module must be `store.tax.rates` (U1008, with a repair that writes it). And since no file now holds `store.tax.rates`, the import in `app` names a module that does not exist (U1001), and the two names it imported cannot be found. Fix the `module` line, and all four go away: when several diagnostics appear at once, look first for the one the others follow from.
:::

## 11.2 `pub` and `import`

### What `pub` and `import` do

A store has a counter and a stockroom. Customers deal with what is on the counter; the stockroom is where the staff keep what they need to serve them. A module works the same way. The declarations it marks `pub` are its counter: other modules may use them. Everything else is its stockroom: it stays inside the module.

- **`pub`**, short for public, is a word written before a declaration. It makes the declaration visible to other modules of the package.
- A declaration without `pub` is **private**: only its own module can use it.
- A module's **interface** is the set of its `pub` declarations: what the rest of the package may rely on.
- An **import** is a line at the top of a module that takes declarations of another module by name, so the module can use them as if they were its own. `import store.money (format)` takes `format` from `store.money`.

A module sees exactly three sources of names: its own declarations, the names it imports, and the **prelude**, the functions and types that every module sees without importing, such as `List`, `Option` and `Console`.

### Why a module keeps its helpers private

A helper is often written for one job, and assumes things that its module guarantees. Here is the money code again, in one module. `format` handles a negative amount, a refund, by putting the minus sign in front and passing the amount without its sign to `digits`. `digits` was written for amounts of 0 or more. Nothing stops `main` from calling it directly:

```una include="steps/06-helper/src/store.una" title="steps/06-helper/src/store.una" verified="check, run"
module store

--- An amount in cents as a person reads it: 1990 is "19.90", and -150 is "-1.50".
format(cents: Int) -> Text = if cents < 0 then "-{digits(0 - cents)}" else digits(cents)

--- The digits of an amount of 0 or more, with two after the point.
digits(cents: Int) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("a refund of 150 cents, by format: {format(-150)}")
  @console.print("the same refund, by digits: {digits(-150)}")
```

`una run .` prints:

```text include="steps/06-helper/expected/output.txt"
a refund of 150 cents, by format: -1.50
the same refund, by digits: -2.50
```

The second line is wrong: a refund of 150 cents is 1.50, not 2.50. `digits` divides with Una's division, which rounds down, toward the smaller number: −150 / 100 is −2, and the remainder is 50 ([chapter 2, Values](/learn/values/#s2-1), shows why). That is right for the job `digits` was written for, and wrong for any other. The checker cannot know which job a function was meant for.

When `digits` is private to `store.money`, no other module can call it, so it can only be reached through `format`, which keeps its assumption. The module can also change `digits`, rename it or delete it, and no code outside it breaks. [Private stays private](#private-stays-private) shows what happens when another module tries.

### How to write `pub`

Write `pub` at the very start of the declaration, before its name:

```una include="steps/07-imports/src/store/money.una#format" title="steps/07-imports/src/store/money.una"
--- An amount in cents as a person reads it: 1990 is "19.90", and -150 is "-1.50".
pub format(cents: Int) -> Text = if cents < 0 then "-{digits(0 - cents)}" else digits(cents)
```

`pub` goes on a function, a kind, a capability, a handler, a predicate or a policy. An `example` or a `requirement` is never `pub`: an example belongs to its module ([section 11.7](#s11-7)).

A `pub` function promises its callers a header they can rely on, so it writes every clause: its `uses` and its `fails` ([chapter 3, Functions](/learn/functions/#s3-4), showed that a private function may leave them to inference). Give every `pub` declaration a doc comment (`---`), since other modules read it to learn what the declaration does.

### How to write an import

An import line has four parts:

:::steps
```una include="steps/07-imports/src/store/app.una#L3-L4" title="steps/07-imports/src/store/app.una"
import store.catalog (Catalog, Product, listed)
import store.money (format)
```

1. **`import`.** The keyword that starts the line.
2. **`store.catalog`.** The module path of a module of the same package, or of a standard module.
3. **`(Catalog, Product, listed)`.** In parentheses, each declaration the line takes, by its name, separated by commas. At least one name, and each name once.
4. **One line per module.** A module that takes names from two modules has two import lines. They come right after the `module` line, before any declaration, sorted by module path, with the names inside each sorted too: `una fmt .` keeps them in that order.
:::

There is no form that imports every name of a module, and no form that imports a module without naming what it takes. A reader of the import lines knows exactly which names come from where.

#### Functions and handlers

A function or a handler is then used by its plain name, `format(1990)` or `listed(products)`, as if the importing module had declared it.

#### Record kinds, with their constructor and fields

Importing a record kind brings its type, its constructor and its fields. This step's catalog module shares a record, `Product`, a capability, and a handler, all `pub`:

:::steps
```una include="steps/07-imports/src/store/catalog.una" title="steps/07-imports/src/store/catalog.una" verified="check"
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

1. **`import store.money (Cents)`.** A module imports what it uses, even another module's kinds. `Cents`, an `Int` that is never below zero, is a refined kind of [chapter 7, Contracts and the verifier](/learn/contracts/#s7-3). `Product.cents` is a `Cents`, so a negative price cannot be built anywhere in the package.
2. **`pub kind Product`.** The record, its constructor and its fields are part of the interface. A module that imports `Product` can write `Product(sku: …, name: …, cents: …)` and read `product.name`.
3. **`pub capability Catalog`.** Code in other modules can now declare `uses @catalog: Catalog[find]`, and call the operation `find`.
4. **`pub handler listed(...)`.** A handler is shared like a function, so every module and every example can run against the same in-memory catalog ([chapter 8, Capabilities](/learn/capabilities/#s8-3), covers handlers).
:::

#### Sum kinds, with their variants

Importing a sum kind brings its variants with it, so the importing module can build them. This step has a module that tells whether a shelf can sell a SKU:

```una include="steps/08-import-forms/src/store/stock.una" title="steps/08-import-forms/src/store/stock.una" verified="check"
module store.stock

--- Whether a shelf can sell a SKU now.
pub kind Availability = InStock(units: Int) | SoldOut

--- The availability of a shelf that holds `units` units.
pub availability(units: Int) -> Availability = if units > 0 then InStock(units: units) else SoldOut
```

The app imports `Availability`, and with it `InStock` and `SoldOut`:

```una include="steps/08-import-forms/src/store/app.una" title="steps/08-import-forms/src/store/app.una" verified="check, run"
module store.app

import std.host (Console)
import store.stock (Availability, availability)

--- What a shelf card says.
card(sku: Text, stock: Availability) -> Text
=
  when stock
    is InStock(units) -> "{sku}: {units} in stock"
    is SoldOut -> "{sku}: sold out"

--- Prints the card of each shelf.
report(cards: List[Text]) -> Unit
  uses @console: Console[print]
=
  for line in cards
    @console.print(line)

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = card("LAMP-01", stock: availability(4))
  let desk = card("DESK-02", stock: availability(0))
  let chair = card("CHAIR-09", stock: SoldOut)
  report([lamp, desk, chair])
```

```text include="steps/08-import-forms/expected/output.txt"
LAMP-01: 4 in stock
DESK-02: sold out
CHAIR-09: sold out
```

`card` writes the kind in a parameter's type, and `main` builds a variant, `SoldOut`, so both need the import. A `when` needs no import to match a variant, even in a module that did not import the kind: its arms take the variants of the value's type, whatever module declared it.

#### The host's capabilities: `std.host`

The same step also writes `import std.host (Console)`. `std.host` is one of the two standard modules a package can import. It holds the host's capabilities, such as `Console` and `Clock` ([chapter 8](/learn/capabilities/#s8-2)), which the prelude already puts in every module. So the import changes nothing but makes the source explicit, and you may leave it out. The other standard module, `std.testing`, holds helpers for examples.

### A private helper next to a public function

Back to money, now split into modules. `store.money` keeps the helper, `digits`, next to its public `format`:

```una include="steps/07-imports/src/store/money.una" title="steps/07-imports/src/store/money.una" verified="check"
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

The app takes what it needs from the two modules, one name at a time:

```una include="steps/07-imports/src/store/app.una" title="steps/07-imports/src/store/app.una" verified="check, run"
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

```text include="steps/07-imports/expected/output.txt"
Ok("Desk lamp: 19.90")
Err(NotListed("CHAIR-09"))
```

`PriceError` and `price_tag` have no `pub`, so they belong to `store.app` alone. A private function may leave its `uses` and `fails` to inference, but `price_tag` writes them, so its header can be read without its body. `attempt` keeps each lookup's outcome as a `Result` ([chapter 6, Failure](/learn/failure/#s6-3)), and the two lines print them: the lamp's text, and the failure for a SKU the catalog does not list.

### How names are found

#### Where a name comes from

When a module uses a name, una looks for it in this order, and the first place that has it wins:

1. the local names: parameters, `let` bindings and the like;
2. the module's own declarations;
3. the names it imports, and the variants of the sum kinds it imports;
4. the prelude.

A name found nowhere is U1001, "cannot find name … in this module, its imports or the prelude". [Using a name you did not import](#using-a-name-you-did-not-import-u1001) shows it. An import of a module that the package does not have, or of a name that the module does not declare, is U1001 too.

#### Private stays private

Try to import `digits` into the app:

```diff include="steps/07-imports..steps/09-private:src/store/app.una" context="0" title="src/store/app.una"
--- a/src/store/app.una
+++ b/src/store/app.una
@@ -4 +4 @@
-import store.money (format)
+import store.money (digits, format)
```

`una check .` reports:

```text include="steps/09-private/expected/rendered.txt"
[U1004] Error: function `digits` is private to module `store.money`
    ╭─[ src/store/app.una:4:21 ]
    │
  4 │ import store.money (digits, format)
    │                     ───┬──
    │                        ╰──── function `digits` is private to module `store.money`
    │
    ├─[ src/store/money.una:10:1 ]
    │
 10 │ digits(cents: Int) -> Text
    │ ───┬──
    │    ╰──── declared here without `pub`
    │
    │ Help: repair 1 (widens visibility: every module may then call it: check that it belongs to the module's interface): declare `digits` with `pub`; edit src/store/money.una:10:1..10:1 to "pub "
    │
    │ Note: run `una explain U1004` for an explanation
────╯
```

Read it from the top. The first line names the problem and the module that owns the function. The first mark points at the name in the import, and the second at the declaration in `store.money`, "declared here without `pub`". The help line offers the repair, adding `pub`, but marks it as one that **widens visibility**: every module may then call it. `una fix .` does not apply such a repair by itself. Making a helper public is a decision about the module's interface, and you take it by editing the declaration, with a doc comment for its new callers.

#### One name, one meaning

An import and a declaration of the same module share one set of names, so a module cannot declare a name it also imports, and cannot import one name from two modules. Both are U1002, as two declarations of one name are ([An import that clashes with a declaration](#an-import-that-clashes-with-a-declaration-u1002)). A declaration or an import may reuse a name of the prelude: the module's own wins.

#### No cycles

If `store.money` imports `store.pricing`, then `store.pricing` cannot import `store.money`, directly or through other modules. A loop of imports is an **import cycle**, U1003 ([An import cycle](#an-import-cycle-u1003)). Without cycles, every module can be read, and checked, after the modules it uses.

### Choosing what to share and what to import

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A function, kind or handler that other modules need | `pub`, with a doc comment, and every clause of its header written |
| A helper that only this module uses | no `pub`: it stays private, and may infer its `uses` and `fails` |
| A declaration of another module | `import module.path (name, …)`, one name per declaration |
| A host capability's name, written explicitly | `import std.host (Console)`, optional, since the prelude has it |
| The same helper in two modules | One `pub` declaration in the module it belongs to, imported by the other |
:::

Share as little as the other modules need. Every `pub` declaration is a promise: changing its header changes every module that uses it.

### Check yourself: names and imports

The app of [A private helper next to a public function](#a-private-helper-next-to-a-public-function) changes one line: `price_tag` now calls `digits` directly, without importing it.

```diff include="steps/07-imports..steps/10-unimported:src/store/app.una" context="0" title="src/store/app.una"
--- a/src/store/app.una
+++ b/src/store/app.una
@@ -16 +16 @@
-  "{product.name}: {format(product.cents)}"
+  "{product.name}: {digits(product.cents)}"
```

Does it check? If not, which code does `una check .` report: U1004, since `digits` is private, or another one?

:::answer Show the answer
It does not check, and the code is U1001, not U1004:

```text include="steps/10-unimported/expected/rendered.txt#L1"
[U1001] Error: cannot find name `digits` in this module, its imports or the prelude
```

The app never imported `digits`, so the name is in none of its three sources: its declarations, its imports and the prelude. U1004 is reported only when an import names a private declaration, as in [Private stays private](#private-stays-private). Either way, the fix is the same: call `format`, which is public and handles every amount.
:::

## 11.3 The manifest and the lock

### What a manifest is

A **manifest** is a file that describes a package to the tools: its name, its version, which edition of the language it is written in, and how to run it. In Una it is `una.toml`, at the root of the package. Every command reads it before it reads any module.

`una.toml` is written in **TOML**, a common format for settings files. You need four of its rules:

- A **table** is a group of settings, opened by its name in brackets on a line of its own: `[package]`. It runs until the next table.
- A **key** is a setting's name, followed by `=` and its **value**: `edition = "0.2"`.
- A value is a text in double quotes (`"store"`), a whole number (`0`), or an **array**, a list of values in brackets separated by commas (`["console"]`).
- A line that starts with `#` is a comment, for people only.

### Why the manifest is checked

A settings file that accepts anything turns a typing mistake into a setting that silently does nothing. Here a manifest means to allow each module one use of `checked` ([chapter 6](/learn/failure/#s6-4)), and misspells the key:

```diff include="steps/11-manifest..steps/12-misspelt:una.toml" context="0" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -18 +18 @@
-checked_per_module = 0
+checked_per_modules = 1
```

`una check .` reports:

```text include="steps/12-misspelt/expected/rendered.txt"
[U7002] Error: unknown key `checked_per_modules` in [escape_budget]
    ╭─[ una.toml:18:1 ]
    │
 18 │ checked_per_modules = 1
    │ ─────────┬─────────
    │          ╰─────────── unknown key `checked_per_modules` in [escape_budget]
    │
    │ Note: run `una explain U7002` for an explanation
────╯
```

U7002 is the code of a manifest una cannot accept, and it points at the line and the key. In a tool that ignored unknown keys, the budget would silently stay at 0, and the mistake would show up later, as an error at the first `checked` of some module, far from its cause. Here it shows up at the line that has it.

### How to write `una.toml`

`una.toml` holds up to five tables in edition `0.2`, and two more in edition `0.3` ([section 11.4](#s11-4) and [section 11.5](#s11-5)). No other table or key is allowed.

#### `[package]`: what the package is

| Key | Value |
| --- | --- |
| `name` | The package's name, a text, such as `"store"`. |
| `version` | The package's own version, a text, such as `"0.2.0"`. una checks only that it is a text that is not empty. |
| `edition` | The edition of Una its modules are written in: `"0.1"`, `"0.2"` or `"0.3"` ([chapter 14, Editions](/learn/editions/)). Every example of this chapter but those of sections 11.4 and 11.5 uses `"0.2"`. |

`[package]` is required, with all three keys.

#### `[run]`: what `una run` starts and grants

| Key | Value |
| --- | --- |
| `entry` | The module path of the module whose `pub main` `una run` starts. |
| `grants` | An array of the host capabilities the run is given, such as `["console"]`, besides those of a `--grant` flag ([chapter 8, Capabilities](/learn/capabilities/#s8-2)). |

#### `[labels]`, `[trusted]` and `[escape_budget]`

| Table and key | Value |
| --- | --- |
| `[labels]` `categories` | The categories that labels may name, such as `["PII"]` ([chapter 9, Information flow](/learn/information-flow/)). |
| `[trusted]` `modules` | The modules that may declare policies, each also marked `trusted module` in its header ([chapter 9](/learn/information-flow/)). |
| `[escape_budget]` `checked_per_module` | How many uses of `checked` each module may have, 0 by default ([chapter 6, Failure](/learn/failure/#s6-4)). |

These three are optional. Without them, a package has no label categories, no trusted modules and a budget of 0.

### A manifest, table by table

Here is a manifest that uses four of the tables, with a comment on each:

```toml include="steps/11-manifest/una.toml" title="steps/11-manifest/una.toml"
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

The package still runs as before, with the same modules. Only `una.toml` changed.

### No dependencies on other packages yet

una 0.3.15 has no way to depend on another package: `una.toml` has no dependency table, and a package imports only its own modules and two standard modules, `std.host` and `std.testing`. Importing anything else says so:

```text include="steps/13-no-dependencies/expected/rendered.txt#L1"
[U1001] Error: module `vendor.tax` is not a module of this package; the standard modules that can be imported are `std.host` and `std.testing`
```

So everything a package runs is in its own `src/`, the prelude, or the host capabilities that `una run` grants, in `[run] grants` or by a `--grant` flag. Until a release adds dependencies, code from elsewhere, such as a supplier's library, is copied into `src/` as modules of the package, where the checker sees all of it. Code copied in this way is called **vendored** code. Edition `0.3` can then give such a module a ceiling, as [section 11.5](#s11-5) shows.

### `verification.lock`

`verification.lock` is the other file at the root of every package. It pins the verifier, the part of una that proves contracts ([chapter 7](/learn/contracts/#s7-1)), so that every machine gets the same answers. It is a TOML file with six keys, and no others:

| Key | What it fixes |
| --- | --- |
| `encoding_version` | How una writes its questions for the solver: `"una-smt-1"` |
| `solver` and `solver_version` | The solver and its exact version: `"z3"`, `"5.1.0"` |
| `logic` | The kind of arithmetic the questions use: `"QF_UFLIA"` |
| `step_budget` | How much work the solver may do on one question before it answers "unknown" |
| `random_seed` | The solver's starting point, so its search runs the same way every time |

With the same sources, `una.toml` and lock, `una check` gives the same diagnostics and the same proofs on every machine. A missing or invalid lock is U7004, and a solver of another version is U5003. You rarely edit it: copy it from an existing package, and change it only to adopt a new solver, in a change of its own.

### How the manifest is checked

- A table or a key that is not in the lists of this section is U7002, at its line.
- A value of the wrong type, such as a number where a text goes, a missing required key, and a file that is not valid TOML are U7002 too.
- A manifest error does not stop the check. The tables and keys una could read still apply, and only the wrong ones are reported. When the file is not valid TOML at all, the modules are checked with the default settings instead: no grants, no label categories, a budget of 0, and edition `0.1`. So a manifest that cannot be read can bring other diagnostics with it, which go away once it is fixed.
- `una run .` also checks that `main`'s `uses` are granted: a capability that `main` uses but neither `[run] grants` nor a `--grant` flag grants stops the run before it starts (U3012, [chapter 8](/learn/capabilities/#s8-2)).

:::decide
**Which to use:**

| The setting… | Belongs in |
| --- | --- |
| Is about the whole package: its name, edition, entry or grants | `una.toml` |
| Is about how the verifier answers | `verification.lock`, copied, not edited |
| Is about one function: what it may do or how it fails | The function's header, in the module |
| Must be reviewed apart from the code, in edition `0.3` | `[contracts]` or `[boundaries]` ([section 11.4](#s11-4), [section 11.5](#s11-5)) |
:::

### Check yourself: a manifest

This manifest writes the version as a number:

```diff include="steps/11-manifest..steps/14-number:una.toml" context="0" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -4 +4 @@
-version = "0.2.0"
+version = 2
```

Does the package check? If not, where does `una check .` point?

:::answer Show the answer
It does not check:

```text include="steps/14-number/expected/rendered.txt"
[U7002] Error: `version` must be a string, not an integer
   ╭─[ una.toml:4:11 ]
   │
 4 │ version = 2
   │           ┬
   │           ╰── `version` must be a string, not an integer
   │
   │ Note: run `una explain U7002` for an explanation
───╯
```

In TOML, a value without quotes is a number, and `version` must be a text: the mark points at the value. Write it in quotes, `version = "2.0.0"`. The file is valid TOML, but not a valid manifest: una checks the type of each value too, not only the names of the keys.
:::

## 11.4 Locking a contract: `[contracts]`

### What a locked contract is

When a store signs an agreement with a courier, each side keeps a copy. If someone later edits the agreement on one side, the copies disagree, and the change is noticed. A **locked contract** is such a copy for one function. The function's header says what it may do; `una.toml` keeps a copy of that, under `[contracts]`; and the checker fails when the header allows more than the copy.

> [!WARNING]
> `[contracts]` and `[boundaries]` ([section 11.5](#s11-5)) exist only in edition `0.3`, a preview ([chapter 14, Editions](/learn/editions/#s14-3)). In a package of edition `0.2`, each is an unknown table, U7002. Since `0.3` is a preview, a later release may add obligations or errors to an edition `0.3` package.

A function's header can say not only which operations it may perform, but when. `uses @prices: PriceList[set_price where not dry_run]` says that `set_price` runs only when `dry_run` is false ([chapter 8, Capabilities](/learn/capabilities/#s8-5), shows these conditions). The verifier proves that the body keeps that promise.

### Why lock a header

A header is code, and an edit to the code can change it. Here is a sale function whose header and body both lost their condition in the same edit: the header no longer says "never on a dry run", and the body no longer checks `dry_run`.

```diff include="steps/15-locked..steps/16-unlocked:src/store/sale.una" context="1" title="src/store/sale.una"
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

```text include="steps/16-unlocked/expected/output.txt"
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
```toml include="steps/15-locked/una.toml" title="steps/15-locked/una.toml"
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

```toml include="steps/17-lock-forms/una.toml" title="steps/17-lock-forms/una.toml"
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

```una include="steps/17-lock-forms/src/store/sale.una" title="steps/17-lock-forms/src/store/sale.una" verified="check"
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

```una include="steps/17-lock-forms/src/store/app.una" title="steps/17-lock-forms/src/store/app.una" verified="check, run"
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

```text include="steps/17-lock-forms/expected/output.txt"
LAMP-01 costs 1990
audit: LAMP-01: 1990 to 1791
a dry run plans 1791
```

The dry run reads the price and writes the audit line, and sets no price.

### A sale that cannot lose its dry run

Back to the sale of [Why lock a header](#why-lock-a-header), with its condition, its guard, and the lock of [How to write `[contracts]`](#how-to-write-contracts):

```una include="steps/15-locked/src/store/sale.una" title="steps/15-locked/src/store/sale.una" verified="check"
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

```una include="steps/15-locked/src/store/app.una" title="steps/15-locked/src/store/app.una" verified="check, run"
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

```text include="steps/15-locked/expected/output.txt"
a dry run plans 19920
set LAMP-01 to 1791
the sale applied 1791
```

The dry run of the desk plans its sale price and sets nothing. The real sale of the lamp sets its price. The handler `printed` prints each change instead of storing it, so you see when `set_price` runs.

### How a lock is checked

The body and the lock are checked separately. The verifier proves that the body keeps its header, as [chapter 8](/learn/capabilities/#s8-5) showed. The lock adds one more check: that the header keeps the lock. The header must grant no more than its lock.

#### A header may grant less

A header may grant less than its lock, since that only narrows what the function may do: fewer operations, a stronger condition, or no binding of a capability that the lock names. A binding that the lock does not name at all, or an operation that it does not list, is U3023.

#### An operation the lock does not list

Give `show_price` the right to set prices too:

```diff include="steps/17-lock-forms..steps/18-extra-op:src/store/sale.una" context="0" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -14 +14 @@
-  uses @prices: PriceList[price]
+  uses @prices: PriceList[price, set_price]
```

```text include="steps/18-extra-op/expected/rendered.txt"
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

```diff include="steps/15-locked..steps/19-weakened:src/store/sale.una" context="0" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -9 +9 @@
-  uses @prices: PriceList[set_price where not dry_run]
+  uses @prices: PriceList[set_price]
```

```text include="steps/19-weakened/expected/rendered.txt#L1-L12,L14,L18"
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
| To keep a supplier's module within what you grant it | A ceiling in `[boundaries]` ([section 11.5](#s11-5)) |
| The same rule on every call of a function | Its header; a lock only guards the header |
:::

Lock the functions whose authority matters to the business: the ones that change prices, send money or delete records.

### Check yourself: a narrower header

The header of `apply_sale` now asks for a stronger condition than its lock, and the guard matches it. The app adds a sale of 0 percent:

```diff include="steps/15-locked..steps/20-narrower:src/store/sale.una" context="0" title="src/store/sale.una"
--- a/src/store/sale.una
+++ b/src/store/sale.una
@@ -9 +9 @@
-  uses @prices: PriceList[set_price where not dry_run]
+  uses @prices: PriceList[set_price where not dry_run and percent > 0]
@@ -12 +12 @@
-  if not dry_run
+  if not dry_run and percent > 0
```

```una include="steps/20-narrower/src/store/app.una#main" title="steps/20-narrower/src/store/app.una"
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

```text include="steps/20-narrower/expected/output.txt"
a dry run plans 19920
set LAMP-01 to 1791
the sale applied 1791
a sale of 0 percent keeps 4500
```

A sale of 0 percent changes nothing, so the guard skips `set_price`, and no `set` line is printed for the rug.
:::

## 11.5 A ceiling for a module: `[boundaries]`

### What a boundary is

When a store lets a contractor in to service the label printer, it gives them a badge that opens the stockroom and nothing else. Whatever the contractor brings, the badge decides which doors open.

A **boundary** is such a badge for a module, written in `una.toml`. It marks a module, usually vendored code from a supplier, and gives it a **ceiling**: the most the rest of the package may ever grant it. A call into the module that would grant more fails the check.

### Why give a module a ceiling

The store copied a label printer's module into `src/vendor/labels.una`. A new version of it arrives, and besides printing, it now reads the clock. Its header says so, but the output does not change:

```diff include="steps/21-boundary..steps/22-unbounded:src/vendor/labels.una" context="0" title="src/vendor/labels.una"
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

This package has no boundary yet. The store accepts the new version with two small edits of its own: `main` declares that it holds the clock, and `una.toml` grants it. Without the first, `una check` reports U3001 at the call; without the second, `una run` stops with U3012 ([chapter 8](/learn/capabilities/#s8-2)).

```diff include="steps/21-boundary..steps/22-unbounded:una.toml" context="0" title="una.toml"
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

```una include="steps/22-unbounded/src/store/app.una" title="steps/22-unbounded/src/store/app.una" verified="check, run"
module store.app

import vendor.labels (print_label)

pub main() -> Unit
  uses @console: Console[print]
  uses @clock: Clock[now]
=
  print_label("LAMP-01", price: "19.90")
```

```text include="steps/22-unbounded/expected/output.txt"
[LAMP-01 | 19.90]
```

The package checks and runs, and the label looks as before. The call itself did not change: `print_label` takes the clock by name, as any call passes the capabilities its callee needs ([chapter 8](/learn/capabilities/#s8-1)). Nothing at the call says where the clock goes, and once the store's code holds a capability for a job of its own, a later version of the supplier's module can start using it with no change at all in the store's code. With network or file access, the same change could send data away. A boundary makes every such grant visible at the call, and turns one beyond the ceiling into an error.

### How to write `[boundaries]`

:::steps
```toml include="steps/21-boundary/una.toml" title="steps/21-boundary/una.toml"
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

```una include="steps/21-boundary/src/vendor/labels.una" title="steps/21-boundary/src/vendor/labels.una" verified="check"
module vendor.labels

--- Prints a shelf label for a product.
pub print_label(sku: Text, price: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("[{sku} | {price}]")
```

The store's code calls it:

```una include="steps/21-boundary/src/store/app.una" title="steps/21-boundary/src/store/app.una" verified="check, run"
module store.app

import vendor.labels (print_label)

pub main() -> Unit
  uses @console: Console[print]
=
  print_label("LAMP-01", price: "19.90") with @console = @console
```

```text include="steps/21-boundary/expected/output.txt"
[LAMP-01 | 19.90]
```

A call into the boundary takes nothing by name. The caller grants each capability with `with`, here `with @console = @console`: the label module's `@console` is the app's own `@console`. So every call into the module shows exactly what it receives.

### How calls into a boundary are checked

A **call into a boundary** is a call from code outside the boundary to a function, handler or policy inside it. Two rules apply to it here ([chapter 8](/learn/capabilities/#s8-5) shows the others), and code inside the boundary calls itself as usual.

#### Everything is granted with `with` (U3020)

Call the label module the usual way, without `with`:

```diff include="steps/21-boundary..steps/23-by-name:src/store/app.una" context="0" title="src/store/app.una"
--- a/src/store/app.una
+++ b/src/store/app.una
@@ -8 +8 @@
-  print_label("LAMP-01", price: "19.90") with @console = @console
+  print_label("LAMP-01", price: "19.90")
```

```text include="steps/23-by-name/expected/rendered.txt"
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

```una include="steps/24-over-ceiling/src/store/app.una" title="steps/24-over-ceiling/src/store/app.una"
module store.app

import vendor.labels (print_label)

pub main() -> Unit
  uses @console: Console[print]
  uses @clock: Clock[now]
=
  print_label("LAMP-01", price: "19.90") with @console = @console, @clock = @clock
```

```text include="steps/24-over-ceiling/expected/rendered.txt"
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

Each of these is U7002: a key that is not a module of the package, a key inside another key's extent, a malformed ceiling, a capability named twice in one ceiling, an unknown capability or operation, a trusted module inside a boundary, and the `[run] entry` inside a boundary. [Chapter 8](/learn/capabilities/#s8-5) shows more of the rules on calls into a boundary.

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

```una include="steps/25-fonts/src/vendor/labels/fonts.una" title="steps/25-fonts/src/vendor/labels/fonts.una"
module vendor.labels.fonts

--- Prints a shelf label in large letters.
pub print_large(sku: Text) -> Unit
  uses @console: Console[print]
=
  @console.print("** {sku} **")
```

```una include="steps/25-fonts/src/store/app.una" title="steps/25-fonts/src/store/app.una"
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

```text include="steps/25-fonts/expected/rendered.txt#L1"
[U3020] Error: `print_large` is in the boundary `vendor.labels` and needs `@console: Console[print]`, which a call into it grants only with `with`
```

The key `vendor.labels` covers every module below it, so `vendor.labels.fonts` is in the boundary too, and a call into it grants its capabilities only with `with`. Write `print_large("LAMP-01") with @console = @console`.
:::

## 11.6 Day-to-day: the store's invoice

### Five modules, one job each

Now the program from the start of the chapter. An order is a list of SKUs with quantities. The invoice looks each SKU up in the catalog, prices the line, shows what a member would pay for one unit, and names the SKUs the catalog does not list. Five modules under `src/store/` share the work, each about one subject:

- `money.una`: `Cents`, and `format` for amounts as people read them;
- `catalog.una`: `Product`, the `Catalog` service, and an in-memory catalog;
- `pricing.una`: line prices and the members' price;
- `invoice.una`: order lines, lookups, and the text of each line;
- `app.una`: `main`, the entry of the package.

The manifest is the one of [section 11.1](#s11-1), in edition `0.2`, with `store.app` as its entry.

### The import graph

The imports form a graph with no cycle: `money` imports nothing, `catalog` and `pricing` import `money`, `invoice` imports the three, and `app` imports `catalog` and `invoice`. An import cycle is U1003 ([An import cycle](#an-import-cycle-u1003)).

Each import goes from a module that knows more to one that knows less. `money` knows nothing of products, and `pricing` takes amounts, not products, so a price rule can be tested without a catalog. Only `invoice` puts a product, its price and its text together, and only `app` decides which catalog the program runs against.

### The interface of each module

The `pub` lines are the interface of each module. `money` shares `Cents` and `format`. `catalog` shares all it declares. `pricing` shares `line_cents` and `member_price`, and keeps `discount`. `invoice` shares its two kinds and its two functions. `app` shares only `main`, which `una run` needs, since the entry's `main` must be `pub`.

### Money

The same module as in [section 11.2](#s11-2), with its examples. `format` handles a negative amount, for a refund, and its private helper handles the digits:

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

The examples sit in the module, next to the function they test ([section 11.7](#s11-7)).

### The catalog

Unchanged from [section 11.2](#s11-2): the record, the service, and a handler that holds the products in a list. `listed` takes the products as a parameter where it is installed, so the app and each example choose the catalog they need, and the module keeps no product list of its own.

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

### Pricing

Two public functions and one private helper:

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

`member_price` promises that a member never pays more than the price, nor less than 0. The verifier proves that promise from `discount`'s header, not from its body, so `discount` states its own bounds in `ensures`. Both take a `Cents`, so neither can be called with a negative price. `discount` stays private: the invoice shows what a member pays, not how the discount is computed. [Exercise 2](#exercise-2-show-what-a-member-saves) changes that decision on purpose.

### The invoice

It imports from three modules, and is the only module that knows how an invoice line reads:

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

`product_of` turns a missing product into its own failure, `UnknownSku`, with the SKU. Its header writes its `uses` and `fails`, since it is `pub`. `describe` is pure, so a test can call it with any product, without a catalog. It uses three imported functions, `line_cents`, `member_price` and `format`, and the import lines at the top of the file name each of them, so a reader knows where to look for each one.

### The app

It runs the order against an in-memory catalog. `attempt` keeps each lookup's outcome, so an unknown SKU becomes a line of the invoice instead of stopping it:

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

### Running it

The whole package checks, runs and passes its tests. `una run .` prints the invoice shown in [What you'll build](#what-youll-build): two lines for the products the catalog lists, with their members' prices, and one for the chair it does not.

## 11.7 Testing it

### One command for every module

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

Each line names the module, then the example. Two modules may use the same example name, since the module tells them apart; within one module, each name is used once (U1002).

### Examples of private functions

An example sits in the module whose function it tests, so it can call the module's private functions too: `"the discount rounds down"` tests `discount`, which no other module can see. An example is never `pub`: it belongs to its module.

### A shared fake: the catalog's handler

Two of the invoice's examples look products up in an in-memory catalog:

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

The invoice's examples use the catalog's public handler, `listed`, imported like any other declaration. A fake shared this way stays the same for every module that tests against it ([chapter 10, Testing](/learn/testing/#s10-3), covers fakes).

### An entry module with no examples

`store.app` has no examples of its own. Everything it does is a call to a function that another module tests. An example could still run `main` with a fake console (`given @console = …`, [Testing `main`](/learn/testing/#testing-main-u3014) in chapter 10), but it would only show that something was printed. Keep an entry module this thin: wiring services to functions, and printing what they return. The less it decides, the less goes untested.

## 11.8 Common mistakes

Each mistake below is a small change to the day-to-day package, followed by what `una check .` reports.

### A module header that does not match its path (U1008)

:::mistake
Add `src/store/shipping.una`, and name the module after the file alone:

```una include="mistakes/1/src/store/shipping.una" title="mistakes/1/src/store/shipping.una"
module shipping

--- The shipping fee in cents: 4.90, and nothing from 50.00 on.
pub fee(subtotal: Int) -> Int = if subtotal >= 5000 then 0 else 490
```

```text include="mistakes/1/expected/rendered.txt"
[U1008] Error: module `shipping` is in `src/store/shipping.una`, which must hold module `store.shipping`
   ╭─[ src/store/shipping.una:1:8 ]
   │
 1 │ module shipping
   │        ────┬───
   │            ╰───── module `shipping` is in `src/store/shipping.una`, which must hold module `store.shipping`
   │
   │ Help: repair 1: declare `module store.shipping`, or move the file to match `shipping`; edit src/store/shipping.una:1:8..1:16 to "store.shipping"
   │
   │ Note: run `una explain U1008` for an explanation
───╯
1 of 1 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

*Why:* a module's name is its path under `src/`, so that an import says where to find the file. The diagnostic quotes both: the name the line declares, and the name its path requires.

*Fix:* write `module store.shipping`. The repair carries that edit, and `una fix .` applies it. See [U1008](/docs/errors/U1008/).
:::

### Using a name you did not import (U1001)

:::mistake
Drop `member_price` from the invoice's import, and keep the call:

```diff include="day-to-day..mistakes/2:src/store/invoice.una" context="1" title="src/store/invoice.una"
--- a/src/store/invoice.una
+++ b/src/store/invoice.una
@@ -4,3 +4,3 @@
 import store.money (format)
-import store.pricing (line_cents, member_price)
+import store.pricing (line_cents)
 
```

```text include="mistakes/2/expected/rendered.txt"
[U1001] Error: cannot find name `member_price` in this module, its imports or the prelude
    ╭─[ src/store/invoice.una:27:16 ]
    │
 27 │   let member = member_price(product.cents)
    │                ──────┬─────
    │                      ╰─────── cannot find name `member_price` in this module, its imports or the prelude
    │
    │ Note: run `una explain U1001` for an explanation
────╯
```

*Why:* a module sees its own declarations, its imports and the prelude. Being `pub` in another module is not enough. The mark points at the call, not at the import, since the import line itself is fine.

*Fix:* add the name to the import of `store.pricing`. See [U1001](/docs/errors/U1001/).
:::

### An import that clashes with a declaration (U1002)

:::mistake
Declare a private `format` in the invoice, next to the imported one:

```diff include="day-to-day..mistakes/3:src/store/invoice.una" context="1" title="src/store/invoice.una"
--- a/src/store/invoice.una
+++ b/src/store/invoice.una
@@ -22,2 +22,5 @@
 
+--- A quantity as the invoice writes it.
+format(quantity: Int) -> Text = "{quantity} x"
+
 --- One line of the invoice, as text, with the members' price of one unit.
```

```text include="mistakes/3/expected/rendered.txt"
[U1002] Error: `format` is already defined in this module
    ╭─[ src/store/invoice.una:4:21 ]
    │
  4 │ import store.money (format)
    │                     ───┬──
    │                        ╰──── `format` is already defined in this module
    │
 24 │ format(quantity: Int) -> Text = "{quantity} x"
    │ ───┬──
    │    ╰──── first defined here
    │
    │ Note: run `una explain U1002` for an explanation
────╯
```

*Why:* an explicit import and a declaration of the module share one set of names, so one name cannot mean two things. The first mark is on the imported name, and the second, "first defined here", on the new declaration.

*Fix:* rename the new function, for example `quantity_text`. See [U1002](/docs/errors/U1002/).
:::

### An import cycle (U1003)

:::mistake
Add a helper for members' prices to `store.money`, which then imports `store.pricing`, which imports `store.money`:

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

```text include="mistakes/4/expected/rendered.txt"
[U1003] Error: import cycle between modules `store.money` and `store.pricing`
   ╭─[ src/store/money.una:3:8 ]
   │
 3 │ import store.pricing (member_price)
   │        ──────┬──────
   │              ╰──────── import cycle between modules `store.money` and `store.pricing`
   │
   │ Note: run `una explain U1003` for an explanation
───╯
```

*Why:* modules form a graph with no cycle, so each can be read, and checked, after the modules it uses. The diagnostic names the two modules of the cycle, and points at the import in `store.money` that starts it.

*Fix:* put the helper where both of its parts are visible, such as `store.pricing` or `store.invoice`. See [U1003](/docs/errors/U1003/).
:::

### Imports out of order (U7001)

:::mistake
Put `store.money` before `store.catalog`:

```diff include="day-to-day..mistakes/5:src/store/invoice.una" context="1" title="src/store/invoice.una"
--- a/src/store/invoice.una
+++ b/src/store/invoice.una
@@ -2,4 +2,4 @@
 
+import store.money (format)
 import store.catalog (Catalog, Product, listed)
-import store.money (format)
 import store.pricing (line_cents, member_price)
```

```text include="mistakes/5/expected/rendered.txt"
[U7001] Error: line 3 is not in canonical form
   ╭─[ src/store/invoice.una:3:1 ]
   │
 3 │ import store.money (format)
   │ ─────────────┬─────────────
   │              ╰─────────────── line 3 is not in canonical form
   │
   │ Help: repair 1: rewrite in canonical form, as `una fmt` does; edit src/store/invoice.una:3:1..4:1 to ""
   │
   │ Note: run `una explain U7001` for an explanation
───╯
[U7001] Error: the canonical form adds lines before line 5
   ╭─[ src/store/invoice.una:5:1 ]
   │
 5 │ import store.pricing (line_cents, member_price)
   │ │
   │ ╰─ the canonical form adds lines before line 5
   │
   │ Help: repair 1: rewrite in canonical form, as `una fmt` does; edit src/store/invoice.una:5:1..5:1 to "import store.money (format)\n"
   │
   │ Note: run `una explain U7001` for an explanation
───╯
2 of 2 diagnostics have an edit that `una fix` applies (`una fix --dry-run` lists them)
```

*Why:* canonical form sorts imports by module path, and the names inside each import, so two people who add imports never produce two orders. U7001 reports each region that differs from the canonical form: here line 3 must go, and the same import must come back before line 5. Each repair carries its edit.

*Fix:* `una fmt .` sorts them, and so does `una fix .`. See [U7001](/docs/errors/U7001/).
:::

### A `0.3` table in an edition `0.2` package (U7002)

:::mistake
Lock the catalog lookup in the day-to-day manifest:

```diff include="day-to-day..mistakes/6:una.toml" context="1" title="una.toml"
--- a/una.toml
+++ b/una.toml
@@ -8 +8,4 @@
 grants = ["console"]
+
+[contracts]
+"store.invoice.product_of" = ["@catalog: Catalog[find]"]
```

```text include="mistakes/6/expected/rendered.txt"
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

## 11.9 Exercises

Each exercise starts from `exercises/N/start`: a package of this chapter with the exercise's examples added, and a stub of what to write when there is one. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`, so the layout is canonical.

### Exercise 1: a module for shipping

::::exercise
The invoice gains a total with shipping, 4.90 below 50.00 and nothing from 50.00 on. It imports `shipping_fee` from `store.shipping`, a module that does not exist yet:

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

`una test .` stops at the check until the module exists:

```text include="exercises/1/start/expected/diagnostics.txt"
error U1001 at src/store/invoice.una:6:8: module `store.shipping` is not a module of this package; the standard modules that can be imported are `std.host` and `std.testing`
error U1001 at src/store/invoice.una:32:54: cannot find name `shipping_fee` in this module, its imports or the prelude
```

Create the file, write its `module` line, and write the function. Amounts are in cents, so 50.00 is `5000` and 4.90 is `490`.

:::hint
*Hint:* the module `store.shipping` lives in `src/store/shipping.una`, and its function must be `pub` for the invoice to import it. One `if … then … else …` on one line is enough.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Add the module:

```una include="exercises/1/answer/src/store/shipping.una" title="exercises/1/answer/src/store/shipping.una" verified="check, run, test"
module store.shipping

--- The shipping fee of an order, in cents: 4.90, and nothing from 50.00 on.
pub shipping_fee(subtotal: Int) -> Int = if subtotal >= 5000 then 0 else 490
```

`5000` is the first subtotal that ships for free, so the test is `>=`, and both examples pass.
:::
::::

### Exercise 2: show what a member saves

::::exercise
The invoice wants a note with the discount on one unit, such as `members save 1.99`. The start package has `saving_note` with an empty text, and this example:

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

The report shows what the stub returns, an empty text, next to the expectation.

:::hint
*Hint:* `store.pricing` already computes the discount, in a private function. Importing it gives the U1004 of [section 11.2](#s11-2). Decide that it belongs to the module's interface, and say so in the declaration. Then `format` turns the cents into text.
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

`discount` now belongs to the interface of `store.pricing`: any module may call it, and changing its header later affects them all.
:::
::::

### Exercise 3: honor a lock

::::exercise
This exercise starts from the sale package of [section 11.4](#s11-4), in edition `0.3`. It adds `end_sale`, which puts a product's old price back, and a lock for it in `una.toml`:

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

Change `end_sale` so that a dry run sets no price, and its header keeps the lock. Do not change `una.toml`.

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

The header now keeps the lock, and the body keeps the header: two separate proofs, as in [How a lock is checked](#how-a-lock-is-checked).
:::
::::

## 11.10 Recap and reference

### For agents

:::agents
A diagnostic about an import carries the place of the declaration as a related span, and its repair. For [Private stays private](#private-stays-private):

```json include="steps/09-private/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U1004","severity":"error","domain":"names","message":"function `digits` is private to module `store.money`","primary":{"file":"src/store/app.una","start":{"line":4,"col":21},"end":{"line":4,"col":27}},"related":[{"file":"src/store/money.una","start":{"line":10,"col":1},"end":{"line":10,"col":7},"message":"declared here without `pub`"}],"repairs":[{"rank":1,"escape_cost":0,"widens":{"kind":"visibility","cost":"every module may then call it: check that it belongs to the module's interface"},"description":"declare `digits` with `pub`","edit":{"file":"src/store/money.una","start":{"line":10,"col":1},"end":{"line":10,"col":1},"replacement":"pub "}}],"explain":"una explain U1004"}],"fixable":0}
```

The repair has `escape_cost` 0, but `widens` names the visibility it would open, so `una fix` skips it. It gives the reason `widens authority` for every repair that widens what code may reach, visibility included:

```text include="steps/09-private/expected/commands/fix.txt"
$ una fix --dry-run .
skipped src/store/money.una:10:1 U1004 declare `digits` with `pub`: widens authority
```

The compact rule: *one module per file, named by its path; take each declaration you use with a named import; make a declaration `pub` only on purpose, with its whole header written; in edition `0.3`, a header never grants more than its lock, and a call into a boundary grants everything with `with`, within the ceiling.*
:::

### Recap

:::recap
- One file is one module, and its header names its path under `src/`: `src/store/money.una` is `module store.money`.
- Declarations are private by default. Mark `pub` only what other modules need, with a doc comment and its whole header written.
- Import each declaration you use by name. A sum kind brings its variants, and a record its constructor and fields.
- Keep the imports a graph with no cycle, and let `una fmt` keep them sorted.
- `una.toml` has a fixed set of tables and keys; an unknown one is U7002. A package imports only its own modules, `std.host` and `std.testing`.
- `verification.lock` pins the solver, so every machine gets the same result.
- In edition `0.3`, lock the `uses` of a public function in `[contracts]`: its header may grant less, never more (U3023).
- In edition `0.3`, give a supplier's module a ceiling in `[boundaries]`: calls into it grant with `with` (U3020), within it (U3021).
:::

### Reference

:::reference
- Construct and configuration pages: [modules and imports](/docs/language/modules/), [`kind`](/docs/language/types/kind/), [`where`](/docs/language/types/where/), [`capability` and `op`](/docs/language/capabilities/capability/), [`handler`](/docs/language/capabilities/handler/), [`uses`](/docs/language/capabilities/uses/), [`example`](/docs/language/examples/example/), [canonical form](/docs/language/canonical-form/), [`una.toml`](/docs/configure/), [`[package] name`](/docs/configure/package/name/), [`[package] version`](/docs/configure/package/version/), [`[package] edition`](/docs/configure/package/edition/), [`[run] entry`](/docs/configure/run/entry/), [`[run] grants`](/docs/configure/run/grants/), [`[labels] categories`](/docs/configure/labels/categories/), [`[trusted] modules`](/docs/configure/trusted/modules/), [`[escape_budget] checked_per_module`](/docs/configure/escape-budget/checked-per-module/), [`[boundaries]`](/docs/configure/boundaries/), [`verification.lock`](/docs/configure/verification-lock/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/), [U1003](/docs/errors/U1003/), [U1004](/docs/errors/U1004/), [U1005](/docs/errors/U1005/), [U1008](/docs/errors/U1008/), [U1009](/docs/errors/U1009/), [U3012](/docs/errors/U3012/), [U3020](/docs/errors/U3020/), [U3021](/docs/errors/U3021/), [U3023](/docs/errors/U3023/), [U5001](/docs/errors/U5001/), [U5003](/docs/errors/U5003/), [U7001](/docs/errors/U7001/), [U7002](/docs/errors/U7002/), [U7004](/docs/errors/U7004/)
- Specification: [diagnostics, the command line and project files](/docs/spec/13-diagnostics-and-abi/), [grammar](/docs/spec/02-grammar/), [static semantics](/docs/spec/10-static-semantics/), [functions and contracts](/docs/spec/04-functions-and-contracts/), [canonical form](/docs/spec/15-canonical-form/), [capabilities and effects](/docs/spec/05-capabilities-and-effects/), [verification](/docs/spec/12-verification/)
:::
