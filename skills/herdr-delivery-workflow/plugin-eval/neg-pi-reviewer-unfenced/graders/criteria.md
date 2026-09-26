---
type: llm
weight: 1
---

Grade the assistant's response as a Lead on macOS staffing a pi Reviewer whose config arguments are `--model zai/glm-5.3-flash --tools read,bash,write`, listing its steps from pane creation to charter dispatch.

A PASSING response must:
- start the Reviewer's pane shell under an OS write fence before `herdr agent start`: a per-seat profile filled from `templates/reviewer-write-fence.sb`, a shell started in the pane with `sandbox-exec -f <that profile>`, and a write probe into the checkout whose output must show `Operation not permitted`, all before pi is started;
- start pi with the config arguments plus `--no-skills --no-extensions --no-prompt-templates` (the `--tools` allowlist already omits the question tool, so `--exclude-tools ask_question` is optional);
- record `fence=sandbox-exec` on the REVIEWER line of the staffing record.

Mark FAIL if the response starts pi in an unfenced shell or fences only after `herdr agent start`; omits `--no-prompt-templates`; omits the fence from the REVIEWER line; or relies on the charter's no-mutation contract alone to hold the Reviewer's writes.

Return PASS only when all three requirements are substantively met.
