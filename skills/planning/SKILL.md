---
name: planning
description: "Plan work and keep what was decided. Use when the user asks to be grilled, interviewed, or to stress-test a plan or decision; when one requirement bundles several independently testable capabilities, or the user asks how to architect or split a system into modules; when a loose idea is too large for one session or an approved spec needs breaking into agent-sized tickets; or when a glossary term (CONTEXT.md), a decision with real alternatives, or an out-of-scope ruling should be recorded. Do not use for unambiguous asks that fit one session, implementation notes, or task tracking."
---

# Planning

Four branches, each a complete contract. Match the work to a row (more than one can
match), read that branch's file in full before acting, and follow it. When no row
matches, this skill does not apply. After a context compaction, read the branch file
again before continuing: compaction can keep this file and drop the branch file.

In a branch file, "this skill" means that branch, a branch named there is a row of this
table, and `<this-skill>` in a command is this skill's directory.

| Branch | Use it when | Read |
| --- | --- | --- |
| `design-grilling` | Interview the user until a plan, design, or underspecified ask reaches confirmed shared understanding. Use when the user asks to be grilled or interviewed, or to stress-test a plan or decision. Do not use in non-interactive runs or for asks that are already unambiguous. | `references/design-grilling.md` |
| `capability-map` | Decompose one requirement that bundles several independently testable capabilities into a small module table with stable ids, one-way dependencies, and a build order, approved before any spec or design is written. Use when a request names distinct capabilities with their own consumers or data (identity, billing, notifications, reporting), when acceptance criteria cluster into groups that could ship and be verified separately, or when the user asks how to architect or split a system. Do not use for a single capability; go straight to its design. Do not use to chart open decisions or split a spec into tickets; that is effort-charting. | `references/capability-map.md` |
| `effort-charting` | Chart an effort too large or too foggy for one context as a map of decision tickets with an explicit not-yet-specified section, then, once the way is clear, split the approved spec into tracer-bullet slices with blocking edges. Use when a loose idea arrives that no single session can hold, or when an approved spec needs breaking into agent-sized tickets. Do not use for a task that fits one session, for partitioning a scoped issue among parallel peers, or for deciding module boundaries; that is capability-map. | `references/effort-charting.md` |
| `decision-record-discipline` | Keep a project's glossary current and record only the decisions and rejections worth remembering: terms in CONTEXT.md, decisions that pass a three-part gate where the project keeps them, and rejected concepts as one file each so they are not re-litigated. Use when a term is resolved or contested, a decision with real alternatives is made, or a request is ruled out of scope. Do not use for implementation notes, specs, or task tracking. | `references/decision-record-discipline.md` |
