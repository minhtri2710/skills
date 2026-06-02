# BEO Doctrine Map

Load exactly the narrowest canonical source needed for the decision. Do not eagerly load all references.

| Question | Load exactly | Decision produced | Never load |
|---|---|---|---|
| What invariant controls this situation? | `references/kernel.md` | Binding hard invariant or authority split | Full registry bundle |
| Where does this artifact or field belong? | `references/artifact-boundaries.md` | Canonical artifact owner and allowed placement | Lifecycle prose |
| What may this skill read, write, or emit? | `registry/phase-contracts.json` | Binding phase permission, write authority, or emitted condition | Other skill cards |
| Why does a phase permission or repair boundary exist? | `references/phase-contracts.md` | Binding guidance for ambiguous phase/repair cases | Full registry bundle |
| Which route or condition name is legal? | `registry/pipeline.json` | Exact transition, support outcome, or forbidden normal event | Narrative lifecycle docs |
| Is this `TICKET.yaml` valid? | `registry/ticket.schema.json` | Binding ticket shape and allowed fields | Historical examples |
| Is this `state.json` write valid? | `registry/state.schema.json` | Binding state shape and owner write policy | Ticket schema |
| Can I append this runtime event? | `registry/runtime-event.schema.json` | Allowed non-normal event kind and payload | Normal transition docs |
| Is `PASS_EXECUTE` still valid? | `registry/approval-envelope.json` | Approval validity predicates and invalidation reason | Memory docs |
| Which mode or path rule applies? | `registry/profiles.json` | Quick/standard/strict requirement, protected path, or broad-glob decision | Strict reservation schema unless strict mode needs it |
| Can I claim, decompose, use `bv`, or close with `br`? | `references/lifecycle.md` | Beads lifecycle command authority and `bv` advisory boundary | Safety docs unless mutation risk is disputed |
| Can I mutate this file or perform this side effect? | `references/safety.md` | Scope, dirty-tree, side-effect, recovery, or reservation decision | Memory docs |
| Can memory inform this decision? | `references/memory.md` | Advisory recall/learning decision; never approval, verdict, closure, or Human Gate authority | Approval/state registries unless independently needed |
| Is a missing tool blocking or degraded? | `references/degraded-tools.md` | Required/degraded tool status and fallback | Full setup script implementation |
| Who owns a BEO maintenance rule change? | `beo-author/SKILL.md` plus this map | Canonical owner for the rule before editing | Unrelated skill cards |

## Rule ownership

If a rule appears in multiple places, the `Load exactly` column identifies the canonical owner. Non-owner files should cite the canonical owner instead of restating the rule.
