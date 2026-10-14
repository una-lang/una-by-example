---
learn: "10.3"
title: Requirements and una trace
editions: ["0.2"]
codes: [U5001]
---

# 10.3 Requirements and una trace

A `requirement` records an intent in words, with where it came from, who owns it, and whether it is active. `derived from` in a function's header ties its contract to the requirement, and `una trace` shows the chain: the requirement, the contracts derived from it, and whether each is proven.

## The program

- `src/tickets.una` states a requirement, and a function whose `ensures` clause is derived from it.

## What you should see

`una run .` prints `sold out`, and `una trace SOLD_OUT_1` shows the requirement and its proven contract.

## Try it

1. Show an event as sold out only below zero seats. `una check .` reports U5001: the contract derived from the requirement no longer holds.

## See also

- [`requirement` and `derived from`](https://github.com/una-lang/una/blob/main/docs/guide/language/requirements/requirement.md)
