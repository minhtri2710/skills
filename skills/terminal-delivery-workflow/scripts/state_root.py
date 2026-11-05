"""The one skill-owned state root: <root>/<slug>/{config.json,gates.md,runs/...}."""
from pathlib import Path

STATE_ROOT_REL = Path(".terminal-delivery") / "projects"
STATE_ROOT = Path.home() / STATE_ROOT_REL
