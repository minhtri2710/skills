# Validation Operations

Detailed operational playbook for `beo-validating`. Load this file when you need exact prerequisite checks, planning-aware orientation, graph-health commands, spike handling, approval messaging, or handoff details.

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Learnings Retrieval + Current-Phase Orientation](#2-learnings-retrieval--current-phase-orientation)
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
```

Read these artifacts with your file reading tool:

- `.beads/artifacts/<feature_slug>/CONTEXT.md` (required)
- `.beads/artifacts/<feature_slug>/discovery.md` (optional)
- `.beads/artifacts/<feature_slug>/approach.md` (required)
- `.beads/artifacts/<feature_slug>/plan.md` (required)
- `.beads/artifacts/<feature_slug>/phase-plan.md` (optional)
- `.beads/artifacts/<feature_slug>/phase-contract.md` (required)
- `.beads/artifacts/<feature_slug>/story-map.md` (required)

Stop and route back to `beo-planning` if tasks, `approach.md`, `phase-contract.md`, or `story-map.md` are missing.

Interpretation rules:

- if `phase-plan.md` exists, treat the feature as multi-phase unless current artifacts clearly contradict that model
- `phase-contract.md` and `story-map.md` always describe the **current phase**

## 2. Learnings Retrieval + Current-Phase Orientation

Before validating structure, use `../../reference/references/learnings-read-protocol.md` as the canonical read-side workflow.

If a prior learning affects phase closure, story order, spike design, or sequencing, verify that the current phase plan reflects it.

### Current-phase orientation

Before running the structural check, orient the validator.

Read, when available:

- `.beads/STATE.json`
- `approach.md`
- `phase-plan.md`
- `phase-contract.md`
- `story-map.md`

Summarize:

```text
Validating current phase: <phase number>/<total or unknown> - <phase name>
Planning mode: <single-phase | multi-phase>

Stories:
- Story 1: <name>
- Story 2: <name>
- Story 3: <name>

Goal of this phase:
- <one-line practical outcome>
```

If `phase-plan.md` exists, also verify:

- this current phase still makes sense in the larger sequence
- the selected current phase matches the plan summary and state metadata
- later phases remain intentionally deferred

## 3. Structural Verification Flow

### Run the Plan Checker

Load `plan-checker-prompt.md`. Spawn an isolated subagent with:
- all current-phase task beads for the epic (`br show <TASK_ID> --json` for each)
- `CONTEXT.md`
- `discovery.md` if it exists
- `approach.md`
- `plan.md`
- `phase-plan.md` if it exists
- `phase-contract.md`
- `story-map.md`
- dependency output for each task: `br dep list <TASK_ID> --direction down --type blocks --json`

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
| Decision/gap issue | Revise `approach.md`, story map, and/or bead descriptions |
| Dependency/scope/budget issue | Revise beads |
| Exit state not convincingly reachable | Revise `phase-contract.md`, `story-map.md`, `approach.md`, or `plan.md` |
| Current phase no longer fits the whole-feature sequence | Revise `phase-plan.md` and current-phase artifacts |

### Failure Handling

- **1-2 failures**: fix in place
- **3+ failures**: route back to `beo-planning`
- **After 3 iterations with any FAIL still present**: stop and escalate to the user

Do not attempt iteration 4.

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

If `phase-plan.md` exists, also verify:
- every bead belongs to the **current phase**
- no future-phase work is smuggled into the current execution set

### Bead Description Verification

For each task bead under the epic, read `br show <TASK_ID> --json` and verify:
- `.description` is non-empty
- it uses the appropriate shared bead template
- it includes story context (if planned), file scope, implementation steps, and verification
- it provides enough context for a fresh worker

Fail validation if any bead is empty or underspecified.

### Semantic Cross-Checks

Beyond structural completeness, verify that bead specs are semantically compatible with locked decisions:

1. **Interface compatibility**: For every trait, interface, or abstract type in bead specs, ask: "Does any locked decision require dynamic dispatch (`dyn Trait`, plugin system, registry)?" If yes, verify the design supports it.
2. **Secret handling**: For every decision mentioning API keys, tokens, secrets, or credentials, verify bead specs include file permission requirements, redaction in logs, and secure transport.
3. **Error contracts**: For every bead involving I/O (network, subprocess, filesystem), verify the spec states what happens on failure — propagated, logged, or shown to the user.
4. **Test plan adequacy**: For user-facing entry points, verify the test plan distinguishes unit tests from integration/end-to-end tests. New environment paths (clipboard, terminal multiplexer, etc.) require at least one end-to-end workflow test.

Semantic gaps are structural failures, not optional quality notes.

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
- no implementation history
- no broad conversation context

If issues are found, fix bead descriptions before proceeding.

## 7. Approval Gate

### Present the Validation Summary

```text
Validation Summary for: <feature-name>

Planning mode: <single-phase | multi-phase>
Current phase: <phase number>/<total or unknown> - <phase name>
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
Recommended next execution mode if approved: <beo-executing | beo-swarming>

Whole-feature note: <N/A for single-phase | later phases remain deferred in phase-plan.md>
Unresolved concerns: <none | list>

Approve execution for this current phase? (yes/no)
```

### On Approval

Use the canonical approval rule from `../../reference/references/approval-gates.md`, then:

```bash
br label add <EPIC_ID> -l approved
br sync --flush-only
```

Approval is not fully summarized until you also name the next execution mode for the approved current phase.
Do not stop at "approved for execution" without saying whether the next skill is `beo-executing` or `beo-swarming`.
If the next mode is not obvious, inspect the ready current-phase work immediately and resolve it before ending the approval summary.

### On Rejection

```bash
br label remove <EPIC_ID> -l approved 2>/dev/null
```

Then route appropriately:
- `beo-planning` if the plan needs rework
- `beo-exploring` if decisions changed
- fix in place if the feedback is minor

## 8. Handoff and Checkpointing

### Quick Mode

For Quick-scope features, see `../../reference/references/pipeline-contracts.md` for the canonical definition. When the feature qualifies as Quick:
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

When relevant, include planning-aware fields per `../../reference/references/state-and-handoff-protocol.md` § Planning-Aware HANDOFF.json Extension Fields, plus artifact completeness.

### Normal Handoff

After user approval, decide execution mode immediately:

```bash
br ready --json
# Filter to tasks under this epic by cross-referencing br dep list <EPIC_ID> --direction up --type parent-child --json
```

Decision rule:
- ≤2 independent ready tasks → `beo-executing`
- 3+ independent ready tasks → `beo-swarming`
- if the exact independent-track count is not available from the current context, inspect it now
- if it is still ambiguous after a reasonable inspection, default to `beo-executing` unless there is clear evidence that swarming is warranted

Your approval summary must end with a concrete `Next skill: beo-executing` or `Next skill: beo-swarming` statement. Without it, validation handoff is incomplete.

Update `.beads/STATE.json` with:
- validated task count
- planning mode
- current phase
- next skill

If `planning_mode = multi-phase`, note explicitly that later phases remain deferred until routed back through `beo-planning`.
