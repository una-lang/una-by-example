---
learn: "2.4"
title: Fixed-width integers
editions: ["0.2"]
codes: [U2022, U5001]
---

# 2.4 Fixed-width integers

`Int` never overflows, so most code uses it. Where a width matters, in bytes, protocols or hashes, edition `0.2` has `I8` to `I64` and `U8` to `U64`. An operation that could leave the range is a proof obligation: the verifier proves it stays in range, or the program is rejected. Overflow never happens at run time.

## The program

- `src/bytes.una` adds two `U8` values. Its two `requires` keep each one at most 100, so their sum fits in a `U8`, and the verifier proves it.
- `to_int()` turns a `U8` into an `Int`, to print it.

## What you should see

`una run .` prints `155`.

## Try it

1. Allow `a` up to 200: `requires a <= 200`. `una check .` reports U5001: the sum may now overflow, and the counterexample gives two values whose sum is over 255.
2. Bind `small` to `300`. `una check .` reports U2022: the literal does not fit a `U8`.

## See also

- [Fixed-width integers, in the specification](https://github.com/una-lang/una/blob/main/docs/spec/18-fixed-width-integers.md)
