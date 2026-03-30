# Task Status Mapping

Beo uses richer task states than br's native model. This table maps each Beo state to the exact br CLI commands required.

## Beo States → br Commands

| Beo State | br Status | br Labels | Commands (in order) |
|---------------|-----------|-----------|-------------------|
| `pending` | `open` | (none) | `br update <id> -s open` then remove stale labels: `br label remove <id> -l blocked`, `br label remove <id> -l failed`, `br label remove <id> -l partial`, `br label remove <id> -l cancelled`, `br label remove <id> -l dispatch_prepared`, `br label remove <id> -l in_progress` |
| `dispatch_prepared` | `open` | `dispatch_prepared` | `br label add <id> -l dispatch_prepared` |
| `in_progress` | `in_progress` | `in_progress` | `br update <id> --claim` then `br label remove <id> -l dispatch_prepared` then `br label add <id> -l in_progress` |
| `done` | `closed` | (none) | `br label remove <id> -l in_progress` then `br close <id>` |
| `blocked` | `deferred` | `blocked` | `br label remove <id> -l in_progress` then `br update <id> -s deferred` then `br label add <id> -l blocked` |
| `failed` | `deferred` | `failed` | `br label remove <id> -l in_progress` then `br update <id> -s deferred` then `br label add <id> -l failed` |
| `partial` | `deferred` | `partial` | `br label remove <id> -l in_progress` then `br update <id> -s deferred` then `br label add <id> -l partial` |
| `cancelled` | `deferred` | `cancelled` | `br label remove <id> -l in_progress` then `br update <id> -s deferred` then `br label add <id> -l cancelled` |

## Allowed State Transitions

```
pending → dispatch_prepared → in_progress → done
                                          → blocked → pending (after unblock)
                                          → failed → pending (re-queue)
                                          → partial → cancelled → pending
```

**Forbidden transitions**:
- `done → in_progress` (NEVER reopen a completed task — create a new one)
- `done → pending` (same reason)
- Any skip of `dispatch_prepared` (always goes pending → dispatch_prepared → in_progress)

## Reading Beo State from br

To determine the Beo state from br output:

```
if status == "closed" → done
if status == "deferred":
  if has label "blocked" → blocked
  if has label "failed" → failed
  if has label "partial" → partial
  if has label "cancelled" → cancelled
if status == "in_progress" → in_progress
if status == "open":
  if has label "dispatch_prepared" → dispatch_prepared
  else → pending
```

## Feature States

| Feature State | br Epic Status | br Labels | How to Set |
|--------------|---------------|-----------|-----------|
| `planning` | `open` | (none) | Default after `br create -t epic` |
| `approved` | `open` | `approved` | `br label add <epic> -l approved` |
| `executing` | `in_progress` | `approved` | `br update <epic> --claim` |
| `completed` | `closed` | `approved` | `br close <epic>` |

## Stale Label Cleanup

Before setting a new state, always remove conflicting labels. The safe cleanup sequence:

```bash
# Before marking pending (removes all status labels)
br label remove <id> -l blocked
br label remove <id> -l failed
br label remove <id> -l partial
br label remove <id> -l cancelled
br label remove <id> -l dispatch_prepared
br label remove <id> -l in_progress

# Before marking in_progress (remove dispatch_prepared)
br label remove <id> -l dispatch_prepared

# Before marking done (remove in_progress)
br label remove <id> -l in_progress
```

Note: `br label remove` on a non-existent label is a no-op (safe to run unconditionally).
