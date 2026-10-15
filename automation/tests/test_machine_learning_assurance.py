from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from automation.scripts.run_profile import run_profile

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "automation/profiles/fixtures/machine-learning-assurance-pass.json"
TIME = "2026-10-15T00:00:00Z"


def _run(data, outdir):
    path = Path(outdir) / "input.json"
    path.write_text(json.dumps(data), encoding="utf-8")
    return run_profile("machine-learning-assurance-v0.1", path, Path(outdir), evaluation_time=TIME)


class MachineLearningAssuranceTests(unittest.TestCase):
    def test_pass_is_structural_only(self) -> None:
        with tempfile.TemporaryDirectory() as outdir:
            code, result = run_profile("machine-learning-assurance-v0.1", FIXTURE, Path(outdir), evaluation_time=TIME)
        self.assertEqual(code, 0)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertIn("structural", result["details"]["pass_means"].lower())
        self.assertTrue(result["evidence_references"])

    def test_fail_closed_cases(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cases = {
            "stale evidence": {**data, "evidence_stale": True},
            "material drift": {**data, "material_drift": True},
            "blocking unknown": {**data, "blocking_unknowns": ["external authenticity"]},
            "subject mismatch": {**data, "dataset_reference": {**data["dataset_reference"], "subject_id": "other"}},
            "configuration mismatch": {**data, "model_reference": {**data["model_reference"], "configuration_digest": "sha256:" + "22" * 32}},
            "expired evidence": {**data, "evaluation_reference": {**data["evaluation_reference"], "expires_at": "2020-01-01T00:00:00Z"}},
        }
        for label, payload in cases.items():
            with self.subTest(label=label):
                with tempfile.TemporaryDirectory() as outdir:
                    code, result = _run(payload, outdir)
                self.assertEqual(result["status"], "FAIL", label)
                self.assertEqual(code, 1)

    def test_schema_rejects_authority_and_automatic_promotion(self) -> None:
        data = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cases = [
            {**data, "authority_effect": "AUTHORIZE"},
            {**data, "automatic_requalification": True},
            {**data, "automatic_promotion": True},
            {k: v for k, v in data.items() if k != "evaluation_reference"},
            {**data, "dataset_reference": {**data["dataset_reference"], "artifact_digest": "sha256:short"}},
        ]
        for payload in cases:
            with tempfile.TemporaryDirectory() as outdir:
                path = Path(outdir) / "input.json"
                path.write_text(json.dumps(payload), encoding="utf-8")
                with self.assertRaises(ValueError):
                    run_profile("machine-learning-assurance-v0.1", path, Path(outdir), evaluation_time=TIME)
                self.assertFalse((Path(outdir) / "profile-result.json").exists())


if __name__ == "__main__":
    unittest.main()
