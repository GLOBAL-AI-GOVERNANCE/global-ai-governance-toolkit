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
INDEP = json.loads((ROOT / "automation/assurance/independent-assurance/fixtures/pass.json").read_text(encoding="utf-8"))
TIME = "2026-10-15T00:00:00Z"
OTHER_DIGEST = "sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"


def _run(profile: str, data: dict, time: str = TIME):
    with tempfile.TemporaryDirectory() as outdir:
        path = Path(outdir) / "input.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return run_profile(profile, path, Path(outdir), evaluation_time=time)


def _qual(**overrides) -> dict:
    item = {
        "qualification_id": "qual-001",
        "principal_ref": "opaque-principal",
        "role": "operator",
        "scope": "synthetic-mission-assurance",
        "subject_id": MISSION["subject_id"],
        "configuration_digest": MISSION["configuration_digest"],
        "competence_evidence_refs": ["evidence-001"],
        "qualified_from": "2026-01-01T00:00:00Z",
        "expires_at": "2027-01-01T00:00:00Z",
        "outcome": "QUALIFIED",
        "authority_effect": "NONE",
    }
    item.update(overrides)
    return item


def _decision(**overrides) -> dict:
    item = {
        "decision_id": "dec-001",
        "subject_id": MISSION["subject_id"],
        "configuration_digest": MISSION["configuration_digest"],
        "owner_ref": "opaque-owner",
        "deadline": "2026-12-01T00:00:00Z",
        "blocking": True,
        "status": "OPEN",
        "escalation_route_ref": "opaque-route",
        "authority_effect": "NONE",
    }
    item.update(overrides)
    return item


def _concern(**overrides) -> dict:
    item = {
        "concern_disposition_id": "c-001",
        "opaque_concern_ref": "opaque-concern",
        "subject_id": MISSION["subject_id"],
        "configuration_digest": MISSION["configuration_digest"],
        "assurance_effect": "QUESTIONED",
        "status": "CLOSED",
        "revalidation_required": False,
        "closure_evidence_refs": ["bounded-closure"],
        "authority_effect": "NONE",
    }
    item.update(overrides)
    return item


