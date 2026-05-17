#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REFERENCE = SCRIPTS.parent


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


approval = load_script("beo_approval_check")
registry_check = load_script("beo_registry_check")


def write_compact_fixture(root: Path, ticket: str, *, default_current_owner: str | None = "beo-validate") -> None:
    artifact_root = root / ".beads" / "artifacts" / "compact-case"
    artifact_root.mkdir(parents=True)
    manifest = {
        "feature_slug": "compact-case",
        "artifact_root": ".beads/artifacts/compact-case",
        "artifact_density": "compact",
        "lifecycle_status": "active",
        "current_owner": "beo-validate",
        "created_at": "2026-05-14T00:00:00Z",
        "updated_at": "2026-05-14T00:00:00Z",
        "artifacts": ["FEATURE.json", "TICKET.md"],
    }
    (artifact_root / "FEATURE.json").write_text(json.dumps(manifest))
    if "```yaml beo.ticket\n" in ticket:
        if "\nrequest:" not in ticket:
            ticket = ticket.replace("```yaml beo.ticket\n", "```yaml beo.ticket\nrequest: Test request\n", 1)
        if default_current_owner is not None and "\ncurrent_owner:" not in ticket:
            ticket = ticket.replace("```yaml beo.ticket\n", f"```yaml beo.ticket\ncurrent_owner: {default_current_owner}\n", 1)
    (artifact_root / "TICKET.md").write_text(ticket)


def write_full_review_fixture(root: Path, tracker: dict[str, object]) -> None:
    artifact_root = root / ".beads" / "artifacts" / "full-case"
    artifact_root.mkdir(parents=True)
    manifest = {
        "feature_slug": "full-case",
        "artifact_root": ".beads/artifacts/full-case",
        "artifact_density": "full",
        "lifecycle_status": "active",
        "current_owner": "beo-review",
        "created_at": "2026-05-14T00:00:00Z",
        "updated_at": "2026-05-14T00:00:00Z",
        "artifacts": ["FEATURE.json", "CONTEXT.md", "PLAN.md", "TRACKER.json"],
    }
    (artifact_root / "FEATURE.json").write_text(json.dumps(manifest))
    (artifact_root / "CONTEXT.md").write_text("""```yaml beo.context
request: Test request
human_gates:
  status: not_applicable
  gates: []
```
""")
    (artifact_root / "PLAN.md").write_text("""```yaml beo.plan
declared_files:
  - src/a.py
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    items:
      - id: item-1
        files:
          - src/a.py
acceptance_criteria:
  - AC-1
verification_contract:
  commands:
    - python3 -m unittest
readiness: PASS_EXECUTE
approval_ref:
  id: approval-current
  approved_by_owner: beo-validate
  approved_at: "2026-05-14T00:00:00Z"
  artifact_density: full
  selected_execution_set: set-1
  execution_mode: normal
  approval_projection_rule: full_plan_explicit
  envelope_hash: sha256:stale
  artifact_hashes: {}
integrity:
  status: verified
  evidence_ref: beo_approval_check:test
selected_execution_set: set-1
execution_mode: normal
```
""")
    (artifact_root / "TRACKER.json").write_text(json.dumps(tracker))


def write_full_validate_fixture(root: Path, human_gates: str) -> None:
    human_gates_yaml = {
        "not_applicable": "\n  status: not_applicable\n  gates: []",
        "unresolved": "\n  status: unresolved\n  gates:\n    - id: HG-1\n      type: clarification\n      question: Decide scope\n      affects: [scope]\n      resolution_status: unresolved\n      resolution_ref: missing",
        "resolved": "\n  status: resolved\n  gates:\n    - id: HG-1\n      type: clarification\n      question: Decide scope\n      affects: [scope]\n      resolution_status: resolved\n      resolution_ref: user:1",
    }.get(human_gates, human_gates)
    artifact_root = root / ".beads" / "artifacts" / "full-case"
    artifact_root.mkdir(parents=True)
    manifest = {
        "feature_slug": "full-case",
        "artifact_root": ".beads/artifacts/full-case",
        "artifact_density": "full",
        "lifecycle_status": "active",
        "current_owner": "beo-validate",
        "created_at": "2026-05-14T00:00:00Z",
        "updated_at": "2026-05-14T00:00:00Z",
        "artifacts": ["FEATURE.json", "CONTEXT.md", "PLAN.md"],
    }
    (artifact_root / "FEATURE.json").write_text(json.dumps(manifest))
    (artifact_root / "CONTEXT.md").write_text(f"""```yaml beo.context
request: Test request
human_gates:{human_gates_yaml}
```
""")
    (artifact_root / "PLAN.md").write_text("""```yaml beo.plan
declared_files:
  - src/a.py
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    items:
      - id: item-1
        files:
          - src/a.py
acceptance_criteria:
  - AC-1
verification_contract:
  commands:
    - python3 -m unittest
```
""")


