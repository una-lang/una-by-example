---
learn: "3.1"
title: Parâmetros, rótulos e resultados
editions: ["0.2"]
codes: [U2004, U2005]
source: 7ed7de8dce9374a699a9b592da6798863b879c81be9345f9d2e5cc783d1624c7
status: draft
---

# 3.1 Parâmetros, rótulos e resultados

O cabeçalho de uma função dá nome aos seus parâmetros, cada um com seu tipo, e ao tipo do seu resultado. Uma chamada passa o primeiro argumento como está e todos os outros com o nome do parâmetro, de modo que a chamada se lê daqui a um ano como no dia em que foi escrita. Uma variável com o nome do parâmetro não precisa de rótulo.

## O programa

- `src/area.una` declara `rectangle` e o chama duas vezes: uma com o rótulo `height:`, outra com uma variável chamada `height`.

## O que você deve ver

`una run .` imprime `12 and 20`.

## Experimente

1. Chame `rectangle(3, 4)`. `una check .` relata U2004: o segundo argumento precisa do seu rótulo. O diagnóstico traz a alteração que o adiciona, e `una fix .` a aplica.
2. Chame `rectangle(3, depth: 4)`. `una check .` relata U2005: `rectangle` não tem o parâmetro `depth`.

## Veja também

- [Chamadas e argumentos rotulados](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#44-calls-and-labeled-arguments)
