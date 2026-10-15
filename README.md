# Una by Example

Small, complete Una programs, one per page of the Learn section of the Una website. Each directory below a chapter is a package you can check and run as it is:

```sh
cd 01-hello/01-package
una check .
una run .
```

Every example is checked against the una release that `una.lock` names. `expected/` holds what that release prints or reports for it. Each `try/N` holds a change suggested on the page, with its own expected outcome.

## Layout

- `NN-chapter/README.md`: the chapter's page.
- `NN-chapter/MM-page/`: a page. It holds `README.md` (the page's text), `una.toml`, `verification.lock` and `src/`, the package. It also holds `expected/` and `try/`, which the checks use and `una` never reads.

## Checking

```sh
python3 -B scripts/check.py --una "$(command -v una)"
```

This needs Python 3 and the `una` of `una.lock`, with Z3 at the version its `verification.lock` pins on the path. `python3 -B scripts/check.py --self-test` checks the script itself and needs neither.

## Translations

Pages are translated into Brazilian Portuguese (`pt-br`) and Spanish (`es`) under `translations/<locale>/`, at the path of the English page: `translations/pt-br/01-hello/01-package/README.md` translates `01-hello/01-package/README.md`, and `translations/pt-br/01-hello/README.md` the chapter page. A translated page points to the same package: the code is never copied. The downloads stay in English.

A translation's front matter keeps the English page's `learn`, `editions` and `codes`, translates its `title`, and adds two fields:

- `source`: the SHA-256 of the English README it translates (`shasum -a 256 01-hello/01-package/README.md`).
- `status`: `draft`, or `approved` once a fluent speaker of the language has reviewed it.

`scripts/check.py` checks each translation against its English page:

- The same headings, with as many numbered items under each.
- The same code and links: every inline code span, every fenced block, every link target, reference definition and URL of the English page, no more and no fewer, and no HTML tag it does not have. Code stays in English, the comments inside fenced blocks included, and so do commands, identifiers, diagnostic codes and what a program prints. Only the prose around them is translated.
- An `approved` translation whose `source` is not the digest of the current English page fails the check: the English page changed after the review. Set it back to `draft` with the change, or review it again. A `draft` one is reported as out of date.

The website shows a translated page only when it is `approved` and its `source` matches; otherwise it shows the English page. A draft never appears on the website. The terms follow the glossaries of the website, one per language.

## Downloads

Each release of this repository is named after the una release it is checked against, such as `for-una-0.3.14`. It carries one archive per page, one archive of everything, and `SHA256SUMS`, all built by `python3 -B scripts/archive.py OUT`. `-B` keeps Python from writing bytecode into the repository, which `check.py` refuses.

## License

Apache-2.0. See `LICENSE`.
