# Operator card

Use this as the first-pass operational view. It does not replace canonical doctrine.

## Core flow

`route -> explore -> plan -> validate -> execute/swarm -> review -> done`

Go mode is a macro over this flow, not a separate owner. See `beo-references -> go-mode.md`.

## Session scout summary

Use this shape for first-pass operator orientation. It is presentation only and
must not authorize execution, replace routing, or create approval.

| Field | Source | Meaning |
| --- | --- | --- |
| onboarding freshness | live onboard check or scout hint | whether managed startup needs `beo-onboard` |
| active feature | canonical `STATE.json` plus live artifacts | selected feature slug or ambiguity |
| current owner | canonical `STATE.json.current_owner` | trusted only when not contradicted |
| requirements | `CONTEXT.md` | missing, unlocked, locked, or contradicted |
| plan | `PLAN.md` + bead graph | missing, incomplete, current, or invalidated |
| approval | `approval-record.json` + approval doctrine | missing, referenced-unverified, current, or stale |
| readiness | `STATE.json.readiness` | absent, `PASS_SERIAL`, `PASS_SWARM`, or failure class |
| likely next owner | `beo-route` evidence | route candidate, not a final scout decision |
| blockers | live artifacts | external input, access, root cause, or artifact repair |
| next reads | required vs conditional | minimum files to confirm the route |

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
It must not say "recommended owner" or authorize execution.

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

## Go-mode display checkpoints

These checkpoints are user-facing summaries, not gate records.

| Checkpoint | Show | Authority remains |
| --- | --- | --- |
| explore complete | locked decisions, acceptance, non-goals, compatibility, constraints | `CONTEXT.md` |
| plan complete | phase exit state, bead set, file scope, forbidden paths, verification | `PLAN.md` + bead graph |
| validate complete | approved beads, mode, approval ref, invalidation triggers | `approval-record.json` |
| review complete | verdict, P0/P1 status, verification evidence, learning disposition | `REVIEW.md` |

Do not create separate phase, story, merge, or UAT approval records from these summaries.

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

Return only:
- decision
- evidence
- changed surfaces
- blocked_by
- next_owner
- next_owner_reason

## Canonical pointers

- owner selection -> `beo-route`
- legal transitions -> `beo-references -> pipeline.md`
- approval -> `beo-references -> approval.md`
- state/handoff -> `beo-references -> state.md`
- learning -> `beo-references -> learning.md`
