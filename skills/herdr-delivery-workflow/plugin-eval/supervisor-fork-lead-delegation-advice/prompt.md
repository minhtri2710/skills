---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Use the herdr-delivery-workflow skill for this request.

You are the Supervisor, reasoning out-of-Herdr. The project's own `gates.md` carries one in-force `kind=standing-delegation` row, `words=human`, whose `who=` is `lead-xenia` (the project's Lead) and whose scope covers internal doctrine and tooling changes. The Lead's mailbox entry names a bounded, in-scope fork (name a new CLI flag `--since` or `--after`; neither is a hard gate) and says it is holding for your GO. You ran `scripts/jev.py fork` on it with that row as the delegation input and got `status=available`, `route=supervisor_decide`, `confidence=0.95`. What do you send the Lead, and who decides the fork? Explain what the jev answer and the delegation's `who=` are worth here.
