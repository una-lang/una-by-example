---
learn: "8.2"
title: The host's capabilities and grants
editions: ["0.2"]
codes: [U3012, U4003]
---

# 8.2 The host's capabilities and grants

The host provides `Console`, `Files`, `Env`, `Clock`, `Keys` and `Http`. `una run` gives `main` only what `[run] grants` in `una.toml` lists: here, the console, and reading and writing files under `src`. What a program reads from outside is labeled `internal`: it may go to a file, but not to the console, which accepts only `public` data.

## The program

- `src/notes.una` reads `notes.txt` and writes a copy of it, `copy.txt`, then prints that it did.

## What you should see

`una run .` prints `copied the notes`, and `src/copy.txt` holds the note.

## Try it

1. Grant only `files:src:read` in `una.toml`. `una check .` reports U3012: `main` writes a file, which no grant allows.
2. Print the note itself. `una check .` reports U4003: the console accepts `public` data, and the note is `internal`. Lowering a label takes a policy (chapter 9).

## See also

- [Host capabilities and grants](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/host.md)
- [`[run] grants`](https://github.com/una-lang/una/blob/main/docs/guide/configure/run/grants.md)
