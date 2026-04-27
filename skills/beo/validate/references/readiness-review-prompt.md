Non-normative asset.

# readiness-review-prompt

Role: ASSET
Allowed content only: prompt text only; no pass/fail doctrine

## Readiness review prompt

Review the current planning artifacts for execution readiness. Do not grant approval, deny approval, or edit artifacts; return observations for `beo-validate` to classify.

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
2. Confirm `PLAN.md` has current phase, design, bead graph, dependencies, file scopes, and verification plan.
3. Confirm every bead has Goal, Scope, Acceptance, File scope, Dependencies, and Verification.
4. Check dependency graph for cycles and ambiguous ordering.
5. Check file scopes for missing mutable paths, broad globs, generated outputs, and forbidden paths.
6. Check serial/swarm mode evidence is supportable by dependency and file-scope isolation.
7. Identify contract-bearing mutations that would require approval invalidation.

Return shape:

```md
Observations:
- <fact>

Readiness concerns:
- <concern or none>

Mode considerations:
- serial: <evidence>
- swarm: <evidence>

Approval freshness inputs:
- context_hash source: <path>
- plan_hash source: <path>
- bead_graph_hash source: <source>
```
