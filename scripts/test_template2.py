#!/usr/bin/env python3
"""Tests of the template 2 rules (template2.py and their use in check.py).

They run with Python 3 alone: a stub stands for `una`, and nothing goes to the network.

  python3 -B scripts/test_template2.py
"""

import sys

sys.dont_write_bytecode = True

import hashlib  # noqa: E402
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
# the normalization removes; `run .` prints each `print("...")`, prints its environment's names
# when a file holds `PRINTENV`, and writes a failing file into src/ when one holds `WRITESRC`;
# `test .` fails when a file holds `FAILTEST`. In a template 1 page of check.py's own fixture
# (src/main.una), it hands over to check.py's stub, `una1` beside it.
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
    if any("PRINTENV" in text for _, text in files):
        print(" ".join(sorted(os.environ)))
    if any("WRITESRC" in text for _, text in files):
        open("src/zz.una", "w").write("FAILTEST\n")
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

OUTPUT = "ok      2 x LAMP-01\nreject  no product has the SKU CHAIR-09\n"

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

```text include="day-to-day/expected/output.txt"
```

You will learn to:

- declare an error kind.
:::

## Why it works this way

{lead}

> [!KEY]
> A key idea.

## 6.1 Declaring a failure

### A quantity that can be wrong

{lead}

### A first failing function

```una title="steps/01-quantity/src/quantity.una" verified="check, run" include="steps/01-quantity/src/quantity.una"
```

`una run .` prints:

```text include="steps/01-quantity/expected/output.txt"
```

### How `fail` ends a function

{lead}

## 6.2 Handling a failure

### The five clauses

{lead}

### Translating between layers

```una include="steps/02-translate/src/translate.una#translate" verified="check"
```

### Recovering with a default

{lead}

## 6.3 Failures as values

### Keeping an outcome

{lead}

### A batch that goes on

```diff include="steps/02-translate..steps/03-defaults:src/translate.una"
```

### Choosing a clause

