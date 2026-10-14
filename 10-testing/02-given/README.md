---
learn: "10.2"
title: given, failures, and what an example performs
editions: ["0.2"]
codes: []
---

# 10.2 given, failures, and what an example performs

`given @x = h(...)` installs a handler for one example, so a test never touches the real world, and examples cannot use host capabilities at all. `expect fails V` checks a failure, and `expect performed @x.op` or `expect not performed @x.op` checks which operations ran.

## The program

- `src/orders.una` mails a confirmation only for an item that could be reserved. Two examples check both cases with fake stock and a fake mailbox.

## What you should see

`una run .` prints a reminder, and `una test .` reports both examples passing.

## Try it

1. Mail the confirmation before reserving the item. The program still checks, but `una test .` reports the out-of-stock example failing: the mail was sent.

## See also

- [`example`](https://github.com/una-lang/una/blob/main/docs/guide/language/examples/example.md)
