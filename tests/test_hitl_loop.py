from __future__ import annotations

import os
import pty
import select
import subprocess
import time
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "bug-diagnosis" / "scripts" / "hitl-loop.sh"


class HitlLoopTest(unittest.TestCase):
    def test_non_tty_stdin_is_refused(self) -> None:
        result = subprocess.run(
            [str(SCRIPT)], input="", capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("hitl-loop: needs an interactive terminal", result.stderr)

    def test_capture_keeps_multiline_answer_on_one_output_line(self) -> None:
        master, slave = pty.openpty()
        try:
            process = subprocess.Popen(
                [str(SCRIPT)],
                stdin=slave,
                stdout=slave,
                stderr=slave,
                text=True,
                close_fds=True,
            )
            os.close(slave)
            output = bytearray()
            deadline = time.monotonic() + 60
            os.write(master, b"\n")
            os.write(master, b"y\n\n")
            os.write(master, b"first line\nsecond line\n\n")
            while time.monotonic() < deadline:
                ready, _, _ = select.select([master], [], [], 0.1)
                if ready:
                    try:
                        output.extend(os.read(master, 4096))
                    except OSError:
                        break
                if process.poll() is not None:
                    break
            if process.poll() is None:
                process.kill()
                process.wait()
            while True:
                ready, _, _ = select.select([master], [], [], 0)
                if not ready:
                    break
                try:
                    chunk = os.read(master, 4096)
                except OSError:
                    break
                if not chunk:
                    break
                output.extend(chunk)
            text = output.decode(errors="replace")
        finally:
            os.close(master)
        self.assertEqual(process.returncode, 0, text)
        self.assertIn("ERROR_MSG=first line\\nsecond line", text)
        self.assertEqual(text.count("ERROR_MSG="), 1)


if __name__ == "__main__":
    unittest.main()
