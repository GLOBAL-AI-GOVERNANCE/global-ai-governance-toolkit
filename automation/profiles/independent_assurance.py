"""Independent Assurance profile evaluator.

Non-authorizing. Assembles reference evidence only.
"""

from __future__ import annotations

from pathlib import Path

from .common import finding, result, sha256_bytes, canonical_bytes


PROFILE_ID = "independent-assurance-v0.1"
VERSION = "0.1.0"


def evaluate(payload: dict, root: Path) -> dict:
    findings = []
    evidence = []

    subject = payload.get("subject_id")
    if not subject or not isinstance(subject, str):
        findings.append(finding(PROFILE_ID, "SUBJECT_MISSING", "CRITICAL",
                                "Subject identity is required.",
                                "Supply exact subject_id."))

    if payload.get("authority_effect") != "NONE":
        findings.append(finding(PROFILE_ID, "AUTHORITY_EFFECT", "CRITICAL",
                                "Authority effect must remain NONE.",
                                "Set authority_effect to NONE."))

    evaluator = payload.get("evaluator") or {}
    if not evaluator.get("identity"):
        findings.append(finding(PROFILE_ID, "EVALUATOR_IDENTITY", "HIGH",
                                "Evaluator identity is missing.",
                                "Disclose evaluator identity."))
    if not evaluator.get("interests_disclosed"):
        findings.append(finding(PROFILE_ID, "INTERESTS", "HIGH",
                                "Evaluator interests not disclosed.",
                                "Disclose interests."))

    if not payload.get("scope"):
        findings.append(finding(PROFILE_ID, "SCOPE", "MEDIUM",
                                "Evaluation scope is missing.",
                                "State evaluation scope."))

    source_digest = sha256_bytes(canonical_bytes(payload))
    return result(
        PROFILE_ID,
        VERSION,
        source_digest,
        None,
        findings,
        evidence,
        {"reference_only": True},
    )
