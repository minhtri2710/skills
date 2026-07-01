---
name: beo-reference
description: "Read-only lookup for BEO doctrine, registries, command authority, transitions, schemas, and safety invariants. Use for BEO rule/schema questions, not delivery execution, approval, or review. Never mutates delivery state. Routes operators to the right helper via `references/command-manifest.md`."
---
# beo-reference

Canonical lookup router: `references/doctrine-map.md`. Helper index: `references/command-manifest.md`.

## Read

- The user's BEO rule, schema, transition, command authority, or safety lookup request.
- `references/doctrine-map.md` first to choose the narrowest source.
- `references/command-manifest.md` when the user wants to know which Python helper to run.
- `br robot-docs guide` and `br capabilities --format json` (in-tool) when the user asks how to use the `br`/`bv` CLI; CLI syntax/authority detail lives in `references/lifecycle.md`.
- `references/context-budget.md` when the user asks about what to load at a given phase.
- `references/kernel.md` when authority, lifecycle, safety, closure, or invariant questions are involved.
- The narrow registry, schema, template, script contract, or reference file needed for the lookup.

## Do

- Answer from canonical BEO references and registries.
- Prefer registries for machine-readable contracts.
- Prefer references for rationale and operating guidance.
- Cite exact file paths or section names.
- State clearly when an answer is advisory rather than approval-bearing.
- Use this lookup shape when practical: Answer; Canonical source; Authority status (`binding` or `advisory`); Related caveat.

## Write

- Nothing; read-only lookup only.

## Emit

- `lookup_complete`

## Never

- See `beo-reference -> registry/phase-contracts.json` `must_not[]`; audit C8 enforces drift.
- Do not mutate product files, BEO artifacts, registries, memory, qmd indexes, or Beads state.
- Do not claim issues.
- Do not grant `PASS_EXECUTE`.
- Do not issue review verdicts.
- Do not close or route Beads issues.
- Do not act as a delivery phase owner.
