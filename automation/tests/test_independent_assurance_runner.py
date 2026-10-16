"""Runner integration test for Independent Assurance profile."""

import unittest
from pathlib import Path

from automation.scripts.run_profile import run_profile


class IndependentAssuranceRunnerTest(unittest.TestCase):
    def test_runner_pass_fixture(self):
        fixture = Path("automation/assurance/independent-assurance/fixtures/pass.json")
        code, result = run_profile(
            "independent-assurance-v0.1",
            fixture,
            Path("/tmp"),
            None,
            "2026-10-15T00:00:00Z",
        )
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["profile_id"], "independent-assurance-v0.1")


if __name__ == "__main__":
    unittest.main()
