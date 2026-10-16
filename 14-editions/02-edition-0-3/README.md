---
learn: "14.2"
title: The 0.3 preview
editions: ["0.3"]
codes: [U0101]
---

# 14.2 The 0.3 preview

Edition `0.3` is a preview: what it adds may still change before it is stable. It adds conditions on operations (page 8.5), boundaries (page 8.6) and locked contracts (page 11.3). The constructs of `0.3` exist only in a package that picks it.

## The program

- `una.toml` picks edition `0.3`.
- `src/preview.una` puts a condition on an operation.

## What you should see

`una run .` prints `edition 0.3`.

## Try it

1. Set `edition = "0.2"` in `una.toml`. `una check .` reports U0101 at `where`: in edition `0.2`, an operation takes no condition.

## See also

- [Conditions on operations](../../08-capabilities/)
