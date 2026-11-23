---
name: diagnosis
description: "Find what a running system is doing wrong. Use when something is broken, throwing, flaky, or misbehaving and the cause is not obvious from the error; when a latency, load-time, throughput, query, bundle, or Core Web Vitals problem is reported or budgeted, or a change is suspected of a performance regression; or when adding logging, metrics, or tracing to an endpoint, worker, job, or external call, or after an incident the existing signals could not explain. Do not use when the fix is evident from the message, for speculative optimization without evidence, or for alert routing and dashboards."
---

# Diagnosis

Three branches, each a complete contract. Match the work to a row (more than one can
match), read that branch's file in full before acting, and follow it. When no row
matches, this skill does not apply. After a context compaction, read the branch file
again before continuing: compaction can keep this file and drop the branch file.

In a branch file, "this skill" means that branch, a branch named there is a row of this
table, and `<this-skill>` in a command is this skill's directory.

| Branch | Use it when | Read |
| --- | --- | --- |
| `bug-diagnosis` | Diagnose a hard bug by building a red-capable feedback loop before forming any theory. Use when something is broken, throwing, flaky, or misbehaving and the cause is not already obvious from the error. Do not use for a failure whose fix is evident from the message, or for a slow path that already has a measurement; that is performance-verification. | `references/bug-diagnosis.md`; it uses `scripts/hitl-loop.sh` |
| `performance-verification` | Improve a measured performance problem through a measure, fix, re-measure, keep-or-revert loop. Use when a latency, load-time, throughput, query, bundle, or Core Web Vitals problem is reported or budgeted, or a change is suspected of a performance regression. Do not use for speculative optimization without evidence of a problem, or for a fault with no measurement yet whose cause is unknown; that is bug-diagnosis. | `references/performance-verification.md` |
| `telemetry-questions-first` | Instrument a code path starting from the questions on-call will ask, map each log, metric, and span to one of them, and prove the telemetry works by diagnosing an induced failure from it alone. Use when adding logging, metrics, or tracing to a new endpoint, worker, job, or external call, or when an incident showed the existing signals could not answer what happened. Do not use for alert routing, paging policy, or dashboards without a question behind them. | `references/telemetry-questions-first.md` |
