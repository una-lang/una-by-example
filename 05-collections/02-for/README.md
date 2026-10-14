---
learn: "5.2"
title: for
editions: ["0.2"]
codes: [U2019]
---

# 5.2 for

In edition `0.2`, `for x in xs` visits the elements of a list in order, and `for i in a..<b` the integers of a range. A loop updates `let edit` bindings declared before it. There is no `break` and no `continue`: what a loop computes is in the bindings it updates.

## The program

- `src/loops.una` sums a list, and builds the squares of `1` to `4` with a range.

## What you should see

`una run .` prints `15`, then `1 4 9 16`.

## Try it

1. Assign `x = 0` inside the loop. `una check .` reports U2019: the loop variable is a plain binding, and cannot be rebound.

## See also

- [`for`](https://github.com/una-lang/una/blob/main/docs/guide/language/control-flow/for.md)
