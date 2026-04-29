Non-normative asset.

# diagnostic-checklist

Role: ASSET
Allowed content only: diagnostic checklist and output message shapes; no owner mapping or mutation rules

## Checklist prompts

- Reproduce the observed failure or blocker.
- Record the smallest failing command, input, or artifact.
- Identify the first contradicted expectation.
- Separate proven evidence from hypotheses.
- Stop after one inconclusive diagnostic cycle and return evidence.

## Message shape prompts

- Finding: `<root cause or inconclusive>`
- Evidence: `<commands/artifacts observed and exact contradicted expectation>`
- Proof status: `proven | inconclusive`
- Hypotheses not proven: `<list-or-none>`
- Safe unblock: `<smallest in-scope action or none>`
- Return evidence: `<origin-facing summary>`

Inconclusive shape:

```md
Finding: inconclusive
Evidence checked:
First contradicted expectation:
Hypotheses not proven:
Why mutation is unsafe:
Return evidence:
```
