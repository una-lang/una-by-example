---
learn: "1.4"
title: Printing
editions: ["0.2"]
codes: [U2001]
---

# 1.4 Printing

`Console.print` writes one line of text. Its argument is `Text`, and a value of another type goes into the text in braces. The console is a capability: a function prints only when its header says `uses @console: Console[print]`, and `una run` provides it only when `una.toml` grants it.

## The program

- `src/printing.una` prints three lines. The third puts the `Int` bound to `lines` into the text.

## What you should see

`una run .` prints:

```text
one line
and another
3 lines in all
```

## Try it

1. Print `lines` itself, `@console.print(lines)`. `una check .` reports U2001: `print` takes `Text`, and `lines` is an `Int`. Writing `"{lines}"` turns it into text.

## See also

- [The host's capabilities](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/host.md)
- [Text](https://github.com/una-lang/una/blob/main/docs/spec/22-text.md)
