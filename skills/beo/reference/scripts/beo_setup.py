#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path

# Add script directory to sys.path for importing beo_utils
sys.path.insert(0, str(Path(__file__).parent))
import beo_utils
import os


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
        code, out, err = beo_utils.run_cmd(["obsidian", "vaults", "--verbose"])
        if code != 0:
            results["vault"]["status"] = "degraded"
            warn(results, "Failed to list vaults via obsidian CLI")
        else:
            vaults = out.split("\n")
            if vault_name in vaults:
                results["vault"]["name"] = vault_name
                p_code, p_out, p_err = beo_utils.run_cmd(["obsidian", f"vault={vault_name}", "vault", "info=path"])
                if p_code == 0:
                    vault_path = Path(p_out)
                    learning_dir = vault_path / "beo-learnings"
            else:
                warn(results, f"Vault '{vault_name}' not found in registered obsidian vaults: {vaults}")

    results["vault"]["path"] = str(vault_path)
    results["vault"]["learning_dir"] = str(learning_dir)

    vault_configured = explicitly_configured_vault()
    if learning_dir.exists() and learning_dir.is_dir():
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

    if results["dependencies"].get("qmd") != "missing":
        code, out, err = beo_utils.run_cmd(["qmd", "collection", "list"])
        if code == 0:
            if collection_exists(out, qmd_collection):
                results["qmd_collection"].update({"name": qmd_collection, "exists": True})
            elif args.configure_memory:
                if not results["vault"].get("exists") or not vault_configured:
                    warn(results, "qmd collection was not added because explicit vault configuration is required")
                    results["qmd_collection"].update({"name": qmd_collection, "exists": False, "needs_configuration": True})
                else:
                    add_code, add_out, add_err = beo_utils.run_cmd([
                        "qmd", "collection", "add", str(learning_dir), "--name", qmd_collection, "--mask", "**/*.md"
                    ])
                    if add_code == 0:
                        results["qmd_collection"].update({"name": qmd_collection, "exists": True, "added": True})
                    else:
                        warn(results, f"Failed to add qmd collection for {learning_dir}: {add_err}")
                        results["qmd_collection"].update({"name": qmd_collection, "exists": False, "needs_configuration": True})
            else:
                results["qmd_collection"].update({"name": qmd_collection, "exists": False, "needs_configuration": True})

            if results["qmd_collection"].get("exists"):
                if args.refresh_memory_index:
                    u_code, u_out, u_err = beo_utils.run_cmd(["qmd", "update"])
                    results["qmd_collection"]["index_refreshed"] = u_code == 0
                    if u_code != 0:
                        warn(results, f"Failed to run qmd update: {u_err}")
                s_code, s_out, s_err = beo_utils.run_cmd(["qmd", "status"])
                if s_code == 0:
                    results["qmd_collection"]["status"] = "indexed"
                    pending_match = re.search(r"Pending:\s*(\d+)\s+need\s+embedding", s_out)
                    pending_count = int(pending_match.group(1)) if pending_match else 0
                    results["qmd_collection"]["pending_embeddings"] = pending_count
                    if pending_count > 0 and args.refresh_memory_index:
                        emb_code, emb_out, emb_err = beo_utils.run_cmd(["qmd", "embed"])
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
