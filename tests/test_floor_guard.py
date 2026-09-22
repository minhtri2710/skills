#!/usr/bin/env python3
"""Tests for the quality-floor diff guard."""
from __future__ import annotations

import io
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "quality-floor" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import floor_guard  # noqa: E402

CONSTRAINTS = """# Constraints

## Floor

- No new suppression comments
- No skipped or deleted tests

## Enforced with numbers

| Dimension | Rule | Checked by | Runs at |
| --- | --- | --- | --- |
| Coverage | changed lines >= 80% | `pytest --cov` | task end |
| LCP | <= 2500 ms | `lighthouse` | preview |

## Exceptions

| ID | Rule | Path | Reason | Removal condition |
| --- | --- | --- | --- | --- |
"""


class FloorGuardRepoTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self._tmp.name)
        self.git("init", "-q", "-b", "main")
        self.write("src/app.py", "def total(items):\n    return sum(items)\n")
        self.write(
            "tests/test_app.py",
            "from app import total\n\n\ndef test_total():\n    assert total([1, 2]) == 3\n    assert total([]) == 0\n",
        )
        self.write("tests/test_old.py", "def test_old():\n    assert True\n")
        self.write("tests/test_é.py", "def test_non_ascii():\n    assert True\n")
        self.write("src é.py", "value = 1\n")
        self.write("CONSTRAINTS.md", CONSTRAINTS)
        self.git("add", ".")
        self.git("commit", "-q", "-m", "base")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
            cwd=self.repo,
            check=True,
            capture_output=True,
        )

    def write(self, name: str, text: str) -> None:
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def run_guard(self, base: str = "main") -> tuple[int, str]:
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            code = floor_guard.main(["--base", base, "--repo", str(self.repo)])
        return code, err.getvalue()

    def test_ordinary_change_is_clean(self) -> None:
        self.write("src/app.py", "def total(items):\n    return sum(i for i in items)\n")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_added_lowering_moves_are_flagged_without_line_text(self) -> None:
        self.write(
            "src/app.py",
            "def total(items):\n"
            "    key = 'sk-live-SECRETVALUE'  # noqa: S105\n"
            "    raise NotImplementedError\n",
        )
        self.write("tests/test_app.py", (self.repo / "tests/test_app.py").read_text() + "\n@pytest.mark.skip\ndef test_x():\n    assert total([1]) == 1\n")
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[silenced-checker] src/app.py:2", err)
        self.assertIn("[unfinished-work] src/app.py:3", err)
        self.assertIn("[test-made-easier] tests/test_app.py:8", err)
        self.assertNotIn("SECRETVALUE", err)

    def test_untracked_file_is_scanned(self) -> None:
        self.write("src/new.py", "def later():\n    pass  # TODO\n")
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[unfinished-work] src/new.py:2", err)

    def test_deleted_test_file_is_flagged(self) -> None:
        (self.repo / "tests/test_old.py").unlink()
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[test-deleted] tests/test_old.py", err)
        self.assertNotIn("assertion-removed", err)

    def test_net_assertion_loss_in_kept_test_is_flagged(self) -> None:
        self.write("tests/test_app.py", "from app import total\n\n\ndef test_total():\n    assert total([1, 2]) == 3\n")
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[assertion-removed] tests/test_app.py:6", err)

    def test_rewritten_assertion_is_not_a_loss(self) -> None:
        self.write(
            "tests/test_app.py",
            "from app import total\n\n\ndef test_total():\n    assert total([1, 2]) == 3\n    assert total([]) == 0, 'empty'\n",
        )
        self.assertEqual(self.run_guard(), (0, ""))

    def test_tightened_thresholds_are_silent(self) -> None:
        text = CONSTRAINTS.replace(">= 80%", ">= 90%").replace("<= 2500 ms", "<= 2000 ms")
        self.write("CONSTRAINTS.md", text)
        self.assertEqual(self.run_guard(), (0, ""))

    def test_loosened_thresholds_are_flagged(self) -> None:
        text = CONSTRAINTS.replace(">= 80%", ">= 70%").replace("<= 2500 ms", "<= 3000 ms")
        self.write("CONSTRAINTS.md", text)
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertEqual(err.count("[threshold-loosened] CONSTRAINTS.md"), 2)

    def test_removed_bound_floor_rule_and_row_are_flagged(self) -> None:
        text = (
            CONSTRAINTS.replace("changed lines >= 80%", "changed lines covered")
            .replace("- No skipped or deleted tests\n", "")
            .replace("| LCP | <= 2500 ms | `lighthouse` | preview |\n", "")
        )
        self.write("CONSTRAINTS.md", text)
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[threshold-loosened]", err)
        self.assertIn("[floor-rule-removed]", err)
        self.assertIn("[constraint-removed]", err)

    def test_complete_exception_row_suppresses_matching_finding(self) -> None:
        self.write("src/new.py", "def later():\n    raise NotImplementedError\n")
        self.write("CONSTRAINTS.md", CONSTRAINTS + "| E1 | unfinished-work | src/*.py | port in progress | port lands |\n")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_exception_row_is_scoped_by_rule_and_path(self) -> None:
        self.write("src/new.py", "def later():\n    raise NotImplementedError\n")
        self.write("lib/x.py", "def later():\n    raise NotImplementedError\n")
        self.write("CONSTRAINTS.md", CONSTRAINTS + "| E1 | silenced-checker | src/*.py | vendor types | upstream ships types |\n")
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[unfinished-work] src/new.py:2", err)
        self.assertIn("[unfinished-work] lib/x.py:2", err)

    def test_incomplete_exception_row_is_flagged_and_suppresses_nothing(self) -> None:
        self.write("src/new.py", "def later():\n    raise NotImplementedError\n")
        self.write("CONSTRAINTS.md", CONSTRAINTS + "| E1 | * | src/** | port in progress |  |\n")
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[exception-incomplete] CONSTRAINTS.md:19", err)
        self.assertIn("[unfinished-work] src/new.py:2", err)

    def test_todo_as_vocabulary_is_not_unfinished_work(self) -> None:
        self.write("src/app.py", "def add(todo, items):\n    return [*items, todo]  # the Todo list\n")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_renamed_test_file_is_not_a_deletion(self) -> None:
        self.git("mv", "tests/test_old.py", "tests/test_older.py")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_unresolvable_base_exits_2(self) -> None:
        code, err = self.run_guard(base="does-not-exist")
        self.assertEqual(code, 2)
        self.assertIn("cannot run", err)

    def test_non_ascii_and_spaced_paths_drive_findings_and_exceptions(self) -> None:
        self.write("tests/test_é.py", "def test_non_ascii():\n    pass\n")
        self.write("src é.py", "value = 1  # noqa: E501\n")
        self.write(
            "CONSTRAINTS.md",
            CONSTRAINTS + "| E1 | silenced-checker | src *.py | generated | source removed |\n",
        )
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[assertion-removed] tests/test_é.py:2", err)
        self.assertNotIn("[silenced-checker]", err)


