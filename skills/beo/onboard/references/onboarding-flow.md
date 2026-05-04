## Contents

- Preflight
- Decision Matrix
- Managed surfaces
- Exact commands
- `checkRepo` result schema
- Scout contract
- Apply order
- Migrated startup gates

# onboarding-flow

Role: APPENDIX
Allowed content only: `checkRepo` schema, managed surfaces, exact check/apply commands, apply order

## Preflight

1. verify `node --version` is `>=18` before running `scripts/onboard_beo.mjs`
2. report `br` and `bv` availability when known; never invoke bare `bv`, which requires a TTY and fails in non-interactive agent sessions; do not claim the script probes tooling it does not probe
3. if Node is unavailable or broken, stop and ask the user to repair tooling before proceeding
4. if `br` or `bv` is reported as unavailable or broken, continue managed startup repair in degraded mode and note the missing tooling as an advisory dependency gap; actual tooling discovery happens at runtime, not during onboarding

## Decision Matrix

The `checkRepo` return value contains a script-local `status`, not `STATE.json.status` and not a routing state. Do not rename the script JSON field; keep the distinction in prose.

| `status` | Action |
| --- | --- |
| `up_to_date` | no managed repair needed; record freshness evidence |
| `needs_onboarding` | run apply once, then re-check |
| `invalid_state_json` | stop; parseable live state cannot be guessed |

## Managed surfaces

| Surface | Rule |
| --- | --- |
| `AGENTS.md` managed block | create, append, or replace only between BEO sentinels |
| `.beads/onboarding.json` | write current plugin and managed startup contract versions |
| `.beads/beo_status.mjs` | write generated read-only scout helper when missing or stale |

Read-only orientation may report `.beads/STATE.json` parseability and `.beads/critical-patterns.md` presence, but onboarding does not create or repair runtime artifacts.
Startup reads only the active feature directory named by `STATE.json.feature_slug` or a fresh `HANDOFF.json`; other feature artifact directories are historical evidence only.

## Exact commands

Check only:

```sh
node skills/beo/onboard/scripts/onboard_beo.mjs --repo-root "$(pwd)"
```

Apply managed repair:

```sh
node skills/beo/onboard/scripts/onboard_beo.mjs --repo-root "$(pwd)" --apply
```

Status helper after onboarding:

```sh
node .beads/beo_status.mjs --json
```

The scout output is orientation only. It must remain read-only and cannot
validate onboarding freshness, authorize execution, or replace live routing.

## `checkRepo` result schema

| Field | Meaning |
| --- | --- |
| `status` | `up_to_date`, `needs_onboarding`, or `invalid_state_json` |
| `actions[]` | managed repair actions required |
| `details` | booleans for managed surface freshness and parseability |

## Scout contract

`node .beads/beo_status.mjs --json` should expose:
- `read_only: true`
- onboarding freshness summary plus the live check command
- observed current owner, state schema version, and operator view when present
- handoff existence plus freshness signal
- approval reference observations only when present; approval pointers must be reported as `referenced_unverified`, never `current`, unless the live approval doctrine has been verified outside the scout
- `reads.required` vs `reads.conditional`
- advisory dependency posture when known
- state conflicts and advisory next actions when observed
- an authority notice that status is display-only and cannot route, approve, validate, review, dispatch, or promote
- no `next_owner`, `recommended_owner`, `selected_owner`, `approved`, `ready`, `PASS_EXECUTE`, or any `PASS_*` readiness verdict, terminal verdict, or promotion decision fields

## Apply order

| Step | Action |
| --- | --- |
| 1 | Resolve `<absolute-repo-root>` to the repository root, not transient shell cwd. |
| 2 | Run check-only command and capture `status`, `actions`, and `details`. |
| 3 | If `status=invalid_state_json`, stop and record that escalation is required; owner routing remains canonical in `beo-onboard`. |
| 4 | If `status=up_to_date`, run `.beads/beo_status.mjs --json` when present and capture the scout output. |
| 5 | If `status=needs_onboarding`, run apply command once. |
| 6 | Re-run check-only command; require `status=up_to_date`. |
| 7 | Run `.beads/beo_status.mjs --json` and record required vs conditional reads. |
| 8 | Ensure the managed `AGENTS.md` session-end block preserves owner-specific write boundaries for bead/status/handoff surfaces. |
| 9 | Record actions applied and freshness evidence; successor-owner selection remains canonical in `beo-onboard`. |

Non-normative success example:

```json
{
  "status": "up_to_date",
  "actions": [],
  "details": {
    "managed_block_current": true,
    "onboarding_json_exists": true,
    "state_json_parseable": true
  }
}
```

## Migrated startup gates

Startup checks are managed by the live onboarding script and managed AGENTS block. File presence alone is not freshness.

## `onboarding.json` schema

Written by the apply command to `.beads/onboarding.json`.

| Field | Required | Rule |
| --- | --- | --- |
| `schema_version` | yes | current onboarding schema version |
| `plugin` | yes | always `"beo"` |
| `plugin_version` | yes | matches the onboarding script's version from `onboarding-metadata.json` |
| `managed_startup_contract_version` | yes | matches the managed startup contract version from `onboarding-metadata.json` |
| `installed_at` | yes | ISO-8601 timestamp of the apply run |
| `status` | yes | `"complete"` after successful apply |
| `agent_mail` | yes | advisory field; `available: null`, `checked_at: null`, `source: "not_probed_advisory_unknown_by_default"` — not a live capability probe |
| `managed_assets` | yes | records the managed surfaces: `agents_mode` (one of `created_from_template`, `updated_managed_block`, `appended_managed_block`, `retained_existing_managed_block`), `status_script` path |
| `tooling` | no | when present, cached `br`/`bv` version observations from the apply run; advisory only |

Note: `agent_mail` and `tooling` fields are advisory cache; the onboarding script does not probe agent mail or tooling capabilities. Do not treat them as live capability guarantees.
