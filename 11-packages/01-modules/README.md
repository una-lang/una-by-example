---
learn: "11.1"
title: Modules and imports
editions: ["0.2"]
codes: [U1004, U7001]
---

# 11.1 Modules and imports

A module is one file, and its path follows the file's: `src/shop/prices.una` is `shop.prices`. `import` names a module and the declarations it uses from it. Only `pub` declarations can be imported, so a module's private functions stay its own.

## The program

- `src/shop/prices.una` exports `with_tax`, and keeps `tax` private.
- `src/shop/app.una` imports `with_tax` and prints a price.

## What you should see

`una run .` prints `1200 cents`.

## Try it

1. Import `tax` too. `una check .` reports U1004: `tax` is private to `shop.prices`. It also reports U7001: in canonical form, the imported names are in order.

## See also

- [Modules and imports](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#2-modules-and-imports)
