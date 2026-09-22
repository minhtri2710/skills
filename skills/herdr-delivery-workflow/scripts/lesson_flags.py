#!/usr/bin/env python3
"""Report superseded and stale Herdr lesson records for Human review."""

import argparse
import datetime
import os
import sys

from recall import LESSON_STATUSES, LessonParseError, lesson_record_lines

PROJECTS_ROOT = os.path.expanduser("~/.herdr/projects")
STATUSES = LESSON_STATUSES


def project_root(parser, project):
    if (
        not project
        or project in (".", "..")
        or os.path.isabs(project)
        or os.path.basename(project) != project
    ):
        parser.error("--project must be a project slug")
    return os.path.join(os.path.abspath(PROJECTS_ROOT), project)


def record_fields(path):
    with open(path, encoding="utf-8") as handle:
        record = lesson_record_lines(handle.read())
    fields = {name: value for name, (_index, value) in record.fields.items()}
    return fields, datetime.date.fromisoformat(fields["last_used"])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, metavar="SLUG")
    parser.add_argument("--days", type=int, default=90, metavar="N")
    args = parser.parse_args(argv)
    if args.days < 1:
        parser.error("--days must be positive")

    lessons = os.path.join(project_root(parser, args.project), "runs", "coordination", "lessons")
    if not os.path.isdir(lessons):
        print("Nothing to flag: lessons directory does not exist.")
        return 0

    cutoff = datetime.datetime.now(datetime.timezone.utc).date() - datetime.timedelta(days=args.days)
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
