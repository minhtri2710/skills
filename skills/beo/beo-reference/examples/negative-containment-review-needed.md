# Negative Trace: Containment Review Needed

This trace illustrates an interrupted execution that created attributable dirty paths outside of the approved scope.

## Scenario

- `beo-execute` starts execution in `executing` phase.
- An interrupted run modifies `unrelated.py` (which is not allowed in `TICKET.yaml`).
- Upon re-entering, `beo-execute` detects `unrelated.py` is modified and attributes it to the current BEO execution run.
- `beo-execute` must fail closed and route to review for containment.

## Handoff event appended to runtime-events.jsonl

```json
{
  "issue_id": "br-105",
  "kind": "handoff",
  "phase": "executing",
  "actor": "beo-execute",
  "timestamp": "2026-06-02T13:20:00Z",
  "payload": {
    "to": "beo-review",
    "condition_id": "containment_review_needed",
    "reason": "Attributable dirty files found outside approved scope: unrelated.py",
    "evidence_refs": []
  }
}
```

## State delta after handoff

```json
{
  "phase": "blocked",
  "metadata": {
    "last_owner": "beo-execute",
    "updated_at": "2026-06-02T13:20:00Z"
  }
}
```

## Expected Route

- **Condition**: `containment_review_needed`
- **Route**: `containment_review_needed` -> `beo-review`

## Outcomes

- `beo-review` must audit the containment path.
- `beo-review` must never emit `verdict_accept` for attributable out-of-scope mutations.
- Normal `executed` completion is forbidden.
