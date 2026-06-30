# BEO Kernel (Operator Rules)

BEO is a thin, repo-local safety layer over Beads. It is not an independent workflow manager. Work on one verified issue at a time.

## 1. Delivery Loop & Authority Split

```text
beo-plan -> beo-validate -> beo-execute -> beo-review
```

- **`br`**: Owns issue lifecycle, claim, dependencies, comments, ready queue, and closure.
- **`bv`**: Optional read-only graph orientation (never required for delivery readiness).
- **`TICKET.json`**: Declarative contract owning request, done criteria, approved scope, verification commands, and risk/mode contracts. Must not include claim/lifecycle fields.
- **`state.json`**: Owns approval, execution, and review state. Must not mirror lifecycle or closure state except as evidence refs or review verdict.
- **`runtime-events.jsonl`**: Optional append-only log of non-normal events. Must not record normal transition events.
- **qmd/Obsidian**: Optional advisory memory. Cannot grant approval, execution permission, verdicts, closure, or Human Gate resolution.

---

## 2. Hard Invariants

1. **Atomic Claim**: Work on exactly one claimed atomic issue at a time. Verify claim matches acting actor using `br show --json`.
2. **Fresh-Read**: Fresh-read `br` status and artifacts at each phase entry.
3. **Approval Gates**: Mutate product files only after `PASS_EXECUTE` is written to `state.json`.
4. **Scope Containment**: Mutate only `scope.files.allow` and declared `scope.generated_outputs`.
5. **Human Gates**: Broad globs require explicit resolved Human Gate authorization in `TICKET.json`.
6. **Side-Effects**: Stateful or external side effects require `strict` mode contracts in `TICKET.json`.
7. **Dirty Prestate**: Dirty approved files or generated outputs before validation fail closed.
8. **No Expiry**: BEO assertions and approvals do not expire by elapsed time.
9. **Closure Rule**: Only `beo-review` may close accepted work through `br` (strictly via `verdict_accept`).
10. **Evidence Integrity**: All evidence refs must be durable, repo-relative, and free of secrets or unredacted customer data.
11. **CLI Surface**: All Beads state reads and mutations go through the `br`/`bv` CLI — `br ready --json`, `br show --json`, `br create`, `br close`, `br dep`, `br coordination status --json`. Never generate scripts (Python/shell) to edit `issues.jsonl`/`beads.db` or to parse them when a `br` command exists; direct writes bypass CLI locking, validation, and the `--actor` audit trail that phases rely on. Command detail lives in `references/lifecycle.md`.

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

## 7. Worktree Isolation Policy

Worktree isolation is an optional strict-mode feature for full filesystem isolation.

1. **Creation**: Worktree is created by `beo-validate` before `PASS_EXECUTE`. Requires a clean git tree.
2. **Ownership**: The worktree branch follows the naming convention `beo/<issue-id>/<actor>/<timestamp>`.
3. **Execution**: All mutations happen inside the worktree. The main repo remains untouched.
4. **Merge**: Only `beo-review` on `verdict_accept` may merge the worktree branch into the main repo.
5. **Cleanup**: Worktree is always cleaned up on terminal routes (accept, cannot_deliver, abandoned) and repair routes.
6. **Idempotency**: If a worktree already exists for the same issue (e.g., agent re-entry), the existing worktree is reused.
7. **No Bypass**: Worktree isolation does not replace reservation, dirty prestate checks, or approval validity. All standard strict-mode invariants still apply.

---

## 8. Memory & Learning Boundary

- **Recall**: Opt-in and advisory only. Prior lessons do not grant approval or authority.
- **Learning**: Save lessons via `beo-learn` only when an explicit `learning_candidate` exists or the user requests it. Default Vault: `<vault>/beo-learnings/`. Fallback: `.beads/learnings/`.

---

## 9. Climate Control Policy

`beo-climate` is a proactive maintenance skill that runs periodic scans of BEO harness files.

1. **Advisory only**: `beo-climate` never mutates delivery state, product files, or BEO control-plane files directly.
2. **Findings become issues**: Scan results become Beads issues for human or `beo-author` triage.
3. **Auto-heal allowlist**: Only safe, mechanical fix types may auto-route to `beo-author` via `climate_self_heal`. The allowlist is defined in `beo-climate/config.json`.
4. **No delivery authority**: `beo-climate` cannot grant `PASS_EXECUTE`, close issues, or alter review verdicts.
5. **Cadence**: Default is weekly. Configurable in `beo-climate/config.json`. Runs as a background agent, not blocking delivery.

## 10. Harness Mutation Guardrails

Delivery agents (beo-execute, beo-review) may propose BEO harness changes through a controlled handoff.

1. **Proposal only**: Delivery agents write `harness-proposal.json`. They never mutate harness files directly.
2. **Scope restriction**: Proposals must target paths under `skills/beo/`. Product delivery scope proposals are rejected.
3. **beo-author gate**: Only `beo-author` applies harness changes. It reviews the proposal, validates safety, and applies or declines.
4. **Idempotency**: Multiple `harness_change_needed` emissions for the same proposal are idempotent. The proposal hash is tracked in state.
5. **No authority expansion**: A harness proposal cannot grant new permissions to the proposing agent. It changes the harness for future beads.
6. **Invariant preservation**: Harness changes must not weaken the hard invariants in this kernel. `beo-author` must verify this before applying.
7. **Continuation**: After `beo-author` returns, the delivery agent re-reads state and continues if the bead remains valid.

## 11. Repair Boundaries

- **`repair_same_scope`**: Used when the approved file set, generated outputs, done criteria, verification commands, mode, and Human Gates remain unchanged. Routes back to `beo-validate` (does not require re-planning).
- **`repair_rescope`**: Used when scope (allow/forbid), done criteria, verification commands, mode, or Human Gates must change. Routes back to `beo-plan` for re-authoring.

---

## 12. Fast Track (Quick Mode Optimization)

Fast track is an opt-in flag for `quick` mode beads only. When `TICKET.json` has `fast_track: true`:

1. All `quick` mode invariants still apply (explicit file scope, at least one verification command).
2. `beo-validate` writes `PASS_EXECUTE` as normal. Fast track does not skip validation.
3. `beo-execute` runs all verification commands. If ALL pass, emits `executed_and_verified` -> done (bypasses review).
4. If ANY verification fails, falls back to `executed` -> `beo-review` (normal path).
5. Fast track file scope must use explicit paths, not globs. This ensures deterministic scope enforcement.
6. Evidence integrity still applies: all verification results and changed files must be recorded in `state.json`.
7. `fast_track` is never allowed for `standard` or `strict` mode beads.

The fast track exists to reduce phase overhead for trivial, low-risk changes where review ceremony adds no safety value.

## 13. Interrupted Execution Recovery

If re-entering with `state.phase = executing`:
1. Recompute approval validity predicates and check dirty paths.
2. If predicates fail, route to `beo-validate`.
3. If dirty paths are outside approved scope and attributable to the interrupted run, route to `beo-review` via `containment_review_needed` or `beo-debug` via `root_cause_diagnosis_needed`.
4. If outside-scope dirtiness is unattributed or partial mutation cannot be classified, route to `beo-debug`.

