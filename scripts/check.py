#!/usr/bin/env python3
"""Checks every example of Una by Example against a `una` binary.

A chapter whose README.md has `template: 2` in its front matter is one page, checked by the
rules of template 2 (scripts/template2.py, TEMPLATE.md): its parts in order, the subsections
inside its sections (template2.structure), its packages under
steps/, day-to-day/, mistakes/ and exercises/ checked as in step 2 below, with their rendered
diagnostics, every fenced block an include whose text is the included file's, the exercises'
examples failing on start/ and passing on the answer, and links to the site's own pages. A
chapter is on template 1 only when its README.md has no front matter and no code, and it has
page directories and no template 2 directory; anything else that is not exactly template 2
fails. For each page directory `NN-chapter/MM-page/` of a template 1 chapter:

1. Its README.md has the front matter (`learn`, `title`, `editions`, `codes`) and the parts of
   the template in order, no hidden code (template2.hidden_code: a `$$` line, indented code, a
   fence in a quote or a list, invisible or control characters), its `learn` number matches its path, and its `codes` are the codes its
   outcomes show.
2. A fresh copy of the package (`una.toml`, `verification.lock`, `src/`) has the outcome in
   `expected/`: either it checks clean at tier 1 in canonical form and `una run` prints
   `expected/output.txt` byte for byte, or `una check` reports exactly the lines of
   `expected/diagnostics.txt`, each `error <code> at <file>:<line>:<col>: <message>`, followed
   by `  counterexample: <name> = <value>, ...` when the diagnostic has one.
   Each `expected/commands/*.txt` is a further command, `$ una <args>` on its first line, and
   what it prints on stdout in the package, byte for byte.
3. Each `try/N` holds files that replace the package's, and its own `expected/`, checked in the
   same way on a fresh copy. The page's "Try it" list has one item per `try/N`.

4. Each translation `translations/<locale>/NN-chapter[/MM-page]/README.md`, for a locale of
   LOCALES, translates an English README of the same path. Its front matter keeps the English
   page's `learn`, `editions` and `codes`, gives the translated `title`, and adds `source`, the
   SHA-256 of the English README it translates, and `status`, `draft` or `approved`. It has the
   English README's headings, the same number of them, with as many numbered items under each;
   its code (inline spans and fenced blocks, comments included) and its links (link targets,
   reference definitions and every URL, autolinks and bare ones included) are the English
   README's, the same multiset; and so are its HTML tags outside code. An `approved` translation whose `source` is not the
   English README's digest fails: it was approved for a text that has changed. A `draft` one
   is reported as out of date, and the website shows the English page for both.

With UNA_NEUTRALITY_PATTERN set in the environment, an extended regular expression (grep -E),
no tracked text file, English or translated, may match it; the pattern is never stored or
printed. The una release gate runs its own check, with the same dialect. With `--require-neutrality`, as the una
release gate runs it, an unset or empty pattern is a failure; without it, the check is skipped
and the report says so.

`una` always runs with a minimal environment (`una_env`: PATH, a HOME and TMPDIR of its own, a
fixed locale, no colors, nothing else), on a package whose una.toml stays within MANIFEST_TABLES
and GRANT, with the commands of COMMAND only. No symbolic link in a page or package is copied
or followed; each is a failure, and so is a tracked one anywhere. una.toml is read with tomllib,
or on a Python before 3.11 with the stricter `plain_toml`.

Then every commit's author and committer must be GitHub noreply addresses, and with
`--archives DIR`, every archive of `scripts/archive.py` must unpack to its page's or chapter's
files, each package byte for byte the copy the check runs, and pass step 2 as unpacked.

Usage:
  check.py --una PATH [--una-version-from-binary] [--archives DIR] [--require-neutrality]
  check.py --fill
  check.py --self-test

`--fill` rewrites the body of every include block of the template 2 pages, English and
translated, from the packages, and needs no `una`.

`una.lock` names the release the examples are checked against; `--una-version-from-binary`
checks against the given binary's version instead, as the una release gate does for a release
candidate. Standard library only. Exit code 0 on PASS, 1 on any failure, 2 on a usage error.
"""

import sys

# The scripts import each other; nothing they run writes bytecode into the repository.
sys.dont_write_bytecode = True

import json  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tarfile  # noqa: E402
import tempfile  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CHAPTER = re.compile(r"^(\d\d)-[a-z0-9]+(?:-[a-z0-9]+)*$")
PAGE = CHAPTER
PACKAGE_FILES = ("README.md", "una.toml", "verification.lock")
PARTS = ["## The program", "## What you should see", "## Try it", "## See also"]
OPTIONAL_PARTS = ["## Notes"]
DIAGNOSTIC = re.compile(r"^error (U\d{4}) at ([^:]+):(\d+):(\d+): (.+)$")
COUNTEREXAMPLE = re.compile(r"^  counterexample: .+$")
LOCALES = ("pt-br", "es")
STATUSES = ("draft", "approved")
FENCE = re.compile(r"^```[^\n]*\n.*?^```$", re.MULTILINE | re.DOTALL)
SPAN = re.compile(r"`[^`\n]+`")
LINK = re.compile(r"\]\(([^)\s]+)\)")
URL = re.compile(r"https?://[^\s)>\]]+")
REFERENCE = re.compile(r"^ {0,3}\[[^\]]+\]:\s*(\S+)", re.MULTILINE)
TAG = re.compile(r"<[A-Za-z/][^>\n]*>?")
CAPTION = re.compile(r'\scaption=("[^"]*"|\S+)')
NOREPLY = re.compile(r"^(\d+\+)?[A-Za-z0-9-]+@users\.noreply\.github\.com$")


class Failures:
    """The failures found, each with where it is."""

    def __init__(self):
        self.items = []

    def add(self, where, what):
        self.items.append(f"{where}: {what}")


def chapters(root):
    """The chapter directories, in order."""
    return sorted(
        name
        for name in os.listdir(root)
        if CHAPTER.match(name) and os.path.isdir(os.path.join(root, name))
    )


def pages(root):
    """The page directories, as (chapter, page), in order."""
    out = []
    for chapter in chapters(root):
        for page in sorted(os.listdir(os.path.join(root, chapter))):
            if PAGE.match(page) and os.path.isdir(os.path.join(root, chapter, page)):
                out.append((chapter, page))
    return out


# A list whose first item is quoted holds quoted items only, each without a quote, and they may
# hold commas: `["checked, and the escape budget", "Maps"]`. The site reads lists the same way.
QUOTED_LIST = re.compile(r'^"[^"]*"(?:\s*,\s*"[^"]*")*$')


def front_matter(text):
    """The front matter of `text` as a dict of strings and lists, and the rest of the text.
    A list is `[a, b]`, or, when its first item is quoted, quoted items only (QUOTED_LIST);
    a quoted list that is not that does not parse."""
    if not text.startswith("---\n"):
        return None, text
    end = text.find("\n---\n", 4)
    if end < 0:
        return None, text
    fields = {}
    for line in text[4:end].splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            return None, text
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if inner.startswith('"'):
                if not QUOTED_LIST.match(inner):
                    return None, text
                items = re.findall(r'"([^"]*)"', inner)
            else:
                items = [v.strip().strip('"') for v in inner.split(",") if v.strip()]
            fields[key.strip()] = items
        else:
            fields[key.strip()] = value.strip('"')
    return fields, text[end + 5 :]


