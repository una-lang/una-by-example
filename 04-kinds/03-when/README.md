---
learn: "4.3"
title: when … is
editions: ["0.2"]
codes: [U2007, U5001]
---

# 4.3 when … is

`when` takes a value apart: each arm names a variant and binds its fields by name, and the value of the `when` is the value of the arm that matches. The checker proves that every variant has an arm. Arms on literals end with `else`, which covers every other value.

## The program

- `src/areas.una` computes an area for each variant of `Shape`, and names a number with literal arms.

## What you should see

`una run .` prints two lines.

## Try it

1. Remove the arm `is Dot -> 0`. `una check .` reports U2007: the `when` does not cover `Dot`.
2. Remove the arm `else -> "many"`. Literal arms are an obligation, so `una check .` reports U5001: they do not cover every `Int`, and the counterexample is a `code` that no arm matches.

## See also

- [`when`](https://github.com/una-lang/una/blob/main/docs/guide/language/control-flow/when.md)
