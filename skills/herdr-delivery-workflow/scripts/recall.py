#!/usr/bin/env python3
"""Recall indexed Herdr project records or read a cited line span."""

import argparse
import datetime
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


LESSON_FIELDS = {
    "id",
    "added",
    "source_run",
    "approved_by",
    "status",
    "last_used",
}
LESSON_STATUSES = {"active", "failure-mode", "rejected"}


def lesson_record_lines(text):
    lines = text.splitlines(keepends=True)
    if not lines:
        return None
    start = 0
    if lines[0].rstrip("\r\n") != "---":
        if not re.fullmatch(r"<!--[\s\S]*-->\r?\n?", lines[0]):
            return None
        start = 1
    if start >= len(lines) or lines[start].rstrip("\r\n") != "---":
        return None
    end = next(
        (index for index, line in enumerate(lines[start + 1 :], start=start + 1) if line.rstrip("\r\n") == "---"),
        None,
    )
    if end is None:
        return None

    fields = {}
    for index, line in enumerate(lines[start + 1 : end], start=start + 1):
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):[ \t]*(.*?)(?:\r?\n)?", line)
        if match is None or match.group(1) in fields:
            return None
        fields[match.group(1)] = (index, match.group(2))
    if set(fields) != LESSON_FIELDS or fields["status"][1] not in LESSON_STATUSES:
        return None
    if any(not value for _index, value in fields.values()):
        return None
    try:
        datetime.date.fromisoformat(fields["added"][1])
        datetime.date.fromisoformat(fields["last_used"][1])
    except ValueError:
        return None
    return lines, end, fields


def stamp_lesson(path, today):
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        parsed = lesson_record_lines(text)
        if parsed is None:
            return
        lines, _end, fields = parsed
        line_index = fields["last_used"][0]
        newline = "\r\n" if lines[line_index].endswith("\r\n") else "\n"
        replacement = f"last_used: {today}{newline}"
        if lines[line_index] == replacement:
            return
        lines[line_index] = replacement
        with open(path, "w", encoding="utf-8", newline="") as handle:
            handle.write("".join(lines))
    except (OSError, UnicodeError):
        return


def lesson_result_path(relative):
    parts = os.path.normpath(relative).split(os.sep)
    if "lessons" not in parts or parts[-1] in {"", ".", ".."}:
        return None
    root = os.path.realpath(os.path.abspath(PROJECTS_ROOT))
    path = os.path.realpath(os.path.join(root, relative))
    try:
        inside_root = os.path.commonpath((root, path)) == root
    except ValueError:
        inside_root = False
    if not inside_root:
        return None
    return path


def stamp_results(results):
    today = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    stamped = set()
    for (relative, _line), _score in results:
        path = lesson_result_path(relative)
        if path is None or path in stamped:
            continue
        stamped.add(path)
        stamp_lesson(path, today)


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
    parser.add_argument("--stamp", action="store_true")
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
    if args.stamp:
        stamp_results(results[: args.n])
    for (path, line), _score in results[: args.n]:
        print(f"{path}:{line}  {snippets[(path, line)]}")
    db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
