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

    def test_subject_bindings_are_explicit(self) -> None:
        result = validate_thread(THREAD)
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertEqual(result["bindings"], 6)
        self.assertTrue(THREAD["synthetic"])
        self.assertFalse(THREAD["automatic_requalification"])
        bindings = {item["reference_id"]: item for item in THREAD["subject_bindings"]}
        subject_refs = [
            item for item in THREAD["references"]
            if "subject_id" in item or "configuration_digest" in item
        ]
        self.assertEqual(set(bindings), {item["reference_id"] for item in subject_refs})
        for ref in subject_refs:
            binding = bindings[ref["reference_id"]]
            self.assertEqual(binding["binding_type"], "SUPPORTING_EVIDENCE_FOR")
            self.assertEqual(binding["thread_subject_id"], THREAD["subject_id"])
            self.assertEqual(binding["thread_configuration_digest"], THREAD["configuration_digest"])
            self.assertEqual(binding["native_subject_id"], ref["subject_id"])
            self.assertEqual(binding["native_configuration_digest"], ref["configuration_digest"])
            self.assertNotEqual(binding["native_subject_id"], binding["thread_subject_id"])
            self.assertEqual(binding["authority_effect"], "NONE")
            self.assertTrue(binding["limitations"])
            text = " ".join(binding["limitations"]).lower()
            self.assertIn("synthetic declared binding", text)
            self.assertIn("not external proof", text)
        scenarios = {item["id"]: item for item in THREAD["scenarios"]}
        self.assertEqual(scenarios["dependency-failure"]["expect"], "NOT_CURRENT")
        self.assertEqual(scenarios["succession-failure"]["expect"], "NOT_CURRENT")
        self.assertIn(scenarios["dependency-failure"]["native_reference"], bindings)
        self.assertIn(scenarios["succession-failure"]["native_reference"], bindings)
        normal_code, normal = _mission(MISSION)
        self.assertEqual(normal_code, 0)
        self.assertEqual(normal["status"], "PASS")
        adversarial = {k: v for k, v in MISSION.items() if k != scenarios["adversarial-failure"]["drop"]}
        recovery = {k: v for k, v in MISSION.items() if k != scenarios["recovery-failure"]["drop"]}
        material = {**MISSION, "material_change": True}
        for payload in (adversarial, recovery, material):
            _code, outcome = _mission(payload)
            self.assertEqual(outcome["status"], "FAIL")
            self.assertEqual(outcome["authority_effect"], "NONE")
        _code, after = _mission(material)
        self.assertTrue(after["details"]["requalification_required"])

    def test_institutional_candidates_and_hostile_cases(self) -> None:
        result = validate_thread(THREAD)
        self.assertEqual(result["authority_effect"], "NONE")
        refs = {item["reference_id"]: item for item in THREAD["references"]}
        qual = refs["qualification-evidence-record"]
        decision = refs["unresolved-decision-record"]
        concern = refs["protected-concern-disposition-record"]
        self.assertEqual(qual["source_commit"], "9aa9f4d42527832828c29886db18d79bf480e021")
        self.assertEqual(decision["source_commit"], qual["source_commit"])
        self.assertEqual(concern["source_commit"], qual["source_commit"])
        self.assertTrue(qual["artifact_digest"].startswith("sha256:"))
        summary = THREAD["qualification_summary"]
        self.assertEqual(summary["outcome"], "QUALIFIED")
        self.assertEqual(summary["subject_id"], qual["subject_id"])
        self.assertEqual(summary["configuration_digest"], qual["configuration_digest"])
        self.assertLessEqual(summary["qualified_from"], TIME)
        self.assertGreaterEqual(summary["expires_at"], TIME)
        bindings = {item["reference_id"]: item for item in THREAD["subject_bindings"]}
        for ref_id in (qual["reference_id"], decision["reference_id"], concern["reference_id"]):
            binding = bindings[ref_id]
            self.assertEqual(binding["binding_type"], "SUPPORTING_EVIDENCE_FOR")
            self.assertEqual(binding["native_subject_id"], refs[ref_id]["subject_id"])
            self.assertNotEqual(binding["native_subject_id"], THREAD["subject_id"])
            self.assertEqual(binding["authority_effect"], "NONE")
        _code, supported = _mission(MISSION)
        self.assertEqual(supported["status"], "PASS")
        self.assertEqual(supported["authority_effect"], "NONE")
        self.assertEqual(supported["details"]["native_authenticity"], "not established")
        self.assertIn("operational readiness", supported["details"]["does_not_mean"])
        self.assertNotIn("qualification_evidence_refs", MISSION)
        self.assertNotIn("unresolved_decision_refs", MISSION)
        self.assertNotIn("protected_concern_disposition_refs", MISSION)
        text = json.dumps(supported).lower()
        self.assertNotIn("no unresolved decision exists", text)
        self.assertNotIn("no protected concern exists", text)
        limitations = " ".join(THREAD["limitations"]).lower()
        self.assertIn("no unresolved decision exists", limitations)
        self.assertIn("no protected concern exists", limitations)

        other = "sha256:" + "cc" * 32

        def qual_ref(**overrides):
            item = {
                "qualification_id": summary["qualification_id"],
                "subject_id": MISSION["subject_id"],
                "configuration_digest": MISSION["configuration_digest"],
                "competence_evidence_refs": list(summary["competence_evidence_refs"]),
                "qualified_from": summary["qualified_from"],
                "expires_at": summary["expires_at"],
                "outcome": "QUALIFIED",
                "authority_effect": "NONE",
            }
            item.update(overrides)
            return item

        def decision_ref(**overrides):
            native = THREAD["decision_summary"]
            item = {
                "decision_id": native["decision_id"],
                "subject_id": MISSION["subject_id"],
                "configuration_digest": MISSION["configuration_digest"],
                "owner_ref": native["owner_ref"],
                "deadline": native["deadline"],
                "blocking": True,
                "status": "OPEN",
                "escalation_route_ref": native["escalation_route_ref"],
                "authority_effect": "NONE",
            }
            item.update(overrides)
            return item

        def concern_ref(**overrides):
            native = THREAD["concern_summary"]
            item = {
                "concern_disposition_id": native["concern_disposition_id"],
                "subject_id": MISSION["subject_id"],
                "configuration_digest": MISSION["configuration_digest"],
                "assurance_effect": native["assurance_effect"],
                "status": native["status"],
                "revalidation_required": native["revalidation_required"],
                "closure_evidence_refs": ["bounded-closure"],
                "authority_effect": "NONE",
            }
            item.update(overrides)
            return item

        failures = {
            "qualification-conditional": {"qualification_evidence_refs": [qual_ref(outcome="CONDITIONAL")]},
            "qualification-not-qualified": {"qualification_evidence_refs": [qual_ref(outcome="NOT_QUALIFIED")]},
            "qualification-not-yet-effective": {"qualification_evidence_refs": [qual_ref(qualified_from="2026-11-01T00:00:00Z", expires_at="2027-01-01T00:00:00Z")]},
            "qualification-expired": {"qualification_evidence_refs": [qual_ref(qualified_from="2026-01-01T00:00:00Z", expires_at="2026-02-01T00:00:00Z")]},
            "qualification-wrong-subject": {"qualification_evidence_refs": [qual_ref(subject_id=summary["subject_id"])]},
            "qualification-wrong-configuration": {"qualification_evidence_refs": [qual_ref(configuration_digest=other)]},
            "decision-blocking-open": {"unresolved_decision_refs": [decision_ref()]},
            "decision-blocking-escalated": {"unresolved_decision_refs": [decision_ref(status="ESCALATED")]},
            "decision-expired": {"unresolved_decision_refs": [decision_ref(deadline="2026-10-01T00:00:00Z")]},
            "decision-wrong-subject": {"unresolved_decision_refs": [decision_ref(subject_id=decision["subject_id"], blocking=False, status="WITHDRAWN")]},
            "decision-wrong-configuration": {"unresolved_decision_refs": [decision_ref(configuration_digest=other, blocking=False, status="WITHDRAWN")]},
            "decision-resolved-without-reference": {"unresolved_decision_refs": [decision_ref(status="RESOLVED", blocking=False)]},
            "concern-questioned-revalidation": {"protected_concern_disposition_refs": [concern_ref()]},
            "concern-hold": {"protected_concern_disposition_refs": [concern_ref(assurance_effect="HOLD", status="ACTIVE")]},
            "concern-stale": {"protected_concern_disposition_refs": [concern_ref(assurance_effect="STALE", status="CLOSED")]},
            "concern-active-not-resolved": {"protected_concern_disposition_refs": [concern_ref(revalidation_required=False)]},
            "concern-wrong-subject": {"protected_concern_disposition_refs": [concern_ref(subject_id=concern["subject_id"], status="CLOSED", assurance_effect="QUESTIONED", revalidation_required=False)]},
            "concern-wrong-configuration": {"protected_concern_disposition_refs": [concern_ref(configuration_digest=other, status="CLOSED", assurance_effect="QUESTIONED", revalidation_required=False)]},
            "concern-closed-without-evidence": {"protected_concern_disposition_refs": [concern_ref(status="CLOSED", assurance_effect="QUESTIONED", revalidation_required=False, closure_evidence_refs=[])]},
        }
        for label, patch in failures.items():
            with self.subTest(label=label):
                _code, outcome = _mission({**MISSION, **patch})
                self.assertNotEqual(outcome["status"], "PASS")
                self.assertEqual(outcome["authority_effect"], "NONE")
        incomplete = qual_ref()
        incomplete["competence_evidence_refs"] = []
        with self.assertRaises(ValueError):
            _mission({**MISSION, "qualification_evidence_refs": [incomplete]})

    def test_subject_binding_negatives(self) -> None:
        def reject(mutator, label):
            broken = json.loads(json.dumps(THREAD))
            mutator(broken)
            with self.subTest(label=label):
                with self.assertRaises(ChallengeError):
                    validate_thread(broken)

        reject(
            lambda thread: thread.__setitem__(
                "subject_bindings",
                [item for item in thread["subject_bindings"] if item["reference_id"] != "evidence-object"],
            ),
            "missing binding",
        )
        reject(
            lambda thread: thread["subject_bindings"].append(
                dict(thread["subject_bindings"][0], binding_id="binding-duplicate")
            ),
            "duplicate binding",
        )
        reject(
            lambda thread: thread["subject_bindings"][0].__setitem__("reference_id", "missing-reference"),
            "unknown reference",
        )
        reject(
            lambda thread: thread["subject_bindings"][0].__setitem__("thread_subject_id", "other-mission"),
            "wrong thread subject",
        )
        reject(
            lambda thread: thread["subject_bindings"][0].__setitem__(
                "thread_configuration_digest", "sha256:" + "11" * 32
            ),
            "wrong thread configuration",
        )
        reject(
            lambda thread: thread["subject_bindings"][0].__setitem__("native_subject_id", "other-subject"),
            "wrong native subject",
        )
        reject(
            lambda thread: thread["subject_bindings"][0].__setitem__(
                "native_configuration_digest", "sha256:" + "22" * 32
            ),
            "wrong native configuration",
        )
        reject(
            lambda thread: thread["subject_bindings"][0].__setitem__("binding_type", "SAME_SUBJECT"),
            "false SAME_SUBJECT",
        )
        reject(
            lambda thread: thread["subject_bindings"][0].__setitem__("binding_type", "OWNS"),
            "unsupported relationship",
        )
        reject(
            lambda thread: thread["subject_bindings"][0].__setitem__("binding_type", "AUTHORIZES"),
            "attempted AUTHORIZES relationship",
        )
        reject(
            lambda thread: thread["subject_bindings"][0].__setitem__("authority_effect", "AUTHORIZE"),
            "authority transfer",
        )
        reject(
            lambda thread: thread["subject_bindings"][0].__setitem__("limitations", []),
            "missing limitations",
        )
        reject(
            lambda thread: thread.__setitem__(
                "subject_bindings",
                [
                    item
                    for item in thread["subject_bindings"]
                    if item["reference_id"] != "succession-evidence-failed"
                ],
            ),
            "unbound failure scenario",
        )

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
