# Onboarding Flow

Use this file when the short onboarding contract in `SKILL.md` is not enough.

## Prerequisites

1. verify `node --version` is `>=18` before running `scripts/onboard_beo.mjs`
2. verify `br` and `bv` are installed, callable, and compatible
3. if Node, `br`, or `bv` is unavailable or broken, stop and ask the user to repair tooling before proceeding

## Decision Matrix

The `checkRepo` return value contains a script-level `status`, not a routing state.

| `status` | Action |
| --- | --- |
| `"up_to_date"` | verify tool readiness, report onboarding current, return to `beo-route` |
| `"needs_onboarding"` | summarize needed actions, ask for approval only when shared repo guidance changes, then apply the minimum safe bootstrap changes |

These are script results, not `STATE.json` statuses.

## What Onboarding Installs

Onboarding manages:

| Asset | Purpose |
| --- | --- |
| `AGENTS.md` managed block | install or update managed beo instructions |
| `.beads/` | workspace root |
| `.beads/artifacts/` | feature artifacts |
| `.beads/learnings/` | learnings |
| `.beads/beo_status.mjs` | repo-local scout |
| `.beads/STATE.json` | bootstrap state |
| `.beads/critical-patterns.md` | bootstrap shared-guidance file |
| `.beads/onboarding.json` | onboarding metadata |

## `checkRepo` JSON Schema

```json
{
  "status": "up_to_date" | "needs_onboarding",
  "actions": [
    "create_AGENTS.md",
    "append_beo_managed_block",
    "update_beo_managed_block",
    "create_.beads/onboarding.json",
    "create_.beads/beo_status.mjs",
    "create_.beads/STATE.json",
    "create_.beads/critical-patterns.md",
    "create_.beads/artifacts/",
    "create_.beads/learnings/"
  ],
  "details": {
    "agents_md_exists": true,
    "has_beo_managed_block": false,
    "managed_block_current": false,
    "onboarding_json_exists": false,
    "plugin_match": false,
    "plugin_version_match": false,
    "managed_startup_contract_version_match": false,
    "status_script_exists": false,
    "state_json_exists": false,
    "state_json_parseable": false,
    "state_json_refreshable_bootstrap": false,
    "critical_patterns_exists": false,
    "artifacts_dir_exists": false,
    "learnings_dir_exists": false
  }
}
```

Key meaning:
- `plugin_match` → onboarding metadata belongs to `beo`
- `plugin_version_match` → metadata matches the current onboarder implementation
- `managed_startup_contract_version_match` → metadata matches the current managed startup contract
- `managed_block_current` → the managed `AGENTS.md` block still matches the live template
- `state_json_parseable` + `state_json_exists` together distinguish missing vs corrupt state
- `state_json_refreshable_bootstrap` means it is safe to overwrite bootstrap state during re-onboarding

## `applyRepo` Behavior

When onboarding is needed, apply only the actions returned by `checkRepo`, in this order:
1. merge `AGENTS.md` by create, replace-managed-block, or append-managed-block strategy
2. create `.beads/` if missing
3. create `.beads/artifacts/` if missing
4. create `.beads/learnings/` if missing
5. write `.beads/beo_status.mjs` only when requested
6. write `.beads/STATE.json` with canonical bootstrap defaults only when requested
7. initialize `.beads/critical-patterns.md` only when requested
8. write `.beads/onboarding.json`

The generated `.beads/beo_status.mjs` is a repo-local scout only. The live `checkRepo` logic in `scripts/onboard_beo.mjs` is the source of truth for onboarding freshness.

## `onboarding.json` Schema

```json
{
  "schema_version": "1.0",
  "plugin": "beo",
  "plugin_version": "<version>",
  "managed_startup_contract_version": "<version>",
  "installed_at": "<ISO-8601>",
  "status": "complete",
  "managed_assets": {
    "agents_mode": "created_from_template" | "updated_managed_block" | "appended_managed_block" | "retained_existing_managed_block",
    "status_script": ".beads/beo_status.mjs",
    "state_json": ".beads/STATE.json",
    "critical_patterns": ".beads/critical-patterns.md"
  }
}
```

Treat onboarding as current only when live `checkRepo` sees both metadata checks pass and the managed `AGENTS.md` block still matches the installed startup contract.

Use `retained_existing_managed_block` when onboarding refreshed metadata without changing an already-current managed block.

## Approval Boundary

Use explicit approval before:
- creating or merging the managed `AGENTS.md` block
- applying any onboarding change that modifies shared repo guidance

Do not add extra approval gates for purely local bootstrap state once the user has asked onboarding to proceed.
