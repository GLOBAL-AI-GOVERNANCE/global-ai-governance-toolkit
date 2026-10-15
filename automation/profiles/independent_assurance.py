"""Independent Assurance profile evaluator.

Non-authorizing. Assembles reference evidence only.
"""

from __future__ import annotations

from pathlib import Path

from .common import finding

PROFILE_ID = "independent-assurance-v0.1"
VERSION = "0.1.0"


def evaluate(data: dict, root: Path, evaluation_time: str | None = None) -> tuple[list, list, dict]:
    findings = []
    evidence = []

    subject = data.get("subject_id")
    if not subject or not isinstance(subject, str):
        findings.append(finding(PROFILE_ID, "SUBJECT_MISSING", "CRITICAL",
                                "Subject identity is required.",
                                "Supply exact subject_id."))

    if data.get("authority_effect") != "NONE":
        findings.append(finding(PROFILE_ID, "AUTHORITY_EFFECT", "CRITICAL",
                                "Authority effect must remain NONE.",
                                "Set authority_effect to NONE."))

    evaluator = data.get("evaluator") or {}
    if not evaluator.get("identity"):
        findings.append(finding(PROFILE_ID, "EVALUATOR_IDENTITY", "HIGH",
                                "Evaluator identity is missing.",
                                "Disclose evaluator identity."))
    if not evaluator.get("interests_disclosed"):
        findings.append(finding(PROFILE_ID, "INTERESTS", "HIGH",
                                "Evaluator interests not disclosed.",
                                "Disclose interests."))

    if not data.get("scope"):
        findings.append(finding(PROFILE_ID, "SCOPE", "MEDIUM",
                                "Evaluation scope is missing.",
                                "State evaluation scope."))

    details = {"reference_only": True}
    return findings, evidence, details
