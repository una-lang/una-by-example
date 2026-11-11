---
learn: "9"
title: Repeating: for
editions: ["0.2"]
codes: [U0101, U0103, U1002, U2001, U2019, U5001, U5002]
time: 50
builds: A weekly restock plan that follows each product's stock week by week and says when to order
prerequisites: ["2", "3", "4", "5", "6", "7", "8"]
template: 2
nav: ["for over ranges and texts", "let edit", "What a loop keeps", "Day-to-day: restock plan", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 9 Repeating: for

Until now, a step that runs four times was written four times, or put in a function that calls itself. A plan for four weeks had four lines, and a plan for five weeks needed a fifth. Real work repeats: the same check for every week of a plan, every character of a SKU, every aisle of a store. This chapter teaches the `for` loop, which runs the same steps once for each number of a range or each character of a text, and `let edit`, the name that a loop changes from one turn to the next. It ends with what the verifier knows about a loop, and a restock plan built from both.

## What you'll build

:::build
A restock plan for the next four weeks. For each product, it follows the stock week by week: what is left after the week's sales, and the order the store places when the stock falls below its reorder point. It ends each product with the units ordered and the weeks the shelf started too low. The program prints:

```text include="day-to-day/expected/output.txt"
Restock plan, 4 weeks
LAMP-01, LAMP
  week 1: 9 left
  week 2: 4 left, order 10
  week 3: 9 left
  week 4: 4 left, order 10
  20 units ordered, 0 weeks short
RUG-07, RUG
  week 1: 1 left, order 4
  week 2: 3 left
  week 3: 1 left, order 4
  week 4: 3 left
  8 units ordered, 0 weeks short
DESK-02, DESK
  week 1: 0 left, order 2
  week 2: 0 left, order 2
  week 3: 0 left, order 2
  week 4: 0 left, order 2
  8 units ordered, 4 weeks short
```

You will learn to:

- repeat steps with `for`, over a range of whole numbers or the characters of a text;
- choose between `..`, which includes the end of a range, and `..<`, which leaves it out;
- keep a total, a count or a growing text in an editable name, `let edit`;
- give an editable name a refined type, so that the verifier keeps its fact through the loop;
- read U2019, U5002 and the other diagnostics a loop can give.
:::

## Why it works this way

In many languages, a loop is where a program goes wrong most quietly. A loop that counts from 0 to 10 when it meant 0 to 9 reads one item past the end. A loop that repeats "while the stock is above zero" never ends when its body forgets to lower the stock, and the program hangs. A name that any line may change makes a reader trace every line to know what it holds.

Una keeps the loop small and visible. A `for` loop walks a range of numbers, or a list such as the characters of a text, and the number of turns is fixed before the first turn: a reader sees where the loop ends from its first line. The range says in its own syntax whether its end is included. A name changes only when it is declared `let edit`, so a plain `let` still holds the value it was given. And the verifier checks a loop's body once, for every turn at the same time: what it keeps from one turn to the next is what the types of the changing names say, and nothing else.

> [!KEY]
> In Una, a `for` loop takes one turn for each value of a range or a list fixed before it starts, and only a name declared `let edit` changes from turn to turn.

## 9.1 `for` over ranges and texts

### What a loop is

A **loop** runs the same steps several times, once for each value of a group. Think of a store clerk who counts stock aisle by aisle. The instruction is not "count aisle 1, then count aisle 2, then count aisle 3". It is "for each aisle from 1 to 3, count its shelves": one instruction, the same steps, and the aisle changes at each step. The instruction stays the same for a store of three aisles or of thirty.

A few words name the parts of a loop, and the rest of this chapter uses them:

- The **body** is the indented block of lines under the loop's first line: the steps to repeat.
- A **turn** is one run of the body, for one value. A loop over the aisles 1 to 3 takes three turns. (Other books call a turn an *iteration*.)
- The **loop variable** is the name the body uses for the value of the current turn. You choose it, and each turn gives it the next value.
- What the loop **walks** is the group it takes the values from: a **range** of whole numbers, such as 1 to 3, or the characters of a text.

### Why programs repeat work

Here is a plan for four weeks, without a loop:

```una include="steps/01-no-loop/src/plan.una" title="src/plan.una" verified="check, run"
module plan

--- Prints a restock plan of four weeks, one line for each week, written out by hand.
pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("week 1: count the lamp shelf")
  @console.print("week 2: count the lamp shelf")
  @console.print("week 3: count the lamp shelf")
  @console.print("week 4: count the lamp shelf")
```

Each example of this chapter is a package of its own, made as [chapter 2](/learn/numbers/#each-step-is-a-package) explains, and the chapter's download, `09-loops.tar.gz`, holds them all. This one works, and `una run .` prints:

```text include="steps/01-no-loop/expected/output.txt"
week 1: count the lamp shelf
week 2: count the lamp shelf
week 3: count the lamp shelf
week 4: count the lamp shelf
```

But the program is fragile in three ways:

1. **It fits one size.** It plans exactly four weeks. A plan of six weeks needs two more lines, and a plan whose length comes from a parameter cannot be written this way at all: the number of lines is fixed when you write the code, not when it runs.
2. **It repeats itself.** The text of the line is written four times. To change it, you change four places, and a missed one prints two different lines in one plan.
3. **It grows with the work.** A plan of a year would be fifty-two lines that differ in one number.

A function that calls itself, as [section 6.1](/learn/functions/#s6-1) showed with `marked_down`, can repeat a step a number of times that comes from a parameter. A loop says the same thing more directly: do these steps for each week from 1 to `weeks`.

### How to write a `for` loop

Here is the plan with a loop:

:::steps
```una include="steps/02-for/src/plan.una#print_weeks" title="src/plan.una"
--- Prints the line of each week of the plan, from week 1 to week `weeks`.
pub print_weeks(weeks: Int) -> Unit
  uses @console: Console[print]
=
  for week in 1..weeks
    @console.print("week {week}: count the lamp shelf")
```

1. **`for`.** The keyword that starts a loop.
2. **`week`.** The loop variable. You choose the name; a good name says what one value is.
3. **`in 1..weeks`.** What the loop walks: here the range of whole numbers from 1 to `weeks`, both included.
4. **The indented line.** The body, indented two spaces under the `for` line. It runs once for each number of the range, with `week` holding that number.
:::

`main` calls `print_weeks(4)`, and `una run .` prints the same four lines as the plan written by hand:

```text include="steps/02-for/expected/output.txt"
week 1: count the lamp shelf
week 2: count the lamp shelf
week 3: count the lamp shelf
week 4: count the lamp shelf
```

Follow it turn by turn. The range `1..4` holds the numbers 1, 2, 3 and 4. The first turn gives `week` the value 1, and the body prints `week 1: …`. The second turn gives it 2, and so on. After the turn for 4 there is no number left, the loop ends, and so does `print_weeks`. The text of the line is written once, and `print_weeks(6)` plans six weeks with no change to the function.

### What a loop can walk

What comes after `in` decides which values the loop visits. Each form below is a function of one package, `steps/03-range-forms`, whose `main` calls them with a few pairs of ends.

#### An inclusive range: `..`

`first..last` is the range from `first` to `last`, **both included**:

```una include="steps/03-range-forms/src/aisles.una#through" title="steps/03-range-forms/src/aisles.una"
--- Prints the aisles from `first` to `last`, `last` included: an inclusive range.
pub through(first: Int, last: Int) -> Unit
  uses @console: Console[print]
=
  @console.print("{first}..{last}:")
  for aisle in first..last
    @console.print("  aisle {aisle}")
```

`through(1, last: 3)` prints:

```text include="steps/03-range-forms/expected/output.txt#L1-L4"
1..3:
  aisle 1
  aisle 2
  aisle 3
```

#### An exclusive range: `..<`

`first..<last` is the range from `first` up to `last`, **with `last` left out**. Read `..<` as "up to, but less than":

```una include="steps/03-range-forms/src/aisles.una#before" title="steps/03-range-forms/src/aisles.una"
--- Prints the aisles from `first` up to `last`, `last` left out: an exclusive range.
pub before(first: Int, last: Int) -> Unit
  uses @console: Console[print]
=
  @console.print("{first}..<{last}:")
  for aisle in first..<last
    @console.print("  aisle {aisle}")
```

`before(1, last: 3)` prints:

```text include="steps/03-range-forms/expected/output.txt#L5-L7"
1..<3:
  aisle 1
  aisle 2
```

The exclusive form fits a count of things numbered from 0: `0..<count` takes exactly `count` turns, for the numbers 0 to `count - 1`.

#### Ends that are computed

The ends of a range may be any expressions that give whole numbers, such as a parameter plus 1. Both ends have one type, here `Int`:

```una include="steps/03-range-forms/src/aisles.una#next_two" title="steps/03-range-forms/src/aisles.una"
--- Prints the two aisles after `aisle`: the ends of a range may be computed.
pub next_two(aisle: Int) -> Unit
  uses @console: Console[print]
=
  @console.print("after aisle {aisle}:")
  for next in aisle + 1..aisle + 2
    @console.print("  aisle {next}")
```

`next_two(4)` prints:

```text include="steps/03-range-forms/expected/output.txt#L16-L18"
after aisle 4:
  aisle 5
  aisle 6
```

A range may also start below zero: `through(-1, last: 1)` visits -1, 0 and 1.

#### A range of a fixed-width type

The ends may be of a fixed-width type, such as `U8` ([section 2.3](/learn/numbers/#s2-3)). A literal end then takes the type of the other end, so in `first..255` the `255` is a `U8` too:

```una include="steps/03-range-forms/src/aisles.una#last_codes" title="steps/03-range-forms/src/aisles.una"
--- Prints the last two label codes of a roll, which fit in one byte: a range of `U8`.
pub last_codes() -> Unit
  uses @console: Console[print]
=
  let first: U8 = 254
  @console.print("codes from {first}:")
  for code in first..255
    @console.print("  code {code}")
```

```text include="steps/03-range-forms/expected/output.txt#L19-L21"
codes from 254:
  code 254
  code 255
```

An inclusive range stops at its end without computing the number after it, so a range up to 255, the largest `U8`, does not overflow.

#### The characters of a text: `chars`

`sku.chars()` gives the characters of a text, in order, each one a text of one character. A loop walks them one by one:

```una include="steps/04-texts/src/skus.una#print_characters" title="steps/04-texts/src/skus.una"
--- Prints each character of a SKU, between brackets.
pub print_characters(sku: Text) -> Unit
  uses @console: Console[print]
=
  for character in sku.chars()
    @console.print("[{character}]")
```

`print_characters("Café-2")` prints:

```text include="steps/04-texts/expected/output.txt#L1-L6"
[C]
[a]
[f]
[é]
[-]
[2]
```

`é` is one character, as `.len` counts it ([section 3.1](/learn/text-and-conditions/#s3-1)), and so is the dash. What `chars` gives back is a **list** of texts, a sequence of values; lists are the subject of [chapter 10](/learn/collections/#s10-1), which also shows a loop over any list. Here you need only what the loop does with it: one turn per character.

#### The parts of a text: `split`

`sku.split(on: "-")` cuts a text at each dash and gives the parts between them, also as a list of texts ([section 3.2](/learn/text-and-conditions/#s3-2) lists it):

```una include="steps/04-texts/src/skus.una#print_parts" title="steps/04-texts/src/skus.una"
--- Prints each part of a SKU, the texts between its dashes.
pub print_parts(sku: Text) -> Unit
  uses @console: Console[print]
=
  for part in sku.split(on: "-")
    @console.print("part: {part}")
```

`print_parts("LAMP-01-BR")` prints:

```text include="steps/04-texts/expected/output.txt#L7-L9"
part: LAMP
part: 01
part: BR
```

#### The positions of a text

A text's characters sit at positions numbered from 0, so `0..<sku.len` walks the positions of a text, from the first to the last:

```una include="steps/04-texts/src/skus.una#print_positions" title="steps/04-texts/src/skus.una"
--- Prints each position of a SKU, from 0 up to its length.
pub print_positions(sku: Text) -> Unit
  uses @console: Console[print]
=
  for position in 0..<sku.len
    @console.print("position {position} of {sku.len}")
```

`print_positions("RUG")` prints:

```text include="steps/04-texts/expected/output.txt#L10-L12"
position 0 of 3
position 1 of 3
position 2 of 3
```

A text of 3 characters has the positions 0, 1 and 2. With `..` in place of `..<`, the loop would also visit 3, a position past the end. [What the body knows](#what-the-body-knows) shows how the verifier catches that when the body cuts the text at the position.

### What a loop body can hold

The body of a loop is a block like the body of a function: it may hold a `let`, an `if`, a `when`, and another loop. The step for this part plans a store's week:

```una include="steps/05-bodies/src/week.una#Day..day_kind" title="steps/05-bodies/src/week.una" caption="the days"
--- The kind of a day of the week, for the store's hours.
kind Day = Weekday | Saturday | Sunday

--- The kind of day `day` is, counting Monday as day 1.
pub day_kind(day: Int) -> Day = if day == 6 then Saturday else if day == 7 then Sunday else Weekday
```

#### A `when` in the body

A `when` inside the body chooses, at each turn, by the variant of a sum kind ([section 4.3](/learn/kinds/#s4-3)):

```una include="steps/05-bodies/src/week.una#print_hours" title="steps/05-bodies/src/week.una"
--- Prints the hours of each day: a `when` inside a loop.
pub print_hours() -> Unit
  uses @console: Console[print]
=
  for day in 1..7
    when day_kind(day)
      is Weekday -> @console.print("day {day}: 9:00 to 18:00")
      is Saturday -> @console.print("day {day}: 10:00 to 16:00")
      is Sunday -> @console.print("day {day}: closed")
```

```text include="steps/05-bodies/expected/output.txt#L1-L7"
day 1: 9:00 to 18:00
day 2: 9:00 to 18:00
day 3: 9:00 to 18:00
day 4: 9:00 to 18:00
day 5: 9:00 to 18:00
day 6: 10:00 to 16:00
day 7: closed
```

#### An `if` in the body

An `if` without `else` inside the body runs its own lines only on the turns where its condition holds ([section 8.1](/learn/choices/#s8-1)):

```una include="steps/05-bodies/src/week.una#print_deliveries" title="steps/05-bodies/src/week.una"
--- Prints the days a delivery comes, Tuesday and Thursday: an `if` inside a loop.
pub print_deliveries() -> Unit
  uses @console: Console[print]
=
  for day in 1..7
    if day == 2 or day == 4
      @console.print("day {day}: delivery")
```

```text include="steps/05-bodies/expected/output.txt#L8-L9"
day 2: delivery
day 4: delivery
```

Seven turns run, and two of them print. This is how a loop skips a value: the steps that should not run for it go under an `if`.

#### A `let` in the body

A `let` inside the body names a value for one turn. Each turn computes it afresh, from that turn's `week`:

```una include="steps/05-bodies/src/week.una#print_sale" title="steps/05-bodies/src/week.una"
--- Prints the price of a lamp in each of three weeks of a sale: a `let` inside a loop.
pub print_sale(cents: Int) -> Unit
  uses @console: Console[print]
=
  for week in 1..3
    let off = week * 10
    let price = cents - cents * off / 100
    @console.print("week {week}: {off}% off, {price} cents")
```

`print_sale(2_000)` prints:

```text include="steps/05-bodies/expected/output.txt#L10-L12"
week 1: 10% off, 1800 cents
week 2: 20% off, 1600 cents
week 3: 30% off, 1400 cents
```

#### A loop inside a loop

A body may hold another loop. The inner loop runs all its turns during each turn of the outer one, so 2 aisles of 3 shelves give 6 turns of the inner body:

```una include="steps/05-bodies/src/week.una#print_shelf_codes" title="steps/05-bodies/src/week.una"
--- Prints the code of every shelf of the first aisles: a loop inside a loop.
pub print_shelf_codes(aisles: Int, shelves: Int) -> Unit
  uses @console: Console[print]
=
  for aisle in 1..aisles
    for shelf in 1..shelves
      @console.print("A{aisle}-S{shelf}")
```

`print_shelf_codes(2, shelves: 3)` prints:

```text include="steps/05-bodies/expected/output.txt#L13-L18"
A1-S1
A1-S2
A1-S3
A2-S1
A2-S2
A2-S3
```

All the shelves of aisle 1 come first, then all the shelves of aisle 2: the outer loop moves on only when the inner one has finished.

### How a loop behaves

#### Order, and how many turns

- A loop over a range visits its numbers in increasing order, each one once.
- A loop over the characters or the parts of a text visits them in the text's order.
- The range, or the list, is computed once, before the first turn. So the number of turns is fixed when the loop starts. [Section 9.2](#s9-2) shows that changing a name inside the body does not change it.

#### An empty range runs no turn

A range from a number to itself visits that number once with `..`, and nothing with `..<`. A range whose start is above its end visits nothing: Una never counts down. The calls `through(2, last: 2)`, `before(2, last: 2)` and `through(3, last: 1)` each print their heading, and only the first prints an aisle under it:

```text include="steps/03-range-forms/expected/output.txt#L8-L11"
2..2:
  aisle 2
2..<2:
3..1:
```

The same holds for a text: the empty text, `""`, has no characters, and a loop over `"".chars()` runs its body zero times.

#### A text is walked through `chars`, not by itself

A loop walks a range or a list, and a text is neither. Write `for character in sku` in `print_characters`, and `una check .` reports:

```text include="steps/06-text-itself/expected/rendered.txt"
[U2001] Error: expected `List[_]`, found `Text`
   ╭─[ src/skus.una:7:20 ]
   │
 7 │   for character in sku
   │                    ─┬─
   │                     ╰─── expected `List[_]`, found `Text`
   │
   │ Note: run `una explain U2001` for an explanation
───╯
```

The checker expected a list, `List[_]`, after `in`, and found a `Text`. Write `sku.chars()`, which gives the list of its characters.

#### A body has at least one line

The body is the indented block under the `for` line, and it cannot be empty. Leave the line of `print_weeks` unindented, and the loop has no body:

```text include="steps/07-empty-body/expected/rendered.txt#L1"
[U0101] Error: unexpected `@console`, expected an indented block
```

The line after `for` must be indented two spaces deeper than the `for` line.

#### Every turn runs

Una has no `break`, which other languages use to leave a loop early, and no `continue`, which skips the rest of a turn. Every turn of the range runs its body. To skip a value, put the steps under an `if`, as `print_deliveries` does.

#### A loop is a step, not a value

A `for` loop gives no value of its own: it is a **statement**, a step of a block that does something instead of giving a value. What a loop computes either goes out through its steps, as the printing loops of this section do, or stays in names that its body changes, which [section 9.2](#s9-2) introduces. A function whose result is `Unit` may end with a loop, as `print_weeks` does.

A loop's turns are not calls of a function, so a long loop does not count toward the limit on how many calls may wait at once, which [section 16.4](/learn/memory/#s16-4) explains.

### Una has no `while`

Many languages have a second kind of loop, `while`, which repeats its body for as long as a condition holds. Its end depends on the body changing something that the condition reads. When the body forgets to, the loop never ends, and the program hangs.

Una has no `while`. Write one anyway, in a `main` that counts how long the stock lasts:

```diff include="steps/08-weeks-of-stock..steps/09-while:src/stock.una" context="1" title="src/stock.una"
--- a/src/stock.una
+++ b/src/stock.una
@@ -13,3 +13,4 @@
 =
-  @console.print("10 units at 3 a week last {weeks_of_stock(10, per_week: 3)} weeks")
-  @console.print("2 units at 3 a week last {weeks_of_stock(2, per_week: 3)} weeks")
+  let stock = 10
+  while stock >= 3
+    @console.print("one more week")
```

`una check .` reports:

```text include="steps/09-while/expected/rendered.txt"
[U0103] Error: `while` is not a keyword in Una; use `for` or recursion
    ╭─[ src/stock.una:15:3 ]
    │
 15 │   while stock >= 3
    │   ──┬──
    │     ╰──── `while` is not a keyword in Una; use `for` or recursion
    │
    │ Note: run `una explain U0103` for an explanation
────╯
```

The message names the two ways Una repeats work: `for`, and **recursion**, a function that calls itself ([section 6.1](/learn/functions/#s6-1)). This `while` is the bug of the first paragraph, too: its body never lowers `stock`, so the condition never turns false. How many weeks the stock lasts is not known before the loop starts, so a range does not fit, and recursion does:

```una include="steps/08-weeks-of-stock/src/stock.una#weeks_of_stock" title="steps/08-weeks-of-stock/src/stock.una"
--- How many whole weeks `stock` units last when `per_week` units sell each week: a
--- function that calls itself, with less stock each time.
pub weeks_of_stock(stock: Int, per_week: Int) -> Int
  requires per_week >= 1
=
  if stock < per_week then 0 else 1 + weeks_of_stock(stock - per_week, per_week: per_week)
```

```text include="steps/08-weeks-of-stock/expected/output.txt"
10 units at 3 a week last 3 weeks
2 units at 3 a week last 0 weeks
```

With 10 units and 3 sold a week, the function answers 1 + the weeks of 7 units, which is 1 + the weeks of 4 units, which is 1 + the weeks of 1 unit, which is 0: 3 weeks. Each call has less stock, so the calls end, and `requires per_week >= 1` keeps a caller from passing 0, which would never lower the stock ([section 5.1](/learn/contracts/#s5-1)). When you know an upper limit, such as "at most 52 weeks", a range up to that limit with an `if` in the body is the other choice.

Loops that end on a condition, rather than after a number of turns fixed before they start, are planned for a later version of Una.

### Choosing a range, the characters or recursion

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Repeat steps a number of times, counting from 1 | `for n in 1..count` |
| Visit the positions of something numbered from 0 | `for position in 0..<count` |
| Visit each character of a text | `for character in text.chars()` |
| Visit the parts of a text between separators | `for part in text.split(on: separator)` |
| Run some steps only for some turns | an `if` without `else` in the body |
| Repeat until something happens, with no limit known in advance | recursion, with a case that stops it |
| Visit each element of a list | `for` over the list ([section 10.1](/learn/collections/#s10-1)) |
:::

### Check yourself: loops

This program prints the shelves to count this morning:

```una include="steps/10-check-ranges/src/shelves.una" title="src/shelves.una"
module shelves

--- Prints the shelves to count this morning.
pub main() -> Unit
  uses @console: Console[print]
=
  for aisle in 1..2
    for shelf in 2..<4
      @console.print("{aisle}-{shelf}")
  for aisle in 5..4
    @console.print("aisle {aisle}")
  @console.print("done")
```

What does `una run .` print?

:::answer Show the answer
```text include="steps/10-check-ranges/expected/output.txt"
1-2
1-3
2-2
2-3
done
```

The outer loop takes two turns, for aisles 1 and 2. In each, the inner range `2..<4` gives the shelves 2 and 3, since `..<` leaves 4 out. The second loop's range, `5..4`, starts above its end, so it runs no turn, and the program goes on to `done`.
:::

## 9.2 Names that change: `let edit`

### What an editable name is

A plain `let` gives a value a name for good ([section 2.1](/learn/numbers/#s2-1)): like a price printed on a tag, it says the same thing every time you read it. Some values must change as a program runs. Think of the display of a till: it shows a total, and each scanned item changes what it shows. The display is one thing, with one name, whose value moves.

An **editable name** is such a name. You declare it with `let edit`, and an **assignment**, a line of the form `name = value`, gives it a new value. Every later line that reads the name sees the new value.

### Why some names must change

Without editable names, a running total needs a new name for each step:

```una include="steps/11-names-per-scan/src/till.una" title="src/till.una" verified="check, run"
module till

--- Prints the total of a till after each of three scans, with a new name for each total.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = 1_990
  let rug = 4_500
  let after_one = lamp
  let after_two = after_one + lamp
  let after_three = after_two + rug
  @console.print("after one item: {after_one} cents")
  @console.print("after two items: {after_two} cents")
  @console.print("after three items: {after_three} cents")
```

```text include="steps/11-names-per-scan/expected/output.txt"
after one item: 1990 cents
after two items: 3980 cents
after three items: 8480 cents
```

It works for three scans, written out one by one. In a loop it cannot work at all: the body is written once, so it cannot make a new name for each turn. A loop must carry its total from one turn to the next in the same name. Try it with a plain `let`:

```una include="steps/12-plain-let-loop/src/demand.una#demand" title="src/demand.una"
--- The units customers ask for over `weeks` weeks, at `per_week` units a week.
pub demand(weeks: Int, per_week: Int) -> Int
=
  let total = 0
  for week in 1..weeks
    total = total + per_week
  total
```

`una check .` reports:

```text include="steps/12-plain-let-loop/expected/rendered.txt"
[U2019] Error: `total` is not editable; declare it `let edit total`, or the parameter `edit total`
   ╭─[ src/demand.una:8:5 ]
   │
 8 │     total = total + per_week
   │     ──┬──
   │       ╰──── `total` is not editable; declare it `let edit total`, or the parameter `edit total`
   │
   │ Note: run `una explain U2019` for an explanation
───╯
```

The marks point at `total` on the left of the assignment. A name declared with plain `let` is not editable, and the message names the declaration to write instead: `let edit total`. (The message also names an `edit` parameter, a parameter that a function may change for its caller, which [section 16.2](/learn/memory/#s16-2) covers.)

### How to write `let edit` and an assignment

A till adds up the items a cashier scans:

:::steps
```una include="steps/13-till/src/till.una" title="src/till.una" verified="check, run"
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

1. **`let lamp = 1_990`.** A plain name. Its type, `Int`, comes from its value, and its value never changes.
2. **`let edit total = 0`.** An editable name. Its first value is 0, and its type is the type of that value, `Int`.
3. **`total = total + lamp`.** An assignment: the name on the left, `=`, and the new value on the right. The right side is worked out first, from the old value of `total`, and then `total` holds the result. An assignment is a statement, on a line of its own.
4. **`let edit receipt: Text = "LAMP-01"`.** A type written after the name, with `:`, as for a plain `let`. It is optional here, but it tells a reader what the name will hold.
5. **`receipt = "{receipt}, LAMP-01, RUG-07"`.** A text built from the old value: the way to add to the end of a text.
:::

`una run .` prints:

```text include="steps/13-till/expected/output.txt"
2 items, 3980 cents
3 items, 8480 cents
LAMP-01, LAMP-01, RUG-07
```

Read `=` in an assignment as "becomes", not as "is equal to": `total = total + lamp` says "the total becomes the old total plus the lamp". The comparison "is equal to" is `==` ([section 3.3](/learn/text-and-conditions/#s3-3)).

An assignment may also change one field of an editable record ([section 4.1](/learn/kinds/#s4-1)): `restocked.units = restocked.units + per_delivery` gives the record a new `units` and keeps its other fields. [A record that changes](#a-record-that-changes) shows it in a loop.

### Accumulators: what a loop carries from turn to turn

An editable name that a loop builds up turn by turn is an **accumulator**. It is declared before the loop, with the value it should have when the loop takes no turn, and each turn updates it. After the loop, it holds the result. The step for this part has one function per kind of accumulator:

#### A sum

```una include="steps/14-accumulators/src/counts.una#demand" title="steps/14-accumulators/src/counts.una"
--- The units customers ask for over `weeks` weeks, at `per_week` units a week: a sum.
pub demand(weeks: Int, per_week: Int) -> Int
=
  let edit total = 0
  for week in 1..weeks
    total = total + per_week
  total
```

```text include="steps/14-accumulators/expected/output.txt#L1-L2"
demand over 4 weeks: 20
demand over 0 weeks: 0
```

Before the loop, `total` is 0. Each of the 4 turns adds 5, so `total` goes 5, 10, 15, 20, and the last line of the function, `total`, gives that last value back. With 0 weeks, the range `1..0` is empty, no turn runs, and `total` keeps its first value, 0: the right answer, with no special case.

#### A count

```una include="steps/14-accumulators/src/counts.una#dashes_in" title="steps/14-accumulators/src/counts.una"
--- How many dashes a SKU holds: a count.
pub dashes_in(sku: Text) -> Int
=
  let edit count = 0
  for character in sku.chars()
    if character == "-"
      count = count + 1
  count
```

```text include="steps/14-accumulators/expected/output.txt#L3"
dashes in LAMP-01-BR: 2
```

The count goes up only on the turns where the `if` holds: the two dashes of `LAMP-01-BR`.

#### A text that grows

```una include="steps/14-accumulators/src/counts.una#spaced" title="steps/14-accumulators/src/counts.una"
--- A SKU with a space after each character, for a sign that is read from afar: a text that
--- grows.
pub spaced(sku: Text) -> Text
=
  let edit sign = ""
  for character in sku.chars()
    sign = "{sign}{character} "
  sign.trim
```

```text include="steps/14-accumulators/expected/output.txt#L4"
sign: [R U G - 0 7]
```

Each turn adds one character and a space to the end of `sign`. The last turn leaves a space at the end, which `trim` removes before the function gives the text back.

#### A flag

```una include="steps/14-accumulators/src/counts.una#has_digit" title="steps/14-accumulators/src/counts.una"
--- Whether a SKU holds a digit: a flag that a turn may set.
pub has_digit(sku: Text) -> Bool
=
  let edit found = false
  for character in sku.chars()
    if character.is_digits()
      found = true
  found
```

```text include="steps/14-accumulators/expected/output.txt#L5"
a digit in RUG-07: true, in GIFTCARD: false
```

A **flag** is a `Bool` that starts `false` and that a turn sets to `true` when it sees what it looks for. `is_digits`, from the prelude, is `true` when every character of a text is a digit from 0 to 9. Once the flag is `true`, the later turns leave it so. The loop still visits every character, since every turn runs.

#### A record that changes

```una include="steps/14-accumulators/src/counts.una#after_deliveries" title="steps/14-accumulators/src/counts.una"
--- A shelf after `weeks` deliveries of `per_delivery` units: one field of a record changes.
pub after_deliveries(shelf: Shelf, weeks: Int, per_delivery: Int) -> Shelf
=
  let edit restocked = shelf
  for week in 1..weeks
    restocked.units = restocked.units + per_delivery
  restocked
```

```text include="steps/14-accumulators/expected/output.txt#L6"
aisle 3: 16 units
```

`let edit restocked = shelf` makes an editable copy of the parameter. Each turn changes its field `units`, and its `aisle` stays 3. The caller's shelf does not change: the function changes its own copy and gives it back.

### How editable names behave

#### A name lives to the end of its block

A **block** is a run of lines at the same indentation, such as the body of a function or of a loop. A name exists from its `let` line to the end of its block, and a line before the `let` cannot use it. This is why an accumulator is declared before its loop: a name declared inside the body would end with each turn.

#### One name, one meaning: no shadowing

Making a name that another `let` of the same body already made is an error, even with `let` both times:

```diff include="steps/13-till..steps/15-rebind:src/till.una" title="src/till.una" context="1"
--- a/src/till.una
+++ b/src/till.una
@@ -7,2 +7,3 @@
   let lamp = 1_990
+  let lamp = 2_490
   let edit total = 0
```

```text include="steps/15-rebind/expected/rendered.txt"
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

The diagnostic marks both lines: where the name was first defined, and where it was made again. Its **scope** is the stretch of code where a name can be used: here, the body of `main`. Some languages allow the second `let`, which **shadows** the first: the old value is still there, hidden behind the new one. Una does not, in a block or in a block nested in it, such as a loop's body. So a name means one thing from its line to the end of its block. To change a value, use `let edit` and an assignment; for a different value, choose a different name.

#### An editable name keeps its type

`let edit items = 0` makes `items` an `Int` for good. Assign it a text:

```diff include="steps/13-till..steps/16-edit-type:src/till.una" title="src/till.una" context="1"
--- a/src/till.una
+++ b/src/till.una
@@ -10,3 +10,3 @@
   total = total + lamp
-  items = items + 1
+  items = "one"
   total = total + lamp
```

```text include="steps/16-edit-type/expected/rendered.txt#L1"
[U2001] Error: expected `Int`, found `Text`
```

The checker expected an `Int`, the type of `items`, and found a `Text`. Every value an editable name takes must have the type it was declared with.

#### A name made in the body is new at each turn

A `let` inside a loop's body, such as `let price` in `print_sale` ([section 9.1](#s9-1)), is made afresh at each turn and is gone after it. It is a plain name: within its turn it does not change. To carry a value from one turn to the next, or out of the loop, declare it before the loop with `let edit`.

#### The loop variable is not editable

The loop variable is a plain name: each turn gives it the next value, and the body only reads it. Assign it, to skip a week:

```diff include="steps/14-accumulators..steps/17-loop-variable:src/counts.una" title="src/counts.una" context="1"
--- a/src/counts.una
+++ b/src/counts.una
@@ -13,2 +13,3 @@
     total = total + per_week
+    week = week + 1
   total
```

```text include="steps/17-loop-variable/expected/rendered.txt#L1"
[U2019] Error: `week` is the variable of a `for` loop, which is read-only; bind a copy in the body with `let edit`, as `let edit next_week = week`
```

The message says why: the loop owns its variable, which is read-only, so it cannot be declared `let edit`. What it offers is a copy, `let edit next_week = week`, a new name in the body that starts at the loop variable's value and may change within the turn; it does not change the turns the loop takes. To skip turns, put the steps under an `if`; to walk every second week, compute it from the loop variable, such as `let other = week * 2`.

#### The range is fixed before the first turn

A loop computes its range once, before the first turn. A body that changes a name used in the range does not change how many turns the loop takes:

```una include="steps/14-accumulators/src/counts.una#turns_taken" title="steps/14-accumulators/src/counts.una"
--- How many turns a loop takes when its body moves the end of its own range: the range
--- was computed before the first turn, so the change does not add a turn.
pub turns_taken(last: Int) -> Int
=
  let edit end = last
  let edit turns = 0
  for aisle in 1..end
    end = end + 1
    turns = turns + 1
  turns
```

```text include="steps/14-accumulators/expected/output.txt#L7"
turns of 1..3: 3
```

Each turn moves `end` one further, and the loop still takes the 3 turns of `1..3`, the range it had when it started.

> [!NOTE]
> `let edit` belongs to edition `0.2` and later. In a package of edition `0.1`, `edit` is a reserved word, and every name is a plain `let`.

### Choosing between `let` and `let edit`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| Name a value you compute once | `let` |
| Keep a total, a count, a flag or a text that a loop builds | `let edit`, declared before the loop |
| Name a value for one turn of a loop | `let`, inside the body |
| Say what type a name holds | `let name: Type = …`, with either form |
| A value that differs by case | `let` with an `if … then … else`, not a `let edit` assigned in two places |
:::

Prefer `let`. A name that cannot change is one less thing a reader must track, and in most functions every name can be a plain `let`. Use `let edit` when a value really accumulates, as `total` does in a loop.

### Check yourself: names

A shelf holds 10 units. Three are sold, then a delivery brings five:

```una include="steps/18-restock/src/restock.una" title="src/restock.una"
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
```text include="steps/18-restock/expected/output.txt"
12 in stock, 3 sold
```

`stock` goes 10, 7, 12. `sold` is computed once, when `stock` is 7, so it is 3, and it stays 3 when `stock` changes later: a plain `let` holds the value it was given, not a formula.
:::

## 9.3 What a loop keeps and what the verifier knows

### What the verifier knows inside a loop

The verifier proves the rules of a program before it runs: preconditions, postconditions and refined kinds ([chapter 5](/learn/contracts/)). For a loop it faces a problem: the body runs once for each value of a range that it may only learn when the program runs. So the verifier does not follow a loop turn by turn. It checks the body **once, for any turn at all**.

Think of a rule for the clerk who counts the aisles: "after each aisle, the count on your sheet is not negative". You can check that rule for one aisle without knowing which aisle it is or how many came before: if the count was not negative before the aisle, and the aisle only adds, it is not negative after it. That is how the verifier reads a loop. What it knows at the start of a turn is only what holds at the start of every turn.

### When a loop forgets a fact

Here `demand` gives back `Units`, a number that is never negative, and its total is a plain `Int`:

```una include="steps/19-loop-forgets/src/demand.una#Units..demand" title="steps/19-loop-forgets/src/demand.una"
--- A number of units. It is never negative.
kind Units = Int where it >= 0

--- The units customers ask for over `weeks` weeks, at `per_week` units a week.
pub demand(weeks: Int, per_week: Units) -> Units
=
  let edit total = 0
  for week in 1..weeks
    total = total + per_week
  total
```

`una check .` reports:

```text include="steps/19-loop-forgets/expected/rendered.txt#L1"
[U5002] Error: refinement `result >= 0` could not be proven (the loop forgets every fact about `total` but the refinements of its type, so the counterexample sets `total` freely; guard the use with an `if`, or move the update into a helper with an `edit` parameter whose `ensures` states what the use needs)
```

The total starts at 0 and only adds `per_week`, which is never negative, so it is never negative either. But the proof is missing, and the reason in parentheses says why: "the loop forgets every fact about `total` but the refinements of its type". A **refinement** is the rule a refined kind adds to its base type, such as `it >= 0` for `Units` ([section 5.3](/learn/contracts/#s5-3)). `total` is a plain `Int`, which has none. So at the start of a turn, as far as the verifier knows, `total` could be any whole number, and after the loop too: the result might be negative. The code is not wrong; the fact is not where the verifier looks for it. It is U5002, "could not be proven", not U5001, "refuted" ([section 5.4](/learn/contracts/#s5-4)), since no real run breaks the rule.

### Keeping a fact through the loop: a refined type

The fact the result needs, "not negative", can be the type of the accumulator:

```diff include="steps/19-loop-forgets..steps/20-loop-keeps:src/demand.una" context="1" title="src/demand.una"
--- a/src/demand.una
+++ b/src/demand.una
@@ -8,3 +8,3 @@
 =
-  let edit total = 0
+  let edit total: Units = 0
   for week in 1..weeks
```

Now `total` is a `Units`, and the step checks and prints:

```text include="steps/20-loop-keeps/expected/output.txt"
20 units
```

Two proofs make this work. First, each assignment to `total` must give it a `Units`, as every value of a refined type must be. `total + per_week` is a sum of two numbers that are not negative, so the verifier proves it at every turn. Second, since every assignment keeps `total` a `Units`, the verifier knows at the start of every turn, and after the loop, that `total >= 0`. A type written on an editable name is a rule that holds at every turn: in other books, a **loop invariant**.

### What the body knows

Inside the body, the verifier knows more than the types of the names the loop changes.

#### The loop variable lies in its range

In a loop over a range, the loop variable lies between the range's ends at every turn: in `for position in 0..<sku.len`, the verifier knows that `0 <= position` and `position < sku.len`. That proves a cut of the text at the position:

```una include="steps/21-body-facts/src/signs.una#spaced" title="steps/21-body-facts/src/signs.una"
--- A SKU with a space after each character, for a sign that is read from afar. Each turn
--- cuts one character out of the SKU, at a position the range keeps inside it.
pub spaced(sku: Text) -> Text
=
  let edit sign = ""
  for position in 0..<sku.len
    sign = "{sign}{sku.slice(start: position, end: position + 1)} "
  sign.trim
```

`slice` requires its positions to lie inside the text ([section 3.2](/learn/text-and-conditions/#s3-2)): here `position + 1 <= sku.len`, which follows from `position < sku.len`. Change the range to `0..sku.len`, which also visits the position `sku.len`, one past the last character:

```text include="steps/22-one-too-far/expected/rendered.txt#L1-L6,L8,L14"
[U5001] Error: precondition `0 <= position and position <= (position + 1) and (position + 1) <= sku.len` of this call is refuted
   ╭─[ src/signs.una:9:20 ]
   │
 9 │     sign = "{sign}{sku.slice(start: position, end: position + 1)} "
   │                    ──────────────────────┬──────────────────────
   │                                          ╰──────────────────────── precondition `0 <= position and position <= (position + 1) and (position + 1) <= sku.len` of this call is refuted
   │ Help 1: repair 1: add a guard (`if` or a `when` arm) that handles the values where `0 <= position and position <= (position + 1) and (position + 1) <= sku.len` does not hold
   │ Note 2: counterexample: position = 0, sign = "", sku = Text#1, sku.len = 0
```

This one is U5001, refuted, with a real counterexample: an empty SKU, whose length is 0. The range `0..0` visits the position 0, and the text has no character there. The marks point at the call of `slice`. The `Help` line proposes a guard around the call, which would work, but the mistake is in the range: `..<` is the fix, and every position it visits is inside the text.

#### Facts from before the loop stay

Names that the loop does not change keep what the verifier knew about them before it. A `requires` on a parameter holds in every turn:

```una include="steps/21-body-facts/src/signs.una#boxes" title="steps/21-body-facts/src/signs.una"
--- The boxes needed over `weeks` weeks, when each week `units` units arrive in boxes of
--- `per_box`. The division is proved in every turn by the `requires`, a fact from before the
--- loop.
pub boxes(weeks: Int, units: Int, per_box: Int) -> Int
  requires per_box >= 1
=
  let edit count = 0
  for week in 1..weeks
    count = count + (units + per_box - 1) / per_box
  count
```

The division by `per_box`, a value that is not a literal, must be proven safe ([section 2.2](/learn/numbers/#s2-2)). No turn changes `per_box`, so `per_box >= 1` from the `requires` holds in each one, and the division checks. `main` prints both results:

```text include="steps/21-body-facts/expected/output.txt"
[R U G - 0 7]
9 boxes
```

The rule: what the body knows is the facts of the code around the loop, the range of the loop variable, and the refined types of the names the loop changes. What it does not know is the value those names had at the end of the turn before.

### Each assignment is proved

Every assignment to an editable name of a refined type must give it a value of that type, and the verifier proves it at the line of the assignment. A shelf that sells the same amount every week:

```una include="steps/23-stock-below-zero/src/shelf.una#left_after" title="steps/23-stock-below-zero/src/shelf.una"
--- The units left on a shelf after `weeks` weeks of sales, at `per_week` units a week.
pub left_after(start: Units, weeks: Int, per_week: Units) -> Units
=
  let edit stock: Units = start
  for week in 1..weeks
    stock = stock - per_week
  stock
```

`una check .` reports:

```text include="steps/23-stock-below-zero/expected/rendered.txt#L1-L10,L12,L18"
[U5001] Error: refinement `(stock - per_week) >= 0` is refuted
    ╭─[ src/shelf.una:11:13 ]
    │
  4 │ kind Units = Int where it >= 0
    │                        ───┬───
    │                           ╰───── where clause
    │
 11 │     stock = stock - per_week
    │             ────────┬───────
    │                     ╰───────── refinement `(stock - per_week) >= 0` is refuted
    │ Help 1: repair 1: add a guard (`if` or a `when` arm) that handles the values where `(stock - per_week) >= 0` does not hold
    │ Note 2: counterexample: per_week = 1, start = 0, stock = 0, stock (assigned) = -1, week = 1, weeks = 1
```

Here the rule really breaks, so it is U5001 with a counterexample: a shelf with `start = 0` and `per_week = 1`, for one week. The line `stock (assigned) = -1` is the value the assignment would give, below zero. The repair is the guard that the `Help` line proposes ([section 8.3](/learn/choices/#s8-3)): a shelf cannot sell more than it holds.

```diff include="steps/23-stock-below-zero..steps/24-stock-guarded:src/shelf.una" context="1" title="src/shelf.una"
--- a/src/shelf.una
+++ b/src/shelf.una
@@ -10,3 +10,3 @@
   for week in 1..weeks
-    stock = stock - per_week
+    stock = if stock >= per_week then stock - per_week else 0
   stock
```

In the branch where `stock >= per_week` holds, the difference is not negative, and the other branch gives 0. The step checks, and prints:

```text include="steps/24-stock-guarded/expected/output.txt"
8 units left
0 units left
```

A shelf of 5 units that sells 4 a week has 1 left after the first week, and 0 after the second and third.

### How the loop check behaves

- **The body is checked once.** The verifier checks it for any turn, with the names the loop changes holding any value of their types.
- **After the loop**, those names again hold any value of their types: no fact about their values survives, only their refined types.
- **The rest stays.** Names the loop does not change, and the facts about them, are the same in every turn and after the loop.
- **The loop variable** of a range loop lies between the range's ends, as a fact the body knows.
- **Every assignment is proved** against the type of its name, so an editable name of a refined type never holds a value outside it.
- **Unknown or refuted.** When the only values that break a rule come from forgetting, the verifier reports U5002, "could not be proven". When a real run breaks it, U5001, "refuted", with a counterexample.

The reason of a U5002 from a loop names one more repair: "move the update into a helper with an `edit` parameter whose `ensures` states what the use needs". The postcondition of such a helper tells the verifier what one call did to the name, in the turn that makes the call; [section 16.2](/learn/memory/#s16-2) covers `edit` parameters.

### A refined type, a guard or a helper

:::decide
**Which to use:**

| The fact the code after the loop needs… | Use |
| --- | --- |
| Holds of every value the name takes, such as "never negative" | a refined type on the name: `let edit total: Units = 0` |
| Could break at one assignment, such as a stock that sells more than it holds | a guard at that assignment: `if stock >= per_week then … else 0` |
| Is about the loop variable and the range | nothing: the body knows it, if the range is right (`..<` for positions) |
| Is about a name the loop does not change | nothing: it stays |
| Depends on the number of turns, such as "exactly 5 units per week" | an example ([section 9.5](#s9-5)): the verifier forgets how many turns ran |
:::

### Check yourself: what a loop keeps

This function counts the days the store stays open late:

```una include="steps/25-late-days/src/hours.una#late_days" title="src/hours.una"
--- How many days of the week the store stays open late, from day `first_day` on, counting
--- Monday as day 1.
pub late_days(first_day: Int) -> Int in 0..7
=
  let edit count: Int in 0..7 = 0
  for day in 1..7
    if day >= first_day
      count = count + 1
  count
```

Does `una check .` pass, and if not, is it U5001 or U5002?

:::answer Show the answer
No, and it is U5002:

```text include="steps/25-late-days/expected/rendered.txt#L1"
[U5002] Error: refinement `(count + 1) in 0..7` could not be proven (the loop forgets every fact about `count` but the refinements of its type, so the counterexample sets `count` freely; guard the use with an `if`, or move the update into a helper with an `edit` parameter whose `ensures` states what the use needs)
```

The verifier checks the body for any turn, with `count` holding any value of its type, `Int in 0..7`. For `count = 7`, `count + 1` is 8, outside the range. No real run gets there, since the loop takes 7 turns and adds at most one per turn, but that fact depends on the number of turns, which the verifier forgets. So the proof is missing, not refuted. A guard is the repair: `count = if count < 7 then count + 1 else 7`.
:::

## 9.4 Day-to-day: a weekly restock plan

### What the program must do

Every week, a store sells some units of each product, and when a shelf runs low, it orders more. A restock plan looks ahead: for the next weeks, it follows the stock of each product and shows when to order. For each product, the plan knows:

- its SKU and the stock on hand today;
- how many units sell in a week;
- the **reorder point**: when a week ends with fewer units than this, the store orders more;
- the **batch**: how many units one order brings. An order placed at the end of a week arrives before the next week starts.

For each week, the plan prints the units left after the week's sales and the order, if any. For each product, it ends with the units ordered and the number of weeks that started with too few units for the week's sales. The program is one module, `restock`, in a package whose `una.toml` names it as the entry and grants the console:

```toml include="day-to-day/una.toml" title="day-to-day/una.toml"
[package]
name = "restock"
version = "0.1.0"
edition = "0.2"

[run]
entry = "restock"
grants = ["console"]
```

### The kinds and the products

```una include="day-to-day/src/restock.una#Units..desk" title="day-to-day/src/restock.una" caption="the kinds and the products" verified="check"
--- A number of units. It is never negative.
kind Units = Int where it >= 0

--- What the plan knows about one product: its stock today, how many units sell in a week,
--- the stock below which the store orders more, and how many units one order brings.
kind Product
  sku: Text
  on_hand: Units
  weekly_sales: Units
  reorder_at: Units
  batch: Units

--- The desk lamp, which sells fast.
pub lamp() -> Product = Product(sku: "LAMP-01", on_hand: 14, weekly_sales: 5, reorder_at: 6, batch: 10)

--- The wool rug, which sells slowly.
pub rug() -> Product = Product(sku: "RUG-07", on_hand: 3, weekly_sales: 2, reorder_at: 2, batch: 4)

--- The oak desk, whose orders are too small for its sales.
pub desk() -> Product = Product(sku: "DESK-02", on_hand: 2, weekly_sales: 3, reorder_at: 3, batch: 2)
```

`Units` is a refined kind: a number of units is never negative. Every number of `Product` is a `Units`, so a product with a negative stock cannot be built. The three products are functions that give back a record, so that `main` and the examples share them. The desk is set up to show a problem: it sells 3 a week, and an order brings only 2.

### The department of a SKU: a loop over characters

The plan prints each product's department, the part of its SKU before the first dash:

```una include="day-to-day/src/restock.una#department" title="day-to-day/src/restock.una" verified="check"
--- The department of a SKU: its characters before the first dash, such as `LAMP` for
--- `LAMP-01`.
pub department(sku: Text) -> Text
=
  let edit code = ""
  let edit past_dash = false
  for character in sku.chars()
    if character == "-"
      past_dash = true
    if not past_dash
      code = "{code}{character}"
  code
```

Two accumulators work together. `code` is a text that grows, and `past_dash` is a flag. Each turn first looks at its character: a dash sets the flag. Then, while the flag is still `false`, the character joins the code. The dash itself is not added, since the flag is already set when the second `if` reads it. A SKU without a dash, such as `GIFTCARD`, never sets the flag, so the whole SKU is its department.

### One week: selling and ordering

Two small functions say what one week does:

```una include="day-to-day/src/restock.una#sell_week..order_for" title="day-to-day/src/restock.una" verified="check"
--- The stock after one week of sales. A shelf cannot sell more than it holds.
pub sell_week(stock: Units, sales: Units) -> Units = if stock >= sales then stock - sales else 0

--- The units to order at the end of a week: a batch when the stock is below the reorder
--- point, and nothing otherwise.
pub order_for(product: Product, stock: Units) -> Units
=
  if stock < product.reorder_at
    product.batch
  else
    0
```

`sell_week` is the guard of [Each assignment is proved](#each-assignment-is-proved), made a function of its own: a shelf cannot sell more than it holds, so the result is never below 0 and is a `Units`. `order_for` gives a batch when the stock is below the reorder point, and 0 otherwise. Neither has a loop: each is one step, which the loops call and the examples test on its own.

### The plan: loops over the weeks

Three functions walk the weeks, each for one result:

```una include="day-to-day/src/restock.una#stock_after..weeks_short" title="day-to-day/src/restock.una" caption="three loops over the weeks" verified="check"
--- The stock at the end of `weeks` weeks. Each week sells, then the week's order arrives.
pub stock_after(product: Product, weeks: Int) -> Units
=
  let edit stock: Units = product.on_hand
  for week in 1..weeks
    stock = sell_week(stock, sales: product.weekly_sales)
    stock = stock + order_for(product, stock: stock)
  stock

--- The units ordered over `weeks` weeks.
pub units_ordered(product: Product, weeks: Int) -> Units
=
  let edit stock: Units = product.on_hand
  let edit ordered: Units = 0
  for week in 1..weeks
    stock = sell_week(stock, sales: product.weekly_sales)
    let order = order_for(product, stock: stock)
    stock = stock + order
    ordered = ordered + order
  ordered

--- How many of the `weeks` weeks start with too few units for the week's sales.
pub weeks_short(product: Product, weeks: Int) -> Int
=
  let edit stock: Units = product.on_hand
  let edit short = 0
  for week in 1..weeks
    if stock < product.weekly_sales
      short = short + 1
    stock = sell_week(stock, sales: product.weekly_sales)
    stock = stock + order_for(product, stock: stock)
  short
```

Each has the same accumulator: `let edit stock: Units = product.on_hand`, the stock today, which each turn sells from and then restocks. The type `Units` is what lets the verifier prove each function's result. In `stock_after`, the result is `stock`, a `Units` at every turn. In `units_ordered`, a second accumulator, `ordered`, adds each week's order, and it is a `Units` too: without that type, the loop would forget that it is never negative, as [An accumulator without its refined type](#an-accumulator-without-its-refined-type-u5002) shows.

Each turn uses `sell_week` and `order_for` rather than writing their steps again, so the rule for one week lives in one place. `units_ordered` names the week's order with a `let` in the body, new at each turn, because it uses it twice. `weeks_short` counts with a plain `Int`, since its result is a plain `Int` and needs no fact. Its `if` looks at the stock before the week's sales.

None of the three uses the loop variable `week`: each turn is one week, and only the number of turns matters. With 0 weeks, each loop runs no turn and gives back its first value.

### Printing the plan

```una include="day-to-day/src/restock.una#plan_line..main" title="day-to-day/src/restock.una" caption="the functions that print" verified="check, run"
--- One line of the plan: the week, the units left after its sales, and its order, if any.
pub plan_line(week: Int, left: Units, order: Units) -> Text
=
  if order > 0
    "  week {week}: {left} left, order {order}"
  else
    "  week {week}: {left} left"

--- Prints the plan of one product, week by week, then its totals.
print_plan(product: Product, weeks: Int) -> Unit
  uses @console: Console[print]
=
  @console.print("{product.sku}, {department(product.sku)}")
  let edit stock: Units = product.on_hand
  for week in 1..weeks
    stock = sell_week(stock, sales: product.weekly_sales)
    let order = order_for(product, stock: stock)
    @console.print(plan_line(week, left: stock, order: order))
    stock = stock + order
  let ordered = units_ordered(product, weeks: weeks)
  let short = weeks_short(product, weeks: weeks)
  @console.print("  {ordered} units ordered, {short} weeks short")

--- Prints the restock plan of the next four weeks.
pub main() -> Unit
  uses @console: Console[print]
=
  let weeks = 4
  @console.print("Restock plan, {weeks} weeks")
  print_plan(lamp(), weeks: weeks)
  print_plan(rug(), weeks: weeks)
  print_plan(desk(), weeks: weeks)
```

`plan_line` builds the text of one week, with the order only when there is one. `print_plan` walks the weeks once more, with the same accumulator, and prints a line at each turn: the week's number, from the loop variable, the units left and the order. After the loop, it prints the totals, which `units_ordered` and `weeks_short` compute. `main` sets the number of weeks once, in `weeks`, and plans each product.

### Running it

In the `day-to-day` directory:

```sh
una check .
una run .
```

`una check .` prints nothing, and `una run .` prints the plan:

```text include="day-to-day/expected/output.txt"
Restock plan, 4 weeks
LAMP-01, LAMP
  week 1: 9 left
  week 2: 4 left, order 10
  week 3: 9 left
  week 4: 4 left, order 10
  20 units ordered, 0 weeks short
RUG-07, RUG
  week 1: 1 left, order 4
  week 2: 3 left
  week 3: 1 left, order 4
  week 4: 3 left
  8 units ordered, 0 weeks short
DESK-02, DESK
  week 1: 0 left, order 2
  week 2: 0 left, order 2
  week 3: 0 left, order 2
  week 4: 0 left, order 2
  8 units ordered, 4 weeks short
```

Read the lamp's plan: 14 units, minus 5, leave 9, which is not below 6, so no order. The next week leaves 4, below 6, so the store orders 10, and the third week starts with 14 again. The desk's plan shows the problem it was set up for: it starts every week with 2 units, fewer than the 3 it sells, so it is short all 4 weeks. A larger batch fixes it.

### The whole program

```una include="day-to-day/src/restock.una" title="day-to-day/src/restock.una" caption="the whole program" verified="check, run, test"
module restock

-- The weekly restock plan of the store: for each product, the stock at the end of each week,
-- and the orders that keep its shelf from running empty.

--- A number of units. It is never negative.
kind Units = Int where it >= 0

--- What the plan knows about one product: its stock today, how many units sell in a week,
--- the stock below which the store orders more, and how many units one order brings.
kind Product
  sku: Text
  on_hand: Units
  weekly_sales: Units
  reorder_at: Units
  batch: Units

--- The desk lamp, which sells fast.
pub lamp() -> Product = Product(sku: "LAMP-01", on_hand: 14, weekly_sales: 5, reorder_at: 6, batch: 10)

--- The wool rug, which sells slowly.
pub rug() -> Product = Product(sku: "RUG-07", on_hand: 3, weekly_sales: 2, reorder_at: 2, batch: 4)

--- The oak desk, whose orders are too small for its sales.
pub desk() -> Product = Product(sku: "DESK-02", on_hand: 2, weekly_sales: 3, reorder_at: 3, batch: 2)

--- The department of a SKU: its characters before the first dash, such as `LAMP` for
--- `LAMP-01`.
pub department(sku: Text) -> Text
=
  let edit code = ""
  let edit past_dash = false
  for character in sku.chars()
    if character == "-"
      past_dash = true
    if not past_dash
      code = "{code}{character}"
  code

--- The stock after one week of sales. A shelf cannot sell more than it holds.
pub sell_week(stock: Units, sales: Units) -> Units = if stock >= sales then stock - sales else 0

--- The units to order at the end of a week: a batch when the stock is below the reorder
--- point, and nothing otherwise.
pub order_for(product: Product, stock: Units) -> Units
=
  if stock < product.reorder_at
    product.batch
  else
    0

--- The stock at the end of `weeks` weeks. Each week sells, then the week's order arrives.
pub stock_after(product: Product, weeks: Int) -> Units
=
  let edit stock: Units = product.on_hand
  for week in 1..weeks
    stock = sell_week(stock, sales: product.weekly_sales)
    stock = stock + order_for(product, stock: stock)
  stock

--- The units ordered over `weeks` weeks.
pub units_ordered(product: Product, weeks: Int) -> Units
=
  let edit stock: Units = product.on_hand
  let edit ordered: Units = 0
  for week in 1..weeks
    stock = sell_week(stock, sales: product.weekly_sales)
    let order = order_for(product, stock: stock)
    stock = stock + order
    ordered = ordered + order
  ordered

--- How many of the `weeks` weeks start with too few units for the week's sales.
pub weeks_short(product: Product, weeks: Int) -> Int
=
  let edit stock: Units = product.on_hand
  let edit short = 0
  for week in 1..weeks
    if stock < product.weekly_sales
      short = short + 1
    stock = sell_week(stock, sales: product.weekly_sales)
    stock = stock + order_for(product, stock: stock)
  short

--- One line of the plan: the week, the units left after its sales, and its order, if any.
pub plan_line(week: Int, left: Units, order: Units) -> Text
=
  if order > 0
    "  week {week}: {left} left, order {order}"
  else
    "  week {week}: {left} left"

--- Prints the plan of one product, week by week, then its totals.
print_plan(product: Product, weeks: Int) -> Unit
  uses @console: Console[print]
=
  @console.print("{product.sku}, {department(product.sku)}")
  let edit stock: Units = product.on_hand
  for week in 1..weeks
    stock = sell_week(stock, sales: product.weekly_sales)
    let order = order_for(product, stock: stock)
    @console.print(plan_line(week, left: stock, order: order))
    stock = stock + order
  let ordered = units_ordered(product, weeks: weeks)
  let short = weeks_short(product, weeks: weeks)
  @console.print("  {ordered} units ordered, {short} weeks short")

--- Prints the restock plan of the next four weeks.
pub main() -> Unit
  uses @console: Console[print]
=
  let weeks = 4
  @console.print("Restock plan, {weeks} weeks")
  print_plan(lamp(), weeks: weeks)
  print_plan(rug(), weeks: weeks)
  print_plan(desk(), weeks: weeks)

example "a department is the part of the SKU before its dash"
  do department("LAMP-01")
  expect result == "LAMP"

example "a SKU without a dash is its own department"
  do department("GIFTCARD")
  expect result == "GIFTCARD"

example "a week sells its sales from the stock"
  do sell_week(9, sales: 5)
  expect result == 4

example "a shelf cannot sell more than it holds"
  do sell_week(3, sales: 5)
  expect result == 0

example "a stock below the reorder point orders a batch"
  do order_for(lamp(), stock: 4)
  expect result == 10

example "a stock at the reorder point orders nothing"
  do order_for(lamp(), stock: 6)
  expect result == 0

example "a plan of no weeks leaves the stock as it is"
  do stock_after(lamp(), weeks: 0)
  expect result == 14

example "the lamp ends four weeks with 14 units"
  do stock_after(lamp(), weeks: 4)
  expect result == 14

example "the lamp orders two batches in four weeks"
  do units_ordered(lamp(), weeks: 4)
  expect result == 20

example "the lamp is never short"
  do weeks_short(lamp(), weeks: 4)
  expect result == 0

example "the desk is short every week"
  do weeks_short(desk(), weeks: 4)
  expect result == 4

example "a week with an order says how many units"
  do plan_line(2, left: 4, order: 10)
  expect result == "  week 2: 4 left, order 10"
```

## 9.5 Testing it

### The single steps and their edges

The functions with no loop get an example for each side of their choice:

```una include="day-to-day/src/restock.una#L126-L140" title="day-to-day/src/restock.una" caption="selling and ordering"
example "a week sells its sales from the stock"
  do sell_week(9, sales: 5)
  expect result == 4

example "a shelf cannot sell more than it holds"
  do sell_week(3, sales: 5)
  expect result == 0

example "a stock below the reorder point orders a batch"
  do order_for(lamp(), stock: 4)
  expect result == 10

example "a stock at the reorder point orders nothing"
  do order_for(lamp(), stock: 6)
  expect result == 0
```

`sell_week` is tested where the stock is enough and where it is not. `order_for` is tested just below the reorder point and exactly at it, where nothing is ordered: the edge where a `<` written as `<=` would be caught.

### The loops, with no weeks and with many

A loop gets an example where it runs no turn, and examples where it runs several:

```una include="day-to-day/src/restock.una#L142-L160" title="day-to-day/src/restock.una" caption="the loops"
example "a plan of no weeks leaves the stock as it is"
  do stock_after(lamp(), weeks: 0)
  expect result == 14

example "the lamp ends four weeks with 14 units"
  do stock_after(lamp(), weeks: 4)
  expect result == 14

example "the lamp orders two batches in four weeks"
  do units_ordered(lamp(), weeks: 4)
  expect result == 20

example "the lamp is never short"
  do weeks_short(lamp(), weeks: 4)
  expect result == 0

example "the desk is short every week"
  do weeks_short(desk(), weeks: 4)
  expect result == 4
```

The plan of 0 weeks checks the first value of the accumulator, which is the whole answer when the range is empty. The others pin the results of four weeks. The verifier proves that each result is a `Units`; it does not prove that the lamp ends with 14 units, since that depends on the number of turns. An example states it. `department` gets one example with a dash and one without, so the flag is tested both ways.

### Running the examples

In the `day-to-day` directory, `una test .` checks the package, then runs the examples:

```text include="day-to-day/expected/commands/test.txt#L2-L15"
example restock "a department is the part of the SKU before its dash" ... ok
example restock "a SKU without a dash is its own department" ... ok
example restock "a week sells its sales from the stock" ... ok
example restock "a shelf cannot sell more than it holds" ... ok
example restock "a stock below the reorder point orders a batch" ... ok
example restock "a stock at the reorder point orders nothing" ... ok
example restock "a plan of no weeks leaves the stock as it is" ... ok
example restock "the lamp ends four weeks with 14 units" ... ok
example restock "the lamp orders two batches in four weeks" ... ok
example restock "the lamp is never short" ... ok
example restock "the desk is short every week" ... ok
example restock "a week with an order says how many units" ... ok

12 examples: 12 passed, 0 failed
```

Each example names what it shows, so a failing line of the report says which rule broke. The examples leave out `print_plan` and `main`, which print. They print only what the tested functions give back, and an example of a function that prints needs a stand-in for the console, which [section 14.3](/learn/testing/#s14-3) shows.

## 9.6 Common mistakes

Each mistake is a small change to `day-to-day/src/restock.una`, followed by what `una check .` reports.

### Assigning a plain `let` (U2019)

:::mistake
Declare the accumulator of `stock_after` with `let`:

```diff include="day-to-day..mistakes/1:src/restock.una" context="1"
--- a/src/restock.una
+++ b/src/restock.una
@@ -54,3 +54,3 @@
 =
-  let edit stock: Units = product.on_hand
+  let stock: Units = product.on_hand
   for week in 1..weeks
```

```text include="mistakes/1/expected/rendered.txt#L1-L9"
[U2019] Error: `stock` is not editable; declare it `let edit stock`, or the parameter `edit stock`
    ╭─[ src/restock.una:57:5 ]
    │
 57 │     stock = sell_week(stock, sales: product.weekly_sales)
    │     ──┬──
    │       ╰──── `stock` is not editable; declare it `let edit stock`, or the parameter `edit stock`
    │
    │ Note: run `una explain U2019` for an explanation
────╯
```

*Why:* a name declared with plain `let` holds one value for good, and only a name declared `let edit` can be assigned. The loop assigns `stock` twice in its body, so there are two diagnostics, one at each assignment; the first is shown. The marks point at the name on the left of the assignment.

*Fix:* `let edit stock: Units = product.on_hand`, as the message says. See [U2019](/docs/errors/U2019/).
:::

### A second `let` inside the loop (U1002, U2019)

:::mistake
Make the stock after the sales a new `let` inside the body:

```diff include="day-to-day..mistakes/2:src/restock.una" context="1"
--- a/src/restock.una
+++ b/src/restock.una
@@ -56,3 +56,3 @@
   for week in 1..weeks
-    stock = sell_week(stock, sales: product.weekly_sales)
+    let stock = sell_week(stock, sales: product.weekly_sales)
     stock = stock + order_for(product, stock: stock)
```

```text include="mistakes/2/expected/rendered.txt#L1-L13"
[U1002] Error: `stock` is already bound in this scope; a local cannot rebind another
    ╭─[ src/restock.una:57:9 ]
    │
 55 │   let edit stock: Units = product.on_hand
    │            ──┬──
    │              ╰──── first defined here
    │
 57 │     let stock = sell_week(stock, sales: product.weekly_sales)
    │         ──┬──
    │           ╰──── `stock` is already bound in this scope; a local cannot rebind another
    │
    │ Note: run `una explain U1002` for an explanation
────╯
```

*Why:* the body is a block nested in the function's body, where `stock` is already a name, and Una lets no name shadow another. The diagnostic marks both: where `stock` was first defined, and the new `let`. A second diagnostic, U2019, follows at the next line: `stock = stock + …` now names the new, plain `stock`, which cannot be assigned.

*Fix:* assign the name the loop carries, `stock = sell_week(…)`, without `let`. See [U1002](/docs/errors/U1002/).
:::

### Walking a text without `chars` (U2001)

:::mistake
Walk the SKU itself in `department`:

```diff include="day-to-day..mistakes/3:src/restock.una" context="1"
--- a/src/restock.una
+++ b/src/restock.una
@@ -32,3 +32,3 @@
   let edit past_dash = false
-  for character in sku.chars()
+  for character in sku
     if character == "-"
```

```text include="mistakes/3/expected/rendered.txt#L1"
[U2001] Error: expected `List[_]`, found `Text`
```

*Why:* a `for` loop walks a range or a list. A text is neither, so the checker reports the type it expected after `in`, a list, `List[_]`, where `_` stands for any type of element, and the type it found, `Text`. The marks point at `sku`, after `in`.

*Fix:* walk `sku.chars()`, the list of the characters of the text. See [U2001](/docs/errors/U2001/).
:::

### An accumulator without its refined type (U5002)

:::mistake
Leave the type out of `ordered`, in `units_ordered`:

```diff include="day-to-day..mistakes/4:src/restock.una" context="1"
--- a/src/restock.una
+++ b/src/restock.una
@@ -64,3 +64,3 @@
   let edit stock: Units = product.on_hand
-  let edit ordered: Units = 0
+  let edit ordered = 0
   for week in 1..weeks
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U5002] Error: refinement `result >= 0` could not be proven (the loop forgets every fact about `ordered` but the refinements of its type, so the counterexample sets `ordered` freely; guard the use with an `if`, or move the update into a helper with an `edit` parameter whose `ensures` states what the use needs)
```

*Why:* without the annotation, `ordered` is a plain `Int`, the type of its first value. The verifier checks the body once for any turn and keeps, about `ordered`, only the refinements of its type: none. So after the loop, `ordered` could be negative as far as it knows, and the result of the function, a `Units`, is not proven. The code is right; the proof is missing.

*Fix:* `let edit ordered: Units = 0`. Each assignment then proves that `ordered` stays a `Units`, and the fact survives the loop. See [U5002](/docs/errors/U5002/).
:::

### A subtraction that can go below zero (U5001)

:::mistake
Sell the week's units in `stock_after` without `sell_week`:

```diff include="day-to-day..mistakes/5:src/restock.una" context="1"
--- a/src/restock.una
+++ b/src/restock.una
@@ -56,3 +56,3 @@
   for week in 1..weeks
-    stock = sell_week(stock, sales: product.weekly_sales)
+    stock = stock - product.weekly_sales
     stock = stock + order_for(product, stock: stock)
```

```text include="mistakes/5/expected/rendered.txt#L1-L10,L12,L18"
[U5001] Error: refinement `(stock - product.weekly_sales) >= 0` is refuted
    ╭─[ src/restock.una:57:13 ]
    │
  7 │ kind Units = Int where it >= 0
    │                        ───┬───
    │                           ╰───── where clause
    │
 57 │     stock = stock - product.weekly_sales
    │             ──────────────┬─────────────
    │                           ╰─────────────── refinement `(stock - product.weekly_sales) >= 0` is refuted
    │ Help 1: repair 1: add a guard (`if` or a `when` arm) that handles the values where `(stock - product.weekly_sales) >= 0` does not hold
    │ Note 2: counterexample: product = Product#0, product.on_hand = 0, product.weekly_sales = 1, stock = 0, stock (assigned) = -1, week = 1, weeks = 1
```

*Why:* `stock` is a `Units`, so every assignment to it must give a number that is not negative. A shelf that holds fewer units than a week's sales would end the week below zero, and the counterexample is such a shelf: `product.on_hand = 0` and `product.weekly_sales = 1`, for one week. `stock (assigned) = -1` is the value the assignment would give. This rule really breaks, so it is U5001, refuted.

*Fix:* sell with `sell_week`, whose guard gives 0 when the stock is short. See [U5001](/docs/errors/U5001/).
:::

### Counting the weeks with `while` (U0103)

:::mistake
Count the weeks of `stock_after` by hand, with a `while` loop:

```diff include="day-to-day..mistakes/6:src/restock.una" context="1"
--- a/src/restock.una
+++ b/src/restock.una
@@ -55,5 +55,7 @@
   let edit stock: Units = product.on_hand
-  for week in 1..weeks
+  let edit week = 1
+  while week <= weeks
     stock = sell_week(stock, sales: product.weekly_sales)
     stock = stock + order_for(product, stock: stock)
+    week = week + 1
   stock
```

```text include="mistakes/6/expected/rendered.txt#L1"
[U0103] Error: `while` is not a keyword in Una; use `for` or recursion
```

*Why:* Una has no `while`. Its loops walk a range or a list whose length is known before the first turn, so a reader sees where each one ends. The message names the two ways Una repeats work, `for` and recursion. Here the number of weeks is known before the loop starts, so `for` fits, and the name `week` and its assignment are not needed.

*Fix:* `for week in 1..weeks`, as in the program. See [U0103](/docs/errors/U0103/).
:::

## 9.7 Exercises

The exercises come with the chapter's download, `09-loops.tar.gz`, which holds every package of this chapter. Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added, and a stub of the function to write, whose body gives back a placeholder. `una test .` fails there until the exercise is done. Run `una check .` as you go, and `una test .` until every example passes.

### Exercise 1: the demand of the plan

::::exercise
Write `demand`, the units customers ask for over the weeks of the plan, at the product's weekly sales. The start package has the stub and two examples:

```una include="exercises/1/start/src/restock.una#demand" title="exercises/1/start/src/restock.una"
--- The units customers ask for over `weeks` weeks, at the product's weekly sales.
pub demand(product: Product, weeks: Int) -> Units = 0
```

```una include="exercises/1/start/src/restock.una#L169-L175" title="exercises/1/start/src/restock.una"
example "the lamp is asked for 20 times in four weeks"
  do demand(lamp(), weeks: 4)
  expect result == 20

example "no weeks, no demand"
  do demand(lamp(), weeks: 0)
  expect result == 0
```

:::hint
*Hint:* an accumulator that starts at 0 and adds `product.weekly_sales` at each turn of `1..weeks`. The result is a `Units`, so give the accumulator that type, or the loop forgets that it is never negative.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L14-L19"
example restock "the lamp is asked for 20 times in four weeks" ... FAILED
  src/restock.una:171: expect result == 20
  it is false, with `result` = `0`
example restock "no weeks, no demand" ... ok

14 examples: 13 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
A sum over the weeks, with a `Units` accumulator:

```diff include="exercises/1/start..exercises/1/answer:src/restock.una" context="1" title="src/restock.una"
--- a/src/restock.una
+++ b/src/restock.una
@@ -85,3 +85,8 @@
 --- The units customers ask for over `weeks` weeks, at the product's weekly sales.
-pub demand(product: Product, weeks: Int) -> Units = 0
+pub demand(product: Product, weeks: Int) -> Units
+=
+  let edit total: Units = 0
+  for week in 1..weeks
+    total = total + product.weekly_sales
+  total
 
```

The empty range of 0 weeks runs no turn, so `total` keeps 0, and the second example passes with no special case.
:::
::::

### Exercise 2: how many orders

::::exercise
Write `orders_placed`, the number of weeks that end with an order, and add it to the last line of each product's plan, so that it reads `20 units ordered in 2 orders, 0 weeks short`. The start package has the stub and two examples:

```una include="exercises/2/start/src/restock.una#orders_placed" title="exercises/2/start/src/restock.una"
--- How many of the `weeks` weeks end with an order.
pub orders_placed(product: Product, weeks: Int) -> Int = 0
```

```una include="exercises/2/start/src/restock.una#L169-L175" title="exercises/2/start/src/restock.una"
example "the lamp orders in two of four weeks"
  do orders_placed(lamp(), weeks: 4)
  expect result == 2

example "the desk orders every week"
  do orders_placed(desk(), weeks: 4)
  expect result == 4
```

:::hint
*Hint:* walk the weeks as `units_ordered` does, with the same `stock` accumulator, and count, in a second accumulator, the turns whose order is above 0. In `print_plan`, name the count with a `let`, as `ordered` and `short` are, and put it in the text.
:::

Check your answer with `una test .`, then `una run .` for the new totals.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
A count inside the walk of the weeks, and one more value on the last line:

```diff include="exercises/2/start..exercises/2/answer:src/restock.una" context="1" title="src/restock.una"
--- a/src/restock.una
+++ b/src/restock.una
@@ -85,3 +85,13 @@
 --- How many of the `weeks` weeks end with an order.
-pub orders_placed(product: Product, weeks: Int) -> Int = 0
+pub orders_placed(product: Product, weeks: Int) -> Int
+=
+  let edit stock: Units = product.on_hand
+  let edit orders = 0
+  for week in 1..weeks
+    stock = sell_week(stock, sales: product.weekly_sales)
+    let order = order_for(product, stock: stock)
+    if order > 0
+      orders = orders + 1
+    stock = stock + order
+  orders
 
@@ -108,3 +118,4 @@
   let short = weeks_short(product, weeks: weeks)
-  @console.print("  {ordered} units ordered, {short} weeks short")
+  let orders = orders_placed(product, weeks: weeks)
+  @console.print("  {ordered} units ordered in {orders} orders, {short} weeks short")
 
```

The stock must still be followed, since whether a week orders depends on what the weeks before left. The count is a plain `Int`, since its result needs no fact.
:::
::::

### Exercise 3: the lowest stock

::::exercise
Write `lowest_stock`, the fewest units the shelf holds after a week's sales over the plan. With no weeks, it is the stock today. The stub gives back the stock today, which passes only the last of its three examples:

```una include="exercises/3/start/src/restock.una#lowest_stock" title="exercises/3/start/src/restock.una"
--- The fewest units the shelf holds after a week's sales, over `weeks` weeks: the stock
--- today when there are no weeks.
pub lowest_stock(product: Product, weeks: Int) -> Units = product.on_hand
```

```una include="exercises/3/start/src/restock.una#L170-L180" title="exercises/3/start/src/restock.una"
example "the lamp's shelf gets down to 4 units"
  do lowest_stock(lamp(), weeks: 4)
  expect result == 4

example "the desk's shelf runs empty"
  do lowest_stock(desk(), weeks: 4)
  expect result == 0

example "with no weeks, the lowest stock is the stock today"
  do lowest_stock(rug(), weeks: 0)
  expect result == 3
```

:::hint
*Hint:* two accumulators: the stock, as in `stock_after`, and the lowest value seen so far, which starts at the stock today. Look at the stock right after the week's sales, before the order arrives. The result is a `Units`, so the lowest value needs that type, and every value you assign it must be a `Units` too.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/3/start/expected/commands/test.txt#L14-L22"
example restock "the lamp's shelf gets down to 4 units" ... FAILED
  src/restock.una:172: expect result == 4
  it is false, with `result` = `14`
example restock "the desk's shelf runs empty" ... FAILED
  src/restock.una:176: expect result == 0
  it is false, with `result` = `2`
example restock "with no weeks, the lowest stock is the stock today" ... ok

15 examples: 13 passed, 2 failed
```

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Keep the lowest value in a `Units` accumulator, and lower it when the stock after the sales is below it:

```diff include="exercises/3/start..exercises/3/answer:src/restock.una" context="1" title="src/restock.una"
--- a/src/restock.una
+++ b/src/restock.una
@@ -86,3 +86,12 @@
 --- today when there are no weeks.
-pub lowest_stock(product: Product, weeks: Int) -> Units = product.on_hand
+pub lowest_stock(product: Product, weeks: Int) -> Units
+=
+  let edit stock: Units = product.on_hand
+  let edit lowest: Units = product.on_hand
+  for week in 1..weeks
+    stock = sell_week(stock, sales: product.weekly_sales)
+    if stock < lowest
+      lowest = stock
+    stock = stock + order_for(product, stock: stock)
+  lowest
 
```

`lowest = stock` proves itself, since `stock` is a `Units`. The check of the stock comes between the sales and the order, so the lamp's lowest is 4, the stock before its order arrives, and not 14.
:::
::::

## 9.8 Recap and reference

### For agents

:::agents
`una --json check .` prints each diagnostic with its `code`, `message`, `primary` span and `repairs`; U5001 also carries a `counterexample`. U2019 has no repair: its message names the declaration, `let edit x`, or, for a loop variable, which is read-only, a copy bound in the body, `let edit next_x = x`. U5001 and U5002 rank repairs without edits, from a guard (`escape_cost` 0) to `checked` (1). The compact rule: *`for` walks `a..b` (end included), `a..<b` (end left out), `t.chars()` or `t.split(on: s)`, fixed before the first turn; a name a loop changes is `let edit`, declared before it, with a refined type when the code after the loop needs its fact.*
:::

### Recap

:::recap
- `a..b` includes `b`, `a..<b` leaves it out, and a range whose start is above its end runs no turn.
- Walk a text with `text.chars()` or `text.split(on: s)`, never the text itself.
- The range is fixed before the first turn, and every turn runs: there is no `break` and no `while`.
- Declare an accumulator before its loop with `let edit`, at the value for no turn, and change it by assignment.
- A plain `let` and the loop variable are never assigned, and no name shadows another.
- The verifier checks a body once for any turn, and keeps only the refined types of the names the loop changes.
- Give an accumulator a refined type, `let edit total: Units = 0`, when the code after the loop needs its fact.
- With no limit known in advance, use recursion with a case that stops it.
:::

### Reference

:::reference
- Construct pages: [`for`](/docs/language/control-flow/for/), [`let edit`](/docs/language/control-flow/let-edit/), [refined kinds and `where`](/docs/language/types/where/), [`requires`](/docs/language/functions/requires/), [what the verifier proves](/docs/language/verification/), [`example`](/docs/language/examples/example/)
- Standard library: [the prelude](/docs/std/) (`is_digits`, `trim`), [text](/docs/std/text/) (`chars`, `split`, `slice`)
- Diagnostics: [U0101](/docs/errors/U0101/), [U0103](/docs/errors/U0103/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2019](/docs/errors/U2019/), [U5001](/docs/errors/U5001/), [U5002](/docs/errors/U5002/)
- Specification: [memory model: editable bindings and loops](/docs/spec/17-memory-model/), [verification](/docs/spec/12-verification/), [text](/docs/spec/22-text/), [standard library](/docs/spec/14-standard-library/)
:::
