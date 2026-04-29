---
name: beo-validate
description: |
  Decide execution readiness and serial/swarm mode. Use when artifacts need no content edits but approval, readiness, remediation class, or mode is absent or invalid. Do not use when artifact content edits or execution are required.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: unavailable
      reason: Required to prove bead graph readiness and approved execution units.
    - id: agent-mail
      kind: mcp_server
      server_names: [mcp_agent_mail]
      config_sources: [repo_config, global_config]
      missing_effect: unavailable_for_swarm
      reason: Required before PASS_SWARM can be emitted.
---
# beo-validate

## Purpose
Decide execution readiness and serial/swarm mode.

## Primary owned decision
Emit exactly one readiness verdict: `PASS_SERIAL`, `PASS_SWARM`, `FAIL_EXPLORE`, `FAIL_PLAN`, or `BLOCK_USER`, from existing artifacts without editing their content.

## Ownership predicate
- Requirements, plan, approval, bead readiness, remediation class, or execution mode needs classification.
- Artifacts appear content-complete and need readiness verification rather than edits.
- Swarm eligibility or Agent Mail availability must be checked live before parallel dispatch.
- No artifact content edit or implementation is required.

## Dependencies
Machine-readable dependency posture lives in frontmatter. When `agent-mail` is unavailable, this owner cannot emit `PASS_SWARM`.

## Writable surfaces
- Readiness, approval reference, and execution-mode fields in shared state surfaces.
- Bead readiness/status fields only as allowed by canonical bead/status mapping.
- Shared `STATE/HANDOFF` surfaces under the common contract baseline.

> Canonical: `beo-reference -> artifacts.md`
> Locally enforced as:
> - Check `Forbidden paths` and `Swarm eligibility` in the canonical bead schema.
> - Do not redefine bead fields locally.
> - Return content repair to the owning artifact writer.

> Canonical: `beo-reference -> pipeline.md` and `beo-reference -> approval.md`
> Locally enforced as:
> - Route content repair to artifact owners.
> - Grant or refresh approval only through canonical approval doctrine.
> - Emit `BLOCK_USER` when required external authorization, access, secret, or clarification is missing.

## Hard stops
- Do not edit `CONTEXT.md`, `PLAN.md`, or implementation files.
- Do not emit `PASS_SWARM` from cached onboarding posture.
- Do not bypass current approval checks.

## Allowed next owners
- `beo-execute`
- `beo-swarm`
- `beo-plan`
- `beo-explore`
- `user`
- `beo-route` — only when owner state is missing, stale, contradictory, or colliding.

## References
- `beo-reference -> approval.md` — read when checking approval freshness, invalidation, or execution envelope rules.
- `beo-reference -> artifacts.md` — read when checking artifact and bead schemas.
- `beo-reference -> complexity.md` — read when validating required planning-depth sections.
- `beo-reference -> coordination.md` — read when checking Agent Mail and swarm coordination preconditions.
- `beo-reference -> status-mapping.md` — read when mapping readiness to bead labels/statuses.
- `references/readiness-review-prompt.md` — read when running a non-normative readiness review.
- `references/bead-readiness-prompt.md` — read when checking bead-level readiness prompts.
