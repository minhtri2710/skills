---
name: beo-route
description: |
  Use when a beo session is starting, resuming, or the correct next skill is not already determined. Route reads the current request, onboarding readiness, `.beads/STATE.json`, optional `.beads/HANDOFF.json`, and live bead or epic state to choose exactly one next action: load one downstream skill, return control to the user, or stop. Do not use when the downstream skill is already known, or to perform requirements, planning, validation, execution, review, debugging, learning, onboarding, reference lookup, or authoring work itself.
---

> **HARD-GATE: ONBOARDING** — Before any routing work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-route

## Atomic purpose
Detect current beo state and emit exactly one canonical next action.

## When to use
- session start
- resume after interruption or checkpoint
- explicit "continue", "resume", or "what's next?"
- any time multiple beo skills could plausibly apply and routing must choose exactly one

## Inputs
**Required**
- current user request or resume signal
- onboarding readiness state
- `.beads/STATE.json`
- live bead and epic state from `br` and `bv`

**Optional**
- `.beads/HANDOFF.json`

## Outputs
**Decisions**
- exactly one `NextAction`: `LoadSkill(name)`, `ReturnToUser(reason)`, or `Stop(done)`

**Allowed writes**
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it
- canonical intake scaffolding only when the routing table explicitly assigns it to route for new-intake rows

**Must not write**
- feature artifacts under `.beads/artifacts/<feature_slug>/`
- implementation code
- review or learning artifacts

## Boundary rules
- Route owns selection of the next skill; it does not perform downstream work.
- Route does not clarify requirements, design solutions, validate plans, implement code, review outcomes, debug blockers, extract learnings, or rewrite skills.
- Route may perform only the minimum intake scaffolding already required by the canonical routing table; it must not expand that into planning or execution work.

## Minimum hard gates
- **HANDOFF-PRECEDENCE** — If `.beads/HANDOFF.json` exists, honor the saved `skill` and `next_action` per `beo-reference` → `references/state-and-handoff-protocol.md` before normal state detection.
- **CANONICAL-FIELDS-ONLY** — Use the canonical `STATE.json` and `HANDOFF.json` field names from `beo-reference` → `references/state-and-handoff-protocol.md`. Do not invent aliases such as `NextSkill` or `STATE.skill`.
- **FIRST-MATCH-WINS** — Match live state against the routing table in `beo-reference` → `references/pipeline-contracts.md` top-to-bottom.
- **TERMINATE-ON-HANDOFF** — After writing handoff state, stop immediately (`beo-reference` → `references/shared-hard-gates.md`).
- **FRESH-LOAD-REQUIRED** — Route must run as a fresh invocation, not as a continuation of another skill's session (`beo-reference` → `references/shared-hard-gates.md`).

## Default loop
1. Verify onboarding readiness.
2. Read `.beads/HANDOFF.json` first when present, then `.beads/STATE.json`, using the canonical resume protocol.
3. If no handoff controls the next step, inspect the live bead / epic state and current request, then match the first applicable routing row in `pipeline-contracts.md`.
4. Emit exactly one `NextAction` and write `.beads/STATE.json` for the selected transition.
5. Stop. Never begin the downstream skill in the same session.

## References
| File | Use when |
|------|----------|
| `references/router-operations.md` | Applying route-specific detection and intake mechanics |
| `references/go-mode.md` | A fresh request explicitly enters compressed go-mode intake |
| `beo-reference` → `references/pipeline-contracts.md` | Selecting the canonical next action |
| `beo-reference` → `references/state-and-handoff-protocol.md` | Reading or writing `STATE.json` / `HANDOFF.json` |
| `beo-reference` → `references/shared-hard-gates.md` | Enforcing onboarding and session-boundary rules |

## Handoff and exit
- Allowed direct outcomes: `beo-onboard`, `beo-explore`, `beo-plan`, `beo-validate`, `beo-execute`, `beo-swarm`, `beo-review`, `beo-compound`, `beo-debug`, `beo-dream`, `beo-author`, `ReturnToUser`, `Stop(done)`.
- Every route decision must match an allowed edge in `beo-reference` → `references/pipeline-contracts.md`.

## Context budget
If context exceeds 65%, checkpoint using the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- using non-canonical handoff field names
- clearing or rewriting handoff state outside the canonical protocol
- doing exploration, planning, validation, execution, review, debug, or learning work after selecting a route
- creating feature artifacts not explicitly owned by route in the routing table
- continuing after writing `STATE.json`
