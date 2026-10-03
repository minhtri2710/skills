---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in a project whose config has `ci` trigger `pr`. The Engineer's charter lists these checks for the change to invoice rounding: `tests.test_invoice_rounding` and `tests.test_invoice_totals`, `ruff check` on the two changed files, and `git diff --check`. The suite has 4,100 tests and CI runs all of them on the PR. The Engineer messages you: "The change is committed. Before I report, shall I also run the whole suite locally, to be safe? Nothing outside the two modules reads the changed code."

What do you reply to the Engineer? Give your reply only.
