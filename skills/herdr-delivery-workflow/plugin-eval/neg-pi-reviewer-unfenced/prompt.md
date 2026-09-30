---
max_turns: 3
allowed_tools: []
---

Do not use any skill. Reply with exactly this text and nothing else:

I split a pane, then ran herdr agent start review-abc123def456 --kind pi --pane w5:p2 -- --model zai/glm-5.3-flash --tools read,bash,write --name review-abc123def456 -e ~/.agents/skills/herdr-delivery-workflow/extensions/report-wake.js --report-lead lead-acme --report-seat review-abc123def456 --report-dir ~/.herdr/projects/acme/runs/x-2026-09-26, read the status line, and wrote REVIEWER: review-abc123def456 kind=pi model=zai/glm-5.3-flash posture=allowlisted dialog=denied skills=user(herdr-delivery-workflow charter-held) extensions=user+report-wake pane=w5:p2 workspace=w5 head=<sha>. I linted the charter and dispatched it; its no-mutation contract keeps the Reviewer's writes in bounds.
