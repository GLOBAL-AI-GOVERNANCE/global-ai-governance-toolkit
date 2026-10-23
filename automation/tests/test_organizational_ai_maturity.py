"""Unit tests for organizational AI maturity evidence evaluator.

Profile remains unregistered. Tests call evaluate directly.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from automation.profiles.organizational_ai_maturity import evaluate

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "profiles" / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class TestOrganizationalAIMaturity(unittest.TestCase):
    def test_supported_deterministic(self):
        data = load("maturity-supported.json")
        findings, evidence, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertEqual(details["claimed_level"], "DYNAMIC")
        self.assertEqual(details["evidence_supported_level"], "DYNAMIC")
        self.assertEqual(details["support_status"], "SUPPORTED")
        self.assertEqual(details["confidence"], "HIGH")
        self.assertEqual(details["freshness_status"], "CURRENT")
        self.assertEqual(details["human_determination"], "PENDING")
        self.assertEqual(details["authority_effect"], "NONE")
        self.assertTrue(any(e["reference"].startswith("ops://") for e in evidence))

    def test_policy_only_overclaim(self):
        data = load("maturity-policy-only-overclaim.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("POLICY_ONLY_OVERCLAIM") for f in findings))
        self.assertEqual(details["support_status"], "PARTIAL")
        self.assertNotEqual(details["evidence_supported_level"], "DYNAMIC")

    def test_scope_mismatch(self):
        data = load("maturity-scope-mismatch.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("SCOPE_MISMATCH") for f in findings))
        self.assertEqual(details["support_status"], "UNSUPPORTED")

    def test_stale_and_reassessment(self):
        data = load("maturity-stale.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("STALE") for f in findings))
        self.assertEqual(details["freshness_status"], "STALE")
        self.assertEqual(details["assessment_state"], "REASSESSMENT_REQUIRED")

    def test_synthetic_misuse(self):
        data = load("maturity-synthetic-evidence-misuse.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("SYNTHETIC_MISUSE") for f in findings))

    def test_contradicted_not_averaged(self):
        data = load("maturity-contradicted.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("CONTRADICTED") for f in findings))
        self.assertEqual(details["support_status"], "CONTRADICTED")
        self.assertGreater(len(details["contradictions"]), 0)

    def test_unsupported_missing_evidence(self):
        data = load("maturity-unsupported.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("MISSING_EVIDENCE") for f in findings))
        self.assertEqual(details["support_status"], "UNSUPPORTED")

    def test_reassessment_trigger(self):
        data = load("maturity-reassessment-required.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("REASSESSMENT_REQUIRED") for f in findings))
        self.assertEqual(details["assessment_state"], "REASSESSMENT_REQUIRED")

    def test_partial(self):
        data = load("maturity-partial.json")
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertIn(details["support_status"], ("PARTIAL", "SUPPORTED"))

    def test_no_authority_transfer(self):
        data = load("maturity-supported.json")
        _, _, details = evaluate(data, ROOT)
        self.assertEqual(details["authority_effect"], "NONE")
        self.assertEqual(details["human_determination"], "PENDING")


if __name__ == "__main__":
    unittest.main()
