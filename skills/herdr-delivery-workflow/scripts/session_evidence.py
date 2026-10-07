#!/usr/bin/env python3
"""Locate paired events in one bounded Pi JSONL range; never judge their result."""
from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from dataclasses import dataclass, field
from pathlib import Path

MAX_LINE_NUMBER = 1_000_000
MAX_RANGE_LINES = 1_000
MAX_LINE_BYTES = 1_048_576
MAX_SELECTED_BYTES = 16 * 1_048_576
MAX_START_BYTE = 2**63 - 1
MAX_EVENTS = 2_000
ID_PATTERN = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")
LINE_ARGUMENT = re.compile(r"[0-9]{1,7}\Z")
BYTE_ARGUMENT = re.compile(r"[0-9]{1,19}\Z")
SOURCE_REFERENCE = re.compile(r"S[1-9][0-9]{0,3}\Z")
KNOWN_TOOLS = frozenset({"bash", "fffind", "ffgrep", "obs_recall", "read"})
METADATA_FIELDS = frozenset({"type", "id", "timestamp", "parentId", "name", "provider", "modelId", "thinkingLevel"})
METADATA_EVENTS = frozenset({"session", "session_info", "model_change", "thinking_level_change"})
EVENT_FIELDS = frozenset({"type", "id", "timestamp", "parentId", "message", "name", "provider", "modelId", "thinkingLevel"})
MESSAGE_FIELDS = {
    "assistant": frozenset({"api", "content", "model", "provider", "rawStopReason", "responseId", "role", "stopReason", "thinkingLevel", "timestamp", "usage"}),
    "toolResult": frozenset({"content", "details", "isError", "role", "timestamp", "toolCallId", "toolName"}),
    "user": frozenset({"content", "role", "timestamp"}),
    "system": frozenset({"content", "role", "sections", "timestamp", "toolsAdded"}),
}
LIMIT = "LIMIT: caller supplies locator coordinates; no Pi parentId/active-leaf branch proof; pairing only, no result, exit, head, artifact, or verdict inference."


@dataclass
class Event:
    line: int
    kind: str
    tool: str
    tool_key: str | None = field(repr=False)
    identifier: str | None = field(repr=False)
    reference: str
    reasons: set[str] = field(default_factory=set)
    paired_with: str | None = None


@dataclass(frozen=True)
class Finding:
    line: int | None
    reason: str


@dataclass(frozen=True)
class Inspection:
    records: tuple[str, ...]
    unproven: bool


def _invalid(reason: str) -> Inspection:
    return Inspection((f"UNPROVEN reason={reason}", LIMIT), True)


def _context(source_ref: str, start: int, end: int, offset: int) -> str:
    return f"ADVISORY ONLY source={source_ref} lines={start}-{end} byte={offset}"


def _valid_range(start: int, end: int) -> bool:
    return (
        isinstance(start, int) and not isinstance(start, bool)
        and isinstance(end, int) and not isinstance(end, bool)
        and 1 <= start <= end <= MAX_LINE_NUMBER
        and end - start + 1 <= MAX_RANGE_LINES
    )


def _safe_tool(value: object) -> tuple[str, str | None, str | None]:
    if not isinstance(value, str):
        return "other", None, "malformed-tool-name"
    if len(value) > 32 or value not in KNOWN_TOOLS:
        return "other", None, "unsupported-tool"
    return value, value, None


def _add_event(
    events: list[Event], findings: list[Finding], line: int,
    kind: str, identifier: object, tool_name: object,
) -> Event | None:
    if len(events) >= MAX_EVENTS:
        findings.append(Finding(line, "event-limit"))
        return None
    tool, tool_key, tool_issue = _safe_tool(tool_name)
    reasons = {tool_issue} if tool_issue else set()
    valid_id = isinstance(identifier, str) and len(identifier) <= 128 and ID_PATTERN.fullmatch(identifier)
    if not valid_id:
        reasons.add("malformed-identifier")
        identifier = None
    event = Event(line, kind, tool, tool_key, identifier, f"R{len(events) + 1:04d}", reasons)
    events.append(event)
    return event


def _unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError
        result[key] = value
    return result


