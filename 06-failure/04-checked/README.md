---
learn: "6.4"
title: checked, and the escape budget
editions: ["0.2"]
codes: [U7003]
---

# 6.4 checked, and the escape budget

Some facts no proof can establish, such as whether a text is a valid phone number by a rule the verifier cannot see inside. `checked(v, p) else fail V` tests `p` when the program runs, and fails with `V` if it is false. It replaces a proof with a test, so it is an escape hatch, and `una.toml` budgets it per module.

## The program

- `una.toml` allows one `checked` per module.
- `src/phones.una` declares an opaque predicate and a refined kind over it, and checks two texts.

## What you should see

`una run .` prints one valid phone number and one malformed text.

## Try it

1. Set `checked_per_module = 0` in `una.toml`. `una check .` reports U7003: the module uses more `checked` than its budget allows.

## See also

- [`checked` and the escape budget](https://github.com/una-lang/una/blob/main/docs/guide/language/errors/checked.md)
