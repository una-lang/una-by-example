---
learn: "3.3"
title: if como expressão
editions: ["0.2"]
codes: [U2001]
source: edff9c3f8b46706bbbfe2e9f60f53417023b79488691673a5e045bdda1655b0d
status: draft
---

# 3.3 if como expressão

`if` dá um valor: os dois ramos têm um, do mesmo tipo. Em uma linha, ele se lê `if c then a else b`. Em várias linhas, cada ramo é um bloco, e o valor de um bloco é sua última linha. `else if` encadeia os casos.

## O programa

- `src/parity.una` classifica um número como par ou ímpar com um `if` de uma linha e depois o descreve com uma cadeia em várias linhas.

## O que você deve ver

`una run .` imprime três descrições.

## Experimente

1. Faça o ramo `else` de `parity` dar `1` em vez de `"odd"`. `una check .` relata U2001: os ramos de um `if` precisam ter o mesmo tipo.

## Veja também

- [`if`](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#52-if)
