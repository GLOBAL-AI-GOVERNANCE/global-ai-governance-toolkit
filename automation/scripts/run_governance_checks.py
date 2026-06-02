#!/usr/bin/env python3
"""
Global AI Governance Solutions v1.2
Run Governance Checks

Pipeline:
1. Calculate risk tiers
2. Validate governance gaps
3. Generate executive report
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd):
    print("+ " + " ".join(str(c) for c in cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the v1.2 governance automation pipeline.")
    parser.add_argument("input_csv", type=Path, help="Path to AI inventory CSV.")
    parser.add_argument("--outdir", type=Path, default=Path("automation/reports"), help="Output directory.")
    args = parser.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)

    tiered_csv = args.outdir / "risk-tier-output.csv"
    validation_report = args.outdir / "governance-validation-report.md"
    executive_report = args.outdir / "executive-ai-governance-report.md"

    script_dir = Path(__file__).resolve().parent

    run([sys.executable, script_dir / "risk_tier_calculator.py", args.input_csv, "--output", tiered_csv])
    run([sys.executable, script_dir / "governance_validator.py", tiered_csv, "--report", validation_report])
    run([sys.executable, script_dir / "generate_governance_report.py", tiered_csv, "--output", executive_report])

    print("\nGovernance automation complete.")
    print(f"- {tiered_csv}")
    print(f"- {validation_report}")
    print(f"- {executive_report}")


if __name__ == "__main__":
    main()
