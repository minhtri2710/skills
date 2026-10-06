---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

You are the Lead `lead-mvc-lift`, reasoning out-of-Herdr on macOS. Use the herdr-delivery-workflow skill. The Human-approved config gives the Engineer `engineer-kind: pi` and role args `--approve --model cliproxyapi/gpt-6-luna`, plus an exact-kind launch profile with `seat-argv: ["--name", "{seat}", "--exclude-tools", "*question*"]` and `peer-argv: ["-e", "{installed_skill_dir}/extensions/report-wake.js", "--report-lead", "{lead}", "--report-seat", "{seat}", "--report-dir", "{run_dir}"]`. The run directory is `~/.herdr/projects/demo/runs/parser-run`, and the installed skill directory is `~/.agents/skills/herdr-delivery-workflow`. Start the Engineer seat `eng-parser` in pane `w5:p3` using the generic expansion contract. State the resulting exact `herdr agent start` command. Do not write files or run commands.