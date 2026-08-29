from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from automation.scripts.contract_verifier import validate_instance


ROOT = Path(__file__).resolve().parents[2]
VALID = ROOT / "automation/fixtures/valid-ai-inventory.csv"
CRITICAL = ROOT / "automation/fixtures/critical-ai-inventory.csv"
PIPELINE = ROOT / "automation/scripts/run_governance_checks.py"
RUNNER = ROOT / "web/tests/parity-runner.mjs"
EVALUATION_TIME = "2026-08-29T12:00:00Z"


@unittest.skipUnless(shutil.which("node"), "Node.js is required for browser parity tests")
class BrowserParityTests(unittest.TestCase):
    def browser(self, fixture: Path) -> dict[str, object]:
        completed = subprocess.run(
            ["node", str(RUNNER), str(fixture), EVALUATION_TIME],
            cwd=ROOT, text=True, capture_output=True, check=True,
        )
        return json.loads(completed.stdout)

    def cli(self, fixture: Path, fail_on: str = "none") -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
        with tempfile.TemporaryDirectory() as temporary:
            outdir = Path(temporary)
            completed = subprocess.run(
                [sys.executable, "-B", str(PIPELINE), str(fixture), "--outdir", str(outdir), "--evaluation-time", EVALUATION_TIME, "--fail-on", fail_on],
                cwd=ROOT, text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            return tuple(json.loads((outdir / name).read_text(encoding="utf-8")) for name in ("normalized-inventory.json", "governance-findings.json", "governance-result.json"))

    def assert_parity(self, fixture: Path) -> None:
        browser = self.browser(fixture)
        normalized, findings, result = self.cli(fixture)
        self.assertEqual(browser["normalized"]["records"], normalized["records"])
        self.assertEqual(browser["findings"]["findings"], findings["findings"])
        for field in ("schema_version", "generator_version", "normalization_version", "policy_id", "policy_version", "evaluation_time", "input_digest", "validation_state", "governance_gate_state", "human_decision_state", "blocking_threshold", "finding_count", "system_ids"):
            self.assertEqual(browser["result"][field], result[field], field)
        self.assertEqual(browser["handoff"]["authority_effect"], "NONE")

    def test_browser_machine_outputs_validate_against_wave_a_contracts(self) -> None:
        browser = self.browser(VALID)
        contracts = ROOT / "automation/contracts"
        for key, schema in (
            ("normalized", "v1/normalized-inventory.schema.json"),
            ("findings", "v1/governance-findings.schema.json"),
            ("result", "v1/governance-result.schema.json"),
            ("manifest", "v1/decision-pack-manifest.schema.json"),
            ("handoff", "governance-decision-handoff.schema.json"),
        ):
            schema_path = contracts / schema
            validate_instance(
                browser[key],
                json.loads(schema_path.read_text(encoding="utf-8")),
                base=schema_path.parent,
            )

    def test_valid_fixture_matches_cli(self) -> None:
        self.assert_parity(VALID)

    def test_critical_fixture_matches_cli_in_report_only_mode(self) -> None:
        self.assert_parity(CRITICAL)

    def test_static_surface_is_local_only_and_complete(self) -> None:
        combined = "\n".join((ROOT / "web" / name).read_text(encoding="utf-8") for name in ("index.html", "app.mjs", "governance-engine.mjs"))
        for phrase in ("Try the safe sample", "Load your CSV", "Normalization preview", "Governance results", "Machine outputs", "Decision Pack", "authority_effect"):
            self.assertIn(phrase, combined)
        for forbidden in ("fetch(", "XMLHttpRequest", "WebSocket", "sendBeacon", "https://", "http://"):
            self.assertNotIn(forbidden, combined)

    def test_browser_contract_bundle_is_current(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-B", "automation/scripts/generate_browser_contract_bundle.py", "--check"],
            cwd=ROOT, text=True, capture_output=True, check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)


if __name__ == "__main__":
    unittest.main()
