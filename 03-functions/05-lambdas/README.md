---
learn: "3.5"
title: Lambdas and function values
editions: ["0.2"]
codes: [U2010]
---

# 3.5 Lambdas and function values

A function is a value: it can be passed to a parameter of function type, such as `fn(Int) -> Int`. A lambda, `fn(params) -> body`, is a function written where it is used, with a body of one line. Its parameters' types come from the parameter it is passed to.

## The program

- `src/lambdas.una` passes a named function and a lambda to `twice`, which calls the function it receives two times.

## What you should see

`una run .` prints `7 200`.

## Try it

1. Bind a lambda with `let`, unused: `let keep = fn(n) -> n + 1`. `una check .` reports U2010: nothing says what type `n` has, and the message asks for an annotation, `n: Int`.

## See also

- [Lambdas and function types](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#46-lambdas-and-function-types)
