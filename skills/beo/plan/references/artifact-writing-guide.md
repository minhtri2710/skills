# Artifact Writing Guide

Artifact write order, writing guidance, multi-phase approval, current-phase definition, and the high-stakes review.

## 1. Artifact Write Order

### Single-phase flow

1. `discovery.md` → 2. `approach.md` → 3. `plan.md` → 4. `phase-contract.md` → 5. `story-map.md` → 6. task beads

### Multi-phase flow

1. `discovery.md` → 2. `approach.md` → 3. `plan.md` → 4. `phase-plan.md` → 5. multi-phase approval → 6. `phase-contract.md` *(current phase)* → 7. `story-map.md` *(current phase)* → 8. task beads *(current phase)*

### Artifact roles

| Artifact | Role |
|----------|------|
| `discovery.md` | Implementation landscape and findings |
| `approach.md` | Chosen strategy, alternatives, risks |
| `plan.md` | Human-readable plan summary |
| `phase-plan.md` | Whole-feature sequencing (multi-phase only) |
| `phase-contract.md` | Current phase only |
| `story-map.md` | Current phase only |

Do not use `phase-contract.md` as a whole-feature artifact for multi-phase work.

## 2. Writing `approach.md`

Write to `.beads/artifacts/<feature_slug>/approach.md` using `approach-template.md`.

**Inputs:** CONTEXT.md, discovery findings, prior learnings/critical patterns, codebase constraints, external dependency findings.

**Must explain:**
- What the feature needs to make true
- What the codebase already provides
- What is missing or risky
- Recommended implementation strategy
- Alternatives considered
- Risk map
- Whether work is single-phase or multi-phase

### Self-check

- [ ] Approach described in practical language, not only abstract terms
- [ ] At least one rejected alternative named when meaningful alternatives exist
- [ ] Risk map usable by validating and execution
- [ ] Planning mode decision explicit and justified
- [ ] Relevant learnings actually applied, not just listed

If `approach.md` is weak, fix it first — do not compensate by overloading `plan.md`.

## 3. Writing `plan.md`

Write to `.beads/artifacts/<feature_slug>/plan.md` using `plan-template.md`.

Human-readable planning summary. Must remain readable even when `approach.md` and `phase-plan.md` hold more structured detail.

**Summarize:** feature goal, chosen direction, main risks, phase shape, current phase for validation, story/task shape at high level.

**Rules:**
- Keep readable for a human scanning quickly
- Do not duplicate every detail from `approach.md`
- Do not turn into a second `phase-plan.md`
- If multi-phase: summarize phase sequence briefly, point to `phase-plan.md`

## 4. Writing `phase-plan.md`

Only for `multi-phase` planning mode. Write to `.beads/artifacts/<feature_slug>/phase-plan.md` using `phase-plan-template.md`.

**Must answer:**
1. What the full feature makes true
2. Why one phase is not enough
3. What the 2-4 phases are
4. What becomes true after each phase
5. Why the order makes sense
6. Which phase to prepare now
7. What later phases intentionally defer

**Rules:**
- Every phase = real capability slice, not a work bucket
- Phase 1 should feel obviously first
- Later phases must be intentionally deferred, not vaguely implied
- If phase list grows past 4, reconsider feature framing

Do not create `phase-plan.md` for single-phase features.

## 5. Multi-Phase Planning Approval

Required before current phase handoff to validation. Approves: whole-feature phase sequence, selected current phase, intentional deferral of later phases. This is **not** the execution approval gate.

Use the canonical rule from `beo-reference` → `references/approval-gates.md`.

## 6. Writing Current-Phase Artifacts

After `approach.md` (and `phase-plan.md` if multi-phase), prepare the current phase.

### `phase-contract.md`

Write to `.beads/artifacts/<feature_slug>/phase-contract.md` using `phase-contract-template.md`. Describes the **current phase only**.

**Must define:** why this phase exists now, entry state, exit state, simplest demo story, what it unlocks, out of scope, pivot signals.

### `story-map.md`

Write to `.beads/artifacts/<feature_slug>/story-map.md` using `story-map-template.md`. Maps the **current phase only**.

**Must explain:** why each story exists, story ordering rationale, what each unlocks, how completion supports exit state.

Do not create beads until both files exist.

### Multi-phase current-phase rule

- `phase-contract.md` and `story-map.md` describe the selected current phase
- Task beads created for current phase only
- Do not pre-create beads for later phases

## 7. High-Stakes Multi-Perspective Check

Only for high-stakes features: multiple HIGH-risk components, core architecture changes, auth flows, data model changes, broad blast radius, external dependency risk.

Run a fresh isolated review pass with: approach.md, plan.md, phase-plan.md (if exists), phase-contract.md, story-map.md. Spawn a subagent only when the current runtime supports delegation for the session; otherwise perform the same narrowed pass locally.

**Prompt:**

> Review this planning package for blind spots:
> 1. Does the approach fit codebase reality?
> 2. If multi-phase, does the phase sequence make practical sense?
> 3. Does the current phase close a believable small loop?
> 4. Do the stories make sense in this order?
> 5. What is missing from the exit state?
> 6. Which story or task is too large, vague, or risky?
> 7. What would the team regret 6 months from now?

Iterate 1-2 rounds. Stop when changes become incremental.
