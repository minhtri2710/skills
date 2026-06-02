#!/usr/bin/env python3
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-reference"
scripts = REFERENCE_ROOT / "scripts"
sys.path.insert(0, str(scripts))


class HelperSemanticsTest(unittest.TestCase):
    def quick_ticket(self):
        return {
            "version": 1,
            "issue_id": "br-1",
            "mode": "quick",
            "request": "x",
            "done_criteria": ["ok"],
            "scope": {
                "files": {"allow": ["README.md"], "forbid": []},
                "generated_outputs": [],
                "verify": {"commands": ["rtk git diff --check"]},
            },
        }

    def test_setup_blocks_when_pyyaml_missing(self):
        import beo_setup
        real_import = __import__

        def import_without_yaml(name, *args, **kwargs):
            if name == "yaml":
                raise ImportError("no yaml")
            return real_import(name, *args, **kwargs)

        def fake_run_cmd(args, strip=True, cwd=None):
            if args[:2] == ["br", "--version"]:
                return 0, "br 0.1.28", ""
            if args[:2] == ["bv", "--version"]:
                return 0, "bv 0.15.2", ""
            if args[:2] == ["qmd", "--version"]:
                return 0, "qmd 0.1.0", ""
            if args[:2] == ["obsidian", "help"]:
                return 0, "obsidian help", ""
            if args[:2] == ["qmd", "collection"]:
                return 0, '[{"name":"beo-learning"}]', ""
            if args[:2] == ["qmd", "status"]:
                return 0, "Pending: 0 need embedding", ""
            return 0, "", ""

        with mock.patch("builtins.__import__", side_effect=import_without_yaml), \
             mock.patch.object(beo_setup.beo_io, "run_cmd", side_effect=fake_run_cmd), \
             mock.patch.dict(os.environ, {"BEO_QMD_COLLECTION": "beo-learning"}, clear=True), \
             mock.patch.object(sys, "argv", ["beo_setup.py"]), \
             contextlib.redirect_stdout(io.StringIO()) as stdout:
            rc = beo_setup.main()
        report = json.loads(stdout.getvalue())
        self.assertEqual(rc, 1)
        self.assertEqual(report["dependencies"]["PyYAML"], "missing")
        self.assertEqual(report["status"], "blocked")

    def test_ticket_yaml_and_path_safety(self):
        import beo_paths
        import beo_ticket
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".beads" / "artifacts" / "br-1").mkdir(parents=True)
            with self.assertRaisesRegex(FileNotFoundError, "ticket_artifact_missing"):
                beo_ticket.read_ticket(root, "br-1")
            data = self.quick_ticket()
            path = beo_ticket.write_ticket(root, "br-1", data)
            with self.assertRaises(FileExistsError):
                beo_ticket.write_ticket(root, "br-1", data)
            self.assertEqual(beo_ticket.read_ticket(root, "br-1").data["version"], 1)
            path.write_text("version: 1\nissue_id: br-1\nissue_id: br-2\nmode: quick\nrequest: x\ndone_criteria: [x]\nscope: {files: {allow: [README.md], forbid: []}, generated_outputs: [], verify: {commands: [true]}}\n")
            with self.assertRaisesRegex(ValueError, "duplicate key"):
                beo_ticket.read_ticket(root, "br-1")
            path.write_text("version: 1\nfirst: &anchor x\nsecond: *anchor\n")
            with self.assertRaisesRegex(ValueError, "anchors or aliases"):
                beo_ticket.read_ticket(root, "br-1")
            path.write_text("version: 1\n---\nissue_id: br-1\n")
            with self.assertRaisesRegex(ValueError, "exactly one YAML document"):
                beo_ticket.read_ticket(root, "br-1")
            mismatch = dict(data, issue_id="br-2")
            with self.assertRaisesRegex(ValueError, "issue_id must match artifact"):
                beo_ticket.write_ticket(root, "br-1", mismatch, overwrite=True)
            path.write_text("version: 1\nissue_id: br-2\nmode: quick\nrequest: x\ndone_criteria: [x]\nscope: {files: {allow: [README.md], forbid: []}, generated_outputs: [], verify: {commands: ['true']}}\n")
            with self.assertRaisesRegex(ValueError, "issue_id must match artifact"):
                beo_ticket.read_ticket(root, "br-1")
            unsafe_scope = dict(data)
            unsafe_scope["scope"] = {"files": {"allow": ["../x"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            with self.assertRaisesRegex(ValueError, "scope.files.allow contains unsafe path"):
                beo_ticket.validate_plan_only(unsafe_scope)
            untrimmed_scope = dict(data)
            untrimmed_scope["scope"] = {"files": {"allow": [" README.md "], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            with self.assertRaisesRegex(ValueError, "scope.files.allow contains unsafe path"):
                beo_ticket.validate_plan_only(untrimmed_scope)
            dot_scope = dict(data)
            dot_scope["scope"] = {"files": {"allow": ["."], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            with self.assertRaisesRegex(ValueError, "scope.files.allow contains unsafe path"):
                beo_ticket.validate_plan_only(dot_scope)
            scalar_scope = dict(data)
            scalar_scope["scope"] = {"files": {"allow": "README.md", "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            with self.assertRaisesRegex(ValueError, "scope.files.allow must be a list"):
                beo_ticket.validate_plan_only(scalar_scope)
            legacy = dict(data, ticket_schema_version="old")
            with self.assertRaisesRegex(ValueError, "contains unknown field"):
                beo_ticket.validate_plan_only(legacy)
            unknown = dict(data, surprise=True)
            with self.assertRaisesRegex(ValueError, "unknown field"):
                beo_ticket.validate_plan_only(unknown)
            bad_scope = dict(data)
            bad_scope["scope"] = {**data["scope"], "extra": True}
            with self.assertRaisesRegex(ValueError, "scope contains unknown"):
                beo_ticket.validate_plan_only(bad_scope)
            unsafe_issue = dict(data, issue_id="../bad")
            with self.assertRaisesRegex(ValueError, "unsafe issue_id"):
                beo_ticket.validate_plan_only(unsafe_issue)
            slash_issue = dict(data, issue_id="bad/id")
            with self.assertRaisesRegex(ValueError, "unsafe issue_id"):
                beo_ticket.validate_plan_only(slash_issue)
            whitespace_issue = dict(data, issue_id="bad id")
            with self.assertRaisesRegex(ValueError, "unsafe issue_id"):
                beo_ticket.validate_plan_only(whitespace_issue)
            missing = dict(data)
            missing.pop("version")
            with self.assertRaisesRegex(ValueError, "version"):
                beo_ticket.validate_plan_only(missing)
        for unsafe in ["/etc/passwd", "../x", "a/../../b", "C:\\tmp\\x", ".", "a\nb", "a\rb", "a\tb"]:
            with self.assertRaises(ValueError):
                beo_paths.reject_unsafe_path(unsafe)

    def test_approval_projection_and_plan_validation(self):
        import beo_approval
        import beo_check
        import beo_paths
        ticket = self.quick_ticket()
        projection = beo_approval.approval_projection(ticket, ticket_file_hash="hash", repo_head="head")
        self.assertEqual(projection["done_criteria"], ["ok"])
        self.assertEqual(projection["scope.generated_outputs"], [])
        self.assertNotIn("command_contracts_hash", projection)
        with self.assertRaises(TypeError):
            beo_approval.approval_projection(ticket, {}, "bead", "contracts")
        self.assertFalse(beo_check.validate_plan(Path.cwd(), ticket, {"id": "br-1", "type": "task"}))
        self.assertFalse(beo_paths.path_matches_pattern("src/foo.py", "src"))
        self.assertTrue(beo_paths.path_token_covers("**", "src/**"))
        self.assertTrue(beo_paths.path_token_covers("src/**", "src/private/**"))
        self.assertTrue(beo_paths.path_token_covers("src/**", "src/**/*.py"))
        self.assertTrue(beo_paths.path_token_covers("src/**", "src/foo.py"))
        self.assertTrue(beo_paths.path_token_covers("src/**", "src/**/*.py"))
        self.assertFalse(beo_paths.path_token_covers("src", "src/**"))
        self.assertFalse(beo_paths.path_token_covers("src", "src/**/*.py"))
        self.assertFalse(beo_paths.path_token_covers("src", "src/foo.py"))
        self.assertFalse(beo_paths.path_token_covers("src/*.py", "src/private/**"))
        self.assertFalse(beo_paths.path_token_covers("*.py", "src/*.py"))
        self.assertFalse(beo_paths.path_token_covers("src2", "src/**"))
        self.assertFalse(beo_paths.path_token_covers("src/private/**", "src/**"))
        protected = dict(ticket)
        protected["scope"] = {"files": {"allow": [".env"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
        self.assertTrue(any("protected" in err for err in beo_check.validate_plan(Path.cwd(), protected, {})))
        protected_glob = dict(ticket)
        protected_glob["scope"] = {"files": {"allow": [".git/**"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
        self.assertTrue(any("protected" in err for err in beo_check.validate_plan(Path.cwd(), protected_glob, {})))
        protected_everything = dict(ticket)
        protected_everything["scope"] = {"files": {"allow": ["**"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
        self.assertTrue(any("protected" in err for err in beo_check.validate_plan(Path.cwd(), protected_everything, {})))
        protected_pem_glob = dict(ticket)
        protected_pem_glob["scope"] = {"files": {"allow": ["**/*.pem"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
        self.assertTrue(any("protected" in err for err in beo_check.validate_plan(Path.cwd(), protected_pem_glob, {})))
        protected_descendants = dict(ticket)
        protected_descendants["scope"] = {"files": {"allow": ["src/**"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
        self.assertTrue(any("protected" in err for err in beo_check.validate_plan(Path.cwd(), protected_descendants, {})))
        protected_single_star_descendants = dict(ticket)
        protected_single_star_descendants["scope"] = {"files": {"allow": ["src/*.py"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
        self.assertTrue(any("protected" in err for err in beo_check.validate_plan(Path.cwd(), protected_single_star_descendants, {})))
        protected_beads = dict(ticket)
        protected_beads["scope"] = {"files": {"allow": [".beads/artifacts/br-1/state.json"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
        self.assertTrue(any("protected" in err for err in beo_check.validate_plan(Path.cwd(), protected_beads, {})))
        forbidden_protected = dict(ticket)
        forbidden_protected["scope"] = {"files": {"allow": ["README.md"], "forbid": [".env"]}, "generated_outputs": [], "verify": {"commands": ["true"]}}
        self.assertFalse(any("protected" in err for err in beo_check.validate_plan(Path.cwd(), forbidden_protected, {})))
        standard = dict(ticket, mode="standard", risk={"summary": "risk", "rollback": "revert"})
        standard["risk"] = {**standard["risk"], "extra": True}
        import beo_ticket
        with self.assertRaisesRegex(ValueError, "risk contains unknown"):
            beo_ticket.validate_plan_only(standard)
        human_gate = {"type": "external_side_effect_authorization", "scope": "prod", "approver_handle": "human", "valid_for_issue_id": "br-1", "reason": "needed for test"}
        strict = dict(ticket, mode="strict", risk={"summary": "risk", "rollback": "revert"}, human_gates={"status": "resolved", "gates": [human_gate]}, strict={"reason": "external", "authorization_refs": ["gate"], "rollback_refs": ["rollback"], "external_side_effects": [{"type": "deploy"}], "stateful_external_systems": [{"name": "prod", "effect_ref": "deploy"}]})
        with self.assertRaisesRegex(ValueError, r"strict.external_side_effects\[0\] missing"):
            beo_ticket.validate_plan_only(strict)
        bad_gate = dict(strict)
        bad_gate["human_gates"] = {"status": "resolved", "gates": [{**human_gate, "valid_for_issue_id": "br-2", "reason": "needed for test"}]}
        with self.assertRaisesRegex(ValueError, "valid_for_issue_id must match issue_id"):
            beo_ticket.validate_plan_only(bad_gate)
        missing_reason_gate = dict(strict)
        missing_reason = dict(human_gate)
        missing_reason.pop("reason")
        missing_reason_gate["human_gates"] = {"status": "resolved", "gates": [missing_reason]}
        with self.assertRaisesRegex(ValueError, r"missing required field\(s\): reason"):
            beo_ticket.validate_plan_only(missing_reason_gate)
        revocation_gate = dict(ticket, human_gates={"status": "resolved", "gates": [{**human_gate, "revocation_ref": "br-comment:revoked"}]})
        beo_ticket.validate_plan_only(revocation_gate)
        bad_revocation_gate = dict(ticket, human_gates={"status": "resolved", "gates": [{**human_gate, "revocation_ref": 123}]})
        with self.assertRaisesRegex(ValueError, r"human_gates.gates\[0\].revocation_ref"):
            beo_ticket.validate_plan_only(bad_revocation_gate)
        typed_bad_gate = dict(strict)
        typed_bad_gate["human_gates"] = {"status": "resolved", "gates": [{**human_gate, "approver_handle": 123}]}
        with self.assertRaisesRegex(ValueError, r"human_gates.gates\[0\].approver_handle"):
            beo_ticket.validate_plan_only(typed_bad_gate)
        strict["strict"]["external_side_effects"] = [{"type": "deploy", "target": "prod", "authorization_ref": "gate", "precheck": "check", "rollback_or_compensation": "rollback", "postcheck": "post", "blast_radius": "bounded"}]
        strict["strict"]["stateful_external_systems"] = []
        with self.assertRaisesRegex(ValueError, "strict.stateful_external_systems must not be empty"):
            beo_ticket.validate_plan_only(strict)
        strict["strict"]["stateful_external_systems"] = [{"name": "prod", "effect_ref": "missing"}]
        with self.assertRaisesRegex(ValueError, "effect_ref must match"):
            beo_ticket.validate_plan_only(strict)
        strict["strict"]["external_side_effects"] = [{"type": "deploy", "target": 123, "authorization_ref": "gate", "precheck": "check", "rollback_or_compensation": "rollback", "postcheck": "post", "blast_radius": "bounded"}]
        strict["strict"]["stateful_external_systems"] = [{"name": "prod", "effect_ref": "deploy"}]
        with self.assertRaisesRegex(ValueError, r"strict.external_side_effects\[0\].target"):
            beo_ticket.validate_plan_only(strict)
        strict["strict"]["external_side_effects"] = [{"type": "deploy", "target": "prod", "authorization_ref": "gate", "precheck": "check", "rollback_or_compensation": "rollback", "postcheck": "post", "blast_radius": "bounded"}]
        strict["strict"]["stateful_external_systems"] = [{"name": "prod", "effect_ref": "prod"}]
        strict["strict"] = {**strict["strict"], "extra": True}
        with self.assertRaisesRegex(ValueError, "strict contains unknown"):
            beo_ticket.validate_plan_only(strict)
        broad = dict(ticket)
        broad["scope"] = {"files": {"allow": ["src/**"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
        broad_errors = beo_check.validate_plan(Path.cwd(), broad, {})
        self.assertTrue(any("broad glob" in err for err in broad_errors))
        self.assertFalse(any("path escapes repo" in err for err in broad_errors))
        single_star = dict(ticket)
        single_star["scope"] = {"files": {"allow": ["src/*.py"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
        self.assertTrue(any("matching Human Gate" in err for err in beo_check.validate_plan(Path.cwd(), single_star, {})))
        broad_wrong_gate = dict(broad, human_gates={"status": "resolved", "gates": [human_gate]})
        self.assertTrue(any("matching Human Gate" in err for err in beo_check.validate_plan(Path.cwd(), broad_wrong_gate, {})))
        broad_narrow_gate = dict(broad, human_gates={"status": "resolved", "gates": [{"type": "broad_scope_authorization", "scope": "src/foo.py", "approver_handle": "human", "valid_for_issue_id": "br-1", "reason": "needed for test"}]})
        self.assertTrue(any("matching Human Gate" in err for err in beo_check.validate_plan(Path.cwd(), broad_narrow_gate, {})))
        broad_matching_gate = dict(broad, human_gates={"status": "resolved", "gates": [{"type": "broad_scope_authorization", "scope": "src/**", "approver_handle": "human", "valid_for_issue_id": "br-1", "reason": "needed for test"}]})
        self.assertFalse(any("matching Human Gate" in err for err in beo_check.validate_plan(Path.cwd(), broad_matching_gate, {})))
        self.assertIn(
            "changed path matches forbidden scope: src/secret.py",
            beo_paths.match_allowed_paths(["src/secret.py"], ["src/**"], [], ["src/secret.py"]).errors,
        )
        broad_with_empty_gate = dict(broad, human_gates={"status": "resolved", "gates": []})
        with self.assertRaisesRegex(ValueError, "resolved human_gates requires"):
            beo_ticket.validate_plan_only(broad_with_empty_gate)
        standard_empty_resolved_gate = dict(standard)
        standard_empty_resolved_gate["risk"] = {"summary": "risk", "rollback": "revert"}
        standard_empty_resolved_gate["human_gates"] = {"status": "resolved", "gates": []}
        with self.assertRaisesRegex(ValueError, "resolved human_gates requires"):
            beo_ticket.validate_plan_only(standard_empty_resolved_gate)

    def test_path_tokens_overlap_bracket_edge_cases(self):
        import beo_paths
        self.assertFalse(beo_paths.path_tokens_overlap("src/*.py", "src/private/*.py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/*", "src/private/**"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/**/*.py", "src/*.md"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/*.md", "src/*.py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/a*.py", "src/b*.py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/foo?.py", "src/bar?.py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/foo?.py", "src/foo?.md"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/file[0-9].py", "src/file[0-9].md"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/[ab].py", "src/[cd].py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/[ab][cd].py", "src/[ef][gh].py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/[ab].py", "src/[cd][ef].py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/[ab][cd].py", "src/[ef].py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/file[0-9].py", "src/file[a-z].py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/[a-].py", "src/[b].py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/[]a].py", "src/[bc].py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/[!a].py", "src/[a].py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/[!ab].py", "src/[ab].py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/[!]].py", "src/[]].py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/[ab].py", "src/[bc].py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/[ab][cd].py", "src/[bc][de].py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/[a-].py", "src/[-].py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/[]a].py", "src/[a].py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/[]a].py", "src/[]b].py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/[!a].py", "src/[b].py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/[!]].py", "src/[a].py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/file?.py", "src/file[0-9].py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/*.py", "src/*test.py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/ab*.py", "src/a*.py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/**/*.py", "src/private/foo.py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/**", "src"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/**", "src/private/*.py"))
        self.assertTrue(beo_paths.path_tokens_overlap("src/**/foo.py", "src/*.py"))
        self.assertFalse(beo_paths.path_tokens_overlap("src/**/foo.py", "src/*.md"))

    def test_changed_files_handles_quoted_paths(self):
        import beo_check_scope
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (root / "file with space.txt").write_text("dirty\n", encoding="utf-8")
            self.assertEqual(beo_check_scope.changed_files(root), ["file with space.txt"])
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            subprocess.run(["git", "add", "file with space.txt"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "mv", "file with space.txt", "new name.txt"], cwd=root, check=True)
            self.assertEqual(beo_check_scope.changed_files(root), ["new name.txt"])

    def test_glob_prestate_tracks_matching_files(self):
        import beo_check_approval
        import beo_ticket
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            (root / "src").mkdir()
            (root / "src" / "tracked.py").write_text("old\n", encoding="utf-8")
            (root / "src" / "nested").mkdir()
            (root / "src" / "nested" / "tracked.py").write_text("nested\n", encoding="utf-8")
            ticket = self.quick_ticket()
            ticket["scope"] = {"files": {"allow": ["./src/**"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            ticket["human_gates"] = {"status": "resolved", "gates": [{"type": "broad_scope_authorization", "scope": "src/**", "approver_handle": "human", "valid_for_issue_id": "br-1", "reason": "needed for test"}]}
            beo_ticket.validate_plan_only(ticket)
            prestate = beo_check_approval.compute_prestate(root, ticket)
            self.assertEqual(prestate["src/**#matches"], ["src/nested/tracked.py", "src/tracked.py"])
            broad_ticket = self.quick_ticket()
            broad_ticket["scope"] = {"files": {"allow": ["**"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            broad_ticket["human_gates"] = {"status": "resolved", "gates": [{"type": "broad_scope_authorization", "scope": "**", "approver_handle": "human", "valid_for_issue_id": "br-1", "reason": "needed for test"}]}
            (root / ".beads" / "artifacts" / "br-1").mkdir(parents=True)
            (root / ".beads" / "artifacts" / "br-1" / "TICKET.yaml").write_text("ticket\n", encoding="utf-8")
            broad_prestate = beo_check_approval.compute_prestate(root, broad_ticket)
            self.assertNotIn(".git/HEAD", broad_prestate["**#matches"])
            self.assertIn(".beads/artifacts/br-1/TICKET.yaml", broad_prestate["**#matches"])
            (root / "src" / "secret.py").write_text("secret\n", encoding="utf-8")
            forbid_ticket = dict(ticket)
            forbid_ticket["scope"] = {"files": {"allow": ["./src/**"], "forbid": ["src/secret.py"]}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            self.assertEqual(beo_check_approval.compute_prestate(root, forbid_ticket)["src/**#matches"], ["src/nested/tracked.py", "src/tracked.py"])
            (root / "src" / "secret.py").unlink()
            (root / "src" / "local-link.txt").symlink_to(root / "src" / "tracked.py")
            explicit_symlink = self.quick_ticket()
            explicit_symlink["scope"] = {"files": {"allow": ["src/local-link.txt"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            with self.assertRaisesRegex(ValueError, "symlink"):
                beo_check_approval.compute_prestate(root, explicit_symlink)
            (root / "src" / "local-link.txt").unlink()
            (root / "src" / "dir-link").symlink_to(root / "src" / "nested", target_is_directory=True)
            explicit_symlink_parent = self.quick_ticket()
            explicit_symlink_parent["scope"] = {"files": {"allow": ["src/dir-link/tracked.py"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            with self.assertRaisesRegex(ValueError, "symlink"):
                beo_check_approval.compute_prestate(root, explicit_symlink_parent)
            with self.assertRaisesRegex(ValueError, "symlink"):
                beo_check_approval.compute_prestate(root, ticket)
            (root / "src" / "dir-link").unlink()
            (root / "src" / "new.py").write_text("new\n", encoding="utf-8")
            self.assertNotEqual(prestate, beo_check_approval.compute_prestate(root, ticket))
            outside = root.parent / "outside-beo-prestate.txt"
            outside.write_text("secret\n", encoding="utf-8")
            try:
                (root / "src" / "escape.txt").symlink_to(outside)
                with self.assertRaisesRegex(ValueError, "symlink"):
                    beo_check_approval.compute_prestate(root, ticket)
            finally:
                outside.unlink(missing_ok=True)

    def test_beo_state_sequence_and_event_validation(self):
        import beo_state
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            issue_id = "br-9"
            with self.assertRaisesRegex(FileNotFoundError, "state_artifact_missing"):
                beo_state.read_state(root, issue_id)
            state = beo_state.initialize_state(root, issue_id)
            self.assertEqual(state["version"], 1)
            self.assertEqual(state["phase_sequence_id"], 1)
            self.assertEqual(state["metadata"]["last_owner"], "beo-plan")
            with self.assertRaises(FileExistsError):
                beo_state.initialize_state(root, issue_id)

            def approve(candidate):
                candidate["phase"] = "approved"
                candidate["approval"].update({"status": "PASS_EXECUTE", "approved_by": "beo-validate", "actor": "assistant", "ticket_file_hash": "hash", "approval_projection_hash": "proj", "repo_head": "head"})
                return candidate

            approved = beo_state.locked_update_state(root, issue_id, "beo-validate", approve)
            self.assertEqual(approved["phase"], "approved")
            self.assertEqual(approved["approval"]["approved_phase_sequence_id"], approved["phase_sequence_id"])
            self.assertTrue(beo_state.execution_entry_is_current(approved))

            def bad_sequence(candidate):
                candidate["approval"]["approved_phase_sequence_id"] = 999
                return candidate

            with self.assertRaisesRegex(ValueError, "approved_phase_sequence_id"):
                beo_state.locked_update_state(root, issue_id, "beo-validate", bad_sequence)

            def reapprove(candidate):
                candidate["approval"]["ticket_file_hash"] = "hash2"
                candidate["approval"]["approval_projection_hash"] = "proj2"
                return candidate

            reapproved = beo_state.locked_update_state(root, issue_id, "beo-validate", reapprove)
            self.assertEqual(reapproved["approval"]["approved_phase_sequence_id"], reapproved["phase_sequence_id"])
            self.assertTrue(beo_state.execution_entry_is_current(reapproved))

            def bad_metadata(candidate):
                candidate["metadata"]["last_owner"] = "caller"
                return candidate

            with self.assertRaisesRegex(ValueError, "metadata.last_owner"):
                beo_state.locked_update_state(root, issue_id, "beo-validate", bad_metadata)

            def legacy_field(candidate):
                candidate["schema_epoch"] = 1
                return candidate

            with self.assertRaisesRegex(ValueError, "cannot write state field"):
                beo_state.locked_update_state(root, issue_id, "beo-validate", legacy_field)
            with self.assertRaisesRegex(ValueError, "may not update delivery state"):
                beo_state.locked_update_state(root, issue_id, "beo-debug", lambda candidate: candidate)
            with self.assertRaisesRegex(ValueError, "unknown state owner"):
                beo_state.locked_update_state(root, issue_id, "beo-unknown", lambda candidate: candidate)
            missing_nested = dict(approved)
            missing_nested["approval"] = dict(missing_nested["approval"])
            missing_nested["approval"].pop("prestate")
            with self.assertRaisesRegex(ValueError, "approval missing required field"):
                beo_state.validate_state(missing_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["phase_sequence_id"] = True
            with self.assertRaisesRegex(ValueError, "phase_sequence_id"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["approval"]["approved_phase_sequence_id"] = True
            with self.assertRaisesRegex(ValueError, "approval.approved_phase_sequence_id"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["approval"]["prestate"] = []
            with self.assertRaisesRegex(ValueError, "approval.prestate must be an object"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["execution"]["changed_files"] = "README.md"
            with self.assertRaisesRegex(ValueError, "execution.changed_files must be a list"):
                beo_state.validate_state(bad_nested, issue_id)
            for field in ["changed_files", "evidence_refs"]:
                for unsafe_path in ["../x", "/tmp/x", ".", "a\nb"]:
                    bad_nested = json.loads(json.dumps(approved))
                    bad_nested["execution"][field] = [unsafe_path]
                    with self.assertRaisesRegex(ValueError, f"execution.{field} contains unsafe path"):
                        beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["execution"]["verify_results"] = ["true"]
            with self.assertRaisesRegex(ValueError, "execution.verify_results entries must be objects"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["review"]["repair_count"] = -1
            with self.assertRaisesRegex(ValueError, "review.repair_count"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["review"]["repair_count"] = True
            with self.assertRaisesRegex(ValueError, "review.repair_count"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["review"]["closed_in_br"] = "false"
            with self.assertRaisesRegex(ValueError, "review.closed_in_br"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["metadata"]["updated_at"] = 1
            with self.assertRaisesRegex(ValueError, "metadata.updated_at"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["review"]["verdict"] = "repair_same_scope"
            bad_nested["review"]["route_condition_id"] = "cannot_deliver"
            with self.assertRaisesRegex(ValueError, "repair_same_scope verdict"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["review"]["verdict"] = "cannot_deliver"
            bad_nested["review"]["route_condition_id"] = "root_cause_diagnosis_needed"
            with self.assertRaisesRegex(ValueError, "cannot_deliver verdict"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(approved))
            bad_nested["review"]["verdict"] = "repair_same_scope"
            bad_nested["review"]["route_condition_id"] = "root_cause_diagnosis_needed"
            with self.assertRaisesRegex(ValueError, "repair_same_scope verdict"):
                beo_state.validate_state(bad_nested, issue_id)

            finding_state = json.loads(json.dumps(approved))
            finding_state["review"]["findings"] = [{"severity": "major", "category": "scope", "message": "scope issue", "evidence_refs": ["logs/review.txt"], "recommended_route": "repair_rescope"}]
            beo_state.validate_state(finding_state, issue_id)
            bad_nested = json.loads(json.dumps(finding_state))
            bad_nested["review"]["findings"][0]["severity"] = "urgent"
            with self.assertRaisesRegex(ValueError, "severity is invalid"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(finding_state))
            bad_nested["review"]["findings"][0]["recommended_route"] = "none"
            with self.assertRaisesRegex(ValueError, "cannot be none"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(finding_state))
            bad_nested["review"]["findings"][0]["evidence_refs"] = ["../escape"]
            with self.assertRaisesRegex(ValueError, "evidence_refs contains unsafe path"):
                beo_state.validate_state(bad_nested, issue_id)
            bad_nested = json.loads(json.dumps(finding_state))
            bad_nested["review"]["findings"][0]["extra"] = "nope"
            with self.assertRaisesRegex(ValueError, r"review.findings\[0\] contains unknown field"):
                beo_state.validate_state(bad_nested, issue_id)
            coverage_state = json.loads(json.dumps(approved))
            coverage_state["review"]["done_criteria_coverage"] = [{"criterion": "works", "status": "covered", "evidence_refs": ["logs/check.txt"]}]
            beo_state.validate_state(coverage_state, issue_id)
            bad_nested = json.loads(json.dumps(coverage_state))
            bad_nested["review"]["done_criteria_coverage"][0]["extra"] = "nope"
            with self.assertRaisesRegex(ValueError, r"review.done_criteria_coverage\[0\] contains unknown field"):
                beo_state.validate_state(bad_nested, issue_id)
            debug_route = json.loads(json.dumps(approved))
            debug_route["review"]["verdict"] = None
            debug_route["review"]["route_condition_id"] = "root_cause_diagnosis_needed"
            beo_state.validate_state(debug_route, issue_id)
            containment_route = json.loads(json.dumps(approved))
            containment_route["review"]["verdict"] = None
            containment_route["review"]["route_condition_id"] = "containment_review_needed"
            with self.assertRaisesRegex(ValueError, "requires a non-null verdict"):
                beo_state.validate_state(containment_route, issue_id)
            accept_not_closed = json.loads(json.dumps(approved))
            accept_not_closed["review"]["verdict"] = "accept"
            accept_not_closed["review"]["route_condition_id"] = "verdict_accept"
            with self.assertRaisesRegex(ValueError, "closed_in_br must be true"):
                beo_state.validate_state(accept_not_closed, issue_id)
            accept_closed = json.loads(json.dumps(accept_not_closed))
            accept_closed["review"]["closed_in_br"] = True
            beo_state.validate_state(accept_closed, issue_id)

            def stale_approval(candidate):
                candidate["phase"] = "blocked"
                candidate["approval"]["status"] = "failed"
                return candidate

            stale = beo_state.locked_update_state(root, issue_id, "beo-validate", stale_approval)
            with self.assertRaisesRegex(ValueError, "requires approved/executing/executed"):
                beo_state.locked_update_state(root, issue_id, "beo-execute", lambda candidate: candidate)
            stale["phase"] = "approved"
            stale["approval"]["status"] = "failed"
            stale["approval"]["approved_phase_sequence_id"] = stale["phase_sequence_id"]
            beo_state.atomic_write_json(root / ".beads" / "artifacts" / issue_id / "state.json", stale)
            with self.assertRaisesRegex(ValueError, "current PASS_EXECUTE"):
                beo_state.locked_update_state(root, issue_id, "beo-execute", lambda candidate: candidate)
            stale["approval"]["status"] = "PASS_EXECUTE"
            stale["approval"]["approved_phase_sequence_id"] = stale["phase_sequence_id"] - 1
            beo_state.atomic_write_json(root / ".beads" / "artifacts" / issue_id / "state.json", stale)
            with self.assertRaisesRegex(ValueError, "PASS_EXECUTE approval is stale"):
                beo_state.locked_update_state(root, issue_id, "beo-execute", lambda candidate: candidate)

            def reapprove_for_execution(candidate):
                candidate["phase"] = "approved"
                candidate["approval"]["status"] = "PASS_EXECUTE"
                return candidate

            beo_state.locked_update_state(root, issue_id, "beo-validate", reapprove_for_execution)

            def execute_without_started_at(candidate):
                candidate["phase"] = "executing"
                candidate["execution"]["actor"] = "assistant"
                return candidate

            with self.assertRaisesRegex(ValueError, "execution start requires execution.started_at"):
                beo_state.locked_update_state(root, issue_id, "beo-execute", execute_without_started_at)

            def execute(candidate):
                candidate["phase"] = "executing"
                candidate["execution"]["actor"] = "assistant"
                candidate["execution"]["started_at"] = "2026-01-01T00:00:00Z"
                return candidate

            executing = beo_state.locked_update_state(root, issue_id, "beo-execute", execute)
            self.assertFalse(beo_state.execution_entry_is_current(executing))
            event = {"issue_id": issue_id, "kind": "handoff", "phase": "executing", "actor": "beo-execute", "timestamp": "2026-01-01T00:00:00Z", "payload": {"to": "beo-debug", "condition_id": "root_cause_diagnosis_needed", "reason": "debug", "evidence_refs": []}}
            beo_state.append_event(root, issue_id, event)
            events = beo_state.read_events(root, issue_id)
            self.assertEqual(events[0]["kind"], "handoff")
            with self.assertRaisesRegex(ValueError, "handoff condition_id must not be a normal transition"):
                beo_state.append_event(root, issue_id, {**event, "payload": {**event["payload"], "condition_id": "executed"}})
            with self.assertRaisesRegex(ValueError, "handoff.reason must be a non-empty string"):
                beo_state.append_event(root, issue_id, {**event, "payload": {**event["payload"], "reason": ""}})
            with self.assertRaisesRegex(ValueError, "handoff.evidence_refs contains unsafe path"):
                beo_state.append_event(root, issue_id, {**event, "payload": {**event["payload"], "evidence_refs": ["../escape"]}})
            with self.assertRaisesRegex(ValueError, "handoff.evidence_refs entries must be strings"):
                beo_state.append_event(root, issue_id, {**event, "payload": {**event["payload"], "evidence_refs": [1]}})
            return_event = {"issue_id": issue_id, "kind": "return", "phase": "blocked", "actor": "beo-debug", "timestamp": "2026-01-01T00:00:00Z", "payload": {"to": "beo-review", "caller_skill": "beo-review", "caller_route_context": "root_cause_diagnosis_needed", "root_cause_status": "likely", "evidence_refs": [], "recommended_next_route": "repair_same_scope"}}
            beo_state.append_event(root, issue_id, return_event)
            with self.assertRaisesRegex(ValueError, "return.root_cause_status is invalid"):
                beo_state.append_event(root, issue_id, {**return_event, "payload": {**return_event["payload"], "root_cause_status": "maybe"}})
            with self.assertRaisesRegex(ValueError, "return.evidence_refs contains unsafe path"):
                beo_state.append_event(root, issue_id, {**return_event, "payload": {**return_event["payload"], "evidence_refs": ["../escape"]}})
            learning_event = {"issue_id": issue_id, "kind": "learning_candidate", "phase": "reviewing", "actor": "beo-review", "timestamp": "2026-01-01T00:00:00Z", "payload": {"trigger": "repeat", "lesson": "safe", "safe_evidence_refs": [], "reuse_condition": "same"}}
            beo_state.append_event(root, issue_id, learning_event)
            with self.assertRaisesRegex(ValueError, "learning_candidate.safe_evidence_refs contains unsafe path"):
                beo_state.append_event(root, issue_id, {**learning_event, "payload": {**learning_event["payload"], "safe_evidence_refs": ["/tmp/unsafe"]}})
            suggestion_event = {"issue_id": issue_id, "kind": "learning_candidate_suggestion", "phase": "blocked", "actor": "beo-debug", "timestamp": "2026-01-01T00:00:00Z", "payload": {"trigger": "debug", "hypothesis": "save", "safe_evidence_refs": [], "caller_skill": "beo-review", "caller_route_context": "root_cause_diagnosis_needed"}}
            beo_state.append_event(root, issue_id, suggestion_event)
            with self.assertRaisesRegex(ValueError, "missing required field"):
                beo_state.append_event(root, issue_id, {**suggestion_event, "payload": {"trigger": "debug", "hypothesis": "save", "safe_evidence_refs": []}})
            with self.assertRaisesRegex(ValueError, "unknown field"):
                beo_state.append_event(root, issue_id, {**suggestion_event, "payload": {**suggestion_event["payload"], "extra": "nope"}})
            with self.assertRaisesRegex(ValueError, "learning_candidate_suggestion.safe_evidence_refs entries must be strings"):
                beo_state.append_event(root, issue_id, {**suggestion_event, "payload": {**suggestion_event["payload"], "safe_evidence_refs": [1]}})
            user_stop_event = {"issue_id": issue_id, "kind": "user_stop", "phase": "blocked", "actor": "beo-plan", "timestamp": "2026-01-01T00:00:00Z", "payload": {"gate_id": "gate-1", "reason": "needs input", "needed_from_user": "decision", "resume_route": "planned"}}
            beo_state.append_event(root, issue_id, user_stop_event)
            with self.assertRaisesRegex(ValueError, "unknown field"):
                beo_state.append_event(root, issue_id, {**user_stop_event, "unexpected": "nope"})
            with self.assertRaisesRegex(ValueError, "unknown field"):
                beo_state.append_event(root, issue_id, {**user_stop_event, "payload": {**user_stop_event["payload"], "extra": "nope"}})
            with self.assertRaisesRegex(ValueError, "user_stop resume_route"):
                beo_state.append_event(root, issue_id, {**user_stop_event, "payload": {**user_stop_event["payload"], "resume_route": "missing_route"}})
            change_request_event = {"issue_id": issue_id, "kind": "change_request", "phase": "reviewing", "actor": "beo-review", "timestamp": "2026-01-01T00:00:00Z", "payload": {"subtype": "scope_change", "reason": "needs file", "scope_delta": {}, "recommended_route": "repair_rescope"}}
            beo_state.append_event(root, issue_id, change_request_event)
            with self.assertRaisesRegex(ValueError, "change_request recommended_route"):
                beo_state.append_event(root, issue_id, {**change_request_event, "payload": {**change_request_event["payload"], "recommended_route": "missing_route"}})
            with self.assertRaisesRegex(ValueError, "change_request.subtype is invalid"):
                beo_state.append_event(root, issue_id, {**change_request_event, "payload": {**change_request_event["payload"], "subtype": "unknown"}})
            with self.assertRaisesRegex(ValueError, "normal transition must not be a runtime event"):
                beo_state.append_event(root, issue_id, dict(event, kind="PASS_EXECUTE"))
            with self.assertRaisesRegex(ValueError, "beo-debug may emit only"):
                beo_state.append_event(root, issue_id, dict(event, actor="beo-debug", kind="learning_candidate"))
            beo_state.append_event(root, issue_id, dict(event, actor="beo-review", kind="handoff", phase="reviewing", payload={**event["payload"], "extra": "allowed"}))
            events = beo_state.read_events(root, issue_id)
            self.assertEqual([item["actor"] for item in events if item["kind"] == "handoff"], ["beo-execute", "beo-review"])
            with self.assertRaisesRegex(ValueError, "beo-execute may emit only"):
                beo_state.append_event(root, issue_id, dict(event, kind="user_stop"))
            beo_state.append_event(root, issue_id, dict(event, actor="beo-review", kind="abandoned", phase="reviewing", payload={"reason": "cancelled", "requested_by": "user", "final_state": "abandoned"}))
            with self.assertRaisesRegex(ValueError, "invalid event kind"):
                beo_state.append_event(root, issue_id, dict(event, actor="beo-review", kind="invalid_event_kind", phase="reviewing"))
            with self.assertRaisesRegex(ValueError, "beo-review may emit only"):
                beo_state.append_event(root, issue_id, dict(event, actor="beo-review", kind="return"))
            with self.assertRaisesRegex(ValueError, "runtime event actor must be one of"):
                beo_state.append_event(root, issue_id, dict(event, actor="custom-agent"))
            import beo_check_events
            self.assertEqual(beo_check_events.validate_runtime_events(events, issue_id), [])
            self.assertEqual(beo_check_events.validate_runtime_events(None, issue_id), [])
            self.assertEqual(beo_check_events.validate_runtime_events([], issue_id), [])
            self.assertEqual(beo_check_events.validate_runtime_events({}, issue_id), ["runtime events must be a list"])
            self.assertEqual(beo_check_events.validate_runtime_events("", issue_id), ["runtime events must be a list"])
            self.assertIn("runtime event missing required field(s): timestamp", beo_check_events.validate_runtime_events([{key: value for key, value in event.items() if key != "timestamp"}], issue_id))
            self.assertIn("runtime event issue_id mismatch", beo_check_events.validate_runtime_events([dict(event, issue_id="br-other")], issue_id))
            self.assertIn("runtime event issue_id must be a non-empty string", beo_check_events.validate_runtime_events([dict(event, issue_id=123)], issue_id))
            self.assertIn("runtime event actor must be a non-empty string", beo_check_events.validate_runtime_events([dict(event, actor=123)], issue_id))
            self.assertIn("runtime event timestamp must be a non-empty string", beo_check_events.validate_runtime_events([dict(event, timestamp=123)], issue_id))
            self.assertIn("runtime event payload must be an object", beo_check_events.validate_runtime_events([dict(event, payload="debug")], issue_id))
            with self.assertRaisesRegex(ValueError, "runtime event actor must be"):
                beo_state.append_event(root, issue_id, dict(event, actor=123))

    def test_check_cli_enforces_prestate_and_approval_freshness(self):
        import beo_approval
        import beo_state
        import beo_ticket
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            (root / "README.md").write_text("clean\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            ticket = self.quick_ticket()
            beo_ticket.write_ticket(root, "br-1", ticket)
            beo_state.initialize_state(root, "br-1")
            (root / "README.md").write_text("dirty\n", encoding="utf-8")
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "assistant"}, None)), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "assistant"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "validate", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = __import__("beo_check").main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 1)
            self.assertTrue(any("dirty before validation" in err for err in report["errors"]))
            (root / "README.md").write_text("clean\n", encoding="utf-8")
            unrelated_forbid_ticket = self.quick_ticket()
            unrelated_forbid_ticket["scope"] = {"files": {"allow": ["README.md"], "forbid": ["secret.txt"]}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            broad_dirty_ticket = self.quick_ticket()
            broad_dirty_ticket["scope"] = {"files": {"allow": ["**"], "forbid": ["secret.txt"]}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            (root / "secret.txt").write_text("dirty forbidden\n", encoding="utf-8")
            self.assertEqual(__import__("beo_check_approval").validate_working_tree_prestate(root, unrelated_forbid_ticket), [])
            self.assertEqual(
                __import__("beo_check_approval").validate_working_tree_prestate(root, broad_dirty_ticket),
                ["forbidden-scope path is dirty before validation: secret.txt"],
            )
            self.assertEqual(
                __import__("beo_check").validate_containment(root, broad_dirty_ticket),
                ["changed path matches forbidden scope: secret.txt"],
            )
            (root / "secret.txt").unlink()
            with mock.patch("beo_check_scope.subprocess.run", return_value=mock.Mock(returncode=1, stderr="fatal", stdout="")):
                self.assertEqual(__import__("beo_check_approval").validate_working_tree_prestate(root, ticket), ["unable to inspect working tree: fatal"])
                self.assertEqual(__import__("beo_check").validate_containment(root, ticket), ["unable to inspect working tree: fatal"])

            profiles_path = root / "skills" / "beo" / "beo-reference" / "registry" / "profiles.json"
            profiles_path.parent.mkdir(parents=True)
            profiles_path.write_text("{bad json", encoding="utf-8")
            bad_profile = dict(ticket)
            bad_profile["scope"] = {"files": {"allow": [".env"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            self.assertTrue(any("failed to load profiles.json" in err for err in __import__("beo_check").validate_plan(root, bad_profile, {})))
            profiles_path.unlink()

            (root / "src").mkdir()
            (root / "src" / "tracked.py").write_text("tracked\n", encoding="utf-8")
            subprocess.run(["git", "add", "src/tracked.py"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "add tracked"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            outside = root.parent / "outside-beo-validate.txt"
            outside.write_text("secret\n", encoding="utf-8")
            try:
                (root / "src" / "escape.txt").symlink_to(outside)
                subprocess.run(["git", "add", "src/escape.txt"], cwd=root, check=True)
                subprocess.run(["git", "commit", "-m", "add escape symlink"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                glob_ticket = self.quick_ticket()
                glob_ticket["scope"] = {"files": {"allow": ["src/**"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
                glob_ticket["human_gates"] = {"status": "resolved", "gates": [{"type": "broad_scope_authorization", "scope": "src/**", "approver_handle": "human", "valid_for_issue_id": "br-1", "reason": "needed for test"}]}
                beo_ticket.write_ticket(root, "br-1", glob_ticket, overwrite=True)
                with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "assistant"}, None)), \
                     mock.patch.dict(os.environ, {"BR_ACTOR": "assistant"}), \
                     mock.patch.object(sys, "argv", ["beo_check.py", "--check", "validate", "--issue", "br-1", "--root", str(root)]), \
                     contextlib.redirect_stdout(io.StringIO()) as stdout:
                    rc = __import__("beo_check").main()
                report = json.loads(stdout.getvalue())
                self.assertEqual(rc, 1)
                self.assertIn("approved path is a symlink: src/escape.txt", report["errors"])
            finally:
                outside.unlink(missing_ok=True)

            beo_ticket.write_ticket(root, "br-1", ticket, overwrite=True)
            (root / "README.md").write_text("clean\n", encoding="utf-8")
            ticket_path = root / ".beads" / "artifacts" / "br-1" / "TICKET.yaml"
            ticket_hash = __import__("beo_git").file_hash(ticket_path)
            repo_head = __import__("beo_git").repo_head_sentinel(root)
            projection_hash = beo_approval.approval_projection_hash(ticket, ticket_file_hash=ticket_hash, repo_head=repo_head)
            prestate = __import__("beo_check_approval").compute_prestate(root, ticket)

            def approve(candidate):
                candidate["phase"] = "approved"
                candidate["approval"].update({"status": "PASS_EXECUTE", "approved_by": "beo-validate", "actor": "assistant", "ticket_file_hash": ticket_hash, "approval_projection_hash": projection_hash, "repo_head": repo_head, "prestate": prestate})
                return candidate

            beo_state.locked_update_state(root, "br-1", "beo-validate", approve)
            (root / "README.md").write_text("changed after approval\n", encoding="utf-8")
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "assistant", "title": "x"}, None)), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "assistant"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "execute-entry", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = __import__("beo_check").main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 1)
            self.assertIn("approval.prestate is stale", report["errors"])
            (root / "README.md").write_text("clean\n", encoding="utf-8")

            def stale_head(candidate):
                candidate["approval"].update({"repo_head": "stale-head"})
                return candidate

            beo_state.locked_update_state(root, "br-1", "beo-validate", stale_head)
            mismatch = dict(ticket, issue_id="br-2")
            ticket_path.write_text("version: 1\nissue_id: br-2\nmode: quick\nrequest: x\ndone_criteria: [ok]\nscope: {files: {allow: [README.md], forbid: []}, generated_outputs: [], verify: {commands: ['true']}}\n", encoding="utf-8")
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "assistant"}, None)), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "assistant"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "validate", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = __import__("beo_check").main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 1)
            self.assertIn("TICKET.yaml issue_id must match artifact issue_id", report["errors"])

            beo_ticket.write_ticket(root, "br-1", ticket, overwrite=True)
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "other"}, None)), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "assistant"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "validate", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = __import__("beo_check").main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 1)
            self.assertIn("br issue claim does not match acting actor", report["errors"])

            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "assistant", "title": "x"}, None)), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "assistant"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "execute-entry", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = __import__("beo_check").main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 1)
            self.assertIn("approval.repo_head is stale", report["errors"])

            stale_state = beo_state.read_state(root, "br-1")
            stale_state["phase"] = "executed"
            stale_state["execution"]["verify_results"] = [{"command": "true", "status": "passed"}]
            beo_state.atomic_write_json(root / ".beads" / "artifacts" / "br-1" / "state.json", stale_state)
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "assistant", "title": "x"}, None)), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "assistant"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "execute-entry", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = __import__("beo_check").main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 1)
            self.assertIn("execute-entry requires approved state", report["errors"])

            ticket_hash = __import__("beo_git").file_hash(ticket_path)
            repo_head = __import__("beo_git").repo_head_sentinel(root)
            projection_hash = beo_approval.approval_projection_hash(ticket, ticket_file_hash=ticket_hash, repo_head=repo_head)
            prestate = __import__("beo_check_approval").compute_prestate(root, ticket)

            def reapprove_clean(candidate):
                candidate["phase"] = "approved"
                candidate["approval"].update({"status": "PASS_EXECUTE", "ticket_file_hash": ticket_hash, "approval_projection_hash": projection_hash, "repo_head": repo_head, "prestate": prestate})
                return candidate

            beo_state.locked_update_state(root, "br-1", "beo-validate", reapprove_clean)
            pre_review_state = beo_state.read_state(root, "br-1")
            pre_review_state["execution"]["verify_results"] = [{"command": "true", "status": "passed"}]
            beo_state.atomic_write_json(root / ".beads" / "artifacts" / "br-1" / "state.json", pre_review_state)
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "assistant", "title": "x"}, None)), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "assistant"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "review-entry", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = __import__("beo_check").main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 1)
            self.assertIn("review-entry requires executed or reviewing state", report["errors"])

            def start_execution(candidate):
                candidate["phase"] = "executing"
                candidate["execution"]["actor"] = "assistant"
                candidate["execution"]["started_at"] = "2026-01-01T00:00:00Z"
                return candidate

            beo_state.locked_update_state(root, "br-1", "beo-execute", start_execution)

            def record_execution(candidate):
                candidate["phase"] = "executed"
                candidate["execution"]["verify_results"] = [{"command": "rtk git diff --check", "status": "passed"}]
                return candidate

            beo_state.locked_update_state(root, "br-1", "beo-execute", record_execution)
            missing_verify_state = beo_state.read_state(root, "br-1")
            missing_verify_state["execution"]["verify_results"] = []
            self.assertIn("execution verify_results are required before review", __import__("beo_check").validate_review(root, ticket, missing_verify_state))
            missing_verify_state["execution"]["verify_results"] = [{"command": "other", "status": "passed"}]
            self.assertIn("verification command missing result: rtk git diff --check", __import__("beo_check").validate_review(root, ticket, missing_verify_state))
            missing_verify_state["execution"]["verify_results"] = [{"command": "rtk git diff --check", "status": "failed"}]
            self.assertIn("verification command did not pass: rtk git diff --check", __import__("beo_check").validate_review(root, ticket, missing_verify_state))
            recorded_outside_state = json.loads(json.dumps(missing_verify_state))
            recorded_outside_state["execution"]["verify_results"] = [{"command": "rtk git diff --check", "status": "passed"}]
            recorded_outside_state["execution"]["changed_files"] = ["outside.txt"]
            self.assertIn("changed path outside approved scope: outside.txt", __import__("beo_check").validate_review(root, ticket, recorded_outside_state))
            broad_review_ticket = self.quick_ticket()
            broad_review_ticket["scope"] = {"files": {"allow": ["src/**"], "forbid": ["src/secret.py"]}, "generated_outputs": [], "verify": {"commands": ["rtk git diff --check"]}}
            recorded_forbidden_state = json.loads(json.dumps(missing_verify_state))
            recorded_forbidden_state["execution"]["verify_results"] = [{"command": "rtk git diff --check", "status": "passed"}]
            recorded_forbidden_state["execution"]["changed_files"] = ["src/secret.py"]
            self.assertIn("changed path matches forbidden scope: src/secret.py", __import__("beo_check").validate_review(root, broad_review_ticket, recorded_forbidden_state))
            (root / "README.md").write_text("execution changed approved file\n", encoding="utf-8")
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "assistant", "title": "x"}, None)), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "assistant"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "review-entry", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = __import__("beo_check").main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(report["errors"], [])

            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task"}, None)), \
                 mock.patch.dict(os.environ, {}, clear=True), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "status", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = __import__("beo_check").main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(report["errors"], [])

    def test_reservation_release_routes(self):
        import beo_reservation
        with tempfile.TemporaryDirectory() as tmp, contextlib.redirect_stdout(io.StringIO()):
            root = Path(tmp)
            with mock.patch.object(beo_reservation, "actor_identity", return_value="agent"):
                self.assertEqual(beo_reservation.cmd_reserve(root, "br-1", ["README.md"]), 0)
                self.assertEqual(beo_reservation.cmd_reserve(root, "br-1", ["README.md"]), 0)
                active = beo_reservation.get_active_reservations(beo_reservation.read_reservations(root))
                self.assertEqual(len(active), 1)
                self.assertEqual(active[0]["actor"], "agent")
                self.assertEqual(beo_reservation.cmd_release(root, "br-1", "verdict_accept"), 0)
                self.assertEqual(beo_reservation.cmd_reserve(root, "br-1", ["README.md"]), 0)
                self.assertEqual(beo_reservation.cmd_release(root, "br-1", "repair_rescope"), 0)
            with mock.patch.object(beo_reservation, "actor_identity", return_value=None):
                self.assertEqual(beo_reservation.cmd_reserve(root, "br-1", ["README.md"]), 1)
                self.assertEqual(beo_reservation.cmd_release(root, "br-1", "verdict_accept"), 1)
            self.assertEqual(beo_reservation.cmd_release(root, "br-1", "executed"), 1)
            with mock.patch.object(beo_reservation, "actor_identity", return_value="other"):
                self.assertEqual(beo_reservation.cmd_reserve(root, "br-2", ["README.md"]), 0)
            with mock.patch.object(beo_reservation, "actor_identity", return_value="agent"):
                self.assertEqual(beo_reservation.cmd_reserve(root, "br-2", ["README.md"]), 1)
                self.assertEqual(beo_reservation.cmd_check(root, "br-2", ["README.md"]), 1)
                self.assertEqual(beo_reservation.cmd_release(root, "br-2", "verdict_accept"), 1)
            active = beo_reservation.get_active_reservations(beo_reservation.read_reservations(root))
            self.assertEqual([r["actor"] for r in active if r["issue_id"] == "br-2"], ["other"])
            base_record = {
                "reservation_id": "res-aaaaaaaa",
                "issue_id": "br-test",
                "actor": "agent",
                "paths": ["test.txt"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }
            (root / ".beads" / "beo-reservations.jsonl").write_text(json.dumps(base_record) + "\n", encoding="utf-8")
            records = beo_reservation.read_reservations(root)
            self.assertEqual(records[0]["status"], "active")

            missing_active_metadata = {key: value for key, value in base_record.items() if key not in {"released_at", "release_reason"}}
            with self.assertRaisesRegex(ValueError, "missing required field"):
                beo_reservation.validate_reservation_record(missing_active_metadata, 1)
            unsafe_path_record = {**base_record, "status": "active", "paths": ["../escape"], "released_at": None, "release_reason": None}
            with self.assertRaisesRegex(ValueError, "unsafe repo-relative path"):
                beo_reservation.validate_reservation_record(unsafe_path_record, 1)
            absolute_path_record = {**unsafe_path_record, "paths": ["/tmp/escape"]}
            with self.assertRaisesRegex(ValueError, "path must be relative"):
                beo_reservation.validate_reservation_record(absolute_path_record, 1)
            pattern = __import__("json").loads((REFERENCE_ROOT / "registry" / "reservation-schema.json").read_text(encoding="utf-8"))["properties"]["paths"]["items"]["pattern"]
            for valid_path in ["README.md", "dir\\file.txt", "./README.md", ".\\README.md"]:
                self.assertRegex(valid_path, pattern)
            invalid_paths = ["../escape", "..\\escape", "/tmp/escape", "\\tmp\\escape", "C:/tmp/escape", "1:foo", ".", "./", ".\\", "a/../b", "a\nb", "a\rb", "a\tb"]
            for invalid_path in invalid_paths:
                self.assertIsNone(re.search(pattern, invalid_path), invalid_path)
            ticket_schema = json.loads((REFERENCE_ROOT / "registry" / "ticket.schema.json").read_text(encoding="utf-8"))
            state_schema = json.loads((REFERENCE_ROOT / "registry" / "state.schema.json").read_text(encoding="utf-8"))
            ticket_path_pattern = ticket_schema["$defs"]["safe_path"]["pattern"]
            state_path_pattern = state_schema["$defs"]["safe_path"]["pattern"]
            for invalid_path in invalid_paths:
                self.assertIsNone(re.search(ticket_path_pattern, invalid_path), invalid_path)
                self.assertIsNone(re.search(state_path_pattern, invalid_path), invalid_path)
            active_record = {
                "reservation_id": "res-aaaaaaaa",
                "issue_id": "br-active",
                "actor": "agent",
                "paths": ["active.txt"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }
            wrong_actor_record = {**active_record, "reservation_id": "res-bbbbbbbb", "actor": "other"}
            (root / ".beads" / "beo-reservations.jsonl").write_text(json.dumps(active_record) + "\n" + json.dumps(wrong_actor_record) + "\n", encoding="utf-8")
            current_actor_record = {**wrong_actor_record, "reservation_id": "res-cccccccc", "actor": "agent", "paths": ["current.txt"]}
            (root / ".beads" / "beo-reservations.jsonl").write_text(json.dumps(current_actor_record) + "\n" + json.dumps(wrong_actor_record) + "\n", encoding="utf-8")
            with mock.patch.object(beo_reservation, "actor_identity", return_value="agent"), \
                 mock.patch.object(beo_reservation, "now_utc", return_value=beo_reservation.parse_iso("2026-01-01T00:00:02Z")):
                self.assertEqual(beo_reservation.cmd_release(root, "br-active", "verdict_accept"), 0)
            records = beo_reservation.read_reservations(root)
            self.assertEqual(records[0]["status"], "released")
            self.assertEqual(records[0]["release_reason"], "verdict_accept")
            self.assertEqual(records[1]["status"], "active")
            with self.assertRaisesRegex(ValueError, "unknown field"):
                beo_reservation.validate_reservation_record({
                    "reservation_id": "res-1",
                    "issue_id": "br-1",
                    "actor": "agent",
                    "paths": ["README.md"],
                    "created_at": "2026-01-01T00:00:00Z",
                    "status": "active",
                    "surprise": True,
                }, 1)
            valid_record = {
                "reservation_id": "res-12345678",
                "issue_id": "br-1",
                "actor": "agent",
                "paths": ["README.md"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }
            beo_reservation.validate_reservation_record(valid_record, 1)
            with self.assertRaisesRegex(ValueError, "release metadata on active"):
                beo_reservation.validate_reservation_record({**valid_record, "released_at": "2026-01-01T00:30:00Z", "release_reason": "superseded"}, 1)
            with self.assertRaisesRegex(ValueError, "invalid status invalid_status"):
                beo_reservation.validate_reservation_record({**valid_record, "status": "invalid_status", "released_at": None, "release_reason": None}, 1)
            with self.assertRaisesRegex(ValueError, "invalid released metadata"):
                beo_reservation.validate_reservation_record({**valid_record, "status": "released", "released_at": "2026-01-01T00:30:00Z", "release_reason": "invalid_reason"}, 1)
            with self.assertRaisesRegex(ValueError, "invalid released_at"):
                beo_reservation.validate_reservation_record({**valid_record, "status": "released", "released_at": "not-a-time", "release_reason": "verdict_accept"}, 1)
            active_revoke = {**valid_record, "reservation_id": "res-11111111", "issue_id": "br-revoke-active"}
            released_revoke = {
                **valid_record,
                "reservation_id": "res-22222222",
                "issue_id": "br-revoke-released",
                "status": "released",
                "released_at": "2026-01-01T00:30:00Z",
                "release_reason": "verdict_accept",
            }
            superseded_revoke = {
                **valid_record,
                "reservation_id": "res-33333333",
                "issue_id": "br-revoke-active",
                "status": "superseded",
                "superseded_by": "res-44444444",
            }
            (root / ".beads" / "beo-reservations.jsonl").write_text(
                json.dumps(active_revoke) + "\n" + json.dumps(released_revoke) + "\n" + json.dumps(superseded_revoke) + "\n",
                encoding="utf-8",
            )
            with mock.patch.object(beo_reservation, "actor_identity", return_value="agent"):
                self.assertEqual(beo_reservation.cmd_revoke(root, "br-active", "", "br-comment:1"), 1)
                self.assertEqual(beo_reservation.cmd_revoke(root, "br-active", "human", ""), 1)
            self.assertEqual(beo_reservation.cmd_revoke(root, "br-revoke-active", "human", "br-comment:1"), 0)
            records = beo_reservation.read_reservations(root)
            revoked_active = next(r for r in records if r["reservation_id"] == "res-11111111")
            self.assertEqual(revoked_active["status"], "revoked")
            self.assertIsNone(revoked_active["released_at"])
            self.assertIsNone(revoked_active["release_reason"])
            still_superseded = next(r for r in records if r["reservation_id"] == "res-33333333")
            self.assertEqual(still_superseded["status"], "superseded")
            self.assertEqual(beo_reservation.cmd_revoke(root, "br-revoke-released", "human", "br-comment:2"), 0)
            records = beo_reservation.read_reservations(root)
            revoked_released = next(r for r in records if r["reservation_id"] == "res-22222222")
            self.assertEqual(revoked_released["status"], "revoked")
            self.assertEqual(revoked_released["released_at"], "2026-01-01T00:30:00Z")
            self.assertEqual(revoked_released["release_reason"], "verdict_accept")
            with self.assertRaisesRegex(ValueError, "both released_at and release_reason"):
                beo_reservation.validate_reservation_record({**revoked_active, "released_at": "2026-01-01T00:30:00Z", "release_reason": None}, 1)
            with self.assertRaisesRegex(ValueError, "superseded_by"):
                beo_reservation.validate_reservation_record({**revoked_active, "superseded_by": "res-44444444"}, 1)
            with self.assertRaisesRegex(ValueError, "invalid revoked_by|missing revoked_by|invalid revocation_ref"):
                beo_reservation.validate_reservation_record({**revoked_active, "revoked_by": 123}, 1)
            with self.assertRaisesRegex(ValueError, "invalid revoked_by|missing revoked_by|invalid revocation_ref"):
                beo_reservation.validate_reservation_record({**revoked_active, "revocation_ref": 123}, 1)
            with self.assertRaisesRegex(ValueError, "invalid superseded_by"):
                beo_reservation.validate_reservation_record({**still_superseded, "superseded_by": 123}, 1)


    def test_check_skill_bundle_passes_current_repo(self):
        import check_skill_bundle
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(check_skill_bundle.run_checks(), 0)

    def test_setup_qmd_and_recall_use_direct_commands(self):
        import beo_setup
        calls = []

        def fake_run_cmd(args, strip=True, cwd=None):
            calls.append(args)
            if args[:2] == ["br", "--version"]:
                return 0, "br", ""
            if args[:2] == ["bv", "--version"]:
                return 0, "bv", ""
            if args[:2] == ["qmd", "--version"]:
                return 0, "qmd", ""
            if args[:2] == ["obsidian", "help"]:
                return 0, "obsidian", ""
            if args == ["qmd", "collection", "list"]:
                return 0, '[{"name":"beo-learning"}]', ""
            if args == ["qmd", "status"]:
                return 0, "Pending: 0 need embedding", ""
            return 0, "{}", ""

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with mock.patch.object(beo_setup.beo_io, "run_cmd", side_effect=fake_run_cmd), \
                 mock.patch.dict(os.environ, {"BEO_QMD_COLLECTION": "beo-learning"}, clear=True), \
                 mock.patch.object(sys, "argv", ["beo_setup.py", "--root", str(root), "--configure-memory"]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = beo_setup.main()
            report = json.loads(stdout.getvalue())
        self.assertEqual(rc, 0)
        self.assertIn(["qmd", "collection", "list"], calls)
        self.assertTrue(report["qmd_collection"]["exists"])
        self.assertEqual(report["local_learning"]["path"], str((root / ".beads" / "learnings").resolve()))

    def test_memory_write_helpers(self):
        import beo_memory_write
        self.assertIn("success_pattern", beo_memory_write.load_learning_case_types())
        name = beo_memory_write.safe_note_name("br-1", "success_pattern", "valid-slug", {"success_pattern"})
        self.assertTrue(name.endswith("--success-pattern--br-1--valid-slug.md"))
        with self.assertRaises(ValueError):
            beo_memory_write.safe_note_name("../bad", "success_pattern", "valid", {"success_pattern"})

    def test_quick_fill_protected_paths_raise_value_error(self):
        import beo_quick_fill
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(ValueError, "protected path touched"):
                beo_quick_fill.check_protected_paths(root, [".env"])

    def test_state_rejects_inconsistent_accept_routes(self):
        import beo_state
        state = beo_state.initial_state("br-1")
        state["review"]["verdict"] = "accept"
        with self.assertRaisesRegex(ValueError, "accept verdict"):
            beo_state.validate_state(state, "br-1")
        state["review"]["route_condition_id"] = "repair_same_scope"
        with self.assertRaisesRegex(ValueError, "accept verdict"):
            beo_state.validate_state(state, "br-1")
        state = beo_state.initial_state("br-1")
        state["review"]["route_condition_id"] = "verdict_accept"
        with self.assertRaisesRegex(ValueError, "verdict_accept"):
            beo_state.validate_state(state, "br-1")

    def test_strict_approval_hash_binds_active_reservation_evidence(self):
        import beo_approval
        import beo_check_approval
        import beo_reservation
        import beo_ticket
        human_gate = {"type": "external_side_effect_authorization", "scope": "prod", "approver_handle": "human", "valid_for_issue_id": "br-1", "reason": "needed for test"}
        ticket = self.quick_ticket()
        ticket.update({
            "mode": "strict",
            "risk": {"summary": "risk", "rollback": "revert"},
            "human_gates": {"status": "resolved", "gates": [human_gate]},
            "strict": {
                "reason": "external",
                "authorization_refs": ["gate"],
                "rollback_refs": ["rollback"],
                "external_side_effects": [{"type": "deploy", "target": "prod", "authorization_ref": "gate", "precheck": "check", "rollback_or_compensation": "rollback", "postcheck": "post", "blast_radius": "bounded"}],
                "stateful_external_systems": [{"name": "prod", "effect_ref": "prod"}],
            },
        })
        beo_ticket.validate_plan_only(ticket)
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            frozen_now = beo_reservation.parse_iso("2026-01-01T00:00:00Z")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.object(beo_check_approval, "actor_identity", return_value="agent"):
                with self.assertRaisesRegex(ValueError, "strict approval requires an active reservation"):
                    beo_check_approval.compute_approval_fields(root, root / "TICKET.yaml", ticket)
                (root / ".beads").mkdir()
                (root / ".beads" / "beo-reservations.jsonl").write_text(json.dumps({
                    "reservation_id": "res-12345678",
                    "issue_id": "br-1",
                    "actor": "agent",
                    "paths": ["README.md"],
                    "created_at": "2026-01-01T00:00:00Z",
                    "status": "active",
                    "released_at": None,
                    "release_reason": None,
                    "superseded_by": None,
                    "revoked_by": None,
                    "revocation_ref": None,
                }) + "\n", encoding="utf-8")
                with_reservation = beo_check_approval.compute_approval_fields(root, root / "TICKET.yaml", ticket)["approval_projection_hash"]
        self.assertEqual(
            with_reservation,
            beo_approval.approval_projection_hash(
                ticket,
                ticket_file_hash="missing",
                repo_head="git:no-head",
                reservation_evidence=[{"reservation_id": "res-12345678", "issue_id": "br-1", "actor": "agent", "paths": ["README.md"], "status": "active"}],
            ),
        )

    def test_strict_reservation_evidence_fails_closed_on_bad_ledger(self):
        import beo_check_approval
        import beo_reservation
        ticket = self.quick_ticket()
        ticket["mode"] = "strict"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".beads").mkdir()
            ledger = root / ".beads" / "beo-reservations.jsonl"
            actor_patch = mock.patch.object(beo_check_approval, "actor_identity", return_value="agent")
            actor_patch.start()
            self.addCleanup(actor_patch.stop)
            ledger.write_text(json.dumps({"issue_id": "br-1", "status": "active"}) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid reservation_id|missing required field"):
                beo_check_approval.active_reservation_evidence(root, ticket)
            ledger.write_text(json.dumps({"issue_id": "br-2", "status": "active"}) + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "invalid reservation_id|missing required field"):
                beo_check_approval.active_reservation_evidence(root, ticket)
            ledger.write_text(json.dumps({
                "reservation_id": "res-12345678",
                "issue_id": "br-2",
                "actor": "agent",
                "paths": ["unrelated.txt"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }) + "\n", encoding="utf-8")
            frozen_now = beo_reservation.parse_iso("2026-01-01T00:00:02Z")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 self.assertRaisesRegex(ValueError, "does not cover approved path"):
                beo_check_approval.active_reservation_evidence(root, ticket)
            ledger.write_text(json.dumps({
                "reservation_id": "res-87654321",
                "issue_id": "br-1",
                "actor": "agent",
                "paths": ["README.md"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }) + "\n" + ledger.read_text(encoding="utf-8"), encoding="utf-8")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now):
                self.assertEqual(beo_check_approval.active_reservation_evidence(root, ticket)[0]["reservation_id"], "res-87654321")
            ledger.write_text(json.dumps({
                "reservation_id": "res-12345678",
                "issue_id": "br-2",
                "actor": "agent",
                "paths": ["README.md"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }) + "\n", encoding="utf-8")
            frozen_now = beo_reservation.parse_iso("2026-01-01T00:00:00Z")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 self.assertRaisesRegex(ValueError, "conflicts with another issue"):
                beo_check_approval.active_reservation_evidence(root, ticket)
            ledger.write_text(json.dumps({
                "reservation_id": "res-12345678",
                "issue_id": "br-1",
                "actor": "agent",
                "paths": ["src/**"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }) + "\n", encoding="utf-8")
            frozen_now = beo_reservation.parse_iso("2026-01-01T00:00:00Z")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 self.assertRaisesRegex(ValueError, "does not cover approved path"):
                beo_check_approval.active_reservation_evidence(root, ticket)
            broad_ticket = self.quick_ticket()
            broad_ticket.update(ticket)
            broad_ticket["scope"] = {"files": {"allow": ["src/**"], "forbid": []}, "generated_outputs": [], "verify": {"commands": ["true"]}}
            ledger.write_text(json.dumps({
                "reservation_id": "res-12345678",
                "issue_id": "br-1",
                "actor": "agent",
                "paths": ["src/private/**"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }) + "\n", encoding="utf-8")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 self.assertRaisesRegex(ValueError, "does not cover approved path"):
                beo_check_approval.active_reservation_evidence(root, broad_ticket)
            with mock.patch.object(beo_reservation, "actor_identity", return_value="agent"), \
                 mock.patch.object(beo_reservation, "now_utc", return_value=frozen_now), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = beo_reservation.cmd_check(root, "br-1", ["src/**"])
            self.assertEqual(rc, 1)
            self.assertEqual(json.loads(stdout.getvalue())["missing_paths"], ["src/**"])
            ledger.write_text(json.dumps({
                "reservation_id": "res-12345678",
                "issue_id": "br-1",
                "actor": "agent",
                "paths": ["**"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }) + "\n", encoding="utf-8")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.object(beo_check_approval, "actor_identity", return_value=None), \
                 self.assertRaisesRegex(ValueError, "BR_ACTOR or BEO_ACTOR"):
                beo_check_approval.active_reservation_evidence(root, broad_ticket)
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.object(beo_check_approval, "actor_identity", return_value="other"), \
                 self.assertRaisesRegex(ValueError, "different actor"):
                beo_check_approval.active_reservation_evidence(root, broad_ticket)
            ledger.write_text("".join([
                json.dumps({"reservation_id": "res-12345678", "issue_id": "br-1", "actor": "agent", "paths": ["**"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}) + "\n",
                json.dumps({"reservation_id": "res-87654321", "issue_id": "br-1", "actor": "other", "paths": ["src/foo.py"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}) + "\n",
            ]), encoding="utf-8")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.object(beo_check_approval, "actor_identity", return_value="agent"):
                self.assertEqual(beo_check_approval.active_reservation_evidence(root, broad_ticket)[0]["paths"], ["**"])
            ledger.write_text("".join([
                json.dumps({"reservation_id": "res-12345678", "issue_id": "br-1", "actor": "agent", "paths": ["README.md"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}) + "\n",
                json.dumps({"reservation_id": "res-87654321", "issue_id": "br-1", "actor": "other", "paths": ["src/**"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}) + "\n",
            ]), encoding="utf-8")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.object(beo_check_approval, "actor_identity", return_value="agent"), \
                 self.assertRaisesRegex(ValueError, "different actor"):
                beo_check_approval.active_reservation_evidence(root, broad_ticket)
            ledger.write_text("".join([
                json.dumps({"reservation_id": "res-12345678", "issue_id": "br-1", "actor": "agent", "paths": ["README.md"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}) + "\n",
                json.dumps({"reservation_id": "res-87654321", "issue_id": "br-1", "actor": "other", "paths": ["docs/**"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}) + "\n",
            ]), encoding="utf-8")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.object(beo_check_approval, "actor_identity", return_value="agent"):
                self.assertEqual(beo_check_approval.active_reservation_evidence(root, ticket)[0]["paths"], ["README.md"])
            ledger.write_text(json.dumps({
                "reservation_id": "res-12345678",
                "issue_id": "br-1",
                "actor": "agent",
                "paths": ["**"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }) + "\n", encoding="utf-8")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.object(beo_check_approval, "actor_identity", return_value="agent"):
                self.assertEqual(beo_check_approval.active_reservation_evidence(root, broad_ticket)[0]["paths"], ["**"])
            with mock.patch.object(beo_reservation, "actor_identity", return_value="agent"), \
                 mock.patch.object(beo_reservation, "now_utc", return_value=frozen_now), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = beo_reservation.cmd_check(root, "br-1", ["src/**"])
            self.assertEqual(rc, 0)
            self.assertEqual(json.loads(stdout.getvalue())["missing_paths"], [])
            ledger.write_text("".join([
                json.dumps({"reservation_id": "res-12345678", "issue_id": "br-1", "actor": "agent", "paths": ["**"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}) + "\n",
                json.dumps({"reservation_id": "res-87654321", "issue_id": "br-1", "actor": "other", "paths": ["src/foo.py"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}) + "\n",
            ]), encoding="utf-8")
            with mock.patch.object(beo_reservation, "actor_identity", return_value="agent"), \
                 mock.patch.object(beo_reservation, "now_utc", return_value=frozen_now), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = beo_reservation.cmd_check(root, "br-1", ["src/**"])
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(report["status"], "success")
            self.assertEqual(report["wrong_actor_reservations"][0]["actor"], "other")
            ledger.write_text("".join([
                json.dumps({"reservation_id": "res-12345678", "issue_id": "br-1", "actor": "agent", "paths": ["README.md"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}) + "\n",
                json.dumps({"reservation_id": "res-87654321", "issue_id": "br-1", "actor": "other", "paths": ["src/**"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}) + "\n",
            ]), encoding="utf-8")
            with mock.patch.object(beo_reservation, "actor_identity", return_value="agent"), \
                 mock.patch.object(beo_reservation, "now_utc", return_value=frozen_now), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = beo_reservation.cmd_check(root, "br-1", ["src/**"])
            self.assertEqual(rc, 1)
            self.assertEqual(json.loads(stdout.getvalue())["status"], "wrong_actor_reservation")
            ledger.write_text(json.dumps({
                "reservation_id": "res-12345678",
                "issue_id": "br-1",
                "actor": "agent",
                "paths": ["../escape"],
                "created_at": "2026-01-01T00:00:00Z",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }) + "\n", encoding="utf-8")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now):
                self.assertIn("invalid paths", beo_check_approval.validate_approval_envelope(root, root / "TICKET.yaml", ticket, {"approval": {"status": "PASS_EXECUTE"}})[0])
            ledger.write_text(json.dumps({
                "reservation_id": "res-12345678",
                "issue_id": "br-1",
                "actor": "agent",
                "paths": ["README.md"],
                "created_at": "2026-01-01T00:00:00+00:00",
                "status": "active",
                "released_at": None,
                "release_reason": None,
                "superseded_by": None,
                "revoked_by": None,
                "revocation_ref": None,
            }) + "\n", encoding="utf-8")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now):
                self.assertIn("invalid created_at", beo_check_approval.validate_approval_envelope(root, root / "TICKET.yaml", ticket, {"approval": {"status": "PASS_EXECUTE"}})[0])

    def test_validate_check_enforces_strict_reservation_ledger(self):
        import beo_check
        import beo_check_approval
        import beo_reservation
        import beo_state
        import beo_ticket
        human_gate = {"type": "external_side_effect_authorization", "scope": "prod", "approver_handle": "human", "valid_for_issue_id": "br-1", "reason": "needed for test"}
        ticket = self.quick_ticket()
        ticket.update({
            "mode": "strict",
            "risk": {"summary": "risk", "rollback": "revert"},
            "human_gates": {"status": "resolved", "gates": [human_gate]},
            "strict": {
                "reason": "external",
                "authorization_refs": ["gate"],
                "rollback_refs": ["rollback"],
                "external_side_effects": [{"type": "deploy", "target": "prod", "authorization_ref": "gate", "precheck": "check", "rollback_or_compensation": "rollback", "postcheck": "post", "blast_radius": "bounded"}],
                "stateful_external_systems": [{"name": "prod", "effect_ref": "prod"}],
            },
        })
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=root, check=True)
            subprocess.run(["git", "config", "user.name", "Test User"], cwd=root, check=True)
            (root / "README.md").write_text("clean\n", encoding="utf-8")
            subprocess.run(["git", "add", "README.md"], cwd=root, check=True)
            subprocess.run(["git", "commit", "-m", "initial"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            beo_ticket.write_ticket(root, "br-1", ticket)
            beo_state.initialize_state(root, "br-1")
            frozen_now = beo_reservation.parse_iso("2026-01-01T00:00:00Z")
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "agent"}, None)), \
                 mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "agent"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "validate", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = beo_check.main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 1)
            self.assertIn("strict approval requires an active reservation", report["errors"])

            ledger = root / ".beads" / "beo-reservations.jsonl"
            valid_current = {"reservation_id": "res-12345678", "issue_id": "br-1", "actor": "agent", "paths": ["README.md"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}
            ledger.write_text(json.dumps(valid_current) + "\n", encoding="utf-8")
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "agent"}, None)), \
                 mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "agent"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "validate", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = beo_check.main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(report["errors"], [])

            valid_broad = {**valid_current, "reservation_id": "res-bbbbbbbb", "paths": ["**"]}
            ledger.write_text(json.dumps(valid_broad) + "\n", encoding="utf-8")
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "agent"}, None)), \
                 mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "agent"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "validate", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = beo_check.main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 0)
            self.assertEqual(report["errors"], [])

            incomplete_current = {**valid_current, "reservation_id": "res-abcdef12", "paths": ["docs/**"]}
            ledger.write_text(json.dumps(incomplete_current) + "\n", encoding="utf-8")
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "agent"}, None)), \
                 mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "agent"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "validate", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = beo_check.main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 1)
            self.assertIn("active reservation does not cover approved path(s): README.md", report["errors"])

            conflicting_other_issue = {"reservation_id": "res-87654321", "issue_id": "br-2", "actor": "other", "paths": ["README.md"], "created_at": "2026-01-01T00:00:00Z", "status": "active", "released_at": None, "release_reason": None, "superseded_by": None, "revoked_by": None, "revocation_ref": None}
            ledger.write_text(json.dumps(valid_current) + "\n" + json.dumps(conflicting_other_issue) + "\n", encoding="utf-8")
            with mock.patch("beo_check.run_br_show", return_value=({"id": "br-1", "type": "task", "assignee": "agent"}, None)), \
                 mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.dict(os.environ, {"BR_ACTOR": "agent"}), \
                 mock.patch.object(sys, "argv", ["beo_check.py", "--check", "validate", "--issue", "br-1", "--root", str(root)]), \
                 contextlib.redirect_stdout(io.StringIO()) as stdout:
                rc = beo_check.main()
            report = json.loads(stdout.getvalue())
            self.assertEqual(rc, 1)
            self.assertIn("active reservation conflicts with another issue: br-2", report["errors"])

            invalid_released = {**valid_current, "reservation_id": "res-aaaaaaaa", "status": "released", "released_at": "2026-01-01T00:30:00Z", "release_reason": "invalid_reason"}
            ledger.write_text(json.dumps(invalid_released) + "\n" + json.dumps(valid_current) + "\n", encoding="utf-8")
            with mock.patch.object(beo_check_approval, "now_utc", return_value=frozen_now), \
                 mock.patch.object(beo_check_approval, "actor_identity", return_value="agent"), \
                 self.assertRaisesRegex(ValueError, "invalid released metadata"):
                beo_check_approval.active_reservation_evidence(root, ticket)


if __name__ == "__main__":
    unittest.main()
