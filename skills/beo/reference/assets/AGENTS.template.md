<!-- BEO:MANAGED START -->
## Beo Startup

1. Read `.beads/STATE.json` if present.
2. Read `.beads/HANDOFF.json` only if resuming paused or transferred work.
3. Read active feature artifacts only for the active `feature_slug`.
4. If no active feature exists, start through `beo-route` or `beo-explore`.
5. If multiple active feature candidates exist, stop and ask the user which feature is active.
6. Treat startup output as advisory only; it cannot approve execution, select execution sets, emit review verdicts, or promote learning.

## Beo Skill Chain

Startup orientation summary: read `operator-card.md` first for the workflow quick map; normal path is `beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`.
Legal transitions remain canonical in `references/pipeline.md`.
Optional closure: `beo-review -> beo-compound -> beo-dream/done`.
Support skills: `beo-debug`, `beo-author`. Corpus skill: `beo-dream`. Reference skill: `beo-reference`.
Go mode only changes assumption posture. It does not bypass owner selection, Human approval gates, UAT gates, validation, approval freshness, `PASS_EXECUTE`, execution scope, review, or learning thresholds; see `references/go-mode.md`.

Startup pointers: workflow quick map (`operator-card.md`), legal transitions (`pipeline.md`), state/handoff freshness (`state.md`), approval refresh (`approval.md`), and go mode (`go-mode.md`).

## Working Files

- `.beads/STATE.json`
- `.beads/HANDOFF.json`
- `.beads/artifacts/<feature_slug>/`
- `.beads/learnings/`

## Session End

1. Update or close the active bead only when the current owner owns bead status/evidence mutation.
2. Update `STATE.json` only for fields owned by the current owner.
3. Flush bead DB mutations through `references/cli.md`.
4. Write or update `HANDOFF.json` only when pausing or transferring ownership.
5. Record blockers, questions, and the next action.

<!-- BEO:MANAGED END -->
