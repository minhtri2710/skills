# readiness-classification

Role: APPENDIX
Allowed content only: `beo-validate` readiness verdict and execution-set classification procedure.

## Classification order

Evaluate execution readiness in this order:

1. Missing or contradicted requirements -> `FAIL_EXPLORE`.
2. Missing, incomplete, stale, or scope-invalid plan/bead graph -> `FAIL_PLAN`.
3. Missing external authorization, access, secret, or required clarification -> `BLOCK_USER`.
4. Stale, missing, or changed execution approval envelope -> obtain or record the required approval action only through canonical approval doctrine before any pass verdict.
5. No approved ready bead and no approved dependency chain whose first bead is ready -> `FAIL_PLAN` or `BLOCK_USER`, according to the missing evidence.
6. Exactly one approved ready bead with no approved child in the selected dependency chain, current approval, and valid scope proof -> write `execution_mode=single`, `execution_set_id`, and `execution_set_beads` to STATE.json and emit `PASS_EXECUTE`.
7. Multiple approved beads in one explicit dependency chain whose first bead is ready and whose children are blocked only by earlier beads in that same selected chain -> write `execution_mode=ordered_batch`, `execution_set_id`, and `execution_set_beads` in execution sequence order to STATE.json and emit `PASS_EXECUTE`.
8. Multiple approved ready beads with explicit dependency edges in the bead graph, no ambiguous ordering, and no dependency-blocked children -> write `execution_mode=ordered_batch`, `execution_set_id`, and `execution_set_beads` in execution sequence order to STATE.json and emit `PASS_EXECUTE`.
9. Multiple approved ready beads with disjoint write scopes, disjoint generated outputs, no dependency edge, and shared current approval -> write `execution_mode=local_parallel`, `execution_set_id`, and `execution_set_beads` to STATE.json and emit `PASS_EXECUTE`.
10. Multiple ready or dependency-chain candidate beads with unresolved overlap, missing ordering, missing generated-output proof, or ambiguous dependency constraints -> `FAIL_PLAN`.

Do not emit `PASS_EXECUTE` for multiple beads unless the execution set is explicit and every bead is inside the current approval envelope.
