#!/usr/bin/env python3
import json
import os
import sys
from pathlib import Path

# Add script directory to sys.path for importing beo_utils
sys.path.insert(0, str(Path(__file__).parent))
import beo_utils

def main() -> int:
    results = {
      "status": "success",
      "dependencies": {},
      "vault": {},
      "qmd_collection": {},
      "errors": []
    }

    # 1. Check core binaries
    for binary in ["br", "bv", "qmd", "obsidian"]:
        code, out, err = beo_utils.run_cmd([binary, "--version"] if binary != "obsidian" else [binary, "help"])
        if code == -1:
            results["dependencies"][binary] = "missing"
            results["errors"].append(f"{binary} CLI is not installed or not in PATH")
            results["status"] = "failed"
        else:
            if binary == "br":
                results["dependencies"]["br"] = out.split("\n")[0]
            elif binary == "bv":
                results["dependencies"]["bv"] = out.split("\n")[0]
            elif binary == "qmd":
                results["dependencies"]["qmd"] = out.split("\n")[0]
            elif binary == "obsidian":
                results["dependencies"]["obsidian"] = "present"

    # Resolve env variables using beo_utils
    env = beo_utils.resolve_obsidian_env()
    vault_name = env["vault_name"]
    vault_path = env["vault_path"]
    learning_dir = env["learning_dir"]

    # 2. Check Obsidian Vault
    code, out, err = beo_utils.run_cmd(["obsidian", "vaults", "--verbose"])
    if code != 0:
        results["vault"]["status"] = "failed"
        results["errors"].append("Failed to list vaults via obsidian CLI")
    else:
        vaults = out.split("\n")
        if vault_name in vaults:
            results["vault"]["name"] = vault_name
            p_code, p_out, p_err = beo_utils.run_cmd(["obsidian", f"vault={vault_name}", "vault", "info=path"])
            if p_code == 0:
                vault_path = Path(p_out)
                learning_dir = vault_path / "beo-learnings"
        else:
            results["errors"].append(f"Vault '{vault_name}' not found in registered obsidian vaults: {vaults}")

    results["vault"]["path"] = str(vault_path)
    results["vault"]["learning_dir"] = str(learning_dir)
    
    if learning_dir.exists() and learning_dir.is_dir():
        results["vault"]["exists"] = True
    else:
        results["vault"]["exists"] = False
        try:
            learning_dir.mkdir(parents=True, exist_ok=True)
            results["vault"]["created"] = True
            results["vault"]["exists"] = True
        except Exception as e:
            results["errors"].append(f"Failed to create learnings directory: {e}")
            results["status"] = "failed"

    # 3. Check qmd Collection
    if results["dependencies"].get("qmd") != "missing":
        code, out, err = beo_utils.run_cmd(["qmd", "collection", "list"])
        if code == 0:
            if vault_name in out or "beo-skills" in out:
                results["qmd_collection"]["name"] = vault_name
                results["qmd_collection"]["exists"] = True
            else:
                # Add collection automatically
                add_code, add_out, add_err = beo_utils.run_cmd([
                    "qmd", "collection", "add", str(vault_path), "--name", vault_name, "--mask", "**/*.md"
                ])
                if add_code == 0:
                    results["qmd_collection"]["name"] = vault_name
                    results["qmd_collection"]["exists"] = True
                    results["qmd_collection"]["added"] = True
                else:
                    results["errors"].append(f"Failed to add qmd collection for {vault_path}: {add_err}")
                    results["status"] = "failed"
            
            # Check for pending embeddings and automatically run embed if needed
            if results["qmd_collection"].get("exists"):
                s_code, s_out, s_err = beo_utils.run_cmd(["qmd", "status"])
                if s_code == 0:
                    results["qmd_collection"]["status"] = "indexed"
                    import re
                    pending_match = re.search(r"Pending:\s*(\d+)\s+need\s+embedding", s_out)
                    if pending_match:
                        pending_count = int(pending_match.group(1))
                        results["qmd_collection"]["pending_embeddings"] = pending_count
                        if pending_count > 0:
                            emb_code, emb_out, emb_err = beo_utils.run_cmd(["qmd", "embed"])
                            if emb_code == 0:
                                results["qmd_collection"]["embeddings_refreshed"] = True
                                results["qmd_collection"]["pending_embeddings"] = 0
                            else:
                                results["errors"].append(f"Failed to run qmd embed: {emb_err}")
                    else:
                        results["qmd_collection"]["pending_embeddings"] = 0
                else:
                    results["qmd_collection"]["status"] = "error_fetching_status"
        else:
            results["errors"].append("Failed to list qmd collections")
            results["status"] = "failed"

    # Print results in stable JSON format
    print(json.dumps(results, indent=2))
    return 0 if results["status"] == "success" else 1

if __name__ == "__main__":
    sys.exit(main())
