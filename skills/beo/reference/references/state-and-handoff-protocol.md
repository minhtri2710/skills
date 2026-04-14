# State and Handoff Protocol

> **~334 lines.** Key sections: STATE.json Schema (canonical fields), HANDOFF.json Schema, Status Values, Examples A-F. Use your editor's search to jump to the section you need.

## Contents

- [Why This Exists](#why-this-exists)
- [Core Rule](#core-rule)
- [Canonical STATE.json Schema](#canonical-statejson-schema)
- [Canonical HANDOFF.json Base Schema](#canonical-handoffjson-base-schema)
- [Planning-Aware HANDOFF.json Extension Fields](#planning-aware-handoffjson-extension-fields)
- [Go-Mode Extension](#go-mode-extension)
- [Optional Artifact Presence Map](#optional-artifact-presence-map)
- [When To Write HANDOFF.json](#when-to-write-handoffjson)
- [What To Include In A Checkpoint](#what-to-include-in-a-checkpoint)
- [Resume Protocol](#resume-protocol)
- [Cleanup Rule](#cleanup-rule)
- [Examples](#examples)
- [Planning-Aware Field Transition Cleanup](#planning-aware-field-transition-cleanup)
- [Hard Rules](#hard-rules)

Canonical protocol for writing, reading, and cleaning up `.beads/STATE.json` and `.beads/HANDOFF.json`.

## Why This Exists

The beo pipeline uses two state surfaces:

- `STATE.json` for normal adjacent-skill handoff
- `HANDOFF.json` for emergency checkpointing when context is running out or a session must resume later

All skills must use the same shapes and semantics.

## Core Rule

- `STATE.json` is the happy-path handoff between adjacent skills.
- `HANDOFF.json` is the emergency checkpoint that survives context resets.
- Router reads `HANDOFF.json` first on resume.
- Other skills read `STATE.json` from the predecessor skill.

## Canonical STATE.json Schema

Every skill must write `.beads/STATE.json` with all fields present.

### Base fields (required)

```json
{
  "schema_version": 1,
  "phase": "<skill-name>",
  "status": "<canonical-routing-state>",
  "feature": "<epic-id>",
  "feature_slug": "<feature_slug>",
  "tasks": "<summary relevant to current phase>",
  "next": "beo-<next-skill>"
}
```

### Planning-aware fields (required — use defaults for single-phase)

```json
{
  "planning_mode": "single-phase",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "<current phase name or feature summary>"
}
```

The complete STATE.json combines both blocks above (12 fields total).

### Field semantics

- **schema_version** — always `1`; increment only when the schema changes incompatibly

- **phase** — the skill that wrote this state (e.g., `"planning"`, `"executing"`)

- **status** — the canonical routing state from the state routing table (e.g., `"exploring"`, `"ready-to-validate"`, `"executing"`)
- This may also be a paused pre-execution planning state such as `"awaiting-planning-approval"` when the user must approve the multi-phase sequence before validation can begin.

- **feature** — the epic ID (e.g., `"pe-abc"`)

- **feature_slug** — the stable feature slug / artifact-path identifier (e.g., `"feedback-flow"`)

- **tasks** — human-readable summary of task state relevant to the current phase (e.g., `"4 planned for current phase"`, `"3/5 complete, 1 blocked"`)

- **next** — the next skill or action to take (e.g., `"beo-validating"`, `"beo-compounding"`)

- **planning_mode**
  - `"single-phase"`: one current phase covers the execution scope
  - `"multi-phase"`: the feature spans multiple meaningful phases, and only the current phase is prepared now
  - `"unknown"`: planning has not yet determined the mode (valid only during exploring and early planning, before approach.md is finalized)

- **has_phase_plan**
  - `true`: `.beads/artifacts/<feature>/phase-plan.md` exists and is part of the active planning model
  - `false`: no whole-feature phase sequencing artifact exists; this is normal for single-phase work

- **current_phase**
  - The selected current phase number
  - Use `1` for single-phase work

- **total_phases**
  - Total phase count when known
  - Use `"unknown"` when sequencing exists conceptually but the count is not yet stable
  - For single-phase work, use `1`

- **phase_name**
  - Human-readable name of the current phase
  - For single-phase work, this may be the feature name or a concise summary of the current loop

## Canonical HANDOFF.json Base Schema

All fields below are required.

Note: `feature_name` is the historical field name, but in beo it carries the stable feature slug / artifact-path identifier, not a mutable display title. (STATE.json uses the clearer name `feature_slug` for the same value.)

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

Planning-aware field semantics are defined in the [Field semantics](#field-semantics) section above.

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

Do not write it for normal phase-to-phase progression when `STATE.json` is sufficient.

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
- never assume current-phase completion means whole-feature completion when `planning_mode = "multi-phase"`

## Cleanup Rule

Do not delete `HANDOFF.json` until the resumed skill has successfully written a fresh `STATE.json` or an equivalent new checkpoint.

Canonical cleanup command after successful resume:

```bash
rm .beads/HANDOFF.json
```

## Examples

### Example A — STATE.json for single-phase planning handoff

```json
{
  "schema_version": 1,
  "phase": "planning",
  "status": "ready-to-validate",
  "feature": "pe-abc",
  "feature_slug": "feedback-flow",
  "tasks": "4 planned for current phase",
  "next": "beo-validating",
  "planning_mode": "single-phase",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "Feedback flow"
}
```

### Example B — STATE.json for multi-phase planning handoff

Same as Example A with these field changes:

- `"planning_mode": "multi-phase"`, `"has_phase_plan": true`, `"total_phases": 3`

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

Same as Example C with: `"planning_mode": "multi-phase"`, `"has_phase_plan": true`, `"total_phases": 3`, all `artifacts` values `true`.

### Example E — HANDOFF.json for go-mode resume

Same as Example C base fields plus top-level `"mode": "go"` and `"in_flight_beads": ["pe-ghi.2"]`.

### Example F — STATE.json after exploring completes (handoff to planning)

Same as Example A with: `"phase": "exploring"`, `"status": "planning-needs-approach"`, `"next": "beo-planning"`, `"planning_mode": "unknown"`.

## Planning-Aware Field Transition Cleanup

When replanning changes the planning mode, phase structure, or execution scope, refresh all planning-aware fields in both `STATE.json` and `HANDOFF.json` before any handoff.

| Scenario | Fields to set | Artifacts to clean |
|----------|--------------|-------------------|
| Replan → single-phase | `planning_mode: "single-phase"`, `has_phase_plan: false`, `current_phase: 1`, `total_phases: 1`, `phase_name`: feature summary | Delete `phase-plan.md` |
| Replan within multi-phase | `has_phase_plan: true` (rewrite), `current_phase`: new number, `total_phases`: updated, `phase_name`: new name | Rewrite `phase-plan.md` |
| Phase advancement | Increment `current_phase`, update `phase_name`, keep `total_phases` current | Delete old `phase-contract.md` + `story-map.md` |

**Hard rule:** Never leave stale `phase_name`, `current_phase`, or `has_phase_plan` values after replanning or phase advancement.

## Hard Rules

- Never skip `HANDOFF.json` if it exists.
- Never write non-canonical field names in the base schema of either `STATE.json` or `HANDOFF.json`.
- Never omit required fields. `STATE.json` requires all 12 fields; `HANDOFF.json` requires all base-schema fields.
- Never delete `HANDOFF.json` before the resumed skill checkpoints safely.
- Never write a `STATE.json` missing any canonical field. All 12 fields are mandatory.
- Never treat `phase-contract.md` or `story-map.md` as whole-feature artifacts when `planning_mode = "multi-phase"`.
- Never assume `has_phase_plan: false` means an error; it is valid for single-phase work.
- Never write a non-canonical `mode` value; `"go"` is the only documented extension.
