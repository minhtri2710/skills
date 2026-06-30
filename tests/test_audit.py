#!/usr/bin/env python3
"""Unit tests for beo_audit.py (G4 — drift detection)."""
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-reference"
SCRIPTS = REFERENCE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


class AuditDriftDetectionTest(unittest.TestCase):
    def test_audit_imports(self):
        """beo_audit should import without error and expose key check functions."""
        import beo_audit
        self.assertTrue(hasattr(beo_audit, "check_transition_coverage"))
        self.assertTrue(hasattr(beo_audit, "check_reference_existence"))
        self.assertTrue(hasattr(beo_audit, "check_must_not_violations"))
        self.assertTrue(hasattr(beo_audit, "check_runtime_event_kinds"))

    def test_check_transition_coverage_runs_against_current_repo(self):
        """Transition coverage check should run without crashing on the current repo."""
        import beo_audit
        repo_root = Path(__file__).resolve().parents[1]
        pipeline = beo_audit.load_json_registry(repo_root, "pipeline.json")
        skill_cards = beo_audit.load_skill_cards(repo_root)
        emits_by_skill = {
            name: beo_audit.extract_emit_identifiers(text)
            for name, text in skill_cards.items()
        }
        findings = beo_audit.check_transition_coverage(pipeline, emits_by_skill)
        self.assertIsInstance(findings, list)
        for finding in findings:
            self.assertTrue(hasattr(finding, "severity"))
            self.assertTrue(hasattr(finding, "check_id"))
            self.assertTrue(hasattr(finding, "message"))

    def test_check_transition_coverage_emits_finding_for_unknown_condition(self):
        """A condition_id in pipeline that is not in any skill card Emit should produce a finding."""
        import beo_audit
        synthetic_pipeline = {
            "transitions": [
                {"from": "beo-plan", "condition_id": "not_a_real_condition", "to": "beo-validate"},
            ],
        }
        findings = beo_audit.check_transition_coverage(synthetic_pipeline, {})
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding.check_id, "C1")
        self.assertEqual(finding.severity, beo_audit.SEVERITY_CRITICAL)
        self.assertIn("not_a_real_condition", finding.message)

    def test_check_runtime_event_kinds_runs(self):
        """Runtime event kind consistency check should run without crashing."""
        import beo_audit
        repo_root = Path(__file__).resolve().parents[1]
        events_schema = beo_audit.load_json_registry(repo_root, "runtime-event.schema.json")
        findings = beo_audit.check_runtime_event_kinds(events_schema, repo_root)
        self.assertIsInstance(findings, list)

    def test_check_must_not_violations_runs(self):
        """must_not violation check should run without crashing."""
        import beo_audit
        repo_root = Path(__file__).resolve().parents[1]
        phase_contracts = beo_audit.load_json_registry(repo_root, "phase-contracts.json")
        skill_cards = beo_audit.load_skill_cards(repo_root)
        findings = beo_audit.check_must_not_violations(phase_contracts, skill_cards)
        self.assertIsInstance(findings, list)

    def test_c3_fallback_lowercases_unknown_token(self):
        """A token absent from _MUST_NOT_KEYWORDS must still match case-insensitively.

        The fallback derives keywords from the token via replace('_',' ').
        write_blob is lowercased by extract_write_bullets, so the fallback
        must also lowercase or uppercase tokens silently miss violations.
        """
        import beo_audit
        phase_contracts = {
            "skills": {
                "beo-test": {"must_not": ["Modify_REGISTRY_FileS"]},
            },
        }
        skill_cards = {
            "beo-test": "# Test\n\n## Write\n\n- modify registry files here\n",
        }
        findings = beo_audit.check_must_not_violations(phase_contracts, skill_cards)
        c3 = [f for f in findings if f.check_id == "C3"]
        self.assertEqual(len(c3), 1)
        self.assertIn("Modify_REGISTRY_FileS", c3[0].message)

    def test_extract_emit_identifiers_finds_known_conditions(self):
        """Extract emit identifiers should find conditions in a SKILL.md Emit section."""
        import beo_audit
        text = """# Test skill

## Emit

- `verdict_accept` -> close accepted work
- `repair_same_scope` -> beo-validate
- `harness_change_needed` -> beo-author
"""
        ids = beo_audit.extract_emit_identifiers(text)
        self.assertIn("verdict_accept", ids)
        self.assertIn("repair_same_scope", ids)
        self.assertIn("harness_change_needed", ids)

    def test_string_root_is_accepted(self) -> None:
        """Programmatic callers may pass a string root; functions must coerce to Path."""
        import beo_audit
        root_str = str(Path(__file__).resolve().parents[1])
        pipeline = beo_audit.load_json_registry(root_str, "pipeline.json")
        self.assertIsInstance(pipeline, dict)
        findings, checks = beo_audit.run_audit(root_str, check_manifest=False)
        self.assertIsInstance(findings, list)
        self.assertIsInstance(checks, list)


