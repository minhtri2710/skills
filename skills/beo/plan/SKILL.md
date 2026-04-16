---
name: beo-plan
description: |
  Use when a fully locked CONTEXT.md exists and needs transformation into executable planning artifacts and current-phase beads. Runs codebase discovery, selects technical approach, writes plan artifacts (discovery.md, approach.md, plan.md, optional phase-plan.md), then creates current-phase phase-contract.md, story-map.md, and bead graph. MUST NOT create beads beyond the current phase, write implementation code, or verify plan quality. Do not use when requirements are still unlocked or ambiguous (use beo-explore), or when a plan exists and needs structural verification (use beo-validate).
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-plan

## Overview
Convert locked requirements into executable planning artifacts, current-phase contracts, and bead graphs that are ready for validation. **Core principle: decompose precisely for the current phase only, without writing implementation code.**

## Boundary Rules
- **MUST NOT** perform independent state detection or free-form routing — owned by `beo-route`. May emit canonical handoff to the next allowed pipeline skill when exit conditions are met.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** verify plan quality — owned by `beo-validate`.
- **MUST NOT** write implementation code — owned by `beo-execute`.
- **MUST NOT** orchestrate workers — owned by `beo-swarm`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.

## Hard Gates
> **HARD-GATE: LOCKED-CONTEXT-REQUIRED** — Plan never starts without a `CONTEXT.md` where every decision is locked. If unlocked items exist, route back to `beo-explore`.

> **HARD-GATE: CURRENT-PHASE-ONLY** — Plan creates beads only for the current phase. If future-phase beads are created, stop and reconcile to the current phase per the pipeline transition rules (`beo-reference` → `references/pipeline-contracts.md`).

> **HARD-GATE: NO-CODE** — Plan never writes implementation code. It writes planning artifacts and creates beads only. If violated, stop and remove implementation drift from the planning session.

> **HARD-GATE: APPROVAL-REMOVAL** — If the `approved` label exists from a prior validation cycle, plan must remove it before writing artifacts per the beo approval gates (`beo-reference` → `references/approval-gates.md`). If violated, cleanup is required before planning continues.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Plan Loop
1. **Discovery** — Read the codebase, identify relevant files, dependencies, and constraints, then write `.beads/artifacts/<feature_slug>/discovery.md` using `references/discovery-reference.md` patterns.
2. **Approach** — Choose the technical strategy and write `.beads/artifacts/<feature_slug>/approach.md` using `references/approach-template.md`. If the work is multi-phase, also write `.beads/artifacts/<feature_slug>/phase-plan.md` using `references/phase-plan-template.md` and obtain approval per the beo approval gates (`beo-reference` → `references/approval-gates.md`).
3. **Planning** — Write `.beads/artifacts/<feature_slug>/plan.md` using `references/plan-template.md`, covering the full feature and its story breakdown.
4. **Current-Phase Artifacts** — Write `.beads/artifacts/<feature_slug>/phase-contract.md` using `references/phase-contract-template.md` and `.beads/artifacts/<feature_slug>/story-map.md` using `references/story-map-template.md`.
5. **Bead Creation** — Create beads via `br` for the current phase only, reconcile dependencies using the scheduling cascade (`beo-reference` → `references/dependency-and-scheduling.md`), use `references/bead-ops.md` for command patterns, and use standard bead description templates (`beo-reference` → `references/bead-description-templates.md`) for descriptions.

### Reference Files
| File | Purpose |
|------|---------|
| `references/planning-prerequisites.md` | Preconditions and readiness checks before planning begins. |
| `references/planning-state-and-cleanup.md` | Planning-specific state hygiene, cleanup, and resumption rules. |
| `references/artifact-writing-guide.md` | Writing standards for planning artifacts and artifact quality checks. |
| `references/bead-ops.md` | Canonical `br` command patterns for creating and managing current-phase beads. |
| `references/discovery-reference.md` | Discovery patterns for codebase analysis and constraint capture. |
| `references/approach-template.md` | Template and rubric for selecting the implementation approach. |
| `references/plan-template.md` | Template for the full feature plan artifact. |
| `references/phase-plan-template.md` | Template for multi-phase decomposition when a feature spans phases. |
| `references/phase-contract-template.md` | Template for defining current-phase scope and execution boundaries. |
| `references/story-map-template.md` | Template for current-phase story and bead dependency mapping. |

## Inputs and Outputs
- **Inputs** — Locked `.beads/artifacts/<feature_slug>/CONTEXT.md`, feature learnings, and critical patterns per the learnings read protocol (`beo-reference` → `references/learnings-read-protocol.md`).
- **Outputs** — Written to `.beads/artifacts/<feature_slug>/`:
  - `discovery.md`
  - `approach.md`
  - `plan.md`
  - `phase-plan.md` when applicable
  - `phase-contract.md`
  - `story-map.md`
  - current-phase beads created via `br`
- Artifact paths and ownership follow artifact conventions (`beo-reference` → `references/artifact-conventions.md`).

## Decision Rubrics
### Single Phase vs Multi-Phase
- If the scope fits within 12 or fewer beads and has no natural phase boundary, use a single phase.
- Otherwise write `phase-plan.md`, segment by phase, and obtain the required approval before continuing.

### Bead Granularity
- Each bead must represent one verifiable deliverable.
- If one bead would require more than one independent verification step, split it.
- If two beads always execute together and cannot be verified independently, merge them.

### Dependency Wiring
- Apply the reconciliation procedure from the scheduling cascade (`beo-reference` → `references/dependency-and-scheduling.md`).
- Validate that the bead graph has no cycles and that dependencies reflect real execution constraints.

### Return-to-Explore Threshold
- If planning reveals unresolved or contradictory requirements, stop planning and route back to `beo-explore`.
- Do not paper over missing requirements with speculative assumptions.

## Approval and State Rules
- Approval gates follow the beo approval gates (`beo-reference` → `references/approval-gates.md`).
- State transitions follow the bead lifecycle states (`beo-reference` → `references/status-mapping.md`).
- `STATE.json` and `HANDOFF.json` updates follow the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).

## Failure Recovery
> Any missing artifact, stale approval, dependency conflict, malformed bead graph, or planning interruption must return a concise recovery action to the user.

## Handoff
> Write `STATE.json` for the transition to the next adjacent skill with discovery status, current-phase artifacts, bead graph state, and unresolved assumptions. Use `HANDOFF.json` only for emergency checkpoint or low-context resume scenarios.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Plan creating beads for future phases.
- Plan writing implementation code or execution details that belong to workers.
- Plan starting without a fully locked `CONTEXT.md`.
- Plan exceeding 20 beads for a single phase without explicit decomposition review.
- Plan failing to remove a stale `approved` label before rewriting artifacts.
