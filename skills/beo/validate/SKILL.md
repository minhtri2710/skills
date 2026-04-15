---
name: beo-validate
description: |
  Use after planning completes and before any implementation begins, when current-phase plan artifacts need structural verification. Triggers: "validate the plan", "is this ready to build?", "check the bead graph", "verify execution readiness". Performs 8-dimension structural verification of phase-contract.md, story-map.md, and the bead graph, returning approval or rejection with remediation steps. MUST NOT modify plans, approve below threshold, or assess implementation quality. Do not use for post-implementation review (use beo-review) or mid-execution quality checks.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-validate

## Overview
Perform structural verification of current-phase planning artifacts across 8 dimensions and return a binary gate decision. **Core principle: inspect and decide without modifying planned scope or implementation artifacts.**

## Boundary Rules
- **MUST NOT** route to skills — owned by `beo-route`.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** write or modify plans — owned by `beo-plan`.
- **MUST NOT** write code — owned by `beo-execute`.
- **MUST NOT** orchestrate workers — owned by `beo-swarm`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.

## Hard Gates
> **HARD-GATE: NO-CODE-BEFORE-APPROVAL** — No implementation code until validation passes and the `Approved` label is set. If code exists, fail validation.

> **HARD-GATE: UNDERSPECIFIED-BEAD-FAIL** — Any bead missing acceptance criteria or verification steps fails the entire validation. No partial passes.

> **HARD-GATE: CURRENT-PHASE-ONLY** — Validate only checks beads for the current phase. Future-phase beads are out of scope.

> **HARD-GATE: SPIKE-NO-INVALIDATES** — If a bead is marked as spike, it must have a clear deliverable (report, prototype, decision). Spikes without deliverables fail validation.

> **HARD-GATE: SWARMING-ELIGIBILITY** — Count independent ready beads. If ≥3 with non-overlapping file scopes, note swarm eligibility in the approval. If <3, note single-worker mode.

> **HARD-GATE: APPROVAL-OWNERSHIP** — Only validate adds the `Approved` label. Per the beo approval gates (`beo-reference` → `references/approval-gates.md`).

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Validate Loop
1. **Load artifacts**: Read current-phase artifacts from `.beads/artifacts/<feature_slug>/` per artifact conventions (`beo-reference` → `references/artifact-conventions.md`): `phase-contract.md`, `story-map.md`, `plan.md`, and `CONTEXT.md`. Query beads via `br` and `bv` using canonical CLI behavior from the shared references.
2. **8-dimension structural check**: Run the plan-check workflow across all 8 dimensions per `references/validation-operations.md`. Use `references/plan-checker-prompt.md` for each dimension assessment.
3. **Bead-level review**: For each current-phase bead, verify acceptance criteria, verification steps, dependencies, and description quality. Use `references/bead-reviewer-prompt.md`.
4. **Decision**: If all checks pass, add `Approved`, note swarming eligibility, and hand off forward via the defined pipeline transitions. If any check fails, produce an ordered repair list and route back to `beo-plan`.

### Reference Files
| File | Purpose |
|------|---------|
| `references/validation-operations.md` | Operational sequence for running the structural validation gate |
| `references/plan-checker-prompt.md` | Prompt contract for evaluating each validation dimension |
| `references/bead-reviewer-prompt.md` | Prompt contract for bead-level specification review |

## Inputs and Outputs
- **Inputs** — Read `phase-contract.md`, `story-map.md`, `plan.md`, and `CONTEXT.md` from `.beads/artifacts/<feature_slug>/`, plus current-phase beads via `br`/`bv`, following artifact conventions (`beo-reference` → `references/artifact-conventions.md`).
- **Outputs** — Either add the `Approved` label to the epic or emit an ordered repair list routed back to `beo-plan`, with state and handoff artifacts using the required state and handoff artifacts.

## Validation Dimensions
1. **Phase-contract completeness** — The current phase contract is complete enough to execute without hidden planning work.
2. **Story-map structural integrity** — The story map is coherent, ordered, and aligned to current-phase execution.
3. **Bead specification quality** — Each bead is actionable, bounded, and has explicit acceptance criteria.
4. **Dependency graph acyclicity** — Dependencies are executable and free of blocking cycles.
5. **`CONTEXT.md` alignment** — Planned work aligns with locked requirements and constraints.
6. **Scope containment (current phase only)** — Validation covers only current-phase scope per the pipeline contract.
7. **Verification step coverage** — Every bead has concrete verification steps tied to acceptance criteria.
8. **Swarming eligibility assessment** — Ready-bead independence and file-scope separation are sufficient for possible swarm handoff.

## Decision Rubrics
- **Repair vs Route-Back** — If there are ≤3 issues and all are bead-level, return an ordered repair list to `beo-plan`. If issues are structural (`phase-contract.md`, `story-map.md`, cross-artifact integrity), route back to `beo-plan` with full diagnosis.
- **Spike or Not** — If a bead deliverable is framed as “investigate” or “research,” treat it as a spike. Spikes require an explicit deliverable format.
- **Clear Deliverable** — A deliverable is clear when a machine or a specifically described human action can verify it. Vague outcomes like “it works” or “looks good” fail.
- **Approval or Fail** — Approval requires all 8 dimensions to pass, all current-phase beads to be sufficiently specified, and all hard gates to remain satisfied. Any unresolved failure blocks approval.

## Failure Recovery Rules
> Recover all validation failure modes via standard failure recovery (`beo-reference` → `references/failure-recovery.md`).

## State and Approval Rules
- Follow the bead lifecycle states (`beo-reference` → `references/status-mapping.md`) for allowed state transitions associated with validation outcomes.
- Follow the beo approval gates (`beo-reference` → `references/approval-gates.md`) for approval timing, ownership, and label authority.

## Handoff
> Write `HANDOFF.json` for every skill transition (`beo-reference` → `references/pipeline-contracts.md`). Transitions follow the pipeline: route → explore → plan → validate → (execute | swarm → execute) → review → compound.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Modifying any artifact instead of evaluating it.
- Writing code or changing implementation files.
- Approving with unresolved failures.
- Checking future-phase beads as part of current-phase validation.
- Running multiple validation passes without producing a decision.
