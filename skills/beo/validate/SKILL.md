---
name: beo-validate
description: |
  Decide whether the current phase is executable by checking the locked context, current-phase contract, story map, and bead graph for pre-execution completeness. Use it only for the readiness gate and execution-mode selection, not for repairing the plan or implementing the work.

---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-validate

## Atomic purpose
Gate execution readiness only.

## When to use
- current-phase planning artifacts exist and execution readiness must be checked
- an earlier approval may be stale and needs a fresh gate
- the next step depends on whether the current phase is sufficiently specified to implement

## Inputs
**Required**
- locked `.beads/artifacts/<feature_slug>/CONTEXT.md`
- current-phase `.beads/artifacts/<feature_slug>/phase-contract.md`
- current-phase `.beads/artifacts/<feature_slug>/story-map.md`
- current-phase bead graph and bead details from `br` and `bv`

**Optional**
- supporting planning artifacts when needed

## Outputs
**Allowed writes**
- `approved` label management on the active epic
- one readiness verdict: approved or remediation required
- ordered remediation list in the validation response
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- planning artifacts
- bead descriptions or dependency graphs
- implementation code

## Boundary rules
- Validate owns the pre-execution correctness gate only.
- Validate must not repair or rewrite planning artifacts, bead specs, or dependencies.
- Validate must not write code, coordinate execution, perform post-execution review, or debug failures.
- Validate decides readiness for the current phase only.

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
- Pause: `next: "user"` when explicit execution approval is required
- Validate never repairs artifacts itself.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- editing artifacts during validation
- approving with any unresolved structural or bead-level failure
- checking future-phase work as part of the current gate
- treating planning artifacts as implicit approval
- continuing after approval or remediation handoff is written
