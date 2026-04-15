# Onboarding Flow

Use this file when the short onboarding summary in `SKILL.md` is not enough.

## Prerequisites

1. Verify `node --version` is `>=18` before running `scripts/onboard_beo.mjs`.
2. If Node.js is unavailable, stop and ask the user to install it or perform manual setup.

## Decision Matrix

The `checkRepo` return value contains a script-level `status` field, not a routing state:

| `status` | Action |
| --- | --- |
| `"up_to_date"` | Report that onboarding is current and hand back to `beo-route`. |
| `"needs_onboarding"` | Summarize the actions, ask for approval, then apply when approved. |

> **Note:** These are script return values, not STATE.json routing states. The canonical routing state for a freshly-onboarded repo is `needs-onboarding` (see `pipeline-contracts.md` routing table).

## What Onboarding Installs

Onboarding manages:

| Asset | Purpose |
| --- | --- |
| `AGENTS.md` merge with the `<!-- BEO:START -->` / `<!-- BEO:END -->` block | Install or update the managed beo instructions. |
| `.beads/` | Create the beo workspace root. |
| `.beads/artifacts/` | Store artifacts. |
| `.beads/learnings/` | Store learnings. |
| `.beads/beo_status.mjs` | Install the repo-local scout command. |
| `.beads/STATE.json` | Initialize bootstrap state. |
| `.beads/critical-patterns.md` | Seed critical patterns defaults. |
| `.beads/onboarding.json` | Record onboarding completion and managed assets. |

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
    "onboarding_json_exists": false,
    "onboarding_version_match": false,
    "status_script_exists": false,
    "state_json_exists": false,
    "critical_patterns_exists": false,
    "artifacts_dir_exists": false,
    "learnings_dir_exists": false
  }
}
```

## `applyRepo` Behavior

When onboarding is needed, apply in this order:

1. Merge `AGENTS.md` using one of three strategies:
   - create from template when no `AGENTS.md` exists
   - replace the existing managed block when sentinels already exist
   - append the managed block when `AGENTS.md` exists but has no sentinels
2. Create `.beads/` if missing
3. Create `.beads/artifacts/` if missing
4. Create `.beads/learnings/` if missing
5. Write `.beads/beo_status.mjs`
6. Write `.beads/STATE.json` with canonical bootstrap defaults if missing (`phase: "router"`, `status: "needs-onboarding"`, `planning_mode: "unknown"`)
7. Write `.beads/critical-patterns.md` defaults if missing
8. Write `.beads/onboarding.json`

## `onboarding.json` Schema

```json
{
  "schema_version": "1.0",
  "plugin": "beo",
  "plugin_version": "<version>",
  "installed_at": "<ISO-8601>",
  "status": "complete",
  "managed_assets": {
    "agents_mode": "created_from_template" | "updated_managed_block" | "appended_managed_block",
    "status_script": ".beads/beo_status.mjs",
    "state_json": ".beads/STATE.json",
    "critical_patterns": ".beads/critical-patterns.md"
  }
}
```
