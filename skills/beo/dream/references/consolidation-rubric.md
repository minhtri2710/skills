# Dream Consolidation Rubric

Classify each candidate as `clear match`, `ambiguous`, `no match`, or `no durable signal`.

## `clear match`

Use only when all are true:
- exactly one existing learning file owns the same durable lesson
- the candidate strengthens or corrects that lesson without expanding domain scope
- no competing target has comparable ownership strength

Action:
- merge or rewrite that one justified target
- keep durable guidance, drop contradicted details
- preserve the existing file format; do not invent new metadata during consolidation

## `ambiguous`

Use when:
- 2 or more files plausibly own the lesson
- the best target cannot be justified confidently
- the lesson overlaps adjacent domains and ownership is unclear

Action:
- show the candidate files and why each is plausible
- offer labeled choices:
  - `merge -> <target file>`
  - `merge -> <target file>`
  - `create new`
  - `skip`
- wait for user choice before writing

## `no match`

Use when the signal is durable but no existing file is a justified owner.

Action:
- do not create new shared guidance unless the dream workflow explicitly calls for it
- keep the candidate out of shared guidance until enough multi-feature evidence exists

## `no durable signal`

Use when the signal is transient, noisy, or not reusable.

Examples:
- temporary command output with no reusable lesson
- one-off failure details with no general prevention rule
- ephemeral environment state unlikely to recur

Action:
- skip the write

## Rewrite Rule

Rewrite only when exactly one owner is clear. If more than one target is plausible, treat it as `ambiguous`.