class ParseDiffTest(unittest.TestCase):
    def test_quoted_paths_are_unescaped_and_strip_trailing_tabs(self) -> None:
        diff = (
            'diff --git "a/tests/test_\\303\\251.py" "b/src \\303\\251.py"\n'
            '--- "a/tests/test_\\303\\251.py"\t\n'
            '+++ "b/src \\303\\251.py"\t\n'
            "@@ -4,1 +4,1 @@\n"
            "-    assert True\n"
            "+    pass\n"
        )
        added, removed = floor_guard.parse_diff(diff)
        self.assertEqual(removed, [floor_guard.Line("tests/test_é.py", 4, "    assert True")])
        self.assertEqual(added, [floor_guard.Line("src é.py", 4, "    pass")])

    def test_removed_line_starting_with_dashes_is_content(self) -> None:
        diff = (
            "diff --git a/q.sql b/q.sql\n"
            "index 1..2 100644\n"
            "--- a/q.sql\n"
            "+++ b/q.sql\n"
            "@@ -3,1 +3,1 @@\n"
            "--- old comment\n"
            "+++ new comment\n"
        )
        added, removed = floor_guard.parse_diff(diff)
        self.assertEqual(removed, [floor_guard.Line("q.sql", 3, "-- old comment")])
        self.assertEqual(added, [floor_guard.Line("q.sql", 3, "++ new comment")])


if __name__ == "__main__":
    unittest.main()
