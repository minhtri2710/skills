#!/usr/bin/env python3
"""BEO sensor telemetry (advisory, read-only).

Aggregates `verification_run` runtime events across beads to surface sensor
firing rates — how often verify and `behaviour_gate` commands pass/fail/skip.
Addresses the harness-engineering question: "if a sensor never fires, is that
high quality or inadequate detection?" (Böckeler/Fowler). Advisory only; never
grants authority and never writes. Output: JSON to stdout.

CLI:
    python3 beo_metrics.py [--root .] [--issue <id>]

Exit codes: 0 always (advisory).
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

HELPER_VERSION = "beo-metrics/v1"


def _iter_events(root: Path, issue_filter: str | None):
    """Yield parsed JSON objects from every bead's runtime-events.jsonl."""
    artifacts = root / ".beads" / "artifacts"
    if not artifacts.is_dir():
        return
    for entry in sorted(artifacts.iterdir()):
        if not entry.is_dir():
            continue
        if issue_filter and entry.name != issue_filter:
            continue
        events_path = entry / "runtime-events.jsonl"
        if not events_path.is_file():
            continue
        try:
            raw = events_path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(event, dict):
                yield event


def aggregate(root: Path, issue_filter: str | None) -> dict[str, Any]:
    """Aggregate verification_run outcomes overall, per gate, and per issue."""
    outcomes: Counter[str] = Counter()
    by_gate: dict[str, Counter[str]] = {"verify": Counter(), "behaviour": Counter()}
    per_issue: dict[str, Counter[str]] = {}
    for event in _iter_events(root, issue_filter):
        if event.get("kind") != "verification_run":
            continue
        payload = event.get("payload") if isinstance(event.get("payload"), dict) else {}
        outcome = str(payload.get("outcome", "unknown"))
        gate = str(payload.get("gate") or "verify")
        outcomes[outcome] += 1
        bucket = by_gate.get(gate) or by_gate.setdefault(gate, Counter())
        bucket[outcome] += 1
        issue_id = str(event.get("issue_id", "?"))
        per_issue.setdefault(issue_id, Counter())[outcome] += 1
    total = sum(outcomes.values())
    fail_rate = (outcomes.get("fail", 0) / total) if total else 0.0
    return {
        "helper_version": HELPER_VERSION,
        "total_verification_runs": total,
        "outcomes": dict(outcomes),
        "by_gate": {g: dict(c) for g, c in by_gate.items()},
        "fail_rate": round(fail_rate, 4),
        "per_issue": {k: dict(v) for k, v in sorted(per_issue.items())},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="BEO sensor telemetry (advisory, read-only)")
    parser.add_argument("--root", default=".", help="Repo root")
    parser.add_argument("--issue", default=None, help="Limit to one issue id")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    print(json.dumps(aggregate(root, args.issue), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
