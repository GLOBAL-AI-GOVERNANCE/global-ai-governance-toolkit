"""Tests for the organizational AI maturity evidence profile."""

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from automation.profiles.common import canonical_bytes
from automation.profiles.organizational_ai_maturity import CATALOG_PATH, evaluate, load_catalog
from automation.scripts.contract_verifier import validate_instance
from automation.scripts.run_profile import MODULES, run_profile

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "profiles" / "fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class TestOrganizationalAIMaturity(unittest.TestCase):
    def test_supported_but_level_undetermined(self):
        data = load("maturity-supported.json")
        findings, evidence, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        cats = details["categories"]
        self.assertEqual(len(cats), 1)
        cat = cats[0]
        self.assertEqual(cat["claimed_level"], "DYNAMIC")
        self.assertIsNone(cat["evidence_supported_level"])
        self.assertEqual(cat["level_support_state"], "NOT_DETERMINED")
        self.assertEqual(cat["support_status"], "SUPPORTED")
        self.assertEqual(details["human_determination"], "PENDING")
        self.assertEqual(details["authority_effect"], "NONE")
        self.assertEqual(details["overall_synthesis"], "PENDING_HUMAN_SYNTHESIS")

    def test_multi_category_all_evaluated(self):
        data = load("maturity-supported.json")
        # add second adverse category
        data["categories"].append({
            "pillar_id": "people-culture",
            "category_id": "people-culture.ai-literacy-awareness",
            "claimed_level": "ADVANCED",
            "evidence": [],
        })
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertEqual(len(details["categories"]), 2)
        self.assertEqual(details["categories"][1]["support_status"], "UNSUPPORTED")

    def test_policy_only_overclaim(self):
        data = load("maturity-policy-only-overclaim.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("POLICY_ONLY_OVERCLAIM") for f in findings))
        self.assertEqual(details["categories"][0]["support_status"], "PARTIAL")

    def test_scope_mismatch(self):
        data = load("maturity-scope-mismatch.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("SCOPE_MISMATCH") for f in findings))
        self.assertEqual(details["categories"][0]["support_status"], "UNSUPPORTED")

    def test_stale_and_reassessment(self):
        data = load("maturity-stale.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("STALE") for f in findings))
        self.assertEqual(details["categories"][0]["freshness_status"], "STALE")
        self.assertEqual(details["categories"][0]["assessment_state"], "REASSESSMENT_REQUIRED")

    def test_synthetic_misuse(self):
        data = load("maturity-synthetic-evidence-misuse.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("SYNTHETIC_MISUSE") for f in findings))

    def test_contradicted_preserved_with_stale(self):
        data = load("maturity-contradicted.json")
        data["categories"][0]["evidence"][0]["valid_through"] = "2025-01-01T00:00:00Z"
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("CONTRADICTED") for f in findings))
        cat = details["categories"][0]
        self.assertEqual(cat["support_status"], "CONTRADICTED")
        self.assertEqual(cat["freshness_status"], "STALE")

    def test_unsupported_missing_evidence(self):
        data = load("maturity-unsupported.json")
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("MISSING_EVIDENCE") for f in findings))
        self.assertEqual(details["categories"][0]["support_status"], "UNSUPPORTED")

    def test_configured_trigger_alone_does_not_reassess(self):
        data = load("maturity-reassessment-required.json")
        # only triggers, no material_change_events
        data["categories"][0]["material_change_events"] = []
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertFalse(any(f["id"].endswith("REASSESSMENT_REQUIRED") for f in findings))
        self.assertEqual(details["categories"][0]["assessment_state"], "CURRENT")

    def test_observed_material_change_does_reassess(self):
        data = load("maturity-reassessment-required.json")
        data["categories"][0]["material_change_events"] = ["provider-change"]
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("REASSESSMENT_REQUIRED") for f in findings))
        self.assertEqual(details["categories"][0]["assessment_state"], "REASSESSMENT_REQUIRED")

    def test_wrong_framework_version_rejected(self):
        data = load("maturity-supported.json")
        data["framework_version"] = "2024"
        findings, _, _ = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("FRAMEWORK_VERSION") for f in findings))

    def test_time_with_offset(self):
        data = load("maturity-stale.json")
        data["categories"][0]["evidence"][0]["valid_through"] = "2025-01-01T00:00:00+00:00"
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00+00:00")
        self.assertTrue(any(f["id"].endswith("STALE") for f in findings))
        data["categories"][0]["evidence"][0]["valid_through"] = "2026-10-01T00:00:00Z"
        data["categories"][0]["evidence"][0]["is_representative"] = True
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertFalse(any(item["id"].endswith("STALE") for item in findings))
        self.assertEqual(details["categories"][0]["freshness_status"], "CURRENT")
        data["categories"][0]["evidence"][0]["valid_through"] = "not-a-time"
        findings, _, _ = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(item["id"].endswith("INVALID_TIME") for item in findings))

    def test_non_representative_operating(self):
        data = load("maturity-supported.json")
        data["categories"][0]["evidence"][0]["is_representative"] = False
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(f["id"].endswith("NON_REPRESENTATIVE") for f in findings))
        self.assertEqual(details["categories"][0]["support_status"], "PARTIAL")

    def test_no_authority_transfer(self):
        data = load("maturity-supported.json")
        _, _, details = evaluate(data, ROOT)
        self.assertEqual(details["authority_effect"], "NONE")
        self.assertEqual(details["human_determination"], "PENDING")


