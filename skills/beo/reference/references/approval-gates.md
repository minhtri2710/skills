# Approval Gates

## Contents

- [Why This Exists](#why-this-exists)
- [Approval-Requiring Moments](#approval-requiring-moments)
- [Approval Presentation Guidance](#approval-presentation-guidance)
- [Planning-Specific Guidance](#planning-specific-guidance)
- [Rejection / Withheld Approval Handling](#rejection--withheld-approval-handling)
- [Hard Rules](#hard-rules)

Canonical wording and protocol for human approval requirements in the beo pipeline.

## Why This Exists

Several beo skills require explicit user confirmation before proceeding with an irreversible or shared-state-changing action.

This file centralizes those approval rules so all beo skills ask for approval consistently and stop in the same places.

## Approval-Requiring Moments

### 1. Planning Approval for Multi-Phase Work

If planning determines that a feature is **multi-phase**, user approval is required for the whole-feature phase sequence before the current phase is treated as execution-ready.

This approval confirms:

- the feature should be understood as multiple phases
- the phase sequence is believable
- the selected current phase is the right first / next slice
- later phases are intentionally deferred, not forgotten

Canonical rule:

> For multi-phase work, user approval is required for the whole-feature phase sequence and current-phase selection before treating the current phase as ready for validation handoff.

This gate applies in `beo-planning` when `phase-plan.md` exists.

#### Canonical approval prompt for multi-phase planning

```text
Whole-feature phase plan is ready.

- Total phases: <N>
- Current phase to prepare now: <phase name>
- Why this phase is first / next: <reason>
- Later phases intentionally deferred: <summary>

Approve this phase sequence and current phase selection before validation?
```

### 2. Validation Approval

Before any execution begins, user approval is required.

Canonical rule:

> User approval is required before any code is written. This is non-negotiable.

Use this gate in `beo-validating` before setting the `approved` label.

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

#### Canonical approval prompt for validation

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

During `beo-reviewing`, human review is required.

Canonical rule:

> Human review is required. Walk through the feature with the user.

For locked decisions and exit-state checks, ask one thing at a time and wait for confirmation.

Use this gate even if all automated review passes are clean.

### 4. Critical Pattern Promotion

Before appending to `.beads/critical-patterns.md`, explicit user approval is required.

Canonical rule:

> Never auto-append to `critical-patterns.md`; explicit user approval is mandatory.

Use this gate in `beo-compounding` and `beo-dream`.

### 5. Ambiguous Dream Consolidation Decisions

If `beo-dream` finds multiple plausible owners for a candidate learning, it must ask the user to choose between merge / create / skip outcomes.

Do not silently choose a target file when ownership is ambiguous.

### 6. Partial or Deferred Review Outcomes

If `beo-reviewing` encounters blocked, failed, or partial tasks before closure, it must report them and obtain explicit user direction before proceeding, deferring, or re-planning.

Do not close the feature or proceed to compounding while the outcome is still ambiguous.

## Approval Presentation Guidance

When asking for approval:

- summarize what is being approved
- summarize relevant unresolved concerns
- make the next step explicit
- ask for a clear yes / no or a structured choice

Approval prompts should be concrete enough that the user can understand the consequence of saying yes.

Prefer:

- what becomes allowed if approved
- what remains deferred if approved
- what will happen next

Avoid vague prompts like:

- "Looks good?"
- "Can I continue?"
- "Should I proceed?"

## Planning-Specific Guidance

### Single-phase planning

A separate planning approval is not required just because planning artifacts exist.

For single-phase work, planning normally hands off to `beo-validating`, and the key irreversible approval remains the validation gate before execution.

### Multi-phase planning

For multi-phase work, planning approval is required because choosing the whole-feature sequence and the current phase changes the shape of all downstream work.

That approval does **not** replace validation approval.

It comes earlier and answers a different question:

- planning approval = "Is this the right feature sequence and current phase to prepare?"
- validation approval = "Is this current phase safe to execute now?"

## Rejection / Withheld Approval Handling

If the user rejects or withholds approval:

- stop at the current skill
- do not silently proceed
- route back to the artifact or decision layer that must change
- summarize what must be revised before asking again

### Typical route-back patterns

- rejects phase sequencing -> revise `phase-plan.md`
- rejects current phase choice -> revise `phase-plan.md` and current-phase artifacts
- rejects current-phase readiness -> revise `phase-contract.md`, `story-map.md`, bead descriptions, or broader planning
- rejects UAT outcome -> create or route to fix work, then re-run review
- rejects critical promotion -> keep the learning local; do not promote it

## Hard Rules

- Never infer approval from silence.
- Never convert a required approval into an implicit default.
- Never write shared artifacts gated by approval without first asking.
- Never continue execution if the user rejects or withholds approval.
- Never treat current-phase approval as whole-feature approval when planning mode is `multi-phase`.
- Never skip the validation approval gate just because the user already approved the phase sequence.
