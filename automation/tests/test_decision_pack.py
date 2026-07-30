from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
AUTOMATION = REPO_ROOT / "automation"
PIPELINE = (
    AUTOMATION
    / "scripts"
    / "run_governance_checks.py"
)
GENERATOR = (
    AUTOMATION
    / "scripts"
    / "generate_decision_pack.py"
)
VALID_FIXTURE = (
    AUTOMATION
    / "fixtures"
    / "valid-ai-inventory.csv"
)
CRITICAL_FIXTURE = (
    AUTOMATION
    / "fixtures"
    / "critical-ai-inventory.csv"
)
SCHEMA = (
    AUTOMATION
    / "schemas"
    / "ai-system-inventory.schema.json"
)
POLICY = (
    AUTOMATION
    / "policy-as-code"
    / "governance-rules.yaml"
)
REFERENCE = (
    REPO_ROOT
    / "examples"
    / "decision-pack"
    / "valid-system"
)
PACK_FILES = {
    "executive-summary.md",
    "system-profile.md",
    "risk-and-findings.md",
    "evidence-and-ownership.md",
    "decision-record.md",
    "action-plan.md",
    "manifest.json",
}


class DecisionPackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.environment = os.environ.copy()
        self.environment["PYTHONDONTWRITEBYTECODE"] = "1"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_pipeline(
        self,
        fixture: Path,
        name: str,
        *extra: object,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(PIPELINE),
                str(fixture),
                "--outdir",
                str(self.root / name),
                *[str(item) for item in extra],
            ],
            check=False,
            capture_output=True,
            text=True,
            env=self.environment,
        )

    def generator_command(
        self,
        outdir: Path,
        target: Path,
        *extra: object,
    ) -> list[str]:
        return [
            sys.executable,
            "-B",
            str(GENERATOR),
            "--risk-csv",
            str(outdir / "risk-tier-output.csv"),
            "--schema-report",
            str(outdir / "schema-validation-report.md"),
            "--governance-report",
            str(outdir / "governance-validation-report.md"),
            "--executive-report",
            str(outdir / "executive-ai-governance-report.md"),
            "--schema",
            str(SCHEMA),
            "--policy",
            str(POLICY),
            "--output-dir",
            str(target),
            *[str(item) for item in extra],
        ]

    def pack_bytes(self, path: Path) -> dict[str, bytes]:
        return {
            file.name: file.read_bytes()
            for file in sorted(path.iterdir())
            if file.is_file()
        }

    def test_valid_inventory_generates_complete_pack(self) -> None:
        result = self.run_pipeline(
            VALID_FIXTURE,
            "valid",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        pack = self.root / "valid" / "decision-pack"
        self.assertEqual(
            {path.name for path in pack.iterdir()},
            PACK_FILES,
        )
        decision_record = (
            pack / "decision-record.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "PENDING HUMAN DECISION",
            (
                pack / "executive-summary.md"
            ).read_text(encoding="utf-8"),
        )
        self.assertIn(
            "Not approved by automation",
            decision_record,
        )

    def test_critical_default_blocks_before_pack(self) -> None:
        result = self.run_pipeline(
            CRITICAL_FIXTURE,
            "critical",
        )
        self.assertEqual(result.returncode, 1)
        self.assertFalse(
            (
                self.root
                / "critical"
                / "decision-pack"
            ).exists()
        )

    def test_critical_report_only_generates_visible_hold(self) -> None:
        result = self.run_pipeline(
            CRITICAL_FIXTURE,
            "report-only",
            "--fail-on",
            "none",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        pack = self.root / "report-only" / "decision-pack"
        summary = (
            pack / "executive-summary.md"
        ).read_text(encoding="utf-8")
        findings = (
            pack / "risk-and-findings.md"
        ).read_text(encoding="utf-8")
        decision = (
            pack / "decision-record.md"
        ).read_text(encoding="utf-8")

        self.assertIn(
            "BLOCKED BY CRITICAL FINDINGS",
            summary,
        )
        self.assertIn("GAI-AUTO-001", findings)
        self.assertIn("GAI-AUTO-003", findings)
        self.assertIn(
            "Not approved by automation",
            decision,
        )

    def test_generation_is_byte_stable(self) -> None:
        first = self.run_pipeline(
            VALID_FIXTURE,
            "first",
        )
        second = self.run_pipeline(
            VALID_FIXTURE,
            "second",
        )
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(
            self.pack_bytes(
                self.root / "first" / "decision-pack"
            ),
            self.pack_bytes(
                self.root / "second" / "decision-pack"
            ),
        )

    def test_check_detects_drift(self) -> None:
        result = self.run_pipeline(
            VALID_FIXTURE,
            "drift-source",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        source = (
            self.root
            / "drift-source"
            / "decision-pack"
        )
        target = self.root / "drift-target"
        shutil.copytree(source, target)
        with (target / "decision-record.md").open(
            "a",
            encoding="utf-8",
        ) as file_handle:
            file_handle.write("\nDRIFT\n")

        check = subprocess.run(
            self.generator_command(
                self.root / "drift-source",
                target,
                "--check",
            ),
            check=False,
            capture_output=True,
            text=True,
            env=self.environment,
        )
        self.assertEqual(check.returncode, 1)
        self.assertIn(
            "changed generated file: decision-record.md",
            check.stdout,
        )

    def test_missing_source_artifact_fails_safely(self) -> None:
        result = self.run_pipeline(
            VALID_FIXTURE,
            "missing-source",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        outdir = self.root / "missing-source"
        (outdir / "executive-ai-governance-report.md").unlink()

        generated = subprocess.run(
            self.generator_command(
                outdir,
                self.root / "missing-pack",
            ),
            check=False,
            capture_output=True,
            text=True,
            env=self.environment,
        )
        self.assertEqual(generated.returncode, 2)
        self.assertIn(
            "Missing required Executive governance report",
            generated.stdout,
        )

    def test_committed_reference_is_current(self) -> None:
        result = self.run_pipeline(
            VALID_FIXTURE,
            "reference-source",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        check = subprocess.run(
            self.generator_command(
                self.root / "reference-source",
                REFERENCE,
                "--check",
            ),
            check=False,
            capture_output=True,
            text=True,
            env=self.environment,
        )
        self.assertEqual(
            check.returncode,
            0,
            check.stdout + check.stderr,
        )


if __name__ == "__main__":
    unittest.main()
