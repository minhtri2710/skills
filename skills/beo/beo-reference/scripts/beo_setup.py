#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import beo_io
import beo_memory_write


MANAGED_START = "<!-- BEO:MANAGED START -->"
MANAGED_END = "<!-- BEO:MANAGED END -->"
AGENTS_TEMPLATE = Path(__file__).resolve().parent.parent / "templates" / "AGENTS.template.md"


def warn(results: dict, message: str) -> None:
    results.setdefault("warnings", []).append(message)


def load_agents_template(results: dict) -> str | None:
    try:
        return AGENTS_TEMPLATE.read_text()
    except OSError as exc:
        warn(results, f"Failed to read AGENTS template: {exc}")
        return None


def inspect_agents(root: Path, results: dict) -> dict:
    agents_path = root / "AGENTS.md"
    agents = {"path": str(agents_path)}
    results["agents"] = agents
    if not agents_path.exists():
        agents.update({"status": "missing", "needs_install": True})
        return agents
    try:
        content = agents_path.read_text()
    except OSError as exc:
        agents.update({"status": "unreadable", "needs_manual_repair": True})
        warn(results, f"Failed to read AGENTS.md: {exc}")
        return agents
    start_count = content.count(MANAGED_START)
    end_count = content.count(MANAGED_END)
    if start_count == 1 and end_count == 1 and content.index(MANAGED_START) < content.index(MANAGED_END):
        template = load_agents_template(results)
        current_block = content[content.index(MANAGED_START):content.index(MANAGED_END) + len(MANAGED_END)]
        template_block = template.strip() if template is not None else None
        agents.update({"status": "managed_current" if current_block.strip() == template_block else "managed_stale", "managed_block": True})
    elif start_count == 0 and end_count == 0:
        agents.update({"status": "unmanaged_exists", "needs_install": True, "can_append_managed_block": True})
    else:
        agents.update({"status": "malformed_markers", "needs_manual_repair": True})
    return agents


def install_agents(root: Path, results: dict) -> None:
    agents = inspect_agents(root, results)
    template = load_agents_template(results)
    if template is None:
        agents.update({"install_attempted": True, "install_succeeded": False, "status": "template_missing"})
        return
    agents_path = Path(agents["path"])
    if agents["status"] == "missing":
        agents_path.write_text(template)
        agents.update({"status": "installed", "install_attempted": True, "install_succeeded": True})
        return
    if agents["status"] in {"managed_current", "managed_stale"}:
        content = agents_path.read_text()
        start = content.index(MANAGED_START)
        end = content.index(MANAGED_END) + len(MANAGED_END)
        new_content = content[:start] + template.strip() + content[end:]
        agents_path.write_text(new_content)
        agents.update({"status": "managed_refreshed", "install_attempted": True, "install_succeeded": True})
        return
    if agents["status"] == "unmanaged_exists":
        content = agents_path.read_text()
        separator = "\n\n" if not content.endswith("\n") else "\n"
        agents_path.write_text(content + separator + template.rstrip() + "\n")
        agents.update({"status": "managed_appended", "install_attempted": True, "install_succeeded": True})
        return
    agents.update({"install_attempted": True, "install_succeeded": False})
    if agents["status"] == "malformed_markers":
        warn(results, "AGENTS.md has malformed BEO managed markers; manual repair required, not editing")


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BEO-on-Beads integration health.")
    parser.add_argument("--configure-memory", action="store_true", help="Create local learning/Obsidian memory configuration when explicitly authorized.")
    parser.add_argument("--install-agents", action="store_true", help="Create AGENTS.md from the BEO template when missing; replace the BEO managed block when valid markers are present. Requires explicit authorization.")
    parser.add_argument("--root", default=".", help="Workspace root path")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    results = {"status": "ready", "dependencies": {}, "agents": {}, "vault": {}, "local_learning": {}, "errors": []}

    if args.install_agents:
        install_agents(root, results)
    else:
        inspect_agents(root, results)

    # TICKET.json, harness-proposal.json, and learning frontmatter are all
    # parsed from stdlib (json + a minimal frontmatter parser in
    # beo_memory_write). No third-party Python packages are required.

    for binary in ["br", "bv", "obsidian"]:
        argv = [binary, "--version"] if binary != "obsidian" else [binary, "help"]
        code, out, _ = beo_io.run_cmd(argv)
        if code == -1:
            results["dependencies"][binary] = "missing"
            if binary == "br":
                results["errors"].append("br CLI is not installed or not in PATH")
            else:
                warn(results, f"{binary} CLI is unavailable; optional BEO memory/triage capability is degraded but not blocking")
        else:
            results["dependencies"][binary] = "present" if binary == "obsidian" else (out.split("\n")[0] if out else "present")

    env = beo_memory_write.resolve_obsidian_env()
    vault_name = env["vault_name"]
    vault_path = env["vault_path"]
    learning_dir = env["learning_dir"]
    local_learning_dir = root / ".beads" / "learnings"

    results["local_learning"]["path"] = str(local_learning_dir)
    if local_learning_dir.is_dir():
        results["local_learning"]["exists"] = True
    elif args.configure_memory:
        try:
            local_learning_dir.mkdir(parents=True, exist_ok=True)
            results["local_learning"].update({"exists": True, "created": True})
        except Exception as exc:
            results["local_learning"].update({"exists": False, "needs_configuration": True})
            warn(results, f"Failed to create local learning directory: {exc}")
    else:
        results["local_learning"].update({"exists": False, "needs_configuration": True})

    if results["dependencies"].get("obsidian") == "missing":
        results["vault"]["status"] = "obsidian_missing"
    elif not vault_name:
        results["vault"]["status"] = "obsidian_present_unconfigured"
    else:
        results["vault"].update({"status": "obsidian_present_configured_unverified", "name": vault_name})
        code, out, _ = beo_io.run_cmd(["obsidian", f"vault={vault_name}", "vault"])
        if code == 0 and out.strip():
            vault_path = Path(out.strip()).expanduser().resolve()
            learning_dir = vault_path / "beo-learnings"
        results["vault"].update({"path": str(vault_path) if vault_path else None, "learning_dir": str(learning_dir) if learning_dir else None})
        if learning_dir and learning_dir.is_dir():
            results["vault"].update({"status": "obsidian_write_succeeded", "exists": True})
        elif args.configure_memory and learning_dir:
            try:
                learning_dir.mkdir(parents=True, exist_ok=True)
                results["vault"].update({"status": "obsidian_write_succeeded", "exists": True})
            except Exception as exc:
                results["vault"].update({"status": "obsidian_write_failed_fallback_local", "exists": False})
                warn(results, f"Failed to create learnings directory: {exc}")
        else:
            results["vault"].update({"status": "obsidian_write_failed_fallback_local", "exists": False})

    memory_config_failed = args.configure_memory and results["local_learning"].get("needs_configuration")
    agents_config_failed = args.install_agents and not results["agents"].get("install_succeeded")
    if results["dependencies"].get("br") == "missing" or results["dependencies"].get("PyYAML") == "missing":
        results["status"] = "blocked"
    elif memory_config_failed or agents_config_failed:
        results["status"] = "degraded"
    else:
        # Obsidian/bv being missing is optional and does not make BEO degraded
        results["status"] = "ready"

    print(json.dumps(results, indent=2))
    return 0 if results["status"] != "blocked" else 1


if __name__ == "__main__":
    sys.exit(main())
