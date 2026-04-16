# Reviewing Operations

Operational playbook for `beo-review`.

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Automated Review Setup](#2-automated-review-setup)
- [3. Artifact Verification](#3-artifact-verification)
- [4. Human UAT](#4-human-uat)
- [5. Completion Handoff](#5-completion-handoff)
- [6. Quick Mode](#6-quick-mode)
- [7. Context-Budget Checkpoint](#7-context-budget-checkpoint)

## 1. Prerequisites

Before review:

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

Verify graph state matches conversation state. Every executed bead must be `closed` in `br`, not just reported done in conversation.

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
```

| State | Action |
| --- | --- |
| Open/in-progress tasks | Route back to `beo-execute` |
| Cancelled/failed tasks | Pause and present options: re-queue, accept, or re-plan |
| Missing required artifacts (`plan.md`, `phase-contract.md`, `story-map.md`) | Route to planning |
| Blocked/partial tasks | Use approval rules in `beo-reference` → `references/approval-gates.md` |
| Multi-phase | See `beo-reference` → `references/shared-hard-gates.md` § Multi-Phase Completion Routing |

## 2. Automated Review Setup

Use `review-specialist-prompts.md` for the canonical 5-specialist table, dispatch strategy, and P1/P2/P3 bead-creation patterns.

Prefer isolated review inputs:
1. changed files or diff
2. `CONTEXT.md`
3. `plan.md`
4. `approach.md` if it exists
5. final current-phase artifacts (`phase-contract.md`, `story-map.md`, and `phase-plan.md` when present)

If multiple specialists produce the same finding, deduplicate before creating follow-up work.
P2 findings become non-blocking follow-up beads outside the current epic scope; only P1 findings block acceptance.

## 3. Artifact Verification

For each significant artifact promised by the final execution scope, run 3-level verification:

1. L1 exists
2. L2 substantive
3. L3 wired

Suggested verification actions:

```text
- confirm the expected file or artifact exists
- inspect for placeholder markers such as TODO, FIXME, return null, or not implemented
- inspect imports/usages to confirm the artifact is actually wired into the feature path
```

Also verify each exit-state line from `phase-contract.md` against the actual implementation.

L2 or L3 failures are P1 findings and must be fixed before proceeding.

## 3b. Reactive Fix Routing

When a P1 finding requires a fix, specify the remediation target clearly in `review-findings.md` and use the canonical reactive-fix contract from `beo-reference` → `references/pipeline-contracts.md` to route the work.

Review may identify and describe the fix path, but it must not create or implement fix work directly inside the review phase.

## 4. Human UAT

Use the canonical human-review rule from `beo-reference` → `references/approval-gates.md`.

For each locked decision and each exit-state line:
1. state it
2. show how implementation fulfills it
3. ask whether it matches intent

### UAT Outcomes

- yes → mark verified and continue
- no → record a blocking remediation target and route through the canonical reactive-fix or replan path
- close enough, fix later → record a non-blocking follow-up recommendation using the shared follow-up template
- changed mind → update `CONTEXT.md`, assess impact, and route appropriately

## 5. Completion Handoff

After all P1 issues are resolved and UAT is complete:

1. run full build/test/lint
2. write review comments to the epic with severity labels and concrete fixes
3. write `.beads/artifacts/<feature_slug>/review-findings.md` for compounding
4. close the epic: `br close <EPIC_ID>`
5. write a fresh `.beads/STATE.json` using `beo-reference` → `references/state-and-handoff-protocol.md`; set `status: "learnings-pending"` and `next: "beo-compound"`; include planning-aware fields when known
6. remove `.beads/HANDOFF.json` only after the fresh state write succeeds

Close the epic before writing learnings-pending state. Compounding rejects an open epic.

## 6. Quick Mode

For Quick-scope work, see `beo-reference` → `references/pipeline-contracts.md` for the canonical definition. When the feature qualifies as Quick:
1. skip specialist subagents
2. do a quick manual artifact check
3. do a quick user confirmation
4. run build/test/lint and prepare the compounding handoff

## 7. Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical `STATE.json` and `HANDOFF.json` shapes from `beo-reference` → `references/state-and-handoff-protocol.md`, then include:
1. current review phase
2. gathered findings so far
3. UAT progress
4. any in-flight fix beads
5. planning-aware fields per `beo-reference` → `references/state-and-handoff-protocol.md` § Planning-Aware HANDOFF.json Extension Fields