class MustNotCoverageTest(unittest.TestCase):
    """Tests for C8 — must_not Never-section coverage drift detection."""

    def test_c8_current_repo_has_no_drift(self):
        """Baseline guard: current repo Never sections cover all registry must_not tokens.

        If this fails, either a registry must_not token was added without
        updating the skill card Never prose (real drift), or the stem-word
        matcher needs widening. Investigate each finding before adjusting.
        """
        import beo_audit
        repo_root = Path(__file__).resolve().parents[1]
        phase_contracts = beo_audit.load_json_registry(repo_root, "phase-contracts.json")
        skill_cards = beo_audit.load_skill_cards(repo_root)
        findings = beo_audit.check_must_not_coverage(phase_contracts, skill_cards)
        self.assertEqual(
            findings, [],
            f"C8 drift detected: {[f.message for f in findings]}",
        )

    def test_c8_flags_token_missing_from_never_section(self):
        """A registry must_not token absent from Never prose must produce a C8 warning."""
        import beo_audit
        phase_contracts = {
            "skills": {
                "beo-test": {
                    "must_not": ["mutate_product_files", "grant_PASS_EXECUTE", "totally_new_constraint"],
                },
            },
        }
        skill_cards = {
            "beo-test": "# Test\n\n## Never\n\n- Do not mutate product files.\n- Do not grant PASS_EXECUTE.\n",
        }
        findings = beo_audit.check_must_not_coverage(phase_contracts, skill_cards)
        c8 = [f for f in findings if f.check_id == "C8"]
        self.assertEqual(len(c8), 1)
        self.assertEqual(c8[0].severity, beo_audit.SEVERITY_WARNING)
        self.assertIn("totally_new_constraint", c8[0].message)

    def test_c8_no_findings_when_tokens_covered_in_never(self):
        """Tokens whose stems appear in Never prose must not produce findings."""
        import beo_audit
        phase_contracts = {
            "skills": {
                "beo-test": {
                    "must_not": ["mutate_product_files", "close", "review"],
                },
            },
        }
        skill_cards = {
            "beo-test": "# Test\n\n## Never\n\n- Do not mutate product files.\n- Do not review or close work.\n",
        }
        findings = beo_audit.check_must_not_coverage(phase_contracts, skill_cards)
        self.assertEqual(findings, [])

    def test_c8_ignores_canonical_cite_line_vocabulary(self):
        """The Binding cite line's own words must not falsely cover a token.

        The cite line ("- Binding: phase-contracts.json ... (audit C8)") sits
        inside the Never section. Its words (canonical, phase, audit, prose)
        must not satisfy stem coverage for an unrelated token, or real drift
        would be masked.
        """
        import beo_audit
        phase_contracts = {
            "skills": {
                "beo-test": {"must_not": ["audit_logs"]},
            },
        }
        skill_cards = {
            "beo-test": (
                "# Test\n\n## Never\n\n"
                "- Binding: `phase-contracts.json` `must_not[]` is canonical; "
                "prose below mirrors it (audit C8).\n"
                "- Do not mutate product files.\n"
            ),
        }
        findings = beo_audit.check_must_not_coverage(phase_contracts, skill_cards)
        c8 = [f for f in findings if f.check_id == "C8"]
        self.assertEqual(len(c8), 1)
        self.assertIn("audit_logs", c8[0].message)

    def test_c8_word_boundary_not_substring(self):
        """Substring inside an unrelated word must not satisfy coverage.

        Stem 'store' must not be covered by prose containing 'restore';
        stem 'approve' must not be covered by 'approved'. Without
        word-boundary anchoring these would mask real drift.
        """
        import beo_audit
        phase_contracts = {
            "skills": {"beo-test": {"must_not": ["store_secrets", "approve"]}},
        }
        skill_cards = {
            "beo-test": "# Test\n\n## Never\n\n- Do not restore data.\n- Only approved scope may be mutated.\n",
        }
        findings = beo_audit.check_must_not_coverage(phase_contracts, skill_cards)
        c8 = [f for f in findings if f.check_id == "C8"]
        self.assertEqual(len(c8), 2)
        flagged = {f.message.split("'")[1] for f in c8}
        self.assertEqual(flagged, {"store_secrets", "approve"})

    def test_c8_flags_token_with_no_significant_stems(self):
        """A token whose words are all <=3 chars must be flagged as unverifiable.

        Stem matching can't verify such a token (e.g. 'act'), so it must
        not be silently skipped — a human needs to see it. This closes
        the blind spot where drift would go invisible.
        """
        import beo_audit
        phase_contracts = {"skills": {"beo-test": {"must_not": ["act"]}}}
        skill_cards = {"beo-test": "# Test\n\n## Never\n\n- do not act.\n"}
        findings = beo_audit.check_must_not_coverage(phase_contracts, skill_cards)
        c8 = [f for f in findings if f.check_id == "C8"]
        self.assertEqual(len(c8), 1)
        self.assertIn("act", c8[0].message)
        self.assertIn("unverifiable", c8[0].message)

    def test_c8_flags_when_never_section_absent(self):
        """A skill with must_not but no Never section must flag every token."""
        import beo_audit
        phase_contracts = {
            "skills": {
                "beo-test": {"must_not": ["mutate_product_files", "close"]},
            },
        }
        skill_cards = {"beo-test": "# Test\n\n## Write\n\n- nothing relevant\n"}
        findings = beo_audit.check_must_not_coverage(phase_contracts, skill_cards)
        self.assertEqual(len(findings), 2)


