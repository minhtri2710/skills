---
name: beo-debug
description: "Diagnose BEO execution or review blockers without repair authority. Returns root-cause evidence to the calling owner. Never approves, repairs, reviews, or closes."
---
# beo-debug

## Read

- `br show <issue-id> --json`
- `.beads/artifacts/<issue-id>/TICKET.yaml` and `state.json`
- `.beads/artifacts/<issue-id>/runtime-events.jsonl` when present
- Caller-provided evidence/log files
- `beo-reference -> registry/runtime-event.schema.json` before appending caller-routed runtime events

## Input

May be invoked only by `beo-execute`, `beo-review`, or an explicit operator request to diagnose a BEO blocker. Two modes:
1. **Caller-routed**: from `beo-execute` or `beo-review`. Required input: `caller_skill`, `issue_id`, `caller_route_context`, blocker summary, evidence/log refs, optional allowed read-only probes, and expected durable return channel.
2. **Standalone**: explicit operator diagnosis — read-only, no runtime events.

## Output

Returns: `caller_skill`, `caller_route_context`, `root_cause_status` (`proven | likely | insufficient_evidence`), `root_cause`, `evidence_refs`, `recommended_next_route`, `safe_repair_boundary`. Never decides the delivery route — the caller fresh-reads state and artifacts, consumes output, and emits the actual route.

## Do

1. Reproduce or inspect the blocker using read-only probes where possible.
2. Identify the smallest proven root cause or the next missing evidence.
3. Return diagnosis to the calling BEO owner.
4. For caller-routed debug only, optionally append a `return` or `learning_candidate_suggestion` runtime event when a durable return channel exists.

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
