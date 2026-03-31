# Blocker Handling

Protocol for handling blocked tasks during `beo-executing`.

## Step 1: Understand the Blocker

```bash
# Read the task's blocker info
br show <TASK_ID> --json
br comments list <TASK_ID> --json
# Look for the blocker description in the latest report
```

## Step 2: Classify the Blocker

| Blocker Type | Action |
|-------------|--------|
| **Missing dependency output** | Check if the dependency task actually completed; if so, the worker may need clearer input |
| **External service unavailable** | Report to user, cannot resolve automatically |
| **Scope exceeds task boundary** | The task needs re-planning. Strip `approved` label (`br label remove <EPIC_ID> -l approved`) and route to `beo-planning` |
| **Ambiguous requirement** | Route to user for clarification |
| **Technical issue** (build failure, test failure) | Route to `beo-debugging` if not resolvable in-context |

## Step 3: Ask User for Decision

Present the blocker to the user with options:
1. Provide the missing information/decision
2. Skip the task (mark as cancelled)
3. Re-plan the task
4. Unblock manually

## Step 4: Resume

After the user provides a decision:

```bash
# Remove blocked label
br label remove <TASK_ID> -l blocked

# Reset to open
br update <TASK_ID> -s open

# Update description with the new information
br update <TASK_ID> --description "<updated spec with user's decision>"
```

Then loop back to Phase 1 to re-schedule.
