#!/usr/bin/env python3
from __future__ import annotations

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

import support
import floor_guard

SCRIPTS = support.ROOT / "skills" / "quality-floor" / "scripts"


def setUpModule() -> None:
    support.never_run("git", sys.executable)


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
        self.repo = support.temp_git_repo(Path(self._tmp.name))
        self.write("src/app.py", "def total(items):\n    return sum(items)\n")
        self.write(
            "tests/test_app.py",
            "from app import total\n\n\ndef test_total():\n    assert total([1, 2]) == 3\n    assert total([]) == 0\n",
        )
        self.write("tests/test_old.py", "def test_old():\n    assert True\n")
        self.write("CONSTRAINTS.md", CONSTRAINTS)
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "base")

    def tearDown(self) -> None:
        self._tmp.cleanup()

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

    def test_non_ascii_untracked_violation_is_reported_under_legacy_locale(self) -> None:
        self.write("src/new_é.py", "def later():\n    pass  # TODO\n")
        proc = support.run_in_locale(
            "en_US.ISO8859-1",
            "import sys; sys.path.insert(0, sys.argv[1]); import floor_guard; sys.exit(floor_guard.main(sys.argv[2:]))",
            str(SCRIPTS), "--base", "main", "--repo", str(self.repo),
        )
        self.assertEqual(proc.returncode, 1, proc.stderr)
        self.assertIn(
            "[unfinished-work] src/new_é.py:2".encode("iso8859-1"), proc.stderr
        )

    def test_non_utf8_content_in_a_changed_file_is_scanned(self) -> None:
        legacy = self.repo / "src" / "legacy.py"
        legacy.write_bytes(b"caf\xe9 = 1\n")
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "legacy")
        legacy.write_bytes(b"caf\xe9 = 1  # noqa\n")
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [silenced-checker] src/legacy.py:1\n"))

    def test_non_utf8_text_in_an_untracked_file_is_scanned(self) -> None:
        (self.repo / "src" / "legacy.py").write_bytes(b"caf\xe9 = 1  # noqa\n")
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [silenced-checker] src/legacy.py:1\n"))

    def test_untracked_binary_file_is_skipped(self) -> None:
        (self.repo / "src" / "blob.py").write_bytes(b"\0\xff\n x = 1  # noqa\n")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_external_diff_driver_does_not_hide_a_tracked_change(self) -> None:
        support.git(self.repo, "config", "diff.external", "true")
        self.write("src/app.py", "def total(items):\n    return sum(items)  # noqa\n")
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [silenced-checker] src/app.py:2\n"))

    def test_noprefix_diff_config_does_not_empty_the_paths(self) -> None:
        self.write("pyproject.toml", "[tool.coverage.report]\nfail_under = 80\n")
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "coverage")
        support.git(self.repo, "config", "diff.noprefix", "true")
        self.write("pyproject.toml", "[tool.coverage.report]\nfail_under = 70\n")
        self.write("src/app.py", "def total(items):\n    return sum(items)  # noqa\n")
        self.assertEqual(
            self.run_guard(),
            (1, "floor-guard: 2 violation(s)\n  [silenced-checker] src/app.py:2\n  [threshold-loosened] pyproject.toml:2\n"),
        )

    def test_textconv_driver_does_not_hide_a_tracked_change(self) -> None:
        (self.repo / ".git" / "info" / "attributes").write_text("*.py diff=hide\n")
        support.git(self.repo, "config", "diff.hide.textconv", "true")
        self.write("src/app.py", "def total(items):\n    return sum(items)  # noqa\n")
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [silenced-checker] src/app.py:2\n"))

    def test_inter_hunk_context_config_does_not_fuse_hunks(self) -> None:
        ruff = '[tool.ruff.lint]\nselect = [\n  "E",\n]\nignore = [\n  "E501",\n]\n'
        self.write("pyproject.toml", ruff)
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "ruff")
        support.git(self.repo, "config", "diff.interHunkContext", "3")
        self.write("pyproject.toml", ruff.replace('  "E",\n', '  "E",\n  "F",\n').replace('  "E501",\n', '  "E501",\n  "E402",\n'))
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [lint-rule-disabled] pyproject.toml:8\n"))

    def test_big_file_threshold_does_not_hide_a_tracked_change(self) -> None:
        support.git(self.repo, "config", "core.bigFileThreshold", "1")
        self.write("src/app.py", "def total(items):\n    return sum(items)  # noqa\n")
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [silenced-checker] src/app.py:2\n"))

    def test_diff_attribute_does_not_hide_a_tracked_change(self) -> None:
        (self.repo / ".git" / "info" / "attributes").write_text("*.py -diff\n")
        self.write("src/app.py", "def total(items):\n    return sum(items)  # noqa\n")
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [silenced-checker] src/app.py:2\n"))

    def test_tracked_binary_file_is_skipped(self) -> None:
        blob = self.repo / "src" / "blob.py"
        blob.write_bytes(b"\0\xff\n")
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "blob")
        blob.write_bytes(b"\0\xff\nx = 1  # noqa\n")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_tracked_file_that_was_binary_at_the_base_is_skipped(self) -> None:
        blob = self.repo / "src" / "blob.py"
        blob.write_bytes(b"\0\xff\n")
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "blob")
        blob.write_bytes(b"x = 1  # noqa\n")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_binary_base_renamed_to_a_text_file_is_skipped(self) -> None:
        old, new = self.repo / "src" / "blob.py", self.repo / "src" / "moved.py"
        old.write_bytes(b"\0" + b"a" * 62 + b"\n" + (b"a" * 63 + b"\n") * 30)
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "blob")
        support.git(self.repo, "mv", "src/blob.py", "src/moved.py")
        new.write_bytes(b"b" * 63 + b"\n" + (b"a" * 63 + b"\n") * 30 + b"x = 1  # noqa\n")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_text_base_renamed_to_a_binary_file_is_skipped(self) -> None:
        old, new = self.repo / "tests" / "test_text.py", self.repo / "tests" / "test_moved.py"
        old.write_bytes(b"b" * 63 + b"\n" + (b"a" * 63 + b"\n") * 30 + b"assert x\n")
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "text")
        support.git(self.repo, "mv", "tests/test_text.py", "tests/test_moved.py")
        new.write_bytes(b"\0" + b"a" * 62 + b"\n" + (b"a" * 63 + b"\n") * 30)
        self.assertEqual(self.run_guard(), (0, ""))

    def test_tracked_file_replaced_by_a_symlink_to_a_binary_file_is_not_read_through(self) -> None:
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / "data.bin"
        target.write_bytes(b"\0\xff\n")
        (self.repo / "tests" / "test_old.py").unlink()
        (self.repo / "tests" / "test_old.py").symlink_to(target)
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [assertion-removed] tests/test_old.py:2\n"))

    def test_untracked_symlink_is_skipped(self) -> None:
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / "elsewhere.py"
        target.write_text("x = 1  # noqa\n")
        (self.repo / "src" / "link.py").symlink_to(target)
        self.assertEqual(self.run_guard(), (0, ""))

    def test_moved_submodule_pointer_is_not_read_as_a_blob(self) -> None:
        support.git(self.repo, "update-index", "--add", "--cacheinfo", "160000," + "1" * 40 + ",sub")
        support.git(self.repo, "commit", "-q", "-m", "submodule")
        support.git(self.repo, "update-index", "--add", "--cacheinfo", "160000," + "1" * 40 + ",moved")
        support.git(self.repo, "rm", "-q", "--cached", "sub")
        (self.repo / "moved").mkdir()
        self.assertEqual(self.run_guard(), (0, ""))

    def test_untracked_symlink_at_a_deleted_path_does_not_hide_its_removed_lines(self) -> None:
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)
        target = Path(outside.name) / "data.bin"
        target.write_bytes(b"\0\xff\n")
        self.write("pyproject.toml", "[tool.coverage.report]\nfail_under = 80\n")
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "coverage")
        support.git(self.repo, "rm", "-q", "--cached", "pyproject.toml")
        (self.repo / "pyproject.toml").unlink()
        (self.repo / "pyproject.toml").symlink_to(target)
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [threshold-loosened] pyproject.toml:2\n"))

    def test_tracked_crlf_file_is_flagged_at_the_right_line(self) -> None:
        crlf = self.repo / "src" / "crlf.py"
        crlf.write_bytes(b"a = 1\r\nb = 2\r\n")
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "crlf")
        crlf.write_bytes(b"a = 1\r\nb = 2  # noqa\r\n")
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [silenced-checker] src/crlf.py:2\n"))

    def test_removed_submodule_pointer_is_not_read_as_a_blob(self) -> None:
        support.git(self.repo, "update-index", "--add", "--cacheinfo", "160000," + "1" * 40 + ",sub")
        support.git(self.repo, "commit", "-q", "-m", "submodule")
        support.git(self.repo, "rm", "-q", "--cached", "sub")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_touched_tracked_file_with_unchanged_content_is_clean(self) -> None:
        os.utime(self.repo / "src" / "app.py", (1_000_000_000, 1_000_000_000))
        self.assertEqual(self.run_guard(), (0, ""))

    def test_non_utf8_content_of_a_watched_file_renamed_away_is_read(self) -> None:
        cfg = (self.repo / "pkg" / "setup.cfg")
        cfg.parent.mkdir()
        cfg.write_bytes(b"[metadata]\nauthor = Ren\xe9\n[report]\nfail_under = 80\n")
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "legacy config")
        support.git(self.repo, "mv", "pkg/setup.cfg", "pkg/setup.cfg.old")
        (self.repo / "pkg" / "setup.cfg.old").write_bytes(b"[metadata]\nauthor = Ren\xe9\n[report]\nfail_under = 70\n")
        self.assertEqual(self.run_guard(), (1, "floor-guard: 1 violation(s)\n  [threshold-loosened] pkg/setup.cfg:4\n"))

    def test_non_utf8_constraints_file_still_parses_its_exception_rows(self) -> None:
        self.write("src/new.py", "def later():\n    raise NotImplementedError\n")
        row = "| E1 | unfinished-work | src/*.py | port of caf\xe9 | port lands |\n"
        (self.repo / "CONSTRAINTS.md").write_bytes((CONSTRAINTS + row).encode("latin-1"))
        self.assertEqual(self.run_guard(), (0, ""))

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
        self.write(
            "CONSTRAINTS.md",
            CONSTRAINTS
            + "| E1 | unfinished-work | src/*.py | port in progress | port lands |\n"
            + "| E2 | silenced-checker | lib/*.py | vendor types | upstream ships types |\n",
        )
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertNotIn("[unfinished-work] src/new.py:2", err)
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
        support.git(self.repo, "mv", "tests/test_old.py", "tests/test_older.py")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_renamed_test_file_is_not_a_deletion_when_the_repo_disables_rename_detection(self) -> None:
        support.git(self.repo, "config", "diff.renames", "false")
        support.git(self.repo, "mv", "tests/test_old.py", "tests/test_older.py")
        self.assertEqual(self.run_guard(), (0, ""))

    def test_a_renamed_file_with_an_edited_watched_line_is_compared_with_its_old_path(self) -> None:
        eslint = '{\n  "name": "demo",\n  "rules": {\n    "no-console": "off",\n    "eqeqeq": "error"\n  }\n}\n'
        cfg = "[metadata]\nname = demo\nversion = 1\nauthor = a\n[report]\nfail_under = 80\n"
        self.write("pkg/.eslintrc.json", eslint)
        self.write("pkg/setup.cfg", cfg)
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "configs")
        for old, new in (("tests/test_app.py", "tests/test_apps.py"), ("pkg/.eslintrc.json", "app/.eslintrc.json"),
                         ("pkg/setup.cfg", "app/setup.cfg")):
            (self.repo / new).parent.mkdir(exist_ok=True)
            support.git(self.repo, "mv", old, new)
        self.write("tests/test_apps.py", (self.repo / "tests/test_apps.py").read_text().replace("== 0", "== 0, 'empty'"))
        self.write("app/.eslintrc.json", eslint.replace('"no-console": "off"', '"no-console": 0'))
        self.write("app/setup.cfg", cfg.replace("= 80", "= 80.0"))
        self.assertEqual(self.run_guard(), (0, ""))

    def test_constraints_renamed_out_of_its_name_is_flagged_as_removed(self) -> None:
        (self.repo / "docs").mkdir()
        support.git(self.repo, "mv", "CONSTRAINTS.md", "docs/floor.md")
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[floor-rule-removed] CONSTRAINTS.md:5", err)
        self.assertIn("[constraint-removed] CONSTRAINTS.md:13", err)

    def test_a_coverage_config_renamed_out_of_its_name_with_a_lower_threshold_is_flagged(self) -> None:
        cfg = "[metadata]\nname = demo\nversion = 1\nauthor = a\n[report]\nfail_under = 80\n"
        self.commit_then_edit("pkg/setup.cfg", cfg, cfg)
        support.git(self.repo, "mv", "pkg/setup.cfg", "pkg/setup.cfg.old")
        self.write("pkg/setup.cfg.old", cfg.replace("= 80", "= 70"))
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[threshold-loosened] pkg/setup.cfg:6", err)

    def test_test_file_renamed_out_of_a_test_path_is_a_deletion(self) -> None:
        support.git(self.repo, "mv", "tests/test_old.py", "src/old.py")
        code, err = self.run_guard()
        self.assertEqual(code, 1)
        self.assertIn("[test-deleted] tests/test_old.py", err)
        self.assertNotIn("assertion-removed", err)

    def test_runtime_skip_and_focus_forms_are_flagged_and_lookalikes_are_not(self) -> None:
        rows = [
            ("def test_a(self):\n    self.skipTest('x')\n", "[test-made-easier] tests/test_new.py:2"),
            ("def test_a():\n    pytest.skip('x')\n", "[test-made-easier] tests/test_new.py:2"),
            ("pytestmark = pytest.mark.skip(reason='x')\n", "[test-made-easier] tests/test_new.py:1"),
            ("pytestmark = [pytest.mark.skipif(True, reason='x'), pytest.mark.xfail]\n", "[test-made-easier] tests/test_new.py:1"),
            ("fit('x', () => {})\n", "[test-made-easier] tests/test_new.py:1"),
            ("fdescribe('x', () => {})\n", "[test-made-easier] tests/test_new.py:1"),
            ("func TestA(t *testing.T) {\n\tt.SkipNow()\n}\n", "[test-made-easier] tests/test_new.py:2"),
            ("total = profit(1) + outfit(2)\n", None),
            ("score = model.fit(x)\n", None),
            ("def fit(self):\n    return self\n", None),
            ("pytestmark = pytest.mark.usefixtures('db')\n", None),
        ]
        for text, expected in rows:
            with self.subTest(text=text):
                self.write("tests/test_new.py", text)
                code, err = self.run_guard()
                if expected is None:
                    self.assertEqual((code, err), (0, ""))
                else:
                    self.assertEqual(code, 1)
                    self.assertIn(expected, err)

    def commit_then_edit(self, name: str, before: str, after: str) -> None:
        self.write(name, before)
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "--allow-empty", "-m", "config")
        self.write(name, after)

    def assert_config_rows(self, rows: list[tuple[str, str, str, str | None]]) -> None:
        for name, before, after, expected in rows:
            with self.subTest(name=name, after=after):
                self.commit_then_edit(name, before, after)
                code, err = self.run_guard()
                if expected is None:
                    self.assertEqual((code, err), (0, ""))
                else:
                    self.assertEqual(code, 1)
                    self.assertIn(expected, err)
                support.git(self.repo, "reset", "-q", "--hard")

    def test_loosened_coverage_thresholds_in_tool_configs_are_flagged(self) -> None:
        loose = "[threshold-loosened] "
        report = "[report]\nfail_under = 80\n"
        addopts = "[pytest]\naddopts = --cov --cov-fail-under=80\n"
        jest = "module.exports = {\n  coverageThreshold: {\n    global: { branches: 80, lines: 80 },\n  },\n};\n"
        self.assert_config_rows([
            ("pyproject.toml", "[tool.coverage.report]\nfail_under = 80\n", "[tool.coverage.report]\nfail_under = 70\n", loose + "pyproject.toml:2"),
            ("pyproject.toml", "[tool.coverage.report]\nfail_under = 80\n", "[tool.coverage.report]\n", loose + "pyproject.toml:2"),
            ("setup.cfg", report, report.replace("80", "79.5"), loose + "setup.cfg:2"),
            (".coveragerc", report, report.replace("80", "0"), loose + ".coveragerc:2"),
            ("tox.ini", report, "[report]\n", loose + "tox.ini:2"),
            ("tox.ini", addopts, addopts.replace("=80", "=70"), loose + "tox.ini:2"),
            ("tox.ini", addopts, "[pytest]\naddopts = --cov\n", loose + "tox.ini:2"),
            ("jest.config.js", jest, jest.replace("branches: 80", "branches: 70"), loose + "jest.config.js:3"),
            ("jest.config.js", jest, "module.exports = {\n};\n", loose + "jest.config.js:3"),
            ("package.json", '{\n  "jest": {\n    "coverageThreshold": {\n      "global": {\n        "lines": 80\n      }\n    }\n  }\n}\n',
             '{\n  "jest": {\n    "coverageThreshold": {\n      "global": {\n        "lines": 60\n      }\n    }\n  }\n}\n', loose + "package.json:5"),
            ("pyproject.toml", "[tool.coverage.report]\nfail_under = 80\n", "[tool.coverage.report]\nfail_under = 90\n", None),
            ("tox.ini", addopts, addopts.replace("=80", "=95"), None),
            ("jest.config.js", jest, jest.replace("branches: 80", "branches: 90"), None),
        ])

    def test_disabled_lint_rules_in_tool_configs_are_flagged(self) -> None:
        off = "[lint-rule-disabled] "
        eslint = '{\n  "rules": {\n    "eqeqeq": "error"\n  }\n}\n'
        ruff = '[tool.ruff.lint]\nselect = [\n  "E",\n]\nignore = [\n  "E501",\n]\n'
        self.assert_config_rows([
            (".eslintrc.json", eslint, eslint.replace('"error"', '"off"'), off + ".eslintrc.json:3"),
            (".eslintrc.json", eslint, eslint.replace('"error"', "0"), off + ".eslintrc.json:3"),
            (".eslintrc.json", eslint, eslint.replace('"error"', '["off"]'), off + ".eslintrc.json:3"),
            ("eslint.config.js", "export default [{ rules: { eqeqeq: 'error' } }];\n",
             "export default [{ rules: { eqeqeq: 'off' } }];\n", off + "eslint.config.js:1"),
            (".eslintrc.json", eslint.replace('"error"', '"off"'), eslint, None),
            ("pyproject.toml", ruff, ruff.replace('  "E501",\n', '  "E501",\n  "E402",\n'), off + "pyproject.toml:7"),
            ("pyproject.toml", ruff, ruff.replace('  "E501",\n', '  "E501",\n  "E402",\n').replace("ignore = [", "extend-ignore = ["), off + "pyproject.toml:7"),
            ("ruff.toml", 'ignore = ["E501"]\n', 'ignore = ["E501", "E402"]\n', off + "ruff.toml:1"),
            ("ruff.toml", 'lint.select = ["E"]\n', 'lint.select = ["E"]\nextend-ignore = ["E402"]\n', off + "ruff.toml:2"),
            ("pyproject.toml", ruff, ruff.replace('  "E",\n', '  "E",\n  "F",\n'), None),
            ("pyproject.toml", ruff, ruff.replace('  "E501",\n', ""), None),
            ("ruff.toml", 'ignore = ["E501", "E402"]\n', 'ignore = ["E402", "E501"]\n', None),
            ("ruff.toml", 'ignore = ["E501"]\n', "ignore = []\n", None),
        ])

    def test_unresolvable_base_exits_2(self) -> None:
        code, err = self.run_guard(base="does-not-exist")
        self.assertEqual(code, 2)
        self.assertIn("cannot run", err)

    def test_non_ascii_and_spaced_paths_drive_findings_and_exceptions(self) -> None:
        self.write("tests/test_é.py", "def test_non_ascii():\n    assert True\n")
        self.write("src é.py", "value = 1\n")
        support.git(self.repo, "add", ".")
        support.git(self.repo, "commit", "-q", "-m", "non-ascii")
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
    def test_quoted_paths_are_unescaped_and_unquoted_paths_lose_their_trailing_tab(self) -> None:
        diff = (
            'diff --git "a/we\\"ird.py" "b/we\\"ird.py"\n'
            'index 422c2b7..7898192 100644\n'
            '--- "a/we\\"ird.py"\n'
            '+++ "b/we\\"ird.py"\n'
            "@@ -2 +1,0 @@\n"
            "-b\n"
            'diff --git "a/back\\\\slash.py" "b/back\\\\slash.py"\n'
            'index 587be6b..975fbec 100644\n'
            '--- "a/back\\\\slash.py"\n'
            '+++ "b/back\\\\slash.py"\n'
            "@@ -1 +1 @@\n"
            "-x\n"
            "+y\n"
            'diff --git "a/ctl\\001.py" "b/ctl\\001.py"\n'
            "index 587be6b..975fbec 100644\n"
            '--- "a/ctl\\001.py"\n'
            '+++ "b/ctl\\001.py"\n'
            "@@ -1 +1 @@\n"
            "-x\n"
            "+y\n"
            'diff --git "a/tab\\there.py" "b/tab\\there.py"\n'
            "index 422c2b7..7898192 100644\n"
            '--- "a/tab\\there.py"\n'
            '+++ "b/tab\\there.py"\n'
            "@@ -2 +1,0 @@ a\n"
            "-b\n"
            "diff --git a/sp ace.py b/sp ace.py\n"
            "index 1..2 100644\n"
            "--- a/sp ace.py\t\n"
            "+++ b/sp ace.py\t\n"
            "@@ -1 +1 @@\n"
            "-p\n"
            "+q\n"
        )
        added, removed = floor_guard.parse_diff(diff)
        self.assertEqual(
            removed,
            [
                floor_guard.Line('we"ird.py', 2, "b"),
                floor_guard.Line("back\\slash.py", 1, "x"),
                floor_guard.Line("ctl\x01.py", 1, "x"),
                floor_guard.Line("tab\there.py", 2, "b"),
                floor_guard.Line("sp ace.py", 1, "p"),
            ],
        )
        self.assertEqual(
            added,
            [
                floor_guard.Line("back\\slash.py", 1, "y"),
                floor_guard.Line("ctl\x01.py", 1, "y"),
                floor_guard.Line("sp ace.py", 1, "q"),
            ],
        )

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

    def test_context_lines_advance_both_line_numbers(self) -> None:
        diff = (
            "diff --git a/pyproject.toml b/pyproject.toml\n"
            "index 1..2 100644\n"
            "--- a/pyproject.toml\n"
            "+++ b/pyproject.toml\n"
            "@@ -2,5 +2,5 @@\n"
            " keep\n"
            "-old\n"
            "+new\n"
            " \n"
            " keep\n"
            "-gone\n"
            "+here\n"
        )
        added, removed = floor_guard.parse_diff(diff)
        self.assertEqual(
            removed,
            [floor_guard.Line("pyproject.toml", 3, "old"), floor_guard.Line("pyproject.toml", 6, "gone")],
        )
        self.assertEqual(
            added,
            [floor_guard.Line("pyproject.toml", 3, "new"), floor_guard.Line("pyproject.toml", 6, "here")],
        )

    def test_empty_line_in_a_hunk_is_a_context_line(self) -> None:
        diff = (
            "diff --git a/pyproject.toml b/pyproject.toml\n"
            "index 1..2 100644\n"
            "--- a/pyproject.toml\n"
            "+++ b/pyproject.toml\n"
            "@@ -2,4 +2,4 @@\n"
            " keep\n"
            "\n"
            "-old\n"
            "+new\n"
        )
        added, removed = floor_guard.parse_diff(diff)
        self.assertEqual(removed, [floor_guard.Line("pyproject.toml", 4, "old")])
        self.assertEqual(added, [floor_guard.Line("pyproject.toml", 4, "new")])

    def test_only_a_line_feed_ends_a_patch_line(self) -> None:
        diff = (
            "diff --git a/f.py b/f.py\n"
            "index 1..2 100644\n"
            "--- a/f.py\n"
            "+++ b/f.py\n"
            "@@ -1,0 +1,2 @@\n"
            "+a\x0cb\x85c\n"
            "+d\n"
        )
        added, removed = floor_guard.parse_diff(diff)
        self.assertEqual(added, [floor_guard.Line("f.py", 1, "a\x0cb\x85c"), floor_guard.Line("f.py", 2, "d")])
        self.assertEqual(removed, [])


if __name__ == "__main__":
    unittest.main()
