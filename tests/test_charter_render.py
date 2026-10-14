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
            subprocess.run([*git, "commit", "-q", "-m", subject], check=True, stdin=subprocess.DEVNULL)
        self.base, self.head = subprocess.run(
            [*git, "rev-parse", "HEAD~1", "HEAD"], check=True, capture_output=True, text=True,
            stdin=subprocess.DEVNULL,
        ).stdout.split()
        self.staffing = self.run_dir / "staffing.txt"
        self.write_staffing("MODE: solo-Lead\nLEAD: kind=claude model=claude-opus-5-5 workspace=w7\n")

    def write_staffing(self, seats: str) -> None:
        self.staffing.write_text(
            f"{seats}HEAD: {self.head}\nREVIEWER: review-x kind=claude model=m posture=allowlisted "
            "dialog=absent dialog-tools=none dialog-deny=none dialog-source=inventory skills=none "
            f"extensions=none fence=none(test) pane=w7:p3 workspace=w7 head={self.head}\n",
            encoding="utf-8",
        )

    def render(self, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = charter_render.main([
                "--repo", str(self.repo), "--run-dir", str(self.run_dir), "--base", self.base,
                "--head", self.head, "--pane", "w7:p3", "--lane", "normal", "--reason", "new script",
                "--boundary", "b.py exists", "--validation", "G1", "--check", "git diff --check",
                "--staffing", str(self.staffing),
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
            f"Scope authors (staffing record): {LEAD} (claude claude-opus-5-5).",
            f"Governing contracts: {self.repo}/AGENTS.md, {self.repo}/é/AGENTS.md;",
            "pane w7:p3, workspace w7.",
            "1. git diff --check",
            f"`python3 {SCRIPTS / 'bounded_run.py'} --seconds N -- CMD`",
        ):
            self.assertIn(expected, text)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as lint_err:
            lint = charter_lint.main([
                "--charter", str(charter), "--lead", LEAD, "--staffing", str(self.staffing), "--repo", str(self.repo),
            ])
        self.assertEqual((lint, lint_err.getvalue()), (0, ""))

    def merge_main(self, land: bool) -> str:
        """Merge a later main commit into the head; origin/HEAD is origin/main. Returns the merge."""
        git = lambda *a: subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=t", "-c",
                                         "user.email=t@example.com", *a], check=True, capture_output=True,
                                        text=True, stdin=subprocess.DEVNULL).stdout.strip()
        bare = self.repo.parent / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True, stdin=subprocess.DEVNULL)
        git("remote", "add", "origin", str(bare))
        git("checkout", "-q", "-b", "trunk", self.base)
        (self.repo / "main.txt").write_text("main\n", encoding="utf-8")
        git("add", "main.txt")
        git("commit", "-q", "-m", "main")
        git("push", "-q", "origin", f"{self.base if not land else 'HEAD'}:refs/heads/main")
        git("fetch", "-q", "origin")
        git("remote", "set-head", "origin", "main")
        git("checkout", "-q", "-B", "work", self.head)
        git("merge", "-q", "--no-edit", "trunk")
        return git("rev-parse", "HEAD")

    def partitioned(self, owned: str) -> None:
        self.write_staffing(
            "MODE: partitioned\nLEAD: kind=claude model=claude-opus-5-5 workspace=w7\n"
            f"ENGINEER: eng-a kind=claude model=claude-haiku-5-5 posture=bypassed pane=w7:p4 owned={owned} extensions=none\n"
            "ENGINEER: eng-b kind=pi model=luna posture=bypassed pane=w7:p5 owned=docs/ extensions=none\n"
        )

    def test_partitioned_authors_are_the_engineers_owning_the_changed_paths(self):
        self.partitioned("é/")
        code, _, err = self.render()
        self.assertEqual((code, err), (0, ""))
        text = (self.run_dir / f"charter-review-{self.head[:12]}.md").read_text(encoding="utf-8")
        self.assertIn("Mode: partitioned. Declared source scope: é/AGENTS.md, é/b.py. "
                      "Scope authors (staffing record): eng-a (claude claude-haiku-5-5).", text)

    def test_a_changed_path_with_no_engineer_owner_is_refused(self):
        self.partitioned("é/b.py")
        code, _, err = self.render()
        self.assertEqual(code, 1)
        self.assertIn("é/AGENTS.md has no ENGINEER owner", err)

    def test_a_staffing_record_without_a_mode_is_refused(self):
        self.write_staffing("LEAD: kind=claude model=claude-opus-5-5 workspace=w7\n")
        code, _, err = self.render()
        self.assertEqual(code, 1)
        self.assertIn("has no MODE: solo-Lead or MODE: partitioned line", err)

    def test_a_clean_merge_of_landed_main_leaves_main_out_of_the_scope(self):
        self.partitioned("é/")
        head = self.merge_main(land=True)
        code, _, err = self.render("--head", head)
        self.assertEqual((code, err), (0, ""))
        text = (self.run_dir / f"charter-review-{head[:12]}.md").read_text(encoding="utf-8")
        self.assertIn("Declared source scope: é/AGENTS.md, é/b.py.", text)

    def test_an_unlanded_main_commit_needs_an_owner(self):
        self.partitioned("é/")
        code, _, err = self.render("--head", self.merge_main(land=False))
        self.assertEqual(code, 1)
        self.assertIn("main.txt has no ENGINEER owner", err)

    def test_a_conflict_resolving_merge_owner_checks_its_own_content(self):
        git = lambda *a: subprocess.run(["git", "-C", str(self.repo), "-c", "user.name=t", "-c",
                                         "user.email=t@example.com", *a], capture_output=True, text=True,
                                        stdin=subprocess.DEVNULL)
        git("checkout", "-q", "-b", "side", self.head)
        (self.repo / "é" / "b.py").write_text("side\n", encoding="utf-8")
        git("commit", "-q", "-am", "side")
        git("checkout", "-q", "-B", "work", self.head)
        (self.repo / "é" / "b.py").write_text("work\n", encoding="utf-8")
        git("commit", "-q", "-am", "work")
        self.assertNotEqual(git("merge", "-q", "side").returncode, 0)
        (self.repo / "é" / "b.py").write_text("resolved\n", encoding="utf-8")
        (self.repo / "evil.txt").write_text("evil\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "merge side")
        self.partitioned("é/")
        code, _, err = self.render("--head", git("rev-parse", "HEAD").stdout.strip())
        self.assertEqual(code, 1)
        self.assertIn("evil.txt has no ENGINEER owner", err)

    def test_a_lead_line_without_kind_and_model_is_refused(self):
        self.write_staffing("MODE: solo-Lead\nLEAD: workspace=w7\n")
        code, _, err = self.render()
        self.assertEqual(code, 1)
        self.assertIn("LEAD line lacks kind= or model=", err)

    def test_refuses_an_abbreviated_head(self):
        code, _, err = self.render("--head", self.head[:12])
        self.assertEqual(code, 1)
        self.assertIn("--head must be the full 40-hex SHA", err)


if __name__ == "__main__":
    unittest.main()
