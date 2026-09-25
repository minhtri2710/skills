---
name: devops-pipeline
description: Route repository quality checks across local pre-commit, pre-push, and lean CI lanes from observed project evidence. Use when designing or auditing where checks belong without duplicating the quality floor, security setup, dependency intake, or Herdr delivery contracts.
---

# DevOps Pipeline

This skill designs a check-routing plan. It does not silently install tools,
change hooks, write CI, use credentials, commit, push, deploy, or make another
outward change.

The axis is **where an already evidenced repository check should run**:
fast changed-file checks at `pre-commit`, repository-wide local checks at
`pre-push`, and only genuinely environment-, version-, secret-, or
deployment-dependent work in CI. The three lanes are a routing policy, not a
request to generate configuration automatically.

## Human approval boundary

Inspection and a proposed routing plan are read-only. Before any outward change,
obtain explicit approval from the Human for the exact action and paths involved.
This includes:

- installing or upgrading a tool, package, hook framework, runner, or database;
- creating, merging, migrating, or installing hook configuration;
- creating or changing a CI workflow, permissions, environment, secret, or
  credential use;
- running a check that writes files, warms external data, contacts a service, or
  otherwise changes state;
- committing, pushing, opening or changing a pull request, deploying, releasing,
  or adopting a generated/installed copy.

A request to “consider CI,” an existing command in a repository, or write access
is not approval. Keep proposed commands and paths visible so the Human can
approve or reject them separately.

## Scope and adjacent owners

Keep this skill to routing and overlap policy. Do not recreate another skill's
contract:

- `quality-floor` owns numerical quality constraints and its diff guard. Reuse
  the repository's recorded commands and bounds; do not invent coverage floors,
  thresholds, or another diff-guard policy here.
- `security-setup` owns scanner selection, offline security configuration,
  machine-readable reports, and security bypass semantics. Route an already
  selected security check to a lane, but do not select scanners, define reports,
  or add a second bypass contract.
- `dependency-intake-audit` owns package acceptance, lifecycle-script controls,
  installation boundaries, and advisory triage. This skill never installs
  `pre-commit` or any project dependency as a setup shortcut.
- `herdr-delivery-workflow` owns agent orchestration and the Human-gate ledger.
  This skill states its action boundary but does not create a competing delivery
  workflow or scheduler path.

If the proposed pipeline cannot be reduced to this routing axis without copying
one of those owners, stop and report `REOPEN_REQUEST` rather than creating a
redundant skill.

## Evidence-first inspection

Inspect the target repository before assigning a lane. Use read-only evidence
from the repository and local tool availability; do not synchronize branches,
install missing tools, or infer facts from a template.

Record each relevant fact with its source and status:

| Fact | Evidence to seek | If unseen or unavailable |
| --- | --- | --- |
| repository root, branch, and changed paths | Git metadata and status | `Not-Assessed`; operator must confirm the target and base |
| languages and package/build managers | manifests, lockfiles, build files, scripts | `Not-Assessed`; operator must identify the toolchain |
| existing checks and their scope | test/lint/type/security config and documented commands | `Not-Assessed`; do not invent a command |
| local tool availability and versions | a read-only executable/version check | `Not-Assessed`; operator must provide or approve setup |
| existing hook configuration | `.pre-commit-config.yaml` and hook files | `Not-Assessed`; do not assume hooks exist or are installable |
| CI provider, default branch, permissions, and base SHA behavior | checked-in workflows and repository evidence | `Not-Assessed`; operator must confirm the CI boundary |
| credentials, secrets, and deployment prerequisites | explicit repository/operator evidence only | `Not-Assessed`; never probe or use them |
| CLI status and commands | an evidenced CLI entry point plus repository docs/source | `Not-Assessed`; do not add CLI E2E coverage by assumption |

`Not-Assessed` means the claim was not proven. It is not a pass, a failure
converted to green, or permission to guess. Name the operator prerequisite in
the plan and final report.

Also identify whether a check is already owned by `quality-floor` or
`security-setup`, whether a package/install step belongs to dependency intake,
and whether a delivery step belongs to the delivery owner. Preserve existing
hooks and workflows in the proposal; never treat their presence as permission to
overwrite or merge them.

## The routing table

Every substantive check has one primary lane. The only intentional overlap is
the CI bypass guard described below.

