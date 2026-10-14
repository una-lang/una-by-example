---
learn: "9.1"
title: Labels and levels
editions: ["0.2"]
codes: [U4001]
---

# 9.1 Labels and levels

A label says how sensitive a value is: `public`, `internal`, `confidential`, `secret` or `restricted`, from least to most. A type without one is `public`. A result carries the labels of what it was computed from, and a value flows only to a place labeled at least as high, which the checker proves at every step.

## The program

- `src/salary.una` raises secret salaries, and prints how many there are. Their number is not secret, even though the salaries are.

## What you should see

`una run .` prints `3 people`.

## Try it

1. Make `headcount` return `pays.sum()`. `una check .` reports U4001: the sum of secret salaries is `secret`, and `headcount` returns a `public Int`.

## See also

- [Labels](https://github.com/una-lang/una/blob/main/docs/guide/language/information-flow/labels.md)
