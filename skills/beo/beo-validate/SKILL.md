---
name: beo-validate
description: "Validate BEO PLAN.md readiness or grant/deny PASS_EXECUTE for atomic tickets. Checks claim, ticket shape, scope, mode, dirty prestate, and approval validity. Never execute or review."
---
# beo-validate

## Read

- `br show <issue-id> --json`
- `.beads/artifacts/<issue-id>/PLAN.md` when validating epic/feature decomposition readiness
- `.beads/artifacts/<issue-id>/TICKET.yaml` when validating an atomic ticket
- `.beads/artifacts/<issue-id>/state.json` when present
- `.beads/artifacts/<issue-id>/runtime-events.jsonl` when present
- `.beads/beo-reservations.jsonl` and `beo-reference -> registry/reservation-schema.json` for strict mode
- `beo-reference -> scripts/beo_reservation.py` before creating, superseding, or checking strict reservations
- `beo-reference -> registry/ticket.schema.json` for ticket shape
- `beo-reference -> registry/approval-envelope.json` before writing `PASS_EXECUTE`
- `beo-reference -> registry/profiles.json` for protected paths and broad globs
- `beo-reference -> registry/runtime-event.schema.json` before appending runtime events
- `beo-reference -> registry/pipeline.json` when choosing the emitted route
- `beo-reference -> templates/PLAN.template.md` when validating epic/feature decomposition readiness

## Do

1. Fresh-read `br`, ticket/plan, state when present, runtime events when present, and phase-relevant registries named above.
2. For epic/feature plan validation: validate `.beads/artifacts/<issue-id>/PLAN.md` against `beo-reference/templates/PLAN.template.md`. Confirm it references the parent bead, states goals and non-goals, gives overall completion criteria, records assumptions, records brainstorm/options considered for non-trivial planning with one recommended selected direction and rationale unless a blocking user/operator-owned decision prevents safe convergence, aligns the decision summary with that recommendation, defines scope boundaries, gives a verification strategy, and proposes atomic child beads as detailed markdown task descriptions with self-contained implementation context, done criteria, expected scope, verification guidance, dependencies, suggested mode/risk, and atomicity rationale sufficient to author child Beads and quick, standard, or strict child tickets without rereading the parent `PLAN.md`. Do not require parent-plan task-completion checkboxes; decomposition tracking belongs to child Beads and dependency edges. Emit `plan_validated`, `validation_failed`, or `user_review_needed`; then stop. Never write `PASS_EXECUTE` for parent plans, and never emit `plan_validated` while a blocking user/operator-owned open decision remains.
3. When plan validation fails, report missing sections or ambiguous atomic boundaries as findings. Do not patch the plan directly. Route `validation_failed -> beo-plan` unless the missing decision requires user authority, in which case route `user_review_needed -> user` with compact handoff details.
4. For atomic ticket validation: confirm the bead is claimed, open, atomic, and unchanged enough for the ticket.
5. Validate current `version: 1` ticket fields and mode requirements.
6. For strict mode, create or supersede the current actor's BEO reservation before computing approval validity predicates.
7. Reject dirty approved files, dirty declared generated outputs, unsafe paths, and unauthorized broad globs.
8. Write `PASS_EXECUTE` or a failed/blocked approval state.
9. When emitting `user_review_needed`, include a compact handoff subtype, blocking question, recommended option, fallback if any, and evidence refs in the Beads comment or handoff text. Do not emit a vague user handoff.

## Write

- `state.json` phase and approval fields only for atomic ticket validation
- `.beads/beo-reservations.jsonl` via `beo-reference -> scripts/beo_reservation.py` for strict-mode reservation create/supersede only
- Optional validation evidence under `.beads/artifacts/<issue-id>/checks/`
- Beads comments for compact `user_review_needed` route handoffs, and labels for `user_stop` only when an existing BEO label represents the state, including `beo:blocked-user`
- `runtime-events.jsonl` for `user_stop` only when a Human Gate blocks progress

## Emit

- `PASS_EXECUTE` -> `beo-execute`
- `plan_validated` -> `beo-plan`
- `validation_failed` -> `beo-plan`
- `user_review_needed` -> user

## Never

- Do not patch the plan.
- Do not mutate product files.
- Do not execute verification commands that change product state.
- Do not review or close work.
