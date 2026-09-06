#!/usr/bin/env python3
"""Unit tests for gate_row.py (C19 — the ledger row is derived, not typed)."""
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import gate_row  # noqa: E402


def make_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    repo.mkdir()
    run = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True,
                                    capture_output=True, text=True)
    run("init", "-q", "-b", "main")
    run("config", "user.email", "t@example.invalid")
    run("config", "user.name", "t")
    for n in range(3):
        (repo / f"f{n}.txt").write_text(f"{n}\n")
        run("add", "-A")
        run("commit", "-qm", f"c{n}")
    return repo


class GateRowTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.repo = make_repo(self.tmp)
        self.ledger = self.tmp / "gates.md"
        self.ledger.write_text("# Gate ledger — test\n\n")
        self.addCleanup(self._tmp.cleanup)

    def run_main(self, argv: list[str]) -> int:
        """Run the CLI with its stdout and stderr captured, so a test run stays readable."""
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return gate_row.main(argv)

    def append(self, *extra: str) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--note", "merged the reviewed head", "--quote", "merge it", *extra,
        ])

    def rev(self, ref: str) -> str:
        return subprocess.run(["git", "-C", str(self.repo), "rev-parse", ref],
                              capture_output=True, text=True, check=True).stdout.strip()

    def last_row(self) -> str:
        return [l for l in self.ledger.read_text().splitlines()
                if gate_row.ID_RE.match(l)][-1]

    def test_round_trip(self):
        """A row the script writes is a row --check accepts, unchanged."""
        self.assertEqual(self.append(), 0)
        written = self.last_row()
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)
        self.assertEqual(self.last_row(), written)

    def test_ids_are_consecutive_and_read_from_the_file(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        ids = [l.split(" | ")[0] for l in self.ledger.read_text().splitlines()
               if gate_row.ID_RE.match(l)]
        self.assertEqual(ids, ["G1", "G2"])

    def test_a_count_that_does_not_match_the_range_is_rejected(self):
        """The recount rule as code: parts that do not sum fail --check."""
        base, head = self.rev("HEAD~2"), self.rev("HEAD")
        row = (f'G9 | 2026-09-06T00:00:00Z | kind=push | main@{head} | '
               f'status=resolved:standing-waiver | record=timely | '
               f'push={base}..{head} count=7 boundary-check="" | note=n | quote="q"')
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(row, self.repo)
        self.assertIn("carries 2 commits", str(ctx.exception))

    def test_a_pipe_in_note_is_refused(self):
        """note= is the seat's own words, so it fails closed on the delimiter."""
        self.assertEqual(self.append("--note", "a | b"), 1)

    def test_a_pipe_in_quote_is_kept_verbatim(self):
        """G33: the Human typed a literal | inside their own words (G52)."""
        human = "à cho các lead revert lại model từ abc-tunnel về cliproxy gpt luna|zai/glm 5.3 flash đi"
        self.assertEqual(self.append("--quote", human), 0)
        self.assertTrue(self.last_row().endswith(f'quote="{human}"'))
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)

    def test_narrative_over_the_cap_is_refused(self):
        self.assertEqual(self.append("--note", "x" * (gate_row.NOTE_MAX + 1)), 1)

    def test_an_undocumented_key_is_refused(self):
        """The drifted shape this project actually wrote must not pass."""
        head = self.rev("HEAD")
        row = (f'G9 | 2026-09-06T00:00:00Z | kind=push | main@{head} | '
               f'status=resolved:standing-waiver | authority=G64 | project=beo-skills | '
               f'record=timely | note=n | quote="q"')
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(row, self.repo)
        self.assertIn("not in the row schema", str(ctx.exception))

    def add_remote(self, ref: str) -> None:
        """A bare origin holding `ref`, so ls-remote answers for real."""
        bare = self.tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "origin", str(bare)],
                       check=True)
        subprocess.run(["git", "-C", str(self.repo), "push", "-q", "origin",
                        f"{self.rev(ref)}:refs/heads/main"], check=True, capture_output=True)

    def test_a_push_row_whose_push_has_not_landed_is_refused(self):
        """origin is a commit behind, so the row would claim a push that did not happen."""
        self.add_remote("HEAD~1")
        base = self.rev("HEAD~2")
        self.assertEqual(self.append("--kind", "push", "--push-base", base), 1)

    def test_a_landed_push_derives_its_own_count_and_boundary(self):
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt", "--boundary", "f2.txt"), 0)
        row = self.last_row()
        self.assertIn("count=2", row)
        self.assertIn('boundary-check=""', row)

    def test_a_path_outside_the_boundary_is_named(self):
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt"), 0)
        self.assertIn('boundary-check="f2.txt"', self.last_row())


if __name__ == "__main__":
    unittest.main()
