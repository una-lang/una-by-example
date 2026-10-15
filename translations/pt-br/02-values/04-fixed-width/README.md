---
learn: "2.4"
title: Inteiros de largura fixa
editions: ["0.2"]
codes: [U2022, U5001]
source: 8c2004ba7856f962ce3955fe171bfc4382bf1148c3ed20332b6411e646562a8e
status: draft
---

# 2.4 Inteiros de largura fixa

`Int` nunca transborda, então a maior parte do código o usa. Onde a largura importa, em bytes, protocolos ou hashes, a edição `0.2` tem de `I8` a `I64` e de `U8` a `U64`. Uma operação que poderia sair do intervalo é uma obrigação de prova: o verificador prova que ela fica no intervalo, ou o programa é rejeitado. O transbordamento nunca acontece em tempo de execução.

## O programa

- `src/bytes.una` soma dois valores `U8`. Seus dois `requires` limitam cada um a no máximo 100, então a soma cabe em um `U8`, e o verificador prova isso.
- `to_int()` transforma um `U8` em um `Int`, para imprimi-lo.

## O que você deve ver

`una run .` imprime `155`.

## Experimente

1. Permita `a` até 200: `requires a <= 200`. `una check .` relata U5001: agora a soma pode transbordar, e o contraexemplo dá dois valores cuja soma passa de 255.
2. Associe `small` a `300`. `una check .` relata U2022: o literal não cabe em um `U8`.

## Veja também

- [Inteiros de largura fixa, na especificação](https://github.com/una-lang/una/blob/main/docs/spec/18-fixed-width-integers.md)
