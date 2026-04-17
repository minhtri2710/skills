---
name: beo-explore
description: |
  Lock ambiguous product requirements into `CONTEXT.md` when scope, behavior, constraints, interfaces, compatibility, or acceptance boundaries are still unclear, and establish the active feature thread only if it does not yet exist. Use it only for requirement definition and intake bootstrap, not for architecture, decomposition, sequencing, validation, or implementation planning.

---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-explore

## Atomic purpose
Define the requirement contract and establish intake bootstrap when missing.

## When to use
- a feature or change request still has missing, conflicting, or ambiguous requirements
- planning would otherwise have to guess scope, behavior, constraints, interfaces, compatibility, or acceptance boundaries
- replanning reveals that requirement-level decisions are still unlocked

## Inputs
**Required**
- current feature or change request
- feature slug or identifier
- user clarification responses

**Optional**
- existing `.beads/artifacts/<feature_slug>/CONTEXT.md`
- relevant prior learnings only as requirement-shaping context

## Outputs
**Allowed writes**
- feature-intake bootstrap required to establish the active feature thread, including the feature epic and canonical `feature_slug` when they do not already exist
- `.beads/artifacts/<feature_slug>/CONTEXT.md`
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- planning artifacts (`discovery.md`, `approach.md`, `plan.md`, `phase-plan.md`, `phase-contract.md`, `story-map.md`)
- beads or decomposition state
- implementation code

## Boundary rules
- Explore owns requirement definition and new-feature intake bootstrap only.
- Explore must define user-visible scope, constraints, interfaces, compatibility, and acceptance boundaries without choosing architecture, decomposition, sequencing, or implementation strategy.
- Explore may establish the feature epic and canonical `feature_slug` only when missing for a new feature intake.
- Explore must not create plans or beads, validate readiness, implement code, review work, debug failures, or consolidate learnings.
- Any unresolved scope, behavior, contract, UX, or compatibility decision must be locked here or routed back here.

## Minimum hard gates
- **INTAKE-BOOTSTRAP-ONLY-WHEN-MISSING** — Create the feature epic and canonical `feature_slug` only for new-feature intake or recovery when they do not already exist.
- **LOCK-BEFORE-PLAN** — Do not hand off while any scope-affecting decision remains unlocked.
- **NO-PLANNING** — Do not create planning artifacts or beads.
- **STRUCTURED-QUESTIONS-ONLY** — Use the structured question tool for clarification or approvals per `beo-reference` → `references/shared-hard-gates.md`.
- **GO-MODE** — If the user explicitly requests go mode, switch to `references/go-mode.md`.
- **TERMINATE-ON-HANDOFF** — After writing `CONTEXT.md` and handoff state, stop immediately.
- **FRESH-LOAD-REQUIRED** — Explore must run as a fresh invocation.

## Default loop
1. If this is a new feature intake, create the active feature epic when missing and record the canonical `feature_slug` on the epic before writing feature artifacts.
2. Read any existing `CONTEXT.md` and relevant learnings so the session resumes instead of restarting.
3. Identify unresolved gray areas using `references/gray-area-probes.md`.
4. Ask targeted questions until all requirement-level decisions are locked.
5. Record locked decisions in `CONTEXT.md` using `references/context-template.md`.
6. When requirements are fully locked, write `.beads/STATE.json` for `beo-plan` and stop.

## References
| File | Use when |
|------|----------|
| `references/context-template.md` | Writing or normalizing `CONTEXT.md` |
| `references/gray-area-probes.md` | Finding missing scope / behavior decisions |
| `references/go-mode.md` | Running compressed intake with explicit user consent |
| `beo-reference` → `references/artifact-conventions.md` | Creating and preserving the canonical `feature_slug` |
| `beo-reference` → `references/br-cli-reference.md` | Creating the feature epic during intake |
| `beo-reference` → `references/learnings-read-protocol.md` | Reading prior learnings without turning explore into dream/compound |
| `beo-reference` → `references/state-and-handoff-protocol.md` | Writing handoff state |

## Handoff and exit
- Normal forward handoff: `beo-plan`
- Backward / pause outcome: `next: "user"` when awaiting clarification
- Explore must not load `beo-plan` directly; it writes state and yields.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- drafting solutions or decomposition instead of clarifying requirements
- leaving behavior-affecting ambiguity for planning to guess later
- writing anything other than `CONTEXT.md` plus canonical handoff state
- continuing after handoff state is written
