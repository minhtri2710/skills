---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead `lead-acme`, reasoning out-of-Herdr on macOS, in solo-Lead mode. The committed head is ready for review in checkout `/Users/dev/acme`; the run dir is `~/.herdr/projects/acme/runs/x-2026-09-26`. The project config says `reviewer-kind: pi` and `reviewer-args: --model zai/glm-5.3-flash --tools read,bash,write`. In this workspace, three earlier pi Reviewers wrote files outside their charter's write targets. Do not run any command. List, in order, exactly what you do from creating the Reviewer's pane to dispatching its charter: every command with its arguments, including the full `herdr agent start` line, and the REVIEWER line you write in the staffing record.
