# Bead Readiness Prompt v2

Role: APPENDIX

For each candidate bead, check:

1. Requirement refs are present and locked.
2. Dependencies are explicit and satisfied.
3. Declared files are present.
4. Forbidden paths are explicit.
5. Generated outputs are explicit.
6. Verification is direct and runnable or has valid N/A.
7. Risk proof or mitigation is present or valid N/A.
8. Rollback boundary is explicit.
9. Human blockers are absent or classified as `BLOCK_USER`.
10. Current approval covers the bead, execution mode, and execution set.
11. Scope overlap is safe for the selected sequential order.

Return the smallest repair owner: `beo-plan`, `beo-explore`, `user`, or `beo-route` for owner-state defects.
