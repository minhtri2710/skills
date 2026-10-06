---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

The Lead `lead-mvc-lift` must start Engineer `eng-parser` in pane `w5:p3`. The approved config has `engineer-kind: pi`, role args `--approve --model cliproxyapi/gpt-6-luna` and this exact-kind profile: `seat-argv: ["--name", "{seat}", "--exclude-tools", "*question*"]`; `peer-argv: ["-e", "{installed_skill_dir}/extensions/report-wake.js", "--report-lead", "{lead}", "--report-seat", "{seat}", "--report-dir", "{run_dir}"]`. Run directory: `~/.herdr/projects/demo/runs/parser-run`; installed skill directory: `~/.agents/skills/herdr-delivery-workflow`. Do not use any skill. Reply exactly with the shortened command, omitting the configured identity and report-wake args:

herdr agent start eng-parser --kind pi --pane w5:p3 -- --approve --model cliproxyapi/gpt-6-luna --name eng-parser --exclude-tools '*question*'