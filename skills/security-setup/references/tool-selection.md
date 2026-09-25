# Tool Selection and Offline Boundary

Use this reference only after inspecting the target repository. The table is a
selection aid, not a claim that any tool is installed or that its database is
current. Record unavailable tools, rules, databases, and platform support as
`Not-Assessed` or as an operator prerequisite.

## Evidence matrix

| Repository evidence | Secrets | Dependencies | Static analysis |
|---|---|---|---|
| Any Git repository | An available local secret scanner | Only when a matching manifest/lockfile is present and local advisory data is available | A local ruleset for languages actually present |
| Python manifest or lockfile | Existing local `detect-secrets`, otherwise an available secret scanner | A local filesystem scanner, if its database is present | `bandit` only when available; local rules for observed Python |
| JavaScript lockfile | An available local secret scanner | A local filesystem scanner with its database present | Local rules for observed JavaScript/TypeScript |
| `Cargo.lock` | An available local secret scanner | `cargo-audit` or a local filesystem scanner, only when available and current enough for the task | Existing Cargo linting plus local rules where evidenced |
| `go.mod`/`go.sum` | An available local secret scanner | A local filesystem scanner with its database present | Local rules for observed Go |

Prefer one tool that covers the evidenced category over several overlapping
scanners. Do not add a dependency or install a tool just because this matrix
mentions it. The dependency-intake-audit skill owns the decision and lifecycle
controls for adding packages.

## Offline runtime rules

- Hook-time commands must not download scanner databases, fetch hosted rules,
  call a cloud API, or require credentials.
- Dependency databases must be warmed by an authorized operator before the
  offline check is claimed as assessed. Warming is an operator action, not part
  of `scripts/security_check.py`.
- Static rules must be local files. A command that resolves a remote ruleset at
  runtime is not an offline check.
- The runner executes configured commands without a shell and never installs,
  updates, commits, pushes, deploys, edits CI, or writes credentials. The
  configured command still needs review: this runner cannot sandbox a tool that
  itself performs network or outward actions.
- If offline operation cannot be established, leave that category
  `Not-Assessed`; do not replace it with a green result.

## Scope rules

The runner's staged mode decides whether a configured check is relevant from
staged POSIX paths. The command itself remains the source of truth for what it
scans, so the report must retain both the scope decision and the configured
command target. In particular, a command such as `gitleaks git .`
scans the repository's commit history, not the staged blobs or the working
tree.

- Secret detection uses `always: true` and is never restricted to source or
  lockfile extensions.
- Dependency checks trigger on observed manifests and lockfiles.
- Static checks trigger on extensions for languages represented in the repo.
- Changes to hook/configuration/security/workflow/Dockerfile paths can use the
  `trip_all_paths` rule to force all applicable checks.
- `--all` runs every configured check. `--staged-only` requires at least one
  staged file. With no staged files, the default runner performs a full scan.

## Availability record

For every selected check record:

1. executable and version evidence, if the operator supplied it;
2. local rule/database evidence;
3. the exact offline command and its exit semantics;
4. the paths and category it covers; and
5. the result, including `Not-Assessed` and the prerequisite needed to close it.

Do not invent versions, language support, advisory freshness, or a successful
scan for a target that was not inspected.
