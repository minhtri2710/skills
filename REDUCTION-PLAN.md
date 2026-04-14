# Beo Skills Conciseness Plan

Keep all 13 skills. Cut context footprint aggressively. No merges, no architecture changes.

**Current beo skill tree**: 10,217 lines of active skill payload (1,776 `SKILL.md` + 8,328 references + 113 assets)
**Target**: ~8,400 lines of active skill payload (~18% reduction)

Count notes:
- "active skill payload" means the 13 `SKILL.md` files, all `references/*.md`, and assets under `skills/beo/**/assets/`
- workspace/eval artifacts are intentionally excluded from the reduction target
- the prior `1,915 SKILL.md` figure was stale; live count is `1,776`

---

## Deep Review Update

Deep review across the current skill set changes the plan in four ways:

- several Track A items are already partially done (`bead-ops.md` rename, `shared-hard-gates.md`, some reviewing/debugging cleanup)
- the biggest remaining wins are still the same, but the top line estimates should be recalibrated to current file sizes
- template consolidation is now a higher-risk/lower-value move than reference compression and should be deferred
- the current repo state already contains some renamed files from this plan, so execution should treat the plan as a rolling reduction pass, not a greenfield checklist

### Current Verified Hotspots

Largest remaining docs from the live tree:

| File | Current Lines | Notes |
|------|--------------:|------|
| `reference/references/state-and-handoff-protocol.md` | 451 | still carries TOC, duplicate schema examples, and repeated planning-aware semantics |
| `reference/references/artifact-conventions.md` | 432 | still contains TOC, verbose examples, duplicated planning interpretation, and knowledge-store overlap |
| `swarming/references/message-templates.md` | 390 | still the highest bloat ratio among operational refs |
| `executing/references/execution-operations.md` | 376 | still repeats reservation API shapes and long artifact examples |
| `router/references/router-operations.md` | 366 | still contains the giant quick-path artifact stub block |
| `validating/references/validation-operations.md` | 354 | still has long examples and repeated validator prose |
| `validating/references/plan-checker-prompt.md` | 303 | still heavily compressible |
| `planning/references/artifact-writing-guide.md` | 262 | still repeats approval/current-phase guidance |
| `planning/references/bead-ops.md` | 259 | renamed already, but still has overlapping checklist prose |
| `writing-skills/references/pressure-test-template.md` | 259 | still over-explained for a template file |

### Already Landed Since This Plan Was Written

- `planning/references/bead-creation-guide.md` → `planning/references/bead-ops.md`
- `planning/references/discovery-guide.md` → `planning/references/discovery-reference.md`
- `reference/references/shared-hard-gates.md` was added and is already absorbing some repeated gate text
- `planning/SKILL.md` and `reference/SKILL.md` are already somewhat slimmer than the older baseline this plan assumed
- `debugging/SKILL.md` appears clean on reactive-fix duplication; Track A3 should focus on `reviewing` only

### Revised Priorities

1. Finish protocol dedup that now has clear canonical homes.
2. Compress the top 10 reference docs using current line counts, not historical estimates.
3. Trim SKILL bodies only after the shared refs are tighter.
4. Defer file-merging/consolidation unless a later pass still needs more reduction.

## Strategy

Three parallel tracks plus one deferred ergonomic track:

| Track | Lines Saved | Risk |
|-------|------------|------|
| A. Protocol deduplication (single canonical owners) | ~120-160 | Low |
| B. Reference doc compression (top 10 files) | ~1,300-1,500 | Low-Medium |
| C. SKILL.md + remaining refs trimming | ~200-350 | Low |
| D. Optional file consolidation | situational | Medium |
| **Total** | **~1,600-2,000** | |

The reduction target is now expressed against active skill payload only. Most remaining savings are in reference compression, not structural consolidation.

---

## Track A: Protocol Deduplication

Replace duplicated protocol blocks with pointers to canonical owners. Prevents drift.

### A1. Approval Prompt — Single Owner
- **Canonical**: `reference/references/approval-gates.md` (lines 37-44)
- **Remove inline copy from**: `planning/references/artifact-writing-guide.md` (section 8) — replace with pointer
- **Remove inline copy from**: `planning/references/planning-state-and-cleanup.md` (section 13) — pointer + local extension (Mode/Stories/Tasks)
- **Saves**: ~30 lines | Risk: Low
- **Deep review status**: still valid; approval text is still duplicated in planning refs even though the canonical home is now stronger

### A2. Bead Template — Remove Inline Reproduction
- **Canonical**: `reference/references/bead-description-templates.md` (lines 43-81)
- **Strip from**: `planning/references/bead-ops.md` (lines 16-57) — keep CLI ops only, pointer to template
- **Saves**: ~35 lines | Risk: Low
- **Deep review status**: partially landed by rename only; content reduction still remains

