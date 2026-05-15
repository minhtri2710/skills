# Skill Contract Common

Authority: canonical for shared owner boundaries.

Runtime owner `SKILL.md` files must load and obey this contract before acting, and should keep only local entry conditions, ownership, writable surfaces, local stops/forbids, and explicit legal exits.

## Skill must be loaded to act

A BEO skill's `SKILL.md` must be loaded before any mutation owned by that skill. STATE/HANDOFF can orient but cannot authorize action by itself.

## Common Authority Rule

Human-readable artifact text may orient work, but approval-bearing or owner-bearing decisions require the current structured authority block for that density. Compact uses one `beo.ticket.v1` authority block in `TICKET.md`; full uses the canonical owner surfaces named in `references/artifacts.md`.

## Common Forbidden Actions

Unless explicitly owned by the loaded skill:
- do not mutate product files;
- do not mutate another owner’s artifact section;
- do not grant or refresh approval;
- do not select execution sets;
- do not emit terminal verdicts;
- do not route by STATE alone;
- do not treat helper output as authority;
- do not preserve compatibility shims or old aliases.

## Common Stop Conditions

Stop when owner identity is unsafe, required current artifacts or structured authority blocks are missing or contradictory, approval/integrity is missing/stale/invalid/unavailable for execution, Human Gates are unresolved outside the owner that records or resolves Human Gate status, the requested mutation is outside writable surfaces, or a handoff would cross owner boundaries without a legal transition.

When stopping, report the next action in this shape:

```text
Cannot continue because: <reason>
Current owner: <loaded owner>
Legal next owner/source: <owner | user | canonical reference>
Required read/evidence: <artifact section, registry, or helper output>
Writable surface now: <surface | none>
```

## Common Exit Rule

Owner files may name legal condition IDs, but `beo-reference -> registry/pipeline.json` is the only transition topology.
