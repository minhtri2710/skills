#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import date
from pathlib import Path


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


def obsidian_create_available() -> bool:
    try:
        proc = subprocess.run(["obsidian", "help"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        create_proc = subprocess.run(["obsidian", "help", "create"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError:
        return False
    help_text = f"{proc.stdout}\n{proc.stderr}"
    create_help_text = f"{create_proc.stdout}\n{create_proc.stderr}"
    return proc.returncode == 0 and create_proc.returncode == 0 and "vault=" in help_text and all(token in create_help_text for token in ["path=", "content="])


def obsidian_vault_target() -> str:
    return os.environ.get("BEO_OBSIDIAN_VAULT_ID") or os.environ.get("BEO_OBSIDIAN_VAULT_NAME") or ""


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

    vault_value = os.environ.get("BEO_OBSIDIAN_VAULT", "")
    vault_target = obsidian_vault_target()
    if vault_value and vault_target:
        try:
            vault = Path(vault_value).expanduser().resolve()
            learning_dir = vault / "beo-learnings"
            target = learning_dir / note_name
            ensure_under(learning_dir, target)
            if obsidian_create_available():
                proc = subprocess.run(
                    ["obsidian", f"vault={vault_target}", "create", f"path=beo-learnings/{note_name}", f"content={markdown}"],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                if proc.returncode == 0:
                    print(json.dumps({"status": "written", "backend": "obsidian_cli", "path": str(target)}, indent=2))
                    return 0
        except Exception:
            pass

    fallback = write_fallback(root, args.issue, note_name, markdown)
    print(json.dumps({"status": "written", "backend": "fallback_local_markdown", "path": str(fallback)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
