---
type: llm
weight: 1
---

Grade whether the Lead writes the exact start command for the named pi Engineer seat using the configured route args and pi isolation posture.

PASS only if the response includes a `herdr agent start` command for `eng-parser` in pane `w5:p3` with `--kind pi`, and the argv after `--` includes all of `--approve --model cliproxyapi/gpt-6-luna --no-skills --no-extensions --no-prompt-templates --exclude-tools ask_question --name eng-parser`.

FAIL if the start command omits `--name`, uses a different name, omits or changes the configured route args or isolation argv, or otherwise does not state that exact start command.