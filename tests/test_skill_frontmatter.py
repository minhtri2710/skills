#!/usr/bin/env python3
"""Regression tests for skill YAML frontmatter."""
from __future__ import annotations

import unittest
from pathlib import Path

import yaml


class SkillFrontmatterTest(unittest.TestCase):
    def test_every_skill_has_valid_frontmatter(self):
        repo_root = Path(__file__).resolve().parents[1]
        skill_paths = sorted((repo_root / "skills").glob("*/SKILL.md"))
        skill_dirs = {path.parent.name for path in skill_paths}
        self.assertEqual(len(skill_paths), len(skill_dirs))

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
                self.assertEqual(name, path.parent.name)
                self.assertIsInstance(description, str, path)
                self.assertTrue(description.strip(), path)
                self.assertLessEqual(len(description), 1024, path)

        readme = (repo_root / "README.md").read_text(encoding="utf-8")
        inventory = {
            line.split("`", 2)[1]
            for line in readme.splitlines()
            if line.startswith("| `") and " |" in line
        }
        self.assertEqual(inventory, skill_dirs)


if __name__ == "__main__":
    unittest.main()