def write_approval_script_fixture(tmp: str, registry_file: str, key: str, value: object | None) -> tuple[Path, Path]:
    base = Path(tmp) / "reference"
    (base / "scripts").mkdir(parents=True)
    shutil.copy(SCRIPTS / "beo_approval_check.py", base / "scripts" / "beo_approval_check.py")
    shutil.copytree(REFERENCE / "registry", base / "registry")
    artifact_root = Path(tmp) / "repo" / ".beads" / "artifacts" / "compact-case"
    artifact_root.mkdir(parents=True)
    (artifact_root / "FEATURE.json").write_text(json.dumps({
        "feature_slug": "compact-case",
        "artifact_root": ".beads/artifacts/compact-case",
        "artifact_density": "compact",
        "lifecycle_status": "active",
        "current_owner": "beo-validate",
        "created_at": "2026-05-14T00:00:00Z",
        "updated_at": "2026-05-14T00:00:00Z",
        "artifacts": ["FEATURE.json", "TICKET.md"],
    }))
    (artifact_root / "TICKET.md").write_text("""```yaml beo.ticket
current_owner: beo-validate
request: Test request
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
    path = base / "registry" / registry_file
    payload = json.loads(path.read_text())
    if value is None:
        payload.pop(key, None)
    else:
        payload[key] = value
    path.write_text(json.dumps(payload))
    return base, Path(tmp) / "repo"


class ApprovalCheckTests(unittest.TestCase):
    def test_human_gates_free_text_is_unresolved(self) -> None:
        self.assertTrue(approval.gates_unresolved("needs legal review"))
        self.assertTrue(approval.gates_unresolved([]))
        self.assertTrue(approval.gates_unresolved({}))

    def test_canonical_human_gates_object_can_be_resolved(self) -> None:
        self.assertFalse(
            approval.gates_unresolved(
                {
                    "status": "resolved",
                    "gates": [
                        {
                            "id": "HG-1",
                            "type": "clarification",
                            "question": "Which API should be used?",
                            "affects": ["scope"],
                            "resolution_status": "resolved",
                            "resolution_ref": "TICKET.md#Human Gates",
                        }
                    ],
                }
            )
        )
        self.assertFalse(approval.gates_unresolved({"status": "not_applicable", "gates": []}))

    def test_human_gate_approval_bearing_false_does_not_bypass_resolution(self) -> None:
        self.assertTrue(
            approval.gates_unresolved(
                {
                    "status": "resolved",
                    "gates": [
                        {
                            "id": "HG-1",
                            "type": "clarification",
                            "question": "Which API should be used?",
                            "affects": ["scope"],
                            "approval_bearing": False,
                            "resolution_status": "unresolved",
                            "resolution_ref": "",
                        }
                    ],
                }
            )
        )

    def test_human_gate_requires_canonical_gate_fields(self) -> None:
        errors = approval.validate_human_gates(
            {
                "status": "resolved",
                "gates": [
                    {
                        "id": "HG-1",
                        "type": "other",
                        "question": "",
                        "affects": ["scope", "other"],
                        "resolution_status": "resolved",
                        "resolution_ref": "user:1",
                    }
                ],
            }
        )
        paths = {error["path"] for error in errors}
        self.assertIn("human_gates.gates[0].type", paths)
        self.assertIn("human_gates.gates[0].question", paths)
        self.assertIn("human_gates.gates[0].affects", paths)

    def test_approval_ref_requires_current_envelope_hash(self) -> None:
        ref = {
            "id": "approval-1",
            "approved_by_owner": "beo-validate",
            "approved_at": "2026-05-14T00:00:00Z",
            "artifact_density": "compact",
            "selected_execution_set": "set-1",
            "execution_mode": "normal",
            "approval_projection_rule": approval.projection_rule_for_density("compact"),
            "envelope_hash": "",
            "artifact_hashes": {"approval_bearing_projection": "sha256:ticket"},
        }
        errors = approval.validate_approval_ref(
            ref,
            "compact",
            "set-1",
            "normal",
            {
                "approval_envelope": "sha256:envelope",
                "approval_bearing_projection": "sha256:ticket",
            },
        )
        self.assertIn("approval_ref.envelope_hash", {error["path"] for error in errors})

    def test_approval_ref_rejects_empty_required_identity_fields(self) -> None:
        ref = {
            "id": "",
            "approved_by_owner": "beo-validate",
            "approved_at": "",
            "artifact_density": "compact",
            "selected_execution_set": "set-1",
            "execution_mode": "normal",
            "approval_projection_rule": approval.projection_rule_for_density("compact"),
            "envelope_hash": "sha256:envelope",
            "artifact_hashes": {"approval_bearing_projection": "sha256:ticket"},
        }
        errors = approval.validate_approval_ref(
            ref,
            "compact",
            "set-1",
            "normal",
            {
                "approval_envelope": "sha256:envelope",
                "approval_bearing_projection": "sha256:ticket",
            },
        )
        error_paths = {error["path"] for error in errors}
        self.assertIn("approval_ref.id", error_paths)
        self.assertIn("approval_ref.approved_at", error_paths)

    def test_approval_ref_rejects_removed_shape_field(self) -> None:
        removed_suffix = "_" + "ver" + "sion"
        shape_field = "schema" + removed_suffix
        ref = {
            "id": "approval-1",
            "approved_by_owner": "beo-validate",
            "approved_at": "2026-05-14T00:00:00Z",
            "artifact_density": "compact",
            "selected_execution_set": "set-1",
            "execution_mode": "normal",
            "approval_projection_rule": approval.projection_rule_for_density("compact"),
            "envelope_hash": "sha256:envelope",
            "artifact_hashes": {"approval_bearing_projection": "sha256:ticket"},
            shape_field: "old",
        }
        errors = approval.validate_approval_ref(
            ref,
            "compact",
            "set-1",
            "normal",
            {
                "approval_envelope": "sha256:envelope",
                "approval_bearing_projection": "sha256:ticket",
            },
        )
        unsupported_paths = {error["path"] for error in errors if error["code"] == "UNSUPPORTED_FIELD"}
        self.assertIn(f"approval_ref.{shape_field}", unsupported_paths)

    def test_compact_requires_direct_verification_and_simple_generated_outputs(self) -> None:
        values = {
            "execution_sets": [{"id": "set-1", "items": [{"id": "item-1"}]}],
            "declared_files": ["src/a.py"],
            "human_gates": {"status": "not_applicable", "gates": []},
            "verification_contract": {"type": "manual", "commands": []},
            "generated_outputs": ["dist/a.js", "dist/b.js"],
            "risk_scope": "broad refactor",
        }
        codes = {error["code"] for error in approval.validate_compact_density(values)}
        self.assertIn("COMPACT_DENSITY_VIOLATION", codes)

    def test_review_changed_files_must_belong_to_selected_execution_set(self) -> None:
        values = {
            "changed_files": ["src/b.py"],
            "declared_files": ["src/a.py", "src/b.py"],
            "forbidden_paths": [],
            "selected_execution_set": "set-1",
            "execution_sets": [{"id": "set-1", "kind": "normal", "files": ["src/a.py"], "items": [{"id": "item-1"}]}],
        }
        codes = {error["code"] for error in approval.validate_changed_file_scope(values)}
        self.assertIn("OUT_OF_SCOPE_CHANGED_FILE", codes)

    def test_review_skipped_required_verification_command_is_missing(self) -> None:
        errors = approval.validate_verification_evidence(
            [{"command": "python3 -m unittest", "status": "skipped", "evidence_ref": "not run"}],
            {"commands": ["python3 -m unittest"]},
        )
        missing_paths = {error["path"] for error in errors if error["code"] == "MISSING_FIELD"}
        self.assertIn("verification_evidence", missing_paths)

    def test_review_rejects_uncontracted_verification_command(self) -> None:
        errors = approval.validate_verification_evidence(
            [{"command": "echo uncontracted", "status": "passed", "evidence_ref": "test-output"}],
            {"commands": ["python3 -m unittest"]},
        )
        mismatches = {error["path"] for error in errors if error["code"] == "MISMATCH"}
        self.assertIn("verification_evidence[0].command", mismatches)

    def test_required_verification_command_needs_evidence_ref(self) -> None:
        errors = approval.validate_verification_evidence(
            [{"command": "python3 -m unittest", "status": "passed", "evidence_ref": ""}],
            {"commands": ["python3 -m unittest"]},
        )
        missing_paths = {error["path"] for error in errors if error["code"] == "MISSING_FIELD"}
        self.assertIn("verification_evidence", missing_paths)
        self.assertIn("verification_evidence[0].evidence_ref", missing_paths)

    def test_malformed_skipped_verification_command_reports_command_shape_only(self) -> None:
        errors = approval.validate_verification_evidence(
            [{"command": "", "status": "skipped", "evidence_ref": "not run"}],
            {"commands": ["python3 -m unittest"]},
        )
        missing_paths = {error["path"] for error in errors if error["code"] == "MISSING_FIELD"}
        mismatch_paths = {error["path"] for error in errors if error["code"] == "MISMATCH"}
        self.assertIn("verification_evidence[0].command", missing_paths)
        self.assertNotIn("verification_evidence[0].status", mismatch_paths)

    def test_required_verification_command_cannot_be_downgraded_to_optional_skip(self) -> None:
        errors = approval.validate_verification_evidence(
            [{"command": "python3 -m unittest", "status": "skipped", "evidence_ref": "not run"}],
            {"commands": ["python3 -m unittest"], "optional_commands": ["python3 -m unittest"]},
        )
        missing_paths = {error["path"] for error in errors if error["code"] == "MISSING_FIELD"}
        mismatch_paths = {error["path"] for error in errors if error["code"] == "MISMATCH"}
        self.assertIn("verification_evidence", missing_paths)
        self.assertIn("verification_evidence[0].status", mismatch_paths)

    def test_verification_contract_rejects_blank_commands(self) -> None:
        values = {
            "execution_sets": [{"id": "set-1", "items": [{"id": "item-1"}]}],
            "declared_files": ["src/a.py"],
            "human_gates": {"status": "not_applicable", "gates": []},
            "verification_contract": {"commands": ["   "]},
            "generated_outputs": "not_applicable",
            "risk_scope": "bounded",
        }
        self.assertTrue(approval.missing_required_value("verification_contract", values["verification_contract"]))
        codes = {error["code"] for error in approval.validate_compact_density(values)}
        self.assertIn("COMPACT_DENSITY_VIOLATION", codes)

    def test_active_blocker_normalizes_safe_status_strings(self) -> None:
        self.assertFalse(approval.active_blocker(" None "))
        self.assertFalse(approval.active_blocker({"status": " Resolved "}))
        self.assertFalse(approval.active_blocker({"status": " no active blockers "}))
        self.assertFalse(approval.active_blocker({"status": "", "blocker_status": "none"}))

    def test_review_scope_handles_malformed_execution_items(self) -> None:
        values = {
            "changed_files": ["src/a.py"],
            "declared_files": ["src/a.py"],
            "forbidden_paths": [],
            "selected_execution_set": "set-1",
            "execution_sets": [{"id": "set-1", "items": None}],
        }
        self.assertEqual(approval.validate_changed_file_scope(values), [])

    def test_path_validation_rejects_parent_directory_segments(self) -> None:
        self.assertTrue(approval.unsafe_path("src/.."))
        self.assertTrue(approval.unsafe_path("src/../x"))
        self.assertFalse(approval.unsafe_path("src/file.py"))

    def test_missing_yaml_dependency_returns_structured_unavailable_payload(self) -> None:
        code = f"""
import builtins
import json
import runpy
import sys

real_import = builtins.__import__

def blocked_import(name, *args, **kwargs):
    if name == 'yaml' or name.startswith('yaml.'):
        raise ModuleNotFoundError("No module named 'yaml'")
    return real_import(name, *args, **kwargs)

builtins.__import__ = blocked_import
sys.argv = [{str(SCRIPTS / 'beo_approval_check.py')!r}]
try:
    runpy.run_path(sys.argv[0], run_name='__main__')
except SystemExit as exc:
    raise SystemExit(exc.code)
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["approval_envelope_status"], "unavailable")
        self.assertIn("REGISTRY_UNAVAILABLE", {error["code"] for error in payload["errors"]})
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_approval_registry_returns_structured_unavailable_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "reference"
            (base / "scripts").mkdir(parents=True)
            shutil.copy(SCRIPTS / "beo_approval_check.py", base / "scripts" / "beo_approval_check.py")
            shutil.copytree(REFERENCE / "registry", base / "registry")
            path = base / "registry" / "vocabulary.json"
            payload = json.loads(path.read_text())
            payload["artifact_density"] = 1
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(base / "scripts" / "beo_approval_check.py")],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["approval_envelope_status"], "unavailable")
        self.assertIn("REGISTRY_UNAVAILABLE", {error["code"] for error in payload["errors"]})
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_approval_required_fields_returns_structured_unavailable_payload(self) -> None:
        self.assert_malformed_approval_registry_unavailable("approval-envelope.json", "required_fields", ["bad-entry"])

    def test_malformed_owner_classes_returns_structured_unavailable_payload(self) -> None:
        self.assert_malformed_approval_registry_unavailable("vocabulary.json", "owner_classes", "bad")

    def test_blank_approval_required_field_id_returns_structured_unavailable_payload(self) -> None:
        required_fields = json.loads((REFERENCE / "registry" / "approval-envelope.json").read_text())["required_fields"]
        required_fields[0]["id"] = " "
        self.assert_malformed_approval_registry_unavailable("approval-envelope.json", "required_fields", required_fields)

    def test_invalid_readiness_required_value_returns_structured_unavailable_payload(self) -> None:
        invalid_values = [" ", " PASS_EXECUTE ", "NOT_A_READINESS"]
        for invalid_value in invalid_values:
            with self.subTest(invalid_value=invalid_value):
                required_fields = json.loads((REFERENCE / "registry" / "approval-envelope.json").read_text())["required_fields"]
                required_fields[0]["required_value"] = invalid_value
                self.assert_malformed_approval_registry_unavailable("approval-envelope.json", "required_fields", required_fields)

    def test_missing_approval_required_fields_returns_structured_unavailable_payload(self) -> None:
        self.assert_malformed_approval_registry_unavailable("approval-envelope.json", "required_fields", None)

    def test_missing_readiness_required_field_returns_structured_unavailable_payload(self) -> None:
        required_fields = json.loads((REFERENCE / "registry" / "approval-envelope.json").read_text())["required_fields"]
        self.assert_malformed_approval_registry_unavailable(
            "approval-envelope.json",
            "required_fields",
            [field for field in required_fields if field.get("id") != "readiness"],
        )

    def test_missing_manifest_required_fields_registry_returns_structured_unavailable_payload(self) -> None:
        self.assert_malformed_approval_registry_unavailable("artifact-schemas.json", "manifest_schema", None)

    def test_compact_field_ownership_drift_returns_structured_unavailable_payload(self) -> None:
        artifact_schemas = json.loads((REFERENCE / "registry" / "artifact-schemas.json").read_text())
        artifact_schemas["artifact_densities"]["compact"]["field_ownership"].pop("beo-plan")
        self.assert_malformed_approval_registry_unavailable(
            "artifact-schemas.json",
            "artifact_densities",
            artifact_schemas["artifact_densities"],
        )

    def test_empty_compact_field_ownership_returns_structured_unavailable_payload(self) -> None:
        artifact_schemas = json.loads((REFERENCE / "registry" / "artifact-schemas.json").read_text())
        artifact_schemas["artifact_densities"]["compact"]["field_ownership"]["beo-plan"] = []
        self.assert_malformed_approval_registry_unavailable(
            "artifact-schemas.json",
            "artifact_densities",
            artifact_schemas["artifact_densities"],
        )

    def test_blank_compact_field_ownership_returns_structured_unavailable_payload(self) -> None:
        artifact_schemas = json.loads((REFERENCE / "registry" / "artifact-schemas.json").read_text())
        artifact_schemas["artifact_densities"]["compact"]["field_ownership"]["beo-plan"] = [""]
        self.assert_malformed_approval_registry_unavailable(
            "artifact-schemas.json",
            "artifact_densities",
            artifact_schemas["artifact_densities"],
        )

    def test_manifest_values_must_match_registry_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
            manifest_path = root / ".beads" / "artifacts" / "compact-case" / "FEATURE.json"
            manifest = json.loads(manifest_path.read_text())
            manifest.update({
                "artifact_root": "wrong/path",
                "lifecycle_status": "planned",
                "current_owner": "nobody",
                "created_at": "not-a-timestamp",
                "artifacts": ["FEATURE.json", 123],
            })
            manifest_path.write_text(json.dumps(manifest))
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        error_paths = {error["path"] for error in result["errors"]}
        self.assertIn("FEATURE.json.artifact_root", error_paths)
        self.assertIn("FEATURE.json.lifecycle_status", error_paths)
        self.assertIn("FEATURE.json.current_owner", error_paths)
        self.assertIn("FEATURE.json.created_at", error_paths)
        self.assertIn("FEATURE.json.artifacts", error_paths)

    def test_removed_manifest_shape_fields_are_unsupported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
            removed_suffix = "_" + "ver" + "sion"
            shape_field = "schema" + removed_suffix
            contract_field = "beo" + "_contract" + removed_suffix
            manifest_path = root / ".beads" / "artifacts" / "compact-case" / "FEATURE.json"
            manifest = json.loads(manifest_path.read_text())
            manifest[shape_field] = "old"
            manifest[contract_field] = "old"
            manifest_path.write_text(json.dumps(manifest))
            result = approval.verify(root, "compact-case", "validate")
        unsupported_paths = {error["path"] for error in result["errors"] if error["code"] == "UNSUPPORTED_FIELD"}
        self.assertIn(f"FEATURE.json.{shape_field}", unsupported_paths)
        self.assertIn(f"FEATURE.json.{contract_field}", unsupported_paths)

    def test_compact_current_owner_can_advance_ahead_of_manifest_mirror(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
current_owner: beo-plan
owner: beo-plan
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
            manifest_path = root / ".beads" / "artifacts" / "compact-case" / "FEATURE.json"
            manifest = json.loads(manifest_path.read_text())
            manifest["current_owner"] = "beo-explore"
            manifest_path.write_text(json.dumps(manifest))
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "complete")
        self.assertNotIn("UNSAFE_IDENTITY", {error["code"] for error in result["errors"]})

    def test_compact_ticket_requires_current_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""", default_current_owner=None)
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("UNSAFE_IDENTITY", {error["code"] for error in result["errors"]})
        self.assertIn("current_owner", {error["path"] for error in result["errors"]})

    def test_compact_ticket_rejects_unknown_current_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
current_owner: mystery-owner
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("UNSAFE_IDENTITY", {error["code"] for error in result["errors"]})
        self.assertIn("current_owner", {error["path"] for error in result["errors"]})

    def test_compact_ticket_rejects_utility_current_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
current_owner: beo-reference
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("UNSAFE_IDENTITY", {error["code"] for error in result["errors"]})
        self.assertIn("current_owner", {error["path"] for error in result["errors"]})

    def test_compact_ticket_allows_runtime_support_current_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
current_owner: beo-debug
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "complete")
        self.assertNotIn("UNSAFE_IDENTITY", {error["code"] for error in result["errors"]})

    def test_compact_owner_mirror_must_match_current_owner(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
current_owner: beo-plan
owner: beo-validate
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("UNSAFE_IDENTITY", {error["code"] for error in result["errors"]})

    def assert_malformed_approval_registry_unavailable(self, filename: str, key: str, value: object | None) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base, root = write_approval_script_fixture(tmp, filename, key, value)
            result = subprocess.run(
                [
                    sys.executable,
                    str(base / "scripts" / "beo_approval_check.py"),
                    "compact-case",
                    "--artifact-root",
                    str(root),
                ],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["approval_envelope_status"], "unavailable")
        self.assertIn("REGISTRY_UNAVAILABLE", {error["code"] for error in payload["errors"]})
        self.assertNotIn("Traceback", result.stderr)

    def test_compact_yaml_parses_canonical_constraints_and_verification(self) -> None:
        parsed = approval.parse_simple_yaml(
            """non_goal_constraints:
  - do not touch auth
