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

    qual = data.get("qualification_evidence") or {}
    if not qual.get("qualification_id"):
        findings.append(finding(PROFILE_ID, "QUALIFICATION_MISSING", "HIGH",
                                "Valid qualification reference is required for positive independent assurance.",
                                "Supply a Foundations Qualification Evidence Record reference."))
    else:
        if qual.get("authority_effect") != "NONE":
            findings.append(finding(PROFILE_ID, "QUALIFICATION_AUTHORITY", "CRITICAL",
                                    "Qualification cannot confer authority.",
                                    "Set authority_effect to NONE."))
        if qual.get("outcome") != "QUALIFIED":
            findings.append(finding(PROFILE_ID, "QUALIFICATION_OUTCOME", "CRITICAL",
                                    "Qualification outcome must be QUALIFIED for positive state.",
                                    "Provide a QUALIFIED outcome."))
        if evaluation_time and qual.get("expires_at") and evaluation_time > qual["expires_at"]:
            findings.append(finding(PROFILE_ID, "QUALIFICATION_EXPIRED", "CRITICAL",
                                    "Qualification is expired.",
                                    "Requalify."))
        scope = data.get("scope", "")
        if qual.get("scope") and scope and qual["scope"] not in scope and scope not in qual["scope"]:
            findings.append(finding(PROFILE_ID, "QUALIFICATION_SCOPE", "HIGH",
                                    "Qualification role/scope incompatible with evaluation scope.",
                                    "Align scope."))

    if not data.get("scope"):
        findings.append(finding(PROFILE_ID, "SCOPE", "MEDIUM",
                                "Evaluation scope is missing.",
                                "State evaluation scope."))

    validity_state = "VALID"
    revalidation_required = False
    trigger = None

    if data.get("material_change") or data.get("expired"):
        findings.append(finding(PROFILE_ID, "STALE", "CRITICAL",
                                "Prior assurance is stale.",
                                "Revalidate."))
        validity_state = "STALE"
        revalidation_required = True
        trigger = "MATERIAL_CHANGE" if data.get("material_change") else "EXPIRED"

    if data.get("unresolved_concern"):
        findings.append(finding(PROFILE_ID, "UNRESOLVED_CONCERN", "HIGH",
                                "Unresolved material concern affects assurance basis.",
                                "Investigate and revalidate."))
        if validity_state == "VALID":
            validity_state = "QUESTIONED"
        revalidation_required = True
        if trigger is None:
            trigger = "UNRESOLVED_CONCERN"

    if data.get("evaluator_conflict"):
        findings.append(finding(PROFILE_ID, "EVALUATOR_CONFLICT", "CRITICAL",
                                "Material independence conflict.",
                                "Resolve conflict and revalidate."))
        validity_state = "STALE"
        revalidation_required = True
        trigger = "EVALUATOR_CONFLICT"

    if data.get("high_consequence") and not data.get("shutdown_evidence_present"):
        findings.append(finding(PROFILE_ID, "SHUTDOWN_EVIDENCE", "CRITICAL",
                                "High-consequence subject lacks shutdown evidence.",
                                "Supply verified shutdown evidence."))
        validity_state = "STALE"
        revalidation_required = True
        if trigger is None:
            trigger = "SHUTDOWN_EVIDENCE"

    details = {
        "reference_only": True,
        "validity_state": validity_state,
        "revalidation_required": revalidation_required,
        "trigger": trigger,
    }
    return findings, evidence, details
