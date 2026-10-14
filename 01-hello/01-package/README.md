---
learn: "1.1"
title: A package
editions: ["0.2"]
codes: [U3004, U7001]
---

# 1.1 A package

Every Una program is a package: a directory with `una.toml`, `verification.lock` and its modules under `src/`. This one prints a line. Its one function, `main`, also says in its header the only thing it may do: print on the console.

## The program

- `una.toml` names the package and picks edition `0.2`. Its `[run]` table says that `una run` starts at the module `hello`, and grants it the console.
- `verification.lock` pins the solver that proves the package's contracts, so that a proof means the same on every machine. Every package has one; this one is the same as in every example.
- `src/hello.una` holds the module `hello` and its function `main`. The line `uses @console: Console[print]` is part of the header: `main` may call the operation `print` of the capability `Console`, and nothing else.

## What you should see

`una run .` prints `Hello, Una`.

## Try it

1. Change the text to `"Hello again, Una"`. `una run .` prints the new line.
2. Delete the line `uses @console: Console[print]`. `una check .` now reports U3004: `main` uses `@console`, but its header declares no `uses`. It also reports U7001, because a header without clauses is written on one line in canonical form, which `una fmt` would do for you.

## See also

- [The `uses` clause](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/uses.md)
- [The host's capabilities](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/host.md)
- [`[run] grants`](https://github.com/una-lang/una/blob/main/docs/guide/configure/run/grants.md)
