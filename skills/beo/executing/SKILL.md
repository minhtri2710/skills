---
name: beo-executing
description: >-
  Use when an approved epic is ready for implementation and the next current-phase
  bead should be executed directly in single-worker mode or by a single worker
  inside a swarm. Use for prompts like "implement this bead", "do the work",
  "run the worker", "start implementing", "execute the next task", or
  whenever approved current-phase work needs to move from plan into verified
  implementation one task at a time.
---

# Beo Executing

## Overview

Executing is the per-worker implementation loop. It picks the next actionable task, assembles a worker prompt, dispatches a subagent to implement it, and reports results back.

## Key Terms

- **current phase**: the approved slice being implemented now
- **worker mode**: this skill is being used by a worker inside a swarm, so it should implement directly
- **standalone mode**: this skill is driving execution outside a swarm and may dispatch or implement directly depending on scope
- **reactive fix bead**: a post-planning fix bead created by review, debugging, or instant routing rather than initial planning

## Default Execution Loop

1. pick the next truly ready bead
2. verify the bead spec is complete enough to execute
3. reserve files and transition the bead cleanly
4. assemble only the context needed for this bead
5. dispatch if appropriate, otherwise implement directly
6. run verification
7. write the report artifact and update bead state
8. loop, or hand off when the current phase is complete

Use `references/execution-operations.md` for the exact scheduling cascade, transition protocol, dispatch contract, and completion bookkeeping.

**Two operating modes:**
- **Worker mode** (dispatched by `beo-swarming`): Receives identity and epic ID from the orchestrator. Reports progress via Agent Mail. Implements code directly. Does NOT spawn sub-subagents.
- **Standalone mode** (after `beo-validating` for ≤2 tasks): Acts as both dispatcher and executor. Reports progress via `STATE.md`. Can delegate implementation through the session's normal subagent/task mechanism, or implement directly for single-task features.

In both modes the loop is identical; the difference is how results are reported (Agent Mail vs `STATE.md`) and whether implementation is direct (worker mode) or delegated (standalone mode with multiple tasks).

**Core principle**: One task at a time. Implement, verify, report, loop.

Execution scope is always the **currently approved phase**. If planning mode is `multi-phase`, execution must not silently expand into later phases.

## Dispatch Modes and Fallbacks

When this skill says "dispatch a worker", use the session's normal subagent or task-execution mechanism. The exact tool name can vary by environment; the intent does not.

- **Worker mode**: do not dispatch again; implement the claimed bead directly.
- **Standalone delegated mode**: use when 2 or more ready beads exist and a worker-dispatch mechanism is available.
- **Standalone direct mode**: use when only one bead is ready, or delegation overhead would exceed the benefit.
- **Fallback rule**: if no subagent or task-dispatch mechanism is available, execute directly in standalone mode instead of inventing a pseudo-dispatch workflow.

Never block execution on finding a perfect dispatcher. Prefer direct execution over a vague or unreliable delegation path.

## Prerequisites

Default checks:

```bash
br show <EPIC_ID> --json
br dep list <EPIC_ID> --direction up --type parent-child --json
cat .beads/artifacts/<feature_slug>/CONTEXT.md 2>/dev/null
cat .beads/artifacts/<feature_slug>/plan.md 2>/dev/null
cat .beads/artifacts/<feature_slug>/phase-contract.md 2>/dev/null
cat .beads/artifacts/<feature_slug>/story-map.md 2>/dev/null
```

Load `references/execution-operations.md` for the exact prerequisite checks, current-phase scope verification, and epic-claim procedure.

<HARD-GATE>
If the epic does not have the `approved` label, do not treat planning artifacts as implicit approval. First verify the label was not accidentally removed or the wrong epic was selected. If approval is genuinely missing, route to `beo-validating`.
</HARD-GATE>

## The Execution Loop

```
┌─→ Schedule (pick next task)
│        ↓
│   Dispatch (build prompt, launch worker)
│        ↓
│   Monitor (worker runs, returns result)
│        ↓
│   Update (record outcome, update bead)
│        ↓
│   Check (more tasks? blockers? done?)
│        ↓
└── Loop or Complete
```

