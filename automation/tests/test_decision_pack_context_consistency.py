"""Positive and negative tests for Decision Pack / Assurance Context Binding consistency.

Uses standard-library unittest.
"""
from __future__ import annotations

import hashlib
import json
import unittest

from automation.interoperability.decision_pack_context_consistency import (
    validate_decision_pack_context_consistency,
)
from automation.scripts.contract_verifier import ContractError

PORTFOLIO_REF = {
    "schema_version": "1.0.0",
    "handoff_id": "foundation-to-toolkit",
    "source_repository": "ai-governance-os",
    "target_repository": "global-ai-governance-toolkit",
    "source_artifact_type": "Assurance Context Binding fixture",
    "source_artifact_id": "sample-data/assurance-context-binding.json",
    "source_version": "fad094618e723acec14a8cdc905d1cfcbdf58813",
    "reference_only": True,
    "authority_effect": "NONE",
}
BINDING = {
    "binding_id": "acb-example-001",
    "subject_id": "synthetic-system-alpha",
    "configuration_digest": "sha256:9c65e5fc67d0b78e02f25fdc181add45eb98c4c1bf8cf461a1709c534b980504",
    "context_boundary": "bounded synthetic evaluation environment",
    "evidence_provenance": {
        "source": "synthetic evaluation run",
        "timestamp": "2026-10-15T00:00:00Z",
        "digest": "sha256:7b0cf66aaf4a68d6cbff76ba5d02b3de81ee5a7cb103d65cb7c8ede037c03107",
    },
    "validity_from": "2026-10-15T00:00:00Z",
    "invalidation_triggers": ["configuration change"],
    "reference_only": True,
    "authority_effect": "NONE",
}
BINDING_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "assurance-context-binding.schema.json",
    "title": "Assurance Context Binding",
    "description": "Reference-only binding of subject, configuration, and evidence context. Authority effect remains NONE. Material change invalidates prior binding. Does not implement runtime detection.",
    "type": "object",
    "properties": {
        "binding_id": {"type": "string", "minLength": 1},
        "subject_id": {"type": "string", "minLength": 1},
        "configuration_digest": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
        "context_boundary": {"type": "string", "minLength": 1},
        "evidence_provenance": {
            "type": "object",
            "properties": {
                "source": {"type": "string", "minLength": 1},
                "timestamp": {"type": "string", "minLength": 1},
                "digest": {"type": "string", "pattern": "^sha256:[a-f0-9]{64}$"},
            },
            "required": ["source", "timestamp", "digest"],
            "additionalProperties": False,
        },
        "validity_from": {"type": "string", "minLength": 1},
        "invalidation_triggers": {"type": "array", "minItems": 1, "items": {"type": "string", "minLength": 1}},
        "reference_only": {"type": "boolean", "const": True},
        "authority_effect": {"type": "string", "const": "NONE"},
    },
    "required": [
        "binding_id", "subject_id", "configuration_digest", "context_boundary",
        "evidence_provenance", "validity_from", "invalidation_triggers",
        "reference_only", "authority_effect",
    ],
    "additionalProperties": False,
}
MANIFEST = b'{"synthetic": "decision-pack-manifest"}'
MANIFEST_DIGEST = "sha256:" + hashlib.sha256(MANIFEST).hexdigest()
HANDOFF = {
    "schema_version": "1.0.0",
    "handoff_id": "toolkit-to-agentic",
    "source_repository": "global-ai-governance-toolkit",
    "source_artifact_type": "AI_GOVERNANCE_DECISION_PACK_REFERENCE",
    "decision_pack_id": "dp-001",
    "system_id": "synthetic-system-alpha",
    "target_repository": "agentic-ai-governance",
    "artifact_digest": MANIFEST_DIGEST,
    "evidence_refs": ["finding-001"],
    "authority_refs": [],
    "authority_effect": "NONE",
    "review_boundary": "Human review required before any consequential action.",
    "configuration_ref": BINDING["configuration_digest"],
}
HANDOFF_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "schema_version": {"const": "1.0.0"},
        "handoff_id": {"type": "string", "minLength": 1},
        "source_repository": {"const": "global-ai-governance-toolkit"},
        "source_artifact_type": {"const": "AI_GOVERNANCE_DECISION_PACK_REFERENCE"},
        "decision_pack_id": {"type": "string", "minLength": 1},
        "system_id": {"type": "string", "minLength": 1},
        "target_repository": {"type": "string", "minLength": 1},
        "artifact_digest": {"type": "string", "pattern": "^sha256:[0-9a-f]{64}$"},
        "evidence_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
        "authority_refs": {"type": "array", "items": {"type": "string", "minLength": 1}, "uniqueItems": True},
        "authority_effect": {"const": "NONE"},
        "review_boundary": {"type": "string", "minLength": 1},
        "configuration_ref": {"type": ["string", "null"]},
    },
    "required": [
        "schema_version", "handoff_id", "source_repository", "source_artifact_type",
        "decision_pack_id", "system_id", "target_repository", "artifact_digest",
        "evidence_refs", "authority_refs", "authority_effect", "review_boundary",
    ],
}


class DecisionPackContextConsistencyTests(unittest.TestCase):
    def _call(self, handoff=HANDOFF, manifest=MANIFEST, portfolio=PORTFOLIO_REF, binding=BINDING, schema=BINDING_SCHEMA):
        return validate_decision_pack_context_consistency(
            handoff,
            HANDOFF_SCHEMA,
            manifest,
            portfolio,
            binding,
            schema,
            expected_subject_id="synthetic-system-alpha",
            expected_configuration_digest=BINDING["configuration_digest"],
            expected_context_boundary=BINDING["context_boundary"],
        )

    def test_positive_consistent(self) -> None:
        result = self._call()
        self.assertTrue(result["consistent"])
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertTrue(result["reference_only"])

    def test_negative_cases(self) -> None:
        cases = [
            (lambda: self._call(handoff={**HANDOFF, "system_id": "wrong"}), "wrong subject"),
            (lambda: self._call(handoff={**HANDOFF, "artifact_digest": "sha256:" + "0" * 64}), "mismatched digest"),
            (lambda: self._call(manifest=b"tampered"), "tampered manifest"),
            (lambda: self._call(portfolio={**PORTFOLIO_REF, "source_repository": "other"}), "wrong source"),
            (lambda: self._call(binding={**BINDING, "subject_id": "wrong"}), "binding subject mismatch"),
            (lambda: self._call(schema={}), "changed foundational schema"),
            (lambda: self._call(handoff={**HANDOFF, "authority_effect": "AUTHORIZE"}), "non-NONE authority"),
            (lambda: self._call(handoff={**HANDOFF, "extra": "bad"}), "unsupported field"),
        ]
        for caller, label in cases:
            with self.subTest(label=label):
                with self.assertRaises(ContractError):
                    caller()


if __name__ == "__main__":
    unittest.main()
