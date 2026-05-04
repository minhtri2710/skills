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
- Shared state/handoff fields allowed by `beo-reference -> skill-contract-common.md`.

## Hard stops
- Do not implement the fix unless ownership routes back through an execution owner.
- Do not redesign scope or decomposition.
- Do not present speculation as root cause.
- Do not include patch wording in diagnostic output; return proven cause and legal unblock owner/action only.
- Do not change `debug_return.return_to` by habit; override it only when canonical debug-return evidence proves the recorded return owner invalid.
- Do not authorize rollback or repair mutation from debug output; return rollback or repair evidence to the legal owner chosen by canonical state and pipeline doctrine. The legal owner for rollback of the current executing bead's mutation is `beo-execute`, bounded to that bead's declared file scope.

## Debug Return Card

```md
Finding:
Evidence checked:
Proof status: proven | inconclusive
Safe unblock action class: <see taxonomy below>
Return to: <owner per debug_return.return_to or canonical pipeline>
Return evidence: <facts needed by the receiving owner to act>
Authority note: display-only; canonical authority remains in the referenced state/artifact surface.
```

### Safe unblock action class taxonomy

| Class | Meaning |
| --- | --- |
| `retry_without_change` | the failure is transient or environmental; re-run without modifying artifacts |
| `apply_fix_within_scope` | the fix is contained within the current approved bead's declared file scope; route back to `beo-execute` only when the existing current `PASS_EXECUTE` execution set remains valid; review-created reactive-fix beads route to `beo-validate` |
| `expand_scope_to_beo_plan` | the fix requires files outside the current approved scope; a plan repair is needed before execution |
| `retry_with_corrected_input` | the failure is due to incorrect command arguments or missing input; re-issue with corrected input |
| `escalate_to_user` | the blocker requires a human decision (access, secret, external approval, ambiguous requirement) |

### FORBIDDEN in debug output

Debug output MUST NOT include:
- patch text, code changes, or implementation instructions
- a next-owner selection that bypasses `debug_return.return_to` without override evidence
- an approval grant, PASS_EXECUTE, or readiness verdict
- a rollback instruction (return rollback evidence to the legal executing owner instead)

## Allowed next owners
- `beo-execute`
- `beo-review`
- `beo-plan`
- `beo-validate`
- `beo-explore`
- `user`
- `beo-route` — only for exceptional owner-state resolution under canonical route doctrine.

## References
- `beo-reference -> operator-card.md` — read when reporting diagnostic findings.
- `beo-reference -> approval.md` — read when checking whether a fix remains inside approval.
- `beo-reference -> state.md` — read when recording debug return metadata.
- `beo-reference -> pipeline.md` — read when returning to a legal next owner.
- `references/diagnostic-checklist.md` — read when gathering non-normative diagnostic evidence.
