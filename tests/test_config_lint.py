#!/usr/bin/env python3
"""Unit tests for the reviewer-fallback config lint."""
from __future__ import annotations

import contextlib
import io
import tempfile
import unittest
from pathlib import Path
import sys

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import config_lint  # noqa: E402


class ConfigLintTest(unittest.TestCase):
    def run_config(self, text: str) -> tuple[int, str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.md"
            path.write_text(text, encoding="utf-8")
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                code = config_lint.main(["--config", str(path)])
            return code, output.getvalue()

    def test_clean_config_is_ok(self):
        code, output = self.run_config(
            "- engineer-kind: pi\n"
            "- reviewer-fallback: codex\n"
            "- engineer-args: --model engineer/model\n"
        )
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)

    def test_same_kind_without_distinct_reviewer_model_is_conflict(self):
        cases = (
            "- engineer-kind: pi\n- reviewer-fallback: pi\n",
            "- engineer-kind: pi\n- reviewer-fallback: pi\n"
            "- engineer-args: --model same/model\n"
            "- reviewer-fallback-args: --model same/model\n",
        )
        for text in cases:
            with self.subTest(text=text):
                code, output = self.run_config(text)
                self.assertNotEqual(code, 0)
                self.assertIn("CONFLICT:", output)
                self.assertIn("reviewer-fallback-args", output)
                self.assertIn("engineer-args", output)

    def test_distinct_pinned_model_is_clean(self):
        code, output = self.run_config(
            "- engineer-kind: pi\n"
            "- reviewer-fallback: pi\n"
            "- engineer-args: --model engineer/model\n"
            "- reviewer-fallback-args: --model reviewer/model\n"
        )
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertNotIn("CONFLICT:", output)

    def test_engineer_fallback_collision_is_warning_only(self):
        code, output = self.run_config(
            "- engineer-kind: pi\n"
            "- reviewer-fallback: pi\n"
            "- engineer-args: --model engineer/model\n"
            "- reviewer-fallback-args: --model reviewer/model\n"
            "- engineer-fallback-args: --model reviewer/model\n"
        )
        self.assertEqual(code, 0)
        self.assertIn("WARNING:", output)
        self.assertNotIn("CONFLICT:", output)


if __name__ == "__main__":
    unittest.main()
