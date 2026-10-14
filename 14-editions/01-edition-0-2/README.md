---
learn: "14.1"
title: What edition 0.2 changes
editions: ["0.2"]
codes: [U0103]
---

# 14.1 What edition 0.2 changes

A package names its edition in `una.toml`. Edition `0.2` adds `for` loops, `let edit` with `edit` and `take` parameters, fixed-width integers, maps, JSON, constraints on generics and `together`. A package of edition `0.1` keeps its meaning under any compiler that serves it.

## The program

- `src/loops.una` uses `let edit` and `for`, both of edition `0.2`.

## What you should see

`una run .` prints `6`.

## Try it

1. Set `edition = "0.1"` in `una.toml`. `una check .` reports U0103: `edit` is reserved there for edition `0.2`.

## See also

- [`[package] edition`](https://github.com/una-lang/una/blob/main/docs/guide/configure/package/edition.md)
