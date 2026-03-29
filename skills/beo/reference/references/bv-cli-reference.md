# bv CLI Reference

`bv` (Beads Viewer) provides graph analytics over the bead dependency graph. All robot-mode commands output JSON.

## Scheduling & Triage

```bash
bv --robot-plan --format json       # Parallel execution tracks (task ordering)
bv --robot-next --format json       # Single top-pick next task recommendation
bv --robot-triage --format json     # Full triage with recommendations
```

## Graph Health

```bash
bv --robot-insights --format json   # Graph health: cycles, articulation points, critical path, bottlenecks
bv --robot-suggest --format json    # Suggest missing dependencies, detect duplicates
bv --robot-priority --format json   # Priority misalignment detection
bv --robot-alerts --format json     # Stale issues, blocking cascades
```

## Per-Bead Analysis

```bash
bv --robot-blocker-chain <id> --format json   # Blocker chain for a specific bead
bv --robot-causality <id> --format json       # Causality analysis for a specific bead
```

## Scoped Queries

```bash
bv --robot-triage --graph-root <epic-id> --format json   # Triage scoped to one epic
bv --robot-plan --label <label> --format json             # Plan scoped to label subgraph
```

## Recipes (Pre-Filtered)

```bash
bv --recipe actionable --robot-plan --format json      # Only actionable beads
bv --recipe high-impact --robot-triage --format json   # Only high-impact beads
```

## Interpreting bv Output

### robot-plan
Returns `{ plan: { tracks: [{ items: [{ id, unblocks, ... }] }], total_actionable, total_blocked, summary } }`. Each track is a parallel execution lane. Items within a track must be executed sequentially. Access via `jq '.plan.tracks[0].items | map(.id)'`. When no tasks are actionable, `tracks` is `null`.

### robot-next
Returns `{ pick: { id, title, reason } }` when a task is available. Returns `{ message: "No actionable items available" }` when nothing is ready. The single best next task to work on.

### robot-insights
Returns analytics including `cycles`, `articulation_points`, `k_core`, `slack`, and `advanced_insights`. Key fields:
- `cycles`: Array of circular dependency chains (MUST be resolved before execution)
- `articulation_points`: Beads whose removal would disconnect the graph (high-risk)
- `slack`: Tasks with scheduling flexibility vs. those on the critical path
- `advanced_insights`: PageRank, betweenness, HITS rankings (when computed)

### robot-triage
Returns `{ quick_ref, recommendations, health }` with metrics, per-bead advisories, and actionable recommendations.

### robot-suggest
Returns suggestions for missing dependencies, duplicates, label hygiene, and cycles. Filter with `--suggest-type <type>`.

### robot-alerts
Returns `{ alerts: [...], summary: { total, critical, warning, info } }`. Detects stale issues and blocking cascades. Filter with `--alert-type` and `--severity`.
