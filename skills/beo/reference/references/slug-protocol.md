# Slug Protocol

Canonical protocol for creating, reading, preserving, and recovering the immutable `feature_slug` used across the beo pipeline.

## Why This Exists

The `feature_slug` is the stable identifier that ties together:
- the epic bead description
- `.beads/artifacts/<feature-slug>/`
- `STATE.md`
- `HANDOFF.json`
- learnings file naming

Once created, it must not drift.

## Source of Truth

The canonical storage location is the **first line of the epic description**:

```text
slug: <feature_slug>
```

See `pipeline-contracts.md` → **Feature Slug** for derivation rules and invariants.

## When To Create

Only the router creates the slug, at epic creation time.

## Creation Procedure

1. Derive the slug from the epic title using the pipeline-contract rules.
2. Write it as the first line of the epic description.

```bash
br update <EPIC_ID> --description "slug: <feature_slug>"
```

## Read Procedure

Whenever a skill needs artifact paths, read the current epic description first and extract the first line.

Expected first line:

```text
slug: <feature_slug>
```

Use that slug for:
- `.beads/artifacts/<feature_slug>/...`
- `feature_name` in `HANDOFF.json` (historical field name; value is still the slug)
- the `Feature:` field in `STATE.md`
- learnings file slug components where applicable

## Safe Update Procedure

When updating the epic description for summaries or planning content:

1. Read the current description first.
2. Extract and preserve the first line.
3. Replace only the body below the slug line.
4. Rewrite the full description with the slug first.

Canonical shape:

```bash
br update <EPIC_ID> --description "slug: <feature_slug>\n<rest of description>"
```

## Hard Rules

- Never overwrite an epic description without preserving the first-line slug.
- Never derive artifact paths from the mutable epic title after creation.
- Never rename the slug because the feature title changed.
- Never move the slug line below any other content.

## Recovery Procedure

If the slug line is missing:

### Case 1: No tasks yet
- recover the slug from the epic title
- rewrite the epic description with the slug first line

### Case 2: Tasks or artifacts already exist
- STOP
- inspect `.beads/artifacts/` to identify the existing feature directory
- restore that slug to the epic description
- do not guess between multiple plausible directories without user confirmation

## Example Summary Update

```bash
br update <EPIC_ID> --description "slug: <feature_slug>\nFeature: <name>\n\nScope: <summary>\nDecisions: <count> locked\nDomains: <list>"
```
