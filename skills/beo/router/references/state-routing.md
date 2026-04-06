# State Routing Table

Canonical state routing table from `beo-reference` → `../../reference/references/pipeline-contracts.md`. Evaluate **top-to-bottom, first match wins**.

| # | Condition | State | Route To |
|---|-----------|-------|----------|
| 1 | Skill creation or editing requested | **meta-skill** | `beo-writing-skills` |
| 2 | User explicitly requests learnings consolidation / dream work and the request is not impossible or stale | **consolidation-requested** | `beo-dream` |
| 3 | No active epic exists and the new request is clearly debug work | **new-debug-intake** | `beo-debugging` |
| 4 | No active epic exists and the new request is clearly instant-scoped work | **new-instant-intake** | create epic + instant scaffold, then `beo-validating` |
| 5 | No active epic exists and the request is normal feature intake | **new-feature-intake** | create epic, then `beo-exploring` |
| 6 | Any tasks have `blocked` or `failed` labels, `debug_attempted` label absent | **needs-debugging** | `beo-debugging` |
| 7 | Any tasks have `blocked` or `failed` labels, `debug_attempted` label present | **blocked** | Report blockers, ask user for decision |
| 8 | Epic is closed, any child task NOT closed | **invalid-epic-closure** | Report inconsistency, route to `beo-executing` or `beo-reviewing` to resolve open tasks |
| 9 | All tasks closed, epic closed, no learnings file | **learnings-pending** | `beo-compounding` |
| 10 | Epic is closed | **completed** | Report status, ask for next work |
| 11 | Any tasks have `partial` or `cancelled` labels, epic still open | **partial-completion** | Report status, ask user for decision |
| 12 | Epic exists, all tasks for the current phase are closed, epic still open, and later phases remain | **phase-complete-needs-replan** | `beo-planning` |
| 13 | Epic exists, all tasks for the final execution scope are closed, epic still open, and no later phases remain | **ready-to-review** | `beo-reviewing` |
| 14 | Epic exists, current-phase tasks exist, no `approved` label, and some current-phase tasks are already `in_progress` or `closed` | **approval-invalidated** | `beo-planning` |
| 15 | Epic exists, current-phase tasks exist, `approved` label on epic, and some current-phase tasks are `in_progress` or `closed` (and no blocked/failed) | **executing** | `beo-executing` |
| 16 | Epic exists, current-phase tasks exist, `approved` label on epic, all tasks open, 3+ independent tasks | **ready-to-swarm** | `beo-swarming` |
| 17 | Epic exists, current-phase tasks exist, `approved` label on epic, all tasks open, ≤2 independent tasks | **ready-to-execute** | `beo-executing` |
| 18 | Epic exists, current-phase tasks exist, no `approved` label, `phase-contract.md` AND `story-map.md` exist, and execution approval has not yet been granted or was removed on a back-edge | **ready-to-validate** | `beo-validating` |
| 19 | Epic exists, `approach.md` exists, no `approved` label, current-phase artifacts missing or incomplete | **planning-current-phase** | `beo-planning` |
| 20 | Epic exists, `CONTEXT.md` exists, no `approach.md` | **planning-needs-approach** | `beo-planning` |
| 21 | Epic exists, no tasks, no `approved` label | **exploring** | `beo-exploring` |

**Evaluation order**: explicit user intent short-circuits feature-state routing when it is actionable. Most-specific closed states come before generic execution states. Current-phase completion is not whole-feature completion when later phases remain, and execution resumes only while the `approved` lifecycle is still valid.

Ordering notes:
1. Keep explicit-intent rows at the top so meta-skill work and explicit dream requests can short-circuit normal feature-state routing.
2. Keep new-feature intake rows above active-feature rows so clearly instant/debug/normal feature requests can bootstrap correctly.
3. Keep `invalid-epic-closure` (row 8) above `learnings-pending` and `completed` so a prematurely closed epic with open child tasks is caught before being treated as finished.
4. Keep `learnings-pending` above `completed` so closed epics route to compounding first.
5. Keep `phase-complete-needs-replan` above review and execution states so multi-phase advancement returns to planning deterministically.
6. Treat `exploring` as the fallback when the context and planning-artifact states do not match.
