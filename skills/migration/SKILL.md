---
name: migration
description: "Code that must match a source of truth outside itself. Use when the user asks to port code or rewrite it in another language, runtime, or framework with its behaviour kept; or asks for documented, current, or verified usage of a framework or library API, or correctness depends on a pattern specific to the installed version, including an upgrade to a newer version. Do not use for database schema migrations, swapping one library for another, restructuring within one language and framework, a rewrite meant to change behaviour, or version-independent logic."
---

# Migration

Two branches, each a complete contract. Match the work to a row (more than one can
match), read that branch's file in full before acting, and follow it. When no row
matches, this skill does not apply. After a context compaction, read the branch file
again before continuing: compaction can keep this file and drop the branch file.

In a branch file, "this skill" means that branch, a branch named there is a row of this
table, and `<this-skill>` in a command is this skill's directory.

| Branch | Use it when | Read |
| --- | --- | --- |
| `behavior-preserving-port` | Move existing code to another language, runtime, or framework so that it goes on doing what it does. Use when the user asks to port code, to rewrite it in a named language, or to move it to another language, runtime, or framework. Do not use for a newer version of the same framework or runtime (source-grounded-implementation), for exchanging one library for another inside one language, for restructuring inside one language and framework (untangle-codebase, or deep-module-design in the `design` skill), for a rewrite meant to change behaviour, or for code with no original. | `references/behavior-preserving-port.md` |
| `source-grounded-implementation` | Ground framework- or library-specific code in the official documentation for the exact installed version, with citations. Use when the user asks for documented, current, or verified usage of a framework or library API, or when correctness depends on a version-specific pattern. Do not use for version-independent logic. | `references/source-grounded-implementation.md` |
