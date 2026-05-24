---
name: beo-author
description: Maintain and edit BEO control-plane doctrine, registries, templates, scripts, or skill contracts. Always use this skill when the user asks to modify workflow rules, update command contracts, write ADRs, or edit BEO SKILL.md files. Trigger this when the user says "change the BEO rules", "update the pipeline", or "edit this skill card."
---
# beo-author

## Use when

The user or an authorized learning handoff asks to change BEO control-plane material rather than deliver a product ticket.

## Read

- The explicit maintenance request, claimed maintenance bead, or `authoring_requested` payload.
- Relevant current BEO doctrine, registry, template, skill contract, and script contract metadata; inspect script implementation only when the authorized maintenance request is specifically a script change.
- `beo-reference` canonical contracts: `references/kernel.md`, `references/doctrine-map.md`, `registry/command-contracts.json`, and any registry/schema directly affected.
- Existing ADRs when the change encodes a hard-to-reverse trade-off.

## Do

1. Confirm authorization and distinguish maintenance from product delivery.
2. Identify the canonical artifact that owns the rule before editing generated or explanatory material.
3. Update only the affected BEO control-plane files needed to keep contracts consistent.
4. Preserve kernel invariants and record ADRs only for real, hard-to-reverse trade-offs.
5. Validate registries or scripts by running the appropriate commands; do not read large scripts as doctrine.

## Write

- BEO doctrine, registry, schema, template, script, or skill contract changes within the approved maintenance scope.
- ADRs when the decision meets ADR criteria.
- User-review notes when the requested change is ambiguous or risky.

## Emit

- `skill_authored_or_updated` -> stop.
- `reference_or_registry_updated` -> stop.
- `no_change_needed` -> stop.
- `user_review_needed` -> stop for user decision.

## Never

- Do not mutate product delivery scope.
- Do not grant `PASS_EXECUTE`, execute tickets, review delivery, or close issues.
- Do not create new doctrine files without deleting, generating, replacing, or justifying the old source.
- Do not treat helper script implementation text as canonical policy when a registry or doctrine contract exists.
- Do not load BEO delivery skills to continue implementation after an authoring emit; stop first.
