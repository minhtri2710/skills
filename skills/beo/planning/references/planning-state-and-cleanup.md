# Planning State and Cleanup

Operational reference for state updates, handoff rules, replanning cleanup, and context-budget checkpointing.

## 13. State Update and Handoff Rules

After planning artifacts are written, tasks are created, and dependencies are wired, write `.beads/STATE.json` using the canonical schema from:

```text
../../reference/references/state-and-handoff-protocol.md
```

Include these planning-specific fields.

### Minimum planning state fields

```json
{
  "schema_version": 1,
  "phase": "planning",
  "status": "ready-to-validate",
  "feature": "<epic-id>",
  "feature_slug": "<feature_slug>",
  "tasks": "<summary>",
  "next": "beo-validating",
  "planning_mode": "single-phase | multi-phase",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "<name or feature summary>"
}
```

### Handoff rules

#### Single-phase

- validating checks the current phase, which is also the full execution scope

#### Multi-phase

- validating checks the selected current phase only
- later phases remain deferred in `phase-plan.md`
- when the current phase completes and later phases remain, router should return to `beo-planning`
- do not treat current-phase completion as whole-feature completion
- do not hand off to validating until the user has approved the phase sequence and current-phase selection

### Approval summary templates

#### Single-phase

```text
Plan ready.
Mode: single-phase

- Current phase: full feature scope
- Stories: <count>
- Tasks: <count>
- Risks: <summary>

Ready to validate.
```

#### Multi-phase

```text
Whole-feature phase plan is ready.
Mode: multi-phase

- Total phases: <N>
- Current phase to prepare now: <phase name>
- Why this phase is first / next: <reason>
- Stories in current phase: <count>
- Tasks in current phase: <count>
- Later phases intentionally deferred: <summary>

Approve this phase sequence and current phase selection before validation?
```

## 14. Phase-Plan Invalidation and Replanning Cleanup

When planning re-enters (multi-phase back-edge, scope revision, or user-initiated replan), stale artifacts and state fields must be cleaned up before new planning proceeds.

### Trigger conditions

Replanning cleanup is required when any of these are true:

- the current phase completed and the back-edge returns to planning for the next phase
- the user or reviewer requests a scope revision that changes the phase structure
- the planning mode changes (e.g., multi-phase to single-phase or vice versa)
- the phase sequence changes within multi-phase work

### If replanning results in single-phase work

```bash
# 1. Delete stale phase-plan.md
rm .beads/artifacts/<feature_slug>/phase-plan.md

# 2. Delete stale current-phase artifacts if they reference the old phase identity
rm .beads/artifacts/<feature_slug>/phase-contract.md
rm .beads/artifacts/<feature_slug>/story-map.md
```

Then rewrite planning-aware state fields in `STATE.json` and `HANDOFF.json`:

- `planning_mode: single-phase`
- `has_phase_plan: false`
- `current_phase: 1`
- `total_phases: 1`
- `phase_name:` set to the feature summary (clear the stale value)

Regenerate `phase-contract.md` and `story-map.md` for the new single-phase scope.

### If replanning remains multi-phase but changes sequencing

1. Rewrite `phase-plan.md` to reflect the new sequence
2. Delete stale `phase-contract.md` and `story-map.md` if they reference an old phase identity
3. Refresh all planning-aware fields including `phase_name`
4. Regenerate current-phase artifacts for the newly selected phase
5. Prior approval is invalidated — route back through `beo-validating`

### If the current phase completed and the next phase starts

1. Update `phase-plan.md` to mark the completed phase
2. Delete old `phase-contract.md` and `story-map.md`
3. Increment `current_phase`
4. Update `phase_name` to the new current phase name
5. Create fresh `phase-contract.md` and `story-map.md` for the new current phase
6. Prior approval is invalidated — route back through `beo-validating`

### Hard rules

- **Delete, do not invalidate.** Stale `phase-plan.md` must be deleted, not marked invalid.
- **`phase_name` must be refreshed.** Do not leave a stale phase name from a prior cycle.
- **Prior approval is always invalidated** when the phase structure or execution scope changes.
- **`STATE.json` and `HANDOFF.json` must be refreshed** before any handoff after replanning.

## 15. Context-Budget Checkpointing

If context usage exceeds 65% during planning:

1. write findings so far to `discovery.md`
2. write `approach.md` if approach shaping has started
3. write `plan.md` if a summary exists
4. write `phase-plan.md` if multi-phase sequencing is already clear
5. write `phase-contract.md` if the current phase is drafted
6. write `story-map.md` if the current phase story sequence is drafted
7. create any ready current-phase task beads
8. write `HANDOFF.json`

Use the canonical base schema from:

```text
../../reference/references/state-and-handoff-protocol.md
```

Then add any planning-specific resume detail you need.

### Checkpoint rule

Prefer partial but truthful artifacts over leaving planning state only in conversation history.

A partial `approach.md` or `phase-plan.md` is acceptable if clearly marked as incomplete.
A missing artifact is harder to resume from than an incomplete one with explicit gaps.
