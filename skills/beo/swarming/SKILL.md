---
name: beo-swarming
description: >-
  Use when an approved current phase has 3 or more independent ready tasks and
  parallel execution will materially reduce cycle time. Use for prompts about
  swarming, parallel workers, launching multiple agents, coordinating a worker
  pool, or running approved current-phase work at scale. Do not use for
  single-worker execution (use beo-executing instead) or when fewer than 3
  independent ready tasks exist.
---

<HARD-GATE>
Onboarding — see `../reference/references/shared-hard-gates.md` § Onboarding Check.
</HARD-GATE>

> See `../reference/references/shared-hard-gates.md` § Shared References Convention.

# Beo Swarming

## Overview

Swarming orchestrates parallel current-phase execution.
Launch workers, coordinate them through the live graph and Agent Mail, resolve conflicts, and keep the approved phase moving.

**Core principle:** the orchestrator coordinates; workers execute.

## Hard Gates

<HARD-GATE>
If you are editing source code, stop immediately and route that work to `beo-executing`.
</HARD-GATE>

<HARD-GATE>
If Agent Mail is unavailable before workers are launched, do NOT attempt swarming. Degrade to `beo-executing`.
If Agent Mail fails mid-swarm with active workers: stop spawning new workers, wait for in-flight workers to report or time out, reconcile all file reservations, confirm single-worker ownership of any remaining work, then degrade to `beo-executing`.
</HARD-GATE>

<HARD-GATE>
The current phase must have 3 or more independent tasks that are open (`pending` status) and parallel-safe (no overlapping file scopes, no blocking dependencies between them). If fewer than 3 qualify, route to `beo-executing` instead.
</HARD-GATE>

<HARD-GATE>
Before dispatching workers, verify that no two workers are assigned beads with overlapping file scopes. Each file must have exactly one owning worker. If file scopes overlap, either split the file scope between beads or serialize the overlapping beads into a single worker's queue.
</HARD-GATE>

<HARD-GATE>
Approval verification — see `../reference/references/shared-hard-gates.md` § Approval Verification.
</HARD-GATE>

<HARD-GATE>
If no active epic or current-phase task beads exist, do not attempt swarming. Route to `beo-router` for state detection and proper intake.
</HARD-GATE>

## Role Boundary

You are the **ORCHESTRATOR**. Launch workers, monitor coordination, handle escalations, and keep the approved current phase moving. Do **not** implement beads or edit source files.

- **beo-swarming** = launch and tend workers
- **beo-executing** = each worker's implementation loop

## Default Swarm Loop

1. confirm current-phase execution is approved and swarm-worthy
2. confirm Agent Mail is healthy enough for coordination
3. register the coordinator and announce the swarm
4. spawn bounded workers with explicit current-phase scope
5. monitor completions, blockers, idle workers, and file conflicts
6. reassign, rescue, or degrade when coordination stops paying off
7. route to `beo-reviewing` for final scope, or remove `approved` and route to `beo-planning` when later phases remain

| File | Use for |
| --- | --- |
| `references/swarming-operations.md` | readiness checks, worker-spawn contract, monitor/tend loop, progress heuristics, and completion/checkpoint mechanics |
| `references/message-templates.md` | Agent Mail bodies |
| `../reference/references/worker-template.md` | worker context |

## Decision Rubrics

Keep detailed swarm mechanics in the references; use these tie-breaks inline:

### Swarm or degrade

| Choose | When |
| --- | --- |
| Swarm | Parallelism reduces cycle time after coordination overhead |
| Degrade to `beo-executing` | Worker slots, Agent Mail health, or file-scope contention make the phase effectively serial |

### Repeated conflicts

| Trigger | Action |
| --- | --- |
| Same lane conflicts twice | Stop treating it as parallel-safe |
| Conflict repeats | Serialize that lane, re-scope ownership, or degrade the remaining work |

## Active Swarm Never Idles

If workers are spawned, online, busy, blocked, or expected to report, you are in a tending phase.
Keep looping through Agent Mail and the live bead graph. Do not treat a quiet thread as permission to stop.

---

## Handoff

See `references/swarming-operations.md` § 5. Swarm Completion for the full completion checklist, graph verification, and routing logic.

## Context Budget

Follow `../reference/references/shared-hard-gates.md` § Context Budget Protocol. Skill-specific checkpoint items: active workers, reservations, blockers, and the current planning-aware route state.

---

## Red Flags & Anti-Patterns

See `references/swarming-operations.md` for monitoring heuristics and completion checks.
Verify coordinator behavior against `references/pressure-scenarios.md` when debugging swarm coordination failures.
Stop and diagnose before continuing if:
- the orchestrator starts editing code
- workers go idle while ready current-phase beads still exist
- Agent Mail falls quiet for too long
- file conflicts repeat
- stale reservations survive resume
- current-phase completion is being mistaken for final review while later phases remain
