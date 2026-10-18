---
learn: "4"
title: Kinds
editions: ["0.2"]
codes: [U1001, U1002, U2001, U2002, U2004, U2007, U2008, U2009, U2025, U2026, U5001]
time: 60
builds: A shipment tracker that prices parcels and follows each one from packing to delivery or return
prerequisites: ["2", "3"]
template: 2
nav: ["Records", "Sum kinds", "when", "Generic kinds and constraints", "Kinds that contain themselves", "Day-to-day: shipment tracking", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---

# 4 Kinds

A working program is mostly about the shape of its data: a parcel has an order number, a weight and a zone; a shipment is packed, in transit, delivered or returned, and each of those states knows different things. In Una you declare that shape as a kind: a record of named fields, or a sum of variants. The checker then holds every function to it. A field cannot be forgotten, a state cannot carry data it does not have, and a `when` that misses a state does not check. This chapter declares the kinds of a shipment tracker for a small store.

## What you'll build

:::build
A shipment tracker for a small store. It prices each parcel by zone and weight, follows a shipment through the events a carrier reports, ignores a scan that arrives twice, and says whether a returned parcel is owed a refund:

```text include="day-to-day/expected/output.txt"
A-1001: postage 600
A-1001: with the courier, tracking CX-4471
A-1001: no change, still with the courier, tracking CX-4471
A-1001: delivered on day 3
A-1002: postage 1200
A-1002: returned on day 12, damaged; refund due: true
```

You will learn to:

- declare a record kind, build its values with labeled fields, and read them with a dot;
- declare a sum kind whose variants carry only the data that is true in that state;
- take a value apart with `when`, and let the checker find the arm you forgot;
- write a generic kind, and constrain a generic function with `Eq` or `Ord`;
- declare a kind that contains itself, and test a program built from kinds with examples.
:::

## Why it works this way

Many programs describe a shipment with one object and a string: `status = "in_transit"`, with a `tracking` field that is null, an empty value that means "nothing here", unless the status says otherwise, and a `delivered_on` field that is null in three states out of four. Nothing stops a value that is "delivered" with no date, or "packed" with a tracking number. A typo in `"in_trnasit"` is a new status. When a new status is added, every `switch`, a choice among the statuses with a `default` branch for the ones it does not name, is still accepted by the tools, and quietly does the wrong thing.

Una gives the shape a type:

:::steps
1. **A record is a type of its own.** `Parcel` has exactly its fields, every one of them is given when a value is built, and a `Parcel` is never mistaken for another record with the same fields.
2. **A sum lists every state.** `Status` is `Packed`, `InTransit`, `Delivered` or `Returned`, and nothing else. Each variant carries its own fields: only `InTransit` has a tracking number, and only `Delivered` and `Returned` have a day.
3. **`when` covers every variant.** A `when` over a `Status` has an arm for each variant, or an `else`. Add a variant, and the checker points at every `when` that needs a new arm.
:::

The price is a few more declarations at the top of a module. In return, a value that makes no sense cannot be built, and a change to the shape of the data shows every place it touches.

> [!KEY]
> Declare the states your data can be in as the variants of a sum, each carrying only what is true in that state. Then a value that makes no sense cannot be built, and no code can forget a state.

## 4.1 Records

### What a type and a kind are

A **type** is a set of values, together with what you may do with them. You met the built-in ones in [chapter 2](/learn/values/): `Int` is the set of whole numbers, and you may add them; `Text` is the set of texts, and you may cut them; `Bool` is the set of two values, `true` and `false`. Every value in Una has a type, and the checker uses the types to refuse a program that, say, adds a text to a number.

The built-in types describe single values. A store's data is made of several values that belong together: a parcel has an order number, a weight and an address, and an address has a name, a street and a city. A **kind** is a type that you declare yourself, with the keyword `kind`, to describe such data. Una has four forms of kind, and this chapter teaches three of them:

- A **record** groups several named values that are all there at once. This section.
- A **sum** is one of several cases. [Section 4.2](#s4-2).
- An **alias** gives an existing type another name. [Aliases](#aliases-another-name-for-a-type), in this section.

The fourth form, a kind with a condition such as "never negative", is in [chapter 7](/learn/contracts/#s7-3).

Think of a record as a printed form, such as a shipping label with its boxes: "order", "weight", "name", "street", "city". The kind is the blank form. Each value of the kind is one filled-in copy, with something written in every box.

### Each step is a package

Each step of this chapter is a package, as in [chapter 1, Hello, Una](/learn/hello/#s1-1): a directory with `una.toml`, `verification.lock` and the module under `src/`. The manifest names the package and the module that `una run` starts:

```toml include="steps/02-records/una.toml" title="steps/02-records/una.toml"
[package]
name = "labels"
version = "0.1.0"
edition = "0.2"

[run]
entry = "labels"
grants = ["console"]
```

`verification.lock` pins the solver and is the same in every example: copy it from chapter 1, or take the step's package, whole, from the chapter's download, `04-kinds.tar.gz`. Then, in the package's directory:

```sh
una check .
una run .
```

### Why group values into a record

Without a record, a function that prints a parcel's label must take each part of the parcel as a parameter of its own:

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

`una run .` prints:

```text include="steps/01-loose/expected/output.txt"
A-1001: Corner Bakery, 12 Elm Road, Northfield, 1200 g
A-1002: 12 Elm Road, Northfield, Corner Bakery, 300 g
```

The second line is wrong: the street is printed as the name and the store's name as the city. The call gave every label, so it checks, but the values went into the wrong boxes, and all three are `Text`, so the checker cannot tell. The loose form has other costs too:

1. **Every function repeats the list.** Each function that works on a parcel takes the same five parameters, and each call passes the same five values. Add a sixth part, a zone, and every one of them changes.
2. **A function returns one value.** A function that sends a parcel to a new address must return a parcel, its order, weight and address together. With loose values, there is nothing to return.
3. **Nothing says what belongs together.** A reader of `label` sees five values, not one parcel and its address.

A record answers all three. It gathers the values under one name, the function takes one parameter, and the result can be a whole parcel.

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
2. **`Address`.** The kind's name. Kind names start with a capital letter and capitalize each word, as `ReturnReason`.
3. **The fields.** One per line, indented two spaces under the name. A **field** is one named part of the record: `name`, `street` and `city`.
4. **`: Text` after each field.** The field's type. Every value of the kind has a value of that type in that field.

A field's type can be any type: `Int`, `Text`, `Bool`, a list of values ([chapter 5](/learn/collections/#s5-1)), or another kind.

#### Building a value

To make a value of a record kind, write the kind's name like a call, and give every field, each with its field's name as a label: `Address(name: "Corner Bakery", street: "12 Elm Road", city: "Northfield")`. Written this way, the kind's name is the **constructor**, the function that builds a value of the kind. The labels work like the labels of a call ([chapter 3](/learn/functions/#s3-1)), with one difference: a record of two or more fields labels every field, the first one too.

A record of one field may leave out the label. `Note("fragile")` builds the record `Note` of the step below, whose one field is `text`.

#### Reading a field with a dot

`parcel.grams` reads the field `grams` of the value `parcel`. When the field is itself a record, the dots go on: `parcel.address.city` is the city of the parcel's address.

#### A field whose kind is a record

A field can hold a whole record. `Parcel` has a field `address` of kind `Address`, so each parcel holds an address with its three fields. The checker knows the kind of every field, so `parcel.address.city` is a `Text`, and `parcel.address.grams` does not check.

### An address inside a parcel

The module `labels` declares two record kinds, builds a parcel, and redirects it:

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
2. **`Address(name: "Corner Bakery", street: …, city: …)`.** Building a value. Every field is given, each with its label. The parser takes them in any order, but `una check .` reports another order than the declared one as not canonical (U7001) until `una fmt .` puts them in that order. There are no default values: a field left out is an error.
3. **`parcel.address.city`.** Reading a field, and a field of a field.
4. **`redirect`.** A record never changes after it is built. To "change" a field, you build a new record from the old one, with the new value in that field. `parcel` itself is still sent home, as the first line of the output shows.
5. **`"{home}"`.** Interpolation writes a record in the form you would type in Una, with its kind's name and every field. This works from edition 0.2 on: in edition 0.1, interpolation takes only numbers, `Bool` and `Text`, and a record there is U2001.
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

--- The same box with another note. The parameter is not changed: the copy is.
relabel(box: Box, text: Text) -> Box
=
  let edit copy = box
  copy.note.text = text
  copy

pub main() -> Unit
  uses @console: Console[print]
=
  let fragile = Note("fragile")
  let lamp: Sku = "LAMP-01"
  let edit box = Box(sku: lamp, grams: 1200, note: fragile)
  let packed = box
  box.grams = 1500
  box.note.text = "this side up"
  @console.print("{packed}")
  @console.print("{box}")
  @console.print("same box: {packed == box}")
  @console.print("{lamp.len} characters in {lamp}")
  let heavy = relabel(packed, text: "heavy")
  @console.print("{packed.note.text}, then {heavy.note.text}")
```

`una run .` prints, among other lines:

```text include="steps/03-record-forms/expected/output.txt#L1-L4"
Box(sku: "LAMP-01", grams: 1200, note: Note("fragile"))
Box(sku: "LAMP-01", grams: 1500, note: Note("this side up"))
same box: false
7 characters in LAMP-01
```

#### Every field, every time

A value of a record has a value in every field. There are no default values and no empty fields: build a `Parcel` without its zone, and the checker reports U2009, "`Parcel` is missing field `zone`" ([Leaving out a field](#leaving-out-a-field-u2009) shows it whole). A field the kind does not declare is U2009 too, with "`Address` has no field `zip`", and so is reading one with a dot: `home.street` on a kind without `street` is U1001.

#### A value never changes; a binding can take a new one

A record value, once built, never changes. `redirect` shows the way to get a different parcel: build a new one. When you hold a record in an editable binding, a `let edit` ([chapter 2](/learn/values/#s2-4)), you may also assign one of its fields, as `box.grams = 1500` does in `main`. The assignment gives the binding `box` a new record, with 1500 in `grams` and the other fields as they were. `packed`, which took the box's value before the assignment, keeps the old one: the first line of the output still says 1200 grams. An assignment can reach a field of a field, as `box.note.text = "this side up"` does. It needs a `let edit`: on a plain `let`, `home.city = "Southport"` is U2019, "`home` is not editable".

#### Equality, and how a record prints

`==` compares two records field by field: two records are equal when every field is equal. `packed == box` is `false`, since their weights and notes differ. Interpolation writes a record as you would build it, with its kind's name and every field labeled, and a record of one field without its label, as `Note("fragile")` shows. Interpolating a record, a variant or an `Option` needs edition 0.2 or later; in edition 0.1 it is U2001, "interpolation converts `Int`, `Bool` and `Text` to text".

#### Records are nominal

Records are **nominal**: two kinds with the same fields are two different types, because a kind is known by its name. Declare a `Warehouse` with the same three fields as `Address`, and pass one where the parcel needs an address:

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

Read it from the top. The first line names the problem: the argument `address` of `redirect` must be an `Address`, and it is a `Warehouse`. The mark points at `office`, the value of the wrong kind. The fields are the same, but a warehouse is not a customer's address, and the checker keeps the two apart. To send a parcel to the warehouse, build an `Address` from its fields.

### Aliases: another name for a type

`kind Sku = Text`, in the step of this part, is an **alias**: another name for an existing type. A `Sku` is a `Text` wherever one is expected, and the other way round, so `lamp.len` works on it as on any text, and `"LAMP-01"` can be given where a `Sku` goes. An alias is written `kind`, its name, `=` and the type it names. It may name another alias.

An alias documents what a field holds: `sku: Sku` says more than `sku: Text`. It does not keep two kinds apart the way a record does: a `Sku` and a customer's name are both `Text`, and the checker lets one go where the other goes. [Chapter 7, Contracts and the verifier](/learn/contracts/#s7-3), adds a condition to an alias, as in `kind Cents = Int where it >= 0`, and the verifier proves it.

### A record, loose values or an alias

:::decide
**Which to use:**

| Your data… | Use |
| --- | --- |
| Has several parts that belong together, all there at once | A record, such as `kind Parcel` with its fields |
| Is passed around and returned as a whole | A record: one parameter, one result |
| Is one or two values that a single function needs | Plain parameters |
| Is an existing type under a name that says what it holds | An alias, such as `kind Sku = Text` |
| Must not be mixed up with another kind of the same shape | A record: records are nominal, aliases are not |
:::

### Check yourself: records

`relabel`, in the step of this part, copies a box into a `let edit` binding and assigns its note. `main` then calls it:

```una include="steps/03-record-forms/src/packing.una#L36-L37" title="steps/03-record-forms/src/packing.una"
  let heavy = relabel(packed, text: "heavy")
  @console.print("{packed.note.text}, then {heavy.note.text}")
```

`packed` holds the box with the note `"fragile"`. What does the last line print?

:::answer Show the answer
```text include="steps/03-record-forms/expected/output.txt#L5"
fragile, then heavy
```

`relabel` assigns the note of `copy`, its own binding, and returns that. The value passed in, `packed`, never changes, so it still says `"fragile"`. Only the returned box, `heavy`, has the new note.
:::

## 4.2 Sum kinds

### What a sum kind is

A **sum kind** is a type whose values are each one of a fixed list of cases. Each case is a **variant**. A zone is local, national or abroad; a shipment is packed, in transit, delivered or returned. Think of a box on a paper form where you tick exactly one option: "door", "locker" or "store". A sum is that box, and a value is the ticked option.

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

The program checks and runs, and two of its three lines are wrong. `"in_trnasit"` is a typo, and `"returned"` is a status that `customer_note` does not know. Both fall into the last `else`, so a parcel on its way and a parcel that came back are both "being packed". Any text is a valid `Text`, so the checker cannot tell a status from a typo, and nothing points at `customer_note` when a new status appears.

A sum fixes the list of statuses in one declaration. A misspelt variant is a name that does not exist, which does not check, and a `when` over the sum must say what to do with every variant ([section 4.3](#s4-3)).

### How to write a sum kind

A sum kind is written `kind`, its name, `=`, then its variants separated by `|`, all on one line. Variant names start with a capital letter, as kind names do.

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

A sum with a single variant starts with `|`. Without it, `kind QuoteError = NoCarrier` would be an alias of a type named `NoCarrier` ([A sum of one variant without its bar](#a-sum-of-one-variant-without-its-bar) shows what the checker says). Sums of one variant are common for failures, which [chapter 6](/learn/failure/) declares.

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
4. **`AtLocker(locker: "Station 14")`.** A variant with fields is built like a record. A variant with one field may leave out the label.
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

A variant with fields prints as you would build it: one field without its label, as `AtLocker("Station 14")`, and two or more with their labels. As for records, interpolating a variant needs edition 0.2 or later.

### How a sum behaves

#### A variant is tested with `is`

`delivery is AtLocker` is `true` when `delivery` is a locker delivery, whatever its locker. `is` names the variant only, never its fields, and works on a variant with fields or without. It gives a `Bool`, so it fits wherever a condition goes: in an `if`, after `not`, or as a function's whole body, as `needs_code` shows.

#### Equality compares whole values

`==` and `!=` compare two values of the same sum. They are equal when they are the same variant and every field is equal. `AtDoor == AtDoor` is `true`. Two store deliveries to the same store at different hours are not equal.

#### Only variants without fields have an order

`<`, `<=`, `>` and `>=` work on a sum whose variants have no fields, in the order the declaration lists them: `Local < Abroad` is `true`. A sum with fields has no order, since nothing says whether a locker comes before a store.

#### A variant with fields is not a value alone

`AtLocker` on its own names the variant, not a value: a locker delivery needs its locker. These three lines break the rules of this part:

```diff include="steps/06-sums..steps/08-variant-rules:src/carriers.una" title="src/carriers.una" context="0"
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

```text include="steps/08-variant-rules/expected/rendered.txt#L1-L13"
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

**Variant names are unique in a module.** The two marks show the two places: `AtDoor` is first a variant of `Delivery`, on line 7, and then of `Packing`, on line 10. A variant's name is a value, so `AtDoor` must mean one thing in the module. Rename one of them.

The second error is the variant without its fields:

```text include="steps/08-variant-rules/expected/rendered.txt#L14"
[U2009] Error: variant `AtLocker` needs its fields: `locker`
```

The message lists what is missing: the field `locker`. Write `AtLocker(locker: "Station 14")`, or, to ask whether a value is a locker delivery, `value is AtLocker`.

The third is an order on a sum with fields:

```text include="steps/08-variant-rules/expected/rendered.txt#L23"
[U2001] Error: `<` orders `Int`, `Text` and variants without fields, not `Delivery`
```

#### A sum of one variant without its bar

Remove the bar from `QuoteError`:

```diff include="steps/06-sums..steps/07-no-bar:src/carriers.una" title="src/carriers.una" context="0"
--- a/src/carriers.una
+++ b/src/carriers.una
@@ -10 +10 @@
-kind QuoteError = | NoCarrier
+kind QuoteError = NoCarrier
```

```text include="steps/07-no-bar/expected/rendered.txt#L1-L9"
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

Without `|`, the right-hand side is a type, so `QuoteError` is read as an alias, and the checker looks for a type named `NoCarrier`. It finds none, and reports U1001 at that name. A second U1001 follows wherever the program uses `NoCarrier` as a value. Both disappear when the bar is back: `kind QuoteError = | NoCarrier`.

### A record, a sum or an alias

:::decide
**Which to use:**

| Your data… | Use |
| --- | --- |
| Has several parts that are all there at once | A record: `kind Parcel` with fields |
| Is one of several cases, each with its own data | A sum: `kind Delivery = AtDoor \| AtLocker(locker: Text)` |
| Is one of a fixed list of names, with no data | A sum of variants without fields: `kind Zone = Local \| National \| Abroad` |
| Is another type, under a name that says what it holds | An alias: `kind Sku = Text` |
| Is a boolean flag that will grow a third case | A sum from the start, not a `Bool` |
| Is a status written as a text | A sum: the checker then knows every status |
:::

A record and a sum combine. A variant's field can be a record, and a record's field can be a sum, as `Parcel` has a `zone` in the day-to-day program.

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

## 4.3 Taking a value apart: `when`

### What `when` is

`when` chooses what to do by the variant of a value. Think of a sorting table in a warehouse, with one bin for each kind of delivery. Each parcel goes into the bin that matches its label, and each bin has its own instructions. `when` is that table:

- The **subject** is the value after `when`: the parcel on the table.
- An **arm** is one line under it: one bin, with its instructions.
- The **pattern** is the start of an arm, such as `is AtLocker(locker)`: what the arm matches.
- After `->` comes the arm's value: what the `when` gives when that arm matches.

`when` is an expression, as `if` is ([chapter 3](/learn/functions/#s3-3)): it gives the value of the arm that matched, so it can be a function's body or the value of a `let`.

### Why `when` exists

`is` says which variant a value is. It does not give you the variant's fields. Try to read the locker of a locker delivery after testing it:

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

The mark points at `locker` in `delivery.locker`. A `Delivery` has no field `locker`: only the variant `AtLocker` has one, and the checker does not use the `if` to narrow the value to that variant. The function has a second problem that no message points at: a store delivery falls into the `else`, so it would say "delivered to the door". An `if` covers the cases you thought of, and the rest fall into its `else`.

`when` solves both. Each arm names a variant and can **bind** its fields, which means give each field's value a name that the arm can use. The checker also makes sure every variant has an arm.

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

The step of this part has one small function for each form an arm takes. Its `main` prints one line for each.

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

#### Literal arms

A `when` also works on an `Int` or a `Text`. An arm `is 2` matches the value 2, and `is "RUG-07"` the text `"RUG-07"`. A **literal** is a value written out in the code, such as `2` or `"RUG-07"`.

```una include="steps/10-when-forms/src/desk.una#aisle_name..family" title="steps/10-when-forms/src/desk.una"
--- Literal arms: whole numbers, then `else` for every other value.
aisle_name(aisle: Int) -> Text
=
  when aisle
    is 1 -> "lighting"
    is 2 -> "rugs"
    else -> "aisle {aisle}"

--- Literal arms over a text.
family(sku: Text) -> Text
=
  when sku
    is "LAMP-01" -> "lamps"
    is "RUG-07" -> "rugs"
    else -> "other"
```

```text include="steps/10-when-forms/expected/output.txt#L4-L5"
rugs; aisle 7
rugs
```

The whole numbers and the texts never run out, so a `when` with literal arms ends with an `else`.

#### Range arms

`in 1..<10` matches a whole number from 1 up to 10, 10 left out, and `in 10..49` one from 10 to 49, both ends included. The two forms of range are those of [chapter 5](/learn/collections/#s5-2): `..` includes its end, and `..<` leaves it out.

```una include="steps/10-when-forms/src/desk.una#box_size" title="steps/10-when-forms/src/desk.una"
--- Range arms: `..` includes its end, `..<` leaves it out.
box_size(units: Int) -> Text
=
  when units
    in 1..<10 -> "small box"
    in 10..49 -> "large box"
    else -> "pallet"
```

```text include="steps/10-when-forms/expected/output.txt#L6"
small box; large box; pallet
```

9 units fit a small box, 10 need a large one, and 50 go on a pallet.

#### The `else` arm

`else -> value` matches every value that no arm above it matched. It is always the last arm. `aisle_name` uses one for every aisle without a name of its own, and `store_name` for every delivery that is not a store.

#### An arm of several lines

When an arm needs more than one line, write nothing after `->`, and put the arm's lines under it, indented two more spaces. The lines are a block, as a function's body is ([chapter 3](/learn/functions/#s3-2)): `let` lines first, and the block's value is its last line.

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

```text include="steps/10-when-forms/expected/output.txt#L7"
Harbour Road, 9:00 to 18:00
```

#### `when` as the value of a `let`

A `when` can stand after `let`, and the name takes the value of the arm that matched:

```una include="steps/10-when-forms/src/desk.una#L81-L84" title="steps/10-when-forms/src/desk.una"
  let urgent = when locker
    is AtDoor -> "no"
    else -> "yes"
  @console.print("collect soon: {urgent}")
```

```text include="steps/10-when-forms/expected/output.txt#L8"
collect soon: yes
```

### Postage by zone, weight and delivery

The module `postage` puts the forms to work on a parcel: a `when` over a sum, over ranges of an `Int`, and with arms that bind fields:

:::steps
```una include="steps/11-when/src/postage.una" title="steps/11-when/src/postage.una" verified="check, run"
module postage

kind Zone = Local | National | Abroad

kind Delivery = AtDoor | AtLocker(locker: Text) | AtStore(store: Text, opens: Int)

--- The price of a zone, in cents. One arm for each variant, and no `else`.
zone_cents(zone: Zone) -> Int
=
  when zone
    is Local -> 300
    is National -> 450
    is Abroad -> 1200

--- The supplement for a weight, by bands. Ranges need an `else` for the values they leave out.
weight_cents(grams: Int) -> Int
=
  when grams
    in 0..500 -> 0
    in 501..2000 -> 150
    else -> 400

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
  @console.print("{zone_cents(National) + weight_cents(1200)} cents")
  @console.print(pickup_note(AtStore(store: "Harbour Road", opens: 9)))
  @console.print(pickup_note(AtLocker(locker: "Station 14")))
```

1. **`zone_cents`.** One arm per variant and no `else`. If `Zone` gains a variant, this `when` stops checking until it has an arm for it. That is why it has no `else`: an `else` would give a new zone the price of some other zone, silently.
2. **`weight_cents`.** Arms over ranges of an `Int`: `in 0..500` includes both ends, so 500 grams pays nothing. The `else` covers everything above 2,000 grams, and also every value the ranges leave out.
3. **`is AtLocker(locker) -> …`.** The arm binds the field `locker` and uses it. An arm binds only the fields it needs: `is AtDoor` binds none.
4. **`is AtStore(store, opens) -> …`.** The names bind the fields of the same names.
:::

`una run .` prints:

```text include="steps/11-when/expected/output.txt"
600 cents
collect at Harbour Road from 9:00
collect at locker Station 14
```

### How `when` behaves

#### The arms are tried in order

When the program runs, the arms are tried from the first to the last, and the first that matches gives the value. Over variants, at most one arm can match each value. Over literals, the same: a literal repeated in a later arm is U2008, "this literal is already matched by an earlier arm". Ranges may overlap, and then the first arm that matches wins: with `in 1..5` and then `in 3..8`, the value 4 takes the first arm. Write ranges that do not overlap, so that their order does not change the answer.

#### Every variant has an arm

The checker makes sure that every variant of the subject's kind has an arm, or that an `else` covers the ones left out. A `when` over a `Zone` with arms for `Local` and `National` only is U2007, "`when` does not match variant `Abroad` of `Zone`", and its help offers the repair: an arm for each missing variant, or an `else`. [A `when` that misses a variant](#a-when-that-misses-a-variant-u2007) shows the whole diagnostic.

This rule is what makes a sum safe to grow. Add a variant to a kind, and every `when` over it without an `else` stops checking, each one at its `when` line, until it says what the new variant means.

> [!TIP]
> Prefer an arm per variant to `else` on a sum that will grow. Keep `else` for "every other case is the same", as `refund_due` does in the day-to-day program, and for literals and ranges.

#### `else` comes last, and every arm can be reached

An arm that no value can reach is an error, U2008. Move the `else` of `aisle_name` to the top:

```diff include="steps/10-when-forms..steps/12-when-rules:src/desk.una" title="src/desk.una" context="1"
--- a/src/desk.una
+++ b/src/desk.una
@@ -31,5 +31,5 @@
   when aisle
+    else -> "aisle {aisle}"
     is 1 -> "lighting"
     is 2 -> "rugs"
-    else -> "aisle {aisle}"
 
```

```text include="steps/12-when-rules/expected/rendered.txt#L1-L12"
[U2008] Error: this arm follows the `else` arm, so no value reaches it; `else` must be the last arm
    ╭─[ src/desk.una:33:5 ]
    │
 32 │     else -> "aisle {aisle}"
    │     ──┬─
    │       ╰─── the `else` arm
 33 │     is 1 -> "lighting"
    │     ──┬─
    │       ╰─── this arm follows the `else` arm, so no value reaches it; `else` must be the last arm
    │
    │ Note: run `una explain U2008` for an explanation
────╯
```

The first mark shows the `else`, and the second an arm after it: `else` already matched every value, so `is 1` can never run. The checker reports each arm after the `else`, here two. The same code reports an arm for a variant that an earlier arm already matched, "variant `Local` is already matched by an earlier arm", an `else` after arms for every variant, "no value reaches this `else`", and a literal that an earlier arm already matched, "this literal is already matched by an earlier arm".

#### Ranges must cover every value

Over variants, the checker counts the arms. Over ranges with no `else`, it cannot: an `Int` has no end. So whether the ranges cover every value the subject can take is a **proof obligation**, a question that the verifier must answer for every possible input ([chapter 2](/learn/values/#s2-1) met the first ones). When some value falls between the ranges, the verifier reports U5001 with a **counterexample**: a value that no arm matches. [Ranges that leave a gap](#ranges-that-leave-a-gap-u5001) shows one, with `grams = -1`. An `else` ends the question.

#### The arms give one type

Every arm of a `when` gives a value of the same type, as both branches of an `if` do. An arm that gives a number where the others give a text is reported where it is written: in a function that returns `Text`, U2001, "`note` returns `Text`, found `Int`".

#### A bound name is new

The names an arm binds exist only in that arm. They are new names, so one cannot repeat a name already bound around the `when`, such as a parameter: binding `locker` in a function that has a parameter `locker` is U1002, "`locker` is already bound in this scope". Bind the field under another name, as `is AtLocker(locker: spot)`.

### `when`, `if` or `is`

:::decide
**Which to use:**

| You want to… | Use |
| --- | --- |
| A different value for each variant of a sum | `when`, one arm per variant |
| The fields of a variant | `when`, with an arm that binds them |
| One question about the variant, as a `Bool` | `is`: `delivery is AtLocker` |
| A different value for some numbers or texts | `when` with literal or range arms, and `else` |
| A choice on a condition, such as `grams > 2000` | `if` ([chapter 3](/learn/functions/#s3-3)) |
| The same answer for every other variant | `when` with `else` last, knowing that a new variant gets it too |
:::

### Check yourself: `when`

The step of this part ends with a function that chooses a shelf by how many units arrive:

```una include="steps/10-when-forms/src/desk.una#shelf" title="steps/10-when-forms/src/desk.una"
--- The shelf for a number of units. Check yourself: what does `main` print for 0, 5 and 12?
shelf(units: Int) -> Text
=
  when units
    in 1..4 -> "low shelf"
    in 5..10 -> "middle shelf"
    else -> "floor"
```

`main` prints `shelf(0)`, `shelf(5)` and `shelf(12)` on one line. What does it print?

:::answer Show the answer
```text include="steps/10-when-forms/expected/output.txt#L9"
floor; middle shelf; floor
```

5 is in `1..4`? No: 4 is that range's end. It is in `5..10`, so it goes on the middle shelf. 12 is above 10, so it falls to `else`. 0 is in neither range either, so it falls to `else` too: an `else` catches values below the ranges as well as above them. Without it, the verifier would report U5001 with a value that no arm matches as its counterexample, such as 11.
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

The type parameter goes in brackets after the kind's name. Inside the declaration, `T` stands for whatever type the kind is used with, as a field type or as part of one. Both fields have the type `T`, so the two values of one change always have the same type.

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

A sum can take a type parameter too. The prelude's `Option[T]`, a value that may be missing, is one: `Some(value)` holds a `T`, and `None` holds nothing. `Some("LAMP-01")` is an `Option[Text]`, as the last line of the output shows. [Chapter 5, Collections](/learn/collections/#s5-3), uses it everywhere.

### Generic functions and their constraints

A function can take type parameters too, written in brackets after its name: `undo[T](change: Change[T]) -> Change[T]` works on a change of any type. Inside it, `T` is a type the function knows nothing about. It can move values of `T` around, put them in fields, and return them, but not compare them, since some types cannot be compared.

A **constraint** says what the function needs from `T`, and in exchange limits the types it accepts. It is written after the parameter, with a colon: `changed[T: Eq]`. Una has three, each including the one before. The **fixed-width integers** in the table are the types such as `U8` and `I32` of [section 2.5](/learn/values/#s2-5), and `x.to_int()` turns one into an `Int`:

| Constraint | Allows on values of `T` | Satisfied by |
| --- | --- | --- |
| `Eq` | `==`, `!=`, and interpolation | every type whose values hold no functions |
| `Ord` | what `Eq` allows, and `<`, `<=`, `>`, `>=` | `Int`, the fixed-width integers, `Text`, and sums whose variants have no fields |
| `Integer` | what `Ord` allows, and `x.to_int()` | `Int` and the fixed-width integers |

A record or a sum is `Eq` when its values hold no functions, and only a sum without fields is `Ord`. A list or an `Option` is `Eq` when its elements are.

> [!NOTE]
> Constraints exist from edition 0.2 on, the edition of every package in this book. In edition 0.1, a type parameter takes no constraint, and the checker works out on its own whether a function compares values of `T`.

### Undoing and comparing changes

The module `changes` declares `Change[T]` and three generic functions over it, with the three levels of need:

:::steps
```una include="steps/16-generics/src/changes.una" title="steps/16-generics/src/changes.una" verified="check, run"
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
3. **`changed[T: Eq]`.** `!=` compares two values of `T`, so `T` must be `Eq`: every type whose values hold no functions is, and a record with a function field is not.
4. **`larger[T: Ord]`.** `>` needs an order, so `T` must be `Ord`: `Int`, `Text`, the fixed-width integers, and sums whose variants carry no fields. `Zone` qualifies, so `larger(zone)` gives the farther zone.
5. **`Change(before: 1990, after: 1790)`.** `T` is inferred as `Int` here, `Text` for `name` and `Zone` for `zone`.
:::

`una run .` prints, among other lines:

```text include="steps/16-generics/expected/output.txt#L1-L3"
Change(before: 1790, after: 1990)
price changed: true, name changed: false
larger price 1990, farther zone Abroad
```

### How generics behave

#### One type per parameter, in every field

A type parameter stands for one type in each value. Build a `Change` with a text before and a number after:

```diff include="steps/14-generic-forms..steps/15-mixed-change:src/forms.una" title="src/forms.una" context="0"
--- a/src/forms.una
+++ b/src/forms.una
@@ -25 +25 @@
-  let name = Change(before: "Desk lamp", after: "Reading lamp")
+  let name = Change(before: "Desk lamp", after: 1790)
```

```text include="steps/15-mixed-change/expected/rendered.txt"
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

The checker took `T` from the first field, `Text`, so the second must be a `Text` as well, and the mark points at `1790`.

#### An operator needs its constraint

In a function that writes no constraint, `==` on values of `T` is U2026, with a repair that writes the constraint: "equality on values of the type parameter `T` needs the constraint `Eq`; write `[T: Eq]`". [Comparing values of a type parameter without `Eq`](#comparing-values-of-a-type-parameter-without-eq-u2026) shows it. Arithmetic is never defined on `T`, with a constraint or without: `a + b` on two values of a `T: Integer` does not check. Turn them into `Int` with `to_int()`, and add those.

#### A call passes a type that satisfies it

At each call, the type argument must satisfy the constraint. Pass `larger` a change of shelves, a record:

```diff include="steps/16-generics..steps/17-constraint-rules:src/changes.una" title="src/changes.una" context="0"
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

A kind's type parameters take no constraint: `kind Change[T: Eq]` is a syntax error, U0101. The kind only holds values; the functions that compare them state what they need. A name other than `Eq`, `Ord` or `Integer` after the colon is U2027, "`Same` is not a constraint".

#### A private function's constraint is inferred

A private function may leave its constraint out, and the checker infers the least one its body needs, as it infers a private function's `uses` ([chapter 3](/learn/functions/#s3-4)). `differs`, in the step of [How to write a generic kind](#how-to-write-a-generic-kind), compares with `!=` and writes no constraint. `una contract` shows what the checker inferred:

```sh
una contract forms.differs
```

```text include="steps/14-generic-forms/expected/commands/contract.txt#L3"
differs[T: Eq](before: T, after: T) -> Bool -- inferred
```

A `pub` function writes its constraints: its callers in other modules rely on its header.

### The weakest constraint the body needs

:::decide
**Which to use:**

| The body… | Write |
| --- | --- |
| Only moves values of `T`: stores, swaps, returns them | `[T]`, no constraint |
| Compares values with `==` or `!=`, or puts them in a text | `[T: Eq]` |
| Orders values with `<`, `>`, `min` or `max` | `[T: Ord]` |
| Needs the number, with `to_int()` | `[T: Integer]` |
| Works on one type only | No type parameter: name the type |
:::

Write the weakest constraint the body needs. `undo` needs none, so it works on a `Change` of any type. `changed` needs `Eq`, and `larger` needs `Ord`, which also gives `Eq`. A stronger constraint than the body uses only refuses callers for no reason.

### Check yourself: generics

`main` ends with a change of a product name that only changes one letter's case:

```una include="steps/16-generics/src/changes.una#L28-L29" title="steps/16-generics/src/changes.una"
  let label = Change(before: "desk lamp", after: "Desk lamp")
  @console.print("{changed(label)} {larger(label)}")
```

Does `changed(label)` say `true` or `false`, and which name does `larger(label)` give?

:::answer Show the answer
```text include="steps/16-generics/expected/output.txt#L4"
true desk lamp
```

`"desk lamp"` and `"Desk lamp"` are different texts, since `==` compares character by character, so the change counts. `Text` is ordered character by character too, by each character's number in Unicode, where every capital letter comes before every small one. `d` comes after `D`, so `"desk lamp"` is the larger.
:::

## 4.5 Kinds that contain themselves

### What a recursive kind is

Some data holds smaller data of the same shape. A store sells gift kits: a kit holds two products, and each of them may be a single item or another kit. A box of boxes, like a set of nesting dolls. A **recursive kind** is a kind that contains itself in one of its fields, so a value can hold another value of its own kind, which can hold another, as deep as the data goes.

### Why a kind contains itself

With records of fixed fields, every level of nesting needs a kind of its own: a kit of items, a kit of kits of items, and so on, with a limit you choose in advance. A real catalog does not stop at the depth you planned. A recursive kind describes every depth with one declaration.

### How to write a recursive kind

```una include="steps/18-bundles/src/bundles.una#Bundle" title="steps/18-bundles/src/bundles.una"
--- A product the store sells: one item, or a kit of two products, each of which may be a kit.
kind Bundle = Item(sku: Text, cents: Int) | Kit(first: Bundle, second: Bundle)
```

A kind can contain itself in two ways.

#### A variant that holds its own kind

`Bundle` is a sum whose variant `Kit` has two fields of kind `Bundle`, the kind being declared. The variant `Item` has none, and that matters: it is where a bundle stops. Every value of `Bundle` is built from items at the bottom, with kits above them.

> [!NOTE]
> A kind that holds itself directly in a field, as `Kit` does, needs edition 0.2 or later, the edition of every package in this book. In edition 0.1, a kind may contain itself only through a `List` or an `Option` field, the form that follows; `Bundle` there is U2002, "kind `Bundle` contains itself through field `first`; a kind may contain itself only through `List` or `Option`".

#### Through a list or an option

A field may hold a list of values of the kind being declared, `List[GiftSet]`, or a value that may be missing, `Option[Category]`. A **list** is a sequence of values of one type, written in brackets, such as `[bulb, bulb]` ([chapter 5](/learn/collections/#s5-1) teaches lists). An **`Option`** holds either `Some(value)` or `None`, nothing ([section 4.4](#generic-sums) introduces it). This form works in every edition, and it needs no variant that ends: the empty list `[]` and `None` are where the value stops.

```una include="steps/19-gift-sets/src/kits.una" title="steps/19-gift-sets/src/kits.una" verified="check, run"
module kits

--- A gift set of any number of products, each of which may be a set. The kind contains itself
--- through a list, and the empty list is where a set stops.
kind GiftSet
  sku: Text
  parts: List[GiftSet]

--- A product category, inside a larger one or at the top. The kind contains itself through
--- an `Option`, and `None` is where the chain stops.
kind Category
  name: Text
  parent: Option[Category]

pub main() -> Unit
  uses @console: Console[print]
=
  let bulb = GiftSet(sku: "BULB-02", parts: [])
  let lamp = GiftSet(sku: "LAMP-01", parts: [bulb, bulb])
  @console.print("{lamp.sku} holds {lamp.parts.len} parts")
  let lighting = Category(name: "Lighting", parent: None)
  let lamps = Category(name: "Lamps", parent: Some(lighting))
  @console.print("{lamps}")
```

```text include="steps/19-gift-sets/expected/output.txt"
LAMP-01 holds 2 parts
Category(name: "Lamps", parent: Some(Category(name: "Lighting", parent: None)))
```

A gift set holds any number of parts, each a gift set, and a set with no parts, `parts: []`, is a single product. A category may sit inside a larger one, and `parent: None` marks the top. `lamp.parts.len` is the number of elements of the list: 2. Use a list when a value holds any number of parts, and an `Option` when it holds at most one, as a category has at most one parent.

### A reading kit, priced

A function over a recursive kind usually calls itself: for a kit, it computes the answer for each part and combines them. A function that calls itself is **recursive**, as [chapter 3](/learn/functions/#s3-1) showed with `marked_down`.

:::steps
```una include="steps/18-bundles/src/bundles.una" title="steps/18-bundles/src/bundles.una" verified="check, run"
module bundles

--- A product the store sells: one item, or a kit of two products, each of which may be a kit.
kind Bundle = Item(sku: Text, cents: Int) | Kit(first: Bundle, second: Bundle)

--- The price of a bundle: an item's price, or the prices of a kit's two parts added up.
price(bundle: Bundle) -> Int
=
  when bundle
    is Item(cents) -> cents
    is Kit(first, second) -> price(first) + price(second)

--- How many items a bundle holds. Check yourself: what does `main` print for `office`?
items(bundle: Bundle) -> Int
=
  when bundle
    is Item -> 1
    is Kit(first, second) -> items(first) + items(second)

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Item(sku: "LAMP-01", cents: 1990)
  let bulb = Item(sku: "BULB-02", cents: 350)
  let reading = Kit(first: lamp, second: Kit(first: bulb, second: bulb))
  @console.print("reading kit: {price(reading)} cents")
  @console.print("{reading}")
  let desk = Item(sku: "DESK-02", cents: 15900)
  let office = Kit(first: desk, second: reading)
  @console.print("office kit: {items(office)} items")
```

1. **`is Item(cents) -> cents`.** The bottom: an item's price is its own.
2. **`is Kit(first, second) -> price(first) + price(second)`.** A kit's price is the price of each part, added. Each call works on a smaller bundle, so the calls end at the items.
3. **`Kit(first: lamp, second: Kit(first: bulb, second: bulb))`.** A kit of a lamp and a kit of two bulbs: two levels.
:::

`una run .` prints, among other lines:

```text include="steps/18-bundles/expected/output.txt#L1-L2"
reading kit: 2690 cents
Kit(first: Item(sku: "LAMP-01", cents: 1990), second: Kit(first: Item(sku: "BULB-02", cents: 350), second: Item(sku: "BULB-02", cents: 350)))
```

The lamp costs 1990 and each bulb 350: 1990 + 350 + 350 = 2690. The second line prints the kit as you would build it, every level inside the one above.

### How a recursive kind behaves

#### Every kind needs a value that ends

Every value of a kind is finite: it must be possible to build one without going on forever. A kind whose every variant needs another value of the same kind has no such value. Declare one:

```diff include="steps/18-bundles..steps/20-endless:src/bundles.una" title="src/bundles.una" context="0"
--- a/src/bundles.una
+++ b/src/bundles.una
@@ -4,0 +5,3 @@
+
+--- A crate that always holds another crate: no value of it can ever be built.
+kind Crate = | Holds(inner: Crate)
```

```text include="steps/20-endless/expected/rendered.txt"
[U2002] Error: kind `Crate` has no finite value: every variant contains a kind without one; add a variant without it, as `End`
   ╭─[ src/bundles.una:7:6 ]
   │
 7 │ kind Crate = | Holds(inner: Crate)
   │      ──┬──
   │        ╰──── kind `Crate` has no finite value: every variant contains a kind without one; add a variant without it, as `End`
   │
   │ Note: run `una explain U2002` for an explanation
───╯
```

A `Crate` would hold a crate, which would hold a crate, without end, so no `Crate` can ever be built. U2002 says so, and its message gives the repair: a variant that does not contain the kind, such as `End`. In `Bundle`, `Item` is that variant. In edition 0.1, the same declaration is U2002 for another reason: `Crate` contains itself directly, which that edition allows only through a `List` or an `Option`.

#### A recursive call has a limit

Each level of a bundle is one more call of `price` waiting for its parts. A run has a limit on how many calls may wait at once, and a value deep enough to exceed it stops the run with U6003. Store data such as kits nests a few levels, far below the limit. For a long sequence of the same thing, use a list ([chapter 5](/learn/collections/#s5-1)) and a loop, which do not count calls.

### A recursive kind or a list

:::decide
**Which to use:**

| Your data… | Use |
| --- | --- |
| Is many values of one kind, in order | A list: `List[Item]` |
| Holds parts that are each a whole of the same kind | A recursive kind, with a variant that ends |
| Has a fixed depth, such as an order and its lines | Records, one per level |
:::

### Check yourself: recursive kinds

`items` counts the items of a bundle:

```una include="steps/18-bundles/src/bundles.una#items" title="steps/18-bundles/src/bundles.una"
--- How many items a bundle holds. Check yourself: what does `main` print for `office`?
items(bundle: Bundle) -> Int
=
  when bundle
    is Item -> 1
    is Kit(first, second) -> items(first) + items(second)
```

`office` is `Kit(first: desk, second: reading)`, where `desk` is an item and `reading` is the reading kit of this section. What does `items(office)` give?

:::answer Show the answer
```text include="steps/18-bundles/expected/output.txt#L3"
office kit: 4 items
```

`items(office)` is `items(desk) + items(reading)`. The desk is an item, 1. The reading kit is `items(lamp)` plus the items of its inner kit of two bulbs, 1 + 2 = 3. In all, 1 + 3 = 4. The bulb is counted twice, since the kit holds two of it.
:::

## 4.6 Day-to-day: shipment tracking

### What the program must do

Now the program from the start of the chapter. The store ships parcels by post or by courier. Each parcel has a price for its zone and its weight. Carriers report events: a pickup, a delivery, a parcel that came back. The tracker must keep each shipment's status, ignore an event that does not fit, such as a pickup scan sent twice, and say whether a returned parcel is owed a refund.

The program uses every part of the chapter: records for parcels, sums for zones, carriers, reasons, statuses and events, `when` to take each one apart, and a generic `Change[T]` to compare a status before and after an event.

### The kinds

The design starts from the kinds. Everything a function does follows from them.

```una include="day-to-day/src/tracking.una#Zone..Change" title="day-to-day/src/tracking.una" caption="the kinds"
--- How far a parcel travels.
pub kind Zone = Local | National | Abroad

--- A parcel ready to ship. `order` is the number on the customer's receipt.
pub kind Parcel
  order: Text
  grams: Int
  zone: Zone

--- Who carries a parcel.
pub kind Carrier = Post | Courier

--- Why a parcel came back.
pub kind ReturnReason = Damaged | WrongItem | Refused

--- Where a shipment is. Each state carries what is known in that state, and nothing else.
pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int)

--- What a carrier or the warehouse reports about a shipment.
pub kind Event = PickedUp(carrier: Carrier, tracking: Text) | DeliveredOn(day: Int) | CameBack(reason: ReturnReason, day: Int)

--- A value before and after something happened.
pub kind Change[T]
  before: T
  after: T
```

Read them in order:

- **`Zone`, `Carrier` and `ReturnReason`** are sums without fields: fixed lists of names. `Zone` is ordered nearest first.
- **`Parcel`** is a record of three fields, one of which is a `Zone`.
- **`Status`** is the heart of the program. Each variant carries what is known in that state: nothing while packed, a carrier and a tracking number while in transit, a day once delivered, a reason and a day once returned. A delivered status without a day cannot be written.
- **`Event`** is a second sum, for what the outside world reports, and its variants mirror the transitions.
- **`Change[T]`** records a value before and after an event. `Change[Status]` lets the report tell an event that changed something from one that did not.

Every kind is `pub`, so other modules can use it ([chapter 3](/learn/functions/#s3-4) explains `pub`).

### Pricing a parcel

`postage` adds the price of the zone to the supplement for the weight. Each part is a `when`: one arm per zone, and weight bands with an `else`, as in [section 4.3](#s4-3). `postage` is public and has a doc comment; its two helpers are private.

```una include="day-to-day/src/tracking.una#postage..weight_cents" title="day-to-day/src/tracking.una"
--- Postage in cents: a price for the zone, and a supplement for the weight.
pub postage(parcel: Parcel) -> Int = zone_cents(parcel.zone) + weight_cents(parcel.grams)

zone_cents(zone: Zone) -> Int
=
  when zone
    is Local -> 300
    is National -> 450
    is Abroad -> 1200

weight_cents(grams: Int) -> Int
=
  when grams
    in 0..500 -> 0
    in 501..2000 -> 150
    else -> 400
```

`zone_cents` has no `else`, so a new zone stops the program from checking until it has a price. `weight_cents` has an `else`, since weights never run out: it is what makes the bands cover every `Int`.

### Following events

`apply` takes the status and an event, and gives the next status. One `when` over the event, and in each arm a test of the status with `is`. An event that does not fit the current status leaves it as it is, so a second pickup scan, or a return before any delivery, changes nothing. `track` wraps the two statuses in a `Change`, and `changed` compares them with the `Eq` constraint of [section 4.4](#s4-4).

```una include="day-to-day/src/tracking.una#apply..changed" title="day-to-day/src/tracking.una"
--- The status after an event. An event that does not fit the status changes nothing, such
--- as a pickup scan that a carrier sends twice.
pub apply(status: Status, event: Event) -> Status
=
  when event
    is PickedUp(carrier, tracking) -> if status is Packed then InTransit(carrier, tracking) else status
    is DeliveredOn(day) -> if status is InTransit then Delivered(day) else status
    is CameBack(reason, day) -> if status is Delivered then Returned(reason, day) else status

--- What an event does to a status: the status before it, and after it.
pub track(status: Status, event: Event) -> Change[Status] = Change(before: status, after: apply(status, event))

--- Whether something changed. Any type whose values can be compared will do.
pub changed[T: Eq](change: Change[T]) -> Bool = change.before != change.after
```

Follow one event through it. `apply(Packed, event: PickedUp(carrier: Courier, tracking: "CX-4471"))` matches the first arm, which binds `carrier` and `tracking`. The status is `Packed`, so the arm builds `InTransit(carrier, tracking)` from the two fields it bound. The same event again, on that `InTransit` status, matches the same arm, but `status is Packed` is now `false`, and the arm gives `status` back unchanged.

Why ignore an event that does not fit, rather than fail? Carriers resend scans, and a report that arrives late is still a report. The tracker keeps the status it trusts, and the `Change` shows that nothing happened. [Chapter 6, Failure](/learn/failure/), shows how a function declares that it can fail, for the cases where an event that does not fit must stop the work. `Event` and `Status` are two kinds, not one, because what a carrier reports and what the store knows are different things: a `PickedUp` event carries what the status after it will hold, and nothing about the status before it.

`InTransit(carrier, tracking)` in the first arm builds a variant from two bindings of the same names as its fields. A name equal to the field's name counts as its label, so this is `InTransit(carrier: carrier, tracking: tracking)`.

### Words for people

`describe` has one arm per status and binds the fields it prints. `carrier_name` and `reason_text` turn variants without fields into words. None of them has an `else`, so a new carrier, reason or status is reported at the `when` that must say something about it. `refund_due` is the other kind of function: one case matters, and `else` covers the rest. A parcel refused at the door is not owed a refund, since the store sent it correctly.

```una include="day-to-day/src/tracking.una#describe..refund_due" title="day-to-day/src/tracking.una"
--- A status, for a person to read.
pub describe(status: Status) -> Text
=
  when status
    is Packed -> "packed, waiting for a carrier"
    is InTransit(carrier, tracking) -> "with {carrier_name(carrier)}, tracking {tracking}"
    is Delivered(day) -> "delivered on day {day}"
    is Returned(reason, day) -> "returned on day {day}, {reason_text(reason)}"

carrier_name(carrier: Carrier) -> Text
=
  when carrier
    is Post -> "the post"
    is Courier -> "the courier"

reason_text(reason: ReturnReason) -> Text
=
  when reason
    is Damaged -> "damaged"
    is WrongItem -> "the wrong item"
    is Refused -> "refused at the door"

--- Whether the store owes the customer a refund: only for a parcel that came back by the
--- store's fault.
pub refund_due(status: Status) -> Bool
=
  when status
    is Returned(reason) -> reason != Refused
    else -> false
```

`is Returned(reason) -> reason != Refused` binds one of the two fields of `Returned` and leaves `day` out. `reason != Refused` compares two values of `ReturnReason` with `!=`, which works on any kind without functions.

### Running it

`main` prices a lamp, then sends it through a pickup, the same pickup again, and a delivery. Then it prices a vase sent abroad and reports its return. Each line comes from `report`, which says "no change" when the event did not change the status.

```una include="day-to-day/src/tracking.una#report..main" title="day-to-day/src/tracking.una"
--- One line of the tracking report.
pub report(order: Text, change: Change[Status]) -> Text = if changed(change) then "{order}: {describe(change.after)}" else "{order}: no change, still {describe(change.after)}"

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
  @console.print("{lamp.order}: postage {postage(lamp)}")
  let picked = track(Packed, event: PickedUp(carrier: Courier, tracking: "CX-4471"))
  @console.print(report(lamp.order, change: picked))
  let again = track(picked.after, event: PickedUp(carrier: Courier, tracking: "CX-4471"))
  @console.print(report(lamp.order, change: again))
  let arrived = track(again.after, event: DeliveredOn(day: 3))
  @console.print(report(lamp.order, change: arrived))
  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad)
  @console.print("{vase.order}: postage {postage(vase)}")
  let back = track(Delivered(day: 8), event: CameBack(reason: Damaged, day: 12))
  @console.print("{report(vase.order, change: back)}; refund due: {refund_due(back.after)}")
```

Each event starts from the status the event before it left: `picked.after`, then `again.after`. `una run .` prints the report shown in [What you'll build](#what-youll-build). The third line is the duplicate scan: the status stayed `InTransit`, and the report says so instead of pretending something happened. Nothing in `main` can build a delivered shipment without a day, or a shipment in transit without a tracking number, because `Status` has no such variant.

### The whole program

The whole file, to read in one piece or to copy:

```una include="day-to-day/src/tracking.una" title="day-to-day/src/tracking.una" caption="the whole program" verified="check, run, test"
module tracking

--- How far a parcel travels.
pub kind Zone = Local | National | Abroad

--- A parcel ready to ship. `order` is the number on the customer's receipt.
pub kind Parcel
  order: Text
  grams: Int
  zone: Zone

--- Who carries a parcel.
pub kind Carrier = Post | Courier

--- Why a parcel came back.
pub kind ReturnReason = Damaged | WrongItem | Refused

--- Where a shipment is. Each state carries what is known in that state, and nothing else.
pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int)

--- What a carrier or the warehouse reports about a shipment.
pub kind Event = PickedUp(carrier: Carrier, tracking: Text) | DeliveredOn(day: Int) | CameBack(reason: ReturnReason, day: Int)

--- A value before and after something happened.
pub kind Change[T]
  before: T
  after: T

--- Postage in cents: a price for the zone, and a supplement for the weight.
pub postage(parcel: Parcel) -> Int = zone_cents(parcel.zone) + weight_cents(parcel.grams)

zone_cents(zone: Zone) -> Int
=
  when zone
    is Local -> 300
    is National -> 450
    is Abroad -> 1200

weight_cents(grams: Int) -> Int
=
  when grams
    in 0..500 -> 0
    in 501..2000 -> 150
    else -> 400

--- The status after an event. An event that does not fit the status changes nothing, such
--- as a pickup scan that a carrier sends twice.
pub apply(status: Status, event: Event) -> Status
=
  when event
    is PickedUp(carrier, tracking) -> if status is Packed then InTransit(carrier, tracking) else status
    is DeliveredOn(day) -> if status is InTransit then Delivered(day) else status
    is CameBack(reason, day) -> if status is Delivered then Returned(reason, day) else status

--- What an event does to a status: the status before it, and after it.
pub track(status: Status, event: Event) -> Change[Status] = Change(before: status, after: apply(status, event))

--- Whether something changed. Any type whose values can be compared will do.
pub changed[T: Eq](change: Change[T]) -> Bool = change.before != change.after

--- A status, for a person to read.
pub describe(status: Status) -> Text
=
  when status
    is Packed -> "packed, waiting for a carrier"
    is InTransit(carrier, tracking) -> "with {carrier_name(carrier)}, tracking {tracking}"
    is Delivered(day) -> "delivered on day {day}"
    is Returned(reason, day) -> "returned on day {day}, {reason_text(reason)}"

carrier_name(carrier: Carrier) -> Text
=
  when carrier
    is Post -> "the post"
    is Courier -> "the courier"

reason_text(reason: ReturnReason) -> Text
=
  when reason
    is Damaged -> "damaged"
    is WrongItem -> "the wrong item"
    is Refused -> "refused at the door"

--- Whether the store owes the customer a refund: only for a parcel that came back by the
--- store's fault.
pub refund_due(status: Status) -> Bool
=
  when status
    is Returned(reason) -> reason != Refused
    else -> false

--- One line of the tracking report.
pub report(order: Text, change: Change[Status]) -> Text = if changed(change) then "{order}: {describe(change.after)}" else "{order}: no change, still {describe(change.after)}"

pub main() -> Unit
  uses @console: Console[print]
=
  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
  @console.print("{lamp.order}: postage {postage(lamp)}")
  let picked = track(Packed, event: PickedUp(carrier: Courier, tracking: "CX-4471"))
  @console.print(report(lamp.order, change: picked))
  let again = track(picked.after, event: PickedUp(carrier: Courier, tracking: "CX-4471"))
  @console.print(report(lamp.order, change: again))
  let arrived = track(again.after, event: DeliveredOn(day: 3))
  @console.print(report(lamp.order, change: arrived))
  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad)
  @console.print("{vase.order}: postage {postage(vase)}")
  let back = track(Delivered(day: 8), event: CameBack(reason: Damaged, day: 12))
  @console.print("{report(vase.order, change: back)}; refund due: {refund_due(back.after)}")

example "a heavy parcel abroad pays the zone and the weight"
  do postage(Parcel(order: "A-1003", grams: 2500, zone: Abroad))
  expect result == 1600

example "a pickup moves a packed parcel into transit"
  do apply(Packed, event: PickedUp(carrier: Post, tracking: "PO-1"))
  expect result is InTransit

example "a second pickup scan changes nothing"
  do track(InTransit(carrier: Post, tracking: "PO-1"), event: PickedUp(carrier: Post, tracking: "PO-1"))
  expect not changed(result)

example "a parcel cannot come back before it was delivered"
  do apply(Packed, event: CameBack(reason: Damaged, day: 2))
  expect result is Packed

example "a refused parcel is not refunded"
  do refund_due(Returned(reason: Refused, day: 5))
  expect result == false
```

## 4.7 Testing it

### Values typed in place

Kinds make tests short. Each example builds the values it needs, in one line, and checks one fact. There is no setup and no fake object: `Packed` and `Returned(reason: Refused, day: 5)` are values you type.

```una include="day-to-day/src/tracking.una#L110-L128" title="day-to-day/src/tracking.una" caption="the examples"
example "a heavy parcel abroad pays the zone and the weight"
  do postage(Parcel(order: "A-1003", grams: 2500, zone: Abroad))
  expect result == 1600

example "a pickup moves a packed parcel into transit"
  do apply(Packed, event: PickedUp(carrier: Post, tracking: "PO-1"))
  expect result is InTransit

example "a second pickup scan changes nothing"
  do track(InTransit(carrier: Post, tracking: "PO-1"), event: PickedUp(carrier: Post, tracking: "PO-1"))
  expect not changed(result)

example "a parcel cannot come back before it was delivered"
  do apply(Packed, event: CameBack(reason: Damaged, day: 2))
  expect result is Packed

example "a refused parcel is not refunded"
  do refund_due(Returned(reason: Refused, day: 5))
  expect result == false
```

> [!TIP]
> An `example` is a test that lives next to the code ([chapter 1](/learn/hello/#s1-6)). `do` calls the code under test, `result` is what that call returned, and each `expect` line states something that must hold. `una test .` runs every example and reports each one. [Chapter 10, Testing](/learn/testing/), covers examples in full.

### Variants, and the edges the run does not reach

`expect result is InTransit` checks the variant without its fields, which is all that example is about. `expect not changed(result)` calls a function of the program on the result: any `Bool` expression works. The examples cover the edges that the run in `main` does not reach: a heavy parcel abroad, a return before a delivery, and a refused parcel. Each one names its case in plain words, so the list of examples reads as the rules of the tracker.

### One example per rule that an `else` decides

An arm per variant is checked by the checker: forget one, and the program does not check. An `else` is not: whatever it answers, it checks. So the rules that an `else` decides deserve examples of their own. "a refused parcel is not refunded" tests the one arm of `refund_due`, and "a parcel cannot come back before it was delivered" tests the `else status` of `apply`.

### Running the examples

`una test .` prints:

```text include="day-to-day/expected/commands/test.txt#L2-L8"
example tracking "a heavy parcel abroad pays the zone and the weight" ... ok
example tracking "a pickup moves a packed parcel into transit" ... ok
example tracking "a second pickup scan changes nothing" ... ok
example tracking "a parcel cannot come back before it was delivered" ... ok
example tracking "a refused parcel is not refunded" ... ok

5 examples: 5 passed, 0 failed
```

### When an example fails

When an example fails, `una test .` names it and shows the value `result` had, as [Exercise 1](#exercise-1-a-lost-parcel) shows. Because every value prints as you would build it, the failure message is a value you can paste into a new example.

## 4.8 Common mistakes

Each mistake below is a small change to `day-to-day/src/tracking.una`, followed by what `una check .` reports.

### Leaving out a field (U2009)

:::mistake
Build the lamp's `Parcel` without its zone:

```diff include="day-to-day..mistakes/1:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -96,3 +96,3 @@
 =
-  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
+  let lamp = Parcel(order: "A-1001", grams: 1200)
   @console.print("{lamp.order}: postage {postage(lamp)}")
```

```text include="mistakes/1/expected/rendered.txt#L1-L6"
[U2009] Error: `Parcel` is missing field `zone`
    ╭─[ src/tracking.una:97:14 ]
    │
 97 │   let lamp = Parcel(order: "A-1001", grams: 1200)
    │              ───┬──
    │                 ╰──── `Parcel` is missing field `zone`
```

*Why:* every field gets a value when a record is built. There are no defaults, so a parcel without a zone cannot exist. The mark points at the kind's name, `Parcel`, the constructor that lacks a field, and the message names the field.

*Fix:* give the field, `zone: National`. When you add a field to a kind, this error appears at every place that builds it, which is the list of places to update. See [U2009](/docs/errors/U2009/).
:::

### A `when` that misses a variant (U2007)

:::mistake
Remove the `Returned` arm from `describe`:

```diff include="day-to-day..mistakes/2:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -67,3 +67,2 @@
     is Delivered(day) -> "delivered on day {day}"
-    is Returned(reason, day) -> "returned on day {day}, {reason_text(reason)}"
 
```

```text include="mistakes/2/expected/rendered.txt#L1-L8"
[U2007] Error: `when` does not match variant `Returned` of `Status`
    ╭─[ src/tracking.una:64:3 ]
    │
 64 │   when status
    │   ──┬─
    │     ╰─── `when` does not match variant `Returned` of `Status`
    │
    │ Help: repair 1: add an arm for each missing variant, such as `is Returned`, or an `else` arm
```

*Why:* a `when` over a sum covers every variant. The mark is on the `when` itself, since the problem is an arm that is not there, and the message names the missing variant and its kind. This is the same error you get after adding a variant to `Status`, at every `when` that needs an arm for it.

*Fix:* add the arm. Add `else` only when every remaining variant really gets the same answer. See [U2007](/docs/errors/U2007/).
:::

### A text where a variant goes (U2001)

:::mistake
Give the zone as a text:

```diff include="day-to-day..mistakes/3:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -104,3 +104,3 @@
   @console.print(report(lamp.order, change: arrived))
-  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad)
+  let vase = Parcel(order: "A-1002", grams: 300, zone: "Abroad")
   @console.print("{vase.order}: postage {postage(vase)}")
```

```text include="mistakes/3/expected/rendered.txt#L1-L6"
[U2001] Error: field `zone` of `Parcel` must be `Zone`, found `Text`
     ╭─[ src/tracking.una:105:56 ]
     │
 105 │   let vase = Parcel(order: "A-1002", grams: 300, zone: "Abroad")
     │                                                        ────┬───
     │                                                            ╰───── field `zone` of `Parcel` must be `Zone`, found `Text`
```

*Why:* `Zone` is a kind of its own, and `"Abroad"` is a `Text`. The message names the field, the type it needs and the type it found. The checker never turns one into the other, so a typo such as `"Abraod"` cannot become a new zone.

*Fix:* the variant, `zone: Abroad`, without quotes. See [U2001](/docs/errors/U2001/).
:::

### Ranges that leave a gap (U5001)

:::mistake
Replace the `else` of `weight_cents` with a last band:

```diff include="day-to-day..mistakes/4:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -43,3 +43,3 @@
     in 501..2000 -> 150
-    else -> 400
+    in 2001..30000 -> 400
 
```

```text include="mistakes/4/expected/rendered.txt#L1,L8,L12"
[U5001] Error: exhaustiveness of this `when`, `grams in 0..500 or grams in 501..2000 or grams in 2001..30000`, is refuted
    │ Help: repair 1: add an `else` arm, or arms for the values the others miss
    │ Note 2: counterexample: grams = -1
```

*Why:* without an `else`, the verifier must prove that the ranges cover every `Int`, and the first line quotes what it tried to prove. `Note 2` is the counterexample: no arm matches `grams = -1`, nor anything above 30,000. An `Int` can be any whole number, negative ones included.

*Fix:* end with an `else` arm, as the help says. To rule out negative weights for good, give the field a refined kind, as [chapter 7](/learn/contracts/#s7-3) shows. See [U5001](/docs/errors/U5001/).
:::

### Comparing with a variant that has fields (U2009)

:::mistake
Test the status with `==` in `apply`:

```diff include="day-to-day..mistakes/5:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -51,3 +51,3 @@
     is PickedUp(carrier, tracking) -> if status is Packed then InTransit(carrier, tracking) else status
-    is DeliveredOn(day) -> if status is InTransit then Delivered(day) else status
+    is DeliveredOn(day) -> if status == InTransit then Delivered(day) else status
     is CameBack(reason, day) -> if status is Delivered then Returned(reason, day) else status
```

```text include="mistakes/5/expected/rendered.txt#L1,L8"
[U2009] Error: variant `InTransit` needs its fields: `carrier`, `tracking`
    │ Help: repair 1: write `status is InTransit`; edit src/tracking.una:52:31..52:50 to "status is InTransit"
```

*Why:* `InTransit` on its own is not a value: it needs a carrier and a tracking number. `==` compares two whole values, so it has nothing to compare `status` with. This one comes from other languages, where comparing a status with a name is the usual test.

*Fix:* `status is InTransit`, which tests the variant only. The help line holds the exact edit, and `una fix .` applies it. See [U2009](/docs/errors/U2009/).
:::

### Comparing values of a type parameter without `Eq` (U2026)

:::mistake
Leave the constraint out of `changed`:

```diff include="day-to-day..mistakes/6:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -58,3 +58,3 @@
 --- Whether something changed. Any type whose values can be compared will do.
-pub changed[T: Eq](change: Change[T]) -> Bool = change.before != change.after
+pub changed[T](change: Change[T]) -> Bool = change.before != change.after
 
```

```text include="mistakes/6/expected/rendered.txt#L1,L8"
[U2026] Error: equality on values of the type parameter `T` needs the constraint `Eq`; write `[T: Eq]`
    │ Help: repair 1: constrain `T` by `Eq`; edit src/tracking.una:59:13..59:14 to "T: Eq"
```

*Why:* a generic function knows only what its constraints say about `T`, and `!=` needs `Eq`. `changed` is `pub`, so nothing is inferred for it: its header must say what it needs.

*Fix:* `[T: Eq]`, which the help's edit writes and `una fix .` applies. See [U2026](/docs/errors/U2026/).
:::

### A field without its label (U2004)

:::mistake
Build the lamp's parcel with its order number first and unlabeled, as a function call allows:

```diff include="day-to-day..mistakes/7:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -96,3 +96,3 @@
 =
-  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
+  let lamp = Parcel("A-1001", grams: 1200, zone: National)
   @console.print("{lamp.order}: postage {postage(lamp)}")
```

```text include="mistakes/7/expected/rendered.txt#L1,L8"
[U2004] Error: `Parcel` has 3 fields, so every argument needs its field's label
    │ Help: repair 1: label it `order`; edit src/tracking.una:97:21..97:29 to "order: \"A-1001\""
```

*Why:* a call may leave the label of its first argument out, so the habit carries over. A record or variant with two or more fields labels every one, the first too, so a value reads the same wherever it is built.

*Fix:* `order: "A-1001"`, which the help's edit writes and `una fix .` applies. See [U2004](/docs/errors/U2004/).
:::

## 4.9 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added, and a stub of what to write when there is one. `una check .` or `una test .` fails there until the exercise is done. Work in small steps: make one change, run `una check .`, and read what it reports before the next change. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

### Exercise 1: a lost parcel

::::exercise
Sometimes a carrier loses a parcel. Add a variant `Lost(day: Int)` to `Status`, describe it as "lost since day N", and make it owed a refund. The start package ends with these examples, and `una check .` reports U1001 until the variant exists:

```una include="exercises/1/start/src/tracking.una#L130-L136" title="exercises/1/start/src/tracking.una"
example "a lost parcel says since when"
  do describe(Lost(day: 20))
  expect result == "lost since day 20"

example "a lost parcel is refunded"
  do refund_due(Lost(day: 20))
  expect result == true
```

:::hint
*Hint:* work in three steps. First add the variant at the end of `Status`, after a `|`, and run `una check .`: the checker shows the one `when` that needs a new arm. Then add that arm to `describe`, binding `day`. Last, run `una test .`: the other `when` over `Status` has an `else`, so it checks, and only the second example tells you that it answers wrongly.
:::

What `una check .` reports after adding only the variant:

```text include="exercises/1/variant/expected/rendered.txt#L1,L8"
[U2007] Error: `when` does not match variant `Lost` of `Status`
    │ Help: repair 1: add an arm for each missing variant, such as `is Lost`, or an `else` arm
```

With the variant and an arm in `describe`, `una check .` is clean, and `una test .` shows what the `else` of `refund_due` answers:

```text include="exercises/1/described/expected/commands/test.txt#L8-L12"
example tracking "a lost parcel is refunded" ... FAILED
  src/tracking.una:137: expect result == true
  it is false, with `result` = `false`

7 examples: 6 passed, 1 failed
```

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/1/answer`).
Add the variant, and an arm in each `when` over `Status`:

```diff include="exercises/1/start..exercises/1/answer:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -18,3 +18,3 @@
 --- Where a shipment is. Each state carries what is known in that state, and nothing else.
-pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int)
+pub kind Status = Packed | InTransit(carrier: Carrier, tracking: Text) | Delivered(day: Int) | Returned(reason: ReturnReason, day: Int) | Lost(day: Int)
 
@@ -68,2 +68,3 @@
     is Returned(reason, day) -> "returned on day {day}, {reason_text(reason)}"
+    is Lost(day) -> "lost since day {day}"
 
@@ -88,2 +89,3 @@
     is Returned(reason) -> reason != Refused
+    is Lost -> true
     else -> false
```

The `else` of `refund_due` would have answered `false` for a lost parcel. This is the cost of an `else` on a sum that grows: the checker cannot tell you that a new variant needs a different answer.
:::
::::

### Exercise 2: express shipping

::::exercise
The store offers express shipping for 5.00 more. Add a field `express: Bool` to `Parcel`, and add 500 cents to the postage of an express parcel. The start package ends with this example, and `una check .` reports U2009 until the field exists:

```una include="exercises/2/start/src/tracking.una#L130-L132" title="exercises/2/start/src/tracking.una"
example "express adds 5.00 to the postage"
  do postage(Parcel(order: "A-1004", grams: 300, zone: Local, express: true))
  expect result == 800
```

:::hint
*Hint:* add the field as a fourth line under `kind Parcel`, then run `una check .`: every place that builds a `Parcel` is reported, since each must now say whether it is express. Give each one `express: false` or `express: true`. Then change `postage`: an `if … then … else` in parentheses can be one term of an addition; without the parentheses it is U0101.
:::

Check your answer with `una test .`, and `una run .` to see the new postage of the vase, if you send it express.

:::answer Answer (*check, run, test*; `exercises/2/answer`).
Add the field, use it in `postage`, and give it in every `Parcel`:

```diff include="exercises/2/start..exercises/2/answer:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -10,2 +10,3 @@
   zone: Zone
+  express: Bool
 
@@ -29,3 +30,3 @@
 --- Postage in cents: a price for the zone, and a supplement for the weight.
-pub postage(parcel: Parcel) -> Int = zone_cents(parcel.zone) + weight_cents(parcel.grams)
+pub postage(parcel: Parcel) -> Int = zone_cents(parcel.zone) + weight_cents(parcel.grams) + (if parcel.express then 500 else 0)
 
@@ -96,3 +97,3 @@
 =
-  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National)
+  let lamp = Parcel(order: "A-1001", grams: 1200, zone: National, express: false)
   @console.print("{lamp.order}: postage {postage(lamp)}")
@@ -104,3 +105,3 @@
   @console.print(report(lamp.order, change: arrived))
-  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad)
+  let vase = Parcel(order: "A-1002", grams: 300, zone: Abroad, express: true)
   @console.print("{vase.order}: postage {postage(vase)}")
@@ -110,3 +111,3 @@
 example "a heavy parcel abroad pays the zone and the weight"
-  do postage(Parcel(order: "A-1003", grams: 2500, zone: Abroad))
+  do postage(Parcel(order: "A-1003", grams: 2500, zone: Abroad, express: false))
   expect result == 1600
```

The answer sends the vase express, so `una run .` prints `A-1002: postage 1700`.
:::
::::

### Exercise 3: the next action

::::exercise
Design a kind. For each status, the store does one thing next: wait while a parcel is packed, send the tracking number to the customer while it is in transit, ask for a review once it is delivered, refund a parcel returned damaged or wrong, and put a refused parcel back on the shelf. The start package has a placeholder kind, `Action`, a stub for `next_action`, and these examples, which report U1001 until the kind has the variants they name:

```una include="exercises/3/start/src/tracking.una#L136-L150" title="exercises/3/start/src/tracking.una"
example "a parcel in transit sends its tracking number"
  do next_action(InTransit(carrier: Post, tracking: "PO-7"))
  expect result == SendTracking(tracking: "PO-7")

example "a damaged parcel is refunded"
  do next_action(Returned(reason: Damaged, day: 4))
  expect result == Refund

example "a refused parcel goes back on the shelf"
  do next_action(Returned(reason: Refused, day: 4))
  expect result == Restock

example "a delivered parcel asks for a review"
  do next_action(Delivered(day: 3))
  expect result == AskForReview
```

:::hint
*Hint:* read the examples first: they name the variants, `SendTracking`, `Refund`, `Restock` and `AskForReview`, and the placeholder has `Wait`. Only one action carries data, so only one variant has a field. In `next_action`, write one arm per status; the `Returned` arm binds `reason` and compares it with `==`, which works on a variant without fields. A `when` inside an arm starts on its own line, below the `->`.
:::

Check your answer with `una test .`.

:::answer Answer (*check, run, test*; `exercises/3/answer`).
Declare the actions, and choose one for each status:

```diff include="exercises/3/start..exercises/3/answer:src/tracking.una" context="1" title="src/tracking.una"
--- a/src/tracking.una
+++ b/src/tracking.una
@@ -93,7 +93,13 @@
 
---- What the store does next about a shipment. Exercise 3: declare it as a sum kind.
-pub kind Action = | Wait
+--- What the store does next about a shipment.
+pub kind Action = Wait | SendTracking(tracking: Text) | AskForReview | Refund | Restock
 
---- The next action for a status. Exercise 3: one action for each case.
-pub next_action(status: Status) -> Action = Wait
+--- The next action for a status.
+pub next_action(status: Status) -> Action
+=
+  when status
+    is Packed -> Wait
+    is InTransit(tracking) -> SendTracking(tracking)
+    is Delivered -> AskForReview
+    is Returned(reason) -> if reason == Refused then Restock else Refund
 
```

`is InTransit(tracking)` binds one of the two fields of `InTransit` by its name, and `SendTracking(tracking)` passes it on, unlabeled since that variant has one field. The `Returned` arm chooses with an `if`, since only one reason differs.
:::
::::

## 4.10 Recap and reference

### For agents

:::agents
`una --json check .` gives every diagnostic as JSON. For [A `when` that misses a variant](#a-when-that-misses-a-variant-u2007):

```json include="mistakes/2/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U2007","severity":"error","domain":"types","message":"`when` does not match variant `Returned` of `Status`","primary":{"file":"src/tracking.una","start":{"line":64,"col":3},"end":{"line":64,"col":7}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"add an arm for each missing variant, such as `is Returned`, or an `else` arm","edit":null}],"explain":"una explain U2007"}],"fixable":0}
```

U2007 carries no `edit`, since only the author knows what a new arm should do. U2004, U2026 and the `==` form of U2009 carry exact edits, which `una fix .` applies. The compact rule: *records label every field and are nominal; a sum of one variant starts with `|`; `when` covers every variant or ends with `else`, which comes last; test a variant with `is`, not `==`; a generic function writes `[T: Eq]`, `[T: Ord]` or `[T: Integer]` for what it does with `T`; a recursive kind has a variant that ends.*
:::

### Recap

:::recap
- Declare a record for parts that are all there at once; build it with every field labeled, and read it with a dot.
- Records are nominal: the same fields do not make the same kind. An alias is only another name.
- Declare a sum for a value of several cases, each variant with only its own fields. A sum of one variant starts with `|`.
- Test a variant with `is`; `==` compares whole values, and only sums without fields have an order.
- `when` covers every variant; prefer an arm per variant to `else` on a sum that will grow, and put `else` last.
- Range and literal arms end with `else`, unless they cover every value.
- A generic function writes the weakest constraint its body needs: `Eq`, `Ord` or `Integer`.
- A recursive kind needs a variant that does not contain it.
:::

### Reference

:::reference
- Construct pages: [`kind`](/docs/language/types/kind/), [`when`](/docs/language/control-flow/when/), [constraints on generics](/docs/language/types/constraints/), [`example`](/docs/language/examples/example/)
- Prelude: [`Option`](/docs/std/)
- Commands: [`una contract`](/docs/cli/contract/), [`una fix`](/docs/cli/fix/)
- Diagnostics: [U0101](/docs/errors/U0101/), [U1001](/docs/errors/U1001/), [U1002](/docs/errors/U1002/), [U2001](/docs/errors/U2001/), [U2002](/docs/errors/U2002/), [U2004](/docs/errors/U2004/), [U2007](/docs/errors/U2007/), [U2008](/docs/errors/U2008/), [U2009](/docs/errors/U2009/), [U2019](/docs/errors/U2019/), [U2025](/docs/errors/U2025/), [U2026](/docs/errors/U2026/), [U2027](/docs/errors/U2027/), [U5001](/docs/errors/U5001/), [U6003](/docs/errors/U6003/), [U7001](/docs/errors/U7001/)
- Specification: [types](/docs/spec/03-types/), [grammar](/docs/spec/02-grammar/), [functions and contracts](/docs/spec/04-functions-and-contracts/), [static semantics](/docs/spec/10-static-semantics/), [constraints on generics](/docs/spec/20-constraints-on-generics/), [canonical form](/docs/spec/15-canonical-form/), [verification](/docs/spec/12-verification/)
:::
