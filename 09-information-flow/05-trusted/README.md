---
learn: "9.5"
title: Trusted modules
editions: ["0.2"]
codes: [U7005]
---

# 9.5 Trusted modules

A trusted module may declare policies, and the checker does not check information flow inside them: it trusts them, as part of the program's trusted base. So a module is trusted only when it says so in its header, `trusted module`, and `una.toml` lists it too, where adding one is visible in review.

## The program

- `una.toml` lists `redact` under `[trusted] modules`.
- `src/redact.una` declares a policy that reveals only a note's length.

## What you should see

`una run .` prints the length of a secret note.

## Try it

1. Remove `[trusted]` from `una.toml`. `una check .` reports U7005: the module calls itself trusted, and `una.toml` does not list it.

## See also

- [Trusted modules](https://github.com/una-lang/una/blob/main/docs/guide/language/information-flow/trusted.md)
