---
name: beo-review
description: "Review one executed atomic BEO bead against its self-contained description, TICKET.json scope, evidence, verification, and done criteria. Emits one route; only this skill may close accepted work."
---
# beo-review

## Read

- `beo-reference -> references/default-reads.md`
- `.beads/artifacts/<parent-issue-id>/PLAN.md` only when review evidence or an explicit inconsistency requires parent-boundary audit; child descriptions should be self-contained
- `.beads/beo-reservations.jsonl` and `beo-reference -> registry/reservation-schema.json` before any route that may release an existing reservation
- `beo-reference -> scripts/beo_worktree.py` when the bead has `worktree_isolation: true` (for merge or cleanup)
- `beo-reference -> registry/state.schema.json` when state update ownership or fields are unclear

## Do

1. Fresh-read `br`, ticket, state, runtime events when present, phase-relevant registries named above, and any referenced evidence. If the atomic bead was decomposed from an epic/feature, review against the self-contained child bead description; read the parent `PLAN.md` only when the child description is ambiguous, review evidence explicitly references it, or a suspected parent-boundary conflict cannot be resolved from the child bead and `TICKET.json`.
2. Apply the review rubric:
   - Scope: every changed file is allowed by `TICKET.json` or declared generated outputs.
   - Intent: the implementation satisfies the self-contained child bead description.
   - Done criteria: each criterion is covered by evidence or explicitly marked not covered.
   - Verification: recorded command results actually support the done criteria, not merely command execution.
   - Regression surface: obvious adjacent behavior affected by the touched files is considered.
   - Repair boundary: same-scope repair is allowed only when file set, generated outputs, done criteria, verification, mode, risk, and Human Gates remain unchanged.
   Done when: each of the 6 rubric items evaluated and recorded as evidence-backed pass/fail.
3. Audit changed files against approved scope and generated outputs; confirm verification results cover `scope.verify.commands` and `done_criteria`; record compact done-criteria coverage. Only emit `verdict_accept` when scope, intent, done criteria coverage, and verification evidence all support acceptance. If evidence is missing but work may be correct, route repair or user decision; do not accept on trust. Done when: every changed file in approved scope or generated outputs; verification covers both `scope.verify.commands` and `done_criteria`; coverage recorded; `verdict_accept` only when all 4 conditions (scope, intent, coverage, evidence) hold.
4. Record findings with severity, category, message, evidence refs, and recommended route; the final route must be derivable from findings. For `user_review_needed`, the route may be derived from `review.route_condition_id`, blocking findings with `recommended_route: none`, and the Beads decision envelope. Emit exactly one review route.
5. For `root_cause_diagnosis_needed`, set the route condition, leave `review.verdict` null, and append a `handoff` runtime event before routing to `beo-debug`. Use `repair_same_scope` only when approved files, generated outputs, done criteria, verification, mode, risk, and Human Gates remain unchanged; otherwise use `repair_rescope`.
6. For beads with `worktree_isolation: true`:
    - On `verdict_accept`: merge the worktree branch via `beo-reference -> scripts/beo_worktree.py merge --issue <issue-id>`, then cleanup via `beo-reference -> scripts/beo_worktree.py cleanup --issue <issue-id> --reason accepted`.
    - On `repair_same_scope` or `repair_rescope`: cleanup without merge via `beo-reference -> scripts/beo_worktree.py cleanup --issue <issue-id> --reason repair`.
    - On `cannot_deliver` or `abandoned`: cleanup via `beo-reference -> scripts/beo_worktree.py cleanup --issue <issue-id> --reason <route>`.
7. If during review a BEO harness improvement is identified:
    - Write `.beads/artifacts/<issue-id>/harness-proposal.json` following `beo-reference -> registry/harness-proposal.schema.json`.
    - Emit `harness_change_needed` -> `beo-author`. The review is paused; `beo-author` returns to caller after resolution.
    - On return from `beo-author`, re-read state and continue review.
8. Close with `br` only on `verdict_accept`; otherwise leave the issue open for repair or user action. When emitting `user_review_needed`, set `review.route_condition_id` to `user_review_needed`, leave `review.verdict` null, record blocking findings with existing categories and `recommended_route: none` when no enum route applies, and follow the `user_review_needed` handoff format in `beo-reference -> references/user-handoff.md`. Do not write a `user_stop` runtime event for review user decisions.

## Write

- `state.json` phase and review fields only
- `.beads/artifacts/<issue-id>/harness-proposal.json` when proposing a harness change
- Beads comments/labels for the final route when needed, including compact `user_review_needed` route comments and labels only when an existing BEO label represents the state
- Reservation release on `verdict_accept`, `cannot_deliver`, `abandoned`, and `repair_rescope` only for strict-mode active reservations or when a reservation exists
- `runtime-events.jsonl` for non-normal review events, including `handoff` before `root_cause_diagnosis_needed`
- Optional `learning_candidate` only after a final route and only when high-signal

## Emit

- `verdict_accept` -> close accepted work
- `repair_same_scope` -> `beo-validate`
- `repair_rescope` -> `beo-plan`
- `cannot_deliver` -> user
- `abandoned` -> user
- `root_cause_diagnosis_needed` -> `beo-debug`
- `harness_change_needed` -> `beo-author`
- `user_review_needed` -> user

Non-normal `runtime-events.jsonl` events (advisory, optional): `verification_run` (when `beo_verify.py` is invoked during review), `intervention` (when external human, CI, or reviewer input is recorded).

## Never

- See `beo-reference -> registry/phase-contracts.json` `must_not[]`; audit C8 enforces drift.
- Do not mutate product files.
- Do not grant `PASS_EXECUTE`.
- Do not close non-accepted work.
- Do not emit more than one review route.
