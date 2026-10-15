"""Runner integration test for Independent Assurance profile."""

from pathlib import Path

from automation.scripts.run_profile import run_profile


def test_runner_pass_fixture(tmp_path):
    fixture = Path("automation/assurance/independent-assurance/fixtures/pass.json")
    code, result = run_profile(
        "independent-assurance-v0.1",
        fixture,
        tmp_path,
        None,
        None,
    )
    assert code == 0
    assert result["status"] == "PASS"
    assert result["authority_effect"] == "NONE"
    assert result["profile_id"] == "independent-assurance-v0.1"
