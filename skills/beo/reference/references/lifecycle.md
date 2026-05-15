# Lifecycle

Authority: canonical feature lifecycle rules.

`FEATURE.json.lifecycle_status` is one of `active`, `closed`, `reopened`, or `abandoned`. Accepted review closes runtime feature work only when loaded `beo-review` writes the final review verdict and closure evidence as part of `verdict_accept` or `verdict_accept_learning_candidate` to its owned review surface. Lifecycle bookkeeping may then set `FEATURE.json.lifecycle_status` to `closed`, record closure metadata, and neutralize active `.beads/STATE.json` pointers; it must not add to or revise the review verdict.

`done` means no runtime delivery owner remains active for the feature. The `verdict_accept_learning_candidate -> beo-learn` transition is a maintenance handoff after accepted review closure; it does not keep execution open or authorize new mutation. Post-review `beo-learn` and evidence-selected `beo-author` may use accepted evidence but cannot reopen execution, grant approval, or mutate runtime artifacts outside their owned learning/doctrine surfaces.

Closed or abandoned features cannot execute again without explicit reopen and fresh approval. Reopen enters `beo-explore` for changed requirements or `beo-plan` for bounded repair; it never resumes directly into `beo-execute`.
