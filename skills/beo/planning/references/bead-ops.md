# Bead Operations

Operational reference for task bead creation, description writing, dependency wiring, review checklists, Quick Mode, and promotion flow.

## Table of Contents

- [Story Context Block](#story-context-block)
- [Story-to-Bead Decomposition Rules](#story-to-bead-decomposition-rules)
- [Bead Completeness Check](#bead-completeness-check)
- [Plan Review Checklists](#plan-review-checklists)
- [Quick Mode](#quick-mode)
- [Promotion Flow](#promotion-flow)
- [Task Bead Creation Operations](#task-bead-creation-operations)
- [Epic Description Update](#epic-description-update)

---

## Story Context Block

Every bead description must be written in Markdown format using the shared templates from `../../reference/references/bead-description-templates.md` and include the required sections.

If no institutional learnings apply, write: "No prior learnings for this domain."

---

## Story-to-Bead Decomposition Rules

- One story usually becomes 1-3 beads
- A bead should not span multiple unrelated stories
- If a story needs 4+ substantial beads, re-check whether the story is too large
- The story order should still be visible after decomposition
- Story closure matters more than layer purity

---

## Bead Completeness Check

<HARD-GATE>
After all beads are created, read every bead back and verify. No bead may be handed off without passing this check.
</HARD-GATE>

For each task bead under the epic:

```bash
br show <TASK_ID> --json
```

Verify that `.description` contains:

- [ ] Non-empty description
- [ ] Markdown-formatted description using the shared planned bead template
- [ ] Story context block (Story, Purpose, Contributes To, Unlocks)
- [ ] File scope (which files to create/modify)
- [ ] Numbered implementation steps
- [ ] Verification criteria
- [ ] Enough context for a fresh worker who has never seen the plan
- [ ] Error contract for I/O beads (what happens on failure?)
- [ ] Secret handling requirements when decisions mention API keys/tokens
- [ ] Locked decision references (D-IDs) are present when `CONTEXT.md` has a Locked Decisions table

If any bead fails this check, fix it immediately via `br update <TASK_ID> --description`. A bead without a complete description is an invalid intermediate state. It must not survive to handoff.

---

## Plan Review Checklists

Before marking the plan as approved, run these self-review checks.

### Completeness Check

For each CONTEXT.md decision (D1, D2, ...):
- [ ] Is there at least one task that implements this decision?
- [ ] Is the verification criteria traceable to the decision?

### Decomposition Quality Check

For each task:
- [ ] Could a developer start this task with only the task description + plan?
- [ ] Is the file scope clear (no overlapping files between independent tasks)?
- [ ] Are verification criteria concrete and testable?
- [ ] Is the risk assessment honest?

### Story Completeness Check

For each story in story-map.md:
- [ ] At least one bead maps to this story
- [ ] The bead set for this story covers the story's "Done Looks Like" criteria
- [ ] No bead is orphaned (every bead maps to exactly one story)

---

## Quick Mode

For features classified as **Quick**, see `../../reference/references/pipeline-contracts.md` for the canonical definition.

1. Skip the parallel exploration step. Do a quick single-pass review of affected files
2. Write abbreviated plan.md (approach + tasks, skip discovery summary)
3. Create task beads directly
4. Still wire dependencies and validate the graph
5. Skip the formal review. Present directly to user
6. Write abbreviated phase-contract.md (approach + exit state, skip phase diagram)
7. Write abbreviated story-map.md (single story, skip dependency diagram)

---

## Promotion Flow

When instant-path tasks grow beyond their envelope:

### Step 1: Gather Existing Tasks

```bash
# List existing manual tasks (canonical enumeration; see pipeline-contracts.md)
br dep list <EPIC_ID> --direction up --type parent-child --json
```

### Step 2: Write Plan Around Them

Create plan.md that incorporates existing tasks as entries, plus any new tasks needed.

### Step 3: Create Missing Task Beads

Only create beads for tasks that don't already exist. Wire dependencies for all tasks (existing + new).

### Step 4: Proceed to Validation

Route to `beo-validating`. Promoted plans need the same rigor as fresh plans.

---

## Task Bead Creation Operations

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

After all beads are created, read each one back and verify it passes the Bead Completeness Check section above.

### Scope rule for multi-phase work

If planning mode is `multi-phase`, verify that every bead belongs to the selected current phase.

If a bead belongs to a later phase:

- remove it from the current execution set
- keep that work deferred in `phase-plan.md`
- do not smuggle future-phase work into the current phase “just to save time”

## Epic Description Update

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
