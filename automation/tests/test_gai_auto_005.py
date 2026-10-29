"""GAI-AUTO-005 must fire for Full autonomy after tier calculation."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "automation" / "scripts"))

from risk_tier_calculator import calculate_risk_tier  # type: ignore
from run_governance_checks import evaluate_row  # type: ignore


class Auto005Tests(unittest.TestCase):
    def test_full_autonomy_always_critical_or_frontier(self) -> None:
        low = {
            "autonomy_level": "Full",
            "public_facing": "No",
            "data_sensitivity": "None",
            "impact_safety": "No",
            "impact_security": "No",
            "impact_rights": "No",
            "impact_financial": "No",
        }
        self.assertEqual(calculate_risk_tier(low), "Critical")
        self.assertEqual(calculate_risk_tier({**low, "public_facing": "Yes"}), "Frontier")

    def test_rule_fires_for_full_after_tiering(self) -> None:
        row = {
            "system_id": "FULL-1",
            "system_name": "Full Agent",
            "owner": "Owner",
            "business_unit": "Ops",
            "vendor_internal": "Internal",
            "use_case": "Demo",
            "data_sensitivity": "Internal",
            "impact_people": "No",
            "impact_money": "No",
            "impact_security": "No",
            "impact_rights": "No",
            "impact_safety": "No",
            "autonomy_level": "Full",
            "public_facing": "No",
            "monitoring_active": "Yes",
            "shutdown_path_exists": "Yes",
            "evidence_complete": "Yes",
        }
        row["calculated_risk_tier"] = calculate_risk_tier(row)
        self.assertEqual(row["calculated_risk_tier"], "Critical")
        policy = json.loads(
            (ROOT / "automation/policy-as-code/governance-rules.yaml").read_text(encoding="utf-8")
        )
        findings = evaluate_row(row, policy["rules"])
        ids = {item.rule_id for item in findings}
        self.assertIn("GAI-AUTO-005", ids, findings)
        # Prior dead condition (Full + not Critical/Frontier) can never hold after calculator.
        self.assertNotIn(row["calculated_risk_tier"], {"Low", "Moderate", "High"})


if __name__ == "__main__":
    unittest.main()
