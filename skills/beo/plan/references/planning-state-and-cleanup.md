# Planning State And Cleanup

State, handoff, and replanning rules for `beo-plan`.

## 1. Normal State Write

After artifacts are written, beads created, and dependencies wired, write `.beads/STATE.json` using the canonical schema from `beo-reference` → `references/state-and-handoff-protocol.md`.

Minimum planning fields:

```json
{
  "schema_version": 1,
  "phase": "planning",
  "status": "ready-to-validate",
  "feature": "<epic-id>",
  "feature_slug": "<feature_slug>",
  "tasks": "<summary>",
  "next": "beo-validate",
  "planning_mode": "single-phase | multi-phase",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "<name or feature summary>"
}
```

## 2. Handoff Rules

Single-phase:
- validation checks the only phase, which is also the full execution scope

Multi-phase:
- validation checks the selected current phase only
- later phases stay deferred in `phase-plan.md`
- when the current phase completes and later phases remain, route back to `beo-plan`
- do not hand off to validation until the user approves the phase sequence and current-phase choice

Use the single-phase summary inline when needed:

```text
Plan ready.
Mode: single-phase

- Current phase: full feature scope
- Stories: <count>
- Tasks: <count>
- Risks: <summary>

Ready to validate.
```

For multi-phase approval wording, use `beo-reference` → `references/approval-gates.md`.

## 3. Replanning Cleanup

Before replanning, remove stale current-phase artifacts instead of marking them invalid.

Cleanup is required when:
- the next phase begins after the current one completes
- user or review changes phase structure or scope
- planning mode changes
- multi-phase sequencing changes

### Replan To Single-Phase

```bash
rm .beads/artifacts/<feature_slug>/phase-plan.md
rm .beads/artifacts/<feature_slug>/phase-contract.md
rm .beads/artifacts/<feature_slug>/story-map.md
```

Then rewrite planning-aware state fields:
- `planning_mode: single-phase`
- `has_phase_plan: false`
- `current_phase: 1`
- `total_phases: 1`
- `phase_name:` reset to the feature summary

Regenerate `phase-contract.md` and `story-map.md` for the new single phase.

### Replan Within Multi-Phase

1. rewrite `phase-plan.md` if sequencing changed
2. delete stale `phase-contract.md` and `story-map.md` if they describe the wrong phase
3. refresh `phase_name` and the other planning-aware state fields
4. regenerate current-phase artifacts
5. remove approval with `br label remove <EPIC_ID> -l approved`
6. route back through `beo-validate`

### Advance To The Next Phase

1. update `phase-plan.md` to mark the completed phase
2. delete the old `phase-contract.md` and `story-map.md`
3. increment `current_phase`
4. update `phase_name`
5. create fresh current-phase artifacts
6. remove approval with `br label remove <EPIC_ID> -l approved`
7. route back through `beo-validate`

## 4. Hard Rules

- delete stale planning artifacts; do not merely label them stale
- refresh `phase_name` every time phase identity changes
- invalidate prior approval whenever phase structure or execution scope changes
- refresh `STATE.json` and `HANDOFF.json` before handing off after replanning

## 5. Context-Budget Checkpoint

If context exceeds 65%, write what is already true in this order:
1. `discovery.md`
2. `approach.md`
3. `plan.md`
4. `phase-plan.md` when sequencing is clear
5. `phase-contract.md` when the current phase is drafted
6. `story-map.md` when story order is drafted
7. any ready current-phase beads
8. `STATE.json` for the normal adjacent-skill transition; write `HANDOFF.json` only when checkpoint or low-context resume detail is needed

Prefer partial but truthful artifacts over leaving planning state only in chat history.
