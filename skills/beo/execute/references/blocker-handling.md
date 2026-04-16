# Blocker Handling

Protocol for handling blocked tasks during `beo-execute`.

## Step 1: Understand the Blocker

```bash
br show <TASK_ID> --json
br comments list <TASK_ID> --json
```

## Step 2: Classify and Act

| Blocker Type | Action |
|-------------|--------|
| Missing dependency output | Check if dependency completed; worker may need clearer input |
| External service unavailable | Report to user — cannot resolve automatically |
| Scope exceeds task boundary | Strip `approved` (`br label remove <EPIC_ID> -l approved`), route to `beo-plan` |
| Ambiguous requirement | Route to user for clarification |
| Technical issue (build/test failure) | Route to `beo-debug` if not resolvable in-context |

## Step 3: Ask User for Decision

Use the structured question tool to present the blocker and available options, such as: provide missing info, skip/cancel task, re-plan task, or unblock manually.

## Step 4: Resume

If the blocker is cleared without changing scope, update task status and resume through the normal execute flow.

If the user decision changes scope, requirements, or planning assumptions, stop executing and route through the canonical back-edge instead of rewriting the task inside execute.
