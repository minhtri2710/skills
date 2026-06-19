#!/usr/bin/env python3
"""BEO proposal generator (advisory, propose-only).

Scans runtime-events.jsonl, harness-proposal.json, and learning notes
for BEO change signals (friction, learning_candidate_suggestion,
advisory learning notes) and writes a deduplicated prop-<sha1>.md file
per distinct trigger into `<root>/skills/beo/beo-climate/proposals/pending/`.

This script NEVER applies any change — it only generates proposal files
for beo-author to triage. It is fully idempotent: re-running creates
zero new files once all proposals exist.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

from beo_io import now, stable_json

PROPOSAL_KINDS = {"friction", "learning_candidate_suggestion"}
PROPOSAL_DIR = os.environ.get("BEO_PROPOSAL_DIR", "skills/beo/beo-climate/proposals/pending")
LEARNINGS_VAULT_SUBDIR = "beo-learnings"
LEARNINGS_LOCAL_SUBDIR = ".beads/learnings"


def _proposal_dir(root: Path) -> Path:
    return root / PROPOSAL_DIR


def _load_jsonl(path: Path) -> list[dict[str, Any]]:
    """Load a JSONL file, ignoring blank lines. Malformed lines are skipped."""
    events: list[dict[str, Any]] = []
    if not path.exists():
        return events
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            events.append(obj)
    return events


def _scan_runtime_events(root: Path) -> list[tuple[Path, dict[str, Any]]]:
    """Return (path, event) pairs for events with proposal-relevant kinds."""
    out: list[tuple[Path, dict[str, Any]]] = []
    artifacts = root / ".beads" / "artifacts"
    if not artifacts.exists():
        return out
    for path in sorted(artifacts.glob("*/runtime-events.jsonl")):
        for event in _load_jsonl(path):
            if event.get("kind") in PROPOSAL_KINDS:
                out.append((path, event))
    return out


def _scan_harness_proposals(root: Path) -> list[Path]:
    """Return paths to all harness-proposal.json files under .beads/artifacts/."""
    artifacts = root / ".beads" / "artifacts"
    if not artifacts.exists():
        return []
    return sorted(artifacts.glob("*/harness-proposal.json"))


def _scan_learning_notes(root: Path) -> list[Path]:
    """Return learning-note paths from BEO_LEARNING_VAULT or local fallback."""
    vault = os.environ.get("BEO_LEARNING_VAULT")
    if vault:
        vault_path = Path(vault) / LEARNINGS_VAULT_SUBDIR
        if vault_path.exists():
            return sorted(vault_path.glob("*.md"))
    local = root / LEARNINGS_LOCAL_SUBDIR
    if local.exists():
        return sorted(local.glob("*.md"))
    return []


def _proposal_id(trigger_blob: str) -> str:
    """Return a deterministic proposal_id like `prop-<sha1-prefix>`."""
    digest = hashlib.sha1(trigger_blob.encode("utf-8")).hexdigest()
    return f"prop-{digest[:8]}"


def _build_proposal(triggers: list[dict[str, str]], sources: list[str], proposal_id: str) -> str:
    """Render a single proposal file as a markdown document with YAML frontmatter."""
    trigger_lines = "\n".join(f"  - {json.dumps(t)}" for t in triggers)
    source_lines = "\n".join(f"  - {json.dumps(s)}" for s in sources)
    body = (
        f"---\n"
        f"proposal_id: {proposal_id}\n"
        f"generated_at: {now()}\n"
        f"sources:\n{source_lines}\n"
        f"triggers:\n{trigger_lines}\n"
        f"suggested_action: |\n"
        f"  Review these BEO control-plane signals and decide whether to author or update a skill card,\n"
        f"  reference, registry, or template. Use beo-author to apply any change; never apply directly.\n"
        f"  Group related triggers, confirm safety, and update doctrine via the canonical owner per\n"
        f"  `beo-reference -> references/doctrine-map.md`.\n"
        f"scope: BEO_control_plane\n"
        f"---\n"
    )
    return body


def _trigger_from_event(event: dict[str, Any]) -> dict[str, str] | None:
    """Map a runtime event to a trigger dict, or None if it carries no signal."""
    kind = event.get("kind")
    payload = event.get("payload", {}) or {}
    if kind == "friction":
        description = payload.get("description") or payload.get("reason") or ""
        return {"friction": str(description)[:500]} if description else None
    if kind == "learning_candidate_suggestion":
        hypothesis = payload.get("hypothesis") or payload.get("trigger") or ""
        if hypothesis:
            return {"learning": str(hypothesis)[:500]}
    return None


def _trigger_from_harness_proposal(path: Path) -> dict[str, str] | None:
    """Map a harness-proposal.json to a trigger dict, or None if empty/unreadable."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"harness_proposal": f"unreadable: {path.name}"}
    if not isinstance(data, dict):
        return None
    rationale = data.get("rationale") or data.get("change_type") or ""
    return {"harness_proposal": f"{data.get('change_type', 'unknown')}: {rationale}"[:500]} if rationale else None


def _trigger_from_learning_note(path: Path) -> dict[str, str] | None:
    """Map a learning note to a trigger dict using the first heading or filename."""
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    summary = match.group(1) if match else path.stem
    return {"learning_note": str(summary)[:500]}


def main() -> int:
    parser = argparse.ArgumentParser(description="BEO proposal generator (advisory, propose-only)")
    parser.add_argument("--root", default=".", help="Repository root (default: cwd)")
    parser.add_argument("--dry-run", action="store_true", help="Print summary without writing files")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    triggers: list[dict[str, str]] = []
    sources: list[str] = []
    for path, event in _scan_runtime_events(root):
        trigger = _trigger_from_event(event)
        if trigger:
            triggers.append(trigger)
            sources.append(f"runtime-events.jsonl#{event.get('issue_id', path.parent.name)}")
    for path in _scan_harness_proposals(root):
        trigger = _trigger_from_harness_proposal(path)
        if trigger:
            triggers.append(trigger)
            sources.append(str(path.relative_to(root)))
    for path in _scan_learning_notes(root):
        trigger = _trigger_from_learning_note(path)
        if trigger:
            triggers.append(trigger)
            sources.append(str(path))

    if not triggers:
        print(json.dumps({"ok": True, "proposals_created": 0, "proposals_skipped": 0, "files": []}, indent=2))
        return 0

    # Group triggers by deterministic proposal_id; multiple signals may share one proposal.
    grouped: dict[str, list[dict[str, str]]] = {}
    grouped_sources: dict[str, list[str]] = {}
    for trigger, source in zip(triggers, sources):
        pid = _proposal_id(stable_json(trigger))
        grouped.setdefault(pid, []).append(trigger)
        grouped_sources.setdefault(pid, []).append(source)

    target_dir = _proposal_dir(root)
    if not args.dry_run:
        target_dir.mkdir(parents=True, exist_ok=True)
    created: list[str] = []
    skipped: list[str] = []
    for pid, items in sorted(grouped.items()):
        target = target_dir / f"{pid}.md"
        if target.exists():
            skipped.append(str(target.relative_to(root)))
            continue
        body = _build_proposal(items, grouped_sources[pid], pid)
        if args.dry_run:
            created.append(str(target.relative_to(root)))
            continue
        target.write_text(body, encoding="utf-8")
        created.append(str(target.relative_to(root)))
    print(json.dumps({
        "ok": True,
        "proposals_created": len(created),
        "proposals_skipped": len(skipped),
        "files": created + skipped,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
