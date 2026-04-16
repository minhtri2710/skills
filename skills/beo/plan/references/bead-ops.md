# Bead Operations

Task bead creation, description writing, dependency wiring, review checklists, Quick Mode, and promotion flow.

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

Every bead description must use Markdown format with the shared templates from `beo-reference` → `references/bead-description-templates.md`. If no institutional learnings apply, write: "No prior learnings for this domain."

---

## Story-to-Bead Decomposition Rules

- One story → usually 1-3 beads
- A bead must not span multiple unrelated stories
- If a story needs 4+ substantial beads, the story may be too large
- Story order must remain visible after decomposition
- Story closure matters more than layer purity

---

## Bead Completeness Check

<HARD-GATE>
After all beads are created, read every bead back and verify. No bead may be handed off without passing this check.
</HARD-GATE>

For each task bead: `br show <TASK_ID> --json`

Verify `.description` contains:

- [ ] Non-empty Markdown description using the shared planned bead template
- [ ] Story context block (Story, Purpose, Contributes To, Unlocks)
- [ ] File scope (files to create/modify)
- [ ] Numbered implementation steps
- [ ] Verification criteria
- [ ] Enough context for a fresh worker who has never seen the plan
- [ ] Error contract for I/O beads (failure behavior)
- [ ] Secret handling requirements when decisions mention API keys/tokens
- [ ] Locked decision references (D-IDs) when `CONTEXT.md` has a Locked Decisions table

Fix immediately via `br update <TASK_ID> --description`. A bead without a complete description is an invalid state that must not survive to handoff.

---

## Plan Review Checklists

### Completeness

For each CONTEXT.md decision (D1, D2, ...):
- [ ] At least one task implements this decision
- [ ] Verification criteria traceable to the decision

### Decomposition Quality

For each task:
- [ ] Developer can start with only the task description + plan
- [ ] File scope clear (no overlapping files between independent tasks)
- [ ] Verification criteria concrete and testable
- [ ] Risk assessment honest

### Story Completeness

For each story in story-map.md:
- [ ] At least one bead maps to this story
- [ ] Bead set covers the story's "Done Looks Like" criteria
- [ ] No orphaned beads (every bead maps to exactly one story)

---

## Quick Mode

For features classified as **Quick** (see `beo-reference` → `references/pipeline-contracts.md` § Quick-Scope Definition):

1. Skip parallel exploration — do a quick single-pass review of affected files
2. Write abbreviated plan.md (approach + tasks, skip discovery summary)
3. Create task beads directly
4. Wire dependencies and validate the graph
5. Continue through the normal pipeline: validate → execute → review → compound
6. Write abbreviated phase-contract.md (approach + exit state)
7. Write abbreviated story-map.md (single story)

Quick mode reduces ceremony with smaller artifacts and faster cycles, but it does not skip validation or review.

---

## Promotion Flow

When instant-path tasks grow beyond their envelope:

1. **Gather existing tasks:** `br dep list <EPIC_ID> --direction up --type parent-child --json`
2. **Write plan around them:** Create plan.md incorporating existing tasks + any new tasks needed
3. **Create missing beads:** Only for tasks that don't already exist. Wire dependencies for all (existing + new)
4. **Proceed to validation:** Route to `beo-validate`. Promoted plans need the same rigor as fresh plans

---

## Task Bead Creation Operations

### Create task beads

```bash
br create "<Task Name>" -t task --parent <EPIC_ID> -p <priority> --json
```

| Priority | Use for |
|----------|---------|
| 0 | Spike / urgent proof task |
| 1 | Critical path |
| 2 | Standard delivery |
| 3 | Cleanup / nice-to-have |

### Write descriptions

Use the **Planned Task Bead Template** from `beo-reference` → `references/bead-description-templates.md`.

```bash
br update <TASK_ID> --description "<markdown task spec content>"
```

### Wire dependencies

```bash
# Task B depends on Task A (B is blocked by A)
br dep add <TASK_B_ID> <TASK_A_ID>
```

### Complete story-to-bead mapping

After bead creation, fill `Story-To-Bead Mapping` in `.beads/artifacts/<feature_slug>/story-map.md`.

### Validate the graph

```bash
br dep cycles --json        # Check for cycles
bv --robot-insights --format json  # Verify all tasks reachable
```

If cycles detected: identify cycle → find weakest edge → `br dep remove <child> <parent>` → re-validate.

### Run bead completeness check

Read each bead back and verify it passes the check above.

### Multi-phase scope rule

If multi-phase, verify every bead belongs to the current phase. If a bead belongs to a later phase: remove from current set, keep deferred in `phase-plan.md`. Do not smuggle future-phase work into the current phase.

## Epic Description Update

Use `beo-reference` → `references/artifact-conventions.md#slug-lifecycle` to preserve the canonical slug-first shape.

If the epic description includes a planning summary, update to reflect: planning mode, whether `phase-plan.md` exists, current phase number/name, total phase count. Keep concise — do not paste full artifact contents.
