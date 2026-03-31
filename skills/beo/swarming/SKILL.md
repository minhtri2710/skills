---
name: beo-swarming
description: >-
  Use when an approved epic has 3 or more independent ready tasks and parallel
  execution will materially reduce cycle time. Orchestrates bounded workers,
  monitors blockers and file conflicts, coordinates rescues, and hands off to
  reviewing when all execution beads are closed. Use for prompts about
  swarming, parallel workers, launching multiple agents, coordinating a worker
  pool, or running approved work at scale.
---

# Swarming

## Role Boundary: Read First

You are the **ORCHESTRATOR**. You launch workers, monitor coordination, handle escalations, and keep the swarm moving. You do NOT implement beads. If you find yourself editing source files, stop immediately. That is the `beo-executing` skill's job.

- **beo-swarming** = launches and tends workers (this skill)
- **beo-executing** = each worker's self-routing implementation loop

The orchestrator launches the swarm, then tends it. Workers decide what to do next by using `bv --robot-plan` against the live bead graph.

<HARD-GATE>
If Agent Mail is unavailable, do NOT attempt swarming. Degrade to `beo-executing`.
</HARD-GATE>

If Agent Mail becomes unavailable mid-run, stop launching new workers, let active workers finish if possible, and degrade remaining work to `beo-executing`.

## Minimal Swarm Checklist

1. Confirm the epic is approved and at least 3 independent ready tasks exist
2. Confirm Agent Mail is working before spawning any workers
3. Register the coordinator and announce the swarm
4. Spawn bounded workers with explicit bead scope
5. Monitor completions, blockers, idle workers, and file conflicts
6. Reassign, rescue, or degrade when workers stall
7. Hand off to `beo-reviewing` only after all execution beads are closed

## Worker Count Heuristic

Start with one worker per independent ready track, capped by coordination safety rather than optimism.

- 3 ready tracks -> usually 2-3 workers
- 4-6 ready tracks -> usually 3-4 workers
- Shared-file hotspots or fragile infrastructure -> bias downward
- Never spawn more workers than independent ready tracks

If unsure, start smaller and expand only after the first monitor loop is healthy.

## Rescue and Degrade Rules

- If a worker is silent for >10 poll cycles, ping once and inspect Agent Mail, reservations, and graph state
- If the worker is still silent after one rescue attempt, stop assigning it new work and re-route the bead
- If the same file conflict happens twice, pause that lane and escalate decomposition or ownership clarity
- If 2 or more workers stall, or coordination costs exceed progress, stop expanding the swarm and degrade remaining work to `beo-executing`

---

## Phase 1: Confirm Swarm Readiness

Load `references/swarming-operations.md` for the exact readiness checks, epic-claim step, and scheduling cascade.

---

## Phase 2: Initialize Agent Mail

Load `references/swarming-operations.md` for the exact Agent Mail setup sequence, coordinator registration, and thread bootstrap pattern. Use `references/message-templates.md` for message bodies.

---

## Phase 3: Spawn Workers

Load `references/swarming-operations.md` for the exact worker-spawn contract, worker input shape, and `STATE.md` tracking expectations. Use `references/worker-template.md` when building worker context.

---

## Phase 4: Monitor + Tend

Load `references/swarming-operations.md` for the exact monitor/tend loop, event types, progress heuristics, and checkpoint mechanics. Use `references/message-templates.md` for mail content.

---

## Phase 5: Swarm Complete

Load `references/swarming-operations.md` for the exact completion checks, `STATE.md` update, and Agent Mail completion announcement.

---

## Red Flags

Stop and diagnose before continuing if you see:

- **Worker implements multiple beads at once**: self-routing does not mean parallelizing within one worker
- **Orchestrator edits source files**: role violation
- **Workers are idle but ready beads exist**: check mail, reservations, or startup drift
- **No Agent Mail activity for >10 poll cycles**: workers may be stuck or context-exhausted
- **The same file conflict repeats**: bead decomposition may be too coarse; escalate
- **Workers stop using `bv --robot-plan` and start freelancing**: re-broadcast the execution contract
- **Build/test failures accumulate without intervention**: create fix beads or stop and escalate

---

## Reference Files

Load when needed:

| File | Load When |
|---|---|
| `references/worker-template.md` | Spawning any worker (Phase 3) |
| `references/message-templates.md` | Posting or parsing Agent Mail messages |
