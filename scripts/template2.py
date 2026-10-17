"""The rules of template 2, a tutorial chapter on one page (TEMPLATE.md).

A chapter `NN-chapter/` is on template 2 when the front matter of its README.md is exactly
`template: 2`. A chapter is on template 1 only when its README.md has no front matter at all,
it has page directories `MM-page/`, and none of steps/, day-to-day/, mistakes/ or exercises/;
anything in between fails, so a chapter cannot leave the rules by a malformed front matter.

A chapter on template 2 holds its page, README.md, and its packages:

  steps/NN-slug/          one package per example in the text
  day-to-day/             the chapter's program
  mistakes/N/             one per common mistake, an overlay with its diagnostic
  exercises/N/start/      the starting point of an exercise, whose examples fail
  exercises/N/answer/     its answer, which checks clean, runs and passes `una test`
  exercises/N/<slug>/     any other state an exercise shows

Each of them is either a package (`una.toml`, `verification.lock`, `src/`) or an overlay: a
`base.txt` naming a package of the chapter (such as `day-to-day`), and the files that replace
that package's. Each has its own `expected/`, checked as check.py checks a page's, with one
more file: `expected/rendered.txt`, what `una --color never check .` prints on stderr, after
`normalize`. An overlay with no files of its own is the package it names, and has no
`expected/`. A package holds only the files of PACKAGE_FILE, and no symbolic link.

Every fenced block on the page is an include: its info string names a file of a package, and
its body is that file's text, exactly. The only blocks written by hand are `sh` blocks of
commands. No code may hide where the check does not look: a fence inside a quote or a list,
an indented code block, a setext heading, raw HTML, or an unknown container or callout fails.
See INCLUDES below.

Inside each `## N.k` section, `structure` checks the subsections: 3 to 12 `### ` in a concept
section, one `### ` per card in Common mistakes and Exercises, and the closing section
`Recap and reference` with `### For agents`, `### Recap` and `### Reference`; a breach fails.

Standard library only.
"""

import sys

sys.dont_write_bytecode = True

import difflib  # noqa: E402
import os  # noqa: E402
import re  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import check as base  # noqa: E402

INCLUDES = """
Include forms, in a fence's info string (the path is relative to the chapter directory; every
attribute value is quoted):

  ```una include="steps/01-quantity/src/quantity.una"        the whole file
  ```una include="day-to-day/src/orders.una#check_stock"     one top-level declaration, with
                                                             its doc comment
  ```una include="day-to-day/src/orders.una#reason..describe"
                                                             from one declaration to the end
                                                             of another
  ```text include="day-to-day/expected/output.txt"           an expected file
  ```text include="mistakes/2/expected/rendered.txt#L1"      lines: #L3, #L3-L9, and on an
                                                             expected file #L1,L8-L9
  ```diff include="day-to-day..mistakes/1:src/orders.una"    a unified diff, 3 lines of context
                                                             (context="1" to change it)

Other attributes: title="..." (the include's path), caption="..." (translatable),
verified="check, run, test", mistake="wrong" or mistake="right".
"""

TEMPLATE = "2"
FRONT_MATTER = ("learn", "title", "editions", "codes", "time", "builds", "prerequisites", "template")
# Optional fields. `nav`: the sidebar's short label of each numbered section `## N.1` to
# `## N.k`, in order, one per section: plain text of 1 to NAV_MAX characters, none of NAV_NOT.
OPTIONAL_FRONT_MATTER = ("nav",)
NAV_MAX = 32
NAV_NOT = '`~<>"'
KEPT_BY_TRANSLATIONS = ("template", "time", "prerequisites")
FIXED = ["## What you'll build", "## Why it works this way"]
DAY_TO_DAY = "Day-to-day: "
TAIL = ["Testing it", "Common mistakes", "Exercises", "Recap and reference"]
CONCEPTS = (3, 6)
# Inside a section (TEMPLATE.md): a concept section has SUBSECTIONS `### ` headings, none of them
# a GENERIC label; Common mistakes and Exercises have one `### ` per card; the closing section
# has exactly CLOSING, in order.
SUBSECTIONS = (3, 12)
GENERIC = {"overview", "introduction", "intro", "background", "basics", "details", "example", "examples",
           "more", "notes", "other", "misc", "summary", "usage", "discussion", "explanation", "more details",
           "further details", "general", "description"}
CLOSING = ["For agents", "Recap", "Reference"]
# The ids of the closing subsections, which no other heading of a chapter may take.
RESERVED_IDS = {"for-agents", "recap", "reference"}
# Day-to-day and Testing it have at least this many `### ` subsections.
PARTS_AT_LEAST = 2
# The tail before the section rules: For agents, Recap and Reference as sections of their own.
# headings() reads it so that structure() can say how to merge it; it always fails.
LEGACY_TAIL = ["Testing it", "Common mistakes", "For agents", "Exercises", "Recap", "Reference"]
GROUPS = ("steps", "day-to-day", "mistakes", "exercises")
ENTRIES = {"README.md", *GROUPS}
STEP = re.compile(r"^(\d\d)-[a-z0-9]+(?:-[a-z0-9]+)*$")
SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ATTRS = {"include", "title", "caption", "verified", "mistake", "context"}
VERIFIED = ("check", "run", "test")
OPEN = re.compile(r"^( {0,3})(`{3,}|~{3,})(.*)$")
ATTR = re.compile(r'\s+([A-Za-z][\w-]*)="([^"]*)"')
LINES = re.compile(r"^L(\d+)(?:-L(\d+))?$")
NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
KEYWORDS = {"pub", "trusted", "kind", "capability", "handler", "predicate", "opaque", "policy",
            "record", "requirement", "label", "const", "extern", "measure"}
NOT_DECLARATIONS = {"module", "import", "example"}
# The files a package or an overlay may hold, and the ones a block may include.
PACKAGE_FILE = re.compile(
    r"^(una\.toml|verification\.lock|base\.txt|src/([A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.una"
    r"|expected/(output|diagnostics|rendered)\.txt|expected/commands/[a-z0-9-]+\.txt)$"
)
INCLUDABLE = re.compile(
    r"^(una\.toml|src/([A-Za-z0-9_-]+/)*[A-Za-z0-9_-]+\.una"
    r"|expected/(output|diagnostics|rendered)\.txt|expected/commands/[a-z0-9-]+\.txt)$"
)
SOURCE = re.compile(r"^(una\.toml|src/.+\.una)$")
# A plain `sh` block holds only commands the reader types, never their output.
SH_LINE = re.compile(r"^(una (?P<args>.+)|(cd|mkdir) [A-Za-z0-9_./-]+|python3 -B scripts/check\.py( --fill| --self-test)?)$")
# The component vocabulary of TEMPLATE.md.
CONTAINERS = {"build", "steps", "decide", "mistake", "pair", "agents", "exercise", "hint", "answer",
              "recap", "reference"}
CALLOUTS = {"NOTE", "TIP", "IMPORTANT", "WARNING", "SECURITY", "KEY"}
# As the site reads them: a name right after the colons, and only spaces or tabs after a closer.
OPENER = re.compile(r"^(:{3,})([a-z][\w-]*)[ \t]*(.*)$")
CLOSER = re.compile(r"^(:{3,})[ \t]*$")
HTML = re.compile(r"<[A-Za-z/!?][^>\n]*>?")
AUTOLINK = re.compile(r"<(https?://|mailto:)[^>\s]*>")
# Word targets per part: outside them is a warning.
TARGETS = {
    "lead": (60, 120), "build": (80, 150), "why": (150, 300), "concept": (300, 2500),
    "day-to-day": (500, 1200), "testing": (200, 400), "agents": (60, 120), "recap": (80, 150),
    "page": (3000, 20000),
}
# Counts: mistakes and exercises fail outside (low, high), except that more than 8 mistakes is
# a warning; recap bullets only warn.
MISTAKES = (4, 8)
EXERCISES = (3, 5)
RECAP = (5, 8)


def is_v2(fields):
    return bool(fields) and fields.get("template") == TEMPLATE


def padded(text):
    """`front_matter(text)`, with the body preceded by as many empty lines as the front matter
    takes, so that a line number in the body is the line number in the file."""
    fields, body = base.front_matter(text)
    return fields, "\n" * text[:len(text) - len(body)].count("\n") + body


# --- Normalization of a rendered diagnostic.

