# Lifecycle, Decomposition, and Triage Authority

> [!NOTE]
> This reference is subordinate to `references/kernel.md`. `references/kernel.md` is the canonical owner of BEO rules and invariants.

`br` and `bv` are the external Beads tools used for issue tracking and orientation.

## 1. Issue Triage and Claim Authority

All issue transitions are governed by strict claim invariants to avoid parallel conflict and preserve audit trails.

### Startup and Claim Sequence
1. **Orient**: `bv` robot triage for graph orientation only.
2. **Discover**: `br ready --json` for the canonical queue; `bv` only for track choice or graph hazards.
3. **Inspect**: Canonical issue details with `br show --json`.
4. **Classify atomicity**: Epic/feature -> `beo-plan`. Misclassified atomic issues -> `br update --type task`. Do not downgrade just to bypass decomposition.
5. **Claim**: `beo-plan` claims via `br update <issue-id> --claim --actor <actor> --json`. Later phases verify the claim matches, do not re-claim.
6. **Bind helper**: BEO helpers use `BR_ACTOR`/`BEO_ACTOR` set to the claimed assignee.
7. **Flush**: `br sync --flush-only` after a claim that must be visible to subsequent checks.

### Claim Authority and Phase Boundaries
- **Plan claim**: `beo-plan` establishes the initial claim.
- **Later phases**: Verify claim matches acting owner; do not re-claim.
- **Resume**: Only `beo-plan`, after user-driven resume or reassignment, may re-claim.
- **Parent claim**: Covers `PLAN.md` authoring, plan handoffs, and child bead creation. Atomic child work follows the one-claimed-atomic-issue invariant.

### Common Lifecycle Failure Triage

| Symptom | Cause | Resolution |
| --- | --- | --- |
| `issue is not atomic; route to beo-plan decomposition` or `issue must be decomposed before validation` | Issue type is `epic` or `feature` | Route to `beo-plan` decomposition; use `br update <issue-id> --type task` only when the issue is confirmed misclassified |
| `br issue claim does not match acting actor` or `BR_ACTOR or BEO_ACTOR is required` | Missing or mismatched actor identity | `export BR_ACTOR=<actor>`, then `br update <issue-id> --claim --actor <actor> --json` and `br sync --flush-only` |
| `error: unexpected argument '--message' found` | `br close` uses Beads-specific syntax, not git commit syntax | Use `br close <issue-id>` or `br close <issue-id> --reason "Completed" --actor <actor> --json`; never use `--message` |

---

## 2. Parent Handling and Decomposition

Only atomic beads can be validated or executed. Epics and Features must be decomposed.

### Decomposition Invariants
- Epic: never executed directly; Feature: must be decomposed; Atomic Bead: one independently approvable unit.

### File Conflict Prevention

Before finalizing decomposed beads, cross-reference their expected file scopes. If 2+ beads share a file, merge into one agent (preferred for 2-3) or add dependency edges to enforce ordering. Document the rationale in the parent PLAN decomposition strategy or child bead description.

### Epic Planning Mechanics
`beo-plan/SKILL.md` owns the full epic/feature planning procedure. The key mechanical commands used after `plan_validated`:
1. Create child atomic beads: `br create ... --json`
2. Add dependency edges: `br dep add ... --json`
3. Add parent summary comment referencing `PLAN.md` + child bead IDs: `br comments add ... --json`
4. Exit with `decomposition_recorded` dispatch.

Each child atomic bead description must be self-contained for implementation (task context, done criteria, expected scope, verification commands, dependencies, suggested mode/risk, atomicity rationale). Do not require child implementers to reread the parent `PLAN.md`; preserve parent traceability through Beads dependency edges and the parent decomposition comment.

---

## 3. Runtime Events

Runtime event kinds and payload contracts are canonical in `registry/runtime-event.schema.json`.

Runtime events are append-only non-normal state entries in `.beads/artifacts/<issue-id>/runtime-events.jsonl`. They are not written for normal transitions, and they are not plan-owned `TICKET.yaml` fields.

---

## 4. Fast Track Path (Quick Mode Only)

Fast track is an optional terminal shortcut for `quick` mode beads with `fast_track: true`.

### Normal Path (4 phases)
```
beo-plan -> beo-validate -> beo-execute -> beo-review -> done
```

### Fast Track Path (3 phases, when ALL verifications pass)
```
beo-plan -> beo-validate -> beo-execute -> done
```

### Fast Track Fallback (when ANY verification fails)

> See kernel.md §12 item 4. The fast track flag is ignored on failure; the bead routes to normal review.

### Fast Track Invariants
- Only for `quick` mode. Never `standard` or `strict`.
- Requires explicit (non-glob) file scope.
- Requires at least 1 verification command.
- All verifications must pass. No partial acceptance.
- `state.json` must record full verification results even on fast track.
- Review phase is skipped; `beo-execute` writes a terminal review block with auto-accept.
- The `state.review` block for fast-track is a **stub record** authored by `beo-execute`, not a real
  review record authored by `beo-review`. The `review.reviewed_by` field distinguishes the two:
  `"beo-execute"` for fast-track, `"beo-review"` for normal path. Stub records carry `verdict: null`,
  `route_condition_id: "executed_and_verified"`, `closed_in_br: false`, and no findings or
  done_criteria_coverage. They are not review verdicts and must not be treated as such.

---

## 5. Repair Loop Policy

Repair boundary is canonical in `references/phase-contracts.md`.

- `beo-review` emits exactly one route. Final verdict routes are accept, repair same scope, repair rescope, cannot deliver, or abandoned; `root_cause_diagnosis_needed` is a non-final diagnostic handoff route.
- Repair counters are recorded in `state.json` for review visibility only.
- Non-deliverable or abandoned issues route strictly to the user for manual decision; BEO never auto-closes or auto-abandons them on `br`.

---

## 6. Phase Handoff Boundaries

Phase transitions are artifact-validity-based, not conversation-turn-based:
1. A phase owner transitions only after writing durable state/evidence.
2. The next owner starts only after re-reading `br`, `TICKET.yaml`, `state.json`, `runtime-events.jsonl` when present, and phase-relevant registries.
3. No phase may run the next phase's commands until those artifacts have been re-read.

---

## 7. Transition & Closure Labels

Labels on `br` are advisory: `beo:atomic`, `beo:quick`, `beo:standard`, `beo:strict`, `beo:blocked-user`, `beo:ready-review`.

- **Completed**: `verdict_accept` -> `br close` with `--reason "Completed" --actor <actor> --json` + `beo:completed` label.
- **Abandoned**: `beo-review` records status in `state.json`, appends audit comment, applies `beo:abandoned` label, leaves issue open for manual closure.
- **Epic closure**: does not cascade. Close parent explicitly after all children are closed.
- **Syntax**: Use `br close <issue-id> --reason "Completed" --actor <actor> --json`. No `--message` flag.
