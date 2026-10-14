---
learn: "5.6"
title: JSON
editions: ["0.2"]
codes: [U2001]
---

# 5.6 JSON

`Json` is a kind of the prelude, with one variant for each kind of JSON value: `Null`, `Boolean`, `Number`, `Decimal`, `Str`, `Array` and `Object`. `to_json` writes a value in one canonical form, with an object's keys in order and no spaces, so the same value always gives the same text. `parse_json` reads text, and can fail (chapter 6).

## The program

- `src/json.una` builds an object with three fields and prints it.

## What you should see

`una run .` prints `{"name":"Una","pages":79,"tags":["learn",true]}`.

## Try it

1. Set `pages` to `79` instead of `Number(value: 79)`. `una check .` reports U2001: a field of a JSON object is a `Json`, and `79` is an `Int`.

## See also

- [JSON, in the specification](https://github.com/una-lang/una/blob/main/docs/spec/23-json.md)
