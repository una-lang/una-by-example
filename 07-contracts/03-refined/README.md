---
learn: "7.3"
title: Refined kinds with where
editions: ["0.2"]
codes: [U5001]
---

# 7.3 Refined kinds with where

A refined kind is a base type with a condition: `Int in 0..100` is sugar for `Int where 0 <= it and it <= 100`. A value of the refined kind can be used wherever its base is expected. Making one is an obligation: the verifier proves the condition holds wherever such a value is made.

## The program

- `src/percent.una` declares `Percent`, and clamps any number into it.

## What you should see

`una run .` prints `100% 0% 35%`.

## Try it

1. Leave out the lower branch, `if n < 0 then 0`. `una check .` reports U5001, with the counterexample of a negative `n`.

## See also

- [`where` and refinements](https://github.com/una-lang/una/blob/main/docs/guide/language/types/where.md)
