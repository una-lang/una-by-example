---
learn: "2.1"
title: Int, Bool, Text and literals
editions: ["0.2"]
codes: [U2001]
---

# 2.1 Int, Bool, Text and literals

An `Int` is a whole number of any size: it never overflows, so `9000000000 * 9000000000` is exact. A `Bool` is `true` or `false`. A `Text` is a string of UTF-8 characters between double quotes. Each value has one type, and nothing converts from one type to another unless the code says so.

## The program

- `src/literals.una` binds four values with `let` and prints them. Braces in a text put a value there, whatever its type.

## What you should see

`una run .` prints the four values.

## Try it

1. Bind `ready` to `1` instead of `true`, and use it with `and`. `una check .` reports U2001: `and` takes `Bool` operands, and `1` is an `Int`. Una has no truthy numbers.

## See also

- [Built-in types](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#31-built-in-types)
