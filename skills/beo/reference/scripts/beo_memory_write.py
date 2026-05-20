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


def compact_text(text: str, limit: int = 600) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...[truncated]"


def qmd_refresh_status() -> dict[str, str | bool]:
    update_code, _update_out, update_err = beo_utils.run_cmd(["qmd", "update"])
    embed_code, _embed_out, embed_err = beo_utils.run_cmd(["qmd", "embed"])
    result: dict[str, str | bool] = {
        "qmd_update_status": "ok" if update_code == 0 else "failed",
        "qmd_embed_status": "ok" if embed_code == 0 else "failed",
        "qmd_indexed": update_code == 0 and embed_code == 0,
    }
    if update_code != 0:
        result["qmd_update_error"] = compact_text(update_err)
    if embed_code != 0:
        result["qmd_embed_error"] = compact_text(embed_err)
    return result

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


def validate_fallback_target(root: Path, issue_id: str) -> Path:
    beads_dir = root / ".beads"
    issue_dir = beads_dir / "artifacts" / issue_id
    if not beads_dir.is_dir():
        raise ValueError(f"root is not a Beads workspace: {root}")
    if not issue_dir.is_dir():
        raise ValueError(f"issue artifact directory does not exist: {issue_dir}")
    return issue_dir / "learning"

def write_fallback(root: Path, issue_id: str, note_name: str, markdown: str) -> Path:
    learning_dir = validate_fallback_target(root, issue_id)
    path = learning_dir / note_name
    path.parent.mkdir(parents=True, exist_ok=True)
    ensure_under(learning_dir, path)
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
    vault_target = os.environ.get("BEO_OBSIDIAN_VAULT_ID") or os.environ.get("BEO_OBSIDIAN_VAULT_NAME") or vault_name

    fallback_reason = "obsidian environment is not configured"
    if vault_path and vault_target:
        try:
            target = learning_dir / note_name
            if learning_dir.exists():
                ensure_under(learning_dir, target)
                if beo_utils.obsidian_create_available():
                    code, out, err = beo_utils.run_cmd([
                        "obsidian", f"vault={vault_target}", "create", f"path=beo-learnings/{note_name}", f"content={markdown}"
                    ])
                    if code == 0:
                        result = {"status": "written", "backend": "obsidian_cli", "path": str(target)}
                        result.update(qmd_refresh_status())
                        print(json.dumps(result, indent=2))
                        return 0
                    fallback_reason = err or out or "obsidian create failed"
                else:
                    fallback_reason = "obsidian create command is unavailable"
            else:
                fallback_reason = "learning directory is not configured; run beo_setup.py --configure-memory"
        except Exception as exc:
            fallback_reason = str(exc)

    try:
        fallback = write_fallback(root, args.issue, note_name, markdown)
    except ValueError as exc:
        return fail(str(exc))
    print(json.dumps({"status": "written", "backend": "fallback_local_markdown", "path": str(fallback), "fallback_reason": compact_text(fallback_reason), "qmd_indexed": "not_run"}, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
