#!/usr/bin/env python3
"""Recall indexed Herdr project records or read a cited line span."""

import argparse
import glob
import os
import re
import sqlite3
import sys
import unicodedata

PROJECTS_ROOT = os.path.expanduser("~/.herdr/projects")
STOP = set(
    "the did what why about was were how when who does not have has with of and is are to for in on at it this that vi sao khong duoc toi la va cua".split()
)
INDEX_BONUS = 1e-6


def fold(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    ).lower()


def terms(variant):
    return [word for word in re.findall(r"\w+", fold(variant)) if len(word) > 1 and word not in STOP]


def project_root(parser, project):
    root = os.path.abspath(PROJECTS_ROOT)
    if project is not None:
        if (
            not project
            or project in (".", "..")
            or os.path.isabs(project)
            or os.path.basename(project) != project
        ):
            parser.error("--project must be a project slug")
        return os.path.join(root, project)
    return root


def build_index(index_root):
    db = sqlite3.connect(":memory:")
    db.execute(
        "create virtual table r using fts5(path, line, text, tokenize='unicode61 remove_diacritics 2')"
    )
    root = os.path.abspath(PROJECTS_ROOT)
    for path in glob.glob(os.path.join(index_root, "**", "*.md"), recursive=True):
        with open(path, errors="ignore") as handle:
            lines = handle.read().splitlines()
        relative = os.path.relpath(path, root)
        for start in range(0, len(lines), 8):
            chunk = "\n".join(lines[start : start + 8]).strip()
            if chunk:
                db.execute("insert into r values(?,?,?)", (relative, start + 1, fold(chunk)))
    db.commit()
    return db


def query_records(db, variants, count):
    scores = {}
    snippets = {}
    for variant in variants:
        query_terms = terms(variant)
        if not query_terms:
            continue
        query = " OR ".join('"' + term.replace('"', '""') + '"' for term in query_terms)
        rows = db.execute(
            "select path,line,snippet(r,2,'[',']','…',14) "
            "from r where r match ? order by bm25(r) limit 10",
            (query,),
        ).fetchall()
        for rank, (path, line, snippet) in enumerate(rows):
            key = (path, line)
            scores[key] = scores.get(key, 0) + 1 / (60 + rank)
            if os.path.basename(path) == "INDEX.md":
                scores[key] += INDEX_BONUS
            snippets.setdefault(key, snippet)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0][0], item[0][1])), snippets


def span_target(parser, spec):
    try:
        path, start, count = spec.rsplit(":", 2)
        start = int(start)
        count = int(count)
    except (AttributeError, ValueError):
        parser.error("--get must be PATH:FROM:COUNT")
    if not path or os.path.isabs(path) or start < 1 or count < 1:
        parser.error("--get must use a relative path and positive FROM and COUNT")
    root = os.path.realpath(os.path.abspath(PROJECTS_ROOT))
    target = os.path.realpath(os.path.join(root, path))
    try:
        inside = os.path.commonpath((root, target)) == root
    except ValueError:
        inside = False
    if not inside or target == root or not os.path.isfile(target):
        parser.error("--get path must name a file under the projects root")
    return target, start, count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", metavar="SLUG")
    parser.add_argument("-n", type=int, default=3, metavar="N")
    parser.add_argument("--get", metavar="PATH:FROM:COUNT")
    parser.add_argument("variants", nargs="*", metavar="VARIANT")
    args = parser.parse_args(argv)
    if args.n < 1:
        parser.error("-n must be positive")
    if args.get is not None and args.variants:
        parser.error("--get and query variants are mutually exclusive")
    if args.get is None and len(args.variants) < 2:
        parser.error("query mode requires at least two variants")

    root = project_root(parser, args.project)
    if args.get is not None:
        target, start, count = span_target(parser, args.get)
        with open(target, errors="ignore") as handle:
            lines = handle.read().splitlines(keepends=True)
        sys.stdout.write("".join(lines[start - 1 : start - 1 + count]))
        return 0

    db = build_index(root)
    results, snippets = query_records(db, args.variants, args.n)
    for (path, line), _score in results[: args.n]:
        print(f"{path}:{line}  {snippets[(path, line)]}")
    db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
