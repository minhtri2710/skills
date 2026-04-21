# Failure Recovery

Shared recovery rules for failures that cross skill boundaries.

## Shared Failure Classes

### `br` unavailable

- record the exact command and error
- do not infer graph state from memory or stale artifacts
- report that beo cannot continue safely without `br`
- ask whether to restore the tool, inspect install state, or pause

### `bv` unavailable

- continue only if the current skill has a safe `br`-only fallback
- otherwise stop and surface the missing graph capability
- do not fabricate graph-health conclusions

### Agent Mail or reservation system unavailable

- in solo or non-swarm work, continue and note the limitation
- in swarm work, stop parallel dispatch, preserve state, and degrade or ask
- do not leave ambiguous reservations unresolved

### State file malformed

- treat malformed `.beads/STATE.json` or `.beads/HANDOFF.json` as untrusted
- reconstruct from live graph state and canonical artifacts
- preserve the malformed file unless canonical recovery replaces it
- state which file failed and which source of truth replaced it

### Artifact write failure

- do not claim phase advancement
- surface the failing path and underlying error
- keep routing at the last confirmed safe state

### Resume corruption

- if resume artifacts, graph state, and conversation disagree, treat resume as corrupted
- prefer live graph state and canonical artifacts over stale checkpoint text
- summarize the contradiction before continuing

## Recovery Rule

When a shared failure class triggers:

1. Stop making irreversible state changes.
2. Name the failed dependency or artifact explicitly.
3. State the safest fallback or route-back option.
4. Checkpoint only with data you trust.
