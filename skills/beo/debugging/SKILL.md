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
If `.beads/onboarding.json` is missing or stale, stop and load `beo-using-beo` before continuing.
</HARD-GATE>

# Beo Debugging

## Overview

Debugging resolves blockers and failures systematically.
Use it to classify the problem, reproduce it, isolate root cause, apply the right fix path, and capture the pattern.

**Core principle:** triage -> reproduce -> diagnose -> fix -> learn.
Do not guess.

## Hard Gates

<HARD-GATE>
If you cannot write a one-sentence root cause, you do not have the root cause yet. Do not proceed to Fix.
</HARD-GATE>

<HARD-GATE>
Do not skip reproduction just because the error message looks obvious.
If the failure cannot be reproduced directly, say so explicitly and treat that as part of diagnosis.
</HARD-GATE>

<HARD-GATE>
Substantial fixes belong in a fix bead that follows the shared reactive-fix template and normal execution path.
Do not smuggle major repair work through ad-hoc debugging edits.
</HARD-GATE>

## Default Debugging Loop

0. **read prior learnings** — use the canonical learnings-read protocol (`../reference/references/learnings-read-protocol.md`) before investigating. 30-40% of recurring failures are already documented. QMD/Obsidian first, flat-file fallback when unavailable.
1. classify the issue clearly
2. reproduce it or state why reproduction is not yet possible
3. diagnose until the root cause fits in one sentence
4. apply the right fix path
5. capture the pattern and route back cleanly

Use `references/debugging-operations.md` for the exact known-pattern check, reproduction flow, fix split, blocker handling, and checkpoint behavior.
Use `references/diagnostic-checklist.md` for the ordered sub-checks.
Use `references/message-templates.md` when reporting blockers or results to the orchestrator via Agent Mail.

## Triage and Diagnosis

The output of triage should be a one-line classification such as `[TYPE] in [component]: [symptom]`.
Then work through reproduction and diagnosis in order.

## Fix Path

Fix beads must still use the shared **Reactive Fix Bead Template** from `../reference/references/bead-description-templates.md`.

## Learn

After the fix path is clear or a blocker is confirmed, capture the pattern using the debug-note flow in `references/debugging-operations.md`, including the `debug_attempted` labeling rule.

## Escalation and Timeout

<HARD-GATE>
If you have spent more than 3 diagnostic cycles (reproduce → diagnose → attempt) without isolating the root cause, **stop and ask the user** for guidance. Do not keep spinning.
</HARD-GATE>

<HARD-GATE>
If the failure involves infrastructure, permissions, or external services you cannot inspect, report what you know and escalate immediately rather than guessing. Do not attempt workarounds for inaccessible systems.
</HARD-GATE>

- If a blocker remains unresolved after one rescue attempt, classify it as `needs_human` and pause the bead. Do not silently retry indefinitely.

## Handoff

After the fix is verified:
- if debugging was entered from `beo-executing`, route back to `beo-executing`
- if debugging was entered from `beo-reviewing`, route back to `beo-reviewing`
- if the issue remains ambiguous, report the blocker clearly and pause for user direction

For blocker-specific handling, use `references/debugging-operations.md`. Do not spin; report once, then pause.

---

## Context Budget

Use `references/debugging-operations.md` and `../reference/references/state-and-handoff-protocol.md` for canonical checkpoint behavior when context exceeds 65%.

---

## Red Flags & Anti-Patterns

- **Fixing symptoms, not root cause**: If the same error recurs after the fix, root cause was not found. Return to Step 3.
- **Skipping reproduction**: Diagnosing from the error message alone leads to wrong fixes. Always reproduce first.
- **Not checking critical-patterns.md first**: Always check `.beads/learnings/critical-patterns.md` before investigating from scratch — 30-40% of recurring failures are already documented.
- **Committing a fix without running verification**: The fix must be verified with the exact failing command, not a different test.
- **Decision violation silently patched**: Violating a `CONTEXT.md` decision to make a test pass propagates the violation downstream. Report and align first.
- **Calling the first visible error the root cause**: Walk the error chain; the first error you see is often a symptom of a deeper cause.
- **Treating blocked work as "someone else's problem"**: Classify and report blockers cleanly instead of ignoring them.

See `references/debugging-operations.md` for the full diagnostic checklist and fix-path details.

---
