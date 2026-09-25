# Configuration Shapes

These are source-grounded shapes for a target repository. They are not a
turnkey catalog and must not be copied until inspection identifies the tools,
languages, paths, and existing configuration. Replace placeholders only with
observed values. A Human must approve every target path before it is written.

## Local pre-commit hook

Merge, rather than replace, the target's existing hooks. Keep the hook local and
make the command's offline behavior explicit:

```yaml
repos:
  - repo: local
    hooks:
      - id: security-check
        name: local security baseline
        entry: python3 scripts/security_check.py
        language: system
        pass_filenames: false
        stages: [pre-commit]
```

`python3` is an example entry, not a repository fact. Use the interpreter
already supported by the target and record `Not-Assessed` when that cannot be
established.

## Tool configuration

The runner accepts JSON with `fail_on`, optional `trip_all_paths`, and a `checks`
array. Each check names a category, executable command, and optional `required`
and `triggers` fields. The command must be an argv array, not a shell string;
`{output}` is replaced with a temporary per-check JSON output path.

```json
{
  "fail_on": ["CRITICAL", "HIGH"],
  "trip_all_paths": [
    ".pre-commit-config.yaml",
    "security/**",
    ".github/workflows/**",
    "Dockerfile*",
    ".dockerignore",
    "scripts/security_check.py"
  ],
  "checks": [
    {
      "name": "gitleaks",
      "category": "secrets",
      "required": true,
      "triggers": {"always": true},
      "command": ["gitleaks", "git", ".", "--redact", "--report-format", "json", "--report-path", "{output}"]
    }
  ]
}
```

Add dependency and static checks only when the repository evidence supports
them. Commands should use local rule files and offline flags such as a scanner's
skip-database-update option. A tool that requires a missing database or
network-accessible ruleset is `Not-Assessed`, not a successful check.

## Reports

The default output paths are `security/security-report.json` and
`security/security-report.md`. They are declared reporting artifacts only. The
runner may create their parent directory and the two report files; it must not
write a backup, configuration, hook, CI workflow, security policy, lockfile, or
any path outside the explicitly selected report outputs and temporary files.

The JSON report has a top-level `summary`, `scope`, `checks`, `findings`, and
`generated_at`. Each check records whether it ran, its scope reason, executable
name, return code, and any tool error; the reviewed configuration remains the
source of the full argv. Missing tools and unusable reports are visible as
`Not-Assessed` findings. Reports must not copy raw tool stdout/stderr because
scanner output may contain sensitive values.

A report can be clean only for the checks that actually ran and produced usable
results. A full report with skipped or unavailable categories remains partial.
