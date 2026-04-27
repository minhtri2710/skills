# onboarding-flow

Role: APPENDIX
Allowed content only: `checkRepo` schema, managed surfaces, exact check/apply commands, apply order

## Managed surfaces

| Surface | Rule |
| --- | --- |
| `AGENTS.md` managed block | create, append, or replace only between BEO sentinels |
| `.beads/onboarding.json` | write current plugin and managed startup contract versions |
| `.beads/beo_status.mjs` | write generated status helper when missing or stale |
| `.beads/STATE.json` | create only when absent; never overwrite parseable live state with guessed values |
| `.beads/critical-patterns.md` | create when absent or repair managed header/marker only |
| `.beads/artifacts/` | create directory when absent; do not mutate feature-specific artifact content |
| `.beads/learnings/` | create directory when absent; do not mutate feature-specific learning content |

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

## `checkRepo` result schema

| Field | Meaning |
| --- | --- |
| `status` | `up_to_date`, `needs_onboarding`, or `invalid_state_json` |
| `actions[]` | managed repair actions required |
| `details` | booleans for managed surface freshness and parseability |

## Apply order

| Step | Action |
| --- | --- |
| 1 | Resolve `<absolute-repo-root>` to the repository root, not transient shell cwd. |
| 2 | Run check-only command and capture `status`, `actions`, and `details`. |
| 3 | If `status=invalid_state_json`, stop and record that escalation is required; owner routing remains canonical in `beo-onboard`. |
| 4 | If `status=up_to_date`, run `.beads/beo_status.mjs --json` when present and capture the status output. |
| 5 | If `status=needs_onboarding`, run apply command once. |
| 6 | Re-run check-only command; require `status=up_to_date`. |
| 7 | Run `.beads/beo_status.mjs --json` and record next reads. |
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
