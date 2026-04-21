# Validation Operations

Operational playbook for `beo-validate`.

`beo-validate` is a read-only gate over current-phase planning quality. Its only writes are approval-label management, stale `swarming` cleanup, and canonical handoff state.

## 1. Prerequisites

Run:

```bash
br show <EPIC_ID> --json
br dep list <EPIC_ID> --direction up --type parent-child --json
```

Read artifacts in this order:
1. `CONTEXT.md`
2. `discovery.md` if present
3. `approach.md`
4. `plan.md`
5. `phase-plan.md` if present
6. `phase-contract.md`
7. `story-map.md`

If tasks, `approach.md`, `phase-contract.md`, or `story-map.md` are missing, stop and route to `beo-plan`.

Interpretation rules:
- `phase-plan.md` present → treat as multi-phase unless current artifacts prove it stale
- `phase-contract.md` and `story-map.md` always describe the current phase

Before validation, remove stale `swarming` only when the epic has `swarming` without `approved`:

```bash
br label remove <EPIC_ID> -l swarming
```

## 2. Learnings Retrieval + Current-Phase Orientation

Use `learnings-read-protocol.md` for read-side learnings behavior.

If a prior learning affects phase closure, story order, spike design, or sequencing, verify the current phase reflects it.

Read, when available, in this order:
1. `.beads/STATE.json`
2. `approach.md`
3. `phase-plan.md`
4. `phase-contract.md`
5. `story-map.md`

Summarize:
- current phase number and name
- planning mode
- current stories
- one-line phase goal

If `phase-plan.md` exists, verify the current phase still fits the larger sequence and later phases remain intentionally deferred.

## 3. Structural Verification Flow

### Run the Plan Checker

Load `plan-checker-prompt.md`. Run an isolated plan-check pass, locally or via delegation when the runtime supports it, over:
1. all current-phase task beads
2. `CONTEXT.md`
3. `discovery.md` if present
4. `approach.md`
5. `plan.md`
6. `phase-plan.md` if present
7. `phase-contract.md`
8. `story-map.md`
9. dependency output for each task: `br dep list <TASK_ID> --direction down --type blocks --json`

The checker returns PASS or FAIL across the 8 validation dimensions.

### Triage Results

- all PASS → continue to graph health
- any FAIL → produce an ordered remediation report and route to `beo-plan`
- if the failure is really a requirement change rather than a planning defect, route to `beo-explore`
- if reject/replan loops do not converge, escalate to the user

### Repair Routing

| Failed Dimension | Report For `beo-plan` To Fix |
|-----------------|-------------------------------|
| Phase contract unclear | revise `phase-contract.md` |
| Story order or scope unclear | revise `story-map.md` |
| Decision or gap issue | revise `approach.md`, `story-map.md`, and/or bead specs |
| Dependency, scope, or budget issue | revise beads and dependency declarations |
| Exit state not convincingly reachable | revise `phase-contract.md`, `story-map.md`, `approach.md`, or `plan.md` |
| Current phase no longer fits the whole-feature sequence | revise `phase-plan.md` and current-phase artifacts |

## 4. Graph Health Operations

Run:

```bash
bv --robot-suggest --format json 2>/dev/null
bv --robot-insights --graph-root <EPIC_ID> --format json
bv --robot-priority --format json 2>/dev/null
```

Interpret results:

| Finding | Action |
|---------|--------|
| Missing dependency suggested | report for `beo-plan` to evaluate and declare |
| Duplicate beads detected | report for `beo-plan` to merge, rewrite, or close |
| Cycle detected | report the cycle and the edge `beo-plan` should reconsider |
| Articulation point | recommend task splitting for `beo-plan` |
| Priority misalignment | report for `beo-plan` to adjust |
| Critical path identified | note it; do not delay these tasks |

Also verify:
- deduplication across titles and descriptions
- every story maps to at least one bead
- every bead belongs to a story
- no bead spans unrelated stories
- in multi-phase work, every bead belongs to the current phase only

### Bead Description Verification

For each task bead, read `br show <TASK_ID> --json` and verify:
- `.description` is non-empty
- it uses the appropriate shared bead template
- it includes file scope, implementation steps, and verification
- it includes story context unless it is a reactive fix bead

Any empty or underspecified bead is a validation failure.

### Semantic Cross-Checks

Verify bead specs against locked decisions:
1. interface compatibility with any required dynamic dispatch or registry model
2. secret handling for keys, tokens, credentials, and logs
3. error contracts for network, subprocess, and filesystem work
4. test adequacy, including at least one end-to-end workflow check for new environment paths

Semantic gaps are structural failures.

## 5. Spike Assessment

Recommend a spike only when the approach is unproven, depends on external systems, has hard performance limits, or otherwise relies on hope.

If needed, instruct `beo-plan` to create a spike that:
1. asks a binary yes/no question
2. is time-boxed to 30 minutes
3. produces a concrete finding

Do not create spikes during validation. If a required spike is missing or unresolved, reject validation and route back to `beo-plan`.

## 6. Fresh-Eyes Review

For deep-complexity features or features with 5+ tasks, load `bead-reviewer-prompt.md` and run a fresh-eyes pass over the current-phase bead set.

Use it to catch underspecified scopes, vague deliverables, missing tradeoffs, and story-boundary drift.

## 7. Approval Gate

Present a concise approval summary ending with a concrete next skill recommendation:
- `beo-execute` for ≤2 independent ready tasks
- `beo-swarm` for 3+ independent ready tasks
- if independence is still ambiguous after reasonable inspection, default to `beo-execute`

On approval:

```bash
br label add <EPIC_ID> -l approved
br sync --flush-only
```

On rejection:

```bash
br label remove <EPIC_ID> -l approved 2>/dev/null
```

Then route:
- `beo-plan` if the plan needs rework
- `beo-explore` if decisions changed

Validation never fixes in place.

## 8. Handoff and Checkpointing

### Quick Mode

For Quick-scope work, keep validation lightweight but preserve the binary gate: shorter analysis is acceptable, but explicit user approval is still required before adding `approved`.

### Context-Budget Checkpoint

If context usage exceeds 65%:
1. save validation progress
2. save any spike results
3. write `HANDOFF.json`

Use the canonical schema from `state-and-handoff-protocol.md`. Include planning-aware fields and artifact completeness when relevant.

### Normal Handoff

After approval, update `.beads/STATE.json` with:
- current phase
- validation handoff status
- concrete next skill

If `planning_mode = multi-phase`, state explicitly that later phases remain deferred until routed back through `beo-plan`.
