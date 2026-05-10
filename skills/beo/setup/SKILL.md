---
name: beo-setup
description: |
  Use this skill to set up, check, or explain how to use the BEO workflow in a repository/project. Use when AGENTS.md setup, BEO managed startup text, project bootstrap orientation, workflow usage guidance, or lightweight setup health checking is requested. Do not use as a runtime owner for feature delivery, approval, execution, review, debugging, learning recording/consolidation/authoring, or product implementation.
---

# beo-setup

## Purpose
Set up, check, and explain BEO workflow usage without becoming a runtime owner.

## Active when
User asks to set up BEO workflow, check whether setup is present, install/refresh the BEO managed block in `AGENTS.md`, understand BEO usage, or diagnose missing startup/setup surfaces before normal BEO operation.

## Owns
Decide whether BEO startup/setup is present and explain the correct next usage path.

## Reads
- `AGENTS.md` managed block presence
- `.beads/STATE.json` if present (display-only, STATE-01)
- `setup/references/setup-operations.md`
- `beo-reference -> references/operator-card.md`
- `beo-reference -> assets/AGENTS.template.md`

## Writes
- `AGENTS.md` only for installing or refreshing the BEO managed startup block from `skills/beo/reference/assets/AGENTS.template.md`
- Optional setup report in chat or owner output

## Must stop when
- feature runtime artifacts are requested (SETUP-01, SETUP-02)
- a valid current runtime owner exists and can continue
- `AGENTS.md` managed markers are duplicated, malformed, or ambiguous without user confirmation
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Setup output
Use only:

```md
Setup status:
- <missing_agents | missing_managed_block | valid_managed_block | malformed_managed_block | no_active_runtime | active_runtime_detected>

Setup action:
- <none | installed_managed_block | appended_managed_block | blocked_user_confirmation_needed>

Runtime recommendation:
- <advisory next step>

Authority:
- setup is advisory only; it does not create runtime authority, approval, execution evidence, review verdict, or learning record.
```

Avoid any `Next owner:` wording unless explicitly labeled advisory.

## Setup modes
**Check-only:** read surfaces, report status, explain usage. Not allowed: write files.
**Apply mode:** create `AGENTS.md` from template when missing, append managed block when missing, leave valid block unchanged. Not allowed: edit malformed/duplicated blocks without user confirmation, create `.beads` or feature artifacts.

## Exit map
| Condition | Next owner |
| --- | --- |
| setup complete, no runtime | done |
| user wants to start a feature | beo-explore (advisory) |
| setup/user decision needed | user |

## References
- `setup/references/setup-operations.md`
- `beo-reference -> references/operator-card.md`
- `beo-reference -> assets/AGENTS.template.md`
- `beo-reference -> references/skill-contract-common.md`
