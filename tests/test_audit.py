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
        """A path like '.beads/artifacts/br-123/TICKET.yaml' must be classified as 'ticket'."""
        result = self._classify(".beads/artifacts/br-123/TICKET.yaml")
        self.assertEqual(result, "ticket")

    def test_classify_ticket_with_absolute_prefix(self):
        """A path like '/repo/.beads/artifacts/br-123/TICKET.yaml' must be classified as 'ticket'."""
        result = self._classify("/repo/.beads/artifacts/br-123/TICKET.yaml")
        self.assertEqual(result, "ticket")


class HarnessProposalTargetTest(unittest.TestCase):
    """Tests for C6 — harness proposal target scope enforcement."""

    def _make_proposal(self, root: Path, target: str, issue_id: str = "br-test") -> Path:
        """Create a harness-proposal.yaml under .beads/artifacts/ and return its path."""
        import yaml
        proposal_dir = root / ".beads" / "artifacts" / issue_id
        proposal_dir.mkdir(parents=True, exist_ok=True)
        proposal_path = proposal_dir / "harness-proposal.yaml"
        with open(proposal_path, "w") as f:
            yaml.dump({
                "version": 1,
                "proposal_id": f"prop-{issue_id[-8:]}",
                "source_issue_id": issue_id,
                "target": target,
                "change_type": "improvement",
                "rationale": "test",
                "proposed_diff": "test",
                "safety_note": "test",
            }, f)
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
    """Tests for beo-climate/config.yaml audit_check_id mappings."""

    def _load_climate_config(self) -> dict:
        """Load and return the beo-climate config.yaml."""
        import yaml
        config_path = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-climate" / "config.yaml"
        with open(config_path, "r") as f:
            return yaml.safe_load(f)

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


if __name__ == "__main__":
    unittest.main()
