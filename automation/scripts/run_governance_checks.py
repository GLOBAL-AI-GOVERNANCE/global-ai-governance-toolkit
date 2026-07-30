#!/usr/bin/env python3
"""
Run governance checks.

Pipeline:
1. Validate inventory against the checked-in schema.
2. Calculate preliminary risk tiers.
3. Evaluate checked-in governance policy.
4. Generate an executive report.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Sequence


def run(command: Sequence[object]) -> None:
    rendered = [str(item) for item in command]
    print("+ " + " ".join(rendered), flush=True)

    completed = subprocess.run(rendered, check=False)

    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    automation_dir = script_dir.parent

    parser = argparse.ArgumentParser(
        description="Run the governance automation pipeline."
    )
    parser.add_argument(
        "input_csv",
        type=Path,
        help="Path to AI inventory CSV.",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        default=Path("automation/reports"),
        help="Output directory.",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=(
            automation_dir
            / "schemas"
            / "ai-system-inventory.schema.json"
        ),
        help="Path to the runtime inventory schema.",
    )
    parser.add_argument(
        "--policy",
        type=Path,
        default=(
            automation_dir
            / "policy-as-code"
            / "governance-rules.yaml"
        ),
        help="Path to the runtime governance policy.",
    )
    parser.add_argument(
        "--fail-on",
        choices=("none", "high", "critical"),
        default="critical",
        help=(
            "Return exit code 1 when governance findings meet "
            "or exceed the selected severity."
        ),
    )

    args = parser.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)

    schema_report = (
        args.outdir / "schema-validation-report.md"
    )
    tiered_csv = args.outdir / "risk-tier-output.csv"
    governance_report = (
        args.outdir / "governance-validation-report.md"
    )
    executive_report = (
        args.outdir / "executive-ai-governance-report.md"
    )

    run(
        [
            sys.executable,
            script_dir / "schema_validator.py",
            args.input_csv,
            "--schema",
            args.schema,
            "--report",
            schema_report,
        ]
    )

    run(
        [
            sys.executable,
            script_dir / "risk_tier_calculator.py",
            args.input_csv,
            "--output",
            tiered_csv,
        ]
    )

    run(
        [
            sys.executable,
            script_dir / "governance_validator.py",
            tiered_csv,
            "--report",
            governance_report,
            "--policy",
            args.policy,
            "--fail-on",
            args.fail_on,
        ]
    )

    run(
        [
            sys.executable,
            script_dir / "generate_governance_report.py",
            tiered_csv,
            "--output",
            executive_report,
        ]
    )

    print("\nGovernance automation complete.")
    print(f"- {schema_report}")
    print(f"- {tiered_csv}")
    print(f"- {governance_report}")
    print(f"- {executive_report}")


if __name__ == "__main__":
    main()
