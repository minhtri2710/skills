#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

# Add script directory to sys.path for importing beo_utils
sys.path.insert(0, str(Path(__file__).parent))
import beo_utils

SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,120}$")
SAFE_ISSUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,120}$")
LEARNING_CASE_TYPES = {
    "success_pattern",
    "failure_pattern",
    "near_miss",
    "recurring_mistake",
    "cannot_deliver_pattern",
    "debug_pattern",
    "authoring_candidate",
}

def fail(message: str, *, fallback_path: str | None = None) -> int:
    print(json.dumps({"status": "failed", "error": message, "fallback_path": fallback_path}, indent=2))
    return 1

def safe_note_name(issue_id: str, case_type: str, slug: str) -> str:
    if not SAFE_SLUG.fullmatch(slug):
        raise ValueError("slug must be lowercase alphanumeric with hyphens only")
    if case_type not in LEARNING_CASE_TYPES:
        raise ValueError("case_type is not registered")
    if not SAFE_ISSUE_ID.fullmatch(issue_id):
        raise ValueError("issue_id must be alphanumeric with hyphens or underscores only")
    return f"{date.today().isoformat()}--{case_type.replace('_', '-')}--{issue_id}--{slug}.md"

def ensure_under(base: Path, target: Path) -> None:
    if base.is_symlink():
        raise ValueError("base must not be a symlink")
    base_real = base.resolve()
    target_parent = target.parent.resolve()
    target_parent.relative_to(base_real)
    if target.is_symlink():
        raise ValueError("target must not be a symlink")

def write_fallback(root: Path, issue_id: str, note_name: str, markdown: str) -> Path:
    path = root / ".beads" / "artifacts" / issue_id / "learning" / note_name
    path.parent.mkdir(parents=True, exist_ok=True)
    ensure_under(root / ".beads" / "artifacts" / issue_id / "learning", path)
    path.write_text(markdown, encoding="utf-8")
    return path

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Write a BEO learning note with Obsidian CLI fallback.")
    parser.add_argument("--issue", required=True)
    parser.add_argument("--case-type", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--markdown-file", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    markdown = Path(args.markdown_file).read_text(encoding="utf-8")
    try:
        note_name = safe_note_name(args.issue, args.case_type, args.slug)
    except ValueError as exc:
        return fail(str(exc))

    # Resolve environment dynamically using beo_utils
    env = beo_utils.resolve_obsidian_env()
    vault_name = env["vault_name"]
    vault_path = env["vault_path"]
    learning_dir = env["learning_dir"]

    # Retrieve Vault Target Name/ID
    vault_target = os.environ.get("BEO_OBSIDIAN_VAULT_ID") or os.environ.get("BEO_OBSIDIAN_VAULT_NAME") or ""

    if vault_path and vault_target:
        try:
            learning_dir.mkdir(parents=True, exist_ok=True)
            target = learning_dir / note_name
            ensure_under(learning_dir, target)
            
            if beo_utils.obsidian_create_available():
                code, out, err = beo_utils.run_cmd([
                    "obsidian", f"vault={vault_target}", "create", f"path=beo-learnings/{note_name}", f"content={markdown}"
                ])
                if code == 0:
                    beo_utils.run_cmd(["qmd", "update"])
                    beo_utils.run_cmd(["qmd", "embed"])
                    print(json.dumps({"status": "written", "backend": "obsidian_cli", "path": str(target)}, indent=2))
                    return 0
        except Exception:
            pass

    fallback = write_fallback(root, args.issue, note_name, markdown)
    print(json.dumps({"status": "written", "backend": "fallback_local_markdown", "path": str(fallback)}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
