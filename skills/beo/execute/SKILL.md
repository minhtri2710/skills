---
name: beo-execute
description: Implement approved code changes and record execution evidence for an atomic Beads ticket with current PASS_EXECUTE. Always use this skill when starting coding, mutating files within scope.files.allow, running the verification commands, or writing implementation status. Trigger this whenever the user says "implement this", "write the code", "fix the bug", or "start coding."
requires: br>=0.1.28
---
# beo-execute

## Use when

A claimed atomic issue has a current validation-owned `PASS_EXECUTE` and the next action is bounded implementation.

## Read

- Claimed issue state from `br show <issue-id> --json`.
- Plan-owned `TICKET.md` and validate-owned `state.json` approval evidence.
- Relevant `runtime-events.jsonl` entries when handoff, repair, blocker, or abandon history affects execution.
- `beo-reference` canonical contracts: `references/kernel.md`, `references/safety.md`, `registry/approval-envelope.json`, `registry/ticket-schema.json`, `registry/pipeline.json`, and `registry/command-contracts.json`.

## Repair Handoff Semantics

When execution follows a repair route from `beo-review`, the repair event context guides the implementation:

### After `repair_same_scope`
- Approval boundaries are unchanged; only within-scope code refinement is allowed.
- Same-scope repair delta boundaries to preserve are defined in `pipeline.json repair_loop_policy.same_scope_repair_delta`.
- Review findings guide what to fix, but scope/acceptance/gates/side-effects remain frozen.
- If repair requires scope expansion, emit `scope_delta_required` -> `beo-plan` instead of attempting out-of-scope changes.

### After `repair_rescope`
- Planning has revised scope, acceptance, gates, or side effects
- Validation has issued new `PASS_EXECUTE` with updated approval projection
- Execute as normal with the new approval boundaries

### Repair Counter Awareness
- Execute does not increment or check repair counter (review owns repair budget enforcement)
- If execution fails and review must repair again, review will check repair budget before emitting next repair route
- If repair budget is exceeded, review routes `repair_budget_exceeded` -> user, not back to execute

## Do

1. Confirm claim, current `PASS_EXECUTE`, approval projection, prestate hashes, and reservation status when required.
2. Mutate only `scope.files.allow` and declared generated outputs.
3. Stop for `beo-plan` if scope must expand or acceptance must change.
4. Stop for `beo-validate` if approval or prestate is stale.
5. Run the ticket verification commands and containment checks.
6. Record changed paths, verification output, and execution evidence.

## Write

- Product file changes strictly within approved scope.
- Declared generated outputs only when approved.
- Execution-owned `state.json` fields and evidence refs.
- Runtime events for blocker, scope delta, abandon, or ready-for-review handoff when needed.

## Emit

- `execution_ready_for_review` -> stop and load `beo-review`.
- `approval_stale_or_invalid` -> stop and load `beo-validate`.
- `scope_delta_required` -> stop and load `beo-plan`.
- `blocker_found` -> stop and load `beo-debug`.
- `user_blocker` -> stop for user input.
- `abandoned` -> stop and load `beo-review`.

## Never

- Do not mutate outside approved scope (containment checks fail closed on any unauthorized or dirty file changes).
- Do not grant, refresh, or reinterpret `PASS_EXECUTE` (only validate can write approval sentinels).
- Do not redesign scope, acceptance, or Human Gates (if constraints block coding, emit scope_delta_required and return to plan).
- Do not issue review verdicts or close issues (review owns final closure verdicts).
- Do not load another BEO delivery owner in the same turn for the same issue after emitting; stop first.