class ManifestRegexTest(unittest.TestCase):
    """Tests for _manifest_script_names regex robustness."""

    def test_manifest_regex_bare_name(self):
        """A bare script name like 'beo_foo.py' must be found."""
        import beo_audit
        manifest = """| `beo_foo.py` | `--issue <id>` | Foo | json | 0, 1 |"""
        unplanned, planned = beo_audit._manifest_script_names(manifest)
        self.assertIn("beo_foo.py", unplanned)

    def test_manifest_regex_scripts_prefix(self):
        """A scripts/ prefixed name like 'scripts/beo_foo.py' must be found."""
        import beo_audit
        manifest = """| `scripts/beo_foo.py` | `--issue <id>` | Foo | json | 0, 1 |"""
        unplanned, planned = beo_audit._manifest_script_names(manifest)
        self.assertIn("beo_foo.py", unplanned)

    def test_manifest_regex_full_path(self):
        """A full path like 'skills/beo/beo-reference/scripts/beo_foo.py' must be found."""
        import beo_audit
        manifest = """| `skills/beo/beo-reference/scripts/beo_foo.py` | `--issue <id>` | Foo | json | 0, 1 |"""
        unplanned, planned = beo_audit._manifest_script_names(manifest)
        self.assertIn("beo_foo.py", unplanned)

    def test_manifest_regex_planned(self):
        """A [planned] entry must be tracked separately from unplanned."""
        import beo_audit
        manifest = """| `beo_planned.py` [planned] | `--issue <id>` | Planned | json | 0, 1 |"""
        unplanned, planned = beo_audit._manifest_script_names(manifest)
        self.assertNotIn("beo_planned.py", unplanned)
        self.assertIn("beo_planned.py", planned)


class ScoreContextClassifyTest(unittest.TestCase):
    """Tests for beo_score_context._classify path handling."""

    def _classify(self, path: str) -> str | None:
        import beo_score_context
        return beo_score_context._classify(path)

    def test_classify_ticket_with_leading_dot(self):
        """A path like '.beads/artifacts/br-123/TICKET.json' must be classified as 'ticket'."""
        result = self._classify(".beads/artifacts/br-123/TICKET.json")
        self.assertEqual(result, "ticket")

    def test_classify_ticket_with_absolute_prefix(self):
        """A path like '/repo/.beads/artifacts/br-123/TICKET.json' must be classified as 'ticket'."""
        result = self._classify("/repo/.beads/artifacts/br-123/TICKET.json")
        self.assertEqual(result, "ticket")


