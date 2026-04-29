Non-normative asset.

# readiness-review-prompt

Role: ASSET
Allowed content only: prompt text only; no pass/fail doctrine

## Readiness review prompt

Review the current planning artifacts for execution readiness. This prompt is assistive only: it cannot grant approval, deny approval, choose serial vs swarm, or replace canonical approval, coordination, or routing doctrine. Do not edit artifacts; return observations for `beo-validate` to classify.

Inputs to inspect:
- locked `CONTEXT.md`
- current `PLAN.md`
- bead graph and bead descriptions
- dependency edges
- file scopes and forbidden paths
- verification plan
- approval record when present

Checklist:
1. Confirm `CONTEXT.md` is locked and required sections are present.
2. Confirm `PLAN.md` declares its context binding and planning depth class.
3. Confirm `PLAN.md` contains the sections required for its planning depth: minimal approach or approach, prior learning and discovery facts when required, risk map, current phase contract, current phase story map when required, bead graph, file scopes, verification commands, and execution envelope proposal.
4. Confirm MED/HIGH risks have proof or accepted mitigation.
5. Confirm acceptance-critical decisions map to bead acceptance, verification, review/UAT, or explicit `N/A`.
6. Confirm every bead has Goal, Scope, Acceptance, File scope, Dependencies, and Verification.
7. Check dependency graph for cycles and ambiguous ordering.
8. Check file scopes for missing mutable paths, broad globs, generated outputs, and forbidden paths.
9. Check the execution envelope proposal for candidate mode, approved beads, scope refs, and verification coverage consistent with the bead graph.
10. Check serial/swarm mode evidence is supportable by dependency and file-scope isolation.
11. Identify contract-bearing mutations that would require approval invalidation.
12. Check approval envelope freshness or whether a new grant is needed.
13. If two or more ready beads exist, evaluate swarm eligibility before serial.
14. Count ready beads:
   - exactly one ready bead
   - two or more ready beads with isolation proof
   - two or more ready beads without isolation proof
15. Confirm whether Agent Mail availability supports swarm dispatch.
16. Confirm whether any serial fallback would require a fresh serial approval envelope.

Return shape:

```md
Observations:
- <fact>

Readiness concerns:
- <concern or none>

Mode considerations:
- ready bead count: <number and ids>
- serial eligibility: <evidence or none>
- swarm eligibility: <evidence or none>
- Agent Mail dependency: <available/unavailable/unknown>
- fallback approval note: <fresh serial envelope required? yes/no/N/A>

Approval freshness inputs:
- context_hash source: <path>
- plan_hash source: <path>
- bead_graph_hash source: <source>
```
