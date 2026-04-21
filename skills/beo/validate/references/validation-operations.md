# Validation Operations

Operational playbook for `beo-validate`.

`beo-validate` is a read-only quality gate for planning artifacts. It inspects, evaluates, and reports. It does not repair planning artifacts, edit dependency graphs, create or close spikes, rewrite bead descriptions, or otherwise mutate planned scope. Its only write actions are `approved` label management, stale `swarming` label cleanup, `HANDOFF.json`, and minimal `.beads/STATE.json` updates needed for handoff.

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

Run:

```bash
# Epic exists and has tasks
br show <EPIC_ID> --json
# Canonical task enumeration (see pipeline-contracts.md)
br dep list <EPIC_ID> --direction up --type parent-child --json
```

Read artifacts in this order:

1. `.beads/artifacts/<feature_slug>/CONTEXT.md` (required)
2. `.beads/artifacts/<feature_slug>/discovery.md` (optional)
3. `.beads/artifacts/<feature_slug>/approach.md` (required)
4. `.beads/artifacts/<feature_slug>/plan.md` (required)
5. `.beads/artifacts/<feature_slug>/phase-plan.md` (optional)
6. `.beads/artifacts/<feature_slug>/phase-contract.md` (required)
7. `.beads/artifacts/<feature_slug>/story-map.md` (required)

Stop and route back to `beo-plan` if tasks, `approach.md`, `phase-contract.md`, or `story-map.md` are missing.

Artifact interpretation rules:

- If `phase-plan.md` exists, treat the feature as multi-phase unless current artifacts prove the model stale or invalid.
- `phase-contract.md` and `story-map.md` always describe the **current phase**.

Before evaluating plan readiness, perform stale label cleanup:

1. If the epic has a `swarming` label but no `approved` label, remove `swarming` (`br label remove <EPIC_ID> -l swarming`). This is a transient state from interrupted swarm operations; the label is not needed for validation.

## 2. Learnings Retrieval + Current-Phase Orientation

Use `beo-reference` → `references/learnings-read-protocol.md` as the canonical read-side workflow.

If a prior learning affects phase closure, story order, spike design, or sequencing, verify that the current phase plan reflects it.

### Current-phase orientation

Read, when available, in this order:

1. `.beads/STATE.json`
2. `approach.md`
3. `phase-plan.md`
4. `phase-contract.md`
5. `story-map.md`

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

Load `plan-checker-prompt.md`. Run an isolated plan-check pass with the following package. Spawn a subagent only when the current runtime supports delegation for the session; otherwise perform the pass locally with the same isolated inputs:

1. all current-phase task beads for the epic (`br show <TASK_ID> --json` for each)
2. `CONTEXT.md`
3. `discovery.md` if it exists
4. `approach.md`
5. `plan.md`
6. `phase-plan.md` if it exists
7. `phase-contract.md`
8. `story-map.md`
9. dependency output for each task: `br dep list <TASK_ID> --direction down --type blocks --json`

The checker returns a structured PASS/FAIL report for all 8 dimensions.

### Triage Results

1. If all 8 dimensions PASS, proceed to graph health.
2. If any dimension FAILS:
   1. report the issue in the rejection output
   2. map the issue to the artifact or bead set `beo-plan` must update
   3. stop validation and route back to `beo-plan`

### Repair Routing

| Failed Dimension | Report For `beo-plan` To Fix |
|-----------------|-------------------------------|
| Phase contract unclear | Revise `phase-contract.md` |
| Story order or scope unclear | Revise `story-map.md` |
| Decision/gap issue | Revise `approach.md`, story map, and/or bead descriptions |
| Dependency/scope/budget issue | Revise beads and dependency declarations |
| Exit state not convincingly reachable | Revise `phase-contract.md`, `story-map.md`, `approach.md`, or `plan.md` |
| Current phase no longer fits the whole-feature sequence | Revise `phase-plan.md` and current-phase artifacts |

### Failure Handling

- **1+ failures**: produce a prioritized rejection report and route back to `beo-plan`
- **If decisions changed rather than planning structure**: route back to `beo-explore`
- **Repeated reject/replan loops with no convergence**: escalate to the user

The rejection report is the remediation plan. Order fixes so `beo-plan` can apply them deterministically.

## 4. Graph Health Operations

Run:

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
| Missing dependency suggested | Report dependency issue for `beo-plan` to evaluate and declare |
| Duplicate beads detected | Report duplication for `beo-plan` to merge, rewrite, or close |
| Cycle detected | Report the cycle and recommend the dependency edge `beo-plan` should reconsider |
| Articulation point | Recommend task splitting for `beo-plan` |
| Priority misalignment | Report priority concern for `beo-plan` to adjust |
| Critical path identified | Note it; do not delay these tasks |

### Deduplication Check

