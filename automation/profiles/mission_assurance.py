"""Mission Assurance interoperability profile.

Non-authorizing. Assembles submitted references only.
A PASS means the selected stage's structural checks passed.
It does not validate native source artifacts or authorize use.
"""
from __future__ import annotations

import re
from pathlib import Path

from .common import finding

PROFILE_ID = "mission-assurance-v0.1"
VERSION = "0.1.0"
DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
STAGES = ["G0", "G1", "G2", "G3", "G4", "G5", "G6", "G7", "G8"]
STAGE_INDEX = {stage: index for index, stage in enumerate(STAGES)}


def _critical(findings: list, code: str, message: str, action: str) -> None:
    findings.append(finding(PROFILE_ID, code, "CRITICAL", message, action))


def _bind(reference: dict, data: dict, findings: list, label: str) -> None:
    if not isinstance(reference, dict):
        _critical(findings, f"{label}_INVALID", f"{label} must be an evidence reference.", "Supply a complete evidence reference.")
        return
    if reference.get("authority_effect") != "NONE":
        _critical(findings, f"{label}_AUTHORITY", f"{label} cannot confer authority.", "Set authority_effect to NONE.")
    if reference.get("subject_id") != data.get("subject_id"):
        _critical(findings, f"{label}_SUBJECT", f"{label} subject does not match the mission subject.", "Bind the reference to the same subject.")
    if reference.get("configuration_digest") != data.get("configuration_digest"):
        _critical(findings, f"{label}_CONFIGURATION", f"{label} configuration does not match.", "Bind the reference to the same configuration.")
    if not DIGEST.fullmatch(str(reference.get("artifact_digest", ""))):
        _critical(findings, f"{label}_DIGEST", f"{label} artifact digest is malformed.", "Supply a sha256 digest.")


def evaluate(data: dict, root: Path, evaluation_time: str | None = None) -> tuple[list, list, dict]:
    findings: list = []
    evidence: list = []
    target = data.get("target_stage")
    required_through = STAGE_INDEX.get(target, -1)
    if required_through < 0:
        _critical(findings, "TARGET_STAGE", "target_stage is unsupported.", "Select G0 through G8.")
        required_through = -1
    if data.get("reference_only") is not True:
        _critical(findings, "REFERENCE_ONLY", "Profile input must remain reference-only.", "Set reference_only to true.")
    if data.get("human_decision_required") is not True:
        _critical(findings, "HUMAN_DECISION", "Human decision remains required.", "Set human_decision_required to true.")
    if data.get("authority_effect") != "NONE":
        _critical(findings, "AUTHORITY_EFFECT", "Automated output cannot create authority.", "Set authority_effect to NONE.")
    if not DIGEST.fullmatch(str(data.get("configuration_digest", ""))):
        _critical(findings, "CONFIGURATION_DIGEST", "configuration_digest is malformed.", "Supply a sha256 digest.")

    known = data.get("known_unknowns") if isinstance(data.get("known_unknowns"), list) else []
    blocking = data.get("blocking_unknowns") if isinstance(data.get("blocking_unknowns"), list) else []
    if blocking:
        _critical(findings, "BLOCKING_UNKNOWN", "Blocking unknowns prevent the selected stage.", "Resolve or explicitly re-scope the blocking unknowns.")

    if data.get("material_change") is True:
        _critical(findings, "MATERIAL_CHANGE", "Prior assurance cannot establish current assurance after material change.", "Requalify the current subject and configuration.")

    checks = {
        0: ("MISSION", bool(data.get("mission_id") and data.get("mission_objective") and data.get("accountable_human_ref")), "mission identity"),
        1: ("BASELINE", isinstance(data.get("baseline_reference"), dict), "baseline reference"),
        2: ("AUTHORITY_DATA", isinstance(data.get("authority_data_references"), list) and bool(data.get("authority_data_references")), "authority/data reference"),
        3: ("QUALIFICATION", isinstance(data.get("qualification_reference"), dict), "qualification reference"),
        4: ("ADVERSARIAL_ASSURANCE", isinstance(data.get("adversarial_assurance_reference"), dict), "adversarial assurance reference"),
        5: ("HUMAN_READINESS", isinstance(data.get("human_readiness_reference"), dict), "human readiness reference"),
        6: ("OPERATIONAL_ACCEPTANCE", isinstance(data.get("operational_acceptance_reference"), dict), "operational acceptance reference"),
        7: ("SUSTAINMENT", all(isinstance(data.get(key), dict) for key in ("degraded_mode_reference", "recovery_reference", "support_owner_reference")), "sustainment references"),
        8: ("SUCCESSION", isinstance(data.get("succession_reference"), dict), "succession reference"),
    }
    for index in range(required_through + 1):
        code, present, label = checks[index]
        if not present:
            _critical(findings, f"MISSING_{code}", f"Required {label} is absent for {target}.", f"Supply the {label} before claiming this stage.")
    bindings = [
        (1, "baseline_reference", "BASELINE"),
        (3, "qualification_reference", "QUALIFICATION"),
        (4, "adversarial_assurance_reference", "ADVERSARIAL"),
        (5, "human_readiness_reference", "HUMAN_READINESS"),
        (6, "operational_acceptance_reference", "OPERATIONAL_ACCEPTANCE"),
        (7, "degraded_mode_reference", "DEGRADED_MODE"),
        (7, "recovery_reference", "RECOVERY"),
        (7, "support_owner_reference", "SUPPORT_OWNER"),
        (8, "succession_reference", "SUCCESSION"),
    ]
    for index, key, label in bindings:
        if index <= required_through and isinstance(data.get(key), dict):
            _bind(data[key], data, findings, label)
    if required_through >= 2 and isinstance(data.get("authority_data_references"), list):
        for item in data["authority_data_references"]:
            _bind(item, data, findings, "AUTHORITY_DATA")

    stage_keys = {
        1: ["baseline_reference"],
        2: ["authority_data_references"],
        3: ["qualification_reference"],
        4: ["adversarial_assurance_reference"],
        5: ["human_readiness_reference"],
        6: ["operational_acceptance_reference"],
        7: ["degraded_mode_reference", "recovery_reference", "support_owner_reference"],
        8: ["succession_reference"],
    }
    seen = set()
    for index in range(1, required_through + 1):
        for key in stage_keys.get(index, []):
            value = data.get(key)
            items = value if isinstance(value, list) else [value]
            for item in items:
                if not isinstance(item, dict):
                    continue
                reference = "/".join(str(item.get(field, "")) for field in ("source", "artifact_type", "artifact_id", "schema_version"))
                sha = str(item.get("artifact_digest", ""))
                marker = (reference, sha)
                if marker in seen:
                    continue
                seen.add(marker)
                evidence.append({"type": "ARTIFACT_ID", "reference": reference, "sha256": sha})
    evidence.sort(key=lambda item: (item["type"], item["reference"], item["sha256"]))

    details = {
        "reference_only": True,
        "authority_effect": "NONE",
        "target_stage": target,
        "known_unknowns": known,
        "blocking_unknowns": blocking,
        "requalification_required": data.get("material_change") is True,
        "pass_means": "Selected-stage structural, identity, configuration-binding, and integrity checks only.",
        "does_not_mean": [
            "operational readiness",
            "legal authority",
            "certification",
            "compliance",
            "factual truth of source evidence",
            "native validation of referenced artifacts",
            "production approval",
            "endorsement",
            "mission success",
        ],
    }
    return findings, evidence, details
