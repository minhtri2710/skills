#!/usr/bin/env python3
"""Reprime one live seat after compaction (Supervisor-side command).

Resolves the seat from the backend roster, counts the verified compaction markers
in its Claude or Pi session file, and keeps one {baseline, sent} JSON file per
seat-session. The first observation sets the baseline and sends nothing; each
later newly crossed threshold of four markers since baseline sends one
pointer-only prompt.
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
from typing import Sequence

import backend
import runtimes
import state_root


THRESHOLD = 4
RELAUNCH_THRESHOLD = 8
_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
_DOCTRINE = Path(__file__).resolve().parents[1] / "references"


def _live_agent(seats: backend.Backend, seat: str) -> backend.Seat:
    try:
        roster = seats.list_seats()
    except backend.BackendError as exc:
        raise runtimes.Unavailable(f"live roster unavailable: {exc}")
    matches = [a for a in roster if seat in (a.name, a.handle)]
    if len(matches) != 1:
        raise runtimes.Unavailable(f"{seat} is not exactly one live roster seat")
    return matches[0]


def _block(run_id: str, seat: str, threshold: int, slug: str) -> str:
    run_dir = state_root.run_dir(slug, run_id)
    required = [state_root.context_pack(slug), state_root.ledger(slug), state_root.notebook(slug)]
    if not run_dir.is_dir() or not all(p.is_file() for p in required):
        raise runtimes.Unavailable(f"threshold {threshold} remains pending; prompt not attempted")
    lead, supervisor, closeout = (_DOCTRINE / f"{name}.md" for name in ("lead", "supervisor", "closeout"))
    lines = [
        f"run-id: {run_id}", f"seat: {seat}", f"run-dir: {run_dir}",
        f"context-pack: {required[0]}", f"gate-ledger: {required[1]}", f"supervisor-notebook: {required[2]}",
    ]
    for label, name in state_root.RUN_RECORDS.items():
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


def _state_dir(slug: str) -> Path:
    current = state_root.STATE_ROOT
    current.mkdir(parents=True, exist_ok=True)
    for part in state_root.coordination_dir(slug).relative_to(current).parts:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            current.mkdir()
            continue
        if not stat.S_ISDIR(mode):
            raise runtimes.Unavailable(f"{current} is not a plain directory")
    return current


def _load_state(path: Path, count: int) -> dict[str, int] | None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(mode):
        raise runtimes.Unavailable(f"{path} is not a regular file")
    try:
        state = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise runtimes.Unavailable(f"unreadable state {path}")
    if not isinstance(state, dict) or set(state) != {"baseline", "sent"} or not all(
        type(v) is int and v >= 0 for v in state.values()
    ) or count < state["baseline"]:
        raise runtimes.Unavailable(f"invalid state {path}")
    return state


def _save_state(path: Path, state: dict[str, int]) -> None:
    descriptor, temporary = tempfile.mkstemp(dir=path.parent, prefix=".baseline-", suffix=".tmp")
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(state, sort_keys=True) + "\n")
        os.replace(temporary, path)
    except BaseException:
        Path(temporary).unlink(missing_ok=True)
        raise


def reprime(run_id: str, seat: str, project_root: Path, seats: backend.Backend) -> str:
    project = project_root.resolve(strict=True)
    try:
        if not _ID.fullmatch(run_id):
            raise ValueError(run_id)
        slug = state_root.slug_for(project)
    except ValueError:
        raise runtimes.Unavailable("run id or project name is not a safe path component")
    agent = _live_agent(seats, seat)
    cwd = agent.cwd
    if not isinstance(cwd, str) or not Path(cwd).is_absolute() or not Path(cwd).resolve(strict=True).is_relative_to(project):
        raise runtimes.Unavailable("roster cwd is not inside --project-root")
    count, session_id = runtimes.compactions(agent, project, Path.home())

    digest = hashlib.sha256(f"{agent.handle}\0{session_id}".encode("utf-8")).hexdigest()
    path = _state_dir(slug) / f"baseline-{digest}.json"
    state = _load_state(path, count)
    if state is None:
        _save_state(path, {"baseline": count, "sent": 0})
        return f"no newly crossed threshold for {seat}"
    threshold = state["sent"] + THRESHOLD
    if count - state["baseline"] < threshold:
        return f"no newly crossed threshold for {seat}"

    block = _block(run_id, seat, threshold, slug)
    _save_state(path, {**state, "sent": threshold})  # advanced first: a crash never re-prompts
    try:
        seats.prompt(agent.handle, block)
    except backend.BackendError as exc:
        _save_state(path, state)  # unsent: the next run retries this threshold
        raise runtimes.Unavailable(f"prompt failed for {seat} at threshold {threshold}: {exc}")
    suffix = "; relaunch recommended at the next slice boundary" if threshold >= RELAUNCH_THRESHOLD else ""
    return f"prompted {seat} at threshold {threshold}{suffix}"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True, help="canonical current run id")
    parser.add_argument("--seat", required=True, help="live seat name or handle")
    parser.add_argument("--project-root", required=True, help="absolute project checkout")
    backend.add_backend_option(parser)
    args = parser.parse_args(argv)
    if not Path(args.project_root).is_absolute():
        parser.error("--project-root must be an absolute path")
    try:
        seats = backend.open_backend(os.environ, args.backend)
        print(f"compaction_reprime: {reprime(args.run_id, args.seat, Path(args.project_root), seats)}")
    except (runtimes.Unavailable, backend.BackendError, OSError, UnicodeError) as exc:
        print(f"compaction_reprime: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
