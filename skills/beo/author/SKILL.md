---
name: beo-author
description: |
  Use this skill to author or harden beo skill contracts and doctrine text. Use when creating, rewriting, simplifying, deduping, normalizing, reviewing, or manually pressure-reviewing beo skill definitions or skill-local writing guidance. Do not use when runtime delivery, checker scripts, fixture suites, release gates, governance validation, topology changes, automated evals, benchmarks, or product implementation is requested.
---

# beo-author

## Purpose

Author or harden beo skill contracts and doctrine text.

## Fast predicate

Active when creating, rewriting, simplifying, deduping, normalizing, reviewing, or manually pressure-reviewing beo skill definitions or skill-local writing guidance.

Not active when runtime delivery, checker scripts, fixture suites, release gates, governance validation, topology changes, automated evals, benchmarks, or product implementation is requested.

## Primary owned decision

Produce skill-contract or doctrine text that preserves owner boundaries and canonical homes.

## Writable surfaces

`<skill_name>/SKILL.md`; `<skill_name> -> references/xxx` skill-local writing assets; `beo-reference -> references/xxx` when explicitly editing shared doctrine; HANDOFF.json only when pausing/transferring.

## Hard stops

Do not perform runtime owner mutations unless that owner skill is loaded. Do not add eval/checker/benchmark/release-gate requirements. Do not duplicate canonical doctrine into owner files beyond local hard stops. Do not hide writable surfaces in references.

## Allowed next owners

done, user

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
