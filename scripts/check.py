#!/usr/bin/env python3
"""Checks every example of Una by Example against a `una` binary.

For each page directory `NN-chapter/MM-page/`:

1. Its README.md has the front matter (`learn`, `title`, `editions`, `codes`) and the parts of
   the template in order, its `learn` number matches its path, and its `codes` are the codes its
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

Then every commit's author and committer must be GitHub noreply addresses, and with
`--archives DIR`, every archive of `scripts/archive.py` must unpack to its page's files, and
pass step 2 as unpacked.

Usage:
  check.py --una PATH [--una-version-from-binary] [--archives DIR]
  check.py --self-test

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


def front_matter(text):
    """The front matter of `text` as a dict of strings and lists, and the rest of the text."""
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
            items = [v.strip().strip('"') for v in value[1:-1].split(",") if v.strip()]
            fields[key.strip()] = items
        else:
            fields[key.strip()] = value.strip('"')
    return fields, text[end + 5 :]


def package_files(directory):
    """The files of the package in `directory`, relative to it, in order: the README, the
    manifest, the lock and every file under `src/`."""
    out = [name for name in PACKAGE_FILES if os.path.isfile(os.path.join(directory, name))]
    src = os.path.join(directory, "src")
    for base, dirs, files in os.walk(src):
        dirs.sort()
        for name in sorted(files):
            out.append(os.path.relpath(os.path.join(base, name), directory))
    return out


def copy_package(directory, to, overlay=None):
    """Copies the package in `directory` to `to`, then the files of `overlay` over it."""
    for name in package_files(directory):
        if name == "README.md":
            continue
        os.makedirs(os.path.dirname(os.path.join(to, name)) or to, exist_ok=True)
        shutil.copyfile(os.path.join(directory, name), os.path.join(to, name))
    if overlay:
        for base, dirs, files in os.walk(overlay):
            dirs[:] = sorted(d for d in dirs if not (base == overlay and d == "expected"))
            for name in sorted(files):
                source = os.path.join(base, name)
                target = os.path.join(to, os.path.relpath(source, overlay))
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copyfile(source, target)


def run(una, args, cwd):
    """Runs `una` with `args` in `cwd`."""
    return subprocess.run(
        [una, *args], cwd=cwd, capture_output=True, stdin=subprocess.DEVNULL, check=False
    )


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


def outcome(una, package, expected, where, failures):
    """Checks the package at `package` against the outcome in `expected`; returns its codes."""
    output = os.path.join(expected, "output.txt")
    listed = os.path.join(expected, "diagnostics.txt")
    if os.path.isfile(output) == os.path.isfile(listed):
        failures.add(where, "expected/ must hold exactly one of output.txt and diagnostics.txt")
        return set()
    lines, result = diagnostics_of(una, package)
    if lines is None:
        failures.add(where, f"`una check` printed no JSON: {result.stderr.decode(errors='replace')[:200]}")
        return set()
    if os.path.isfile(listed):
        wanted = [line for line in read(listed).splitlines() if line]
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


def commands(una, package, expected, where, failures):
    """Each `expected/commands/*.txt`: its first line is `$ una <args>`, and the rest is what
    that command prints on stdout in the package, byte for byte."""
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
        ran = run(una, first[len("$ una "):].split(" "), package)
        if ran.stdout.decode(errors="replace") != printed:
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
    for chapter in chapters(root):
        if not os.path.isfile(os.path.join(root, chapter, "README.md")):
            failures.add(chapter, "no README.md (the chapter page)")
    return counted


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


def archives(root, una, directory, failures, scratch):
    """Step 5: each page's archive unpacks to its files and passes step 2."""
    for chapter, page in pages(root):
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
        for member, data in found.items():
            target = os.path.join(unpacked, member)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "wb") as handle:
                handle.write(data)
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
                    wanted[f"{whole}/{chapter}/README.md"] = read_bytes(os.path.join(root, chapter, "README.md"))
                for chapter, page in pages(root):
                    source = os.path.join(root, chapter, page)
                    for f in package_files(source):
                        wanted[f"{whole}/{chapter}/{page}/{f}"] = read_bytes(os.path.join(source, f))
                if found != wanted:
                    failures.add(f"archive {whole}.tar.gz", "does not hold exactly the repository's pages")
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
    una = None
    from_binary = False
    archive_dir = None
    args = list(argv)
    while args:
        arg = args.pop(0)
        if arg == "--una" and args:
            una = args.pop(0)
        elif arg == "--una-version-from-binary":
            from_binary = True
        elif arg == "--archives" and args:
            archive_dir = args.pop(0)
        else:
            print(__doc__, file=sys.stderr)
            return 2
    if not una:
        print(__doc__, file=sys.stderr)
        return 2
    return check(ROOT, una, from_binary, archive_dir)


def check(root, una, from_binary, archive_dir):
    failures = Failures()
    version = run(una, ["--json", "--version"], root)
    try:
        found = json.loads(version.stdout)["version"]
    except (ValueError, KeyError):
        print(f"check.py: FAIL\n  {una}: no version", file=sys.stderr)
        return 1
    wanted = lock_version(root)
    if not from_binary and found != wanted:
        failures.add("una.lock", f"pins una {wanted}, but {una} is {found}")
    scratch = tempfile.mkdtemp(prefix="una-by-example-")
    try:
        counted = check_pages(root, una, failures, scratch)
        commits(root, failures)
        tracked(root, failures)
        if archive_dir:
            archives(root, una, archive_dir, failures, scratch)
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    if failures.items:
        print("check.py: FAIL", file=sys.stderr)
        for item in failures.items:
            print(f"  {item}", file=sys.stderr)
        return 1
    print(f"check.py: PASS ({counted[0]} pages, {counted[1]} changes, {counted[2]} commands, una {found})")
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


def quiet_check(root, una, archive_dir=None):
    """`check` with its report captured: (exit code, report)."""
    saved = sys.stdout, sys.stderr
    from io import StringIO

    sys.stdout = sys.stderr = StringIO()
    try:
        code = check(root, una, False, archive_dir)
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

        def case(name, expect_pass, mutate=None, wants=None, archive=False):
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
            code, report = quiet_check(root, una, archive_dir)
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
    if failed:
        print("check.py: self-test FAIL", file=sys.stderr)
        for item in failed:
            print(f"  {item}", file=sys.stderr)
        return 1
    print("check.py: self-test PASS (17 cases, archives reproducible)")
    return 0


def read_bytes(path):
    with open(path, "rb") as handle:
        return handle.read()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
