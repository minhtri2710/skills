# Artifact Writing Guide

Operational reference for artifact write order, approach/plan/phase-plan writing, multi-phase approval, current-phase definition, and the high-stakes multi-perspective review.

## 4. Artifact Write Order

Use the correct artifact order for the selected planning mode.

### Single-phase flow

1. `discovery.md`
2. `approach.md`
3. `plan.md`
4. `phase-contract.md`
5. `story-map.md`
6. task beads

### Multi-phase flow

1. `discovery.md`
2. `approach.md`
3. `plan.md`
4. `phase-plan.md`
5. multi-phase planning approval
6. `phase-contract.md` *(current phase only)*
7. `story-map.md` *(current phase only)*
8. task beads for the current phase only

### Artifact roles

- `discovery.md` = implementation landscape and findings
- `approach.md` = chosen strategy, alternatives, and risks
- `plan.md` = human-readable plan summary
- `phase-plan.md` = whole-feature sequencing for multi-phase work
- `phase-contract.md` = current phase only
- `story-map.md` = current phase only

Do not use `phase-contract.md` as a whole-feature artifact when the feature is clearly multi-phase.

## 5. Writing `approach.md`

Write `approach.md` to:

```bash
# .beads/artifacts/<feature_slug>/approach.md
```

Use `approach-template.md`.

Inputs:

- `CONTEXT.md`
- discovery findings
- prior learnings / critical patterns
- codebase constraints
- external dependency findings, if any

`approach.md` must explain:

- what the feature needs to make true
- what the codebase already provides
- what is missing or risky
- the recommended implementation strategy
- alternatives considered
- the risk map
- whether the work stays single-phase or becomes multi-phase

### Self-check for `approach.md`

Before continuing, verify:

- the recommended approach is described in practical language, not only abstract architecture terms
- at least one rejected alternative is named when meaningful alternatives exist
- the risk map is usable by validating and execution
- the planning mode decision is explicit and justified
- relevant learnings are actually applied, not just listed

If `approach.md` is weak, do not compensate by overloading `plan.md`. Fix `approach.md` first.

## 6. Writing `plan.md`

Write `plan.md` to:

```bash
# .beads/artifacts/<feature_slug>/plan.md
```

Use `plan-template.md` as the starting structure.

`plan.md` is the human-readable planning summary.

It should remain readable even when `approach.md` and `phase-plan.md` hold more structured detail.

### `plan.md` should summarize

- the feature goal
- the chosen implementation direction
- the main risks
- the phase shape
- the current phase that will be validated next
- the story/task shape at a high level

### Rules for `plan.md`

- keep it readable by a human scanning the plan quickly
- do not duplicate every detail from `approach.md`
- do not turn it into a second `phase-plan.md`
- if multi-phase, summarize the phase sequence briefly and point to `phase-plan.md` for full detail

## 7. Writing `phase-plan.md`

Only write `phase-plan.md` when planning mode is `multi-phase`.

Write to:

```bash
# .beads/artifacts/<feature_slug>/phase-plan.md
```

Use `phase-plan-template.md`.

`phase-plan.md` must answer:

1. what the full feature makes true
2. why one phase is not enough
3. what the 2-4 meaningful phases are
4. what becomes true after each phase
5. why the order makes sense
6. which phase should be prepared now
7. what later phases are intentionally deferred

### Rules for a good `phase-plan.md`

- every phase must describe a real capability slice, not a work bucket
- Phase 1 should feel obviously first
- later phases must be intentionally deferred, not vaguely implied
- the selected current phase must be a believable first / next slice
- if the phase list grows past 4, reconsider the feature framing

Do not create `phase-plan.md` for a feature that still fits a single clean closed loop.

## 8. Multi-Phase Planning Approval

If planning mode is `multi-phase`, explicit user approval is required before the current phase is handed off for validation.

This approval is for:
- the whole-feature phase sequence
- the selected current phase
- the intentional deferral of later phases

It is **not** the execution approval gate.

Use the canonical rule from `../../reference/references/approval-gates.md`.

## 9. Writing Current-Phase Artifacts

After `approach.md` is complete — and after `phase-plan.md` if multi-phase — prepare the current phase for execution.

### Write `phase-contract.md`

Use `phase-contract-template.md` and write to:

```bash
# .beads/artifacts/<feature_slug>/phase-contract.md
```

`phase-contract.md` always describes the **current phase only**.

It must define:

- why this phase exists now
- the entry state
- the exit state
- the simplest demo story
- what this phase unlocks next
- what is explicitly out of scope
- what signals would force a pivot

### Write `story-map.md`

Use `story-map-template.md` and write to:

```bash
# .beads/artifacts/<feature_slug>/story-map.md
```

`story-map.md` maps the **current phase only**.

It must explain:

- why each story exists
- why the stories appear in this order
- what each story unlocks
- how story completion supports the phase exit state

Do not create beads until both files exist.

### Current-phase rule for multi-phase work

If planning mode is `multi-phase`:

- `phase-contract.md` must describe the selected current phase
- `story-map.md` must map the selected current phase
- task beads must be created for the selected current phase only

Do not pre-create execution beads for later phases in this planning model.

## 10. High-Stakes Multi-Perspective Check

Only for high-stakes features:

- multiple HIGH-risk components
- core architecture changes
- auth flows
- data model changes
- broad blast radius
- external dependency risk that could invalidate the approach

Spawn a fresh subagent with:

- `approach.md`
- `plan.md`
- `phase-plan.md` if it exists
- `phase-contract.md`
- `story-map.md`

Prompt:

> Review this planning package for blind spots:
> 1. Does the chosen approach fit the codebase reality?
> 2. If this is multi-phase, does the phase sequence make practical sense?
> 3. Does the current phase close a believable small loop?
> 4. Do the stories make sense in this order?
> 5. What is missing from the exit state?
> 6. Which story or task is too large, vague, or risky?
> 7. What would the team regret 6 months from now?

Iterate 1-2 rounds. Stop when changes become incremental.
