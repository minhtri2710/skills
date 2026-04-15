# Debugging Operations

Operational playbook for `beo-debug`. Load this file for exact known-pattern checks, reproduction commands, fix-bead handling, debug-note writes, blocker handling, or checkpoint mechanics.

## Table of Contents

- [1. Known-Pattern Check](#1-known-pattern-check)
- [2. Reproduction Flow](#2-reproduction-flow)
- [3. Diagnostic Flow](#3-diagnostic-flow)
- [4. Fix Application](#4-fix-application)
- [5. Learnings Capture](#5-learnings-capture)
- [6. Blocker Protocol](#6-blocker-protocol)
- [7. Context-Budget Checkpoint](#7-context-budget-checkpoint)

## 1. Known-Pattern Check

Use `beo-reference` → `references/learnings-read-protocol.md` as the canonical read-side workflow.

If a known pattern matches, jump directly to fix application using the documented resolution.

## 2. Reproduction Flow

Run the exact failing command verbatim and capture output:

```bash
npm run build 2>&1 | tee /tmp/debug-output.txt
# or equivalent failing command
```

Then:
1. Isolate the minimal repro.
2. Run twice to distinguish deterministic vs flaky behavior.
3. Classify flaky tests separately.

## 3. Diagnostic Flow

Use `diagnostic-checklist.md` for the ordered sub-checks:
1. source read
2. git blame
3. bead context
4. CONTEXT.md decision check
5. Agent Mail check
6. root-cause sentence

Do not proceed until you can state the root cause in one sentence.

## 4. Fix Application

A fix is **small** if it touches `<=2` files, takes less than 15 minutes, and does not change user-facing behavior. Everything else is **substantial** and requires a fix bead.

### Small Fix

Implement directly, then verify with the original failing command plus broader regression checks.

### Substantial Fix

Create a fix bead using the shared reactive-fix template. Per `pipeline-contracts.md` Fix Beads rules, use `--parent` only — do **not** use `--deps blocks:<closed-bead>`. Reference the affected bead in the description instead:

```bash
br create "Fix: <root cause summary> (ref: <original-bead-id>)" -t task --parent <EPIC_ID>
```

If the issue is a locked-decision violation, coordinate before silently changing behavior.

## 5. Learnings Capture

If this is a new failure pattern, append a debug note to:

```text
.beads/artifacts/<feature_slug>/debug-notes.md
```

If this reveals an outdated critical pattern, write a pattern-update note there.

After debugging, mark:

```bash
br label add <TASK_ID> -l debug_attempted
```

## 6. Blocker Protocol

For non-code blockers:
1. inspect dependency cycles / reservations / waiting status
2. classify waiting vs genuinely blocked
3. use `message-templates.md` for `blocked-waiting` or `hard-blocker`
4. report once, then pause instead of spinning

## 7. Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical `STATE.json` and `HANDOFF.json` shapes from `beo-reference` → `references/state-and-handoff-protocol.md`, then include the current debugging step, root-cause hypothesis, and affected task IDs.
