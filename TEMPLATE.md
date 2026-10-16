# Chapter template 2

A chapter on template 2 is one long page that teaches one idea of Una through a program the reader builds. Every block of code, output and diagnostic on it comes from a package that `scripts/check.py` checks against the pinned `una`, so nothing on the page is typed by hand.

A chapter opts in with exactly `template: 2` in the front matter of its `README.md`. A chapter stays on template 1 (the fixed parts `The program`, `What you should see`, `Try it` and `See also`, one directory per page) only while its `README.md` has no front matter and no code block, it has page directories, and it has none of `steps/`, `day-to-day/`, `mistakes/` or `exercises/`. Anything in between fails the check: a front matter that does not parse, `template` with another value or spelling (`template: 02`, `Template: 2`), or template 2 directories without `template: 2`. Pages use LF line ends; a carriage return fails. The chapter's `README.md` is a plain file: a symbolic link fails.

## Files

```text
NN-chapter/
  README.md                 the page, in English
  steps/01-<slug>/          one package per example in the text, in order
    una.toml  verification.lock  src/  expected/
  steps/02-<slug>/ ...
  day-to-day/               the chapter's program, a package with examples
  mistakes/N/               one per common mistake: an overlay with expected/diagnostics.txt
                            and expected/rendered.txt
  exercises/N/start/        where the exercise starts: an overlay holding the exercise's
                            example, which fails
  exercises/N/answer/       the answer: checks clean, runs, and passes `una test`
  exercises/N/<slug>/       any other state the exercise shows, such as a diagnostic on the way
translations/<locale>/NN-chapter/README.md
                            a translation of the page; the packages are never copied
```

Each directory under `steps/`, `day-to-day/`, `mistakes/` and `exercises/` is one of:

- **A package**: `una.toml`, `verification.lock` and `src/`, as in template 1.
- **An overlay**: a file `base.txt` whose one line names a package of the chapter (`day-to-day`, `steps/02-handling`), and the files that replace that package's, at the same paths (`src/orders.una`). An overlay's base is always a package, never another overlay. An overlay with no files of its own (only `base.txt`) is that package, and has no `expected/`.

A package or overlay holds only these files: `una.toml`, `verification.lock`, `base.txt` (in an overlay), `src/**/*.una`, and in `expected/` the files below. Anything else fails, and so does a symbolic link anywhere in the chapter.

Every package and every overlay with files of its own has `expected/`, checked as template 1 checks a page's:

| File | What it holds |
| --- | --- |
| `expected/output.txt` | What `una run .` prints, byte for byte. The package then also checks clean at tier 1 and is in canonical form (`una fmt --check`). |
| `expected/diagnostics.txt` | Instead of `output.txt`: the lines `una check` reports, `error <code> at <file>:<line>:<col>: <message>`, each followed by its counterexample line when it has one. |
| `expected/rendered.txt` | What `una --color never check .` prints on stderr, as a reader sees it in a terminal, after the normalization below. Every mistake has one. |
| `expected/commands/<name>.txt` | A further command: `$ una <args>` on the first line, then what it prints on stdout, byte for byte. `<name>` is lowercase letters, digits and dashes. |

**Commands.** A command is one of: `check .`, `test .`, `run .`, `build .`, `report .` and `obligations .` (each optionally after `--json`), `fmt --check .`, `fix --dry-run .`, `explain U1234`, `trace NAME` and `contract NAME` (optionally after `--json`). No other argument, no `--grant`, and no path but `.`.

**What `una` may do.** `una` runs with a minimal environment: `PATH`, a `HOME` and `TMPDIR` of its own, fresh for each run, `LANG=C.UTF-8` and `NO_COLOR=1`, nothing else. A package's `una.toml` holds only the tables `[package]`, `[run]`, `[escape_budget]`, `[labels]`, `[trusted]`, `[boundaries]` and `[contracts]`; `[package]` holds only `name`, `version` and `edition`; `[run]` holds only `entry` and `grants`; and the grants are `console`, `clock` and `files:src:<access>` or `files:src/<dir>:<access>`, where `<access>` is `read`, `write` or `read,write`. No environment, no network, no files outside the package's `src/`. Each command runs on a fresh copy of the package, so what one writes never reaches another.