def package_files(directory):
    """The files of the package in `directory`, relative to it, in order: the README, the
    manifest, the lock and every file under `src/`. A symbolic link is never followed: a
    linked `src/` or directory under it is not entered (`symlinks` reports it)."""
    out = [name for name in PACKAGE_FILES if os.path.isfile(os.path.join(directory, name))]
    src = os.path.join(directory, "src")
    if os.path.islink(src):
        return out
    for base, dirs, files in os.walk(src):
        dirs.sort()
        for name in sorted(files):
            out.append(os.path.relpath(os.path.join(base, name), directory))
    return out


def copy_package(directory, to, overlay=None):
    """Copies the package in `directory` to `to`, then the files of `overlay` over it. A
    symbolic link is never copied or followed; `symlinks` reports it as a failure."""
    for name in package_files(directory):
        if name == "README.md" or os.path.islink(os.path.join(directory, name)):
            continue
        os.makedirs(os.path.dirname(os.path.join(to, name)) or to, exist_ok=True)
        shutil.copyfile(os.path.join(directory, name), os.path.join(to, name), follow_symlinks=False)
    if overlay:
        for base, dirs, files in os.walk(overlay):
            dirs[:] = sorted(d for d in dirs if not (base == overlay and d == "expected"))
            for name in sorted(files):
                source = os.path.join(base, name)
                if os.path.islink(source):
                    continue
                target = os.path.join(to, os.path.relpath(source, overlay))
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copyfile(source, target, follow_symlinks=False)


def symlinks(directory, where, failures):
    """Every symbolic link under `directory`, file or directory, is a failure: una-by-example
    holds none, and the website refuses them too."""
    if os.path.islink(directory):
        failures.add(where, "a symbolic link; una-by-example holds none")
        return
    for base, dirs, files in os.walk(directory):
        dirs.sort()
        for name in sorted(dirs + files):
            if os.path.islink(os.path.join(base, name)):
                relative = os.path.relpath(os.path.join(base, name), directory).replace(os.sep, "/")
                failures.add(f"{where}/{relative}", "a symbolic link; una-by-example holds none")


# The home directory `una` runs with: a directory of its own, never the user's.
HOME = None


def una_home():
    global HOME
    if HOME is None:
        import atexit

        HOME = tempfile.mkdtemp(prefix="una-by-example-home-")
        atexit.register(shutil.rmtree, HOME, True)
    return HOME


def una_env():
    """The environment of one `una` run: PATH (to find Z3 and a C toolchain), a fresh HOME and
    TMPDIR of its own, which no other run sees, a fixed locale and no colors. Nothing else of
    the caller's environment reaches it, UNA_NEUTRALITY_PATTERN and every other variable
    included."""
    home = tempfile.mkdtemp(prefix="home-", dir=una_home())
    return {"PATH": os.environ.get("PATH", os.defpath), "HOME": home, "TMPDIR": home,
            "LANG": "C.UTF-8", "NO_COLOR": "1"}


def run(una, args, cwd):
    """Runs `una` with `args` in `cwd`, in the environment of `una_env`."""
    return subprocess.run(
        [una, *args], cwd=cwd, capture_output=True, stdin=subprocess.DEVNULL, env=una_env(), check=False
    )


# What a package's una.toml may hold: these tables, and in [run] only `entry` and `grants`,
# with these grants. No env, no network, no files outside the package's src/.
MANIFEST_TABLES = {"package", "run", "escape_budget", "labels", "trusted", "boundaries", "contracts"}
PACKAGE_KEYS = {"name", "version", "edition"}
GRANT = re.compile(r"^(console|clock|files:src(/[A-Za-z0-9_-]+)*:(read|write|read,write))$")
# The commands an `expected/commands/*.txt` may run, all in the package and nowhere else.
COMMAND = re.compile(
    r"^(--json )?(check|test|run|build|report|obligations) \.$|^fmt --check \.$|^fix --dry-run \.$"
    r"|^(--json )?explain U\d{4}$|^(--json )?(trace|contract) [A-Za-z0-9_.]+$"
)


TOML_KEY = re.compile(r'[A-Za-z0-9_-]+|"[^"\\\n]*"')
TOML_STRING = re.compile(r'"([^"\\\n]*)"')


def plain_toml(text):
    """A strict reading of the TOML a una-by-example manifest uses, for a Python without
    tomllib (before 3.11): `[table]` headers, and `key = value` lines whose value is a string
    without escapes, an integer, true or false, or a one-line array of such strings; comments
    and blank lines. Only spaces and tabs separate tokens; a control character other than the
    tab (a carriage return and DEL included) anywhere, and a character outside ASCII anywhere
    but inside a string or a comment, raise ValueError, and so does anything else outside
    that subset, so the manifest fails: the reading is never looser than tomllib's."""
    bad = re.search(r"[\x00-\x08\x0a-\x1f\x7f]", text.replace("\n", " "))
    if bad:
        raise ValueError(f"the control character U+{ord(bad.group(0)):04X}")
    document, table = {}, None
    for number, raw in enumerate(text.split("\n"), start=1):
        line = raw.strip(" \t")
        code = re.sub(r'"[^"\\\n]*"', '""', line).split("#", 1)[0]
        if not code.isascii():
            raise ValueError(f"line {number}: a character outside ASCII outside a string or a comment")
        if not line or line.startswith("#"):
            continue
        header = re.fullmatch(r"\[([A-Za-z0-9_-]+)\]", line)
        if header:
            if header.group(1) in document:
                raise ValueError(f"line {number}: [{header.group(1)}] twice")
            table = document[header.group(1)] = {}
            continue
        key = TOML_KEY.match(line)
        if not key or table is None:
            raise ValueError(f"line {number}: not a key in a table")
        rest = line[key.end():].lstrip(" \t")
        if not rest.startswith("="):
            raise ValueError(f"line {number}: no `=` after the key")
        rest = rest[1:].strip(" \t")
        name = key.group(0)[1:-1] if key.group(0).startswith('"') else key.group(0)
        if rest.startswith("["):
            items, rest = [], rest[1:].strip(" \t")
            while not rest.startswith("]"):
                found = TOML_STRING.match(rest)
                if not found:
                    raise ValueError(f"line {number}: an array holds strings only")
                items.append(found.group(1))
                rest = rest[found.end():].strip(" \t")
                if rest.startswith(","):
                    rest = rest[1:].strip(" \t")
                elif not rest.startswith("]"):
                    raise ValueError(f"line {number}: an array's items are separated by commas")
            value, rest = items, rest[1:].strip(" \t")
        elif TOML_STRING.match(rest):
            found = TOML_STRING.match(rest)
            value, rest = found.group(1), rest[found.end():].strip(" \t")
        else:
            found = re.match(r"(-?(?:0|[1-9][0-9]*)|true|false)\b", rest)
            if not found:
                raise ValueError(f"line {number}: a value is a string, a whole number, true, false or an array of strings")
            value = int(found.group(1)) if found.group(1) not in ("true", "false") else found.group(1) == "true"
            rest = rest[found.end():].strip(" \t")
        if rest and not rest.startswith("#"):
            raise ValueError(f"line {number}: text after the value")
        if name in table:
            raise ValueError(f"line {number}: `{name}` twice")
        table[name] = value
    return document


