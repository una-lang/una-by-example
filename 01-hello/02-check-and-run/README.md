---
learn: "1.2"
title: una check and una run
editions: ["0.2"]
codes: [U1001, U2001]
---

# 1.2 una check and una run

`una check .` reads the package and reports every problem it finds, each with a code and a place. Nothing runs. `una run .` runs the package, but only once it checks clean. This program calls a small function and prints its result.

## The program

- `src/greet.una` declares `double`, a function of one `Int` that returns an `Int`. It is private: without `pub`, only its module can call it.
- `main` binds the result of `double(21)` with `let`, then prints it. `{answer}` in the text puts the value there.

## What you should see

`una check .` reports nothing, and `una run .` prints `the answer is 42`.

## Try it

1. Call `double("21")`. `una check .` reports U2001 at the argument: `double` takes an `Int`, and `"21"` is `Text`.
2. Call `@console.show(...)` instead of `@console.print(...)`. `una check .` reports U1001: `Console` has no operation `show`.

## See also

- [Getting started](https://github.com/una-lang/una/blob/main/docs/guide/getting-started.md)
- `una explain U2001` prints what a code means and how to repair it.
