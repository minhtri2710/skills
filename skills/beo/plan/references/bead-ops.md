# Bead Operations

Role: APPENDIX

## Planning bead graph

Every selected bead must record:

- requirement refs
- dependency order
- declared files
- forbidden paths
- generated outputs
- verification
- risk proof or valid N/A
- rollback boundary
- human blockers, if any

Use `[]` or `N/A: <reason>` where appropriate. Missing is not the same as none.

## Dependencies

Dependencies must be satisfied before execution begins.

For `ordered_batch`, beads execute in the validated order. If one bead blocks, stop the batch and route by the proven condition.

## Approval-bearing changes

Changing bead graph, execution order, scope, generated outputs, verification, risk proof, or rollback boundary makes prior approval/readiness stale and requires clearing validation mirrors.
