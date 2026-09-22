#!/usr/bin/env python3
"""Run configured local security checks and write bounded reports.

The runner uses only the Python standard library. It invokes configured tools
without a shell, never installs or updates anything, and writes only the two
explicit report paths plus per-check temporary output files. A configured tool
may have behavior outside this runner's control, so review commands before
approving a target configuration.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

SEVERITIES = ("CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO")
DEFAULT_TIMEOUT_SECONDS = 120
DEFAULT_TRIP_ALL_PATHS = (
    ".pre-commit-config.yaml",
    "security/**",
    ".github/workflows/**",
    "Dockerfile",
    "Dockerfile.*",
    "**/Dockerfile",
    "**/Dockerfile.*",
    ".dockerignore",
    "scripts/security_check.py",
)
DEFAULT_TRIGGERS = {
    "gitleaks": {"always": True},
    "trivy": {
        "paths": [
            "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
            "Cargo.lock", "Cargo.toml", "go.mod", "go.sum",
            "requirements*.txt", "Pipfile", "Pipfile.lock", "pyproject.toml",
            "poetry.lock", "composer.json", "composer.lock", "Gemfile",
            "Gemfile.lock", "pom.xml", "build.gradle", "build.gradle.kts",
            "**/package.json", "**/package-lock.json", "**/pnpm-lock.yaml",
            "**/yarn.lock", "**/Cargo.lock", "**/Cargo.toml", "**/go.mod",
            "**/go.sum", "**/requirements*.txt", "**/Pipfile",
            "**/Pipfile.lock", "**/pyproject.toml", "**/poetry.lock",
            "**/composer.json", "**/composer.lock", "**/Gemfile",
            "**/Gemfile.lock", "**/pom.xml", "**/build.gradle",
            "**/build.gradle.kts",
        ],
    },
    "semgrep": {
        "paths": [
            "**/*.py", "**/*.js", "**/*.jsx", "**/*.ts", "**/*.tsx",
            "**/*.mjs", "**/*.cjs", "**/*.go", "**/*.rb", "**/*.php",
            "**/*.java", "**/*.kt", "**/*.kts", "**/*.scala", "**/*.cs",
            "**/*.c", "**/*.h", "**/*.cc", "**/*.cpp", "**/*.hpp",
            "**/*.rs", "**/*.swift", "**/*.sh", "**/*.bash", "**/*.zsh",
            "**/*.yaml", "**/*.yml", "**/Dockerfile", "**/Dockerfile.*",
        ],
    },
    "bandit": {"paths": ["**/*.py"]},
    "cargo-audit": {"paths": ["Cargo.lock", "Cargo.toml", "**/Cargo.lock", "**/Cargo.toml"]},
}
DEFAULT_CONFIG = {
    "fail_on": ["CRITICAL", "HIGH"],
    "checks": [
        {
            "name": "gitleaks",
            "category": "secrets",
            "required": True,
            "command": [
                "gitleaks", "detect", "--source", ".", "--redact",
                "--report-format", "json", "--report-path", "{output}",
            ],
        },
        {
            "name": "trivy",
            "category": "dependencies",
            "required": True,
            "command": [
                "trivy", "fs", "--scanners", "vuln", "--skip-db-update",
                "--format", "json", "--exit-code", "0", ".",
            ],
        },
        {
            "name": "semgrep",
            "category": "static",
            "required": True,
            "command": [
                "semgrep", "--config", "security/semgrep-rules.yml",
                "--json", "--error", ".",
            ],
        },
    ],
}
EXPECTED_RETURNCODES = {
    "gitleaks": (0, 1),
    "trivy": (0, 1),
    "semgrep": (0, 1),
    "bandit": (0, 1),
    "cargo-audit": (0, 1),
}


class ConfigurationError(Exception):
    """Raised when the selected runner configuration cannot be used."""


class JsonOutputError(Exception):
    """Raised when a selected check does not produce usable JSON."""


def normalize_severity(value: Any) -> str:
    if value is None:
        return "INFO"
    text = str(value).upper()
    if text == "ERROR":
        return "HIGH"
    if text == "WARNING":
        return "MEDIUM"
    return text if text in SEVERITIES else "INFO"


def load_config(path: Optional[Path]) -> Dict[str, Any]:
    if path is None:
        path = Path("security/security-tools.json")
        if not path.exists():
            validate_config(DEFAULT_CONFIG)
            return DEFAULT_CONFIG
    elif not path.exists():
        raise ConfigurationError("configuration file not found: " + str(path))
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigurationError("could not read valid JSON configuration") from exc
    validate_config(value)
    return value


def validate_config(config: Any) -> None:
    if not isinstance(config, dict):
        raise ConfigurationError("configuration must be a JSON object")
    fail_on = config.get("fail_on", ["CRITICAL", "HIGH"])
    if (
        not isinstance(fail_on, list)
        or not fail_on
        or any(not isinstance(item, str) or item.upper() not in SEVERITIES for item in fail_on)
    ):
        raise ConfigurationError("fail_on must be a non-empty list of known severities")
    checks = config.get("checks")
    if not isinstance(checks, list) or not checks:
        raise ConfigurationError("checks must be a non-empty list")
    names = set()
    for check in checks:
        if not isinstance(check, dict):
            raise ConfigurationError("each check must be an object")
        name = check.get("name")
        command = check.get("command")
        if not isinstance(name, str) or not name or name in {".", ".."} or Path(name).name != name:
            raise ConfigurationError("each check needs a unique path-safe name")
        if name in names:
            raise ConfigurationError("check names must be unique")
        names.add(name)
        if not isinstance(command, list) or not command or any(not isinstance(part, str) for part in command):
            raise ConfigurationError("each check command must be a non-empty argv list")
        if "triggers" in check and not isinstance(check["triggers"], dict):
            raise ConfigurationError("check triggers must be an object")
        if check.get("category") == "secrets" and "triggers" in check and not check["triggers"].get("always"):
            raise ConfigurationError("secret checks must be always-on")
        if "timeout_seconds" in check:
            try:
                timeout = int(check["timeout_seconds"])
            except (TypeError, ValueError) as exc:
                raise ConfigurationError("timeout_seconds must be an integer") from exc
            if timeout <= 0:
                raise ConfigurationError("timeout_seconds must be positive")


def command_exists(command: Sequence[str]) -> bool:
    return bool(command and shutil.which(command[0]))


def materialize_command(command: Sequence[str], output: Path) -> List[str]:
    return [part.replace("{output}", str(output)) for part in command]


def staged_files() -> Optional[List[str]]:
    if not shutil.which("git"):
        return None
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z"],
            capture_output=True,
            check=False,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    return [item for item in result.stdout.decode(errors="replace").split("\0") if item]


def matches_any(path: str, patterns: Sequence[str]) -> bool:
    for pattern in patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
        if pattern.startswith("**/") and fnmatch.fnmatch(path, pattern[3:]):
            return True
    return False


def evaluate_scope(
    config: Dict[str, Any], files: Optional[List[str]]
) -> Tuple[List[str], Dict[str, Dict[str, Any]]]:
    decisions: Dict[str, Dict[str, Any]] = {}
    full_scan = files is None or not files
    trip_paths = config.get("trip_all_paths", list(DEFAULT_TRIP_ALL_PATHS))
    if not isinstance(trip_paths, list) or any(not isinstance(item, str) for item in trip_paths):
        raise ConfigurationError("trip_all_paths must be a list of globs")
    tripped = [] if full_scan else [item for item in files or [] if matches_any(item, trip_paths)]

    for check in config["checks"]:
        name = check["name"]
        triggers = check.get("triggers", DEFAULT_TRIGGERS.get(name, {"always": True}))
        if not isinstance(triggers, dict):
            raise ConfigurationError("check triggers must be an object")
        if full_scan:
            decisions[name] = {
                "run": True,
                "reason": "full scan (--all or no staged files)",
                "matched_paths": [],
            }
        elif triggers.get("always"):
            decisions[name] = {
                "run": True,
                "reason": "always-on check",
                "matched_paths": list(files or []),
            }
        elif tripped:
            decisions[name] = {
                "run": True,
                "reason": "trip-all path staged: " + tripped[0],
                "matched_paths": tripped,
            }
        else:
            patterns = triggers.get("paths", [])
            if not isinstance(patterns, list) or any(not isinstance(item, str) for item in patterns):
                raise ConfigurationError("check trigger paths must be a list of globs")
            matched = [item for item in files or [] if matches_any(item, patterns)]
            decisions[name] = {
                "run": bool(matched),
                "reason": (
                    "matched staged file(s): " + ", ".join(matched[:5])
                    if matched else "no staged file matches this check's triggers"
                ),
                "matched_paths": matched,
            }
    return list(files or []), decisions


def make_finding(
    category: str,
    severity: Any,
    tool: str,
    title: str,
    path: str = "",
    hint: str = "",
    assessment: str = "Assessed",
) -> Dict[str, str]:
    return {
        "assessment": assessment,
        "category": category,
        "severity": normalize_severity(severity),
        "tool": tool,
        "title": title,
        "path": path,
        "hint": hint,
    }


def parse_gitleaks(raw: Any, category: str, tool: str) -> List[Dict[str, str]]:
    items = raw if isinstance(raw, list) else []
    return [
        make_finding(
            category, "HIGH", tool,
            item.get("Description") or item.get("RuleID") or "Potential secret",
            item.get("File") or "",
            "Rotate the exposed credential and remove it from history if committed.",
        )
        for item in items if isinstance(item, dict)
    ]


def parse_trivy(raw: Any, category: str, tool: str) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    results = raw.get("Results", []) if isinstance(raw, dict) else []
    for result in results or []:
        if not isinstance(result, dict):
            continue
        target = result.get("Target", "")
        for vuln in result.get("Vulnerabilities", []) or []:
            if not isinstance(vuln, dict):
                continue
            fixed = vuln.get("FixedVersion")
            findings.append(make_finding(
                category,
                vuln.get("Severity", "INFO"),
                tool,
                "%s in %s" % (vuln.get("VulnerabilityID", "Vulnerability"), vuln.get("PkgName", "package")),
                target,
                "Upgrade to %s." % fixed if fixed else "Review the advisory and upgrade or apply its workaround.",
            ))
    return findings


def parse_semgrep(raw: Any, category: str, tool: str) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    for item in raw.get("results", []) if isinstance(raw, dict) else []:
        if not isinstance(item, dict):
            continue
        extra = item.get("extra", {})
        if not isinstance(extra, dict):
            extra = {}
        findings.append(make_finding(
            category,
            extra.get("severity", "INFO"),
            tool,
            extra.get("message") or item.get("check_id", "Static-analysis finding"),
            item.get("path", ""),
            "Review the matching code and apply the rule guidance.",
        ))
    return findings


def parse_bandit(raw: Any, category: str, tool: str) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    for item in raw.get("results", []) if isinstance(raw, dict) else []:
        if not isinstance(item, dict):
            continue
        findings.append(make_finding(
            category,
            item.get("issue_severity", "INFO"),
            tool,
            item.get("issue_text") or item.get("test_id") or "Bandit finding",
            item.get("filename", ""),
            "Follow the scanner's remediation guidance.",
        ))
    return findings


def parse_cargo_audit(raw: Any, category: str, tool: str) -> List[Dict[str, str]]:
    findings: List[Dict[str, str]] = []
    vulnerabilities = raw.get("vulnerabilities", {}) if isinstance(raw, dict) else {}
    for item in vulnerabilities.get("list", []) if isinstance(vulnerabilities, dict) else []:
        if not isinstance(item, dict):
            continue
        advisory = item.get("advisory", {})
        package = item.get("package", {})
        if not isinstance(advisory, dict) or not isinstance(package, dict):
            continue
        findings.append(make_finding(
            category,
            advisory.get("severity", "HIGH"),
            tool,
            "%s in %s" % (advisory.get("id", "Advisory"), package.get("name", "crate")),
            "Cargo.lock",
            "Update the affected crate or apply the advisory workaround.",
        ))
    return findings


PARSERS = {
    "gitleaks": parse_gitleaks,
    "trivy": parse_trivy,
    "semgrep": parse_semgrep,
    "bandit": parse_bandit,
    "cargo-audit": parse_cargo_audit,
}


def read_json_output(output_path: Path, stdout: bytes) -> Any:
    try:
        if output_path.exists():
            text = output_path.read_text(encoding="utf-8")
            if text.strip():
                return json.loads(text)
        text = stdout.decode(errors="replace")
        if text.strip().startswith(("{", "[")):
            return json.loads(text)
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise JsonOutputError("scanner output was not valid JSON") from exc
    raise JsonOutputError("scanner produced no JSON report")


def unavailable_result(check: Dict[str, Any], decision: Dict[str, Any], title: str) -> Dict[str, Any]:
    required = bool(check.get("required", False))
    result: Dict[str, Any] = {
        "name": check["name"],
        "category": check.get("category", "other"),
        "required": required,
        "status": "Not-Assessed",
        "skipped": False,
        "scope_reason": decision["reason"],
        "matched_paths": decision.get("matched_paths", []),
        "returncode": None,
        "tool_error": title,
        "findings": [make_finding(
            "tool-errors", "INFO", check["name"], title, "",
            "Provide the missing executable or record the operator prerequisite.",
            "Not-Assessed",
        )],
    }
    result["required_failure"] = required
    return result


def run_check(check: Dict[str, Any], tempdir: Path, decision: Dict[str, Any]) -> Dict[str, Any]:
    base: Dict[str, Any] = {
        "name": check["name"],
        "category": check.get("category", "other"),
        "required": bool(check.get("required", False)),
        "status": "Skipped" if not decision["run"] else "Pending",
        "skipped": not decision["run"],
        "scope_reason": decision["reason"],
        "matched_paths": decision.get("matched_paths", []),
        "returncode": None,
        "findings": [],
    }
    if not decision["run"]:
        return base

    command = materialize_command(check["command"], tempdir / (check["name"] + ".json"))
    base["command_name"] = command[0]
    if not command_exists(command):
        return unavailable_result(check, decision, "missing executable: " + command[0])

    timeout = int(check.get("timeout_seconds", DEFAULT_TIMEOUT_SECONDS))
    try:
        proc = subprocess.run(
            command,
            capture_output=True,
            check=False,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        base.update({
            "status": "Not-Assessed",
            "tool_error": "scanner timed out after %ss" % timeout,
            "operational_error": True,
            "findings": [make_finding(
                "tool-errors", "INFO", check["name"],
                "scanner timed out after %ss" % timeout, "",
                "Reduce scope or resolve the scanner timeout before claiming coverage.",
                "Not-Assessed",
            )],
        })
        base["required_failure"] = bool(check.get("required", False))
        return base
    except OSError:
        base.update({
            "status": "Not-Assessed",
            "tool_error": "scanner could not be started",
            "operational_error": True,
            "findings": [make_finding(
                "tool-errors", "INFO", check["name"], "scanner could not be started", "",
                "Check the local executable and operator prerequisites.", "Not-Assessed",
            )],
        })
        base["required_failure"] = bool(check.get("required", False))
        return base

    base["returncode"] = proc.returncode
    output_path = tempdir / (check["name"] + ".json")
    try:
        raw = read_json_output(output_path, proc.stdout)
    except JsonOutputError as exc:
        base.update({
            "status": "Not-Assessed",
            "tool_error": str(exc),
            "operational_error": True,
            "findings": [make_finding(
                "tool-errors", "INFO", check["name"], str(exc), "",
                "Make the configured scanner produce usable JSON before claiming coverage.",
                "Not-Assessed",
            )],
        })
        base["required_failure"] = bool(check.get("required", False))
        return base

    parser = PARSERS.get(check["name"])
    if parser is None:
        base.update({
            "status": "Not-Assessed",
            "tool_error": "no parser registered for scanner output",
            "operational_error": True,
            "findings": [make_finding(
                "tool-errors", "INFO", check["name"],
                "no parser registered for scanner output", "",
                "Use a supported scanner name or add a reviewed parser.", "Not-Assessed",
            )],
        })
        base["required_failure"] = bool(check.get("required", False))
        return base

    expected = check.get("expected_returncodes", EXPECTED_RETURNCODES.get(check["name"], (0, 1)))
    if not isinstance(expected, (list, tuple)) or any(not isinstance(item, int) for item in expected):
        raise ConfigurationError("expected_returncodes must be a list of integers")
    findings = parser(raw, check.get("category", "other"), check["name"])
    base["status"] = "Assessed"
    base["findings"] = findings
    if proc.returncode not in tuple(expected):
        base["status"] = "Not-Assessed"
        base["tool_error"] = "scanner exited with unexpected code %s" % proc.returncode
        base["operational_error"] = True
        base["findings"].append(make_finding(
            "tool-errors", "INFO", check["name"],
            "scanner exited with unexpected code %s" % proc.returncode, "",
            "Resolve the scanner failure before claiming coverage.", "Not-Assessed",
        ))
        base["required_failure"] = bool(check.get("required", False))
    return base


def summarize(results: List[Dict[str, Any]]) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
    findings = [item for result in results for item in result.get("findings", [])]
    severity_counts = Counter(item["severity"] for item in findings)
    category_counts = Counter(item["category"] for item in findings)
    return findings, {
        "checks_run": sum(1 for result in results if not result.get("skipped")),
        "checks_skipped": sum(1 for result in results if result.get("skipped")),
        "checks_configured": len(results),
        "checks_assessed": sum(1 for result in results if result.get("status") == "Assessed"),
        "not_assessed": sum(1 for result in results if result.get("status") == "Not-Assessed"),
        "finding_count": len(findings),
        "severity_counts": dict(severity_counts),
        "category_counts": dict(category_counts),
    }


def should_fail(findings: List[Dict[str, str]], fail_on: Sequence[str]) -> bool:
    levels = {item.upper() for item in fail_on}
    return any(item.get("assessment") == "Assessed" and item["severity"] in levels for item in findings)


def confirm_force() -> bool:
    if not sys.stdin.isatty():
        print("Refusing --force in a non-interactive context; run from a terminal and type YES.", file=sys.stderr)
        return False
    try:
        answer = input("Type YES to override blocking findings: ")
    except EOFError:
        print("No confirmation received; bypass denied.", file=sys.stderr)
        return False
    return answer == "YES"


def format_counter(counter: Dict[str, int]) -> str:
    if not counter:
        return "none"
    ordered = ["%s=%s" % (level, counter[level]) for level in SEVERITIES if level in counter]
    return ", ".join(ordered)


def format_categories(counter: Dict[str, int]) -> str:
    if not counter:
        return "none"
    return ", ".join("%s=%s" % (name, counter[name]) for name in sorted(counter))


def render_markdown(payload: Dict[str, Any]) -> str:
    summary = payload["summary"]
    scope = payload["scope"]
    bypass = payload["bypass"]
    lines = [
        "# Security Check Report", "", "Generated: " + payload["generated_at"], "",
        "## Summary", "",
        "- Mode: " + scope["mode"],
        "- Staged files considered: %s" % len(scope.get("files", [])),
        "- Checks run: %s of %s (skipped: %s)" % (
            summary["checks_run"], summary["checks_configured"], summary["checks_skipped"]),
        "- Checks assessed: %s" % summary["checks_assessed"],
        "- Not-Assessed checks: %s" % summary["not_assessed"],
        "- Findings: %s" % summary["finding_count"],
        "- Severity: " + format_counter(summary["severity_counts"]),
        "- Categories: " + format_categories(summary["category_counts"]),
        "- Bypass: " + bypass["status"], "", "## Scope Decisions", "",
    ]
    for check in payload["checks"]:
        lines.append("- **%s**: %s — %s" % (
            check["name"], check["status"], check.get("scope_reason", "")))
    lines.extend(["", "## Findings", ""])
    if not payload["findings"]:
        lines.append("No findings.")
    for item in payload["findings"]:
        path = " (%s)" % item["path"] if item.get("path") else ""
        lines.append("- **%s** [%s/%s, %s] %s%s" % (
            item["severity"], item["category"], item["tool"],
            item["assessment"], item["title"], path))
        if item.get("hint"):
            lines.append("  - Hint: " + item["hint"])
    lines.append("")
    return "\n".join(lines)


def write_reports(json_path: Path, markdown_path: Path, payload: Dict[str, Any]) -> None:
    if json_path.resolve() == markdown_path.resolve():
        raise ConfigurationError("JSON and Markdown report paths must differ")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path.write_text(render_markdown(payload), encoding="utf-8")


def print_summary(payload: Dict[str, Any], json_path: Path, markdown_path: Path) -> None:
    summary = payload["summary"]
    print("Security Check Summary")
    print("======================")
    print("Mode: " + payload["scope"]["mode"])
    if payload["scope"]["mode"] == "staged":
        print("Staged files: %s" % len(payload["scope"]["files"]))
    print("Checks run: %s of %s (skipped: %s)" % (
        summary["checks_run"], summary["checks_configured"], summary["checks_skipped"]))
    print("Checks assessed: %s; Not-Assessed: %s" % (
        summary["checks_assessed"], summary["not_assessed"]))
    print("Findings: %s" % summary["finding_count"])
    print("Severity: " + format_counter(summary["severity_counts"]))
    print("Categories: " + format_categories(summary["category_counts"]))
    print("Bypass: " + payload["bypass"]["status"])
    print("JSON report: " + str(json_path))
    print("Markdown report: " + str(markdown_path))
    if payload["findings"]:
        print("\nTop findings:")
        for item in payload["findings"][:10]:
            path = " (%s)" % item["path"] if item.get("path") else ""
            print("- %s [%s/%s, %s] %s%s" % (
                item["severity"], item["category"], item["tool"],
                item["assessment"], item["title"], path))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run configured local security checks and write reports.")
    parser.add_argument("--config", default=None, help="JSON tool configuration path")
    parser.add_argument("--output", default="security/security-report.json", help="JSON report path")
    parser.add_argument("--markdown", default="security/security-report.md", help="Markdown report path")
    parser.add_argument("--force", action="store_true", help="Request an interactive YES bypass for blocking findings")
    parser.add_argument(
        "--allow-missing-tools", action="store_true",
        help="Permit exit 0 for missing executables, while keeping the report partial and Not-Assessed",
    )
    scope = parser.add_mutually_exclusive_group()
    scope.add_argument("--all", dest="all_files", action="store_true", help="Run every configured check")
    scope.add_argument("--staged-only", action="store_true", help="Require staged files and use staged-file scope")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    json_path = Path(args.output)
    markdown_path = Path(args.markdown)
    try:
        config = load_config(Path(args.config) if args.config is not None else None)
        if args.all_files:
            files = None
            mode = "full"
        elif args.staged_only:
            files = staged_files()
            if not files:
                print("--staged-only requires a Git repository with staged files.", file=sys.stderr)
                return 2
            mode = "staged"
        else:
            files = staged_files()
            mode = "staged" if files else "full"
        _, decisions = evaluate_scope(config, files if mode == "staged" else None)
        with tempfile.TemporaryDirectory(prefix="security-check-") as temp:
            results = [
                run_check(check, Path(temp), decisions[check["name"]])
                for check in config["checks"]
            ]
    except ConfigurationError as exc:
        print("Configuration error: " + str(exc), file=sys.stderr)
        return 2

    findings, summary = summarize(results)
    blocking = should_fail(findings, config.get("fail_on", ["CRITICAL", "HIGH"]))
    missing_tools = [
        result for result in results
        if result.get("status") == "Not-Assessed"
        and result.get("tool_error", "").startswith("missing executable:")
    ]
    required_failure = any(result.get("required_failure") for result in results)
    operational_failure = any(result.get("operational_error") for result in results)
    bypass = {"requested": bool(args.force), "accepted": False, "status": "not-requested"}
    if args.force and blocking:
        bypass["accepted"] = confirm_force()
        bypass["status"] = "BYPASSED" if bypass["accepted"] else "denied"
    elif args.force and (required_failure or operational_failure):
        bypass["status"] = "not-allowed-for-prerequisite-gap"
    elif args.force:
        bypass["status"] = "not-needed"

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": {"mode": mode, "files": files if mode == "staged" else []},
        "summary": summary,
        "bypass": bypass,
        "findings": findings,
        "checks": results,
    }
    try:
        write_reports(json_path, markdown_path, payload)
    except (ConfigurationError, OSError) as exc:
        print("Report error: " + str(exc), file=sys.stderr)
        return 2
    print_summary(payload, json_path, markdown_path)

    if required_failure or operational_failure:
        if args.allow_missing_tools and missing_tools and not operational_failure and not blocking:
            print("Required executables are missing; report is partial and Not-Assessed.", file=sys.stderr)
            return 0
        print("Security assessment incomplete; resolve Not-Assessed prerequisites.", file=sys.stderr)
        return 2
    if blocking and not bypass["accepted"]:
        print("Security checks failed. Fix findings or rerun with --force and type YES.", file=sys.stderr)
        return 1
    if blocking and bypass["accepted"]:
        print("Blocking findings bypassed by explicit YES; report remains non-clean.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
