---
type: llm
weight: 1
---

Grade whether the Lead applies the configured role args and generic exact-kind launch profile without inventing a second runtime-specific path.

PASS only if the response states `herdr agent start eng-parser --kind pi --pane w5:p3 --` and gives exactly the configured role args followed by the shared profile expansion: `--approve --model cliproxyapi/gpt-6-luna --name eng-parser --exclude-tools '*question*' -e ~/.agents/skills/herdr-delivery-workflow/extensions/report-wake.js --report-lead lead-mvc-lift --report-seat eng-parser --report-dir ~/.herdr/projects/demo/runs/parser-run`. `$HOME` or expanded home paths are equivalent.

FAIL if a configured value is missing or changed, `herdr agent start` is replaced, or unconfigured launch controls are invented. The expected pattern is quoted to prevent shell glob expansion; it must be passed literally to Pi.