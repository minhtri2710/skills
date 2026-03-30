---
name: beo-validating
description: Use after planning completes and before execution begins. Verifies plan soundness, polishes beads with graph analytics, executes spikes for HIGH-risk items, and requires user approval. The gate between planning and coding.
---

# Beo Validating

## Overview

Validating is the critical gate between planning and execution. No code is written until this skill completes successfully.

**Core principle**: Catch plan failures before they become implementation failures.

This skill prevents:
- Executing broken plans that waste worker cycles
- Hitting unknown blockers mid-execution
- Redundant or duplicate work
- Structural graph problems (cycles, orphans, missing deps)

## When to Use

- After `beo-planning` completes (tasks exist in the bead graph)
- User says "validate", "check the plan", "ready to build"
- Router detected state = **ready-to-validate** (tasks exist, no `approved` label, plan.md exists)

## Prerequisites

Verify before starting:

```bash
# Epic exists and has tasks
br show <EPIC_ID> --json
# Canonical task enumeration (see pipeline-contracts.md)
br dep list <EPIC_ID> --direction up --type parent-child --json

# CONTEXT.md exists
cat .beads/artifacts/<feature-name>/CONTEXT.md

# plan.md exists
cat .beads/artifacts/<feature-name>/plan.md
```

<HARD-GATE>
If tasks don't exist in the bead graph, STOP. Route back to `beo-planning`.
</HARD-GATE>

## Phase 1: Structural Verification

Check the plan across 8 dimensions. For each dimension, assign PASS or FAIL.

### The 8 Dimensions

| # | Dimension | What to Check | FAIL if... |
|---|-----------|--------------|------------|
| 1 | **Requirement coverage** | Every CONTEXT.md decision (D1, D2...) maps to at least one task | Any decision has no corresponding task |
| 2 | **Dependency correctness** | Dependencies reflect actual implementation order | A task references files produced by a task it doesn't depend on |
| 3 | **File scope isolation** | Independent tasks don't modify the same files | Two tasks without a dependency edge share a file |
| 4 | **Context budget** | Each task is completable in one agent session | Any task description + plan context exceeds reasonable prompt limits |
| 5 | **Verification coverage** | Every task has concrete verification criteria | A task says "verify it works" without specifying how |
| 6 | **Gap detection** | No obvious implementation steps are missing | The plan has logical jumps (e.g., "create API" without "add route") |
| 7 | **Risk alignment** | HIGH-risk tasks have mitigations or spike flags | A HIGH-risk task has no rollback or mitigation plan |
| 8 | **Completeness** | All tasks together deliver the full feature | Completing all tasks would leave the feature partially done |

### Running the Check

For each dimension:
1. Read the relevant artifacts (CONTEXT.md, plan.md, task descriptions)
2. Cross-reference against the bead graph
3. Assign PASS or FAIL with a specific reason

### Handling Failures

- **1-2 failures**: Fix them in-place (update task descriptions, add missing dependencies). For missing tasks, route back to `beo-planning` — do not create implementation tasks during validation (spikes are the exception, see Phase 3).
- **3+ failures**: Route back to `beo-planning` for a rework pass
- **After 3 total validation attempts**: Escalate to the user with specific failures

## Phase 2: Graph Health

Use bv to analyze the bead graph for structural issues.

```bash
# Check for suggestions (missing deps, duplicates)
bv --robot-suggest --format json 2>/dev/null

# Check for graph health issues
bv --robot-insights --graph-root <EPIC_ID> --format json

# Verify priority alignment
bv --robot-priority --format json 2>/dev/null
```

### Interpret Results

| Finding | Action |
|---------|--------|
| **Missing dependency suggested** | Evaluate if genuine → `br dep add` |
| **Duplicate beads detected** | Merge or close the duplicate → `br close <dup_id>` |
| **Cycle detected** | Break the weakest edge → `br dep remove` |
| **Articulation point** (bottleneck) | Consider splitting the task or adding redundancy |
| **Priority misalignment** | Adjust → `br update <id> --priority <n>` |
| **Critical path identified** | Note it — these tasks must not be delayed |

### Deduplication Check

Manually review task titles and descriptions for overlap:
- Two tasks that produce the same output → merge
- Two tasks that modify the same files → sequence or merge
- Tasks with nearly identical descriptions → one is probably unnecessary

## Phase 3: Spike Execution (HIGH-Risk Only)

For each HIGH-risk task, evaluate whether a spike is needed.

**Spike criteria**: A spike is needed when:
- The approach is unproven (no prior art in the codebase)
- External dependencies are involved (API availability, SDK compatibility)
- Performance is a hard requirement (not just "should be fast")
- The risk mitigation in the plan is "hope it works"

### Running a Spike

```bash
# Create a spike bead (priority 0 = highest)
br create "Spike: <specific question to answer>" -t task --parent <EPIC_ID> -p 0 --json
```

The spike must:
1. Have a specific, binary question (YES/NO answer)
2. Be time-boxed to 30 minutes maximum
3. Produce a concrete finding

After the spike:

