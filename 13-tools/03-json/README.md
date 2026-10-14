---
learn: "13.3"
title: JSON output, for agents
editions: ["0.2"]
codes: [U2001]
---

# 13.3 JSON output, for agents

Every command takes `--json`, and then prints one JSON document named by its schema, such as `una.diagnostics/1`. Each diagnostic has its code, its message, its exact place and its repairs, so an agent reads the result without parsing text. A schema keeps its name until it changes incompatibly.

## The program

- `src/labels.una` is rejected on purpose: it prints an `Int` where `Text` is expected.

## What you should see

`una --json check .` prints one line of JSON with the diagnostic U2001.

## Try it

There is nothing to change here: compare `una check .` with `una --json check .` on any page of this book.

## See also

- [Una for agents](https://github.com/una-lang/una/blob/main/docs/guide/una-for-agents.md)
