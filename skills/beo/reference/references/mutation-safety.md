# Mutation Safety

`beo-execute` mutates only paths approved in the current ticket projection.

## Path Rules

Reject absolute paths, empty paths, `.`, `..`, NUL, and symlink escapes. Protected paths (`.git/**`, `.beads/beads.db`, `.env*`, keys) are never writable by BEO.

## Changed-File Containment

Before review, compare changed files against `scope.files.allow`, `scope.files.forbid`, and declared generated outputs. Any undeclared or forbidden change fails closed.

## Path Overlap (Tree Semantics)

`beo-validate` must detect active scope conflicts using tree-aware semantics:
- **File-File**: Identical path mutation requested by two tickets.
- **Dir-File**: A ticket requests a file mutation inside a directory already claimed for mutation by another ticket.
- **Glob-Dir**: A broad glob pattern (e.g., `src/**`) covers a directory claimed by another ticket.
- **Parent-Child**: A generated output is nested within a directory currently being modified by another ticket.

### High-Risk Globs
- Broad globs (e.g., `**`, `src/**`, `*`, `/*`) are considered **High-Risk**.
- They must be avoided in favor of explicit file lists.
- If broad globs are required, they require explicit Human Gate authorization (type `authorization`) and must be flagged as a potential collision risk for all other tickets. `beo_check.py` enforces this requirement during validation.

### Safe Overlap Modeling
Active scope conflicts normally stop validation. Parallel execution is allowed only when an overlap is declared safe per-issue and per-path:
```yaml
scope:
  scope_overlap:
    status: safe
    overlaps:
      - issue_id: <other-id>
        paths:
          - <current-path> overlaps <other-path>
        safe_reason: dependency_ordered | disjoint_region | user_authorized
        evidence_ref: <required>
```
`beo_check.py` enforces this granular mapping; global bypasses are invalid.

## Prestate and Drift

Before first mutation, record hashes for approved files and generated outputs. On resume, unexplained drift stops execution.

## Side Effects and Stateful Systems

Strict mode is mandatory for external, stateful, or high-risk work.
- **Contracts**: Stateful systems require a contract (target, authorization, precheck, rollback/compensation, postcheck, blast radius) either in `external_side_effects.effects` or mapped to it.
- **Evidence**: Explicit Human Gate authorization, `STRICT.md`, `ROLLBACK.md`, and matching artifact hashes are mandatory.
- **No Bypass**: `strict.reason` cannot bypass the requirement for a side-effect contract in stateful systems.
