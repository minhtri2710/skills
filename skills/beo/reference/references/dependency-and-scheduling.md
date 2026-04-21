# Dependency Reconciliation

Reconcile planned task dependencies with actual bead dependency edges.

## Procedure

Build a map of `{ child_bead_id → [parent_bead_id, ...] }` from the plan's `dependsOn` fields.

For each task bead under the epic, run:

```bash
br dep list <bead-id> --direction down --type blocks --json
```

This returns the beads that `<bead-id>` depends on.

### 3. Compute Diff

```
edges_to_add = desired - actual
edges_to_remove = actual - desired
```

```bash
# Add missing edges
br dep add <child-id> <parent-id>    # child depends on parent

# Remove stale edges
br dep remove <child-id> <parent-id>
```

```bash
# Check for cycles (must be zero)
br dep cycles --json

# If cycles detected, remove the most recently added edge that created the cycle
```

## Epic Lookup

```bash
br list --type epic -a --json
```

## Listing Tasks Under an Epic

```bash
br dep list <epic-id> --direction up --type parent-child --json
```

## Scheduling Cascade

Select the next task to execute with this priority cascade:

### 1. `bv --robot-plan` (primary)

```bash
bv --robot-plan --graph-root <EPIC_ID> --format json
```

Returns parallel execution tracks. Pick the first unstarted bead from the first track with no in-progress beads. This preserves optimal parallelism.

### 2. `bv --robot-next` (fallback when plan data is unavailable)

```bash
bv --robot-next --format json
```

Returns a single recommendation with reasoning. Use it when robot-plan data is missing or stale, then post-filter the result to the active epic and current phase before acting.

### 3. `br ready` (fallback when `bv` is unavailable)

```bash
br ready --json
```

Returns all unblocked, open beads. Post-filter to beads under the active epic and current phase, then pick the highest-priority bead (lowest number). Break ties by creation order.

### 4. Manual Selection (Last resort)

If all CLI tools fail:

1. Run `br list --type task -s open --json` to get all open tasks.
2. For each task, run `br dep list <id> --direction down --type blocks --json` and skip the task if any dependency is not closed.
3. Pick the highest-priority unblocked task.
