## Contents

- Core flow
- Session scout summary
- Communication contract
- Go-mode display checkpoints
- Optional closure
- Owner boundary matrix
- When unsure
- Read first
- Exit packet
- Canonical pointers
- Structured operator output

# Operator card

Use this as the first-pass operational view. It does not replace canonical doctrine.

## Core flow

`route -> explore -> plan -> validate -> execute/swarm -> review -> done`

Go mode is a macro over this flow, not a separate owner. See `beo-reference -> go-mode.md`.

First move: run managed startup, read the minimum canonical state/artifacts, then continue with the single current owner when fresh and uncontradicted. Use `beo-route` only when owner state is missing, stale, contradictory, or colliding.

## Session scout summary

Use this shape for first-pass operator orientation. It is presentation only and
must not authorize execution, replace routing, or create approval.
Status and scout output are advisory/display only; they cannot select owners,
approve readiness, emit review verdicts, dispatch swarm work, or promote learning.

| Field | Source | Meaning |
| --- | --- | --- |
| onboarding freshness | live onboard check or scout hint | whether managed startup needs `beo-onboard` |
| active feature | canonical `STATE.json` plus live artifacts | selected feature slug or ambiguity |
| current owner | canonical `STATE.json.current_owner` | trusted only when not contradicted |
| requirements | `CONTEXT.md` | missing, unlocked, locked, or contradicted |
| plan | `PLAN.md` + bead graph | missing, incomplete, current, or invalidated |
| approval | `approval-record.json` + approval doctrine | missing, referenced-unverified, current, or stale |
| readiness | `STATE.json.readiness` | absent, `PASS_SERIAL`, `PASS_SWARM`, or failure class |
| blockers | live artifacts | external input, access, root cause, or artifact repair |
| next reads | required vs conditional | minimum files to confirm the route |

Only a valid current owner or `beo-route` may select the next owner.

If the scout output conflicts with canonical artifacts, trust canonical artifacts
and route through `beo-route`.

### Operator summary shape

When presenting first-pass orientation to a human or freshly resumed agent, use
this concise shape. It is advisory only; `beo-route` remains the owner selector.

```md
Current state:
- Feature:
- Current owner:
- Why this owner:
- Blocking evidence:
- Next legal action:
- Must read:
- Must not touch:
- Route required if:
```

`Route required if` may name missing, stale, contradictory, or ambiguous evidence.
It must not authorize execution.

## Communication contract

For route decisions, validation failures, blockers, review findings, and
handoffs, report in this order:

1. Plain-language summary
2. Current evidence
3. Why it matters
4. Concrete scenario
5. Next legal owner/action

Translate decision ids, invariants, and owner rules into user-visible meaning.
Do not say only "violates D5"; explain what D5 requires and what would break in
the workflow or delivered behavior.
When explaining a route or blocker, name the canonical owner and the user-visible
consequence. Avoid bare doctrine shorthand.

## Go-mode display checkpoints

These checkpoints are user-facing summaries, not gate records.

| Checkpoint | Show | Authority remains |
| --- | --- | --- |
| startup / route sanity | onboarding freshness, required reads, current-owner conflicts | live onboarding check + `STATE.json`; `beo-route` when needed |
| requirements | locked decisions, acceptance, non-goals, compatibility, constraints | `CONTEXT.md` |
| plan / approval | phase exit state, bead set, file scope, forbidden paths, verification, approval ref | `PLAN.md` + bead graph + `approval-record.json` |
| serial execution | executed bead, changed files, verification evidence, scope match | `beo-execute` + `execution-bundle.json` |
| swarm dispatch | isolated approved beads, live coordination evidence, aggregation status | `beo-swarm` + live coordination checks |
| review | verdict, P0/P1 status, verification evidence | `REVIEW.md` |
| learning | no-learning, feature learning, or consolidation candidate | `beo-reference -> learning.md`, `beo-compound`, `beo-dream` |

Do not create separate phase, story, merge, or UAT approval records from these summaries. Display checkpoints must not approve, route, validate, dispatch, accept, reject, or promote.

## Optional closure

`review -> compound -> dream/done`

## Owner boundary matrix

| Owner | Single decision | Writable surface | Must not do |
| --- | --- | --- | --- |
| `beo-explore` | lock requirements | `CONTEXT.md` | plan or execute |
| `beo-plan` | create or repair current-phase graph | `PLAN.md`, bead graph metadata | approve or execute |
| `beo-validate` | classify readiness, mode, and approval action | approval record, readiness state | repair artifact content |
| `beo-execute` | deliver one approved serial bead | approved product file scope | widen scope or diagnose unknown blocker |
| `beo-swarm` | coordinate approved parallel beads | coordination and aggregation surfaces | implement product changes |
| `beo-review` | emit one terminal verdict | `REVIEW.md`, bounded reactive-fix record | fix code |
| `beo-compound` | record one feature learning outcome | feature learning record | cross-feature consolidation |
| `beo-dream` | consolidate cross-feature learning | shared learning guidance | treat one feature as corpus evidence by default |

## When unsure

Use `beo-route`.

## Read first

1. `.beads/STATE.json`
2. `.beads/HANDOFF.json` only if present and fresh
3. `.beads/artifacts/<feature_slug>/CONTEXT.md` when the active feature requires requirements context
4. `.beads/artifacts/<feature_slug>/PLAN.md` when the active feature requires planning/execution context
5. `.beads/artifacts/<feature_slug>/approval-record.json` when approval/readiness is relevant
6. `.beads/artifacts/<feature_slug>/execution-bundle.json` when review evidence is relevant
7. `.beads/artifacts/<feature_slug>/REVIEW.md` when closure evidence is relevant

Use `STATE.json.operator_view` for quick orientation, but trust canonical fields when they differ.

## Exit packet

Return only from the canonical owner that owns the decision:
- decision
- evidence
- changed surfaces
- blocked_by
- next_owner
- next_owner_reason

## Canonical pointers

- owner selection -> `beo-route`
- legal transitions -> `beo-reference -> pipeline.md`
- approval -> `beo-reference -> approval.md`
- state/handoff -> `beo-reference -> state.md`
- learning -> `beo-reference -> learning.md`

## Structured operator output

When reporting findings, state the active owner, evidence read, decision, next owner, and blockers before optional detail.
