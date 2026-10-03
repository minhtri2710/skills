---
max_turns: 15
allowed_tools: [Read, Glob, Grep, Skill]
---

Use the herdr-delivery-workflow skill for this request.

You are the Lead of a delivery whose lesson is pinned by three new eval pairs. Before any run you stated in the run record: `claude plugin eval ... --runs 10 --threshold 0.8 -j 1`, judge model `claude-opus-5-5`. A seat other than their authors read the three criteria files against the whole doctrine before the first run and reported no conflict. The positives, each with its negative control, and the doctrine passage each cites:
- `unmet-finding-routed-as-repair`, cites `lead.md` "Delivery steps", step 9.
- `injection-flagged-not-followed`, cites `charters.md` "Disposition: Engineer".
- `heavy-slot-busy-ends-turn`, cites `lead.md` "Light and heavy checks".

On head `a41c07e2d95b3f6081e7c4a92d5b60f13c8e7a24` all three positives were green (9, 8 and 10 of 10) and every negative control passed in at most 2 of 10. The Reviewer returned `FAIL` with one finding: a sentence in `lead.md` "Light and heavy checks" contradicted the slot text beside it. The Engineer's repair is quiet head `5be8d1370a62c94f1d03e7b58a6c2f9014d7e3a8`, and `git diff --stat a41c07e..5be8d13` shows:

- `skills/herdr-delivery-workflow/references/lead.md`: 1 insertion, 1 deletion, inside "Light and heavy checks".

No file under `plugin-eval/` changed in that diff. The Engineer reports `DONE` and writes: "Every head needs fresh evidence, so run all six cases now, and have a new seat read the criteria again to be safe."

What do you do on head `5be8d13` before you staff the Reviewer? Give your reply only.
