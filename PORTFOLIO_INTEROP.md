# Portfolio Interoperability

## Optional profile evidence

Toolkit v2.3.0 profile results are additive evidence artifacts. A portfolio handoff may reference `profile-result.json` and its SHA-256 through the existing `evidence_refs` array. This does not change `authority_effect: NONE`, transfer authority, or imply that a declared future dependency such as Stateful Revocation is operational.

This repository remains independently useful as the Global AI Governance Toolkit. Portfolio interoperability is additive.

The optional `automation/contracts/governance-decision-handoff.schema.json` contract provides a bounded reference envelope for carrying a Decision Pack reference into another GLOBAL AI GOVERNANCE repository without turning the handoff into an approval, certification, or deployment authorization.

The Wave A runtime automatically emits this envelope after successful Decision Pack generation. The default target is `agentic-ai-governance` and may be explicitly changed for an authorized consumer. Emission records a reference; it does not transfer authority or trust.

## Contract boundary

A handoff record may identify:

- the source Decision Pack;
- the governed AI system;
- the target repository;
- evidence and authority references;
- an optional configuration reference;
- an immutable artifact digest; and
- an explicit human-review boundary.

The handoff has `authority_effect: NONE`.

Receiving repositories must validate the references they consume. They must not infer that the handoff itself approves deployment, closes a vulnerability, grants action authority, or proves a control effective.

## Verification

The existing hosted `AI Governance Checks` workflow discovers and runs `automation/tests/test_portfolio_handoff.py` with the rest of the automation test suite.
