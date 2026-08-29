from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "automation" / "contracts" / "governance-decision-handoff.schema.json"
EXAMPLE = ROOT / "automation" / "fixtures" / "governance-decision-handoff.example.json"


class PortfolioHandoffTests(unittest.TestCase):
    def test_contract_is_reference_only_and_fail_bounded(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        example = json.loads(EXAMPLE.read_text(encoding="utf-8"))

        self.assertEqual(schema["properties"]["authority_effect"]["const"], "NONE")
        self.assertEqual(example["authority_effect"], "NONE")
        self.assertEqual(example["source_repository"], "global-ai-governance-toolkit")
        self.assertRegex(example["artifact_digest"], r"^sha256:[0-9a-f]{64}$")
        self.assertIn("human review", example["review_boundary"].lower())

    def test_example_has_exact_required_contract_keys(self) -> None:
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        example = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        required = set(schema["required"])
        self.assertTrue(required.issubset(example))
        self.assertTrue(set(example).issubset(schema["properties"]))

    def test_interop_document_does_not_claim_authority(self) -> None:
        text = (ROOT / "PORTFOLIO_INTEROP.md").read_text(encoding="utf-8")
        self.assertIn("authority_effect: NONE", text)
        self.assertIn("automatically emits", text)
        self.assertNotIn("automatically approves deployment", text.lower())


if __name__ == "__main__":
    unittest.main()
