---
learn: "4"
title: Kinds
editions: ["0.2"]
codes: [U1001, U2001, U2004, U2007, U2009, U2026, U5001]
time: 35
builds: A shipment tracker that prices parcels and follows each one from packing to delivery or return
prerequisites: ["2", "3"]
template: 2
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
- test a program built from kinds with examples.
:::

## Why it works this way

Many programs describe a shipment with one object and a string: `status = "in_transit"`, with a `tracking` field that is null unless the status says otherwise, and a `delivered_on` field that is null in three states out of four. Nothing stops a value that is "delivered" with no date, or "packed" with a tracking number. A typo in `"in_trnasit"` is a new status. When a new status is added, every `switch` with a `default` branch keeps compiling, and quietly does the wrong thing.

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

### Fields, labels and the dot

A record kind declares a type of named fields, one per line, indented under its name. Each field has a type, and the types can be other kinds. You build a value by naming the kind and giving every field, with its label, and you read a field with a dot.

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
5. **`"{home}"`.** Interpolation writes a record in the form you would type in Una, with its kind's name and every field.
:::

`una run .` prints:

```text include="steps/01-records/expected/output.txt"
Corner Bakery, Northfield, 1200 g
Corner Bakery, Southport, 1200 g
Address(name: "Corner Bakery", street: "12 Elm Road", city: "Northfield")
```

### Records are nominal

Records are **nominal**: two kinds with the same fields are two different types. If you declare `kind Warehouse` with a `name`, a `street` and a `city`, a `Warehouse` still cannot be passed where an `Address` is expected. The name of a kind is part of what it means, so the checker keeps a warehouse's address apart from a customer's.

### Aliases: another name for a type

A kind can also be another name for a type: `kind Sku = Text` is an **alias**, and a `Sku` is a `Text` wherever one is expected. An alias documents a field, but does not keep two kinds apart the way a record does. [Chapter 7, Contracts and the verifier](/learn/contracts/), adds a condition to an alias, as in `kind Cents = Int where it >= 0`, and proves it.

## 4.2 Sum kinds

### One of several cases

A sum kind lists its variants, separated by `|`. A value is exactly one of them. A variant may carry fields, written in parentheses, and different variants carry different fields. Use a sum whenever a value is one of several cases that a program treats differently: a delivery to the door, to a locker, or to a store.

### Zones and deliveries

The module `carriers` declares three sum kinds, then builds, tests and compares their variants:

:::steps
```una include="steps/02-sums/src/carriers.una" title="steps/02-sums/src/carriers.una" verified="check, run"
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
```

1. **`kind Zone = Local | National | Abroad`.** Three variants with no fields. Each is a value of its own: `Local` is a `Zone`.
2. **`kind Delivery = AtDoor | AtLocker(locker: Text) | AtStore(store: Text, opens: Int)`.** Variants with fields. Only a locker delivery has a locker, and only a store delivery has an opening hour. A value such as "at the door, locker 14" cannot be built.
3. **`kind QuoteError = | NoCarrier`.** A sum with one variant starts with a bar. Without it, `kind QuoteError = NoCarrier` would be an alias of a type named `NoCarrier`.
4. **`AtLocker(locker: "Station 14")`.** A variant with fields is built like a record. A variant with one field may leave out the label.
5. **`delivery is AtLocker`.** `is` tests which variant a value is, and gives a `Bool`. It does not need the fields.
6. **`Local < Abroad` and `National == National`.** Variants without fields are ordered as they are declared, so list them in an order that means something: here, nearest first. `==` compares any two values of the same kind.
:::

`una run .` prints:

```text include="steps/02-sums/expected/output.txt"
AtLocker("Station 14") AtStore(store: "Harbour Road", opens: 9) AtDoor
code needed: true false
Local before Abroad: true; same zone: true
NoCarrier
```

A variant with fields prints as you would build it: one field without its label, as `AtLocker("Station 14")`, and two or more with their labels.

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
:::

