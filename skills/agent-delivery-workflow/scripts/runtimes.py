"""What each agent runtime keeps on disk and shows on screen, keyed by `Seat.kind`.

`claude` and `pi` seats: where a session file lives and how its compaction markers are counted, which model a Pi
session runs, and the Pi pane footer the waker reads. Callers ask here and never open a runtime's files themselves.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import backend

# The measured pi footer needs 8 lines to show its marker, and a read refused a 15-line tail on a working seat (10 succeeded).
TAIL_LINES = 10
SESSION_MODEL_KINDS = frozenset({"pi"})
_SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_MARKERS = ("Awaiting:", "Awaiting reports:")


class Unavailable(Exception):
    """Evidence could not be proven; callers fail closed."""


def _reported_pi_session(session: backend.Session) -> tuple[Path, str]:
    path = Path(session.value)
    session_id = path.stem.rpartition("_")[2]
    if session.kind == "path" and path.is_absolute() and path.suffix == ".jsonl" and _SESSION_ID.fullmatch(session_id):
        return path, session_id
    raise Unavailable("roster session is not a Claude id or Pi path")


def _session_file(seat: backend.Seat, project: Path, home: Path) -> tuple[Path, str]:
    session = seat.session
    if session is None:
        raise Unavailable("backend reports no agent session")
    if seat.kind == "claude" and session.kind == "id" and _SESSION_ID.fullmatch(session.value):
        key = re.sub(r"[^A-Za-z0-9]", "-", str(project))
        return home / ".claude" / "projects" / key / f"{session.value}.jsonl", session.value
    if seat.kind == "pi":
        return _reported_pi_session(session)
    raise Unavailable("roster session is not a Claude id or Pi path")


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                if line.endswith("\n"):
                    raise Unavailable(f"malformed record in {path}")
                break  # a writer's partial last line
            if not isinstance(record, dict):
                raise Unavailable(f"malformed record in {path}")
            records.append(record)
    return records


def _count_pi(records: list[dict[str, Any]], session_id: str) -> int:
    if not records or records[0].get("type") != "session" or records[0].get("id") != session_id:
        raise Unavailable("Pi session header does not match the roster session")
    seen: set[str] = set()
    for record in records[1:]:
        if record.get("type") != "compaction":
            continue
        marker_id = record.get("id")
        if (
            not isinstance(marker_id, str) or not marker_id or marker_id in seen
            or not all(isinstance(record.get(k), str) and record[k] for k in ("timestamp", "firstKeptEntryId"))
            or not isinstance(record.get("summary"), str)
            or type(record.get("tokensBefore")) is not int or record["tokensBefore"] < 0
        ):
            raise Unavailable("unverified Pi compaction record")
        seen.add(marker_id)
    return len(seen)


def _count_claude(records: list[dict[str, Any]], session_id: str) -> int:
    """A marker is a compact_boundary followed by its isCompactSummary, both for this session."""
    seen: set[str] = set()
    pending = False
    count = 0
    for record in records:
        if record.get("sessionId", session_id) != session_id:
            raise Unavailable("Claude record belongs to another session")
        boundary = record.get("type") == "system" and record.get("subtype") == "compact_boundary"
        summary = not boundary and record.get("isCompactSummary") is True
        if not (boundary or summary):
            continue
        uuid = record.get("uuid")
        metadata = record.get("compactMetadata")
        trigger = metadata.get("trigger") if isinstance(metadata, dict) else None
        if (
            record.get("sessionId") != session_id or not isinstance(uuid, str) or uuid in seen
            or pending == boundary or (boundary and not (isinstance(trigger, str) and trigger.strip()))
        ):
            raise Unavailable("unverified Claude compaction record")
        seen.add(uuid)
        pending = boundary
        if summary:
            count += 1
    if pending:
        raise Unavailable("Claude compact boundary has no summary")
    return count


def compactions(seat: backend.Seat, project: Path, home: Path) -> tuple[int, str]:
    """The seat's verified compaction-marker count and its session id."""
    path, session_id = _session_file(seat, project, home)
    records = _read_jsonl(path)
    return (_count_claude if seat.kind == "claude" else _count_pi)(records, session_id), session_id


