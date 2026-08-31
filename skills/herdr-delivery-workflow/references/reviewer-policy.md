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
- the checkout, workspace, and pane used for review;
- the agent kind running the review and the agent kind that produced the head;
- required checks;
- coordinator receiving the verdict.

Review runs in the delivery's single checkout, from its own pane, after the implementation stage has stopped. That is honest evidence only when the tree is frozen: the implementation agent is idle, `git rev-parse HEAD` equals the named implementation SHA, and `git status --porcelain` is empty apart from entries the coordinator has already explained in the record. Record `HEAD` and porcelain before the review and again after it, and discard the verdict if either moved. A review taken while the implementation agent is still editing is not evidence, however clean the diff looked.

Run the review on a different agent kind than the implementation agent when another kind is installed, and record every agent's kind beside its name, pane, workspace, branch, and exact head. A review-only route never reads the coordinator policy, so the roster has to be built here.

Choose the reviewer kind and its fallback kind before staffing, and pin both to the same exact head. Take the preferred reviewer kind and fallback from the Human-owned project config (`project-config.md`, at `~/.herdr/projects/<project-slug>/config.md`) when one is recorded; an explicit Human instruction in the current request overrides it. Write the staffing record before the review starts. The FALLBACK trigger list and the INDEPENDENCE rule are fixed text — copy them verbatim into the record whatever the scenario, because they state when a substitution fires and what a same-kind review would mean, not what happened this run:

```text
IMPLEMENTATION: <name> kind=<kind> pane=<id> head=<exact SHA>
REVIEWER: <name> kind=<kind> pane=<id> head=<same exact SHA>
FALLBACK: kind=<kind>, pinned to the same exact head; triggers: preferred kind uninstalled or unavailable; reviewer errors or reaches no verdict; only remaining kind is the implementation kind; reviewer breaks read-only — a no-mutation violation
INDEPENDENCE: <different-kind | same-kind> — a same-kind review counts as recorded residual risk, not independence
```

Deciding the fallback in advance is what keeps a substitution visible: a reviewer that dies mid-review otherwise gets replaced by whatever is convenient, which is usually the implementation kind, and the swap never reaches the record. When the review does end up on the same kind, the INDEPENDENCE line and the verdict both say so as residual risk.

Name the reviewer with the exact head it reviews and rename it with `herdr agent rename` whenever that head changes, so the agent listing alone proves which head a verdict covers. A name pointing at a head the reviewer no longer sits on is worse than no name, because it invites belief.

## No-mutation contract

The reviewer inspects repository guidance, the implementation report, the exact diff, relevant production paths, tests, and claim-shaped evidence. It checks that the implementation stayed within the recorded lane, plan, ownership, and validation boundary. The implementation report is a claim to test, not a narrative to confirm: attempt to disconfirm each material claim with a concrete failure scenario against the acceptance boundary — an input, state, or sequence that would make the claim false — and report what was tried even when nothing fails. Agreement reached without a disconfirming attempt is compliance, not review. When architecture, ownership, lifecycle, scalability, latency, compatibility, or proof quality is materially in question, read `structural-misfit-policy.md` and apply only relevant lenses. Report evidence-backed concerns without manufacturing alternatives. The reviewer does not edit, repair, format, stage, commit, launch subagents, start background work, change external state, or move the reviewed head.

If the runtime boundary cannot prove technical read-only execution, record that as residual risk. The coordinator still compares the tree before and after the verdict; any mutation invalidates the verdict.

## Verdict

Return exactly one of:

- `PASS` — the exact head satisfies the acceptance boundary;
- `FAIL` — one or more evidence-backed findings violate it;
- `BLOCKED` — the named head, report, repository, or required evidence is missing or non-exact.

Include file/line evidence, commands and results, residual risks, and the exact reviewed SHA. A verdict applies only to the named SHA. After the verdict, recompute `HEAD` and `git status --porcelain`; discard the verdict if either changed.

A `FAIL` is routed to the implementation agent for a bounded fix. If a finding increases scope, architecture, ownership, or proof risk, return `SCOPE_REOPEN` before implementation continues. The coordinator never repairs source code from the review. Every fix creates a new exact head and requires a new review.
