---
name: beo-debugging
description: Systematic debugging for blocked workers, test failures, build errors, runtime crashes, and integration issues. Invoked standalone ("debug this error") or by other skills (reviewing spawns debugger on UAT failure, executing invokes it on blocker). Reads .beads/critical-patterns.md to avoid re-solving known issues. Writes debug notes that compounding can later capture.
---

# Debugging

Load `beo-reference` for knowledge-store protocol (`references/knowledge-store.md`).

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

**Check known patterns first**, before any investigation:

```bash
# Primary: search flat-file learnings
cat .beads/critical-patterns.md 2>/dev/null | grep -i "<keyword>"
grep -rl "<keyword>" .beads/learnings/ 2>/dev/null

# Optional enhancement: if QMD is available, also run semantic search
qmd search "<keyword from classification>" --json 2>/dev/null
```

If a known pattern matches → jump directly to Step 4 (Fix), using the documented resolution.

**If not a known pattern, reproduce it:**

1. Run the exact command that failed. Do not paraphrase it:
   ```bash
   # Whatever CI/worker ran, run it verbatim
   npm run build 2>&1 | tee /tmp/debug-output.txt
   # or: pytest tests/specific_test.py -v 2>&1 | tee /tmp/debug-output.txt
   ```

2. Capture error output verbatim. Do not summarize. The exact line numbers and messages matter.

3. Identify the minimal reproduction case:
   - Can you trigger the failure with one file change? One command?
   - Does it fail in isolation or only in combination with other changes?
   - Is it environment-specific (CI only, one machine only)?

4. Confirm reproducibility:
   - Run twice. If intermittent → classify as **flaky test**, not a deterministic failure.
   - Flaky tests require a different approach: check for shared state, race conditions, or test ordering.

---

## Step 3: Diagnose: Root Cause Analysis

Work through the 6 diagnostic sub-checks in order (3a-3f). Stop when you find the cause.

Load `references/diagnostic-checklist.md` for the full checklist with commands. Summary:

- **3a.** Read relevant source files (only files implicated by error)
- **3b.** Check git blame for recent changes
- **3c.** Check bead context (`br show <bead-id>`)
- **3d.** Check CONTEXT.md for decision violations
- **3e.** Check Agent Mail for related blockers
- **3f.** Narrow to root cause -- write a one-sentence root cause sentence

If you cannot write a root cause sentence after 3a-3f, you do not have the root cause yet. Do not proceed to Fix.

---

## Step 4: Fix: Apply and Verify

### Fix size determines approach

**Small fix** (1–3 files, obvious change, low risk):
- Implement directly
- Commit: `fix(<bead-id>): <what was wrong and what was changed>`
- Run verification immediately:
  ```bash
  npm run build && npm test   # or language equivalent
  ```

**Substantial fix** (cross-cutting change, logic redesign, multiple files):
- Create a fix bead before implementing (must use both --parent and --blocks per pipeline-contracts.md):
  ```bash
  br create "Fix: <root cause summary>" -t task --parent <EPIC_ID> --blocks <original-bead-id>
  ```
- Implement in the fix bead's scope
- Run verification: the fix bead's acceptance criteria must pass

### Fix Bead Description Requirements

When creating a fix bead, the description must contain at minimum:

1. **File scope**: exact file paths to modify
2. **What to fix**: specific problem and root cause
3. **Verification criteria**: runnable checks that prove the fix works

Fix beads are exempt from the story context block requirement (they are reactive, not planned). But they must still have enough context for `beo-executing` to dispatch without guessing.

If the fix is trivial (single-line change with obvious verification), inline the fix directly instead of creating a bead.

**Decision violation** (CONTEXT.md decision ignored):
- Do not silently fix. The decision may need to be revisited.
- Report via Agent Mail before implementing. Send message using the **decision-violation** template from `references/message-templates.md`.
- Wait for response or implement the conservative fix (honor the locked decision)

