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
2. check `br` and `bv` availability when possible; check `bv` with `bv --version` only (never invoke bare `bv`, which requires a TTY and fails in non-interactive agent sessions)
3. if Node is unavailable or broken, stop and ask the user to repair tooling before proceeding
4. if `br` or `bv` is unavailable or broken, continue managed startup repair in degraded mode and report the missing tooling as a blocker for live bead or viewer-backed verification

## Decision Matrix

The `checkRepo` return value contains a script-level `status`, not a routing state.

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

## Exact commands

Check only:

```sh
node <installed-beo-onboard-root>/scripts/onboard_beo.mjs --repo-root "<absolute-repo-root>"
```

Apply managed repair:

```sh
node <installed-beo-onboard-root>/scripts/onboard_beo.mjs --repo-root "<absolute-repo-root>" --apply
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
- no `next_owner`, `recommended_owner`, `selected_owner`, `approved`, `ready`, `PASS_SERIAL`, `PASS_SWARM`, terminal verdict, or promotion decision fields

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
