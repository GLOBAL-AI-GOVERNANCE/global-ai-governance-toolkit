"""XSS escaping, maturity evaluation time, and GAI-AUTO-005 browser checks."""

from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNNER = ROOT / "web/tests/xss-and-maturity-runner.mjs"


@unittest.skipUnless(shutil.which("node"), "Node.js is required")
class XssAndMaturityBrowserTests(unittest.TestCase):
    def test_xss_date_and_auto005_runner(self) -> None:
        completed = subprocess.run(
            ["node", str(RUNNER)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            self.fail(completed.stdout + completed.stderr)
        self.assertIn('"ok":true', completed.stdout.replace(" ", ""))


if __name__ == "__main__":
    unittest.main()