def normalize(text, package):
    """What `expected/rendered.txt` holds for `text`, what una printed in the copy of a package
    at `package`: CRLF becomes LF; the copy's absolute path, followed by `/`, is removed, and
    where it stands alone it becomes `.` (both as given and with links resolved); spaces and
    tabs at the end of each line are removed; blank lines at the end are removed, and the text
    ends with one newline (or is empty)."""
    text = text.replace("\r\n", "\n")
    for path in sorted({package, os.path.realpath(package)}, key=len, reverse=True):
        path = path.rstrip("/")
        text = text.replace(path + "/", "").replace(path, ".")
    lines = [line.rstrip(" \t") for line in text.split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n" if lines else ""


# --- Fenced blocks.

class Block:
    """A fenced block of a page: where it is, its fence, its info string and body."""

    def __init__(self, line, indent, fence, info, body, closed):
        self.line, self.indent, self.fence, self.info, self.body, self.closed = line, indent, fence, info, body, closed
        match = re.match(r"^([A-Za-z0-9_+-]*)(.*)$", info.rstrip())
        self.lang, self.rest = match.group(1), match.group(2)
        self.attrs = {}
        self.duplicates = []
        self.stray = []
        position = 0
        for found in ATTR.finditer(self.rest):
            if found.start() != position:
                self.stray.append(self.rest[position:found.start()].strip())
            if found.group(1) in self.attrs:
                self.duplicates.append(found.group(1))
            self.attrs[found.group(1)] = found.group(2)
            position = found.end()
        if self.rest[position:].strip():
            self.stray.append(self.rest[position:].strip())

    def key(self):
        """What a translation keeps of the block: everything but the caption's text."""
        attrs = tuple(sorted((k, v) for k, v in self.attrs.items() if k != "caption"))
        return (self.indent, self.fence, self.lang, attrs, "caption" in self.attrs, tuple(self.stray), self.body)


def fences(text, lenient=False):
    """The fenced blocks of `text` that open at the start of a line (0 to 3 spaces), and the set
    of line numbers (0-based) inside them. A closer is the fence followed by spaces or tabs
    only, as the site reads it; `lenient` also takes any other whitespace after it."""
    lines = text.split("\n")
    out, inside = [], set()
    i = 0
    while i < len(lines):
        match = OPEN.match(lines[i])
        if not match or (match.group(2)[0] == "`" and "`" in match.group(3)):
            i += 1
            continue
        indent, fence, info = match.group(1), match.group(2), match.group(3)
        close = re.compile(r"^ {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}" + (r"\s*$" if lenient else r"[ \t]*$"))
        j = i + 1
        while j < len(lines) and not close.match(lines[j]):
            j += 1
        body = "\n".join(lines[i + 1:j]) + "\n" if j > i + 1 else ""
        out.append(Block(i + 1, indent, fence, info, body, j < len(lines)))
        inside.update(range(i, min(j, len(lines) - 1) + 1))
        i = j + 1
    return out, inside


def prose_lines(text):
    """The lines of `text` outside fenced blocks, as (0-based number, line)."""
    _, inside = fences(text)
    return [(n, line) for n, line in enumerate(text.split("\n")) if n not in inside]


# --- Code and markup the check would not see.

def columns(text, col):
    """The column after `text` (spaces and tabs) when it starts at `col`; tabs stop every 4."""
    for ch in text:
        col = col + 4 - col % 4 if ch == "\t" else col + 1
    return col


def analyse(line):
    """How Markdown reads the start of `line`: (rest, markers, lead, why). `rest` is the text
    after the blockquote and list-item markers, `markers` how many there were, `lead` the
    columns of whitespace before `rest`, and `why` a reason the line hides code, or None: a tab
    in the indentation; 4 or more columns at the start of the line, or 5 or more after a
    marker, which make an indented code block."""
    i, col, markers = 0, 0, 0
    while True:
        j = i
        while j < len(line) and line[j] in " \t":
            j += 1
        start = col
        col = columns(line[i:j], col)
        lead = col - start
        if j >= len(line):
            return "", markers, lead, None
        if "\t" in line[i:j]:
            return line[j:], markers, lead, "a tab in the indentation, which Markdown may read as code; indent with spaces"
        if lead >= (5 if markers else 4):
            return line[j:], markers, lead, (f"{lead} columns after a list or quote marker, which Markdown renders as code" if markers
                                             else "a line indented by 4 or more spaces, which Markdown may render as code; indent list items by 2 or 3 spaces")
        if line[j] == ">":
            i, col, markers = j + 1, col + 1, markers + 1
            continue
        marker = re.match(r"([-*+]|\d{1,9}[.)])(?=[ \t]|$)", line[j:])
        if marker:
            i, col, markers = j + len(marker.group(0)), col + len(marker.group(0)), markers + 1
            continue
        return line[j:], markers, lead, None


def strip_containers(line):
    """`line` without its blockquote and list-item markers: (rest, markers stripped)."""
    rest, markers, _, _ = analyse(line)
    return rest, markers


def invisible(text):
    """The characters a page's text may not hold, outside the bodies of its includes, as
    (line, why): controls but the tab (Cc), format characters (Cf), line and paragraph
    separators (Zl, Zp), and every space separator but the plain space (Zs), NBSP included.
    They make the check and the site read a line differently."""
    import unicodedata

    # Block ends as both readings see them: a line that closes a block for one and not for the
    # other is never skipped.
    blocks, _ = fences(text, lenient=True)
    skip = set()
    for block in blocks:
        if "include" in block.attrs:
            skip.update(range(block.line, block.line + block.body.count("\n")))
    out = []
    for n, line in enumerate(text.split("\n")):
        if n in skip:
            continue
        for ch in line:
            category = unicodedata.category(ch)
            if (category in ("Cc", "Cf", "Zl", "Zp") and ch != "\t") or (category == "Zs" and ch != " "):
                out.append((n + 1, f"the invisible or control character U+{ord(ch):04X}; page text holds plain spaces only"))
                break
    return out


def hidden_code(text):
    """Code outside the fences `fences` finds, as (line, why): a fence or a `$$` block inside a
    quote or a list item, or anywhere for `$$`; an indented code block (4 or more columns at the
    start of a line, 5 or more after a list or quote marker, or a tab); and invisible or control
    characters. Lists may nest one level, by 2 spaces."""
    out = list(invisible(text))
    for n, line in prose_lines(text):
        if not line.strip():
            continue
        rest, markers, lead, why = analyse(line)
        if rest.rstrip().startswith("$$"):
            out.append((n + 1, "a `$$` line, which the site renders as a block of code; Learn pages have none"))
            continue
        if re.match(r"^(`{3,}|~{3,})", rest):
            out.append((n + 1, "a fenced block inside a quote, a list or an indentation; every block starts at column 0, outside any container but ::: ones"))
            continue
        if why:
            out.append((n + 1, why))
    return out


def markup(text, where, failures):
    """The strict reading of a template 2 page or translation: no hidden code, headings only as
    `#` lines at column 0, no setext heading, no raw HTML, and only the containers and callouts
    of the template, each `:::` line at column 0."""
    for line, why in hidden_code(text):
        failures.add(f"{where}:{line}", why)
    previous, previous_n = "", -2
    stack = []
    for n, line in prose_lines(text):
        at = f"{where}:{n + 1}"
        rest, markers, lead, _ = analyse(line)
        if re.match(r"^#{1,6}(\s|$)", rest) and (markers or lead or not re.match(r"^#{1,6} \S", line)):
            failures.add(at, "a heading is a `#` line at column 0, `## Name`, outside quotes and lists")
        if rest.startswith(":::") and (markers or lead):
            failures.add(at, "a ::: line starts at column 0, outside quotes and lists")
        unquoted = re.sub(r"^( {0,3}>\s?)+", "", line)
        if re.match(r"^ {0,3}(=+|-+)[ \t]*$", unquoted) and previous_n == n - 1 and previous.strip() and not CLOSER.match(previous):
            failures.add(at, "a setext heading (a line of = or - under text); use `## ` headings, or a blank line before a rule")
        previous, previous_n = (unquoted if line.strip() else ""), n
        prose = spans_removed(AUTOLINK.sub("", line))
        if HTML.search(prose):
            failures.add(at, "raw HTML; the pages are Markdown without HTML")
        callout = re.match(r"^ {0,3}>\s*\[!([^\]]*)\]", line)
        if callout and callout.group(1) not in CALLOUTS:
            failures.add(at, f"no callout [!{callout.group(1)}]; they are {sorted(CALLOUTS)}")
        if line.startswith(":::"):
            opener, closer = OPENER.match(line), CLOSER.match(line)
            if opener:
                if opener.group(2) not in CONTAINERS:
                    failures.add(at, f"no container :::{opener.group(2)}; they are {sorted(CONTAINERS)}")
                stack.append(opener.group(1))
            elif closer:
                if not stack or stack[-1] != closer.group(1):
                    failures.add(at, "this closing ::: matches no open container of as many colons")
                else:
                    stack.pop()
            else:
                failures.add(at, "a ::: line is `:::name`, with the name right after the colons, or a closing `:::`")
    if stack:
        failures.add(where, f"{len(stack)} ::: container(s) not closed")


def spans_removed(text, unescape=False):
    """`text` without its code spans, read as CommonMark does: a backslash-escaped backtick
    opens no span, and a span closes on a run of as many backticks. Other backslash escapes of
    ASCII punctuation become blanks, or with `unescape` the character they escape, as in a
    link destination (`\\/` is `/`)."""
    text = re.sub(r"\\([!-/:-@\[-`{-~])", lambda m: "  " if m.group(1) == "`" or not unescape else m.group(1), text)
    return re.sub(r"(?<!`)(`+)(?!`)(.*?[^`])\1(?!`)", "", text)


REPOSITORY_HOSTS = {"github.com", "www.github.com", "raw.githubusercontent.com"}


def repository_link(target):
    """Whether `target`, read as the site reads a link (HTML entities decoded, percent escapes
    decoded, user information and port dropped, the host in any case and without a final
    dot), points into the una-lang repositories on GitHub."""
    from html import unescape
    from urllib.parse import unquote, urlsplit

    try:
        parts = urlsplit(unescape(target).strip())
        host = (parts.hostname or "").rstrip(".")
    except ValueError:
        return True
    return host in REPOSITORY_HOSTS and unquote(parts.path).lower().lstrip("/").startswith("una-lang/")


class Container:
    def __init__(self, name, start, rest):
        self.name, self.start, self.rest, self.end = name, start, rest, None


def containers(text):
    """The ::: containers of `text`, in order of opening, with their line ranges (1-based)."""
    out, stack = [], []
    for n, line in prose_lines(text):
        opener, closer = OPENER.match(line), CLOSER.match(line)
        if opener:
            container = Container(opener.group(2), n + 1, opener.group(3))
            container.colons = opener.group(1)
            out.append(container)
            stack.append(container)
        elif closer and stack and stack[-1].colons == closer.group(1):
            stack.pop().end = n + 1
    return out


# --- Declarations.

def declaration_name(line):
    """The name a top-level line declares, or None."""
    for word in re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\S", line):
        if word in NOT_DECLARATIONS:
            return None
        if word in KEYWORDS:
            continue
        return word if NAME.match(word) else None
    return None


def declarations(text):
    """The top-level declarations of a Una file: name -> list of (first, last) line indexes,
    0-based and inclusive. A declaration starts at its doc comment (the `---` lines right above
    it) and ends before the next top-level line (a line at column 0 that is neither blank nor a
    line starting with `=`), with blank lines at its end left out."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    top = [n for n, line in enumerate(lines) if line[:1] not in ("", " ", "\t", "=")]
    out = {}
    for index, n in enumerate(top):
        line = lines[n]
        if line.startswith("--"):
            continue
        name = declaration_name(line)
        if name is None:
            continue
        first = n
        while first > 0 and lines[first - 1].startswith("---"):
            first -= 1
        after = top[index + 1:]
        last = (after[0] if after else len(lines)) - 1
        while last > n and not lines[last].strip():
            last -= 1
        out.setdefault(name, []).append((first, last))
    return out


def select(text, selector, several=True):
    """The part of `text` that `selector` names: `name`, `first..last`, `L3-L9`, or with
    `several`, ascending and disjoint lists such as `L1,L8-L9`. Returns (text, None) or
    (None, why)."""
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    parts = selector.split(",")
    if all(LINES.match(p) for p in parts):
        if len(parts) > 1 and not several:
            return None, "several line ranges are allowed only on an expected/ file"
        picked = []
        after = 0
        for p in parts:
            match = LINES.match(p)
            low = int(match.group(1))
            high = int(match.group(2) or low)
            if not 1 <= low <= high <= len(lines):
                return None, f"lines {p} are not within the file's {len(lines)} lines"
            if low <= after:
                return None, f"line ranges go in ascending order without overlap; {p} does not"
            after = high
            picked.extend(lines[low - 1:high])
        return "\n".join(picked) + "\n", None
    first_name, sep, last_name = selector.partition("..")
    found = declarations(text)
    spans = []
    for name in (first_name, last_name) if sep else (first_name,):
        if not NAME.match(name):
            return None, f"`#{selector}` is neither a declaration's name nor lines such as `#L3-L9`"
        if name not in found:
            return None, f"no top-level declaration `{name}`"
        if len(found[name]) > 1:
            return None, f"`{name}` is declared {len(found[name])} times; include lines instead"
        spans.append(found[name][0])
    first, last = spans[0][0], spans[-1][1]
    if last < first:
        return None, f"`{last_name}` comes before `{first_name}`"
    return "\n".join(lines[first:last + 1]) + "\n", None


# --- Packages.

class Package:
    """A package or an overlay of a chapter: `ref` is its path in the chapter."""

    def __init__(self, ref, directory):
        self.ref, self.directory = ref, directory
        self.base = None
        self.clean = False
        self.runs = False
        self.tested = None
        self.copies = 0

    @property
    def overlay(self):
        return os.path.isfile(os.path.join(self.directory, "base.txt"))

    def files(self):
        """Every file under the package's directory, relative to it."""
        out = []
        for root, dirs, files in os.walk(self.directory):
            dirs.sort()
            for name in sorted(files):
                out.append(os.path.relpath(os.path.join(root, name), self.directory).replace(os.sep, "/"))
        return out

    def own_files(self):
        """An overlay's files, without base.txt and expected/."""
        return [f for f in self.files() if f != "base.txt" and not f.startswith("expected/")]

    @property
    def reference_only(self):
        return self.overlay and not self.own_files()

    def outcome_of(self):
        """The package whose outcome this one has: itself, or its base when it is a reference."""
        return self.base if self.reference_only and self.base else self

    def file(self, relative):
        """The path of `relative` as a reader of this package sees it, or None."""
        own = os.path.join(self.directory, *relative.split("/"))
        if relative.startswith("expected/"):
            return own if os.path.isfile(own) else None
        if os.path.isfile(own) and relative != "base.txt":
            return own
        if self.overlay and self.base is not None:
            return self.base.file(relative)
        return None


def chapter_packages(chapter_dir, where, failures):
    """The packages of a chapter, by ref, in order; checks the layout and what each holds."""
    found = {}
    base.symlinks(chapter_dir, where, failures)
    for name in sorted(os.listdir(chapter_dir)):
        if name not in ENTRIES:
            failures.add(f"{where}/{name}", "a chapter on template 2 holds only README.md, steps/, day-to-day/, mistakes/ and exercises/")
    steps = os.path.join(chapter_dir, "steps")
    if os.path.isdir(steps):
        names = sorted(os.listdir(steps))
        for index, name in enumerate(names, start=1):
            if not STEP.match(name) or int(name[:2]) != index or not os.path.isdir(os.path.join(steps, name)):
                failures.add(f"{where}/steps/{name}", f"steps are the directories 01-<slug>, 02-<slug>, ... in order; found {names}")
                continue
            found[f"steps/{name}"] = Package(f"steps/{name}", os.path.join(steps, name))
    if os.path.isdir(os.path.join(chapter_dir, "day-to-day")):
        found["day-to-day"] = Package("day-to-day", os.path.join(chapter_dir, "day-to-day"))
    else:
        failures.add(where, "no day-to-day/ package")
    for group in ("mistakes", "exercises"):
        directory = os.path.join(chapter_dir, group)
        if not os.path.isdir(directory):
            failures.add(where, f"no {group}/")
            continue
        names = sorted(os.listdir(directory), key=lambda n: (len(n), n))
        if names != [str(i) for i in range(1, len(names) + 1)] or not all(os.path.isdir(os.path.join(directory, n)) for n in names):
            failures.add(f"{where}/{group}", f"must hold the directories 1, 2, ...; found {names}")
            continue
        for name in names:
            if group == "mistakes":
                found[f"mistakes/{name}"] = Package(f"mistakes/{name}", os.path.join(directory, name))
                continue
            inner = sorted(os.listdir(os.path.join(directory, name)))
            for part in ("start", "answer"):
                if part not in inner:
                    failures.add(f"{where}/exercises/{name}", f"no {part}/")
            for part in inner:
                if not SLUG.match(part) or not os.path.isdir(os.path.join(directory, name, part)):
                    failures.add(f"{where}/exercises/{name}/{part}", "an exercise holds start/, answer/ and other <slug>/ packages only")
                    continue
                found[f"exercises/{name}/{part}"] = Package(f"exercises/{name}/{part}", os.path.join(directory, name, part))
    for package in found.values():
        here = f"{where}/{package.ref}"
        if os.path.islink(package.directory):
            continue
        for relative in package.files():
            if not PACKAGE_FILE.match(relative):
                failures.add(f"{here}/{relative}", "not a file a package holds: una.toml, verification.lock, src/**/*.una, base.txt in an overlay, "
                             "and expected/output.txt, diagnostics.txt, rendered.txt and commands/<name>.txt")
        if package.overlay:
            target = base.read(os.path.join(package.directory, "base.txt")).strip()
            package.base = found.get(target)
            if package.base is None or package.base.overlay:
                failures.add(here, f"base.txt names {target!r}, which is not a package of this chapter (an overlay's base is a package, not another overlay)")
                package.base = None
        else:
            for name in ("una.toml", "verification.lock", "src"):
                if not os.path.exists(os.path.join(package.directory, name)):
                    failures.add(here, f"no {name}: a package holds una.toml, verification.lock and src/, or is an overlay with base.txt")
        if package.ref.endswith("/answer") and package.reference_only:
            failures.add(here, "an answer changes something: an overlay with no files of its own is its base")
        if package.ref.startswith("mistakes/"):
            for name in ("diagnostics.txt", "rendered.txt"):
                if not os.path.isfile(os.path.join(package.directory, "expected", name)):
                    failures.add(here, f"a mistake has expected/{name}: the diagnostic it shows")
        has_expected = os.path.isdir(os.path.join(package.directory, "expected"))
        if package.reference_only and has_expected:
            failures.add(here, "an overlay with no files of its own is its base, and has no expected/")
        if not package.reference_only and not has_expected:
            failures.add(here, "no expected/")
    return found


def materialize(package, to):
    """Copies `package` to `to`: its base, then its own files over it. Symbolic links are
    never copied (`chapter_packages` fails them)."""
    if package.overlay:
        base.copy_package(package.base.directory, to)
        for relative in package.own_files():
            source = os.path.join(package.directory, *relative.split("/"))
            if os.path.islink(source):
                continue
            target = os.path.join(to, *relative.split("/"))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            shutil.copyfile(source, target, follow_symlinks=False)
    else:
        base.copy_package(package.directory, to)


def fresh(package, scratch):
    """A fresh copy of the package (or of its base, for a reference), for one command: what a
    command writes never reaches another."""
    target = package.outcome_of()
    target.copies += 1
    copy = os.path.join(scratch, *target.ref.split("/"), str(target.copies))
    materialize(target, copy)
    return copy


def una(una_path, args, cwd):
    return subprocess.run([una_path, *args], cwd=cwd, capture_output=True, stdin=subprocess.DEVNULL,
                          env=base.una_env(), check=False)


def rendered(una_path, copy):
    """What `una --color never check .` prints on stderr in `copy`, normalized."""
    return normalize(una(una_path, ["--color", "never", "check", "."], copy).stderr.decode("utf-8", "replace"), copy)


def exits(code):
    return "is not run, since its una.toml is not allowed" if code == -1 else f"exits with {code}"


def tested(una_path, package, scratch):
    """`una test .` on a fresh copy of the package, once; returns its exit code, or -1 when the
    manifest is not allowed and nothing ran."""
    target = package.outcome_of()
    if target.tested is None:
        copy = fresh(target, scratch)
        if not base.manifest(copy, target.ref, base.Failures()):
            target.tested = -1
        else:
            target.tested = una(una_path, ["test", "."], copy).returncode
    return target.tested


def check_packages(una_path, packages, where, failures, scratch):
    """Checks every package's outcome, as check.py checks a page's, its commands and rendered
    diagnostics, each on a fresh copy, and the exercises; returns the codes the outcomes show
    and the number of commands."""
    codes, count = set(), 0
    for package in packages.values():
        if package.reference_only or (package.overlay and package.base is None):
            continue
        here = f"{where}/{package.ref}"
        expected = os.path.join(package.directory, "expected")
        if not os.path.isdir(expected):
            continue
        before = len(failures.items)
        codes |= base.outcome(una_path, fresh(package, scratch), expected, here, failures)
        count += base.commands(una_path, None, expected, here, failures, fresh=lambda: fresh(package, scratch))
        package.runs = os.path.isfile(os.path.join(expected, "output.txt"))
        package.clean = package.runs and len(failures.items) == before
        shown = os.path.join(expected, "rendered.txt")
        if os.path.isfile(shown):
            copy = fresh(package, scratch)
            printed = rendered(una_path, copy) if base.manifest(copy, here, base.Failures()) else ""
            if printed != base.read(shown):
                failures.add(f"{here}/expected/rendered.txt", "is not what `una --color never check .` prints on stderr (normalized):\n" + printed)
    for ref, package in packages.items():
        if not (ref.startswith("exercises/") and ref.endswith("/answer")):
            continue
        here = f"{where}/{ref}"
        if not package.overlay or package.base is not None:
            if not package.runs:
                failures.add(here, "an answer checks clean and runs: its expected/ holds output.txt")
            code = tested(una_path, package, scratch)
            if code != 0:
                failures.add(here, f"an answer passes its tests, but `una test .` {exits(code)}")
        start = packages.get(ref[:-len("answer")] + "start")
        if start is not None and (not start.overlay or start.base is not None):
            if tested(una_path, start, scratch) == 0:
                failures.add(f"{where}/{start.ref}", "the exercise's examples fail on start/: `una test .` passes there, so nothing tells the reader when the answer is done")
    return codes, count


# --- Includes.

def plain(path):
    return bool(path) and not path.startswith("/") and "\\" not in path and ".." not in path.split("/")


def package_of(packages, path):
    """(package, path in it) for a chapter-relative path, or (None, why)."""
    if not plain(path):
        return None, f"{path!r} is not a plain path in the chapter"
    for ref in sorted(packages, key=len, reverse=True):
        if path.startswith(ref + "/"):
            return packages[ref], path[len(ref) + 1:]
    return None, f"{path!r} is not in a package of the chapter (steps/, day-to-day/, mistakes/, exercises/)"


def inside_chapter(path, chapter_dir):
    """Whether `path` is a plain file of the chapter: no symbolic link on the way out of it."""
    real = os.path.realpath(path)
    return not os.path.islink(path) and real.startswith(os.path.realpath(chapter_dir) + os.sep)


class Include:
    """What an include names: its text, its package, the file in it, and the other side of a
    diff."""

    def __init__(self, text, package, relative, old=None, selector=""):
        self.text, self.package, self.relative, self.old, self.selector = text, package, relative, old, selector


def resolve(block, packages, chapter_dir):
    """The include of `block`: (Include, None) or (None, why)."""
    spec = block.attrs.get("include", "")
    if block.lang == "diff":
        match = re.match(r"^([^:]+)\.\.([^:]+):(.+)$", spec)
        if not match:
            return None, "a diff include is `A..B:FILE`, two packages and a file of both"
        old, new, relative = match.groups()
        if not plain(relative) or not INCLUDABLE.match(relative):
            return None, f"{relative!r} is not a file a block may show"
        sides = []
        for ref in (old, new):
            package = packages.get(ref)
            if package is None:
                return None, f"{ref!r} is not a package of the chapter"
            path = package.file(relative)
            if path is None:
                return None, f"{ref} has no {relative}"
            if not inside_chapter(path, chapter_dir):
                return None, f"{ref}/{relative} is a symbolic link or outside the chapter"
            sides.append(base.read(path).splitlines(keepends=True))
        context = block.attrs.get("context", "3")
        if not context.isdigit():
            return None, "context= is a number of lines"
        lines = list(difflib.unified_diff(sides[0], sides[1], f"a/{relative}", f"b/{relative}", n=int(context)))
        if not lines:
            return None, f"{old} and {new} have the same {relative}"
        text = "".join(line if line.endswith("\n") else line + "\n" for line in lines)
        return Include(text, packages[new], relative, packages[old]), None
    path, _, selector = spec.partition("#")
    package, relative = package_of(packages, path)
    if package is None:
        return None, relative
    if not INCLUDABLE.match(relative):
        return None, f"{path}: a block shows una.toml, src/**/*.una or an expected/ file, not {relative}"
    file = package.file(relative)
    if file is None:
        return None, f"{path} does not exist"
    if not inside_chapter(file, chapter_dir):
        return None, f"{path} is a symbolic link or outside the chapter"
    text = base.read(file)
    if text and not text.endswith("\n"):
        text += "\n"
    if selector:
        text, why = select(text, selector, several=relative.startswith("expected/"))
        if text is None:
            return None, f"{path}: {why}"
    return Include(text, package, relative, selector=selector), None


def check_sh(block, at, failures):
    """A plain `sh` block: commands only, one per line, no prompt and no output."""
    for line in block.body.split("\n"):
        match = SH_LINE.match(line)
        if line.strip() and (not match or (match.group("args") is not None and not base.COMMAND.fullmatch(match.group("args")))):
            failures.add(at, f"an `sh` block holds only commands (una, cd, mkdir), with no prompt and no output; not {line!r}")


def check_blocks(text, packages, chapter_dir, where, failures, una_path=None, scratch=None):
    """Every fenced block of a page is an include whose body is the included text. Returns the
    blocks with their includes, as (block, Include or None)."""
    out = []
    blocks, _ = fences(text)
    for block in blocks:
        at = f"{where}:{block.line}"
        if not block.closed:
            failures.add(at, "a fenced block is not closed")
            out.append((block, None))
            continue
        if "include" not in block.attrs:
            if block.info.strip() == "sh" and not block.indent:
                check_sh(block, at, failures)
            else:
                failures.add(at, f"a ```{block.info.strip()} block that is not an include: every block on a template 2 page comes from a checked package (only plain `sh` blocks of commands are written by hand)")
            out.append((block, None))
            continue
        if not block.lang:
            failures.add(at, "an include names its language first, such as ```una include=\"...\"")
        if block.indent:
            failures.add(at, "an include's fence starts at column 0")
        for key in block.attrs:
            if key not in ATTRS:
                failures.add(at, f"no fence attribute `{key}`; they are {sorted(ATTRS)}")
        for key in block.duplicates:
            failures.add(at, f"the attribute `{key}` is given twice")
        if block.stray:
            failures.add(at, f"cannot read {block.stray} in the info string; attributes are key=\"value\", quoted")
        if block.attrs.get("mistake", "wrong") not in ("wrong", "right"):
            failures.add(at, "mistake= is \"wrong\" or \"right\"")
        found, why = resolve(block, packages, chapter_dir)
        out.append((block, found))
        if found is None:
            failures.add(at, f"include={block.attrs['include']}: {why}")
            continue
        if "title" in block.attrs:
            path = block.attrs["include"].partition("#")[0]
            allowed = {found.relative} if block.lang == "diff" else {path, found.relative}
            if block.attrs["title"] not in allowed:
                failures.add(at, f"title=\"{block.attrs['title']}\" is not the included file's path ({' or '.join(sorted(allowed))})")
        if re.search(r"^ {0,3}" + re.escape(block.fence[0]) + "{" + str(len(block.fence)) + r",}[ \t]*$", found.text, re.M):
            failures.add(at, f"the included text holds a line that closes a {block.fence} fence; use a longer fence")
        if block.body != found.text:
            failures.add(at, f"the block is not the text of include={block.attrs['include']} (run `python3 -B scripts/check.py --fill`)")
        verified = [v.strip() for v in block.attrs.get("verified", "").split(",") if v.strip()]
        if "verified" in block.attrs:
            if block.lang == "diff" or not SOURCE.match(found.relative) or LINES.match(found.selector.split(",")[0] or "-"):
                failures.add(at, "verified= goes only on a block of una.toml or a src/ file, whole or by declaration, not on a diff or lines")
            if not verified:
                failures.add(at, "verified= lists at least one of check, run, test")
        for token in verified:
            if token not in VERIFIED:
                failures.add(at, f"verified= lists {list(VERIFIED)}, not {token!r}")
        if una_path is not None and verified:
            target = found.package.outcome_of()
            if "check" in verified and not target.clean:
                failures.add(at, f"verified=check, but {found.package.ref} does not check clean")
            if "run" in verified and not target.runs:
                failures.add(at, f"verified=run, but {found.package.ref} has no expected/output.txt for `una run`")
            if "test" in verified:
                code = tested(una_path, found.package, scratch)
                if code != 0:
                    failures.add(at, f"verified=test, but `una test .` {exits(code)} in {found.package.ref}")
    return out


def refs_of(found):
    """The packages an include shows: its package, and a diff's other side."""
    if found is None:
        return set()
    return {found.package.ref} | ({found.old.ref} if found.old is not None else set())


# --- The page.

def sections(text):
    """The page split at its `## ` headings outside fences: [(heading or None, [(n, line)])],
    n 0-based."""
    _, inside = fences(text)
    out = [(None, [])]
    for n, line in enumerate(text.split("\n")):
        if n not in inside and line.startswith("## "):
            out.append((line, []))
        else:
            out[-1][1].append((n, line))
    return out


def words(lines, inside):
    count = 0
    for n, line in lines:
        # Prose only: code, ::: lines and headings do not count.
        if n in inside or OPENER.match(line) or CLOSER.match(line) or re.match(r"^#{1,6} ", line):
            continue
        count += len(re.findall(r"[^\s|>*`#-]\S*", line))
    return count


def headings(fields, body, where, failures):
    """The parts of the template, in order. Returns the number of concept sections, or None."""
    number = fields.get("learn", "")
    lines = [line for _, line in prose_lines(body)]
    first = body.lstrip("\n").split("\n", 1)[0]
    if first != f"# {number} {fields.get('title', '')}":
        failures.add(where, f"the title line must be `# {number} {fields.get('title', '')}`")
    if [line for line in lines if line.startswith("# ")] != [first]:
        failures.add(where, "the page has one `# ` heading, its title")
    found = [line for line in lines if line.startswith("## ")]
    shape = (f"`## What you'll build`, `## Why it works this way`, then `## {number}.1 <concept>` to "
             f"`## {number}.k <concept>` (k from {CONCEPTS[0]} to {CONCEPTS[1]}), then `## {number}.k+1 {DAY_TO_DAY}<program>`, "
             + ", ".join(f"`## {number}.k+{i} {t}`" for i, t in enumerate(TAIL, start=2)))
    # LEGACY_TAIL passes here; structure() fails it with how to merge it.
    if found[:2] != FIXED:
        failures.add(where, f"the parts must be {shape}; found {found}")
        return None
    titles = []
    for index, line in enumerate(found[2:], start=1):
        match = re.match(rf"^## {re.escape(number)}\.(\d+) (\S.*)$", line)
        if not match or int(match.group(1)) != index:
            failures.add(where, f"`{line}` must be numbered `## {number}.{index} <name>`; the parts must be {shape}")
            return None
        titles.append(match.group(2))
    starts = [i for i, t in enumerate(titles) if t.startswith(DAY_TO_DAY)]
    if not starts or not titles[starts[0]][len(DAY_TO_DAY):].strip():
        failures.add(where, f"no `## {number}.k+1 {DAY_TO_DAY}<program>`; the parts must be {shape}")
        return None
    concepts = starts[0]
    if not CONCEPTS[0] <= concepts <= CONCEPTS[1] or titles[concepts + 1:] not in (TAIL, LEGACY_TAIL):
        failures.add(where, f"the parts must be {shape}; found {found}")
        return None
    return concepts


def subsections(lines, inside):
    """The `### ` subsections of a section's lines, outside fences: [(title or None, [(n, line)])],
    the first entry holding the lines before the first `### `. A heading's own line is in no entry."""
    out = [(None, [])]
    for n, line in lines:
        if n not in inside and line.startswith("### "):
            out.append((line[4:].strip(), []))
        else:
            out[-1][1].append((n, line))
    return out


def generic(title):
    """Whether a heading's title is a generic label (`Overview`, `An overview`, `Details.`)."""
    words = re.sub(r"[^a-z ]", "", title.lower()).split()
    if words and words[0] in ("a", "an", "the"):
        words = words[1:]
    return " ".join(words) in GENERIC


def slug(text):
    """A heading's id as the site makes it (website scripts/preview/markdown.mjs, `slug`): the
    heading's text without its inline markup, lowercase, with every character that is not a
    letter, a digit, a space or `-` dropped, trimmed, and each run of spaces as one `-`."""
    text = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = text.lower().replace("`", "")
    text = re.sub(r"[^\w\s-]|_", "", text).strip()
    return re.sub(r"\s+", "-", text)


def heading_ids(body):
    """Every heading of a page outside fences, as the site gives it ids: [{line, level, text,
    base, id, number, section}]. A heading numbered `N.M` (`## 6.1 …`) has the id `sN-M`; any
    other the slug of its words, with `-1` appended while it is taken. A heading of level 3 or
    deeper inside a numbered section also has the number the site gives it (`6.2.1`, `6.2.1.1`:
    a level that skips its parent counts that parent as 1), whose id is `s6-2-1`. `section` is
    the numbered section's title without its number, or None."""
    _, inside = fences(body)
    out, used = [], set()
    prefix, section, counts = None, None, []
    for n, line in enumerate(body.split("\n")):
        match = re.match(r"^(#{1,6}) (.*?)\s*$", line)
        if n in inside or not match:
            continue
        level, text = len(match.group(1)), match.group(2)
        dotted = re.match(r"^(\d+(?:\.\d+)+)\s", text)
        number = None
        if level <= 2:
            prefix = dotted.group(1) if level == 2 and dotted else None
            section = re.sub(r"^\d+\.\d+ ", "", text) if prefix else None
            counts = []
        elif prefix:
            depth = level - 3
            counts = (counts + [0] * (depth + 1))[:depth + 1]
            counts = [c or 1 for c in counts[:depth]] + [counts[depth] + 1]
            number = prefix + "." + ".".join(str(c) for c in counts)
        base_id = "s" + dotted.group(1).replace(".", "-") if dotted else slug(text)
        ident = base_id
        while ident in used:
            ident += "-1"
        used.add(ident)
        out.append({"line": n + 1, "level": level, "text": text, "base": base_id, "id": ident,
                    "number": number, "section": section})
    return out


def anchors(body, where, failures):
    """The anchors of a page: every `#id` link names a heading of the page (its id, or the id
    of its number, `#s6-2-1`); no two headings have the same id; and no heading's words make
    the id of a section number. Returns heading_ids(body)."""
    found = heading_ids(body)
    for heading in found:
        if heading["id"] != heading["base"]:
            failures.add(f"{where}:{heading['line']}", f"`{heading['text']}` has the id `{heading['base']}`, as an earlier heading does; "
                         "every heading of a chapter has its own words, so that its anchor is its own")
        if not re.match(r"^\d+(?:\.\d+)+\s", heading["text"]) and re.match(r"^s\d+(-\d+)+$", heading["base"]):
            failures.add(f"{where}:{heading['line']}", f"`{heading['text']}` would take the id of a section number (`{heading['base']}`); reword it")
    known = {h["id"] for h in found} | {"s" + h["number"].replace(".", "-") for h in found if h["number"]}
    rest = "\n".join(spans_removed(line, unescape=True) for _, line in prose_lines(body))
    for target in LINK.findall(rest) + base.REFERENCE.findall(rest):
        if not target.startswith("#"):
            continue
        from urllib.parse import unquote

        ident = unquote(target[1:])
        if ident not in known:
            failures.add(where, f"the link {target} names no heading of the chapter; a numbered heading's anchor is its number "
                         "(#s6-1), another's the slug of its words (#what-youll-build)")
    return found


def structure(body, concepts, where, failures, chapter_dir=None):
    """The rules inside a section (TEMPLATE.md, "Inside a section"): 3 to 12 `### ` subsections
    with specific titles in each concept section; in Common mistakes and Exercises, one `### `
    per card, each holding its card; and the closing section `Recap and reference` with exactly
    `### For agents`, `### Recap` and `### Reference`. Every breach fails. Returns the breaches."""
    _, inside = fences(body)
    boxes = containers(body)
    numbered = [(h, lines) for h, lines in sections(body) if h and re.match(r"^## \d+\.\d+ ", h)]
    titles = [re.sub(r"^## \d+\.\d+ ", "", h) for h, _ in numbered]
    problems = []
    if titles[concepts + 1:] == LEGACY_TAIL:
        number = re.match(r"^## (\d+)\.", numbered[0][0]).group(1)
        problems.append(f"For agents, Recap and Reference are one closing section, `## {number}.{concepts + 5} Recap and reference`, "
                        "with `### For agents`, `### Recap` and `### Reference`; the sections after it are renumbered")
    for index, ((heading, lines), title) in enumerate(zip(numbered, titles)):
        found = subsections(lines, inside)[1:]
        names = [name for name, _ in found]
        label = heading[3:]
        if index < concepts:
            if not SUBSECTIONS[0] <= len(names) <= SUBSECTIONS[1]:
                problems.append(f"`{label}` has {len(names)} `### ` subsections; a concept section has {SUBSECTIONS[0]} to {SUBSECTIONS[1]}")
        elif title.startswith(DAY_TO_DAY) or title == "Testing it":
            if len(names) < PARTS_AT_LEAST:
                problems.append(f"`{label}` has {len(names)} `### ` subsections; it has at least {PARTS_AT_LEAST}: "
                                + ("one per part of the program, then running it" if title != "Testing it" else "one per kind of test"))
        if title in ("Common mistakes", "Exercises"):
            card = "mistake" if title == "Common mistakes" else "exercise"
            cards_of = [box for box in boxes if box.name == card and lines and lines[0][0] < box.start <= lines[-1][0] + 1]
            spans = [(sub[0][0] + 1 if sub else None, sub[-1][0] + 1 if sub else None) for _, sub in found]
            per = [sum(1 for box in cards_of if a is not None and a <= box.start <= b) for a, b in spans]
            loose = len(cards_of) - sum(per)
            if len(names) != len(cards_of) or loose or any(k != 1 for k in per):
                problems.append(f"`{label}` has one `### ` subsection per :::{card} card, titled by the {card}, "
                                f"with its card in it; found {len(names)} subsections for {len(cards_of)} cards")
            for k, name in enumerate(names, start=1):
                if card == "exercise" and not re.match(rf"^Exercise {k}: \S", name):
                    problems.append(f"`{label}`: subsection {k} is titled `### Exercise {k}: <goal>`; found `### {name}`")
                if card == "mistake":
                    code = re.search(r"\((U\d{4}(?:, U\d{4})*)\)$", name)
                    shown = None
                    if chapter_dir is not None:
                        path = os.path.join(chapter_dir, "mistakes", str(k), "expected", "diagnostics.txt")
                        shown = set(re.findall(r"^error (U\d{4}) ", base.read(path), re.M)) if os.path.isfile(path) else set()
                    if not code:
                        problems.append(f"`{label}`: `### {name}` ends with its code in parentheses, such as `(U3007)` or `(U0101, U7002)`")
                    elif shown is not None:
                        for named in code.group(1).split(", "):
                            if named not in shown:
                                problems.append(f"`{label}`: `### {name}` names {named}, but mistakes/{k} reports {sorted(shown) or 'no code'}")
        elif title == "Recap and reference":
            loose = [line for n, line in subsections(lines, inside)[0][1] if line.strip()]
            if names != CLOSING or loose:
                problems.append(f"`{label}` holds exactly `### For agents`, `### Recap` and `### Reference`, in order; "
                                f"found {['### ' + n for n in names]}" + (" and text before them" if loose else ""))
    # No generic title anywhere, and the closing ids only on the closing subsections.
    for heading in heading_ids(body):
        if heading["level"] >= 3 and generic(heading["text"]):
            problems.append(f"`### {heading['text']}` (line {heading['line']}) is a generic label; title a subsection by what it holds")
        if heading["base"] in RESERVED_IDS and not (heading["level"] == 3 and heading["section"] == "Recap and reference"):
            problems.append(f"`{heading['text']}` (line {heading['line']}) takes the id `{heading['base']}`, which only the "
                            "closing section's `### For agents`, `### Recap` and `### Reference` have")
    for problem in problems:
        failures.add(where, problem)
    return problems


def check_yourself(body, concepts, where, warnings):
    """A warning for each concept section with no `### Check yourself: <topic>` subsection
    (TEMPLATE.md, "Teaching a concept"). It warns, and does not fail, while the chapters are
    rewritten to the standard."""
    _, inside = fences(body)
    numbered = [(h, lines) for h, lines in sections(body) if h and re.match(r"^## \d+\.\d+ ", h)]
    for heading, lines in numbered[:concepts]:
        names = [name for name, _ in subsections(lines, inside)[1:]]
        if not any(name and name.startswith("Check yourself") for name in names):
            warnings.append(f"{where}: `{heading[3:]}` has no `### Check yourself: <topic>` subsection")


def numbered(body, number):
    """The `## N.M` headings of the page, as their numbers."""
    return [line.split(" ")[1] for _, line in prose_lines(body) if re.match(rf"^## {re.escape(number)}\.\d+ ", line)]


def nav(fields, body, number, where, failures):
    """The optional `nav` of the front matter: a list of labels, one per numbered section, in
    order, each plain text of 1 to NAV_MAX characters, with no character of NAV_NOT, no space at
    its ends, no section number of its own, and no control, format or other invisible
    character."""
    import unicodedata

    if "nav" not in fields:
        return
    labels = fields["nav"]
    sections = numbered(body, number)
    if not isinstance(labels, list):
        failures.add(where, '`nav` is a list of quoted labels, one per numbered section, such as ["fails and fail", "Recap"]')
        return
    if len(labels) != len(sections):
        failures.add(where, f"`nav` has {len(labels)} labels, but the page has {len(sections)} numbered sections"
                            f" ({sections[0] if sections else 'none'} to {sections[-1] if sections else 'none'}); give one per section, in order")
    for i, label in enumerate(labels):
        name = f"`nav` label {i + 1}" + (f" (for {sections[i]})" if i < len(sections) else "")
        if not label.strip() or label != label.strip():
            failures.add(where, f"{name} is empty or has spaces at its ends")
            continue
        if len(label) > NAV_MAX:
            failures.add(where, f"{name}, {label!r}, has {len(label)} characters, more than {NAV_MAX}")
        bad = sorted({ch for ch in label if ch in NAV_NOT})
        if bad:
            failures.add(where, f"{name}, {label!r}, holds {' '.join(bad)}; a label is plain text, without a backtick, a tilde, <, > or a double quote")
        if any((unicodedata.category(ch) in ("Cc", "Cf", "Zl", "Zp")) or (unicodedata.category(ch) == "Zs" and ch != " ") for ch in label):
            failures.add(where, f"{name} holds a control, format or invisible character; it holds plain spaces only")
        if re.match(r"^\d+\.\d+\s", label):
            failures.add(where, f"{name} starts with a section number; the site adds it")


LINK = re.compile(r"\]\(\s*<?([^)\s>]+)")


def links(body, where, failures):
    """A page links to the site's own pages: a root-relative route such as /docs/errors/U3007/,
    an anchor on the page, or an https URL that is not a file of the una-lang repositories."""
    from html import unescape

    rest = "\n".join(spans_removed(line, unescape=True) for _, line in prose_lines(body))
    targets = LINK.findall(rest) + base.REFERENCE.findall(rest) + base.URL.findall(rest)
    targets += re.findall(r"<(https?://[^>\s]+)>", rest)
    for target in targets:
        if repository_link(target):
            failures.add(where, f"{target}: links to the repositories, which change after the release; link the site's page, such as /docs/...")
            continue
        target = unescape(target).strip()
        lower = target.lower()
        if target.startswith("#") or (target.startswith("/") and not target.startswith("//")):
            continue
        if lower.startswith("mailto:"):
            continue
        if lower.startswith("http://"):
            failures.add(where, f"{target}: links use https")
        elif not lower.startswith("https://"):
            failures.add(where, f"{target}: a relative link resolves on GitHub, not on the site; use a route such as /docs/... or /learn/...")


def part_of(parts, line):
    """The name of the part that holds 1-based `line`."""
    name = None
    for heading, lines in parts:
        if lines and lines[0][0] + 1 > line:
            break
        if heading is not None:
            name = re.sub(r"^## (\d+\.\d+ )?", "", heading)
    return name


def cards(body, where, blocks, packages, failures, warnings):
    """The mistake and exercise cards, each with what it must show, and the build card."""
    parts = sections(body)
    boxes = containers(body)

    def within(box):
        return [(b, f) for b, f in blocks if box.start < b.line < (box.end or 10 ** 9)]

    build = [b for b, f in blocks if part_of(parts, b.line) == "What you'll build" and b.attrs.get("include") == "day-to-day/expected/output.txt"]
    if not build:
        failures.add(where, "`What you'll build` shows the day-to-day program's output: ```text include=\"day-to-day/expected/output.txt\"")
    for group, part, name, low_high in (("mistakes", "Common mistakes", "mistake", MISTAKES), ("exercises", "Exercises", "exercise", EXERCISES)):
        refs = sorted({ref.split("/")[1] for ref in packages if ref.startswith(group + "/")}, key=int)
        shown = [box for box in boxes if box.name == name]
        for box in shown:
            if part_of(parts, box.start) != part:
                failures.add(f"{where}:{box.start}", f"a :::{name} block goes in `{part}`")
        if len(shown) != len(refs):
            failures.add(where, f"`{part}` has {len(shown)} :::{name} blocks, but there are {len(refs)} {group}/N")
        low, high = low_high
        if len(refs) < low or (group == "exercises" and len(refs) > high):
            failures.add(where, f"{len(refs)} {group}; the template asks for {low} to {high}")
        elif len(refs) > high:
            warnings.append(f"{where}: {len(refs)} {group}; the template asks for {low} to {high}")
        for k, box in enumerate(shown, start=1):
            inside = within(box)
            mine = f"{group}/{k}"
            others = sorted({r for _, f in inside for r in refs_of(f) if r.startswith(group + "/") and not (r == mine or r.startswith(mine + "/"))})
            if others:
                failures.add(f"{where}:{box.start}", f"{name} {k} shows {others}; it shows only {mine}")
            if group == "mistakes":
                if not any(b.attrs.get("include", "").partition("#")[0] == f"{mine}/expected/rendered.txt" for b, _ in inside):
                    failures.add(f"{where}:{box.start}", f"mistake {k} shows its diagnostic: ```text include=\"{mine}/expected/rendered.txt\"")
            else:
                answers = [a for a in boxes if a.name == "answer" and box.start < a.start < (box.end or 10 ** 9)]
                if not any(f is not None and f.package.ref == f"{mine}/answer" for a in answers for _, f in within(a)):
                    failures.add(f"{where}:{box.start}", f"exercise {k} has a :::answer that shows {mine}/answer")


def check_page(root, chapter, fields, body, packages, una_path, codes, failures, warnings, scratch):
    """The page of a chapter on template 2."""
    where = f"{chapter}/README.md"
    chapter_dir = os.path.join(root, chapter)
    for key in fields:
        if key not in FRONT_MATTER + OPTIONAL_FRONT_MATTER:
            failures.add(where, f"the front matter has no field `{key}`; the fields are {list(FRONT_MATTER)}, and optionally {list(OPTIONAL_FRONT_MATTER)}")
    for key in FRONT_MATTER:
        if key not in fields:
            failures.add(where, f"the front matter has no `{key}`")
    number = str(int(chapter[:2]))
    if fields.get("learn") != number:
        failures.add(where, f"`learn` is {fields.get('learn')!r}, but its path says {number!r}")
    if not str(fields.get("time", "")).isdigit():
        failures.add(where, "`time` is the reading time in minutes, a whole number")
    prerequisites = fields.get("prerequisites", [])
    if not isinstance(prerequisites, list) or not all(p.isdigit() and 0 < int(p) < int(number) for p in prerequisites):
        failures.add(where, "`prerequisites` lists earlier chapters' numbers, such as [\"3\", \"4\"]")
    if not isinstance(fields.get("editions", []), list) or not fields.get("editions"):
        failures.add(where, "`editions` lists the editions, such as [\"0.2\"]")
    concepts = headings(fields, body, where, failures)
    nav(fields, body, number, where, failures)
    markup(body, where, failures)
    blocks = check_blocks(body, packages, chapter_dir, where, failures, una_path, scratch)
    links(body, where, failures)
    if sorted(fields.get("codes", [])) != sorted(codes):
        failures.add(where, f"`codes` is {fields.get('codes')}, but the outcomes show {sorted(codes)}")
    cards(body, where, blocks, packages, failures, warnings)
    used = {r for _, f in blocks for r in refs_of(f)}
    if "day-to-day" not in used:
        failures.add(where, "the page shows nothing of day-to-day/")
    for ref in packages:
        if ref.startswith("steps/") and ref not in used:
            warnings.append(f"{where}: nothing on the page includes {ref}")
    if concepts is not None:
        structure(body, concepts, where, failures, chapter_dir)
        check_yourself(body, concepts, where, warnings)
    anchors(body, where, failures)
    parts = sections(body)
    _, inside = fences(body)
    by_name = {}
    for heading, lines in parts:
        by_name[None if heading is None else re.sub(r"^## (\d+\.\d+ )?", "", heading)] = lines
    # For agents and Recap are subsections of the closing section, or, in a chapter not yet
    # restructured, sections of their own.
    for name, lines in subsections(by_name.get("Recap and reference", []), inside)[1:]:
        by_name.setdefault(name, lines)
    recap = sum(1 for _, line in by_name.get("Recap", []) if re.match(r"^[-*] ", line))
    if not RECAP[0] <= recap <= RECAP[1]:
        warnings.append(f"{where}: `Recap` has {recap} bullets; the template asks for {RECAP[0]} to {RECAP[1]}")
    if concepts is None:
        return
    lead = [(n, line) for n, line in parts[0][1] if not line.startswith("# ")]
    named = [("lead", lead), ("build", by_name.get("What you'll build", [])), ("why", by_name.get("Why it works this way", []))]
    for _, lines in parts[3:3 + concepts]:
        named.append(("concept", lines))
    for heading, lines in parts:
        if heading and DAY_TO_DAY in heading:
            named.append(("day-to-day", lines))
    named += [("testing", by_name.get("Testing it", [])), ("agents", by_name.get("For agents", [])),
              ("recap", by_name.get("Recap", []))]
    for name, lines in named:
        low, high = TARGETS[name]
        count = words(lines, inside)
        if not low <= count <= high:
            warnings.append(f"{where}: the part `{name}` has {count} words; the target is {low} to {high}")
    total = sum(words(lines, inside) for _, lines in parts)
    low, high = TARGETS["page"]
    if not low <= total <= high:
        warnings.append(f"{where}: {total} words of prose; the target is {low} to {high}")


def classify(root, chapter, failures):
    """(fields, body) of a chapter on template 2, or None for one on template 1. A chapter is
    on template 1 only when its README.md has no front matter and no code, it has page
    directories, and none of steps/, day-to-day/, mistakes/ or exercises/; anything else that
    is not exactly template 2 fails."""
    directory = os.path.join(root, chapter)
    readme = os.path.join(directory, "README.md")
    where = f"{chapter}/README.md"
    if os.path.islink(readme):
        failures.add(where, "a symbolic link; una-by-example holds none, and the chapter is not checked through it")
        return None
    if not os.path.isfile(readme):
        return None  # check_pages reports it
    text = base.read(readme)
    if b"\r" in base.read_bytes(readme):
        failures.add(where, "carriage returns; the pages use LF line ends")
        return None
    fields, body = padded(text)
    if text.startswith("---") and fields is None:
        failures.add(where, "its front matter does not parse: `key: value` lines between `---` lines, with no blank line")
        return None
    names = [k for k in (fields or {}) if k.strip().lower() == "template"]
    if names and (names != ["template"] or fields["template"] != TEMPLATE):
        failures.add(where, f"`template` is exactly `template: {TEMPLATE}`")
        return None
    if names:
        return fields, body
    marks = [g + "/" for g in GROUPS if os.path.exists(os.path.join(directory, g))]
    has_pages = any(base.PAGE.match(n) and os.path.isdir(os.path.join(directory, n)) for n in os.listdir(directory))
    if marks or not has_pages:
        failures.add(where, f"a chapter with {', '.join(marks) or 'no page directories'} is on template 2: its front matter says `template: {TEMPLATE}`")
        return None
    if fields is not None:
        failures.add(where, "a template 1 chapter page has no front matter")
    blocks, _ = fences(text)
    for block in blocks:
        failures.add(f"{where}:{block.line}", "a template 1 chapter page holds no code block")
    for line, why in hidden_code(text):
        failures.add(f"{where}:{line}", f"a template 1 chapter page holds no code: {why}")
    return None


def check_chapters(root, una_path, failures, scratch, warnings):
    """Every chapter, classified; every chapter on template 2 checked. Returns (chapters,
    packages, commands)."""
    counted = [0, 0, 0]
    for chapter in base.chapters(root):
        found = classify(root, chapter, failures)
        if found is None:
            continue
        fields, body = found
        counted[0] += 1
        packages = chapter_packages(os.path.join(root, chapter), chapter, failures)
        room = os.path.join(scratch, "template-2", chapter)
        codes, commands = check_packages(una_path, packages, chapter, failures, room)
        counted[1] += sum(1 for p in packages.values() if not p.reference_only)
        counted[2] += commands
        check_page(root, chapter, fields, body, packages, una_path, codes, failures, warnings, room)
    return counted


def check_translation(root, path, fields, body, english_fields, english_body, where, failures):
    """The further rules of a translation of a template 2 page: the title line with the
    translated `title`; `template`, `time`, `prerequisites` and the `## N.M` numbers kept; `nav`
    translated, by the English page's rules, when the English page has one, and absent otherwise; the
    strict markup and link rules of the English page; and the same blocks, in the same order,
    byte for byte but for `caption`, each resolving to its include, and the same containers."""
    if not is_v2(english_fields):
        if fields and any(k.strip().lower() == "template" for k in fields):
            failures.add(where, "`template` is the English page's: this one has none")
        # Code the site would render that the skeleton comparison does not see.
        for line, why in hidden_code(body):
            failures.add(f"{where}:{line}", why)
        if len(path) == 1:
            for block in fences(body)[0]:
                failures.add(f"{where}:{block.line}", "a template 1 chapter page holds no code block")
        return
    if b"\r" in base.read_bytes(os.path.join(root, *where.split("/"))):
        failures.add(where, "carriage returns; the pages use LF line ends")
    number = english_fields.get("learn", "")
    first = body.lstrip("\n").split("\n", 1)[0]
    if not fields.get("title") or first != f"# {number} {fields.get('title')}":
        failures.add(where, f"the title line must be `# {number} <title>`, with the translated `title`")
    for key in KEPT_BY_TRANSLATIONS:
        if fields.get(key) != english_fields.get(key):
            failures.add(where, f"`{key}` is {fields.get(key)!r}, but the English page's is {english_fields.get(key)!r}")

    def numbers(text):
        return [re.match(r"^## (\d+\.\d+ )?", line).group(1) for _, line in prose_lines(text) if line.startswith("## ")]

    if numbers(body) != numbers(english_body):
        failures.add(where, "its `## N.M` headings are not numbered as the English page's")
    if ("nav" in fields) != ("nav" in english_fields):
        failures.add(where, "`nav` is translated when the English page has one, and absent when it has none")
    nav(fields, body, number, where, failures)
    markup(body, where, failures)
    links(body, where, failures)
    chapter_dir = os.path.join(root, *path)
    packages = chapter_packages(chapter_dir, "/".join(path), base.Failures())
    check_blocks(body, packages, chapter_dir, where, failures)
    mine = [b.key() for b in fences(body)[0]]
    english = [b.key() for b in fences(english_body)[0]]
    if mine != english:
        failures.add(where, "its blocks are not the English page's, in the same order, byte for byte (only caption= is translated)")
    if [c.name for c in containers(body)] != [c.name for c in containers(english_body)]:
        failures.add(where, "its ::: containers are not the English page's, in the same order")


# --- Filling the blocks.

def fill_text(text, packages, chapter_dir):
    """`text` with the body of every include replaced by the included text; and the includes
    that could not be resolved, as (line, why)."""
    blocks, _ = fences(text)
    lines = text.split("\n")
    problems = []
    for block in reversed(blocks):
        if "include" not in block.attrs or not block.closed:
            continue
        found, why = resolve(block, packages, chapter_dir)
        if found is None:
            problems.append((block.line, why))
            continue
        start = block.line
        end = start + (block.body.count("\n") if block.body else 0)
        lines[start:end] = found.text.split("\n")[:-1]
    return "\n".join(lines), sorted(problems)


def fill(root):
    """Rewrites the include blocks of every template 2 page and its translations. Returns the
    files changed and the problems found. A symbolic link is never written through."""
    changed, problems = [], []
    for chapter in base.chapters(root):
        readme = os.path.join(root, chapter, "README.md")
        if not os.path.isfile(readme):
            continue
        fields, _ = base.front_matter(base.read(readme))
        if not is_v2(fields):
            continue
        packages = chapter_packages(os.path.join(root, chapter), chapter, base.Failures())
        files = [readme] + [os.path.join(root, "translations", locale, chapter, "README.md") for locale in base.LOCALES]
        for path in files:
            if not os.path.lexists(path):
                continue
            if os.path.islink(path) or any(os.path.islink(os.path.join(root, *os.path.relpath(path, root).split(os.sep)[:i]))
                                           for i in range(1, len(os.path.relpath(path, root).split(os.sep)))):
                problems.append(f"{os.path.relpath(path, root)}: a symbolic link, never written through")
                continue
            text = base.read(path)
            new, found = fill_text(text, packages, os.path.join(root, chapter))
            problems += [f"{os.path.relpath(path, root)}:{line}: {why}" for line, why in found]
            if new != text:
                with open(path, "w", encoding="utf-8") as handle:
                    handle.write(new)
                changed.append(os.path.relpath(path, root))
    return changed, problems


# --- Downloads.

def is_v2_chapter(root, chapter):
    """Whether the chapter's README.md is on template 2 (classify() checks the rest)."""
    readme = os.path.join(root, chapter, "README.md")
    return os.path.isfile(readme) and not os.path.islink(readme) and is_v2(base.front_matter(base.read(readme))[0])


def chapter_files(root, chapter):
    """What the download of a template 2 chapter holds, as {path in the chapter: source file}:
    its README.md, and every package of steps/, day-to-day/, mistakes/ and exercises/, each
    one a whole package a reader can run as it is (una.toml, verification.lock and src/). An
    overlay is resolved: its base's files, with its own over them, so base.txt is not needed.
    expected/ stays in the repository, as for a template 1 page. Symbolic links, which the
    check refuses, are never followed."""
    directory = os.path.join(root, chapter)
    out = {"README.md": os.path.join(directory, "README.md")}
    for ref, package in chapter_packages(directory, chapter, base.Failures()).items():
        if package.overlay and package.base is None:
            continue  # the check reports the overlay
        sources = {}
        if package.overlay:
            for name in base.package_files(package.base.directory):
                sources[name] = os.path.join(package.base.directory, *name.split("/"))
            for name in package.own_files():
                sources[name] = os.path.join(package.directory, *name.split("/"))
        else:
            for name in base.package_files(package.directory):
                sources[name] = os.path.join(package.directory, *name.split("/"))
        for name, source in sources.items():
            if name != "README.md" and not os.path.islink(source):
                out[f"{ref}/{name}"] = source
    return dict(sorted(out.items()))
