---
name: beo-debugging
description: >-
  Use when a bead is blocked or when a build, test, runtime, integration, or
  worker-execution failure needs root-cause analysis. Also use when the user
  asks why something is failing, stuck, flaky, blocked, or repeatedly
  regressing. Reproduces the issue, diagnoses the cause, applies a direct fix or
  fix bead, and records reusable debug notes instead of guessing.
---

# Debugging

Load `beo-reference` for knowledge-store protocol (`../reference/references/knowledge-store.md`).

Resolve blockers and failures systematically. Do not guess. Triage first, then reproduce, then diagnose, then fix.

---

## Step 1: Triage: Classify the Issue

Classify before investigating. Misclassifying wastes time.

| Type | Signals |
|---|---|
| **Build failure** | Compilation error, type error, missing module, bundler failure |
| **Test failure** | Assertion mismatch, snapshot diff, timeout, flaky intermittent pass |
| **Runtime error** | Crash, uncaught exception, segfault, undefined behavior |
| **Integration failure** | HTTP 4xx/5xx, env variable missing, API schema mismatch, auth error |
| **Blocker** | Stuck agent, circular bead dependency, conflicting file reservations |

**Output of triage:** A one-line classification: `[TYPE] in [component]: [symptom]`

Example: `Build failure in packages/sdk: TS2345 type mismatch in auth.ts`

---

## Step 2: Reproduce: Isolate the Failure

Load `references/debugging-operations.md` for the exact known-pattern check, reproduction flow, and blocker-vs-failure mechanics.

---

## Step 3: Diagnose: Root Cause Analysis

Work through the diagnostic sequence from `references/debugging-operations.md` and `references/diagnostic-checklist.md` in order.

<HARD-GATE>
If you cannot write a one-sentence root cause, you do not have the root cause yet. Do not proceed to Fix.
</HARD-GATE>

---

## Step 4: Fix: Apply and Verify

Load `references/debugging-operations.md` for the exact small-fix vs substantial-fix split, fix-bead creation rule, verification sequence, and blocker reporting expectations.

Fix beads must still use the shared **Reactive Fix Bead Template** from `../reference/references/bead-description-templates.md`.

---

## Step 5: Learn: Capture the Pattern

Load `references/debugging-operations.md` for the exact debug-note write pattern, pattern-update flow, and `debug_attempted` labeling rule.

---

## Blocker-Specific Protocol

Load `references/debugging-operations.md` for the exact blocker protocol and message-template usage. Do not spin; report once, then pause.

---

## Red Flags

- **Fixing symptoms, not root cause**: If the same error recurs after the fix, root cause was not found. Return to Step 3.
- **Skipping reproduction**: Diagnosing from the error message alone leads to wrong fixes. Always reproduce first.
- **Not checking critical-patterns.md**: Teams report that 30-40% of recurring failures are already documented. Check before investigating.
- **Committing a fix without running verification**: The fix must be verified with the exact failing command, not a different test.
- **Decision violation silently patched**: Violating a CONTEXT.md decision to make a test pass propagates the violation downstream. Always report and align first.

---

## Context Budget

If context usage exceeds 65%, use `references/debugging-operations.md` together with `../reference/references/state-and-handoff-protocol.md` for the canonical checkpoint behavior.

---

## Quick Reference

See `references/diagnostic-checklist.md` for the full quick reference table mapping situations to first actions.
