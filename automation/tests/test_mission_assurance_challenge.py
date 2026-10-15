from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from automation.scripts.validate_mission_challenge import ChallengeError, validate_thread
from automation.scripts.run_profile import run_profile

ROOT = Path(__file__).resolve().parents[2]
THREAD = json.loads((ROOT / "automation/assurance/mission-assurance/challenge/golden-thread.json").read_text(encoding="utf-8"))
MISSION = json.loads((ROOT / "automation/profiles/fixtures/mission-assurance-pass.json").read_text(encoding="utf-8"))
TIME = "2026-10-15T00:00:00Z"


def _mission(data):
    with tempfile.TemporaryDirectory() as outdir:
        path = Path(outdir) / "input.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return run_profile("mission-assurance-v0.1", path, Path(outdir), evaluation_time=TIME)


class MissionAssuranceChallengeTests(unittest.TestCase):
    def test_golden_thread_keeps_one_subject(self) -> None:
        self.assertEqual(THREAD["subject_id"], MISSION["subject_id"])
        self.assertEqual(THREAD["configuration_digest"], MISSION["configuration_digest"])
        self.assertEqual(THREAD["authority_effect"], "NONE")
        self.assertTrue(THREAD["synthetic"])
        self.assertEqual(validate_thread(THREAD)["authority_effect"], "NONE")

    def test_golden_thread_outcomes(self) -> None:
        normal_code, normal = _mission(MISSION)
        self.assertEqual(normal["status"], "PASS")
        self.assertEqual(normal_code, 0)
        scenarios = {item["id"]: item for item in THREAD["scenarios"]}
        cases = {
            "adversarial-failure": {k: v for k, v in MISSION.items() if k != scenarios["adversarial-failure"]["drop"]},
            "recovery-failure": {k: v for k, v in MISSION.items() if k != scenarios["recovery-failure"]["drop"]},
            "succession-failure": {k: v for k, v in MISSION.items() if k != "succession_reference"},
            "material-change": {**MISSION, "material_change": True},
        }
        for step_id, payload in cases.items():
            with self.subTest(step=step_id):
                _code, result = _mission(payload)
                self.assertEqual(result["status"], "FAIL")
        changed = cases["material-change"]
        _code, after = _mission(changed)
        self.assertTrue(after["details"]["requalification_required"])
        self.assertNotEqual(after["status"], normal["status"])
        refs = {item["reference_id"]: item for item in THREAD["references"]}
        dependency = refs[scenarios["dependency-failure"]["native_reference"]]
        succession = refs[scenarios["succession-failure"]["native_reference"]]
        self.assertEqual(dependency["expected_outcome"], "FAILED")
        self.assertEqual(succession["expected_outcome"], "FAILED")
        self.assertTrue(dependency["artifact_path"].endswith("synthetic-exit-failed.json"))
        self.assertTrue(succession["artifact_path"].endswith("succession-evidence-failed.json"))
        broken = json.loads(json.dumps(THREAD))
        broken["references"][0]["authority_effect"] = "AUTHORIZE"
        with self.assertRaises(ChallengeError):
            validate_thread(broken)

    def test_hostile_cases_do_not_create_authority(self) -> None:
        mutations = {
            "missing authority reference": {**MISSION, "authority_data_references": []},
            "unknown authority": {**MISSION, "authority_effect": "UNKNOWN"},
            "stale evidence": {**MISSION, "blocking_unknowns": ["stale evidence"]},
            "contradictory evidence": {**MISSION, "blocking_unknowns": ["contradictory evidence"]},
            "subject mismatch": {**MISSION, "baseline_reference": {**MISSION["baseline_reference"], "subject_id": "other"}},
            "configuration mismatch": {**MISSION, "qualification_reference": {**MISSION["qualification_reference"], "configuration_digest": "sha256:" + "11" * 32}},
            "expired evidence": {**MISSION, "blocking_unknowns": ["expired evidence"]},
            "revoked agent passport": {**MISSION, "blocking_unknowns": ["revoked agent passport"]},
            "malformed digest": {**MISSION, "configuration_digest": "sha256:short"},
            "dependency-exit failure": {**MISSION, "blocking_unknowns": ["dependency-exit failure"]},
            "recovery failure": {k: v for k, v in MISSION.items() if k != "recovery_reference"},
            "succession failure": {k: v for k, v in MISSION.items() if k != "succession_reference"},
            "creator assistance required": {**MISSION, "blocking_unknowns": ["creator assistance required"]},
            "blocking unknown": {**MISSION, "blocking_unknowns": ["unresolved source"]},
            "material change": {**MISSION, "material_change": True},
            "later-stage evidence cannot satisfy an earlier gate": {k: v for k, v in MISSION.items() if k != "baseline_reference"},
            "attempted authority transfer": {**MISSION, "authority_effect": "AUTHORIZE"},
            "attempted automatic requalification": {**MISSION, "material_change": True, "known_unknowns": ["automatic requalification is not available"]},
        }
        schema_errors = {"unknown authority", "malformed digest", "attempted authority transfer"}
        for label, payload in mutations.items():
            with self.subTest(label=label):
                if label in schema_errors:
                    with tempfile.TemporaryDirectory() as outdir:
                        path = Path(outdir) / "input.json"
                        path.write_text(json.dumps(payload), encoding="utf-8")
                        with self.assertRaises(ValueError):
                            run_profile("mission-assurance-v0.1", path, Path(outdir), evaluation_time=TIME)
                    continue
                _code, result = _mission(payload)
                self.assertEqual(result["status"], "FAIL")
                self.assertEqual(result["authority_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
