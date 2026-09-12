#!/usr/bin/env python3
"""Report stale Herdr lesson records for Human review."""

import argparse
import datetime
import os
import re
import sys

PROJECTS_ROOT = os.path.expanduser("~/.herdr/projects")
STATUSES = ("active", "failure-mode", "rejected")


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
    try:
        with open(path, encoding="utf-8") as handle:
            lines = handle.read().splitlines()
    except (OSError, UnicodeError):
        return None
    if not lines:
        return None
    start = 0
    if lines[0] != "---":
        if not re.fullmatch(r"<!--[\s\S]*-->", lines[0]):
            return None
        start = 1
    if start >= len(lines) or lines[start] != "---":
        return None
    try:
        end = lines.index("---", start + 1)
    except ValueError:
        return None
    fields = {}
    for line in lines[start + 1 : end]:
        match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):[ \t]*(.*)", line)
        if match is None or match.group(1) in fields:
            return None
        fields[match.group(1)] = match.group(2)
    if set(fields) != {"id", "added", "source_run", "approved_by", "status", "last_used"}:
        return None
    if fields["status"] not in STATUSES:
        return None
    try:
        last_used = datetime.date.fromisoformat(fields["last_used"])
    except ValueError:
        return None
    return fields, last_used


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
    for root, _dirs, files in os.walk(lessons):
        for name in sorted(files):
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            parsed = record_fields(path)
            if parsed is None:
                continue
            fields, last_used = parsed
            if last_used < cutoff:
                flagged.append((fields["status"], os.path.relpath(path, lessons), fields["last_used"]))

    if not flagged:
        print("Nothing to flag: no stale lessons.")
        return 0
    print(f"Stale lesson candidates (last_used before {cutoff.isoformat()}):")
    for status in STATUSES:
        status_records = [item for item in flagged if item[0] == status]
        if not status_records:
            continue
        print(f"[{status}]")
        for _status, relative, last_used in status_records:
            print(f"- {relative} (last_used: {last_used}) — retire candidate for Human review")
    return 0


if __name__ == "__main__":
    sys.exit(main())
