# BEO Doctrine Map

For any general operator question, check the primary BEO Kernel first. Load narrow files only when detailed schema or registry validation is required.

## Primary Operator Rules
- [kernel.md](references/kernel.md): Binding hard invariants, delivery loop, authority splits, risk modes, approval validity, runtime events, reservations, memory, and repair policies.

## Subordinate Reference Map

| Question | Load exactly | Decision produced | Never load |
|---|---|---|---|
| Where does this artifact or field belong? | `references/artifact-boundaries.md` | Canonical artifact owner and allowed placement | Lifecycle prose |
| What must a parent epic/feature `PLAN.md` contain? | `templates/PLAN.template.md`; phase-specific behavior stays in the selected phase skill card (`beo-plan` when writing, `beo-validate` when validating) | Binding PLAN artifact shape for decomposition readiness | Ticket/state schemas unless writing atomic artifacts |
| What may this skill read, write, or emit? | `registry/phase-contracts.json` | Binding phase permission, write authority, or emitted condition | Other skill cards |
| Why does a phase permission or repair boundary exist? | `references/phase-contracts.md` | Subordinate guidance for phase/repair details | Full registry bundle |
| Which route or condition name is legal? | `registry/pipeline.json` | Exact transition, support outcome, or forbidden normal event | Narrative lifecycle docs |
| Is this `TICKET.yaml` valid? | `registry/ticket.schema.json` | Binding ticket shape and allowed fields | Historical examples |
| Is this `state.json` write valid? | `registry/state.schema.json` | Binding state shape and owner write policy | Ticket schema |
| Can I append this runtime event? | `registry/runtime-event.schema.json` | Allowed non-normal event kind and payload | Normal transition docs |
| Is `PASS_EXECUTE` still valid? | `registry/approval-envelope.json` | Approval validity predicates and invalidation reason | Memory docs |
| Which mode or path rule applies? | `registry/profiles.json` | Quick/standard/strict requirement, protected path, or broad-glob decision | Strict reservation schema unless strict mode needs it |
| Can I claim, decompose, use `bv`, close with `br`, or debug lifecycle CLI syntax? | `references/lifecycle.md` | Subordinate lifecycle command authority, CLI syntax, and `bv` advisory boundary | Safety docs unless mutation risk is disputed |
| Can I mutate this file or perform this side effect? | `references/safety.md` | Subordinate dirty-tree, side-effect, and recovery guidance | Memory docs |
| Can memory inform this decision? | `references/memory.md` | Subordinate memory and learning guidance | Approval/state registries unless independently needed |
| Is a harness change proposal valid? | `registry/harness-proposal.schema.json` | Binding proposal shape and allowed fields | Ticket or state schema |
| Does a climate scan need to run? | `beo-climate/SKILL.md` plus `beo-climate/config.yaml` | Scan cadence, scope, and auto-heal allowlist | Delivery skill cards |
| Is a missing tool blocking or degraded? | `references/degraded-tools.md` | Required/degraded tool status and fallback | Full setup script implementation |
| Who owns a BEO maintenance rule change? | `beo-author/SKILL.md` plus this map | Canonical owner for the rule before editing | Unrelated skill cards |

## Rule ownership

`references/kernel.md` is the canonical owner of BEO rules and invariants. Other markdown references in the `references/` directory are subordinate to `references/kernel.md`.

