# Blocker Handling

Protocol for handling blocked tasks during `beo-execute`.

## Step 1: Understand the Blocker

```bash
br show <TASK_ID> --json
br comments list <TASK_ID> --json --no-daemon
```

## Step 2: Classify and Act

| Blocker Type | Action |
|-------------|--------|
| Missing dependency output | Check if dependency completed; worker may need clearer input |
| External service unavailable | In `runtime-only` standalone dispatch, return `blocked` through the runtime result channel. In `agent-mail` dispatch, send a blocker alert to the parent/coordinator thread. Only direct user-facing `beo-execute` runs should route to user — cannot resolve automatically |
| Scope exceeds task boundary | Strip `approved` (`br label remove <EPIC_ID> -l approved`), route to `beo-plan` |
| Ambiguous requirement | In `runtime-only` standalone dispatch, return `blocked` through the runtime result channel for parent/orchestrator clarification. In `agent-mail` dispatch, send a blocker alert to the parent/coordinator thread for clarification. Only direct user-facing `beo-execute` runs should route to user |
| Technical issue (build/test failure) | Route to `beo-debug` if not resolvable in-context |

## Step 3: Ask User or Return Blocker

If `beo-execute` is running with a direct user-facing channel, use the runtime's canonical user-interaction mechanism to present the blocker and available options, such as: provide missing info, skip/cancel task, re-plan task, or unblock manually.

If the current worker is using `agent-mail`, do not ask the user directly. Post the blocker to the coordinator / launching parent using the canonical blocker alert path, then wait for reassignment, clarification, or stop instructions.

If the current worker is `runtime-only` standalone dispatch, do not pause for direct user input. Return `blocked` through the runtime result channel and let the parent/orchestrator request the needed decision.

## Step 4: Resume

If the blocker is cleared without changing scope, update task status and resume through the normal execute flow.

If the user decision changes scope, requirements, or planning assumptions, stop executing and route through the canonical back-edge instead of rewriting the task inside execute.
