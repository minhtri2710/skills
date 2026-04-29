---
name: beo-debug
description: |
  Prove one blocker root cause. Use when progress is blocked by unproven root cause or root-cause analysis is requested. Do not use when scope or decomposition needs redesign.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: degraded
      reason: Helpful for bead context, but exact failure evidence can still allow diagnosis.
    - id: beads-viewer
      kind: command
      command: bv
      missing_effect: degraded
      reason: Helpful for read-only inspection, but not required when exact failing artifacts are already known.
---
# beo-debug

## Purpose
Prove one blocker root cause.

## Primary owned decision
Establish a single root cause and return the smallest safe unblock path.

## Ownership predicate
- Progress is blocked by an unproven failure, diagnostic uncertainty, or explicit root-cause request.
- Evidence is needed before planning, execution, or reactive fix can proceed safely.
- The work is diagnosis, not scope redesign or implementation delivery.
- A bounded proof can unblock the current owner.

## Writable surfaces
- Diagnostic notes and state/handoff fields needed to return proven root cause.
- Shared `STATE/HANDOFF` surfaces under the common contract baseline.

## Hard stops
- Do not implement the fix unless ownership routes back through an execution owner.
- Do not redesign scope or decomposition.
- Do not present speculation as root cause.
- Do not include patch wording in diagnostic output; return proven cause and legal unblock owner/action only.

## Output card

```md
Finding:
Evidence checked:
Proof status: proven | inconclusive
Safe unblock:
Return evidence:
Authority note: This output is valid only when emitted by `beo-debug`. It proves diagnosis only and does not authorize mutation.
```

## Allowed next owners
- `beo-execute`
- `beo-swarm`
- `beo-review`
- `beo-plan`
- `beo-validate`
- `beo-explore`
- `user`
- `beo-route` — only when owner state is missing, stale, contradictory, or colliding.

## References
- `beo-reference -> operator-card.md` — read when reporting diagnostic findings.
- `beo-reference -> approval.md` — read when checking whether a fix remains inside approval.
- `beo-reference -> state.md` — read when recording debug return metadata.
- `beo-reference -> pipeline.md` — read when returning to a legal next owner.
- `references/diagnostic-checklist.md` — read when gathering non-normative diagnostic evidence.
