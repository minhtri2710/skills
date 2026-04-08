# CONTEXT Template: <Feature Name>

Use this template for `.beads/artifacts/<feature_slug>/CONTEXT.md`.
All sections are required. If a section is empty, write `N/A`.

## Feature Boundary

- Scope: <one-sentence statement of what this feature changes>
- Domain Type: <SEE | CALL | RUN | READ | ORGANIZE>

## Locked Decisions

| D-ID | Decision | Rationale | Source |
|------|----------|-----------|--------|
| D1 | <decision> | <why it is locked> | <user | agent default> |

D-ID format is `D<sequential number>` with no hyphen, for example `D1`, `D2`, `D3`.
Assign these during exploring, reference them in planning bead descriptions, and verify them during execution.

### Agent's Discretion

- <decision the agent may make without asking>

## Specific Ideas & References

- <user-provided reference, example, screenshot, prior art, or notable preference>

## Existing Code Context

- Reusable assets: <components, commands, helpers, templates, or docs already present>
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

- `beo-planning` reads: <which sections matter most for decomposition>
- `beo-validating` reads: <which sections matter most for validation>
- `beo-executing` reads: <which sections matter most for execution>
- `beo-reviewing` reads: <which sections matter most for review/UAT>
