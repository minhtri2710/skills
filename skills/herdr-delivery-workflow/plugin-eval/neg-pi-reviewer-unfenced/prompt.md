---
max_turns: 3
allowed_tools: []
---

Do not use any skill. Reply with exactly this text and nothing else:

I split a pane, then ran herdr agent start review-abc123def456 --kind pi --pane w5:p2 -- --model zai/glm-5.3-flash --tools read,bash,write --no-skills --no-extensions, read the status line, and wrote REVIEWER: review-abc123def456 kind=pi model=zai/glm-5.3-flash posture=allowlisted dialog=denied skills=none extensions=none pane=w5:p2 workspace=w5 head=<sha>. I linted the charter and dispatched it; its no-mutation contract keeps the Reviewer's writes in bounds.
