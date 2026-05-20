# Modes

| Mode | Use for | Forbidden |
| --- | --- | --- |
| quick | one tiny repo-only low-risk atomic change | generated outputs unless declared, external/stateful side effects |
| standard | moderate repo-only atomic change, declared generated outputs | external/stateful side effects |
| strict | external/stateful/high-risk/destructive/uncertain rollback | anything without explicit authorization and rollback/compensation |

## Independence policy

- Quick: same actor/session allowed.
- Standard: same actor/session allowed; review must independently inspect diff/evidence.
- Strict: separate validate or review actor by default, or explicit human override when one actor must run every gate.

## Rules

- Quick may keep plan intake compact.
- For quick mode, omitted optional posture/flow fields are helper-expanded defaults, not missing evidence.
- Quick never collapses validate, execute, or review.
- Standard must declare generated outputs, risk scope, and rollback boundary when not profile-expanded.
- Strict must declare authorization, target, side effect, rollback/compensation, and command contract.
- Strict uses independent validate/review by default, or an explicit human override when one actor must run every gate.
- Strict mode is mandatory for deployment, database migration, cloud resource mutation, payment/cost impact, third-party stateful API mutation, package publication, email/message send, security/privacy/access impact, destructive action, or uncertain rollback.
- Mode registry data lives in `registry/profiles.json`.