def manifest(package, where, failures):
    """Whether the una.toml of the copy at `package` is within MANIFEST_TABLES and GRANT. It is
    read with tomllib, or where Python has none, with the stricter `plain_toml`."""
    path = os.path.join(package, "una.toml")
    try:
        with open(path, "rb") as handle:
            data = handle.read()
        try:
            import tomllib

            document = tomllib.loads(data.decode("utf-8"))
        except ImportError:
            document = plain_toml(data.decode("utf-8"))
    except (OSError, ValueError) as error:
        failures.add(where, f"una.toml cannot be read: {error}")
        return False
    good = True
    for table, value in document.items():
        if table not in MANIFEST_TABLES:
            failures.add(where, f"una.toml: no [{table}] in una-by-example; the tables are {sorted(MANIFEST_TABLES)}")
            good = False
        elif not isinstance(value, dict):
            failures.add(where, f"una.toml: `{table}` is a table, [{table}]")
            good = False
    if not good:
        return False
    for key in document.get("package", {}):
        if key not in PACKAGE_KEYS:
            failures.add(where, f"una.toml: [package] holds only {sorted(PACKAGE_KEYS)}, not `{key}`")
            good = False
    section = document.get("run", {})
    for key in section:
        if key not in ("entry", "grants"):
            failures.add(where, f"una.toml: [run] holds only `entry` and `grants`, not `{key}`")
            good = False
    grants = section.get("grants", [])
    if not isinstance(grants, list):
        failures.add(where, "una.toml: [run] grants is a list of strings")
        return False
    for grant in grants:
        if not isinstance(grant, str) or not GRANT.fullmatch(grant) or ".." in grant:
            failures.add(where, f"una.toml: the grant {grant!r} is not allowed; grants are console, clock and files:src[/dir]:read|write|read,write")
            good = False
    return good


def diagnostics_of(una, package):
    """The lines `una check` reports for `package`, in the form of `expected/diagnostics.txt`."""
    result = run(una, ["--json", "check", "."], package)
    try:
        document = json.loads(result.stdout)
    except ValueError:
        return None, result
    lines = []
    for d in document.get("diagnostics", []):
        start = d["primary"]["start"]
        file = d["primary"]["file"]
        lines.append(f"{d['severity']} {d['code']} at {file}:{start['line']}:{start['col']}: {d['message']}")
        bindings = (d.get("counterexample") or {}).get("bindings") or []
        if bindings:
            shown = ", ".join(f"{b['name']} = {json.dumps(b['value'])}" for b in bindings)
            lines.append(f"  counterexample: {shown}")
    return lines, result


def read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


# `una report` names the host target on its `native:` line (spec/13 §6, spec/16 §1). For the two
# targets una builds for, that line is compared without its value, so the report of a package
# checks on either host; any other value on the line is compared as it is, and fails.
NATIVE = re.compile(r"^native: (aarch64-apple-darwin|x86_64-unknown-linux-gnu)$", re.MULTILINE)


def host_neutral(args, text):
    """`text`, the output of `una <args>`, with the target of a `report` command's `native:` line
    replaced by a fixed token when it is one of the supported targets."""
    if args.split(" ") != ["report", "."]:
        return text
    return NATIVE.sub("native: <supported target>", text)


def has_commands(expected):
    """Whether `expected/commands/` holds a command file."""
    directory = os.path.join(expected, "commands")
    return os.path.isdir(directory) and any(name.endswith(".txt") for name in os.listdir(directory))


def outcome(una, package, expected, where, failures):
    """Checks the package at `package` against the outcome in `expected`; returns its codes. An
    empty diagnostics.txt states that the package checks clean and is not run, which only a
    command file that shows what running it does may stand in for."""
    output = os.path.join(expected, "output.txt")
    listed = os.path.join(expected, "diagnostics.txt")
    if os.path.isfile(output) == os.path.isfile(listed):
        failures.add(where, "expected/ must hold exactly one of output.txt and diagnostics.txt")
        return set()
    if not manifest(package, where, failures):
        return set()
    lines, result = diagnostics_of(una, package)
    if lines is None:
        failures.add(where, f"`una check` printed no JSON: {result.stderr.decode(errors='replace')[:200]}")
        return set()
    if os.path.isfile(listed):
        wanted = [line for line in read(listed).splitlines() if line]
        if not wanted and not has_commands(expected):
            failures.add(where, "an empty diagnostics.txt says the package checks clean and is not run; it needs a command in expected/commands/ that shows what running it does, or an output.txt")
        for line in wanted:
            if not DIAGNOSTIC.match(line) and not COUNTEREXAMPLE.match(line):
                failures.add(where, f"diagnostics.txt: not `error <code> at <file>:<line>:<col>: <message>`: {line}")
        if lines != wanted:
            failures.add(where, "`una check` reports:\n  " + "\n  ".join(lines or ["(nothing)"]))
        return {DIAGNOSTIC.match(line).group(1) for line in wanted if DIAGNOSTIC.match(line)}
    if lines:
        failures.add(where, "expected to check clean, but `una check` reports:\n  " + "\n  ".join(lines))
        return set()
    canonical = run(una, ["fmt", "--check", "."], package)
    if canonical.returncode != 0:
        failures.add(where, "not in canonical form (`una fmt --check`)")
    ran = run(una, ["run", "."], package)
    if ran.returncode != 0:
        failures.add(where, f"`una run` exited with {ran.returncode}: {ran.stderr.decode(errors='replace')[:200]}")
    with open(output, "rb") as handle:
        printed = handle.read()
    if ran.stdout != printed:
        failures.add(where, f"`una run` prints {ran.stdout!r}, not output.txt")
    return set()


def commands(una, package, expected, where, failures, fresh=None):
    """Each `expected/commands/*.txt`: its first line is `$ una <args>`, with args one of
    COMMAND, and the rest is what that command prints on stdout in the package, byte for byte.
    With `fresh`, each command runs in the copy `fresh()` makes, not in `package`."""
    directory = os.path.join(expected, "commands")
    if not os.path.isdir(directory):
        return 0
    count = 0
    for name in sorted(os.listdir(directory)):
        text = read(os.path.join(directory, name))
        first, _, printed = text.partition("\n")
        if not first.startswith("$ una "):
            failures.add(f"{where}/commands/{name}", "the first line must be `$ una <args>`")
            continue
        if not COMMAND.fullmatch(first[len("$ una "):]):
            failures.add(f"{where}/commands/{name}", f"`{first[2:]}` is not one of the commands una-by-example runs")
            continue
        cwd = fresh() if fresh else package
        if not manifest(cwd, where, Failures()):
            failures.add(f"{where}/commands/{name}", "not run: the package's una.toml is not allowed")
            continue
        args = first[len("$ una "):]
        ran = run(una, args.split(" "), cwd)
        if host_neutral(args, ran.stdout.decode(errors="replace")) != host_neutral(args, printed):
            failures.add(f"{where}/commands/{name}", f"`{first[2:]}` prints:\n{ran.stdout.decode(errors='replace')}")
        count += 1
    return count


