"""Runner integration test for Independent Assurance profile."""

from pathlib import Path

from automation.scripts.run_profile import run_profile


def test_runner_invokes_independent_assurance(tmp_path):
    fixture = Path("automation/assurance/independent-assurance/fixtures/pass.json")
    code, result = run_profile(
        "independent-assurance-v0.1",
        fixture,
        tmp_path,
        None,
        None,
    )
    assert result["authority_effect"] == "NONE"
    assert result["profile_id"] == "independent-assurance-v0.1"
    assert code in (0, 1)
