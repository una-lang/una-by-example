---
learn: "7.5"
title: Reading a counterexample
editions: ["0.2"]
codes: [U5001]
---

# 7.5 Reading a counterexample

This program is rejected on purpose. A refuted obligation comes with a counterexample: values of the function's parameters, and of `result`, for which the contract fails. It is a concrete case to read, not a guess: run the body on those values by hand and the contract breaks.

## The program

- `src/discount.una` promises a result that is never negative, but subtracts any discount from the price.

## What you should see

`una check .` reports U5001 at the `ensures`, with a counterexample in which `off` is larger than `price`. Read it as a test case: with those arguments, `price - off` is negative.

## Try it

1. Add `requires off <= price`. The verifier now proves the `ensures`, and the program runs.

## See also

- [Reading a counterexample, for agents](https://github.com/una-lang/una/blob/main/docs/guide/una-for-agents.md)
