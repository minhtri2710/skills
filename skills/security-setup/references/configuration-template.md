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

The runner accepts JSON; its fields, and each check's, are validated in
`validate_config` and read in `run_check`, both in `scripts/security_check.py`.
The command must be an argv array, not a shell string; `{output}` is replaced
with a temporary per-check JSON output path. An optional `staged_command`
(same shape) replaces `command` in staged mode. The runner uses
`security/security-tools.json` from the working directory; without it, it uses
`DEFAULT_CONFIG`, unless the repository root holds that file, in which case it
exits 2 until run from the root or given `--config`. Every report names the
configuration in use. Omitted fields take the script's
values: `fail_on` (default `CRITICAL`, `HIGH`, and `UNKNOWN`, Trivy's level for an
unscored advisory; drop `UNKNOWN` from it to stop those blocking), `trip_all_paths` (`DEFAULT_TRIP_ALL_PATHS`), and the
per-scanner triggers are defined in `scripts/security_check.py`, as is the
built-in `DEFAULT_CONFIG` used when no configuration file exists. Read them
there and set a field only to differ.

```json
{
  "checks": [
    {
      "name": "gitleaks",
      "category": "secrets",
      "required": true,
      "triggers": {"always": true},
      "command": ["gitleaks", "<observed offline subcommand and flags>", "--report-path", "{output}"],
      "staged_command": ["gitleaks", "<observed offline flags that scan the staged blobs>", "--report-path", "{output}"]
    }
  ]
}
```

Add dependency and static checks only when the repository evidence supports
them. Commands should use local rule files and offline flags such as a scanner's
skip-database-update option. A tool that requires a missing database or
network-accessible ruleset is `Not-Assessed`, not a successful check.

## Reports

The default output paths are the `--output` and `--markdown` defaults in
`scripts/security_check.py`. They are declared reporting artifacts only. The
runner may create their parent directory and the two report files; it must not
write a backup, configuration, hook, CI workflow, security policy, lockfile, or
any path outside the explicitly selected report outputs and temporary files.

The JSON report's top-level keys are those of the payload `main` writes in
`scripts/security_check.py`. Each check records whether it ran, its scope
reason, executable name, return code, and any tool error; the reviewed
configuration remains the source of the full argv. Missing tools and unusable
reports are visible as `Not-Assessed` findings. Reports must not copy raw tool
stdout/stderr because scanner output may contain sensitive values.

A report can be clean only for the checks that actually ran and produced usable
results. A full report with skipped or unavailable categories remains partial.
