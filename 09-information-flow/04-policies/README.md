---
learn: "9.4"
title: Policies and via
editions: ["0.2"]
codes: [U4003]
---

# 9.4 Policies and via

A label is lowered only through a policy: it names what it lowers, to what, through which function (`via`), for what purpose, and who owns it. A policy lives in a trusted module, and its `via` function is private, so the policy is the only way in. Every call of a policy is listed in the build report.

## The program

- `src/masks.una` is a trusted module with a policy that shows only the last two digits of a phone number.
- `src/app.una` prints a receipt through the policy.

## What you should see

`una run .` prints the receipt with a masked number.

## Try it

1. Print the phone itself. `una check .` reports U4003: the console accepts `public` data, and the phone is `secret[PII]`.

## See also

- [`policy`](https://github.com/una-lang/una/blob/main/docs/guide/language/information-flow/policy.md)
