# CONTEXT Template: <Feature Name>

Use for `.beads/artifacts/<feature_slug>/CONTEXT.md`. All sections required; write `N/A` if empty.

## Feature Boundary

- Scope: <one-sentence statement of what this feature changes>
- Scope Classification: <Quick | Standard | Deep>
- Domain Type: <SEE | CALL | RUN | READ | ORGANIZE>

Quick: all conditions in `beo-reference` → `references/pipeline-contracts.md` § Quick-Scope Definition met.
Standard: needs planning, beads, at least one review cycle (days to a week).
Deep: large, cross-cutting, likely multi-phase with parallel execution (weeks).

## Locked Decisions

| D-ID | Decision | Rationale | Source |
|------|----------|-----------|--------|
| D1 | <decision> | <why locked> | <user \| agent default> |

D-ID format: `D<number>` (no hyphen). Assign during exploring, reference in planning, verify during execution.

### Agent's Discretion

- <decision the agent may make without asking>

## Specific Ideas & References

- <user-provided reference, example, screenshot, prior art, or preference>

## Existing Code Context

- Reusable assets: <components, commands, helpers, templates, docs already present>
- Established patterns: <repo conventions that should shape the solution>
- Integration points: <files, modules, commands, or artifacts the feature will touch>

## Canonical References

- <spec, RFC, product doc, upstream API doc, or other source of truth>

## Outstanding Questions

### Resolve Before Planning

- <question that blocks artifact creation>

### Deferred to Planning

- <question safe to resolve during decomposition>

## Deferred Ideas

- <explicitly out-of-scope idea to revisit later>

## Handoff Note

- `beo-plan` reads: <sections for decomposition>
- `beo-validate` reads: <sections for validation>
- `beo-execute` reads: <sections for execution>
- `beo-review` reads: <sections for review/UAT>
