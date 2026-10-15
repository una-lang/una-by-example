---
learn: "1.4"
title: Imprimir
editions: ["0.2"]
codes: [U2001]
source: b54383033a546d61df880b0a99094a1223f1c4460503452cbae1612349d3d3fa
status: draft
---

# 1.4 Imprimir

`Console.print` escreve uma linha de texto. Seu argumento é `Text`, e um valor de outro tipo entra no texto entre chaves. O console é uma capacidade: uma função só imprime quando seu cabeçalho diz `uses @console: Console[print]`, e `una run` só a fornece quando `una.toml` a concede.

## O programa

- `src/printing.una` imprime três linhas. A terceira põe no texto o `Int` associado a `lines`.

## O que você deve ver

`una run .` imprime:

```text
one line
and another
3 lines in all
```

## Experimente

1. Imprima o próprio `lines`, `@console.print(lines)`. `una check .` relata U2001: `print` recebe `Text`, e `lines` é um `Int`. Escrever `"{lines}"` o transforma em texto.

## Veja também

- [As capacidades do host](https://github.com/una-lang/una/blob/main/docs/guide/language/capabilities/host.md)
- [Texto](https://github.com/una-lang/una/blob/main/docs/spec/22-text.md)
