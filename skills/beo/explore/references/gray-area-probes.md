Non-normative asset.

# gray-area-probes

Role: ASSET
Allowed content only: probe axes / question prompts only

## Acceptance probes

- What observable behavior proves this is done?
- What inputs, outputs, UI states, or commands define success?
- What failure mode should no longer occur?
- What acceptance evidence should review expect?

## Non-goal probes

- What tempting adjacent work should not be included?
- What refactor, migration, redesign, or cleanup is explicitly out of scope?
- What existing behavior should remain intentionally imperfect for now?

## Compatibility probes

- Which existing API, file format, config, CLI, or data must remain compatible?
- Are old users, old configs, old data, or old clients supported?
- Is backwards compatibility required across feature flags or rollout phases?

## Constraint probes

- Are there performance, security, privacy, latency, cost, dependency, platform, or accessibility constraints?
- Are network, storage, database, or third-party service changes allowed?
- Are dependency or lockfile changes allowed?

## Scope-risk probes

- Could this touch auth, billing, permissions, migrations, data deletion, secrets, or privacy surfaces?
- Could this require multi-phase delivery?
- Could this create generated files, snapshots, schema outputs, or lockfile changes?
- Could parallel work conflict with the same files or public interfaces?

## Clarification triage probes

- Would the answer change acceptance criteria?
- Would the answer change file scope or approval scope?
- Would the answer change compatibility or security/privacy constraints?
- If not, can it be recorded as a non-blocking assumption under `go_mode`?
