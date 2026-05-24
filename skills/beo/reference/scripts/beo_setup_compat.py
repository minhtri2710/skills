#!/usr/bin/env python3
"""
BEO Setup Compatibility Checker

Checks availability and configuration of BEO tooling:
- br (required)
- bv (optional, triage/orientation)
- qmd (optional, memory recall)
- obsidian (optional, learning persistence)

Emits structured compatibility report for setup skill.
"""

import json
import os
import shutil
import subprocess
import sys
from typing import Any, Dict, List


def check_br() -> Dict[str, Any]:
    """Check br availability and version."""
    br_path = shutil.which("br")
    if not br_path:
        return {"status": "missing", "reason": "executable not found"}

    try:
        result = subprocess.run(
            ["br", "capabilities", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return {"status": "degraded", "reason": "capabilities check failed"}

        # Try to parse version if available
        caps = json.loads(result.stdout)
        version = caps.get("version", "unknown")
        return {"status": "available", "version": version, "path": br_path}
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return {"status": "degraded", "reason": "version check failed", "path": br_path}


def check_bv() -> Dict[str, Any]:
    """Check bv availability."""
    bv_path = shutil.which("bv")
    if not bv_path:
        return {"status": "missing", "reason": "executable not found"}

    try:
        # Just check if bv exists and is executable
        result = subprocess.run(
            ["bv", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        version = result.stdout.strip() if result.returncode == 0 else "unknown"
        return {"status": "available", "version": version, "path": bv_path}
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"status": "degraded", "reason": "version check failed", "path": bv_path}


def check_qmd() -> Dict[str, Any]:
    """Check qmd availability and collection configuration."""
    qmd_path = shutil.which("qmd")
    if not qmd_path:
        return {"status": "missing", "reason": "executable not found"}

    # Check for collection configuration
    collection = os.environ.get("BEO_QMD_COLLECTION")
    if not collection:
        return {
            "status": "degraded",
            "reason": "BEO_QMD_COLLECTION not configured",
            "path": qmd_path
        }

    try:
        # Check if qmd is functional
        result = subprocess.run(
            ["qmd", "collections"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return {
                "status": "available",
                "collection": collection,
                "path": qmd_path
            }
        else:
            return {
                "status": "degraded",
                "reason": "qmd collections check failed",
                "path": qmd_path
            }
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return {"status": "degraded", "reason": "qmd check failed", "path": qmd_path}


def check_obsidian() -> Dict[str, Any]:
    """Check Obsidian CLI availability and vault configuration."""
    obsidian_path = shutil.which("obsidian")
    if not obsidian_path:
        return {"status": "missing", "reason": "executable not found"}

    # Check for vault configuration
    vault_path = os.environ.get("BEO_OBSIDIAN_VAULT")
    vault_name = os.environ.get("BEO_OBSIDIAN_VAULT_NAME")
    vault_id = os.environ.get("BEO_OBSIDIAN_VAULT_ID")

    if not (vault_path or vault_name or vault_id):
        return {
            "status": "degraded",
            "reason": "vault not configured (BEO_OBSIDIAN_VAULT* vars missing)",
            "path": obsidian_path
        }

    # Check if vault path exists (if specified)
    if vault_path and not os.path.isdir(vault_path):
        return {
            "status": "degraded",
            "reason": f"vault path does not exist: {vault_path}",
            "path": obsidian_path
        }

    return {
        "status": "available",
        "vault_path": vault_path,
        "vault_name": vault_name,
        "vault_id": vault_id,
        "path": obsidian_path
    }


def determine_workflow_readiness(tools: Dict[str, Dict]) -> str:
    """Determine overall workflow readiness state."""
    br_status = tools["br"]["status"]

    if br_status != "available":
        return "blocked"

    # Check if any optional tools are degraded/missing
    optional_degraded = any(
        tools[tool]["status"] in ["missing", "degraded"]
        for tool in ["bv", "qmd", "obsidian"]
    )

    if optional_degraded:
        return "degraded"

    return "ready"


def collect_degraded_capabilities(tools: Dict[str, Dict]) -> List[str]:
    """Collect list of degraded capabilities."""
    degraded = []

    if tools["bv"]["status"] != "available":
        degraded.append("bv_triage")

    if tools["qmd"]["status"] != "available":
        degraded.append("qmd_recall")

    if tools["obsidian"]["status"] != "available":
        degraded.append("obsidian_persistence")

    return degraded


def generate_operator_guidance(readiness: str, degraded: List[str]) -> str:
    """Generate human-readable operator guidance."""
    if readiness == "blocked":
        return "BEO workflow is blocked. br (Beads CLI) is required but not available. Install br >= 0.1.28 before proceeding."

    if readiness == "degraded":
        capabilities_str = ", ".join(degraded)
        return f"BEO workflow is ready. {capabilities_str} degraded but not required. Core delivery workflow remains fully functional."

    return "BEO workflow is ready. All tools available and configured."


def main():
    """Run compatibility check and emit structured report."""
    tools = {
        "br": check_br(),
        "bv": check_bv(),
        "qmd": check_qmd(),
        "obsidian": check_obsidian()
    }

    readiness = determine_workflow_readiness(tools)
    degraded_caps = collect_degraded_capabilities(tools)
    guidance = generate_operator_guidance(readiness, degraded_caps)

    report = {
        "tools": tools,
        "workflow_readiness": readiness,
        "degraded_capabilities": degraded_caps,
        "operator_guidance": guidance
    }

    # Emit JSON report
    print(json.dumps(report, indent=2))

    # Exit with appropriate code
    if readiness == "blocked":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
