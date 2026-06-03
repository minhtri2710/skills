---
name: beo-execute
description: "Implement one approved atomic BEO bead after PASS_EXECUTE. Use bv only for read-only orientation and br for authoritative ready/claim checks. Mutate only approved scope. Never approve, review, or close."
---
# beo-execute

## Read

- `bv` robot output only for optional read-only graph orientation or ready-work visualization
- `br ready --json` when choosing work from the executable queue
- `br show <issue-id> --json`
- `.beads/artifacts/<issue-id>/TICKET.yaml`
- `.beads/artifacts/<issue-id>/state.json`
- `.beads/artifacts/<issue-id>/runtime-events.jsonl` when present
- `beo-reference -> registry/approval-envelope.json` before checking approval validity predicates or mutating files
- `beo-reference -> registry/state.schema.json` before updating `state.json`
- `beo-reference -> registry/runtime-event.schema.json` before appending runtime events
- `beo-reference -> registry/pipeline.json` when choosing the emitted route

## Do

1. When no issue is already selected, use `bv` only to orient in the dependency graph, then use `br ready --json` and `br show --json` as the authoritative source for executable work.
2. Fresh-read `br`, ticket, state, runtime events when present, and phase-relevant registries named above.
3. Verify the issue is open, claimed, unblocked, atomic, and materially consistent with the ticket.
4. Verify current `PASS_EXECUTE` validity predicates before first mutation.
5. Durably update `state.json` to `executing` with `execution.actor` and `execution.started_at` before product mutation.
6. Mutate only `scope.files.allow` and `scope.generated_outputs`.
7. Run ticket verification commands.
8. Record changed files, verification results, and evidence refs in `state.json`.
9. Append a `handoff` runtime event before emitting `root_cause_diagnosis_needed` or `containment_review_needed`.

## Write

- Approved product files only
- Declared generated outputs only
- `state.json` phase and execution fields only
- `runtime-events.jsonl` for `handoff` only when routing to `beo-debug` or `beo-review`
- Optional check evidence

## Emit

- `executed` -> `beo-review`
- `root_cause_diagnosis_needed` -> `beo-debug`
- `approval_stale_or_invalid` -> `beo-validate`
- `containment_review_needed` -> `beo-review`

## Never

- Do not approve, validate, review, or close.
- Do not treat `bv` as lifecycle, claim, approval, or closure authority.
- Do not mutate outside approved scope.
- Do not write normal success runtime events.
