#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

scripts_dir = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-reference" / "scripts"
sys.path.insert(0, str(scripts_dir))


class ImportTest(unittest.TestCase):
    def test_imports(self):
        import beo_approval  # noqa: F401
        import beo_git  # noqa: F401
        import beo_io  # noqa: F401
        import beo_memory_tools  # noqa: F401
        import beo_paths  # noqa: F401
        import beo_ticket  # noqa: F401
        import check_skill_bundle  # noqa: F401
        import beo_check_identity  # noqa: F401
        import beo_check_scope  # noqa: F401
        import beo_check_approval  # noqa: F401
        import beo_check_events  # noqa: F401
        import beo_check  # noqa: F401
        import beo_quick_fill  # noqa: F401
        import beo_reservation  # noqa: F401
        import beo_state  # noqa: F401
        import beo_recall  # noqa: F401
        import beo_memory_write  # noqa: F401
        import beo_setup  # noqa: F401
        import beo_audit  # noqa: F401
        import beo_propose  # noqa: F401
        import beo_verify  # noqa: F401
        import beo_score_trace  # noqa: F401
        import beo_score_context  # noqa: F401


class MemoryWriteMigrationTest(unittest.TestCase):
    """Unit tests for the legacy 'type' backfill in beo_memory_write."""

    def test_migrate_defaults_to_learning(self):
        import beo_memory_write
        migrated = beo_memory_write.migrate_legacy_note({"basis_ref": "x"}, "some body text")
        self.assertEqual(migrated["type"], "learning")
        self.assertEqual(migrated["basis_ref"], "x")

    def test_migrate_picks_decision_when_body_indicates(self):
        import beo_memory_write
        migrated = beo_memory_write.migrate_legacy_note({}, "this is a decision about the validator")
        self.assertEqual(migrated["type"], "decision")

    def test_migrate_picks_reference_when_body_indicates(self):
        import beo_memory_write
        migrated = beo_memory_write.migrate_legacy_note({}, "see the reference doc for details")
        self.assertEqual(migrated["type"], "reference")

    def test_migrate_preserves_existing_type(self):
        import beo_memory_write
        original = {"type": "decision", "basis_ref": "x"}
        migrated = beo_memory_write.migrate_legacy_note(original, "any body")
        self.assertIs(migrated, original)

    def test_rewrite_frontmatter_round_trip(self):
        import beo_memory_write
        md = "---\nbasis_ref: x\nevidence_refs: [a, b]\nsecret_policy: handles_only\n---\nbody text"
        rewritten = beo_memory_write._rewrite_frontmatter(md, {"type": "learning", "basis_ref": "x", "evidence_refs": ["a", "b"], "secret_policy": "handles_only"})
        # Round-trip back to a dict via the extractor
        extracted = beo_memory_write.extract_frontmatter(rewritten)
        self.assertEqual(extracted["type"], "learning")
        self.assertEqual(extracted["basis_ref"], "x")
        self.assertEqual(extracted["evidence_refs"], ["a", "b"])
        self.assertEqual(extracted["secret_policy"], "handles_only")
        # Body is preserved
        self.assertIn("body text", rewritten)


if __name__ == "__main__":
    unittest.main()
