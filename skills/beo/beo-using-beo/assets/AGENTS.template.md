<!-- BEO:START -->
## Beo Startup Rules

1. Read this file at session start and again after any context compaction.
2. Check `.beads/onboarding.json` exists and is current. If it is missing or stale, stop and load `beo-using-beo`.
3. If `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` as the first quick scout step.
4. If `.beads/HANDOFF.json` exists, do not auto-resume from it; present the saved state to the user first.
5. Read `.beads/critical-patterns.md` before planning or execution.

## Beo Skill Chain

Bootstrap gate: `beo-using-beo` runs first when onboarding is missing or stale.

```text
beo-router -> beo-exploring -> beo-planning -> beo-validating ->
beo-swarming -> beo-executing -> beo-reviewing -> beo-compounding
```

Support skills: `beo-debugging`, `beo-dream`, `beo-writing-skills`

## Critical Rules

- Never execute without passing validation.
- `CONTEXT.md` is the source of truth for locked decisions.
- 65% context usage triggers a `HANDOFF.json` checkpoint and a clean pause.
- Keep `STATE.md` current with the active phase and next action.
- After context compaction, re-read `AGENTS.md`, rerun `node .beads/beo_status.mjs --json` if available, then reopen `STATE.md`, `HANDOFF.json` if present, and the active feature artifacts before more work.
- P1 review findings block merge or feature completion.
- Never disturb concurrent work from other agents; work around existing edits unless the user explicitly tells you otherwise.

## Working Files

- `.beads/onboarding.json` - onboarding state and managed asset version
- `.beads/beo_status.mjs` - read-only scout command for onboarding, state, and handoff summary
- `.beads/STATE.md` - current phase and feature narrative
- `.beads/HANDOFF.json` - optional resume checkpoint when a session must pause
- `.beads/artifacts/<feature_slug>/` - per-feature artifacts such as `CONTEXT.md`, `discovery.md`, `approach.md`, `plan.md`, `phase-contract.md`, and `story-map.md`
- `.beads/critical-patterns.md` - promoted learnings approved for broad reuse
- `.beads/learnings/` - per-feature learnings files

## Session Finish

1. Update or close the active bead.
2. Leave `STATE.md` current. If the session is pausing under context pressure or interruption, write or update `HANDOFF.json` too.
3. Mention blockers, open questions, and next actions explicitly.
<!-- BEO:END -->
