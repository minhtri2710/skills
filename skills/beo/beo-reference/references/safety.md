# Mutation Safety, Approval Validity, and Recovery

> [!NOTE]
> This reference is subordinate to [references/kernel.md](file:///Users/beowulf/Work/personal/beo-skills/skills/beo/beo-reference/references/kernel.md). `references/kernel.md` is the canonical owner of BEO rules and invariants.

## Scope precedence

`scope.files.forbid` is a negative constraint, not alternate scope.

Precedence:

1. protected paths
2. forbid patterns
3. allow paths
4. generated outputs

If a path matches both allow and forbid, it is forbidden.

## Approval validity

`PASS_EXECUTE` has no arbitrary elapsed-time invalidation.

Approval remains valid until a bound predicate fails, a newer artifact supersedes it, or a human/operator revokes or removes the authority.

Agents must not infer invalidity from elapsed time alone.

Canonical machine-readable predicates: `registry/approval-envelope.json`.

## Reservation

Reservation is BEO-local strict-mode path ownership evidence, not an OS/git lock.

It is active until explicitly released, superseded, or revoked. It does not expire by elapsed time.

Reservation prevents BEO from knowingly approving overlapping strict path ownership; it does not prevent external edits. Validation and review must still inspect dirty/prestate changes.

## Execution start

Execution starts only after a durable `state.json` update where:

- `phase` becomes `executing`,
- `execution.actor` is set,
- `execution.started_at` is set,
- approval validity predicates still hold.

No product file mutation may occur before this executing-state entry is written.

## Interrupted execution recovery

If re-entering with `state.phase = executing`:

1. Fresh-read `br`, `TICKET.yaml`, `state.json`, runtime events when present, and approval contracts.
2. Recompute approval validity predicates.
3. Inspect approved files and generated outputs for dirty changes.
4. Compare current dirty paths against `execution.changed_files` and approved scope.
5. If all dirty paths are approved and classifiable, continue execution.
6. If approval predicates fail, emit `approval_stale_or_invalid -> beo-validate`; `beo-execute` may recompute predicates and route, but must not mutate `approval.*`.
7. If dirty paths are outside approved scope and attributable to the interrupted execution, fail closed via `containment_review_needed -> beo-review` if that route exists, or via `root_cause_diagnosis_needed -> beo-debug`; never use normal `executed` for containment.
8. If outside-scope dirtiness is unattributed or appears pre-existing/external, fail closed to `root_cause_diagnosis_needed` rather than treating it as reviewable execution output.
9. If partial mutation cannot be classified, append a handoff event and route to `root_cause_diagnosis_needed`.
