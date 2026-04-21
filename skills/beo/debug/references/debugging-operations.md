# Debugging Operations

Operational playbook for `beo-debug`.

## 1. Known-Pattern Check

Use `learnings-read-protocol.md` for prior known patterns. If a known pattern matches, jump directly to the documented fix path.

## 2. Reproduction Flow

Run the exact failing command and capture output:

```bash
npm run build 2>&1 | tee /tmp/debug-output.txt
```

Then:
1. isolate the minimal repro
2. run it twice to distinguish deterministic vs flaky behavior
3. classify flaky tests separately

## 3. Diagnostic Flow

Use `diagnostic-checklist.md` in order:
1. source read
2. git blame
3. bead context
4. `CONTEXT.md` decision check
5. Agent Mail check
6. root-cause sentence

Do not proceed until the root cause fits in one sentence.

## 4. Fix Application

Heuristic: a fix is usually small if it touches about 2 files, takes about 15 minutes, and does not change user-facing behavior. Treat this as guidance, not a hard gate.

### Small Fix

Implement directly, then verify with the original failing command plus broader regression checks.

### Substantial Fix

Create a fix bead using the shared reactive-fix template. Use `--parent` only; do not use `--deps blocks:<closed-bead>`.

```bash
br create "Fix: <root cause summary> (ref: <original-bead-id>)" -t task --parent <EPIC_ID>
```

If the issue is a locked-decision violation, coordinate before silently changing behavior.

## 5. Resolution Reporting

Record the verified blocker, root cause, and minimal unblock in debug-owned reporting surfaces allowed by contract. If the investigation suggests a reusable learning or outdated shared guidance, return that evidence to the origin phase rather than writing learning artifacts from debug.

After debugging:

```bash
br label add <TASK_ID> -l debug_attempted
```

## 6. Blocker Protocol

For non-code blockers:
1. inspect dependency cycles, reservations, and waiting state
2. classify waiting vs genuinely blocked
3. use `message-templates.md` for `blocked-waiting` or `hard-blocker`
4. report once, then pause instead of spinning

## 7. Context-Budget Checkpoint

If context usage exceeds 65%, write canonical `STATE.json` and `HANDOFF.json`, then include:
- current debugging step
- root-cause hypothesis
- affected task IDs
