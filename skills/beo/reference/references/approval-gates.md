# Approval Gates

Canonical wording and protocol for human approval requirements in the beo pipeline.

## Required Gates

### 1. Planning Approval for Multi-Phase Work

If planning determines that a feature is **multi-phase**, get user approval for the whole-feature phase sequence before treating the current phase as execution-ready.

This approval confirms:

- the feature should be understood as multiple phases
- the phase sequence is believable
- the selected current phase is the right first / next slice
- later phases are intentionally deferred, not forgotten

Canonical rule:

> For multi-phase work, user approval is required for the whole-feature phase sequence and current-phase selection before treating the current phase as ready for validation handoff.

Apply this gate in `beo-plan` when `phase-plan.md` exists.

Prompt:

```text
Whole-feature phase plan is ready.

- Total phases: <N>
- Current phase to prepare now: <phase name>
- Why this phase is first / next: <reason>
- Later phases intentionally deferred: <summary>

Approve this phase sequence and current phase selection before validation?
```

### 1a. CONTEXT.md Approval (Go Mode Only)

In go mode, get user approval of `CONTEXT.md` after exploring and before planning.

Canonical rule:

> In go mode, present `CONTEXT.md` and obtain explicit user approval before invoking planning.

Apply this gate only in `beo-route` when go mode is active.

See `beo-route` → `references/go-mode.md` for the full go-mode gate sequence.

### 2. Validation Approval

Canonical rule:

> User approval is required before any code is written. This is non-negotiable.

Use this gate in `beo-validate` before setting the `approved` label.

#### Validation semantics by planning mode

##### Single-phase
Validation approval means:
- the current phase is execution-ready
- the current phase also represents the full planned execution scope

##### Multi-phase
Validation approval means:
- the selected current phase is execution-ready
- approval applies to the current phase only
- later phases remain deferred
- current-phase approval must never be interpreted as approval for the whole feature

Prompt:

```text
Current phase validation is complete.

- Planning mode: <single-phase | multi-phase>
- Current phase: <phase number / name>
- Stories: <count>
- Tasks: <count>
- Main risks: <summary>

Approve execution for this current phase?
```

### 3. Review / UAT Confirmation

During `beo-review`, request human confirmation only when the accepted exit state, locked intent, or repo policy requires explicit user-facing UAT.

Canonical rule:

> Human UAT is conditional, not automatic. Ask for it when user confirmation is needed to judge intent match or user-visible acceptance.

When UAT is required, walk through the relevant locked decisions and exit-state checks one thing at a time and wait for confirmation.

### 4. Critical Pattern Promotion

Before writing to `.beads/critical-patterns.md`, explicit user approval is required.

Canonical rule:

> Never auto-write to `critical-patterns.md`; explicit user approval is mandatory.

Use this gate in `beo-compound` and `beo-dream`.

### 5. Ambiguous Dream Consolidation Decisions

If `beo-dream` finds multiple plausible owners for a candidate learning, ask the user to choose merge / create / skip.

### 6. Partial or Deferred Review Outcomes

If `beo-review` encounters blocked, failed, or partial tasks before closure, report them and get explicit user direction before proceeding, deferring, or re-planning.

## Asking For Approval

- summarize what is being approved
- summarize unresolved concerns
- state what becomes allowed if approved
- state what remains deferred if approved
- state the next step
- ask for a clear yes/no or bounded choice

Avoid vague prompts such as "Looks good?" or "Can I continue?"

## Rejection / Withheld Approval Handling

If the user rejects or withholds approval:

- stop at the current skill
- do not silently proceed
- route back to the artifact or decision layer that must change
- summarize what must be revised before asking again

Typical route-backs:

1. rejects phase sequencing -> revise `phase-plan.md`
2. rejects current phase choice -> revise `phase-plan.md` and current-phase artifacts
3. rejects current-phase readiness -> revise `phase-contract.md`, `story-map.md`, bead descriptions, or broader planning
4. rejects UAT outcome -> create or route to fix work, then re-run review
5. rejects critical promotion -> keep the learning local; do not promote it

## Hard Rules

- Never infer approval from silence.
- Never convert a required approval into an implicit default.
- Never write shared artifacts gated by approval without first asking.
- Never continue execution if the user rejects or withholds approval.
- Never require separate planning approval for single-phase work.
- Never treat current-phase approval as whole-feature approval when planning mode is `multi-phase`.
- Never skip the validation approval gate just because the user already approved the phase sequence.

> **See also:** `pipeline-contracts.md` → Label Lifecycle for the `approved` label back-edge removal rule.

## Approved Label Ownership

| Skill | Action | When |
|-------|--------|------|
| `beo-validate` | Adds `approved` via `br label add <EPIC_ID> -l approved` | After user grants execution approval |
| `beo-plan` | Removes `approved` via `br label remove <EPIC_ID> -l approved` | During replanning cleanup when phase structure or scope changes |
| `beo-execute` | Removes `approved` via `br label remove <EPIC_ID> -l approved` | When execution discovers a scope or intent change and routes back to planning |
| `beo-review` | Removes `approved` via `br label remove <EPIC_ID> -l approved` | When verdict is `fix` or `reject` and work routes backward |
| `beo-route` | Reads `approved` label to determine routing | Never adds or removes |

On normal completion, the `approved` label remains on the closed epic as historical state.