def template(root, chapter, page, readme, tries, codes, failures):
    """Checks the page's README against the template."""
    where = f"{chapter}/{page}/README.md"
    fields, body = front_matter(readme)
    if fields is None:
        failures.add(where, "no front matter")
        return
    for key in ("learn", "title", "editions", "codes"):
        if key not in fields:
            failures.add(where, f"the front matter has no `{key}`")
    number = f"{int(chapter[:2])}.{int(page[:2])}"
    if fields.get("learn") != number:
        failures.add(where, f"`learn` is {fields.get('learn')!r}, but its path says {number!r}")
    first = body.lstrip("\n").split("\n", 1)[0]
    if first != f"# {number} {fields.get('title', '')}":
        failures.add(where, f"the title line must be `# {number} {fields.get('title', '')}`")
    headings = [line for line in body.splitlines() if line.startswith("## ")]
    required = [h for h in headings if h not in OPTIONAL_PARTS]
    if required != PARTS:
        failures.add(where, f"the parts must be {PARTS}, in order, with `## Notes` optional; found {headings}")
    if "## Notes" in headings and headings.index("## Notes") != 2:
        failures.add(where, "`## Notes` goes after `## What you should see`")
    if "## Try it" in body:
        part = body.split("## Try it", 1)[1].split("\n## ", 1)[0]
        items = [line for line in part.splitlines() if re.match(r"^\d+\. ", line)]
        if len(items) != tries:
            failures.add(where, f"`## Try it` lists {len(items)} changes, but there are {tries} `try/N`")
    if sorted(fields.get("codes", [])) != sorted(codes):
        failures.add(where, f"`codes` is {fields.get('codes')}, but the outcomes show {sorted(codes)}")


def check_pages(root, una, failures, scratch):
    """Steps 1 to 3 for every page; returns the number of pages and of changes."""
    counted = [0, 0, 0]
    for chapter, page in pages(root):
        directory = os.path.join(root, chapter, page)
        where = f"{chapter}/{page}"
        counted[0] += 1
        symlinks(directory, where, failures)
        package = os.path.join(scratch, chapter, page, "package")
        copy_package(directory, package)
        codes = outcome(una, package, os.path.join(directory, "expected"), where, failures)
        counted[2] += commands(una, package, os.path.join(directory, "expected"), where, failures)
        try_root = os.path.join(directory, "try")
        tries = sorted(os.listdir(try_root), key=lambda n: (len(n), n)) if os.path.isdir(try_root) else []
        for index, name in enumerate(tries, start=1):
            if name != str(index):
                failures.add(where, f"try/ must hold 1, 2, ...; found {tries}")
                break
            changed = os.path.join(scratch, chapter, page, f"try-{name}")
            copy_package(directory, changed, os.path.join(try_root, name))
            codes |= outcome(una, changed, os.path.join(try_root, name, "expected"), f"{where}/try/{name}", failures)
            counted[2] += commands(una, changed, os.path.join(try_root, name, "expected"), f"{where}/try/{name}", failures)
            counted[1] += 1
        readme = os.path.join(directory, "README.md")
        if not os.path.isfile(readme):
            failures.add(where, "no README.md")
            continue
        template(root, chapter, page, read(readme), len(tries), codes, failures)
        import template2

        # The site renders these as code that no package backs: a `$$` line, indented code, a
        # fence inside a quote or a list, and invisible or control characters.
        for line, why in template2.hidden_code(template2.padded(read(readme))[1]):
            failures.add(f"{where}/README.md:{line}", why)
    for chapter in chapters(root):
        if not os.path.isfile(os.path.join(root, chapter, "README.md")):
            failures.add(chapter, "no README.md (the chapter page)")
    return counted


def skeleton(body):
    """What a translation keeps of a README's `body`: its headings, each with the number of
    numbered items under it; its code and link targets, as a sorted list (fenced blocks whole,
    then outside them: code spans, link targets, reference definitions and every URL); and its
    HTML tags outside code, as a sorted list."""
    parts = []
    for line in body.splitlines():
        if line.startswith("#"):
            parts.append([line.split(" ", 1)[0], 0])
        elif re.match(r"^\d+\. ", line) and parts:
            parts[-1][1] += 1
    # A fence's caption= is prose, which a translation translates; the rest of the fence is kept.
    fences = []
    for fence in FENCE.findall(body):
        opener, newline, rest = fence.partition("\n")
        fences.append(CAPTION.sub(" caption=", opener, count=1) + newline + rest)
    rest = FENCE.sub("", body)
    spans = SPAN.findall(rest)
    kept = sorted(fences + spans + LINK.findall(rest) + REFERENCE.findall(rest) + URL.findall(rest))
    tags = sorted(TAG.findall(SPAN.sub("", rest)))
    return [tuple(p) for p in parts], kept, tags


def check_translations(root, failures):
    """Step 4: every translation against its English README. Returns the number of
    translations, of approved ones, and the drafts whose English README has changed."""
    import hashlib

    counted = [0, 0]
    stale = []
    base = os.path.join(root, "translations")
    if not os.path.isdir(base):
        return counted, stale
    for directory, dirs, files in os.walk(base):
        dirs.sort()
        relative = os.path.relpath(directory, base)
        parts = [] if relative == "." else relative.split(os.sep)
        for name in sorted(files):
            where = "/".join(["translations", *parts, name])
            if name != "README.md" or not 2 <= len(parts) <= 3:
                failures.add(where, "a translation is `translations/<locale>/NN-chapter[/MM-page]/README.md`")
                continue
            locale, *path = parts
            if locale not in LOCALES:
                failures.add(where, f"no locale {locale!r}; the locales are {list(LOCALES)}")
                continue
            english = os.path.join(root, *path, "README.md")
            if not (CHAPTER.match(path[0]) and (len(path) == 1 or PAGE.match(path[1]))) or not os.path.isfile(english):
                failures.add(where, f"translates {'/'.join(path)}/README.md, which does not exist")
                continue
            counted[0] += 1
            text = read(os.path.join(directory, name))
            fields, body = front_matter(text)
            if fields is None:
                failures.add(where, "no front matter")
                continue
            english_text = read(english)
            english_fields, english_body = front_matter(english_text)
            if english_fields is None:
                english_fields, english_body = {}, english_text
            for key in ("learn", "editions", "codes"):
                if fields.get(key) != english_fields.get(key):
                    failures.add(where, f"`{key}` is {fields.get(key)!r}, but the English page's is {english_fields.get(key)!r}")
            if len(path) == 2:
                number = english_fields.get("learn", "")
                first = body.lstrip("\n").split("\n", 1)[0]
                if not fields.get("title") or first != f"# {number} {fields.get('title')}":
                    failures.add(where, f"the title line must be `# {number} <title>`, with the translated `title`")
            status = fields.get("status")
            if status not in STATUSES:
                failures.add(where, f"`status` is {status!r}, not one of {list(STATUSES)}")
            digest = hashlib.sha256(english_text.encode("utf-8")).hexdigest()
            if fields.get("source") != digest:
                if status == "approved":
                    failures.add(where, f"approved for another text: `source` is not the SHA-256 of {'/'.join(path)}/README.md ({digest})")
                else:
                    stale.append(where)
            if status == "approved":
                counted[1] += 1
            import template2

            template2.check_translation(root, path, fields, template2.padded(text)[1], english_fields,
                                        template2.padded(english_text)[1] if english_fields else english_body, where, failures)
            headings, kept, tags = skeleton(body)
            english_headings, english_kept, english_tags = skeleton(english_body)
            if headings != english_headings:
                failures.add(where, f"its headings and numbered items {headings} are not the English page's {english_headings}")
            if kept != english_kept:
                missing = sorted(set(english_kept) - set(kept))
                extra = sorted(set(kept) - set(english_kept))
                failures.add(where, f"its code and links differ from the English page's: missing {missing}, added {extra} (or counts differ)")
            if tags != english_tags:
                failures.add(where, f"its HTML tags {tags} are not the English page's {english_tags}")
    return counted, stale