verification_contract:
  commands:
    - python3 -m unittest
"""
        )
        self.assertEqual(parsed["non_goal_constraints"], ["do not touch auth"])
        self.assertEqual(parsed["verification_contract"]["commands"], ["python3 -m unittest"])

    def test_compact_yaml_parses_execution_set_files(self) -> None:
        parsed = approval.parse_simple_yaml(
            """execution_sets:
  - id: set-1
    kind: normal
    files:
      - src/a.py
    items:
      - id: item-1
        files:
          - src/b.py
selected_execution_set: set-1
"""
        )
        self.assertEqual(approval.selected_execution_files(parsed), {"src/a.py", "src/b.py"})

    def test_execution_set_ids_must_be_strings(self) -> None:
        values = {
            "execution_sets": [{"id": 0, "kind": "normal", "items": [{"id": "item-1", "files": ["src/a.py"]}]}],
            "declared_files": ["src/a.py"],
            "forbidden_paths": [],
        }
        errors = approval.validate_projection_file_scope(values)
        self.assertIn("execution_sets[0].id", {error["path"] for error in errors})
        self.assertEqual(approval.execution_set_ids(values["execution_sets"]), set())

    def test_compact_ticket_uses_non_goal_constraints_as_canonical_field(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
non_goals:
  - do not edit src/b.py
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    type: manual
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
rollback_boundary: git checkout -- src/a.py
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["field_status"].get("non_goal_constraints"), "complete")
        self.assertNotIn("non_goal_constraints", {error["path"] for error in result["errors"]})

    def test_compact_ticket_derives_canonical_shorthand_before_required_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
non_goals:
  - do not edit src/b.py
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - validates compact shorthand
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "complete")
        self.assertEqual(result["field_status"].get("declared_files"), "complete")
        self.assertEqual(result["field_status"].get("execution_sets"), "complete")

    def test_compact_ticket_rejects_malformed_yaml_authority_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
declared_files: [src/a.py
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("INVALID_AUTHORITY_BLOCK", {error["code"] for error in result["errors"]})

    def test_compact_ticket_rejects_duplicate_yaml_keys(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
artifact_density: full
human_gates:
  status: not_applicable
  gates: []
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("INVALID_AUTHORITY_BLOCK", {error["code"] for error in result["errors"]})

    def test_compact_ticket_rejects_non_string_yaml_keys_before_hashing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
    1: invalid numeric key
acceptance_criteria:
  - validates compact shorthand
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("INVALID_AUTHORITY_BLOCK", {error["code"] for error in result["errors"]})

    def test_compact_ticket_rejects_yaml_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
defaults: &defaults
  commands:
    - python3 -m unittest
verification_contract: *defaults
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("INVALID_AUTHORITY_BLOCK", {error["code"] for error in result["errors"]})

    def test_compact_ticket_rejects_yaml_anchors_without_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
declared_files:
  - src/a.py
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    items:
      - id: item-1
        files:
          - src/a.py
acceptance_criteria:
  - AC-1
verification_contract: &verification
  commands:
    - python3 -m unittest
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("INVALID_AUTHORITY_BLOCK", {error["code"] for error in result["errors"]})

    def test_compact_ticket_rejects_yaml_custom_tags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates: !beo.gate not_applicable
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("INVALID_AUTHORITY_BLOCK", {error["code"] for error in result["errors"]})

    def test_compact_ticket_rejects_json_authority_fence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```json beo.ticket.old
{"artifact_density":"compact","human_gates":"not_applicable","declared_files":["src/a.py"],"forbidden_paths":[],"generated_outputs":"not_applicable","non_goal_constraints":[],"risk_scope":"not_applicable","rollback_boundary":"not_applicable","execution_sets":[{"id":"set-1","items":[{"id":"item-1","files":["src/a.py"]}]}],"acceptance_criteria":["AC-1"],"verification_contract":{"commands":["python3 -m unittest"]}}
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("INVALID_AUTHORITY_BLOCK", {error["code"] for error in result["errors"]})

    def test_compact_ticket_rejects_json_authority_fence_even_with_valid_yaml(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```json beo.ticket.old
{"artifact_density":"compact"}
```

```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
declared_files:
  - src/a.py
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    items:
      - id: item-1
        files:
          - src/a.py
acceptance_criteria:
  - AC-1
verification_contract:
  commands:
    - python3 -m unittest
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("INVALID_AUTHORITY_BLOCK", {error["code"] for error in result["errors"]})

    def test_compact_ticket_hashes_derived_shorthand_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
non_goals:
  - do not edit src/b.py
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - validates compact shorthand
```
""")
            result = approval.verify(root, "compact-case", "validate")
        expected_projection = {
            "request": "Test request",
            "declared_files": ["src/a.py"],
            "forbidden_paths": [],
            "generated_outputs": "not_applicable",
            "verification_contract": {"commands": ["python3 -m unittest"]},
            "execution_sets": [{"id": "set-1", "kind": "normal", "files": ["src/a.py"], "items": [{"id": "item-1", "description": "update the checker"}]}],
            "acceptance_criteria": ["validates compact shorthand"],
            "non_goal_constraints": ["do not edit src/b.py"],
            "risk_scope": "not_applicable",
            "rollback_boundary": "not_applicable",
            "human_gates": {"status": "not_applicable", "gates": []},
        }
        self.assertEqual(result["machine_hashes"]["approval_bearing_projection"], approval.stable_hash(expected_projection))

    def test_compact_ticket_hash_binds_request(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def ticket(request: str) -> str:
                return f"""```yaml beo.ticket
current_owner: beo-validate
request: {request}
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
non_goals:
  - do not edit src/b.py
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - validates compact shorthand
```
"""

            write_compact_fixture(root, ticket("Initial request"))
            first = approval.verify(root, "compact-case", "validate")
            (root / ".beads" / "artifacts" / "compact-case" / "TICKET.md").write_text(ticket("Changed request"))
            second = approval.verify(root, "compact-case", "validate")
        self.assertNotEqual(
            first["machine_hashes"]["approval_bearing_projection"],
            second["machine_hashes"]["approval_bearing_projection"],
        )

    def test_compact_ticket_rejects_contradictory_expanded_projection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - validates compact shorthand
declared_files:
  - src/b.py
execution_sets:
  - id: set-1
    items:
      - id: item-1
        description: update the checker
        files:
          - src/b.py
verification_contract:
  commands:
    - python3 -m unittest
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("CONTRADICTORY_PROJECTION", {error["code"] for error in result["errors"]})

    def test_compact_ticket_preserves_specified_optional_projection_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - validates compact shorthand
generated_outputs:
  - dist/a.json
risk_scope: bounded generated output
rollback_boundary: revert declared file changes
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "complete")
        self.assertEqual(result["field_status"].get("generated_outputs"), "complete")

    def test_validate_rejects_invalid_declared_paths_before_pass_execute(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
declared_files:
  - /etc/passwd
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    items:
      - id: item-1
        files:
          - /etc/passwd
acceptance_criteria:
  - AC-1
verification_contract:
  commands:
    - python3 -m unittest
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("INVALID_PATH", {error["code"] for error in result["errors"]})

    def test_validate_rejects_malformed_path_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
declared_files:
  - 123
forbidden_paths:
  - false
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    kind: normal
    files:
      - path: src/a.py
      - bad: src/b.py
    items:
      - id: item-1
        files:
          - 456
acceptance_criteria:
  - AC-1
verification_contract:
  commands:
    - python3 -m unittest
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        error_paths = {error["path"] for error in result["errors"]}
        self.assertIn("declared_files[0]", error_paths)
        self.assertIn("forbidden_paths[0]", error_paths)
        self.assertIn("execution_sets[0].files[1]", error_paths)
        self.assertIn("execution_sets[0].items[0].files[0]", error_paths)

    def test_validate_rejects_execution_set_files_outside_declared_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_validate_fixture(root, "not_applicable")
            plan_path = root / ".beads" / "artifacts" / "full-case" / "PLAN.md"
            plan_path.write_text("""```yaml beo.plan
declared_files:
  - src/a.py
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    kind: normal
    items:
      - id: item-1
        files:
          - src/b.py
acceptance_criteria:
  - AC-1
verification_contract:
  commands:
    - python3 -m unittest
```
""")
            result = approval.verify(root, "full-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("OUT_OF_SCOPE_EXECUTION_FILE", {error["code"] for error in result["errors"]})

    def test_full_validate_rejects_unresolved_human_gates_before_pass_execute(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_validate_fixture(root, "unresolved")
            result = approval.verify(root, "full-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("human_gates", {error["path"] for error in result["errors"]})

    def test_full_validate_requires_request_before_pass_execute(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_validate_fixture(root, "not_applicable")
            context_path = root / ".beads" / "artifacts" / "full-case" / "CONTEXT.md"
            context_path.write_text("""```yaml beo.context
human_gates:
  status: not_applicable
  gates: []
```
""")
            result = approval.verify(root, "full-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("request", {error["path"] for error in result["errors"]})

    def test_full_validate_rejects_old_authority_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_validate_fixture(root, "not_applicable")
            context_path = root / ".beads" / "artifacts" / "full-case" / "CONTEXT.md"
            plan_path = root / ".beads" / "artifacts" / "full-case" / "PLAN.md"
            old_context = "beo.context." + "v1"
            old_plan = "beo.plan." + "v1"
            context_path.write_text(context_path.read_text().replace("beo.context", old_context))
            plan_path.write_text(plan_path.read_text().replace("beo.plan", old_plan))
            result = approval.verify(root, "full-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("UNSUPPORTED_MARKER", {error["code"] for error in result["errors"]})

    def test_compact_projection_ignores_nested_non_projection_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
notes:
  declared_files:
    - src/a.py
  forbidden_paths: []
  generated_outputs: not_applicable
  non_goal_constraints: []
  risk_scope: not_applicable
  rollback_boundary: not_applicable
  execution_sets:
    - id: set-1
      items:
        - id: item-1
          files:
            - src/a.py
  acceptance_criteria:
    - AC-1
  verification_contract:
    commands:
      - python3 -m unittest
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        missing_paths = {error["path"] for error in result["errors"] if error["code"] == "MISSING_FIELD"}
        self.assertIn("declared_files", missing_paths)
        self.assertEqual(result["field_status"].get("declared_files"), "missing")

    def test_compact_projection_derives_default_optional_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "complete")
        self.assertEqual(result["field_status"].get("generated_outputs"), "complete")
        self.assertEqual(result["field_status"].get("non_goal_constraints"), "complete")
        self.assertEqual(result["field_status"].get("risk_scope"), "complete")
        self.assertEqual(result["field_status"].get("rollback_boundary"), "complete")

    def test_compact_expanded_projection_without_marker_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
declared_files:
  - src/a.py
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    items:
      - id: item-1
        files:
          - src/a.py
acceptance_criteria:
  - AC-1
verification_contract:
  commands:
    - python3 -m unittest
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("UNSUPPORTED_FIELD", {error["code"] for error in result["errors"]})
        self.assertFalse(any("projection_generated_by" in warning for warning in result["warnings"]))

    def test_compact_ticket_requires_explicit_shorthand_forbidden_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - validates compact shorthand
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("scope.files.forbid", {error["path"] for error in result["errors"]})

    def test_markdown_section_ticket_cannot_satisfy_approval_bearing_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """# TICKET.md

## Request
Update the checker.

## Done
- validates compact shorthand

## Human Gates
not_applicable

## Scope
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
non_goals:
  - do not edit src/b.py
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("MISSING_AUTHORITY_BLOCK", {error["code"] for error in result["errors"]})
        self.assertTrue(any("structured authority block" in error["expected"] for error in result["errors"]))
        self.assertTrue(any("draft-only" in error["observed"] for error in result["errors"]))
        self.assertEqual(result["field_status"].get("declared_files"), "missing")

    def test_malformed_markdown_fallback_returns_invalid_payload(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """# TICKET.md

## Request
foo: [
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("MISSING_AUTHORITY_BLOCK", {error["code"] for error in result["errors"]})

    def test_execute_requires_direct_selected_execution_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
readiness: PASS_EXECUTE
approval_ref:
  id: approval-1
  approved_by_owner: beo-validate
  approved_at: 2026-05-14T00:00:00Z
  artifact_density: compact
  selected_execution_set: set-1
  execution_mode: normal
  approval_projection_rule: compact_derived
  envelope_hash: sha256:placeholder
  artifact_hashes:
    approval_bearing_projection: sha256:placeholder
integrity:
  status: verified
  evidence_ref: beo_approval_check:test
```
""")
            result = approval.verify(root, "compact-case", "execute")
        missing_paths = {error["path"] for error in result["errors"] if error["code"] == "MISSING_FIELD"}
        self.assertIn("selected_execution_set", missing_paths)
        self.assertIn("execution_mode", missing_paths)

    def test_execute_rejects_invalid_declared_paths_before_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def ticket(envelope_hash: str, artifact_hash: str) -> str:
                return f"""```yaml beo.ticket
current_owner: beo-validate
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
declared_files:
  - /etc/passwd
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    items:
      - id: item-1
        files:
          - /etc/passwd
acceptance_criteria:
  - AC-1
verification_contract:
  commands:
    - python3 -m unittest
readiness: PASS_EXECUTE
approval_ref:
  id: approval-1
  approved_by_owner: beo-validate
  approved_at: "2026-05-14T00:00:00Z"
  artifact_density: compact
  selected_execution_set: set-1
  execution_mode: normal
  approval_projection_rule: {approval.projection_rule_for_density("compact")}
  envelope_hash: {envelope_hash}
  artifact_hashes:
    approval_bearing_projection: {artifact_hash}
integrity:
  status: verified
  evidence_ref: beo_approval_check:test
selected_execution_set: set-1
execution_mode: normal
```
"""

            write_compact_fixture(root, ticket("sha256:placeholder", "sha256:placeholder"))
            first_result = approval.verify(root, "compact-case", "execute")
            (root / ".beads" / "artifacts" / "compact-case" / "TICKET.md").write_text(
                ticket(
                    first_result["machine_hashes"]["approval_envelope"],
                    first_result["machine_hashes"]["approval_bearing_projection"],
                )
            )
            result = approval.verify(root, "compact-case", "execute")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("INVALID_PATH", {error["code"] for error in result["errors"]})

    def test_execute_rejects_malformed_scalar_fields_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, f"""```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
readiness: PASS_EXECUTE
approval_ref:
  id: approval-1
  approved_by_owner: beo-validate
  approved_at: "2026-05-14T00:00:00Z"
  artifact_density: compact
  selected_execution_set: set-1
  execution_mode: normal
  approval_projection_rule: {approval.projection_rule_for_density("compact")}
  envelope_hash: sha256:placeholder
  artifact_hashes: {{}}
integrity:
  status: verified
  evidence_ref: beo_approval_check:test
selected_execution_set: set-1
execution_mode:
  - normal
changed_files:
  - src/a.py
```
""")
            result = approval.verify(root, "compact-case", "execute")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("execution_mode", {error["path"] for error in result["errors"]})

    def test_execute_rejects_falsey_non_string_selected_execution_set(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, f"""```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
readiness: PASS_EXECUTE
approval_ref:
  id: approval-1
  approved_by_owner: beo-validate
  approved_at: "2026-05-14T00:00:00Z"
  artifact_density: compact
  selected_execution_set: 0
  execution_mode: normal
  approval_projection_rule: {approval.projection_rule_for_density("compact")}
  envelope_hash: sha256:placeholder
  artifact_hashes: {{}}
integrity:
  status: verified
  evidence_ref: beo_approval_check:test
selected_execution_set: 0
execution_mode: normal
changed_files:
  - src/a.py
```
""")
            result = approval.verify(root, "compact-case", "execute")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("selected_execution_set", {error["path"] for error in result["errors"]})

    def test_execute_rejects_out_of_scope_changed_files_before_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            def ticket(envelope_hash: str, artifact_hash: str) -> str:
                return f"""```yaml beo.ticket
current_owner: beo-validate
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid:
      - src/secret.py
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
readiness: PASS_EXECUTE
approval_ref:
  id: approval-1
  approved_by_owner: beo-validate
  approved_at: "2026-05-14T00:00:00Z"
  artifact_density: compact
  selected_execution_set: set-1
  execution_mode: normal
  approval_projection_rule: {approval.projection_rule_for_density("compact")}
  envelope_hash: {envelope_hash}
  artifact_hashes:
    approval_bearing_projection: {artifact_hash}
integrity:
  status: verified
  evidence_ref: beo_approval_check:test
selected_execution_set: set-1
execution_mode: normal
changed_files:
  - src/secret.py
```
"""

            write_compact_fixture(root, ticket("sha256:placeholder", "sha256:placeholder"))
            first_result = approval.verify(root, "compact-case", "execute")
            (root / ".beads" / "artifacts" / "compact-case" / "TICKET.md").write_text(
                ticket(
                    first_result["machine_hashes"]["approval_envelope"],
                    first_result["machine_hashes"]["approval_bearing_projection"],
                )
            )
            result = approval.verify(root, "compact-case", "execute")
        codes = {error["code"] for error in result["errors"]}
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("OUT_OF_SCOPE_CHANGED_FILE", codes)
        self.assertIn("FORBIDDEN_CHANGED_FILE", codes)

    def test_verify_accepts_direct_artifact_root_with_feature_slug(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
            result = approval.verify(root / ".beads" / "artifacts" / "compact-case", "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "complete")

    def test_verify_uses_state_feature_when_slug_is_omitted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
            other_root = root / ".beads" / "artifacts" / "other-case"
            other_root.mkdir(parents=True)
            (other_root / "FEATURE.json").write_text(json.dumps({"feature_slug": "other-case"}))
            (root / ".beads" / "STATE.json").write_text(json.dumps({"active": {"feature": "compact-case"}}))
            result = approval.verify(root, None, "validate")
        self.assertEqual(result["approval_envelope_status"], "complete")
        self.assertEqual(result["feature_slug"], "compact-case")

    def test_approval_envelope_hash_binds_approval_ref_metadata(self) -> None:
        values = {
            "readiness": "PASS_EXECUTE",
            "approval_ref": {
                "id": "approval-1",
                "approved_by_owner": "beo-validate",
                "approved_at": "2026-05-14T00:00:00Z",
                "artifact_density": "compact",
                "selected_execution_set": "set-1",
                "execution_mode": "normal",
                "approval_projection_rule": approval.projection_rule_for_density("compact"),
                "envelope_hash": "ignored",
                "artifact_hashes": {"approval_bearing_projection": "ignored"},
            },
            "selected_execution_set": "set-1",
            "execution_mode": "normal",
        }
        changed = json.loads(json.dumps(values))
        changed["approval_ref"]["id"] = "approval-2"
        self.assertNotEqual(approval.approval_envelope_hash(values), approval.approval_envelope_hash(changed))

    def test_validate_rejects_empty_required_approval_arrays(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
declared_files: []
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets: []
acceptance_criteria: []
verification_contract:
  commands: []
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("declared_files", {error["path"] for error in result["errors"]})
        self.assertIn("execution_sets", {error["path"] for error in result["errors"]})

    def test_validate_required_fields_are_registry_driven(self) -> None:
        registry_field = {
            "id": "registry_only_required",
            "owner": "beo-plan",
            "compact_source": "TICKET.md `beo.ticket` registry_only_required",
            "full_source": "PLAN.md#registry_only_required",
        }
        try:
            approval.APPROVAL_ENVELOPE["required_fields"].append(registry_field)
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
                result = approval.verify(root, "compact-case", "validate")
        finally:
            approval.APPROVAL_ENVELOPE["required_fields"].remove(registry_field)
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("registry_only_required", {error["path"] for error in result["errors"]})

    def test_validate_defers_only_pass_execute_approval_fields(self) -> None:
        registry_field = {
            "id": "future_validate_field",
            "owner": "beo-validate",
            "compact_source": "TICKET.md `beo.ticket` future_validate_field",
            "full_source": "PLAN.md#future_validate_field",
        }
        try:
            approval.APPROVAL_ENVELOPE["required_fields"].append(registry_field)
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
```
""")
                result = approval.verify(root, "compact-case", "validate")
        finally:
            approval.APPROVAL_ENVELOPE["required_fields"].remove(registry_field)
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("future_validate_field", {error["path"] for error in result["errors"]})

    def test_validate_rejects_compact_density_violations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
declared_files:
  - src/a.py
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    items:
      - id: item-1
        files:
          - src/a.py
  - id: set-2
    items:
      - id: item-2
        files:
          - src/a.py
acceptance_criteria:
  - AC-1
verification_contract:
  commands:
    - python3 -m unittest
```
""")
            result = approval.verify(root, "compact-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("COMPACT_DENSITY_VIOLATION", {error["code"] for error in result["errors"]})

    def test_review_rejects_empty_compact_evidence_lists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
readiness: PASS_EXECUTE
approval_ref: {}
integrity:
  status: verified
  evidence_ref: beo_approval_check:test
selected_execution_set: set-1
execution_mode: normal
pre_execution_integrity_check:
  helper: beo_approval_check
  evidence_ref: beo_approval_check:test
  approval_envelope_status: complete
changed_files: []
verification_evidence: []
execution_status: ready_for_review
review_status: ready_for_review
blocker: none
```
""")
            result = approval.verify(root, "compact-case", "review")
        missing_paths = {error["path"] for error in result["errors"] if error["code"] == "MISSING_FIELD"}
        self.assertIn("changed_files", missing_paths)
        self.assertIn("verification_evidence", missing_paths)
        self.assertEqual(result["field_status"].get("changed_files"), "missing")
        self.assertEqual(result["field_status"].get("verification_evidence"), "missing")

    def test_review_rejects_malformed_compact_verification_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
readiness: PASS_EXECUTE
approval_ref: {}
integrity:
  status: verified
  evidence_ref: beo_approval_check:test
selected_execution_set: set-1
execution_mode: normal
pre_execution_integrity_check:
  helper: beo_approval_check
  evidence_ref: beo_approval_check:test
  approval_envelope_status: complete
changed_files:
  - src/a.py
verification_evidence:
  - command: "   "
    status: passed
    evidence_ref: ""
execution_status: ready_for_review
review_status: ready_for_review
blocker: none
```
""")
            result = approval.verify(root, "compact-case", "review")
        missing_paths = {error["path"] for error in result["errors"] if error["code"] == "MISSING_FIELD"}
        self.assertIn("verification_evidence[0].command", missing_paths)
        self.assertIn("verification_evidence[0].evidence_ref", missing_paths)

    def test_review_rejects_active_compact_blocker(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
readiness: PASS_EXECUTE
approval_ref: {}
integrity:
  status: verified
  evidence_ref: beo_approval_check:test
selected_execution_set: set-1
execution_mode: normal
pre_execution_integrity_check:
  helper: beo_approval_check
  evidence_ref: beo_approval_check:test
  approval_envelope_status: complete
changed_files:
  - src/a.py
verification_evidence:
  - command: python3 -m unittest
    status: passed
    evidence_ref: test-output
execution_status: ready_for_review
review_status: ready_for_review
blocker: tests failing
```
""")
            result = approval.verify(root, "compact-case", "review")
        self.assertIn("blocker", {error["path"] for error in result["errors"]})

    def test_review_rejects_invalid_compact_pre_execution_integrity_check(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_compact_fixture(root, """```yaml beo.ticket
artifact_density: compact
human_gates:
  status: not_applicable
  gates: []
scope:
  files:
    allow:
      - src/a.py
    forbid: []
  item: update the checker
  verify:
    commands:
      - python3 -m unittest
acceptance_criteria:
  - AC-1
readiness: PASS_EXECUTE
approval_ref: {}
integrity:
  status: verified
  evidence_ref: beo_approval_check:test
selected_execution_set: set-1
execution_mode: normal
pre_execution_integrity_check:
  helper: other
  evidence_ref: beo_approval_check:test
  approval_envelope_status: invalid
changed_files:
  - src/a.py
verification_evidence:
  - command: python3 -m unittest
    status: passed
    evidence_ref: test-output
execution_status: ready_for_review
review_status: ready_for_review
blocker: none
```
""")
            result = approval.verify(root, "compact-case", "review")
        paths = {error["path"] for error in result["errors"]}
        self.assertIn("pre_execution_integrity_check.helper", paths)
        self.assertIn("pre_execution_integrity_check.approval_envelope_status", paths)

    def test_full_review_tracker_must_match_current_approval_binding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_review_fixture(root, {
                "ledger_status": "ready_for_review",
                "approval_ref_id": "approval-stale",
                "selected_execution_set": "set-1",
                "execution_mode": "go",
                "changed_files": ["src/a.py"],
                "blockers": [],
            })
            result = approval.verify(root, "full-case", "review")
        paths = {error["path"] for error in result["errors"]}
        self.assertIn("TRACKER.json.approval_ref_id", paths)
        self.assertIn("TRACKER.json.execution_mode", paths)

    def test_full_review_tracker_requires_binding_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_review_fixture(root, {
                "ledger_status": "ready_for_review",
                "changed_files": ["src/a.py"],
            })
            result = approval.verify(root, "full-case", "review")
        paths = {error["path"] for error in result["errors"] if error["code"] == "MISSING_FIELD"}
        self.assertIn("TRACKER.json.approval_ref_id", paths)
        self.assertIn("TRACKER.json.selected_execution_set", paths)
        self.assertIn("TRACKER.json.execution_mode", paths)
        self.assertIn("TRACKER.json.blockers", paths)

    def test_full_review_tracker_requires_complete_ledger_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_review_fixture(root, {
                "ledger_status": "ready_for_review",
                "approval_ref_id": "approval-current",
                "selected_execution_set": "set-1",
                "execution_mode": "normal",
                "changed_files": ["src/a.py"],
                "blockers": [],
            })
            result = approval.verify(root, "full-case", "review")
        paths = {error["path"] for error in result["errors"] if error["code"] == "MISSING_FIELD"}
        self.assertIn("TRACKER.json.items", paths)
        self.assertIn("TRACKER.json.observations", paths)
        self.assertIn("TRACKER.json.scope_delta_requests", paths)
        self.assertIn("TRACKER.json.repair_budget", paths)
        self.assertIn("TRACKER.json.resume_point", paths)
        self.assertIn("TRACKER.json.rollback_status", paths)

    def test_full_review_tracker_allows_empty_noop_ledger_lists(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_review_fixture(root, {
                "feature_slug": "full-case",
                "artifact_root": ".beads/artifacts/full-case",
                "ledger_status": "ready_for_review",
                "approval_ref_id": "approval-current",
                "selected_execution_set": "set-1",
                "execution_mode": "normal",
                "items": [{"id": "item-1", "status": "applied"}],
                "changed_files": ["src/a.py"],
                "observations": [],
                "blockers": [],
                "scope_delta_requests": [],
                "repair_budget": {"used": 0, "limit": 0},
                "resume_point": "complete",
                "rollback_status": "not_applicable",
            })
            result = approval.verify(root, "full-case", "review")
        paths = {error["path"] for error in result["errors"] if error["code"] == "MISSING_FIELD"}
        self.assertNotIn("TRACKER.json.observations", paths)
        self.assertNotIn("TRACKER.json.blockers", paths)
        self.assertNotIn("TRACKER.json.scope_delta_requests", paths)

    def test_full_review_tracker_requires_list_typed_noop_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_review_fixture(root, {
                "feature_slug": "full-case",
                "artifact_root": ".beads/artifacts/full-case",
                "ledger_status": "ready_for_review",
                "approval_ref_id": "approval-current",
                "selected_execution_set": "set-1",
                "execution_mode": "normal",
                "items": [{"id": "item-1", "status": "applied"}],
                "changed_files": ["src/a.py"],
                "observations": {},
                "blockers": "none",
                "scope_delta_requests": {},
                "repair_budget": {"used": 0, "limit": 0},
                "resume_point": "complete",
                "rollback_status": "not_applicable",
            })
            result = approval.verify(root, "full-case", "review")
        paths = {error["path"] for error in result["errors"] if error["code"] == "MISSING_FIELD"}
        self.assertIn("TRACKER.json.observations", paths)
        self.assertIn("TRACKER.json.blockers", paths)
        self.assertIn("TRACKER.json.scope_delta_requests", paths)

    def test_full_review_rejects_empty_tracker_object(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_review_fixture(root, {})
            result = approval.verify(root, "full-case", "review")
        paths = {error["path"] for error in result["errors"] if error["code"] == "MISSING_FIELD"}
        self.assertIn("TRACKER.json.approval_ref_id", paths)
        self.assertIn("TRACKER.json.ledger_status", paths)
        self.assertIn("TRACKER.json.selected_execution_set", paths)
        self.assertIn("TRACKER.json.execution_mode", paths)
        self.assertIn("TRACKER.json.changed_files", paths)
        self.assertIn("TRACKER.json.blockers", paths)

    def test_full_review_tracker_matching_binding_has_no_binding_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_review_fixture(root, {
                "ledger_status": "ready_for_review",
                "approval_ref_id": "approval-current",
                "selected_execution_set": "set-1",
                "execution_mode": "normal",
                "changed_files": ["src/a.py"],
                "blockers": [],
            })
            result = approval.verify(root, "full-case", "review")
        binding_paths = {
            "TRACKER.json.approval_ref_id",
            "TRACKER.json.selected_execution_set",
            "TRACKER.json.execution_mode",
        }
        self.assertFalse(binding_paths & {error["path"] for error in result["errors"]})

    def test_full_review_uses_top_level_tracker_changed_files_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_full_review_fixture(root, {
                "feature_slug": "full-case",
                "artifact_root": ".beads/artifacts/full-case",
                "approval_ref_id": "approval-current",
                "ledger_status": "ready_for_review",
                "pre_execution_integrity_check": {
                    "helper": "beo_approval_check",
                    "evidence_ref": "beo_approval_check:test",
                    "approval_envelope_status": "complete",
                },
                "selected_execution_set": "set-1",
                "execution_mode": "normal",
                "items": [{"id": "item-1", "changed_files": ["src/a.py"]}],
                "changed_files": [],
                "observations": [],
                "blockers": [],
                "scope_delta_requests": [],
                "repair_budget": {"used": 0, "limit": 0},
                "resume_point": "complete",
                "rollback_status": "not_applicable",
            })
            result = approval.verify(root, "full-case", "review")
        self.assertIn("TRACKER.json.changed_files", {error["path"] for error in result["errors"]})

    def test_full_plan_requires_top_level_declared_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifact_root = root / ".beads" / "artifacts" / "full-case"
            artifact_root.mkdir(parents=True)
            manifest = {
                "feature_slug": "full-case",
                "artifact_root": ".beads/artifacts/full-case",
                "artifact_density": "full",
                "lifecycle_status": "active",
                "current_owner": "beo-validate",
                "created_at": "2026-05-14T00:00:00Z",
                "updated_at": "2026-05-14T00:00:00Z",
                "artifacts": ["FEATURE.json", "CONTEXT.md", "PLAN.md"],
            }
            (artifact_root / "FEATURE.json").write_text(json.dumps(manifest))
            (artifact_root / "CONTEXT.md").write_text("""```yaml beo.context
human_gates:
  status: not_applicable
  gates: []
```
""")
            (artifact_root / "PLAN.md").write_text("""```yaml beo.plan
forbidden_paths: []
generated_outputs: not_applicable
non_goal_constraints: []
risk_scope: not_applicable
rollback_boundary: not_applicable
execution_sets:
  - id: set-1
    items:
      - id: item-1
        declared_files:
          - src/a.py
acceptance_criteria:
  - AC-1
verification_contract:
  commands:
    - python3 -m unittest
```
""")
            result = approval.verify(root, "full-case", "validate")
        self.assertEqual(result["approval_envelope_status"], "invalid")
        self.assertIn("declared_files", {error["path"] for error in result["errors"]})


class RegistryCheckTests(unittest.TestCase):
    def test_acceptance_refs_is_not_a_required_approval_field(self) -> None:
        approval_envelope = json.loads((REFERENCE / "registry" / "approval-envelope.json").read_text())
        ids = {field["id"] for field in approval_envelope["required_fields"]}
        self.assertIn("acceptance_criteria", ids)
        self.assertNotIn("acceptance_refs", ids)

    def test_compact_approval_sources_name_authority_block_not_markdown_headings(self) -> None:
        approval_envelope = json.loads((REFERENCE / "registry" / "approval-envelope.json").read_text())
        compact_sources = [field["compact_source"] for field in approval_envelope["required_fields"]]
        self.assertTrue(all(source.startswith("TICKET.md `beo.ticket` ") for source in compact_sources))
        self.assertFalse(any("TICKET.md#" in source for source in compact_sources))

    def test_human_gate_shape_is_shared_not_compact_local(self) -> None:
        artifact_schemas = json.loads((REFERENCE / "registry" / "artifact-schemas.json").read_text())
        self.assertIn("human_gate_shape", artifact_schemas["shared_shapes"])
        self.assertNotIn("human_gate_shape", artifact_schemas["artifact_densities"]["compact"])
        self.assertNotIn("documented TICKET.md markdown sections", artifact_schemas["artifact_densities"]["compact"]["authority_blocks"])
        self.assertNotIn("severity", artifact_schemas["shared_shapes"]["human_gate_shape"]["gates"][0])

    def test_registry_schema_accepts_compact_metadata_fields(self) -> None:
        artifact_schemas = json.loads((REFERENCE / "registry" / "artifact-schemas.json").read_text())
        schema = json.loads((REFERENCE / "registry" / "registry.schema.json").read_text())
        errors: list[str] = []
        registry_check.validate_schema_node(
            errors,
            "artifact-schemas.json",
            "<root>",
            artifact_schemas,
            schema["definitions"]["artifact-schemas"],
            schema,
        )
        self.assertEqual([], errors)

    def test_compact_field_ownership_covers_identity_handoff_fields(self) -> None:
        artifact_schemas = json.loads((REFERENCE / "registry" / "artifact-schemas.json").read_text())
        ownership = artifact_schemas["artifact_densities"]["compact"]["field_ownership"]
        self.assertLessEqual(
            {"artifact_density", "phase_status", "current_owner", "owner"},
            set(ownership["beo-explore"]),
        )
        for owner in ["beo-explore", "beo-plan", "beo-validate", "beo-execute", "beo-review", "beo-route"]:
            self.assertLessEqual({"phase_status", "current_owner", "owner"}, set(ownership[owner]))

    def test_human_gate_docs_keep_soft_assumptions_out_of_gate_shape(self) -> None:
        text = (REFERENCE / "references" / "decision-boundaries.md").read_text()
        self.assertIn("Do not use Human Gates for soft assumptions", text)
        self.assertIn("assumptions", text)
        self.assertIn("Every listed gate is approval-bearing", text)
        self.assertNotIn("soft_assumption", text)

    def test_approval_check_declares_yaml_dependency_contract(self) -> None:
        command_contracts = json.loads((REFERENCE / "registry" / "command-contracts.json").read_text())
        approval_check = next(
            command for command in command_contracts["commands"]
            if command["command_id"] == "beo.approval_check"
        )
        dependencies = set(approval_check["runtime_dependencies"])
        self.assertIn("PyYAML importable as yaml", dependencies)
        self.assertIn("StrictYamlLoader duplicate-key rejection enabled", dependencies)
        self.assertTrue(any("BEO YAML subset enforced" in item for item in dependencies))
        self.assertIn("missing runtime dependency", approval_check["failure_handling"])
        self.assertIn("missing structured authority block", approval_check["failure_handling"])

    def test_helper_output_schema_accepts_unknown_density_status(self) -> None:
        vocabulary = json.loads((REFERENCE / "registry" / "vocabulary.json").read_text())
        helper_schema = json.loads((REFERENCE / "registry" / "helper-output-schema.json").read_text())
        density_ref = helper_schema["fields"]["artifact_density"]["allowed_values_ref"]
        self.assertIn("unknown", vocabulary[density_ref])

    def test_registry_check_rejects_unknown_helper_output_allowed_values_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "helper-output-schema.json"
            payload = json.loads(path.read_text())
            payload["fields"]["artifact_density"]["allowed_values_ref"] = "missing_vocab_field"
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("allowed_values_ref points to unknown string-list vocabulary field", result.stdout)

    def test_registry_check_reports_malformed_vocabulary_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "vocabulary.json"
            payload = json.loads(path.read_text())
            payload["runtime_owners"] = 1
            payload["style_forbidden_aliases"] = []
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('"status": "invalid"', result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_registry_check_reports_malformed_pipeline_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "pipeline.json"
            payload = json.loads(path.read_text())
            payload["transitions"] = ["bad-entry"]
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('"status": "invalid"', result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_registry_check_reports_malformed_transition_fields_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "pipeline.json"
            payload = json.loads(path.read_text())
            payload["transitions"][0]["to"] = []
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('"status": "invalid"', result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_registry_check_reports_malformed_registry_schema_without_traceback(self) -> None:
        schema_cases = [
            ("root", "[]"),
            ("definitions", '{"definitions": []}'),
            ("object_shape", None),
            ("missing_type", {"properties": {}}),
            ("bad_type", {"type": "nonsense"}),
            ("bad_enum", {"type": "object", "required": [], "properties": {"description": {"type": "string", "enum": "bad"}}}),
            ("bad_additional_properties", {"type": "object", "required": [], "properties": {}, "additionalProperties": []}),
            ("bad_required_entry", {"type": "object", "required": [1], "properties": {}}),
            ("bad_min_items", {"type": "array", "minItems": "bad", "items": {"type": "string"}}),
        ]
        for case_name, schema_override in schema_cases:
            with self.subTest(case_name=case_name):
                with tempfile.TemporaryDirectory() as tmp:
                    base = Path(tmp)
                    registry = base / "registry"
                    shutil.copytree(REFERENCE / "registry", registry)
                    shutil.copytree(REFERENCE / "references", base / "references")
                    shutil.copytree(REFERENCE / "assets", base / "assets")
                    schema_path = registry / "registry.schema.json"
                    if isinstance(schema_override, dict):
                        payload = json.loads(schema_path.read_text())
                        payload["definitions"]["pipeline"] = schema_override
                        schema_path.write_text(json.dumps(payload))
                    elif schema_override is None:
                        payload = json.loads(schema_path.read_text())
                        payload["definitions"]["pipeline"] = {"type": "object", "required": "bad", "properties": []}
                        schema_path.write_text(json.dumps(payload))
                    else:
                        schema_path.write_text(schema_override)
                    result = subprocess.run(
                        [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('"status": "invalid"', result.stdout)
                self.assertIn("registry.schema.json schema error", result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_registry_check_reports_malformed_approval_fields_without_traceback(self) -> None:
        malformed_cases = [
            (None, ("schema error",)),
            ("bad-entry", ("schema error",)),
            ({"id": "", "required_value": "PASS_EXECUTE"}, ("schema error", "required_fields[", "].id")),
            ({"id": " ", "required_value": "PASS_EXECUTE"}, ("required_fields[", "].id", "non-blank")),
            ({"id": "readiness", "required_value": []}, ("schema error", "required_value")),
            ({"id": "readiness", "required_value": ""}, ("schema error", "required_value")),
            ({"id": "readiness", "required_value": " "}, ("required_value", "non-blank")),
            ({"id": "readiness", "required_value": " PASS_EXECUTE "}, ("required_value", "surrounding whitespace")),
            ({"id": "readiness", "required_value": "NOT_A_READINESS"}, ("required_value", "not registered readiness")),
        ]
        for entry, expected_snippets in malformed_cases:
            with self.subTest(entry=entry):
                with tempfile.TemporaryDirectory() as tmp:
                    base = Path(tmp)
                    registry = base / "registry"
                    shutil.copytree(REFERENCE / "registry", registry)
                    shutil.copytree(REFERENCE / "references", base / "references")
                    shutil.copytree(REFERENCE / "assets", base / "assets")
                    path = registry / "approval-envelope.json"
                    payload = json.loads(path.read_text())
                    if entry is None:
                        payload = []
                    else:
                        payload["required_fields"].append(entry)
                    path.write_text(json.dumps(payload))
                    result = subprocess.run(
                        [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('"status": "invalid"', result.stdout)
                self.assertIn("approval-envelope.json", result.stdout)
                for expected_snippet in expected_snippets:
                    self.assertIn(expected_snippet, result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_registry_check_requires_readiness_required_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "approval-envelope.json"
            payload = json.loads(path.read_text())
            for field in payload["required_fields"]:
                if field.get("id") == "readiness":
                    field.pop("required_value")
                    break
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("readiness required_value is required", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_registry_check_reports_malformed_artifact_schema_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "artifact-schemas.json"
            payload = json.loads(path.read_text())
            payload["artifact_densities"] = []
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('"status": "invalid"', result.stdout)
        self.assertIn("artifact-schemas.json schema error", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_registry_check_rejects_owner_class_duplicates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "vocabulary.json"
            payload = json.loads(path.read_text())
            payload["owner_classes"]["maintenance"].append("beo-explore")
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("owner_classes assigns owners to multiple classes", result.stdout)

    def test_registry_check_parses_contract_exits_only(self) -> None:
        text = """# skill
Exit summary (non-authoritative):
- `summary_only` -> `done`

## Contract

Exits:
- `real_exit` -> `beo-plan`

## Other

Exits:
- `other_exit` -> `done`
"""
        self.assertEqual(registry_check.skill_exit_pairs(text), [("real_exit", "beo-plan")])

    def test_operator_navigation_surfaces_exist(self) -> None:
        expected_markers = {
            "operator-cockpit.md": ["<!-- beo:operator-cockpit -->", "<!-- beo:operator-cockpit:mutation -->"],
            "README.md": ["<!-- beo:reference-tier:operator -->", "<!-- beo:reference-tier:runtime-authority -->", "context-management.md"],
            "resume-resolution.md": ["<!-- beo:resume-resolution:owner-orientation -->", "<!-- beo:resume-resolution:route-boundary -->"],
            "route-resolution.md": ["<!-- beo:route-resolution:meta-targets -->", "<!-- beo:route-resolution:operator-output -->"],
        }
        self.assertTrue((REFERENCE / "references" / "glossary.md").exists(), "glossary.md")
        for filename, markers in expected_markers.items():
            text = (REFERENCE / "references" / filename).read_text()
            self.assertTrue((REFERENCE / "references" / filename).exists(), filename)
            for marker in markers:
                self.assertIn(marker, text)
        agents_template = (REFERENCE / "assets" / "AGENTS.template.md").read_text()
        self.assertIn("<!-- beo:agents:start-cockpit -->", agents_template)

    def test_setup_contract_replaces_only_agents_managed_block(self) -> None:
        setup = (REFERENCE.parent / "setup" / "SKILL.md").read_text()
        template = (REFERENCE / "assets" / "AGENTS.template.md").read_text()
        expected_order = [
            "Treat `beo-reference -> assets/AGENTS.template.md` as the exact managed-block payload.",
            "Inspect the target repository `AGENTS.md` for BEO managed markers before editing",
            "if `AGENTS.md` is missing, create it from the template",
            "if `AGENTS.md` has partial, malformed, nested, or duplicate BEO managed markers, stop with `user_confirmation_needed`",
            "if `AGENTS.md` has exactly one valid BEO managed block, replace only that marker-delimited span",
            "if `AGENTS.md` has no BEO managed block but has unmarked BEO integration instructions, stop with `user_confirmation_needed`",
            "if `AGENTS.md` has no BEO managed block and no conflicting unmarked BEO integration instructions, append the template after a blank-line separator and preserve existing content",
            "Do not rewrite, normalize, or delete non-managed `AGENTS.md` content.",
        ]
        positions = [setup.index(text) for text in expected_order]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("target `AGENTS.md` contains partial, malformed, nested, or duplicate BEO managed markers", setup)
        self.assertIn("unmarked BEO integration instructions", setup)
        self.assertIn("<!-- BEO:MANAGED START -->", template)
        self.assertIn("<!-- BEO:MANAGED END -->", template)

    def test_review_contract_reads_live_declared_files(self) -> None:
        review = (REFERENCE.parent / "review" / "SKILL.md").read_text()
        self.assertIn("live declared files", review)

    def test_validate_contract_uses_contracted_approval_helper(self) -> None:
        validate = (REFERENCE.parent / "validate" / "SKILL.md").read_text()
        self.assertIn("beo_approval_check", validate)
        self.assertNotIn("projection_check", validate)
        self.assertNotIn("human_gate_check", validate)
        self.assertNotIn("scope_binding_check", validate)

    def test_owner_skills_load_common_contract_without_stop_boilerplate(self) -> None:
        for path in sorted(REFERENCE.parent.glob("*/SKILL.md")):
            text = path.read_text()
            if path.parent.name == "reference":
                continue
            self.assertIn(
                "Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.",
                text,
                f"{path.relative_to(REFERENCE.parent)} lacks common contract loading guidance",
            )
            self.assertNotIn(
                "Stop reporting:",
                text,
                f"{path.relative_to(REFERENCE.parent)} repeats stop reporting boilerplate",
            )

    def test_route_and_debug_operator_constraints_are_explicit(self) -> None:
        route = (REFERENCE.parent / "route" / "SKILL.md").read_text()
        route_resolution = (REFERENCE / "references" / "route-resolution.md").read_text()
        debug = (REFERENCE.parent / "debug" / "SKILL.md").read_text()
        self.assertIn("Artifacts prove:", route_resolution)
        self.assertNotIn("Owner Resolution Table", route_resolution)
        self.assertIn("resume-resolution.md", route_resolution)
        self.assertIn("Repair identity metadata only", route)
        self.assertIn("Never repair requirements, plan, approval, execution evidence, review, or product files", route)
        self.assertIn("explicitly authorizes more probes", debug)

    def test_transition_provenance_nests_return_metadata_under_transition(self) -> None:
        text = (REFERENCE / "references" / "transition-provenance.md").read_text()
        section = text.split("## Temporary owner return", 1)[1].split("## `return_to_caller`", 1)[0]
        self.assertIn('"transition": {', section)
        self.assertIn('    "return": {', section)
        self.assertNotIn('{\n  "return": {', section)

    def test_abandonment_write_exception_is_explicit(self) -> None:
        common = (REFERENCE / "references" / "skill-contract-common.md").read_text()
        lifecycle = (REFERENCE / "references" / "lifecycle.md").read_text()
        artifacts = (REFERENCE / "references" / "artifacts.md").read_text()
        artifact_schemas = json.loads((REFERENCE / "registry" / "artifact-schemas.json").read_text())
        abandoned_rule = artifact_schemas["shared_shapes"]["closure_shape"]["abandoned_rule"]
        self.assertIn("user_abandoned", common)
        self.assertIn("abandonment lifecycle bookkeeping", common)
        self.assertIn("owner emitting `user_abandoned`", lifecycle)
        self.assertIn("does not grant review closure", artifacts)
        self.assertIn("owner emitting legal user_abandoned", abandoned_rule)

    def test_registry_check_rejects_compact_local_human_gate_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "artifact-schemas.json"
            payload = json.loads(path.read_text())
            payload["artifact_densities"]["compact"]["human_gate_shape"] = {}
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("compact artifact density must not define human_gate_shape", result.stdout)

    def test_registry_check_rejects_unsupported_compact_authority_source(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "approval-envelope.json"
            payload = json.loads(path.read_text())
            payload["required_fields"][0]["compact_source"] = "TICKET.md beo.ticket.extra readiness"
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("approval envelope compact sources must use exact TICKET.md `beo.ticket` authority source", result.stdout)

    def test_registry_check_rejects_malformed_compact_field_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "artifact-schemas.json"
            payload = json.loads(path.read_text())
            payload["artifact_densities"]["compact"]["field_ownership"]["beo-plan"] = ["scope", 1]
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("artifact-schemas.json schema error", result.stdout)

    def test_registry_check_rejects_missing_compact_field_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "artifact-schemas.json"
            payload = json.loads(path.read_text())
            payload["artifact_densities"]["compact"].pop("field_ownership")
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required field field_ownership", result.stdout)

    def test_registry_check_rejects_empty_compact_field_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "artifact-schemas.json"
            payload = json.loads(path.read_text())
            payload["artifact_densities"]["compact"]["field_ownership"]["beo-plan"] = []
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected at least 1 item", result.stdout)

    def test_registry_check_rejects_blank_compact_field_ownership(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "artifact-schemas.json"
            payload = json.loads(path.read_text())
            payload["artifact_densities"]["compact"]["field_ownership"]["beo-plan"] = [" "]
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("compact field_ownership fields must be non-empty strings", result.stdout)

    def test_registry_check_rejects_missing_compact_handoff_identity_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "artifact-schemas.json"
            payload = json.loads(path.read_text())
            payload["artifact_densities"]["compact"]["field_ownership"]["beo-plan"].remove("phase_status")
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("compact field_ownership.beo-plan missing handoff identity fields", result.stdout)

    def test_registry_check_rejects_compact_field_ownership_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "vocabulary.json"
            payload = json.loads(path.read_text())
            payload["owner_classes"]["runtime_support"].remove("beo-debug")
            payload["owner_classes"]["runtime_delivery"].append("beo-debug")
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("compact field_ownership keys must match compact artifact owners", result.stdout)

    def test_registry_check_rejects_invalid_transition_wildcard_conflict(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "pipeline.json"
            payload = json.loads(path.read_text())
            for transition in payload["invalid_transitions"]:
                if transition.get("from") == "beo-execute" and transition.get("to") == "done":
                    transition["condition_id"] = "any"
                    break
            else:
                payload["invalid_transitions"].append({
                    "from": "beo-execute",
                    "condition_id": "any",
                    "to": "done",
                    "reason": "test conflict",
                })
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid transition conflicts with legal transition", result.stdout)

    def test_registry_check_rejects_human_gate_bypass_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "artifact-schemas.json"
            payload = json.loads(path.read_text())
            payload["shared_shapes"]["human_gate_shape"]["gates"][0]["approval_bearing"] = False
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("human_gate_shape must not define approval_bearing", result.stdout)

    def test_registry_check_rejects_invalid_schema_enum(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            registry = base / "registry"
            shutil.copytree(REFERENCE / "registry", registry)
            shutil.copytree(REFERENCE / "references", base / "references")
            shutil.copytree(REFERENCE / "assets", base / "assets")
            path = registry / "command-contracts.json"
            payload = json.loads(path.read_text())
            payload["commands"][0]["contract_status"] = "definitely_invalid"
            path.write_text(json.dumps(payload))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "beo_registry_check.py"), str(registry)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expected one of", result.stdout)


if __name__ == "__main__":
    unittest.main()
