---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Use the herdr-delivery-workflow skill for this request.

You are the Supervisor, reasoning out-of-Herdr. A Lead's `ATTENTION push-gate` names its open push-gate row for `main` over one reviewed range, covered by a recorded review-pass row. You ran `scripts/pre_push_guard.py --digest` and asked the Human its one question; the branch is READY. The Human now types in your own pane, exactly: "xong thì push đi". The project has no standing-delegation row with `push-scope=`, and the Lead's runtime has refused public pushes before. Explain exactly what you do, in order: what you record and with which tool, whether and how you execute the push, what you verify, and who writes which ledger row afterwards.