def neutrality(root, failures):
    """The neutrality check of the published text, when UNA_NEUTRALITY_PATTERN is set: no tracked
    text file, English or translated, a page, a package, an outcome or a change, matches the
    pattern, an extended regular expression read case-insensitively by `grep -E`, the dialect of
    the una release gate's own check. The pattern is read from the environment only, never
    stored or printed, and goes to grep on a pipe, never as an argument; a match reports the file
    only, never the text, and a pattern grep cannot apply fails with a fixed message. Returns
    the number of files checked, or None when the pattern is unset."""
    pattern = os.environ.get("UNA_NEUTRALITY_PATTERN")
    if not pattern:
        return None
    if len(pattern) > 60000:
        # More than a pipe holds at once: the write below would wait for a reader forever.
        failures.add("neutrality", "the pattern is longer than 60,000 characters")
        return 0
    listed = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=False)
    if listed.returncode != 0:
        failures.add("neutrality", "the tracked files cannot be listed")
        return 0
    files = [name for name in listed.stdout.decode("utf-8", "replace").split("\0") if name]
    if not files:
        return 0
    read_end, write_end = os.pipe()
    os.write(write_end, pattern.encode("utf-8") + b"\n")
    os.close(write_end)
    env = {k: v for k, v in os.environ.items() if k != "UNA_NEUTRALITY_PATTERN"}
    found = subprocess.run(
        ["grep", "-E", "-i", "-I", "-l", "-f", f"/dev/fd/{read_end}", "--", *files],
        cwd=root, capture_output=True, pass_fds=(read_end,), env=env, check=False,
    )
    os.close(read_end)
    if found.returncode == 0:
        for name in found.stdout.decode("utf-8", "replace").splitlines():
            failures.add(name, "matches the neutrality pattern")
    elif found.returncode != 1:
        failures.add("neutrality", "the pattern could not be applied: it is not a valid extended regular expression (grep -E)")
    return len(files)


def commits(root, failures):
    """Step 4: every commit's author and committer are GitHub noreply addresses."""
    result = subprocess.run(
        ["git", "log", "--format=%H %ae %ce"], cwd=root, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        failures.add("git", "cannot read the commits")
        return
    for line in result.stdout.splitlines():
        sha, author, committer = line.split(" ")
        if not NOREPLY.match(author):
            failures.add(f"commit {sha}", "the author email is not a GitHub noreply address")
        if not (NOREPLY.match(committer) or committer == "noreply@github.com"):
            failures.add(f"commit {sha}", "the committer email is not a GitHub noreply address")


def tracked_links(root, failures):
    """No tracked file is a symbolic link, anywhere in the repository."""
    result = subprocess.run(["git", "ls-files", "-s", "-z"], cwd=root, capture_output=True, check=False)
    for entry in result.stdout.decode("utf-8", "replace").split("\0"):
        mode, _, rest = entry.partition(" ")
        if mode == "120000":
            failures.add(rest.split("\t", 1)[-1], "a symbolic link; una-by-example holds none")


def tracked(root, failures):
    """No tracked file is Python bytecode: `__pycache__/` or `*.pyc` is a build artifact."""
    result = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True, check=False)
    for path in result.stdout.splitlines():
        if "__pycache__" in path.split("/") or path.endswith(".pyc"):
            failures.add(path, "Python bytecode is tracked; it is a build artifact")


def safe_members(archive, where, failures):
    """The regular-file members of `archive`; a member that is not a plain relative file or
    directory is a failure."""
    out = []
    for member in archive.getmembers():
        name = member.name
        if name.startswith("/") or ".." in name.split("/") or not (member.isfile() or member.isdir()):
            failures.add(where, f"an unsafe member: {name!r}")
            return None
        if member.uid != 0 or member.gid != 0 or member.uname or member.gname:
            failures.add(where, f"{name}: the owner must be 0:0, with no names")
        if member.isfile():
            out.append(member)
    return out


def unpack(path, where, failures):
    """The regular files of the archive at `path`, {name: bytes}, or None (missing, unsafe)."""
    if not os.path.isfile(path):
        failures.add(where, "missing")
        return None
    with tarfile.open(path, "r:gz") as archive:
        members = safe_members(archive, where, failures)
        if members is None:
            return None
        return {m.name: archive.extractfile(m).read() for m in members}


def tree_bytes(directory, leave_out=()):
    """Every file under `directory`, {relative path: bytes}, but the names in `leave_out`."""
    out = {}
    for base, dirs, files in os.walk(directory):
        dirs.sort()
        for name in sorted(files):
            relative = os.path.relpath(os.path.join(base, name), directory).replace(os.sep, "/")
            if relative not in leave_out:
                out[relative] = read_bytes(os.path.join(base, name))
    return out


def same_as_checked(unpacked, copy, where, failures, leave_out=()):
    """The identity of the two paths: a package as an archive gives it is, byte for byte, the
    copy of it that the check runs."""
    archived, checked = tree_bytes(unpacked, leave_out), tree_bytes(copy)
    if archived != checked:
        differ = sorted(n for n in set(archived) | set(checked) if archived.get(n) != checked.get(n))
        failures.add(where, f"is not the package the check runs: {differ[:5]} differ")


def write_out(found, target):
    for member, data in found.items():
        path = os.path.join(target, member)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as handle:
            handle.write(data)


