---
learn: "9.3"
title: Categories
editions: ["0.2"]
codes: [U4001]
---

# 9.3 Categories

A label may name categories, kinds of sensitive data: `secret[PII] Text`. `una.toml` declares the categories a package uses. A label flows into another only if its level is lower or equal and its categories are among the other's, so personal data never loses its category by accident.

## The program

- `una.toml` declares the category `PII`.
- `src/contacts.una` keeps each contact's phone as `secret[PII] Text`, and prints only names and a count.

## What you should see

`una run .` prints the names, then how many phone numbers are kept secret.

## Try it

1. Return the phones as `List[secret Text]`. `una check .` reports U4001: that would drop the category `PII`.

## See also

- [`[labels] categories`](https://github.com/una-lang/una/blob/main/docs/guide/configure/labels/categories.md)
