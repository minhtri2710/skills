## Contents

- Approval model
- Approval record schema
- Approval taxonomy
- Execution envelope invariant
- Contract-bearing PLAN.md content
- ApprovalCurrent predicate
- Grant / invalidate write order
- Contract-bearing mutation
- Invalidation protocol
- Manual pressure tie-breakers
- Short approval block example
- Canonical usage note

# Approval

## Approval model

Keep these terms distinct:
- `user authorization` = explicit user approval or approved policy permission
- `execution approval` = the readiness/scope record written by `beo-validate`
- `acceptance verdict` = the terminal `accept`/`fix`/`reject` outcome written by `beo-review`

Execution approval is an internal readiness/scope grant for the current approved bead set. It never replaces explicit user authorization when the requirement, policy, secret, access, destructive action, or external decision still requires it.

## Approval record schema

| Field | Required | Rule |
| --- | --- | --- |
| path | yes | `.beads/artifacts/<feature_slug>/approval-record.json` |
| `"feature_slug"` | yes | approved feature slug |
| `"phase"` | yes | current phase or compact phase marker |
| `"user_authorization_ref"` | yes | explicit approval source or policy reference |
| `"approval_kind"` | yes | `execution_approval` |
| `"validated_by"` | yes | `beo-validate` |
| `"context_hash"` | yes | hash of locked `CONTEXT.md` |
| `"plan_hash"` | yes | hash of current `PLAN.md` / phase artifact |
| `"bead_graph_hash"` | yes | hash of approved bead graph |
| `"approved_beads"` | yes | explicit approved bead ids |
| `"approved_file_scope"` | yes | explicit writable file paths/globs approved for execution |
| `"approved_generated_outputs"` | yes | generated outputs allowed to change, or `[]` |
| `"forbidden_paths"` | yes | paths/globs that remain out of scope |
| `"verification_commands"` | yes | verification commands that approval expects |
| `"execution_mode"` | yes | `single` \| `ordered_batch` \| `local_parallel` |
| `"scope_source_refs"` | yes | refs back to `PLAN.md` sections or bead ids defining the approved scope |
| `"approved_at"` | yes | approval timestamp |
| `"schema_version"` | yes | approval record schema version (current: `1`) |
| `"doctrine_version_ref"` | yes | beo doctrine version or git commit ref at approval time |
| `"approval_seq"` | no | advisory monotonic counter; increment on every write to this approval record; enables ordering when multiple approval writes occur in sequence |

Label alone is never enough for execution approval. `doctrine_version_ref` is provenance only; it does not create a standalone revalidation gate.

## Approval taxonomy

| Term | Meaning |
| --- | --- |
| `execution_approval` | approval to execute the selected bead set inside the approved scope, mode, and verification contract |
| `user_authorization` | explicit user or policy permission required before execution when applicable |
| `acceptance_verdict` | `accept`/`fix`/`reject` decision after review |
| `approval_refresh` | freshness-only renewal when approved scope and contract remain unchanged |
| `new_approval_grant` | a new execution approval required when bead set, mode, file scope, or verification contract changes |

Do not introduce separate approval records, gate records, card approval, or guide approval. BEO keeps one execution approval envelope and one review verdict.

## Execution envelope invariant

One approval record binds exactly one execution envelope:
- approved beads
- execution mode
- approved file scope
- approved generated outputs
- forbidden paths
- verification contract
- current `CONTEXT.md` / `PLAN.md` / bead graph hashes

Any execution-envelope change invalidates prior execution approval. A freshness-only refresh is legal only when the full envelope is unchanged and artifacts remain content-complete.

## PASS_EXECUTE authority

A `PASS_EXECUTE` verdict is executable only when it records:
- `approval_ref`
- selected `execution_set_id`
- selected `execution_set_beads`
- selected `execution_set_mode`
- `partial_progress_allowed` when applicable

This applies even when `approval_action=unchanged`.

Execution cannot begin from stale approval, missing `approval_ref`, mismatched `CONTEXT.md` hash, mismatched `PLAN.md` hash, or scope not covered by the approval envelope.

## Contract-bearing PLAN.md content

The following `PLAN.md` sections are contract-bearing when present:
- current phase contract
- story map
- risk map entries marked MED or HIGH
- bead graph
- file scope
- forbidden paths
- verification plan
- execution envelope proposal

Any mutation to these sections after approval makes execution approval stale unless `beo-validate` grants or refreshes approval against the updated hashes according to the execution envelope invariant.

## ApprovalCurrent predicate

| Field | Rule |
| --- | --- |
| record | approval record exists at the current approval path and is explicit |
| freshness | approval timestamp >= latest contract-bearing artifact mutation |
| scope | approved scope matches current phase/bead set |
| state mirror | `STATE.json.approval_ref` points to the current approval record |

