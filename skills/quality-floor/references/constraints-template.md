# CONSTRAINTS.md template

Copy the block below to the repository root and fill it from the detected stack and
the user's answers. `floor_guard.py` reads this shape: bounds written as `>=` or
`<=` inside table rows keyed by their first cell, floor rules as `- ` bullets, and
exception ids as `E<n>`.

```markdown
# Constraints

## Floor

- No new suppression comments (`@ts-ignore`, `eslint-disable`, `# noqa`, `# type: ignore`)
- No stubs, empty `catch`, `TODO`, or `FIXME` in place of an implementation
- No skipped, focused, or deleted tests, and no assertions removed from kept tests
- No secrets in source
- This file changes only in a commit of its own

## Enforced with numbers

| Dimension | Rule | Checked by | Runs at | Reason |
| --- | --- | --- | --- | --- |
| Types | errors <= 0 | `tsc --noEmit` | edit | type errors are defects |
| Lint | errors <= 0 | `biome check` | edit | the project config is the style contract |
| Secrets | findings <= 0 | `gitleaks git --redact --no-banner` | edit | a committed secret is a breach |
| Coverage | changed lines >= 80% | lcov report intersected with `git diff` | task end | forces a test, allows a config line |
| Dependencies | high findings <= 0 | `osv-scanner scan source -r .` | CI | below high is mostly noise |
| Accessibility | critical+serious <= 0 | `axe $URL --tags wcag2a,wcag2aa,wcag21aa` | preview | moderate and minor are often debatable |
| LCP | <= 2500 ms | `lighthouse $URL --output=json` | preview | Core Web Vitals good threshold |
| CLS | <= 0.1 | `lighthouse $URL --output=json` | preview | same |

## Measured and held

| Metric | Bound | Measured by | Reason |
| --- | --- | --- | --- |
| Project coverage | >= 62.4% | lcov total | today's value; must not fall |
| Main bundle | <= 184 kB | `size-limit --json` | today's value; must not grow |

## Exceptions

| ID | Rule | Path | Reason | Removal condition |
| --- | --- | --- | --- | --- |
```

Update a held bound when the metric improves. A drop against it is the finding, not
a reason to lower it.

## Tools by dimension

| Dimension | Tool | Run | Gate on |
| --- | --- | --- | --- |
| Types (TS) | tsc | `tsc --noEmit` | any error |
| Types (Python) | mypy or pyright | `mypy .` | any error |
| Lint | the existing config | `eslint .`, `biome check`, `ruff check` | any error |
| Coverage (JS) | the test runner | `vitest run --coverage` | changed-line coverage |
| Coverage (Python) | pytest-cov | `pytest --cov --cov-report=lcov` | changed-line coverage |
| Code security | Semgrep | `semgrep scan --config p/default` on changed paths | high findings |
| Secrets | gitleaks | `gitleaks git --redact --no-banner` | any finding |
| Dependencies | osv-scanner | `osv-scanner scan source -r .` | high and above |
| Page performance | Lighthouse | `lighthouse $URL --output=json --quiet` | LCP, CLS, score |
| Bundle size | size-limit | `size-limit --json` | per-entry budget |
| Accessibility | axe-core CLI | `axe $URL --tags wcag2a,wcag2aa,wcag21aa` | critical or serious |
| Architecture | dependency-cruiser | `depcruise --validate src` | any violation |
| Assertion quality | Stryker | `stryker run --mutate <changed files>` | mutation score |
