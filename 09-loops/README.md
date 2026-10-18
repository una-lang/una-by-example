---
learn: "9"
title: Repeating: for
editions: ["0.2"]
codes: [U0103, U1002, U2001, U2019, U5002]
time: 20
builds: A weekly restock plan
prerequisites: ["2", "3", "4", "5", "6", "7", "8"]
template: 2
nav: ["for over ranges and texts", "let edit", "What the verifier knows", "Common mistakes"]
---

# 9 Repeating: for

## 9.1 `for` over ranges and texts


### What a loop is

A **loop** repeats the same steps once for each item of a group. Think of a cashier at a till. The basket holds some items, and the cashier does the same thing with each one: scan it, and add its price to the total. Nobody writes down separate instructions for the first item, the second and the third. The instruction is "for each item in the basket, scan it and add its price", and it works for a basket of one item or of fifty.

In Una you write that instruction with `for`. A few words name its parts, and the rest of this section uses them:

- The **body** is the indented block of lines under the `for` line: the steps to repeat.
- A **turn** is one run of the body, for one item. A list of three elements gives three turns. (Other books call a turn an *iteration*.)
- The **loop variable** is the name the body uses for the current item. You choose it, and at each turn it holds the next element.
- What the loop **walks** is the group it takes the items from: a list ([section 10.1](/learn/collections/#s10-1)), or a range of whole numbers.

### Why programs repeat work

Without a loop, a program can only do work it can count in advance. Here is a function that prices a cart without one:

```una include="steps/01-no-loop/src/receipt.una" title="steps/01-no-loop/src/receipt.una" verified="check, run"
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

```text include="steps/01-no-loop/expected/output.txt"
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
```una include="steps/02-for/src/totals.una#total" title="steps/02-for/src/totals.una"
--- What a cart costs, in cents.
total(lines: List[CartLine]) -> Int
=
  let edit sum = 0
  for line in lines
    sum = sum + line.quantity * line.cents
  sum
```

1. **`let edit sum = 0`.** Before the loop, a binding that will hold the running total. A **binding** is a name for a value ([chapter 2](/learn/numbers/#s2-1)). A plain `let` names one value for good; `let edit` makes a binding you may give new values. A binding that a loop builds up turn by turn is often called an **accumulator**. It starts at the answer for an empty cart: 0.
2. **`for`.** The keyword that starts a loop: a word with a fixed meaning in the language ([chapter 1](/learn/hello/#s1-4)), which cannot name a binding.
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
| `for entry in stock.entries()` | the entries of a map, in key order ([section 10.4](/learn/collections/#s10-4)) |
| `let made = together for sku in skus` | each element, at the same time, building a list of the results ([chapter 15](/learn/concurrency/#s15-1)) |

In a loop, the ends of a range can be any integer expressions of one type, such as `0..<skus.len`. In a `when` arm or a kind, they are literals. There is no other kind of loop: no `while` and no `loop`. [Una has no `while`](#una-has-no-while) says why.

### Loops over lists and ranges

#### Totals, bulk lines and weeks

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

#### Where a range starts and stops

A range is the easiest place to be off by one, so it pays to see each form run. The next step walks ranges and keeps the numbers each loop visits:

```una include="steps/03-loop-forms/src/shelves.una#aisles_through..aisles_before" title="steps/03-loop-forms/src/shelves.una"
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

```text include="steps/03-loop-forms/expected/output.txt#L3-L7"
aisles 1..3: [1, 2, 3]
aisles 1..<3: [1, 2]
aisles 2..2: [2]
aisles 2..<2: []
aisles 3..1: []
```

Read the lines in pairs. `..` stops *at* its end, and `..<` stops *before* it. A range from a number to itself visits that number once with `..`, and nothing with `..<`. A range whose start is above its end visits nothing: Una never counts down.

#### Positions of a list

Sometimes the body needs the position of each element, as a numbered receipt does. Walk the range of positions, from 0 up to the length:

```una include="steps/03-loop-forms/src/shelves.una#numbered" title="steps/03-loop-forms/src/shelves.una"
--- The lines of a receipt, numbered from 1: a loop over the positions of a list.
numbered(skus: List[Text]) -> List[Text]
=
  let edit lines: List[Text] = []
  for position in 0..<skus.len
    let sku = skus.at(index: position).or_else(default: "")
    lines = lines.append(item: "{position + 1}. {sku}")
  lines
```

```text include="steps/03-loop-forms/expected/output.txt#L8"
["1. DESK-02", "2. LAMP-01"]
```

`0..<skus.len` visits exactly the valid positions. `at` still returns an `Option`, because Una has no `skus[position]` form, and `or_else` gives the value inside it, or the default `""` ([section 7.1](/learn/failure/#s7-1) explains both). When you need only the elements, walk the list itself: it is shorter, and it cannot miss an element or read past the end.

#### The characters of a text

Any function that returns a list gives a loop something to walk. `chars()` gives the characters of a text, one text of one character each. `is_digits` is true when every character of a text is a digit, 0 to 9:

```una include="steps/03-loop-forms/src/shelves.una#digits_in" title="steps/03-loop-forms/src/shelves.una"
--- How many digits a SKU holds: a loop over the characters of a text.
digits_in(sku: Text) -> Int
=
  let edit count = 0
  for character in sku.chars()
    if character.is_digits()
      count = count + 1
  count
```

```text include="steps/03-loop-forms/expected/output.txt#L9"
digits in LAMP-01: 2
```

#### An empty list

A loop over an empty list runs its body zero times. The accumulator keeps its first value, so a function that starts from the right value for "nothing" needs no special case:

```una include="steps/03-loop-forms/src/shelves.una#units" title="steps/03-loop-forms/src/shelves.una"
--- How many units a cart holds: a loop over a list.
units(lines: List[CartLine]) -> Int
=
  let edit count = 0
  for line in lines
    count = count + line.quantity
  count
```

```text include="steps/03-loop-forms/expected/output.txt#L1-L2"
units in the cart: 7
units in an empty cart: 0
```

### What a loop body can hold

The body of a loop is a block like any other: it can hold `let` lines, an `if`, a `when`, and another loop. The step for this part works on orders:

```una include="steps/04-loop-bodies/src/orders.una#OrderLine..Movement" title="steps/04-loop-bodies/src/orders.una" caption="the kinds"
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

```una include="steps/04-loop-bodies/src/orders.una#lighting_and_other" title="steps/04-loop-bodies/src/orders.una"
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

```text include="steps/04-loop-bodies/expected/output.txt#L1"
lighting 5, other 1
```

A `when` chooses by the variant of a sum kind ([chapter 4](/learn/kinds/#s4-3)). Each arm that assigns writes its assignment on its own line, indented under the arm:

```una include="steps/04-loop-bodies/src/orders.una#stock_after" title="steps/04-loop-bodies/src/orders.una"
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

```text include="steps/04-loop-bodies/expected/output.txt#L2"
stock at closing: 8
```

The stock starts at 4, receives 10, sells 3, loses 1 and sells 2: 4 + 10 − 3 − 1 − 2 = 8.

#### A loop inside a loop

A body may hold another loop. The inner loop runs all its turns during each turn of the outer one. Orders hold lines, so counting every unit of every order takes two loops:

```una include="steps/04-loop-bodies/src/orders.una#all_units" title="steps/04-loop-bodies/src/orders.una"
--- Every unit of every order: a loop inside a loop.
all_units(orders: List[Order]) -> Int
=
  let edit total = 0
  for order in orders
    for line in order.lines
      total = total + line.quantity
  total
```

```text include="steps/04-loop-bodies/expected/output.txt#L3"
units in two orders: 6
```

Nested loops also combine two lists. Each color meets each size, so two colors and two sizes give four SKUs, in the order the loops visit them: all the sizes of the first color, then all the sizes of the second.

```una include="steps/04-loop-bodies/src/orders.una#tee_skus" title="steps/04-loop-bodies/src/orders.una"
--- Every SKU of a T-shirt, one for each color and size, such as `TEE-RED-S`.
tee_skus(colors: List[Text], sizes: List[Text]) -> List[Text]
=
  let edit skus: List[Text] = []
  for color in colors
    for size in sizes
      skus = skus.append(item: "TEE-{color}-{size}")
  skus
```

```text include="steps/04-loop-bodies/expected/output.txt#L4"
["TEE-RED-S", "TEE-RED-M", "TEE-BLUE-S", "TEE-BLUE-M"]
```

The inner loop assigns `skus`, which is declared outside both loops. That is how a result leaves a loop: through an editable binding declared before it.

### How a loop behaves

#### Order, and how many turns

- A loop over a list visits the elements in the list's order, each one once.
- A loop over a range visits the integers in increasing order.
- The list or the range is computed once, before the first turn. Changing a binding inside the body does not change how many turns the loop takes.
- Every turn runs. Una has no `break` to leave a loop early and no `continue` to skip the rest of a turn. To skip an element, put the body's steps under an `if`. To stop at the first element that matches, use `first_where` ([section 10.3](/learn/collections/#s10-3)), which stops there.

#### What lives from one turn to the next

A binding declared inside the body, with `let`, is new at each turn of the loop and is gone after it. To carry a value from one turn to the next, or out of the loop, declare it before the loop with `let edit`, as `sum` and `found` are. The loop variable, `line` or `week`, is a plain binding: you read it, and the next turn gives it the next element. Assigning it is an error, U2019, as for any plain `let` ([updating a plain `let`](#updating-a-plain-let-u2019) shows the message).

#### A loop is a statement

A `for` loop gives no value of its own: it is a statement, and what it computes lives in the bindings it updates. So a function ends with the binding, `sum`, after the loop, never with the loop. `together for` is the exception: it is written after `let`, and its value is the list it builds.

#### A loop is not a call

A **call** is one function running another and waiting for its answer. The **call depth** is how many calls are waiting at once, and a run has a limit on it. A loop's turns are not calls, so a loop does not use up the call depth, however many turns it takes ([chapter 16](/learn/memory/#s16-4)). A function that calls itself, which [Una has no `while`](#una-has-no-while) shows, adds one call per step.

### Una has no `while`

Many languages have a second kind of loop, `while`, which repeats its body for as long as a condition holds. Its end depends on the body changing something that the condition reads. When the body forgets to, the loop never ends, and the program hangs.

In Una, every loop walks a list or a range whose size is known before the first turn, so a reader can see where each loop ends. Write a `while` anyway, in a function that counts how long the stock lasts:

```diff include="steps/04-loop-bodies..steps/05-while:src/orders.una" context="1" title="src/orders.una"
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

```text include="steps/05-while/expected/rendered.txt"
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

The message names the two ways Una repeats work. Here, how many weeks the stock lasts is not known in advance, so a range does not fit. **Recursion** does: a function that calls itself with a smaller problem, and stops at a case it can answer at once ([chapter 6](/learn/functions/) introduces functions).

```una include="steps/04-loop-bodies/src/orders.una#weeks_of_stock" title="steps/04-loop-bodies/src/orders.una"
--- How many whole weeks `stock` units last when `per_week` units sell each week.
weeks_of_stock(stock: Int, per_week: Int) -> Int
  requires per_week >= 1
=
  if stock < per_week then 0 else 1 + weeks_of_stock(stock - per_week, per_week)
```

```text include="steps/04-loop-bodies/expected/output.txt#L5"
10 units at 3 a week last 3 weeks
```

With 10 units and 3 sold a week, the function answers 1 + the weeks of 7 units, which is 1 + the weeks of 4 units, which is 1 + the weeks of 1 unit, which is 0: 3 weeks. Each call has a smaller stock, so the calls end. `requires per_week >= 1` keeps a caller from passing 0, which would never make the stock smaller ([chapter 6](/learn/functions/#s6-2) introduced `requires`, and [chapter 5](/learn/contracts/#s5-1) explains it). When you know an upper limit, such as "at most 52 weeks", a range up to that limit with an `if` in the body is the other choice.

### Choosing a loop or a function over the list

A loop says *how* to walk a list. The prelude also has functions that walk the list for you, so you say only what to do with each element ([section 10.3](/learn/collections/#s10-3)):

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

```una include="steps/04-loop-bodies/src/orders.una#low_shelves" title="steps/04-loop-bodies/src/orders.una"
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
```text include="steps/04-loop-bodies/expected/output.txt#L6"
low shelves: 2
```

The body runs four times. `low` goes up for 0 and for 1, the two counts below 2, and stays put for 3 and 5. An empty list would give 0, the value `low` starts with.
:::

This one keeps a running total, and the list of totals after each line:

```una include="steps/04-loop-bodies/src/orders.una#running" title="steps/04-loop-bodies/src/orders.una"
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
```text include="steps/04-loop-bodies/expected/output.txt#L7"
running totals: [2, 3, 6]
```

Both bindings live outside the loop, so each turn starts from what the previous turn left. `total` goes 2, 3, 6, and each turn appends the new total to `seen`.
:::

## 9.2 Names that change: `let edit`

### A running total at the till

A till adds up the items a cashier scans, so its total is an editable name:

:::steps
```una include="steps/06-till/src/till.una" title="src/till.una" verified="check, run"
module till

--- Prints the running total of a till as three items are scanned.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = 1_990
  let edit total = 0
  let edit items = 0
  total = total + lamp
  items = items + 1
  total = total + lamp
  items = items + 1
  @console.print("{items} items, {total} cents")
  total = total + 4_500
  items = items + 1
  @console.print("{items} items, {total} cents")
  let edit receipt: Text = "LAMP-01"
  receipt = "{receipt}, LAMP-01, RUG-07"
  @console.print(receipt)
```

1. **`let lamp = 1_990`.** A plain name. Its type, `Int`, comes from its value.
2. **`let edit total = 0`.** An editable name, which later lines may assign. Its type is fixed by its first value: every later value must be an `Int`.
3. **`total = total + lamp`.** An assignment. It is a statement on its own line, and it gives `total` a new value.
4. **`let edit receipt: Text = "LAMP-01"`.** A type written after the name, with `:`. It is optional here, but it tells a reader what the name will hold.
5. **`receipt = "{receipt}, LAMP-01, RUG-07"`.** A text that starts with the old value: the way to add to a text.
:::

`una run .` prints:

```text include="steps/06-till/expected/output.txt"
2 items, 3980 cents
3 items, 8480 cents
LAMP-01, LAMP-01, RUG-07
```

> [!NOTE]
> `let edit` belongs to edition `0.2` and later. In a package of edition `0.1`, `edit` is a reserved word, and every name is a plain `let`.

### How names behave

#### A name lives to the end of its block

A **block** is a run of lines at the same indentation, such as the body of a function. A name exists from its `let` line to the end of its block. A line before the `let` cannot use it.

#### One name, one meaning: no shadowing

Making a name that another `let` of the same body already made is an error, even with `let` both times:

```diff include="steps/06-till..steps/07-rebind:src/till.una" title="src/till.una" context="1"
--- a/src/till.una
+++ b/src/till.una
@@ -7,2 +7,3 @@
   let lamp = 1_990
+  let lamp = 2_490
   let edit total = 0
```

```text include="steps/07-rebind/expected/rendered.txt"
[U1002] Error: `lamp` is already bound in this scope; a local cannot rebind another
   ╭─[ src/till.una:8:7 ]
   │
 7 │   let lamp = 1_990
   │       ──┬─
   │         ╰─── first defined here
 8 │   let lamp = 2_490
   │       ──┬─
   │         ╰─── `lamp` is already bound in this scope; a local cannot rebind another
   │
   │ Note: run `una explain U1002` for an explanation
───╯
```

The diagnostic marks both lines: where the name was first defined, and where it was made again. Its **scope** is the stretch of code where a name can be used: here, the body of `main`. Some languages allow the second `let`, which **shadows** the first: the old value is still there, hidden behind the new one. Una does not, inside a block or in a block nested in it, so a name means one thing from its line to the end of its block. To change a value, use `let edit` and an assignment; for a different value, choose a different name.

#### An editable name keeps its type

`let edit items = 0` makes `items` an `Int` for good. Assign it a text:

```diff include="steps/06-till..steps/08-edit-type:src/till.una" title="src/till.una" context="1"
--- a/src/till.una
+++ b/src/till.una
@@ -10,3 +10,3 @@
   total = total + lamp
-  items = items + 1
+  items = "one"
   total = total + lamp
```

```text include="steps/08-edit-type/expected/rendered.txt#L1"
[U2001] Error: expected `Int`, found `Text`
```

The checker expected an `Int`, the type of `items`, and found a `Text`.

#### Adding to a text in place

`receipt = "{receipt}, …"` does not copy the whole text each time. When an assignment adds to the end of a text that nothing else holds, the text grows in place, so building a long text this way takes time in proportion to its length.

### Choosing between `let` and `let edit`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Name a value you compute once | `let` |
| Keep a total, a count or a text that grows | `let edit`, and assignments |
| Say what type a name holds | `let name: Type = …`, with either form |
| A value that differs by case | `let` with an `if … then … else`, not a `let edit` assigned in two places |
:::

Prefer `let`. A name that cannot change is one less thing a reader must track, and in most functions every name can be a `let`. Use `let edit` when a value really accumulates, as `total` does here, and as loops do in [chapter 10](/learn/collections/).

### Check yourself: names

A shelf holds 10 units. Three are sold, then a delivery brings five:

```una include="steps/09-restock/src/restock.una" title="steps/09-restock/src/restock.una"
module restock

--- Prints the stock of a shelf after a sale and a delivery.
pub main() -> Unit
  uses @console: Console[print]
=
  let edit stock = 10
  stock = stock - 3
  let sold = 10 - stock
  stock = stock + 5
  @console.print("{stock} in stock, {sold} sold")
```

What does it print?

:::answer Show the answer
```text include="steps/09-restock/expected/output.txt"
12 in stock, 3 sold
```

`stock` goes 10, 7, 12. `sold` is computed once, when `stock` is 7, so it is 3, and it stays 3 when `stock` changes later: a plain `let` holds the value it was given, not a formula.
:::

## 9.3 What a loop keeps and what the verifier knows

### When a loop forgets a fact

A loop gives U5002 too. A loop's body runs any number of times, so the verifier does not follow it turn by turn. From one turn to the next it keeps, about each binding the loop updates, only the refinement of its type. Everything else about the binding is forgotten. Here `total` is a plain `Int`:

```una include="steps/10-loop-unknown/src/units.una#units_of" title="steps/10-loop-unknown/src/units.una"
--- The units of a delivery, counting only the lines with a positive quantity.
units_of(quantities: List[Int]) -> Int
  ensures result >= 0
=
  let edit total = 0
  for quantity in quantities
    if quantity > 0
      total = total + quantity
  total
```

```text include="steps/10-loop-unknown/expected/rendered.txt#L1"
[U5002] Error: postcondition of `units_of` could not be proven (the loop forgets every fact about `total` but the refinements of its type, so the counterexample sets `total` freely; state what one iteration does as the `ensures` of a helper with an `edit` parameter, and call the helper in the loop)
```

The reason says what happened: "the loop forgets every fact about `total` but the refinements of its type". `Int` has no refinement, so after the loop `total` could be anything, as far as the solver knows. The reason also says what to do in general: state what one turn does as the `ensures` of a helper with an `edit` parameter, and call the helper in the loop. An `edit` parameter is one the function may change for its caller, as `restock` in [section 5.2](/learn/contracts/#s5-2) does; [chapter 16](/learn/memory/) covers it.

Here a simpler fix is enough. The fact the clause needs, "not negative", can be the type of `total`. `Nat`, from the prelude, is the integers that are not negative:

```diff include="steps/10-loop-unknown..steps/11-loop-nat:src/units.una" context="1" title="src/units.una"
--- a/src/units.una
+++ b/src/units.una
@@ -6,3 +6,3 @@
 =
-  let edit total = 0
+  let edit total: Nat = 0
   for quantity in quantities
```

Now each assignment `total = total + quantity` proves that the new value is a `Nat`, which holds since `quantity > 0` on that branch, and the loop keeps `total >= 0` from turn to turn. The step checks, and prints:

```text include="steps/11-loop-nat/expected/output.txt"
units: 5
```

The day-to-day program's `subtotal` uses the same move, with `let edit total: Cents = 0`.

U5002 has two more sources: a question that runs out of the step budget in `verification.lock`, and, rarely, one that runs out of the wall-clock limit of one question (`--solver-wallclock`, 60 seconds by default), whose result can differ between machines. The reason says which. Both are rare in code of this size; split the function, or state an intermediate fact with a `let` and a guard, so that each question is smaller. In edition `0.3`, an `effect_condition` or `contract_lock` obligation can be unknown too.

## 9.4 Common mistakes

### Assigning a plain `let` (U2019)

:::mistake
Declare the running total with `let`:

```diff include="steps/12-shelf-labels..mistakes/1:src/labels.una" context="1"
--- a/src/labels.una
+++ b/src/labels.una
@@ -55,3 +55,3 @@
 =
-  let edit printed = 0
+  let printed = 0
   @console.print(regular_label(" lamp-01", name: "Desk lamp, brass", cents: 1990))
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U2019] Error: `printed` is not editable; declare it `let edit printed`, or the parameter `edit printed`
```

*Why:* a name declared with `let` holds one value. una reports each of the four assignments, one diagnostic each, and the message gives the exact declaration to write.

*Fix:* `let edit printed = 0`, as the message says. See [U2019](/docs/errors/U2019/).
:::

### Updating a plain `let` (U2019)

:::mistake
Declare the result of `read_all` with `let` instead of `let edit`:

```diff include="steps/13-daily-sales-report..mistakes/2:src/report.una" context="1"
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

*Why:* a plain `let` names one value for good, and only a binding declared `let edit` can take a new one. The loop assigns `lines` at each turn, and that assignment is what the checker refuses. The message names the binding and gives both ways to make it editable: a `let edit` binding, or an `edit` parameter, which [chapter 16](/learn/memory/#s16-2) covers.

*Fix:* `let edit lines: List[Line] = []`, as the message says.
:::
