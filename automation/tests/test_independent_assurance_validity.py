"""Independent validity-state tests."""

import unittest
from pathlib import Path

from automation.scripts.run_profile import run_profile


class IndependentAssuranceValidityTest(unittest.TestCase):
    def test_material_change_only(self):
        fixture = Path("automation/assurance/independent-assurance/fixtures/material_change.json")
        code, result = run_profile("independent-assurance-v0.1", fixture, Path("/tmp"), None, None)
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["details"]["validity_state"], "STALE")
        self.assertTrue(result["details"]["revalidation_required"])
        self.assertEqual(result["details"]["trigger"], "MATERIAL_CHANGE")

    def test_unresolved_concern_only(self):
        fixture = Path("automation/assurance/independent-assurance/fixtures/unresolved_concern.json")
        code, result = run_profile("independent-assurance-v0.1", fixture, Path("/tmp"), None, None)
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["details"]["validity_state"], "QUESTIONED")
        self.assertTrue(result["details"]["revalidation_required"])
        self.assertEqual(result["details"]["trigger"], "UNRESOLVED_CONCERN")
        self.assertEqual(result["status"], "CONDITIONAL")


if __name__ == "__main__":
    unittest.main()
