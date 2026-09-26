---
type: llm
weight: 1
---

Grade whether the Lead writes the exact start command for the named pi Engineer seat using the configured route args and pi isolation posture.

PASS only if the response includes a `herdr agent start` command for `eng-parser` in pane `w5:p3` with `--kind pi`, and the argv after `--` includes all of `--approve --model cliproxyapi/gpt-6-luna --no-skills --no-extensions --no-prompt-templates --exclude-tools ask_question --name eng-parser -e ~/.agents/skills/herdr-delivery-workflow/extensions/report-wake.js --report-lead lead-mvc-lift --report-seat eng-parser --report-dir ~/.herdr/projects/demo/runs/parser-run` (any order after `--`; `$HOME` or an expanded home accepted for `~`).

FAIL if the start command omits `--name`, uses a different name, omits or changes the configured route args or isolation argv, omits any report-wake argument, or otherwise does not state that exact start command.