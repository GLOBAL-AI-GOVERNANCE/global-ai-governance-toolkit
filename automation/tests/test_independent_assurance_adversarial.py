"""Adversarial validity behavior for Independent Assurance profile."""

from pathlib import Path

from automation.scripts.run_profile import run_profile


def test_runner_adversarial_fixture(tmp_path):
    fixture = Path("automation/assurance/independent-assurance/fixtures/adversarial.json")
    code, result = run_profile(
        "independent-assurance-v0.1",
        fixture,
        tmp_path,
        None,
        None,
    )
    assert code == 1
    assert result["status"] == "FAIL"
    assert result["authority_effect"] == "NONE"
    assert result["details"]["validity_firewall"] is True
