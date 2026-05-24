#!/usr/bin/env python3
import os
import sys
import tempfile
import json
import unittest
from pathlib import Path

# Add BEO scripts directory to sys.path
REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "skills" / "beo" / "reference"
scripts = REFERENCE_ROOT / "scripts"
sys.path.insert(0, str(scripts))

class HelperSemanticsTest(unittest.TestCase):
    def test_helper_semantics(self):
        import beo_check  # type: ignore[import-not-found]
        from beo_command import CommandAdapter  # type: ignore[import-not-found]
        from beo_registry_context import RegistryContext

        ticket = {
            "schema_version": "beo-beads/v3",
            "issue_id": "br-1",
            "mode": "quick",
            "request": "x",
            "done_target": "one target",
            "done": ["y"],
            "human_gates": {"status": "not_applicable", "gates": []},
            "scope": {"files": {"allow": ["README.md"], "forbid": []}, "verify": {"commands": ["rtk git diff --check"]}},
            "acceptance_criteria": ["ok"],
            "atomicity": {"decision": "atomic", "reason": "one bounded repo-only edit", "rejects_multi_task": True},
            "posture_profile": "repo_only_low_risk",
            "readiness": "PASS_EXECUTE",
            "selected_execution_set": "set-1",
            "execution_mode": "normal",
        }
        base_hash = beo_check.plan_input_hash(ticket)
        appended = dict(ticket)
        appended.update(
            {
                "triage_records": [{"owner": "beo-plan", "purpose": "issue_selection", "selected_issue": "br-1"}],
                "execution": {"status": "ready_for_review", "changed_files": ["README.md"]},
                "review": {"verdict": "accept"},
                "debug": {"status": "not_used"},
                "runtime_events": [{"id": "evt-1", "kind": "user_stop", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "user_blocker", "basis_ref": "checks/run.json", "message": "Stop for user."}],
            }
        )

        self.assertEqual(beo_check.plan_input_hash(appended), base_hash)

        issue = {"id": "br-1", "title": "Test", "status": "in_progress", "assignee": "assistant", "labels": ["beo:atomic"]}
        bead_hash = beo_check.sha256_text(beo_check.stable_json(beo_check.hard_bead_snapshot(issue)))
        contracts_hash = "sha256:contracts"
        approval_ref = {
            "id": "approval:test",
            "approved_by_owner": "beo-validate",
            "approved_at": "2026-01-01T00:00:00Z",
            "issue_id": "br-1",
            "ticket_schema_version": "beo-beads/v3",
            "approval_projection_rule": "plan_input_execution_binding",
            "approval_projection_hash": beo_check.approval_hash(ticket, issue, bead_hash, contracts_hash),
            "plan_input_hash": base_hash,
            "bead_snapshot_hash": bead_hash,
            "command_contracts_hash": contracts_hash,
            "helper_version": beo_check.HELPER_VERSION,
            "helper_run_id": "beo_check:test",
            "repo_head": beo_check.repo_head_sentinel(Path.cwd()),
        }
        approved_ticket = dict(ticket, approval_ref=approval_ref, integrity={"status": "verified", "evidence_ref": "checks/test.json"})
        self.assertEqual(beo_check.approval_envelope_status(approved_ticket, issue, base_hash, bead_hash, contracts_hash, Path.cwd()), "complete")

        stale_ticket = dict(approved_ticket, approval_ref=dict(approval_ref, repo_head="stale-head"))
        stale_diagnostics = beo_check.approval_envelope_diagnostics(stale_ticket, issue, base_hash, bead_hash, contracts_hash, Path.cwd())
        self.assertIn("repo_head", [reason.get("field") for reason in stale_diagnostics.get("invalid_reasons", [])])

        classified = beo_check.validation_subreasons([
            "atomicity.decision must be atomic before PASS_EXECUTE",
            "path matches protected pattern .env: .env",
            "mode must be one of ['quick']",
            "Human Gates are unresolved",
            "done_target is required for one atomic completion target",
        ])
        self.assertEqual(set(classified), {"fail_atomicity", "fail_scope", "fail_profile", "fail_human_gate", "fail_schema"})

        base_approval = beo_check.approval_hash(ticket, issue, bead_hash, contracts_hash)
        self.assertEqual(beo_check.approval_hash(appended, issue, bead_hash, contracts_hash), base_approval)

        issue_with_comment = dict(issue, comments=[{"body": "ordinary comment"}], updated_at="2026-01-01T00:03:00Z")
        comment_hash = beo_check.sha256_text(beo_check.stable_json(beo_check.hard_bead_snapshot(issue_with_comment)))
        self.assertEqual(comment_hash, bead_hash)

        changed_execution_set = dict(ticket, selected_execution_set="set-2")
        self.assertNotEqual(beo_check.approval_hash(changed_execution_set, issue, bead_hash, contracts_hash), base_approval)

        boundary_errors = beo_check.validate_phase_boundary(dict(ticket, readiness="PASS_EXECUTE"), "beo-plan")
        self.assertTrue(boundary_errors)

        repair_ticket = dict(
            ticket,
            review={"verdict": "repair_same_scope"},
            runtime_events=[
                {
                    "id": "evt-1",
                    "kind": "change_request",
                    "subtype": "repair_same_scope",
                    "created_at": "2026-01-01T00:00:00Z",
                    "owner": "beo-review",
                    "issue_id": "br-1",
                    "condition_id": "repair_same_scope",
                    "basis_ref": "review:finding-1",
                    "message": "Repair same scope.",
                    "requested_by": "beo-review",
                    "repair_type": "same_scope",
                    "finding_refs": ["finding-1"],
                    "prior_approval_ref": "checks/beo-check.json",
                    "unchanged_boundaries": {
                        "scope.files.allow": True,
                        "generated_outputs": True,
                        "human_gates": True,
                        "acceptance_criteria": True,
                        "external_side_effects": True,
                        "stateful_external_systems": True,
                        "scope.files.forbid": True,
                        "scope.verify.commands": True,
                    },
                }
            ],
        )
        self.assertFalse(beo_check.validate_runtime_events(repair_ticket, "br-1"))

        bad_debug_return = dict(
            ticket,
            runtime_events=[
                {"id": "evt-1", "kind": "handoff", "subtype": "debug", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "root_cause_diagnosis_needed", "basis_ref": "execution:blocker", "message": "Need debug.", "caller_owner": "beo-execute", "caller_actor": "assistant", "return_to": "beo-execute", "return_condition_id": "debug_return_ready", "question": "Why is execution blocked?"},
                {"id": "evt-2", "kind": "return", "subtype": "debug", "created_at": "2026-01-01T00:01:00Z", "owner": "beo-debug", "issue_id": "br-1", "condition_id": "debug_returned", "basis_ref": "debug:artifact", "message": "Done.", "caller_owner": "beo-review", "caller_actor": "assistant", "return_to": "beo-review", "return_condition_id": "debug_return_ready", "diagnosis_status": "root_cause_proven", "diagnosis_ref": "debug:artifact"},
            ],
        )
        self.assertTrue(beo_check.validate_runtime_events(bad_debug_return, "br-1"))

        wrong_owner_debug_return = dict(
            ticket,
            runtime_events=[
                {"id": "evt-1", "kind": "handoff", "subtype": "debug", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "root_cause_diagnosis_needed", "basis_ref": "execution:blocker", "message": "Need debug.", "caller_owner": "beo-execute", "caller_actor": "assistant", "return_to": "beo-execute", "return_condition_id": "debug_return_ready", "question": "Why is execution blocked?"},
                {"id": "evt-2", "kind": "return", "subtype": "debug", "created_at": "2026-01-01T00:01:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "debug_returned", "basis_ref": "debug:artifact", "message": "Done.", "caller_owner": "beo-execute", "caller_actor": "assistant", "return_to": "beo-execute", "return_condition_id": "debug_return_ready", "diagnosis_status": "root_cause_proven", "diagnosis_ref": "debug:artifact"},
            ],
        )
        self.assertTrue(beo_check.validate_runtime_events(wrong_owner_debug_return, "br-1"))

        direct_recall_return = dict(
            ticket,
            runtime_events=[
                {"id": "evt-1", "kind": "return", "subtype": "recall", "created_at": "2026-01-01T00:01:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "memory_recalled", "basis_ref": "recall:summary", "message": "Done.", "caller_owner": "beo-execute", "return_to": "beo-execute", "result_status": "memory_recalled", "recall_ref": ".beads/artifacts/br-1/RECALL_SUMMARY.md"},
            ],
        )
        self.assertTrue(beo_check.validate_runtime_events(direct_recall_return, "br-1"))

        malformed_events = dict(ticket, runtime_events=["bad"])
        self.assertTrue(beo_check.validate_runtime_events(malformed_events, "br-1"))

        bad_author_recall = dict(
            ticket,
            runtime_events=[
                {"id": "evt-1", "kind": "handoff", "subtype": "recall", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-author", "issue_id": "br-1", "condition_id": "memory_recalled", "basis_ref": "author:need", "message": "Recall.", "caller_owner": "beo-author", "return_to": "beo-author", "query": "prior doctrine"},
            ],
        )
        self.assertTrue(beo_check.validate_runtime_events(bad_author_recall, "br-1"))

        early_learning = dict(
            ticket,
            runtime_events=[
                {"id": "evt-1", "kind": "learning_candidate", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-debug", "issue_id": "br-1", "condition_id": "learning_candidate", "basis_ref": "debug:none", "message": "Learn.", "case_type": "debug_pattern", "source_phase": "beo-debug"},
            ],
        )
        self.assertTrue(beo_check.validate_runtime_events(early_learning, "br-1"))
        self.assertTrue(any("source_event_id is required" in err for err in beo_check.validate_runtime_events(early_learning, "br-1")))

        valid_debug_learning = dict(
            ticket,
            runtime_events=[
                {"id": "evt-1", "kind": "handoff", "subtype": "debug", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "root_cause_diagnosis_needed", "basis_ref": "execution:blocker", "message": "Need debug.", "caller_owner": "beo-execute", "caller_actor": "assistant", "return_to": "beo-execute", "return_condition_id": "debug_return_ready", "question": "Why is execution blocked?"},
                {"id": "evt-2", "kind": "return", "subtype": "debug", "created_at": "2026-01-01T00:01:00Z", "owner": "beo-debug", "issue_id": "br-1", "condition_id": "debug_returned", "basis_ref": "debug:artifact", "message": "Done.", "caller_owner": "beo-execute", "caller_actor": "assistant", "return_to": "beo-execute", "return_condition_id": "debug_return_ready", "diagnosis_status": "root_cause_proven", "diagnosis_ref": "debug:artifact"},
                {"id": "evt-3", "kind": "learning_candidate", "created_at": "2026-01-01T00:02:00Z", "owner": "beo-debug", "issue_id": "br-1", "condition_id": "learning_candidate", "basis_ref": "debug:artifact", "message": "Learn.", "case_type": "debug_pattern", "source_phase": "beo-debug", "source_event_id": "evt-2"},
            ],
        )
        self.assertFalse(beo_check.validate_runtime_events(valid_debug_learning, "br-1"))

        mismatched_learning = dict(valid_debug_learning, runtime_events=valid_debug_learning["runtime_events"][:-1] + [dict(valid_debug_learning["runtime_events"][-1], source_phase="beo-review")])
        self.assertTrue(beo_check.validate_runtime_events(mismatched_learning, "br-1"))

        bad_debug_learning_source = dict(valid_debug_learning, runtime_events=valid_debug_learning["runtime_events"][:-1] + [dict(valid_debug_learning["runtime_events"][-1], source_event_id="evt-1")])
        self.assertTrue(beo_check.validate_runtime_events(bad_debug_learning_source, "br-1"))

        valid_review_learning = dict(
            ticket,
            review={"verdict": "accept"},
            runtime_events=[
                {"id": "evt-1", "kind": "change_request", "subtype": "repair_same_scope", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-review", "issue_id": "br-1", "condition_id": "repair_same_scope", "basis_ref": "review:finding", "message": "Route.", "requested_by": "beo-review", "finding_refs": ["review:finding"], "prior_approval_ref": "approval:test", "unchanged_boundaries": {"scope.files.allow": True, "generated_outputs": True, "human_gates": True, "acceptance_criteria": True, "external_side_effects": True, "stateful_external_systems": True, "scope.files.forbid": True, "scope.verify.commands": True}},
                {"id": "evt-2", "kind": "learning_candidate", "created_at": "2026-01-01T00:01:00Z", "owner": "beo-review", "issue_id": "br-1", "condition_id": "learning_candidate", "basis_ref": "review:finding", "message": "Learn.", "case_type": "success_pattern", "source_phase": "beo-review", "source_event_id": "evt-1"},
            ],
        )
        self.assertFalse(beo_check.validate_runtime_events(valid_review_learning, "br-1"))

        bad_review_learning_source = dict(valid_review_learning, runtime_events=valid_review_learning["runtime_events"][:-1] + [dict(valid_review_learning["runtime_events"][-1], source_event_id="missing")])
        self.assertTrue(beo_check.validate_runtime_events(bad_review_learning_source, "br-1"))

        adapter = CommandAdapter(Path.cwd())
        adapter.build_argv("qmd.query", owner="beo-recall", query="x", limit=1, collection="c")
        adapter.build_argv("qmd.get", owner="beo-recall", path_or_docid="doc")

        with self.assertRaises(ValueError):
            adapter.build_argv("qmd.query", owner="beo-plan", query="x", limit=1, collection="c")

        with self.assertRaises(TypeError):
            adapter.build_argv("qmd.query", query="x", limit=1, collection="c")  # type: ignore[call-arg]

        superseded = dict(repair_ticket, runtime_events=repair_ticket["runtime_events"] + [{"id": "evt-3", "kind": "change_request", "subtype": "scope_delta", "created_at": "2026-01-01T00:02:00Z", "owner": "beo-review", "issue_id": "br-1", "condition_id": "scope_delta_required", "basis_ref": "review:finding-2", "message": "Scope changed."}])
        self.assertFalse(beo_check.validate_runtime_events(superseded, "br-1"))

        ctx = RegistryContext(Path.cwd())
        self.assertTrue(beo_check.validate_review_verdict({"verdict": "cannot_deliver"}, ctx))
        self.assertFalse(beo_check.validate_review_verdict({"verdict": "cannot_deliver", "reason_class": "user_owned", "cannot_deliver_reason": "user_owned"}, ctx))
        self.assertTrue(beo_check.validate_review_verdict({"verdict": "cannot_deliver", "reason_class": "user_owned", "cannot_deliver_reason": "invalid_reason"}, ctx))
        self.assertTrue(beo_check.validate_review_verdict({"verdict": "cannot_deliver", "reason_class": "user_owned"}, ctx))

        self.assertFalse(beo_check.validate_repair_budget({"mode": "quick"}, {"verdict": "repair_same_scope", "repair_counter": 0}))
        self.assertTrue(beo_check.validate_repair_budget({"mode": "quick"}, {"verdict": "repair_same_scope", "repair_counter": "1"}))
        self.assertTrue(beo_check.validate_repair_budget({"mode": "quick"}, {"verdict": "repair_same_scope", "repair_counter": -1}))
        self.assertTrue(beo_check.validate_repair_budget({"mode": "quick"}, {"verdict": "repair_same_scope", "repair_counter": 1}))
        self.assertTrue(beo_check.validate_repair_budget({"mode": "standard"}, {"verdict": "repair_rescope", "repair_counter": 2}))

        bad_mode = dict(ticket, mode="typo")
        self.assertTrue(any("mode must be one of" in err for err in beo_check.validate_plan(Path.cwd(), bad_mode, {"id": "br-1", "labels": ["beo:atomic"]})))

        missing_done_target = dict(ticket)
        missing_done_target.pop("done_target", None)
        self.assertTrue(any("done_target is required" in err for err in beo_check.validate_plan(Path.cwd(), missing_done_target, {"id": "br-1", "labels": ["beo:atomic"]})))

        bad_gate = dict(ticket, human_gates={"status": "resolved", "gates": [{"type": "authorization", "message": "ok"}]})
        gate_errors = beo_check.validate_plan(Path.cwd(), bad_gate, {"id": "br-1", "labels": ["beo:atomic"]})
        self.assertTrue(any("scope is required" in err for err in gate_errors) or any("valid_for_issue_id or expires_at" in err for err in gate_errors))

        with tempfile.TemporaryDirectory() as tmp:
            reservation_root = Path(tmp)
            pass_ticket = dict(ticket, readiness="PASS_EXECUTE")
            pre_pass_ticket = dict(ticket)
            pre_pass_ticket.pop("readiness", None)
            quick_errors = beo_check.validate_plan(reservation_root, pre_pass_ticket, {"id": "br-1", "labels": ["beo:atomic"]})
            self.assertFalse(any("active path reservation is required" in err for err in quick_errors))

            strict_ticket = dict(pre_pass_ticket, mode="strict", strict={"reason": "test"}, authorization_refs=["test"], risk_scope="strict test", rollback_boundary="test")
            self.assertTrue(any("active path reservation is required" in err for err in beo_check.validate_plan(reservation_root, strict_ticket, {"id": "br-1", "labels": ["beo:atomic"]})))
            self.assertTrue(any("active path reservation" in err for err in beo_check.check_path_reservations(reservation_root, pass_ticket, require_current=True)))

            (reservation_root / ".beads").mkdir()
            reservations = reservation_root / ".beads" / "beo-reservations.jsonl"
            previous_actor = os.environ.get("BR_ACTOR")
            os.environ["BR_ACTOR"] = "assistant"
            try:
                reservations.write_text(json.dumps({"issue_id": "br-1", "actor": beo_check.actor_identity(), "status": "active", "paths": ["README.md"], "expires_at": "2999-01-01T00:00:00Z"}) + "\n")
                self.assertFalse(beo_check.check_path_reservations(reservation_root, pass_ticket, require_current=True))

                reservations.write_text(json.dumps({"issue_id": "br-1", "actor": "other", "status": "active", "paths": ["README.md"], "expires_at": "2999-01-01T00:00:00Z"}) + "\n")
                self.assertTrue(any("different actor" in err for err in beo_check.check_path_reservations(reservation_root, pass_ticket, require_current=True)))

                reservations.write_text(json.dumps({"issue_id": "br-1", "actor": beo_check.actor_identity(), "status": "active", "paths": ["other.md"], "expires_at": "2999-01-01T00:00:00Z"}) + "\n")
                self.assertTrue(any("does not cover planned paths" in err for err in beo_check.check_path_reservations(reservation_root, pass_ticket, require_current=True)))

                reservations.write_text(json.dumps({"issue_id": "br-1", "actor": beo_check.actor_identity(), "status": "active", "paths": ["README.md"], "expires_at": "2000-01-01T00:00:00Z"}) + "\n")
                self.assertTrue(any("active path reservation is required" in err for err in beo_check.check_path_reservations(reservation_root, pass_ticket, require_current=True)))

                reservations.write_text("{not json}\n")
                self.assertTrue(any("path reservation read failed" in err for err in beo_check.check_path_reservations(reservation_root, pass_ticket, require_current=True)))
            finally:
                if previous_actor is None:
                    os.environ.pop("BR_ACTOR", None)
                else:
                    os.environ["BR_ACTOR"] = previous_actor

            ticket_dir = reservation_root / ".beads" / "artifacts" / "br-1"
            ticket_dir.mkdir(parents=True)
            ticket_file = ticket_dir / "TICKET.md"
            ticket_file.write_text("beo.ticket:\n  schema_version: beo-beads/v3\n  issue_id: br-1\n  mode: quick\n  readiness: PASS_EXECUTE\n")
            self.assertNotIn("readiness", beo_check.read_ticket(ticket_file))

            # Standard YAML frontmatter format (requires re match)
            ticket_file.write_text("---\nschema_version: beo-beads/v3\nissue_id: br-1\nmode: quick\n---\n")
            t_parsed = beo_check.read_ticket(ticket_file)
            self.assertEqual(t_parsed.get("issue_id"), "br-1")

            other_root = Path(tempfile.mkdtemp())
            other_ticket_dir = other_root / ".beads" / "artifacts" / "br-1"
            other_ticket_dir.mkdir(parents=True)
            (other_ticket_dir / "state.json").write_text(json.dumps({"readiness": "PASS_EXECUTE"}))
            self.assertEqual(beo_check.read_ticket(ticket_file, other_root, "br-1")["state.json"].get("readiness"), "PASS_EXECUTE")

            ticket_file.write_text("---\n- not\n- an\n- object\n---\n")
            with self.assertRaises(ValueError):
                beo_check.read_ticket(ticket_file)

            ticket_file.write_text("---\nschema_version: beo-beads/v3\nissue_id: br-1\nmode: quick\n---\n")
            (ticket_dir / "state.json").write_text("{not json}\n")
            with self.assertRaises(Exception):
                beo_check.read_ticket(ticket_file)

            (ticket_dir / "state.json").unlink()
            (ticket_dir / "runtime-events.jsonl").write_text("{not json}\n")
            with self.assertRaises(Exception):
                beo_check.read_ticket(ticket_file)

        removed_learning_tree = "skills/beo/reference" + "/learnings"
        curated_scope = dict(ticket, scope={"files": {"allow": [f"{removed_learning_tree}/example.md"], "forbid": []}, "verify": {"commands": ["rtk git diff --check"]}})
        self.assertTrue(any("curated learning" in err for err in beo_check.validate_plan(Path.cwd(), curated_scope, {"id": "br-1", "labels": ["beo:atomic"]})))

        old_env = {key: os.environ.get(key) for key in ["BR_ACTOR", "BEO_ACTOR", "AGENT_NAME", "BR_AGENT_NAME", "ACTOR"]}
        try:
            for key in old_env:
                os.environ.pop(key, None)
            issue = {"status": "in_progress", "assignee": "assistant"}
            self.assertFalse(beo_check.claim_valid(issue))

            os.environ["AGENT_NAME"] = "assistant"
            self.assertTrue(beo_check.claim_valid(issue))

            os.environ["BR_ACTOR"] = "other"
            self.assertFalse(beo_check.claim_valid(issue))

            os.environ["BR_ACTOR"] = "assistant"
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "new.txt").write_text("new")
                drift_ticket = dict(ticket, execution={"prestate_refs": {"files": {"new.txt": "missing"}}, "changed_files": []})
                self.assertTrue(any("unexplained prestate drift" in err for err in beo_check.validate_execute(root, drift_ticket, issue, "complete")))

                structured_drift = dict(ticket, execution={"prestate_refs": {"files": {"new.txt": {"kind": "expected_missing", "hash": "missing"}}}, "changed_files": []})
                self.assertTrue(any("unexplained prestate drift" in err for err in beo_check.validate_execute(root, structured_drift, issue, "complete")))

                bad_existing = dict(ticket, execution={"prestate_refs": {"files": {"new.txt": {"kind": "existing", "hash": "missing"}}}, "changed_files": ["new.txt"]})
                self.assertTrue(any("must not be missing for existing" in err for err in beo_check.validate_execute(root, bad_existing, issue, "complete")))

                missing_prestate_ticket = dict(ticket, execution={"prestate_refs": {"files": {}}, "changed_files": ["new.txt"]})
                self.assertTrue(any("missing prestate hash" in err for err in beo_check.validate_execute(root, missing_prestate_ticket, issue, "complete")))
        finally:
            for key, value in old_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

if __name__ == "__main__":
    unittest.main()
