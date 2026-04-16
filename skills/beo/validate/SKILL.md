---
name: beo-validate
description: |
  Use when current-phase planning artifacts exist and execution readiness needs a binary gate before implementation begins. Validate reads the locked context, current-phase contract, story map, and current-phase bead graph, then either approves execution or returns an ordered remediation list. Only validate may add the `approved` label. Do not use to repair planning artifacts, write code, review completed work, or diagnose blockers.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-validate

## Atomic purpose
Gate current-phase execution readiness with one decision: approve or remediate.

## When to use
- current-phase planning artifacts are present and execution must be approved or rejected
- approved scope may have become stale and needs a fresh gate
- quick-path intake has produced the minimum planning artifacts required for validation

## Inputs
**Required**
- locked `.beads/artifacts/<feature_slug>/CONTEXT.md`
- current-phase `.beads/artifacts/<feature_slug>/phase-contract.md`
- current-phase `.beads/artifacts/<feature_slug>/story-map.md`
- current-phase bead graph and details from `br` / `bv`

**Optional**
- `.beads/artifacts/<feature_slug>/plan.md`
- `.beads/artifacts/<feature_slug>/approach.md`

## Outputs
**Allowed writes**
- `approved` label management on the active epic
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it
- ordered remediation report in the validation response

**Must not write**
- planning artifacts
- bead descriptions or dependency graphs
- implementation code

## Boundary rules
- Validate is a read-only gate over current-phase planning quality.
- Validate does not repair failures itself; it only decides readiness.
- Validate owns the execution-readiness decision and validates only the current phase.

## Minimum hard gates
- **READ-ONLY-VALIDATION** — The only mutable state owned here is approval state and canonical handoff state.
- **CURRENT-PHASE-ONLY** — Validate only the current phase.
- **NO-CODE-BEFORE-APPROVAL** — If implementation already exists for unapproved current-phase work, fail validation and route back appropriately.
- **UNDERSPECIFIED-BEAD-FAILS-THE-GATE** — Missing acceptance criteria, verification steps, or clear deliverables block approval.
- **APPROVAL-OWNERSHIP** — Only validate adds `approved`.
- **STRUCTURED-APPROVALS-ONLY** — If human execution approval is required, request it via the structured question tool before adding `approved`.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Read the locked context, current-phase artifacts, and current-phase bead graph.
2. Run the 8-dimension structural check using `references/validation-operations.md` and `references/plan-checker-prompt.md`.
3. Review every current-phase bead for acceptance criteria, verification, dependency correctness, and deliverable clarity using `references/bead-reviewer-prompt.md`.
4. If all checks pass, obtain any required user approval, add `approved`, recommend `beo-execute` or `beo-swarm`, write `.beads/STATE.json`, and stop.
5. If any check fails, produce an ordered remediation list for `beo-plan`, write `.beads/STATE.json`, and stop.

## References
| File | Use when |
|------|----------|
| `references/validation-operations.md` | Running the validation gate end-to-end |
| `references/plan-checker-prompt.md` | Applying the canonical 8 validation dimensions |
| `references/bead-reviewer-prompt.md` | Reviewing bead-level specification quality |
| `beo-reference` → `references/approval-gates.md` | Approved-label ownership and execution approval timing |
| `beo-reference` → `references/failure-recovery.md` | Recovering from malformed or interrupted validation |

## Handoff and exit
- Forward handoff: `beo-execute` or `beo-swarm` after approval
- Backward handoff: `beo-plan` for remediation
- Pause: `ReturnToUser(...)` when explicit execution approval is required
- Validate never repairs artifacts itself.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- editing artifacts during validation
- approving with any unresolved structural or bead-level failure
- checking future-phase work as part of the current gate
- treating planning artifacts as implicit approval
- continuing after approval or remediation handoff is written
