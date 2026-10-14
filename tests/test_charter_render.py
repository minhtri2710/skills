"""charter_render fills the Reviewer charter template from one Lead command line."""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import charter_lint
import charter_render

LEAD = "lead-demo"


class CharterRenderTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.repo = root / "repo"
        self.run_dir = root / ".herdr" / "projects" / "demo" / "runs" / "demo-run"
        self.run_dir.mkdir(parents=True)
        (self.run_dir.parents[1] / "config.json").write_text(json.dumps({
            "lead-kind": "claude", "lead-args": ["--model", "claude-opus-5-5"],
            "reviewer-kind": "claude", "reviewer-args": ["--model", "claude-sonnet-5-5"],
            "target-line": "main",
        }), encoding="utf-8")
        (self.run_dir / "evidence-x.log").write_text("Ran 1 OK\n", encoding="utf-8")
        git = ["git", "-C", str(self.repo), "-c", "user.name=t", "-c", "user.email=t@example.com"]
        self.repo.mkdir()
        subprocess.run([*git, "init", "-q"], check=True, stdin=subprocess.DEVNULL)
        for names, subject in ((("AGENTS.md",), "docs: guidance"), (("é/AGENTS.md", "é/b.py"), "feat(é): add b")):
            for name in names:
                (self.repo / name).parent.mkdir(exist_ok=True)
                (self.repo / name).write_text("x\n", encoding="utf-8")
            subprocess.run([*git, "add", *names], check=True, stdin=subprocess.DEVNULL)
            subprocess.run(
                [*git, "commit", "-q", "-m", subject, "--trailer", f"Seat: {LEAD}",
                 "--trailer", "Model: claude claude-opus-5-5"],
                check=True, stdin=subprocess.DEVNULL,
            )
        self.base, self.head = subprocess.run(
            [*git, "rev-parse", "HEAD~1", "HEAD"], check=True, capture_output=True, text=True,
            stdin=subprocess.DEVNULL,
        ).stdout.split()

    def render(self, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = charter_render.main([
                "--repo", str(self.repo), "--run-dir", str(self.run_dir), "--base", self.base,
                "--head", self.head, "--pane", "w7:p3", "--lane", "normal", "--reason", "new script",
                "--boundary", "b.py exists", "--validation", "G1", "--check", "git diff --check",
                *extra,
            ])
        return code, out.getvalue(), err.getvalue()

    def test_rendered_charter_passes_charter_lint(self):
        code, out, err = self.render()
        self.assertEqual((code, err), (0, ""))
        charter = self.run_dir / f"charter-review-{self.head[:12]}.md"
        self.assertTrue(out.startswith(f"{charter} sha256="))
        text = charter.read_text(encoding="utf-8")
        for expected in (
            f"Reviewed unit: the range {self.base}..{self.head} (1 commit: {self.head[:7]}).",
            "Mode: solo-Lead. Declared source scope: é/AGENTS.md, é/b.py.",
            f"Scope authors (commit trailers): {LEAD} (claude claude-opus-5-5).",
            f"Governing contracts: {self.repo}/AGENTS.md, {self.repo}/é/AGENTS.md;",
            "pane w7:p3, workspace w7.",
            "1. git diff --check",
            f"`python3 {SCRIPTS / 'bounded_run.py'} --seconds N -- CMD`",
        ):
            self.assertIn(expected, text)
        staffing = self.run_dir / "staffing.txt"
        staffing.write_text(
            f"MODE: solo-Lead\nHEAD: {self.head}\nREVIEWER: review-x kind=claude model=m posture=allowlisted "
            "dialog=absent dialog-tools=none dialog-deny=none dialog-source=inventory skills=none "
            f"extensions=none fence=none(test) pane=w7:p3 workspace=w7 head={self.head}\n",
            encoding="utf-8",
        )
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as lint_err:
            lint = charter_lint.main([
                "--charter", str(charter), "--lead", LEAD, "--staffing", str(staffing), "--repo", str(self.repo),
            ])
        self.assertEqual((lint, lint_err.getvalue()), (0, ""))

    def merge_untrailered_main(self, land: bool) -> str:
        """Merge a trailer-less main commit into the head; origin/HEAD is origin/main. Returns the merge."""
        git = lambda *a: subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=t", "-c",
                                         "user.email=t@example.com", *a], check=True, capture_output=True,
                                        text=True, stdin=subprocess.DEVNULL).stdout.strip()
        bare = self.repo.parent / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True, stdin=subprocess.DEVNULL)
        git("remote", "add", "origin", str(bare))
        git("checkout", "-q", "-b", "trunk", self.base)
        (self.repo / "main.txt").write_text("main\n", encoding="utf-8")
        git("add", "main.txt")
        git("commit", "-q", "-m", "main without trailers")
        git("push", "-q", "origin", f"{self.base if not land else 'HEAD'}:refs/heads/main")
        git("fetch", "-q", "origin")
        git("remote", "set-head", "origin", "main")
        git("checkout", "-q", "-B", "work", self.head)
        git("merge", "-q", "--no-edit", "trunk")
        return git("rev-parse", "HEAD")

    def test_a_clean_merge_of_landed_main_needs_no_trailers(self):
        code, _, err = self.render("--head", self.merge_untrailered_main(land=True))
        self.assertEqual((code, err), (0, ""))
        charter = next(self.run_dir.glob("charter-review-*.md")).read_text(encoding="utf-8")
        self.assertIn("Mode: solo-Lead.", charter)

    def test_an_unlanded_untrailered_commit_is_refused(self):
        code, _, err = self.render("--head", self.merge_untrailered_main(land=False))
        self.assertEqual(code, 1)
        self.assertIn("lacks a Seat: or Model: trailer", err)

    def test_refuses_an_abbreviated_head(self):
        code, _, err = self.render("--head", self.head[:12])
        self.assertEqual(code, 1)
        self.assertIn("--head must be the full 40-hex SHA", err)


if __name__ == "__main__":
    unittest.main()
