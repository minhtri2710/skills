---
name: beo-compounding
description: >-
  Use after reviewing completes and a feature is effectively finished. Use for
  prompts like "what did we learn?", "capture learnings", "document what we
  found", "compound this work", or whenever a finished feature should improve
  future work instead of ending as isolated effort. Do not use for cross-feature
  learnings consolidation (use beo-dream instead).
---

<HARD-GATE>
Onboarding — see `../reference/references/shared-hard-gates.md` § Onboarding Check.
</HARD-GATE>

# Beo Compounding

## Overview

Compounding is the per-feature learnings capture phase after review truly finishes.
Its job is to turn completed feature work into durable, reusable knowledge without inflating weak observations into institutional rules.

> See `../reference/references/shared-hard-gates.md` § Shared References Convention.

**Core principle:** preserve what future work should remember, not just what happened.

## Hard Gates

<GUIDELINE>
Do NOT have subagents write the final learnings file; only the orchestrator writes that.
Subagents produce staging files; the orchestrator synthesizes, triages, and writes the final learnings artifact.
</GUIDELINE>

<HARD-GATE>
Never auto-append to `critical-patterns.md`; use the canonical approval rule from `../reference/references/approval-gates.md`.
</HARD-GATE>

<HARD-GATE>
One learnings file per feature. Group related findings within that file instead of scattering them across multiple files.
</HARD-GATE>

<HARD-GATE>
The feature status must be `learnings-pending` (set by reviewing). Do not enter compounding if review has not finished.
</HARD-GATE>

<HARD-GATE>
Before writing any learnings artifact, scan all content for PII (names, emails, credentials, internal URLs, customer data). Redact or generalize any PII found. Learnings must be safe to persist in the knowledge store without access restrictions.
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

See `references/compounding-operations.md` § 3. Synthesis and Triage (subsection Triage Tags) for the severity scale and triage procedure.

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

Follow `../reference/references/shared-hard-gates.md` § Context Budget Protocol. Skill-specific checkpoint: see `references/compounding-operations.md` for the full checkpoint procedure.

## Red Flags & Anti-Patterns

- **Never skip compounding** — the loop only works if it runs every cycle
- **Never promote everything as critical** — `critical-patterns.md` caps at 20-30 entries; only promote learnings that would have saved ≥30 min
- **Never write generic learnings** — "Test more carefully" is worthless; include specific cause-and-effect (e.g., "non-null migration without default fails silently")
- **Never fabricate findings** — 2 genuine entries beats a long file with invented ones
- **Never let subagents author the final learnings file** — they produce staging only; orchestrator synthesizes
- **Never promote local notes without proving broad reuse value**
- **Never split one feature's learnings across multiple files**

---

## References

- `references/learnings-template.md`: full template for learnings files with YAML frontmatter
