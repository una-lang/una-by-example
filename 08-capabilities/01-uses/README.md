---
learn: "8.1"
title: uses and operations
editions: ["0.2"]
codes: [U3001]
---

# 8.1 uses and operations

A function that reaches outside the program says so in its header: `uses @console: Console[print]` names a binding, `@console`, its capability, `Console`, and the operations it may call, `print`. A binding is passed by name: a callee that uses `@console` receives its caller's `@console`.

## The program

- `src/report.una` prints two lines through a helper, `line`, which uses the same `@console` as `main`.

## What you should see

`una run .` prints `apples: 3` and `pears: 5`.

## Try it

1. Rename `line`'s binding to `@out`. `una check .` reports U3001 at each call: `main` holds no `@out`. A capability is never found by its type, only by name, or handed over with `with` (page 8.4).

## See also

- [`uses`](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/uses.md)
