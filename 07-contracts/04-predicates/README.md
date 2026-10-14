---
learn: "7.4"
title: Predicates
editions: ["0.2"]
codes: [U5001]
---

# 7.4 Predicates

A predicate names a condition, for use in contracts and refinements. A `reflect` predicate is one the verifier can see inside, so it can prove it. An `opaque` one is hidden from proofs, and only `checked` can establish it (page 6.4).

## The program

- `src/evens.una` declares `even` as a `reflect` predicate, a kind `Even` over it, and a function the verifier proves always returns one.

## What you should see

`una run .` prints `42`.

## Try it

1. Return `2 * n + 1`. `una check .` reports U5001: the result is not even, and the counterexample shows an `n`.

## See also

- [`predicate`](https://github.com/una-lang/una/blob/main/docs/guide/language/types/predicate.md)
