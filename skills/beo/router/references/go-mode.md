# Go Mode (Full Pipeline)

Go mode chains all skills end-to-end with exactly **3 human gates**. No phase is skipped.

**Trigger:** User says "go", "run the full pipeline", "go mode", or `/go [feature]`.

**The 3 gates (never skip these):**

```
GATE 1 (after exploring):
  Present .beads/artifacts/<feature-name>/CONTEXT.md to user.
  Ask: "Decisions locked. Approve CONTEXT.md before planning?"
  HARD-GATE: do not invoke planning until user approves.

GATE 2 (after validating):
  Present: phase exit state, story count, bead count, risk summary, spike results.
  Ask: "Phase verified. Approve execution?"
  HARD-GATE: do not invoke swarming/executing until user approves.

GATE 3 (after reviewing):
  Present: P1 count, P2 count, P3 count.
  If P1 > 0: "P1 findings block merge. Fix before proceeding?"
  If P1 = 0: "Review complete. Approve close?"
  HARD-GATE: do not close epic until user responds.
```

**Go mode sequence:**
```
exploring → [GATE 1] → planning → validating → [GATE 2]
         → swarming (+ executing ×N) → reviewing → [GATE 3]
         → compounding → DONE
```

**Context budget in go mode:** If context exceeds 65% mid-pipeline, write HANDOFF.json with `"mode": "go"` so the next session resumes in go mode from the current phase.
