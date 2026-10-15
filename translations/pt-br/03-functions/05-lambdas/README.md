---
learn: "3.5"
title: Lambdas e valores de função
editions: ["0.2"]
codes: [U2010]
source: 8f2708d1e39a3f9e726d88cffd8b32211285151542fc6b64a976c96674c0d351
status: draft
---

# 3.5 Lambdas e valores de função

Uma função é um valor: pode ser passada a um parâmetro de tipo função, como `fn(Int) -> Int`. Uma lambda, `fn(params) -> body`, é uma função escrita onde é usada, com um corpo de uma linha. Os tipos dos seus parâmetros vêm do parâmetro ao qual ela é passada.

## O programa

- `src/lambdas.una` passa uma função nomeada e uma lambda para `twice`, que chama duas vezes a função que recebe.

## O que você deve ver

`una run .` imprime `7 200`.

## Experimente

1. Associe uma lambda a um nome com `let`, sem usá-la: `let keep = fn(n) -> n + 1`. `una check .` relata U2010: nada diz qual é o tipo de `n`, e a mensagem pede uma anotação, `n: Int`.

## Veja também

- [Lambdas e tipos de função](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#46-lambdas-and-function-types)
