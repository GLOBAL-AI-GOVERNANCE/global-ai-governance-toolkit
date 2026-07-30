from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PIPELINE = (
    REPO_ROOT
    / "automation"
    / "scripts"
    / "run_governance_checks.py"
)
VALID_FIXTURE = (
    REPO_ROOT
    / "automation"
    / "fixtures"
    / "valid-ai-inventory.csv"
)
CRITICAL_FIXTURE = (
    REPO_ROOT
    / "automation"
    / "fixtures"
    / "critical-ai-inventory.csv"
)
SCHEMA = (
    REPO_ROOT
    / "automation"
    / "schemas"
    / "ai-system-inventory.schema.json"
)
POLICY = (
    REPO_ROOT
    / "automation"
    / "policy-as-code"
    / "governance-rules.yaml"
)


class RuntimeAlignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.environment = os.environ.copy()
        self.environment["PYTHONDONTWRITEBYTECODE"] = "1"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def run_pipeline(
        self,
        inventory: Path,
        name: str,
        *extra: object,
    ) -> subprocess.CompletedProcess[str]:
        outdir = self.root / name
        command = [
            sys.executable,
            "-B",
            str(PIPELINE),
            str(inventory),
            "--outdir",
            str(outdir),
            *[str(item) for item in extra],
        ]
        return subprocess.run(
            command,
            check=False,
            text=True,
            capture_output=True,
            env=self.environment,
        )

    def write_inventory(
        self,
        name: str,
        fieldnames: list[str],
        row: dict[str, str],
    ) -> Path:
        path = self.root / name
        with path.open(
            "w",
            encoding="utf-8",
            newline="",
        ) as file_handle:
            writer = csv.DictWriter(
                file_handle,
                fieldnames=fieldnames,
            )
            writer.writeheader()
            writer.writerow(row)
        return path

    def read_fixture(self) -> tuple[list[str], dict[str, str]]:
        with VALID_FIXTURE.open(
            "r",
            encoding="utf-8",
            newline="",
        ) as file_handle:
            reader = csv.DictReader(file_handle)
            return list(reader.fieldnames or []), next(reader)

    def test_valid_inventory_passes_schema_and_policy(self) -> None:
        result = self.run_pipeline(
            VALID_FIXTURE,
            "valid",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        schema_report = (
            self.root
            / "valid"
            / "schema-validation-report.md"
        )
        governance_report = (
            self.root
            / "valid"
            / "governance-validation-report.md"
        )

        self.assertIn(
            "Inventory schema validation passed.",
            schema_report.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "No governance gaps found.",
            governance_report.read_text(encoding="utf-8"),
        )

    def test_critical_policy_findings_block_with_rule_ids(self) -> None:
        result = self.run_pipeline(
            CRITICAL_FIXTURE,
            "critical",
        )
        self.assertEqual(result.returncode, 1)

        report = (
            self.root
            / "critical"
            / "governance-validation-report.md"
        ).read_text(encoding="utf-8")

        self.assertIn("[GAI-AUTO-001]", report)
        self.assertIn("[GAI-AUTO-003]", report)
        self.assertIn(
            "CRITICAL - Missing named owner",
            report,
        )
        self.assertIn(
            "CRITICAL - Shutdown path is missing",
            report,
        )

    def test_report_only_mode_retains_findings(self) -> None:
        result = self.run_pipeline(
            CRITICAL_FIXTURE,
            "report-only",
            "--fail-on",
            "none",
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        report = (
            self.root
            / "report-only"
            / "governance-validation-report.md"
        ).read_text(encoding="utf-8")
        self.assertIn("[GAI-AUTO-001]", report)

    def test_missing_required_column_blocks_with_exit_2(self) -> None:
        fieldnames, row = self.read_fixture()
        fieldnames.remove("business_unit")
        row.pop("business_unit")
        inventory = self.write_inventory(
            "missing-column.csv",
            fieldnames,
            row,
        )

        result = self.run_pipeline(
            inventory,
            "missing-column",
        )
        self.assertEqual(result.returncode, 2)

        report = (
            self.root
            / "missing-column"
            / "schema-validation-report.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "missing required field 'business_unit'",
            report,
        )

    def test_invalid_enum_blocks_with_exit_2(self) -> None:
        fieldnames, row = self.read_fixture()
        row["monitoring_active"] = "Maybe"
        inventory = self.write_inventory(
            "invalid-enum.csv",
            fieldnames,
            row,
        )

        result = self.run_pipeline(
            inventory,
            "invalid-enum",
        )
        self.assertEqual(result.returncode, 2)

        report = (
            self.root
            / "invalid-enum"
            / "schema-validation-report.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "value 'Maybe' is not allowed",
            report,
        )

    def test_missing_schema_fails_safely(self) -> None:
        result = self.run_pipeline(
            VALID_FIXTURE,
            "missing-schema",
            "--schema",
            self.root / "missing-schema.json",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "Schema file not found",
            result.stdout,
        )

    def test_missing_policy_fails_safely(self) -> None:
        result = self.run_pipeline(
            VALID_FIXTURE,
            "missing-policy",
            "--policy",
            self.root / "missing-policy.yaml",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn(
            "Policy file not found",
            result.stdout,
        )

    def test_policy_change_changes_runtime_outcome(self) -> None:
        policy = json.loads(
            POLICY.read_text(encoding="utf-8")
        )

        monitoring_rule = next(
            rule
            for rule in policy["rules"]
            if rule["id"] == "GAI-AUTO-002"
        )
        monitoring_rule["severity"] = "critical"
        monitoring_rule["all"][0]["value"] = "Yes"
        monitoring_rule["message"] = (
            "Mutation test proves runtime consumes policy."
        )

        mutated_policy = self.root / "mutated-policy.yaml"
        mutated_policy.write_text(
            json.dumps(policy, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

        result = self.run_pipeline(
            VALID_FIXTURE,
            "mutated-policy",
            "--policy",
            mutated_policy,
        )
        self.assertEqual(result.returncode, 1)

        report = (
            self.root
            / "mutated-policy"
            / "governance-validation-report.md"
        ).read_text(encoding="utf-8")
        self.assertIn("[GAI-AUTO-002]", report)
        self.assertIn(
            "Mutation test proves runtime consumes policy.",
            report,
        )

    def test_default_sources_are_the_checked_in_files(self) -> None:
        self.assertTrue(SCHEMA.is_file())
        self.assertTrue(POLICY.is_file())


if __name__ == "__main__":
    unittest.main()
