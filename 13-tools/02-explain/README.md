---
learn: "13.2"
title: una explain
editions: ["0.2"]
codes: [U5001]
---

# 13.2 una explain

Every diagnostic has a code, and `una explain <code>` prints what the code means and how to repair it, with a failing example and a fixed one. The explanations are part of the compiler, so they match the release that reports the code.

## The program

- `src/ratio.una` is rejected on purpose: a division by a value that may be zero.

## What you should see

`una check .` reports U5001 with the counterexample `b = 0`, and `una explain U5001` prints the explanation.

## Try it

1. Divide only when `b` is not zero. The program checks and prints `5`.

## See also

- [All diagnostic codes](https://github.com/una-lang/una/blob/main/docs/spec/13-diagnostics-and-abi.md)
