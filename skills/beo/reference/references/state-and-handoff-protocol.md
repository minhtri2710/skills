# State and Handoff Protocol

Canonical protocol for `.beads/STATE.json` and `.beads/HANDOFF.json`.

## Core Rule

- `STATE.json` is the normal adjacent-skill handoff.
- `HANDOFF.json` is the emergency checkpoint that survives context resets.
- Router reads `HANDOFF.json` first on resume.
- Other skills read `STATE.json` from the predecessor skill.

## Canonical STATE.json Schema

Every skill writes all 12 required fields:

```json
{
  "schema_version": 1,
  "phase": "<skill-name>",
  "status": "<canonical-routing-state>",
  "feature": "<epic-id>",
  "feature_slug": "<feature_slug>",
  "tasks": "<summary relevant to current phase>",
  "next": "beo-<next-skill>",
  "planning_mode": "single-phase",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "<current phase name or feature summary>"
}
```

### Optional extension fields

Use these only when needed:

```json
{
  "reason": "awaiting-planning-approval",
  "content": "planning approval is required before continuing",
  "origin_skill": "beo-review",
  "return_to": "beo-review",
  "reactive_fix": true
}
```

- `reason` — canonical routing or wait-state reason
- `content` — concise human-facing pause or handoff content
- `origin_skill` — skill that initiated a debug or reactive-fix transition
- `return_to` — skill to return to after resolution
- `reactive_fix` — `true` only for a review-origin reactive fix

Clear `origin_skill`, `return_to`, and `reactive_fix` after successful return. Preserve `reason` and `content` only while they still describe the current `next` target. Include these fields in `HANDOFF.json` when checkpointing if they are set.

### Field semantics

| Field | Meaning |
|---|---|
| `schema_version` | Always `1`; bump only for incompatible schema changes |
| `phase` | Skill that wrote the state, such as `"router"` or `"planning"` |
| `status` | Canonical routing or wait-state status |
| `feature` | Epic ID |
| `feature_slug` | Stable artifact-path identifier |
| `tasks` | Concise summary of current-phase task state |
| `next` | Direct next target: `beo-<skill>`, `user`, or `done` |
| `planning_mode` | `"single-phase"`, `"multi-phase"`, or `"unknown"` before approach is finalized |
| `has_phase_plan` | `true` only when active `.beads/artifacts/<feature>/phase-plan.md` exists |
| `current_phase` | Selected current phase number; use `1` for single-phase work |
| `total_phases` | Total count when known; `"unknown"` if not yet stable |
| `phase_name` | Human-readable current-phase name |

## Canonical HANDOFF.json Base Schema

All base fields below are required. `feature_name` is historical but still carries the immutable feature slug.

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

Use `[]` when there are no in-flight beads. Use `content: ""` when no extra content is needed.

## Planning-Aware HANDOFF.json Extension Fields

Include these when known:

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

Go-mode checkpoints may add:

```json
{
  "mode": "go"
}
```

Rules:
- Allow only `"go"` or field absence.
- Use `"go"` to resume the saved `skill` and `next` inside go mode instead of normal feature routing.
- Keep planning-aware fields at their normal meaning when `mode = "go"`.
- Do not invent additional mode values without updating this protocol.

## Optional Artifact Presence Map

Include `artifacts` only when artifact completeness materially improves resume safety:

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

Rules:
- Use booleans only.
- Treat `phase_contract` and `story_map` as current-phase artifacts.
- Do not treat `phase_plan: false` as an error; it is normal for single-phase work.

## When To Write HANDOFF.json

Write `HANDOFF.json` when:
- context usage exceeds 65%
- a long-running orchestration must pause cleanly
- the session must checkpoint before continuation

Do not write it for normal phase-to-phase progression when `STATE.json` is sufficient.

## What To Include In A Checkpoint

Include:
- completed sub-steps
- pending dimensions or checks
- active workers
- open blockers
- locked decisions already captured
- resume instructions
- planning mode or phase-selection state
- artifact completeness when relevant

Swarming may extend the top level, but the base schema must remain intact.

## Resume Protocol

When `HANDOFF.json` exists:

1. Read it before normal routing.
2. Verify it against the live graph and current files.
3. Load the saved skill.
4. Follow `next` and any supporting `reason` or `content`.

