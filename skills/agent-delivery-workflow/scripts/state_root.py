"""The one skill-owned state root: <root>/<slug>/{config.json,gates.md,runs/...}."""
from pathlib import Path

STATE_ROOT = Path.home() / ".agent-delivery" / "projects"
