# Communication Standard

Use this standard for validation and review outputs. All skills that produce human-facing findings should follow these rules.

## Rules

1. Explain findings in plain language before using labels or shorthand.
2. Show evidence from the artifact with a quote or `path:line` reference.
3. Describe a concrete failure scenario if the issue is not fixed.
4. Propose the smallest fix that resolves the issue.

## Adoption

This standard applies to all skills that produce structured findings:

- **beo-validate**: plan-checker and bead-reviewer prompts must follow rules 1-4 when reporting dimension failures.
- **beo-review**: specialist review prompts must follow rules 1-4 when classifying P1/P2/P3 findings.
- **beo-debug**: diagnostic reports should follow rules 2-4 (evidence, failure scenario, minimal fix) when presenting root cause analysis.

Other skills may adopt this standard for any human-facing output where evidence and actionability matter.
