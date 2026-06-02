#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import beo_io
import beo_memory_tools


def collection_exists(output: str, collection: str) -> bool:
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, list):
        return any((item == collection) if isinstance(item, str) else (isinstance(item, dict) and item.get("name") == collection) for item in data)
    if isinstance(data, dict) and isinstance(data.get("collections"), list):
        return collection_exists(json.dumps(data["collections"]), collection)
    for line in output.splitlines():
        fields = [field for field in re.split(r"[\s│|]+", line.strip()) if field]
        if fields and fields[0] == collection:
            return True
    return False


def warn(results: dict, message: str) -> None:
    results.setdefault("warnings", []).append(message)


def pending_embeddings(output: str) -> int | None:
    try:
        data = json.loads(output)
    except json.JSONDecodeError:
        data = None
    if isinstance(data, dict):
        value = data.get("pending_embeddings", data.get("pending"))
        if isinstance(value, int):
            return value
        if isinstance(value, str) and value.isdigit():
            return int(value)
    match = re.search(r"pending\D+(\d+)|(?:^|\D)(\d+)\D+(?:need embedding|pending)", output, re.IGNORECASE)
    if match:
        return int(next(group for group in match.groups() if group is not None))
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BEO-on-Beads integration health.")
    parser.add_argument("--configure-memory", action="store_true", help="Create local learning/qmd memory configuration when explicitly authorized.")
    parser.add_argument("--refresh-memory-index", action="store_true", help="Run qmd index/embed maintenance for configured learning notes.")
    parser.add_argument("--root", default=".", help="Workspace root path")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    results = {"status": "ready", "dependencies": {}, "vault": {}, "local_learning": {}, "qmd_collection": {}, "errors": []}

    try:
        __import__("yaml")
        results["dependencies"]["PyYAML"] = "present"
    except ImportError:
        results["dependencies"]["PyYAML"] = "missing"
        results["errors"].append("PyYAML is required for TICKET.yaml parsing, BEO helper checks, state/event updates, and learning frontmatter validation")

    for binary in ["br", "bv", "qmd", "obsidian"]:
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

    env = beo_memory_tools.resolve_obsidian_env()
    vault_name = env["vault_name"]
    vault_path = env["vault_path"]
    learning_dir = env["learning_dir"]
    qmd_collection = env["qmd_collection"]
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

    if results["dependencies"].get("qmd") == "missing":
        results["qmd"] = {"status": "missing", "reason": "qmd_binary_missing"}
    elif not qmd_collection:
        results["qmd_collection"].update({"name": None, "exists": False, "needs_configuration": True})
        warn(results, "BEO_QMD_COLLECTION or an Obsidian vault name is required before configuring qmd memory")
    else:
        code, out, _ = beo_io.run_cmd(["qmd", "collection", "list"])
        if code != 0:
            results["qmd"] = {"status": "degraded", "reason": "collection_status_unavailable"}
            results["qmd_collection"].update({"name": qmd_collection, "status": "degraded", "reason": "collection_status_unavailable", "exists": False})
            warn(results, "qmd collection discovery failed")
        else:
            found = collection_exists(out, qmd_collection)
            if found:
                results["qmd_collection"].update({"name": qmd_collection, "exists": True})
            elif args.configure_memory:
                add_target = str(learning_dir) if learning_dir and results["vault"].get("exists") else str(local_learning_dir)
                add_code, _, add_err = beo_io.run_cmd(["qmd", "collection", "add", qmd_collection, add_target])
                if add_code == 0:
                    results["qmd_collection"].update({"name": qmd_collection, "exists": True, "added": True})
                else:
                    results["qmd_collection"].update({"name": qmd_collection, "exists": False, "needs_configuration": True})
                    warn(results, f"Failed to add qmd collection: {add_err}")
            else:
                results["qmd_collection"].update({"name": qmd_collection, "exists": False, "needs_configuration": True})

            if results["qmd_collection"].get("exists"):
                if args.refresh_memory_index:
                    u_code, _, u_err = beo_io.run_cmd(["qmd", "index", "update"])
                    results["qmd_collection"]["index_refreshed"] = u_code == 0
                    if u_code != 0:
                        warn(results, f"Failed to run qmd update: {u_err}")
                s_code, s_out, _ = beo_io.run_cmd(["qmd", "status"])
                pending_count = pending_embeddings(s_out) if s_code == 0 else None
                if pending_count is None:
                    results["qmd"] = {"status": "degraded", "reason": "index_status_unavailable"}
                    results["qmd_collection"].update({"status": "degraded", "reason": "index_status_unavailable"})
                else:
                    results["qmd_collection"].update({"status": "indexed", "pending_embeddings": pending_count})
                    if pending_count > 0 and args.refresh_memory_index:
                        emb_code, _, emb_err = beo_io.run_cmd(["qmd", "index", "embed"])
                        if emb_code == 0:
                            results["qmd_collection"].update({"embeddings_refreshed": True, "pending_embeddings": 0})
                        else:
                            warn(results, f"Failed to run qmd embed: {emb_err}")
                    elif pending_count > 0:
                        results["qmd_collection"]["needs_refresh"] = True

    memory_config_failed = args.configure_memory and (results["local_learning"].get("needs_configuration") or results["qmd_collection"].get("needs_configuration"))
    if results["dependencies"].get("br") == "missing" or results["dependencies"].get("PyYAML") == "missing":
        results["status"] = "blocked"
    elif memory_config_failed:
        results["status"] = "degraded"
    else:
        # qmd/obsidian/bv being missing is optional and does not make BEO degraded
        results["status"] = "ready"

    print(json.dumps(results, indent=2))
    return 0 if results["status"] != "blocked" else 1


if __name__ == "__main__":
    sys.exit(main())
