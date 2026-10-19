#!/usr/bin/env python3
"""Builds the download archives of Una by Example into OUT.

- One archive per page of a template 1 chapter, `NN-MM-page.tar.gz` (`01-01-package.tar.gz`),
  holding only the package a reader runs: `NN-MM-page/README.md`, `una.toml`,
  `verification.lock` and `src/`, or from edition 0.4 `ita.una`, `ita.lock`, `src/` and the
  path dependencies under `deps/`.
- One archive per template 2 chapter, `NN-chapter.tar.gz` (`06-failure.tar.gz`), holding
  `NN-chapter/README.md` and every package of the chapter (steps/, day-to-day/, mistakes/N/,
  exercises/N/start/, answer/ and the others), each a whole package that runs as it is: an
  overlay is resolved into its base's files with its own over them (template2.chapter_files).
- One archive of everything, `una-by-example-<version>.tar.gz`, with the root's README.md,
  LICENSE and una.lock, every chapter's README.md, and every page's and chapter's packages as
  in the archives above, under `una-by-example-<version>/`.
- `SHA256SUMS`, one line per archive.

No symbolic link is archived or followed: a link anywhere on the path of a file to archive,
a file or a directory such as a linked `src/`, stops the build with an error naming it (the
check refuses such a tree too).

The archives are reproducible: entries sorted, every mtime the commit's time (or
SOURCE_DATE_EPOCH), owner and group 0:0 with no names, modes 0644 and 0755, and gzip without a
name or a time. Two builds of one commit give the same bytes. Standard library only.

Usage: archive.py OUT
"""

import sys

# check.py is imported below; nothing writes bytecode into the repository.
sys.dont_write_bytecode = True

import gzip  # noqa: E402
import hashlib  # noqa: E402
import io  # noqa: E402
import os  # noqa: E402
import subprocess  # noqa: E402
import tarfile  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from check import ROOT, chapters, lock_version, package_files, pages  # noqa: E402
import template2  # noqa: E402


def entries_of(root, chapter, page):
    """The package files of a page, as (path under the root, path in the archive)."""
    directory = os.path.join(root, chapter, page)
    return [(os.path.join(directory, name), name) for name in package_files(directory)]


class LinkError(Exception):
    """A symbolic link on the path of a file to archive."""


def plain_source(root, source):
    """Raises LinkError when `source`, or a directory between `root` and it, is a symbolic link."""
    relative = os.path.relpath(source, root)
    if relative.startswith(".."):
        raise LinkError(f"{source} is outside {root}")
    path = root
    for part in relative.split(os.sep):
        path = os.path.join(path, part)
        if os.path.islink(path):
            raise LinkError(f"{os.path.relpath(path, root)} is a symbolic link; archive.py never follows one")


def refuse_links(root, directory):
    """Raises LinkError for the first symbolic link under `directory`, file or directory."""
    if os.path.islink(directory):
        raise LinkError(f"{os.path.relpath(directory, root)} is a symbolic link; archive.py never follows one")
    for base, dirs, files in os.walk(directory):
        dirs.sort()
        for name in sorted(dirs + files):
            if os.path.islink(os.path.join(base, name)):
                raise LinkError(f"{os.path.relpath(os.path.join(base, name), root)} is a symbolic link; archive.py never follows one")


def tar_gz(path, prefix, files, mtime, root=None):
    """Writes `files`, (source, name) pairs, under `prefix/` into a reproducible `path`. With
    `root`, every source is checked by `plain_source` first."""
    if root is not None:
        for source, _ in files:
            plain_source(root, source)
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.PAX_FORMAT) as archive:
        directories = set()
        for _, name in files:
            parts = name.split("/")[:-1]
            for depth in range(1, len(parts) + 1):
                directories.add("/".join(parts[:depth]))
        items = [(None, d) for d in directories] + list(files)
        items.sort(key=lambda item: item[1])
        top = tarfile.TarInfo(prefix)
        top.type, top.mode, top.mtime = tarfile.DIRTYPE, 0o755, mtime
        archive.addfile(top)
        for source, name in items:
            info = tarfile.TarInfo(f"{prefix}/{name}")
            info.mtime, info.uid, info.gid, info.uname, info.gname = mtime, 0, 0, "", ""
            if source is None:
                info.type, info.mode = tarfile.DIRTYPE, 0o755
                archive.addfile(info)
                continue
            with open(source, "rb") as handle:
                data = handle.read()
            info.size, info.mode = len(data), 0o644
            archive.addfile(info, io.BytesIO(data))
    with open(path, "wb") as out:
        with gzip.GzipFile(filename="", mode="wb", fileobj=out, mtime=0, compresslevel=9) as zipped:
            zipped.write(raw.getvalue())


def build(root, out, mtime):
    """Builds every archive of `root` into `out`; returns their names."""
    os.makedirs(out, exist_ok=True)
    names = []
    everything = []
    for name in ("README.md", "LICENSE", "una.lock"):
        if os.path.isfile(os.path.join(root, name)):
            everything.append((os.path.join(root, name), name))
    for chapter in chapters(root):
        refuse_links(root, os.path.join(root, chapter))
    for chapter in chapters(root):
        if os.path.isfile(os.path.join(root, chapter, "README.md")):
            everything.append((os.path.join(root, chapter, "README.md"), f"{chapter}/README.md"))
        if not template2.is_v2_chapter(root, chapter):
            continue
        files = [(source, name) for name, source in template2.chapter_files(root, chapter).items()]
        tar_gz(os.path.join(out, f"{chapter}.tar.gz"), chapter, files, mtime, root)
        names.append(f"{chapter}.tar.gz")
        everything.extend((source, f"{chapter}/{name}") for source, name in files if name != "README.md")
    for chapter, page in pages(root):
        if template2.is_v2_chapter(root, chapter):
            continue  # a template 2 chapter has no pages; the check fails any it holds
        files = entries_of(root, chapter, page)
        name = f"{chapter[:2]}-{page}"
        tar_gz(os.path.join(out, f"{name}.tar.gz"), name, files, mtime, root)
        names.append(f"{name}.tar.gz")
        everything.extend((source, f"{chapter}/{page}/{inner}") for source, inner in files)
    version = lock_version(root)
    whole = f"una-by-example-{version}"
    tar_gz(os.path.join(out, f"{whole}.tar.gz"), whole, everything, mtime, root)
    names.append(f"{whole}.tar.gz")
    with open(os.path.join(out, "SHA256SUMS"), "w", encoding="ascii") as sums:
        for name in sorted(names):
            with open(os.path.join(out, name), "rb") as handle:
                sums.write(f"{hashlib.sha256(handle.read()).hexdigest()}  {name}\n")
    return names


def commit_time(root):
    if "SOURCE_DATE_EPOCH" in os.environ:
        return int(os.environ["SOURCE_DATE_EPOCH"])
    result = subprocess.run(
        ["git", "log", "-1", "--format=%ct"], cwd=root, capture_output=True, text=True, check=True
    )
    return int(result.stdout.strip())


def main(argv):
    if len(argv) != 1:
        print(__doc__, file=sys.stderr)
        return 2
    try:
        names = build(ROOT, argv[0], commit_time(ROOT))
    except LinkError as error:
        print(f"archive.py: {error}", file=sys.stderr)
        return 1
    print(f"archive.py: {len(names)} archives in {argv[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
