# Requirements Traceability

| Requirement | Evidence |
|---|---|
| Explicit seed and synthetic inputs | `fixtures/pass.json` |
| Deterministic classical baseline | `automation/profiles/quantum_ai.py` |
| Quality and measurement boundary | fixture and profile-result details |
| Reproducibility and prohibited claims | `automation/tests/test_profiles.py` |
| Human authority preserved | common `authority_effect: NONE` result |
