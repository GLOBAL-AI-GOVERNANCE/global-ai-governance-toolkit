"""Packaging regression for the isolated framework adapter."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQUIRED = (
    "framework-metadata.json",
    "ATTRIBUTION.md",
    "LICENSE-NOTICE.md",
    "PROVENANCE.md",
)


class TestFrameworkPackaging(unittest.TestCase):
    def test_framework_resources_are_in_the_wheel(self):
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", tmp, str(ROOT)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            wheels = list(Path(tmp).glob("*.whl"))
            self.assertEqual(len(wheels), 1, wheels)
            with zipfile.ZipFile(wheels[0]) as archive:
                names = archive.namelist()
            for name in REQUIRED:
                self.assertTrue(any(name in entry for entry in names), name)
