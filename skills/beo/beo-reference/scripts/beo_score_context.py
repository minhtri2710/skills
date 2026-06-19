#!/usr/bin/env python3
"""Advisory context coverage scorer.

Counts SKILL.md and reference files actually loaded during execution and
compares to the minimum required by TICKET.json.mode. Does not write
state.json. Appends a single `score` event to runtime-events.jsonl under its own
actor name `beo-score-context`.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from beo_io import now, sha256_text, stable_json
from beo_state import append_event, read_events, read_state
from beo_ticket import read_ticket

HELPER_VERSION = "beo-score-context/v1"

MODE_TO_TIER = {"quick": "minimal", "standard": "standard", "strict": "detailed"}

MIN_REQUIRES = {
    "minimal": {"skill_cards": 1, "references": 1, "ticket": 0, "state": 0},
    "standard": {"skill_cards": 2, "references": 2, "ticket": 0, "state": 0},
    "detailed": {"skill_cards": 3, "references": 3, "ticket": 1, "state": 1},
}


def resolve_tier(state: dict[str, Any], ticket: dict[str, Any] | None) -> str:
    tier = (state.get("execution") or {}).get("trace_tier")
    if tier in {"minimal", "standard", "detailed"}:
        return tier
    mode = (ticket or {}).get("mode")
    if isinstance(mode, str):
        return MODE_TO_TIER.get(mode, "standard")
    return "standard"


def _normalize(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _classify(path: str) -> str | None:
    """Return one of: 'skill_card', 'reference', 'ticket', 'state' or None."""
    normalized = _normalize(path)
    if not normalized:
        return None
    if normalized.endswith("SKILL.md") or "/SKILL.md" in normalized:
        return "skill_card"
    if "/beo-reference/references/" in normalized or normalized.startswith("references/"):
        return "reference"
    if normalized.endswith("TICKET.json") and (
        "/.beads/artifacts/" in normalized or normalized.startswith("beads/artifacts/")
    ):
        return "ticket"
    if normalized.endswith("state.json") and (
        "/.beads/artifacts/" in normalized or normalized.startswith("beads/artifacts/")
    ):
        return "state"
    return None


def _coalesce_paths(state: dict[str, Any], events: list[dict[str, Any]]) -> list[str]:
    """Collect every path that could plausibly be a 'read'.

    v1 reality: no explicit files_read field exists. We synthesize a list
    from:
      - execution.evidence_refs
      - execution.changed_files
      - review.findings[].evidence_refs
      - review.done_criteria_coverage[].evidence_refs
      - any 'files_read' or 'evidence_refs' list found in runtime event payloads
    """
    paths: list[str] = []
    seen: set[str] = set()

    def add(value: Any) -> None:
        if isinstance(value, str) and value and value not in seen:
            seen.add(value)
            paths.append(value)

    execution = state.get("execution") if isinstance(state.get("execution"), dict) else {}
    for entry in execution.get("evidence_refs") or []:
        add(entry)
    for entry in execution.get("changed_files") or []:
        add(entry)

    review = state.get("review") if isinstance(state.get("review"), dict) else {}
    for finding in review.get("findings") or []:
        if isinstance(finding, dict):
            for entry in finding.get("evidence_refs") or []:
                add(entry)
    for coverage in review.get("done_criteria_coverage") or []:
        if isinstance(coverage, dict):
            for entry in coverage.get("evidence_refs") or []:
                add(entry)

    for event in events:
        if not isinstance(event, dict):
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict):
            continue
        for key in ("files_read", "evidence_refs", "safe_evidence_refs"):
            value = payload.get(key)
            if isinstance(value, list):
                for entry in value:
                    add(entry)
        trace_id = payload.get("trace_id")
        if isinstance(trace_id, str):
            add(trace_id)
        worktree = payload.get("worktree_path")
        if isinstance(worktree, str):
            add(worktree)

    return paths


def _scope_files(ticket: dict[str, Any] | None) -> list[str]:
    if not isinstance(ticket, dict):
        return []
    scope = ticket.get("scope") or {}
    if not isinstance(scope, dict):
        return []
    files = scope.get("files") or {}
    if not isinstance(files, dict):
        return []
    allow = files.get("allow") or []
    return [entry for entry in allow if isinstance(entry, str)]


def _tally(paths: list[str], ticket: dict[str, Any] | None, state: dict[str, Any] | None) -> dict[str, int]:
    """Count classified paths and fold in the loaded ticket/state.

    The explicit ticket/state increment is gated on the corresponding
    count being zero, so a TICKET.json or state.json path that already
    appears in `paths` (e.g. from `evidence_refs`) does not double-count.
    """
    counts = {"skill_card": 0, "reference": 0, "ticket": 0, "state": 0}
    for path in paths:
        category = _classify(path)
        if category:
            counts[category] += 1
    if ticket is not None and isinstance(ticket.get("issue_id"), str) and counts["ticket"] == 0:
        counts["ticket"] += 1
    if state is not None and state.get("issue_id") and counts["state"] == 0:
        counts["state"] += 1
    return counts


def score_context(state: dict[str, Any], ticket: dict[str, Any] | None, events: list[dict[str, Any]], *, state_loaded: bool) -> dict[str, Any]:
    tier = resolve_tier(state, ticket)
    requires = MIN_REQUIRES[tier]

    paths = _coalesce_paths(state, events)
    if ticket is not None:
        paths.extend(_scope_files(ticket))
    counts = _tally(paths, ticket, state if state_loaded else None)

    breakdown = {
        "skill_cards_loaded": counts["skill_card"] >= requires["skill_cards"],
        "references_loaded": counts["reference"] >= requires["references"],
        "ticket_loaded": counts["ticket"] >= requires["ticket"],
        "state_loaded": counts["state"] >= requires["state"],
    }

    missing: list[str] = []
    if counts["skill_card"] < requires["skill_cards"]:
        missing.append("skill_cards_loaded")
    if counts["reference"] < requires["references"]:
        missing.append("references_loaded")
    if requires["ticket"] and not breakdown["ticket_loaded"]:
        missing.append("ticket_loaded")
    if requires["state"] and not breakdown["state_loaded"]:
        missing.append("state_loaded")

    if missing:
        score_value = 0
    else:
        over_skill = max(0, counts["skill_card"] - requires["skill_cards"])
        over_ref = max(0, counts["reference"] - requires["references"])
        over = over_skill + over_ref
        if tier == "minimal":
            score_value = 1 if over == 0 else (3 if over >= 2 else 2)
        elif tier == "standard":
            score_value = 1 if over == 0 else (3 if over >= 3 else 2)
        else:
            score_value = 1 if over == 0 else (3 if over >= 4 else 2)

    evaluated_at = now()
    score_id_payload = {
        "issue_id": state.get("issue_id"),
        "tier": tier,
        "score_value": score_value,
        "breakdown": breakdown,
        "evaluated_at": evaluated_at,
    }
    score_id = f"context:{state.get('issue_id')}:{sha256_text(stable_json(score_id_payload))[7:14]}"

    return {
        "ok": True,
        "issue_id": state.get("issue_id"),
        "tier": tier,
        "score_value": score_value,
        "score_id": score_id,
        "score_breakdown": breakdown,
        "missing_required": missing,
        "counts": counts,
        "requires": requires,
        "evaluated_at": evaluated_at,
        "helper_version": HELPER_VERSION,
    }


def append_score_event(root: Path, issue_id: str, result: dict[str, Any]) -> None:
    event = {
        "issue_id": issue_id,
        "kind": "score",
        "phase": "executed",
        "actor": "beo-score-context",
        "timestamp": result["evaluated_at"],
        "payload": {
            "score_id": result["score_id"],
            "score_kind": "context",
            "score_value": result["score_value"],
            "score_breakdown": result["score_breakdown"],
            "evaluated_at": result["evaluated_at"],
            "tier": result["tier"],
        },
    }
    try:
        append_event(root, issue_id, event)
    except Exception as exc:
        # Scoring is advisory; failure to append must not break the caller,
        # but the data loss should be visible to the operator.
        print(f"warning: failed to append context score event: {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Score context coverage against TICKET.json.mode")
    parser.add_argument("--issue", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    state_loaded = False
    try:
        state = read_state(root, args.issue)
        state_loaded = True
    except FileNotFoundError:
        state = {"issue_id": args.issue, "execution": {}, "review": {}}
    try:
        ticket = read_ticket(root, args.issue).data
    except Exception:
        ticket = None
    events = read_events(root, args.issue)
    result = score_context(state, ticket, events, state_loaded=state_loaded)
    if state.get("issue_id") and (state.get("execution") or {}).get("started_at"):
        append_score_event(root, args.issue, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
