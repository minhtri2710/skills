# Diagnostic Checklist

Use in order. Do not move to the fix until you can write a one-sentence root cause.

## 1. Read The Implicated Source

1. Search for the failing symbol, function, or file in the real source roots.
2. Read only the implicated files.

Do not read the whole codebase. Follow the error trail.

## 2. Check Recent Change History

```bash
git log --oneline -20
git blame <file> -L <line>,<line>
git diff HEAD~3 -- <file>
```

If the failure came from a recent change, start there before inventing new theories.

## 3. Check The Bead Contract

```bash
br show <bead-id>
```

Ask:
- was the bead implemented against the wrong spec?
- or was the spec itself wrong?

## 4. Check Locked Decisions

Read `.beads/artifacts/<feature_slug>/CONTEXT.md`.

Ask whether the implementation violated a locked decision. Many bugs are locally reasonable but globally forbidden.

## 5. Check Coordination History

If Agent Mail is active, read recent coordination history using the APIs in `beo-reference` → `references/agent-mail-coordination.md` before duplicating work.

If Agent Mail is not active, use the solo fallback from `message-templates.md`:

```bash
br comments add <TASK_ID> --no-daemon --message "Debug report: <root cause or current blocker>. Verification: <command/result>. Next step: <fix applied | needs decision>."
```

## 6. Write The Root-Cause Sentence

Write:

> Root cause: `<file>:<line>` -- `<what is wrong and why>`

If you cannot write that sentence, you do not have the root cause yet.

## Flaky Test Branch

When the failure is intermittent:
1. rerun the exact failing test multiple times before changing code
2. check shared mutable state, ordering assumptions, timers, retries, and environment-sensitive setup
3. compare pass and fail output to isolate what changes
4. treat "cannot reproduce twice in a row" as missing evidence, not a fix

Common flaky-test causes:
- leaked global state between tests
- async work not awaited
- timeouts too tight for CI variance
- races around filesystem, mocks, or background workers
- dependence on wall-clock time, locale, or machine-specific environment

## Quick Reference

| Situation | First move |
| --- | --- |
| Build fails | `git log --oneline -10` |
| Test fails | rerun the exact test and capture the assertion output |
| Flaky test | rerun at least 5 times, then inspect shared state and ordering |
| Runtime crash | read the stack trace top-down and stop at the first line in your code |
| Integration error | check env vars, then inspect the full API response body |
| Worker stuck | check bead deps in `bv`, then coordination history |
| Recurring issue | check `.beads/critical-patterns.md` first |