### A3. Reactive Fix Bead Protocol — Single Source
- **Canonical**: `reference/references/pipeline-contracts.md` § Fix Beads
- **Strip from**: `reviewing/references/reviewing-operations.md` (section 3b) — pointer + routing note
- `debugging/SKILL.md` already clean (pointer-only)
- **Saves**: ~10 lines | Risk: Low
- **Deep review status**: keep, but scope only `reviewing`; `debugging` no longer needs work here

### A4. Agent Mail API Signatures — Remove Local Reproductions
- **Canonical**: `reference/references/agent-mail-coordination.md` (lines 68-91)
- **Strip from**: `executing/references/execution-operations.md` (section 5) — keep pointer + conflict handling
- **Strip from**: `swarming/references/swarming-operations.md` (section 2) — keep pointer + swarm-specific params
- **Saves**: ~25 lines | Risk: Medium (workers may benefit from inline signatures)
- **Deep review status**: still a good cut; both files still inline reservation/setup shapes

### A5. Shared Learnings Governance — Centralize
- **Add to**: `reference/references/knowledge-store.md` § Learnings Write Governance (PII redaction, approval pointer, QMD refresh)
- **Trim**: `compounding/SKILL.md` hard gate — one-line + pointer
- **Trim**: `dream/SKILL.md` hard gate — one-line + pointer
- **Trim**: `compounding/references/compounding-operations.md` — remove inline QMD + approval rules
- **Trim**: `dream/references/dream-operations.md` — remove inline QMD + approval rules
- **Saves**: ~15 net lines | Risk: Low
- **Deep review status**: still worth doing; write-side governance is still split across 4 files and `knowledge-store.md`

### A6. Artifact Roles Overlap in Hub
- **Remove**: "Planning Mode Interpretation" summary from `reference/references/artifact-conventions.md` (self-described as "summarized for convenience")
- **Keep**: artifact table in `pipeline-contracts.md` + semantics in `artifact-conventions.md`
- **Saves**: ~15 lines | Risk: Low
- **Deep review status**: still a direct win; the overlap is unchanged

### A7. Fix 4 Broken Cross-Doc Paths
- `reference/references/approval-gates.md:64` — wrong relative path to go-mode.md
- `executing/references/worker-prompt-guide.md:5` — wrong path to worker-template.md
- `executing/references/execution-operations.md:143` — wrong path to swarming message-templates.md
- `planning/references/bead-ops.md:47` — wrong path to execution-operations.md
- **Saves**: 0 lines (correctness fix) | Risk: Low
- **Deep review status**: likely still pending; verify during implementation because the rename churn makes these especially fragile

---

## Track B: Reference Doc Compression

The top 10 reference docs are 3,462 lines and contain ~40% compressible content. Apply these patterns everywhere:

### Universal Compression Rules
1. **Delete all Tables of Contents** — agents don't browse, headings suffice
2. **Replace "Why This Exists" sections with 1-line intros**
3. **Keep one example per concept**, not every permutation
4. **Convert verbose prose to tables/checklists**
5. **Externalize inline template bodies** — point to template files
6. **Stop re-explaining "current-phase only"** in every doc — it's a shared rule

### B1. `state-and-handoff-protocol.md` — 451 → ~260 lines (-40% to -43%)
| Section | Action |
|---------|--------|
| TOC (lines 3-20) | Delete |
| "Why This Exists" + "Core Rule" (24-38) | Compress to 3 bullets |
| Base fields → planning fields → full schema (44-87) | Collapse into ONE canonical schema |
| Field semantics (89-127) | Convert to compact table |
| HANDOFF planning extension + meanings (149-200) | Compress: "same semantics as STATE" |
| Optional artifact map (202-225) | 5-line note + tiny example |
| When to write / checkpoint / resume / cleanup (227-278) | Merge into one "Checkpoint Protocol" section |
| Examples A-F (280-415) | Reduce 6 examples to 2 (one STATE, one HANDOFF) |
| Planning-aware transitions (418-449) | Short mutation table |
| Hard rules (451-460) | Deduplicate vs earlier sections |

### B2. `artifact-conventions.md` — 432 → ~250 lines (-42%)
| Section | Action |
|---------|--------|
| TOC (5-30) | Delete |
| Spec section (46-67) | Compress to ~8 lines (just point to templates) |
| Report format + examples (69-110) | Keep header format + "latest wins" + 1 short example |
| Task_state write example (120-154) | Keep format + 2 hard notes only |
| Slug lifecycle "Why This Exists" (177-186) | 1 sentence |
| Create/read/update procedures (198-240) | Merge into one concise protocol block |
| Artifact semantics (315-393) | Replace each artifact with 1-2 line purpose. Detail lives in artifact-writing-guide |
| Planning mode interpretation (394-408) | Delete (Track A6) |
| Knowledge store section (419-432) | Move to knowledge-store.md |

