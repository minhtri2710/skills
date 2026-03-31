# Bead Creation Guide

Detailed rules, templates, and checklists for Phase 6 (Task Bead Creation) and Phase 7 (Plan Review) of `beo-planning`.

## Table of Contents

- [Story Context Block](#story-context-block)
- [Story-to-Bead Decomposition Rules](#story-to-bead-decomposition-rules)
- [Bead Completeness Check](#bead-completeness-check)
- [Plan Review Checklists](#plan-review-checklists)
- [Lightweight Mode](#lightweight-mode)
- [Promotion Flow](#promotion-flow)

---

## Story Context Block

Every bead description must include this block:

```markdown
## Story Context

Story: <Story Name>
Purpose: <what this story makes true>
Contributes To: <phase exit-state statement>
Unlocks: <what the next story or phase can now do>

## Planning Context

From plan.md: <specific approach decision that applies here>

## Institutional Learnings

From .beads/learnings/<file> or .beads/critical-patterns.md:
- <key gotcha or pattern>
```

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
- [ ] Story context block (Story, Purpose, Contributes To, Unlocks)
- [ ] File scope (which files to create/modify)
- [ ] Numbered implementation steps
- [ ] Verification criteria
- [ ] Enough context for a fresh worker who has never seen the plan

If any bead fails this check, fix it immediately via `br update <TASK_ID> --description`. A bead without a complete description is an invalid intermediate state — it must not survive to handoff.

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

## Lightweight Mode

For features classified as **lightweight** by the router (2-3 files, clear scope):

1. Skip Phase 1 parallel exploration — do a quick single-pass review of affected files
2. Write abbreviated plan.md (approach + tasks, skip discovery summary)
3. Create task beads directly
4. Still wire dependencies and validate the graph
5. Skip the formal review — present directly to user
6. Write abbreviated phase-contract.md (approach + exit state, skip phase diagram)
7. Write abbreviated story-map.md (single story, skip dependency diagram)

---

## Promotion Flow

When direct/instant tasks grow beyond their envelope:

### Step 1: Gather Existing Tasks

```bash
# List existing manual tasks (canonical enumeration — see pipeline-contracts.md)
br dep list <EPIC_ID> --direction up --type parent-child --json
```

### Step 2: Write Plan Around Them

Create plan.md that incorporates existing tasks as entries, plus any new tasks needed.

### Step 3: Create Missing Task Beads

Only create beads for tasks that don't already exist. Wire dependencies for all tasks (existing + new).

### Step 4: Proceed to Validation

Route to `beo-validating` — promoted plans need the same rigor as fresh plans.
