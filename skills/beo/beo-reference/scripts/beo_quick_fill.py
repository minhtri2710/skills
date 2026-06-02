#!/usr/bin/env python3
from __future__ import annotations

import sys
import json
import subprocess
from pathlib import Path
from typing import Any

from beo_paths import is_protected_path, normalize_posix_path as normalize_posix, reject_unsafe_path


def get_issue_info(root: Path, issue_id: str) -> tuple[dict[str, Any], str | None]:
    try:
        proc = subprocess.run(
            ["br", "show", issue_id, "--json"],
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            return {}, f"br show exit code {proc.returncode}"
        payload = json.loads(proc.stdout or "{}")
        if isinstance(payload, list) and payload:
            payload = payload[0]
        if isinstance(payload, dict) and isinstance(payload.get("issue"), dict):
            payload = payload["issue"]
        if isinstance(payload, dict):
            return payload, None
    except Exception as exc:
        return {}, str(exc)
    return {}, "issue payload not an object"


def check_protected_paths(root: Path, paths: list[str]) -> list[str]:
    for path in paths:
        reject_unsafe_path(path)

    profiles_path = root / "skills" / "beo" / "beo-reference" / "registry" / "profiles.json"
    if not profiles_path.exists():
        profiles_path = Path(__file__).resolve().parents[1] / "registry" / "profiles.json"
    try:
        profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to load profiles.json: {exc}") from exc
    if not isinstance(profiles, dict):
        raise ValueError("profiles.json must be a JSON object")
    for path in paths:
        if is_protected_path(path, profiles):
            raise ValueError(f"protected path touched: {path}")
    return paths


def main() -> int:
    import argparse
    import yaml
    import beo_ticket

    parser = argparse.ArgumentParser(description="BEO quick-mode TICKET.yaml auto-fill tool")
    parser.add_argument("--issue", required=True, help="Active Bead issue ID")
    parser.add_argument("--root", default=".", help="Workspace root path")
    parser.add_argument("--request", required=True, help="Short request for the quick ticket")
    parser.add_argument("--done-criterion", action="append", required=True, dest="done_criteria", help="Concrete completion criterion; repeatable")
    parser.add_argument("--path", action="append", required=True, dest="paths", help="Explicit allowed scope path; repeatable")
    parser.add_argument("--generated-output", action="append", default=[], dest="generated_outputs", help="Declared generated output path; repeatable")
    parser.add_argument("--verify", action="append", required=True, dest="verify", help="Verification command; repeatable")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing TICKET.yaml; maintenance/authoring only")
    parser.add_argument("--confirm", action="store_true", help="Auto-confirm write without prompt")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    issue, err = get_issue_info(root, args.issue)
    if err:
        print(f"WARNING: br show failed ({err}). Falling back gracefully to empty template placeholders.")
        issue = {}

    issue_type = str(issue.get("issue_type") or issue.get("type") or "atomic")
    if issue_type not in {"atomic", "task", "bug", "story"}:
        print(f"ERROR: Issue {args.issue} is not known atomic enough for Quick Fill: {issue_type}", file=sys.stderr)
        return 1

    try:
        allowed_paths = check_protected_paths(root, args.paths)
        generated_outputs = check_protected_paths(root, args.generated_outputs)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    allowed_paths = [normalize_posix(path) for path in allowed_paths]
    generated_outputs = [normalize_posix(path) for path in generated_outputs]
    if not allowed_paths:
        print("ERROR: No paths declared in scope. Quick-fill cannot generate empty ticket.", file=sys.stderr)
        return 1

    ticket_data = {
        "version": 1,
        "issue_id": str(args.issue),
        "mode": "quick",
        "request": args.request,
        "done_criteria": args.done_criteria,
        "scope": {
            "files": {
                "allow": allowed_paths,
                "forbid": [],
            },
            "generated_outputs": generated_outputs,
            "verify": {
                "commands": args.verify,
            },
        },
    }

    proposed_yaml = yaml.safe_dump(ticket_data, sort_keys=False, default_flow_style=False)
    print("\n--- Proposed Auto-Filled TICKET.yaml Draft ---\n")
    print(proposed_yaml)
    print("----------------------------------------------\n")

    if not args.confirm and sys.stdin.isatty():
        try:
            choice = input("Do you want to write this TICKET.yaml to the active Bead directory? (y/n): ").strip().lower()
            if choice not in {"y", "yes"}:
                print("Aborted.")
                return 0
        except KeyboardInterrupt:
            print("\nAborted.")
            return 1

    try:
        dest_path = beo_ticket.write_ticket(root, args.issue, ticket_data, overwrite=args.overwrite)
        print(f"SUCCESS: Auto-filled TICKET.yaml written to {dest_path.relative_to(root)}")
    except Exception as exc:
        print(f"ERROR: Failed to write TICKET.yaml: {exc}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
