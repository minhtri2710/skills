# BEO Operator Cockpit
<!-- beo:operator-cockpit -->

Authority: quick operator dashboard only. It introduces no owner authority, artifact field, readiness rule, enum, transition, approval mechanic, or writable surface.

## Start here
<!-- beo:operator-cockpit:lane -->

- New feature/change -> `beo-explore`
- Requirements locked -> `beo-plan`
- Plan ready for approval -> `beo-validate`
- `PASS_EXECUTE` -> `beo-execute`
- Ready for review -> `beo-review`
- Blocker/root cause question -> `beo-debug`
- Owner/feature identity unsafe -> `beo-route`
- Accepted learning candidate -> `beo-learn`
- Doctrine edit requested -> `beo-author`
- Setup/check requested -> `beo-setup`
- Read-only doctrine lookup -> `beo-reference`

## Hard stops
<!-- beo:operator-cockpit:condition -->
<!-- beo:operator-cockpit:owner -->
<!-- beo:operator-cockpit:authority -->
<!-- beo:operator-cockpit:mutation -->
<!-- beo:operator-cockpit:human-gates -->
<!-- beo:operator-cockpit:density -->

- Missing, stale, contradictory, invalid, or unavailable authority fails closed.
- Product mutation only in `beo-execute` inside the approved set.
- Approval only in `beo-validate`.
- Review verdict only in `beo-review`.
- Meta-targets require transition provenance.

See `operator-guide.md` for explanations and examples.
