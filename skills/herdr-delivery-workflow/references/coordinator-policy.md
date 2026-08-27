# Coordinator Policy

Use this policy for delivery or bounded monitoring. It defines the coordinator's authority and the minimum evidence needed to move between stages.

## Intake and risk

Read `intake-policy.md` before creating panes, agents, worktrees, or tabs. It is the single source of truth for lanes, hard gates, design gates, high-risk plans, intake records, and `SCOPE_REOPEN`.

Keep the current run context explicit:

- `Lane`, `Reason`, `Owners`, `Plan`, and `Validation`;
- outcome and acceptance boundary;
- target repository/product line, exclusions, base, merge-base, and current worktree condition;
- one writer and one owner for each moving scope;
- dependencies, stop conditions, and next action;
- Human-owned gates;
- Herdr resources created by this run.

Pass the recorded lane, plan reference, governing contracts, and validation claims into each implementation or review charter. If architecture, ownership, lifecycle, scalability, latency, compatibility, or proof quality is materially uncertain, read `structural-misfit-policy.md` and apply only the relevant lenses.

## Ownership and topology

The coordinator is the single routing and acceptance owner for the run. Use one writer per moving scope. Create a dedicated worktree for concurrent writers, requested isolation, or an independent review. Keep each agent's name, pane ID, workspace ID, worktree path, branch, and exact head together in the run context.

Preserve the caller's focus and working directory by default. Use `--no-focus`, `--current`, or an explicit ID. Read every returned ID from Herdr JSON before using it. Do not create extra coordinator roles, hidden workers, native-provider subagents, schedules, background orchestration, or a second state system.

## Lifecycle and waiting

Use `herdr agent prompt --wait` or `herdr agent wait` with a named target and a finite timeout. Do not poll `herdr agent list`, repeatedly sleep, or loop status commands. A settled `idle` or `done` state only means the agent can be inspected; it does not establish completion or acceptance. A blocked state requires reading the UI and routing the Human decision or concrete blocker.

If a wait fails, inspect the agent and preserve partial evidence before choosing the next action. Do not duplicate an active run merely because a response is slow.

## Acceptance custody

Before review, recompute the implementation repository's:

- full `git rev-parse HEAD`;
- merge-base;
- changed-file list;
- `git status --porcelain`;
- every acceptance command and real exit code.

A moving branch, missing commit, stale report, or unexplained dirty state is not reviewable. Return it to the implementation agent or route the blocker.

Accept only after an independent reviewer returns `PASS` for that exact head and the coordinator confirms the review tree did not move or become dirty. Any implementation change after review creates a new head and requires a fresh review.

## Coordinator boundaries

The coordinator may route work, classify findings, verify evidence, and decide whether the stated acceptance boundary is met. The coordinator does not repair source code after a review finding; it sends the bounded fix to the implementation agent. Scope, architecture, dependency, security, external-effect, and irreversible changes require the appropriate Human decision before crossing the boundary.

When new evidence increases blast radius, irreversibility, uncertainty, ownership impact, or proof weakness, stop before crossing the old boundary and emit `SCOPE_REOPEN` with the old lane, proposed lane, changed boundary, and decision needed. Do not lower intake to preserve momentum.
