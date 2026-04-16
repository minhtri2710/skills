---
name: beo-debug
description: |
  Use when a specific blocker or failure prevents execution from proceeding and the cause is not obvious enough for a local retry. Diagnoses root cause, applies the minimal viable fix, verifies resolution, and returns control to the invoking skill. Do not use for requirements ambiguity (use beo-explore), general quality review (use beo-review), cross-feature pattern analysis (use beo-dream), or when execute can resolve via simple retry.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-debug

## Overview
**Atomic purpose: diagnose a specific failure's root cause and apply the minimal targeted fix to unblock execution.** Diagnose and minimally unblock a specific failure, then return to the invoking skill. **Core principle: minimal-intervention troubleshooting with explicit return to origin.**

## Boundary Rules
- **MUST NOT** perform independent state detection or free-form routing — owned by `beo-route`. May emit canonical handoff to the next allowed pipeline skill when exit conditions are met.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** verify plans — owned by `beo-validate`.
- **MUST NOT** orchestrate workers — owned by `beo-swarm`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.
- **MUST NOT** consolidate learnings — owned by `beo-dream`.

## Hard Gates
> **HARD-GATE: ORIGIN-TRACKING** — Debug always records which skill invoked it and returns based on the state uncovered during debugging using `the STATE.json/HANDOFF.json protocol` (`beo-reference` → `references/state-and-handoff-protocol.md`). Default: return to the invoking skill. If debugging reveals a plan defect, route to `beo-plan`. If resolution requires a substantial fix bead, route to `beo-execute`. If a blocker is resolved during an active review loop, `beo-review` resumes.

> **HARD-GATE: MINIMAL-INTERVENTION** — Debug fixes the specific blocker only. It does not refactor, optimize, or expand scope beyond what is required to unblock.

> **HARD-GATE: VERIFICATION-REQUIRED** — Every fix must be verified before marking the issue resolved. No unverifiable “should work now” outcomes are allowed.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Debug Loop
1. **Diagnose**: Read blocked bead description, error messages, bead comments, and relevant code or artifacts. Use `references/diagnostic-checklist.md` to classify the issue: build, test, runtime, integration, worker-execution, or environment.
2. **Root Cause**: Isolate the specific cause and document what failed, why it failed, and which component owns the failure.
3. **Fix**: Apply the minimal fix. If the issue is structural rather than local, prepare the correct escalation back-edge per the pipeline transition rules (`beo-reference` → `references/pipeline-contracts.md`).
4. **Verify**: Re-run the failing verification or the narrowest proof of resolution. Record evidence in a bead comment using the exact `br comments add <ID> --no-daemon -c "..."` form required by repo policy.

### Reference Files
| File | Purpose |
|------|---------|
| `references/debugging-operations.md` | Canonical debug workflow, escalation handling, and resolution mechanics. |
| `references/diagnostic-checklist.md` | Systematic checklist for root-cause isolation across supported failure classes. |
| `references/message-templates.md` | Standard messaging patterns for blocker reporting, updates, and resolution handoffs. |

## Inputs and Outputs
- **Inputs** — Invoking skill identifier, blocked bead or failure evidence/logs, relevant code/artifacts, current execution/review state.
- **Outputs** — Root-cause statement, minimal applied fix or evidence-based escalation target, verification evidence, bead comment/status update, return-to-origin handoff.

## Decision Rubrics
- **Fix vs Escalate** — If root cause is within bead scope and resolvable quickly with a local change, fix directly. If root cause is structural, missing dependency, wrong approach, or plan error, escalate to the appropriate skill.
- **Return Target** — Always return to the invoking skill. Execute returns to execute, swarm returns to swarm, route returns to route, and so on.
- **Shared Failure** — If the issue matches a failure class in `standard failure recovery (`beo-reference` → `references/failure-recovery.md`)`, follow that recovery path. If not, diagnose it fresh and record the new pattern locally.
- **Verification Scope** — Prefer the narrowest verification that proves the blocker is gone, but never skip the exact failing check when that is the necessary evidence.

## Special Rules
- After verification, update bead state and handoff artifacts using `the STATE.json/HANDOFF.json protocol` (`beo-reference` → `references/state-and-handoff-protocol.md`).
- State transitions must align with `the bead lifecycle states` (`beo-reference` → `references/status-mapping.md`).
- If debug uncovers plan-level defects, do not silently repair scope; route back through the proper pipeline edge.
- Every failure mode recovers via `standard failure recovery (`beo-reference` → `references/failure-recovery.md`)`.
- Debug should not exceed three diagnostic cycles without a documented root-cause hypothesis or escalation decision.

## Handoff
> Return to the invoking skill using origin-tracking once the blocker is resolved or a bounded debugging report is produced. Write `STATE.json` for the normal return handoff, and reserve `HANDOFF.json` for emergency checkpoint or low-context resume scenarios.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Debug performs feature work beyond the blocker.
- Debug does not record or preserve the origin skill.
- Debug skips verification or records no evidence.
- Debug changes bead scope instead of unblocking it.
- Debug loops for more than three diagnostic cycles without root cause or escalation.
- Debug duplicates shared-reference content instead of citing canonical documents.
