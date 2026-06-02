#!/usr/bin/env python3
"""
Global AI Governance Solutions v1.2
Governance Validator

Validates AI inventory records against core governance requirements:
- owner
- monitoring
- shutdown path
- evidence for high-impact systems

This is a governance support tool, not a substitute for human review.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Dict, List


HIGH_TIERS = {"High", "Critical", "Frontier"}


def is_yes(value: str) -> bool:
    return str(value).strip().lower() == "yes"


def is_blank(value: str) -> bool:
    return str(value).strip() == ""


def validate_row(row: Dict[str, str]) -> List[str]:
    findings: List[str] = []

    system_name = row.get("system_name", "[unknown system]")
    risk_tier = row.get("calculated_risk_tier") or row.get("risk_tier") or ""

    if is_blank(row.get("owner", "")):
        findings.append(f"{system_name}: CRITICAL - Missing named owner. No owner, no deployment.")

    if not is_yes(row.get("monitoring_active", "")):
        findings.append(f"{system_name}: HIGH - Monitoring is not active.")

    if not is_yes(row.get("shutdown_path_exists", "")):
        findings.append(f"{system_name}: CRITICAL - Shutdown path is missing.")

    if risk_tier in HIGH_TIERS and not is_yes(row.get("evidence_complete", "")):
        findings.append(f"{system_name}: HIGH - Evidence incomplete for {risk_tier} system.")

    if row.get("autonomy_level", "").strip() == "Full" and risk_tier not in {"Critical", "Frontier"}:
        findings.append(f"{system_name}: HIGH - Full autonomy requires Critical or Frontier review.")

    return findings


def validate_csv(input_path: Path, report_path: Path) -> None:
    with input_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    findings: List[str] = []
    for row in rows:
        findings.extend(validate_row(row))

    if not findings:
        report = "# Governance Validation Report\n\nNo governance gaps found.\n"
    else:
        report = "# Governance Validation Report\n\n"
        report += "## Findings\n\n"
        for finding in findings:
            report += f"- {finding}\n"

    report_path.write_text(report, encoding="utf-8")
    print(f"Governance validation complete: {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate AI inventory records against core governance rules.")
    parser.add_argument("input_csv", type=Path, help="Path to AI inventory CSV.")
    parser.add_argument("--report", "-r", type=Path, default=Path("governance-validation-report.md"), help="Output report path.")
    args = parser.parse_args()

    validate_csv(args.input_csv, args.report)


if __name__ == "__main__":
    main()
