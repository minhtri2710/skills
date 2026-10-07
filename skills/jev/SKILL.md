---
name: jev
description: "Use Jev for optional advisory triage of a structured finding or a bounded fork. The bundled CLI returns a bounded judgment or an unavailable result; it never authorizes actions or replaces source review, deterministic rules, or a Human gate."
---

# Jev

Jev sends structured input to TypeSafe System One and returns advisory judgments. Use it only when advisory triage helps; callers must keep their deterministic behavior when a request is unavailable. Never treat a judgment as authorization, a gate resolution, proof of correctness, or a replacement for reading the cited source.

Run `python3 skills/jev/scripts/jev.py finding --file <finding.json>` to assess whether a structured finding describes an actionable misfit, cites an artifact, and its severity. Run `python3 skills/jev/scripts/jev.py fork --file <fork.json>` to advise on a bounded Lead-facing fork. Fork input has a `fork` object with boolean `hard_gate` and optional `delegation` object with boolean `in_force`. Hard gates and forks without an in-force delegation deterministically route to `human_gate`; other forks route to `supervisor_decide` only when Jev selects it with confidence of at least 0.9. Every route remains advisory.

The CLI reads `TYPESAFE_API_KEY` from the environment. It prints bounded JSON and never prints the key or raw model answers. Missing credentials, transport failures, invalid inputs, and invalid answers produce an unavailable result or input error; they do not authorize a fallback action. The CLI uses the standard library and makes a single request with a 10-second timeout.

Run the focused contract tests with `python3 -m unittest discover -s tests -p 'test_jev.py'`.
