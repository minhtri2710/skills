#!/usr/bin/env python3
"""BEO verification runner for atomic beads.

Runs TICKET.yaml.scope.verify.commands and records per-command results to
runtime-events.jsonl. Returns the results in JSON for the caller
(beo-execute, beo-review) to durably record into state.json.execution.verify_results.

This script NEVER writes to state.json (read-only mode). Only
runtime-events.jsonl is appended to, and only as a best-effort advisory log.

CLI:
    python3 beo_verify.py run --issue <id> [--root .]   # single bead (default subcommand)
    python3 beo_verify.py --all [--root .]              # all approved/executing/executed beads

Exit codes:
    0  all verifications pass (or all skipped for missing worktree)
    1  at least one verification failed (exit_code != 0)
    2  refuse to run (state.phase=planned, missing ticket, or missing state.json)
"""
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

HELPER_VERSION = "beo-verify/v1"
ACTOR = "beo-verify"
EXECUTABLE_PHASES = {"approved", "executing", "executed"}

# Ensure sibling modules are importable when run as a script.
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from beo_io import now
from beo_state import append_event, read_state
from beo_ticket import read_ticket
from beo_approval import verify_commands


def _run_one_command(command: str, cwd: Path, worktree_path: str | None) -> dict[str, Any]:
    """Execute one verify command and return a per-command result entry.

    The command is tokenized with shlex and executed without a shell so that
    metacharacters in a verify command cannot trigger arbitrary execution.
    TICKET.yaml is human-approved, but the harness should not rely on the
    author to sanitize their own commands.
    """
    ran_at = now()
    start = time.monotonic()
    argv = shlex.split(command)
    if not argv:
        # An empty command is a ticket misconfiguration; treat it as a
        # failure (exit_code -1) so the bead does not pass verification.
        # The empty "command" string itself is the diagnostic.
        return {
            "command": command,
            "exit_code": -1,
            "duration_ms": int((time.monotonic() - start) * 1000),
            "ran_at": ran_at,
            "worktree_path": worktree_path,
        }
    try:
        proc = subprocess.run(
            argv,
            cwd=cwd,
            shell=False,
            text=True,
            capture_output=True,
            check=False,
        )
        exit_code = proc.returncode
    except FileNotFoundError:
        exit_code = -1
    duration_ms = int((time.monotonic() - start) * 1000)
    return {
        "command": command,
        "exit_code": exit_code,
        "duration_ms": duration_ms,
        "ran_at": ran_at,
        "worktree_path": worktree_path,
    }


def _skipped_result(command: str, reason: str) -> dict[str, Any]:
    """Build a skipped per-command result entry."""
    return {
        "command": command,
        "exit_code": -1,
        "duration_ms": 0,
        "ran_at": now(),
        "worktree_path": None,
        "status": "skipped",
        "skip_reason": reason,
    }


def _emit_event(root: Path, issue_id: str, result: dict[str, Any], outcome: str) -> None:
    """Append a verification_run event. Best-effort; never raises."""
    event = {
        "issue_id": issue_id,
        "kind": "verification_run",
        "phase": "executing",
        "actor": ACTOR,
        "timestamp": now(),
        "payload": {
            "command": result["command"],
            "outcome": outcome,
            "exit_code": result.get("exit_code", -1),
            "ran_at": result["ran_at"],
            "duration_ms": result.get("duration_ms", 0),
            "worktree_path": result.get("worktree_path"),
        },
    }
    try:
        append_event(root, issue_id, event)
    except Exception as exc:
        # Event append is best-effort. The returned results are authoritative;
        # the caller writes them into state.json.
        print(f"warning: failed to append verification_run event: {exc}", file=sys.stderr)


def _resolve_run_target(root: Path, ticket: dict[str, Any], issue_id: str) -> tuple[Path, str | None, bool]:
    """Resolve where to run commands.

    Returns (cwd, worktree_path, worktree_missing). When worktree_isolation
    is true but the worktree directory does not exist, returns
    (root, None, True) so the caller emits skipped results for every command.
    """
    strict = ticket.get("strict") if isinstance(ticket.get("strict"), dict) else {}
    if not bool(strict.get("worktree_isolation")):
        return root, None, False
    from beo_worktree import worktree_path as wt_path_for
    wt_path = wt_path_for(issue_id)
    if wt_path.is_dir():
        return wt_path, str(wt_path), False
    return root, None, True


