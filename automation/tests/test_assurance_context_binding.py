"""Positive and negative tests for the Assurance Context Binding local consumer.

Uses standard-library unittest so the existing CI discovery command can run them.
"""
from __future__ import annotations

import json
import unittest

from automation.interoperability.assurance_context_binding import validate_assurance_context_binding
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
    "invalidation_triggers": [
        "configuration change",
        "evidence source change",
        "context boundary change",
    ],
    "reference_only": True,
    "authority_effect": "NONE",
}
# Exact schema content from ai-governance-os @ fad094618e723acec14a8cdc905d1cfcbdf58813
SCHEMA = {
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
        "invalidation_triggers": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "string", "minLength": 1},
        },
        "reference_only": {"type": "boolean", "const": True},
        "authority_effect": {"type": "string", "const": "NONE"},
    },
    "required": [
        "binding_id",
        "subject_id",
        "configuration_digest",
        "context_boundary",
        "evidence_provenance",
        "validity_from",
        "invalidation_triggers",
        "reference_only",
        "authority_effect",
    ],
    "additionalProperties": False,
}


class AssuranceContextBindingTests(unittest.TestCase):
    def _call(self, portfolio_ref, binding, schema=SCHEMA):
        return validate_assurance_context_binding(
            portfolio_ref,
            binding,
            schema,
            expected_subject_id="synthetic-system-alpha",
            expected_configuration_digest=BINDING["configuration_digest"],
            expected_context_boundary=BINDING["context_boundary"],
        )

    def test_positive_validates(self) -> None:
        result = self._call(PORTFOLIO_REF, BINDING)
        self.assertTrue(result["valid"])
        self.assertEqual(result["authority_effect"], "NONE")
        self.assertTrue(result["reference_only"])

    def test_negative_portfolio_reference_cases(self) -> None:
        cases = [
            (lambda d: d.update({"source_repository": "other"}), "wrong source"),
            (lambda d: d.update({"target_repository": "other"}), "wrong target"),
            (lambda d: d.update({"handoff_id": "wrong"}), "wrong handoff"),
            (lambda d: d.update({"source_version": "wrong"}), "wrong commit"),
            (lambda d: d.pop("source_artifact_id", None), "missing field"),
            (lambda d: d.update({"extra": "bad"}), "unsupported field"),
            (lambda d: d.update({"reference_only": False}), "false reference_only"),
            (lambda d: d.update({"authority_effect": "AUTHORIZE"}), "non-NONE authority"),
            (lambda d: d.update({"schema_version": "2.0.0"}), "schema version mismatch"),
            (lambda d: d.update({"source_artifact_type": "wrong"}), "wrong artifact type"),
        ]
        for mutator, label in cases:
            with self.subTest(label=label):
                bad = json.loads(json.dumps(PORTFOLIO_REF))
                mutator(bad)
                with self.assertRaises(ContractError):
                    self._call(bad, BINDING)

    def test_negative_binding_fixture_cases(self) -> None:
        cases = [
            (lambda d: d.update({"subject_id": "wrong"}), "incorrect subject"),
            (lambda d: d.update({"configuration_digest": "sha256:" + "0" * 64}), "digest mismatch"),
            (lambda d: d.update({"context_boundary": "wrong"}), "context mismatch"),
            (lambda d: d.update({"configuration_digest": "not-a-digest"}), "malformed digest"),
            (lambda d: d.update({"reference_only": False}), "false reference_only"),
            (lambda d: d.update({"authority_effect": "AUTHORIZE"}), "non-NONE authority"),
            (lambda d: d.pop("evidence_provenance", None), "missing provenance"),
            (lambda d: d.update({"extra": "bad"}), "unsupported field"),
        ]
        for mutator, label in cases:
            with self.subTest(label=label):
                bad = json.loads(json.dumps(BINDING))
                mutator(bad)
                with self.assertRaises(ContractError):
                    self._call(PORTFOLIO_REF, bad)

    def test_negative_schema_fingerprint_cases(self) -> None:
        cases = [
            ({}, "empty schema"),
            ({"type": "object"}, "minimal schema"),
            (dict(SCHEMA, required=[k for k in SCHEMA["required"] if k != "evidence_provenance"]), "removed provenance requirement"),
            (dict(SCHEMA, properties={**SCHEMA["properties"], "authority_effect": {"type": "string"}}), "weakened authority constant"),
        ]
        for bad_schema, label in cases:
            with self.subTest(label=label):
                with self.assertRaises(ContractError):
                    self._call(PORTFOLIO_REF, BINDING, schema=bad_schema)


if __name__ == "__main__":
    unittest.main()
