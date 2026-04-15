---
name: beo-debug
description: |
  Use when a bead is blocked or when a build, test, runtime, integration, or worker-execution failure needs root-cause analysis. Triggers: "why is this failing?", "it's stuck", "flaky test", "blocked", "keeps regressing", or any failure that needs systematic diagnosis. Systematic debugging: diagnose, root-cause, minimal-fix, verify. MUST NOT guess at fixes, apply fixes without root cause, expand scope beyond the blocker, or perform quality review. Do not use for planning ambiguity (use beo-explore), post-implementation quality checks (use beo-review), or cross-feature learnings (use beo-dream).
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-debug

## Overview
Unblock failed or stalled work by isolating root cause, applying the smallest viable fix, and proving the blocker is resolved. **Core principle: minimal-intervention troubleshooting with explicit return to the invoking skill.**

## Boundary Rules
- **MUST NOT** route to skills — owned by `beo-route`.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** verify plans — owned by `beo-validate`.
- **MUST NOT** orchestrate workers — owned by `beo-swarm`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.
- **MUST NOT** consolidate learnings — owned by `beo-dream`.

## Hard Gates
> **HARD-GATE: ORIGIN-TRACKING** — Debug always records which skill invoked it and returns to that origin skill using `the STATE.json/HANDOFF.json protocol` (`beo-reference` → `references/state-and-handoff-protocol.md`). Never hand off to an unrelated skill.

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
- **Inputs** — Blocked bead or failure context, origin skill identifier, error evidence, relevant artifacts under `.beads/artifacts/<feature_slug>/`, and current state records per `the STATE.json/HANDOFF.json protocol` (`beo-reference` → `references/state-and-handoff-protocol.md`).
- **Outputs** — Root cause diagnosis, minimal applied fix or escalation, verification evidence, bead comment update, status transition per `the bead lifecycle states` (`beo-reference` → `references/status-mapping.md`), and return handoff to the invoking skill.

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
> Write `HANDOFF.json` for every skill transition (`beo-reference` → `references/pipeline-contracts.md`). Transitions follow the pipeline: route → explore → plan → validate → (execute | swarm → execute) → review → compound.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Debug performs feature work beyond the blocker.
- Debug does not record or preserve the origin skill.
- Debug skips verification or records no evidence.
- Debug changes bead scope instead of unblocking it.
- Debug loops for more than three diagnostic cycles without root cause or escalation.
- Debug duplicates shared-reference content instead of citing canonical documents.
