"""Expiry, conflict, and shutdown tests."""

import unittest
from pathlib import Path

from automation.scripts.run_profile import run_profile


class ExpiryConflictShutdownTest(unittest.TestCase):
    def test_expired(self):
        fixture = Path("automation/assurance/independent-assurance/fixtures/expired.json")
        code, result = run_profile("independent-assurance-v0.1", fixture, Path("/tmp"), None, None)
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["details"]["validity_state"], "STALE")
        self.assertEqual(result["details"]["trigger"], "EXPIRED")

    def test_evaluator_conflict(self):
        fixture = Path("automation/assurance/independent-assurance/fixtures/conflict.json")
        code, result = run_profile("independent-assurance-v0.1", fixture, Path("/tmp"), None, None)
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["details"]["trigger"], "EVALUATOR_CONFLICT")

    def test_missing_shutdown(self):
        fixture = Path("automation/assurance/independent-assurance/fixtures/missing_shutdown.json")
        code, result = run_profile("independent-assurance-v0.1", fixture, Path("/tmp"), None, None)
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["details"]["trigger"], "SHUTDOWN_EVIDENCE")


if __name__ == "__main__":
    unittest.main()
