---
learn: "1.3"
title: Comments and doc comments
editions: ["0.2"]
codes: [U0101]
---

# 1.3 Comments and doc comments

A comment starts with `--` and runs to the end of its line. A doc comment starts with `---` and belongs to the declaration that follows it: `una contract` prints it with the declaration's header, so tools and agents read it too. There are no block comments.

## The program

- `src/notes.una` shows an ordinary comment at the top, a doc comment on `days`, and a comment inside the body of `main`.

## What you should see

`una run .` prints `a week has 7 days`.

## Try it

1. Start the first comment with `//` instead of `--`. `una check .` reports U0101: `//` is not a comment in Una.

## See also

- [The specification: comments](https://github.com/una-lang/una/blob/main/docs/spec/01-lexical-structure.md)
