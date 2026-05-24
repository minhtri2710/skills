#!/usr/bin/env python3
from __future__ import annotations

import sys
import json
import subprocess
from pathlib import Path
from typing import Any

from beo_utils import load_json, normalize_posix, run_cmd

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

def get_git_diff_paths(root: Path) -> list[str]:
    paths = set()
    for command in [["git", "diff", "--name-only"], ["git", "diff", "--cached", "--name-only"]]:
        code, stdout, stderr = run_cmd(command, cwd=root)
        if code == 0:
            for line in stdout.splitlines():
                if line.strip():
                    paths.add(normalize_posix(line.strip()))
    return sorted(list(paths))

def filter_protected_paths(root: Path, paths: list[str]) -> list[str]:
    # Load profiles.json
    profiles_path = root / "skills" / "beo" / "reference" / "registry" / "profiles.json"
    if not profiles_path.exists():
        profiles_path = Path(__file__).resolve().parents[1] / "registry" / "profiles.json"
    profiles = load_json(profiles_path, {})
    protected_patterns = profiles.get("protected_path_defaults", [])
    
    import fnmatch
    filtered = []
    for path in paths:
        is_protected = False
        for pattern in protected_patterns:
            if fnmatch.fnmatch(path, pattern):
                is_protected = True
                break
        if not is_protected:
            filtered.append(path)
    return filtered

def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="BEO Quick-mode TICKET.md auto-fill tool")
    parser.add_argument("--issue", required=True, help="Active Bead issue ID")
    parser.add_argument("--root", default=".", help="Workspace root path")
    parser.add_argument("--confirm", action="store_true", help="Auto-confirm write without prompt")
    args = parser.parse_args()
    
    root = Path(args.root).resolve()
    
    # 1. Fetch active issue info
    issue, err = get_issue_info(root, args.issue)
    if err:
        print(f"WARNING: br show failed ({err}). Falling back gracefully to empty template placeholders.")
        issue = {}
        
    issue_title = str(issue.get("title", f"Fix issue {args.issue}"))
    
    # 2. Fetch git diff paths
    diff_paths = get_git_diff_paths(root)
    allowed_paths = filter_protected_paths(root, diff_paths)
    if not allowed_paths:
        allowed_paths = ["<path>"]
        
    # 3. Build Ticket content
    ticket_yaml = f"""```yaml beo.ticket
schema_version: beo-beads/v3
issue_id: {json.dumps(str(args.issue))}
mode: quick
request: {json.dumps(issue_title)}
done_target: {json.dumps(issue_title)}
done:
  - {json.dumps(f"{issue_title} matches requirements.")}
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
"""
    for p in allowed_paths:
        ticket_yaml += f"      - {json.dumps(str(p))}\n"
        
    ticket_yaml += """    forbid: []
  verify:
    commands:
      - git diff --check
acceptance_criteria:
  - "Verify that all changes are fully within the allowed files."
atomicity:
  decision: atomic
  reason: "One bounded repo-only edit."
  rejects_multi_task: true
generated_outputs: []
```
"""
    
    print("\n--- Proposed Auto-Filled TICKET.md Draft ---\n")
    print(ticket_yaml)
    print("--------------------------------------------\n")
    
    # 4. Human Confirmation Gate
    if not args.confirm and sys.stdin.isatty():
        try:
            choice = input("Do you want to write this TICKET.md to the active Bead directory? (y/n): ").strip().lower()
            if choice not in {"y", "yes"}:
                print("Aborted.")
                return 0
        except KeyboardInterrupt:
            print("\nAborted.")
            return 1
            
    # Write to Bead directory
    bead_dir = root / ".beads" / "artifacts" / args.issue
    bead_dir.mkdir(parents=True, exist_ok=True)
    ticket_path = bead_dir / "TICKET.md"
    
    try:
        ticket_path.write_text(ticket_yaml, encoding="utf-8")
        print(f"SUCCESS: Auto-filled TICKET.md written to {ticket_path.relative_to(root)}")
    except Exception as exc:
        print(f"ERROR: Failed to write TICKET.md: {exc}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())