def accepted(level="DYNAMIC", status="ACCEPTED", conditions=None):
    item = {
        "level": level,
        "status": status,
        "accountable_role": "assurance-function",
        "determined_at": "2026-09-15T00:00:00Z",
        "basis_references": ["record:governance-review"],
    }
    if conditions is not None:
        item["conditions"] = conditions
    return item


class TestMaturitySemantics(unittest.TestCase):
    def test_catalog_shape(self):
        catalog = load_catalog()["raw"]
        labels = [category["label"] for pillar in catalog["pillars"] for category in pillar["categories"]]
        ids = [category["id"] for pillar in catalog["pillars"] for category in pillar["categories"]]
        self.assertEqual(len(catalog["pillars"]), 6)
        self.assertEqual(len(labels), 29)
        self.assertEqual(len(set(ids)), 29)
        self.assertEqual(catalog["levels"], ["BASIC", "READY", "DYNAMIC", "ADVANCED"])
        self.assertIn("Model Deployment & Management (MLOps)", labels)
        self.assertIn("Data Readiness for AI", labels)
        self.assertNotIn("Basic –", json.dumps(catalog))

    def test_unknown_pillar_category_mismatch_and_duplicate(self):
        data = load("maturity-supported.json")
        data["categories"][0]["pillar_id"] = "not-a-pillar"
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(item["id"].endswith("UNKNOWN_PILLAR") for item in findings))
        self.assertEqual(details["categories"], [])

        data = load("maturity-supported.json")
        data["categories"][0]["category_id"] = "not-a-category"
        findings, _, _ = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(item["id"].endswith("UNKNOWN_CATEGORY") for item in findings))

        data = load("maturity-supported.json")
        data["categories"][0]["pillar_id"] = "people-culture"
        findings, _, _ = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(item["id"].endswith("CATEGORY_PILLAR_MISMATCH") for item in findings))

        data = load("maturity-supported.json")
        data["categories"].append(json.loads(json.dumps(data["categories"][0])))
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(item["id"].endswith("DUPLICATE_CATEGORY") for item in findings))
        self.assertEqual(len(details["categories"]), 1)

    def test_partial_and_full_coverage(self):
        data = load("maturity-supported.json")
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertEqual(details["coverage_status"], "PARTIAL")
        self.assertEqual(details["framework_category_count"], 29)
        self.assertEqual(details["assessed_category_count"], 1)
        self.assertEqual(len(details["missing_category_ids"]), 28)
        self.assertNotIn("organizational maturity", json.dumps(details).lower())

        catalog = load_catalog()["raw"]
        data["assessment_coverage"] = "FULL_FRAMEWORK"
        data["categories"] = [
            {
                "pillar_id": pillar["id"],
                "category_id": category["id"],
                "claimed_level": "BASIC",
                "evidence": [],
            }
            for pillar in catalog["pillars"]
            for category in pillar["categories"]
        ]
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertFalse(any(item["id"].endswith("COVERAGE_INCOMPLETE") for item in findings))
        self.assertEqual(details["coverage_status"], "COMPLETE")
        self.assertEqual(details["missing_category_ids"], [])
        data["categories"].pop()
        findings, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertTrue(any(item["id"].endswith("COVERAGE_INCOMPLETE") for item in findings))
        self.assertEqual(details["coverage_status"], "INCOMPLETE")

    def test_human_determination_gates(self):
        data = load("maturity-supported.json")
        data["categories"][0]["human_determination"] = accepted(status="PENDING")
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertIsNone(details["categories"][0]["evidence_supported_level"])
        self.assertEqual(details["categories"][0]["level_support_state"], "NOT_DETERMINED")

        for status in ("REJECTED", "RETURNED_FOR_REASSESSMENT"):
            data["categories"][0]["human_determination"] = accepted(status=status)
            _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
            self.assertIsNone(details["categories"][0]["evidence_supported_level"])
            self.assertIsNone(details["categories"][0]["human_determined_level"])

        data["categories"][0]["human_determination"] = accepted(level="READY")
        data["categories"][0]["claimed_level"] = "DYNAMIC"
        data["categories"][0]["target_level"] = "ADVANCED"
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        cat = details["categories"][0]
        self.assertEqual(cat["evidence_supported_level"], "READY")
        self.assertEqual(cat["human_determined_level"], "READY")
        self.assertEqual(cat["claimed_level"], "DYNAMIC")
        self.assertEqual(cat["target_level"], "ADVANCED")
        self.assertEqual(cat["level_support_state"], "HUMAN_DETERMINATION_SUPPORTED")
        self.assertEqual(cat["authority_effect"], "NONE")
        self.assertEqual(details["overall_synthesis"], "PENDING_HUMAN_SYNTHESIS")

    def test_accepted_blocked_by_evidence_defects(self):
        data = load("maturity-stale.json")
        data["categories"][0]["evidence"][0]["is_representative"] = True
        data["categories"][0]["human_determination"] = accepted()
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertIsNone(details["categories"][0]["evidence_supported_level"])
        self.assertEqual(details["categories"][0]["level_support_state"], "EVIDENCE_STALE")

        data = load("maturity-contradicted.json")
        data["categories"][0]["human_determination"] = accepted()
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertEqual(details["categories"][0]["level_support_state"], "EVIDENCE_CONTRADICTED")
        self.assertIsNone(details["categories"][0]["evidence_supported_level"])

        data = load("maturity-supported.json")
        data["categories"][0]["material_change_events"] = ["provider-change"]
        data["categories"][0]["human_determination"] = accepted()
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertIsNone(details["categories"][0]["evidence_supported_level"])
        self.assertEqual(details["categories"][0]["assessment_state"], "REASSESSMENT_REQUIRED")

        data = load("maturity-synthetic-evidence-misuse.json")
        data["categories"][0]["human_determination"] = accepted()
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertIsNone(details["categories"][0]["evidence_supported_level"])

        data = load("maturity-scope-mismatch.json")
        data["categories"][0]["human_determination"] = accepted()
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertIsNone(details["categories"][0]["evidence_supported_level"])

        data = load("maturity-supported.json")
        data["categories"][0]["evidence"][0]["is_representative"] = False
        data["categories"][0]["human_determination"] = accepted()
        _, _, details = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertIsNone(details["categories"][0]["evidence_supported_level"])
        self.assertEqual(details["categories"][0]["level_support_state"], "EVIDENCE_INSUFFICIENT")

    def test_conditions_and_replay(self):
        data = load("maturity-supported.json")
        data["categories"][0]["human_determination"] = accepted(
            status="ACCEPTED_WITH_CONDITIONS", conditions=["recheck after the next operating cycle"]
        )
        _, _, first = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        _, _, second = evaluate(data, ROOT, "2026-10-01T00:00:00Z")
        self.assertEqual(first["categories"][0]["conditions"], ["recheck after the next operating cycle"])
        self.assertEqual(first["categories"][0]["evidence_supported_level"], "DYNAMIC")
        self.assertEqual(canonical_bytes(first), canonical_bytes(second))
        self.assertNotIn("urlopen", Path(evaluate.__code__.co_filename).read_text(encoding="utf-8"))

    def test_registration_and_browser_parity(self):
        registry = json.loads((ROOT / "profiles" / "registry.json").read_text(encoding="utf-8"))
        self.assertIn("organizational-ai-maturity-v0.1", {item["id"] for item in registry["profiles"]})
        self.assertEqual(MODULES["organizational-ai-maturity-v0.1"], "automation.profiles.organizational_ai_maturity")
        data = load("maturity-supported.json")
        schema = json.loads((ROOT / "contracts" / "profiles" / "organizational-ai-maturity.schema.json").read_text(encoding="utf-8"))
        catalog = load_catalog()["raw"]
        self.assertEqual(schema["properties"]["categories"]["items"]["properties"]["category_id"]["enum"], [category["id"] for pillar in catalog["pillars"] for category in pillar["categories"]])
        validate_instance(data, schema, base=ROOT / "contracts" / "profiles")
        broken = json.loads(json.dumps(data))
        broken["categories"][0]["category_id"] = "not-a-category"
        with tempfile.TemporaryDirectory() as tmp:
            bad = Path(tmp) / "bad.json"
            bad.write_text(json.dumps(broken), encoding="utf-8")
            with self.assertRaises(ValueError) as caught:
                run_profile("organizational-ai-maturity-v0.1", bad, Path(tmp) / "out", evaluation_time="2026-10-01T00:00:00Z")
            self.assertIn("input fails registered schema", str(caught.exception))
            source = Path(tmp) / "input.json"
            source.write_text(json.dumps(data), encoding="utf-8")
            completed = subprocess.run(
                ["python3", "-B", "automation/scripts/run_profile.py", "organizational-ai-maturity-v0.1", str(source), "--outdir", str(Path(tmp) / "cli"), "--evaluation-time", "2026-10-01T00:00:00Z"],
                cwd=ROOT.parent, text=True, capture_output=True, check=False,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            output = json.loads((Path(tmp) / "cli" / "profile-result.json").read_text(encoding="utf-8"))
        result_schema = json.loads((ROOT.parent / "automation" / "contracts" / "v1" / "profile-result.schema.json").read_text(encoding="utf-8"))
        validate_instance(output, result_schema, base=ROOT.parent / "automation" / "contracts" / "v1")
        self.assertEqual(output["authority_effect"], "NONE")
        self.assertEqual(output["details"]["overall_synthesis"], "PENDING_HUMAN_SYNTHESIS")
        keys = ["category_id", "claimed_level", "target_level", "human_determined_level", "evidence_supported_level", "level_support_state", "support_status", "freshness_status", "assessment_state", "confidence", "contradictions", "conditions"]
        page = (ROOT.parent / "web/maturity/index.html").read_text(encoding="utf-8")
        style = (ROOT.parent / "web/maturity/styles.css").read_text(encoding="utf-8")
        self.assertIn("<label>", page)
        self.assertIn("aria-live", page)
        self.assertIn(":focus-visible", style)
        self.assertIn("prefers-reduced-motion", style)
        for fixture in sorted((ROOT / "profiles" / "fixtures").glob("maturity-*.json")):
            _, _, details = evaluate(json.loads(fixture.read_text(encoding="utf-8")), ROOT, "2026-10-01T00:00:00Z")
            browser_run = subprocess.run(
                ["node", str(ROOT / "tests" / "run_maturity_parity.mjs"), str(fixture), "2026-10-01T00:00:00Z"],
                cwd=ROOT.parent, text=True, capture_output=True, check=False,
            )
            self.assertEqual(browser_run.returncode, 0, browser_run.stderr)
            browser = json.loads(browser_run.stdout)
            self.assertEqual(browser["missing_category_ids"], details["missing_category_ids"])
            self.assertEqual(browser["authority_effect"], "NONE")
            self.assertEqual(
                [{key: item.get(key) for key in keys} for item in browser["categories"]],
                [{key: item.get(key) for key in keys} for item in details["categories"]],
                fixture.name,
            )


if __name__ == "__main__":
    unittest.main()


