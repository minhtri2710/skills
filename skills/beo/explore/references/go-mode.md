# Go Mode

Use this note only when the user explicitly wants the full beo pipeline while keeping the normal approval gates intact.

Explore still owns only requirement locking. It must not orchestrate downstream phases from this reference.

When go-mode intent is explicit during explore:
- compress requirement gathering only as far as the user allows
- still lock every requirement-level decision before handing off
- preserve any go-mode marker in canonical handoff state so downstream routing can continue the same mode
- rely on downstream skills to enforce their own approvals and handoff rules
