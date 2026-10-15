from __future__ import annotations

import json
import unittest
from pathlib import Path

from automation.profiles.mission_assurance import evaluate

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = json.loads((ROOT / "automation/profiles/fixtures/mission-assurance-pass.json").read_text(encoding="utf-8"))


def run(data):
    return evaluate(data, ROOT, "2026-10-15T00:00:00Z")


class MissionAssuranceTests(unittest.TestCase):
    def test_g8_pass_preserves_unknowns_and_boundaries(self) -> None:
        findings, _evidence, details = run(FIXTURE)
        self.assertFalse(any(item["severity"] == "CRITICAL" for item in findings))
        self.assertEqual(details["authority_effect"], "NONE")
        self.assertTrue(details["reference_only"])
        self.assertIn("external authenticity of source artifacts", details["known_unknowns"])
        self.assertFalse(details["requalification_required"])

    def test_later_stage_does_not_satisfy_missing_baseline(self) -> None:
        data = {**FIXTURE, "target_stage": "G8"}
        data.pop("baseline_reference")
        findings, _evidence, _details = run(data)
        self.assertTrue(any("MISSING_BASELINE" in item["id"] for item in findings))

    def test_negatives(self) -> None:
        wrong = {**FIXTURE["baseline_reference"], "subject_id": "other-subject"}
        bad_config = {**FIXTURE["qualification_reference"], "configuration_digest": "sha256:" + "1" * 64}
        bad_digest = {**FIXTURE["adversarial_assurance_reference"], "artifact_digest": "sha256:short"}
        elevated = {**FIXTURE["human_readiness_reference"], "authority_effect": "AUTHORIZE"}
        cases = [
            ({**FIXTURE, "target_stage": "G1", "baseline_reference": None}, "missing baseline"),
            ({**FIXTURE, "target_stage": "G2", "authority_data_references": []}, "missing authority"),
            ({**FIXTURE, "target_stage": "G1", "baseline_reference": wrong}, "subject mismatch"),
            ({**FIXTURE, "target_stage": "G3", "qualification_reference": bad_config}, "configuration mismatch"),
            ({**FIXTURE, "target_stage": "G4", "adversarial_assurance_reference": bad_digest}, "malformed digest"),
            ({**FIXTURE, "target_stage": "G5", "human_readiness_reference": elevated}, "non-NONE authority"),
            ({**FIXTURE, "target_stage": "G5", "human_readiness_reference": None}, "missing human readiness"),
            ({**FIXTURE, "target_stage": "G7", "recovery_reference": None}, "missing recovery"),
            ({**FIXTURE, "target_stage": "G8", "succession_reference": None}, "missing succession"),
            ({**FIXTURE, "material_change": True}, "material change"),
            ({**FIXTURE, "blocking_unknowns": ["source authenticity"]}, "blocking unknown"),
        ]
        for data, label in cases:
            with self.subTest(label=label):
                findings, _evidence, details = run(data)
                self.assertTrue(any(item["severity"] == "CRITICAL" for item in findings), label)
                if label == "material change":
                    self.assertTrue(details["requalification_required"])
                if label == "blocking unknown":
                    self.assertEqual(details["blocking_unknowns"], ["source authenticity"])


if __name__ == "__main__":
    unittest.main()
