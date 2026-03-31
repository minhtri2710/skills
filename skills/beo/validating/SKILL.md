---
name: beo-validating
description: >-
  Use after planning completes and before execution begins. Verifies the phase
  contract, story map, and bead graph across 8 structural dimensions, executes
  spikes for HIGH-risk items, polishes beads with bv graph analytics, and
  requires user approval. The gate between planning and coding.
---

# Beo Validating

## Overview

Validating is the critical gate between planning and execution. No code is written until this skill completes successfully.

**Core principle**: Catch plan failures before they become implementation failures.

This skill treats a phase as a **small closed loop**:

- clear entry state
- clear exit state
- simple demo story
- stories that explain why the internal order makes sense
- beads that implement those stories

It is not enough for the bead graph to look tidy. The validator must answer:

- Does this phase close a meaningful loop?
- If all stories finish, will the exit state be true?
- If all beads finish, will the stories actually be complete?
- If the phase fails, will we know whether to debug locally or pivot the larger plan?

This skill prevents:
- Executing broken plans that waste worker cycles
- Hitting unknown blockers mid-execution
- Redundant or duplicate work
- Structural graph problems (cycles, orphans, missing deps)

## When to Use

- After `beo-planning` completes (tasks exist in the bead graph)
- User says "validate", "check the plan", "ready to build"
- Router detected state = **ready-to-validate** (tasks exist, no `approved` label, phase-contract.md AND story-map.md exist)

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

# phase-contract.md exists
cat .beads/artifacts/<feature-name>/phase-contract.md

# story-map.md exists
cat .beads/artifacts/<feature-name>/story-map.md
```

<HARD-GATE>
If tasks don't exist in the bead graph, STOP. Route back to `beo-planning`.
If phase-contract.md is missing, STOP. Route back to `beo-planning`.
If story-map.md is missing, STOP. Route back to `beo-planning`.
</HARD-GATE>

## Phase 0: Learnings Retrieval

Before validating structure, check institutional memory for relevant failure patterns.

- Read `.beads/critical-patterns.md` if present
- Search `.beads/learnings/` for domain-relevant prior learnings (if QMD is available, use it as an optional enhancement for semantic search)
- If a prior learning affects phase closure, story order, or spike design, verify that the plan reflects it

## Phase 1: Structural Verification

Check the plan across 8 dimensions. For each dimension, assign PASS or FAIL.

### The 8 Dimensions

| # | Dimension | What to Check | FAIL if... |
|---|-----------|--------------|------------|
| 1 | **Phase contract clarity** | phase-contract.md has clear entry state, exit state, demo story, unlocks, scope | Exit state is vague or aspirational, demo does not prove the phase, phase sounds like a work bucket |
| 2 | **Story coverage and ordering** | story-map.md stories have purpose, why-now, contributes-to, unlocks, done-looks-like | A story cannot answer "what does this unlock?", order feels arbitrary, a needed story is missing |
| 3 | **Decision coverage** | Every CONTEXT.md decision (D1, D2...) maps to at least one story and bead | A locked decision appears nowhere in the story map, or a story mentions it but no bead implements it |
| 4 | **Dependency correctness** | Story order and bead dependencies agree, graph is acyclic | Story order says one thing but bead dependencies say another, cycles exist, implicit undeclared dependencies |
| 5 | **File scope isolation** | Parallel-ready beads don't silently collide | Two ready beads write the same file, config/schema files have no explicit owner |
| 6 | **Context budget** | Each bead fits in one worker context window | A bead spans multiple stories, requires reading too many large files, tries to implement an entire subsystem |
| 7 | **Verification completeness** | Stories and beads both have explicit done/verify criteria | Story "done" is vague, bead verify steps are not runnable, story completion depends on subjective judgment |
| 8 | **Exit-state completeness and risk alignment** | If all beads complete, the phase reaches its exit state; HIGH-risk items have spike paths | Bead graph could finish while phase is not demoable, exit state depends on missing work, HIGH-risk items lack spikes |

### Running the Check

#### Step 1.1: Spawn Plan-Checker

Load `references/plan-checker-prompt.md`. Spawn an isolated subagent with:

- all task beads for this epic (via `br show <TASK_ID> --json` for each)
- `.beads/artifacts/<feature-name>/CONTEXT.md`
- `.beads/artifacts/<feature-name>/discovery.md`
- `.beads/artifacts/<feature-name>/plan.md`
- `.beads/artifacts/<feature-name>/phase-contract.md`
- `.beads/artifacts/<feature-name>/story-map.md`

The plan-checker produces a structured PASS/FAIL report for all 8 dimensions.

#### Step 1.2: Triage Results

**If all 8 dimensions PASS:** proceed to Phase 2.

**If any dimension FAILS:**

1. Fix the specific issue in the relevant artifact
2. Re-run the checker
3. Count that as the next iteration

### Repair Routing

| Failed Dimension | Fix In |
|-----------------|--------|
| Phase contract unclear | Revise `phase-contract.md` |
| Story order or scope unclear | Revise `story-map.md` |
| Decision/gap issue | Revise story map and/or bead descriptions |
| Dependency/scope/budget issue | Revise beads |
| Exit state not convincingly reachable | Revise contract, story map, or plan.md |

### Handling Failures

- **1-2 failures**: Fix them in-place (update task descriptions, add missing dependencies). For missing tasks, route back to `beo-planning` — do not create implementation tasks during validation (spikes are the exception, see Phase 3).
- **3+ failures**: Route back to `beo-planning` for a rework pass
- **After 3 iterations with any FAIL still present**: Stop, escalate to the user, explain which dimension is still failing and why. Do not attempt iteration 4.

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

### Story-to-Bead Coherence Check

Before leaving Phase 2, inspect `.beads/artifacts/<feature-name>/story-map.md`:

- every story should map to at least one bead
- every bead should belong to a story
- if a story has too many beads (4+), it may be too large
- if a bead spans multiple unrelated stories, the decomposition is muddy

### Bead Description Verification

For each task bead under the epic, read `br show <TASK_ID> --json` and verify:

- `.description` is non-empty
- Description contains: story context block, file scope, implementation steps, verification criteria
- Description provides enough context for a fresh worker

<HARD-GATE>
FAIL the plan if any bead has an empty or underspecified description. This is a structural verification failure, not an optional quality note. Route back to `beo-planning` to complete the bead specs.
</HARD-GATE>

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

Load `references/bead-reviewer-prompt.md`. Spawn an isolated subagent with:

- ONLY the current bead descriptions (`br show <TASK_ID> --json` for each)
- NO planning artifacts — the reviewer must be truly isolated

The reviewer checks that each bead is understandable in isolation and contains enough context for a fresh worker.

After the reviewer returns its report, the orchestrator (not the reviewer) cross-references findings against `phase-contract.md` and `story-map.md` to determine if flagged beads are missing story context or traceability.

If issues found → fix task descriptions before proceeding.

## Phase 5: Exit-State Readiness Review

This is the human-readable readiness check before approval.

Ask these questions explicitly:

1. If all stories reach "Done Looks Like", does the phase exit state hold?
2. If all beads close successfully, will all stories actually be done?
3. Is the phase demo story now credible?
4. Does this phase still make sense in the larger whole plan?

If any answer is "no" or "not sure", do not approve execution. Route back:

| Problem | Route To |
|---------|----------|
| Phase meaning / exit state problem | Revise `phase-contract.md` |
| Story decomposition problem | Revise `story-map.md` |
| Implementation granularity problem | Revise bead descriptions |
| Architecture / risk problem | Revise `plan.md` and possibly route to `beo-planning` |

## Phase 6: Approval Gate

<HARD-GATE>
User approval is required before any code is written. This is non-negotiable.
</HARD-GATE>

### Present the Validation Summary

```
Validation Summary for: <feature-name>

