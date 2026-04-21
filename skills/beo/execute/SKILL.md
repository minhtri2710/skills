---
name: beo-execute
description: |
  Implement exactly one approved ready bead, run its required verification, and record the result when bounded delivery work is ready. Use only for single-bead implementation delivery, not for planning, approval, multi-bead coordination, diagnosis-heavy investigation, review, or learning capture.

---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-execute

## Atomic purpose
Deliver one approved bead and verify it.

## When to use
- a single approved ready bead must be executed
- `beo-swarm` assigned one specific bead to a worker
- an allowed reactive-fix path requires direct implementation work

## Inputs
**Required**
- one bead ID and bead specification
- acceptance criteria and verification steps
- active epic approval state
- relevant source files

**Optional**
- swarm assignment metadata
- reactive-fix origin or return fields in `.beads/STATE.json`

## Outputs
**Allowed writes**
- implementation changes required for the assigned bead
- verification evidence
- allowed bead status updates and comments
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- planning artifacts unless the canonical pipeline explicitly routes back for replan
- unrelated beads or cross-feature learnings
- review verdicts

## Boundary rules
- Execute owns scoped implementation delivery only, one bead at a time.
- Execute must not redesign scope or plan, validate or approve work, coordinate multiple workers, perform diagnosis-heavy root-cause investigation beyond bounded local retries, or do post-execution review or learning extraction.
- Execute must not work on more than one bead at a time.
- When a failure exceeds the bounded retry limit or requires investigation beyond the assigned bead's scope, execute must stop and route through the canonical escalation path.

## Minimum hard gates
- **APPROVED-ONLY** — Verify the active epic has the `approved` label before starting.
- **ONE-BEAD-AT-A-TIME** — Never parallelize within a worker.
- **STATUS-TRANSITIONS-ONLY** — Use only allowed bead transitions from `beo-reference` → `references/status-mapping.md`.
- **VERIFICATION-REQUIRED** — Never mark `done` without the bead's required verification evidence.
- **BOUNDED-LOCAL-RETRIES** — Keep retries local and within the configured limit; failures exceeding the limit escalate.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules for transitions to other skills.

## Default loop
1. Confirm the epic is approved and the bead is ready.
2. Claim the bead, move through the allowed status transitions, and load the relevant code and acceptance criteria.
3. Implement only the changes required for that bead.
4. Run the specified verification.
5. If verification passes, mark the bead `done` and record evidence.
6. If verification fails within bounded local retry scope, retry within the configured limit.
7. If the failure exceeds the retry limit or requires cross-bead investigation, record the blocker and hand off through the canonical pipeline (`beo-debug`, `beo-plan`, or `beo-review` path as appropriate), then stop.

## References
| File | Use when |
|------|----------|
| `references/execution-operations.md` | Following the canonical claim → build → verify → report flow |
| `references/worker-prompt-guide.md` | Building the implementation prompt from bead context |
| `references/blocker-handling.md` | Deciding retry vs block vs escalation |
| `beo-reference` → `references/dependency-and-scheduling.md` | Selecting the next ready bead in single-worker mode |
| `beo-reference` → `references/approval-gates.md` | Verifying execution preconditions |
| `beo-reference` → `references/pipeline-contracts.md` | Reactive-fix and back-edge rules |

## Handoff and exit
- Normal self-loop: another ready bead in single-worker mode
- Forward handoff: `beo-review` when the final execution scope is complete
- Backward handoff: `beo-plan` when later phases remain or approved scope is invalidated
- Escalation handoff: `beo-debug` for failures exceeding the bounded retry limit
- Execute stops after writing an inter-skill handoff.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- starting without verifying `approved`
- changing scope beyond the assigned bead
- marking work complete without verification evidence
- using execute to diagnose broad or unclear failures
- continuing after writing inter-skill handoff state
