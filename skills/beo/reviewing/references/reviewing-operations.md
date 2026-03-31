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
cat .beads/artifacts/<feature-name>/CONTEXT.md
cat .beads/artifacts/<feature-name>/phase-contract.md
cat .beads/artifacts/<feature-name>/story-map.md 2>/dev/null
```

Also run project-specific build/tests before review.

If tasks are still open/in progress, route back to `beo-executing`.
If any tasks remain blocked/failed/partial, use the approval rules in `../../reference/references/approval-gates.md` before deciding whether to proceed, defer, or re-plan.

## 2. Automated Review Setup

Use `review-specialist-prompts.md` for the specialist table, dispatch strategy, and P1/P2/P3 bead-creation patterns.

## 3. Artifact Verification

For each significant artifact promised by the plan, run the 3-level verification:
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
2. close the epic:

```bash
br close <EPIC_ID>
br comments add <EPIC_ID> --no-daemon --message "Feature complete. All tasks closed. UAT passed."
br sync --flush-only
```

3. write `.beads/review-findings.md` for compounding
4. optionally sync AGENTS.md changes with user approval
5. remove `.beads/HANDOFF.json` but keep `.beads/STATE.md`

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
