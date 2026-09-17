---
name: agent-doc-writing
description: Write or prune a document an agent consumes — a skill, AGENTS.md, CLAUDE.md, or a doctrine or reference file reached by a pointer. Use when creating, editing, reviewing, or trimming such a document. Do not use for human-facing README or product documentation, or to run evals and benchmarks on a skill; that is skill-creator.
---

# Agent Doc Writing

An agent document makes the agent take the same process on every run. Its wording
decides when material is reached, what the agent does, and when it thinks it is
done.

## Pointers

A context pointer is an in-context line that names out-of-context material and the
condition for reaching it: a skill description, or an `AGENTS.md` line naming a doc.
The wording, not the target, decides how reliably the material is reached; sharpen
a weak pointer before inlining its target.

- Lead with the word that does the triggering.
- Give one trigger per distinct branch; synonyms for one branch are one trigger.
- Leave out identity the body already carries.
- Every always-loaded word costs on every turn, so prune pointers harder than
  bodies.

## Placement

Order content by how immediately the agent needs it: in-file steps, then in-file
reference, then disclosed reference behind a pointer. Inline what every branch
needs; disclose what only some branches reach. Keep a concept's definition, rules,
and caveats under one heading. A document too long even when every line is live
thins attention; cure it by disclosing and by splitting per branch. Point one
level deep, from the skill straight to the file, never through an intermediate
document. A bundled script costs no context when it runs, only its output does,
so prefer a script to an inline code block that is paid for on every load.

A model-invoked skill pays permanent context load for its description; a
user-invoked skill (`disable-model-invocation: true`) pays none but relies on the
human remembering it. Choose model invocation only when the agent or another skill
must reach it unprompted.

## Steps end on completion criteria

Every step ends on a condition the agent can check. A vague bound ("once understood")
invites ending early, pulled by the steps still ahead. Sharpen the bound first;
hide later steps behind a real context boundary (a handoff or subagent) only when
the bound stays fuzzy and rushing is observed. Demanding criteria ("every modified
caller accounted for") drive thorough work; the strongest are checkable and
exhaustive.

## Leading words

A leading word is a compact concept the model already knows (tight loop, tracer
bullet, frontier) that anchors a whole behavior. Reuse it as a token throughout
instead of re-explaining the idea; collapse a repeated triad or a sentence
gesturing at one idea into one word. Prefer an existing word to a coined one, which
costs definition tokens.

State the target behavior positively. A prohibition makes the prohibited behavior
more available; keep one only as a hard guardrail, paired with the positive target.

## Pruning

- One meaning lives in one place; other places cite it.
- The environment is a source of truth. Leave one-command lookups (scripts,
  config, `--help`) to the environment and record only what looking cannot find:
  unwritten conventions, reasons, gotchas.
- Test each sentence against the default: if the model already behaves that way
  without it, delete the whole sentence. The test is model-relative and settled by
  running the document, not by debate. A leading word too weak to move the default
  gets a stronger word.
- Remove lines that went stale or never bore on the task; stale layers settle
  because adding feels safe and removing feels risky.
