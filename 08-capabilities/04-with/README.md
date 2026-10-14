---
learn: "8.4"
title: "with: installing and rebinding"
editions: ["0.2"]
codes: [U3001]
---

# 8.4 with: installing and rebinding

`with` hands a callee a binding, for one call: `with @out = @console` gives the callee's `@out` the caller's `@console`, and `with @greeting = english()` installs a handler. The caller always says what it hands over, and the callee never takes more.

## The program

- `src/rebinding.una` calls `banner`, which asks for `@out`, with the caller's `@console`.

## What you should see

`una run .` prints the banner, then `done`.

## Try it

1. Remove `with @out = @console`. `una check .` reports U3001: `main` has no `@out` of its own.

## See also

- [`@` bindings and `with`](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/with.md)
