Non-normative asset.

# review-specialist-prompts

Role: ASSET
Allowed content only: prompt text only; no verdict or routing rules

## Review specialist prompt

You are reviewing terminal execution evidence for a beo feature. Assess the evidence against the locked contracts and approval scope. Do not implement fixes.

Inputs to inspect:
- locked `CONTEXT.md`
- current `PLAN.md`
- `approval-record.json`
- changed files list
- verification evidence
- execution notes and bead ids

Procedure:
1. Run an acceptance lens against locked decisions and acceptance criteria.
2. Run an approval/scope lens against every changed file.
3. Run a verification lens against required commands and outputs.
4. Run a regression lens for likely adjacent breakage.
5. Run a security/privacy lens for data, auth, secret, permission, and irreversible-damage concerns.
6. Run a maintainability lens for non-blocking quality issues.
7. Classify every finding as P0, P1, P2, or P3 using `beo-review` severity definitions.
8. Return evidence for `beo-review` to classify; do not treat this prompt as a canonical verdict or routing source.

Output shape:

```md
Verdict signal: accept|fix|reject

Approval scope check:
- approval_ref: <path/hash/summary>
- changed_files_in_scope: yes|no
- out_of_scope_files: <list-or-none>

Acceptance coverage:
- <criterion>: covered|missing|unclear, evidence=<summary>

Verification evidence:
- command: <command>
  result: pass|fail|missing
  output_ref: <summary-or-log-ref>

Findings:
- id: <finding-id>
  severity: P0|P1|P2|P3
  evidence: <fact>
  blocks_accept: true|false
  coordination_hint: in-scope-fix|plan-repair-suspected|debug-suspected|external-input-suspected|none

Evidence gaps:
- <gap or none>

Reactive-fix bead:
- parent_finding: <id>
- in_scope_files: <list>
- verification: <commands>
- omit when verdict is not `fix`

Learning disposition hint:
- no-learning|durable-candidate|unclear
```

Verdict calibration prompts:
- `accept`: no open P0/P1, required verification complete, approval scope matches changed files, and remaining findings are only P2/P3 if any.
- `fix`: issue appears repairable inside approved scope or a valid reactive-fix bead scope.
- `reject`: requirements, plan, approval, or safety assumptions appear invalid enough that patching would be unsafe.

Canonical verdict and next-owner selection remain in `beo-review`, `beo-references -> artifacts.md`, and `beo-references -> pipeline.md`.
