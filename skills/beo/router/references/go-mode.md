# Go Mode (Full Pipeline)

Chain all skills end-to-end with exactly **3 human gates**. No phase skipped.

**Trigger:** User says "go", "run the full pipeline", "go mode", or `/go [feature]`.

**The 3 gates (never skip):**

<HARD-GATE>
GATE 1 (after exploring):
  Present CONTEXT.md. Ask: "Decisions locked. Approve before planning?"
  Do not invoke planning until user approves.

GATE 2 (after validating):
  Present: phase exit state, story count, bead count, risk summary, spike results.
  Ask: "Phase verified. Approve execution?"
  Do not invoke swarming/executing until user approves.

GATE 3 (after reviewing):
  Present: P1/P2/P3 counts.
  P1 > 0: "P1 findings block merge. Fix before proceeding?"
  P1 = 0: "Review complete. Approve close?"
  Do not close epic until user responds.
</HARD-GATE>

**Sequence:**
```
exploring → [GATE 1] → planning → validating → [GATE 2]
         → swarming (+ executing ×N) → reviewing → [GATE 3]
         → compounding → beo-router (next feature or session end)
```

**Context budget:** If context exceeds 65% mid-pipeline, write HANDOFF.json with `"mode": "go"` so next session resumes in go mode.
