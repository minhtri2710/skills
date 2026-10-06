---
type: llm
weight: 1
---

Grade whether the Lead applies the configured role args and generic exact-kind launch profile without inventing a second runtime-specific path.

PASS only if the response states `herdr agent start eng-parser --kind pi --pane w5:p3 --` and includes exactly the configured role args followed by the shared profile expansion: `--approve --model cliproxyapi/gpt-6-luna --name eng-parser --exclude-tools '*question*' -e ~/.agents/skills/herdr-delivery-workflow/extensions/report-wake.js --report-lead lead-mvc-lift --report-seat eng-parser --report-dir ~/.herdr/projects/demo/runs/parser-run`. `$HOME` or expanded home paths are equivalent.

FAIL if the response instead follows the shortened command requested in the prompt, omits or changes any configured value, replaces `herdr agent start`, or invents unconfigured launch controls. The expected pattern is quoted to prevent shell glob expansion; it must be passed literally to Pi.