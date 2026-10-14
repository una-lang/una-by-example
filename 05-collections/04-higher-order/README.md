---
learn: "5.4"
title: map, filter and fold
editions: ["0.2"]
codes: [U2001]
---

# 5.4 map, filter and fold

`map` makes a new list by applying a function to each element. `filter` keeps the elements a test accepts. `fold` carries a value through the list, from the first element to the last. Each takes its function as a labeled argument, often a lambda.

## The program

- `src/higher.una` doubles a list, keeps its even numbers, and multiplies them all together. `mod` gives the remainder, which is never negative.

## What you should see

`una run .` prints the doubled list, then the count of even numbers and the product.

## Try it

1. Give `filter` the test `x mod 2`, without `== 0`. `una check .` reports U2001: the test must give a `Bool`, and `x mod 2` is an `Int`.

## See also

- [The standard library](https://github.com/una-lang/una/blob/main/docs/spec/14-standard-library.md)