### B3. `message-templates.md` (swarming) — 390 → ~185 lines (-52% to -53%)
| Section | Action |
|---------|--------|
| Banner + TOC (3-21) | Delete |
| Per-template "Posted by / When / Purpose / Runtime call" | Replace with one global note at top |
| Spawn Notification (25-52) | Compress to ~10 lines |
| Worker Spawn Ack (56-74) | Compress to ~8 lines |
| File Conflict Resolution (173-201) | 3-option compact format |
| Overseer Broadcast (205-226) | Shorten drastically |
| Context Warning (230-257) | 1 compact template |
| Startup + Silent Worker Reminders (291-326) | Merge into one parameterized "Reminder" template |
| Handoff JSON Template (330-391) | Minimal skeleton + pointers to canonical schema |

### B4. `execution-operations.md` — 376 → ~245 lines (-35%)
| Section | Action |
|---------|--------|
| Intro + TOC (3-15) | Delete |
| Stale label cleanup (73-84) | 1 rule + pointer to label list in pipeline-contracts |
| Reservation flow (126-156) | 1 signature + 1 conflict rule + 1 release rule (Track A4) |
| Git commit format (232-256) | Cut to 2-line recommendation |
| Full report artifact example (258-279) | Reference artifact-conventions.md |
| Bead completion validation (288-301) | 4 bullets |
| STATE update schema (319-358) | By reference, not restated |

### B5. `router-operations.md` — 366 → ~230 lines (-37%)
| Section | Action |
|---------|--------|
| TOC (19-28) | Delete |
| Quick-path inline artifact stubs (91-211) | **Biggest cut**: externalize to template asset or reduce to 5 stub requirements. ~120 lines saved |
| Planning-aware routing rules A-E (240-279) | Convert to routing table |
| Resume from handoff (282-321) | Compress — reference state-and-handoff-protocol.md |
| STATE.json on handoff (360-366) | 1 sentence + canonical reference |

### B6. `validation-operations.md` — 354 → ~235 lines (-34%)
| Section | Action |
|---------|--------|
| Intro + TOC (3-14) | Delete |
| Learnings + orientation (44-81) | Compress sample orientation block |
| Dedup/coherence/semantic checks (153-191) | Keep validator-only checks, pointer to bead-ops for rest |
| Validation summary template (229-267) | Required fields only, not verbose sample |
| Checkpoint + handoff examples (304-354) | Keep decision rule, cut example wording |

### B7. `plan-checker-prompt.md` — 303 → ~195 lines (-36%)
| Section | Action |
|---------|--------|
| TOC (9-22) | Delete |
| Verification goal (44-62) | Halve the prose |
| 8 dimensions (119-287) | Each dimension: 1 check line + 1-3 fail conditions. Cut verbose PASS/FAIL blocks |
| Behaviors to avoid (290-303) | 5 bullets total |

### B8. `artifact-writing-guide.md` — 262 → ~165 lines (-37%)
| Section | Action |
|---------|--------|
| Write order + roles (5-38) | Single table |
| `approach.md` section (40-78) | Remove repeated "approach = strategy" restatements |
| Multi-phase approval (142-177) | Pointer to approval-gates.md (Track A1) |
| Current-phase artifacts (179-230) | Remove repeated "current phase only" |
| High-stakes review (232-262) | Move 7-question prompt to inline checklist |

### B9. `pressure-test-template.md` — 259 → 145 lines (-44%)
| Section | Action |
|---------|--------|
| HTML comments + TOC (3-13) | Delete |
| Template scenarios B/C (of A-E) | Replace with scenario generator formula. Keep A + D/E only |
| Anatomy bad/good/great (180-217) | Short "good scenario checklist" |

### B10. `bead-ops.md` — 259 → ~165 lines (-36%)
| Section | Action |
|---------|--------|
| TOC (5-13) | Delete |
| Story Context Block (16-50) | Remove inline template (Track A2) |
| Plan review checklists (93-117) | Compress — overlaps validation |
| Quick mode (120-130) | 3 bullets or move to pipeline docs |
| Graph validation prose (159-240) | Keep commands, shorten interpretive prose |

---

## Track C: SKILL.md + Remaining Refs

