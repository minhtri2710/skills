Non-normative asset.

# skill-writing-method

Role: APPENDIX
Allowed content only: skill authoring method and wording guidance for selected learning cases
Forbidden content: external quality-process requirements, routing topology, approval authority, review verdict authority, runtime execution rules

## Purpose

Use this file only when `beo-author` is already active.

It helps turn a selected learning case or explicit user request into a small skill update or a new BEO skill.

## Method

1. Identify the selected source:
   - explicit user request; or
   - finalized learning case; or
   - consolidated learning pattern.

2. Identify the affected surface:
   - existing owner `SKILL.md`;
   - owner-local reference;
   - canonical shared reference;
   - new skill.

3. Prefer the smallest change that prevents the observed false case.

4. Harden an existing skill before creating a new skill when possible.

5. Do not add runtime ceremony unless the false case cannot be blocked otherwise.

6. Do not add shared doctrine until the canonical home is identified.

7. Do not duplicate multi-step shared logic across owners.

8. Do not write product implementation, approval, execution, review verdicts, or route decisions.

9. Keep output focused on the selected case/request.

## Case-to-skill checklist

- What happened?
- What should have happened?
- Which owner or reference failed to block the false case?
- Is this a wording issue, ownership issue, missing hard stop, or missing skill?
- Can an existing skill be hardened instead of creating a new one?
- What is the smallest safe edit?
- Does the edit add runtime ceremony? If yes, why is it unavoidable?
- Which canonical home owns any shared rule?
- What should remain out of scope?

## Author output reminder

```md
Decision:
Source request or case:
Canonical home:
Surfaces changed:
Why this blocks the false case or satisfies the request:
Doctrine duplicated? no
Runtime ceremony added? no/yes with reason
Next owner:
```

## Must not

- Add checker scripts.
- Add fixtures.
- Add external quality-process gates.
- Hide owner-selection logic in local references.
- Create broad doctrine from one vague case.
