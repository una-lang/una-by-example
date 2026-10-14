---
learn: "6.2"
title: if error and if none
editions: ["0.2"]
codes: [U3008]
---

# 6.2 if error and if none

A call that may fail is followed by a handling clause on its own indented line. `if error pass` hands the failure on unchanged, `if error fail V` turns it into another failure, and `if error use e` recovers with a value. For an `Option`, `if none fail V` and `if none use e` do the same with `None`.

## The program

- `src/handling.una` parses a number with `if none fail`, passes a failure on with `if error pass`, and recovers with `if error use`.

## What you should see

`una run .` prints three lines, two of them recovered.

## Try it

1. Declare `double` with another error kind, `OtherError`. `una check .` reports U3008: `if error pass` hands on an `InputError`, which `double` cannot fail with, and the message says to use `if error fail`.

## See also

- [`if error` and `if none`](https://github.com/una-lang/una/blob/main/docs/guide/language/errors/if-error.md)
