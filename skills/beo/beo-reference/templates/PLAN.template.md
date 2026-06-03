# PLAN for <parent-issue-id>

## Parent bead

- Parent issue id: `<issue-id>`
- Parent type: `epic | feature`
- Source request: `<short user/request summary>`
- Planning actor: `<actor>`

## Decision summary

State the recommended implementation direction in 3-7 bullets.

## Clarification record

List clarification questions asked during planning, or write `None — safe defaults and assumptions captured below` when no question is needed.
Each question asked must include:

- Question
- Why it matters
- Recommended default
- User answer, or fallback assumption if unanswered

## Requirements

### Goals

- `<goal>`

### Non-goals

- `<explicit non-goal>`

### Assumptions

- `<assumption>`

### Constraints

- `<technical, safety, product, repo, or workflow constraint>`

## Overall completion criteria

List the parent-level outcomes that make the full decomposed epic/feature complete.

- `<parent-level completion criterion>`

## Scope

### In scope

- `<in-scope area>`

### Out of scope

- `<out-of-scope area>`

### Expected touched areas

- `<expected file/path/module area, if known>`

## Risks

| Risk | Impact | Mitigation | Affects decomposition? |
|---|---|---|---|
| `<risk>` | `<impact>` | `<mitigation>` | `yes/no` |

## Verification strategy

Describe how completion will be verified across the decomposed atomic beads.

Include expected command categories, manual review expectations, and any evidence that child beads should produce.

## Decomposition strategy

Explain the boundary rule used to split atomic child beads.

A valid atomic child bead must have:

- one independently approvable task,
- clear done criteria,
- expected file/scope boundary,
- verification command or review method,
- independent repair path,
- explicit dependency/blocker links when needed.

## Proposed atomic beads

| Temp id | Title | Description | Done criteria | Expected scope | Verification | Dependencies | Suggested mode/risk |
|---|---|---|---|---|---|---|---|
| `A1` | `<title>` | `<one paragraph implementation task>` | `<criteria>` | `<files/areas>` | `<commands/checks>` | `<none/Ax>` | `<quick/standard/strict + mode rationale; risk/rollback, human gate, side-effect, reservation, or strict-contract notes when needed>` |

## Dependency graph

Describe parent-child and child-child dependencies before creating Beads edges.

```text
<parent-issue-id>
  -> A1
  -> A2 depends on A1
```

## Open decisions

Only list decisions that genuinely block safe decomposition and require user/operator authority. Agent-resolvable uncertainty should become an explicit assumption or recommended default instead of an open decision. `plan_validated` requires no actual blocking decision rows; non-blocking follow-up notes belong in assumptions, risks, or a separate follow-up note, not this blocking-decision table. Any blocking open decision routes `user_review_needed`.

If no blocking decisions remain, write `None — no blocking user/operator decisions remain` and do not leave placeholder rows.

| Decision | Why blocked | Recommended option | Required owner |
|---|---|---|---|
| `<actual blocking decision only>` | `<reason>` | `<recommendation>` | `user/operator` |

## Plan validation checklist

- [ ] Parent bead id is present.
- [ ] Goals and non-goals are explicit.
- [ ] Overall completion criteria are explicit.
- [ ] Assumptions are explicit.
- [ ] Scope and out-of-scope areas are explicit.
- [ ] Verification strategy exists.
- [ ] Proposed atomic beads have descriptions.
- [ ] Proposed atomic beads have done criteria.
- [ ] Proposed atomic beads have expected scope.
- [ ] Proposed atomic beads have verification guidance.
- [ ] Dependencies are declared.
- [ ] The plan states that child beads created during decomposition will link back to the parent issue and `PLAN.md` through child bead descriptions, dependency edges when needed, and the parent decomposition comment after `plan_validated`; do not require per-row link fields before child Beads exist, and do not require a non-schema `TICKET.yaml` field.
- [ ] Each proposed atomic bead has suggested mode/risk detail sufficient to author quick, standard, or strict child tickets without re-interpreting risk.
- [ ] No blocking open decisions remain; user/operator-owned blockers route `user_review_needed` instead of `plan_validated`.

`beo-plan` marks checklist items only when the requirement is actually satisfied. Unchecked required checklist items cause `validation_failed` or `user_review_needed`, depending on whether BEO can repair the plan without user/operator authority.

`beo-validate` must validate the actual PLAN content, not trust checklist marks alone. Checklist marks are planning evidence, not validation authority.
