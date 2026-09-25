"""The Reviewer charter template carries every clause charter_lint requires of a Reviewer."""
from __future__ import annotations

import ast
import contextlib
import inspect
import io
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow"
sys.path.insert(0, str(SKILL / "scripts"))

import charter_lint  # noqa: E402

TEMPLATE = SKILL / "templates" / "reviewer-charter.txt"
REPORT_BLOCK = SKILL / "templates" / "report-by-prompt.txt"
LEAD = "lead-beo-skills"
SLOT_RE = re.compile(r"<([a-z][a-z0-9_]*)>")
NOT_CLAUSES = {"SEAT_RE", "PLACEHOLDER_RE", "RANGE_RE", "STAFFED_HEAD_RE"}


def staffing(head: str) -> str:
    return (
        "MODE: solo-Lead\n"
        "LEAD: kind=claude model=claude-opus-5-5 workspace=w1\n"
        f"HEAD: {head}\n"
        "REVIEWER: review-aaaaaaaaaaaa kind=claude model=claude-opus-5-5 posture=allowlisted "
        f"dialog=denied skills=none extensions=none pane=w1:p1 workspace=w1 head={head}\n"
    )


def fill(text: str, base: str, head: str) -> str:
    values = {"head_sha": head, "base_sha": base, "lead_name": LEAD, "peer_name": "review-aaaaaaaaaaaa"}
    return SLOT_RE.sub(lambda m: values.get(m.group(1), f"filled-{m.group(1)}"), text)


def lint_patterns() -> dict[str, re.Pattern[str]]:
    patterns = {}
    for name, value in vars(charter_lint).items():
        if name in NOT_CLAUSES:
            continue
        if isinstance(value, re.Pattern):
            patterns[name] = value
        elif isinstance(value, tuple) and value and all(isinstance(v, re.Pattern) for v in value):
            patterns.update({f"{name}[{i}]": v for i, v in enumerate(value)})
    return patterns


def lint_literals() -> list[str]:
    """String clauses _charter_problems tests with `"..." not in text`."""
    tree = ast.parse(inspect.getsource(charter_lint._charter_problems))
    literals = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and isinstance(node.ops[0], ast.NotIn):
            left = node.left
            if isinstance(left, ast.Constant):
                literals.append(left.value)
            elif isinstance(left, ast.JoinedStr):
                literals.append(
                    "".join(v.value if isinstance(v, ast.Constant) else LEAD for v in left.values)
                )
    return literals


class ReviewerCharterTemplateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._repo_tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        cls.repo = Path(cls._repo_tmp.name)
        cls.addClassCleanup(cls._repo_tmp.cleanup)
        git = ["git", "-C", str(cls.repo), "-c", "user.name=t", "-c", "user.email=t@example.com"]
        subprocess.run([*git, "init", "-q"], check=True)
        for message in ("base", "head"):
            subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", message], check=True)
        cls.base, cls.head = subprocess.run(
            [*git, "rev-parse", "HEAD~1", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.split()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.filled = fill(TEMPLATE.read_text(encoding="utf-8"), self.base, self.head)

    def run_lint(self, charter: str) -> tuple[int, str]:
        charter_path = self.tmp / "charter.md"
        staffing_path = self.tmp / "staffing.txt"
        charter_path.write_text(charter, encoding="utf-8")
        staffing_path.write_text(staffing(self.head), encoding="utf-8")
        stderr = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            rc = charter_lint.main(
                ["--charter", str(charter_path), "--lead", LEAD, "--staffing", str(staffing_path),
                 "--repo", str(self.repo)]
            )
        return rc, stderr.getvalue()

    def test_placeholders_are_snake_case_and_all_filled(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        self.assertEqual(
            charter_lint.PLACEHOLDER_RE.findall(text), [m.group(0) for m in SLOT_RE.finditer(text)]
        )
        self.assertIsNone(charter_lint.PLACEHOLDER_RE.search(self.filled))

    def test_report_block_matches_report_by_prompt_template(self):
        block = REPORT_BLOCK.read_text(encoding="utf-8").strip()
        block = block.replace("<run-dir>", "<run_dir>").replace("<peer-name>", "<peer_name>")
        block = block.replace("<lead-name>", "<lead_name>")
        self.assertIn(block, TEMPLATE.read_text(encoding="utf-8"))

    def test_filled_template_lints_ok(self):
        self.assertEqual(self.run_lint(self.filled), (0, ""))

    def test_clause_set_is_derived_from_charter_lint(self):
        self.assertGreaterEqual(len(lint_patterns()), 7)
        self.assertIn(f"herdr agent prompt {LEAD}", lint_literals())
        self.assertIn("SEND-FAILED", lint_literals())

    def test_removing_any_required_clause_fails_naming_it(self):
        clauses = [(name, lambda t, p=p: p.sub("", t)) for name, p in lint_patterns().items()]
        clauses += [(lit, lambda t, s=lit: t.replace(s, "")) for lit in lint_literals()]
        for name, remove in clauses:
            with self.subTest(clause=name):
                stripped = remove(self.filled)
                self.assertNotEqual(stripped, self.filled, f"template lacks {name}")
                rc, err = self.run_lint(stripped)
                self.assertEqual(rc, 1)
                problems = err.strip().splitlines()
                self.assertEqual(len(problems), 1, err)
                self.assertTrue(problems[0].startswith("charter_lint: missing "), err)


if __name__ == "__main__":
    unittest.main()
