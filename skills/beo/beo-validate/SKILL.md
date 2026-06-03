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

## Do

1. Fresh-read `br`, ticket/plan, state when present, runtime events when present, and phase-relevant registries named above.
2. For epic/feature plan validation: confirm `PLAN.md` exists, references the parent bead, captures clarified requirements, and proposes atomic child beads with descriptions, done criteria, expected scope, verification, dependencies, and parent/plan links; emit `plan_validated`, `validation_failed`, or `user_review_needed`; stop. Never write `PASS_EXECUTE` for parent plans.
3. For atomic ticket validation: confirm the bead is claimed, open, atomic, and unchanged enough for the ticket.
4. Validate current `version: 1` ticket fields and mode requirements.
5. For strict mode, create or supersede the current actor's BEO reservation before computing approval validity predicates.
6. Reject dirty approved files, dirty declared generated outputs, unsafe paths, and unauthorized broad globs.
7. Write `PASS_EXECUTE` or a failed/blocked approval state.

## Write

- `state.json` phase and approval fields only
- `.beads/beo-reservations.jsonl` via `beo-reference -> scripts/beo_reservation.py` for strict-mode reservation create/supersede only
- Optional validation evidence under `.beads/artifacts/<issue-id>/checks/`
- Beads comments and labels for `user_stop` only, including `beo:blocked-user`
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
