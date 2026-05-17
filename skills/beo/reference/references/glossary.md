# BEO Glossary

Authority: canonical terminology only. It adds no workflow rule, owner authority, artifact field, readiness rule, enum, or transition.

- Owner: the loaded skill allowed to write one owned surface.
- Surface: the artifact section or file an owner may write.
- Authority block: structured block used for runtime decisions.
- Projection: normalized fields derived from artifacts for approval and integrity.
- `PASS_EXECUTE`: validate-owned readiness result that permits execute to act.
- Approval ref: record/hash of the approved projection.
- Integrity: helper evidence that current artifacts still match approval.
- Mirror: STATE/HANDOFF identity hint; never authority.
- Density: compact/full artifact shape; never safety strength.
- Human Gate: user-owned decision that affects scope, approval, or safety.
- Transition: legal `condition_id` -> target pair in `registry/pipeline.json`.
- Meta-target: symbolic target such as `return_to_caller` or `restored_owner`, resolved only by legal metadata and artifacts.
- Operator cockpit: first-page navigation reference for lane, owner, authority, mutation, Human Gate, density, and condition decisions.
- Operator form: advisory drafting aid that cannot grant authority or replace canonical artifacts/schemas.
- Compact operator form: advisory `TICKET.md` drafting aid aligned to compact schema and phase ownership.
- Resume resolution: read-only artifact-derived orientation for normal context-loss resume.
- Route repair: unsafe owner/feature identity metadata repair only.
- Decision card: human scan summary in owner skills; it is not machine transition authority.
- Anchor: stable markdown marker used for navigation or checker expectations.

## `beo-reference -> <path>`

`beo-reference -> <path>` is a symbolic lookup instruction: use `beo-reference` to read the canonical file at `<path>` under `skills/beo/reference/`.

It is not a shell path, runtime transition, or mutation permission.

Example: `beo-reference -> references/skill-contract-common.md` means read `skills/beo/reference/references/skill-contract-common.md` as canonical doctrine.
