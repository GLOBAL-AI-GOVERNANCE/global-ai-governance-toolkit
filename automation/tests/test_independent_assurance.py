"""Tests for Independent Assurance profile."""

from pathlib import Path

from automation.profiles.independent_assurance import evaluate


def test_pass_fixture_produces_non_authorizing_result():
    payload = {
        "subject_id": "system-001",
        "authority_effect": "NONE",
        "evaluator": {"identity": "evaluator-001", "interests_disclosed": True},
        "scope": "bounded",
    }
    result = evaluate(payload, Path("."))
    assert result["authority_effect"] == "NONE"
    assert result["status"] in ("PASS", "CONDITIONAL")
    assert result["details"]["reference_only"] is True
