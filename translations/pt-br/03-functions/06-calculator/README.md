---
learn: "3.6"
title: "Caso de estudo: uma pequena calculadora"
editions: ["0.2"]
codes: [U5001]
source: d5be5c7cd9495606df13c836406ee53257ffcd2523818fe7f66c703833ff1f90
status: draft
---

# 3.6 Caso de estudo: uma pequena calculadora

Esta página junta o que o capítulo mostrou: funções com parâmetros rotulados, cadeias de `if` e uma função passada como valor.

## O programa

- `src/calculator.una` escolhe uma operação pelo nome e imprime o maior de dois números com uma lambda passada a `report`.

## O que você deve ver

`una run .` imprime três linhas.

## Experimente

1. Faça uma operação desconhecida dividir, `a / b`, em vez de dar `0`. `una check .` relata U5001: `b` pode ser zero, e uma divisão por zero não é permitida nem mesmo em um ramo que nenhum teste alcança.

## Veja também

- [Contratos e o verificador](../../07-contracts/#s7-1)
