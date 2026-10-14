---
learn: "5.1"
title: Lists
editions: ["0.2"]
codes: [U2001]
---

# 5.1 Lists

A `List[T]` holds values of one type, in order, written in brackets. A list is a value: `append` gives a new list and leaves the old one as it was. The prelude gives lists `len`, `first`, `at`, `contains`, `sum` and the functions of the next pages.

## The program

- `src/lists.una` appends a prime to a list, and prints both lengths, whether `5` is in the new list, and its total.

## What you should see

`una run .` prints three lines.

## Try it

1. Put `"5"` among the numbers. `una check .` reports U2001: a list holds one type, and `"5"` is `Text`.

## See also

- [The standard library](https://github.com/una-lang/una/blob/main/docs/spec/14-standard-library.md)
