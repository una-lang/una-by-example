# Draft notes

The pages and packages listed here teach features that are on the compiler's `main` but in no released `una` yet. The book is pinned to una 0.3.16 (`una.lock`), which does not have them, so these parts are drafts. They merge only when the book moves to a release that has the features, in the pull request that adopts that release.

Every `expected/` file below was written by reasoning from the specification, the decision records, the conformance cases and the compiler's sources on `main`, not by running `una`. Before the merge, regenerate each one with a `una` built from `main` (or the release that adopts these features), compare, and fix the page text wherever a message, a column or an output line differs. Then delete this file.

## F64 (edition 0.3): `02-numbers`, sections 2.4 to 2.6

New sections 2.4 "Numbers with a fraction: `F64`", 2.5 "Converting and rounding" and 2.6 "Special values and comparing `F64`"; the sections after them are renumbered (2.4 to 2.8 became 2.7 to 2.11), and the one link from another chapter to the old 2.4 (`06-functions`) follows. The front matter gains edition `0.3`, the code U2033 and the new `nav` labels.

Outputs (`expected/output.txt`), derived from `spec/29` §3 to §7. The digits of every `F64` were computed with IEEE binary64 arithmetic in Python and printed by the rendering rule of `spec/29 §7` (shortest round-trip digits, positional for a decimal exponent from -6 to 20); that renderer was first checked against every rendering in `tests/conformance/runtime/float_run`.

- `02-numbers/steps/22-fraction-0-3/expected/output.txt`
- `02-numbers/steps/23-floats/expected/output.txt`
- `02-numbers/steps/24-parcel/expected/output.txt`
- `02-numbers/steps/26-conversions/expected/output.txt` (the `parse_f64` line follows the `ParseError` rendering of `float_run`: `Err(NotADigit(1))`)
- `02-numbers/steps/27-label/expected/output.txt`
- `02-numbers/steps/30-specials/expected/output.txt`
- `02-numbers/steps/31-scale/expected/output.txt`

Diagnostics (`expected/diagnostics.txt` and `expected/rendered.txt`). The messages and repairs are copied from `crates/una-check/src/types/float.rs` and `expr.rs`; the columns, the underline and the repair spans are counted by hand. Check in particular the span of each diagnostic (the whole comparison for U2033, the whole method call for `to_int`), and whether the trailing line "1 of 1 diagnostics have an edit ..." appears.

- `02-numbers/steps/25-float-integer/expected/diagnostics.txt`, `rendered.txt` (U2001, integer literal where `F64` is expected)
- `02-numbers/steps/28-int-operand/expected/diagnostics.txt`, `rendered.txt` (U2001, `Int` operand of an `F64` operator)
- `02-numbers/steps/29-to-int/expected/diagnostics.txt`, `rendered.txt` (U2001, `to_int` on `F64`)
- `02-numbers/steps/32-zero-compare/expected/diagnostics.txt`, `rendered.txt` (U2033)

Also to confirm with the built `una`: that every new step is in canonical form (`una fmt --check`), in particular `(-7.5).abs()`, `(-0.0).to_int_exact()` and the long header of `volumetric_kg`.

## `Map.update` (edition 0.5, moved from 0.4 by ADR 0139): `10-collections`, section 10.5

New section 10.5 "Changing one value of a map: `update`", after the maps; the sections after it are renumbered (10.5 to 10.10 became 10.6 to 10.11), and the one link from another chapter to the old 10.5 (`19-editions`) follows. The front matter gains edition `0.4`, the code U1002 and a `nav` label.

`scripts/check.py` does not accept these packages yet: it requires `una.toml` and `verification.lock`, refuses `ita.una` and `ita.lock` in a package, and refuses a block that shows `ita.una`. Edition `0.4` has no `una.toml` (`spec/30 §8` rule 1), so the script needs to learn the edition `0.4` layout before these steps can be checked; until then, `--fill` skips the block of `steps/25-update-forms/ita.una`, whose body was written by hand. Each `ita.lock` is the text `una ita lock` writes for a package with no dependency (`write_lock` in `crates/una-project/src/ita.rs`).

