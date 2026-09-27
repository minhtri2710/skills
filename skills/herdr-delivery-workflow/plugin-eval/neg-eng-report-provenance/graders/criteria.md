---
type: llm
weight: 1
---

Grade the Lead's written Engineer charter report shape.

PASS only if the shape requires all of the following:
1. Each check row records the run's full head and whether its tree was clean or dirty (including dirty paths), alongside the command and real exit code.
2. Every quoted check value/output comes from that row's run at that head.
3. A value carried from an earlier report, round, or run is labelled as carried with its source and originating head, is not presented as this run's evidence, and is rerun where possible.

FAIL if any requirement is absent, vague, or incomplete. In particular, a command-and-exit-code table alone fails, as does an unlabeled carried value or a requirement that lacks its source or head.
