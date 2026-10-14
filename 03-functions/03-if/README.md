---
learn: "3.3"
title: if as an expression
editions: ["0.2"]
codes: [U2001]
---

# 3.3 if as an expression

`if` gives a value: both branches have one, of the same type. On one line it reads `if c then a else b`. Over several lines each branch is a block, and the value of a block is its last line. `else if` chains the cases.

## The program

- `src/parity.una` names a number even or odd with a one-line `if`, then describes it with a chain over several lines.

## What you should see

`una run .` prints three descriptions.

## Try it

1. Make the `else` branch of `parity` give `1` instead of `"odd"`. `una check .` reports U2001: the branches of an `if` must have the same type.

## See also

- [`if`](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#52-if)
