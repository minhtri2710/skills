#!/usr/bin/env python3
"""Unit tests for gate_row.py (C19 — the ledger row is derived, not typed)."""
from __future__ import annotations

import contextlib
import io
import re
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
        """Run the CLI with its stdout and stderr captured, so a test run stays readable.

        stderr is kept on `self.err`: a refusal that exits 1 for the wrong reason
        is still a passing exit code, so the message is part of the assertion.
        """
        self.err = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(self.err):
            return gate_row.main(argv)

    def append(self, *extra: str) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--note", "merged the reviewed head", "--quote", "merge it", *extra,
        ])

    def git(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, text=True, check=True).stdout.strip()

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
            gate_row.check(row, self.repo, ["f1.txt", "f2.txt"])
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
            gate_row.check(row, self.repo, [])
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

    def test_a_path_added_and_deleted_inside_the_range_is_still_named(self):
        """S1 F002's own reproduction. The two end trees agree; the union does not.

        This is the one input where a net `diff --name-only <base>..<head>` and the
        doctrine's `rev-list | diff-tree` union disagree, and it disagrees in the
        direction that lets an out-of-boundary write through clean.
        """
        base = self.rev("HEAD")
        (self.repo / "src").mkdir()
        (self.repo / "src" / "out-of-boundary.py").write_text("x\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "add outside the boundary")
        self.git("rm", "-q", "src/out-of-boundary.py")
        self.git("commit", "-qm", "delete it again")

        net = self.git("diff", "--name-only", f"{base}..HEAD")
        self.assertEqual(net, "", "the net tree diff must be empty, or this case proves nothing")

        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", base,
                                     "--boundary", "docs"), 0)
        row = self.last_row()
        self.assertIn("count=2", row)
        self.assertIn('boundary-check="src/out-of-boundary.py"', row)

    def test_a_boundary_flag_holding_several_joined_paths_is_refused(self):
        """The shape three ledgers actually wrote: one --boundary holding a joined list.

        `--boundary` is `action="append"`, one flag per path, so a joined value is a
        single string no path can equal or sit under. Every changed path then reads
        as outside the boundary and the row is indistinguishable from one that
        declared no boundary at all — which is why it fails closed here instead.
        """
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt f2.txt"), 1)

    def test_a_changed_path_holding_a_space_is_refused(self):
        """boundary-check joins paths with spaces, so such a path cannot be read back."""
        base = self.rev("HEAD")
        (self.repo / "two words.txt").write_text("x\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "a path with a space")
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", base,
                                     "--boundary", "docs"), 1)

    def valid_push_row(self) -> tuple[str, list[str]]:
        """One push row the script built itself, with the boundary it was built against."""
        boundary = ["f1.txt", "f2.txt"]
        self.add_remote("HEAD")
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", self.rev("HEAD~2"),
            "--channel", "supervisor-relay:typed", "--writer", "lead-beo-skills",
            *[a for b in boundary for a in ("--boundary", b)]), 0)
        return self.last_row(), boundary

    def test_the_control_row_still_checks_out(self):
        """The matrix below only means something if the unmodified row passes."""
        row, boundary = self.valid_push_row()
        gate_row.check(row, self.repo, boundary)

    def test_every_tamper_the_receive_record_found_passing_is_now_refused(self):
        """S1 F001's six-of-six matrix: one field hand-edited at a time, re-checked."""
        row, boundary = self.valid_push_row()
        tampers = {
            "boundary-check": ('boundary-check=""', 'boundary-check="src/fabricated.py"'),
            "record": ("record=timely", "record=bogus"),
            "quote": ('quote="merge it"', 'quote=""'),
            "branch": ("main@", "nonexistent-branch@"),
            "channel": ("channel=supervisor-relay:typed", "channel=bogus:bogus"),
            "writer": ("writer=lead-beo-skills", "writer=NOT_A_SEAT"),
        }
        for name, (before, after) in tampers.items():
            with self.subTest(name):
                tampered = row.replace(before, after)
                self.assertNotEqual(tampered, row, "the tamper did not change the row")
                with self.assertRaises(gate_row.RowError):
                    gate_row.check(tampered, self.repo, boundary)

    def test_check_refuses_a_push_row_when_no_boundary_was_declared(self):
        """The refusal is a guard, because the comparison alone fails open.

        An empty boundary puts every touched path outside it, so the derivation
        reproduces the whole changed set in sorted order. That refuses a row
        claiming `""` but accepts one claiming everything — see
        `test_a_row_over_claiming_the_whole_changed_set_is_refused`. So the
        missing argument has to be refused outright, not derived against.
        """
        _, boundary = self.valid_push_row()
        argv = ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]
        self.assertEqual(self.run_main(argv), 1)
        self.assertIn("no boundary was declared", self.err.getvalue())
        self.assertEqual(
            self.run_main(argv + [a for b in boundary for a in ("--boundary", b)]), 0)

    def test_a_row_over_claiming_the_whole_changed_set_is_refused(self):
        """The shape six rows across two ledgers already carry.

        `--boundary` is `action="append"`, one flag per path; a seat that passes
        all its paths joined in a single flag declares one string no path can
        match, so every path lands outside and the row records the entire
        changed set. That row asserts a breach that did not happen, and against
        an empty boundary the derivation reproduces it exactly.
        """
        row, boundary = self.valid_push_row()
        p = re.search(r'boundary-check="([^"]*)"', row)
        self.assertEqual(p.group(1), "", "the control row declares no breach")
        base = self.rev("HEAD~2")
        changed = sorted({
            path
            for commit in self.git("rev-list", f"{base}..HEAD").splitlines()
            for path in self.git("diff-tree", "--root", "-m", "--no-commit-id",
                                 "--name-only", "-r", commit).splitlines()
            if path
        })
        self.assertTrue(set(boundary) & set(changed), "the range touches the boundary")
        over = row.replace('boundary-check=""', f'boundary-check="{" ".join(changed)}"')
        self.assertNotEqual(over, row)
        self.ledger.write_text(over + "\n")
        argv = ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]
        self.assertEqual(self.run_main(argv), 1)
        self.assertEqual(
            self.run_main(argv + [a for b in boundary for a in ("--boundary", b)]), 1)
        self.assertIn("outside the declared boundary", self.err.getvalue())


if __name__ == "__main__":
    unittest.main()
