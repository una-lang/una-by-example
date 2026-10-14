---
learn: "4.1"
title: Records
editions: ["0.2"]
codes: [U2009]
---

# 4.1 Records

A record kind declares a type of named fields, each with its type, one per indented line. A value is built with every field labeled, and its fields are read with a dot. Records are nominal: two kinds with the same fields are still different types.

## The program

- `src/records.una` declares `Book` and prints a summary of one.

## What you should see

`una run .` prints the book's title and pages.

## Try it

1. Build a `Book` with its `title` only. `una check .` reports U2009: `Book` is missing field `pages`. Every field gets a value; there are no defaults.

## See also

- [Declaring kinds](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#32-declaring-kinds)
