# Gray-Area Probes

Select the feature domain first, then use the matching probe set. Skip categories that do not apply.

## SEE (UI / Display)

- What should the user see before the feature has any data?
- What should the user see on success? On failure?
- Which states must be visually distinct?
- What is visible without interaction vs hidden until interaction?
- How dense should the layout feel?
- What interaction starts/ends the flow?
- What happens on slow loading, empty results, partial results?
- Mobile as well as desktop requirements?
- Permission-based visibility differences?
- Accessibility or keyboard expectations?
- Does this feature change how navigation, routing, or import primitives work? Which existing components currently import the affected modules (e.g. `next/link`, `next/navigation`, router hooks) and will need updating?
- What is explicitly out of scope?

## CALL (API / Service)

- Exact caller-visible contract?
- Who is allowed to call it? Authentication required?
- Authorization rules that change behavior?
- Required vs optional inputs?
- Behavior on: invalid input, duplicate requests, upstream failure, timeout, resource not found, insufficient permission?
- Synchronous or asynchronous from caller's perspective?
- Does response shape differ across success modes?
- What should be logged?
- What must remain backward-compatible?

## RUN (CLI / Pipeline)

- How is the command/job invoked? Required inputs/flags?
- Required outputs? Stdout vs stderr separation?
- Exit codes that matter?
- Retryable vs permanent failure?
- Behavior on partial progress? Resumable?
- Behavior when dependencies missing?
- Non-interactive environment expectations?
- What should be logged/reported at end?
- Dry-run or preview modes required?
- Behavior when run twice?
- Timing/performance constraints?
- What is explicitly out of scope?

## READ (Docs / Content)

- Who is the reader? What should they understand by the end?
- Detail level required? Tone?
- Navigation structure?
- Prerequisites: assumed vs explained?
- Required examples?
- Failure/edge cases to document?
- What to link vs repeat?
- What must stay concise vs exhaustive?
- What is intentionally not covered?

## ORGANIZE (Config / Structure)

- Grouping principle for the structure?
- Naming convention?
- Existing structure to preserve?
- Acceptable vs unacceptable duplication?
- Migration path required?
- What breaks if names/locations change?
- Consumers depending on current structure?
- What must remain easy to discover? To edit?
- Compatibility shims needed?
- Deprecated entry handling?
- Failure modes if organization is wrong?
- What belongs together vs must stay separate?
- Edge cases affecting classification/placement?
- What is explicitly out of scope?

## Cross-Cutting

- Real scope boundary?
- Earlier decisions constraining this work?
- Downstream skill/consumer most dependent on a clean answer?
- What would materially change the plan if answered differently?
- What can safely remain open until planning?
