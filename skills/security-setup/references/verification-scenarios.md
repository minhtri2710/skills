# Verification Scenarios

Use only safe local fixtures and synthetic values. Do not install scanners,
fetch advisory databases, contact external services, or stage unrelated files.
Restore any temporary fixture after the check.

1. **CLI boundary:** `--help` exits 0; an unknown option exits non-zero;
   `--all --staged-only` is rejected; `--staged-only` with no staged file is
   rejected.
2. **Missing executable:** point a temporary config at a nonexistent required
   executable. The report records `Not-Assessed` and the default run exits
   non-zero. The same run with `--allow-missing-tools` is explicitly partial,
   records the same gap, and does not claim coverage.
3. **Always-on secret scope:** with a staged synthetic secret-like fixture in a
   documentation path, the secret check is selected even though dependency and
   language checks are skipped. Do not use a real credential.
4. **Path-triggered checks:** a staged lockfile selects dependency scanning; a
   staged source file selects matching static analysis; a staged workflow or
   security configuration path trips the repository-wide rule.
5. **Malformed output and timeout:** configure a local fixture command that emits
   invalid JSON or exceeds its bounded timeout. The report records a tool error
   and the run does not become green.
6. **Bypass boundary:** run `--force` non-interactively and confirm refusal. In a
   safe fixture, interactive literal `YES` changes only the reported exit result
   to `BYPASSED`; it does not run Git, install anything, or push anything.
7. **Report containment:** select temporary report paths and verify only those
   declared paths are created; inspect the JSON for a `summary` and explicit
   scope/tool status without including raw scanner output.
8. **Full scan:** `--all` runs every configured check regardless of staged-file
   paths; unavailable tools remain visible as `Not-Assessed`.
