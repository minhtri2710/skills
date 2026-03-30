---
name: beo-planning
description: Use after exploring completes. Research, synthesize, write plan.md, decompose into task beads with dependencies via br/bv CLI.
---

# Beo Planning

## Overview

Planning is the research-and-decompose phase. It takes CONTEXT.md from exploring and produces:
1. A `plan.md` document with the implementation approach
2. Task beads in the bead graph with dependencies wired
3. A risk classification for each task

**Core principle**: Plan once, execute many. Every minute spent planning saves 10 minutes of confused implementation.

## When to Use

- After `beo-exploring` completes (CONTEXT.md exists)
- User says "plan this", "create tasks", "decompose"
- Router detected state = **planning** (epic exists, no `approved` label, tasks may or may not exist)

## Prerequisites

Before starting, verify:

```bash
# CONTEXT.md must exist
cat .beads/artifacts/<feature-name>/CONTEXT.md

# Epic must exist
br show <EPIC_ID> --json

# Check for critical-patterns.md
cat .beads/critical-patterns.md 2>/dev/null
```

<HARD-GATE>
If CONTEXT.md does not exist, STOP. Route back to `beo-exploring`.
</HARD-GATE>

## Phase 0: Learnings Retrieval

**Mandatory.** Before any research, check institutional memory.

```bash
# Search knowledge store for relevant learnings
qmd query "<feature domain keywords>" --json 2>/dev/null || cat .beads/critical-patterns.md 2>/dev/null
```

If QMD is available, also run a semantic search:
```bash
qmd query "<feature description from CONTEXT.md>" --json 2>/dev/null
```

If any patterns are relevant to this feature's domain:
- Note them explicitly
- Embed them into the plan and affected task descriptions
- This prevents re-solving known problems

## Phase 1: Discovery

Goal-oriented research to understand the implementation landscape.

### Step 1: Identify Research Questions

From CONTEXT.md, extract:
- **Architecture questions**: "How is the existing code structured?"
- **Pattern questions**: "What patterns does this codebase use?"
- **Constraint questions**: "What limits or requirements exist?"
- **External questions**: "What do external APIs/libraries require?"

### Step 2: Parallel Exploration

Launch 2-4 parallel research subagents (using `task()` calls) focused on:

1. **Architecture Agent**: Explore codebase structure relevant to the feature
   - File organization, module boundaries, import patterns
   - Existing code that will be modified or extended
   
2. **Pattern Agent**: Identify patterns to follow
   - How similar features are implemented
   - Testing patterns, error handling conventions
   - Naming conventions, file placement rules

3. **Constraint Agent**: Discover hard limits
   - Type system constraints, API contracts
   - Performance requirements, compatibility needs
   - Dependencies and version constraints

4. **External Agent** (if needed): Research external dependencies
   - API documentation, SDK usage patterns
   - Known issues, migration guides
   - Community best practices

Each agent writes findings to a structured format. Collect all results.

### Step 3: Synthesize Findings

Combine research into a discovery summary:
- What exists today (architecture)
- What patterns to follow (conventions)
- What constraints apply (limits)
- What external factors matter (dependencies)

Write findings to the artifacts directory:

```bash
# Save discovery findings alongside CONTEXT.md
# Write to .beads/artifacts/<feature-name>/discovery.md
```

## Phase 2: Plan Writing

### Step 1: Draft the Approach

Based on CONTEXT.md decisions and discovery findings, write the implementation approach:

```markdown
# Plan: <feature-name>

## Approach
<High-level implementation strategy in 2-3 paragraphs>

## Discovery Summary
<Key findings from research phase>

## Risk Assessment
<Known risks and mitigations>
```

### Step 2: Decompose into Tasks

Break the approach into discrete, executable tasks. Each task must be:
- **One agent, one context window**: Completable by a single worker in one session
- **30-90 minutes of work**: Not too small (overhead), not too large (context exhaustion)
- **Clear boundaries**: Obvious when it starts and when it's done
- **Independently verifiable**: Has its own test/verification criteria

### Task Format in plan.md

```markdown
## Tasks

### 1. <Task Name>
**Files**: <list of files to create/modify>
**Dependencies**: none | [task numbers]
**Risk**: LOW | MEDIUM | HIGH
**Description**: <what to implement>
**Verification**: <how to verify it works>

### 2. <Task Name>
**Files**: <list of files>
**Dependencies**: [1]
**Risk**: LOW
**Description**: <what to implement>
**Verification**: <how to verify>
```

### Risk Classification

| Signal | Risk Level |
|--------|-----------|
| Following existing pattern, <3 files | **LOW** |
| New pattern or 3-5 files | **MEDIUM** |
| External dependency, >5 files, architectural change | **HIGH** |
| Unknown territory, no prior art in codebase | **HIGH** |

