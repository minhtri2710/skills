---
name: beo-explore
description: |
  Use when a feature or change request still has unlocked requirements and planning cannot begin safely. Explore resolves ambiguity in scope, behavior, interfaces, constraints, compatibility, edge cases, and acceptance boundaries, then writes a fully locked `CONTEXT.md`. Do not use once requirements are already locked, or for technical design, validation, execution, review, debugging, learning capture, or routing decisions.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-explore

## Atomic purpose
Turn ambiguous feature intent into one fully locked `CONTEXT.md`.

## When to use
- new feature or change request with missing or contradictory requirements
- planning cannot start because scope or behavior is still unclear
- a replan reveals locked decisions are missing or inconsistent and work must return to requirements clarification

## Inputs
**Required**
- current feature request
- feature identifier / slug
- user answers to clarification questions

**Optional**
- existing `.beads/artifacts/<feature_slug>/CONTEXT.md`
- relevant prior learnings read via `beo-reference` → `references/learnings-read-protocol.md` when needed

## Outputs
**Allowed writes**
- `.beads/artifacts/<feature_slug>/CONTEXT.md`
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- planning artifacts (`discovery.md`, `approach.md`, `plan.md`, `phase-plan.md`, `phase-contract.md`, `story-map.md`)
- beads or decomposition state
- implementation code

## Boundary rules
- Explore owns requirement locking only.
- Explore does not choose implementation approach, create bead graphs, validate readiness, implement code, review results, debug failures, or synthesize learnings.
- Anything that changes scope, behavior, contracts, UX, or compatibility must be resolved here before handoff.

## Minimum hard gates
- **LOCK-BEFORE-PLAN** — Do not hand off while any scope-affecting decision remains unlocked.
- **NO-PLANNING** — Do not create planning artifacts or beads.
- **STRUCTURED-QUESTIONS-ONLY** — Use the structured question tool for clarification or approvals per `beo-reference` → `references/shared-hard-gates.md`.
- **GO-MODE** — If the user explicitly requests go mode, switch to `references/go-mode.md`.
- **TERMINATE-ON-HANDOFF** — After writing `CONTEXT.md` and handoff state, stop immediately.
- **FRESH-LOAD-REQUIRED** — Explore must run as a fresh invocation.

## Default loop
1. Read any existing `CONTEXT.md` and relevant learnings so the session resumes instead of restarting.
2. Identify unresolved gray areas using `references/gray-area-probes.md`.
3. Ask targeted questions until all requirement-level decisions are locked.
4. Record locked decisions in `CONTEXT.md` using `references/context-template.md`.
5. When requirements are fully locked, write `.beads/STATE.json` for `beo-plan` and stop.

## References
| File | Use when |
|------|----------|
| `references/context-template.md` | Writing or normalizing `CONTEXT.md` |
| `references/gray-area-probes.md` | Finding missing scope / behavior decisions |
| `references/go-mode.md` | Running compressed intake with explicit user consent |
| `beo-reference` → `references/learnings-read-protocol.md` | Reading prior learnings without turning explore into dream/compound |
| `beo-reference` → `references/state-and-handoff-protocol.md` | Writing handoff state |

## Handoff and exit
- Normal forward handoff: `beo-plan`
- Backward / pause outcome: `ReturnToUser(...)` when awaiting clarification
- Explore must not load `beo-plan` directly; it writes state and yields.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- drafting solutions or decomposition instead of clarifying requirements
- leaving behavior-affecting ambiguity for planning to guess later
- writing anything other than `CONTEXT.md` plus canonical handoff state
- continuing after handoff state is written
