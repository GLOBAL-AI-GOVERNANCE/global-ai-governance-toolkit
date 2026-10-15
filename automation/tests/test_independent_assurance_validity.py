"""Independent validity-state tests."""

from pathlib import Path

from automation.scripts.run_profile import run_profile


def test_material_change_only(tmp_path):
    fixture = Path("automation/assurance/independent-assurance/fixtures/material_change.json")
    code, result = run_profile("independent-assurance-v0.1", fixture, tmp_path, None, None)
    assert code == 1
    assert result["status"] == "FAIL"
    assert result["details"]["validity_state"] == "STALE"
    assert result["details"]["revalidation_required"] is True
    assert result["details"]["trigger"] == "MATERIAL_CHANGE"


def test_unresolved_concern_only(tmp_path):
    fixture = Path("automation/assurance/independent-assurance/fixtures/unresolved_concern.json")
    code, result = run_profile("independent-assurance-v0.1", fixture, tmp_path, None, None)
    assert result["authority_effect"] == "NONE"
    assert result["details"]["validity_state"] == "QUESTIONED"
    assert result["details"]["revalidation_required"] is True
    assert result["details"]["trigger"] == "UNRESOLVED_CONCERN"
