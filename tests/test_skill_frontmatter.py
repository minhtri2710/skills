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
        tracked = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "-z", "--", "skills"],
            capture_output=True, text=True, check=True,
        ).stdout.split("\0")
        tracked_parts = [Path(name).parts for name in tracked if name]
        skill_dirs = {parts[1] for parts in tracked_parts if len(parts) > 2}
        skill_paths = sorted(repo_root.joinpath(*parts) for parts in tracked_parts
                             if len(parts) == 3 and parts[2] == "SKILL.md")
        for skill_dir in sorted(skill_dirs):
            with self.subTest(skill_dir=skill_dir):
                self.assertIn(repo_root / "skills" / skill_dir / "SKILL.md", skill_paths, skill_dir)

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
