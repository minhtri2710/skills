# BEO State v2

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
