---
learn: "3.2"
title: The short and the long form
editions: ["0.2"]
codes: [U7001]
---

# 3.2 The short and the long form

A function with no clauses and a one-line body is written on one line: `square(n: Int) -> Int = n * n`. Any other function takes the long form: the header and its clauses, then `=` alone on its line, then the body, indented. Each function has exactly one canonical form, and `una fmt` writes it.

## The program

- `src/forms.una` writes `square` in the short form, and `triple` in the long form, since it has an `ensures` clause.

## What you should see

`una run .` prints `16 15`.

## Try it

1. Write `square` in the long form. `una check .` reports U7001: the canonical form of a function with no clauses and a one-line body is the short one. `una fmt .` rewrites it.

## See also

- [Two forms](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#41-two-forms)
