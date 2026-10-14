---
learn: "6.3"
title: attempt and Result
editions: ["0.2"]
codes: [U0101]
---

# 6.3 attempt and Result

`attempt` turns one call that may fail into a value of `Result[T, E]`: `Ok(value)` when it returns, `Err(failure)` when it fails. A `when` then branches on it, like on any sum. It is the way to look at a failure instead of only handling it.

## The program

- `src/parsing.una` shows whether a text is a number, with `attempt` and `when`.

## What you should see

`una run .` prints two lines.

## Try it

1. Write `attempt number(text) + 1`. `una check .` reports U0101: `attempt` takes one call, not an expression around it.

## See also

- [`attempt`](https://github.com/una-lang/una/blob/main/docs/guide/language/errors/attempt.md)
