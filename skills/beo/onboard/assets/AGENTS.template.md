<!-- BEO:MANAGED START -->
## Beo Startup

1. Run the live onboarding check before downstream beo work: `node <installed-beo-onboard-root>/scripts/onboard_beo.mjs --repo-root "<absolute-repo-root>"`.
2. If the check result is not `up_to_date`, stop and load `beo-onboard`.
3. If `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` after the live check passes.
4. Reopen `.beads/STATE.json` and `.beads/HANDOFF.json` when present; verify handoff freshness before routing.
5. Reopen active feature artifacts under `.beads/artifacts/<feature_slug>/` before acting on that feature.
6. Treat cached dependency posture as advisory and unknown-by-default; only live `beo-validate` / `beo-swarm` checks can authorize `PASS_SWARM`.

## Beo Skill Chain

Startup orientation only: `beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute/beo-swarm -> beo-review -> done`.
This chain is an orientation summary only; legal transitions remain canonical in `beo-reference -> pipeline.md`.
Optional closure: `beo-review -> beo-compound -> beo-dream/done`.
Support skills: `beo-debug`, `beo-dream`, `beo-author`. Reference skill: `beo-reference`.

Canonical pointers:
- legal transitions: `beo-reference -> pipeline.md`
- approval refresh/invalidation: `beo-reference -> approval.md`
- learning closure split: `beo-reference -> learning.md`
- state and handoff freshness: `beo-reference -> state.md`
- commands: `beo-reference -> cli.md`

## Runtime Rules

- Never execute without validation approval.
- `CONTEXT.md` owns locked decisions.
- `beo-route` selects exactly one next owner.
- `beo-swarm` coordinates and never implements as coordinator.
- Swarm never self-downgrades to serial; reclassification returns through `beo-validate`.
- Managed startup freshness comes from the live onboarding check, not file presence.
- Do not disturb concurrent work from other agents.
- After bead DB mutations, flush with `br sync --flush-only` before committing.

## Working Files

- `.beads/onboarding.json`
- `.beads/beo_status.mjs`
- `.beads/STATE.json`
- `.beads/HANDOFF.json`
- `.beads/artifacts/<feature_slug>/`
- `.beads/critical-patterns.md`
- `.beads/learnings/`

## Session End

1. Update or close the active bead only when the current owner owns bead status/evidence mutation.
2. Update `STATE.json` only for fields owned by the current owner.
3. Run `br sync --flush-only` after bead DB mutations.
4. Write or update `HANDOFF.json` only when pausing or transferring ownership.
5. Record blockers, questions, and next action.

<!-- BEO:MANAGED END -->
