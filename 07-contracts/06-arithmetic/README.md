---
learn: "7.6"
title: Overflow and division, proven
editions: ["0.2"]
codes: [U5001]
---

# 7.6 Overflow and division, proven

A division by a value that might be zero, and a fixed-width operation that might overflow, are proof obligations. The verifier proves each one away before the program runs, so neither ever fails at run time. Here, the empty list is handled before the division.

## The program

- `src/average.una` averages a list, and gives `0` for an empty one.

## What you should see

`una run .` prints `5 0`.

## Try it

1. Write the body as `xs.sum() / xs.len` alone. `una check .` reports U5001: the length may be zero, and the counterexample says so.

## See also

- [Verification](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#11-verification)
