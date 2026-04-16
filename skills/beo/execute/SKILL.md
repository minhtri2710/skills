---
name: beo-execute
description: |
  Use when exactly one approved bead is ready for implementation, either in single-worker mode or assigned by swarm. Execute claims the bead, makes only the required changes, runs the bead’s verification steps, and reports success or blocker. Only obvious local retries belong here; non-obvious diagnosis belongs to debug. Do not use for worker coordination, planning, validation, post-implementation review, or cross-feature learning work.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-execute

## Atomic purpose
Implement, verify, and report exactly one approved bead.

## When to use
- a single approved ready bead must be executed
- swarm assigned one specific bead to a worker
- a reactive fix has already been judged safe for direct execution by the canonical pipeline contract

## Inputs
**Required**
- one bead ID and its specification
- acceptance criteria and verification steps for that bead
- active epic approval state
- relevant source files

**Optional**
- swarm assignment metadata
- origin / return fields in `.beads/STATE.json` for reactive-fix execution

## Outputs
**Allowed writes**
- implementation changes required by the assigned bead
- verification evidence
- bead comments / status updates allowed by `beo-reference` → `references/status-mapping.md`
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- planning artifacts unless the canonical pipeline explicitly routes back for replan
- unrelated beads or cross-feature learnings
- review verdicts

## Boundary rules
- Execute owns only one bead at a time.
- Execute does not redesign scope, approve execution, coordinate multiple workers, perform post-phase review, or do broad root-cause analysis.
- If the blocker is not obvious and local, execute stops escalating through the proper edge instead of guessing.

## Minimum hard gates
- **APPROVED-ONLY** — Verify the active epic has the `approved` label before starting.
- **ONE-BEAD-AT-A-TIME** — Never parallelize within a worker.
- **STATUS-TRANSITIONS-ONLY** — Use only allowed bead transitions from `beo-reference` → `references/status-mapping.md`.
- **VERIFICATION-REQUIRED** — Never mark `done` without the bead's required verification evidence.
- **OBVIOUS-RETRIES-ONLY** — Keep retries local and bounded; non-obvious blockers escalate.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules for transitions to other skills.

## Default loop
1. Confirm the epic is approved and the bead is ready.
2. Claim the bead, move through the allowed status transitions, and load the relevant code and acceptance criteria.
3. Implement only the changes required for that bead.
4. Run the specified verification.
5. If verification passes, mark the bead `done` and record evidence.
6. If verification fails in an obvious local way, retry within the local limit.
7. If the issue is structural or non-obvious, record the blocker and hand off through the canonical pipeline (`beo-debug`, `beo-plan`, or `beo-review` path as appropriate), then stop.

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
- Escalation handoff: `beo-debug` for non-obvious blockers
- Execute stops after writing an inter-skill handoff.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- starting without verifying `approved`
- changing scope beyond the assigned bead
- marking work complete without verification evidence
- using execute to diagnose broad or unclear failures
- continuing after writing inter-skill handoff state