class HarnessProposalTargetTest(unittest.TestCase):
    """Tests for C6 — harness proposal target scope enforcement."""

    def _make_proposal(self, root: Path, target: str, issue_id: str = "br-test") -> Path:
        """Create a harness-proposal.json under .beads/artifacts/ and return its path."""
        import json
        proposal_dir = root / ".beads" / "artifacts" / issue_id
        proposal_dir.mkdir(parents=True, exist_ok=True)
        proposal_path = proposal_dir / "harness-proposal.json"
        with open(proposal_path, "w") as f:
            json.dump({
                "version": 1,
                "proposal_id": f"prop-{issue_id[-8:]}",
                "source_issue_id": issue_id,
                "target": target,
                "change_type": "improvement",
                "rationale": "test",
                "proposed_diff": "test",
                "safety_note": "test",
            }, f, indent=2)
        return proposal_path

    def test_c6_accepts_valid_target(self):
        """A target under skills/beo/ must not produce a finding."""
        import beo_audit
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_proposal(root, "skills/beo/beo-foo/SKILL.md")
            findings = beo_audit.check_harness_proposal_targets(root)
            c6_findings = [f for f in findings if f.check_id == "C6"]
            self.assertEqual(len(c6_findings), 0, f"Expected no C6 findings, got: {c6_findings}")

    def test_c6_rejects_outside_target(self):
        """A target outside skills/beo/ must produce a critical C6 finding."""
        import beo_audit
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            self._make_proposal(root, "src/main.js")
            findings = beo_audit.check_harness_proposal_targets(root)
            c6_findings = [f for f in findings if f.check_id == "C6"]
            self.assertEqual(len(c6_findings), 1)
            self.assertEqual(c6_findings[0].severity, beo_audit.SEVERITY_CRITICAL)
            self.assertIn("skills/beo/", c6_findings[0].message)
            self.assertIn("src/main.js", c6_findings[0].message)

    def test_c6_handles_empty_artifacts_dir(self):
        """An artifacts directory with no proposals must not produce findings."""
        import beo_audit
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            findings = beo_audit.check_harness_proposal_targets(root)
            c6_findings = [f for f in findings if f.check_id == "C6"]
            self.assertEqual(len(c6_findings), 0)


class ClimateConfigTest(unittest.TestCase):
    """Tests for beo-climate/config.json audit_check_id mappings."""

    def _load_climate_config(self) -> dict:
        """Load and return the beo-climate config.json."""
        import json
        config_path = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-climate" / "config.json"
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def test_auto_heal_check_ids_are_valid(self):
        """Every auto_heal_allowlist item must reference a known audit check_id."""
        import beo_audit
        known_check_ids = beo_audit.get_check_ids()
        self.assertIn("C1", known_check_ids, "get_check_ids should include C1-C7")
        config = self._load_climate_config()
        items = config.get("auto_heal_allowlist", {}).get("items", [])
        self.assertGreater(len(items), 0, "auto_heal_allowlist should have at least one item")
        for item in items:
            check_id = item.get("audit_check_id")
            self.assertIn(check_id, known_check_ids,
                          f"Item '{item.get('id')}' has unknown audit_check_id '{check_id}'; "
                          f"expected one of {sorted(known_check_ids)}")
            self.assertIsInstance(item.get("summary"), str)
            self.assertGreater(len(item["summary"]), 0)


