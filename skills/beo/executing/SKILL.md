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

Executing is the per-worker implementation loop for approved current-phase work.
Its job is to pick one truly ready bead, execute it safely, verify the result, report it, and repeat.

**Core principle:** one task at a time — implement, verify, report, loop.

Execution scope is always the **currently approved phase**. If planning mode is `multi-phase`, do not silently expand into later phases.

## Operating Modes

- **Worker mode**: dispatched by `beo-swarming`; implement directly, report to the orchestrator, and do **not** spawn sub-subagents.
- **Standalone mode**: entered after `beo-validating`; may delegate through the session's normal subagent/task mechanism or implement directly, depending on scope and overhead. Standalone delegation is still one-bead-at-a-time — if multiple beads would benefit from parallel execution, route to `beo-swarming` instead.
- **Solo mode**: standalone execution when Agent Mail or reservation APIs are unavailable. Before entering Solo mode, verify that no other beo workers are active (check for in-flight beads in the graph and any existing reservation state). If active workers or reservations exist but cannot be coordinated, do not enter Solo mode — pause and report the conflict to the user. Once exclusivity is confirmed, execute one bead at a time, avoid speculative parallelism, and treat local file ownership as exclusive.

The loop is the same in all three modes. The main differences are how results are reported and whether delegated dispatch is available.

## Hard Gates

<HARD-GATE>
If no active epic or current-phase task beads exist, do not attempt execution. Route to `beo-router` for state detection and proper intake.
</HARD-GATE>

<HARD-GATE>
Approval verification — see `../reference/references/shared-hard-gates.md` § Approval Verification.
</HARD-GATE>

<HARD-GATE>
If a bead description is empty or still lacks execution-critical detail, stop and treat it as invalid for execution.
At minimum, execution requires concrete file scope and verification criteria.
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
Route back through the planning-aware flow instead.
</HARD-GATE>

<HARD-GATE>
Do not mark a bead as `done` until verification has run and passed.
Verification means the bead's stated verification criteria (tests, build, lint, or manual check) have been executed and the results confirm the deliverable works.
</HARD-GATE>

<HARD-GATE>
Do not edit files that are reserved by another active worker.
If file ownership is unclear (no reservation system active or reservation state is stale), treat the file as contested and coordinate before editing.
</HARD-GATE>

<HARD-GATE>
If specs must change during execution in a way that alters file scope, adds or removes beads, changes story boundaries, or invalidates the phase contract exit state, stop treating the phase as execution-ready.
Strip `approved` (`br label remove <EPIC_ID> -l approved`) and route back to planning-aware repair instead of silently rewriting the plan in execution.
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

Use `references/execution-operations.md` for the exact scheduling cascade, transition protocol, dispatch contract, status mapping, completion bookkeeping, and checkpoint procedure.
Use `references/worker-prompt-guide.md` for the full worker prompt template.

## Execution Notes

- **Before implementation:** Verify prerequisites, task selection, stale-label cleanup, and description checks per `references/execution-operations.md` sections 1-4. If swarming supplied a startup hint, verify it against the live graph.
- **File coordination:** Reserve files before editing; see `references/execution-operations.md` section 5 and `references/worker-prompt-guide.md` for the prompt template. Never truncate the bead spec.
- **Dispatch:** Implement directly in worker mode; delegate in standalone mode when overhead is justified; never invent pseudo-dispatch. See `references/execution-operations.md` sections 6-7 for dispatch and result-to-state mapping. If blocked, use `references/blocker-handling.md` and resume from task selection.
- **State flushing:** After any status transition or reservation update, flush graph state so downstream routing does not depend on stale metadata.

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

Avoid duplicate dispatch, speculative redispatch after failures, silent spec rewrites during execution, and worker prompts that omit verification requirements.
