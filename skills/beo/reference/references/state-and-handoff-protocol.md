# State and Handoff Protocol

Canonical protocol for writing, reading, and cleaning up `.beads/STATE.md` and `.beads/HANDOFF.json`.

## Why This Exists

The beo pipeline uses two state surfaces:

- `STATE.md` for normal adjacent-skill handoff
- `HANDOFF.json` for emergency checkpointing when context is running out or a session must resume later

All skills must use the same shapes and semantics.

## Core Rule

- `STATE.md` is the happy-path handoff between adjacent skills.
- `HANDOFF.json` is the emergency checkpoint that survives context resets.
- Router reads `HANDOFF.json` first on resume.
- Other skills read `STATE.md` from the predecessor skill.

## Canonical STATE.md Header

Every skill must write this header in this exact order:

```markdown
# Beo State
- Phase: <skill-name> → <status>
- Feature: <epic-id> (<feature_slug>)
- Tasks: <summary relevant to current phase>
- Next: <next skill or action>
```

Skills may append phase-specific fields below a blank line.

## Planning-Aware STATE.md Fields

When the work is in or downstream of planning, append these fields when known:

```markdown
- Planning mode: <single-phase | multi-phase>
- Has phase plan: <true | false>
- Current phase: <number or 1>
- Total phases: <number | unknown>
- Phase name: <current phase name or feature summary>
```

These fields are strongly recommended for:

- `beo-planning`
- `beo-validating`
- `beo-swarming`
- `beo-executing`
- `beo-reviewing`
- `beo-router` when reporting or rewriting state

### Field semantics

- **Planning mode**
  - `single-phase`: one current phase covers the execution scope
  - `multi-phase`: the feature spans multiple meaningful phases, and only the current phase is prepared now

- **Has phase plan**
  - `true`: `.beads/artifacts/<feature>/phase-plan.md` exists and is part of the active planning model
  - `false`: no whole-feature phase sequencing artifact exists; this is normal for single-phase work

- **Current phase**
  - The selected current phase number
  - Use `1` for single-phase work unless a skill truly cannot know the phase number

- **Total phases**
  - Total phase count when known
  - Use `unknown` when sequencing exists conceptually but the count is not yet stable
  - For single-phase work, use `1`

- **Phase name**
  - Human-readable name of the current phase
  - For single-phase work, this may be the feature name or a concise summary of the current loop

## Canonical HANDOFF.json Base Schema

All fields below are required.

Note: `feature_name` is the historical field name, but in beo it carries the stable feature slug / artifact-path identifier, not a mutable display title.

```json
{
  "schema_version": 1,
  "phase": "<skill phase name>",
  "skill": "beo-<skill-name>",
  "feature": "<epic-id>",
  "feature_name": "<feature-slug>",
  "next_action": "<what to do next>",
  "in_flight_beads": ["<bead-ids>"],
  "timestamp": "<iso8601>"
}
```

Use `[]` when there are no in-flight beads.

## Planning-Aware HANDOFF.json Extension Fields

For planning-aware or downstream skills, include these additional top-level fields when known:

```json
{
  "planning_mode": "single-phase",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "Feedback flow"
}
```

These fields extend the base schema without replacing it.

## Go-Mode Extension

Go-mode checkpoints may add an optional top-level `mode` field:

```json
{
  "mode": "go"
}
```

Rules:

- allowed values: `"go"` or field absent
- `"go"` means resume the saved `skill` and `next_action` inside go-mode rather than normal feature routing
- planning-aware fields keep their normal meaning when `mode = "go"`
- do not invent additional mode values without updating this canonical protocol first

### Canonical meanings

- `planning_mode`
  - `"single-phase"` or `"multi-phase"`

- `has_phase_plan`
  - `true` when `.beads/artifacts/<feature>/phase-plan.md` exists and is active
  - `false` otherwise

- `current_phase`
  - current selected phase number
  - use `1` for single-phase work

- `total_phases`
  - integer when known
  - `"unknown"` when not yet stable

- `phase_name`
  - concise current phase label

## Optional Artifact Presence Map

When checkpointing planning, validating, routing, or execution state, include an `artifacts` object when it materially improves resume safety:

```json
{
  "artifacts": {
    "context": true,
    "discovery": true,
    "approach": true,
    "plan": true,
    "phase_plan": false,
    "phase_contract": true,
    "story_map": true
  }
}
```

### Artifact map rules

- Use booleans only
- Include the map when artifact completeness matters to the next step
- Do not infer that `phase_plan: false` is an error; it is normal for single-phase work
- `phase_contract` and `story_map` always refer to the **current phase** artifacts

## When To Write HANDOFF.json

Write `HANDOFF.json` when:

- context usage exceeds 65%
- a long-running orchestration must pause cleanly
- the session must checkpoint before continuation

Do not write it for normal phase-to-phase progression when `STATE.md` is sufficient.

## What To Include In A Checkpoint

In addition to the base fields, include phase-specific context such as:

- completed sub-steps
- pending dimensions/checks
- active workers
- open blockers
- locked decisions already captured
- resume instructions
- planning mode / phase-selection state
- artifact completeness when relevant

Swarming may extend the top level with extra fields, but the base schema must remain intact.

## Resume Protocol

When `HANDOFF.json` exists:

