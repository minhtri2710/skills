# BEO Learning

## Purpose

BEO learning records observed workflow cases and turns repeated patterns into controlled skill improvements.

## LEARN-01 — Learning is case-based

A learning item must be a concrete observed case, not a vague impression.

## LEARN-02 — Compound records one case

`beo-compound` records exactly one observed learning case or false case.
It does not edit skills, shared doctrine, runtime artifacts, or product files.

## LEARN-03 — Dream consolidates repeated cases

`beo-dream` consolidates at least two finalized cases that support the same recurring pattern, or acts when the user explicitly asks for consolidation.
It does not edit skills, shared doctrine, runtime artifacts, or product files.

## LEARN-04 — Author performs selected skill changes

`beo-author` updates skills or creates new skills only from explicit user request or selected learning evidence.
It does not perform runtime delivery or product implementation.

## LEARN-05 — No automatic self-modification

BEO must not automatically rewrite skills or doctrine during runtime delivery.
Learning owners may recommend changes, but only `beo-author` may perform skill/doctrine edits.

## LEARN-06 — Runtime safety comes before learning

Learning routing is lower priority than runtime safety routing.
If approval, scope, requirements, review, debug, route repair, or user blocking remains active, complete the required runtime handoff first.
Route to `beo-compound` only after the safe runtime decision is complete.

## LEARN-07 — Compound reads source evidence only

`beo-compound` records one learning case from selected source evidence.

`beo-compound` requires `learning_source` provenance before reading any evidence. If `learning_source` is missing:
- If runtime delivery is still active, compound is not yet the correct owner. Return to the active runtime owner.
- If runtime delivery is complete or inactive, ask `user` or return to the calling owner for provenance clarification.
- Do not infer provenance from memory.
- Do not read `REVIEW.md` by default.

`REVIEW.md` is valid source evidence only when:
- `beo-review` produced the learning case; or
- the user explicitly selects `REVIEW.md` as the source evidence.

For non-review learning cases, compound reads the actual source evidence:
- debug output for debug-sourced cases;
- validation output or approval/readiness surface for validate-sourced cases;
- execution safe-stop/evidence output for execute-sourced cases;
- route output for route-sourced cases;
- selected user-provided case text for user-sourced cases.

## LEARN-08 — Tiny provenance canonical surface

For tiny lane:
- `TICKET.md` Review/Closure `learning_source` is canonical.
- `STATE.json.learning_source` may mirror it for handoff/navigation only.
- If `TICKET.md` and `STATE.json` conflict, `TICKET.md` wins for tiny learning provenance.
- Compound should read only the tagged tiny `TICKET.md` section or pointer.

For standard lane:
- `REVIEW.md` or the originating owner output is canonical when it contains the tagged evidence.
- `STATE.json.learning_source` may mirror for handoff/navigation only.
- If a standard artifact and STATE conflict, the artifact/source surface named by the calling owner wins.

## Canonical provenance packet

Minimum packet required before compound reads any evidence:

```yaml
learning_source:
  origin_owner: beo-review | beo-debug | beo-validate | beo-execute | beo-route | user
  source_surface: REVIEW.md | TICKET.md | TRACKER.json | STATE.json | HANDOFF.json | owner_output | user_text
  source_section_or_pointer: "<exact section, field path, or selected text pointer>"
  case_type: wrong-owner-selection | unsafe-mutation-temptation | approval-scope-confusion | review-debug-confusion | human-gate-confusion | tiny-standard-confusion | route-identity-confusion | durable-workflow-learning | unclear-learning
  case_status: candidate
  affected_owner: "<owner most likely affected, or none>"
  target_path: "<skill/reference path likely affected, or none>"
  runtime_status: runtime_complete | runtime_active | user_blocked
```

Every route to compound must provide this provenance. Missing `learning_source` is a hard stop.

## Learning case format

```md
# Learning Case: <case_slug>

## Status
case_status: candidate | finalized | consolidated | closed

## What happened
<One concrete observed false case or learning.>

## What should have happened
<Correct owner, action, hard stop, or rule behavior.>

## Source evidence
source_owner: beo-review | beo-debug | beo-validate | beo-execute | beo-route | user
source_surface: REVIEW.md | TICKET.md | TRACKER.json | STATE.json | HANDOFF.json | owner_output | user_text
source_section_or_pointer: "<exact section, field path, or selected text pointer>"

## Evidence
- Source owner:
- Source surface:
- Source sections read:
- Observed:
- Expected:
- Rule or boundary involved:

## Classification
case_type: wrong-owner-selection | unsafe-mutation-temptation | approval-scope-confusion | review-debug-confusion | human-gate-confusion | tiny-standard-confusion | route-identity-confusion | durable-workflow-learning | unclear-learning
affected_owner: beo-explore | beo-plan | beo-validate | beo-execute | beo-review | beo-debug | beo-route | beo-compound | beo-dream | beo-author | beo-setup | beo-reference | none
target_path: <skill/reference path likely affected, or none>

## Runtime status
runtime_status: runtime_complete | runtime_active | user_blocked

## Suggested target
target_type: owner-skill | canonical-reference | new-skill | none
candidate_action: none | update-existing-skill | create-new-skill | consolidate-later | needs-user-decision

## Why this matters
<workflow risk>

## Recommendation
<non-binding recommendation; no patch text>

## Next
next_owner: done | beo-dream | user
```

When `source_surface: REVIEW.md`, the learning case may cite only the review's learning case fields, findings, next owner, reason, and directly relevant evidence lines. It must not re-run review or change the verdict.

## Consolidated pattern format

```md
# Learning Pattern: <pattern_slug>

## Status
pattern_status: candidate | ready-for-author | closed

## Pattern
<One recurring workflow failure or improvement opportunity.>

## Supporting cases
- `.beads/learnings/<case_1>.md`
- `.beads/learnings/<case_2>.md`

## Affected surface
affected_owner: <owner or none>
target_type: owner-skill | canonical-reference | new-skill | none
target_path: <path or none>

## Recommendation
recommended_action: none | update-existing-skill | create-new-skill | user-decision

## Why not direct edit
Dream consolidates learning only. Skill or doctrine edits belong to `beo-author`.
```

## Learning is exceptional

Learning is not part of the default delivery path.

Use `beo-compound` only when all are true:

- runtime safety decision is already complete
- evidence shows one concrete workflow-learning case
- canonical `learning_source` exists
- learning is not being used to bypass repair, diagnosis, approval, or review

If any condition is missing, close normally or return to the required runtime owner.

Default closure after accept is `done`. Route to `beo-compound` only when:
- concrete workflow-learning case exists
- runtime decision is complete
- canonical `learning_source` exists
- no runtime owner still needs repair, diagnosis, approval, or verdict

## Routing

- no learning case -> done
- one concrete case -> beo-compound -> done
- repeated finalized cases -> beo-dream -> done
- explicit skill update request -> beo-author -> done

## Learning artifacts are never runtime authority

Learning artifacts and learning-owner outputs are never runtime authority. They do not grant approval, refresh integrity, select execution sets, authorize mutation, emit verdicts, repair owner identity, or bypass Human Gates.
