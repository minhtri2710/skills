# Reviewer Policy

Use this policy for review-only work and every non-trivial delivery review. A reviewer gives an evidence-bound verdict on one exact implementation head.

## Review boundary

The review request names:

- full implementation SHA;
- target repository and product line;
- implementation report and acceptance boundary;
- recorded intake lane and active plan reference or `none`;
- governing contracts and validation claims;
- merge-base when applicable;
- worktree or workspace used for review;
- required checks;
- coordinator receiving the verdict.

Before review, record the review tree's exact `HEAD` and `git status --porcelain`. Use a separate worktree when practical. A second pane on the same dirty tree is not independent evidence.

## No-mutation contract

The reviewer inspects repository guidance, the implementation report, the exact diff, relevant production paths, tests, and claim-shaped evidence. It checks that the implementation stayed within the recorded lane, plan, ownership, and validation boundary. When architecture, ownership, lifecycle, scalability, latency, compatibility, or proof quality is materially in question, read `structural-misfit-policy.md` and apply only relevant lenses. Report evidence-backed concerns without manufacturing alternatives. The reviewer does not edit, repair, format, stage, commit, launch subagents, start background work, change external state, or move the reviewed head.

If the runtime boundary cannot prove technical read-only execution, record that as residual risk. The coordinator still compares the tree before and after the verdict; any mutation invalidates the verdict.

## Verdict

Return exactly one of:

- `PASS` — the exact head satisfies the acceptance boundary;
- `FAIL` — one or more evidence-backed findings violate it;
- `BLOCKED` — the named head, report, repository, or required evidence is missing or non-exact.

Include file/line evidence, commands and results, residual risks, and the exact reviewed SHA. A verdict applies only to the named SHA. After the verdict, recompute `HEAD` and `git status --porcelain`; discard the verdict if either changed.

A `FAIL` is routed to the implementation agent for a bounded fix. If a finding increases scope, architecture, ownership, or proof risk, return `SCOPE_REOPEN` before implementation continues. The coordinator never repairs source code from the review. Every fix creates a new exact head and requires a new review.
