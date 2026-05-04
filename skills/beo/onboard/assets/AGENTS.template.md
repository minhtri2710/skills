<!-- BEO:MANAGED START -->
## Beo Startup

1. Run the live onboarding check before any downstream beo work: `node skills/beo/onboard/scripts/onboard_beo.mjs --repo-root "$(pwd)"`.
2. If the check result is not `up_to_date`, stop and load `beo-onboard`.
3. If `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` after the live check passes.
4. Reopen `.beads/STATE.json` and `.beads/HANDOFF.json` when present; verify handoff freshness before routing.
5. Reopen active feature artifacts under `.beads/artifacts/<feature_slug>/` before acting on that feature.
6. Treat status output and cached dependency posture as advisory, display-only context; canonical owners and references remain binding.

## Beo Skill Chain

Startup orientation summary: `beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`.
Legal transitions remain canonical in `beo-reference -> pipeline.md`.
Optional closure: `beo-review -> beo-compound -> beo-dream/done`.
Support skills: `beo-debug`, `beo-author`. Bootstrap skill: `beo-onboard`. Corpus skill: `beo-dream`. Reference skill: `beo-reference`.
Go mode only reduces unnecessary operator prompts. It does not bypass owner selection, approval, readiness, execution scope, review, or learning gates; see `beo-reference -> go-mode.md`.

Startup pointers: legal transitions (`pipeline.md`), state/handoff freshness (`state.md`), approval refresh (`approval.md`), and go mode (`go-mode.md`).

## Advisory Status Rule

Startup and status surfaces are orientation only. They do not approve execution,
select routes, validate readiness, select execution sets, emit review verdicts,
or promote learning.

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
3. Flush bead DB mutations through `beo-reference -> cli.md`.
4. Write or update `HANDOFF.json` only when pausing or transferring ownership.
5. Record blockers, questions, and the next action.

<!-- BEO:MANAGED END -->
