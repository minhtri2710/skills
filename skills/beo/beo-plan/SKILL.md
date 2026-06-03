---
name: beo-plan
description: "Plan BEO work from Beads issues. Use for epic requirement intake, recommended clarification, PLAN.md creation, validated atomic decomposition, and atomic TICKET.yaml/state authoring. Never mutate product files."
---
# beo-plan

## Read

- `br show <issue-id> --json`
- `.beads/artifacts/<issue-id>/PLAN.md` when it already exists
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
2. Claim the issue before any plan, ticket, or lifecycle write.
3. For an epic or feature, combine the user request with bead context and ask recommended clarification questions until scope, non-goals, assumptions, constraints, done criteria, verification strategy, risks, and decomposition boundaries are clear.
4. Write `.beads/artifacts/<issue-id>/PLAN.md` with the parent bead id, requirement summary, assumptions, scope, non-goals, risks, verification strategy, decomposition strategy, proposed atomic beads, and unresolved decisions.
5. Emit `planned -> beo-validate` for `PLAN.md` validation.
6. On re-entry after `plan_validated`, create child atomic beads, dependency edges, and a parent summary comment that references `PLAN.md`, then stop.
7. For an atomic bead, record a compact atomicity rationale as a Beads comment or plan evidence ref, not as a `TICKET.yaml` field.
8. Write the smallest current `version: 1` `TICKET.yaml` for quick, standard, or strict mode.
9. Initialize `state.json` in planned state.

## Write

- `.beads/artifacts/<issue-id>/PLAN.md` for epic/feature planning only
- `.beads/artifacts/<issue-id>/TICKET.yaml`
- `.beads/artifacts/<issue-id>/state.json` initialization only
- Beads lifecycle/decomposition comments, child beads, dependency edges, and labels when needed, including `beo:blocked-user` for `user_stop`
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
