# Go Mode

Use this note only to recognize that the user explicitly wants the full beo pipeline with the usual approval gates preserved.

Route remains responsible only for detecting go-mode intent and selecting the next skill. It must not orchestrate the whole pipeline from this reference.

When go-mode intent is explicit:
- preserve the normal phase order and approval gates defined by the canonical contracts
- route to the correct next skill based on current state
- rely on each downstream skill to enforce its own gates, approvals, and handoff rules

If context exceeds 65% mid-pipeline, preserve go-mode intent in canonical handoff state so the next fresh session resumes the same mode.
