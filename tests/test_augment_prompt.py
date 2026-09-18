#!/usr/bin/env python3
"""Tests for the TypeSafe-backed prompt upgrader."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "prompt-leverage" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import augment_prompt  # noqa: E402


def answers(*, score, choice=None):
    result = {"intensity": {"score": score}}
    if choice is not None:
        result["task"] = {"choice": choice}
    return result


class ClassifyTest(unittest.TestCase):
    def test_choice_and_score_are_asked_together(self):
        captured = {}

        def fake(state, questions):
            captured["state"] = state
            captured["questions"] = questions
            return answers(score=0.2, choice="research")

        with mock.patch.object(augment_prompt, "_system_one", fake):
            task, intensity = augment_prompt.classify("find the latest sources", None)

        self.assertEqual((task, intensity), ("research", "Light"))
        self.assertEqual(set(captured["questions"]), {"task", "intensity"})
        self.assertEqual(captured["questions"]["task"]["type"], "choice")
        self.assertEqual(captured["questions"]["intensity"]["type"], "score")

    def test_explicit_task_skips_the_choice_question(self):
        captured = {}

        def fake(state, questions):
            captured["questions"] = questions
            return answers(score=1.7)  # no "task" answer needed

        with mock.patch.object(augment_prompt, "_system_one", fake):
            task, intensity = augment_prompt.classify("ship it", "writing")

        self.assertEqual((task, intensity), ("writing", "Deep"))
        self.assertNotIn("task", captured["questions"])

    def test_score_rounds_to_nearest_level_and_clamps(self):
        cases = {0.0: "Light", 0.6: "Standard", 1.4: "Standard", 1.5: "Deep", 9.0: "Deep"}
        for score, expected in cases.items():
            with self.subTest(score=score):
                with mock.patch.object(
                    augment_prompt, "_system_one", lambda s, q, v=score: answers(score=v, choice="analysis")
                ):
                    _task, intensity = augment_prompt.classify("x", None)
                self.assertEqual(intensity, expected)

    def test_missing_api_key_fails_fast(self):
        with mock.patch.dict(augment_prompt.os.environ, {}, clear=True):
            with self.assertRaises(SystemExit):
                augment_prompt._system_one("x", {})


class UpgradeTest(unittest.TestCase):
    def test_template_carries_task_intensity_and_prompt(self):
        with mock.patch.object(
            augment_prompt, "_system_one", lambda s, q: answers(score=2.0, choice="coding")
        ):
            out = augment_prompt.upgrade_prompt("  fix   the\nparser bug  ", None)
        self.assertIn("Complete this task: fix the parser bug", out)
        self.assertIn("Task type: coding", out)
        self.assertIn("Effort level: Deep", out)
        self.assertIn("Inspect the relevant files", out)  # coding tool rule


if __name__ == "__main__":
    unittest.main()
