# Glossary

| Term | Meaning |
| --- | --- |
| bead | smallest execution unit in the current phase |
| current phase | the phase currently being planned, validated, or executed |
| execution envelope | approved bead set + approved scope + forbidden paths + verification contract + mode |
| approved scope | the exact file scope and generated-output scope covered by the current approval record |
| execution approval | readiness and scope grant written by `beo-validate` |
| user authorization | user or policy permission that is distinct from execution approval |
| approval refresh | freshness-only renewal when the execution envelope is unchanged |
| new approval grant | a new approval required when bead set, mode, approved scope, or verification contract changes |
| worker | execution delegate in swarm, not a route owner |
| handoff | real checkpoint or resume surface, not every same-session transition |
