---
learn: "3.2"
title: A forma curta e a forma longa
editions: ["0.2"]
codes: [U7001]
source: 57f0e9101bb935dd677e4dcfad9da3054bb480f2f4896d3e4831dfd19181e658
status: draft
---

# 3.2 A forma curta e a forma longa

Uma função sem cláusulas e com corpo de uma linha se escreve em uma só linha: `square(n: Int) -> Int = n * n`. Qualquer outra função usa a forma longa: o cabeçalho e suas cláusulas, depois `=` sozinho na sua linha, depois o corpo, indentado. Cada função tem exatamente uma forma canônica, e `una fmt` a escreve.

## O programa

- `src/forms.una` escreve `square` na forma curta, e `triple` na forma longa, já que ela tem uma cláusula `ensures`.

## O que você deve ver

`una run .` imprime `16 15`.

## Experimente

1. Escreva `square` na forma longa. `una check .` relata U7001: a forma canônica de uma função sem cláusulas e com corpo de uma linha é a curta. `una fmt .` a reescreve.

## Veja também

- [Duas formas](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#41-two-forms)
