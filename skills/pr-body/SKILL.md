---
name: pr-body
description: Write, draft, rewrite, or revise the text of a pull or merge request's description, covering the shape of the change, what merging puts at risk, and the evidence observed. Use when that text is the deliverable. Do not use for the act on the forge (posting the text, opening the request, changing its state, merging it), a commit message, or release notes.
---

# PR Body

The description is read by the person deciding whether to merge. The diff shows
the lines, so the body carries what the diff cannot give quickly: the shape of
the change, what merging puts at risk, and what was observed. This skill owns
that content and nothing that happens on the forge.

Write three parts in the order below. Fill each, or mark it as not applying with
the reason in a clause. They are contents, not headings to paste: where the
repository has its own request template, its headings stand and the parts go
inside them. Open on the first part, with no greeting, no restated title, and no
walk through the files; use prose only where a view or a fact needs a sentence.

## 1. The change

Give one view of what differs, a level above the diff: the units the change
touches (a function, a type, a file, a screen, a table) and what each now does
differently, never its lines. Use the project's own terms, from its glossary
where it has one.

- Test the view by prediction: a reader of it can say, before opening the diff,
  which units are touched and what to look for in each.
- Test each element by removal: if the prediction survives without it, cut it.
- Show a unit the change creates whole, and one it alters only where it differs.
- One view is the default; add a second only for a second, separate point.

## 2. The risk of merging

State two facts, not an adjective.

- **Reach**: what else runs this code or reads what it produces. Search for the
  direct callers and consumers and name each with where the search found it.
  Reach beyond them is not traced here: write it as unchecked, and tell the user
  that `change-impact-review` traces it (the user invokes it; this skill never
  does). Write "nothing else" as the search that was made, with the limit that a
  search with no hit does not show absence.
- **Undo**: whether reverting the merge commit alone restores the earlier state.
  If not, name what it leaves behind: data already rewritten, a message already
  sent, an artefact already published, state held by another system.

## 3. The evidence

For each behaviour the change claims, run one check before the change and again
after it, on this change, and quote the output cut to the lines that show the
result. For a change that is seen, add a capture before and after where the
harness can take one.

- Answer part 2: each item under Reach is covered by a check shown here or is
  said to be unchecked.
- When the check cannot run on the earlier code because it exercises something
  the change creates, write the before half as not runnable there, with why.
- A check that was not run is written as not run; call nothing passing from
  expectation.
- The body is published, so redact every secret and private value from quoted
  output and captures before pasting.

Risk comes before evidence because the evidence is read against it, and Reach
before Undo because Reach is what the evidence has to cover. The body is done
when every part is filled or marked not applying with a reason, every claim of a
result quotes observed output, every Reach item is covered or said unchecked,
and no secret or private value is in the text.

## Neighbours

- Posting the text, opening the request, changing its state, or merging it:
  `paseo-delivery-workflow` or `agent-delivery-workflow` where the work runs
  under one, otherwise the forge tool in use. Where a workflow turns the body
  into a commit message, its form for the message wins over this skill's.
- Whether the change does what its spec asked: `spec-conformance-review`.
- Reach beyond the direct callers and consumers: `change-impact-review`.
