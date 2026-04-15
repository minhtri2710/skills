---
name: beo-debugging
description: >-
  Use when a bead is blocked or when a build, test, runtime, integration, or
  worker-execution failure needs root-cause analysis. Also use when the user
  asks why something is failing, stuck, flaky, blocked, or repeatedly
  regressing. Do not use for planning ambiguity or scope-shaping (use
  beo-exploring), unrouted or undecomposed work (use beo-router),
  post-implementation quality checks (use beo-reviewing), or cross-feature
  learnings consolidation (use beo-dream).
---

<HARD-GATE>
Onboarding — see `../reference/references/shared-hard-gates.md` § Onboarding Check.
</HARD-GATE>

# Beo Debugging

## Overview

Debugging resolves blockers and failures systematically.
Classify the problem, reproduce it, isolate root cause, apply the right fix path, and capture the pattern.

> See `../reference/references/shared-hard-gates.md` § Shared References Convention.

**Core principle:** triage -> reproduce -> diagnose -> fix -> learn.
Do not guess.

## Hard Gates

<HARD-GATE>
If you cannot write a one-sentence root cause that names the specific component, condition, and failure mechanism, you do not have the root cause. Do not proceed to Fix.
A valid root cause sentence follows the pattern: "[Component] fails when [condition] because [mechanism]."
</HARD-GATE>

<HARD-GATE>
Do not skip reproduction because the error message looks obvious.
If the failure cannot be reproduced directly, state that explicitly and treat it as part of diagnosis.
</HARD-GATE>

<HARD-GATE>
After applying a fix, verify it with the exact failing command or reproduction path from diagnosis.
Do not treat a different test or a clean build as proof the original failure is resolved.
</HARD-GATE>

<HARD-GATE>
Fixes that change more than one file, alter public interfaces, or require test updates belong in a fix bead that follows the shared reactive-fix template and normal execution path.
Do not route multi-file or interface-changing repair work through ad-hoc debugging edits.
Single-file fixes that do not alter public interfaces or require test updates may be applied directly within the debugging session, except when debugging was entered from `beo-reviewing` — review-found defects must go through fix beads per reviewing's routing rules.
</HARD-GATE>

## Default Debugging Loop

0. **read prior learnings** — use the canonical learnings-read protocol (`../reference/references/learnings-read-protocol.md`) before investigating. 30-40% of recurring failures are already documented. QMD/Obsidian first, flat-file fallback when unavailable.
1. classify the issue clearly
2. reproduce it or state why reproduction is not yet possible
3. diagnose until the root cause fits in one sentence
4. apply the right fix path
5. capture the pattern and route back cleanly

| File | Use for |
|---|---|
| `references/debugging-operations.md` | Known-pattern check, reproduction flow, fix split, blocker handling, and checkpoint behavior |
| `references/diagnostic-checklist.md` | Ordered diagnostic sub-checks |
| `references/message-templates.md` | Agent Mail blocker and result reporting |

## Triage and Diagnosis

Output triage as one line: `[TYPE] in [component]: [symptom]`.
Then run reproduction and diagnosis in order.

## Fix Path

Fix beads must still use the shared **Reactive Fix Bead Template** from `../reference/references/bead-description-templates.md`.

## Learn

After the fix path is clear or a blocker is confirmed, capture the pattern with the debug-note flow in `references/debugging-operations.md`, including the `debug_attempted` labeling rule.

## Escalation and Timeout

<HARD-GATE>
If you have spent more than 3 diagnostic cycles (reproduce → diagnose → attempt) without isolating the root cause, **stop and ask the user** for guidance. Do not keep spinning.
</HARD-GATE>

<HARD-GATE>
If the failure involves infrastructure, permissions, or external services you cannot inspect, report what you know and escalate immediately rather than guessing. Do not attempt workarounds for inaccessible systems.
</HARD-GATE>

- If a blocker remains unresolved after one rescue attempt, leave the bead in `blocked` status with a comment documenting the blocker details, then pause and report to the user for direction. Do not silently retry indefinitely.

## Handoff

After debugging resolves the root cause and the fix is verified, route based on origin:

| Origin | Route |
|--------|-------|
| `beo-executing` (worker hit a blocker) | Route back to `beo-executing` to resume the execution loop |
| `beo-reviewing` (review found a defect) | Route back to `beo-reviewing` to continue the review cycle |
| `beo-swarming` (worker blocker during swarm) | Return findings to the swarm orchestrator via the worker’s blocker comment; the coordinator decides whether to unblock, reassign, or escalate |
| `beo-router` (standalone debugging session) | Hand back to `beo-router` with findings in STATE.json so router can re-route |
| Direct user invocation | If a direct fix was applied, summarize what changed and ask for user confirmation before further routing. Otherwise, present findings and recommended fix to the user; do not auto-route without user confirmation |

If the issue remains unresolved after escalation, report the blocker clearly and pause for user direction. Do not spin; report once, then pause.

For blocker-specific handling details, see `references/debugging-operations.md`.

---

## Context Budget

Follow `../reference/references/shared-hard-gates.md` § Context Budget Protocol. Skill-specific checkpoint: see `references/debugging-operations.md` for the full procedure.

---

## Red Flags & Anti-Patterns

- Fixing symptoms instead of root cause — if the error recurs, return to diagnosis
- Skipping reproduction — never diagnose from the error message alone
- Not checking `critical-patterns.md` first — 30-40% of recurring failures are already documented
- Committing fixes without verification using the exact failing command
- Calling the first visible error the root cause — walk the full error chain

---
