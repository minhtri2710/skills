#!/usr/bin/env python3
"""Observe verified Claude and Pi compaction markers for one live Herdr seat.

This slice is deliberately read-only.  It resolves a seat from a supplied
live-roster payload, derives the durable session path from that identity, and
counts only marker records that can be associated with the resolved session.
"""
from __future__ import annotations

import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_PROJECT_KEY = re.compile(r"^-[A-Za-z0-9][A-Za-z0-9._-]*$")
_SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


@dataclass(frozen=True)
class SessionRecord:
    """A session path authenticated from one live roster record."""

    seat: str
    agent_name: str | None
    kind: str
    session_id: str
    cwd: Path
    session_root: Path
    session_path: Path


def _valid_identifier(value: Any, pattern: re.Pattern[str] = _IDENTIFIER) -> bool:
    return isinstance(value, str) and value == value.strip() and pattern.fullmatch(value) is not None


def _contained(root: Path, child: Path) -> bool:
    try:
        relative = child.relative_to(root)
    except ValueError:
        return False
    return relative != Path(".") and not relative.is_absolute()


def _canonical_directory(path: Path) -> Path | None:
    try:
        resolved = path.expanduser().resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    return resolved if resolved.is_dir() else None


def _canonical_file(path: Path, root: Path) -> Path | None:
    if not path.is_absolute():
        return None
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if not _contained(root, resolved):
        return None
    try:
        mode = resolved.stat().st_mode
    except OSError:
        return None
    return resolved if stat.S_ISREG(mode) else None


def _project_key(cwd: Path) -> str | None:
    rendered = str(cwd)
    if not rendered.startswith("/"):
        return None
    key = "-" + rendered.lstrip("/").replace("/", "-")
    return key if _PROJECT_KEY.fullmatch(key) is not None else None


def _agents(roster: Any) -> list[Mapping[str, Any]] | None:
    raw: Any = roster
    if isinstance(roster, Mapping):
        result = roster.get("result")
        if isinstance(result, Mapping):
            raw = result.get("agents")
        elif "agents" in roster:
            raw = roster.get("agents")
        else:
            return None
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes, bytearray)):
        return None
    agents: list[Mapping[str, Any]] = []
    for agent in raw:
        if not isinstance(agent, Mapping):
            return None
        agents.append(agent)
    return agents


def _matching_agent(roster: Any, seat: str) -> Mapping[str, Any] | None:
    if not _valid_identifier(seat):
        return None
    agents = _agents(roster)
    if agents is None:
        return None

    matches: list[Mapping[str, Any]] = []
    for agent in agents:
        name = agent.get("name")
        pane_id = agent.get("pane_id")
        if name == seat or pane_id == seat:
            matches.append(agent)
    return matches[0] if len(matches) == 1 else None


def _validated_cwd(agent: Mapping[str, Any], project_root: Path) -> Path | None:
    raw_cwd = agent.get("cwd")
    if not isinstance(raw_cwd, str) or not raw_cwd or not Path(raw_cwd).is_absolute():
        return None
    cwd = _canonical_directory(Path(raw_cwd))
    return cwd if cwd is not None and cwd == project_root else None


def _resolve_pi_session(
    agent: Mapping[str, Any],
    seat: str,
    agent_name: str | None,
    cwd: Path,
    home: Path,
) -> SessionRecord | None:
    session = agent.get("agent_session")
    if not isinstance(session, Mapping):
        return None
    if session.get("source") != "herdr:pi" or session.get("agent") != "pi" or session.get("kind") != "path":
        return None
    raw_path = session.get("value")
    if not isinstance(raw_path, str):
        return None
    root = _canonical_directory(home / ".pi" / "agent" / "sessions")
    if root is None or not _contained(home, root):
        return None
    path = _canonical_file(Path(raw_path), root)
    if path is None or path.suffix != ".jsonl":
        return None
    _, separator, session_id = path.stem.rpartition("_")
    if not separator or not _valid_identifier(session_id, _SESSION_ID):
        return None
    return SessionRecord(seat, agent_name, "pi", session_id, cwd, root, path)


