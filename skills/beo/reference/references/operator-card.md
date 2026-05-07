# BEO Operator Card

## Startup rule

At session start:

1. Read `.beads/STATE.json` if present.
2. Read `.beads/HANDOFF.json` only if resuming paused or transferred work.
3. Read active feature artifacts only for the active `feature_slug`.
4. If no active feature exists and the user request names a feature goal, start through `beo-explore`.
5. Use `beo-route` only when owner identity or active feature identity is unsafe. If multiple active feature candidates exist, stop and ask the user which feature is active.

Startup output is advisory only. It cannot approve execution, select execution sets, emit review verdicts, or promote learning.

## Owner quick map

`beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`

Use repair paths in `pipeline.md` when validation, execution, or review discovers a blocker.

## AGENTS.md setup

Use `beo-setup` for all AGENTS.md managed-block setup, checks, and refreshes. Do not create or append the managed block outside `beo-setup`.

## Setup and usage helper

Use `beo-setup` only for project setup, AGENTS.md managed-block checks, setup health checks, and concise usage guidance.

`beo-setup` is not a runtime owner and is not part of the normal feature delivery path.

Normal feature delivery remains:

`beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`

`beo-setup` output is advisory only. It cannot approve execution, select execution sets, emit review verdicts, mutate feature artifacts, or promote learning.

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
