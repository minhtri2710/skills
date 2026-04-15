---
name: beo-explore
description: |
  Use before any non-Quick feature work, refactor, behavior change, or requirements-shaping conversation where user intent is not yet locked. Triggers: "let's think through X", "what should we build?", "define requirements", or when the user knows what they want but hasn't fully specified edge cases, scope boundaries, or expected behavior. Gathers, clarifies, and locks requirements into CONTEXT.md via Socratic dialogue. MUST NOT design solutions, create beads, accept vague requirements, or proceed to planning with unlocked decisions. Do not use for instant work, clear bug-fix root-cause work (use beo-debug), or mid-pipeline resume (use beo-route).
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-explore

## Overview
Run a focused Socratic dialogue that turns user intent into a fully locked `CONTEXT.md` for a single feature. **Core principle: clarify and lock decisions without drifting into planning or implementation.**

## Boundary Rules
- **MUST NOT** route to skills — owned by `beo-route`.
- **MUST NOT** decompose into tasks — owned by `beo-plan`.
- **MUST NOT** verify plans — owned by `beo-validate`.
- **MUST NOT** write code — owned by `beo-execute`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.
- **MUST NOT** diagnose failures — owned by `beo-debug`.

## Hard Gates
> **HARD-GATE: NO-PLANNING** — Explore never creates beads, epics, tasks, `discovery.md`, `approach.md`, or `plan.md`. If violated, stop and return to pure requirements capture.

> **HARD-GATE: NO-UNLOCKED-EXIT** — Explore does not hand off to `beo-plan` unless every decision in `CONTEXT.md` is marked locked. If violated, continue probing until all unlocked items are resolved.

> **HARD-GATE: GO-MODE** — If the user says “go mode” or equivalent, follow `references/go-mode.md`. If violated, restart the interaction in compressed confirmation mode.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Explore Loop
1. Read existing `.beads/artifacts/<feature_slug>/CONTEXT.md` if present so the session resumes instead of restarts. Also read feature learnings and critical patterns per the learnings read protocol (`beo-reference` → `references/learnings-read-protocol.md`).
2. Identify gray areas, ambiguous scope, hidden assumptions, edge cases, and behavioral boundaries using `references/gray-area-probes.md`.
3. Ask targeted questions with one concern per question and no more than three questions per turn, then wait for the user response.
4. Record each resolved decision in `CONTEXT.md` using `references/context-template.md`, marking locked and unlocked items explicitly.
5. When every decision is locked, write the final `CONTEXT.md` and hand off to `beo-plan` via `HANDOFF.json` per the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).

### Reference Files
| File | Purpose |
|------|---------|
| `references/context-template.md` | Canonical structure for recording requirements and lock status in `CONTEXT.md`. |
| `references/gray-area-probes.md` | Probe patterns for resolving ambiguity, assumptions, and missing requirements. |
| `references/go-mode.md` | Compressed intake protocol for batch-confirmed requirement capture. |

## Inputs and Outputs
- **Inputs** — User intent in natural language, optional existing `.beads/artifacts/<feature_slug>/CONTEXT.md`.
- **Outputs** — Completed `.beads/artifacts/<feature_slug>/CONTEXT.md` with all decisions locked.
- Artifact locations and ownership follow artifact conventions (`beo-reference` → `references/artifact-conventions.md`).

## Decision Rubrics
### Lock vs Probe
- If the user provides a clear, unambiguous answer, lock the decision.
- If the answer is vague, contradictory, or incomplete, probe deeper before locking.

### Go-Mode vs Standard
- If the user says “go mode”, “just do it”, or equivalent compression language, switch to the batch-confirmation protocol in `references/go-mode.md`.
- Otherwise stay in the standard Socratic flow.

### Scope Creep Handling
- If new information changes a previously locked decision, unlock the affected section and re-probe.
- If new information is additive and consistent, lock it without reopening unrelated decisions.

## Approval and State Rules
- Approval moments must follow the beo approval gates (`beo-reference` → `references/approval-gates.md`).
- State transitions and handoff data must follow the bead lifecycle states (`beo-reference` → `references/status-mapping.md`) and the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).

## Failure Recovery
> Any stalled dialogue, contradictory answers, missing context, or failed handoff must return a concise recovery action to the user.

## Handoff
> Write `HANDOFF.json` for every skill transition (`beo-reference` → `references/pipeline-contracts.md`). Transitions follow the pipeline: route → explore → plan → validate → (execute | swarm → execute) → review → compound.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Explore writing any code or pseudo-code implementation plan.
- Explore creating beads, epics, or phase artifacts.
- Explore producing anything beyond `CONTEXT.md`.
- Explore handing off with unlocked decisions still present.
- Explore spending more than 10 turns on a single unresolved gray area.
