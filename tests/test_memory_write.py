"""Unit tests for the shared learning-note frontmatter parser and writer."""
from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-reference"
SCRIPTS = REFERENCE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


VALID_USER_REQUEST = """---
type: "learning"
basis_ref: "skills/beo/beo-reference/references/memory.md"
evidence_refs:
  - "skills/beo/beo-reference/references/memory.md"
  - "skills/beo/beo-reference/scripts/beo_memory_write.py"
secret_policy: "handles_only"
source_type: "user_request"
case_type: "success_pattern"
tags: [parser, frontmatter]
---
Short body.
"""

VALID_LEARNING_CANDIDATE = """---
type: "learning"
basis_ref: "skills/beo/beo-reference/references/memory.md"
evidence_refs:
  - "skills/beo/beo-reference/references/memory.md"
  - "skills/beo/beo-reference/scripts/beo_memory_write.py"
secret_policy: "handles_only"
source_bead_id: "br-1"
source_phase: "review"
condition_id: "repeat_pattern"
case_type: "success_pattern"
tags: [parser, frontmatter]
---
Short body.
"""


def remove_field(note: str, key: str) -> str:
    lines = note.splitlines(keepends=True)
    result: list[str] = []
    removing = False
    for line in lines:
        if not removing and line.startswith(f"{key}:"):
            removing = True
            continue
        if removing and line.startswith("  - "):
            continue
        removing = False
        result.append(line)
    return "".join(result)


def replace_field(note: str, key: str, new_line: str) -> str:
    lines = note.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.startswith(f"{key}:"):
            ending = "\n" if line.endswith("\n") else ""
            lines[index] = new_line + ending
            next_index = index + 1
            while next_index < len(lines) and lines[next_index].startswith("  - "):
                del lines[next_index]
            return "".join(lines)
    raise AssertionError(f"field not found: {key}")


def parse_note(note: str) -> dict[str, object]:
    import beo_memory_write

    return beo_memory_write.extract_frontmatter(note)


class ExtractFrontmatterTest(unittest.TestCase):
    def test_extract_frontmatter_cases(self):
        import beo_memory_write

        cases = [
            ("valid note", VALID_USER_REQUEST, None),
            ("no leading marker", VALID_USER_REQUEST.removeprefix("---\n"), "must start with frontmatter"),
            ("unclosed", VALID_USER_REQUEST.rsplit("\n---\n", 1)[0], "not closed"),
            ("wrong closer", VALID_USER_REQUEST.replace("\n---\nShort body.", "\n----\nShort body."), "not closed"),
            ("CRLF", VALID_USER_REQUEST.replace("\n", "\r\n"), "LF line endings"),
            ("no body", VALID_USER_REQUEST.rsplit("\n---\n", 1)[0] + "\n---", None),
        ]
        for name, note, error in cases:
            with self.subTest(name=name):
                if error is None:
                    frontmatter = beo_memory_write.extract_frontmatter(note)
                    self.assertEqual(frontmatter["type"], "learning")
                else:
                    with self.assertRaisesRegex(ValueError, error):
                        beo_memory_write.extract_frontmatter(note)

    def test_valid_note_has_expected_values(self):
        frontmatter = parse_note(VALID_USER_REQUEST)
        self.assertEqual(frontmatter["evidence_refs"], [
            "skills/beo/beo-reference/references/memory.md",
            "skills/beo/beo-reference/scripts/beo_memory_write.py",
        ])
        self.assertEqual(frontmatter["tags"], ["parser", "frontmatter"])


class ParseScalarTest(unittest.TestCase):
    def test_parse_scalar_cases(self):
        import beo_memory_write

        cases = [
            ("", None),
            ("~", "~"),
            ("true", "true"),
            ("123", "123"),
            ("1e3", "1e3"),
            ("nan", "nan"),
            ('"a b"', "a b"),
            ("'a'", "a"),
            ('""', ""),
            ('"open', '"open'),
            ("  x  ", "x"),
        ]
        for token, expected in cases:
            with self.subTest(token=token):
                self.assertEqual(beo_memory_write._parse_scalar(token), expected)


