---
name: beo-setup
description: |
  Use this skill to set up, check, or explain how to use the BEO workflow in a repository/project. Use when AGENTS.md setup, BEO managed startup text, project bootstrap orientation, workflow usage guidance, or lightweight setup health checking is requested. Do not use as a runtime owner for feature delivery, approval, execution, review, debugging, learning promotion, or product implementation.
---

# beo-setup

## Purpose

Set up, check, and explain BEO workflow usage without becoming a runtime owner.

## Fast predicate

Active when the user asks to:

- set up BEO workflow in a project;
- check whether BEO workflow setup is present or healthy;
- install or refresh the BEO managed block in `AGENTS.md`;
- understand how to use BEO workflow;
- get a quick operational map of BEO owners and artifacts;
- diagnose missing startup/setup surfaces before normal BEO operation.

Not active when:

- a feature is already in normal runtime flow and a valid owner can continue;
- implementation, planning, validation, execution, review, debug, or learning ownership is needed;
- approval, `PASS_EXECUTE`, execution-set selection, review verdict, or corpus learning promotion is requested.

## Primary owned decision

Decide whether BEO startup/setup is present and explain the correct next usage path.

## Writable surfaces

- `AGENTS.md` only for installing or refreshing the BEO managed startup block from `skills/beo/reference/assets/AGENTS.template.md`.
- Optional setup report in chat or owner output.

No other files are writable.

## Hard stops

Do not implement product changes.

Do not create, edit, or repair feature runtime artifacts:

- `.beads/STATE.json`
- `.beads/HANDOFF.json`
- `.beads/artifacts/<feature_slug>/CONTEXT.md`
- `.beads/artifacts/<feature_slug>/PLAN.md`
- `.beads/artifacts/<feature_slug>/approval-record.json`
- `.beads/artifacts/<feature_slug>/readiness-record.json`
- `.beads/artifacts/<feature_slug>/execution-bundle.json`
- `.beads/artifacts/<feature_slug>/REVIEW.md`
- `.beads/learnings/<feature_slug>.md`

Do not approve readiness.

Do not emit `PASS_EXECUTE`.

Do not create or refresh approval records.

Do not select execution sets.

Do not execute selected beads.

Do not emit review verdicts.

Do not debug root cause.

Do not promote learning.

Do not override a valid current runtime owner.

Do not treat setup status as authority for execution, approval, review, or closure.

If `AGENTS.md` managed markers are duplicated, malformed, or ambiguous, stop and ask the user before editing.

## Setup/check procedure

### 1. Read the BEO quick map

Read:

```text
skills/beo/reference/references/operator-card.md
```

Use it only as startup and usage guidance.

### 2. Check `AGENTS.md`

Inspect project root `AGENTS.md`.

Classify status as one of:

| Status | Meaning | Action |
| --- | --- | --- |
| `missing_agents` | `AGENTS.md` does not exist | Create it from the BEO managed template if the user requested setup/apply. |
| `missing_managed_block` | `AGENTS.md` exists but lacks `<!-- BEO:MANAGED START -->` and `<!-- BEO:MANAGED END -->` | Append the managed block if the user requested setup/apply. |
| `valid_managed_block` | exactly one valid BEO managed block exists | Do not edit. |
| `malformed_managed_block` | markers are duplicated, nested, missing one side, or ambiguous | Stop and ask the user before editing. |

Managed block source:

```text
skills/beo/reference/assets/AGENTS.template.md
```

### 3. Check existing BEO runtime orientation surfaces

Read-only check only:

```text
.beads/STATE.json
.beads/HANDOFF.json
.beads/artifacts/<feature_slug>/
```

Rules:

- Read `.beads/STATE.json` if present.
- Read `.beads/HANDOFF.json` only if resuming paused or transferred work.
- Read active feature artifacts only for the active `feature_slug`.
- If no `.beads` exists, report that no active BEO runtime state is present. Do not create `.beads`.
- If multiple active feature candidates appear and canonical state cannot select one, report that runtime owner selection needs `beo-route` or user selection.

### 4. Produce setup status

Output a concise setup card:

```md
Decision:
Setup status:
AGENTS.md status:
Runtime state status:
Active feature:
Current owner:
Issues found:
Changed surfaces:
Recommended next step:
Authority note:
```

Authority note must say:

```md
Setup output is advisory only. Runtime authority remains with canonical BEO state, artifacts, approval records, and the selected owner.
```

### 5. Suggest how to use BEO workflow

When the user asks how to use BEO, explain the shortest correct path:

```text
beo-setup -> beo-route only if owner/feature identity is unsafe
beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done
```

Use this explanation:

- `beo-explore`: lock requirements.
- `beo-plan`: turn locked requirements into executable bead scope.
- `beo-validate`: check readiness, approval freshness, and selected execution set.
- `beo-execute`: implement exactly the approved selected set.
- `beo-review`: independently accept, fix, or reject from evidence.
- `beo-compound`: record feature-level learning only when accepted review contains durable/unclear learning evidence.
- `beo-dream`: consolidate shared learning only when threshold evidence or explicit corpus request exists.
- `beo-debug`: prove one unproven blocker root cause.
- `beo-author`: edit BEO skill contracts/doctrine text.
- `beo-reference`: read canonical references only.

Keep usage guidance short and task-oriented.

## Setup modes

### Check-only mode

Use when the user asks:

- "check BEO setup"
- "is BEO installed?"
- "does this repo have BEO workflow?"
- "review setup"
- "show me how to use BEO"

Allowed:

- read setup surfaces;
- report missing or malformed setup;
- explain usage.

Not allowed:

- write files.

### Apply mode

Use when the user explicitly asks:

- "set up BEO"
- "install BEO startup"
- "add the AGENTS.md block"
- "fix missing BEO managed block"
- "refresh BEO setup"

Allowed:

- create `AGENTS.md` from the template when missing;
- append the managed block when missing;
- leave valid block unchanged.

Not allowed:

- edit malformed/duplicated blocks without user confirmation;
- create `.beads`;
- create feature artifacts;
- approve or execute anything.

## Allowed next owners

beo-route, beo-explore, beo-plan, beo-validate, beo-execute, beo-review, beo-debug, beo-compound, beo-dream, beo-author, beo-reference, user, done

## References

- `beo-reference -> references/operator-card.md`
- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/go-mode.md`
- `beo-reference -> references/human-gate.md`
- `beo-reference -> references/learning.md`
- `beo-reference -> assets/AGENTS.template.md`
