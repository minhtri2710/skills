# State Routing Table

Canonical state routing table from `beo-reference` → `../../reference/references/pipeline-contracts.md`. Evaluate **top-to-bottom, first match wins**.

| # | Condition | State | Route To |
|---|-----------|-------|----------|
| 1 | Skill creation or editing requested | **meta-skill** | `beo-writing-skills` |
| 2 | Any tasks have `blocked` or `failed` labels, `debug_attempted` label absent | **needs-debugging** | `beo-debugging` |
| 3 | Any tasks have `blocked` or `failed` labels, `debug_attempted` label present | **blocked** | Report blockers, ask user for decision |
| 4 | All tasks closed, epic closed, no learnings file | **learnings-pending** | `beo-compounding` |
| 5 | Epic is closed | **completed** | Report status, ask for next work |
| 6 | Any tasks have `partial` or `cancelled` labels, epic still open | **partial-completion** | Report status, ask user for decision |
| 7 | Epic exists, all tasks closed, epic still open | **ready-to-review** | `beo-reviewing` |
| 8 | Epic exists, tasks exist, some in_progress/closed (and no blocked/failed) | **executing** | `beo-executing` |
| 9 | Epic exists, tasks exist, `approved` label on epic, all tasks open, 3+ independent tasks | **ready-to-swarm** | `beo-swarming` |
| 10 | Epic exists, tasks exist, `approved` label on epic, all tasks open, ≤2 independent tasks | **ready-to-execute** | `beo-executing` |
| 11 | Epic exists, tasks exist, no `approved` label, phase-contract.md AND story-map.md exist | **ready-to-validate** | `beo-validating` |
| 12 | Epic exists, tasks exist, no `approved` label, phase-contract.md or story-map.md missing | **planning** | `beo-planning` |
| 13 | Epic exists, no tasks, no `approved` label | **exploring** | `beo-exploring` |
| 14 | Learnings stale (last dream >30 days or 3+ new learnings since last dream), user requests consolidation | **consolidation-due** | `beo-dream` |

**Evaluation order**: Explicit user intent (Row 1) short-circuits feature-state routing. Most-specific closed states (Rows 4-5) before generic. `debug_attempted` label (Rows 2-3) makes routing machine-decidable.
