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

Executing is the per-worker implementation loop for approved current-phase work.
Its job is to pick one truly ready bead, execute it safely, verify the result, report it, and repeat.

**Core principle:** one task at a time — implement, verify, report, loop.

Execution scope is always the **currently approved phase**. If planning mode is `multi-phase`, do not silently expand into later phases.

## Operating Modes

- **Worker mode**: dispatched by `beo-swarming`; implement directly, report to the orchestrator, and do **not** spawn sub-subagents.
- **Standalone mode**: entered after `beo-validating`; may delegate through the session's normal subagent/task mechanism or implement directly, depending on scope and overhead.

The loop is the same in both modes. The main differences are how results are reported and whether delegated dispatch is available.

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
Use `references/execution-guardrails.md` for recovery steps and anti-patterns.

## Hard Gates

<HARD-GATE>
If the epic does not have the `approved` label, do not treat planning artifacts as implicit approval.
First verify the label was not accidentally removed or the wrong epic was selected.
If approval is genuinely missing, do not execute:
- if current-phase tasks have already advanced, treat approval as invalidated and route to `beo-planning`
- otherwise route to `beo-validating`
</HARD-GATE>

<HARD-GATE>
If a bead description is empty or still lacks execution-critical detail, stop and treat it as invalid for execution.
At minimum, execution requires concrete file scope and verification criteria.
Do not reconstruct the full spec from `plan.md` or `CONTEXT.md`.
If the gap is purely clerical and the intended spec already exists verbatim elsewhere in the bead package, restore it faithfully; otherwise route back to `beo-planning` or `beo-validating`.
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
If specs must change materially during execution, stop treating the phase as execution-ready.
Strip `approved` and route back to planning-aware repair instead of silently rewriting the plan in execution.
</HARD-GATE>

## Execution Notes

Use `references/execution-operations.md` for the exact prereq checks, task-selection cascade, transition protocol, state mapping, completion bookkeeping, and checkpoint procedure.

### Before implementation
Confirm:
- the epic is the correct one and still `approved`
- current-phase scope is understood
- the selected bead is still open, executable, and belongs to the current phase
- blocking dependencies are closed
- stale `blocked` / `failed` / `partial` labels are cleared when appropriate

If `beo-swarming` supplied a startup hint, still verify it against the live graph before acting.

### Bead classes
Two bead classes may reach execution:
- **Planned execution bead** — created by `beo-planning`; requires story context, file scope, execution steps, and verification.
- **Reactive fix bead** — created after planning by review, debugging, or instant routing; does not require story context, but still requires file scope, what to fix, and verification.

### File coordination and prompt assembly
Reserve files before editing. In worker mode this is required; in standalone mode use an explicit reservation mechanism when available or equivalent coordination when it is not.
Do not edit files when ownership is unclear.

Every worker prompt must include:
- the full bead spec
- the current-phase exit state
- only the relevant story context
- only the relevant `CONTEXT.md` decisions
- only the prior task results this bead actually depends on
- the verification criteria

Use `references/worker-prompt-guide.md` for the full template and budget rules.
Never truncate the bead spec itself.

### Dispatch and result handling
- **Worker mode**: implement directly after the pre-dispatch checks.
- **Standalone delegated mode**: use when multiple ready beads exist and a reliable dispatch mechanism is available.
- **Standalone direct mode**: use when only one bead is ready or delegation overhead would exceed the benefit.
- **Fallback rule**: if no dispatch mechanism is available, execute directly instead of inventing pseudo-dispatch.

After implementation or worker return, map the result to bead state using `references/execution-operations.md`, write the report artifact, flush state updates, and continue only after the graph is current again.

Expected result classes remain `done`, `blocked`, `failed`, or `partial`.
If a task is blocked, use `references/blocker-handling.md` and then resume from task selection.

## Handoff

When the current phase closes successfully:
- route to `beo-reviewing` if this completes the final execution scope
- remove `approved` and route to `beo-planning` if later phases remain
- never describe current-phase completion as full feature completion when multi-phase work remains

## Completion

When all current-phase tasks under the epic are closed:
1. verify the current-phase exit state appears true in practice
2. run project-specific verification
3. write fresh `.beads/STATE.md` using `../reference/references/state-and-handoff-protocol.md`
4. announce the next skill

Routing rules:
- if `planning_mode = single-phase` and no later phases remain -> `beo-reviewing`
- if `planning_mode = multi-phase` and later phases remain -> remove `approved`, then route to `beo-planning`
- if `planning_mode = multi-phase` and this was the final phase -> `beo-reviewing`

When later phases remain, do **not** claim the whole feature is complete.
This is a phase-advance back-edge, not a successful final review path.
Before routing back, remove the approval label:

```bash
br label remove <EPIC_ID> -l approved
```

## Context Budget

If context usage exceeds 65%, write `.beads/HANDOFF.json` using `../reference/references/state-and-handoff-protocol.md`, then checkpoint the current execution state using the procedure in `references/execution-operations.md`.
Include planning-aware fields when known.

## Post-Compaction Recovery

If context has been compacted, use `references/execution-guardrails.md` to re-read the core artifacts, current task graph, and any existing `STATE.md` / `HANDOFF.json` before resuming.

## Red Flags & Anti-Patterns

See `references/execution-guardrails.md` for the full tables.
