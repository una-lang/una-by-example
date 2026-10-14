---
learn: "7.2"
title: ensures
editions: ["0.2"]
codes: [U5001]
---

# 7.2 ensures

`ensures` states a postcondition, about `result`. The verifier proves it on every path that returns, so a caller may rely on it without reading the body. When a proof fails, the diagnostic gives a counterexample: values of the parameters for which the body breaks its promise.

## The program

- `src/clamp.una` clamps a number into a range, and promises a result inside it.

## What you should see

`una run .` prints `100 0 42`.

## Try it

1. Return `x` instead of `high` when `x > high`. `una check .` reports U5001, with a counterexample: arguments for which the result is above `high`.

## See also

- [`ensures`](https://github.com/una-lang/una/blob/main/docs/guide/language/functions/ensures.md)
