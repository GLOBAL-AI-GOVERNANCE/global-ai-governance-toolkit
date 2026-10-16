#!/usr/bin/env python3
"""Hostile synthetic cases for mission assurance fabric integration.

No scenario authorizes operation. authority_effect remains NONE.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from automation.scripts.run_profile import run_profile

ROOT = Path(__file__).resolve().parents[2]
MISSION = json.loads((ROOT / "automation/profiles/fixtures/mission-assurance-pass.json").read_text(encoding="utf-8"))
INDEP = json.loads((ROOT / "automation/profiles/fixtures/independent-assurance-pass.json").read_text(encoding="utf-8")) if (ROOT / "automation/profiles/fixtures/independent-assurance-pass.json").exists() else {
    "subject_id": "synthetic-subject-alpha",
    "authority_effect": "NONE",
    "evaluator": {"identity": "opaque-eval", "interests_disclosed": True},
    "scope": "synthetic-mission-assurance",
}
TIME = "2026-10-15T00:00:00Z"


def _run(profile: str, data: dict, time: str = TIME):
    with tempfile.TemporaryDirectory() as outdir:
        path = Path(outdir) / "input.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return run_profile(profile, path, Path(outdir), evaluation_time=time)


class MissionAssuranceFabricHostileTests(unittest.TestCase):
    def test_original_developer_disappears_successor_expired(self) -> None:
        data = {**MISSION}
        data["qualification_evidence_refs"] = [{
            "qualification_id": "qual-001",
            "outcome": "QUALIFIED",
            "expires_at": "2026-09-01T00:00:00Z",
            "authority_effect": "NONE",
            "subject_id": data["subject_id"],
        }]
        code, result = _run("mission-assurance-v0.1", data, "2026-10-15T00:00:00Z")
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_evaluator_identity_no_valid_qualification(self) -> None:
        data = {**INDEP}
        data["qualification_evidence"] = {
            "qualification_id": "qual-001",
            "outcome": "NOT_QUALIFIED",
            "authority_effect": "NONE",
        }
        code, result = _run("independent-assurance-v0.1", data)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_decision_deadline_expires(self) -> None:
        data = {**MISSION}
        data["unresolved_decision_refs"] = [{
            "decision_id": "dec-001",
            "status": "OPEN",
            "deadline": "2026-10-01T00:00:00Z",
            "blocking": True,
            "authority_effect": "NONE",
        }]
        code, result = _run("mission-assurance-v0.1", data, "2026-10-15T00:00:00Z")
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_decision_escalates_unresolved(self) -> None:
        data = {**MISSION}
        data["unresolved_decision_refs"] = [{
            "decision_id": "dec-001",
            "status": "ESCALATED",
            "blocking": True,
            "authority_effect": "NONE",
        }]
        code, result = _run("mission-assurance-v0.1", data)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_material_concern_hold(self) -> None:
        data = {**MISSION}
        data["protected_concern_disposition_refs"] = [{
            "concern_disposition_id": "c-001",
            "assurance_effect": "HOLD",
            "status": "ACTIVE",
            "authority_effect": "NONE",
            "revalidation_required": True,
        }]
        code, result = _run("mission-assurance-v0.1", data)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_concern_closes_revalidation_required(self) -> None:
        data = {**MISSION}
        data["protected_concern_disposition_refs"] = [{
            "concern_disposition_id": "c-001",
            "assurance_effect": "STALE",
            "status": "CLOSED",
            "closure_evidence_refs": ["bounded-ref"],
            "revalidation_required": True,
            "authority_effect": "NONE",
        }]
        code, result = _run("mission-assurance-v0.1", data)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_no_auto_authorization(self) -> None:
        # Even clean case remains NONE
        code, result = _run("mission-assurance-v0.1", MISSION)
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertTrue(result["details"]["reference_only"])


if __name__ == "__main__":
    unittest.main()
