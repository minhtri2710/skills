---
name: beo-swarm
description: |
  Use when execution is already approved and at least three independent ready beads with non-overlapping file scopes make parallel coordination worthwhile. Swarm assigns beads to workers, monitors progress, resolves coordination conflicts, and aggregates status; if those preconditions disappear, it degrades to execute. Do not use for single-bead work, plan validation, code implementation by the coordinator, review, debugging, or learning capture.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-swarm

## Atomic purpose
Coordinate safe parallel execution across multiple approved current-phase beads.

## When to use
- at least 3 independent ready beads exist
- their file scopes do not overlap
- parallel coordination will outperform serial execution

## Inputs
**Required**
- approved current-phase ready bead set
- dependency / readiness state
- declared file scopes for candidate beads
- Agent Mail availability

**Optional**
- existing worker status from a resumed swarm session

## Outputs
**Allowed writes**
- worker assignments and coordination messages
- orchestration state / status updates allowed by the canonical protocols
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- implementation code
- planning or review artifacts
- feature learnings

## Boundary rules
- Swarm owns assignment, monitoring, conflict resolution, and degradation decisions.
- Swarm does not implement code, redesign plans, approve work, review outcomes, debug substantive root causes, or extract learnings.
- Worker implementation remains owned by `beo-execute` running in worker mode.

## Minimum hard gates
- **THREE-PLUS-INDEPENDENT** — Start only when at least 3 independent ready beads exist.
- **NO-OVERLAPPING-FILE-SCOPES** — Assignment scopes must not overlap.
- **APPROVED-ONLY** — Swarm runs only on approved current-phase work.
- **AGENT-MAIL-REQUIRED** — Coordination requires Agent Mail; otherwise degrade.
- **NO-CODE-EDITING** — The coordinator does not edit implementation code.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Enumerate current-phase ready beads and confirm they are independent and non-overlapping.
2. Assign one bead per worker using Agent Mail.
3. Monitor worker progress, blockers, and file-scope drift.
4. Resolve coordination conflicts by reassignment or minimal serialization.
5. Continue dispatching while useful parallel work remains.
6. If preconditions collapse, degrade to `beo-execute`.
7. If the current phase completes, hand off according to the canonical pipeline and stop.

## References
| File | Use when |
|------|----------|
| `references/swarming-operations.md` | Running coordinator logic and conflict handling |
| `references/message-templates.md` | Sending worker assignments and updates |
| `references/pressure-scenarios.md` | Checking expected behavior under contention or failure |
| `beo-reference` → `references/agent-mail-coordination.md` | Agent Mail protocol |
| `beo-reference` → `references/dependency-and-scheduling.md` | Readiness and assignment ordering |
| `beo-reference` → `references/pipeline-contracts.md` | Degradation and downstream transitions |

## Handoff and exit
- Degrade to `beo-execute` when parallel coordination no longer makes sense
- Hand off to `beo-plan` when later phases remain after current-phase completion
- Hand off to `beo-review` when the final execution scope is complete
- Return control to the user when all remaining work is blocked and a decision is required
- Swarm stops after writing inter-skill handoff state.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- coordinator editing code
- assigning overlapping file scopes
- running with fewer than 3 independent beads
- continuing without Agent Mail
- continuing after writing inter-skill handoff state
