#!/usr/bin/env python3
"""Observe and explicitly reprime one live Herdr seat after compaction.

The Supervisor-side command resolves a live seat from Herdr's roster, counts
only verified durable Claude/Pi markers, persists one per-seat threshold state,
and sends a pointer-only reprime prompt when a new threshold is crossed.
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
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Mapping, Sequence

import herdr_cli


_IDENTIFIER = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
_PROJECT_KEY = re.compile(r"^-[A-Za-z0-9][A-Za-z0-9._-]*$")
_PROJECT_SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
_SESSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")

BASELINE_STATE_VERSION = 1
COMPACTION_THRESHOLD = 4
RELAUNCH_RECOMMEND_THRESHOLD = 8
_STATE_STATUS = {"initialized", "idle", "eligible", "prompting", "failed", "consumed"}
_MISSING = object()


@dataclass(frozen=True)
class SessionRecord:
    """A session path authenticated from one live roster record."""

    seat: str
    agent_name: str | None
    kind: str
    session_id: str
    cwd: Path
    project_root: Path
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
    if cwd is None:
        return None
    try:
        cwd.relative_to(project_root)
    except ValueError:
        return None
    return cwd


def _resolve_pi_session(
    agent: Mapping[str, Any],
    seat: str,
    agent_name: str | None,
    cwd: Path,
    project_root: Path,
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
    return SessionRecord(seat, agent_name, "pi", session_id, cwd, project_root, root, path)


def _resolve_claude_session(
    agent: Mapping[str, Any],
    seat: str,
    agent_name: str | None,
    cwd: Path,
    project_root: Path,
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
    project_key = _project_key(project_root)
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
    return SessionRecord(seat, agent_name, "claude", session_id, cwd, project_root, root, path)


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
        return _resolve_pi_session(agent, seat, agent_name, cwd, project, home)
    return _resolve_claude_session(agent, seat, agent_name, cwd, project, home)


def _parse_jsonl(path: Path) -> list[Mapping[str, Any]] | None:
    records: list[Mapping[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line in stream:
                try:
                    value = json.loads(line)
                except (json.JSONDecodeError, UnicodeDecodeError):
                    if line.endswith("\n"):
                        return None
                    break
                if not isinstance(value, Mapping):
                    return None
                records.append(value)
    except (OSError, UnicodeError):
        return None
    return records


def _authorized_cwd(raw_cwd: object, session: SessionRecord) -> Path | None:
    if not isinstance(raw_cwd, str) or not raw_cwd:
        return None
    record_cwd = _canonical_directory(Path(raw_cwd))
    if record_cwd is None:
        return None
    try:
        record_cwd.relative_to(session.project_root)
    except ValueError:
        return None
    return record_cwd


def _session_header(records: list[Mapping[str, Any]], session: SessionRecord) -> str | None:
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
            if _authorized_cwd(raw_cwd, session) is None:
                return None
        return session.session_id

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
    if _authorized_cwd(raw_cwd, session) is None:
        return None
    return session_id


def _record_matches_session(record: Mapping[str, Any], session: SessionRecord, header_id: str) -> bool:
    record_id = record.get("sessionId")
    if record_id is not None and record_id != header_id:
        return False
    raw_cwd = record.get("cwd")
    if raw_cwd is not None:
        if not isinstance(raw_cwd, str):
            return False
        if _authorized_cwd(raw_cwd, session) is None:
            return False
    return True


def _valid_claude_boundary(record: Mapping[str, Any], session: SessionRecord, header_id: str) -> bool:
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
        and _record_matches_session(record, session, header_id)
    )


def _valid_claude_summary(record: Mapping[str, Any], session: SessionRecord, header_id: str) -> bool:
    return (
        record.get("isCompactSummary") is True
        and isinstance(record.get("sessionId"), str)
        and record.get("sessionId") == header_id
        and isinstance(record.get("uuid"), str)
        and _valid_identifier(record.get("uuid"), _SESSION_ID)
        and isinstance(record.get("cwd"), str)
        and _record_matches_session(record, session, header_id)
    )


def _observe_claude(records: list[Mapping[str, Any]], session: SessionRecord) -> int | None:
    header = _session_header(records, session)
    if header is None:
        return None
    header_id = header
    pending = False
    count = 0
    seen_marker_ids: set[str] = set()
    for record in records:
        is_boundary = record.get("type") == "system" and record.get("subtype") == "compact_boundary"
        is_summary = record.get("isCompactSummary") is True
        if is_boundary:
            if not _valid_claude_boundary(record, session, header_id) or pending:
                return None
            marker_id = record["uuid"]
            if marker_id in seen_marker_ids:
                return None
            seen_marker_ids.add(marker_id)
            pending = True
        elif is_summary:
            if not _valid_claude_summary(record, session, header_id):
                return None
            marker_id = record["uuid"]
            if marker_id in seen_marker_ids or not pending:
                return None
            seen_marker_ids.add(marker_id)
            count += 1
            pending = False
    return None if pending else count


def _valid_pi_compaction(record: Mapping[str, Any], session: SessionRecord, header_id: str) -> bool:
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
        and _record_matches_session(record, session, header_id)
    )


def _observe_pi(records: list[Mapping[str, Any]], session: SessionRecord) -> int | None:
    header = _session_header(records, session)
    if header is None:
        return None
    header_id = header
    seen_ids: set[str] = set()
    count = 0
    for record in records[1:]:
        if record.get("type") != "compaction":
            continue
        if not _valid_pi_compaction(record, session, header_id):
            return None
        record_id = record["id"]
        if record_id in seen_ids:
            return None
        seen_ids.add(record_id)
        count += 1
    return count


def _verified_observation(session: SessionRecord | None) -> int | None:
    if session is None:
        return None
    path = _canonical_file(session.session_path, session.session_root)
    if path is None or path != session.session_path:
        return None
    records = _parse_jsonl(path)
    if records is None:
        return None
    if session.kind == "claude":
        return _observe_claude(records, session)
    if session.kind == "pi":
        return _observe_pi(records, session)
    return None


@dataclass(frozen=True)
class BaselineState:
    """The one validated durable baseline record for a live seat."""

    schema_version: int
    project_slug: str
    run_id: str
    seat: str
    kind: str
    session_id: str
    session_path: str
    cwd: str
    baseline_count: int
    observed_count: int
    next_threshold: int
    consumed_threshold: int
    eligible_threshold: int | None
    prompt_status: str


@dataclass(frozen=True)
class BaselineResult:
    """The state after one verified observation and its newly crossed threshold."""

    state: BaselineState
    state_path: Path
    newly_observed: int
    newly_eligible_threshold: int | None

    @property
    def baseline_count(self) -> int:
        return self.state.baseline_count

    @property
    def observed_count(self) -> int:
        return self.state.observed_count

    @property
    def next_threshold(self) -> int:
        return self.state.next_threshold

    @property
    def consumed_threshold(self) -> int:
        return self.state.consumed_threshold

    @property
    def eligible_threshold(self) -> int | None:
        """Return the durable threshold awaiting the later dispatch slice."""
        return self.state.eligible_threshold

    @property
    def pending_threshold(self) -> int | None:
        return self.state.eligible_threshold

    @property
    def eligible(self) -> bool:
        return self.newly_eligible_threshold is not None


@dataclass(frozen=True)
class ReprimePaths:
    """Canonical durable pointers allowed in a reprime prompt."""

    context_pack: Path
    gates: Path
    notebook: Path
    run_dir: Path
    intake: Path | None
    plan: Path | None
    specification: Path | None
    slices: Path | None
    lead_doctrine: Path
    supervisor_doctrine: Path
    closeout_doctrine: Path


@dataclass(frozen=True)
class ReprimeDispatchResult:
    """The durable state and outcome of one threshold dispatch attempt."""

    state: BaselineState
    state_path: Path
    threshold: int | None
    prompt_attempted: bool
    prompt_succeeded: bool
    block: str | None
    outcome_unknown: bool = False

    @property
    def retryable(self) -> bool:
        return self.prompt_attempted and not self.prompt_succeeded and self.threshold is not None


def _project_slug(project: Path) -> str | None:
    slug = project.name.lower()
    return slug if _PROJECT_SLUG.fullmatch(slug) is not None else None


def _canonical_child(path: Path, root: Path, *, directory: bool) -> Path | None:
    if not path.is_absolute():
        return None
    try:
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if resolved != path or not _contained(root, resolved):
        return None
    try:
        mode = resolved.stat().st_mode
    except OSError:
        return None
    if directory:
        return resolved if stat.S_ISDIR(mode) else None
    return resolved if stat.S_ISREG(mode) else None


def _validated_reprime_paths(
    project: Path,
    home: Path,
    run_id: str,
) -> ReprimePaths | None:
    project_slug = _project_slug(project)
    if project_slug is None or not _valid_identifier(run_id, _SESSION_ID):
        return None

    records_root = home / ".herdr" / "projects" / project_slug
    records_root = _canonical_child(records_root, home, directory=True)
    if records_root is None:
        return None
    runs_root = _canonical_child(records_root / "runs", records_root, directory=True)
    run_root = _canonical_child(runs_root / run_id, runs_root, directory=True) if runs_root else None
    if run_root is None:
        return None

    project_files = {
        "context_pack": home / ".herdr" / "projects" / project_slug / "context-pack.md",
        "gates": home / ".herdr" / "projects" / project_slug / "gates.md",
        "notebook": home / ".herdr" / "projects" / project_slug / "supervisor-notebook.md",
    }
    run_files = {
        "intake": run_root / "intake-record.md",
        "plan": run_root / "plan.md",
        "specification": run_root / "specification.md",
        "slices": run_root / "slices.json",
    }
    canonical_project_files: dict[str, Path] = {}
    for name, path in project_files.items():
        resolved = _canonical_child(path, records_root, directory=False)
        if resolved is None:
            return None
        canonical_project_files[name] = resolved
    canonical_run_files: dict[str, Path | None] = {}
    for name, path in run_files.items():
        if not os.path.lexists(path):
            canonical_run_files[name] = None
            continue
        resolved = _canonical_child(path, run_root, directory=False)
        if resolved is None:
            return None
        canonical_run_files[name] = resolved

    skill_root = Path(__file__).resolve().parents[1]
    doctrine_root = _canonical_child(skill_root / "references", skill_root, directory=True)
    if doctrine_root is None:
        return None
    doctrine: dict[str, Path] = {}
    for name in ("lead_doctrine", "supervisor_doctrine", "closeout_doctrine"):
        filename = {
            "lead_doctrine": "lead.md",
            "supervisor_doctrine": "supervisor.md",
            "closeout_doctrine": "closeout.md",
        }[name]
        resolved = _canonical_child(doctrine_root / filename, doctrine_root, directory=False)
        if resolved is None:
            return None
        doctrine[name] = resolved

    return ReprimePaths(
        context_pack=canonical_project_files["context_pack"],
        gates=canonical_project_files["gates"],
        notebook=canonical_project_files["notebook"],
        run_dir=run_root,
        intake=canonical_run_files["intake"],
        plan=canonical_run_files["plan"],
        specification=canonical_run_files["specification"],
        slices=canonical_run_files["slices"],
        lead_doctrine=doctrine["lead_doctrine"],
        supervisor_doctrine=doctrine["supervisor_doctrine"],
        closeout_doctrine=doctrine["closeout_doctrine"],
    )


def build_reprime_block(
    *,
    run_id: str,
    seat: str,
    threshold: int,
    project_root: str | os.PathLike[str],
    home_dir: str | os.PathLike[str] | None = None,
) -> str | None:
    """Build a prompt block containing only validated durable pointers."""
    if not _valid_identifier(run_id, _SESSION_ID) or not _valid_identifier(seat):
        return None
    project = _canonical_directory(Path(project_root))
    home = _validated_home(home_dir)
    if project is None or home is None:
        return None
    pointers = _validated_reprime_paths(project, home, run_id)
    if pointers is None:
        return None
    lines = [
        f"run-id: {run_id}",
        f"seat: {seat}",
        f"run-dir: {pointers.run_dir}",
        f"context-pack: {pointers.context_pack}",
        f"gate-ledger: {pointers.gates}",
        f"supervisor-notebook: {pointers.notebook}",
    ]
    for label, path in (
        ("intake", pointers.intake),
        ("plan", pointers.plan),
        ("specification", pointers.specification),
        ("slices", pointers.slices),
    ):
        if path is not None:
            lines.append(f"{label}: {path}")
    lines.extend(
        (
            f"lead-recovery: {pointers.lead_doctrine}#Recovery",
            f"lead-delivery: {pointers.lead_doctrine}#Delivery sequence",
            f"lead-gates: {pointers.lead_doctrine}#Gates and ledger",
            f"supervisor-handoff: {pointers.supervisor_doctrine}#Handoff",
            f"closeout: {pointers.closeout_doctrine}#Acceptance custody",
        )
    )
    if threshold >= RELAUNCH_RECOMMEND_THRESHOLD:
        lines.append(
            f"relaunch-recommended: {threshold} compactions since baseline; "
            f"at the next slice boundary: {pointers.lead_doctrine}#Relaunch and doctrine"
        )
    return "\n".join(lines)


def _validated_home(home_dir: str | os.PathLike[str] | None) -> Path | None:
    raw_home = home_dir if home_dir is not None else os.environ.get("HOME")
    if not isinstance(raw_home, (str, os.PathLike)) or not str(raw_home):
        return None
    return _canonical_directory(Path(raw_home))


def _validated_state_root(home: Path, project_slug: str) -> Path | None:
    """Create and validate the only directory in which baseline state may live."""
    if _PROJECT_SLUG.fullmatch(project_slug) is None:
        return None
    current = home
    for component in (".herdr", "projects", project_slug, "runs", "coordination"):
        candidate = current / component
        try:
            info = os.lstat(candidate)
        except FileNotFoundError:
            try:
                candidate.mkdir()
                info = os.lstat(candidate)
            except OSError:
                return None
        except OSError:
            return None
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            return None
        current = candidate

    try:
        resolved = current.resolve(strict=True)
    except (OSError, RuntimeError):
        return None
    if resolved != current or not _contained(home, resolved):
        return None
    return resolved


def _state_path(root: Path, seat: str) -> Path | None:
    if not _valid_identifier(seat):
        return None
    digest = hashlib.sha256(seat.encode("utf-8")).hexdigest()
    path = root / f"baseline-{digest}.json"
    if not _contained(root, path):
        return None
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return path
    except OSError:
        return None
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        return None
    return path


def _is_nonnegative_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _state_payload(state: BaselineState) -> dict[str, Any]:
    return {
        "schema_version": state.schema_version,
        "project_slug": state.project_slug,
        "run_id": state.run_id,
        "seat": state.seat,
        "kind": state.kind,
        "session_id": state.session_id,
        "session_path": state.session_path,
        "cwd": state.cwd,
        "baseline_count": state.baseline_count,
        "observed_count": state.observed_count,
        "next_threshold": state.next_threshold,
        "consumed_threshold": state.consumed_threshold,
        "eligible_threshold": state.eligible_threshold,
        "prompt_status": state.prompt_status,
    }


def _decode_state(
    payload: Any,
    session: SessionRecord,
    project_slug: str,
) -> BaselineState | None:
    if not isinstance(payload, Mapping):
        return None
    expected = {
        "schema_version", "project_slug", "run_id", "seat", "kind", "session_id",
        "session_path", "cwd", "baseline_count", "observed_count", "next_threshold",
        "consumed_threshold", "eligible_threshold", "prompt_status",
    }
    if set(payload) != expected:
        return None
    if not _is_nonnegative_int(payload.get("schema_version")) or payload["schema_version"] != BASELINE_STATE_VERSION:
        return None
    string_fields = ("project_slug", "run_id", "seat", "kind", "session_id", "session_path", "cwd", "prompt_status")
    if any(not isinstance(payload.get(field), str) for field in string_fields):
        return None
    if (
        payload["project_slug"] != project_slug
        or not _PROJECT_SLUG.fullmatch(payload["project_slug"])
        or not _valid_identifier(payload["run_id"], _SESSION_ID)
        or not _valid_identifier(payload["seat"])
        or payload["seat"] != session.seat
        or payload["kind"] != session.kind
        or payload["session_id"] != session.session_id
        or payload["session_path"] != str(session.session_path)
        or payload["cwd"] != str(session.cwd)
        or payload["prompt_status"] not in _STATE_STATUS
    ):
        return None
    integer_fields = ("baseline_count", "observed_count", "next_threshold", "consumed_threshold")
    if any(not _is_nonnegative_int(payload.get(field)) for field in integer_fields):
        return None
    eligible = payload["eligible_threshold"]
    if eligible is not None and not _is_nonnegative_int(eligible):
        return None
    baseline = payload["baseline_count"]
    observed = payload["observed_count"]
    next_threshold = payload["next_threshold"]
    consumed = payload["consumed_threshold"]
    if observed < baseline or consumed % COMPACTION_THRESHOLD:
        return None
    if eligible is not None and (
        eligible == 0 or eligible % COMPACTION_THRESHOLD or eligible <= consumed
    ):
        return None
    active_threshold = eligible if eligible is not None else consumed
    newly_available = observed - baseline
    if newly_available < active_threshold:
        return None
    if eligible is None and newly_available >= next_threshold and payload["prompt_status"] != "consumed":
        return None
    if next_threshold != active_threshold + COMPACTION_THRESHOLD:
        return None
    if payload["prompt_status"] == "initialized":
        if observed != baseline or consumed != 0 or eligible is not None or next_threshold != COMPACTION_THRESHOLD:
            return None
    elif payload["prompt_status"] == "idle":
        if eligible is not None:
            return None
    elif payload["prompt_status"] == "consumed":
        if eligible is not None or consumed == 0:
            return None
    elif payload["prompt_status"] in {"failed", "prompting"}:
        if eligible is None:
            return None
    elif payload["prompt_status"] == "eligible":
        if eligible is None:
            return None
    else:
        return None
    return BaselineState(
        schema_version=payload["schema_version"],
        project_slug=payload["project_slug"],
        run_id=payload["run_id"],
        seat=payload["seat"],
        kind=payload["kind"],
        session_id=payload["session_id"],
        session_path=payload["session_path"],
        cwd=payload["cwd"],
        baseline_count=baseline,
        observed_count=observed,
        next_threshold=next_threshold,
        consumed_threshold=consumed,
        eligible_threshold=eligible,
        prompt_status=payload["prompt_status"],
    )


def _read_state(
    path: Path,
    session: SessionRecord,
    project_slug: str,
) -> BaselineState | None | object:
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        return _MISSING
    except OSError:
        return None
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        return None
    try:
        with path.open("r", encoding="utf-8") as stream:
            payload = json.load(stream)
    except (OSError, UnicodeError, json.JSONDecodeError):
        return None
    return _decode_state(payload, session, project_slug)


def _write_state(root: Path, path: Path, state: BaselineState) -> bool:
    if path.parent != root or not _contained(root, path):
        return False
    try:
        info = os.lstat(path)
    except FileNotFoundError:
        info = None
    except OSError:
        return False
    if info is not None and (stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode)):
        return False

    temporary: Path | None = None
    descriptor: int | None = None
    try:
        descriptor, raw_temporary = tempfile.mkstemp(
            prefix=f".{path.stem}-", suffix=".tmp", dir=str(root)
        )
        temporary = Path(raw_temporary)
        if temporary.parent != root or not _contained(root, temporary):
            return False
        temporary_info = os.lstat(temporary)
        if stat.S_ISLNK(temporary_info.st_mode) or not stat.S_ISREG(temporary_info.st_mode):
            return False
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = None
            json.dump(_state_payload(state), stream, sort_keys=True, separators=(",", ":"))
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        try:
            target_info = os.lstat(path)
        except FileNotFoundError:
            target_info = None
        if target_info is not None and (stat.S_ISLNK(target_info.st_mode) or not stat.S_ISREG(target_info.st_mode)):
            return False
        os.replace(temporary, path)
        temporary = None
        final_info = os.lstat(path)
        return stat.S_ISREG(final_info.st_mode) and not stat.S_ISLNK(final_info.st_mode)
    except (OSError, TypeError, ValueError):
        return False
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass


def track_live_seat(
    roster: Any,
    seat: str,
    *,
    run_id: str,
    project_root: str | os.PathLike[str],
    home_dir: str | os.PathLike[str] | None = None,
) -> BaselineResult | None:
    """Persist one verified seat baseline and report a newly crossed threshold.

    ``None`` means the live identity, marker evidence, state root, or state
    record could not be proven.  No in-memory or alternate state is used.
    """
    if not _valid_identifier(run_id, _SESSION_ID):
        return None
    session = resolve_live_session(roster, seat, project_root=project_root, home_dir=home_dir)
    observation = _verified_observation(session)
    if session is None or observation is None:
        return None
    project = _canonical_directory(Path(project_root))
    home = _validated_home(home_dir)
    if project is None or home is None:
        return None
    project_slug = _project_slug(project)
    if project_slug is None:
        return None
    root = _validated_state_root(home, project_slug)
    if root is None:
        return None
    path = _state_path(root, session.seat)
    if path is None:
        return None
    existing = _read_state(path, session, project_slug)
    if existing is None:
        return None

    newly_eligible: int | None = None
    if existing is _MISSING:
        state = BaselineState(
            schema_version=BASELINE_STATE_VERSION,
            project_slug=project_slug,
            run_id=run_id,
            seat=session.seat,
            kind=session.kind,
            session_id=session.session_id,
            session_path=str(session.session_path),
            cwd=str(session.cwd),
            baseline_count=observation,
            observed_count=observation,
            next_threshold=COMPACTION_THRESHOLD,
            consumed_threshold=0,
            eligible_threshold=None,
            prompt_status="initialized",
        )
    else:
        if observation < existing.observed_count:
            return None
        newly_observed = observation - existing.observed_count
        eligible = existing.eligible_threshold
        next_threshold = existing.next_threshold
        status = existing.prompt_status
        if eligible is None and observation - existing.baseline_count >= next_threshold:
            newly_eligible = next_threshold
            eligible = newly_eligible
            next_threshold += COMPACTION_THRESHOLD
            status = "eligible"
        elif eligible is not None:
            status = existing.prompt_status
        elif status == "initialized":
            status = "idle"
        state = BaselineState(
            schema_version=existing.schema_version,
            project_slug=existing.project_slug,
            run_id=run_id,
            seat=existing.seat,
            kind=existing.kind,
            session_id=existing.session_id,
            session_path=existing.session_path,
            cwd=existing.cwd,
            baseline_count=existing.baseline_count,
            observed_count=observation,
            next_threshold=next_threshold,
            consumed_threshold=existing.consumed_threshold,
            eligible_threshold=eligible,
            prompt_status=status,
        )
    if not _write_state(root, path, state):
        return None
    newly_observed = 0 if existing is _MISSING else observation - existing.observed_count
    return BaselineResult(state, path, newly_observed, newly_eligible)


def dispatch_live_seat(
    roster: Any,
    seat: str,
    *,
    run_id: str,
    project_root: str | os.PathLike[str],
    home_dir: str | os.PathLike[str] | None = None,
) -> ReprimeDispatchResult | None:
    """Prompt one validated live seat for its durable pending threshold.

    The baseline result is the sole source of threshold state.  A pending
    threshold is retried after a failed prompt and is consumed only after the
    exact Herdr prompt returns success.  The ``prompting`` status is written
    before the prompt; a run that finds it consumes the threshold without
    prompting, because the earlier outcome is unknown.  No other command or
    target is used.
    """
    result = track_live_seat(
        roster,
        seat,
        run_id=run_id,
        project_root=project_root,
        home_dir=home_dir,
    )
    if result is None:
        return None
    threshold = result.state.eligible_threshold
    if threshold is None:
        return ReprimeDispatchResult(result.state, result.state_path, None, False, False, None)
    if result.state.prompt_status == "prompting":
        consumed = replace(
            result.state,
            consumed_threshold=threshold,
            eligible_threshold=None,
            prompt_status="consumed",
        )
        if not _write_state(result.state_path.parent, result.state_path, consumed):
            return None
        return ReprimeDispatchResult(consumed, result.state_path, threshold, False, False, None, True)

    block = build_reprime_block(
        run_id=run_id,
        seat=seat,
        threshold=threshold,
        project_root=project_root,
        home_dir=home_dir,
    )
    if block is None:
        return ReprimeDispatchResult(result.state, result.state_path, threshold, False, False, None)

    prompting = replace(result.state, prompt_status="prompting")
    if not _write_state(result.state_path.parent, result.state_path, prompting):
        return None
    try:
        prompt_result = herdr_cli.run(["agent", "prompt", seat, block])
        prompt_succeeded = prompt_result.returncode == 0
    except herdr_cli.HerdrUnavailable:
        prompt_succeeded = False

    status = "consumed" if prompt_succeeded else "failed"
    updated = replace(
        prompting,
        consumed_threshold=threshold if prompt_succeeded else result.state.consumed_threshold,
        eligible_threshold=None if prompt_succeeded else threshold,
        prompt_status=status,
    )
    if not _write_state(result.state_path.parent, result.state_path, updated):
        return None
    return ReprimeDispatchResult(
        updated,
        result.state_path,
        threshold,
        True,
        prompt_succeeded,
        block,
    )


def _load_live_roster() -> Any | None:
    try:
        result = herdr_cli.run(["agent", "list"])
    except herdr_cli.HerdrUnavailable:
        return None
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except (json.JSONDecodeError, TypeError):
        return None


def main(argv: Sequence[str] | None = None) -> int:
    """Run one explicit Supervisor-side observation and optional reprime."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="canonical current run id")
    parser.add_argument("--seat", required=True, help="live Herdr seat name or pane id")
    parser.add_argument("--project-root", required=True, help="absolute project checkout")
    args = parser.parse_args(argv)
    if not Path(args.project_root).is_absolute():
        parser.error("--project-root must be an absolute path")

    roster = _load_live_roster()
    if roster is None:
        print("compaction_reprime: live Herdr roster unavailable", file=sys.stderr)
        return 1

    result = dispatch_live_seat(
        roster,
        args.seat,
        run_id=args.run_id,
        project_root=args.project_root,
        home_dir=os.environ.get("HOME"),
    )
    if result is None:
        print("compaction_reprime: observation or state validation failed closed", file=sys.stderr)
        return 1
    if result.threshold is None:
        print(f"compaction_reprime: no newly crossed threshold for {args.seat}")
        return 0
    if result.outcome_unknown:
        print(
            f"compaction_reprime: {args.seat} threshold {result.threshold} outcome unknown; not re-prompted",
            file=sys.stderr,
        )
        return 1
    if not result.prompt_attempted:
        print(
            f"compaction_reprime: threshold {result.threshold} remains pending; prompt not attempted",
            file=sys.stderr,
        )
        return 1
    if not result.prompt_succeeded:
        print(
            f"compaction_reprime: prompt failed for {args.seat} at threshold {result.threshold}",
            file=sys.stderr,
        )
        return 1
    suffix = "; relaunch recommended at the next slice boundary" if result.threshold >= RELAUNCH_RECOMMEND_THRESHOLD else ""
    print(f"compaction_reprime: prompted {args.seat} at threshold {result.threshold}{suffix}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
