---
learn: "8.5"
title: Conditions on operations (0.3 preview)
editions: ["0.3"]
codes: [U5001]
---

# 8.5 Conditions on operations (0.3 preview)

In edition `0.3`, an operation in `uses` may carry a condition over the function's parameters: `print where not quiet`. The verifier proves that every place that may print does so only where the condition holds. A header then says not only what a function may do, but when.

## The program

- `una.toml` picks edition `0.3`.
- `src/prices.una` prints a total unless `quiet`, and guards the operation to match its header.

## What you should see

`una run .` prints `total: 42` only: the second call is quiet.

## Try it

1. Remove the guard `if not quiet`. `una check .` reports U5001: `print` may run where `not quiet` is not proven, with the counterexample `quiet = true`.

## See also

- [`uses`](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/uses.md)
