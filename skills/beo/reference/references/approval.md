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
| `"mode"` | yes | `serial` or `swarm` |
| `"scope_source_refs"` | yes | refs back to `PLAN.md` sections or bead ids defining the approved scope |
| `"approved_at"` | yes | approval timestamp |

Label alone is never enough for execution approval.

## Approval taxonomy

| Term | Meaning |
| --- | --- |
| `execution_approval` | approval to execute the selected bead set inside the approved scope, mode, and verification contract |
| `user_authorization` | explicit user or policy permission required before execution when applicable |
| `acceptance_verdict` | `accept`/`fix`/`reject` decision after review |
| `approval_refresh` | freshness-only renewal when approved scope and contract remain unchanged |
| `new_approval_grant` | a new execution approval required when bead set, mode, file scope, or verification contract changes |

Do not introduce separate `phase_approval`, `story_approval`, `merge_approval`, `beo-go`, `beo-uat`, or external gate records. BEO keeps one execution approval envelope and one review verdict.

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

## Contract-bearing PLAN.md content

The following `PLAN.md` sections are contract-bearing when present:
- current phase contract
- current phase story map
- risk map entries marked MED or HIGH
- bead graph
- file scope
- forbidden paths
- verification commands
- execution envelope proposal

Any mutation to these sections after approval makes execution approval stale unless `beo-validate` grants or refreshes approval against the updated hashes according to the execution envelope invariant.

## ApprovalCurrent predicate

| Field | Rule |
| --- | --- |
| record | approval record exists and is explicit |
| marker | live approved label/marker matches the record |
| freshness | approval timestamp >= latest contract-bearing artifact mutation |
| scope | approved scope matches current phase/bead set |

## Grant / invalidate write order

| Action | Order | Writer |
| --- | --- | --- |
| grant | 1 write approval record; 2 write approved marker/label; 3 write STATE approval pointer | beo-validate |
| invalidate | 1 clear STATE pointer; 2 remove approved marker/label; 3 mark record invalidated | authorized mutator skill |

## Contract-bearing mutation

Any mutation to the following makes execution approval stale:
- locked requirement content in `CONTEXT.md`
- design, current phase contract, current phase story map, any MED/HIGH risk-map row, risk proof requirement, bead graph, file scope, forbidden paths, verification content, or execution envelope proposal content in `PLAN.md`
- approved bead dependency or file-scope metadata
- locked acceptance, compatibility, or constraint content

## Invalidation protocol

| Case | Owner |
| --- | --- |
| stale approval before product mutation, artifacts unchanged | beo-validate |
| stale approval before product mutation, but scope/plan/bead graph needs repair | beo-plan |
| stale approval after product mutation, but rollback is clean and leaves `changed_files=[]` | beo-validate or beo-plan depending on artifact repair need |
| stale approval after product mutation and changed files remain, but scope impact still needs terminal assessment against the prior envelope | `beo-review` |
| stale approval after product mutation and evidence already proves plan, file scope, bead graph, or verification repair is required | `beo-plan` |
| stale approval because requirements are contradicted or unlocked | beo-explore |

## Manual pressure tie-breakers

Use these short cases during manual review:
- blocker plus stale approval before mutation -> if artifact or approval invalidity is already proven, `beo-validate` or `beo-plan` wins before `beo-debug`
- blocker plus unknown root cause during execution -> `beo-debug` wins
- review finding plus unknown root cause -> `beo-debug` before verdict-driven repair routing
- phase/story/risk mutation after approval -> approval stale, not a separate gate
- swarm-to-serial fallback -> fresh `PASS_SERIAL`, never reused swarm approval

## Short approval block example

```json
{
  "approved_beads": ["B1"],
  "mode": "serial",
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
- `beo-execute` and `beo-swarm` should point here rather than restating approval schema or approval law.
