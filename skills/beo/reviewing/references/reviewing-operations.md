# Reviewing Operations

Detailed operational playbook for `beo-reviewing`. Load this file when you need exact prerequisite checks, artifact-verification procedure, finishing commands, Quick-review flow, or checkpoint mechanics.

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Automated Review Setup](#2-automated-review-setup)
- [3. Artifact Verification](#3-artifact-verification)
- [4. Human UAT](#4-human-uat)
- [5. Completion Handoff](#5-completion-handoff)
- [6. Quick Mode](#6-quick-mode)
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
If any tasks are `cancelled` or `failed`, these are terminal but non-success states. Pause and present the cancelled/failed tasks to the user with a request for direction (re-queue, accept, or re-plan) before proceeding with review.
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

When a P1 finding requires a fix, create a reactive fix bead under the current epic:

```bash
br create "Fix: <root cause summary>" -t task --parent <EPIC_ID> -p 1 --json
```

The fix bead is visible in epic task enumeration via `--parent`.
Reference the affected bead ID in the fix bead description (using the Reactive Fix Bead Template) for traceability.
Do not use `--deps blocks:<closed-bead>` — blocking an already-closed bead is a no-op and adds no scheduling value.

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

## 5. Completion Handoff

After all P1 issues are resolved and UAT is complete:

1. run full build/test/lint
2. write review comments to the epic with severity labels and concrete fixes
3. write `.beads/review-findings.md` for compounding
4. close the epic: `br close <EPIC_ID>`
5. write a fresh `.beads/STATE.json` using `../../reference/references/state-and-handoff-protocol.md`; set `status: "learnings-pending"` and `next: "beo-compounding"`; include planning-aware fields when known
6. remove `.beads/HANDOFF.json` only after the fresh state write succeeds

The epic must be closed (step 4) before writing learnings-pending state (step 5). Compounding's graph verification expects a closed epic and will reject an open one.

## 6. Quick Mode

For Quick-scope work, see `../../reference/references/pipeline-contracts.md` for the canonical definition. When the feature qualifies as Quick:
- skip specialist subagents
- do a quick manual artifact check
- do a quick user confirmation
- run build/test/lint and prepare the compounding handoff

## 7. Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical `STATE.json` and `HANDOFF.json` shapes from `../../reference/references/state-and-handoff-protocol.md`, then include:
- current review phase
- gathered findings so far
- UAT progress
- any in-flight fix beads
- planning-aware fields when relevant (`planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`)