### Step 3: Write plan.md

Write the complete plan to the feature artifacts:

```bash
# Write to .beads/artifacts/<feature-name>/plan.md
```

Also write the plan to the epic bead description:

```bash
br update <EPIC_ID> --description "<plan content>"
```

## Phase 3: Task Bead Creation

Convert plan tasks into bead graph entries.

### Step 1: Create Task Beads

For each task in the plan:

```bash
# Create the task bead
br create "<Task Name>" -t task --parent <EPIC_ID> -p <priority> --json
```

Priority assignment:
- Critical path tasks: priority 1
- Standard tasks: priority 2-3
- Nice-to-have / cleanup: priority 4-5

### Step 2: Write Task Descriptions

For each task bead, write a complete description using the artifact protocol:

```bash
br update <TASK_ID> --description "<task spec content>"
```

The description (spec) must include:
- **Background**: What this task accomplishes and why
- **Files**: Exact file paths to create/modify
- **Steps**: Numbered implementation steps
- **Verification**: How to verify the task is complete
- **Rollback**: How to undo if something goes wrong (for HIGH risk tasks)

### Step 3: Wire Dependencies

For each task that depends on another:

```bash
# Task B depends on Task A (B is blocked by A)
br dep add <TASK_B_ID> <TASK_A_ID>
```

### Step 4: Validate the Graph

```bash
# Check for dependency cycles
br dep cycles --json

# Verify all tasks are reachable
bv --robot-insights --format json
```

If cycles are detected:
1. Identify the cycle
2. Determine which dependency is weakest (can be broken)
3. Remove it: `br dep remove <child> <parent>`
4. Re-validate

## Phase 4: Plan Review

Before marking the plan as approved, do a self-review.

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

### Present to User

Show the plan summary:
```
Plan: <feature-name>
Tasks: <count> (<HIGH risk>, <MEDIUM risk>, <LOW risk>)
Dependencies: <count> edges
Estimated parallel tracks: <count based on dependency structure>

[Task list with names, risk levels, and dependency chains]

Ready to validate? Load beo-validating for structural verification and approval.
```

## Lightweight Mode

For features classified as **lightweight** by the router (2-3 files, clear scope):

1. Skip Phase 1 parallel exploration — do a quick single-pass review of affected files
2. Write abbreviated plan.md (approach + tasks, skip discovery summary)
3. Create task beads directly
4. Still wire dependencies and validate the graph
5. Skip the formal review — present directly to user

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

## Context Budget

If context usage exceeds 65% during planning:

1. Write all findings so far to discovery.md
2. Write partial plan.md if any tasks are decomposed
3. Create any task beads that are ready
4. Write HANDOFF.json:
   ```json
   {
     "schema_version": 1,
     "phase": "planning",
     "skill": "beo-planning",
     "feature": "<epic-id>",
     "next_action": "Continue from Phase <N>, Step <M>",
      "in_flight_beads": [],
     "timestamp": "<iso8601>"
   }
   ```
5. Report progress and pause

## Handoff

After plan is written, tasks are created, and dependencies are wired:

Update state:
```bash
Write `.beads/STATE.md`:
```markdown
# Beo State
- Phase: planning → complete
- Feature: <epic-id> (<feature-name>)
- Tasks: <count> created
- Dependencies: <count> edges
- Next: beo-validating
```

Announce:
```
Planning complete.
- <N> tasks created with descriptions and verification criteria
- <M> dependency edges wired
- <K> HIGH-risk tasks identified

Ready for validation. Load beo-validating to verify plan quality and get approval.
```

## Red Flags

| Flag | Description |
|------|-------------|
| **Creating tasks without a plan** | Always write plan.md first (except in promotion flow) |
| **Tasks without verification criteria** | Every task must have concrete "how to verify" |
| **Overlapping file scopes** | If two independent tasks modify the same file, they must be sequenced |
| **Skipping dependency validation** | Always run `br dep cycles --json` after wiring |
| **Risk-inflating everything to HIGH** | Be honest — most tasks in a well-scoped feature are LOW or MEDIUM |
| **Tasks that are too granular** | "Add import statement" is not a task. Tasks should be 30-90 min of work |
| **Tasks that are too large** | "Implement the entire feature" is not a task. Break it down. |
| **Skipping learnings retrieval** | Phase 0 is mandatory, not optional |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Planning without CONTEXT.md | Assumptions will bite you | Route back to beo-exploring |
| One giant task per feature | No parallelism, no incremental progress | Decompose into 3-8 tasks |
| Dependencies everywhere | Over-constraining kills parallelism | Only add dependencies that are truly required |
| Copy-pasting CONTEXT.md into every task | Bloats descriptions, drifts | Reference the decision IDs (D1, D2) |
| Research without synthesis | Raw findings are not a plan | Always write the approach section |
