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

    validity_state = "VALID"
    revalidation_required = False
    trigger = None

    if data.get("material_change"):
        findings.append(finding(PROFILE_ID, "MATERIAL_CHANGE", "CRITICAL",
                                "Prior assurance is stale after material change.",
                                "Revalidate."))
        validity_state = "STALE"
        revalidation_required = True
        trigger = "MATERIAL_CHANGE"

    if data.get("unresolved_concern"):
        findings.append(finding(PROFILE_ID, "UNRESOLVED_CONCERN", "HIGH",
                                "Unresolved material concern affects assurance basis.",
                                "Investigate and revalidate."))
        if validity_state == "VALID":
            validity_state = "QUESTIONED"
        revalidation_required = True
        if trigger is None:
            trigger = "UNRESOLVED_CONCERN"

    details = {
        "reference_only": True,
        "validity_state": validity_state,
        "revalidation_required": revalidation_required,
        "trigger": trigger,
    }
    return findings, evidence, details
