Non-normative asset.

# bead-readiness-prompt

Role: ASSET
Allowed content only: prompt text only; no pass/fail doctrine

## Bead readiness prompt

Review bead descriptions and graph evidence for operational clarity. This prompt is assistive only: it cannot approve execution, choose execution-set mode, or replace canonical validate, approval, or routing doctrine. Return observations for `beo-validate`.

Inputs to inspect:
- bead ids and descriptions
- dependency graph
- file scopes and forbidden paths
- generated outputs
- verification commands

Checklist:
1. Confirm each bead states Goal, Scope, Acceptance, File scope, Forbidden paths, Dependencies, Verification, and generated outputs.
2. Confirm acceptance is observable and testable.
3. Confirm file scope is narrow enough for safe execution.
4. Confirm forbidden paths cover adjacent high-risk surfaces.
5. Confirm verification commands are concrete and runnable.
6. Confirm dependency edges prevent unsafe ordering.
7. Confirm scope isolation when two or more independently ready beads are present (no overlapping file scope or unresolved dependency edges).
8. Count ready beads and list ids that are operationally ready; separately list approved dependency-chain children that are blocked only by an earlier selected parent bead.
9. Record facts relevant to later execution-set mode classification without choosing the mode.
10. Flag missing or overly broad file scope.
11. Flag acceptance-critical decisions that are unmapped.
12. Flag scope overlap that would block local_parallel classification.

Return shape:

```md
Bead observations:
- <bead-id>: <fact>

Scope concerns:
- <concern or none>

Dependency concerns:
- <concern or none>

Verification concerns:
- <concern or none>

Mode readiness notes:
- ready bead count: <number and ids>
- mode-relevant facts: <single bead / ordered chain / isolated independent beads / conflicts>
- isolation evidence: <evidence or none>
- ordering constraints: <constraints or none>
```
