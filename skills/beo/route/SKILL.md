---
name: beo-route
description: |
  Determine exactly one next pipeline target from canonical session state when a session starts, resumes, or the next step is not already fixed by an active handoff. Use it only for state detection and next-target selection, not for clarification, design, validation, delivery, review, debugging, learning, onboarding repair, or authoring.

---

> **HARD-GATE: ONBOARDING** — Before any routing work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-route

## Atomic purpose
Select the single correct next skill.

## When to use
- session start
- session resume
- the next step is not already fixed by an active canonical handoff
- multiple beo skills could plausibly apply and routing must decide

## Inputs
**Required**
- current user request or resume signal
- onboarding readiness state
- `.beads/STATE.json`
- live bead and epic state from `br` and `bv`

**Optional**
- `.beads/HANDOFF.json`
- current feature artifacts only as needed to classify state

## Outputs
**Decisions**
- exactly one canonical next target: `beo-onboard`, `beo-explore`, `beo-plan`, `beo-validate`, `beo-swarm`, `beo-execute`, `beo-review`, `beo-debug`, `beo-compound`, `beo-dream`, `beo-author`, `user`, or `done`

**Allowed writes**
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- feature artifacts under `.beads/artifacts/<feature_slug>/`
- planning, review, or learning artifacts
- implementation code

## Boundary rules
- Route owns state detection and next-step selection only.
- Route must not clarify requirements, design solutions, validate readiness, implement code, review outcomes, debug failures, extract learnings, or rewrite skills.
- Route must not create feature artifacts, planning artifacts, review artifacts, learning artifacts, or implementation code.
- Route must not repair onboarding; it routes to `beo-onboard` when readiness is stale.
- Route must not override a canonical downstream handoff that already determines the next skill.
- Route must stop after writing the next target and required handoff state.

## Minimum hard gates
- **HANDOFF-PRECEDENCE** — If `.beads/HANDOFF.json` exists, honor the saved `skill` and `next` per `beo-reference` → `references/state-and-handoff-protocol.md` before normal state detection.
- **CANONICAL-FIELDS-ONLY** — Use the canonical `STATE.json` and `HANDOFF.json` field names from `beo-reference` → `references/state-and-handoff-protocol.md`. Do not invent aliases such as `NextSkill` or `STATE.skill`.
- **FIRST-MATCH-WINS** — Match live state against the routing table in `beo-reference` → `references/pipeline-contracts.md` top-to-bottom.
- **TERMINATE-ON-HANDOFF** — After writing handoff state, stop immediately (`beo-reference` → `references/shared-hard-gates.md`).
- **FRESH-LOAD-REQUIRED** — Route must run as a fresh invocation, not as a continuation of another skill's session (`beo-reference` → `references/shared-hard-gates.md`).

## Default loop
1. Verify onboarding readiness.
2. Read `.beads/HANDOFF.json` first when present, then `.beads/STATE.json`, using the canonical resume protocol.
3. If no active handoff already fixes the next step, inspect the live bead / epic state and current request, then match the first applicable routing row in `pipeline-contracts.md`.
4. Emit exactly one direct next target and write `.beads/STATE.json` for the selected transition.
5. Stop. Never begin the downstream skill in the same session.

## References
| File | Use when |
|------|----------|
| `references/router-operations.md` | Applying route-specific detection and intake mechanics |
| `references/go-mode.md` | A fresh request explicitly enters compressed go-mode intake |
| `beo-reference` → `references/pipeline-contracts.md` | Selecting the canonical next target |
| `beo-reference` → `references/state-and-handoff-protocol.md` | Reading or writing `STATE.json` / `HANDOFF.json` |
| `beo-reference` → `references/shared-hard-gates.md` | Enforcing onboarding and session-boundary rules |

## Handoff and exit
- Allowed direct next targets: `beo-onboard`, `beo-explore`, `beo-plan`, `beo-validate`, `beo-execute`, `beo-swarm`, `beo-review`, `beo-compound`, `beo-debug`, `beo-dream`, `beo-author`, `user`, `done`.
- Every route decision must match an allowed edge in `beo-reference` → `references/pipeline-contracts.md`.

## Context budget
If context exceeds 65%, checkpoint using the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- using non-canonical handoff field names
- clearing or rewriting handoff state outside the canonical protocol
- doing exploration, planning, validation, execution, review, debug, or learning work after selecting a route
- creating feature artifacts not explicitly owned by route in the routing table
- continuing after writing `STATE.json`
