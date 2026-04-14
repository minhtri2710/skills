# Discovery Reference

Detailed instructions for the Discovery step of `beo-planning`.

## Research Questions

From CONTEXT.md, extract:
- **Architecture questions**: "How is the existing code structured?"
- **Pattern questions**: "What patterns does this codebase use?"
- **Constraint questions**: "What limits or requirements exist?"
- **External questions**: "What do external APIs/libraries require?"

## Parallel Research Subagents

Launch 2-4 parallel research subagents using the session's normal subagent/task-dispatch mechanism, focused on:

1. **Architecture Agent**: Explore codebase structure relevant to the feature
   - File organization, module boundaries, import patterns
   - Existing code that will be modified or extended

2. **Pattern Agent**: Identify patterns to follow
   - How similar features are implemented
   - Testing patterns, error handling conventions
   - Naming conventions, file placement rules

3. **Constraint Agent**: Discover hard limits
   - Type system constraints, API contracts
   - Performance requirements, compatibility needs
   - Dependencies and version constraints

4. **External Agent** (if needed): Research external dependencies
   - API documentation, SDK usage patterns
   - Known issues, migration guides
   - Community best practices

Each agent writes findings to a structured format. Collect all results.
Write the discovery report using the Output Template section below.

For refactoring work touching 3+ module boundaries, use multi-agent audit with narrow, non-overlapping mandates (e.g., structural/module, architecture/UX, domain/backend). Different architectural lenses reveal different issues that a single-perspective audit would miss.

## Annotation Verification

When discovery inventories items by annotation (`#[allow(dead_code)]`, `// TODO`, `@deprecated`, `@SuppressWarnings`), treat annotations as human claims, not compiler guarantees. For each annotated item, verify the claim independently before including it in the plan:

| Annotation | Verification |
|-----------|-------------|
| `#[allow(dead_code)]` | Remove annotation, compile, check for warnings |
| `@deprecated` | Grep for callers |
| `// TODO: remove` | Verify the removal condition is met |

Discovery artifacts should list annotated items as "annotated — verify before removing" not "confirmed dead code."
When annotation-verification findings exist, record them under `## Verified Annotations / Deletion Candidates` in the Output Template section below.

## Synthesis

Combine research into a discovery summary:
- What exists today (architecture)
- What patterns to follow (conventions)
- What constraints apply (limits)
- What external factors matter (dependencies)

Write findings to `.beads/artifacts/<feature_slug>/discovery.md`.
Use the Output Template section below to preserve the architecture, pattern, constraint, external research, and verified-annotation sections consistently.

---

## Output Template

## Agent A - Architecture Snapshot

- Relevant modules:
- Entry points:
- Data flow:
- Existing patterns:

## Agent B - Pattern Search

- Similar features in the codebase:
- Reusable components or helpers:
- Established conventions to follow:

## Agent C - Constraints & Risks

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

## Agent D - External Research

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
