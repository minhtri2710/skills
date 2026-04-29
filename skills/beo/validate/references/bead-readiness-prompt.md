Non-normative asset.

# bead-readiness-prompt

Role: ASSET
Allowed content only: prompt text only; no pass/fail doctrine

## Bead readiness prompt

Review bead descriptions and graph evidence for operational clarity. Do not approve execution; return observations for `beo-validate`.

Inputs to inspect:
- bead ids and descriptions
- dependency graph
- file scopes and forbidden paths
- verification commands
- swarm eligibility notes

Checklist:
1. Confirm each bead states Goal, Scope, Acceptance, File scope, Forbidden paths, Dependencies, Verification, and Swarm eligibility.
2. Confirm acceptance is observable and testable.
3. Confirm file scope is narrow enough for safe execution.
4. Confirm forbidden paths cover adjacent high-risk surfaces.
5. Confirm verification commands are concrete and runnable.
6. Confirm dependency edges prevent unsafe ordering.
7. Confirm swarm eligibility is denied when scopes overlap or dependency edges exist.
8. Count ready beads and list ids that are operationally ready.
9. Distinguish serial eligibility from merely having at least one ready bead.
10. Record whether Agent Mail availability is known for swarm dispatch.

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

Swarm isolation notes:
- <note or none>

Mode readiness notes:
- ready bead count: <number and ids>
- serial eligibility: <evidence or none>
- swarm eligibility: <evidence or none>
- Agent Mail dependency: <available/unavailable/unknown>
```
