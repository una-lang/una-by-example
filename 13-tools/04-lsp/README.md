---
learn: "13.4"
title: "The editor: una lsp"
editions: ["0.2"]
codes: [U2001]
---

# 13.4 The editor: una lsp

`una lsp` is a language server: it speaks the Language Server Protocol over standard input and output. An editor that supports the protocol shows the same diagnostics as `una check` while you type, offers each repair with an edit as a quick fix, and shows a function's contract, its doc comments included, when you hover its name. It checks, formats and proves; it never runs a program.

## The program

- `src/editor.una` has a doc comment an editor shows on hover.

## What you should see

`una run .` prints `Hello, editor`.

## Try it

1. Call `greeting(42)`. In an editor connected to `una lsp`, the call is underlined with U2001; `una check .` reports the same.

## See also

- [`una lsp`, in the specification](https://github.com/una-lang/una/blob/main/docs/spec/13-diagnostics-and-abi.md)
