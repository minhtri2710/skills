---
name: beo-swarm
description: |
  Use when an Approved current phase has 3+ independent ready beads with non-overlapping file scopes and parallel execution will materially reduce cycle time. Triggers: prompts about swarming, parallel workers, launching multiple agents, coordinating a worker pool, or running approved work at scale. Orchestrates parallel worker agents for feature execution using Agent Mail. MUST NOT implement code directly, operate on unvalidated plans, or swarm fewer than 3 independent tasks. Do not use for single-worker execution (use beo-execute) or when fewer than 3 independent ready tasks exist.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-swarm

## Overview
Coordinate parallel worker execution across independent current-phase beads without file-scope collisions. **Core principle: orchestrate only — assign, monitor, and resolve coordination issues without editing implementation code.**

## Boundary Rules
- **MUST NOT** route to skills — owned by `beo-route`.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** verify plans — owned by `beo-validate`.
- **MUST NOT** write implementation code — owned by `beo-execute`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.
- **MUST NOT** diagnose root causes — owned by `beo-debug`.

## Hard Gates
> **HARD-GATE: NO-CODE-EDITING** — Swarm never writes, modifies, or deletes implementation code. It orchestrates only.

> **HARD-GATE: AGENT-MAIL-REQUIRED** — All worker communication uses Agent Mail per the Agent Mail protocol (`beo-reference` → `references/agent-mail-coordination.md`). No direct state mutation.

> **HARD-GATE: THREE-PLUS-INDEPENDENT** — Swarm requires ≥3 independent ready beads with non-overlapping file scopes. If <3, degrade to single-worker `beo-execute`.

> **HARD-GATE: NO-OVERLAPPING-FILE-SCOPES** — Two workers must never be assigned beads that touch the same file. If overlap is detected, reassign or serialize.

> **HARD-GATE: APPROVAL-VERIFICATION** — Swarm only runs on `Approved`-labeled epics. Per the beo approval gates (`beo-reference` → `references/approval-gates.md`).

> **HARD-GATE: ACTIVE-EPIC-REQUIRED** — A current epic must exist. If no epic exists, route to `beo-plan`.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Swarm Loop
1. **Enumerate ready beads**: Query `br` for ready beads in the current phase. Filter by independence and file scope.
2. **Assign workers**: Create worker assignments so each worker gets exactly 1 bead. Use the standard worker prompt template (`beo-reference` → `references/worker-template.md`) for worker prompt structure.
3. **Dispatch workers**: Send assignments via Agent Mail per `references/message-templates.md`.
4. **Monitor progress**: Poll worker status and track completion, blockers, and conflicts.
5. **Resolve conflicts**: If file-scope overlap appears mid-execution, pause the conflicting worker and reassign per `references/swarming-operations.md`.
6. **Report completion**: When all assigned beads complete or block, aggregate results.
7. **Decide next**: If more ready beads exist, loop to step 1. If all work is done, hand off to `beo-review`. If degradation is triggered, hand off to `beo-execute`.

### Reference Files
| File | Purpose |
|------|---------|
| `references/swarming-operations.md` | Coordination flow, assignment rules, and runtime swarm operations |
| `references/message-templates.md` | Agent Mail message formats for worker dispatch and updates |
| `references/pressure-scenarios.md` | Expected swarm behavior under contention, failures, and load |

## Inputs and Outputs
- **Inputs** — Approved current-phase beads with at least 3 independent ready items and non-overlapping file scopes, using artifact and state contracts from `.beads/artifacts/<feature_slug>/` using artifact conventions (`beo-reference` → `references/artifact-conventions.md`).
- **Outputs** — Worker assignments sent through Agent Mail, conflict-resolution decisions, degradation decisions, and handoff/state artifacts using the required state and handoff artifacts.

## Decision Rubrics
- **Swarm or Degrade** — If there are ≥3 independent ready beads with non-overlapping scopes, swarm. Otherwise, degrade to `beo-execute` via `HANDOFF.json`.
- **Repeated Conflicts** — If the same file-scope conflict occurs 2 or more times across different bead pairs, serialize those beads and continue swarming the rest.
- **Active Swarm Never Idles** — If a worker finishes and more ready beads exist, assign the next bead immediately. Do not batch-wait.
- **Conflict Resolution Priority** — Prefer reassignment first; if safe reassignment is impossible, serialize only the minimal conflicting subset.

## Degradation Triggers
| Trigger | Action |
|---------|--------|
| `<3 independent beads` | Degrade to `beo-execute` |
| `Agent Mail unavailable` | Degrade to `beo-execute` per standard failure recovery (`beo-reference` → `references/failure-recovery.md`) |
| `Repeated file conflicts` | Serialize conflicting beads and continue the rest |
| `All beads blocked` | Hand off to `beo-debug` |

## Scheduling and State Rules
- Follow the scheduling cascade (`beo-reference` → `references/dependency-and-scheduling.md`) for readiness reconciliation and assignment ordering.
- Follow the bead lifecycle states (`beo-reference` → `references/status-mapping.md`) for allowed status transitions affected by swarm coordination.
- Follow the beo approval gates (`beo-reference` → `references/approval-gates.md`) for approval preconditions before swarm startup.

## Failure Recovery Rules
> Recover all swarm failure modes via standard failure recovery (`beo-reference` → `references/failure-recovery.md`).

## Handoff
> Write `HANDOFF.json` for every skill transition (`beo-reference` → `references/pipeline-contracts.md`). Transitions follow the pipeline: route → explore → plan → validate → (execute | swarm → execute) → review → compound.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Writing code directly from the swarm coordinator.
- Assigning overlapping file scopes.
- Continuing coordination without Agent Mail.
- Idling while ready beads are available.
- Running swarm on a non-approved epic.
