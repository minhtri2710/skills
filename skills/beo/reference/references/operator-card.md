# BEO Operator Card v2

## Startup rule

At session start:

1. Read `.beads/STATE.json` if present.
2. Read `.beads/HANDOFF.json` only if resuming paused or transferred work.
3. Read active feature artifacts only for the active `feature_slug`.
4. If no active feature exists, start through `beo-route` or `beo-explore`.
5. If multiple active feature candidates exist, stop and ask the user which feature is active.

Startup output is advisory only. It cannot approve execution, select execution sets, emit review verdicts, or promote learning.

## Owner quick map

`beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`

Use repair paths in `pipeline.md` when validation, execution, or review discovers a blocker.

## AGENTS.md setup

For a new BEO project, ensure `AGENTS.md` exists.

- If `AGENTS.md` is missing, create it from `assets/AGENTS.template.md`.
- If `AGENTS.md` exists but lacks the BEO managed block, append the managed block from `assets/AGENTS.template.md`.
- If `AGENTS.md` already contains the managed block, do not change it unless the user explicitly requests a refresh.
- If the managed block markers are duplicated or malformed, ask the user before editing.

This is setup-only. Its only writable surface is `AGENTS.md`.

## Standard decision packet

Every non-trivial owner output begins with:

```md
Decision:
Active owner:
Feature:
Evidence checked:
Changed surfaces:
Blocked by:
Next owner:
Next owner reason:
Authority note: display-only; canonical authority remains in the referenced state/artifact surface.
```

## Output compactness

Prefer concise operator output.

Do name the decision, evidence checked, changed surfaces, blocker if any, next owner, and reason.

Do not restate canonical doctrine, explain every possible branch, include unused templates, or include long checklists when all checks passed.

Use long cards only for route decisions, validation failure, execute preflight failure, debug return, review verdict, learning disposition, human gate, and stale approval.
