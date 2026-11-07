#!/usr/bin/env python3
from __future__ import annotations

import unittest

import support
import augment_prompt


def setUpModule() -> None:
    support.never_run()


class TaskDetectionTest(unittest.TestCase):
    def test_keyword_precedence(self):
        self.assertEqual(augment_prompt.detect_task("research the code and review it", None), "review")
        self.assertEqual(augment_prompt.detect_task("write code", None), "coding")

    def test_keyword_boundaries_and_fallback(self):
        self.assertEqual(augment_prompt.detect_task("preview the output", None), "analysis")
        self.assertEqual(augment_prompt.detect_task("fixing the output", None), "analysis")
        self.assertEqual(augment_prompt.detect_task("find sources", None), "research")


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

    def test_cli_infers_task_and_defaults_the_intensity(self):
        _, out, _ = support.run_main(augment_prompt.main, ["review this code"])
        self.assertIn("Task type: review", out)
        self.assertIn("Effort level: Standard", out)

    def test_cli_explicit_task_and_intensity_override_the_defaults(self):
        _, out, _ = support.run_main(augment_prompt.main, ["review this code", "--task", "writing", "--intensity", "Light"])
        self.assertIn("Task type: writing", out)
        self.assertIn("Effort level: Light", out)


if __name__ == "__main__":
    unittest.main()