1. read it before normal routing
2. verify the saved state is still valid against the live graph and current files
3. load the saved skill
4. follow `next_action`

### Planning-aware resume notes

When the checkpoint includes planning-aware fields:

- treat `planning_mode` as the source of truth unless live artifacts contradict it
- if `has_phase_plan` is `true`, check whether `phase-plan.md` still exists
- if `current_phase` is present, resume against that phase unless the live graph proves the phase already completed
- never assume current-phase completion means whole-feature completion when `planning_mode = multi-phase`

## Cleanup Rule

Do not delete `HANDOFF.json` until the resumed skill has successfully written a fresh `STATE.md` or an equivalent new checkpoint.

Canonical cleanup command after successful resume:

```bash
rm .beads/HANDOFF.json
```

## Examples

### Example A — STATE.md for single-phase planning handoff

```markdown
# Beo State
- Phase: planning → complete
- Feature: pe-abc (feedback-flow)
- Tasks: 4 planned for current phase
- Next: beo-validating

- Planning mode: single-phase
- Has phase plan: false
- Current phase: 1
- Total phases: 1
- Phase name: Feedback flow
```

### Example B — STATE.md for multi-phase planning handoff

```markdown
# Beo State
- Phase: planning → complete
- Feature: pe-def (inbound-mail)
- Tasks: 5 planned for current phase
- Next: beo-validating

- Planning mode: multi-phase
- Has phase plan: true
- Current phase: 1
- Total phases: 3
- Phase name: Accept inbound payload safely
```

### Example C — HANDOFF.json for single-phase work

```json
{
  "schema_version": 1,
  "phase": "planning",
  "skill": "beo-planning",
  "feature": "pe-abc",
  "feature_name": "feedback-flow",
  "next_action": "Finish phase-contract.md, then write story-map.md and create current-phase beads.",
  "in_flight_beads": [],
  "timestamp": "2026-03-31T12:00:00Z",
  "planning_mode": "single-phase",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "Feedback flow",
  "artifacts": {
    "context": true,
    "discovery": true,
    "approach": true,
    "plan": true,
    "phase_plan": false,
    "phase_contract": false,
    "story_map": false
  }
}
```

### Example D — HANDOFF.json for multi-phase work

```json
{
  "schema_version": 1,
  "phase": "validating",
  "skill": "beo-validating",
  "feature": "pe-def",
  "feature_name": "inbound-mail",
  "next_action": "Resume current-phase validation for Phase 1, then route to execution only if approval is granted.",
  "in_flight_beads": [],
  "timestamp": "2026-03-31T12:30:00Z",
  "planning_mode": "multi-phase",
  "has_phase_plan": true,
  "current_phase": 1,
  "total_phases": 3,
  "phase_name": "Accept inbound payload safely",
  "artifacts": {
    "context": true,
    "discovery": true,
    "approach": true,
    "plan": true,
    "phase_plan": true,
    "phase_contract": true,
    "story_map": true
  }
}
```

### Example E — HANDOFF.json for go-mode resume

```json
{
  "schema_version": 1,
  "phase": "executing",
  "skill": "beo-executing",
  "feature": "pe-ghi",
  "feature_name": "router-remediation",
  "next_action": "Resume the current execution loop, then continue go-mode routing at the next gate.",
  "in_flight_beads": ["pe-ghi.2"],
  "timestamp": "2026-03-31T13:00:00Z",
  "mode": "go",
  "planning_mode": "single-phase",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "Router remediation"
}
```

## Planning-Aware Field Transition Cleanup

When replanning changes the planning mode, phase structure, or execution scope, all planning-aware fields must be refreshed in both `STATE.md` and `HANDOFF.json` before any handoff.

### Replanning to single-phase

Set:

- `planning_mode: single-phase`
- `has_phase_plan: false`
- `current_phase: 1`
- `total_phases: 1`
- `phase_name:` feature summary or cleared value — do not leave a stale phase name

Delete `phase-plan.md` from the artifact directory. Do not leave it as a stale artifact.

### Replanning within multi-phase (changed sequencing)

Set all fields to reflect the new sequence:

- `has_phase_plan: true` (rewrite the plan)
- `current_phase:` new selected phase number
- `total_phases:` updated count
- `phase_name:` new current phase name — must not carry the old phase name

### Phase advancement (current phase completed, next phase starts)

Increment `current_phase`, update `phase_name` to the new phase, and keep `total_phases` current. Delete old `phase-contract.md` and `story-map.md` before regenerating for the new phase.

### Hard rule

Never leave stale `phase_name`, `current_phase`, or `has_phase_plan` values after replanning or phase advancement. Every planning-aware field must reflect the actual state of the work.

## Hard Rules

- Never skip `HANDOFF.json` if it exists.
- Never write non-canonical field names in the base schema.
- Never omit `feature_name` or `in_flight_beads`.
- Never delete `HANDOFF.json` before the resumed skill checkpoints safely.
- Never write a `STATE.md` missing the four canonical header fields.
- Never treat `phase-contract.md` or `story-map.md` as whole-feature artifacts when `planning_mode = multi-phase`.
- Never assume `phase_plan: false` means an error; it is valid for single-phase work.
- Never write a non-canonical `mode` value; `"go"` is the only documented extension.
