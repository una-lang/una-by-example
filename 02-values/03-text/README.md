---
learn: "2.3"
title: Text and interpolation
editions: ["0.2"]
codes: [U5001]
---

# 2.3 Text and interpolation

A `Text` has a length, `len`, and the prelude gives it functions: `to_upper`, `split`, `join`, `slice`, `contains_text` and more. A function of one argument reads like a field: `line.to_upper` is `to_upper(line)`. Inside a text, `{name}` puts a value there.

## The program

- `src/words.una` counts the characters and words of a line, prints it in capitals, and joins its words with `/`.

## What you should see

`una run .` prints three lines.

## Try it

1. Split on `""` instead of `" "`. `split` requires a separator that is not empty, and `una check .` reports U5001: the precondition is refuted, before the program ever runs.

## See also

- [Text, in the specification](https://github.com/una-lang/una/blob/main/docs/spec/22-text.md)
