# Mutation Safety, Approval, and Execution Modes

This document defines the strict safety boundaries for BEO to prevent unintended side effects, secure authorization boundaries, and avoid parallel conflict.

---

## 1. Execution Modes

See `registry/profiles.json` for mode definitions (quick/standard/strict), requirements, independence policy, and flow profiles.

---

## 2. Mutation Safety & Path Rules

`beo-execute` must only mutate paths approved in the current ticket projection.

### Path Isolation & Containment
- **Path Rejections**: Reject absolute paths, empty paths, `.`, `..`, NUL, and symlink escapes.
- **Protected Paths**: See `profiles.json` `protected_path_defaults` for the canonical list.
- **Containment Check**: Before review, compare changed files against `scope.files.allow`, `scope.files.forbid`, and declared generated outputs. Any undeclared or forbidden change fails closed.
- **Prestate Integrity**: Record cryptographic hashes for all approved files and expected generated outputs before first mutation. On resume, unexplained file drift stops execution immediately.

### Tree-Aware Scope Overlap
`beo-validate` detects active scope conflicts using tree-aware semantics to prevent parallel resource starvation or dirty writes:
1. **File-File**: Identical path mutation requested by two tickets.
2. **Dir-File**: A ticket requests a file mutation inside a directory already claimed for mutation by another ticket.
3. **Glob-Dir**: A broad glob pattern (e.g., `src/**`) covers a directory claimed by another ticket.
4. **Parent-Child**: A generated output is nested within a directory currently being modified by another ticket.

> [!WARNING]
> Broad/High-Risk globs (e.g. `**`, `src/**`, `*`, `/*`) must be avoided in favor of explicit file lists. If broad globs are required, they require explicit Human Gate authorization (`authorization` type) and are flagged by `beo_check.py` as collision risks.

#### Declarative Overlap Resolvers
Parallel execution on overlapping paths is allowed *only* when declared safe per-issue and per-path:
```yaml
scope:
  scope_overlap:
    status: safe
    overlaps:
      - issue_id: <other-id>
        paths:
          - current: <current-path>
            other: <other-path>
        safe_reason: dependency_ordered | disjoint_region | user_authorized
        evidence_ref: <required>
```
`beo_check.py` enforces this granular mapping; global bypasses are invalid.

---

## 3. Stateful & External Systems

Strict mode is mandatory for stateful integrations. `profiles.json` owns mode/profile requirements, `command-contracts.json` owns side-effect command-contract fields, `ticket-schema.json` owns ticket field shape, and `approval-envelope.json` owns hash/freshness binding. `strict.reason` explains why strict mode applies; it never substitutes for the side-effect contract.

---

## 4. Approval Lifecycle

See `registry/approval-envelope.json` for projection fields, hash rules, hard invalidators, and soft drift policy.