def _parse_record(raw: bytes, line: int, events: list[Event], findings: list[Finding]) -> None:
    try:
        record = json.loads(raw.decode("utf-8"), object_pairs_hook=_unique_object)
    except (UnicodeError, json.JSONDecodeError, RecursionError, TypeError, ValueError):
        findings.append(Finding(line, "malformed-line"))
        return
    if not isinstance(record, dict):
        findings.append(Finding(line, "malformed-line"))
        return

    event_type = record.get("type")
    if not isinstance(event_type, str):
        findings.append(Finding(line, "unsupported-event"))
        return
    if event_type in METADATA_EVENTS:
        if set(record) - METADATA_FIELDS:
            findings.append(Finding(line, "unsupported-event-shape"))
        return
    if event_type != "message":
        findings.append(Finding(line, "unsupported-event"))
        return
    if set(record) - EVENT_FIELDS:
        findings.append(Finding(line, "unsupported-event-shape"))

    message = record.get("message")
    if not isinstance(message, dict):
        findings.append(Finding(line, "malformed-message"))
        return
    role = message.get("role")
    if not isinstance(role, str) or role not in MESSAGE_FIELDS:
        findings.append(Finding(line, "unsupported-role"))
        return
    if set(message) - MESSAGE_FIELDS[role]:
        findings.append(Finding(line, "unsupported-message-shape"))
    if role == "assistant":
        content = message.get("content")
        if not isinstance(content, list):
            findings.append(Finding(line, "malformed-message"))
            return
        unsupported_block = False
        for block in content:
            if not isinstance(block, dict) or not isinstance(block.get("type"), str):
                unsupported_block = True
                continue
            if block["type"] == "toolCall":
                if set(block) - {"arguments", "id", "name", "type"}:
                    findings.append(Finding(line, "unsupported-content-block"))
                event = _add_event(events, findings, line, "call", block.get("id"), block.get("name"))
                if event and not isinstance(block.get("arguments"), dict):
                    event.reasons.add("malformed-call")
            elif block["type"] == "text":
                if set(block) - {"text", "type"}:
                    findings.append(Finding(line, "unsupported-content-block"))
                if not isinstance(block.get("text"), str):
                    findings.append(Finding(line, "malformed-text-block"))
            elif block["type"] == "thinking":
                if set(block) - {"thinking", "thinkingSignature", "type"}:
                    findings.append(Finding(line, "unsupported-content-block"))
                if not isinstance(block.get("thinking"), str):
                    findings.append(Finding(line, "malformed-thinking-block"))
            else:
                unsupported_block = True
            if len(events) >= MAX_EVENTS:
                findings.append(Finding(line, "event-limit"))
                return
        if unsupported_block:
            findings.append(Finding(line, "unsupported-content-block"))
        return
    if role == "toolResult":
        content, details = message.get("content"), message.get("details", {})
        if not isinstance(content, list) or not isinstance(details, dict):
            findings.append(Finding(line, "malformed-result"))
            return
        if any(
            not isinstance(block, dict) or block.get("type") != "text"
            or set(block) - {"text", "type"}
            or not isinstance(block.get("text"), str)
            for block in content
        ):
            findings.append(Finding(line, "unsupported-result-content"))
        event = _add_event(
            events, findings, line, "result",
            message.get("toolCallId"), message.get("toolName"),
        )
        if event is not None:
            if not isinstance(message.get("isError"), bool):
                event.reasons.add("malformed-result")
            elif message["isError"]:
                event.reasons.add("tool-error")
            if "truncation" in details:
                event.reasons.add("truncated-result")
            if set(details) - {"truncation"}:
                event.reasons.add("unsupported-result-details")
        else:
            if not isinstance(message.get("isError"), bool):
                findings.append(Finding(line, "malformed-result"))
            elif message["isError"]:
                findings.append(Finding(line, "tool-error"))
            if "truncation" in details:
                findings.append(Finding(line, "truncated-result"))
            if set(details) - {"truncation"}:
                findings.append(Finding(line, "unsupported-result-details"))
        return
    if role not in {"system", "user"}:
        findings.append(Finding(line, "unsupported-role"))


def _pair_events(events: list[Event], findings: list[Finding]) -> None:
    groups: dict[str, list[Event]] = {}
    for event in events:
        if event.identifier is not None:
            groups.setdefault(event.identifier, []).append(event)
    for group in groups.values():
        calls = [event for event in group if event.kind == "call"]
        results = [event for event in group if event.kind == "result"]
        if len(calls) > 1 or len(results) > 1:
            for event in group:
                event.reasons.add("duplicate-identifier")
        elif len(calls) == len(results) == 1:
            if results[0].line <= calls[0].line:
                for event in group:
                    event.reasons.add("ordering-contradiction")
            elif calls[0].tool_key != results[0].tool_key:
                for event in group:
                    event.reasons.add("tool-mismatch")
            else:
                calls[0].paired_with = results[0].reference
                results[0].paired_with = calls[0].reference
        else:
            for event in group:
                event.reasons.add("unmatched-in-range")
    for event in events:
        findings.extend(Finding(event.line, reason) for reason in event.reasons)


