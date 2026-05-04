## Contents

- Owner groups
- Delivery order
- Allowed handoffs
- Orientation pointers
- Canonical source notes
- State transition table
- Manual pressure note

# Pipeline

This file defines legal transitions after an owner decision exists.
It must not redefine owner collision precedence. Collision resolution belongs to `beo-route`.

## Execution model baseline

Beo uses one execution model:
- `beo-validate` emits `PASS_EXECUTE`.
- `PASS_EXECUTE` selects exactly one execution set.
- The selected execution set mode is one of `single`, `ordered_batch`, or `local_parallel`.
- `beo-execute` delivers the selected approved execution set.
- `local_parallel` is local execution only.
- No `beo-swarm` owner exists.
- No `PASS_SERIAL` or `PASS_SWARM` verdict exists.
- External worker coordination, Agent Mail, coordinator/worker protocols, worker reservations, and heartbeat protocols are outside beo execution doctrine.

## Forbidden execution vocabulary

Do not use these terms in canonical beo workflow:

| Forbidden | Replacement |
| --- | --- |
| `PASS_SERIAL` | `PASS_EXECUTE` |
| `PASS_SWARM` | no replacement; delete |
| `beo-swarm` | no replacement; delete |
| `execute/swarm` | `beo-execute` |
| `serial/swarm` | `execution set mode` |
| `swarm execution` | delete |
| `Agent Mail execution` | delete |
| `coordinator/worker execution` | delete |
| `worker reservation` | delete |

## Owner groups

### Core runtime
- beo-route
- beo-explore
- beo-plan
- beo-validate
- beo-execute
- beo-review

### Optional closure
- beo-compound
- beo-dream

### Support/meta
- beo-onboard
- beo-reference
- beo-author
- beo-debug

### External/terminal
- user
- done

## Delivery order

Minimal shape only:
- core runtime -> `beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`
- optional closure -> `beo-review -> beo-compound -> beo-dream/done`

Go mode only reduces unnecessary operator prompts. It does not bypass owner selection, approval, readiness, execution scope, review, or learning gates; see `beo-reference -> go-mode.md`.
Use `beo-reference -> operator-card.md` as the first operator view.

Stale approval after mutation is never a continue-execute path. The executing owner stops and hands off by evidence to `beo-review`, `beo-plan`, `beo-validate`, or exceptionally `beo-route`; see `beo-reference -> approval.md`.

## Allowed handoffs

| From | To |
| --- | --- |
| beo-route | beo-onboard, beo-reference, beo-author, beo-dream, beo-debug, beo-explore, beo-plan, beo-validate, beo-execute, beo-review, beo-compound, user, done |
| beo-onboard | beo-route, user |
| beo-reference | done |
| beo-author | beo-route, user, done |
| beo-explore | beo-plan, user |
| beo-plan | beo-validate, beo-explore, user, beo-route (exceptional collision/stale-state resolution only) |
| beo-validate | beo-execute, beo-plan, beo-explore, user, beo-route (exceptional collision/stale-state resolution only) |
| beo-execute | beo-review, beo-debug, beo-plan, beo-validate, user, beo-route (exceptional collision/stale-state resolution only) |
| beo-review | beo-compound, beo-validate, beo-plan, beo-explore, beo-debug, user, done, beo-route (exceptional collision/stale-state resolution only) |
| beo-debug | beo-execute, beo-review, beo-plan, beo-validate, beo-explore, user, beo-route (exceptional collision/stale-state resolution only) |
| beo-compound | beo-dream, user, done |
| beo-dream | user, done |

Exceptional `beo-route` handoffs from runtime owners are legal only when owner state is missing, stale, contradictory, or colliding; they are not happy-path successors.

## Orientation pointers

Quick index only:
- owner selection, collision, and route suppression -> `beo-route`
- go-mode happy path and assumption rule -> `beo-reference -> go-mode.md`
- core runtime owner contracts -> `skills/beo/{explore,plan,validate,execute,review}/SKILL.md`
- optional closure owner contracts -> `skills/beo/{compound,dream}/SKILL.md`
- support/meta owner contracts -> `skills/beo/{onboard,reference,author,debug}/SKILL.md`

## Canonical source notes
- Allowed handoffs and state-transition routing are canonical here.
- Routing collisions and precedence are canonical in `beo-route`.
- Approval semantics are canonical in `beo-reference -> approval.md`.
- Artifact schemas and writer boundaries are canonical in `beo-reference -> artifacts.md`.
- State/handoff freshness and route evidence fields are canonical in `beo-reference -> state.md`.

## State transition table

Representative legal transitions only. This table is not a routing engine, does not override owner predicates, and must not be used to bypass the loaded owner contract, approval doctrine, or artifact schemas.

| From state | Event | Next owner |
| --- | --- | --- |
| no active feature | new feature request | beo-explore |
| context locked | plan missing or stale | beo-plan |
| plan current | approval/readiness/mode missing | beo-validate |
| approval current and `execution_mode=single` | one bead selected | beo-execute |
| approval current and `execution_mode=ordered_batch` | explicit ordered bead set | beo-execute |
| approval current and `execution_mode=local_parallel` | disjoint isolated bead set proven | beo-execute |
| execution terminal | review bundle complete | beo-review |
| execute requires mutation outside approved scope | plan/approval repair needed | beo-plan |
| execute hits blocker with unproven root cause | diagnostic needed | beo-debug |
| debug proves requirements are contradicted | requirements repair needed | beo-explore |
| review verdict=`accept` and learning disposition=`no-learning` is obvious | terminal closure allowed | done |
| review verdict=`accept` and durable or unclear learning remains | learning disposition needed | beo-compound |
| review verdict=`reject` | requirements invalid or contradicted | beo-explore |
| accepted learnings repeat | two or more features support pattern | beo-dream |

For approval invalidation, closure splitting, and debug precedence, inherit canonical doctrine from `beo-reference -> approval.md`, `beo-reference -> learning.md`, and `beo-route`.

## Cycle note

Direct cycle edges are legal as listed above. Cycles do not require re-routing
through `beo-route` on every traversal; route only when its ownership predicate
triggers. Fresh evidence for each cycle is owned by the downstream owner
contract and shared approval/state references. The same-pair-twice loop guard is
canonical in `beo-reference -> skill-contract-common.md`.

## Manual pressure note

Use `skills/beo/author/references/manual-pressure-scenarios.md` for prose-only pressure review.
Do not restate scenario law here.
