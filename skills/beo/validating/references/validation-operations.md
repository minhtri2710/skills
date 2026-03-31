# Validation Operations

Detailed operational playbook for `beo-validating`. Load this file when you need exact prerequisite checks, graph-health commands, spike handling, approval messaging, or handoff details.

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Learnings Retrieval](#2-learnings-retrieval)
- [3. Structural Verification Flow](#3-structural-verification-flow)
- [4. Graph Health Operations](#4-graph-health-operations)
- [5. Spike Execution](#5-spike-execution)
- [6. Fresh-Eyes Review](#6-fresh-eyes-review)
- [7. Approval Gate](#7-approval-gate)
- [8. Handoff and Checkpointing](#8-handoff-and-checkpointing)

## 1. Prerequisites

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

Stop and route back to `beo-planning` if tasks, `phase-contract.md`, or `story-map.md` are missing.

## 2. Learnings Retrieval

Before validating structure, use `../../reference/references/learnings-read-protocol.md` as the canonical read-side workflow. If a prior learning affects phase closure, story order, or spike design, verify that the plan reflects it.

## 3. Structural Verification Flow

### Run the Plan Checker

Load `plan-checker-prompt.md`. Spawn an isolated subagent with:
- all task beads for the epic (`br show <TASK_ID> --json` for each)
- `CONTEXT.md`
- `discovery.md`
- `plan.md`
- `phase-contract.md`
- `story-map.md`

The checker returns a structured PASS/FAIL report for all 8 dimensions.

### Triage Results

- If all 8 dimensions PASS → proceed to graph health.
- If any dimension FAILS:
  1. fix the issue in the relevant artifact
  2. re-run the checker
  3. count that as the next iteration

### Repair Routing

| Failed Dimension | Fix In |
|-----------------|--------|
| Phase contract unclear | Revise `phase-contract.md` |
| Story order or scope unclear | Revise `story-map.md` |
| Decision/gap issue | Revise story map and/or bead descriptions |
| Dependency/scope/budget issue | Revise beads |
| Exit state not convincingly reachable | Revise contract, story map, or `plan.md` |

### Failure Handling

- **1-2 failures**: fix in place
- **3+ failures**: route back to `beo-planning`
- **After 3 iterations with any FAIL still present**: stop and escalate to the user

## 4. Graph Health Operations

Use `bv` to inspect graph health:

```bash
# Suggestions (missing deps, duplicates)
bv --robot-suggest --format json 2>/dev/null

# Graph health
bv --robot-insights --graph-root <EPIC_ID> --format json

# Priority alignment
bv --robot-priority --format json 2>/dev/null
```

### Interpret Results

| Finding | Action |
|---------|--------|
| Missing dependency suggested | Evaluate if genuine -> `br dep add <child-id> <depends-on-id>` |
| Duplicate beads detected | Merge or close the duplicate -> `br close <dup_id>` |
| Cycle detected | Break the weakest edge -> `br dep remove <child-id> <depends-on-id>` |
| Articulation point | Consider splitting the task |
| Priority misalignment | Adjust with `br update <id> -p <n>` |
| Critical path identified | Note it; do not delay these tasks |

### Deduplication Check

Manually review task titles and descriptions for overlap:
- same output → merge
- same files → sequence or merge
- near-identical descriptions → one may be unnecessary

### Story-to-Bead Coherence Check

Inspect `story-map.md` and verify:
- every story maps to at least one bead
- every bead belongs to a story
- stories with 4+ beads may be too large
- no bead spans unrelated stories

### Bead Description Verification

For each task bead under the epic, read `br show <TASK_ID> --json` and verify:
- `.description` is non-empty
- it uses the appropriate shared bead template
- it includes story context (if planned), file scope, implementation steps, and verification
- it provides enough context for a fresh worker

Fail validation if any bead is empty or underspecified.

## 5. Spike Execution

Use for HIGH-risk tasks when the approach is unproven, depends on external systems, has hard performance requirements, or otherwise relies on hope.

### Create the Spike

```bash
br create "Spike: <specific question to answer>" -t task --parent <EPIC_ID> -p 0 --json
```

The spike must:
1. ask a binary yes/no question
2. be time-boxed to 30 minutes
3. produce a concrete finding

### Record the Result

```bash
br close <SPIKE_ID>
br comments add <SPIKE_ID> --no-daemon --message "FINDING: YES|NO: <explanation>"
```

- YES → continue validation and embed the finding
- NO → full stop, route back to `beo-planning`

## 6. Fresh-Eyes Review

For deep-complexity features or features with 5+ tasks, load `bead-reviewer-prompt.md` and spawn an isolated subagent with:
- only the current bead descriptions
- no planning artifacts

If issues are found, fix bead descriptions before proceeding.

## 7. Approval Gate

### Present the Validation Summary

```text
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
  1. <name>: <story> | <risk> | <deps>
  2. <name>: <story> | <risk> | deps: [1]
  ...

Parallel tracks: <count based on dependency structure>
Critical path: <task chain>
Estimated complexity: <LOW/MEDIUM/HIGH>

Unresolved concerns: <none | list>

Approve execution? (yes/no)
```

### On Approval

Use the canonical approval rule from `../../reference/references/approval-gates.md`, then:

```bash
br label add <EPIC_ID> -l approved
br sync --flush-only
```

### On Rejection

```bash
br label remove <EPIC_ID> -l approved 2>/dev/null
```

Then route appropriately:
- `beo-planning` if the plan needs rework
- `beo-exploring` if decisions changed
- fix in place if the feedback is minor

## 8. Handoff and Checkpointing

### Lightweight Mode

For features with ≤2 low-risk tasks, no external deps, no schema changes, and no auth/security impact:
1. skip the full 8-dimension pass
2. skip graph analysis
3. skip spikes
4. skip fresh-eyes review
5. still require user approval

### Context-Budget Checkpoint

If context usage exceeds 65%:
1. save validation progress
2. save any spike results
3. write `HANDOFF.json`

Use the canonical base schema from `../../reference/references/state-and-handoff-protocol.md`, then add any validating-specific resume detail you need.

### Normal Handoff

After user approval, decide execution mode:

```bash
br ready --json
# Filter to tasks under this epic by cross-referencing br dep list <EPIC_ID> --direction up --type parent-child --json
```

- ≤2 independent tasks → `beo-executing`
- 3+ independent tasks → `beo-swarming`

Update `.beads/STATE.md` with validated task count and next skill.
