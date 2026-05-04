# BEO Go Mode

Go mode is an operator macro for running the normal BEO pipeline from feature
intake to terminal closure. It is not a separate owner, not an expedited
execution path, and does not override routing, approval, state, writable-
surface doctrine, locked requirements, `beo-validate`, `PASS_EXECUTE`,
selected execution-set scope, or review.

## Happy path

`beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> beo-compound? -> done`

Use `beo-dream` only when the cross-feature consolidation threshold is met.

## Gate mapping

| Gate | Owner | Artifact |
| --- | --- | --- |
| requirements locked | `beo-explore` | `CONTEXT.md` |
| current phase executable | `beo-plan` | `PLAN.md` + bead graph |
| execution approved and classified | `beo-validate` | `approval-record.json` + `STATE.json` readiness/mode |
| terminal verdict | `beo-review` | `REVIEW.md` |
| learning disposition | `beo-review` / `beo-compound` / `beo-dream` | inline no-learning or learning record |

Gate names are display labels only. They must not create separate approval or
gate records. Go Mode cards are display-only; they cannot approve, route,
validate, dispatch, accept, reject, or promote learning.

Display-card authority and output shapes are canonical in `beo-reference -> operator-card.md`.

## Operator behavior

- Go mode suppresses unnecessary user questions; it does not suppress owner selection.
- Go mode may persist across legal owner handoffs within the same authorized feature scope.
- Go mode must not bypass `beo-route` when owner collision exists.
- Go mode must not bypass `beo-validate` before execution.
- Go mode must not bypass external approval, secrets/access, legal/business decisions, or approved file scope changes.

## Default assumption rule

When `go_mode.active=true`, do not route to `user` for design-only or
implementation-detail ambiguity that does not change acceptance, non-goals,
compatibility, external approval, secret/access, legal/business decision,
approved file scope, or verification.

Proceed with a conservative assumption and record it in:
- `CONTEXT.md` if it affects requirements
- `PLAN.md` if it affects approach only
- `STATE.json.operator_view` if it affects current operator awareness

## Edge cases

| Case | Expected behavior |
| --- | --- |
| User says "go implement" but requirements are missing or contradicted | route through requirements locking first |
| User says "go" but approval is stale or missing | validate/approval flow first |
| User says "go" during an execution blocker with unproven root cause | use `beo-debug` when the legal owner routes there |
| User says "skip review" | refuse the shortcut; review remains required |
| User says "just implement" before `PASS_EXECUTE` | no execution; `beo-validate` must emit `PASS_EXECUTE` first |
| Broad instruction conflicts with locked requirements | repair requirements before planning or execution |
