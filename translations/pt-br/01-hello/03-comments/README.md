---
learn: "1.3"
title: Comentários e comentários de documentação
editions: ["0.2"]
codes: [U0101]
source: 6fc1ce29695c7b81432fdac023f2cfa3a41fa9991366ac8f079b9692593915d9
status: draft
---

# 1.3 Comentários e comentários de documentação

Um comentário começa com `--` e vai até o fim da linha. Um comentário de documentação começa com `---` e pertence à declaração que vem depois dele: `una contract` o imprime com o cabeçalho da declaração, de modo que ferramentas e agentes também o leem. Não há comentários de bloco.

## O programa

- `src/notes.una` mostra um comentário comum no topo, um comentário de documentação em `days` e um comentário dentro do corpo de `main`.

## O que você deve ver

`una run .` imprime `a week has 7 days`.

## Experimente

1. Comece o primeiro comentário com `//` em vez de `--`. `una check .` relata U0101: `//` não é um comentário em Una.

## Veja também

- [A especificação: comentários](https://github.com/una-lang/una/blob/main/docs/spec/01-lexical-structure.md)
