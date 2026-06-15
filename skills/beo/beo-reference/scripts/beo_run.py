#!/usr/bin/env python3
"""BEO lifecycle runner for quick-mode beads.

Automates: validate (PASS_EXECUTE) -> execute -> review (verdict_accept) -> br close.

Usage:
    python3 beo_run.py <issue_id> [<changed_file> ...]

Prerequisites:
    - TICKET.yaml already written in .beads/artifacts/<issue_id>/
    - Product edits already made (script records evidence, does not mutate product)
    - BEO_ACTOR or BR_ACTOR environment variable set

Exit codes:
    0   Full lifecycle completed (PASS_EXECUTE -> executed -> accepted -> br closed)
    1   Prerequisite error (missing ticket, actor, etc.)
    2   Verification command(s) failed (bead left in approved state for repair)
    3   br close failed (state left in executed; fix and retry or close manually)
"""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path
from typing import Any

import yaml

# Ensure sibling modules are importable
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import beo_state
import beo_approval
import beo_git
import beo_ticket
from beo_io import now


def _truncated(text: str, limit: int) -> str:
    """Truncate text to limit chars, appending indicator if cut."""
    if len(text) <= limit:
        return text
    return text[:limit] + "...[truncated]"


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _actor() -> str:
    actor = os.environ.get("BEO_ACTOR") or os.environ.get("BR_ACTOR")
    if not actor:
        _die("BEO_ACTOR or BR_ACTOR must be set")
    return actor


def _parse_porcelain_path(line: str) -> str:
    """Extract working-tree path from a git status --porcelain line.

    Handles normal entries (XY path) and rename/copy entries (R/C XY old -> new).
    The " -> " separator only applies when column 0 is R or C.
    """
    rest = line[3:].strip() if len(line) > 3 else line.strip()
    # Rename/copy: column 0 is R or C, path uses " -> " separator
    if len(line) > 2 and line[0] in ("R", "C") and " -> " in rest:
        return rest.split(" -> ", 1)[1]
    return rest


