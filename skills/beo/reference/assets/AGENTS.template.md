<!-- BEO:MANAGED START -->
Canonical workflow rules live in `skills/beo/reference/references/*`. This managed block is orientation only and creates no workflow authority.

## BEO Setup / Usage Requests

If the user asks to set up BEO, check BEO setup, install or refresh the AGENTS.md BEO managed block, or explain how to use BEO, use `beo-setup`.

`beo-setup` is setup/check/usage only. It is not a runtime owner and cannot approve, execute, review, or mutate feature artifacts (SETUP-01).

For feature delivery, do not use setup as a runtime owner. Continue with the current valid BEO owner, or use `beo-route` only if owner/feature identity is unsafe (ROUTE-01).

## Beo Startup

1. Read `.beads/STATE.json` if present.
2. Read `.beads/HANDOFF.json` only when resuming paused or transferred work.
3. Read only current required surfaces for the active feature (ART-01).
4. If no active feature exists and the user request names a feature goal, start through `beo-explore`.
5. Use `beo-route` only when owner identity or active feature identity is unsafe (ROUTE-01). If multiple active feature candidates exist, stop and ask the user which feature is active (STATE-02).
6. Treat startup output as advisory only; it cannot approve execution, select execution sets, emit review verdicts, record learning, consolidate learning, or author skill changes (STATE-01).
7. Before any owner action or mutation, load the active owner's `SKILL.md`. `STATE.json.current_owner` is not sufficient authority by itself.
8. Do not inspect unrelated files as workflow authority.
9. `STATE.json` and `HANDOFF.json` are non-authoritative mirrors/context; current required surfaces and active owner contract win (STATE-01).

## Beo Skill Chain

Normal delivery path: `beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`.
Legal transitions: `pipeline.md`.
Support: `beo-debug` proves unproven root cause. `beo-route` repairs unsafe owner/feature identity. `beo-reference` returns canonical references. `beo-setup` handles setup/check/usage only.
Learning: `beo-compound` records one observed learning case. `beo-dream` consolidates repeated finalized cases. `beo-author` updates or creates skills only when explicitly requested or selected. Learning has no runtime authority; see `references/learning.md`.

Startup pointers: operator card (`operator-card.md`), runtime kernel (`runtime-kernel.md`), pipeline (`pipeline.md`), state (`state.md`), approval (`approval.md`), go-mode (`go-mode.md`).

## Working Files

Tiny: `TICKET.md`. Standard: `CONTEXT.md`, `PLAN.md`, `TRACKER.json`, `REVIEW.md`.
Optional: `STATE.json`, `HANDOFF.json`, learning files when needed.

## Session End

1. Update or close the active bead only when the current owner owns bead status/evidence mutation.
2. Update `STATE.json` only for fields owned by the current owner.
3. Flush any owner-owned artifact mutation before handoff or session end.
4. Write or update `HANDOFF.json` only when pausing or transferring ownership.
5. Record blockers, questions, and the next action.
<!-- BEO:MANAGED END -->