```bash
# Close the spike with the finding
br close <SPIKE_ID>
br comments add <SPIKE_ID> --no-daemon --message "FINDING: YES|NO — <explanation>"
```

### Spike Results

- **YES** (approach is viable) → Continue validation, embed finding in the task description
- **NO** (approach is not viable) → **FULL STOP** → Route back to `beo-planning` with the finding

<HARD-GATE>
A spike NO result means the plan is invalid. Do not proceed to approval.
</HARD-GATE>

## Phase 4: Fresh-Eyes Review (Optional)

For **deep** complexity features or features with 5+ tasks:

Launch a subagent with isolated context (no planning history) that reads only:
- The task beads (via `br show <id>` for each)
- CONTEXT.md

The subagent checks:
- Can each task be understood without the plan?
- Are descriptions self-contained enough for a worker?
- Are there implicit assumptions not captured in the bead?

If issues found → fix task descriptions before proceeding.

## Phase 5: Approval Gate

<HARD-GATE>
User approval is required before any code is written. This is non-negotiable.
</HARD-GATE>

### Present the Validation Summary

```
Validation Summary for: <feature-name>

Structural Check: <N>/8 PASS
Graph Health: <clean | N issues found and fixed>
Spikes: <N run, all YES | N/A>
Fresh-Eyes: <PASS | N issues fixed | skipped>

Tasks (<count>):
  1. <name> — <risk> — <deps>
  2. <name> — <risk> — deps: [1]
  ...

Parallel tracks: <count based on dependency structure>
Critical path: <task chain>
Estimated complexity: <LOW/MEDIUM/HIGH>

Approve execution? (yes/no)
```

### On Approval

```bash
# Mark the epic as approved
br label add <EPIC_ID> -l approved

# Flush to persist
br sync --flush-only
```

### On Rejection

Strip the `approved` label if it was set during a previous validation pass:
```bash
br label remove <EPIC_ID> -l approved 2>/dev/null
```

Ask what needs to change. Route to:
- `beo-planning` if the plan needs rework
- `beo-exploring` if decisions need to change
- Fix specific issues in-place if the feedback is minor

## Lightweight Mode

For features meeting ALL of these criteria:
- ≤2 tasks, all LOW risk
- No external dependencies
- No schema changes
- No auth/security impact

1. Skip Phase 1 formal 8-dimension check — do a quick sanity check instead
2. Skip Phase 2 bv graph analysis (too small to matter)
3. Skip Phase 3 spikes (LOW risk = no spikes needed)
4. Skip Phase 4 fresh-eyes review
5. Still require Phase 5 user approval (always)

Lightweight validation should take <2 minutes.

## Context Budget

If context usage exceeds 65%:

1. Save validation progress (which dimensions passed, which failed)
2. Save any spike results
3. Write HANDOFF.json:
   ```json
   {
     "schema_version": 1,
     "phase": "validating",
     "skill": "beo-validating",
     "feature": "<epic-id>",
     "feature_name": "<feature-name>",
     "next_action": "Continue from Phase <N>. Dimensions 1-5 PASS, 6-8 pending.",
     "in_flight_beads": ["<spike-ids-if-any>"],
     "timestamp": "<iso8601>"
   }
   ```
4. Pause

## Handoff

After user approves:

Determine execution mode:
```bash
# Count independent ready tasks (intersect with epic children)
br ready --json
# Filter results to only include tasks under this epic (cross-reference with br dep list <EPIC_ID> --direction up --type parent-child --json)
```

- **≤2 independent tasks** → single-worker mode → route to `beo-executing`
- **3+ independent tasks** → parallel mode → route to `beo-swarming`

Update state:
```markdown
# Beo State
- Phase: validating → approved
- Feature: <epic-id> (<feature-name>)
- Tasks: <count> validated
- Next: beo-executing (single-worker) or beo-swarming (parallel)

Approval: granted by user
```

Announce:
```
Plan approved. <N> tasks ready for execution.
Execution mode: <single-worker | parallel (swarming)>
Load <beo-executing | beo-swarming> to begin implementation.
```

## Red Flags

| Flag | Description |
|------|-------------|
| **Skipping validation entirely** | "The plan looks fine" is not validation |
| **Auto-approving without user** | Phase 5 is non-negotiable |
| **Ignoring spike NO results** | A failing spike means the plan is broken |
| **Fixing failures without re-checking** | After fixing, re-run the failed dimension check |
| **Validating without CONTEXT.md** | Decisions are the source of truth for requirement coverage |
| **Spending >1 hour on validation** | If it takes that long, the plan probably needs rework |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Rubber-stamping approval | Defeats the purpose of the gate | Every dimension gets a genuine check |
| Running spikes for LOW-risk tasks | Waste of time | Spikes are for HIGH-risk only |
| Fixing plan issues during validation | Scope creep | Note issues, route back to beo-planning if >2 failures |
| Adding implementation tasks during validation | That's planning work; only spikes are allowed | Route back to beo-planning for missing tasks |
| Skipping deduplication | Wastes worker time on redundant tasks | Always check for overlap |