def _resolve_claude_session(
    agent: Mapping[str, Any],
    seat: str,
    agent_name: str | None,
    cwd: Path,
    home: Path,
) -> SessionRecord | None:
    session = agent.get("agent_session")
    if not isinstance(session, Mapping):
        return None
    if session.get("source") != "herdr:claude" or session.get("agent") != "claude" or session.get("kind") != "id":
        return None
    session_id = session.get("value")
    if not _valid_identifier(session_id, _SESSION_ID):
        return None
    project_key = _project_key(cwd)
    if project_key is None:
        return None
    root = _canonical_directory(home / ".claude" / "projects")
    if root is None or not _contained(home, root):
        return None
    project_dir = root / project_key
    if not _contained(root, project_dir):
        return None
    path = _canonical_file(project_dir / f"{session_id}.jsonl", root)
    if path is None:
        return None
    return SessionRecord(seat, agent_name, "claude", session_id, cwd, root, path)


def resolve_live_session(
    roster: Any,
    seat: str,
    *,
    project_root: str | os.PathLike[str],
    home_dir: str | os.PathLike[str] | None = None,
) -> SessionRecord | None:
    """Resolve exactly one live roster seat to a contained durable session.

    The roster is data captured from ``herdr agent list``.  A transcript path
    supplied outside the roster is intentionally not accepted by this seam.
    """
    agent = _matching_agent(roster, seat)
    if agent is None:
        return None
    project = _canonical_directory(Path(project_root))
    if project is None:
        return None
    cwd = _validated_cwd(agent, project)
    if cwd is None:
        return None

    kind = agent.get("agent")
    if kind not in {"pi", "claude"}:
        return None
    raw_name = agent.get("name")
    agent_name = raw_name if isinstance(raw_name, str) else None
    raw_home = home_dir if home_dir is not None else os.environ.get("HOME")
    if not isinstance(raw_home, (str, os.PathLike)) or not str(raw_home):
        return None
    home = _canonical_directory(Path(raw_home))
    if home is None:
        return None
    if kind == "pi":
        return _resolve_pi_session(agent, seat, agent_name, cwd, home)
    return _resolve_claude_session(agent, seat, agent_name, cwd, home)


