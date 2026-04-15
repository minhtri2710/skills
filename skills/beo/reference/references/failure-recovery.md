# Failure Recovery

Canonical recovery guidance for cross-skill failures that are not specific to one execution mode. Keep skill-local blocker logic in local references; use this file for shared recovery classes only.

## Shared Failure Classes

### `br` unavailable

1. Confirm the exact command and error output.
2. Do not guess graph state from memory or stale artifacts.
3. Report that beo cannot safely continue without `br`.
4. Ask whether to restore the tool, inspect PATH/install state, or pause the pipeline.

### `bv` unavailable

1. Continue only if the current skill can safely fall back to `br`-only checks.
2. If the skill requires graph analytics or dependency inspection that `br` alone cannot replace, stop and surface the limitation.
3. Do not fabricate graph-health conclusions without tool evidence.

### Agent Mail or reservation system unavailable

1. If the current skill is in solo or non-swarm mode, continue with local bookkeeping and note that Agent Mail is not expected.
2. If swarm coordination is required, stop parallel dispatch, preserve current state, and either downgrade to a safe non-swarm path or ask how to proceed.
3. Do not leave ambiguous reservations unaddressed.

### State file malformed

1. Treat malformed `.beads/STATE.json` or `.beads/HANDOFF.json` as untrusted input.
2. Prefer reconstruction from live graph state plus canonical artifacts.
3. Preserve the malformed file for inspection unless a canonical recovery flow explicitly replaces it.
4. State which file is malformed and which source of truth you used instead.

### Artifact write failure

1. Do not claim the phase advanced if the canonical artifact was not written successfully.
2. Surface the failing path and underlying filesystem or tool error.
3. Keep routing at the last confirmed safe state until the write succeeds.

### Resume corruption

1. If resume artifacts, graph state, and conversation disagree, treat the resume as corrupted.
2. Prefer live graph state and canonical artifacts over stale checkpoint text.
3. Summarize the contradiction before continuing so the user can confirm the recovery path.

## Recovery Rule

When a shared failure class triggers:

1. Stop making irreversible state changes.
2. Name the failed dependency or artifact explicitly.
3. State the safest fallback or route-back option.
4. Checkpoint only with data you trust.
