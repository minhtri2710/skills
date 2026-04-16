---
name: beo-plan
description: |
  Use when `CONTEXT.md` is locked and the work needs technical design and current-phase decomposition. Plan reads the codebase, selects the implementation approach, writes planning artifacts, and creates the current-phase execution contract and bead graph. Do not use while requirements are still ambiguous, when only execution readiness must be checked, or for implementation, review, debugging, or learning work.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-plan

## Atomic purpose
Convert one locked feature into technical design artifacts and a current-phase bead plan.

## When to use
- `CONTEXT.md` is locked and technical design must be chosen
- later phases remain and the next current phase must be prepared
- validation or execution invalidated approved scope and the work must be replanned

## Inputs
**Required**
- `.beads/artifacts/<feature_slug>/CONTEXT.md`
- relevant codebase context
- feature identifier / slug

**Optional**
- existing planning artifacts for the same feature
- current bead graph and epic state from `br` / `bv`

## Outputs
**Allowed writes**
- `.beads/artifacts/<feature_slug>/discovery.md`
- `.beads/artifacts/<feature_slug>/approach.md`
- `.beads/artifacts/<feature_slug>/plan.md`
- `.beads/artifacts/<feature_slug>/phase-plan.md` when multi-phase work is required
- `.beads/artifacts/<feature_slug>/phase-contract.md`
- `.beads/artifacts/<feature_slug>/story-map.md`
- current-phase beads and dependency wiring via `br`
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- implementation code
- validation verdicts or `approved` labels
- review or learning artifacts

## Boundary rules
- Plan owns technical design and decomposition for the current phase.
- Plan does not gather requirements, approve execution, coordinate workers, implement code, review outcomes, debug blockers, or write learnings.
- Multi-phase planning is allowed, but only the current phase gets executable beads.

## Minimum hard gates
- **LOCKED-CONTEXT-REQUIRED** — Start only from a fully locked `CONTEXT.md`.
- **CURRENT-PHASE-ONLY** — Create executable beads only for the current phase.
- **NO-CODE** — Do not write implementation code.
- **APPROVAL-REMOVAL-ON-REPLAN** — If replanning invalidates a prior approval cycle, remove `approved` per `beo-reference` → `references/approval-gates.md`.
- **STRUCTURED-APPROVALS-ONLY** — Use the structured question tool for planning approvals when `phase-plan.md` requires them.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Read `CONTEXT.md`, existing artifacts, and the relevant code paths.
2. Write `discovery.md` to capture constraints, existing patterns, and important files.
3. Choose and record the implementation strategy in `approach.md`.
4. If the feature spans meaningful phases, write `phase-plan.md` and obtain the required planning approval before preparing the current phase.
5. Write `plan.md`, `phase-contract.md`, and `story-map.md`.
6. Create and wire current-phase beads via `br`, using the dependency rules from the shared references.
7. Write `.beads/STATE.json` for `beo-validate` or, if requirements were found to be insufficient, back-edge to `beo-explore`.
8. Stop.

## References
| File | Use when |
|------|----------|
| `references/planning-prerequisites.md` | Checking whether planning can start safely |
| `references/planning-state-and-cleanup.md` | Cleaning up stale plan state or resuming planning |
| `references/artifact-writing-guide.md` | Keeping planning artifacts high-signal and consistent |
| `references/bead-ops.md` | Creating / updating current-phase beads |
| `references/discovery-reference.md` | Structuring technical discovery |
| `references/approach-template.md` | Writing the chosen strategy |
| `references/plan-template.md` | Writing the full plan summary |
| `references/phase-plan-template.md` | Multi-phase sequencing |
| `references/phase-contract-template.md` | Defining current-phase execution boundaries |
| `references/story-map-template.md` | Mapping stories to current-phase beads |
| `beo-reference` → `references/dependency-and-scheduling.md` | Dependency wiring and readiness logic |
| `beo-reference` → `references/approval-gates.md` | Planning approval and approved-label lifecycle |

## Handoff and exit
- Normal forward handoff: `beo-validate`
- Normal backward handoff: `beo-explore` when locked requirements prove insufficient or contradictory
- Planning pauses with `ReturnToUser(...)` when explicit planning approval is required
- Plan never starts validation itself; it writes state and yields.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- planning from an unlocked or contradictory `CONTEXT.md`
- creating future-phase executable beads
- keeping or adding `approved` during replanning
- writing implementation details that belong in execute
- validating or reviewing the plan inside the planning skill
- continuing after handoff state is written
