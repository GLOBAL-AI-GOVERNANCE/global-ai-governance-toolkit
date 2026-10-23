"""Organizational AI Maturity Evidence evaluator.

Non-authorizing. Profile remains unregistered.
Returns (findings, evidence, details) for common result machinery.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .common import finding

PROFILE_ID = "organizational-ai-maturity-v0.1"
VERSION = "0.1.0"

LEVELS = ("BASIC", "READY", "DYNAMIC", "ADVANCED")
LEVEL_ORDER = {level: i for i, level in enumerate(LEVELS)}


def evaluate(data: dict, root: Path, evaluation_time: str | None = None) -> tuple[list, list, dict]:
    findings: list[dict] = []
    evidence: list[dict] = []
    details: dict[str, Any] = {
        "support_status": "UNSUPPORTED",
        "freshness_status": "CURRENT",
        "assessment_state": "CURRENT",
        "confidence": "LOW",
        "claimed_level": None,
        "evidence_supported_level": None,
        "target_level": None,
        "contradictions": [],
        "gaps": [],
        "corrective_actions": [],
        "reassessment_triggers": [],
        "human_determination": "PENDING",
        "authority_effect": "NONE",
    }

    if data.get("authority_effect") not in (None, "NONE"):
        findings.append(finding(PROFILE_ID, "AUTHORITY_EFFECT", "CRITICAL",
                                "Authority effect must remain NONE.",
                                "Set authority_effect to NONE."))

    categories = data.get("categories") or []
    if not isinstance(categories, list) or not categories:
        findings.append(finding(PROFILE_ID, "CATEGORIES_MISSING", "CRITICAL",
                                "At least one category assessment is required.",
                                "Supply category records."))
        return findings, evidence, details

    # Aggregate across categories for bounded result (first category primary for details)
    cat = categories[0]
    claimed = cat.get("claimed_level")
    details["claimed_level"] = claimed
    details["target_level"] = cat.get("target_level")

    if claimed not in LEVELS:
        findings.append(finding(PROFILE_ID, "INVALID_LEVEL", "CRITICAL",
                                "Claimed level must be BASIC, READY, DYNAMIC, or ADVANCED.",
                                "Use only the four source vocabulary levels."))

    evs = cat.get("evidence") or []
    if not isinstance(evs, list):
        evs = []

    has_operating = False
    has_policy_only = False
    has_pilot = False
    has_synthetic = False
    scope_mismatch = False
    stale = False
    integrity_fail = False
    contradictions = cat.get("contradictions") or []
    if contradictions:
        findings.append(finding(PROFILE_ID, "CONTRADICTED", "HIGH",
                                "Contradictory evidence present. Do not average away.",
                                "Resolve contradictions before treating as supported."))
        details["support_status"] = "CONTRADICTED"
        details["contradictions"] = contradictions

    for ev in evs:
        if not isinstance(ev, dict):
            continue
        ref = ev.get("reference")
        if ref:
            evidence.append({"type": "URI", "reference": ref, "sha256": ev.get("sha256")})
        cls = ev.get("evidence_class")
        if cls == "OPERATING":
            has_operating = True
        elif cls == "POLICY":
            has_policy_only = True
        elif cls == "PILOT":
            has_pilot = True
        elif cls == "SYNTHETIC":
            has_synthetic = True
            findings.append(finding(PROFILE_ID, "SYNTHETIC_MISUSE", "HIGH",
                                    "Synthetic evidence cannot support operating maturity claim.",
                                    "Label as synthetic. Do not treat as operating evidence."))
        if ev.get("scope") and ev.get("scope") != data.get("assessment_scope"):
            scope_mismatch = True
            findings.append(finding(PROFILE_ID, "SCOPE_MISMATCH", "HIGH",
                                    "Evidence scope does not match assessment scope.",
                                    "Evidence must cover the claimed organizational scope."))
        valid_through = ev.get("valid_through")
        if valid_through and evaluation_time and valid_through < evaluation_time:
            stale = True
            findings.append(finding(PROFILE_ID, "STALE", "HIGH",
                                    "Evidence is stale or expired.",
                                    "Reassess. Stale evidence does not remain current."))
        if ev.get("integrity_asserted") and not ev.get("sha256"):
            integrity_fail = True
            findings.append(finding(PROFILE_ID, "INTEGRITY_FAIL", "HIGH",
                                    "Integrity asserted but digest missing.",
                                    "Supply sha256 or remove integrity assertion."))

    if not evs:
        findings.append(finding(PROFILE_ID, "MISSING_EVIDENCE", "HIGH",
                                "No evidence supplied for claimed level.",
                                "Supply representative operating evidence."))
        details["support_status"] = "UNSUPPORTED"

    if has_policy_only and not has_operating and claimed in ("DYNAMIC", "ADVANCED"):
        findings.append(finding(PROFILE_ID, "POLICY_ONLY_OVERCLAIM", "HIGH",
                                "Policy document alone does not support Dynamic or Advanced.",
                                "Supply representative operating evidence."))
        details["support_status"] = "PARTIAL"

    if has_pilot and data.get("assessment_scope", "").lower().find("enterprise") >= 0:
        findings.append(finding(PROFILE_ID, "PILOT_AS_ENTERPRISE", "HIGH",
                                "Single pilot cannot support organization-wide claim.",
                                "Collect representative cross-unit evidence."))
        details["support_status"] = "PARTIAL"

    if scope_mismatch:
        details["support_status"] = "UNSUPPORTED"
    if stale:
        details["freshness_status"] = "STALE"
        details["assessment_state"] = "REASSESSMENT_REQUIRED"
    if integrity_fail:
        details["support_status"] = "UNSUPPORTED"

    triggers = cat.get("reassessment_triggers") or []
    if triggers:
        details["reassessment_triggers"] = triggers
        details["assessment_state"] = "REASSESSMENT_REQUIRED"
        findings.append(finding(PROFILE_ID, "REASSESSMENT_REQUIRED", "MEDIUM",
                                "Material change or trigger requires reassessment.",
                                "Reassess before treating prior state as current."))

    # Determine evidence-supported level (bounded, not inventing scores)
    if details["support_status"] == "CONTRADICTED" or not has_operating or scope_mismatch or stale or integrity_fail:
        supported = "BASIC" if claimed else None
    elif has_operating and not has_policy_only and not has_pilot and not has_synthetic and not scope_mismatch and not stale:
        supported = claimed
        details["support_status"] = "SUPPORTED"
        details["confidence"] = "HIGH"
    else:
        supported = "READY" if claimed in ("DYNAMIC", "ADVANCED") else claimed
        details["support_status"] = "PARTIAL"
        details["confidence"] = "MEDIUM"

    details["evidence_supported_level"] = supported
    details["gaps"] = cat.get("gaps") or []
    details["corrective_actions"] = cat.get("corrective_actions") or []

    if cat.get("organization_defined_critical") and not cat.get("critical_rationale"):
        findings.append(finding(PROFILE_ID, "CRITICAL_RATIONALE", "MEDIUM",
                                "Organization-defined critical category requires explicit rationale.",
                                "Document the organization's own governance decision."))

    # Prohibited interpretations
    if any("certified" in str(x).lower() or "endorsement" in str(x).lower() for x in [data.get("assessment_id"), claimed]):
        findings.append(finding(PROFILE_ID, "PROHIBITED_CLAIM", "CRITICAL",
                                "Result does not constitute certification or endorsement.",
                                "Remove prohibited claim language."))

    return findings, evidence, details
