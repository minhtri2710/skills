#!/usr/bin/env python3
"""Recall indexed project records or read a cited line span."""

import argparse
import datetime
import glob
import os
import re
import sqlite3
import sys
import tempfile
import unicodedata

import state_root
from lessons import LessonParseError, lesson_record_lines

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


def index_root(parser, project):
    if project is None:
        return os.path.abspath(state_root.STATE_ROOT)
    try:
        return str(state_root.project_dir(project))
    except ValueError:
        parser.error("--project must be a project slug")


def build_index(index_root):
    db = sqlite3.connect(":memory:")
    db.execute(
        "create virtual table r using fts5(path, line, text, tokenize='unicode61 remove_diacritics 2')"
    )
    root = os.path.abspath(state_root.STATE_ROOT)
    for path in glob.glob(os.path.join(index_root, "**", "*.md"), recursive=True):
        with open(path, encoding="utf-8", errors="ignore") as handle:
            lines = handle.read().splitlines()
        relative = os.path.relpath(path, root)
        for start in range(0, len(lines), 8):
            chunk = "\n".join(lines[start : start + 8]).strip()
            if chunk:
                db.execute("insert into r values(?,?,?)", (relative, start + 1, fold(chunk)))
    db.commit()
    return db


def query_records(db, variants):
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
            if os.path.basename(path) == state_root.INDEX:
                scores[key] += INDEX_BONUS
            snippets.setdefault(key, snippet)
    return sorted(scores.items(), key=lambda item: (-item[1], item[0][0], item[0][1])), snippets


def stamp_lesson(path, today):
    temporary_path = None
    descriptor = None
    try:
        with open(path, "rb") as handle:
            original = handle.read()
        record = lesson_record_lines(original.decode("utf-8"))
        if record.fields["status"][1] == "superseded":
            return
        line_index = record.fields["last_used"][0]
        newline = "\r\n" if record.lines[line_index].endswith("\r\n") else "\n"
        replacement = f"last_used: {today}{newline}"
        if record.lines[line_index] == replacement:
            return
        record.lines[line_index] = replacement
        updated = "".join(record.lines).encode("utf-8")

        directory = os.path.dirname(path) or "."
        descriptor, temporary_path = tempfile.mkstemp(
            prefix=f".{os.path.basename(path)}.", dir=directory
        )
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = None
            handle.write(updated)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
        temporary_path = None
    except (OSError, UnicodeError, LessonParseError):
        return
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except OSError:
                pass


def lesson_result_path(relative):
    parts = os.path.normpath(relative).split(os.sep)
    if state_root.LESSONS not in parts or parts[-1] in {"", ".", ".."}:
        return None
    path = os.path.realpath(os.path.join(state_root.STATE_ROOT, relative))
    return path if state_root.inside_state_root(path) else None


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
    target = os.path.realpath(os.path.join(state_root.STATE_ROOT, path))
    if not state_root.inside_state_root(target) or not os.path.isfile(target):
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

    root = index_root(parser, args.project)
    if args.get is not None:
        target, start, count = span_target(parser, args.get)
        with open(target, encoding="utf-8", errors="ignore") as handle:
            lines = handle.read().splitlines(keepends=True)
        sys.stdout.write("".join(lines[start - 1 : start - 1 + count]))
        return 0

    db = build_index(root)
    results, snippets = query_records(db, args.variants)
    if args.stamp:
        stamp_results(results[: args.n])
    for (path, line), _score in results[: args.n]:
        print(f"{path}:{line}  {snippets[(path, line)]}")
    db.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
