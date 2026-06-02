#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

scripts_dir = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-reference" / "scripts"
sys.path.insert(0, str(scripts_dir))


class ImportTest(unittest.TestCase):
    def test_imports(self):
        import beo_approval  # noqa: F401
        import beo_git  # noqa: F401
        import beo_io  # noqa: F401
        import beo_memory_tools  # noqa: F401
        import beo_paths  # noqa: F401
        import beo_ticket  # noqa: F401
        import check_skill_bundle  # noqa: F401
        import beo_check_identity  # noqa: F401
        import beo_check_scope  # noqa: F401
        import beo_check_approval  # noqa: F401
        import beo_check_events  # noqa: F401
        import beo_check  # noqa: F401
        import beo_quick_fill  # noqa: F401
        import beo_reservation  # noqa: F401
        import beo_state  # noqa: F401
        import beo_recall  # noqa: F401
        import beo_memory_write  # noqa: F401
        import beo_setup  # noqa: F401


if __name__ == "__main__":
    unittest.main()
