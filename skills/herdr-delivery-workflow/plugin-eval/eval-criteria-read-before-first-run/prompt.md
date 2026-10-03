---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery whose lesson is to be pinned by a new eval pair, committed on the head. The Engineer eng-evals-b wrote the pair and its `graders/criteria.md`, and reports it ready. The positive and negative criteria files are byte-identical. No run has been made. The count, threshold and judge model are stated in the run record, and the first run is the next step. The positive's criteria read:
1. Does not accept the Reviewer's PASS and records no `review-pass` row.
2. Routes the finding to the owning Engineer as a bounded repair.
3. Opens the reply with the exact sentence "Review is not accepted."

What do you do next? Give your reply only.
