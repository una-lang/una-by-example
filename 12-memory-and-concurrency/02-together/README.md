---
learn: "12.2"
title: together
editions: ["0.2"]
codes: [U1001]
---

# 12.2 together

`together` runs its `let` branches as concurrent tasks, and all of them end before the block does. `together for x in xs` runs one task per element and gives the results in list order. The result is always the same as running the tasks one after another, so concurrency never changes what a program computes.

## The program

- `src/tasks.una` computes two squares together, then the squares of a list together.

## What you should see

`una run .` prints `25`, then `1 4 9 16`.

## Try it

1. Make the second branch use the first's result, `slow_square(a)`. `una check .` reports U1001: a task never sees its siblings' bindings, so `a` is not in scope there.

## See also

- [`together`](https://github.com/una-lang/una/blob/main/docs/guide/language/control-flow/together.md)
