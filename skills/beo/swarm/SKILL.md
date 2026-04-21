---
name: beo-swarm
description: |
  Coordinate parallel workers across approved independent current-phase beads when concurrency is safe and materially better than serial execution. Use only for orchestration, not for implementation, replanning, approval, review, debugging, or learning work.

---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-swarm

## Atomic purpose
Coordinate parallel workers for approved independent beads.

## When to use
- approved current-phase work contains at least 3 independent ready beads
- candidate beads have non-overlapping file scopes
- parallel coordination is materially better than serial execution

## Inputs
**Required**
- approved current-phase ready bead set
- dependency and readiness state
- declared file scopes for candidate beads
- Agent Mail availability

**Optional**
- existing worker status from a resumed swarm session

## Outputs
**Allowed writes**
- worker-to-bead assignments
- coordination and progress messages
- orchestration metadata or state updates allowed by protocol
- `swarming` label on epic (added on swarm start, removed on swarm exit or degradation)
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- implementation code
- planning or review artifacts
- feature learnings

## Boundary rules
- Swarm owns parallel coordination only.
- The coordinator must not implement code, redesign plans, approve work, review outcomes, debug root causes, or write learnings.
- Swarm must not assign overlapping file scopes or claim completion beyond worker evidence and orchestration state.
- Swarm must degrade to `beo-execute` when safe parallelism stops applying.

## Minimum hard gates
- **THREE-PLUS-INDEPENDENT** — Start only when at least 3 independent ready beads exist.
- **NO-OVERLAPPING-FILE-SCOPES** — Assignment scopes must not overlap.
- **APPROVED-ONLY** — Swarm runs only on approved current-phase work.
- **AGENT-MAIL-REQUIRED** — Coordination requires Agent Mail; otherwise degrade.
- **NO-CODE-EDITING** — The coordinator does not edit implementation code.
- **SWARMING-LABEL** — Add `swarming` label on swarm start; remove it on completion, degradation, or handoff.
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