Review task titles and descriptions for overlap:

- same output → merge
- same files → sequence or merge
- near-identical descriptions → one may be unnecessary

### Story-to-Bead Coherence Check

Verify:

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

Verify that bead specs are semantically compatible with locked decisions:

1. **Interface compatibility**: For every trait, interface, or abstract type in bead specs, ask: "Does any locked decision require dynamic dispatch (`dyn Trait`, plugin system, registry)?" If yes, verify the design supports it.
2. **Secret handling**: For every decision mentioning API keys, tokens, secrets, or credentials, verify bead specs include file permission requirements, redaction in logs, and secure transport.
3. **Error contracts**: For every bead involving I/O (network, subprocess, filesystem), verify the spec states what happens on failure — propagated, logged, or shown to the user.
4. **Test plan adequacy**: For user-facing entry points, verify the test plan distinguishes unit tests from integration/end-to-end tests. New environment paths (clipboard, terminal multiplexer, etc.) require at least one end-to-end workflow test.

Semantic gaps are structural failures, not optional quality notes.

## 5. Spike Assessment

Use for HIGH-risk tasks when the approach is unproven, depends on external systems, has hard performance requirements, or otherwise relies on hope.

### Recommend the Spike

If a spike is needed, tell `beo-plan` to create it. The recommendation must specify that the spike:

1. ask a binary yes/no question
2. be time-boxed to 30 minutes
3. produce a concrete finding

### Record the Need

If prior spike results already exist, incorporate them into validation. If a required spike has not yet been created or resolved, reject validation and instruct `beo-plan` to add it before execution.

## 6. Fresh-Eyes Review

For deep-complexity features or features with 5+ tasks, load `bead-reviewer-prompt.md` and run a fresh-eyes pass with:

1. only the current bead descriptions
2. no implementation history
3. no broad conversation context

Spawn a subagent only when the current runtime supports delegation for the session; otherwise perform the same pass locally with the same isolated package.

If issues are found, flag the affected bead descriptions for `beo-plan` to rewrite before validation can pass.

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
Graph Health: <clean | N issues found>
Spikes: <N completed with findings | N recommended | N/A>
Fresh-Eyes: <PASS | N issues flagged | skipped>

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
Recommended next execution mode if approved: <beo-execute | beo-swarm>

Whole-feature note: <N/A for single-phase | later phases remain deferred in phase-plan.md>
Unresolved concerns: <none | list>

Approve execution for this current phase? (yes/no)
```

### On Approval

Use the canonical approval rule from `beo-reference` → `references/approval-gates.md`, then run:

```bash
br label add <EPIC_ID> -l approved
br sync --flush-only
```

Approval is incomplete until you name the next execution mode for the approved current phase: `beo-execute` or `beo-swarm`. If it is not obvious, inspect the ready current-phase work immediately and resolve it before ending the approval summary.

### On Rejection

```bash
br label remove <EPIC_ID> -l approved 2>/dev/null
```

Then route:

- `beo-plan` if the plan needs rework
- `beo-explore` if decisions changed
- do not fix in place during validation; the rejection report becomes the ordered remediation plan

## 8. Handoff and Checkpointing

### Quick Mode

For Quick-scope features, see `beo-reference` → `references/pipeline-contracts.md` for the canonical definition. When the feature qualifies as Quick, keep validation lightweight but preserve the binary gate: shorten supporting analysis as appropriate, do not create work during validation, and still require explicit user approval before any approval label is added.

### Context-Budget Checkpoint

If context usage exceeds 65%:

1. save validation progress
2. save any spike results
3. write `HANDOFF.json`

Use the canonical base schema from `beo-reference` → `references/state-and-handoff-protocol.md`, then add any validating-specific resume detail needed.

When relevant, include planning-aware fields from `beo-reference` → `references/state-and-handoff-protocol.md` § Planning-Aware HANDOFF.json Extension Fields, plus artifact completeness.

### Normal Handoff

After user approval, decide execution mode immediately:

```bash
br ready --json
# Filter to tasks under this epic by cross-referencing br dep list <EPIC_ID> --direction up --type parent-child --json
```

Decision rule:

- ≤2 independent ready tasks → `beo-execute`
- 3+ independent ready tasks → `beo-swarm`
- if the exact independent-track count is not available from the current context, inspect it now
- if it is still ambiguous after a reasonable inspection, default to `beo-execute` unless there is clear evidence that swarming is warranted

Your approval summary must end with a concrete `Next skill: beo-execute` or `Next skill: beo-swarm` statement. Without it, validation handoff is incomplete.

Update `.beads/STATE.json` with:

- current phase
- current skill/status for validation handoff
- next action / next skill

If `planning_mode = multi-phase`, note explicitly that later phases remain deferred until routed back through `beo-plan`.
