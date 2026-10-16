---
learn: "3.6"
title: "Testcase: a small calculator"
editions: ["0.2"]
codes: [U5001]
---

# 3.6 Testcase: a small calculator

This page combines what the chapter showed: functions with labeled parameters, `if` chains, and a function passed as a value.

## The program

- `src/calculator.una` picks an operation by its name, and prints the largest of two numbers with a lambda passed to `report`.

## What you should see

`una run .` prints three lines.

## Try it

1. Make an unknown operation divide, `a / b`, instead of giving `0`. `una check .` reports U5001: `b` may be zero, and a division by zero is not allowed even in a branch no test reaches.

## See also

- [Contracts and the verifier](../../07-contracts/)
