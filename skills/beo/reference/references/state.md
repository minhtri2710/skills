# BEO State

## STATE-01 — STATE is display/orientation only

`STATE.json` is orientation and display state. It never grants approval, selects execution sets, emits verdicts, overrides current required surfaces, or substitutes for an active owner contract.

Runtime authority remains with:

- active owner contract
- current required surfaces (ART-01)
- tool-verified approval/integrity status (INT-03)

`STATE.json` and `HANDOFF.json` are non-authoritative mirrors/context; current required surfaces and active owner contract win.

## STATE-02 — One active feature

BEO manages one active feature at a time. If multiple active feature candidates exist and canonical evidence cannot select one, route to `user`. Do not infer feature identity from branch, worktree, recent files, or status scouts.

## Lightweight shape

```json
{
  "active_feature": "example_feature",
  "lane": "beo_tiny | standard",
  "current_owner": "beo-plan",
  "status": "active | blocked | done",
  "artifact_shape": "ticket | standard",
  "canonical_artifacts": {
    "ticket": "TICKET.md",
    "context": "CONTEXT.md",
    "plan": "PLAN.md",
    "tracker": "TRACKER.json",
    "review": "REVIEW.md"
  },
  "br_enabled": true,
  "mirrors": {
    "readiness": "display-only",
    "approval_ref": "display-only",
    "execution_set_id": "display-only"
  },
  "next_owner": null,
  "reason": ""
}
```

Display fields such as `feature_slug`, `current_phase`, `readiness`, `approval_ref`, `execution_mode`, `execution_set_id`, and `execution_set_beads` may exist as mirrors. They are not execution authority.

## Handoff

`HANDOFF.json` is resume context for pause or transfer. It never grants approval, verdict, integrity, route authority, or product mutation authority.

A handoff is usable only when fresh, from/to owners are legal, and its reason/status matches canonical artifacts.

If `HANDOFF.json` conflicts with current canonical artifact or STATE owner identity, route to `beo-route` or `user` depending on whether the conflict is resolvable.

## Cold-start behavior

If `STATE.json` exists:
1. Read `STATE.json`.
2. Verify active owner and feature.
3. Load active owner `SKILL.md`.
4. Continue or route only if owner identity is unsafe.

If `STATE.json` is absent but `.beads/artifacts/` exists:
1. Do not infer owner from memory.
2. Inspect canonical artifact presence minimally.
3. Treat as `missing_owner`.
4. Use `beo-route` to repair owner identity.

If no STATE and no artifacts exist:
- Setup/usage request -> `beo-setup`.
- New feature request -> `beo-explore`.
- Read-only rule lookup -> `beo-reference`.

## Debug return lifecycle

Before handing to `beo-debug`, the sending owner records return owner, source owner, blocked invariant, and evidence reference. `beo-debug` may not change the return owner unless evidence proves it invalid. The receiving owner must consume or clear the debug return before continuing.

## Closure lifecycle

When `STATE.json.status` becomes `done`, write closure summary with source owner, evidence ref, and closed time. Terminal closure requires both `status=done` and closure evidence.

## Pre-write freshness guard

Before any owner-owned mutation, reread the current required surfaces that authorize that mutation. If any required surface changed, disappeared, became stale, or contradicted preflight evidence, stop and route to the legal repair owner.

## Learning status is display-only

Learning status in `STATE.json` is display/orientation only. It does not authorize skill edits, approval, execution, review acceptance, or route selection.

Optional learning mirror fields:

```text
learning_case_pending
latest_learning_case
latest_learning_pattern
recommended_author_action
```

These are mirrors only. Avoid adding them unless needed.

## learning_source mirror

STATE may mirror `learning_source` for handoff/navigation only:

```json
{
  "learning_source": {
    "origin_owner": "...",
    "source_surface": "...",
    "source_section_or_pointer": "...",
    "case_type": "...",
    "case_status": "candidate",
    "affected_owner": "...",
    "target_path": "...",
    "runtime_status": "runtime_complete"
  }
}
```

Rules:
- For tiny lane, `TICKET.md` Review/Closure `learning_source` is canonical.
- For standard lane, the tagged source artifact/output is canonical.
- STATE `learning_source` is a navigation mirror unless no artifact source exists.
- If STATE conflicts with canonical source, canonical source wins.
- Do not let STATE learning mirror authorize compound to read broader evidence.
