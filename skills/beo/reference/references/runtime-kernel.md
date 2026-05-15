# Runtime Kernel

Authority: canonical runtime safety invariants.

This kernel may be summarized elsewhere, but those summaries never add authority.

## Core invariants

1. Owner authority is exclusive: only the loaded legal owner may write its owned surface.
2. Only `beo-validate` may grant/refuse `PASS_EXECUTE`.
3. Only `beo-execute` may mutate declared product files or generated outputs.
4. Only `beo-review` may emit terminal verdicts.
5. STATE, HANDOFF, chat memory, summaries, helpers, templates, and generated/advisory surfaces never override current required artifacts.
6. Missing, stale, invalid, contradictory, or unavailable approval, integrity, or owner authority fails closed.
7. Human Gates, approval freshness, integrity, declared scope, and legal transitions are never bypassed by go-mode, user pressure, or helper output.
8. Artifact density changes ceremony only; it never weakens approval, execution scope, review, owner authority, or fail-closed behavior.
9. Execution state lives in artifacts and the Execution Ledger, not chat memory.
10. Every runtime decision has one canonical authority and one legal transition source: `beo-reference -> registry/pipeline.json`.

## Delegated rules

- Operator flow: `beo-reference -> references/operator-cockpit.md`
- Normal resume orientation: `beo-reference -> references/resume-resolution.md`
- Unsafe identity repair: `beo-reference -> references/route-resolution.md`
- Loading and reload: `beo-reference -> references/loading.md`
- Approval, integrity, and helper semantics: `beo-reference -> references/approval.md`
- Artifact density, shape, ownership, and placeholders: `beo-reference -> references/artifacts.md`
- STATE and HANDOFF semantics: `beo-reference -> references/state.md`
- Ask/assume posture, go-mode, Human Gates, and secrets: `beo-reference -> references/decision-boundaries.md`
- Execution ledger and rollback execution: `beo-reference -> references/execution-ledger.md`
- Lifecycle, closure, reopen, and abandonment: `beo-reference -> references/lifecycle.md`
- Learning runtime boundary: `beo-reference -> references/learning.md`
- Doctrine authoring boundary: `beo-author -> SKILL.md`
