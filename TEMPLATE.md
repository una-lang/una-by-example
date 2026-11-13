# Chapter template 2

A chapter on template 2 is one long page that teaches one idea of Una through a program the reader builds. Every block of code, output and diagnostic on it comes from a package that `scripts/check.py` checks against the pinned `una`, so nothing on the page is typed by hand.

A chapter opts in with exactly `template: 2` in the front matter of its `README.md`. A chapter stays on template 1 (the fixed parts `The program`, `What you should see`, `Try it` and `See also`, one directory per page) only while its `README.md` has no front matter and no code block, it has page directories, and it has none of `steps/`, `day-to-day/`, `mistakes/` or `exercises/`. Anything in between fails the check: a front matter that does not parse, `template` with another value or spelling (`template: 02`, `Template: 2`), or template 2 directories without `template: 2`. Pages use LF line ends; a carriage return fails. The chapter's `README.md` is a plain file: a symbolic link fails.

## Files

```text
NN-chapter/
  README.md                 the page, in English
  steps/01-<slug>/          one package per example in the text, in order
    una.toml  verification.lock  src/  expected/
                            or, from edition 0.4:
    ita.una  ita.lock  src/  deps/<name>/  expected/
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

- **A package**: `una.toml`, `verification.lock` and `src/`, as in template 1. From edition `0.4`, `ita.una`, `ita.lock` and `src/` instead, and its path dependencies under `deps/<name>/`, each a package with its own `ita.una` and `src/` (`spec/30 §12`). A package has exactly one manifest, `una.toml` or `ita.una`: both or neither fails, and so does `ita.lock` or `deps/` beside `una.toml`, or `verification.lock` beside `ita.una`.
- **An overlay**: a file `base.txt` whose one line names a package of the chapter (`day-to-day`, `steps/02-handling`), and the files that replace that package's, at the same paths (`src/orders.una`). An overlay's base is always a package, never another overlay. An overlay with no files of its own (only `base.txt`) is that package, and has no `expected/`.

A package or overlay holds only these files: `una.toml`, `verification.lock`, `base.txt` (in an overlay), `src/**/*.una`, from edition `0.4` `ita.una`, `ita.lock`, `deps/<name>/ita.una` and `deps/<name>/src/**/*.una`, and in `expected/` the files below. Anything else fails, and so does a symbolic link anywhere in the chapter.

Every package and every overlay with files of its own has `expected/`, checked as template 1 checks a page's:

| File | What it holds |
| --- | --- |
| `expected/output.txt` | What `una run .` prints, byte for byte. The package then also checks clean at tier 1 and is in canonical form (`una fmt --check`). |
| `expected/diagnostics.txt` | Instead of `output.txt`: the lines `una check` reports, `error <code> at <file>:<line>:<col>: <message>`, each followed by its counterexample line when it has one. An empty file states that the package checks clean and is not run; use it when a command file shows what running it does, such as an abort. An empty file with no command file fails the check. |
| `expected/rendered.txt` | What `una --color never check .` prints on stderr, as a reader sees it in a terminal, after the normalization below. Every mistake has one. |
| `expected/commands/<name>.txt` | A further command: `$ una <args>` on the first line, then what it prints on stdout, byte for byte. `<name>` is lowercase letters, digits and dashes. The output of `report .` names the host: `native:`, `solver build:`, `runtime sha256:` and `linker:` differ between the targets of una 0.4.0, `aarch64-apple-darwin` and `aarch64-unknown-linux-gnu`. The book's reports are those of `aarch64-apple-darwin`, so their check passes on macOS arm64 only. |

**Commands.** A command is one of: `check .`, `test .`, `run .`, `build .`, `report .` and `obligations .` (each optionally after `--json`), `fmt --check .`, `fix --dry-run .`, `explain U1234`, `trace NAME` and `contract NAME` (optionally after `--json`), and for an edition `0.4` package `ita lock` and `ita lock --check` (optionally after `--json`, with `.` or no path). No other argument, no `--grant`, no `--accept-authority`, and no path but `.`.

**What `una` may do.** `una` runs with a minimal environment: `PATH`, a `HOME` and `TMPDIR` of its own, fresh for each run, `LANG=C.UTF-8` and `NO_COLOR=1`, nothing else. A package's `una.toml` holds only the tables `[package]`, `[run]`, `[escape_budget]`, `[labels]`, `[trusted]`, `[boundaries]` and `[contracts]`; `[package]` holds only `name`, `version` and `edition`; `[run]` holds only `entry` and `grants`; and the grants are `console`, `clock` and `files:src:<access>` or `files:src/<dir>:<access>`, where `<access>` is `read`, `write` or `read,write`. A package's `ita.una` is held to the same: its head holds only `version` and `edition`; its sections are only `needs`, `labels`, `trusted`, `escapes`, `boundaries`, `contracts` and `run`; a need is a path dependency under `deps/`, `<name> [as <local>] from path "deps/<dir>"`, with only `may` and `accept name` lines; `run` holds only `entry` and `grants`, and the grants are `console`, `clock` and `files "src" <access>` or `files "src/<dir>" <access>`, with no limit lines; and a dependency's `ita.una` holds its head only. No environment, no network, no files outside the package's `src/`. Each command runs on a fresh copy of the package, so what one writes never reaches another.

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
nav: ["fails and fail", "The five handling clauses", "attempt and Result", "checked", "Day-to-day: order intake", "Testing it", "Common mistakes", "Exercises", "Recap and reference"]
---
```

