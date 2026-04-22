---
name: beo-plan
description: |
  Turn a locked `CONTEXT.md` into current-phase design artifacts and executable bead specs when work needs solution design or replanning. Use only for solution design and current-phase decomposition, not for requirement locking, readiness gating, implementation, review, or learning.

---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-plan

## Atomic purpose
Define the current-phase solution and executable bead set.

## When to use
- `CONTEXT.md` is locked and the work needs technical design
- the next current phase must be prepared for validation and execution
- approved or planned work must be replanned because the solution changed

## Inputs
**Required**
- locked `.beads/artifacts/<feature_slug>/CONTEXT.md`
- relevant codebase context
- feature slug or identifier

**Optional**
- existing planning artifacts for the feature
- current bead graph and epic state from `br` and `bv`

## Outputs
**Allowed writes**
- `.beads/artifacts/<feature_slug>/discovery.md`
- `.beads/artifacts/<feature_slug>/approach.md`
- `.beads/artifacts/<feature_slug>/plan.md`
- `.beads/artifacts/<feature_slug>/phase-plan.md` when needed
- `.beads/artifacts/<feature_slug>/phase-contract.md`
- `.beads/artifacts/<feature_slug>/story-map.md`
- current-phase beads and dependency wiring via `br`
- removal of stale `approved` state when replanning invalidates a prior approval cycle
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- implementation code
- validation verdicts or execution approval state
- review or learning artifacts

## Boundary rules
- Plan owns solution design only.
- Plan must route to `beo-explore` if requirements are not locked.
- Plan creates only current-phase executable specifications.
- Plan must not validate readiness, grant execution approval, implement code, review work, debug blockers, or write learnings.

## Minimum hard gates
- **LOCKED-CONTEXT-REQUIRED** — Start only from a fully locked `CONTEXT.md`.
- **CURRENT-PHASE-ONLY** — Create executable beads only for the current phase.
- **NO-CODE** — Do not write implementation code.
- **APPROVAL-REMOVAL-ON-REPLAN** — If replanning invalidates a prior approval cycle, remove `approved` per `beo-reference` → `references/approval-gates.md`.
- **CANONICAL-APPROVAL-PROTOCOL** — Use the runtime's canonical user-interaction mechanism for planning approvals when `phase-plan.md` requires them.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Read `CONTEXT.md`, existing artifacts, and the relevant code paths.
2. Write `discovery.md` to capture constraints, existing patterns, and important files. For features that restructure routing, move files, or change import primitives (e.g. navigation libraries, module paths), explicitly list all consuming files across ALL directories — not only the files being moved — as integration points requiring update.
3. Choose and record the implementation strategy in `approach.md`.
4. If the feature spans meaningful phases, write `phase-plan.md` and obtain the required planning approval before preparing the current phase.
5. Write `plan.md`, `phase-contract.md`, and `story-map.md`.
6. Create and wire current-phase beads via `br`, using the dependency rules from the shared references. Beads involving structural changes (file moves, routing restructure, import-primitive migration) must explicitly include acceptance criteria for auditing all consuming code — not just the files being moved.
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
- Planning pauses with `next: "user"` when explicit planning approval is required
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
- structural-change beads (routing restructure, file moves, library migration) that list only target files without auditing consuming code across the full codebase
