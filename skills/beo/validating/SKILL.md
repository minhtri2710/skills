---
name: beo-validating
description: >-
  Use after planning completes and before any implementation begins. Verifies
  that the current phase contract, story map, and bead graph are structurally
  sound, execution-ready, and aligned with locked decisions. Use for prompts
  like "validate the plan", "is this ready to build?", "check the bead graph",
  "verify execution readiness", or whenever there is doubt about whether the
  current phase is safe to execute. Do not use for post-implementation review
  (use beo-reviewing instead).
---

<HARD-GATE>
Onboarding — see `../reference/references/shared-hard-gates.md` § Onboarding Check.
</HARD-GATE>

> See `../reference/references/shared-hard-gates.md` § Shared References Convention.

# Beo Validating

## Overview

Validating is the gate between planning and execution.
Its job is to prove that the **current phase** is structurally sound before any code is written.

**Core principle:** catch plan failures before they become implementation failures.

If `phase-plan.md` exists, validation still applies to the **current phase only**. Whole-feature sequencing matters for context, but approval never expands into later phases.

## Communication Standard

All validation outputs (plan-checker findings, bead-reviewer findings, dimension failures) must follow `../reference/references/communication-standard.md`: plain language first, evidence with quotes or path:line, concrete failure scenario, and smallest fix.

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
A bead is underspecified if it lacks any of: concrete file scope, verification criteria, or a clear deliverable.
If only 1-2 beads are underspecified and all other beads pass the three-field check above, you may tighten those specs by restoring missing text that already exists verbatim in the bead package, story-map, or phase-contract — do not invent new scope or rewrite task boundaries — and then re-run validation. If the underspecified beads expose a larger decomposition problem (e.g., the story they belong to cannot be executed as described), route back to `beo-planning`.
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

<HARD-GATE>
When choosing the execution mode, if swarming (parallel worker execution) is under consideration, verify: (1) at least 3 independent ready tasks exist in the current phase, (2) no two tasks share write access to the same file, and (3) task dependencies do not create a serial chain that negates parallelism. If any condition fails, flag the plan for revision — swarming is not justified.
</HARD-GATE>

## Default Validation Loop

1. confirm current-phase artifacts and task beads exist
2. retrieve prior learnings and orient to the current phase
3. run the 8-dimension structural check
4. inspect graph health and bead quality
5. run spikes only where yes/no proof would change go / no-go
6. summarize readiness in human terms
7. get explicit user approval before execution

Load `references/validation-operations.md` when you need the exact checker flow, graph commands, spike mechanics, approval summary, Quick mode, or handoff procedure.

## Prerequisites

Confirm that all execution prerequisites are met: epic, task beads, and all required artifacts exist and are readable. See `references/validation-operations.md` Section 1 for the exact artifact checklist and read order.

## Current-Phase Orientation

Orient to the current phase before running the structural gate. Verify that current-phase artifacts, state metadata, and task graph all describe the same phase. See `references/validation-operations.md` Section 2 for the orientation procedure and summary format.

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

See `references/validation-operations.md` Section 3 (Failure Handling) for the repair-routing table and iteration limits. Do not keep patching a plan whose current phase no longer makes sense as a closed loop.
After repairing a failed dimension, re-run the relevant checks instead of assuming the plan now passes.
If failures reveal a broader decomposition problem rather than an isolated defect, route back to planning instead of continuing to patch in place.

## Graph Health and Bead Quality

Confirm graph integrity, story-to-bead coherence, and bead description quality. See `references/validation-operations.md` Section 4 for the exact graph-health procedure, and `references/bead-reviewer-prompt.md` for fresh-eyes bead review when complexity is high.

## Spikes for HIGH-Risk Work

Use spikes only when a yes/no proof would change whether this phase should proceed. Do not create ceremonial spikes for already-understood work. See `references/validation-operations.md` Section 5 for the exact create / record / result-handling sequence.

## Exit-State Readiness Review

Before approval, confirm that completing all stories and beads will achieve the phase exit state. See `references/plan-checker-prompt.md` Dimension 8 for the exact readiness questions. If any answer is no or uncertain, do not approve execution -- route back to the layer that must change.

Reject plans whose phase exit state is vague or non-observable, whose first story cannot explain why it must happen first, or whose bead-level "done" definitions do not trace cleanly to story outcomes.

## Approval Gate

Use the canonical approval rule from `../reference/references/approval-gates.md`.
Approval must be explicit and must apply to the **current phase** only.

When approval is granted:
- run `br label add <epic-id> -l approved`
- choose and explicitly state the next execution mode (`beo-executing` or `beo-swarming`)

When approval is rejected or withheld:
- do not proceed; route back to planning or exploring as needed

See `references/validation-operations.md` Section 7 for the full approval summary format, execution-mode decision rule, rejection procedure, and handoff steps.

## Quick Mode

For very small, low-risk work (Quick scope), use the Quick-validation shortcut in `references/validation-operations.md` Section 8.
Even in Quick mode, user approval is still required before any code is written.

## Handoff

After approval, choose and announce the execution mode, then write `.beads/STATE.json`. See `references/validation-operations.md` Section 8 (Normal Handoff) for the decision rule and state fields.

If later phases remain, say so explicitly. Validation approval for the current phase never means the whole feature is approved.

## Context Budget

Follow `../reference/references/shared-hard-gates.md` § Context Budget Protocol. Skill-specific checkpoint items: validation progress, and see `references/validation-operations.md` Section 8 for the full checkpoint procedure.

## Red Flags & Anti-Patterns

Do not rubber-stamp approval, skip decision coverage, or treat overlap and missing story linkage as minor issues. Validation must produce evidence, not vibes.
