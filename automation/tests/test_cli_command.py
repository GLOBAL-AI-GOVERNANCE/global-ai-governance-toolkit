"""The installed command is ``gaig``. No other command name is installed."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import gaig_toolkit  # noqa: E402
import gaig_toolkit.cli  # noqa: E402


class CliCommandTests(unittest.TestCase):
    def test_only_gaig_console_script_is_installed(self) -> None:
        project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]
        self.assertEqual(project["scripts"], {"gaig": "gaig_toolkit.cli:main"})

    def test_parser_uses_gaig(self) -> None:
        self.assertEqual(gaig_toolkit.cli.build_parser().prog, "gaig")

    def test_no_legacy_import_package(self) -> None:
        self.assertFalse((ROOT / ("ga" + "g_toolkit")).exists())
        self.assertIsNone(importlib.util.find_spec("ga" + "g_toolkit"))

    def test_module_path_runs(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", "-m", "gaig_toolkit.cli", "--version"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), gaig_toolkit.__version__)


if __name__ == "__main__":
    unittest.main()
