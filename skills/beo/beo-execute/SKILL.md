---
name: beo-execute
description: "Implement one approved atomic BEO bead after PASS_EXECUTE. Use bv only for read-only orientation and br for authoritative ready/claim checks. Mutate only approved scope. Never approve, review, or close."
---
# beo-execute

## Read

- `bv` robot output only for optional read-only graph orientation or ready-work visualization
- `br ready --json` when choosing ready candidates
- `br show <issue-id> --json`
- `.beads/artifacts/<issue-id>/TICKET.json`
- `.beads/artifacts/<issue-id>/state.json`
- `.beads/artifacts/<issue-id>/runtime-events.jsonl` when present
- `beo-reference -> registry/approval-envelope.json` before checking approval validity predicates or mutating files
- `beo-reference -> registry/state.schema.json` before updating `state.json`
- `beo-reference -> registry/runtime-event.schema.json` before appending runtime events
- `beo-reference -> registry/pipeline.json` when choosing the emitted route
- `beo-reference -> registry/profiles.json` when checking fast track requirements
- `beo-reference -> scripts/beo_worktree.py` when strict ticket has `worktree_isolation: true`

## Do

1. When no issue is already selected, use `bv` only to orient in the dependency graph, then use `br ready --json` and `br show --json` as the authoritative source for ready candidates.
2. Fresh-read `br`, ticket, state, runtime events when present, and phase-relevant registries named above.
3. Verify the issue is open, claimed, unblocked, atomic, and materially consistent with the ticket.
4. Verify current `PASS_EXECUTE` validity predicates before first mutation.
5. If strict ticket has `worktree_isolation: true`, resolve the worktree path via `beo-reference -> scripts/beo_worktree.py status --issue <issue-id>`. All subsequent mutations run inside the worktree directory. Fail if no worktree exists.
6. Durably update `state.json` to `executing` with `execution.actor` and `execution.started_at` before product mutation.
7. Mutate only `scope.files.allow` and `scope.generated_outputs`. For worktree-isolated beads, paths resolve relative to the worktree root.
8. Run ticket verification commands inside the worktree.
9. Record changed files, verification results, and evidence refs in `state.json`. For worktree-isolated beads, record paths as repo-relative (strip worktree prefix).
10. If during execution a BEO harness improvement is identified (better validation rule, missing script, registry fix):
    - Write `.beads/artifacts/<issue-id>/harness-proposal.json` following `beo-reference -> registry/harness-proposal.schema.json`.
    - Emit `harness_change_needed` -> `beo-author`. The current bead pauses; `beo-author` returns to caller after resolution.
    - On return from `beo-author`, re-read state and continue execution if the bead remains valid.
    - Stop here; do not proceed to steps 11-12 (fast track or normal route).
11. If `TICKET.json` has `fast_track: true`:
   - Check all verification results. If ALL pass: write `state.json` with `phase: "reviewed"` and
     `review.route_condition_id: "executed_and_verified"`, `review.verdict: null`, `review.findings: []`,
     `review.repair_count: 0`, `review.closed_in_br: false`, `review.reviewed_by: "beo-execute"`.
     Do not populate `done_criteria_coverage` or `verdict` — fast track is an execution-side
     auto-completion, not a review verdict. The `reviewed_by` marker distinguishes this stub record
     from a real review by `beo-review`. Then emit `executed_and_verified` -> done. Do not emit
     `executed`. Do not call `br close`; beo-execute is not authorized to close. The issue remains
     open in `br` for user closure or follow-up work.
   - If ANY verification fails: fall back to normal path (emit `executed` -> `beo-review`). Fast track
     requires ALL verifications to pass; partial success routes to normal review.
12. Otherwise, emit `executed` -> `beo-review`. Append a `handoff` runtime event only before emitting
    `root_cause_diagnosis_needed` or `containment_review_needed`.
13. Optional: if a prior `intervention` runtime event exists for the same `trace_id` or `story_id` (per `beo-reference -> registry/runtime-event.schema.json` intervention payload), include its evidence ref in `state.json.execution.evidence_refs` before emitting. This is a context-aggregation step, not a phase change.

## Write

- Approved product files only
- Declared generated outputs only
- `state.json` phase and execution fields; also `state.json` review.route_condition_id and review.reviewed_by when fast track auto-completes (verdict stays null; closed_in_br stays false)
- `state.json.execution.interventions[]` (optional mirror of `intervention` runtime events that should survive the runtime event log)
- `.beads/artifacts/<issue-id>/harness-proposal.json` when proposing a harness change
- `runtime-events.jsonl` for `handoff` only when routing to `beo-debug` or `beo-review`
- Optional check evidence

## Emit

- `executed` -> `beo-review`
- `executed_and_verified` -> done (fast track, all verifications passed)
- `root_cause_diagnosis_needed` -> `beo-debug`
- `approval_stale_or_invalid` -> `beo-validate`
- `containment_review_needed` -> `beo-review`
- `harness_change_needed` -> `beo-author`

Non-normal `runtime-events.jsonl` events (advisory, optional): `verification_run` (when `beo_verify.py` is invoked), `intervention` (when external human, reviewer, or CI input is recorded during execution).

## Never

- Do not approve, validate, or close.
- Do not perform manual review (fast track auto-accept is an automated safety optimization, not a substitute for human or `beo-review` judgment).
- Do not treat `bv` as lifecycle, claim, approval, or closure authority.
- Do not mutate outside approved scope.
- Do not write normal success runtime events.
