# BEO Doctrine Map v2

## Restatement rule

Each workflow rule has exactly one canonical home.

Owner SKILL files may restate a canonical rule only as a local hard stop needed to prevent unsafe action.

Do not duplicate multi-step approval, routing, state, review, go-mode, or learning logic in owner files. Use one-line canonical pointers instead.

When a local owner hard stop is stricter than the canonical reference, the stricter local stop applies only to that owner.

## Canonical homes

| Doctrine | Canonical surface |
| --- | --- |
| Owner selection | `references/pipeline.md` |
| Route suppression | `route/SKILL.md` and pointer from `pipeline.md` |
| Legal transitions | `references/pipeline.md` |
| State and handoff lifecycle | `references/state.md` |
| Approval freshness | `references/approval.md` |
| Artifact layout and templates | `references/artifacts.md` |
| Triage and tiny path | `references/complexity.md` |
| Human Gate discipline | `references/human-gate.md` |
| Go-mode | `references/go-mode.md` |
| Learning thresholds | `references/learning.md` |
| Shared output packet | `references/skill-contract-common.md` |
| Operator quick map | `references/operator-card.md` |
| Doctrine authoring rules | `references/authoring.md` |
| Exact CLI command forms | `references/cli.md` |
