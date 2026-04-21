# State and Handoff Protocol

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
- [Canonical Wait-State Statuses](#canonical-wait-state-statuses)
- [Examples](#examples)
- [Planning-Aware Field Transition Cleanup](#planning-aware-field-transition-cleanup)
- [Hard Rules](#hard-rules)

Canonical protocol for writing, reading, resuming, and cleaning up `.beads/STATE.json` and `.beads/HANDOFF.json`.

## Why This Exists

Use `STATE.json` for normal adjacent-skill handoff and `HANDOFF.json` for emergency checkpointing when context is low or a session must resume later.
Use the canonical shapes and semantics in every skill.

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

The complete `STATE.json` combines both blocks above (12 required fields).

### Optional extension fields

These top-level fields are valid when present but not required in every write:

```json
{
  "reason": "awaiting-planning-approval",
  "content": "planning approval is required before continuing",
  "origin_skill": "beo-review",
  "return_to": "beo-review",
  "reactive_fix": true
}
```

- **reason** — Canonical routing or wait-state reason when the writer needs to explain why the current `next` target was chosen.
- **content** — Concise human-facing pause, checkpoint, or handoff content when the writer needs more than `status` and `tasks` to make the next step clear.
- **origin_skill** — The skill that initiated a reactive-fix or debugging transition. Set when entering `beo-debug` or routing a reactive fix through `beo-execute`.
- **return_to** — The skill to return to after the fix or debug session completes.
- **reactive_fix** — `true` when the transition is a reactive fix from review; `false` or absent otherwise.

Clear `origin_skill`, `return_to`, and `reactive_fix` after successful return to the origin skill. Preserve `reason` / `content` only while they still describe the current `next` target. When checkpointing to `HANDOFF.json`, include these fields if they are set.

### Field semantics

- **schema_version** — Always `1`. Increment only for incompatible schema changes.
- **phase** — Record the skill that wrote the state, such as `"router"` or `"planning"`.
- **status** — Use the canonical routing state from the state routing table, such as `"exploring"`, `"ready-to-validate"`, or `"executing"`. Use paused pre-execution planning states such as `"awaiting-planning-approval"` when the user must approve the multi-phase sequence before validation begins.
- **feature** — Record the epic ID, such as `"pe-abc"`.
- **feature_slug** — Record the stable feature slug / artifact-path identifier, such as `"feedback-flow"`.
- **tasks** — Summarize task state for the current phase, such as `"4 planned for current phase"` or `"3/5 complete, 1 blocked"`.
- **next** — Record the direct next target, such as `"beo-validate"`, `"user"`, or `"done"`.
- **planning_mode** — Use `"single-phase"` when one current phase covers execution scope, `"multi-phase"` when the feature spans meaningful phases and only the current phase is prepared now, and `"unknown"` only during exploring and early planning before `approach.md` is finalized.
- **has_phase_plan** — Set `true` when `.beads/artifacts/<feature>/phase-plan.md` exists and is part of the active planning model. Set `false` when no whole-feature phase sequencing artifact exists; this is normal for single-phase work.
- **current_phase** — Record the selected current phase number. Use `1` for single-phase work.
- **total_phases** — Record the total phase count when known. Use `"unknown"` when sequencing exists conceptually but the count is not yet stable. Use `1` for single-phase work.
- **phase_name** — Record a human-readable name for the current phase. For single-phase work, use the feature name or a concise summary of the current loop.

## Canonical HANDOFF.json Base Schema

All fields below are required.

Note: `feature_name` is the historical field name, but in beo it carries the stable feature slug / artifact-path identifier, not a mutable display title. `STATE.json` uses `feature_slug` for the same value.

```json
{
  "schema_version": 1,
  "phase": "<skill phase name>",
  "skill": "beo-<skill-name>",
  "feature": "<epic-id>",
  "feature_name": "<feature-slug>",
  "next": "<beo-skill | user | done>",
  "reason": "<canonical routing or checkpoint reason>",
  "content": "<optional concise checkpoint or pause content>",
  "in_flight_beads": ["<bead-ids>"],
  "timestamp": "<iso8601>"
}
```

Use `[]` when there are no in-flight beads. Use `content: ""` when no extra checkpoint content is needed.

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

- Allow only `"go"` or field absence.
- Use `"go"` to resume the saved `skill` and `next` inside go-mode instead of normal feature routing.
- Keep planning-aware fields at their normal meaning when `mode = "go"`.
- Do not invent additional mode values without updating this canonical protocol first.

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

- Use booleans only.
- Include the map when artifact completeness matters to the next step.
- Do not treat `phase_plan: false` as an error; it is normal for single-phase work.
- Treat `phase_contract` and `story_map` as **current phase** artifacts.

## When To Write HANDOFF.json

Write `HANDOFF.json` when:

- context usage exceeds 65%
- a long-running orchestration must pause cleanly
- the session must checkpoint before continuation

Do not write it for normal phase-to-phase progression when `STATE.json` is sufficient.

## What To Include In A Checkpoint

Include phase-specific context such as:

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

1. Read it before normal routing.
2. Verify the saved state against the live graph and current files.
3. Load the saved skill.
4. Follow `next` and any supporting `reason` / `content`.

### Planning-aware resume notes

When the checkpoint includes planning-aware fields:

- Treat `planning_mode` as the source of truth unless live artifacts contradict it.
- If `has_phase_plan` is `true`, check whether `phase-plan.md` still exists.
- If `current_phase` is present, resume against that phase unless the live graph proves the phase already completed.
- Never assume current-phase completion means whole-feature completion when `planning_mode = "multi-phase"`.

## Cleanup Rule

Do not delete `HANDOFF.json` until the resumed skill has successfully written a fresh `STATE.json` or an equivalent new checkpoint.

Canonical cleanup command after successful resume:

```bash
rm .beads/HANDOFF.json
```

## State Transitions Per Skill

| Skill | Write `phase` | Write `status` | Write `next` |
|---|---|---|---|
| `beo-route` | `"router"` | current routing state | routed skill |
| `beo-explore` | `"exploring"` | `"planning-needs-approach"` on completion; `"awaiting-exploration-answer"` when paused for user | `"beo-plan"` on completion; current skill on pause |
| `beo-plan` | `"planning"` | planning state from the routing table, including `"awaiting-planning-approval"` and `"ready-to-validate"` | next required skill or action |
| `beo-validate` | `"validating"` | validation result state; `"awaiting-execution-approval"` when waiting for user approval | next required skill or action |
| `beo-swarm` | `"swarming"` | swarming/execution routing state from the routing table; `"needs-debugging"` or `"cancelled-needs-decision"` when redirecting to route | next required skill or action |
| `beo-execute` | `"executing"` | execution state; `"blocked-awaiting-user"` or `"blocked-external"` when paused; `"needs-debugging"` or `"cancelled-needs-decision"` when redirecting to route | next required skill or action |
| `beo-review` | `"reviewing"` | review result state; `"awaiting-uat"` when waiting for human UAT | `"beo-compound"` or other required next action |
| `beo-debug` | `"debugging"` | debugging state; `"debug-findings-ready"` or `"blocked-external"` when paused | origin skill via `return_to`, or `"beo-route"` for standalone |
| `beo-compound` | `"compounding"` | final post-review state from the routing table | next required skill or action |
| `beo-dream` | `"dream"` | consolidation state; `"dream-complete"` on finish | `"beo-route"` |
| `beo-author` | `"writing-skills"` | skill-creation state from the RED/GREEN/REFACTOR cycle | `"beo-route"` |
| `beo-onboard` | `"using-beo"` | onboarding state; `"onboarding-complete"` on finish | `"beo-route"` |

## Canonical Wait-State Statuses

When a skill pauses for a human decision, use one of these canonical `status` values in `STATE.json`. This prevents router from reloading the wrong skill or advancing prematurely after resume.

| Status | Skill That Sets It | Meaning | Resume Trigger |
|---|---|---|---|
| `awaiting-exploration-answer` | `beo-explore` | Exploring paused for user answer to a gray-area question | User provides the answer |
| `awaiting-planning-approval` | `beo-plan` | Multi-phase sequence needs user approval before validation | User approves or rejects the sequence |
| `awaiting-execution-approval` | `beo-validate` | Validation passed; waiting for explicit user approval to begin execution | User grants execution approval |
| `awaiting-uat` | `beo-review` | Automated review complete; waiting for human UAT walkthrough | User completes UAT confirmation |
| `blocked-awaiting-user` | `beo-execute` | All remaining work is blocked and requires a human decision | User provides direction on blockers |
| `blocked-external` | `beo-execute`, `beo-debug` | Blocked on infrastructure, permissions, or external service outside agent control | External dependency resolved |
| `debug-findings-ready` | `beo-debug` | Root cause identified or escalation limit reached; findings ready for user review | User reviews findings and provides direction |

### Wait-State Usage Rules

- Write the wait-state status to `STATE.json` before pausing.
- Router must match the wait-state status to decide whether to resume the paused skill or return to user.
- Do not advance past a wait state without the triggering event.
- On resume, the paused skill re-reads `STATE.json` and continues from its saved progress.

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
  "next": "beo-validate",
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
  "skill": "beo-plan",
  "feature": "pe-abc",
  "feature_name": "feedback-flow",
  "next": "beo-plan",
  "reason": "planning-checkpoint",
  "content": "Finish phase-contract.md, then write story-map.md and create current-phase beads.",
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

Same as Example C base fields plus top-level `"mode": "go"`, `"next": "beo-plan"`, and `"in_flight_beads": ["pe-ghi.2"]`.

### Example F — STATE.json after exploring completes (handoff to planning)

Same as Example A with: `"phase": "exploring"`, `"status": "planning-needs-approach"`, `"next": "beo-plan"`, `"planning_mode": "unknown"`.

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