- The fields are exactly these, one `key: value` line each, with no blank line; only `nav` is optional.
- `learn` is the chapter's number, as its directory says.
- `codes` is the union of the codes of every `expected/diagnostics.txt` in the chapter.
- `time` is the reading time in minutes, without the exercises.
- `builds` describes the day-to-day program in one line.
- `prerequisites` lists the numbers of earlier chapters the reader needs.
- `template: 2` turns on the rules of this document.
- `nav` gives the site's sidebar a short label for each numbered section, `N.1` to the last one, in order; the sidebar shows `N.k <label>`. When it is present:
  - It has one label per numbered section, whatever the page's count of numbered sections is: no more and no fewer.
  - Each label is in double quotes, and the labels are separated by commas. A label may hold a comma, but no double quote.
  - Each label is plain text of 1 to 32 characters, with no space at its ends, no backtick, tilde, `<` or `>` (the front matter holds none), no section number of its own, and no control or invisible character.
  - A label names what the section teaches, briefly: `fails and fail`, not `Declaring a failure: fails and fail`. Code names are written plainly, without backticks.
  - The fixed parts of the table below keep their headings as labels, and the day-to-day label is `Day-to-day: <program>`, shortened to fit.

A translation keeps `learn`, `editions`, `codes`, `template`, `time` and `prerequisites`, translates `title` and `builds`, and adds `source` and `status` as in template 1. It translates `nav` when the English page has one, by the same rules and with one label per section, and has no `nav` when the English page has none.

## Parts, in order, with target lengths

The headings are fixed. `N` is the chapter's number, and the numbered parts count up from `N.1` with no gap.

