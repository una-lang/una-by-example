---
learn: "4"
title: Kinds
editions: ["0.2"]
codes: [U1001, U1002, U2001, U2004, U2007, U2009, U2025, U2026]
time: 55
builds: A parcel pricer built from records, sum kinds and a generic kind, with an example for each rule
prerequisites: ["2", "3"]
template: 2
nav: ["Records", "Sum kinds and is", "Taking a sum apart: when", "Generic kinds and constraints", "Day-to-day: parcel pricing", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 4 Kinds

So far every value has been a single number, text or condition. A store's data comes in larger shapes. A parcel has an order number, a weight, a zone and a place where the customer collects it. A zone is one of a few fixed choices. A place may be a locker, which has a name, or the door, which has none. This chapter shows how to declare such shapes yourself, as **kinds**, so that the checker knows them as well as it knows `Int` and `Text`. You end with a program that prices parcels from their kinds.

## What you'll build

:::build
A price list for the day's parcels: each parcel's charges for its zone, its weight, its speed and its delivery, then its total, and what express shipping would cost for the first one. The program prints:

```text include="day-to-day/expected/output.txt"
Parcel A-1001, 1200 g
  National: 450 cents
  up to 2 kg: 150 cents
  Standard: 0 cents
  locker Station 14: 0 cents
  total: 600 cents
Parcel A-1002, 3500 g
  Local: 300 cents
  over 2 kg: 400 cents
  Express: 500 cents
  to the door: 250 cents
  total: 1450 cents
Parcel A-1003, 400 g
  Abroad: 1200 cents
  up to 500 g: 0 cents
  Express: 900 cents
  store Harbour Road: 0 cents
  total: 2100 cents
Express for A-1001: 600 cents now, 1100 cents express
```

You will learn to:

- declare a record kind, build its values, and read their fields;
- declare a sum kind, whose values are each one of a fixed list of variants;
- test a variant with `is`, and take a value apart with `when`;
- write a generic kind and a generic function, and the constraint it needs.
:::

## Why it works this way

Many programs keep a parcel's status as a text, such as `"in_transit"`, next to fields that are empty in most states: a tracking number that only a parcel in transit has, a delivery date that only a delivered one has. Nothing stops a parcel that is "delivered" with no date, or "packed" with a tracking number. A typo such as `"in_trnasit"` is a new status that no code knows. And when the store adds a status, every choice among the statuses still runs, and the new status quietly falls into whatever case comes last.

Una lets you give each shape a type of its own:

:::steps
1. **A record is a type of its own.** A `Parcel` has exactly its fields, every one of them is given when a parcel is built, and a `Parcel` is never mistaken for another record with the same fields.
2. **A sum lists every case.** A `Zone` is `Local`, `National` or `Abroad`, and nothing else. Each case carries only its own data: a locker delivery has a locker's name, and a door delivery has none.
3. **`when` covers every case.** A `when` over a `Zone` has an arm for each zone, or an `else`. Add a zone, and the checker points at every `when` that needs a new arm.
:::

The price is a few declarations at the top of a module. In return, a value that makes no sense cannot be built, and a change to the shape of the data shows every place it touches.

> [!KEY]
> Declare the cases your data can be in as the variants of a sum, each carrying only what is true in that case. Then a value that makes no sense cannot be built, and no code can forget a case.

## 4.1 Records

### What a type and a kind are

A **type** is a set of values, together with what you may do with them. You met the built-in ones in [chapter 2](/learn/numbers/#s2-1) and [chapter 3](/learn/text-and-conditions/#s3-1): `Int` is the set of whole numbers, which you may add; `Text` is the set of texts, which you may join; `Bool` is the set of the two values `true` and `false`. The checker uses the types to refuse a program that, say, adds a text to a number.

The built-in types describe single values. A store's data is made of several values that belong together: a parcel has an order number, a weight and an address, and an address has a name, a street and a city. A **kind** is a type that you declare yourself, with the keyword `kind`, to describe such data. Una has four forms of kind, and this chapter teaches three of them:

- A **record** groups several named values that are all there at once. This section.
- A **sum** is one of several cases. [Section 4.2](#s4-2).
- An **alias** gives an existing type another name. [Aliases](#aliases-another-name-for-a-type), in this section.

The fourth form, a kind with a condition such as "never negative", is in [chapter 5](/learn/contracts/#s5-3).

Think of a record as a printed form, such as a shipping label with its boxes: "order", "weight", "name", "street", "city". The kind is the blank form. Each value of the kind is one filled-in copy, with something written in every box.

### Why group values into a record

Without a record, a function that writes a parcel's label must take each part of the parcel as a parameter of its own:

```una include="steps/01-loose/src/slips.una" title="steps/01-loose/src/slips.una" verified="check, run"
module slips

--- The line printed on a parcel's label, from five loose values.
label(order: Text, grams: Int, name: Text, street: Text, city: Text) -> Text = "{order}: {name}, {street}, {city}, {grams} g"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(label("A-1001", grams: 1200, name: "Corner Bakery", street: "12 Elm Road", city: "Northfield"))
  @console.print(label("A-1002", grams: 300, name: "12 Elm Road", street: "Northfield", city: "Corner Bakery"))
```

Like every example of this chapter, this one is a package of its own, made as in [Making the package](/learn/hello/#making-the-package), with its module as the `entry`. You can also take each package, whole, from the chapter's download, `04-kinds.tar.gz`. `una run .` prints:

```text include="steps/01-loose/expected/output.txt"
A-1001: Corner Bakery, 12 Elm Road, Northfield, 1200 g
A-1002: 12 Elm Road, Northfield, Corner Bakery, 300 g
```

The second line is wrong: the street is printed as the name, and the store's name as the city. Every argument after the first has its label, so the call checks, but the values went into the wrong boxes, and all three are `Text`, so the checker cannot tell. The loose form has other costs too:

1. **Every function repeats the list.** Each function that works on a parcel takes the same five parameters, and each call passes the same five values. Add a sixth part, a zone, and every one of them changes.
2. **A function gives back one value.** A function that sends a parcel to a new address must give back a parcel: its order, weight and address together. With loose values, there is nothing to give back.
3. **Nothing says what belongs together.** A reader of `label` sees five values, not one parcel and its address.

A record answers all three. It gathers the values under one name, a function takes it as one parameter, and a result can be a whole parcel.

### How to write a record kind

#### The declaration

```una include="steps/02-records/src/labels.una#Address" title="steps/02-records/src/labels.una"
--- Where a parcel goes.
kind Address
  name: Text
  street: Text
  city: Text
```

A record kind is written in four parts:

1. **`kind`.** The keyword that declares a kind.
2. **`Address`.** The kind's name. A kind's name starts with a capital letter, and each word in it starts with one too, as in `ReturnReason`.
3. **The fields.** One per line, indented two spaces under the name. A **field** is one named part of the record: here `name`, `street` and `city`.
4. **`: Text` after each field.** The field's type. Every value of the kind holds a value of that type in that field.

A field's type can be any type: `Int`, `Text`, `Bool`, another kind, or a list of values ([chapter 10](/learn/collections/#s10-1)).

#### Building a value

To make a value of a record kind, write the kind's name like a call, and give every field, each with its name as a label: `Address(name: "Corner Bakery", street: "12 Elm Road", city: "Northfield")`. Written this way, the kind's name is the **constructor**, the function that builds a value of the kind. The labels work as the labels of a call ([section 1.4](/learn/hello/#s1-4)), with one difference: a record of two or more fields labels every field, the first one too.

A record of one field may leave out the label. `Note("fragile")` builds the record `Note` of [How a record behaves](#how-a-record-behaves), whose one field is `text`.

#### Reading a field with a dot

`parcel.grams` reads the field `grams` of the value `parcel`. When the field is itself a record, the dots go on: `parcel.address.city` is the city of the parcel's address. It is the dot of [method syntax](/learn/text-and-conditions/#s3-2), and when a value has a field of the name after the dot, the dot reads the field.

#### A field whose kind is a record

A field can hold a whole record. `Parcel` has a field `address` of kind `Address`, so each parcel holds an address with its three fields. The checker knows the type of every field, so `parcel.address.city` is a `Text`, and `parcel.address.grams` does not check.

### An address inside a parcel

The module `labels` declares two record kinds, builds a parcel, and sends it to a second address:

:::steps
```una include="steps/02-records/src/labels.una" title="steps/02-records/src/labels.una" verified="check, run"
module labels

--- Where a parcel goes.
kind Address
  name: Text
  street: Text
  city: Text

--- A parcel ready to ship.
kind Parcel
  order: Text
  grams: Int
  address: Address

--- The line printed on a parcel's label.
label(parcel: Parcel) -> Text = "{parcel.address.name}, {parcel.address.city}, {parcel.grams} g"

--- The same parcel, sent to another address. A record never changes: this builds a new one.
redirect(parcel: Parcel, address: Address) -> Parcel = Parcel(order: parcel.order, grams: parcel.grams, address: address)

pub main() -> Unit
  uses @console: Console[print]
=
  let home = Address(name: "Corner Bakery", street: "12 Elm Road", city: "Northfield")
  let office = Address(name: "Corner Bakery", street: "4 Quay Street", city: "Southport")
  let parcel = Parcel(order: "A-1001", grams: 1200, address: home)
  let moved = redirect(parcel, address: office)
  @console.print(label(parcel))
  @console.print(label(moved))
  @console.print("{home}")
```

1. **`kind Address` and `kind Parcel`.** Two record kinds. `Parcel` has a field of kind `Address`, so a parcel holds its address whole.
2. **`Address(name: "Corner Bakery", street: …, city: …)`.** Building a value. Every field is given, each with its label. `una` accepts them in any order, but `una check .` reports an order other than the declared one as not in canonical form (U7001), and `una fmt .` puts them back in that order. There are no default values: a field left out is an error.
3. **`parcel.address.city`.** Reading a field, and a field of a field.
4. **`redirect`.** A record never changes after it is built. To "change" a field, you build a new record from the old one, with the new value in that field. `parcel` itself still goes to the first address, as the first line of the output shows.
5. **`"{home}"`.** Interpolation writes a record in the form you would type it in Una: its kind's name and every field.
:::

`una run .` prints:

```text include="steps/02-records/expected/output.txt"
Corner Bakery, Northfield, 1200 g
Corner Bakery, Southport, 1200 g
Address(name: "Corner Bakery", street: "12 Elm Road", city: "Northfield")
```

### How a record behaves

The next step shows the rules of this part in one module. It declares a record of one field, an alias, and a record that holds both:

```una include="steps/03-record-forms/src/packing.una" title="steps/03-record-forms/src/packing.una" verified="check, run"
module packing

--- A note printed on a parcel: a record of one field.
kind Note
  text: Text

--- A SKU is a text, under a name that says what it holds: an alias.
kind Sku = Text

--- A box on the packing table.
kind Box
  sku: Sku
  grams: Int
  note: Note

--- The same box with another note. The box passed in does not change: a new one is built.
relabel(box: Box, text: Text) -> Box = Box(sku: box.sku, grams: box.grams, note: Note(text))

pub main() -> Unit
  uses @console: Console[print]
=
  let fragile = Note("fragile")
  let lamp: Sku = "LAMP-01"
  let box = Box(sku: lamp, grams: 1200, note: fragile)
  let heavier = Box(sku: box.sku, grams: 1500, note: box.note)
  @console.print("{box}")
  @console.print("{heavier}")
  @console.print("same box: {box == heavier}")
  @console.print("{lamp.len} characters in {lamp}")
  let marked = relabel(box, text: "this side up")
  @console.print("{box.note.text}, then {marked.note.text}")
```

`una run .` prints, among other lines:

```text include="steps/03-record-forms/expected/output.txt#L1-L4"
Box(sku: "LAMP-01", grams: 1200, note: Note("fragile"))
Box(sku: "LAMP-01", grams: 1500, note: Note("fragile"))
same box: false
7 characters in LAMP-01
```

#### Every field, every time

A value of a record has a value in every field. There are no default values and no empty fields. Build a `Parcel` without one of its fields, and the checker reports U2009, "`Parcel` is missing field `speed`", as [Leaving out a field](#leaving-out-a-field-u2009) shows. A field the kind does not declare is U2009 too: `Address(…, zip: "1234")` gives "`Address` has no field `zip`". Reading a field the kind does not have, as `home.zip`, is U1001, "`Address` has no field `zip`, and no function `zip` in scope applies".

#### A value never changes

A record value, once built, never changes. `heavier` is a second box, built from the fields of `box` with another weight: `box` still weighs 1200 grams, as the first line of the output shows. `relabel` works the same way, as a function: it builds a new box with the new note, and the box passed in keeps its own. A name that can take a new value, `let edit`, comes in [chapter 9](/learn/loops/#s9-2).

#### Equality, and how a record prints

`==` compares two records field by field: two records are equal when every field is equal. `box == heavier` is `false`, since their weights differ. Interpolation writes a record as you would build it, with its kind's name and every field labeled, and a record of one field without its label, as `Note("fragile")` shows. Interpolating a record works from edition 0.2 on, the edition of every package in this book.

#### Records are nominal

Records are **nominal**: two kinds with the same fields are two different types, because a kind is known by its name. Declare a `Warehouse` with the same three fields as `Address`, and pass one where `redirect` needs an address:

```diff include="steps/02-records..steps/04-nominal:src/labels.una" title="src/labels.una" context="0"
--- a/src/labels.una
+++ b/src/labels.una
@@ -4,0 +5,6 @@
+  name: Text
+  street: Text
+  city: Text
+
+--- A warehouse of the store. Its fields are those of an `Address`, but it is another kind.
+kind Warehouse
@@ -25 +31 @@
-  let office = Address(name: "Corner Bakery", street: "4 Quay Street", city: "Southport")
+  let office = Warehouse(name: "North Depot", street: "4 Quay Street", city: "Southport")
```

`una check .` reports:

```text include="steps/04-nominal/expected/rendered.txt"
[U2001] Error: argument `address` of `redirect` must be `Address`, found `Warehouse`
    ╭─[ src/labels.una:33:41 ]
    │
 33 │   let moved = redirect(parcel, address: office)
    │                                         ───┬──
    │                                            ╰──── argument `address` of `redirect` must be `Address`, found `Warehouse`
    │
    │ Note: run `una explain U2001` for an explanation
────╯
```

Read it from the top. The first line names the problem: the argument `address` of `redirect` must be an `Address`, and it is a `Warehouse`. The marks point at `office`, the value of the wrong kind. The fields are the same, but a warehouse is not a customer's address, and the checker keeps the two apart. To send a parcel to the warehouse, build an `Address` from the warehouse's fields.

### Aliases: another name for a type

`kind Sku = Text`, in the step of [How a record behaves](#how-a-record-behaves), is an **alias**: another name for an existing type. A `Sku` is a `Text` wherever one is expected, and the other way round, so `lamp.len` works on it as on any text, and `"LAMP-01"` can be given where a `Sku` goes. An alias is written `kind`, its name, `=` and the type it names. It may name another alias.

An alias documents what a field holds: `sku: Sku` says more than `sku: Text`. It does not keep two kinds apart the way a record does: a `Sku` and a customer's name are both `Text`, and the checker lets one go where the other goes. [Chapter 5](/learn/contracts/#s5-3) adds a condition to an alias, as in `kind Cents = Int where it >= 0`, and the checker then proves that every value keeps it.

### A record, loose values or an alias

:::decide
**Which to use:**

| Your data… | Use |
| --- | --- |
| Has several parts that belong together, all there at once | A record, such as `kind Parcel` with its fields |
| Is passed around and given back as a whole | A record: one parameter, one result |
| Is one or two values that a single function needs | Plain parameters |
| Is an existing type under a name that says what it holds | An alias, such as `kind Sku = Text` |
| Must not be mixed up with another kind of the same shape | A record: records are nominal, aliases are not |
:::

### Check yourself: records

`main`, in the step of [How a record behaves](#how-a-record-behaves), ends with these two lines:

```una include="steps/03-record-forms/src/packing.una#L30-L31" title="steps/03-record-forms/src/packing.una"
  let marked = relabel(box, text: "this side up")
  @console.print("{box.note.text}, then {marked.note.text}")
```

`box` holds the note `"fragile"`. What does the last line print?

:::answer Show the answer
```text include="steps/03-record-forms/expected/output.txt#L5"
fragile, then this side up
```

`relabel` builds a new box with the new note, and gives it back as `marked`. The box passed in, `box`, never changes, so its note still says `fragile`. Only `marked` has the new note.
:::

## 4.2 Sum kinds, and `is`

### What a sum kind is

A **sum kind** is a type whose values are each one of a fixed list of cases. Each case is a **variant**. A zone is local, national or abroad; a delivery goes to the door, to a locker or to a store. Think of a box on a paper form where you tick exactly one option: "door", "locker" or "store". A sum is that box, and a value is the ticked option.

A variant may carry data of its own, its **fields**, written in parentheses after its name: a delivery to a locker needs the locker's name, and a delivery to a store needs the store and its opening hour. Each variant has only the fields that make sense for it. A record has all its fields at once; a sum has one variant at a time, with that variant's fields. (The fields of a variant are also called its **payload**.)

### Why a value needs a sum

Without a sum, a status is often written as a text, and the code compares texts:

```una include="steps/05-text-status/src/board.una" title="steps/05-text-status/src/board.una" verified="check, run"
module board

--- What the store tells a customer about a shipment, from its status written as a text.
customer_note(status: Text) -> Text = if status == "in_transit" then "on its way" else if status == "delivered" then "arrived" else "being packed"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(customer_note("in_transit"))
  @console.print(customer_note("in_trnasit"))
  @console.print(customer_note("returned"))
```

`una run .` prints:

```text include="steps/05-text-status/expected/output.txt"
on its way
being packed
being packed
```

The program checks and runs, and two of its three lines are wrong. `"in_trnasit"` is a typo, and `"returned"` is a status that `customer_note` does not know. Both fall into the last `else` of the `if` ([section 3.4](/learn/text-and-conditions/#s3-4)), so a parcel on its way and a parcel that came back are both "being packed". Any text is a valid `Text`, so the checker cannot tell a status from a typo, and nothing points at `customer_note` when a new status appears.

A sum fixes the list of statuses in one declaration. A misspelt variant is a name that does not exist, which does not check, and a `when` over the sum must say what to do with every variant ([section 4.3](#s4-3)).

### How to write a sum kind

A sum kind is written `kind`, its name, `=`, then its variants separated by `|`, all on one line. A variant's name starts with a capital letter, as a kind's name does.

#### Variants without fields

```una include="steps/06-sums/src/carriers.una#Zone" title="steps/06-sums/src/carriers.una"
--- How far a parcel travels, nearest first.
kind Zone = Local | National | Abroad
```

Each variant is a value of its own: `Local` is a `Zone`, and so are `National` and `Abroad`. There are exactly three zones.

#### Variants with fields

```una include="steps/06-sums/src/carriers.una#Delivery" title="steps/06-sums/src/carriers.una"
--- Where a customer collects a parcel. Each variant carries what that place needs.
kind Delivery = AtDoor | AtLocker(locker: Text) | AtStore(store: Text, opens: Int)
```

`AtDoor` has no fields. `AtLocker` has one, `locker`, a `Text`. `AtStore` has two, `store` and `opens`. Fields are written as parameters are: a name, `:` and a type, separated by commas. Variants with and without fields mix freely in one sum.

#### A sum of one variant

```una include="steps/06-sums/src/carriers.una#QuoteError" title="steps/06-sums/src/carriers.una"
--- A sum with one variant starts with a bar.
kind QuoteError = | NoCarrier
```

A sum with a single variant starts with `|`. Without it, `kind QuoteError = NoCarrier` would be an alias of a type named `NoCarrier`, as [A sum of one variant without its bar](#a-sum-of-one-variant-without-its-bar) shows. Sums of one variant are common for failures, which [chapter 7](/learn/failure/#s7-2) declares.

#### Building a variant

A variant without fields is written by its name: `AtDoor`. A variant with fields is built like a record, with its fields labeled: `AtStore(store: "Harbour Road", opens: 9)`. A variant of one field may leave out the label: `AtLocker("Station 14")` is `AtLocker(locker: "Station 14")`.

### Zones and deliveries

The module `carriers` declares three sum kinds, then builds, tests and compares their variants:

:::steps
```una include="steps/06-sums/src/carriers.una" title="steps/06-sums/src/carriers.una" verified="check, run"
module carriers

--- How far a parcel travels, nearest first.
kind Zone = Local | National | Abroad

--- Where a customer collects a parcel. Each variant carries what that place needs.
kind Delivery = AtDoor | AtLocker(locker: Text) | AtStore(store: Text, opens: Int)

--- A sum with one variant starts with a bar.
kind QuoteError = | NoCarrier

--- Whether a customer needs a code to collect the parcel.
needs_code(delivery: Delivery) -> Bool = delivery is AtLocker

pub main() -> Unit
  uses @console: Console[print]
=
  let locker = AtLocker(locker: "Station 14")
  let store = AtStore(store: "Harbour Road", opens: 9)
  @console.print("{locker} {store} {AtDoor}")
  @console.print("code needed: {needs_code(locker)} {needs_code(AtDoor)}")
  @console.print("Local before Abroad: {Local < Abroad}; same zone: {National == National}")
  @console.print("{NoCarrier}")
  let later = AtStore(store: "Harbour Road", opens: 10)
  @console.print("{Abroad > National} {store == later} {needs_code(store)}")
```

1. **`kind Zone = Local | National | Abroad`.** Three variants with no fields. Each is a value of its own: `Local` is a `Zone`.
2. **`kind Delivery = AtDoor | AtLocker(locker: Text) | AtStore(store: Text, opens: Int)`.** Variants with fields. Only a locker delivery has a locker, and only a store delivery has an opening hour. A value such as "at the door, locker 14" cannot be built.
3. **`kind QuoteError = | NoCarrier`.** A sum with one variant starts with a bar.
4. **`AtLocker(locker: "Station 14")`.** A variant with fields is built like a record.
5. **`delivery is AtLocker`.** `is` tests which variant a value is, and gives a `Bool`. It does not need the fields.
6. **`Local < Abroad` and `National == National`.** Variants without fields are ordered as they are declared, so list them in an order that means something: here, nearest first. `==` compares any two values of the same kind.
:::

`una run .` prints, among other lines:

```text include="steps/06-sums/expected/output.txt#L1-L4"
AtLocker("Station 14") AtStore(store: "Harbour Road", opens: 9) AtDoor
code needed: true false
Local before Abroad: true; same zone: true
NoCarrier
```

A variant with fields prints as you would build it: one field without its label, as `AtLocker("Station 14")`, and two or more with their labels.

### How a sum behaves

#### A variant is tested with `is`

`delivery is AtLocker` is `true` when `delivery` is a locker delivery, whatever its locker. `is` names the variant only, never its fields, and works on a variant with fields or without. It gives a `Bool`, so it fits wherever a condition goes: in an `if`, after `not`, or as a function's whole body, as `needs_code` shows.

#### Equality compares whole values

`==` and `!=` compare two values of the same sum. They are equal when they are the same variant and every field is equal. `AtDoor == AtDoor` is `true`. Two store deliveries to the same store at different hours are not equal.

#### Only variants without fields have an order

`<`, `<=`, `>` and `>=` work on a sum whose variants have no fields, in the order the declaration lists them: `Local < Abroad` is `true`. A sum with fields has no order, since nothing says whether a locker comes before a store.

#### A variant with fields is not a value alone

`AtLocker` on its own names the variant, not a value: a locker delivery needs its locker. These three changes break the rules of this part:

```diff include="steps/06-sums..steps/07-variant-rules:src/carriers.una" title="src/carriers.una" context="0"
--- a/src/carriers.una
+++ b/src/carriers.una
@@ -7,0 +8,3 @@
+
+--- How a parcel is packed. `AtDoor` is a variant of `Delivery` already.
+kind Packing = Box | AtDoor
@@ -23,0 +27,2 @@
+  let pending = AtLocker
+  let first = locker < store
```

`una check .` reports three errors. The first is about the new kind:

```text include="steps/07-variant-rules/expected/rendered.txt#L1-L13"
[U1002] Error: `AtDoor` is defined twice in this module, both times as a variant
    ╭─[ src/carriers.una:10:22 ]
    │
  7 │ kind Delivery = AtDoor | AtLocker(locker: Text) | AtStore(store: Text, opens: Int)
    │                 ───┬──
    │                    ╰──── first defined here
    │
 10 │ kind Packing = Box | AtDoor
    │                      ───┬──
    │                         ╰──── `AtDoor` is defined twice in this module, both times as a variant
    │
    │ Note: run `una explain U1002` for an explanation
────╯
```

**A variant's name is unique in its module.** The two marks show the two places: `AtDoor` is first a variant of `Delivery`, on line 7, and then of `Packing`, on line 10. A variant's name is a value, so `AtDoor` must mean one thing in the module. Rename one of them.

The second error is the variant without its fields:

```text include="steps/07-variant-rules/expected/rendered.txt#L14"
[U2009] Error: variant `AtLocker` needs its fields: `locker`
```

The message lists what is missing: the field `locker`. Write `AtLocker(locker: "Station 14")`, or, to ask whether a value is a locker delivery, `value is AtLocker`.

The third is an order on a sum with fields:

```text include="steps/07-variant-rules/expected/rendered.txt#L23"
[U2001] Error: `<` orders `Int`, `Text` and variants without fields, not `Delivery`
```

#### A sum of one variant without its bar

Remove the bar from `QuoteError`:

```diff include="steps/06-sums..steps/08-no-bar:src/carriers.una" title="src/carriers.una" context="0"
--- a/src/carriers.una
+++ b/src/carriers.una
@@ -10 +10 @@
-kind QuoteError = | NoCarrier
+kind QuoteError = NoCarrier
```

```text include="steps/08-no-bar/expected/rendered.txt#L1-L9"
[U1001] Error: cannot find type `NoCarrier` in this module, its imports or the prelude
    ╭─[ src/carriers.una:10:19 ]
    │
 10 │ kind QuoteError = NoCarrier
    │                   ────┬────
    │                       ╰────── cannot find type `NoCarrier` in this module, its imports or the prelude
    │
    │ Note: run `una explain U1001` for an explanation
────╯
```

Without `|`, what follows `=` is a type, so `QuoteError` is read as an alias, and the checker looks for a type named `NoCarrier`. It finds none, and reports U1001 at that name. A second U1001 follows where `main` uses `NoCarrier` as a value. Both go away when the bar is back: `kind QuoteError = | NoCarrier`.

### A record, a sum or an alias

:::decide
**Which to use:**

| Your data… | Use |
| --- | --- |
| Has several parts that are all there at once | A record: `kind Parcel` with fields |
| Is one of several cases, each with its own data | A sum: `kind Delivery = AtDoor \| AtLocker(locker: Text)` |
| Is one of a fixed list of names, with no data | A sum of variants without fields: `kind Zone = Local \| National \| Abroad` |
| Is another type, under a name that says what it holds | An alias: `kind Sku = Text` |
| Is a yes-or-no flag that may grow a third case | A sum from the start, not a `Bool` |
| Is a status written as a text | A sum: the checker then knows every status |
:::

A record and a sum combine. A variant's field can be a record, and a record's field can be a sum, as `Parcel` has a `zone` in [the day-to-day program](#s4-5).

### Check yourself: sums

`main` ends with three more values:

```una include="steps/06-sums/src/carriers.una#L24-L25" title="steps/06-sums/src/carriers.una"
  let later = AtStore(store: "Harbour Road", opens: 10)
  @console.print("{Abroad > National} {store == later} {needs_code(store)}")
```

`store` is `AtStore(store: "Harbour Road", opens: 9)`. Predict the three words the last line prints.

:::answer Show the answer
```text include="steps/06-sums/expected/output.txt#L5"
true false false
```

`Abroad > National` is `true`: `Abroad` is declared after `National`. `store == later` is `false`: the same variant and the same store, but the opening hours differ, and `==` compares every field. `needs_code(store)` is `false`: `store` is not an `AtLocker`.
:::

## 4.3 Taking a sum apart: `when`

### What `when` is

`when` chooses what to do by the variant of a value. Think of a sorting table in a warehouse, with one bin for each kind of delivery. Each parcel goes into the bin that matches its label, and each bin has its own instructions. `when` is that table:

- The **subject** is the value after `when`: the parcel on the table.
- An **arm** is one line under it: one bin, with its instructions.
- The **pattern** is the start of an arm, such as `is AtLocker(locker)`: what the arm matches.
- After `->` comes the arm's value: what the `when` gives when that arm matches.

`when` is an expression, as `if` is ([section 3.4](/learn/text-and-conditions/#s3-4)): it gives the value of the arm that matched, so it can be a function's body or the value of a `let`.

### Why `when` exists

`is` says which variant a value is. It does not give you the variant's fields. Try to read the locker of a locker delivery after testing it with `is`:

```una include="steps/09-no-when/src/pickup.una" title="steps/09-no-when/src/pickup.una"
module pickup

--- Where a customer collects a parcel.
kind Delivery = AtDoor | AtLocker(locker: Text) | AtStore(store: Text, opens: Int)

--- Where to collect the parcel, written with `if` and `is` alone.
pickup_note(delivery: Delivery) -> Text = if delivery is AtLocker then "collect at locker {delivery.locker}" else "delivered to the door"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print(pickup_note(AtLocker(locker: "Station 14")))
```

`una check .` reports:

```text include="steps/09-no-when/expected/rendered.txt"
[U1001] Error: `Delivery` has no field `locker`, and no function `locker` in scope applies
   ╭─[ src/pickup.una:7:101 ]
   │
 7 │ pickup_note(delivery: Delivery) -> Text = if delivery is AtLocker then "collect at locker {delivery.locker}" else "delivered to the door"
   │                                                                                                     ───┬──
   │                                                                                                        ╰──── `Delivery` has no field `locker`, and no function `locker` in scope applies
   │
   │ Note: run `una explain U1001` for an explanation
───╯
```

The marks point at `locker` in `delivery.locker`. A `Delivery` has no field `locker`: only its variant `AtLocker` has one, and the checker does not use the `if` to narrow the value to that variant. The function has a second problem that no message points at: a store delivery falls into the `else`, so it would say "delivered to the door". An `if` covers the cases you thought of, and the rest fall into its `else`.

`when` solves both. Each arm names a variant and can **bind** its fields, which means give each field's value a name that the arm can use. And the checker makes sure that every variant has an arm.

### How to write `when`

```una include="steps/10-when-forms/src/desk.una#pickup_note" title="steps/10-when-forms/src/desk.una"
--- Binding fields by name. An arm binds only the fields it uses.
pickup_note(delivery: Delivery) -> Text
=
  when delivery
    is AtDoor -> "delivered to the door"
    is AtLocker(locker) -> "collect at locker {locker}"
    is AtStore(store, opens) -> "collect at {store} from {opens}:00"
```

A `when` is written in four parts:

1. **`when delivery`.** The keyword, then the subject, on a line of its own.
2. **The arms.** One per line, indented two spaces under `when`.
3. **`is AtLocker(locker)`.** The pattern: `is`, a variant of the subject's kind, and in parentheses the fields the arm binds.
4. **`-> "collect at locker {locker}"`.** The arm's value, after `->`. Inside it, `locker` is the field's value.

A function whose body is a `when` is written in the long form, with `=` alone on its line: a `when` cannot follow `=` on the header's line. The step of this part has one small function for each form an arm takes, and its `main` prints one line for each. A `when` can also choose by a number or a text, and by a range of numbers; [section 8.2](/learn/choices/#s8-2) shows those arms.

#### Binding fields by name

`is AtStore(store, opens)` binds the fields `store` and `opens` under their own names. An arm binds only the fields it uses: `is AtDoor` binds nothing, and an arm may name a variant with fields and bind none of them.

```text include="steps/10-when-forms/expected/output.txt#L1"
collect at Harbour Road from 9:00
```

#### Binding a field under another name

`field: name` binds a field under a name of your choice. `is AtStore(store: place)` gives the field `store` the name `place`, and leaves `opens` out:

```una include="steps/10-when-forms/src/desk.una#store_name" title="steps/10-when-forms/src/desk.una"
--- A field bound under another name, `store: place`, and a field left out.
store_name(delivery: Delivery) -> Text
=
  when delivery
    is AtStore(store: place) -> place
    else -> "no store"
```

```text include="steps/10-when-forms/expected/output.txt#L2"
Harbour Road; no store
```

Use it when the field's name is already taken in the function, or when another name reads better.

#### A field of a one-field variant under any name

A variant with one field binds it under any name, without the `field:` part. `AtLocker` has one field, `locker`, so `is AtLocker(spot)` binds it as `spot`:

```una include="steps/10-when-forms/src/desk.una#locker_code" title="steps/10-when-forms/src/desk.una"
--- A variant of one field binds it under any name.
locker_code(delivery: Delivery) -> Text
=
  when delivery
    is AtLocker(spot) -> "code for {spot}"
    else -> "no code"
```

```text include="steps/10-when-forms/expected/output.txt#L3"
code for Station 14; no code
```

On a variant of two or more fields, a name must be a field's name: `is AtStore(place)` is U2009, "variant `AtStore` has no field `place`".

#### The `else` arm

`else -> value` matches every value that no arm before it matched. It is always the last arm. `store_name` uses one for every delivery that is not a store, and `locker_code` for every delivery that is not a locker.

#### An arm of several lines

When an arm needs more than one line, write nothing after `->`, and put the arm's lines under it, indented two more spaces. The lines are a block, as a branch of an `if` over several lines is ([section 3.4](/learn/text-and-conditions/#s3-4)): `let` lines first, and the block's value is its last line.

```una include="steps/10-when-forms/src/desk.una#opening" title="steps/10-when-forms/src/desk.una"
--- An arm of several lines: a block, whose value is its last line.
opening(delivery: Delivery) -> Text
=
  when delivery
    is AtStore(store, opens) ->
      let closes = opens + 9
      "{store}, {opens}:00 to {closes}:00"
    else -> "any time"
```

```text include="steps/10-when-forms/expected/output.txt#L4"
Harbour Road, 9:00 to 18:00
```

#### `when` as the value of a `let`

A `when` can stand after `let`, and the name takes the value of the arm that matched:

```una include="steps/10-when-forms/src/desk.una#L54-L57" title="steps/10-when-forms/src/desk.una"
  let urgent = when locker
    is AtDoor -> "no"
    else -> "yes"
  @console.print("collect soon: {urgent}")
```

```text include="steps/10-when-forms/expected/output.txt#L5"
collect soon: yes
```

### Postage by zone and delivery

The module `postage` puts the forms to work on a parcel: a `when` with one arm per variant, a `when` with an `else`, and a `when` whose arms bind fields:

:::steps
```una include="steps/11-when/src/postage.una" title="steps/11-when/src/postage.una" verified="check, run"
module postage

--- How far a parcel travels, nearest first.
kind Zone = Local | National | Abroad

--- Where a customer collects a parcel.
kind Delivery = AtDoor | AtLocker(locker: Text) | AtStore(store: Text, opens: Int)

--- The price of a zone, in cents. One arm for each variant, and no `else`.
zone_cents(zone: Zone) -> Int
=
  when zone
    is Local -> 300
    is National -> 450
    is Abroad -> 1200

--- The fee for bringing the parcel to the door. Every other place is free: `else`.
delivery_cents(delivery: Delivery) -> Int
=
  when delivery
    is AtDoor -> 250
    else -> 0

--- Where to collect the parcel. Each arm binds the fields it uses, by name.
pickup_note(delivery: Delivery) -> Text
=
  when delivery
    is AtDoor -> "delivered to the door"
    is AtLocker(locker) -> "collect at locker {locker}"
    is AtStore(store, opens) -> "collect at {store} from {opens}:00"

pub main() -> Unit
  uses @console: Console[print]
=
  let store = AtStore(store: "Harbour Road", opens: 9)
  @console.print("{zone_cents(National) + delivery_cents(AtDoor)} cents")
  @console.print("{zone_cents(Abroad) + delivery_cents(store)} cents")
  @console.print(pickup_note(store))
  @console.print(pickup_note(AtLocker(locker: "Station 14")))
```

1. **`zone_cents`.** One arm per variant, and no `else`. If `Zone` gains a variant, this `when` stops checking until it has an arm for it, as [How `when` behaves](#how-when-behaves) shows. That is why it has no `else`: an `else` would give a new zone the price of some other zone, silently.
2. **`delivery_cents`.** One arm for the door, and `else` for every other place. Here the `else` says what the store means: every place but the door is free.
3. **`is AtLocker(locker) -> …`.** The arm binds the field `locker` and uses it. `is AtDoor` binds nothing.
4. **`is AtStore(store, opens) -> …`.** The names bind the fields of the same names.
:::

`una run .` prints:

```text include="steps/11-when/expected/output.txt"
700 cents
1200 cents
collect at Harbour Road from 9:00
collect at locker Station 14
```

### How `when` behaves

#### Every variant has an arm

A `when` over a sum must match every variant: each has an arm, or an `else` takes the rest. Add an island zone to `Zone`, and change nothing else:

```diff include="steps/11-when..steps/12-missing-arm:src/postage.una" title="src/postage.una" context="0"
--- a/src/postage.una
+++ b/src/postage.una
@@ -4 +4 @@
-kind Zone = Local | National | Abroad
+kind Zone = Local | National | Abroad | Island
```

`una check .` reports:

```text include="steps/12-missing-arm/expected/rendered.txt"
[U2007] Error: `when` does not match variant `Island` of `Zone`
    ╭─[ src/postage.una:12:3 ]
    │
 12 │   when zone
    │   ──┬─
    │     ╰─── `when` does not match variant `Island` of `Zone`
    │
    │ Help: repair 1: add an arm for each missing variant, such as `is Island`, or an `else` arm
    │
    │ Note: run `una explain U2007` for an explanation
────╯
```

The marks point at the `when` of `zone_cents`, and the message names the variant it does not match, `Island`. The `Help` line gives both repairs: an arm `is Island`, or an `else`. `delivery_cents` and `pickup_note` are not reported, since they do not choose by the zone. This is how a new variant shows you every place it touches: the checker lists each `when` that needs an arm.

#### One arm runs

The arms are tried from the top, and the first that matches gives the value. Only that arm runs. `handover`, in [Check yourself: `when`](#check-yourself-when), lists the store first and the door second, and gives the same answers as with the two arms the other way round, since a value matches only one variant.

#### Every arm gives the same type

All the arms of one `when` give values of one type, as both branches of an `if` do. In a function that gives back a `Text`, an arm that gives the number `3` is U2001, "`note` returns `Text`, found `Int`".

#### `else` comes last, and only when it is needed

An `else` before another arm is U2008: no value reaches the arms after it. An `else` after arms that already match every variant is U2008 too, since no value reaches it. [Section 8.2](/learn/choices/#s8-2) gives every rule of `when`.

### `when`, `if` or `is`

:::decide
**Which to use:**

| You want… | Use |
| --- | --- |
| A `Bool`: is this value a given variant? | `is`, such as `delivery is AtLocker` |
| A value for each variant, using its fields | `when`, with an arm for each variant |
| A value for one variant, and the same value for all the others | `when` with one arm and `else` |
| A choice by a condition that is not a variant, such as a weight | `if` |
| A rule that must be revisited when a variant is added | `when` with no `else`, so the checker reports it |
:::

### Check yourself: `when`

The step of this part ends with a function that says how the customer gets the parcel:

```una include="steps/10-when-forms/src/desk.una#handover" title="steps/10-when-forms/src/desk.una"
--- What the customer does to get the parcel. Check yourself: what does `main` print?
handover(delivery: Delivery) -> Text
=
  when delivery
    is AtStore(store: place, opens) -> "ask at {place} after {opens}:00"
    is AtDoor -> "sign at the door"
    else -> "code sent by text"
```

`main` prints `handover(AtDoor)`, `handover(locker)` and `handover(store)` on one line, where `locker` is `AtLocker(locker: "Station 14")` and `store` is `AtStore(store: "Harbour Road", opens: 9)`. What does it print?

:::answer Show the answer
```text include="steps/10-when-forms/expected/output.txt#L6"
sign at the door; code sent by text; ask at Harbour Road after 9:00
```

`AtDoor` matches the second arm. The locker matches neither the first nor the second, so it falls to `else`. The store matches the first arm, which binds the field `store` under the name `place`, and `opens` under its own name.
:::

## 4.4 Generic kinds and constraints

### What a generic kind is

Some kinds have the same shape whatever they hold. A change to a catalog entry has a value before the edit and a value after it, whether it is a price, a name or a zone. A **generic kind** is a kind with a blank in it, filled in each time the kind is used. The blank is a **type parameter**, a name for a type, written in brackets after the kind's name: `kind Change[T]`. Think of a storage box with a label "contents: ____". The box is the same; what you write on the line says what it holds.

`Change[Int]` is a change of prices, and `Change[Text]` a change of names. The type written in the brackets, `Int` or `Text`, is the **type argument**. Each type argument gives a type of its own, with `T` replaced by it.

### Why generic kinds exist

Without a type parameter, each type needs its own kind, and each kind its own functions:

```una include="steps/13-no-generics/src/edits.una" title="steps/13-no-generics/src/edits.una" verified="check, run"
module edits

--- A price before and after an edit.
kind PriceChange
  before: Int
  after: Int

--- A product name before and after an edit: the same shape, for a text.
kind NameChange
  before: Text
  after: Text

--- The price edit the other way round.
undo_price(change: PriceChange) -> PriceChange = PriceChange(before: change.after, after: change.before)

--- The name edit the other way round: the same body, written again.
undo_name(change: NameChange) -> NameChange = NameChange(before: change.after, after: change.before)

pub main() -> Unit
  uses @console: Console[print]
=
  let price = undo_price(PriceChange(before: 1990, after: 1790))
  let name = undo_name(NameChange(before: "Desk lamp", after: "Reading lamp"))
  @console.print("{price}")
  @console.print("{name}")
```

`una run .` prints:

```text include="steps/13-no-generics/expected/output.txt"
PriceChange(before: 1790, after: 1990)
NameChange(before: "Reading lamp", after: "Desk lamp")
```

It works, and it is the same declaration twice and the same function twice, with only the type changed. A change of zones would need a third copy of each. A fix to one copy must be made in all of them, and the copies drift apart over time. A generic kind is written once, and works for every type.

### How to write a generic kind

```una include="steps/14-generic-forms/src/forms.una#Change" title="steps/14-generic-forms/src/forms.una"
--- A value before and after an edit. `T` is the type of both.
kind Change[T]
  before: T
  after: T
```

The type parameter goes in brackets after the kind's name. Inside the declaration, `T` stands for whatever type the kind is used with, as a field's type or as part of one. Both fields have the type `T`, so the two values of one change always have the same type.

The step of this part declares three generic kinds and uses each:

```una include="steps/14-generic-forms/src/forms.una" title="steps/14-generic-forms/src/forms.una" verified="check, run"
module forms

--- A value before and after an edit. `T` is the type of both.
kind Change[T]
  before: T
  after: T

--- How many units of something: `T` is what is counted, and `units` is always an `Int`.
kind Count[T]
  item: T
  units: Int

--- A place in the warehouse and an amount kept there, each of a type of its own.
kind Slot[Place, Amount]
  place: Place
  amount: Amount

--- Whether two values differ. It is private and writes no constraint: the checker infers it.
differs[T](before: T, after: T) -> Bool = before != after

pub main() -> Unit
  uses @console: Console[print]
=
  let price: Change[Int] = Change(before: 1990, after: 1790)
  let name = Change(before: "Desk lamp", after: "Reading lamp")
  let lamps = Count(item: "LAMP-01", units: 3)
  let shelf = Slot(place: "A-4", amount: 12)
  @console.print("{price}")
  @console.print("{name.after}, {lamps.units} of {lamps.item}, shelf {shelf.place}")
  @console.print("price differs: {differs(price.before, after: price.after)}")
  let found: Option[Text] = Some("LAMP-01")
  let missing: Option[Text] = None
  @console.print("{found} {missing}")
```

```text include="steps/14-generic-forms/expected/output.txt"
Change(before: 1990, after: 1790)
Reading lamp, 3 of LAMP-01, shelf A-4
price differs: true
Some("LAMP-01") None
```

#### Fields of a fixed type next to `T`

`Count[T]` has a field `item` of type `T` and a field `units` that is always an `Int`. A generic kind may mix the two: only what varies takes the parameter.

#### Several type parameters

`Slot[Place, Amount]` takes two, separated by a comma, and its fields may have different types: `Slot(place: "A-4", amount: 12)` is a `Slot[Text, Int]`. A type parameter is often one capital letter, such as `T`, but a name that says what it stands for, such as `Place`, reads better when there are several.

#### The type argument, inferred or written

Where a value is built, the checker **infers** the type argument, which means it works the type out from the values given: `Change(before: "Desk lamp", after: "Reading lamp")` is a `Change[Text]`. You can also write it, in a type: `let price: Change[Int] = …` says what `price` holds, and the checker holds the value to it.

#### Generic sums

A sum can take a type parameter too. `Option[T]`, a value that may be missing, is one that every module has: `Some(value)` holds a `T`, and `None` holds nothing. `Some("LAMP-01")` is an `Option[Text]`, as the last line of the output shows. [Section 7.1](/learn/failure/#s7-1) teaches `Option` in full.

### Generic functions and their constraints

A function can take type parameters too, written in brackets after its name: `undo[T](change: Change[T]) -> Change[T]` works on a change of any type. Inside it, `T` is a type the function knows nothing about. It can move values of `T` around, put them in fields, and give them back, but not compare them, since some types cannot be compared.

A **constraint** says what the function needs from `T`, and in exchange limits the types it accepts. It is written after the parameter, with a colon: `changed[T: Eq]`. Una has three, each including the one before. The **fixed-width integers** in the table are the types such as `U8` and `I32` of [section 2.3](/learn/numbers/#s2-3), and `x.to_int()` turns one into an `Int`:

| Constraint | Allows on values of `T` | Satisfied by |
| --- | --- | --- |
| `Eq` | `==`, `!=`, and interpolation | every type whose values hold no functions |
| `Ord` | what `Eq` allows, and `<`, `<=`, `>`, `>=` | `Int`, the fixed-width integers, `Text`, and sums whose variants have no fields |
| `Integer` | what `Ord` allows, and `x.to_int()` | `Int` and the fixed-width integers |

A record or a sum is `Eq` when its values hold no functions, and only a sum without fields is `Ord`. A function as a value comes in [chapter 10](/learn/collections/#s10-2); every type of this chapter is `Eq`.

> [!NOTE]
> Constraints exist from edition 0.2 on, the edition of every package in this book. In edition 0.1, a type parameter takes no constraint, and the checker works out on its own whether a function compares values of `T`.

### Undoing and comparing changes

The module `changes` declares `Change[T]` and three generic functions over it, with three levels of need:

:::steps
```una include="steps/15-generics/src/changes.una" title="steps/15-generics/src/changes.una" verified="check, run"
module changes

kind Zone = Local | National | Abroad

--- A value before and after an edit to a catalog entry. `T` is any type.
kind Change[T]
  before: T
  after: T

--- The edit the other way round. It works for every `T`, since it only moves values.
undo[T](change: Change[T]) -> Change[T] = Change(before: change.after, after: change.before)

--- Whether the edit changed anything. `!=` needs values that can be compared: `Eq`.
changed[T: Eq](change: Change[T]) -> Bool = change.before != change.after

--- The larger of the two values. `>` needs values with an order: `Ord`.
larger[T: Ord](change: Change[T]) -> T = if change.after > change.before then change.after else change.before

pub main() -> Unit
  uses @console: Console[print]
=
  let price = Change(before: 1990, after: 1790)
  let name = Change(before: "Desk lamp", after: "Desk lamp")
  let zone = Change(before: Local, after: Abroad)
  @console.print("{undo(price)}")
  @console.print("price changed: {changed(price)}, name changed: {changed(name)}")
  @console.print("larger price {larger(price)}, farther zone {larger(zone)}")
  let label = Change(before: "desk lamp", after: "Desk lamp")
  @console.print("{changed(label)} {larger(label)}")
```

1. **`kind Change[T]`.** A record with a type parameter. Both fields have the type `T`, so a change from a price to a name cannot be built.
2. **`undo[T]`.** No constraint is needed: `undo` only swaps the two values.
3. **`changed[T: Eq]`.** `!=` compares two values of `T`, so `T` must be `Eq`.
4. **`larger[T: Ord]`.** `>` needs an order, so `T` must be `Ord`: `Int`, `Text`, the fixed-width integers, and sums whose variants have no fields. `Zone` is one, so `larger(zone)` gives the farther zone.
5. **`Change(before: 1990, after: 1790)`.** `T` is inferred as `Int` here, `Text` for `name` and `Zone` for `zone`.
:::

`una run .` prints, among other lines:

```text include="steps/15-generics/expected/output.txt#L1-L3"
Change(before: 1790, after: 1990)
price changed: true, name changed: false
larger price 1990, farther zone Abroad
```

### How generics behave

#### One type per parameter, in every field

A type parameter stands for one type in each value. Build a `Change` with a text before and a number after:

```diff include="steps/14-generic-forms..steps/16-mixed-change:src/forms.una" title="src/forms.una" context="0"
--- a/src/forms.una
+++ b/src/forms.una
@@ -25 +25 @@
-  let name = Change(before: "Desk lamp", after: "Reading lamp")
+  let name = Change(before: "Desk lamp", after: 1790)
```

```text include="steps/16-mixed-change/expected/rendered.txt"
[U2001] Error: field `after` of `Change` must be `Text`, found `Int`
    ╭─[ src/forms.una:25:49 ]
    │
 25 │   let name = Change(before: "Desk lamp", after: 1790)
    │                                                 ──┬─
    │                                                   ╰─── field `after` of `Change` must be `Text`, found `Int`
    │
    │ Note: run `una explain U2001` for an explanation
────╯
```

The checker took `T` from the first field, `Text`, so the second must be a `Text` as well, and the marks point at `1790`.

#### An operator needs its constraint

In a public function, `==` or interpolation on values of `T` without the constraint `Eq` is U2026, and its repair writes the constraint: [A public generic function without its constraint](#a-public-generic-function-without-its-constraint-u2026) shows it. Arithmetic is never allowed on `T`, with a constraint or without: `a + b` on two values of a `T: Integer` is U2001, "an operand of `+` must be `Int`, found `T`". Turn them into `Int` with `to_int()`, and add those.

#### A call passes a type that satisfies it

At each call, the type argument must satisfy the constraint. Pass `larger` a change of shelves, a record:

```diff include="steps/15-generics..steps/17-constraint-rules:src/changes.una" title="src/changes.una" context="0"
--- a/src/changes.una
+++ b/src/changes.una
@@ -3,0 +4,5 @@
+
+--- A shelf of the warehouse: a record, which has no order.
+kind Shelf
+  aisle: Int
+  level: Int
@@ -29,0 +35,2 @@
+  let moved = Change(before: Shelf(aisle: 4, level: 1), after: Shelf(aisle: 2, level: 3))
+  @console.print("{larger(moved)}")
```

```text include="steps/17-constraint-rules/expected/rendered.txt#L1-L6"
[U2025] Error: `larger` needs its type parameter `T` to satisfy `Ord`, and `Shelf` does not
    ╭─[ src/changes.una:36:20 ]
    │
 36 │   @console.print("{larger(moved)}")
    │                    ──────┬──────
    │                          ╰──────── `larger` needs its type parameter `T` to satisfy `Ord`, and `Shelf` does not
```

The error is at the call, U2025, and names the three things involved: the function, `larger`, its constraint, `Ord`, and the type that does not satisfy it, `Shelf`. A record has no order, so there is no larger shelf. Compare the fields you mean, such as `aisle`, with a function written for shelves.

#### Constraints go on functions, not on kinds

A kind's type parameters take no constraint: `kind Change[T: Eq]` does not parse, U0101, "unexpected `:`". The kind only holds values; the functions that compare them state what they need. A name other than `Eq`, `Ord` or `Integer` after the colon is U2027, "`Same` is not a constraint".

#### A private function's constraint is inferred

A function without `pub` may leave its constraint out, and the checker infers the least one its body needs, as it works out such a function's `uses` ([section 6.3](/learn/functions/#s6-3)). `differs`, in the step of [How to write a generic kind](#how-to-write-a-generic-kind), compares with `!=` and writes no constraint. `una contract`, which prints a function's header as the checker sees it, shows what it inferred:

```sh
una contract forms.differs
```

```text include="steps/14-generic-forms/expected/commands/contract.txt#L3"
differs[T: Eq](before: T, after: T) -> Bool -- inferred
```

A `pub` function writes its constraints, since callers in other modules rely on its header. Apart from `differs`, which shows the rule, this book writes them on every function, as it writes every `uses` line.

### The weakest constraint the body needs

:::decide
**Which to use:**

| The body… | Write |
| --- | --- |
| Only moves values of `T`: stores, swaps, gives them back | `[T]`, no constraint |
| Compares values with `==` or `!=`, or puts them in a text | `[T: Eq]` |
| Orders values with `<`, `<=`, `>` or `>=` | `[T: Ord]` |
| Needs the number, with `to_int()` | `[T: Integer]` |
| Works on one type only | No type parameter: name the type |
:::

Write the weakest constraint the body needs. `undo` needs none, so it works on a `Change` of any type. `changed` needs `Eq`, and `larger` needs `Ord`, which also gives `Eq`. A stronger constraint than the body uses only refuses callers for no reason.

### Check yourself: generics

`main` ends with a change of a product name that only changes one letter from small to capital:

```una include="steps/15-generics/src/changes.una#L28-L29" title="steps/15-generics/src/changes.una"
  let label = Change(before: "desk lamp", after: "Desk lamp")
  @console.print("{changed(label)} {larger(label)}")
```

Does `changed(label)` say `true` or `false`, and which name does `larger(label)` give?

:::answer Show the answer
```text include="steps/15-generics/expected/output.txt#L4"
true desk lamp
```

`"desk lamp"` and `"Desk lamp"` are different texts, since `==` compares them character by character, so the change counts. `Text` is ordered character by character too, by each character's number in Unicode, where the capital letters `A` to `Z` come before the small letters `a` to `z`. `d` comes after `D`, so `"desk lamp"` is the larger.
:::

## 4.5 Day-to-day: parcel pricing

### What the program must do

Each afternoon the store prices the parcels it ships that day. A parcel's price has four parts:

- **the zone:** 300 cents to a local address, 450 for the rest of the country, 1200 abroad;
- **the weight:** nothing up to 500 g, 150 cents up to 2 kg, 400 above;
- **the speed:** standard is free, and express costs 500 cents, or 900 abroad;
- **the delivery:** 250 cents to the door, and nothing to a locker or a store.

The price list shows each part on a line of its own, then the total, so that a customer at the desk can see where the price comes from. The program is one module, `pricing`, in a package whose `una.toml` names it as the entry and grants the console:

```toml include="day-to-day/una.toml" title="day-to-day/una.toml"
[package]
name = "pricing"
version = "0.1.0"
edition = "0.2"

[run]
entry = "pricing"
grants = ["console"]
```

### The kinds

The data comes first: three sums, a record, and a generic record:

```una include="day-to-day/src/pricing.una#Zone..Charge" title="day-to-day/src/pricing.una" caption="the kinds" verified="check"
--- How far a parcel travels, nearest first.
kind Zone = Local | National | Abroad

--- How fast a parcel travels.
kind Speed = Standard | Express

--- Where the customer collects a parcel. Each variant carries what that place needs.
kind Delivery = AtDoor | AtLocker(locker: Text) | AtStore(store: Text)

--- A parcel ready to price.
kind Parcel
  order: Text
  grams: Int
  zone: Zone
  speed: Speed
  delivery: Delivery

--- One part of a price: what it is for, of any type, and its amount in cents.
kind Charge[T]
  item: T
  cents: Int
```

`Zone` and `Speed` are sums of variants without fields, nearest and slowest first. `Delivery` is a sum whose variants carry what each place needs: a locker's name, a store's name, and nothing for the door. `Parcel` is a record that holds all the rest: a parcel always has an order, a weight, a zone, a speed and a delivery.

`Charge[T]` is one line of the price list: what the line is for, and its amount. What it is for depends on the line. For the zone it is the `Zone` itself, for the speed the `Speed`, and for the weight and the delivery a text. So `item` has the type parameter `T`, and `cents` is always an `Int`.

### Pricing each part

Each part of the price is a function that gives back a `Charge`:

```una include="day-to-day/src/pricing.una#zone_charge..delivery_charge" title="day-to-day/src/pricing.una" caption="the four charges" verified="check"
--- The charge for the zone. One arm for each zone, and no `else`.
zone_charge(zone: Zone) -> Charge[Zone]
=
  when zone
    is Local -> Charge(item: zone, cents: 300)
    is National -> Charge(item: zone, cents: 450)
    is Abroad -> Charge(item: zone, cents: 1200)

--- The charge for the weight, by bands.
weight_charge(grams: Int) -> Charge[Text]
=
  if grams <= 500
    Charge(item: "up to 500 g", cents: 0)
  else if grams <= 2000
    Charge(item: "up to 2 kg", cents: 150)
  else
    Charge(item: "over 2 kg", cents: 400)

--- The charge for the speed. Express costs more abroad.
speed_charge(speed: Speed, zone: Zone) -> Charge[Speed]
=
  when speed
    is Standard -> Charge(item: speed, cents: 0)
    is Express -> Charge(item: speed, cents: if zone is Abroad then 900 else 500)

--- The charge for the last step: only the door costs extra.
delivery_charge(delivery: Delivery) -> Charge[Text]
=
  when delivery
    is AtDoor -> Charge(item: "to the door", cents: 250)
    is AtLocker(locker) -> Charge(item: "locker {locker}", cents: 0)
    is AtStore(store) -> Charge(item: "store {store}", cents: 0)
```

- **`zone_charge`** has one arm per zone and no `else`. If the store adds a zone, this function stops checking until the new zone has a price, which is what the store wants. Each arm gives a `Charge[Zone]` whose item is the zone itself.
- **`weight_charge`** chooses by a number, not by a variant, so it uses `if` and `else if`, as in [section 3.4](/learn/text-and-conditions/#s3-4). Its item is the name of the weight band.
- **`speed_charge`** takes the zone too, since express costs more abroad. The arm for `Express` uses `is` inside an `if`, to ask one question about the zone.
- **`delivery_charge`** binds the field of each variant that has one, so that the line names the locker or the store.

### The total, and a parcel sent express

```una include="day-to-day/src/pricing.una#total..express" title="day-to-day/src/pricing.una" caption="the total and the express parcel" verified="check"
--- The price of a parcel, in cents: the four charges added up.
total(parcel: Parcel) -> Int
=
  let zone = zone_charge(parcel.zone)
  let weight = weight_charge(parcel.grams)
  let speed = speed_charge(parcel.speed, zone: parcel.zone)
  let delivery = delivery_charge(parcel.delivery)
  zone.cents + weight.cents + speed.cents + delivery.cents

--- The same parcel, sent express. The parcel passed in does not change.
express(parcel: Parcel) -> Parcel = Parcel(order: parcel.order, grams: parcel.grams, zone: parcel.zone, speed: Express, delivery: parcel.delivery)
```

`total` names each charge with `let`, then adds their `cents` fields. Each `let` holds a `Charge` of its own type: `zone` is a `Charge[Zone]` and `weight` a `Charge[Text]`, and both have a `cents` field that is an `Int`, so they add up.

`express` gives back the parcel as it would be sent express. A record never changes, so it builds a new `Parcel` with every field of the old one and `Express` as its speed. The parcel passed in is unchanged: `main` prices both.

### Printing a quote

```una include="day-to-day/src/pricing.una#charge_line..main" title="day-to-day/src/pricing.una" caption="the price list" verified="check, run"
--- One line of the price list. Interpolating `charge.item` needs `Eq`.
charge_line[T: Eq](charge: Charge[T]) -> Text = "  {charge.item}: {charge.cents} cents"

--- Prints a parcel's charges, one per line, and its total.
quote(parcel: Parcel) -> Unit
  uses @console: Console[print]
=
  @console.print("Parcel {parcel.order}, {parcel.grams} g")
  @console.print(charge_line(zone_charge(parcel.zone)))
  @console.print(charge_line(weight_charge(parcel.grams)))
  @console.print(charge_line(speed_charge(parcel.speed, zone: parcel.zone)))
  @console.print(charge_line(delivery_charge(parcel.delivery)))
  @console.print("  total: {total(parcel)} cents")

--- Prints the quotes of the day's parcels, and what express would cost for the first.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National, speed: Standard, delivery: AtLocker("Station 14"))
  let rug = Parcel(order: "A-1002", grams: 3500, zone: Local, speed: Express, delivery: AtDoor)
  let gift = Parcel(order: "A-1003", grams: 400, zone: Abroad, speed: Express, delivery: AtStore("Harbour Road"))
  quote(lamp)
  quote(rug)
  quote(gift)
  @console.print("Express for {lamp.order}: {total(lamp)} cents now, {total(express(lamp))} cents express")
```

`charge_line` is a generic function. It writes `charge.item` into a text, and interpolation of a value of `T` needs the constraint `Eq`, so the header says `[T: Eq]`. Every item of this program is a `Zone`, a `Speed` or a `Text`, and each is `Eq`, so one function writes every line of the list.

`quote` prints one parcel: its order and weight, its four charges, and its total. `main` builds the day's three parcels and prices each. Its last line compares the first parcel's price now with its price sent express.

### Running it

In the `day-to-day` directory:

```sh
una check .
una run .
```

`una check .` prints nothing, and `una run .` prints the price list:

```text include="day-to-day/expected/output.txt"
Parcel A-1001, 1200 g
  National: 450 cents
  up to 2 kg: 150 cents
  Standard: 0 cents
  locker Station 14: 0 cents
  total: 600 cents
Parcel A-1002, 3500 g
  Local: 300 cents
  over 2 kg: 400 cents
  Express: 500 cents
  to the door: 250 cents
  total: 1450 cents
Parcel A-1003, 400 g
  Abroad: 1200 cents
  up to 500 g: 0 cents
  Express: 900 cents
  store Harbour Road: 0 cents
  total: 2100 cents
Express for A-1001: 600 cents now, 1100 cents express
```

Each item prints as interpolation writes it: a variant by its name, such as `National` or `Express`, and a text as it is. The parcel abroad pays 900 cents for express, and the others 500.

### The whole program

```una include="day-to-day/src/pricing.una" title="day-to-day/src/pricing.una" caption="the whole program" verified="check, run, test"
module pricing

-- The price of shipping a parcel: its zone, its weight, its speed and where it is collected.

--- How far a parcel travels, nearest first.
kind Zone = Local | National | Abroad

--- How fast a parcel travels.
kind Speed = Standard | Express

--- Where the customer collects a parcel. Each variant carries what that place needs.
kind Delivery = AtDoor | AtLocker(locker: Text) | AtStore(store: Text)

--- A parcel ready to price.
kind Parcel
  order: Text
  grams: Int
  zone: Zone
  speed: Speed
  delivery: Delivery

--- One part of a price: what it is for, of any type, and its amount in cents.
kind Charge[T]
  item: T
  cents: Int

--- The charge for the zone. One arm for each zone, and no `else`.
zone_charge(zone: Zone) -> Charge[Zone]
=
  when zone
    is Local -> Charge(item: zone, cents: 300)
    is National -> Charge(item: zone, cents: 450)
    is Abroad -> Charge(item: zone, cents: 1200)

--- The charge for the weight, by bands.
weight_charge(grams: Int) -> Charge[Text]
=
  if grams <= 500
    Charge(item: "up to 500 g", cents: 0)
  else if grams <= 2000
    Charge(item: "up to 2 kg", cents: 150)
  else
    Charge(item: "over 2 kg", cents: 400)

--- The charge for the speed. Express costs more abroad.
speed_charge(speed: Speed, zone: Zone) -> Charge[Speed]
=
  when speed
    is Standard -> Charge(item: speed, cents: 0)
    is Express -> Charge(item: speed, cents: if zone is Abroad then 900 else 500)

--- The charge for the last step: only the door costs extra.
delivery_charge(delivery: Delivery) -> Charge[Text]
=
  when delivery
    is AtDoor -> Charge(item: "to the door", cents: 250)
    is AtLocker(locker) -> Charge(item: "locker {locker}", cents: 0)
    is AtStore(store) -> Charge(item: "store {store}", cents: 0)

--- The price of a parcel, in cents: the four charges added up.
total(parcel: Parcel) -> Int
=
  let zone = zone_charge(parcel.zone)
  let weight = weight_charge(parcel.grams)
  let speed = speed_charge(parcel.speed, zone: parcel.zone)
  let delivery = delivery_charge(parcel.delivery)
  zone.cents + weight.cents + speed.cents + delivery.cents

--- The same parcel, sent express. The parcel passed in does not change.
express(parcel: Parcel) -> Parcel = Parcel(order: parcel.order, grams: parcel.grams, zone: parcel.zone, speed: Express, delivery: parcel.delivery)

--- One line of the price list. Interpolating `charge.item` needs `Eq`.
charge_line[T: Eq](charge: Charge[T]) -> Text = "  {charge.item}: {charge.cents} cents"

--- Prints a parcel's charges, one per line, and its total.
quote(parcel: Parcel) -> Unit
  uses @console: Console[print]
=
  @console.print("Parcel {parcel.order}, {parcel.grams} g")
  @console.print(charge_line(zone_charge(parcel.zone)))
  @console.print(charge_line(weight_charge(parcel.grams)))
  @console.print(charge_line(speed_charge(parcel.speed, zone: parcel.zone)))
  @console.print(charge_line(delivery_charge(parcel.delivery)))
  @console.print("  total: {total(parcel)} cents")

--- Prints the quotes of the day's parcels, and what express would cost for the first.
pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National, speed: Standard, delivery: AtLocker("Station 14"))
  let rug = Parcel(order: "A-1002", grams: 3500, zone: Local, speed: Express, delivery: AtDoor)
  let gift = Parcel(order: "A-1003", grams: 400, zone: Abroad, speed: Express, delivery: AtStore("Harbour Road"))
  quote(lamp)
  quote(rug)
  quote(gift)
  @console.print("Express for {lamp.order}: {total(lamp)} cents now, {total(express(lamp))} cents express")

example "each zone has its price"
  do zone_charge(National)
  expect result == Charge(item: National, cents: 450)

example "the nearest zone is the cheapest"
  do zone_charge(Local)
  expect result.cents == 300

example "abroad costs the most"
  do zone_charge(Abroad)
  expect result.cents == 1200

example "500 g is still the lightest band"
  do weight_charge(500)
  expect result == Charge(item: "up to 500 g", cents: 0)

example "501 g is the next band"
  do weight_charge(501)
  expect result == Charge(item: "up to 2 kg", cents: 150)

example "2 kg is the last gram of the middle band"
  do weight_charge(2000)
  expect result.cents == 150

example "over 2 kg pays the most"
  do weight_charge(2001)
  expect result == Charge(item: "over 2 kg", cents: 400)

example "standard speed is free"
  do speed_charge(Standard, zone: Abroad)
  expect result.cents == 0

example "express at home costs 500"
  do speed_charge(Express, zone: National)
  expect result == Charge(item: Express, cents: 500)

example "express abroad costs 900"
  do speed_charge(Express, zone: Abroad)
  expect result.cents == 900

example "the door costs extra"
  do delivery_charge(AtDoor)
  expect result == Charge(item: "to the door", cents: 250)

example "a locker is free, and named"
  do delivery_charge(AtLocker("Station 14"))
  expect result == Charge(item: "locker Station 14", cents: 0)

example "a store is free, and named"
  do delivery_charge(AtStore("Harbour Road"))
  expect result == Charge(item: "store Harbour Road", cents: 0)

example "the total adds the four charges"
  do total(Parcel(order: "A-1002", grams: 3500, zone: Local, speed: Express, delivery: AtDoor))
  expect result == 1450

example "express changes the speed and nothing else"
  do express(Parcel(order: "A-1001", grams: 1200, zone: National, speed: Standard, delivery: AtDoor))
  expect result == Parcel(order: "A-1001", grams: 1200, zone: National, speed: Express, delivery: AtDoor)
```

## 4.6 Testing it

The examples are the simplest form of [section 1.7](/learn/hello/#s1-7): a call, and what it must give back. A sum makes it easy to see what to test, since its variants are listed in one place.

### One example per variant

Each function that chooses by a variant has an example for each variant: the three zones, the two speeds, the three deliveries. When a variant is added, a `when` without an `else` stops checking, and the list of examples shows the variant that has none yet.

```una include="day-to-day/src/pricing.una#L138-L148" title="day-to-day/src/pricing.una" caption="one example per delivery"
example "the door costs extra"
  do delivery_charge(AtDoor)
  expect result == Charge(item: "to the door", cents: 250)

example "a locker is free, and named"
  do delivery_charge(AtLocker("Station 14"))
  expect result == Charge(item: "locker Station 14", cents: 0)

example "a store is free, and named"
  do delivery_charge(AtStore("Harbour Road"))
  expect result == Charge(item: "store Harbour Road", cents: 0)
```

`expect result == Charge(…)` builds the charge the call must give back, and compares the two field by field, as `==` compares any two records.

### The edges of the weight bands

The bands of `weight_charge` meet at 500 and 2000 grams, and the examples sit on both sides of each edge: 500 and 501, 2000 and 2001. A mistake such as `<` in place of `<=` moves a parcel into the wrong band at exactly one weight, which only an example at that weight catches.

### A field of the result

`expect result.cents == 300` reads one field of the result. Use it when only one field matters to the rule, as the price of a zone does. The example for the whole parcel, `the total adds the four charges`, checks the sum that `quote` prints.

### Running the examples

In the `day-to-day` directory, `una test .` checks the package, then runs the examples:

```text include="day-to-day/expected/commands/test.txt#L2-L18"
example pricing "each zone has its price" ... ok
example pricing "the nearest zone is the cheapest" ... ok
example pricing "abroad costs the most" ... ok
example pricing "500 g is still the lightest band" ... ok
example pricing "501 g is the next band" ... ok
example pricing "2 kg is the last gram of the middle band" ... ok
example pricing "over 2 kg pays the most" ... ok
example pricing "standard speed is free" ... ok
example pricing "express at home costs 500" ... ok
example pricing "express abroad costs 900" ... ok
example pricing "the door costs extra" ... ok
example pricing "a locker is free, and named" ... ok
example pricing "a store is free, and named" ... ok
example pricing "the total adds the four charges" ... ok
example pricing "express changes the speed and nothing else" ... ok

15 examples: 15 passed, 0 failed
```

`main`, `quote` and `charge_line` have no examples of their own: the first two print, and the third only writes the line that the tested charges give it.

## 4.7 Common mistakes

Each mistake is a small change to `day-to-day/src/pricing.una`, followed by what `una check .` reports. Read each diagnostic as [section 1.1](/learn/hello/#if-una-check-finds-a-mistake) shows: the message, then the place, then the help.

### Leaving out a field (U2009)

:::mistake
Build a parcel without its speed:

```diff include="day-to-day..mistakes/1:src/pricing.una" context="1"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -90,3 +90,3 @@
   let lamp = Parcel(order: "A-1001", grams: 1200, zone: National, speed: Standard, delivery: AtLocker("Station 14"))
-  let rug = Parcel(order: "A-1002", grams: 3500, zone: Local, speed: Express, delivery: AtDoor)
+  let rug = Parcel(order: "A-1002", grams: 3500, zone: Local, delivery: AtDoor)
   let gift = Parcel(order: "A-1003", grams: 400, zone: Abroad, speed: Express, delivery: AtStore("Harbour Road"))
```

```text include="mistakes/1/expected/rendered.txt#L1"
[U2009] Error: `Parcel` is missing field `speed`
```

*Why:* a record has a value in every field, and there are no default values. The marks point at `Parcel`, the constructor, and the message names the field that is missing. A record cannot be half built, so no function ever meets a parcel without a speed.

*Fix:* give the field, `speed: Express`. If a parcel may truly have no speed, that is a case of its own: add a variant for it to `Speed`. See [U2009](/docs/errors/U2009/).
:::

### A field without its label (U2004)

:::mistake
Leave out the label of a record's first field:

```diff include="day-to-day..mistakes/2:src/pricing.una" context="1"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -30,3 +30,3 @@
   when zone
-    is Local -> Charge(item: zone, cents: 300)
+    is Local -> Charge(zone, cents: 300)
     is National -> Charge(item: zone, cents: 450)
```

```text include="mistakes/2/expected/rendered.txt#L1-L10"
[U2004] Error: `Charge` has 2 fields, so every argument needs its field's label
    ╭─[ src/pricing.una:31:24 ]
    │
 31 │     is Local -> Charge(zone, cents: 300)
    │                        ──┬─
    │                          ╰─── `Charge` has 2 fields, so every argument needs its field's label
    │
    │ Help: repair 1: label it `item`; edit src/pricing.una:31:24..31:28 to "item: zone"
    │
    │ Note: run `una explain U2004` for an explanation
```

*Why:* in a call of a function, the first argument may go without its label. A record of two or more fields is different: every field carries its label, the first one too, so that the line says which box each value goes into. The marks point at `zone`, the value without a label.

*Fix:* write `item: zone`, as the `Help` line says, or let `una fix .` make that edit. See [U2004](/docs/errors/U2004/).
:::

### A text where a variant goes (U2001)

:::mistake
Write the zone as a text:

```diff include="day-to-day..mistakes/3:src/pricing.una" context="1"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -89,3 +89,3 @@
 =
-  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National, speed: Standard, delivery: AtLocker("Station 14"))
+  let lamp = Parcel(order: "A-1001", grams: 1200, zone: "National", speed: Standard, delivery: AtLocker("Station 14"))
   let rug = Parcel(order: "A-1002", grams: 3500, zone: Local, speed: Express, delivery: AtDoor)
```

```text include="mistakes/3/expected/rendered.txt#L1"
[U2001] Error: field `zone` of `Parcel` must be `Zone`, found `Text`
```

*Why:* `"National"` is a `Text`, and the field `zone` holds a `Zone`. A variant is a value of its sum, written by its name, without quotes. The message names the field, the type it needs, and the type it found.

*Fix:* write `National`, without quotes. A text from outside the program, such as a zone typed by a clerk, is turned into a variant by a function with a `when` or an `if`, once, where it comes in. See [U2001](/docs/errors/U2001/).
:::

### Reading a variant's field without binding it (U1001)

:::mistake
Leave out the binding of the locker, and read it with a dot:

```diff include="day-to-day..mistakes/4:src/pricing.una" context="1"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -56,3 +56,3 @@
     is AtDoor -> Charge(item: "to the door", cents: 250)
-    is AtLocker(locker) -> Charge(item: "locker {locker}", cents: 0)
+    is AtLocker -> Charge(item: "locker {delivery.locker}", cents: 0)
     is AtStore(store) -> Charge(item: "store {store}", cents: 0)
```

```text include="mistakes/4/expected/rendered.txt#L1"
[U1001] Error: `Delivery` has no field `locker`, and no function `locker` in scope applies
```

*Why:* `delivery` is a `Delivery`, and a `Delivery` has no field `locker`: only its variant `AtLocker` has one. The arm `is AtLocker` matches the variant, but a dot on `delivery` still reads the sum, not the variant. The marks point at `locker`.

*Fix:* bind the field in the pattern, `is AtLocker(locker)`, and use the name `locker` in the arm. See [U1001](/docs/errors/U1001/).
:::

### A `when` that misses a variant (U2007)

:::mistake
Leave out the arm for `Abroad`:

```diff include="day-to-day..mistakes/5:src/pricing.una" context="1"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -32,3 +32,2 @@
     is National -> Charge(item: zone, cents: 450)
-    is Abroad -> Charge(item: zone, cents: 1200)
 
```

```text include="mistakes/5/expected/rendered.txt#L1-L10"
[U2007] Error: `when` does not match variant `Abroad` of `Zone`
    ╭─[ src/pricing.una:30:3 ]
    │
 30 │   when zone
    │   ──┬─
    │     ╰─── `when` does not match variant `Abroad` of `Zone`
    │
    │ Help: repair 1: add an arm for each missing variant, such as `is Abroad`, or an `else` arm
    │
    │ Note: run `una explain U2007` for an explanation
```

*Why:* a `when` over a sum matches every variant, so that no value falls through it with no answer. The marks point at the `when`, and the message names the variant it does not match. The same message comes when a new variant is added to the sum and a `when` has no arm for it yet.

*Fix:* add the arm, `is Abroad -> Charge(item: zone, cents: 1200)`. Add an `else` only when the other variants truly share one answer. See [U2007](/docs/errors/U2007/).
:::

### A public generic function without its constraint (U2026)

:::mistake
Make `charge_line` public, and leave out its constraint:

```diff include="day-to-day..mistakes/6:src/pricing.una" context="1"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -72,3 +72,3 @@
 --- One line of the price list. Interpolating `charge.item` needs `Eq`.
-charge_line[T: Eq](charge: Charge[T]) -> Text = "  {charge.item}: {charge.cents} cents"
+pub charge_line[T](charge: Charge[T]) -> Text = "  {charge.item}: {charge.cents} cents"
 
```

```text include="mistakes/6/expected/rendered.txt#L1-L10"
[U2026] Error: interpolation on values of the type parameter `T` needs the constraint `Eq`; write `[T: Eq]`
    ╭─[ src/pricing.una:73:53 ]
    │
 73 │ pub charge_line[T](charge: Charge[T]) -> Text = "  {charge.item}: {charge.cents} cents"
    │                                                     ─────┬─────
    │                                                          ╰─────── interpolation on values of the type parameter `T` needs the constraint `Eq`; write `[T: Eq]`
    │
    │ Help: repair 1: constrain `T` by `Eq`; edit src/pricing.una:73:17..73:18 to "T: Eq"
    │
    │ Note: run `una explain U2026` for an explanation
```

*Why:* interpolation writes `charge.item`, a value of `T`, into a text, and that needs `Eq`. A function without `pub` may leave the constraint out, and the checker infers it; a public one writes it, so that callers in other modules can read what it needs from its header. The marks point at the interpolation.

*Fix:* write `[T: Eq]`, as the `Help` line says, or let `una fix .` make that edit. See [U2026](/docs/errors/U2026/).
:::

## 4.8 Exercises

The exercises come with the chapter's download, `04-kinds.tar.gz`. Each starts from `exercises/N/start`: the day-to-day program with the exercise's example added. Work in this order: read the example, change the code, run `una check .` and fix what it reports, then run `una test .` until every example passes.

### Exercise 1: lockers cost 100 cents

::::exercise
The locker company now charges the store, and the store passes it on: a locker delivery costs 100 cents. The example for lockers has already been changed:

```una include="exercises/1/start/src/pricing.una#L142-L144" title="exercises/1/start/src/pricing.una"
example "a locker costs 100 cents, and is named"
  do delivery_charge(AtLocker("Station 14"))
  expect result == Charge(item: "locker Station 14", cents: 100)
```

Change `delivery_charge` so that the example passes.

:::hint
*Hint:* only one arm of the `when` in `delivery_charge` changes. Its doc comment, which says that only the door costs extra, should change too.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/1/start/expected/commands/test.txt#L13-L15,L20"
example pricing "a locker costs 100 cents, and is named" ... FAILED
  src/pricing.una:144: expect result == Charge(item: "locker Station 14", cents: 100)
  it is false, with `result` = `Charge(item: "locker Station 14", cents: 0)`
15 examples: 14 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Give the locker arm its new amount:

```diff include="exercises/1/start..exercises/1/answer:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -51,3 +51,3 @@
 
---- The charge for the last step: only the door costs extra.
+--- The charge for the last step: the door costs the most, and a locker a little.
 delivery_charge(delivery: Delivery) -> Charge[Text]
@@ -56,3 +56,3 @@
     is AtDoor -> Charge(item: "to the door", cents: 250)
-    is AtLocker(locker) -> Charge(item: "locker {locker}", cents: 0)
+    is AtLocker(locker) -> Charge(item: "locker {locker}", cents: 100)
     is AtStore(store) -> Charge(item: "store {store}", cents: 0)
```

The first parcel goes to a locker, so its total is now 700 cents.
:::
::::

### Exercise 2: overnight shipping

::::exercise
The store adds a third speed, overnight, at 1500 cents in every zone. The start package adds the variant and its example:

```una include="exercises/2/start/src/pricing.una#Speed" title="exercises/2/start/src/pricing.una"
--- How fast a parcel travels.
kind Speed = Standard | Express | Overnight
```

```una include="exercises/2/start/src/pricing.una#L158-L160" title="exercises/2/start/src/pricing.una"
example "overnight costs 1500 in every zone"
  do speed_charge(Overnight, zone: Local)
  expect result == Charge(item: Overnight, cents: 1500)
```

`una check .` already says where the program needs to change:

```text include="exercises/2/start/expected/rendered.txt#L1-L10"
[U2007] Error: `when` does not match variant `Overnight` of `Speed`
    ╭─[ src/pricing.una:48:3 ]
    │
 48 │   when speed
    │   ──┬─
    │     ╰─── `when` does not match variant `Overnight` of `Speed`
    │
    │ Help: repair 1: add an arm for each missing variant, such as `is Overnight`, or an `else` arm
    │
    │ Note: run `una explain U2007` for an explanation
```

Make the program check, and the example pass.

:::hint
*Hint:* the message names the `when` and the missing variant. Add an arm for it. Do not add an `else`: a fourth speed should be reported in the same way.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Add the arm for `Overnight` to `speed_charge`:

```diff include="exercises/2/start..exercises/2/answer:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -50,2 +50,3 @@
     is Express -> Charge(item: speed, cents: if zone is Abroad then 900 else 500)
+    is Overnight -> Charge(item: speed, cents: 1500)
 
```

No other function chooses by the speed, so this is the only change. The checker found it for you.
:::
::::

### Exercise 3: the cheaper of two charges

::::exercise
A clerk wants to tell customers which of two ways to collect a parcel costs less. Write `cheaper`, which gives back the charge with fewer cents, and the first one when the two cost the same. It must work for a `Charge` of any type. The start package ends with:

```una include="exercises/3/start/src/pricing.una#L158-L167" title="exercises/3/start/src/pricing.una"
--- The cheaper of two charges, and the first one when they cost the same.
cheaper[T](first: Charge[T], second: Charge[T]) -> Charge[T] = first

example "a locker is cheaper than the door"
  do cheaper(delivery_charge(AtDoor), second: delivery_charge(AtLocker("Station 14")))
  expect result == Charge(item: "locker Station 14", cents: 0)

example "on a tie, the first charge"
  do cheaper(delivery_charge(AtLocker("Station 14")), second: delivery_charge(AtStore("Harbour Road")))
  expect result == Charge(item: "locker Station 14", cents: 0)
```

:::hint
*Hint:* compare `first.cents` and `second.cents` with an `if`. Ask yourself whether the body does anything with a value of `T`: it compares the `cents` fields, which are `Int`, and only moves the charges. So `T` needs no constraint.
:::

Check your answer with `una test .`. On the start package it reports:

```text include="exercises/3/start/expected/commands/test.txt#L17-L19,L22"
example pricing "a locker is cheaper than the door" ... FAILED
  src/pricing.una:163: expect result == Charge(item: "locker Station 14", cents: 0)
  it is false, with `result` = `Charge(item: "to the door", cents: 250)`
17 examples: 16 passed, 1 failed
```

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Give back the second charge only when it costs less:

```diff include="exercises/3/start..exercises/3/answer:src/pricing.una" context="1" title="src/pricing.una"
--- a/src/pricing.una
+++ b/src/pricing.una
@@ -158,3 +158,3 @@
 --- The cheaper of two charges, and the first one when they cost the same.
-cheaper[T](first: Charge[T], second: Charge[T]) -> Charge[T] = first
+cheaper[T](first: Charge[T], second: Charge[T]) -> Charge[T] = if second.cents < first.cents then second else first
 
```

`second.cents < first.cents`, and not `<=`, keeps the first charge on a tie. The function never compares two values of `T`, so `[T]` with no constraint is enough, and `cheaper` works on a `Charge[Zone]` as well as on a `Charge[Text]`.
:::
::::

## 4.9 Recap and reference

### For agents

:::agents
`una --json check .` prints each diagnostic with its `code`, `message`, `primary` span and `repairs`; `una --json test .` prints each example's outcome. U2004 and U2026 carry exact edits, which `una fix .` applies: the field's label, and the constraint `[T: Eq]`. U2007's repair names the missing variant, but the arm's value depends on intent, so add it by hand. U1001, U2001, U2009 and U2025 depend on intent. The compact rule: *a record builds with every field labeled; a sum lists its variants with `|`, and one of a single variant starts with `|`; a `when` over a sum matches every variant or ends with `else`; a public generic function writes the constraint its body needs.*
:::

### Recap

:::recap
- `kind Parcel` with indented fields is a record: build it with every field labeled, and read a field with a dot.
- A record never changes: to change a field, build a new record from the old one.
- Records are nominal: two kinds with the same fields are two types. An alias, `kind Sku = Text`, is the type it names.
- `kind Zone = Local | National | Abroad` is a sum; a variant may carry fields, and a sum of one variant starts with `|`.
- `value is AtLocker` tests the variant and gives a `Bool`.
- `when` takes a sum apart: one arm per variant, each binding the fields it uses, or `else` for the rest.
- Leave out `else` where each variant needs its own answer: a new variant is then reported.
- Generic kinds and functions take type parameters, `[T]`, with the weakest constraint the body needs.
:::

### Reference

:::reference
- Construct pages: [`kind`](/docs/language/types/kind/), [`when`](/docs/language/control-flow/when/), [constraints on generics](/docs/language/types/constraints/), [`example`](/docs/language/examples/example/)
- Prelude: [`Option`](/docs/std/)
- Commands: [`una check`](/docs/cli/check/), [`una test`](/docs/cli/test/), [`una fix`](/docs/cli/fix/), [`una contract`](/docs/cli/contract/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2004](/docs/errors/U2004/), [U2007](/docs/errors/U2007/), [U2008](/docs/errors/U2008/), [U2009](/docs/errors/U2009/), [U2025](/docs/errors/U2025/), [U2026](/docs/errors/U2026/), [U2027](/docs/errors/U2027/), [U7001](/docs/errors/U7001/)
- Specification: [types](/docs/spec/03-types/), [grammar](/docs/spec/02-grammar/), [functions and contracts](/docs/spec/04-functions-and-contracts/), [static semantics](/docs/spec/10-static-semantics/), [constraints on generics](/docs/spec/20-constraints-on-generics/)
:::
