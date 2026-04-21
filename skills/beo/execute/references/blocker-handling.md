# Blocker Handling

Blocked-task protocol for `beo-execute`.

## 1. Inspect The Blocker

```bash
br show <TASK_ID> --json
br comments list <TASK_ID> --json --no-daemon
```

## 2. Classify It

| Blocker type | Action |
| --- | --- |
| Missing dependency output | Check whether the dependency actually finished; if yes, the worker likely needs clearer handoff input |
| External service unavailable | In `runtime-only`, return `blocked` through the runtime result channel. In `agent-mail`, send a blocker alert to the coordinator. Only direct user-facing `beo-execute` runs may route to user |
| Scope exceeds task boundary | Remove `approved` with `br label remove <EPIC_ID> -l approved`, then route to `beo-plan` |
| Ambiguous requirement | In `runtime-only`, return `blocked` upward for clarification. In `agent-mail`, send a blocker alert. Only direct user-facing `beo-execute` runs may route to user |
| Technical issue (build or test failure) | Route to `beo-debug` if it is not resolvable inside the current execution context |

## 3. Escalate Through The Right Surface

- Direct user-facing `beo-execute`: present the blocker and the available options through the runtime's user-interaction path
- `agent-mail` worker: report to the coordinator or launching parent and wait for reassignment, clarification, or stop
- `runtime-only` standalone worker: return `blocked` through the runtime result channel and stop

Do not ask the user directly from an Agent Mail worker. Do not wait silently in `runtime-only`.

## 4. Resume Or Backtrack

- If the blocker clears without changing scope, resume the normal execute flow.
- If the decision changes scope, requirements, or planning assumptions, stop execution and route through the canonical back-edge instead of rewriting the bead inside execute.
