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
If `.beads/onboarding.json` is missing or stale, stop and load `beo-using-beo` before continuing.
</HARD-GATE>

> **Shared references** — this skill references specific `beo-reference` docs by path. Do not co-load the full `beo-reference` skill; read individual reference docs as needed.
>
> Also uses `../reference/references/communication-standard.md` for inter-skill message formatting.

# Beo Swarming

## Overview

Swarming is the orchestration layer for parallel current-phase execution.
Its job is to launch workers, coordinate them through the live graph and Agent Mail, resolve conflicts, and keep the approved current phase moving.

**Core principle:** the orchestrator coordinates; workers execute.

## Hard Gates

<GUIDELINE>
If you are editing source code, stop immediately and route that work to `beo-executing`.
The orchestrator coordinates; workers execute. See the Role Boundary section below.
</GUIDELINE>

<HARD-GATE>
If Agent Mail is unavailable before workers are launched, do NOT attempt swarming. Degrade to `beo-executing`.
If Agent Mail fails mid-swarm with active workers: stop spawning new workers, wait for in-flight workers to report or time out, reconcile all file reservations, confirm single-worker ownership of any remaining work, then degrade to `beo-executing`. Do not leave orphaned reservations or uncoordinated concurrent workers.
</HARD-GATE>

<HARD-GATE>
The current phase must have 3 or more independent tasks that are open (`pending` status) and parallel-safe (no overlapping file scopes, no blocking dependencies between them). If fewer than 3 qualify, route to `beo-executing` instead.
</HARD-GATE>

<HARD-GATE>
Before dispatching workers, verify that no two workers are assigned beads with overlapping file scopes. Each file must have exactly one owning worker. If file scopes overlap, either split the file scope between beads or serialize the overlapping beads into a single worker's queue.
</HARD-GATE>


<HARD-GATE>
If the epic does not have the `approved` label, do not treat planning artifacts as implicit approval.
First verify the label was not accidentally removed or the wrong epic was selected.
If approval is genuinely missing, do not execute:
- if current-phase tasks have already advanced, treat approval as invalidated and route to `beo-planning`
- otherwise route to `beo-validating`
</HARD-GATE>

## Role Boundary

You are the **ORCHESTRATOR**. Launch workers, monitor coordination, handle escalations, and keep the approved current phase moving. Do **not** implement beads or edit source files yourself.

- **beo-swarming** = launch and tend workers
- **beo-executing** = each worker's implementation loop

## Default Swarm Loop

1. confirm current-phase execution is approved and swarm-worthy
2. confirm Agent Mail is healthy enough to coordinate
3. register the coordinator and announce the swarm
4. spawn bounded workers with explicit current-phase scope
5. monitor completions, blockers, idle workers, and file conflicts
6. reassign, rescue, or degrade when coordination stops paying off
7. route to `beo-reviewing` for final scope or remove `approved` and route to `beo-planning` when later phases remain

Use `references/swarming-operations.md` for the exact readiness checks, worker-spawn contract, monitor/tend loop, progress heuristics, and completion/checkpoint mechanics.
Use `references/message-templates.md` for Agent Mail bodies.
Use `../reference/references/worker-template.md` when building worker context.

## Active Swarm Never Idles

If workers are spawned, online, busy, blocked, or expected to report, you are in a tending phase.
Keep looping through Agent Mail and the live bead graph. Do not treat a quiet thread as permission to stop coordinating.

---

## Handoff

See `references/swarming-operations.md` § Swarm Completion for the full completion checklist, graph verification, and routing logic.

## Context Budget

If context usage exceeds 65%, use `../reference/references/state-and-handoff-protocol.md` for the canonical `STATE.json` and `HANDOFF.json` shapes, then checkpoint active workers, reservations, blockers, and the current planning-aware route state.

---

## Red Flags & Anti-Patterns

See `references/swarming-operations.md` for monitoring heuristics and completion checks.
Verify coordinator behavior against `references/pressure-scenarios.md` when debugging swarm coordination failures.
Stop and diagnose before continuing if the orchestrator starts editing code, workers go idle while ready current-phase beads still exist, Agent Mail falls quiet for too long, file conflicts repeat, or current-phase completion is being mistaken for final review while later phases remain.
