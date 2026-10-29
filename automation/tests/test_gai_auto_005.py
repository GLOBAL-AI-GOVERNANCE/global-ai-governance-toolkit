"""GAI-AUTO-005: characterize the dead prior condition, then assert the restored rule."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "automation" / "scripts"))

from risk_tier_calculator import calculate_risk_tier  # type: ignore
from run_governance_checks import evaluate_row  # type: ignore


FULL_LOW_IMPACT = {
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


def _matches(rule: dict, row: dict) -> bool:
    """Minimal all/any matcher mirroring the dead historical condition shape."""
    clauses = rule.get("all") or []
    for clause in clauses:
        field = clause["field"]
        op = clause["operator"]
        value = row.get(field)
        if op == "equals" and value != clause.get("value"):
            return False
        if op == "not_in" and value in clause.get("values", []):
            return False
        if op == "in" and value not in clause.get("values", []):
            return False
    return True


class Auto005Tests(unittest.TestCase):
    def test_characterization_prior_not_in_tier_condition_unreachable(self) -> None:
        """Historical rule: Full AND calculated_risk_tier not_in [Critical, Frontier].

        The calculator always maps Full autonomy to Critical or Frontier, so that
        compound condition can never hold. Keep this characterization even after
        restoration so a regression to the dead form fails loudly.
        """
        dead_rule = {
            "id": "GAI-AUTO-005-DEAD",
            "all": [
                {"field": "autonomy_level", "operator": "equals", "value": "Full"},
                {
                    "field": "calculated_risk_tier",
                    "operator": "not_in",
                    "values": ["Critical", "Frontier"],
                },
            ],
        }
        for public in ("No", "Yes"):
            row = {**FULL_LOW_IMPACT, "public_facing": public}
            row["calculated_risk_tier"] = calculate_risk_tier(row)
            self.assertIn(row["calculated_risk_tier"], {"Critical", "Frontier"})
            self.assertFalse(
                _matches(dead_rule, row),
                f"dead condition unexpectedly matched for tier={row['calculated_risk_tier']}",
            )

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

    def test_restored_rule_fires_on_full_autonomy(self) -> None:
        """Docs/policy: Full autonomy requires Critical or Frontier review.

        Intent is clear. Firing on autonomy_level Full (after calculator has already
        escalated the tier) is stricter and accurate: the finding flags Full autonomy
        for that review. The prior not_in-tier form was unreachable and weaker.
        """
        row = dict(FULL_LOW_IMPACT)
        row["calculated_risk_tier"] = calculate_risk_tier(row)
        self.assertEqual(row["calculated_risk_tier"], "Critical")
        policy = json.loads(
            (ROOT / "automation/policy-as-code/governance-rules.yaml").read_text(encoding="utf-8")
        )
        rule = next(item for item in policy["rules"] if item["id"] == "GAI-AUTO-005")
        self.assertEqual(rule["all"], [{"field": "autonomy_level", "operator": "equals", "value": "Full"}])
        findings = evaluate_row(row, policy["rules"])
        ids = {item.rule_id for item in findings}
        self.assertIn("GAI-AUTO-005", ids, findings)


if __name__ == "__main__":
    unittest.main()
