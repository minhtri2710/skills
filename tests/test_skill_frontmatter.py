#!/usr/bin/env python3
from __future__ import annotations

import unittest

import yaml

import support


class SkillFrontmatterTest(unittest.TestCase):
    def test_every_skill_has_valid_frontmatter(self):
        skills_root = support.ROOT / "skills"
        tracked = support.git(support.ROOT, "ls-files", "--cached", "--others", "--exclude-standard", "--", "skills").splitlines()
        skill_dirs = {path.split("/")[1] for path in tracked if path.count("/") >= 2}
        skill_paths = []
        for skill_dir in sorted(skill_dirs):
            path = skills_root / skill_dir / "SKILL.md"
            with self.subTest(skill_dir=skill_dir):
                self.assertTrue(path.is_file(), skill_dir)
            if path.is_file():
                skill_paths.append(path)

        expected_catalog = []
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
                manual = frontmatter.get("disable-model-invocation", False)
                self.assertIsInstance(manual, bool, path)
                label = f"/{name}" if manual else name
                target = path.relative_to(support.ROOT).as_posix()
                expected_catalog.append(f"[`{label}`]({target})")

        readme = (support.ROOT / "README.md").read_text(encoding="utf-8")
        section = readme.partition("\n## Standalone skills\n")[2].partition("\n## ")[0]
        cells = (row.split("|", 2)[1].strip() for row in section.splitlines() if row.startswith("|"))
        catalog = [cell for cell in cells if cell != "Skill" and cell.strip(":-")]
        self.assertCountEqual(catalog, expected_catalog)


if __name__ == "__main__":
    unittest.main()
