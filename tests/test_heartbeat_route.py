#!/usr/bin/env python3
"""Heartbeat route is present as the highest-priority read-only route.

A heartbeat / quick-status request must have an explicit route that starts no
long-running work. This pins the doctrine text so a future edit cannot quietly
drop the route, its prohibitions, or the relaunch-time carve — the mechanical
half of this delivery's R1 pin (the plugin-eval pos/neg pair is the reasoning
half, authored but not run per the Human's instruction).
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow"


class HeartbeatRouteTest(unittest.TestCase):
    def setUp(self):
        self.skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_heartbeat_is_the_first_route_table_row(self):
        rows = [ln for ln in self.skill_md.splitlines() if ln.startswith("| **")]
        self.assertTrue(rows, "no route-table rows found")
        self.assertIn(
            "Heartbeat", rows[0],
            "Heartbeat must be the first (highest-priority) route row")

    def test_heartbeat_paragraph_prohibits_long_running_work(self):
        low = self.skill_md.lower()
        for token in ("plugin eval", "test suite", "benchmark",
                      "relaunch recovery", "background command"):
            self.assertIn(
                token, low, f"heartbeat prohibition must name {token!r}")

    def test_relaunch_line_carves_out_heartbeat(self):
        # The before-any-other-action relaunch rule must exempt a heartbeat, else
        # recovery (itself long-running) would run on a bare status request.
        m = re.search(r"On a relaunch or compaction.*?(?:\n\n|\Z)",
                      self.skill_md, re.DOTALL)
        self.assertIsNotNone(m, "relaunch entry sentence not found")
        self.assertIn("heartbeat", m.group(0).lower(),
                      "relaunch entry must carve out the heartbeat route")

    def test_eval_execution_needs_explicit_request(self):
        low = self.skill_md.lower()
        self.assertIn("run eval", low)
        self.assertIn("--runs", low)


if __name__ == "__main__":
    unittest.main()
