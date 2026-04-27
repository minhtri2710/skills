<!-- BEO:START -->
## Beo Startup

1. At session start and after every context compaction, rerun this startup sequence from step 2.
2. Run the live onboarding check before downstream skill work:
   `node <installed-beo-onboard-root>/scripts/onboard_beo.mjs --repo-root "<absolute-repo-root>"`
3. Resolve `<installed-beo-onboard-root>` from the installed `beo-onboard` skill path.
4. Resolve `<absolute-repo-root>` to the directory containing this `AGENTS.md`, not the transient shell cwd.
5. If the check result is not `up_to_date`, stop and load `beo-onboard`.
6. If `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` after the live check passes.
7. Reopen `.beads/STATE.json` and `.beads/HANDOFF.json` when present; verify `HANDOFF.json` against live state before routing.
8. Reopen the selected active feature artifacts under `.beads/artifacts/<feature_slug>/` before acting on that feature.
9. Read `.beads/critical-patterns.md` before `beo-plan`, `beo-execute`, or `beo-swarm`.

## Beo Skill Chain
Startup orientation only:
```text
core runtime: beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute/beo-swarm -> beo-review -> done
optional closure: beo-review -> beo-compound -> beo-dream/done
```

Support skills: `beo-debug`, `beo-dream`, `beo-author`  
Reference skill: `beo-reference`

Legal owner transitions are canonical in `beo-references -> pipeline.md`.
Approval refresh/invalidation is canonical in `beo-references -> approval.md`.
Learning closure split is canonical in `beo-references -> learning.md`.
Use this chain as a startup orientation only, not as an alternative routing source.

## Runtime Rules
- never execute without validation approval
- `CONTEXT.md` owns locked decisions
- `beo-route` selects exactly one next owner; legal transitions are canonical in `beo-references -> pipeline.md`
- `beo-swarm` coordinates; it does not implement as coordinator
- swarm never self-downgrades to serial; reclassification must return through `beo-validate`
- use `HANDOFF.json` only for real checkpoints
- keep `STATE.json` current under `beo-references -> state.md`
- review severity and acceptance blocking are canonical in `beo-review` and `beo-references -> artifacts.md`
- `review -> done` is the default accepted-work closure when obvious `no-learning` applies; durable or unclear learning routes to `beo-compound`
- managed startup freshness comes from the live onboarding check, not file presence alone
- multiple active feature candidates require user selection
- do not disturb concurrent work from other agents
- never run bare `bv`; use robot commands from `beo-references -> cli.md`
- after bead DB mutations, flush with `br sync --flush-only` before committing

## Working Files
- `.beads/onboarding.json`
- `.beads/beo_status.mjs`
- `.beads/STATE.json`
- `.beads/HANDOFF.json`
- `.beads/artifacts/<feature_slug>/`
- `.beads/critical-patterns.md`
- `.beads/learnings/`

## Session End
1. update or close the active bead only when the current owner owns bead status/evidence mutation; otherwise record that no bead mutation was performed
2. update `STATE.json` only for fields owned by the current owner
3. run `br sync --flush-only` after bead DB mutations
4. write or update `HANDOFF.json` only when pausing or transferring ownership
5. record blockers, questions, and next action

<!-- BEO:END -->