class SplitFlowListTest(unittest.TestCase):
    def test_split_flow_list_cases(self):
        import beo_memory_write

        cases = [
            ("a, b", ["a", "b"]),
            ('"a, b", c', ["a, b", "c"]),
            ("'x,y', z", ["x,y", "z"]),
            ("a, [b, c]", ["a", "[b, c]"]),
            ("", []),
            ("a,,b", ["a", "b"]),
        ]
        for inner, expected in cases:
            with self.subTest(inner=inner):
                self.assertEqual(beo_memory_write._split_flow_list_items(inner), expected)


class ParseFrontmatterBlockTest(unittest.TestCase):
    def test_parse_frontmatter_block_cases(self):
        import beo_memory_write

        cases = [
            ("indented block list", 'key:\n  - "a"\n  - "b"', {"key": ["a", "b"]}, None),
            ("flush-left block list", 'key:\n- "a"\n- "b"', {"key": ["a", "b"]}, None),
            ("flow list", 'tags: ["a, b", c]', {"tags": ["a, b", "c"]}, None),
            ("key alone", "key:", {"key": None}, None),
            ("indented non-list", "key:\n  value", None, "expected list item"),
            ("indented first line", "  key: value", None, "unexpected indented line"),
            ("line without colon", "title", None, "expected 'key: value'"),
            ("empty key", ": value", None, "empty key"),
            ("comments and blanks", '# comment\n\nkey: "value"\n\n', {"key": "value"}, None),
            ("quoted colon", 'title: "a: b"', {"title": "a: b"}, None),
            ("numeric-looking scalar", "n: 123", {"n": "123"}, None),
            ("duplicate key", "key: one\nkey: two", {"key": "two"}, None),
            ("blank before flush-left list", "key:\n\n- a", None, "expected 'key: value'"),
        ]
        for name, block, expected, error in cases:
            with self.subTest(name=name):
                if error is None:
                    self.assertEqual(beo_memory_write._parse_frontmatter_block(block), expected)
                else:
                    with self.assertRaisesRegex(ValueError, error):
                        beo_memory_write._parse_frontmatter_block(block)


class ValidateLearningFrontmatterTest(unittest.TestCase):
    def assert_valid(self, note: str, issue: str | None, case_type: str, mode: str) -> None:
        import beo_memory_write

        beo_memory_write.validate_learning_frontmatter(parse_note(note), issue, case_type, mode)

    def test_required_fields_and_validation_cases(self):
        import beo_memory_write

        required_by_mode = [
            ("user_request", VALID_USER_REQUEST, None, ["type", "basis_ref", "evidence_refs", "secret_policy", "source_type"]),
            ("learning_candidate", VALID_LEARNING_CANDIDATE, "br-1", ["type", "basis_ref", "evidence_refs", "secret_policy", "source_bead_id", "source_phase", "condition_id"]),
        ]
        for mode, valid_note, issue, required_fields in required_by_mode:
            for field in required_fields:
                with self.subTest(mode=mode, case="missing", field=field):
                    missing = remove_field(valid_note, field)
                    with self.assertRaisesRegex(ValueError, field):
                        beo_memory_write.validate_learning_frontmatter(
                            parse_note(missing), issue, "success_pattern", mode,
                        )

        cases = [
            ("source bead mismatch", replace_field(VALID_LEARNING_CANDIDATE, "source_bead_id", 'source_bead_id: "br-2"'), "learning_candidate", "br-1", "source_bead_id 'br-2'.*br-1", "failure"),
            ("numeric-looking issue id", replace_field(VALID_LEARNING_CANDIDATE, "source_bead_id", "source_bead_id: 123"), "learning_candidate", "123", None, "valid"),
            ("wrong source type", replace_field(VALID_USER_REQUEST, "source_type", 'source_type: "other"'), "user_request", None, "source_type: user_request", "failure"),
            ("case type mismatch", replace_field(VALID_USER_REQUEST, "case_type", 'case_type: "failure_pattern"'), "user_request", None, "case_type", "failure"),
            ("missing evidence refs", remove_field(VALID_USER_REQUEST, "evidence_refs"), "user_request", None, "evidence_refs", "failure"),
            ("empty evidence refs scalar", replace_field(VALID_USER_REQUEST, "evidence_refs", "evidence_refs:"), "user_request", None, "non-empty list", "failure"),
            ("empty evidence refs list", replace_field(VALID_USER_REQUEST, "evidence_refs", "evidence_refs: []"), "user_request", None, "non-empty list", "failure"),
            ("blank evidence ref", VALID_USER_REQUEST.replace(
                '  - "skills/beo/beo-reference/references/memory.md"', '  - ""', 1,
            ), "user_request", None, "non-empty list", "failure"),
            ("wrong type", replace_field(VALID_USER_REQUEST, "type", 'type: "other"'), "user_request", None, "type must be one of", "failure"),
            ("wrong secret policy", replace_field(VALID_USER_REQUEST, "secret_policy", 'secret_policy: "plain"'), "user_request", None, "secret_policy must be handles_only", "failure"),
        ]
        for name, note, mode, issue, error, result in cases:
            with self.subTest(name=name):
                if result == "valid":
                    self.assert_valid(note, issue, "success_pattern", mode)
                else:
                    with self.assertRaisesRegex(ValueError, error):
                        self.assert_valid(note, issue, "success_pattern", mode)


