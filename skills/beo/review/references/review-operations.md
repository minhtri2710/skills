# Review Operations

Role: APPENDIX
Allowed content only: verdict routing procedure, bounded repair packet, accept hard stops
Forbidden content: owner selection beyond verdict routing, approval authority, writable-surface expansion

## REV-01 — Cold evidence required

Review reads cold evidence from current required surfaces and live declared files. Memory and chat summaries are never review evidence.

Review packet is a navigation aid only. Review must still reread current required surfaces and live declared files. If the packet conflicts with canonical artifacts or live evidence, the packet loses.

Helper checks can block accept, but helper output cannot by itself prove acceptance. Acceptance still requires cold requirement trace, verification evidence, declared-output discipline, and live declared file/evidence comparison.

If current execution evidence does not exist, review blocks.

## REV-02 — Verdict routing

```text
accept + no learning case -> done
accept + concrete learning/false-case -> beo-compound
fix with known bounded repair -> beo-plan
fix/reject with unproven root cause -> beo-debug
requirements contradiction -> beo-explore
needs approval/integrity refresh, no mutation-caused contradiction -> beo-validate
integrity contradiction after mutation, root cause unproven -> beo-debug
```

Do not route to `beo-author` automatically from review.
Do not route to `beo-compound` for vague or speculative learning.
Learning case routing is secondary. If a finding requires plan/debug/explore first, route there before compound. Compound records the learning case only after the runtime-safe route is complete.

## REV-03 — Review hard stops

Review never routes directly to execute. Review never creates fix beads. Review records findings only.

## Learning case handoff to compound

When review routes to `beo-compound`, review must record the canonical `learning_source` packet defined in `beo-reference -> references/learning.md`. Compound records the case from that provenance and must not reopen or reinterpret the verdict.

Standard lane: record the packet in `REVIEW.md`.

Tiny lane: record the packet in `TICKET.md` Review/Closure.

Compound may read only those source sections needed to record the selected learning case. Compound must not re-run review or change the verdict.

## Cold review evidence

Review rereads current evidence before verdict:

- tiny: `TICKET.md`, live changed files, verification evidence
- standard: `CONTEXT.md`, `PLAN.md`, `TRACKER.json`, live changed files, verification evidence, and selected BR task descriptions only when canonical `PLAN.md` uses selected BR tasks for the selected execution set

## Accept hard stop checklist

Do not accept when any is true:

- integrity is stale, invalid, or unavailable when required (INT-04)
- execution evidence is missing
- selected BR task descriptions contradict `PLAN.md` (ART-05)
- tracker/ticket execution evidence and live file evidence disagree
- generated outputs are undeclared or unapproved (ART-06)
- verification evidence is missing or vague
- trace coverage is incomplete
- P0/P1 findings exist
- review relies on memory instead of artifacts

## Partial execution and rollback

Review must classify partial execution as accept/fix/reject only from evidence. It may not authorize rollback unless rollback was declared and evidence supports it. Undeclared rollback routes to `beo-plan` or `user` by risk.

## Bounded repair packet

When routing to `beo-plan` with a fix finding, include a structured repair packet:

```yaml
bounded_repair_packet:
  verdict: fix
  finding_id: F-01
  acceptance_requirement_affected: "<requirement id/text>"
  evidence: "<file/line/test/live observation>"
  known_root_cause: true | false
  root_cause_proof_reference: "<review evidence or debug return>"
  repair_boundary: "<allowed scope>"
  why_plan_owns_the_repair: "<why revised executable scope is needed>"
  forbidden_shortcut: "review must not route directly to execute or create fix beads"
  must_not_change: ["<protected behavior/path>"]
  required_verification: ["<test/check>"]
  approval_impact: "refresh_required"
  return_owner_after_plan_repair: "beo-validate"
```

Rules:

- If `known_root_cause: false`, route to `beo-debug`, not plan (REV-02).
- If `repair_boundary` is broader than the selected feature scope, route to `beo-explore`.
- The packet is not executable approval and does not select an execution set.
- The packet does not authorize mutation.
- `beo-plan` turns the packet into revised plan scope; `beo-validate` must approve again (APP-02).

## Verdict output

Record verdict, evidence reviewed, trace coverage, findings, integrity status, generated output status, learning case (none or present with type), next owner, and reason.
