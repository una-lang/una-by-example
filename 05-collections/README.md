---
learn: "5"
title: Collections
editions: ["0.2"]
codes: [U0007, U0101, U0103, U1001, U2001, U2007, U2019, U2020, U2025, U3007]
time: 55
builds: A daily sales report that reads order lines from JSON, groups them by category and sums them up
prerequisites: ["2", "3", "4"]
template: 2
nav: ["Lists", "for and let edit", "Option", "map, filter and fold", "Maps", "JSON", "Day-to-day: a daily sales report", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
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

### What a list is

A **list** is one value that holds several values of the same type, one after another. Think of the lines of a receipt: there may be one line or forty, they come in a fixed order, and each line is the same sort of thing. A list works the same way. The values it holds are its **elements**, and each element has a **position**, its place in the order.

A few words name the parts, and the rest of this chapter uses them:

- A **list literal** writes a list's elements between brackets, separated by commas: `[2, 1, 3]`. A literal is a value written out in the code, as `3` or `"LAMP-01"` is ([chapter 2](/learn/values/)).
- The **type** of a list names the type of its elements: `List[Int]` is a list of whole numbers, and `List[Text]` a list of texts. `List` is a **generic** type: it takes another type between brackets, as `Option` does in [chapter 4](/learn/kinds/#s4-4).
- A **position**, also called an **index**, counts from 0. In `[2, 1, 3]`, the element at position 0 is 2, and the element at position 2 is 3.
- The **length** of a list is how many elements it holds. `[2, 1, 3]` has a length of 3, and `[]`, the **empty list**, a length of 0.

The **prelude** is the set of functions and types that every module has without importing anything. It gives lists most of what a program needs: adding an element, adding up, sorting, searching. You call these functions with method syntax ([chapter 3](/learn/functions/#s3-1)): `more.sum()` is the call `sum(more)`.

### Why a program needs lists

Without a list, every value needs a name of its own. A cart of three lines needs three names, and a function that totals a cart needs three parameters. Here is such a function, from [section 5.2](#s5-2):

```una include="steps/04-no-loop/src/receipt.una#total_of_three" title="steps/04-no-loop/src/receipt.una"
--- What a cart of exactly three lines costs, in cents. A cart of two lines, or of four, does
--- not fit this function.
total_of_three(one: CartLine, two: CartLine, three: CartLine) -> Int = one.quantity * one.cents + two.quantity * two.cents + three.quantity * three.cents
```

It prices a cart of exactly three lines. A real cart may hold any number of lines, and the program learns that number only when it runs. A list solves that: `List[CartLine]` is one type for a cart of any size, so one name and one parameter hold the whole cart, and the functions of this chapter work on it whatever its length.

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

Every package of this chapter uses edition `0.2`, the edition in which maps, `sort` and JSON are part of the prelude; in a package of edition `0.1` they do not exist. `verification.lock` pins the solver and is the same in every example: copy it from chapter 1, or take the step's package, whole, from the chapter's download, `05-collections.tar.gz`. Then, in the package's directory:

```sh
una check .
una run .
```

### A cart and its receipt

Start with the quantities of a cart, then the SKUs on its receipt. A SKU, a stock-keeping unit, is the code a store gives each product, such as `LAMP-01`.

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

1. **`[2, 1, 3]`.** A list literal. Every element has the same type, here `Int`, so the list is a `List[Int]`.
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

A list in an interpolation is written as you would type it in Una, with brackets, and with quotes around texts.

### How to write and use a list

The next step shows each form of a list, and each thing the prelude does with one. Its `main` prints one line per form:

```una include="steps/02-list-forms/src/shelf.una#Size..recount" title="steps/02-list-forms/src/shelf.una"
--- The size of a T-shirt. Its variants carry no data, so they have an order: the order of
--- their declaration.
kind Size = Small | Medium | Large

--- The counts on a shelf, after a recount of the shelf at `position`.
recount(counts: List[Int], position: Int, counted: Int) -> List[Int]
  requires 0 <= position and position < counts.len
=
  let edit fixed = counts
  edit fixed.set(index: position, item: counted)
  fixed
```

#### Literals: empty, of values, of variants, of lists

```una include="steps/02-list-forms/src/shelf.una#L18-L22" title="steps/02-list-forms/src/shelf.una"
  let empty: List[Text] = []
  let counts = [4, 0, 7]
  let sizes = [Large, Small, Medium]
  let aisles = [[1, 2], [3]]
  @console.print("{empty.len} {counts.len} {sizes.len} {aisles.len}")
```

```text include="steps/02-list-forms/expected/output.txt#L1"
0 3 3 2
```

- `[]` is the empty list. It has no element to take a type from, so you write the type on the binding: `let empty: List[Text] = []`.
- `[4, 0, 7]` is a `List[Int]`, and its type comes from its elements.
- `[Large, Small, Medium]` holds variants of the kind `Size`, so it is a `List[Size]`.
- `[[1, 2], [3]]` is a list whose elements are lists: a `List[List[Int]]`, here two aisles with their shelf numbers.

Canonical form keeps a list literal on one line, however long it is.

#### Length and emptiness: `len` and `is_empty`

```una include="steps/02-list-forms/src/shelf.una#L23" title="steps/02-list-forms/src/shelf.una"
  @console.print("{empty.is_empty()} {counts.is_empty()}")
```

```text include="steps/02-list-forms/expected/output.txt#L2"
true false
```

`is_empty()` is `true` exactly when `len` is 0.

#### Reading an element: `first` and `at`

```una include="steps/02-list-forms/src/shelf.una#L24" title="steps/02-list-forms/src/shelf.una"
  @console.print("{counts.first()} {counts.at(index: 2)} {counts.at(index: 3)} {empty.first()}")
```

```text include="steps/02-list-forms/expected/output.txt#L3"
Some(4) Some(7) None None
```

`counts.first()` reads position 0, and `counts.at(index: 2)` reads position 2. Una has no `counts[2]` syntax. Both return an `Option`: `Some` with the element, or `None` when there is no element there, as for position 3 of a list of three, or the first element of an empty list. [Section 5.3](#s5-3) shows how to use what they return.

#### Searching and adding up: `contains`, `sum` and `join`

```una include="steps/02-list-forms/src/shelf.una#L25-L26" title="steps/02-list-forms/src/shelf.una"
  let receipt = empty.join(separator: ", ")
  @console.print("{counts.contains(item: 0)} {counts.sum()} '{receipt}'")
```

```text include="steps/02-list-forms/expected/output.txt#L4"
true 11 ''
```

`contains(item: 0)` is `true` when some element equals 0. `sum()` adds up a list of numbers, and gives 0 for an empty list. `join` puts a list of texts together, with the separator between each two; an empty list gives the empty text, which the quotes make visible.

#### Sorting: `sort`

```una include="steps/02-list-forms/src/shelf.una#L27" title="steps/02-list-forms/src/shelf.una"
  @console.print("{counts.sort()} {sizes.sort()}")
```

```text include="steps/02-list-forms/expected/output.txt#L5"
[0, 4, 7] [Small, Medium, Large]
```

`sort` returns a new list in ascending order. It works on any type with an order: `Int`, `Text`, the fixed-width integers of [chapter 2](/learn/values/#s2-5), and kinds whose variants carry no data, in the order the variants are declared, which is why `Small` comes before `Large`. It is **stable**: elements that are equal keep the order they had. A record such as an order line has no order of its own, and [Sorting records](#sorting-records-u2025) shows what the checker says when you try.

#### Adding and replacing: `append` and `set`

`append` returns a new list with one more element, as the first step showed. To replace the element at a position, `set` changes a list in place:

```una include="steps/02-list-forms/src/shelf.una#L28" title="steps/02-list-forms/src/shelf.una"
  @console.print("{recount(counts, position: 1, counted: 5)} {counts}")
```

```text include="steps/02-list-forms/expected/output.txt#L6"
[4, 5, 7] [4, 0, 7]
```

`recount` copies its parameter into `let edit fixed`, a binding it may change, and then writes `edit fixed.set(index: position, item: counted)`. The word `edit` before the call marks the place where `fixed` changes, as every change in Una is marked. `set` has a **precondition**, a condition every call must meet: `0 <= index and index < xs.len`, a position that exists. Una proves it before the program runs, so `recount` states the same condition in a `requires` line under its header, and every caller of `recount` must show it in turn ([chapter 3](/learn/functions/#s3-2) introduces `requires`, and [chapter 7](/learn/contracts/#s7-1) covers it). The caller's `counts` keeps its values: the copy changed, not the original.

#### Comparing lists: `==`

```una include="steps/02-list-forms/src/shelf.una#L29" title="steps/02-list-forms/src/shelf.una"
  @console.print("{counts == [4, 0, 7]} {counts == [0, 4, 7]}")
```

```text include="steps/02-list-forms/expected/output.txt#L7"
true false
```

Two lists are equal when they hold equal elements in the same order. The same elements in another order make a different list.

### How a list behaves

#### Every element has the list's type

A list holds values of one type. Write a count as a word in the middle of a list of numbers:

```diff include="steps/02-list-forms..steps/03-mixed-list:src/shelf.una" context="1" title="src/shelf.una"
--- a/src/shelf.una
+++ b/src/shelf.una
@@ -18,3 +18,3 @@
   let empty: List[Text] = []
-  let counts = [4, 0, 7]
+  let counts = [4, "zero", 7]
   let sizes = [Large, Small, Medium]
```

`una check .` reports:

```text include="steps/03-mixed-list/expected/rendered.txt"
[U2001] Error: expected `Int`, found `Text`
    ╭─[ src/shelf.una:19:20 ]
    │
 19 │   let counts = [4, "zero", 7]
    │                    ───┬──
    │                       ╰──── expected `Int`, found `Text`
    │
    │ Note: run `una explain U2001` for an explanation
────╯
```

The first line names the problem: an element was expected to be an `Int`, and a `Text` was found. The mark points at `"zero"`, the element that does not fit; the list took its type, `Int`, from its first element. To keep values of several shapes in one list, declare a sum kind with one variant for each shape ([chapter 4](/learn/kinds/#s4-2)), and make the list a list of that kind.

#### A list is a value

A list never changes behind your back. `append` and `sort` return new lists, and the list you called them on keeps its elements. A function that receives a list cannot change the caller's list: `recount` changed its own copy. A binding changes only where the code says so, with `let edit` and an assignment, or with `edit` before a call.

#### Positions and absence

Positions count from 0, so the last element of a list of length n is at position n − 1. Reading a position never stops the program: `at` gives `None` for a position that is negative or past the end. That is why it returns an `Option`.

#### Appending without copying

> [!NOTE]
> A list is a value, but `append` does not copy the whole list each time. When nothing else holds the list, it is updated in place, so a loop that appends one element at a time takes time in proportion to the number of elements.

### Check yourself: lists

Read the two lines, and predict what they print before you open the answer:

```una include="steps/02-list-forms/src/shelf.una#L30-L31" title="steps/02-list-forms/src/shelf.una"
  let shelf = [3, 1, 2]
  @console.print("{shelf.append(item: 1).sort()} {shelf.len}")
```

:::answer Show the answer
```text include="steps/02-list-forms/expected/output.txt#L8"
[1, 1, 2, 3] 3
```

`append` returns a new list, `[3, 1, 2, 1]`, and `sort` puts it in order; the two equal 1s both stay. `shelf` itself still has 3 elements, since `append` never changes the list it is called on.
:::

## 5.2 Loops: `for` and `let edit`

### What a loop is

A **loop** repeats the same steps once for each item of a group. Think of a cashier at a till. The basket holds some items, and the cashier does the same thing with each one: scan it, and add its price to the total. Nobody writes down separate instructions for the first item, the second and the third. The instruction is "for each item in the basket, scan it and add its price", and it works for a basket of one item or of fifty.

In Una you write that instruction with `for`. A few words name its parts, and the rest of this section uses them:

- The **body** is the indented block of lines under the `for` line: the steps to repeat.
- A **turn** is one run of the body, for one item. A list of three elements gives three turns. (Other books call a turn an *iteration*.)
- The **loop variable** is the name the body uses for the current item. You choose it, and at each turn it holds the next element.
- What the loop **walks** is the group it takes the items from: a list ([section 5.1](#s5-1)), or a range of whole numbers.

### Why programs repeat work

Without a loop, a program can only do work it can count in advance. Here is a function that prices a cart without one:

```una include="steps/04-no-loop/src/receipt.una" title="steps/04-no-loop/src/receipt.una" verified="check, run"
module receipt

--- One line of a cart: a SKU, how many units, and the price of one unit in cents.
kind CartLine
  sku: Text
  quantity: Int
  cents: Int

--- What a cart of exactly three lines costs, in cents. A cart of two lines, or of four, does
--- not fit this function.
total_of_three(one: CartLine, two: CartLine, three: CartLine) -> Int = one.quantity * one.cents + two.quantity * two.cents + three.quantity * three.cents

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = CartLine(sku: "LAMP-01", quantity: 2, cents: 1990)
  let rug = CartLine(sku: "RUG-07", quantity: 1, cents: 4500)
  let desk = CartLine(sku: "DESK-02", quantity: 1, cents: 15900)
  @console.print("total: {total_of_three(lamp, two: rug, three: desk)} cents")
```

`una run .` prints:

```text include="steps/04-no-loop/expected/output.txt"
total: 24380 cents
```

The answer is right, but the function is fragile in three ways:

1. **It fits one size.** It prices a cart of exactly three lines. A cart of two lines has nothing to pass as `three`, and a cart of four lines has nowhere to put the fourth. A real cart can hold any number of lines, and the program learns that number only when it runs.
2. **It repeats itself.** The rule "quantity times price" is written three times. To change the rule, say to add a fee per line, you must change three places, and forgetting one is an easy mistake.
3. **It grows with the data.** A function for ten lines would need ten parameters and a line of code longer than the screen.

A loop solves all three. You state the rule once, and the loop applies it to every line the cart holds, however many there are, including none.

### How to write a `for` loop

Here is the same total with a loop. It takes a `List[CartLine]`, so it prices a cart of any size:

:::steps
```una include="steps/05-for/src/totals.una#total" title="steps/05-for/src/totals.una"
--- What a cart costs, in cents.
total(lines: List[CartLine]) -> Int
=
  let edit sum = 0
  for line in lines
    sum = sum + line.quantity * line.cents
  sum
```

1. **`let edit sum = 0`.** Before the loop, a binding that will hold the running total. A **binding** is a name for a value ([chapter 2](/learn/values/#s2-4)). A plain `let` names one value for good; `let edit` makes a binding you may give new values. A binding that a loop builds up turn by turn is often called an **accumulator**. It starts at the answer for an empty cart: 0.
2. **`for`.** The keyword that starts a loop: a word with a fixed meaning in the language ([chapter 1](/learn/hello/#s1-3)), which cannot name a binding.
3. **`line`.** The loop variable. You choose the name; a good name says what one item is.
4. **`in lines`.** What the loop walks: here the parameter `lines`, a list.
5. **The indented line.** The body, indented two spaces under `for`. It runs once for each element, with `line` holding that element.
6. **`sum = sum + line.quantity * line.cents`.** An **assignment**: it gives `sum` a new value, computed from its old one. It is a **statement**, a line that does something instead of giving a value, so it stands on its own line.
7. **`sum`, after the loop.** When the loop has visited every element, the function returns the last value of `sum`.
:::

Follow it by hand for the cart of the next example, a lamp line of 2 units at 1990 cents and a rug line of 5 units at 4500 cents. Before the loop, `sum` is 0. The first turn sets `line` to the lamp line, and `sum` becomes 0 + 2 × 1990 = 3980. The second turn sets `line` to the rug line, and `sum` becomes 3980 + 5 × 4500 = 26480. There is no third element, so the loop ends, and `total` returns 26480.

#### What a loop can walk

What comes after `in` decides what the loop visits. Una has these forms:

| You write | The loop visits |
| --- | --- |
| `for line in lines` | each element of a list, from first to last |
| `for week in 1..3` | the whole numbers from 1 to 3, both included: 1, 2, 3 |
| `for position in 0..<count` | the whole numbers from 0 up to `count`, without `count` |
| `for character in sku.chars()` | each element of the list a function returns: here the characters of a text |
| `for entry in stock.entries()` | the entries of a map, in key order ([section 5.5](#s5-5)) |
| `let made = together for sku in skus` | each element, at the same time, building a list of the results ([chapter 12](/learn/memory-and-concurrency/#s12-4)) |

In a loop, the ends of a range can be any integer expressions of one type, such as `0..<skus.len`. In a `when` arm or a kind, they are literals. There is no other kind of loop: no `while` and no `loop`. [Una has no `while`](#una-has-no-while) says why.

### Loops over lists and ranges

#### Totals, bulk lines and weeks

The step totals a cart, lists its bulk lines, and walks a range of weeks:

:::steps
```una include="steps/05-for/src/totals.una" title="steps/05-for/src/totals.una" verified="check, run"
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

```text include="steps/05-for/expected/output.txt"
total: 26480 cents
bulk: ["RUG-07"]
week 1: 26480 cents so far
week 2: 52960 cents so far
week 3: 79440 cents so far
```

The output of `bulk` is a list of texts, and interpolation writes it in the form you would type in Una, with brackets and quotes.

#### Where a range starts and stops

A range is the easiest place to be off by one, so it pays to see each form run. The next step walks ranges and keeps the numbers each loop visits:

```una include="steps/06-loop-forms/src/shelves.una#aisles_through..aisles_before" title="steps/06-loop-forms/src/shelves.una"
--- The aisles from `start` to `stop`, `stop` included: a loop over an inclusive range.
aisles_through(start: Int, stop: Int) -> List[Int]
=
  let edit visited: List[Int] = []
  for aisle in start..stop
    visited = visited.append(item: aisle)
  visited

--- The aisles from `start` up to `stop`, `stop` left out: a loop over an exclusive range.
aisles_before(start: Int, stop: Int) -> List[Int]
=
  let edit visited: List[Int] = []
  for aisle in start..<stop
    visited = visited.append(item: aisle)
  visited
```

`main` calls them with a few pairs of ends:

```text include="steps/06-loop-forms/expected/output.txt#L3-L7"
aisles 1..3: [1, 2, 3]
aisles 1..<3: [1, 2]
aisles 2..2: [2]
aisles 2..<2: []
aisles 3..1: []
```

Read the lines in pairs. `..` stops *at* its end, and `..<` stops *before* it. A range from a number to itself visits that number once with `..`, and nothing with `..<`. A range whose start is above its end visits nothing: Una never counts down.

#### Positions of a list

Sometimes the body needs the position of each element, as a numbered receipt does. Walk the range of positions, from 0 up to the length:

```una include="steps/06-loop-forms/src/shelves.una#numbered" title="steps/06-loop-forms/src/shelves.una"
--- The lines of a receipt, numbered from 1: a loop over the positions of a list.
numbered(skus: List[Text]) -> List[Text]
=
  let edit lines: List[Text] = []
  for position in 0..<skus.len
    let sku = skus.at(index: position).or_else(default: "")
    lines = lines.append(item: "{position + 1}. {sku}")
  lines
```

```text include="steps/06-loop-forms/expected/output.txt#L8"
["1. DESK-02", "2. LAMP-01"]
```

`0..<skus.len` visits exactly the valid positions. `at` still returns an `Option`, because Una has no `skus[position]` form, and `or_else` gives the value inside it, or the default `""` ([section 5.3](#s5-3) explains both). When you need only the elements, walk the list itself: it is shorter, and it cannot miss an element or read past the end.

#### The characters of a text

Any function that returns a list gives a loop something to walk. `chars()` gives the characters of a text, one text of one character each. `is_digits` is true when every character of a text is a digit, 0 to 9:

```una include="steps/06-loop-forms/src/shelves.una#digits_in" title="steps/06-loop-forms/src/shelves.una"
--- How many digits a SKU holds: a loop over the characters of a text.
digits_in(sku: Text) -> Int
=
  let edit count = 0
  for character in sku.chars()
    if character.is_digits()
      count = count + 1
  count
```

```text include="steps/06-loop-forms/expected/output.txt#L9"
digits in LAMP-01: 2
```

#### An empty list

A loop over an empty list runs its body zero times. The accumulator keeps its first value, so a function that starts from the right value for "nothing" needs no special case:

```una include="steps/06-loop-forms/src/shelves.una#units" title="steps/06-loop-forms/src/shelves.una"
--- How many units a cart holds: a loop over a list.
units(lines: List[CartLine]) -> Int
=
  let edit count = 0
  for line in lines
    count = count + line.quantity
  count
```

```text include="steps/06-loop-forms/expected/output.txt#L1-L2"
units in the cart: 7
units in an empty cart: 0
```

#### Building a list at the same time: `together for`

`together for` runs one **task** per element: a piece of work the program may run alongside the others, at the same time, instead of one after another. It gives the list of what each task's body ends with. It stands where a value goes, after `let` or in an assignment:

```una include="steps/06-loop-forms/src/shelves.una#labels" title="steps/06-loop-forms/src/shelves.una"
--- A shelf label for each SKU, made at the same time: `together for` builds a list.
labels(skus: List[Text]) -> List[Text]
=
  let made = together for sku in skus
    "label {sku}"
  made
```

```text include="steps/06-loop-forms/expected/output.txt#L10"
["label DESK-02", "label LAMP-01"]
```

The results come in the order of the list, whatever order the tasks finish in. A task cannot assign a binding declared outside it, so `together for` cannot keep a running total: it only builds a list. [Chapter 12](/learn/memory-and-concurrency/#s12-4) covers tasks in full.

### What a loop body can hold

The body of a loop is a block like any other: it can hold `let` lines, an `if`, a `when`, and another loop. The step for this part works on orders:

```una include="steps/07-loop-bodies/src/orders.una#OrderLine..Movement" title="steps/07-loop-bodies/src/orders.una" caption="the kinds"
--- One line of an order: a SKU, the category it is sold under, and how many units.
kind OrderLine
  sku: Text
  category: Text
  quantity: Int

--- An order: its number and its lines.
kind Order
  number: Int
  lines: List[OrderLine]

--- A change to the stock of one SKU.
kind Movement = Received(units: Int) | Sold(units: Int) | Lost(units: Int)
```

#### A choice at each turn: `if` and `when`

An `if` inside the body decides, for each element, which steps to run. With an `else`, every element goes one way or the other, and two accumulators collect two results in one pass:

```una include="steps/07-loop-bodies/src/orders.una#lighting_and_other" title="steps/07-loop-bodies/src/orders.una"
--- The units of lighting, and of everything else: an `if` with an `else` inside a loop.
lighting_and_other(lines: List[OrderLine]) -> Text
=
  let edit lighting = 0
  let edit other = 0
  for line in lines
    if line.category == "lighting"
      lighting = lighting + line.quantity
    else
      other = other + line.quantity
  "lighting {lighting}, other {other}"
```

```text include="steps/07-loop-bodies/expected/output.txt#L1"
lighting 5, other 1
```

A `when` chooses by the variant of a sum kind ([chapter 4](/learn/kinds/#s4-3)). Each arm that assigns writes its assignment on its own line, indented under the arm:

```una include="steps/07-loop-bodies/src/orders.una#stock_after" title="steps/07-loop-bodies/src/orders.una"
--- The stock after a day of movements, from `start` units: a `when` inside a loop.
stock_after(start: Int, movements: List[Movement]) -> Int
=
  let edit stock = start
  for movement in movements
    when movement
      is Received(units) ->
        stock = stock + units
      is Sold(units) ->
        stock = stock - units
      is Lost(units) ->
        stock = stock - units
  stock
```

```text include="steps/07-loop-bodies/expected/output.txt#L2"
stock at closing: 8
```

The stock starts at 4, receives 10, sells 3, loses 1 and sells 2: 4 + 10 − 3 − 1 − 2 = 8.

#### A loop inside a loop

A body may hold another loop. The inner loop runs all its turns during each turn of the outer one. Orders hold lines, so counting every unit of every order takes two loops:

```una include="steps/07-loop-bodies/src/orders.una#all_units" title="steps/07-loop-bodies/src/orders.una"
--- Every unit of every order: a loop inside a loop.
all_units(orders: List[Order]) -> Int
=
  let edit total = 0
  for order in orders
    for line in order.lines
      total = total + line.quantity
  total
```

```text include="steps/07-loop-bodies/expected/output.txt#L3"
units in two orders: 6
```

Nested loops also combine two lists. Each color meets each size, so two colors and two sizes give four SKUs, in the order the loops visit them: all the sizes of the first color, then all the sizes of the second.

```una include="steps/07-loop-bodies/src/orders.una#tee_skus" title="steps/07-loop-bodies/src/orders.una"
--- Every SKU of a T-shirt, one for each color and size, such as `TEE-RED-S`.
tee_skus(colors: List[Text], sizes: List[Text]) -> List[Text]
=
  let edit skus: List[Text] = []
  for color in colors
    for size in sizes
      skus = skus.append(item: "TEE-{color}-{size}")
  skus
```

```text include="steps/07-loop-bodies/expected/output.txt#L4"
["TEE-RED-S", "TEE-RED-M", "TEE-BLUE-S", "TEE-BLUE-M"]
```

The inner loop assigns `skus`, which is declared outside both loops. That is how a result leaves a loop: through an editable binding declared before it.

### How a loop behaves

#### Order, and how many turns

- A loop over a list visits the elements in the list's order, each one once.
- A loop over a range visits the integers in increasing order.
- The list or the range is computed once, before the first turn. Changing a binding inside the body does not change how many turns the loop takes.
- Every turn runs. Una has no `break` to leave a loop early and no `continue` to skip the rest of a turn. To skip an element, put the body's steps under an `if`. To stop at the first element that matches, use `first_where` ([section 5.4](#s5-4)), which stops there.

#### What lives from one turn to the next

A binding declared inside the body, with `let`, is new at each turn of the loop and is gone after it. To carry a value from one turn to the next, or out of the loop, declare it before the loop with `let edit`, as `sum` and `found` are. The loop variable, `line` or `week`, is a plain binding: you read it, and the next turn gives it the next element. Assigning it is an error, U2019, as for any plain `let` ([updating a plain `let`](#updating-a-plain-let-u2019) shows the message).

#### A loop is a statement

A `for` loop gives no value of its own: it is a statement, and what it computes lives in the bindings it updates. So a function ends with the binding, `sum`, after the loop, never with the loop. `together for` is the exception: it is written after `let`, and its value is the list it builds.

#### A loop is not a call

A **call** is one function running another and waiting for its answer. The **call depth** is how many calls are waiting at once, and a run has a limit on it. A loop's turns are not calls, so a loop does not use up the call depth, however many turns it takes ([chapter 12](/learn/memory-and-concurrency/#s12-5)). A function that calls itself, which [Una has no `while`](#una-has-no-while) shows, adds one call per step.

### Una has no `while`

Many languages have a second kind of loop, `while`, which repeats its body for as long as a condition holds. Its end depends on the body changing something that the condition reads. When the body forgets to, the loop never ends, and the program hangs.

In Una, every loop walks a list or a range whose size is known before the first turn, so a reader can see where each loop ends. Write a `while` anyway, in a function that counts how long the stock lasts:

```diff include="steps/07-loop-bodies..steps/08-while:src/orders.una" context="1" title="src/orders.una"
--- a/src/orders.una
+++ b/src/orders.una
@@ -64,3 +64,8 @@
 =
-  if stock < per_week then 0 else 1 + weeks_of_stock(stock - per_week, per_week)
+  let edit left = stock
+  let edit weeks = 0
+  while left >= per_week
+    left = left - per_week
+    weeks = weeks + 1
+  weeks
 
```

`una check .` reports:

```text include="steps/08-while/expected/rendered.txt"
[U0103] Error: `while` is not a keyword in Una; use `for` or recursion
    ╭─[ src/orders.una:67:3 ]
    │
 67 │   while left >= per_week
    │   ──┬──
    │     ╰──── `while` is not a keyword in Una; use `for` or recursion
    │
    │ Note: run `una explain U0103` for an explanation
────╯
```

The message names the two ways Una repeats work. Here, how many weeks the stock lasts is not known in advance, so a range does not fit. **Recursion** does: a function that calls itself with a smaller problem, and stops at a case it can answer at once ([chapter 3](/learn/functions/) introduces functions).

```una include="steps/07-loop-bodies/src/orders.una#weeks_of_stock" title="steps/07-loop-bodies/src/orders.una"
--- How many whole weeks `stock` units last when `per_week` units sell each week.
weeks_of_stock(stock: Int, per_week: Int) -> Int
  requires per_week >= 1
=
  if stock < per_week then 0 else 1 + weeks_of_stock(stock - per_week, per_week)
```

```text include="steps/07-loop-bodies/expected/output.txt#L5"
10 units at 3 a week last 3 weeks
```

With 10 units and 3 sold a week, the function answers 1 + the weeks of 7 units, which is 1 + the weeks of 4 units, which is 1 + the weeks of 1 unit, which is 0: 3 weeks. Each call has a smaller stock, so the calls end. `requires per_week >= 1` keeps a caller from passing 0, which would never make the stock smaller ([chapter 3](/learn/functions/#s3-2) introduced `requires`, and [chapter 7](/learn/contracts/#s7-1) explains it). When you know an upper limit, such as "at most 52 weeks", a range up to that limit with an `if` in the body is the other choice.

### Choosing a loop or a function over the list

A loop says *how* to walk a list. The prelude also has functions that walk the list for you, so you say only what to do with each element ([section 5.4](#s5-4)):

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| A total of integers | `map`, then `sum()`, or a loop |
| A new list with one result per element | `map` |
| Some of the elements | `filter`, or a loop with an `if` |
| The first element that matches, and stop there | `first_where` |
| Several results from one pass, or a step of several lines | a `for` loop with `let edit` bindings |
| A result per position, or a combination of two lists | a `for` loop over a range, or nested loops |
| Repeat until something happens, with no limit known in advance | recursion |
:::

Both are right where the table gives two answers. Choose what a reader follows faster: a one-line function call, or a loop when the step needs room.

### Check yourself: loops

Read each function, and predict what it returns before you open the answer.

This function counts shelves that need restocking:

```una include="steps/07-loop-bodies/src/orders.una#low_shelves" title="steps/07-loop-bodies/src/orders.una"
--- How many shelves hold fewer than 2 units.
low_shelves(counts: List[Int]) -> Int
=
  let edit low = 0
  for count in counts
    if count < 2
      low = low + 1
  low
```

What does `low_shelves([3, 0, 1, 5])` return?

:::answer Show the answer
```text include="steps/07-loop-bodies/expected/output.txt#L6"
low shelves: 2
```

The body runs four times. `low` goes up for 0 and for 1, the two counts below 2, and stays put for 3 and 5. An empty list would give 0, the value `low` starts with.
:::

This one keeps a running total, and the list of totals after each line:

```una include="steps/07-loop-bodies/src/orders.una#running" title="steps/07-loop-bodies/src/orders.una"
--- The total after each line, in order.
running(quantities: List[Int]) -> List[Int]
=
  let edit total = 0
  let edit seen: List[Int] = []
  for quantity in quantities
    total = total + quantity
    seen = seen.append(item: total)
  seen
```

What does `running([2, 1, 3])` return?

:::answer Show the answer
```text include="steps/07-loop-bodies/expected/output.txt#L7"
running totals: [2, 3, 6]
```

Both bindings live outside the loop, so each turn starts from what the previous turn left. `total` goes 2, 3, 6, and each turn appends the new total to `seen`.
:::

## 5.3 A value that may be missing: `Option`

### What an `Option` is

Some questions have no answer. Ask a catalog for the price of a SKU it does not sell, ask an empty list for its first element, or ask the text `"seven"` for the number it holds: there is nothing to give back. An **`Option`** is the type of an answer that may be missing. Think of a parcel locker at a pickup point: you open it, and either a parcel is inside or the locker is empty. Before you carry anything away, you look.

`Option[T]` is a sum kind of the prelude ([chapter 4](/learn/kinds/#s4-2)) with two variants:

- `Some(value)` holds one value of the type `T`. A price lookup that finds the price gives `Some(1990)`, an `Option[Int]`.
- `None` holds nothing. It means "there is no value here".

`T` is a **type parameter**: it stands for whatever type the option may hold. `Option[Int]` may hold an `Int`, and `Option[Product]` a `Product`. An `Option[Int]` is not an `Int`, and you cannot add it, compare it or print it as a number until you have said what happens when it is `None`.

### Why absence needs its own type

In many languages a search that finds nothing returns a special value, often called null, of the same type as a real answer. The type then says that a price is always there, and the first line that uses a missing price fails while the program runs, often far from the search.

In Una the type says it. Here is a price lookup that uses the search result as if the product were always found:

```diff include="steps/11-option..steps/09-missing-price:src/lookup.una" context="1" title="src/lookup.una"
--- a/src/lookup.una
+++ b/src/lookup.una
@@ -11,5 +11,3 @@
   let found = catalog.first_where(keep: fn(product) -> product.sku == sku)
-  when found
-    is Some(product) -> Some(product.cents)
-    is None -> None
+  Some(found.cents)
 
```

`una check .` reports:

```text include="steps/09-missing-price/expected/rendered.txt"
[U1001] Error: `Option[Product]` has no field `cents`, and no function `cents` in scope applies
    ╭─[ src/lookup.una:12:14 ]
    │
 12 │   Some(found.cents)
    │              ──┬──
    │                ╰──── `Option[Product]` has no field `cents`, and no function `cents` in scope applies
    │
    │ Note: run `una explain U1001` for an explanation
────╯
```

Read it from the top. `first_where` returned an `Option[Product]`, and the message says that this type has no field `cents`: the field belongs to `Product`, which the option may or may not hold. The mark points at `.cents`. The checker does not guess what a missing product should mean. You decide, with one of the forms of the next part, and the decision is written where the value is used.

### How to write and use an `Option`

The step of this part shows each form on a shelf count, which a clerk may not have taken yet:

```una include="steps/10-option-forms/src/counts.una#shown..typed_units" title="steps/10-option-forms/src/counts.una"
--- What a shelf label shows for a count that may be missing: `when` with both arms.
shown(count: Option[Int]) -> Text
=
  when count
    is Some(units) -> "{units} on the shelf"
    is None -> "not counted yet"

--- Whether a shelf holds more than 10 units: `when` with an `else` arm.
well_stocked(count: Option[Int]) -> Bool
=
  when count
    is Some(units) -> units > 10
    else -> false

--- The units to order for a shelf: a missing count orders a full shelf of 12.
to_order(count: Option[Int]) -> Int = 12 - count.or_else(default: 0)

--- Whether a shelf still needs counting: a test of the variant, in a condition.
needs_count(count: Option[Int]) -> Bool = count is None

--- The units typed by a clerk, or 0 when the text is not a number: `if none use`.
typed_units(raw: Text) -> Int
=
  let units = raw.trim.to_int()
    if none use 0
  units
```

#### Making one: `Some`, `None`, and the functions that return one

```una include="steps/10-option-forms/src/counts.una#L33-L35" title="steps/10-option-forms/src/counts.una"
  let counted = Some(14)
  let missing: Option[Int] = None
  @console.print("{counted} {missing}")
```

```text include="steps/10-option-forms/expected/output.txt#L1"
Some(14) None
```

`Some(14)` wraps a value. `None` holds nothing, so it says nothing about the type: write the type on the binding, `Option[Int]`, as for an empty list. More often an `Option` comes from a function. In the prelude, these return one: `first`, `at` and `first_where` on a list, `get` on a map ([section 5.5](#s5-5)), and `to_int` and `find` on a text:

```una include="steps/10-option-forms/src/counts.una#L44-L47" title="steps/10-option-forms/src/counts.una"
  let sku = "LAMP-01"
  let dash = sku.find(text: "-")
  let number = sku.slice(start: 5, end: 7).to_int()
  @console.print("{dash} {number} {sku.chars().first()}")
```

```text include="steps/10-option-forms/expected/output.txt#L8"
Some(4) Some(1) Some("L")
```

`find` gives the position of the first `-` in `LAMP-01`, `to_int` reads the digits `01` as 1, and `chars().first()` is the first character.

#### Both cases: `when`

A `when` ([chapter 4](/learn/kinds/#s4-3)) takes an `Option` apart. `shown` has one arm per variant: `is Some(units)` binds the value inside to the name `units`, and `is None` says what to do without one. Each arm gives a `Text`, so the `when` gives one too.

```una include="steps/10-option-forms/src/counts.una#L36" title="steps/10-option-forms/src/counts.una"
  @console.print("{shown(counted)} / {shown(missing)}")
```

```text include="steps/10-option-forms/expected/output.txt#L2"
14 on the shelf / not counted yet
```

#### One case and the rest: `else`

When only the `Some` case needs work, an `else` arm covers every variant without an arm of its own. `well_stocked` answers `false` for a missing count:

```una include="steps/10-option-forms/src/counts.una#L37" title="steps/10-option-forms/src/counts.una"
  @console.print("{well_stocked(counted)} {well_stocked(missing)}")
```

```text include="steps/10-option-forms/expected/output.txt#L3"
true false
```

#### A default: `or_else`

`count.or_else(default: 0)` is the value inside `Some`, or the default for `None`. It is the short form of a `when` whose `None` arm is a plain value. `to_order` orders a full shelf of 12 units when no count is known:

```una include="steps/10-option-forms/src/counts.una#L38" title="steps/10-option-forms/src/counts.una"
  @console.print("{to_order(Some(5))} {to_order(missing)}")
```

```text include="steps/10-option-forms/expected/output.txt#L4"
7 12
```

#### A question about the case: `is None` and `is_some`

`count is None` is a condition, `true` or `false`, that tests the variant without taking the value out. `is_some()` is the same question the other way round:

```una include="steps/10-option-forms/src/counts.una#L39" title="steps/10-option-forms/src/counts.una"
  @console.print("{needs_count(missing)} {missing.is_some()}")
```

```text include="steps/10-option-forms/expected/output.txt#L5"
true false
```

#### A default under the line: `if none use`

`typed_units` writes the default on its own line under the call: `if none use 0`. After that line, `units` is a plain `Int`. This clause, and `if none fail`, which turns a missing value into a failure, belong to [chapter 6, Failure](/learn/failure/#s6-2).

```una include="steps/10-option-forms/src/counts.una#L40-L42" title="steps/10-option-forms/src/counts.una"
  let typed = typed_units(" 7 ")
  let spelled = typed_units("seven")
  @console.print("{typed} {spelled}")
```

```text include="steps/10-option-forms/expected/output.txt#L6"
7 0
```

### Looking up a price

The forms together, in a catalog lookup. `price_of` passes the absence on to its caller, and `label` decides what it means:

:::steps
```una include="steps/11-option/src/lookup.una" title="steps/11-option/src/lookup.una" verified="check, run"
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
2. **`when found`.** One arm per case, `is Some(product)` and `is None`. The name in `Some(product)` binds the value inside.
3. **`Some(product.cents)`.** `price_of` itself returns an `Option`, so its caller decides what a missing price means. `label` decides: it prints "not sold here".
4. **`missing.or_else(default: 0)`.** The short form when a default is right: the value inside `Some`, or the default for `None`.
5. **`"3".to_int()` and `catalog.at(index: 5)`.** Two more functions that return an `Option`: a text that may not be a number, and a position that may be past the end.
:::

`una run .` prints:

```text include="steps/11-option/expected/output.txt"
DESK-02: 15900 cents
CHAIR-09: not sold here
None or 0
Some(3) and None
```

An `Option` interpolates as `Some(3)` or `None`, which helps when you debug, but a report should say what the absence means, as `label` does.

### How an `Option` behaves

#### A `when` covers both cases

A `when` over an `Option` must have an arm for `Some` and one for `None`, or an `else`. Leave one out, and the checker names the variant that has no arm: [a `when` that forgets `None`](#a-when-that-forgets-none-u2007) shows the message. When the day comes that a value is missing, the program already says what to do.

#### Options compare by what they hold

```una include="steps/10-option-forms/src/counts.una#L43" title="steps/10-option-forms/src/counts.una"
  @console.print("{counted == Some(14)} {missing == None}")
```

```text include="steps/10-option-forms/expected/output.txt#L7"
true true
```

`Some(14) == Some(14)` holds, and `None == None` holds. `Some(0)` and `None` differ: a count of zero is a count, and a missing count is not.

#### The default of `or_else` is computed first

> [!NOTE]
> The default of `or_else` is an argument like any other, so it is computed before the call, whether it is used or not. Keep it a plain value, such as `0` or `"other"`. A call that has effects, such as one that asks a service, cannot be the default: bind its result with `let` first.

### Choosing how to use an `Option`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Do different things when the value is there and when it is not | `when` with `is Some(v)` and `is None` |
| Work only on the value, with one answer for the rest | `when` with `is Some(v)` and `else` |
| Carry on with a default | `or_else(default: v)`, or `if none use v` on the line under the call ([chapter 6](/learn/failure/)) |
| Know only whether there is a value | `is_some()`, or `o is None` in a condition |
| Make a missing value a failure of your function | `if none fail V`, in [chapter 6](/learn/failure/) |
:::

Prefer a `when` when the absence needs its own words, as on a product page. Prefer `or_else` when the default is the honest answer, as 0 units for a category with no sales.

### Check yourself: `Option`

The three functions of [How to write and use an `Option`](#how-to-write-and-use-an-option) get one more set of counts:

```una include="steps/10-option-forms/src/counts.una#L48" title="steps/10-option-forms/src/counts.una"
  @console.print("{shown(Some(0))} / {to_order(Some(12))} / {well_stocked(Some(10))}")
```

What does the line print?

:::answer Show the answer
```text include="steps/10-option-forms/expected/output.txt#L9"
0 on the shelf / 0 / false
```

`Some(0)` is a count of zero, not a missing count, so `shown` takes the `Some` arm. `to_order(Some(12))` is 12 − 12 = 0. `well_stocked(Some(10))` takes the `Some` arm, and 10 > 10 is `false`.
:::

## 5.4 Functions over lists: `map`, `filter` and `fold`

### What a function over a list is

A loop ([section 5.2](#s5-2)) says *how* to walk a list: start a binding, visit each element, update the binding. Most walks are one of a few shapes, and the prelude has a function for each shape. You give it the list and the one step that differs, and it does the walking.

Think of instructions to a stock clerk. "Put a new price tag on every item" changes each item. "Pull every item past its date" keeps some items. "Count the units on the shelf" turns many items into one number. "Find me the first blue mug" stops at a match. Each instruction names one shape of work and one rule. In Una, these are `map`, `filter`, `fold` and `first_where`, and the rule is a function you pass to them.

A function that takes another function as an argument is a **higher-order function**. The function you pass is often a **lambda**, a function written in place with `fn` ([chapter 3](/learn/functions/#s3-5)): `fn(cents) -> cents * 2` takes `cents` and gives `cents * 2`.

### Why the prelude walks the list for you

Here are three loops over a cart: one prices each line, one leaves out the gift cards, and one counts the units.

```una include="steps/12-loops-repeat/src/cart.una#line_totals..units" title="steps/12-loops-repeat/src/cart.una"
--- What each line costs, in cents.
line_totals(lines: List[CartLine]) -> List[Int]
=
  let edit totals: List[Int] = []
  for line in lines
    totals = totals.append(item: line.quantity * line.cents)
  totals

--- The lines that are not gift cards.
goods(lines: List[CartLine]) -> List[CartLine]
=
  let edit kept: List[CartLine] = []
  for line in lines
    if not line.sku.starts_with(prefix: "GIFT-")
      kept = kept.append(item: line)
  kept

--- How many units the cart holds.
units(lines: List[CartLine]) -> Int
=
  let edit count = 0
  for line in lines
    count = count + line.quantity
  count
```

```text include="steps/12-loops-repeat/expected/output.txt"
[3980, 5000] 1 3
```

They work, and they are almost the same code. Each declares an empty binding, walks the list, updates the binding, and returns it. Only one line in each says what the function is for. A reader has to read all of them to find that line, and each copy of the walk is one more place to get the start value or the update wrong. With the prelude's functions, the walk is written once, in the prelude, and your code keeps only the line that matters.

### How to write `map`, `filter`, `fold` and `first_where`

Each one is called with method syntax on a list, and takes its function under a label that says what the function does: `each`, `keep` or `step`. The step for this part works on prices and SKUs:

```una include="steps/13-list-functions/src/prices.una#L1-L11" title="steps/13-list-functions/src/prices.una"
module prices

--- A price with 10% sales tax added, rounded down.
with_tax(cents: Int) -> Int = cents + cents / 10

pub main() -> Unit
  uses @console: Console[print]
=
  let prices = [1990, 4500, 850]
  let skus = ["LAMP-01", "RUG-07", "MUG-11"]
  let empty: List[Int] = []
```

#### A new value for each element: `map(each:)`

`map` calls its function on each element and gives the list of the results, in the same order and of the same length. The function may be a declared function, passed by its name, or a lambda. Its result may have another type than the elements: the second call gives SKUs in lower case, and the third gives a `Bool` for each price.

```una include="steps/13-list-functions/src/prices.una#L12-L14" title="steps/13-list-functions/src/prices.una"
  @console.print("map: {prices.map(each: with_tax)}")
  @console.print("map: {skus.map(each: fn(sku) -> sku.to_lower())}")
  @console.print("map: {prices.map(each: fn(cents) -> cents >= 2000)}")
```

```text include="steps/13-list-functions/expected/output.txt#L1-L3"
map: [2189, 4950, 935]
map: ["lamp-01", "rug-07", "mug-11"]
map: [false, true, false]
```

`with_tax` is passed by name, without parentheses: you hand over the function, and `map` calls it. 1990 plus a tenth, rounded down, is 2189.

#### Some of the elements: `filter(keep:)`

`filter` keeps the elements for which its function gives `true`, in their order. The function must give a `Bool`.

```una include="steps/13-list-functions/src/prices.una#L15-L18" title="steps/13-list-functions/src/prices.una"
  let limit = 2000
  let above = prices.filter(keep: fn(cents) -> cents >= limit)
  let mugs = skus.filter(keep: fn(sku) -> sku.starts_with(prefix: "MUG"))
  @console.print("filter: {above} {mugs}")
```

```text include="steps/13-list-functions/expected/output.txt#L4"
filter: [4500] ["MUG-11"]
```

The first lambda reads `limit`, a binding declared outside it. A lambda can read the bindings around it, as they were when it was made.

#### One value from all the elements: `fold(initial:, step:)`

`fold` carries one value from the first element to the last. It starts from `initial`. At each element it calls `step` with two arguments, the value so far and the element, and the step's result becomes the new value so far. The last value is the result.

```una include="steps/13-list-functions/src/prices.una#L19-L21" title="steps/13-list-functions/src/prices.una"
  let total = prices.fold(initial: 0, step: fn(sum, cents) -> sum + cents)
  let top = prices.fold(initial: 0, step: fn(best, cents) -> max(best, b: cents))
  @console.print("fold: {total} and {top}")
```

```text include="steps/13-list-functions/expected/output.txt#L5"
fold: 7340 and 4500
```

The first `fold` adds up: 0 + 1990 = 1990, + 4500 = 6490, + 850 = 7340. The second keeps the largest price seen so far with `max`, whose second parameter is named `b`. The value so far may have any type, the same for `initial`, the step's first parameter, and its result.

#### The first match: `first_where(keep:)`

`first_where` gives the first element for which its function gives `true`, as an `Option`, and stops there. When no element matches, it gives `None`.

```una include="steps/13-list-functions/src/prices.una#L22-L24" title="steps/13-list-functions/src/prices.una"
  let rug = skus.first_where(keep: fn(sku) -> sku.starts_with(prefix: "RUG"))
  let desk = skus.first_where(keep: fn(sku) -> sku.starts_with(prefix: "DESK"))
  @console.print("first_where: {rug} and {desk}")
```

```text include="steps/13-list-functions/expected/output.txt#L6"
first_where: Some("RUG-07") and None
```

#### One after another: chaining

The result of one call is a list, so the next call can follow it with another dot. Read a chain from left to right: keep the prices under 2000, add tax to each, and add them up.

```una include="steps/13-list-functions/src/prices.una#L25-L26" title="steps/13-list-functions/src/prices.una"
  let cheap = prices.filter(keep: fn(cents) -> cents < 2000).map(each: with_tax).sum()
  @console.print("chained: {cheap}")
```

```text include="steps/13-list-functions/expected/output.txt#L7"
chained: 3124
```

1990 and 850 are under 2000; with tax they are 2189 and 935, and their sum is 3124.

### Pricing a cart without a loop

The tools in a store example. The step prices a cart, counts its units, and decides whether it ships free:

:::steps
```una include="steps/14-higher-order/src/pricing.una" title="steps/14-higher-order/src/pricing.una" verified="check, run"
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

```text include="steps/14-higher-order/expected/output.txt"
[3980, 4500, 5000]
["LAMP-01"]
4 units
free shipping: false
```

The three loops of [Why the prelude walks the list for you](#why-the-prelude-walks-the-list-for-you) are each one call here: `map(each: line_cents)`, a `filter`, and a `fold`.

### How the functions behave

#### Order, and how often the function is called

`map`, `filter`, `fold` and `first_where` call their function on the elements from first to last, at most once per element. `first_where` stops after the first element it accepts, so the elements after it are never tested.

#### Functions over an empty list

Each one has a plain answer for an empty list. `map` gives `[]`, `fold` gives its `initial` value, `first_where` gives `None`, and `sum` gives 0:

```una include="steps/13-list-functions/src/prices.una#L27-L30" title="steps/13-list-functions/src/prices.una"
  let doubled = empty.map(each: fn(cents) -> cents * 2)
  let counted = empty.fold(initial: 0, step: fn(sum, cents) -> sum + cents)
  let first_big = empty.first_where(keep: fn(cents) -> cents > 0)
  @console.print("empty: {doubled} {counted} {first_big}")
```

```text include="steps/13-list-functions/expected/output.txt#L8"
empty: [] 0 None
```

So choose `initial` as the right answer for "nothing": 0 for a total, and for a largest value, one that no element can be below, such as 0 for prices.

#### The function must fit

The function you pass must take the element's type and give what the call needs. `filter` needs a `Bool` from `keep`. Give it a number instead:

```diff include="steps/13-list-functions..steps/15-filter-result:src/prices.una" context="1" title="src/prices.una"
--- a/src/prices.una
+++ b/src/prices.una
@@ -15,3 +15,3 @@
   let limit = 2000
-  let above = prices.filter(keep: fn(cents) -> cents >= limit)
+  let above = prices.filter(keep: fn(cents) -> cents - limit)
   let mugs = skus.filter(keep: fn(sku) -> sku.starts_with(prefix: "MUG"))
```

`una check .` reports:

```text include="steps/15-filter-result/expected/rendered.txt"
[U2001] Error: expected `Bool`, found `Int`
    ╭─[ src/prices.una:16:48 ]
    │
 16 │   let above = prices.filter(keep: fn(cents) -> cents - limit)
    │                                                ──────┬──────
    │                                                      ╰──────── expected `Bool`, found `Int`
    │
    │ Note: run `una explain U2001` for an explanation
────╯
```

The message says what `keep` must give, a `Bool`, and what the lambda gives, an `Int`. The mark points at the lambda's body, `cents - limit`, which is a number, not a yes-or-no answer. The fix is a comparison: `cents >= limit`.

#### What a lambda can see

A lambda sees the values of the bindings around it as they were when it was made, and it cannot assign to a `let edit` binding outside it: its body is one expression, not a block of statements. To accumulate, use `fold`, or a `for` loop.

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

### Check yourself: functions over lists

Predict what this prints before you open the answer:

```una include="steps/13-list-functions/src/prices.una#L31-L33" title="steps/13-list-functions/src/prices.una"
  let picked = [5, 12, 8].filter(keep: fn(units) -> units > 6).map(each: fn(units) -> units * 2)
  let longest = skus.fold(initial: 0, step: fn(best, sku) -> max(best, b: sku.len))
  @console.print("question: {picked} {longest}")
```

:::answer Show the answer
```text include="steps/13-list-functions/expected/output.txt#L9"
question: [24, 16] 7
```

`filter` keeps 12 and 8, the units above 6, in their order, and `map` doubles each: `[24, 16]`. The `fold` keeps the longest length seen so far: `LAMP-01` has 7 characters, `RUG-07` 6 and `MUG-11` 6, so the result is 7.
:::

## 5.5 Maps

### What a map is

A **map** holds values under keys. Think of a stock ledger: each SKU has one line, and the line says how many units are on hand. You never read the ledger from the top to find a SKU; you go to its line. A map works the same way. Each **key**, here a SKU, appears once, and maps to one **value**, here the units. A key together with its value is an **entry**.

`Map[K, V]` is the type of a map whose keys have the type `K` and whose values have the type `V`. The stock of each SKU is a `Map[Text, Int]`. The units of each category are a `Map[Text, Int]` too, and the summary of each category, in the day-to-day program, a `Map[Text, Summary]`.

### Why a program needs maps

Count the units sold in each category with what this chapter has shown so far. A list of the categories, and a `filter` and a `sum` for each one:

```una include="steps/16-groups-by-hand/src/sales.una" title="steps/16-groups-by-hand/src/sales.una" verified="check, run"
module sales

--- A sale of some units of one SKU, in a category.
kind Sale
  sku: Text
  category: Text
  quantity: Int

--- The units sold in one category: a walk over every sale, for each category asked.
units_of(sales: List[Sale], category: Text) -> Int = sales.filter(keep: fn(sale) -> sale.category == category).map(each: fn(sale) -> sale.quantity).sum()

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Sale(sku: "LAMP-01", category: "lighting", quantity: 2)
  let rug = Sale(sku: "RUG-07", category: "textiles", quantity: 1)
  let shade = Sale(sku: "SHADE-05", category: "lighting", quantity: 3)
  let spade = Sale(sku: "SPADE-02", category: "garden", quantity: 4)
  let sales = [lamp, rug, shade, spade]
  let categories = ["lighting", "textiles"]
  for category in categories
    @console.print("{category}: {units_of(sales, category: category)}")
  @console.print("{sales.map(each: fn(sale) -> sale.quantity).sum()} units sold in all")
```

`una run .` prints:

```text include="steps/16-groups-by-hand/expected/output.txt"
lighting: 5
textiles: 1
10 units sold in all
```

The totals by category add up to 6, and the store sold 10 units. The 4 units of `SPADE-02` are lost, because nobody wrote `"garden"` into the list of categories. The code has to know every category in advance. It is also slow on a real day: it walks every sale once for each category, so 1,000 sales in 50 categories take 50,000 tests. A map fixes both. You add each sale to its category's entry as you meet it, so a new category gets an entry by itself, and each sale is visited once.

### How to write and use a map

The step of this part keeps a ledger. Its `main` prints one line per group of operations:

```una include="steps/17-map-forms/src/ledger.una#stock_after_day" title="steps/17-map-forms/src/ledger.una"
--- The units on hand of each SKU, after a delivery and a sale.
stock_after_day() -> Map[Text, Int]
=
  let edit stock: Map[Text, Int] = empty_map()
  edit stock.set(key: "LAMP-01", value: 4)
  edit stock.set(key: "DESK-02", value: 1)
  edit stock.set(key: "VASE-03", value: 6)
  edit stock.set(key: "LAMP-01", value: 3)
  edit stock.remove(key: "VASE-03")
  stock
```

#### An empty map: `empty_map()`

A map starts empty. `empty_map()` makes one, and takes its key and value types from the binding, so write them there: `let edit stock: Map[Text, Int] = empty_map()`.

```una include="steps/17-map-forms/src/ledger.una#L17-L19" title="steps/17-map-forms/src/ledger.una"
  let empty: Map[Text, Int] = empty_map()
  let stock = stock_after_day()
  @console.print("{empty} {empty.len} / {stock} {stock.len}")
```

```text include="steps/17-map-forms/expected/output.txt#L1"
{} 0 / {"DESK-02": 1, "LAMP-01": 3} 2
```

A map interpolates between braces, as `{}` when empty, and `m.len` is its number of entries. `stock_after_day` set `LAMP-01` twice and removed `VASE-03`, so two entries are left.

#### Changing a map in place: `edit m.set` and `edit m.remove`

`edit stock.set(key: "LAMP-01", value: 4)` adds the key with its value, or replaces the value when the key is already there. `edit stock.remove(key: "VASE-03")` takes the key out. Both change the map in place, so:

- the binding is declared `let edit`, since only an editable binding may change ([chapter 2](/learn/values/#s2-4));
- the call starts with the word `edit`, which marks the line where the map changes;
- the call stands alone on its line, as a statement: it gives no value.

In `stock_after_day`, the fourth line sets `LAMP-01` again, to 3, so the map keeps one entry for it.

#### A new map from an old one: `with` and `without`

`stock.with(key: "RUG-07", value: 9)` gives a new map with one more entry, or one changed entry, and `without` a new map with one key fewer. The map you call them on does not change, so they need no `edit`:

```una include="steps/17-map-forms/src/ledger.una#L20-L22" title="steps/17-map-forms/src/ledger.una"
  let restocked = stock.with(key: "RUG-07", value: 9)
  let retired = restocked.without(key: "DESK-02")
  @console.print("{restocked} {retired} {stock}")
```

```text include="steps/17-map-forms/expected/output.txt#L2"
{"DESK-02": 1, "LAMP-01": 3, "RUG-07": 9} {"LAMP-01": 3, "RUG-07": 9} {"DESK-02": 1, "LAMP-01": 3}
```

The last of the three maps is `stock`, unchanged.

#### Reading: `get`, `has` and `len`

`get` returns an `Option`: `Some` with the value, or `None` for a key the map does not hold ([section 5.3](#s5-3)). `has` answers only whether the key is there.

```una include="steps/17-map-forms/src/ledger.una#L23-L27" title="steps/17-map-forms/src/ledger.una"
  let lamps = stock.get(key: "LAMP-01")
  let vases = stock.get(key: "VASE-03")
  let has_desks = stock.has(key: "DESK-02")
  let has_vases = stock.has(key: "VASE-03")
  @console.print("{lamps} {vases} {has_desks} {has_vases}")
```

```text include="steps/17-map-forms/expected/output.txt#L3"
Some(3) None true false
```

#### Listing: `keys`, `values` and `entries`

`keys()` and `values()` give lists, and `entries()` a list of `Entry` records, each with the fields `key` and `value`. A `for` loop over `entries()` visits each key with its value:

```una include="steps/17-map-forms/src/ledger.una#L28-L30" title="steps/17-map-forms/src/ledger.una"
  @console.print("{restocked.keys()} {restocked.values()}")
  for entry in restocked.entries()
    @console.print("{entry.key} has {entry.value}")
```

```text include="steps/17-map-forms/expected/output.txt#L4-L7"
["DESK-02", "LAMP-01", "RUG-07"] [1, 3, 9]
DESK-02 has 1
LAMP-01 has 3
RUG-07 has 9
```

### Stock by SKU

The forms together. The step keeps the stock of each SKU, and groups sales by category:

:::steps
```una include="steps/18-maps/src/stock.una" title="steps/18-maps/src/stock.una" verified="check, run"
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

```text include="steps/18-maps/expected/output.txt"
{"DESK-02": 1, "LAMP-01": 4} and {"DESK-02": 1, "LAMP-01": 4, "RUG-07": 9}
Some(4) None
["DESK-02", "LAMP-01", "RUG-07"]
lighting: 5
textiles: 1
```

`units_by_category` needs no list of categories. The first sale of a category finds no entry, starts from 0, and creates one; every later sale of it adds to that entry.

### How a map behaves

#### Entries in key order

A map keeps its entries ordered by key, ascending, not in the order you added them. `keys()`, `values()` and `entries()` all list them in that order, and so does interpolation. Texts order character by character, and numbers by value:

```una include="steps/17-map-forms/src/ledger.una#L31-L32" title="steps/17-map-forms/src/ledger.una"
  let aisles = empty_map().with(key: 12, value: "garden").with(key: 3, value: "lighting")
  @console.print("{aisles}")
```

```text include="steps/17-map-forms/expected/output.txt#L8"
{3: "lighting", 12: "garden"}
```

The key 12 was added first, and 3 still comes first. So a report built from a map comes out sorted by key, with no `sort` call, and the same input always gives the same output.

#### One value per key

A key appears once. `set` and `with` on a key that is there replace its value, so the length stays the same. To keep several values under one key, make the value a list, as `Map[Int, List[Text]]` in [exercise 3](#exercise-3-categories-by-revenue).

#### A missing key is not an error

`get` on a missing key gives `None`, and `remove` or `without` on a missing key leaves the map as it is. Neither stops the program.

#### Maps are values, and compare by content

`with` and `without` never change the map they are called on, and `set` and `remove` change only the binding they are written on. Two maps are equal when they hold the same keys with equal values:

```una include="steps/17-map-forms/src/ledger.una#L33-L34" title="steps/17-map-forms/src/ledger.una"
  let same = restocked.without(key: "DESK-02")
  @console.print("{retired == same} {retired == stock}")
```

```text include="steps/17-map-forms/expected/output.txt#L9"
true false
```

#### Keys need an order

A key type must have an order: `Text`, `Int`, the fixed-width integers, or a kind whose variants carry no data. A record has no order, so it cannot be a key. Key a map by sales, and the checker refuses:

```diff include="steps/18-maps..steps/19-record-key:src/stock.una" context="1" title="src/stock.una"
--- a/src/stock.una
+++ b/src/stock.una
@@ -21,2 +21,3 @@
   let edit stock: Map[Text, Int] = empty_map()
+  let edit by_sale: Map[Sale, Int] = empty_map()
   edit stock.set(key: "LAMP-01", value: 4)
```

```text include="steps/19-record-key/expected/rendered.txt#L1-L8"
[U2025] Error: a map's key type must satisfy `Ord`, and `Sale` does not
    ╭─[ src/stock.una:22:21 ]
    │
 22 │   let edit by_sale: Map[Sale, Int] = empty_map()
    │                     ───────┬──────
    │                            ╰──────── a map's key type must satisfy `Ord`, and `Sale` does not
    │
    │ Note: run `una explain U2025` for an explanation
```

The message says that the key type must satisfy `Ord`, the constraint of types with an order ([chapter 4](/learn/kinds/#s4-4)), and that `Sale` does not. A second message, at `empty_map()`, says the same thing about the map it would make. Key the map by a field that has an order instead, such as the SKU.

#### Cost

Each lookup, insertion and removal takes time in proportion to the logarithm of the number of entries, written O(log n). The time grows very slowly with the size of the map, where `first_where` on a list may look at every element.

### The operations of a map

| Operation | Gives | Notes |
| --- | --- | --- |
| `empty_map()` | a new map | its types come from where it is used |
| `m.len` | `Int` | the number of entries |
| `m.has(key: k)` | `Bool` | |
| `m.get(key: k)` | `Option[V]` | `None` for a missing key |
| `edit m.set(key: k, value: v)` | updates `m` | adds or replaces |
| `edit m.remove(key: k)` | updates `m` | |
| `m.with(key: k, value: v)` | a new map | `m` is unchanged |
| `m.without(key: k)` | a new map | `m` is unchanged |
| `m.keys()`, `m.values()`, `m.entries()` | lists | in key order |

### A map or a list

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Values in the order they arrived, repeats allowed | a list |
| One value per key, found by its key | a map |
| Totals or groups by a key you meet as you go | a map, with `get`, `or_else` and `set` |
| Output sorted by a key, every time | a map keyed by it |
| Values sorted by something a record holds | a map keyed by that field, then `values()` |
:::

### Check yourself: maps

Predict what these two lines print:

```una include="steps/17-map-forms/src/ledger.una#L35-L36" title="steps/17-map-forms/src/ledger.una"
  let tally = empty_map().with(key: "RUG-07", value: 1).with(key: "LAMP-01", value: 2).with(key: "RUG-07", value: 5)
  @console.print("{tally} {tally.len}")
```

:::answer Show the answer
```text include="steps/17-map-forms/expected/output.txt#L10"
{"LAMP-01": 2, "RUG-07": 5} 2
```

The second `with` on `RUG-07` replaces its value, so the map has two entries, not three, and `RUG-07` holds 5. The keys print in order, `LAMP-01` first, whatever order they were added in.
:::

## 5.6 JSON

### What JSON is

**JSON** is a way to write data as text, so that two programs can exchange it: a shop and its accounting service, a warehouse and a product feed. It has six kinds of value:

- `null`, which means "nothing";
- `true` and `false`;
- numbers, such as `1990` or `19.90`;
- strings, text between double quotes, such as `"LAMP-01"`;
- arrays, values in order between brackets, such as `["new", "sale"]`;
- objects, named fields between braces, such as `{"sku": "LAMP-01", "cents": 1990}`. Each field has a name, a string, and a value of any kind.

A product record of a feed is one object: `{"sku": "LAMP-01", "cents": 1990, "tags": ["new"]}`. Reading such text into a value the program can use is **parsing**, and writing a value out as text is **serializing**.

### Why JSON needs a parser

A JSON record is only text, and a program could try to read it by cutting the text, as a person might read it by eye. Here is a function that finds the price by taking what comes after the first comma and the next colon:

```una include="steps/20-json-by-hand/src/byhand.una" title="steps/20-json-by-hand/src/byhand.una" verified="check, run"
module byhand

--- The price in a product record, read by cutting the text: it expects the SKU first and the
--- price second, and nothing else.
price_by_hand(text: Text) -> Option[Int]
=
  let second = text.split(on: ",").at(index: 1).or_else(default: "")
  let value = second.split(on: ":").at(index: 1).or_else(default: "")
  value.replace(pattern: "\}", by: "").trim.to_int()

pub main() -> Unit
  uses @console: Console[print]
=
  let usual = "\{\"sku\": \"LAMP-01\", \"cents\": 1990\}"
  let reordered = "\{\"cents\": 1990, \"sku\": \"LAMP-01\"\}"
  let tagged = "\{\"sku\": \"LAMP-01\", \"tags\": [\"new\", \"sale\"], \"cents\": 1990\}"
  @console.print("{price_by_hand(usual)} {price_by_hand(reordered)} {price_by_hand(tagged)}")
```

`una run .` prints:

```text include="steps/20-json-by-hand/expected/output.txt"
Some(1990) None None
```

The first record works. The other two hold the same price, and the function finds nothing: in one the fields come in another order, which JSON allows, and in the other an array holds a comma of its own. Code that cuts text depends on how the sender happened to write it. A parser reads the text by the rules of JSON, whatever the order of the fields or the spaces, and says exactly where the text breaks those rules.

### How to read and write JSON

#### The kind `Json`

The prelude reads JSON into a value of the sum kind `Json`, with one variant for each kind of JSON value:

| JSON | Variant of `Json` | What it holds |
| --- | --- | --- |
| `null` | `Null` | nothing |
| `true`, `false` | `Boolean(value)` | a `Bool` |
| a whole number, such as `1990` | `Number(value)` | an `Int`, exact at any size |
| a number with a fraction or an exponent, such as `19.90` | `Decimal(text)` | the number as written in the input |
| a string | `Str(value)` | a `Text` |
| an array | `Array(items)` | a `List[Json]` |
| an object | `Object(fields)` | a `Map[Text, Json]`, so everything of [section 5.5](#s5-5) applies |

The step of this part reads one value of each kind, and `describe` has one arm per variant:

```una include="steps/21-json-forms/src/records.una#describe" title="steps/21-json-forms/src/records.una"
--- What a parsed value is: one arm for each variant of `Json`.
describe(json: Json) -> Text
=
  when json
    is Null -> "null"
    is Boolean(value) -> "yes or no: {value}"
    is Number(value) -> "a whole number: {value}"
    is Decimal(text) -> "a number with a fraction: {text}"
    is Str(value) -> "a string: {value}"
    is Array(items) -> "an array of {items.len} items"
    is Object(fields) -> "an object with the fields {fields.keys()}"
```

#### Parsing: `parse_json` and its clause

`text.parse_json()` parses a text. The text may not be JSON at all, so the call can **fail**: it ends without a value. Una makes you say, on the line under the call, what happens then. `if error use Null` carries on with `Null` in place of the value. [Chapter 6, Failure](/learn/failure/), explains this clause and the others.

```una include="steps/21-json-forms/src/records.una#L38-L42" title="steps/21-json-forms/src/records.una"
  let inputs = ["null", "true", "1990", "19.90", "\"LAMP-01\"", "[1, 2, 3]", "\{\"sku\": \"LAMP-01\", \"cents\": 1990\}"]
  for text in inputs
    let value = text.parse_json()
      if error use Null
    @console.print(describe(value))
```

```text include="steps/21-json-forms/expected/output.txt#L1-L7"
null
yes or no: true
a whole number: 1990
a number with a fraction: 19.90
a string: LAMP-01
an array of 3 items
an object with the fields ["cents", "sku"]
```

The inputs are Una texts. In Una text, `{` starts an interpolation, so a literal brace is written `\{` and `\}`, and a double quote is `\"`.

#### Reading a field: `when`, then `get`

A field is read in two steps. A `when` checks that the value is an object and binds its fields; then `get` reads one field, as on any map. Each step can find nothing, so each says what to do then. `tags` reads the array `tags` of a record, and keeps the strings in it:

```una include="steps/21-json-forms/src/records.una#tags" title="steps/21-json-forms/src/records.una"
--- The tags of a product record: the strings in its array `tags`, or `[]` when it has none.
tags(record: Json) -> List[Text]
=
  let listed = when record
    is Object(fields) -> fields.get(key: "tags").or_else(default: Null)
    else -> Null
  let items = when listed
    is Array(items) -> items
    else -> []
  let edit found: List[Text] = []
  for item in items
    when item
      is Str(value) ->
        found = found.append(item: value)
      else -> unit
  found
```

```una include="steps/21-json-forms/src/records.una#L43-L45" title="steps/21-json-forms/src/records.una"
  let record = "\{\"sku\": \"LAMP-01\", \"tags\": [\"new\", 7, \"sale\"]\}".parse_json()
    if error use Null
  @console.print("tags: {tags(record)} and {tags(Null)}")
```

```text include="steps/21-json-forms/expected/output.txt#L8"
tags: ["new", "sale"] and []
```

The `7` in the array is a `Number`, not a `Str`, so the `else` arm skips it. `Null`, which is not an object, has no tags.

#### Keeping the failure: `attempt` and `JsonError`

When a text is not JSON, the failure is a value of the kind `JsonError`, and each variant carries `at`, the position where reading stopped, counted in characters from 0:

- `Syntax(at)`: the first character where no valid JSON can continue, or the end of the text when it ends too early;
- `DuplicateKey(at)`: an object names the same field twice;
- `TooDeep(at)`: arrays and objects nest more than 512 levels deep;
- `NumberTooLong(at)`: a whole number of more than 4300 digits.

`attempt` keeps the outcome as a value instead of handling it on the spot ([chapter 6](/learn/failure/#s6-3)): `Ok` with the `Json`, or `Err` with the `JsonError`.

```una include="steps/21-json-forms/src/records.una#parsed" title="steps/21-json-forms/src/records.una"
--- A text read as JSON, kept as a value: `Ok` with the JSON, or `Err` with where it broke.
parsed(text: Text) -> Result[Json, JsonError] = attempt text.parse_json()
```

```una include="steps/21-json-forms/src/records.una#L46-L49" title="steps/21-json-forms/src/records.una"
  let trailing = parsed("[1, 2,]")
  let twice = parsed("\{\"sku\": \"LAMP-01\", \"sku\": \"RUG-07\"\}")
  let empty = parsed("")
  @console.print("{trailing} {twice} {empty}")
```

```text include="steps/21-json-forms/expected/output.txt#L9"
Err(Syntax(6)) Err(DuplicateKey(19)) Err(Syntax(0))
```

In `[1, 2,]`, position 6 is the `]` after the comma, where JSON wants another value. The second text names `sku` twice, and the second `sku` starts at position 19. The empty text ends before any value, at position 0.

#### Writing: build a `Json`, then `to_json`

To write JSON, build a `Json` value with the variants, and call `to_json`. An object is a `Map[Text, Json]` wrapped in `Object`:

```una include="steps/21-json-forms/src/records.una#L50-L56" title="steps/21-json-forms/src/records.una"
  let edit fields: Map[Text, Json] = empty_map()
  edit fields.set(key: "sku", value: Str(value: "LAMP-01"))
  edit fields.set(key: "tags", value: Array(items: [Str(value: "new"), Null]))
  edit fields.set(key: "on_sale", value: Boolean(value: false))
  @console.print(Object(fields).to_json())
  let note = "a \"bright\" lamp"
  @console.print(note.quote_json())
```

```text include="steps/21-json-forms/expected/output.txt#L10-L11"
{"on_sale":false,"sku":"LAMP-01","tags":["new",null]}
"a \"bright\" lamp"
```

`quote_json` writes one text as a JSON string, with its quotes escaped, for when you build JSON text yourself.

### Reading and writing a product feed

The forms together. The step parses two records of a product feed, reads a price, and writes JSON back:

:::steps
```una include="steps/22-json/src/feed.una" title="steps/22-json/src/feed.una" verified="check, run"
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

1. **`\{`, `\}` and `\"`.** JSON in a text literal: a literal brace is written `\{` and `\}`, and a quote is `\"`.
2. **`text.parse_json()` and `if error use Null`.** Parsing can fail, and the line under the call says what to do then: here, carry on with `Null`.
3. **`when record` with `is Object(fields)`.** Reading JSON is reading a sum kind: one arm for the variant you expect, and `else` for the rest. Then `fields.get(key: "cents")` is an ordinary map lookup, and `or_else(default: Null)` treats a missing field like a `null` one.
4. **`Object(fields).to_json()`.** Writing. `to_json` writes one canonical text: no spaces, and the keys of each object in order.
:::

`una run .` prints:

```text include="steps/22-json/expected/output.txt"
Object({"cents": Number(1990), "sku": Str("LAMP-01"), "tags": Array([Str("new")])})
Some(1990)
None
{"cents":1990,"in_stock":true,"sku":"LAMP-01"}
```

The first line is the interpolation of a `Json`, which shows the Una value, not JSON text. Note that the keys come out sorted: a JSON object is a map, so the order of the input is not kept. The second record has a trailing comma, which JSON does not allow, so it parses as `Null` and has no price.

### How JSON behaves

#### One way to write each value

`to_json` writes a value in one canonical form: no spaces, the fields of every object in key order, and strings escaped the same way every time. So equal values always give the same text, and the text of a value read and written back does not depend on how the sender spaced or ordered it.

#### Strict reading

`parse_json` reads exactly one JSON value, with spaces allowed around it, and nothing else. It refuses what JSON does not allow: comments, a comma after the last item, single quotes, `NaN`, a leading `+` or a leading zero on a number, and a field named twice.

#### Interpolation shows the Una value

`"{record}"` writes a `Json` in its Una form, such as `Object({"cents": Number(1990)})`, which helps when you debug. `to_json` writes JSON.

#### Numbers with a fraction

> [!WARNING]
> A JSON number with a fraction, such as `19.90`, is a `Decimal`, not a `Number`, so `is Number(value)` does not match it. Keep money in whole cents, in JSON as in Una.

#### Read once, then use typed values

A misspelt field name, such as `"cent"`, still checks: no checker knows which fields a text will hold, and `get` gives `None` at run time. So read the JSON in one place, into a record with typed fields, as the day-to-day program's `read_line` does, and let the rest of the program use the record. A misspelt field of a record does not check.

### Choosing how to read a field

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| A value of one variant, and nothing for the rest | `when` with that variant's arm and `else` |
| A field that may be missing, read as `Null` | `fields.get(key: k).or_else(default: Null)`, then `when` |
| A field with a sensible default | read it as an `Option`, then `or_else` |
| Every failure, with where the text broke | `attempt text.parse_json()`, then `when` on `Ok` and `Err` |
| JSON text from your own values | build a `Json`, then `to_json` |
:::

### Check yourself: JSON

These lines read a record and write it back. Predict the line they print:

```una include="steps/21-json-forms/src/records.una#L57-L60" title="steps/21-json-forms/src/records.una"
  let input = "\{\"sku\": \"RUG-07\", \"cents\": 4500, \"active\": true\}"
  let product = input.parse_json()
    if error use Null
  @console.print(product.to_json())
```

:::answer Show the answer
```text include="steps/21-json-forms/expected/output.txt#L12"
{"active":true,"cents":4500,"sku":"RUG-07"}
```

The record parses as an `Object`, whose fields form a map, so `to_json` writes them in key order, `active`, `cents`, `sku`, and with no spaces. The order of the input is not kept.
:::

## 5.7 Day-to-day: a daily sales report

### What the report must do

At the end of each day the shop exports its order lines, one JSON object per line. Some lines are incomplete. The report must read every line it can, say how many it skipped, total the units and the revenue of each category, name the best seller, and hand the totals to the accounting service as JSON.

The design follows from the data. The export is text, so each line is parsed on its own, and a bad line becomes `None` instead of stopping the report. The fields have types, so a `Line` record holds them once they are read, and nothing after `read_line` deals with JSON. The totals are per category and per SKU, so two maps hold them, and their key order gives the report its order.

The program is one module, and each part uses one idea of this chapter: records hold the fields, JSON and `Option` read them ([section 5.6](#s5-6) and [section 5.3](#s5-3)), a loop keeps the good lines ([section 5.2](#s5-2)), maps group them ([section 5.5](#s5-5)), and `fold` and `first_where` find the best seller ([section 5.4](#s5-4)). Here it is in parts.

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

This is the only part of the program that sees JSON. Two private helpers read one field each, as an `Option`: they use the reading form of [Reading a field](#reading-a-field-when-then-get), and give `None` when the field is missing or holds another kind of value. `read_line` parses the text, checks that it is an object, and builds a `Line` when the fields it needs are there.

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

A `for` loop over the export, with an accumulator, `lines`, declared before it with `let edit`. At each turn, a `when` over the `Option` that `read_line` gives appends the `Some` values. The `None` arm gives `unit`, the only value of the type `Unit`, and so does nothing: the line is skipped.

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

The default for a new category is a `Summary` with zeros, so the same lines handle the first line of a category and every later one. No list of categories is written anywhere: a category the store adds tomorrow gets its own entry the first time a line names it.

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

Two of the examples pin down what the report's output alone would hide. "on a tie, the first SKU in order is the best seller" builds the map with `RUG-07` first and expects `LAMP-01`, so it proves that the result follows the key order and not the order of insertion. "a day without sales has no best seller" checks the `None` arm of `headline`, a path the sample export never reaches.

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

*Why:* many languages read a position with brackets, so the hand writes them by habit. Una has no index syntax: reading a position can find nothing, so it is a function that returns an `Option`. The message reads the line as the parser does. `export` is a complete value, and after it the parser expected the line to end; the `[` is where it gave up.

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

*Why:* a plain `let` names one value for good, and only a binding declared `let edit` can take a new one. The loop assigns `lines` at each turn, and that assignment is what the checker refuses. The message names the binding and gives both ways to make it editable: a `let edit` binding, or an `edit` parameter, which [chapter 12](/learn/memory-and-concurrency/#s12-2) covers.

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

*Why:* `get` returns `Option[Int]`, and `+` needs an `Int`. The message names the operator, the type it needs, and the type it found. The checker does not guess what a missing SKU means: 0 is right here, but it would be wrong for a price.

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

*Why:* a `when` must cover every variant, and `None` is the day without sales. The message names the variant that has no arm, `None`, and the kind it belongs to; the help line offers the two repairs, an arm for it or an `else`.

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

*Why:* `sort` needs an order, and a record has none: should lines sort by SKU, by category, by price? In the message, `T` is the element type of the list, here `Line`, and `Ord` is the constraint of types with an order ([chapter 4](/learn/kinds/#s4-4)).

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

*Why:* a call that reads, such as `get`, needs no mark, so it is easy to forget that `set` is different. `set` changes the map, and every change is marked where it happens. The message names the operation and writes the call as it must be.

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

*Why:* `parse_json` can fail with `JsonError`, and a failure is handled on the line under the call. The message names the call, the kind it fails with, and the two ways to handle it: an `if error` clause, or `attempt`.

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

*Why:* JSON is full of braces, and in a Una text `{` starts an interpolation. The message says that the brace cannot start one here, and the help line gives the exact edit, with the line and the columns of the brace.

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
*Hint:* a map holds each key once and lists its keys in order, which is exactly "each once, in SKU order". Work in two steps. First keep only the lines of the category, with `filter` and a lambda that compares `line.category` with `category` ([section 5.4](#s5-4)). Then build a map keyed by SKU from those lines: the program already has a function that does, `units_by_sku`, and `keys()` lists its keys ([section 5.5](#s5-5)). The function's long form, with `=` on its own line, gives you room for a `let`.
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
*Hint:* a `for` loop over the export ([section 5.2](#s5-2)) with two `let edit` bindings declared before it: `number`, which counts the lines, and `numbers`, which collects the numbers of the bad ones. At each turn, add 1 to `number` first, so the first line is 1. Then call `read_line` on the text, and when its result is `None`, append `number` to `numbers`: `found is None` is a condition an `if` can test ([section 5.3](#s5-3)). Last, change the first `print` of `main` to show the list.
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
*Hint:* `sort` cannot sort a `Summary`, and the prelude has no `sort_by`, `reverse` or `concat`. A map lists its keys in ascending order, so let a map do the sorting. Key it by the revenue with its sign changed, `-summary.cents`, so that the largest revenue becomes the smallest key and comes first. Two categories can have the same revenue, so the value under each key is a list of names: `Map[Int, List[Text]]`, filled with the grouping pattern of [section 5.5](#s5-5), with `[]` as the default. Then walk `values()` and append every name of every list to one result list, with a loop inside a loop.
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
- A list holds values of one type, from position 0. `append` and `sort` return new lists; `at` and `first` read one.
- A binding that changes is `let edit`; a plain `let` names one value.
- `for x in xs` runs once per element; `a..b` includes `b`, `a..<b` does not. Without `while`, repeat with a range or recursion.
- `first`, `at`, `get`, `first_where` and `to_int` return an `Option`: use it with `when` or `or_else`.
- Use `map`, `filter`, `fold` and `first_where` for one-expression steps, and `for` for longer ones.
- Group with a map: `get` and `or_else`, then `edit m.set(...)`.
- A map lists its keys in order; its keys need an order.
- Parse JSON with a clause or `attempt`, read it with `when` and `get`, write it with `to_json`.
:::

### Reference

:::reference
- Construct pages: [`for`](/docs/language/control-flow/for/), [`let edit` and `edit` parameters](/docs/language/control-flow/let-edit/), [`when`](/docs/language/control-flow/when/), [`example`](/docs/language/examples/example/), [`if error` and `if none`](/docs/language/errors/if-error/)
- Standard library: [the prelude](/docs/std/) (`List`, `Option`, `append`, `set`, `at`, `first`, `is_empty`, `first_where`, `contains`, `sum`, `sort`, `map`, `filter`, `fold`, `or_else`, `is_some`, `to_int`, `max`), [maps](/docs/std/maps/) (`Map`, `Entry`, `empty_map`), [text](/docs/std/text/) (`join`, `chars`, `find`), [JSON](/docs/std/json/) (`Json`, `JsonError`, `parse_json`, `to_json`, `quote_json`)
- Diagnostics: [U0007](/docs/errors/U0007/), [U0101](/docs/errors/U0101/), [U0103](/docs/errors/U0103/) (a word Una does not use, such as `while`), [U1001](/docs/errors/U1001/), [U2001](/docs/errors/U2001/), [U2007](/docs/errors/U2007/), [U2019](/docs/errors/U2019/), [U2020](/docs/errors/U2020/), [U2025](/docs/errors/U2025/), [U3007](/docs/errors/U3007/)
- Specification: [the standard library](/docs/spec/14-standard-library/), [the memory model](/docs/spec/17-memory-model/) (`for`, ranges, `let edit`), [structured concurrency](/docs/spec/19-structured-concurrency/) (`together for`), [constraints on generics](/docs/spec/20-constraints-on-generics/), [maps](/docs/spec/21-maps/), [text](/docs/spec/22-text/), [JSON](/docs/spec/23-json/)
:::