See [the errors](/docs/errors/U3007/) and [What you'll build](#what-youll-build).

## 6.4 Day-to-day: order intake

### The kinds of an order

```una include="day-to-day/src/orders.una#Order" caption="the kinds" title="src/orders.una"
```

### The report

```una include="day-to-day/src/orders.una#reason..describe" verified="check, run, test"
```

### Running the program

```sh
cd 06-failure/day-to-day
una run .
```

## 6.5 Testing it

### An example per path

```una include="day-to-day/src/orders.una#L36-L38"
```

### Running the examples

```text include="day-to-day/expected/commands/test.txt"
```

## 6.6 Common mistakes

{mistakes}
## 6.7 Exercises

{exercises}
## 6.8 Recap and reference

### For agents

:::agents
Run `una --json check .`.
:::

### Recap

:::recap
- One.
- Two.
- Three.
- Four.
- Five.
:::

### Reference

:::reference
- [fails](/docs/reference/language/errors/fails/)
:::
"""

MISTAKE = """### Forgetting clause {n} (U3007)

:::mistake
Remove clause {n}.

```diff include="day-to-day..mistakes/{n}:src/orders.una" context="1"
```

```text include="mistakes/{n}/expected/rendered.txt"
```

*Fix:* add the clause.
:::

"""

EXERCISE = """### Exercise {n}: extend the program

::::exercise
Extend the program.

:::hint
*Hint:* look at `reason`.
:::

:::answer Answer
```una include="exercises/{n}/answer/src/orders.una#shipped" verified="check, run, test"
```
:::
::::

"""


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def package(directory, src_name, src, output, toml=TOML):
    write(os.path.join(directory, "una.toml"), toml)
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
    package(day, "orders.una", ORDERS, OUTPUT)
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
        wanted = f'\nexample "shipped gives {n}"\n  do shipped({n})\n  expect result == {n}\n'
        write(os.path.join(exercise, "start", "base.txt"), "day-to-day\n")
        write(os.path.join(exercise, "start", "src", "orders.una"), ORDERS + wanted.replace("expect", "expect FAILTEST"))
        write(os.path.join(exercise, "start", "expected", "output.txt"), OUTPUT)
        write(os.path.join(exercise, "answer", "base.txt"), "day-to-day\n")
        write(os.path.join(exercise, "answer", "src", "orders.una"),
              ORDERS + f"\n--- How many units ship.\npub shipped(n: Int) -> Int = {n}\n" + wanted)
        write(os.path.join(exercise, "answer", "expected", "output.txt"), OUTPUT)
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
        self.assertEqual(template2.declaration_name("pub measure Meter"), "Meter")
        self.assertIsNone(template2.declaration_name('example "a line"'))

    def test_lines(self):
        self.assertEqual(template2.select("a\nb\nc\nd\n", "L2-L3")[0], "b\nc\n")
        self.assertEqual(template2.select("a\nb\nc\nd\n", "L1,L4")[0], "a\nd\n")
        self.assertIn("not within", template2.select("a\n", "L2")[1])
        self.assertIn("ascending", template2.select("a\nb\nc\nd\n", "L3,L1")[1])
        self.assertIn("ascending", template2.select("a\nb\nc\nd\n", "L1-L3,L2")[1])
        self.assertIn("only on an expected/ file", template2.select("a\nb\n", "L1,L2", several=False)[1])

    def test_normalize(self):
        package = os.path.join(tempfile.gettempdir(), "pkg")
        text = f"x  \r\n  at {package}/src/a.una\n in {package}\t\n\n\n"
        self.assertEqual(template2.normalize(text, package), "x\n  at src/a.una\n in .\n")
        self.assertEqual(template2.normalize("", package), "")

    def test_fences(self):
        text = '````una include="a b/c.una#f" title="x" verified="check, run"\n```\n````\n\nprose\n\n```sh\nuna run .\n```\n'
        blocks, inside = template2.fences(text)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0].lang, "una")
        self.assertEqual(blocks[0].attrs, {"include": "a b/c.una#f", "title": "x", "verified": "check, run"})
        self.assertEqual(blocks[0].body, "```\n")
        self.assertEqual(blocks[1].lang, "sh")
        self.assertNotIn(4, inside)
        self.assertEqual(template2.fences('```una include="x" stray\n```\n')[0][0].stray, ["stray"])
        self.assertEqual(template2.fences("```una include=x\n```\n")[0][0].stray, ["include=x"])
        self.assertEqual(template2.fences('```una verified="check" verified="test"\n```\n')[0][0].duplicates, ["verified"])
        self.assertFalse(template2.fences("```una\nno end\n")[0][0].closed)

    def test_links(self):
        failures = check.Failures()
        template2.links("[a](/docs/x/) [b](#top) [c](https://example.org/) `https://github.com/una-lang/una/blob/main/x`", "p", failures)
        self.assertEqual(failures.items, [])
        for bad, wants in (
            ("[a](https://github.com/una-lang/una/blob/main/docs/guide/x.md)", "repositories"),
            ("see https://github.com/una-lang/una/tree/main/docs", "repositories"),
            ("[a](../05-collections/)", "relative link"),
            ('[a](../05-collections/README.md "Collections")', "relative link"),
            ("[a](http://example.org/)", "https"),
            ("[a]: https://raw.githubusercontent.com/una-lang/una/main/x", "repositories"),
        ):
            failures = check.Failures()
            template2.links(bad, "p", failures)
            self.assertTrue(any(wants in item for item in failures.items), (bad, failures.items))

    def test_markup(self):
        def found(text):
            failures = check.Failures()
            template2.markup(text, "p", failures)
            return "\n".join(failures.items)

        self.assertEqual(found("Text.\n\n- a\n  - b\n\n> [!NOTE] Title.\n> Body.\n\n:::steps\n1. **x**\n   more\n:::\n\n---\n"), "")
        self.assertIn("inside a quote", found("> [!NOTE]\n> ```una\n> BAD\n> ```\n"))
        self.assertIn("inside a quote", found("- First:\n  - then:\n\n    ```una\n    nonsense\n    ```\n"))
        self.assertIn("indented by 4", found("Text.\n\n    pub main() -> Unit = nonsense\n"))
        self.assertIn("a tab in the indentation", found("Text.\n\n\tnonsense\n"))
        self.assertIn("setext", found("An extra part\n-------------\n"))
        self.assertIn("setext", found("An extra part\n===\n"))
        self.assertIn("heading", found("> ## A heading in a quote\n"))
        self.assertIn("heading", found(" ## Indented\n"))
        self.assertIn("raw HTML", found("Some <pre>code</pre>.\n"))
        self.assertEqual(found("An autolink <https://example.org/> and `<T>` in code.\n"), "")
        self.assertIn("no container :::demo", found(":::demo\nx\n:::\n"))
        self.assertIn("no callout [!DANGER]", found("> [!DANGER]\n> x\n"))
        self.assertIn("not closed", found(":::build\nx\n"))

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
        # The tail before the section rules passes here; structure() reports it.
        old_tail = body[:body.index("## 6.7 Exercises")] + "## 6.7 For agents\n\n## 6.8 Exercises\n\n## 6.9 Recap\n\n## 6.10 Reference\n"
        failures = check.Failures()
        self.assertEqual(template2.headings(fields, old_tail, "p", failures), 3)
        self.assertEqual(failures.items, [])
        fewer = body.replace("## 6.3 Failures as values", "### Failures as values")
        for n in range(4, 11):
            fewer = fewer.replace(f"## 6.{n} ", f"## 6.{n - 1} ")
        failures = check.Failures()
        template2.headings(fields, fewer, "p", failures)
        self.assertTrue(any("the parts must be" in item for item in failures.items), failures.items)

    def test_structure(self):
        page = PAGE.format(lead="x", mistakes="", exercises="")
        fields, body = check.front_matter(page)
        failures = check.Failures()
        self.assertEqual(template2.structure(body, 3, "p", failures), [])
        # A `### ` line inside a fenced block is code, not a subsection.
        fenced = body.replace("### How `fail` ends a function\n", '```text include="steps/01-quantity/expected/output.txt"\n### How `fail` ends a function\n```\n')
        problems = template2.structure(fenced, 3, "p", failures)
        self.assertEqual(problems, ["`6.1 Declaring a failure` has 2 `### ` subsections; a concept section has 3 to 12"])
        self.assertEqual(failures.items, ["p: " + problems[0]])
        # A `#### ` part does not count as a subsection.
        deeper = body.replace("### How `fail` ends a function", "#### How `fail` ends a function")
        self.assertEqual(len(template2.structure(deeper, 3, "p", check.Failures())), 1)

    def test_quoted_lists(self):
        fields, _ = check.front_matter('---\nnav: ["checked, and the escape budget", "Maps"]\ncodes: [U0101, U0102]\n---\nx\n')
        self.assertEqual(fields["nav"], ["checked, and the escape budget", "Maps"])
        self.assertEqual(fields["codes"], ["U0101", "U0102"])
        for value in ('["a", b]', '["a"b"]', '["a",]', '["a" "b"]'):
            self.assertIsNone(check.front_matter(f"---\nnav: {value}\n---\nx\n")[0], value)

    def test_caption_only_in_the_opener(self):
        english = check.skeleton('```una\nlet caption="Total"\n```\n')
        translated = check.skeleton('```una\nlet caption="Anything"\n```\n')
        self.assertNotEqual(english, translated)
        self.assertEqual(check.skeleton('```una caption="the kinds"\nx\n```\n'), check.skeleton('```una caption="os tipos"\nx\n```\n'))

    def test_manifest(self):
        base = tempfile.mkdtemp(prefix="una-by-example-manifest-")
        try:
            for toml, good in (
                (TOML, True),
                (TOML.replace('["console"]', '["console", "clock", "files:src:read,write", "files:src/data:read"]'), True),
                (TOML.replace('["console"]', '["console", "env"]'), False),
                (TOML.replace('["console"]', '["files:/:read,write"]'), False),
                (TOML.replace('["console"]', '["files:src/..:read"]'), False),
                (TOML.replace('["console"]', '["http:https://collector.example.invalid"]'), False),
                (TOML + '\n[dependencies]\nother = { path = "../.." }\n', False),
                (TOML.replace('[run]\n', '[run]\nflags = ["x"]\n'), False),
            ):
                write(os.path.join(base, "una.toml"), toml)
                failures = check.Failures()
                self.assertEqual(check.manifest(base, "p", failures), good, (toml, failures.items))
        finally:
            shutil.rmtree(base, ignore_errors=True)

    def test_commands(self):
        for line in ("test .", "--json check .", "run .", "fmt --check .", "fix --dry-run .", "build .",
                     "explain U5001", "trace SOLD_OUT_1"):
            self.assertTrue(check.COMMAND.match(line), line)
        for line in ("run . --grant env", "run . --grant files:/:read", "fmt /abs/path", "check ..", "test . extra", "run"):
            self.assertFalse(check.COMMAND.match(line), line)

    def test_environment(self):
        base = tempfile.mkdtemp(prefix="una-by-example-env-")
        saved = os.environ.get("UNA_NEUTRALITY_PATTERN")
        os.environ["UNA_NEUTRALITY_PATTERN"] = "zebra-canary"
        try:
            write(os.path.join(base, "una"), STUB)
            os.chmod(os.path.join(base, "una"), 0o755)
            write(os.path.join(base, "pkg", "src", "a.una"), "-- PRINTENV\n")
            names = set(check.run(os.path.join(base, "una"), ["run", "."], os.path.join(base, "pkg")).stdout.decode().split())
            self.assertNotIn("UNA_NEUTRALITY_PATTERN", names)
            self.assertTrue({"PATH", "HOME", "TMPDIR", "LANG", "NO_COLOR"} <= names, names)
            # What Python or the system adds on its own, at most.
            self.assertTrue(names <= {"PATH", "HOME", "TMPDIR", "LANG", "NO_COLOR", "LC_CTYPE", "__CF_USER_TEXT_ENCODING"}, names)
            self.assertNotEqual(check.una_env()["HOME"], os.path.expanduser("~"))
        finally:
            os.environ.pop("UNA_NEUTRALITY_PATTERN", None)
            if saved is not None:
                os.environ["UNA_NEUTRALITY_PATTERN"] = saved
            shutil.rmtree(base, ignore_errors=True)

    def test_round_two_markup(self):
        def found(text):
            failures = check.Failures()
            template2.markup(text, "p", failures)
            return "\n".join(failures.items)

        # $$ blocks, which the site renders as code.
        self.assertIn("`$$`", found("Text.\n\n$$\npub main() -> Unit = nonsense\n$$\n"))
        self.assertIn("`$$`", found("Text.\n$$\nnonsense\n$$\n"))
        self.assertIn("`$$`", found("- item\n  $$\n  nonsense\n  $$\n"))
        # A list or quote marker followed by 5 or more columns, or by a tab.
        for line in ("- item\n-     pub main() -> Unit = nonsense\n", "1.     pub main() -> Unit = nonsense\n",
                     "-\t\tpub main() -> Unit = nonsense\n", "- >     pub main() -> Unit = nonsense\n",
                     "> -     pub main() -> Unit = nonsense\n", ">      pub main() -> Unit = nonsense\n"):
            self.assertRegex(found(line), "columns after a list or quote marker|a tab in the indentation", line)
        self.assertEqual(found("-    four columns is a paragraph\n> - quote and list\n>    three after a quote\n"), "")
        # Invisible and control characters, a fence closer among them.
        for ch in ("\u00a0", "\u200b", "\u2028", "\u3000", "\x0c", "\ufeff"):
            self.assertIn(f"U+{ord(ch):04X}", found(f"Text{ch}here.\n"), repr(ch))
        self.assertEqual(found("Text with a\ttab inside.\n"), "")
        # Indented or spaced ::: lines.
        self.assertIn("a ::: line starts at column 0", found(" :::mistake\nx\n :::\n"))
        self.assertIn("a ::: line starts at column 0", found("> :::agents\n> x\n> :::\n"))
        self.assertIn("with the name right after the colons", found("::: mistake\nx\n:::\n"))
        self.assertIn("no container :::demo", found(":::demo\nx\n:::\n"))

    def test_a_closer_with_other_whitespace(self):
        for ch in ("\u00a0", "\x0c", "\u2000"):
            blocks, _ = template2.fences(f"```una\ncode\n```{ch}\nfree\n```\n")
            self.assertEqual(blocks[0].body, f"code\n```{ch}\nfree\n", repr(ch))
        self.assertEqual(template2.fences("```una\ncode\n``` \t\nprose\n")[0][0].body, "code\n")

    def test_round_two_links(self):
        for bad in ("\\`[src](https://github.com/una-lang/una/blob/main/x.una)`",
                    "[a](https://GitHub.com/una-lang/una/blob/main/x)",
                    "[a](https://github.com:443/una-lang/una/blob/main/x)",
                    "[a](HTTPS://WWW.GITHUB.COM/una-lang/una/tree/main/)"):
            failures = check.Failures()
            template2.links(bad, "p", failures)
            self.assertTrue(any("repositories" in i for i in failures.items), (bad, failures.items))
        failures = check.Failures()
        template2.links("`[a](https://github.com/una-lang/una/blob/main/x)` and ``[b](../x) `with` ticks``", "p", failures)
        self.assertEqual(failures.items, [])

    def test_round_two_manifests(self):
        base = tempfile.mkdtemp(prefix="una-by-example-manifest-")
        try:
            for toml in ('[[run]]\nentry = "x"\n', 'run = "x"\n', TOML.replace('["console"]', '["console\\n"]'),
                         TOML.replace('edition = "0.2"', 'edition = "0.2"\nextra = 1'), TOML.replace('["console"]', '"console"')):
                write(os.path.join(base, "una.toml"), toml)
                failures = check.Failures()
                self.assertFalse(check.manifest(base, "p", failures), toml)
                self.assertTrue(failures.items, toml)
        finally:
            shutil.rmtree(base, ignore_errors=True)

    def test_the_toml_reading_without_tomllib(self):
        document = check.plain_toml(TOML + '\n# a comment\n[contracts]\n"billing.charge" = ["@console: Console[print where not dry_run]"]\n')
        self.assertEqual(document["run"], {"entry": "orders", "grants": ["console"]})
        self.assertEqual(document["contracts"], {"billing.charge": ["@console: Console[print where not dry_run]"]})
        for text in ('x = 1\n', '[a]\nb = "c\\"d"\n', '[a]\nb = [1]\n', '[a]\nb.c = 1\n', '[a]\nb = { c = 1 }\n',
                     "[a]\nb = 'x'\n", '[a]\nb = 1\nb = 2\n', '[a]\n[a]\n', '[[run]]\n'):
            with self.assertRaises(ValueError, msg=text):
                check.plain_toml(text)
        try:
            import tomllib
        except ImportError:
            return
        self.assertEqual(document, tomllib.loads(TOML + '\n# a comment\n[contracts]\n"billing.charge" = ["@console: Console[print where not dry_run]"]\n'))

    def test_round_three_links(self):
        for bad in ("[s](https://github.com\\/una-lang/una/blob/main/x.una)",
                    "[s](https://github.com&#47;una-lang/una/blob/main/x.una)",
                    "[s](https://github.com/una&#45;lang/una/blob/main/x.una)",
                    "[s](https://x@github.com/una-lang/una/blob/main/x.una)",
                    "[s](https://github.com./una-lang/una/blob/main/x.una)",
                    "[s](HTTPS://GITHUB.COM/UNA-LANG/una/blob/main/x.una)",
                    "[s](https://github.com/%75na-lang/una/blob/main/x.una)",
                    "[s](//github.com/una-lang/una/blob/main/x.una)"):
            failures = check.Failures()
            template2.links(bad, "p", failures)
            self.assertTrue(any("repositories" in i for i in failures.items), (bad, failures.items))
        failures = check.Failures()
        template2.links("[a](https://example.org/una-lang/) [b](https://github.com/other/x) [c](/docs/x&#47;y/)", "p", failures)
        self.assertEqual(failures.items, [])

    def test_round_three_toml(self):
        for text in ('[package]\nname\u00a0= "x"\n', '[package]\nname = "x\x00"\n', '[package]\nname = "x" # a\rb\n',
                     '[package]\n\x0bname = "x"\n', '[package]\nname = "x"\u3000\n', '\u2028[package]\n',
                     '[package]\nname = "x"\r\n', '[escape_budget]\nchecked_per_module = 01\n', '[package]\nname = "x\x7f"\n'):
            with self.assertRaises(ValueError, msg=repr(text)):
                check.plain_toml(text)
        self.assertEqual(check.plain_toml('[package]\nname = "Ñandú"  # é\n'), {"package": {"name": "Ñandú"}})

    def test_a_fresh_home_per_run(self):
        first, second = check.una_env()["HOME"], check.una_env()["HOME"]
        self.assertNotEqual(first, second)
        self.assertEqual(os.path.dirname(first), check.una_home())

    def test_sh_lines(self):
        def found(body):
            failures = check.Failures()
            block = template2.fences(f"```sh\n{body}```\n")[0][0]
            template2.check_sh(block, "p", failures)
            return failures.items

        self.assertEqual(found("cd 06-failure/day-to-day\nmkdir orders\nuna run .\nuna --json check .\npython3 -B scripts/check.py --fill\n"), [])
        for line in ("una run .   ok 99 x LAMP-01  Total: 4200 cents", "una run . --grant env", "$ una run .",
                     "cd 06-failure; rm -rf x", "python3 -B scripts/check.py --una x", "ok 2 x LAMP-01"):
            self.assertTrue(found(line + "\n"), line)


class Chapters(Base):
    def setUp(self):
        super().setUp()
        self.chapter = chapter(self.root)
        self.readme = os.path.join(self.chapter, "README.md")

    def refill(self):
        template2.fill(self.root)

    def test_a_good_chapter(self):
        items, warnings = self.run_chapters()
        self.assertEqual(items, [])
        # The prose is short, so the targets give warnings, never failures.
        self.assertTrue(any("words" in w for w in warnings), warnings)
        # A concept section without a check-yourself question warns, and does not fail.
        self.assertTrue(any("`6.1 Declaring a failure` has no `### Check yourself: <topic>` subsection" in w for w in warnings), warnings)

    def test_fill_wrote_the_blocks(self):
        text = check.read(self.readme)
        self.assertIn('```text include="day-to-day/expected/output.txt"\nok      2 x LAMP-01\n', text)
        self.assertIn("--- One line of an order.\npub kind Order\n  sku: Text\n  quantity: Int\n```", text)
        self.assertIn("--- a/src/translate.una\n+++ b/src/translate.una\n", text)
        changed, problems = template2.fill(self.root)
        self.assertEqual((changed, problems), ([], []))

    # Blocks that are not includes, and code the check would not see (H1, M1).

    def test_a_free_una_block(self):
        edit(self.readme, "```sh\ncd 06-failure/day-to-day\nuna run .\n```", "```una\nmain()\n```")
        self.assertFails("not an include")

    def test_a_free_text_block(self):
        edit(self.readme, "```sh\ncd 06-failure/day-to-day\nuna run .\n```", "```text\nok\n```")
        self.assertFails("not an include")

    def test_a_tilde_fence(self):
        edit(self.readme, "```sh\ncd 06-failure/day-to-day\nuna run .\n```", "~~~una\nnonsense\n~~~")
        self.assertFails("not an include")

    def test_a_fence_in_a_callout(self):
        edit(self.readme, "> A key idea.", "> A key idea.\n> ```una\n> pub main() -> Unit = BAD\n> ```")
        self.assertFails("a fenced block inside a quote")

    def test_a_fence_in_a_list(self):
        edit(self.readme, "- declare an error kind.", "- First:\n  - then:\n\n    ```una\n    pub main() -> Unit = nonsense\n    ```")
        self.assertFails("a fenced block inside a quote")

    def test_indented_code(self):
        edit(self.readme, "## 6.2 Handling a failure\n", "## 6.2 Handling a failure\n\nText.\n\n    pub main() -> Unit = nonsense\n")
        self.assertFails("indented by 4 or more spaces")

    def test_output_in_an_sh_block(self):
        edit(self.readme, "una run .\n```", "una run .\nTotal: 4200 cents\n```")
        self.assertFails("an `sh` block holds only commands")

    def test_a_prompt_in_an_sh_block(self):
        edit(self.readme, "una run .\n```", "$ una run .\n```")
        self.assertFails("an `sh` block holds only commands")

    def test_a_setext_heading(self):
        edit(self.readme, "## 6.2 Handling a failure\n", "## 6.2 Handling a failure\n\nAn extra part\n-------------\n")
        self.assertFails("a setext heading")

    def test_raw_html(self):
        edit(self.readme, "## 6.2 Handling a failure\n", "## 6.2 Handling a failure\n\n<pre>nonsense</pre>\n")
        self.assertFails("raw HTML")

    def test_an_unknown_container(self):
        edit(self.readme, ":::agents", ":::demo")
        self.assertFails("no container :::demo")

    # Round two: code the site renders that the check would not see.

    def test_a_math_block(self):
        edit(self.readme, "## 6.2 Handling a failure\n", "## 6.2 Handling a failure\n\nText.\n$$\npub main() -> Unit = nonsense\n$$\n")
        self.assertFails("a `$$` line")

    def test_a_marker_and_five_columns(self):
        edit(self.readme, "- declare an error kind.", "- declare an error kind.\n-     pub main() -> Unit = nonsense")
        self.assertFails("columns after a list or quote marker")

    def test_a_closer_with_a_no_break_space_in_a_card(self):
        text = check.read(self.readme)
        at = text.index('```text include="mistakes/1/expected/rendered.txt"')
        close = text.index("\n```\n", at) + 1
        write(self.readme, text[:close] + "```\u00a0\n*Fix:* use pub main() -> Unit = nonsense\n" + text[close + 4:])
        self.assertFails("U+00A0")
        self.assertFails('is not the text of include=mistakes/1/expected/rendered.txt')

    def test_a_closer_with_a_form_feed_at_the_end(self):
        with open(self.readme, "a", encoding="utf-8") as handle:
            handle.write('\n```text include="day-to-day/expected/output.txt"\n' + OUTPUT + "```\x0c\npub main() -> Unit = nonsense\n")
        self.assertFails("U+000C")

    def test_an_indented_card(self):
        edit(self.readme, ":::agents\n", " :::mistake\n```text include=\"mistakes/2/expected/rendered.txt\"\n```\n :::\n\n:::agents\n")
        self.refill()
        self.assertFails("a ::: line starts at column 0")

    def test_a_symlinked_readme(self):
        outside = os.path.join(self.base, "README.md")
        shutil.move(self.readme, outside)
        os.symlink(outside, self.readme)
        self.assertFails("06-failure/README.md: a symbolic link")

    # Includes (H4, M4, M5, M7, L6).

    def test_a_block_that_differs(self):
        edit(self.readme, "  sku: Text\n  quantity: Int\n```", "  sku: Text\n  quantity: Nat\n```")
        self.assertFails('is not the text of include=day-to-day/src/orders.una#Order')

    def test_a_changed_package(self):
        edit(os.path.join(self.chapter, "steps", "01-quantity", "src", "quantity.una"), "--- A step", "--- One step")
        self.assertFails("is not the text of include=steps/01-quantity/src/quantity.una")

    def test_a_missing_declaration(self):
        edit(self.readme, "#reason..describe", "#explain")
        self.assertFails("no top-level declaration `explain`")

    def test_a_path_outside_the_packages(self):
        edit(self.readme, 'include="steps/01-quantity/expected/output.txt"', 'include="../../una.lock"')
        self.assertFails("is not a plain path")
        edit(self.readme, 'include="../../una.lock"', 'include="README.md"')
        self.assertFails("is not in a package")

    def test_a_made_up_expected_file(self):
        write(os.path.join(self.chapter, "day-to-day", "expected", "made-up.txt"), "ok   99 x LAMP-01\n")
        edit(self.readme, 'include="steps/01-quantity/expected/output.txt"', 'include="day-to-day/expected/made-up.txt"')
        self.refill()
        self.assertFails("day-to-day/expected/made-up.txt: not a file a package holds")
        self.assertFails("a block shows una.toml, src/**/*.una or an expected/ file")

    def test_a_file_outside_src(self):
        write(os.path.join(self.chapter, "day-to-day", "notes.una"), "pub main() -> Unit = nonsense\n")
        edit(self.readme, 'include="steps/02-translate/src/translate.una#translate"', 'include="day-to-day/notes.una"')
        self.refill()
        self.assertFails("day-to-day/notes.una: not a file a package holds")

    def test_verified_on_an_expected_file(self):
        edit(self.readme, '```text include="steps/01-quantity/expected/output.txt"', '```text include="steps/01-quantity/expected/output.txt" verified="check"')
        self.assertFails("verified= goes only on a block of una.toml or a src/ file")

    def test_verified_on_lines(self):
        edit(self.readme, '#L36-L38"', '#L36-L38" verified="check"')
        self.assertFails("verified= goes only on a block of una.toml or a src/ file")

    def test_lines_out_of_order(self):
        edit(self.readme, '#L36-L38"', '#L9,L19,L18"')
        self.assertFails("several line ranges are allowed only on an expected/ file")

    def test_an_unknown_attribute(self):
        edit(self.readme, 'caption="the kinds"', 'captoin="the kinds"')
        self.assertFails("no fence attribute `captoin`")

    def test_an_unquoted_attribute(self):
        edit(self.readme, 'caption="the kinds"', "caption=kinds")
        self.assertFails("attributes are key=\"value\", quoted")

    def test_a_duplicate_attribute(self):
        edit(self.readme, 'verified="check, run" include="steps/01-quantity', 'verified="check, run" verified="check" include="steps/01-quantity')
        self.assertFails("the attribute `verified` is given twice")

    def test_a_wrong_title(self):
        edit(self.readme, 'title="src/orders.una"', 'title="exercises/1/answer/src/orders.una"')
        self.assertFails("is not the included file's path")

    def test_a_diff_of_a_dotted_path(self):
        edit(self.readme, 'include="day-to-day..mistakes/1:src/orders.una"', 'include="day-to-day..mistakes/1:src/../una.toml"')
        self.assertFails("is not a file a block may show")

    def test_a_fence_the_text_would_close(self):
        edit(os.path.join(self.chapter, "steps", "01-quantity", "expected", "output.txt"), "quantity 3\n", "quantity 3\n```\n")
        self.refill()
        self.assertFails("use a longer fence")

    def test_a_wrong_diff(self):
        edit(os.path.join(self.chapter, "steps", "03-defaults", "src", "translate.una"), "translate 2", "translate 3")
        self.assertFails("is not the text of include=steps/02-translate..steps/03-defaults:src/translate.una")

    # Outcomes and badges.

    def test_a_wrong_rendering(self):
        edit(os.path.join(self.chapter, "mistakes", "2", "expected", "rendered.txt"), "Error:", "error:")
        self.assertFails("mistakes/2/expected/rendered.txt: is not what `una --color never check .` prints")

    def test_a_wrong_diagnostic(self):
        edit(os.path.join(self.chapter, "mistakes", "3", "expected", "diagnostics.txt"), ":15:3:", ":16:3:")
        self.assertFails("06-failure/mistakes/3: `una check` reports")

    def test_verified_check_on_a_mistake(self):
        edit(self.readme, '```text include="mistakes/1/expected/rendered.txt"\n', '```text include="mistakes/1/expected/rendered.txt"\n```\n\n```una include="mistakes/1/src/orders.una#parse_order" verified="check"\n')
        self.refill()
        self.assertFails("verified=check, but mistakes/1 does not check clean")

    def test_verified_test_that_fails(self):
        edit(os.path.join(self.chapter, "day-to-day", "src", "orders.una"), "expect result.quantity == 2", "expect FAILTEST")
        self.refill()
        self.assertFails("verified=test, but `una test .` exits with 1 in day-to-day")

    def test_verified_run_without_output(self):
        edit(self.readme, '```text include="mistakes/1/expected/rendered.txt"\n', '```text include="mistakes/1/expected/rendered.txt"\n```\n\n```una include="mistakes/1/src/orders.una#reason" verified="run"\n')
        self.refill()
        self.assertFails("verified=run, but mistakes/1 has no expected/output.txt")

    def test_a_mistake_that_checks_clean(self):
        mistake = os.path.join(self.chapter, "mistakes", "4")
        os.remove(os.path.join(mistake, "expected", "diagnostics.txt"))
        write(os.path.join(mistake, "expected", "output.txt"), OUTPUT)
        self.assertFails("a mistake has expected/diagnostics.txt")

    # Exercises (L5).

    def test_an_answer_that_fails_its_tests(self):
        edit(os.path.join(self.chapter, "exercises", "2", "answer", "src", "orders.una"), "expect result.quantity == 2", "expect FAILTEST")
        self.assertFails("exercises/2/answer: an answer passes its tests, but `una test .` exits with 1")

    def test_a_start_that_passes(self):
        shutil.rmtree(os.path.join(self.chapter, "exercises", "2", "start", "src"))
        shutil.rmtree(os.path.join(self.chapter, "exercises", "2", "start", "expected"))
        self.assertFails("exercises/2/start: the exercise's examples fail on start/")

    def test_an_exercise_without_an_answer(self):
        shutil.rmtree(os.path.join(self.chapter, "exercises", "3", "answer"))
        self.assertFails("exercises/3: no answer/")

    def test_an_exercise_without_a_start(self):
        shutil.rmtree(os.path.join(self.chapter, "exercises", "1", "start"))
        self.assertFails("exercises/1: no start/")

    def test_an_answer_that_changes_nothing(self):
        shutil.rmtree(os.path.join(self.chapter, "exercises", "1", "answer", "src"))
        shutil.rmtree(os.path.join(self.chapter, "exercises", "1", "answer", "expected"))
        self.assertFails("an answer changes something")

    def test_a_run_that_writes_does_not_change_the_tests(self):
        # The answer's `una run` writes a failing file into src/; `una test` runs on its own copy.
        edit(os.path.join(self.chapter, "exercises", "1", "answer", "src", "orders.una"), "--- How many units ship.", "-- WRITESRC\n\n--- How many units ship.")
        self.assertPasses()

    # Cards and counts (M6, L5).

    def test_a_mistake_not_on_the_page(self):
        text = check.read(self.readme)
        start = text.index(":::mistake\nRemove clause 4.")
        write(self.readme, text[:start] + text[text.index(":::\n\n", start) + 5:])
        self.assertFails("`Common mistakes` has 3 :::mistake blocks, but there are 4 mistakes/N")

    def test_too_few_mistakes(self):
        shutil.rmtree(self.base)
        os.makedirs(self.root)
        write(os.path.join(self.root, "una.lock"), 'version = "9.9.9"\n')
        write(self.una, STUB)
        os.chmod(self.una, 0o755)
        chapter(self.root, mistakes=3, exercises=2)
        self.assertFails("3 mistakes; the template asks for 4 to 8")
        self.assertFails("2 exercises; the template asks for 3 to 5")

    def test_cards_that_show_another_mistake(self):
        text = check.read(self.readme)
        one = text.index("```diff include=\"day-to-day..mistakes/1")
        two = text.index("```diff include=\"day-to-day..mistakes/2")
        end_one = text.index("*Fix:*", one)
        end_two = text.index("*Fix:*", two)
        first, second = text[one:end_one], text[two:end_two]
        write(self.readme, text[:one] + second + text[end_one:two] + first + text[end_two:])
        self.assertFails("mistake 1 shows ['mistakes/2']")

    def test_a_card_without_its_diagnostic(self):
        edit(self.readme, '```text include="mistakes/3/expected/rendered.txt"', '```text include="mistakes/3/expected/diagnostics.txt"')
        self.refill()
        self.assertFails("mistake 3 shows its diagnostic")

    def test_an_exercise_without_its_answer_block(self):
        edit(self.readme, 'include="exercises/2/answer/src/orders.una#shipped"', 'include="exercises/1/answer/src/orders.una#shipped"')
        self.refill()
        self.assertFails("exercise 2 shows ['exercises/1/answer']")
        self.assertFails("exercise 2 has a :::answer that shows exercises/2/answer")

    def test_the_build_output_by_substring(self):
        edit(self.readme, '```text include="day-to-day/expected/output.txt"', '```text include="steps/01-quantity/expected/output.txt"')
        edit(self.readme, "The program prints:", "The program prints `include=day-to-day/expected/output.txt`:")
        self.refill()
        self.assertFails("`What you'll build` shows the day-to-day program's output")

    # Links, codes, layout, manifests, symbolic links (M2, M3, H3).

    def test_a_link_to_github_main(self):
        edit(self.readme, "(/docs/errors/U3007/)", "(https://github.com/una-lang/una/blob/main/docs/guide/errors.md)")
        self.assertFails("links to the repositories")

    NAV = '["Declaring a failure", "Handling a failure", "Failures as values", "Day-to-day: order intake", ' \
          '"Testing it", "Common mistakes", "Exercises", "Recap and reference"]'

    def with_nav(self, labels):
        edit(self.readme, "template: 2\n", f"template: 2\nnav: {labels}\n")

    def test_nav(self):
        self.with_nav(self.NAV)
        self.assertPasses()

    def test_nav_with_commas_and_32_characters(self):
        self.with_nav(self.NAV.replace('"Declaring a failure"', '"fails, fail and the clauses abcd"'))
        self.assertPasses()

    def test_nav_with_a_label_too_few(self):
        self.with_nav(self.NAV.replace(', "Recap and reference"', ""))
        self.assertFails("`nav` has 7 labels, but the page has 8 numbered sections (6.1 to 6.8)")

    def test_nav_with_a_label_too_many(self):
        self.with_nav(self.NAV.replace('"Recap and reference"', '"Recap and reference", "More"'))
        self.assertFails("`nav` has 9 labels, but the page has 8 numbered sections")

    def test_nav_with_a_long_label(self):
        self.with_nav(self.NAV.replace('"Declaring a failure"', '"Declaring a failure: fails and fail"'))
        self.assertFails("has 35 characters, more than 32")

    def test_nav_with_an_empty_label(self):
        self.with_nav(self.NAV.replace('"Exercises"', '""'))
        self.assertFails("`nav` label 7 (for 6.7) is empty")

    def test_nav_with_spaces_at_the_ends(self):
        self.with_nav(self.NAV.replace('"Exercises"', '" Exercises"'))
        self.assertFails("has spaces at its ends")

    def test_nav_with_markup(self):
        original = check.read(self.readme)
        for label in ("`fails`", "a ~ b", "a < b", "a > b"):
            write(self.readme, original)
            self.with_nav(self.NAV.replace('"Declaring a failure"', f'"{label}"'))
            self.assertFails("a label is plain text")

    def test_nav_with_an_invisible_character(self):
        self.with_nav(self.NAV.replace('"Declaring a failure"', '"Declaring\u00a0a failure"'))
        self.assertFails("holds a control, format or invisible character")

    def test_nav_with_a_section_number(self):
        self.with_nav(self.NAV.replace('"Declaring a failure"', '"6.1 Declaring a failure"'))
        self.assertFails("starts with a section number")

    def test_nav_that_is_not_a_list(self):
        self.with_nav('"Declaring a failure"')
        self.assertFails("`nav` is a list of quoted labels")

    def test_nav_with_a_quote_inside(self):
        self.with_nav(self.NAV.replace('"Declaring a failure"', '"the "fails" clause"'))
        self.assertFails("its front matter does not parse")

    def test_another_optional_field(self):
        edit(self.readme, "template: 2\n", "template: 2\nsidebar: x\n")
        self.assertFails("the front matter has no field `sidebar`")

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
        edit(self.readme, "## 6.8 Recap and reference", "## 6.8 Recap")
        self.assertFails("the parts must be")

    # Inside a section: subsections, one per card, and the closing section.

    def legacy(self):
        """The fixture's page with the tail before the section rules: For agents, Recap and
        Reference as sections of their own, and For agents before Exercises."""
        text = check.read(self.readme)
        exercises = text[text.index("## 6.7 Exercises\n"):text.index("## 6.8 Recap and reference\n")]
        closing = text[text.index("## 6.8 Recap and reference\n"):]
        agents = closing[closing.index(":::agents"):closing.index("### Recap")]
        recap = closing[closing.index(":::recap"):closing.index("### Reference")]
        reference = closing[closing.index(":::reference"):]
        tail = ("## 6.7 For agents\n\n" + agents + exercises.replace("## 6.7 Exercises", "## 6.8 Exercises")
                + "## 6.9 Recap\n\n" + recap + "## 6.10 Reference\n\n" + reference)
        write(self.readme, text[:text.index("## 6.7 Exercises\n")] + tail)

    def test_the_old_tail_fails(self):
        self.legacy()
        self.assertFails("For agents, Recap and Reference are one closing section, `## 6.8 Recap and reference`")

    def test_a_concept_section_with_two_subsections(self):
        edit(self.readme, "### How `fail` ends a function\n\n", "")
        self.assertFails("`6.1 Declaring a failure` has 2 `### ` subsections; a concept section has 3 to 12")

    def test_a_concept_section_with_thirteen_subsections(self):
        edit(self.readme, "### Recovering with a default\n", "### Recovering with a default\n\n" + "".join(
            f"Text.\n\n### Further case {n}\n\n" for n in range(1, 11)))
        self.assertFails("`6.2 Handling a failure` has 13 `### ` subsections")

    def test_a_generic_subsection_title(self):
        edit(self.readme, "### The five clauses", "### Overview")
        self.assertFails("`### Overview` (line")

    def test_a_mistake_without_its_subsection(self):
        edit(self.readme, "### Forgetting clause 2 (U3007)\n\n", "")
        self.assertFails("`6.6 Common mistakes` has one `### ` subsection per :::mistake card, titled by the mistake, with its card in it; found 3 subsections for 4 cards")

    def test_two_mistakes_under_one_subsection(self):
        edit(self.readme, "### Forgetting clause 3 (U3007)\n\n", "")
        edit(self.readme, "## 6.7 Exercises\n", "### A subsection with no card\n\nText.\n\n## 6.7 Exercises\n")
        self.assertFails("found 4 subsections for 4 cards")

    def test_an_exercise_subsection_without_its_card(self):
        edit(self.readme, "## 6.8 Recap and reference\n", "### Exercise 4: more\n\nText.\n\n## 6.8 Recap and reference\n")
        self.assertFails("`6.7 Exercises` has one `### ` subsection per :::exercise card")

    def test_a_closing_section_with_another_subsection(self):
        edit(self.readme, "### Reference\n", "### Links\n")
        self.assertFails("`6.8 Recap and reference` holds exactly `### For agents`, `### Recap` and `### Reference`")

    def test_a_closing_section_out_of_order(self):
        text = check.read(self.readme)
        closing = text[text.index("### For agents"):]
        agents = closing[:closing.index("### Recap")]
        recap = closing[closing.index("### Recap"):closing.index("### Reference")]
        write(self.readme, text[:text.index("### For agents")] + recap + agents + closing[closing.index("### Reference"):])
        self.assertFails("holds exactly `### For agents`, `### Recap` and `### Reference`, in order")

    def test_text_before_the_closing_subsections(self):
        edit(self.readme, "## 6.8 Recap and reference\n", "## 6.8 Recap and reference\n\nA few words.\n")
        self.assertFails("and text before them")

    def test_a_day_to_day_with_one_subsection(self):
        edit(self.readme, "### The report\n\n", "")
        edit(self.readme, "### Running the program\n\n", "")
        self.assertFails("`6.4 Day-to-day: order intake` has 1 `### ` subsections; it has at least 2")

    def test_a_testing_section_with_one_subsection(self):
        edit(self.readme, "### Running the examples\n\n", "")
        self.assertFails("`6.5 Testing it` has 1 `### ` subsections; it has at least 2")

    def test_a_generic_title_outside_the_concept_sections(self):
        edit(self.readme, "### The report", "### Details")
        self.assertFails("`### Details` (line")

    def test_a_generic_title_with_an_article(self):
        edit(self.readme, "### The five clauses", "### An overview")
        self.assertFails("`### An overview` (line")

    def test_a_generic_part(self):
        edit(self.readme, "### Recovering with a default\n\n{lead}".format(lead=LOREM), "### Recovering with a default\n\n#### Summary\n\n" + LOREM)
        self.assertFails("`### Summary` (line")

    def test_an_exercise_title_out_of_order(self):
        edit(self.readme, "### Exercise 2: extend the program", "### Exercise 7: extend the program")
        self.assertFails("subsection 2 is titled `### Exercise 2: <goal>`; found `### Exercise 7: extend the program`")

    def test_an_exercise_title_without_its_number(self):
        edit(self.readme, "### Exercise 1: extend the program", "### Extend the program")
        self.assertFails("subsection 1 is titled `### Exercise 1: <goal>`")

    def test_a_mistake_title_without_its_code(self):
        edit(self.readme, "### Forgetting clause 2 (U3007)", "### Forgetting clause 2")
        self.assertFails("`### Forgetting clause 2` ends with its code in parentheses")

    def test_a_mistake_title_with_two_codes(self):
        edit(self.readme, "### Forgetting clause 3 (U3007)", "### Forgetting clause 3 (U3007, U3007)")
        self.assertPasses()
        edit(self.readme, "### Forgetting clause 3 (U3007, U3007)", "### Forgetting clause 3 (U3007, U7002)")
        self.assertFails("names U7002, but mistakes/3 reports ['U3007']")

    def test_headings_are_not_prose(self):
        lines = [(0, "### A long title of many words here"), (1, "#### Another title"), (2, "Three words here.")]
        self.assertEqual(template2.words(lines, set()), 3)

    def test_a_mistake_title_with_another_code(self):
        edit(self.readme, "### Forgetting clause 3 (U3007)", "### Forgetting clause 3 (U9999)")
        self.assertFails("names U9999, but mistakes/3 reports ['U3007']")

    # Anchors.

    def test_a_dangling_link(self):
        edit(self.readme, "(#what-youll-build)", "(#what-you-build)")
        self.assertFails("the link #what-you-build names no heading of the chapter")

    def test_links_to_a_slug_and_to_a_number(self):
        edit(self.readme, "(#what-youll-build)", "(#forgetting-clause-2-u3007)")
        edit(self.readme, "- One.", "- One, as in [the report](#s6-4-2) and [Testing it](#s6-5).")
        self.assertPasses()

    def test_a_repeated_slug(self):
        edit(self.readme, "### Running the examples", "### The report")
        self.assertFails("`The report` has the id `the-report`, as an earlier heading does")

    def test_a_slug_like_a_section_number(self):
        edit(self.readme, "### Keeping an outcome", "### S6 1")
        self.assertFails("would take the id of a section number (`s6-1`)")

    def test_a_reserved_id_outside_the_closing_section(self):
        edit(self.readme, "### Keeping an outcome", "### Recap")
        self.assertFails("`Recap` (line")
        self.assertFails("takes the id `recap`")

    def test_the_slug_rule(self):
        self.assertEqual(template2.slug("Translating between layers with `error`"), "translating-between-layers-with-error")
        self.assertEqual(template2.slug("`if none` before `if error` (U0102)"), "if-none-before-if-error-u0102")
        self.assertEqual(template2.slug("What you'll build"), "what-youll-build")
        self.assertEqual(template2.slug("A function that fails: `parse_quantity`"), "a-function-that-fails-parsequantity")
        self.assertEqual(template2.slug("See [the errors](/docs/errors/U3007/) now"), "see-the-errors-now")

    def test_the_recap_is_counted_inside_the_closing_section(self):
        edit(self.readme, "- Five.\n", "")
        _, warnings = self.run_chapters()
        self.assertTrue(any("`Recap` has 4 bullets" in w for w in warnings), warnings)

    def test_a_grant_of_the_environment(self):
        edit(os.path.join(self.chapter, "day-to-day", "una.toml"), 'grants = ["console"]', 'grants = ["console", "env"]')
        self.assertFails("the grant 'env' is not allowed")

    def test_a_command_with_a_grant(self):
        write(os.path.join(self.chapter, "day-to-day", "expected", "commands", "env.txt"), "$ una run . --grant env\n")
        self.assertFails("is not one of the commands una-by-example runs")

    def test_a_symbolic_link(self):
        target = os.path.join(self.chapter, "steps", "01-quantity", "src", "quantity.una")
        os.remove(target)
        os.symlink(os.path.join(self.root, "una.lock"), target)
        self.assertFails("is a symbolic link or outside the chapter")

    def test_a_symbolic_link_nothing_includes(self):
        os.symlink(os.path.join(self.root, "una.lock"), os.path.join(self.chapter, "day-to-day", "src", "hosts.una"))
        self.assertFails("06-failure/day-to-day/src/hosts.una: a symbolic link")

    def test_a_blank_line_in_the_front_matter(self):
        edit(self.readme, "time: 35\n", "time: 35\n\n")
        edit(self.readme, "```sh\n", "```una\nnonsense\n```\n\n```sh\n")
        self.assertFails("its front matter does not parse")

    def test_another_template_value(self):
        for value in ("template: 02", "Template: 2", 'template: "2 "'):
            edit(self.readme, "template: 2", value)
            self.assertFails("`template` is exactly `template: 2`")
            edit(self.readme, value, "template: 2")

    def test_carriage_returns(self):
        write(self.readme, check.read(self.readme).replace("\n", "\r\n"))
        self.assertFails("carriage returns")

    def test_packages_without_the_template(self):
        text = check.read(self.readme)
        write(self.readme, "# 6 Failure\n\n" + text.split("# 6 Failure\n", 1)[1])
        self.assertFails("a chapter with steps/, day-to-day/, mistakes/, exercises/ is on template 2")

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
        self.assertIn("template 2: 1 chapters, 14 packages, 1 commands", out.getvalue())
        self.assertIn("warning: 06-failure/README.md", out.getvalue())


class Archives(Base):
    """The download archives of a repository with a template 1 chapter and a template 2 one."""

    def setUp(self):
        super().setUp()
        import archive

        self.archive = archive
        self.chapter = chapter(self.root)
        check.fixture(self.root)
        check.git(self.root, "init", "-q")
        check.git(self.root, "add", "-A")
        check.git(self.root, "commit", "-q", "-m", "c")
        self.out = os.path.join(self.base, "out")
        archive.build(self.root, self.out, 0)

    def members(self, name):
        import tarfile

        with tarfile.open(os.path.join(self.out, name), "r:gz") as handle:
            return {m.name: (m, handle.extractfile(m).read() if m.isfile() else None) for m in handle.getmembers()}

    def checked(self):
        out = io.StringIO()
        with redirect_stdout(out), redirect_stderr(out):
            code = check.check(self.root, self.una, False, self.out)
        return code, out.getvalue()

    def test_the_archives_pass(self):
        self.assertEqual(sorted(os.listdir(self.out)),
                         ["01-01-first.tar.gz", "06-failure.tar.gz", "SHA256SUMS", "una-by-example-9.9.9.tar.gz"])
        code, report = self.checked()
        self.assertEqual(code, 0, report)

    def test_a_chapter_archive_holds_whole_packages(self):
        found = self.members("06-failure.tar.gz")
        files = {n: d for n, (m, d) in found.items() if m.isfile()}
        self.assertEqual(files["06-failure/README.md"], check.read_bytes(os.path.join(self.chapter, "README.md")))
        # An overlay is resolved: its own file, and its base's others.
        self.assertEqual(files["06-failure/mistakes/1/src/orders.una"],
                         check.read_bytes(os.path.join(self.chapter, "mistakes", "1", "src", "orders.una")))
        for ref in ("mistakes/1", "exercises/1/start", "exercises/1/answer", "steps/01-quantity", "day-to-day"):
            self.assertIn(f"06-failure/{ref}/una.toml", files, ref)
            self.assertIn(f"06-failure/{ref}/verification.lock", files, ref)
        self.assertEqual(files["06-failure/exercises/1/answer/una.toml"], check.read_bytes(os.path.join(self.chapter, "day-to-day", "una.toml")))
        self.assertFalse([n for n in files if n.endswith("/base.txt") or "/expected/" in n])
        for member, _ in found.values():
            self.assertEqual((member.uid, member.gid, member.uname, member.gname, member.mtime), (0, 0, "", "", 0))
            self.assertIn(member.mode, (0o644, 0o755))
        whole = self.members("una-by-example-9.9.9.tar.gz")
        for name, data in files.items():
            self.assertEqual(whole[f"una-by-example-9.9.9/{name}"][1], data, name)
        self.assertIn("una-by-example-9.9.9/01-hello/README.md", whole)
        self.assertIn("una-by-example-9.9.9/01-hello/01-first/src/main.una", whole)

    def test_the_packages_the_check_runs_are_the_archived_ones(self):
        files = {n: d for n, (m, d) in self.members("06-failure.tar.gz").items() if m.isfile()}
        packages = template2.chapter_packages(self.chapter, "06-failure", check.Failures())
        self.assertEqual(len(packages), 14)
        for ref, package in packages.items():
            copy = os.path.join(self.base, "copies", *ref.split("/"))
            template2.materialize(package, copy)
            archived = {n[len(f"06-failure/{ref}/"):]: d for n, d in files.items() if n.startswith(f"06-failure/{ref}/")}
            self.assertEqual(archived, check.tree_bytes(copy), ref)
        page = {n[len("01-01-first/"):]: d for n, (m, d) in self.members("01-01-first.tar.gz").items() if m.isfile()}
        copy = os.path.join(self.base, "copies", "01-first")
        check.copy_package(os.path.join(self.root, "01-hello", "01-first"), copy)
        self.assertEqual({n: d for n, d in page.items() if n != "README.md"}, check.tree_bytes(copy))

    def test_the_check_ties_the_archive_to_the_checked_package(self):
        saved = template2.materialize

        def more(package, to):
            saved(package, to)
            write(os.path.join(to, "src", "extra.una"), "-- not archived\n")

        template2.materialize = more
        try:
            code, report = self.checked()
        finally:
            template2.materialize = saved
        self.assertIn("is not the package the check runs: ['src/extra.una'] differ", report)

    def test_a_symlinked_src_directory(self):
        src = os.path.join(self.chapter, "steps", "01-quantity", "src")
        moved = os.path.join(self.base, "elsewhere")
        shutil.move(src, moved)
        os.symlink(moved, src)
        self.assertEqual(check.package_files(os.path.dirname(src)), ["una.toml", "verification.lock"])
        with self.assertRaises(self.archive.LinkError) as raised:
            self.archive.build(self.root, os.path.join(self.base, "out-2"), 0)
        self.assertIn("06-failure/steps/01-quantity/src is a symbolic link", str(raised.exception))

    def test_a_symlinked_file_and_page_src(self):
        os.symlink(os.path.join(self.root, "una.lock"), os.path.join(self.chapter, "day-to-day", "src", "hosts.una"))
        with self.assertRaises(self.archive.LinkError):
            self.archive.build(self.root, os.path.join(self.base, "out-2"), 0)
        os.remove(os.path.join(self.chapter, "day-to-day", "src", "hosts.una"))
        src = os.path.join(self.root, "01-hello", "01-first", "src")
        shutil.move(src, os.path.join(self.base, "page-src"))
        os.symlink(os.path.join(self.base, "page-src"), src)
        with self.assertRaises(self.archive.LinkError) as raised:
            self.archive.build(self.root, os.path.join(self.base, "out-3"), 0)
        self.assertIn("01-hello/01-first/src is a symbolic link", str(raised.exception))
        with self.assertRaises(self.archive.LinkError):
            self.archive.plain_source(self.root, os.path.join(src, "main.una"))

    def test_two_builds_are_the_same_bytes(self):
        again = os.path.join(self.base, "again")
        self.archive.build(self.root, again, 0)
        for name in sorted(os.listdir(self.out)):
            self.assertEqual(check.read_bytes(os.path.join(self.out, name)), check.read_bytes(os.path.join(again, name)), name)

    def test_a_missing_chapter_archive(self):
        os.remove(os.path.join(self.out, "06-failure.tar.gz"))
        code, report = self.checked()
        self.assertIn("archive 06-failure.tar.gz: missing", report)

    def test_a_chapter_archive_with_another_file(self):
        write(os.path.join(self.chapter, "steps", "01-quantity", "src", "quantity.una"), "--- changed\n" + STEP.format(name="quantity", extra="3"))
        code, report = self.checked()
        self.assertIn("archive 06-failure.tar.gz: holds", report)

    def test_a_whole_archive_without_the_chapter(self):
        import tarfile

        path = os.path.join(self.out, "una-by-example-9.9.9.tar.gz")
        kept = {n: d for n, (m, d) in self.members("una-by-example-9.9.9.tar.gz").items() if m.isfile() and "/06-failure/steps/" not in n}
        files = []
        for name, data in kept.items():
            source = os.path.join(self.base, "kept", name)
            write(source, "")
            with open(source, "wb") as handle:
                handle.write(data)
            files.append((source, name.split("/", 1)[1]))
        self.archive.tar_gz(path, "una-by-example-9.9.9", files, 0)
        code, report = self.checked()
        self.assertIn("does not hold exactly the repository's pages and chapters: missing ['una-by-example-9.9.9/06-failure/steps/01-quantity/src/quantity.una'", report)


class TemplateOne(Base):
    """A chapter on template 1: no front matter, no code, pages, no template 2 directories."""

    def setUp(self):
        super().setUp()
        check.fixture(self.root)
        self.readme = os.path.join(self.root, "01-hello", "README.md")

    def test_a_template_1_chapter(self):
        self.assertPasses()

    def test_code_on_a_template_1_chapter_page(self):
        write(self.readme, "# 1 Hello\n\n```una\nnonsense\n```\n")
        self.assertFails("a template 1 chapter page holds no code block")
        write(self.readme, "# 1 Hello\n\nText.\n\n    nonsense\n")
        self.assertFails("a template 1 chapter page holds no code")

    def test_front_matter_on_a_template_1_chapter_page(self):
        write(self.readme, "---\nlearn: \"1\"\n---\n\n# 1 Hello\n")
        self.assertFails("a template 1 chapter page has no front matter")

    def test_a_chapter_without_pages(self):
        shutil.rmtree(os.path.join(self.root, "01-hello", "01-first"))
        self.assertFails("a chapter with no page directories is on template 2")

    def test_hidden_code_on_a_template_1_chapter_page(self):
        for extra in ("$$\nnonsense\n$$\n", "-     pub main() -> Unit = nonsense\n", "Text\u00a0here.\n"):
            write(self.readme, "# 1 Hello\n\n" + extra)
            self.assertFails("a template 1 chapter page holds no code")

    def test_a_tracked_symbolic_link(self):
        os.makedirs(os.path.join(self.root, "translations", "pt-br"))
        os.symlink(os.path.join(self.root, "una.lock"), os.path.join(self.root, "translations", "pt-br", "x.md"))
        check.git(self.root, "init", "-q")
        check.git(self.root, "add", "-A")
        check.git(self.root, "commit", "-q", "-m", "c")
        failures = check.Failures()
        check.tracked_links(self.root, failures)
        self.assertIn("translations/pt-br/x.md: a symbolic link; una-by-example holds none", failures.items)

    def test_hidden_code_on_a_template_1_page(self):
        page = os.path.join(self.root, "01-hello", "01-first", "README.md")
        english = check.read(page)
        for extra in ("$$\nnonsense\n$$\n", "-     pub main() -> Unit = nonsense\n", "Text.\n\n    nonsense\n", "Text\u00a0here.\n"):
            write(page, english.replace("A lead.", "A lead.\n\n" + extra))
            failures = check.Failures()
            scratch = tempfile.mkdtemp(dir=self.base)
            check.check_pages(self.root, self.una, failures, scratch)
            self.assertTrue(any("01-hello/01-first/README.md:1" in i for i in failures.items), (extra, failures.items))
        write(page, english.replace("A lead.", "A lead.\n$$\nnonsense\n$$"))
        failures = check.Failures()
        check.check_pages(self.root, self.una, failures, tempfile.mkdtemp(dir=self.base))
        line = english.split("\n").index("A lead.") + 2
        self.assertIn(f"01-hello/01-first/README.md:{line}: a `$$` line, which the site renders as a block of code; Learn pages have none", failures.items)

    def test_hidden_code_in_template_1_translations(self):
        english = check.read(os.path.join(self.root, "01-hello", "01-first", "README.md"))
        chapter = check.read(self.readme)
        cases = [(("01-hello",), chapter, "# 1 Hello\n"), (("01-hello", "01-first"), english, "A lead.\n")]
        for path, source, anchor in cases:
            digest = hashlib.sha256(source.encode()).hexdigest()
            if source.startswith("---"):
                base = source.replace('editions: ["0.2"]', f'editions: ["0.2"]\nsource: {digest}\nstatus: approved')
            else:
                base = f"---\nsource: {digest}\nstatus: approved\n---\n\n" + source
            target = os.path.join(self.root, "translations", "pt-br", *path, "README.md")
            write(target, base)
            failures = check.Failures()
            check.check_translations(self.root, failures)
            self.assertEqual([i for i in failures.items if "README.md:" in i], [], path)
            for extra, wants in (("$$\nnonsense\n$$\n", "a `$$` line"), ("-     pub main() -> Unit = nonsense\n", "columns after a list"),
                                 ("Text.\n\n    nonsense\n", "indented by 4"), ("Texto\u00a0aqui.\n", "U+00A0")):
                write(target, base.replace(anchor, anchor + "\n" + extra, 1))
                failures = check.Failures()
                check.check_translations(self.root, failures)
                self.assertTrue(any(wants in i for i in failures.items), (path, extra, failures.items))
            write(target, base)
        write(os.path.join(self.root, "translations", "pt-br", "01-hello", "README.md"),
              cases[0][1].replace("# 1 Hello\n", f"---\nsource: x\nstatus: draft\n---\n\n# 1 Hello\n\n~~~una\nnonsense\n~~~\n"))
        failures = check.Failures()
        check.check_translations(self.root, failures)
        self.assertTrue(any("a template 1 chapter page holds no code block" in i for i in failures.items), failures.items)


class Translations(Base):
    def setUp(self):
        super().setUp()
        chapter(self.root)
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

    def assertTranslationFails(self, text, wants):
        items = self.failures(text)
        self.assertTrue(any(wants in i for i in items), f"no failure with {wants!r} in:\n" + "\n".join(items))

    def test_a_translation(self):
        self.assertEqual(self.failures(self.text), [])

    def test_a_translated_caption(self):
        self.assertEqual(self.failures(self.text.replace('caption="the kinds"', 'caption="os tipos"')), [])

    def test_a_changed_include(self):
        self.assertTranslationFails(self.text.replace("#reason..describe", "#reason"), "its blocks are not the English page's")

    def test_a_tilde_fence(self):
        self.assertTranslationFails(self.text.replace("Você vai aprender a:", "~~~una\npub main() -> Unit = nonsense\n~~~\n\nVocê vai aprender a:"),
                                    "not an include")

    def test_a_fence_in_a_quote(self):
        self.assertTranslationFails(self.text.replace("> A key idea.", "> A key idea.\n> ```una\n> nonsense\n> ```"), "inside a quote")

    def test_indented_code(self):
        self.assertTranslationFails(self.text.replace("Você vai aprender a:", "Texto.\n\n    nonsense()\n\nVocê vai aprender a:"), "indented by 4")

    def test_a_math_block(self):
        self.assertTranslationFails(self.text.replace("Você vai aprender a:", "$$\nnonsense\n$$\n\nVocê vai aprender a:"), "a `$$` line")

    def test_a_marker_and_five_columns(self):
        self.assertTranslationFails(self.text.replace("- declare an error kind.", "-     pub main() -> Unit = nonsense"),
                                    "columns after a list or quote marker")

    def test_swapped_blocks(self):
        first = self.text.index('```una include="day-to-day/src/orders.una#Order"')
        first_end = self.text.index("```\n", self.text.index("\n", first)) + 4
        second = self.text.index('```una include="day-to-day/src/orders.una#reason..describe"')
        second_end = self.text.index("```\n", self.text.index("\n", second)) + 4
        a, b = self.text[first:first_end], self.text[second:second_end]
        swapped = self.text[:first] + b + self.text[first_end:second] + a + self.text[second_end:]
        self.assertTranslationFails(swapped, "in the same order")

    def test_a_changed_number(self):
        self.assertTranslationFails(self.text.replace("## 6.2 Handling a failure", "## 6.20 Tratando uma falha"), "numbered as the English page's")

    def test_a_translated_nav(self):
        english = os.path.join(self.root, "06-failure", "README.md")
        edit(english, "template: 2\n", f"template: 2\nnav: {Chapters.NAV}\n")
        text = check.read(english)
        digest = hashlib.sha256(text.encode()).hexdigest()
        translated = text.replace("title: Failure", "title: Falhas").replace("# 6 Failure", "# 6 Falhas").replace(
            "template: 2", f"template: 2\nsource: {digest}\nstatus: approved").replace('"Exercises"', '"Exercícios"')
        self.assertEqual(self.failures(translated), [])
        self.assertTranslationFails(translated.replace(', "Recap and reference"', ""), "`nav` has 7 labels")
        self.assertTranslationFails(translated.replace('"Exercícios"', '"`Exercícios`"'), "a label is plain text")
        self.assertTranslationFails(translated.replace(f"nav: {Chapters.NAV.replace('Exercises', 'Exercícios')}\n", ""),
                                    "`nav` is translated when the English page has one")

    def test_a_nav_the_english_page_has_not(self):
        self.assertTranslationFails(self.text.replace("template: 2\n", f"template: 2\nnav: {Chapters.NAV}\n"),
                                    "absent when it has none")

    def test_a_changed_time(self):
        self.assertTranslationFails(self.text.replace("time: 35", "time: 40"), "`time` is '40'")

    def test_fill_fills_translations(self):
        write(self.path, self.text.replace("  quantity: Int\n```", "```"))
        changed, problems = template2.fill(self.root)
        self.assertEqual((changed, problems), (["translations/pt-br/06-failure/README.md"], []))
        self.assertEqual(self.failures(check.read(self.path)), [])

    def test_fill_does_not_write_through_a_link(self):
        outside = os.path.join(self.base, "outside.md")
        write(outside, self.text.replace("  quantity: Int\n```", "```"))
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        os.symlink(outside, self.path)
        changed, problems = template2.fill(self.root)
        self.assertEqual(changed, [])
        self.assertTrue(any("never written through" in p for p in problems), problems)
        self.assertNotIn("  quantity: Int\n```", check.read(outside))


def main():
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=1, stream=sys.stderr).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
