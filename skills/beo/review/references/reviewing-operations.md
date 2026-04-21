# Reviewing Operations

Operational playbook for `beo-review`.

## 1. Prerequisites

Before review:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
```

Read:
- `CONTEXT.md`
- `plan.md` if present
- `approach.md` if present
- `phase-plan.md` if present
- `phase-contract.md`
- `story-map.md`

Also run project-specific build and tests before review.

Verify graph state matches execution state. Every executed bead must be `closed` in `br`, not merely reported done in conversation.

| State | Action |
| --- | --- |
| Open or in-progress tasks | route back to `beo-execute` |
| Accepted cancelled tasks | proceed; document accepted cancellations |
| Cancelled tasks without `cancelled_accepted` | route to `user` |
| Failed tasks | route back to debugging |
| Missing `phase-contract.md` or `story-map.md` | route to planning |
| Blocked or partial tasks | follow `approval-gates.md` |
| Multi-phase with later phases | follow `shared-hard-gates.md` |

## 2. Automated Review Setup

Use `review-specialist-prompts.md` for the canonical 5-specialist setup, dispatch strategy, and P1/P2/P3 follow-up patterns.

Prefer isolated inputs:
1. changed files or diff
2. `CONTEXT.md`
3. `plan.md`
4. `approach.md` if present
5. final current-phase artifacts: `phase-contract.md`, `story-map.md`, and `phase-plan.md` when present

Deduplicate repeated findings before creating follow-up work. P2 findings are non-blocking follow-up beads outside the current epic scope; only P1 blocks acceptance.

## 3. Artifact Verification

For each significant promised artifact, run 3-level verification:
1. exists
2. substantive
3. wired

Suggested checks:
- confirm the file or artifact exists
- inspect for placeholder markers such as `TODO`, `FIXME`, `return null`, or `not implemented`
- inspect imports or usages to confirm the artifact is wired into the real feature path

Also verify each exit-state line from `phase-contract.md` against implementation.

Any L2 or L3 failure is P1.

## 3b. Reactive Fix Routing

When a P1 finding requires a fix, specify the remediation target clearly in `review-findings.md` and use the reactive-fix contract from `pipeline-contracts.md`.

Review may identify the fix path, but it must not create or implement the fix directly.

## 4. Human UAT

Use `approval-gates.md` for the canonical human-review rule.

For each locked decision and exit-state line:
1. state it
2. show how implementation fulfills it
3. ask whether it matches intent

UAT outcomes:
- yes → mark verified and continue
- no → record a blocking remediation target and route through reactive-fix or replan flow
- close enough, fix later → record a non-blocking follow-up recommendation
- changed mind → update `CONTEXT.md`, assess impact, and route appropriately

## 5. Completion Handoff

After aggregation, write `review-findings.md` and emit exactly one verdict.

### `accept`

After all P1 issues are resolved and any required UAT is complete:
1. run full build, test, and lint
2. write review comments with severity labels and concrete fixes
3. write `.beads/artifacts/<feature_slug>/review-findings.md`
4. close the epic: `br close <EPIC_ID>`
5. write fresh `.beads/STATE.json` with `status: "learnings-pending"` and `next: "beo-compound"`
6. remove `.beads/HANDOFF.json` only after the fresh state write succeeds

### `fix`

1. run the review-specific verification needed to support the finding set
2. write review comments and `review-findings.md`
3. remove `approved` if the work is routing backward
4. write `.beads/STATE.json` for the canonical reactive-fix or backward path

Do not close the epic.

### `reject`

1. write review comments and `review-findings.md`
2. remove `approved`
3. write `.beads/STATE.json` for `beo-plan`

Do not close the epic.

## 6. Quick Mode

For Quick-scope work, skip specialist review dispatch. Do:
1. a quick manual artifact check
2. a quick user confirmation
3. build, test, and lint
4. normal compounding handoff if accepted

## 7. Context-Budget Checkpoint

If context usage exceeds 65%, write canonical `STATE.json` and `HANDOFF.json`, then include:
1. current review phase
2. gathered findings so far
3. UAT progress
4. any in-flight fix beads
5. planning-aware fields when relevant
