# Chapter template 2

A chapter on template 2 is one long page that teaches one idea of Una through a program the reader builds. Every block of code, output and diagnostic on it comes from a package that `scripts/check.py` checks against the pinned `una`, so nothing on the page is typed by hand.

A chapter opts in with `template: 2` in the front matter of its `README.md`. Chapters without it keep the rules of template 1 (the fixed parts `The program`, `What you should see`, `Try it` and `See also`, one directory per page) until they are rewritten.

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
  exercises/N/start/        where the exercise starts (often an overlay naming a package)
  exercises/N/answer/       the answer: checks clean, runs, and passes `una test`
  exercises/N/<slug>/       any other state the exercise shows, such as a diagnostic on the way
translations/<locale>/NN-chapter/README.md
                            a translation of the page; the packages are never copied
```

Each directory under `steps/`, `day-to-day/`, `mistakes/` and `exercises/` is one of:

- **A package**: `una.toml`, `verification.lock` and `src/`, as in template 1.
- **An overlay**: a file `base.txt` whose one line names a package of the chapter (`day-to-day`, `steps/02-handling`), and the files that replace that package's, at the same paths (`src/orders.una`). An overlay's base is always a package, never another overlay. An overlay with no files of its own (only `base.txt`) is that package, and has no `expected/`; an exercise's `start/` is often one.

Every package and every overlay with files of its own has `expected/`, checked as template 1 checks a page's:

| File | What it holds |
| --- | --- |
| `expected/output.txt` | What `una run .` prints, byte for byte. The package then also checks clean at tier 1 and is in canonical form (`una fmt --check`). |
| `expected/diagnostics.txt` | Instead of `output.txt`: the lines `una check` reports, `error <code> at <file>:<line>:<col>: <message>`, each followed by its counterexample line when it has one. |
| `expected/rendered.txt` | What `una --color never check .` prints on stderr, as a reader sees it in a terminal, after the normalization below. Optional; a mistake that the page shows needs it. |
| `expected/commands/*.txt` | A further command: `$ una <args>` on the first line, then what it prints on stdout, byte for byte. `$ una test .` is the usual one. |

**Normalization of `rendered.txt`.** The checks run each package in a fresh copy, at a path that changes on every run. Before comparing, the output is normalized: CRLF becomes LF; the copy's absolute path followed by `/` is removed, and where it stands alone it becomes `.`; spaces and tabs at the end of a line are removed; blank lines at the end are removed, and the text ends with one newline. Write `rendered.txt` already normalized. The simplest way is to copy what `una --color never check . 2>&1` prints in the package and remove the spaces at the ends of lines.

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

`### ` headings may be used inside any part. No other `## ` heading may appear.

Rules:

- Every output, diagnostic and number shown comes from an `expected/` file.
- Identifiers are real words from the domain. Never `demo`, `foo`, `A`, `B` or `Oops`.
- The prose never cites a specification section inline. Citations go in Reference.

## Blocks are includes

The page has no free-floating code. Every fenced block names, in its info string, the file it shows, and its body is that file's text, exactly. The page therefore reads the same in any Markdown viewer, on the site, and as the `.md` twin an agent reads, and `check.py` fails the moment a package and its page disagree.

| Write | Shows |
| --- | --- |
| ```` ```una include=steps/01-quantity/src/quantity.una ```` | The whole file. |
| ```` ```una include=day-to-day/src/orders.una#check_stock ```` | One top-level declaration, with its doc comment. |
| ```` ```una include=day-to-day/src/orders.una#reason..describe ```` | From one declaration to the end of another, everything between included. |
| ```` ```text include=day-to-day/expected/output.txt ```` | Any file of a package, its `expected/` files included. |
| ```` ```text include=mistakes/2/expected/rendered.txt#L1 ```` | Lines of a file: `#L3`, `#L3-L9`, or a list such as `#L1,L8-L9`. Use this to trim a long diagnostic to its message line. |
| ```` ```diff include=day-to-day..mistakes/1:src/orders.una ```` | A unified diff of one file between two packages (`a/` and `b/` prefixes, 3 lines of context; `context=1` changes it). |
| ```` ```toml include=steps/04-checked/una.toml ```` | A manifest. |

Paths are relative to the chapter's directory. An include of an overlay's file that the overlay does not replace shows its base's file.

**Declarations.** A top-level line is a line at column 0 that is not blank and does not start with `=` (the `=` that opens a function body is part of its declaration). A declaration starts at its name's top-level line, or at the `---` doc comment lines right above it, and ends before the next top-level line, without the blank lines at its end. The name is the first word after `pub`, `trusted`, `kind`, `capability`, `handler`, `predicate`, `opaque` and the like: `main` in `pub main() -> Unit`, `Inventory` in `pub capability Inventory`. A plain `--` comment at column 0 ends the declaration above it and belongs to none. Examples, `module` lines and names declared twice cannot be named; include them by lines.

**Filling the blocks.** Write the fence line with an empty body, then run

```sh
python3 -B scripts/check.py --fill
```

It writes the body of every include, on the English page and its translations, from the packages. It needs no `una`, and it changes nothing else.

**Other attributes.** Values may be quoted, and must be when they hold a space.

| Attribute | Meaning |
| --- | --- |
| `title="day-to-day/src/orders.una"` | The path shown in the block's header. |
| `caption="the kinds and the service"` | A short label after the title. It is prose: a translation translates it. |
| `verified="check, run, test"` | The badges. Each is checked: `check` needs the package to check clean, `run` needs its `expected/output.txt`, and `test` runs `una test .` on it, which must pass. A block from a mistake has no `verified`. |
| `mistake="wrong"` or `mistake="right"` | The two sides of a `:::pair`. |
| `context=N` | The lines of context of a diff. |

Any other attribute fails the check, so a misspelt `include` does not pass unnoticed.

**Blocks written by hand.** Only `sh` blocks, with no attributes, for commands the reader types. Every other block, `text` and `json` included, is an include.

**Translations.** A translation holds the same blocks, byte for byte, with the same includes and bodies: only the prose around them and the `caption` values change. `--fill` keeps them in step with the English page.

## Mistakes and exercises

- `mistakes/N` are numbered from 1, and the Common mistakes part has one `:::mistake` block per directory. Each shows something of its own `mistakes/N`, usually its `rendered.txt` and a diff from its base.
- `exercises/N` are numbered from 1, each with `start/` and `answer/`, and the Exercises part has one `::::exercise` block per directory. Each shows its answer.
- An answer changes something (it is not only a `base.txt`), checks clean, prints its `expected/output.txt` under `una run`, and passes `una test .`. Give it at least one example that fails on `start/` and passes on the answer, so that the reader's `una test .` tells them when they are done.

## Links

Links point to the site's own pages at the release: a root-relative route such as `/docs/errors/U3007/`, or an anchor on the page such as `#what-youll-build`. A link to a file of the una-lang repositories on GitHub (`/blob/`, `/tree/`, `raw.githubusercontent.com`) fails, since those files change after the release; so does a relative link such as `../05-collections/README.md`, which resolves on GitHub but not on the site, and an `http://` link. Other `https://` links are allowed.

## Components

The page uses Markdown and a small set of markers that the site renders. None of them is raw HTML.

| Write | Get | Part |
| --- | --- | --- |
| front matter `time`, `editions`, `prerequisites`, `codes` | a strip under the title: reading time, edition, linked prerequisite chapters, code chips | 0, 1 |
| first paragraph after `# N <title>` | the lead paragraph | 1 |
| `:::build` … `:::` | the "What you'll build" card. The paragraph before the list becomes its label, and the list gets checks | 2 |
| `> [!KEY]` | the key-idea pull quote, one per chapter | 3 |
| `:::steps` around a code block and a numbered list | numbered steps. A step that opens with bold code is tied to that code's line | 3, 4, 5 |
| `> [!NOTE]`, `[!TIP]`, `[!IMPORTANT]`, `[!WARNING]`, `[!SECURITY]`, with an optional title after the marker | a callout with an icon, a color and a title line | 4, 5 |
| ```` ```una include=… title="…" caption="…" verified="check, run" ```` | a code block with a header: path, caption, check badges, language and Copy | 4, 5, 6 |
| ```` ```text include=…/expected/output.txt ```` | output in a terminal look | 2, 4, 6 |
| ```` ```text include=…/expected/rendered.txt ```` | a diagnostic: accent color, linked code, Help and Note lines | 7, 9 |
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

A container that holds others uses more colons (`::::exercise` around `:::hint`). A translation changes only the prose, the `caption` values and the summary after `:::answer`.

## What `check.py` checks on a template 2 chapter

Failures:

1. The chapter directory holds only `README.md`, `steps/`, `day-to-day/`, `mistakes/` and `exercises/`, laid out as above.
2. Every package and overlay has the outcome in its `expected/`, its commands print what they say, and its `rendered.txt` is what `una` prints, normalized.
3. The front matter has every field; `learn` matches the directory; `codes` are the codes the outcomes show.
4. The parts are the ones above, in order, numbered without gaps, with 3 to 6 concept sections.
5. Every fenced block is an include (or a plain `sh` block), its include resolves, its body is the included text, and its `verified` badges hold.
6. "What you'll build" includes `day-to-day/expected/output.txt`; the page shows something of `day-to-day/`, of each `mistakes/N` and of each `exercises/N/answer`; the `:::mistake` and `::::exercise` blocks match the directories.
7. Each answer checks clean, runs, and passes `una test .`.
8. Links are to the site's pages, as above.
9. Translations, neutrality, commit addresses and tracked bytecode are checked as for every chapter. A translation of a template 2 page also keeps `template`, `time`, `prerequisites` and the `N.M` numbers of its headings.

Warnings, which do not fail the check but are listed in its report: a part outside its target length, a count of mistakes, exercises or recap bullets outside its range, and a step that no block includes.

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
