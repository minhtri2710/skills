# BEO Go Mode

Go mode is an operator macro for running the normal BEO pipeline from feature
intake to terminal closure. It is not a separate owner and does not override
routing, approval, state, or writable-surface doctrine.

## Happy path

`beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute | beo-swarm -> beo-review -> beo-compound? -> done`

Use `beo-dream` only when the cross-feature consolidation threshold is met.

## Gate mapping

| Gate | Owner | Artifact |
| --- | --- | --- |
| requirements locked | `beo-explore` | `CONTEXT.md` |
| current phase executable | `beo-plan` | `PLAN.md` + bead graph |
| execution approved and classified | `beo-validate` | `approval-record.json` + `STATE.json` readiness/mode |
| terminal verdict | `beo-review` | `REVIEW.md` |
| learning disposition | `beo-review` / `beo-compound` / `beo-dream` | inline no-learning or learning record |

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
