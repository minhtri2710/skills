---
name: pr-body
description: Write, draft, rewrite, or revise a PR description or PR body (the text of a pull or merge request), covering the shape of the change, what merging puts at risk, and the evidence observed. Use whenever that text is written, including while a delivery workflow opens or updates the request. Do not use for carrying out the act on the forge (posting, opening, changing state, merging), a commit message, or release notes.
---

# PR Body

The description is read by the person deciding whether to merge. The diff shows
the lines, so the body carries what the diff cannot give quickly: the shape of
the change, what merging puts at risk, and what was observed.

Write three parts in the order below: risk comes before evidence because the
evidence is read against it, and Reach before Undo because Reach is what the
evidence has to cover. Fill each part, or mark it as not applying with the
reason in a clause. They are contents, not headings to paste: where the
repository has its own request template, its headings stand and the parts go
inside them. Open on the first part, with no greeting, no restated title, and no
walk through the files; use prose only where a view or a fact needs a sentence.

## 1. The change

Give one view of what differs, a level above the diff: the units the change
touches (a function, a type, a file, a screen, a table) and what each now does
differently, never its lines. Each name the body uses for a thing is the name
the code or the project's glossary gives it.

- Test the view by prediction: a reader of it can say, before opening the diff,
  which units are touched and what to look for in each.
- Test each element by removal: if the prediction survives without it, cut it.
- Show a unit the change creates whole: every element of it that a caller or
  reader meets, none of its lines, each still passing the removal test. Show a
  unit the change alters only where it differs.
- One view is the default; add a second only for a second, separate point.

## 2. The risk of merging

State two facts, not an adjective.

- **Reach**: what else runs this code or reads what it produces. Search for the
  direct callers and consumers and name each with where the search found it.
  Where a trace of farther reach is already in hand (the user ran
  `change-impact-review`, or the delivery produced one), report its result as
  such. Reach nobody traced is written as unchecked, and the user is told that
  `change-impact-review` traces it (the user invokes it; this skill never does).
  Write "nothing else" as the search that was made, with the limit that a search
  with no hit does not show absence.
- **Undo**: whether reverting the merge commit alone restores the earlier state.
  If not, name what it leaves behind: data already rewritten, a message already
  sent, an artefact already published, state held by another system.

## 3. The evidence

For each behaviour the change claims, show one check observed before the change
and again after it, on this change, with the output quoted and cut to the lines
that show the result. For a change that is seen, add a capture before and after
where the harness can take one.

- The before half is the observed output of the check on the earlier code, from
  any run made in the course of this change (a test seen failing before the fix
  counts), taken without changing the working tree the user is in. A before half
  nobody observed is written as not observed, never made by switching the tree.
- Answer part 2: each item under Reach is covered by a check shown here, is
  reported from a trace, or is said to be unchecked.
- When the check cannot run on the earlier code because it exercises something
  the change creates, write the before half as not runnable there, with why.
- A check that was not run is written as not run; call nothing passing from
  expectation.
- The body is published, so redact every secret and private value from quoted
  output and captures before pasting.

The body is done when every part is filled or marked not applying with a reason,
every claim of a result quotes observed output, every Reach item is covered,
traced, or said unchecked, and no secret or private value is in the text.

## Neighbours

- Posting the text, opening the request, changing its state, or merging it:
  `paseo-delivery-workflow` or `agent-delivery-workflow` where the work runs
  under one, otherwise the forge tool in use. Where a workflow turns the body
  into a commit message, its form for the message wins over this skill's.
- Whether the change does what its spec asked: `spec-conformance-review`.
- Reach beyond the direct callers and consumers: `change-impact-review`.