def archives(root, una, directory, failures, scratch):
    """Step 5: each page's archive and each template 2 chapter's archive unpacks to its files
    and passes step 2, each package against its expected outcome in the repository, and each
    package unpacked is byte for byte the copy of it that the check runs (`same_as_checked`); the
    archive of everything holds exactly the root's files, every chapter's README.md and every
    page's and chapter's files; SHA256SUMS matches."""
    import template2

    for chapter in chapters(root):
        if not template2.is_v2_chapter(root, chapter):
            continue
        where = f"archive {chapter}.tar.gz"
        found = unpack(os.path.join(directory, f"{chapter}.tar.gz"), where, failures)
        if found is None:
            continue
        wanted = {f"{chapter}/{name}": read_bytes(source) for name, source in template2.chapter_files(root, chapter).items()}
        if found != wanted:
            failures.add(where, f"holds {sorted(found)}, not {sorted(wanted)}")
            continue
        unpacked = os.path.join(scratch, "archives", chapter)
        write_out(found, os.path.join(scratch, "archives"))
        packages = template2.chapter_packages(os.path.join(root, chapter), chapter, Failures())
        for ref, package in packages.items():
            if package.overlay and package.base is None:
                continue
            copy = os.path.join(scratch, "identity", chapter, *ref.split("/"))
            template2.materialize(package, copy)
            same_as_checked(os.path.join(unpacked, *ref.split("/")), copy, f"{where} {ref}", failures)
            expected = os.path.join(package.outcome_of().directory, "expected")
            if os.path.isdir(os.path.join(unpacked, *ref.split("/"))) and os.path.isdir(expected):
                outcome(una, os.path.join(unpacked, *ref.split("/")), expected, f"{where} {ref}", failures)
    for chapter, page in pages(root):
        if template2.is_v2_chapter(root, chapter):
            continue
        name = f"{chapter[:2]}-{page}"
        path = os.path.join(directory, f"{name}.tar.gz")
        where = f"archive {name}.tar.gz"
        if not os.path.isfile(path):
            failures.add(where, "missing")
            continue
        source = os.path.join(root, chapter, page)
        with tarfile.open(path, "r:gz") as archive:
            members = safe_members(archive, where, failures)
            if members is None:
                continue
            found = {m.name: archive.extractfile(m).read() for m in members}
        wanted = {f"{name}/{f}": read_bytes(os.path.join(source, f)) for f in package_files(source)}
        if found != wanted:
            failures.add(where, f"holds {sorted(found)}, not {sorted(wanted)}")
            continue
        unpacked = os.path.join(scratch, "archives", name)
        write_out(found, unpacked)
        copy = os.path.join(scratch, "identity", name)
        copy_package(source, copy)
        same_as_checked(os.path.join(unpacked, name), copy, where, failures, leave_out=("README.md",))
        outcome(una, os.path.join(unpacked, name), os.path.join(source, "expected"), where, failures)
    whole = f"una-by-example-{lock_version(root)}"
    path = os.path.join(directory, f"{whole}.tar.gz")
    if not os.path.isfile(path):
        failures.add(f"archive {whole}.tar.gz", "missing")
    else:
        with tarfile.open(path, "r:gz") as archive:
            members = safe_members(archive, f"archive {whole}.tar.gz", failures)
            if members is not None:
                found = {m.name: archive.extractfile(m).read() for m in members}
                wanted = {}
                for name in ("README.md", "LICENSE", "una.lock"):
                    if os.path.isfile(os.path.join(root, name)):
                        wanted[f"{whole}/{name}"] = read_bytes(os.path.join(root, name))
                for chapter in chapters(root):
                    if os.path.isfile(os.path.join(root, chapter, "README.md")):
                        wanted[f"{whole}/{chapter}/README.md"] = read_bytes(os.path.join(root, chapter, "README.md"))
                for chapter, page in pages(root):
                    if template2.is_v2_chapter(root, chapter):
                        continue
                    source = os.path.join(root, chapter, page)
                    for f in package_files(source):
                        wanted[f"{whole}/{chapter}/{page}/{f}"] = read_bytes(os.path.join(source, f))
                for chapter in chapters(root):
                    if template2.is_v2_chapter(root, chapter):
                        for name, source in template2.chapter_files(root, chapter).items():
                            wanted[f"{whole}/{chapter}/{name}"] = read_bytes(source)
                if found != wanted:
                    missing, extra = sorted(set(wanted) - set(found)), sorted(set(found) - set(wanted))
                    changed = sorted(n for n in set(found) & set(wanted) if found[n] != wanted[n])
                    failures.add(f"archive {whole}.tar.gz", f"does not hold exactly the repository's pages and chapters: missing {missing[:5]}, extra {extra[:5]}, changed {changed[:5]}")
    sums = os.path.join(directory, "SHA256SUMS")
    if not os.path.isfile(sums):
        failures.add("SHA256SUMS", "missing")
        return
    import hashlib

    for line in read(sums).splitlines():
        digest, _, name = line.partition("  ")
        target = os.path.join(directory, name)
        if not os.path.isfile(target) or hashlib.sha256(read_bytes(target)).hexdigest() != digest:
            failures.add("SHA256SUMS", f"{name} does not match")


def lock_version(root):
    for line in read(os.path.join(root, "una.lock")).splitlines():
        key, sep, value = line.partition("=")
        if sep and key.strip() == "version":
            return value.strip().strip('"')
    return None


def main(argv):
    if argv == ["--self-test"]:
        return self_test()
    if argv == ["--fill"]:
        import template2

        changed, problems = template2.fill(ROOT)
        for path in changed:
            print(f"check.py: filled {path}")
        for problem in problems:
            print(f"check.py: {problem}", file=sys.stderr)
        return 1 if problems else 0
    una = None
    from_binary = False
    archive_dir = None
    require_neutrality = False
    args = list(argv)
    while args:
        arg = args.pop(0)
        if arg == "--una" and args:
            una = args.pop(0)
        elif arg == "--una-version-from-binary":
            from_binary = True
        elif arg == "--archives" and args:
            archive_dir = args.pop(0)
        elif arg == "--require-neutrality":
            require_neutrality = True
        else:
            print(__doc__, file=sys.stderr)
            return 2
    if not una:
        print(__doc__, file=sys.stderr)
        return 2
    return check(ROOT, una, from_binary, archive_dir, require_neutrality)


