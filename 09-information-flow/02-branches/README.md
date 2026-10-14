---
learn: "9.2"
title: Branches raise the program counter
editions: ["0.2"]
codes: [U4001, U4003]
---

# 9.2 Branches raise the program counter

A branch on a secret makes what it decides secret, even when each branch is a constant: from the answer, one could learn the secret. The checker tracks this with the label of the program counter, raised inside a branch on labeled data.

## The program

- `src/bonus.una` decides a bonus from a secret score, and returns a `secret Bool`.

## What you should see

`una run .` prints `decided`.

## Try it

1. Return a plain `Bool`. `una check .` reports U4001: which value is returned depends on a `secret` condition.
2. Print the decision. `una check .` reports U4003: the console accepts `public` data, and the decision is `secret`.

## See also

- [Labels](https://github.com/una-lang/una/blob/main/docs/guide/language/information-flow/labels.md)
