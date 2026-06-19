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
import beo_memory_tools

SAFE_SLUG = re.compile(r"^[a-z0-9][a-z0-9-]{0,120}$")
SAFE_ISSUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,120}$")


OKF_TYPES = {"learning", "decision", "reference"}


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
        raise ValueError("learning note must start with frontmatter")
    end = markdown.find("\n---", 4)
    if end == -1:
        raise ValueError("learning note frontmatter is not closed")
    try:
        frontmatter = _parse_frontmatter_block(markdown[4:end])
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError(f"learning note frontmatter is invalid: {exc}") from exc
    if not isinstance(frontmatter, dict):
        raise ValueError("learning note frontmatter must be a mapping")
    return frontmatter


def validate_learning_frontmatter(frontmatter: dict[str, object], issue: str | None, case_type: str, mode: str) -> None:
    required = {"type", "basis_ref", "evidence_refs", "secret_policy"}
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
        raise ValueError("evidence_refs must be a non-empty list of strings")
    if frontmatter["type"] not in OKF_TYPES:
        raise ValueError(f"type must be one of {sorted(OKF_TYPES)}, got '{frontmatter['type']}'")
    if frontmatter["secret_policy"] != "handles_only":
        raise ValueError("secret_policy must be handles_only")


def migrate_legacy_note(frontmatter: dict[str, object], markdown_body: str) -> dict[str, object]:
    """Backfill the new required 'type' field for notes written before it was required.

    Existing notes in `.beads/learnings/` or `<vault>/beo-learnings/` lack the
    'type' key. The default for the legacy learning-note format is 'learning';
    only override when the body or other frontmatter clearly indicates a
    decision or reference. Returns a new dict; the input is not mutated.
    """
    if "type" in frontmatter:
        return frontmatter
    migrated = dict(frontmatter)
    body_lower = markdown_body.lower()
    if "decision" in body_lower and "reference" not in body_lower:
        migrated["type"] = "decision"
    elif "reference" in body_lower and "decision" not in body_lower:
        migrated["type"] = "reference"
    else:
        migrated["type"] = "learning"
    return migrated


def _rewrite_frontmatter(markdown: str, frontmatter: dict[str, object]) -> str:
    """Replace the frontmatter block in `markdown` with a fresh dump of `frontmatter`.

    The closing ``---`` separator and the body after it are preserved. The
    new frontmatter is emitted in key-sorted order for deterministic output.
    """
    end = markdown.find("\n---", 4)
    if end == -1:
        raise ValueError("learning note frontmatter is not closed")
    body = markdown[end:]
    dumped = _dump_frontmatter(frontmatter)
    return f"---\n{dumped}\n{body}"


# ---- Minimal frontmatter parser (no PyYAML dependency) ---------------------
#
# BEO learning frontmatter uses a small YAML subset:
#   * top-level mapping: ``key: value`` lines
#   * flow-style lists: ``key: [a, b, c]``
#   * block-style lists: ``key:\\n  - item``
#   * scalars: strings (plain or quoted), integers, booleans, null
# This parser is intentionally narrow. It rejects YAML features BEO never
# produces (anchors, aliases, multi-doc streams, complex keys, flow mappings)
# so any unrecognised token raises a clear error rather than silently
# being misread. Trailing whitespace is trimmed. Comments are NOT supported
# inside the frontmatter block; the body that follows the closing ``---``
# may contain them.

_FRONTMATTER_FLOW_LIST = re.compile(r"^\[(.*)\]\s*$")
_FRONTMATTER_SCALAR_NULL = {"null", "Null", "NULL", "~", ""}
_FRONTMATTER_SCALAR_TRUE = {"true", "True", "TRUE"}
_FRONTMATTER_SCALAR_FALSE = {"false", "False", "FALSE"}


def _split_flow_list_items(inner: str) -> list[str]:
    """Split a flow-list body on top-level commas (no nested flow support)."""
    items: list[str] = []
    depth = 0
    current: list[str] = []
    for char in inner:
        if char in "[{":
            depth += 1
            current.append(char)
        elif char in "]}":
            depth -= 1
            current.append(char)
        elif char == "," and depth == 0:
            items.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if current:
        items.append("".join(current).strip())
    return [item for item in items if item != ""]


def _parse_scalar(token: str) -> object:
    token = token.strip()
    if token == "" or token in _FRONTMATTER_SCALAR_NULL:
        return None
    if token in _FRONTMATTER_SCALAR_TRUE:
        return True
    if token in _FRONTMATTER_SCALAR_FALSE:
        return False
    if (token.startswith('"') and token.endswith('"')) or (token.startswith("'") and token.endswith("'")):
        return token[1:-1]
    try:
        return int(token)
    except ValueError:
        pass
    try:
        return float(token)
    except ValueError:
        pass
    return token


