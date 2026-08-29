from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTOMATION = ROOT / "automation"
PIPELINE = AUTOMATION / "scripts" / "run_governance_checks.py"
NORMALIZER = AUTOMATION / "scripts" / "inventory_normalizer.py"
TEMPLATE_GENERATOR = AUTOMATION / "scripts" / "generate_inventory_templates.py"
VALID = AUTOMATION / "fixtures" / "valid-ai-inventory.csv"
CRITICAL = AUTOMATION / "fixtures" / "critical-ai-inventory.csv"
HUMAN_TEMPLATE = ROOT / "spreadsheets" / "ai-system-inventory-template.csv"
LEGACY = ROOT / "spreadsheets" / "ai-system-inventory-legacy-v2.csv"


class ContractSpineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.work = Path(self.temp.name)
        self.env = os.environ.copy()
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def command(self, *args: object) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", *map(str, args)],
            cwd=ROOT,
            env=self.env,
            text=True,
            capture_output=True,
            check=False,
        )

    def normalize(self, source: Path, name: str = "normalized.json") -> subprocess.CompletedProcess[str]:
        return self.command(NORMALIZER, source, "--output-json", self.work / name, "--output-csv", self.work / f"{name}.csv")

    def canonical_row(self) -> dict[str, str]:
        with VALID.open("r", encoding="utf-8", newline="") as handle:
            return next(csv.DictReader(handle))

    def write_csv(self, name: str, headers: list[str], values: list[str]) -> Path:
        path = self.work / name
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.writer(handle, lineterminator="\n")
            writer.writerow(headers)
            writer.writerow(values)
        return path

    def test_existing_canonical_csv_normalizes(self) -> None:
        result = self.normalize(VALID)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads((self.work / "normalized.json").read_text(encoding="utf-8"))
        self.assertEqual(value["schema_version"], "1.0.0")
        self.assertEqual(value["records"][0]["system_id"], "TEST-VALID-001")

    def test_generated_human_template_maps_deterministically(self) -> None:
        with HUMAN_TEMPLATE.open("r", encoding="utf-8-sig", newline="") as handle:
            headers = next(csv.reader(handle))
        mapping = json.loads((AUTOMATION / "contracts" / "v1" / "inventory-mapping.json").read_text(encoding="utf-8"))
        reverse = {item["human_label"]: key for key, item in mapping["fields"].items()}
        row = self.canonical_row()
        source = self.write_csv(
            "human.csv",
            headers,
            ["1.0.0" if reverse[label] == "schema_version" else row[reverse[label]] for label in headers],
        )
        result = self.normalize(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        value = json.loads((self.work / "normalized.json").read_text(encoding="utf-8"))
        self.assertEqual(value["source"]["format"], "generated_human_csv")
        self.assertTrue(value["mappings_applied"])

    def test_boolean_and_enum_case_variants_are_normalized(self) -> None:
        headers = list(self.canonical_row())
        row = self.canonical_row()
        row.update({"monitoring_active": "TRUE", "shutdown_path_exists": "y", "evidence_complete": "1", "vendor_internal": "internal"})
        source = self.write_csv("variants.csv", headers, [row[key] for key in headers])
        result = self.normalize(source)
        self.assertEqual(result.returncode, 0, result.stderr)
        record = json.loads((self.work / "normalized.json").read_text(encoding="utf-8"))["records"][0]
        self.assertEqual((record["monitoring_active"], record["shutdown_path_exists"], record["evidence_complete"]), ("Yes", "Yes", "Yes"))
        self.assertEqual(record["vendor_internal"], "Internal")

    def test_ambiguous_value_returns_stable_error(self) -> None:
        headers = list(self.canonical_row())
        row = self.canonical_row()
        row["monitoring_active"] = "sometimes"
        result = self.normalize(self.write_csv("ambiguous.csv", headers, [row[key] for key in headers]))
        self.assertEqual(result.returncode, 2)
        self.assertIn("INVALID_ENUM_VALUE", result.stdout)
        self.assertIn("monitoring_active", result.stdout)

    def test_unknown_column_is_not_dropped(self) -> None:
        headers = [*self.canonical_row(), "Mystery"]
        row = self.canonical_row()
        result = self.normalize(self.write_csv("unknown.csv", headers, [*[row[key] for key in headers[:-1]], "x"]))
        self.assertEqual(result.returncode, 2)
        self.assertIn("UNKNOWN_COLUMN", result.stdout)

    def test_legacy_template_maps_only_safe_fields_and_fails_closed(self) -> None:
        result = self.normalize(LEGACY)
        self.assertEqual(result.returncode, 2)
        self.assertIn("MISSING_REQUIRED_COLUMN", result.stdout)
        self.assertNotIn("UNKNOWN_COLUMN", result.stdout)

    def test_duplicate_header_empty_input_and_unsupported_version(self) -> None:
        row = self.canonical_row()
        duplicate = self.write_csv("duplicate.csv", [*row, "system_id"], [*[row[key] for key in row], row["system_id"]])
        self.assertIn("DUPLICATE_HEADER", self.normalize(duplicate, "d.json").stdout)
        empty = self.work / "empty.csv"
        empty.write_text(",".join(row) + "\n", encoding="utf-8")
        self.assertIn("EMPTY_INPUT", self.normalize(empty, "e.json").stdout)
        headers = ["schema_version", *row]
        unsupported = self.write_csv("unsupported.csv", headers, ["2.0.0", *[row[key] for key in row]])
        self.assertIn("UNSUPPORTED_SCHEMA_VERSION", self.normalize(unsupported, "u.json").stdout)

    def test_machine_outputs_validate_and_never_approve(self) -> None:
        outdir = self.work / "out"
        result = self.command(PIPELINE, VALID, "--outdir", outdir, "--evaluation-time", "2026-08-29T12:00:00Z")
        self.assertEqual(result.returncode, 0, result.stderr)
        machine = json.loads((outdir / "governance-result.json").read_text(encoding="utf-8"))
        handoff = json.loads((outdir / "governance-handoff.json").read_text(encoding="utf-8"))
        self.assertEqual(machine["human_decision_state"], "PENDING_HUMAN_DECISION")
        self.assertEqual(handoff["authority_effect"], "NONE")
        self.assertIn("Wave A contracts", result.stdout)

    def test_blocking_finding_returns_one_and_machine_result(self) -> None:
        outdir = self.work / "blocked"
        result = self.command(PIPELINE, CRITICAL, "--outdir", outdir)
        self.assertEqual(result.returncode, 1)
        self.assertTrue((outdir / "governance-findings.json").is_file())
        self.assertEqual(json.loads((outdir / "governance-result.json").read_text(encoding="utf-8"))["governance_gate_state"], "BLOCKED")
        self.assertFalse((outdir / "decision-pack").exists())

    def test_malformed_evaluation_time_is_configuration_error(self) -> None:
        result = self.command(
            PIPELINE,
            VALID,
            "--outdir",
            self.work / "bad-time",
            "--evaluation-time",
            "2026-08-29 12:00:00",
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("evaluation time must be UTC", result.stdout)

    def test_repeated_explicit_time_run_is_byte_identical(self) -> None:
        outputs = []
        for name in ("one", "two"):
            outdir = self.work / name
            result = self.command(PIPELINE, VALID, "--outdir", outdir, "--evaluation-time", "2026-08-29T12:00:00Z")
            self.assertEqual(result.returncode, 0, result.stderr)
            outputs.append({path.relative_to(outdir).as_posix(): path.read_bytes() for path in outdir.rglob("*") if path.is_file()})
        self.assertEqual(outputs[0], outputs[1])

    def test_manifest_tampering_is_detected(self) -> None:
        outdir = self.work / "tamper"
        self.assertEqual(self.command(PIPELINE, VALID, "--outdir", outdir).returncode, 0)
        with (outdir / "decision-pack" / "decision-record.md").open("a", encoding="utf-8") as handle:
            handle.write("tamper\n")
        verify = self.command("-m", "gag_toolkit.cli", "verify", outdir)
        self.assertEqual(verify.returncode, 2)
        self.assertIn("digest mismatch", verify.stderr)

    def test_template_drift_check_and_network_free_runtime(self) -> None:
        self.assertEqual(self.command(TEMPLATE_GENERATOR, "--check").returncode, 0)
        runtime_files = [
            AUTOMATION / "scripts" / name
            for name in (
                "run_governance_checks.py", "inventory_normalizer.py", "machine_contracts.py",
                "schema_validator.py", "risk_tier_calculator.py", "governance_validator.py",
                "generate_governance_report.py", "generate_decision_pack.py",
            )
        ]
        forbidden = ("import socket", "import requests", "urllib.request", "http.client")
        combined = "\n".join(path.read_text(encoding="utf-8") for path in runtime_files)
        self.assertFalse(any(token in combined for token in forbidden))


if __name__ == "__main__":
    unittest.main()
