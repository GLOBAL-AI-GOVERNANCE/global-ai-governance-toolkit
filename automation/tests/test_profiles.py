from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from automation.scripts.contract_verifier import validate_instance
from automation.scripts.run_profile import run_profile
from automation.profiles.common import canonical_bytes, sha256_bytes

ROOT = Path(__file__).resolve().parents[2]
AA_PASS = ROOT / "automation/assurance/auditable-ai/fixtures/pass.json"
AA_FAIL = ROOT / "automation/assurance/auditable-ai/fixtures/fail.json"
Q_PASS = ROOT / "automation/assurance/quantum-ai/fixtures/pass.json"
C_PASS = ROOT / "automation/profiles/fixtures/ciso-pass.json"
C_FAIL = ROOT / "automation/profiles/fixtures/ciso-fail.json"
RESULT_SCHEMA = ROOT / "automation/contracts/v1/profile-result.schema.json"
EVAL = "2026-08-29T12:00:00Z"


class ProfileTests(unittest.TestCase):
    def evaluate_profile(self, profile, fixture, evaluation_time=EVAL):
        temporary = tempfile.TemporaryDirectory()
        code, output = run_profile(profile, fixture, Path(temporary.name), evaluation_time=evaluation_time)
        raw = (Path(temporary.name) / "profile-result.json").read_bytes()
        self.addCleanup(temporary.cleanup)
        return code, output, raw

    def mutate_assurance(self, mutation):
        data = json.loads(AA_PASS.read_text(encoding="utf-8")); mutation(data)
        temporary = tempfile.TemporaryDirectory(); self.addCleanup(temporary.cleanup)
        path = Path(temporary.name) / "case.json"; path.write_text(json.dumps(data), encoding="utf-8")
        return self.evaluate_profile("auditable-ai-v1", path)[1]

    def mutate_quantum(self, mutation):
        data = json.loads(Q_PASS.read_text(encoding="utf-8")); mutation(data)
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "q.json"; path.write_text(json.dumps(data), encoding="utf-8")
            code, output = run_profile("quantum-ai-convergence-v0.1", path, Path(td) / "out", evaluation_time=EVAL)
        self.assertEqual(code, 1)
        return {item["id"].split(":", 1)[1] for item in output["findings"]}

    def test_common_contract_and_deterministic_output(self):
        code, output, first = self.evaluate_profile("auditable-ai-v1", AA_PASS)
        _, _, second = self.evaluate_profile("auditable-ai-v1", AA_PASS)
        self.assertEqual(code, 0); self.assertEqual(output["status"], "PASS"); self.assertEqual(first, second)
        validate_instance(output, json.loads(RESULT_SCHEMA.read_text(encoding="utf-8")), base=RESULT_SCHEMA.parent)
        self.assertEqual(output["authority_effect"], "NONE")

    def test_auditable_fail_fixture_and_hard_failures(self):
        code, output, _ = self.evaluate_profile("auditable-ai-v1", AA_FAIL)
        self.assertEqual(code, 1); self.assertEqual(output["status"], "FAIL")
        ids = {item["id"].split(":", 1)[1] for item in output["findings"]}
        for expected in ("MISSING_EVIDENCE", "POLICY_MODEL_MISMATCH", "PROHIBITED_USE_TEST_FAILED", "CRITICAL_FALSE_NEGATIVE", "UNRESOLVED_CRITICAL_BYPASS", "MISSING_APPROVING_REVIEW", "INAPPROPRIATE_ADVANCEMENT"):
            self.assertIn(expected, ids)

    def test_auditable_missing_control(self): self.assertIn("auditable-ai-v1:MISSING_CONTROL", {x["id"] for x in self.mutate_assurance(lambda d: d.pop("control"))["findings"]})
    def test_auditable_invalid_digest(self): self.assertIn("auditable-ai-v1:INVALID_ARTIFACT_REFERENCE", {x["id"] for x in self.mutate_assurance(lambda d: d["evidence"][0].update(sha256="bad"))["findings"]})
    def test_auditable_malformed_pointer(self): self.assertIn("auditable-ai-v1:MALFORMED_JSON_POINTER", {x["id"] for x in self.mutate_assurance(lambda d: d["evidence"][0].update(json_pointer="not/a/pointer"))["findings"]})
    def test_auditable_path_traversal(self): self.assertIn("auditable-ai-v1:PATH_TRAVERSAL", {x["id"] for x in self.mutate_assurance(lambda d: d["evidence"][0].update(type="LOCAL_PATH", reference="../secret"))["findings"]})
    def test_auditable_stale_evidence(self): self.assertIn("auditable-ai-v1:STALE_EVIDENCE", {x["id"] for x in self.mutate_assurance(lambda d: d["evidence"][0].update(expires_at="2025-01-01T00:00:00Z"))["findings"]})

    def test_quantum_reproducible_and_bounded(self):
        code, output, first = self.evaluate_profile("quantum-ai-convergence-v0.1", Q_PASS)
        _, _, second = self.evaluate_profile("quantum-ai-convergence-v0.1", Q_PASS)
        self.assertEqual(code, 0); self.assertEqual(first, second)
        self.assertEqual([x["matched_label"] for x in output["details"]["estimates"]], ["A", "B", "C", "D"])
        self.assertIn("not an operational safety threshold", output["details"]["threshold_boundary"])
        self.assertEqual(output["authority_effect"], "NONE")
        self.assertEqual(output["details"]["certification_semantics"], "NONE")
        self.assertEqual(set(output["details"]["evidence_dimensions"]), {"basis", "provenance", "publication_status", "replication_status"})
        self.assertEqual(output["details"]["replay_taxonomy"], {"deterministic_artifact_replay":"VERIFIED", "statistical_repeatability":"NOT_ASSESSED", "independent_external_reproducibility":"NOT_REPORTED"})
        validate_instance(output, json.loads(RESULT_SCHEMA.read_text()), base=RESULT_SCHEMA.parent)

    def test_quantum_prohibited_claim_fails(self):
        data = json.loads(Q_PASS.read_text()); data["claim"] = "quantum advantage"
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)/"q.json"; path.write_text(json.dumps(data)); code, output = run_profile("quantum-ai-convergence-v0.1", path, Path(td)/"out", evaluation_time=EVAL)
        self.assertEqual(code, 1); self.assertTrue(any("UNSUPPORTED_CLAIM" in x["id"] for x in output["findings"]))

    def test_quantum_measurement_and_quality_hazards(self):
        cases = [("MISSING_MEASUREMENTS",lambda d:d.update(measurements=[])),("MALFORMED_MEASUREMENT",lambda d:d["measurements"][0].update(value="bad")),("MISSING_MEASUREMENT_DECLARED",lambda d:d["quality"].update(missing_count=1)),("SATURATION",lambda d:d["quality"].update(saturation=True)),("CLOCK_DRIFT",lambda d:d["quality"].update(clock_drift=.01))]
        for expected, mutation in cases:
            with self.subTest(expected=expected): self.assertIn(expected, self.mutate_quantum(mutation))

    def test_quantum_bias_hazards(self):
        self.assertIn("CONSTANT_BIAS", self.mutate_quantum(lambda d:[x.update(value=r["value"]+.6) for x,r in zip(d["measurements"],d["reference_map"])]))
        self.assertIn("STEP_BIAS", self.mutate_quantum(lambda d:[x.update(value=r["value"]+(-.6 if i<2 else .6)) for i,(x,r) in enumerate(zip(d["measurements"],d["reference_map"]))]))

    def test_quantum_integrity_and_control_hazards(self):
        def tamper(d):
            d["run_evidence"]["input_snapshot"]["seed"] = 999
            d["evidence_digest"] = sha256_bytes(canonical_bytes(d["run_evidence"]))
        cases = [("CORRUPTED_REFERENCE_MAP",lambda d:d["reference_map"][0].update(value="bad")),("ALGORITHM_SUBSTITUTION",lambda d:d.update(algorithm="substituted")),("STALE_CALIBRATION",lambda d:d["calibration"].update(status="STALE")),("FALSE_HIGH_CONFIDENCE",lambda d:d["confidence"].update(level="HIGH")),("EVIDENCE_DIGEST_MISMATCH",lambda d:d.update(evidence_digest="sha256:"+"0"*64)),("RUN_EVIDENCE_TAMPERING",tamper),("MISSING_HUMAN_BOUNDARY",lambda d:d.pop("human_boundary")),("AUTHORITY_CHANGING_HANDOFF",lambda d:d["handoff"].update(authority_effect="APPROVAL")),("FALLBACK_UNAVAILABLE",lambda d:d["fallback"].update(available=False))]
        for expected, mutation in cases:
            with self.subTest(expected=expected): self.assertIn(expected, self.mutate_quantum(mutation))

    def test_quantum_unsupported_claim_classes(self):
        claims = {"UNSUPPORTED_CLAIM_OPERATIONAL":"operational deployment","UNSUPPORTED_CLAIM_AUTONOMOUS_ACTION":"autonomous action","UNSUPPORTED_CLAIM_COUNTER_DETECTION":"counter-detection","UNSUPPORTED_CLAIM_REAL_HARDWARE":"real quantum hardware","UNSUPPORTED_CLAIM_QUANTUM_ADVANTAGE":"quantum advantage","UNSUPPORTED_CLAIM_CERTIFICATION":"certification"}
        for expected, claim in claims.items():
            with self.subTest(expected=expected): self.assertIn(expected, self.mutate_quantum(lambda d,value=claim:d.update(claim=value)))

    def test_ciso_pass_fail_expiry_accountability_and_dependency(self):
        code, passed, _ = self.evaluate_profile("ciso-ai-risk-v0.1", C_PASS)
        self.assertEqual(code, 0); self.assertEqual(passed["details"]["current_decision"], "conditionally_authorized")
        self.assertEqual(passed["details"]["dependency_state"][0]["state"], "NOT_YET_ESTABLISHED")
        self.assertNotEqual(passed["details"]["dependency_state"][0]["state"], "OPERATIONAL")
        code, failed, _ = self.evaluate_profile("ciso-ai-risk-v0.1", C_FAIL)
        self.assertEqual(code, 1); ids = {x["id"] for x in failed["findings"]}
        self.assertIn("ciso-ai-risk-v0.1:MISSING_STOP_CONDITION", ids); self.assertIn("ciso-ai-risk-v0.1:DECISION_EXPIRED", ids)

    def test_decision_pack_manifest_digest_checked(self):
        data = json.loads(C_PASS.read_text()); data["decision_pack_manifest_sha256"] = "sha256:" + "0"*64
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"input.json"; manifest=Path(td)/"manifest.json"; path.write_text(json.dumps(data)); manifest.write_text("{}\n")
            with self.assertRaisesRegex(ValueError, "digest mismatch"): run_profile("ciso-ai-risk-v0.1", path, Path(td)/"out", manifest, EVAL)

    def test_handoff_evidence_extension_preserves_no_authority(self):
        handoff = json.loads((ROOT/"automation/fixtures/governance-decision-handoff.example.json").read_text())
        handoff["evidence_refs"].append("profile-result.json#sha256=" + "a"*64)
        schema_path=ROOT/"automation/contracts/governance-decision-handoff.schema.json"
        validate_instance(handoff, json.loads(schema_path.read_text()), base=schema_path.parent)
        self.assertEqual(handoff["authority_effect"], "NONE")

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_browser_viewer_reads_same_contract(self):
        _, output, _ = self.evaluate_profile("ciso-ai-risk-v0.1", C_PASS)
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"result.json"; path.write_text(json.dumps(output))
            completed=subprocess.run(["node", str(ROOT/"web/tests/profile-viewer-runner.mjs"), str(path)], cwd=ROOT, text=True, capture_output=True, check=True)
        view=json.loads(completed.stdout); self.assertTrue(view["profile"].startswith("ciso-ai-risk-v0.1")); self.assertIn("stop_condition", view["details"])

    def test_stable_contracts_remain_v1(self):
        for name in ("canonical-inventory-record.schema.json", "decision-pack-manifest.schema.json", "governance-findings.schema.json", "governance-result.schema.json", "normalized-inventory.schema.json"):
            self.assertTrue((ROOT/"automation/contracts/v1"/name).is_file())


if __name__ == "__main__": unittest.main()
