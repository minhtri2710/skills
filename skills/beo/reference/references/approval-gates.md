# Approval Gates

Canonical wording and protocol for human approval requirements in the beo pipeline.

## Why This Exists

Several beo skills require explicit user confirmation before proceeding with an irreversible or shared-state-changing action. This file centralizes those approval rules.

## Approval-Requiring Moments

### 1. Validation Approval

Before any execution begins, user approval is required.

Canonical rule:

> User approval is required before any code is written. This is non-negotiable.

Use this gate in `beo-validating` before setting the `approved` label.

### 2. Review / UAT Confirmation

During `beo-reviewing`, human review is required.

Canonical rule:

> Human review is required. Walk through the feature with the user.

For locked decisions and exit-state checks, ask one thing at a time and wait for confirmation.

### 3. Critical Pattern Promotion

Before appending to `.beads/critical-patterns.md`, explicit user approval is required.

Canonical rule:

> Never auto-append to `critical-patterns.md`; explicit user approval is mandatory.

Use this gate in `beo-compounding` and `beo-dream`.

### 4. Ambiguous Dream Consolidation Decisions

If `beo-dream` finds multiple plausible owners for a candidate learning, it must ask the user to choose between merge/create/skip outcomes.

### 5. Partial or Deferred Review Outcomes

If `beo-reviewing` encounters blocked, failed, or partial tasks before closure, it must report them and obtain explicit user direction before proceeding, deferring, or re-planning.

## Approval Presentation Guidance

When asking for approval:
- summarize what is being approved
- summarize relevant unresolved concerns
- make the next step explicit
- ask for a clear yes/no or a structured choice

## Hard Rules

- Never infer approval from silence.
- Never convert a required approval into an implicit default.
- Never write shared artifacts gated by approval without first asking.
- Never continue execution if the user rejects or withholds approval.
