---
learn: "5.7"
title: "Testcase: word frequencies"
editions: ["0.2"]
codes: []
---

# 5.7 Testcase: word frequencies

This page combines the chapter: a text split into words, a map from each word to its count, and a loop over the map's entries, which come in key order.

## The program

- `src/frequencies.una` counts the words of a sentence and prints each with its count.

## What you should see

`una run .` prints one line per word, in alphabetical order.

## Try it

1. Count `"The cat saw the dog"`. The output has both `The` and `the`: words are compared exactly, so case matters.

## See also

- [`for`](../02-for/)
