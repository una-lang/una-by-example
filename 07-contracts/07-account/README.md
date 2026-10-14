---
learn: "7.7"
title: "Testcase: an account that cannot go negative"
editions: ["0.2"]
codes: [U5001]
---

# 7.7 Testcase: an account that cannot go negative

This page combines the chapter: a refined kind for a balance, a function with a contract, and a function that fails rather than break the refinement. No test could cover every amount; the verifier does.

## The program

- `src/account.una` deposits, then withdraws twice: once too much, which fails and keeps the balance, and once within it.

## What you should see

`una run .` prints `75 75 15`.

## Try it

1. Remove the check `amount > b` from `withdraw`. `una check .` reports U5001: the result may be negative, as the counterexample shows.

## See also

- [Refined kinds with `where`](../03-refined/)
