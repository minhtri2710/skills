# Diagnostic Checklist

Role: APPENDIX
Allowed content only: diagnostic checklist and output message shapes
Forbidden content: owner selection, approval authority, review verdict authority, routing topology, writable-surface expansion

## Checklist prompts

- Confirm sender recorded `return_to`, `source_owner`, `blocked_invariant`, `evidence_ref`, and allowed unblock classes.
- Reproduce the observed failure or blocker.
- Record the smallest failing command, input, or artifact.
- Identify the first contradicted expectation.
- Separate proven evidence from hypotheses.
- Stop after one inconclusive diagnostic cycle and return evidence.

## Allowed diagnostic content

- affected owner condition
- affected file/surface category
- invariant that failed
- command/output evidence
- smallest legal unblock class
- return owner still legal

## Forbidden diagnostic content

- exact diff
- patch text
- mutation command
- approval/readiness/verdict
- rollback authorization

If a debug output contains patch text, approximate implementation, or file diffs, it is invalid and must be rerun.

## Output shape

```md
Finding: <proven cause | inconclusive>
Proof status: proven | inconclusive
Affected invariant: <approval | scope | verification | state | requirement | environment | dependency | unknown>
Affected surface: <file/surface category or N/A>
Observed evidence: <commands/artifacts observed>
First contradicted expectation: <expected vs observed>
Safe unblock class: plan repair | execute retry inside approved scope | validate refresh | explore clarification | user blocker | no safe unblock
Return owner: <beo-execute | beo-review | beo-plan | beo-validate | beo-explore | user>
Learning case: none | candidate
Debug return consumed by receiver: pending
Patch text: none
Mutation command: none
```

`Patch text: none` and `Mutation command: none` are explicit required fields in every debug output. If either field is absent or contains any value other than `none`, the output is invalid.
