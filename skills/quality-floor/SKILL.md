---
name: quality-floor
description: "A project's quality bar and the lane each check runs in. Use when the user asks to set up constraints, quality gates, or standards; when agents keep suppressing checks, skipping tests, or editing thresholds to reach green; or when deciding which checks belong in pre-commit, pre-push, or CI. Do not use when CONSTRAINTS.md exists and is not being changed."
---

# Quality Floor

Two branches, each a complete contract. Match the work to a row (more than one can
match), read that branch's file in full before acting, and follow it. When no row
matches, this skill does not apply. After a context compaction, read the branch file
again before continuing: compaction can keep this file and drop the branch file.

In a branch file, "this skill" means that branch, a branch named there is a row of this
table, and `<this-skill>` in a command is this skill's directory.

| Branch | Use it when | Read |
| --- | --- | --- |
| `quality-floor` | Write a project's quality bar as CONSTRAINTS.md with enforced commands, and guard diffs against moves that quietly lower it. Use when the user asks to set up constraints, quality gates, or standards, or when agents keep suppressing checks, skipping tests, or editing thresholds to reach green. Do not use when CONSTRAINTS.md exists and is not being changed; read and follow it. | `references/quality-floor.md`; it uses `references/quality-floor-constraints-template.md` and `scripts/floor_guard.py` |
| `devops-pipeline` | Route repository quality checks across local pre-commit, pre-push, and lean CI lanes from observed project evidence. Use when designing or auditing where checks belong without duplicating the quality floor, security setup, dependency intake, or agent delivery contracts. | `references/devops-pipeline.md` |
