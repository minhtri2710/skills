#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from beo_io import compact_text

SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,120}$")
SAFE_ISSUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,120}$")


def load_learning_case_types() -> set[str]:
    return {
        "success_pattern",
        "failure_pattern",
        "near_miss",
        "recurring_mistake",
        "cannot_deliver_pattern",
        "debug_pattern",
        "authoring_candidate",
    }


def fail(message: str) -> int:
    print(json.dumps({"status": "failed", "error": message}, indent=2))
    return 1


def safe_note_name(issue_id: str, case_type: str, slug: str, learning_case_types: set[str]) -> str:
    if not SAFE_SLUG.fullmatch(slug):
        raise ValueError("slug must be lowercase alphanumeric with hyphens only")
    if case_type not in learning_case_types:
        raise ValueError("case_type is not registered")
    if not SAFE_ISSUE_ID.fullmatch(issue_id):
        raise ValueError("issue_id must be alphanumeric with hyphens or underscores only")
    return f"{date.today().isoformat()}--{case_type.replace('_', '-')}--{issue_id}--{slug}.md"


def validate_fallback_target(root: Path) -> Path:
    beads_dir = root / ".beads"
    if not beads_dir.is_dir():
        raise ValueError(f"root is not a Beads workspace: {root}")
    return beads_dir / "learnings"


def extract_frontmatter(markdown: str) -> dict[str, object]:
    if not markdown.startswith("---\n"):
        raise ValueError("learning note must start with YAML frontmatter")
    end = markdown.find("\n---", 4)
    if end == -1:
        raise ValueError("learning note frontmatter is not closed")
    try:
        import yaml  # type: ignore[import-not-found]
        frontmatter = yaml.safe_load(markdown[4:end]) or {}
    except ImportError as exc:
        raise ValueError("PyYAML is required to validate learning note frontmatter") from exc
    except Exception as exc:
        raise ValueError(f"learning note frontmatter is invalid YAML: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise ValueError("learning note frontmatter must be a YAML mapping")
    return frontmatter


def validate_learning_frontmatter(frontmatter: dict[str, object], issue: str | None, case_type: str, mode: str) -> None:
    required = {"basis_ref", "evidence_refs", "secret_policy"}
    if mode == "learning_candidate":
        required.update({"source_bead_id", "source_phase", "condition_id"})
    else:
        required.add("source_type")
    missing = required - set(frontmatter)
    if missing:
        raise ValueError(f"learning note frontmatter is missing required fields: {', '.join(sorted(missing))}")
    if mode == "learning_candidate" and frontmatter["source_bead_id"] != issue:
        raise ValueError(f"source_bead_id '{frontmatter['source_bead_id']}' in frontmatter must match --issue '{issue}'")
    if mode == "user_request" and frontmatter.get("source_type") != "user_request":
        raise ValueError("user_request frontmatter must set source_type: user_request")
    if "case_type" in frontmatter and frontmatter["case_type"] != case_type:
        raise ValueError(f"case_type '{frontmatter['case_type']}' in frontmatter must match --case-type '{case_type}'")
    evidence_refs = frontmatter["evidence_refs"]
    if not isinstance(evidence_refs, list) or not evidence_refs or not all(isinstance(ref, str) and ref.strip() for ref in evidence_refs):
        raise ValueError("evidence_refs must be a non-empty YAML list of strings")
    if frontmatter["secret_policy"] != "handles_only":
        raise ValueError("secret_policy must be handles_only")


def write_learning(root: Path, note_name: str, markdown: str) -> Path:
    learning_dir = validate_fallback_target(root)
    path = learning_dir / note_name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError(f"learning note already exists at local path: {path}")
    with path.open("x", encoding="utf-8") as handle:
        handle.write(markdown)
    return path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Write a BEO learning note.")
    parser.add_argument("--mode", choices=["learning_candidate", "user_request"], required=True)
    parser.add_argument("--issue")
    parser.add_argument("--case-type")
    parser.add_argument("--slug")
    parser.add_argument("--markdown-file", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    markdown = Path(args.markdown_file).read_text(encoding="utf-8")
    try:
        frontmatter = extract_frontmatter(markdown)
    except ValueError as exc:
        return fail(f"Frontmatter validation failed: {exc}")

    case_type = args.case_type or str(frontmatter.get("case_type") or "success_pattern")
    issue_token = args.issue or "user-request"
    slug = args.slug or str(frontmatter.get("slug") or "manual")
    if args.mode == "learning_candidate" and not args.issue:
        return fail("learning_candidate mode requires --issue")
    try:
        validate_learning_frontmatter(frontmatter, args.issue, case_type, args.mode)
        note_name = safe_note_name(issue_token, case_type, slug, load_learning_case_types())
    except ValueError as exc:
        return fail(str(exc))

    try:
        note_path = write_learning(root, note_name, markdown)
    except ValueError as exc:
        return fail(str(exc))

    result = {
        "status": "written",
        "memory_backend": "local_markdown",
        "backend": "local_markdown",
        "path": str(note_path)
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
