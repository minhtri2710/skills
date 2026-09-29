#!/usr/bin/env python3
"""Heartbeat is first in the route table; plugin-eval cases own its behavior."""
from __future__ import annotations

import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow"


class HeartbeatRouteTest(unittest.TestCase):
    def setUp(self):
        self.skill_md = (SKILL / "SKILL.md").read_text(encoding="utf-8")

    def test_heartbeat_is_the_first_route_table_row(self):
        rows = [ln for ln in self.skill_md.splitlines() if ln.startswith("| **")]
        self.assertTrue(rows, "no route-table rows found")
        first_route = rows[0].split("|")[1].strip()
        self.assertEqual(
            first_route, "**Heartbeat**",
            "Heartbeat must be the first (highest-priority) route row")


if __name__ == "__main__":
    unittest.main()
