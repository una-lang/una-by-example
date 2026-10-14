---
learn: "4.4"
title: Generics and constraints
editions: ["0.2"]
codes: [U2026]
---

# 4.4 Generics and constraints

A kind or a function may take type parameters in brackets, `Pair[T]`, and the type arguments are inferred at each call. Without a constraint, a function knows nothing about a `T` but what its parameters give it. A constraint adds operations: `Eq` allows `==`, `Ord` also allows `<`, and `Integer` also allows `to_int()`.

## The program

- `src/generics.una` declares `Pair[T]`, swaps a pair of numbers, and finds the larger of a pair of texts with `[T: Ord]`.

## What you should see

`una run .` prints `2 1` and `pear`.

## Try it

1. Constrain `larger` with `[T: Eq]` instead of `[T: Ord]`. `una check .` reports U2026: ordering needs `Ord`, and the message says so.

## See also

- [Constraints on generics](https://github.com/una-lang/una/blob/main/docs/guide/language/types/constraints.md)
