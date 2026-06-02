# BEO Kernel (Operator Rules)

BEO is a thin, repo-local safety layer over Beads. It is not an independent workflow manager. Work on one verified issue at a time.

## 1. Delivery Loop & Authority Split

```text
beo-plan -> beo-validate -> beo-execute -> beo-review
```

- **`br`**: Owns issue lifecycle, claim, dependencies, comments, ready queue, and closure.
- **`bv`**: Optional read-only graph orientation (never required for delivery readiness).
- **`TICKET.yaml`**: Declarative contract owning request, done criteria, approved scope, verification commands, and risk/mode contracts. Must not include claim/lifecycle fields.
- **`state.json`**: Owns approval, execution, and review state. Must not mirror lifecycle or closure state except as evidence refs or review verdict.
- **`runtime-events.jsonl`**: Optional append-only log of non-normal events. Must not record normal transition events.
- **qmd/Obsidian**: Optional advisory memory. Cannot grant approval, execution permission, verdicts, closure, or Human Gate resolution.

---

## 2. Hard Invariants

1. **Atomic Claim**: Work on exactly one claimed atomic issue at a time. Verify claim matches acting actor using `br show --json`.
2. **Fresh-Read**: Fresh-read `br` status and artifacts at each phase entry.
3. **Approval Gates**: Mutate product files only after `PASS_EXECUTE` is written to `state.json`.
4. **Scope Containment**: Mutate only `scope.files.allow` and declared `scope.generated_outputs`.
5. **Human Gates**: Broad globs require explicit resolved Human Gate authorization in `TICKET.yaml`.
6. **Side-Effects**: Stateful or external side effects require `strict` mode contracts in `TICKET.yaml`.
7. **Dirty Prestate**: Dirty approved files or generated outputs before validation fail closed.
8. **No Expiry**: BEO assertions and approvals do not expire by elapsed time.
9. **Closure Rule**: Only `beo-review` may close accepted work through `br` (strictly via `verdict_accept`).
10. **Evidence Integrity**: All evidence refs must be durable, repo-relative, and free of secrets or unredacted customer data.

---

## 3. Risk Modes Summary

BEO safety ceremony scales with the risk tier:
- **`quick`**: Repo-only low-risk work. Requires explicit file scope and at least one verification command. No `risk` or `strict` blocks allowed.
- **`standard`**: Medium-risk work. Quick requirements plus explicit `risk.summary` and `risk.rollback` plan. No `strict` block allowed.
- **`strict`**: High-risk work. Standard requirements plus resolved human gates, side-effect contracts, and a current actor-matching BEO reservation.

---

## 4. Approval Validity

`PASS_EXECUTE` remains valid until:
1. A bound predicate fails (e.g., ticket file hash mismatch, repo head drift).
2. A newer artifact supersedes it.
3. An operator explicitly revokes or removes the approval.
Agents must not infer invalidity from age/elapsed-time alone.

---

## 5. Runtime Events Policy

`runtime-events.jsonl` is optional abnormal-event evidence:
- **Normal transitions** (plan, validate, execute, review success) are represented in `state.json`, NOT runtime events.
- **Quick/Standard** modes do not create it for normal transitions.
- **Strict** mode or abnormal handoffs (e.g., routing to `beo-debug`, `user_stop` on blocked human gates) may write non-normal events.

---

## 6. Reservations Policy

Reservations are BEO-local strict-mode path ownership evidence:
- **Quick/Standard** work uses `br claim`, branch discipline, and dirty prestate checks instead of reservations.
- **Strict** work requires a current active actor-matching reservation.
- A reservation is not an OS/git lock and never replaces dirty checks.

---

## 7. Memory & Learning Boundary

- **Recall**: Opt-in and advisory only. Prior lessons do not grant approval or authority.
- **Learning**: Save lessons via `beo-learn` only when an explicit `learning_candidate` exists or the user requests it. Default Vault: `<vault>/beo-learnings/`. Fallback: `.beads/learnings/`.

---

## 8. Repair Boundaries

- **`repair_same_scope`**: Used when the approved file set, generated outputs, done criteria, verification commands, mode, and Human Gates remain unchanged. Routes back to `beo-validate` (does not require re-planning).
- **`repair_rescope`**: Used when scope (allow/forbid), done criteria, verification commands, mode, or Human Gates must change. Routes back to `beo-plan` for re-authoring.

---

## 9. Interrupted Execution Recovery

If re-entering with `state.phase = executing`:
1. Recompute approval validity predicates and check dirty paths.
2. If predicates fail, route to `beo-validate`.
3. If dirty paths are outside approved scope and attributable to the interrupted run, route to `beo-review` via `containment_review_needed` or `beo-debug` via `root_cause_diagnosis_needed`.
4. If outside-scope dirtiness is unattributed or partial mutation cannot be classified, route to `beo-debug`.

