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

## `Map.update` (edition 0.4): `10-collections`, section 10.5

New section 10.5 "Changing one value of a map: `update`", after the maps; the sections after it are renumbered (10.5 to 10.10 became 10.6 to 10.11), and the one link from another chapter to the old 10.5 (`19-editions`) follows. The front matter gains edition `0.4`, the code U1002 and a `nav` label.

`scripts/check.py` does not accept these packages yet: it requires `una.toml` and `verification.lock`, refuses `ita.una` and `ita.lock` in a package, and refuses a block that shows `ita.una`. Edition `0.4` has no `una.toml` (`spec/30 §8` rule 1), so the script needs to learn the edition `0.4` layout before these steps can be checked; until then, `--fill` skips the block of `steps/25-update-forms/ita.una`, whose body was written by hand. Each `ita.lock` is the text `una ita lock` writes for a package with no dependency (`write_lock` in `crates/una-project/src/ita.rs`).

Outputs, derived from `spec/21 §2` rule 5 and the conformance case `runtime/map_update_run` (whose map rendering and `Err` rendering they follow):

- `10-collections/steps/24-wrong-key/expected/output.txt` (edition `0.2`; this one una 0.3.16 can already check)
- `10-collections/steps/25-update-forms/expected/output.txt`
- `10-collections/steps/26-update-report/expected/output.txt` (also confirm that `initial: []` takes its type from the map)
- `10-collections/steps/27-update-fails/expected/output.txt`

Diagnostics, with the message of `crates/una-check/src/types/collections.rs`:

- `10-collections/steps/28-update-name/expected/diagnostics.txt`, `rendered.txt` (U1002)