**Normalization of `rendered.txt`.** The checks run each package in a fresh copy, at a path that changes on every run. Before comparing, the output is normalized: CRLF becomes LF; the copy's absolute path followed by `/` is removed, and where it stands alone it becomes `.`; spaces and tabs at the end of a line are removed; blank lines at the end are removed, and the text ends with one newline. Write `rendered.txt` already normalized. Only stderr counts: in the package, run `una --color never check . 2>&1 >/dev/null`, and remove the spaces at the ends of lines.

## Front matter

```yaml
---
learn: "6"
title: Failure
editions: ["0.2"]
codes: [U0101, U0102, U2001, U2007, U3007, U3008, U3009, U3013]
time: 35
builds: An order-intake step that accepts or rejects each line of an order batch
prerequisites: ["3", "4", "5"]
template: 2
---
```

- The fields are exactly these, one `key: value` line each, with no blank line.
- `learn` is the chapter's number, as its directory says.
- `codes` is the union of the codes of every `expected/diagnostics.txt` in the chapter.
- `time` is the reading time in minutes, without the exercises.
- `builds` describes the day-to-day program in one line.
- `prerequisites` lists the numbers of earlier chapters the reader needs.
- `template: 2` turns on the rules of this document.

A translation keeps `learn`, `editions`, `codes`, `template`, `time` and `prerequisites`, translates `title` and `builds`, and adds `source` and `status` as in template 1.

## Parts, in order, with target lengths

The headings are fixed. `N` is the chapter's number, and the numbered parts count up from `N.1` with no gap.

| # | Part (heading) | Required content | Target |
| --- | --- | --- | --- |
| 0 | Front matter | As above | n/a |
| 1 | `# N <title>` and the lead | One paragraph: the problem this chapter solves in a working program | 60–120 words |
| 2 | `## What you'll build` | The day-to-day program's output, included from `day-to-day/expected/output.txt`, and 3 to 5 "you will learn" bullets | 80–150 words |
| 3 | `## Why it works this way` | The motivation: what goes wrong in languages without this, what Una guarantees instead, stated concretely and without polemic | 150–300 words |
| 4 | `## N.1 <concept>` to `## N.k <concept>`, k from 3 to 6 | One idea per section: explanation, then a step package with a walkthrough, then its output. Examples grow in difficulty: a minimal use, then a second use of the same idea in context. A decision table where alternatives exist | 300–700 words each, 1 to 3 blocks each |
| 5 | `## N.k+1 Day-to-day: <program>` | The program in the shared store domain, 80 to 200 lines. Shown in parts with walkthroughs, then whole (collapsed), then run, then tested | 600–1,200 words |
| 6 | `## N.k+2 Testing it` | The chapter's idea under `una test`: examples, fakes, the failure paths | 200–400 words |
| 7 | `## N.k+3 Common mistakes` | 4 to 8 items: the wrong code (a diff), the real diagnostic, why it happens, the fix, and a link to the code's page | 60–120 words each |
| 8 | `## N.k+4 For agents` | 3 to 6 lines: the JSON shape of this chapter's diagnostics, the repairs `una fix` can apply, the compact rule | 60–120 words |
| 9 | `## N.k+5 Exercises` | 3 to 5: one direct, one that extends the day-to-day program, one stretch. Each has a goal, a hint, a collapsed answer, and the command that checks it | 80–200 words each |
| 10 | `## N.k+6 Recap` | 5 to 8 bullets, each a rule the reader can apply | 80–150 words |
| 11 | `## N.k+7 Reference` | Links to the construct pages, std items, error codes and specification sections, all on the site, at the release | list |

Totals: 3,000 to 5,000 words of prose, 150 to 350 lines of code across all blocks, 25 to 40 minutes to read, 60 to 90 minutes with the exercises. A page longer than the site's page budget (40 KiB gzip) splits in two.

`### ` headings may be used inside any part. No other `## ` heading may appear. Every heading is a `#` line at column 0, outside quotes and lists; an underlined (setext) heading fails, so put a blank line before a `---` rule.

Rules:

- Every output, diagnostic and number shown comes from an `expected/` file.
- Identifiers are real words from the domain. Never `demo`, `foo`, `A`, `B` or `Oops`.
- The prose never cites a specification section inline. Citations go in Reference.

## Blocks are includes

The page has no free-floating code. Every fenced block names, in its info string, the file it shows, and its body is that file's text, exactly. The page therefore reads the same in any Markdown viewer, on the site, and as the `.md` twin an agent reads, and `check.py` fails the moment a package and its page disagree.

