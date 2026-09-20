#!/usr/bin/env python3
"""Regression tests for skill YAML frontmatter."""
from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

import yaml


class SkillFrontmatterTest(unittest.TestCase):
    def test_every_skill_has_valid_frontmatter(self):
        repo_root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            ["git", "ls-files", "--", "skills/*/SKILL.md"],
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        skill_paths = sorted(
            repo_root / relative_path for relative_path in result.stdout.splitlines()
        )
        self.assertEqual(
            len(skill_paths),
            27,
            f"expected 27 skill files, found {len(skill_paths)}",
        )

        for path in skill_paths:
            with self.subTest(path=path):
                text = path.read_text(encoding="utf-8")
                self.assertTrue(text.startswith("---\n"), path)
                closing = text.find("\n---\n", 4)
                self.assertGreaterEqual(closing, 0, path)

                try:
                    frontmatter = yaml.safe_load(text[4:closing])
                except yaml.YAMLError as error:
                    self.fail(f"{path}: invalid YAML frontmatter: {error}")

                self.assertIsInstance(frontmatter, dict, path)
                name = frontmatter.get("name")
                description = frontmatter.get("description")
                self.assertIsInstance(name, str, path)
                self.assertTrue(name.strip(), path)
                self.assertIsInstance(description, str, path)
                self.assertTrue(description.strip(), path)


if __name__ == "__main__":
    unittest.main()
