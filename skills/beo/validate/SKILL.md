---
name: beo-validate
description: |
  Gate current-phase execution readiness from locked requirements, current-phase contracts, and bead specs, then choose `beo-execute` or `beo-swarm` when approved. Use only for the pre-execution gate, not for planning repair, bead rewriting, or implementation.

---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-validate

## Atomic purpose
Decide whether the current phase is ready and pick the execution mode.

## When to use
- current-phase planning artifacts exist and execution readiness must be checked
- an earlier approval may be stale and needs a fresh gate
- the next step depends on whether the current phase is specified well enough to implement

## Inputs
**Required**
- locked `.beads/artifacts/<feature_slug>/CONTEXT.md`
- current-phase `.beads/artifacts/<feature_slug>/phase-contract.md`
- current-phase `.beads/artifacts/<feature_slug>/story-map.md`
- current-phase bead graph and bead details from `br` and `bv`

**Optional**
- supporting planning artifacts only when the gate needs more context

## Outputs
**Allowed writes**
- `approved` label management on the active epic
- one readiness verdict: approved or remediation required
- ordered remediation list in the validation response
- execution-mode selection (`beo-execute` or `beo-swarm`) when approved
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- planning artifacts
- bead descriptions or dependency graphs
- implementation code

## Boundary rules
- Validate owns the pre-execution gate only.
- Validate is read-only except for approval state and canonical handoff state.
- Validate must not repair artifacts, rewrite bead specs or dependencies, write code, coordinate execution, review outcomes, or debug failures.
- Validate decides readiness for the current phase only.

## Minimum hard gates
- **READ-ONLY-VALIDATION** — The only mutable state owned here is approval state and canonical handoff state.
- **CURRENT-PHASE-ONLY** — Validate only the current phase.
- **NO-CODE-BEFORE-APPROVAL** — If implementation already exists for unapproved current-phase work, fail validation and route back appropriately.
- **UNDERSPECIFIED-BEAD-FAILS-THE-GATE** — Missing acceptance criteria, verification steps, or clear deliverables block approval.
- **APPROVAL-OWNERSHIP** — Only validate adds `approved`.
- **CANONICAL-APPROVAL-PROTOCOL** — If human execution approval is required, request it via the runtime's canonical user-interaction mechanism before adding `approved`.
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