def _parse_jsonl(path: Path) -> list[Mapping[str, Any]] | None:
    records: list[Mapping[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line in stream:
                try:
                    value = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return None
                if not isinstance(value, Mapping):
                    return None
                records.append(value)
    except (OSError, UnicodeError):
        return None
    return records


def _session_header(records: list[Mapping[str, Any]], session: SessionRecord) -> tuple[str, Path] | None:
    if not records:
        return None
    if session.kind == "claude":
        if Path(session.session_path).stem != session.session_id:
            return None
        session_ids = {record.get("sessionId") for record in records if "sessionId" in record}
        if session_ids != {session.session_id}:
            return None
        for record in records:
            raw_cwd = record.get("cwd")
            if raw_cwd is None:
                continue
            if not isinstance(raw_cwd, str):
                return None
            record_cwd = _canonical_directory(Path(raw_cwd))
            if record_cwd is None or record_cwd != session.cwd:
                return None
        return session.session_id, session.cwd

    header = records[0]
    if header.get("type") != "session":
        return None
    session_id = header.get("id")
    raw_cwd = header.get("cwd")
    timestamp = header.get("timestamp")
    if not _valid_identifier(session_id, _SESSION_ID) or session_id != session.session_id:
        return None
    if not isinstance(raw_cwd, str) or not raw_cwd or not isinstance(timestamp, str) or not timestamp:
        return None
    header_cwd = _canonical_directory(Path(raw_cwd))
    if header_cwd is None or header_cwd != session.cwd:
        return None
    return session_id, header_cwd


def _record_matches_session(record: Mapping[str, Any], session: SessionRecord, header_id: str, header_cwd: Path) -> bool:
    record_id = record.get("sessionId")
    if record_id is not None and record_id != header_id:
        return False
    raw_cwd = record.get("cwd")
    if raw_cwd is not None:
        if not isinstance(raw_cwd, str):
            return False
        record_cwd = _canonical_directory(Path(raw_cwd))
        if record_cwd is None or record_cwd != header_cwd:
            return False
    return True


def _valid_claude_boundary(record: Mapping[str, Any], session: SessionRecord, header_id: str, header_cwd: Path) -> bool:
    metadata = record.get("compactMetadata")
    trigger = metadata.get("trigger") if isinstance(metadata, Mapping) else None
    return (
        record.get("type") == "system"
        and record.get("subtype") == "compact_boundary"
        and isinstance(record.get("sessionId"), str)
        and record.get("sessionId") == header_id
        and isinstance(record.get("uuid"), str)
        and _valid_identifier(record.get("uuid"), _SESSION_ID)
        and isinstance(trigger, str)
        and bool(trigger.strip())
        and isinstance(record.get("cwd"), str)
        and _record_matches_session(record, session, header_id, header_cwd)
    )


def _valid_claude_summary(record: Mapping[str, Any], session: SessionRecord, header_id: str, header_cwd: Path) -> bool:
    return (
        record.get("isCompactSummary") is True
        and isinstance(record.get("sessionId"), str)
        and record.get("sessionId") == header_id
        and isinstance(record.get("uuid"), str)
        and _valid_identifier(record.get("uuid"), _SESSION_ID)
        and isinstance(record.get("cwd"), str)
        and _record_matches_session(record, session, header_id, header_cwd)
    )


def _observe_claude(records: list[Mapping[str, Any]], session: SessionRecord) -> int:
    header = _session_header(records, session)
    if header is None:
        return 0
    header_id, header_cwd = header
    pending = False
    count = 0
    seen_marker_ids: set[str] = set()
    for record in records:
        is_boundary = record.get("type") == "system" and record.get("subtype") == "compact_boundary"
        is_summary = record.get("isCompactSummary") is True
        if is_boundary:
            if not _valid_claude_boundary(record, session, header_id, header_cwd) or pending:
                return 0
            marker_id = record["uuid"]
            if marker_id in seen_marker_ids:
                return 0
            seen_marker_ids.add(marker_id)
            pending = True
        elif is_summary:
            if not _valid_claude_summary(record, session, header_id, header_cwd):
                return 0
            marker_id = record["uuid"]
            if marker_id in seen_marker_ids or not pending:
                return 0
            seen_marker_ids.add(marker_id)
            count += 1
            pending = False
    return 0 if pending else count


def _valid_pi_compaction(record: Mapping[str, Any], session: SessionRecord, header_id: str, header_cwd: Path) -> bool:
    parent_id = record.get("parentId")
    return (
        record.get("type") == "compaction"
        and _valid_identifier(record.get("id"), _SESSION_ID)
        and (parent_id is None or _valid_identifier(parent_id, _SESSION_ID))
        and isinstance(record.get("timestamp"), str)
        and bool(record.get("timestamp"))
        and isinstance(record.get("summary"), str)
        and isinstance(record.get("firstKeptEntryId"), str)
        and bool(record.get("firstKeptEntryId"))
        and isinstance(record.get("tokensBefore"), int)
        and not isinstance(record.get("tokensBefore"), bool)
        and record.get("tokensBefore") >= 0
        and _record_matches_session(record, session, header_id, header_cwd)
    )


def _observe_pi(records: list[Mapping[str, Any]], session: SessionRecord) -> int:
    header = _session_header(records, session)
    if header is None:
        return 0
    header_id, header_cwd = header
    seen_ids: set[str] = set()
    count = 0
    for record in records[1:]:
        if record.get("type") != "compaction":
            continue
        if not _valid_pi_compaction(record, session, header_id, header_cwd):
            return 0
        record_id = record["id"]
        if record_id in seen_ids:
            return 0
        seen_ids.add(record_id)
        count += 1
    return count


def observe_session(session: SessionRecord | None) -> int:
    """Return the verified compaction count, or zero on any failed proof."""
    if session is None:
        return 0
    path = _canonical_file(session.session_path, session.session_root)
    if path is None or path != session.session_path:
        return 0
    records = _parse_jsonl(path)
    if records is None:
        return 0
    if session.kind == "claude":
        return _observe_claude(records, session)
    if session.kind == "pi":
        return _observe_pi(records, session)
    return 0


def observe_live_seat(
    roster: Any,
    seat: str,
    *,
    project_root: str | os.PathLike[str],
    home_dir: str | os.PathLike[str] | None = None,
) -> int:
    """Resolve one live seat and count only its verified durable markers."""
    session = resolve_live_session(roster, seat, project_root=project_root, home_dir=home_dir)
    return observe_session(session) if session is not None else 0
