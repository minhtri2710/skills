---
name: beo-validate
description: "Grant or deny PASS_EXECUTE for a planned BEO ticket. Checks claim, ticket shape, scope, mode, dirty prestate, and approval validity. Never execute or review."
---
# beo-validate

## Read

- `br show <issue-id> --json`
- `.beads/artifacts/<issue-id>/TICKET.yaml`
- `.beads/artifacts/<issue-id>/state.json`
- `.beads/artifacts/<issue-id>/runtime-events.jsonl` when present
- `.beads/beo-reservations.jsonl` and `beo-reference -> registry/reservation-schema.json` for strict mode
- `beo-reference -> scripts/beo_reservation.py` before creating, superseding, or checking strict reservations
- `beo-reference -> registry/ticket.schema.json` for ticket shape
- `beo-reference -> registry/approval-envelope.json` before writing `PASS_EXECUTE`
- `beo-reference -> registry/profiles.json` for protected paths and broad globs
- `beo-reference -> registry/runtime-event.schema.json` before appending runtime events
- `beo-reference -> registry/pipeline.json` when choosing the emitted route

## Do

1. Fresh-read `br`, ticket, state, runtime events when present, and phase-relevant registries named above.
2. Confirm the bead is claimed, open, atomic, and unchanged enough for the ticket.
3. Validate current `version: 1` ticket fields and mode requirements.
4. For strict mode, create or supersede the current actor's BEO reservation before computing approval validity predicates.
5. Reject dirty approved files, dirty declared generated outputs, unsafe paths, and unauthorized broad globs.
6. Write `PASS_EXECUTE` or a failed/blocked approval state.

## Write

- `state.json` phase and approval fields only
- `.beads/beo-reservations.jsonl` via `beo-reference -> scripts/beo_reservation.py` for strict-mode reservation create/supersede only
- Optional validation evidence under `.beads/artifacts/<issue-id>/checks/`
- Beads comments and labels for `user_stop` only, including `beo:blocked-user`
- `runtime-events.jsonl` for `user_stop` only when a Human Gate blocks progress

## Emit

- `PASS_EXECUTE` -> `beo-execute`
- `validation_failed` -> `beo-plan`
- `user_review_needed` -> user

## Never

- Do not patch the plan.
- Do not mutate product files.
- Do not execute verification commands that change product state.
- Do not review or close work.