def _parse_frontmatter_block(block: str) -> dict[str, object]:
    """Parse a frontmatter block (text between the two ``---`` markers) into a dict.

    Raises ``ValueError`` with a precise location on any unsupported construct.
    """
    lines = block.split("\n")
    result: dict[str, object] = {}
    i = 0
    while i < len(lines):
        raw = lines[i]
        if raw.strip() == "" or raw.lstrip().startswith("#"):
            i += 1
            continue
        if raw.startswith(" ") or raw.startswith("\t"):
            raise ValueError(f"unexpected indented line at position {i}: {raw!r}")
        if ":" not in raw:
            raise ValueError(f"expected 'key: value' at position {i}: {raw!r}")
        key, _, value = raw.partition(":")
        key = key.strip()
        if not key:
            raise ValueError(f"empty key at position {i}: {raw!r}")
        value = value.lstrip()
        if value == "":
            # Either ``key:`` with nothing after, or ``key:`` followed by a block list.
            # Block list items may be indented (standard YAML) or flush at column 0
            # (tolerated by pyyaml, used in many BEO learning notes).
            block_items: list[object] = []
            j = i + 1
            while j < len(lines):
                stripped = lines[j].lstrip()
                if lines[j].startswith(" ") or lines[j].startswith("\t"):
                    if not stripped.startswith("- "):
                        raise ValueError(f"expected list item at position {j}: {lines[j]!r}")
                    block_items.append(_parse_scalar(stripped[2:]))
                    j += 1
                    continue
                if stripped.startswith("- "):
                    block_items.append(_parse_scalar(stripped[2:]))
                    j += 1
                    continue
                break
            if block_items:
                result[key] = block_items
                i = j
                continue
            result[key] = None
            i += 1
            continue
        flow = _FRONTMATTER_FLOW_LIST.match(value)
        if flow:
            inner = flow.group(1)
            result[key] = [_parse_scalar(item) for item in _split_flow_list_items(inner)]
            i += 1
            continue
        result[key] = _parse_scalar(value)
        i += 1
    return result


def _dump_scalar(value: object) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, list):
        return "[" + ", ".join(_dump_scalar(item) for item in value) + "]"
    text = str(value)
    # Quote strings that would otherwise re-parse as bool/null/number,
    # and strings with structural chars or surrounding whitespace.
    if (
        any(ch in text for ch in [":", "#", "[", "]", "{", "}", ","])
        or text.strip() != text
        or not isinstance(_parse_scalar(text), str)
    ):
        return json.dumps(text)
    return text


def _dump_frontmatter(frontmatter: dict[str, object]) -> str:
    return "\n".join(f"{key}: {_dump_scalar(frontmatter[key])}" for key in sorted(frontmatter))


def write_note_to_dir(learning_dir: Path, note_name: str, markdown: str, backend: str, fallback_reason: str | None = None) -> dict[str, str]:
    path = learning_dir / note_name
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise ValueError(f"learning note already exists at path: {path}")
    with path.open("x", encoding="utf-8") as handle:
        handle.write(markdown)
    result = {"memory_backend": backend, "backend": backend, "path": str(path)}
    if fallback_reason:
        result["fallback_reason"] = fallback_reason
    return result


def resolve_learning_target(root: Path) -> tuple[Path, str, str | None]:
    fallback_dir = validate_fallback_target(root)
    env = beo_memory_tools.resolve_obsidian_env()
    vault_path = env["vault_path"]
    learning_dir = env["learning_dir"]
    if vault_path is None or learning_dir is None:
        return fallback_dir, "local_markdown", "obsidian_vault_unconfigured"
    if not isinstance(vault_path, Path) or not isinstance(learning_dir, Path):
        return fallback_dir, "local_markdown", "obsidian_vault_invalid"
    if not vault_path.is_dir():
        return fallback_dir, "local_markdown", "obsidian_vault_missing"
    try:
        learning_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return fallback_dir, "local_markdown", "obsidian_learning_dir_unwritable"
    return learning_dir, "obsidian_markdown", None


def write_learning(root: Path, note_name: str, markdown: str) -> dict[str, str]:
    learning_dir, backend, fallback_reason = resolve_learning_target(root)
    return write_note_to_dir(learning_dir, note_name, markdown, backend, fallback_reason)


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

    # Backfill the new 'type' field for notes written before it was required.
    body_start = markdown.find("\n---", 4) + 4
    migrated = migrate_legacy_note(frontmatter, markdown[body_start:])
    if migrated is not frontmatter:
        frontmatter = migrated
        markdown = _rewrite_frontmatter(markdown, frontmatter)

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
        write_result = write_learning(root, note_name, markdown)
    except ValueError as exc:
        return fail(str(exc))

    result = {
        "status": "written",
        **write_result,
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