Phase: <phase name from phase-contract.md>
Stories: <N>
Beads: <N>
Demo story: <one-line from phase-contract.md>

Structural Check: <N>/8 PASS (after <N> iterations)
Graph Health: <clean | N issues found and fixed>
Spikes: <N run, all YES | N/A>
Fresh-Eyes: <PASS | N issues fixed | skipped>

Exit-State Readiness:
- Entry state understood: YES
- Exit state observable: YES
- Story sequence coherent: YES
- Demo credible: YES

Bead Descriptions: all <N> verified non-empty with story context

Tasks (<count>):
  1. <name> — <story> — <risk> — <deps>
  2. <name> — <story> — <risk> — deps: [1]
  ...

Parallel tracks: <count based on dependency structure>
Critical path: <task chain>
Estimated complexity: <LOW/MEDIUM/HIGH>

Unresolved concerns: <none | list>

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
5. Still require Phase 6 user approval (always)

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
| **Auto-approving without user** | Phase 6 is non-negotiable |
| **Ignoring spike NO results** | A failing spike means the plan is broken |
| **Fixing failures without re-checking** | After fixing, re-run the failed dimension check |
| **Validating without CONTEXT.md** | Decisions are the source of truth for requirement coverage |
| **Spending >1 hour on validation** | If it takes that long, the plan probably needs rework |
| **Validating a bead set that has no phase contract** | Phase contract defines the closed loop |
| **Validating a story map that cannot explain "why now" for Story 1** | Story 1 must have an obvious reason to exist first |
| **A phase exit state that is not observable** | "Improve quality" is not an exit state |
| **A bead's "done" does not connect to any story** | Every bead must trace to a story |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Rubber-stamping approval | Defeats the purpose of the gate | Every dimension gets a genuine check |
| Running spikes for LOW-risk tasks | Waste of time | Spikes are for HIGH-risk only |
| Fixing plan issues during validation | Scope creep | Note issues, route back to beo-planning if >2 failures |
| Adding implementation tasks during validation | That's planning work; only spikes are allowed | Route back to beo-planning for missing tasks |
| Skipping deduplication | Wastes worker time on redundant tasks | Always check for overlap |
| Approving when bead descriptions are empty | Workers will freelance with no spec | FAIL and route back to planning |
