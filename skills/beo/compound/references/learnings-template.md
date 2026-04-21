# Learnings File Template

Use for `.beads/learnings/YYYYMMDD-<feature_slug>.md`.

Write one file per feature. A file may contain multiple learning entries separated by `---`.

## Frontmatter

Required first block:

```yaml
---
date: YYYY-MM-DD
feature: <feature-name>
categories: [pattern, decision, failure, anti-pattern]
severity: routine | useful | critical
tags: [tag1, tag2, tag3]
---
```

Rules:
- include only categories that appear in the file
- set `severity` to the highest severity used by any entry
- use domain tags, not prose

## Entry Format

Repeat for each learning:

```markdown
# Learning: <concise title>

**Category:** pattern | decision | failure | anti-pattern
**Severity:** routine | useful | critical
**Tags:** [tag1, tag2]
**Applicable-when:** <one sentence>

## What Happened
<2-4 concrete sentences; name files, tools, commands, or surfaces when useful>

## Root Cause / Key Insight
<why this happened or why this approach worked>

## Recommendation for Future Work
<imperative advice a later agent can follow directly>
```

## Filename Rules

- format: `YYYYMMDD-<feature_slug>.md`
- use the immutable feature slug, not a topic nickname
- lowercase, hyphens only

Examples:
- `20260315-auth-token-refresh.md`
- `20260320-bead-scope-isolation.md`
- `20260318-db-migration-ordering.md`

## `critical-patterns.md` Promotion Format

When promoting a critical learning, use:

```markdown
## [YYYYMMDD] <Learning Title>
**Category:** pattern | decision | failure
**Feature:** <feature-name>
**Tags:** [tag1, tag2]

<2-4 sentence summary: what happened, why it mattered, what to do next time>

**Full entry:** .beads/learnings/YYYYMMDD-<feature_slug>.md
```
