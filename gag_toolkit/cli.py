"""Installed ``gag`` command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from automation.scripts.contract_verifier import verify_output_directory
from automation.scripts.inventory_normalizer import normalize_file
from automation.scripts.run_governance_checks import run_pipeline
from automation.scripts.run_profile import run_profile

from . import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gag",
        description="Local-first Global AI Governance reference CLI.",
    )
    parser.add_argument("--version", action="version", version=__version__)
    commands = parser.add_subparsers(dest="command", required=True)

    normalize = commands.add_parser(
        "normalize",
        help="Normalize a supported inventory CSV to canonical JSON and CSV.",
    )
    normalize.add_argument("input_csv", type=Path)
    normalize.add_argument("--output-json", type=Path, required=True)
    normalize.add_argument("--output-csv", type=Path)

    check = commands.add_parser(
        "check",
        help="Run normalization, governance checks, Decision Pack, and handoff.",
    )
    check.add_argument("input_csv", type=Path)
    check.add_argument("--outdir", type=Path, required=True)
    check.add_argument(
        "--fail-on",
        choices=("none", "high", "critical"),
        default="critical",
    )
    check.add_argument("--evaluation-time")
    check.add_argument(
        "--target-repository",
        default="agentic-ai-governance",
    )

    verify = commands.add_parser(
        "verify",
        help="Verify machine contracts and Decision Pack integrity.",
    )
    verify.add_argument("output_directory", type=Path)
    profile = commands.add_parser("profile", help="Run an optional non-authorizing assurance/accountability profile.")
    profile.add_argument("profile_id")
    profile.add_argument("input", type=Path)
    profile.add_argument("--outdir", type=Path, required=True)
    profile.add_argument("--decision-pack-manifest", type=Path)
    profile.add_argument("--evaluation-time")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    try:
        if args.command == "normalize":
            normalize_file(
                args.input_csv,
                args.output_json,
                args.output_csv,
            )
        elif args.command == "check":
            run_pipeline(
                args.input_csv,
                args.outdir,
                fail_on=args.fail_on,
                evaluation_time=args.evaluation_time,
                target_repository=args.target_repository,
            )
        elif args.command == "profile":
            code, _ = run_profile(args.profile_id, args.input, args.outdir, args.decision_pack_manifest, args.evaluation_time)
            raise SystemExit(code)
        else:
            verify_output_directory(args.output_directory)
    except (OSError, ValueError) as exc:
        print(f"gag: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
