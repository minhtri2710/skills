---
name: security
description: "Harden a project against insecure code and supply-chain risk. Use when setting up a repository's local security checks (secret detection, dependency and static scans); when adding, upgrading, or replacing a dependency, triaging audit or advisory-bot findings, or reviewing a lockfile diff; or when building or reviewing a chatbot, summarizer, agent loop, RAG pipeline, MCP server, or any code that gives a model tools or puts model output into a query, command, markup, or path. Do not use for a general vulnerability review, audit, or pen test, incident response, cloud security review, or choosing libraries on features."
license: MIT
effort: high
---

# Security

Three branches, each a complete contract. Match the work to a row (more than one can
match), read that branch's file in full before acting, and follow it. When no row
matches, this skill does not apply. After a context compaction, read the branch file
again before continuing: compaction can keep this file and drop the branch file.

In a branch file, "this skill" means that branch, a branch named there is a row of this
table, and `<this-skill>` in a command is this skill's directory.

| Branch | Use it when | Read |
| --- | --- | --- |
| `security-setup` | Design and, after explicit approval, implement a local-first security baseline with always-on secret detection, offline-capable dependency and static checks, machine-readable reports, explicit bypasses, and a separately gated optional CI mirror. Use when hardening a repository's local security workflow. Do not use for incident response, cloud security review, or deciding whether a dependency may enter the project. | `references/security-setup.md`; it uses `references/security-setup-tool-selection.md`, `references/security-setup-configuration-template.md`, `references/security-setup-verification-scenarios.md` and `scripts/security_check.py` |
| `dependency-intake-audit` | Decide whether a package may enter the project, install it without letting its lifecycle scripts run unreviewed, and triage what the audit reports. Use when adding, upgrading, or replacing a dependency, when an audit or advisory bot reports findings, or when a lockfile diff needs review. Do not use for choosing between libraries on features alone. | `references/dependency-intake-audit.md` |
| `llm-trust-boundary` | Harden a feature that calls a model, exposes tools to one, or retrieves documents for one. Use when building or reviewing a chatbot, summarizer, agent loop, RAG pipeline, MCP server, or any code path that puts model output into a query, a command, markup, or a file path. Do not use for prompt wording or output quality. | `references/llm-trust-boundary.md` |
