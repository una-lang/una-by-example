---
learn: "8.3"
title: A capability and handlers of your own
editions: ["0.2"]
codes: [U3001]
---

# 8.3 A capability and handlers of your own

A `capability` declares operations, with no code. A `handler` gives them code, and several handlers can implement one capability. `with @greeting = english()` installs a handler for one call, so the same function can talk to a real service in a program and to a fake one in a test.

## The program

- `src/greetings.una` declares `Greeting`, two handlers for it, and greets the same name with each.

## What you should see

`una run .` prints a greeting in English, then in Portuguese.

## Try it

1. Call `welcome("Ana")` without `with`. `una check .` reports U3001: nothing in `main` is `@greeting`.

## See also

- [`handler`](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/handler.md)
