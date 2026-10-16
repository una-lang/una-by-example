---
learn: "5"
title: Collections
editions: ["0.2"]
codes: [U0007, U0101, U2001, U2007, U2019, U2020, U2025, U3007]
time: 35
builds: A daily sales report that reads order lines from JSON, groups them by category and sums them up
prerequisites: ["2", "3", "4"]
template: 2
---

# 5 Collections

Most of a working program moves data around in groups: the lines of an order, the products of a catalog, the stock of each SKU, a batch of records that arrives as JSON. In Una these groups are values. A list or a map never changes behind your back, a lookup that can find nothing says so in its type, and every place where a binding changes is marked in the code. This chapter shows how to build, search, transform and group collections, and how to read and write JSON, through a report that a store runs at the end of each day.

## What you'll build

:::build
A daily sales report. It reads the day's order lines, exported by the shop as one JSON object per line, skips the lines it cannot read, groups the rest by category, finds the best seller, and ends with a JSON summary for the accounting service:

```text include="day-to-day/expected/output.txt"
8 lines, 1 skipped
furniture: 2 units, 318.00
lighting: 8 units, 144.40
other: 2 units, 48.00
textiles: 4 units, 180.00
best seller: LAMP-01, 6 units
{"categories":4,"cents":69040,"skipped":1,"units":16}
```

You will learn to:

- build lists and loop over them with `for`, updating a `let edit` binding;
- handle a value that may be missing with `Option`, `when` and `or_else`;
- transform lists with `map`, `filter`, `fold` and `first_where`, and choose between them and a loop;
- count and group with a `Map`, whose keys come out in order;
- read fields from parsed JSON, and write canonical JSON.
:::

## Why it works this way

In many languages a collection is a shared, mutable object. You pass a list to a function, and the function may add to it or sort it in place, so the caller's data changes without a sign at the call. A lookup that finds nothing returns a null or throws, and its type does not say which. Parsed JSON often arrives as an untyped dictionary, and a missing field surfaces as a crash or a null far from the line that read it.

Una makes each of these visible:

:::steps
1. **Collections are values.** `append` returns a new list, and `with` returns a new map. A function that receives a list cannot change the caller's list, unless the call marks the argument `edit` ([`edit` parameters](/learn/memory-and-concurrency/#s12-2), in chapter 12).
2. **A change is marked where it happens.** A binding that changes is declared `let edit`, and a call that updates a map in place is written `edit stock.set(...)`.
3. **Absence is a type.** `first`, `at`, `get` and `first_where` return an `Option`. To use the value inside, you write a `when` that also says what happens when there is none, and the checker holds you to it.
4. **JSON is a sum kind.** A parsed value is a `Json`, with one variant for each kind of JSON value. Reading a field is a `get`, which gives an `Option`, and a `when`. A misspelt field name is still `None` at run time, since no checker knows which fields a text will hold, but the code must say on that line what a missing field means.
:::

> [!KEY]
> A name in Una holds one value until the code says, with `edit`, that it changes. A list or a map you pass to a function stays as it was, unless the call itself says `edit`.

## 5.1 Lists

### Values of one type, in order

A list holds values of one type, in order. You write it between brackets, and `List[Int]` is its type. The prelude, the functions every module has without an import, gives lists most of what a program needs. You call them with method syntax: `more.sum()` is the call `sum(more)`.

### Each step is a package