### Verify the fix

Run the exact command that originally failed. It must pass cleanly, not "mostly pass":

```bash
# Rerun original failing command
<original-failing-command>

# Also run broader test suite to check for regressions
npm test   # or equivalent
```

If verification fails → do not report success. Return to Step 3 with new information.

### Report the fix via Agent Mail

Send message using the **fix-applied** template from `references/message-templates.md`.

---

## Step 5: Learn: Capture the Pattern

### If this is a new failure pattern

Write a debug note for compounding to capture:

```bash
# Write to the feature's artifact directory
cat >> .beads/artifacts/<feature-name>/debug-notes.md << 'EOF'
## Debug Note: <date> -- <classification>

**Root cause**: <root cause sentence>
**Trigger**: <what causes this>
**Fix**: <what resolves it>
**Signal**: <how to recognize this pattern in future>
EOF
```

Tell the user: "New failure pattern found. Run `beo-compounding` skill to promote this to `.beads/learnings/`."

### If this matches a known pattern from critical-patterns.md

Verify the existing advice still works:
- Did following the documented resolution solve it?
- If yes: no action needed
- If the documented resolution failed or is outdated: note the discrepancy in `debug-notes.md` and flag it for compounding to update:

```bash
cat >> .beads/artifacts/<feature-name>/debug-notes.md << 'EOF'
## Pattern Update Needed: <date> -- <pattern name>

**Existing pattern**: <name from critical-patterns.md>
**Issue**: Resolution no longer accurate: <what changed>
**Proposed update**: <corrected resolution>
EOF
```

Tell the user: "Pattern '<name>' needs updating in critical-patterns.md. Run `beo-compounding` to review and update."

### Mark Debug Attempted

After completing debugging (whether the fix succeeded or not), mark the task so the router can distinguish "debugging attempted" from "not yet attempted":

```bash
br label add <TASK_ID> -l debug_attempted
```

This label is read by the router (Rows 2-3 of the routing table) to distinguish between tasks that need debugging and tasks that have already been debugged but remain blocked.

---

## Blocker-Specific Protocol

When a worker is stuck (cannot make progress, not a code error):

1. Check bead dependencies: `bv --robot-insights --format json 2>/dev/null | jq '.Cycles'`
2. Check file reservations via Agent Mail for conflicts
3. Determine: is this **waiting for another worker** or **genuinely blocked**?

**Waiting for another worker** → send message using the **blocked-waiting** template from `references/message-templates.md`, then yield.

**Genuinely blocked** (circular dep, impossible constraint, conflicting decisions) → send message using the **hard-blocker** template from `references/message-templates.md`.

Do not spin. One report, then pause and let the orchestrator escalate.

---

## Red Flags

- **Fixing symptoms, not root cause**: If the same error recurs after the fix, root cause was not found. Return to Step 3.
- **Skipping reproduction**: Diagnosing from the error message alone leads to wrong fixes. Always reproduce first.
- **Not checking critical-patterns.md**: Teams report that 30-40% of recurring failures are already documented. Check before investigating.
- **Committing a fix without running verification**: The fix must be verified with the exact failing command, not a different test.
- **Decision violation silently patched**: Violating a CONTEXT.md decision to make a test pass propagates the violation downstream. Always report and align first.

---

## Context Budget

If context usage exceeds 65%, write HANDOFF.json before pausing:

```json
{
  "schema_version": 1,
  "phase": "debugging",
  "skill": "beo-debugging",
  "feature": "<epic-id>",
  "feature_name": "<feature-name>",
  "next_action": "Continue debugging from Step <N>. Root cause hypothesis: <hypothesis>.",
  "in_flight_beads": ["<task-being-debugged>"],
  "timestamp": "<iso8601>"
}
```

Also update STATE.md with canonical header before pausing.

---

## Quick Reference

See `references/diagnostic-checklist.md` for the full quick reference table mapping situations to first actions.
