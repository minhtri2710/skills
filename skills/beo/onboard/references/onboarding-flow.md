# Onboarding Flow

Use this file when the short onboarding summary in `SKILL.md` is not enough.

## Prerequisites

1. Verify `node --version` is `>=18` before running `scripts/onboard_beo.mjs`.
2. Verify `br` and `bv` are installed, callable, and compatible with the repo's onboarding requirements.
3. If Node.js, `br`, or `bv` is unavailable or broken, stop and ask the user to install or repair the missing tooling before proceeding.

## Decision Matrix

The `checkRepo` return value contains a script-level `status` field, not a routing state. Treat a repo as ready only when the bootstrap state is present enough for beo operation and the required tooling checks pass.

| `status` | Action |
| --- | --- |
| `"up_to_date"` | Verify tool readiness, report that onboarding is current, and hand back to `beo-route`. |
| `"needs_onboarding"` | Summarize the actions, ask for approval only when shared repo guidance will be created or merged, then apply the minimum safe bootstrap changes. |

> **Note:** These are script return values, not STATE.json routing states. `needs_onboarding` is the pre-onboarding detection state; after successful onboarding, the repository returns to normal routing for its actual project state.

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
| `.beads/critical-patterns.md` | Initialize the canonical shared-guidance file when the repo bootstrap expects it. This is bootstrap plumbing, not pattern promotion. |
| `.beads/onboarding.json` | Record onboarding completion and managed asset versions for the live onboarder check. |

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
    "critical_patterns_exists": false,
    "artifacts_dir_exists": false,
    "learnings_dir_exists": false
  }
}
```

`plugin_match` is true when onboarding metadata is owned by the `beo` plugin. `plugin_version_match` is true when onboarding metadata matches the current onboarder implementation. `managed_startup_contract_version_match` is true when onboarding metadata matches the current managed startup contract. `managed_block_current` is true only when the managed `AGENTS.md` block still matches the live startup contract template.

## `applyRepo` Behavior

When onboarding is needed, apply only the actions returned by `checkRepo`, in this order:

1. If `checkRepo` requested an `AGENTS.md` action, merge it using one of three strategies:
   - create from template when no `AGENTS.md` exists
   - replace the existing managed block when sentinels already exist
   - append the managed block when `AGENTS.md` exists but has no sentinels
2. Create `.beads/` if missing
3. Create `.beads/artifacts/` if missing
4. Create `.beads/learnings/` if missing
5. Write `.beads/beo_status.mjs` only when `checkRepo` requested it
6. Write `.beads/STATE.json` with canonical bootstrap defaults only when `checkRepo` requested it (`phase: "using-beo"`, `status: "onboarding-complete"`, `next: "beo-route"`, `planning_mode: "unknown"`)
7. Initialize `.beads/critical-patterns.md` only when `checkRepo` requested it
8. Write `.beads/onboarding.json`

The generated `.beads/beo_status.mjs` is a repo-local scout for recorded onboarding metadata, `STATE.json`, and optional `HANDOFF.json`. It is not the source of truth for startup freshness; only the live `checkRepo` logic in `scripts/onboard_beo.mjs` decides whether onboarding is current.

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

Treat onboarding as current only when the live `checkRepo` logic sees both metadata checks pass and the managed `AGENTS.md` block still matches the installed startup contract.
Use `.beads/beo_status.mjs` only for repo-local state summary after that gate has already passed.
Use `retained_existing_managed_block` when onboarding refreshed metadata without touching the already-current managed `AGENTS.md` block.

## Approval Boundary

Use explicit approval before:
- creating or merging the managed `AGENTS.md` block
- applying any onboarding change that modifies shared repo guidance

Do not introduce extra approval gates for purely local bootstrap state such as `.beads/` directories or checkpoint files when the user has already asked onboarding to proceed.
