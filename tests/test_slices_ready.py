#!/usr/bin/env python3
"""Tests for the slice DAG ready-set CLI."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import slices_ready  # noqa: E402


class SlicesReadyTest(unittest.TestCase):
    def run_dag(self, dag: dict, *args: str) -> tuple[int, str, str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "slices.json"
            path.write_text(json.dumps(dag), encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = slices_ready.main(["--file", str(path), *args])
            return code, stdout.getvalue(), stderr.getvalue()

    @staticmethod
    def dag() -> dict:
        return {
            "id": "run",
            "version": 1,
            "nodes": [
                {"id": "root", "owner": "a", "paths": ["a"], "join": "shared"},
                {"id": "middle", "owner": "b", "paths": ["b"], "join": "shared"},
                {"id": "leaf", "owner": "c", "paths": ["c"], "join": "shared"},
            ],
            "edges": [
                {"from": "root", "to": "middle"},
                {"from": "middle", "to": "leaf"},
            ],
        }

    def test_roots_are_ready_when_done_is_empty(self):
        code, stdout, stderr = self.run_dag(self.dag())
        self.assertEqual(code, 0)
        self.assertEqual(stdout, "root\n")
        self.assertEqual(stderr, "")

    def test_node_waits_for_all_dependency_sources(self):
        dag = {
            "id": "run",
            "version": 1,
            "nodes": [
                {"id": "root", "owner": "a", "paths": ["a"], "join": "shared"},
                {"id": "other", "owner": "b", "paths": ["b"], "join": "shared"},
                {"id": "leaf", "owner": "c", "paths": ["c"], "join": "shared"},
            ],
            "edges": [
                {"from": "root", "to": "leaf"},
                {"from": "other", "to": "leaf"},
            ],
        }
        code, stdout, _ = self.run_dag(dag, "--done", "root")
        self.assertEqual(code, 0)
        self.assertEqual(stdout, "other\n")
        code, stdout, _ = self.run_dag(dag, "--done", "root,other")
        self.assertEqual(code, 0)
        self.assertEqual(stdout, "leaf\n")

    def test_fully_done_dag_has_empty_ready_set(self):
        code, stdout, stderr = self.run_dag(self.dag(), "--done", "root,middle,leaf")
        self.assertEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "")

    def test_unknown_edge_node_is_an_error(self):
        dag = self.dag()
        dag["edges"].append({"from": "missing", "to": "root"})
        code, stdout, stderr = self.run_dag(dag)
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("unknown node id", stderr)
        self.assertIn("missing", stderr)

    def test_cycle_is_an_error_naming_the_cycle(self):
        dag = self.dag()
        dag["edges"] = [
            {"from": "root", "to": "middle"},
            {"from": "middle", "to": "root"},
        ]
        code, stdout, stderr = self.run_dag(dag)
        self.assertNotEqual(code, 0)
        self.assertEqual(stdout, "")
        self.assertIn("cycle detected", stderr)
        self.assertIn("root", stderr)
        self.assertIn("middle", stderr)


if __name__ == "__main__":
    unittest.main()
