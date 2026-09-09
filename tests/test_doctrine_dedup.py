#!/usr/bin/env python3
"""Doctrine dedup eval (slice C): every rule has exactly one owner file.

The role-restructured herdr-delivery-workflow doctrine requires that a rule's
text live in exactly one loaded file; any other file cites it by section rather
than restating it. This measures that invariant: no rule-bearing sentence
(>=8 words, code blocks stripped) may appear verbatim in more than one loaded
prose file. Templates are verbatim record shapes, and RATIONALE.md restates
rule gist by design, so both are excluded.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow"

# Prose files a seat loads on some route. Templates and RATIONALE.md are excluded
# for the reasons in the module docstring.
LOADED = [
    "SKILL.md",
    "references/lead.md",
    "references/relaunch.md",
    "references/herdr-cli.md",
    "references/project-config.md",
    "references/structural-misfit-policy.md",
    "references/charters.md",
    "references/closeout.md",
    "references/supervisor.md",
]


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
        for name in LOADED:
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


if __name__ == "__main__":
    unittest.main()
