---
learn: "3.4"
title: pub, e os cabeçalhos que uma função privada infere
editions: ["0.2"]
codes: [U3004]
source: 314b16c1e4a8a8e6467ed05eb11d68bababe15cd6fadf1c50872afe61f407bc2
status: draft
---

# 3.4 pub, e os cabeçalhos que uma função privada infere

Uma declaração sem `pub` é privada ao seu módulo. Uma função privada pode omitir `uses` e `fails`: o compilador os infere, e `una contract` imprime o cabeçalho que ele inferiu. Uma função `pub` é a fronteira revisada de um módulo, por isso declara tudo o que pode fazer.

## O programa

- `src/visibility.una` tem uma `shout` privada que imprime sem dizer isso no seu cabeçalho. `main` declara a capacidade, e `shout` a recebe.

## O que você deve ver

`una run .` imprime `INFERRED`.

## Experimente

1. Torne `shout` pública. `una check .` relata U3004: uma função pública que usa `@console` precisa declará-lo.

## Veja também

- [Visibilidade e inferência](https://github.com/una-lang/una/blob/main/docs/guide/syntax-reference.md#43-visibility-and-inference)
