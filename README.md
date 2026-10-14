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

## Downloads

Each release of this repository is named after the una release it is checked against, such as `for-una-0.3.14`. It carries one archive per page, one archive of everything, and `SHA256SUMS`, all built by `python3 -B scripts/archive.py OUT`. `-B` keeps Python from writing bytecode into the repository, which `check.py` refuses.

## License

Apache-2.0. See `LICENSE`.
