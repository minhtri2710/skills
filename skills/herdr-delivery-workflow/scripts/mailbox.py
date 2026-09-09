#!/usr/bin/env python3
"""Select entries from an append-only Supervisor mailbox."""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

HEADER_RE = re.compile(
    r"^## [^|\r\n]+ -> [^|\r\n]+ \| "
    r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}"
    r"(?::[0-9]{2}(?:\.[0-9]+)?)?Z) \|"
)
ISO_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}"
    r"(?::[0-9]{2}(?:\.[0-9]+)?)?Z"
)


@dataclass(frozen=True)
class Entry:
    header: str
    timestamp: str
    body: str


def _entries(text: str) -> list[Entry]:
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if HEADER_RE.match(line)]
    entries = []
    for number, start in enumerate(starts):
        end = starts[number + 1] if number + 1 < len(starts) else len(lines)
        header = lines[start]
        match = HEADER_RE.match(header)
        assert match is not None
        body_lines = lines[start + 1:end]
        if body_lines and body_lines[-1] == "---":
            body_lines = body_lines[:-1]
        entries.append(Entry(header, match.group(1), "\n".join(body_lines)))
    return entries


def select_entries(
    text: str,
    *,
    since: str | None = None,
    last: int | None = None,
    headers: bool = False,
) -> list[str]:
    """Select mailbox entries, optionally returning only their headers."""
    if since is not None and last is not None:
        raise ValueError("since and last are mutually exclusive")
    entries = _entries(text)
    if since is not None:
        if ISO_RE.fullmatch(since) is None:
            raise ValueError("since must be an ISO-8601 UTC timestamp ending in Z")
        # UTC ISO-8601 Z timestamps sort correctly lexicographically.
        entries = [entry for entry in entries if entry.timestamp > since]
    elif last is not None:
        if last < 0:
            raise ValueError("last must be non-negative")
        entries = entries[-last:] if last else []
    if headers:
        return [entry.header for entry in entries]
    return ["\n".join((entry.header, entry.body)) for entry in entries]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="select Supervisor mailbox entries")
    parser.add_argument("--file", required=True, metavar="PATH", help="mailbox file")
    selectors = parser.add_mutually_exclusive_group()
    selectors.add_argument("--since", metavar="ISO")
    selectors.add_argument("--last", metavar="N", type=int)
    parser.add_argument("--headers", action="store_true")
    args = parser.parse_args(argv)

    try:
        if args.since is None and args.last is None and not args.headers:
            raise ValueError("at least one of --headers, --since, or --last is required")
        text = Path(args.file).read_text(encoding="utf-8")
        output = select_entries(text, since=args.since, last=args.last, headers=args.headers)
    except (OSError, ValueError) as exc:
        print(f"mailbox: {exc}", file=sys.stderr)
        return 1

    if output:
        print(("\n" if args.headers else "\n\n").join(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
