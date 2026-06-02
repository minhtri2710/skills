---
name: beo-debug
description: "Diagnose BEO execution or review blockers without repair authority. Returns root-cause evidence to the calling owner. Never approves, repairs, reviews, or closes."
---
# beo-debug

## Read

- `br show <issue-id> --json`
- `.beads/artifacts/<issue-id>/TICKET.yaml` and `state.json`
- `.beads/artifacts/<issue-id>/runtime-events.jsonl` when present
- Evidence/log files referenced by the caller
- `beo-reference -> registry/runtime-event.schema.json` before appending caller-routed runtime events

## Caller contract

`beo-debug` may be invoked only by:

1. `beo-execute`,
2. `beo-review`,
3. or an explicit operator request to diagnose a BEO blocker.

Two modes are allowed:

1. Caller-routed debug from `beo-execute` or `beo-review`.
2. Standalone explicit operator diagnosis of a BEO blocker.

Required caller-routed input:

- `caller_skill`: `beo-execute` or `beo-review`
- `issue_id`
- `caller_route_context`: the route or blocked transition that requested diagnosis
- blocker summary
- evidence/log refs
- allowed read-only probes, if any
- expected durable return channel

## Return contract

Return:

- `caller_skill`
- `caller_route_context`
- `root_cause_status`: `proven | likely | insufficient_evidence`
- `root_cause`
- `evidence_refs`
- `recommended_next_route`
- `safe_repair_boundary`

`beo-debug` never decides the delivery route. The caller fresh-reads `state.json` and current artifacts, consumes debug output, and emits the actual delivery route.

## Do

1. Reproduce or inspect the blocker using read-only probes where possible.
2. Identify the smallest proven root cause or the next missing evidence.
3. Return diagnosis to the calling BEO owner.
4. For caller-routed debug only, optionally append a debug `return` or `learning_candidate_suggestion` runtime event when `caller_skill`, `caller_route_context`, and a durable return channel exist.

## Write

- No product files.
- No delivery state.
- Optional caller-routed `runtime-events.jsonl` event of kind `return` or `learning_candidate_suggestion` only when `caller_skill`, `caller_route_context`, and a durable return channel exist; standalone diagnosis is read-only/advisory; final candidates belong to review.

## Emit

- `debug_returned` -> caller
- `debug_abandoned` -> caller

## Never

- Do not repair code.
- Do not grant approval.
- Do not issue review verdicts.
- Do not close issues.
- Do not emit final `learning_candidate`.
