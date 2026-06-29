---
name: beo-execute
description: "Implement one approved atomic BEO bead after PASS_EXECUTE. Use bv only for read-only orientation and br for authoritative ready/claim checks. Mutate only approved scope. Never approve, review, or close."
---
# beo-execute

## Read

- `beo-reference -> references/default-reads.md`
- `bv` robot output only for optional read-only graph orientation or ready-work visualization
- `br ready --json` when choosing ready candidates
- `beo-reference -> registry/approval-envelope.json` before checking approval validity predicates or mutating files
- `beo-reference -> registry/state.schema.json` before updating `state.json`
- `beo-reference -> registry/profiles.json` when checking fast track requirements
- `beo-reference -> scripts/beo_worktree.py` when strict ticket has `worktree_isolation: true`

## Do

1. When no issue is already selected, use `bv` only to orient in the dependency graph, then use `br ready --json` and `br show --json` as the authoritative source for ready candidates. Fresh-read `br`, ticket, state, runtime events when present, and phase-relevant registries named above.
2. Verify the issue is open, claimed, unblocked, atomic, and materially consistent with the ticket, and that current `PASS_EXECUTE` validity predicates hold. Done when: `br show <id>` confirms open + claimed-by-current-actor + unblocked + atomic; ticket is materially consistent; approval validity predicates are all green.
3. If strict ticket has `worktree_isolation: true`, resolve the worktree path via `beo-reference -> scripts/beo_worktree.py status --issue <issue-id>`. All subsequent mutations run inside the worktree directory. Fail if no worktree exists.
4. Durably update `state.json` to `executing` with `execution.actor` and `execution.started_at` before product mutation. Mutate only `scope.files.allow` and `scope.generated_outputs`. For worktree-isolated beads, paths resolve relative to the worktree root. Run ticket verification commands inside the worktree. Record changed files, verification results, and evidence refs in `state.json`. For worktree-isolated beads, record paths as repo-relative (strip worktree prefix). Done when: `state.json.phase == "executing"`, `execution.actor` and `execution.started_at` set, mutations only in approved scope or generated outputs, verify results recorded, evidence refs present.
5. If during execution a BEO harness improvement is identified (better validation rule, missing script, registry fix):
    - Write `.beads/artifacts/<issue-id>/harness-proposal.json` following `beo-reference -> registry/harness-proposal.schema.json`.
    - Emit `harness_change_needed` -> `beo-author`. The current bead pauses; `beo-author` returns to caller after resolution.
    - On return from `beo-author`, re-read state and continue execution if the bead remains valid.
    - Stop here; do not proceed to step 6 (final emit).
6. If `TICKET.json` has `fast_track: true`:
   - Check all verification results. If ALL pass: write the fast-track auto-accept stub in `state.json` per `beo-reference -> references/lifecycle.md` §4 (Fast Track) and `registry/state.schema.json`. Do not populate `done_criteria_coverage` or `verdict` — fast track is an execution-side auto-completion, not a review verdict. The `reviewed_by` marker distinguishes this stub record from a real review by `beo-review`. Then emit `executed_and_verified` -> done. Do not emit `executed`. Do not call `br close`; beo-execute is not authorized to close. The issue remains open in `br` for user closure or follow-up work.
   - If ANY verification fails: fall back to normal path (emit `executed` -> `beo-review`). Fast track requires ALL verifications to pass; partial success routes to normal review.
   Done when: ALL verifications pass and the auto-accept stub is written, OR ANY verification fails and `executed` is emitted to `beo-review`.
7. Otherwise, emit `executed` -> `beo-review`. Append a `handoff` runtime event only before emitting
    `root_cause_diagnosis_needed` or `containment_review_needed`.
8. Optional: if a prior `intervention` runtime event exists for the same `trace_id` or `story_id` (per `beo-reference -> registry/runtime-event.schema.json` intervention payload), include its evidence ref in `state.json.execution.evidence_refs` before emitting. This is a context-aggregation step, not a phase change.
9. When dispatching execution work to a background or parallel subagent (operator-initiated, not beo-execute-internal):
    - Append a `handoff` runtime event with the subagent id and target `trace_id` (or `story_id`) before any product mutation. This preserves audit trail and satisfies Hard Invariant #3 (`beo-reference -> references/kernel.md` §2.3) in spirit when the actor is parallelizing.
    - Confirm the subagent model tier can read files before dispatch. Model tiers that fail on file reads (e.g. haiku-tier in observed failures) are not safe for code-touching subagents; use a tier that handles file I/O.
    - Record the subagent id and intended scope in a Beads comment on the issue as a durable audit-trail row.
    - Do not skip `state.json` phase updates; the operator (or a follow-up call to `beo_run.py`) still owns the `executing` -> `executed` -> `reviewed` sequence.

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

- See `beo-reference -> registry/phase-contracts.json` `must_not[]`; audit C8 enforces drift.
- Do not approve, validate, or close.
- Do not perform manual review (fast track auto-accept is an automated safety optimization, not a substitute for human or `beo-review` judgment).
- Do not treat `bv` as lifecycle, claim, approval, or closure authority.
- Do not mutate outside approved scope.
- Do not write normal success runtime events.
