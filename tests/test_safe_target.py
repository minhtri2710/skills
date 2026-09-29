#!/usr/bin/env python3
"""Tests for the destructive-path guard."""
from __future__ import annotations

import io
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "destructive-path-guard" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import safe_target  # noqa: E402


class SafeTargetTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name).resolve()
        self.root = base / "sessions"
        self.outside = base / "elsewhere"
        (self.root / "abc123").mkdir(parents=True)
        self.outside.mkdir()
        (self.root / "abc123" / ".owner").write_text("worker-7\n")

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def resolve(self, candidate: Path, **kwargs: object) -> Path:
        return safe_target.resolve_target(candidate, [str(self.root)], **kwargs)  # type: ignore[arg-type]

    def test_child_of_root_is_accepted(self) -> None:
        self.assertEqual(self.resolve(self.root / "abc123"), self.root / "abc123")

    def test_root_itself_is_refused(self) -> None:
        with self.assertRaises(safe_target.Refused):
            self.resolve(self.root)

    def test_path_outside_root_is_refused(self) -> None:
        with self.assertRaises(safe_target.Refused):
            self.resolve(self.outside)

    def test_traversal_out_of_root_is_refused(self) -> None:
        with self.assertRaises(safe_target.Refused):
            self.resolve(self.root / "abc123" / ".." / ".." / "elsewhere")

    def test_symlink_escaping_the_root_is_refused(self) -> None:
        link = self.root / "escape"
        link.symlink_to(self.outside)
        with self.assertRaises(safe_target.Refused):
            self.resolve(link)

    def test_in_root_symlink_is_printed_as_the_link(self) -> None:
        pointee = self.root / "abc123" / "object"
        pointee.mkdir()
        link = self.root / "abc123" / "link"
        link.symlink_to(pointee)
        code, out, _ = self.run_cli(str(link), "--root", str(self.root))
        self.assertEqual((code, out.strip()), (0, str(link)))

    def test_dangling_in_root_symlink_is_printed_as_the_link(self) -> None:
        link = self.root / "abc123" / "dangling"
        link.symlink_to(self.root / "abc123" / "not-created")
        code, out, _ = self.run_cli(str(link), "--root", str(self.root))
        self.assertEqual((code, out.strip()), (0, str(link)))

    def test_target_equal_to_a_root_is_refused_even_with_a_parent_root(self) -> None:
        nested = self.root / "abc123"
        code, out, err = self.run_cli(
            str(nested), "--root", str(nested), "--root", str(self.root)
        )
        self.assertEqual((code, out), (1, ""))
        self.assertIn("target is or contains", err)

    def test_target_containing_a_listed_root_is_refused(self) -> None:
        nested = self.root / "a" / "b"
        nested.mkdir(parents=True)
        target = self.root / "a"
        with self.assertRaisesRegex(safe_target.Refused, "target is or contains"):
            safe_target.resolve_target(target, [str(self.root), str(nested)])

    def test_depth_uses_the_nearest_containing_root(self) -> None:
        nested = self.root / "a"
        nested.mkdir()
        target = nested / "x"
        target.mkdir()
        with self.assertRaises(safe_target.Refused):
            safe_target.resolve_target(target, [str(self.root), str(nested)], min_depth=2)

    def test_symlink_owner_evidence_is_read_from_its_parent(self) -> None:
        pointee = self.root / "abc123" / "object"
        pointee.mkdir()
        link = self.root / "abc123" / "link"
        link.symlink_to(pointee)
        self.assertEqual(
            safe_target.resolve_target(
                link,
                [str(self.root)],
                owner_file=".owner",
                expect_owner="worker-7",
            ),
            link,
        )

    def test_sibling_named_like_traversal_is_accepted(self) -> None:
        sneaky = self.root / "..cache"
        sneaky.mkdir()
        self.assertEqual(self.resolve(sneaky), sneaky)

    def test_min_depth_rejects_a_shallow_target(self) -> None:
        with self.assertRaises(safe_target.Refused):
            self.resolve(self.root / "abc123", min_depth=2)

    def test_min_depth_below_one_cannot_be_checked(self) -> None:
        with self.assertRaises(safe_target.CannotCheck):
            self.resolve(self.root / "abc123", min_depth=0)

    def test_owner_evidence_is_never_read_from_the_root(self) -> None:
        (self.root / ".owner").write_text("worker-7\n")
        with self.assertRaises(safe_target.Refused):
            self.resolve(self.root / "gone", owner_file=".owner", expect_owner="worker-7")

    def test_missing_target_is_checked_through_its_parent(self) -> None:
        target = self.root / "abc123" / "not-created-yet"
        self.assertEqual(self.resolve(target), target)

    def test_missing_parent_cannot_be_checked(self) -> None:
        with self.assertRaises(safe_target.CannotCheck):
            self.resolve(self.root / "gone" / "child")

    def test_matching_owner_evidence_is_accepted(self) -> None:
        target = self.root / "abc123"
        self.assertEqual(self.resolve(target, owner_file=".owner", expect_owner="worker-7"), target)

    def test_wrong_owner_evidence_is_refused(self) -> None:
        with self.assertRaises(safe_target.Refused):
            self.resolve(self.root / "abc123", owner_file=".owner", expect_owner="worker-8")

    def test_absent_owner_evidence_is_refused(self) -> None:
        (self.root / "def456").mkdir()
        with self.assertRaises(safe_target.Refused):
            self.resolve(self.root / "def456", owner_file=".owner", expect_owner="worker-7")

    def test_unresolvable_root_cannot_be_checked(self) -> None:
        with self.assertRaises(safe_target.CannotCheck):
            safe_target.resolve_target(self.root / "abc123", [str(self.outside / "missing")])

    def run_cli(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = safe_target.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_cli_prints_the_resolved_target_on_acceptance(self) -> None:
        code, out, _ = self.run_cli(str(self.root / "abc123"), "--root", str(self.root))
        self.assertEqual(code, 0)
        self.assertEqual(out.strip(), str(self.root / "abc123"))

    def test_cli_refusal_exits_1_and_names_the_target(self) -> None:
        code, out, err = self.run_cli(str(self.outside), "--root", str(self.root))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("refusing", err)

    def test_cli_rejects_min_depth_below_one(self) -> None:
        with self.assertRaises(SystemExit) as ctx, redirect_stderr(io.StringIO()):
            safe_target.main([str(self.root / "abc123"), "--root", str(self.root), "--min-depth", "0"])
        self.assertEqual(ctx.exception.code, 2)

    def test_cli_unresolvable_root_exits_2(self) -> None:
        code, _, err = self.run_cli(str(self.root / "abc123"), "--root", str(self.outside / "missing"))
        self.assertEqual(code, 2)
        self.assertIn("cannot check", err)


if __name__ == "__main__":
    unittest.main()
