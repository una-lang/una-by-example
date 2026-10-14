---
learn: "11.2"
title: The keys of una.toml
editions: ["0.2"]
codes: [U4007]
---

# 11.2 The keys of una.toml

`una.toml` describes the package: `[package]` its name, version and edition; `[run]` the entry module and its grants; `[labels]` the categories labels may name; `[escape_budget]` how many `checked` each module may use; and `[trusted]` the trusted modules. An unknown key is an error, so a typo never passes as a setting.

## The program

- `una.toml` uses four tables, with a comment on each.
- `src/settings.una` labels two fields with the declared categories.

## What you should see

`una run .` prints `one account`.

## Try it

1. Declare only `PII` in `una.toml`. `una check .` reports U4007: the category `Finance` is not declared.

## See also

- [`[package] edition`](https://github.com/una-lang/una/blob/main/docs/guide/configure/package/edition.md)
