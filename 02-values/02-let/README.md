---
learn: "2.2"
title: let and let edit
editions: ["0.2"]
codes: [U2019]
---

# 2.2 let and let edit

`let` binds a name to a value once. In edition `0.2`, `let edit` binds a name that later lines may rebind with `name = value`. There are no references: rebinding `total` changes only `total`.

## The program

- `src/counter.una` starts `total` at the value of `start`, then rebinds it twice.

## What you should see

`una run .` prints `total is 30`.

## Try it

1. Declare `total` with `let` instead of `let edit`. `una check .` reports U2019 at both lines that assign it, and the message says how to declare it.
2. Assign `start = 6` after binding it. `start` was bound with `let`, so this is U2019 too.

## See also

- [`let edit` and `edit` parameters](https://github.com/una-lang/una/blob/main/docs/guide/language/control-flow/let-edit.md)
