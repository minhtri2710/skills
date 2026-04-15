---
name: beo-executing
description: >-
  Use when an approved epic is ready for implementation and the next current-phase
  bead should be executed directly in single-worker mode or by a single worker
  inside a swarm. Use for prompts like "implement this bead", "do the work",
  "run the worker", "start implementing", "execute the next task", or
  whenever approved current-phase work needs to move from plan into verified
  implementation one task at a time. Do not use for multi-worker orchestration
  (use beo-swarming instead).
---

<HARD-GATE>
Onboarding — see `../reference/references/shared-hard-gates.md` § Onboarding Check.
</HARD-GATE>

> See `../reference/references/shared-hard-gates.md` § Shared References Convention.

# Beo Executing

## Overview

Executing is the per-worker loop for approved current-phase work.
Pick one ready bead, execute safely, verify, report, and repeat.

**Core principle:** one task at a time — implement, verify, report, loop.

Execution scope is always the **currently approved phase**. If planning mode is `multi-phase`, do not expand into later phases.

## Operating Modes

- **Worker mode**: dispatched by `beo-swarming`; implement directly, report to the orchestrator, and do **not** spawn sub-subagents.
- **Standalone mode**: entered after `beo-validating`; implement directly or delegate through the normal subagent/task mechanism when overhead is justified. Keep execution one bead at a time; route multi-bead parallel work to `beo-swarming`.
- **Solo mode**: use when Agent Mail or reservation APIs are unavailable. Enter only after confirming no active workers, in-flight beads, or uncoordinated reservations; otherwise pause and report the conflict. Then execute one bead at a time with exclusive local file ownership.

The loop is the same in all three modes; only reporting and delegation change.

## Hard Gates

<HARD-GATE>
If no active epic or current-phase task beads exist, do not attempt execution. Route to `beo-router` for state detection and proper intake.
</HARD-GATE>

<HARD-GATE>
Approval verification — see `../reference/references/shared-hard-gates.md` § Approval Verification.
</HARD-GATE>

<HARD-GATE>
If a bead description is empty or still fails the execution-critical-detail check below, stop and treat it as invalid for execution.
Execution requires concrete file scope and verification criteria.
Do not reconstruct the full spec from `plan.md` or `CONTEXT.md`.
If the gap is purely clerical and the intended spec already exists verbatim elsewhere in the bead package, restore it faithfully; otherwise route to `beo-validating` for clerical spec-completeness defects, or to `beo-planning` if the gap involves scope, decomposition, or story-boundary changes.
</HARD-GATE>

<HARD-GATE>
Reactive fix beads are exempt only from the story-context requirement.
They still require file scope, a clear fix target, and verification criteria.
</HARD-GATE>

<HARD-GATE>
Execute only current-phase work.
If `phase-plan.md` exists and the selected bead belongs to a later phase, do not execute it.
Route back through the planning-aware flow.
</HARD-GATE>

<HARD-GATE>
Do not mark a bead as `done` until verification has run and passed.
</HARD-GATE>

<HARD-GATE>
Do not edit files that are reserved by another active worker.
If file ownership is unclear, treat the file as contested and coordinate before editing.
</HARD-GATE>

<HARD-GATE>
If specs must change during execution in a way that alters file scope, adds or removes beads, changes story boundaries, or invalidates the phase contract exit state, stop treating the phase as execution-ready.
Strip `approved` (`br label remove <EPIC_ID> -l approved`) and route back to planning-aware repair.
</HARD-GATE>

## Default Execution Loop

1. verify approval and current-phase scope
2. pick the next truly ready bead
3. verify the bead spec is executable
4. reserve files and transition the bead cleanly
5. assemble only the context needed for this bead
6. dispatch if appropriate, otherwise implement directly
7. run verification, write the report, and update bead state
8. loop, or hand off when the current phase is complete

| File | Use for |
| --- | --- |
| `references/execution-operations.md` | scheduling cascade, transition protocol, dispatch contract, status mapping, completion bookkeeping, checkpoint procedure |
| `references/worker-prompt-guide.md` | full worker prompt template |

## Execution Notes

- **Before implementation:** Verify prerequisites, task selection, stale-label cleanup, and description checks per `references/execution-operations.md` sections 1-4. Validate any swarming startup hint against the live graph.
- **File coordination:** Reserve files before editing per `references/execution-operations.md` section 5. Use `references/worker-prompt-guide.md` for the prompt template. Never truncate the bead spec.
- **Dispatch:** Implement directly in worker mode. In standalone mode, delegate only when overhead is justified. Use `references/execution-operations.md` sections 6-7 for dispatch and result-to-state mapping. If blocked, use `references/blocker-handling.md` and resume from task selection.
- **State flushing:** After any status transition or reservation update, flush graph state.

## Decision Rubrics

Use these tie-breaks without duplicating the full execution operations.

### Pick the next bead

| Priority | Prefer |
| --- | --- |
| 1 | no unresolved dependency |
| 2 | uncontested file scope |
| 3 | closes the most immediate story or blocker |

If beads are equally ready, choose the one with the smaller blast radius.

### Implement directly vs delegate

| Choose | When |
| --- | --- |
| Implement directly | bead is narrow, needed context is already local, or delegation overhead is comparable to the work |
| Delegate | bead is still single-worker-sized and implementation effort materially exceeds prompt/setup overhead |

### Execution-critical detail

| Required detail | Meaning |
| --- | --- |
| target files or surfaces | where to act |
| intended change | what to do |
| verification | how success will be checked |

If any are missing, the bead is not execution-ready.

## Completion

When all current-phase tasks are closed, run the completion and routing procedure in `references/execution-operations.md` section 8. When later phases remain, do **not** claim the whole feature is complete.

For multi-phase completion routing, see `../reference/references/shared-hard-gates.md` § Multi-Phase Completion Routing.

Do not track completion only in the conversation. Once verification passes, update the bead state in the graph immediately.

## Handoff

When the current phase closes successfully:
- route to `beo-reviewing` if this completes the final execution scope
- remove `approved` and route to `beo-planning` if later phases remain
- never describe current-phase completion as full feature completion when multi-phase work remains

## Context Budget

Follow `../reference/references/shared-hard-gates.md` § Context Budget Protocol. Skill-specific checkpoint items: current execution state via `references/execution-operations.md`, and planning-aware fields when known.

## Post-Compaction Recovery

If context was compacted, re-read the essential feature artifacts (`CONTEXT.md`, `plan.md`, `phase-contract.md`, `story-map.md`), relevant state files, and the live task graph before resuming. Continue from the last known good state rather than guessing from memory.

## Red Flags & Anti-Patterns

Avoid duplicate dispatch, speculative redispatch after failures, stale reservation collisions, duplicate completion updates, and worker prompts that omit verification requirements.
