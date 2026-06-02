# BEO Skills

BEO is a repo-local Agent Skills package for safe Beads-backed delivery.

Install/copy/validate the whole `skills/beo/` sibling set together because delivery skills share `skills/beo/beo-reference/{references,registry,scripts}`.

## Agent loading rule

Do not eagerly load all BEO references. Load:

1. the selected skill card,
2. `beo-reference/references/doctrine-map.md`,
3. then only the narrow reference or registry required for the current decision.

## Skill classes

### Delivery owners

- `beo-plan`
- `beo-validate`
- `beo-execute`
- `beo-review`

### Support subroutines

- `beo-debug`
- `beo-learn`

### Maintenance

- `beo-author`
- `beo-setup`

### Read-only lookup

- `beo-reference`

## Normal delivery path

`beo-plan -> beo-validate -> beo-execute -> beo-review`

Support skills do not advance delivery state unless a delivery owner routes to them and then consumes their result.

## Minimal agent path

1. Pick or inspect exactly one bead with `br`.
2. Use `beo-plan` to claim, decompose if needed, and author `TICKET.yaml`.
3. Use `beo-validate` to grant or deny `PASS_EXECUTE`.
4. Use `beo-execute` to mutate approved scope and record evidence.
5. Use `beo-review` to accept, repair, diagnose, or route to user.

## Canonical lookup

Start with `beo-reference/references/doctrine-map.md`.

Hard invariants live in `beo-reference/references/kernel.md`.
Artifact boundaries live in `beo-reference/references/artifact-boundaries.md`.
Machine-readable contracts live in `beo-reference/registry/`.
