---
name: docs
description: "Write the documents a project keeps. Use when creating, editing, reviewing, or trimming a document an agent reads (a skill, AGENTS.md, CLAUDE.md, a reference file); when README or docs Markdown, including a setup or deploy runbook, must match the code; whenever a PR or merge request description is written or revised; or when the user wants a prompt for Codex or another agent strengthened, or a hook that upgrades prompts. Do not use to run evals or benchmarks on a skill (skill-creator), to post or merge on the forge, or for product copy, commit messages, or release notes."
license: MIT
---

# Docs

Four branches, each a complete contract. Match the work to a row (more than one can
match), read that branch's file in full before acting, and follow it. When no row
matches, this skill does not apply. After a context compaction, read the branch file
again before continuing: compaction can keep this file and drop the branch file.

In a branch file, "this skill" means that branch, a branch named there is a row of this
table, and `<this-skill>` in a command is this skill's directory.

| Branch | Use it when | Read |
| --- | --- | --- |
| `agent-doc-writing` | Write or prune a document an agent consumes — a skill, AGENTS.md, CLAUDE.md, or a doctrine or reference file reached by a pointer. Use when creating, editing, reviewing, or trimming such a document. Do not use for human-facing README or product documentation, or to run evals and benchmarks on a skill; that is skill-creator. | `references/agent-doc-writing.md` |
| `doc-manager` | Reconcile Markdown documentation with the implementation and produce only source-grounded claims, citing non-obvious facts to path:line and asking when evidence is ambiguous. Use for README, docs, and component Markdown that must match code. If a document contains a setup, release, deploy, or operational runbook, also validate that section through the check-only path in references/doc-manager-runbook-validation.md. Do not use for API-reference generation, product copy, or AGENTS.md/CLAUDE.md. | `references/doc-manager.md`; it uses `references/doc-manager-runbook-validation.md` |
| `pr-body` | Write, draft, rewrite, or revise a PR description or PR body (the text of a pull or merge request), covering the shape of the change, what merging puts at risk, and the evidence observed. Use whenever that text is written, including while a delivery workflow opens or updates the request. Do not use for carrying out the act on the forge (posting, opening, changing state, merging), a commit message, or release notes. | `references/pr-body.md` |
| `prompt-leverage` | Strengthen a raw user prompt into an execution-ready instruction set for Codex or another AI agent. Use when the user wants to improve an existing prompt, build a reusable prompting framework, wrap the current request with better structure, add clearer tool rules, or create a hook that upgrades prompts before execution. | `references/prompt-leverage.md`; it uses `references/prompt-leverage-framework.md` and `scripts/augment_prompt.py` |
