"""Distribution metadata and wheel layout for the ``global-ai-governance`` package."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
import tomllib
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO_URL = "https://github.com/GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit"


def project() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["project"]


class DistributionMetadataTests(unittest.TestCase):
    def test_distribution_name_command_and_import_package(self) -> None:
        data = project()
        self.assertEqual(data["name"], "global-ai-governance")
        self.assertEqual(data["scripts"], {"gaig": "gaig_toolkit.cli:main"})
        self.assertEqual(data["license"], "MIT")
        self.assertEqual(data["license-files"], ["LICENSE"])
        self.assertEqual(
            set(data["urls"]), {"Homepage", "Repository", "Documentation", "Changelog"}
        )
        self.assertFalse(any(c.startswith("License ::") for c in data["classifiers"]))

    def test_readme_links_are_absolute_and_pinned_to_the_release_tag(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        relative = re.findall(r"\]\((?!https?:|#|mailto:)([^)\s]+)\)", readme)
        self.assertEqual(relative, [], "relative links do not resolve on PyPI")
        refs = set(re.findall(re.escape(REPO_URL) + r"/(?:blob|tree)/([^/)#\s]+)", readme))
        self.assertEqual(refs, {f"v{project()['version']}"})

    def test_publish_jobs_stay_skipped_until_enabled(self) -> None:
        workflow = (ROOT / ".github/workflows/release-assets.yml").read_text(encoding="utf-8")
        self.assertIn("vars.PYPI_PUBLISH_ENABLED == 'true'", workflow)
        self.assertIn("vars.TESTPYPI_PUBLISH_ENABLED == 'true'", workflow)
        self.assertEqual(workflow.count("cp dist/*.whl dist/*.tar.gz upload/"), 2)
        self.assertRegex(workflow, r"pypa/gh-action-pypi-publish@[0-9a-f]{40} ")


class WheelLayoutTests(unittest.TestCase):
    def test_wheel_installs_only_gaig_toolkit_at_top_level(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            completed = subprocess.run(
                [sys.executable, "-m", "pip", "wheel", "--no-deps", "--wheel-dir", tmp, str(ROOT)],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            (wheel,) = Path(tmp).glob("*.whl")
            self.assertTrue(wheel.name.startswith("global_ai_governance-"), wheel.name)
            with zipfile.ZipFile(wheel) as archive:
                names = archive.namelist()
        top = {name.split("/", 1)[0] for name in names if not name.split("/", 1)[0].endswith(".dist-info")}
        self.assertEqual(top, {"gaig_toolkit"})
        self.assertIn("gaig_toolkit/_bundled/automation/scripts/run_governance_checks.py", names)
        self.assertFalse(any("/tests/" in name for name in names))


if __name__ == "__main__":
    unittest.main()
