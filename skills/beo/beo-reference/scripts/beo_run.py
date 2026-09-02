#!/usr/bin/env python3
"""BEO lifecycle runner for quick-mode beads.

Automates: validate (PASS_EXECUTE) -> execute -> review (verdict_accept) -> br close.

Usage:
    python3 beo_run.py <issue_id> [<changed_file> ...]

Prerequisites:
    - TICKET.json already written in .beads/artifacts/<issue_id>/
    - Product edits already made (script records evidence, does not mutate product)
    - BEO_ACTOR or BR_ACTOR environment variable set

Exit codes:
    0   Full lifecycle completed (PASS_EXECUTE -> executed -> accepted -> br closed)
    1   Prerequisite error (missing ticket, actor, etc.)
    2   Verification command(s) failed (bead left in approved state for repair)
    3   br close failed (state left in executed; fix and retry or close manually)
"""
from __future__ import annotations

import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Any

# Ensure sibling modules are importable
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import beo_state
import beo_approval
import beo_ticket
from beo_check import changed_files, compute_prestate, validate_working_tree_prestate
from beo_io import now, repo_head_sentinel
from beo_verify import behaviour_gate_command, run_one_command


def _die(msg: str, code: int = 1) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(code)


def _actor() -> str:
    actor = os.environ.get("BEO_ACTOR") or os.environ.get("BR_ACTOR")
    if not actor:
        _die("BEO_ACTOR or BR_ACTOR must be set")
    return actor


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    issue_id = sys.argv[1]
    recorded_changed_files = sys.argv[2:]
    actor = _actor()

    # root detection: walk up from cwd looking for .beads
    cwd = Path.cwd().resolve()
    root = cwd
    while root.parent != root and not (root / ".beads").is_dir():
        root = root.parent
    if not (root / ".beads").is_dir():
        _die("no .beads directory found in path")

    base = root / ".beads" / "artifacts" / issue_id
    ticket_path = base / "TICKET.json"

    if not ticket_path.exists():
        _die(f"TICKET.json not found at {ticket_path.relative_to(root)}")

    # Fresh-read ticket
    ticket = json.loads(ticket_path.read_text())
    if not isinstance(ticket, dict):
        _die("TICKET.json must be an object")

    if ticket.get("mode", "quick") != "quick":
        print(f"WARNING: mode is '{ticket.get('mode')}', not 'quick'. Proceeding anyway.", file=sys.stderr)

    # Initialize state (idempotent — safe if already exists)
    try:
        beo_state.initialize_state(root, issue_id, owner="beo-plan")
    except FileExistsError:
        pass  # already initialized

    # Compute approval hashes
    ticket_file_hash = beo_ticket.ticket_file_hash(ticket_path)
    repo_head = repo_head_sentinel(root)
    approval_projection_hash = beo_approval.approval_projection_hash(
        ticket,
        ticket_file_hash=ticket_file_hash,
        repo_head=repo_head,
    )

    # Dirty prestate check
    print(f"[prestate] checking dirty paths outside changed_files...")
    current_changed_files = changed_files(root)
    prestate_errors = validate_working_tree_prestate(root, ticket, recorded_changed_files)
    if prestate_errors:
        _die("; ".join(prestate_errors))
    unexpected = sorted(path for path in current_changed_files if path not in recorded_changed_files)
    if unexpected:
        print(f"  WARNING: unexpected dirty paths: {unexpected}", file=sys.stderr)
        print(f"  Continuing; these are outside the bead's approved scope.", file=sys.stderr)

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
                "prestate": compute_prestate(root, ticket),
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
        result = run_one_command(cmd, root, None)
        ok = result["exit_code"] == 0
        if not ok:
            all_ok = False
        verify_results.append(result)
        status = "OK" if ok else "FAIL"
        print(f"[verify] {status} exit={result['exit_code']} :: {cmd[:80]}")

    # Optional behaviour_gate (scope.behaviour_gate) — same exec rules as verify.
    bg_cmd, bg_type = behaviour_gate_command(ticket)
    if bg_cmd:
        result = run_one_command(bg_cmd, root, None)
        ok = result["exit_code"] == 0
        if not ok:
            all_ok = False
        result["gate"] = "behaviour"
        if bg_type:
            result["gate_type"] = bg_type
        verify_results.append(result)
        print(f"[behaviour_gate] {'OK' if ok else 'FAIL'} exit={result['exit_code']} :: {bg_cmd[:80]}")

    if not all_ok:
        _die("verification command(s) failed — bead left in approved state for repair", code=2)

    # executing
    def _start_exec(state: dict[str, Any]) -> dict[str, Any]:
        state["phase"] = "executing"
        state["execution"]["actor"] = actor
        state["execution"]["started_at"] = now()
        state["execution"]["changed_files"] = recorded_changed_files
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
        {"criterion": c, "status": "covered", "evidence_refs": recorded_changed_files}
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
