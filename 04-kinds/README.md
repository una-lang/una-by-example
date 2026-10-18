---
learn: "4"
title: Kinds
editions: ["0.2"]
codes: [U1001, U1002, U2001, U2009, U2025]
time: 30
builds: A parcel pricer built from records, sum kinds and generic kinds
prerequisites: ["2", "3"]
template: 2
nav: ["Records", "Sum kinds and is", "Taking a sum apart: when", "Generic kinds and constraints"]
---

# 4 Kinds


A working program is mostly about the shape of its data: a parcel has an order number, a weight and a zone; a shipment is packed, in transit, delivered or returned, and each of those states knows different things. In Una you declare that shape as a kind: a record of named fields, or a sum of variants. The checker then holds every function to it. A field cannot be forgotten, a state cannot carry data it does not have, and a `when` that misses a state does not check. This chapter declares the kinds of a shipment tracker for a small store.

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

A **type** is a set of values, together with what you may do with them. You met the built-in ones in [chapter 2](/learn/numbers/): `Int` is the set of whole numbers, and you may add them; `Text` is the set of texts, and you may cut them; `Bool` is the set of two values, `true` and `false`. Every value in Una has a type, and the checker uses the types to refuse a program that, say, adds a text to a number.

The built-in types describe single values. A store's data is made of several values that belong together: a parcel has an order number, a weight and an address, and an address has a name, a street and a city. A **kind** is a type that you declare yourself, with the keyword `kind`, to describe such data. Una has four forms of kind, and this chapter teaches three of them:

