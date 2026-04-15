# Diagnostic Checklist

## Table of Contents

- [3a. Read Relevant Source Files](#3a-read-relevant-source-files)
- [3b. Check Git Blame for Recent Changes](#3b-check-git-blame-for-recent-changes)
- [3c. Check Bead Context](#3c-check-bead-context)
- [3d. Check CONTEXT.md for Decision Violations](#3d-check-contextmd-for-decision-violations)
- [3e. Check Agent Mail for Related Blockers](#3e-check-agent-mail-for-related-blockers)
- [3f. Narrow to Root Cause](#3f-narrow-to-root-cause)
- [Quick Reference Table](#quick-reference-table)

---

## 3a. Read Relevant Source Files

1. Use your content search tool to find files containing `<error symbol or function>` in `src/` (e.g., `*.ts` files).
2. Read the implicated files.

Do not read the entire codebase. Read exactly the files implicated by the error output.

## 3b. Check Git Blame for Recent Changes

```bash
git log --oneline -20          # What changed recently?
git blame <file> -L <line>,<line>  # Who changed the failing line?
git diff HEAD~3 -- <file>      # What did it look like before?
```

If a recent commit introduced the failure, the fix is likely reverting or adjusting that change.

## 3c. Check Bead Context

```bash
br show <bead-id>   # What was this bead supposed to do?
```

Verify: does the failure indicate the bead was implemented against the wrong spec, or that it was implemented correctly but the spec was wrong?

## 3d. Check CONTEXT.md for Decision Violations

Read `.beads/artifacts/<feature_slug>/CONTEXT.md` with your file reading tool.

Ask: was a locked decision (D1, D2...) violated by the implementation? Decision violations are a frequent root cause -- the code does something "reasonable" that was explicitly excluded.

## 3e. Check Agent Mail for Related Blockers

If Agent Mail is available (a swarm is active and the mail session was initialized):

```bash
br mail fetch-inbox --project "<project-root-path>" --agent "<agent-name>"
```

Another worker may have already reported the same issue or conflict. Avoid duplicate debugging.

If Agent Mail is **not** available (solo mode, no swarm, or mail initialization failed), use the solo-debug-mode fallback from `message-templates.md`:

```bash
br comments add <TASK_ID> --no-daemon --message "[DEBUG NOTE] <one-sentence root cause and status>"
```

## 3f. Narrow to Root Cause

After checks 3a-3e, write a one-sentence root cause:

> Root cause: `<file>:<line>` -- `<what is wrong and why>`

If you cannot write this sentence, you do not have the root cause yet. Do not proceed to Fix.

## Flaky Test Diagnosis

When a failure is intermittent rather than deterministic:

1. rerun the exact failing test multiple times before changing code
2. check for shared mutable state, test ordering assumptions, timers, retries, and environment-sensitive setup
3. compare pass vs fail output to identify what actually changes between runs
4. treat "cannot reproduce twice in a row" as missing evidence, not a fix

| Common flaky-test causes |
|---|
| leaked global state between tests |
| async work not awaited |
| timeouts that are too tight for CI variance |
| race conditions around filesystem, network mocks, or background workers |
| dependence on wall-clock time, locale, or machine-specific environment |

---

## Quick Reference Table

| Situation | First action |
|---|---|
| Build fails | `git log --oneline -10` -- check recent changes |
| Test fails | Run test verbatim, capture exact assertion output |
| Flaky test | Run 5x -- if intermittent, check shared state/ordering |
| Runtime crash | Read stack trace top-to-bottom, find first line in your code |
| Integration error | Check env vars, then API response body (not just status code) |
| Worker stuck | Check bead deps with `bv`, then Agent Mail for conflicts |
| Recurring issue | Check `.beads/critical-patterns.md` first |
