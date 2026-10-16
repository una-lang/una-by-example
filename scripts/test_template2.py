#!/usr/bin/env python3
"""Tests of the template 2 rules (template2.py and their use in check.py).

They run with Python 3 alone: a stub stands for `una`, and nothing goes to the network.

  python3 -B scripts/test_template2.py
"""

import sys

sys.dont_write_bytecode = True

import io  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import tempfile  # noqa: E402
import unittest  # noqa: E402
from contextlib import redirect_stderr, redirect_stdout  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check  # noqa: E402
import template2  # noqa: E402

# A stub `una`. `--json check .` reports U3007 at each line holding `BAD`; `--color never check .`
# renders the same on stderr, with the absolute path of the package and trailing spaces, which
# the normalization removes; `run .` prints each `print("...")`; `test .` fails when a file holds
# `FAILTEST`. In a template 1 page of check.py's own fixture (src/main.una), it hands over to
# check.py's stub, `una1` beside it.
STUB = r'''#!/usr/bin/env python3
import json, os, re, sys
args = sys.argv[1:]
if os.path.exists("src/main.una"):
    one = os.path.join(os.path.dirname(os.path.abspath(__file__)), "una1")
    os.execv(sys.executable, [sys.executable, one, *args])
if args == ["--json", "--version"]:
    print(json.dumps({"schema": "una.version/1", "version": "9.9.9", "editions": ["0.2"], "z3": "5.1.0"}))
    sys.exit(0)
files = []
for base, dirs, names in os.walk("src"):
    dirs.sort()
    for name in sorted(names):
        path = os.path.join(base, name)
        files.append((path, open(path).read()))
found = []
for path, text in files:
    for n, line in enumerate(text.split("\n"), start=1):
        if "BAD" in line:
            found.append((path, n, line))
if args == ["--json", "check", "."]:
    diagnostics = [{"code": "U3007", "severity": "error", "message": "`parse_order` can fail",
                    "primary": {"file": p, "start": {"line": n, "col": 3}, "end": {"line": n, "col": 3}}}
                   for p, n, _ in found]
    print(json.dumps({"schema": "una.diagnostics/1", "diagnostics": diagnostics, "fixable": 0}))
    sys.exit(1 if diagnostics else 0)
if args == ["--color", "never", "check", "."]:
    for p, n, line in found:
        sys.stderr.write("[U3007] Error: `parse_order` can fail\n")
        sys.stderr.write(f"    ╭─[ {p}:{n}:3 ]   \n")
        sys.stderr.write(f" {n} │{line}\n")
        sys.stderr.write(f"    │ Note: in {os.path.join(os.getcwd(), p)}\n")
        sys.stderr.write("────╯\r\n\n")
    sys.exit(1 if found else 0)
if args == ["fmt", "--check", "."]:
    sys.exit(0)
if args == ["run", "."]:
    for _, text in files:
        for said in re.findall(r'print\("([^"]*)"\)', text):
            print(said)
    sys.exit(0)
if args == ["test", "."]:
    if any("FAILTEST" in text for _, text in files):
        print("1 example: 0 passed, 1 failed")
        sys.exit(1)
    print("1 example: 1 passed, 0 failed")
    sys.exit(0)
sys.exit(2)
'''

TOML = '[package]\nname = "orders"\nversion = "0.1.0"\nedition = "0.2"\n\n[run]\nentry = "orders"\ngrants = ["console"]\n'

ORDERS = """module orders

--- One line of an order.
pub kind Order
  sku: Text
  quantity: Int

--- Reads `"SKU, quantity"`.
pub parse_order(line: Text) -> Order
  fails OrderError
=
  let parts = line.split(on: ",")
  Order(sku: line, quantity: 1)

--- Confirms the stock.
pub check_stock(order: Order) -> Order
  fails OrderError
=
  order

-- A plain comment between declarations.

--- What a person reads.
pub reason(e: OrderError) -> Text
=
  "no"

pub describe(order: Order) -> Text = "ok"

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("ok      2 x LAMP-01")
  @console.print("reject  no product has the SKU CHAIR-09")

example "a line is accepted"
  do parse_order("LAMP-01, 2")
  expect result.quantity == 2
"""