### C1. `planning/SKILL.md` — 209 → ~180 lines (-30)
- Trim "Bead Creation Rules" (lines 144-171): 27 lines → ~10 with pointer to bead-ops.md
- Remove verbatim "If approach.md is weak..." restatement (lines 117-123): ~3 lines
- Remove inline current-phase restatement (lines 135-142): ~5 lines

### C2. `reference/SKILL.md` — 139 → ~115 lines (-25)
- Move "Pause and Resume" (lines 109-122) to state-and-handoff-protocol.md
- Move "Skip-Stage Policy" (lines 124-135) to pipeline-contracts.md or shared-hard-gates.md
- Tighten "Canonical Ownership" section
- **Deep review note**: `shared-hard-gates.md` is now the better home for skip-stage policy than `pipeline-contracts.md`

### C3. All Other SKILL.md Files — ~100 lines total across 11 files
Apply universal patterns:
- Remove explanatory prose that restates reference doc content
- Tighten Red Flags sections
- Compress verbose "When NOT to Use" lists where obvious

### C4. Remaining Reference Docs
Apply universal compression rules to all remaining reference docs:
- Delete any TOCs
- Replace "Why This Exists" sections with 1-line intros
- Compress verbose examples
- Prioritize files still over ~150 lines after the top-10 pass
- **Target**: ~10-15% reduction → ~500-700 additional lines saved

---

## Track D: File Consolidation (Deferred / Optional)

Deep review suggests this should move behind all content-reduction work. It saves file count, but not much context unless the merged file is also rewritten aggressively. It also raises navigation risk and increases diff blast radius.

### D1. Merge 5 Planning Templates → 1
- `approach-template.md` (126) + `phase-contract-template.md` (136) + `phase-plan-template.md` (88) + `plan-template.md` (33) + `story-map-template.md` (115) → `artifact-templates.md` with TOC
- **-4 files**, same content
- **Deep review recommendation**: defer; merge only if a later pass also removes duplicate scaffold prose inside the combined file

### D2. Absorb `planning-prerequisites.md` → `artifact-writing-guide.md`
- 73 lines absorbed into § Prerequisites
- **-1 file**
- **Deep review recommendation**: defer; current split keeps prerequisite checks distinct from artifact-writing mechanics

---

## Implementation Order

Execute in this order to minimize risk:

| Phase | Track | Actions | Estimated Lines Saved |
|-------|-------|---------|----------------------|
| 1 | A7 | Fix broken cross-doc paths and verify renamed-file references | 0 (correctness) |
| 2 | A1-A6 | Finish protocol dedup against the new canonical owners | ~120-160 |
| 3 | B5 | `router-operations.md` quick-path stub compression | ~130+ |
| 4 | B3 | `swarming/references/message-templates.md` | ~200+ |
| 5 | B1 | `state-and-handoff-protocol.md` | ~180-200 |
| 6 | B2 | `artifact-conventions.md` | ~180 |
| 7 | B4-B10 | Remaining top-10 reference docs | ~650+ |
| 8 | C1-C4 | SKILL.md files + medium-size refs | ~200-350 |
| 9 | D1-D2 | Optional consolidation only if still needed | file-count reduction only |

### Verification After Each Phase
- Spot-check that all cross-doc pointers resolve
- Verify no operational content was lost (canonical owners still contain full rules)
- Run repo validators and any skill evals that are cheap enough to justify the pass

---

## What NOT to Change

| Item | Why |
|------|-----|
| 13-skill architecture | Each skill has distinct triggers, failure modes, state transitions |
| `message-templates.md` (swarming) vs `message-templates.md` (debugging) | Different content verified |
| `pressure-scenarios.md` (swarming) vs `pressure-scenarios.md` (dream) | Different domains verified |
| All `openai.yaml` files | Each has unique display_name, short_description, default_prompt |
| Onboarding hard gate in every SKILL.md | Intentional per-skill guardrail |
| Compounding + dream as separate skills | Different triggers, different write behavior |
| Template fill-in content | Templates need their fields — do not shrink by removing required placeholders |
| Current canonical owner docs | Reduce duplication around them; do not hollow them out so far that downstream skills lose the source of truth |

---

## Risk Notes

- **Low behavior risk, not zero**: Consolidating prompts and reference ownership can change prompt salience
- **Track A4 medium risk**: executing/swarming workers may benefit from inline API signatures — monitor after change
- **Track B biggest risk**: over-compressing reference docs may lose edge-case guidance. When in doubt, keep the rule, cut the explanation
- **Track D risk is now higher than initially estimated**: merging files may reduce navigability while saving little context unless the merged result is rewritten aggressively
- **Principle**: Keep rules and constraints. Cut explanations, examples, and re-statements.
