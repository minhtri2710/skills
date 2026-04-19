# Discovery Reference

Detailed instructions for the Discovery step of `beo-plan`.

## Research Questions

From `CONTEXT.md`, extract:
- **Architecture**: How is the existing code structured?
- **Patterns**: What patterns does this codebase use?
- **Constraints**: What limits or requirements exist?
- **External**: What do external APIs/libraries require?

## Parallel Research

Default: run one focused discovery pass locally. For broad or high-risk features, escalate to 2–4 parallel research passes only when the current runtime and session policy allow delegation:

| Lens | Focus |
|------|-------|
| **Architecture** | File organization, module boundaries, import patterns, existing code to be modified or extended |
| **Pattern** | Similar features, reusable helpers, testing patterns, error handling, naming conventions, file placement |
| **Constraint** | Type system constraints, API contracts, performance requirements, compatibility, dependency versions |
| **External** *(if needed)* | API docs, SDK usage, known issues, migration guides, community best practices |

If delegation is unavailable for the current session, run the same lenses sequentially and then write the discovery report using the Output Template below.

For refactoring work touching 3+ module boundaries, use parallel or multi-pass audit with narrow, non-overlapping mandates (e.g., structural/module, architecture/UX, domain/backend). Run them in parallel only when delegation is available; otherwise execute the same audit lenses sequentially.

## Annotation Verification

When discovery inventories items by annotation, treat annotations as human claims, not compiler guarantees. Verify each independently before including in the plan:

| Annotation | Verification |
|-----------|-------------|
| `#[allow(dead_code)]` | Remove annotation, compile, check for warnings |
| `@deprecated` | Grep for callers |
| `// TODO: remove` | Verify the removal condition is met |

List annotated items as "annotated — verify before removing", not "confirmed dead code." Record findings under `## Verified Annotations / Deletion Candidates` in the Output Template.

## Synthesis

Combine research into a discovery summary covering: what exists today, patterns to follow, constraints, and external factors. Write to `.beads/artifacts/<feature_slug>/discovery.md` using the Output Template below.

---

## Output Template

## Architecture Snapshot

- Relevant modules:
- Entry points:
- Data flow:
- Existing patterns:

## Pattern Search

- Similar features in the codebase:
- Reusable components or helpers:
- Established conventions to follow:

## Constraints & Risks

- Hard constraints:
- Dependency versions verified against registry or lockfiles:
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

- Relevant entries from `.beads/critical-patterns.md`:
- Relevant entries from `.beads/learnings/`:

## Summary for Synthesis

- Key findings:
- Unresolved questions:
- Recommended approach direction:
