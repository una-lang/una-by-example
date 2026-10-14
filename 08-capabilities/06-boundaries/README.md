---
learn: "8.6"
title: Boundaries (0.3 preview)
editions: ["0.3"]
codes: [U3020]
---

# 8.6 Boundaries (0.3 preview)

In edition `0.3`, `una.toml` can mark a module as a boundary, such as a vendored library, with a ceiling: the most the rest of the package may grant it. A call into a boundary takes nothing by name. The caller grants each capability with `with`, so every call shows exactly what the boundary receives.

## The program

- `una.toml` marks `plugin` as a boundary that may receive `Console[print]`.
- `src/plugin.una` is the boundary; `src/app.una` calls it, granting the console on purpose.

## What you should see

`una run .` prints `GRANTED ON PURPOSE`.

## Try it

1. Call `shout(...)` without `with`. `una check .` reports U3020: a call into the boundary grants only with `with`.

## See also

- [`[boundaries]`](https://github.com/una-lang/una/blob/main/docs/guide/configure/boundaries.md)
