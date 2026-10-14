---
learn: "9.6"
title: "Testcase: a contact book that never prints a phone number"
editions: ["0.2"]
codes: [U4003]
---

# 9.6 Testcase: a contact book that never prints a phone number

This page combines the chapter: categories, a policy in a trusted module, and a loop that prints only what the labels allow. The checker proves that no name or phone number reaches the console except through the policy.

## The program

- `src/privacy.una` declares a policy that keeps only a name's initial.
- `src/book.una` prints each contact's initial and city.

## What you should see

`una run .` prints `A. in Recife` and `R. in Porto`.

## Try it

1. Print the phone instead of the city. `una check .` reports U4003: the phone is `secret[PII]`.

## See also

- [Policies and `via`](../04-policies/)
