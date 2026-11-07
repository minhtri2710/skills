"""The skill-owned project-state layout: <root>/<slug>/{config.json,gates.md,runs/...}.

Every script that names a file under the root asks this module; STATE_ROOT is read at call time.
"""
from __future__ import annotations

import re
from pathlib import Path

STATE_ROOT = Path.home() / ".agent-delivery" / "projects"

SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,127}$")
SEAT_ROLES = ("lead", "supervisor")
CONFIG = "config.json"
LEDGER = "gates.md"
MAILBOX = "supervisor-mailbox.md"
CONTEXT_PACK = "context-pack.md"
NOTEBOOK = "supervisor-notebook.md"
RUN_RECORDS = {
    "intake": "intake-record.md",
    "plan": "plan.md",
    "specification": "specification.md",
    "slices": "slices.json",
}
RUNS = "runs"
COORDINATION = "coordination"
LESSONS = "lessons"
INDEX = "INDEX.md"


def check_slug(slug: str) -> str:
    if not SLUG_RE.fullmatch(slug):
        raise ValueError(f"{slug!r} is not a project slug")
    return slug


def slug_for(checkout: Path) -> str:
    """The project slug of a checkout: its directory name, lower-cased."""
    return check_slug(checkout.name.lower())


def project_dir(slug: str) -> Path:
    return STATE_ROOT / check_slug(slug)


def config(slug: str) -> Path:
    return project_dir(slug) / CONFIG


def ledger(slug: str) -> Path:
    return project_dir(slug) / LEDGER


def mailbox(slug: str) -> Path:
    return project_dir(slug) / MAILBOX


def context_pack(slug: str) -> Path:
    return project_dir(slug) / CONTEXT_PACK


def notebook(slug: str) -> Path:
    return project_dir(slug) / NOTEBOOK


def seat_record(slug: str, role: str) -> Path:
    """The one-line `<backend> <handle>` record of a seat: `lead-seat` or `supervisor-seat`."""
    if role not in SEAT_ROLES:
        raise ValueError(f"{role!r} is not a seat role: {', '.join(SEAT_ROLES)}")
    return project_dir(slug) / f"{role}-seat"


def runs_dir(slug: str) -> Path:
    return project_dir(slug) / RUNS


def runs_index(slug: str) -> Path:
    return runs_dir(slug) / INDEX


def run_dir(slug: str, run_id: str) -> Path:
    if run_id in ("", ".", "..") or "/" in run_id or "\\" in run_id:
        raise ValueError(f"{run_id!r} is not a run id")
    return runs_dir(slug) / run_id


def coordination_dir(slug: str) -> Path:
    return runs_dir(slug) / COORDINATION


def lessons_dir(slug: str) -> Path:
    return coordination_dir(slug) / LESSONS


def inside_state_root(path: str | Path) -> bool:
    """Whether the path, symlinks resolved, lies strictly below the state root."""
    return STATE_ROOT.resolve() in Path(path).resolve().parents


def _under_root(path: Path) -> tuple[str, ...]:
    try:
        return path.resolve().relative_to(STATE_ROOT.resolve()).parts
    except ValueError:
        return ()


def parse_run_dir(path: Path) -> tuple[str, str]:
    """The (slug, run id) of `<root>/<slug>/runs/<run id>`; ValueError for any other path."""
    parts = _under_root(path)
    if len(parts) != 3 or parts[1] != RUNS or not SLUG_RE.fullmatch(parts[0]):
        raise ValueError(f"{path} is not {STATE_ROOT}/<slug>/{RUNS}/<run>")
    return parts[0], parts[2]


def mailbox_slug(path: str | Path) -> str:
    """The slug of a project mailbox: the path must be `mailbox(slug)` for a valid slug."""
    parts = _under_root(Path(path))
    if len(parts) != 2 or parts[1] != MAILBOX or not SLUG_RE.fullmatch(parts[0]):
        raise ValueError(f"{path} is not {STATE_ROOT}/<slug>/{MAILBOX}")
    return parts[0]
