---
name: beo-execute
description: |
  Use when an approved bead is ready for implementation by one worker, either self-directed or assigned by swarm. Triggers: "implement this bead", "do the work", "run the worker", "start implementing", "execute the next task". Per-worker implementation loop: claim, build prompt, dispatch, verify, report. MUST NOT work on unassigned beads, modify other workers' beads, skip verification, or parallelize within a single worker. Do not use for multi-worker orchestration (use beo-swarm) or when the plan is not yet validated.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-execute

## Overview
Implement one bead at a time from claim through verification and reporting, whether running independently or under swarm direction. **Core principle: one bead, one bounded implementation target, one verified outcome at a time.**

## Boundary Rules
- **MUST NOT** route to skills — owned by `beo-route`.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** verify plans — owned by `beo-validate`.
- **MUST NOT** orchestrate parallel workers — owned by `beo-swarm`.
- **MUST NOT** review completed scope — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.
- **MUST NOT** diagnose complex root causes — owned by `beo-debug`.

## Hard Gates
> **HARD-GATE: APPROVED-ONLY** — Execute only runs on beads under an `Approved`-labeled epic. Per the beo approval gates (`beo-reference` → `references/approval-gates.md`).

> **HARD-GATE: ONE-BEAD-AT-A-TIME** — Execute works on exactly one bead at a time. Never parallelize within a single worker.

> **HARD-GATE: STATUS-TRANSITIONS** — All bead status changes follow the bead lifecycle states (`beo-reference` → `references/status-mapping.md`) allowed transitions. Forbidden transitions abort the operation.

> **HARD-GATE: VERIFICATION-REQUIRED** — Every bead must pass its acceptance-criteria verification before being marked `done`. No unverified completion.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Execute Loop
1. **Claim**: In single-worker mode, select the next bead via the scheduling cascade from the scheduling cascade (`beo-reference` → `references/dependency-and-scheduling.md`) (`bv --robot-plan` → `bv --robot-next` → `br ready` → manual). In swarm-worker mode, claim the assigned bead. Set status to `in_progress` per the bead lifecycle states (`beo-reference` → `references/status-mapping.md`).
2. **Build prompt**: Read the bead description, acceptance criteria, dependencies, and relevant source files. Build the implementation prompt per `references/worker-prompt-guide.md`.
3. **Implement**: Write code to satisfy the bead's acceptance criteria while following project conventions.
4. **Verify**: Run acceptance-criteria verification such as tests, linting, type-checking, or manual checks as specified. If verification fails, attempt a fix up to 2 retries. If it still fails, mark the bead `blocked` and report.
5. **Report**: On success, set the bead status to `done` and record verification results in a bead comment. On failure, set `blocked` or `failed` and describe the blocker in a bead comment. In swarm-worker mode, report via Agent Mail. In single-worker mode, either claim the next ready bead or hand off according to pipeline state.

### Reference Files
| File | Purpose |
|------|---------|
| `references/execution-operations.md` | Operational sequence for claiming, implementing, verifying, and reporting bead work |
| `references/worker-prompt-guide.md` | Rules for constructing implementation prompts from bead context |
| `references/blocker-handling.md` | Standard handling for retries, blockers, escalation, and reporting |

## Modes
- **Single-worker mode** — Self-directed execution. Select the next ready bead via the scheduling cascade in the scheduling cascade (`beo-reference` → `references/dependency-and-scheduling.md`).
- **Swarm-worker mode** — Directed execution. Receive a bead assignment from `beo-swarm` via Agent Mail and execute only that assignment.

## Inputs and Outputs
- **Inputs** — A single bead claimed through `br`, plus worker prompt context from swarm or self-generated artifact/state context in `.beads/artifacts/<feature_slug>/`, using artifact conventions (`beo-reference` → `references/artifact-conventions.md`).
- **Outputs** — Implementation changes, verification results, bead comments, status updates (`done`, `blocked`, or `failed`), and handoff/state artifacts using the required state and handoff artifacts.

## Blocker Handling
- **Implementation failure after 2 retries** — Mark `blocked` and add blocker detail with `br comments add <ID> --no-daemon -c "..."`.
- **External dependency missing** — Mark `blocked` and note the dependency explicitly.
- **Swarm-worker blocker** — Report the blocker to the swarm orchestrator via Agent Mail.
- **Complex blocker** — Hand off to `beo-debug` with origin context when root-cause analysis is required.

## Decision Rubrics
- **Fix vs Block** — If the failure is a simple code error with an obvious correction, retry up to 2 times. If it is structural, environmental, or unclear, block immediately.
- **Done vs Partial** — If all acceptance criteria pass, mark `done`. If any acceptance criterion still fails, do not mark partial success; mark `blocked` with details.
- **Next Bead vs Handoff** — In single-worker mode, if more ready beads exist, continue the loop. If no ready beads remain and some are blocked, hand off to `beo-debug`. If all beads are done, hand off to `beo-review`.
- **Assignment Boundaries** — In swarm-worker mode, never expand scope beyond the assigned bead without a new swarm instruction.

## Scheduling, Approval, and Recovery Rules
- Follow the scheduling cascade (`beo-reference` → `references/dependency-and-scheduling.md`) for bead selection and readiness order.
- Follow the beo approval gates (`beo-reference` → `references/approval-gates.md`) for execution preconditions tied to Approved scope.
- Follow the bead lifecycle states (`beo-reference` → `references/status-mapping.md`) for status transition legality.
- Recover all execution failures via standard failure recovery (`beo-reference` → `references/failure-recovery.md`).

## Handoff
> Write `HANDOFF.json` for every skill transition (`beo-reference` → `references/pipeline-contracts.md`). Transitions follow the pipeline: route → explore → plan → validate → (execute | swarm → execute) → review → compound.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Working on beads that are not under an Approved epic.
- Skipping verification before marking work complete.
- Modifying beads outside the current assignment.
- Spending more than 2 retries on the same failure.
- Failing to report via Agent Mail in swarm mode.
- Using project-specific commands not called for by the bead description.
