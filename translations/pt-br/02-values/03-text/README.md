---
learn: "2.3"
title: Texto e interpolação
editions: ["0.2"]
codes: [U5001]
source: 05f045f5fab2726a44bc488a10e59ccf3534a9274a36951eed5045ae6160f7ef
status: draft
---

# 2.3 Texto e interpolação

Um `Text` tem um comprimento, `len`, e o prelúdio lhe dá funções: `to_upper`, `split`, `join`, `slice`, `contains_text` e outras. Uma função de um só argumento se lê como um campo: `line.to_upper` é `to_upper(line)`. Dentro de um texto, `{name}` põe um valor ali.

## O programa

- `src/words.una` conta os caracteres e as palavras de uma linha, a imprime em maiúsculas e junta suas palavras com `/`.

## O que você deve ver

`una run .` imprime três linhas.

## Experimente

1. Divida por `""` em vez de `" "`. `split` exige um separador que não seja vazio, e `una check .` relata U5001: a pré-condição é refutada antes mesmo de o programa ser executado.

## Veja também

- [Texto, na especificação](https://github.com/una-lang/una/blob/main/docs/spec/22-text.md)
