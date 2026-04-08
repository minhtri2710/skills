# State Routing Table

Canonical state routing table lives in `../../reference/references/pipeline-contracts.md`.

Evaluate **top-to-bottom, first match wins**. See that file for the full table, ordering notes, and planning artifact hierarchy.

Quick orientation:
- Explicit user intent short-circuits feature-state routing when it is actionable.
- Most-specific closed states come before generic execution states.
- Current-phase completion is not whole-feature completion when later phases remain.
- Execution resumes only while the `approved` lifecycle is still valid.
