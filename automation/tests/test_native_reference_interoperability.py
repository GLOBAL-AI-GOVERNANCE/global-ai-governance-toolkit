from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "automation" / "interoperability" / "native_reference.py"
SPEC = importlib.util.spec_from_file_location("native_reference_candidate", MODULE_PATH)
assert SPEC and SPEC.loader
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)
FIXTURE = ROOT / "automation" / "fixtures" / "native-reference-envelope.example.json"


class NativeReferenceInteroperabilityTests(unittest.TestCase):
    def refs(self):
        subject = "system.synthetic.001"
        when = "2026-10-14T12:00:00Z"
        values = [
            MOD.build_native_reference(
                source_repository="GLOBAL-AI-GOVERNANCE/agentic-ai-governance",
                artifact_type="agent-trust-passport",
                artifact_id="sha256:3bff2559b8dba5091534959df0c587a94873703dd4ee735da9ce7842e57908e7",
                schema_version="0.1.0-alpha.1",
                subject_id=subject,
                artifact_digest="sha256:51d3e06011e72a85ad14c3f888b42fe34a3b6aca24d58fdec71dd26561c39297",
                generated_at=when,
            ),
            MOD.build_native_reference(
                source_repository="GLOBAL-AI-GOVERNANCE/verified-vulnerability-governance",
                artifact_type="governed-closure-receipt",
                artifact_id="finding-synthetic-001",
                schema_version="1.0.0",
                subject_id=subject,
                artifact_digest="sha256:e0c243f8f4dc302c6315d5bff558c4ae7593bbdf7642b7a669cbd5790dbfc247",
                generated_at=when,
            ),
            MOD.build_native_reference(
                source_repository="GLOBAL-AI-GOVERNANCE/ai-cyber-resilience-framework",
                artifact_type="change-impact",
                artifact_id="change-synthetic-001",
                schema_version="1.0.0",
                subject_id=subject,
                artifact_digest="sha256:7a27441209ffbdfc06e023a51d28870433bdcce25df9f7730a44fb999daa9dd9",
                generated_at=when,
            ),
            MOD.build_native_reference(
                source_repository="GLOBAL-AI-GOVERNANCE/ai-cyber-resilience-framework",
                artifact_type="operating-disposition",
                artifact_id="disposition-synthetic-001",
                schema_version="1.0.0",
                subject_id=subject,
                artifact_digest="sha256:1184dc814d92adf870e0c944bf7529270b46fe1ac44a8e272c5f5d634795325f",
                generated_at=when,
            ),
        ]
        return subject, values

    def test_fixture_matches_deterministic_composition(self):
        subject, refs = self.refs()
        actual = MOD.compose_reference_envelope(subject, reversed(refs))
        expected = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(actual, expected)

    def test_authority_transfer_fails_closed(self):
        subject, refs = self.refs()
        refs[0]["authority_effect"] = "GRANT"
        with self.assertRaisesRegex(ValueError, "authority"):
            MOD.compose_reference_envelope(subject, refs)

    def test_owner_mismatch_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "ownership"):
            MOD.build_native_reference(
                source_repository="GLOBAL-AI-GOVERNANCE/global-ai-governance-toolkit",
                artifact_type="agent-trust-passport",
                artifact_id="synthetic",
                schema_version="0.1.0-alpha.1",
                subject_id="system.synthetic.001",
                artifact_digest="sha256:" + "0" * 64,
                generated_at="2026-10-14T12:00:00Z",
            )

    def test_subject_mismatch_fails_closed(self):
        subject, refs = self.refs()
        refs[0]["subject_id"] = "other.subject"
        with self.assertRaisesRegex(ValueError, "subject binding"):
            MOD.compose_reference_envelope(subject, refs)

    def test_duplicate_reference_fails_closed(self):
        subject, refs = self.refs()
        with self.assertRaisesRegex(ValueError, "duplicate"):
            MOD.compose_reference_envelope(subject, refs + [dict(refs[0])])

    def test_contract_keys_are_exact(self):
        _, refs = self.refs()
        self.assertEqual(set(refs[0]), MOD.REFERENCE_KEYS)
        self.assertEqual(refs[0]["authority_effect"], "NONE")


if __name__ == "__main__":
    unittest.main()
