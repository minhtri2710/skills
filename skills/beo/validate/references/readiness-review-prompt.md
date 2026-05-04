Non-normative asset.

# readiness-review-prompt

Role: ASSET
Allowed content only: prompt text only; no pass/fail doctrine

## Readiness review prompt

Review the current planning artifacts for execution readiness. This prompt is assistive only: it cannot grant approval, deny approval, select execution-set mode, or replace canonical approval or routing doctrine. Do not edit artifacts; return observations for `beo-validate` to classify.

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
10. Check execution-set mode evidence is supportable by dependency and file-scope isolation.
11. Identify contract-bearing mutations that would require approval invalidation.
12. Check approval envelope freshness or whether a new grant is needed.
13. If two or more independently ready beads exist, evaluate scope isolation for local_parallel classification.
14. Count execution-set candidates:
   - exactly one ready bead
   - one ready root bead plus approved child beads blocked only by earlier beads in the same explicit dependency chain
   - two or more ready beads with isolation proof
   - two or more ready beads without isolation proof
15. Confirm execution-set mode is consistent with scope isolation and dependency ordering; ordered_batch may include dependency-chain children that are not independently ready yet when the selected parent bead is their only blocker.
16. Confirm whether any mode change would require a fresh PASS_EXECUTE approval envelope.

Return shape:

```md
Observations:
- <fact>

Readiness concerns:
- <concern or none>

Mode considerations:
- ready bead count: <number and ids>
- proposed mode: single | ordered_batch | local_parallel
- isolation evidence: <evidence or none>
- ordering constraints: <constraints or none>
- mode-change approval note: <fresh PASS_EXECUTE required? yes/no/N/A>

Approval freshness inputs:
- context_hash source: <path>
- plan_hash source: <path>
- bead_graph_hash source: <source>
```
