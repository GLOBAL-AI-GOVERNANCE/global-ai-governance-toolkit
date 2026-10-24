"""The primary command is ``gaig``; ``gag`` remains a deprecated alias."""

from __future__ import annotations

import subprocess
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import gag_toolkit  # noqa: E402
import gag_toolkit.cli  # noqa: E402
import gaig_toolkit  # noqa: E402
import gaig_toolkit.cli  # noqa: E402


class CliAliasTests(unittest.TestCase):
    def test_console_scripts_share_one_entry_point(self) -> None:
        scripts = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]["scripts"]
        self.assertEqual(scripts["gaig"], "gaig_toolkit.cli:main")
        self.assertEqual(scripts["gag"], "gaig_toolkit.cli:main")

    def test_deprecated_import_package_reexports_primary(self) -> None:
        self.assertIs(gag_toolkit.cli.main, gaig_toolkit.cli.main)
        self.assertIs(gag_toolkit.cli.build_parser, gaig_toolkit.cli.build_parser)
        self.assertEqual(gag_toolkit.__version__, gaig_toolkit.__version__)

    def test_program_name_follows_invocation(self) -> None:
        name = gaig_toolkit.cli.program_name
        self.assertEqual(name("/usr/bin/gaig"), "gaig")
        self.assertEqual(name("/usr/bin/gag"), "gag")
        self.assertEqual(name("C:\\venv\\Scripts\\gag.exe".replace("\\", "/")), "gag")
        self.assertEqual(name("/repo/gaig_toolkit/cli.py"), "gaig")
        self.assertEqual(gaig_toolkit.cli.build_parser("gaig").prog, "gaig")
        self.assertEqual(gaig_toolkit.cli.build_parser("gag").prog, "gag")

    def test_both_module_paths_run(self) -> None:
        for module in ("gaig_toolkit.cli", "gag_toolkit.cli"):
            result = subprocess.run(
                [sys.executable, "-B", "-m", module, "--version"],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), gaig_toolkit.__version__)


if __name__ == "__main__":
    unittest.main()
