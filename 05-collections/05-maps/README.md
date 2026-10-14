---
learn: "5.5"
title: Maps
editions: ["0.2"]
codes: [U2001]
---

# 5.5 Maps

A `Map[K, V]` maps keys to values, ordered by its keys. `edit m.set(...)` changes an editable map in place, and `get` gives an `Option`, since a key may be absent. `empty_map()` takes its key and value types from the binding it is written to.

## The program

- `src/maps.una` puts two fruits in a map, reads one back, and prints the keys in order.

## What you should see

`una run .` prints `2 kinds, 7 apples`, then `apples, pears`.

## Try it

1. Set the pears to `"four"`. `una check .` reports U2001: the map holds `Int` values.

## See also

- [Maps, in the specification](https://github.com/una-lang/una/blob/main/docs/spec/21-maps.md)
