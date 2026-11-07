"""The lesson record schema: frontmatter fields, statuses, the parser, and the stale window."""
import datetime
import re
from dataclasses import dataclass

LESSON_FIELDS = {
    "id",
    "added",
    "source_run",
    "approved_by",
    "status",
    "last_used",
}
LESSON_STATUSES = ("active", "failure-mode", "rejected", "superseded")
STALE_DAYS = 90


class LessonParseError(ValueError):
    pass


@dataclass
class LessonRecord:
    lines: list[str]
    end: int
    fields: dict[str, tuple[int, str]]


def lesson_record_lines(text):
    lines = text.splitlines(keepends=True)
    if not lines:
        raise LessonParseError("file is empty")

    start = 0
    if lines[0].rstrip("\r\n") != "---":
        if not re.fullmatch(r"<!--[\s\S]*-->", lines[0].rstrip("\r\n")):
            raise LessonParseError("missing frontmatter opening delimiter")
        start = 1
    if start >= len(lines) or lines[start].rstrip("\r\n") != "---":
        raise LessonParseError("missing frontmatter opening delimiter")

    end = next(
        (
            index
            for index, line in enumerate(lines[start + 1 :], start=start + 1)
            if line.rstrip("\r\n") == "---"
        ),
        None,
    )
    if end is None:
        raise LessonParseError("missing frontmatter closing delimiter")

    fields = {}
    for index, line in enumerate(lines[start + 1 : end], start=start + 1):
        match = re.fullmatch(
            r"([A-Za-z_][A-Za-z0-9_-]*):[ \t]*(.*?)(?:\r?\n)?", line
        )
        if match is None:
            raise LessonParseError(f"invalid frontmatter line {index + 1}")
        name, value = match.groups()
        if name in fields:
            raise LessonParseError(f"duplicate field: {name}")
        fields[name] = (index, value)

    missing = LESSON_FIELDS - set(fields)
    if missing:
        raise LessonParseError(f"missing field: {sorted(missing)[0]}")
    unexpected = set(fields) - LESSON_FIELDS - {"superseded_by"}
    if unexpected:
        raise LessonParseError(f"unexpected field: {sorted(unexpected)[0]}")

    status = fields["status"][1]
    if status not in LESSON_STATUSES:
        raise LessonParseError(f"invalid status: {status}")
    has_landing = "superseded_by" in fields
    if status == "superseded" and not has_landing:
        raise LessonParseError("superseded lesson is missing superseded_by")
    if status != "superseded" and has_landing:
        raise LessonParseError("superseded_by is valid only for superseded lessons")
    for name, (_index, value) in fields.items():
        if not value:
            raise LessonParseError(f"empty field: {name}")

    try:
        datetime.date.fromisoformat(fields["added"][1])
        datetime.date.fromisoformat(fields["last_used"][1])
    except ValueError as exc:
        raise LessonParseError("added and last_used must be ISO dates") from exc
    return LessonRecord(lines, end, fields)
