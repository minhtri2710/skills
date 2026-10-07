#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import os
import sys
import unittest
import urllib.request
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "prompt-leverage" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import augment_prompt  # noqa: E402


class TaskDetectionTest(unittest.TestCase):
    def test_keyword_precedence(self):
        self.assertEqual(augment_prompt.detect_task("research the code and review it", None), "review")
        self.assertEqual(augment_prompt.detect_task("write code", None), "coding")

    def test_keyword_boundaries_and_fallback(self):
        self.assertEqual(augment_prompt.detect_task("preview the output", None), "analysis")
        self.assertEqual(augment_prompt.detect_task("fixing the output", None), "analysis")
        self.assertEqual(augment_prompt.detect_task("find sources", None), "research")

    def test_explicit_task_overrides_detected_keywords(self):
        self.assertEqual(augment_prompt.detect_task("review this code", "writing"), "writing")


class UpgradeTest(unittest.TestCase):
    def test_template_preserves_prompt_and_uses_default_intensity(self):
        prompt = "  fix   the\n```python\nvalue = 1\n```\n"
        out = augment_prompt.upgrade_prompt(prompt)
        self.assertIn("Complete this task:   fix   the\n```python\nvalue = 1\n```", out)
        self.assertIn("Task type: coding", out)
        self.assertIn("Effort level: Standard", out)
        self.assertIn("Inspect the relevant files", out)

    def test_explicit_task_and_intensity_override_inference_and_default(self):
        out = augment_prompt.upgrade_prompt("review this code", "writing", "Deep")
        self.assertIn("Task type: writing", out)
        self.assertIn("Effort level: Deep", out)
        self.assertIn("Return polished final copy", out)

    def test_cli_defaults_and_explicit_overrides_without_credentials_or_network(self):
        defaults = augment_prompt.parse_args(["review this code"])
        self.assertIsNone(defaults.task)
        self.assertEqual(defaults.intensity, "Standard")

        out = io.StringIO()
        with (
            mock.patch.object(sys, "argv", ["augment_prompt.py", "review this code", "--task", "writing", "--intensity", "Light"]),
            mock.patch.dict(os.environ, {}, clear=True),
            mock.patch.object(urllib.request, "urlopen", side_effect=AssertionError("unexpected network request")),
            contextlib.redirect_stdout(out),
        ):
            augment_prompt.main()

        self.assertIn("Task type: writing", out.getvalue())
        self.assertIn("Effort level: Light", out.getvalue())


if __name__ == "__main__":
    unittest.main()
