---
learn: "12.1"
title: edit and take
editions: ["0.2"]
codes: [U2017, U2020]
---

# 12.1 edit and take

There are no references in Una, and no lifetimes. An `edit` parameter is passed in and out: the function receives the caller's value, and the caller's binding receives the final value. The call says so with `edit`. A `take` parameter consumes its argument, which the caller cannot use afterwards. In `ensures`, `old(t)` is the value on entry.

## The program

- `src/tally.una` records three values into a `Tally` through an `edit` parameter, then consumes it with `take`.

## What you should see

`una run .` prints `3 values, total 12`.

## Try it

1. Print `t.seen` after `finish(take t)`. `una check .` reports U2017: `t` was taken.
2. Call `t.record(value: x)` without `edit`. `una check .` reports U2020: the parameter is `edit`, so the call must say so.

## See also

- [`let edit` and `edit` parameters](https://github.com/una-lang/una/blob/main/docs/guide/language/control-flow/let-edit.md)
- [`take`](https://github.com/una-lang/una/blob/main/docs/guide/language/control-flow/take.md)
