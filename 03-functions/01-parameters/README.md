---
learn: "3.1"
title: Parameters, labels and results
editions: ["0.2"]
codes: [U2004, U2005]
---

# 3.1 Parameters, labels and results

A function's header names its parameters, each with its type, and the type of its result. A call passes the first argument as it is and every other one with its parameter's name, so a call reads the same in a year as the day it was written. A variable with the parameter's name needs no label.

## The program

- `src/area.una` declares `rectangle` and calls it twice: once with the label `height:`, once with a variable named `height`.

## What you should see

`una run .` prints `12 and 20`.

## Try it

1. Call `rectangle(3, 4)`. `una check .` reports U2004: the second argument needs its label. The diagnostic carries the edit that adds it, which `una fix .` applies.
2. Call `rectangle(3, depth: 4)`. `una check .` reports U2005: `rectangle` has no parameter `depth`.

## See also

- [Calls and labeled arguments](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#44-calls-and-labeled-arguments)