- A **record** groups several named values that are all there at once. This section.
- A **sum** is one of several cases. [Section 4.2](#s4-2).
- An **alias** gives an existing type another name. [Aliases](#aliases-another-name-for-a-type), in this section.

The fourth form, a kind with a condition such as "never negative", is in [chapter 5](/learn/contracts/#s5-3).

Think of a record as a printed form, such as a shipping label with its boxes: "order", "weight", "name", "street", "city". The kind is the blank form. Each value of the kind is one filled-in copy, with something written in every box.

### Each step is a package

Each step of this chapter is a package, as in [chapter 1, Hello, Una](/learn/hello/#s1-1): a directory with `una.toml`, `verification.lock` and the module under `src/`. The manifest names the package and the module that `una run` starts:

```toml include="steps/01-records/una.toml" title="steps/01-records/una.toml"
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

```una include="steps/02-loose/src/slips.una" title="steps/02-loose/src/slips.una" verified="check, run"
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

```text include="steps/02-loose/expected/output.txt"
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

```una include="steps/01-records/src/labels.una#Address" title="steps/01-records/src/labels.una"
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

A field's type can be any type: `Int`, `Text`, `Bool`, a list of values ([chapter 10](/learn/collections/#s10-1)), or another kind.

#### Building a value

To make a value of a record kind, write the kind's name like a call, and give every field, each with its field's name as a label: `Address(name: "Corner Bakery", street: "12 Elm Road", city: "Northfield")`. Written this way, the kind's name is the **constructor**, the function that builds a value of the kind. The labels work like the labels of a call ([chapter 6](/learn/functions/#s6-1)), with one difference: a record of two or more fields labels every field, the first one too.

A record of one field may leave out the label. `Note("fragile")` builds the record `Note` of the step below, whose one field is `text`.

#### Reading a field with a dot

`parcel.grams` reads the field `grams` of the value `parcel`. When the field is itself a record, the dots go on: `parcel.address.city` is the city of the parcel's address.

#### A field whose kind is a record

A field can hold a whole record. `Parcel` has a field `address` of kind `Address`, so each parcel holds an address with its three fields. The checker knows the kind of every field, so `parcel.address.city` is a `Text`, and `parcel.address.grams` does not check.

### An address inside a parcel

The module `labels` declares two record kinds, builds a parcel, and redirects it:

:::steps
```una include="steps/01-records/src/labels.una" title="steps/01-records/src/labels.una" verified="check, run"
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

```text include="steps/01-records/expected/output.txt"
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

A value of a record has a value in every field. There are no default values and no empty fields: build a `Parcel` without its zone, and the checker reports U2009, "`Parcel` is missing field `zone`" ([Leaving out a field](/learn/choices/#leaving-out-a-field-u2009) shows it whole). A field the kind does not declare is U2009 too, with "`Address` has no field `zip`", and so is reading one with a dot: `home.street` on a kind without `street` is U1001.

#### A value never changes; a binding can take a new one

A record value, once built, never changes. `redirect` shows the way to get a different parcel: build a new one. When you hold a record in an editable binding, a `let edit` ([chapter 2](/learn/numbers/#s2-1)), you may also assign one of its fields, as `box.grams = 1500` does in `main`. The assignment gives the binding `box` a new record, with 1500 in `grams` and the other fields as they were. `packed`, which took the box's value before the assignment, keeps the old one: the first line of the output still says 1200 grams. An assignment can reach a field of a field, as `box.note.text = "this side up"` does. It needs a `let edit`: on a plain `let`, `home.city = "Southport"` is U2019, "`home` is not editable".

#### Equality, and how a record prints

`==` compares two records field by field: two records are equal when every field is equal. `packed == box` is `false`, since their weights and notes differ. Interpolation writes a record as you would build it, with its kind's name and every field labeled, and a record of one field without its label, as `Note("fragile")` shows. Interpolating a record, a variant or an `Option` needs edition 0.2 or later; in edition 0.1 it is U2001, "interpolation converts `Int`, `Bool` and `Text` to text".

#### Records are nominal

Records are **nominal**: two kinds with the same fields are two different types, because a kind is known by its name. Declare a `Warehouse` with the same three fields as `Address`, and pass one where the parcel needs an address:

```diff include="steps/01-records..steps/04-nominal:src/labels.una" title="src/labels.una" context="0"
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

An alias documents what a field holds: `sku: Sku` says more than `sku: Text`. It does not keep two kinds apart the way a record does: a `Sku` and a customer's name are both `Text`, and the checker lets one go where the other goes. [Chapter 7, Contracts and the verifier](/learn/contracts/#s5-3), adds a condition to an alias, as in `kind Cents = Int where it >= 0`, and the verifier proves it.

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

## 4.2 Sum kinds, and `is`


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

A sum with a single variant starts with `|`. Without it, `kind QuoteError = NoCarrier` would be an alias of a type named `NoCarrier` ([A sum of one variant without its bar](#a-sum-of-one-variant-without-its-bar) shows what the checker says). Sums of one variant are common for failures, which [chapter 7](/learn/failure/) declares.

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

**Variant names are unique in a module.** The two marks show the two places: `AtDoor` is first a variant of `Delivery`, on line 7, and then of `Packing`, on line 10. A variant's name is a value, so `AtDoor` must mean one thing in the module. Rename one of them.

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

## 4.3 Taking a sum apart: `when`


### What `when` is

`when` chooses what to do by the variant of a value. Think of a sorting table in a warehouse, with one bin for each kind of delivery. Each parcel goes into the bin that matches its label, and each bin has its own instructions. `when` is that table:

- The **subject** is the value after `when`: the parcel on the table.
- An **arm** is one line under it: one bin, with its instructions.
- The **pattern** is the start of an arm, such as `is AtLocker(locker)`: what the arm matches.
- After `->` comes the arm's value: what the `when` gives when that arm matches.

`when` is an expression, as `if` is ([chapter 3](/learn/text-and-conditions/#s3-4)): it gives the value of the arm that matched, so it can be a function's body or the value of a `let`.

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

`in 1..<10` matches a whole number from 1 up to 10, 10 left out, and `in 10..49` one from 10 to 49, both ends included. The two forms of range are those of [chapter 9](/learn/loops/#s9-1): `..` includes its end, and `..<` leaves it out.

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

When an arm needs more than one line, write nothing after `->`, and put the arm's lines under it, indented two more spaces. The lines are a block, as a function's body is ([chapter 6](/learn/functions/#s6-2)): `let` lines first, and the block's value is its last line.

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

```una include="steps/12-no-generics/src/edits.una" title="steps/12-no-generics/src/edits.una" verified="check, run"
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

```text include="steps/12-no-generics/expected/output.txt"
PriceChange(before: 1790, after: 1990)
NameChange(before: "Reading lamp", after: "Desk lamp")
```

It works, and it is the same declaration twice and the same function twice, with only the type changed. A change of zones would need a third copy of each. A fix to one copy must be made in all of them, and the copies drift apart over time. A generic kind is written once, and works for every type.

### How to write a generic kind

```una include="steps/13-generic-forms/src/forms.una#Change" title="steps/13-generic-forms/src/forms.una"
--- A value before and after an edit. `T` is the type of both.
kind Change[T]
  before: T
  after: T
```

The type parameter goes in brackets after the kind's name. Inside the declaration, `T` stands for whatever type the kind is used with, as a field type or as part of one. Both fields have the type `T`, so the two values of one change always have the same type.

The step of this part declares three generic kinds and uses each:

```una include="steps/13-generic-forms/src/forms.una" title="steps/13-generic-forms/src/forms.una" verified="check, run"
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

```text include="steps/13-generic-forms/expected/output.txt"
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

A sum can take a type parameter too. The prelude's `Option[T]`, a value that may be missing, is one: `Some(value)` holds a `T`, and `None` holds nothing. `Some("LAMP-01")` is an `Option[Text]`, as the last line of the output shows. [Chapter 5, Collections](/learn/failure/#s7-1), uses it everywhere.

### Generic functions and their constraints

A function can take type parameters too, written in brackets after its name: `undo[T](change: Change[T]) -> Change[T]` works on a change of any type. Inside it, `T` is a type the function knows nothing about. It can move values of `T` around, put them in fields, and return them, but not compare them, since some types cannot be compared.

A **constraint** says what the function needs from `T`, and in exchange limits the types it accepts. It is written after the parameter, with a colon: `changed[T: Eq]`. Una has three, each including the one before. The **fixed-width integers** in the table are the types such as `U8` and `I32` of [section 2.3](/learn/numbers/#s2-3), and `x.to_int()` turns one into an `Int`:

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
```una include="steps/14-generics/src/changes.una" title="steps/14-generics/src/changes.una" verified="check, run"
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

```text include="steps/14-generics/expected/output.txt#L1-L3"
Change(before: 1790, after: 1990)
price changed: true, name changed: false
larger price 1990, farther zone Abroad
```

### How generics behave

#### One type per parameter, in every field

A type parameter stands for one type in each value. Build a `Change` with a text before and a number after:

```diff include="steps/13-generic-forms..steps/15-mixed-change:src/forms.una" title="src/forms.una" context="0"
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

In a function that writes no constraint, `==` on values of `T` is U2026, with a repair that writes the constraint: "equality on values of the type parameter `T` needs the constraint `Eq`; write `[T: Eq]`". [Comparing values of a type parameter without `Eq`](/learn/choices/#comparing-values-of-a-type-parameter-without-eq-u2026) shows it. Arithmetic is never defined on `T`, with a constraint or without: `a + b` on two values of a `T: Integer` does not check. Turn them into `Int` with `to_int()`, and add those.

#### A call passes a type that satisfies it

At each call, the type argument must satisfy the constraint. Pass `larger` a change of shelves, a record:

```diff include="steps/14-generics..steps/16-constraint-rules:src/changes.una" title="src/changes.una" context="0"
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

```text include="steps/16-constraint-rules/expected/rendered.txt#L1-L6"
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

A private function may leave its constraint out, and the checker infers the least one its body needs, as it infers a private function's `uses` ([chapter 6](/learn/functions/#s6-3)). `differs`, in the step of [How to write a generic kind](#how-to-write-a-generic-kind), compares with `!=` and writes no constraint. `una contract` shows what the checker inferred:

```sh
una contract forms.differs
```

```text include="steps/13-generic-forms/expected/commands/contract.txt#L3"
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

```una include="steps/14-generics/src/changes.una#L28-L29" title="steps/14-generics/src/changes.una"
  let label = Change(before: "desk lamp", after: "Desk lamp")
  @console.print("{changed(label)} {larger(label)}")
```

Does `changed(label)` say `true` or `false`, and which name does `larger(label)` give?

:::answer Show the answer
```text include="steps/14-generics/expected/output.txt#L4"
true desk lamp
```

`"desk lamp"` and `"Desk lamp"` are different texts, since `==` compares character by character, so the change counts. `Text` is ordered character by character too, by each character's number in Unicode, where every capital letter comes before every small one. `d` comes after `D`, so `"desk lamp"` is the larger.
:::
