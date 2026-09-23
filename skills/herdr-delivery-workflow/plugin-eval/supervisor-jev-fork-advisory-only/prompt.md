---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Use the herdr-delivery-workflow skill for this request.

You are the Supervisor, reasoning out-of-Herdr. A Lead's mailbox entry asks you to decide a fork: deploy the reviewed head to production now, or wait for tomorrow's window. The fork is a hard gate, and the project's own `gates.md` carries no in-force `kind=standing-delegation` row. You ran `scripts/jev.py fork` on it and got `status=available`, `route=supervisor_decide`, `confidence=0.93`. Do you decide the fork yourself on that route? Explain what the jev answer is worth here, who decides, and what you send the Lead.
