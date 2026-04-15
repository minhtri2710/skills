# Blocker Handling

Protocol for handling blocked tasks during `beo-executing`.

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
| Scope exceeds task boundary | Strip `approved` (`br label remove <EPIC_ID> -l approved`), route to `beo-planning` |
| Ambiguous requirement | Route to user for clarification |
| Technical issue (build/test failure) | Route to `beo-debugging` if not resolvable in-context |

## Step 3: Ask User for Decision

Present blocker with options: (1) provide missing info, (2) skip/cancel task, (3) re-plan task, (4) unblock manually.

## Step 4: Resume

```bash
br label remove <TASK_ID> -l blocked
br update <TASK_ID> -s open
br update <TASK_ID> --description "<updated spec with user's decision>"
```

Loop back to task selection.
