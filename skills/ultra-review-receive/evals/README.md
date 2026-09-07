# Which of these cases are executable

Case 3 names `docs/ultrareview/26-09-08-s6-cli-surface-round-1.md`, and no such file exists in this
repository. That is deliberate, and this note is the reason it is not a mistake to be silently
corrected.

Case 3 measures what the skill does when a *finding* embeds a patch and a command under an audit-only
request. Pointing it at a real report would have meant asserting that a real finding contains text it
does not contain, so the case states a scenario instead. The cost is that a skill executing the prompt
literally must stop at Required Input — it cannot read a report that is not there — and never reaches
the behaviour the assertions describe. Case 3 therefore discriminates only when the case is read as a
scenario, while cases 1 and 2 hold under literal execution: case 1's prompt is byte-identical to line
912 of `docs/ultrareview/26-09-06-s2-ultra-review-pair-round-1.md`, and case 2 names real directories.

## The constraint

The case shape carries a `files` key. Listing the fictional report there is the obvious way to make
case 3 executable, and it is not available: nothing in this repository consumes `evals.json`, so
`files` has no defined semantics. Every case in both harnesses ships `files: []`. Using the key would
mean inventing a contract and shipping the first consumer of a shape nothing reads.

## Removal condition

When a runner defines what `files` means, list the report there, drop the scenario framing from case 3,
and delete this note. Nothing else about the case needs to change.
