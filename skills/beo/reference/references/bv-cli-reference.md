# bv CLI Reference

Canonical `bv` robot-mode commands for graph analytics. Robot-mode outputs use JSON.

## Scheduling And Triage

```bash
bv --robot-plan --format json
bv --robot-next --format json
bv --robot-triage --format json
```

## Graph Health

```bash
bv --robot-insights --format json
bv --robot-suggest --format json
bv --robot-priority --format json
bv --robot-alerts --format json
```

## Per-Bead Analysis

```bash
bv --robot-blocker-chain <id> --format json
bv --robot-causality <id> --format json
```

## Scoped Queries

`--graph-root <epic-id>` scopes any robot command to one epic subgraph.

```bash
bv --robot-triage --graph-root <epic-id> --format json
bv --robot-plan --graph-root <epic-id> --format json
bv --robot-insights --graph-root <epic-id> --format json
bv --robot-plan --label <label> --format json
```

## Recipes

```bash
bv --recipe actionable --robot-plan --format json
bv --recipe high-impact --robot-triage --format json
```

## Output Notes

### `robot-plan`

Returns:

```text
{ plan: { tracks: [{ items: [{ id, unblocks, ... }] }], total_actionable, total_blocked, summary } }
```

Each track is one parallel execution lane. Items inside a track execute sequentially. When nothing is actionable, `tracks` is `null`.

### `robot-next`

Returns:

```text
{ pick: { id, title, reason } }
```

When nothing is ready, returns:

```text
{ message: "No actionable items available" }
```

### `robot-insights`

Returns analytics including `cycles`, `articulation_points`, `k_core`, `slack`, and `advanced_insights`.

Key fields:
- `cycles`: circular dependencies that must be resolved before execution
- `articulation_points`: high-risk beads whose removal disconnects the graph
- `slack`: scheduling flexibility versus critical-path work
- `advanced_insights`: PageRank, betweenness, and HITS rankings when computed

### `robot-triage`

Returns:

```text
{
  data_hash,
  generated_at,
  triage: {
    quick_ref,
    recommendations,
    quick_wins,
    blockers_to_clear,
    project_health
  },
  usage_hints
}
```

### `robot-suggest`

Returns missing-dependency, duplicate, label-hygiene, and cycle suggestions. Filter with `--suggest-type <type>`.

### `robot-alerts`

Returns:

```text
{ alerts: [...], summary: { total, critical, warning, info } }
```

Filter with `--alert-type` and `--severity`.
