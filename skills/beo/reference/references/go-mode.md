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

Gate names are display labels only. They must not create separate approval or
gate records. Go Mode cards are display-only; they cannot approve, route,
validate, dispatch, accept, reject, or promote learning.

## Operator sequence

Use the smallest safe ceremony from `beo-reference -> complexity.md`.

| Step | Operator display | Required owner evidence |
| --- | --- | --- |
| intake | "requirements are locked" | `CONTEXT.md` has acceptance, non-goals, compatibility, constraints |
| planning | "current phase is executable" | `PLAN.md` has phase, beads, scope, verification, and risk proof required by planning depth |
| validation | "execution envelope is current" | approval envelope binds beads, mode, scope, forbidden paths, verification, and freshness inputs |
| execution | "approved work is being delivered" | serial bead or swarm proof remains inside the approval envelope |
| review | "review evidence is ready" | evidence bundle proves acceptance, scope, verification, and decision/UAT coverage |
| closure | "learning disposition is settled" | `no-learning`, feature learning, or cross-feature consolidation threshold is recorded |

## Display-only checkpoint cards

Use this shape only for operator-visible progress summaries:

```md
Observed:
Evidence checked:
Why this matters:
Canonical owner/reference:
Continue via:
Authority note: This card is advisory/display only. Binding authority remains with the named Beo owner and canonical reference.
```

Checkpoint cards may cover startup/route sanity, requirements, plan/approval,
serial execution, swarm dispatch, review, and learning. They must not use binding
fields such as `Approved`, `Selected owner`, `Readiness verdict`, `Final verdict`,
`Promotion decision`, `Gate passed`, `PASS_SERIAL`, or `PASS_SWARM` outside the
canonical owner output that actually owns that decision.

When the canonical deciding owner emits its own output, use:

```md
Authority note: This output is valid only when emitted by the named Beo owner. It does not create authority for status, scout, guide, specialist, or card-only output.
```

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