| # | Part (heading) | Required content | Target |
| --- | --- | --- | --- |
| 0 | Front matter | As above | n/a |
| 1 | `# N <title>` and the lead | One paragraph: the problem this chapter solves in a working program | 60–120 words |
| 2 | `## What you'll build` | The day-to-day program's output, included from `day-to-day/expected/output.txt`, and 3 to 5 "you will learn" bullets | 80–150 words |
| 3 | `## Why it works this way` | The motivation: what goes wrong in languages without this, what Una guarantees instead, stated concretely and without polemic | 150–300 words |
| 4 | `## N.1 <concept>` to `## N.k <concept>`, k from 3 to 6 | One idea per section, taught as [Teaching a concept](#teaching-a-concept) says: what it is, why it exists, how to write it in every form, several examples with their output, how it behaves, when to use it, and a check-yourself question | 300–2,500 words each, as many blocks as the forms need |
| 5 | `## N.k+1 Day-to-day: <program>` | The program in the shared store domain, 80 to 200 lines. Shown in parts with walkthroughs, then whole (collapsed), then run, then tested | 500–1,200 words |
| 6 | `## N.k+2 Testing it` | The chapter's idea under `una test`: examples, fakes, the failure paths | 200–400 words |
| 7 | `## N.k+3 Common mistakes` | 4 to 8 items: the wrong code (a diff), the real diagnostic, why it happens, the fix, and a link to the code's page | 60–120 words each |
| 8 | `## N.k+4 Exercises` | 3 to 5: one direct, one that extends the day-to-day program, one stretch. Each has a goal, a hint, a collapsed answer, and the command that checks it | 80–200 words each |
| 9 | `## N.k+5 Recap and reference` | Three subsections, in this order: | |
| | `### For agents` | 3 to 6 lines: the JSON shape of this chapter's diagnostics, the repairs `una fix` can apply, the compact rule | 60–120 words |
| | `### Recap` | 5 to 8 bullets, each a rule the reader can apply | 80–150 words |
| | `### Reference` | Links to the construct pages, std items, error codes and specification sections, all on the site, at the release | list |

Totals: 3,000 to 20,000 words of prose (paragraphs and list text; headings, code and `:::` lines do not count, and the same holds for each part's target), so that six concept sections at their longest fit with the other parts. The site shows each numbered section as a page of its own, so a long chapter stays readable; the budget of the whole-chapter page (40 KiB gzip) is handled by the site, separately from these targets.

Inside each numbered part, `### ` subsections follow the rules of [Inside a section](#inside-a-section). No other `## ` heading may appear. Every heading is a `#` line at column 0, outside quotes and lists; an underlined (setext) heading fails, so put a blank line before a `---` rule.

Rules:

- Every output, diagnostic and number shown comes from an `expected/` file.
- Identifiers are real words from the domain. Never `demo`, `foo`, `A`, `B` or `Oops`.
- The prose never cites a specification section inline. Citations go in Reference.

## Inside a section

The site shows each numbered section (`## N.k`) as a page of its own, and lists the section's `### ` subsections in "On this page", numbered `N.k.1`, `N.k.2` and so on. A section's subsections are its outline: a reader scans them to find a rule again, and a link can name each one. Every numbered section therefore has an internal structure:

| Section | Its `### ` subsections |
| --- | --- |
| Concept (`N.1` to `N.k`) | 3 to 12, each titled by what it teaches, in the order of [Teaching a concept](#teaching-a-concept). Three to six is the least a concept needs; a concept with many forms takes more, and `#### ` parts inside them. |
| Day-to-day | At least 2: one per part of the program, each module or step in the order the text builds it, then running it, then the whole program. The whole program is optional when the text already shows each module whole. A subsection may follow the whole program when it continues the program's story, such as `### The checks before a release`. |
| Testing it | At least 2: one per kind of test, such as the happy path, the failure paths and what must not happen, then running the examples. The rule is distinct kinds of tests, not length: a subsection may be a lead sentence and a list. |
| Common mistakes | One per mistake, titled by the mistake and ending with its code in parentheses, or its codes (`(U0101, U7002)`), each one a code the mistake's `diagnostics.txt` reports, such as `### Forgetting the clause (U3007)`, holding that mistake's `:::mistake` card and nothing of another. |
| Exercises | One per exercise, `### Exercise N: <goal>` with `N` its place in order, holding its `::::exercise` card. |
| Recap and reference | Exactly `### For agents`, `### Recap` and `### Reference`, in this order, with nothing before the first. |

- **Titles are specific.** Every subsection's title, in every section, says what it holds: `### Translating between layers with error`, not `### Overview`, `### Details`, `### Example` or `### More`. A title is short, has no final period, and reads well after its number.
- **Deeper parts.** A subsection may hold `#### ` parts, which the site numbers `N.k.m.1`. Use them for parts a reader would look up one by one: each form of a construct under "How to write it", each rule under "How it behaves".
- **Text before the first subsection.** A section may open with a sentence or two before its first `### `, such as the intro of Common mistakes. A concept section usually starts its first subsection at once.
- **Restructuring keeps the content.** Insert headings, and move or split paragraphs; add only the bridging sentence a subsection needs to read well on its own. Includes, expected outputs and verified blocks stay as they are.
- **Anchors.** A subsection's anchor is the slug of its English words (`#forgetting-the-clause-u3007`): lowercase, backticks and other punctuation dropped, spaces as `-`. The site also gives it the anchor of its number (`#s6-7-1`), which changes when a subsection is added before it; prefer the slug. So that every anchor names one heading:
  - every heading of a chapter has its own slug (the site would give a repeated one `-1`, which no link can count on);
  - no heading's words make the id of a section number (`### S6 1` would be `s6-1`);
  - `for-agents`, `recap` and `reference` are the ids of the closing section's three subsections, and no other heading of the chapter takes them;
  - every link to `#id` on the page names a heading's slug or number.

## Teaching a concept

Write every concept section for a reader who may never have programmed, and who has never seen Una. Such a reader learns from the page what a construct is, why the language has it, and how to use it; nothing may depend on knowledge the book has not given. When an example needs a construct of a later chapter, it gives that construct a one-clause gloss and a link to where it is taught, as the Style guide asks, and relies on nothing more. A concept section teaches its construct in this order, each part one or more `### ` subsections titled by what it holds:

| Part | What it does | Usual title |
| --- | --- | --- |
| What it is | Says what the construct is in plain language first, with an everyday analogy where one helps. Defines every programming term at its first use in the book, or links to where it was defined. | `### What a loop is` |
| Why it exists | Shows the problem first: code that is wrong, fragile or impossible without the construct, with its output or diagnostic, and says what goes wrong. For a construct most languages lack, such as contracts, capabilities and labels, says why Una has it. | `### Why programs repeat work` |
| How to write it | Names and explains each part of the syntax. Covers every form and variant the language allows, each in its own short example, usually a `#### ` part per form. | `### How to write a for loop` |
| Several examples | Small, focused examples, each showing one form or behavior, with its output or diagnostic. Then a realistic example in the store domain that combines them, with a walkthrough. | `### Installments that never divide by zero` |
| How it behaves | The precise rules and the edge cases, each with an example: an empty input, the boundaries, what happens when it fails, and the diagnostic a broken version gives and how to read it. | `### How a loop behaves` |
| When to use it, and what instead | The alternatives and how to choose between them, usually as a `:::decide` table. | `### A precondition, a guard or a kind` |
| Check yourself | One or two short questions, usually "predict the output" or "does it check?", each with its answer in a `:::answer` box. | `### Check yourself: loops` |

The chapters are being rewritten to this standard one by one. Until all are, `check.py` reports a concept section without a `### Check yourself: <topic>` subsection as a warning, not a failure; a section that is not yet rewritten keeps its earlier arc.

Two parts may share a subsection, and a part may take several: a construct with many forms gives "How to write it" a `#### ` part per form, and a long realistic example keeps its own `### `. The order holds.

- **Ground every claim.** A rule stated in the text comes from the specification or a decision record, and each example shows it. Nothing is invented, and nothing is stated only in a comment.
- **Words first, then show, then name.** "What it is" uses words and an analogy, and no code block. From "How to write it" on, show the code and its output first, then name what the reader saw. A term the reader has not met is defined in the sentence that uses it.
- **Every form is checked.** Each example is an include of a checked package, as everywhere on the page: a step package, an overlay for a broken version, or a function of a step package shown by its name (`#units`) with its line of output (`#L2`). A step package may hold several small functions, one per form, and its `main` prints one line for each.
- **Diagnostics are read aloud.** When an example fails, the page shows the diagnostic, says which line names the problem, what the marks point at, what the counterexample means, and which repair fits.
- **Check yourself.** The question comes first, with the code it asks about. The answer follows in `:::answer Show the answer`, folded, with the expected output or diagnostic that proves it and a sentence or two of why. The output a question asks about is not shown earlier in the section. A question may ask whether a changed version checks; its answer then shows that version's diagnostic from an overlay, whole or by selected lines (`rendered.txt#L1,L22`). A question about a rule may be answered in prose alone, when the rule is stated earlier in the chapter.
- **Style.** Clear, warm and precise. Short sentences in the second person, no filler and no hype. An analogy is one or two sentences, from daily life, and never replaces the precise rule that follows it.

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
| ```` ```una include="steps/15-path-dependency/ita.una" ```` | A manifest of edition `0.4`; `ita.lock` and a dependency's `deps/tags/ita.una` and `deps/tags/src/format.una` are shown the same way. |

A block shows only `una.toml`, `src/**/*.una` and the expected files, and from edition `0.4` `ita.una`, `ita.lock`, `deps/<name>/ita.una` and `deps/<name>/src/**/*.una`. Paths are relative to the chapter's directory, with no `..`. An include of an overlay's file that the overlay does not replace shows its base's file.

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
| `verified="check, run, test"` | The badges, only on a block of `una.toml`, `ita.una` or a `src/` file, a dependency's included, whole or by declaration (not on lines or a diff). Each is checked: `check` needs the package to check clean, `run` needs its `expected/output.txt`, and `test` runs `una test .` on it, which must pass. A block from a mistake has no `verified`. |
| `mistake="wrong"` or `mistake="right"` | The two sides of a `:::pair`. |
| `context="N"` | The lines of context of a diff. |

Any other attribute fails the check, so a misspelt `include` does not pass unnoticed.

**Blocks written by hand.** Only plain `sh` blocks (```` ```sh ````, no attributes) of commands the reader types, one per line, with no `$` prompt and no output: `una <command>` with a command from the list above, such as `una ita lock`, `cd <path>` or `mkdir <path>` with one plain path, or `python3 -B scripts/check.py` alone, with `--fill` or with `--self-test`. Every other block, `text` and `json` included, is an include; output comes from `expected/commands/`.

**Translations.** A translation holds the same blocks, in the same order, byte for byte, with the same includes and bodies, and the same `:::` containers in the same order: only the prose, the `caption` values and the summary after `:::answer` change. `--fill` keeps the blocks in step with the English page.

## Mistakes and exercises

- A chapter has at least 4 `mistakes/N` (more than 8 is reported), numbered from 1. Each has `expected/diagnostics.txt` and `expected/rendered.txt`. The Common mistakes part has one `### ` subsection and one `:::mistake` card per directory, in order: card `k` shows `mistakes/k/expected/rendered.txt` (whole or by lines), usually a diff from its base, and nothing of another mistake.
- A chapter has 3 to 5 `exercises/N`, numbered from 1, each with `start/` and `answer/`. The Exercises part has one `### ` subsection and one `::::exercise` card per directory, in order: card `k` holds a `:::answer` with a block of `exercises/k/answer`, and nothing of another exercise.
- `start/` holds the exercise's example, and `una test .` fails on it: that is what tells the reader the exercise is not done yet. It is usually an overlay of the day-to-day program with the example added. An answer changes something (it is not only a `base.txt`), checks clean, prints its `expected/output.txt` under `una run`, and passes `una test .`.

## Links

**Between sections, link; never write "above" or "below".** Each numbered section is a page of its own on the site, so "the table above" or "mistake 4" can name something the reader does not see. Name it, and link it: `[section 6.2](#s6-2)`, `[Common mistakes](#s6-7)`, `[the clause on the same line](#the-clause-on-the-same-line-u0101)`. Inside one section, which is one page, "below" and "above" are fine.

Links point to the site's own pages at the release: a root-relative route such as `/docs/errors/U3007/`, or an anchor on the page such as `#what-youll-build`. An anchor names a numbered heading by its number, `#s6-1` for `## 6.1 …`, and another heading by the slug of its English words (`#what-youll-build`); a translation keeps the English page's anchors, and its headings match the English page's in number and order. A link to a file of the una-lang repositories on GitHub (`/blob/`, `/tree/`, `raw.githubusercontent.com`) fails, since those files change after the release; so does a relative link such as `../05-collections/README.md`, which resolves on GitHub but not on the site, and an `http://` link. The host is matched in any case and with any port. Other `https://` links are allowed.

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
| ```` ```text include="…/expected/rendered.txt" ```` | a diagnostic: accent color, linked code, Help and Note lines | 7, 8 |
| `:::decide` around `**Which to use:**` and a table | a decision table, read as "want → use" | 4 |
| `### <mistake>` then `:::mistake` | a mistake card under its subsection: the change, the diagnostic, then the rows. The `### ` heading is its title, so the card opens with plain text, not a bold lead | 7 |
| `*Why:*`, `*Fix:*`, `*Hint:*` opening a paragraph | a labeled row | 7, 8 |
| `:::pair` around blocks with `mistake="wrong"` and `mistake="right"` | before and after, side by side | 7 |
| `:::agents` | the machine panel, under `### For agents` | 9 |
| `### Exercise N: <goal>` then `::::exercise` holding `:::hint` and `:::answer <summary>` | an exercise card under its subsection, a hint box, and a collapsed answer; the card opens with the goal in plain text | 8 |
| `:::answer <summary>` on its own, in `### Check yourself: <topic>` | a collapsed answer to a check-yourself question | 4 |
| `:::recap` | a checklist of rules, under `### Recap` | 9 |
| `:::reference` | a quiet index list, under `### Reference` | 9 |
| `` `code` `` | a chip, colored by what it holds: keyword, kind, capability, command or path | all |
| `U1234`, in text or in backticks | a chip linked to the code's page | all |
| `[[Ctrl]]` | a keyboard key | all |

A container that holds others uses more colons (`::::exercise` around `:::hint`), and every container is closed by a line of as many colons. A `:::` line starts at column 0, outside quotes and lists, with the name right after the colons: `:::mistake`, not `::: mistake`.

## What `check.py` checks on a template 2 chapter

Failures:

1. The chapter is exactly on template 2 or exactly on template 1, as above.
2. The chapter directory holds only `README.md`, `steps/`, `day-to-day/`, `mistakes/` and `exercises/`, laid out as above, with only the allowed files and no symbolic link.
3. Every package and overlay has exactly one allowed manifest, `una.toml` or `ita.una`, and the outcome in its `expected/`; its commands are allowed and print what they say; its `rendered.txt` is what `una` prints, normalized.
4. The front matter has exactly its fields; `learn` matches the directory; `codes` are the codes the outcomes show.
5. The parts are the ones above, in order, numbered without gaps, with 3 to 6 concept sections; inside them, each concept section has 3 to 12 `### ` subsections, none titled by a generic label (`Overview`, `Details`, `Example` and the like), Day-to-day and Testing it have at least 2 `### `, no subsection anywhere has a generic title, Common mistakes and Exercises have one `### ` per card with its card in it (a mistake's title ends with a code its diagnostics show, an exercise's is `Exercise k: <goal>` in order), the anchors follow the rules of Anchors in [Inside a section](#inside-a-section) (a dangling `#id` link, a repeated slug and a slug like a section number fail in every chapter), and the closing section is `Recap and reference` with exactly `### For agents`, `### Recap` and `### Reference`. The markup is strict: no code outside the blocks the check reads (no `$$` line, no indented code, no fence inside a quote or list), no invisible or control character, no setext heading, no raw HTML, only the template's containers and callouts, at column 0.
6. Every fenced block is an include (or a plain `sh` block of commands); its include resolves; its body is the included text; its attributes are quoted, known and given once; its `title` is its path; its `verified` badges hold.
7. "What you'll build" has a block that includes exactly `day-to-day/expected/output.txt`; the page shows something of `day-to-day/`; there are at least 4 mistakes and 3 to 5 exercises; each card shows its own mistake or answer, as above.
8. Each exercise's examples fail on `start/`; each answer checks clean, runs, and passes `una test .`.
9. Links are to the site's pages, as above.
10. Translations, neutrality, commit addresses and tracked bytecode are checked as for every chapter. A translation of a template 2 page also keeps `template`, `time`, `prerequisites`, the `N.M` numbers of its headings, the blocks and the containers, as above, and follows the same markup and link rules.

Warnings, which do not fail the check but are listed in its report: a concept section without a `### Check yourself: <topic>` subsection, a part outside its target length, more than 8 mistakes, a count of recap bullets outside 5 to 8, and a step that no block includes.

## Style guide

- **Voice.** Second person, present tense, active. "You declare", not "one declares" and not "we will declare".
- **One idea per section.** Define a term on first use. Never use a term before its chapter without a one-clause gloss.
- **Order inside a section.** As in [Teaching a concept](#teaching-a-concept): what it is, why it exists, how to write it, examples, how it behaves, when to use it, check yourself.
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
- [ ] Each concept section follows [Teaching a concept](#teaching-a-concept): a reader who has never programmed can follow it, every form of the construct has its own checked example, and the section ends with a check-yourself question.
- [ ] Every section has its subsections: 3 to 12 specific `### ` titles in each concept section, one per mistake and per exercise, and the closing `Recap and reference`; no "above" or "below" across sections.
- [ ] The page is within the site's page budget (40 KiB gzip). Otherwise, split it.
