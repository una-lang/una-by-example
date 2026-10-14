---
learn: "4.5"
title: "Testcase: a shape library"
editions: ["0.2"]
codes: [U2001]
---

# 4.5 Testcase: a shape library

This page combines the chapter: records inside variants, `when` arms that bind only the fields they use, and functions over shapes.

## The program

- `src/shapes.una` moves a list of shapes ten units to the right and prints where each one is, then a perimeter.

## What you should see

`una run .` prints the shapes' new `x` positions, then `800`.

## Try it

1. Call `move(corner, dx)` without `dy:`. `una check .` reports U2001: `move` is missing argument `dy`. Every parameter receives an argument.

## See also

- [Records](../01-records/)
