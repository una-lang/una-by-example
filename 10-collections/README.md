---
learn: "10"
title: Collections
editions: ["0.2"]
codes: [U0007, U0101, U2001, U2007, U2010, U2020, U2025, U3001, U3003, U3007, U3009]
time: 70
builds: A daily sales report that reads order lines from JSON, groups them by category and sums them up
prerequisites: ["4", "5", "6", "7", "8", "9"]
template: 2
nav: ["Lists", "Functions as values", "map, filter and fold", "Maps", "JSON", "Day-to-day: a daily sales report", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 10 Collections

Most of a working program handles data in groups: the lines of an order, the products of a catalog, the stock of each SKU, a batch of records that arrives as JSON text. A group of values held as one value is a **collection**. This chapter teaches the two collections Una has today, the list and the map. It also shows how to pass a function as a value, so that one call can apply a rule to every element of a list, and how to read and write JSON. It ends with a report that a store runs at the end of each day.

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

- build lists, and visit each of their elements with `for`;
- pass functions as values, and write lambdas, functions without a name;
- transform lists with `map`, `filter`, `fold` and `first_where`, and choose between them and a loop;
- count and group with a `Map`, whose keys come out in order;
- read fields from parsed JSON, and write JSON back.
:::

## Why it works this way

In many languages a collection is a shared object that anyone holding it may change. You pass a list to a function, and the function may add to it or sort it, so your list changes without a sign at the call. A lookup that finds nothing gives a special "null" value or stops the program, and its type does not say which. Parsed JSON often arrives as a loose dictionary, and a missing field shows up as a crash far from the line that read it.

Una makes each of these visible:

:::steps
1. **Collections are values.** `append` gives back a new list, and `with` a new map. A function that receives your list cannot change it, unless the call says so with `edit` ([section 16.2](/learn/memory/#s16-2)).
2. **A change is marked where it happens.** A name that changes is declared `let edit`, as in [section 9.2](/learn/loops/#s9-2), and a call that changes a map in place is written `edit stock.set(...)`.
3. **Absence is a type.** `first`, `at`, `get` and `first_where` give an `Option`, which you met in [section 7.1](/learn/failure/#s7-1), so the code says what happens when nothing is found.
4. **A function you pass keeps its promises.** The type of a function parameter says whether the function may fail or print, so a rule you hand to `map` cannot do more than its type allows.
5. **JSON is a sum kind.** A parsed value is a `Json`, with one variant for each kind of JSON value, and reading a field is a `when` and a lookup.
:::

> [!KEY]
> A list or a map is a value. You can pass it to any function and keep using it: it holds the same elements afterwards, unless the code says, with `edit`, that it changes.

## 10.1 Lists

### What a list is

A **list** is one value that holds several values of the same type, one after another. Think of the lines of a receipt: there may be one line or forty, they come in a fixed order, and each line is the same sort of thing. A list works the same way. The values it holds are its **elements**, and each element has a **position**, its place in the order.

A few words name the parts, and the rest of this chapter uses them:

- A **list literal** writes a list's elements between brackets, separated by commas: `[2, 1, 3]`. A literal is a value written out in the code, as `3` or `"LAMP-01"` is ([section 2.1](/learn/numbers/#s2-1)).
- The **type** of a list names the type of its elements: `List[Int]` is a list of whole numbers, and `List[Text]` a list of texts. `List` is a **generic** kind, as in [section 4.4](/learn/kinds/#s4-4): it takes another type between brackets, as `Option[Int]` does.
- A **position**, also called an **index**, counts from 0. In `[2, 1, 3]`, the element at position 0 is 2, and the element at position 2 is 3.
- The **length** of a list is how many elements it holds. `[2, 1, 3]` has a length of 3, and `[]`, the **empty list**, a length of 0.

The **prelude**, the set of functions every module has without importing anything ([section 3.2](/learn/text-and-conditions/#s3-2)), gives lists most of what a program needs: adding an element, adding up, sorting, searching. You call these functions with method syntax: `[2, 1, 3].sum()` is the call `sum([2, 1, 3])`.

### Why a program needs lists

Without a list, every value needs a name of its own. Here is a function that counts the units of a cart, with one parameter for each line of the cart:

```una include="steps/01-fixed-cart/src/cart.una" title="steps/01-fixed-cart/src/cart.una" verified="check, run"
module cart

--- The units in a cart of exactly three lines: one parameter for each line.
units_of_three(first: Int, second: Int, third: Int) -> Int = first + second + third

--- Prints the units of a cart of three lines.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{units_of_three(2, second: 1, third: 3)} units")
```

```text include="steps/01-fixed-cart/expected/output.txt"
6 units
```

It works for a cart of exactly three lines. A cart of four lines needs another function, with four parameters, and a cart of one line a third. A real cart may hold any number of lines, and the program learns that number only when it runs. A list solves that: `List[Int]` is one type for any number of quantities, so one name and one parameter hold the whole cart, and the functions of this chapter work on it whatever its length.

Each example of this chapter is a package, made as [chapter 2](/learn/numbers/#each-step-is-a-package) explains, and the chapter's download, `10-collections.tar.gz`, holds them all. Every package of this chapter uses edition `0.2`, the edition that brings maps, `sort`, `set`, JSON and the functions that take failing functions; a package of edition `0.1` has none of them.

### How to write a list: a cart and its receipt

Start with the quantities of a cart, then the SKUs on its receipt. A SKU, a stock-keeping unit, is the code a store gives each product, such as `LAMP-01`.

:::steps
```una include="steps/02-lists/src/cart.una" title="steps/02-lists/src/cart.una" verified="check, run"
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

1. **`[2, 1, 3]`.** A list literal. Every element has the same type, here `Int`, so the list is a `List[Int]`. You do not write the type: Una takes it from the elements.
2. **`quantities.append(item: 4)`.** This gives back a new list with `4` at the end. `quantities` itself does not change: the first line of the output shows both lists.
3. **`more.len`.** The number of elements, as on `Text`. `.len` is built in and is written without parentheses: `more.len()` does not check.
4. **`more.sum()` and `more.contains(item: 3)`.** The sum of a list of integers, and whether some element equals 3.
5. **`skus.sort().join(separator: ", ")`.** `sort` gives back the elements in ascending order, and `join` puts a list of texts together, with the separator between each two. The result of `sort` is a list, so `.join` can follow it on the same line.
6. **`receipt(skus: List[Text])`.** A parameter of a list type, written like any other parameter.
:::

`una run .` prints:

```text include="steps/02-lists/expected/output.txt"
[2, 1, 3] then [2, 1, 3, 4]
4 lines, 10 units
a line of 3 units: true
DESK-02, LAMP-01, RUG-07
```

A list in an interpolation is written as you would type it in Una, with brackets, and with quotes around texts.

### Visiting each element: `for` over a list

[Section 9.1](/learn/loops/#s9-1) walked ranges of numbers and the characters of a text with `for`. A `for` loop walks a list the same way: `for line in cart` runs its body once for each element, from the first to the last, and inside the body `line` names the element of that turn. Think of a cashier who scans the items of a basket one at a time: the same step, done once per item, in order.

The step of this part prints a shelf list and a receipt:

```una include="steps/03-for-lists/src/receipt.una#CartLine..total" title="steps/03-for-lists/src/receipt.una" verified="check"
--- One line of a cart: a SKU, how many units, and the price of one unit in cents.
kind CartLine
  sku: Text
  quantity: Int
  cents: Int

--- The total of a cart in cents: one turn of the loop for each line.
total(lines: List[CartLine]) -> Int
=
  let edit sum = 0
  for line in lines
    sum = sum + line.quantity * line.cents
  sum
```

```una include="steps/03-for-lists/src/receipt.una#main" title="steps/03-for-lists/src/receipt.una" verified="check, run"
--- Prints a shelf list, then a receipt with one line for each line of the cart.
pub main() -> Unit
  uses @console: Console[print]
=
  let skus = ["LAMP-01", "RUG-07", "DESK-02"]
  for sku in skus
    @console.print("on the shelf list: {sku}")
  let lamp = CartLine(sku: "LAMP-01", quantity: 2, cents: 1990)
  let rug = CartLine(sku: "RUG-07", quantity: 1, cents: 4500)
  let cart = [lamp, rug]
  for line in cart
    if line.quantity >= 2
      @console.print("{line.sku}: {line.quantity} units, bulk")
    else
      @console.print("{line.sku}: {line.quantity} unit")
  @console.print("total: {total(cart)} cents")
  let empty: List[CartLine] = []
  for line in empty
    @console.print("never printed: {line.sku}")
  @console.print("an empty cart: {total(empty)} cents")
  for sku in skus
    for size in ["S", "L"]
      @console.print("label {sku}-{size}")
```

`una run .` prints:

```text include="steps/03-for-lists/expected/output.txt"
on the shelf list: LAMP-01
on the shelf list: RUG-07
on the shelf list: DESK-02
LAMP-01: 2 units, bulk
RUG-07: 1 unit
total: 8480 cents
an empty cart: 0 cents
label LAMP-01-S
label LAMP-01-L
label RUG-07-S
label RUG-07-L
label DESK-02-S
label DESK-02-L
```

#### One element at a time

`for sku in skus` runs `@console.print` three times, once for each SKU, in the order of the list. `sku` is a new name in each turn, and it exists only inside the loop's body. It is a plain name: the body cannot assign it, since it is not `let edit`.

#### A running total over a list

`total` is the pattern of [section 9.2](/learn/loops/#s9-2) over a list: a `let edit` name declared before the loop, `sum`, updated at each turn, and given back after the loop. Here each turn adds what one line costs, its quantity times its price: 2 × 1990 + 1 × 4500 = 8480.

#### A choice at each turn

The body may hold any steps, here an `if` with two branches ([section 8.1](/learn/choices/#s8-1)): a line of two units or more is printed as bulk.

#### An empty list

A loop over an empty list runs its body zero times, so `never printed` never appears, and `total` gives back the value `sum` started with, 0. The empty list needs its type written, `List[CartLine]`, since it has no element to take one from.

#### A loop inside a loop

The last loop prints a label for each SKU in each size. The inner loop runs completely, for both sizes, at each turn of the outer one, so 3 SKUs and 2 sizes give 6 labels. A list literal such as `["S", "L"]` may stand right after `in`.

### What the prelude does with a list

The next step shows the other forms of a list, and the prelude's functions for lists. Its `main` prints one line per form:

```una include="steps/04-list-forms/src/shelf.una#Size..recount" title="steps/04-list-forms/src/shelf.una"
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

```una include="steps/04-list-forms/src/shelf.una#L18-L22" title="steps/04-list-forms/src/shelf.una"
  let empty: List[Text] = []
  let counts = [4, 0, 7]
  let sizes = [Large, Small, Medium]
  let aisles = [[1, 2], [3]]
  @console.print("{empty.len} {counts.len} {sizes.len} {aisles.len}")
```

```text include="steps/04-list-forms/expected/output.txt#L1"
0 3 3 2
```

- `[]` is the empty list. It has no element to take a type from, so you write the type on the name: `let empty: List[Text] = []`.
- `[4, 0, 7]` is a `List[Int]`, and its type comes from its elements.
- `[Large, Small, Medium]` holds variants of the sum kind `Size`, so it is a `List[Size]`.
- `[[1, 2], [3]]` is a list whose elements are lists: a `List[List[Int]]`, here two aisles with their shelf numbers.

Canonical form keeps a list literal on one line, however long it is.

#### Length and emptiness: `len` and `is_empty`

```una include="steps/04-list-forms/src/shelf.una#L23" title="steps/04-list-forms/src/shelf.una"
  @console.print("{empty.is_empty()} {counts.is_empty()}")
```

```text include="steps/04-list-forms/expected/output.txt#L2"
true false
```

`is_empty()` is `true` exactly when `len` is 0.

#### Reading one element: `first` and `at`

```una include="steps/04-list-forms/src/shelf.una#L24" title="steps/04-list-forms/src/shelf.una"
  @console.print("{counts.first()} {counts.at(index: 2)} {counts.at(index: 3)} {empty.first()}")
```

```text include="steps/04-list-forms/expected/output.txt#L3"
Some(4) Some(7) None None
```

`counts.first()` reads position 0, and `counts.at(index: 2)` reads position 2. Una has no `counts[2]` syntax. Both give an `Option`: `Some` with the element, or `None` when there is no element there, as for position 3 of a list of three, or the first element of an empty list. Use what they give with `when` or `or_else`, as [section 7.1](/learn/failure/#s7-1) shows.

#### Searching and adding up: `contains`, `sum` and `join`

```una include="steps/04-list-forms/src/shelf.una#L25-L26" title="steps/04-list-forms/src/shelf.una"
  let receipt = empty.join(separator: ", ")
  @console.print("{counts.contains(item: 0)} {counts.sum()} '{receipt}'")
```

```text include="steps/04-list-forms/expected/output.txt#L4"
true 11 ''
```

`contains(item: 0)` is `true` when some element equals 0. `sum()` adds up a list of numbers, and gives 0 for an empty list; like every `Int`, the sum has no upper limit. `join` on an empty list gives the empty text, which the quotes around it make visible.

#### Sorting: `sort`

```una include="steps/04-list-forms/src/shelf.una#L27" title="steps/04-list-forms/src/shelf.una"
  @console.print("{counts.sort()} {sizes.sort()}")
```

```text include="steps/04-list-forms/expected/output.txt#L5"
[0, 4, 7] [Small, Medium, Large]
```

`sort` gives back a new list in ascending order. It works on any type with an order, the constraint `Ord` of [section 4.4](/learn/kinds/#s4-4): `Int`, `Text`, the fixed-width integers, and sum kinds whose variants carry no data, in the order the variants are declared, which is why `Small` comes before `Large`. It is **stable**: elements that are equal keep the order they had. A record such as a cart line has no order of its own, and [Sorting records](#sorting-records-u2025) shows what the checker says when you try.

#### Replacing one element: `set`

`append` gives back a new list with one more element. To replace the element at a position, `set` changes a list in place:

```una include="steps/04-list-forms/src/shelf.una#L28" title="steps/04-list-forms/src/shelf.una"
  @console.print("{recount(counts, position: 1, counted: 5)} {counts}")
```

```text include="steps/04-list-forms/expected/output.txt#L6"
[4, 5, 7] [4, 0, 7]
```

`recount` copies its parameter into `let edit fixed`, a name it may change, then writes `edit fixed.set(index: position, item: counted)`. The word `edit` before the call marks the line where `fixed` changes: `set` takes its list as an `edit` parameter, which [section 16.2](/learn/memory/#s16-2) explains. `set` has a precondition, a position that exists: `0 <= index and index < xs.len`. So `recount` states the same condition in its `requires` line ([section 5.1](/learn/contracts/#s5-1)), and each caller of `recount` must meet it. The caller's `counts` keeps its values: the copy changed, not the original.

#### Comparing lists: `==`

```una include="steps/04-list-forms/src/shelf.una#L29" title="steps/04-list-forms/src/shelf.una"
  @console.print("{counts == [4, 0, 7]} {counts == [0, 4, 7]}")
```

```text include="steps/04-list-forms/expected/output.txt#L7"
true false
```

Two lists are equal when they hold equal elements in the same order. The same elements in another order make a different list.

### How a list behaves

#### Every element has the list's type

A list holds values of one type. Write a count as a word in the middle of a list of numbers:

```diff include="steps/04-list-forms..steps/05-mixed-list:src/shelf.una" context="1" title="src/shelf.una"
--- a/src/shelf.una
+++ b/src/shelf.una
@@ -18,3 +18,3 @@
   let empty: List[Text] = []
-  let counts = [4, 0, 7]
+  let counts = [4, "zero", 7]
   let sizes = [Large, Small, Medium]
```

`una check .` reports:

```text include="steps/05-mixed-list/expected/rendered.txt"
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

The first line names the problem: an element was expected to be an `Int`, and a `Text` was found. The mark points at `"zero"`, the element that does not fit; the list took its type, `Int`, from its first element. To keep values of several shapes in one list, declare a sum kind with one variant for each shape ([section 4.2](/learn/kinds/#s4-2)), and make the list a list of that kind.

#### A list is a value

A list never changes behind your back. `append` and `sort` give back new lists, and the list you called them on keeps its elements. A function that receives a list cannot change the caller's list: `recount` changed its own copy. A name changes only where the code says so: with `let edit` and an assignment, or with `edit` before a call.

#### Positions and absence

Positions count from 0, so the last element of a list of length n is at position n - 1. Reading a position never stops the program: `at` gives `None` for a position that is negative or past the end. That is why it gives an `Option`.

#### Adding at the end without copying

> [!NOTE]
> A list is a value: `append` gives back a new list, and the old one is unchanged for anyone who still holds it. When nothing else holds the list, una may reuse it and update it in place instead of copying it; whether it does is not something a program can observe, and the language does not promise it.

### A list, a loop or a function of the prelude

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Values in an order, the same value maybe twice | a list |
| A step for each element, such as printing it | `for x in xs` |
| A total, a test or a sorted copy | `sum`, `contains`, `sort` and the other prelude functions |
| One element, by its position | `at(index:)` or `first()`, which give an `Option` |
| A value found by a key, such as the stock of a SKU | a map, [section 10.4](#s10-4) |
:::

### Check yourself: lists

Read the two lines, and predict what they print before you open the answer:

```una include="steps/04-list-forms/src/shelf.una#L30-L31" title="steps/04-list-forms/src/shelf.una"
  let shelf = [3, 1, 2]
  @console.print("{shelf.append(item: 1).sort()} {shelf.len}")
```

:::answer Show the answer
```text include="steps/04-list-forms/expected/output.txt#L8"
[1, 1, 2, 3] 3
```

`append` gives back a new list, `[3, 1, 2, 1]`, and `sort` puts it in order; the two equal 1s both stay. `shelf` itself still has 3 elements, since `append` never changes the list it is called on.
:::

## 10.2 Functions as values, and lambdas

### What a function value is

So far, a function was something you call. In Una, a function is also a **value**, like a number or a text: you can pass it to another function as an argument, name it with `let`, and get it back as a result. Think of a recipe card. You can follow it yourself, but you can also hand the card to someone else and let them follow it when the time comes. Passing a function is handing over the card.

Two new terms name the parts:

- A **function type** is the type of a function value. `fn(Int) -> Int` is the type of every function that takes one `Int` and gives back an `Int`, whatever its name.
- A **lambda** is a function written in place, without a name, where a value goes: `fn(cents) -> cents - 500`. The name comes from mathematics; other books call it an anonymous function.

### Why pass a function

A store keeps changing its promotions. Here are three, each written as its own function:

```una include="steps/06-no-lambdas/src/rules.una" title="steps/06-no-lambdas/src/rules.una" verified="check, run"
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

```text include="steps/06-no-lambdas/expected/output.txt"
1550 1999 1640
0 299 240
```

Each function does two things: it applies its rule, and it keeps the result between 0 and the price, with `max` and `min` from the prelude (`min` gives the smaller of its two arguments, as `max` gives the larger). The second part is the same in all three, copied. A fourth promotion means a fourth copy, and a change to that part, such as a minimum price, must be made in every copy.

What differs between the three is only the rule. If the rule could be a parameter, the part that keeps the price in bounds would be written once, and each promotion would be just its rule. A function type makes that possible.

### How to write function values

#### A function type: `fn(Int) -> Int`

Write `fn`, the parameter types in parentheses, `->`, and the result type. A parameter of a function type is declared like any other parameter, and called like any function:

```una include="steps/07-lambdas/src/pricing.una#priced" title="steps/07-lambdas/src/pricing.una"
--- A price after a pricing rule: a function from a price in cents to a price in cents.
pub priced(cents: Int, rule: fn(Int) -> Int) -> Int = rule(cents)
```

`rule` is a parameter whose value is a function. `rule(cents)` calls whatever function the caller passed.

#### Passing a named function

Pass a declared function by its name, without parentheses: `priced(2_050, rule: ends_in_99)`. With parentheses, `ends_in_99(2_050)` would call it, and pass its result, a number. Without them, the function itself is passed, to be called later by `priced`. The function's type must match the parameter's: `ends_in_99` takes an `Int` and gives back an `Int`, so it fits `fn(Int) -> Int`.

#### A lambda

`fn(parameters) -> expression` writes a function in place:

```una include="steps/07-lambdas/src/pricing.una#L14" title="steps/07-lambdas/src/pricing.una"
  @console.print("{priced(2_050, rule: fn(cents) -> cents - 500)}")
```

`fn(cents) -> cents - 500` takes `cents` and gives `cents - 500`. Its parameter's type, `Int`, comes from the type of `rule`, so you need not write it. Its body is one expression, after `->`.

#### A lambda with its types written

Where nothing says what a lambda's parameters are, write their types, as in a header. A lambda named with `let` needs them:

```una include="steps/08-function-forms/src/promotions.una#L17-L18" title="steps/08-function-forms/src/promotions.una"
  let clearance = fn(cents: Int) -> cents - 500
  @console.print("clearance: {clearance(2_000)}")
```

```text include="steps/08-function-forms/expected/output.txt#L3"
clearance: 1500
```

`clearance` is now a name for a function, called like one: `clearance(2_000)`.

#### Several parameters

A function type may take several parameters, `fn(Int, Int) -> Int`, and a lambda then names each one. A function value is called with its arguments in order, with no labels, since its type gives its parameters no names:

```una include="steps/08-function-forms/src/promotions.una#line_price" title="steps/08-function-forms/src/promotions.una"
--- The price of a line under a rule for whole lines: a function of two parameters.
line_price(unit_cents: Int, units: Int, rule: fn(Int, Int) -> Int) -> Int = rule(unit_cents, units)
```

```una include="steps/08-function-forms/src/promotions.una#L13" title="steps/08-function-forms/src/promotions.una"
  @console.print("3 for 2: {line_price(1_990, units: 3, rule: fn(cents, units) -> cents * (units - units / 3))}")
```

```text include="steps/08-function-forms/expected/output.txt#L1"
3 for 2: 3980
```

The lambda prices "3 for 2": of 3 units, one is free, so the line pays 1990 × 2 = 3980.

#### A function that gives back a function

The result type can be a function type too. Such a function builds functions:

```una include="steps/08-function-forms/src/promotions.una#percent_off" title="steps/08-function-forms/src/promotions.una"
--- A promotion that takes `percent` percent off: a function that returns a function.
percent_off(percent: Int) -> fn(Int) -> Int = fn(cents) -> cents * (100 - percent) / 100
```

```una include="steps/08-function-forms/src/promotions.una#L14-L16" title="steps/08-function-forms/src/promotions.una"
  let ten_off = percent_off(10)
  let quarter_off = percent_off(25)
  @console.print("10 off: {ten_off(2_000)}, 25 off: {quarter_off(2_000)}")
```

```text include="steps/08-function-forms/expected/output.txt#L2"
10 off: 1800, 25 off: 1500
```

`percent_off(10)` gives back a lambda that takes 10 percent off, and `percent_off(25)` one that takes 25. The lambda uses `percent`, a parameter of the function that made it, and keeps its value after `percent_off` has returned.

### Pricing rules passed as values

The module `pricing` passes a named function and two lambdas to the same parameter:

:::steps
```una include="steps/07-lambdas/src/pricing.una" title="steps/07-lambdas/src/pricing.una" verified="check, run"
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

1. **`priced(cents: Int, rule: fn(Int) -> Int) -> Int = rule(cents)`.** A parameter of a function type, called like any function.
2. **`priced(2_050, rule: ends_in_99)`.** A named function passed as a value: no parentheses after its name, since it is not called here.
3. **`fn(cents) -> cents - 500`.** A lambda. Its parameter's type comes from the type of `rule`.
4. **`fn(cents) -> cents * markup / 100`.** A lambda that uses `markup`, a name from around it.
:::

`una run .` prints:

```text include="steps/07-lambdas/expected/output.txt"
1999
1550
2460
```

`priced` knows nothing about promotions: it applies whatever rule it is given. A new rule is a new function or a new lambda, and `priced` never changes.

### Functions that may fail

[Section 7.2](/learn/failure/#s7-2) showed `fails of p`, the header line that says a function fails when, and only when, its function parameter `p` fails. With function values in hand, here are the ways a function you pass may fail. The step of this part prices a cart with several price functions:

```una include="steps/10-fails-of/src/prices.una#PriceError..strict_total" title="steps/10-fails-of/src/prices.una" verified="check"
--- Why a price list has no price for a SKU.
kind PriceError = | NoPrice(sku: Text)

--- The store's price list. It knows two SKUs, and fails for any other.
listed(sku: Text) -> Int
  fails PriceError
=
  if sku == "LAMP-01"
    1990
  else if sku == "DESK-02"
    15900
  else
    fail NoPrice(sku)

--- The total of a cart, each SKU priced by `price`. It fails when, and only when, `price`
--- fails, and with the same error kind.
pub total_with(skus: List[Text], price: fn(Text) -> Int) -> Int
  fails of price
=
  let edit total = 0
  for sku in skus
    let cents = price(sku)
      if error pass
    total = total + cents
  total

--- The total of a cart, each SKU priced by `price`, whose type says that it may fail.
pub strict_total(skus: List[Text], price: fn(Text) -> Int fails PriceError) -> Int
  fails PriceError
=
  let edit total = 0
  for sku in skus
    let cents = price(sku)
      if error pass
    total = total + cents
  total
```

```una include="steps/10-fails-of/src/prices.una#L44-L53" title="steps/10-fails-of/src/prices.una"
  let cart = ["LAMP-01", "GIFT-50"]
  let flat = total_with(cart, price: fn(sku) -> 500)
  let no_gifts = total_with(cart, price: fn(sku) -> if sku.starts_with(prefix: "GIFT-") then fail NoPrice(sku) else 500)
    if error use -1
  let known = total_with(["LAMP-01", "DESK-02"], price: listed)
    if error use -1
  @console.print("{flat} {no_gifts} {known}")
  let strict = strict_total(["LAMP-01"], price: fn(sku) -> 500)
    if error use -1
  @console.print("strict: {strict}")
```

```text include="steps/10-fails-of/expected/output.txt#L1-L2"
1000 -1 17890
strict: 500
```

#### A lambda that fails, for a `fails of` parameter

`total_with` declares `fails of price`. So a lambda passed for `price` may fail, as its body says: `fn(sku) -> if sku.starts_with(prefix: "GIFT-") then fail NoPrice(sku) else 500` refuses gift cards with `fail`, and prices every other SKU at 500. The call then fails as the lambda does, and takes a clause, here `if error use -1`. The cart holds `GIFT-50`, so this call gives -1. A lambda that cannot fail, such as `fn(sku) -> 500`, needs no clause, and its call gives 1000.

A lambda's body is one line, so it cannot hold a clause under a call. A lambda whose body calls a function that can fail, such as `listed`, does not check; pass `listed` by its name instead, as the third call does.

#### `fails` in a function type

A function type may also say that the function fails: `fn(Text) -> Int fails PriceError`. `strict_total` takes such a parameter. Every call of `price` in its body may then fail, so `strict_total` declares `fails PriceError` itself, and every call of `strict_total` takes a clause, even with a function that never fails, as `fn(sku) -> 500`. That is why `fails of` exists: with it, a caller who passes a function that cannot fail writes no clause.

#### A failing lambda is passed, never kept

A lambda that can fail exists only as an argument: it can be passed, but not named with `let`, given back as a result or stored in a record. Name the gift-card rule with `let` before passing it:

```diff include="steps/10-fails-of..steps/11-failing-lambda-let:src/prices.una" context="1" title="src/prices.una"
--- a/src/prices.una
+++ b/src/prices.una
@@ -45,3 +45,4 @@
   let flat = total_with(cart, price: fn(sku) -> 500)
-  let no_gifts = total_with(cart, price: fn(sku) -> if sku.starts_with(prefix: "GIFT-") then fail NoPrice(sku) else 500)
+  let no_gifts_rule = fn(sku: Text) -> if sku.starts_with(prefix: "GIFT-") then fail NoPrice(sku) else 500
+  let no_gifts = total_with(cart, price: no_gifts_rule)
     if error use -1
```

```text include="steps/11-failing-lambda-let/expected/rendered.txt#L1-L6"
[U3009] Error: this code declares no error kind, so it cannot fail with `NoPrice`; declare `fails` in its header
    ╭─[ src/prices.una:46:86 ]
    │
 46 │   let no_gifts_rule = fn(sku: Text) -> if sku.starts_with(prefix: "GIFT-") then fail NoPrice(sku) else 500
    │                                                                                      ───┬───
    │                                                                                         ╰───── this code declares no error kind, so it cannot fail with `NoPrice`; declare `fails` in its header
```

The message says that the code declares no error kind: a lambda named with `let` has no type that lets it fail, so it is pure, and its `fail` is refused. Write the lambda at the call, or declare a named function with `fails PriceError` and pass its name.

### A promotion that cannot overcharge

A shipping report of the store charges each order by weight and zone, then applies promotions. The promotions go through one function, `promoted`, which keeps every charge between 0 and the charge before the promotion:

```una include="steps/12-shipping-quotes/src/shipping.una#half_off..promoted" title="steps/12-shipping-quotes/src/shipping.una" verified="check"
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

```una include="steps/12-shipping-quotes/src/shipping.una#L71-L76" title="steps/12-shipping-quotes/src/shipping.una"
  let charge = quote(4_500, grams: 3_200, zone: 3)
  show(1044, charge)
  let weekend = promoted(charge, promotion: half_off)
  show(1045, charge: weekend)
  let members = promoted(lamps, promotion: fn(cents) -> cents * 80 / 100)
  show(1046, charge: members)
```

```text include="steps/12-shipping-quotes/expected/output.txt#L3-L5"
order 1044: 30.90
order 1045: 15.45
order 1046: 6.32
```

This is the design that [Why pass a function](#why-pass-a-function) asked for. `max` and `min` are written once, in `promoted`, and its `ensures` line promises every caller a charge from 0 to `charge`, whatever the promotion computes. `half_off` is passed by its name, and the members' rule of 20 percent off as a lambda, on `lamps`, the 790 cents of order 1042: 790 × 80 / 100 = 632, printed as 6.32. The day-to-day program of this chapter passes lambdas in the same way, to `map`, `fold` and `first_where`.

### How function values behave

#### Where a lambda gets its types

A lambda gets its parameter types from where it is used: the parameter it is passed to says `fn(Int) -> Int`, so `cents` is an `Int`. Named with `let` on its own line, a lambda has no such place, and the checker asks for the type, with U2010 ([A lambda named with `let`](#a-lambda-named-with-let-u2010), in Common mistakes). Write `fn(cents: Int) -> …`, or pass the lambda straight to the function that uses it.

#### A lambda captures values

A lambda may use names from around it, such as `markup` or `percent`. It **captures** them: it keeps a copy of the value each one has when the lambda is made. A later assignment to a `let edit` name does not reach a lambda made before it, and the lambda cannot assign the name itself. A lambda's parameter cannot take a name already used around it, since Una gives a name one meaning in a block ([section 9.2](/learn/loops/#s9-2)).

#### A function type without `uses` is pure

`fn(Int) -> Int` has no `uses`, so a function of that type cannot print or touch anything outside the program. Pass a function that prints where such a type is expected, and the call does not check:

```diff include="steps/07-lambdas..steps/09-lambda-prints:src/pricing.una" title="src/pricing.una" context="1"
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

```text include="steps/09-lambda-prints/expected/rendered.txt#L12-L17"
[U3003] Error: this function uses `@console: ?[print]`, which the expected function type does not allow
    ╭─[ src/pricing.una:19:40 ]
    │
 19 │   @console.print("{priced(2_050, rule: logged)}")
    │                                        ───┬──
    │                                           ╰──── this function uses `@console: ?[print]`, which the expected function type does not allow
```

The mark points at `logged`, where it is passed: it uses `@console`, which `fn(Int) -> Int` does not allow. In `@console: ?[print]`, the `?` stands for the capability's type, `Console`, which the checker does not name in this message. A first diagnostic, U3001, says that no caller of `logged` gives it the console, since it is only passed, never called from `main`. So a promotion passed to `priced` is a pure function, whoever wrote it: its type guarantees it. A function may also accept a parameter that prints, with the header line `uses of`, which [section 12.4](/learn/capabilities/#s12-4) teaches.

#### A lambda's body is one expression

A lambda holds one expression, on one line. A rule that needs several lines, a `let` or a clause is a named function, passed by its name. A named function can also have its own examples, which a lambda cannot.

#### Functions cannot be compared

`==` compares two values of the same type, but not two functions: whether two functions always give the same answer is not something a program can decide. Comparing two functions with `==` is U2001, whose message says that the values hold functions. Compare what the functions give back instead.

### A named function or a lambda

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A rule used in several places, or one worth an example | A named function, passed by its name |
| A one-line rule used once, at the call | A lambda, `fn(x) -> …` |
| A rule that reads a value from around the call | A lambda, which captures it |
| A rule that needs several lines, or calls a function that can fail | A named function |
| A family of rules that differ by a number, such as a percentage | A function that gives back a lambda, such as `percent_off` |
| A parameter that may fail exactly when its argument does | `fails of` the parameter |
:::

Lists use function values everywhere: `map`, `filter` and `fold`, in [section 10.3](#s10-3), take a function that says what to do with each element.

### Check yourself: function values

`main` in `promotions` builds one more rule out of `ten_off`:

```una include="steps/08-function-forms/src/promotions.una#L19-L20" title="steps/08-function-forms/src/promotions.una"
  let twice = fn(cents: Int) -> ten_off(ten_off(cents))
  @console.print("10 off twice: {twice(1_000)}")
```

Predict what it prints.

:::answer Show the answer
```text include="steps/08-function-forms/expected/output.txt#L4"
10 off twice: 810
```

`twice` calls `ten_off` on the result of `ten_off`. 1000 less 10 percent is 900, and 900 less 10 percent is 810.
:::

Then `main` makes a lambda that reads an editable name, and changes the name:

```una include="steps/08-function-forms/src/promotions.una#L21-L24" title="steps/08-function-forms/src/promotions.una"
  let edit markup = 120
  let raised = fn(cents: Int) -> cents * markup / 100
  markup = 200
  @console.print("markup: {raised(1_000)}, markup now {markup}")
```

Predict the line it prints.

:::answer Show the answer
```text include="steps/08-function-forms/expected/output.txt#L5"
markup: 1200, markup now 200
```

`raised` captured `markup` when it was made, with the value 120, so it gives 1000 × 120 / 100 = 1200. The assignment of 200 changes the name, which the last part of the line shows, but not the value the lambda keeps.
:::

## 10.3 Functions over lists: `map`, `filter` and `fold`

### What a function over a list is

A loop says *how* to walk a list: start a name, visit each element, update the name. Most walks have one of a few shapes, and the prelude has a function for each shape. You give it the list and the one step that differs, and it does the walking.

Think of instructions to a stock clerk. "Put a new price tag on every item" changes each item. "Pull every item past its date" keeps some items. "Count the units on the shelf" turns many items into one number. "Find me the first blue mug" stops at a match. Each instruction names one shape of work and one rule. In Una, these are `map`, `filter`, `fold` and `first_where`, and the rule is a function you pass to them, often a lambda.

A function that takes another function as an argument is a **higher-order function**. `priced` of [section 10.2](#s10-2) is one, and so are the four of this section.

### Why the prelude walks the list for you

Here are three loops over a cart: one prices each line, one leaves out the gift cards, and one counts the units.

```una include="steps/13-loops-repeat/src/cart.una#line_totals..units" title="steps/13-loops-repeat/src/cart.una"
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

```text include="steps/13-loops-repeat/expected/output.txt"
[3980, 5000] 1 3
```

They work, and they are almost the same code. Each declares a name that starts empty or at 0, walks the list, updates the name, and gives it back. Only one line in each says what the function is for. A reader has to read all of them to find that line, and each copy of the walk is one more place to get the start value or the update wrong. With the prelude's functions, the walk is written once, in the prelude, and your code keeps only the line that matters.

### How to write `map`, `filter`, `fold` and `first_where`

Each one is called with method syntax on a list, and takes its function under a label that says what the function does: `each`, `keep` or `step`. The step for this part works on prices and SKUs:

```una include="steps/14-list-functions/src/prices.una#L1-L11" title="steps/14-list-functions/src/prices.una"
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

```una include="steps/14-list-functions/src/prices.una#L12-L14" title="steps/14-list-functions/src/prices.una"
  @console.print("map: {prices.map(each: with_tax)}")
  @console.print("map: {skus.map(each: fn(sku) -> sku.to_lower())}")
  @console.print("map: {prices.map(each: fn(cents) -> cents >= 2000)}")
```

```text include="steps/14-list-functions/expected/output.txt#L1-L3"
map: [2189, 4950, 935]
map: ["lamp-01", "rug-07", "mug-11"]
map: [false, true, false]
```

`with_tax` is passed by name, without parentheses: you hand over the function, and `map` calls it. 1990 plus a tenth, rounded down, is 2189.

#### Some of the elements: `filter(keep:)`

`filter` keeps the elements for which its function gives `true`, in their order. The function must give a `Bool`.

```una include="steps/14-list-functions/src/prices.una#L15-L18" title="steps/14-list-functions/src/prices.una"
  let limit = 2000
  let above = prices.filter(keep: fn(cents) -> cents >= limit)
  let mugs = skus.filter(keep: fn(sku) -> sku.starts_with(prefix: "MUG"))
  @console.print("filter: {above} {mugs}")
```

```text include="steps/14-list-functions/expected/output.txt#L4"
filter: [4500] ["MUG-11"]
```

The first lambda reads `limit`, a name declared outside it, as it was when the lambda was made.

#### One value from all the elements: `fold(initial:, step:)`

`fold` carries one value from the first element to the last. It starts from `initial`. At each element it calls `step` with two arguments, the value so far and the element, and the step's result becomes the new value so far. The last value is the result.

```una include="steps/14-list-functions/src/prices.una#L19-L21" title="steps/14-list-functions/src/prices.una"
  let total = prices.fold(initial: 0, step: fn(sum, cents) -> sum + cents)
  let top = prices.fold(initial: 0, step: fn(best, cents) -> max(best, b: cents))
  @console.print("fold: {total} and {top}")
```

```text include="steps/14-list-functions/expected/output.txt#L5"
fold: 7340 and 4500
```

The first `fold` adds up: 0 + 1990 = 1990, + 4500 = 6490, + 850 = 7340. The second keeps the largest price seen so far with `max`, whose second parameter is named `b`. The value so far may have any type, the same for `initial`, the step's first parameter, and its result.

#### The first match: `first_where(keep:)`

`first_where` gives the first element for which its function gives `true`, as an `Option`, and stops there. When no element matches, it gives `None`.

```una include="steps/14-list-functions/src/prices.una#L22-L24" title="steps/14-list-functions/src/prices.una"
  let rug = skus.first_where(keep: fn(sku) -> sku.starts_with(prefix: "RUG"))
  let desk = skus.first_where(keep: fn(sku) -> sku.starts_with(prefix: "DESK"))
  @console.print("first_where: {rug} and {desk}")
```

```text include="steps/14-list-functions/expected/output.txt#L6"
first_where: Some("RUG-07") and None
```

#### One after another: chaining

The result of one call is a list, so the next call can follow it with another dot. Read a chain from left to right: keep the prices under 2000, add tax to each, and add them up.

```una include="steps/14-list-functions/src/prices.una#L25-L26" title="steps/14-list-functions/src/prices.una"
  let cheap = prices.filter(keep: fn(cents) -> cents < 2000).map(each: with_tax).sum()
  @console.print("chained: {cheap}")
```

```text include="steps/14-list-functions/expected/output.txt#L7"
chained: 3124
```

1990 and 850 are under 2000; with tax they are 2189 and 935, and their sum is 3124.

### Pricing a cart without a loop

The tools together, in a store example. The step prices a cart, counts its units, and decides whether it ships free:

:::steps
```una include="steps/15-higher-order/src/pricing.una" title="steps/15-higher-order/src/pricing.una" verified="check, run"
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

1. **`cart.map(each: line_cents)`.** A function declared with a name is passed by that name.
2. **`fn(line) -> line.quantity >= 2`.** A lambda. Its parameter's type, `CartLine`, comes from the list it is used on.
3. **`fold(initial: 0, step: fn(sum, line) -> sum + line.quantity)`.** The step takes the value so far and the next element. Here it counts units; `initial` is the result for an empty cart.
4. **`ships_free`.** The same tools in a function: leave out the gift cards, price each line, add up, compare. Each step is one call, and the result of one is the input of the next.
:::

`una run .` prints:

```text include="steps/15-higher-order/expected/output.txt"
[3980, 4500, 5000]
["LAMP-01"]
4 units
free shipping: false
```

The three loops of [Why the prelude walks the list for you](#why-the-prelude-walks-the-list-for-you) are each one call here: `map(each: line_cents)`, a `filter`, and a `fold`.

### How the functions behave

#### Order, and how often the function is called

`map`, `filter`, `fold` and `first_where` call their function on the elements from first to last, once per element. `first_where` stops after the first element it accepts, so the elements after it are never tested.

#### Functions over an empty list

Each one has a plain answer for an empty list. `map` gives `[]`, `fold` gives its `initial` value, `first_where` gives `None`, and `sum` gives 0:

```una include="steps/14-list-functions/src/prices.una#L27-L30" title="steps/14-list-functions/src/prices.una"
  let doubled = empty.map(each: fn(cents) -> cents * 2)
  let counted = empty.fold(initial: 0, step: fn(sum, cents) -> sum + cents)
  let first_big = empty.first_where(keep: fn(cents) -> cents > 0)
  @console.print("empty: {doubled} {counted} {first_big}")
```

```text include="steps/14-list-functions/expected/output.txt#L8"
empty: [] 0 None
```

So choose `initial` as the right answer for "nothing": 0 for a total, and for a largest value, one that no element can be below, such as 0 for prices.

#### The function must fit

The function you pass must take the element's type and give what the call needs. `filter` needs a `Bool` from `keep`. Give it a number instead:

```diff include="steps/14-list-functions..steps/16-filter-result:src/prices.una" context="1" title="src/prices.una"
--- a/src/prices.una
+++ b/src/prices.una
@@ -15,3 +15,3 @@
   let limit = 2000
-  let above = prices.filter(keep: fn(cents) -> cents >= limit)
+  let above = prices.filter(keep: fn(cents) -> cents - limit)
   let mugs = skus.filter(keep: fn(sku) -> sku.starts_with(prefix: "MUG"))
```

`una check .` reports:

```text include="steps/16-filter-result/expected/rendered.txt"
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

#### A function that can fail

`map`, `filter`, `fold` and `first_where` declare `fails of` their function, as `total_with` of [section 10.2](#s10-2) does. So you may pass them a function that can fail, such as `listed`, and the call then takes a clause:

```una include="steps/10-fails-of/src/prices.una#L54-L58" title="steps/10-fails-of/src/prices.una"
  let found = ["LAMP-01", "DESK-02"].map(each: listed)
    if error use []
  let unknown = ["LAMP-01", "VASE-03"].map(each: listed)
    if error use []
  @console.print("map: {found} {unknown}")
```

```text include="steps/10-fails-of/expected/output.txt#L3"
map: [1990, 15900] []
```

The first list has a price for each SKU. In the second, `listed` fails at `VASE-03`, and `map` stops at that first failure: the whole call fails, and the clause gives `[]`. A function that cannot fail needs no clause, as in every other call of this section.

#### What a lambda can see

A lambda sees the values of the names around it as they were when it was made, and it cannot assign a `let edit` name outside it: its body is one expression, not a list of steps. To build up a value, use `fold`, or a `for` loop.

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
| A step for each element that prints | `for` |
:::

The rows with two answers have two right answers. Choose the one a reader follows faster: a `fold` with a one-line step, or a loop when the step needs room.

### Check yourself: functions over lists

Predict what this prints before you open the answer:

```una include="steps/14-list-functions/src/prices.una#L31-L33" title="steps/14-list-functions/src/prices.una"
  let picked = [5, 12, 8].filter(keep: fn(units) -> units > 6).map(each: fn(units) -> units * 2)
  let longest = skus.fold(initial: 0, step: fn(best, sku) -> max(best, b: sku.len))
  @console.print("question: {picked} {longest}")
```

:::answer Show the answer
```text include="steps/14-list-functions/expected/output.txt#L9"
question: [24, 16] 7
```

`filter` keeps 12 and 8, the units above 6, in their order, and `map` doubles each: `[24, 16]`. The `fold` keeps the longest length seen so far: `LAMP-01` has 7 characters, `RUG-07` 6 and `MUG-11` 6, so the result is 7.
:::

## 10.4 Maps

### What a map is

A **map** holds values under keys. Think of a stock ledger: each SKU has one line, and the line says how many units are on hand. You never read the ledger from the top to find a SKU; you go to its line. A map works the same way. Each **key**, here a SKU, appears once, and leads to one **value**, here the units. A key together with its value is an **entry**.

`Map[K, V]` is the type of a map whose keys have the type `K` and whose values have the type `V`. The stock of each SKU is a `Map[Text, Int]`. The units sold in each category are a `Map[Text, Int]` too, and the summary of each category, in the day-to-day program, a `Map[Text, Summary]`.

### Why a program needs maps

Count the units sold in each category with what this chapter has shown so far: a list of the categories, and a `filter` and a `sum` for each one.

```una include="steps/17-groups-by-hand/src/sales.una" title="steps/17-groups-by-hand/src/sales.una" verified="check, run"
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

```text include="steps/17-groups-by-hand/expected/output.txt"
lighting: 5
textiles: 1
10 units sold in all
```

The totals by category add up to 6, and the store sold 10 units. The 4 units of `SPADE-02` are lost, because nobody wrote `"garden"` into the list of categories. The code has to know every category in advance. It is also slow on a real day: it walks every sale once for each category, so 1,000 sales in 50 categories take 50,000 tests. A map fixes both. You add each sale to its category's entry as you meet it, so a new category gets an entry by itself, and each sale is visited once.

### How to write and use a map

The step of this part keeps a ledger. Its `main` prints one line per group of operations:

```una include="steps/18-map-forms/src/ledger.una#stock_after_day" title="steps/18-map-forms/src/ledger.una"
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

A map starts empty. `empty_map()` makes one, and takes its key and value types from the name it is given to, so write them there: `let edit stock: Map[Text, Int] = empty_map()`.

```una include="steps/18-map-forms/src/ledger.una#L17-L19" title="steps/18-map-forms/src/ledger.una"
  let empty: Map[Text, Int] = empty_map()
  let stock = stock_after_day()
  @console.print("{empty} {empty.len} / {stock} {stock.len}")
```

```text include="steps/18-map-forms/expected/output.txt#L1"
{} 0 / {"DESK-02": 1, "LAMP-01": 3} 2
```

A map in an interpolation is written between braces, `{}` when empty, and `m.len` is its number of entries. `stock_after_day` set `LAMP-01` twice and removed `VASE-03`, so two entries are left.

#### Changing a map in place: `edit m.set` and `edit m.remove`

`edit stock.set(key: "LAMP-01", value: 4)` adds the key with its value, or replaces the value when the key is already there. `edit stock.remove(key: "VASE-03")` takes the key out. Both change the map in place, so:

- the name is declared `let edit`, since only an editable name may change ([section 9.2](/learn/loops/#s9-2));
- the call starts with the word `edit`, which marks the line where the map changes, as for a list's `set` ([section 16.2](/learn/memory/#s16-2) explains `edit` at a call);
- the call stands alone on its line, as a step: it gives no value.

In `stock_after_day`, the fourth line sets `LAMP-01` again, to 3, so the map keeps one entry for it.

#### A new map from an old one: `with` and `without`

`stock.with(key: "RUG-07", value: 9)` gives a new map with one more entry, or one changed entry, and `without` a new map with one key fewer. The map you call them on does not change, so they need no `edit`:

```una include="steps/18-map-forms/src/ledger.una#L20-L22" title="steps/18-map-forms/src/ledger.una"
  let restocked = stock.with(key: "RUG-07", value: 9)
  let retired = restocked.without(key: "DESK-02")
  @console.print("{restocked} {retired} {stock}")
```

```text include="steps/18-map-forms/expected/output.txt#L2"
{"DESK-02": 1, "LAMP-01": 3, "RUG-07": 9} {"LAMP-01": 3, "RUG-07": 9} {"DESK-02": 1, "LAMP-01": 3}
```

The last of the three maps is `stock`, unchanged.

#### Reading: `get` and `has`

`get` gives an `Option`: `Some` with the value, or `None` for a key the map does not hold. `has` answers only whether the key is there.

```una include="steps/18-map-forms/src/ledger.una#L23-L27" title="steps/18-map-forms/src/ledger.una"
  let lamps = stock.get(key: "LAMP-01")
  let vases = stock.get(key: "VASE-03")
  let has_desks = stock.has(key: "DESK-02")
  let has_vases = stock.has(key: "VASE-03")
  @console.print("{lamps} {vases} {has_desks} {has_vases}")
```

```text include="steps/18-map-forms/expected/output.txt#L3"
Some(3) None true false
```

#### Listing: `keys`, `values` and `entries`

`keys()` and `values()` give lists, and `entries()` a list of `Entry` records, each with the fields `key` and `value`. A `for` loop over `entries()` visits each key with its value:

```una include="steps/18-map-forms/src/ledger.una#L28-L30" title="steps/18-map-forms/src/ledger.una"
  @console.print("{restocked.keys()} {restocked.values()}")
  for entry in restocked.entries()
    @console.print("{entry.key} has {entry.value}")
```

```text include="steps/18-map-forms/expected/output.txt#L4-L7"
["DESK-02", "LAMP-01", "RUG-07"] [1, 3, 9]
DESK-02 has 1
LAMP-01 has 3
RUG-07 has 9
```

### Stock by SKU

The forms together. The step keeps the stock of each SKU, and groups sales by category:

:::steps
```una include="steps/19-maps/src/stock.una" title="steps/19-maps/src/stock.una" verified="check, run"
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
2. **`edit stock.set(key: "LAMP-01", value: 4)`.** `set` adds the key, or replaces its value. It changes the map, so the name is `let edit`, and the call starts with `edit`.
3. **`stock.with(key: "RUG-07", value: 9)`.** The value form: a new map with one more entry. `stock` keeps its two entries, as the first line of the output shows.
4. **`stock.get(key: "VASE-03")`.** `get` gives an `Option`: `None` for a key the map does not hold. A missing key is not an error.
5. **`totals.get(key: sale.category).or_else(default: 0)`.** The grouping pattern: read the total so far, with `0` for a category not seen yet, then `set` the new total. You will meet it again in the day-to-day program.
:::

`una run .` prints:

```text include="steps/19-maps/expected/output.txt"
{"DESK-02": 1, "LAMP-01": 4} and {"DESK-02": 1, "LAMP-01": 4, "RUG-07": 9}
Some(4) None
["DESK-02", "LAMP-01", "RUG-07"]
lighting: 5
textiles: 1
```

`units_by_category` needs no list of categories. The first sale of a category finds no entry, starts from 0, and creates one; every later sale of it adds to that entry.

### How a map behaves

#### Entries in key order

A map keeps its entries ordered by key, from the smallest up, not in the order you added them. `keys()`, `values()` and `entries()` all list them in that order, and so does interpolation. Texts order character by character, and numbers by value:

```una include="steps/18-map-forms/src/ledger.una#L31-L32" title="steps/18-map-forms/src/ledger.una"
  let aisles = empty_map().with(key: 12, value: "garden").with(key: 3, value: "lighting")
  @console.print("{aisles}")
```

```text include="steps/18-map-forms/expected/output.txt#L8"
{3: "lighting", 12: "garden"}
```

The key 12 was added first, and 3 still comes first. So a report built from a map comes out sorted by key, with no `sort` call, and the same input always gives the same output.

#### One value per key

A key appears once. `set` and `with` on a key that is there replace its value, so the length stays the same. To keep several values under one key, make the value a list, as `Map[Int, List[Text]]` in [exercise 3](#exercise-3-categories-by-revenue).

#### A missing key is not an error

`get` on a missing key gives `None`, and `remove` or `without` on a missing key leaves the map as it is. Neither stops the program.

#### Maps are values, and compare by content

`with` and `without` never change the map they are called on, and `set` and `remove` change only the name they are written on. Two maps are equal when they hold the same keys with equal values:

```una include="steps/18-map-forms/src/ledger.una#L33-L34" title="steps/18-map-forms/src/ledger.una"
  let same = restocked.without(key: "DESK-02")
  @console.print("{retired == same} {retired == stock}")
```

```text include="steps/18-map-forms/expected/output.txt#L9"
true false
```

#### Keys need an order

A key type must have an order, the constraint `Ord`: `Text`, `Int`, the fixed-width integers, or a sum kind whose variants carry no data. A record has no order, so it cannot be a key. Key a map by sales, and the checker refuses:

```diff include="steps/19-maps..steps/20-record-key:src/stock.una" context="1" title="src/stock.una"
--- a/src/stock.una
+++ b/src/stock.una
@@ -21,2 +21,3 @@
   let edit stock: Map[Text, Int] = empty_map()
+  let edit by_sale: Map[Sale, Int] = empty_map()
   edit stock.set(key: "LAMP-01", value: 4)
```

```text include="steps/20-record-key/expected/rendered.txt#L1-L8"
[U2025] Error: a map's key type must satisfy `Ord`, and `Sale` does not
    ╭─[ src/stock.una:22:21 ]
    │
 22 │   let edit by_sale: Map[Sale, Int] = empty_map()
    │                     ───────┬──────
    │                            ╰──────── a map's key type must satisfy `Ord`, and `Sale` does not
    │
    │ Note: run `una explain U2025` for an explanation
```

The message says that the key type must satisfy `Ord`, the constraint of types with an order ([section 4.4](/learn/kinds/#s4-4)), and that `Sale` does not. A second message, at `empty_map()`, says the same thing about the map it would make. Key the map by a field that has an order instead, such as the SKU.

#### Cost

Each lookup, insertion and removal takes time in proportion to the logarithm of the number of entries, written O(log n). The time grows very slowly with the size of the map: a map of a million entries takes about twice the steps of a map of a thousand, where `first_where` on a list may look at every element.

### The operations of a map

| Operation | Gives | Notes |
| --- | --- | --- |
| `empty_map()` | a new map | its types come from where it is used |
| `m.len` | `Int` | the number of entries |
| `m.has(key: k)` | `Bool` | |
| `m.get(key: k)` | `Option[V]` | `None` for a missing key |
| `edit m.set(key: k, value: v)` | changes `m` | adds or replaces |
| `edit m.remove(key: k)` | changes `m` | |
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

More collections, such as queues, stacks and sets, are coming to Una; until then, the list and the map cover the programs of this book.

### Check yourself: maps

Predict what these two lines print:

```una include="steps/18-map-forms/src/ledger.una#L35-L36" title="steps/18-map-forms/src/ledger.una"
  let tally = empty_map().with(key: "RUG-07", value: 1).with(key: "LAMP-01", value: 2).with(key: "RUG-07", value: 5)
  @console.print("{tally} {tally.len}")
```

:::answer Show the answer
```text include="steps/18-map-forms/expected/output.txt#L10"
{"LAMP-01": 2, "RUG-07": 5} 2
```

The second `with` on `RUG-07` replaces its value, so the map has two entries, not three, and `RUG-07` holds 5. The keys print in order, `LAMP-01` first, whatever order they were added in.
:::

## 10.5 JSON

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

```una include="steps/21-json-by-hand/src/byhand.una" title="steps/21-json-by-hand/src/byhand.una" verified="check, run"
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

```text include="steps/21-json-by-hand/expected/output.txt"
Some(1990) None None
```

The first record works. The other two hold the same price, and the function finds nothing: in one the fields come in another order, which JSON allows, and in the other an array holds a comma of its own. Code that cuts text depends on how the sender happened to write it. A **parser** reads the text by the rules of JSON, whatever the order of the fields or the spaces, and says exactly where the text breaks those rules.

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
| an object | `Object(fields)` | a `Map[Text, Json]`, so everything of [section 10.4](#s10-4) applies |

The step of this part reads one value of each kind, and `describe` has one arm per variant:

```una include="steps/22-json-forms/src/records.una#describe" title="steps/22-json-forms/src/records.una"
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

`text.parse_json()` parses a text. The text may not be JSON at all, so the call can fail with `JsonError`, and it takes a clause on the line under it, as every call that can fail does ([section 7.3](/learn/failure/#s7-3)). `if error use Null` carries on with `Null` in place of the value.

```una include="steps/22-json-forms/src/records.una#L38-L42" title="steps/22-json-forms/src/records.una"
  let inputs = ["null", "true", "1990", "19.90", "\"LAMP-01\"", "[1, 2, 3]", "\{\"sku\": \"LAMP-01\", \"cents\": 1990\}"]
  for text in inputs
    let value = text.parse_json()
      if error use Null
    @console.print(describe(value))
```

```text include="steps/22-json-forms/expected/output.txt#L1-L7"
null
yes or no: true
a whole number: 1990
a number with a fraction: 19.90
a string: LAMP-01
an array of 3 items
an object with the fields ["cents", "sku"]
```

The inputs are Una texts. In Una text, `{` starts an interpolation, so a literal brace is written `\{` and `\}`, and a double quote is `\"` ([section 3.1](/learn/text-and-conditions/#s3-1)).

#### Reading a field: `when`, then `get`

A field is read in two steps. A `when` checks that the value is an object and binds its fields; then `get` reads one field, as on any map. Each step can find nothing, so each says what to do then. `tags` reads the array `tags` of a record, and keeps the strings in it:

```una include="steps/22-json-forms/src/records.una#tags" title="steps/22-json-forms/src/records.una"
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

```una include="steps/22-json-forms/src/records.una#L43-L45" title="steps/22-json-forms/src/records.una"
  let record = "\{\"sku\": \"LAMP-01\", \"tags\": [\"new\", 7, \"sale\"]\}".parse_json()
    if error use Null
  @console.print("tags: {tags(record)} and {tags(Null)}")
```

```text include="steps/22-json-forms/expected/output.txt#L8"
tags: ["new", "sale"] and []
```

The `7` in the array is a `Number`, not a `Str`, so the `else` arm skips it: it gives `unit`, the only value of the type `Unit`, which does nothing. `Null`, which is not an object, has no tags.

#### Keeping the failure: `attempt` and `JsonError`

When a text is not JSON, the failure is a value of the kind `JsonError`, and each variant carries `at`, the position where reading stopped, counted in characters from 0:

- `Syntax(at)`: the first character where no valid JSON can continue, or the end of the text when it ends too early;
- `DuplicateKey(at)`: an object names the same field twice;
- `TooDeep(at)`: arrays and objects nest more than 512 levels deep;
- `NumberTooLong(at)`: a whole number of more than 4300 digits.

`attempt` keeps the outcome as a value instead of handling it on the spot ([section 7.4](/learn/failure/#s7-4)): `Ok` with the `Json`, or `Err` with the `JsonError`.

```una include="steps/22-json-forms/src/records.una#parsed" title="steps/22-json-forms/src/records.una"
--- A text read as JSON, kept as a value: `Ok` with the JSON, or `Err` with where it broke.
parsed(text: Text) -> Result[Json, JsonError] = attempt text.parse_json()
```

```una include="steps/22-json-forms/src/records.una#L46-L49" title="steps/22-json-forms/src/records.una"
  let trailing = parsed("[1, 2,]")
  let twice = parsed("\{\"sku\": \"LAMP-01\", \"sku\": \"RUG-07\"\}")
  let empty = parsed("")
  @console.print("{trailing} {twice} {empty}")
```

```text include="steps/22-json-forms/expected/output.txt#L9"
Err(Syntax(6)) Err(DuplicateKey(19)) Err(Syntax(0))
```

In `[1, 2,]`, position 6 is the `]` after the comma, where JSON wants another value. The second text names `sku` twice, and the second `sku` starts at position 19. The empty text ends before any value, at position 0.

#### Writing: build a `Json`, then `to_json`

To write JSON, build a `Json` value with the variants, and call `to_json`. An object is a `Map[Text, Json]` wrapped in `Object`:

```una include="steps/22-json-forms/src/records.una#L50-L56" title="steps/22-json-forms/src/records.una"
  let edit fields: Map[Text, Json] = empty_map()
  edit fields.set(key: "sku", value: Str(value: "LAMP-01"))
  edit fields.set(key: "tags", value: Array(items: [Str(value: "new"), Null]))
  edit fields.set(key: "on_sale", value: Boolean(value: false))
  @console.print(Object(fields).to_json())
  let note = "a \"bright\" lamp"
  @console.print(note.quote_json())
```

```text include="steps/22-json-forms/expected/output.txt#L10-L11"
{"on_sale":false,"sku":"LAMP-01","tags":["new",null]}
"a \"bright\" lamp"
```

`quote_json` writes one text as a JSON string, with its quotes escaped, for when you build JSON text yourself.

### Reading and writing a product feed

The forms together. The step parses two records of a product feed, reads a price, and writes JSON back:

:::steps
```una include="steps/23-json/src/feed.una" title="steps/23-json/src/feed.una" verified="check, run"
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

```text include="steps/23-json/expected/output.txt"
Object({"cents": Number(1990), "sku": Str("LAMP-01"), "tags": Array([Str("new")])})
Some(1990)
None
{"cents":1990,"in_stock":true,"sku":"LAMP-01"}
```

The first line is the interpolation of a `Json`, which shows the Una value, not JSON text. The keys come out sorted: a JSON object is a map, so the order of the input is not kept. The second record has a comma after its last field, which JSON does not allow, so it parses as `Null` and has no price.

### How JSON behaves

#### One way to write each value

`to_json` writes a value in one canonical form: no spaces, the fields of every object in key order, and strings escaped the same way every time. So equal values always give the same text, and the text of a value read and written back does not depend on how the sender spaced or ordered it.

#### Strict reading

`parse_json` reads exactly one JSON value, with spaces allowed around it, and nothing else. It refuses what JSON does not allow: comments, a comma after the last item, single quotes, `NaN`, a leading `+`, a leading zero before other digits, as in `01`, and a field named twice.

#### Interpolation shows the Una value

`"{record}"` writes a `Json` in its Una form, such as `Object({"cents": Number(1990)})`, which helps when you look for a mistake. `to_json` writes JSON.

#### Numbers with a fraction

> [!WARNING]
> A JSON number with a fraction, such as `19.90`, is a `Decimal`, not a `Number`, so `is Number(value)` does not match it. Keep money in whole cents, in JSON as in Una. Una has no type for numbers with a fraction yet; one is coming.

#### Read once, then use typed values

A misspelt field name, such as `"cent"`, still checks: no checker knows which fields a text will hold, and `get` gives `None` when the program runs. So read the JSON in one place, into a record with typed fields, as the day-to-day program's `read_line` does, and let the rest of the program use the record. A misspelt field of a record does not check.

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

```una include="steps/22-json-forms/src/records.una#L57-L60" title="steps/22-json-forms/src/records.una"
  let input = "\{\"sku\": \"RUG-07\", \"cents\": 4500, \"active\": true\}"
  let product = input.parse_json()
    if error use Null
  @console.print(product.to_json())
```

:::answer Show the answer
```text include="steps/22-json-forms/expected/output.txt#L12"
{"active":true,"cents":4500,"sku":"RUG-07"}
```

The record parses as an `Object`, whose fields form a map, so `to_json` writes them in key order, `active`, `cents`, `sku`, and with no spaces. The order of the input is not kept.
:::

## 10.6 Day-to-day: a daily sales report

### What the report must do

At the end of each day the shop exports its order lines, one JSON object per line. Some lines are incomplete. The report must read every line it can, say how many it skipped, total the units and the revenue of each category, name the best seller, and hand the totals to the accounting service as JSON.

The design follows from the data. The export is text, so each line is parsed on its own, and a bad line becomes `None` instead of stopping the report. The fields have types, so a `Line` record holds them once they are read, and nothing after `read_line` deals with JSON. The totals are per category and per SKU, so two maps hold them, and their key order gives the report its order.

The program is one module, and each part uses one idea of this chapter: records hold the fields, JSON and `Option` read them ([section 10.5](#s10-5)), a loop over a list keeps the good lines ([section 10.1](#s10-1)), maps group them ([section 10.4](#s10-4)), and `fold` and `first_where` find the best seller ([section 10.3](#s10-3)). Here it is in parts.

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

A missing category has a sensible default, so `or_else` gives "other". A missing SKU, quantity or price has none: the line cannot be used, so the result is `None`. Each `when` handles one of these fields, and the three nest: the `Line` is built only in the innermost arm, where all three are `Some`.

### Keeping the lines that could be read

A `for` loop over the export, with a list, `lines`, declared before it with `let edit`. At each turn, a `when` over the `Option` that `read_line` gives appends the `Some` values. The `None` arm gives `unit`, and so does nothing: the line is skipped.

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

The pattern of [Stock by SKU](#stock-by-sku), twice. `by_category` keeps a `Summary` per category, and `units_by_sku` an `Int` per SKU.

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

`fold` finds the largest number of units. Then `first_where` finds the first entry with that number. Entries come in SKU order, so on a tie the first SKU in order wins, and the result does not depend on the order of the export. An empty map gives `None`, and `headline` says so. An `Entry` is the prelude's record of one key and its value, so in `headline`, `entry.key` is the SKU and `entry.value` its units.

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

In the `day-to-day` directory, `una run .` prints the report shown in [What you'll build](#what-youll-build): eight lines, the `CHAIR-09` line skipped for its missing quantity, and the `VASE-03` line counted under "other". `summaries` comes from `values()`, so the categories print in name order. `skipped` is the difference of two lengths, since every line of the export either became a `Line` or was left out.

> [!SECURITY]
> The export here is a literal. A program that reads it from a file needs the right to read files, a capability ([chapter 12](/learn/capabilities/)). The text it reads is marked as internal data, which may reach the console only under a declared policy ([chapter 17](/learn/information-flow/)).

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

## 10.7 Testing it

### One example per path

Each path through the program gets an example: a complete line, a line that uses the default category, a line without a quantity, a line that is not JSON, two lines of one category, a tie for the best seller, a day without sales, and an amount with a leading zero in its cents. Each example calls one function with a `do` line and checks the result with an `expect` line, as in [chapter 1](/learn/hello/#s1-7), so each one names the case it covers. [Chapter 14](/learn/testing/#s14-1) covers examples in full.

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

Two of the examples pin down what the report's output alone would hide. "on a tie, the first SKU in order is the best seller" builds the map with `RUG-07` first and expects `LAMP-01`, so it shows that the result follows the key order and not the order of insertion. "a day without sales has no best seller" checks the `None` arm of `headline`, a path the sample export never reaches.

### Whole values compared with `==`

Every function the examples call is pure, with no `uses` line, so an example only gives it values and checks what comes back. The examples compare whole values with `==`: an `Option` of a record, a list, a map lookup. Lists, maps, records and `Option`s are values, so `==` compares what they hold, element by element and field by field.

### Running the examples

In the `day-to-day` directory, `una test .` prints:

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

## 10.8 Common mistakes

Each mistake is a small change to `day-to-day/src/report.una`, except the last, which changes the shipping report of [A promotion that cannot overcharge](#a-promotion-that-cannot-overcharge). Each is followed by what `una check .` reports.

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

*Why:* many languages read a position with brackets, so the hand writes them by habit. Una has no index syntax: reading a position can find nothing, so it is a function that gives an `Option`. The message reads the line as the parser does. `export` is a complete value, and after it the parser expected the line to end; the `[` is where it gave up.

*Fix:* `export.at(index: 0)` or `export.first()`, then `when` or `or_else`. See [U0101](/docs/errors/U0101/).
:::

### Using an `Option` as its value (U2001)

:::mistake
Leave out the default when reading the units so far:

```diff include="day-to-day..mistakes/2:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -83,3 +83,3 @@
   for line in lines
-    let before = units.get(key: line.sku).or_else(default: 0)
+    let before = units.get(key: line.sku)
     edit units.set(key: line.sku, value: before + line.quantity)
```

```text include="mistakes/2/expected/rendered.txt#L1"
[U2001] Error: an operand of `+` must be `Int`, found `Option[Int]`
```

*Why:* `get` gives an `Option[Int]`, and `+` needs an `Int`. The message names the operator, the type it needs, and the type it found. The checker does not guess what a missing SKU means: 0 is right here, but it would be wrong for a price.

*Fix:* `or_else(default: 0)`, or a `when` when the absence needs its own handling. See [U2001](/docs/errors/U2001/).
:::

### A `when` that forgets `None` (U2007)

:::mistake
Remove the `is None` arm of `headline`:

```diff include="day-to-day..mistakes/3:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -98,3 +98,2 @@
     is Some(entry) -> "best seller: {entry.key}, {entry.value} units"
-    is None -> "no sales"
 
```

```text include="mistakes/3/expected/rendered.txt#L1,L8"
[U2007] Error: `when` does not match variant `None` of `Option`
    │ Help: repair 1: add an arm for each missing variant, such as `is None`, or an `else` arm
```

*Why:* a `when` must cover every variant, and `None` is the day without sales. The message names the variant that has no arm, `None`, and the kind it belongs to; the help line offers the two repairs, an arm for it or an `else`.

*Fix:* add the arm, `is None -> "no sales"`. See [U2007](/docs/errors/U2007/).
:::

### Sorting records (U2025)

:::mistake
Sort the lines as they are read:

```diff include="day-to-day..mistakes/4:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -136,3 +136,3 @@
   let export = sample_export()
-  let lines = read_all(export)
+  let lines = read_all(export).sort()
   let skipped = export.len - lines.len
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U2025] Error: `sort` needs its type parameter `T` to satisfy `Ord`, and `Line` does not
```

*Why:* `sort` needs an order, and a record has none: should lines sort by SKU, by category, by price? In the message, `T` is the element type of the list, here `Line`, and `Ord` is the constraint of types with an order ([section 4.4](/learn/kinds/#s4-4)).

*Fix:* sort something that has an order, such as `lines.map(each: fn(line) -> line.sku).sort()`, or group into a map keyed by what you want to sort by, as [exercise 3](#exercise-3-categories-by-revenue) does. See [U2025](/docs/errors/U2025/).
:::

### Calling `set` without `edit` (U2020)

:::mistake
Write the update in `units_by_sku` as a plain call:

```diff include="day-to-day..mistakes/5:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -84,3 +84,3 @@
     let before = units.get(key: line.sku).or_else(default: 0)
-    edit units.set(key: line.sku, value: before + line.quantity)
+    units.set(key: line.sku, value: before + line.quantity)
   units
```

```text include="mistakes/5/expected/rendered.txt#L1"
[U2020] Error: `set` updates the map, so the call is written `edit units.set(...)`
```

*Why:* a call that reads, such as `get`, needs no mark, so it is easy to forget that `set` is different. `set` changes the map, and every change is marked where it happens. The message names the operation and writes the call as it must be.

*Fix:* `edit units.set(...)`, as the message says. See [U2020](/docs/errors/U2020/).
:::

### Parsing JSON without a clause (U3007)

:::mistake
Remove `if error use Null` from `read_line`:

```diff include="day-to-day..mistakes/6:src/report.una" context="1"
--- a/src/report.una
+++ b/src/report.una
@@ -36,3 +36,2 @@
   let json = text.parse_json()
-    if error use Null
   when json
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U3007] Error: `parse_json` can fail with `JsonError`; handle the failure with an `if error` clause, or wrap the call in `attempt`
```

*Why:* `parse_json` can fail with `JsonError`, and a call that can fail takes a clause on the line under it. The message names the call, the kind it fails with, and the two ways to handle it: an `if error` clause, or `attempt`.

*Fix:* add a clause, such as `if error use Null`, as [section 7.3](/learn/failure/#s7-3) shows. See [U3007](/docs/errors/U3007/).
:::

### A brace in JSON text (U0007)

:::mistake
Write a JSON object in a text literal without escaping its braces:

```diff include="day-to-day..mistakes/7:src/report.una" context="0"
--- a/src/report.una
+++ b/src/report.una
@@ -129 +129 @@
-  lines = lines.append(item: "\{\"sku\": \"VASE-03\", \"quantity\": 2, \"cents\": 2400\}")
+  lines = lines.append(item: "{\"sku\": \"VASE-03\", \"quantity\": 2, \"cents\": 2400}")
```

```text include="mistakes/7/expected/rendered.txt#L1,L8"
[U0007] Error: unescaped `{` in text, where no interpolation can start; write `\{`
     │ Help: repair 1: write `\{`; edit src/report.una:129:31..129:32 to "\\{"
```

*Why:* JSON is full of braces, and in a Una text `{` starts an interpolation. The message says that the brace cannot start one here, and the help line gives the exact edit, with the line and the columns of the brace.

*Fix:* write `\{` and `\}`, or let `una fix .` write them for you. See [U0007](/docs/errors/U0007/).
:::

### A lambda named with `let` (U2010)

:::mistake
Name the members' rule of the shipping report before passing it:

```diff include="steps/12-shipping-quotes..mistakes/8:src/shipping.una" context="1"
--- a/src/shipping.una
+++ b/src/shipping.una
@@ -74,3 +74,4 @@
   show(1045, charge: weekend)
-  let members = promoted(lamps, promotion: fn(cents) -> cents * 80 / 100)
+  let members_rule = fn(cents) -> cents * 80 / 100
+  let members = promoted(lamps, promotion: members_rule)
   show(1046, charge: members)
```

```text include="mistakes/8/expected/rendered.txt#L1"
[U2010] Error: cannot infer the type of lambda parameter `cents`; annotate it, as in `cents: Int`
```

*Why:* a lambda's parameter types come from the place it is passed to. A `let` gives it none, so the checker cannot know that `cents` is an `Int`. The message names the parameter and the annotation to add.

*Fix:* `fn(cents: Int) -> cents * 80 / 100`, or pass the lambda straight to `promoted`. See [U2010](/docs/errors/U2010/).
:::

## 10.9 Exercises

The exercises come with the chapter's download, `10-collections.tar.gz`. Each starts from `exercises/N/start`: a program of this chapter with the exercise's example added, and a **stub** of the function to write, a header with a placeholder body. The first three start from the day-to-day program, and the last two from the shipping report of [A promotion that cannot overcharge](#a-promotion-that-cannot-overcharge). `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

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
*Hint:* a map holds each key once and lists its keys in order, which is exactly "each once, in SKU order". Work in two steps. First keep only the lines of the category, with `filter` and a lambda that compares `line.category` with `category` ([section 10.3](#s10-3)). Then build a map keyed by SKU from those lines: the program already has a function that does, `units_by_sku`, and `keys()` lists its keys ([section 10.4](#s10-4)). The function's long form, with `=` on its own line, gives you room for a `let`.
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
*Hint:* a `for` loop over the export ([section 10.1](#s10-1)) with two `let edit` names declared before it: `number`, which counts the lines, and `numbers`, which collects the numbers of the bad ones. At each turn, add 1 to `number` first, so the first line is 1. Then call `read_line` on the text, and when its result is `None`, append `number` to `numbers`: `found is None` is a condition an `if` can test ([section 7.1](/learn/failure/#s7-1)). Last, change the first `print` of `main` to show the list.
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
*Hint:* `sort` cannot sort a `Summary`, and the prelude has no function to sort by a field or to reverse a list. A map lists its keys in ascending order, so let a map do the sorting. Key it by the revenue with its sign changed, `-summary.cents`, so that the largest revenue becomes the smallest key and comes first. Two categories can have the same revenue, so the value under each key is a list of names: `Map[Int, List[Text]]`, filled with the grouping pattern of [Stock by SKU](#stock-by-sku), with `[]` as the default. Then walk `values()` and append every name of every list to one result list, with a loop inside a loop.
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

### Exercise 4: a promotion for members

::::exercise
Members pay 300 cents less for shipping. Write `member_discount(charge)`, and print a sixth line of the shipping report, for order 1047, with the charge of order 1044 at the members' price. The start package ends with:

```una include="exercises/4/start/src/shipping.una#L114-L123" title="exercises/4/start/src/shipping.una"
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

:::answer Answer (*check, run, test*; `exercises/4/answer`).
Give `member_discount` its body, and print order 1047 in `main`:

```diff include="exercises/4/start..exercises/4/answer:src/shipping.una" context="1" title="src/shipping.una"
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

`member_discount` may give back a negative number for a small charge, and that is fine: the promise not to charge less than nothing belongs to `promoted`, which every promotion goes through.
:::
::::

### Exercise 5: two promotions in a row

::::exercise
Write `both(first, second)`, which gives back a new promotion: `first`, then `second` on what `first` gives. The start package ends with:

```una include="exercises/5/start/src/shipping.una#L114-L123" title="exercises/5/start/src/shipping.una"
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
*Hint:* the result type is `fn(Int) -> Int`, so the body is a lambda, as in `percent_off` of [section 10.2](#s10-2). The lambda takes a charge, gives it to `first`, and gives what `first` returns to `second`. It may call `first` and `second`, which it captures.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/5/answer`).
Give back a lambda that applies both:

```diff include="exercises/5/start..exercises/5/answer:src/shipping.una" context="1" title="src/shipping.una"
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

## 10.10 Recap and reference

### For agents

:::agents
Every diagnostic of [Common mistakes](#s10-8) is available as JSON with `una --json check .`. For [a `when` that forgets `None`](#a-when-that-forgets-none-u2007):

```json include="mistakes/3/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U2007","severity":"error","domain":"types","message":"`when` does not match variant `None` of `Option`","primary":{"file":"src/report.una","start":{"line":97,"col":3},"end":{"line":97,"col":7}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"add an arm for each missing variant, such as `is None`, or an `else` arm","edit":null}],"explain":"una explain U2007"}],"fixable":0}
```

The repair of U2007 has a description and no `edit`, because the right arm depends on what the absence means. The U0007 of [a brace in JSON text](#a-brace-in-json-text-u0007) carries exact edits, which `una fix .` applies. The compact rule: *a value from `first`, `at`, `get` or `first_where` is an `Option`, used through `when` or `or_else`; a call that changes a list or a map in place is written `edit xs.set(...)` on a `let edit` name; a lambda takes its types from the parameter it is passed to; `map`, `filter`, `fold` and `first_where` declare `fails of` their function.*
:::

### Recap

:::recap
- A list holds values of one type, from position 0. `append` and `sort` give back new lists; `at` and `first` read one element, as an `Option`.
- `for x in xs` runs its body once per element, in order, and zero times for an empty list.
- A function type, `fn(Int) -> Int`, lets you pass a function by its name or as a lambda, `fn(x) -> …`, whose types come from where it is passed.
- A function type without `uses` or `fails` is pure; a lambda may fail only for a parameter whose function declares `fails of` it.
- Use `map`, `filter`, `fold` and `first_where` for one-expression steps, and `for` for longer ones.
- Group with a map: `get` and `or_else`, then `edit m.set(...)`. A map lists its keys in order, and its keys need an order.
- Parse JSON with a clause or `attempt`, read it with `when` and `get`, and write it with `to_json`.
:::

### Reference

:::reference
- Construct pages: [functions and lambdas](/docs/language/functions/), [`for`](/docs/language/control-flow/for/), [`let edit` and `edit` parameters](/docs/language/control-flow/let-edit/), [`when`](/docs/language/control-flow/when/), [`if error` and `if none`](/docs/language/errors/if-error/), [`example`](/docs/language/examples/example/)
- Standard library: [the prelude](/docs/std/) (`List`, `Option`, `append`, `set`, `at`, `first`, `is_empty`, `first_where`, `contains`, `sum`, `sort`, `map`, `filter`, `fold`, `or_else`, `min`, `max`), [maps](/docs/std/maps/) (`Map`, `Entry`, `empty_map`), [text](/docs/std/text/) (`join`), [JSON](/docs/std/json/) (`Json`, `JsonError`, `parse_json`, `to_json`, `quote_json`)
- Diagnostics: [U0007](/docs/errors/U0007/), [U0101](/docs/errors/U0101/), [U2001](/docs/errors/U2001/), [U2007](/docs/errors/U2007/), [U2010](/docs/errors/U2010/), [U2020](/docs/errors/U2020/), [U2025](/docs/errors/U2025/), [U3001](/docs/errors/U3001/), [U3003](/docs/errors/U3003/), [U3007](/docs/errors/U3007/), [U3009](/docs/errors/U3009/)
- Specification: [functions and contracts](/docs/spec/04-functions-and-contracts/) (lambdas), [the standard library](/docs/spec/14-standard-library/), [the memory model](/docs/spec/17-memory-model/) (`for`, `let edit`, `set`), [constraints on generics](/docs/spec/20-constraints-on-generics/), [maps](/docs/spec/21-maps/), [JSON](/docs/spec/23-json/)
:::
