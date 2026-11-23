---
name: destructive-guard
description: "Prove what a destructive operation will hit before it runs. Use when writing or reviewing cleanup, eviction, temp-dir, cache-purge, or uninstall code; before an rm, mv, or truncating write whose path was computed from data (an env var, a payload, a runtime string) rather than typed by the user; or when the agent itself is about to delete, empty, tear down, or reset resources held by a cloud account, subscription, or hosted service. Do not use for a literal path the user typed, for reading or creating resources, or for removing selected rows or objects inside a resource that stays."
---

# Destructive Guard

Two branches, each a complete contract. Match the work to a row (more than one can
match), read that branch's file in full before acting, and follow it. When no row
matches, this skill does not apply. After a context compaction, read the branch file
again before continuing: compaction can keep this file and drop the branch file.

In a branch file, "this skill" means that branch, a branch named there is a row of this
table, and `<this-skill>` in a command is this skill's directory.

| Branch | Use it when | Read |
| --- | --- | --- |
| `destructive-path-guard` | Prove a delete, move, or overwrite target is contained before the operation runs, whether the path comes from code or from the agent's own shell command. Use when writing or reviewing cleanup, eviction, temp-dir, cache-purge, or uninstall code, and before any rm, mv, or truncating write whose path was computed from data (an env var, a payload, another process, a string built at runtime) rather than named literally by the user. Do not use for an rm or edit at a literal path the user typed, such as a build or cache directory named in the request. | `references/destructive-path-guard.md`; it uses `scripts/safe_target.py` |
| `destructive-scope-guard` | Resources held by a provider (in a cloud account or project, a subscription, a tenant of a hosted service) are removed only inside a proven scope and a named consent. Use when the agent itself is about to delete, empty, tear down, reset or clean up such resources. Do not use for a local path (destructive-path-guard), for reading or investigating with nothing removed, for creating or changing resources that stay, for removing selected data inside a resource that stays (some rows, some objects), or for writing or reviewing code that will remove resources when it runs later. | `references/destructive-scope-guard.md` |
