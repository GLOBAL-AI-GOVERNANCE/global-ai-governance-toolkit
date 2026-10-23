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
    def test_supported_but_level_undetermined(self):
        data = load("maturity-supported.json")
        findings, evidence, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        cats = details["categories"]
        self.assertEqual(len(cats), 1)
        cat = cats[0]
        self.assertEqual(cat["claimed_level"], "DYNAMIC")
        self.assertIsNone(cat["evidence_supported_level"])  # conservative: no auto-level
        self.assertEqual(cat["support_status"], "PARTIAL")
        self.assertEqual(details["human_determination"], "PENDING")
        self.assertEqual(details["authority_effect"], "NONE")
        self.assertEqual(details["overall_synthesis"], "PENDING_HUMAN_SYNTHESIS")

    def test_multi_category_all_evaluated(self):
        data = load("maturity-supported.json")
        # add second adverse category
        data["categories"].append({
            "pillar": "People & Culture",
            "category": "AI Literacy",
            "claimed_level": "ADVANCED",
            "evidence": []
        })
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertEqual(len(details["categories"]), 2)
        self.assertEqual(details["categories"][1]["support_status"], "UNSUPPORTED")

    def test_policy_only_overclaim(self):
        data = load("maturity-policy-only-overclaim.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("POLICY_ONLY_OVERCLAIM") for f in findings))
        self.assertEqual(details["categories"][0]["support_status"], "PARTIAL")

    def test_scope_mismatch(self):
        data = load("maturity-scope-mismatch.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("SCOPE_MISMATCH") for f in findings))
        self.assertEqual(details["categories"][0]["support_status"], "UNSUPPORTED")

    def test_stale_and_reassessment(self):
        data = load("maturity-stale.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("STALE") for f in findings))
        self.assertEqual(details["categories"][0]["freshness_status"], "STALE")
        self.assertEqual(details["categories"][0]["assessment_state"], "REASSESSMENT_REQUIRED")

    def test_synthetic_misuse(self):
        data = load("maturity-synthetic-evidence-misuse.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("SYNTHETIC_MISUSE") for f in findings))

    def test_contradicted_preserved_with_stale(self):
        data = load("maturity-contradicted.json")
        data["categories"][0]["evidence"][0]["valid_through"] = "2025-01-01T00:00:00Z"
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("CONTRADICTED") for f in findings))
        cat = details["categories"][0]
        self.assertEqual(cat["support_status"], "CONTRADICTED")
        self.assertEqual(cat["freshness_status"], "STALE")

    def test_unsupported_missing_evidence(self):
        data = load("maturity-unsupported.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("MISSING_EVIDENCE") for f in findings))
        self.assertEqual(details["categories"][0]["support_status"], "UNSUPPORTED")

    def test_configured_trigger_alone_does_not_reassess(self):
        data = load("maturity-reassessment-required.json")
        # only triggers, no material_change_events
        data["categories"][0]["material_change_events"] = []
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertFalse(any(f["id"].endswith("REASSESSMENT_REQUIRED") for f in findings))
        self.assertEqual(details["categories"][0]["assessment_state"], "CURRENT")

    def test_observed_material_change_does_reassess(self):
        data = load("maturity-reassessment-required.json")
        data["categories"][0]["material_change_events"] = ["provider-change"]
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("REASSESSMENT_REQUIRED") for f in findings))
        self.assertEqual(details["categories"][0]["assessment_state"], "REASSESSMENT_REQUIRED")

    def test_wrong_framework_version_rejected(self):
        data = load("maturity-supported.json")
        data["framework_version"] = "2024"
        findings, _, _ = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("FRAMEWORK_VERSION") for f in findings))

    def test_time_with_offset(self):
        data = load("maturity-stale.json")
        data["categories"][0]["evidence"][0]["valid_through"] = "2025-01-01T00:00:00+00:00"
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00+00:00")
        self.assertTrue(any(f["id"].endswith("STALE") for f in findings))

    def test_non_representative_operating(self):
        data = load("maturity-supported.json")
        data["categories"][0]["evidence"][0]["is_representative"] = False
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("NON_REPRESENTATIVE") for f in findings))
        self.assertEqual(details["categories"][0]["support_status"], "PARTIAL")

    def test_no_authority_transfer(self):
        data = load("maturity-supported.json")
        _, _, details = evaluate(data, ROOT)
        self.assertEqual(details["authority_effect"], "NONE")
        self.assertEqual(details["human_determination"], "PENDING")


if __name__ == "__main__":
    unittest.main()
