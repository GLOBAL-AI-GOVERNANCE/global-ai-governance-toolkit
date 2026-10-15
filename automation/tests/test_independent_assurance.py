"""Tests for Independent Assurance profile."""

from pathlib import Path

from automation.profiles.independent_assurance import evaluate


def test_pass_case_returns_findings_evidence_details():
    payload = {
        "subject_id": "system-001",
        "authority_effect": "NONE",
        "evaluator": {"identity": "evaluator-001", "interests_disclosed": True},
        "scope": "bounded",
    }
    findings, evidence, details = evaluate(payload, Path("."), None)
    assert details["reference_only"] is True
    assert not any(f["severity"] == "CRITICAL" for f in findings)
