"""Fail fixture behavior for Independent Assurance profile."""

import unittest
from pathlib import Path

from automation.scripts.run_profile import run_profile


class IndependentAssuranceFailTest(unittest.TestCase):
    def test_runner_fail_fixture(self):
        fixture = Path("automation/assurance/independent-assurance/fixtures/fail.json")
        code, result = run_profile(
            "independent-assurance-v0.1",
            fixture,
            Path("/tmp"),
            None,
            None,
        )
        self.assertEqual(code, 1)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["authority_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
