"""Maturity import must reject malformed shapes and leave prior assessment unchanged."""

from __future__ import annotations

import json
import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = ROOT / "web" / "maturity" / "app.mjs"
HTML = ROOT / "web" / "maturity" / "index.html"
ENGINE = ROOT / "web" / "maturity" / "maturity-engine.mjs"
RUNNER = ROOT / "web" / "tests" / "maturity-import-runner.mjs"


class MaturityImportGuardTests(unittest.TestCase):
    def test_validator_and_status_region_exist(self) -> None:
        app = APP.read_text(encoding="utf-8")
        html = HTML.read_text(encoding="utf-8")
        engine = ENGINE.read_text(encoding="utf-8")
        self.assertIn("function validateMaturityImport", app)
        self.assertIn("validateMaturityAssessment", app)
        self.assertIn("export function validateMaturityAssessment", engine)
        self.assertIn("showImportStatus", app)
        self.assertIn('id="import-status"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn("Your current assessment was left unchanged.", app)
        self.assertIn("not valid JSON", app)
        self.assertIn("framework_id must be unesco-ai-maturity-2025", engine)
        self.assertIn("fixed-evaluation-time", html)
        self.assertIn("captureEvaluationInstant", app)
        self.assertIn("Advisory vs enforcement", html)
        self.assertNotRegex(app, re.compile(r"Object\.assign\(state,\s*imported\)"))

    def test_malformed_shapes_rejected_without_engine_throw(self) -> None:
        completed = subprocess.run(
            ["node", str(RUNNER)],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout.strip().splitlines()[-1])
        self.assertTrue(payload["ok"])
        self.assertGreaterEqual(payload["cases"], 8)


    def test_python_evaluator_rejects_evidence_object_without_throw(self) -> None:
        from automation.profiles.organizational_ai_maturity import evaluate

        payload = {
            "framework_id": "unesco-ai-maturity-2025",
            "framework_version": "2025",
            "assessment_id": "t",
            "assessment_scope": "scope",
            "assessment_coverage": "PARTIAL",
            "accountable_owner": "owner",
            "authority_effect": "NONE",
            "categories": [
                {
                    "pillar_id": "ai-governance-ethics-risk",
                    "category_id": "ai-governance-ethics-risk.ai-governance-framework",
                    "claimed_level": "READY",
                    "target_level": "DYNAMIC",
                    "evidence": {"reference": "x", "evidence_class": "OPERATING"},
                }
            ],
        }
        findings, _evidence, _details = evaluate(payload, ROOT, "2026-10-29T12:00:00Z")
        ids = {item["id"] for item in findings}
        self.assertTrue(any(item.endswith("EVIDENCE_SHAPE") for item in ids), ids)


if __name__ == "__main__":
    unittest.main()
