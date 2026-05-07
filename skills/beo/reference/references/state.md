# BEO State

## State authority

`STATE.json` records routing-safe facts only. Durable rationale belongs in owner artifacts.

Human-readable mirrors such as `operator_view` are display-only. Canonical fields win.

## Active feature invariant

BEO manages one active feature at a time.

`STATE.json.feature_slug` names the active feature. All runtime owner decisions operate on that feature only.

If multiple active feature candidates exist and the active feature cannot be selected from canonical state and artifacts, route to `user`.

Do not solve feature collision by branch, worktree, status scout, or inference from recent files.

## Required fields during active runtime

| Field | Meaning |
| --- | --- |
| `current_owner` | active owner |
| `status` | `active`, `blocked`, or `done` |
| `feature_slug` | active feature |
| `current_phase` | `requirements`, `plan`, `validation`, `execution`, `review`, or `learning` |
| `triage_class` | `beo_tiny` or `standard` |
| `go_mode` | assumption posture only |
| `updated_at` | last canonical state update |

## Minimal STATE.json

```json
{
  "current_owner": "beo-explore",
  "status": "active",
  "feature_slug": "feature-slug",
  "current_phase": "requirements",
  "triage_class": "beo_tiny",
  "go_mode": {
    "active": false,
    "suspended": false,
    "reason": null
  },
  "readiness": null,
  "approval_ref": null,
  "execution_mode": null,
  "execution_set_id": null,
  "execution_set_beads": [],
  "debug_return": null,
  "closure": null,
  "operator_view": {
    "current_owner": "beo-explore",
    "next_action": "lock requirements",
    "updated_at": "..."
  },
  "updated_at": "..."
}
```

## Validation mirrors

| Field | Clear when |
| --- | --- |
| `readiness` | requirements, plan, scope, verification, approval, or execution set changes |
| `approval_ref` | approval invalidates |
| `execution_mode` | plan or execution set changes |
| `execution_set_id` | execution set changes |
| `execution_set_beads` | execution set changes |

When approval becomes stale, the owner that caused staleness must clear all validation mirrors in the same handoff.

## No worktree dependency

BEO does not require a worktree identity model.

Workflow authority comes from one active feature, canonical state, canonical handoff when fresh, feature artifacts, fresh approval, selected execution set, live file-change evidence, and review evidence.

Repository/file checks may prove scope, freshness, or post-execution modification. They do not create a separate worktree authority layer.

Do not require branch, HEAD, worktree, or `last_git_ref` fields.

## Handoff

`HANDOFF.json` is used only for pause/resume or owner transfer. It is not a second state file.

Minimum shape:

```json
{
  "from_owner": "beo-plan",
  "intended_resume_owner": "beo-validate",
  "feature_slug": "feature-slug",
  "reason": "plan complete",
  "evidence_refs": [
    ".beads/artifacts/feature-slug/CONTEXT.md",
    ".beads/artifacts/feature-slug/PLAN.md"
  ],
  "state_updated_at": "...",
  "created_at": "..."
}
```

If HANDOFF contradicts live STATE/artifacts, ignore stale handoff and use canonical state/artifact evidence. Route only if owner identity becomes unsafe.


## Debug return lifecycle

Before handing to `beo-debug`, the sending owner records `debug_return.return_to`, `source_owner`, `blocked_invariant`, and `evidence_ref`.

```json
"debug_return": {
  "return_to": "beo-execute",
  "source_owner": "beo-execute",
  "blocked_invariant": "verification failed with unproven root cause",
  "evidence_ref": ".beads/artifacts/feature-slug/execution-bundle.json",
  "created_at": "..."
}
```

`beo-debug` may not change `debug_return.return_to` unless evidence proves it invalid.

The receiving owner must consume or clear `debug_return` before continuing.

Do not reuse an old debug return for a new blocker.

## Closure lifecycle

When `STATE.json.status` becomes `done`, write `closure`.

```json
"closure": {
  "type": "accepted | rejected | deferred | canceled | user_stop",
  "source_owner": "beo-review | user | beo-compound | beo-dream",
  "evidence_ref": ".beads/artifacts/feature-slug/REVIEW.md",
  "closed_at": "..."
}
```

A feature is terminal only when `status=done` and `closure` is present.


## Blocked status recovery

When a blocker is resolved, the owner that consumes the resolution sets `status=active`, updates `current_owner`, and clears stale blocker fields before continuing.


## Pre-write freshness guard

Before any owner-owned mutation, the owner must reread the canonical surfaces that authorize that mutation.

If any required surface changed, disappeared, became stale, or contradicted the owner's preflight evidence, the owner must stop and route to the legal repair owner.

This is not a worktree model and not a parallel-worker protocol. It is a local stale-read guard for AI agents.

Examples:

- `beo-plan` rereads locked `CONTEXT.md` before writing `PLAN.md`.
- `beo-validate` rereads `CONTEXT.md` and `PLAN.md` before writing approval/readiness.
- `beo-execute` rereads approval/readiness/selected set before first mutation.
- `beo-review` rereads execution bundle and live file evidence before verdict.
