"""Offline validator for the synthetic mission-assurance challenge. No network."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
THREAD_PATH = ROOT / "automation/assurance/mission-assurance/challenge/golden-thread.json"
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
COMMIT = re.compile(r"^[a-f0-9]{40}$")
ALLOWED = {
    "ai-governance-os",
    "global-ai-governance-toolkit",
    "agentic-ai-governance",
    "governed-systems-administration",
    "verified-vulnerability-governance",
    "ai-cyber-resilience-framework",
    "peace-os",
}
REQUIRED_SCENARIOS = {
    "normal",
    "adversarial-failure",
    "dependency-failure",
    "recovery-failure",
    "succession-failure",
    "material-change",
    "initial-result-after-material-change",
}
REFERENCE_KEYS = {
    "reference_id",
    "source_repository",
    "source_commit",
    "artifact_path",
    "artifact_type",
    "artifact_digest",
    "authority_effect",
}
OPTIONAL_REFERENCE_KEYS = {"subject_id", "configuration_digest", "expected_outcome"}


class ChallengeError(Exception):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ChallengeError(message)


def validate_thread(thread: dict) -> dict:
    _require(isinstance(thread, dict), "thread must be an object")
    _require(thread.get("reference_only") is True, "reference_only must be true")
    _require(thread.get("authority_effect") == "NONE", "authority_effect must be NONE")
    _require(thread.get("synthetic") is True, "thread must be synthetic")
    _require(thread.get("automatic_requalification") is False, "automatic requalification is not permitted")
    _require(isinstance(thread.get("subject_id"), str) and thread["subject_id"].strip(), "subject_id required")
    _require(DIGEST.fullmatch(str(thread.get("configuration_digest", ""))), "configuration_digest malformed")
    scenarios = thread.get("scenarios")
    _require(isinstance(scenarios, list), "scenarios required")
    by_id = {}
    for item in scenarios:
        _require(isinstance(item, dict) and item.get("id"), "scenario id required")
        _require(item["id"] not in by_id, f"duplicate scenario {item['id']}")
        by_id[item["id"]] = item
        _require(item.get("expect") in {"PASS", "FAIL", "NOT_CURRENT"}, "unsupported scenario expectation")
    missing = REQUIRED_SCENARIOS - set(by_id)
    _require(not missing, f"missing scenarios: {', '.join(sorted(missing))}")
    _require(by_id["normal"]["expect"] == "PASS", "normal scenario must expect PASS")
    _require(by_id["material-change"].get("material_change") is True, "material change must invalidate current assurance")
    _require(by_id["material-change"]["expect"] == "FAIL", "material change must fail")
    _require(by_id["initial-result-after-material-change"]["expect"] == "NOT_CURRENT", "initial result must not stay current")
    references = thread.get("references")
    _require(isinstance(references, list) and references, "references required")
    seen = {}
    for ref in references:
        _require(isinstance(ref, dict), "reference must be an object")
        extra = set(ref) - REFERENCE_KEYS - OPTIONAL_REFERENCE_KEYS
        _require(not extra, f"unsupported reference fields: {', '.join(sorted(extra))}")
        _require(REFERENCE_KEYS <= set(ref), "reference is missing required fields")
        _require(ref["source_repository"] in ALLOWED, f"unsupported repository {ref['source_repository']}")
        _require(COMMIT.fullmatch(ref["source_commit"]), "source_commit must be 40 lowercase hex")
        _require(DIGEST.fullmatch(ref["artifact_digest"]), "artifact_digest malformed")
        _require(ref["authority_effect"] == "NONE", "reference cannot transfer authority")
        _require(isinstance(ref["artifact_path"], str) and ref["artifact_path"] and "://" not in ref["artifact_path"], "artifact_path required")
        if "subject_id" in ref:
            _require(isinstance(ref["subject_id"], str) and ref["subject_id"].strip(), "subject_id malformed")
        if "configuration_digest" in ref:
            _require(DIGEST.fullmatch(ref["configuration_digest"]), "reference configuration malformed")
        _require(ref["reference_id"] not in seen, "duplicate reference")
        seen[ref["reference_id"]] = ref
    dependency = by_id["dependency-failure"].get("native_reference")
    succession = by_id["succession-failure"].get("native_reference")
    _require(dependency in seen and seen[dependency]["artifact_path"].endswith("synthetic-exit-failed.json"), "dependency failure must name the native failed exit record")
    _require(succession in seen and seen[succession]["artifact_path"].endswith("succession-evidence-failed.json"), "succession failure must name the native failed succession record")
    _require(seen[dependency]["expected_outcome"] == "FAILED", "dependency failure cannot be PASS")
    _require(seen[succession]["expected_outcome"] == "FAILED", "succession failure cannot be PASS")
    return {"valid": True, "authority_effect": "NONE", "scenarios": len(scenarios), "references": len(references)}


def validate_thread_file(path: Path | None = None) -> dict:
    path = path or THREAD_PATH
    return validate_thread(json.loads(path.read_text(encoding="utf-8")))


def main() -> None:
    print(json.dumps(validate_thread_file(), sort_keys=True))


if __name__ == "__main__":
    main()
