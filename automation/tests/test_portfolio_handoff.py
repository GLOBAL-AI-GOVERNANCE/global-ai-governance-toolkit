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

    def test_current_docs_do_not_repeat_known_false_state(self) -> None:
        roots = [
            ROOT / "README.md",
            ROOT / "PORTFOLIO_INTEROP.md",
            ROOT / "automation" / "README.md",
            ROOT / "docs" / "ORGANIZATIONAL_AI_MATURITY_EVIDENCE.md",
            ROOT / "docs" / "internal-current-main-auditable-ai-1.0-readiness.md",
            ROOT / "automation" / "profiles" / "quantum_ai.py",
            ROOT / "automation" / "assurance" / "quantum-ai",
        ]
        banned = (
            "The profile is not registered.",
            '"publication_status":"CURRENT_MAIN_DEVELOPMENT"',
            "The published Toolkit release remains the v2.3.0 tag.",
        )
        chunks = []
        for path in roots:
            if path.is_dir():
                chunks.extend(item.read_text(encoding="utf-8") for item in path.rglob("*") if item.is_file())
            else:
                chunks.append(path.read_text(encoding="utf-8"))
        text = "\n".join(chunks)
        for phrase in banned:
            self.assertNotIn(phrase, text)
        self.assertIn("## Organizational maturity evidence", (ROOT / "PORTFOLIO_INTEROP.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