class MissionAssuranceFabricHostileTests(unittest.TestCase):
    def test_current_qualified_summary_does_not_authorize(self) -> None:
        data = {**MISSION, "qualification_evidence_refs": [_qual()]}
        _code, result = _run("mission-assurance-v0.1", data)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["details"]["native_authenticity"], "not established")

    def test_minimal_fake_qualification_rejected(self) -> None:
        data = {**MISSION, "qualification_evidence_refs": [{"qualification_id": "qual-001"}]}
        with self.assertRaises(ValueError):
            _run("mission-assurance-v0.1", data)

    def test_missing_competence_evidence_rejected(self) -> None:
        item = _qual()
        item["competence_evidence_refs"] = []
        data = {**MISSION, "qualification_evidence_refs": [item]}
        with self.assertRaises(ValueError):
            _run("mission-assurance-v0.1", data)

    def test_future_qualification_rejected(self) -> None:
        data = {**MISSION, "qualification_evidence_refs": [_qual(qualified_from="2026-11-01T00:00:00Z", expires_at="2027-01-01T00:00:00Z")]}
        _code, result = _run("mission-assurance-v0.1", data)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_conditional_does_not_satisfy_readiness(self) -> None:
        data = {**MISSION, "qualification_evidence_refs": [_qual(outcome="CONDITIONAL")]}
        _code, result = _run("mission-assurance-v0.1", data)
        self.assertEqual(result["status"], "FAIL")

    def test_wrong_qualification_subject_and_configuration(self) -> None:
        _code, subject = _run("mission-assurance-v0.1", {**MISSION, "qualification_evidence_refs": [_qual(subject_id="other-subject")]})
        _code, config = _run("mission-assurance-v0.1", {**MISSION, "qualification_evidence_refs": [_qual(configuration_digest=OTHER_DIGEST)]})
        self.assertEqual(subject["status"], "FAIL")
        self.assertEqual(config["status"], "FAIL")

    def test_expired_qualification_and_not_qualified(self) -> None:
        _code, expired = _run("mission-assurance-v0.1", {**MISSION, "qualification_evidence_refs": [_qual(expires_at="2026-02-01T00:00:00Z")]})
        _code, negative = _run("mission-assurance-v0.1", {**MISSION, "qualification_evidence_refs": [_qual(outcome="NOT_QUALIFIED")]})
        self.assertEqual(expired["status"], "FAIL")
        self.assertEqual(negative["status"], "FAIL")

    def test_decision_wrong_subject_and_configuration(self) -> None:
        _code, subject = _run("mission-assurance-v0.1", {**MISSION, "unresolved_decision_refs": [_decision(subject_id="other-subject")]})
        _code, config = _run("mission-assurance-v0.1", {**MISSION, "unresolved_decision_refs": [_decision(configuration_digest=OTHER_DIGEST)]})
        self.assertEqual(subject["status"], "FAIL")
        self.assertEqual(config["status"], "FAIL")

    def test_decision_missing_owner_or_escalation_rejected(self) -> None:
        missing_owner = _decision()
        del missing_owner["owner_ref"]
        missing_route = _decision()
        del missing_route["escalation_route_ref"]
        with self.assertRaises(ValueError):
            _run("mission-assurance-v0.1", {**MISSION, "unresolved_decision_refs": [missing_owner]})
        with self.assertRaises(ValueError):
            _run("mission-assurance-v0.1", {**MISSION, "unresolved_decision_refs": [missing_route]})

    def test_blocking_open_escalated_and_expired_fail(self) -> None:
        _code, opened = _run("mission-assurance-v0.1", {**MISSION, "unresolved_decision_refs": [_decision(status="OPEN", deadline="2026-12-01T00:00:00Z")]})
        _code, escalated = _run("mission-assurance-v0.1", {**MISSION, "unresolved_decision_refs": [_decision(status="ESCALATED")]})
        _code, expired = _run("mission-assurance-v0.1", {**MISSION, "unresolved_decision_refs": [_decision(status="OPEN", deadline="2026-10-01T00:00:00Z")]})
        self.assertEqual(opened["status"], "FAIL")
        self.assertEqual(escalated["status"], "FAIL")
        self.assertEqual(expired["status"], "FAIL")
        self.assertEqual(expired["authority_effect"], "NONE")

    def test_resolved_without_resolution_reference_fails(self) -> None:
        _code, result = _run("mission-assurance-v0.1", {**MISSION, "unresolved_decision_refs": [_decision(status="RESOLVED", blocking=False)]})
        self.assertEqual(result["status"], "FAIL")

    def test_withdrawn_does_not_authorize(self) -> None:
        _code, result = _run("mission-assurance-v0.1", {**MISSION, "unresolved_decision_refs": [_decision(status="WITHDRAWN", blocking=False)]})
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["authority_effect"], "NONE")

    def test_questioned_revalidation_hold_and_stale_cannot_pass(self) -> None:
        questioned = _run("mission-assurance-v0.1", {**MISSION, "protected_concern_disposition_refs": [_concern(assurance_effect="QUESTIONED", revalidation_required=True)]})[1]
        hold = _run("mission-assurance-v0.1", {**MISSION, "protected_concern_disposition_refs": [_concern(assurance_effect="HOLD", status="ACTIVE", revalidation_required=True)]})[1]
        stale = _run("mission-assurance-v0.1", {**MISSION, "protected_concern_disposition_refs": [_concern(assurance_effect="STALE", revalidation_required=True)]})[1]
        self.assertEqual(questioned["status"], "FAIL")
        self.assertEqual(hold["status"], "FAIL")
        self.assertEqual(stale["status"], "FAIL")

    def test_concern_wrong_subject_and_configuration(self) -> None:
        subject = _run("mission-assurance-v0.1", {**MISSION, "protected_concern_disposition_refs": [_concern(subject_id="other-subject")]})[1]
        config = _run("mission-assurance-v0.1", {**MISSION, "protected_concern_disposition_refs": [_concern(configuration_digest=OTHER_DIGEST)]})[1]
        self.assertEqual(subject["status"], "FAIL")
        self.assertEqual(config["status"], "FAIL")

    def test_malformed_reference_and_authority_rejected(self) -> None:
        extra = _qual(reporter_identity="hidden")
        bad_authority = _qual(authority_effect="AUTHORIZE")
        with self.assertRaises(ValueError):
            _run("mission-assurance-v0.1", {**MISSION, "qualification_evidence_refs": [extra]})
        with self.assertRaises(ValueError):
            _run("mission-assurance-v0.1", {**MISSION, "qualification_evidence_refs": [bad_authority]})

    def test_independent_weak_qualification_rejected(self) -> None:
        data = {**INDEP, "qualification_evidence": {"qualification_id": "qual-001", "outcome": "QUALIFIED"}}
        with self.assertRaises(ValueError):
            _run("independent-assurance-v0.1", data)

    def test_independent_conditional_and_future_fail(self) -> None:
        conditional = {**INDEP}
        conditional["qualification_evidence"] = {**INDEP["qualification_evidence"], "outcome": "CONDITIONAL"}
        future = {**INDEP}
        future["qualification_evidence"] = {**INDEP["qualification_evidence"], "qualified_from": "2026-12-01T00:00:00Z", "expires_at": "2027-12-01T00:00:00Z"}
        self.assertEqual(_run("independent-assurance-v0.1", conditional)[1]["status"], "FAIL")
        self.assertEqual(_run("independent-assurance-v0.1", future)[1]["status"], "FAIL")
        self.assertEqual(_run("independent-assurance-v0.1", INDEP)[1]["authority_effect"], "NONE")

    def test_no_auto_authorization(self) -> None:
        _code, result = _run("mission-assurance-v0.1", MISSION)
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertTrue(result["details"]["reference_only"])


if __name__ == "__main__":
    unittest.main()
