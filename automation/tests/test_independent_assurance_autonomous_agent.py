"""Autonomous agent passport reference and shutdown test age tests."""

import json
import tempfile
import unittest
from pathlib import Path

from automation.profiles import independent_assurance
from automation.scripts.run_profile import run_profile

FIXTURES = Path("automation/assurance/independent-assurance/fixtures")
AT = "2026-10-24T00:00:00Z"
PROFILE = "independent-assurance-v0.1"


def rule_ids(result):
    return {f["id"].split(":", 1)[1] for f in result["findings"]}


class AutonomousAgentTest(unittest.TestCase):
    def run_fixture(self, name, at=AT):
        with tempfile.TemporaryDirectory() as out:
            return run_profile(PROFILE, FIXTURES / name, Path(out), None, at)

    def run_data(self, data, at=AT):
        with tempfile.TemporaryDirectory() as out:
            path = Path(out) / "case.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            return run_profile(PROFILE, path, Path(out), None, at)

    def test_profile_contract_version(self):
        self.assertEqual(independent_assurance.VERSION, "0.2.0")
        registry = json.loads(Path("automation/profiles/registry.json").read_text(encoding="utf-8"))
        entry = next(p for p in registry["profiles"] if p["id"] == PROFILE)
        self.assertEqual(entry["version"], "0.2.0")

    def test_current_passing_test_with_passport_passes(self):
        code, result = self.run_fixture("agent_pass.json")
        self.assertEqual(code, 0, result["findings"])
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["details"]["shutdown_test"]["state"], "CURRENT")
        self.assertEqual(result["details"]["shutdown_test"]["age_days"], 23)
        self.assertEqual(result["details"]["shutdown_test"]["max_age_days"], 90)
        self.assertEqual(result["authority_effect"], "NONE")

    def test_missing_passport_fails(self):
        code, result = self.run_fixture("agent_missing_passport.json")
        self.assertEqual(code, 1)
        self.assertIn("AGENT_PASSPORT_MISSING", rule_ids(result))
        self.assertEqual(result["details"]["trigger"], "AGENT_PASSPORT")

    def test_missing_shutdown_test_fails(self):
        code, result = self.run_fixture("agent_missing_shutdown_test.json")
        self.assertEqual(code, 1)
        self.assertIn("SHUTDOWN_TEST_MISSING", rule_ids(result))
        self.assertEqual(result["details"]["trigger"], "SHUTDOWN_EVIDENCE")

    def test_stale_shutdown_test_fails(self):
        code, result = self.run_fixture("agent_stale_shutdown_test.json")
        self.assertEqual(code, 1)
        self.assertIn("SHUTDOWN_TEST_STALE", rule_ids(result))
        self.assertEqual(result["details"]["shutdown_test"]["state"], "STALE")

    def test_failed_shutdown_test_fails(self):
        code, result = self.run_fixture("agent_failed_shutdown_test.json")
        self.assertEqual(code, 1)
        self.assertIn("SHUTDOWN_TEST_NOT_PASSED", rule_ids(result))

    def test_tighter_max_age_applies(self):
        code, result = self.run_fixture("agent_tighter_max_age.json")
        self.assertEqual(code, 1)
        self.assertIn("SHUTDOWN_TEST_STALE", rule_ids(result))
        self.assertEqual(result["details"]["shutdown_test"]["max_age_days"], 14)

    def test_max_age_cannot_be_extended(self):
        data = json.loads((FIXTURES / "agent_stale_shutdown_test.json").read_text(encoding="utf-8"))
        data["max_shutdown_test_age_days"] = 365
        try:
            code, result = self.run_data(data)
        except ValueError:
            return  # rejected by the input schema
        self.assertEqual(code, 1)
        self.assertIn("SHUTDOWN_TEST_STALE", rule_ids(result))
        self.assertEqual(result["details"]["shutdown_test"]["max_age_days"], 90)

    def test_boundary_is_inclusive(self):
        data = json.loads((FIXTURES / "agent_pass.json").read_text(encoding="utf-8"))
        data["shutdown_evidence"]["shutdown_tested_at"] = "2026-07-26T00:00:00Z"
        code, result = self.run_data(data)
        self.assertEqual(code, 0, result["findings"])
        data["shutdown_evidence"]["shutdown_tested_at"] = "2026-07-25T23:59:59Z"
        code, result = self.run_data(data)
        self.assertIn("SHUTDOWN_TEST_STALE", rule_ids(result))

    def test_future_shutdown_test_fails(self):
        data = json.loads((FIXTURES / "agent_pass.json").read_text(encoding="utf-8"))
        data["shutdown_evidence"]["shutdown_tested_at"] = "2026-10-25T00:00:00Z"
        code, result = self.run_data(data)
        self.assertEqual(code, 1)
        self.assertIn("SHUTDOWN_TEST_IN_FUTURE", rule_ids(result))

    def test_no_evaluation_time_fails_closed(self):
        code, result = self.run_fixture("agent_pass.json", at=None)
        self.assertEqual(code, 1)
        self.assertIn("SHUTDOWN_TEST_AGE_UNKNOWN", rule_ids(result))

    def test_missing_evidence_refs_rejected_by_schema(self):
        data = json.loads((FIXTURES / "agent_pass.json").read_text(encoding="utf-8"))
        data["shutdown_evidence"]["evidence_refs"] = []
        with self.assertRaises(ValueError):
            self.run_data(data)

    def test_legacy_boolean_does_not_satisfy_autonomous_agent(self):
        data = json.loads((FIXTURES / "agent_missing_shutdown_test.json").read_text(encoding="utf-8"))
        data["shutdown_evidence_present"] = True
        code, result = self.run_data(data)
        self.assertEqual(code, 1)
        self.assertIn("SHUTDOWN_TEST_MISSING", rule_ids(result))

    def test_structured_evidence_satisfies_high_consequence(self):
        data = json.loads((FIXTURES / "agent_pass.json").read_text(encoding="utf-8"))
        data["high_consequence"] = True
        code, result = self.run_data(data)
        self.assertEqual(code, 0, result["findings"])

    def test_hint_states_boundary(self):
        code, result = self.run_fixture("missing_shutdown.json")
        hints = [f["action"] for f in result["findings"] if f["id"].endswith(":SHUTDOWN_EVIDENCE")]
        self.assertTrue(hints)
        self.assertNotIn("verified", hints[0].lower())
        self.assertIn("does not establish", hints[0])


if __name__ == "__main__":
    unittest.main()
