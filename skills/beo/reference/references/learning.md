# Learning

Authority: canonical for post-runtime learning capture.

## LEARN-01 Concrete Case Only

A learning item must describe one concrete observed workflow case with provenance. Vague impressions are invalid.

Learning records use `beo.learning_case.v1` or `beo.learning_pattern.v1` from `registry/artifact-schemas.json`. Learning enum values come from `registry/learning-vocabulary.json`.

## LEARN-02 No Runtime Authority

`beo-learn` cannot approve, unlock execution, mutate product files, emit verdict, route runtime delivery, or edit doctrine.

## LEARN-03 Record Home and Naming

Learning records live under `.beads/artifacts/<feature_slug>/learning/` unless an explicit corpus request names another destination.

Case filenames and IDs use `case-<feature_slug>-<short-topic>.yaml`. Pattern filenames and IDs use `pattern-<short-topic>.yaml`. Keep IDs stable once referenced.

Minimal case record:

```yaml
schema_version: beo.learning_case.v1
id: case-demo-owner-boundary
case_status: finalized
case_type: wrong-owner-selection
feature_slug: demo
source:
  source_surface: REVIEW.md
  source_pointer: "## Learning"
observed_case: "Accepted review identified an owner-boundary confusion in one concrete demo workflow."
affected_owner: beo-author
runtime_status: runtime_complete
created_at: "2026-05-14T00:00:00Z"
```

## LEARN-04 Consolidate Only Repeated Patterns

A repeated-pattern consolidation requires at least two finalized learning cases that independently support the same recurring workflow issue.

Authoring from one selected case is not pattern consolidation. It may only recommend a focused doctrine change for `beo-author` when the user explicitly selects that case or the accepted review section requests authoring.

## LEARN-05 Consolidation Source Boundaries

Explicit consolidation may use finalized learning cases and accepted review learning sections. Exclude runtime-active, advisory, generated, or non-authoritative artifacts unless the user explicitly selects them as evidence.

## LEARN-06 Authoring Requires `beo-author`

Learning may recommend a doctrine change. Only `beo-author` may edit skills or reference doctrine, and only from explicit user request or selected evidence.

## Minimal Learning Source

```yaml
learning_source:
  source_surface: <REVIEW.md | TICKET.md | learning/case-*.yaml | user_text>
  source_pointer: <exact section/field/path>
  observed_case: <one concrete observed case>
  affected_owner: <owner | none>
```
