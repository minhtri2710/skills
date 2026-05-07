# BEO Skill Contract Common v2

## Canonical vocabulary registry

Use these canonical values:

- Owners: `beo-route`, `beo-explore`, `beo-plan`, `beo-validate`, `beo-execute`, `beo-review`, `beo-debug`, `beo-compound`, `beo-dream`, `user`, `done`.
- Readiness: `PASS_EXECUTE`, `FAIL_PLAN`, `FAIL_EXPLORE`, `BLOCK_USER`, `FAIL_STATE`.
- Execution modes: `single`, `ordered_batch`.
- Triage classes: `beo_tiny`, `standard`.
- Review verdicts: `accept`, `fix`, `reject`.
- Learning dispositions: `no-learning`, `durable-candidate`, `unclear`, `rejection-retrospective`.

Do not introduce aliases for removed or unsupported runtime concepts.

## Skill must be loaded to act

A beo skill's `SKILL.md` must be loaded before any mutation owned by that skill.

Identifying `STATE.json.current_owner` is not sufficient authorization to act. The loaded skill contract's writable surfaces and hard stops must be in scope.

## Standard decision packet

Every non-trivial owner output begins with:

```md
Decision:
Active owner:
Feature:
Evidence checked:
Changed surfaces:
Blocked by:
Next owner:
Next owner reason:
Authority note: display-only; canonical authority remains in the referenced state/artifact surface.
```

Rules:

- Keep it short.
- Do not restate canonical doctrine.
- `Next owner` must be allowed by the active owner.
- Use `done` only for terminal closure.
- Use `user` only for human decision, approval, access, secret, legal/business, or external constraint.

## Output compactness

Prefer concise operator output.

Normal shape:

```md
Decision:
Evidence:
Result:
Next:
```

Use long cards only when the active owner requires one.
