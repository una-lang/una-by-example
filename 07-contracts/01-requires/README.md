---
learn: "7.1"
title: requires
editions: ["0.2"]
codes: [U5001, U7001]
---

# 7.1 requires

`requires` states a precondition over the parameters. The verifier proves it at every call, before the program runs, and the body may assume it. Here it lets the body divide by `people`, since the verifier knows it is not zero.

## The program

- `src/share.una` divides a total among a number of people, which `requires` keeps above zero.

## What you should see

`una run .` prints `30`.

## Try it

1. Call `share(120, people: 0)`. `una check .` reports U5001: the precondition `0 > 0` is refuted at the call.
2. Remove the `requires`. `una check .` reports U7001: without a clause, `share` belongs in the short form.
3. Write it in that form, `share(total: Int, people: Int) -> Int = total / people`. `una check .` reports U5001: the division by `people` is refuted, with the counterexample `people = 0`.

## See also

- [`requires`](https://github.com/una-lang/una/blob/main/docs/guide/language/functions/requires.md)
