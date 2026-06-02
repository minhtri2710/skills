---
name: beo-author
description: "Maintain BEO control-plane files: skill cards, references, registries, templates, scripts, and ADRs. Use when modifying BEO workflow rules or contracts. No product delivery authority."
---
# beo-author

## Rule ownership

Before changing any BEO rule, identify its canonical owner via `beo-reference -> references/doctrine-map.md`.

Do not duplicate a rule into multiple references. Non-owner files should cite the canonical owner.

When a repeated behavior becomes durable workflow doctrine, update the canonical reference, registry, script, skill card, or AGENTS template. Do not add ad-hoc rules elsewhere.

## Read

- The explicit BEO maintenance request
- The affected BEO file(s)
- Narrow `beo-reference` docs/registries that own the affected rule; start with `beo-reference -> references/doctrine-map.md` when authority is unclear

## Do

1. Confirm the request is BEO control-plane maintenance, not product delivery.
2. Identify the canonical artifact that owns the rule.
3. Edit only affected BEO control-plane files.
4. Keep the four-phase loop simple: plan, validate, execute, review.
5. Run only targeted validation for changed registry, schema, script, or skill-card artifacts when such validation exists; do not invent broad delivery checks.

## Write

- BEO doctrine, registry, schema, template, helper script, skill-card, or ADR changes within scope
- User-review notes when the requested maintenance is ambiguous or risky

## Emit

- `skill_authored_or_updated`
- `reference_or_registry_updated`
- `no_change_needed`
- `user_review_needed`

## Never

- Do not mutate product delivery scope.
- Do not grant `PASS_EXECUTE`.
- Do not execute or review product tickets.
- Do not close Beads delivery issues.
