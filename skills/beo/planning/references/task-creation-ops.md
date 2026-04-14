# Task Creation Operations

Operational reference for task bead creation, description writing, dependency wiring, and epic description updates.

## 11. Task Bead Creation Operations

### Create Task Beads

For each current-phase task in the plan:

```bash
br create "<Task Name>" -t task --parent <EPIC_ID> -p <priority> --json
```

Priority assignment:

- spike / urgent proof task: 0
- critical path: 1
- standard delivery: 2
- cleanup / nice-to-have: 3

### Write Task Descriptions

Use the shared **Planned Task Bead Template** from:

```text
../../reference/references/bead-description-templates.md
```

```bash
br update <TASK_ID> --description "<markdown task spec content>"
```

If no institutional learnings apply, include:

```text
No prior learnings for this domain.
```

### Wire Dependencies

For each dependency:

```bash
# Task B depends on Task A (B is blocked by A)
br dep add <TASK_B_ID> <TASK_A_ID>
```

### Complete Story-to-Bead Mapping

After bead creation, fill the `Story-To-Bead Mapping` section in:

```bash
# .beads/artifacts/<feature_slug>/story-map.md
```

### Validate the Graph

```bash
# Check for dependency cycles
br dep cycles --json

# Verify all tasks are reachable
bv --robot-insights --format json
```

If cycles are detected:

1. identify the cycle
2. determine the weakest edge
3. remove it with `br dep remove <child> <parent>`
4. re-validate

### Bead Completeness Check

After all beads are created, read each one back and verify it passes the checklist from `bead-creation-guide.md`.

### Scope rule for multi-phase work

If planning mode is `multi-phase`, verify that every bead belongs to the selected current phase.

If a bead belongs to a later phase:

- remove it from the current execution set
- keep that work deferred in `phase-plan.md`
- do not smuggle future-phase work into the current phase “just to save time”

## 12. Epic Description Update

Before updating the epic description, use:

```text
../../reference/references/artifact-conventions.md#slug-lifecycle
```

Preserve the canonical slug-first shape.

If the epic description includes a planning summary, update it to reflect:

- planning mode (`single-phase` or `multi-phase`)
- whether `phase-plan.md` exists
- current phase number / name, if known
- total phase count, if known

Keep the description concise. Do not paste full artifact contents into the epic bead.
