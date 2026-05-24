---
name: beo-reference
description: Perform read-only lookup of BEO doctrine, registries, templates, and contracts. Always use this skill when answering conceptual, safety, or authority questions. Trigger this whenever the user or another skill asks "what are the kernel invariants?", "what is the pipeline transition for X?", or "show me the safety rules."
---
# beo-reference

## Use when

A user or BEO owner needs canonical BEO guidance, registry lookup, or command-contract interpretation without mutation.

## Read

- `references/doctrine-map.md` to route the lookup.
- `references/kernel.md` when the question involves authority, safety, lifecycle, or invariants.
- The narrow reference, registry, template, or command contract needed to answer the question.
- No broad reference set unless the user asks for a cross-doctrine audit.

## Do

1. Identify the canonical artifact for the question.
2. Prefer registry files for machine-enforced workflow, command, schema, profile, and pipeline facts.
3. Prefer doctrine references for human-readable invariants and operating principles.
4. Cite file paths and section names or line ranges clearly.
5. Say when a lookup is advisory rather than approval-bearing.

## Write

- Nothing. This is a read-only lookup skill.

## Emit

- No delivery transition. Return the cited answer and stop.

## Never

- Do not mutate product files, BEO artifacts, registries, doctrine, memory, or Beads lifecycle.
- Do not grant `PASS_EXECUTE`, review verdicts, Human Gate resolution, or closure.
- Do not run setup, qmd indexing, Obsidian writes, or delivery commands.
- Do not load a BEO delivery owner to continue the task unless the user explicitly asks to move from lookup into delivery.