def verify_issue(root: Path, issue_id: str) -> dict[str, Any]:
    """Run verification for a single issue.

    Returns a per-issue result dict with keys: ok, refused, refusal_reason,
    issue_id, issue_results (list of per-command results), and summary.
    """
    refusal: dict[str, Any] = {
        "ok": False,
        "refused": True,
        "refusal_reason": None,
        "issue_id": issue_id,
        "issue_results": [],
        "summary": {"pass": 0, "fail": 0, "skipped": 0},
    }
    try:
        ticket = read_ticket(root, issue_id).data
    except FileNotFoundError as exc:
        return {**refusal, "refusal_reason": f"ticket_missing: {exc}"}
    except Exception as exc:
        return {**refusal, "refusal_reason": f"ticket_invalid: {exc}"}
    try:
        state = read_state(root, issue_id)
    except FileNotFoundError as exc:
        return {**refusal, "refusal_reason": f"state_missing: {exc}"}
    except Exception as exc:
        return {**refusal, "refusal_reason": f"state_invalid: {exc}"}

    if state.get("phase") == "planned":
        return {**refusal, "refusal_reason": "state.phase is planned; PASS_EXECUTE required"}

    commands = verify_commands(ticket)
    cwd, worktree_path, worktree_missing = _resolve_run_target(root, ticket, issue_id)

    summary = {"pass": 0, "fail": 0, "skipped": 0}
    results: list[dict[str, Any]] = []
    for command in commands:
        if worktree_missing:
            result = _skipped_result(command, "worktree_missing")
            results.append(result)
            summary["skipped"] += 1
            _emit_event(root, issue_id, result, "skipped")
            continue
        result = _run_one_command(command, cwd, worktree_path)
        results.append(result)
        outcome = "pass" if result["exit_code"] == 0 else "fail"
        summary[outcome] += 1
        _emit_event(root, issue_id, result, outcome)

    return {
        "ok": summary["fail"] == 0,
        "refused": False,
        "refusal_reason": None,
        "issue_id": issue_id,
        "issue_results": results,
        "summary": summary,
    }


def discover_beads(root: Path) -> list[str]:
    """Scan .beads/artifacts/*/state.json for phases in EXECUTABLE_PHASES.

    Directories without a readable state.json are skipped silently; we never
    fail the --all run for a single missing artifact directory.
    """
    artifacts = root / ".beads" / "artifacts"
    if not artifacts.is_dir():
        return []
    found: list[str] = []
    for entry in sorted(artifacts.iterdir()):
        if not entry.is_dir():
            continue
        state_path = entry / "state.json"
        if not state_path.is_file():
            continue
        try:
            data = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(data, dict):
            continue
        if data.get("phase") not in EXECUTABLE_PHASES:
            continue
        issue_id = data.get("issue_id")
        if isinstance(issue_id, str) and issue_id:
            found.append(issue_id)
    return found


def _print_json(payload: dict[str, Any]) -> None:
    print(json.dumps(payload, indent=2, sort_keys=True))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="BEO verification runner",
        epilog=(
            "VERIFY COMMAND SECURITY: Each verify command is exec'd directly via execve "
            "(shell=False, no shell interpreter). Pipes, redirects, &&, ||, ;, and "
            "env-var expansion are NOT supported. For multi-step commands, list them as "
            "separate items in scope.verify.commands in TICKET.yaml."
        ),
    )
    parser.add_argument("--all", action="store_true", help="Run all atomic beads with executable phases")
    parser.add_argument("--issue", help="Single issue id (used with the default 'run' subcommand)")
    parser.add_argument("--root", default=".", help="Repo root")
    parser.add_argument(
        "subcommand",
        nargs="?",
        default="run",
        choices=["run"],
        help="Subcommand (default: run)",
    )
    args = parser.parse_args()
    root = Path(args.root).resolve()

    if args.all:
        issue_ids = discover_beads(root)
        per_issue: list[dict[str, Any]] = []
        any_fail = False
        any_refuse = False
        agg = {"pass": 0, "fail": 0, "skipped": 0}
        for issue_id in issue_ids:
            result = verify_issue(root, issue_id)
            per_issue.append(result)
            if result.get("refused"):
                any_refuse = True
            elif not result["ok"]:
                any_fail = True
            for key in agg:
                agg[key] += result["summary"][key]
        _print_json({
            "ok": not (any_fail or any_refuse),
            "issue_id": None,
            "issue_results": per_issue,
            "summary": agg,
        })
        if any_refuse:
            return 2
        return 1 if any_fail else 0

    if not args.issue:
        print("error: --issue is required (or use --all)", file=sys.stderr)
        return 1
    result = verify_issue(root, args.issue)
    _print_json({
        "ok": result["ok"],
        "issue_id": result["issue_id"],
        "issue_results": result["issue_results"],
        "summary": result["summary"],
        "refused": result.get("refused", False),
        "refusal_reason": result.get("refusal_reason"),
    })
    if result.get("refused"):
        return 2
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