Outputs, derived from `spec/21 §2` rule 5 and the conformance case `runtime/map_update_run` (whose map rendering and `Err` rendering they follow):

- `10-collections/steps/24-wrong-key/expected/output.txt` (edition `0.2`; this one una 0.3.16 can already check)
- `10-collections/steps/25-update-forms/expected/output.txt`
- `10-collections/steps/26-update-report/expected/output.txt` (also confirm that `initial: []` takes its type from the map)
- `10-collections/steps/27-update-fails/expected/output.txt`

Diagnostics, with the message of `crates/una-check/src/types/collections.rs`:

- `10-collections/steps/28-update-name/expected/diagnostics.txt`, `rendered.txt` (U1002)

## Path dependencies (edition 0.4): `11-packages`, section 11.4

New section 11.4 "Path dependencies", after the manifest; the sections after it are renumbered (11.4 to 11.8 became 11.5 to 11.9). The subsection of 11.3 on dependencies is now "No dependencies before edition `0.4`" and points to 11.4. The front matter gains edition `0.4`, the codes U1010, U3021 and U7012, and a `nav` label.

What `scripts/check.py` must learn before these steps can be checked, besides the edition `0.4` layout of the `Map.update` notes:

- a package that holds another package under `deps/` (the path dependency, with its own `ita.una` and `src/`), copied whole into the fresh directory each command runs in;
- blocks that show `ita.una`, `ita.lock` and a dependency's `deps/<name>/src/*.una`, which `--fill` refuses today: their bodies in `11-packages/README.md` were written by hand from the files;
- the command `una ita lock` in an `sh` block (the page shows it once), and perhaps `ita lock --check .` as an `expected/commands/` file.

Each `ita.lock` follows `lock_command` in `crates/una-cli/src/ita.rs`. Its digest was computed by the listing of `spec/30 §9` rule 2 over the dependency's `ita.una` and `src/**/*.una`; confirm it with `una ita lock --check`. In `17-no-accept` and `18-beyond-ceiling` the lock is the one of the package before the change the step makes.

Outputs:

- `11-packages/steps/15-path-dependency/expected/output.txt`
- `11-packages/steps/16-path-grant/expected/output.txt`
- `11-packages/steps/19-path-as/expected/output.txt`

Diagnostics, with the messages of `crates/una-cli/src/package.rs` (U7012), `crates/una-check/src/names/mod.rs` (U1001, U1010) and `crates/una-check/src/types/crossing.rs` (U3021), following the conformance cases `project/ita_path_dep_*`. Check the span of U7012 (taken here as the need's first line, from `tags` to the end of the path) and the order of the diagnostics:

- `11-packages/steps/17-no-accept/expected/diagnostics.txt`, `rendered.txt` (U7012, then U1001 three times)
- `11-packages/steps/18-beyond-ceiling/expected/diagnostics.txt`, `rendered.txt` (U3021 twice)
- `11-packages/steps/20-local-clash/expected/diagnostics.txt`, `rendered.txt` (U1010)

## Unclear points to settle before merge

- The U3021 message for a path dependency says "whose ceiling in `una.toml` allows no operation of `Console`", since the boundary code builds one message for both kinds of ceiling. In edition `0.4` the ceiling is the `may` lines of `ita.una`, so the message may change; the page quotes it only through `rendered.txt`.
- `spec/30 §4` rule 4 still says that `una ita lock` refuses a package with `needs`, while §3 rule 4, §12 and the code lock path dependencies.
- The page states that the path of a need is relative to the package and may lie inside it, as `deps/tags` does here (as in the conformance cases); `spec/30 §12` rule 1 excludes only the package itself and its `src/`.
