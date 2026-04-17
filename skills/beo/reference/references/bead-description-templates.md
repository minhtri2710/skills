# Bead Description Templates

Canonical Markdown templates for beo task descriptions.

## Table of Contents

- [Planned Task Bead Template](#planned-task-bead-template)
- [Reactive Fix Bead Template](#reactive-fix-bead-template)
- [Follow-Up Bead Template](#follow-up-bead-template)

## Usage Rules

- Planned execution beads use the **Planned Task Bead Template**.
- Reactive repair work uses the **Reactive Fix Bead Template**.
- Review/debug follow-up work uses the **Follow-Up Bead Template**.
- Keep bead descriptions self-sufficient enough that a fresh worker can act from the bead plus referenced artifacts.
- Do not duplicate whole artifacts into the bead when references are sufficient.

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

Checklist:
- Do not copy all of `CONTEXT.md` into the bead. Reference the relevant decision(s).
- Write the bead so a fresh worker can build from it alone.

---

## Reactive Fix Bead Template

Use for beads created by `beo-review`, `beo-debug`, or other canonical reactive repair flows. These beads do not need Story Context but still require a complete Markdown spec.

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

---

## Follow-Up Bead Template

Use for non-blocking review/debug follow-up work that is intentionally deferred.

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
