#!/usr/bin/env python3
from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


class SkillFrontmatterTest(unittest.TestCase):
    def test_every_skill_has_valid_frontmatter(self):
        repo_root = Path(__file__).resolve().parents[1]
        skills_root = repo_root / "skills"
        skill_dirs = {path.name for path in skills_root.iterdir() if path.is_dir()}
        skill_paths = sorted(skills_root.glob("*/SKILL.md"))
        for skill_dir in sorted(skill_dirs):
            with self.subTest(skill_dir=skill_dir):
                self.assertTrue((skills_root / skill_dir / "SKILL.md").is_file(), skill_dir)

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


    def test_terminal_delivery_backends_cover_every_seat_operation(self):
        skill = Path(__file__).resolve().parents[1] / "skills" / "terminal-delivery-workflow"
        references = skill / "references"
        text = (references / "seat-operations.md").read_text(encoding="utf-8")
        section = text.split("\n## Operations\n", 1)[1].split("\n## ", 1)[0]
        operations = re.findall(r"^### `([a-z]+)`$", section, re.M)
        self.assertEqual(
            operations,
            ["identify", "spawn", "prompt", "read", "state", "wait", "list",
             "processes", "interrupt", "close", "notify"],
        )
        backends = sorted(references.glob("backend-*.md"))
        self.assertTrue(backends)
        for path in backends:
            body = path.read_text(encoding="utf-8")
            for operation in operations:
                with self.subTest(backend=path.name, operation=operation):
                    heading = re.search(rf"^## {operation}$", body, re.M)
                    self.assertIsNotNone(heading)
                    entry = body[heading.end():].split("\n## ", 1)[0]
                    self.assertTrue(entry.strip())

    def test_terminal_delivery_doctrine_names_no_tool_command(self):
        skill = Path(__file__).resolve().parents[1] / "skills" / "terminal-delivery-workflow"
        references = skill / "references"
        paths = [skill / "SKILL.md", *sorted((skill / "templates").iterdir())]
        paths += [references / f"{name}.md" for name in (
            "lead", "supervisor", "charters", "closeout", "relaunch", "project-config", "seat-operations")]
        command = re.compile(r"\bherdr (?:agent|pane|tab|workspace|notification|server|worktree)\b")
        for path in paths:
            with self.subTest(path=path.name):
                self.assertIsNone(command.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
