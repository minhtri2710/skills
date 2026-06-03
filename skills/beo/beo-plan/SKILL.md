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
- `beo-reference -> templates/PLAN.template.md` when writing or decomposing a parent `PLAN.md`

## Do

1. Fresh-read the issue with `br`.
2. Claim the issue before any plan, ticket, or lifecycle write.
3. For an epic or feature, combine the user request with bead context and produce one clarification batch when needed. Each question must include why it matters, a recommended default, and the fallback assumption BEO will use if unanswered. Do not ask endless questions. If safe defaults exist, write `PLAN.md` with explicit assumptions. Use `user_review_needed` only when a missing decision affects risk mode, broad scope, human authorization, external side effects, irreversible behavior, or safe decomposition.
4. Write `.beads/artifacts/<issue-id>/PLAN.md` using `beo-reference/templates/PLAN.template.md`. The plan must include parent-level completion criteria, explicit assumptions, scope boundaries, verification strategy, and proposed atomic beads detailed enough that `beo-plan` can later create child Beads without re-interpreting the parent requirement or risk/mode needs.
5. Emit `planned -> beo-validate` for `PLAN.md` validation.
6. Planning stop rule: after `PLAN.md` is written, emit `planned -> beo-validate` and stop. Do not create child beads until re-entering after `plan_validated`.
7. On re-entry after `plan_validated`, create child atomic beads directly from the validated `PLAN.md` proposed atomic beads, dependency edges, and a parent summary comment that references `PLAN.md`, then stop. Do not reinterpret parent requirements outside the validated plan.
8. For an atomic bead, record a compact atomicity rationale as a Beads comment or plan evidence ref, not as a `TICKET.yaml` field.
9. Write the smallest current `version: 1` `TICKET.yaml` for quick, standard, or strict mode.
10. Initialize `state.json` in planned state.
11. When emitting `user_review_needed`, include a compact handoff subtype, blocking question, recommended option, fallback if any, and evidence refs in the Beads comment or handoff text. Do not emit a vague user handoff.

## Write

- `.beads/artifacts/<issue-id>/PLAN.md` for epic/feature planning only
- `.beads/artifacts/<issue-id>/TICKET.yaml`
- `.beads/artifacts/<issue-id>/state.json` initialization only
- Beads lifecycle/decomposition comments, child beads, dependency edges, compact `user_review_needed` route comments, and labels when needed, including `beo:blocked-user` only when an existing BEO label represents the state
- `runtime-events.jsonl` for `user_stop` only when a Human Gate blocks progress

## Emit

- `planned` -> `beo-validate`
- `decomposition_recorded` -> user
- `user_review_needed` -> user

## Never

- Do not mutate product files.
- Do not grant `PASS_EXECUTE`.
- Do not review or close work.
- Do not create fields outside the current canonical ticket or plan contracts.
