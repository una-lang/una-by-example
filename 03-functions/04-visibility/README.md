---
learn: "3.4"
title: pub, and the headers a private function infers
editions: ["0.2"]
codes: [U3004]
---

# 3.4 pub, and the headers a private function infers

A declaration without `pub` is private to its module. A private function may leave out `uses` and `fails`: the compiler infers them, and `una contract` prints the header it inferred. A `pub` function is a module's reviewed boundary, so it declares everything it may do.

## The program

- `src/visibility.una` has a private `shout` that prints without saying so in its header. `main` declares the capability, and `shout` receives it.

## What you should see

`una run .` prints `INFERRED`.

## Try it

1. Make `shout` public. `una check .` reports U3004: a public function that uses `@console` must declare it.

## See also

- [Visibility and inference](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#43-visibility-and-inference)
