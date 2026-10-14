---
learn: "10.1"
title: "Examples: do and expect"
editions: ["0.2"]
codes: []
---

# 10.1 Examples: do and expect

An `example` is a test that lives next to the code it tests. `do` runs one expression, and each `expect` line is a condition on its `result` that must hold. `una check` checks examples like any code, and `una test` runs them all, each in a fresh machine.

## The program

- `src/grades.una` grades a score, with an example on each side of the pass mark.

## What you should see

`una run .` prints a reminder, and `una test .` reports both examples passing.

## Try it

1. Make `grade` pass only above 50. The program still checks, since no contract says otherwise, but `una test .` reports the example at 50 failing, with the `result` it got.

## See also

- [`example`](https://github.com/una-lang/una/blob/main/docs/guide/language/examples/example.md)