| Lane | Scope and purpose | Appropriate checks |
| --- | --- | --- |
| `pre-commit` stage | changed files; fast, deterministic, local checks with no credentials or runtime fetch | format, lint, type checks, compile/import checks, already-selected offline checks, and fast tests when repository evidence supports them |
| `pre-push` stage | the whole repository or the affected repository-wide surface before code leaves the machine | full tests, integration checks, repository-wide validation, and CLI E2E when the target is evidenced to be a CLI |
| CI | only work a developer's environment cannot credibly prove, or an explicitly approved external effect | version/OS matrices, genuinely isolated environment checks, credential-dependent work owned by the appropriate contract, and approved release/deployment work |

Do not put a laptop-runnable check in CI merely because CI is convenient. Do not
repeat a pre-push check as a single-version CI job. A matrix or materially
different environment is a distinct CI purpose; a duplicate command is not.
Keep the check's existing command and owner visible when mapping it to a lane.

### Hook stages

Use current pre-commit stage names in any proposed configuration:

- `pre-commit` for changed-file checks;
- `pre-push` for repository-wide local checks;
- `manual` only for an intentionally operator-invoked check.

Do not emit deprecated `commit` or `push` stage names. If an existing config
uses them, record a migration as a separately approved hook change. Do not run a
migration or install either hook without that approval. Remember that running
`pre-commit` without an explicit stage exercises the commit-stage default and
does not prove the `pre-push` suite.

### CLI E2E is conditional

Add a CLI E2E check only when repository evidence establishes that the target is a
CLI and identifies its commands or subcommands. Enumerate the evidenced command
surface, include representative success and failure paths, and route the suite
to `pre-push`. If CLI status or command enumeration is not proven, record it as
`Not-Assessed` and name the evidence an operator must provide; do not generate a
speculative script.

## CI overlap: one deliberate guard

If CI is explicitly requested and its provider, pull-request event, base branch,
toolchain, and permissions are evidenced, propose a thin CI guard rather than a
second full pipeline. The guard is the one deliberate overlap because local
hooks can be bypassed with `--no-verify`; its purpose is to verify incoming
changes, not to move local checks back into CI.

The guard must:

1. run only in the pull-request context where the base SHA is defined;
2. fetch the complete history needed for both diff endpoints;
3. use the repository's evidenced toolchain without silently installing one;
4. scope both invocations to the pull-request diff; and
5. name both modern hook stages explicitly.

The essential command shape is:

```sh
base="<evidenced pull-request base SHA>"
pre-commit run --hook-stage pre-commit --from-ref "$base" --to-ref HEAD
pre-commit run --hook-stage pre-push --from-ref "$base" --to-ref HEAD
```

The surrounding workflow must make the pull-request condition and full-history
requirement explicit. Do not use an all-files CI run as the bypass guard. Do not
add a separate CI lint, format, type-check, full-test, or CLI-E2E job when the
same check is already owned by a local lane. Do not add a secret, token, hosted
scanner, upload, deployment, or release step without its own Human approval and
an owner contract.

If the CI platform, default branch, base SHA, toolchain, permissions, or required
credential is not evidenced, leave the CI proposal `Not-Assessed` and state the
operator prerequisite. A user request to investigate CI is not authorization to
write it.

## Existing configuration and unavailable tools

Treat existing `.pre-commit-config.yaml`, hook files, and CI workflows as
reviewable user-owned configuration:

- never overwrite them;
- do not merge, migrate, install, or remove hooks without explicit Human
  approval;
- preserve existing hook IDs, pinned revisions, and unrelated workflow steps in
  any later approved change;
- surface conflicting stages, duplicate commands, and missing toolchains rather
  than hiding them with skips or relaxed rules.

If a required executable, package manager, project command, runner capability,
security database, or CI prerequisite is unavailable, report the affected check
as `Not-Assessed`, its exact prerequisite, and whether the lane assignment can
still be reviewed. Never claim a configured hook, audit, matrix, or workflow
passes from configuration text alone.

## Read-only verification and report

After producing a routing plan, verify only what is available and safe to run in
check-only mode. Record the command and real exit code. A missing executable,
missing project fact, unavailable database, malformed config, or unrun stage
remains visible as `Not-Assessed`; it is not silently suppressed.

The report should include:

- evidence inspected and the fact/source/status table;
- every check and its single primary lane, including deliberate CI overlap;
- modern stage-name findings and any deprecated names requiring approval;
- CLI evidence or `Not-Assessed` status;
- existing hooks/workflows that were deliberately not changed;
- Human approvals still required and their exact proposed paths/actions;
- checks run, checks skipped, real exit codes, and residual risks.

This skill is complete when the routing decision is evidence-backed, unavailable
facts are explicit, the local/CI overlap is limited to the diff-scoped dual-stage
guard, and no outward change has been implied or performed without approval.
