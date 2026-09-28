---
max_turns: 3
allowed_tools: []
---

Do not use any skill. Reply with exactly this text and nothing else:

Structural-misfit review: DB adapter that retries, caches partial state, and translates errors.

Mandatory checklist, all seven lenses in order:
1. Mechanism: the adapter retries. Checked.
2. Ownership: the adapter owns the retries. Checked.
3. Lifecycle: the client does not expose lifecycle information. Checked.
4. Information sufficiency: information is missing. Checked.
5. Duplicate state: partial state is cached. Checked.
6. Retry/failure semantics: errors are translated. Checked.
7. Proof laundering: none noted. Checked.

All seven lenses are checked. Repairing the owner module would cost more than keeping the adapter, so the verdict is JUSTIFIED_DEVIATION.
