---
learn: "12.3"
title: "A native executable: una build"
editions: ["0.2"]
codes: [U2001]
---

# 12.3 A native executable: una build

`una run` interprets a program. `una build .` compiles it into a native executable, `target/una/<name>`, after the same checks. The executable runs on its own, with the grants of `una.toml`. Linking needs a C compiler, `cc`.

## The program

- `src/native.una` sums a list and prints it.

## What you should see

`una run .` prints `built natively: 15`. `una build .` reports where it wrote the executable, and running it prints the same line.

## Try it

1. Put `"5"` in the list. `una check .` reports U2001, and `una build .` builds nothing: a program that does not check is never compiled.

## See also

- [Getting started](https://github.com/una-lang/una/blob/main/docs/guide/getting-started.md)
