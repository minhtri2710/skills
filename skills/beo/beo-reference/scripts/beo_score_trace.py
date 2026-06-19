#!/usr/bin/env python3
"""Advisory trace quality scorer.

Reads state.json and runtime-events.jsonl for a delivery bead and scores
the trace 0-3 against the tier implied by state.execution.trace_tier or
TICKET.json.mode. Does not write state.json. Appends a single
`score` event to runtime-events.jsonl under its own actor name
`beo-score-trace`.
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

HELPER_VERSION = "beo-score-trace/v1"

TRACE_FIELDS = {
    "task_summary",
    "outcome",
    "intake_id",
    "story_id",
    "agent",
    "actions_taken",
    "files_read",
    "files_changed",
    "errors",
    "friction",
    "decisions_made",
    "duration_seconds",
    "token_estimate",
}

MINIMAL_REQUIRED = ("task_summary", "outcome")
STANDARD_REQUIRED = (
    "intake_id_or_story_id",
    "agent",
    "actions_taken",
    "files_read",
    "files_changed",
    "errors_or_friction",
)
DETAILED_REQUIRED = (
    "decisions_made",
    "duration_seconds",
    "token_estimate",
)

MODE_TO_TIER = {"quick": "minimal", "standard": "standard", "strict": "detailed"}


def resolve_tier(state: dict[str, Any], ticket: dict[str, Any] | None) -> str:
    tier = (state.get("execution") or {}).get("trace_tier")
    if tier in {"minimal", "standard", "detailed"}:
        return tier
    mode = (ticket or {}).get("mode")
    if isinstance(mode, str):
        return MODE_TO_TIER.get(mode, "standard")
    return "standard"


def _merge_event_payloads(events: list[dict[str, Any]]) -> dict[str, Any]:
    """Coalesce trace-shaped fields from all runtime event payloads.

    Last write wins: events are append-only in chronological order, so
    iterating left-to-right and reassigning for each non-empty value means
    the most recent non-empty value for a key overrides earlier ones. Returns
    a dict keyed by trace field name; only fields that actually appear in the
    events are returned.
    """
    merged: dict[str, Any] = {}
    for event in events:
        if not isinstance(event, dict):
            continue
        payload = event.get("payload")
        if not isinstance(payload, dict):
            continue
        for key in TRACE_FIELDS:
            if key in payload and payload[key] not in (None, "", [], {}):
                merged[key] = payload[key]
    return merged


def extract_trace(state: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    """Pull together everything we know about the trace.

    Order of precedence (later overrides earlier):
      1. execution.interventions[].description  -> narrative evidence
      2. review.findings[].message + done_criteria_coverage[].criterion
         -> task_summary fallback
      3. execution.evidence_refs / verify_results -> files_read, files_changed,
         actions_taken proxies
      4. runtime event payloads (any kind) with trace-shaped keys
    """
    execution = state.get("execution") if isinstance(state.get("execution"), dict) else {}
    review = state.get("review") if isinstance(state.get("review"), dict) else {}

    trace: dict[str, Any] = {}

    intervention_descriptions = [
        item.get("description")
        for item in (execution.get("interventions") or [])
        if isinstance(item, dict) and isinstance(item.get("description"), str)
    ]
    if intervention_descriptions:
        trace["task_summary"] = " | ".join(intervention_descriptions)

    if not trace.get("task_summary"):
        finding_messages = [
            f.get("message")
            for f in (review.get("findings") or [])
            if isinstance(f, dict) and isinstance(f.get("message"), str)
        ]
        if finding_messages:
            trace["task_summary"] = " | ".join(finding_messages)

    if not trace.get("outcome"):
        verdict = review.get("verdict")
        if verdict:
            trace["outcome"] = verdict

    if not trace.get("agent"):
        actor = execution.get("actor") or review.get("actor")
        if isinstance(actor, str) and actor.strip():
            trace["agent"] = actor

    files_changed = execution.get("changed_files")
    if isinstance(files_changed, list) and files_changed:
        trace["files_changed"] = files_changed

    evidence_refs = execution.get("evidence_refs")
    if isinstance(evidence_refs, list) and evidence_refs:
        trace["files_read"] = list(evidence_refs)
        trace["actions_taken"] = list(evidence_refs)

    verify_results = execution.get("verify_results")
    if isinstance(verify_results, list) and verify_results:
        actions = trace.get("actions_taken") or []
        for result in verify_results:
            if isinstance(result, dict):
                command = result.get("command")
                if isinstance(command, str) and command:
                    actions.append(f"verify:{command}")
        if actions:
            trace["actions_taken"] = actions

    trace.update(_merge_event_payloads(events))

    return trace


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, dict)):
        return len(value) >= 1
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return True
    return bool(value)


def _has_text_at_least(value: Any, minimum: int) -> bool:
    return isinstance(value, str) and len(value.strip()) >= minimum


def _required_for_tier(tier: str) -> tuple[str, ...]:
    if tier == "minimal":
        return MINIMAL_REQUIRED
    if tier == "standard":
        return STANDARD_REQUIRED
    return STANDARD_REQUIRED + DETAILED_REQUIRED


def _optional_for_tier(tier: str) -> tuple[str, ...]:
    if tier == "minimal":
        return ()
    if tier == "standard":
        return DETAILED_REQUIRED
    return ()


def _breakdown(trace: dict[str, Any], tier: str) -> dict[str, bool]:
    breakdown: dict[str, bool] = {}
    breakdown["task_summary"] = _has_text_at_least(trace.get("task_summary"), 10)
    breakdown["outcome"] = _has_value(trace.get("outcome"))
    breakdown["intake_id"] = _has_value(trace.get("intake_id"))
    breakdown["story_id"] = _has_value(trace.get("story_id"))
    breakdown["agent"] = _has_value(trace.get("agent"))
    breakdown["actions_taken"] = _has_value(trace.get("actions_taken"))
    breakdown["files_read"] = _has_value(trace.get("files_read"))
    breakdown["files_changed"] = _has_value(trace.get("files_changed"))
    breakdown["errors"] = _has_value(trace.get("errors"))
    breakdown["friction"] = _has_value(trace.get("friction"))
    breakdown["decisions_made"] = _has_value(trace.get("decisions_made"))
    breakdown["duration_seconds"] = _has_value(trace.get("duration_seconds"))
    breakdown["token_estimate"] = _has_value(trace.get("token_estimate"))
    return breakdown


def _missing_required(tier: str, breakdown: dict[str, bool]) -> list[str]:
    missing: list[str] = []
    for field in _required_for_tier(tier):
        if field == "intake_id_or_story_id":
            if not (breakdown["intake_id"] or breakdown["story_id"]):
                missing.append("intake_id|story_id")
        elif field == "errors_or_friction":
            if not (breakdown["errors"] or breakdown["friction"]):
                missing.append("errors|friction")
        else:
            if not breakdown.get(field):
                missing.append(field)
    return missing


def _diff(tier: str, trace: dict[str, Any], breakdown: dict[str, bool]) -> list[str]:
    diffs: list[str] = []
    if tier != "minimal" and not (breakdown["intake_id"] or breakdown["story_id"]):
        diffs.append("intake_id and story_id both empty")
    if tier != "minimal" and not breakdown["agent"]:
        diffs.append("agent not recorded")
    if tier != "minimal":
        actions = trace.get("actions_taken")
        if not (isinstance(actions, list) and actions):
            diffs.append("actions_taken empty")
        reads = trace.get("files_read")
        if not (isinstance(reads, list) and reads):
            diffs.append("files_read empty")
    if tier == "detailed":
        if not (breakdown["decisions_made"] and breakdown["duration_seconds"] and breakdown["token_estimate"]):
            diffs.append("decisions_made/duration_seconds/token_estimate not all populated")
    return diffs


def score_trace(state: dict[str, Any], ticket: dict[str, Any] | None, events: list[dict[str, Any]]) -> dict[str, Any]:
    tier = resolve_tier(state, ticket)
    trace = extract_trace(state, events)
    breakdown = _breakdown(trace, tier)
    missing = _missing_required(tier, breakdown)
    optional = _optional_for_tier(tier)
    optional_present = sum(1 for field in optional if breakdown.get(field))

    if missing:
        score_value = 0
    else:
        if not optional:
            score_value = 1
        else:
            ratio = optional_present / len(optional)
            if ratio >= 0.75:
                score_value = 3
            elif ratio >= 0.5:
                score_value = 2
            else:
                score_value = 1

    evaluated_at = now()
    score_id_payload = {
        "issue_id": state.get("issue_id"),
        "tier": tier,
        "score_value": score_value,
        "breakdown": breakdown,
        "evaluated_at": evaluated_at,
    }
    score_id = f"trace:{state.get('issue_id')}:{sha256_text(stable_json(score_id_payload))[7:14]}"

    return {
        "ok": True,
        "issue_id": state.get("issue_id"),
        "tier": tier,
        "score_value": score_value,
        "score_id": score_id,
        "score_breakdown": breakdown,
        "missing_required": missing,
        "diff": _diff(tier, trace, breakdown),
        "evaluated_at": evaluated_at,
        "helper_version": HELPER_VERSION,
    }


def append_score_event(root: Path, issue_id: str, result: dict[str, Any]) -> None:
    event = {
        "issue_id": issue_id,
        "kind": "score",
        "phase": "executed",
        "actor": "beo-score-trace",
        "timestamp": result["evaluated_at"],
        "payload": {
            "score_id": result["score_id"],
            "score_kind": "trace",
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
        print(f"warning: failed to append trace score event: {exc}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Score a delivery trace by quality tier")
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
    result = score_trace(state, ticket, events)
    if state_loaded and (state.get("execution") or {}).get("started_at"):
        append_score_event(root, args.issue, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
