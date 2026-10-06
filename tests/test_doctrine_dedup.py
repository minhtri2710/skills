#!/usr/bin/env python3
"""Doctrine dedup lint: repeated rule text has one owner file.

The herdr-delivery-workflow doctrine requires that a rule's text live in
exactly one loaded file; any other file cites it by section rather than
restating it. This measures that invariant: no rule-bearing sentence (>=8
words, code blocks stripped) may appear verbatim in more than one loaded prose
file. Templates are verbatim record shapes, so they are excluded. Each loaded
file also stays within its byte ceiling, so doctrine that every seat loads cannot
grow without the Human's word.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow"

# Prose files a seat loads on some route, each with its byte ceiling. Templates are
# excluded for the reason in the module docstring. Ceilings only fall. A diff that
# adds bytes to a file cuts as many bytes from that same file. A diff that shrinks a
# file lowers that file's ceiling to its new size. Raising a ceiling needs the
# Human's own words, cited by ledger row id in the commit message.
BUDGET = {
    "SKILL.md": 10_308,
    "references/lead.md": 98_942,
    "references/relaunch.md": 3_779,
    "references/herdr-cli.md": 21_588,
    "references/project-config.md": 6_196,
    "references/structural-misfit-policy.md": 8_497,
    "references/charters.md": 40_134,
    "references/closeout.md": 12_263,
    "references/supervisor.md": 24_303,
}


def _sentences(path: Path) -> list[str]:
    text = re.sub(r"```.*?```", " ", path.read_text(), flags=re.DOTALL)
    text = re.sub(r"\s+", " ", text)
    out = []
    for raw in re.split(r"(?<=[.:;])\s+", text):
        s = raw.strip(" -*|#").strip()
        if len(s.split()) >= 8:
            out.append(re.sub(r"[^a-z0-9 ]", "", s.lower()).strip())
    return out


class DoctrineDedupTest(unittest.TestCase):
    def test_no_rule_text_duplicated_across_loaded_files(self):
        owners: dict[str, set[str]] = {}
        for name in BUDGET:
            path = SKILL / name
            self.assertTrue(path.exists(), f"loaded doctrine file missing: {name}")
            for sent in _sentences(path):
                owners.setdefault(sent, set()).add(name)
        dupes = {s: sorted(f) for s, f in owners.items() if len(f) > 1}
        self.assertEqual(
            dupes,
            {},
            "rule text appears in more than one loaded file; the non-owner must cite "
            f"by section instead of restating:\n" + "\n".join(
                f"  {files}: {sent[:120]}" for sent, files in dupes.items()
            ),
        )

    def test_lead_commit_message_contract_preserves_custody(self):
        lead = (SKILL / "references/lead.md").read_text()
        commit_step = next(
            line for line in lead.splitlines()
            if line.startswith("3. In partitioned mode")
        )
        for requirement in (
            "subject `type(scope): what changed`",
            "at most 72 characters",
            "gate IDs, Human quotes, task names, and test counts",
            "optional short body for why",
            "`Seat: <seat name>` and `Model: <kind> <model>` trailers",
            "provenance belongs in the ledger and `runs/`",
            "`git add -- <owned paths>`; never `git add -A` or `git commit -a`",
            "Let every hook finish uninterrupted",
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, commit_step)

    def test_loaded_files_stay_within_byte_budget(self):
        over = {
            name: (size, cap)
            for name, cap in BUDGET.items()
            if (size := len((SKILL / name).read_bytes())) > cap
        }
        self.assertEqual(
            over,
            {},
            "loaded doctrine over its byte ceiling (size, ceiling); cut as many bytes "
            "from the same file, or cite the Human's words for a raise",
        )


if __name__ == "__main__":
    unittest.main()
