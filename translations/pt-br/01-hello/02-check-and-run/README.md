---
learn: "1.2"
title: una check e una run
editions: ["0.2"]
codes: [U1001, U2001]
source: 3ebd2af57aeb3d904ae7851a608658aaf9e2c0e0aa4827d497b1e17cb4b96f12
status: draft
---

# 1.2 una check e una run

`una check .` lê o pacote e relata cada problema que encontra, cada um com um código e um lugar. Nada é executado. `una run .` executa o pacote, mas só quando a verificação não encontra problemas. Este programa chama uma pequena função e imprime seu resultado.

## O programa

- `src/greet.una` declara `double`, uma função de um `Int` que devolve um `Int`. Ela é privada: sem `pub`, só o seu módulo pode chamá-la.
- `main` associa o resultado de `double(21)` a um nome com `let` e depois o imprime. `{answer}` no texto põe o valor ali.

## O que você deve ver

`una check .` não relata nada, e `una run .` imprime `the answer is 42`.

## Experimente

1. Chame `double("21")`. `una check .` relata U2001 no argumento: `double` recebe um `Int`, e `"21"` é `Text`.
2. Chame `@console.show(...)` em vez de `@console.print(...)`. `una check .` relata U1001: `Console` não tem a operação `show`.

## Veja também

- [Primeiros passos](https://github.com/una-lang/una/blob/main/docs/guide/getting-started.md)
- `una explain U2001` imprime o que um código significa e como repará-lo.
