---
learn: "2.2"
title: let e let edit
editions: ["0.2"]
codes: [U2019]
source: 920d2a7d4ab760b1bb006be740d90fea1e6c55804730e50ed0d49b5071181b2f
status: draft
---

# 2.2 let e let edit

`let` associa um nome a um valor uma única vez. Na edição `0.2`, `let edit` associa um nome que linhas posteriores podem reassociar com `name = value`. Não há referências: reassociar `total` muda apenas `total`.

## O programa

- `src/counter.una` começa `total` com o valor de `start` e depois o reassocia duas vezes.

## O que você deve ver

`una run .` imprime `total is 30`.

## Experimente

1. Declare `total` com `let` em vez de `let edit`. `una check .` relata U2019 nas duas linhas que o atribuem, e a mensagem diz como declará-lo.
2. Atribua `start = 6` depois de associá-lo. `start` foi associado com `let`, então isso também é U2019.

## Veja também

- [`let edit` e parâmetros `edit`](https://github.com/una-lang/una/blob/main/docs/guide/language/control-flow/let-edit.md)