## 4.3 Taking a value apart: `when`

### Arms, bindings and the value of a `when`

`when` chooses an arm by the value it is given. Each arm starts with `is` and a variant, then `->` and the value of that arm. An arm can bind the fields of its variant, by name, and use them. The value of the `when` is the value of the arm that matched.

### Every variant has an arm

The checker makes sure that every variant has an arm. An `else` arm, last, covers every variant not named before it. Over an `Int` or a `Text`, arms name literals with `is`, or ranges with `in`, and these need an `else` unless the ranges cover every value.

> [!TIP]
> Prefer an arm per variant to `else` on a sum that will grow. Keep `else` for "every other case is the same", as `refund_due` does in the day-to-day program, and for literals and ranges.

### Postage by zone, weight and delivery

The module `postage` uses `when` over a sum, over ranges of an `Int`, and with arms that bind fields:

:::steps
```una include="steps/03-when/src/postage.una" title="steps/03-when/src/postage.una" verified="check, run"
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

```text include="steps/03-when/expected/output.txt"
600 cents
collect at Harbour Road from 9:00
collect at locker Station 14
```

### Range arms, a proof obligation

Range arms with no `else` are a proof obligation: the verifier must show that some arm matches every `Int`. When it cannot, it reports the value that no arm matches, a counterexample ([Ranges that leave a gap](#ranges-that-leave-a-gap-u5001), in Common mistakes). [Chapter 7](/learn/contracts/) explains what the verifier proves and how to read its counterexamples.

## 4.4 Generic kinds and constraints

### Generic kinds: `Change[T]`

Some kinds have the same shape whatever they hold. A change to a catalog entry has a value before and a value after, whether it is a price, a name or a zone. A **generic kind** takes a type parameter in brackets, `Change[T]`, and `Change[Int]` and `Change[Text]` are two types built from it. The type argument is inferred where a value is built.

### Constraints on a generic function: `Eq`, `Ord` and `Integer`

A generic function takes type parameters too. Without a constraint, it knows nothing about a `T` and can only move values around. A **constraint** gives it more: `Eq` allows `==` and `!=`, `Ord` also allows `<`, `<=`, `>` and `>=`, and `Integer` also allows `to_int()`.

### Undoing and comparing changes

The module `changes` declares `Change[T]` and three generic functions over it:

:::steps
```una include="steps/04-generics/src/changes.una" title="steps/04-generics/src/changes.una" verified="check, run"
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
```

1. **`kind Change[T]`.** A record with a type parameter. Both fields have the type `T`, so a change from a price to a name cannot be built.
2. **`undo[T]`.** No constraint is needed: `undo` only swaps the two values.
3. **`changed[T: Eq]`.** `!=` compares two values of `T`, so `T` must be `Eq`: every type whose values hold no functions is, and a record with a function field is not.
4. **`larger[T: Ord]`.** `>` needs an order, so `T` must be `Ord`: `Int`, `Text`, the fixed-width integers, and sums whose variants carry no fields. `Zone` qualifies, so `larger(zone)` gives the farther zone.
5. **`Change(before: 1990, after: 1790)`.** `T` is inferred as `Int` here, `Text` for `name` and `Zone` for `zone`.
:::

`una run .` prints:

```text include="steps/04-generics/expected/output.txt"
Change(before: 1790, after: 1990)
price changed: true, name changed: false
larger price 1990, farther zone Abroad
```

### The weakest constraint the body needs

Write the weakest constraint the body needs. `undo` needs none, so it works on a `Change` of any type. `changed` needs `Eq`, and `larger` needs `Ord`, which also gives `Eq`. A stronger constraint than the body uses only refuses callers for no reason. When a call passes a type that does not satisfy the constraint, such as a record to `larger`, the checker reports it at the call (U2025).

### Type parameters of kinds, and `Option`

A kind's type parameters take no constraint; only a function's do. The prelude's `Option[T]`, which holds a value or nothing, is a generic sum kind, and [chapter 5, Collections](/learn/collections/), uses it everywhere.

## 4.5 Day-to-day: shipment tracking

### What the program must do

Now the program from the start of the chapter. The store ships parcels by post or by courier. Each parcel has a price for its zone and its weight. Carriers report events: a pickup, a delivery, a parcel that came back. The tracker must keep each shipment's status, ignore an event that does not fit, such as a pickup scan sent twice, and say whether a returned parcel is owed a refund.

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

`Status` is the heart of the program. Each variant carries what is known in that state: a carrier and a tracking number while in transit, a day once delivered, a reason and a day once returned. `Event` is a second sum, for what the outside world reports, and its variants mirror the transitions. `Change[Status]` records a status before and after an event, so the report can tell an event that changed something from one that did not.

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

`una run .` prints the report shown in [What you'll build](#what-youll-build). The third line is the duplicate scan: the status stayed `InTransit`, and the report says so instead of pretending something happened. Nothing in `main` can build a delivered shipment without a day, or a shipment in transit without a tracking number, because `Status` has no such variant.

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

## 4.6 Testing it

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
> An `example` is a test that lives next to the code. `do` calls the code under test, `result` is what that call returned, and each `expect` line states something that must hold. `una test .` runs every example and reports each one. [Chapter 10, Testing](/learn/testing/), covers examples in full.

### Variants, and the edges the run does not reach

`expect result is InTransit` checks the variant without its fields, which is all that example is about. `expect not changed(result)` calls a function of the program on the result: any `Bool` expression works. The examples cover the edges that the run in `main` does not reach: a heavy parcel abroad, a return before a delivery, and a refused parcel. Each one names its case in plain words, so the list of examples reads as the rules of the tracker.

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

## 4.7 Common mistakes

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

```text include="mistakes/1/expected/rendered.txt#L1"
[U2009] Error: `Parcel` is missing field `zone`
```

*Why:* every field gets a value when a record is built. There are no defaults, so a parcel without a zone cannot exist.

*Fix:* give the field, `zone: National`.
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

```text include="mistakes/2/expected/rendered.txt#L1,L8"
[U2007] Error: `when` does not match variant `Returned` of `Status`
    │ Help: repair 1: add an arm for each missing variant, such as `is Returned`, or an `else` arm