def _process_start(pid: int | None) -> datetime:
    try:
        proc = subprocess.run(
            ["ps", "-o", "lstart=", "-p", str(pid)],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
            timeout=10,
            env={**os.environ, "LC_ALL": "C"},
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise Unavailable(f"could not read pi process start for pid {pid}: {exc}") from exc
    if proc.returncode:
        detail = proc.stderr.strip() or proc.stdout.strip() or str(proc.returncode)
        raise Unavailable(f"could not read pi process start for pid {pid}: {detail}")
    try:
        return datetime.strptime(proc.stdout.strip(), "%a %b %d %H:%M:%S %Y").astimezone()
    except ValueError as exc:
        raise Unavailable(f"could not read pi process start for pid {pid}: invalid ps timestamp") from exc


def pi_session_dir(cwd: str) -> Path:
    """Where Pi keeps the sessions begun in `cwd`."""
    agent_dir = os.path.expanduser(os.environ.get("PI_CODING_AGENT_DIR") or "~/.pi/agent")
    slug = cwd.removeprefix("/").replace("/", "-").replace(":", "-")
    return Path(agent_dir) / "sessions" / f"--{slug}--"


def _pi_session_is_named(path: Path, name: str, process_start: datetime) -> bool:
    try:
        with path.open(encoding="utf-8") as session:
            first = json.loads(next(session))
            if not isinstance(first, dict) or first.get("type") != "session":
                return False
            raw_timestamp = first.get("timestamp")
            if not isinstance(raw_timestamp, str):
                return False
            timestamp = datetime.fromisoformat(raw_timestamp.replace("Z", "+00:00"))
            if timestamp.tzinfo is None or timestamp < process_start.astimezone(timezone.utc):
                return False
            named = False
            for line in session:
                try:
                    entry = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return False
                if not isinstance(entry, dict):
                    return False
                if entry.get("type") in {"message", "model_change"}:
                    return named
                if entry.get("type") == "session_info" and entry.get("name") == name:
                    named = True
            return named
    except (OSError, StopIteration, KeyError, TypeError, ValueError, UnicodeDecodeError):
        return False


def _pi_session_files(seat: backend.Seat, process: backend.Process) -> list[Path]:
    """The path the backend reports; else the Pi sessions under the process cwd named for the seat and begun after it started."""
    if seat.session is not None:
        try:
            return [_reported_pi_session(seat.session)[0]]
        except Unavailable:
            return []
    process_start = _process_start(process.pid)
    if process.cwd is None or seat.name is None:
        return []
    try:
        return [
            path for path in pi_session_dir(process.cwd).glob("*.jsonl")
            if _pi_session_is_named(path, seat.name, process_start)
        ]
    except OSError:
        return []


def _last_pi_model(path: Path) -> str | None:
    model = None
    try:
        with path.open(encoding="utf-8") as session:
            for line in session:
                try:
                    entry = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    return None
                if isinstance(entry, dict) and entry.get("type") == "model_change":
                    provider, model_id = entry.get("provider"), entry.get("modelId")
                    valid_model = isinstance(provider, str) and provider and isinstance(model_id, str) and model_id
                    model = f"{provider}/{model_id}" if valid_model else None
    except (OSError, UnicodeDecodeError):
        return None
    return model


def session_model(seat: backend.Seat, process: backend.Process) -> tuple[str | None, str | None]:
    """The model a seat of a SESSION_MODEL_KINDS kind runs, read from its session file: (model, None) or (None, reason)."""
    files = _pi_session_files(seat, process)
    if not files:
        return None, "no-named-session"
    if len(files) != 1:
        return None, "ambiguous-session"
    model = _last_pi_model(files[0])
    return (model, None) if model is not None else (None, "no-named-session")


def model_matches(route_model: str | None, running_model: str) -> bool:
    """A Pi route names the model in full (`prov/luna`) or bare (`luna`)."""
    return route_model == running_model or (
        route_model is not None
        and "/" not in route_model
        and running_model.rpartition("/")[2] == route_model
    )


def _is_rule(line: str) -> bool:
    stripped = line.strip()
    return len(stripped) >= 3 and set(stripped) == {"─"}


# ponytail: only the two-rule pi footer can suppress. Measured claude (one rule, prompt line) and every other layout fail open, so they only cost extra wakes. Upgrade when a suppressing layout is measured for another runtime.
def has_awaiting_marker(tail: str) -> bool:
    """True only when the Lead's last message ends in an explicit, unquoted, unfenced Awaiting line.

    The measured layout is a footer bounded by two rules. The cluster is the rules and blanks above the last rule.
    The message is the text above the cluster; its last non-blank line must start with a marker at column 0 and sit
    outside a fenced block. Anything else, including a single-rule or unrecognised layout, is not established.
    """
    lines = tail.split("\n")
    rules = [index for index, line in enumerate(lines) if _is_rule(line)]
    if len(rules) < 2:
        return False
    top = rules[-1]
    while top > 0 and (_is_rule(lines[top - 1]) or not lines[top - 1].strip()):
        top -= 1
    if sum(1 for line in lines[top:] if _is_rule(line)) < 2:
        return False
    body = [index for index in range(top) if lines[index].strip()]
    if not body:
        return False
    last = body[-1]
    fences = sum(1 for line in lines[:last] if line.strip().startswith("```"))
    return fences % 2 == 0 and lines[last].startswith(_MARKERS)
