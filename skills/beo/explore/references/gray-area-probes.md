Non-normative asset.

# gray-area-probes

Role: APPENDIX
Allowed content only: probe axes and question prompts
Forbidden content: owner selection, approval authority, review verdict authority, routing topology, writable-surface expansion

## Acceptance probes

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
- Does this feature change how navigation, routing, or import primitives work? Which existing components currently import the affected modules (for example, `next/link`, `next/navigation`, router hooks) and will need updating?
- What is explicitly out of scope?

- What observable behavior proves this is done?
- What inputs, outputs, UI states, or commands define success?
- What failure mode should no longer occur?
- What acceptance evidence should review expect?

## Non-goal probes

- What tempting adjacent work should not be included?
- What refactor, data-change, redesign, or cleanup is explicitly out of scope?
- What existing behavior should remain intentionally imperfect for now?

## Existing user/data support probes

- Must existing users, configs, data, clients, or rollout phases keep working?
- Would this change break current public behavior, saved data, configs, URLs, APIs, or user expectations?
- Is preserving existing behavior required for this feature?

## Constraint probes

- Are there performance, security, privacy, latency, cost, dependency, platform, or accessibility constraints?
- Are network, storage, database, or third-party service changes allowed?
- Are dependency or lockfile changes allowed?

## Scope-risk probes

- Could this touch auth, billing, permissions, schema changes, data deletion, secrets, or privacy surfaces?
- Could this require multi-phase delivery?
- Could this create generated files, snapshots, schema outputs, or lockfile changes?
- Could parallel work conflict with the same files or public interfaces?

## Clarification triage probes

- Would the answer change acceptance criteria?
- Would the answer change file scope or approval scope?
- Would the answer change existing user/data support or security/privacy constraints?
- If not, can it be recorded as a non-blocking assumption under `go_mode`?

## Intake boundary probes

Use these when deciding whether user intent constitutes explicit intake evidence before beginning requirements locking:

- Does the user's instruction name a specific feature, task, ticket, or scope area?
- Is the scope specific enough that acceptance criteria could be drafted from it?
- Has the user confirmed they want to start a new feature (vs. continue existing work)?
- Is there an existing CONTEXT.md that could be the intended target?
- Would proceeding without clarification risk locking the wrong requirements?

If any of these is uncertain, ask one scoped clarifying question before creating a feature slug.
