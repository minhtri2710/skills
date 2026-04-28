Non-normative asset.

# skill-writing-method

Role: ASSET
Allowed content only: skill authoring method, manual pressure scenarios, wording guidance; no checker, fixture, release, routing, or topology rules.

## Method

Use this file only as supporting material when authoring beo skill contracts.

## Cycle

1. Define the skill behavior.
2. Identify failure modes without the skill.
3. Write 3-5 manual pressure scenarios.
4. Start with the baseline pressure set: happy path, owner collision, stale approval/handoff, forbidden-surface temptation, debug return/rollback, and user-clarification vs go-mode.
5. Add scenario coverage for any new human-readable mirror, scout helper, dependency gate, or worker-report protocol you introduce.
6. Write the smallest SKILL.md that blocks observed failure modes.
7. Remove hypothetical content not tied to observed pressure.
8. Re-read the contract for overlap with existing skills.
9. Keep references non-normative unless they are canonical shared references.

## Skill contract checklist

- Frontmatter name matches the skill directory.
- Description states trigger conditions, not workflow summary.
- Purpose is one sentence.
- Primary owned decision is exactly one decision.
- Ownership test has one predicate group.
- Writable surfaces are explicit.
- Forbidden surfaces block neighboring skills.
- Allowed next owners are explicit.
- References are pointers, not hidden routing logic.

## Pressure scenario shape

```text
Scenario:
Pressure:
Expected wrong behavior without skill:
Observed or likely rationalization:
Required wording change:
```

## Recommended baseline scenarios

- Happy path: contract should route and exit cleanly without extra doctrine.
- Owner collision: neighboring owner should be disqualified for a stated reason.
- Stale approval/handoff: stale control surface must not be followed silently.
- Forbidden-surface temptation: contract must block the most likely out-of-scope edit.
- Debug return/rollback: temporary diagnosis must not steal permanent ownership.
- User clarification vs go-mode: non-blocking authorization must not become approval bypass.

## Must not

- Add checker scripts.
- Add route fixtures.
- Add release gates.
- Add topology validation.
- Hide owner-selection logic in local references.
