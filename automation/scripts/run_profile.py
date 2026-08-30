#!/usr/bin/env python3
"""Registry-backed optional profile CLI."""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from automation.profiles.common import canonical_bytes, result

MODULES = {"auditable-ai-v1": "automation.profiles.auditable_ai", "quantum-ai-convergence-v0.1": "automation.profiles.quantum_ai", "ciso-ai-risk-v0.1": "automation.profiles.ciso_ai_risk"}


def digest(raw: bytes) -> str:
    return "sha256:" + hashlib.sha256(raw).hexdigest()


def run_profile(profile_id: str, input_path: Path, outdir: Path, manifest_path: Path | None = None, evaluation_time: str | None = None) -> tuple[int, dict[str, object]]:
    if profile_id not in MODULES:
        raise ValueError(f"Unknown profile id: {profile_id}")
    if evaluation_time is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", evaluation_time):
        raise ValueError("evaluation time must use YYYY-MM-DDTHH:MM:SSZ")
    raw = input_path.read_bytes()
    try: data = json.loads(raw)
    except json.JSONDecodeError as exc: raise ValueError(f"input is not valid JSON: {exc}") from exc
    if not isinstance(data, dict): raise ValueError("profile input root must be an object")
    manifest = None
    if manifest_path:
        manifest_raw = manifest_path.read_bytes()
        manifest_data = json.loads(manifest_raw)
        if not isinstance(manifest_data, dict): raise ValueError("Decision Pack manifest must be an object")
        expected = data.get("decision_pack_manifest_sha256")
        actual = digest(manifest_raw)
        if expected is not None and expected != actual: raise ValueError("Decision Pack manifest digest mismatch")
        manifest = {"reference": str(manifest_path), "sha256": actual}
    module = importlib.import_module(MODULES[profile_id])
    findings, evidence, details = module.evaluate(data, input_path.parent, evaluation_time)
    output = result(profile_id, module.VERSION, digest(raw), evaluation_time, findings, evidence, details, manifest)
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "profile-result.json").write_bytes(canonical_bytes(output))
    return (1 if output["status"] == "FAIL" else 0), output


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run an optional non-authorizing governance profile.")
    parser.add_argument("profile_id"); parser.add_argument("input", type=Path); parser.add_argument("--outdir", type=Path, required=True)
    parser.add_argument("--decision-pack-manifest", type=Path); parser.add_argument("--evaluation-time")
    args = parser.parse_args(argv)
    try: code, _ = run_profile(args.profile_id, args.input, args.outdir, args.decision_pack_manifest, args.evaluation_time)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"gag profile: {exc}"); raise SystemExit(2) from exc
    raise SystemExit(code)


if __name__ == "__main__": main()
