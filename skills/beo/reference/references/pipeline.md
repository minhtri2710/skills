# Pipeline

This file defines legal transitions after an owner decision exists.
It must not redefine owner collision precedence. Collision resolution belongs to `beo-route`.

## Owner groups

### Core runtime
- beo-route
- beo-explore
- beo-plan
- beo-validate
- beo-execute
- beo-swarm
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
- core runtime -> `beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute/beo-swarm -> beo-review -> done`
- optional closure -> `beo-review -> beo-compound -> beo-dream/done`

Go mode is an operator macro over this pipeline, not a new owner.
See `beo-references -> go-mode.md`.

Use `beo-references -> operator-card.md` as the first operator view.
Use `beo-route` for owner selection when multiple predicates compete.

## Allowed handoffs

| From | To |
| --- | --- |
| beo-route | beo-onboard, beo-reference, beo-author, beo-dream, beo-debug, beo-explore, beo-plan, beo-validate, beo-execute, beo-swarm, beo-review, beo-compound, user, done |
| beo-onboard | beo-route, user |
| beo-reference | done |
| beo-author | beo-route, user, done |
| beo-explore | beo-plan, user |
| beo-plan | beo-validate, beo-explore, user |
| beo-validate | beo-execute, beo-swarm, beo-plan, beo-explore, user |
| beo-execute | beo-review, beo-debug, beo-plan, beo-validate, user |
| beo-swarm | beo-review, beo-validate, beo-plan, beo-debug, user |
| beo-review | beo-compound, beo-execute, beo-plan, beo-explore, beo-debug, user, done |
| beo-debug | beo-execute, beo-swarm, beo-review, beo-plan, beo-validate, beo-explore, user |
| beo-compound | beo-dream, user, done |
| beo-dream | user, done |

## Orientation pointers

Quick index only:
- owner selection, collision, and route suppression -> `beo-route`
- go-mode happy path and assumption rule -> `beo-references -> go-mode.md`
- core runtime owner contracts -> `skills/beo/{explore,plan,validate,execute,swarm,review}/SKILL.md`
- optional closure owner contracts -> `skills/beo/{compound,dream}/SKILL.md`
- support/meta owner contracts -> `skills/beo/{onboard,reference,author,debug}/SKILL.md`

## Canonical source notes
- Allowed handoffs and state-transition routing are canonical here.
- Routing collisions and precedence are canonical in `beo-route`.
- Approval semantics are canonical in `beo-references -> approval.md`.
- Artifact schemas and writer boundaries are canonical in `beo-references -> artifacts.md`.
- State/handoff freshness and route evidence fields are canonical in `beo-references -> state.md`.

## State transition table

Representative legal transitions only:

| From state | Event | Next owner |
| --- | --- | --- |
| no active feature | new feature request | beo-explore |
| context locked | plan missing or stale | beo-plan |
| plan current | approval/readiness/mode missing | beo-validate |
| approval current and mode=`serial` | one bead selected | beo-execute |
| approval current and mode=`swarm` | isolated bead set proven | beo-swarm |
| execution terminal | review bundle complete | beo-review |
| execute requires mutation outside approved scope | plan/approval repair needed | beo-plan |
| execute hits blocker with unproven root cause | diagnostic needed | beo-debug |
| debug proves requirements are contradicted | requirements repair needed | beo-explore |
| review verdict=`accept` and learning disposition=`no-learning` is obvious | terminal closure allowed | done |
| review verdict=`accept` and durable or unclear learning remains | learning disposition needed | beo-compound |
| review verdict=`reject` | requirements invalid or contradicted | beo-explore |
| accepted learnings repeat | two or more features support pattern | beo-dream |

For approval invalidation, closure splitting, swarm fallback, and debug precedence, inherit canonical doctrine from `beo-references -> approval.md`, `beo-references -> learning.md`, and `beo-route`.

## Manual pressure note

Use `skills/beo/author/references/manual-pressure-scenarios.md` for prose-only pressure review.
Do not restate scenario law here.