class DuplicateOwnerRulesTest(unittest.TestCase):
    """Tests for _find_duplicate_owner_rules JSON-based duplicate detection."""

    def test_no_duplicates_returns_empty(self):
        """A schema with no duplicate owner_rules keys returns no findings."""
        import json
        import beo_audit
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ref_dir = root / "skills" / "beo" / "beo-reference" / "registry"
            ref_dir.mkdir(parents=True)
            schema = {
                "beo_contract_metadata": {
                    "owner_rules": {
                        "beo-plan": {"may_emit": ["planned"]},
                        "beo-validate": {"may_emit": ["PASS_EXECUTE"]},
                    }
                }
            }
            (ref_dir / "runtime-event.schema.json").write_text(json.dumps(schema), encoding="utf-8")
            findings = beo_audit._find_duplicate_owner_rules(root)
            self.assertEqual(findings, [])

    def test_duplicate_key_detected(self):
        """A schema with a repeated owner_rules key produces a C4 finding."""
        import beo_audit
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ref_dir = root / "skills" / "beo" / "beo-reference" / "registry"
            ref_dir.mkdir(parents=True)
            # Raw JSON with a duplicate key (Python's json.loads + object_pairs_hook detects it)
            raw = (
                '{"beo_contract_metadata": {"owner_rules": '
                '{"beo-plan": {"may_emit": ["a"]}, '
                '"beo-plan": {"may_emit": ["b"]}'
                '}}}'
            )
            (ref_dir / "runtime-event.schema.json").write_text(raw, encoding="utf-8")
            findings = beo_audit._find_duplicate_owner_rules(root)
            c4 = [f for f in findings if f.check_id == "C4"]
            self.assertEqual(len(c4), 1)
            self.assertIn("beo-plan", c4[0].message)
            self.assertIn("duplicate", c4[0].message)


class StaleLearningEvidenceRefTest(unittest.TestCase):
    """Tests for C9 — learning evidence_ref resolution, including dual-root."""

    def test_resolve_learning_ref_accepts_list_of_bases(self):
        """_resolve_learning_ref must accept a list of bases (vault + repos).

        Regression guard for the dual-root fix: the signature changed from
        (vault, repo) to (bases) so a single C9 run can resolve both skills/
        refs and product .beads/src refs.
        """
        import beo_audit
        with tempfile.TemporaryDirectory() as tmp:
            base_a = Path(tmp) / "a"
            base_b = Path(tmp) / "b"
            base_a.mkdir()
            base_b.mkdir()
            (base_b / "target.txt").write_text("x", encoding="utf-8")
            # ref only exists under base_b, with base_a searched first
            resolved = beo_audit._resolve_learning_ref("target.txt", [base_a, base_b])
            self.assertIsNotNone(resolved)
            self.assertEqual(resolved, (base_b / "target.txt").resolve())
            # ref present under neither base
            self.assertIsNone(beo_audit._resolve_learning_ref("missing.txt", [base_a, base_b]))

    def test_c9_extra_repos_resolve_product_refs_from_skills_root(self):
        """C9 with extra_repos resolves a product-repo ref while --root is elsewhere.

        Mirrors the real dual-root case: skills repo is --root, but a learning
        note cites a product path like .beads/issues.jsonl. Without extra_repos
        the ref is a false positive; with it, C9 stays quiet.
        """
        import beo_audit
        with tempfile.TemporaryDirectory() as skills_tmp, tempfile.TemporaryDirectory() as prod_tmp:
            skills_root = Path(skills_tmp)
            prod_root = Path(prod_tmp)
            # Simulate a product-repo evidence file absent from the skills root
            (prod_root / ".beads").mkdir()
            (prod_root / ".beads" / "issues.jsonl").write_text("[]", encoding="utf-8")
            ref = ".beads/issues.jsonl"
            bases_default = [skills_root]  # only --root
            bases_dual = [skills_root, prod_root]  # --root + --learning-repo
            self.assertIsNone(
                beo_audit._resolve_learning_ref(ref, bases_default),
                "ref must NOT resolve from skills root alone (dual-root gap)",
            )
            self.assertIsNotNone(
                beo_audit._resolve_learning_ref(ref, bases_dual),
                "ref MUST resolve once the product repo is an extra base",
            )

    def test_c9_extra_repos_dedupe_and_default_none_is_backward_compatible(self):
        """extra_repos=None must behave as the empty list (backward compat)."""
        import beo_audit
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # Should not raise and should return a list (no learnings dir here)
            findings_none = beo_audit.check_stale_learning_evidence_refs(root, None)
            findings_empty = beo_audit.check_stale_learning_evidence_refs(root, [])
            self.assertEqual(findings_none, findings_empty)


if __name__ == "__main__":
    unittest.main()
