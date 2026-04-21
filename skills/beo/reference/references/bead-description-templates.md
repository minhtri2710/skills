# Bead Description Templates

Canonical task-description templates for beo beads.

Use:
- planned execution work -> `Planned Task Bead Template`
- reactive repair work -> `Reactive Fix Bead Template`
- deferred non-blocking follow-up work -> `Follow-Up Bead Template`

Rules:
- keep the bead self-sufficient enough for a fresh worker
- reference the relevant decisions and artifacts; do not paste whole artifacts into the bead
- include exact file scope, acceptance criteria, and verification

## Planned Task Bead Template

Use for normal planned execution beads created during planning.

```markdown
## Objective

<specific deliverable for this bead>

## Story Context

- Story: <story name>
- Why this exists now: <current-phase reason>

## Files

- <exact file path>
- <exact file path>

## Implementation

- <required change>
- <required change>

## Acceptance Criteria

- <observable condition>
- <observable condition>

## Verification

- <command or check>
- <command or check>

## References

- `CONTEXT.md`: <relevant decision IDs or sections>
- `<artifact>`: <relevant section>
```

## Reactive Fix Bead Template

Use for beads created by `beo-review`, `beo-debug`, or another canonical reactive-fix path. Story context is optional, but the spec still must be complete.

```markdown
## Objective

<specific defect to fix>

## Files

- <exact file path>
- <exact file path>

## What To Fix

- <broken behavior>
- <required correction>

## Acceptance Criteria

- <condition proving the defect is fixed>
- <condition proving no intended scope drift>

## Verification

- <command or check>
- <command or check>

## Traceability

- Origin bead: <bead id>
- Trigger: <review finding or debug root cause>
```

## Follow-Up Bead Template

Use for non-blocking review or debug follow-up work that is intentionally deferred.

```markdown
## Objective

<follow-up improvement>

## Why Deferred

<why this is not blocking the current acceptance path>

## Files

- <exact file path>
- <exact file path>

## Acceptance Criteria

- <observable condition>
- <observable condition>

## Verification

- <command or check>
- <command or check>

## Traceability

- Source: <review finding, debug note, or decision>
```
