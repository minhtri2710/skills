---
name: beo-validating
description: >-
  Use after planning completes and before any implementation begins. Verifies
  that the current phase contract, story map, and bead graph are structurally
  sound, execution-ready, and aligned with locked decisions. Use for prompts
  like "validate the plan", "is this ready to build?", "check the bead graph",
  "verify execution readiness", or whenever there is doubt about whether the
  current phase is safe to execute.
---

# Beo Validating

## Overview

Validating is the gate between planning and execution.
Its job is to prove that the **current phase** is structurally sound before any code is written.

**Core principle:** catch plan failures before they become implementation failures.

If `phase-plan.md` exists, validation still applies to the **current phase only**. Whole-feature sequencing matters for context, but approval never expands into later phases.

## Default Validation Loop

1. confirm current-phase artifacts and task beads exist
2. retrieve prior learnings and orient to the current phase
3. run the 8-dimension structural check
4. inspect graph health and bead quality
5. run spikes only where yes/no proof would change go / no-go
6. summarize readiness in human terms
7. get explicit user approval before execution

Load `references/validation-operations.md` when you need the exact checker flow, graph commands, spike mechanics, approval summary, lightweight mode, or handoff procedure.

## Hard Gates

<HARD-GATE>
No code is written until validation succeeds and the user explicitly approves execution.
Do not infer approval from silence, tone, or partial agreement.
</HARD-GATE>

<HARD-GATE>
If tasks do not exist, or `phase-contract.md` / `story-map.md` are genuinely missing, do not guess the plan into existence here. Route back to `beo-planning`.
</HARD-GATE>

<HARD-GATE>
If any bead description is empty or underspecified, fail validation. This is a structural failure, not an optional quality note.
If only 1-2 beads are thin and the phase shape is otherwise sound, you may tighten those specs and re-run validation. If the thin specs expose a larger decomposition problem, route back to `beo-planning`.
</HARD-GATE>

<HARD-GATE>
Validation approves the current phase only. If planning mode is `multi-phase`, current-phase approval does not approve later phases or the whole feature.
</HARD-GATE>

<HARD-GATE>
After approval, do not stop at "the current phase is approved." Validation is not complete until you also choose and announce the next execution mode (`beo-executing` or `beo-swarming`) for the approved current-phase work.
</HARD-GATE>

<HARD-GATE>
A spike NO result invalidates the current phase plan. Do not proceed to approval.
</HARD-GATE>

## Prerequisites

Before validating, confirm:
- the epic exists
- task beads exist
- `CONTEXT.md` exists
- `approach.md` exists
- `plan.md` exists
- `phase-contract.md` exists
- `story-map.md` exists
- `phase-plan.md` is read when present

Use `references/validation-operations.md` for the exact checks and read order.

## Current-Phase Orientation

Before running the structural gate:
- orient to the current phase
- understand how it fits the larger whole-feature plan when `phase-plan.md` exists
- verify that current-phase artifacts, state metadata, and task graph all describe the same phase

Use the orientation summary format in `references/validation-operations.md` when needed.

## The 8-Dimension Structural Check

Run validation across these 8 dimensions:

1. **Phase contract clarity**
2. **Story coverage and ordering**
3. **Decision coverage**
4. **Dependency correctness**
5. **File scope isolation**
6. **Context budget**
7. **Verification completeness**
8. **Exit-state completeness and risk alignment**

Use `references/validation-operations.md` and `references/plan-checker-prompt.md` for the exact checker procedure and full PASS / FAIL detail.

### Repair Rule

- 1-2 structural failures -> repair in place, then re-run validation
- 3+ failures -> route back to `beo-planning`
- after 3 validation iterations with any FAIL still present -> stop and escalate to the user

Do not keep patching a plan whose current phase no longer makes sense as a closed loop.

## Graph Health and Bead Quality

Validation must also confirm:
- story order and bead dependencies agree
- every story maps to at least one bead
- every bead belongs to the current phase
- no future-phase work is smuggled into the current execution set
- every bead is specific enough for a fresh worker

Use `references/validation-operations.md` for the exact graph-health procedure and `references/bead-reviewer-prompt.md` for fresh-eyes bead review when complexity is high.

## Spikes for HIGH-Risk Work

Use spikes only when the approach is unproven, depends on external systems, has hard performance requirements, or otherwise relies on hope.

A spike is appropriate only when a yes/no proof would change whether this phase should proceed.
Do not create ceremonial spikes for already-understood work.

Use `references/validation-operations.md` for the exact create / record / result-handling sequence.

## Exit-State Readiness Review

Before approval, ask these questions explicitly:

1. if all stories reach done, does the phase exit state hold?
2. if all beads close successfully, will the stories actually be done?
3. is the demo story now credible?
4. if `phase-plan.md` exists, does this current phase still make sense inside the larger sequence?

If any answer is no or not sure, do not approve execution. Route back to the layer that must change.

## Approval Gate

Use the canonical approval rule from `../reference/references/approval-gates.md`.
Approval must be explicit and must apply to the **current phase** only.

When approval is granted:
- mark the epic approved
- inspect ready current-phase work immediately if the mode is not already obvious
- choose and explicitly state the next execution mode (`beo-executing` or `beo-swarming`)
- if exact parallelism is still unknown after inspection, default to `beo-executing` unless there is clear evidence of 3+ independent ready tracks
- write fresh state with the chosen next skill
- do not end the approval summary without a concrete next-skill statement

When approval is rejected or withheld:
- do not proceed
- remove implicit approval assumptions
- route back to planning or exploring as needed

Use `references/validation-operations.md` for the exact approval summary and handoff procedure.

## Lightweight Mode

For very small, low-risk work, use the lightweight-validation shortcut in `references/validation-operations.md`.
Even in lightweight mode, user approval is still required before any code is written.

## Handoff

After approval:
1. choose and explicitly announce execution mode from the ready current-phase work
2. if independence/count is unclear, inspect it now; if it is still unknown, choose `beo-executing` by default unless clear evidence supports `beo-swarming`
3. state the concrete next skill in the approval summary itself, not only in later state-writing
4. write `.beads/STATE.md` using `../reference/references/state-and-handoff-protocol.md`
5. include planning-aware fields when known
6. announce the next skill

If later phases remain, say so explicitly. Validation approval for the current phase never means the whole feature is approved.

## Context Budget

If context usage exceeds 65%, write `.beads/HANDOFF.json` using `../reference/references/state-and-handoff-protocol.md`, then checkpoint:
- validation progress
- planning-aware fields
- artifact completeness
- any spike status or unresolved failures

## Red Flags & Anti-Patterns

See `references/validating-guardrails.md` for the full tables.
