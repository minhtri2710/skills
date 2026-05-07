# Readiness Classification v2

Role: APPENDIX

Evaluate execution readiness in this order:

1. Requirements missing, unlocked, or contradicted -> `FAIL_EXPLORE`.
2. Plan, bead graph, declared files, forbidden paths, generated outputs, verification, risk proof, or rollback boundary missing/stale/invalid -> `FAIL_PLAN`.
3. Human approval/access/secret/legal/business/UAT blocker exists -> `BLOCK_USER`.
4. Owner-state contradiction or unreadable canonical state prevents safe classification -> `FAIL_STATE`.
5. Exactly one approved ready bead with fresh approval -> write `execution_mode=single`, `execution_set_id`, and `execution_set_beads` to `STATE.json` and emit `PASS_EXECUTE`.
6. Multiple approved ready beads with explicit dependency order and all dependencies satisfied -> write `execution_mode=ordered_batch`, `execution_set_id`, and `execution_set_beads` to `STATE.json` and emit `PASS_EXECUTE`.

Do not select unsupported execution modes. Do not allow continuation after a blocked bead in an ordered batch.
