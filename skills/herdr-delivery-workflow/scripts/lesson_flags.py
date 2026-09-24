#!/usr/bin/env python3
"""Report superseded and stale Herdr lesson records, or unprovenanced and stale RATIONALE.md entries, for Human review."""

import argparse
import datetime
import os
import re
import sys

from recall import LESSON_STATUSES, LessonParseError, lesson_record_lines, project_root

STATUSES = LESSON_STATUSES
RATIONALE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references", "RATIONALE.md"
)
TAG = re.compile(r"Origin: (?P<ref>[^;]+); (?P<origin>\S+)\. Confirmed: (?P<confirmed>\S+)\.$")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")


def record_fields(path):
    with open(path, encoding="utf-8") as handle:
        record = lesson_record_lines(handle.read())
    fields = {name: value for name, (_index, value) in record.fields.items()}
    return fields, datetime.date.fromisoformat(fields["last_used"])


def rationale_entries(text):
    """Yield (section, title, text) per top-level bullet, or per bullet-less section."""
    section = None
    body = []

    def close():
        if section is None:
            return []
        bullets = [line for line in body if line.startswith("- **")]
        if bullets:
            return [(section, line[4:].split("**", 1)[0].rstrip("."), line) for line in bullets]
        paragraphs = [line for line in body if line.strip()]
        return [(section, section, paragraphs[-1] if paragraphs else "")]

    entries = []
    for line in text.splitlines():
        if line.startswith("## "):
            entries += close()
            section, body = line[3:].strip(), []
        elif section is not None:
            body.append(line)
    return entries + close()


def tag_problem(text, cutoff):
    """Return (malformed_reason, review_reason); at most one is set."""
    if "Origin:" not in text:
        return "missing provenance tag", None
    match = TAG.search(text)
    if not match:
        return "malformed provenance tag", None
    dates = {}
    for name in ("origin", "confirmed"):
        value = match.group(name)
        try:
            if not DATE.fullmatch(value):
                raise ValueError
            dates[name] = datetime.date.fromisoformat(value)
        except ValueError:
            return f"bad {name} date: {value}", None
    if match.group("ref").strip() == "unknown":
        return None, "origin unknown"
    if dates["confirmed"] < cutoff:
        return None, f"confirmed {dates['confirmed'].isoformat()}"
    return None, None


def rationale_report(cutoff):
    with open(RATIONALE_PATH, encoding="utf-8") as handle:
        entries = rationale_entries(handle.read())
    flagged = []
    malformed = []
    for section, title, text in entries:
        bad, review = tag_problem(text, cutoff)
        if bad:
            malformed.append(f"malformed: {section} / {title}: {bad}")
        elif review:
            flagged.append(f"- {section} / {title} ({review}) — review candidate for Human review")
    for line in malformed:
        print(line)
    if not flagged:
        if malformed:
            return 1
        print("Nothing to flag: every rationale entry has a known, recently confirmed origin.")
        return 0
    print(f"Review candidates — origin unknown, or confirmed before {cutoff.isoformat()}:")
    for line in flagged:
        print(line)
    return 1 if malformed else 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--project", metavar="SLUG")
    mode.add_argument("--rationale", action="store_true")
    parser.add_argument("--days", type=int, default=90, metavar="N")
    args = parser.parse_args(argv)
    if args.days < 1:
        parser.error("--days must be positive")
    cutoff = datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=args.days)
    if args.rationale:
        return rationale_report(cutoff)

    lessons = os.path.join(project_root(parser, args.project), "runs", "coordination", "lessons")
    if not os.path.isdir(lessons):
        print("Nothing to flag: lessons directory does not exist.")
        return 0

    flagged = []
    malformed = []
    for root, _dirs, files in os.walk(lessons):
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            try:
                fields, last_used = record_fields(path)
            except (OSError, UnicodeError, LessonParseError) as exc:
                malformed.append((path, str(exc)))
                continue
            # A superseded lesson is replaced doctrine; surface it for retirement
            # regardless of staleness. A freshly-used superseded record is the
            # dangerous case — a seat still recalling doctrine that has been
            # replaced — so it must show up even when last_used is recent.
            if last_used < cutoff or fields["status"] == "superseded":
                flagged.append((fields["status"], os.path.relpath(path, lessons), fields["last_used"]))

    for path, reason in malformed:
        print(f"malformed: {path}: {reason}")
    if not flagged:
        if malformed:
            return 1
        print("Nothing to flag: no superseded or stale lessons.")
        return 0
    print(f"Retire candidates — superseded, or stale (last_used before {cutoff.isoformat()}):")
    for status in STATUSES:
        status_records = [item for item in flagged if item[0] == status]
        if not status_records:
            continue
        print(f"[{status}]")
        for _status, relative, last_used in status_records:
            print(f"- {relative} (last_used: {last_used}) — retire candidate for Human review")
    return 1 if malformed else 0


if __name__ == "__main__":
    sys.exit(main())