def check(root, una, from_binary, archive_dir, require_neutrality=False):
    failures = Failures()
    global HOME
    scratch = tempfile.mkdtemp(prefix="una-by-example-")
    HOME = os.path.join(scratch, "home")
    os.makedirs(HOME)
    try:
        return checked(root, una, from_binary, archive_dir, require_neutrality, failures, scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
        HOME = None


def checked(root, una, from_binary, archive_dir, require_neutrality, failures, scratch):
    version = run(una, ["--json", "--version"], root)
    try:
        found = json.loads(version.stdout)["version"]
    except (ValueError, KeyError):
        print(f"check.py: FAIL\n  {una}: no version", file=sys.stderr)
        return 1
    wanted = lock_version(root)
    if not from_binary and found != wanted:
        failures.add("una.lock", f"pins una {wanted}, but {una} is {found}")
    counted = check_pages(root, una, failures, scratch)
    tracked_links(root, failures)
    if os.path.isdir(os.path.join(root, "translations")):
        symlinks(os.path.join(root, "translations"), "translations", failures)
    import template2

    warnings = []
    second = template2.check_chapters(root, una, failures, scratch, warnings)
    translated, stale = check_translations(root, failures)
    neutral = neutrality(root, failures)
    if neutral is None and require_neutrality:
        failures.add("neutrality", "--require-neutrality, but UNA_NEUTRALITY_PATTERN is unset or empty")
    commits(root, failures)
    tracked(root, failures)
    if archive_dir:
        archives(root, una, archive_dir, failures, scratch)
    if failures.items:
        print("check.py: FAIL", file=sys.stderr)
        for item in failures.items:
            print(f"  {item}", file=sys.stderr)
        return 1
    print(
        f"check.py: PASS ({counted[0]} pages, {counted[1]} changes, {counted[2]} commands, "
        f"{translated[0]} translations ({translated[1]} approved), una {found})"
    )
    print(f"  template 2: {second[0]} chapters, {second[1]} packages, {second[2]} commands")
    print(f"  neutrality: {'skipped (UNA_NEUTRALITY_PATTERN unset)' if neutral is None else f'PASS ({neutral} files)'}")
    for warning in warnings:
        print(f"  warning: {warning}")
    for where in stale:
        print(f"  out of date, a draft: {where}")
    return 0


# --- Self-test: synthetic pages, a stub `una`, and a git repository with a bad commit.

STUB = r'''#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
if args == ["--json", "--version"]:
    print(json.dumps({"schema": "una.version/1", "version": "9.9.9", "editions": ["0.2"], "z3": "5.1.0"}))
    sys.exit(0)
src = open("src/main.una").read()
if args == ["--json", "check", "."]:
    diagnostics = []
    if "bad" in src:
        start = {"line": 3, "col": 1}
        diagnostics.append({"code": "U1001", "severity": "error", "message": "unknown name `bad`",
                            "primary": {"file": "src/main.una", "start": start, "end": start}})
    if "cex" in src:
        start = {"line": 2, "col": 1}
        diagnostics.append({"code": "U5001", "severity": "error", "message": "refuted",
                            "primary": {"file": "src/main.una", "start": start, "end": start},
                            "counterexample": {"bindings": [{"name": "n", "value": -1}, {"name": "ok", "value": True}]}})
    print(json.dumps({"schema": "una.diagnostics/1", "diagnostics": diagnostics, "fixable": 0}))
    sys.exit(1 if diagnostics else 0)
if args == ["fmt", "--check", "."]:
    sys.exit(0)
if args == ["test", "."]:
    print("1 example passed")
    sys.exit(0)
if args == ["run", "."]:
    sys.stdout.write(src.split("print ", 1)[1] if "print " in src else "")
    sys.exit(0)
if args == ["report", "."]:
    target = src.split("target ", 1)[1].split()[0] if "target " in src else "aarch64-apple-darwin"
    print("package main 0.1.0")
    print(f"native: {target}")
    sys.exit(0)
sys.exit(2)
'''

README = """---
learn: "1.1"
title: A first page
editions: ["0.2"]
codes: [{codes}]
---

# 1.1 A first page

A lead.

## The program

The program.

## What you should see

What it prints.

## Try it

1. Write `bad`.

## See also

- Nothing.
"""


TRANSLATION = """---
learn: "1.1"
title: Uma primeira página
editions: ["0.2"]
codes: [U1001]
source: {source}
status: {status}
---

# 1.1 Uma primeira página

Uma introdução.

## O programa

O programa.

## O que você deve ver

O que ele imprime.

## Experimente

1. Escreva `bad`.

## Veja também

- Nada.
"""


def translate(root, status="approved", source=None, text=None, locale="pt-br", path=("01-hello", "01-first")):
    """Writes a translation of the fixture's page, by default approved for its current text."""
    import hashlib

    english = read(os.path.join(root, "01-hello", "01-first", "README.md"))
    digest = source if source is not None else hashlib.sha256(english.encode("utf-8")).hexdigest()
    text = text if text is not None else TRANSLATION
    write(os.path.join(root, "translations", locale, *path, "README.md"), text.format(source=digest, status=status))


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def fixture(root, readme=None, output="hi\n", try_file="bad\n"):
    """A repository with one chapter and one page."""
    write(os.path.join(root, "una.lock"), 'version = "9.9.9"\n')
    write(os.path.join(root, "01-hello", "README.md"), "# 1 Hello\n")
    page = os.path.join(root, "01-hello", "01-first")
    write(os.path.join(page, "README.md"), readme if readme is not None else README.format(codes="U1001"))
    write(os.path.join(page, "una.toml"), "[package]\n")
    write(os.path.join(page, "verification.lock"), "lock\n")
    write(os.path.join(page, "src", "main.una"), "module main\nprint hi\n")
    write(os.path.join(page, "expected", "output.txt"), output)
    write(os.path.join(page, "try", "1", "src", "main.una"), try_file)
    write(
        os.path.join(page, "try", "1", "expected", "diagnostics.txt"),
        "error U1001 at src/main.una:3:1: unknown name `bad`\n",
    )
    return page


def git(root, *args, email="1+someone@users.noreply.github.com"):
    env = dict(os.environ, GIT_AUTHOR_NAME="x", GIT_COMMITTER_NAME="x",
               GIT_AUTHOR_EMAIL=email, GIT_COMMITTER_EMAIL=email,
               GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_SYSTEM=os.devnull)
    subprocess.run(["git", *args], cwd=root, env=env, capture_output=True, check=True)


def quiet_check(root, una, archive_dir=None, require_neutrality=False):
    """`check` with its report captured: (exit code, report)."""
    saved = sys.stdout, sys.stderr
    from io import StringIO

    sys.stdout = sys.stderr = StringIO()
    try:
        code = check(root, una, False, archive_dir, require_neutrality)
        report = sys.stdout.getvalue()
    finally:
        sys.stdout, sys.stderr = saved
    return code, report


def self_test():
    base = tempfile.mkdtemp(prefix="una-by-example-self-test-")
    failed = []
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import archive as builder
    try:
        una = os.path.join(base, "una")
        write(una, STUB)
        os.chmod(una, 0o755)

        def case(name, expect_pass, mutate=None, wants=None, archive=False, pattern=None, require=False):
            root = os.path.join(base, name)
            page = fixture(root)
            if mutate:
                mutate(root, page)
            git(root, "init", "-q")
            git(root, "add", "-A")
            email = "someone@example.invalid" if name == "a personal email" else "1+someone@users.noreply.github.com"
            git(root, "commit", "-q", "-m", "c", email=email)
            archive_dir = None
            if archive:
                archive_dir = os.path.join(base, name + "-archives")
                builder.build(root, archive_dir, 0)
                if callable(archive):
                    archive(archive_dir)
            saved = os.environ.pop("UNA_NEUTRALITY_PATTERN", None)
            if pattern is not None:
                os.environ["UNA_NEUTRALITY_PATTERN"] = pattern
            try:
                code, report = quiet_check(root, una, archive_dir, require)
            finally:
                os.environ.pop("UNA_NEUTRALITY_PATTERN", None)
                if saved is not None:
                    os.environ["UNA_NEUTRALITY_PATTERN"] = saved
            ok = (code == 0) == expect_pass and (wants is None or wants in report)
            if not ok:
                failed.append(f"{name}: exit {code}\n{report}")

        case("a good page", True)
        case("a good page with archives", True, archive=True)
        case("a wrong output", False, lambda r, p: write(os.path.join(p, "expected", "output.txt"), "bye\n"), "not output.txt")
        case("a wrong diagnostic", False,
             lambda r, p: write(os.path.join(p, "try", "1", "expected", "diagnostics.txt"), "error U1002 at src/main.una:3:1: x\n"),
             "reports")
        def counterexample(r, p, line):
            write(os.path.join(p, "try", "1", "src", "main.una"), "cex\n")
            write(os.path.join(p, "try", "1", "expected", "diagnostics.txt"), "error U5001 at src/main.una:2:1: refuted\n" + line)
            write(os.path.join(p, "README.md"), README.format(codes="U5001"))

        case("a counterexample", True, lambda r, p: counterexample(r, p, "  counterexample: n = -1, ok = true\n"))
        case("a wrong counterexample", False, lambda r, p: counterexample(r, p, "  counterexample: n = 0, ok = true\n"), "reports")
        case("a command", True, lambda r, p: write(os.path.join(p, "expected", "commands", "test.txt"), "$ una test .\n1 example passed\n"))
        case("a wrong command output", False,
             lambda r, p: write(os.path.join(p, "expected", "commands", "test.txt"), "$ una test .\n2 examples passed\n"), "prints")
        report = "$ una report .\npackage main 0.1.0\nnative: aarch64-apple-darwin\n"

        def reported(r, p, target):
            write(os.path.join(p, "expected", "commands", "report.txt"), report)
            if target:
                write(os.path.join(p, "src", "main.una"), f"module main\n-- target {target}\nprint hi\n")
        case("a report on the same host", True, lambda r, p: reported(r, p, None))
        case("a report on the other supported host", True, lambda r, p: reported(r, p, "x86_64-unknown-linux-gnu"))
        case("a report on an unsupported host", False, lambda r, p: reported(r, p, "riscv64gc-unknown-linux-gnu"), "prints")

        def unrun(r, p, command):
            os.remove(os.path.join(p, "expected", "output.txt"))
            write(os.path.join(p, "expected", "diagnostics.txt"), "")
            if command:
                write(os.path.join(p, "expected", "commands", "test.txt"), "$ una test .\n1 example passed\n")
        case("an empty diagnostics.txt with a command", True, lambda r, p: unrun(r, p, True))
        case("an empty diagnostics.txt alone", False, lambda r, p: unrun(r, p, False), "an empty diagnostics.txt")
        case("both outcomes", False, lambda r, p: write(os.path.join(p, "expected", "diagnostics.txt"), "x\n"), "exactly one")
        case("a missing part", False,
             lambda r, p: write(os.path.join(p, "README.md"), README.format(codes="U1001").replace("## See also", "## Also")),
             "the parts must be")
        case("a wrong number", False,
             lambda r, p: write(os.path.join(p, "README.md"), README.format(codes="U1001").replace('learn: "1.1"', 'learn: "1.2"')),
             "its path says")
        case("wrong codes", False, lambda r, p: write(os.path.join(p, "README.md"), README.format(codes="")), "`codes`")
        case("a missing change", False,
             lambda r, p: write(os.path.join(p, "README.md"), README.format(codes="U1001").replace("1. Write `bad`.", "")),
             "lists 0 changes")
        case("a personal email", False, None, "noreply")
        case("tracked bytecode", False,
             lambda r, p: write(os.path.join(r, "scripts", "__pycache__", "x.cpython-314.pyc"), "x"),
             "bytecode is tracked")
        case("a wrong version", False, lambda r, p: write(os.path.join(r, "una.lock"), 'version = "1.0.0"\n'), "pins una")

        case("a translation", True, lambda r, p: translate(r), "1 translations (1 approved)")
        case("an out-of-date draft", True, lambda r, p: translate(r, "draft", "0" * 64), "out of date, a draft")
        case("an out-of-date approval", False, lambda r, p: translate(r, "approved", "0" * 64), "approved for another text")
        case("no status", False, lambda r, p: translate(r, "done"), "`status`")
        case("a changed code span", False,
             lambda r, p: translate(r, text=TRANSLATION.replace("`bad`", "`ruim`")), "code and links differ")

        def fenced(r, p, comment):
            english = README.format(codes="U1001").replace("The program.", "The program.\n\n```una\n-- a comment\nmain()\n```")
            write(os.path.join(p, "README.md"), english)
            translate(r, text=TRANSLATION.replace("O programa.", "O programa.\n\n```una\n" + comment + "\nmain()\n```"))

        case("a fenced block", True, lambda r, p: fenced(r, p, "-- a comment"))
        case("a translated comment", False, lambda r, p: fenced(r, p, "-- um comentário"), "code and links differ")
        case("a missing item", False,
             lambda r, p: translate(r, text=TRANSLATION.replace("1. Escreva `bad`.", "Escreva `bad`.")), "headings and numbered items")
        case("a changed link", False,
             lambda r, p: translate(r, text=TRANSLATION.replace("- Nada.", "- [Nada](https://example.org/)")), "code and links differ")
        case("other codes", False, lambda r, p: translate(r, text=TRANSLATION.replace("codes: [U1001]", "codes: []")), "`codes`")
        case("a translation of no page", False, lambda r, p: translate(r, path=("01-hello", "02-none")), "does not exist")
        case("an unknown locale", False, lambda r, p: translate(r, locale="fr"), "no locale")
        added = lambda extra: lambda r, p: translate(r, text=TRANSLATION.replace("O programa.", "O programa. " + extra))
        case("a bare URL", False, added("Veja https://example.org/x."), "code and links differ")
        case("an autolink", False, added("<https://example.org/>"), "code and links differ")
        case("a reference definition", False,
             lambda r, p: translate(r, text=TRANSLATION + "\n[x]: https://example.org/\n"), "code and links differ")
        case("an HTML tag", False, added('<img src="x" onerror="alert(1)">'), "HTML tags")
        case("an HTML closing tag", False, added("</details>"), "HTML tags")
        # A synthetic pattern stands for the real one, which is never written down.
        case("a neutral page", True, lambda r, p: translate(r), "neutrality: PASS (", pattern="zebra-canary")
        case("a match in a translation", False,
             lambda r, p: translate(r, text=TRANSLATION.replace("Uma introdução.", "Uma introdução, ZEBRA-CANARY.")),
             "translations/pt-br/01-hello/01-first/README.md: matches the neutrality pattern", pattern="zebra-canary")
        case("a match in a package", False,
             lambda r, p: write(os.path.join(p, "src", "main.una"), "module main\n-- zebra-canary\nprint hi\n"),
             "01-hello/01-first/src/main.una: matches the neutrality pattern", pattern="zebra-canary")
        case("a pattern grep cannot apply", False, None,
             "the pattern could not be applied: it is not a valid extended regular expression", pattern="(zebra-canary")
        case("a required pattern, unset", False, None, "UNA_NEUTRALITY_PATTERN is unset or empty", require=True)
        case("a required pattern, empty", False, None, "UNA_NEUTRALITY_PATTERN is unset or empty", pattern="", require=True)
        case("a required pattern, set", True, None, "neutrality: PASS", pattern="zebra-canary", require=True)
        case("a match in a page", False,
             lambda r, p: write(os.path.join(p, "README.md"), README.format(codes="U1001").replace("A lead.", "A zebra-canary lead.")),
             "matches the neutrality pattern", pattern="zebra-canary")

        def tamper(directory):
            path = os.path.join(directory, "01-01-first.tar.gz")
            with tarfile.open(path, "w:gz") as archive:
                info = tarfile.TarInfo("../escape")
                info.size = 0
                archive.addfile(info)

        case("an unsafe archive", False, archive=tamper, wants="unsafe member")

        # Two builds of the archives are the same bytes.
        root = os.path.join(base, "a good page")
        first, second = os.path.join(base, "build-1"), os.path.join(base, "build-2")
        builder.build(root, first, 0)
        builder.build(root, second, 0)
        for name in sorted(os.listdir(first)):
            if read_bytes(os.path.join(first, name)) != read_bytes(os.path.join(second, name)):
                failed.append(f"two builds of {name} differ")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    # The rules of template 2 have their own tests, with their own stub.
    import test_template2

    if test_template2.main() != 0:
        failed.append("template 2: scripts/test_template2.py failed")
    if failed:
        print("check.py: self-test FAIL", file=sys.stderr)
        for item in failed:
            print(f"  {item}", file=sys.stderr)
        return 1
    print("check.py: self-test PASS (47 cases, archives reproducible, and the template 2 tests)")
    return 0


def read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


if __name__ == "__main__":
    # One instance of this module: template2.py imports it as `check`, so run that one.
    import check

    sys.exit(check.main(sys.argv[1:]))
