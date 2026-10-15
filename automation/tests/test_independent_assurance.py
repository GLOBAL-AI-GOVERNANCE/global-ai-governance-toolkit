"""Tests for Independent Assurance profile."""

import unittest
from pathlib import Path

from automation.profiles.independent_assurance import evaluate


class IndependentAssuranceEvaluatorTest(unittest.TestCase):
    def test_pass_case_returns_findings_evidence_details(self):
        payload = {
            "subject_id": "system-001",
            "authority_effect": "NONE",
            "evaluator": {"identity": "evaluator-001", "interests_disclosed": True},
            "scope": "bounded",
        }
        findings, evidence, details = evaluate(payload, Path("."), None)
        self.assertTrue(details["reference_only"])
        self.assertEqual(details["validity_state"], "VALID")
        self.assertFalse(any(f["severity"] == "CRITICAL" for f in findings))


if __name__ == "__main__":
    unittest.main()
