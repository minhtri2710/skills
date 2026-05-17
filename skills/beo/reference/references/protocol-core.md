# BEO Protocol Core

Authority: canonical runtime invariants. Summaries elsewhere may point here but must not add authority.

## Invariants

1. Exactly one current owner acts at a time.
2. Owners may write only fields and artifacts they own.
3. Product files may be mutated only by `beo-execute` inside a current approved execution set.
4. `PASS_EXECUTE` may be emitted only by `beo-validate`.
5. Terminal review verdicts may be emitted only by `beo-review`.
6. Helper output never grants approval, refreshes approval, selects execution sets, or emits verdicts.
7. Artifact authority beats STATE, HANDOFF, chat, helper summaries, and generated surfaces when contradictory.
8. Missing, stale, contradictory, invalid, or unavailable authority fails closed.
9. Meta-targets must resolve through transition provenance, never chat memory.
10. Abandonment and closure require legal pipeline conditions.

## Delegated canonical homes

- Shared owner contract: `beo-reference -> references/skill-contract-common.md`
- Legal transitions: `beo-reference -> registry/pipeline.json`
- Artifact ownership and schema: `beo-reference -> references/artifacts.md` and `beo-reference -> registry/artifact-schemas.json`
- Approval: `beo-reference -> references/approval.md` and `beo-reference -> registry/approval-envelope.json`
- Transition provenance and meta-targets: `beo-reference -> references/transition-provenance.md`
- State and HANDOFF mirrors: `beo-reference -> references/state.md`
- Lifecycle closure and reopen: `beo-reference -> references/lifecycle.md`
- Human Gates: `beo-reference -> references/decision-boundaries.md`
- Density: `beo-reference -> references/density.md`
