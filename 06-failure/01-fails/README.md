---
learn: "6.1"
title: fails and fail
editions: ["0.2"]
codes: [U3007]
---

# 6.1 fails and fail

An error kind is an ordinary sum kind. A function that may fail declares it with `fails`, and `fail V` ends it with that variant. A function without `fails` cannot fail at all. There are no exceptions: every failure is in a header, and every call that may fail is handled where it is made.

## The program

- `src/withdraw.una` fails when an amount is negative or larger than the balance. `main` handles the failure with `if error use 0`.

## What you should see

`una run .` prints `70 left`.

## Try it

1. Remove the line `if error use 0`. `una check .` reports U3007: the call can fail, and nothing says what to do if it does.

## See also

- [`fails`](https://github.com/una-lang/una/blob/main/docs/guide/language/errors/fails.md)
- [`fail`](https://github.com/una-lang/una/blob/main/docs/guide/language/errors/fail.md)
