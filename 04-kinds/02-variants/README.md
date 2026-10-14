---
learn: "4.2"
title: Variants
editions: ["0.2"]
codes: [U2009]
---

# 4.2 Variants

A sum kind lists its variants, separated by `|`. A value is exactly one of them, and a variant may carry fields. `s is Dot` tests which variant a value is.

## The program

- `src/variants.una` declares `Shape` with three variants, makes a list of shapes and counts the points among them.

## What you should see

`una run .` prints `3 shapes, 1 of them a point`.

## Try it

1. Compare `Dot == Circle`. `una check .` reports U2009: `Circle` carries a field, so on its own it is not a value. To test a variant, write `s is Circle`.

## See also

- [`kind`](https://github.com/una-lang/una/blob/main/docs/guide/language/types/kind.md)
