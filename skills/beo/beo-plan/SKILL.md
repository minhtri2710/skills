---
name: beo-plan
description: "Scope one claimed Beads issue into BEO TICKET.yaml and initial state. Use for claim, atomic decomposition, and plan authoring. Never mutate product files."
---
# beo-plan

## Read

- `br show <issue-id> --json`
- `.beads/artifacts/<issue-id>/TICKET.yaml` when it already exists
- `.beads/artifacts/<issue-id>/state.json` when it already exists
- `.beads/artifacts/<issue-id>/runtime-events.jsonl` when present
- `beo-reference -> registry/ticket.schema.json` when writing or changing `TICKET.yaml`
- `beo-reference -> registry/state.schema.json` before initializing `state.json`
- `beo-reference -> registry/profiles.json` when checking scope or protected paths
- `beo-reference -> registry/runtime-event.schema.json` before appending runtime events
- `beo-reference -> registry/pipeline.json` when choosing the emitted route

## Do

1. Fresh-read the issue with `br`.
2. Claim the issue before any ticket or lifecycle write.
3. Record a compact atomicity rationale as a Beads comment or plan evidence ref, not as a `TICKET.yaml` field.
4. If the bead is not atomic, decompose into child beads and stop.
5. Write the smallest current `version: 1` `TICKET.yaml` for quick, standard, or strict mode.
6. Initialize `state.json` in planned state.

## Write

- `.beads/artifacts/<issue-id>/TICKET.yaml`
- `.beads/artifacts/<issue-id>/state.json` initialization only
- Beads lifecycle/decomposition comments and labels when needed, including `beo:blocked-user` for `user_stop`
- `runtime-events.jsonl` for `user_stop` only when a Human Gate blocks progress

## Emit

- `planned` -> `beo-validate`
- `decomposition_recorded` -> user
- `user_review_needed` -> user

## Never

- Do not mutate product files.
- Do not grant `PASS_EXECUTE`.
- Do not review or close work.
- Do not create legacy ticket fields or compatibility artifacts.