## Phase 1: Select Next Task

Load `references/execution-operations.md` for the scheduling cascade and task-selection procedure.

## Phase 2: Pre-Dispatch Checks

Load `references/execution-operations.md` for the exact pre-dispatch checks, stale-label cleanup, task-transition protocol, and current-phase scope check.

<HARD-GATE>
If `.description` is empty, or is missing file scope AND verification criteria, stop and treat the bead as invalid for execution.

"Task <TASK_ID> has an empty or underspecified description. Route back to beo-planning or beo-validating to complete the bead spec."

Do not reconstruct the full spec from `plan.md` or `CONTEXT.md`; that produces low-quality worker output. If the gap is purely clerical and the intended spec already exists verbatim elsewhere in the bead package, restore it faithfully. Otherwise route back.
</HARD-GATE>

### Bead Classes

Two classes of beads may reach execution:

| Class | Created By | Story Context Required | Minimum Description |
|-------|-----------|----------------------|-------------------|
| **Planned execution bead** | beo-planning | Yes (full story context block) | Story context + file scope + steps + verification |
| **Reactive fix bead** | beo-reviewing (P1), beo-debugging, beo-router (instant) | No (exempt) | File scope + what to fix + verification |

Reactive fix beads are exempt from the story context requirement because they are created after planning completes. They still require file scope and verification criteria.

### Transition to In-Progress

Reserve files before editing (required in worker mode, recommended in standalone mode). Use Agent Mail `file_reservation_paths` or coordinate via the file convention your project uses. Do not edit files without reserving them first.

Follow the canonical transition sequence in `references/execution-operations.md`.

## Phase 3: Worker Prompt Assembly

Build the complete worker prompt for the subagent. The prompt includes current-phase exit state, story context, plan summary, task spec, relevant `CONTEXT.md` decisions, previous task results, and verification criteria.

Minimum prompt payload:
- the full bead spec
- the current-phase exit state
- only the relevant story context
- only the relevant `CONTEXT.md` decisions
- only the prior task results this bead actually depends on
- the verification criteria

See `references/worker-prompt-guide.md` for the full prompt template, data gathering commands, and budget truncation rules.

**Key rule**: Never truncate the task spec itself; that is the core payload.

## Phase 4: Worker Dispatch

**Standalone mode only**: in worker mode, implement the task directly (skip to Phase 5 after implementation).

Load `references/execution-operations.md` for the canonical dispatch contract and worker-report expectations.

## Phase 5: Post-Worker Update

After the worker returns, update the bead graph.

Load `references/execution-operations.md` for the status-mapping quick table, report-artifact write pattern, and flush sequence.

## Phase 6: Progress Check

After each worker completes, load `references/execution-operations.md` for the canonical progress-check commands and decision table.

## Blocker Handling

When a task reports blocked, follow the classification and resolution protocol in `references/blocker-handling.md`. Key steps: understand the blocker, classify it (missing dependency / external / scope / ambiguous / technical), ask the user for a decision, then resume from Phase 1.

## Completion

When all current-phase tasks under the epic are closed, first verify that the phase exit state now appears true in practice, then load `references/execution-operations.md` for the final verification steps and canonical completion behavior for swarming mode vs single-worker mode.

Announce:
```text
Current-phase execution complete.
- <N>/<total> tasks completed successfully
- Build: <pass/fail>
- Tests: <pass/fail>
```

If `planning_mode = single-phase` and no later phases remain, load `beo-reviewing` for quality verification and feature completion.

If `planning_mode = multi-phase` and later phases remain, route back through the planning-aware flow instead of claiming the whole feature is complete.

## Context Budget

If context usage exceeds 65%, load `references/execution-operations.md` and follow the checkpoint procedure for the current operating mode.

## Post-Compaction Recovery

If you detect that context has been compacted (prior conversation is summarized), follow the recovery procedure in `references/execution-guardrails.md` to re-read `CONTEXT.md`, `approach.md`, current-phase context, and task state before resuming.

## Red Flags & Anti-Patterns

See `references/execution-guardrails.md` for the complete red flags and anti-patterns tables.
