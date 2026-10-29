"""Maturity import must show an error and never wipe state on invalid input."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "web" / "maturity" / "app.mjs"
HTML = ROOT / "web" / "maturity" / "index.html"


class MaturityImportGuardTests(unittest.TestCase):
    def test_validator_and_status_region_exist(self) -> None:
        app = APP.read_text(encoding="utf-8")
        html = HTML.read_text(encoding="utf-8")
        self.assertIn("function validateMaturityImport", app)
        self.assertIn("showImportStatus", app)
        self.assertIn('id="import-status"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn("Your current assessment was left unchanged.", app)
        self.assertIn("not valid JSON", app)
        self.assertIn("framework_id must be unesco-ai-maturity-2025", app)
        # Must not blindly Object.assign the whole import anymore
        self.assertNotRegex(app, re.compile(r"Object\.assign\(state,\s*imported\)"))


if __name__ == "__main__":
    unittest.main()
