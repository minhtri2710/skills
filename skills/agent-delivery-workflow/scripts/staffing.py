#!/usr/bin/env python3
"""Staffing-record grammar: seat lines, key=value fields and owned-path globs."""
from __future__ import annotations

import re
from pathlib import Path
from typing import NamedTuple

PEER_DISPOSITIONS = ("Engineer", "Reviewer", "Architect")
STAFFED_SEAT_RE = re.compile(
    r"^[ \t]*(" + "|".join(PEER_DISPOSITIONS) + r"):(.*)$", re.IGNORECASE | re.MULTILINE
)
_FIELD = r"(?:^|\s)([a-z][a-z-]*)=(\S*)"
GLOB_TOKEN_RE = re.compile(r"\*\*/|\*\*|\*|\?|[^*?]+")


class StaffedSeat(NamedTuple):
    role: str  # ENGINEER, REVIEWER or ARCHITECT
    name: str
    fields: dict[str, str]  # lowercase key -> value, first occurrence
    line: str


def fields_of(text: str) -> dict[str, str]:
    """The `key=value` tokens of a staffing-record line, keys lowercased, the first occurrence of a key kept."""
    fields: dict[str, str] = {}
    for key, value in re.findall(_FIELD, text, re.IGNORECASE):
        fields.setdefault(key.lower(), value)
    return fields


def staffed_seats(text: str) -> list[StaffedSeat]:
    """Every ENGINEER, REVIEWER and ARCHITECT line of a staffing record, in order."""
    return [
        StaffedSeat(match.group(1).upper(), (match.group(2).split() or [""])[0],
                    fields_of(match.group(2)), match.group(0))
        for match in STAFFED_SEAT_RE.finditer(text)
    ]


def _glob_re(entry: str) -> re.Pattern[str]:
    parts = {"**/": "(?:.*/)?", "**": ".*", "*": "[^/]*", "?": "[^/]"}
    return re.compile("".join(parts.get(token, re.escape(token)) for token in GLOB_TOKEN_RE.findall(entry)))


def _owns(entry: str, path: str) -> bool:
    return (entry == path or path.startswith(entry.rstrip("/") + "/")
            or _glob_re(entry).fullmatch(path) is not None)


def scope_authors(staffing: Path, lead: str, paths: list[str]) -> tuple[str, list[str]]:
    text = staffing.read_text(encoding="utf-8")
    mode = re.search(r"^MODE: (\S+)", text, re.MULTILINE)
    if mode is None or mode.group(1) not in ("solo-Lead", "partitioned"):
        raise ValueError(f"{staffing} has no MODE: solo-Lead or MODE: partitioned line")
    if mode.group(1) == "solo-Lead":
        line = re.search(r"^LEAD: (.*)$", text, re.MULTILINE)
        if line is None:
            raise ValueError(f"{staffing} has no LEAD line")
        fields = fields_of(line.group(1))
        if not fields.get("kind") or not fields.get("model"):
            raise ValueError(f"{staffing} LEAD line lacks kind= or model=")
        return "solo-Lead", [f"{lead} ({fields.get('kind')} {fields.get('model')})"]
    engineers = [(seat.name, seat.fields) for seat in staffed_seats(text) if seat.role == "ENGINEER"]
    authors: dict[str, None] = {}
    for path in paths:
        owners = [(name, fields) for name, fields in engineers
                  if any(_owns(entry, path) for entry in fields.get("owned", "").split(",") if entry)]
        if not owners:
            raise ValueError(f"{path} has no ENGINEER owner in {staffing}")
        authors.update((f"{name} ({fields.get('kind')} {fields.get('model')})", None) for name, fields in owners)
    return "partitioned", list(authors)