class MainTest(unittest.TestCase):
    def call_main(self, root: Path, note: str, *args: str) -> tuple[int, dict[str, object]]:
        import beo_memory_write

        markdown_file = root / "input.md"
        markdown_file.write_text(note, encoding="utf-8")
        extra = list(args)
        mode = "user_request"
        if "--mode" in extra:
            mode_index = extra.index("--mode")
            mode = extra[mode_index + 1]
            del extra[mode_index:mode_index + 2]
        argv = ["--mode", mode, "--markdown-file", str(markdown_file), "--root", str(root), *extra]
        with mock.patch.dict(os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()) as stdout:
            rc = beo_memory_write.main(argv)
        return rc, json.loads(stdout.getvalue())

    def test_main_cases(self):
        cases = [
            ("user request", VALID_USER_REQUEST, (), 0, "written"),
            ("learning candidate", VALID_LEARNING_CANDIDATE, ("--mode", "learning_candidate", "--issue", "br-1", "--case-type", "success_pattern", "--slug", "ok"), 0, "written"),
            ("candidate without issue", VALID_LEARNING_CANDIDATE, ("--mode", "learning_candidate"), 1, "failed"),
            ("missing markdown file", None, (), 1, "failed"),
            ("without frontmatter", VALID_USER_REQUEST.removeprefix("---\n"), (), 1, "failed"),
        ]
        for name, note, args, expected_rc, expected_status in cases:
            with self.subTest(name=name):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp)
                    (root / ".beads").mkdir()
                    if name == "missing markdown file":
                        import beo_memory_write

                        with mock.patch.dict(os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()) as stdout:
                            rc = beo_memory_write.main([
                                "--mode", "user_request", "--markdown-file", str(root / "missing.md"), "--root", str(root),
                            ])
                        report = json.loads(stdout.getvalue())
                    else:
                        rc, report = self.call_main(root, note, *args)
                    self.assertEqual(rc, expected_rc)
                    self.assertEqual(report["status"], expected_status)
                    if name == "user request":
                        self.assertTrue(list((root / ".beads" / "learnings").glob("*.md")))
                    elif name == "missing markdown file":
                        self.assertIn("cannot read --markdown-file", report["error"])
                    elif name == "without frontmatter":
                        self.assertIn("Frontmatter validation failed", report["error"])


if __name__ == "__main__":
    unittest.main()
