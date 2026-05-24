#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import beo_utils
from beo_command import CommandAdapter


def explicitly_configured_vault() -> bool:
    return bool(os.environ.get("BEO_OBSIDIAN_VAULT")) and bool(
        os.environ.get("BEO_OBSIDIAN_VAULT_NAME") or os.environ.get("BEO_OBSIDIAN_VAULT_ID")
    )


def collection_exists(output: str, collection: str) -> bool:
    for line in output.splitlines():
        fields = [field for field in re.split(r"[\s│|]+", line.strip()) if field]
        if fields and fields[0] == collection:
            return True
    return False


def warn(results: dict, message: str) -> None:
    results.setdefault("warnings", []).append(message)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check BEO-on-Beads integration health.")
    parser.add_argument("--configure-memory", action="store_true", help="Create the learning directory and qmd collection when missing.")
    parser.add_argument("--refresh-memory-index", action="store_true", help="Run qmd index/embed maintenance for configured learning notes.")
    args = parser.parse_args()

    adapter = CommandAdapter(Path(".").resolve())

    results = {
        "status": "success",
        "dependencies": {},
        "vault": {},
        "qmd_collection": {},
        "errors": [],
    }

    # br is lifecycle-critical; bv/qmd/obsidian are degraded capabilities.
    for binary in ["br", "bv", "qmd", "obsidian"]:
        code, out, err = beo_utils.run_cmd([binary, "--version"] if binary != "obsidian" else [binary, "help"])
        if code == -1:
            results["dependencies"][binary] = "missing"
            if binary == "br":
                results["errors"].append("br CLI is not installed or not in PATH")
                results["status"] = "failed"
            else:
                warn(results, f"{binary} CLI is unavailable; related BEO capability is degraded")
        elif binary == "obsidian":
            results["dependencies"]["obsidian"] = "present"
        else:
            results["dependencies"][binary] = out.split("\n")[0]

    env = beo_utils.resolve_obsidian_env()
    vault_name = env["vault_name"]
    vault_path = env["vault_path"]
    learning_dir = env["learning_dir"]
    qmd_collection = env["qmd_collection"]

    if results["dependencies"].get("obsidian") == "missing":
        results["vault"]["status"] = "memory_unavailable"
    else:
        try:
            obsidian_vaults_argv = adapter.build_argv("obsidian.vaults", owner="beo-setup")
        except Exception as exc:
            warn(results, f"CommandAdapter failed to build obsidian.vaults argv: {exc}")
            obsidian_vaults_argv = []
        code, out, err = beo_utils.run_cmd(obsidian_vaults_argv) if obsidian_vaults_argv else (1, "", "CommandAdapter failed")
        if code != 0:
            results["vault"]["status"] = "degraded"
            warn(results, "Failed to list vaults via obsidian CLI")
        else:
            vaults = out.split("\n")
            if vault_name and vault_name in vaults:
                results["vault"]["name"] = vault_name
                try:
                    obsidian_info_argv = adapter.build_argv("obsidian.vault.info", owner="beo-setup", vault_name=vault_name)
                except Exception as exc:
                    warn(results, f"CommandAdapter failed to build obsidian.vault.info argv: {exc}")
                    obsidian_info_argv = []
                p_code, p_out, p_err = beo_utils.run_cmd(obsidian_info_argv) if obsidian_info_argv else (1, "", "CommandAdapter failed")
                if p_code == 0:
                    vault_path = Path(p_out)
                    learning_dir = vault_path / "beo-learnings"
            elif vault_name:
                warn(results, f"Vault '{vault_name}' not found in registered obsidian vaults: {vaults}")

    results["vault"]["path"] = str(vault_path) if vault_path else None
    results["vault"]["learning_dir"] = str(learning_dir) if learning_dir else None

    vault_configured = explicitly_configured_vault()
    if learning_dir is None:
        results["vault"].update({"exists": False, "needs_configuration": True})
        if args.configure_memory:
            warn(results, "BEO_OBSIDIAN_VAULT and BEO_OBSIDIAN_VAULT_NAME or BEO_OBSIDIAN_VAULT_ID are required before creating beo-learnings")
    elif learning_dir.exists() and learning_dir.is_dir():
        results["vault"]["exists"] = True
        if args.configure_memory and not vault_configured:
            warn(results, "BEO_OBSIDIAN_VAULT and BEO_OBSIDIAN_VAULT_NAME or BEO_OBSIDIAN_VAULT_ID are required before configuring beo-learnings")
            results["vault"].update({"needs_configuration": True})
    elif args.configure_memory:
        if not vault_configured:
            warn(results, "BEO_OBSIDIAN_VAULT and BEO_OBSIDIAN_VAULT_NAME or BEO_OBSIDIAN_VAULT_ID are required before creating beo-learnings")
            results["vault"].update({"exists": False, "needs_configuration": True})
        else:
            try:
                learning_dir.mkdir(parents=True, exist_ok=True)
                results["vault"].update({"created": True, "exists": True})
            except Exception as exc:
                warn(results, f"Failed to create learnings directory: {exc}")
                results["vault"].update({"exists": False, "needs_configuration": True})
    else:
        results["vault"].update({"exists": False, "needs_configuration": True})

    if results["dependencies"].get("qmd") != "missing" and not qmd_collection:
        results["qmd_collection"].update({"name": None, "exists": False, "needs_configuration": True})
        warn(results, "BEO_QMD_COLLECTION or an Obsidian vault name is required before configuring qmd memory")

    if results["dependencies"].get("qmd") != "missing" and qmd_collection:
        try:
            qmd_list_argv = adapter.build_argv("qmd.collection.list", owner="beo-setup")
        except Exception as exc:
            warn(results, f"CommandAdapter failed to build qmd.collection.list argv: {exc}")
            qmd_list_argv = []
        code, out, err = beo_utils.run_cmd(qmd_list_argv) if qmd_list_argv else (1, "", "CommandAdapter failed")
        if code == 0:
            if collection_exists(out, qmd_collection):
                results["qmd_collection"].update({"name": qmd_collection, "exists": True})
            elif args.configure_memory:
                if not results["vault"].get("exists") or not vault_configured:
                    warn(results, "qmd collection was not added because explicit vault configuration is required")
                    results["qmd_collection"].update({"name": qmd_collection, "exists": False, "needs_configuration": True})
                else:
                    try:
                        qmd_add_argv = adapter.build_argv(
                            "qmd.collection.add_obsidian_vault",
                            owner="beo-setup",
                            vault_learning_dir=str(learning_dir),
                            collection=qmd_collection
                        )
                    except Exception as exc:
                        warn(results, f"CommandAdapter failed to build qmd.collection.add_obsidian_vault argv: {exc}")
                        qmd_add_argv = []
                    add_code, add_out, add_err = beo_utils.run_cmd(qmd_add_argv) if qmd_add_argv else (1, "", "CommandAdapter failed")
                    if add_code == 0:
                        results["qmd_collection"].update({"name": qmd_collection, "exists": True, "added": True})
                    else:
                        warn(results, f"Failed to add qmd collection for {learning_dir}: {add_err}")
                        results["qmd_collection"].update({"name": qmd_collection, "exists": False, "needs_configuration": True})
            else:
                results["qmd_collection"].update({"name": qmd_collection, "exists": False, "needs_configuration": True})

            if results["qmd_collection"].get("exists"):
                if args.refresh_memory_index:
                    try:
                        qmd_update_argv = adapter.build_argv("qmd.index.update", owner="beo-setup")
                    except Exception as exc:
                        warn(results, f"CommandAdapter failed to build qmd.index.update argv: {exc}")
                        qmd_update_argv = []
                    u_code, u_out, u_err = beo_utils.run_cmd(qmd_update_argv) if qmd_update_argv else (1, "", "CommandAdapter failed")
                    results["qmd_collection"]["index_refreshed"] = u_code == 0
                    if u_code != 0:
                        warn(results, f"Failed to run qmd update: {u_err}")
                try:
                    qmd_status_argv = adapter.build_argv("qmd.status", owner="beo-setup")
                except Exception as exc:
                    warn(results, f"CommandAdapter failed to build qmd.status argv: {exc}")
                    qmd_status_argv = []
                s_code, s_out, s_err = beo_utils.run_cmd(qmd_status_argv) if qmd_status_argv else (1, "", "CommandAdapter failed")
                if s_code == 0:
                    results["qmd_collection"]["status"] = "indexed"
                    pending_match = re.search(r"Pending:\s*(\d+)\s+need\s+embedding", s_out)
                    pending_count = int(pending_match.group(1)) if pending_match else 0
                    results["qmd_collection"]["pending_embeddings"] = pending_count
                    if pending_count > 0 and args.refresh_memory_index:
                        try:
                            qmd_embed_argv = adapter.build_argv("qmd.index.embed", owner="beo-setup")
                        except Exception as exc:
                            warn(results, f"CommandAdapter failed to build qmd.index.embed argv: {exc}")
                            qmd_embed_argv = []
                        emb_code, emb_out, emb_err = beo_utils.run_cmd(qmd_embed_argv) if qmd_embed_argv else (1, "", "CommandAdapter failed")
                        if emb_code == 0:
                            results["qmd_collection"].update({"embeddings_refreshed": True, "pending_embeddings": 0})
                        else:
                            warn(results, f"Failed to run qmd embed: {emb_err}")
                    elif pending_count > 0:
                        results["qmd_collection"]["needs_refresh"] = True
                else:
                    results["qmd_collection"]["status"] = "error_fetching_status"
        else:
            warn(results, "Failed to list qmd collections")
            results["qmd_collection"]["status"] = "degraded"

    print(json.dumps(results, indent=2))
    return 0 if results["status"] == "success" else 1


if __name__ == "__main__":
    sys.exit(main())
