---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill, Bash]
---

Use the herdr-delivery-workflow skill for this request.

You are the Supervisor, reasoning out-of-Herdr. Reading a Lead's Engineer charter, you see it names the owned paths `src/billing/invoice.py` and `tests/billing/test_invoice.py` and requires `def render_invoice(order: Order) -> InvoiceDoc`. That signature was pinned by the previous slice, which passed independent review and is committed on the branch; other scopes already call it. The charter says: "How `render_invoice` assembles line items and taxes is open; judge it from the code and report." Do you record pre-solving in the notebook and send the Lead an observation? Explain.
