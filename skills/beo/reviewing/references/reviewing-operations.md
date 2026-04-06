# Reviewing Operations

Detailed operational playbook for `beo-reviewing`. Load this file when you need exact prerequisite checks, artifact-verification procedure, finishing commands, lightweight-review flow, or checkpoint mechanics.

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Automated Review Setup](#2-automated-review-setup)
- [3. Artifact Verification](#3-artifact-verification)
- [4. Human UAT](#4-human-uat)
- [5. Finishing Steps](#5-finishing-steps)
- [6. Lightweight Mode](#6-lightweight-mode)
- [7. Context-Budget Checkpoint](#7-context-budget-checkpoint)

## 1. Prerequisites

Verify before review:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
```

Read these artifacts with your file reading tool:

- `.beads/artifacts/<feature_slug>/CONTEXT.md` (required)
- `.beads/artifacts/<feature_slug>/plan.md` (required)
- `.beads/artifacts/<feature_slug>/approach.md` (optional but strongly recommended when it exists)
- `.beads/artifacts/<feature_slug>/phase-plan.md` (optional)
- `.beads/artifacts/<feature_slug>/phase-contract.md` (required)
- `.beads/artifacts/<feature_slug>/story-map.md` (required)

Also run project-specific build/tests before review.

Verify graph state matches conversation state — all executed beads must be `closed` in `br`, not just reported as done in conversation. If any bead that was implemented and verified is still open in `br`, close it before proceeding:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
# Check: every bead that was executed should have status "closed"
```

If tasks from the final execution scope are still open/in progress, route back to `beo-executing`.
If required current-scope artifacts such as `plan.md`, `phase-contract.md`, or `story-map.md` are missing, stop and route back to the planning-aware layer before continuing review.
If any tasks remain blocked/failed/partial, use the approval rules in `../../reference/references/approval-gates.md` before deciding whether to proceed, defer, or re-plan.
If `planning_mode = multi-phase` and later phases remain, remove the `approved` label first, then route back to `beo-planning` instead of reviewing the feature as complete:

```bash
br label remove <EPIC_ID> -l approved
```

## 2. Automated Review Setup

Use `review-specialist-prompts.md` for the specialist table, dispatch strategy, and P1/P2/P3 bead-creation patterns.

Prefer isolated review inputs:
- changed files or diff
- `CONTEXT.md`
- `plan.md`
- `approach.md` if it exists
- final current-phase artifacts (`phase-contract.md`, `story-map.md`, and `phase-plan.md` when present)

If multiple specialists produce the same finding, deduplicate before creating follow-up work.

## 3. Artifact Verification

For each significant artifact promised by the final execution scope, run the 3-level verification:
- L1 exists
- L2 substantive
- L3 wired

Suggested verification actions:

```text
- confirm the expected file or artifact exists
- inspect for placeholder markers such as TODO, FIXME, return null, or not implemented
- inspect imports/usages to confirm the artifact is actually wired into the feature path
```

Also verify each exit-state line from `phase-contract.md` against the actual implementation.

L2 or L3 failures are P1 findings and must be fixed before proceeding.

## 3b. Reactive Fix Bead Creation

When a P1 finding requires a fix, create a reactive fix bead under the current epic using both `--parent` and an explicit blocking dependency:

```bash
br create "Fix: <root cause summary>" -t task --parent <EPIC_ID> --deps blocks:<affected-bead-id>
```

This ensures the fix bead is:
1. Visible in epic task enumeration (via `--parent`)
2. Properly linked to the affected bead (via `--deps blocks:<affected-bead-id>`)

Write the bead description using the **Reactive Fix Bead Template** from `../../reference/references/bead-description-templates.md`.

Then route the fix bead through `beo-executing`. Do not implement fix code inside review.

## 4. Human UAT

Use the canonical human-review rule from `../../reference/references/approval-gates.md`.

For each locked decision:
1. state the decision
2. show how implementation fulfills it
3. ask whether it matches intent

Then do the same for each exit-state line.

### UAT Outcomes

- yes → mark verified and continue
- no → create P1 fix bead and route to executing
- close enough, fix later → create P2 follow-up bead using the shared follow-up template
- changed mind → update `CONTEXT.md`, assess impact, and route appropriately

## 5. Finishing Steps

After all P1 issues are resolved and UAT is complete:

1. run full build/test/lint
2. present the merge-path options to the user:
   - create PR
   - merge directly
   - keep branch for more work
   - discard branch
3. close the epic:

```bash
br close <EPIC_ID>
br comments add <EPIC_ID> --no-daemon --message "Feature complete. All tasks in the final execution scope closed. UAT passed."
br sync --flush-only
```

4. write `.beads/review-findings.md` for compounding
5. write a fresh `.beads/STATE.md` using `../../reference/references/state-and-handoff-protocol.md`; include `Next: beo-compounding` and planning-aware fields when known
6. optionally sync `AGENTS.md` changes with user approval
7. remove `.beads/HANDOFF.json` only after the fresh state write succeeds

## 6. Lightweight Mode

For ≤2 low-risk tasks with no external deps, schema changes, or auth/security impact:
- skip specialist subagents
- do a quick manual artifact check
- do a quick user confirmation
- run build/test/lint and close the epic

## 7. Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical `STATE.md` and `HANDOFF.json` shapes from `../../reference/references/state-and-handoff-protocol.md`, then include:
- current review phase
- gathered findings so far
- UAT progress
- any in-flight fix beads
- planning-aware fields when relevant (`planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`)
