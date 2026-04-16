---
name: beo-execute
description: |
  Use when an approved bead is ready for implementation by one worker, either self-directed or assigned by swarm. Claims one bead, constructs the implementation prompt, writes code, verifies against acceptance criteria, and reports outcome. Operates in two modes: single-worker (self-directed sequencing) and swarm-worker (assigned via Agent Mail). MUST NOT work on unapproved or unassigned beads, parallelize within a single worker, or skip verification before marking complete. Do not use for multi-worker orchestration (use beo-swarm), when the plan is not validated (use beo-validate), or for complex blocked-bead diagnosis (use beo-debug).
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-execute

## Overview
Implement one bead at a time from claim through verification and reporting, whether running independently or under swarm direction. **Core principle: one bead, one bounded implementation target, one verified outcome at a time.**

## Boundary Rules
- **MUST NOT** perform independent state detection or free-form routing — owned by `beo-route`. May emit canonical handoff to the next allowed pipeline skill when exit conditions are met.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** verify plans — owned by `beo-validate`.
- **MUST NOT** orchestrate parallel workers — owned by `beo-swarm`.
- **MUST NOT** review completed scope — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.
- **MUST NOT** diagnose complex root causes — owned by `beo-debug`.

## Hard Gates
> **HARD-GATE: APPROVED-ONLY** — Execute only runs on beads under an `approved`-labeled epic. Per the beo approval gates (`beo-reference` → `references/approval-gates.md`).

> **HARD-GATE: ONE-BEAD-AT-A-TIME** — Execute works on exactly one bead at a time. Never parallelize within a single worker.

> **HARD-GATE: STATUS-TRANSITIONS** — All bead status changes follow the bead lifecycle states (`beo-reference` → `references/status-mapping.md`) allowed transitions. Forbidden transitions abort the operation.

> **HARD-GATE: VERIFICATION-REQUIRED** — Every bead must pass its acceptance-criteria verification before being marked `done`. No unverified completion.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Execute Loop
1. **Claim**: In single-worker mode, select the next bead via the scheduling cascade (`beo-reference` → `references/dependency-and-scheduling.md`) (`bv --robot-plan` → `bv --robot-next` → `br ready` → manual). In swarm-worker mode, claim the assigned bead only.
2. **Pre-dispatch**: Validate the bead is still `open`, dependencies are satisfied, and file scope is still safe. Set status to `dispatch_prepared` per the bead lifecycle states (`beo-reference` → `references/status-mapping.md`), then transition to `in_progress` when active work begins.
3. **Build prompt**: Read the bead description, acceptance criteria, dependencies, and relevant source files. Build the implementation prompt per `references/worker-prompt-guide.md`.
4. **Implement**: Write code to satisfy the bead's acceptance criteria while following project conventions.
5. **Verify**: Run acceptance-criteria verification such as tests, linting, type-checking, or manual checks as specified. If verification fails, attempt a fix up to 2 retries. If it still fails, mark the bead `blocked` or `failed` and report.
6. **Report**: On success, set the bead status to `done` and record verification results in a bead comment. On failure, set `blocked`, `failed`, or `cancelled` as appropriate and describe the outcome in a bead comment. In swarm-worker mode, report via Agent Mail. In single-worker mode, either claim the next ready bead or hand off according to pipeline state.

### Reference Files
| File | Purpose |
|------|---------|
| `references/execution-operations.md` | Operational sequence for claiming, implementing, verifying, and reporting bead work |
| `references/worker-prompt-guide.md` | Rules for constructing implementation prompts from bead context |
| `references/blocker-handling.md` | Standard handling for retries, blockers, escalation, and reporting |

## Modes
- **Single-worker mode** — Self-directed execution. Select the next ready bead via the scheduling cascade (`beo-reference` → `references/dependency-and-scheduling.md`).
- **Swarm-worker mode** — Directed execution. Receive a bead assignment from `beo-swarm` via Agent Mail and execute only that assignment.

## Inputs and Outputs
- **Inputs** — A single bead claimed through `br`, plus worker prompt context from swarm or self-generated artifact/state context in `.beads/artifacts/<feature_slug>/`, using artifact conventions (`beo-reference` → `references/artifact-conventions.md`).
- **Outputs** — Implementation changes, verification results, bead comments, status updates using the canonical execution terms (`open`, `dispatch_prepared`, `in_progress`, `done`, `blocked`, `failed`, `cancelled`), and handoff/state artifacts using the required state and handoff artifacts.

## Blocker Handling
- **Implementation failure after 2 retries** — Mark `blocked` and add blocker detail with `br comments add <ID> --no-daemon --message "..."`.
- **External dependency missing** — Mark `blocked` and note the dependency explicitly.
- **Swarm-worker blocker** — Report the blocker to the swarm orchestrator via Agent Mail.
- **Complex blocker** — Hand off to `beo-debug` with origin context when root-cause analysis is required.

## Decision Rubrics
- **Fix vs Block** — If the failure is a simple code error with an obvious correction, retry up to 2 times. If it is structural, environmental, or unclear, block immediately.
- **Done vs Blocked/Failed** — If all acceptance criteria pass, mark `done`. If any acceptance criterion still fails, do not mark incomplete success; mark `blocked` or `failed` with details.
- **Next Bead vs Handoff** — In single-worker mode, if more ready beads exist, continue the loop. If no ready beads remain and some are blocked, hand off to `beo-debug`. If all current-phase beads are in terminal states and later phases remain, remove `approved` and hand off to `beo-plan`. If all current-phase beads are in terminal states for the final execution scope, hand off to `beo-review`.
- **Assignment Boundaries** — In swarm-worker mode, never expand scope beyond the assigned bead without a new swarm instruction.

## Scheduling, Approval, and Recovery Rules
- Follow the scheduling cascade (`beo-reference` → `references/dependency-and-scheduling.md`) for bead selection and readiness order.
- Follow the beo approval gates (`beo-reference` → `references/approval-gates.md`) for execution preconditions tied to approved scope.
- Follow the bead lifecycle states (`beo-reference` → `references/status-mapping.md`) for status transition legality.
- Recover all execution failures via standard failure recovery (`beo-reference` → `references/failure-recovery.md`).

## Handoff
> Write `STATE.json` for normal transitions to adjacent skills so the next skill has current implementation status, verification results, blockers, and artifact locations. Use `HANDOFF.json` only for emergency checkpoint or low-context resume scenarios.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Working on beads that are not under an approved epic.
- Skipping verification before marking work complete.
- Modifying beads outside the current assignment.
- Spending more than 2 retries on the same failure.
- Failing to report via Agent Mail in swarm mode.
- Using project-specific commands not called for by the bead description.