When planning-aware fields are present:
- Treat `planning_mode` as the source of truth unless live artifacts contradict it.
- If `has_phase_plan` is `true`, check whether `phase-plan.md` still exists.
- If `current_phase` is present, resume against that phase unless the live graph proves it already completed.
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
| `beo-swarm` | `"swarming"` | swarming or execution routing state from the routing table; `"needs-debugging"` or `"cancelled-needs-decision"` when redirecting to route | next required skill or action |
| `beo-execute` | `"executing"` | execution state; `"blocked-awaiting-user"` or `"blocked-external"` when paused; `"needs-debugging"` or `"cancelled-needs-decision"` when redirecting to route | next required skill or action |
| `beo-review` | `"reviewing"` | review result state; `"awaiting-uat"` when waiting for human UAT | `"beo-compound"` or other required next action |
| `beo-debug` | `"debugging"` | debugging state; `"debug-findings-ready"` or `"blocked-external"` when paused | origin skill via `return_to`, or `"beo-route"` for standalone |
| `beo-compound` | `"compounding"` | final post-review state from the routing table | next required skill or action |
| `beo-dream` | `"dream"` | consolidation state; `"dream-complete"` on finish | `"beo-route"` |
| `beo-author` | `"writing-skills"` | skill-creation state from the RED/GREEN/REFACTOR cycle | `"beo-route"` |
| `beo-onboard` | `"using-beo"` | onboarding state; `"onboarding-complete"` on finish | `"beo-route"` |

## Canonical Wait-State Statuses

When pausing for a human or external dependency, use one of these `status` values in `STATE.json`.

| Status | Skill That Sets It | Meaning | Resume Trigger |
|---|---|---|---|
| `awaiting-exploration-answer` | `beo-explore` | Exploring paused for user answer to a gray-area question | User provides the answer |
| `awaiting-planning-approval` | `beo-plan` | Multi-phase sequence needs user approval before validation | User approves or rejects the sequence |
| `awaiting-execution-approval` | `beo-validate` | Validation passed; waiting for explicit user approval to begin execution | User grants execution approval |
| `awaiting-uat` | `beo-review` | Automated review complete; waiting for human UAT walkthrough | User completes UAT confirmation |
| `blocked-awaiting-user` | `beo-execute` | All remaining work is blocked and requires a human decision | User provides direction on blockers |
| `blocked-external` | `beo-execute`, `beo-debug` | Blocked on infrastructure, permissions, or external service outside agent control | External dependency resolved |
| `debug-findings-ready` | `beo-debug` | Root cause identified or escalation limit reached; findings ready for user review | User reviews findings and provides direction |

Rules:
- Write the wait-state status to `STATE.json` before pausing.
- Router must match the wait-state status to decide whether to resume the paused skill or return to `user`.
- Do not advance past a wait state without the triggering event.
- On resume, the paused skill re-reads `STATE.json` and continues from saved progress.

## Examples

### STATE.json: single-phase planning handoff

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

### HANDOFF.json: single-phase checkpoint

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

### Variants

- Multi-phase handoff: set `"planning_mode": "multi-phase"`, `"has_phase_plan": true`, and the real `"total_phases"`.
- Go-mode checkpoint: add top-level `"mode": "go"`.
- Explore → plan handoff: set `"phase": "exploring"`, `"status": "planning-needs-approach"`, `"next": "beo-plan"`, and `"planning_mode": "unknown"`.

## Planning-Aware Field Transition Cleanup

When replanning changes planning mode, phase structure, or execution scope, refresh all planning-aware fields in both `STATE.json` and `HANDOFF.json` before handoff.

| Scenario | Fields to set | Artifacts to clean |
|----------|--------------|-------------------|
| Replan → single-phase | `planning_mode: "single-phase"`, `has_phase_plan: false`, `current_phase: 1`, `total_phases: 1`, `phase_name`: feature summary | Delete `phase-plan.md` |
| Replan within multi-phase | `has_phase_plan: true` (rewrite), `current_phase`: new number, `total_phases`: updated, `phase_name`: new name | Rewrite `phase-plan.md` |
| Phase advancement | Increment `current_phase`, update `phase_name`, keep `total_phases` current | Delete old `phase-contract.md` + `story-map.md` |

Hard rule: never leave stale `phase_name`, `current_phase`, or `has_phase_plan` values after replanning or phase advancement.

## Hard Rules

- Never skip `HANDOFF.json` if it exists.
- Never write non-canonical field names in the base schema of `STATE.json` or `HANDOFF.json`.
- Never omit required fields. `STATE.json` requires all 12 fields; `HANDOFF.json` requires all base-schema fields.
- Never delete `HANDOFF.json` before the resumed skill checkpoints safely.
- Never treat `phase-contract.md` or `story-map.md` as whole-feature artifacts when `planning_mode = "multi-phase"`.
- Never assume `has_phase_plan: false` means an error; it is valid for single-phase work.
- Never write a non-canonical `mode` value; `"go"` is the only documented extension.
