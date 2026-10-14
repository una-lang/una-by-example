---
learn: "13.1"
title: una fix
editions: ["0.2"]
codes: [U2004]
---

# 13.1 una fix

Many diagnostics carry a repair, and some repairs carry an exact edit. `una fix .` applies those edits, checks again, and repeats until nothing is left to apply, then formats the package. It never applies an edit that would widen what the program may do. `--dry-run` shows what it would change without writing.

## The program

- `src/area.una` is rejected on purpose: a second argument without its label.

## What you should see

`una check .` reports U2004, and `una fix --dry-run .` shows the edit it would apply: the label `height`.

## Try it

1. Apply it yourself: `rectangle(3, height: 4)`. The program checks, prints `12`, and `una fix --dry-run .` has nothing left to do.

## See also

- [`una fix`, in the specification](https://github.com/una-lang/una/blob/main/docs/spec/13-diagnostics-and-abi.md)
