#!/usr/bin/env python3
from __future__ import annotations

import unittest
from importlib import import_module

import support

augment_prompt = import_module("skills.docs.scripts.augment_prompt")


def setUpModule() -> None:
    support.never_run()


class UpgradeTest(unittest.TestCase):
    def test_default_scaffold_is_independent_of_language_and_preserves_input(self):
        prompts = ("  S\u1eeda l\u1ed7i \u0111\u0103ng nh\u1eadp", "  fix   the login bug")
        scaffolds = []
        for text in prompts:
            prompt = text + "\n```python\n  value = 1\n```"
            _, out, _ = support.run_main(augment_prompt.main, [prompt])
            self.assertIn(prompt, out)
            self.assertIn("Task profile: general", out)
            scaffolds.append(out.replace(prompt, "<input>", 1))
        self.assertEqual(scaffolds[0], scaffolds[1])

    def test_explicit_profile_changes_guidance_not_just_the_label(self):
        prompt = "review the code"
        _, coding, _ = support.run_main(augment_prompt.main, [prompt, "--task", "coding"])
        _, review, _ = support.run_main(augment_prompt.main, [prompt, "--task", "review"])
        advice = "\nTool Rules:\n"
        self.assertNotEqual(coding.split(advice, 1)[1], review.split(advice, 1)[1])


if __name__ == "__main__":
    unittest.main()
