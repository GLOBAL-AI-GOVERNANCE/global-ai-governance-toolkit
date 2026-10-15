from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from automation.profiles.mission_assurance import evaluate
from automation.scripts.contract_verifier import validate_instance
from automation.scripts.run_profile import run_profile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "automation/profiles/fixtures/mission-assurance-pass.json"
RESULT_SCHEMA = json.loads((ROOT / "automation/contracts/v1/profile-result.schema.json").read_text(encoding="utf-8"))
TIME = "2026-10-15T00:00:00Z"


def _run(data, outdir):
    path = Path(outdir) / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return run_profile("mission-assurance-v0.1", path, Path(outdir), evaluation_time=TIME)


class MissionAssuranceRegisteredPathTests(unittest.TestCase):
    def test_positive_fixture_is_deterministic_and_evidence_bearing(self) -> None:
        with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
            code_a, result_a = run_profile("mission-assurance-v0.1", FIXTURE, Path(first), evaluation_time=TIME)
            code_b, result_b = run_profile("mission-assurance-v0.1", FIXTURE, Path(second), evaluation_time=TIME)
            self.assertEqual(code_a, 0)
            self.assertEqual(result_a["status"], "PASS")
            self.assertEqual(result_a["authority_effect"], "NONE")
            self.assertTrue(result_a["evidence_references"])
            self.assertEqual((Path(first) / "profile-result.json").read_bytes(), (Path(second) / "profile-result.json").read_bytes())
            self.assertEqual(result_a["source_artifact_sha256"], result_b["source_artifact_sha256"])
            validate_instance(result_a, RESULT_SCHEMA, base=ROOT / "automation/contracts/v1")
            self.assertTrue(all(item["type"] == "ARTIFACT_ID" and item["sha256"].startswith("sha256:") for item in result_a["evidence_references"]))

    def test_stage_bounding_excludes_later_references(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data["target_stage"] = "G1"
        with tempfile.TemporaryDirectory() as outdir:
            _code, result = _run(data, outdir)
        references = [item["reference"] for item in result["evidence_references"]]
        self.assertTrue(any("baseline" in item for item in references))
        self.assertFalse(any("succession" in item for item in references))

    def test_semantic_failures_fail_closed(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cases = {
            "missing baseline": {k: v for k, v in {**data, "target_stage": "G1"}.items() if k != "baseline_reference"},
            "missing authority": {**data, "target_stage": "G2", "authority_data_references": []},
            "subject mismatch": {**data, "target_stage": "G1", "baseline_reference": {**data["baseline_reference"], "subject_id": "other-subject"}},
            "configuration mismatch": {**data, "target_stage": "G3", "qualification_reference": {**data["qualification_reference"], "configuration_digest": "sha256:" + "1" * 64}},
            "missing human readiness": {k: v for k, v in {**data, "target_stage": "G5"}.items() if k != "human_readiness_reference"},
            "missing recovery": {k: v for k, v in {**data, "target_stage": "G7"}.items() if k != "recovery_reference"},
            "missing succession": {k: v for k, v in {**data, "target_stage": "G8"}.items() if k != "succession_reference"},
            "later stage cannot satisfy earlier gate": {k: v for k, v in data.items() if k != "baseline_reference"},
            "material change": {**data, "material_change": True},
            "blocking unknown": {**data, "blocking_unknowns": ["source authenticity"]},
        }
        for label, payload in cases.items():
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory() as outdir:
                    code, result = _run(payload, outdir)
                self.assertEqual(code, 1, label)
                self.assertEqual(result["status"], "FAIL", label)
                self.assertEqual(result["authority_effect"], "NONE")

    def test_schema_invalid_input_is_rejected_without_a_result(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cases = {
            "malformed digest": {**data, "target_stage": "G4", "adversarial_assurance_reference": {**data["adversarial_assurance_reference"], "artifact_digest": "sha256:short"}},
            "non-NONE top-level authority": {**data, "authority_effect": "AUTHORIZE"},
            "non-NONE referenced authority": {**data, "human_readiness_reference": {**data["human_readiness_reference"], "authority_effect": "AUTHORIZE"}},
            "unsupported field": {**data, "extra": "bad"},
            "malformed schema input": {"target_stage": "G0"},
        }
        for label, payload in cases.items():
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory() as outdir:
                    path = Path(outdir) / "input.json"
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    with self.assertRaises(ValueError):
                        run_profile("mission-assurance-v0.1", path, Path(outdir), evaluation_time=TIME)
                    self.assertFalse((Path(outdir) / "profile-result.json").exists())

    def test_evaluate_path_still_bounds_stage_evidence(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        data["target_stage"] = "G0"
        _findings, evidence, _details = evaluate(data, ROOT, TIME)
        self.assertEqual(evidence, [])


if __name__ == "__main__":
    unittest.main()
