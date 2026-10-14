#!/usr/bin/env python3
"""Builds the download archives of Una by Example into OUT.

- One archive per page, `NN-MM-page.tar.gz` (`01-01-package.tar.gz`), holding only the package a
  reader runs: `NN-MM-page/README.md`, `una.toml`, `verification.lock` and `src/`.
- One archive of everything, `una-by-example-<version>.tar.gz`, with the root's README.md,
  LICENSE and una.lock, and every chapter's page and packages, under
  `una-by-example-<version>/`.
- `SHA256SUMS`, one line per archive.

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

from check import ROOT, lock_version, package_files, pages  # noqa: E402


def entries_of(root, chapter, page):
    """The package files of a page, as (path under the root, path in the archive)."""
    directory = os.path.join(root, chapter, page)
    return [(os.path.join(directory, name), name) for name in package_files(directory)]


def tar_gz(path, prefix, files, mtime):
    """Writes `files`, (source, name) pairs, under `prefix/` into a reproducible `path`."""
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
    chapters_seen = set()
    for chapter, page in pages(root):
        if chapter not in chapters_seen:
            chapters_seen.add(chapter)
            everything.append((os.path.join(root, chapter, "README.md"), f"{chapter}/README.md"))
        files = entries_of(root, chapter, page)
        name = f"{chapter[:2]}-{page}"
        tar_gz(os.path.join(out, f"{name}.tar.gz"), name, files, mtime)
        names.append(f"{name}.tar.gz")
        everything.extend((source, f"{chapter}/{page}/{inner}") for source, inner in files)
    version = lock_version(root)
    whole = f"una-by-example-{version}"
    tar_gz(os.path.join(out, f"{whole}.tar.gz"), whole, everything, mtime)
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
    names = build(ROOT, argv[0], commit_time(ROOT))
    print(f"archive.py: {len(names)} archives in {argv[0]}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
