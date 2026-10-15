---
learn: "2.1"
title: Int, Bool, Text e literais
editions: ["0.2"]
codes: [U2001]
source: 672143ac1e30c34b7a7cebd9ee41f86348c8d63cf6c581f7696e59e22598f96e
status: draft
---

# 2.1 Int, Bool, Text e literais

Um `Int` é um número inteiro de qualquer tamanho: ele nunca transborda, então `9000000000 * 9000000000` é exato. Um `Bool` é `true` ou `false`. Um `Text` é uma sequência de caracteres UTF-8 entre aspas duplas. Cada valor tem um só tipo, e nada se converte de um tipo para outro a menos que o código diga isso.

## O programa

- `src/literals.una` associa quatro valores a nomes com `let` e os imprime. Chaves dentro de um texto põem um valor ali, seja qual for o seu tipo.

## O que você deve ver

`una run .` imprime os quatro valores.

## Experimente

1. Associe `ready` a `1` em vez de `true` e use-o com `and`. `una check .` relata U2001: `and` recebe operandos `Bool`, e `1` é um `Int`. Em Una, números não valem como verdadeiro ou falso.

## Veja também

- [Tipos embutidos](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#31-built-in-types)
