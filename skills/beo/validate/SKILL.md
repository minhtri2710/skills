---
name: beo-validate
description: |
  Use when current-phase planning artifacts exist and need a binary execution-readiness gate before implementation begins. Reads phase-contract.md, story-map.md, and bead graph, runs 8-dimension structural verification, and either approves or returns an ordered remediation list. Only validate may add the approved label. Do not use to modify artifacts (use beo-plan), write code (use beo-execute), assess post-implementation quality (use beo-review), or diagnose failures (use beo-debug).
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-validate

## Overview
**Atomic purpose: verify plan artifacts meet all 8 quality dimensions and gate execution readiness.** Gate execution by approving or rejecting the current-phase plan. **Core principle: inspect and decide without modifying planning artifacts, dependency graphs, or bead descriptions.**

## Boundary Rules
- **MUST NOT** perform independent state detection or free-form routing — owned by `beo-route`. May emit canonical handoff to the next allowed pipeline skill when exit conditions are met.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** write or modify plans — owned by `beo-plan`.
- **MUST NOT** write code — owned by `beo-execute`.
- **MUST NOT** orchestrate workers — owned by `beo-swarm`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.

## Hard Gates
> **HARD-GATE: NO-CODE-BEFORE-APPROVAL** — No implementation code until validation passes and the `approved` label is set. If code exists, fail validation.

> **HARD-GATE: READ-ONLY-VALIDATION** — Validate does not modify planning artifacts, dependency edges, priorities, spike beads, or bead descriptions. The only permitted writes are `approved` label management, `STATE.json` for normal transitions, `HANDOFF.json` for emergency checkpoint/resume scenarios, and minimal `.beads/STATE.json` updates for phase, skill, and next_action.

> **HARD-GATE: UNDERSPECIFIED-BEAD-FAIL** — Any bead missing acceptance criteria or verification steps fails the entire validation. No partial passes.

> **HARD-GATE: CURRENT-PHASE-ONLY** — Validate only checks beads for the current phase. Future-phase beads are out of scope.

> **HARD-GATE: SPIKE-NO-INVALIDATES** — If a bead is marked as spike, it must have a clear deliverable (report, prototype, decision). Spikes without deliverables fail validation.

> **HARD-GATE: APPROVAL-OWNERSHIP** — Only validate adds the `approved` label. Per the beo approval gates (`beo-reference` → `references/approval-gates.md`).

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Validate Loop
1. **Load artifacts**: Read current-phase artifacts from `.beads/artifacts/<feature_slug>/` per artifact conventions (`beo-reference` → `references/artifact-conventions.md`): `phase-contract.md`, `story-map.md`, `plan.md`, and `CONTEXT.md`. Query beads via `br` and `bv` using canonical CLI behavior from the shared references.
2. **8-dimension structural check**: Run the plan-check workflow across all 8 dimensions per `references/validation-operations.md`. Use `references/plan-checker-prompt.md` for each dimension assessment.
3. **Bead-level review**: For each current-phase bead, verify acceptance criteria, verification steps, dependencies, and description quality. Use `references/bead-reviewer-prompt.md`.
4. **Decision**: If all checks pass, add `approved`, include an execution-mode recommendation, and hand off forward via the defined pipeline transitions. If any check fails, produce an ordered repair list for `beo-plan` and route back without fixing artifacts directly.

### Reference Files
| File | Purpose |
|------|---------|
| `references/validation-operations.md` | Operational sequence for running the structural validation gate |
| `references/plan-checker-prompt.md` | Prompt contract for evaluating each validation dimension |
| `references/bead-reviewer-prompt.md` | Prompt contract for bead-level specification review |

## Inputs and Outputs
- **Inputs** — `CONTEXT.md`, `plan.md`, `phase-contract.md`, `story-map.md`, current-phase bead definitions and dependencies from `.beads/artifacts/<feature_slug>/` and `br`/`bv`.
- **Outputs** — Validation decision (`approved` or `rejected`), ordered remediation list when rejected, `approved` label update when approved, `STATE.json` for normal transitions.

## Validation Dimensions
Validate uses a canonical 8-dimension model defined in `references/plan-checker-prompt.md`.

Briefly, the dimensions cover:
1. Phase contract clarity
2. Story coverage and ordering
3. Decision coverage from `CONTEXT.md`
4. Dependency correctness
5. File-scope isolation
6. Context-budget fit
7. Verification completeness
8. Exit-state completeness and risk alignment

See `references/plan-checker-prompt.md` for the canonical evaluation dimensions and pass/fail criteria.

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
> Write `STATE.json` for normal adjacent-skill transitions with validation results, blocking issues, approval status, and artifact pointers. Use `HANDOFF.json` only for emergency checkpoint or low-context resume scenarios.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Modifying any artifact instead of evaluating it.
- Modifying dependency graphs, priorities, or bead descriptions during validation.
- Writing code or changing implementation files.
- Approving with unresolved failures.
- Checking future-phase beads as part of current-phase validation.
- Running multiple validation passes without producing a decision.