```

*Why:* a `when` over a sum covers every variant. This is the same error you get after adding a variant to `Status`, at every `when` that needs an arm for it.

*Fix:* add the arm. Add `else` only when every remaining variant really gets the same answer.
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

```text include="mistakes/3/expected/rendered.txt#L1"
[U2001] Error: field `zone` of `Parcel` must be `Zone`, found `Text`
```

*Why:* `Zone` is a kind of its own, and `"Abroad"` is a `Text`. The checker never turns one into the other, so a typo such as `"Abraod"` cannot become a new zone.

*Fix:* the variant, `zone: Abroad`.
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

```text include="mistakes/4/expected/rendered.txt#L1,L12"
[U5001] Error: exhaustiveness of this `when`, `grams in 0..500 or grams in 501..2000 or grams in 2001..30000`, is refuted
    │ Note 2: counterexample: grams = -1
```

*Why:* no arm matches `grams = -1`, the counterexample the verifier found, nor anything above 30,000. An `Int` can be any whole number.

*Fix:* end with an `else` arm. To rule out negative weights for good, give the field a refined kind, as [chapter 7](/learn/contracts/) shows.
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

*Why:* `InTransit` on its own is not a value: it needs a carrier and a tracking number. `==` compares two whole values.

*Fix:* `status is InTransit`, which tests the variant only. `una fix .` applies the repair shown.
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

*Why:* a generic function knows only what its constraints say about `T`, and `!=` needs `Eq`.

*Fix:* `[T: Eq]`, which `una fix .` writes.
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

*Why:* a record or variant with two or more fields labels every one, so a value reads the same wherever it is built.

*Fix:* `order: "A-1001"`, which `una fix .` writes.
:::

## 4.8 Exercises

Each exercise starts from `exercises/N/start`: the day-to-day program with the exercise's examples added, and a stub of what to write when there is one. `una check .` or `una test .` fails there until the exercise is done. Run `una fmt .` before `una check .`: canonical form, for example, puts a body of one expression on the header line.

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
*Hint:* add the variant first and run `una check .`: the checker shows the one `when` that needs a new arm. The other `when` over `Status` has an `else`, so it checks, and only the second example tells you that it answers wrongly.
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
*Hint:* add the field, then run `una check .`: every place that builds a `Parcel` is reported, since each must now say whether it is express. An `if … then … else` in parentheses can be one term of an addition; without the parentheses it is U0101.
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
*Hint:* only one action carries data, so only one variant has a field. In `next_action`, one arm per status; the `Returned` arm binds `reason` and compares it with `==`, which works on a variant without fields. A `when` inside an arm starts on its own line, below the `->`.
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
:::
::::

## 4.9 Recap and reference

### For agents

:::agents
`una --json check .` gives every diagnostic as JSON. For [A `when` that misses a variant](#a-when-that-misses-a-variant-u2007):

```json include="mistakes/2/expected/commands/json.txt#L2"
{"schema":"una.diagnostics/1","diagnostics":[{"schema":"una.diagnostic/1","code":"U2007","severity":"error","domain":"types","message":"`when` does not match variant `Returned` of `Status`","primary":{"file":"src/tracking.una","start":{"line":64,"col":3},"end":{"line":64,"col":7}},"related":[],"repairs":[{"rank":1,"escape_cost":0,"description":"add an arm for each missing variant, such as `is Returned`, or an `else` arm","edit":null}],"explain":"una explain U2007"}],"fixable":0}
```

U2007 carries no `edit`, since only the author knows what a new arm should do. U2004, U2026 and the `==` form of U2009 carry exact edits, which `una fix .` applies. The compact rule: *records label every field and are nominal; a sum of one variant starts with `|`; `when` covers every variant or ends with `else`; test a variant with `is`, not `==`; a generic function writes `[T: Eq]`, `[T: Ord]` or `[T: Integer]` for what it does with `T`.*
:::

### Recap

:::recap
- Declare a record for data whose parts are all there at once; build it with every field labeled, and read it with a dot.
- Records are nominal: the name of a kind is part of its meaning, and the same fields do not make the same kind.
- Declare a sum for a value that is one of several cases, and give each variant only the fields true in that case.
- A sum of one variant starts with `|`. Test a variant that has fields with `is`; `==` compares whole values.
- `when` covers every variant; prefer an arm per variant to `else` on a sum that will grow.
- Range and literal arms end with `else`, unless they cover every value.
- A generic kind holds any type; a generic function writes the constraint, `Eq` or `Ord`, for what it does with its values.
:::

### Reference

:::reference
- Construct pages: [`kind`](/docs/language/types/kind/), [`when`](/docs/language/control-flow/when/), [constraints on generics](/docs/language/types/constraints/), [`example`](/docs/language/examples/example/)
- Prelude: [`Option`](/docs/std/)
- Diagnostics: [U1001](/docs/errors/U1001/), [U2001](/docs/errors/U2001/), [U2004](/docs/errors/U2004/), [U2007](/docs/errors/U2007/), [U2009](/docs/errors/U2009/), [U2025](/docs/errors/U2025/), [U2026](/docs/errors/U2026/), [U5001](/docs/errors/U5001/)
- Specification: [types](/docs/spec/03-types/), [functions and contracts](/docs/spec/04-functions-and-contracts/), [constraints on generics](/docs/spec/20-constraints-on-generics/), [verification](/docs/spec/12-verification/)
:::
