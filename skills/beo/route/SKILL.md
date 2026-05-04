---
name: beo-route
description: |
  Select exactly one beo owner. Use when owner state is missing, invalid, contradictory, or colliding. Do not use when exactly one non-route owner predicate is true.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: degraded
      reason: Helpful for live bead context, but some routing decisions can proceed from artifacts and state.
    - id: beads-viewer
      kind: command
      command: bv
      missing_effect: degraded
      reason: Helpful for read-only inspection, but not required for every route decision.
---
# beo-route

## Purpose
Select exactly one beo owner.

## Primary owned decision
Resolve missing, invalid, contradictory, or colliding owner state into one next owner.

## Default routing posture

Preserve the current valid non-route owner by default.

`beo-route` is an exception-resolution owner, not a normal pipeline hop. Use it
only when owner state is missing, stale, contradictory, colliding, or when no
exactly-one non-route owner predicate is live.

Do not re-route merely to reconfirm a valid owner.

## Ownership predicate
- Current owner state is missing, stale, contradictory, or colliding.
- User intent conflicts with state, handoff, approval, or live artifact evidence.
- Multiple owner predicates appear true or no non-route owner predicate is true.
- The user explicitly asks to debug a failure and no current owner already validly owns that diagnostic work.
- Zero, multiple, stale, or contradictory non-route owner predicates require owner selection.

## Writable surfaces
- Route evidence and owner fields in `STATE.json`.
- Write `HANDOFF.json` only on pause, transfer, or when session context is approaching capacity and state must persist before compaction — not for routine routing decisions.
- No feature artifact content except route metadata explicitly owned by canonical state doctrine.

> Related canonical references: `beo-reference -> pipeline.md` for legal transitions and `beo-reference -> state.md` for route evidence fields.
> Locally owned here:
> - Select exactly one owner.
> - Resolve owner collision precedence.
> - Suppress unnecessary re-routing.
> - Treat handoff and cached state as advisory when live artifacts contradict them.

## Collision precedence matrix

When multiple non-route owner predicates appear true, use this table. First matching row wins.

| Collision condition | Route to | Precedence reason |
| --- | --- | --- |
| `debug_return` set and `debug_result` present | per `debug_return.return_to` | consume debug result before any other routing |
| Root cause unproven and progress blocked | `beo-debug` | debug must prove root cause before execution or re-plan can proceed |
| Requirements contradicted or unlocked after planning began | `beo-explore` | broken contract; re-lock before plan or execution |
| Contract-bearing plan content changed after existing approval | `beo-plan` | approval is stale; plan must be repaired before re-approval |
| Approval stale but plan and scope unchanged | `beo-validate` | freshness-only renewal; no plan repair needed |
| Both plan-stale and approval-stale predicates match | `beo-plan` | most upstream unsatisfied gate wins; plan before approval |
| Execution selection exists but bead graph diverges from `br` | `beo-plan` | bead graph must be repaired before validate can re-approve |
| Review verdict = fix, scope still correct | `beo-validate` | reactive-fix beads require a new `PASS_EXECUTE`; route to `beo-validate`, which must produce the approval and execution set before `beo-execute` |
| Review verdict = reject, design failure (requirements still valid) | `beo-plan` | design or implementation was wrong; requirements re-locking is not needed |
| Review verdict = reject, requirements invalid or contradicted | `beo-explore` | requirements failure; re-lock before plan or execution |
| Handoff present but stale and exactly one live-artifact owner predicate matches | that matching legal owner | stale handoff is advisory; live artifacts are canonical |
| Handoff present but stale and no single live-artifact owner predicate matches | `user` | route cannot select exactly one owner without a live evidence anchor |
| Multiple active feature candidates in state | `user` | operator must select exactly one active feature before routing |
| User defers or cancels active feature | `user` after state close evidence is recorded | abandonment is an operator decision; state must clear approval/readiness mirrors before another feature becomes active |
| Historical feature is explicitly reactivated | exactly one legal owner from live artifacts, otherwise `beo-route` remains active | historical artifacts become active only after state points to the slug again |
| No active feature and explicit new-feature intake evidence is present | `beo-explore` | fresh feature requests enter requirements locking before artifacts exist |
| No live artifact evidence, no valid handoff, and no explicit new-feature intake evidence | `user` | cannot route safely without evidence anchor |

## Route Suppression Checklist

Before invoking `beo-route`, confirm that at least one of these is true:
1. `STATE.json.current_owner` is missing, stale, contradicted by live artifacts, or colliding with another valid owner predicate.
2. User intent conflicts with current state, handoff, approval, or live artifact evidence.
3. Multiple non-route owner predicates appear true simultaneously.
4. The current handoff is stale, invalid, or no longer consistent with live artifacts.
5. No live artifact evidence provides a clear ownership anchor.

Do **not** invoke `beo-route` when:
- The current owner is valid and its predicate is satisfied by live artifacts.
- The issue is artifact content repair, not owner selection.
- A downstream owner found content to repair but the pipeline owner selection is unambiguous.
- The only contradiction is from scout or status output (not canonical artifacts).

## Hard stops
- Do not perform the selected owner's work.
- Do not invent new owners or transitions.
- Do not route around stale approval or contradicted requirements.
- Do not route to a second feature until the prior feature's state is closed or explicitly deferred — one active feature per worktree.

## Allowed next owners
- `beo-explore`
- `beo-plan`
- `beo-validate`
- `beo-execute`
- `beo-review`
- `beo-debug`
- `beo-compound`
- `beo-dream`
- `beo-onboard` — only when startup freshness is false, missing, or stale.
- `beo-author` — only when the user request is explicitly doctrine authoring, not runtime delivery.
- `beo-reference` — only for explicit read-only lookup requests, not runtime owner selection.
- `user`
- done

## References
- `beo-reference -> operator-card.md` — read when presenting the selected owner and evidence.
- `beo-reference -> doctrine-map.md` — read when ownership of a rule is unclear.
- `beo-reference -> pipeline.md` — read when checking legal owner transitions.
- `beo-reference -> approval.md` — read when stale approval affects routing.
- `beo-reference -> learning.md` — read when accepted-work closure affects routing.
- `beo-reference -> state.md` — read when evaluating state, handoff freshness, and route evidence fields.
- `beo-reference -> artifacts.md` — read when interpreting decision mapping and artifact provenance.
- `references/router-operations.md` — read when inspecting current route evidence without unsupported commands.
