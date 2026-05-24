# Mutation Safety, Approval, and Execution Modes

This document defines the strict safety boundaries for BEO to prevent unintended side effects, secure authorization boundaries, and avoid parallel conflict.

---

## 1. Execution Modes

See `beo-reference` -> `registry/profiles.json` for mode definitions (quick/standard/strict), requirements, independence policy, and flow profiles.

---

## 2. Mutation Safety & Path Rules

`beo-execute` must only mutate paths approved in the current ticket projection.

### Path Isolation & Containment
- **Path Rejections**: Reject absolute paths, empty paths, `.`, `..`, NUL, and symlink escapes.
- **Protected Paths**: `profiles.json` `protected_path_defaults` is the canonical source for protected path defaults; this document intentionally does not duplicate that list or matching logic.
- **Containment Check**: Before review, compare changed files against `scope.files.allow`, `scope.files.forbid`, and declared generated outputs. Any undeclared or forbidden change fails closed.
- **Prestate Integrity**: Record cryptographic hashes for all approved files and expected generated outputs before first mutation. Prestate refs may distinguish `existing`, `expected_missing`, and `generated_declared` paths so generated outputs that do not exist yet are explicit. On resume, unexplained file drift stops execution immediately.

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

### 2.5 Path Reservation & Leases

To prevent parallel conflict *before* validation or execution, BEO uses a BEO-local pre-hoc lease-based path reservation system implemented by `beo-reference` -> `scripts/beo_reservation.py`. It is not a native `br` feature. `profiles.json` `reservation_policy` is canonical for when a current reservation is required.
1. **Creation**: `beo-plan` creates a path reservation in `.beads/beo-reservations.jsonl` only when the selected profile or risk context requires one. Quick and standard work are not forced to reserve by default, but strict mode, declared parallel risk, detected overlap/concurrency risk, or broad Human-Gate-authorized scope require a current reservation.
2. **Actor binding**: Reservation commands derive actor identity from `BEO_ACTOR` / `BR_ACTOR`; run them with the same actor identity that holds the Beads claim.
3. **Fencing**: Leases are identified by a unique `reservation_id` and have a default TTL of 3600 seconds (1 hour). Expired leases are automatically garbage-collected.
4. **Validation**: `beo-validate` always checks active reservations for conflicts and requires a current covering reservation only when `profiles.json` policy requires it.
5. **Renewal**: `beo-execute` renews active leases before long-running mutation or verification using `beo-reference` -> `scripts/beo_reservation.py renew --issue <issue-id> --reservation-id <reservation-id>`.
6. **Release**: `beo-review` releases the path reservation immediately upon emitting a final verdict (`verdict_accept`, `cannot_deliver`, or `abandoned`).


### 2.6 Working Tree Baseline Policy

**Pre-Flight State (during Validation)**: Before issuing `PASS_EXECUTE`, validate that the approved `scope.files.allow` paths have no uncommitted changes. Unrelated dirty files outside the approved scope are permitted but must be documented in ticket assumptions. Scope-overlapping dirty files must trigger a fail-closed action.

**Mid-Execution Drift**: Prestate hashes catch file drift on resume (§2 existing). Files in `scope.files.forbid` changed externally → stop immediately. Files outside scope entirely → log warning, continue. Files in `scope.files.allow` changed externally (not by current execution) → stop, require user confirmation.

**Generated Output Baseline**: `expected_missing` prestate type permits non-existent generated outputs. Existing generated outputs must be hashed as `existing`. Any generated outputs marked `expected_missing` must be asserted as absent from the filesystem before execution begins; pre-existing dirty outputs modified outside current execution → fail closed.

---

## 3. Stateful & External Systems

Strict mode is mandatory for stateful integrations. `beo-reference` -> `registry/profiles.json` owns mode/profile requirements, `beo-reference` -> `registry/command-contracts.json` owns side-effect command-contract fields, `beo-reference` -> `registry/ticket-schema.json` owns ticket field shape, and `beo-reference` -> `registry/approval-envelope.json` owns hash/freshness binding. `strict.reason` explains why strict mode applies; it never substitutes for the side-effect contract.

---

## 4. Approval Lifecycle

See `beo-reference` -> `registry/approval-envelope.json` for projection fields, hash rules, hard invalidators, and soft drift policy.