| Write | Shows |
| --- | --- |
| ```` ```una include="steps/01-quantity/src/quantity.una" ```` | The whole file. |
| ```` ```una include="day-to-day/src/orders.una#check_stock" ```` | One top-level declaration, with its doc comment. |
| ```` ```una include="day-to-day/src/orders.una#reason..describe" ```` | From one declaration to the end of another, everything between included. |
| ```` ```text include="day-to-day/expected/output.txt" ```` | An expected file: `output.txt`, `diagnostics.txt`, `rendered.txt` or a command. |
| ```` ```text include="mistakes/2/expected/rendered.txt#L1" ```` | Lines of a file: `#L3` or `#L3-L9`; on an expected file also an ascending list such as `#L1,L8-L9`. Use this to trim a long diagnostic to its message line. |
| ```` ```diff include="day-to-day..mistakes/1:src/orders.una" ```` | A unified diff of one file between two packages (`a/` and `b/` prefixes, 3 lines of context; `context="1"` changes it). |
| ```` ```toml include="steps/04-checked/una.toml" ```` | A manifest. |

A block shows only `una.toml`, `src/**/*.una` and the expected files. Paths are relative to the chapter's directory, with no `..`. An include of an overlay's file that the overlay does not replace shows its base's file.

**Where blocks go.** Every block starts at column 0, outside quotes and lists; it may sit inside `:::` containers. These fail, since Markdown renders each as code the check would not compare:

- a fence inside a callout (`> [!NOTE]`) or a list item, and a tilde fence that is not an include;
- a line indented by 4 or more spaces, a list or quote marker followed by 5 or more spaces (`-     text`), and a tab in any indentation;
- a `$$` line, which the site renders as a block.

Indent list items by 2 or 3 spaces, put one space after a marker, and nest lists one level at most. A fence closes on a line of its backticks or tildes followed by nothing but spaces or tabs.

**Plain characters.** Outside the bodies of includes, the page holds no invisible or control characters: no no-break space, no other Unicode space but the plain one, no zero-width or format character, no line or paragraph separator, and no control character but the tab.

**Declarations.** A top-level line is a line at column 0 that is not blank and does not start with `=` (the `=` that opens a function body is part of its declaration). A declaration starts at its name's top-level line, or at the `---` doc comment lines right above it, and ends before the next top-level line, without the blank lines at its end. The name is the first word after `pub`, `trusted`, `kind`, `capability`, `handler`, `predicate`, `opaque`, `measure` and the like: `main` in `pub main() -> Unit`, `Inventory` in `pub capability Inventory`. A plain `--` comment at column 0 ends the declaration above it and belongs to none. Examples, `module` lines and names declared twice cannot be named; include them by lines.

**Filling the blocks.** Write the fence line with an empty body, then run

```sh
python3 -B scripts/check.py --fill
```

It writes the body of every include, on the English page and its translations, from the packages. It needs no `una`, it changes nothing else, and it never writes through a symbolic link.

**Attributes.** Every value is quoted, `key="value"`, and each key appears once.

| Attribute | Meaning |
| --- | --- |
| `include="…"` | The file the block shows, as above. |
| `title="src/orders.una"` | The path shown in the block's header: the include's path, chapter-relative (`day-to-day/src/orders.una`) or inside its package (`src/orders.una`); for a diff, its file. |
| `caption="the kinds and the service"` | A short label after the title. It is prose: a translation translates it. |
| `verified="check, run, test"` | The badges, only on a block of `una.toml` or a `src/` file, whole or by declaration (not on lines or a diff). Each is checked: `check` needs the package to check clean, `run` needs its `expected/output.txt`, and `test` runs `una test .` on it, which must pass. A block from a mistake has no `verified`. |
| `mistake="wrong"` or `mistake="right"` | The two sides of a `:::pair`. |
| `context="N"` | The lines of context of a diff. |

Any other attribute fails the check, so a misspelt `include` does not pass unnoticed.

