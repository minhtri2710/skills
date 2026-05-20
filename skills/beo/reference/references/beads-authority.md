# Beads Authority

`br` is canonical for issue identity, lifecycle, dependencies, claims, comments, ready queue, and closure. BEO reads and writes Beads through contracted commands only.

## Canonical startup sequence

1. `br show <issue-id> --json` to verify the selected issue.
2. Claim with `br update --actor "$ACTOR" <issue-id> --claim --json` before any owned write.

## Required selected-issue read

- `br show <issue-id> --json`

## Optional discovery read

- `br ready --json`

## Claim rule

Set actor first:

```bash
ACTOR="${BR_ACTOR:-${AGENT_NAME:-assistant}}"
export BEO_ACTOR="$ACTOR"
```

Then claim before ticket mutation, material decomposition, product mutation, or closure:

```bash
br update --actor "$ACTOR" <issue-id> --claim --json
```

`--claim` is a required contracted BEO capability, not a portable assumption about every Beads install. If setup cannot prove that `--claim` atomically sets assignee and `status=in_progress`, BEO fails closed and must not fall back to separate status/assignee writes.

`ACTOR` is the Beads audit actor for mutating `br` commands. It is not a BEO owner, Git author, Human Gate approver, approval authority, or `bv` recommendation source. Missing actor identity or a non-matching claim fails closed.

## Contracted writes

- `br create --actor "$ACTOR" ... --json` for child beads during decomposition.
- `br dep add --actor "$ACTOR" <dependent-id> <blocker-id> --json` for execution-order edges.
- `br update --actor "$ACTOR" <issue-id> --add-label <label> --json` for BEO state labels.
- `br comments add --actor "$ACTOR" <issue-id> --message <message> --json` for concise milestones.
- `br close --actor "$ACTOR" <issue-id> --reason <reason> --json` only from `beo-review`, after accept or explicit abandonment with a registered `abandon_reason`.
- `br sync --flush-only` to flush Beads state without git operations.

## Parent lifecycle

Parent epic/feature beads are planning containers. `beo-plan` may create child atomic beads and dependency edges, then leave the parent open with a decomposition comment. Parent closure is handled by Beads after children close.

## Boundary

`br` may claim, comment, label, create, link, close, and sync issues. It never grants `PASS_EXECUTE`, widens scope, authorizes side effects, mutates product files, or emits BEO verdicts.
