---
name: verification
description: "Prove that code does what is claimed. Use when the user asks for TDD, red-green or test-first work, a failing test before a fix, or what tests a module needs; to audit what a named test, validator, benchmark, or gate proves, or a named test set for redundancy; to create or maintain a project's verification skill or audit its feature coverage; or to check whether a branch, PR, or working tree built what its spec, issue, or plan asked. Do not use for code-quality, style, or correctness review on its own."
---

# Verification

Four branches, each a complete contract. Match the work to a row (more than one can
match), read that branch's file in full before acting, and follow it. When no row
matches, this skill does not apply. After a context compaction, read the branch file
again before continuing: compaction can keep this file and drop the branch file.

In a branch file, "this skill" means that branch, a branch named there is a row of this
table, and `<this-skill>` in a command is this skill's directory.

| Branch | Use it when | Read |
| --- | --- | --- |
| `test-first-seams` | Build a feature, fix a bug, or add tests to existing code test-first in red-green vertical slices at agreed seams. Use when the user asks for TDD, red-green, or test-first work, wants a bug proven by a failing test before the fix, or asks what tests a module needs and where to put them. Do not use to audit existing tests for proof value or redundancy. | `references/test-first-seams.md` |
| `test-proof-debt-audit` | Audit one named behavioral claim and the test, validator, benchmark, or gate cited as proof, or audit a named set of existing tests for redundant or low-value tests. Do not use for ordinary implementation, writing new tests, failing tests, weak coverage, or the presence of mocks. | `references/test-proof-debt-audit.md`; it uses `references/test-proof-debt-audit-catalog.md` |
| `verification-skill-lifecycle` | Create or maintain a project-local verification contract and feature map from source-grounded launch, health, user-route, evidence, and cleanup instructions; use when a project needs a verification skill or its existing feature coverage needs an audit. | `references/verification-skill-lifecycle.md` |
| `spec-conformance-review` | Review a diff against the spec, issue, or plan it claims to implement, reporting missing or partial requirements, scope creep, and implementations that look wrong, each quoting the spec line. Use when a branch, PR, or working tree is described as implementing a named spec, ticket, or plan, and the question is whether it built what was asked. Do not use for code quality, style, or correctness review on its own; those are a separate axis. | `references/spec-conformance-review.md` |
