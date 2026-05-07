<!-- BEO:MANAGED START -->
## BEO Setup / Usage Requests

If the user asks to set up BEO, check BEO setup, install or refresh the AGENTS.md BEO managed block, or explain how to use BEO, use `beo-setup`.

`beo-setup` is setup/check/usage only. It is not a runtime owner and cannot approve, execute, review, or mutate feature artifacts.

## Beo Startup

1. Read `.beads/STATE.json` if present.
2. Read `.beads/HANDOFF.json` only if resuming paused or transferred work.
3. Read active feature artifacts only for the active `feature_slug`.
4. If no active feature exists and the user request names a feature goal, start through `beo-explore`.
5. Use `beo-route` only when owner identity or active feature identity is unsafe. If multiple active feature candidates exist, stop and ask the user which feature is active.
6. Treat startup output as advisory only; it cannot approve execution, select execution sets, emit review verdicts, or promote learning.

## Beo Skill Chain

Startup orientation summary: read `beo-reference -> references/operator-card.md` first for the workflow quick map; normal path is `beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`.
Legal transitions remain canonical in `beo-reference -> references/pipeline.md`.
Optional learning closure: `beo-review -> beo-compound -> done` only when REVIEW records durable-candidate or unclear single-feature learning. `beo-dream` only when cross-feature threshold or explicit corpus request exists.
Support skills: `beo-setup`, `beo-debug`, `beo-author`. Corpus skill: `beo-dream`. Reference skill: `beo-reference`.
Go mode only changes assumption posture. It does not bypass owner selection, Human approval gates, UAT gates, validation, approval freshness, `PASS_EXECUTE`, execution scope, review, or learning thresholds; see `beo-reference -> references/go-mode.md`.

Startup pointers: workflow quick map (`beo-reference -> references/operator-card.md`), legal transitions (`beo-reference -> references/pipeline.md`), state/handoff freshness (`beo-reference -> references/state.md`), approval refresh (`beo-reference -> references/approval.md`), and go mode (`beo-reference -> references/go-mode.md`).

## Working Files

- `.beads/STATE.json`
- `.beads/HANDOFF.json`
- `.beads/artifacts/<feature_slug>/`
- `.beads/learnings/`

## Session End

1. Update or close the active bead only when the current owner owns bead status/evidence mutation.
2. Update `STATE.json` only for fields owned by the current owner.
3. Flush any owner-owned artifact or optional bead metadata mutation before handoff or session end.
4. Write or update `HANDOFF.json` only when pausing or transferring ownership.
5. Record blockers, questions, and the next action.

<!-- BEO:MANAGED END -->