The `approved` label is an operator-visible bead marker, not part of the `ApprovalCurrent` predicate. When used, `beo-validate` applies it to every bead in the approved execution envelope; `reserved` remains an execution claim marker owned by `beo-execute` and may coexist with `approved` while a bead is in progress.

## Grant / invalidate write order

| Action | Order | Writer |
| --- | --- | --- |
| grant | 1 write approval record; 2 write approved marker/label; 3 write STATE approval pointer | beo-validate |
| invalidate | 1 mark current approval invalid when present; 2 clear STATE approval/readiness mirrors; 3 remove stale approved marker/label | authorized mutator skill |

## Contract-bearing mutation

Any mutation to the following makes execution approval stale:
- locked requirement content in `CONTEXT.md`
- design, current phase contract, story map, any MED/HIGH risk-map row, risk proof requirement, bead graph, file scope, forbidden paths, verification-plan content, or execution-envelope proposal content in `PLAN.md`
- approved bead dependency or file-scope metadata
- locked acceptance, compatibility, or constraint content

## Invalidation protocol

`approval_ref` authority and mirrored field ownership are mapped in `beo-reference -> state.md`. Display cards do not create, refresh, or replace an approval record.

### Approval becomes stale after mutation begins

When approval becomes stale after mutation begins, `beo-execute` must stop immediately.

Route evidence by proven condition:

1. If live diff or scope impact needs independent assessment, return to `beo-review`.
2. If plan, file scope, bead graph, or verification contract is already proven invalid, route to `beo-plan`.
3. If the only issue is approval freshness and plan/scope remain unchanged, route to `beo-validate`.
4. If owner selection is contradictory or cannot be proven from live artifacts, route to `beo-route`.

Never continue implementing merely to finish the change first, and never route directly back to `beo-execute` without a fresh valid owner decision and readiness envelope.

| Case | Owner |
| --- | --- |
| stale approval before product mutation, artifacts unchanged | beo-validate |
| stale approval before product mutation, but scope/plan/bead graph needs repair | beo-plan |
| stale approval after product mutation, rollback is clean, `aggregate_changed_files=[]`, and no artifact repair is needed | `beo-validate` |
| stale approval after product mutation, rollback is clean, `aggregate_changed_files=[]`, and plan/scope/bead/verification artifact repair is needed | `beo-plan` |
| stale approval after product mutation and changed files remain, but scope impact still needs terminal assessment against the prior envelope | `beo-review` |
| stale approval after product mutation and evidence already proves plan, file scope, bead graph, or verification repair is required | `beo-plan` |
| stale approval because requirements are contradicted or unlocked | beo-explore |

> Rollback ownership: reverting product mutation is owned by `beo-execute`, bounded to the current bead's declared changed files only. Once rolled back with `aggregate_changed_files=[]` in execution-bundle.json (no changed files remain), route per the table above.

## Invalidation record fields

When invalidating an approval record, write all of the following to the current record before clearing the STATE pointer. BEO uses a current-only approval record path; a later grant may overwrite the current record after invalidation evidence has been consumed.

| Field | Required | Rule |
| --- | --- | --- |
| `"invalidated"` | yes | `true` |
| `"invalidated_at"` | yes | timestamp of invalidation |
| `"invalidated_by"` | yes | beo owner skill that performed the invalidation |
| `"invalidation_reason"` | yes | one of: `stale_approval`, `scope_change`, `plan_change`, `requirement_change`, `rollback_clean`, `other` |

Stale and revoked records must be distinguishable while present. Do not add approval-history or supersession pointers unless a future explicit history surface is approved.

## Manual pressure tie-breakers

Use these short cases during manual review:
- blocker plus stale approval before mutation -> if artifact or approval invalidity is already proven, `beo-validate` or `beo-plan` wins before `beo-debug`
- blocker plus unknown root cause during execution -> `beo-debug` wins
- review finding plus unknown root cause -> `beo-debug` before verdict-driven repair routing
- phase/story/risk mutation after approval -> approval stale, not a separate gate
- execution-set mode change -> fresh `PASS_EXECUTE`, never reused prior approval

## Short approval block example

```json
{
  "approved_beads": ["B1"],
  "execution_mode": "single",
  "approved_file_scope": ["src/ui/copy.ts"],
  "forbidden_paths": ["src/auth/**"],
  "verification_commands": ["npm test -- copy"],
  "context_hash": "...",
  "plan_hash": "...",
  "bead_graph_hash": "..."
}
```

## Canonical usage note

- `beo-validate` grants or refreshes execution approval according to this file.
- `beo-plan` invalidates stale approval only when contract-bearing planning edits require it.
- `beo-execute` should point here rather than restating approval schema or approval law.

## Stale approval gate

Stale approval must be refreshed before execution; owner handoff or cached state cannot revive an invalidated approval.
