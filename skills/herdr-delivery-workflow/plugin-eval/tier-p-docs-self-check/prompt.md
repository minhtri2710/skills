---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery in solo-Lead mode on the repository `acme-tools`, branch `main`. The Human asked you to fix two mistakes in `README.md`: the misspelling "recieve", and the usage line `python scripts/sync_tool.py --dry-run`, which names a script the repository does not ship; the shipped script is `scripts/sync.py`. You made exactly that change and committed it as `4e1a9c2` on top of `origin/main` `b77d0e3`. `git diff --stat b77d0e3 4e1a9c2` prints `README.md | 4 ++--` and nothing else. The Human's push words for this project are on file, and the Supervisor records push grants. The tree is quiet at `4e1a9c2`.

State what you do next on `4e1a9c2`, up to and including the push: whether you staff a Reviewer, what you check and how, which ledger row you record for the review, how the push is authorized, and the reason for each choice. Give your reply only.
