# Route Resolution
<!-- beo:route-resolution -->

Authority: canonical for unsafe owner/feature identity repair resolution and meta-target semantics only. It adds no transition topology; legal `condition_id` -> target pairs remain defined only by `registry/pipeline.json`.

Use route only when owner/feature identity is missing, stale, contradictory, colliding, or unsafe. Normal resume owner orientation lives in `references/resume-resolution.md`. `beo-route` repairs identity metadata only and never repairs requirements, plan, approval, execution evidence, review, learning, setup state, or product files.

If artifacts remain contradictory after identity comparison, stop for user decision.

## Meta-target resolution
<!-- beo:route-resolution:meta-targets -->

`return_to_caller` is legal only when:
- the current transition came from a temporary owner such as `beo-debug`;
- fresh `caller_owner` and `caller_condition_id` exist;
- the metadata matches a legal originating transition in `registry/pipeline.json`;
- current artifact evidence does not contradict returning.

If any condition fails, use `references/resume-resolution.md` for artifact-derived orientation or stop for user decision.

`restored_owner` is a symbolic meta-target condition emitted only after identity metadata is repaired. It is not a concrete owner and never means "the owner written in STATE". After repair, concrete target selection comes from `references/resume-resolution.md` and must resolve to a runtime owner, terminal `done`, or `user` before the next owner acts.

`return_to_caller` and `restored_owner` do not grant owner authority by themselves. The concrete next owner must still load its `SKILL.md`, common contract, and current artifacts.

## Operator output
<!-- beo:route-resolution:operator-output -->

When repairing identity, report:

```text
Artifacts prove: <artifact evidence and repaired identity basis>
Mirror said: <STATE/HANDOFF owner identity, if present>
Action: repair identity metadata only | user decision needed
Restored target: <symbolic restored_owner | user>
Concrete orientation source: references/resume-resolution.md
Target class: <meta | terminal>
Next read: <resume-resolution.md | canonical reference | none for user>
```

If operator output names a later concrete owner, label it as resume orientation from `references/resume-resolution.md`, not route authority.