STEP = """module {name}

--- A step of the chapter.
pub {name}(raw: Text) -> Int = 1

pub main() -> Unit
  uses @console: Console[print]
=
  @console.print("{name} {extra}")
"""

LOREM = " ".join(["word"] * 20)

PAGE = """---
learn: "6"
title: Failure
editions: ["0.2"]
codes: [U3007]
time: 35
builds: An order-intake step
prerequisites: ["3", "4", "5"]
template: 2
---

# 6 Failure

{lead}

## What you'll build

:::build
The program prints:

```text include=day-to-day/expected/output.txt
```

You will learn to:

- declare an error kind.
:::

## Why it works this way

{lead}

> [!KEY]
> A key idea.

## 6.1 Declaring a failure

```una title="steps/01-quantity/src/quantity.una" verified="check, run" include=steps/01-quantity/src/quantity.una
```

`una run .` prints:

```text include=steps/01-quantity/expected/output.txt
```

## 6.2 Handling a failure

```una include=steps/02-translate/src/translate.una#translate verified=check
```

## 6.3 Failures as values

```diff include=steps/02-translate..steps/03-defaults:src/translate.una
```

See [the errors](/docs/errors/U3007/) and [above](#what-youll-build).

## 6.4 Day-to-day: order intake

```una include=day-to-day/src/orders.una#Order caption="the kinds"
```

```una include=day-to-day/src/orders.una#reason..describe
```

```sh
una run .
```

## 6.5 Testing it

```una include=day-to-day/src/orders.una#L36-L38 verified=test
```

```text include=day-to-day/expected/commands/test.txt
```

## 6.6 Common mistakes

{mistakes}
## 6.7 For agents

:::agents
Run `una --json check .`.
:::

## 6.8 Exercises

{exercises}
## 6.9 Recap

:::recap
- One.
- Two.
- Three.
- Four.
- Five.
:::

## 6.10 Reference

:::reference
- [fails](/docs/reference/language/errors/fails/)
:::
"""

MISTAKE = """:::mistake
**{n}. Forgetting the clause (U3007).**

```diff include=day-to-day..mistakes/{n}:src/orders.una context=1
```

```text include=mistakes/{n}/expected/rendered.txt
```

*Fix:* add the clause.
:::

"""

