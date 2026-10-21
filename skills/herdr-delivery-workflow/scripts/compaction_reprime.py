#!/usr/bin/env python3
"""Reprime one live Herdr seat after compaction (Supervisor-side command).

Resolves the seat from `herdr agent list`, counts the verified compaction markers
in its Claude/Pi session file, and keeps one {baseline, sent} JSON file per
seat-session. The first observation sets the baseline and sends nothing; each
later newly crossed threshold of four markers since baseline sends one
pointer-only `herdr agent prompt`.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any, Sequence

import herdr_cli


THRESHOLD = 4
RELAUNCH_THRESHOLD = 8
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_DOCTRINE = Path(__file__).resolve().parents[1] / "references"


class Unavailable(Exception):
    """Evidence or state could not be proven; nothing is prompted."""


def _live_agent(seat: str) -> dict[str, Any]:
    try:
        result = herdr_cli.run(["agent", "list"])
        roster = json.loads(result.stdout) if result.returncode == 0 else None
    except (herdr_cli.HerdrUnavailable, json.JSONDecodeError):
        roster = None
    if isinstance(roster, dict):
        result = roster.get("result", roster)
        roster = result.get("agents") if isinstance(result, dict) else None
    if not isinstance(roster, list):
        raise Unavailable("live Herdr roster unavailable")
    matches = [a for a in roster if isinstance(a, dict) and seat in (a.get("name"), a.get("pane_id"))]
    if len(matches) != 1:
        raise Unavailable(f"{seat} is not exactly one live roster seat")
    return matches[0]


def _session_file(agent: dict[str, Any], project: Path, home: Path) -> tuple[Path, str]:
    """The seat's session file and session id; Claude storage is keyed by the project root."""
    session = agent.get("agent_session")
    value = session.get("value") if isinstance(session, dict) else None
    if not isinstance(value, str):
        raise Unavailable("roster seat has no durable session")
    if agent.get("agent") == "claude" and session.get("kind") == "id" and _ID.fullmatch(value):
        key = "-" + str(project).lstrip("/").replace("/", "-")
        return home / ".claude" / "projects" / key / f"{value}.jsonl", value
    if agent.get("agent") == "pi" and session.get("kind") == "path":
        path = Path(value)
        session_id = path.stem.rpartition("_")[2]
        if path.is_absolute() and path.suffix == ".jsonl" and _ID.fullmatch(session_id):
            return path, session_id
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


def _block(run_id: str, seat: str, threshold: int, slug: str, home: Path) -> str:
    records = home / ".herdr" / "projects" / slug
    run_dir = records / "runs" / run_id
    required = [records / "context-pack.md", records / "gates.md", records / "supervisor-notebook.md"]
    if not run_dir.is_dir() or not all(p.is_file() for p in required):
        raise Unavailable(f"threshold {threshold} remains pending; prompt not attempted")
    lead, supervisor, closeout = (_DOCTRINE / f"{name}.md" for name in ("lead", "supervisor", "closeout"))
    lines = [
        f"run-id: {run_id}", f"seat: {seat}", f"run-dir: {run_dir}",
        f"context-pack: {required[0]}", f"gate-ledger: {required[1]}", f"supervisor-notebook: {required[2]}",
    ]
    for label, name in (("intake", "intake-record.md"), ("plan", "plan.md"), ("specification", "specification.md"), ("slices", "slices.json")):
        if (run_dir / name).is_file():
            lines.append(f"{label}: {run_dir / name}")
    lines += [
        f"lead-recovery: {lead}#Recovery", f"lead-delivery: {lead}#Delivery sequence",
        f"lead-gates: {lead}#Gates and ledger", f"supervisor-handoff: {supervisor}#Handoff",
        f"closeout: {closeout}#Acceptance custody",
    ]
    if threshold >= RELAUNCH_THRESHOLD:
        lines.append(f"relaunch-recommended: {threshold} compactions since baseline; at the next slice boundary: {lead}#Relaunch and doctrine")
    return "\n".join(lines)


def _state_dir(home: Path, slug: str) -> Path:
    """The coordination directory, created if missing; no component below projects/ may be a symlink."""
    current = home / ".herdr" / "projects"
    current.mkdir(parents=True, exist_ok=True)
    for part in (slug, "runs", "coordination"):
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            current.mkdir()
            continue
        if not stat.S_ISDIR(mode):
            raise Unavailable(f"{current} is not a plain directory")
    return current


def _load_state(path: Path, count: int) -> dict[str, int] | None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(mode):
        raise Unavailable(f"{path} is not a regular file")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise Unavailable(f"unreadable state {path}")
    if not isinstance(state, dict) or set(state) != {"baseline", "sent"} or not all(
        type(v) is int and v >= 0 for v in state.values()
    ) or count < state["baseline"]:
        raise Unavailable(f"invalid state {path}")
    return state


def _save_state(path: Path, state: dict[str, int]) -> None:
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".baseline-", suffix=".tmp")  # O_EXCL: never follows a link
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(state, sort_keys=True) + "\n")
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def reprime(run_id: str, seat: str, project_root: Path) -> str:
    """Return the success line; raise Unavailable when nothing can be proven or sent."""
    project = project_root.resolve(strict=True)
    slug = project.name.lower()
    if not _ID.fullmatch(run_id) or not _SLUG.fullmatch(slug):
        raise Unavailable("run id or project name is not a safe path component")
    agent = _live_agent(seat)
    cwd = agent.get("cwd")
    if not isinstance(cwd, str) or not Path(cwd).is_absolute() or not Path(cwd).resolve(strict=True).is_relative_to(project):
        raise Unavailable("roster cwd is not inside --project-root")
    home = Path.home()
    session_file, session_id = _session_file(agent, project, home)
    records = _read_jsonl(session_file)
    count = (_count_claude if agent["agent"] == "claude" else _count_pi)(records, session_id)

    digest = hashlib.sha256(f"{seat}\0{session_id}".encode("utf-8")).hexdigest()
    path = _state_dir(home, slug) / f"baseline-{digest}.json"
    state = _load_state(path, count)
    if state is None:
        _save_state(path, {"baseline": count, "sent": 0})
        return f"no newly crossed threshold for {seat}"
    threshold = state["sent"] + THRESHOLD
    if count - state["baseline"] < threshold:
        return f"no newly crossed threshold for {seat}"

    block = _block(run_id, seat, threshold, slug, home)
    _save_state(path, {**state, "sent": threshold})  # advanced first: a crash never re-prompts
    try:
        sent = herdr_cli.run(["agent", "prompt", seat, block]).returncode == 0
    except herdr_cli.HerdrUnavailable:
        sent = False
    if not sent:
        _save_state(path, state)  # unsent: the next run retries this threshold
        raise Unavailable(f"prompt failed for {seat} at threshold {threshold}")
    suffix = "; relaunch recommended at the next slice boundary" if threshold >= RELAUNCH_THRESHOLD else ""
    return f"prompted {seat} at threshold {threshold}{suffix}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="canonical current run id")
    parser.add_argument("--seat", required=True, help="live Herdr seat name or pane id")
    parser.add_argument("--project-root", required=True, help="absolute project checkout")
    args = parser.parse_args(argv)
    if not Path(args.project_root).is_absolute():
        parser.error("--project-root must be an absolute path")
    try:
        print(f"compaction_reprime: {reprime(args.run_id, args.seat, Path(args.project_root))}")
    except (Unavailable, OSError, UnicodeError) as exc:
        print(f"compaction_reprime: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
