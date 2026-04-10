# Gray-Area Probes

## Contents

- [SEE (UI / Display)](#see-ui--display)
- [CALL (API / Service)](#call-api--service)
- [RUN (CLI / Pipeline)](#run-cli--pipeline)
- [READ (Docs / Content)](#read-docs--content)
- [ORGANIZE (Config / Structure)](#organize-config--structure)
- [Cross-Cutting](#cross-cutting)

Select the feature domain first, then use the matching probe set.
Skip categories that do not apply.

## SEE (UI / Display)

- What should the user see before the feature has any data?
- What should the user see when the feature succeeds?
- What should the user see when it fails?
- Which states must be visually distinct from each other?
- What information must be visible without interaction?
- What information can stay hidden until interaction?
- How dense should the layout feel?
- What interaction starts the feature flow?
- What interaction ends or dismisses it?
- What should happen on slow loading?
- What should happen on empty results?
- What should happen on partial results?
- What needs to be available on mobile as well as desktop?
- Are there permission-based visibility differences?
- Are there accessibility or keyboard expectations that change behavior?
- What is explicitly out of scope for this UI change?

## CALL (API / Service)

- What is the exact caller-visible contract?
- Who is allowed to call it?
- What authentication is required?
- What authorization rules change behavior?
- What inputs are required?
- What inputs are optional?
- What happens on invalid input?
- What happens on duplicate requests?
- What happens on upstream failure?
- What happens on timeout?
- What happens when the resource does not exist?
- What happens when the caller lacks permission?
- Is the operation synchronous or asynchronous from the caller's perspective?
- Does the response shape differ across success modes?
- What should be logged, if anything?
- What behavior must remain backward-compatible?

## RUN (CLI / Pipeline)

- How is the command or job invoked?
- What inputs or flags are required?
- What outputs are required?
- What should be printed to stdout versus stderr?
- What exit codes matter?
- What counts as a retryable failure?
- What counts as a permanent failure?
- What happens on partial progress?
- Should the run be resumable?
- What should happen when dependencies are missing?
- What behavior is expected in non-interactive environments?
- What should be logged or reported at the end?
- Are dry-run or preview modes required?
- What should happen when the command is run twice?
- What timing or performance constraints matter?
- What is explicitly out of scope for this run mode?

## READ (Docs / Content)

- Who is the reader?
- What should the reader understand by the end?
- What level of detail is required?
- What tone should the content use?
- What structure makes the content easy to navigate?
- What prerequisites should be assumed versus explained?
- What examples are required?
- What failure or edge cases must be documented?
- What should be linked instead of repeated?
- What content must stay concise?
- What content must be exhaustive?
- What is intentionally not covered here?

## ORGANIZE (Config / Structure)

- What grouping principle should drive the structure?
- What naming convention should apply?
- What existing structure should be preserved?
- What duplication is acceptable versus not acceptable?
- What migration path is required?
- What breaks if names or locations change?
- Which consumers depend on the current structure?
- What must remain easy to discover?
- What must remain easy to edit?
- What needs a compatibility shim, if any?
- What should happen to deprecated entries?
- What are the failure modes if organization is wrong?
- What belongs together?
- What must stay separate?
- What edge cases affect classification or placement?
- What is explicitly out of scope for this reorganization?

## Cross-Cutting

- What is the real scope boundary?
- Which earlier decisions already constrain this work?
- Which downstream skill or consumer depends most on a clean answer here?
- What would materially change the plan if answered differently?
- What can safely remain open until planning?
