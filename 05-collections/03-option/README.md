---
learn: "5.3"
title: Option
editions: ["0.2"]
codes: [U2001]
---

# 5.3 Option

A value that may be missing has the type `Option[T]`: it is `Some(value)` or `None`. Una has no null, so a missing value is visible in the type, and code must say what to do with `None` before it can use the value: with `when`, with `or_else`, or with `if none` (chapter 6).

## The program

- `src/options.una` reads the list at two indices, one of them out of range, and takes its first element with a default.

## What you should see

`una run .` prints `found 20`, `nothing` and `10`.

## Try it

1. Bind `xs.first()` to a name declared `Int`. `una check .` reports U2001: the value is an `Option[Int]`, not an `Int`.

## See also

- [`if error` and `if none`](../../06-failure/02-handling/)