def inspect_range(path: Path, start: int, end: int, start_byte: int, source_ref: str) -> Inspection:
    """Inspect caller-selected physical lines; coordinates prove no line count or Pi branch."""
    if not isinstance(source_ref, str) or not SOURCE_REFERENCE.fullmatch(source_ref):
        return _invalid("invalid-source-reference")
    if not _valid_range(start, end):
        return _invalid("invalid-range")
    if not isinstance(start_byte, int) or isinstance(start_byte, bool) or not 0 <= start_byte <= MAX_START_BYTE:
        return _invalid("invalid-byte-offset")
    if (start == 1) != (start_byte == 0):
        return _invalid("invalid-line-boundary")
    if not isinstance(path, Path):
        return _invalid("invalid-source-path")
    if not path.is_absolute():
        return Inspection((_context(source_ref, start, end, start_byte), "UNPROVEN reason=source-unavailable", LIMIT), True)
    events: list[Event] = []
    findings: list[Finding] = []
    original_size = 0
    selected_end = start_byte
    try:
        if not path.is_file() or path.is_symlink():
            return Inspection((_context(source_ref, start, end, start_byte), "UNPROVEN reason=source-unavailable", LIMIT), True)
        descriptor = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_NOFOLLOW", 0))
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            os.close(descriptor)
            return Inspection((_context(source_ref, start, end, start_byte), "UNPROVEN reason=source-unavailable", LIMIT), True)
        with os.fdopen(descriptor, "rb") as source:
            original_size = os.fstat(source.fileno()).st_size
            if start_byte > original_size:
                return Inspection((_context(source_ref, start, end, start_byte), "UNPROVEN reason=range-unavailable", LIMIT), True)
            if start_byte:
                source.seek(start_byte - 1)
                if source.read(1) != b"\n":
                    return Inspection((_context(source_ref, start, end, start_byte), "UNPROVEN reason=invalid-line-boundary", LIMIT), True)
            source.seek(start_byte)
            selected_bytes = 0
            selected_end = start_byte
            for line_number in range(start, end + 1):
                raw = source.readline(MAX_LINE_BYTES + 1)
                if not raw:
                    findings.append(Finding(line_number, "range-unavailable"))
                    break
                selected_bytes += len(raw)
                selected_end += len(raw)
                complete_line = raw.endswith(b"\n")
                if len(raw) > MAX_LINE_BYTES:
                    findings.append(Finding(line_number, "line-too-large"))
                    break
                if selected_bytes > MAX_SELECTED_BYTES:
                    findings.append(Finding(line_number, "range-byte-limit"))
                    break
                _parse_record(raw, line_number, events, findings)
                if not complete_line:
                    next_byte = source.read(1)
                    if next_byte:
                        findings.append(Finding(line_number, "line-boundary-unknown"))
                        findings.append(Finding(line_number + 1, "range-not-fully-read"))
                        break
                    else:
                        findings.append(Finding(line_number, "unterminated-line"))
                        break
                if any(finding.reason == "event-limit" for finding in findings):
                    findings.append(Finding(line_number, "range-not-fully-read"))
                    break
    except (OSError, UnicodeError, ValueError):
        findings.append(Finding(None, "source-unavailable"))
    except Exception:
        findings.append(Finding(None, "source-unavailable"))

    if selected_end < original_size:
        findings.append(Finding(end, "range-ends-before-file-end"))
    _pair_events(events, findings)
    if any(event.reasons for event in events):
        findings.append(Finding(None, "event-unproven"))
    findings = sorted(set(findings), key=lambda finding: (finding.line or 0, finding.reason))
    records = [_context(source_ref, start, end, start_byte)]
    if not events and not findings:
        findings.append(Finding(None, "no-events-in-range"))
    for event in events:
        if event.reasons:
            records.append(
                f"UNPROVEN line={event.line} kind={event.kind} tool={event.tool} "
                f"ref={event.reference} reason={','.join(sorted(event.reasons))}"
            )
        elif event.paired_with:
            records.append(
                f"UNPROVEN line={event.line} kind={event.kind} tool={event.tool} "
                f"ref={event.reference} state=paired-with:{event.paired_with} result-unverified"
            )
        else:
            records.append(
                f"UNPROVEN line={event.line} kind={event.kind} tool={event.tool} "
                f"ref={event.reference} reason=unmatched-in-range"
            )
    records.extend(
        f"UNPROVEN line={finding.line} reason={finding.reason}"
        if finding.line is not None else f"UNPROVEN reason={finding.reason}"
        for finding in findings
    )
    records.append(LIMIT)
    return Inspection(tuple(records), True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--session", required=True, help="one explicit absolute Pi JSONL regular-file path")
    parser.add_argument("--start-line", required=True, help="caller-supplied positive locator line, inclusive")
    parser.add_argument("--start-byte", required=True, help="caller-supplied byte offset at the selected line boundary")
    parser.add_argument("--end-line", required=True, help="caller-supplied positive locator line, inclusive")
    parser.add_argument("--source-ref", required=True, help="sanitized source reference (S1–S9999)")
    args = parser.parse_args(argv)
    if (
        not LINE_ARGUMENT.fullmatch(args.start_line)
        or not LINE_ARGUMENT.fullmatch(args.end_line)
        or not BYTE_ARGUMENT.fullmatch(args.start_byte)
    ):
        inspection = _invalid("invalid-range-or-offset")
    else:
        inspection = inspect_range(
            Path(args.session), int(args.start_line), int(args.end_line),
            int(args.start_byte), args.source_ref,
        )
    for record in inspection.records:
        print(record)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
