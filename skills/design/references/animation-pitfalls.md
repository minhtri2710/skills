# Animation Pitfalls

This file is for common failure modes and fixes.

Read this before complex motion work.

## Common Failures

- every element moves at once
- movement has no narrative reason
- timing is uniform instead of staged
- screen furniture competes with the story
- browser-style chrome is drawn inside the frame when it should stay outside
- motion relies on layout-thrashing properties
- final frames are unstable for export

## Guardrails

- animate hierarchy, not everything
- keep one focal event per beat
- use transforms and opacity first
- design a still frame that is worth pausing on
- keep controls and scrubber UI out of the narrative frame and mark export-only chrome with `[data-role="chrome"]`, `[data-record="hidden"]`, or `.no-record`
- do not fake a product with silhouettes when real assets exist

## Export Safety

Before export, confirm:

- the scene starts cleanly
- the scene reaches a readable end state
- the loop behavior matches the intended export