**Blocks written by hand.** Only plain `sh` blocks (```` ```sh ````, no attributes) of commands the reader types, one per line, with no `$` prompt and no output: `una <command>` with a command from the list above, `cd <path>` or `mkdir <path>` with one plain path, or `python3 -B scripts/check.py` alone, with `--fill` or with `--self-test`. Every other block, `text` and `json` included, is an include; output comes from `expected/commands/`.

**Translations.** A translation holds the same blocks, in the same order, byte for byte, with the same includes and bodies, and the same `:::` containers in the same order: only the prose, the `caption` values and the summary after `:::answer` change. `--fill` keeps the blocks in step with the English page.

## Mistakes and exercises

- A chapter has at least 4 `mistakes/N` (more than 8 is reported), numbered from 1. Each has `expected/diagnostics.txt` and `expected/rendered.txt`. The Common mistakes part has one `:::mistake` card per directory, in order: card `k` shows `mistakes/k/expected/rendered.txt` (whole or by lines), usually a diff from its base, and nothing of another mistake.
- A chapter has 3 to 5 `exercises/N`, numbered from 1, each with `start/` and `answer/`. The Exercises part has one `::::exercise` card per directory, in order: card `k` holds a `:::answer` with a block of `exercises/k/answer`, and nothing of another exercise.
- `start/` holds the exercise's example, and `una test .` fails on it: that is what tells the reader the exercise is not done yet. It is usually an overlay of the day-to-day program with the example added. An answer changes something (it is not only a `base.txt`), checks clean, prints its `expected/output.txt` under `una run`, and passes `una test .`.

## Links

Links point to the site's own pages at the release: a root-relative route such as `/docs/errors/U3007/`, or an anchor on the page such as `#what-youll-build`. A link to a file of the una-lang repositories on GitHub (`/blob/`, `/tree/`, `raw.githubusercontent.com`) fails, since those files change after the release; so does a relative link such as `../05-collections/README.md`, which resolves on GitHub but not on the site, and an `http://` link. The host is matched in any case and with any port. Other `https://` links are allowed.

## Components

The page uses Markdown and a small set of markers that the site renders. Raw HTML fails, and so does a container or callout not in this table (the site knows a `:::demo` container for its own gallery; Learn pages do not use it).

| Write | Get | Part |
| --- | --- | --- |
| front matter `time`, `editions`, `prerequisites`, `codes` | a strip under the title: reading time, edition, linked prerequisite chapters, code chips | 0, 1 |
| first paragraph after `# N <title>` | the lead paragraph | 1 |
| `:::build` … `:::` | the "What you'll build" card. The paragraph before the list becomes its label, and the list gets checks | 2 |
| `> [!KEY]` | the key-idea pull quote, one per chapter | 3 |
| `:::steps` around a code block and a numbered list | numbered steps. A step that opens with bold code is tied to that code's line | 3, 4, 5 |
| `> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!SECURITY]`, with an optional title after the marker | a callout with an icon, a color and a title line | 4, 5 |
| ```` ```una include="…" title="…" caption="…" verified="check, run" ```` | a code block with a header: path, caption, check badges, language and Copy | 4, 5, 6 |
| ```` ```text include="…/expected/output.txt" ```` | output in a terminal look | 2, 4, 6 |
| ```` ```text include="…/expected/rendered.txt" ```` | a diagnostic: accent color, linked code, Help and Note lines | 7, 9 |
| `:::decide` around `**Which to use:**` and a table | a decision table, read as "want → use" | 4 |
| `:::mistake` | a mistake card: the bold lead is its title, then the diagnostic, then the rows | 7 |
| `*Why:*`, `*Fix:*`, `*Hint:*` opening a paragraph | a labeled row | 7, 9 |
| `:::pair` around blocks with `mistake="wrong"` and `mistake="right"` | before and after, side by side | 7 |
| `:::agents` | the machine panel | 8 |
| `::::exercise` holding `:::hint` and `:::answer <summary>` | an exercise card, a hint box, and a collapsed answer | 9 |
| `:::recap` | a checklist of rules | 10 |
| `:::reference` | a quiet index list | 11 |
| `` `code` `` | a chip, colored by what it holds: keyword, kind, capability, command or path | all |
| `U1234`, in text or in backticks | a chip linked to the code's page | all |
| `[[Ctrl]]` | a keyboard key | all |

A container that holds others uses more colons (`::::exercise` around `:::hint`), and every container is closed by a line of as many colons. A `:::` line starts at column 0, outside quotes and lists, with the name right after the colons: `:::mistake`, not `::: mistake`.

## What `check.py` checks on a template 2 chapter

Failures:

1. The chapter is exactly on template 2 or exactly on template 1, as above.
2. The chapter directory holds only `README.md`, `steps/`, `day-to-day/`, `mistakes/` and `exercises/`, laid out as above, with only the allowed files and no symbolic link.
3. Every package and overlay has an allowed `una.toml` and the outcome in its `expected/`; its commands are allowed and print what they say; its `rendered.txt` is what `una` prints, normalized.
4. The front matter has exactly its fields; `learn` matches the directory; `codes` are the codes the outcomes show.
5. The parts are the ones above, in order, numbered without gaps, with 3 to 6 concept sections, and the markup is strict: no code outside the blocks the check reads (no `$$` line, no indented code, no fence inside a quote or list), no invisible or control character, no setext heading, no raw HTML, only the template's containers and callouts, at column 0.
6. Every fenced block is an include (or a plain `sh` block of commands); its include resolves; its body is the included text; its attributes are quoted, known and given once; its `title` is its path; its `verified` badges hold.
7. "What you'll build" has a block that includes exactly `day-to-day/expected/output.txt`; the page shows something of `day-to-day/`; there are at least 4 mistakes and 3 to 5 exercises; each card shows its own mistake or answer, as above.
8. Each exercise's examples fail on `start/`; each answer checks clean, runs, and passes `una test .`.
9. Links are to the site's pages, as above.
10. Translations, neutrality, commit addresses and tracked bytecode are checked as for every chapter. A translation of a template 2 page also keeps `template`, `time`, `prerequisites`, the `N.M` numbers of its headings, the blocks and the containers, as above, and follows the same markup and link rules.

Warnings, which do not fail the check but are listed in its report: a part outside its target length, more than 8 mistakes, a count of recap bullets outside 5 to 8, and a step that no block includes.

## Style guide

- **Voice.** Second person, present tense, active. "You declare", not "one declares" and not "we will declare".
- **One idea per section.** Define a term on first use. Never use a term before its chapter without a one-clause gloss.
- **Order inside a section.** Problem, then the construct, then a minimal example, then a second use in context, then pitfalls.
- **Names.** The store domain throughout: SKU, order, inventory, catalog, customer, payment, shipment, cents. Never `demo`, `foo`, `A`, `B` or `Oops`. Example values are fictional and clearly so, such as `example.invalid` addresses.
- **Code.** Canonical form, always (the check enforces it). Comments only where they add what the prose does not. Doc comments (`---`) on every public item, since they are part of the API story.
- **Outputs and diagnostics** come only from `expected/` files. Quote a diagnostic's message line in prose exactly.
- **Numbers.** Money in cents as `Int`. No floating point.
- **Claims.** No absolute claim without a test or a reference. Write "a `pub` function must declare…", not "functions cannot…".
- **Differentiators** are shown as consequences the reader sees: "the checker points at the `when` that needs a new arm", "the header promises callers a price, always". Avoid abstract praise.
- **Specification citations** go only in the Reference part. No internal ids, issue numbers, decision-record numbers, names of people or roles in public text.
- **Translation-friendly.** Short sentences, no idioms or puns, no wordplay with identifiers. Every fact in prose, none only in comments.
- **Lengths** as in the parts table.

## Review checklist

- [ ] Opens with the problem and "What you'll build", with real output.
- [ ] Each concept has at least two uses, the second in context.
- [ ] A decision table wherever two or more constructs compete.
- [ ] The day-to-day program is in the shared domain, 80–200 lines, with examples for every failure or edge path.
- [ ] Common mistakes: 4–8 items, each with real diagnostic text, why, fix, and a link to the code's page.
- [ ] 3–5 exercises with checked answers and a "check your answer" command.
- [ ] Every code fence is an include; `check.py` passes; the release check passes with the pinned `una`.
- [ ] No absolute claim the tests do not support; a technical review against the specification and the released binary is done.
- [ ] A cold read was done from an empty directory, with its log of confusions resolved.
- [ ] An agent completed the exercises from the `.md` twin.
- [ ] Links point to site routes at the release, not to GitHub.
- [ ] Neutral text: no names, roles, internal ids, issue or decision-record numbers.
- [ ] Every fact is in prose (translatable), headings are from the fixed set, and the length is within target.
- [ ] The page is within the site's page budget (40 KiB gzip). Otherwise, split it.