EXERCISE = """::::exercise
**Exercise {n}.** Extend the program.

:::hint
*Hint:* look at `reason`.
:::

:::answer Answer
```una include=exercises/{n}/answer/src/orders.una#shipped verified="check, run, test"
```
:::
::::

"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def package(directory, src_name, src, output):
    write(os.path.join(directory, "una.toml"), TOML)
    write(os.path.join(directory, "verification.lock"), "lock\n")
    write(os.path.join(directory, "src", src_name), src)
    write(os.path.join(directory, "expected", "output.txt"), output)


def chapter(root, mistakes=4, exercises=3):
    """A chapter on template 2, with its includes filled. Returns its directory."""
    directory = os.path.join(root, "06-failure")
    package(os.path.join(directory, "steps", "01-quantity"), "quantity.una", STEP.format(name="quantity", extra="3"), "quantity 3\n")
    package(os.path.join(directory, "steps", "02-translate"), "translate.una", STEP.format(name="translate", extra="1"), "translate 1\n")
    package(os.path.join(directory, "steps", "03-defaults"), "translate.una", STEP.format(name="translate", extra="2"), "translate 2\n")
    day = os.path.join(directory, "day-to-day")
    package(day, "orders.una", ORDERS, "ok      2 x LAMP-01\nreject  no product has the SKU CHAIR-09\n")
    write(os.path.join(day, "expected", "commands", "test.txt"), "$ una test .\n1 example: 1 passed, 0 failed\n")
    for n in range(1, mistakes + 1):
        mistake = os.path.join(directory, "mistakes", str(n))
        write(os.path.join(mistake, "base.txt"), "day-to-day\n")
        lines = ORDERS.split("\n")
        line = 12 + n
        lines[line - 1] = f"  BAD{n}"
        write(os.path.join(mistake, "src", "orders.una"), "\n".join(lines))
        write(os.path.join(mistake, "expected", "diagnostics.txt"), f"error U3007 at src/orders.una:{line}:3: `parse_order` can fail\n")
        write(os.path.join(mistake, "expected", "rendered.txt"),
              f"[U3007] Error: `parse_order` can fail\n    ╭─[ src/orders.una:{line}:3 ]\n {line} │  BAD{n}\n"
              f"    │ Note: in src/orders.una\n────╯\n")
    for n in range(1, exercises + 1):
        exercise = os.path.join(directory, "exercises", str(n))
        write(os.path.join(exercise, "start", "base.txt"), "day-to-day\n")
        write(os.path.join(exercise, "answer", "base.txt"), "day-to-day\n")
        write(os.path.join(exercise, "answer", "src", "orders.una"),
              ORDERS + f"\n--- How many units ship.\npub shipped(n: Int) -> Int = {n}\n")
        write(os.path.join(exercise, "answer", "expected", "output.txt"), "ok      2 x LAMP-01\nreject  no product has the SKU CHAIR-09\n")
    page = PAGE.format(lead=LOREM, mistakes="".join(MISTAKE.format(n=n) for n in range(1, mistakes + 1)),
                       exercises="".join(EXERCISE.format(n=n) for n in range(1, exercises + 1)))
    write(os.path.join(directory, "README.md"), page)
    changed, problems = template2.fill(root)
    assert not problems, problems
    return directory


def edit(path, old, new):
    text = check.read(path)
    assert old in text, (path, old)
    write(path, text.replace(old, new, 1))


class Base(unittest.TestCase):
    def setUp(self):
        self.base = tempfile.mkdtemp(prefix="una-by-example-template2-")
        self.root = os.path.join(self.base, "repo")
        os.makedirs(self.root)
        write(os.path.join(self.root, "una.lock"), 'version = "9.9.9"\n')
        self.una = os.path.join(self.base, "una")
        write(self.una, STUB)
        os.chmod(self.una, 0o755)
        write(os.path.join(self.base, "una1"), check.STUB)

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def run_chapters(self):
        """The template 2 checks alone: (failures, warnings)."""
        failures = check.Failures()
        warnings = []
        scratch = os.path.join(self.base, "scratch")
        shutil.rmtree(scratch, ignore_errors=True)
        os.makedirs(scratch)
        template2.check_chapters(self.root, self.una, failures, scratch, warnings)
        return failures.items, warnings

    def assertFails(self, wants):
        items, _ = self.run_chapters()
        self.assertTrue(any(wants in item for item in items), f"no failure with {wants!r} in:\n" + "\n".join(items))

    def assertPasses(self):
        items, _ = self.run_chapters()
        self.assertEqual(items, [])


class Units(unittest.TestCase):
    def test_declarations(self):
        found = template2.declarations(ORDERS)
        self.assertEqual(sorted(found), ["Order", "check_stock", "describe", "main", "parse_order", "reason"])
        text, why = template2.select(ORDERS, "parse_order")
        self.assertIsNone(why)
        self.assertTrue(text.startswith("--- Reads `\"SKU, quantity\"`.\npub parse_order(line: Text) -> Order\n"))
        self.assertTrue(text.endswith("  Order(sku: line, quantity: 1)\n"), text)
        text, _ = template2.select(ORDERS, "check_stock")
        self.assertNotIn("A plain comment", text)
        text, _ = template2.select(ORDERS, "main")
        self.assertNotIn("example", text)
        text, _ = template2.select(ORDERS, "reason..describe")
        self.assertTrue(text.startswith("--- What a person reads.") and text.endswith('pub describe(order: Order) -> Text = "ok"\n'))
        self.assertIn("no top-level declaration", template2.select(ORDERS, "missing")[1])
        self.assertIn("comes before", template2.select(ORDERS, "describe..reason")[1])
        self.assertIn("declared 2 times", template2.select("f() -> Int = 1\nf() -> Int = 2\n", "f")[1])
        self.assertEqual(template2.declaration_name("predicate opaque well_formed(t: Text) -> Bool = true"), "well_formed")
        self.assertEqual(template2.declaration_name("handler warehouse(stock: Map[Text, Int]) for Inventory"), "warehouse")
        self.assertIsNone(template2.declaration_name('example "a line"'))

    def test_lines(self):
        self.assertEqual(template2.select("a\nb\nc\nd\n", "L2-L3")[0], "b\nc\n")
        self.assertEqual(template2.select("a\nb\nc\nd\n", "L1,L4")[0], "a\nd\n")
        self.assertIn("not within", template2.select("a\n", "L2")[1])

    def test_normalize(self):
        package = os.path.join(tempfile.gettempdir(), "pkg")
        text = f"x  \r\n  at {package}/src/a.una\n in {package}\t\n\n\n"
        self.assertEqual(template2.normalize(text, package), "x\n  at src/a.una\n in .\n")
        self.assertEqual(template2.normalize("", package), "")

    def test_fences(self):
        text = '````una include="a b/c.una#f" title=x verified="check, run"\n```\n````\n\nprose\n\n```sh\nuna run .\n```\n'
        blocks, inside = template2.fences(text)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0].lang, "una")
        self.assertEqual(blocks[0].attrs, {"include": "a b/c.una#f", "title": "x", "verified": "check, run"})
        self.assertEqual(blocks[0].body, "```\n")
        self.assertEqual(blocks[1].lang, "sh")
        self.assertNotIn(4, inside)
        self.assertEqual(template2.fences("```una include=x stray\n```\n")[0][0].stray, ["stray"])
        self.assertFalse(template2.fences("```una\nno end\n")[0][0].closed)

    def test_links(self):
        failures = check.Failures()
        template2.links("[a](/docs/x/) [b](#top) [c](https://example.org/) `https://github.com/una-lang/una/blob/main/x`", "p", failures)
        self.assertEqual(failures.items, [])
        for bad, wants in (
            ("[a](https://github.com/una-lang/una/blob/main/docs/guide/x.md)", "repositories"),
            ("see https://github.com/una-lang/una/tree/main/docs", "repositories"),
            ("[a](../05-collections/)", "relative link"),
            ("[a](http://example.org/)", "https"),
            ("[a]: https://raw.githubusercontent.com/una-lang/una/main/x", "repositories"),
        ):
            failures = check.Failures()
            template2.links(bad, "p", failures)
            self.assertTrue(any(wants in item for item in failures.items), (bad, failures.items))

    def test_headings(self):
        page = PAGE.format(lead="x", mistakes="", exercises="")
        fields, body = check.front_matter(page)
        failures = check.Failures()
        self.assertEqual(template2.headings(fields, body, "p", failures), 3)
        self.assertEqual(failures.items, [])
        for old, new, wants in (
            ("## Why it works this way", "## Why", "the parts must be"),
            ("## 6.2 Handling", "## 6.3 Handling", "must be numbered `## 6.2"),
            ("## 6.5 Testing it", "## 6.5 Tests", "the parts must be"),
            ("# 6 Failure", "# 6 Failures", "the title line"),
            ("## 6.4 Day-to-day: order intake", "## 6.4 Daily", "Day-to-day"),
        ):
            failures = check.Failures()
            template2.headings(fields, body.replace(old, new), "p", failures)
            self.assertTrue(any(wants in item for item in failures.items), (old, failures.items))
        # Two concept sections are too few.
        fewer = body.replace("## 6.3 Failures as values", "### Failures as values")
        for n in range(4, 11):
            fewer = fewer.replace(f"## 6.{n} ", f"## 6.{n - 1} ")
        failures = check.Failures()
        template2.headings(fields, fewer, "p", failures)
        self.assertTrue(any("the parts must be" in item for item in failures.items), failures.items)


class Chapters(Base):
    def setUp(self):
        super().setUp()
        self.chapter = chapter(self.root)
        self.readme = os.path.join(self.chapter, "README.md")

    def test_a_good_chapter(self):
        items, warnings = self.run_chapters()
        self.assertEqual(items, [])
        # The prose is short, so the targets give warnings, never failures.
        self.assertTrue(any("words" in w for w in warnings), warnings)

    def test_fill_wrote_the_blocks(self):
        text = check.read(self.readme)
        self.assertIn("```text include=day-to-day/expected/output.txt\nok      2 x LAMP-01\n", text)
        self.assertIn("--- One line of an order.\npub kind Order\n  sku: Text\n  quantity: Int\n```", text)
        self.assertIn("--- a/src/translate.una\n+++ b/src/translate.una\n", text)
        changed, problems = template2.fill(self.root)
        self.assertEqual((changed, problems), ([], []))

    def test_a_free_una_block(self):
        edit(self.readme, "```sh\nuna run .\n```", "```una\nmain()\n```")
        self.assertFails("not an include")

    def test_a_free_text_block(self):
        edit(self.readme, "```sh\nuna run .\n```", "```text\nok\n```")
        self.assertFails("not an include")

    def test_a_block_that_differs(self):
        edit(self.readme, "  sku: Text\n  quantity: Int\n```", "  sku: Text\n  quantity: Nat\n```")
        self.assertFails("is not the text of include=day-to-day/src/orders.una#Order")

    def test_a_changed_package(self):
        edit(os.path.join(self.chapter, "steps", "01-quantity", "src", "quantity.una"), "--- A step", "--- One step")
        self.assertFails("is not the text of include=steps/01-quantity/src/quantity.una")

    def test_a_missing_declaration(self):
        edit(self.readme, "#reason..describe", "#explain")
        self.assertFails("no top-level declaration `explain`")

    def test_a_path_outside_the_packages(self):
        edit(self.readme, "include=steps/01-quantity/expected/output.txt", "include=../../una.lock")
        self.assertFails("is not a plain path")
        edit(self.readme, "include=../../una.lock", "include=README.md")
        self.assertFails("is not in a package")

    def test_a_symbolic_link(self):
        target = os.path.join(self.chapter, "steps", "01-quantity", "src", "quantity.una")
        os.remove(target)
        os.symlink(os.path.join(self.root, "una.lock"), target)
        self.assertFails("is a symbolic link or outside the chapter")

    def test_an_unknown_attribute(self):
        edit(self.readme, 'caption="the kinds"', 'captoin="the kinds"')
        self.assertFails("no fence attribute `captoin`")

    def test_a_wrong_rendering(self):
        edit(os.path.join(self.chapter, "mistakes", "2", "expected", "rendered.txt"), "Error:", "error:")
        self.assertFails("mistakes/2/expected/rendered.txt: is not what `una --color never check .` prints")

    def test_a_wrong_diagnostic(self):
        edit(os.path.join(self.chapter, "mistakes", "3", "expected", "diagnostics.txt"), ":15:3:", ":16:3:")
        self.assertFails("06-failure/mistakes/3: `una check` reports")

    def test_verified_check_on_a_mistake(self):
        edit(self.readme, "```text include=mistakes/1/expected/rendered.txt", "```una include=mistakes/1/src/orders.una#parse_order verified=check")
        template2.fill(self.root)
        self.assertFails("verified=check, but mistakes/1 does not check clean")

    def test_verified_test_that_fails(self):
        edit(os.path.join(self.chapter, "day-to-day", "src", "orders.una"), "expect result.quantity == 2", "expect FAILTEST")
        template2.fill(self.root)
        self.assertFails("verified=test, but `una test .` exits with 1 in day-to-day")

    def test_verified_run_without_output(self):
        edit(self.readme, "include=steps/02-translate/src/translate.una#translate verified=check",
             "include=mistakes/1/src/orders.una#reason verified=run")
        template2.fill(self.root)
        self.assertFails("verified=run, but mistakes/1 has no expected/output.txt")

    def test_an_answer_that_fails_its_tests(self):
        edit(os.path.join(self.chapter, "exercises", "2", "answer", "src", "orders.una"), "expect result.quantity == 2", "expect FAILTEST")
        self.assertFails("exercises/2/answer: an answer passes its tests, but `una test .` exits with 1")

    def test_an_exercise_without_an_answer(self):
        shutil.rmtree(os.path.join(self.chapter, "exercises", "3", "answer"))
        self.assertFails("exercises/3: no answer/")

    def test_an_answer_that_changes_nothing(self):
        shutil.rmtree(os.path.join(self.chapter, "exercises", "1", "answer", "src"))
        shutil.rmtree(os.path.join(self.chapter, "exercises", "1", "answer", "expected"))
        self.assertFails("an answer changes something")

    def test_an_exercise_without_a_start(self):
        shutil.rmtree(os.path.join(self.chapter, "exercises", "1", "start"))
        self.assertFails("exercises/1: no start/")

    def test_a_mistake_not_on_the_page(self):
        text = check.read(self.readme)
        start = text.index(":::mistake\n**4.")
        write(self.readme, text[:start] + text[text.index(":::\n\n", start) + 5:])
        self.assertFails("`Common mistakes` has 3 :::mistake blocks, but there are 4 mistakes/N")

    def test_a_link_to_github_main(self):
        edit(self.readme, "(/docs/errors/U3007/)", "(https://github.com/una-lang/una/blob/main/docs/guide/errors.md)")
        self.assertFails("links to the repositories")

    def test_wrong_codes(self):
        edit(self.readme, "codes: [U3007]", "codes: [U3007, U3008]")
        self.assertFails("`codes` is")

    def test_a_template_1_page_in_the_chapter(self):
        package(os.path.join(self.chapter, "01-fails"), "a.una", STEP.format(name="a", extra="1"), "a 1\n")
        self.assertFails("holds only README.md, steps/")

    def test_an_overlay_of_nothing(self):
        write(os.path.join(self.chapter, "mistakes", "1", "base.txt"), "steps/09-none\n")
        self.assertFails("base.txt names 'steps/09-none'")

    def test_a_missing_part(self):
        edit(self.readme, "## 6.7 For agents", "## 6.7 For machines")
        self.assertFails("the parts must be")

    def test_a_wrong_diff(self):
        edit(os.path.join(self.chapter, "steps", "03-defaults", "src", "translate.una"), "translate 2", "translate 3")
        self.assertFails("is not the text of include=steps/02-translate..steps/03-defaults:src/translate.una")

    def test_a_fence_the_text_would_close(self):
        edit(os.path.join(self.chapter, "steps", "01-quantity", "expected", "output.txt"), "quantity 3\n", "quantity 3\n```\n")
        template2.fill(self.root)
        self.assertFails("use a longer fence")

    def test_template_1_rules_still_apply_elsewhere(self):
        # A template 1 chapter beside a template 2 one, checked by check.py as a whole.
        check.fixture(self.root)
        check.git(self.root, "init", "-q")
        check.git(self.root, "add", "-A")
        check.git(self.root, "commit", "-q", "-m", "c")
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(out):
            code = check.check(self.root, self.una, False, None)
        self.assertEqual(code, 0, out.getvalue())
        self.assertIn("check.py: PASS (1 pages, 1 changes, 0 commands", out.getvalue())
        self.assertIn("template 2: 1 chapters, 11 packages, 1 commands", out.getvalue())
        self.assertIn("warning: 06-failure/README.md", out.getvalue())


class Translations(Base):
    def setUp(self):
        super().setUp()
        chapter(self.root)
        import hashlib

        english = check.read(os.path.join(self.root, "06-failure", "README.md"))
        self.text = english.replace("title: Failure", "title: Falhas").replace("# 6 Failure", "# 6 Falhas").replace(
            "template: 2", f"template: 2\nsource: {hashlib.sha256(english.encode()).hexdigest()}\nstatus: approved")
        self.text = self.text.replace("You will learn to:", "Você vai aprender a:")
        self.path = os.path.join(self.root, "translations", "pt-br", "06-failure", "README.md")

    def failures(self, text):
        write(self.path, text)
        failures = check.Failures()
        check.check_translations(self.root, failures)
        return failures.items

    def test_a_translation(self):
        self.assertEqual(self.failures(self.text), [])

    def test_a_translated_caption(self):
        self.assertEqual(self.failures(self.text.replace('caption="the kinds"', 'caption="os tipos"')), [])

    def test_a_changed_include(self):
        items = self.failures(self.text.replace("#reason..describe", "#reason"))
        self.assertTrue(any("code and links differ" in i for i in items), items)

    def test_a_changed_number(self):
        items = self.failures(self.text.replace("## 6.2 Handling a failure", "## 6.20 Tratando uma falha"))
        self.assertTrue(any("numbered as the English page's" in i for i in items), items)

    def test_a_changed_time(self):
        items = self.failures(self.text.replace("time: 35", "time: 40"))
        self.assertTrue(any("`time` is '40'" in i for i in items), items)

    def test_fill_fills_translations(self):
        write(self.path, self.text.replace("  quantity: Int\n```", "```"))
        changed, problems = template2.fill(self.root)
        self.assertEqual((changed, problems), (["translations/pt-br/06-failure/README.md"], []))
        self.assertEqual(self.failures(check.read(self.path)), [])


def main():
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=1, stream=sys.stderr).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
