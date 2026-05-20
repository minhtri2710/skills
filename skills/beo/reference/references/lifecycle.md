# Lifecycle, Decomposition, and Triage Authority

`br` is canonical for issue identity, lifecycle, claims, comments, ready queue, and closure. `bv` drives structural orientation, triage, track planning, and cycle validation. BEO records safety states and transitions in `TICKET.md`.

## 1. Issue Triage and Claim Authority

All issue transitions are governed by strict claim invariants to avoid parallel conflict and preserve audit trails.

### Startup and Claim Sequence
1. **Discover**: Run `br ready --json` or query triage with `bv --robot-triage -f json --no-cache`.
2. **Inspect**: Check specific issue details with `br show <issue-id> --json`.
3. **Claim**: Before any owned write, ticket mutation, decomposition, or product mutation, claim the issue:
   ```bash
   ACTOR="${BR_ACTOR:-${AGENT_NAME:-assistant}}"
   export BEO_ACTOR="$ACTOR"
   rtk br update --actor "$ACTOR" <issue-id> --claim --json
   ```
   `--claim` sets the assignee and sets the status to `in_progress` atomically. If setup cannot prove that `--claim` is atomically supported, BEO must fail closed.

### 6-Step Compact Protocol (Quick Path)
For low-risk repository-only edits (e.g., docstrings, READMEs, simple refactors):
1. **Show & Claim**: Run `br show` and claim the issue.
2. **Intake**: Create a minimal `TICKET.md` with request, done criteria, and atomic scope.
3. **Validate**: Run `beo-validate` to obtain `PASS_EXECUTE`.
4. **Execute**: Perform edits strictly restricted to `scope.files.allow`.
5. **Review**: Emit acceptance verdict.
6. **Close**: Run `br close <issue-id>` only after review acceptance.

---

## 2. Track Planning and Robot Triage

BEO leverages `beads_viewer` (`bv`) to analyze backlog tracks, bottlenecks, and dependencies dynamically during the planning phase:
- **Triage**: `bv --robot-triage -f json --no-cache` returns ready-to-run recommendations, quick wins, and priority scores.
- **Track Planning**: `bv --robot-plan -f json --no-cache` outputs independent parallel execution tracks containing unblocking sequences.
- **Dependency Health**: `bv --robot-insights -f json --no-cache` checks for graph bottlenecks, articulation points, slack lists, and DAG cycles.

> [!IMPORTANT]
> If `bv --robot-insights` detects any cycle (when `.Cycles` is not empty or `has_cycles` is true), the plan must prioritize cycle-break operations before mutating any code.

---

## 3. Parent Handling and Decomposition

Only atomic beads can be validated or executed. Epics and Features must be decomposed.

### Decomposition Invariants
- **Epic**: User-facing milestone; never executed directly.
- **Feature**: Capability group; must be decomposed.
- **Atomic Bead**: One independently approvable execution unit. Must have one done target, one risk posture, one approval projection, a small explicit allowed file set, one verification contract, one verdict, and an independent revert/repair path.

### Parent-Child Mechanics
If a bead is not atomic:
1. `beo-plan` creates child atomic beads using `br create --actor "$ACTOR" ...`.
2. Add dependency edges using `br dep add --actor "$ACTOR" <dependent-id> <blocker-id> --json`.
3. Add a summary comment to the parent bead with `br comments add`.
4. Exit planning with `decomposition_recorded`.
5. Parent epics remain open until Beads reports all children are closed.

---

## 4. Runtime Events

Runtime events are append-only non-normal state entries in `TICKET.md`. They are not written for normal transitions.

### Types & Kinds
- `user_stop`: Emitted when a Human Gate blocks progress. Mark gate status `unresolved`, comment on the issue, and apply the `beo:blocked-user` label.
- `handoff` / `return`: Used for the `debug` subroutine handoff to `beo-debug`.
- `change_request`: Subtypes include `scope_delta`, `repair_same_scope`, and `repair_rescope`.
- `abandon`: Used when the work is cancelled or aborted.
- `learning_candidate`: Emitted post-accept by `beo-review` or `beo-debug` to trigger the learning loop.

---

## 5. Transition Labels

Labels are advisory hints and never replace formal ticket fields:
- `beo:atomic`, `beo:quick`, `beo:standard`, `beo:strict`, `beo:blocked-user`, `beo:ready-review`.
