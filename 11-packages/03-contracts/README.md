---
learn: "11.3"
title: Locked contracts (0.3 preview)
editions: ["0.3"]
codes: [U3023]
---

# 11.3 Locked contracts (0.3 preview)

A condition in a header protects only while it stays there, and an edit could delete it. In edition `0.3`, `[contracts]` in `una.toml` locks the `uses` of a public function: a header weaker than its lock is an error, so weakening it takes a change to `una.toml`, which is reviewed apart.

## The program

- `una.toml` locks `charge`'s condition on `print`.
- `src/billing.una` keeps the condition, and guards the operation to match it.

## What you should see

`una run .` prints `charged 30` only: the second call is a dry run.

## Try it

1. Drop `where not dry_run` from `charge`'s header. `una check .` reports U3023: the header lets `print` run where the lock forbids it, and the counterexample says when.

## See also

- [Conditions on operations](../../08-capabilities/05-conditions/)
