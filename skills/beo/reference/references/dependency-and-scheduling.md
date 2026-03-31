# Dependency Reconciliation

When a plan specifies task dependencies (e.g., "Task 3 depends on Task 1 and Task 2"), you must reconcile the desired dependency graph with the actual bead dependency edges.

## Table of Contents

- [Procedure](#procedure)
- [Example](#example)
- [Epic Lookup](#epic-lookup)
- [Listing Tasks Under an Epic](#listing-tasks-under-an-epic)
- [Scheduling Cascade](#scheduling-cascade)

## Procedure

### 1. Determine Desired Edges

From the plan, build a map of `{ child_bead_id → [parent_bead_id, ...] }` based on the `dependsOn` fields.

### 2. Read Actual Edges

For each task bead under the epic:

```bash
br dep list <bead-id> --direction down --type blocks --json
```

This returns the beads that `<bead-id>` depends on (waits for).

### 3. Compute Diff

```
edges_to_add = desired - actual
edges_to_remove = actual - desired
```

### 4. Apply Changes

```bash
# Add missing edges
br dep add <child-id> <parent-id>    # child depends on parent

# Remove stale edges
br dep remove <child-id> <parent-id>
```

### 5. Validate

```bash
# Check for cycles (must be zero)
br dep cycles --json

# If cycles detected, remove the most recently added edge that created the cycle
```

## Example

Given a plan with:
- Task A (no dependencies)
- Task B depends on A
- Task C depends on A and B

```bash
# After creating all three task beads:
br dep add <B-id> <A-id>    # B depends on A
br dep add <C-id> <A-id>    # C depends on A
br dep add <C-id> <B-id>    # C depends on B

# Verify no cycles
br dep cycles --json
# Expected: { "cycles": [] }
```

## Epic Lookup

To find the epic bead for a feature by name:

```bash
# List all epics (including closed)
br list --type epic -a --json

# Parse JSON output and match by title
# The title field matches the feature name passed to `br create -t epic`
```

## Listing Tasks Under an Epic

```bash
# List children of the epic
br dep list <epic-id> --direction up --type parent-child --json
```

# Scheduling Cascade

When selecting the next task to execute, follow this priority cascade:

## 1. bv --robot-plan (Primary)

```bash
bv --robot-plan --format json
```

Returns parallel execution tracks. Pick the first unstarted bead from the first track that has no in-progress beads. This gives optimal parallelism.

## 2. bv --robot-next (Fallback if plan unavailable)

```bash
bv --robot-next --format json
```

Returns a single recommendation with reasoning. Use when robot-plan data is missing or stale.

## 3. br ready (Fallback if bv unavailable)

```bash
br ready --json
```

Returns all unblocked, open beads. Pick the one with highest priority (lowest number). Break ties by creation order.

## 4. Manual Selection (Last resort)

If all CLI tools fail:
1. `br list --type task -s open --json` — get all open tasks
2. For each, check `br dep list <id> --direction down --type blocks --json` — skip if any dependency is not closed
3. Pick the highest priority unblocked task
