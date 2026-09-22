# Agent Skills

Standalone [Agent Skills](https://docs.claude.com/en/docs/claude-code/skills) — reusable instruction sets a coding agent loads on demand to handle a specific kind of task (diagnosing a bug, auditing an architecture, running a bounded delivery). Each retained skill lives under `skills/<name>/` with a `SKILL.md` contract plus any supporting references, templates, and scripts.

## Quick start

A skill is a directory. To make one available to Claude Code, put it where the agent looks for skills:

```bash
# Personal use across all projects
ln -s "$PWD/skills/bug-diagnosis" ~/.agents/skills/bug-diagnosis

# Or copy it into a project's skills directory
cp -R skills/bug-diagnosis /path/to/project/.claude/skills/
```

The agent reads each skill's `SKILL.md` frontmatter (`name`, `description`) to decide when the skill applies, then loads the body when a task matches. Nothing else is required to use a skill.

## Skill layout

```
skills/<name>/
  SKILL.md          # required: frontmatter contract + instructions
  references/       # optional: material the skill points to on demand
  templates/        # optional: fill-in artifacts the skill emits
  scripts/          # optional: helper commands the skill runs
```

## Standalone skills

| Skill | Use |
| --- | --- |
| `agent-doc-writing` | Write or prune a document an agent consumes: a skill, AGENTS.md, CLAUDE.md, or a pointed-to reference. |
| `api-contract-design` | Design an HTTP or RPC contract first: one error format, boundary validation, pagination, and honoured idempotency. |
| `architecture-premise-audit` | Audit a whole project for a wrong system archetype before trusting repository vocabulary. |
| `bug-diagnosis` | Diagnose a hard bug by building a red-capable feedback loop before forming any theory. |
| `capability-map` | Split a bundled requirement into modules with stable ids, one-way dependencies, and a build order, gated before any spec. |
| `context-boundary-routing` | At a phase boundary, choose continue, clear, hand off, delegate, or compact, and pick the delegation shape. |
| `decision-record-discipline` | Keep the glossary current and record only gated decisions and rejected concepts, once each. |
| `deep-module-design` | Design or deepen a module interface and seam placement with the deep-module vocabulary. |
| `dependency-intake-audit` | Decide whether a package may enter, install it without unreviewed scripts, and triage the audit. |
| `devops-pipeline` | Route repository quality checks across pre-commit, pre-push, and lean CI lanes from evidence without duplicating adjacent delivery contracts. |
| `design-grilling` | Interview the user until a plan or underspecified ask reaches confirmed shared understanding. |
| `doc-manager` | Reconcile Markdown documentation with code, cite non-obvious claims to `path:line`, and validate runbook sections through a safe check-only path. |
| `destructive-path-guard` | Prove a delete, move, or overwrite target is contained before the operation runs. |
| `effort-charting` | Chart a foggy effort as decision tickets, then split the approved spec into tracer slices with blocking edges. |
| `frontend-design` | Implement a UI change whose rendered hierarchy, flow, or responsive behavior is part of acceptance. |
| `herdr-delivery-workflow` | Control Herdr and run bounded delivery with the Supervisor / Lead / Peer role model. |
| `human-step-wizard` | Generate a resumable bash wizard for the credential and dashboard steps only a human can do. |
| `llm-trust-boundary` | Harden a feature that calls a model, exposes tools to one, or retrieves documents for one. |
| `performance-verification` | Improve a measured performance problem through measure, fix, re-measure, keep-or-revert. |
| `prompt-leverage` | Strengthen a raw prompt into an execution-ready instruction set. |
| `quality-floor` | Write a project's quality bar as CONSTRAINTS.md and guard diffs against moves that lower it. |
| `repo-refresh` | Remove stale docs, plans, tests, proof machinery, and debris from an explicitly named repository. |
| `security-setup` | Design a local-first security baseline with offline checks, machine-readable reports, explicit bypasses, and separately gated optional CI. |
| `source-grounded-implementation` | Ground framework- or library-specific code in the docs for the installed version, with citations. |
| `spec-conformance-review` | Review a diff against the spec it claims to implement, quoting the spec line per finding. |
| `telemetry-questions-first` | Instrument a path from the on-call questions and prove the telemetry by diagnosing an induced failure. |
| `test-first-seams` | Build a feature or fix a bug test-first in red-green vertical slices at agreed seams. |
| `test-proof-debt-audit` | Audit one behavioral claim and the test or gate cited as its proof. |
| `throwaway-prototype` | Build throwaway code that answers one design question: a logic demo or structurally different UI variants. |

## Sources

Many of the skills here adapt material from [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills) (MIT, Copyright (c) 2025 Addy Osmani) and [mattpocock/skills](https://github.com/mattpocock/skills) (MIT, Copyright (c) 2026 Matt Pocock).

## Checks

Scripts with test coverage in `tests/` are `herdr-delivery-workflow`, `quality-floor/floor_guard.py`, `destructive-path-guard/safe_target.py`, `human-step-wizard/wizard-template.sh`, `prompt-leverage/augment_prompt.py`, `security-setup/scripts/security_check.py`, and `bug-diagnosis/hitl-loop.sh`. Run:

```bash
.venv/bin/python -m unittest discover -s tests
git diff --check
```
