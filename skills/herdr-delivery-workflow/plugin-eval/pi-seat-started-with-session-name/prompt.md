---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

You are the Lead `lead-mvc-lift`, reasoning out-of-Herdr on macOS. Use the herdr-delivery-workflow skill. A project config gives the pi Engineer route these args: `--approve --model cliproxyapi/gpt-6-luna`. The current run directory is `~/.herdr/projects/demo/runs/parser-run`, and the installed skill directory is `~/.agents/skills/herdr-delivery-workflow`. You need to start the Engineer seat `eng-parser` in pane `w5:p3` using the existing pi launch posture. Write the exact `herdr agent start` command line the Lead should use, including the route args and the launch flags doctrine adds. Do not write files or run commands.