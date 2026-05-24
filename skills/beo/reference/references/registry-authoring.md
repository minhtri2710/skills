# Registry Authoring Hierarchy

This document defines the canonical update hierarchy for BEO-on-Beads registry and reference materials.

## Hierarchy

When registry and prose conflict, changes must propagate in this order:

1. **Registry schema** (`registry.schema.json`, `*-schema.json`) — Structural definitions and type constraints
2. **Registry data** (`command-contracts.json`, `pipeline.json`, `profiles.json`, etc.) — Declarative semantic contracts
3. **Scripts** (`beo_*.py`) — Operational implementation that reads and validates against registries
4. **References** (`references/*.md`) — Prose explanations and rationale
5. **Skills** (`*/SKILL.md`) — Repo-local operator cards that reference canonical registry contracts

## Authoring Rules

1. **Schema First**: Structural changes start in JSON schema definitions.
2. **Declarative Semantics**: Semantic constraints belong in registry data, not hidden in Python validation code.
3. **Scripts Read Registries**: Validation and helper scripts inspect declared registry metadata. Cross-field invariants for named canonical helpers or commands may be enforced in `beo_registry_check.py` when the registry cannot express them directly.
4. **References Explain Decisions**: Markdown references document rationale and edge cases but do not define authority.
5. **Skills Reference Registries**: Operator cards point to canonical registry contracts rather than duplicating them.

## Drift Prevention

- When updating command contracts, check that `beo_registry_check.py` validates declared fields and any named canonical invariants that prevent drift.
- When adding semantic constraints, prefer expanding registry schema before adding Python validation logic; use Python checks for cross-file, cross-field, or named canonical invariants the schema cannot express cleanly.
- When prose and registry disagree, update prose to match registry; do not silently assume prose is newer.

## Examples

### Good: Declarative Command Kind
```json
{
  "command_id": "beo.reservation.check",
  "kind": "read_gc_expired",
  "mutation_scope": "reservation_log_only",
  ...
}
```

### Bad: Implicit String Inspection
```python
if "check" in cmd_id and ".reservation." in cmd_id:
    # assume it GCs expired leases
```

### Good: Registry-Driven Validation
```python
if cmd.get("mutation_scope") == "reservation_log_only":
    if ".beads/beo-reservations.jsonl" not in cmd.get("writes", []):
        errors.append(f"{cmd_id} must declare reservation log writes")
```

## Semantic Metadata Fields

Command contracts should declare:

- `kind`: read | write | read_write_evidence | write_evidence | write_memory_index | read_gc_expired
- `mutation_scope`: none | lifecycle_only | reservation_log_only | evidence_only | memory_index_only | product_files
- `operation_class`: (optional) triage | discovery | maintenance | delivery | learning | memory_index_maintenance
- `authority`: Human-readable authority statement
- `writes`: Explicit list of paths or templates written
- `owner_allow`: List of BEO delivery owners authorized to use this command

## Authority Split

- **br**: Lifecycle mutations only, never product files
- **bv**: Read-only triage and orientation
- **beo helpers**: Evidence, validation, memory index maintenance
- **Obsidian/qmd**: Advisory learning notes and memory retrieval

Learning and memory operations never grant approval, execution permission, review verdicts, closure, or Human Gate resolution.

---

## Registry Versioning and Schema Migration Contract

### Backward Compatibility Guarantee
Minor registry mutations must preserve structural backward compatibility with prior schema versions (e.g. `beo-beads/v3` structures) to prevent breaking active ticket states.

### Breaking Changes Protocol
Schema-breaking changes require incrementing the registry major version, documenting changes in a formal ADR, and authoring a matching migration logic/script (e.g. `beo_migrate_state.py`) that executes under `beo-setup` to upgrade legacy ticket states.

### Append-Only Event Consistency
Event schemas must never be retroactively deleted or altered to avoid breaking historical audit logs.