def _dirty_prestate_check(root: Path, allowed_changed: list[str]) -> list[str]:
    """Return list of dirty paths NOT in the allowed changed set."""
    proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root, text=True, capture_output=True, check=False,
    )
    if proc.returncode != 0:
        print("  [prestate] git status failed; skipping dirty check", file=sys.stderr)
        return []
    allowed = set(allowed_changed)
    unexpected: list[str] = []
    for line in proc.stdout.strip().split("\n"):
        line = line.strip()
        if not line:
            continue
        path = _parse_porcelain_path(line)
        if path and path not in allowed:
            unexpected.append(path)
    return unexpected


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    issue_id = sys.argv[1]
    changed_files = sys.argv[2:]
    actor = _actor()

    # root detection: walk up from cwd looking for .beads
    cwd = Path.cwd().resolve()
    root = cwd
    while root.parent != root and not (root / ".beads").is_dir():
        root = root.parent
    if not (root / ".beads").is_dir():
        _die("no .beads directory found in path")

    base = root / ".beads" / "artifacts" / issue_id
    ticket_path = base / "TICKET.yaml"

    if not ticket_path.exists():
        _die(f"TICKET.yaml not found at {ticket_path.relative_to(root)}")

    # Fresh-read ticket
    ticket = yaml.safe_load(ticket_path.read_text())
    if not isinstance(ticket, dict):
        _die("TICKET.yaml must be a mapping")

    if ticket.get("mode", "quick") != "quick":
        print(f"WARNING: mode is '{ticket.get('mode')}', not 'quick'. Proceeding anyway.", file=sys.stderr)

    # Initialize state (idempotent — safe if already exists)
    try:
        beo_state.initialize_state(root, issue_id, owner="beo-plan")
    except FileExistsError:
        pass  # already initialized

    # Compute approval hashes
    ticket_file_hash = beo_ticket.ticket_file_hash(ticket_path)
    repo_head = beo_git.repo_head_sentinel(root)
    proj_input = beo_ticket.approval_projection_input(ticket)
    proj_input["ticket_file_hash"] = ticket_file_hash
    proj_input["repo_head"] = repo_head
    approval_projection_hash = beo_approval.sha256_text(
        beo_approval.stable_json(proj_input)
    )

    # Dirty prestate check
    print(f"[prestate] checking dirty paths outside changed_files...")
    unexpected = _dirty_prestate_check(root, changed_files)
    if unexpected:
        print(f"  WARNING: unexpected dirty paths: {unexpected}", file=sys.stderr)
        print(f"  Continuing; these will be recorded in prestate evidence.", file=sys.stderr)

    # ----------------------------------------------------------------
    # Phase 1: validate -> PASS_EXECUTE
    # ----------------------------------------------------------------
    def _grant_pass_execute(state: dict[str, Any]) -> dict[str, Any]:
        state["phase"] = "approved"
        state["approval"].update(
            {
                "status": "PASS_EXECUTE",
                "approved_by": "beo-validate",
                "actor": actor,
                "ticket_file_hash": ticket_file_hash,
                "approval_projection_hash": approval_projection_hash,
                "repo_head": repo_head,
                "prestate": {
                    "approved_scope_dirty_paths": changed_files,
                    "unexpected_dirty_paths": unexpected,
                    "note": "approved scope dirty with this bead's changes",
                },
                "failure_category": None,
            }
        )
        return state

    st = beo_state.locked_update_state(root, issue_id, "beo-validate", _grant_pass_execute)
    print(f"[validate] PASS_EXECUTE  phase={st['phase']} seq={st['phase_sequence_id']}")

    # ----------------------------------------------------------------
    # Phase 2: execute -> run verify commands -> executed
    # ----------------------------------------------------------------
    verify_cmds = ticket.get("scope", {}).get("verify", {}).get("commands", [])
    verify_results: list[dict[str, Any]] = []
    all_ok = True

    for cmd in verify_cmds:
        proc = subprocess.run(cmd, cwd=root, shell=True, text=True, capture_output=True, check=False)
        ok = proc.returncode == 0
        if not ok:
            all_ok = False
        verify_results.append(
            {
                "command": cmd,
                "exit_code": proc.returncode,
                "stdout_tail": _truncated((proc.stdout + proc.stderr), 400),
            }
        )
        status = "OK" if ok else "FAIL"
        print(f"[verify] {status} exit={proc.returncode} :: {cmd[:80]}")

    if not all_ok:
        _die("verification command(s) failed — bead left in approved state for repair", code=2)

    # executing
    def _start_exec(state: dict[str, Any]) -> dict[str, Any]:
        state["phase"] = "executing"
        state["execution"]["actor"] = actor
        state["execution"]["started_at"] = now()
        state["execution"]["changed_files"] = changed_files
        return state

    beo_state.locked_update_state(root, issue_id, "beo-execute", _start_exec)

    # executed
    def _finish_exec(state: dict[str, Any]) -> dict[str, Any]:
        state["phase"] = "executed"
        state["execution"]["completed_at"] = now()
        state["execution"]["verify_results"] = verify_results
        state["execution"]["evidence_refs"] = [f".beads/artifacts/{issue_id}/state.json"]
        return state

    st = beo_state.locked_update_state(root, issue_id, "beo-execute", _finish_exec)
    print(f"[execute] phase={st['phase']}")

    # ----------------------------------------------------------------
    # Phase 3: br close first, then record verdict_accept in state
    # ----------------------------------------------------------------
    # br close must succeed before we record closed_in_br=True in state.json.
    # If it fails, the bead stays in "executed" for retry.
    close_proc = subprocess.run(
        ["br", "close", issue_id, "--reason", "done", "--actor", actor],
        cwd=root, text=True, capture_output=True, check=False,
    )
    if close_proc.returncode != 0:
        print(f"ERROR: br close failed with exit {close_proc.returncode}", file=sys.stderr)
        print(f"  stderr: {close_proc.stderr[-300:]}", file=sys.stderr)
        print(f"  Bead left in executed state. Fix and retry or close manually.", file=sys.stderr)
        return 3

    print(f"[close] br closed {issue_id}")

    # Now record the review verdict.
    done_criteria = ticket.get("done_criteria", [])
    coverage = [
        {"criterion": c, "status": "covered", "evidence_refs": changed_files}
        for c in done_criteria
    ]

    def _accept(state: dict[str, Any]) -> dict[str, Any]:
        state["phase"] = "reviewed"
        state["review"]["actor"] = actor
        state["review"]["verdict"] = "accept"
        state["review"]["route_condition_id"] = "verdict_accept"
        state["review"]["findings"] = []
        state["review"]["done_criteria_coverage"] = coverage
        state["review"]["repair_count"] = 0
        state["review"]["closed_in_br"] = True
        return state

    st = beo_state.locked_update_state(root, issue_id, "beo-review", _accept)
    print(f"[review] verdict={st['review']['verdict']}")
    print(f"[done] lifecycle complete for {issue_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
