"""Regressions for confirmed everyday-user defects on the inventory path and Decision Pack."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "web" / "governance-engine.mjs"
TEMPLATE = ROOT / "web" / "ai-system-inventory-template.csv"
NORMALIZER = ROOT / "automation" / "scripts" / "inventory_normalizer.py"
MACHINE = ROOT / "automation" / "scripts" / "machine_contracts.py"


def node_eval(script: str) -> str:
    completed = subprocess.run(
        ["node", "--input-type=module", "-e", script],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(completed.stderr or completed.stdout)
    return completed.stdout.strip()


class BlankTemplateSchemaVersionTests(unittest.TestCase):
    def test_template_ships_example_row_with_schema_version(self) -> None:
        lines = TEMPLATE.read_text(encoding="utf-8").strip().splitlines()
        self.assertGreaterEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith("Schema Version,"))
        self.assertTrue(lines[1].startswith("1.0.0,"))

    def test_browser_accepts_blank_schema_version_cell(self) -> None:
        header = TEMPLATE.read_text(encoding="utf-8").splitlines()[0]
        blank = header + "\n,SYS-BLANK,Demo,Owner,Ops,Internal,Demo use,Internal,No,No,No,No,No,None,No,Yes,Yes,Yes\n"
        out = node_eval(
            f"""
import {{ evaluateCsv }} from './web/governance-engine.mjs';
const csv = {json.dumps(blank)};
const result = await evaluateCsv(csv, {{ sourceName: 'blank.csv' }});
console.log(result.normalized.records[0].schema_version, result.result.validation_state);
"""
        )
        self.assertEqual(out, "1.0.0 VALID")

    def test_python_accepts_blank_schema_version_cell(self) -> None:
        header = TEMPLATE.read_text(encoding="utf-8").splitlines()[0]
        blank = header + "\n,SYS-BLANK,Demo,Owner,Ops,Internal,Demo use,Internal,No,No,No,No,No,None,No,Yes,Yes,Yes\n"
        sys.path.insert(0, str(ROOT))
        from automation.scripts.inventory_normalizer import normalize_inventory

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "blank.csv"
            path.write_text(blank, encoding="utf-8")
            result = normalize_inventory(path)
            self.assertEqual(result["records"][0]["schema_version"], "1.0.0")


class StrictEvaluationTimeTests(unittest.TestCase):
    def test_browser_rejects_impossible_calendar_dates(self) -> None:
        sample = (ROOT / "web" / "sample-ai-inventory.csv").read_text(encoding="utf-8")
        out = node_eval(
            f"""
import {{ evaluateCsv }} from './web/governance-engine.mjs';
const csv = {json.dumps(sample)};
try {{
  await evaluateCsv(csv, {{ evaluationTime: '2026-13-45T99:00:00Z' }});
  console.log('ACCEPTED');
}} catch (error) {{
  console.log(error.issue?.code || error.message);
}}
"""
        )
        self.assertEqual(out, "INVALID_EVALUATION_TIME")

    def test_browser_accepts_real_utc(self) -> None:
        sample = (ROOT / "web" / "sample-ai-inventory.csv").read_text(encoding="utf-8")
        out = node_eval(
            f"""
import {{ evaluateCsv }} from './web/governance-engine.mjs';
const csv = {json.dumps(sample)};
const result = await evaluateCsv(csv, {{ evaluationTime: '2026-08-29T12:00:00Z' }});
console.log(result.result.evaluation_time);
"""
        )
        self.assertEqual(out, "2026-08-29T12:00:00Z")

    def test_cli_rejects_impossible_calendar_dates(self) -> None:
        sys.path.insert(0, str(ROOT))
        from automation.scripts.machine_contracts import validate_evaluation_time

        with self.assertRaises(ValueError):
            validate_evaluation_time("2026-13-45T99:00:00Z")
        with self.assertRaises(ValueError):
            validate_evaluation_time("2026-02-30T12:00:00Z")
        validate_evaluation_time("2026-08-29T12:00:00Z")
        validate_evaluation_time(None)


class DecisionPackManifestCoverageTests(unittest.TestCase):
    def test_every_emitted_pack_file_except_manifest_and_handoff_is_listed(self) -> None:
        sample = (ROOT / "web" / "sample-ai-inventory.csv").read_text(encoding="utf-8")
        out = node_eval(
            f"""
import {{ evaluateCsv, pretty }} from './web/governance-engine.mjs';
const csv = {json.dumps(sample)};
const result = await evaluateCsv(csv, {{ sourceName: 'sample.csv' }});
const downloads = {{
  'normalized-inventory.json': pretty(result.normalized),
  'governance-findings.json': pretty(result.findings),
  'governance-result.json': pretty(result.result),
  'manifest.json': pretty(result.manifest),
  'governance-handoff.json': pretty(result.handoff),
  ...result.documents,
}};
const listed = new Set([
  ...result.manifest.generated_files.map((item) => item.path),
  ...result.manifest.source_artifacts.map((item) => item.path),
]);
const missing = Object.keys(downloads).filter((name) => name !== 'manifest.json' && name !== 'governance-handoff.json' && !listed.has(name));
console.log(JSON.stringify({{ missing, listed: [...listed].sort(), downloads: Object.keys(downloads).sort(), handoff_digest: result.handoff.artifact_digest.startsWith('sha256:') }}));
"""
        )
        payload = json.loads(out)
        self.assertEqual(payload["missing"], [])
        self.assertTrue(payload["handoff_digest"])
        # Claim accuracy: handoff intentionally references the manifest rather than listing inside it.
        self.assertNotIn("governance-handoff.json", payload["listed"])


class FindingsCardSystemIdentityTests(unittest.TestCase):
    def test_finding_cards_include_system_name_outside_details(self) -> None:
        app = (ROOT / "web" / "app.mjs").read_text(encoding="utf-8")
        self.assertIn("finding-system-name", app)
        self.assertIn("${escapeHtml(item.system_name)}", app)
        # Visible before technical details
        visible = app.split("findingCards")[1].split("byId(\"finding-list\")")[0]
        self.assertIn("finding-system", visible)
        self.assertLess(visible.index("finding-system-name"), visible.index("<details>"))


if __name__ == "__main__":
    unittest.main()
