---
name: beo-compounding
description: >-
  Use after reviewing completes and a feature is effectively finished. Use for
  prompts like "what did we learn?", "capture learnings", "document what we
  found", "compound this work", or whenever a finished feature should improve
  future work instead of ending as isolated effort.
---

<HARD-GATE>
If `.beads/onboarding.json` is missing or stale, stop and load `beo-using-beo` before continuing.
</HARD-GATE>

# Beo Compounding

## Overview

Compounding is the per-feature learnings capture phase after review truly finishes.
Its job is to turn completed feature work into durable, reusable knowledge without inflating weak observations into institutional rules.

**Core principle:** preserve what future work should remember, not just what happened.

## Hard Gates

<HARD-GATE>
Do NOT have subagents write the final learnings file; only the orchestrator writes that.
</HARD-GATE>

<HARD-GATE>
Never auto-append to `critical-patterns.md`; use the canonical approval rule from `../reference/references/approval-gates.md`.
</HARD-GATE>

<HARD-GATE>
One learnings file per feature. Group related findings within that file instead of scattering them across multiple files.
</HARD-GATE>

<HARD-GATE>
The feature status must be `learnings-pending` (set by reviewing). Do not enter compounding if review has not finished.
</HARD-GATE>

---

## Boundary with Reviewing

The reviewing skill's Learnings Synthesis specialist **identifies candidate learnings** — patterns, surprises, and reusable insights — but does not write the final learnings file or promote anything. Compounding is where formal capture, triage, dedup, and promotion happen. If the reviewing specialist produced staging notes, use them as input to Phase 2 below rather than re-analyzing from scratch.

## Default Compounding Loop

Complete these phases in order. The three-agent analysis (Phase 2) runs in parallel.

---

### Phase 1: Gather Context

Load `references/compounding-operations.md` for the exact artifact collection set, git-history fallback rules, and context-gathering procedure.

---

### Phase 2: Three-Category Analysis (3 Parallel Subagents)

Load `references/compounding-operations.md` for the exact three-agent analysis split, staging-file targets, and subagent task summaries.

### Phase 3: Synthesis & Triage

After all three agents complete, load `references/compounding-operations.md` for the exact staging-file read order, dedup procedure, triage tags, slugging rule, learnings-file write flow, and QMD refresh step.

Use the format from `references/learnings-template.md`. Include YAML frontmatter.

#### Learning Triage

See `references/compounding-operations.md` § Triage Tags for the severity scale and triage procedure.

---

### Phase 4: Promote Critical Learnings

For every `severity: critical` learning, load `references/compounding-operations.md` for the exact promotion criteria, approval gate, append format, and post-promotion refresh flow.

### Phase 5: Update STATE.json

Load `references/compounding-operations.md` for the canonical `STATE.json` completion shape, flush step, and checkpoint rules.

---

## Handoff

```
Compounding complete.
- Learnings: .beads/learnings/YYYYMMDD-<slug>.md
- Critical promotions: N findings added to critical-patterns.md
- The ecosystem now has [N total] accumulated learnings.

Next feature starts with this knowledge available.
```

After compounding completes, return control to `beo-router` to pick up the next feature or phase.

---

## Context Budget

If context usage exceeds 65%, load `references/compounding-operations.md` and follow the checkpoint procedure exactly.

## Red Flags & Anti-Patterns

**Do NOT skip compounding because "we're in a hurry."**
The compound loop only works if it runs every cycle. One skip is fine;
a habit of skipping means the ecosystem never gets smarter.

**Do NOT promote everything as critical.**
critical-patterns.md is read at the start of every session. If it grows
past 20-30 entries it becomes noise. Only promote learnings that would
have saved >= 30 minutes if known in advance.

**Do NOT write generic learnings.**
"Test more carefully" is worthless. "When migrating database columns with
a non-null constraint, always provide a default in the migration or it
will fail in production with zero rows affected" is valuable.

**Do NOT fabricate findings.**
If the feature ran smoothly with no surprises, write that. A short learnings
file with 2 genuine entries is better than a long file with invented ones.

- Letting subagents author the final learnings file instead of using them as staging-only analyzers
- Promoting local, feature-specific notes to `critical-patterns.md` without proving broad reuse value
- Splitting one feature's learnings across multiple files instead of keeping one coherent feature record
- Rewriting history to sound more insightful than the actual evidence supports

---

## References

- `references/learnings-template.md`: full template for learnings files with YAML frontmatter
