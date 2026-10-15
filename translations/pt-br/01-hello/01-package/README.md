---
learn: "1.1"
title: Um pacote
editions: ["0.2"]
codes: [U3004, U7001]
source: 280975f1c9d962322d53760ac381292426d0175cf53b750486f7a26923fb7357
status: draft
---

# 1.1 Um pacote

Todo programa Una é um pacote: um diretório com `una.toml`, `verification.lock` e seus módulos em `src/`. Este imprime uma linha. Sua única função, `main`, também declara no cabeçalho a única coisa que pode fazer: imprimir no console.

## O programa

- `una.toml` dá nome ao pacote e escolhe a edição `0.2`. Sua tabela `[run]` diz que `una run` começa pelo módulo `hello` e lhe concede o console.
- `verification.lock` fixa o solucionador que prova os contratos do pacote, para que uma prova signifique o mesmo em qualquer máquina. Todo pacote tem um; este é igual ao de todos os exemplos.
- `src/hello.una` contém o módulo `hello` e sua função `main`. A linha `uses @console: Console[print]` faz parte do cabeçalho: `main` pode chamar a operação `print` da capacidade `Console`, e nada mais.

## O que você deve ver

`una run .` imprime `Hello, Una`.

## Experimente

1. Troque o texto por `"Hello again, Una"`. `una run .` imprime a nova linha.
2. Apague a linha `uses @console: Console[print]`. Agora `una check .` relata U3004: `main` usa `@console`, mas seu cabeçalho não declara nenhum `uses`. Também relata U7001, porque um cabeçalho sem cláusulas se escreve em uma só linha na forma canônica, o que `una fmt` faria por você.

## Veja também

- [A cláusula `uses`](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/uses.md)
- [As capacidades do host](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/host.md)
- [`[run] grants`](https://github.com/una-lang/una/blob/main/docs/guide/configure/run/grants.md)