Each step of this chapter is a package, as in [chapter 1](/learn/hello/#s1-1): a directory with `una.toml`, `verification.lock` and the module under `src/`. The manifest names the package and the module that `una run` starts:

```toml include="steps/01-lists/una.toml" title="steps/01-lists/una.toml"
[package]
name = "cart"
version = "0.1.0"
edition = "0.2"

[run]
entry = "cart"
grants = ["console"]
```

`verification.lock` pins the solver and is the same in every example: copy it from chapter 1, or take the step's package, whole, from the chapter's download, `05-collections.tar.gz`. Then, in the package's directory:

```sh
una check .
una run .
```

### A cart and its receipt

Start with the quantities of a cart, then the SKUs on its receipt:

:::steps
```una include="steps/01-lists/src/cart.una" title="steps/01-lists/src/cart.una" verified="check, run"
module cart

--- The SKUs of a cart in the order a receipt lists them.
receipt(skus: List[Text]) -> Text = skus.sort().join(separator: ", ")

pub main() -> Unit
  uses @console: Console[print]
=
  let quantities = [2, 1, 3]
  let more = quantities.append(item: 4)
  @console.print("{quantities} then {more}")
  @console.print("{more.len} lines, {more.sum()} units")
  @console.print("a line of 3 units: {more.contains(item: 3)}")
  let skus = ["RUG-07", "LAMP-01", "DESK-02"]
  @console.print(receipt(skus))
```

1. **`[2, 1, 3]`.** A list literal. Every element has the same type, here `Int`. A literal that mixes `Int` and `Text` does not check.
2. **`quantities.append(item: 4)`.** This returns a new list with `4` at the end. `quantities` itself does not change: the first line of the output shows both lists.
3. **`more.len`.** The number of elements, written without parentheses, as on `Text`. A function that takes nothing but its receiver may be called without parentheses: `raw.trim` and `raw.trim()` are the same call. This tutorial writes `.len` and `.trim` without them.
4. **`more.sum()` and `more.contains(item: 3)`.** The sum of a list of integers, and whether an element is in the list. `Int` has no upper bound, so a sum never overflows.
5. **`skus.sort().join(separator: ", ")`.** `sort` returns the elements in ascending order, and `join` puts a list of texts together with a separator. `receipt` is a function of one expression, written after `=` on its header line.
:::

`una run .` prints:

```text include="steps/01-lists/expected/output.txt"
[2, 1, 3] then [2, 1, 3, 4]
4 lines, 10 units
a line of 3 units: true
DESK-02, LAMP-01, RUG-07
```

### Sorting and reading positions

`sort` works on any type with an order: `Int`, `Text`, the fixed-width integers, and kinds whose variants carry no data, in the order the variants are declared. It is stable, so equal elements keep the order they had. A record such as an order line has no order of its own, and [Sorting records](#sorting-records-u2025) shows what the checker says when you try.

Positions in a list count from 0. There is no `xs[0]` syntax. `xs.at(index: 0)` and `xs.first()` read an element, and they return an `Option`, because the list may be shorter than you think. [Section 5.3](#s5-3) shows how to use what they return.

### Appending without copying

> [!NOTE]
> A list is a value, but `append` does not copy the whole list each time. When nothing else holds the list, it is updated in place, so a loop that appends one element at a time takes time in proportion to the number of elements.

## 5.2 Loops: `for` and `let edit`

### Updating a binding in a loop

`for` visits the elements of a list in order, or the integers of a range. A loop computes something by updating a binding declared before it, and that binding must be declared `let edit`. A plain `let` names one value for good.

### Totals, bulk lines and weeks

The step totals a cart, lists its bulk lines, and walks a range of weeks:

:::steps
```una include="steps/02-for/src/totals.una" title="steps/02-for/src/totals.una" verified="check, run"
module totals

--- One line of a cart: a SKU, how many units, and the price of one unit in cents.
kind CartLine
  sku: Text
  quantity: Int
  cents: Int

--- What a cart costs, in cents.
total(lines: List[CartLine]) -> Int
=
  let edit sum = 0
  for line in lines
    sum = sum + line.quantity * line.cents
  sum

--- The SKUs of the lines with more than `limit` units, in the order of the cart.
bulk(lines: List[CartLine], limit: Int) -> List[Text]
=
  let edit found: List[Text] = []
  for line in lines
    if line.quantity > limit
      found = found.append(item: line.sku)
  found

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = CartLine(sku: "LAMP-01", quantity: 2, cents: 1990)
  let rug = CartLine(sku: "RUG-07", quantity: 5, cents: 4500)
  let cart = [lamp, rug]
  @console.print("total: {total(cart)} cents")
  @console.print("bulk: {bulk(cart, limit: 3)}")
  for week in 1..3
    @console.print("week {week}: {total(cart) * week} cents so far")
```

1. **`let edit sum = 0`.** An editable binding. Its type, `Int`, comes from its first value, and every later value must have that type.
2. **`sum = sum + line.quantity * line.cents`.** An assignment gives `sum` a new value. It is a statement on its own line.
3. **`if line.quantity > limit` with no `else`.** Inside a block, an `if` without `else` is a statement: its body runs only when the condition holds.
4. **`let edit found: List[Text] = []`.** An empty list, with its type written so that a reader sees what it will hold.
5. **`for week in 1..3`.** A range. `1..3` includes 3, and `1..<3` leaves it out, which is the form to use with a length: `0..<items.len`. A range whose start is above its end, such as `3..1`, is empty.
:::

`una run .` prints:

```text include="steps/02-for/expected/output.txt"
total: 26480 cents
bulk: ["RUG-07"]
week 1: 26480 cents so far
week 2: 52960 cents so far
week 3: 79440 cents so far
```

The output of `bulk` is a list of texts, and interpolation writes it in the form you would type in Una, with brackets and quotes.

### What lives from one turn to the next

A binding declared inside the body, with `let`, is new at each turn of the loop and is gone after it. To carry a value from one turn to the next, or out of the loop, declare it before the loop with `let edit`, as `sum` and `found` are. The loop variable, `line` or `week`, is a plain binding: you read it, and the next turn gives it the next element.

### No `while`

> [!TIP]
> Una has no `while`. A loop over a list or a range covers almost every case in day-to-day code, and recursion covers the rest. Because every loop walks a finite list or range, a reader can see where it ends.

## 5.3 A value that may be missing: `Option`

### A search can find nothing

A search can find nothing. A product may not be in the catalog, a list may be empty, and a text may not hold a number. In Una such a result has the type `Option[T]`, which is either `Some(value)` or `None`. You cannot use it as a `T` until you have said what happens in each case.

### Looking up a price

The step looks products up in a catalog, and reads a number and a position:

:::steps
```una include="steps/03-option/src/lookup.una" title="steps/03-option/src/lookup.una" verified="check, run"
module lookup

--- A product the store sells, with the price of one unit in cents.
kind Product
  sku: Text
  cents: Int

--- The price of `sku`, or `None` when the catalog does not list it.
price_of(catalog: List[Product], sku: Text) -> Option[Int]
=
  let found = catalog.first_where(keep: fn(product) -> product.sku == sku)
  when found
    is Some(product) -> Some(product.cents)
    is None -> None

--- What a product page shows for `sku`.
label(catalog: List[Product], sku: Text) -> Text
=
  let price = price_of(catalog, sku: sku)
  when price
    is Some(cents) -> "{sku}: {cents} cents"
    is None -> "{sku}: not sold here"

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Product(sku: "LAMP-01", cents: 1990)
  let desk = Product(sku: "DESK-02", cents: 15900)
  let catalog = [lamp, desk]
  @console.print(label(catalog, sku: "DESK-02"))
  @console.print(label(catalog, sku: "CHAIR-09"))
  let missing = price_of(catalog, sku: "CHAIR-09")
  @console.print("{missing} or {missing.or_else(default: 0)}")
  let typed = "3".to_int()
  @console.print("{typed} and {catalog.at(index: 5)}")
```

1. **`catalog.first_where(keep: fn(product) -> product.sku == sku)`.** The first element for which the test holds, as an `Option[Product]`. The test is a lambda, a function written in place ([chapter 3](/learn/functions/#s3-5); [section 5.4](#s5-4) uses more of them).
2. **`when found`.** A `when` over an `Option` has one arm per case, `is Some(product)` and `is None`. The name in `Some(product)` binds the value inside. A `when` that leaves out a case does not check.
3. **`Some(product.cents)`.** `price_of` itself returns an `Option`, so its caller decides what a missing price means. `label` decides: it prints "not sold here".
4. **`missing.or_else(default: 0)`.** The short form when a default is right: the value inside `Some`, or the default for `None`.
5. **`"3".to_int()` and `catalog.at(index: 5)`.** Two more functions that return an `Option`: a text that may not be a number, and a position that may be past the end.
:::

`una run .` prints:

```text include="steps/03-option/expected/output.txt"
DESK-02: 15900 cents
CHAIR-09: not sold here
None or 0
Some(3) and None
```

An `Option` interpolates as `Some(3)` or `None`, which helps when you debug, but a report should say what the absence means, as `label` does.

### Choosing how to use an `Option`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Do different things when the value is there and when it is not | `when` with `is Some(v)` and `is None` |
| Carry on with a default | `or_else(default: v)`, or `if none use v` on the line under the call ([chapter 6](/learn/failure/)) |
| Know only whether there is a value | `is_some()`, or `o is None` in a condition |
| Make a missing value a failure of your function | `if none fail V`, in [chapter 6](/learn/failure/) |
:::

### The default of `or_else` is computed first

> [!NOTE]
> The default of `or_else` is computed before the call, whether it is used or not. Keep it a plain value, such as `0` or `"other"`.

## 5.4 Functions over lists: `map`, `filter` and `fold`

### Saying what to do with each element

A loop says how to walk a list. Often you only need to say what to do with each element, and the prelude walks the list for you. These functions take a function as an argument:

- `map(each: f)` gives a new list of `f(x)` for each element `x`, in order.
- `filter(keep: f)` keeps the elements for which `f(x)` is `true`.
- `fold(initial: v, step: f)` carries a value from the first element to the last: it starts from `v`, and replaces it with `f(value, x)` at each element.
- `first_where(keep: f)` gives the first element for which `f(x)` is `true`, and stops there.

Each calls its function on the elements from first to last, at most once per element.

### Pricing a cart without a loop

The step prices a cart, counts its units, and decides whether it ships free:

:::steps
```una include="steps/04-higher-order/src/pricing.una" title="steps/04-higher-order/src/pricing.una" verified="check, run"
module pricing

--- One line of a cart: a SKU, how many units, and the price of one unit in cents.
kind CartLine
  sku: Text
  quantity: Int
  cents: Int

--- What one line costs, in cents.
line_cents(line: CartLine) -> Int = line.quantity * line.cents

--- Whether a cart ships for free: 10000 cents or more, not counting gift cards.
ships_free(lines: List[CartLine]) -> Bool
=
  let goods = lines.filter(keep: fn(line) -> not line.sku.starts_with(prefix: "GIFT-"))
  goods.map(each: line_cents).sum() >= 10000

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = CartLine(sku: "LAMP-01", quantity: 2, cents: 1990)
  let rug = CartLine(sku: "RUG-07", quantity: 1, cents: 4500)
  let gift = CartLine(sku: "GIFT-50", quantity: 1, cents: 5000)
  let cart = [lamp, rug, gift]
  @console.print("{cart.map(each: line_cents)}")
  let big = cart.filter(keep: fn(line) -> line.quantity >= 2)
  @console.print("{big.map(each: fn(line) -> line.sku)}")
  let units = cart.fold(initial: 0, step: fn(sum, line) -> sum + line.quantity)
  @console.print("{units} units")
  @console.print("free shipping: {ships_free(cart)}")
```

1. **`cart.map(each: line_cents)`.** A function declared with a name can be passed by that name.
2. **`fn(line) -> line.quantity >= 2`.** A lambda. Its parameter types come from where it is used, and its body is one expression. When it needs more than one line, declare a function and pass its name.
3. **`fold(initial: 0, step: fn(sum, line) -> sum + line.quantity)`.** The step takes the value so far and the next element. Here it counts units; `initial` is the result for an empty cart.
4. **`ships_free`.** The same tools in context: leave out the gift cards, price each line, add up, compare. Each step is one call, and the result of one is the input of the next.
:::

`una run .` prints:

```text include="steps/04-higher-order/expected/output.txt"
[3980, 4500, 5000]
["LAMP-01"]
4 units
free shipping: false
```

### What a lambda can see

A lambda sees the values of the bindings around it as they were when it was made, and it cannot assign to a `let edit` binding outside it. To accumulate, use `fold`, or a `for` loop.

### A function over the list, or a loop

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| A new list with one result per element | `map` |
| Some of the elements | `filter` |
| One element, the first that matches | `first_where` |
| A total of integers | `map`, then `sum()` |
| One value built from all the elements | `fold`, or `for` with `let edit` |
| Several results at once, or a step with an `if` and a few lines | `for` with `let edit` |
:::

The last rows have two right answers. Choose the one a reader follows faster: a `fold` with a one-line step, or a loop when the step needs room.

## 5.5 Maps

### Keys and their values

A `Map[K, V]` maps keys to values: the stock of each SKU, the units of each category. Each key appears once. You make an empty map with `empty_map()`, and you read and change it with [the operations of a map](#the-operations-of-a-map).

### Stock by SKU

The step keeps the stock of each SKU, and groups sales by category:

:::steps
```una include="steps/05-maps/src/stock.una" title="steps/05-maps/src/stock.una" verified="check, run"
module stock

--- A sale of some units of one SKU, in a category.
kind Sale
  sku: Text
  category: Text
  quantity: Int

--- How many units each category sold.
units_by_category(sales: List[Sale]) -> Map[Text, Int]
=
  let edit totals: Map[Text, Int] = empty_map()
  for sale in sales
    let before = totals.get(key: sale.category).or_else(default: 0)
    edit totals.set(key: sale.category, value: before + sale.quantity)
  totals

pub main() -> Unit
  uses @console: Console[print]
=
  let edit stock: Map[Text, Int] = empty_map()
  edit stock.set(key: "LAMP-01", value: 4)
  edit stock.set(key: "DESK-02", value: 1)
  let restocked = stock.with(key: "RUG-07", value: 9)
  @console.print("{stock} and {restocked}")
  let lamps_left = stock.get(key: "LAMP-01")
  let vases_left = stock.get(key: "VASE-03")
  @console.print("{lamps_left} {vases_left}")
  @console.print("{restocked.keys()}")
  let lamp = Sale(sku: "LAMP-01", category: "lighting", quantity: 2)
  let rug = Sale(sku: "RUG-07", category: "textiles", quantity: 1)
  let shade = Sale(sku: "SHADE-05", category: "lighting", quantity: 3)
  for entry in units_by_category([lamp, rug, shade]).entries()
    @console.print("{entry.key}: {entry.value}")
```

1. **`let edit stock: Map[Text, Int] = empty_map()`.** An empty map, with its key and value types written.
2. **`edit stock.set(key: "LAMP-01", value: 4)`.** `set` adds the key, or replaces its value. It updates the map, so the binding is `let edit`, and the call starts with `edit`.
3. **`stock.with(key: "RUG-07", value: 9)`.** The value form: a new map with one more entry. `stock` keeps its two entries, as the first line of the output shows.
4. **`stock.get(key: "VASE-03")`.** `get` returns an `Option`: `None` for a key the map does not hold. A missing key is not an error.
5. **`totals.get(key: sale.category).or_else(default: 0)`.** The grouping pattern: read the total so far, with `0` for a category not seen yet, then `set` the new total. You will meet it again in the day-to-day program.
:::

`una run .` prints:

```text include="steps/05-maps/expected/output.txt"
{"DESK-02": 1, "LAMP-01": 4} and {"DESK-02": 1, "LAMP-01": 4, "RUG-07": 9}
Some(4) None
["DESK-02", "LAMP-01", "RUG-07"]
lighting: 5
textiles: 1
```

### Entries in key order

A map keeps its entries ordered by key, not in the order you added them. `keys()`, `values()` and `entries()` all list them in that order, and `for entry in m.entries()` gives each `entry.key` with its `entry.value`. So a report built from a map comes out sorted by key, with no `sort` call, and the same input always gives the same output.

### Lookup cost and key types

The order has a cost and a rule. Each lookup, insertion and removal takes O(log n) time for a map of n entries. A key type must have an order: `Text`, `Int`, the fixed-width integers, or a kind whose variants carry no data. A record cannot be a key.

### The operations of a map

| Operation | Gives | Notes |
| --- | --- | --- |
| `m.len` | `Int` | the number of entries |
| `m.has(key: k)` | `Bool` | |
| `m.get(key: k)` | `Option[V]` | `None` for a missing key |
| `edit m.set(key: k, value: v)` | updates `m` | adds or replaces |
| `edit m.remove(key: k)` | updates `m` | |
| `m.with(key: k, value: v)` | a new map | `m` is unchanged |
| `m.without(key: k)` | a new map | `m` is unchanged |
| `m.keys()`, `m.values()`, `m.entries()` | lists | in key order |

## 5.6 JSON

### JSON values are a sum kind

JSON is how stores, services and exports exchange records. The prelude reads it into a value of the kind `Json`, with one variant for each kind of JSON value: `Null`, `Boolean(value)`, `Number(value)` for a whole number, `Decimal(text)` for a number with a fraction or an exponent, `Str(value)`, `Array(items)` and `Object(fields)`. The fields of an object are a `Map[Text, Json]`, so everything from [section 5.5](#s5-5) applies.

### Reading and writing a product feed

The step parses two records of a product feed, reads a price, and writes JSON back:

:::steps
```una include="steps/06-json/src/feed.una" title="steps/06-json/src/feed.una" verified="check, run"
module feed

--- The price in a product record of the catalog feed, or `None` when it has none.
price(record: Json) -> Option[Int]
=
  when record
    is Object(fields) ->
      let cents = fields.get(key: "cents").or_else(default: Null)
      when cents
        is Number(value) -> Some(value)
        else -> None
    else -> None

pub main() -> Unit
  uses @console: Console[print]
=
  let text = "\{\"sku\": \"LAMP-01\", \"cents\": 1990, \"tags\": [\"new\"]\}"
  let record = text.parse_json()
    if error use Null
  @console.print("{record}")
  @console.print("{price(record)}")
  let broken = "\{\"sku\": \"LAMP-01\",\}".parse_json()
    if error use Null
  @console.print("{price(broken)}")
  let edit fields: Map[Text, Json] = empty_map()
  edit fields.set(key: "sku", value: Str(value: "LAMP-01"))
  edit fields.set(key: "in_stock", value: Boolean(value: true))
  edit fields.set(key: "cents", value: Number(value: 1990))
  @console.print(Object(fields).to_json())
```

1. **`\{`, `\}` and `\"`.** JSON in a text literal. In Una text, `{` starts an interpolation, so a literal brace is written `\{` and `\}`, and a quote is `\"`.
2. **`text.parse_json()` and `if error use Null`.** Parsing can fail, since the text may not be JSON. The line under the call says what to do then: here, carry on with `Null`. [Chapter 6, Failure](/learn/failure/), explains this clause and the others.
3. **`when record` with `is Object(fields)`.** Reading JSON is reading a sum kind: one arm for the variant you expect, and `else` for the rest. Then `fields.get(key: "cents")` is an ordinary map lookup.
4. **`Object(fields).to_json()`.** Writing. `to_json` writes one canonical text: no spaces, and the keys of each object in order.
:::

`una run .` prints:

```text include="steps/06-json/expected/output.txt"
Object({"cents": Number(1990), "sku": Str("LAMP-01"), "tags": Array([Str("new")])})
Some(1990)
None
{"cents":1990,"in_stock":true,"sku":"LAMP-01"}
```

The first line is the interpolation of a `Json`, which shows the Una value, not JSON text. Note that the keys come out sorted: a JSON object is a map, so the order of the input is not kept. The second record has a trailing comma, which JSON does not allow, so it parses as `Null` and has no price.

### When parsing fails: `JsonError`

When parsing fails, the failure is a `JsonError`. `Syntax(at)` gives the position of the first character where no valid JSON can continue, and `TooDeep`, `DuplicateKey` and `NumberTooLong` name the other cases. Each variant carries the position `at`, counted in characters from 0. [Chapter 6](/learn/failure/) shows how to keep the failure and report it.

### Numbers with a fraction

> [!WARNING]
> A JSON number with a fraction, such as `19.90`, is a `Decimal`, not a `Number`, so `is Number(value)` does not match it. Keep money in whole cents, in JSON as in Una.

## 5.7 Day-to-day: a daily sales report

### What the report must do

At the end of each day the shop exports its order lines, one JSON object per line. Some lines are incomplete. The report must read every line it can, say how many it skipped, total the units and the revenue of each category, name the best seller, and hand the totals to the accounting service as JSON.

The design follows from the data. The export is text, so each line is parsed on its own, and a bad line becomes `None` instead of stopping the report. The fields have types, so a `Line` record holds them once they are read, and nothing after `read_line` deals with JSON. The totals are per category and per SKU, so two maps hold them, and their key order gives the report its order.

The program is one module. Here it is in parts.

### The records

Two kinds: one for a line of the export, and one for what a category sold.

```una include="day-to-day/src/report.una#Line..Summary" title="day-to-day/src/report.una" caption="the records"
--- One line of an order: a SKU, its category, how many units, and the price of one unit in cents.
pub kind Line
  sku: Text
  category: Text
  quantity: Int
  cents: Int

--- What one category sold: its units and its revenue in cents.
pub kind Summary
  category: Text
  units: Int
  cents: Int
```

### Reading a line

Two private helpers read one field each, as an `Option`. `read_line` parses the text, checks that it is an object, and builds a `Line` when the fields it needs are there.

```una include="day-to-day/src/report.una#text_field..read_line" title="day-to-day/src/report.una" caption="reading JSON"
--- The text in the field `name` of a JSON object, or `None` when it is missing or not a string.
text_field(fields: Map[Text, Json], name: Text) -> Option[Text]
=
  let found = fields.get(key: name).or_else(default: Null)
  when found
    is Str(value) -> Some(value)
    else -> None

--- The whole number in the field `name` of a JSON object, or `None`.
int_field(fields: Map[Text, Json], name: Text) -> Option[Int]
=
  let found = fields.get(key: name).or_else(default: Null)
  when found
    is Number(value) -> Some(value)
    else -> None

--- An order line from one line of the export, or `None` when the line cannot be read.
--- A line without a category counts under "other".
pub read_line(text: Text) -> Option[Line]
=
  let json = text.parse_json()
    if error use Null
  when json
    is Object(fields) ->
      let category = text_field(fields, name: "category").or_else(default: "other")
      let sku = text_field(fields, name: "sku")
      let quantity = int_field(fields, name: "quantity")
      let cents = int_field(fields, name: "cents")
      when sku
        is None -> None
        is Some(code) ->
          when quantity
            is None -> None
            is Some(units) ->
              when cents
                is None -> None
                is Some(price) -> Some(Line(sku: code, category: category, quantity: units, cents: price))
    else -> None
```

A missing category has a sensible default, so `or_else` gives "other". A missing SKU, quantity or price has none: the line cannot be used, so the result is `None`. Each `when` handles one of these fields, and the three nest. [Chapter 6](/learn/failure/) shows `if none`, which says the same thing in one line per field.

### Keeping the lines that could be read

A `for` loop over the export, with a `when` that appends the `Some` values. The `None` arm gives `unit`, the only value of the type `Unit`, and so does nothing: the line is skipped.

```una include="day-to-day/src/report.una#read_all" title="day-to-day/src/report.una"
--- The lines that could be read, in the order of the export.
pub read_all(export: List[Text]) -> List[Line]
=
  let edit lines: List[Line] = []
  for text in export
    let found = read_line(text)
    when found
      is Some(line) ->
        lines = lines.append(item: line)
      is None -> unit
  lines
```

### Grouping

The pattern of [section 5.5](#s5-5), twice. `by_category` keeps a `Summary` per category, and `units_by_sku` an `Int` per SKU.

```una include="day-to-day/src/report.una#by_category..units_by_sku" title="day-to-day/src/report.una" caption="grouping with maps"
--- The units and revenue of each category, ordered by category.
pub by_category(lines: List[Line]) -> Map[Text, Summary]
=
  let edit totals: Map[Text, Summary] = empty_map()
  for line in lines
    let empty = Summary(category: line.category, units: 0, cents: 0)
    let before = totals.get(key: line.category).or_else(default: empty)
    let units = before.units + line.quantity
    let cents = before.cents + line.quantity * line.cents
    edit totals.set(key: line.category, value: Summary(category: line.category, units: units, cents: cents))
  totals

--- The units sold of each SKU.
pub units_by_sku(lines: List[Line]) -> Map[Text, Int]
=
  let edit units: Map[Text, Int] = empty_map()
  for line in lines
    let before = units.get(key: line.sku).or_else(default: 0)
    edit units.set(key: line.sku, value: before + line.quantity)
  units
```

The default for a new category is a `Summary` with zeros, so the same lines handle the first line of a category and every later one.

### The best seller

`fold` finds the largest number of units. `max` names its second parameter `b`, so the call labels it, as every argument after the first is labeled. Then `first_where` finds the first entry with that number. Entries come in SKU order, so on a tie the first SKU in order wins, and the result does not depend on the order of the export. An empty map gives `None`, and `headline` says so. An `Entry` is the prelude's record of one key and its value, so in `headline`, `entry.key` is the SKU and `entry.value` its units.

```una include="day-to-day/src/report.una#best_seller..headline" title="day-to-day/src/report.una"
--- The SKU that sold the most units, the first in SKU order on a tie; `None` for no sales.
pub best_seller(units: Map[Text, Int]) -> Option[Entry[Text, Int]]
=
  let most = units.values().fold(initial: 0, step: fn(top, n) -> max(top, b: n))
  units.entries().first_where(keep: fn(entry) -> entry.value == most)

--- The report's line about the best seller.
pub headline(best: Option[Entry[Text, Int]]) -> Text
=
  when best
    is Some(entry) -> "best seller: {entry.key}, {entry.value} units"
    is None -> "no sales"
```

### Money and the JSON summary

`money` writes cents as an amount with two decimals. `totals_json` adds up the categories with `map` and `sum`, and builds a JSON object field by field.

```una include="day-to-day/src/report.una#money..totals_json" title="day-to-day/src/report.una" caption="output"
--- Cents as a decimal amount: 13930 is "139.30".
pub money(cents: Int) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"

--- The totals of the day as one JSON object, for the accounting service.
pub totals_json(summaries: List[Summary], skipped: Int) -> Text
=
  let units = summaries.map(each: fn(summary) -> summary.units).sum()
  let cents = summaries.map(each: fn(summary) -> summary.cents).sum()
  let edit fields: Map[Text, Json] = empty_map()
  edit fields.set(key: "categories", value: Number(value: summaries.len))
  edit fields.set(key: "units", value: Number(value: units))
  edit fields.set(key: "cents", value: Number(value: cents))
  edit fields.set(key: "skipped", value: Number(value: skipped))
  Object(fields).to_json()
```

For an amount that is not negative, `cents / 100` is the whole part and `cents mod 100` the cents left over. The `if … then … else` on one line chooses the form with a leading zero.

### Running it

`sample_export` holds the day's export as literals. Each line is appended on its own, since canonical form keeps a list literal on one line. `main` reads it, groups it, and prints the report.

```una include="day-to-day/src/report.una#sample_export..main" title="day-to-day/src/report.una"
--- The day's export: one JSON object per order line.
pub sample_export() -> List[Text]
=
  let edit lines: List[Text] = []
  lines = lines.append(item: "\{\"sku\": \"LAMP-01\", \"category\": \"lighting\", \"quantity\": 2, \"cents\": 1990\}")
  lines = lines.append(item: "\{\"sku\": \"DESK-02\", \"category\": \"furniture\", \"quantity\": 2, \"cents\": 15900\}")
  lines = lines.append(item: "\{\"sku\": \"RUG-07\", \"category\": \"textiles\", \"quantity\": 3, \"cents\": 4500\}")
  lines = lines.append(item: "\{\"sku\": \"LAMP-01\", \"category\": \"lighting\", \"quantity\": 4, \"cents\": 1990\}")
  lines = lines.append(item: "\{\"sku\": \"CHAIR-09\", \"category\": \"furniture\"\}")
  lines = lines.append(item: "\{\"sku\": \"SHADE-05\", \"category\": \"lighting\", \"quantity\": 2, \"cents\": 1250\}")
  lines = lines.append(item: "\{\"sku\": \"VASE-03\", \"quantity\": 2, \"cents\": 2400\}")
  lines = lines.append(item: "\{\"sku\": \"RUG-07\", \"category\": \"textiles\", \"quantity\": 1, \"cents\": 4500\}")
  lines

pub main() -> Unit
  uses @console: Console[print]
=
  let export = sample_export()
  let lines = read_all(export)
  let skipped = export.len - lines.len
  @console.print("{export.len} lines, {skipped} skipped")
  let summaries = by_category(lines).values()
  for summary in summaries
    @console.print("{summary.category}: {summary.units} units, {money(summary.cents)}")
  @console.print(headline(best_seller(units_by_sku(lines))))
  @console.print(totals_json(summaries, skipped: skipped))
```

`una run .` prints the report shown in [What you'll build](#what-youll-build): eight lines, the `CHAIR-09` line skipped for its missing quantity, and the `VASE-03` line counted under "other". `summaries` comes from `values()`, so the categories print in name order. `skipped` is the difference of two lengths, since every line of the export either became a `Line` or was left out.

> [!SECURITY]
> The export here is a literal. A program that reads it from a file gets text labeled `internal`, a label that may not reach the console without a declared policy. Printing a report built from it is a question of information flow, which [chapter 9, Information flow](/learn/information-flow/), answers with a policy.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/report.una" title="day-to-day/src/report.una" caption="the whole program" verified="check, run, test"
module report

--- One line of an order: a SKU, its category, how many units, and the price of one unit in cents.
pub kind Line
  sku: Text
  category: Text
  quantity: Int
  cents: Int

--- What one category sold: its units and its revenue in cents.
pub kind Summary
  category: Text
  units: Int
  cents: Int

--- The text in the field `name` of a JSON object, or `None` when it is missing or not a string.
text_field(fields: Map[Text, Json], name: Text) -> Option[Text]
=
  let found = fields.get(key: name).or_else(default: Null)
  when found
    is Str(value) -> Some(value)
    else -> None

--- The whole number in the field `name` of a JSON object, or `None`.
int_field(fields: Map[Text, Json], name: Text) -> Option[Int]
=
  let found = fields.get(key: name).or_else(default: Null)
  when found
    is Number(value) -> Some(value)
    else -> None

--- An order line from one line of the export, or `None` when the line cannot be read.
--- A line without a category counts under "other".
pub read_line(text: Text) -> Option[Line]
=
  let json = text.parse_json()
    if error use Null
  when json
    is Object(fields) ->
      let category = text_field(fields, name: "category").or_else(default: "other")
      let sku = text_field(fields, name: "sku")
      let quantity = int_field(fields, name: "quantity")
      let cents = int_field(fields, name: "cents")
      when sku
        is None -> None
        is Some(code) ->
          when quantity
            is None -> None
            is Some(units) ->
              when cents
                is None -> None
                is Some(price) -> Some(Line(sku: code, category: category, quantity: units, cents: price))
    else -> None

--- The lines that could be read, in the order of the export.
pub read_all(export: List[Text]) -> List[Line]
=
  let edit lines: List[Line] = []
  for text in export
    let found = read_line(text)
    when found
      is Some(line) ->
        lines = lines.append(item: line)
      is None -> unit
  lines

--- The units and revenue of each category, ordered by category.
pub by_category(lines: List[Line]) -> Map[Text, Summary]
=
  let edit totals: Map[Text, Summary] = empty_map()
  for line in lines
    let empty = Summary(category: line.category, units: 0, cents: 0)
    let before = totals.get(key: line.category).or_else(default: empty)
    let units = before.units + line.quantity
    let cents = before.cents + line.quantity * line.cents
    edit totals.set(key: line.category, value: Summary(category: line.category, units: units, cents: cents))
  totals

--- The units sold of each SKU.
pub units_by_sku(lines: List[Line]) -> Map[Text, Int]
=
  let edit units: Map[Text, Int] = empty_map()
  for line in lines
    let before = units.get(key: line.sku).or_else(default: 0)
    edit units.set(key: line.sku, value: before + line.quantity)
  units

--- The SKU that sold the most units, the first in SKU order on a tie; `None` for no sales.
pub best_seller(units: Map[Text, Int]) -> Option[Entry[Text, Int]]
=
  let most = units.values().fold(initial: 0, step: fn(top, n) -> max(top, b: n))
  units.entries().first_where(keep: fn(entry) -> entry.value == most)

--- The report's line about the best seller.
pub headline(best: Option[Entry[Text, Int]]) -> Text
=
  when best
    is Some(entry) -> "best seller: {entry.key}, {entry.value} units"
    is None -> "no sales"

--- Cents as a decimal amount: 13930 is "139.30".
pub money(cents: Int) -> Text
=
  let rest = cents mod 100
  if rest < 10 then "{cents / 100}.0{rest}" else "{cents / 100}.{rest}"

--- The totals of the day as one JSON object, for the accounting service.
pub totals_json(summaries: List[Summary], skipped: Int) -> Text
=
  let units = summaries.map(each: fn(summary) -> summary.units).sum()
  let cents = summaries.map(each: fn(summary) -> summary.cents).sum()
  let edit fields: Map[Text, Json] = empty_map()
  edit fields.set(key: "categories", value: Number(value: summaries.len))
  edit fields.set(key: "units", value: Number(value: units))
  edit fields.set(key: "cents", value: Number(value: cents))
  edit fields.set(key: "skipped", value: Number(value: skipped))
  Object(fields).to_json()

--- The day's export: one JSON object per order line.
pub sample_export() -> List[Text]
=
  let edit lines: List[Text] = []
  lines = lines.append(item: "\{\"sku\": \"LAMP-01\", \"category\": \"lighting\", \"quantity\": 2, \"cents\": 1990\}")
  lines = lines.append(item: "\{\"sku\": \"DESK-02\", \"category\": \"furniture\", \"quantity\": 2, \"cents\": 15900\}")
  lines = lines.append(item: "\{\"sku\": \"RUG-07\", \"category\": \"textiles\", \"quantity\": 3, \"cents\": 4500\}")
  lines = lines.append(item: "\{\"sku\": \"LAMP-01\", \"category\": \"lighting\", \"quantity\": 4, \"cents\": 1990\}")
  lines = lines.append(item: "\{\"sku\": \"CHAIR-09\", \"category\": \"furniture\"\}")
  lines = lines.append(item: "\{\"sku\": \"SHADE-05\", \"category\": \"lighting\", \"quantity\": 2, \"cents\": 1250\}")
  lines = lines.append(item: "\{\"sku\": \"VASE-03\", \"quantity\": 2, \"cents\": 2400\}")
  lines = lines.append(item: "\{\"sku\": \"RUG-07\", \"category\": \"textiles\", \"quantity\": 1, \"cents\": 4500\}")
  lines

pub main() -> Unit
  uses @console: Console[print]
=
  let export = sample_export()
  let lines = read_all(export)
  let skipped = export.len - lines.len
  @console.print("{export.len} lines, {skipped} skipped")
  let summaries = by_category(lines).values()
  for summary in summaries
    @console.print("{summary.category}: {summary.units} units, {money(summary.cents)}")
  @console.print(headline(best_seller(units_by_sku(lines))))
  @console.print(totals_json(summaries, skipped: skipped))

example "a line with every field is read"
  do read_line("\{\"sku\": \"LAMP-01\", \"category\": \"lighting\", \"quantity\": 2, \"cents\": 1990\}")
  expect result == Some(Line(sku: "LAMP-01", category: "lighting", quantity: 2, cents: 1990))

example "a line without a category counts under other"
  do read_line("\{\"sku\": \"VASE-03\", \"quantity\": 2, \"cents\": 2400\}")
  expect result == Some(Line(sku: "VASE-03", category: "other", quantity: 2, cents: 2400))

example "a line without a quantity is skipped"
  do read_line("\{\"sku\": \"CHAIR-09\", \"category\": \"furniture\"\}")
  expect result == None

example "a line that is not JSON is skipped"
  do read_line("LAMP-01, 2")
  expect result == None

example "two lines of one category add up"
  do by_category([Line(sku: "LAMP-01", category: "lighting", quantity: 2, cents: 1990), Line(sku: "SHADE-05", category: "lighting", quantity: 1, cents: 1250)])
  expect result.get(key: "lighting") == Some(Summary(category: "lighting", units: 3, cents: 5230))

example "on a tie, the first SKU in order is the best seller"
  do best_seller(empty_map().with(key: "RUG-07", value: 3).with(key: "LAMP-01", value: 3))
  expect result == Some(Entry(key: "LAMP-01", value: 3))

example "a day without sales has no best seller"
  do headline(best_seller(empty_map()))
  expect result == "no sales"

example "amounts keep two digits of cents"
  do money(1205)
  expect result == "12.05"
```

## 5.8 Testing it

### One example per path

Each path through the program gets an example: a complete line, a line that uses the default category, a line without a quantity, a line that is not JSON, two lines of one category, a tie for the best seller, a day without sales, and an amount with a leading zero in its cents. An example calls one function with a `do` line and checks the result with an `expect` line, so each one names the case it covers.

> [!TIP]
> An `example` is a test that lives next to the code. `do` calls the code under test, `result` is what that call returned, and each `expect` line states something that must hold. `una test .` runs every example and reports each one. [Chapter 10, Testing](/learn/testing/), covers examples in full.

```una include="day-to-day/src/report.una#L146-L176" title="day-to-day/src/report.una" caption="the examples"
example "a line with every field is read"
  do read_line("\{\"sku\": \"LAMP-01\", \"category\": \"lighting\", \"quantity\": 2, \"cents\": 1990\}")
  expect result == Some(Line(sku: "LAMP-01", category: "lighting", quantity: 2, cents: 1990))

example "a line without a category counts under other"
  do read_line("\{\"sku\": \"VASE-03\", \"quantity\": 2, \"cents\": 2400\}")
  expect result == Some(Line(sku: "VASE-03", category: "other", quantity: 2, cents: 2400))

example "a line without a quantity is skipped"
  do read_line("\{\"sku\": \"CHAIR-09\", \"category\": \"furniture\"\}")
  expect result == None

example "a line that is not JSON is skipped"
  do read_line("LAMP-01, 2")
  expect result == None

example "two lines of one category add up"
  do by_category([Line(sku: "LAMP-01", category: "lighting", quantity: 2, cents: 1990), Line(sku: "SHADE-05", category: "lighting", quantity: 1, cents: 1250)])
  expect result.get(key: "lighting") == Some(Summary(category: "lighting", units: 3, cents: 5230))

example "on a tie, the first SKU in order is the best seller"
  do best_seller(empty_map().with(key: "RUG-07", value: 3).with(key: "LAMP-01", value: 3))
  expect result == Some(Entry(key: "LAMP-01", value: 3))

example "a day without sales has no best seller"
  do headline(best_seller(empty_map()))
  expect result == "no sales"

example "amounts keep two digits of cents"
  do money(1205)
  expect result == "12.05"
```

### Ties and empty days

Two of them pin down what the output alone would hide. "on a tie, the first SKU in order is the best seller" builds the map with `RUG-07` first and expects `LAMP-01`, so it proves that the result follows the key order and not the order of insertion. "a day without sales has no best seller" checks the `None` arm of `headline`, a path the sample export never reaches.

### Pure functions, whole values

The examples need no fakes. Every function they call is pure, with no `uses` line, so an example only gives it values and checks what comes back. The examples compare whole values with `==`: an `Option` of a record, a list, a map lookup. Lists, maps, records and `Option`s are values, so `==` compares what they hold, element by element and field by field.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L11"
example report "a line with every field is read" ... ok
example report "a line without a category counts under other" ... ok
example report "a line without a quantity is skipped" ... ok
example report "a line that is not JSON is skipped" ... ok
example report "two lines of one category add up" ... ok
example report "on a tie, the first SKU in order is the best seller" ... ok
example report "a day without sales has no best seller" ... ok
example report "amounts keep two digits of cents" ... ok

8 examples: 8 passed, 0 failed
```

## 5.9 Common mistakes

Each mistake below is a small change to `day-to-day/src/report.una`, followed by what `una check .` reports.

### Indexing with brackets (U0101)

:::mistake
Read the first line of the export as `export[0]`:

```diff include="day-to-day..mistakes/1:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -137,2 +137,3 @@
   let lines = read_all(export)
+  let first = export[0]
   let skipped = export.len - lines.len
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U0101] Error: unexpected `[`, expected end of line
```

*Why:* Una has no index syntax. Reading a position can find nothing, so it is a function that returns an `Option`.

*Fix:* `export.at(index: 0)` or `export.first()`, then `when` or `or_else`.
:::

### Updating a plain `let` (U2019)

:::mistake
Declare the result of `read_all` with `let` instead of `let edit`:

```diff include="day-to-day..mistakes/2:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -57,3 +57,3 @@
 =
-  let edit lines: List[Line] = []
+  let lines: List[Line] = []
   for text in export
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U2019] Error: `lines` is not editable; declare it `let edit lines`, or the parameter `edit lines`
```

*Why:* only a binding declared `let edit` can take a new value.

*Fix:* `let edit lines: List[Line] = []`, as the message says.
:::

### Using an `Option` as its value (U2001)

:::mistake
Leave out the default when reading the units so far:

```diff include="day-to-day..mistakes/3:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -83,3 +83,3 @@
   for line in lines
-    let before = units.get(key: line.sku).or_else(default: 0)
+    let before = units.get(key: line.sku)
     edit units.set(key: line.sku, value: before + line.quantity)
```

```text include="mistakes/3/expected/rendered.txt#L1"
[U2001] Error: an operand of `+` must be `Int`, found `Option[Int]`
```

*Why:* `get` returns `Option[Int]`, and `+` needs an `Int`. The checker does not guess what a missing SKU means.

*Fix:* `or_else(default: 0)`, or a `when` when the absence needs its own handling.
:::

### A `when` that forgets `None` (U2007)

:::mistake
Remove the `is None` arm of `headline`:

```diff include="day-to-day..mistakes/4:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -98,3 +98,2 @@
     is Some(entry) -> "best seller: {entry.key}, {entry.value} units"
-    is None -> "no sales"
 
```

```text include="mistakes/4/expected/rendered.txt#L1,L8"
[U2007] Error: `when` does not match variant `None` of `Option`
    │ Help: repair 1: add an arm for each missing variant, such as `is None`, or an `else` arm
```

*Why:* a `when` must cover every variant, and `None` is the day without sales.

*Fix:* add the arm, `is None -> "no sales"`.
:::

### Sorting records (U2025)

:::mistake
Sort the lines as they are read:

```diff include="day-to-day..mistakes/5:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -136,3 +136,3 @@
   let export = sample_export()
-  let lines = read_all(export)
+  let lines = read_all(export).sort()
   let skipped = export.len - lines.len
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U2025] Error: `sort` needs its type parameter `T` to satisfy `Ord`, and `Line` does not
```

*Why:* `sort` needs an order, and a record has none: should lines sort by SKU, by category, by price?

*Fix:* sort something that has an order, such as `lines.map(each: fn(line) -> line.sku).sort()`, or group into a map keyed by what you want to sort by, as [exercise 3](#exercise-3-categories-by-revenue) does.
:::

### Calling `set` without `edit` (U2020)

:::mistake
Write the update in `units_by_sku` as a plain call:

```diff include="day-to-day..mistakes/6:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -84,3 +84,3 @@
     let before = units.get(key: line.sku).or_else(default: 0)
-    edit units.set(key: line.sku, value: before + line.quantity)
+    units.set(key: line.sku, value: before + line.quantity)
   units
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U2020] Error: `set` updates the map, so the call is written `edit units.set(...)`
```

*Why:* `set` changes the map, and every change is marked where it happens.

*Fix:* `edit units.set(...)`, as the message says.
:::

### Parsing JSON without a clause (U3007)

:::mistake
Remove `if error use Null` from `read_line`:

```diff include="day-to-day..mistakes/7:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -36,3 +36,2 @@
   let json = text.parse_json()
-    if error use Null
   when json
```

```text include="mistakes/7/expected/rendered.txt#L1"
[U3007] Error: `parse_json` can fail with `JsonError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
```

*Why:* `parse_json` can fail with `JsonError`, and a failure is handled on the line under the call.

*Fix:* add a clause. [Chapter 6](/learn/failure/) shows all of them.
:::

### A brace in JSON text (U0007)

:::mistake
Write a JSON object in a text literal without escaping its braces:

```diff include="day-to-day..mistakes/8:src/report.una" context="0"
--- a/src/report.una
+++ b/src/report.una
@@ -129 +129 @@
-  lines = lines.append(item: "\{\"sku\": \"VASE-03\", \"quantity\": 2, \"cents\": 2400\}")
+  lines = lines.append(item: "{\"sku\": \"VASE-03\", \"quantity\": 2, \"cents\": 2400}")
```

```text include="mistakes/8/expected/rendered.txt#L1,L8"
[U0007] Error: unescaped `{` in text, where no interpolation can start; write `\{`
     │ Help: repair 1: write `\{`; edit src/report.una:129:31..129:32 to "\\{"
```

*Why:* in a text, `{` starts an interpolation.

*Fix:* `una fix .` writes `\{` and `\}` for you.
:::

## 5.10 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with a stub of the function to write, whose body is `[]`, and the exercise's example. `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

### Exercise 1: the SKUs of a category

::::exercise
Write `skus_in(lines, category)`, the SKUs sold in one category, each once, in SKU order. The start package ends with:

```una include="exercises/1/start/src/report.una#L178-L187" title="exercises/1/start/src/report.una"
--- The SKUs sold in `category`, each once, in SKU order.
pub skus_in(lines: List[Line], category: Text) -> List[Text] = []

example "each SKU of a category appears once"
  do skus_in(read_all(sample_export()), category: "lighting")
  expect result == ["LAMP-01", "SHADE-05"]

example "a category that sold nothing has no SKUs"
  do skus_in(read_all(sample_export()), category: "garden")
  expect result == []
```

:::hint
*Hint:* a map holds each key once and lists its keys in order. The program already has a function that builds a map keyed by SKU.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L10-L15"
example report "each SKU of a category appears once" ... FAILED
  src/report.una:183: expect result == ["LAMP-01", "SHADE-05"]
  it is false, with `result` = `[]`
example report "a category that sold nothing has no SKUs" ... ok

10 examples: 9 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Give `skus_in` its body:

```diff include="exercises/1/start..exercises/1/answer:src/report.una" context="1" title="src/report.una"
--- a/src/report.una
+++ b/src/report.una
@@ -178,3 +178,6 @@
 --- The SKUs sold in `category`, each once, in SKU order.
-pub skus_in(lines: List[Line], category: Text) -> List[Text] = []
+pub skus_in(lines: List[Line], category: Text) -> List[Text]
+=
+  let matching = lines.filter(keep: fn(line) -> line.category == category)
+  units_by_sku(matching).keys()
 
```

`filter` keeps the lines of the category, and `units_by_sku(matching).keys()` gives their SKUs once each, in order.
:::
::::

### Exercise 2: say which lines were skipped

::::exercise
The report says how many lines it skipped. Write `skipped_lines(export)`, the numbers of those lines in the export, counting from 1, and print them on the first line of the report: `8 lines, 1 skipped: [5]`. The start package ends with:

```una include="exercises/2/start/src/report.una#L178-L183" title="exercises/2/start/src/report.una"
--- The numbers of the lines that could not be read, counting from 1.
pub skipped_lines(export: List[Text]) -> List[Int] = []

example "the skipped lines are numbered from 1"
  do skipped_lines(["LAMP-01", "\{\"sku\": \"RUG-07\", \"quantity\": 1, \"cents\": 4500\}", "\{\}"])
  expect result == [1, 3]
```

:::hint
*Hint:* a `for` loop over the export with two `let edit` bindings, one counting the lines and one collecting the numbers. `found is None` is a condition.
:::

Check your answer with `una test .`, then `una run .` for the new first line.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Give `skipped_lines` its body, and print its result in `main`:

```diff include="exercises/2/start..exercises/2/answer:src/report.una" context="1" title="src/report.una"
--- a/src/report.una
+++ b/src/report.una
@@ -138,3 +138,3 @@
   let skipped = export.len - lines.len
-  @console.print("{export.len} lines, {skipped} skipped")
+  @console.print("{export.len} lines, {skipped} skipped: {skipped_lines(export)}")
   let summaries = by_category(lines).values()
@@ -178,3 +178,12 @@
 --- The numbers of the lines that could not be read, counting from 1.
-pub skipped_lines(export: List[Text]) -> List[Int] = []
+pub skipped_lines(export: List[Text]) -> List[Int]
+=
+  let edit numbers: List[Int] = []
+  let edit number = 0
+  for text in export
+    number = number + 1
+    let found = read_line(text)
+    if found is None
+      numbers = numbers.append(item: number)
+  numbers
 
```

The example covers a line that is not JSON and an object without a SKU, around a line that is read.
:::
::::

### Exercise 3: categories by revenue

::::exercise
Write `ranked(summaries)`, the categories from the highest revenue to the lowest, and print them after the category lines: `by revenue: furniture, textiles, lighting, other`. When two categories have the same revenue, they keep the order of `summaries`. The start package ends with:

```una include="exercises/3/start/src/report.una#L178-L184" title="exercises/3/start/src/report.una"
--- The categories, the highest revenue first. On a tie they keep the order of `summaries`,
--- which is name order when they come from `by_category`.
pub ranked(summaries: List[Summary]) -> List[Text] = []

example "categories with the same revenue keep the order of the summaries"
  do ranked([Summary(category: "lighting", units: 1, cents: 500), Summary(category: "garden", units: 2, cents: 900), Summary(category: "textiles", units: 5, cents: 500)])
  expect result == ["garden", "lighting", "textiles"]
```

:::hint
*Hint:* `sort` cannot sort a `Summary`, and the prelude has no `sort_by`, `reverse` or `concat`. A map lists its keys in ascending order: key a map by the revenue with its sign changed, and keep a list of names for each key, since two categories can have the same revenue.
:::

Check your answer with `una test .`, then `una run .` for the new line.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Give `ranked` its body, and print its result in `main`:

```diff include="exercises/3/start..exercises/3/answer:src/report.una" context="1" title="src/report.una"
--- a/src/report.una
+++ b/src/report.una
@@ -142,2 +142,4 @@
     @console.print("{summary.category}: {summary.units} units, {money(summary.cents)}")
+  let order = ranked(summaries).join(separator: ", ")
+  @console.print("by revenue: {order}")
   @console.print(headline(best_seller(units_by_sku(lines))))
@@ -179,3 +181,14 @@
 --- which is name order when they come from `by_category`.
-pub ranked(summaries: List[Summary]) -> List[Text] = []
+pub ranked(summaries: List[Summary]) -> List[Text]
+=
+  let edit by_revenue: Map[Int, List[Text]] = empty_map()
+  for summary in summaries
+    let key = -summary.cents
+    let before = by_revenue.get(key: key).or_else(default: [])
+    edit by_revenue.set(key: key, value: before.append(item: summary.category))
+  let edit names: List[Text] = []
+  for group in by_revenue.values()
+    for name in group
+      names = names.append(item: name)
+  names
 
```

`-summary.cents` turns the largest revenue into the smallest key, so it comes first. `main` joins the names with `let` before printing them, since a text literal such as `", "` cannot appear inside an interpolation. Names with the same key are appended in the order of `summaries`, which `by_category` gives in name order, and the example with two categories at 500 cents checks it.
:::
::::

## 5.11 Recap and reference

### For agents

:::agents
Every diagnostic of [Common mistakes](#s5-9) is available as JSON with `una --json check .`. For [a `when` that forgets `None`](#a-when-that-forgets-none-u2007):

```json include="mistakes/4/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U2007","severity":"error","domain":"types","message":"`when` does not match variant `None` of `Option`","primary":{"file":"src/report.una","start":{"line":97,"col":3},"end":{"line":97,"col":7}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"add an arm for each missing variant, such as `is None`, or an `else` arm","edit":null}],"explain":"una explain U2007"}],"fixable":0}
```

The repair of U2007 has a description and no `edit`, because the right arm depends on what the absence means. The U0007 of [a brace in JSON text](#a-brace-in-json-text-u0007) carries exact edits, which `una fix .` applies. The compact rule: *a value from `first`, `at`, `get`, `first_where` or `to_int` is an `Option`, used through `when` with both arms or `or_else`; a binding that changes is `let edit`, and a call that updates a map is written `edit m.set(...)`.*
:::

### Recap

:::recap
- A list holds values of one type in order, and `append` returns a new list. Read a position with `at` or `first`.
- A binding that changes is `let edit`, and a loop updates it with assignments. A plain `let` names one value.
- `first`, `at`, `get`, `first_where` and `to_int` return an `Option`. Use it through a `when` with both arms, or `or_else` when a default is right.
- Use `map`, `filter`, `fold` and `first_where` when each step is one expression, and `for` when it needs several lines.
- Group with a map: read the total so far with `get` and `or_else`, then write it with `edit m.set(...)`.
- A map lists its keys in order, so output built from it is sorted. Its keys need an order, and records have none.
- Parsed JSON is a `Json`: read it with `when` and `get`, write it with `to_json`, and keep money in whole cents.
:::

### Reference

:::reference
- Construct pages: [`for`](/docs/language/control-flow/for/), [`let edit` and `edit` parameters](/docs/language/control-flow/let-edit/), [`when`](/docs/language/control-flow/when/), [`example`](/docs/language/examples/example/), [`if error` and `if none`](/docs/language/errors/if-error/)
- Standard library: [the prelude](/docs/std/) (`List`, `Option`, `append`, `at`, `first`, `first_where`, `contains`, `sum`, `sort`, `map`, `filter`, `fold`, `or_else`, `is_some`, `to_int`), [maps](/docs/std/maps/) (`Map`, `Entry`, `empty_map`), [text](/docs/std/text/) (`join`), [JSON](/docs/std/json/) (`Json`, `JsonError`, `parse_json`, `to_json`)
- Diagnostics: [U0007](/docs/errors/U0007/), [U0101](/docs/errors/U0101/), [U2001](/docs/errors/U2001/), [U2007](/docs/errors/U2007/), [U2019](/docs/errors/U2019/), [U2020](/docs/errors/U2020/), [U2025](/docs/errors/U2025/), [U3007](/docs/errors/U3007/)
- Specification: [the standard library](/docs/spec/14-standard-library/), [the memory model](/docs/spec/17-memory-model/), [constraints on generics](/docs/spec/20-constraints-on-generics/), [maps](/docs/spec/21-maps/), [text](/docs/spec/22-text/), [JSON](/docs/spec/23-json/)
:::
