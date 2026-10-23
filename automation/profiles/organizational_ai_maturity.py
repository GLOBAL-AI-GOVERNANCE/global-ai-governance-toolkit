"""Organizational AI Maturity Evidence evaluator.

Non-authorizing. Profile remains unregistered.
Evaluates every submitted category. Returns (findings, evidence, details).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .common import finding

PROFILE_ID = "organizational-ai-maturity-v0.1"
VERSION = "0.1.0"

LEVELS = ("BASIC", "READY", "DYNAMIC", "ADVANCED")


def parse_time(value: str | None) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        return None


def evaluate(data: dict, root: Path, evaluation_time: str | None = None) -> tuple[list, list, dict]:
    findings: list[dict] = []
    evidence: list[dict] = []
    eval_dt = parse_time(evaluation_time)

    details: dict[str, Any] = {
        "categories": [],
        "overall_synthesis": "PENDING_HUMAN_SYNTHESIS",
        "authority_effect": "NONE",
        "human_determination": "PENDING",
    }

    if data.get("authority_effect") not in (None, "NONE"):
        findings.append(finding(PROFILE_ID, "AUTHORITY_EFFECT", "CRITICAL",
                                "Authority effect must remain NONE.",
                                "Set authority_effect to NONE."))

    if data.get("framework_version") != "2025":
        findings.append(finding(PROFILE_ID, "FRAMEWORK_VERSION", "CRITICAL",
                                "Only framework_version 2025 is supported by this adapter.",
                                "Use the 2025 adapter or a separately versioned adapter."))

    categories = data.get("categories") or []
    if not isinstance(categories, list) or not categories:
        findings.append(finding(PROFILE_ID, "CATEGORIES_MISSING", "CRITICAL",
                                "At least one category assessment is required.",
                                "Supply category records."))
        return findings, evidence, details

    for cat in categories:
        if not isinstance(cat, dict):
            continue
        cat_result = evaluate_category(cat, data, eval_dt, findings, evidence)
        details["categories"].append(cat_result)

    return findings, evidence, details


def evaluate_category(cat: dict, data: dict, eval_dt: datetime | None, findings: list, evidence: list) -> dict:
    claimed = cat.get("claimed_level")
    result = {
        "pillar": cat.get("pillar"),
        "category": cat.get("category"),
        "claimed_level": claimed,
        "target_level": cat.get("target_level"),
        "evidence_supported_level": None,
        "support_status": "UNSUPPORTED",
        "freshness_status": "CURRENT",
        "assessment_state": "CURRENT",
        "confidence": "LOW",
        "contradictions": cat.get("contradictions") or [],
        "gaps": cat.get("gaps") or [],
        "corrective_actions": cat.get("corrective_actions") or [],
        "reassessment_triggers": cat.get("reassessment_triggers") or [],
        "material_change_events": cat.get("material_change_events") or [],
    }

    if claimed not in LEVELS:
        findings.append(finding(PROFILE_ID, "INVALID_LEVEL", "CRITICAL",
                                f"Claimed level for {cat.get('category')} must be BASIC, READY, DYNAMIC, or ADVANCED.",
                                "Use only the four source vocabulary levels."))

    evs = cat.get("evidence") or []
    has_operating = False
    has_representative = False
    has_policy = False
    has_pilot = False
    has_synthetic = False
    scope_mismatch = False
    stale = False
    integrity_fail = False

    for ev in evs:
        if not isinstance(ev, dict):
            continue
        ref = ev.get("reference")
        if ref:
            evidence.append({"type": "URI", "reference": ref, "sha256": ev.get("sha256")})
        cls = ev.get("evidence_class")
        if cls == "OPERATING":
            has_operating = True
            if ev.get("is_representative") is True:
                has_representative = True
        elif cls == "POLICY":
            has_policy = True
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
        valid_through = parse_time(ev.get("valid_through"))
        if valid_through and eval_dt and valid_through < eval_dt:
            stale = True
            findings.append(finding(PROFILE_ID, "STALE", "HIGH",
                                    "Evidence is stale or expired.",
                                    "Reassess. Stale evidence does not remain current."))
        if ev.get("integrity_asserted") and not ev.get("sha256"):
            integrity_fail = True
            findings.append(finding(PROFILE_ID, "INTEGRITY_FAIL", "HIGH",
                                    "Integrity asserted but digest missing.",
                                    "Supply sha256 or remove integrity assertion."))

    # Precedence: contradiction first
    if result["contradictions"]:
        result["support_status"] = "CONTRADICTED"
        findings.append(finding(PROFILE_ID, "CONTRADICTED", "HIGH",
                                "Contradictory evidence present. Do not average away.",
                                "Resolve contradictions before treating as supported."))
    elif not evs:
        findings.append(finding(PROFILE_ID, "MISSING_EVIDENCE", "HIGH",
                                "No evidence supplied for claimed level.",
                                "Supply representative operating evidence."))
        result["support_status"] = "UNSUPPORTED"
    elif scope_mismatch or integrity_fail or has_synthetic:
        result["support_status"] = "UNSUPPORTED"
    elif has_policy and not has_operating and claimed in ("DYNAMIC", "ADVANCED"):
        findings.append(finding(PROFILE_ID, "POLICY_ONLY_OVERCLAIM", "HIGH",
                                "Policy document alone does not support Dynamic or Advanced.",
                                "Supply representative operating evidence."))
        result["support_status"] = "PARTIAL"
    elif has_pilot:
        findings.append(finding(PROFILE_ID, "PILOT_AS_ENTERPRISE", "HIGH",
                                "Single pilot cannot support organization-wide claim.",
                                "Collect representative cross-unit evidence."))
        result["support_status"] = "PARTIAL"
    elif has_operating and not has_representative:
        findings.append(finding(PROFILE_ID, "NON_REPRESENTATIVE", "MEDIUM",
                                "Operating evidence is not marked representative of typical practice.",
                                "Supply representative-period or is_representative basis."))
        result["support_status"] = "PARTIAL"
        result["confidence"] = "LOW"
    elif has_operating and has_representative and not scope_mismatch and not stale and not integrity_fail:
        # Conservative: existence of representative operating evidence does not auto-prove higher levels.
        # Level-specific criteria are not yet implemented pending adapter/license gate.
        result["support_status"] = "PARTIAL"
        result["confidence"] = "MEDIUM"
        result["evidence_supported_level"] = None  # undetermined until criteria mapping exists
    else:
        result["support_status"] = "UNSUPPORTED"

    if stale:
        result["freshness_status"] = "STALE"
        result["assessment_state"] = "REASSESSMENT_REQUIRED"

    # Only actual material change events trigger reassessment, not mere configuration of triggers
    if result["material_change_events"]:
        result["assessment_state"] = "REASSESSMENT_REQUIRED"
        findings.append(finding(PROFILE_ID, "REASSESSMENT_REQUIRED", "MEDIUM",
                                "Observed material-change event requires reassessment.",
                                "Reassess before treating prior state as current."))

    if cat.get("organization_defined_critical") and not cat.get("critical_rationale"):
        findings.append(finding(PROFILE_ID, "CRITICAL_RATIONALE", "MEDIUM",
                                "Organization-defined critical category requires explicit rationale.",
                                "Document the organization's own governance decision."))

    return result
