# Discovery Reference

Discovery rules for `beo-plan`.

## 1. Questions To Answer

Extract from `CONTEXT.md`:
- architecture: how the existing code is organized
- patterns: what the codebase already does this way
- constraints: what cannot change or what must be preserved
- external: what upstream APIs, libraries, or tools require

## 2. Discovery Shape

Default to one focused local discovery pass.

Escalate to 2-4 research lenses only when the feature is broad or high-risk and the runtime allows delegation:

| Lens | Focus |
| --- | --- |
| Architecture | file layout, module boundaries, imports, extension points |
| Pattern | similar features, reusable helpers, naming, tests, error handling |
| Constraint | types, contracts, performance, compatibility, versions |
| External | upstream docs, SDK usage, known issues, migration notes |

If delegation is unavailable, run the same lenses sequentially.

For refactors spanning 3 or more module boundaries, use the same narrow, non-overlapping lenses whether local or delegated.

## 3. Annotation Verification

Treat annotations as claims, not proof.

| Annotation | Verify by |
| --- | --- |
| `#[allow(dead_code)]` | remove it temporarily, compile, check for warnings |
| `@deprecated` | search for callers |
| `// TODO: remove` | verify the removal condition is actually met |

Record such items as `annotated - verify before removing`, not `confirmed dead code`.

## 4. Output

Write `.beads/artifacts/<feature_slug>/discovery.md` using:

```markdown
## Architecture Snapshot
- Relevant modules:
- Entry points:
- Data flow:
- Existing patterns:

## Pattern Search
- Similar features:
- Reusable helpers:
- Conventions to follow:

## Constraints & Risks
- Hard constraints:
- Dependency versions verified against lockfiles or registry:
- Performance bounds:
- Security surface:
- Licensing or policy constraints:

## Verified Annotations / Deletion Candidates
- Item:
  - Annotation:
  - Verification method:
  - Result:

## External Research
- Library docs:
- API references:
- Community patterns:
- Known pitfalls:

## Institutional Learnings
- Relevant `.beads/critical-patterns.md` entries:
- Relevant `.beads/learnings/` entries:

## Summary For Synthesis
- Key findings:
- Unresolved questions:
- Recommended approach direction:
```
